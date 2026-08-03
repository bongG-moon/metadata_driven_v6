from __future__ import annotations

from typing import Any

from reference_runtime.dummy_data import source_results_for_jobs
from reference_runtime.plan_compiler import (
    _lot_ids,
    build_candidate_bundle,
    compile_plan,
    load_runtime_catalog,
    resolve_intent,
    validate_plan,
)
from reference_runtime.request_literals import build_request_capsule
from reference_runtime.source_contracts import executor_frames, merge_source_results
from reference_runtime.typed_executor import TypedExecutor, validate_plan_integrity


REFERENCE_INSTANT = "2026-07-30T09:00:00+09:00"


def _compile_and_execute(
    question: str,
    *,
    prior_semantics: dict[str, Any] | None = None,
    prior_result: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    catalog = load_runtime_catalog()
    request = build_request_capsule(
        question,
        session_id="semantic-case-fixes",
        subject_id="test",
        reference_instant=REFERENCE_INSTANT,
        previous_state_ref="result:prior" if prior_result is not None else "",
    )
    candidates = build_candidate_bundle(
        request,
        catalog,
        prior_semantics=prior_semantics,
        prior_result=prior_result,
    )
    assert candidates["route_decision"]["route"] == "deterministic"
    intent, telemetry = resolve_intent(request, candidates)
    assert telemetry["intent_llm_calls"] == 0
    plan = validate_plan(
        compile_plan(intent, candidates, catalog, prior_result=prior_result),
        catalog,
    )
    source_results = source_results_for_jobs(plan["retrieval_jobs"], catalog)
    source_bundle = merge_source_results(source_results, catalog, plan["retrieval_jobs"])
    frames = executor_frames(source_bundle, catalog)
    result = TypedExecutor().execute(plan, frames)
    return intent, plan, result.rows


def test_generic_lot_labels_are_not_parsed_as_identifiers() -> None:
    assert _lot_ids("D/S1~D/A4 공정 Hold 된 Lot ID 알려줘") == []
    assert _lot_ids("WB & DA 공정 Hold Lot LIST알려줘") == []
    assert _lot_ids("LOT 목록을 보여줘") == []
    assert _lot_ids("LOT HOLD-A와 LOT L1001 이력") == ["HOLD-A", "L1001"]


def test_ordered_range_filter_consumes_the_range_result() -> None:
    _, plan, rows = _compile_and_execute("D/S1~D/A4 공정 Hold 된 Lot ID 알려줘")
    operations = {operation["id"]: operation for operation in plan["operations"]}
    specialized = operations["op_specialized_process_range"]
    assert specialized["op"] == "registered_call"
    assert specialized["function_ref"]["function_id"] == "manufacturing.filter_ordered_range"
    assert operations["op_filter_1"]["input"] == "op_specialized_process_range"
    assert {row["LOT_ID"] for row in rows} == {"HOLD-B", "HOLD-C"}


def test_registered_equipment_views_have_exact_grain_and_projection() -> None:
    intent, plan, uph_rows = _compile_and_execute(
        "현재 D/A1 공정의 장비 모델, Recipe, 공정, UPH를 보여줘"
    )
    assert intent["semantics"]["analysis_kind"] == "uph_detail"
    assert plan["retrieval_jobs"][0]["dataset_key"] == "eqp_uph"
    assert plan["result_contract"]["columns"] == ["EQP_MODEL", "RECIPE_ID", "OPER_NAME", "UPH"]
    assert [operation["op"] for operation in plan["operations"]] == ["filter", "project", "sort"]
    assert uph_rows == [
        {"EQP_MODEL": "EQM-HBM", "RECIPE_ID": "RCP-002", "OPER_NAME": "D/A1", "UPH": 88.2}
    ]

    intent, plan, grouped_rows = _compile_and_execute(
        "현재 D/A1 공정에 배정된 장비를 장비 모델과 Recipe 조합별로 보여줘"
    )
    assert intent["semantics"]["analysis_kind"] == "equipment_grouped"
    assert plan["retrieval_jobs"][0]["dataset_key"] == "equipment_assign"
    assert plan["result_contract"]["columns"] == ["EQP_MODEL", "RECIPE_ID", "EQP_COUNT", "EQP_LIST"]
    assert [operation["op"] for operation in plan["operations"]] == ["filter", "aggregate", "sort", "project"]
    assert all(row["EQP_COUNT"] == len(row["EQP_LIST"]) for row in grouped_rows)


def test_plain_process_metric_uses_process_grain_and_rg_join_is_nonempty() -> None:
    intent, plan, rows = _compile_and_execute("2026-07-01 W/BM 공정 생산량을 알려줘")
    assert intent["semantics"]["dimension_refs"] == ["OPER_NAME"]
    assert plan["result_contract"]["columns"] == ["OPER_NAME", "PRODUCTION_QTY"]
    assert rows == [{"OPER_NAME": "W/BM", "PRODUCTION_QTY": 321}]

    _, plan, rows = _compile_and_execute(
        "RG 32G DDR4 FBGA 96 DDP 제품 BG공정에서 생산량과 재공수량 알려줘"
    )
    product_calls = [
        operation for operation in plan["operations"]
        if operation.get("op") == "registered_call"
        and operation.get("function_ref", {}).get("function_id") == "manufacturing.match_product_tokens"
    ]
    assert len(product_calls) == 2
    assert {job["dataset_key"] for job in plan["retrieval_jobs"]} == {"production_today", "wip_today"}
    assert rows
    assert rows[0]["PRODUCTION_QTY"] == 423
    assert rows[0]["WIP_QTY"] == 827


def test_hold_duration_rank_includes_all_longest_ties_and_history() -> None:
    prior_semantics = {
        "analysis_kind": "detail",
        "metric_refs": [],
        "dimension_refs": ["LOT_ID"],
        "field_refs": [],
        "process_refs": [],
        "product_group_refs": [],
        "date": "2026-07-30",
        "reference_date": "2026-07-30",
    }
    prior_result = {
        "columns": ["LOT_ID"],
        "rows": [{"LOT_ID": "HOLD-A"}, {"LOT_ID": "HOLD-B"}, {"LOT_ID": "HOLD-C"}],
    }
    intent, plan, rows = _compile_and_execute(
        "HOLD 시간이 가장 오래된 LOT의 이력을 보여줘",
        prior_semantics=prior_semantics,
        prior_result=prior_result,
    )
    assert "HOLD_DURATION_HOURS" in intent["semantics"]["metric_refs"]
    derive = next(operation for operation in plan["operations"] if operation["op"] == "derive")
    assert derive["formula"]["expression"]["op"] == "datetime_diff_hours"
    rank = next(operation for operation in plan["operations"] if operation["op"] == "rank")
    assert rank["tie_policy"] == "include_all"
    assert rank["rank_by"] == [{"field": "HOLD_DURATION_HOURS", "direction": "desc", "nulls": "last"}]
    assert {row["LOT_ID"] for row in rows} == {"HOLD-B", "HOLD-C"}
    assert {row["HOLD_DURATION_HOURS"] for row in rows} == {4.0}
    event_times = [row["HOLD_EVENT_AT"] for row in rows]
    assert event_times == sorted(event_times, reverse=True)


def test_followup_plan_input_ref_is_included_in_identity_and_semantic_seal() -> None:
    catalog = load_runtime_catalog()
    bundle = {"bundle_sha256": "b" * 64}
    previous_rank_intent = {
        "intent_sha256": "a" * 64,
        "semantics": {
            "analysis_kind": "previous_rank",
            "metric_refs": ["PRODUCTION_QTY"],
            "rank": {"mode": "top", "limit": 1},
            "tie_policy": "include_all",
        },
    }
    previous_rank_result = {
        "columns": ["DEVICE", "PRODUCTION_QTY"],
        "rows": [
            {"DEVICE": "A", "PRODUCTION_QTY": 10},
            {"DEVICE": "B", "PRODUCTION_QTY": 10},
        ],
    }

    rank_plan = validate_plan(
        compile_plan(
            previous_rank_intent,
            bundle,
            catalog,
            prior_result=previous_rank_result,
        ),
        catalog,
    )

    assert rank_plan["input_refs"] == ["previous"]
    assert validate_plan_integrity(rank_plan) is rank_plan
    rank_rows = TypedExecutor().execute(
        rank_plan,
        {"previous": {"rows": previous_rank_result["rows"]}},
    ).rows
    assert {row["DEVICE"] for row in rank_rows} == {"A", "B"}

    product_keys = ["TECH", "DEN", "MODE", "PKG_TYPE1", "PKG_TYPE2", "LEAD", "MCP_NO"]
    equipment_intent = {
        "intent_sha256": "c" * 64,
        "semantics": {
            "analysis_kind": "equipment_enrich",
            "followup_mode": "referenced",
            "metric_refs": ["PRODUCTION_QTY"],
            "process_refs": [],
        },
    }
    equipment_result = {
        "columns": [*product_keys, "PRODUCTION_QTY"],
        "rows": [
            {
                **{key: f"value-{key}" for key in product_keys},
                "PRODUCTION_QTY": 10,
            }
        ],
    }

    equipment_plan = validate_plan(
        compile_plan(
            equipment_intent,
            bundle,
            catalog,
            prior_result=equipment_result,
        ),
        catalog,
    )

    assert equipment_plan["input_refs"] == ["previous"]
    assert validate_plan_integrity(equipment_plan) is equipment_plan
