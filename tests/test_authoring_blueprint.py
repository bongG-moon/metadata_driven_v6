from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from reference_runtime.authoring_blueprint import (
    ANNOTATION_KEYS,
    BLUEPRINT_KEYS,
    BLUEPRINT_VERSION,
    EXECUTABLE_KEYS,
    build_executable_blueprint,
    compute_blueprint_sha256,
    merge_blueprint_annotations,
    validate_executable_blueprint,
)
from reference_runtime.authoring_source_manifest import extract_authoring_source_manifest
from reference_runtime.canonical import ContractError, canonical_bytes, sha256_json
from reference_runtime.domain_packages import compile_domain_package


ROOT = Path(__file__).resolve().parents[1]
DRAFT_PATH = ROOT / "metadata" / "domain_packs" / "order_sales" / "authoring_draft.json"
SOURCE_PATH = ROOT / "validation" / "order_sales_metadata_input.txt"


def _draft() -> dict:
    return json.loads(DRAFT_PATH.read_text(encoding="utf-8"))


def _manifest() -> dict:
    return extract_authoring_source_manifest(SOURCE_PATH.read_text(encoding="utf-8"))


def _blueprint() -> tuple[dict, dict]:
    manifest = _manifest()
    blueprint = build_executable_blueprint(
        _draft(),
        domain_id="order_sales",
        environment="test",
        source_manifest=manifest,
    )
    return blueprint, manifest


def _validate(blueprint: dict, manifest: dict, *, pin: str | None = None) -> dict:
    return validate_executable_blueprint(
        blueprint,
        expected_blueprint_sha256=pin or blueprint["blueprint_sha256"],
        expected_domain_id="order_sales",
        expected_environment="test",
        source_manifest=manifest,
    )


def _reason(exc: pytest.ExceptionInfo[ContractError]) -> str:
    return str((exc.value.details or {}).get("reason") or "")


def _reseal_manifest(manifest: dict, *, source_sha256: str) -> dict:
    material = deepcopy(manifest)
    material.pop("manifest_sha256")
    material["source_sha256"] = source_sha256
    return {**material, "manifest_sha256": sha256_json(material)}


def test_build_seals_exact_contract_and_hashes() -> None:
    original_draft = _draft()
    original_manifest = _manifest()
    draft_before = deepcopy(original_draft)
    manifest_before = deepcopy(original_manifest)

    blueprint = build_executable_blueprint(
        original_draft,
        domain_id="order_sales",
        environment="test",
        source_manifest=original_manifest,
    )

    assert original_draft == draft_before
    assert original_manifest == manifest_before
    assert blueprint["contract_version"] == BLUEPRINT_VERSION
    assert set(blueprint) == set(BLUEPRINT_KEYS)
    assert set(blueprint["executable"]) == set(EXECUTABLE_KEYS)
    assert set(blueprint["default_annotations"]) == set(ANNOTATION_KEYS)
    assert blueprint["source_manifest_sha256"] == original_manifest["manifest_sha256"]
    assert blueprint["executable_sha256"] == sha256_json(blueprint["executable"])
    assert blueprint["blueprint_sha256"] == compute_blueprint_sha256(blueprint)
    assert _validate(blueprint, original_manifest) == blueprint


def test_annotation_only_changes_do_not_change_executable_hash() -> None:
    draft = _draft()
    manifest = _manifest()
    first = build_executable_blueprint(
        draft,
        domain_id="order_sales",
        environment="test",
        source_manifest=manifest,
    )
    draft["display_name"] = "다른 표시 이름"
    draft["description"] = "다른 설명"
    second = build_executable_blueprint(
        draft,
        domain_id="order_sales",
        environment="test",
        source_manifest=manifest,
    )

    assert first["executable_sha256"] == second["executable_sha256"]
    assert canonical_bytes(first["executable"]) == canonical_bytes(second["executable"])
    assert first["blueprint_sha256"] != second["blueprint_sha256"]


def test_merge_overlays_only_annotations_and_compiles_full_draft() -> None:
    blueprint, manifest = _blueprint()
    blueprint_before = deepcopy(blueprint)
    manifest_before = deepcopy(manifest)
    executable_bytes = canonical_bytes(blueprint["executable"])

    merged = merge_blueprint_annotations(
        blueprint,
        {"display_name": "주문 분석", "description": "사용자 친화적 설명"},
        expected_blueprint_sha256=blueprint["blueprint_sha256"],
        expected_domain_id="order_sales",
        expected_environment="test",
        source_manifest=manifest,
    )

    assert blueprint == blueprint_before
    assert manifest == manifest_before
    assert merged["display_name"] == "주문 분석"
    assert merged["description"] == "사용자 친화적 설명"
    assert canonical_bytes({key: merged[key] for key in EXECUTABLE_KEYS}) == executable_bytes
    assert sha256_json({key: merged[key] for key in EXECUTABLE_KEYS}) == blueprint["executable_sha256"]
    package = compile_domain_package(merged, "order_sales", "test")
    assert package["domain_id"] == "order_sales"


def test_merge_keeps_reviewed_defaults_for_missing_annotations() -> None:
    blueprint, manifest = _blueprint()
    merged = merge_blueprint_annotations(
        blueprint,
        {},
        expected_blueprint_sha256=blueprint["blueprint_sha256"],
        expected_domain_id="order_sales",
        expected_environment="test",
        source_manifest=manifest,
    )
    assert merged["display_name"] == blueprint["default_annotations"]["display_name"]
    assert merged["description"] == blueprint["default_annotations"]["description"]


