from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from reference_runtime.canonical import ContractError
from reference_runtime.dummy_data import (
    canonical_rows_for_dataset,
    physical_rows_for_dataset,
    source_result_for_dataset,
    source_results_for_jobs,
)
from reference_runtime.engine import AnalysisEngine
from reference_runtime.metadata_compiler import build_runtime_catalog
from reference_runtime.source_contracts import (
    canonicalize_rows,
    compute_bundle_sha256,
    executor_frames,
    merge_source_results,
    validate_source_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
CATALOG = build_runtime_catalog(ROOT / "metadata" / "authoring")


def test_target_mode_and_plan_quantities_canonicalize_once() -> None:
    physical = physical_rows_for_dataset("target")
    canonical, schema = canonicalize_rows("target", physical, CATALOG, physical_schema=physical[0].keys())
    assert len(canonical) == len(physical)
    assert canonical[0]["MODE"] == physical[0]["Mode"]
    assert canonical[0]["INPUT_PLAN_QTY"] == physical[0]["INPUT 계획"]
    assert "Mode" not in canonical[0]
    assert "INPUT 계획" not in canonical[0]
    assert {field["field"] for field in schema} == set(CATALOG["datasets"]["target"]["fields"])


def test_equipment_oper_nm_maps_to_canonical_oper_name() -> None:
    rows = physical_rows_for_dataset("equipment_assign")
    assert "OPER_NM" in rows[0] and "OPER_NAME" not in rows[0]
    canonical = canonical_rows_for_dataset("equipment_assign", CATALOG)
    assert canonical[0]["OPER_NAME"] == rows[0]["OPER_NM"]
    assert "OPER_NM" not in canonical[0]


def test_primary_and_alias_collision_is_fail_closed() -> None:
    row = deepcopy(physical_rows_for_dataset("target")[0])
    row["MODE"] = row["Mode"]
    with pytest.raises(ContractError) as exc:
        canonicalize_rows("target", [row], CATALOG, physical_schema=row.keys())
    assert exc.value.code == "ambiguous_field_binding"


def test_missing_physical_metric_does_not_fallback_to_canonical_name() -> None:
    row = deepcopy(physical_rows_for_dataset("production_today")[0])
    row["PRODUCTION_QTY"] = row.pop("PRODUCTION")
    with pytest.raises(ContractError) as exc:
        canonicalize_rows("production_today", [row], CATALOG, physical_schema=row.keys())
    assert exc.value.code == "source_schema_mismatch"
    assert exc.value.details["field"] == "PRODUCTION_QTY"


def test_hold_timestamp_is_strict_and_timezone_bound() -> None:
    canonical = canonical_rows_for_dataset("hold_history", CATALOG)
    assert canonical[0]["HOLD_EVENT_AT"].endswith("+09:00")
    row = deepcopy(physical_rows_for_dataset("hold_history")[0])
    row["HOLD_TM"] = "not-a-time"
    with pytest.raises(ContractError) as exc:
        canonicalize_rows("hold_history", [row], CATALOG, physical_schema=row.keys())
    assert exc.value.code == "source_schema_mismatch"
    assert exc.value.details["field"] == "HOLD_EVENT_AT"


def test_all_registered_dummy_datasets_round_trip_physical_to_canonical() -> None:
    for dataset_key in CATALOG["datasets"]:
        physical = physical_rows_for_dataset(dataset_key)
        canonical = canonical_rows_for_dataset(dataset_key, CATALOG)
        assert physical
        assert len(canonical) == len(physical)
        assert set(canonical[0]) == set(CATALOG["datasets"][dataset_key]["fields"])


def test_merge_combines_chunks_deterministically_and_returns_minimal_executor_frames() -> None:
    physical = physical_rows_for_dataset("hold_history")
    first = source_result_for_dataset("hold_history", source_alias="history", rows=physical[:2], chunk_index=1)
    second = source_result_for_dataset("hold_history", source_alias="history", rows=physical[2:], chunk_index=2)
    bundle = merge_source_results([second, first], CATALOG)
    assert bundle["contract_version"] == "source.bundle.v1"
    assert bundle["frames"]["history"]["row_count"] == len(physical)
    assert bundle["frames"]["history"]["chunk_count"] == 2
    assert bundle["frames"]["history"]["rows"][0]["HOLD_CD"] == physical[0]["HOLD_CD"]
    assert bundle["bundle_sha256"] == compute_bundle_sha256(bundle)
    assert executor_frames(bundle, CATALOG) == {
        "history": {
            "rows": bundle["frames"]["history"]["rows"],
            "columns": [item["field"] for item in bundle["frames"]["history"]["schema"]],
        }
    }


def test_executor_frames_can_share_owned_snapshot_rows() -> None:
    result = source_result_for_dataset("production_today", source_alias="production")
    bundle = merge_source_results([result], CATALOG)
    snapshot_rows = bundle["frames"]["production"]["rows"]

    isolated = executor_frames(bundle, CATALOG)
    shared = executor_frames(bundle, CATALOG, copy_rows=False)

    assert isolated["production"]["rows"] is not snapshot_rows
    assert shared["production"]["rows"] is snapshot_rows
    assert shared["production"]["rows"] == snapshot_rows


def test_duplicate_source_result_and_error_status_are_not_silently_treated_as_empty() -> None:
    result = source_result_for_dataset("production_today", source_alias="production")
    with pytest.raises(ContractError) as exc:
        merge_source_results([result, deepcopy(result)], CATALOG)
    assert exc.value.code == "duplicate_source_result"

    failed = {
        "contract_version": "source.result.v1",
        "source_result_id": "failed:1",
        "source_alias": "production",
        "dataset_key": "production_today",
        "status": "error",
        "error": {"code": "source_timeout", "retryable": True},
    }
    with pytest.raises(ContractError) as exc:
        merge_source_results([failed], CATALOG)
    assert exc.value.code == "source_timeout"
    assert exc.value.retryable is True


def test_bundle_cannot_be_recanonicalized_or_hash_tampered() -> None:
    result = source_result_for_dataset("production_today", source_alias="production")
    bundle = merge_source_results([result], CATALOG)
    with pytest.raises(ContractError) as exc:
        merge_source_results([bundle], CATALOG)
    assert exc.value.code == "source_already_canonicalized"

    tampered = deepcopy(bundle)
    tampered["frames"]["production"]["rows"][0]["PRODUCTION_QTY"] = 999_999
    with pytest.raises(ContractError) as exc:
        validate_source_bundle(tampered, CATALOG)
    assert exc.value.code == "source_schema_mismatch"


def test_dummy_jobs_apply_canonical_date_and_filter_to_physical_results() -> None:
    results = source_results_for_jobs(
        [
            {
                "job_id": "input-l267",
                "source_alias": "input",
                "dataset_key": "production_today",
                "parameters": {"DATE": "2026-07-30"},
                "filters": {
                    "op": "all",
                    "clauses": [
                        {"field": "OPER_NAME", "operator": "eq", "value": "INPUT"},
                        {"field": "MCP_NO", "operator": "starts_with", "value": "L-267"},
                    ],
                },
            }
        ],
        CATALOG,
    )
    assert len(results) == 1
    assert results[0]["status"] == "ok"
    assert results[0]["row_count"] == 1
    assert results[0]["rows"][0]["MCP_NO"] == "L-267A1"


def test_empty_is_distinct_from_failure_and_keeps_schema_contract() -> None:
    result = source_result_for_dataset("production", source_alias="none", rows=[])
    assert result["status"] == "empty"
    bundle = merge_source_results([result], CATALOG)
    assert bundle["frames"]["none"]["status"] == "empty"
    assert bundle["frames"]["none"]["rows"] == []
    assert bundle["frames"]["none"]["schema"]


def test_default_engine_consumes_dummy_alias_without_double_source_prefix() -> None:
    response = AnalysisEngine(catalog=CATALOG).analyze(
        "오늘 투입된 제품중 MCP NO가 L-267로 시작하는 제품의 INPUT 수량 알려줘",
        session_id="source-contract-q1",
        subject_id="tester",
        reference_instant="2026-07-30T09:00:00+09:00",
    )
    assert response["status"] == "ok"
    assert response["data"]["row_count"] == 1
    assert response["data"]["rows"][0]["MCP_NO"] == "L-267A1"
    assert response["data"]["rows"][0]["INPUT_QTY"] == 292.0
    assert response["trace"]["usage"]["intent_llm_calls"] == 0
    assert response["trace"]["usage"]["pandas_code_llm_calls"] == 0
