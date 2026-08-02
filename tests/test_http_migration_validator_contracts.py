from __future__ import annotations

import inspect
import json
from copy import deepcopy
from hashlib import sha256

import pytest
import tools.validate_langflow_http_migration_patches_e2e as migration_validator

from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    gemini_model_contract_evidence,
)
from tools.validate_langflow_http_authoring_e2e import _expected_prepare_llm_calls
from tools.validate_langflow_http_migration_patches_e2e import (
    AUTHORING_INPUT_PATHS,
    BLUEPRINT_PATH,
    BLUEPRINT_PIN_PATH,
    DATASET_TEXT_PATH,
    DOMAIN_POLICY_TEXT_PATH,
    DOMAIN_TEXT_PATH,
    FREEFORM_CLARIFICATION_PROBE,
    MAIN_FILTER_TEXT_PATH,
    MANUFACTURING_ANSWER_EXTENSION,
    MANUFACTURING_FUNCTION_CARD,
    MANUFACTURING_INTENT_EXTENSION,
    MANUFACTURING_OUTPUT_OVERLAY,
    APPROVED_SOURCE_REGISTRY_PATH,
    APPROVED_SOURCE_REGISTRY_PIN_PATH,
    TRUSTED_SOURCE_MANIFEST_PATH,
    _COMPILER_FIELD_ROLE_ORDER,
    _load_approved_source_registry_oracle,
    _load_trusted_inventory_manifest,
    _load_v6_authoring_sources,
    _domain_oracle_comparison,
    _registry_owned_dataset_draft,
    _run_freeform_clarification_probe,
    run,
)
from reference_runtime.domain_packages import compile_domain_package


def test_migration_validator_uses_only_four_v6_inputs() -> None:
    texts, source_hashes, evidence_by_kind = _load_v6_authoring_sources()

    assert AUTHORING_INPUT_PATHS == {
        "domain": DOMAIN_TEXT_PATH,
        "domain_policy": DOMAIN_POLICY_TEXT_PATH,
        "dataset": DATASET_TEXT_PATH,
        "main_filter": MAIN_FILTER_TEXT_PATH,
    }
    assert set(texts) == {"domain", "domain_policy", "dataset", "main_filter"}
    assert set(source_hashes) == set(texts)
    assert set(evidence_by_kind) == set(texts)
    for kind, path in AUTHORING_INPUT_PATHS.items():
        text = path.read_text(encoding="utf-8-sig").strip()
        content_sha256 = sha256(text.encode("utf-8")).hexdigest()
        assert texts[kind] == text
        assert source_hashes[kind] == content_sha256
        assert evidence_by_kind[kind] == {
            "path": path.relative_to(path.parents[3]).as_posix(),
            "content_sha256": content_sha256,
            "byte_count": len(text.encode("utf-8")),
            "line_count": len(text.splitlines()),
            "source_text_persisted": False,
        }

    serialized = json.dumps(evidence_by_kind, ensure_ascii=False, sort_keys=True)
    assert all(text not in serialized for text in texts.values())


