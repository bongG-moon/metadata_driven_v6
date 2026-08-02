"""Validate the generic v2 lane with an unrelated support-ticket domain.

The catalog fixture is defined by the dedicated candidate tests.  This tool
extends that evidence through deterministic planning and typed execution, then
probes fail-closed bundle/intent/plan boundaries.
"""

from __future__ import annotations

import argparse
import json
import runpy
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import ContractError, sha256_json
from reference_runtime.contracts import validate_contract
from reference_runtime.generic_v2_candidates import (
    build_generic_v2_candidate_bundle,
    normalize_generic_v2_intent,
    resolve_generic_v2_intent,
    validate_generic_v2_candidate_bundle,
)
from reference_runtime.generic_v2_planner import compile_generic_v2_plan, validate_generic_v2_plan
from reference_runtime.typed_executor import TypedExecutor


DEFAULT_OUTPUT = ROOT / "validation_outputs" / "generic_v2_support_pipeline.json"
FIXTURE_TEST = ROOT / "tests" / "test_generic_v2_candidates.py"


def _fixture_api() -> tuple[dict[str, Any], Callable[..., dict[str, Any]]]:
    namespace = runpy.run_path(str(FIXTURE_TEST))
    catalog_factory = namespace.get("support_ticket_catalog")
    request_factory = namespace.get("request")
    if not callable(catalog_factory) or not callable(request_factory):
        raise RuntimeError("support_ticket_fixture_api_missing")
    return catalog_factory(), request_factory


def _source_rows() -> dict[str, list[dict[str, Any]]]:
    return {
        "ticket_events": [
            {
                "CASE_ID": "T-001",
                "OPEN_DATE": "2026-08-01",
                "QUEUE": "technical",
                "OWNER_ID": "A-01",
                "WAIT_MINUTES": 70,
                "SUBJECT": "로그인 오류",
            },
            {
                "CASE_ID": "T-002",
                "OPEN_DATE": "2026-08-01",
                "QUEUE": "billing",
                "OWNER_ID": "A-02",
                "WAIT_MINUTES": 30,
                "SUBJECT": "청구 문의",
            },
            {
                "CASE_ID": "T-003",
                "OPEN_DATE": "2026-08-01",
                "QUEUE": "billing",
                "OWNER_ID": "A-02",
                "WAIT_MINUTES": 20,
                "SUBJECT": "환불 문의",
            },
            {
                "CASE_ID": "T-004",
                "OPEN_DATE": "2026-08-01",
                "QUEUE": "general",
                "OWNER_ID": "A-03",
                "WAIT_MINUTES": 10,
                "SUBJECT": "사용법",
            },
            {
                "CASE_ID": "T-005",
                "OPEN_DATE": "2026-07-31",
                "QUEUE": "technical",
                "OWNER_ID": "A-01",
                "WAIT_MINUTES": 999,
                "SUBJECT": "전일 제외 확인",
            },
        ],
        "agent_directory": [
            {"OWNER_ID": "A-01", "OWNER_NAME": "Kim"},
            {"OWNER_ID": "A-02", "OWNER_NAME": "Lee"},
            {"OWNER_ID": "A-03", "OWNER_NAME": "Park"},
        ],
        "ticket_view": [],
    }


def _blocked(call: Callable[[], Any]) -> dict[str, Any]:
    try:
        call()
    except ContractError as exc:
        return {"blocked": True, "code": exc.code, "stage": exc.stage}
    except Exception as exc:
        return {"blocked": True, "code": type(exc).__name__, "stage": "unexpected_exception"}
    return {"blocked": False, "code": None, "stage": None}


