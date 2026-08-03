"""Closed typed Execution IR interpreter.

The executor accepts only validated operation dictionaries.  It never evaluates
Python source, imports requested modules, or guesses physical column names.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable

import pandas as pd

from .canonical import ContractError, json_value, sha256_json
from .registered_functions import dispatch_registered_call


FILTER_ALIASES = {"ge": "gte", "le": "lte", "like": "contains"}
FILTER_OPERATORS = {
    "eq",
    "in",
    "ne",
    "not_in",
    "gt",
    "gte",
    "lt",
    "lte",
    "between",
    "contains",
    "starts_with",
    "ends_with",
    "is_null",
    "is_not_null",
    "is_blank",
    "is_not_blank",
    "null_or_blank",
}
AGGREGATIONS = {"sum", "mean", "min", "max", "count", "nunique", "median", "std", "var", "list_unique"}
JOIN_TYPES = {"inner", "left", "right", "outer", "semi", "anti"}
COMPARE_OPERATORS = {"eq", "ne", "gt", "gte", "lt", "lte"}


def validate_plan_integrity(plan: dict[str, Any]) -> dict[str, Any]:
    """Reject mutation of a sealed plan before any frame is touched.

    Small unit-test plans without ``analysis.plan.v1`` remain supported.  Every
    production plan carrying that version must have both identities recomputed
    from its complete executable material.
    """

    if not isinstance(plan, dict):
        raise ContractError("plan_contract_error", "execution", "Plan payload must be an object.")
    if plan.get("contract_version") != "analysis.plan.v1":
        return plan
    material = {
        key: value
        for key, value in plan.items()
        if key not in {"plan_id", "plan_fingerprint"}
    }
    jobs = material.get("retrieval_jobs") if isinstance(material.get("retrieval_jobs"), list) else []
    material = {**material, "retrieval_jobs": sorted(jobs, key=lambda item: str(item.get("job_id") or ""))}
    expected_id = f"plan:{sha256_json(material)}"
    semantic = {
        key: material[key]
        for key in (
            "catalog_sha256",
            "input_refs",
            "retrieval_jobs",
            "operations",
            "result_operation_id",
            "result_contract",
            "lineage",
        )
        if key in material
    }
    if plan.get("plan_id") != expected_id or plan.get("plan_fingerprint") != sha256_json(semantic):
        raise ContractError(
            "plan_contract_error",
            "execution",
            "Plan identity or semantic fingerprint does not match executable material.",
        )
    return plan


def _frame(value: Any) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value.copy(deep=False)
    if isinstance(value, list):
        return pd.DataFrame(value)
    if isinstance(value, dict) and isinstance(value.get("rows"), list):
        columns = [str(item) for item in value.get("columns", [])] if isinstance(value.get("columns"), list) else None
        return pd.DataFrame(value["rows"], columns=columns or None)
    raise ContractError("plan_contract_error", "execution", "실행 입력 테이블이 올바르지 않습니다.")


def _require_columns(frame: pd.DataFrame, fields: Iterable[str], operation_id: str) -> None:
    required = [str(field) for field in fields]
    missing = [field for field in required if field not in frame.columns]
    if missing:
        raise ContractError(
            "source_schema_mismatch",
            "execution",
            "실행에 필요한 canonical field가 없습니다.",
            {"operation_id": operation_id, "missing_fields": missing},
        )


def _is_blank(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype("string").fillna("").str.strip().eq("")


def _typed_series(series: pd.Series, semantic_type: str | None) -> pd.Series:
    kind = str(semantic_type or "").lower()
    if kind in {
        "number",
        "quantity",
        "integer",
        "float",
        "rate",
        "duration",
        "currency",
        "percent",
        "percentage",
        "ratio",
        "decimal",
    }:
        return pd.to_numeric(series, errors="coerce")
    if kind in {"date", "datetime", "timestamp"}:
        return pd.to_datetime(series, errors="coerce", utc=False)
    if kind in {"string", "identifier", "category", ""}:
        return series.astype("string")
    return series


def _filter_mask(frame: pd.DataFrame, tree: dict[str, Any], depth: int = 0) -> pd.Series:
    if depth > 3:
        raise ContractError("plan_contract_error", "execution", "filter tree 깊이가 허용 범위를 초과했습니다.")
    connective = str(tree.get("op") or "").lower()
    if connective in {"all", "any"}:
        clauses = tree.get("clauses")
        if not isinstance(clauses, list) or not clauses or len(clauses) > 32:
            raise ContractError("plan_contract_error", "execution", "filter clause 개수가 올바르지 않습니다.")
        masks = [_filter_mask(frame, clause, depth + 1) for clause in clauses if isinstance(clause, dict)]
        if len(masks) != len(clauses):
            raise ContractError("plan_contract_error", "execution", "filter clause 형식이 올바르지 않습니다.")
        result = masks[0]
        for mask in masks[1:]:
            result = (result & mask) if connective == "all" else (result | mask)
        return result.fillna(False)

    field = str(tree.get("field") or "")
    if not field or field not in frame.columns:
        raise ContractError(
            "source_schema_mismatch",
            "execution",
            "filter canonical field가 없습니다.",
            {"field": field},
        )
    operator = FILTER_ALIASES.get(str(tree.get("operator") or connective).lower(), str(tree.get("operator") or connective).lower())
    if operator not in FILTER_OPERATORS:
        raise ContractError("unsupported_operation", "execution", "지원하지 않는 filter operator입니다.", {"operator": operator})
    raw = frame[field]
    series = _typed_series(raw, tree.get("semantic_type"))
    value = tree.get("value")
    values = (
        tree.get("values")
        if isinstance(tree.get("values"), list)
        else value
        if isinstance(value, list)
        else []
    )

    if operator == "is_null":
        return raw.isna()
    if operator == "is_not_null":
        return raw.notna()
    if operator == "is_blank":
        return _is_blank(raw)
    if operator == "is_not_blank":
        return ~_is_blank(raw)
    if operator == "null_or_blank":
        return _is_blank(raw)
    if operator in {"in", "not_in"}:
        mask = series.isin(values)
        return ~mask if operator == "not_in" else mask
    if operator == "between":
        pair = values if len(values) == 2 else value if isinstance(value, list) and len(value) == 2 else []
        if len(pair) != 2:
            raise ContractError("plan_contract_error", "execution", "between은 두 경계값이 필요합니다.")
        return series.between(pair[0], pair[1], inclusive=str(tree.get("inclusive") or "both"))
    if operator == "contains":
        return series.astype("string").str.contains(str(value), regex=False, na=False)
    if operator == "starts_with":
        return series.astype("string").str.startswith(str(value), na=False)
    if operator == "ends_with":
        return series.astype("string").str.endswith(str(value), na=False)
    if operator == "eq":
        return series.eq(value).fillna(False)
    if operator == "ne":
        return series.ne(value).fillna(False)
    if operator == "gt":
        return series.gt(value).fillna(False)
    if operator == "gte":
        return series.ge(value).fillna(False)
    if operator == "lt":
        return series.lt(value).fillna(False)
    if operator == "lte":
        return series.le(value).fillna(False)
    raise AssertionError(operator)


def _stable_unique(values: pd.Series) -> list[Any]:
    result: list[Any] = []
    seen: set[str] = set()
    for value in values.tolist():
        if pd.isna(value):
            continue
        marker = sha256_json(json_value(value))
        if marker in seen:
            continue
        seen.add(marker)
        result.append(value)
    return result


def _aggregate(frame: pd.DataFrame, op: dict[str, Any], operation_id: str) -> pd.DataFrame:
    groups = [str(field) for field in op.get("group_by", [])]
    metrics = op.get("metrics") if isinstance(op.get("metrics"), list) else []
    if not metrics:
        raise ContractError("plan_contract_error", "execution", "aggregate metric이 없습니다.", {"operation_id": operation_id})
    required = list(groups)
    for item in metrics:
        if isinstance(item, dict) and str(item.get("function") or "") != "count":
            required.append(str(item.get("field") or ""))
    _require_columns(frame, required, operation_id)

    def calculate(part: pd.DataFrame, metric: dict[str, Any]) -> Any:
        function = str(metric.get("function") or "").lower()
        field = str(metric.get("field") or "")
        if function not in AGGREGATIONS:
            raise ContractError("unsupported_operation", "execution", "지원하지 않는 집계입니다.", {"function": function})
        if function == "count":
            return int(len(part)) if not field else int(part[field].count())
        series = part[field]
        if function == "sum":
            return pd.to_numeric(series, errors="coerce").sum(min_count=1)
        if function == "mean":
            return pd.to_numeric(series, errors="coerce").mean()
        if function == "min":
            return series.min()
        if function == "max":
            return series.max()
        if function == "nunique":
            return int(series.nunique(dropna=bool(metric.get("dropna", True))))
        if function == "median":
            return pd.to_numeric(series, errors="coerce").median()
        if function == "std":
            return pd.to_numeric(series, errors="coerce").std(ddof=int(metric.get("ddof", 1)))
        if function == "var":
            return pd.to_numeric(series, errors="coerce").var(ddof=int(metric.get("ddof", 1)))
        if function == "list_unique":
            return _stable_unique(series)
        raise AssertionError(function)

    rows: list[dict[str, Any]] = []
    if groups:
        grouped = frame.groupby(groups, dropna=False, sort=False, observed=False)
        for keys, part in grouped:
            key_values = keys if isinstance(keys, tuple) else (keys,)
            row = {field: value for field, value in zip(groups, key_values, strict=True)}
            for metric in metrics:
                row[str(metric.get("as") or metric.get("field") or metric.get("function"))] = calculate(part, metric)
            rows.append(row)
    else:
        row = {}
        for metric in metrics:
            row[str(metric.get("as") or metric.get("field") or metric.get("function"))] = calculate(frame, metric)
        rows.append(row)
    return pd.DataFrame(rows, columns=groups + [str(item.get("as") or item.get("field") or item.get("function")) for item in metrics])


def _sort_frame(frame: pd.DataFrame, keys: list[dict[str, Any]], operation_id: str) -> pd.DataFrame:
    if not keys:
        return frame.reset_index(drop=True)
    fields = [str(item.get("field") or "") for item in keys]
    _require_columns(frame, fields, operation_id)
    directions = [str(item.get("direction") or "asc").lower() != "desc" for item in keys]
    null_values = {str(item.get("nulls") or "last").lower() for item in keys}
    if len(null_values) > 1:
        current = frame.copy()
        for item in reversed(keys):
            current = current.sort_values(
                by=[str(item.get("field"))],
                ascending=str(item.get("direction") or "asc").lower() != "desc",
                na_position=str(item.get("nulls") or "last").lower(),
                kind="mergesort",
            )
        return current.reset_index(drop=True)
    return frame.sort_values(fields, ascending=directions, na_position=next(iter(null_values)), kind="mergesort").reset_index(drop=True)


def _rank_partition(part: pd.DataFrame, op: dict[str, Any], operation_id: str) -> pd.DataFrame:
    rank_by = op.get("rank_by") if isinstance(op.get("rank_by"), list) else []
    tie_break = op.get("tie_break_by") if isinstance(op.get("tie_break_by"), list) else []
    limit = int(op.get("limit") or 1)
    if limit < 1:
        raise ContractError("plan_contract_error", "execution", "rank limit은 1 이상이어야 합니다.")
    sorted_part = _sort_frame(part, rank_by + tie_break, operation_id)
    tie_policy = str(op.get("tie_policy") or "exact_n")
    if tie_policy not in {"exact_n", "include_all"}:
        raise ContractError("plan_contract_error", "execution", "rank tie policy가 올바르지 않습니다.")
    selected = sorted_part.head(limit)
    if tie_policy == "include_all" and len(sorted_part) > limit and not selected.empty:
        rank_fields = [str(item.get("field") or "") for item in rank_by]
        boundary = selected.iloc[-1]
        mask = pd.Series(True, index=sorted_part.index)
        for field in rank_fields:
            if pd.isna(boundary[field]):
                mask &= sorted_part[field].isna()
            else:
                mask &= sorted_part[field].eq(boundary[field])
        boundary_indices = sorted_part.index[mask]
        if len(boundary_indices):
            last_position = max(sorted_part.index.get_loc(index) for index in boundary_indices)
            selected = sorted_part.iloc[: last_position + 1]
    result = selected.copy()
    rank_field = str(op.get("emit_rank_field") or "")
    if rank_field:
        rank_fields = [str(item.get("field") or "") for item in rank_by]
        tuples = [tuple(row[field] for field in rank_fields) for _, row in result.iterrows()]
        ranks: list[int] = []
        prior: Any = object()
        current_rank = 0
        for index, value in enumerate(tuples, start=1):
            if value != prior:
                current_rank = index
                prior = value
            ranks.append(current_rank)
        result[rank_field] = ranks
    return result.reset_index(drop=True)


def _rank(frame: pd.DataFrame, op: dict[str, Any], operation_id: str) -> pd.DataFrame:
    partition_by = [str(field) for field in op.get("partition_by", [])]
    rank_by = op.get("rank_by") if isinstance(op.get("rank_by"), list) else []
    _require_columns(frame, partition_by + [str(item.get("field") or "") for item in rank_by], operation_id)
    if not partition_by:
        return _rank_partition(frame, op, operation_id)
    pieces: list[pd.DataFrame] = []
    for _, part in frame.groupby(partition_by, dropna=False, sort=False, observed=False):
        pieces.append(_rank_partition(part, op, operation_id))
    return pd.concat(pieces, ignore_index=True) if pieces else frame.head(0).copy()


def _compare_fields(frame: pd.DataFrame, op: dict[str, Any], operation_id: str) -> pd.DataFrame:
    left = str(op.get("left_field") or "")
    right = str(op.get("right_field") or "")
    operator = str(op.get("operator") or "eq").lower()
    _require_columns(frame, [left, right], operation_id)
    if operator not in COMPARE_OPERATORS:
        raise ContractError("unsupported_operation", "execution", "지원하지 않는 field 비교입니다.")
    left_s = _typed_series(frame[left], op.get("semantic_type"))
    right_s = _typed_series(frame[right], op.get("semantic_type"))
    nulls = left_s.isna() | right_s.isna()
    comparisons = {
        "eq": left_s.eq(right_s),
        "ne": left_s.ne(right_s),
        "gt": left_s.gt(right_s),
        "gte": left_s.ge(right_s),
        "lt": left_s.lt(right_s),
        "lte": left_s.le(right_s),
    }
    mask = comparisons[operator]
    policy = str(op.get("null_policy") or "false")
    if policy == "error" and bool(nulls.any()):
        raise ContractError("plan_contract_error", "execution", "null field 비교가 금지되어 있습니다.")
    if policy == "true":
        mask = mask | nulls
    elif policy in {"false", "three_valued"}:
        mask = mask & ~nulls
    else:
        raise ContractError("plan_contract_error", "execution", "field 비교 null policy가 올바르지 않습니다.")
    return frame.loc[mask.fillna(False)].reset_index(drop=True)


def _join(left: pd.DataFrame, right: pd.DataFrame, op: dict[str, Any], operation_id: str) -> pd.DataFrame:
    how = str(op.get("how") or "inner").lower()
    if how not in JOIN_TYPES:
        raise ContractError("unsupported_operation", "execution", "지원하지 않는 join 방식입니다.", {"how": how})
    mappings = op.get("key_mappings") if isinstance(op.get("key_mappings"), list) else []
    left_on = [str(item.get("left") or "") for item in mappings]
    right_on = [str(item.get("right") or "") for item in mappings]
    if not left_on or len(left_on) != len(right_on):
        raise ContractError("plan_contract_error", "execution", "join key mapping이 필요합니다.")
    _require_columns(left, left_on, operation_id)
    _require_columns(right, right_on, operation_id)
    null_policy = str(op.get("null_key_policy") or "never_match")
    if null_policy == "error" and (left[left_on].isna().any(axis=None) or right[right_on].isna().any(axis=None)):
        raise ContractError("join_cardinality_violation", "execution", "null join key가 허용되지 않습니다.")
    if null_policy == "never_match":
        left = left.loc[~left[left_on].isna().any(axis=1)].copy()
        right = right.loc[~right[right_on].isna().any(axis=1)].copy()
    elif null_policy not in {"match", "error"}:
        raise ContractError("plan_contract_error", "execution", "join null policy가 올바르지 않습니다.")
    cardinality = str(op.get("cardinality") or "many_to_many")
    validate_map = {
        "one_to_zero_or_one": "one_to_one",
        "one_to_one": "one_to_one",
        "one_to_many": "one_to_many",
        "many_to_one": "many_to_one",
        "many_to_many": "many_to_many",
        "one_to_one_after_aggregate": "one_to_one",
    }
    if cardinality not in validate_map:
        raise ContractError("plan_contract_error", "execution", "join cardinality가 올바르지 않습니다.")
    try:
        if how in {"semi", "anti"}:
            right_keys = right[right_on].drop_duplicates()
            marker = left.merge(
                right_keys,
                how="left",
                left_on=left_on,
                right_on=right_on,
                indicator=True,
                sort=False,
            )["_merge"].eq("both")
            return left.loc[marker if how == "semi" else ~marker].reset_index(drop=True)
        merged = left.merge(
            right,
            how=how,
            left_on=left_on,
            right_on=right_on,
            validate=validate_map[cardinality],
            sort=False,
            suffixes=("", "__right"),
        )
    except Exception as exc:
        raise ContractError(
            "join_cardinality_violation",
            "execution",
            "join cardinality를 만족하지 못했습니다.",
            {"operation_id": operation_id, "cardinality": cardinality, "reason": str(exc)[:300]},
        ) from exc
    collision_columns = [column for column in merged.columns if str(column).endswith("__right")]
    output_fields = [str(field) for field in op.get("output_fields", [])]
    if collision_columns and not output_fields:
        raise ContractError("join_cardinality_violation", "execution", "선언되지 않은 join suffix가 생성되었습니다.")
    if output_fields:
        _require_columns(merged, output_fields, operation_id)
        merged = merged[output_fields]
    empty_policy = str(op.get("empty_side_policy") or "allow")
    if empty_policy == "error" and merged.empty:
        raise ContractError("source_coverage_incomplete", "execution", "join 결과가 비어 있습니다.")
    return merged.reset_index(drop=True)


def _formula_value(frame: pd.DataFrame, expression: dict[str, Any], depth: int = 0) -> Any:
    if depth > 6:
        raise ContractError("plan_contract_error", "execution", "formula 깊이가 허용 범위를 초과했습니다.")
    if "metric_ref" in expression:
        field = str(expression.get("metric_ref") or "")
        _require_columns(frame, [field], "formula")
        return pd.to_numeric(frame[field], errors="coerce")
    if "field_ref" in expression:
        field = str(expression.get("field_ref") or "")
        _require_columns(frame, [field], "formula")
        return frame[field].copy()
    if "literal" in expression:
        return expression.get("literal")
    op = str(expression.get("op") or "")
    args = expression.get("args") if isinstance(expression.get("args"), list) else []
    values = [_formula_value(frame, item, depth + 1) for item in args if isinstance(item, dict)]
    if len(values) != len(args):
        raise ContractError("plan_contract_error", "execution", "formula argument 형식이 올바르지 않습니다.")
    if op == "add" and len(values) == 2:
        return values[0] + values[1]
    if op == "subtract" and len(values) == 2:
        return values[0] - values[1]
    if op == "multiply" and len(values) == 2:
        return values[0] * values[1]
    if op in {"coalesce", "coalesce_blank"} and len(values) == 2:
        primary, fallback = values
        if isinstance(primary, pd.Series):
            missing = primary.isna()
            if op == "coalesce_blank":
                missing = missing | primary.astype("string").str.strip().eq("").fillna(True)
            return primary.mask(missing, fallback)
        missing = primary is None or (isinstance(primary, float) and math.isnan(primary))
        if op == "coalesce_blank" and isinstance(primary, str):
            missing = missing or not primary.strip()
        return fallback if missing else primary
    if op == "safe_divide" and len(values) == 2:
        denominator = values[1]
        zero = denominator.eq(0) if isinstance(denominator, pd.Series) else denominator == 0
        policy = str(expression.get("zero_division") or "null")
        if policy == "error" and (bool(zero.any()) if isinstance(zero, pd.Series) else bool(zero)):
            raise ContractError("plan_contract_error", "execution", "0으로 나눌 수 없습니다.")
        if isinstance(denominator, pd.Series):
            safe = denominator.mask(zero)
            result = values[0] / safe
            return result.fillna(0) if policy == "zero" else result
        if zero:
            return 0 if policy == "zero" else math.nan
        return values[0] / denominator
    if op == "datetime_diff_hours" and len(values) == 2:
        try:
            left = pd.to_datetime(values[0], errors="coerce", utc=True)
            right = pd.to_datetime(values[1], errors="coerce", utc=True)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ContractError(
                "plan_contract_error",
                "execution",
                "datetime_diff_hours 입력을 datetime으로 변환할 수 없습니다.",
            ) from exc
        if not isinstance(values[0], pd.Series) and values[0] is not None and pd.isna(left):
            raise ContractError("plan_contract_error", "execution", "datetime_diff_hours 기준 시각이 올바르지 않습니다.")
        if not isinstance(values[1], pd.Series) and values[1] is not None and pd.isna(right):
            raise ContractError("plan_contract_error", "execution", "datetime_diff_hours 대상 시각이 올바르지 않습니다.")
        delta = left - right
        if isinstance(delta, pd.Series):
            return delta.dt.total_seconds() / 3600.0
        if isinstance(delta, pd.TimedeltaIndex):
            index = values[0].index if isinstance(values[0], pd.Series) else values[1].index if isinstance(values[1], pd.Series) else None
            return pd.Series(delta.total_seconds() / 3600.0, index=index)
        return delta.total_seconds() / 3600.0
    if op == "abs" and len(values) == 1:
        return values[0].abs() if isinstance(values[0], pd.Series) else abs(values[0])
    if op == "round" and len(values) == 1:
        return values[0].round(int(expression.get("digits") or 0))
    if op == "min_pair" and len(values) == 2:
        return pd.concat([pd.Series(values[0]), pd.Series(values[1])], axis=1).min(axis=1)
    if op == "max_pair" and len(values) == 2:
        return pd.concat([pd.Series(values[0]), pd.Series(values[1])], axis=1).max(axis=1)
    raise ContractError("unsupported_operation", "execution", "지원하지 않는 formula 연산입니다.", {"operator": op})


@dataclass(slots=True)
class ExecutionResult:
    rows: list[dict[str, Any]]
    columns: list[str]
    row_count: int
    operation_trace: list[dict[str, Any]]
    result_sha256: str

    def as_contract(self, plan: dict[str, Any]) -> dict[str, Any]:
        return {
            "contract_version": "analysis.result.v1",
            "status": "empty" if self.row_count == 0 else "ok",
            "plan_id": plan.get("plan_id", ""),
            "columns": self.columns,
            "rows": self.rows,
            "row_count": self.row_count,
            "lineage": plan.get("lineage", {}),
            "operation_trace": self.operation_trace,
            "result_sha256": self.result_sha256,
        }


class TypedExecutor:
    """Execute a closed operation DAG over canonical pandas frames."""

    def __init__(self, max_rows: int = 100_000, max_operations: int = 64):
        self.max_rows = int(max_rows)
        self.max_operations = int(max_operations)

    def execute(self, plan: dict[str, Any], frames: dict[str, Any]) -> ExecutionResult:
        validate_plan_integrity(plan)
        operations = plan.get("operations") if isinstance(plan.get("operations"), list) else []
        if not operations or len(operations) > self.max_operations:
            raise ContractError("plan_contract_error", "execution", "operation DAG 크기가 올바르지 않습니다.")
        values: dict[str, pd.DataFrame] = {
            (str(key) if str(key).startswith("source:") else f"source:{key}"): _frame(value)
            for key, value in frames.items()
        }
        trace: list[dict[str, Any]] = []
        last_id = ""
        for operation in operations:
            if not isinstance(operation, dict):
                raise ContractError("plan_contract_error", "execution", "operation 형식이 올바르지 않습니다.")
            operation_id = str(operation.get("id") or "")
            operator = str(operation.get("op") or "")
            if not operation_id or operation_id in values:
                raise ContractError("plan_contract_error", "execution", "operation ID가 없거나 중복되었습니다.")
            input_id = str(operation.get("input") or last_id)
            input_frame = values.get(input_id)
            input_hashes: list[str] = []
            if input_frame is not None:
                input_hashes.append(sha256_json(input_frame.to_dict(orient="records")))

            if operator == "filter":
                current = self._one(values, input_id, operation_id)
                output = current.loc[_filter_mask(current, operation.get("where") or {})].reset_index(drop=True)
            elif operator == "ordered_range":
                current = self._one(values, input_id, operation_id)
                field = str(operation.get("field") or "OPER_SEQ")
                _require_columns(current, [field], operation_id)
                numeric = pd.to_numeric(current[field], errors="coerce")
                start, end = operation.get("start"), operation.get("end")
                output = current.loc[numeric.between(start, end, inclusive="both")].reset_index(drop=True)
            elif operator == "project" or operator == "detail":
                current = self._one(values, input_id, operation_id)
                fields = [str(field) for field in operation.get("fields", [])]
                _require_columns(current, fields, operation_id)
                output = current[fields].copy()
            elif operator == "aggregate":
                output = _aggregate(self._one(values, input_id, operation_id), operation, operation_id)
            elif operator == "sort":
                output = _sort_frame(self._one(values, input_id, operation_id), operation.get("keys") or [], operation_id)
            elif operator == "rank":
                output = _rank(self._one(values, input_id, operation_id), operation, operation_id)
            elif operator == "compare_fields":
                output = _compare_fields(self._one(values, input_id, operation_id), operation, operation_id)
            elif operator == "compare_group_attributes":
                current = self._one(values, input_id, operation_id)
                groups = [str(field) for field in operation.get("group_by", [])]
                fields = [str(field) for field in operation.get("comparison_fields", [])]
                _require_columns(current, groups + fields, operation_id)
                counts = current.groupby(groups, dropna=False, sort=False)[fields].nunique(dropna=False)
                rule = str(operation.get("comparison_rule") or "any")
                mask = counts.gt(1).any(axis=1) if rule == "any" else counts.gt(1).all(axis=1)
                keys = counts.loc[mask].reset_index()[groups]
                output = current.merge(keys, how="inner", on=groups, validate="many_to_one").reset_index(drop=True)
            elif operator == "find_duplicate_groups":
                current = self._one(values, input_id, operation_id)
                fields = [str(field) for field in operation.get("fields", [])]
                _require_columns(current, fields, operation_id)
                counts = current.groupby(fields, dropna=False, sort=False).size().reset_index(name=str(operation.get("count_field") or "DUPLICATE_COUNT"))
                output = counts.loc[counts.iloc[:, -1].ge(int(operation.get("minimum_count") or 2))].reset_index(drop=True)
            elif operator == "join":
                left_id = str(operation.get("left") or input_id)
                right_id = str(operation.get("right") or "")
                left = self._one(values, left_id, operation_id)
                right = self._one(values, right_id, operation_id)
                input_hashes = [sha256_json(left.to_dict(orient="records")), sha256_json(right.to_dict(orient="records"))]
                output = _join(left, right, operation, operation_id)
            elif operator == "presence_filter":
                left = self._one(values, str(operation.get("left") or ""), operation_id)
                right = self._one(values, str(operation.get("right") or ""), operation_id)
                left_metric = str(operation.get("left_metric") or "")
                right_metric = str(operation.get("right_metric") or "")
                keys = [str(field) for field in operation.get("keys", [])]
                _require_columns(left, keys + [left_metric], operation_id)
                _require_columns(right, keys + [right_metric], operation_id)
                left_positive = left.loc[pd.to_numeric(left[left_metric], errors="coerce").fillna(0).gt(0)]
                right_positive = right.loc[pd.to_numeric(right[right_metric], errors="coerce").fillna(0).gt(0), keys].drop_duplicates()
                marker = left_positive.merge(right_positive.assign(__present=True), on=keys, how="left", validate="many_to_one")
                output = marker.loc[marker["__present"].isna()].drop(columns="__present").reset_index(drop=True)
                if bool(operation.get("materialize_right_zero", True)):
                    output[right_metric] = 0
            elif operator == "derive":
                current = self._one(values, input_id, operation_id).copy()
                output_field = str(operation.get("output_field") or "")
                formula = operation.get("formula") if isinstance(operation.get("formula"), dict) else {}
                current[output_field] = _formula_value(current, formula.get("expression") or formula)
                rounding = formula.get("rounding") if isinstance(formula.get("rounding"), dict) else {}
                if rounding:
                    current[output_field] = pd.to_numeric(current[output_field], errors="coerce").round(int(rounding.get("digits") or 0))
                output = current
            elif operator == "dedupe":
                current = self._one(values, input_id, operation_id)
                fields = [str(field) for field in operation.get("fields", [])]
                _require_columns(current, fields, operation_id)
                output = current.drop_duplicates(subset=fields, keep=str(operation.get("keep") or "first")).reset_index(drop=True)
            elif operator == "row_match_groups":
                current = self._one(values, input_id, operation_id)
                groups = operation.get("groups") if isinstance(operation.get("groups"), list) else []
                masks = []
                for group in groups:
                    if not isinstance(group, dict):
                        continue
                    masks.append(_filter_mask(current, {"op": "all", "clauses": group.get("clauses") or []}))
                output = current.loc[pd.concat(masks, axis=1).any(axis=1) if masks else pd.Series(False, index=current.index)].reset_index(drop=True)
            elif operator == "concat_segments":
                segments = operation.get("segments") if isinstance(operation.get("segments"), list) else []
                pieces = []
                for segment in segments:
                    source = self._one(values, str(segment.get("input") or ""), operation_id).copy()
                    source[str(operation.get("label_field") or "RESULT_GROUP")] = str(segment.get("label") or "")
                    pieces.append(source)
                output = pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame()
            elif operator in {"transform_previous_result", "enrich_previous_result"}:
                if operator == "transform_previous_result":
                    output = self._one(values, input_id, operation_id).copy()
                else:
                    left = self._one(values, str(operation.get("left") or input_id), operation_id)
                    right = self._one(values, str(operation.get("right") or ""), operation_id)
                    output = _join(left, right, {**operation, "op": "join", "how": "left"}, operation_id)
            elif operator == "explain_previous":
                output = self._one(values, input_id, operation_id).copy()
            elif operator == "registered_call":
                current = self._one(values, input_id, operation_id)
                required_fields = [str(field) for field in operation.get("required_fields") or []]
                _require_columns(current, required_fields, operation_id)
                records = current.to_dict(orient="records")
                for row in records:
                    for field in required_fields:
                        try:
                            if bool(pd.isna(row[field])):
                                row[field] = None
                        except (TypeError, ValueError):
                            pass
                selected_indices = dispatch_registered_call(
                    operation,
                    records,
                )
                output = current.iloc[selected_indices].reset_index(drop=True)
            else:
                raise ContractError("unsupported_operation", "execution", "지원하지 않는 typed operation입니다.", {"operator": operator})

            if len(output) > self.max_rows:
                raise ContractError("execution_memory_limit_exceeded", "execution", "실행 결과 행 수가 허용 범위를 초과했습니다.")
            values[operation_id] = output
            output_hash = sha256_json(output.to_dict(orient="records"))
            trace.append(
                {
                    "operation_id": operation_id,
                    "operator_id": f"{operator}.v1",
                    "input_contract_sha256": sha256_json(input_hashes),
                    "output_contract_sha256": output_hash,
                    "row_count": int(len(output)),
                }
            )
            last_id = operation_id

        final_id = str(plan.get("result_operation_id") or last_id)
        final = self._one(values, final_id, final_id)
        result_contract = plan.get("result_contract") if isinstance(plan.get("result_contract"), dict) else {}
        columns = [str(field) for field in result_contract.get("columns", [])]
        if columns:
            _require_columns(final, columns, final_id)
            final = final[columns]
        else:
            columns = [str(field) for field in final.columns]
        ordering = result_contract.get("ordering") if isinstance(result_contract.get("ordering"), list) else []
        if ordering:
            final = _sort_frame(final, ordering, "result_contract")
        rows = [json_value(row) for row in final.to_dict(orient="records")]
        return ExecutionResult(rows, columns, len(rows), trace, sha256_json({"columns": columns, "rows": rows}))

    @staticmethod
    def _one(values: dict[str, pd.DataFrame], identifier: str, operation_id: str) -> pd.DataFrame:
        if identifier not in values:
            raise ContractError(
                "plan_contract_error",
                "execution",
                "operation 입력이 존재하지 않습니다.",
                {"operation_id": operation_id, "input": identifier},
            )
        return values[identifier]
