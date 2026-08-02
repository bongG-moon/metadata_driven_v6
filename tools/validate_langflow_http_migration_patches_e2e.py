"""Validate four v6 natural-TXT authoring flows -> analysis over HTTP.

A fresh environment must be bootstrapped by the actual Domain authoring Flow
using the three separate worker-authored Domain, Dataset, and Main Filter TXT
inputs. A separately pinned executable blueprint is only an offline comparison
oracle and is never a Flow input. Domain Policy, Dataset, and Main Filter
authoring then advance the same active package through their bounded ownership
lanes. Persisted evidence is hash/status only: no TXT, blueprint body, provider
response, approval event, credential, or Mongo URI is written.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
import uuid
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import sha256_json
from reference_runtime.authoring_source_manifest import validate_authoring_source_manifest
from reference_runtime.domain_packages import compile_domain_package
from reference_runtime.registered_functions import registered_function_descriptor
from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    assert_secret_absent,
    gemini_model_contract_evidence,
    load_dotenv_values,
    resolve_gemini_api_key,
)
from tools.validate_langflow_http_authoring_e2e import (
    AUTHORING_GEMINI_MODEL,
    FLOW_PATHS,
    _active_package,
    _active_pointer_snapshot,
    _auth_headers,
    _compose_domain_bootstrap_source,
    _flow_defaults,
    _fresh_environment,
    _expected_prepare_llm_calls,
    _loader_roundtrip,
    _run_freeform_clarification_probe,
    _run_authoring_cycle,
    _safe_failure,
    _upload_flow,
)
from tools.validate_langflow_http_e2e import run as run_data_analysis_http
from tools.validate_live_blueprint_authoring import _load_trusted_blueprint


V6_INPUT_DIR = ROOT / "metadata" / "authoring" / "v6_inputs"
DOMAIN_TEXT_PATH = V6_INPUT_DIR / "domain_v6.txt"
DOMAIN_POLICY_TEXT_PATH = V6_INPUT_DIR / "domain_policy_v6.txt"
DATASET_TEXT_PATH = V6_INPUT_DIR / "dataset_v6.txt"
MAIN_FILTER_TEXT_PATH = V6_INPUT_DIR / "main_filter_v6.txt"
AUTHORING_INPUT_PATHS = {
    "domain": DOMAIN_TEXT_PATH,
    "domain_policy": DOMAIN_POLICY_TEXT_PATH,
    "dataset": DATASET_TEXT_PATH,
    "main_filter": MAIN_FILTER_TEXT_PATH,
}
BLUEPRINT_PATH = (
    ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "trusted_executable_blueprint.json"
)
BLUEPRINT_PIN_PATH = BLUEPRINT_PATH.with_suffix(".sha256")
TRUSTED_SOURCE_MANIFEST_PATH = (
    ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "trusted_source_manifest.json"
)
DATA_ANALYSIS_FLOW_PATH = (
    ROOT / "flow_exports" / "metadata_v6_data_analysis_flow_v6_standalone.json"
)
APPROVED_SOURCE_REGISTRY_PATH = (
    ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "approved_source_registry.json"
)
APPROVED_SOURCE_REGISTRY_PIN_PATH = APPROVED_SOURCE_REGISTRY_PATH.with_suffix(".sha256")

_REGISTRY_ROOT_KEYS = {
    "contract_version",
    "domain_id",
    "datasets",
    "semantic_vocabulary",
    "semantic_templates",
    "semantic_templates_sha256",
    "semantic_templates_blueprint_sha256",
    "semantic_templates_executable_sha256",
    "semantic_templates_projection_sha256",
}
_REGISTRY_DATASET_KEYS = {
    "source_type",
    "source_adapter",
    "config_ref",
    "query_ref",
    "family",
    "field_descriptors",
    "proposal_exclusions",
    "dataset_template",
    "dataset_template_sha256",
}
_REGISTRY_FIELD_REQUIRED_KEYS = {"physical_column", "semantic_type", "roles"}
_REGISTRY_FIELD_OPTIONAL_KEYS = {
    "physical_aliases",
    "coercion",
    "nullable",
    "required_in_source",
    "timezone",
}
# This is the canonical order applied by the standalone Authoring Engine before
# compilation.  Comparing role sets would hide ordering drift in the persisted
# package, so the oracle applies this exact normalization and still compares the
# resulting dataset/runtime projections byte-for-byte via canonical hashes.
_COMPILER_FIELD_ROLE_ORDER = (
    "filter",
    "group",
    "join",
    "compare",
    "aggregate",
    "derive",
    "project",
    "sort",
    "rank",
    "metric",
    "output",
)
_ALIAS_CARD_KEYS = {
    "target_type",
    "target_key",
    "values",
    "normalization",
    "match",
    "conflict",
    "provenance_source",
}
_ALIAS_VALUE_KEYS = {"text", "priority"}
_NATURAL_ALIAS_POLICY = {
    "normalization": [
        "unicode_nfkc",
        "trim",
        "collapse_space",
        "latin_casefold",
    ],
    "match": "bounded_longest",
    "conflict": "fail_ambiguous",
    "provenance_source": "natural_authoring",
}
_NATURAL_ALIAS_TARGET_TYPES = {
    "dataset",
    "field",
    "metric",
    "relation",
    "grain",
    "predicate",
    "recipe",
    "entity_group",
}

MANUFACTURING_INTENT_EXTENSION = (
    "제조 용어는 등록된 dataset, field, metric, recipe 별칭만 사용하고 "
    "모호하면 후보 계약으로 제한한다."
)
MANUFACTURING_ANSWER_EXTENSION = (
    "응답은 실행 결과의 검증된 사실만 설명하고 조회 기준, 단위, "
    "빈 결과 여부를 명시한다."
)
_MANUFACTURING_FUNCTION_DESCRIPTOR = registered_function_descriptor(
    "core.trim_and_match_tokens",
    1,
)
MANUFACTURING_FUNCTION_CARD = {
    "function_id": _MANUFACTURING_FUNCTION_DESCRIPTOR["function_id"],
    "version": _MANUFACTURING_FUNCTION_DESCRIPTOR["version"],
    "execution_mode": "registered_standalone",
    "implementation_sha256": _MANUFACTURING_FUNCTION_DESCRIPTOR["implementation_sha256"],
    "input_schema": deepcopy(_MANUFACTURING_FUNCTION_DESCRIPTOR["input_schema"]),
    "output_schema": deepcopy(_MANUFACTURING_FUNCTION_DESCRIPTOR["output_schema"]),
    "required_fields": ["MCP_NO"],
    "limits": {
        "timeout_ms": 1000,
        "max_input_rows": 100,
        "max_output_rows": 100,
        "max_output_bytes": 100_000,
    },
    "failure_policy": "fail_closed",
    "aliases": ["priority MCP labels"],
    "call_template": {
        "dataset_ref": "production",
        "field_ref": "MCP_NO",
        "parameters": {
            "tokens": ["priority"],
            "operator": "equals",
            "match_mode": "any",
            "case_sensitive": False,
        },
        "output_fields": ["MCP_NO"],
    },
}
MANUFACTURING_OUTPUT_OVERLAY = {
    "validation_policy_marker": "manufacturing-natural-patch-v1"
}
FREEFORM_CLARIFICATION_PROBE = (
    "새 업무 분석을 만들고 싶은데 어떤 자료를 봐야 하는지와 무엇을 계산해야 하는지는 "
    "아직 정하지 못했어요. 임의로 정하지 말고 제가 업무 용어로 답할 수 있는 "
    "확인 질문만 해 주세요."
)


def _load_v6_authoring_sources() -> tuple[dict[str, str], dict[str, str], dict[str, Any]]:
    """Load the four v6-only TXT inputs and return text-free evidence."""

    texts: dict[str, str] = {}
    source_hashes: dict[str, str] = {}
    source_evidence: dict[str, Any] = {}
    for kind, path in AUTHORING_INPUT_PATHS.items():
        if not path.is_file():
            raise RuntimeError(f"v6_authoring_input_missing:{kind}")
        text = path.read_text(encoding="utf-8-sig").strip()
        if not text:
            raise RuntimeError(f"v6_authoring_input_empty:{kind}")
        content_sha256 = sha256(text.encode("utf-8")).hexdigest()
        texts[kind] = text
        source_hashes[kind] = content_sha256
        source_evidence[kind] = {
            "path": path.relative_to(ROOT).as_posix(),
            "content_sha256": content_sha256,
            "byte_count": len(text.encode("utf-8")),
            "line_count": len(text.splitlines()),
            "source_text_persisted": False,
        }
    return texts, source_hashes, source_evidence


def _load_trusted_inventory_manifest() -> tuple[dict[str, Any], dict[str, Any]]:
    """Load the admin-reviewed inventory oracle separately from user raw TXT."""

    if not TRUSTED_SOURCE_MANIFEST_PATH.is_file():
        raise RuntimeError("manufacturing_trusted_source_manifest_missing")
    try:
        raw = json.loads(TRUSTED_SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("manufacturing_trusted_source_manifest_invalid") from exc
    if not isinstance(raw, dict):
        raise RuntimeError("manufacturing_trusted_source_manifest_invalid")
    manifest = validate_authoring_source_manifest(raw)
    evidence = {
        "path": TRUSTED_SOURCE_MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "contract_version": str(manifest.get("contract_version") or ""),
        "manifest_sha256": str(manifest.get("manifest_sha256") or ""),
        "source_sha256": str(manifest.get("source_sha256") or ""),
        "counts": deepcopy(manifest.get("counts") or {}),
        "manifest_body_persisted": False,
        "user_raw_txt_used_as_manifest": False,
    }
    return manifest, evidence


def _load_approved_source_registry_oracle(
    trusted_blueprint: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load and independently seal the checked-in Source Registry oracle.

    The compiled catalog beside the registry is a generated historical artifact,
    not the v6 source-binding authority.  Consequently this validator checks the
    v3 registry's closed shape, self-hashes, blueprint provenance, and every
    dataset/field descriptor directly instead of rebuilding it from that catalog.
    """

    if not APPROVED_SOURCE_REGISTRY_PATH.is_file():
        raise RuntimeError("manufacturing_approved_source_registry_missing")
    if not APPROVED_SOURCE_REGISTRY_PIN_PATH.is_file():
        raise RuntimeError("manufacturing_approved_source_registry_pin_missing")
    try:
        registry_bytes = APPROVED_SOURCE_REGISTRY_PATH.read_bytes()
        registry_file_sha256 = sha256(registry_bytes).hexdigest()
        pinned_registry_sha256 = APPROVED_SOURCE_REGISTRY_PIN_PATH.read_text(
            encoding="ascii"
        ).strip()
        registry = json.loads(registry_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, UnicodeError) as exc:
        raise RuntimeError("manufacturing_approved_source_registry_invalid") from exc
    if (
        re.fullmatch(r"[0-9a-f]{64}", pinned_registry_sha256) is None
        or registry_file_sha256 != pinned_registry_sha256
    ):
        raise RuntimeError("manufacturing_approved_source_registry_pin_mismatch")
    if (
        not isinstance(registry, dict)
        or set(registry) != _REGISTRY_ROOT_KEYS
        or registry.get("contract_version") != "metadata.authoring.source-registry.v3"
        or registry.get("domain_id") != "manufacturing"
    ):
        raise RuntimeError("manufacturing_approved_source_registry_invalid")

    try:
        checked_in_blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("manufacturing_trusted_blueprint_invalid") from exc
    executable = trusted_blueprint.get("executable")
    checked_in_executable = (
        checked_in_blueprint.get("executable")
        if isinstance(checked_in_blueprint, dict)
        else None
    )
    if (
        not isinstance(executable, dict)
        or not isinstance(checked_in_executable, dict)
        or executable != checked_in_executable
    ):
        raise RuntimeError("manufacturing_trusted_blueprint_invalid")
    semantic_templates = registry.get("semantic_templates")
    semantic_vocabulary = registry.get("semantic_vocabulary")
    provenance_hashes = (
        "semantic_templates_sha256",
        "semantic_templates_blueprint_sha256",
        "semantic_templates_executable_sha256",
        "semantic_templates_projection_sha256",
    )
    if (
        not isinstance(semantic_templates, dict)
        or not isinstance(semantic_vocabulary, dict)
        or registry.get("semantic_templates_sha256")
        != sha256_json(semantic_templates)
        or registry.get("semantic_templates_blueprint_sha256")
        != checked_in_blueprint.get("blueprint_sha256")
        or registry.get("semantic_templates_executable_sha256")
        != checked_in_blueprint.get("executable_sha256")
        or registry.get("semantic_templates_executable_sha256")
        != trusted_blueprint.get("executable_sha256")
        or any(
            re.fullmatch(r"[0-9a-f]{64}", str(registry.get(key) or "")) is None
            for key in provenance_hashes
        )
    ):
        raise RuntimeError("manufacturing_approved_source_registry_unsealed")

    template_to_blueprint = {
        "aliases": "aliases",
        "entity_groups": "entity_groups",
        "grains": "grains",
        "locale": "locale",
        "metrics": "metrics",
        "orderings": "orderings",
        "planner_policy": "output_profile",
        "predicates": "predicates",
        "recipes": "recipes",
        "relations": "relations",
        "timezone": "timezone",
    }
    if (
        semantic_templates.get("contract_version")
        != "metadata.authoring.semantic-templates.v1"
        or set(semantic_templates)
        != {"contract_version", *template_to_blueprint}
        or any(
            semantic_templates.get(template_key) != executable.get(blueprint_key)
            for template_key, blueprint_key in template_to_blueprint.items()
        )
    ):
        raise RuntimeError("manufacturing_approved_semantic_templates_drift")

    datasets = registry.get("datasets")
    blueprint_datasets = executable.get("datasets")
    if (
        not isinstance(datasets, dict)
        or not datasets
        or not isinstance(blueprint_datasets, dict)
        or set(datasets) != set(blueprint_datasets)
    ):
        raise RuntimeError("manufacturing_approved_dataset_inventory_drift")
    field_count = 0
    allowed_roles = set(_COMPILER_FIELD_ROLE_ORDER)
    allowed_field_keys = _REGISTRY_FIELD_REQUIRED_KEYS | _REGISTRY_FIELD_OPTIONAL_KEYS
    for dataset_id, card in sorted(datasets.items()):
        if not isinstance(card, dict) or set(card) != _REGISTRY_DATASET_KEYS:
            raise RuntimeError("manufacturing_approved_dataset_card_invalid")
        if card.get("dataset_template_sha256") != sha256_json(
            card.get("dataset_template")
        ):
            raise RuntimeError("manufacturing_approved_dataset_template_unsealed")
        descriptors = card.get("field_descriptors")
        if not isinstance(descriptors, dict) or not descriptors:
            raise RuntimeError("manufacturing_approved_field_descriptors_invalid")
        for field_id, descriptor in sorted(descriptors.items()):
            roles = descriptor.get("roles") if isinstance(descriptor, dict) else None
            physical_aliases = (
                descriptor.get("physical_aliases") or []
                if isinstance(descriptor, dict)
                else None
            )
            if (
                not isinstance(field_id, str)
                or not field_id
                or not isinstance(descriptor, dict)
                or not _REGISTRY_FIELD_REQUIRED_KEYS <= set(descriptor) <= allowed_field_keys
                or not isinstance(descriptor.get("physical_column"), str)
                or not descriptor.get("physical_column")
                or not isinstance(descriptor.get("semantic_type"), str)
                or not descriptor.get("semantic_type")
                or not isinstance(roles, list)
                or not roles
                or len(roles) != len(set(roles))
                or not set(roles) <= allowed_roles
                or not isinstance(physical_aliases, list)
                or len(physical_aliases) != len(set(physical_aliases))
                or any(
                    not isinstance(value, str) or not value.strip()
                    for value in physical_aliases
                )
            ):
                raise RuntimeError("manufacturing_approved_field_descriptor_invalid")
        field_count += len(descriptors)

    evidence = {
        "path": APPROVED_SOURCE_REGISTRY_PATH.relative_to(ROOT).as_posix(),
        "pin_path": APPROVED_SOURCE_REGISTRY_PIN_PATH.relative_to(ROOT).as_posix(),
        "contract_version": registry["contract_version"],
        "registry_file_sha256": registry_file_sha256,
        "pinned_registry_file_sha256": pinned_registry_sha256,
        "registry_file_pin_exact": True,
        "semantic_templates_sha256": registry["semantic_templates_sha256"],
        "semantic_templates_blueprint_sha256": registry[
            "semantic_templates_blueprint_sha256"
        ],
        "semantic_templates_executable_sha256": registry[
            "semantic_templates_executable_sha256"
        ],
        "semantic_templates_projection_sha256": registry[
            "semantic_templates_projection_sha256"
        ],
        "counts": {"datasets": len(datasets), "field_descriptors": field_count},
        "registry_body_persisted": False,
    }
    return registry, evidence


