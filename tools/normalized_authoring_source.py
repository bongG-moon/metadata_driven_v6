"""Verify a reviewed v6 natural-language companion without mutating v5 input.

This module is migration-tooling only.  It deliberately does not teach the
standalone authoring component how to interpret broad legacy prose.  A caller
must supply a checked-in provenance record which pins both the untouched
original bytes and the reviewed, explicit-card companion bytes.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from reference_runtime.authoring_source_manifest import (
    MANIFEST_VERSION,
    extract_authoring_source_manifest,
)


PROVENANCE_VERSION = "metadata.normalized-authoring-source-provenance.v1"
MAX_PROVENANCE_BYTES = 16_384
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_NON_ALIAS_INVENTORIES = (
    "datasets",
    "fields",
    "field_bindings",
    "field_roles",
    "metrics",
    "grains",
    "grain_keys",
    "grain_display_fields",
    "relations",
    "relation_endpoints",
    "relation_keys",
    "relation_policies",
    "recipes",
    "operations",
)
_ALL_INVENTORIES = _NON_ALIAS_INVENTORIES + (
    "aliases",
    "alias_targets",
    "alias_bindings",
)
_DATASET_INVENTORIES = {"datasets", "fields", "field_bindings"}
_SOURCE_POLICIES = {
    "dataset": {
        "method": "reviewed-explicit-dataset-cards.v1",
        "required_sections": ["datasets", "fields"],
        "inventory_mode": "datasets_and_fields",
    },
    "main_filter": {
        "method": "reviewed-explicit-alias-cards.v1",
        "required_sections": ["aliases"],
        "inventory_mode": "aliases_only",
    },
    "domain_policy": {
        "method": "reviewed-domain-policy-request.v1",
        "required_sections": [],
        "inventory_mode": "empty",
    },
}
_FORBIDDEN_COMPANION_PATTERNS = (
    re.compile(r"```"),
    re.compile(r"(?:^|\n)\s*(?:from|import)\s+[A-Za-z_]", re.IGNORECASE),
    re.compile(r"\b(?:eval|exec|compile)\s*\(", re.IGNORECASE),
    re.compile(r"\bselect\b.{0,256}\bfrom\b", re.IGNORECASE | re.DOTALL),
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\b(?:password|passwd|api[_ -]?key|secret|access[_ -]?token)\s*[:=]", re.IGNORECASE),
    re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]+@", re.IGNORECASE),
)


class NormalizedAuthoringSourceError(ValueError):
    """Fail-closed provenance or companion validation error."""

    def __init__(self, code: str) -> None:
        self.code = str(code)
        super().__init__(self.code)


def _exact_mapping(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise NormalizedAuthoringSourceError(code)
    return dict(value)


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_value(value: Any, code: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise NormalizedAuthoringSourceError(code)
    return value


def _verified_path(root: Path, relative_value: Any, code: str) -> Path:
    if not isinstance(relative_value, str) or "\\" in relative_value:
        raise NormalizedAuthoringSourceError(code)
    relative = PurePosixPath(relative_value)
    if relative.is_absolute() or not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise NormalizedAuthoringSourceError(code)
    root_resolved = root.resolve(strict=True)
    resolved = root_resolved.joinpath(*relative.parts).resolve(strict=True)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise NormalizedAuthoringSourceError(code) from exc
    if not resolved.is_file():
        raise NormalizedAuthoringSourceError(code)
    return resolved


def _verified_utf8(path: Path, expected_sha256: str, code: str) -> str:
    raw = path.read_bytes()
    if _sha256(raw) != expected_sha256:
        raise NormalizedAuthoringSourceError(code)
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise NormalizedAuthoringSourceError(code) from exc


def load_verified_normalized_authoring_source(
    *,
    root: Path,
    provenance_path: Path,
    expected_source_kind: str,
) -> tuple[str, dict[str, Any]]:
    """Return a verified companion and bounded, text-free provenance evidence."""

    raw_provenance = provenance_path.read_bytes()
    if not raw_provenance or len(raw_provenance) > MAX_PROVENANCE_BYTES:
        raise NormalizedAuthoringSourceError("normalized_source_provenance_size_invalid")
    try:
        provenance_value = json.loads(raw_provenance.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NormalizedAuthoringSourceError("normalized_source_provenance_json_invalid") from exc

    provenance = _exact_mapping(
        provenance_value,
        {
            "contract_version",
            "source_kind",
            "original_source",
            "normalized_companion",
            "normalization",
        },
        "normalized_source_provenance_contract_invalid",
    )
    if provenance["contract_version"] != PROVENANCE_VERSION:
        raise NormalizedAuthoringSourceError("normalized_source_provenance_contract_invalid")
    if provenance["source_kind"] != expected_source_kind:
        raise NormalizedAuthoringSourceError("normalized_source_kind_mismatch")
    source_policy = _SOURCE_POLICIES.get(expected_source_kind)
    if source_policy is None:
        raise NormalizedAuthoringSourceError("normalized_source_kind_unsupported")

    original = _exact_mapping(
        provenance["original_source"],
        {"path", "encoding", "content_sha256"},
        "normalized_source_original_pin_invalid",
    )
    companion = _exact_mapping(
        provenance["normalized_companion"],
        {
            "path",
            "encoding",
            "content_sha256",
            "source_manifest_contract_version",
            "source_manifest_source_sha256",
            "source_manifest_sha256",
        },
        "normalized_source_companion_pin_invalid",
    )
    normalization = _exact_mapping(
        provenance["normalization"],
        {"method", "facts_only", "executable_content_allowed", "secrets_allowed"},
        "normalized_source_policy_invalid",
    )
    if original["encoding"] != "utf-8" or companion["encoding"] != "utf-8":
        raise NormalizedAuthoringSourceError("normalized_source_policy_invalid")
    if normalization != {
        "method": source_policy["method"],
        "facts_only": True,
        "executable_content_allowed": False,
        "secrets_allowed": False,
    }:
        raise NormalizedAuthoringSourceError("normalized_source_policy_invalid")

    original_sha256 = _sha256_value(
        original["content_sha256"], "normalized_source_original_pin_invalid"
    )
    companion_sha256 = _sha256_value(
        companion["content_sha256"], "normalized_source_companion_pin_invalid"
    )
    original_path = _verified_path(root, original["path"], "normalized_source_original_path_invalid")
    companion_path = _verified_path(root, companion["path"], "normalized_source_companion_path_invalid")
    _verified_utf8(original_path, original_sha256, "normalized_source_original_hash_mismatch")
    companion_text = _verified_utf8(
        companion_path,
        companion_sha256,
        "normalized_source_companion_hash_mismatch",
    )
    if any(pattern.search(companion_text) for pattern in _FORBIDDEN_COMPANION_PATTERNS):
        raise NormalizedAuthoringSourceError("normalized_source_companion_content_forbidden")

    manifest = extract_authoring_source_manifest(companion_text)
    counts = manifest.get("counts") if isinstance(manifest, Mapping) else None
    common_manifest_valid = (
        companion["source_manifest_contract_version"] == MANIFEST_VERSION
        and companion["source_manifest_source_sha256"]
        == _sha256_value(
            companion["source_manifest_source_sha256"],
            "normalized_source_companion_manifest_pin_invalid",
        )
        and companion["source_manifest_sha256"]
        == _sha256_value(
            companion["source_manifest_sha256"],
            "normalized_source_companion_manifest_pin_invalid",
        )
        and manifest.get("contract_version") == companion["source_manifest_contract_version"]
        and manifest.get("source_sha256") == companion["source_manifest_source_sha256"]
        and manifest.get("manifest_sha256") == companion["source_manifest_sha256"]
        and manifest.get("required_sections") == source_policy["required_sections"]
        and isinstance(counts, Mapping)
    )
    inventory_valid = False
    if common_manifest_valid and source_policy["inventory_mode"] == "aliases_only":
        inventory_valid = (
            int(counts.get("aliases") or 0) >= 1
            and int(counts.get("alias_bindings") or 0) == int(counts.get("aliases") or 0)
            and all(int(counts.get(kind) or 0) == 0 for kind in _NON_ALIAS_INVENTORIES)
        )
    elif common_manifest_valid and source_policy["inventory_mode"] == "empty":
        inventory_valid = all(int(counts.get(kind) or 0) == 0 for kind in _ALL_INVENTORIES)
    elif common_manifest_valid and source_policy["inventory_mode"] == "datasets_and_fields":
        dataset_count = int(counts.get("datasets") or 0)
        field_count = int(counts.get("fields") or 0)
        field_bindings = int(counts.get("field_bindings") or 0)
        inventory_valid = (
            dataset_count >= 1
            and field_count >= 1
            and field_bindings >= field_count
            and all(
                int(counts.get(kind) or 0) == 0
                for kind in _ALL_INVENTORIES
                if kind not in _DATASET_INVENTORIES
            )
        )
    if not common_manifest_valid or not inventory_valid:
        raise NormalizedAuthoringSourceError("normalized_source_companion_manifest_mismatch")

    evidence = {
        "contract_version": PROVENANCE_VERSION,
        "source_kind": expected_source_kind,
        "original_content_sha256": original_sha256,
        "normalized_content_sha256": companion_sha256,
        "source_manifest_sha256": manifest["manifest_sha256"],
        "required_sections": list(source_policy["required_sections"]),
        "dataset_count": int(counts["datasets"]),
        "field_count": int(counts["fields"]),
        "field_bindings": int(counts["field_bindings"]),
        "alias_bindings": int(counts["alias_bindings"]),
        "source_text_persisted": False,
    }
    return companion_text, evidence


__all__ = [
    "NormalizedAuthoringSourceError",
    "PROVENANCE_VERSION",
    "load_verified_normalized_authoring_source",
]
