"""Static allowlist for deterministic registered-function execution.

Registered functions receive only schema-validated scalar payloads and return
schema-validated selection data.  Domain catalogs can bind canonical fields
and bounded parameters, but cannot provide source text or module paths.
"""

from __future__ import annotations

import time
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from jsonschema import Draft202012Validator

from .canonical import ContractError, byte_size, json_value, sha256_json


REGISTERED_CALL_VERSION = "registered_call.v1"
FAILURE_POLICY = "fail_closed"

_CARD_KEYS = {
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
}
_LIMIT_KEYS = {"timeout_ms", "max_input_rows", "max_output_rows", "max_output_bytes"}
_CALL_KEYS = {
    "contract_version",
    "id",
    "op",
    "input",
    "function_ref",
    "required_fields",
    "arguments",
    "limits",
    "failure_policy",
}
_FUNCTION_REF_KEYS = {
    "function_id",
    "version",
    "implementation_sha256",
    "input_schema_sha256",
    "output_schema_sha256",
}
_CALL_TEMPLATE_KEYS = {"dataset_ref", "field_ref", "parameters", "output_fields"}
_TRIM_ARGUMENT_KEYS = {"field_ref", "tokens", "operator", "match_mode", "case_sensitive"}
_PRODUCT_ARGUMENT_KEYS = {"rules", "match_mode", "case_sensitive"}
_RANGE_ARGUMENT_KEYS = {"field_ref", "start", "end", "ordering_items"}

_TRIM_AND_MATCH_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["values", "tokens", "operator", "match_mode", "case_sensitive"],
    "properties": {
        "values": {
            "type": "array",
            "maxItems": 100_000,
            "items": {"type": ["string", "null"]},
        },
        "tokens": {
            "type": "array",
            "minItems": 1,
            "maxItems": 64,
            "uniqueItems": True,
            "items": {"type": "string", "minLength": 1, "maxLength": 256},
        },
        "operator": {"enum": ["equals", "contains", "starts_with", "ends_with"]},
        "match_mode": {"enum": ["any", "all"]},
        "case_sensitive": {"type": "boolean"},
    },
}

_TRIM_AND_MATCH_OUTPUT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["selected_indices"],
    "properties": {
        "selected_indices": {
            "type": "array",
            "maxItems": 100_000,
            "uniqueItems": True,
            "items": {"type": "integer", "minimum": 0},
        }
    },
}

_PRODUCT_TOKEN_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["records", "rules", "match_mode", "case_sensitive"],
    "properties": {
        "records": {"type": "array", "maxItems": 100_000, "items": {"type": "object"}},
        "rules": {
            "type": "array",
            "minItems": 1,
            "maxItems": 32,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["field_ref", "operator", "value"],
                "properties": {
                    "field_ref": {"type": "string", "minLength": 1, "maxLength": 128},
                    "operator": {"enum": ["equals", "starts_with", "contains", "ends_with"]},
                    "value": {"type": "string", "minLength": 1, "maxLength": 256},
                },
            },
        },
        "match_mode": {"const": "all"},
        "case_sensitive": {"type": "boolean"},
    },
}

_ORDERED_RANGE_INPUT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["values", "start", "end", "ordering_items"],
    "properties": {
        "values": {"type": "array", "maxItems": 100_000, "items": {"type": ["number", "null"]}},
        "start": {"type": "string", "minLength": 1, "maxLength": 128},
        "end": {"type": "string", "minLength": 1, "maxLength": 128},
        "ordering_items": {
            "type": "array",
            "minItems": 1,
            "maxItems": 512,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["label", "aliases", "sequence"],
                "properties": {
                    "label": {"type": "string", "minLength": 1, "maxLength": 128},
                    "aliases": {"type": "array", "maxItems": 32, "items": {"type": "string", "minLength": 1, "maxLength": 128}},
                    "sequence": {"type": "number"},
                },
            },
        },
    },
}


def _implementation_pin(
    function_id: str,
    version: int,
    behavior_revision: str,
    input_schema: Mapping[str, Any],
    output_schema: Mapping[str, Any],
) -> str:
    """Hash the reviewed behavior contract used by the local allowlist."""

    return sha256_json(
        {
            "function_id": function_id,
            "version": version,
            "behavior_revision": behavior_revision,
            "input_schema": input_schema,
            "output_schema": output_schema,
            "effect": "select_rows_by_index",
        }
    )


