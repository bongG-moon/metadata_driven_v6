"""Generate v6 JSON schemas, registries, canonical cases, and case documentation.

This file is the authored source of truth for the generated artifacts owned by
this workstream. Run with ``--check`` in tests/CI and without it to refresh the
committed generated files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = Path("contracts/schemas")
SCHEMA_URI = "https://metadata-driven-v6.local/schemas/"
REFERENCE_INSTANT = "2026-07-30T09:00:00+09:00"
REFERENCE_TIMEZONE = "Asia/Seoul"
ROUTE_POLICY_VERSION = "route-policy.v1"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def nullable(schema: dict[str, Any]) -> dict[str, Any]:
    return {"anyOf": [schema, {"type": "null"}]}


def string(*, const: str | None = None, enum: Iterable[str] | None = None, pattern: str | None = None,
           min_length: int | None = None, fmt: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "string"}
    if const is not None:
        result["const"] = const
    if enum is not None:
        result["enum"] = list(enum)
    if pattern is not None:
        result["pattern"] = pattern
    if min_length is not None:
        result["minLength"] = min_length
    if fmt is not None:
        result["format"] = fmt
    return result


def integer(*, minimum: int | None = None, maximum: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "integer"}
    if minimum is not None:
        result["minimum"] = minimum
    if maximum is not None:
        result["maximum"] = maximum
    return result


def array(items: dict[str, Any], *, min_items: int | None = None, max_items: int | None = None,
          unique: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "array", "items": items}
    if min_items is not None:
        result["minItems"] = min_items
    if max_items is not None:
        result["maxItems"] = max_items
    if unique:
        result["uniqueItems"] = True
    return result


def closed_object(properties: dict[str, Any], required: Iterable[str] = (), *, title: str | None = None,
                  pattern_properties: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }
    if title:
        result["title"] = title
    if pattern_properties:
        result["patternProperties"] = pattern_properties
    return result


JSON_DEFS: dict[str, Any] = {
    "jsonValue": {
        "anyOf": [
            {"type": ["string", "number", "boolean", "null"]},
            {"type": "array", "items": {"$ref": "#/$defs/jsonValue"}, "maxItems": 2048},
            {"$ref": "#/$defs/jsonObject"},
        ]
    },
    "jsonObject": closed_object(
        {},
        pattern_properties={"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$": {"$ref": "#/$defs/jsonValue"}},
    ),
}

# Pending authoring payloads seal an already validated domain package and its
# storage projection.  Domain metadata map keys intentionally allow natural
# labels (for example ``process:PKG OUT``), so this one persistence envelope
# must use the same bounded key grammar as the domain-package contract.  Keep
# the stricter ASCII-key JSON_DEFS for runtime request/response contracts.
PERSISTED_JSON_DEFS: dict[str, Any] = {
    "jsonValue": {
        "anyOf": [
            {"type": ["string", "number", "boolean", "null"]},
            {"type": "array", "items": {"$ref": "#/$defs/jsonValue"}, "maxItems": 4096},
            {"$ref": "#/$defs/jsonObject"},
        ]
    },
    "jsonObject": closed_object(
        {},
        pattern_properties={"^.{1,256}$": {"$ref": "#/$defs/jsonValue"}},
    ),
}


def schema_document(name: str, body: dict[str, Any], *, defs: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SCHEMA_URI}{name}",
        **body,
    }
    if defs:
        result["$defs"] = defs
    return result


def envelope_schema(
    name: str,
    contract_version: str,
    properties: dict[str, Any],
    required: Iterable[str],
    *,
    defs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return schema_document(
        name,
        closed_object(
            {"contract_version": string(const=contract_version), **properties},
            ["contract_version", *required],
            title=contract_version,
        ),
        defs=defs or JSON_DEFS,
    )


SHA256 = string(pattern="^[0-9a-f]{64}$")
OPAQUE_REF = string(pattern="^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$")
STRING_LIST = array(string(min_length=1), unique=True, max_items=256)
OPERATION_SEQUENCE = array(string(pattern="^[a-z][a-z0-9_]*\\.v[0-9]+$"), max_items=256)
JSON_OBJECT_REF = {"$ref": "#/$defs/jsonObject"}
JSON_VALUE_REF = {"$ref": "#/$defs/jsonValue"}


CORE_OPERATION_NAMES = (
    "filter",
    "ordered_range",
    "product_token_match",
    "project",
    "derive",
    "aggregate",
    "compare_fields",
    "compare_group_attributes",
    "find_duplicate_groups",
    "join",
    "presence_filter",
    "sort",
    "rank",
    "concat_segments",
    "detail",
    "dedupe",
    "row_match_groups",
    "enrich_previous_result",
    "transform_previous_result",
    "explain_previous",
    "registered_call",
)

FILTER_OPERATORS = (
    "eq", "in", "ne", "not_in", "gt", "gte", "lt", "lte", "between",
    "contains", "starts_with", "ends_with", "is_null", "is_not_null",
    "is_blank", "is_not_blank", "null_or_blank",
)
AGGREGATIONS = ("sum", "mean", "min", "max", "count", "nunique", "median", "std", "var", "list_unique")
JOIN_TYPES = ("inner", "left", "right", "outer", "semi", "anti")
FORMULA_OPERATORS = (
    "add",
    "subtract",
    "multiply",
    "safe_divide",
    "abs",
    "round",
    "min_pair",
    "max_pair",
    "coalesce",
    "coalesce_blank",
    "datetime_diff_hours",
)

CORE_ERROR_CODES = (
    "request_invalid",
    "route_contract_error",
    "intent_contract_error",
    "metadata_dependency_error",
    "metadata_budget_exceeded",
    "plan_contract_error",
    "missing_required_param",
    "parameter_value_limit_exceeded",
    "ambiguous_alias",
    "ambiguous_field_binding",
    "source_missing",
    "source_retrieval_failed",
    "source_timeout",
    "source_row_limit_exceeded",
    "source_acl_denied",
    "source_schema_mismatch",
    "source_coverage_incomplete",
    "unsupported_operation",
    "execution_memory_limit_exceeded",
    "metric_rollup_violation",
    "metric_lineage_violation",
    "join_cardinality_violation",
    "result_schema_violation",
    "state_reference_expired",
    "state_reference_forbidden",
    "state_conflict",
    "state_policy_mismatch",
    "answer_claim_violation",
    "approval_not_found",
    "approval_expired",
    "approval_hash_mismatch",
    "approval_already_claimed",
    "stale_candidate",
)


def build_operator_registry() -> dict[str, Any]:
    descriptions = {
        "filter": "Bounded typed all/any predicate tree.",
        "ordered_range": "Inclusive ordered process range.",
        "product_token_match": "Metadata-declared product-token matching.",
        "project": "Exact registered field projection and order.",
        "derive": "Closed typed formula AST evaluation.",
        "aggregate": "Declared rollup over a validated grain.",
        "compare_fields": "Typed row-wise field comparison.",
        "compare_group_attributes": "Any/all comparison inside declared groups.",
        "find_duplicate_groups": "Stable duplicate-key group detection.",
        "join": "Policy-pinned binary join.",
        "presence_filter": "Positive-left and missing/zero-right anti-join.",
        "sort": "Stable multi-key ordering with null placement.",
        "rank": "Global/per-group top, bottom, argmax, or argmin.",
        "concat_segments": "Ordered labeled result segment concatenation.",
        "detail": "Registered detail/entity/history projection.",
        "dedupe": "Stable distinct by declared identity fields.",
        "row_match_groups": "AND-within-row, OR-across-row source restriction.",
        "enrich_previous_result": "Left-preserving enrichment of a prior result.",
        "transform_previous_result": "No-retrieval transform of a prior result.",
        "explain_previous": "Trace/lineage explanation without retrieval or execution.",
        "registered_call": "Hash-pinned dispatch to a statically allowlisted standalone function.",
    }
    policy_keys = {
        "filter": ["max_depth", "max_leaves", "null_policy"],
        "aggregate": ["rollup", "null_policy", "grain"],
        "rank": ["scope", "tie_policy", "null_placement", "stable_tie_break"],
        "join": ["join_type", "cardinality", "null_key", "multi_match", "empty_side", "suffix"],
        "derive": ["formula_version", "zero_division", "rounding", "max_depth", "max_nodes"],
        "compare_fields": ["type_compatibility", "null_policy"],
        "registered_call": ["function_id", "version", "implementation_sha256", "limits", "failure_policy"],
    }
    operations = [
        {
            "operator_id": f"{name}.v1",
            "op": name,
            "input_kinds": ["frame"] if name not in {"join", "presence_filter", "enrich_previous_result"} else ["left_frame", "right_frame"],
            "output_kind": "facts" if name == "explain_previous" else "frame",
            "required_policy_keys": policy_keys.get(name, ["grain", "ordering"]),
            "description": descriptions[name],
        }
        for name in CORE_OPERATION_NAMES
    ]
    body = {
        "contract_version": "operator_registry.v1",
        "operations": operations,
        "filter_operators": list(FILTER_OPERATORS),
        "filter_connectives": ["all", "any"],
        "aggregation_functions": list(AGGREGATIONS),
        "join_types": list(JOIN_TYPES),
        "formula_operators": list(FORMULA_OPERATORS),
        "limits": {"filter_max_depth": 3, "filter_max_leaves": 32, "formula_max_depth": 6, "formula_max_nodes": 32, "operation_max_count": 64},
    }
    return {**body, "registry_sha256": sha256_json(body)}


def build_error_registry() -> dict[str, Any]:
    stages = {
        "request_invalid": "request",
        "route_contract_error": "route_eligibility",
        "intent_contract_error": "intent_validation",
        "metadata_dependency_error": "metadata_resolution",
        "metadata_budget_exceeded": "metadata_resolution",
        "plan_contract_error": "plan_validation",
        "missing_required_param": "parameter_binding",
        "parameter_value_limit_exceeded": "parameter_binding",
        "ambiguous_alias": "candidate_selection",
        "ambiguous_field_binding": "source_contract",
        "source_missing": "retrieval",
        "source_retrieval_failed": "retrieval",
        "source_timeout": "retrieval",
        "source_row_limit_exceeded": "retrieval",
        "source_acl_denied": "retrieval",
        "source_schema_mismatch": "source_contract",
        "source_coverage_incomplete": "source_contract",
        "unsupported_operation": "route_eligibility",
        "execution_memory_limit_exceeded": "execution",
        "metric_rollup_violation": "plan_validation",
        "metric_lineage_violation": "result_validation",
        "join_cardinality_violation": "execution",
        "result_schema_violation": "result_validation",
        "state_reference_expired": "state_load",
        "state_reference_forbidden": "state_load",
        "state_conflict": "state_commit",
        "state_policy_mismatch": "state_store_config",
        "answer_claim_violation": "answer_validation",
        "approval_not_found": "metadata_execute",
        "approval_expired": "metadata_execute",
        "approval_hash_mismatch": "metadata_execute",
        "approval_already_claimed": "metadata_execute",
        "stale_candidate": "metadata_execute",
    }
    retryable = {"source_retrieval_failed", "source_timeout", "state_conflict"}
    errors = [
        {
            "code": code,
            "stage": stages[code],
            "retryable": code in retryable,
            "public_message": code.replace("_", " "),
        }
        for code in CORE_ERROR_CODES
    ]
    body = {"contract_version": "error_registry.v1", "errors": errors}
    return {**body, "registry_sha256": sha256_json(body)}


def build_schemas() -> dict[str, dict[str, Any]]:
    selection_ref = closed_object(
        {"candidate_id": string(min_length=1), "target_slots": STRING_LIST},
        ["candidate_id", "target_slots"],
    )
    followup = closed_object(
        {"reference": string(min_length=1), "inherit": STRING_LIST, "replace": STRING_LIST, "drop": STRING_LIST},
        ["reference", "inherit", "replace", "drop"],
    )
    intent_selection_properties = {
        "request_scope": string(enum=("new_analysis", "previous_result_transform", "previous_source_transform", "previous_source_expand", "followup_requery", "previous_result_enrich", "explain_previous")),
        "analysis_kind": string(min_length=1),
        "metric_refs": array(selection_ref, max_items=32),
        "dimension_refs": array(selection_ref, max_items=32),
        "filter_refs": array(selection_ref, max_items=32),
        "time_refs": array(selection_ref, max_items=16),
        "operation_refs": array(selection_ref, max_items=64),
        "recipe_refs": array(selection_ref, max_items=32),
        "function_refs": array(selection_ref, max_items=32),
        "formula_refs": array(selection_ref, max_items=32),
        "followup": followup,
        "unresolved": STRING_LIST,
    }
    intent_selection_required = list(intent_selection_properties)

    route_schema = envelope_schema(
        "analysis-route.schema.json",
        "analysis.route.v1",
        {
            "route": string(enum=("deterministic", "intent_llm", "unsupported")),
            "reason_code": string(enum=("unique_complete_selection", "semantic_choice_required", "unsupported_registry_gap", "ambiguous_candidate_selection", "forced_equivalence_probe")),
            "resolved_candidate_bundle_sha256": SHA256,
            "selected_candidate_ids": STRING_LIST,
            "required_slots": STRING_LIST,
            "unresolved_slots": STRING_LIST,
            "ambiguity_sets": array(array(string(min_length=1), min_items=2, unique=True), max_items=32),
            "route_policy_version": string(const=ROUTE_POLICY_VERSION),
            "eligibility_proof_sha256": SHA256,
        },
        ["route", "reason_code", "resolved_candidate_bundle_sha256", "selected_candidate_ids", "required_slots", "unresolved_slots", "ambiguity_sets", "route_policy_version", "eligibility_proof_sha256"],
    )
    route_schema["allOf"] = [
        {
            "if": {"properties": {"route": {"const": "deterministic"}}, "required": ["route"]},
            "then": {"properties": {"selected_candidate_ids": {"minItems": 1}, "unresolved_slots": {"maxItems": 0}, "ambiguity_sets": {"maxItems": 0}}},
        },
        {
            "if": {"properties": {"route": {"const": "unsupported"}}, "required": ["route"]},
            "then": {"properties": {"reason_code": {"const": "unsupported_registry_gap"}}},
        },
    ]

    operation_entry = closed_object(
        {
            "operator_id": string(pattern="^[a-z][a-z0-9_]*\\.v[0-9]+$"),
            "op": string(enum=CORE_OPERATION_NAMES),
            "input_kinds": STRING_LIST,
            "output_kind": string(enum=("frame", "facts", "scalar")),
            "required_policy_keys": STRING_LIST,
            "description": string(min_length=1),
        },
        ["operator_id", "op", "input_kinds", "output_kind", "required_policy_keys", "description"],
    )
    error_entry = closed_object(
        {"code": string(enum=CORE_ERROR_CODES), "stage": string(min_length=1), "retryable": {"type": "boolean"}, "public_message": string(min_length=1)},
        ["code", "stage", "retryable", "public_message"],
    )

    semantic_oracle = closed_object(
        {
            "request_scope": string(min_length=1),
            "analysis_kind": string(min_length=1),
            "metric_ids": STRING_LIST,
            "dimension_ids": STRING_LIST,
            "filter_ids": STRING_LIST,
            "operation_ids": OPERATION_SEQUENCE,
            "recipe_ids": STRING_LIST,
            "formula_ids": STRING_LIST,
            "followup_mode": string(min_length=1),
            "inherit": STRING_LIST,
            "replace": STRING_LIST,
            "drop": STRING_LIST,
        },
        ["request_scope", "analysis_kind", "metric_ids", "dimension_ids", "filter_ids", "operation_ids", "recipe_ids", "formula_ids", "followup_mode", "inherit", "replace", "drop"],
    )
    variant_oracle = closed_object(
        {"variant_id": string(min_length=1), "analysis_mode": string(min_length=1), "retrieval_calls": integer(minimum=0), "invariant_ids": STRING_LIST},
        ["variant_id", "analysis_mode", "retrieval_calls", "invariant_ids"],
    )
    result_oracle = closed_object(
        {
            "dataset_keys": STRING_LIST,
            "operator_sequence": OPERATION_SEQUENCE,
            "output_fields": STRING_LIST,
            "grain": string(min_length=1),
            "row_oracle": string(enum=("contract_invariants", "exact_fixture", "not_applicable")),
            "invariant_ids": STRING_LIST,
            "variant_oracles": array(variant_oracle, max_items=8),
            "error_stage": nullable(string(min_length=1)),
        },
        ["dataset_keys", "operator_sequence", "output_fields", "grain", "row_oracle", "invariant_ids", "variant_oracles", "error_stage"],
    )
    fixture_setup = closed_object(
        {
            "seed_question": nullable(string(min_length=1)),
            "plan_fault_id": nullable(string(enum=("invalid_join_input",))),
        },
        ["seed_question", "plan_fault_id"],
    )

    registered_limits = closed_object(
        {
            "timeout_ms": integer(minimum=1, maximum=5000),
            "max_input_rows": integer(minimum=1, maximum=100000),
            "max_output_rows": integer(minimum=1, maximum=100000),
            "max_output_bytes": integer(minimum=1, maximum=8388608),
        },
        ["timeout_ms", "max_input_rows", "max_output_rows", "max_output_bytes"],
    )
    registered_parameters = closed_object(
        {
            "tokens": array(
                {"type": "string", "minLength": 1, "maxLength": 256},
                min_items=1,
                max_items=64,
                unique=True,
            ),
            "operator": string(enum=("equals", "contains", "starts_with", "ends_with")),
            "match_mode": string(enum=("any", "all")),
            "case_sensitive": {"type": "boolean"},
        },
        ["tokens", "operator", "match_mode", "case_sensitive"],
    )
    registered_call_template = closed_object(
        {
            "dataset_ref": {"type": "string", "minLength": 1, "maxLength": 128},
            "field_ref": {"type": "string", "minLength": 1, "maxLength": 128},
            "parameters": registered_parameters,
            "output_fields": array(
                {"type": "string", "minLength": 1, "maxLength": 128},
                min_items=1,
                max_items=128,
                unique=True,
            ),
        },
        ["dataset_ref", "field_ref", "parameters", "output_fields"],
    )
    function_schema_defs: dict[str, Any] = {
        "schemaValue": {
            "anyOf": [
                {"type": ["string", "number", "boolean", "null"]},
                {
                    "type": "array",
                    "maxItems": 256,
                    "items": {"$ref": "#/$defs/schemaValue"},
                },
                {"$ref": "#/$defs/schemaObject"},
            ]
        },
        "schemaObject": closed_object(
            {},
            pattern_properties={"^.{1,128}$": {"$ref": "#/$defs/schemaValue"}},
        ),
        "limits": registered_limits,
        "callTemplate": registered_call_template,
    }
    registered_function_card_schema = schema_document(
        "registered-function-card.schema.json",
        closed_object(
            {
                "function_id": {"const": "core.trim_and_match_tokens"},
                "version": {"const": 1},
                "execution_mode": {"const": "registered_standalone"},
                "implementation_sha256": SHA256,
                "input_schema": {"$ref": "#/$defs/schemaObject"},
                "output_schema": {"$ref": "#/$defs/schemaObject"},
                "required_fields": array(
                    {"type": "string", "minLength": 1, "maxLength": 128},
                    min_items=1,
                    max_items=16,
                    unique=True,
                ),
                "limits": {"$ref": "#/$defs/limits"},
                "failure_policy": {"const": "fail_closed"},
                "aliases": array(
                    {"type": "string", "minLength": 1, "maxLength": 200},
                    min_items=1,
                    max_items=32,
                    unique=True,
                ),
                "call_template": {"$ref": "#/$defs/callTemplate"},
            },
            [
                "function_id",
                "version",
                "execution_mode",
                "implementation_sha256",
                "input_schema",
                "output_schema",
                "required_fields",
                "limits",
                "failure_policy",
                "aliases",
                "call_template",
            ],
            title="registered.function.card.v1",
        ),
        defs=function_schema_defs,
    )
    registered_call_schema = schema_document(
        "registered-call.schema.json",
        closed_object(
            {
                "contract_version": string(const="registered_call.v1"),
                "id": {"type": "string", "minLength": 1, "maxLength": 128},
                "op": {"const": "registered_call"},
                "input": {"type": "string", "minLength": 1, "maxLength": 256},
                "function_ref": closed_object(
                    {
                        "function_id": {"enum": [
                            "core.trim_and_match_tokens",
                            "manufacturing.match_product_tokens",
                            "manufacturing.filter_ordered_range",
                        ]},
                        "version": {"const": 1},
                        "implementation_sha256": SHA256,
                        "input_schema_sha256": SHA256,
                        "output_schema_sha256": SHA256,
                    },
                    [
                        "function_id",
                        "version",
                        "implementation_sha256",
                        "input_schema_sha256",
                        "output_schema_sha256",
                    ],
                ),
                "required_fields": array(
                    {"type": "string", "minLength": 1, "maxLength": 128},
                    min_items=1,
                    max_items=16,
                    unique=True,
                ),
                "arguments": {
                    "oneOf": [
                        closed_object(
                            {
                                "field_ref": {"type": "string", "minLength": 1, "maxLength": 128},
                                **registered_parameters["properties"],
                            },
                            ["field_ref", "tokens", "operator", "match_mode", "case_sensitive"],
                        ),
                        closed_object(
                            {
                                "rules": array(
                                    closed_object(
                                        {
                                            "field_ref": {"type": "string", "minLength": 1, "maxLength": 128},
                                            "operator": string(enum=("equals", "starts_with", "contains", "ends_with")),
                                            "value": {"type": "string", "minLength": 1, "maxLength": 256},
                                        },
                                        ["field_ref", "operator", "value"],
                                    ),
                                    min_items=1,
                                    max_items=32,
                                ),
                                "match_mode": {"const": "all"},
                                "case_sensitive": {"type": "boolean"},
                            },
                            ["rules", "match_mode", "case_sensitive"],
                        ),
                        closed_object(
                            {
                                "field_ref": {"type": "string", "minLength": 1, "maxLength": 128},
                                "start": {"type": "string", "minLength": 1, "maxLength": 128},
                                "end": {"type": "string", "minLength": 1, "maxLength": 128},
                                "ordering_items": array(
                                    closed_object(
                                        {
                                            "label": {"type": "string", "minLength": 1, "maxLength": 128},
                                            "aliases": array({"type": "string", "minLength": 1, "maxLength": 128}, max_items=32),
                                            "sequence": {"type": "number"},
                                        },
                                        ["label", "aliases", "sequence"],
                                    ),
                                    min_items=1,
                                    max_items=512,
                                ),
                            },
                            ["field_ref", "start", "end", "ordering_items"],
                        ),
                    ]
                },
                "limits": registered_limits,
                "failure_policy": {"const": "fail_closed"},
            },
            [
                "contract_version",
                "id",
                "op",
                "input",
                "function_ref",
                "required_fields",
                "arguments",
                "limits",
                "failure_policy",
            ],
            title="registered_call.v1",
        ),
    )

    schemas: dict[str, dict[str, Any]] = {
        "registered-function-card.schema.json": registered_function_card_schema,
        "registered-call.schema.json": registered_call_schema,
        "analysis-route.schema.json": route_schema,
        "semantic-intent-selection.schema.json": schema_document(
            "semantic-intent-selection.schema.json",
            closed_object(intent_selection_properties, intent_selection_required, title="analysis.intent.selection.v1"),
            defs=JSON_DEFS,
        ),
        "semantic-intent.schema.json": envelope_schema(
            "semantic-intent.schema.json",
            "analysis.intent.v1",
            {
                "request_id": OPAQUE_REF,
                "candidate_bundle_sha256": SHA256,
                "intent_candidate_id": string(min_length=1),
                "semantics": JSON_OBJECT_REF,
                "intent_sha256": SHA256,
                # Retained as optional documentation properties for consumers of
                # the selection schema.  Runtime intent payloads carry the route
                # once, in trace telemetry, and do not duplicate these fields.
                "route": string(enum=("deterministic", "intent_llm")),
                "intent_generator": string(enum=("deterministic", "llm")),
            },
            ["request_id", "candidate_bundle_sha256", "intent_candidate_id", "semantics", "intent_sha256"],
        ),
        "operator-registry.schema.json": schema_document(
            "operator-registry.schema.json",
            closed_object(
                {
                    "contract_version": string(const="operator_registry.v1"),
                    "registry_sha256": SHA256,
                    "operations": array(operation_entry, min_items=len(CORE_OPERATION_NAMES), unique=True),
                    "filter_operators": array(string(enum=FILTER_OPERATORS), min_items=len(FILTER_OPERATORS), unique=True),
                    "filter_connectives": array(string(enum=("all", "any")), min_items=2, unique=True),
                    "aggregation_functions": array(string(enum=AGGREGATIONS), min_items=len(AGGREGATIONS), unique=True),
                    "join_types": array(string(enum=JOIN_TYPES), min_items=len(JOIN_TYPES), unique=True),
                    "formula_operators": array(string(enum=FORMULA_OPERATORS), min_items=len(FORMULA_OPERATORS), unique=True),
                    "limits": closed_object(
                        {"filter_max_depth": integer(minimum=1), "filter_max_leaves": integer(minimum=1), "formula_max_depth": integer(minimum=1), "formula_max_nodes": integer(minimum=1), "operation_max_count": integer(minimum=1)},
                        ["filter_max_depth", "filter_max_leaves", "formula_max_depth", "formula_max_nodes", "operation_max_count"],
                    ),
                },
                ["contract_version", "registry_sha256", "operations", "filter_operators", "filter_connectives", "aggregation_functions", "join_types", "formula_operators", "limits"],
                title="operator_registry.v1",
            ),
            defs=JSON_DEFS,
        ),
        "error-registry.schema.json": schema_document(
            "error-registry.schema.json",
            closed_object(
                {"contract_version": string(const="error_registry.v1"), "registry_sha256": SHA256, "errors": array(error_entry, min_items=len(CORE_ERROR_CODES), unique=True)},
                ["contract_version", "registry_sha256", "errors"],
                title="error_registry.v1",
            ),
            defs=JSON_DEFS,
        ),
        "validation-case.schema.json": schema_document(
            "validation-case.schema.json",
            closed_object(
                {
                    "contract_version": string(const="validation.case.v1"),
                    "case_id": string(pattern="^[A-Z][A-Z0-9-]{1,31}$"),
                    "suite": string(enum=("single", "date", "multiturn", "operator", "branch")),
                    "scenario_id": nullable(string(min_length=1)),
                    "turn_index": nullable(integer(minimum=1)),
                    "question": string(min_length=1),
                    "capability": string(min_length=1),
                    "reference_instant": string(const=REFERENCE_INSTANT),
                    "timezone": string(const=REFERENCE_TIMEZONE),
                    "expected_route": string(enum=("deterministic", "intent_llm", "unsupported")),
                    "route_reason": string(min_length=1),
                    "expected_intent_llm_calls": integer(minimum=0, maximum=1),
                    "expected_intent_retry_calls": integer(minimum=0, maximum=1),
                    "expected_answer_llm_calls": integer(minimum=0, maximum=1),
                    "fallback_allowed": {"const": False},
                    "expected_retrieval_calls": nullable(integer(minimum=0)),
                    "expected_status": string(enum=("ok", "empty", "error", "needs_clarification")),
                    "expected_error_code": nullable(string(enum=CORE_ERROR_CODES)),
                    "expected_semantic_contract": semantic_oracle,
                    "expected_result_contract": result_oracle,
                    "fixture_setup": fixture_setup,
                    "equivalence_group_id": nullable(string(min_length=1)),
                    "tags": STRING_LIST,
                },
                ["contract_version", "case_id", "suite", "scenario_id", "turn_index", "question", "capability", "reference_instant", "timezone", "expected_route", "route_reason", "expected_intent_llm_calls", "expected_intent_retry_calls", "expected_answer_llm_calls", "fallback_allowed", "expected_retrieval_calls", "expected_status", "expected_error_code", "expected_semantic_contract", "expected_result_contract", "fixture_setup", "equivalence_group_id", "tags"],
                title="validation.case.v1",
            ),
            defs=JSON_DEFS,
        ),
    }

    schemas.update(build_envelope_schemas())
    return schemas


def build_envelope_schemas() -> dict[str, dict[str, Any]]:
    """Build the remaining versioned boundary schemas with closed objects."""
    dep = closed_object({"kind": string(min_length=1), "key": string(min_length=1), "revision": integer(minimum=1), "contract_sha256": SHA256}, ["kind", "key", "revision", "contract_sha256"])
    literal = closed_object({"id": string(min_length=1), "kind": string(min_length=1), "source_span": string(min_length=1), "value": JSON_VALUE_REF, "resolver_version": string(min_length=1)}, ["id", "kind", "source_span", "value", "resolver_version"])
    metadata_ref = closed_object({"kind": string(min_length=1), "key": string(min_length=1), "revision": integer(minimum=1), "contract_sha256": SHA256}, ["kind", "key", "revision", "contract_sha256"])
    source_status = string(enum=("ok", "empty", "error"))
    boolean = {"type": "boolean"}
    response_status = string(enum=("ok", "partial", "empty", "error", "needs_clarification"))
    stage_status = closed_object(
        {
            "overall": response_status,
            "intent": string(enum=("ok", "skipped", "error", "needs_clarification")),
            "retrieval": string(enum=("ok", "empty", "error", "not_called")),
            "analysis": string(enum=("ok", "partial", "empty", "error", "needs_clarification", "not_called")),
        },
        ["overall", "intent", "retrieval", "analysis"],
    )
    usage = closed_object(
        {
            "intent_llm_calls": integer(minimum=0, maximum=2),
            "pandas_code_llm_calls": integer(minimum=0, maximum=0),
            "pandas_repair_llm_calls": integer(minimum=0, maximum=0),
            # Canonical execution is still deterministic and defaults to zero,
            # but the isolated claim-checked narrative profile may make one
            # bounded answer call without changing typed IR or result facts.
            "answer_llm_calls": integer(minimum=0, maximum=1),
        },
        ["intent_llm_calls", "pandas_code_llm_calls", "pandas_repair_llm_calls", "answer_llm_calls"],
    )
    result_ref = closed_object(
        {
            "ref_id": OPAQUE_REF,
            "role": string(enum=("analysis_result", "source_snapshot")),
            "content_sha256": SHA256,
            "expires_at": string(fmt="date-time"),
            "store": string(const="agent_v6_result_store"),
            "path": string(const="payload.rows"),
            "download_url": string(),
        },
        ["ref_id", "role", "content_sha256", "expires_at", "store", "path", "download_url"],
    )
    followup_question = closed_object(
        {"id": string(min_length=1), "text": string(min_length=1)},
        ["id", "text"],
    )
    notice = closed_object(
        {"code": string(min_length=1), "message": string(min_length=1)},
        ["code", "message"],
    )
    download = closed_object(
        {
            "ref_id": OPAQUE_REF,
            "role": string(enum=("analysis_result", "source_snapshot")),
            "label": string(min_length=1),
            "url": string(),
        },
        ["ref_id", "role", "label", "url"],
    )
    trace = closed_object(
        {
            "trace_id": OPAQUE_REF,
            "route": JSON_OBJECT_REF,
            "retrieval": array(JSON_OBJECT_REF, max_items=32),
            "usage": usage,
            "commit_order": array(string(min_length=1), max_items=32),
        },
        ["trace_id", "route", "retrieval", "usage", "commit_order"],
    )
    response_request = closed_object(
        {
            "request_id": nullable(OPAQUE_REF),
            "question": nullable(string()),
            "session_id": nullable(string()),
            "reference_instant": nullable(string(fmt="date-time")),
            "timezone": nullable(string()),
        },
        ["request_id", "question", "session_id", "reference_instant", "timezone"],
    )
    response_data = closed_object(
        {"columns": STRING_LIST, "rows": array(JSON_OBJECT_REF, max_items=50), "row_count": integer(minimum=0)},
        ["columns", "rows", "row_count"],
    )
    response_state = closed_object(
        {
            "state_version": integer(minimum=1),
            "executed_result_ref": OPAQUE_REF,
            "expires_at": string(fmt="date-time"),
        },
        ["state_version", "executed_result_ref", "expires_at"],
    )
    clarification = closed_object(
        {"question": string(min_length=1), "options": array(string(min_length=1), max_items=20)},
        ["question", "options"],
    )

    schemas = {
        "metadata-envelope.schema.json": envelope_schema("metadata-envelope.schema.json", "metadata.envelope.v1", {"record_type": string(min_length=1), "key": string(min_length=1), "revision": integer(minimum=1), "status": string(enum=("draft", "active", "deprecated")), "compiled_at": string(fmt="date-time"), "content_sha256": SHA256, "dependencies": array(dep, max_items=256), "payload": JSON_OBJECT_REF}, ["record_type", "key", "revision", "status", "compiled_at", "content_sha256", "dependencies", "payload"]),
        "pending-metadata-write.schema.json": envelope_schema(
            "pending-metadata-write.schema.json",
            "pending.metadata.write.v1",
            {
                "authoring_kind": string(enum=("domain", "dataset", "main_filter", "domain_policy")),
                "domain_id": string(pattern="^[a-z][a-z0-9_-]{1,63}$"),
                "environment": string(pattern="^[a-z][a-z0-9_-]{1,31}$"),
                "candidate_id": OPAQUE_REF,
                "candidate_sha256": SHA256,
                "status": string(const="prepared"),
                "target_revision": integer(minimum=1),
                "base_revision": nullable(integer(minimum=1)),
                "base_bundle_sha256": nullable(SHA256),
                "base_package_sha256": nullable(SHA256),
                "prepared_at": string(fmt="date-time"),
                "expires_at": string(fmt="date-time"),
                "hash_material": JSON_OBJECT_REF,
            },
            [
                "authoring_kind",
                "domain_id",
                "environment",
                "candidate_id",
                "candidate_sha256",
                "status",
                "target_revision",
                "base_revision",
                "base_bundle_sha256",
                "base_package_sha256",
                "prepared_at",
                "expires_at",
                "hash_material",
            ],
            defs=PERSISTED_JSON_DEFS,
        ),
        "approval-event.schema.json": envelope_schema("approval-event.schema.json", "approval.event.v1", {"event_id": OPAQUE_REF, "candidate_id": OPAQUE_REF, "candidate_sha256": SHA256, "decision": string(enum=("approved", "rejected")), "subject_id": string(min_length=1), "decided_at": string(fmt="date-time"), "expires_at": string(fmt="date-time"), "idempotency_key": string(min_length=1)}, ["event_id", "candidate_id", "candidate_sha256", "decision", "subject_id", "decided_at", "expires_at", "idempotency_key"]),
        "config-registry.schema.json": envelope_schema("config-registry.schema.json", "config.registry.v1", {"config_ref": OPAQUE_REF, "adapter_type": string(enum=("oracle", "h_api", "datalake", "goodocs", "dummy")), "revision": integer(minimum=1), "read_only": {"const": True}, "acl_roles": STRING_LIST, "descriptor": JSON_OBJECT_REF, "contract_sha256": SHA256}, ["config_ref", "adapter_type", "revision", "read_only", "acl_roles", "descriptor", "contract_sha256"]),
        "query-registry.schema.json": envelope_schema("query-registry.schema.json", "query.registry.v1", {"query_ref": OPAQUE_REF, "adapter_type": string(enum=("oracle", "h_api", "datalake", "goodocs", "dummy")), "revision": integer(minimum=1), "action": string(enum=("read", "list", "get")), "parameter_schema": JSON_OBJECT_REF, "timeout_seconds": integer(minimum=1), "max_rows": integer(minimum=1), "contract_sha256": SHA256}, ["query_ref", "adapter_type", "revision", "action", "parameter_schema", "timeout_seconds", "max_rows", "contract_sha256"]),
        "request-capsule.schema.json": envelope_schema("request-capsule.schema.json", "request.capsule.v1", {"request_id": OPAQUE_REF, "question": string(min_length=1), "owner_subject_id": string(min_length=1), "session_id": string(min_length=1), "reference_instant": string(fmt="date-time"), "timezone": string(min_length=1), "literal_candidates": array(literal, max_items=64), "state_ref": nullable(OPAQUE_REF)}, ["request_id", "question", "owner_subject_id", "session_id", "reference_instant", "timezone", "literal_candidates", "state_ref"]),
        "metadata-bundle.schema.json": envelope_schema("metadata-bundle.schema.json", "metadata.bundle.v1", {"bundle_sha256": SHA256, "records": array(metadata_ref, min_items=1, max_items=512), "operator_registry_sha256": SHA256, "compiler_compatibility": string(min_length=1)}, ["bundle_sha256", "records", "operator_registry_sha256", "compiler_compatibility"]),
        "resolved-candidate-bundle.schema.json": envelope_schema(
            "resolved-candidate-bundle.schema.json",
            "resolved.candidate.bundle.v1",
            {
                "request_id": OPAQUE_REF,
                "catalog_sha256": SHA256,
                "dataset_candidates": array(JSON_OBJECT_REF, max_items=64),
                "field_candidates": array(JSON_OBJECT_REF, max_items=64),
                "metric_candidates": array(JSON_OBJECT_REF, max_items=64),
                "entity_group_candidates": array(JSON_OBJECT_REF, max_items=64),
                "grain_candidates": array(JSON_OBJECT_REF, max_items=64),
                "relation_candidates": array(JSON_OBJECT_REF, max_items=64),
                "recipe_candidates": array(JSON_OBJECT_REF, max_items=64),
                "function_candidates": array(JSON_OBJECT_REF, max_items=64),
                "intent_candidates": array(JSON_OBJECT_REF, max_items=32),
                "prompt_cards": array(JSON_OBJECT_REF, max_items=32),
                "bundle_sha256": SHA256,
                "route_decision": JSON_OBJECT_REF,
                "route_evidence": JSON_OBJECT_REF,
            },
            [
                "request_id",
                "dataset_candidates",
                "field_candidates",
                "metric_candidates",
                "entity_group_candidates",
                "grain_candidates",
                "relation_candidates",
                "recipe_candidates",
                "function_candidates",
                "intent_candidates",
                "prompt_cards",
                "bundle_sha256",
                "route_decision",
                "route_evidence",
            ],
        ),
        "analysis-plan.schema.json": envelope_schema(
            "analysis-plan.schema.json",
            "analysis.plan.v1",
            {
                "intent_sha256": SHA256,
                "candidate_bundle_sha256": SHA256,
                "catalog_sha256": SHA256,
                "retrieval_jobs": array(JSON_OBJECT_REF, max_items=32),
                "operations": array(JSON_OBJECT_REF, min_items=1, max_items=64),
                "result_operation_id": string(min_length=1),
                "result_contract": JSON_OBJECT_REF,
                "lineage": JSON_OBJECT_REF,
                "plan_id": OPAQUE_REF,
                "plan_fingerprint": SHA256,
                "input_refs": array(string(min_length=1), max_items=4, unique=True),
            },
            ["intent_sha256", "candidate_bundle_sha256", "retrieval_jobs", "operations", "result_operation_id", "result_contract", "lineage", "plan_id", "plan_fingerprint"],
        ),
        "retrieval-job-bundle.schema.json": envelope_schema("retrieval-job-bundle.schema.json", "retrieval.job_bundle.v1", {"job_bundle_id": OPAQUE_REF, "plan_id": OPAQUE_REF, "bindings": array(JSON_OBJECT_REF, max_items=32), "jobs": array(JSON_OBJECT_REF, min_items=1, max_items=64)}, ["job_bundle_id", "plan_id", "bindings", "jobs"]),
        "source-result.schema.json": envelope_schema("source-result.schema.json", "source.result.v1", {"job_id": string(min_length=1), "status": source_status, "schema": array(JSON_OBJECT_REF, max_items=256), "rows": array(JSON_OBJECT_REF, max_items=20), "source_ref": nullable(OPAQUE_REF), "row_count": integer(minimum=0), "truncated": {"type": "boolean"}, "content_sha256": nullable(SHA256), "error": nullable(JSON_OBJECT_REF)}, ["job_id", "status", "schema", "rows", "source_ref", "row_count", "truncated", "content_sha256", "error"]),
        "source-bundle.schema.json": envelope_schema("source-bundle.schema.json", "source.bundle.v1", {"bundle_id": OPAQUE_REF, "sources": array(JSON_OBJECT_REF, min_items=1, max_items=32), "canonicalized": {"const": True}, "content_sha256": SHA256}, ["bundle_id", "sources", "canonicalized", "content_sha256"]),
        "analysis-result.schema.json": envelope_schema(
            "analysis-result.schema.json",
            "analysis.result.v1",
            {
                "status": string(enum=("ok", "empty", "partial")),
                "plan_id": OPAQUE_REF,
                "columns": STRING_LIST,
                "rows": array(JSON_OBJECT_REF, max_items=100000),
                "row_count": integer(minimum=0),
                "lineage": JSON_OBJECT_REF,
                "operation_trace": array(JSON_OBJECT_REF, max_items=64),
                "result_sha256": SHA256,
            },
            ["status", "plan_id", "columns", "rows", "row_count", "lineage", "operation_trace", "result_sha256"],
        ),
        "executed-result.schema.json": envelope_schema(
            "executed-result.schema.json",
            "executed.result.v1",
            {
                "status": string(enum=("ok", "empty", "partial")),
                "plan_id": OPAQUE_REF,
                "columns": STRING_LIST,
                "rows": array(JSON_OBJECT_REF, max_items=100000),
                "row_count": integer(minimum=0),
                "lineage": JSON_OBJECT_REF,
                "operation_trace": array(JSON_OBJECT_REF, max_items=64),
                "result_sha256": SHA256,
                "grain": STRING_LIST,
                "entities": STRING_LIST,
                "criteria": JSON_OBJECT_REF,
                "source_snapshot_sha256": array(SHA256, max_items=32),
                "analysis_result_sha256": SHA256,
                "executed_result_contract_sha256": SHA256,
            },
            ["status", "plan_id", "columns", "rows", "row_count", "lineage", "operation_trace", "result_sha256", "grain", "entities", "criteria", "source_snapshot_sha256", "analysis_result_sha256", "executed_result_contract_sha256"],
        ),
        "turn-state.schema.json": envelope_schema("turn-state.schema.json", "turn.state.v1", {"state_version": integer(minimum=1), "etag": OPAQUE_REF, "owner_subject_id": string(min_length=1), "session_id": string(min_length=1), "turn_id": string(min_length=1), "parent_turn_id": nullable(string(min_length=1)), "parent_state_sha256": nullable(SHA256), "last_question": string(min_length=1), "semantic_context": JSON_OBJECT_REF, "executed_result_ref": nullable(OPAQUE_REF), "expires_at": string(fmt="date-time")}, ["state_version", "etag", "owner_subject_id", "session_id", "turn_id", "parent_turn_id", "parent_state_sha256", "last_question", "semantic_context", "executed_result_ref", "expires_at"]),
        "answer-facts.schema.json": envelope_schema(
            "answer-facts.schema.json",
            "answer.facts.v1",
            {
                "question": string(),
                "facts": array(closed_object({"fact_id": string(min_length=1), "type": string(min_length=1), "value": JSON_VALUE_REF}, ["fact_id", "type", "value"]), max_items=512),
                "result_sha256": SHA256,
                "plan_id": OPAQUE_REF,
                "facts_sha256": SHA256,
            },
            ["question", "facts", "result_sha256", "plan_id", "facts_sha256"],
        ),
        "display-options.schema.json": envelope_schema("display-options.schema.json", "display.options.v1", {"profile": string(min_length=1), "include_diagnostics": boolean, "show_result_table": boolean, "table_preview_limit": integer(minimum=1, maximum=20), "show_analysis_evidence": boolean, "show_download_links": boolean, "show_notices": boolean, "show_applied_criteria": boolean, "show_next_questions": boolean, "show_intent_analysis": boolean, "show_data_retrieval": boolean, "show_pandas_code": boolean, "show_execution_plan": boolean}, ["profile", "include_diagnostics", "show_result_table", "table_preview_limit", "show_analysis_evidence", "show_download_links", "show_notices", "show_applied_criteria", "show_next_questions", "show_intent_analysis", "show_data_retrieval", "show_pandas_code", "show_execution_plan"]),
        "answer-sections.schema.json": envelope_schema(
            "answer-sections.schema.json",
            "answer.sections.v1",
            {
                "summary": closed_object({"headline": string(), "fact_ids": STRING_LIST}, ["headline", "fact_ids"]),
                "result_table": closed_object({"row_source": string(const="data.rows"), "columns": STRING_LIST, "row_count": integer(minimum=0), "data_ref": string()}, ["row_source", "columns", "row_count", "data_ref"]),
                "applied_criteria": JSON_OBJECT_REF,
                "evidence": JSON_OBJECT_REF,
                "notices": array(notice, max_items=64),
                "downloads": array(download, max_items=32),
                "next_questions": array(followup_question, max_items=3),
            },
            ["summary", "result_table", "applied_criteria", "evidence", "notices", "downloads", "next_questions"],
        ),
        "download-item.schema.json": envelope_schema("download-item.schema.json", "download.item.v1", {"role": string(enum=("result", "source")), "ref": OPAQUE_REF, "url": nullable(string(min_length=1)), "format": string(const="csv"), "expires_at": string(fmt="date-time"), "row_count": integer(minimum=0), "content_sha256": SHA256, "label": string(min_length=1)}, ["role", "ref", "url", "format", "expires_at", "row_count", "content_sha256", "label"]),
        "gaia-metadata.schema.json": envelope_schema(
            "gaia-metadata.schema.json",
            "gaia.metadata.v1",
            {
                "urls": array(closed_object({"title": string(min_length=1), "url": string(min_length=1)}, ["title", "url"]), max_items=16),
                "followup_questions": array(followup_question, max_items=3),
                "trace_id": OPAQUE_REF,
                "usage": usage,
                "docs": array(JSON_OBJECT_REF, max_items=0),
                "images": array(JSON_OBJECT_REF, max_items=0),
                "knowhows": array(JSON_OBJECT_REF, max_items=0),
            },
            ["urls", "followup_questions", "trace_id", "usage", "docs", "images", "knowhows"],
        ),
        "response.schema.json": envelope_schema(
            "response.schema.json",
            "response.v1",
            {
                "response_type": string(const="data_analysis"),
                "status": response_status,
                "stage_status": stage_status,
                "message": string(),
                "data_mode": string(enum=("dummy", "inline", "live")),
                "analysis_mode": string(const="typed_ir"),
                "request": response_request,
                "intent_plan": JSON_OBJECT_REF,
                "analysis": JSON_OBJECT_REF,
                "clarification": nullable(clarification),
                "data": response_data,
                "data_refs": array(result_ref, max_items=32),
                "answer_sections": JSON_OBJECT_REF,
                "state": nullable(response_state),
                "trace": trace,
            },
            ["response_type", "status", "stage_status", "message", "data_mode", "analysis_mode", "request", "intent_plan", "analysis", "clarification", "data", "data_refs", "answer_sections", "state", "trace"],
        ),
        "trace.schema.json": envelope_schema("trace.schema.json", "trace.v1", {"trace_id": string(min_length=1), "events": array(JSON_OBJECT_REF, max_items=128), "verbose_trace_ref": nullable(OPAQUE_REF)}, ["trace_id", "events", "verbose_trace_ref"]),
        "error.schema.json": envelope_schema("error.schema.json", "error.v1", {"error_registry_version": string(const="error_registry.v1"), "error_id": OPAQUE_REF, "code": string(enum=CORE_ERROR_CODES), "stage": string(min_length=1), "message": string(min_length=1), "retryable": {"type": "boolean"}, "details": JSON_OBJECT_REF, "trace_id": string(min_length=1)}, ["error_registry_version", "error_id", "code", "stage", "message", "retryable", "details", "trace_id"]),
        "model-profile.schema.json": envelope_schema("model-profile.schema.json", "model.profile.v1", {"profile_id": string(min_length=1), "provider": string(min_length=1), "model": string(min_length=1), "temperature": {"type": "number", "const": 0}, "runs": integer(minimum=3), "intent_route_only": {"const": True}}, ["profile_id", "provider", "model", "temperature", "runs", "intent_route_only"]),
        "evidence-manifest.schema.json": envelope_schema("evidence-manifest.schema.json", "evidence.manifest.v1", {"git_sha": string(min_length=1), "dirty": {"type": "boolean"}, "generated_at": string(fmt="date-time"), "artifact_hashes": JSON_OBJECT_REF, "route_counts": JSON_OBJECT_REF, "test_summary": JSON_OBJECT_REF}, ["git_sha", "dirty", "generated_at", "artifact_hashes", "route_counts", "test_summary"]),
        "flow-inventory.schema.json": envelope_schema("flow-inventory.schema.json", "flow.inventory.v1", {"namespace_uuid": string(min_length=1), "flows": array(closed_object({"logical_key": string(min_length=1), "endpoint_name": string(min_length=1), "flow_uuid": string(min_length=1), "display_name": string(min_length=1), "trusted_core": {"const": True}}, ["logical_key", "endpoint_name", "flow_uuid", "display_name", "trusted_core"]), min_items=5, max_items=5)}, ["namespace_uuid", "flows"]),
        "unsupported-telemetry.schema.json": envelope_schema("unsupported-telemetry.schema.json", "unsupported.telemetry.v1", {"normalized_shape_id": OPAQUE_REF, "missing_capability_ids": STRING_LIST, "metadata_bundle_sha256": SHA256, "operator_registry_sha256": SHA256, "route_policy_version": string(const=ROUTE_POLICY_VERSION), "occurrence_count": integer(minimum=1), "first_seen_at": string(fmt="date-time"), "last_seen_at": string(fmt="date-time"), "case_ref": nullable(string(min_length=1))}, ["normalized_shape_id", "missing_capability_ids", "metadata_bundle_sha256", "operator_registry_sha256", "route_policy_version", "occurrence_count", "first_seen_at", "last_seen_at", "case_ref"]),
    }
    schemas["response.schema.json"]["allOf"] = [
        {
            "if": {"properties": {"status": {"const": "needs_clarification"}}, "required": ["status"]},
            "then": {"properties": {"clarification": clarification, "state": {"type": "null"}}},
            "else": {"properties": {"clarification": {"type": "null"}}},
        },
        {
            "if": {"properties": {"status": {"const": "error"}}, "required": ["status"]},
            "then": {"properties": {"state": {"type": "null"}}},
        },
    ]
    return schemas


def _operator_ids(names: Iterable[str]) -> list[str]:
    return [name if ".v" in name else f"{name}.v1" for name in names]


def make_case(
    case_id: str,
    suite: str,
    question: str,
    capability: str,
    *,
    route: str = "deterministic",
    reason: str | None = None,
    scenario_id: str | None = None,
    turn_index: int | None = None,
    scope: str = "new_analysis",
    analysis_kind: str = "aggregate",
    metrics: Iterable[str] = (),
    dimensions: Iterable[str] = (),
    filters: Iterable[str] = (),
    operations: Iterable[str] = ("filter", "aggregate"),
    recipes: Iterable[str] = (),
    formulas: Iterable[str] = (),
    followup_mode: str = "none",
    inherit: Iterable[str] = (),
    replace: Iterable[str] = (),
    drop: Iterable[str] = (),
    datasets: Iterable[str] = ("production",),
    output_fields: Iterable[str] = (),
    grain: str = "declared_by_metadata",
    invariants: Iterable[str] = (),
    retrieval_calls: int | None = 1,
    status: str = "ok",
    error_code: str | None = None,
    error_stage: str | None = None,
    variants: Iterable[dict[str, Any]] = (),
    seed_question: str | None = None,
    plan_fault_id: str | None = None,
    equivalence_group_id: str | None = None,
    tags: Iterable[str] = (),
) -> dict[str, Any]:
    if reason is None:
        reason = {
            "deterministic": "unique_complete_selection",
            "intent_llm": "semantic_choice_required",
            "unsupported": "unsupported_registry_gap",
        }[route]
    operator_ids = _operator_ids(operations)
    invariant_ids = list(dict.fromkeys(["route_exact", "no_fallback", "typed_ir_only", *invariants]))
    row_oracle = "not_applicable" if status in {"error", "needs_clarification"} else "contract_invariants"
    return {
        "contract_version": "validation.case.v1",
        "case_id": case_id,
        "suite": suite,
        "scenario_id": scenario_id,
        "turn_index": turn_index,
        "question": question,
        "capability": capability,
        "reference_instant": REFERENCE_INSTANT,
        "timezone": REFERENCE_TIMEZONE,
        "expected_route": route,
        "route_reason": reason,
        "expected_intent_llm_calls": 1 if route == "intent_llm" else 0,
        "expected_intent_retry_calls": 0,
        "expected_answer_llm_calls": 0,
        "fallback_allowed": False,
        "expected_retrieval_calls": retrieval_calls,
        "expected_status": status,
        "expected_error_code": error_code,
        "expected_semantic_contract": {
            "request_scope": scope,
            "analysis_kind": analysis_kind,
            "metric_ids": list(metrics),
            "dimension_ids": list(dimensions),
            "filter_ids": list(filters),
            "operation_ids": operator_ids,
            "recipe_ids": list(recipes),
            "formula_ids": list(formulas),
            "followup_mode": followup_mode,
            "inherit": list(inherit),
            "replace": list(replace),
            "drop": list(drop),
        },
        "expected_result_contract": {
            "dataset_keys": list(datasets),
            "operator_sequence": operator_ids,
            "output_fields": list(output_fields),
            "grain": grain,
            "row_oracle": row_oracle,
            "invariant_ids": invariant_ids,
            "variant_oracles": list(variants),
            "error_stage": error_stage,
        },
        "fixture_setup": {
            "seed_question": seed_question,
            "plan_fault_id": plan_fault_id,
        },
        "equivalence_group_id": equivalence_group_id,
        "tags": list(dict.fromkeys([suite, route, *tags])),
    }


def build_single_cases() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = [
        dict(id="Q01", q="오늘 투입된 제품중 MCP NO가 L-267로 시작하는 제품의 INPUT 수량 알려줘", cap="prefix filter + input sum", m=["input_qty"], d=["device"], f=["date.today", "mcp_no.starts_with:L-267"], o=["registered_call", "filter", "aggregate", "sort"], out=["device", "input_qty"], inv=["prefix_not_contains", "today_kst", "sum_by_device"]),
        dict(id="Q02", q="어제 DA공정 차수별 생산량 알려줘", cap="relative date + process aliases + generation aggregate", m=["production_qty"], d=["generation"], f=["date.yesterday", "process.da"], out=["generation", "production_qty"], inv=["yesterday_kst", "da_alias_closed_set", "sum_by_generation"]),
        dict(id="Q03", q="어제 Mobile제품의 PKG OUT실적을 제품별로 알려줘", cap="product category + package-out aggregate", m=["pkg_out_qty"], d=["device"], f=["date.yesterday", "product.mobile"], out=["device", "pkg_out_qty"], inv=["mobile_metadata_filter", "sum_by_device"]),
        dict(id="Q04", q="HBM제품의 WB공정에서 오늘 아침재공 제품별로 알려줘", cap="snapshot WIP aggregate", m=["morning_wip_qty"], d=["device"], f=["date.today", "product.hbm", "process.wb", "snapshot.morning"], ds=["wip_snapshot"], out=["device", "morning_wip_qty"], inv=["morning_snapshot", "hbm_metadata_filter"]),
        dict(id="Q05", q="6/27일 W/B공정에서 세부 공정별 생산실적과 아침재공 수량 알려줘", cap="two-source metric selection and join", route="deterministic", kind="multi_source_compare", m=["production_qty", "morning_wip_qty"], d=["operation_name"], f=["date.2026-06-27", "process.wb"], o=["filter", "aggregate", "join", "project"], ds=["production", "wip_snapshot"], out=["operation_name", "production_qty", "morning_wip_qty"], inv=["left_join_policy", "metric_specific_time_semantics"], retrieval_calls=2),
        dict(id="Q06", q="HBM제품 FCB공정에서 오늘 아침재공 제품별로 알려줘", cap="HBM FCB snapshot WIP", m=["morning_wip_qty"], d=["device"], f=["date.today", "product.hbm", "process.fcb", "snapshot.morning"], ds=["wip_snapshot"], out=["device", "morning_wip_qty"], inv=["morning_snapshot", "fcb_alias_closed_set"]),
        dict(id="Q07", q="6월 30일 FCB/H 공정 실적이 있는 Device 알려줘", cap="existence filter and projection", kind="metric_presence_detail", m=["production_qty"], d=["device"], f=["date.2026-06-30", "process.fcb_h", "production_qty.gt:0"], o=["filter", "project", "dedupe", "sort"], out=["device"], inv=["positive_production_only", "distinct_device"]),
        dict(id="Q08", q="RG 32G DDR4 FBGA 96 DDP 제품 BG공정에서 생산량과 재공수량 알려줘", cap="product token resolution + two-source join", route="deterministic", kind="multi_source_compare", m=["production_qty", "wip_qty"], d=["device"], f=["product.tokens:RG-32G-DDR4-FBGA-96-DDP", "process.bg"], o=["registered_call", "filter", "aggregate", "join", "project"], ds=["production", "wip_snapshot"], out=["device", "production_qty", "wip_qty"], inv=["all_product_tokens_match", "registered_join_only"], retrieval_calls=2),
        dict(id="Q09", q="FCB 공정에서 SP 16G DDR5 2ND X4 78 FCBGA SDP 제품의 전일 생산량 알려줘", cap="long product-token match + yesterday", m=["production_qty"], d=["device"], f=["date.yesterday", "process.fcb", "product.tokens:SP-16G-DDR5-2ND-X4-78-FCBGA-SDP"], o=["registered_call", "filter", "aggregate"], out=["device", "production_qty"], inv=["all_product_tokens_match", "yesterday_kst"]),
        dict(id="Q10", q="6/24일 투입 실적 대비 D/S1, DA1공정에서 WIP 많은 제품 알려줘", cap="input versus WIP multi-source comparison", route="deterministic", kind="multi_source_compare", m=["input_qty", "wip_qty"], d=["device"], f=["date.2026-06-24", "process.ds1_or_da1"], o=["filter", "aggregate", "join", "sort"], ds=["input", "wip_snapshot"], out=["device", "input_qty", "wip_qty"], inv=["metric_source_dates", "sort_wip_desc"], retrieval_calls=2),
        dict(id="Q11", q="오늘 현시간 기준 INPUT실적은 있으나 D/A공정 WIP 없는 제품 확인해줘", cap="positive-left missing-or-zero-right presence anti-join", route="deterministic", kind="presence_compare", m=["input_qty", "wip_qty"], d=["device"], f=["date.today", "process.da"], o=["filter", "aggregate", "presence_filter", "project"], ds=["input", "wip_snapshot"], out=["device", "input_qty", "wip_qty"], inv=["positive_left", "missing_or_zero_right", "no_plain_anti_join"], retrieval_calls=2),
        dict(id="Q12", q="FCB 공정 생산 실적과 W/B2 공정 재공수량을 제품별로 비교해줘", cap="cross-process multi-source compare", route="deterministic", kind="multi_source_compare", m=["production_qty", "wip_qty"], d=["device"], f=["process.fcb:production", "process.wb2:wip"], o=["filter", "aggregate", "join", "project"], ds=["production", "wip_snapshot"], out=["device", "production_qty", "wip_qty"], inv=["metric_specific_process_filters", "registered_join_only"], retrieval_calls=2),
        dict(id="Q13", q="W/B공정 IN TAT 10시간이상 된 LOT 알려줘", cap="duration threshold detail", kind="detail", m=["in_tat_hours"], d=["lot_id"], f=["process.wb", "in_tat_hours.gte:10"], o=["filter", "detail", "sort"], ds=["lot_status"], out=["lot_id", "operation_name", "in_tat_hours"], inv=["duration_unit_hours", "gte_inclusive"]),
        dict(id="Q14", q="D/S1~D/A4 공정 Hold 된 Lot ID 알려줘", cap="ordered operation range + hold filter", kind="detail", d=["lot_id"], f=["process.range:ds1-da4", "hold.true"], o=["registered_call", "filter", "project", "dedupe", "sort"], ds=["lot_status"], out=["lot_id"], inv=["registered_process_order", "range_inclusive"]),
        dict(id="Q15", q="7월 1일 D/A1~W/B6 공정 구간의 공정별 생산량을 OPER_SEQ 순서로 알려줘", cap="ordered process range aggregate", m=["production_qty"], d=["operation_name", "oper_seq"], f=["date.2026-07-01", "process.range:da1-wb6"], o=["filter", "registered_call", "aggregate", "sort"], out=["oper_seq", "operation_name", "production_qty"], inv=["registered_process_order", "sort_oper_seq_asc"]),
        dict(id="Q16", q="DA, WB공정 HOLD LOT 알려줘", cap="process union + hold lots", kind="detail", d=["lot_id", "operation_name"], f=["process.da_or_wb", "hold.true"], o=["filter", "detail", "dedupe", "sort"], ds=["lot_status"], out=["operation_name", "lot_id"], inv=["or_across_process_aliases", "hold_only"]),
        dict(id="Q17", q="WB & DA 공정 Hold Lot LIST알려줘", cap="process intersection syntax normalized to union", kind="detail", d=["lot_id", "operation_name"], f=["process.wb_or_da", "hold.true"], o=["filter", "detail", "dedupe", "sort"], ds=["lot_status"], out=["operation_name", "lot_id"], inv=["registered_multi_process_semantics", "hold_only"]),
        dict(id="Q18", q="D/S1&D/A 공정 Hold Lot LIST알려줘", cap="mixed process aliases + hold lots", kind="detail", d=["lot_id", "operation_name"], f=["process.ds1_or_da", "hold.true"], o=["filter", "detail", "dedupe", "sort"], ds=["lot_status"], out=["operation_name", "lot_id"], inv=["registered_multi_process_semantics", "hold_only"]),
        dict(id="Q19", q="7월 5일 FCB1,FCB2,FCB/H 공정 실적 알려줘", cap="explicit process list aggregate", m=["production_qty"], d=["operation_name"], f=["date.2026-07-05", "process.fcb1_fcb2_fcbh"], out=["operation_name", "production_qty"], inv=["exact_process_list", "sum_by_operation"]),
        dict(id="Q20", q="7/9 D/A1, D/A2공정에서 생산 실적 알려줘", cap="date + explicit DA operations", m=["production_qty"], d=["operation_name"], f=["date.2026-07-09", "process.da1_da2"], out=["operation_name", "production_qty"], inv=["exact_process_list", "sum_by_operation"]),
        dict(id="Q21", q="오늘 WBM 공정의 제품별 생산량을 알려줘. 제품 정보가 비어 있는 행도 제외하지 말고, 비어 있는 제품 정보는 빈칸으로, 생산량이 비어 있으면 0으로 보여줘.", cap="explicit null-preservation and fill policies", m=["production_qty"], d=["device"], f=["date.today", "process.wbm"], o=["filter", "derive", "aggregate", "project"], formulas=["fill_device_blank", "fill_production_zero"], out=["device", "production_qty"], inv=["preserve_blank_device", "fill_blank_metric_zero"]),
        dict(id="Q22", q="현재 제품 중 TECH, DEN, PKG_TYPE2, MCP_NO는 같지만 MODE, PKG_TYPE1 또는 LEAD가 다른 제품들을 찾아서 보여줘.", cap="same-key differing-attribute group comparison", route="deterministic", kind="group_attribute_compare", d=["tech", "den", "pkg_type2", "mcp_no", "mode", "pkg_type1", "lead", "device"], o=["compare_group_attributes", "detail", "sort"], ds=["product_master"], out=["tech", "den", "pkg_type2", "mcp_no", "mode", "pkg_type1", "lead", "device"], inv=["same_group_keys", "any_variant_attribute_differs"]),
        dict(id="Q23", q="FCB2공정 제품별 UPH 알려줘", cap="registered UPH metric by product", kind="uph", m=["uph"], d=["device"], f=["process.fcb2"], ds=["equipment_assignment"], out=["device", "uph"], inv=["uph_formula_metadata", "declared_uph_rollup"]),
        dict(id="Q24", q="WB공정 L-217제품 차수별, 장비 기종별 UPH 알려줘", cap="prefix product + multidimensional UPH", kind="uph", m=["uph"], d=["generation", "equipment_model"], f=["process.wb", "mcp_no.starts_with:L-217"], o=["registered_call", "filter", "aggregate", "sort"], ds=["equipment_assignment"], out=["generation", "equipment_model", "uph"], inv=["prefix_not_contains", "declared_uph_rollup"]),
        dict(id="Q25", q="F315 L-116로 시작하는 제품 WB 공정 차수별 UPH 알려줘", cap="two product tokens + UPH by generation", kind="uph", m=["uph"], d=["generation"], f=["process.wb", "device.contains:F315", "mcp_no.starts_with:L-116"], o=["registered_call", "filter", "aggregate", "sort"], ds=["equipment_assignment"], out=["generation", "uph"], inv=["all_product_tokens_match", "declared_uph_rollup"]),
        dict(id="Q26", q="현재 D/A1 공정의 장비 모델, Recipe, 공정, UPH를 보여줘", cap="equipment detail projection", kind="uph_detail", m=["uph"], d=["equipment_model", "recipe", "operation_name"], f=["snapshot.current", "process.da1"], o=["filter", "project", "sort"], ds=["equipment_assignment"], out=["equipment_model", "recipe", "operation_name", "uph"], inv=["current_snapshot", "exact_projection_order"]),
        dict(id="Q27", q="현재 D/A1 공정에 배정된 장비를 장비 모델과 Recipe 조합별로 보여줘", cap="equipment assignment grouped detail", kind="equipment_grouped", m=["equipment_count"], d=["equipment_model", "recipe"], f=["snapshot.current", "process.da1"], o=["filter", "aggregate", "sort", "project"], ds=["equipment_assignment"], out=["equipment_model", "recipe", "equipment_count", "equipment_list"], inv=["current_snapshot", "equipment_count_matches_list"]),
        dict(id="Q28", q="W/B공정 현재 HOLD LOT와 HOLD사유 알려줘", cap="current hold lot detail", kind="detail", d=["lot_id", "hold_reason"], f=["snapshot.current", "process.wb", "hold.true"], o=["filter", "detail", "sort"], ds=["lot_status"], out=["lot_id", "hold_reason"], inv=["current_snapshot", "hold_only"]),
        dict(id="Q29", q="현재 HOLD 중인 LOT 목록과 LOT별 UNIT 수량, Wafer 수량, 현재·누적 TAT를 보여줘", cap="current hold detail with quantities and TAT", kind="detail", m=["unit_qty", "wafer_qty", "current_tat", "cumulative_tat"], d=["lot_id"], f=["snapshot.current", "hold.true"], o=["filter", "detail", "sort"], ds=["lot_status"], out=["lot_id", "unit_qty", "wafer_qty", "current_tat", "cumulative_tat"], inv=["current_snapshot", "lot_grain_no_rollup"]),
        dict(id="Q30", q="오늘 DA공정에서 생산량 상위 3개 제품과 각 제품에 할당된 장비 대수 및 LIST를 알려줘", cap="rank then equipment enrichment", route="deterministic", kind="rank_then_enrich", m=["production_qty", "equipment_count"], d=["device"], f=["date.today", "process.da", "snapshot.current:equipment"], o=["filter", "aggregate", "rank", "join", "project"], ds=["production", "equipment_assignment"], out=["device", "production_qty", "equipment_count", "equipment_list"], inv=["rank_before_join", "top_n_exact:3", "equipment_count_matches_list"], retrieval_calls=2),
    ]
    return [
        make_case(
            spec.pop("id"), "single", spec.pop("q"), spec.pop("cap"),
            route=spec.pop("route", "deterministic"), analysis_kind=spec.pop("kind", "aggregate"),
            metrics=spec.pop("m", ()), dimensions=spec.pop("d", ()), filters=spec.pop("f", ()),
            operations=spec.pop("o", ("filter", "aggregate")), formulas=spec.pop("formulas", ()),
            datasets=spec.pop("ds", ("production",)), output_fields=spec.pop("out", ()),
            invariants=spec.pop("inv", ()), **spec,
        )
        for spec in specs
    ]


def build_date_cases() -> list[dict[str, Any]]:
    specs = [
        ("D01", "2026-07-01 제품별 INPUT 계획과 OUT 계획을 OUT 계획이 큰 순서로 알려줘", "two plan metrics and sort", "deterministic", ["input_plan_qty", "out_plan_qty"], ["filter", "aggregate", "sort"], ["device", "input_plan_qty", "out_plan_qty"], ["iso_date", "sort_out_plan_desc"]),
        ("D02", "2026/7/1 제품별 OUT 계획을 알려줘", "slash date normalization", "deterministic", ["out_plan_qty"], ["filter", "aggregate", "sort"], ["device", "out_plan_qty"], ["slash_date_to_local_day"]),
        ("D03", "2026년 7월 1일 제품별 INPUT 계획을 알려줘", "Korean date normalization", "deterministic", ["input_plan_qty"], ["filter", "aggregate", "sort"], ["device", "input_plan_qty"], ["korean_date_to_local_day"]),
        ("D04", "2026-07-01 W/BM 공정 생산량을 알려줘", "explicit date and process production", "deterministic", ["production_qty"], ["filter", "aggregate"], ["operation_name", "production_qty"], ["iso_date", "wbm_exact_alias"]),
        ("D05", "2026/7/1 제품별 INPUT 계획 대비 실제 INPUT 실적과 달성률을 알려줘", "plan versus actual join and derived achievement", "deterministic", ["input_plan_qty", "input_qty", "achievement_rate"], ["filter", "aggregate", "join", "derive", "project"], ["device", "input_plan_qty", "input_qty", "achievement_rate"], ["safe_divide", "registered_plan_actual_join"]),
        ("D06", "2026-07-01T00:00:00+09:00 기준 제품별 OUT 계획을 알려줘", "timezone-aware instant normalization", "deterministic", ["out_plan_qty"], ["filter", "aggregate", "sort"], ["device", "out_plan_qty"], ["explicit_offset_preserved"]),
    ]
    return [
        make_case(case_id, "date", question, capability, route=route, analysis_kind="date_metric_analysis",
                  metrics=metrics, dimensions=["operation_name"] if case_id == "D04" else ["device"], filters=["date.2026-07-01"], operations=ops,
                  datasets=(["plan", "input"] if case_id == "D05" else ["plan"] if case_id != "D04" else ["production"]),
                  retrieval_calls=2 if case_id == "D05" else 1,
                  formulas=["achievement_rate"] if case_id == "D05" else (), output_fields=fields,
                  invariants=["reference_timezone_asia_seoul", *invariants])
        for case_id, question, capability, route, metrics, ops, fields, invariants in specs
    ]


def build_multiturn_cases() -> list[dict[str, Any]]:
    cases = [
        make_case("MT01-01", "multiturn", "오늘 DA공정에서 생산량 상위 3개 제품을 알려줘.", "seed ranked product result",
                  scenario_id="MT01", turn_index=1, analysis_kind="rank", metrics=["production_qty"], dimensions=["device"],
                  filters=["date.today", "process.da"], operations=["filter", "aggregate", "rank"],
                  output_fields=["device", "production_qty"], invariants=["top_n_exact:3", "stable_rank"]),
        make_case("MT01-02", "multiturn", "이 제품들에 할당된 현재 장비 대수와 장비 LIST를 제품별로 알려줘.", "previous-result keyed equipment enrichment",
                  route="deterministic", scenario_id="MT01", turn_index=2, scope="previous_result_enrich", analysis_kind="enrich_previous_result",
                  metrics=["equipment_count"], dimensions=["device"], filters=["snapshot.current"],
                  operations=["transform_previous_result", "aggregate", "enrich_previous_result", "project"], followup_mode="referenced_result",
                  inherit=["device_identity", "result_order"], replace=["metrics"], datasets=["equipment_assignment"],
                  output_fields=["device", "production_qty", "equipment_count", "equipment_list"],
                  invariants=["prior_rows_left_preserved", "equipment_count_matches_list"]),
        make_case("MT01-03", "multiturn", "그중 장비 대수가 가장 많은 제품만 보여줘.", "no-retrieval transform of enriched result",
                  scenario_id="MT01", turn_index=3, scope="previous_result_transform", analysis_kind="argmax_previous_result",
                  metrics=["equipment_count"], dimensions=["device"], operations=["transform_previous_result", "rank", "project"],
                  followup_mode="referenced_result", inherit=["all_prior_columns", "result_ref"], replace=["rank"],
                  datasets=[], retrieval_calls=0, output_fields=["device", "production_qty", "equipment_count", "equipment_list"],
                  invariants=["no_retrieval", "argmax_all_ties"]),
        make_case("MT01-04", "multiturn", "오늘 WB공정에서 생산량 상위 5개 제품을 알려줘.", "explicit context switch resets process and rank",
                  scenario_id="MT01", turn_index=4, analysis_kind="rank", metrics=["production_qty"], dimensions=["device"],
                  filters=["date.today", "process.wb"], operations=["filter", "aggregate", "rank"], followup_mode="context_switch",
                  replace=["process", "rank", "source"], drop=["equipment_enrichment"], output_fields=["device", "production_qty"],
                  invariants=["top_n_exact:5", "no_stale_da_filter"]),
        make_case("MT02-01", "multiturn", "W/B공정 현재 HOLD LOT와 HOLD사유 알려줘", "seed current hold-lot result",
                  scenario_id="MT02", turn_index=1, analysis_kind="detail", dimensions=["lot_id", "hold_reason"],
                  filters=["snapshot.current", "process.wb", "hold.true"], operations=["filter", "detail", "sort"], datasets=["lot_status"],
                  output_fields=["lot_id", "hold_reason"], invariants=["current_snapshot", "hold_only"]),
        make_case("MT02-02", "multiturn", "HOLD 시간이 가장 오래된 LOT의 이력을 보여줘", "rank current holds then retrieve selected lot history",
                  route="deterministic", scenario_id="MT02", turn_index=2, scope="followup_requery", analysis_kind="rank_then_detail_history",
                  metrics=["hold_duration"], dimensions=["lot_id", "event_time", "hold_reason"], operations=["aggregate", "derive", "rank", "join", "sort", "project"],
                  followup_mode="referenced_result", inherit=["process", "hold_population"], replace=["detail_mode"], datasets=["lot_history"],
                  output_fields=["lot_id", "event_time", "event_type", "hold_reason", "hold_duration"],
                  invariants=["argmax_all_ties", "selected_lot_binding", "history_latest_first"]),
        make_case("MT03-01", "multiturn", "W/B공정 차수별 생산량과 재공수량 알려줘", "two-source production and WIP by generation",
                  route="deterministic", scenario_id="MT03", turn_index=1, analysis_kind="multi_source_compare",
                  metrics=["production_qty", "wip_qty"], dimensions=["generation"], filters=["process.wb"],
                  operations=["filter", "aggregate", "join", "project"], datasets=["production", "wip_snapshot"],
                  retrieval_calls=2, output_fields=["generation", "production_qty", "wip_qty"], invariants=["registered_join_only", "generation_grain"]),
        make_case("MT03-02", "multiturn", "위 결과를 제품별로 보여줘, 공정 조건도 유지해줘", "follow-up requery with dimension replacement",
                  scenario_id="MT03", turn_index=2, scope="followup_requery", analysis_kind="dimension_switch_requery",
                  metrics=["production_qty", "wip_qty"], dimensions=["device"], filters=["process.wb"],
                  operations=["filter", "aggregate", "join", "project"], followup_mode="referenced_semantics",
                  inherit=["metrics", "process", "source_bindings"], replace=["dimensions"], datasets=["production", "wip_snapshot"], retrieval_calls=2,
                  output_fields=["device", "production_qty", "wip_qty"], invariants=["process_filter_inherited", "dimension_replaced_not_added"]),
        make_case("MT04-01", "multiturn", "어제 Mobile제품의 PKG OUT실적을 제품별로 알려줘", "seed Mobile package-out result",
                  scenario_id="MT04", turn_index=1, metrics=["pkg_out_qty"], dimensions=["device"],
                  filters=["date.yesterday", "product.mobile"], operations=["filter", "aggregate", "sort"],
                  output_fields=["device", "pkg_out_qty"], invariants=["mobile_metadata_filter", "yesterday_kst"]),
        make_case("MT04-02", "multiturn", "pop제품은어땠어?", "elliptical product-category replacement",
                  route="intent_llm", scenario_id="MT04", turn_index=2, scope="followup_requery", analysis_kind="filter_replacement_requery",
                  metrics=["pkg_out_qty"], dimensions=["device"], filters=["date.yesterday", "product.pop"],
                  operations=["filter", "aggregate", "sort"], followup_mode="referenced_semantics",
                  inherit=["metric", "date", "dimensions"], replace=["product_filter"], retrieval_calls=None,
                  variants=[
                      {"variant_id": "complete_stored_source", "analysis_mode": "previous_source_transform", "retrieval_calls": 0,
                       "invariant_ids": ["coverage_contains_pop", "row_set_complete", "source_hash_valid"]},
                      {"variant_id": "insufficient_stored_source", "analysis_mode": "followup_requery", "retrieval_calls": 1,
                       "invariant_ids": ["coverage_missing_pop", "fresh_source_required"]},
                  ], output_fields=["device", "pkg_out_qty"],
                  invariants=["pop_replaces_mobile", "metric_and_date_inherited"]),
        make_case("MT05-01", "multiturn", "오늘 DA공정에서 생산량 상위 5개 제품을 알려줘", "seed top-five product result",
                  scenario_id="MT05", turn_index=1, analysis_kind="rank", metrics=["production_qty"], dimensions=["device"],
                  filters=["date.today", "process.da"], operations=["filter", "aggregate", "rank"],
                  output_fields=["device", "production_qty"], invariants=["top_n_exact:5", "stable_rank"]),
        make_case("MT05-02", "multiturn", "그중 생산량이 가장 많은 제품만 보여줘", "fast-path argmax over previous result",
                  scenario_id="MT05", turn_index=2, scope="previous_result_transform", analysis_kind="argmax_previous_result",
                  metrics=["production_qty"], dimensions=["device"], operations=["transform_previous_result", "rank", "project"],
                  followup_mode="referenced_result", inherit=["all_prior_columns", "result_ref"], replace=["rank"], datasets=[],
                  retrieval_calls=0, output_fields=["device", "production_qty"], invariants=["no_retrieval", "argmax_all_ties"]),
    ]
    return cases


def build_operator_cases() -> list[dict[str, Any]]:
    return [
        make_case("OP01", "operator", "production 데이터에서 DEVICE, OPER_NAME, PRODUCTION_QTY 컬럼만 이 순서로 보여줘", "exact field projection order",
                  analysis_kind="projection", dimensions=["device", "operation_name"], metrics=["production_qty"], operations=["project"],
                  output_fields=["device", "operation_name", "production_qty"], invariants=["exact_projection_order"]),
        make_case("OP02", "operator", "YIELD_RATE가 80 이상이고 MODE가 A이거나 LEAD가 비어 있는 행을 보여줘", "nested typed all/any filters",
                  analysis_kind="filter_detail", dimensions=["device"], filters=["all:yield_gte_80,any:mode_a,lead_blank"], operations=["filter", "detail"],
                  datasets=["product_master"], output_fields=["device", "yield_rate", "mode", "lead"], invariants=["filter_tree_precedence", "blank_not_only_null"]),
        make_case("OP03", "operator", "오늘 DA공정 생산량 상위 5개 제품을 보여줘", "global top-N rank",
                  analysis_kind="rank", metrics=["production_qty"], dimensions=["device"], filters=["date.today", "process.da"],
                  operations=["filter", "aggregate", "rank"], output_fields=["device", "production_qty"], invariants=["top_n_exact:5", "stable_rank"]),
        make_case("OP04", "operator", "MODE별 OUT 계획 상위 3개 제품을 보여줘", "per-group top-N rank",
                  analysis_kind="group_rank", metrics=["out_plan_qty"], dimensions=["mode", "device"], operations=["aggregate", "rank"],
                  datasets=["plan"], output_fields=["mode", "device", "out_plan_qty"], invariants=["top_n_per_group:3", "stable_rank"]),
        make_case("OP05", "operator", "생산량 최댓값과 동점인 제품을 모두 보여줘", "argmax with all ties",
                  analysis_kind="argmax", metrics=["production_qty"], dimensions=["device"], operations=["aggregate", "rank"],
                  output_fields=["device", "production_qty"], invariants=["argmax_all_ties"]),
        make_case("OP05A", "operator", "INPUT_QTY와 OUT_QTY 각 컬럼별로 값이 가장 큰 행을 보여줘", "independent per-metric argmax segments",
                  route="deterministic", analysis_kind="multi_metric_argmax", metrics=["input_qty", "out_qty"], dimensions=["device"],
                  operations=["rank", "concat_segments", "project"], datasets=["production"],
                  output_fields=["segment", "device", "input_qty", "out_qty"], invariants=["independent_argmax_per_metric", "all_ties_per_segment"]),
        make_case("OP06", "operator", "오늘 DA공정 생산량 상위 3개와 하위 3개를 함께 보여줘", "top and bottom ranked segments",
                  route="deterministic", analysis_kind="top_bottom_segments", metrics=["production_qty"], dimensions=["device"],
                  filters=["date.today", "process.da"], operations=["filter", "aggregate", "rank", "concat_segments"],
                  output_fields=["segment", "device", "production_qty"], invariants=["top_n_exact:3", "bottom_n_exact:3", "segments_labeled"]),
        make_case("OP07", "operator", "INPUT_QTY가 OUT_QTY보다 큰 행을 보여줘", "row-wise field comparison",
                  analysis_kind="field_compare", metrics=["input_qty", "out_qty"], dimensions=["device"], operations=["compare_fields", "detail"],
                  datasets=["production"], output_fields=["device", "input_qty", "out_qty"], invariants=["typed_numeric_compare", "null_compare_false"]),
        make_case("OP08", "operator", "TECH, DEN, MCP_NO 조합이 2개 이상 중복된 그룹과 행을 보여줘", "duplicate group detection with detail rows",
                  analysis_kind="duplicate_groups", dimensions=["tech", "den", "mcp_no", "device"], operations=["find_duplicate_groups", "join", "sort"],
                  datasets=["product_master"], output_fields=["tech", "den", "mcp_no", "device", "group_count"], invariants=["group_count_gte:2", "all_duplicate_rows"]),
        make_case("OP09", "operator", "등록된 DEVICE 키로 생산실적과 장비배정 데이터를 left join해서 보여줘", "policy-pinned left join",
                  route="deterministic", analysis_kind="join", metrics=["production_qty", "equipment_count"], dimensions=["device"], operations=["aggregate", "join", "project"],
                  datasets=["production", "equipment_assignment"], retrieval_calls=2, output_fields=["device", "production_qty", "equipment_count", "equipment_list"],
                  invariants=["left_join_policy", "left_rows_preserved", "join_cardinality_validated"]),
        make_case("OP10", "operator", "생산실적에는 있고 WIP에는 없는 제품을 보여줘", "positive-left missing-right presence filter",
                  route="deterministic", analysis_kind="presence_compare", metrics=["production_qty", "wip_qty"], dimensions=["device"],
                  operations=["aggregate", "presence_filter", "project"], datasets=["production", "wip_snapshot"], retrieval_calls=2,
                  output_fields=["device", "production_qty", "wip_qty"], invariants=["positive_left", "missing_right", "no_plain_join_inference"]),
        make_case("OP11", "operator", "제품별 INPUT 계획 대비 실제 INPUT 실적과 달성률을 보여줘", "registered join plus derived rate",
                  route="deterministic", analysis_kind="join_derive", metrics=["input_plan_qty", "input_qty", "achievement_rate"], dimensions=["device"],
                  operations=["aggregate", "join", "derive", "project"], formulas=["achievement_rate"], datasets=["plan", "input"], retrieval_calls=2,
                  output_fields=["device", "input_plan_qty", "input_qty", "achievement_rate"], invariants=["registered_plan_actual_join", "safe_divide"]),
        make_case("OP12", "operator", "LOT L1001의 HOLD 전체 이력을 최신순으로 보여줘", "registered entity history detail",
                  analysis_kind="history_detail", dimensions=["lot_id", "event_time"], filters=["lot_id.eq:L1001", "event_type.hold"], operations=["filter", "sort", "project"],
                  datasets=["lot_history"], output_fields=["lot_id", "event_time", "event_type", "hold_reason"], invariants=["all_history_rows", "latest_first"]),
        make_case("OP13", "operator", "등록되지 않은 SECRET_SCORE 컬럼으로 임의 수식을 계산해줘", "unsupported unregistered field and formula",
                  route="unsupported", analysis_kind="unsupported", operations=[], datasets=[], output_fields=[], retrieval_calls=0,
                  status="error", error_code="unsupported_operation", error_stage="route_eligibility",
                  invariants=["unsupported_before_retrieval", "state_unchanged"], tags=["negative"]),
    ]


def build_branch_cases() -> list[dict[str, Any]]:
    equivalence = "EQ-DA-TOP3-V1"
    return [
        make_case("BR-D01", "branch", "오늘 DA공정 제품별 생산량 상위 3개를 보여줘", "deterministic unique-complete selection probe",
                  analysis_kind="rank", metrics=["production_qty"], dimensions=["device"], filters=["date.today", "process.da"],
                  operations=["filter", "aggregate", "rank"], output_fields=["device", "production_qty"],
                  invariants=["intent_llm_calls_zero", "top_n_exact:3"], tags=["branch_probe", "zero_call"]),
        make_case("BR-L01", "branch", "오늘 DA 생산량과 현재 재공을 제품별로 비교해서 생산량 상위 5개를 보여줘", "deterministic multi-source selection probe",
                  route="deterministic", analysis_kind="multi_source_compare_rank", metrics=["production_qty", "wip_qty"], dimensions=["device"],
                  filters=["date.today:production", "snapshot.current:wip", "process.da"], operations=["filter", "aggregate", "join", "rank"],
                  datasets=["production", "wip_snapshot"], retrieval_calls=2, output_fields=["device", "production_qty", "wip_qty"],
                  invariants=["intent_llm_calls_zero", "registered_join_only"], tags=["branch_probe", "zero_call"]),
        make_case("BR-A01", "branch", "오늘 수량을 공정별로 보여줘", "ambiguous metric requires clarification",
                  route="intent_llm", reason="ambiguous_candidate_selection", analysis_kind="clarification", filters=["date.today"], operations=[],
                  datasets=[], output_fields=[], retrieval_calls=0, status="needs_clarification", error_stage="intent_validation",
                  invariants=["one_bounded_clarification", "no_retrieval_before_resolution"], tags=["branch_probe", "ambiguity"]),
        make_case("BR-U01", "branch", "등록되지 않은 SECRET_SCORE로 제품 위험도를 계산해줘", "unsupported route terminates before retrieval",
                  route="unsupported", analysis_kind="unsupported", operations=[], datasets=[], output_fields=[], retrieval_calls=0,
                  status="error", error_code="unsupported_operation", error_stage="route_eligibility",
                  invariants=["intent_llm_calls_zero", "unsupported_before_retrieval", "state_unchanged"], tags=["branch_probe", "negative"]),
        make_case("BR-F01", "branch", "오늘 DA공정 제품별 생산량을 보여줘", "deterministic compile fault injection never falls back",
                  analysis_kind="compile_failure", metrics=["production_qty"], dimensions=["device"], filters=["date.today", "process.da"],
                  operations=["filter", "aggregate", "join"], datasets=[], output_fields=[], retrieval_calls=0,
                  status="error", error_code="plan_contract_error", error_stage="plan_validation",
                  plan_fault_id="invalid_join_input",
                  invariants=["fixture_inject_plan_contract_failure", "compile_failure_no_llm_fallback", "no_retrieval_before_valid_plan"], tags=["branch_probe", "negative"]),
        make_case("BR-MT01", "branch", "그중 생산량이 가장 큰 제품만 보여줘", "follow-up previous-result fast path",
                  scenario_id="BR-MT", turn_index=2, scope="previous_result_transform", analysis_kind="argmax_previous_result",
                  metrics=["production_qty"], dimensions=["device"], operations=["transform_previous_result", "rank", "project"],
                  followup_mode="referenced_result", inherit=["all_prior_columns", "result_ref"], replace=["rank"], datasets=[], retrieval_calls=0,
                  seed_question="오늘 DA공정에서 생산량 상위 5개 제품을 보여줘",
                  output_fields=["device", "production_qty"], invariants=["intent_llm_calls_zero", "no_retrieval", "argmax_all_ties"], tags=["branch_probe", "fast_path"]),
        make_case("BR-EQD", "branch", "오늘 DA공정에서 제품별 생산량 상위 3개를 보여줘", "cross-route deterministic equivalence half",
                  reason="unique_complete_selection", analysis_kind="rank", metrics=["production_qty"], dimensions=["device"], filters=["date.today", "process.da"],
                  operations=["filter", "aggregate", "rank"], output_fields=["device", "production_qty"],
                  invariants=["semantic_plan_fingerprint_equal", "result_equal"], equivalence_group_id=equivalence, tags=["branch_probe", "equivalence"]),
        make_case("BR-EQL", "branch", "오늘 DA 쪽에서 잘 나간 제품 세 개만 보면?", "cross-route Intent LLM equivalence half",
                  route="intent_llm", reason="forced_equivalence_probe", analysis_kind="rank", metrics=["production_qty"], dimensions=["device"], filters=["date.today", "process.da"],
                  operations=["filter", "aggregate", "rank"], output_fields=["device", "production_qty"],
                  invariants=["semantic_plan_fingerprint_equal", "result_equal"], equivalence_group_id=equivalence, tags=["branch_probe", "equivalence"]),
    ]


def build_cases() -> list[dict[str, Any]]:
    cases = [*build_single_cases(), *build_date_cases(), *build_multiturn_cases(), *build_operator_cases(), *build_branch_cases()]
    ids = [case["case_id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("case_id values must be unique")
    return cases


def route_counts(cases: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = {"deterministic": 0, "intent_llm": 0, "unsupported": 0}
    for case in cases:
        counts[case["expected_route"]] += 1
    return counts


def _md(value: Any) -> str:
    if value is None:
        return "-"
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_acceptance_matrix(cases: list[dict[str, Any]]) -> str:
    counts = route_counts(cases)
    suites = ("single", "date", "multiturn", "operator", "branch")
    lines = [
        "# v6 Acceptance Matrix",
        "",
        "> GENERATED by `tools/generate_contracts_and_cases.py`. Do not hand-edit this file.",
        "",
        "This matrix is the machine-linked acceptance baseline for the metadata-driven v6 data-analysis flows. "
        "The canonical question and oracle for every row is in `validation/cases.jsonl`; this document is its readable index.",
        "",
        "## Frozen test context",
        "",
        f"- Reference instant: `{REFERENCE_INSTANT}`",
        f"- Timezone: `{REFERENCE_TIMEZONE}`",
        f"- Route contract: `analysis.route.v1` / policy `{ROUTE_POLICY_VERSION}`",
        "- Intent contract: `analysis.intent.v1`",
        "- Plan contract: `analysis.plan.v1`",
        "- Execution: typed registered operators only; generated pandas/Python and repair LLM are forbidden",
        "- Answer mode for canonical route cases: deterministic `narrative_off` (`expected_answer_llm_calls=0`); optional narrative compatibility is a separate presentation profile",
        "- Fallback: `false` for every case",
        "",
        "## Inventory and route budget",
        "",
        "| Suite | Cases | Deterministic (0 intent calls) | Intent LLM (1 intent call) | Unsupported (0 intent calls) |",
        "|---|---:|---:|---:|---:|",
    ]
    for suite in suites:
        subset = [case for case in cases if case["suite"] == suite]
        subset_counts = route_counts(subset)
        lines.append(f"| {suite} | {len(subset)} | {subset_counts['deterministic']} | {subset_counts['intent_llm']} | {subset_counts['unsupported']} |")
    lines.extend([
        f"| **Total** | **{len(cases)}** | **{counts['deterministic']}** | **{counts['intent_llm']}** | **{counts['unsupported']}** |",
        "",
        "The original validation inventory contains 62 cases: Q01-Q30, D01-D06, 12 MT turns, and OP01-OP13 including OP05A. "
        "Eight BR cases add explicit route-control assertions, producing 70 canonical cases total.",
        "",
        "## Mandatory gates",
        "",
        "| Gate | Pass condition | Evidence source |",
        "|---|---|---|",
        "| Schema closure | Every object schema is closed and every artifact validates against Draft 2020-12 | `tests/test_contract_artifacts.py` |",
        "| Deterministic route | Exact route, zero intent calls, valid typed intent and plan | `expected_route`, call counts, semantic/result oracle |",
        "| Intent LLM route | Exactly one intent call, schema-valid selection only, no generated code | case oracle plus trace/usage |",
        "| Unsupported route | Zero LLM calls, zero retrieval, `unsupported_operation`, no state mutation | BR-U01 and OP13 |",
        "| No hidden fallback | Compile/contract failure returns the registered error without route switching | BR-F01 |",
        "| Follow-up fast path | Prior result transform has zero intent calls and zero retrieval | MT01-03, MT05-02, BR-MT01 |",
        "| Cross-route equivalence | Equivalent semantic selection compiles to the same semantic plan/result fingerprint | BR-EQD and BR-EQL |",
        "| Result correctness | Grain, field order, operator sequence, tie/null/join/date rules match oracle invariants | `expected_result_contract` |",
        "| Output compatibility | Response, message display options, data refs/downloads, trace/usage, and state remain contract-valid | response and state contract tests |",
        "",
        "## Route-control branch cases",
        "",
        "| Case | Required branch behavior | Route | Intent calls | Retrieval calls | Expected status/error |",
        "|---|---|---|---:|---:|---|",
    ])
    for case in (case for case in cases if case["suite"] == "branch"):
        outcome = case["expected_error_code"] or case["expected_status"]
        lines.append(
            f"| {case['case_id']} | {_md(case['capability'])} | {case['expected_route']} | "
            f"{case['expected_intent_llm_calls']} | {_md(case['expected_retrieval_calls'])} | {_md(outcome)} |"
        )
    lines.extend([
        "",
        "## Per-case acceptance index",
        "",
        "A case passes only when route, call counts, status/error, semantic oracle, result oracle, and all invariant IDs pass. "
        "A correct-looking answer cannot compensate for a wrong branch or an undeclared fallback.",
        "",
        "| Case | Suite | Route | Intent calls | Status | Capability |",
        "|---|---|---|---:|---|---|",
    ])
    for case in cases:
        lines.append(
            f"| {case['case_id']} | {case['suite']} | {case['expected_route']} | "
            f"{case['expected_intent_llm_calls']} | {case['expected_status']} | {_md(case['capability'])} |"
        )
    lines.extend([
        "",
        "## Release decision",
        "",
        "Release is accepted only when the generator check, schema/registry/case tests, standalone component tests, exact Langflow 1.9.2 import tests, "
        "all 70 canonical cases, repeated Intent-LLM model-profile runs, and flow JSON/source synchronization pass. "
        "An unsupported or clarification response is accepted only for the case that explicitly requires it.",
        "",
    ])
    return "\n".join(lines)


def build_branch_questions(cases: list[dict[str, Any]]) -> str:
    branch = [case for case in cases if case["suite"] == "branch"]
    lines = [
        "# v6 branch validation questions",
        "# GENERATED by tools/generate_contracts_and_cases.py; canonical oracles are in validation/cases.jsonl.",
        f"# reference_instant={REFERENCE_INSTANT} timezone={REFERENCE_TIMEZONE}",
        "",
    ]
    for case in branch:
        lines.extend([
            f"[{case['case_id']}] route={case['expected_route']} intent_llm_calls={case['expected_intent_llm_calls']} "
            f"retrieval_calls={case['expected_retrieval_calls']} fallback_allowed=false",
            case["question"],
            "",
        ])
    return "\n".join(lines)


def build_branch_classification(cases: list[dict[str, Any]]) -> str:
    counts = route_counts(cases)
    lines = [
        "# Validation Route Classification",
        "",
        "> GENERATED by `tools/generate_contracts_and_cases.py`. `validation/cases.jsonl` is the executable source of truth.",
        "",
        "## Conservative policy",
        "",
        "A question is `deterministic` only when compiled metadata proves one complete semantic selection for every required slot. "
        "Multi-source comparison, join/presence semantics, variant-group logic, enrichment, and independently ranked segments may still be deterministic "
        "when every source, key, metric, policy, and operator is uniquely pinned. Only unresolved semantic choice or ellipsis uses the bounded "
        "`intent_llm` selector. An absent registered field/operator/policy is `unsupported`; it is never sent to an LLM to invent behavior.",
        "",
        "There is no automatic route fallback. Deterministic compile failure stays a typed failure; unsupported terminates before retrieval; "
        "previous-result transforms may use the deterministic zero-retrieval fast path.",
        "",
        "## Totals",
        "",
        f"- deterministic: {counts['deterministic']} cases, 0 intent LLM calls each",
        f"- intent_llm: {counts['intent_llm']} cases, exactly 1 intent LLM call each",
        f"- unsupported: {counts['unsupported']} cases, 0 intent LLM calls and 0 retrieval calls each",
        f"- total: {len(cases)} cases",
        "",
        "## Classification",
        "",
        "| Case | Suite | Route | Intent calls | Retrieval | Route reason | Capability |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for case in cases:
        lines.append(
            f"| {case['case_id']} | {case['suite']} | {case['expected_route']} | {case['expected_intent_llm_calls']} | "
            f"{_md(case['expected_retrieval_calls'])} | {_md(case['route_reason'])} | {_md(case['capability'])} |"
        )
    lines.extend([
        "",
        "## Equivalence oracle",
        "",
        "`BR-EQD` and `BR-EQL` intentionally take different routes but resolve to the same metric, dimension, filters, and typed operator sequence. "
        "Their semantic plan fingerprint and executed result must be identical; route provenance is trace data and is excluded from the semantic plan hash.",
        "",
    ])
    return "\n".join(lines)


def build_artifacts() -> dict[Path, str]:
    cases = build_cases()
    artifacts: dict[Path, str] = {
        Path("contracts/operator_registry.json"): json_text(build_operator_registry()),
        Path("contracts/error_registry.json"): json_text(build_error_registry()),
        Path("validation/cases.jsonl"): "".join(
            json.dumps(case, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for case in cases
        ),
        Path("validation/branch_validation_questions.txt"): build_branch_questions(cases),
        Path("validation/branch_classification.md"): build_branch_classification(cases),
        Path("validation/ACCEPTANCE_MATRIX.md"): build_acceptance_matrix(cases),
    }
    for filename, schema in build_schemas().items():
        artifacts[SCHEMA_DIR / filename] = json_text(schema)
    return artifacts


def write_artifacts(*, check: bool) -> int:
    mismatches: list[str] = []
    for relative_path, expected in build_artifacts().items():
        target = ROOT / relative_path
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == expected:
            continue
        if check:
            mismatches.append(relative_path.as_posix())
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected, encoding="utf-8", newline="\n")
        print(f"generated {relative_path.as_posix()}")
    if mismatches:
        print("generated artifacts are stale or missing:")
        for path in mismatches:
            print(f"  - {path}")
        return 1
    if check:
        print(f"OK: {len(build_artifacts())} generated artifacts are current")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated artifacts differ")
    args = parser.parse_args()
    return write_artifacts(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
