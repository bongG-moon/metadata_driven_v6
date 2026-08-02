from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = (
    PROJECT_ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "approved_source_registry.json"
)
DEFAULT_CATALOG_PATH = (
    PROJECT_ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "compiled"
    / "runtime_catalog.v2.json"
)
DEFAULT_EXCLUSIONS_PATH = (
    PROJECT_ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "source_registry_exclusions.json"
)
DEFAULT_BLUEPRINT_PATH = (
    PROJECT_ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "trusted_executable_blueprint.json"
)

REGISTRY_V1 = "metadata.authoring.source-registry.v1"
REGISTRY_V2 = "metadata.authoring.source-registry.v2"
REGISTRY_V3 = "metadata.authoring.source-registry.v3"
SEMANTIC_VOCABULARY_V1 = "metadata.authoring.semantic-vocabulary.v1"
SEMANTIC_TEMPLATES_V1 = "metadata.authoring.semantic-templates.v1"
EXECUTABLE_BLUEPRINT_V1 = "metadata.executable-blueprint.v1"
RUNTIME_CATALOG_V2 = "metadata.runtime.catalog.v2"
EXCLUSIONS_V1 = "metadata.authoring.source-registry-exclusions.v1"
BINDING_KEYS = ("source_type", "source_adapter", "config_ref", "query_ref")
DATASET_TEMPLATE_KEYS = (
    "date_filter_contract",
    "date_policy",
    "default_detail_fields",
    "display_name",
    "fixture_only",
    "parameters",
    "read_policy",
    "time_scope",
    "upstream_bindings",
)
REQUIRED_DATASET_TEMPLATE_KEYS = (
    "date_policy",
    "default_detail_fields",
    "display_name",
    "parameters",
    "read_policy",
    "time_scope",
)
_DATASET_TEMPLATE_EXCLUDED_KEYS = {
    "fields",
    "family",
    *BINDING_KEYS,
}
_RUNTIME_DATASET_IDENTITY_KEYS = {"key"}
_SOURCE_DATASET_DERIVED_KEYS = {
    "family",
    "field_descriptors",
    "proposal_exclusions",
}
_SOURCE_DATASET_TEMPLATE_KEYS = {"dataset_template", "dataset_template_sha256"}
REQUIRED_DESCRIPTOR_KEYS = ("physical_column", "semantic_type", "roles")
OPTIONAL_DESCRIPTOR_KEYS = (
    "physical_aliases",
    "coercion",
    "nullable",
    "required_in_source",
    "timezone",
)

_DOMAIN_ID = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
_CATALOG_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
_ROLE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_EXCLUSION_REASONS = {
    "source_projection_not_registered",
    "source_expression_before_alias",
    "legacy_source_name",
}
_ALIAS_CARD_KEYS = {
    "conflict",
    "match",
    "normalization",
    "provenance_source",
    "target_key",
    "target_type",
    "values",
}
_ALIAS_VALUE_KEYS = {"priority", "text"}
_VOCABULARY_KINDS = ("dataset", "field", "metric")
_LABEL_FORBIDDEN_FRAGMENTS = (
    "http://",
    "https://",
    "mongodb://",
    "mongodb+srv://",
    "config:",
    "query:",
    "password",
    "secret",
    "token=",
    "api_key",
)
_MAX_ALIAS_CARDS = 8192
_MAX_LABELS_PER_CARD = 128
_MAX_LABELS_PER_ENTITY = 256
_MAX_LABEL_CHARACTERS = 256
_MAX_LABEL_UTF8_BYTES = 1024
_MAX_FAMILIES_PER_FIELD = 128
_MAX_SEMANTIC_VOCABULARY_UTF8_BYTES = 64 * 1024
_MAX_SEMANTIC_TEMPLATES_UTF8_BYTES = 128 * 1024
_MAX_DATASET_TEMPLATE_UTF8_BYTES = 32 * 1024
_MAX_ALL_DATASET_TEMPLATES_UTF8_BYTES = 64 * 1024
_MAX_TEMPLATE_DEPTH = 24
_MAX_TEMPLATE_COLLECTION_ITEMS = 8192
_MAX_TEMPLATE_TEXT_CHARACTERS = 4096
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_BLUEPRINT_ROOT_KEYS = {
    "blueprint_sha256",
    "contract_version",
    "default_annotations",
    "domain_id",
    "environment",
    "executable",
    "executable_sha256",
    "source_manifest_sha256",
}
_BLUEPRINT_EXECUTABLE_KEYS = {
    "aliases",
    "contract_version",
    "datasets",
    "entity_groups",
    "grains",
    "locale",
    "metrics",
    "orderings",
    "output_profile",
    "predicates",
    "prompt_extensions",
    "recipes",
    "relations",
    "source_provenance",
    "specialized_functions",
    "timezone",
}
_LEGACY_ALIAS_TARGET_TYPES = {
    "dataset",
    "field",
    "metric",
    "process_group",
    "process",
    "product_group",
    "recipe",
    "status",
}
_GENERIC_ALIAS_TARGET_TYPES = {
    "dataset",
    "field",
    "metric",
    "relation",
    "grain",
    "predicate",
    "recipe",
    "entity_group",
}
_LEGACY_RECIPE_OPERATIONS = {
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
    "transform_previous_result",
}
_GENERIC_RECIPE_OPERATIONS = {
    "filter",
    "project",
    "aggregate",
    "join",
    "derive",
    "compare_fields",
    "sort",
    "rank",
    "transform_previous_result",
}

_TEMPLATE_SECTION_SPECS = {
    "metrics": (
        "metric_id",
        {
            "additivity",
            "aggregation",
            "aliases",
            "dependencies",
            "formula",
            "metric_id",
            "null_policy",
            "source_binding",
            "source_field",
            "temporal_contract",
            "unit",
            "value_type",
            "zero_policy",
        },
        1024,
    ),
    "relations": (
        "relation_id",
        {
            "aliases",
            "cardinality",
            "join_type",
            "key_mappings",
            "left_dataset",
            "left_keys",
            "multi_match_policy",
            "null_key_policy",
            "relation_id",
            "right_dataset",
            "right_keys",
        },
        2048,
    ),
    "entity_groups": (
        "group_id",
        {
            "alias_policy",
            "aliases",
            "display_name",
            "entity",
            "expansion",
            "group_id",
            "legacy_identity",
            "members",
            "selection",
            "target_field",
        },
        2048,
    ),
    "grains": (
        "grain_id",
        {"display_fields", "grain_id", "keys"},
        2048,
    ),
    "orderings": (
        "ordering_id",
        {"items", "keys", "ordering_id"},
        2048,
    ),
    "predicates": (
        "predicate_id",
        {
            "aliases",
            "allowed_operators",
            "grain_id",
            "group_id",
            "predicate",
            "predicate_id",
        },
        2048,
    ),
    "recipes": (
        "recipe_id",
        {
            "aliases",
            "datasets",
            "default_operation_template",
            "derived_metrics",
            "grain",
            "metrics",
            "recipe_id",
            "required_fields",
            "required_slots",
        },
        2048,
    ),
}
_TEMPLATE_FORBIDDEN_KEYS = {
    "code",
    "coercion",
    "config_ref",
    "credential",
    "credentials",
    "physical_column",
    "python",
    "query_ref",
    "script",
    "source_adapter",
    "source_type",
    "sql",
}
_TEMPLATE_FORBIDDEN_VALUE_PATTERNS = (
    re.compile(r"(?:https?|mongodb(?:\+srv)?|jdbc)://", re.IGNORECASE),
    re.compile(r"\b(?:select\s+.+\s+from|insert\s+into|delete\s+from|update\s+.+\s+set)\b", re.IGNORECASE),
    re.compile(r"\b(?:import\s+[A-Za-z_]|from\s+[A-Za-z_][A-Za-z0-9_.]*\s+import|def\s+[A-Za-z_]\w*\s*\(|lambda\s+)"),
)


