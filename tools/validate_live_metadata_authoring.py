"""OBSOLETE DIAGNOSTIC: probe full-draft TXT -> Gemini variability.

This is deliberately not the v6 production authoring path.  Production uses a
trusted executable blueprint plus the annotation-only validator in
``validate_live_blueprint_authoring.py``.  This retained tool calls an external
model once and records why unconstrained full-draft generation is unsuitable;
provider payloads, prompts, source text and credentials are never persisted.
"""

from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import ContractError, sha256_json
from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    GeminiJsonModel,
    assert_secret_absent,
    gemini_model_contract_evidence,
    require_exact_gemini_model,
    resolve_gemini_api_key,
)


DEFAULT_SOURCES = {
    "domain": ROOT / "metadata" / "authoring" / "v6_inputs" / "domain_v6.txt",
    "dataset": ROOT / "metadata" / "authoring" / "v6_inputs" / "dataset_v6.txt",
    "main_filter": ROOT / "metadata" / "authoring" / "v6_inputs" / "main_filter_v6.txt",
}
AUTHORING_COMPONENT = ROOT / "langflow_components" / "metadata_authoring" / "00_metadata_authoring_engine.py"
DEFAULT_V2_SOURCE = ROOT / "validation" / "order_sales_metadata_input.txt"
AUTHORING_DRAFT_SCHEMA = ROOT / "contracts" / "schemas" / "metadata-authoring-draft.schema.json"
ORDER_SALES_EXPECTED_DRAFT = ROOT / "metadata" / "domain_packs" / "order_sales" / "authoring_draft.json"
_ALLOWED_FIELD_ROLES = {
    "filter", "group", "join", "compare", "aggregate", "derive",
    "project", "sort", "rank", "metric", "output",
}
_FIELD_ROLE_PROBE_CANDIDATES = {
    "aggregatable", "comparison", "compare_fields", "date", "dimension",
    "filterable", "group_by", "identifier", "join_key", "key", "measure",
    "order", "projection", "ranking",
}