def _registry_owned_dataset_draft(
    approved_source_registry: dict[str, Any],
) -> dict[str, Any]:
    """Project registry-owned bindings into compiler input deterministically."""

    datasets: dict[str, Any] = {}
    for dataset_id, card in sorted(approved_source_registry["datasets"].items()):
        dataset = deepcopy(card["dataset_template"])
        dataset["family"] = card["family"]
        for key in ("source_type", "source_adapter", "config_ref", "query_ref"):
            dataset[key] = card[key]
        fields: dict[str, Any] = {}
        for field_id, descriptor in sorted(card["field_descriptors"].items()):
            normalized = deepcopy(descriptor)
            raw_roles = normalized["roles"]
            normalized["roles"] = [
                role for role in _COMPILER_FIELD_ROLE_ORDER if role in raw_roles
            ]
            fields[field_id] = normalized
        dataset["fields"] = fields
        datasets[dataset_id] = dataset
    return datasets


def _alias_delta_validation(
    actual_catalog: dict[str, Any],
    oracle_catalog: dict[str, Any],
    *,
    main_filter_source: str,
) -> dict[str, Any]:
    """Validate additive worker aliases without weakening the core oracle."""

    actual_aliases = actual_catalog.get("aliases")
    baseline_aliases = oracle_catalog.get("aliases")
    if not isinstance(actual_aliases, dict) or not isinstance(baseline_aliases, dict):
        return {
            "closed_schema": False,
            "registered_targets": False,
            "baseline_preserved": False,
            "additive_only": False,
            "worker_delta_policy_exact": False,
            "delta_shape_priority_exact": False,
            "delta_source_grounded": False,
            "delta_labels_unique": False,
            "actual_count": 0,
            "baseline_count": 0,
            "added_card_count": 0,
            "extended_card_count": 0,
        }

    process_targets = {
        str(item.get("oper_name"))
        for ordering in (actual_catalog.get("orderings") or {}).values()
        if isinstance(ordering, dict)
        for item in (ordering.get("items") or [])
        if isinstance(item, dict) and str(item.get("oper_name") or "")
    }
    baseline_status_targets = {
        str(card.get("target_key"))
        for card in baseline_aliases.values()
        if isinstance(card, dict) and card.get("target_type") == "status"
    }
    target_registries = {
        "dataset": set(actual_catalog.get("datasets") or {}),
        "field": set(actual_catalog.get("fields") or {}),
        "metric": set(actual_catalog.get("metrics") or {}),
        "relation": set(actual_catalog.get("relations") or {}),
        "grain": set(actual_catalog.get("grains") or {}),
        "predicate": set(actual_catalog.get("predicates") or {}),
        "recipe": set(actual_catalog.get("recipes") or {}),
        "entity_group": set(actual_catalog.get("entity_groups") or {}),
        "process_group": set(actual_catalog.get("entity_groups") or {}),
        "product_group": set(actual_catalog.get("predicates") or {}),
        "process": process_targets,
        "status": baseline_status_targets,
    }
    closed_schema = True
    registered_targets = True
    worker_delta_policy_exact = True
    delta_shape_priority_exact = True
    delta_source_grounded = True
    delta_labels_unique = True
    normalized_source = _normalize_alias_text(main_filter_source)
    delta_source_unmatched_count = 0
    delta_duplicate_normalized_count = 0
    delta_cross_target_count = 0
    delta_baseline_conflict_count = 0
    baseline_label_targets: dict[str, set[tuple[str, str]]] = {}
    for baseline in baseline_aliases.values():
        if not isinstance(baseline, dict):
            continue
        baseline_target = (
            str(baseline.get("target_type") or ""),
            str(baseline.get("target_key") or ""),
        )
        for value in baseline.get("values") or []:
            if isinstance(value, dict) and isinstance(value.get("text"), str):
                label = _normalize_alias_text(value["text"])
                if label:
                    baseline_label_targets.setdefault(label, set()).add(baseline_target)
    delta_label_targets: dict[str, tuple[str, str]] = {}
    delta_value_count = 0
    for alias_id, card in actual_aliases.items():
        if not isinstance(card, dict) or set(card) != _ALIAS_CARD_KEYS:
            closed_schema = False
            registered_targets = False
            continue
        target_type = str(card.get("target_type") or "")
        target_key = str(card.get("target_key") or "")
        normalization = card.get("normalization")
        values = card.get("values")
        scalar_policy_valid = all(
            isinstance(card.get(key), str)
            and bool(card.get(key))
            and len(card[key]) <= 128
            for key in ("match", "conflict", "provenance_source")
        )
        normalization_valid = (
            isinstance(normalization, list)
            and 1 <= len(normalization) <= 16
            and len(normalization) == len(set(normalization))
            and all(
                isinstance(item, str)
                and re.fullmatch(r"[a-z][a-z0-9_]{0,63}", item) is not None
                for item in normalization
            )
        )
        values_valid = isinstance(values, list) and 1 <= len(values) <= 128
        if values_valid:
            value_hashes: list[str] = []
            for value in values:
                priority = value.get("priority") if isinstance(value, dict) else None
                text = value.get("text") if isinstance(value, dict) else None
                if (
                    not isinstance(value, dict)
                    or set(value) != _ALIAS_VALUE_KEYS
                    or not isinstance(text, str)
                    or not text.strip()
                    or len(text.encode("utf-8")) > 1024
                    or any(ord(character) < 32 for character in text)
                    or isinstance(priority, bool)
                    or not isinstance(priority, int)
                    or not 0 <= priority <= 1_000_000
                ):
                    values_valid = False
                    break
                value_hashes.append(sha256_json(value))
            values_valid = values_valid and len(value_hashes) == len(set(value_hashes))
        closed_schema = closed_schema and (
            isinstance(alias_id, str)
            and 1 <= len(alias_id) <= 256
            and alias_id == f"{target_type}:{target_key}"
            and scalar_policy_valid
            and normalization_valid
            and values_valid
        )
        registered_targets = registered_targets and (
            target_type in target_registries
            and target_key in target_registries[target_type]
        )
        if alias_id not in baseline_aliases:
            worker_delta_policy_exact = worker_delta_policy_exact and (
                target_type in _NATURAL_ALIAS_TARGET_TYPES
                and all(card.get(key) == value for key, value in _NATURAL_ALIAS_POLICY.items())
            )

        baseline_value_hashes = {
            sha256_json(value)
            for value in (
                baseline_aliases.get(alias_id, {}).get("values") or []
                if isinstance(baseline_aliases.get(alias_id), dict)
                else []
            )
        }
        current_target = (target_type, target_key)
        for value in values if isinstance(values, list) else []:
            if sha256_json(value) in baseline_value_hashes:
                continue
            delta_value_count += 1
            text = value.get("text") if isinstance(value, dict) else None
            priority = value.get("priority") if isinstance(value, dict) else None
            normalized_label = _normalize_alias_text(text) if isinstance(text, str) else ""
            delta_shape_priority_exact = delta_shape_priority_exact and (
                isinstance(value, dict)
                and set(value) == _ALIAS_VALUE_KEYS
                and priority == 100
                and bool(normalized_label)
            )
            delta_source_grounded = delta_source_grounded and (
                bool(normalized_label)
                and bool(normalized_source)
                and normalized_label in normalized_source
            )
            if not normalized_label or not normalized_source or normalized_label not in normalized_source:
                delta_source_unmatched_count += 1
            baseline_targets = baseline_label_targets.get(normalized_label, set())
            if baseline_targets and baseline_targets != {current_target}:
                delta_labels_unique = False
                delta_baseline_conflict_count += 1
            if normalized_label in delta_label_targets:
                delta_labels_unique = False
                delta_duplicate_normalized_count += 1
                if delta_label_targets[normalized_label] != current_target:
                    delta_cross_target_count += 1
            else:
                delta_label_targets[normalized_label] = current_target

    baseline_preserved = set(baseline_aliases) <= set(actual_aliases)
    extended_card_count = 0
    if baseline_preserved:
        for alias_id, baseline in baseline_aliases.items():
            actual = actual_aliases[alias_id]
            if not isinstance(actual, dict) or any(
                actual.get(key) != baseline.get(key)
                for key in _ALIAS_CARD_KEYS - {"values"}
            ):
                baseline_preserved = False
                break
            baseline_values = {
                sha256_json(value) for value in baseline.get("values") or []
            }
            actual_values = {sha256_json(value) for value in actual.get("values") or []}
            if not baseline_values <= actual_values:
                baseline_preserved = False
                break
            if actual_values != baseline_values:
                extended_card_count += 1
    added_card_count = len(set(actual_aliases) - set(baseline_aliases))
    return {
        "closed_schema": closed_schema,
        "registered_targets": registered_targets,
        "baseline_preserved": baseline_preserved,
        "additive_only": baseline_preserved,
        "worker_delta_policy_exact": worker_delta_policy_exact
        and delta_shape_priority_exact
        and delta_source_grounded
        and delta_labels_unique,
        "delta_shape_priority_exact": delta_shape_priority_exact,
        "delta_source_grounded": delta_source_grounded,
        "delta_labels_unique": delta_labels_unique,
        "delta_value_count": delta_value_count,
        "delta_source_unmatched_count": delta_source_unmatched_count,
        "delta_duplicate_normalized_count": delta_duplicate_normalized_count,
        "delta_cross_target_count": delta_cross_target_count,
        "delta_baseline_conflict_count": delta_baseline_conflict_count,
        "actual_count": len(actual_aliases),
        "baseline_count": len(baseline_aliases),
        "added_card_count": added_card_count,
        "extended_card_count": extended_card_count,
        "actual_aliases_sha256": sha256_json(actual_aliases),
        "baseline_aliases_sha256": sha256_json(baseline_aliases),
        "alias_payload_persisted": False,
        "main_filter_source_persisted": False,
    }