def test_domain_raw_input_and_admin_oracles_use_separate_contracts() -> None:
    texts, _, _ = _load_v6_authoring_sources()
    manifest, evidence = _load_trusted_inventory_manifest()

    assert texts["domain"]
    assert manifest["contract_version"] == "metadata.authoring.source-manifest.v1"
    assert manifest["counts"]["datasets"] >= 1
    assert evidence["manifest_sha256"] == manifest["manifest_sha256"]
    assert evidence["manifest_body_persisted"] is False
    assert evidence["user_raw_txt_used_as_manifest"] is False
    assert TRUSTED_SOURCE_MANIFEST_PATH.name == "trusted_source_manifest.json"
    assert TRUSTED_SOURCE_MANIFEST_PATH.parent.name == "manufacturing"
    assert BLUEPRINT_PATH.name == "trusted_executable_blueprint.json"
    assert BLUEPRINT_PATH.parent.name == "manufacturing"
    assert BLUEPRINT_PIN_PATH == BLUEPRINT_PATH.with_suffix(".sha256")

    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    registry, registry_evidence = _load_approved_source_registry_oracle(blueprint)
    assert APPROVED_SOURCE_REGISTRY_PATH.name == "approved_source_registry.json"
    assert APPROVED_SOURCE_REGISTRY_PIN_PATH.name == "approved_source_registry.sha256"
    assert registry["contract_version"] == "metadata.authoring.source-registry.v3"
    assert registry_evidence["counts"] == {
        "datasets": len(registry["datasets"]),
        "field_descriptors": sum(
            len(card["field_descriptors"])
            for card in registry["datasets"].values()
        ),
    }
    assert registry_evidence["registry_body_persisted"] is False
    assert registry_evidence["registry_file_pin_exact"] is True
    assert registry_evidence["registry_file_sha256"] == registry_evidence[
        "pinned_registry_file_sha256"
    ]

    # Fresh validation environments rebind only blueprint identity. Registry
    # provenance stays pinned while executable content remains exact.
    rebound = deepcopy(blueprint)
    rebound["environment"] = "fresh_validation_environment"
    rebound["blueprint_sha256"] = "0" * 64
    rebound_registry, _ = _load_approved_source_registry_oracle(rebound)
    assert rebound_registry == registry


def test_source_registry_oracle_rejects_wrong_pin_and_tampered_registry(
    tmp_path, monkeypatch
) -> None:
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    registry_bytes = APPROVED_SOURCE_REGISTRY_PATH.read_bytes()
    registry_path = tmp_path / "approved_source_registry.json"
    pin_path = tmp_path / "approved_source_registry.sha256"
    registry_path.write_bytes(registry_bytes)
    pin_path.write_text("0" * 64 + "\n", encoding="ascii")
    monkeypatch.setattr(migration_validator, "APPROVED_SOURCE_REGISTRY_PATH", registry_path)
    monkeypatch.setattr(migration_validator, "APPROVED_SOURCE_REGISTRY_PIN_PATH", pin_path)
    with pytest.raises(RuntimeError, match="source_registry_pin_mismatch"):
        migration_validator._load_approved_source_registry_oracle(blueprint)

    pin_path.write_text(sha256(registry_bytes).hexdigest() + "\n", encoding="ascii")
    registry_path.write_bytes(registry_bytes + b"\n")
    with pytest.raises(RuntimeError, match="source_registry_pin_mismatch"):
        migration_validator._load_approved_source_registry_oracle(blueprint)

def test_v6_authoring_call_budget_and_exact_model_contract() -> None:
    texts, _, _ = _load_v6_authoring_sources()

    assert _expected_prepare_llm_calls("domain", texts["domain"]) == {
        "draft": 3,
        "annotation": 0,
        "repair": 0,
    }
    assert _expected_prepare_llm_calls("domain_policy", texts["domain_policy"]) == {
        "draft": 0,
        "annotation": 0,
        "repair": 0,
    }
    assert _expected_prepare_llm_calls("dataset", texts["dataset"]) == {
        "draft": 1,
        "annotation": 0,
        "repair": 0,
    }
    assert _expected_prepare_llm_calls("main_filter", texts["main_filter"]) == {
        "draft": 1,
        "annotation": 0,
        "repair": 0,
    }
    assert gemini_model_contract_evidence() == {
        "requested_model": DEFAULT_GEMINI_MODEL,
        "temperature": 0,
        "candidate_count": 1,
        "fallback_enabled": False,
        "fallback_models": [],
    }
    assert DEFAULT_GEMINI_MODEL == "gemini-3.5-flash-lite"