class ReplayModel:
    """Local model shim used to replay one already-paid provider response."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def invoke(self, prompt: str) -> str:
        self.calls += 1
        return self.response


def _response_data(value: Any) -> dict[str, Any]:
    raw = getattr(value, "data", value)
    if not isinstance(raw, dict):
        raise RuntimeError("authoring_component_non_object_response")
    return raw


def _safe_failure(exc: BaseException) -> dict[str, Any]:
    if isinstance(exc, ContractError):
        details = exc.details if isinstance(exc.details, dict) else {}
        allowed = {
            "schema",
            "path",
            "reason",
            "section",
            "key",
            "item",
            "authoring_kind",
            "missing",
            "unexpected",
            "dataset_key",
            "field_key",
            "field",
            "metric_id",
            "metric",
            "relation_id",
            "recipe_id",
            "recipe",
            "left_dataset",
            "right_dataset",
            "code",
            "counts",
        }
        def bounded(value: Any, *, depth: int = 0) -> Any:
            if depth > 4:
                return "bounded"
            if isinstance(value, (int, float, bool, type(None))):
                return value
            if isinstance(value, str):
                return _safe_identifier(value)
            if isinstance(value, list):
                return [bounded(item, depth=depth + 1) for item in value[:32]]
            if isinstance(value, dict):
                return {
                    _safe_identifier(key): bounded(item, depth=depth + 1)
                    for key, item in list(sorted(value.items(), key=lambda pair: str(pair[0])))[:32]
                }
            return _safe_identifier(type(value).__name__)
        return {
            "code": str(exc.code),
            "stage": str(exc.stage),
            "message": str(exc.public_message)[:160],
            "safe_details": {
                str(key): bounded(value)
                for key, value in details.items()
                if str(key) in allowed
                and isinstance(value, (str, int, float, bool, type(None), list, dict))
            },
        }
    if type(exc).__name__ == "AuthoringSourceManifestError" and hasattr(exc, "code"):
        evidence = getattr(exc, "evidence", {})

        def manifest_value(value: Any, *, depth: int = 0) -> Any:
            if depth > 3:
                return "bounded"
            if isinstance(value, (int, float, bool, type(None))):
                return value
            if isinstance(value, str):
                return _safe_identifier(value)
            if isinstance(value, list):
                return [manifest_value(item, depth=depth + 1) for item in value[:32]]
            if isinstance(value, dict):
                return {
                    _safe_identifier(key): manifest_value(item, depth=depth + 1)
                    for key, item in list(sorted(value.items(), key=lambda pair: str(pair[0])))[:32]
                }
            return _safe_identifier(type(value).__name__)

        return {
            "code": str(getattr(exc, "code"))[:128],
            "stage": "metadata_source_normalization",
            "safe_details": manifest_value(evidence) if isinstance(evidence, dict) else {},
        }
    message = str(exc).splitlines()[0][:128]
    if message.startswith("gemini_") and all(ch.isalnum() or ch == "_" for ch in message):
        return {"code": message, "stage": "provider"}
    if message in {
        "authoring_draft_json_missing",
        "authoring_draft_json_invalid",
        "authoring_draft_not_object",
        "authoring_component_non_object_response",
        "authoring_component_method_missing",
        "authoring_component_contract_missing",
        "authoring_component_v2_prompt_missing",
    }:
        return {"code": message, "stage": "validation"}
    return {"code": f"validation_{type(exc).__name__}", "stage": "validation"}


def _load_component() -> tuple[type, dict[str, Any]]:
    from lfx.custom.eval import eval_custom_component_code

    source = AUTHORING_COMPONENT.read_text(encoding="utf-8")
    component_cls = eval_custom_component_code(source)
    method = getattr(component_cls, "run_authoring", None)
    if method is None:
        raise RuntimeError("authoring_component_method_missing")
    namespace = method.__globals__
    required = {"_authoring_prompt", "_json_object", "_validated_projection"}
    missing = sorted(name for name in required if not callable(namespace.get(name)))
    if missing:
        raise RuntimeError("authoring_component_contract_missing")
    return component_cls, namespace


def _json_object_text(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0].strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < start:
        raise RuntimeError("authoring_draft_json_missing")
    try:
        value = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        raise RuntimeError("authoring_draft_json_invalid") from None
    if not isinstance(value, dict):
        raise RuntimeError("authoring_draft_not_object")
    return value


def _safe_identifier(value: Any) -> str:
    """Keep bounded identifier-like values; hash everything else."""

    raw = str(value or "")
    if raw and len(raw) <= 96 and all(ch.isalnum() or ch in "_.:-" for ch in raw):
        return raw
    return f"sha256:{sha256(raw.encode('utf-8')).hexdigest()}"


def _draft_structure_evidence(draft: dict[str, Any]) -> dict[str, Any]:
    """Return bounded metadata IDs only, never source text or provider payloads."""

    datasets = draft.get("datasets") if isinstance(draft, dict) else None
    dataset_ids = sorted(_safe_identifier(value) for value in datasets) if isinstance(datasets, dict) else []
    dataset_registry = set(dataset_ids)
    dataset_field_registry = {
        _safe_identifier(dataset_id): {
            _safe_identifier(field_id)
            for field_id in ((dataset.get("fields") or {}) if isinstance(dataset, dict) else {})
        }
        for dataset_id, dataset in (datasets.items() if isinstance(datasets, dict) else [])
    }
    global_field_registry = set().union(*dataset_field_registry.values()) if dataset_field_registry else set()

    def global_field_refs(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        output = []
        for item in value[:32]:
            identifier = _safe_identifier(item)
            output.append(
                identifier
                if identifier in global_field_registry
                else f"sha256:{sha256(str(item).encode('utf-8')).hexdigest()}"
            )
        return output

    grains = draft.get("grains") if isinstance(draft, dict) else None
    grain_rows = []
    if isinstance(grains, dict):
        for grain_id, grain in sorted(grains.items(), key=lambda item: str(item[0]))[:64]:
            card = grain if isinstance(grain, dict) else {}
            grain_rows.append(
                {
                    "grain_id": _safe_identifier(grain_id),
                    "attribute_keys": sorted(_safe_identifier(key) for key in card)[:24],
                    "keys": global_field_refs(card.get("keys")),
                    "display_fields": global_field_refs(card.get("display_fields")),
                }
            )

    expected_draft: dict[str, Any] = {}
    if ORDER_SALES_EXPECTED_DRAFT.is_file():
        try:
            loaded_expected = json.loads(ORDER_SALES_EXPECTED_DRAFT.read_text(encoding="utf-8"))
            expected_draft = loaded_expected if isinstance(loaded_expected, dict) else {}
        except (OSError, json.JSONDecodeError):
            expected_draft = {}
    expected_ids = {
        section: set(map(str, expected_draft.get(section) or {}))
        for section in ("metrics", "relations", "grains", "recipes", "predicates", "orderings")
    }

    def registered_id(value: Any, registry: set[str]) -> str:
        raw = str(value or "")
        return raw if raw in registry else f"sha256:{sha256(raw.encode('utf-8')).hexdigest()}"

    metrics = draft.get("metrics") if isinstance(draft, dict) else None
    metric_rows = []
    if isinstance(metrics, dict):
        for metric_id, metric in sorted(metrics.items(), key=lambda item: str(item[0]))[:128]:
            card = metric if isinstance(metric, dict) else {}
            formula = card.get("formula") if isinstance(card.get("formula"), dict) else {}
            formula_refs = {
                key: registered_id(value, expected_ids["metrics"])
                for key, value in sorted(formula.items())
                if str(key).endswith("_metric") and isinstance(value, str)
            }
            source_binding = card.get("source_binding") if isinstance(card.get("source_binding"), dict) else {}
            metric_rows.append(
                {
                    "metric_id": registered_id(metric_id, expected_ids["metrics"]),
                    "attribute_keys": sorted(_safe_identifier(key) for key in card)[:32],
                    "aggregation": _safe_identifier(card.get("aggregation")),
                    "source_field": registered_id(card.get("source_field"), global_field_registry)
                    if card.get("source_field") is not None
                    else None,
                    "source_binding_keys": sorted(_safe_identifier(key) for key in source_binding)[:16],
                    "formula_keys": sorted(_safe_identifier(key) for key in formula)[:24],
                    "formula_op": _safe_identifier(formula.get("op")) if formula else None,
                    "formula_metric_refs": formula_refs,
                }
            )

    orderings = draft.get("orderings") if isinstance(draft, dict) else None
    ordering_rows = []
    if isinstance(orderings, dict):
        for ordering_id, ordering in sorted(orderings.items(), key=lambda item: str(item[0]))[:128]:
            card = ordering if isinstance(ordering, dict) else {}
            key_rows = []
            for key_card in (card.get("keys") if isinstance(card.get("keys"), list) else [])[:32]:
                item = key_card if isinstance(key_card, dict) else {}
                key_rows.append(
                    {
                        "field": registered_id(item.get("field"), global_field_registry),
                        "direction": _safe_identifier(item.get("direction")),
                        "nulls": _safe_identifier(item.get("nulls")),
                    }
                )
            ordering_rows.append(
                {
                    "ordering_id": registered_id(ordering_id, expected_ids["orderings"]),
                    "keys": key_rows,
                }
            )

    predicates = draft.get("predicates") if isinstance(draft, dict) else None
    predicate_rows = []
    if isinstance(predicates, dict):
        for predicate_id, predicate in sorted(predicates.items(), key=lambda item: str(item[0]))[:128]:
            card = predicate if isinstance(predicate, dict) else {}
            refs = {}
            for key, registry in (
                ("field", global_field_registry),
                ("target_field", global_field_registry),
                ("metric", expected_ids["metrics"]),
                ("metric_id", expected_ids["metrics"]),
                ("relation_id", expected_ids["relations"]),
                ("grain_id", expected_ids["grains"]),
                ("recipe_id", expected_ids["recipes"]),
            ):
                if isinstance(card.get(key), str):
                    refs[key] = registered_id(card[key], registry)
            predicate_rows.append(
                {
                    "predicate_id": registered_id(predicate_id, expected_ids["predicates"]),
                    "attribute_keys": sorted(_safe_identifier(key) for key in card)[:32],
                    "operator": _safe_identifier(card.get("operator")),
                    "refs": refs,
                }
            )

    def template_evidence(value: Any, output: dict[str, set[str]]) -> None:
        if isinstance(value, dict):
            if isinstance(value.get("op"), str):
                output["ops"].add(_safe_identifier(value["op"]))
            for key, registry, bucket in (
                ("relation_id", expected_ids["relations"], "relation_refs"),
                ("metric", expected_ids["metrics"], "metric_refs"),
                ("grain_id", expected_ids["grains"], "grain_refs"),
            ):
                if isinstance(value.get(key), str):
                    output[bucket].add(registered_id(value[key], registry))
            for key, registry, bucket in (
                ("metrics", expected_ids["metrics"], "metric_refs"),
                ("group_by", global_field_registry, "field_refs"),
                ("fields", global_field_registry, "field_refs"),
                ("allowed_fields", global_field_registry, "field_refs"),
                ("stable_tie_break", global_field_registry, "field_refs"),
            ):
                if isinstance(value.get(key), list):
                    output[bucket].update(registered_id(item, registry) for item in value[key][:64])
            for child in value.values():
                template_evidence(child, output)
        elif isinstance(value, list):
            for child in value[:64]:
                template_evidence(child, output)

    expected_slots = {
        str(slot)
        for recipe in (expected_draft.get("recipes") or {}).values()
        if isinstance(recipe, dict)
        for slot in (recipe.get("required_slots") or [])
    }
    recipes = draft.get("recipes") if isinstance(draft, dict) else None
    recipe_rows = []
    if isinstance(recipes, dict):
        for recipe_id, recipe in sorted(recipes.items(), key=lambda item: str(item[0]))[:128]:
            card = recipe if isinstance(recipe, dict) else {}
            refs = {key: set() for key in ("ops", "relation_refs", "metric_refs", "grain_refs", "field_refs")}
            template_evidence(card.get("default_operation_template"), refs)
            recipe_rows.append(
                {
                    "recipe_id": registered_id(recipe_id, expected_ids["recipes"]),
                    "required_slots": [
                        registered_id(slot, expected_slots)
                        for slot in (card.get("required_slots") if isinstance(card.get("required_slots"), list) else [])[:32]
                    ],
                    **{key: sorted(values) for key, values in refs.items()},
                }
            )

    role_candidate_hashes = {
        sha256(value.encode("utf-8")).hexdigest(): value
        for value in _FIELD_ROLE_PROBE_CANDIDATES
    }
    field_roles: list[dict[str, Any]] = []
    if isinstance(datasets, dict):
        for dataset_id, dataset in sorted(datasets.items(), key=lambda item: str(item[0]))[:32]:
            fields = dataset.get("fields") if isinstance(dataset, dict) else None
            if not isinstance(fields, dict):
                continue
            for field_id, field in sorted(fields.items(), key=lambda item: str(item[0]))[:64]:
                roles = field.get("roles") if isinstance(field, dict) else None
                role_rows = []
                if isinstance(roles, list):
                    for role in roles[:16]:
                        raw_role = str(role or "")
                        role_hash = sha256(raw_role.encode("utf-8")).hexdigest()
                        role_rows.append(
                            {
                                "allowed_role": raw_role if raw_role in _ALLOWED_FIELD_ROLES else None,
                                "role_sha256": role_hash,
                                "known_synonym_candidate": role_candidate_hashes.get(role_hash),
                            }
                        )
                field_roles.append(
                    {
                        "dataset_id": _safe_identifier(dataset_id),
                        "field_id": _safe_identifier(field_id),
                        "roles": role_rows,
                    }
                )

    def dataset_refs(value: Any, *, depth: int = 0) -> Any:
        if depth > 3:
            return "bounded"
        if isinstance(value, str):
            identifier = _safe_identifier(value)
            return identifier if identifier in dataset_registry else f"sha256:{sha256(value.encode('utf-8')).hexdigest()}"
        if isinstance(value, list):
            return [dataset_refs(item, depth=depth + 1) for item in value[:16]]
        if isinstance(value, dict):
            return {
                _safe_identifier(key): dataset_refs(item, depth=depth + 1)
                for key, item in list(sorted(value.items(), key=lambda pair: str(pair[0])))[:16]
            }
        if value is None:
            return None
        return _safe_identifier(type(value).__name__)

    def shape_only(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return {"type": "object", "keys": sorted(_safe_identifier(key) for key in value)[:24]}
        if isinstance(value, list):
            item_keys = [
                sorted(_safe_identifier(key) for key in item)[:24]
                for item in value[:8]
                if isinstance(item, dict)
            ]
            return {"type": "array", "length": len(value), "item_keys": item_keys}
        return {"type": type(value).__name__}

    def relation_keys(value: Any, dataset_id: Any) -> list[str]:
        registered = dataset_field_registry.get(_safe_identifier(dataset_id), set())
        if not isinstance(value, list):
            return []
        output = []
        for item in value[:16]:
            identifier = _safe_identifier(item)
            output.append(
                identifier
                if identifier in registered
                else f"sha256:{sha256(str(item).encode('utf-8')).hexdigest()}"
            )
        return output

    relations = draft.get("relations") if isinstance(draft, dict) else None
    relation_rows: list[dict[str, Any]] = []
    if isinstance(relations, dict):
        for relation_id, relation in sorted(relations.items(), key=lambda item: str(item[0]))[:64]:
            row = relation if isinstance(relation, dict) else {}
            endpoint_candidates = {
                key: dataset_refs(row.get(key))
                for key in ("left", "right", "from_dataset", "to_dataset", "datasets", "endpoints")
                if key in row
            }
            relation_rows.append(
                {
                    "relation_id": _safe_identifier(relation_id),
                    "left_dataset": dataset_refs(row.get("left_dataset")),
                    "right_dataset": dataset_refs(row.get("right_dataset")),
                    "left_keys": relation_keys(row.get("left_keys"), row.get("left_dataset")),
                    "right_keys": relation_keys(row.get("right_keys"), row.get("right_dataset")),
                    "join_type": _safe_identifier(row.get("join_type")),
                    "cardinality": _safe_identifier(row.get("cardinality")),
                    "null_key_policy": _safe_identifier(row.get("null_key_policy")),
                    "multi_match_policy": _safe_identifier(row.get("multi_match_policy")),
                    "attribute_keys": sorted(_safe_identifier(key) for key in row)[:24],
                    "endpoint_candidates": endpoint_candidates,
                    "key_mappings_shape": shape_only(row.get("key_mappings")) if "key_mappings" in row else None,
                    "on_shape": shape_only(row.get("on")) if "on" in row else None,
                }
            )
    return {
        "dataset_ids": dataset_ids[:32],
        "dataset_count": len(dataset_ids),
        "dataset_ids_truncated": max(0, len(dataset_ids) - 32),
        "field_roles": field_roles[:256],
        "field_roles_truncated": max(0, len(field_roles) - 256),
        "grains": grain_rows,
        "grain_count": len(grains) if isinstance(grains, dict) else 0,
        "metrics": metric_rows,
        "metric_count": len(metrics) if isinstance(metrics, dict) else 0,
        "orderings": ordering_rows,
        "ordering_count": len(orderings) if isinstance(orderings, dict) else 0,
        "predicates": predicate_rows,
        "predicate_count": len(predicates) if isinstance(predicates, dict) else 0,
        "recipes": recipe_rows,
        "recipe_count": len(recipes) if isinstance(recipes, dict) else 0,
        "relations": relation_rows,
        "relation_count": len(relations) if isinstance(relations, dict) else 0,
        "relations_truncated": max(0, len(relations) - 64) if isinstance(relations, dict) else 0,
    }


def _executable_structure_diff(actual: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    """Compare executable registries using only counts, IDs and content hashes."""

    def strip_annotations(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                str(key): strip_annotations(item)
                for key, item in value.items()
                if str(key) not in {"aliases", "description", "display_name", "label", "summary", "notes"}
            }
        if isinstance(value, list):
            return [strip_annotations(item) for item in value]
        return value

    def metric_projection(card: Any) -> Any:
        value = card if isinstance(card, dict) else {}
        formula = value.get("formula") if isinstance(value.get("formula"), dict) else None
        source_binding = value.get("source_binding") if isinstance(value.get("source_binding"), dict) else None
        return {
            "source_field": value.get("source_field"),
            "source_binding": strip_annotations(source_binding) if source_binding else None,
            "aggregation": value.get("aggregation"),
            "additivity": strip_annotations(value.get("additivity")),
            "formula": strip_annotations(formula) if formula else None,
            "unit": value.get("unit"),
        }

    def alias_projection(card: Any) -> Any:
        value = card if isinstance(card, dict) else {}
        return {"target_type": value.get("target_type"), "target_key": value.get("target_key")}

    projectors = {
        "grains": strip_annotations,
        "metrics": metric_projection,
        "predicates": strip_annotations,
        "entity_groups": strip_annotations,
        "recipes": strip_annotations,
        "aliases": alias_projection,
    }
    sections: dict[str, Any] = {}
    for section, projector in projectors.items():
        expected_cards = expected.get(section) if isinstance(expected.get(section), dict) else {}
        actual_cards = actual.get(section) if isinstance(actual.get(section), dict) else {}
        expected_ids = set(map(str, expected_cards))
        actual_ids = set(map(str, actual_cards))
        common_ids = expected_ids & actual_ids
        expected_projection = {
            key: projector(expected_cards[key])
            for key in sorted(expected_ids)
        }
        actual_projection = {
            key: projector(actual_cards[key])
            for key in sorted(actual_ids)
        }
        mismatched = [
            key
            for key in sorted(common_ids)
            if sha256_json(expected_projection[key]) != sha256_json(actual_projection[key])
        ]
        sections[section] = {
            "expected_count": len(expected_ids),
            "actual_count": len(actual_ids),
            "missing_ids": sorted(expected_ids - actual_ids)[:64],
            "unexpected_id_sha256": [
                sha256(str(key).encode("utf-8")).hexdigest()
                for key in sorted(actual_ids - expected_ids)[:64]
            ],
            "mismatched_ids": mismatched[:64],
            "expected_sha256": sha256_json(expected_projection),
            "actual_sha256": sha256_json(actual_projection),
        }
    return {
        "contract_version": "authoring.executable-structure-diff.v1",
        "sections": sections,
        "all_exact": all(
            not row["missing_ids"]
            and not row["unexpected_id_sha256"]
            and not row["mismatched_ids"]
            for row in sections.values()
        ),
    }


def _v2_prompt(source_text: str) -> str:
    """Build the exact standalone Flow prompt, including deterministic inventory."""

    from lfx.custom.eval import eval_custom_component_code
    from reference_runtime.authoring_source_manifest import extract_authoring_source_manifest

    source = AUTHORING_COMPONENT.read_text(encoding="utf-8")
    component_cls = eval_custom_component_code(source)
    namespace = component_cls.run_authoring.__globals__
    prompt_builder = namespace.get("_v2_authoring_prompt")
    if not callable(prompt_builder):
        raise RuntimeError("authoring_component_v2_prompt_missing")
    manifest = extract_authoring_source_manifest(source_text)
    return str(prompt_builder(source_text, "domain", manifest))


def _v2_supported_operations() -> tuple[str, ...]:
    """Read the exact operation allowlist embedded in the standalone Flow node."""

    from lfx.custom.eval import eval_custom_component_code

    source = AUTHORING_COMPONENT.read_text(encoding="utf-8")
    component_cls = eval_custom_component_code(source)
    values = component_cls.run_authoring.__globals__.get("AUTHORING_SUPPORTED_OPERATIONS", ())
    return tuple(str(value) for value in values)


def _component_v2_replay(
    raw_response: str,
    source_text: str,
    draft: dict[str, Any],
    *,
    domain_id: str,
    environment: str,
    revision: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replay through the embedded v2 compiler and, when exposed, prepare node."""

    from lfx.custom.eval import eval_custom_component_code

    source = AUTHORING_COMPONENT.read_text(encoding="utf-8")
    component_cls = eval_custom_component_code(source)
    namespace = component_cls.run_authoring.__globals__
    embedded_compile = namespace.get("compile_domain_package")
    if not callable(embedded_compile):
        return {}, {"available": False, "prepare_invoked": False, "replay_calls": 0}
    embedded = embedded_compile(
        draft,
        domain_id,
        environment,
        revision=revision,
        lifecycle_status="validated",
    )
    input_names = {str(item.name) for item in getattr(component_cls, "inputs", [])}
    prepare_response: dict[str, Any] = {}
    replay = ReplayModel(raw_response)
    if {"domain_id", "environment"} <= input_names:
        from lfx.schema.message import Message

        component = component_cls()
        component.input_message = Message(text=source_text, session_id=f"live-authoring-{domain_id}")
        component.language_model = replay
        component.mode = "prepare"
        component.dry_run = True
        component.domain_id = domain_id
        component.environment = environment
        if "revision" in input_names:
            component.revision = revision
        component.candidate_ttl_seconds = 3600
        prepare_response = _response_data(component.run_authoring())
    return embedded, {
        "available": True,
        "prepare_invoked": bool(prepare_response),
        "replay_calls": replay.calls,
        "prepare_status": prepare_response.get("status"),
        "prepare_stage": prepare_response.get("stage"),
        "candidate_id": prepare_response.get("candidate_id"),
        "candidate_sha256": prepare_response.get("candidate_sha256"),
        "package_sha256": prepare_response.get("package_sha256"),
        "bundle_sha256": prepare_response.get("bundle_sha256"),
        "catalog_sha256": prepare_response.get("catalog_sha256"),
        "llm_usage": prepare_response.get("llm_usage"),
    }


