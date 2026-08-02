"""Execute the non-manufacturing Domain Package through the exported Flow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.state_contracts import InMemoryStateStore
from tools.validate_langflow_equivalent_pipeline import execute_component_pipeline


DEFAULT_FLOW = ROOT / "flow_exports" / "metadata_v6_data_analysis_flow_v6_standalone.json"
PACKAGE_PATH = ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "domain_package.json"
SAMPLE_PATH = ROOT / "metadata" / "domain_packs" / "order_sales" / "sample_rows.json"


CASES: tuple[dict[str, Any], ...] = (
    {
        "case_id": "OS01",
        "question": "오늘 전체 주문의 매출액 합계를 알려줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders"],
        "expected_operators": ["filter", "aggregate"],
        "expected_output_fields": ["SALES_AMOUNT"],
        "expected_rows": [{"SALES_AMOUNT": 1200.0}],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS02",
        "question": "오늘 매출액 상위 3개 상품을 상품명과 함께 보여줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders", "products"],
        "expected_operators": ["filter", "aggregate", "join", "rank", "project"],
        "expected_output_fields": ["PRODUCT_ID", "PRODUCT_NAME", "SALES_AMOUNT"],
        "expected_rows": [
            {"PRODUCT_ID": "P-300", "PRODUCT_NAME": "Gamma", "SALES_AMOUNT": 1000.0},
            {"PRODUCT_ID": "P-400", "PRODUCT_NAME": "Delta", "SALES_AMOUNT": 200.0},
        ],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS03",
        "question": "오늘 매출액 하위 2개 상품을 알려줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders"],
        "expected_operators": ["filter", "aggregate", "rank", "project"],
        "expected_output_fields": ["PRODUCT_ID", "SALES_AMOUNT"],
        "expected_rows": [
            {"PRODUCT_ID": "P-400", "SALES_AMOUNT": 200.0},
            {"PRODUCT_ID": "P-300", "SALES_AMOUNT": 1000.0},
        ],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS04",
        "question": "오늘 매출액이 가장 큰 상품을 동률이면 모두 보여줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders"],
        "expected_operators": ["filter", "aggregate", "rank", "project"],
        "expected_output_fields": ["PRODUCT_ID", "SALES_AMOUNT"],
        "expected_rows": [{"PRODUCT_ID": "P-300", "SALES_AMOUNT": 1000.0}],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS05",
        "question": "오늘 매출액이 가장 작은 상품을 동률이면 모두 보여줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders"],
        "expected_operators": ["filter", "aggregate", "rank", "project"],
        "expected_output_fields": ["PRODUCT_ID", "SALES_AMOUNT"],
        "expected_rows": [{"PRODUCT_ID": "P-400", "SALES_AMOUNT": 200.0}],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS06",
        "question": "오늘 카테고리별 매출액을 큰 순서로 보여줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders", "products"],
        "expected_operators": ["filter", "join", "aggregate", "sort", "project"],
        "expected_output_fields": ["CATEGORY", "SALES_AMOUNT"],
        "expected_rows": [{"CATEGORY": "B", "SALES_AMOUNT": 1200.0}],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS07",
        "question": "어제 주문에서 주문번호, 주문일, 상품번호, 매출액 컬럼만 보여줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders"],
        "expected_operators": ["filter", "project"],
        "expected_output_fields": ["ORDER_ID", "ORDER_DATE", "PRODUCT_ID", "SALES_AMOUNT"],
        "expected_rows": [
            {"ORDER_ID": "O-001", "ORDER_DATE": "2026-07-01", "PRODUCT_ID": "P-100", "SALES_AMOUNT": 1000.0},
            {"ORDER_ID": "O-002", "ORDER_DATE": "2026-07-01", "PRODUCT_ID": "P-100", "SALES_AMOUNT": 1500.0},
            {"ORDER_ID": "O-003", "ORDER_DATE": "2026-07-01", "PRODUCT_ID": "P-200", "SALES_AMOUNT": 2500.0},
        ],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS08",
        "question": "오늘 상품별 매출액과 환불액을 조인해서 순매출액을 계산해줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders", "refunds"],
        "expected_operators": ["filter", "join", "aggregate", "derive", "project"],
        "expected_output_fields": ["PRODUCT_ID", "SALES_AMOUNT", "REFUND_AMOUNT", "NET_SALES_AMOUNT"],
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
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS09",
        "question": "오늘 상품별 매출액과 목표액, 달성률을 보여줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders", "targets"],
        "expected_operators": ["filter", "aggregate", "join", "derive", "project"],
        "expected_output_fields": ["PRODUCT_ID", "SALES_AMOUNT", "TARGET_AMOUNT", "ACHIEVEMENT_RATE"],
        "expected_rows": [
            {"PRODUCT_ID": "P-300", "SALES_AMOUNT": 1000.0, "TARGET_AMOUNT": 1000.0, "ACHIEVEMENT_RATE": 100.0},
            {"PRODUCT_ID": "P-400", "SALES_AMOUNT": 200.0, "TARGET_AMOUNT": 500.0, "ACHIEVEMENT_RATE": 40.0},
        ],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS10",
        "question": "오늘 매출액이 목표액보다 큰 상품만 보여줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders", "targets"],
        "expected_operators": ["filter", "aggregate", "join", "compare_fields", "project"],
        "expected_output_fields": ["PRODUCT_ID", "SALES_AMOUNT", "TARGET_AMOUNT"],
        "expected_rows": [],
        "expected_status": "empty",
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS11",
        "question": "전자 카테고리에서 매출액이 가장 큰 상품명을 알려줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders", "products"],
        "expected_operators": ["filter", "join", "aggregate", "rank", "project"],
        "expected_output_fields": ["PRODUCT_NAME", "SALES_AMOUNT"],
        "expected_rows": [
            {"PRODUCT_NAME": "Alpha", "SALES_AMOUNT": 2500.0},
            {"PRODUCT_NAME": "Beta", "SALES_AMOUNT": 2500.0},
        ],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS12",
        "question": "오늘 환불액이 0보다 큰 상품의 상품명과 환불액만 보여줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["refunds", "orders", "products"],
        "expected_operators": ["filter", "join", "project"],
        "expected_output_fields": ["PRODUCT_NAME", "REFUND_AMOUNT"],
        "expected_rows": [
            {"PRODUCT_NAME": "Alpha", "REFUND_AMOUNT": 500.0},
            {"PRODUCT_NAME": "Beta", "REFUND_AMOUNT": 100.0},
            {"PRODUCT_NAME": "Gamma", "REFUND_AMOUNT": 300.0},
        ],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS13",
        "question": "오늘 카테고리별 순매출액을 계산하고 업무 설명까지 한 문단으로 요약해줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "deterministic",
        "expected_datasets": ["orders", "refunds", "products"],
        "expected_operators": ["filter", "aggregate", "join", "derive", "project"],
        "expected_output_fields": ["CATEGORY", "NET_SALES_AMOUNT"],
        "expected_rows": [{"CATEGORY": "B", "NET_SALES_AMOUNT": 900.0}],
        "expected_model_calls": 1,
        "narrative_enabled": True,
        "expected_narrative_status": "verified",
    },
    {
        "case_id": "OS14",
        "question": "다음 달 상품별 매출을 예측해줘",
        "reference_instant": "2026-07-02T09:00:00+09:00",
        "expected_route": "unsupported",
        "expected_datasets": [],
        "expected_operators": [],
        "expected_output_fields": [],
        "expected_rows": [],
        "expected_model_calls": 0,
        "narrative_enabled": True,
        "expected_status": "error",
    },
    {
        "case_id": "OS-COMP-TOTAL",
        "question": "전체 매출 합계를 알려줘",
        "expected_rows": [{"SALES_AMOUNT": 6200.0}],
        "expected_output_fields": ["SALES_AMOUNT"],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS-COMP-TOP-TIES",
        "question": "전체 기간 매출이 가장 큰 상품을 동률 포함해서 보여줘",
        "expected_rows": [
            {"PRODUCT_ID": "P-100", "SALES_AMOUNT": 2500.0},
            {"PRODUCT_ID": "P-200", "SALES_AMOUNT": 2500.0},
        ],
        "expected_output_fields": ["PRODUCT_ID", "SALES_AMOUNT"],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS-COMP-BOTTOM",
        "question": "전체 기간 매출이 가장 작은 상품을 보여줘",
        "expected_rows": [{"PRODUCT_ID": "P-400", "SALES_AMOUNT": 200.0}],
        "expected_output_fields": ["PRODUCT_ID", "SALES_AMOUNT"],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS-COMP-NET",
        "question": "상품별 순매출을 보여줘",
        "expected_rows": [
            {"PRODUCT_ID": "P-100", "NET_SALES_AMOUNT": 2000.0},
            {"PRODUCT_ID": "P-200", "NET_SALES_AMOUNT": 2400.0},
            {"PRODUCT_ID": "P-300", "NET_SALES_AMOUNT": 700.0},
            {"PRODUCT_ID": "P-400", "NET_SALES_AMOUNT": 200.0},
        ],
        "expected_output_fields": ["PRODUCT_ID", "NET_SALES_AMOUNT"],
        "expected_model_calls": 0,
    },
    {
        "case_id": "OS-COMP-TARGET",
        "question": "상품별 목표 대비 매출 달성률을 보여줘",
        "expected_rows": [
            {"PRODUCT_ID": "P-100", "ACHIEVEMENT_RATE": 125.0},
            {"PRODUCT_ID": "P-200", "ACHIEVEMENT_RATE": 125.0},
            {"PRODUCT_ID": "P-300", "ACHIEVEMENT_RATE": 100.0},
            {"PRODUCT_ID": "P-400", "ACHIEVEMENT_RATE": 40.0},
        ],
        "expected_output_fields": ["PRODUCT_ID", "ACHIEVEMENT_RATE"],
        "expected_model_calls": 0,
    },
)


class ClaimSafeNarrativeModel:
    """A deterministic fake that makes no numeric or unregistered claim."""

    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, _prompt: Any) -> str:
        self.calls += 1
        return json.dumps(
            {
                "message": "등록된 실행 결과를 기준으로 요약했습니다.",
                "fact_ids": ["fact:row_count"],
            },
            ensure_ascii=False,
        )


def run(flow_path: Path) -> dict[str, Any]:
    flow = json.loads(flow_path.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
    sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    datasets = sample.get("datasets") if isinstance(sample.get("datasets"), dict) else {}
    refunds = [item for item in datasets.get("refunds", []) if isinstance(item, dict)]
    targets = [item for item in datasets.get("targets", []) if isinstance(item, dict)]
    runtime_catalog = package.get("runtime_catalog") if isinstance(package.get("runtime_catalog"), dict) else {}
    refunds_relation = ((runtime_catalog.get("relations") or {}).get("orders_refunds") or {})
    source_boundary_checks = {
        "refund_rows_present": bool(refunds),
        "refund_fields_exact": bool(refunds)
        and all(set(item) == {"order_id", "product_id", "refund_amount"} for item in refunds),
        "refund_date_absent": all("refund_date" not in item for item in refunds),
        "target_rows_present": bool(targets),
        "target_fields_exact": bool(targets)
        and all(set(item) == {"target_date", "product_id", "target_amount"} for item in targets),
        "target_month_absent": all("target_month" not in item for item in targets),
        "refund_relation_composite": refunds_relation.get("left_keys") == ["ORDER_ID", "PRODUCT_ID"]
        and refunds_relation.get("right_keys") == ["ORDER_ID", "PRODUCT_ID"],
        "refund_relation_optional_one": str(refunds_relation.get("cardinality") or "")
        in {"one_to_zero_or_one", "one_to_one_optional"},
    }
    rows: list[dict[str, Any]] = []
    for case in CASES:
        expected_model_calls = int(case.get("expected_model_calls") or 0)
        model = ClaimSafeNarrativeModel() if expected_model_calls else None
        value = execute_component_pipeline(
            flow,
            question=case["question"],
            session_id=f"order-sales:{case['case_id'].lower()}",
            domain_id="order_sales",
            inline_domain_bundle=package,
            inline_source_payload=sample,
            expected_rows=case["expected_rows"],
            reference_instant=case.get("reference_instant", "2026-07-30T09:00:00+09:00"),
            expected_route=case.get("expected_route"),
            expected_datasets=case.get("expected_datasets"),
            expected_operators=case.get("expected_operators"),
            expected_output_fields=case.get("expected_output_fields"),
            expected_retrieval_calls=len(case.get("expected_datasets") or [])
            if "expected_datasets" in case
            else None,
            language_model=model,
            expected_model_calls=expected_model_calls,
            narrative_enabled=bool(case.get("narrative_enabled", False)),
            expected_narrative_status=case.get("expected_narrative_status"),
            expected_status=str(case.get("expected_status") or "ok"),
        )
        rows.append(
            {
                "case_id": case["case_id"],
                "question_sha256": value["question_sha256"],
                "passed": value["passed"],
                "failures": value["failures"],
                "response_status": value["response_status"],
                "response_errors": value["response_errors"],
                "route": value["route"],
                "usage": value["usage"],
                "result_contract": value["result_contract"],
                "plan_contract": value["plan_contract"],
                "narrative_contract": value["narrative_contract"],
                "stage_counts": value["stage_counts"],
                "reference_instant": value["reference_instant"],
            }
        )

    shared_store = InMemoryStateStore()
    sales_isolation = execute_component_pipeline(
        flow,
        question="전체 매출 합계를 알려줘",
        session_id="isolation:order_sales",
        domain_id="order_sales",
        inline_domain_bundle=package,
        inline_source_payload=sample,
        expected_rows=[{"SALES_AMOUNT": 6200.0}],
        shared_state_store=shared_store,
        allow_anonymous_multiturn=True,
    )
    manufacturing_isolation = execute_component_pipeline(
        flow,
        question="오늘 투입된 제품중 MCP NO가 L-267로 시작하는 제품의 INPUT 수량 알려줘",
        session_id="isolation:manufacturing",
        domain_id="manufacturing",
        shared_state_store=shared_store,
        allow_anonymous_multiturn=True,
    )
    sales_state = shared_store.load_state("anonymous", "test:order_sales:isolation:order_sales")
    manufacturing_state = shared_store.load_state(
        "anonymous", "production:manufacturing:isolation:manufacturing"
    )
    isolation_checks = {
        "sales_flow_passed": sales_isolation.get("passed") is True,
        "manufacturing_flow_passed": manufacturing_isolation.get("passed") is True,
        "independent_state_versions": (sales_state or {}).get("state_version") == 1
        and (manufacturing_state or {}).get("state_version") == 1,
        "different_result_refs": bool((sales_state or {}).get("executed_result_ref"))
        and (sales_state or {}).get("executed_result_ref")
        != (manufacturing_state or {}).get("executed_result_ref"),
    }
    return {
        "contract_version": "order-sales.component.validation.v1",
        "domain_id": "order_sales",
        "package_sha256": package.get("package_sha256"),
        "bundle_sha256": package.get("bundle_sha256"),
        "catalog_sha256": (package.get("runtime_catalog") or {}).get("catalog_sha256"),
        "case_count": len(rows),
        "passed": sum(1 for row in rows if row["passed"]),
        "failed": sum(1 for row in rows if not row["passed"]),
        "rows": rows,
        "session_isolation": {
            "passed": all(isolation_checks.values()),
            "checks": isolation_checks,
        },
        "source_boundary_checks": source_boundary_checks,
        "all_passed": all(row["passed"] for row in rows)
        and all(isolation_checks.values())
        and all(source_boundary_checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow", type=Path, default=DEFAULT_FLOW)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs" / "order_sales_component_cases.json",
    )
    args = parser.parse_args()
    report = run(args.flow.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "case_count": report["case_count"],
                "passed": report["passed"],
                "failed": report["failed"],
                "session_isolation": report["session_isolation"]["passed"],
            },
            ensure_ascii=False,
        )
    )
    print(f"report: {args.output}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