def _trim_and_match_tokens(payload: Mapping[str, Any], deadline: float) -> dict[str, Any]:
    values = list(payload["values"])
    tokens = [str(value).strip() for value in payload["tokens"]]
    if any(not token for token in tokens):
        _contract_error("registered function tokens must remain non-empty after trimming.")
    case_sensitive = bool(payload["case_sensitive"])
    if not case_sensitive:
        tokens = [token.casefold() for token in tokens]
    operator = str(payload["operator"])
    match_mode = str(payload["match_mode"])

    def matches(value: Any, token: str) -> bool:
        normalized = str(value).strip()
        if not case_sensitive:
            normalized = normalized.casefold()
        if operator == "equals":
            return normalized == token
        if operator == "contains":
            return token in normalized
        if operator == "starts_with":
            return normalized.startswith(token)
        if operator == "ends_with":
            return normalized.endswith(token)
        raise AssertionError(operator)

    selected: list[int] = []
    for index, value in enumerate(values):
        if index % 128 == 0 and time.monotonic() > deadline:
            _limit_error("registered function exceeded its timeout.", {"timeout": True})
        if value is None:
            continue
        decisions = [matches(value, token) for token in tokens]
        if (all(decisions) if match_mode == "all" else any(decisions)):
            selected.append(index)
    if time.monotonic() > deadline:
        _limit_error("registered function exceeded its timeout.", {"timeout": True})
    return {"selected_indices": selected}


def _normalize_scalar(value: Any, *, case_sensitive: bool) -> str:
    normalized = str(value).strip()
    return normalized if case_sensitive else normalized.casefold()


def _match_product_tokens(payload: Mapping[str, Any], deadline: float) -> dict[str, Any]:
    rules = list(payload["rules"])
    case_sensitive = bool(payload["case_sensitive"])
    selected: list[int] = []
    for index, row in enumerate(payload["records"]):
        if index % 128 == 0 and time.monotonic() > deadline:
            _limit_error("registered function exceeded its timeout.", {"timeout": True})
        decisions: list[bool] = []
        for rule in rules:
            raw = row.get(str(rule["field_ref"]))
            if raw is None:
                decisions.append(False)
                continue
            value = _normalize_scalar(raw, case_sensitive=case_sensitive)
            token = _normalize_scalar(rule["value"], case_sensitive=case_sensitive)
            operator = str(rule["operator"])
            if operator == "equals":
                decisions.append(value == token)
            elif operator == "starts_with":
                decisions.append(value.startswith(token))
            elif operator == "contains":
                decisions.append(token in value)
            elif operator == "ends_with":
                decisions.append(value.endswith(token))
            else:
                raise AssertionError(operator)
        if decisions and all(decisions):
            selected.append(index)
    return {"selected_indices": selected}


def _filter_ordered_range(payload: Mapping[str, Any], deadline: float) -> dict[str, Any]:
    lookup: dict[str, float] = {}
    for item in payload["ordering_items"]:
        sequence = float(item["sequence"])
        for label in [item["label"], *item["aliases"]]:
            lookup[_normalize_scalar(label, case_sensitive=False).replace(" ", "")] = sequence
    start_key = _normalize_scalar(payload["start"], case_sensitive=False).replace(" ", "")
    end_key = _normalize_scalar(payload["end"], case_sensitive=False).replace(" ", "")
    if start_key not in lookup or end_key not in lookup:
        _contract_error("registered ordered range endpoint is absent from ordering metadata.")
    low, high = sorted((lookup[start_key], lookup[end_key]))
    selected: list[int] = []
    for index, value in enumerate(payload["values"]):
        if index % 128 == 0 and time.monotonic() > deadline:
            _limit_error("registered function exceeded its timeout.", {"timeout": True})
        if value is not None and low <= float(value) <= high:
            selected.append(index)
    return {"selected_indices": selected}


@dataclass(frozen=True, slots=True)
class _Registration:
    function_id: str
    version: int
    implementation_sha256: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    limit_ceiling: dict[str, int]
    handler: Callable[[Mapping[str, Any], float], dict[str, Any]]