def validate_domain_source(
    source_path: Path,
    *,
    api_key: str,
    model: str,
    timeout_seconds: int,
    domain_id: str,
    environment: str,
    revision: int,
) -> dict[str, Any]:
    from reference_runtime.domain_packages import (
        build_runtime_catalog_v2,
        compile_domain_package,
        make_active_pointer_document,
        make_bundle_document,
        validate_domain_package,
        validate_runtime_catalog_v2,
    )
    from reference_runtime.authoring_source_manifest import (
        AuthoringSourceManifestError,
        extract_authoring_source_manifest,
        normalize_draft_alias_shorthand,
        validate_draft_inventory_coverage,
    )

    source_text = source_path.read_text(encoding="utf-8-sig")
    source_bytes = source_text.encode("utf-8")
    provider = GeminiJsonModel(
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
        max_output_tokens=32768,
    )
    row: dict[str, Any] = {
        "domain_id": domain_id,
        "environment": environment,
        "revision": revision,
        "source_file": source_path.relative_to(ROOT).as_posix() if source_path.is_relative_to(ROOT) else source_path.name,
        "source_bytes": len(source_bytes),
        "source_sha256": sha256(source_bytes).hexdigest(),
        "expected_provider_calls": 1,
        "expected_repair_calls": 0,
    }
    draft_structure: dict[str, Any] | None = None
    structural_diff: dict[str, Any] | None = None
    try:
        raw_response = provider.invoke(_v2_prompt(source_text))
        provider_draft = _json_object_text(raw_response)
        draft_structure = _draft_structure_evidence(provider_draft)
        source_manifest = extract_authoring_source_manifest(source_text)
        draft = normalize_draft_alias_shorthand(source_manifest, provider_draft)
        draft_structure = _draft_structure_evidence(draft)
        if domain_id == "order_sales" and ORDER_SALES_EXPECTED_DRAFT.is_file():
            expected_draft = json.loads(ORDER_SALES_EXPECTED_DRAFT.read_text(encoding="utf-8"))
            structural_diff = _executable_structure_diff(draft, expected_draft)
        alias_normalization_applied = sha256_json(provider_draft) != sha256_json(draft)
        try:
            source_coverage = validate_draft_inventory_coverage(
                source_manifest,
                draft,
                supported_operations=_v2_supported_operations(),
            )
        except AuthoringSourceManifestError as exc:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_coverage",
                "Compiled metadata does not cover the explicit source inventory.",
                dict(exc.evidence),
            ) from exc
        package = validate_domain_package(
            compile_domain_package(
                draft,
                domain_id,
                environment,
                revision=revision,
                lifecycle_status="validated",
            )
        )
        catalog = validate_runtime_catalog_v2(build_runtime_catalog_v2(package))
        bundle_document = make_bundle_document(package)
        active_pointer = make_active_pointer_document(package)
        embedded, replay = _component_v2_replay(
            raw_response,
            source_text,
            draft,
            domain_id=domain_id,
            environment=environment,
            revision=revision,
        )
        provider_evidence = provider.evidence()
        checks = {
            "provider_call_exact": provider.calls == 1,
            "provider_model_versions_exact": provider_evidence.get(
                "provider_model_versions_exact", True
            )
            is True,
            "draft_contract_v1": draft.get("contract_version") == "metadata.authoring.draft.v1",
            "source_manifest_sealed": source_manifest.get("contract_version")
            == "metadata.authoring.source-manifest.v1"
            and bool(source_manifest.get("manifest_sha256")),
            "source_inventory_covered": source_coverage.get("passed") is True,
            "domain_package_v1": package.get("contract_version") == "domain.package.v1",
            "runtime_catalog_v2": catalog.get("contract_version") == "metadata.runtime.catalog.v2",
            "identity_pinned": package.get("domain_id") == domain_id
            and package.get("environment") == environment
            and package.get("revision") == revision
            and catalog.get("domain_id") == domain_id
            and catalog.get("environment") == environment,
            "bundle_hash_pinned": bundle_document.get("bundle_sha256") == package.get("bundle_sha256"),
            "active_pointer_pinned": active_pointer.get("bundle_sha256") == package.get("bundle_sha256")
            and active_pointer.get("package_sha256") == package.get("package_sha256"),
            "standalone_v2_compiler_available": replay.get("available") is True,
            "standalone_compile_parity": bool(embedded)
            and embedded.get("package_sha256") == package.get("package_sha256")
            and embedded.get("bundle_sha256") == package.get("bundle_sha256"),
            "standalone_prepare_replayed": replay.get("prepare_invoked") is True
            and replay.get("replay_calls") == 1
            and replay.get("prepare_status") == "ok"
            and replay.get("prepare_stage") == "prepared",
            "no_repair": replay.get("llm_usage") in (
                None,
                {"draft_llm_calls": 1, "repair_llm_calls": 0},
            ),
        }
        row.update(
            {
                "passed": all(checks.values()),
                "checks": checks,
                "authoring_sha256": package.get("authoring_sha256"),
                "package_sha256": package.get("package_sha256"),
                "bundle_sha256": package.get("bundle_sha256"),
                "catalog_sha256": catalog.get("catalog_sha256"),
                "counts": {
                    key: len(catalog.get(key) or {})
                    for key in ("datasets", "fields", "metrics", "relations", "recipes", "aliases")
                },
                "standalone_replay": replay,
                "alias_shorthand_normalized": alias_normalization_applied,
                "source_manifest_sha256": source_manifest.get("manifest_sha256"),
                "source_coverage_sha256": sha256_json(source_coverage),
                "provider": provider_evidence,
                "executable_structure_diff": structural_diff,
            }
        )
    except Exception as exc:
        row.update({"passed": False, "failure": _safe_failure(exc), "provider": provider.evidence()})
        if draft_structure is not None:
            row["normalized_draft_structure"] = draft_structure
        if structural_diff is not None:
            row["executable_structure_diff"] = structural_diff
    assert_secret_absent(row, api_key)
    return row