@pytest.mark.parametrize(
    "proposal",
    [
        {"datasets": {}},
        {"prompt_extensions": {}},
        {"specialized_functions": []},
        {"display_name": {"datasets": {}}},
        {"description": ["not", "text"]},
    ],
)
def test_merge_rejects_unknown_or_non_scalar_annotation_payloads(proposal: dict) -> None:
    blueprint, manifest = _blueprint()
    with pytest.raises(ContractError):
        merge_blueprint_annotations(
            blueprint,
            proposal,
            expected_blueprint_sha256=blueprint["blueprint_sha256"],
            expected_domain_id="order_sales",
            expected_environment="test",
            source_manifest=manifest,
        )


@pytest.mark.parametrize("missing", BLUEPRINT_KEYS)
def test_missing_blueprint_field_fails_closed(missing: str) -> None:
    blueprint, manifest = _blueprint()
    blueprint.pop(missing)
    with pytest.raises(ContractError):
        _validate(blueprint, manifest, pin="0" * 64)


def test_unknown_blueprint_field_fails_closed() -> None:
    blueprint, manifest = _blueprint()
    blueprint["untrusted"] = True
    with pytest.raises(ContractError) as exc:
        _validate(blueprint, manifest)
    assert _reason(exc) == "blueprint_top_level_keys_mismatch"


def test_executable_tamper_without_rehash_fails_closed() -> None:
    blueprint, manifest = _blueprint()
    blueprint["executable"]["locale"] = "en-US"
    with pytest.raises(ContractError) as exc:
        _validate(blueprint, manifest)
    assert _reason(exc) == "executable_hash_mismatch"


def test_recomputed_executable_and_self_hash_still_fail_external_pin() -> None:
    blueprint, manifest = _blueprint()
    trusted_pin = blueprint["blueprint_sha256"]
    blueprint["executable"]["locale"] = "en-US"
    blueprint["executable_sha256"] = sha256_json(blueprint["executable"])
    blueprint["blueprint_sha256"] = compute_blueprint_sha256(blueprint)
    assert blueprint["blueprint_sha256"] != trusted_pin

    with pytest.raises(ContractError) as exc:
        _validate(blueprint, manifest, pin=trusted_pin)
    assert _reason(exc) == "blueprint_external_pin_mismatch"


def test_wrong_external_pin_fails_closed() -> None:
    blueprint, manifest = _blueprint()
    wrong_pin = "0" * 64 if blueprint["blueprint_sha256"] != "0" * 64 else "1" * 64
    with pytest.raises(ContractError) as exc:
        _validate(blueprint, manifest, pin=wrong_pin)
    assert _reason(exc) == "blueprint_external_pin_mismatch"


def test_blueprint_self_hash_tamper_fails_closed() -> None:
    blueprint, manifest = _blueprint()
    blueprint["blueprint_sha256"] = "0" * 64
    with pytest.raises(ContractError) as exc:
        _validate(blueprint, manifest, pin="0" * 64)
    assert _reason(exc) == "blueprint_self_hash_mismatch"


@pytest.mark.parametrize(
    ("field", "expected", "reason"),
    [
        ("domain_id", "other_domain", "domain_pin_mismatch"),
        ("environment", "production", "environment_pin_mismatch"),
    ],
)
def test_identity_pin_mismatch_fails_closed(field: str, expected: str, reason: str) -> None:
    blueprint, manifest = _blueprint()
    kwargs = {
        "expected_blueprint_sha256": blueprint["blueprint_sha256"],
        "expected_domain_id": "order_sales",
        "expected_environment": "test",
        "source_manifest": manifest,
    }
    kwargs[f"expected_{field}"] = expected
    with pytest.raises(ContractError) as exc:
        validate_executable_blueprint(blueprint, **kwargs)
    assert _reason(exc) == reason


def test_different_valid_source_manifest_pin_fails_closed() -> None:
    blueprint, manifest = _blueprint()
    other_manifest = _reseal_manifest(manifest, source_sha256="0" * 64)
    with pytest.raises(ContractError) as exc:
        _validate(blueprint, other_manifest)
    assert _reason(exc) == "source_manifest_pin_mismatch"


def test_tampered_source_manifest_fails_closed() -> None:
    blueprint, manifest = _blueprint()
    manifest["source_sha256"] = "0" * 64
    with pytest.raises(ContractError) as exc:
        _validate(blueprint, manifest)
    assert _reason(exc) == "source_manifest_invalid"


def test_build_rejects_source_inventory_coverage_gap() -> None:
    draft = _draft()
    manifest = _manifest()
    draft["metrics"].pop("SALES_AMOUNT")
    with pytest.raises(ContractError) as exc:
        build_executable_blueprint(
            draft,
            domain_id="order_sales",
            environment="test",
            source_manifest=manifest,
        )
    assert _reason(exc) == "source_coverage_incomplete"


def test_executable_missing_or_unknown_section_fails_closed() -> None:
    blueprint, manifest = _blueprint()
    blueprint["executable"].pop("relations")
    blueprint["executable"]["llm_payload"] = {}
    blueprint["executable_sha256"] = sha256_json(blueprint["executable"])
    blueprint["blueprint_sha256"] = compute_blueprint_sha256(blueprint)
    with pytest.raises(ContractError):
        _validate(blueprint, manifest, pin=blueprint["blueprint_sha256"])