_TRIM_AND_MATCH_ID = "core.trim_and_match_tokens"
_TRIM_AND_MATCH_VERSION = 1
_TRIM_AND_MATCH_SHA256 = _implementation_pin(
    _TRIM_AND_MATCH_ID,
    _TRIM_AND_MATCH_VERSION,
    "trim-strip-casefold-match.v1",
    _TRIM_AND_MATCH_INPUT_SCHEMA,
    _TRIM_AND_MATCH_OUTPUT_SCHEMA,
)

_PRODUCT_TOKEN_ID = "manufacturing.match_product_tokens"
_PRODUCT_TOKEN_VERSION = 1
_PRODUCT_TOKEN_SHA256 = _implementation_pin(
    _PRODUCT_TOKEN_ID,
    _PRODUCT_TOKEN_VERSION,
    "multi-field-trimmed-all-token-match.v1",
    _PRODUCT_TOKEN_INPUT_SCHEMA,
    _TRIM_AND_MATCH_OUTPUT_SCHEMA,
)

_ORDERED_RANGE_ID = "manufacturing.filter_ordered_range"
_ORDERED_RANGE_VERSION = 1
_ORDERED_RANGE_SHA256 = _implementation_pin(
    _ORDERED_RANGE_ID,
    _ORDERED_RANGE_VERSION,
    "metadata-ordering-inclusive-range.v1",
    _ORDERED_RANGE_INPUT_SCHEMA,
    _TRIM_AND_MATCH_OUTPUT_SCHEMA,
)

_REGISTRY: dict[tuple[str, int], _Registration] = {
    (_TRIM_AND_MATCH_ID, _TRIM_AND_MATCH_VERSION): _Registration(
        function_id=_TRIM_AND_MATCH_ID,
        version=_TRIM_AND_MATCH_VERSION,
        implementation_sha256=_TRIM_AND_MATCH_SHA256,
        input_schema=_TRIM_AND_MATCH_INPUT_SCHEMA,
        output_schema=_TRIM_AND_MATCH_OUTPUT_SCHEMA,
        limit_ceiling={
            "timeout_ms": 5_000,
            "max_input_rows": 100_000,
            "max_output_rows": 100_000,
            "max_output_bytes": 8 * 1024 * 1024,
        },
        handler=_trim_and_match_tokens,
    ),
    (_PRODUCT_TOKEN_ID, _PRODUCT_TOKEN_VERSION): _Registration(
        function_id=_PRODUCT_TOKEN_ID,
        version=_PRODUCT_TOKEN_VERSION,
        implementation_sha256=_PRODUCT_TOKEN_SHA256,
        input_schema=_PRODUCT_TOKEN_INPUT_SCHEMA,
        output_schema=_TRIM_AND_MATCH_OUTPUT_SCHEMA,
        limit_ceiling={"timeout_ms": 5_000, "max_input_rows": 100_000, "max_output_rows": 100_000, "max_output_bytes": 8 * 1024 * 1024},
        handler=_match_product_tokens,
    ),
    (_ORDERED_RANGE_ID, _ORDERED_RANGE_VERSION): _Registration(
        function_id=_ORDERED_RANGE_ID,
        version=_ORDERED_RANGE_VERSION,
        implementation_sha256=_ORDERED_RANGE_SHA256,
        input_schema=_ORDERED_RANGE_INPUT_SCHEMA,
        output_schema=_TRIM_AND_MATCH_OUTPUT_SCHEMA,
        limit_ceiling={"timeout_ms": 5_000, "max_input_rows": 100_000, "max_output_rows": 100_000, "max_output_bytes": 8 * 1024 * 1024},
        handler=_filter_ordered_range,
    ),
}


def registered_function_descriptor(function_id: str, version: int) -> dict[str, Any]:
    """Return public immutable metadata for one locally allowed implementation."""

    registration = _registration(function_id, version)
    return {
        "function_id": registration.function_id,
        "version": registration.version,
        "implementation_sha256": registration.implementation_sha256,
        "input_schema": deepcopy(registration.input_schema),
        "output_schema": deepcopy(registration.output_schema),
        "limit_ceiling": deepcopy(registration.limit_ceiling),
    }