def run_v2(
    source_path: Path,
    *,
    env_path: Path,
    model: str,
    timeout_seconds: int,
    domain_id: str,
    environment: str,
    revision: int,
) -> dict[str, Any]:
    model = require_exact_gemini_model(model)
    api_key = resolve_gemini_api_key(env_path)
    row = validate_domain_source(
        source_path.resolve(),
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
        domain_id=domain_id,
        environment=environment,
        revision=revision,
    )
    report = {
        "contract_version": "live.metadata.domain-package.validation.v2",
        "model": model,
        "model_contract": gemini_model_contract_evidence(model),
        "execution_mode": "obsolete_full_draft_diagnostic",
        "production_authoring_path": False,
        "replacement_validator": "tools/validate_live_blueprint_authoring.py",
        "provider_payloads_persisted": False,
        "source_text_persisted": False,
        "case_count": 1,
        "passed": 1 if row.get("passed") is True else 0,
        "failed": 0 if row.get("passed") is True else 1,
        "provider_calls": int((row.get("provider") or {}).get("calls") or 0),
        "repair_llm_calls": 0,
        "rows": [row],
    }
    assert_secret_absent(report, api_key)
    return report


def validate_source(
    kind: str,
    source_path: Path,
    *,
    api_key: str,
    model: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    source_text = source_path.read_text(encoding="utf-8-sig")
    source_bytes = source_text.encode("utf-8")
    component_cls, namespace = _load_component()
    provider = GeminiJsonModel(
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
        max_output_tokens=16384,
    )
    row: dict[str, Any] = {
        "authoring_kind": kind,
        "source_file": source_path.relative_to(ROOT).as_posix() if source_path.is_relative_to(ROOT) else source_path.name,
        "source_bytes": len(source_bytes),
        "source_sha256": sha256(source_bytes).hexdigest(),
        "expected_provider_calls": 1,
        "expected_repair_calls": 0,
    }
    try:
        from lfx.schema.message import Message

        prompt = namespace["_authoring_prompt"](kind, source_text)
        raw_response = provider.invoke(prompt)
        draft = namespace["_json_object"](raw_response)
        compiled = namespace["_validated_projection"](kind, draft, source_text)

        replay = ReplayModel(raw_response)
        component = component_cls()
        component.input_message = Message(text=source_text, session_id=f"live-authoring-{kind}")
        component.language_model = replay
        component.authoring_kind = kind
        component.mode = "prepare"
        component.dry_run = True
        component.candidate_ttl_seconds = 3600
        component_response = _response_data(component.run_authoring())

        provider_evidence = provider.evidence()
        checks = {
            "provider_call_exact": provider.calls == 1,
            "provider_model_versions_exact": provider_evidence.get(
                "provider_model_versions_exact", True
            )
            is True,
            "replay_call_exact": replay.calls == 1,
            "component_prepared": component_response.get("status") == "ok"
            and component_response.get("stage") == "prepared",
            "component_one_draft_no_repair": component_response.get("llm_usage")
            == {"draft_llm_calls": 1, "repair_llm_calls": 0},
            "candidate_content_addressed": component_response.get("candidate_id")
            == f"candidate:{component_response.get('candidate_sha256')}",
            "compiled_v6": compiled.get("schema_version") == "metadata.v6",
            "source_hash_bound": compiled.get("source_text_sha256") == row["source_sha256"],
        }
        row.update(
            {
                "passed": all(checks.values()),
                "checks": checks,
                "record_count": len(compiled.get("records") or []),
                "record_kinds": sorted(
                    {str(item.get("kind")) for item in compiled.get("records", []) if isinstance(item, dict)}
                ),
                "compiled_candidate_sha256": sha256_json(compiled),
                "projected_catalog_sha256": compiled.get("projected_catalog_sha256"),
                "candidate_id": component_response.get("candidate_id"),
                "candidate_sha256": component_response.get("candidate_sha256"),
                "persisted": component_response.get("persisted"),
                "provider": provider_evidence,
            }
        )
    except Exception as exc:
        row.update(
            {
                "passed": False,
                "failure": _safe_failure(exc),
                "provider": provider.evidence(),
            }
        )
    assert_secret_absent(row, api_key)
    return row


def run(
    sources: dict[str, Path],
    *,
    env_path: Path,
    model: str = DEFAULT_GEMINI_MODEL,
    timeout_seconds: int = 90,
) -> dict[str, Any]:
    model = require_exact_gemini_model(model)
    api_key = resolve_gemini_api_key(env_path)
    rows = [
        validate_source(
            kind,
            path.resolve(),
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
        )
        for kind, path in sources.items()
    ]
    report = {
        "contract_version": "live.metadata.authoring.validation.v1",
        "model": model,
        "model_contract": gemini_model_contract_evidence(model),
        "execution_mode": "component_dry_run",
        "provider_payloads_persisted": False,
        "source_text_persisted": False,
        "case_count": len(rows),
        "passed": sum(1 for row in rows if row.get("passed") is True),
        "failed": sum(1 for row in rows if row.get("passed") is not True),
        "provider_calls": sum(int((row.get("provider") or {}).get("calls") or 0) for row in rows),
        "repair_llm_calls": 0,
        "rows": rows,
    }
    assert_secret_absent(report, api_key)
    return report


def _source_args(values: list[str]) -> dict[str, Path]:
    if not values:
        return dict(DEFAULT_SOURCES)
    parsed: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit("--source must use KIND=PATH")
        kind, raw_path = value.split("=", 1)
        kind = kind.strip()
        if kind not in {"domain", "dataset", "main_filter"} or kind in parsed:
            raise SystemExit("--source KIND must be one unique domain|dataset|main_filter")
        parsed[kind] = Path(raw_path).expanduser()
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_V2_SOURCE)
    parser.add_argument("--domain-id", default="order_sales")
    parser.add_argument("--environment", default="test")
    parser.add_argument("--revision", type=int, default=1)
    parser.add_argument("--model", default=DEFAULT_GEMINI_MODEL)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs" / "live_metadata_authoring.json",
    )
    args = parser.parse_args()
    report = run_v2(
        args.source,
        env_path=args.env_file,
        model=args.model,
        timeout_seconds=args.timeout_seconds,
        domain_id=args.domain_id,
        environment=args.environment,
        revision=args.revision,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: report[key] for key in ("model", "case_count", "passed", "failed", "provider_calls")},
            ensure_ascii=False,
        )
    )
    print(f"report: {args.output}")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
