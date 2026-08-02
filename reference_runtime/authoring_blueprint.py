"""Trusted executable blueprint boundary for full-domain authoring.

Natural-language authoring remains useful for user-facing names and
descriptions, but an LLM must never be able to create or modify executable
metadata.  A reviewed blueprint therefore seals every executable draft
section and permits an authoring model to overlay only the two top-level
annotations defined here.

The blueprint self-hash detects accidental corruption.  It is not a trust
anchor by itself because an attacker could replace the executable and
recompute both internal hashes.  Every validation/merge call consequently
requires an independently configured ``expected_blueprint_sha256``.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .authoring_source_manifest import (
    AuthoringSourceManifestError,
    validate_authoring_source_manifest,
    validate_draft_inventory_coverage,
)
from .canonical import ContractError, canonical_bytes, sha256_json
from .contracts import validate_contract
from .domain_packages import GENERIC_V2_OPERATIONS, compile_domain_package


BLUEPRINT_VERSION = "metadata.executable-blueprint.v1"
AUTHORING_DRAFT_VERSION = "metadata.authoring.draft.v1"

EXECUTABLE_KEYS = (
    "contract_version",
    "locale",
    "timezone",
    "datasets",
    "metrics",
    "entity_groups",
    "grains",
    "relations",
    "orderings",
    "predicates",
    "recipes",
    "aliases",
    "prompt_extensions",
    "specialized_functions",
    "output_profile",
    "source_provenance",
)
ANNOTATION_KEYS = ("display_name", "description")
BLUEPRINT_KEYS = (
    "contract_version",
    "domain_id",
    "environment",
    "executable",
    "default_annotations",
    "source_manifest_sha256",
    "executable_sha256",
    "blueprint_sha256",
)

_BLUEPRINT_KEY_SET = set(BLUEPRINT_KEYS)
_EXECUTABLE_KEY_SET = set(EXECUTABLE_KEYS)
_ANNOTATION_KEY_SET = set(ANNOTATION_KEYS)
_DRAFT_KEY_SET = _EXECUTABLE_KEY_SET | _ANNOTATION_KEY_SET
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_DOMAIN_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
_ENVIRONMENT_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,31}$")


def _fail(reason: str, details: Mapping[str, Any] | None = None) -> None:
    raise ContractError(
        "metadata_dependency_error",
        "metadata_blueprint_validation",
        "신뢰된 metadata blueprint 검증에 실패했습니다.",
        {"reason": reason, **deepcopy(dict(details or {}))},
    )


def _identity(value: Any, *, label: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        _fail("identity_invalid", {"field": label})
    return value


def _sha256(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not _SHA256_PATTERN.fullmatch(value):
        _fail("sha256_invalid", {"field": label})
    return value


def _validated_manifest_sha256(source_manifest: Mapping[str, Any]) -> str:
    try:
        manifest = validate_authoring_source_manifest(source_manifest)
    except (AuthoringSourceManifestError, TypeError, ValueError) as exc:
        _fail("source_manifest_invalid")
        raise AssertionError("unreachable") from exc
    return _sha256(manifest.get("manifest_sha256"), label="source_manifest_sha256")


def _validate_source_coverage(
    source_manifest: Mapping[str, Any],
    draft: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        return validate_draft_inventory_coverage(
            source_manifest,
            draft,
            supported_operations=GENERIC_V2_OPERATIONS,
        )
    except AuthoringSourceManifestError as exc:
        # Source coverage evidence contains only registered identifiers/hashes
        # and bounded counts; it never includes raw source text.
        _fail("source_coverage_incomplete", exc.evidence)
        raise AssertionError("unreachable") from exc


def _executable_projection(draft: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(draft, Mapping):
        _fail("draft_not_object")
    actual_keys = set(draft)
    if actual_keys != _DRAFT_KEY_SET:
        _fail(
            "draft_top_level_keys_mismatch",
            {
                "missing": sorted(_DRAFT_KEY_SET - actual_keys),
                "extra": sorted(actual_keys - _DRAFT_KEY_SET),
            },
        )
    return {key: deepcopy(draft[key]) for key in EXECUTABLE_KEYS}


def _default_annotations(draft: Mapping[str, Any]) -> dict[str, str]:
    display_name = draft.get("display_name")
    description = draft.get("description")
    if not isinstance(display_name, str) or not display_name:
        _fail("default_annotation_invalid", {"field": "display_name"})
    annotations = {"display_name": display_name}
    if not isinstance(description, str):
        _fail("default_annotation_invalid", {"field": "description"})
    annotations["description"] = description
    return annotations


def compute_blueprint_sha256(blueprint: Mapping[str, Any]) -> str:
    """Hash the exact blueprint envelope, excluding only its self-hash."""

    if not isinstance(blueprint, Mapping):
        _fail("blueprint_not_object")
    material = {
        key: deepcopy(value)
        for key, value in blueprint.items()
        if key != "blueprint_sha256"
    }
    return sha256_json(material)


def build_executable_blueprint(
    draft: Mapping[str, Any],
    *,
    domain_id: str,
    environment: str,
    source_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Seal a reviewed full-domain draft into a trusted blueprint.

    This helper belongs to the administrative build path.  Runtime requests
    must load the resulting artifact and validate it against an external hash
    pin; they must not build a blueprint from request or LLM payloads.
    """

    normalized_domain = _identity(domain_id, label="domain_id", pattern=_DOMAIN_ID_PATTERN)
    normalized_environment = _identity(
        environment,
        label="environment",
        pattern=_ENVIRONMENT_PATTERN,
    )
    source_manifest_sha256 = _validated_manifest_sha256(source_manifest)
    draft_copy = deepcopy(dict(draft)) if isinstance(draft, Mapping) else draft
    validate_contract(
        draft_copy,
        "metadata-authoring-draft.schema.json",
        stage="metadata_blueprint_build",
        error_code="metadata_dependency_error",
    )
    executable = _executable_projection(draft_copy)
    annotations = _default_annotations(draft_copy)

    # Semantic compilation is part of blueprint creation, not deferred until
    # a live LLM call.  The returned package is deliberately discarded.
    _validate_source_coverage(source_manifest, draft_copy)
    compile_domain_package(draft_copy, normalized_domain, normalized_environment)

    material: dict[str, Any] = {
        "contract_version": BLUEPRINT_VERSION,
        "domain_id": normalized_domain,
        "environment": normalized_environment,
        "executable": executable,
        "default_annotations": annotations,
        "source_manifest_sha256": source_manifest_sha256,
        "executable_sha256": sha256_json(executable),
    }
    blueprint = {**material, "blueprint_sha256": sha256_json(material)}
    validate_contract(
        blueprint,
        "executable-blueprint.schema.json",
        stage="metadata_blueprint_build",
        error_code="metadata_dependency_error",
    )
    return deepcopy(blueprint)


