"""Deterministic facts, immutable response, and Message/API/GaiA adapters."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any
from urllib.parse import quote

from .canonical import ContractError, bounded, sha256_json
from .contracts import validate_contract


DEFAULT_DISPLAY_OPTIONS = {
    "profile": "standard",
    "include_diagnostics": False,
    "show_result_table": True,
    "table_preview_limit": 10,
    "show_analysis_evidence": False,
    "show_download_links": True,
    "show_notices": True,
    "show_applied_criteria": True,
    "show_next_questions": False,
    "show_intent_analysis": False,
    "show_data_retrieval": False,
    "show_execution_plan": False,
}


def normalize_display_options(value: Any) -> dict[str, Any]:
    """Normalize the v5-compatible toggles into the closed v6 contract."""

    raw = value if isinstance(value, dict) else {}
    result = deepcopy(DEFAULT_DISPLAY_OPTIONS)
    profile = str(raw.get("profile") or result["profile"]).strip()
    result["profile"] = profile or "standard"
    for key in result:
        if key in {"profile", "table_preview_limit"}:
            continue
        if key in raw:
            result[key] = bool(raw[key])
    if "show_pandas_code" in raw and "show_execution_plan" not in raw:
        # Backward-compatible UI label only; no pandas code is generated.
        result["show_execution_plan"] = bool(raw.get("show_pandas_code"))
    if result["include_diagnostics"]:
        result["show_intent_analysis"] = True
        result["show_data_retrieval"] = True
        result["show_execution_plan"] = True
    try:
        result["table_preview_limit"] = max(1, min(20, int(raw.get("table_preview_limit", 10))))
    except (TypeError, ValueError):
        result["table_preview_limit"] = 10
    normalized = {"contract_version": "display.options.v1", **result}
    return validate_contract(normalized, "display-options.schema.json", stage="display_options")


def build_answer_facts(request: dict[str, Any], plan: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    row_count = int(result.get("row_count") or 0)
    columns = [str(item) for item in result.get("columns", [])]
    datasets = [str(item.get("dataset_key") or "") for item in plan.get("retrieval_jobs", [])]
    parameters = {str(item.get("job_id")): item.get("parameters", {}) for item in plan.get("retrieval_jobs", [])}
    fact_items = [
        {"fact_id": "fact:row_count", "type": "integer", "value": row_count},
        {"fact_id": "fact:columns", "type": "string_list", "value": columns},
        {"fact_id": "fact:datasets", "type": "string_list", "value": datasets},
        {"fact_id": "fact:parameters", "type": "object", "value": parameters},
    ]
    material = {
        "contract_version": "answer.facts.v1",
        "question": str(request.get("question") or ""),
        "facts": fact_items,
        "result_sha256": str(result.get("result_sha256") or ""),
        "plan_id": str(plan.get("plan_id") or ""),
    }
    facts = {**material, "facts_sha256": sha256_json(material)}
    return validate_contract(facts, "answer-facts.schema.json", stage="answer_facts")


def _next_questions(plan: dict[str, Any], result: dict[str, Any]) -> list[dict[str, str]]:
    suggestions: list[str] = []
    if int(result.get("row_count") or 0) > 1:
        suggestions.append("이 결과에서 값이 가장 큰 항목만 보여줘")
    suggestions.append("적용한 조회 조건과 계산 근거를 설명해줘")
    if any(item.get("dataset_key") == "production_today" for item in plan.get("retrieval_jobs", [])):
        suggestions.append("같은 조건으로 어제 결과도 보여줘")
    return [{"id": f"followup:{index}", "text": text} for index, text in enumerate(suggestions[:3], start=1)]


def _usage(route: dict[str, Any]) -> dict[str, int]:
    return {
        "intent_llm_calls": int(route.get("intent_llm_calls") or 0),
        "pandas_code_llm_calls": 0,
        "pandas_repair_llm_calls": 0,
        "answer_llm_calls": 0,
    }


def validate_authoring_response_hash(response: dict[str, Any]) -> dict[str, Any]:
    """Validate the closed authoring terminal contract and its immutable hash."""

    if not isinstance(response, dict):
        raise ContractError(
            "response_contract_error",
            "authoring_terminal",
            "Metadata authoring response must be an object.",
        )
    validate_contract(
        response,
        "metadata-authoring-response.schema.json",
        stage="authoring_terminal",
        error_code="response_contract_error",
    )
    expected = sha256_json(
        {key: value for key, value in response.items() if key != "response_sha256"}
    )
    if response.get("response_sha256") != expected:
        raise ContractError(
            "response_contract_error",
            "authoring_terminal",
            "Metadata authoring response hash does not match its payload.",
        )
    return response


def _finalize_response(material: dict[str, Any]) -> dict[str, Any]:
    # Output nodes exchange ordinary JSON. Durable content hashes are maintained
    # only by the result store and are referenced through data_refs.
    response = deepcopy(material)
    validate_contract(response, "response.schema.json", stage="response_assembly")
    return bounded(response, 256 * 1024, "response")


def assemble_response(
    *,
    request: dict[str, Any],
    intent: dict[str, Any],
    plan: dict[str, Any],
    result: dict[str, Any],
    answer_facts: dict[str, Any],
    state: dict[str, Any],
    result_ref: dict[str, Any],
    source_refs: list[dict[str, Any]],
    route_telemetry: dict[str, Any],
    source_diagnostics: list[dict[str, Any]],
    data_mode: str,
    download_base_url: str = "",
    events: list[str] | None = None,
) -> dict[str, Any]:
    rows = result.get("rows") if isinstance(result.get("rows"), list) else []
    columns = [str(item) for item in result.get("columns", [])]
    row_count = int(result.get("row_count") or 0)
    result_status = str(result.get("status") or ("empty" if row_count == 0 else "ok"))
    status = "empty" if row_count == 0 and result_status in {"ok", "empty"} else result_status
    headline = "조회 결과가 없습니다." if status == "empty" else f"요청한 분석 결과는 총 {row_count}건입니다."
    # Durable descriptors exist only after a persistent state/result commit.
    # Anonymous ephemeral execution intentionally calls this assembler with an
    # empty state and empty result_ref; never manufacture an empty download
    # descriptor because it violates the opaque-ref contract and leaks a false
    # persistence affordance into the response.
    persistent = bool(isinstance(result_ref, dict) and result_ref.get("ref_id"))
    refs = (
        [deepcopy(result_ref)] + [deepcopy(item) for item in source_refs]
        if persistent
        else []
    )
    for item in refs:
        ref_id = str(item.get("ref_id") or "")
        item["store"] = "agent_v6_result_store"
        item["path"] = "payload.rows"
        item["download_url"] = (
            f"{download_base_url.rstrip('/')}/download.csv?download_ref={quote(ref_id)}"
            if download_base_url and ref_id
            else ""
        )
    notices: list[dict[str, str]] = []
    next_questions = _next_questions(plan, result)
    answer_sections = {
        "contract_version": "answer.sections.v1",
        "summary": {"headline": headline, "fact_ids": ["fact:row_count"]},
        "result_table": {
            "row_source": "data.rows",
            "columns": columns,
            "row_count": row_count,
            "data_ref": str(result_ref.get("ref_id") or ""),
        },
        "applied_criteria": {
            "datasets": [item.get("dataset_key") for item in plan.get("retrieval_jobs", [])],
            "required_params": {item.get("job_id"): item.get("parameters", {}) for item in plan.get("retrieval_jobs", [])},
            "analysis_filters": [item.get("filters") for item in plan.get("retrieval_jobs", []) if item.get("filters")],
            "group_by": plan.get("result_contract", {}).get("grain", []),
            "metrics": list(plan.get("lineage", {}).keys()),
        },
        "evidence": {
            "facts_sha256": answer_facts.get("facts_sha256"),
            "plan_id": plan.get("plan_id"),
            "result_sha256": result.get("result_sha256"),
        },
        "notices": notices,
        "downloads": [
            {
                "ref_id": str(item.get("ref_id") or ""),
                "role": str(item.get("role") or ""),
                "label": "분석 결과" if item.get("role") == "analysis_result" else "조회 원본",
                "url": str(item.get("download_url") or ""),
            }
            for item in refs
        ],
        "next_questions": next_questions,
    }
    validate_contract(answer_sections, "answer-sections.schema.json", stage="answer_sections")
    trace_id = f"trace:{sha256_json([request.get('request_id'), plan.get('plan_id'), result.get('result_sha256')])[:24]}"
    usage = _usage(route_telemetry)
    material = {
        "contract_version": "response.v1",
        "response_type": "data_analysis",
        "status": status,
        "stage_status": {
            "overall": status,
            "intent": "skipped" if route_telemetry.get("intent_llm_calls") == 0 else "ok",
            "retrieval": "ok",
            "analysis": status,
        },
        "message": headline,
        "data_mode": str(data_mode or "dummy"),
        "analysis_mode": "typed_ir",
        "answer_sections": answer_sections,
        "request": {
            "request_id": request.get("request_id"),
            "question": request.get("question"),
            "session_id": request.get("session_id"),
            "reference_instant": request.get("reference_instant"),
            "timezone": request.get("timezone"),
        },
        "intent_plan": {
            "intent_sha256": intent.get("intent_sha256"),
            "intent_candidate_id": intent.get("intent_candidate_id"),
            "plan_id": plan.get("plan_id"),
            "plan_fingerprint": plan.get("plan_fingerprint"),
            "semantic_intent": intent.get("semantics", {}),
        },
        "analysis": {
            "status": status,
            "result_sha256": result.get("result_sha256"),
            "operation_trace": result.get("operation_trace", []),
            "execution_ir": plan.get("operations", []),
            "lineage": result.get("lineage", {}),
        },
        "clarification": None,
        "data": {"columns": columns, "rows": rows[:50], "row_count": row_count},
        "data_refs": refs,
        "state": (
            {
                "state_version": state.get("state_version"),
                "executed_result_ref": state.get("executed_result_ref"),
                "expires_at": state.get("expires_at"),
            }
            if persistent
            else None
        ),
        "trace": {
            "trace_id": trace_id,
            "route": deepcopy(route_telemetry),
            "retrieval": deepcopy(source_diagnostics),
            "usage": usage,
            "commit_order": list(events or []),
        },
    }
    return _finalize_response(material)


def _error_stage_status(stage: str, status: str, route: dict[str, Any]) -> dict[str, str]:
    intent_status = "skipped" if int(route.get("intent_llm_calls") or 0) == 0 else "ok"
    if stage in {"request_capsule", "request_contract", "route_contract", "route_eligibility", "candidate_selection", "intent_routing", "intent_llm", "intent_decoding", "intent_validation", "plan_compilation", "plan_validation", "parameter_binding", "metadata_resolution"}:
        intent_status = status if stage.startswith("intent") or stage in {"route_contract", "route_eligibility", "candidate_selection", "request_capsule", "request_contract"} else intent_status
        return {"overall": status, "intent": intent_status, "retrieval": "not_called", "analysis": "not_called"}
    if stage in {"retrieval", "source_merge", "source_contract"}:
        return {"overall": status, "intent": intent_status, "retrieval": "error", "analysis": "not_called"}
    return {"overall": status, "intent": intent_status, "retrieval": "ok", "analysis": "error"}


def error_response(request: dict[str, Any], error: dict[str, Any], route_telemetry: dict[str, Any] | None = None) -> dict[str, Any]:
    route = deepcopy(route_telemetry or {})
    message = str(error.get("message") or "분석을 완료하지 못했습니다.")
    is_clarification = str(error.get("code") or "") == "needs_clarification"
    status = "needs_clarification" if is_clarification else "error"
    options = ((error.get("details") or {}).get("options") or []) if isinstance(error.get("details"), dict) else []
    trace_id = str(error.get("trace_id") or f"trace:{sha256_json([request.get('request_id'), error])[:24]}")
    normalized_error = None if is_clarification else {
        "contract_version": "error.v1",
        **deepcopy(error),
        "trace_id": trace_id,
    }
    if normalized_error is not None:
        validate_contract(normalized_error, "error.schema.json", stage="error_mapping")
    notices = [] if is_clarification else [{"code": str(error.get("code") or "unknown"), "message": message}]
    answer_sections = {
        "contract_version": "answer.sections.v1",
        "summary": {"headline": message, "fact_ids": []},
        "result_table": {"row_source": "data.rows", "columns": [], "row_count": 0, "data_ref": ""},
        "applied_criteria": {},
        "evidence": {},
        "notices": notices,
        "downloads": [],
        "next_questions": [],
    }
    validate_contract(answer_sections, "answer-sections.schema.json", stage="answer_sections")
    usage = _usage(route)
    material = {
        "contract_version": "response.v1",
        "response_type": "data_analysis",
        "status": status,
        "stage_status": _error_stage_status(str(error.get("stage") or "runtime"), status, route),
        "message": message,
        "data_mode": "dummy",
        "analysis_mode": "typed_ir",
        "answer_sections": answer_sections,
        "request": {
            "request_id": request.get("request_id"),
            "question": request.get("question"),
            "session_id": request.get("session_id"),
            "reference_instant": request.get("reference_instant"),
            "timezone": request.get("timezone"),
        },
        "intent_plan": {},
        "analysis": {"status": status, "error": normalized_error},
        "clarification": {"question": message, "options": [str(item) for item in options[:20]]} if is_clarification else None,
        "data": {"columns": [], "rows": [], "row_count": 0},
        "data_refs": [],
        "state": None,
        "trace": {"trace_id": trace_id, "route": route, "retrieval": [], "usage": usage, "commit_order": []},
    }
    return _finalize_response(material)


def _cell(value: Any) -> str:
    if value is None:
        return ""
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":")) if isinstance(value, (dict, list)) else str(value)
    return text.replace("|", "\\|").replace("\n", " ")[:160]


def _table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    rule = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(_cell(row.get(column)) for column in columns) + " |" for row in rows]
    return "\n".join([header, rule, *body])


def render_message(response: dict[str, Any], options: Any = None) -> str:
    response = deepcopy(response) if isinstance(response, dict) else {}
    display = normalize_display_options(options)
    sections = [f"### 응답\n{response.get('message', '')}".strip()]
    data = response.get("data") if isinstance(response.get("data"), dict) else {}
    rows = data.get("rows") if isinstance(data.get("rows"), list) else []
    columns = [str(item) for item in data.get("columns", [])]
    if display["show_result_table"] and columns:
        preview = rows[: int(display["table_preview_limit"])]
        sections.append("### 결과 테이블\n" + (_table(preview, columns) if preview else "표시할 결과 행이 없습니다.") + f"\n\n총 {int(data.get('row_count') or 0)}건입니다.")
    answer_sections = response.get("answer_sections") if isinstance(response.get("answer_sections"), dict) else {}
    if display["show_applied_criteria"] and answer_sections.get("applied_criteria"):
        sections.append("### 적용 기준\n```json\n" + json.dumps(answer_sections["applied_criteria"], ensure_ascii=False, indent=2) + "\n```")
    if display["show_analysis_evidence"] and answer_sections.get("evidence"):
        sections.append("### 분석 근거\n```json\n" + json.dumps(answer_sections["evidence"], ensure_ascii=False, indent=2) + "\n```")
    if display["show_download_links"]:
        downloads = [item for item in answer_sections.get("downloads", []) if item.get("url")]
        if downloads:
            sections.append("### 다운로드\n" + "\n".join(f"- [{item.get('label', '다운로드')}]({item['url']})" for item in downloads))
    if display["show_notices"] and answer_sections.get("notices"):
        sections.append("### 알림\n" + "\n".join(f"- {item.get('message', item)}" for item in answer_sections["notices"]))
    if display["show_next_questions"] and answer_sections.get("next_questions"):
        sections.append("### 후속 질문\n" + "\n".join(f"- {item['text']}" for item in answer_sections["next_questions"][:3]))
    if display["show_intent_analysis"]:
        sections.append("### 의도 분석\n```json\n" + json.dumps(response.get("intent_plan", {}).get("semantic_intent", {}), ensure_ascii=False, indent=2) + "\n```")
    if display["show_data_retrieval"]:
        sections.append("### 조회 진단\n```json\n" + json.dumps(response.get("trace", {}).get("retrieval", []), ensure_ascii=False, indent=2) + "\n```")
    if display["show_execution_plan"]:
        sections.append("### 실행 계획 진단\n```json\n" + json.dumps(response.get("analysis", {}).get("execution_ir", []), ensure_ascii=False, indent=2) + "\n```")
    return "\n\n".join(section for section in sections if section)


def api_output(response: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(response) if isinstance(response, dict) else {}


def gaia_output(response: dict[str, Any]) -> dict[str, Any]:
    canonical = deepcopy(response) if isinstance(response, dict) else {}
    sections = canonical.get("answer_sections") if isinstance(canonical.get("answer_sections"), dict) else {}
    trace = canonical.get("trace") if isinstance(canonical.get("trace"), dict) else {}
    urls = [
        {"title": str(item.get("label") or "다운로드"), "url": str(item.get("url") or "")}
        for item in sections.get("downloads", [])
        if item.get("url")
    ]
    metadata = {
        "contract_version": "gaia.metadata.v1",
        "docs": [],
        "images": [],
        "knowhows": [],
        "followup_questions": [deepcopy(item) for item in sections.get("next_questions", [])[:3]],
        "urls": urls,
        "trace_id": str(trace.get("trace_id") or ""),
        "usage": deepcopy(trace.get("usage", {})),
    }
    validate_contract(metadata, "gaia-metadata.schema.json", stage="gaia_output")
    return {"answer": str(canonical.get("message") or ""), "metadata": metadata}