def _normalize_alias_text(value: str) -> str:
    """Apply the registered natural-alias normalization without retaining text."""

    return " ".join(unicodedata.normalize("NFKC", value).split()).casefold()


def _display_annotation_validation(catalog: dict[str, Any]) -> dict[str, Any]:
    datasets = catalog.get("datasets")
    root_display = catalog.get("display_name")
    root_description = catalog.get("description")
    dataset_displays = {
        key: card.get("display_name") if isinstance(card, dict) else None
        for key, card in (datasets or {}).items()
    } if isinstance(datasets, dict) else {}
    checks = {
        "root_display_name_valid": isinstance(root_display, str)
        and bool(root_display.strip())
        and len(root_display.encode("utf-8")) <= 4096,
        "root_description_valid": isinstance(root_description, str)
        and len(root_description.encode("utf-8")) <= 16_384,
        "dataset_display_names_complete": isinstance(datasets, dict)
        and len(dataset_displays) == len(datasets)
        and all(
            isinstance(value, str)
            and bool(value.strip())
            and len(value.encode("utf-8")) <= 4096
            for value in dataset_displays.values()
        ),
    }
    return {
        "display_annotations_sha256": sha256_json(
            {
                "display_name": root_display,
                "description": root_description,
                "datasets": dataset_displays,
            }
        ),
        "annotation_payload_persisted": False,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _policy_overlay_validation(
    actual_catalog: dict[str, Any],
    oracle_catalog: dict[str, Any],
    expected_policy: dict[str, Any] | None,
) -> dict[str, Any]:
    expected_policy = deepcopy(expected_policy) if isinstance(expected_policy, dict) else {}
    expected_prompts = deepcopy(
        expected_policy.get("prompt_extensions", oracle_catalog.get("prompt_extensions"))
    )
    expected_functions = deepcopy(
        expected_policy.get(
            "specialized_functions", oracle_catalog.get("specialized_functions")
        )
    )
    expected_output = deepcopy(oracle_catalog.get("output_profile") or {})
    output_overlay = expected_policy.get("output_profile_overlay") or {}
    if not isinstance(output_overlay, dict):
        output_overlay = {"__invalid_overlay__": True}
    expected_output.update(deepcopy(output_overlay))
    actual_prompts = actual_catalog.get("prompt_extensions")
    actual_functions = actual_catalog.get("specialized_functions")
    actual_output = actual_catalog.get("output_profile")
    checks = {
        "prompt_extensions_closed": isinstance(actual_prompts, dict)
        and set(actual_prompts) == {"intent", "answer"}
        and all(isinstance(value, str) for value in actual_prompts.values()),
        "prompt_extensions_exact": actual_prompts == expected_prompts,
        "specialized_functions_exact": actual_functions == expected_functions,
        "output_profile_exact": actual_output == expected_output,
    }
    return {
        "actual_policy_sha256": sha256_json(
            {
                "prompt_extensions": actual_prompts,
                "specialized_functions": actual_functions,
                "output_profile": actual_output,
            }
        ),
        "expected_policy_sha256": sha256_json(
            {
                "prompt_extensions": expected_prompts,
                "specialized_functions": expected_functions,
                "output_profile": expected_output,
            }
        ),
        "policy_payload_persisted": False,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _dataset_execution_projection(package: dict[str, Any]) -> dict[str, Any]:
    """Return dataset execution metadata with presentation labels removed."""

    catalog = package.get("runtime_catalog") if isinstance(package, dict) else None
    raw_datasets = catalog.get("datasets") if isinstance(catalog, dict) else None
    if not isinstance(raw_datasets, dict):
        raise RuntimeError("migration_dataset_projection_invalid")
    datasets = deepcopy(raw_datasets)
    for card in datasets.values():
        if not isinstance(card, dict):
            raise RuntimeError("migration_dataset_projection_invalid")
        card.pop("display_name", None)
    return datasets


def _domain_oracle_comparison(
    package: dict[str, Any],
    *,
    trusted_blueprint: dict[str, Any],
    approved_source_registry: dict[str, Any],
    environment: str,
    main_filter_source: str = "",
    expected_revision: int = 1,
    expected_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare the composed Flow result to the reviewed executable oracle.

    The blueprint owns semantic execution templates and the Source Registry owns
    physical dataset bindings.  Display annotations, additive natural aliases,
    and Domain Policy overlays are validated in their own lanes and excluded
    from the exact core projection; they are never silently ignored.
    """

    executable = trusted_blueprint.get("executable")
    annotations = trusted_blueprint.get("default_annotations")
    if not isinstance(executable, dict) or not isinstance(annotations, dict):
        raise RuntimeError("manufacturing_trusted_blueprint_invalid")
    oracle_draft = {**deepcopy(executable), **deepcopy(annotations)}
    oracle_draft["datasets"] = _registry_owned_dataset_draft(
        approved_source_registry
    )
    oracle_package = compile_domain_package(
        oracle_draft,
        "manufacturing",
        environment,
        revision=expected_revision,
        lifecycle_status="validated",
    )
    actual_catalog = deepcopy(package.get("runtime_catalog") or {})
    oracle_catalog = deepcopy(oracle_package.get("runtime_catalog") or {})
    actual_dataset_projection = _dataset_execution_projection(package)
    oracle_dataset_projection = _dataset_execution_projection(oracle_package)
    alias_delta = _alias_delta_validation(
        actual_catalog,
        oracle_catalog,
        main_filter_source=main_filter_source,
    )
    display_annotations = _display_annotation_validation(actual_catalog)
    policy_overlay = _policy_overlay_validation(
        actual_catalog,
        oracle_catalog,
        expected_policy,
    )
    excluded_sections = {
        "display_name",
        "description",
        "catalog_sha256",
        "prompt_extensions",
        "specialized_functions",
        "output_profile",
        "aliases",
    }
    actual_catalog["datasets"] = deepcopy(actual_dataset_projection)
    oracle_catalog["datasets"] = deepcopy(oracle_dataset_projection)
    for catalog in (actual_catalog, oracle_catalog):
        for section in excluded_sections:
            catalog.pop(section, None)
    actual_sha256 = sha256_json(actual_catalog)
    oracle_sha256 = sha256_json(oracle_catalog)
    actual_section_hashes = {
        key: sha256_json(value) for key, value in sorted(actual_catalog.items())
    }
    oracle_section_hashes = {
        key: sha256_json(value) for key, value in sorted(oracle_catalog.items())
    }
    count_sections = {
        "datasets",
        "fields",
        "metrics",
        "entity_groups",
        "grains",
        "relations",
        "orderings",
        "predicates",
        "recipes",
    }
    actual_counts = {
        key: len(actual_catalog.get(key) or {}) for key in sorted(count_sections)
    }
    oracle_counts = {
        key: len(oracle_catalog.get(key) or {}) for key in sorted(count_sections)
    }
    checks = {
        "revision_exact": int(package.get("revision") or 0) == expected_revision,
        "identity_exact": package.get("domain_id") == "manufacturing"
        and package.get("environment") == environment,
        "compiler_exact": package.get("compiler_version")
        == oracle_package.get("compiler_version"),
        "section_keys_exact": set(actual_catalog) == set(oracle_catalog),
        "section_counts_exact": actual_counts == oracle_counts,
        "section_hashes_exact": actual_section_hashes == oracle_section_hashes,
        "executable_runtime_projection_exact": actual_sha256 == oracle_sha256,
        "registry_dataset_binding_exact": sha256_json(actual_dataset_projection)
        == sha256_json(oracle_dataset_projection),
        "compiler_derived_fields_exact": sha256_json(
            (package.get("runtime_catalog") or {}).get("fields") or {}
        )
        == sha256_json(oracle_package["runtime_catalog"].get("fields") or {}),
        "alias_closed_schema": alias_delta["closed_schema"],
        "alias_registered_targets": alias_delta["registered_targets"],
        "baseline_aliases_preserved": alias_delta["baseline_preserved"],
        "worker_alias_delta_additive_only": alias_delta["additive_only"],
        "worker_alias_delta_policy_exact": alias_delta[
            "worker_delta_policy_exact"
        ],
        "worker_alias_delta_shape_priority_exact": alias_delta[
            "delta_shape_priority_exact"
        ],
        "worker_alias_delta_source_grounded": alias_delta[
            "delta_source_grounded"
        ],
        "worker_alias_delta_labels_unique": alias_delta[
            "delta_labels_unique"
        ],
        "display_annotations_valid": display_annotations["passed"],
        "policy_overlay_exact": policy_overlay["passed"],
        "oracle_not_flow_input": True,
    }
    return {
        "actual_executable_projection_sha256": actual_sha256,
        "oracle_executable_projection_sha256": oracle_sha256,
        "actual_section_hashes": actual_section_hashes,
        "oracle_section_hashes": oracle_section_hashes,
        "actual_counts": actual_counts,
        "oracle_counts": oracle_counts,
        "actual_dataset_projection_sha256": sha256_json(actual_dataset_projection),
        "oracle_dataset_projection_sha256": sha256_json(oracle_dataset_projection),
        "source_registry_sha256": sha256_json(approved_source_registry),
        "field_role_normalization": {
            "mode": "compiler_canonical_order",
            "order_sha256": sha256_json(list(_COMPILER_FIELD_ROLE_ORDER)),
            "set_only_comparison_used": False,
        },
        "alias_delta": alias_delta,
        "display_annotations": display_annotations,
        "policy_overlay": policy_overlay,
        "excluded_sections": sorted(excluded_sections),
        "oracle_blueprint_sha256": str(trusted_blueprint.get("blueprint_sha256") or ""),
        "oracle_payload_persisted": False,
        "checks": checks,
        "passed": all(checks.values()),
    }


def run(
    *,
    server_url: str,
    env_path: Path,
    environment_prefix: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    from pymongo import MongoClient

    env = load_dotenv_values(env_path)
    gemini_key = resolve_gemini_api_key(env_path)
    langflow_key = str(os.getenv("LANGFLOW_API_KEY") or env.get("LANGFLOW_API_KEY") or "")
    mongo_uri = str(os.getenv("MONGODB_URI") or env.get("MONGODB_URI") or "").strip()
    database_name = str(os.getenv("MONGODB_DATABASE") or env.get("MONGODB_DATABASE") or "datagov").strip()
    if not mongo_uri:
        raise RuntimeError("mongodb_uri_not_configured")
    if DEFAULT_GEMINI_MODEL != AUTHORING_GEMINI_MODEL:
        raise RuntimeError("authoring_gemini_model_constant_drift")

    nonce = uuid.uuid4().hex
    environment = _fresh_environment(environment_prefix, nonce)
    texts, source_hashes, authoring_sources = _load_v6_authoring_sources()
    domain_bootstrap_source = _compose_domain_bootstrap_source(
        texts["domain"],
        texts["dataset"],
        texts["main_filter"],
    )
    domain_bootstrap_sha256 = sha256(
        domain_bootstrap_source.encode("utf-8")
    ).hexdigest()
    source_manifest, source_manifest_evidence = _load_trusted_inventory_manifest()
    trusted_blueprint, trusted_blueprint_pin, blueprint_trust = _load_trusted_blueprint(
        blueprint_path=BLUEPRINT_PATH,
        pin_path=BLUEPRINT_PIN_PATH,
        source_manifest=source_manifest,
        domain_id="manufacturing",
        environment=environment,
    )
    approved_source_registry, approved_source_registry_evidence = (
        _load_approved_source_registry_oracle(trusted_blueprint)
    )
    blueprint_trust_checks = {
        "checked_in_pin_sha256": len(
            str(blueprint_trust.get("checked_in_blueprint_sha256") or "")
        )
        == 64,
        "target_pin_exact": blueprint_trust.get("target_blueprint_sha256")
        == trusted_blueprint_pin,
        "executable_sha256_exact": blueprint_trust.get("executable_sha256")
        == trusted_blueprint.get("executable_sha256"),
        "source_manifest_sha256_exact": blueprint_trust.get("source_manifest_sha256")
        == trusted_blueprint.get("source_manifest_sha256")
        == source_manifest.get("manifest_sha256"),
        "identity_exact": trusted_blueprint.get("domain_id") == "manufacturing"
        and trusted_blueprint.get("environment") == environment,
    }

    defaults = [_flow_defaults(path) for path in FLOW_PATHS]
    expected_flow_kinds = ["domain", "dataset", "main_filter", "domain_policy"]
    defaults_ok = [row.get("authoring_kind") for row in defaults] == expected_flow_kinds and all(
        row["metadata_contract_mode"] == "domain_package_v2"
        and row["source_grounding_mode"] == "freeform_llm"
        and row["model_names"]
        == ([] if row["authoring_kind"] == "domain_policy" else [AUTHORING_GEMINI_MODEL])
        and row["model_contract"]["passed"] is True
        and (
            row["prompt_node_count"] == 0
            and row["context_builder_node_count"] == 0
            and row["composer_node_count"] == 0
            and row["invoker_node_count"] == 0
            if row["authoring_kind"] == "domain_policy"
            else row["prompt_node_count"]
            == (3 if row["authoring_kind"] == "domain" else 1)
            and row["context_builder_node_count"]
            == (3 if row["authoring_kind"] == "domain" else 1)
            and row["composer_node_count"]
            == (3 if row["authoring_kind"] == "domain" else 1)
            and row["invoker_node_count"]
            == (3 if row["authoring_kind"] == "domain" else 1)
        )
        and row["trusted_blueprint_json_default_empty"] is True
        and row["trusted_blueprint_pin_default_empty"] is True
        for row in defaults
    )
    model_contract = gemini_model_contract_evidence()
    exact_gemini_no_fallback = (
        model_contract.get("requested_model") == AUTHORING_GEMINI_MODEL
        and model_contract.get("temperature") == 0
        and model_contract.get("candidate_count") == 1
        and model_contract.get("fallback_enabled") is False
        and model_contract.get("fallback_models") == []
        and all(row.get("model_contract", {}).get("passed") is True for row in defaults)
    )
    client = requests.Session()
    headers = _auth_headers(client, server_url, env)
    uploaded = [
        _upload_flow(client, headers, server_url, path, timeout_seconds)
        for path in FLOW_PATHS
    ]
    imports = [
        {
            "file": path.name,
            "flow_sha256": sha256(path.read_bytes()).hexdigest(),
            "flow_id_sha256": sha256(str(record.get("id") or "").encode("utf-8")).hexdigest(),
            "endpoint_name": str(record.get("endpoint_name") or ""),
            "node_count": len((record.get("data") or {}).get("nodes") or []),
        }
        for path, record in zip(FLOW_PATHS, uploaded, strict=True)
    ]

    mongo = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    database = mongo[database_name]
    production_pointer_before = _active_pointer_snapshot(
        database,
        domain_id="manufacturing",
    )
    initial_pointer, initial_package = _active_package(
        database,
        domain_id="manufacturing",
        environment=environment,
    )
    if initial_pointer or initial_package:
        mongo.close()
        raise RuntimeError("fresh_v6_authoring_environment_not_empty")

    clarification_probe = _run_freeform_clarification_probe(
        client=client,
        headers=headers,
        server_url=server_url,
        flow_id=str(uploaded[0]["id"]),
        database=database,
        database_name=database_name,
        domain_id="manufacturing",
        environment=environment,
        timeout_seconds=timeout_seconds,
    )
    if not clarification_probe["passed"]:
        mongo.close()
        raise RuntimeError("freeform_clarification_probe_failed")

    policy_overlays = {
        "intent_prompt_extension": MANUFACTURING_INTENT_EXTENSION,
        "answer_prompt_extension": MANUFACTURING_ANSWER_EXTENSION,
        "specialized_functions_json": json.dumps(
            [MANUFACTURING_FUNCTION_CARD],
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        "output_profile_json": json.dumps(
            MANUFACTURING_OUTPUT_OVERLAY,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    }
    specs = (
        ("domain", str(uploaded[0]["id"]), texts["domain"], None),
        ("domain_policy", str(uploaded[3]["id"]), texts["domain_policy"], policy_overlays),
        ("dataset", str(uploaded[1]["id"]), texts["dataset"], None),
        ("main_filter", str(uploaded[2]["id"]), texts["main_filter"], None),
    )
    cycles: list[dict[str, Any]] = []
    latest_package: dict[str, Any] = {}
    domain_bootstrap_checks: dict[str, Any] = {"evaluated": False, "passed": False}
    dataset_patch_checks: dict[str, Any] = {"evaluated": False, "passed": False}
    for index, (kind, flow_id, source_text, overlays) in enumerate(specs, start=1):
        before_cycle_package = latest_package
        input_node_tweaks = (
            {
                "chat_input": {"input_value": texts["domain"]},
                "dataset_source_input": {"input_value": texts["dataset"]},
                "main_filter_source_input": {
                    "input_value": texts["main_filter"]
                },
            }
            if kind == "domain"
            else None
        )
        expected_source_text = (
            domain_bootstrap_source if kind == "domain" else source_text
        )
        cycle, next_package = _run_authoring_cycle(
            client=client,
            headers=headers,
            server_url=server_url,
            flow_id=flow_id,
            database=database,
            database_name=database_name,
            domain_id="manufacturing",
            environment=environment,
            authoring_kind=kind,
            source_text=source_text,
            nonce=f"migration-{index}-{uuid.uuid4().hex}",
            timeout_seconds=timeout_seconds,
            policy_overlays=overlays,
            source_grounding_mode="freeform_llm",
            input_node_tweaks=input_node_tweaks,
            expected_source_text=expected_source_text,
            semantic_completeness_fn=None,
            # Dataset/Main Filter text is already consumed by the initial
            # split bootstrap. Reapplying the same worker text must be an
            # idempotent success; only the explicit operator policy overlay is
            # required to change its owned section.
            require_owned_change=kind == "domain_policy",
        )
        cycles.append(cycle)
        if not cycle["passed"]:
            mongo.close()
            raise RuntimeError(f"migration_natural_patch_failed:{kind}")
        if kind == "domain":
            domain_catalog = next_package.get("runtime_catalog") or {}
            input_hashes = cycle.get("source_input_node_hashes") or {}
            bootstrap_checks = {
                "revision_one": int(next_package.get("revision") or 0) == 1,
                "identity_exact": next_package.get("domain_id") == "manufacturing"
                and next_package.get("environment") == environment,
                "compiler_pinned": next_package.get("compiler_version")
                == "metadata-domain-compiler.v6.3",
                "datasets_nonempty": len(domain_catalog.get("datasets") or {}) >= 1,
                "fields_nonempty": len(domain_catalog.get("fields") or {}) >= 1,
                "composed_source_hash_exact": cycle.get("source_text_sha256")
                == domain_bootstrap_sha256,
                "domain_input_node_hash_exact": input_hashes.get("chat_input")
                == source_hashes["domain"],
                "dataset_input_node_hash_exact": input_hashes.get(
                    "dataset_source_input"
                )
                == source_hashes["dataset"],
                "main_filter_input_node_hash_exact": input_hashes.get(
                    "main_filter_source_input"
                )
                == source_hashes["main_filter"],
                "blueprint_not_flow_input": cycle.get(
                    "trusted_blueprint_configured"
                )
                is False,
            }
            domain_bootstrap_checks = {
                "evaluated": True,
                "package_sha256": str(next_package.get("package_sha256") or ""),
                "catalog_sha256": str(domain_catalog.get("catalog_sha256") or ""),
                "counts": {
                    key: len(domain_catalog.get(key) or {})
                    for key in ("datasets", "fields", "metrics", "relations", "recipes")
                },
                "checks": bootstrap_checks,
                "passed": all(bootstrap_checks.values()),
            }
            if not domain_bootstrap_checks["passed"]:
                mongo.close()
                raise RuntimeError("domain_raw_txt_bootstrap_invalid")
        if kind == "dataset":
            before_projection = _dataset_execution_projection(before_cycle_package)
            after_projection = _dataset_execution_projection(next_package)
            before_displays = {
                key: str(card.get("display_name") or "")
                for key, card in sorted(
                    before_cycle_package["runtime_catalog"]["datasets"].items()
                )
            }
            after_displays = {
                key: str(card.get("display_name") or "")
                for key, card in sorted(next_package["runtime_catalog"]["datasets"].items())
            }
            projection_before_sha256 = sha256_json(before_projection)
            projection_after_sha256 = sha256_json(after_projection)
            checks = {
                "dataset_keys_exact": set(before_projection) == set(after_projection),
                "execution_projection_unchanged": (
                    projection_before_sha256 == projection_after_sha256
                ),
                "display_annotations_stable": before_displays == after_displays,
            }
            dataset_patch_checks = {
                "evaluated": True,
                "execution_projection_before_sha256": projection_before_sha256,
                "execution_projection_after_sha256": projection_after_sha256,
                "checks": checks,
                "passed": all(checks.values()),
            }
            if not dataset_patch_checks["passed"]:
                mongo.close()
                raise RuntimeError("migration_dataset_execution_binding_changed")
        latest_package = next_package

    domain_oracle_checks = {
        "evaluated": True,
        **_domain_oracle_comparison(
            latest_package,
            trusted_blueprint=trusted_blueprint,
            approved_source_registry=approved_source_registry,
            environment=environment,
            main_filter_source="\n".join(
                texts[kind] for kind in ("domain", "dataset", "main_filter")
            ),
            expected_revision=4,
            expected_policy={
                "prompt_extensions": {
                    "intent": MANUFACTURING_INTENT_EXTENSION,
                    "answer": MANUFACTURING_ANSWER_EXTENSION,
                },
                "specialized_functions": [MANUFACTURING_FUNCTION_CARD],
                "output_profile_overlay": MANUFACTURING_OUTPUT_OVERLAY,
            },
        ),
    }
    if not domain_oracle_checks["passed"]:
        mongo.close()
        raise RuntimeError("composed_authoring_oracle_mismatch")

    loader = _loader_roundtrip(
        mongo_uri=mongo_uri,
        database_name=database_name,
        domain_id="manufacturing",
        environment=environment,
    )
    production_pointer_after = _active_pointer_snapshot(
        database,
        domain_id="manufacturing",
    )
    mongo.close()
    production_pointer_checks = {
        "identity_exact": production_pointer_before["environment"] == "production"
        and production_pointer_after["environment"] == "production"
        and production_pointer_before["domain_id"] == "manufacturing"
        and production_pointer_after["domain_id"] == "manufacturing",
        "presence_unchanged": production_pointer_before["present"]
        == production_pointer_after["present"],
        "hash_unchanged": production_pointer_before["sha256"]
        == production_pointer_after["sha256"],
    }
    loader_checks = {
        "loader_ok": loader.get("ok") is True,
        "identity_exact": loader.get("domain_id") == "manufacturing"
        and loader.get("environment") == environment,
        "revision_exact": int(loader.get("revision") or 0) == 4,
        "package_hash_exact": loader.get("package_sha256") == latest_package.get("package_sha256"),
        "bundle_hash_exact": loader.get("bundle_sha256") == latest_package.get("bundle_sha256"),
    }

    data_analysis = run_data_analysis_http(
        DATA_ANALYSIS_FLOW_PATH,
        server_url=server_url,
        env_path=env_path,
        model=AUTHORING_GEMINI_MODEL,
        domain_id="manufacturing",
        environment=environment,
        timeout_seconds=timeout_seconds,
    )
    cycle_order_exact = [row["authoring_kind"] for row in cycles] == [
        "domain",
        "domain_policy",
        "dataset",
        "main_filter",
    ]
    revision_chain = [row["before"]["revision"] for row in cycles] == [0, 1, 2, 3] and [
        row["after"]["revision"] for row in cycles
    ] == [1, 2, 3, 4]
    draft_calls = sum(int(row["prepare"].get("draft_llm_calls") or 0) for row in cycles)
    annotation_calls = sum(
        int(row["prepare"].get("annotation_llm_calls") or 0) for row in cycles
    )
    repair_calls = sum(
        int(row["prepare"].get("repair_llm_calls") or 0)
        + int(row["execute"].get("repair_llm_calls") or 0)
        for row in cycles
    )
    domain_policy_cycle = next(
        (row for row in cycles if row.get("authoring_kind") == "domain_policy"),
        {},
    )
    domain_policy_llm_calls_zero = bool(domain_policy_cycle) and all(
        int((domain_policy_cycle.get(stage) or {}).get(counter) or 0) == 0
        for stage in ("prepare", "execute")
        for counter in ("draft_llm_calls", "annotation_llm_calls", "repair_llm_calls")
    )
    domain_cycle = next(
        (row for row in cycles if row.get("authoring_kind") == "domain"),
        {},
    )
    domain_grounding = (domain_cycle.get("prepare") or {}).get(
        "source_grounding_validation"
    ) or {}
    domain_proposal = (domain_cycle.get("prepare") or {}).get(
        "authoring_proposal_validation"
    ) or {}
    domain_split_proposals = (domain_cycle.get("prepare") or {}).get(
        "authoring_proposals_validation"
    ) or {}
    domain_freeform_contract = {
        "cycle_present": bool(domain_cycle),
        "freeform_mode_requested": domain_cycle.get("source_grounding_mode")
        == "freeform_llm",
        "blueprint_not_flow_input": domain_cycle.get("trusted_blueprint_configured")
        is False,
        "split_draft_llm_three": (domain_cycle.get("prepare") or {}).get(
            "draft_llm_calls"
        )
        == 3,
        "annotation_llm_zero": (domain_cycle.get("prepare") or {}).get(
            "annotation_llm_calls"
        )
        == 0,
        "repair_llm_zero": (domain_cycle.get("prepare") or {}).get(
            "repair_llm_calls"
        )
        == 0,
        "grounding_mode_evidenced": domain_grounding.get("mode") == "freeform_llm",
        "structured_proposal_sealed": len(
            str(domain_grounding.get("structured_proposal_sha256") or "")
        )
        == 64,
        "proposal_contract_exact": domain_proposal.get("proposal_contract_version")
        == "metadata.authoring.proposal.v1",
        "source_hash_exact": domain_proposal.get("source_sha256")
        == domain_bootstrap_sha256,
        "proposal_hash_sealed": len(
            str(domain_proposal.get("proposal_sha256") or "")
        )
        == 64,
        "draft_hash_sealed": len(str(domain_proposal.get("draft_sha256") or ""))
        == 64,
        "draft_hash_matches_grounding": domain_proposal.get("draft_sha256")
        == domain_grounding.get("structured_proposal_sha256"),
        "split_proposal_branches_exact": set(domain_split_proposals)
        == {"domain", "dataset", "main_filter"},
        "split_proposal_source_hashes_exact": all(
            (domain_split_proposals.get(branch) or {}).get("source_sha256")
            == source_hashes[branch]
            for branch in ("domain", "dataset", "main_filter")
        ),
        "split_proposal_hashes_sealed": all(
            len(
                str(
                    (domain_split_proposals.get(branch) or {}).get(
                        "proposal_sha256"
                    )
                    or ""
                )
            )
            == 64
            and len(
                str(
                    (domain_split_proposals.get(branch) or {}).get("draft_sha256")
                    or ""
                )
            )
            == 64
            for branch in ("domain", "dataset", "main_filter")
        ),
    }
    expected_calls = [
        _expected_prepare_llm_calls(
            kind,
            source_text,
            source_grounding_mode="freeform_llm",
            trusted_blueprint_configured=False,
        )
        for kind, _, source_text, _ in specs
    ]
    report = {
        "contract_version": "langflow.http.v6-authoring-analysis-e2e.validation.v2",
        "model": AUTHORING_GEMINI_MODEL,
        "model_contract": model_contract,
        "exact_gemini_no_fallback": exact_gemini_no_fallback,
        "domain_id": "manufacturing",
        "environment": environment,
        "fresh_environment": True,
        "source_hashes": source_hashes,
        "authoring_sources": authoring_sources,
        "domain_bootstrap_source_sha256": domain_bootstrap_sha256,
        "trusted_source_manifest": source_manifest_evidence,
        "approved_source_registry": approved_source_registry_evidence,
        "source_text_persisted": False,
        "trusted_blueprint_json_persisted": False,
        "provider_output_persisted": False,
        "approval_payload_persisted": False,
        "secrets_persisted": False,
        "flow_defaults": defaults,
        "flow_defaults_passed": defaults_ok,
        "imports": imports,
        "blueprint_trust": blueprint_trust,
        "blueprint_trust_checks": blueprint_trust_checks,
        "freeform_clarification_probe": clarification_probe,
        "cycles": cycles,
        "domain_bootstrap_checks": domain_bootstrap_checks,
        "domain_oracle_checks": domain_oracle_checks,
        "dataset_patch_checks": dataset_patch_checks,
        "cycle_order_exact": cycle_order_exact,
        "revision_chain_exact": revision_chain,
        "draft_llm_calls": draft_calls,
        "annotation_llm_calls": annotation_calls,
        "repair_llm_calls": repair_calls,
        "domain_policy_llm_calls_zero": domain_policy_llm_calls_zero,
        "domain_freeform_contract": domain_freeform_contract,
        "expected_llm_calls": {
            "draft": sum(item["draft"] for item in expected_calls),
            "annotation": sum(item["annotation"] for item in expected_calls),
            "repair": sum(item["repair"] for item in expected_calls),
        },
        "loader_roundtrip": loader,
        "loader_checks": loader_checks,
        "production_pointer": {
            "before": production_pointer_before,
            "after": production_pointer_after,
            "checks": production_pointer_checks,
            "passed": all(production_pointer_checks.values()),
        },
        "data_analysis_flow_sha256": sha256(DATA_ANALYSIS_FLOW_PATH.read_bytes()).hexdigest(),
        "data_analysis": data_analysis,
    }
    report["all_passed"] = (
        defaults_ok
        and exact_gemini_no_fallback
        and all(blueprint_trust_checks.values())
        and clarification_probe["passed"]
        and all(row["passed"] for row in cycles)
        and domain_bootstrap_checks["passed"]
        and domain_oracle_checks["passed"]
        and dataset_patch_checks["passed"]
        and cycle_order_exact
        and revision_chain
        and draft_calls == sum(item["draft"] for item in expected_calls)
        and annotation_calls == sum(item["annotation"] for item in expected_calls)
        and repair_calls == sum(item["repair"] for item in expected_calls)
        and domain_policy_llm_calls_zero
        and all(domain_freeform_contract.values())
        and all(loader_checks.values())
        and all(production_pointer_checks.values())
        and data_analysis.get("all_passed") is True
    )
    assert_secret_absent(report, gemini_key)
    assert_secret_absent(report, langflow_key)
    assert_secret_absent(report, mongo_uri)
    assert_secret_absent(
        report,
        json.dumps(trusted_blueprint, ensure_ascii=False, separators=(",", ":")),
    )
    assert_secret_absent(
        report,
        json.dumps(source_manifest, ensure_ascii=False, separators=(",", ":")),
    )
    assert_secret_absent(
        report,
        json.dumps(
            approved_source_registry,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    )
    for path in AUTHORING_INPUT_PATHS.values():
        assert_secret_absent(report, path.read_text(encoding="utf-8-sig"))
    for source_text in texts.values():
        assert_secret_absent(report, source_text)
    assert_secret_absent(report, domain_bootstrap_source)
    assert_secret_absent(report, FREEFORM_CLARIFICATION_PROBE)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-url", default="http://127.0.0.1:7873")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--environment-prefix", default="migration_validation")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs" / "langflow_http_migration_patches_e2e.json",
    )
    args = parser.parse_args()
    try:
        report = run(
            server_url=args.server_url,
            env_path=args.env_file.resolve(),
            environment_prefix=args.environment_prefix,
            timeout_seconds=max(60, min(args.timeout_seconds, 600)),
        )
    except Exception as exc:
        report = {
            "contract_version": "langflow.http.v6-authoring-analysis-e2e.validation.v2",
            "all_passed": False,
            "failure": _safe_failure(exc),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "model": report.get("model"),
                "environment": report.get("environment"),
                "cycles": len(report.get("cycles") or []),
                "all_passed": report.get("all_passed"),
                "failure": report.get("failure"),
            },
            ensure_ascii=False,
        )
    )
    print(f"report: {args.output}")
    return 0 if report.get("all_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
