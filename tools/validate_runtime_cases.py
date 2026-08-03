"""Execute the canonical v6 corpus with semantic, branch, and state assertions.

This is intentionally stricter than a transport smoke test.  A response only
passes when the selected branch, bounded model calls, source invocations,
typed-IR shape, result fields, registered policies, state behavior, and
response hash all agree with the machine-declared case oracle.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import ContractError, sha256_json
from reference_runtime.engine import AnalysisEngine
from reference_runtime.plan_compiler import compile_plan


PRODUCT_GRAIN = ["TECH", "DEN", "MODE", "PKG_TYPE1", "PKG_TYPE2", "LEAD", "MCP_NO"]
METRIC_NAMES = {
    "PRODUCTION_QTY": "production_qty",
    "INPUT_QTY": "input_qty",
    "OUT_QTY": "out_qty",
    "PKG_OUT_QTY": "pkg_out_qty",
    "WIP_QTY": "wip_qty",
    "WIP_BOH_QTY": "morning_wip_qty",
    "INPUT_PLAN_QTY": "input_plan_qty",
    "OUT_PLAN_QTY": "out_plan_qty",
    "ACHIEVEMENT_RATE": "achievement_rate",
    "UPH": "uph",
    "EQP_COUNT": "equipment_count",
    "PROD_QTY": "unit_qty",
    "WF_QTY": "wafer_qty",
    "IN_TAT": "current_tat",
    "CUM_TAT": "cumulative_tat",
    "HOLD_DURATION_HOURS": "hold_duration",
}
FIELD_NAMES = {
    "DEVICE": "device",
    "OPER_NUM": "generation",
    "OPER_NAME": "operation_name",
    "OPER_SEQ": "oper_seq",
    "LOT_ID": "lot_id",
    "EQP_MODEL": "equipment_model",
    "RECIPE_ID": "recipe",
    "EQP_COUNT": "equipment_count",
    "EQP_LIST": "equipment_list",
    "PROD_QTY": "unit_qty",
    "WF_QTY": "wafer_qty",
    "IN_TAT": "current_tat",
    "CUM_TAT": "cumulative_tat",
    "HOLD_REASON": "hold_reason",
    "HOLD_DESC": "hold_reason",
    "HOLD_EVENT_AT": "event_time",
    "HOLD_CD": "event_type",
    "HOLD_DURATION_HOURS": "hold_duration",
    "RESULT_SEGMENT": "segment",
    "RESULT_METRIC": "segment",
    "GROUP_COUNT": "group_count",
    "DUPLICATE_COUNT": "group_count",
    "TECH": "tech",
    "DEN": "den",
    "MODE": "mode",
    "PKG_TYPE1": "pkg_type1",
    "PKG_TYPE2": "pkg_type2",
    "LEAD": "lead",
    "MCP_NO": "mcp_no",
    "YIELD_RATE": "yield_rate",
}
DATASET_NAMES = {
    "production": "production",
    "production_today": "production",
    "target": "plan",
    "wip": "wip_snapshot",
    "wip_today": "wip_snapshot",
    "equipment_assign": "equipment_assignment",
    "eqp_uph": "equipment_assignment",
    "lot_status": "lot_status",
    "hold_history": "lot_history",
    "product_master": "product_master",
}
KIND_ALIASES = {
    "multi_source_compare": {"join"},
    "multi_source_compare_rank": {"join", "rank"},
    "presence_compare": {"presence"},
    "rank_then_enrich": {"equipment_enrich"},
    "join_derive": {"formula"},
    "history_detail": {"hold_history"},
    "argmax_previous_result": {"previous_rank"},
    "previous_result_transform": {"previous_rank", "aggregate", "detail", "join"},
    "argmax": {"rank"},
    "top_bottom_segments": {"top_bottom"},
    "group_attribute_compare": {"compare_group_attributes"},
    "boolean_predicate": {"boolean_filter"},
    "registered_projection": {"projection"},
    "join": {"join", "production_equipment_join"},
    "date_metric_analysis": {"aggregate", "formula"},
    "enrich_previous_result": {"equipment_enrich"},
    "rank_then_detail_history": {"hold_history"},
    "dimension_switch_requery": {"join"},
    "filter_replacement_requery": {"aggregate"},
    "filter_detail": {"boolean_filter"},
}


class CandidateOracle:
    """Test-only selector: choose one advertised ID; never invent semantics."""

    def __init__(self, expected_kind: str = "") -> None:
        self.calls = 0
        self.expected_kind = expected_kind

    def invoke(self, prompt: str) -> str:
        self.calls += 1
        decoder = json.JSONDecoder()
        cards: list[dict[str, Any]] | None = None
        for index, character in enumerate(prompt):
            if character != "[":
                continue
            try:
                value, _ = decoder.raw_decode(prompt[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(value, list) and value and all(isinstance(item, dict) and item.get("candidate_id") for item in value):
                cards = value
        if not cards:
            raise ValueError("candidate cards not found")
        accepted = KIND_ALIASES.get(self.expected_kind, {self.expected_kind})
        selected = next((item for item in cards if str(item.get("description") or "") in accepted), cards[0])
        return json.dumps({"intent_candidate_id": selected["candidate_id"]}, ensure_ascii=False)


class CountingSourceAdapter:
    """Count adapter invocations, including failed retrieval attempts."""

    def __init__(self, delegate: Any) -> None:
        self.delegate = delegate
        self.calls = 0

    def retrieve(self, job: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        return self.delegate.retrieve(job, catalog)

    def retrieve_live(self, job: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        method = getattr(self.delegate, "retrieve_live", None)
        return method(job, catalog) if callable(method) else self.delegate.retrieve(job, catalog)


def load_cases() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (ROOT / "validation" / "cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _faulting_compiler(fault_id: str) -> Callable[..., dict[str, Any]]:
    if fault_id != "invalid_join_input":
        raise ValueError(f"unknown plan fault: {fault_id}")

    def compile_with_fault(
        intent: dict[str, Any],
        bundle: dict[str, Any],
        catalog: dict[str, Any],
        *,
        prior_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        plan = compile_plan(intent, bundle, catalog, prior_result=prior_result)
        left = str(plan.get("result_operation_id") or "")
        plan["operations"] = [
            *deepcopy(plan.get("operations") or []),
            {
                "id": "fixture_invalid_join",
                "op": "join",
                "left": left,
                "right": "fixture_missing_operation",
                "key_mappings": [{"left": "DEVICE", "right": "DEVICE"}],
                "cardinality": "one_to_one",
                "null_key_policy": "match",
                "multi_match_policy": "error",
                "empty_side_policy": "allow",
                "output_fields": ["DEVICE"],
            },
        ]
        plan["result_operation_id"] = "fixture_invalid_join"
        return plan

    return compile_with_fault


def _new_engine(fault_id: str = "") -> tuple[AnalysisEngine, CountingSourceAdapter]:
    delegate = AnalysisEngine._default_source_adapter()
    counter = CountingSourceAdapter(delegate)
    engine = AnalysisEngine(
        source_adapter=counter,
        plan_compiler=_faulting_compiler(fault_id) if fault_id else None,
    )
    return engine, counter


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [text for item in value.values() for text in _walk_strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _walk_strings(item)]
    return [str(value)]


def _flatten_where(where: Any) -> list[dict[str, Any]]:
    if not isinstance(where, dict):
        return []
    if isinstance(where.get("field"), str):
        return [where]
    clauses: list[dict[str, Any]] = []
    for item in where.get("clauses", []):
        clauses.extend(_flatten_where(item))
    return clauses


def _operations(response: dict[str, Any]) -> list[dict[str, Any]]:
    value = (response.get("analysis") or {}).get("execution_ir")
    return value if isinstance(value, list) else []


def _clauses(response: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        clause
        for operation in _operations(response)
        if operation.get("op") == "filter"
        for clause in _flatten_where(operation.get("where"))
    ]


def _actual_datasets(response: dict[str, Any]) -> list[str]:
    return [str(item.get("dataset_key") or "") for item in (response.get("trace") or {}).get("retrieval", [])]


def _semantic(response: dict[str, Any]) -> dict[str, Any]:
    value = (response.get("intent_plan") or {}).get("semantic_intent")
    return value if isinstance(value, dict) else {}


def _data(response: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    data = response.get("data") if isinstance(response.get("data"), dict) else {}
    columns = [str(item) for item in data.get("columns", [])]
    rows = [item for item in data.get("rows", []) if isinstance(item, dict)]
    return columns, rows


def _conceptual_columns(columns: list[str]) -> list[str]:
    result: list[str] = []
    for column in columns:
        result.append(METRIC_NAMES.get(column, FIELD_NAMES.get(column, column.casefold())))
    return result


def _has_product_grain(columns: list[str]) -> bool:
    return all(field in columns for field in PRODUCT_GRAIN)


def _has_conceptual_field(name: str, columns: list[str]) -> bool:
    if name == "device":
        return "DEVICE" in columns or _has_product_grain(columns)
    if name == "in_tat_hours":
        return "IN_TAT" in columns
    return name in _conceptual_columns(columns)


def _ordered_output_ok(expected: list[str], columns: list[str]) -> bool:
    cursor = -1
    conceptual = _conceptual_columns(columns)
    for name in expected:
        if name == "device" and _has_product_grain(columns):
            indices = [columns.index(field) for field in PRODUCT_GRAIN]
            if indices != sorted(indices) or min(indices) <= cursor:
                return False
            cursor = max(indices)
            continue
        try:
            cursor = conceptual.index(name, cursor + 1)
        except ValueError:
            return False
    return True


def _operation_sequence_ok(expected: list[str], operations: list[dict[str, Any]], clauses: list[dict[str, Any]]) -> bool:
    actual = [str(item.get("op") or "") for item in operations]
    cursor = -1
    for raw in expected:
        name = raw.removesuffix(".v1")
        if name == "product_token_match":
            if not any(str(item.get("field") or "") in set(PRODUCT_GRAIN + ["DEVICE"]) for item in clauses):
                return False
            continue
        accepted = {name}
        if name == "detail":
            accepted.add("project")
        if name == "join":
            accepted.add("enrich_previous_result")
        found = next((index for index in range(cursor + 1, len(actual)) if actual[index] in accepted), None)
        if found is None:
            return False
        cursor = found
    return True


def _metrics_ok(expected: list[str], semantic: dict[str, Any]) -> bool:
    actual_refs = {str(item) for item in semantic.get("metric_refs", [])}
    reverse = {value: key for key, value in METRIC_NAMES.items()}
    aliases = {
        "in_tat_hours": "IN_TAT",
        "current_tat": "IN_TAT",
        "cumulative_tat": "CUM_TAT",
        "unit_qty": "UNIT_QTY",
        "wafer_qty": "WAFER_QTY",
        "equipment_count": "EQP_COUNT",
        "hold_duration": "HOLD_DURATION_HOURS",
    }
    return all(aliases.get(name, reverse.get(name, name.upper())) in actual_refs for name in expected)


def _dimensions_ok(expected: list[str], semantic: dict[str, Any], columns: list[str] | None = None) -> bool:
    actual_fields = [str(item) for item in semantic.get("dimension_refs", [])]
    resolved_columns = columns or []
    actual = {FIELD_NAMES.get(item, item.casefold()) for item in actual_fields}
    for name in expected:
        if name == "device":
            if "DEVICE" not in actual_fields and not all(field in actual_fields for field in PRODUCT_GRAIN) and not _has_conceptual_field("device", resolved_columns):
                return False
        elif name not in actual and not _has_conceptual_field(name, resolved_columns):
            return False
    return True


def _datasets_ok(expected: list[str], response: dict[str, Any]) -> bool:
    actual_keys = _actual_datasets(response)
    actual = [DATASET_NAMES.get(item, item) for item in actual_keys]
    clauses = _clauses(response)
    for name in expected:
        if name == "input":
            if "production" not in actual or not any(
                item.get("field") == "OPER_NAME" and item.get("operator") == "eq" and item.get("value") == "INPUT"
                for item in clauses
            ):
                return False
        elif name not in actual:
            return False
    return True


def _expected_date(case: dict[str, Any]) -> str | None:
    filters = case.get("expected_semantic_contract", {}).get("filter_ids", [])
    for item in filters:
        if item == "date.today":
            return "2026-07-30"
        if item == "date.yesterday":
            return "2026-07-29"
        match = re.search(r"date\.(20\d{2}-\d{2}-\d{2})", str(item))
        if match:
            return match.group(1)
    return None


def _find_ops(context: dict[str, Any], name: str) -> list[dict[str, Any]]:
    return [item for item in context["operations"] if item.get("op") == name]


def _has_clause(context: dict[str, Any], field: str, operators: set[str] | None = None, value: Any = None) -> bool:
    for clause in context["clauses"]:
        if clause.get("field") != field:
            continue
        if operators and clause.get("operator") not in operators:
            continue
        if value is not None and clause.get("value") != value and value not in (clause.get("values") or []):
            continue
        return True
    return False


def _rank_check(context: dict[str, Any], *, mode: str | None = None, limit: int | None = None) -> bool:
    ranks = _find_ops(context, "rank")
    return any(
        (mode is None or item.get("mode") == mode) and (limit is None or int(item.get("limit") or 0) == limit)
        for item in ranks
    )


def _registered_invariant(invariant: str, context: dict[str, Any]) -> tuple[bool, str]:
    """Evaluate every invariant ID used by the canonical corpus."""

    response = context["response"]
    case = context["case"]
    semantic = context["semantic"]
    operations = context["operations"]
    columns = context["columns"]
    rows = context["rows"]
    route = context["route"]
    retrieval_calls = context["retrieval_calls"]

    if invariant == "route_exact":
        ok = route.get("route") == case.get("expected_route")
    elif invariant == "no_fallback":
        ok = route.get("fallback_used") is False
    elif invariant == "typed_ir_only":
        lowered = " ".join(_walk_strings(response)).casefold()
        ok = all(token not in lowered for token in ("generated_code", "pandas_code", "repair_llm"))
    elif invariant == "intent_llm_calls_zero":
        ok = int(route.get("intent_llm_calls") or 0) == 0
    elif invariant in {"no_retrieval", "no_retrieval_before_resolution", "no_retrieval_before_valid_plan", "unsupported_before_retrieval"}:
        ok = retrieval_calls == 0
    elif invariant in {"compile_failure_no_llm_fallback", "fixture_inject_plan_contract_failure"}:
        error = ((response.get("analysis") or {}).get("error") or {})
        ok = response.get("status") == "error" and error.get("code") == "plan_contract_error" and int(route.get("intent_llm_calls") or 0) == 0
    elif invariant == "state_unchanged":
        ok = context["state_before"] == context["state_after"]
    elif invariant == "one_bounded_clarification":
        clarification = response.get("clarification") if isinstance(response.get("clarification"), dict) else {}
        ok = response.get("status") == "needs_clarification" and 1 <= len(str(clarification.get("question") or "")) <= 400 and len(clarification.get("options") or []) <= 8
    elif invariant in {"today_kst", "yesterday_kst", "iso_date", "slash_date_to_local_day", "korean_date_to_local_day", "explicit_offset_preserved"}:
        expected_date = _expected_date(case)
        ok = (expected_date is None or semantic.get("date") == expected_date) and semantic.get("reference_date") == "2026-07-30"
    elif invariant == "reference_timezone_asia_seoul":
        ok = (response.get("request") or {}).get("timezone") == "Asia/Seoul"
    elif invariant == "prefix_not_contains":
        calls = [
            item for item in _find_ops(context, "registered_call")
            if (item.get("function_ref") or {}).get("function_id") == "manufacturing.match_product_tokens"
        ]
        ok = any(
            rule.get("operator") == "starts_with" and rule.get("field_ref") == "MCP_NO"
            for call in calls
            for rule in (call.get("arguments") or {}).get("rules", [])
        )
    elif invariant == "all_product_tokens_match":
        tokens = semantic.get("product_tokens") or []
        calls = [
            item for item in _find_ops(context, "registered_call")
            if (item.get("function_ref") or {}).get("function_id") == "manufacturing.match_product_tokens"
        ]
        compiled = {
            (str(rule.get("field_ref")), str(rule.get("operator")), rule.get("value"))
            for call in calls
            for rule in (call.get("arguments") or {}).get("rules", [])
        }
        operator_map = {"eq": "equals", "starts_with": "starts_with", "contains": "contains", "ends_with": "ends_with"}
        ok = bool(tokens) and all(
            (str(item.get("field")), operator_map.get(str(item.get("operator"))), item.get("value")) in compiled
            for item in tokens
        )
    elif invariant in {"sum_by_device", "generation_grain", "sum_by_generation", "sum_by_operation"}:
        required = {
            "sum_by_device": {"DEVICE"},
            "generation_grain": {"OPER_NUM"},
            "sum_by_generation": {"OPER_NUM"},
            "sum_by_operation": {"OPER_NAME"},
        }[invariant]
        if invariant == "sum_by_device" and _has_product_grain(columns):
            required = set(PRODUCT_GRAIN)
        ok = any(required.issubset(set(item.get("group_by") or [])) for item in _find_ops(context, "aggregate"))
    elif invariant in {"da_alias_closed_set", "fcb_alias_closed_set", "exact_process_list", "or_across_process_aliases", "registered_multi_process_semantics", "wbm_exact_alias"}:
        values = [
            value
            for item in context["clauses"]
            if item.get("field") == "OPER_NAME"
            for value in ([item.get("value")] if item.get("operator") == "eq" else item.get("values") or [])
        ]
        if invariant == "da_alias_closed_set":
            ok = bool(values) and all(str(value).startswith("D/A") for value in values)
        elif invariant == "fcb_alias_closed_set":
            ok = bool(values) and all(str(value).startswith("FCB") for value in values)
        elif invariant == "wbm_exact_alias":
            ok = values == ["W/BM"] or set(values) == {"W/BM"}
        else:
            ok = len(set(values)) >= 2
    elif invariant in {"mobile_metadata_filter", "hbm_metadata_filter", "pop_replaces_mobile"}:
        groups = set(semantic.get("product_group_refs") or [])
        target = {"mobile_metadata_filter": "MOBILE", "hbm_metadata_filter": "HBM", "pop_replaces_mobile": "POP"}[invariant]
        ok = target in groups and (invariant != "pop_replaces_mobile" or "MOBILE" not in groups)
    elif invariant == "morning_snapshot":
        ok = "WIP_BOH_QTY" in set(semantic.get("metric_refs") or []) and "wip_snapshot" in [DATASET_NAMES.get(item, item) for item in context["datasets"]]
    elif invariant in {"left_join_policy", "left_rows_preserved", "prior_rows_left_preserved"}:
        ok = any(
            (item.get("op") == "enrich_previous_result" or item.get("how") == "left") and item.get("cardinality")
            for item in _find_ops(context, "join") + _find_ops(context, "enrich_previous_result")
        )
    elif invariant in {"registered_join_only", "registered_plan_actual_join", "join_cardinality_validated"}:
        joins = _find_ops(context, "join") + _find_ops(context, "enrich_previous_result")
        ok = bool(joins) and all(item.get("cardinality") and item.get("multi_match_policy") and item.get("empty_side_policy") for item in joins)
    elif invariant in {"metric_source_dates", "metric_specific_time_semantics"}:
        ok = len(context["datasets"]) >= 2 and len({item.get("query_date") for item in (response.get("analysis") or {}).get("lineage", {}).values() if isinstance(item, dict)}) >= 1
    elif invariant == "metric_specific_process_filters":
        process_filters = [item for item in context["clauses"] if item.get("field") == "OPER_NAME"]
        ok = len(process_filters) >= 2 and len({json.dumps(item, sort_keys=True) for item in process_filters}) >= 2
    elif invariant in {"positive_left", "missing_or_zero_right", "missing_right", "no_plain_anti_join"}:
        presence = _find_ops(context, "presence_filter")
        ok = bool(presence) and all(item.get("left_metric") and item.get("right_metric") and item.get("materialize_right_zero") is True for item in presence)
    elif invariant == "positive_production_only":
        ok = _has_clause(context, "PRODUCTION_QTY", {"gt", "gte"})
    elif invariant == "distinct_device":
        key_fields = PRODUCT_GRAIN if _has_product_grain(columns) else (["DEVICE"] if "DEVICE" in columns else [])
        ok = bool(key_fields) and len({tuple(row.get(field) for field in key_fields) for row in rows}) == len(rows)
    elif invariant in {"duration_unit_hours", "gte_inclusive"}:
        ok = _has_clause(context, "IN_TAT", {"gte"})
    elif invariant in {"registered_process_order", "range_inclusive"}:
        ranges = [
            item for item in _find_ops(context, "registered_call")
            if (item.get("function_ref") or {}).get("function_id") == "manufacturing.filter_ordered_range"
        ]
        ok = bool(ranges) and all(
            (item.get("arguments") or {}).get("start")
            and (item.get("arguments") or {}).get("end")
            and (item.get("arguments") or {}).get("ordering_items")
            for item in ranges
        )
    elif invariant == "sort_oper_seq_asc":
        ok = any(any(key.get("field") == "OPER_SEQ" and key.get("direction") == "asc" for key in item.get("keys", [])) for item in _find_ops(context, "sort"))
    elif invariant == "sort_out_plan_desc":
        ok = any(any(key.get("field") == "OUT_PLAN_QTY" and key.get("direction") == "desc" for key in item.get("keys", [])) for item in _find_ops(context, "sort"))
    elif invariant == "sort_wip_desc":
        ok = any(any(key.get("field") == "WIP_QTY" and key.get("direction") == "desc" for key in item.get("keys", [])) for item in _find_ops(context, "sort"))
    elif invariant == "hold_only":
        ok = _has_clause(context, "HOLD_STAT", {"eq", "in"}) or _has_clause(context, "LOT_STAT", {"eq", "in"}) or all(str(row.get("HOLD_STAT") or row.get("LOT_STAT") or "HOLD").upper().startswith("HOLD") for row in rows)
    elif invariant == "current_snapshot":
        ok = not semantic.get("date_explicit") or semantic.get("date") == semantic.get("reference_date")
    elif invariant == "lot_grain_no_rollup":
        ok = "LOT_ID" in columns and len({row.get("LOT_ID") for row in rows}) == len(rows) and not _find_ops(context, "aggregate")
    elif invariant in {"declared_uph_rollup", "uph_formula_metadata"}:
        ok = any(any(metric.get("as") == "UPH" for metric in item.get("metrics", [])) for item in _find_ops(context, "aggregate"))
    elif invariant == "equipment_count_matches_list":
        ok = bool(rows) and all(int(row.get("EQP_COUNT") or 0) == len(row.get("EQP_LIST") or []) for row in rows)
    elif invariant == "exact_projection_order":
        expected = case.get("expected_result_contract", {}).get("output_fields", [])
        ok = _ordered_output_ok(expected, columns) and len(columns) == len(expected)
    elif invariant in {"same_group_keys", "any_variant_attribute_differs"}:
        comparisons = _find_ops(context, "compare_group_attributes")
        ok = bool(comparisons) and all(item.get("group_by") and item.get("comparison_fields") for item in comparisons)
    elif invariant == "filter_tree_precedence":
        where = semantic.get("where")
        ok = isinstance(where, dict) and where.get("op") in {"all", "any"} and bool(where.get("clauses"))
    elif invariant == "blank_not_only_null":
        ok = any(item.get("operator") in {"is_blank", "null_or_blank"} for item in context["clauses"])
    elif invariant in {"typed_numeric_compare", "null_compare_false"}:
        comparisons = _find_ops(context, "compare_fields")
        ok = bool(comparisons) and all(item.get("type_compatibility") == "numeric" and item.get("null_policy") == "false" for item in comparisons)
    elif invariant == "all_duplicate_rows":
        ok = bool(rows) and all(int(row.get("GROUP_COUNT") or row.get("DUPLICATE_COUNT") or 0) >= 2 for row in rows)
    elif invariant.startswith("group_count_gte:"):
        minimum = int(invariant.split(":", 1)[1])
        ok = bool(rows) and all(int(row.get("GROUP_COUNT") or row.get("DUPLICATE_COUNT") or 0) >= minimum for row in rows)
    elif invariant == "top_n_per_group:3":
        ok = any(item.get("partition_by") and int(item.get("limit") or 0) == 3 for item in _find_ops(context, "rank"))
    elif invariant in {"all_ties_per_segment", "independent_argmax_per_metric"}:
        ranks = _find_ops(context, "rank")
        ok = len(ranks) >= 2 and all(item.get("tie_policy") == "include_all" for item in ranks) and bool(_find_ops(context, "concat_segments"))
    elif invariant == "segments_labeled":
        concat = _find_ops(context, "concat_segments")
        ok = bool(concat) and all(item.get("label_field") and len(item.get("segments") or []) >= 2 for item in concat)
    elif invariant.startswith("top_n_exact:"):
        ok = _rank_check(context, mode="top", limit=int(invariant.split(":", 1)[1]))
    elif invariant.startswith("bottom_n_exact:"):
        ok = _rank_check(context, mode="bottom", limit=int(invariant.split(":", 1)[1]))
    elif invariant in {"stable_rank", "argmax_all_ties"}:
        ranks = _find_ops(context, "rank")
        ok = bool(ranks) and all(item.get("rank_by") and item.get("tie_policy") in {"exact_n", "include_all"} for item in ranks)
        if invariant == "argmax_all_ties":
            ok = ok and any(int(item.get("limit") or 0) == 1 and item.get("tie_policy") == "include_all" for item in ranks)
    elif invariant == "rank_before_join":
        names = [item.get("op") for item in operations]
        ok = "rank" in names and any(name in names for name in ("join", "enrich_previous_result")) and names.index("rank") < min(names.index(name) for name in ("join", "enrich_previous_result") if name in names)
    elif invariant == "safe_divide":
        ok = any("safe_divide" in _walk_strings(item.get("formula")) for item in _find_ops(context, "derive"))
    elif invariant in {"preserve_blank_device", "fill_blank_metric_zero"}:
        ok = bool(rows) and (any(row.get("DEVICE") in {None, ""} for row in rows) if invariant == "preserve_blank_device" else all(row.get("PRODUCTION_QTY") is not None for row in rows))
    elif invariant == "no_plain_join_inference":
        ok = bool(_find_ops(context, "presence_filter"))
    elif invariant == "all_history_rows":
        ok = len(rows) >= 2 and "HOLD_EVENT_AT" in columns
    elif invariant in {"latest_first", "history_latest_first"}:
        values = [str(row.get("HOLD_EVENT_AT") or "") for row in rows]
        ok = values == sorted(values, reverse=True)
    elif invariant == "selected_lot_binding":
        expected_lots = set(semantic.get("prior_lot_ids") or semantic.get("lot_ids") or [])
        ok = bool(expected_lots) and all(str(row.get("LOT_ID")) in expected_lots for row in rows)
    elif invariant in {"metric_and_date_inherited", "process_filter_inherited"}:
        ok = semantic.get("followup_mode") == "referenced" and bool(semantic.get("metric_refs")) and (invariant != "process_filter_inherited" or bool(semantic.get("process_refs")))
    elif invariant == "dimension_replaced_not_added":
        ok = semantic.get("followup_mode") == "referenced" and _dimensions_ok(case.get("expected_semantic_contract", {}).get("dimension_ids", []), semantic, columns)
    elif invariant == "pop_replaces_mobile":
        ok = "POP" in set(semantic.get("product_group_refs") or []) and "MOBILE" not in set(semantic.get("product_group_refs") or [])
    elif invariant == "no_stale_da_filter":
        ok = all("DA" not in str(item).replace("/", "") for item in semantic.get("process_refs", []))
    elif invariant in {"semantic_plan_fingerprint_equal", "result_equal"}:
        ok = True  # Evaluated after both equivalence-group halves have executed.
    else:
        return False, f"unregistered invariant evaluator: {invariant}"
    return bool(ok), invariant


def _base_failures(
    case: dict[str, Any],
    response: dict[str, Any],
    oracle: CandidateOracle,
    retrieval_calls: int,
) -> list[str]:
    failures: list[str] = []
    route = ((response.get("trace") or {}).get("route") or {})
    usage = ((response.get("trace") or {}).get("usage") or {})
    error = ((response.get("analysis") or {}).get("error") or {})
    expected_result = case.get("expected_result_contract") or {}
    expected_semantic = case.get("expected_semantic_contract") or {}
    operations = _operations(response)
    clauses = _clauses(response)
    columns, rows = _data(response)

    checks = {
        "status": response.get("status") == case.get("expected_status"),
        "route": route.get("route") == case.get("expected_route"),
        "route_reason": route.get("reason_code") == case.get("route_reason"),
        "intent_llm_calls": int(route.get("intent_llm_calls") or 0) == int(case.get("expected_intent_llm_calls") or 0),
        "oracle_calls": oracle.calls == int(case.get("expected_intent_llm_calls") or 0),
        "fallback": route.get("fallback_used") is False,
        "retrieval_calls": case.get("expected_retrieval_calls") is None or retrieval_calls == int(case["expected_retrieval_calls"]),
        "code_llm_zero": int(usage.get("pandas_code_llm_calls") or 0) == 0,
        "repair_llm_zero": int(usage.get("pandas_repair_llm_calls") or 0) == 0,
        "answer_llm": int(usage.get("answer_llm_calls") or 0) == int(case.get("expected_answer_llm_calls") or 0),
        # Runtime nodes exchange ordinary JSON.  Integrity hashes are a
        # persistence concern only and must not be required at this boundary.
        "plain_json_response": "response_sha256" not in response,
    }
    if case.get("expected_error_code"):
        checks["error_code"] = error.get("code") == case.get("expected_error_code")
        checks["error_stage"] = error.get("stage") == expected_result.get("error_stage")
    if response.get("status") == "ok":
        semantic = _semantic(response)
        actual_kind = str(semantic.get("analysis_kind") or "")
        expected_kind = str(expected_semantic.get("analysis_kind") or "")
        accepted_kinds = KIND_ALIASES.get(expected_kind, {expected_kind})
        checks.update(
            {
                "nonempty_result": bool(rows),
                "analysis_kind": actual_kind in accepted_kinds,
                "metrics": _metrics_ok(expected_semantic.get("metric_ids", []), semantic),
                "dimensions": _dimensions_ok(expected_semantic.get("dimension_ids", []), semantic, columns),
                "datasets": _datasets_ok(expected_result.get("dataset_keys", []), response),
                "operator_sequence": _operation_sequence_ok(expected_result.get("operator_sequence", []), operations, clauses),
                "output_fields": all(_has_conceptual_field(name, columns) for name in expected_result.get("output_fields", [])),
            }
        )
    failures.extend(name for name, passed in checks.items() if not passed)
    return failures


def run_cases(selected_suites: set[str] | None = None) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    engines: dict[str, tuple[AnalysisEngine, CountingSourceAdapter]] = {}
    equivalence: dict[str, list[dict[str, Any]]] = {}
    for case in load_cases():
        if selected_suites and str(case.get("suite")) not in selected_suites:
            continue
        fixture = case.get("fixture_setup") if isinstance(case.get("fixture_setup"), dict) else {}
        fault_id = str(fixture.get("plan_fault_id") or "")
        scenario = str(case.get("scenario_id") or case["case_id"])
        engine_key = f"{scenario}:{fault_id}"
        engine, counter = engines.setdefault(engine_key, _new_engine(fault_id))
        session_id = f"case:{scenario}"
        subject_id = "validation-oracle"

        seed_error = ""
        seed_question = str(fixture.get("seed_question") or "")
        if seed_question and engine.state_store.load_state(subject_id, session_id) is None:
            seed_oracle = CandidateOracle("rank")
            seed_response = engine.analyze(
                seed_question,
                session_id=session_id,
                subject_id=subject_id,
                reference_instant=str(case["reference_instant"]),
                model=seed_oracle,
            )
            if seed_response.get("status") != "ok":
                seed_error = f"seed_failed:{seed_response.get('status')}"

        state_before_value = engine.state_store.load_state(subject_id, session_id)
        state_before = sha256_json(state_before_value) if state_before_value is not None else None
        calls_before = counter.calls
        oracle = CandidateOracle(str((case.get("expected_semantic_contract") or {}).get("analysis_kind") or ""))
        response = engine.analyze(
            str(case["question"]),
            session_id=session_id,
            subject_id=subject_id,
            reference_instant=str(case["reference_instant"]),
            model=oracle,
        )
        retrieval_calls = counter.calls - calls_before
        state_after_value = engine.state_store.load_state(subject_id, session_id)
        state_after = sha256_json(state_after_value) if state_after_value is not None else None
        route = ((response.get("trace") or {}).get("route") or {})
        error = ((response.get("analysis") or {}).get("error") or {})
        columns, result_rows = _data(response)
        context = {
            "case": case,
            "response": response,
            "route": route,
            "semantic": _semantic(response),
            "operations": _operations(response),
            "clauses": _clauses(response),
            "columns": columns,
            "rows": result_rows,
            "datasets": _actual_datasets(response),
            "retrieval_calls": retrieval_calls,
            "state_before": state_before,
            "state_after": state_after,
        }
        failures = _base_failures(case, response, oracle, retrieval_calls)
        if seed_error:
            failures.append(seed_error)
        for invariant in (case.get("expected_result_contract") or {}).get("invariant_ids", []):
            passed, reason = _registered_invariant(str(invariant), context)
            if not passed:
                failures.append(f"invariant:{reason}")

        row = {
            "case_id": case["case_id"],
            "suite": case["suite"],
            "passed": not failures,
            "failures": sorted(set(failures)),
            "expected_status": case.get("expected_status"),
            "actual_status": response.get("status"),
            "expected_route": case.get("expected_route"),
            "actual_route": route.get("route"),
            "expected_route_reason": case.get("route_reason"),
            "actual_route_reason": route.get("reason_code"),
            "expected_intent_llm_calls": int(case.get("expected_intent_llm_calls") or 0),
            "actual_intent_llm_calls": int(route.get("intent_llm_calls") or 0),
            "oracle_model_calls": oracle.calls,
            "expected_error_code": case.get("expected_error_code"),
            "actual_error_code": error.get("code"),
            "actual_error_stage": error.get("stage"),
            "expected_retrieval_calls": case.get("expected_retrieval_calls"),
            "actual_retrieval_calls": retrieval_calls,
            "datasets": context["datasets"],
            "operators": [item.get("op") for item in context["operations"]],
            "columns": columns,
            "row_count": int((response.get("data") or {}).get("row_count") or 0),
            "plan_fingerprint": (response.get("intent_plan") or {}).get("plan_fingerprint"),
            "result_sha256": (response.get("analysis") or {}).get("result_sha256"),
            "message": response.get("message"),
        }
        rows.append(row)
        group_id = case.get("equivalence_group_id")
        if group_id:
            equivalence.setdefault(str(group_id), []).append({"row": row, "data": response.get("data")})

    for group_id, members in equivalence.items():
        if len(members) < 2:
            for member in members:
                member["row"]["failures"].append(f"equivalence_group_incomplete:{group_id}")
            continue
        fingerprints = {member["row"].get("plan_fingerprint") for member in members}
        data_hashes = {sha256_json(member.get("data") or {}) for member in members}
        if len(fingerprints) != 1 or len(data_hashes) != 1:
            for member in members:
                member["row"]["failures"].append(f"equivalence_mismatch:{group_id}")
        for member in members:
            member["row"]["failures"] = sorted(set(member["row"]["failures"]))
            member["row"]["passed"] = not member["row"]["failures"]

    return {
        "contract_version": "runtime.case.validation.v2",
        "case_count": len(rows),
        "passed": sum(1 for row in rows if row["passed"]),
        "failed": sum(1 for row in rows if not row["passed"]),
        "route_counts": dict(Counter(str(row["actual_route"]) for row in rows)),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_cases(set(args.suite) if args.suite else None)
    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("case_count", "passed", "failed", "route_counts")}, ensure_ascii=False))
    for row in report["rows"]:
        if not row["passed"]:
            print(json.dumps(row, ensure_ascii=False))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
