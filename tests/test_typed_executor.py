from __future__ import annotations

import pytest

from reference_runtime.canonical import ContractError
from reference_runtime.typed_executor import TypedExecutor


def execute(operations, frames, columns=None):
    result = TypedExecutor().execute(
        {
            "plan_id": "plan:test",
            "operations": operations,
            "result_operation_id": operations[-1]["id"],
            "result_contract": {"columns": columns or [], "ordering": []},
            "lineage": {},
        },
        frames,
    )
    return result.rows


def test_recursive_filter_and_projection_are_typed_and_ordered():
    rows = [
        {"A": "x", "B": 3, "C": None},
        {"A": "x", "B": 1, "C": "yes"},
        {"A": "y", "B": 4, "C": ""},
    ]
    result = execute(
        [
            {
                "id": "filtered",
                "op": "filter",
                "input": "source:s",
                "where": {
                    "op": "all",
                    "clauses": [
                        {"field": "A", "operator": "eq", "value": "x"},
                        {
                            "op": "any",
                            "clauses": [
                                {"field": "B", "operator": "gt", "value": 2, "semantic_type": "number"},
                                {"field": "C", "operator": "is_null"},
                            ],
                        },
                    ],
                },
            },
            {"id": "project", "op": "project", "input": "filtered", "fields": ["B", "A"]},
        ],
        {"s": rows},
        ["B", "A"],
    )
    assert result == [{"B": 3, "A": "x"}]


def test_in_filter_accepts_canonical_value_array() -> None:
    result = execute(
        [
            {
                "id": "filtered",
                "op": "filter",
                "input": "source:s",
                "where": {
                    "field": "OPER_NAME",
                    "operator": "in",
                    "value": ["D/A1", "D/A2"],
                    "semantic_type": "string",
                },
            }
        ],
        {
            "s": [
                {"OPER_NAME": "D/A1", "WIP": 300},
                {"OPER_NAME": "D/A2", "WIP": 0},
                {"OPER_NAME": "W/B1", "WIP": 100},
            ]
        },
    )

    assert [row["OPER_NAME"] for row in result] == ["D/A1", "D/A2"]


def test_global_and_per_group_rank_have_stable_exact_n_and_ties():
    rows = [
        {"G": "A", "ITEM": "b", "VALUE": 10},
        {"G": "A", "ITEM": "a", "VALUE": 10},
        {"G": "A", "ITEM": "c", "VALUE": 5},
        {"G": "B", "ITEM": "d", "VALUE": 7},
        {"G": "B", "ITEM": "e", "VALUE": 6},
    ]
    exact = execute(
        [
            {
                "id": "rank",
                "op": "rank",
                "input": "source:s",
                "mode": "top",
                "partition_by": [],
                "rank_by": [{"field": "VALUE", "direction": "desc", "nulls": "last"}],
                "tie_break_by": [{"field": "ITEM", "direction": "asc", "nulls": "last"}],
                "limit": 1,
                "tie_policy": "exact_n",
                "emit_rank_field": "RESULT_RANK",
            }
        ],
        {"s": rows},
    )
    assert exact == [{"G": "A", "ITEM": "a", "VALUE": 10, "RESULT_RANK": 1}]

    ties = execute(
        [
            {
                "id": "rank",
                "op": "rank",
                "input": "source:s",
                "mode": "top",
                "partition_by": [],
                "rank_by": [{"field": "VALUE", "direction": "desc", "nulls": "last"}],
                "tie_break_by": [{"field": "ITEM", "direction": "asc", "nulls": "last"}],
                "limit": 1,
                "tie_policy": "include_all",
                "emit_rank_field": "RESULT_RANK",
            }
        ],
        {"s": rows},
    )
    assert [row["ITEM"] for row in ties] == ["a", "b"]
    assert [row["RESULT_RANK"] for row in ties] == [1, 1]

    grouped = execute(
        [
            {
                "id": "rank",
                "op": "rank",
                "input": "source:s",
                "mode": "top",
                "partition_by": ["G"],
                "rank_by": [{"field": "VALUE", "direction": "desc", "nulls": "last"}],
                "tie_break_by": [{"field": "ITEM", "direction": "asc", "nulls": "last"}],
                "limit": 1,
                "tie_policy": "exact_n",
                "emit_rank_field": "RESULT_RANK",
            }
        ],
        {"s": rows},
    )
    assert [(row["G"], row["ITEM"]) for row in grouped] == [("A", "a"), ("B", "d")]