def validate_registered_function_card(card: Mapping[str, Any]) -> dict[str, Any]:
    """Bind a closed catalog card to exactly one local implementation."""

    if not isinstance(card, Mapping) or set(card) != _CARD_KEYS:
        _contract_error(
            "registered function card does not match the closed contract.",
            {"actual_keys": sorted(card) if isinstance(card, Mapping) else []},
        )
    function_id = str(card.get("function_id") or "")
    version = _positive_int(card.get("version"), "version")
    registration = _registration(function_id, version)
    if card.get("execution_mode") != "registered_standalone":
        _contract_error("registered function execution mode is not allowed.")
    if str(card.get("implementation_sha256") or "") != registration.implementation_sha256:
        _unsupported(
            "registered function implementation hash does not match the local allowlist.",
            {"function_id": function_id, "version": version},
        )
    if card.get("input_schema") != registration.input_schema or card.get("output_schema") != registration.output_schema:
        _contract_error(
            "registered function schemas do not match the local implementation contract.",
            {"function_id": function_id, "version": version},
        )
    required_fields = card.get("required_fields")
    if (
        not isinstance(required_fields, list)
        or not required_fields
        or len(required_fields) > 16
        or len(required_fields) != len(set(map(str, required_fields)))
        or any(not isinstance(field, str) or not field for field in required_fields)
    ):
        _contract_error("registered function required_fields are invalid.")
    limits = _validate_limits(card.get("limits"), registration.limit_ceiling)
    if card.get("failure_policy") != FAILURE_POLICY:
        _contract_error("registered functions currently require fail_closed policy.")
    aliases = card.get("aliases")
    if (
        not isinstance(aliases, list)
        or not aliases
        or len(aliases) > 32
        or len(aliases) != len(set(map(str, aliases)))
        or any(not isinstance(alias, str) or not alias.strip() for alias in aliases)
    ):
        _contract_error("registered function aliases are invalid.")
    call_template = card.get("call_template")
    if not isinstance(call_template, Mapping) or set(call_template) != _CALL_TEMPLATE_KEYS:
        _contract_error("registered function call_template does not match the closed contract.")
    field_ref = str(call_template.get("field_ref") or "")
    if not isinstance(call_template.get("dataset_ref"), str) or not call_template.get("dataset_ref"):
        _contract_error("registered function dataset_ref is required.")
    if field_ref not in set(required_fields):
        _contract_error("registered function field_ref is absent from required_fields.")
    parameters = call_template.get("parameters")
    arguments = {"field_ref": field_ref, **dict(parameters or {})}
    _validate_arguments(arguments)
    output_fields = call_template.get("output_fields")
    if (
        not isinstance(output_fields, list)
        or not output_fields
        or len(output_fields) > 128
        or len(output_fields) != len(set(map(str, output_fields)))
        or any(not isinstance(field, str) or not field for field in output_fields)
    ):
        _contract_error("registered function output_fields are invalid.")
    normalized = deepcopy(dict(card))
    normalized["version"] = version
    normalized["limits"] = limits
    return normalized


def build_registered_call_operation(
    card: Mapping[str, Any],
    *,
    operation_id: str,
    input_ref: str,
) -> dict[str, Any]:
    """Compile one validated card into the closed ``registered_call.v1`` IR."""

    normalized = validate_registered_function_card(card)
    descriptor = registered_function_descriptor(
        str(normalized["function_id"]), int(normalized["version"])
    )
    template = dict(normalized["call_template"])
    arguments = {"field_ref": str(template["field_ref"]), **deepcopy(dict(template["parameters"]))}
    operation = {
        "contract_version": REGISTERED_CALL_VERSION,
        "id": str(operation_id),
        "op": "registered_call",
        "input": str(input_ref),
        "function_ref": {
            "function_id": descriptor["function_id"],
            "version": descriptor["version"],
            "implementation_sha256": descriptor["implementation_sha256"],
            "input_schema_sha256": sha256_json(descriptor["input_schema"]),
            "output_schema_sha256": sha256_json(descriptor["output_schema"]),
        },
        "required_fields": list(normalized["required_fields"]),
        "arguments": arguments,
        "limits": deepcopy(normalized["limits"]),
        "failure_policy": FAILURE_POLICY,
    }
    return validate_registered_call_operation(operation, catalog_card=normalized)


