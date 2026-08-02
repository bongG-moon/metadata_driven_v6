"""Exercise zero-LLM, Intent-LLM and Narrative-LLM lanes in the real Flow graph.

Each case executes the serialized standalone components in Langflow edge order.
Reports persist only route/call counters and hashes; prompts, responses and API
keys are intentionally excluded.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    GeminiJsonModel,
    assert_secret_absent,
    gemini_model_contract_evidence,
    langflow_gemini_contract_evidence,
    require_exact_gemini_model,
    resolve_gemini_api_key,
)
from tools.validate_langflow_equivalent_pipeline import execute_component_pipeline


DEFAULT_FLOW = ROOT / "flow_exports" / "metadata_v6_data_analysis_flow_v6_standalone.json"


CASES = (
    {
        "case_id": "LIVE-ZERO",
        "question": "오늘 투입된 제품중 MCP NO가 L-267로 시작하는 제품의 INPUT 수량 알려줘",
        "narrative_enabled": False,
        "expected_route": "deterministic",
        "expected_status": "ok",
        "expected_calls": 0,
        "expected_intent_calls": 0,
        "expected_answer_calls": 0,
    },
    {
        "case_id": "LIVE-INTENT",
        "question": "오늘 DA 쪽에서 잘 나간 제품 세 개만 보면?",
        "narrative_enabled": False,
        "expected_route": "intent_llm",
        "expected_status": "ok",
        "expected_calls": 1,
        "expected_intent_calls": 1,
        "expected_answer_calls": 0,
    },
    {
        "case_id": "LIVE-NARRATIVE",
        "question": "오늘 투입된 제품중 MCP NO가 L-267로 시작하는 제품의 INPUT 수량 알려줘",
        "narrative_enabled": True,
        "expected_route": "deterministic",
        "expected_status": "ok",
        "expected_calls": 1,
        "expected_intent_calls": 0,
        "expected_answer_calls": 1,
    },
    {
        "case_id": "LIVE-UNSUPPORTED",
        "question": "등록되지 않은 모델로 다음 달 생산량을 예측해줘",
        "narrative_enabled": True,
        "expected_route": "unsupported",
        "expected_status": "error",
        "expected_calls": 0,
        "expected_intent_calls": 0,
        "expected_answer_calls": 0,
    },
)


def _set_narrative(flow: dict[str, Any], enabled: bool) -> None:
    for node in flow.get("data", {}).get("nodes", []):
        if str(node.get("id") or "") != "answer_facts_context_builder":
            continue
        config = node.get("data", {}).get("node", {})
        field = (config.get("template") or {}).get("narrative_enabled")
        if not isinstance(field, dict):
            raise RuntimeError("narrative_template_missing")
        field["value"] = bool(enabled)
        return
    raise RuntimeError("answer_facts_context_node_missing")


def run(flow_path: Path, *, env_path: Path, model: str, timeout_seconds: int) -> dict[str, Any]:
    model = require_exact_gemini_model(model)
    api_key = resolve_gemini_api_key(env_path)
    base_flow = json.loads(flow_path.read_text(encoding="utf-8"))
    flow_model_contract = langflow_gemini_contract_evidence(base_flow)
    if flow_model_contract.get("passed") is not True:
        raise RuntimeError("flow_gemini_model_contract_failed")
    rows: list[dict[str, Any]] = []
    for case in CASES:
        flow = deepcopy(base_flow)
        _set_narrative(flow, bool(case["narrative_enabled"]))
        provider = GeminiJsonModel(
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            max_output_tokens=512,
        )
        pipeline = execute_component_pipeline(
            flow,
            question=str(case["question"]),
            session_id=f"live-component-{case['case_id'].lower()}",
            domain_id="manufacturing",
            language_model=provider,
            expected_model_calls=int(case["expected_calls"]),
            expected_status=str(case["expected_status"]),
        )
        route = pipeline.get("route") if isinstance(pipeline.get("route"), dict) else {}
        usage = pipeline.get("usage") if isinstance(pipeline.get("usage"), dict) else {}
        provider_evidence = provider.evidence()
        checks = {
            "pipeline_passed": pipeline.get("passed") is True,
            "route_exact": route.get("route") == case["expected_route"],
            "intent_calls_exact": int(usage.get("intent_llm_calls") or 0)
            == int(case["expected_intent_calls"]),
            "answer_calls_exact": int(usage.get("answer_llm_calls") or 0)
            == int(case["expected_answer_calls"]),
            "provider_calls_exact": provider.calls == int(case["expected_calls"]),
            "provider_model_versions_exact": provider_evidence.get(
                "provider_model_versions_exact"
            )
            is True,
            "pandas_code_calls_zero": int(usage.get("pandas_code_llm_calls") or 0) == 0,
            "pandas_repair_calls_zero": int(usage.get("pandas_repair_llm_calls") or 0) == 0,
        }
        row = {
            "case_id": case["case_id"],
            "model": str(model).removeprefix("models/"),
            "expected_route": case["expected_route"],
            "actual_route": route.get("route"),
            "expected_status": case["expected_status"],
            "actual_status": pipeline.get("response_status"),
            "narrative_enabled": case["narrative_enabled"],
            "expected_provider_calls": case["expected_calls"],
            "actual_provider_calls": provider.calls,
            "usage": usage,
            "provider": provider_evidence,
            "pipeline_response_sha256": pipeline.get("response_sha256"),
            "pipeline_failures": pipeline.get("failures"),
            "checks": checks,
            "passed": all(checks.values()),
        }
        assert_secret_absent(row, api_key)
        rows.append(row)
    report = {
        "contract_version": "live.langflow.component-model.validation.v1",
        "model": model,
        "model_contract": gemini_model_contract_evidence(model),
        "flow_model_contract": flow_model_contract,
        "flow_file": flow_path.name,
        "provider_payloads_persisted": False,
        "prompts_persisted": False,
        "case_count": len(rows),
        "passed": sum(1 for row in rows if row["passed"]),
        "failed": sum(1 for row in rows if not row["passed"]),
        "provider_calls": sum(int(row["actual_provider_calls"]) for row in rows),
        "provider_model_evidence_passed": all(
            (row.get("checks") or {}).get("provider_model_versions_exact") is True
            for row in rows
        ),
        "rows": rows,
    }
    assert_secret_absent(report, api_key)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow", type=Path, default=DEFAULT_FLOW)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--model", default=DEFAULT_GEMINI_MODEL)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs" / "live_component_models.json",
    )
    args = parser.parse_args()
    report = run(
        args.flow.resolve(),
        env_path=args.env_file,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: report[key] for key in ("model", "case_count", "passed", "failed", "provider_calls")},
            ensure_ascii=False,
        )
    )
    print(f"report: {args.output}")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