def test_http_run_has_no_deterministic_seed_and_orders_all_authoring_flows() -> None:
    source = inspect.getsource(run)

    assert "_seed_migration_package" not in source
    assert "migration_seed" not in source
    assert source.index('(\"domain\", str(uploaded[0][\"id\"])') < source.index(
        '(\"domain_policy\", str(uploaded[3][\"id\"])'
    )
    assert source.index('(\"domain_policy\", str(uploaded[3][\"id\"])') < source.index(
        '(\"dataset\", str(uploaded[1][\"id\"])'
    )
    assert source.index('(\"dataset\", str(uploaded[1][\"id\"])') < source.index(
        '(\"main_filter\", str(uploaded[2][\"id\"])'
    )
    assert '== [0, 1, 2, 3]' in source
    assert '== [1, 2, 3, 4]' in source
    assert "exact_gemini_no_fallback" in source
    assert "extract_authoring_source_manifest" not in source
    assert "trusted_blueprint=trusted_blueprint if kind == \"domain\" else None" not in source
    assert "trusted_blueprint_pin=trusted_blueprint_pin if kind == \"domain\" else \"\"" not in source
    assert "_domain_oracle_comparison" in source
    assert "_run_freeform_clarification_probe" in source
    assert '"chat_input": {"input_value": texts["domain"]}' in source
    assert '"dataset_source_input": {"input_value": texts["dataset"]}' in source
    assert '"main_filter_source_input"' in source
    assert '"input_value": texts["main_filter"]' in source
    assert "expected_source_text=expected_source_text" in source
    assert "domain_bootstrap_source" in source


def test_freeform_clarification_probe_is_three_calls_and_non_persistent() -> None:
    source = inspect.getsource(_run_freeform_clarification_probe)

    assert FREEFORM_CLARIFICATION_PROBE
    assert '"source_grounding_mode": "freeform_llm"' in source
    assert '"draft_llm_three"' in source
    assert '"annotation_llm_zero"' in source
    assert '"repair_llm_zero"' in source
    assert '"candidate_fields_absent"' in source
    assert '"package_fields_absent"' in source
    assert '"persist_fields_absent"' in source
    assert '"mongo_document_count_increase_zero"' in source
    assert '"collections_unchanged"' in source
    assert '"source_text_persisted": False' in source
    probe = FREEFORM_CLARIFICATION_PROBE.casefold()
    for forbidden in (
        "canonical",
        "dataset_id",
        "field_id",
        "등록 id",
        "물리 컬럼",
        "semantic type",
        "relation",
        "grain",
    ):
        assert forbidden.casefold() not in probe


