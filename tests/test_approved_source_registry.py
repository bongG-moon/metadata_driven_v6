from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from reference_runtime.domain_packages import compile_domain_package
from tools.build_approved_source_registry import (
    RegistryBuildError,
    _pretty_json_bytes,
    build_approved_source_registry,
    rebuild_registry,
)


ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = ROOT / "metadata" / "domain_packs" / "manufacturing"
REGISTRY_PATH = DOMAIN_ROOT / "approved_source_registry.json"
CATALOG_PATH = DOMAIN_ROOT / "compiled" / "runtime_catalog.v2.json"
EXCLUSIONS_PATH = DOMAIN_ROOT / "source_registry_exclusions.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _inputs() -> tuple[dict, dict, dict]:
    return _load(REGISTRY_PATH), _load(CATALOG_PATH), _load(EXCLUSIONS_PATH)


def _build() -> dict:
    registry, catalog, exclusions = _inputs()
    return build_approved_source_registry(registry, catalog, exclusions)


def _reverse_object(value: dict) -> dict:
    return {key: value[key] for key in reversed(list(value))}


def _sha256_json(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _reseal_blueprint(value: dict) -> dict:
    candidate = deepcopy(value)
    candidate["executable_sha256"] = _sha256_json(candidate["executable"])
    candidate["blueprint_sha256"] = _sha256_json(
        {key: item for key, item in candidate.items() if key != "blueprint_sha256"}
    )
    return candidate


def test_semantic_vocabulary_is_closed_bounded_and_contains_no_execution_metadata() -> None:
    rebuilt = _build()
    vocabulary = rebuilt["semantic_vocabulary"]

    assert set(rebuilt) == {
        "contract_version",
        "domain_id",
        "datasets",
        "semantic_templates",
        "semantic_templates_sha256",
        "semantic_templates_blueprint_sha256",
        "semantic_templates_executable_sha256",
        "semantic_templates_projection_sha256",
        "semantic_vocabulary",
    }
    assert rebuilt["contract_version"] == "metadata.authoring.source-registry.v3"
    assert set(vocabulary) == {
        "contract_version",
        "datasets",
        "fields",
        "metrics",
        "relations",
        "grains",
        "orderings",
        "predicates",
        "recipes",
        "entity_groups",
    }
    assert vocabulary["contract_version"] == "metadata.authoring.semantic-vocabulary.v1"
    assert 1 <= len(vocabulary["datasets"]) <= 128
    assert 1 <= len(vocabulary["fields"]) <= 2048
    assert 1 <= len(vocabulary["metrics"]) <= 1024
    compact_vocabulary = json.dumps(
        vocabulary,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    assert len(compact_vocabulary) <= 64 * 1024
    assert all(set(item) == {"id", "family", "labels"} for item in vocabulary["datasets"])
    assert all(set(item) == {"id", "families", "labels"} for item in vocabulary["fields"])
    assert all(set(item) == {"id", "labels"} for item in vocabulary["metrics"])
    for section in (
        "relations",
        "grains",
        "orderings",
        "predicates",
        "recipes",
        "entity_groups",
    ):
        assert all(set(item) == {"id", "labels"} for item in vocabulary[section])
    assert [item["id"] for item in vocabulary["datasets"]] == sorted(
        item["id"] for item in vocabulary["datasets"]
    )
    assert [item["id"] for item in vocabulary["fields"]] == sorted(
        item["id"] for item in vocabulary["fields"]
    )
    assert [item["id"] for item in vocabulary["metrics"]] == sorted(
        item["id"] for item in vocabulary["metrics"]
    )
    for collection in (
        "datasets",
        "fields",
        "metrics",
        "relations",
        "grains",
        "orderings",
        "predicates",
        "recipes",
        "entity_groups",
    ):
        assert [item["id"] for item in vocabulary[collection]] == sorted(
            item["id"] for item in vocabulary[collection]
        )
        for item in vocabulary[collection]:
            assert item["labels"]
            assert len(item["labels"]) <= 128
            assert all(
                len(label) <= 256 and len(label.encode("utf-8")) <= 1024
                for label in item["labels"]
            )
            assert item["labels"] == sorted(
                item["labels"], key=lambda label: (" ".join(label.split()).casefold(), label)
            )
            assert len({" ".join(label.split()).casefold() for label in item["labels"]}) == len(
                item["labels"]
            )
    assert all(item["families"] == sorted(set(item["families"])) for item in vocabulary["fields"])

    serialized = json.dumps(vocabulary, ensure_ascii=False, sort_keys=True).casefold()
    for forbidden in (
        "source_type",
        "source_adapter",
        "config_ref",
        "query_ref",
        "source_binding",
        "physical_column",
        "physical_aliases",
        "semantic_type",
        "coercion",
        "nullable",
        "required_in_source",
        "formula",
        "temporal_contract",
    ):
        assert forbidden not in serialized


def test_semantic_templates_are_closed_bounded_and_compiler_only() -> None:
    rebuilt = _build()
    templates = rebuilt["semantic_templates"]

    assert set(templates) == {
        "contract_version",
        "locale",
        "timezone",
        "planner_policy",
        "metrics",
        "relations",
        "entity_groups",
        "grains",
        "orderings",
        "predicates",
        "recipes",
        "aliases",
    }
    assert templates["contract_version"] == "metadata.authoring.semantic-templates.v1"
    assert templates["locale"] == "ko-KR"
    assert templates["timezone"] == "Asia/Seoul"
    assert templates["planner_policy"] == {
        "legacy_catalog_sha256": "6d2c9eaf3a10be1023a5c7aa52c796d5f0caf7287237a488ce38e68840b0e16f",
        "planner_profile": "legacy_v1_compat",
    }
    compact = json.dumps(
        templates,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    assert len(compact) <= 128 * 1024

    identities = {
        "metrics": "metric_id",
        "relations": "relation_id",
        "entity_groups": "group_id",
        "grains": "grain_id",
        "orderings": "ordering_id",
        "predicates": "predicate_id",
        "recipes": "recipe_id",
    }
    for section, identity_key in identities.items():
        assert list(templates[section]) == sorted(templates[section])
        assert all(identity_key not in card for card in templates[section].values())

    input_binding = templates["metrics"]["INPUT_QTY"]["source_binding"]
    assert set(input_binding) == {"dataset_family", "field", "fixed_filters"}
    assert input_binding["dataset_family"] == "production"
    assert input_binding["field"] == "PRODUCTION_QTY"
    assert input_binding["fixed_filters"] == [
        {
            "field": "OPER_NAME",
            "operator": "eq",
            "semantic_type": "string",
            "value": "INPUT",
        }
    ]

    assert len(templates["aliases"]) == 141
    assert sum(key.startswith("status:") for key in templates["aliases"]) == 3
    assert all(set(card) == {
        "conflict",
        "match",
        "normalization",
        "provenance_source",
        "target_key",
        "target_type",
        "values",
    } for card in templates["aliases"].values())

    serialized = json.dumps(templates, ensure_ascii=False, sort_keys=True).casefold()
    for forbidden in (
        "source_type",
        "source_adapter",
        "config_ref",
        "query_ref",
        "physical_column",
        "coercion",
        "credential",
        "http://",
        "https://",
        "mongodb://",
        "mongodb+srv://",
    ):
        assert forbidden not in serialized
    assert "source_binding" in serialized
    assert rebuilt["semantic_templates_sha256"] == hashlib.sha256(compact).hexdigest()
    blueprint = _load(DOMAIN_ROOT / "trusted_executable_blueprint.json")
    assert rebuilt["semantic_templates_blueprint_sha256"] == blueprint["blueprint_sha256"]
    assert rebuilt["semantic_templates_executable_sha256"] == blueprint["executable_sha256"]
    assert len(rebuilt["semantic_templates_projection_sha256"]) == 64


def test_semantic_templates_are_blueprint_sourced_and_runtime_exact() -> None:
    registry, catalog, exclusions = _inputs()
    blueprint = _load(DOMAIN_ROOT / "trusted_executable_blueprint.json")
    rebuilt = build_approved_source_registry(registry, catalog, exclusions, blueprint)
    templates = rebuilt["semantic_templates"]

    for section, identity_key in {
        "metrics": "metric_id",
        "relations": "relation_id",
        "entity_groups": "group_id",
        "grains": "grain_id",
        "orderings": "ordering_id",
        "predicates": "predicate_id",
        "recipes": "recipe_id",
    }.items():
        expected = deepcopy(blueprint["executable"][section])
        assert templates[section] == expected
        assert all(identity_key not in card for card in templates[section].values())
        compiled_without_identity = {
            entry_id: {
                key: value
                for key, value in catalog[section][entry_id].items()
                if key != identity_key
            }
            for entry_id in catalog[section]
        }
        assert compiled_without_identity == expected

    assert templates["aliases"] == blueprint["executable"]["aliases"]

    tampered = deepcopy(blueprint)
    tampered["executable"]["metrics"]["WIP_QTY"]["unit"] = "tampered-unit"
    with pytest.raises(RegistryBuildError, match="executable hash mismatch"):
        build_approved_source_registry(registry, catalog, exclusions, tampered)

    resealed = _reseal_blueprint(tampered)
    with pytest.raises(RegistryBuildError, match="template mismatch"):
        build_approved_source_registry(registry, catalog, exclusions, resealed)


def test_semantic_templates_compile_with_the_sealed_legacy_planner_policy() -> None:
    registry, catalog, exclusions = _inputs()
    blueprint = _load(DOMAIN_ROOT / "trusted_executable_blueprint.json")
    templates = build_approved_source_registry(
        registry,
        catalog,
        exclusions,
        blueprint,
    )["semantic_templates"]
    draft = deepcopy(blueprint["executable"])
    for section in (
        "metrics",
        "relations",
        "entity_groups",
        "grains",
        "orderings",
        "predicates",
        "recipes",
        "aliases",
    ):
        draft[section] = deepcopy(templates[section])
    draft["locale"] = templates["locale"]
    draft["timezone"] = templates["timezone"]
    draft["output_profile"] = deepcopy(templates["planner_policy"])
    draft.update(deepcopy(blueprint["default_annotations"]))

    compiled = compile_domain_package(draft, "manufacturing", "production")
    runtime = compiled["runtime_catalog"]
    assert runtime["output_profile"] == templates["planner_policy"]
    assert runtime["aliases"] == catalog["aliases"]
    for section in (
        "metrics",
        "relations",
        "entity_groups",
        "grains",
        "orderings",
        "predicates",
        "recipes",
    ):
        assert runtime[section] == catalog[section]


def test_dataset_templates_are_blueprint_sourced_closed_and_hash_pinned() -> None:
    rebuilt = _build()
    blueprint = _load(DOMAIN_ROOT / "trusted_executable_blueprint.json")
    _, catalog, _ = _inputs()
    allowed_template_keys = {
        "date_filter_contract",
        "date_policy",
        "default_detail_fields",
        "display_name",
        "fixture_only",
        "parameters",
        "read_policy",
        "time_scope",
        "upstream_bindings",
    }
    excluded_keys = {
        "fields",
        "family",
        "source_type",
        "source_adapter",
        "config_ref",
        "query_ref",
    }
    expected_registry_card_keys = {
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

    templates = {}
    for dataset_id, registry_card in rebuilt["datasets"].items():
        assert set(registry_card) == expected_registry_card_keys
        template = registry_card["dataset_template"]
        templates[dataset_id] = template
        assert set(template) <= allowed_template_keys
        assert excluded_keys.isdisjoint(template)
        assert registry_card["dataset_template_sha256"] == _sha256_json(template)
        expected = {
            key: value
            for key, value in blueprint["executable"]["datasets"][dataset_id].items()
            if key in allowed_template_keys
        }
        assert template == expected
        compiled = {
            key: value
            for key, value in catalog["datasets"][dataset_id].items()
            if key in allowed_template_keys
        }
        assert template == compiled
        assert set(template["default_detail_fields"]) <= set(
            registry_card["field_descriptors"]
        )
        assert template["read_policy"]["read_only"] is True

    compact = json.dumps(
        templates,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    assert len(compact) <= 64 * 1024
    assert "PROD_QTY" in rebuilt["datasets"]["lot_status"]["dataset_template"][
        "default_detail_fields"
    ]
    assert "ORG" not in rebuilt["datasets"]["target"]["dataset_template"][
        "default_detail_fields"
    ]


def test_dataset_template_drift_is_rejected_or_rebuilt_from_trusted_blueprint() -> None:
    registry, catalog, exclusions = _inputs()
    blueprint = _load(DOMAIN_ROOT / "trusted_executable_blueprint.json")
    rebuilt = build_approved_source_registry(registry, catalog, exclusions, blueprint)

    poisoned_registry = deepcopy(rebuilt)
    poisoned_registry["datasets"]["target"]["dataset_template"][
        "default_detail_fields"
    ].append("ORG")
    poisoned_registry["datasets"]["target"]["dataset_template_sha256"] = _sha256_json(
        poisoned_registry["datasets"]["target"]["dataset_template"]
    )
    assert build_approved_source_registry(
        poisoned_registry,
        catalog,
        exclusions,
        blueprint,
    ) == rebuilt

    runtime_drift = deepcopy(catalog)
    runtime_drift["datasets"]["lot_status"]["default_detail_fields"].remove("PROD_QTY")
    with pytest.raises(RegistryBuildError, match="runtime dataset template mismatch"):
        build_approved_source_registry(registry, runtime_drift, exclusions, blueprint)

    blueprint_drift = deepcopy(blueprint)
    blueprint_drift["executable"]["datasets"]["target"]["default_detail_fields"].append(
        "ORG"
    )
    blueprint_drift = _reseal_blueprint(blueprint_drift)
    with pytest.raises(RegistryBuildError, match="runtime dataset template mismatch"):
        build_approved_source_registry(registry, catalog, exclusions, blueprint_drift)


def test_dataset_template_rejects_open_unapproved_or_oversized_values() -> None:
    registry, catalog, exclusions = _inputs()
    blueprint = _load(DOMAIN_ROOT / "trusted_executable_blueprint.json")

    open_registry = deepcopy(registry)
    open_registry["datasets"]["wip"]["unexpected"] = True
    with pytest.raises(RegistryBuildError, match="dataset card contract is open"):
        build_approved_source_registry(open_registry, catalog, exclusions, blueprint)

    unapproved_catalog = deepcopy(catalog)
    unapproved_blueprint = deepcopy(blueprint)
    for container in (
        unapproved_catalog["datasets"]["target"],
        unapproved_blueprint["executable"]["datasets"]["target"],
    ):
        container["default_detail_fields"].append("UNKNOWN_FIELD")
    unapproved_blueprint = _reseal_blueprint(unapproved_blueprint)
    with pytest.raises(RegistryBuildError, match="default detail fields are not approved"):
        build_approved_source_registry(
            registry,
            unapproved_catalog,
            exclusions,
            unapproved_blueprint,
        )

    oversized_catalog = deepcopy(catalog)
    oversized_blueprint = deepcopy(blueprint)
    oversized_parameters = {
        f"P{index:03d}": {"description": "x" * 1000}
        for index in range(128)
    }
    oversized_catalog["datasets"]["eqp_uph"]["parameters"] = oversized_parameters
    oversized_blueprint["executable"]["datasets"]["eqp_uph"][
        "parameters"
    ] = oversized_parameters
    oversized_blueprint = _reseal_blueprint(oversized_blueprint)
    with pytest.raises(RegistryBuildError, match="dataset template exceeds"):
        build_approved_source_registry(
            registry,
            oversized_catalog,
            exclusions,
            oversized_blueprint,
        )


def test_semantic_vocabulary_is_derived_only_from_alias_cards() -> None:
    rebuilt = _build()
    _, catalog, _ = _inputs()
    vocabulary = rebuilt["semantic_vocabulary"]
    by_kind = {
        "dataset": {item["id"]: item["labels"] for item in vocabulary["datasets"]},
        "field": {item["id"]: item["labels"] for item in vocabulary["fields"]},
        "metric": {item["id"]: item["labels"] for item in vocabulary["metrics"]},
    }

    for kind, items in by_kind.items():
        for target_id, labels in items.items():
            raw_labels = [
                " ".join(value["text"].strip().split())
                for value in catalog["aliases"][f"{kind}:{target_id}"]["values"]
            ]
            expected = []
            seen = set()
            for label in sorted(raw_labels, key=lambda item: (item.casefold(), item)):
                if label.casefold() not in seen:
                    seen.add(label.casefold())
                    expected.append(label)
            assert labels == expected


def test_section_vocabulary_merges_only_matching_runtime_and_card_aliases() -> None:
    rebuilt = _build()
    _, catalog, _ = _inputs()
    vocabulary = rebuilt["semantic_vocabulary"]
    specs = {
        "relations": ("relation_id", ("relation",)),
        "grains": ("grain_id", ("grain",)),
        "orderings": ("ordering_id", ("ordering",)),
        "predicates": ("predicate_id", ("predicate", "product_group")),
        "recipes": ("recipe_id", ("recipe",)),
        "entity_groups": ("group_id", ("entity_group", "process_group")),
    }

    for section, (identity_key, alias_types) in specs.items():
        projected = {item["id"]: item["labels"] for item in vocabulary[section]}
        assert set(projected) == set(catalog[section])
        for card in catalog[section].values():
            entry_id = card[identity_key]
            candidates = list(card.get("aliases") or [])
            for alias_type in alias_types:
                alias = catalog["aliases"].get(f"{alias_type}:{entry_id}")
                if alias:
                    candidates.extend(value["text"] for value in alias["values"])
            if not candidates:
                candidates = [entry_id]
            normalized = []
            seen = set()
            for label in sorted(
                (" ".join(value.strip().split()) for value in candidates),
                key=lambda value: (value.casefold(), value),
            ):
                if label.casefold() not in seen:
                    seen.add(label.casefold())
                    normalized.append(label)
            assert projected[entry_id] == normalized

    assert vocabulary["relations"] == []
    assert vocabulary["grains"] == [{"id": "product", "labels": ["product"]}]
    assert vocabulary["orderings"] == [{"id": "process", "labels": ["process"]}]


def test_v2_rebuild_is_idempotent_and_order_independent() -> None:
    registry, catalog, exclusions = _inputs()
    first = build_approved_source_registry(registry, catalog, exclusions)
    second = build_approved_source_registry(first, catalog, exclusions)
    assert second == first

    reordered = deepcopy(catalog)
    reordered["aliases"] = _reverse_object(reordered["aliases"])
    reordered["datasets"] = _reverse_object(reordered["datasets"])
    reordered["fields"] = _reverse_object(reordered["fields"])
    reordered["metrics"] = _reverse_object(reordered["metrics"])
    for section in (
        "relations",
        "entity_groups",
        "grains",
        "orderings",
        "predicates",
        "recipes",
    ):
        reordered[section] = _reverse_object(reordered[section])
    reordered_build = build_approved_source_registry(registry, reordered, exclusions)
    assert reordered_build == first
    assert _pretty_json_bytes(reordered_build) == _pretty_json_bytes(first)


def test_rebuild_preserves_trusted_bindings_descriptors_and_exclusions() -> None:
    registry, catalog, exclusions = _inputs()
    rebuilt = build_approved_source_registry(registry, catalog, exclusions)
    assert rebuilt["datasets"] == registry["datasets"]

    poisoned = deepcopy(rebuilt)
    poisoned["semantic_vocabulary"] = {
        "contract_version": "attacker-controlled",
        "datasets": [],
        "fields": [],
        "metrics": [{"id": "WIP_BOH_QTY", "labels": ["config:secret@1"]}],
    }
    poisoned["semantic_templates"] = {
        "contract_version": "attacker-controlled",
        "metrics": {"WIP_QTY": {"query_ref": "query:unsafe@1"}},
    }
    assert build_approved_source_registry(poisoned, catalog, exclusions) == rebuilt


def test_v3_catalog_physical_drift_cannot_overwrite_approved_descriptors() -> None:
    registry, catalog, exclusions = _inputs()
    drifted_catalog = deepcopy(catalog)
    den = drifted_catalog["datasets"]["product_master"]["fields"]["DEN"]
    den["physical_column"] = "CATALOG_ONLY_DEN"
    den["physical_aliases"] = ["CATALOG_DEN_ALIAS"]

    rebuilt = build_approved_source_registry(registry, drifted_catalog, exclusions)

    assert rebuilt["datasets"] == registry["datasets"]
    approved = rebuilt["datasets"]["product_master"]["field_descriptors"]["DEN"]
    assert approved["physical_column"] == "DENSITY"
    assert approved["physical_aliases"] == ["DEN"]


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda descriptor: descriptor.update({"unexpected": True}),
            "open or incomplete",
        ),
        (
            lambda descriptor: descriptor.update({"semantic_type": "number"}),
            "semantically incompatible",
        ),
        (
            lambda descriptor: descriptor.update({"roles": ["output"]}),
            "roles are incompatible",
        ),
        (
            lambda descriptor: descriptor.update({"coercion": "strict_number"}),
            "semantically incompatible",
        ),
        (
            lambda descriptor: descriptor.update(
                {"nullable": not descriptor["nullable"]}
            ),
            "semantically incompatible",
        ),
        (
            lambda descriptor: descriptor.update({"physical_aliases": [""]}),
            "physical_aliases",
        ),
        (
            lambda descriptor: descriptor.update(
                {"physical_aliases": [f"ALIAS_{index:03d}" for index in range(129)]}
            ),
            "physical_aliases",
        ),
    ],
)
def test_v3_descriptor_contract_rejects_open_unsafe_or_semantic_tampering(
    mutate,
    message: str,
) -> None:
    registry, catalog, exclusions = _inputs()
    candidate = deepcopy(registry)
    descriptor = candidate["datasets"]["product_master"]["field_descriptors"]["DEN"]
    mutate(descriptor)

    with pytest.raises(RegistryBuildError, match=message):
        build_approved_source_registry(candidate, catalog, exclusions)


def test_semantic_vocabulary_field_families_follow_final_approved_descriptors() -> None:
    rebuilt = _build()
    expected: dict[str, set[str]] = {}
    for dataset in rebuilt["datasets"].values():
        for field_id in dataset["field_descriptors"]:
            expected.setdefault(field_id, set()).add(dataset["family"])

    actual = {
        item["id"]: item["families"]
        for item in rebuilt["semantic_vocabulary"]["fields"]
    }
    assert actual == {
        field_id: sorted(families)
        for field_id, families in sorted(expected.items())
    }
    assert "equipment_uph" not in actual["FAMILY"]
    assert "equipment_uph" not in actual["OPER_SEQ"]


@pytest.mark.parametrize(
    "source_version",
    [
        "metadata.authoring.source-registry.v1",
        "metadata.authoring.source-registry.v2",
    ],
)
def test_v1_and_v2_upgrade_still_derives_descriptors_from_compiled_catalog(
    source_version: str,
) -> None:
    registry, catalog, exclusions = _inputs()
    legacy = {
        "contract_version": source_version,
        "domain_id": registry["domain_id"],
        "datasets": {
            dataset_id: {
                key: card[key]
                for key in ("source_type", "source_adapter", "config_ref", "query_ref")
            }
            for dataset_id, card in registry["datasets"].items()
        },
    }
    if source_version.endswith(".v2"):
        legacy["semantic_vocabulary"] = {"contract_version": "stale"}
        legacy["semantic_templates"] = {"contract_version": "stale"}

    rebuilt = build_approved_source_registry(legacy, catalog, exclusions)

    assert rebuilt["contract_version"] == "metadata.authoring.source-registry.v3"
    assert "FAMILY" in rebuilt["datasets"]["eqp_uph"]["field_descriptors"]
    assert (
        rebuilt["datasets"]["product_master"]["field_descriptors"]["DEN"]
        ["physical_column"]
        == "DEN"
    )


def test_rebuild_summary_reports_stable_full_and_vocabulary_hashes(tmp_path: Path) -> None:
    output_path = tmp_path / "approved_source_registry.json"
    first = rebuild_registry(
        registry_path=REGISTRY_PATH,
        catalog_path=CATALOG_PATH,
        output_path=output_path,
        exclusions_path=EXCLUSIONS_PATH,
    )
    second = rebuild_registry(
        registry_path=output_path,
        catalog_path=CATALOG_PATH,
        output_path=output_path,
        exclusions_path=EXCLUSIONS_PATH,
    )
    rebuilt = _load(output_path)
    assert first == second
    assert first["semantic_vocabulary_counts"] == {
        "datasets": 10,
        "fields": 47,
        "metrics": 17,
        "relations": 0,
        "grains": 1,
        "orderings": 1,
        "predicates": 7,
        "recipes": 10,
        "entity_groups": 25,
    }
    assert first["sha256"] == hashlib.sha256(_pretty_json_bytes(rebuilt)).hexdigest()
    assert first["semantic_vocabulary_sha256"] == hashlib.sha256(
        _pretty_json_bytes(rebuilt["semantic_vocabulary"])
    ).hexdigest()
    assert first["semantic_template_counts"] == {
        "metrics": 17,
        "relations": 0,
        "entity_groups": 25,
        "grains": 1,
        "orderings": 1,
        "predicates": 7,
        "recipes": 10,
        "aliases": 141,
    }
    compact_templates = json.dumps(
        rebuilt["semantic_templates"],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    assert first["semantic_templates_bytes"] == len(compact_templates)
    assert first["semantic_templates_sha256"] == hashlib.sha256(compact_templates).hexdigest()
    assert first["semantic_templates_blueprint_sha256"] == rebuilt[
        "semantic_templates_blueprint_sha256"
    ]
    assert first["semantic_templates_executable_sha256"] == rebuilt[
        "semantic_templates_executable_sha256"
    ]
    assert first["semantic_templates_projection_sha256"] == rebuilt[
        "semantic_templates_projection_sha256"
    ]
    dataset_templates = {
        dataset_id: card["dataset_template"]
        for dataset_id, card in sorted(rebuilt["datasets"].items())
    }
    dataset_template_material = {
        dataset_id: {
            "dataset_template": card["dataset_template"],
            "dataset_template_sha256": card["dataset_template_sha256"],
        }
        for dataset_id, card in sorted(rebuilt["datasets"].items())
    }
    without_templates = deepcopy(rebuilt)
    for card in without_templates["datasets"].values():
        card.pop("dataset_template")
        card.pop("dataset_template_sha256")
    assert first["dataset_template_bytes"] == len(
        json.dumps(
            dataset_templates,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    assert first["dataset_template_byte_overhead"] == len(
        _pretty_json_bytes(rebuilt)
    ) - len(_pretty_json_bytes(without_templates))
    assert first["dataset_templates_sha256"] == _sha256_json(dataset_template_material)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda catalog: catalog["aliases"]["dataset:wip"].update({"unexpected": True}),
            "missing or open",
        ),
        (
            lambda catalog: catalog["aliases"].pop("metric:WIP_QTY"),
            "incomplete",
        ),
        (
            lambda catalog: catalog["aliases"]["metric:WIP_QTY"]["values"][0].update(
                {"text": "https://unsafe.example"}
            ),
            "unsafe or oversized",
        ),
        (
            lambda catalog: catalog["aliases"]["metric:WIP_QTY"]["values"].append(
                {"priority": 100, "text": "생산량"}
            ),
            "ambiguous within its vocabulary kind",
        ),
        (
            lambda catalog: catalog["aliases"]["metric:WIP_QTY"].update(
                {
                    "values": [
                        {"priority": 100, "text": f"bounded label {index}"}
                        for index in range(129)
                    ]
                }
            ),
            "labels must be bounded",
        ),
    ],
)
def test_semantic_vocabulary_rejects_open_incomplete_unsafe_or_ambiguous_aliases(
    mutate,
    message: str,
) -> None:
    registry, catalog, exclusions = _inputs()
    candidate = deepcopy(catalog)
    mutate(candidate)
    with pytest.raises(RegistryBuildError, match=message):
        build_approved_source_registry(registry, candidate, exclusions)


def test_source_registry_root_rejects_unknown_keys_but_rebuilds_prior_vocabulary() -> None:
    registry, catalog, exclusions = _inputs()
    rebuilt = build_approved_source_registry(registry, catalog, exclusions)
    assert build_approved_source_registry(rebuilt, catalog, exclusions) == rebuilt

    open_registry = deepcopy(rebuilt)
    open_registry["unexpected"] = {"query_ref": "query:unsafe@1"}
    with pytest.raises(RegistryBuildError, match="root contract is open"):
        build_approved_source_registry(open_registry, catalog, exclusions)


def test_semantic_vocabulary_rejects_total_utf8_payload_over_64_kib() -> None:
    registry, catalog, exclusions = _inputs()
    oversized = deepcopy(catalog)
    field_cards = [
        (alias_key, card)
        for alias_key, card in oversized["aliases"].items()
        if card.get("target_type") == "field"
    ]
    for field_index, (_, card) in enumerate(field_cards):
        card["values"] = [
            {
                "priority": 100,
                "text": f"field {field_index:03d} label {label_index:03d} " + "x" * 200,
            }
            for label_index in range(128)
        ]
    with pytest.raises(RegistryBuildError, match="exceeds the UTF-8 byte limit"):
        build_approved_source_registry(registry, oversized, exclusions)


def test_metric_vocabulary_never_exposes_binding_even_when_catalog_metric_has_one() -> None:
    rebuilt = _build()
    metric = next(
        item
        for item in rebuilt["semantic_vocabulary"]["metrics"]
        if item["id"] == "WIP_BOH_QTY"
    )
    assert set(metric) == {"id", "labels"}
    assert "dataset_family" not in json.dumps(metric, ensure_ascii=False).casefold()
    assert "source_binding" not in json.dumps(metric, ensure_ascii=False).casefold()


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda catalog: catalog["metrics"]["WIP_QTY"].update(
                {"query_ref": "query:unsafe@1"}
            ),
            "open or invalid",
        ),
        (
            lambda catalog: catalog["metrics"]["WIP_QTY"]["source_binding"].update(
                {"config_ref": "config:unsafe@1"}
            ),
            "forbidden payload key",
        ),
        (
            lambda catalog: catalog["metrics"]["WIP_QTY"]["source_binding"].update(
                {"field": "UNKNOWN_FIELD"}
            ),
            "template mismatch",
        ),
        (
            lambda catalog: catalog["recipes"]["rank.top_n"][
                "default_operation_template"
            ].update({"documentation": "https://unsafe.example/template"}),
            "executable or URL payload text",
        ),
        (
            lambda catalog: catalog["aliases"]["metric:WIP_QTY"].update(
                {"target_key": "UNKNOWN_METRIC"}
            ),
            "alias key mismatch|bounded object|identity mismatch|template mismatch",
        ),
    ],
)
def test_semantic_templates_reject_open_forbidden_or_unregistered_payloads(
    mutate,
    message: str,
) -> None:
    registry, catalog, exclusions = _inputs()
    candidate = deepcopy(catalog)
    mutate(candidate)
    with pytest.raises(RegistryBuildError, match=message):
        build_approved_source_registry(registry, candidate, exclusions)


def test_semantic_templates_reject_total_utf8_payload_over_128_kib() -> None:
    registry, catalog, exclusions = _inputs()
    oversized = deepcopy(catalog)
    blueprint = _load(DOMAIN_ROOT / "trusted_executable_blueprint.json")
    oversized_blueprint = deepcopy(blueprint)
    values = [
        f"bounded semantic value {index:04d} " + "x" * 200
        for index in range(1000)
    ]
    oversized["recipes"]["rank.top_n"]["default_operation_template"][
        "bounded_values"
    ] = values
    oversized_blueprint["executable"]["recipes"]["rank.top_n"][
        "default_operation_template"
    ]["bounded_values"] = values
    oversized_blueprint = _reseal_blueprint(oversized_blueprint)
    with pytest.raises(RegistryBuildError, match="exceed the UTF-8 byte limit"):
        build_approved_source_registry(
            registry,
            oversized,
            exclusions,
            oversized_blueprint,
        )