class RegistryBuildError(RuntimeError):
    """Raised when the trusted registry cannot be rebuilt safely."""


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RegistryBuildError(f"{label} file is required")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise RegistryBuildError(f"{label} must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise RegistryBuildError(f"{label} must be valid JSON") from exc
    if not isinstance(value, dict):
        raise RegistryBuildError(f"{label} must be a JSON object")
    return value


def _safe_id(value: Any, *, domain: bool = False) -> str:
    if not isinstance(value, str):
        raise RegistryBuildError("registry contains an unsafe identifier")
    pattern = _DOMAIN_ID if domain else _CATALOG_ID
    if pattern.fullmatch(value) is None:
        raise RegistryBuildError("registry contains an unsafe identifier")
    return value


def _nonempty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or any(ord(char) < 32 for char in value):
        raise RegistryBuildError(f"{label} must be a non-empty safe string")
    return value


def _normalized_name(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def _safe_label(value: Any, label: str) -> str:
    text = re.sub(r"\s+", " ", _nonempty_text(value, label).strip())
    folded = text.casefold()
    if (
        len(text) > _MAX_LABEL_CHARACTERS
        or len(text.encode("utf-8")) > _MAX_LABEL_UTF8_BYTES
        or any(fragment in folded for fragment in _LABEL_FORBIDDEN_FRAGMENTS)
    ):
        raise RegistryBuildError(f"{label} contains an unsafe or oversized value")
    return text


def _deduplicated_labels(candidates: list[str]) -> list[str]:
    labels: list[str] = []
    seen: set[str] = set()
    for candidate in sorted(candidates, key=lambda item: (_normalized_name(item), item)):
        normalized = _normalized_name(candidate)
        if normalized in seen:
            continue
        seen.add(normalized)
        labels.append(candidate)
    if len(labels) > _MAX_LABELS_PER_ENTITY:
        raise RegistryBuildError("semantic vocabulary labels per entity must be bounded")
    return labels


def _alias_labels(
    aliases: dict[str, Any],
    *,
    target_type: str,
    target_id: str,
) -> list[str]:
    alias_key = f"{target_type}:{target_id}"
    card = aliases.get(alias_key)
    if not isinstance(card, dict) or set(card) != _ALIAS_CARD_KEYS:
        raise RegistryBuildError("runtime catalog semantic alias card is missing or open")
    if card.get("target_type") != target_type or card.get("target_key") != target_id:
        raise RegistryBuildError("runtime catalog semantic alias identity mismatch")

    for key in ("conflict", "match", "provenance_source"):
        value = _nonempty_text(card.get(key), f"semantic alias {key}")
        if len(value) > 128:
            raise RegistryBuildError("runtime catalog semantic alias policy is oversized")
    normalization = card.get("normalization")
    if (
        not isinstance(normalization, list)
        or not 1 <= len(normalization) <= 16
        or len(normalization) != len(set(normalization))
        or any(
            not isinstance(item, str)
            or not item
            or len(item) > 64
            or _ROLE.fullmatch(item) is None
            for item in normalization
        )
    ):
        raise RegistryBuildError("runtime catalog semantic alias normalization is invalid")

    values = card.get("values")
    if not isinstance(values, list) or not 1 <= len(values) <= _MAX_LABELS_PER_CARD:
        raise RegistryBuildError("runtime catalog semantic alias labels must be bounded")
    candidates: list[str] = []
    for value in values:
        if not isinstance(value, dict) or set(value) != _ALIAS_VALUE_KEYS:
            raise RegistryBuildError("runtime catalog semantic alias label card is open")
        priority = value.get("priority")
        if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 1_000_000:
            raise RegistryBuildError("runtime catalog semantic alias priority is invalid")
        candidates.append(_safe_label(value.get("text"), "semantic alias label"))

    labels = _deduplicated_labels(candidates)
    if not labels:
        raise RegistryBuildError("runtime catalog semantic alias labels must be non-empty")
    return labels


def _section_vocabulary_projection(
    runtime_catalog: dict[str, Any],
    aliases: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    section_specs = {
        "relations": ("relation_id", ("relation",)),
        "grains": ("grain_id", ("grain",)),
        "orderings": ("ordering_id", ("ordering",)),
        "predicates": ("predicate_id", ("predicate", "product_group")),
        "recipes": ("recipe_id", ("recipe",)),
        "entity_groups": ("group_id", ("entity_group", "process_group")),
    }
    projected: dict[str, list[dict[str, Any]]] = {}
    alias_type_owners: dict[str, str] = {
        alias_type: section
        for section, (_, alias_types) in section_specs.items()
        for alias_type in alias_types
    }
    section_ids: dict[str, set[str]] = {}

    for section, (identity_key, _) in section_specs.items():
        raw_section = runtime_catalog.get(section)
        if not isinstance(raw_section, dict) or len(raw_section) > 2048:
            raise RegistryBuildError(f"runtime catalog {section} must be a bounded object")
        ids: set[str] = set()
        for raw_key, card in raw_section.items():
            entry_id = _safe_id(raw_key)
            if (
                not isinstance(card, dict)
                or card.get(identity_key) != entry_id
                or entry_id in ids
            ):
                raise RegistryBuildError(f"runtime catalog {section} identity mismatch")
            ids.add(entry_id)
        section_ids[section] = ids

    optional_aliases: dict[str, dict[str, list[str]]] = {
        section: {entry_id: [] for entry_id in ids}
        for section, ids in section_ids.items()
    }
    for alias_key, card in aliases.items():
        if not isinstance(card, dict):
            continue
        target_type = card.get("target_type")
        section = alias_type_owners.get(target_type)
        if section is None:
            continue
        target_id = _safe_id(card.get("target_key"))
        if target_id not in section_ids[section]:
            raise RegistryBuildError(
                "runtime catalog semantic alias targets an unknown section identifier"
            )
        if alias_key != f"{target_type}:{target_id}":
            raise RegistryBuildError("runtime catalog semantic section alias key mismatch")
        optional_aliases[section][target_id].extend(
            _alias_labels(
                aliases,
                target_type=target_type,
                target_id=target_id,
            )
        )

    for section, (identity_key, _) in section_specs.items():
        entries: list[dict[str, Any]] = []
        label_owners: dict[str, str] = {}
        raw_section = runtime_catalog[section]
        for entry_id in sorted(section_ids[section]):
            card = raw_section[entry_id]
            raw_card_aliases = card.get("aliases", [])
            if (
                not isinstance(raw_card_aliases, list)
                or len(raw_card_aliases) > _MAX_LABELS_PER_CARD
            ):
                raise RegistryBuildError(f"runtime catalog {section} card aliases must be bounded")
            candidates = list(optional_aliases[section][entry_id])
            candidates.extend(
                _safe_label(value, f"{section} card alias")
                for value in raw_card_aliases
            )
            if not candidates:
                candidates.append(entry_id)
            labels = _deduplicated_labels(candidates)
            for label in labels:
                normalized = _normalized_name(label)
                owner = label_owners.setdefault(normalized, entry_id)
                if owner != entry_id:
                    raise RegistryBuildError(
                        f"runtime catalog {section} alias is ambiguous"
                    )
            entries.append({"id": entry_id, "labels": labels})
        projected[section] = entries
    return projected


def _semantic_vocabulary_projection(
    runtime_catalog: dict[str, Any],
    approved_datasets: dict[str, Any],
) -> dict[str, Any]:
    aliases = runtime_catalog.get("aliases")
    catalog_datasets = runtime_catalog.get("datasets")
    catalog_fields = runtime_catalog.get("fields")
    catalog_metrics = runtime_catalog.get("metrics")
    if not isinstance(aliases, dict) or not 1 <= len(aliases) <= _MAX_ALIAS_CARDS:
        raise RegistryBuildError("runtime catalog aliases must be a bounded object")
    if not isinstance(catalog_datasets, dict) or not 1 <= len(catalog_datasets) <= 128:
        raise RegistryBuildError("runtime catalog vocabulary datasets must be bounded")
    if not isinstance(catalog_fields, dict) or not 1 <= len(catalog_fields) <= 2048:
        raise RegistryBuildError("runtime catalog vocabulary fields must be bounded")
    if not isinstance(catalog_metrics, dict) or not 1 <= len(catalog_metrics) <= 1024:
        raise RegistryBuildError("runtime catalog vocabulary metrics must be bounded")

    catalog_dataset_families: dict[str, str] = {}
    catalog_field_families: dict[str, set[str]] = {}
    for raw_dataset_id in sorted(catalog_datasets):
        dataset_id = _safe_id(raw_dataset_id)
        dataset = catalog_datasets[raw_dataset_id]
        if not isinstance(dataset, dict) or dataset.get("key") != dataset_id:
            raise RegistryBuildError("runtime catalog vocabulary dataset identity mismatch")
        family = _safe_id(dataset.get("family"))
        fields = dataset.get("fields")
        if not isinstance(fields, dict) or not 1 <= len(fields) <= 2048:
            raise RegistryBuildError("runtime catalog vocabulary dataset fields must be bounded")
        catalog_dataset_families[dataset_id] = family
        for raw_field_id in fields:
            field_id = _safe_id(raw_field_id)
            catalog_field_families.setdefault(field_id, set()).add(family)

    global_field_ids = {_safe_id(field_id) for field_id in catalog_fields}
    if (
        global_field_ids != set(catalog_field_families)
        or len(global_field_ids) != len(catalog_fields)
    ):
        raise RegistryBuildError("runtime catalog global fields do not match dataset fields")

    if not isinstance(approved_datasets, dict) or set(approved_datasets) != set(
        catalog_dataset_families
    ):
        raise RegistryBuildError("approved dataset vocabulary inventory is invalid")
    dataset_families: dict[str, str] = {}
    field_families: dict[str, set[str]] = {}
    for dataset_id in sorted(approved_datasets):
        dataset = approved_datasets[dataset_id]
        if not isinstance(dataset, dict):
            raise RegistryBuildError("approved dataset vocabulary card must be an object")
        family = _safe_id(dataset.get("family"))
        if family != catalog_dataset_families[dataset_id]:
            raise RegistryBuildError("approved dataset family is incompatible with runtime catalog")
        descriptors = dataset.get("field_descriptors")
        if not isinstance(descriptors, dict) or not 1 <= len(descriptors) <= 2048:
            raise RegistryBuildError("approved dataset field descriptors must be bounded")
        dataset_families[dataset_id] = family
        for raw_field_id in descriptors:
            field_id = _safe_id(raw_field_id)
            if field_id not in global_field_ids:
                raise RegistryBuildError("approved field is absent from runtime catalog")
            field_families.setdefault(field_id, set()).add(family)
    metric_ids = {_safe_id(metric_id) for metric_id in catalog_metrics}
    if len(metric_ids) != len(catalog_metrics):
        raise RegistryBuildError("runtime catalog metric identifiers are not unique")
    for metric_id in metric_ids:
        metric = catalog_metrics[metric_id]
        if not isinstance(metric, dict) or metric.get("metric_id") != metric_id:
            raise RegistryBuildError("runtime catalog metric identity mismatch")

    expected_by_kind = {
        "dataset": set(dataset_families),
        "field": set(field_families),
        "metric": metric_ids,
    }
    selected_aliases: dict[str, set[str]] = {kind: set() for kind in _VOCABULARY_KINDS}
    for alias_key, card in aliases.items():
        if not isinstance(alias_key, str) or not isinstance(card, dict):
            raise RegistryBuildError("runtime catalog semantic alias entry is invalid")
        target_type = card.get("target_type")
        if target_type not in selected_aliases:
            continue
        target_id = _safe_id(card.get("target_key"))
        if alias_key != f"{target_type}:{target_id}":
            raise RegistryBuildError("runtime catalog semantic alias key mismatch")
        if target_id not in expected_by_kind[target_type]:
            raise RegistryBuildError("runtime catalog semantic alias targets an unknown identifier")
        if target_id in selected_aliases[target_type]:
            raise RegistryBuildError("runtime catalog semantic alias target is duplicated")
        selected_aliases[target_type].add(target_id)
    if any(selected_aliases[kind] != expected_by_kind[kind] for kind in _VOCABULARY_KINDS):
        raise RegistryBuildError("runtime catalog semantic aliases are incomplete")

    labels_by_kind: dict[str, dict[str, list[str]]] = {
        kind: {
            target_id: _alias_labels(
                aliases,
                target_type=kind,
                target_id=target_id,
            )
            for target_id in sorted(expected_by_kind[kind])
        }
        for kind in _VOCABULARY_KINDS
    }
    for kind in _VOCABULARY_KINDS:
        label_owners: dict[str, str] = {}
        for target_id, labels in labels_by_kind[kind].items():
            for label in labels:
                normalized = _normalized_name(label)
                owner = label_owners.setdefault(normalized, target_id)
                if owner != target_id:
                    raise RegistryBuildError(
                        "runtime catalog semantic alias is ambiguous within its vocabulary kind"
                    )

    section_vocabulary = _section_vocabulary_projection(runtime_catalog, aliases)
    vocabulary = {
        "contract_version": SEMANTIC_VOCABULARY_V1,
        "datasets": [
            {
                "id": dataset_id,
                "family": dataset_families[dataset_id],
                "labels": labels_by_kind["dataset"][dataset_id],
            }
            for dataset_id in sorted(dataset_families)
        ],
        "fields": [
            {
                "id": field_id,
                "families": sorted(field_families[field_id]),
                "labels": labels_by_kind["field"][field_id],
            }
            for field_id in sorted(field_families)
        ],
        "metrics": [
            {
                "id": metric_id,
                "labels": labels_by_kind["metric"][metric_id],
            }
            for metric_id in sorted(metric_ids)
        ],
        **section_vocabulary,
    }
    if any(
        not 1 <= len(item["families"]) <= _MAX_FAMILIES_PER_FIELD
        for item in vocabulary["fields"]
    ):
        raise RegistryBuildError("semantic vocabulary field families must be bounded")
    vocabulary_bytes = json.dumps(
        vocabulary,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    if len(vocabulary_bytes) > _MAX_SEMANTIC_VOCABULARY_UTF8_BYTES:
        raise RegistryBuildError("semantic vocabulary exceeds the UTF-8 byte limit")
    return vocabulary


def _safe_template_payload(value: Any, *, path: str, depth: int = 0) -> Any:
    """Copy a compiler-only semantic value while rejecting executable/secret payloads."""

    if depth > _MAX_TEMPLATE_DEPTH:
        raise RegistryBuildError("semantic templates exceed the nesting depth limit")
    if isinstance(value, dict):
        if len(value) > _MAX_TEMPLATE_COLLECTION_ITEMS:
            raise RegistryBuildError("semantic template object exceeds the item limit")
        projected: dict[str, Any] = {}
        for raw_key in sorted(value):
            key = _nonempty_text(raw_key, f"{path} key")
            if len(key) > 256 or key.casefold() in _TEMPLATE_FORBIDDEN_KEYS:
                raise RegistryBuildError("semantic templates contain a forbidden payload key")
            projected[key] = _safe_template_payload(
                value[raw_key],
                path=f"{path}.{key}",
                depth=depth + 1,
            )
        return projected
    if isinstance(value, list):
        if len(value) > _MAX_TEMPLATE_COLLECTION_ITEMS:
            raise RegistryBuildError("semantic template list exceeds the item limit")
        return [
            _safe_template_payload(item, path=f"{path}[]", depth=depth + 1)
            for item in value
        ]
    if isinstance(value, str):
        text = _nonempty_text(value, path)
        if len(text) > _MAX_TEMPLATE_TEXT_CHARACTERS or any(
            pattern.search(text) for pattern in _TEMPLATE_FORBIDDEN_VALUE_PATTERNS
        ):
            raise RegistryBuildError("semantic templates contain executable or URL payload text")
        return text
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise RegistryBuildError("semantic templates contain an unsupported JSON value")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _trusted_blueprint_executable(
    trusted_blueprint: dict[str, Any],
    *,
    domain_id: str,
) -> tuple[dict[str, Any], str, str]:
    if set(trusted_blueprint) != _BLUEPRINT_ROOT_KEYS:
        raise RegistryBuildError("trusted executable blueprint root contract is open or invalid")
    if (
        trusted_blueprint.get("contract_version") != EXECUTABLE_BLUEPRINT_V1
        or trusted_blueprint.get("domain_id") != domain_id
    ):
        raise RegistryBuildError("trusted executable blueprint identity mismatch")
    executable = trusted_blueprint.get("executable")
    if not isinstance(executable, dict) or set(executable) != _BLUEPRINT_EXECUTABLE_KEYS:
        raise RegistryBuildError("trusted executable blueprint payload contract is open or invalid")
    declared_executable_sha256 = trusted_blueprint.get("executable_sha256")
    declared_blueprint_sha256 = trusted_blueprint.get("blueprint_sha256")
    if (
        not isinstance(declared_executable_sha256, str)
        or _SHA256.fullmatch(declared_executable_sha256) is None
        or not isinstance(declared_blueprint_sha256, str)
        or _SHA256.fullmatch(declared_blueprint_sha256) is None
    ):
        raise RegistryBuildError("trusted executable blueprint hash is invalid")
    actual_executable_sha256 = hashlib.sha256(_canonical_json_bytes(executable)).hexdigest()
    blueprint_material = {
        key: value
        for key, value in trusted_blueprint.items()
        if key != "blueprint_sha256"
    }
    actual_blueprint_sha256 = hashlib.sha256(
        _canonical_json_bytes(blueprint_material)
    ).hexdigest()
    if declared_executable_sha256 != actual_executable_sha256:
        raise RegistryBuildError("trusted executable blueprint executable hash mismatch")
    if declared_blueprint_sha256 != actual_blueprint_sha256:
        raise RegistryBuildError("trusted executable blueprint self hash mismatch")
    return deepcopy(executable), declared_blueprint_sha256, declared_executable_sha256


def _semantic_template_sections(
    executable: dict[str, Any],
    runtime_catalog: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    projected: dict[str, dict[str, Any]] = {}
    for section, (identity_key, allowed_keys, max_items) in _TEMPLATE_SECTION_SPECS.items():
        blueprint_section = executable.get(section)
        catalog_section = runtime_catalog.get(section)
        if (
            not isinstance(blueprint_section, dict)
            or not isinstance(catalog_section, dict)
            or len(blueprint_section) > max_items
            or set(blueprint_section) != set(catalog_section)
        ):
            raise RegistryBuildError(f"runtime catalog {section} templates must be a bounded object")
        if section == "metrics" and not blueprint_section:
            raise RegistryBuildError("runtime catalog metric templates must be non-empty")
        normalized: dict[str, Any] = {}
        draft_allowed_keys = allowed_keys - {identity_key}
        for raw_id in sorted(blueprint_section):
            entry_id = _safe_id(raw_id)
            card = blueprint_section[raw_id]
            compiled_card = catalog_section[raw_id]
            if (
                not isinstance(card, dict)
                or not isinstance(compiled_card, dict)
                or identity_key in card
                or not set(card).issubset(draft_allowed_keys)
                or compiled_card.get(identity_key) != entry_id
                or not set(compiled_card).issubset(allowed_keys)
            ):
                raise RegistryBuildError(f"runtime catalog {section} template card is open or invalid")
            safe_blueprint_card = _safe_template_payload(
                card,
                path=f"semantic_templates.{section}.{entry_id}",
            )
            compiled_without_identity = {
                key: value
                for key, value in compiled_card.items()
                if key != identity_key
            }
            safe_compiled_card = _safe_template_payload(
                compiled_without_identity,
                path=f"runtime_catalog.{section}.{entry_id}",
            )
            if safe_compiled_card != safe_blueprint_card:
                raise RegistryBuildError(
                    f"trusted blueprint and runtime catalog {section} template mismatch"
                )
            normalized[entry_id] = safe_blueprint_card
        projected[section] = normalized
    return projected


def _validate_metric_template_bindings(
    metrics: dict[str, Any],
    vocabulary: dict[str, Any],
) -> None:
    registered_families = {item["family"] for item in vocabulary["datasets"]}
    field_families = {
        item["id"]: set(item["families"])
        for item in vocabulary["fields"]
    }
    for metric_id, metric in metrics.items():
        binding = metric.get("source_binding")
        if binding is None:
            continue
        if not isinstance(binding, dict):
            raise RegistryBuildError("semantic metric source binding must be an object")
        permitted = {"dataset_family", "field", "fixed_filters"}
        if (
            not {"dataset_family", "field"}.issubset(binding)
            or not set(binding).issubset(permitted)
        ):
            raise RegistryBuildError("semantic metric source binding is open or incomplete")
        family = _safe_id(binding["dataset_family"])
        field_id = _safe_id(binding["field"])
        if family not in registered_families or family not in field_families.get(field_id, set()):
            raise RegistryBuildError("semantic metric source binding is not registered")
        fixed_filters = binding.get("fixed_filters", [])
        if not isinstance(fixed_filters, list) or len(fixed_filters) > 64:
            raise RegistryBuildError("semantic metric fixed filters must be bounded")
        for fixed_filter in fixed_filters:
            if (
                not isinstance(fixed_filter, dict)
                or set(fixed_filter) != {"field", "operator", "semantic_type", "value"}
            ):
                raise RegistryBuildError("semantic metric fixed filter is open or invalid")
            filter_field = _safe_id(fixed_filter["field"])
            if family not in field_families.get(filter_field, set()):
                raise RegistryBuildError("semantic metric fixed filter field is not registered")
            _nonempty_text(fixed_filter["operator"], "semantic metric fixed filter operator")
            _nonempty_text(
                fixed_filter["semantic_type"],
                "semantic metric fixed filter type",
            )


def _planner_policy_projection(
    executable: dict[str, Any],
    runtime_catalog: dict[str, Any],
) -> tuple[dict[str, str], list[str]]:
    blueprint_profile = executable.get("output_profile")
    runtime_profile = runtime_catalog.get("output_profile")
    if not isinstance(blueprint_profile, dict) or not isinstance(runtime_profile, dict):
        raise RegistryBuildError("planner output profile must be an object")
    planner_profile = str(blueprint_profile.get("planner_profile") or "generic_v2")
    if planner_profile == "legacy_v1_compat":
        legacy_pin = blueprint_profile.get("legacy_catalog_sha256")
        if not isinstance(legacy_pin, str) or _SHA256.fullmatch(legacy_pin) is None:
            raise RegistryBuildError("legacy planner policy hash pin is invalid")
        policy = {
            "legacy_catalog_sha256": legacy_pin,
            "planner_profile": planner_profile,
        }
    elif planner_profile == "generic_v2":
        policy = {"planner_profile": planner_profile}
    else:
        raise RegistryBuildError("semantic template planner profile is unsupported")
    runtime_policy = {
        key: runtime_profile.get(key)
        for key in policy
    }
    if runtime_policy != policy:
        raise RegistryBuildError("trusted blueprint and runtime planner policy mismatch")
    excluded_keys = sorted(set(blueprint_profile) - set(policy))
    return policy, excluded_keys


def _recipe_operations(value: Any) -> set[str]:
    operations: set[str] = set()
    if isinstance(value, dict):
        operation = value.get("op")
        if isinstance(operation, str) and operation:
            operations.add(operation)
        for child in value.values():
            operations.update(_recipe_operations(child))
    elif isinstance(value, list):
        for child in value:
            operations.update(_recipe_operations(child))
    return operations


def _validate_template_recipe_operations(
    recipes: dict[str, Any],
    *,
    planner_profile: str,
) -> None:
    allowed = (
        _LEGACY_RECIPE_OPERATIONS
        if planner_profile == "legacy_v1_compat"
        else _GENERIC_RECIPE_OPERATIONS
    )
    for recipe_id, recipe in recipes.items():
        operations = _recipe_operations(recipe.get("default_operation_template"))
        if not operations <= allowed:
            raise RegistryBuildError(
                f"semantic template recipe operation is incompatible with {planner_profile}"
            )


def _semantic_template_aliases(
    executable: dict[str, Any],
    runtime_catalog: dict[str, Any],
    vocabulary: dict[str, Any],
    sections: dict[str, dict[str, Any]],
    *,
    planner_profile: str,
) -> dict[str, Any]:
    raw_aliases = executable.get("aliases")
    compiled_aliases = runtime_catalog.get("aliases")
    if (
        not isinstance(raw_aliases, dict)
        or not isinstance(compiled_aliases, dict)
        or not 1 <= len(raw_aliases) <= _MAX_ALIAS_CARDS
        or raw_aliases != compiled_aliases
    ):
        raise RegistryBuildError("runtime catalog template aliases must be a bounded object")

    vocabulary_targets = {
        "dataset": {item["id"] for item in vocabulary["datasets"]},
        "field": {item["id"] for item in vocabulary["fields"]},
        "metric": set(sections["metrics"]),
        "relation": set(sections["relations"]),
        "grain": set(sections["grains"]),
        "ordering": set(sections["orderings"]),
        "predicate": set(sections["predicates"]),
        "recipe": set(sections["recipes"]),
        "entity_group": set(sections["entity_groups"]),
        "process_group": set(sections["entity_groups"]),
        "product_group": set(sections["predicates"]),
    }
    process_targets: set[str] = set()
    for ordering in sections["orderings"].values():
        for item in ordering.get("items", []):
            if isinstance(item, dict) and isinstance(item.get("oper_name"), str):
                process_targets.add(item["oper_name"])
    vocabulary_targets["process"] = process_targets

    aliases: dict[str, Any] = {}
    for alias_key in sorted(raw_aliases):
        card = raw_aliases[alias_key]
        compiled_card = compiled_aliases[alias_key]
        if (
            not isinstance(card, dict)
            or not isinstance(compiled_card, dict)
            or set(card) != _ALIAS_CARD_KEYS
            or set(compiled_card) != _ALIAS_CARD_KEYS
        ):
            raise RegistryBuildError("runtime catalog semantic template alias card is open")
        target_type = _nonempty_text(card.get("target_type"), "semantic template alias type")
        target_key = _nonempty_text(card.get("target_key"), "semantic template alias target")
        if alias_key != f"{target_type}:{target_key}":
            raise RegistryBuildError("runtime catalog semantic template alias identity mismatch")
        _alias_labels(
            raw_aliases,
            target_type=target_type,
            target_id=target_key,
        )
        _alias_labels(
            compiled_aliases,
            target_type=target_type,
            target_id=target_key,
        )
        safe_card = _safe_template_payload(
            card,
            path=f"semantic_templates.aliases.{alias_key}",
        )
        safe_compiled_card = _safe_template_payload(
            compiled_card,
            path=f"runtime_catalog.aliases.{alias_key}",
        )
        allowed_target_types = (
            _LEGACY_ALIAS_TARGET_TYPES
            if planner_profile == "legacy_v1_compat"
            else _GENERIC_ALIAS_TARGET_TYPES
        )
        if target_type not in allowed_target_types:
            raise RegistryBuildError("semantic template alias type is not registered")
        # Legacy status values are sealed by the trusted blueprint and consumed
        # only by the compatibility planner. All other targets remain anchored
        # to a vocabulary/template registry.
        if target_type != "status" and target_key not in vocabulary_targets[target_type]:
            raise RegistryBuildError("semantic template alias target is not registered")
        if safe_compiled_card != safe_card:
            raise RegistryBuildError("trusted blueprint and runtime catalog alias template mismatch")
        aliases[alias_key] = safe_card
    return aliases


def _semantic_templates_projection(
    executable: dict[str, Any],
    runtime_catalog: dict[str, Any],
    vocabulary: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if (
        executable.get("locale") != runtime_catalog.get("locale")
        or executable.get("timezone") != runtime_catalog.get("timezone")
    ):
        raise RegistryBuildError("trusted blueprint and runtime catalog locale policy mismatch")
    locale = _safe_label(executable.get("locale"), "runtime catalog locale")
    timezone = _safe_label(executable.get("timezone"), "runtime catalog timezone")
    if len(locale) > 64 or len(timezone) > 128:
        raise RegistryBuildError("semantic template locale or timezone is oversized")
    sections = _semantic_template_sections(executable, runtime_catalog)
    _validate_metric_template_bindings(sections["metrics"], vocabulary)
    planner_policy, excluded_output_profile_keys = _planner_policy_projection(
        executable,
        runtime_catalog,
    )
    _validate_template_recipe_operations(
        sections["recipes"],
        planner_profile=planner_policy["planner_profile"],
    )
    templates = {
        "contract_version": SEMANTIC_TEMPLATES_V1,
        "locale": locale,
        "timezone": timezone,
        "planner_policy": planner_policy,
        **sections,
        "aliases": _semantic_template_aliases(
            executable,
            runtime_catalog,
            vocabulary,
            sections,
            planner_profile=planner_policy["planner_profile"],
        ),
    }
    payload = _canonical_json_bytes(templates)
    if len(payload) > _MAX_SEMANTIC_TEMPLATES_UTF8_BYTES:
        raise RegistryBuildError("semantic templates exceed the UTF-8 byte limit")
    projection_evidence = {
        "contract_version": "metadata.authoring.semantic-template-projection.v1",
        "identity_key_normalization": {
            section: identity_key
            for section, (identity_key, _, _) in sorted(_TEMPLATE_SECTION_SPECS.items())
        },
        "planner_profile": planner_policy["planner_profile"],
        "included_alias_count": len(templates["aliases"]),
        "excluded_alias_ids": [],
        "included_sections": sorted(_TEMPLATE_SECTION_SPECS),
        "output_profile_included_keys": sorted(planner_policy),
        "output_profile_excluded_keys": excluded_output_profile_keys,
    }
    return templates, projection_evidence


def _safe_dataset_template_payload(value: Any, *, path: str, depth: int = 0) -> Any:
    if depth > _MAX_TEMPLATE_DEPTH:
        raise RegistryBuildError("dataset template exceeds the nesting depth limit")
    if isinstance(value, dict):
        if len(value) > _MAX_TEMPLATE_COLLECTION_ITEMS:
            raise RegistryBuildError("dataset template object exceeds the item limit")
        projected: dict[str, Any] = {}
        for raw_key in sorted(value):
            key = _nonempty_text(raw_key, f"{path} key")
            if (
                len(key) > 256
                or key.casefold() in _TEMPLATE_FORBIDDEN_KEYS - {"coercion", "physical_column"}
                or key in _DATASET_TEMPLATE_EXCLUDED_KEYS
            ):
                raise RegistryBuildError("dataset template contains a forbidden payload key")
            projected[key] = _safe_dataset_template_payload(
                value[raw_key],
                path=f"{path}.{key}",
                depth=depth + 1,
            )
        return projected
    if isinstance(value, list):
        if len(value) > _MAX_TEMPLATE_COLLECTION_ITEMS:
            raise RegistryBuildError("dataset template list exceeds the item limit")
        return [
            _safe_dataset_template_payload(item, path=f"{path}[]", depth=depth + 1)
            for item in value
        ]
    if isinstance(value, str):
        text = _nonempty_text(value, path)
        if len(text) > _MAX_TEMPLATE_TEXT_CHARACTERS or any(
            pattern.search(text) for pattern in _TEMPLATE_FORBIDDEN_VALUE_PATTERNS
        ):
            raise RegistryBuildError("dataset template contains executable or URL payload text")
        return text
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise RegistryBuildError("dataset template contains an unsupported JSON value")


def _validate_source_dataset_card_shape(dataset: Any, *, source_version: str) -> None:
    if not isinstance(dataset, dict):
        raise RegistryBuildError("source registry dataset entry must be an object")
    binding_keys = set(BINDING_KEYS)
    base_keys = binding_keys | _SOURCE_DATASET_DERIVED_KEYS
    full_keys = base_keys | _SOURCE_DATASET_TEMPLATE_KEYS
    actual = set(dataset)
    allowed_shapes = (
        {frozenset(binding_keys)}
        if source_version == REGISTRY_V1
        else {frozenset(binding_keys), frozenset(base_keys)}
        if source_version == REGISTRY_V2
        else {frozenset(base_keys), frozenset(full_keys)}
    )
    if frozenset(actual) not in allowed_shapes:
        raise RegistryBuildError("source registry dataset card contract is open or invalid")


def _dataset_template_projection(
    *,
    dataset_id: str,
    blueprint_dataset: Any,
    runtime_dataset: Any,
    approved_field_ids: set[str],
) -> tuple[dict[str, Any], str]:
    if not isinstance(blueprint_dataset, dict) or not isinstance(runtime_dataset, dict):
        raise RegistryBuildError("dataset template source must be an object")
    blueprint_allowed = _DATASET_TEMPLATE_EXCLUDED_KEYS | set(DATASET_TEMPLATE_KEYS)
    runtime_allowed = blueprint_allowed | _RUNTIME_DATASET_IDENTITY_KEYS
    if (
        not set(REQUIRED_DATASET_TEMPLATE_KEYS).issubset(blueprint_dataset)
        or set(blueprint_dataset) - blueprint_allowed
        or set(runtime_dataset) - runtime_allowed
        or set(runtime_dataset) - _RUNTIME_DATASET_IDENTITY_KEYS != set(blueprint_dataset)
        or runtime_dataset.get("key") != dataset_id
    ):
        raise RegistryBuildError("dataset template source contract is open or inconsistent")

    blueprint_projection = {
        key: blueprint_dataset[key]
        for key in DATASET_TEMPLATE_KEYS
        if key in blueprint_dataset
    }
    runtime_projection = {
        key: runtime_dataset[key]
        for key in DATASET_TEMPLATE_KEYS
        if key in runtime_dataset
    }
    template = _safe_dataset_template_payload(
        blueprint_projection,
        path=f"datasets.{dataset_id}.dataset_template",
    )
    compiled_template = _safe_dataset_template_payload(
        runtime_projection,
        path=f"runtime_catalog.datasets.{dataset_id}.dataset_template",
    )
    if compiled_template != template:
        raise RegistryBuildError("trusted blueprint and runtime dataset template mismatch")

    default_fields = template.get("default_detail_fields")
    if (
        not isinstance(default_fields, list)
        or len(default_fields) > 128
        or len(default_fields) != len(set(default_fields))
        or any(not isinstance(field, str) or field not in approved_field_ids for field in default_fields)
    ):
        raise RegistryBuildError("dataset template default detail fields are not approved")
    display_name = template.get("display_name")
    time_scope = template.get("time_scope")
    if (
        not isinstance(display_name, str)
        or not display_name
        or len(display_name) > 200
        or not isinstance(time_scope, str)
        or not time_scope
        or len(time_scope) > 64
    ):
        raise RegistryBuildError("dataset template display or time policy is invalid")
    for policy_key in ("date_policy", "date_filter_contract"):
        if policy_key in template and (
            not isinstance(template[policy_key], dict)
            or len(template[policy_key]) > 32
        ):
            raise RegistryBuildError("dataset template date policy is invalid")
    parameters = template.get("parameters")
    if (
        not isinstance(parameters, dict)
        or len(parameters) > 128
        or any(not isinstance(card, dict) for card in parameters.values())
    ):
        raise RegistryBuildError("dataset template parameters are invalid")
    read_policy = template.get("read_policy")
    if (
        not isinstance(read_policy, dict)
        or set(read_policy) - {"read_only", "timeout_seconds", "max_rows"}
        or read_policy.get("read_only") is not True
        or isinstance(read_policy.get("timeout_seconds"), bool)
        or not isinstance(read_policy.get("timeout_seconds"), int)
        or not 1 <= read_policy["timeout_seconds"] <= 120
        or isinstance(read_policy.get("max_rows"), bool)
        or not isinstance(read_policy.get("max_rows"), int)
        or not 1 <= read_policy["max_rows"] <= 1_000_000
    ):
        raise RegistryBuildError("dataset template read policy is invalid")
    if "fixture_only" in template and not isinstance(template["fixture_only"], bool):
        raise RegistryBuildError("dataset template fixture policy is invalid")
    if "upstream_bindings" in template and (
        not isinstance(template["upstream_bindings"], list)
        or len(template["upstream_bindings"]) > 64
        or any(not isinstance(card, dict) for card in template["upstream_bindings"])
    ):
        raise RegistryBuildError("dataset template upstream bindings are invalid")
    payload = _canonical_json_bytes(template)
    if len(payload) > _MAX_DATASET_TEMPLATE_UTF8_BYTES:
        raise RegistryBuildError("dataset template exceeds the UTF-8 byte limit")
    return template, hashlib.sha256(payload).hexdigest()


def _binding_projection(dataset: Any, *, source_version: str) -> dict[str, str]:
    _validate_source_dataset_card_shape(dataset, source_version=source_version)
    if not isinstance(dataset, dict):
        raise RegistryBuildError("source registry dataset entry must be an object")
    return {
        key: _nonempty_text(dataset.get(key), f"dataset {key}")
        for key in BINDING_KEYS
    }


def _descriptor_projection(binding: Any) -> dict[str, Any]:
    if not isinstance(binding, dict):
        raise RegistryBuildError("runtime catalog field descriptor must be an object")

    physical_column = _nonempty_text(binding.get("physical_column"), "physical_column")
    semantic_type = _nonempty_text(binding.get("semantic_type"), "semantic_type")
    if (
        len(physical_column) > 256
        or len(physical_column.encode("utf-8")) > 1024
        or len(semantic_type) > 128
        or len(semantic_type.encode("utf-8")) > 512
    ):
        raise RegistryBuildError("runtime catalog field descriptor text is oversized")
    roles = binding.get("roles")
    if (
        not isinstance(roles, list)
        or not roles
        or len(roles) > 64
        or any(not isinstance(role, str) or _ROLE.fullmatch(role) is None for role in roles)
        or len(roles) != len(set(roles))
    ):
        raise RegistryBuildError("runtime catalog field roles must be a non-empty unique ID list")

    descriptor: dict[str, Any] = {
        "physical_column": physical_column,
        "semantic_type": semantic_type,
        "roles": deepcopy(roles),
    }
    for key in OPTIONAL_DESCRIPTOR_KEYS:
        if key not in binding:
            continue
        value = binding[key]
        if key == "physical_aliases":
            if (
                not isinstance(value, list)
                or len(value) > 128
                or any(
                    not isinstance(alias, str)
                    or not alias.strip()
                    or len(alias) > 256
                    or len(alias.encode("utf-8")) > 1024
                    or any(ord(char) < 32 for char in alias)
                    for alias in value
                )
                or len(value) != len(set(value))
            ):
                raise RegistryBuildError("physical_aliases must be a unique safe string list")
        elif key in {"nullable", "required_in_source"}:
            if not isinstance(value, bool):
                raise RegistryBuildError(f"{key} must be boolean")
        else:
            text = _nonempty_text(value, key)
            if len(text) > 256 or len(text.encode("utf-8")) > 1024:
                raise RegistryBuildError(f"{key} must be a bounded safe string")
        descriptor[key] = deepcopy(value)
    return descriptor


def _approved_v3_descriptors(
    source_dataset: dict[str, Any],
    catalog_fields: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Validate and preserve the v3 registry's approved physical descriptors.

    The compiled catalog may contain broader semantic coverage, but it is not
    allowed to replace approved physical columns or aliases after a registry has
    reached v3. Semantic typing remains compiler-compatible and fail closed.
    """

    raw_fields = source_dataset.get("field_descriptors")
    if not isinstance(raw_fields, dict) or not 1 <= len(raw_fields) <= 2048:
        raise RegistryBuildError("source registry v3 field descriptors must be bounded")
    if not isinstance(catalog_fields, dict) or not catalog_fields:
        raise RegistryBuildError("runtime catalog dataset fields must be non-empty")

    allowed_descriptor_keys = set(REQUIRED_DESCRIPTOR_KEYS) | set(OPTIONAL_DESCRIPTOR_KEYS)
    semantic_compatibility_keys = (
        "semantic_type",
        "coercion",
        "nullable",
        "required_in_source",
        "timezone",
    )
    catalog_field_ids = {_safe_id(field_id) for field_id in catalog_fields}
    if len(catalog_field_ids) != len(catalog_fields):
        raise RegistryBuildError("runtime catalog field identifiers are not unique")

    projected: dict[str, dict[str, Any]] = {}
    for raw_field_id in sorted(raw_fields):
        field_id = _safe_id(raw_field_id)
        raw_descriptor = raw_fields[raw_field_id]
        if (
            not isinstance(raw_descriptor, dict)
            or not set(REQUIRED_DESCRIPTOR_KEYS).issubset(raw_descriptor)
            or set(raw_descriptor) - allowed_descriptor_keys
        ):
            raise RegistryBuildError("source registry v3 field descriptor is open or incomplete")
        if field_id not in catalog_field_ids:
            raise RegistryBuildError("source registry v3 field is absent from runtime catalog")

        approved_descriptor = _descriptor_projection(raw_descriptor)
        catalog_descriptor = _descriptor_projection(catalog_fields[field_id])
        for key in semantic_compatibility_keys:
            if approved_descriptor.get(key) != catalog_descriptor.get(key):
                raise RegistryBuildError(
                    "source registry v3 field descriptor is semantically incompatible "
                    "with runtime catalog"
                )
        if set(approved_descriptor["roles"]) != set(catalog_descriptor["roles"]):
            raise RegistryBuildError(
                "source registry v3 field roles are incompatible with runtime catalog"
            )
        projected[field_id] = approved_descriptor
    return projected


def _exclusion_projection(
    exclusions: dict[str, Any] | None,
    *,
    domain_id: str,
    dataset_ids: set[str],
) -> dict[str, dict[str, dict[str, str]]]:
    if exclusions is None:
        return {dataset_id: {} for dataset_id in dataset_ids}
    if (
        set(exclusions) != {"contract_version", "domain_id", "datasets"}
        or exclusions.get("contract_version") != EXCLUSIONS_V1
        or exclusions.get("domain_id") != domain_id
        or not isinstance(exclusions.get("datasets"), dict)
    ):
        raise RegistryBuildError("source registry exclusions root contract is invalid")
    unknown_datasets = set(exclusions["datasets"]) - dataset_ids
    if unknown_datasets:
        raise RegistryBuildError("source registry exclusions contain an unknown dataset")
    projected: dict[str, dict[str, dict[str, str]]] = {}
    for dataset_id in sorted(dataset_ids):
        raw = exclusions["datasets"].get(dataset_id, {})
        if not isinstance(raw, dict) or len(raw) > 2048:
            raise RegistryBuildError("proposal exclusions must be a bounded object")
        folded_names: set[str] = set()
        normalized: dict[str, dict[str, str]] = {}
        for name in sorted(raw):
            safe_name = _nonempty_text(name, "proposal exclusion name")
            policy = raw[name]
            if not isinstance(policy, dict):
                raise RegistryBuildError("proposal exclusion policy must be an object")
            reason = policy.get("reason_code")
            expected_keys = (
                {"reason_code", "target_field_id"}
                if reason in {"source_expression_before_alias", "legacy_source_name"}
                else {"reason_code"}
            )
            if (
                len(safe_name) > 256
                or reason not in _EXCLUSION_REASONS
                or set(policy) != expected_keys
            ):
                raise RegistryBuildError("proposal exclusion name or reason is invalid")
            normalized_policy = {"reason_code": reason}
            if "target_field_id" in policy:
                normalized_policy["target_field_id"] = _safe_id(
                    policy["target_field_id"]
                )
            folded = _normalized_name(safe_name)
            if folded in folded_names:
                raise RegistryBuildError("proposal exclusion names must be case-insensitively unique")
            folded_names.add(folded)
            normalized[safe_name] = normalized_policy
        projected[dataset_id] = normalized
    return projected


def build_approved_source_registry(
    source_registry: dict[str, Any],
    runtime_catalog: dict[str, Any],
    exclusions: dict[str, Any] | None = None,
    trusted_blueprint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a v3 registry with trusted bindings and compiler-owned semantics."""

    source_version = source_registry.get("contract_version")
    if source_version not in {REGISTRY_V1, REGISTRY_V2, REGISTRY_V3}:
        raise RegistryBuildError("source registry contract version is unsupported")
    base_source_keys = {"contract_version", "domain_id", "datasets"}
    v2_derived_keys = {"semantic_templates", "semantic_vocabulary"}
    v3_derived_keys = v2_derived_keys | {
        "semantic_templates_sha256",
        "semantic_templates_blueprint_sha256",
        "semantic_templates_executable_sha256",
        "semantic_templates_projection_sha256",
    }
    permitted_keys = (
        set()
        if source_version == REGISTRY_V1
        else v2_derived_keys
        if source_version == REGISTRY_V2
        else v3_derived_keys
    )
    actual_source_keys = set(source_registry)
    if not base_source_keys.issubset(actual_source_keys) or actual_source_keys - base_source_keys - permitted_keys:
        raise RegistryBuildError("source registry root contract is open or invalid")
    if source_version == REGISTRY_V3 and actual_source_keys != base_source_keys | v3_derived_keys:
        raise RegistryBuildError("source registry v3 root contract is incomplete")
    if runtime_catalog.get("contract_version") != RUNTIME_CATALOG_V2:
        raise RegistryBuildError("runtime catalog contract version is unsupported")

    registry_domain = _safe_id(source_registry.get("domain_id"), domain=True)
    catalog_domain = _safe_id(runtime_catalog.get("domain_id"), domain=True)
    if registry_domain != catalog_domain:
        raise RegistryBuildError("source registry and runtime catalog domain mismatch")
    if trusted_blueprint is None:
        trusted_blueprint = _load_json(DEFAULT_BLUEPRINT_PATH, "trusted executable blueprint")
    executable, blueprint_sha256, executable_sha256 = _trusted_blueprint_executable(
        trusted_blueprint,
        domain_id=registry_domain,
    )

    source_datasets = source_registry.get("datasets")
    catalog_datasets = runtime_catalog.get("datasets")
    if not isinstance(source_datasets, dict) or not source_datasets:
        raise RegistryBuildError("source registry datasets must be a non-empty object")
    if not isinstance(catalog_datasets, dict) or not catalog_datasets:
        raise RegistryBuildError("runtime catalog datasets must be a non-empty object")

    source_ids = {_safe_id(dataset_id) for dataset_id in source_datasets}
    catalog_ids = {_safe_id(dataset_id) for dataset_id in catalog_datasets}
    if (
        source_ids != catalog_ids
        or len(source_ids) != len(source_datasets)
        or len(catalog_ids) != len(catalog_datasets)
    ):
        raise RegistryBuildError("source registry and runtime catalog dataset mismatch")
    blueprint_datasets = executable.get("datasets")
    if (
        not isinstance(blueprint_datasets, dict)
        or set(blueprint_datasets) != source_ids
    ):
        raise RegistryBuildError("trusted blueprint dataset inventory mismatch")
    projected_exclusions = _exclusion_projection(
        exclusions,
        domain_id=registry_domain,
        dataset_ids=source_ids,
    )

    datasets: dict[str, Any] = {}
    for dataset_id in sorted(source_ids):
        catalog_dataset = catalog_datasets[dataset_id]
        if not isinstance(catalog_dataset, dict):
            raise RegistryBuildError("runtime catalog dataset entry must be an object")
        if catalog_dataset.get("key") != dataset_id:
            raise RegistryBuildError("runtime catalog dataset identity mismatch")
        family = _safe_id(catalog_dataset.get("family"))

        catalog_fields = catalog_dataset.get("fields")
        if not isinstance(catalog_fields, dict) or not catalog_fields:
            raise RegistryBuildError("runtime catalog dataset fields must be non-empty")

        if source_version == REGISTRY_V3:
            source_dataset = source_datasets[dataset_id]
            source_family = _safe_id(source_dataset.get("family"))
            if source_family != family:
                raise RegistryBuildError(
                    "source registry v3 dataset family is incompatible with runtime catalog"
                )
            family = source_family
            fields = _approved_v3_descriptors(source_dataset, catalog_fields)
        else:
            fields = {}
            for field_id in sorted(catalog_fields):
                safe_field_id = _safe_id(field_id)
                fields[safe_field_id] = _descriptor_projection(catalog_fields[field_id])

        approved_names = {
            _normalized_name(name)
            for field_id, descriptor in fields.items()
            for name in (
                field_id,
                descriptor["physical_column"],
                *(descriptor.get("physical_aliases") or []),
            )
        }
        if approved_names & {
            _normalized_name(name) for name in projected_exclusions[dataset_id]
        }:
            raise RegistryBuildError("proposal exclusions overlap an approved field name")
        for exclusion in projected_exclusions[dataset_id].values():
            target_field_id = exclusion.get("target_field_id")
            if target_field_id is not None and target_field_id not in fields:
                raise RegistryBuildError("proposal exclusion target field is not approved")

        dataset_template, dataset_template_sha256 = _dataset_template_projection(
            dataset_id=dataset_id,
            blueprint_dataset=blueprint_datasets[dataset_id],
            runtime_dataset=catalog_dataset,
            approved_field_ids=set(fields),
        )
        dataset = _binding_projection(
            source_datasets[dataset_id],
            source_version=source_version,
        )
        dataset["family"] = family
        dataset["field_descriptors"] = fields
        dataset["proposal_exclusions"] = projected_exclusions[dataset_id]
        dataset["dataset_template"] = dataset_template
        dataset["dataset_template_sha256"] = dataset_template_sha256
        datasets[dataset_id] = dataset

    all_dataset_templates = {
        dataset_id: datasets[dataset_id]["dataset_template"]
        for dataset_id in sorted(datasets)
    }
    if len(_canonical_json_bytes(all_dataset_templates)) > _MAX_ALL_DATASET_TEMPLATES_UTF8_BYTES:
        raise RegistryBuildError("all dataset templates exceed the UTF-8 byte limit")

    semantic_vocabulary = _semantic_vocabulary_projection(runtime_catalog, datasets)
    semantic_templates, projection_evidence = _semantic_templates_projection(
        executable,
        runtime_catalog,
        semantic_vocabulary,
    )
    semantic_templates_sha256 = hashlib.sha256(
        _canonical_json_bytes(semantic_templates)
    ).hexdigest()
    semantic_templates_projection_sha256 = hashlib.sha256(
        _canonical_json_bytes(projection_evidence)
    ).hexdigest()
    return {
        "contract_version": REGISTRY_V3,
        "domain_id": registry_domain,
        "datasets": datasets,
        "semantic_vocabulary": semantic_vocabulary,
        "semantic_templates": semantic_templates,
        "semantic_templates_sha256": semantic_templates_sha256,
        "semantic_templates_blueprint_sha256": blueprint_sha256,
        "semantic_templates_executable_sha256": executable_sha256,
        "semantic_templates_projection_sha256": semantic_templates_projection_sha256,
    }


def _pretty_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def rebuild_registry(
    *,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    output_path: Path | None = None,
    exclusions_path: Path | None = DEFAULT_EXCLUSIONS_PATH,
    blueprint_path: Path = DEFAULT_BLUEPRINT_PATH,
) -> dict[str, Any]:
    destination = output_path or registry_path
    source_registry = _load_json(registry_path, "approved source registry")
    runtime_catalog = _load_json(catalog_path, "compiled runtime catalog")
    trusted_blueprint = _load_json(blueprint_path, "trusted executable blueprint")
    exclusions = (
        _load_json(exclusions_path, "source registry exclusions")
        if exclusions_path is not None and exclusions_path.is_file()
        else None
    )
    rebuilt = build_approved_source_registry(
        source_registry,
        runtime_catalog,
        exclusions,
        trusted_blueprint,
    )
    payload = _pretty_json_bytes(rebuilt)
    _write_atomic(destination, payload)
    vocabulary_payload = _pretty_json_bytes(rebuilt["semantic_vocabulary"])
    templates_payload = _canonical_json_bytes(rebuilt["semantic_templates"])
    dataset_template_material = {
        dataset_id: {
            "dataset_template": card["dataset_template"],
            "dataset_template_sha256": card["dataset_template_sha256"],
        }
        for dataset_id, card in sorted(rebuilt["datasets"].items())
    }
    registry_without_dataset_templates = deepcopy(rebuilt)
    for card in registry_without_dataset_templates["datasets"].values():
        card.pop("dataset_template", None)
        card.pop("dataset_template_sha256", None)
    dataset_template_overhead = len(payload) - len(
        _pretty_json_bytes(registry_without_dataset_templates)
    )
    return {
        "dataset_count": len(rebuilt["datasets"]),
        "dataset_template_bytes": len(
            _canonical_json_bytes(
                {
                    dataset_id: material["dataset_template"]
                    for dataset_id, material in dataset_template_material.items()
                }
            )
        ),
        "dataset_template_byte_overhead": dataset_template_overhead,
        "dataset_templates_sha256": hashlib.sha256(
            _canonical_json_bytes(dataset_template_material)
        ).hexdigest(),
        "field_count": sum(
            len(item["field_descriptors"]) for item in rebuilt["datasets"].values()
        ),
        "semantic_vocabulary_counts": {
            key: len(rebuilt["semantic_vocabulary"][key])
            for key in (
                "datasets",
                "fields",
                "metrics",
                "relations",
                "grains",
                "orderings",
                "predicates",
                "recipes",
                "entity_groups",
            )
        },
        "semantic_vocabulary_sha256": hashlib.sha256(vocabulary_payload).hexdigest(),
        "semantic_template_counts": {
            key: len(rebuilt["semantic_templates"][key])
            for key in (
                "metrics",
                "relations",
                "entity_groups",
                "grains",
                "orderings",
                "predicates",
                "recipes",
                "aliases",
            )
        },
        "semantic_templates_bytes": len(templates_payload),
        "semantic_templates_sha256": rebuilt["semantic_templates_sha256"],
        "semantic_templates_blueprint_sha256": rebuilt[
            "semantic_templates_blueprint_sha256"
        ],
        "semantic_templates_executable_sha256": rebuilt[
            "semantic_templates_executable_sha256"
        ],
        "semantic_templates_projection_sha256": rebuilt[
            "semantic_templates_projection_sha256"
        ],
        "path": str(destination.resolve()),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild the approved source registry v3 from approved physical bindings "
            "and reviewed semantic templates."
        )
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--exclusions", type=Path, default=DEFAULT_EXCLUSIONS_PATH)
    parser.add_argument("--blueprint", type=Path, default=DEFAULT_BLUEPRINT_PATH)
    args = parser.parse_args()

    summary = rebuild_registry(
        registry_path=args.registry,
        catalog_path=args.catalog,
        output_path=args.output,
        exclusions_path=args.exclusions,
        blueprint_path=args.blueprint,
    )
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