def build_specialized_call_operation(
    function_id: str,
    version: int,
    *,
    operation_id: str,
    input_ref: str,
    required_fields: list[str],
    arguments: Mapping[str, Any],
    limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dynamic-argument call to a statically allowlisted function."""

    descriptor = registered_function_descriptor(function_id, version)
    ceiling = descriptor["limit_ceiling"]
    selected_limits = dict(limits or ceiling)
    operation = {
        "contract_version": REGISTERED_CALL_VERSION,
        "id": str(operation_id),
        "op": "registered_call",
        "input": str(input_ref),
        "function_ref": {
            "function_id": descriptor["function_id"],
            "version": descriptor["version"],
            "implementation_sha256": descriptor["implementation_sha256"],
            "input_schema_sha256": sha256_json(descriptor["input_schema"]),
            "output_schema_sha256": sha256_json(descriptor["output_schema"]),
        },
        "required_fields": list(required_fields),
        "arguments": deepcopy(dict(arguments)),
        "limits": selected_limits,
        "failure_policy": FAILURE_POLICY,
    }
    return validate_registered_call_operation(operation)


def validate_registered_call_operation(
    operation: Mapping[str, Any],
    *,
    catalog_card: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate operation shape, implementation pin, schemas, and limits."""

    if not isinstance(operation, Mapping) or set(operation) != _CALL_KEYS:
        _contract_error(
            "registered call operation does not match the closed contract.",
            {"actual_keys": sorted(operation) if isinstance(operation, Mapping) else []},
        )
    if operation.get("contract_version") != REGISTERED_CALL_VERSION or operation.get("op") != "registered_call":
        _contract_error("registered call discriminator is invalid.")
    if not str(operation.get("id") or "") or not str(operation.get("input") or ""):
        _contract_error("registered call identity and input are required.")
    function_ref = operation.get("function_ref")
    if not isinstance(function_ref, Mapping) or set(function_ref) != _FUNCTION_REF_KEYS:
        _contract_error("registered call function_ref does not match the closed contract.")
    function_id = str(function_ref.get("function_id") or "")
    version = _positive_int(function_ref.get("version"), "function_ref.version")
    registration = _registration(function_id, version)
    expected_ref = {
        "function_id": function_id,
        "version": version,
        "implementation_sha256": registration.implementation_sha256,
        "input_schema_sha256": sha256_json(registration.input_schema),
        "output_schema_sha256": sha256_json(registration.output_schema),
    }
    if dict(function_ref) != expected_ref:
        _unsupported(
            "registered call function pin does not match the local allowlist.",
            {"function_id": function_id, "version": version},
        )
    required_fields = operation.get("required_fields")
    if (
        not isinstance(required_fields, list)
        or not required_fields
        or len(required_fields) != len(set(map(str, required_fields)))
        or any(not isinstance(field, str) or not field for field in required_fields)
    ):
        _contract_error("registered call required_fields are invalid.")
    arguments = operation.get("arguments")
    _validate_arguments(arguments, function_id=function_id)
    if function_id in {_TRIM_AND_MATCH_ID, _ORDERED_RANGE_ID}:
        if str(arguments["field_ref"]) not in set(required_fields):
            _contract_error("registered call field_ref is absent from required_fields.")
    elif function_id == _PRODUCT_TOKEN_ID:
        rule_fields = {str(rule["field_ref"]) for rule in arguments["rules"]}
        if not rule_fields <= set(required_fields):
            _contract_error("registered product token fields are absent from required_fields.")
    limits = _validate_limits(operation.get("limits"), registration.limit_ceiling)
    if operation.get("failure_policy") != FAILURE_POLICY:
        _contract_error("registered call failure policy must be fail_closed.")

    if catalog_card is not None:
        card = validate_registered_function_card(catalog_card)
        if (
            str(card["function_id"]) != function_id
            or int(card["version"]) != version
            or str(card["implementation_sha256"]) != registration.implementation_sha256
            or list(card["required_fields"]) != list(required_fields)
            or dict(card["limits"]) != limits
            or {"field_ref": card["call_template"]["field_ref"], **dict(card["call_template"]["parameters"])}
            != dict(arguments)
        ):
            _contract_error("registered call differs from its catalog card.")
    return deepcopy(dict(operation))


def dispatch_registered_call(operation: Mapping[str, Any], rows: list[dict[str, Any]]) -> list[int]:
    """Run one validated local implementation and return selected row indices."""

    normalized = validate_registered_call_operation(operation)
    limits = dict(normalized["limits"])
    if len(rows) > int(limits["max_input_rows"]):
        _limit_error(
            "registered function input row limit was exceeded.",
            {"actual_rows": len(rows), "max_input_rows": limits["max_input_rows"]},
        )
    function_ref = normalized["function_ref"]
    registration = _registration(str(function_ref["function_id"]), int(function_ref["version"]))
    function_id = registration.function_id
    arguments = normalized["arguments"]
    missing_fields = [
        (index, field)
        for index, row in enumerate(rows)
        for field in normalized["required_fields"]
        if field not in row
    ]
    if missing_fields:
        index, field = missing_fields[0]
        raise ContractError(
            "source_schema_mismatch",
            "registered_function_dispatch",
            "registered function required field is missing.",
            {"field": field, "first_missing_row": index},
        )
    if function_id == _TRIM_AND_MATCH_ID:
        field_ref = str(arguments["field_ref"])
        payload = {
            "values": [json_value(row[field_ref]) for row in rows],
            "tokens": deepcopy(arguments["tokens"]),
            "operator": arguments["operator"],
            "match_mode": arguments["match_mode"],
            "case_sensitive": arguments["case_sensitive"],
        }
    elif function_id == _PRODUCT_TOKEN_ID:
        payload = {
            "records": [
                {field: json_value(row.get(field)) for field in normalized["required_fields"]}
                for row in rows
            ],
            "rules": deepcopy(arguments["rules"]),
            "match_mode": arguments["match_mode"],
            "case_sensitive": arguments["case_sensitive"],
        }
    elif function_id == _ORDERED_RANGE_ID:
        field_ref = str(arguments["field_ref"])
        payload = {
            "values": [json_value(row[field_ref]) for row in rows],
            "start": arguments["start"],
            "end": arguments["end"],
            "ordering_items": deepcopy(arguments["ordering_items"]),
        }
    else:
        raise AssertionError(function_id)
    _validate_payload(registration.input_schema, payload, "input")
    deadline = time.monotonic() + (int(limits["timeout_ms"]) / 1000.0)
    result = registration.handler(payload, deadline)
    if time.monotonic() > deadline:
        _limit_error("registered function exceeded its timeout.", {"timeout": True})
    _validate_payload(registration.output_schema, result, "output")
    if byte_size(result) > int(limits["max_output_bytes"]):
        _limit_error(
            "registered function output byte limit was exceeded.",
            {"max_output_bytes": limits["max_output_bytes"]},
        )
    selected = list(result["selected_indices"])
    if len(selected) > int(limits["max_output_rows"]):
        _limit_error(
            "registered function output row limit was exceeded.",
            {"actual_rows": len(selected), "max_output_rows": limits["max_output_rows"]},
        )
    if selected != sorted(selected) or any(index >= len(rows) for index in selected):
        _contract_error("registered function returned invalid row indices.")
    return selected


def _registration(function_id: str, version: int) -> _Registration:
    registration = _REGISTRY.get((str(function_id), int(version)))
    if registration is None:
        _unsupported(
            "registered function identity is absent from the local allowlist.",
            {"function_id": str(function_id), "version": int(version)},
        )
    return registration


def _validate_arguments(value: Any, *, function_id: str = _TRIM_AND_MATCH_ID) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        _contract_error("registered function arguments must be an object.")
    expected_keys = {
        _TRIM_AND_MATCH_ID: _TRIM_ARGUMENT_KEYS,
        _PRODUCT_TOKEN_ID: _PRODUCT_ARGUMENT_KEYS,
        _ORDERED_RANGE_ID: _RANGE_ARGUMENT_KEYS,
    }.get(function_id)
    if expected_keys is None or set(value) != expected_keys:
        _contract_error(
            "registered function arguments do not match the closed contract.",
            {"actual_keys": sorted(value) if isinstance(value, Mapping) else []},
        )
    if function_id == _PRODUCT_TOKEN_ID:
        rules = value.get("rules")
        if not isinstance(rules, list) or not 1 <= len(rules) <= 32:
            _contract_error("registered product token rules are invalid.")
        for rule in rules:
            if not isinstance(rule, Mapping) or set(rule) != {"field_ref", "operator", "value"}:
                _contract_error("registered product token rule does not match the closed contract.")
            if not isinstance(rule.get("field_ref"), str) or not rule.get("field_ref"):
                _contract_error("registered product token field_ref is required.")
            if rule.get("operator") not in {"equals", "starts_with", "contains", "ends_with"}:
                _contract_error("registered product token operator is invalid.")
            if not isinstance(rule.get("value"), str) or not rule.get("value").strip():
                _contract_error("registered product token value is invalid.")
        if value.get("match_mode") != "all" or not isinstance(value.get("case_sensitive"), bool):
            _contract_error("registered product token match settings are invalid.")
        return deepcopy(dict(value))
    if function_id == _ORDERED_RANGE_ID:
        if not isinstance(value.get("field_ref"), str) or not value.get("field_ref"):
            _contract_error("registered ordered range field_ref is required.")
        if not isinstance(value.get("start"), str) or not value.get("start").strip():
            _contract_error("registered ordered range start is required.")
        if not isinstance(value.get("end"), str) or not value.get("end").strip():
            _contract_error("registered ordered range end is required.")
        items = value.get("ordering_items")
        if not isinstance(items, list) or not 1 <= len(items) <= 512:
            _contract_error("registered ordered range items are invalid.")
        for item in items:
            if not isinstance(item, Mapping) or set(item) != {"label", "aliases", "sequence"}:
                _contract_error("registered ordered range item does not match the closed contract.")
            if not isinstance(item.get("label"), str) or not item.get("label").strip():
                _contract_error("registered ordered range item label is required.")
            if not isinstance(item.get("aliases"), list) or any(not isinstance(alias, str) or not alias for alias in item["aliases"]):
                _contract_error("registered ordered range aliases are invalid.")
            if isinstance(item.get("sequence"), bool) or not isinstance(item.get("sequence"), (int, float)):
                _contract_error("registered ordered range sequence is invalid.")
        return deepcopy(dict(value))
    if not isinstance(value.get("field_ref"), str) or not value.get("field_ref"):
        _contract_error("registered function field_ref is required.")
    tokens = value.get("tokens")
    if (
        not isinstance(tokens, list)
        or not 1 <= len(tokens) <= 64
        or len(tokens) != len(set(map(str, tokens)))
        or any(not isinstance(token, str) or not token.strip() or len(token) > 256 for token in tokens)
    ):
        _contract_error("registered function tokens are invalid.")
    if value.get("operator") not in {"equals", "contains", "starts_with", "ends_with"}:
        _contract_error("registered function operator is invalid.")
    if value.get("match_mode") not in {"any", "all"}:
        _contract_error("registered function match_mode is invalid.")
    if not isinstance(value.get("case_sensitive"), bool):
        _contract_error("registered function case_sensitive must be boolean.")
    return deepcopy(dict(value))


def _validate_limits(value: Any, ceiling: Mapping[str, int]) -> dict[str, int]:
    if not isinstance(value, Mapping) or set(value) != _LIMIT_KEYS:
        _contract_error("registered function limits do not match the closed contract.")
    result: dict[str, int] = {}
    for key in sorted(_LIMIT_KEYS):
        number = _positive_int(value.get(key), f"limits.{key}")
        if number > int(ceiling[key]):
            _contract_error(
                "registered function limit exceeds the local ceiling.",
                {"limit": key, "value": number, "ceiling": int(ceiling[key])},
            )
        result[key] = number
    return result


def _validate_payload(schema: Mapping[str, Any], value: Any, direction: str) -> None:
    errors = sorted(
        Draft202012Validator(dict(schema)).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        first = errors[0]
        path = ".".join(map(str, first.absolute_path)) or "$"
        _contract_error(
            f"registered function {direction} schema validation failed.",
            {"path": path, "reason": first.message[:300]},
        )


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _contract_error(f"{label} must be a positive integer.")
    return int(value)


def _contract_error(message: str, details: dict[str, Any] | None = None) -> None:
    raise ContractError(
        "plan_contract_error",
        "registered_function_contract",
        message,
        details or {},
    )


def _unsupported(message: str, details: dict[str, Any] | None = None) -> None:
    raise ContractError(
        "unsupported_operation",
        "registered_function_allowlist",
        message,
        details or {},
    )


def _limit_error(message: str, details: dict[str, Any] | None = None) -> None:
    raise ContractError(
        "execution_memory_limit_exceeded",
        "registered_function_dispatch",
        message,
        details or {},
    )


__all__ = [
    "FAILURE_POLICY",
    "REGISTERED_CALL_VERSION",
    "build_registered_call_operation",
    "build_specialized_call_operation",
    "dispatch_registered_call",
    "registered_function_descriptor",
    "validate_registered_call_operation",
    "validate_registered_function_card",
]
