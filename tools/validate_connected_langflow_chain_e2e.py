"""Run the real authoring -> MongoDB -> analysis Langflow chain.

This validator uploads the four exported Flows to a running Langflow 1.9.2
server, invokes Gemini through each authoring Flow, inspects the item documents
written to a fresh MongoDB database, and finally executes the analysis Flow
against the compiled three-collection metadata.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import requests
from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import sha256_json
from reference_runtime.metadata_collections import (
    METADATA_COLLECTIONS,
    load_available_domain_package_from_three_collections,
)
from tools.flow_builder_support import sha256_file, write_json_atomic
from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    langflow_gemini_contract_evidence,
    load_dotenv_values,
    resolve_gemini_api_key,
)
from tools.validate_langflow_http_authoring_e2e import _authoring_responses
from tools.validate_langflow_http_e2e import (
    _auth_headers,
    _canonical_responses,
    _upload_flow,
    extract_terminal_evidence,
)


FLOW_PATHS = {
    "analysis": ROOT / "flow_exports" / "metadata_v6_data_analysis_flow_v6_standalone.json",
    "domain": ROOT / "flow_exports" / "metadata_v6_domain_authoring_flow_v6_standalone.json",
    "dataset": ROOT / "flow_exports" / "metadata_v6_dataset_catalog_authoring_flow_v6_standalone.json",
    "main_filter": ROOT / "flow_exports" / "metadata_v6_main_filter_authoring_flow_v6_standalone.json",
}


DOMAIN_PROFILE = """Manufacturing Analysis 도메인을 등록해줘.
이 도메인은 제조 공정 현황을 조회하고 분석하기 위한 업무 영역이야.
기본 언어는 ko-KR이고 시간대는 Asia/Seoul이야."""

DA_GROUP = """DA 공정 그룹을 등록해줘.
display_name은 DA이고 유의어는 DA, D/A, DA공정, D/A공정, DA 공정, D/A 공정이야.
field는 OPER_NAME이야.
포함 공정은 OPER_NAME 값 D/A1, D/A2, D/A3, D/A4, D/A5, D/A6이야.
별칭마다 별도 item을 만들지 말고 공정그룹 하나로 저장해."""

WIP_METRIC = """재공 수량 지표를 WIP_QTY로 등록해줘.
display_name은 재공 수량이고 유의어는 WIP, 재공, 재공량, 현재 재공이야.
wip 계열 데이터셋의 WIP 컬럼을 사용하고 합계(sum)로 집계해."""

PRODUCT_GRAIN = """제품 기준 grain을 product로 등록해줘.
제품을 구분하는 key는 TECH, DEN, MODE, PKG_TYPE1, PKG_TYPE2, LEAD, MCP_NO야."""

PRODUCT_RECIPE = """제품별 집계 recipe를 product.standard로 등록해줘.
유의어는 제품별, 제품 기준, 제품 집계야.
grain은 product이고 key는 TECH, DEN, MODE, PKG_TYPE1, PKG_TYPE2, LEAD, MCP_NO야.
필요한 입력은 dataset과 metric이야."""


def _run_url(server_url: str, flow_id: str) -> str:
    return f"{server_url.rstrip('/')}/api/v1/run/{flow_id}"


def _post_flow(
    client: requests.Session,
    headers: dict[str, str],
    server_url: str,
    flow_id: str,
    *,
    input_value: str,
    tweaks: dict[str, Any],
    output_component: str | None = None,
    timeout_seconds: int,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "input_value": input_value,
        "input_type": "chat",
        "output_type": "any",
        "session_id": f"v6-connected-{uuid.uuid4().hex}",
        "tweaks": tweaks,
    }
    if output_component:
        body["output_component"] = output_component
    response = client.post(
        _run_url(server_url, flow_id),
        headers={**headers, "Content-Type": "application/json"},
        json=body,
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("langflow_response_invalid")
    return payload


def _wip_source_text() -> str:
    source = (ROOT / "metadata" / "authoring" / "v6_inputs" / "dataset_v6.txt").read_text(
        encoding="utf-8"
    )
    match = re.search(
        r"<!-- single_wip_today:start -->(.*?)<!-- single_wip_today:end -->",
        source,
        flags=re.DOTALL,
    )
    if not match or not match.group(1).strip():
        raise RuntimeError("wip_today_source_block_missing")
    return match.group(1).strip()


def _authoring_tweaks(mongo_uri: str, database: str, *, mode: str = "save") -> dict[str, Any]:
    return {
        "simple_metadata_authoring_engine": {
            "mode": mode,
            "mongo_uri": mongo_uri,
            "mongo_database": database,
            "mongo_timeout_ms": 10000,
        },
        "draft_language_model": {"temperature": 0.0, "stream": False},
    }


def _chat_message(payload: dict[str, Any]) -> str:
    for group in payload.get("outputs") or []:
        for block in group.get("outputs") or []:
            if str(block.get("component_id") or "") != "chat_output":
                continue
            message = ((block.get("results") or {}).get("message") or {}).get("text")
            if isinstance(message, str) and message.strip():
                return message.strip()
            artifact = (block.get("artifacts") or {}).get("message")
            if isinstance(artifact, str) and artifact.strip():
                return artifact.strip()
    return ""


def _engine_response(payload: dict[str, Any]) -> dict[str, Any]:
    for group in payload.get("outputs") or []:
        for block in group.get("outputs") or []:
            if str(block.get("component_id") or "") != "simple_metadata_authoring_engine":
                continue
            raw = ((block.get("artifacts") or {}).get("response") or {}).get("raw")
            if isinstance(raw, dict):
                return raw
    return {}


def _authoring_evidence(
    payload: dict[str, Any],
    probe_payload: dict[str, Any],
    *,
    case_id: str,
    source_text: str,
) -> dict[str, Any]:
    message = _chat_message(payload)
    response = _engine_response(probe_payload)
    if not message:
        raise RuntimeError(f"{case_id}:chat_output_missing")
    if not response:
        raise RuntimeError(f"{case_id}:engine_probe_missing")
    usage = response.get("llm_usage") if isinstance(response.get("llm_usage"), dict) else {}
    error = response.get("error") if isinstance(response.get("error"), dict) else {}
    evidence = {
        "case_id": case_id,
        "source_sha256": sha256(source_text.encode("utf-8")).hexdigest(),
        "source_chars": len(source_text),
        "chat_output_sha256": sha256(message.encode("utf-8")).hexdigest(),
        "chat_output_preview": message[:300],
        "status": response.get("status"),
        "stage": response.get("stage"),
        "authoring_kind": response.get("authoring_kind"),
        "persisted": response.get("persisted"),
        "revision": int(response.get("revision") or 0),
        "draft_llm_calls": int(usage.get("draft_llm_calls") or 0),
        "repair_llm_calls": int(usage.get("repair_llm_calls") or 0),
        "error": {
            "code": str(error.get("code") or ""),
            "stage": str(error.get("stage") or ""),
            "message": str(error.get("message") or "")[:500],
        },
    }
    evidence["passed"] = (
        "저장 완료" in message
        and "실패" not in message
        and "확인 필요" not in message
        and evidence["status"] == "ok"
        and evidence["stage"] == "validated"
        and evidence["persisted"] is False
        and evidence["draft_llm_calls"] == 1
        and evidence["repair_llm_calls"] == 0
    )
    if not evidence["passed"]:
        raise RuntimeError(f"{case_id}:authoring_failed:{json.dumps(evidence, ensure_ascii=False)}")
    return evidence


def _document_evidence(database: Any) -> dict[str, Any]:
    summaries: dict[str, list[dict[str, Any]]] = {}
    raw_documents: dict[str, list[dict[str, Any]]] = {}
    for role, collection_name in METADATA_COLLECTIONS.items():
        rows = list(database[collection_name].find({}))
        raw_documents[role] = rows
        summaries[role] = [
            {
                "id": str(row.get("_id") or ""),
                "section": str(row.get("section") or ""),
                "key": str(row.get("key") or ""),
                "natural_text_chars": len(str(row.get("natural_text") or "")),
                "payload_keys": sorted(str(key) for key in (row.get("payload") or {})),
            }
            for row in sorted(rows, key=lambda item: str(item.get("_id") or ""))
        ]

    dataset = next(
        (
            row.get("payload") or {}
            for row in raw_documents["table_catalog"]
            if row.get("section") == "datasets" and row.get("key") == "wip_today"
        ),
        {},
    )
    domain_payloads = {
        (str(row.get("section") or ""), str(row.get("key") or "")): row.get("payload") or {}
        for row in raw_documents["domain"]
    }
    query = str((dataset.get("source_config") or {}).get("query_template") or "")
    metric = domain_payloads.get(("metrics", "WIP_QTY"), {})
    group = domain_payloads.get(("entity_groups", "DA"), {})
    grain = domain_payloads.get(("grains", "product"), {})
    recipe = domain_payloads.get(("recipes", "product.standard"), {})
    critical = {
        "dataset": {
            "family": dataset.get("family"),
            "source_type": dataset.get("source_type"),
            "time_scope": (dataset.get("selection_criteria") or {}).get("time_scope"),
            "date_physical_column": ((dataset.get("fields") or {}).get("DATE") or {}).get(
                "physical_column"
            ),
            "wip_physical_column": ((dataset.get("fields") or {}).get("WIP") or {}).get(
                "physical_column"
            ),
            "required_params": (dataset.get("source_config") or {}).get("required_params"),
            "query_line_count": len(query.splitlines()),
            "query_sha256": sha256(query.encode("utf-8")).hexdigest() if query else "",
            "query_has_date_placeholder": "{DATE}" in query,
        },
        "metric": {
            "metric_id": metric.get("metric_id"),
            "value_type": metric.get("value_type"),
            "allowed_rollups": (metric.get("additivity") or {}).get("allowed_rollups"),
            "source_binding": metric.get("source_binding"),
        },
        "entity_group": {
            "target_field": group.get("target_field"),
            "member_count": len(group.get("members") or []),
            "selection": group.get("selection"),
        },
        "grain": {"keys": grain.get("keys")},
        "recipe": {
            "aliases": recipe.get("aliases"),
            "required_slots": recipe.get("required_slots"),
            "operation": recipe.get("default_operation_template"),
        },
    }
    checks = {
        "all_three_collections_nonempty": all(summaries[role] for role in METADATA_COLLECTIONS),
        "wip_dataset_present": bool(dataset),
        "query_preserved": bool(query) and "{DATE}" in query,
        "time_scope_current_day": critical["dataset"]["time_scope"] == "current_day",
        "metric_bound_to_wip": critical["metric"]["source_binding"]
        == {"dataset_family": "wip", "field": "WIP"},
        "group_typed_in": (critical["entity_group"]["selection"] or {}).get("operator") == "in",
        "grain_exact": critical["grain"]["keys"]
        == ["TECH", "DEN", "MODE", "PKG_TYPE1", "PKG_TYPE2", "LEAD", "MCP_NO"],
        "recipe_typed_aggregate": (critical["recipe"]["operation"] or {}).get("op") == "aggregate",
        "recipe_alias_clean": "제품 집계야" not in (critical["recipe"]["aliases"] or []),
    }
    if not all(checks.values()):
        raise RuntimeError(f"mongodb_document_checks_failed:{json.dumps(checks, ensure_ascii=False)}")
    return {
        "collections": dict(METADATA_COLLECTIONS),
        "counts": {role: len(rows) for role, rows in summaries.items()},
        "items": summaries,
        "critical": critical,
        "checks": checks,
    }


def _analysis_tweaks(mongo_uri: str, database: str) -> dict[str, Any]:
    return {
        "domain_bundle_loader": {
            "mongo_uri": mongo_uri,
            "mongo_database": database,
            "mongo_timeout_ms": 10000,
        },
        "request_state_capsule": {"allow_anonymous_multiturn": True},
        "intent_language_model": {"temperature": 0.0, "stream": False},
        "retrieval_job_router": {"data_mode": "dummy"},
        "answer_facts_narrative": {"narrative_enabled": False},
        "response_state_commit": {"allow_anonymous_multiturn": True},
    }


def _analysis_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    terminal = extract_terminal_evidence(payload)
    responses = _canonical_responses(payload)
    if len(responses) != 1:
        raise RuntimeError(f"analysis_response_count:{len(responses)}")
    response = responses[0]
    sections = response.get("answer_sections") if isinstance(response.get("answer_sections"), dict) else {}
    table = sections.get("result_table") if isinstance(sections.get("result_table"), dict) else {}
    analysis = response.get("analysis") if isinstance(response.get("analysis"), dict) else {}
    evidence = {
        "status": terminal.get("status"),
        "route": terminal.get("route"),
        "usage": terminal.get("usage"),
        "terminal_complete": terminal.get("terminal_equivalent"),
        "row_count": int(table.get("row_count") or 0),
        "columns": table.get("columns") or [],
        "data_ref": str(table.get("data_ref") or ""),
        "retrieval": (response.get("trace") or {}).get("retrieval") or [],
        "pandas_code_present": bool(analysis.get("pandas_code")),
        "state_version": terminal.get("state_version"),
        "persistence": terminal.get("persistence_contract"),
    }
    evidence["passed"] = (
        evidence["status"] == "ok"
        and evidence["route"] == "deterministic"
        and evidence["row_count"] == 2
        and evidence["terminal_complete"] is True
        and all(int(value or 0) == 0 for value in (evidence["usage"] or {}).values())
        and evidence["pandas_code_present"] is True
    )
    if not evidence["passed"]:
        raise RuntimeError(f"analysis_checks_failed:{json.dumps(evidence, ensure_ascii=False)}")
    return evidence


def _typed_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    outputs = [item for group in payload.get("outputs") or [] for item in group.get("outputs") or []]
    if len(outputs) != 1:
        raise RuntimeError("typed_executor_output_missing")
    artifact = (outputs[0].get("artifacts") or {}).get("result_context") or {}
    raw = artifact.get("raw") if isinstance(artifact.get("raw"), dict) else {}
    result = raw.get("result") if isinstance(raw.get("result"), dict) else {}
    rows = result.get("rows") if isinstance(result.get("rows"), list) else []
    if len(rows) != 2:
        raise RuntimeError(f"typed_executor_rows_unexpected:{len(rows)}")
    return rows


def run(*, server_url: str, env_file: Path, database: str, timeout_seconds: int) -> dict[str, Any]:
    env = load_dotenv_values(env_file)
    resolve_gemini_api_key(env_file)
    mongo_uri = str(env.get("MONGODB_URI") or "").strip()
    if not mongo_uri:
        raise RuntimeError("mongodb_uri_not_configured")

    client = requests.Session()
    headers = _auth_headers(client, server_url, env)
    uploaded = {
        name: _upload_flow(client, headers, server_url, path, timeout_seconds)
        for name, path in FLOW_PATHS.items()
    }
    flow_evidence = {
        name: {
            "file": FLOW_PATHS[name].name,
            "sha256": sha256_file(FLOW_PATHS[name]),
            "flow_id": str(record.get("id") or ""),
            "node_count": len((record.get("data") or {}).get("nodes") or []),
            "model_contract": langflow_gemini_contract_evidence(
                json.loads(FLOW_PATHS[name].read_text(encoding="utf-8")),
                require_model=True,
            ),
        }
        for name, record in uploaded.items()
    }
    if any(row["model_contract"].get("passed") is not True for row in flow_evidence.values()):
        raise RuntimeError("flow_gemini_model_contract_failed")

    mongo = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    db = mongo[database]
    if any(db[name].count_documents({}) for name in METADATA_COLLECTIONS.values()):
        raise RuntimeError("fresh_database_not_empty")

    main_filter_text = (
        ROOT / "metadata" / "authoring" / "v6_contract_validation_live" / "main_filter_v6.txt"
    ).read_text(encoding="utf-8").strip()
    cases = [
        ("main_filter", "main_filter", main_filter_text),
        ("domain_profile", "domain", DOMAIN_PROFILE),
        ("dataset_wip_today", "dataset", _wip_source_text()),
        ("domain_da_group", "domain", DA_GROUP),
        ("domain_wip_metric", "domain", WIP_METRIC),
        ("domain_product_grain", "domain", PRODUCT_GRAIN),
        ("domain_product_recipe", "domain", PRODUCT_RECIPE),
    ]
    authoring = []
    try:
        for case_id, flow_name, source_text in cases:
            payload = _post_flow(
                client,
                headers,
                server_url,
                str(uploaded[flow_name]["id"]),
                input_value=source_text,
                tweaks=_authoring_tweaks(mongo_uri, database),
                timeout_seconds=timeout_seconds,
            )
            probe_payload = _post_flow(
                client,
                headers,
                server_url,
                str(uploaded[flow_name]["id"]),
                input_value=source_text,
                tweaks=_authoring_tweaks(mongo_uri, database, mode="validate_only"),
                output_component="simple_metadata_authoring_engine",
                timeout_seconds=timeout_seconds,
            )
            authoring.append(
                _authoring_evidence(
                    payload,
                    probe_payload,
                    case_id=case_id,
                    source_text=source_text,
                )
            )

        package = load_available_domain_package_from_three_collections(db)
        documents = _document_evidence(db)
        question = "오늘 DA공정 WIP을 제품별로 알려줘"
        analysis_payload = _post_flow(
            client,
            headers,
            server_url,
            str(uploaded["analysis"]["id"]),
            input_value=question,
            tweaks=_analysis_tweaks(mongo_uri, database),
            timeout_seconds=timeout_seconds,
        )
        analysis = _analysis_evidence(analysis_payload)
        typed_payload = _post_flow(
            client,
            headers,
            server_url,
            str(uploaded["analysis"]["id"]),
            input_value=question,
            tweaks=_analysis_tweaks(mongo_uri, database),
            output_component="typed_executor_publisher",
            timeout_seconds=timeout_seconds,
        )
        rows = _typed_rows(typed_payload)
    finally:
        mongo.close()

    report = {
        "contract_version": "connected.langflow.chain.validation.v1",
        "validated_at": datetime.now().astimezone().isoformat(),
        "langflow": {"server": server_url, "expected_version": "1.9.2"},
        "model": DEFAULT_GEMINI_MODEL,
        "database": database,
        "flows": flow_evidence,
        "authoring": authoring,
        "mongodb": documents,
        "compiled_package": {
            "domain_id": package.get("domain_id"),
            "environment": package.get("environment"),
            "revision": package.get("revision"),
            "catalog_sha256": (package.get("runtime_catalog") or {}).get("catalog_sha256"),
            "planner_profile": ((package.get("runtime_catalog") or {}).get("output_profile") or {}).get(
                "planner_profile"
            ),
        },
        "analysis": {**analysis, "typed_rows": rows},
        "raw_prompts_persisted": False,
        "secrets_persisted": False,
        "passed": True,
    }
    report["evidence_sha256"] = sha256_json(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-url", default="http://127.0.0.1:7873")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--database", default="")
    parser.add_argument("--timeout-seconds", type=int, default=240)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    database = args.database.strip() or f"datagov_v6_connected_{datetime.now():%Y%m%d_%H%M%S}"
    output = args.output or ROOT / "validation_outputs" / f"connected_langflow_chain_{datetime.now():%Y%m%d_%H%M%S}.json"
    report = run(
        server_url=args.server_url,
        env_file=args.env_file,
        database=database,
        timeout_seconds=args.timeout_seconds,
    )
    write_json_atomic(output, report)
    print(json.dumps({
        "passed": report["passed"],
        "database": report["database"],
        "model": report["model"],
        "authoring_cases": len(report["authoring"]),
        "collection_counts": report["mongodb"]["counts"],
        "analysis": {
            "status": report["analysis"]["status"],
            "route": report["analysis"]["route"],
            "row_count": report["analysis"]["row_count"],
            "typed_rows": report["analysis"]["typed_rows"],
        },
        "output": str(output),
        "evidence_sha256": report["evidence_sha256"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