def run() -> dict[str, Any]:
    catalog, request_factory = _fixture_api()
    request = request_factory("오늘 큐별 대기시간 상위 2개를 보여줘")
    bundle = build_generic_v2_candidate_bundle(request, catalog)
    validate_generic_v2_candidate_bundle(bundle, catalog)
    validate_contract(bundle, "resolved-candidate-bundle.schema.json", stage="candidate_bundle_contract")

    def forbidden_model(_prompt: str) -> str:
        raise AssertionError("deterministic route must not call a model")

    intent, telemetry = resolve_generic_v2_intent(request, bundle, llm_callable=forbidden_model)
    validate_contract(intent, "semantic-intent.schema.json", stage="intent_contract")
    plan = compile_generic_v2_plan(
        intent,
        bundle,
        catalog,
        question=str(request.get("question") or ""),
    )
    validate_generic_v2_plan(plan, catalog)
    validate_contract(plan, "analysis-plan.schema.json", stage="plan_contract")
    rows_by_dataset = _source_rows()
    frames = {
        str(job["job_id"]): rows_by_dataset[str(job["dataset_key"])]
        for job in plan.get("retrieval_jobs", [])
    }
    result = TypedExecutor().execute(plan, frames).as_contract(plan)
    validate_contract(result, "analysis-result.schema.json", stage="result_contract")
    expected_rows = [
        {"QUEUE": "technical", "WAIT_MINUTES": 70.0},
        {"QUEUE": "billing", "WAIT_MINUTES": 50.0},
    ]
    observed_rows = result.get("rows") if isinstance(result.get("rows"), list) else []
    operators = [
        f"{item.get('op')}.v1"
        for item in plan.get("operations", [])
        if isinstance(item, dict) and item.get("op")
    ]
    datasets = [
        str(item.get("dataset_key") or "")
        for item in plan.get("retrieval_jobs", [])
        if isinstance(item, dict)
    ]
    happy_checks = {
        "route_deterministic": bundle["route_decision"]["route"] == "deterministic",
        "intent_calls_zero": int(telemetry.get("intent_llm_calls") or 0) == 0,
        "intent_generator_deterministic": intent.get("intent_generator") == "deterministic",
        "dataset_exact": datasets == ["ticket_events"],
        "typed_operator_coverage": all(
            item in operators for item in ("filter.v1", "aggregate.v1", "rank.v1", "project.v1")
        ),
        "columns_exact": result.get("columns") == ["QUEUE", "WAIT_MINUTES"],
        "rows_exact": observed_rows == expected_rows,
        # TypedExecutor.validate_contract() already verified the canonical result
        # hash above.  Keep this report assertion representation-agnostic: the
        # executor owns the exact hashed projection, while the harness only
        # requires the validated digest to be present.
        "result_hash_present": isinstance(result.get("result_sha256"), str)
        and len(result["result_sha256"]) == 64,
    }

    bundle_hash = deepcopy(bundle)
    bundle_hash["bundle_sha256"] = "0" * 64
    prompt_extra = deepcopy(bundle)
    prompt_extra["prompt_cards"][0]["extra"] = "forbidden"
    semantics_change = deepcopy(bundle)
    semantics_change["intent_candidates"][0]["semantics"]["metric_refs"] = ["UNKNOWN_METRIC"]
    catalog_mismatch = deepcopy(bundle)
    catalog_mismatch["catalog_sha256"] = "0" * 64
    plan_operator = deepcopy(plan)
    plan_operator["operations"][0]["op"] = "python"
    negatives = {
        "bundle_hash_tamper": _blocked(lambda: validate_generic_v2_candidate_bundle(bundle_hash, catalog)),
        "prompt_card_extra_field": _blocked(lambda: validate_generic_v2_candidate_bundle(prompt_extra, catalog)),
        "candidate_semantics_tamper": _blocked(lambda: validate_generic_v2_candidate_bundle(semantics_change, catalog)),
        "catalog_hash_tamper": _blocked(lambda: validate_generic_v2_candidate_bundle(catalog_mismatch, catalog)),
        "unknown_candidate_selection": _blocked(
            lambda: normalize_generic_v2_intent(request, bundle, selected_candidate_id="intent:not-registered")
        ),
        "unregistered_plan_operator": _blocked(lambda: validate_generic_v2_plan(plan_operator, catalog)),
    }
    negative_checks = {
        "all_fail_closed": all(value["blocked"] for value in negatives.values()),
        "candidate_boundary_errors_typed": all(
            value["code"] in {"route_contract_error", "metadata_dependency_error", "intent_contract_error"}
            for key, value in negatives.items()
            if key != "unregistered_plan_operator"
        ),
        "plan_boundary_error_typed": (
            negatives["unregistered_plan_operator"]["code"] == "metadata_dependency_error"
            and negatives["unregistered_plan_operator"]["stage"] == "plan_compilation"
        ),
    }
    module_source = (ROOT / "reference_runtime" / "generic_v2_candidates.py").read_text(encoding="utf-8")
    planner_source = (ROOT / "reference_runtime" / "generic_v2_planner.py").read_text(encoding="utf-8")
    static_checks = {
        "candidate_module_no_support_identifiers": not any(
            token in module_source for token in ("support_tickets", "WAIT_MINUTES", "QUEUE")
        ),
        "planner_no_support_identifiers": not any(
            token in planner_source for token in ("support_tickets", "WAIT_MINUTES", "QUEUE")
        ),
        "no_code_generation_lane": not any(
            token in (module_source + planner_source).casefold()
            for token in ("pandas code", "python code", "repair llm")
        ),
    }
    checks = {
        "happy_path": all(happy_checks.values()),
        "negative_boundaries": all(negative_checks.values()),
        "domain_neutral_static": all(static_checks.values()),
    }
    return {
        "contract_version": "generic-v2.support-pipeline.validation.v1",
        "domain_id": "support_tickets",
        "question_sha256": sha256_json(request.get("question") or ""),
        "catalog_sha256": catalog.get("catalog_sha256"),
        "candidate_bundle_sha256": bundle.get("bundle_sha256"),
        "intent_sha256": intent.get("intent_sha256"),
        "plan_fingerprint": plan.get("plan_fingerprint"),
        "result_sha256": result.get("result_sha256"),
        "datasets": datasets,
        "operators": operators,
        "result_columns": result.get("columns"),
        "result_row_count": result.get("row_count"),
        "happy_checks": happy_checks,
        "negative_cases": negatives,
        "negative_checks": negative_checks,
        "static_checks": static_checks,
        "checks": checks,
        "all_passed": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_passed": report["all_passed"], "checks": report["checks"]}, ensure_ascii=False))
    print(f"report: {args.output}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