def test_join_contract_and_presence_anti_join():
    left = [{"K": 1, "L": 10}, {"K": 2, "L": 20}, {"K": 3, "L": 0}]
    right = [{"K": 1, "R": 5}, {"K": 3, "R": 0}]
    joined = execute(
        [
            {
                "id": "join",
                "op": "join",
                "left": "source:l",
                "right": "source:r",
                "how": "left",
                "key_mappings": [{"left": "K", "right": "K"}],
                "cardinality": "one_to_one",
                "null_key_policy": "never_match",
                "empty_side_policy": "allow",
                "output_fields": ["K", "L", "R"],
            }
        ],
        {"l": left, "r": right},
    )
    assert [row["K"] for row in joined] == [1, 2, 3]

    presence = execute(
        [
            {
                "id": "presence",
                "op": "presence_filter",
                "left": "source:l",
                "right": "source:r",
                "keys": ["K"],
                "left_metric": "L",
                "right_metric": "R",
            }
        ],
        {"l": left, "r": right},
    )
    assert presence == [{"K": 2, "L": 20, "R": 0}]


def test_join_cardinality_violation_is_fail_closed():
    with pytest.raises(ContractError) as error:
        execute(
            [
                {
                    "id": "join",
                    "op": "join",
                    "left": "source:l",
                    "right": "source:r",
                    "how": "left",
                    "key_mappings": [{"left": "K", "right": "K"}],
                    "cardinality": "one_to_one",
                    "null_key_policy": "never_match",
                    "empty_side_policy": "allow",
                    "output_fields": ["K", "L", "R"],
                }
            ],
            {"l": [{"K": 1, "L": 1}], "r": [{"K": 1, "R": 1}, {"K": 1, "R": 2}]},
        )
    assert error.value.code == "join_cardinality_violation"


def test_compare_duplicate_formula_and_concat_segments():
    rows = [
        {"K": "x", "A": 10, "B": 5},
        {"K": "x", "A": 2, "B": 5},
        {"K": "y", "A": 8, "B": 4},
    ]
    compared = execute(
        [{"id": "c", "op": "compare_fields", "input": "source:s", "left_field": "A", "right_field": "B", "operator": "gt", "semantic_type": "number", "null_policy": "false"}],
        {"s": rows},
    )
    assert [(row["K"], row["A"]) for row in compared] == [("x", 10), ("y", 8)]

    duplicates = execute(
        [{"id": "d", "op": "find_duplicate_groups", "input": "source:s", "fields": ["K"], "minimum_count": 2, "count_field": "N"}],
        {"s": rows},
    )
    assert duplicates == [{"K": "x", "N": 2}]

    formula = execute(
        [
            {
                "id": "f",
                "op": "derive",
                "input": "source:s",
                "output_field": "RATE",
                "formula": {
                    "expression": {
                        "op": "multiply",
                        "args": [
                            {"op": "safe_divide", "args": [{"metric_ref": "A"}, {"metric_ref": "B"}], "zero_division": "null"},
                            {"literal": 100},
                        ],
                    },
                    "rounding": {"digits": 1},
                },
            }
        ],
        {"s": rows},
    )
    assert [row["RATE"] for row in formula] == [200.0, 40.0, 200.0]


def test_unregistered_operation_never_falls_back_to_code():
    with pytest.raises(ContractError) as error:
        execute([{"id": "x", "op": "run_python", "input": "source:s", "code": "..."}], {"s": []})
    assert error.value.code == "unsupported_operation"