def validate_executable_blueprint(
    blueprint: Mapping[str, Any],
    *,
    expected_blueprint_sha256: str,
    expected_domain_id: str,
    expected_environment: str,
    source_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate a blueprint against independently supplied trust pins."""

    if not isinstance(blueprint, Mapping):
        _fail("blueprint_not_object")
    value = deepcopy(dict(blueprint))
    actual_keys = set(value)
    if actual_keys != _BLUEPRINT_KEY_SET:
        _fail(
            "blueprint_top_level_keys_mismatch",
            {
                "missing": sorted(_BLUEPRINT_KEY_SET - actual_keys),
                "extra": sorted(actual_keys - _BLUEPRINT_KEY_SET),
            },
        )
    validate_contract(
        value,
        "executable-blueprint.schema.json",
        stage="metadata_blueprint_validation",
        error_code="metadata_dependency_error",
    )

    pinned_blueprint_sha256 = _sha256(
        expected_blueprint_sha256,
        label="expected_blueprint_sha256",
    )
    pinned_domain = _identity(
        expected_domain_id,
        label="expected_domain_id",
        pattern=_DOMAIN_ID_PATTERN,
    )
    pinned_environment = _identity(
        expected_environment,
        label="expected_environment",
        pattern=_ENVIRONMENT_PATTERN,
    )
    pinned_source_manifest_sha256 = _validated_manifest_sha256(source_manifest)

    if value["contract_version"] != BLUEPRINT_VERSION:
        _fail("blueprint_version_mismatch")
    if value["domain_id"] != pinned_domain:
        _fail("domain_pin_mismatch")
    if value["environment"] != pinned_environment:
        _fail("environment_pin_mismatch")
    if value["source_manifest_sha256"] != pinned_source_manifest_sha256:
        _fail("source_manifest_pin_mismatch")

    executable = value["executable"]
    if not isinstance(executable, Mapping) or set(executable) != _EXECUTABLE_KEY_SET:
        _fail("executable_keys_mismatch")
    expected_executable_sha256 = sha256_json(executable)
    if value["executable_sha256"] != expected_executable_sha256:
        _fail("executable_hash_mismatch")

    expected_self_hash = compute_blueprint_sha256(value)
    if value["blueprint_sha256"] != expected_self_hash:
        _fail("blueprint_self_hash_mismatch")
    if value["blueprint_sha256"] != pinned_blueprint_sha256:
        _fail("blueprint_external_pin_mismatch")

    defaults = value["default_annotations"]
    if not isinstance(defaults, Mapping) or set(defaults) != _ANNOTATION_KEY_SET:
        _fail("default_annotations_keys_mismatch")

    # Rebuild and compile the default draft so a hash-correct but semantically
    # invalid administrative artifact never crosses the runtime boundary.
    default_draft = {**deepcopy(dict(executable)), **deepcopy(dict(defaults))}
    if canonical_bytes(_executable_projection(default_draft)) != canonical_bytes(executable):
        _fail("executable_projection_changed")
    validate_contract(
        default_draft,
        "metadata-authoring-draft.schema.json",
        stage="metadata_blueprint_validation",
        error_code="metadata_dependency_error",
    )
    _validate_source_coverage(source_manifest, default_draft)
    compile_domain_package(default_draft, pinned_domain, pinned_environment)
    return value


def merge_blueprint_annotations(
    blueprint: Mapping[str, Any],
    annotations: Mapping[str, Any] | None,
    *,
    expected_blueprint_sha256: str,
    expected_domain_id: str,
    expected_environment: str,
    source_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Overlay allowlisted annotations and return a compiled-valid full draft.

    ``display_name`` and ``description`` are the only accepted LLM-produced
    fields.  Missing values retain the reviewed defaults.  All executable
    sections are copied from the validated blueprint and checked byte-for-byte
    (canonical UTF-8 JSON) before and after the merge and semantic compile.
    """

    sealed = validate_executable_blueprint(
        blueprint,
        expected_blueprint_sha256=expected_blueprint_sha256,
        expected_domain_id=expected_domain_id,
        expected_environment=expected_environment,
        source_manifest=source_manifest,
    )
    if annotations is None:
        proposal: dict[str, Any] = {}
    elif isinstance(annotations, Mapping):
        proposal = deepcopy(dict(annotations))
    else:
        _fail("annotations_not_object")
    extra = set(proposal) - _ANNOTATION_KEY_SET
    if extra:
        _fail("annotation_key_not_allowed", {"extra": sorted(extra)})

    if "display_name" in proposal:
        display_name = proposal["display_name"]
        if not isinstance(display_name, str) or not display_name or len(display_name) > 200:
            _fail("annotation_value_invalid", {"field": "display_name"})
    if "description" in proposal:
        description = proposal["description"]
        if not isinstance(description, str) or len(description) > 4000:
            _fail("annotation_value_invalid", {"field": "description"})

    executable = deepcopy(sealed["executable"])
    before_bytes = canonical_bytes(executable)
    merged_annotations = deepcopy(sealed["default_annotations"])
    merged_annotations.update(proposal)
    draft = {**executable, **merged_annotations}

    validate_contract(
        draft,
        "metadata-authoring-draft.schema.json",
        stage="metadata_blueprint_merge",
        error_code="metadata_dependency_error",
    )
    compile_domain_package(draft, expected_domain_id, expected_environment)

    after_projection = _executable_projection(draft)
    after_bytes = canonical_bytes(after_projection)
    if after_bytes != before_bytes:
        _fail("executable_bytes_changed")
    if sha256_json(after_projection) != sealed["executable_sha256"]:
        _fail("executable_hash_changed")
    return deepcopy(draft)


# Backward-readable spelling for callers that prefer an action verb.
apply_domain_blueprint_annotations = merge_blueprint_annotations


__all__ = [
    "ANNOTATION_KEYS",
    "AUTHORING_DRAFT_VERSION",
    "BLUEPRINT_KEYS",
    "BLUEPRINT_VERSION",
    "EXECUTABLE_KEYS",
    "apply_domain_blueprint_annotations",
    "build_executable_blueprint",
    "compute_blueprint_sha256",
    "merge_blueprint_annotations",
    "validate_executable_blueprint",
]
