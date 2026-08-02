"""Deterministic section patches for ``metadata.runtime.catalog.v2`` authoring.

The authoring LLM is allowed to describe a bounded section patch.  It never
edits an active runtime catalog directly.  This module reconstructs the closed
authoring draft, applies an upsert-only patch to the section selected by the
Flow, and validates the complete draft before the normal domain compiler runs.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .canonical import ContractError
from .contracts import validate_contract
from .domain_packages import (
    AUTHORING_DRAFT_VERSION,
    RUNTIME_CATALOG_V2,
    validate_runtime_catalog_v2,
)


_IDENTITY_FIELDS = {
    "metrics": "metric_id",
    "entity_groups": "group_id",
    "grains": "grain_id",
    "relations": "relation_id",
    "orderings": "ordering_id",
    "predicates": "predicate_id",
    "recipes": "recipe_id",
}

_PATCH_SECTIONS = {
    "dataset": frozenset({"datasets"}),
    "main_filter": frozenset(
        {"aliases", "entity_groups", "grains", "orderings", "predicates", "recipes"}
    ),
    "domain_policy": frozenset(
        {"prompt_extensions", "specialized_functions", "output_profile"}
    ),
}

_DELETE_KEYS = frozenset(
    {
        "$delete",
        "_delete",
        "delete",
        "delete_keys",
        "deleted",
        "remove",
        "remove_keys",
        "removed",
    }
)


def _fail(message: str, details: Mapping[str, Any] | None = None) -> None:
    raise ContractError(
        "metadata_schema_error",
        "metadata_section_patch",
        message,
        dict(details or {}),
    )


def _without_identity_cards(
    values: Mapping[str, Any], identity_field: str
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for key in sorted(values):
        raw = values[key]
        if not isinstance(raw, Mapping):
            _fail("runtime catalog identity card must be an object.", {"section_key": key})
        item = deepcopy(dict(raw))
        if str(item.pop(identity_field, key)) != str(key):
            _fail(
                "runtime catalog identity card does not match its map key.",
                {"section_key": key, "identity_field": identity_field},
            )
        result[str(key)] = item
    return result


def runtime_catalog_v2_to_authoring_draft(catalog: Mapping[str, Any]) -> dict[str, Any]:
    """Reconstruct a closed authoring draft without inventing domain values."""

    validated = validate_runtime_catalog_v2(deepcopy(dict(catalog)))
    if validated.get("contract_version") != RUNTIME_CATALOG_V2:
        _fail("metadata.runtime.catalog.v2 is required.")

    datasets: dict[str, dict[str, Any]] = {}
    for dataset_key in sorted(validated["datasets"]):
        raw = validated["datasets"][dataset_key]
        if not isinstance(raw, Mapping):
            _fail("runtime dataset must be an object.", {"dataset_key": dataset_key})
        dataset = deepcopy(dict(raw))
        if str(dataset.pop("key", dataset_key)) != str(dataset_key):
            _fail("runtime dataset key does not match its map key.", {"dataset_key": dataset_key})
        datasets[str(dataset_key)] = dataset

    draft: dict[str, Any] = {
        "contract_version": AUTHORING_DRAFT_VERSION,
        "display_name": str(validated.get("display_name") or validated["domain_id"]),
        "description": str(validated.get("description") or ""),
        "locale": str(validated.get("locale") or "ko-KR"),
        "timezone": str(validated.get("timezone") or "Asia/Seoul"),
        "datasets": datasets,
        "metrics": _without_identity_cards(validated.get("metrics") or {}, "metric_id"),
        "entity_groups": _without_identity_cards(
            validated.get("entity_groups") or {}, "group_id"
        ),
        "grains": _without_identity_cards(validated.get("grains") or {}, "grain_id"),
        "relations": _without_identity_cards(
            validated.get("relations") or {}, "relation_id"
        ),
        "orderings": _without_identity_cards(
            validated.get("orderings") or {}, "ordering_id"
        ),
        "predicates": _without_identity_cards(
            validated.get("predicates") or {}, "predicate_id"
        ),
        "recipes": _without_identity_cards(validated.get("recipes") or {}, "recipe_id"),
        "aliases": deepcopy(dict(validated.get("aliases") or {})),
        "prompt_extensions": deepcopy(dict(validated.get("prompt_extensions") or {})),
        "specialized_functions": deepcopy(list(validated.get("specialized_functions") or [])),
        "output_profile": deepcopy(dict(validated.get("output_profile") or {})),
        "source_provenance": {
            "source_type": "compiled_runtime_catalog_v2",
            "base_catalog_sha256": str(validated.get("catalog_sha256") or ""),
        },
    }
    return validate_contract(
        draft,
        "metadata-authoring-draft.schema.json",
        stage="metadata_section_patch",
        error_code="metadata_schema_error",
    )


def _assert_no_delete_directive(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            if key.casefold() in _DELETE_KEYS:
                _fail(
                    "authoring section patches are upsert-only.",
                    {"path": ".".join((*path, key))},
                )
            _assert_no_delete_directive(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_delete_directive(child, (*path, str(index)))


def _deep_upsert(base: Mapping[str, Any], patch: Mapping[str, Any]) -> dict[str, Any]:
    merged = deepcopy(dict(base))
    for key in sorted(patch):
        value = patch[key]
        if key in merged and isinstance(merged[key], Mapping) and isinstance(value, Mapping):
            merged[key] = _deep_upsert(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _upsert_specialized_functions(base: Any, patch: Any) -> list[dict[str, Any]]:
    """Upsert function cards by immutable ``(function_id, version)`` identity.

    A policy patch must not silently remove an existing registered function.
    Replacing one exact identity is allowed because the complete card remains
    schema-validated and its implementation hash is pinned by the compiler.
    """

    if not isinstance(base, list) or not isinstance(patch, list) or not patch:
        _fail("specialized_functions policy patch must be a non-empty array.")
    merged: dict[tuple[str, int], dict[str, Any]] = {}
    for source, label in ((base, "base"), (patch, "patch")):
        for index, raw in enumerate(source):
            if not isinstance(raw, Mapping):
                _fail(
                    "specialized function policy card must be an object.",
                    {"source": label, "index": index},
                )
            item = deepcopy(dict(raw))
            function_id = str(item.get("function_id") or "")
            try:
                version = int(item.get("version"))
            except (TypeError, ValueError):
                version = 0
            if not function_id or version < 1:
                _fail(
                    "specialized function policy identity is incomplete.",
                    {"source": label, "index": index},
                )
            merged[(function_id, version)] = item
    return [merged[key] for key in sorted(merged)]


def apply_authoring_section_patch(
    base_draft: Mapping[str, Any],
    patch: Mapping[str, Any],
    authoring_kind: str,
) -> dict[str, Any]:
    """Apply one closed, upsert-only authoring patch and validate the full draft.

    ``domain`` is a deliberate full-draft replacement. Section authoring kinds
    may only modify their registered top-level sections. ``domain_policy``
    owns prompt wording, registered standalone functions and output policy;
    it never regenerates datasets, metrics, relations or filter metadata.
    """

    base = validate_contract(
        deepcopy(dict(base_draft)),
        "metadata-authoring-draft.schema.json",
        stage="metadata_section_patch",
        error_code="metadata_schema_error",
    )
    if not isinstance(patch, Mapping):
        _fail("authoring section patch must be an object.")
    incoming = deepcopy(dict(patch))
    _assert_no_delete_directive(incoming)
    kind = str(authoring_kind or "").strip().casefold()

    if kind == "domain":
        if incoming.get("contract_version") != AUTHORING_DRAFT_VERSION:
            _fail("domain authoring requires a complete metadata.authoring.draft.v1 object.")
        return validate_contract(
            incoming,
            "metadata-authoring-draft.schema.json",
            stage="metadata_section_patch",
            error_code="metadata_schema_error",
        )

    allowed = _PATCH_SECTIONS.get(kind)
    if allowed is None:
        _fail("unsupported authoring section kind.", {"authoring_kind": authoring_kind})
    unknown = sorted(set(incoming) - set(allowed))
    if unknown:
        _fail(
            "authoring patch contains a section owned by another Flow.",
            {"authoring_kind": kind, "unknown_sections": unknown},
        )
    if not incoming:
        _fail("authoring section patch is empty.", {"authoring_kind": kind})

    result = deepcopy(base)
    for section in sorted(incoming):
        value = incoming[section]
        if section == "specialized_functions":
            result[section] = _upsert_specialized_functions(result.get(section), value)
            continue
        if not isinstance(value, Mapping) or not value:
            _fail(
                "authoring section patch must contain at least one object entry.",
                {"section": section},
            )
        before = result.get(section)
        if not isinstance(before, Mapping):
            _fail("base authoring section is not an object.", {"section": section})
        result[section] = _deep_upsert(before, value)

    return validate_contract(
        result,
        "metadata-authoring-draft.schema.json",
        stage="metadata_section_patch",
        error_code="metadata_schema_error",
    )


__all__ = [
    "apply_authoring_section_patch",
    "runtime_catalog_v2_to_authoring_draft",
]