def test_domain_oracle_comparison_is_result_only() -> None:
    source = inspect.getsource(_domain_oracle_comparison)

    assert "compile_domain_package" in source
    assert "executable_runtime_projection_exact" in source
    assert "registry_dataset_binding_exact" in source
    assert "compiler_derived_fields_exact" in source
    assert '"oracle_not_flow_input": True' in source
    assert '"oracle_payload_persisted": False' in source

    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    registry, _ = _load_approved_source_registry_oracle(blueprint)
    draft = {
        **deepcopy(blueprint["executable"]),
        **deepcopy(blueprint["default_annotations"]),
    }
    draft["datasets"] = _registry_owned_dataset_draft(registry)
    package = compile_domain_package(
        draft,
        "manufacturing",
        "production",
        revision=1,
        lifecycle_status="validated",
    )
    exact = _domain_oracle_comparison(
        package,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
    )
    assert exact["passed"] is True
    assert exact["checks"]["executable_runtime_projection_exact"] is True
    assert exact["checks"]["section_counts_exact"] is True
    assert exact["checks"]["section_hashes_exact"] is True
    assert exact["checks"]["registry_dataset_binding_exact"] is True
    assert exact["checks"]["compiler_derived_fields_exact"] is True
    assert exact["field_role_normalization"]["set_only_comparison_used"] is False

    dataset_id, field_id, descriptor = next(
        (
            dataset_id,
            field_id,
            descriptor,
        )
        for dataset_id, card in registry["datasets"].items()
        for field_id, descriptor in card["field_descriptors"].items()
        if descriptor["roles"]
        != [
            role
            for role in _COMPILER_FIELD_ROLE_ORDER
            if role in descriptor["roles"]
        ]
    )
    assert package["runtime_catalog"]["datasets"][dataset_id]["fields"][field_id][
        "roles"
    ] == [
        role for role in _COMPILER_FIELD_ROLE_ORDER if role in descriptor["roles"]
    ]

    policy_only = deepcopy(package)
    policy_only["runtime_catalog"]["prompt_extensions"] = {
        "intent": MANUFACTURING_INTENT_EXTENSION,
        "answer": MANUFACTURING_ANSWER_EXTENSION,
    }
    policy_only["runtime_catalog"]["specialized_functions"] = [
        deepcopy(MANUFACTURING_FUNCTION_CARD)
    ]
    policy_only["runtime_catalog"]["output_profile"].update(
        MANUFACTURING_OUTPUT_OVERLAY
    )
    expected_policy = {
        "prompt_extensions": {
            "intent": MANUFACTURING_INTENT_EXTENSION,
            "answer": MANUFACTURING_ANSWER_EXTENSION,
        },
        "specialized_functions": [MANUFACTURING_FUNCTION_CARD],
        "output_profile_overlay": MANUFACTURING_OUTPUT_OVERLAY,
    }
    policy_comparison = _domain_oracle_comparison(
        policy_only,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
        expected_policy=expected_policy,
    )
    assert policy_comparison["passed"] is True
    assert "prompt_extensions" in policy_comparison["excluded_sections"]

    policy_drift = deepcopy(policy_only)
    policy_drift["runtime_catalog"]["prompt_extensions"]["intent"] += " drift"
    policy_drift_comparison = _domain_oracle_comparison(
        policy_drift,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
        expected_policy=expected_policy,
    )
    assert policy_drift_comparison["passed"] is False
    assert policy_drift_comparison["checks"]["policy_overlay_exact"] is False

    display_changed = deepcopy(package)
    dataset_key = sorted(display_changed["runtime_catalog"]["datasets"])[0]
    display_changed["runtime_catalog"]["datasets"][dataset_key][
        "display_name"
    ] += " changed"
    display_comparison = _domain_oracle_comparison(
        display_changed,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
    )
    assert display_comparison["passed"] is True
    assert display_comparison["checks"]["display_annotations_valid"] is True

    changed = deepcopy(package)
    first_field = sorted(changed["runtime_catalog"]["datasets"][dataset_key]["fields"])[0]
    changed["runtime_catalog"]["datasets"][dataset_key]["fields"][first_field][
        "physical_column"
    ] += "_DRIFT"
    mismatch = _domain_oracle_comparison(
        changed,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
    )
    assert mismatch["passed"] is False
    assert mismatch["checks"]["registry_dataset_binding_exact"] is False


