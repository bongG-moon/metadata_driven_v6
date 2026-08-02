"""Schema validation helpers used by the reference runtime and builders."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .canonical import ContractError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "contracts" / "schemas"


ERROR_CODE_BY_SCHEMA = {
    "request-capsule.schema.json": "intent_contract_error",
    "analysis-route.schema.json": "route_contract_error",
    "semantic-intent.schema.json": "intent_contract_error",
    "analysis-plan.schema.json": "plan_contract_error",
    "source-result.schema.json": "source_schema_mismatch",
    "analysis-result.schema.json": "result_schema_violation",
    "executed-result.schema.json": "result_schema_violation",
    "turn-state.schema.json": "state_conflict",
    "answer-facts.schema.json": "answer_claim_violation",
    "answer-sections.schema.json": "answer_claim_violation",
    "display-options.schema.json": "answer_claim_violation",
    "response.schema.json": "answer_claim_violation",
    "gaia-metadata.schema.json": "answer_claim_violation",
    "error.schema.json": "answer_claim_violation",
    "metadata-authoring-draft.schema.json": "metadata_dependency_error",
    "executable-blueprint.schema.json": "metadata_dependency_error",
    "runtime-catalog-v2.schema.json": "metadata_dependency_error",
    "registered-function-card.schema.json": "metadata_dependency_error",
    "registered-call.schema.json": "plan_contract_error",
    "domain-package.schema.json": "metadata_dependency_error",
    "active-domain-pointer.schema.json": "metadata_dependency_error",
}


@lru_cache(maxsize=64)
def _load_schema_cached(name: str) -> dict[str, Any]:
    path = SCHEMA_ROOT / name
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(name: str) -> dict[str, Any]:
    """Return an isolated schema copy so callers cannot mutate the cache."""

    return deepcopy(_load_schema_cached(name))


@lru_cache(maxsize=64)
def contract_validator(name: str) -> Draft202012Validator:
    schema = _load_schema_cached(name)
    Draft202012Validator.check_schema(schema)
    format_checker = FormatChecker()

    # Some minimal jsonschema installations omit the optional RFC3339 helper.
    # Register a strict local checker so ``format: date-time`` never degrades to
    # an ignored annotation merely because an optional package is absent.
    @format_checker.checks("date-time", raises=(TypeError, ValueError))
    def _date_time_with_offset(value: object) -> bool:
        if not isinstance(value, str):
            return False
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None

    return Draft202012Validator(schema, format_checker=format_checker)


def validate_contract(
    value: Any,
    schema_name: str,
    *,
    stage: str = "contract_validation",
    error_code: str | None = None,
) -> Any:
    """Validate a boundary payload without mutating it.

    ``FormatChecker`` is deliberately enabled: ``date-time`` and other format
    declarations are executable parts of the boundary contract, not comments.
    """

    errors = sorted(contract_validator(schema_name).iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        path = ".".join(str(part) for part in first.absolute_path) or "$"
        raise ContractError(
            error_code or ERROR_CODE_BY_SCHEMA.get(schema_name, "plan_contract_error"),
            stage,
            "계약 형식이 올바르지 않습니다.",
            {"schema": schema_name, "path": path, "reason": first.message[:400]},
        )
    return value
