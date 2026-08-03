from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

import pytest

from tools.rebuild_domain_pack_from_blueprint import _apply_overrides


ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = ROOT / "metadata" / "domain_packs" / "manufacturing"
DATASET_SOURCE = ROOT / "metadata" / "authoring" / "v6_inputs" / "dataset_v6.txt"
DATASET_VARIANT_SOURCE = (
    ROOT
    / "validation"
    / "fixtures"
    / "authoring"
    / "freeform_reordered_v1"
    / "dataset_v6.txt"
)
DATASET_BUSINESS_LABELS = (
    "당일 생산 실적",
    "생산 이력",
    "현재 재공",
    "재공 이력",
    "생산 계획",
    "장비 배정 현황",
    "장비·제품별 UPH",
    "현재 LOT 현황",
    "HOLD 이력",
    "제품 기준정보",
)
DATASET_START = re.compile(
    r"(?m)^.*?는\s+([a-z][a-z0-9_]*)[으]?로\s+등록해줘\.?\s*$"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_field_override_removals_are_audited_and_idempotent() -> None:
    blueprint = _load_json(DOMAIN_ROOT / "trusted_executable_blueprint.json")
    overrides = _load_json(DOMAIN_ROOT / "field_binding_overrides.json")
    draft = deepcopy(blueprint["executable"])

    corrected, first_evidence = _apply_overrides(draft, overrides)
    expected_removed = {
        "equipment_assign": {
            "DIE_ATTACH_QTY",
            "FAB",
            "FACTORY",
            "FAMILY",
            "NETDIE_300_CNT",
            "SHIFT",
            "TSV_DIE_TYP",
        },
        "eqp_uph": {"FAMILY", "OPER_SEQ"},
        "lot_status": {"DEVICE_DESC"},
    }
    for dataset_id, field_ids in expected_removed.items():
        assert field_ids.isdisjoint(corrected["datasets"][dataset_id]["fields"])
    assert corrected["datasets"]["lot_status"]["fields"]["OPER_SEQ"][
        "required_in_source"
    ] is True
    assert first_evidence["applied_count"] == 11
    assert first_evidence["already_current_count"] == 0
    assert {
        (item["dataset_id"], item["field_id"], item["reason_code"])
        for item in first_evidence["applied_operations"]
    } == {
        (dataset_id, field_id, "source_projection_not_registered")
        for dataset_id, field_ids in expected_removed.items()
        for field_id in field_ids
    } | {("product_master", "DEN", "natural_source_binding_correction")}

    snapshot = deepcopy(corrected)
    corrected_again, second_evidence = _apply_overrides(corrected, overrides)
    assert corrected_again == snapshot
    assert second_evidence["applied_count"] == 0
    assert second_evidence["already_current_count"] == 11


def test_field_override_removal_rejects_descriptor_drift() -> None:
    blueprint = _load_json(DOMAIN_ROOT / "trusted_executable_blueprint.json")
    overrides = _load_json(DOMAIN_ROOT / "field_binding_overrides.json")
    draft = deepcopy(blueprint["executable"])
    draft["datasets"]["equipment_assign"]["fields"]["FAB"]["roles"].append(
        "derive"
    )

    with pytest.raises(ValueError, match="expected value mismatch"):
        _apply_overrides(draft, overrides)


def test_dataset_worker_input_is_freeform_with_deterministic_query_blocks() -> None:
    registry = _load_json(DOMAIN_ROOT / "approved_source_registry.json")
    assert len(registry["datasets"]) == len(DATASET_BUSINESS_LABELS) == 10

    forbidden_registration_syntax = (
        "dataset_id",
        "field_id",
        "source_binding",
        "config_ref",
        "query_ref",
        "physical_column",
        "pandas_function_cases",
    )
    for path in (DATASET_SOURCE, DATASET_VARIANT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert 1 <= len(source.encode("utf-8")) <= 65536
        assert all(label in source for label in DATASET_BUSINESS_LABELS)
        assert not any(token in source for token in forbidden_registration_syntax)
        assert not re.search(r"(?i)(password|api[_-]?key|mongodb(?:\+srv)?://|jdbc:|https?://)", source)

    baseline = DATASET_SOURCE.read_text(encoding="utf-8")
    assert baseline.count("query_template:") == 8
    assert re.search(r"(?im)^\s*(?:SELECT|WITH)\b", baseline)
    assert "{DATE}" in baseline and "{LOT_ID}" in baseline

    variant = DATASET_VARIANT_SOURCE.read_text(encoding="utf-8")
    assert "query_template:" not in variant
    assert not re.search(r"(?im)^\s*(SELECT|FROM|WHERE|JOIN)\b", variant)
    assert not DATASET_START.search(variant)

    assert not re.search(r"(?m)^\s{0,3}#{1,6}\s+", variant)