def test_domain_oracle_alias_delta_is_closed_registered_and_additive() -> None:
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    registry, _ = _load_approved_source_registry_oracle(blueprint)
    draft = {
        **deepcopy(blueprint["executable"]),
        **deepcopy(blueprint["default_annotations"]),
        "datasets": _registry_owned_dataset_draft(registry),
    }
    package = compile_domain_package(
        draft,
        "manufacturing",
        "production",
        revision=1,
        lifecycle_status="validated",
    )

    additive = deepcopy(package)
    aliases = additive["runtime_catalog"]["aliases"]
    aliases["field:DATE"]["values"].append({"text": "기준 날짜", "priority": 100})
    aliases["predicate:HBM"] = {
        "target_type": "predicate",
        "target_key": "HBM",
        "values": [{"text": "고대역폭 메모리", "priority": 100}],
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
    alias_source = "기준 날짜와 고대역폭 메모리를 주요 필터 별칭으로 사용한다."
    additive_result = _domain_oracle_comparison(
        additive,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
        main_filter_source=alias_source,
    )
    assert additive_result["passed"] is True
    assert additive_result["alias_delta"]["added_card_count"] == 1
    assert additive_result["alias_delta"]["extended_card_count"] == 1
    assert additive_result["checks"]["alias_closed_schema"] is True
    assert additive_result["checks"]["alias_registered_targets"] is True
    assert additive_result["checks"]["worker_alias_delta_source_grounded"] is True
    assert additive_result["checks"]["worker_alias_delta_labels_unique"] is True

    not_sourced_result = _domain_oracle_comparison(
        additive,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
        main_filter_source="등록 문장에는 다른 표현만 있다.",
    )
    assert not_sourced_result["passed"] is False
    assert not_sourced_result["checks"]["worker_alias_delta_source_grounded"] is False

    priority_drift = deepcopy(additive)
    priority_drift["runtime_catalog"]["aliases"]["predicate:HBM"]["values"][0][
        "priority"
    ] = 101
    priority_result = _domain_oracle_comparison(
        priority_drift,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
        main_filter_source=alias_source,
    )
    assert priority_result["passed"] is False
    assert priority_result["checks"]["worker_alias_delta_shape_priority_exact"] is False

    duplicate_label = deepcopy(additive)
    duplicate_label["runtime_catalog"]["aliases"]["predicate:HBM"]["values"].append(
        {"text": "  고대역폭   메모리  ", "priority": 100}
    )
    duplicate_result = _domain_oracle_comparison(
        duplicate_label,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
        main_filter_source=alias_source,
    )
    assert duplicate_result["passed"] is False
    assert duplicate_result["checks"]["worker_alias_delta_labels_unique"] is False

    cross_target = deepcopy(additive)
    cross_target["runtime_catalog"]["aliases"]["field:DATE"]["values"].append(
        {"text": "고대역폭 메모리", "priority": 100}
    )
    cross_target_result = _domain_oracle_comparison(
        cross_target,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
        main_filter_source=alias_source,
    )
    assert cross_target_result["passed"] is False
    assert cross_target_result["checks"]["worker_alias_delta_labels_unique"] is False

    removed_baseline = deepcopy(additive)
    removed_baseline["runtime_catalog"]["aliases"]["field:DATE"]["values"].pop(0)
    removed_result = _domain_oracle_comparison(
        removed_baseline,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
        main_filter_source=alias_source,
    )
    assert removed_result["passed"] is False
    assert removed_result["checks"]["baseline_aliases_preserved"] is False

    open_alias = deepcopy(additive)
    open_alias["runtime_catalog"]["aliases"]["predicate:HBM"]["unexpected"] = True
    open_result = _domain_oracle_comparison(
        open_alias,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
        main_filter_source=alias_source,
    )
    assert open_result["passed"] is False
    assert open_result["checks"]["alias_closed_schema"] is False

    unregistered = deepcopy(additive)
    unregistered["runtime_catalog"]["aliases"]["predicate:UNKNOWN"] = {
        **deepcopy(unregistered["runtime_catalog"]["aliases"]["predicate:HBM"]),
        "target_key": "UNKNOWN",
    }
    unregistered_result = _domain_oracle_comparison(
        unregistered,
        trusted_blueprint=blueprint,
        approved_source_registry=registry,
        environment="production",
        main_filter_source=alias_source,
    )
    assert unregistered_result["passed"] is False
    assert unregistered_result["checks"]["alias_registered_targets"] is False


def test_migration_policy_extensions_are_clean_utf8_korean() -> None:
    assert MANUFACTURING_INTENT_EXTENSION == (
        "제조 용어는 등록된 dataset, field, metric, recipe 별칭만 사용하고 "
        "모호하면 후보 계약으로 제한한다."
    )
    assert MANUFACTURING_ANSWER_EXTENSION == (
        "응답은 실행 결과의 검증된 사실만 설명하고 조회 기준, 단위, "
        "빈 결과 여부를 명시한다."
    )
    for text in (MANUFACTURING_INTENT_EXTENSION, MANUFACTURING_ANSWER_EXTENSION):
        assert text.encode("utf-8").decode("utf-8") == text
        assert "\ufffd" not in text
        assert "?" not in text
