"""Run OS01/OS02/OS08 through the real Langflow Data Analysis Flow.

This gate is intentionally ordered after the HTTP authoring E2E: it requires
the active ``order_sales/e2e_validation`` pointer produced from natural text.
The Flow uses its trusted inline retrieval lane for the synthetic fixture.
Reports keep only bounded result projections and hashes, never raw HTTP bodies,
provider credentials, or the full source payload.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.flow_builder_support import BuildContractError, sha256_file, write_json_atomic
from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    assert_secret_absent,
    gemini_model_contract_evidence,
    langflow_gemini_contract_evidence,
    load_dotenv_values,
)
from tools.validate_langflow_http_e2e import (
    _auth_headers,
    _bounded_error,
    _canonical_responses,
    _run_url,
    _upload_flow,
    extract_terminal_evidence,
)


DEFAULT_FLOW = ROOT / "flow_exports" / "metadata_v6_data_analysis_flow_v6_standalone.json"
DEFAULT_SAMPLE = ROOT / "metadata" / "domain_packs" / "order_sales" / "sample_rows.json"
DEFAULT_OUTPUT = ROOT / "validation_outputs" / "langflow_http_order_sales_e2e.json"
REFERENCE_INSTANT = "2026-07-02T09:00:00+09:00"


CASES: tuple[dict[str, Any], ...] = (
    {
        "case_id": "OS01",
        "question": "오늘 전체 주문의 매출액 합계를 알려줘",
        "expected_datasets": ["orders"],
        "expected_operators": ["filter.v1", "aggregate.v1", "project.v1"],
        "expected_columns": ["SALES_AMOUNT"],
        "expected_rows": [{"SALES_AMOUNT": 1200.0}],
    },
    {
        "case_id": "OS02",
        "question": "오늘 매출액 상위 3개 상품을 상품명과 함께 보여줘",
        "expected_datasets": ["orders", "products"],
        "expected_operators": ["filter.v1", "aggregate.v1", "join.v1", "rank.v1", "project.v1"],
        "expected_columns": ["PRODUCT_ID", "PRODUCT_NAME", "SALES_AMOUNT"],
        "expected_rows": [
            {"PRODUCT_ID": "P-300", "PRODUCT_NAME": "Gamma", "SALES_AMOUNT": 1000.0},
            {"PRODUCT_ID": "P-400", "PRODUCT_NAME": "Delta", "SALES_AMOUNT": 200.0},
        ],
    },
    {
        "case_id": "OS08",
        "question": "오늘 상품별 매출액과 환불액을 조인해서 순매출액을 계산해줘",
        "expected_datasets": ["orders", "refunds"],
        "expected_operators": ["filter.v1", "join.v1", "aggregate.v1", "derive.v1", "project.v1"],
        "expected_columns": ["PRODUCT_ID", "SALES_AMOUNT", "REFUND_AMOUNT", "NET_SALES_AMOUNT"],
        "expected_rows": [
            {
                "PRODUCT_ID": "P-300",
                "SALES_AMOUNT": 1000.0,
                "REFUND_AMOUNT": 300.0,
                "NET_SALES_AMOUNT": 700.0,
            },
            {
                "PRODUCT_ID": "P-400",
                "SALES_AMOUNT": 200.0,
                "REFUND_AMOUNT": 0.0,
                "NET_SALES_AMOUNT": 200.0,
            },
        ],
    },
)


def _active_pointer(
    mongo_uri: str,
    database_name: str,
    *,
    domain_id: str,
    environment: str,
) -> dict[str, Any]:
    from pymongo import MongoClient

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    try:
        document = client[database_name]["agent_v6_metadata_active"].find_one(
            {"_id": f"active:{environment}:{domain_id}"}
        ) or {}
    finally:
        client.close()
    if not document:
        raise BuildContractError("order_sales_active_pointer_missing_run_authoring_first")
    checks = {
        "contract_version": document.get("contract_version") == "metadata.active-domain-pointer.v1",
        "domain_id": document.get("domain_id") == domain_id,
        "environment": document.get("environment") == environment,
        "active_status": document.get("status") == "active",
        "revision_positive": int(document.get("revision") or 0) >= 1,
        "package_hash_present": len(str(document.get("package_sha256") or "")) == 64,
        "bundle_hash_present": len(str(document.get("bundle_sha256") or "")) == 64,
    }
    if not all(checks.values()):
        raise BuildContractError("order_sales_active_pointer_invalid")
    return {
        "revision": int(document["revision"]),
        "package_sha256": str(document["package_sha256"]),
        "bundle_sha256": str(document["bundle_sha256"]),
        "checks": checks,
    }


def _inline_fixture(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    datasets = payload.get("datasets") if isinstance(payload.get("datasets"), dict) else {}
    order_products = {
        str(row.get("order_id") or ""): str(row.get("product_id") or "")
        for row in datasets.get("orders", [])
        if isinstance(row, dict) and row.get("order_id")
    }
    # Natural authoring declares PRODUCT_ID on refunds.  The shipped synthetic
    # fixture historically omitted that redundant physical value, so enrich it
    # only in-memory from the registered ORDER_ID relation for this HTTP gate.
    for row in datasets.get("refunds", []):
        if isinstance(row, dict) and not row.get("product_id"):
            product_id = order_products.get(str(row.get("order_id") or ""))
            if product_id:
                row["product_id"] = product_id
    return payload


def _matches_rows(actual: list[Any], expected: list[dict[str, Any]]) -> bool:
    if len(actual) != len(expected):
        return False
    for actual_row, expected_row in zip(actual, expected, strict=True):
        if not isinstance(actual_row, dict):
            return False
        if set(actual_row) != set(expected_row) or actual_row != expected_row:
            return False
    return True


def _json_input_tweak(value: dict[str, Any]) -> dict[str, Any]:
    """Copy a scalar NestedDict input for a Langflow 1.9.2 Flow tweak.

    Physical rows are deliberately a scalar node setting, not a handle input:
    Langflow ignores static/tweaked values on handle-only ``DataInput`` fields.
    """

    return deepcopy(value)


def _run_case(
    client: requests.Session,
    headers: dict[str, str],
    server_url: str,
    flow_id: str,
    case: dict[str, Any],
    *,
    source_payload: dict[str, Any],
    domain_id: str,
    environment: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    session_id = f"v6-http-order-sales-{case['case_id'].lower()}-{uuid.uuid4().hex}"
    tweaks = {
        "domain_bundle_loader": {
            "domain_id": domain_id,
            "environment": environment,
            "metadata_source_mode": "v6_active",
        },
        "request_state_capsule": {
            "reference_instant": REFERENCE_INSTANT,
            # Validation-only opt-in. Production Flow export must stay false.
            "allow_anonymous_multiturn": True,
        },
        "retrieval_job_router": {"data_mode": "inline"},
        "inline_source_retriever": {
            "source_payload": _json_input_tweak(source_payload),
            "source_row_limit": 50000,
            "source_memory_limit_mb": 16,
        },
        "answer_facts_narrative": {"narrative_enabled": False},
        "response_state_commit": {"allow_anonymous_multiturn": True},
        "intent_language_model": {"temperature": 0.0, "stream": False},
    }
    response = client.post(
        _run_url(server_url, flow_id, headers),
        headers={**headers, "Content-Type": "application/json"},
        json={
            "input_value": str(case["question"]),
            "input_type": "chat",
            "output_type": "any",
            "session_id": session_id,
            "tweaks": tweaks,
        },
        timeout=timeout_seconds,
    )
    http_sha256 = sha256(response.content).hexdigest()
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise BuildContractError("langflow_run_response_invalid")
    terminal = extract_terminal_evidence(payload)
    canonical = _canonical_responses(payload)
    primary = canonical[0] if len(canonical) == 1 else {}
    data = primary.get("data") if isinstance(primary.get("data"), dict) else {}
    rows = data.get("rows") if isinstance(data.get("rows"), list) else []
    columns = data.get("columns") if isinstance(data.get("columns"), list) else []
    analysis = primary.get("analysis") if isinstance(primary.get("analysis"), dict) else {}
    error = analysis.get("error") if isinstance(analysis.get("error"), dict) else {}
    operation_ids = [
        str(item.get("operator_id") or "")
        for item in analysis.get("operation_trace", [])
        if isinstance(item, dict) and item.get("operator_id")
    ]
    trace = primary.get("trace") if isinstance(primary.get("trace"), dict) else {}
    datasets = [
        str(item.get("dataset_key") or "")
        for item in trace.get("retrieval", [])
        if isinstance(item, dict) and item.get("dataset_key")
    ]
    persistence = terminal.get("persistence_contract") or {}
    checks = {
        "http_200": response.status_code == 200,
        "status_ok": terminal["status"] == "ok",
        "route_deterministic": terminal["route"] == "deterministic",
        "intent_llm_zero": terminal["usage"]["intent_llm_calls"] == 0,
        "answer_llm_zero": terminal["usage"]["answer_llm_calls"] == 0,
        "pandas_code_llm_zero": terminal["usage"]["pandas_code_llm_calls"] == 0,
        "pandas_repair_llm_zero": terminal["usage"]["pandas_repair_llm_calls"] == 0,
        "state_version_one": terminal["state_version"] == 1,
        "persistent_state_present": persistence.get("state_present") is True,
        "persistent_data_refs_present": int(persistence.get("data_ref_count") or 0) >= 1,
        "persistent_download_entries_exact": int(persistence.get("answer_download_count") or 0)
        == int(persistence.get("data_ref_count") or 0),
        "persistent_ref_ids_valid": persistence.get("all_data_ref_ids_valid") is True
        and persistence.get("all_download_ref_ids_valid") is True,
        "persistent_ref_sets_exact": persistence.get("download_refs_match_data_refs") is True,
        "persistent_analysis_ref_exact": persistence.get("one_analysis_result_ref") is True
        and persistence.get("state_ref_matches_analysis_result") is True
        and persistence.get("result_table_ref_matches_analysis_result") is True,
        "terminal_hash_equivalent": terminal["terminal_equivalent"] is True,
        "datasets_exact": datasets == case["expected_datasets"],
        "operators_covered": all(item in operation_ids for item in case["expected_operators"]),
        "columns_exact": columns == case["expected_columns"],
        "rows_exact": _matches_rows(rows, case["expected_rows"]),
    }
    return {
        "case_id": case["case_id"],
        "http_status": response.status_code,
        "http_response_sha256": http_sha256,
        "canonical_response_sha256": terminal["canonical_response_sha256"],
        "response_status": str(primary.get("status") or ""),
        "error_code": str(error.get("code") or "")[:80],
        "error_stage": str(error.get("stage") or "")[:80],
        "result_sha256": analysis.get("result_sha256"),
        "route": terminal["route"],
        "usage": terminal["usage"],
        "state_version": terminal["state_version"],
        "persistence_contract": persistence,
        "terminal_hashes": terminal["terminal_hashes"],
        "terminal_equivalent": terminal["terminal_equivalent"],
        "retrieval_datasets": datasets,
        "operator_ids": operation_ids,
        "columns": columns,
        "row_count": len(rows),
        "result_rows": [
            {key: row.get(key) for key in case["expected_columns"]}
            for row in rows
            if isinstance(row, dict)
        ],
        "checks": checks,
        "passed": all(checks.values()),
    }


def run(
    flow_path: Path,
    sample_path: Path,
    *,
    server_url: str,
    env_path: Path,
    domain_id: str,
    environment: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    env = load_dotenv_values(env_path)
    flow = json.loads(flow_path.read_text(encoding="utf-8"))
    flow_model_contract = langflow_gemini_contract_evidence(flow)
    if flow_model_contract.get("passed") is not True:
        raise BuildContractError("flow_gemini_model_contract_failed")
    mongo_uri = str(os.getenv("MONGODB_URI") or env.get("MONGODB_URI") or "").strip()
    database_name = str(os.getenv("MONGODB_DATABASE") or env.get("MONGODB_DATABASE") or "datagov").strip()
    langflow_key = str(os.getenv("LANGFLOW_API_KEY") or env.get("LANGFLOW_API_KEY") or "")
    if not mongo_uri:
        raise BuildContractError("mongodb_uri_not_configured")
    active = _active_pointer(
        mongo_uri,
        database_name,
        domain_id=domain_id,
        environment=environment,
    )
    source_payload = _inline_fixture(sample_path)
    source_payload_sha256 = sha256(
        json.dumps(source_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    client = requests.Session()
    headers = _auth_headers(client, server_url, env)
    uploaded = _upload_flow(client, headers, server_url, flow_path, timeout_seconds)
    rows: list[dict[str, Any]] = []
    for case in CASES:
        try:
            row = _run_case(
                client,
                headers,
                server_url,
                str(uploaded["id"]),
                case,
                source_payload=source_payload,
                domain_id=domain_id,
                environment=environment,
                timeout_seconds=timeout_seconds,
            )
        except Exception as exc:
            row = {"case_id": case["case_id"], "failure": _bounded_error(exc), "passed": False}
        rows.append(row)
    report = {
        "contract_version": "langflow.http.order-sales.validation.v1",
        "model": DEFAULT_GEMINI_MODEL,
        "model_contract": gemini_model_contract_evidence(),
        "flow_model_contract": flow_model_contract,
        "flow_file": flow_path.name,
        "flow_sha256": sha256_file(flow_path),
        "uploaded_flow_id": str(uploaded.get("id") or ""),
        "domain_id": domain_id,
        "environment": environment,
        "metadata_source_mode": "v6_active",
        "data_mode": "inline",
        "reference_instant": REFERENCE_INSTANT,
        "active_pointer": active,
        "source_payload_sha256": source_payload_sha256,
        "source_payload_persisted": False,
        "raw_http_responses_persisted": False,
        "secrets_persisted": False,
        "case_count": len(rows),
        "passed": sum(1 for row in rows if row.get("passed") is True),
        "failed": sum(1 for row in rows if row.get("passed") is not True),
        "rows": rows,
    }
    report["all_passed"] = report["failed"] == 0
    assert_secret_absent(report, mongo_uri)
    assert_secret_absent(report, langflow_key)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow", type=Path, default=DEFAULT_FLOW)
    parser.add_argument("--sample", type=Path, default=DEFAULT_SAMPLE)
    parser.add_argument("--server-url", default="http://127.0.0.1:7873")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--domain-id", default="order_sales")
    parser.add_argument("--environment", default="e2e_validation")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        report = run(
            args.flow.resolve(),
            args.sample.resolve(),
            server_url=args.server_url,
            env_path=args.env_file.resolve(),
            domain_id=args.domain_id,
            environment=args.environment,
            timeout_seconds=max(60, min(args.timeout_seconds, 600)),
        )
    except Exception as exc:
        report = {
            "contract_version": "langflow.http.order-sales.validation.v1",
            "all_passed": False,
            "failure": _bounded_error(exc),
        }
    write_json_atomic(args.output.resolve(), report)
    print(
        json.dumps(
            {key: report.get(key) for key in ("domain_id", "environment", "case_count", "passed", "failed", "all_passed")},
            ensure_ascii=False,
        )
    )
    print(f"report: {args.output}")
    return 0 if report.get("all_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
