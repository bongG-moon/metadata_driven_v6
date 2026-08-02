from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

import pytest

from reference_runtime.authoring_source_manifest import (
    AuthoringSourceManifestError,
    extract_authoring_source_manifest,
    normalize_authoring_draft_shorthand,
    normalize_authoring_section_patch_shorthand,
    normalize_draft_alias_shorthand,
    validate_draft_inventory_coverage,
)
from reference_runtime.contracts import validate_contract
from reference_runtime.domain_authoring_patches import (
    apply_authoring_section_patch,
    runtime_catalog_v2_to_authoring_draft,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "validation" / "order_sales_metadata_input.txt"
DRAFT_PATH = ROOT / "metadata" / "domain_packs" / "order_sales" / "authoring_draft.json"
MANUFACTURING_PACKAGE_PATH = (
    ROOT / "metadata" / "domain_packs" / "manufacturing" / "compiled" / "domain_package.json"
)
ENDPOINT_DECLARATION = (
    " \ub4f1\ub85d relation endpoint\ub294 orders_products=orders->products, "
    "orders_refunds=orders->refunds, sales_targets=orders->targets\uc774\ub2e4."
)
RELATION_KEY_DECLARATION = (
    " \ub4f1\ub85d relation key\ub294 orders_products=PRODUCT_ID->PRODUCT_ID, "
    "orders_refunds=ORDER_ID|PRODUCT_ID->ORDER_ID|PRODUCT_ID, "
    "sales_targets=PRODUCT_ID->PRODUCT_ID\uc774\ub2e4."
)


def _source() -> str:
    return SOURCE_PATH.read_text(encoding="utf-8")


def _draft() -> dict:
    return json.loads(DRAFT_PATH.read_text(encoding="utf-8"))


def _covered_draft() -> dict:
    draft = _draft()
    aliases = draft["metrics"]["TARGET_AMOUNT"].setdefault("aliases", [])
    if "목표액" not in aliases:
        aliases.append("목표액")
    return draft


def _manifest() -> dict:
    return extract_authoring_source_manifest(_source())


def _manufacturing_draft() -> dict:
    package = json.loads(MANUFACTURING_PACKAGE_PATH.read_text(encoding="utf-8"))
    return runtime_catalog_v2_to_authoring_draft(package["runtime_catalog"])


def _validate(manifest: dict, draft: dict) -> dict:
    return validate_draft_inventory_coverage(
        manifest,
        draft,
        supported_operations=manifest["inventories"]["operations"],
    )


def test_dataset_section_patch_normalization_does_not_synthesize_aliases() -> None:
    patch = {"datasets": {"products": {"display_name": "상품 기준정보"}}}

    normalized = normalize_authoring_section_patch_shorthand(
        _manifest(),
        patch,
        "dataset",
    )

    assert normalized == patch
    assert "aliases" not in normalized


def test_dataset_section_patch_preserves_explicit_cross_owner_key_for_rejection() -> None:
    patch = {
        "datasets": {"products": {"display_name": "상품 기준정보"}},
        "aliases": {"forbidden": {"target_type": "dataset", "target_key": "products", "values": ["상품"]}},
    }

    normalized = normalize_authoring_section_patch_shorthand(
        _manifest(),
        patch,
        "dataset",
    )

    assert normalized == patch
    assert "aliases" in normalized


def test_dataset_patch_maps_unique_physical_name_to_source_declared_canonical_noop() -> None:
    source = """equipment_assign 데이터셋은 장비 배정 현황입니다.
canonical 필드는 EQP_ID입니다.
"""
    base = _manufacturing_draft()
    original = deepcopy(base)
    base_field = deepcopy(base["datasets"]["equipment_assign"]["fields"]["EQP_ID"])

    for physical_reference in ({}, base_field):
        normalized = normalize_authoring_section_patch_shorthand(
            extract_authoring_source_manifest(source),
            {
                "datasets": {
                    "equipment_assign": {
                        "display_name": "장비 배정 현황",
                        "fields": {"EQUIP_ID": physical_reference},
                    }
                }
            },
            "dataset",
            base_draft=base,
        )

        equipment = normalized["datasets"]["equipment_assign"]
        assert "EQUIP_ID" not in equipment["fields"]
        assert equipment["fields"]["EQP_ID"] == base_field
        assert equipment["display_name"] == "장비 배정 현황"
        assert base == original


def test_dataset_patch_rejects_physical_alias_delta_and_unknown_targets() -> None:
    base = _manufacturing_draft()
    manifest = extract_authoring_source_manifest(
        "equipment_assign dataset is registered. Canonical fields are EQP_ID."
    )
    with pytest.raises(AuthoringSourceManifestError) as rebound:
        normalize_authoring_section_patch_shorthand(
            manifest,
            {
                "datasets": {
                    "equipment_assign": {
                        "fields": {"EQUIP_ID": {"semantic_type": "string"}}
                    }
                }
            },
            "dataset",
            base_draft=base,
        )
    assert rebound.value.code == "authoring_dataset_physical_alias_rebind_forbidden"

    with pytest.raises(AuthoringSourceManifestError) as dataset_unknown:
        normalize_authoring_section_patch_shorthand(
            manifest,
            {"datasets": {"production": {"display_name": "forbidden"}}},
            "dataset",
            base_draft=base,
        )
    assert dataset_unknown.value.code == "authoring_dataset_target_unknown"

    with pytest.raises(AuthoringSourceManifestError) as field_unknown:
        normalize_authoring_section_patch_shorthand(
            manifest,
            {"datasets": {"equipment_assign": {"fields": {"LOT_ID": {}}}}},
            "dataset",
            base_draft=base,
        )
    assert field_unknown.value.code == "authoring_dataset_field_target_unknown"


def test_dataset_patch_rejects_ambiguous_physical_binding() -> None:
    base = _manufacturing_draft()
    equipment_fields = base["datasets"]["equipment_assign"]["fields"]
    equipment_fields["LOT_ID"]["physical_aliases"] = ["EQUIP_ID"]
    manifest = extract_authoring_source_manifest(
        "equipment_assign dataset is registered. Canonical fields are EQP_ID, LOT_ID."
    )

    with pytest.raises(AuthoringSourceManifestError) as ambiguous:
        normalize_authoring_section_patch_shorthand(
            manifest,
            {"datasets": {"equipment_assign": {"fields": {"EQUIP_ID": {}}}}},
            "dataset",
            base_draft=base,
        )

    assert ambiguous.value.code == "authoring_dataset_field_target_ambiguous"


def test_dataset_patch_rejects_canonical_physical_duplicate_and_cross_dataset_lookup() -> None:
    base = _manufacturing_draft()
    equipment_manifest = extract_authoring_source_manifest(
        "equipment_assign dataset is registered. Canonical fields are EQP_ID."
    )

    with pytest.raises(AuthoringSourceManifestError) as duplicate:
        normalize_authoring_section_patch_shorthand(
            equipment_manifest,
            {
                "datasets": {
                    "equipment_assign": {
                        "fields": {"EQP_ID": {}, "EQUIP_ID": {}}
                    }
                }
            },
            "dataset",
            base_draft=base,
        )
    assert duplicate.value.code == "authoring_dataset_field_target_duplicate"

    production_manifest = extract_authoring_source_manifest(
        "production dataset is registered. Canonical fields are EQP_ID."
    )
    with pytest.raises(AuthoringSourceManifestError) as cross_dataset:
        normalize_authoring_section_patch_shorthand(
            production_manifest,
            {"datasets": {"production": {"fields": {"EQUIP_ID": {}}}}},
            "dataset",
            base_draft=base,
        )
    assert cross_dataset.value.code == "authoring_dataset_field_target_unknown"


def test_source_explicit_new_dataset_and_field_require_complete_schema_card() -> None:
    base = _manufacturing_draft()
    manifest = extract_authoring_source_manifest(
        "new_source dataset is registered. Canonical fields are NEW_ID."
    )
    complete_patch = {
        "datasets": {
            "new_source": {
                "family": "new_source",
                "source_type": "dummy",
                "fields": {
                    "NEW_ID": {
                        "physical_column": "new_id",
                        "semantic_type": "identifier",
                        "roles": ["filter", "output"],
                    }
                },
            }
        }
    }
    normalized = normalize_authoring_section_patch_shorthand(
        manifest,
        complete_patch,
        "dataset",
        base_draft=base,
    )
    merged = apply_authoring_section_patch(base, normalized, "dataset")
    assert merged["datasets"]["new_source"]["fields"]["NEW_ID"]["semantic_type"] == "identifier"

    with pytest.raises(AuthoringSourceManifestError) as invalid:
        normalize_authoring_section_patch_shorthand(
            manifest,
            {"datasets": {"new_source": {"fields": {"NEW_ID": {}}}}},
            "dataset",
            base_draft=base,
        )
    assert invalid.value.code == "authoring_field_role_inventory_missing"


def test_main_filter_section_patch_uses_base_as_read_only_target_context() -> None:
    source = """products dataset is declared. Canonical fields are CATEGORY.
Natural-language aliases: category and product category -> CATEGORY.
"""
    manifest = extract_authoring_source_manifest(source)
    base = _draft()
    base["aliases"]["field:CATEGORY"] = {
        "target_type": "field",
        "target_key": "CATEGORY",
        "values": ["existing category"],
    }
    original = deepcopy(base)

    normalized = normalize_authoring_section_patch_shorthand(
        manifest,
        {"aliases": {"category": "CATEGORY"}},
        "main_filter",
        base_draft=base,
    )

    assert base == original
    assert set(normalized) == {"aliases"}
    assert normalized["aliases"] == {
        "field:CATEGORY": {
            "target_type": "field",
            "target_key": "CATEGORY",
            "values": ["category", "existing category", "product category"],
        }
    }


def test_main_filter_section_patch_preserves_migrated_alias_priority_cards() -> None:
    source = """별칭 카드의 안정 식별자는 field:CATEGORY이고 대상 유형은 field, 대상 키는 CATEGORY입니다.
사용자가 '카테고리', '상품군'라고 말하면 CATEGORY 필드로 해석하세요.
"""
    base = _draft()
    base["aliases"]["field:CATEGORY"] = {
        "target_type": "field",
        "target_key": "CATEGORY",
        "values": [{"text": "카테고리", "priority": 70}],
        "match": "bounded_longest",
    }
    original = deepcopy(base)
    manifest = extract_authoring_source_manifest(source)

    normalized = normalize_authoring_section_patch_shorthand(
        manifest,
        {"aliases": {"카테고리": "CATEGORY", "상품군": "CATEGORY"}},
        "main_filter",
        base_draft=base,
    )

    assert base == original
    assert normalized["aliases"]["field:CATEGORY"]["values"] == [
        {"text": "카테고리", "priority": 70},
        "상품군",
    ]
    assert "match" not in normalized["aliases"]["field:CATEGORY"]
    merged = apply_authoring_section_patch(base, normalized, "main_filter")
    assert merged["aliases"]["field:CATEGORY"]["match"] == "bounded_longest"
    assert merged["aliases"]["field:CATEGORY"]["values"] == [
        {"text": "카테고리", "priority": 70},
        "상품군",
    ]
    assert validate_draft_inventory_coverage(manifest, merged)["passed"] is True


def test_alias_coverage_reads_only_exact_text_from_ranked_value_cards() -> None:
    manifest = extract_authoring_source_manifest(
        "Natural-language aliases: category -> CATEGORY."
    )
    ranked = {
        "datasets": {},
        "aliases": {
            "field:CATEGORY": {
                "target_type": "field",
                "target_key": "CATEGORY",
                "values": [{"text": "category", "priority": 70}],
            }
        },
    }
    original = deepcopy(ranked)

    assert validate_draft_inventory_coverage(manifest, ranked)["passed"] is True
    assert ranked == original

    non_string = deepcopy(ranked)
    non_string["aliases"]["field:CATEGORY"]["values"] = [
        {"text": {"nested": "category"}, "priority": 70}
    ]
    with pytest.raises(AuthoringSourceManifestError) as missing:
        validate_draft_inventory_coverage(manifest, non_string)
    assert missing.value.code == "authoring_source_coverage_incomplete"
    assert missing.value.evidence["counts"]["missing"]["aliases"] == 1


def test_ranked_alias_value_cannot_rebind_enclosing_target_identity() -> None:
    manifest = extract_authoring_source_manifest(
        "Natural-language aliases: category -> CATEGORY."
    )
    rebound = {
        "datasets": {},
        "aliases": {
            "field:PRODUCT_ID": {
                "target_type": "field",
                "target_key": "PRODUCT_ID",
                "values": [
                    {
                        "text": "category",
                        "priority": 70,
                        "target_key": "CATEGORY",
                    }
                ],
            }
        },
    }

    with pytest.raises(AuthoringSourceManifestError) as missing:
        validate_draft_inventory_coverage(manifest, rebound)

    assert missing.value.code == "authoring_source_coverage_incomplete"
    alias_missing = missing.value.evidence["missing"]["aliases"]
    assert len(alias_missing) == 1
    assert alias_missing[0].endswith(":CATEGORY")
    assert "PRODUCT_ID" not in json.dumps(alias_missing, ensure_ascii=False)


def test_main_filter_section_patch_preserves_cross_owner_root_for_rejection() -> None:
    base = _draft()
    original = deepcopy(base)
    patch = {
        "datasets": {"products": {"display_name": "forbidden"}},
        "aliases": {"category": "CATEGORY"},
    }

    normalized = normalize_authoring_section_patch_shorthand(
        extract_authoring_source_manifest(
            "products dataset is declared. Canonical fields are CATEGORY.\n"
            "Natural-language aliases: category -> CATEGORY."
        ),
        patch,
        "main_filter",
        base_draft=base,
    )

    assert normalized == patch
    assert base == original


def test_main_filter_section_patch_rejects_unknown_target_and_identity_rebind() -> None:
    base = _draft()
    missing_manifest = extract_authoring_source_manifest(
        "products dataset is declared. Canonical fields are UNKNOWN_FIELD.\n"
        "Natural-language aliases: unknown -> UNKNOWN_FIELD."
    )
    with pytest.raises(AuthoringSourceManifestError) as unknown:
        normalize_authoring_section_patch_shorthand(
            missing_manifest,
            {"aliases": {"unknown": "UNKNOWN_FIELD"}},
            "main_filter",
            base_draft=base,
        )
    assert unknown.value.code == "authoring_alias_target_unknown"

    base["aliases"]["field:CATEGORY"] = {
        "target_type": "field",
        "target_key": "CATEGORY",
        "values": ["category"],
    }
    no_alias_manifest = extract_authoring_source_manifest(
        "products dataset is declared. Canonical fields are CATEGORY."
    )
    with pytest.raises(AuthoringSourceManifestError) as rebound:
        normalize_authoring_section_patch_shorthand(
            no_alias_manifest,
            {
                "aliases": {
                    "field:CATEGORY": {
                        "target_type": "field",
                        "target_key": "PRODUCT_ID",
                        "values": ["category"],
                    }
                }
            },
            "main_filter",
            base_draft=base,
        )
    assert rebound.value.code == "authoring_alias_target_mismatch"


def test_order_sales_manifest_extracts_exact_inventory_without_source_retention() -> None:
    source = _source()
    first = extract_authoring_source_manifest(source)
    second = extract_authoring_source_manifest(source)

    assert first == second
    assert first["counts"] == {
        "datasets": 4,
        "fields": 10,
        "field_bindings": 14,
        "field_roles": 14,
        "metrics": 5,
        "grains": 4,
        "grain_keys": 4,
        "grain_display_fields": 4,
        "relations": 3,
        "relation_endpoints": 3,
        "relation_keys": 3,
        "relation_policies": 3,
        "recipes": 6,
        "operations": 8,
        "aliases": 11,
        "alias_targets": 8,
        "alias_bindings": 11,
    }
    assert first["inventories"]["datasets"] == ["orders", "products", "refunds", "targets"]
    assert first["inventories"]["metrics"] == [
        "ACHIEVEMENT_RATE",
        "NET_SALES_AMOUNT",
        "REFUND_AMOUNT",
        "SALES_AMOUNT",
        "TARGET_AMOUNT",
    ]
    assert first["inventories"]["relations"] == [
        "orders_products",
        "orders_refunds",
        "sales_targets",
    ]
    assert first["inventories"]["relation_endpoints"] == {
        "orders_products": {"left_dataset": "orders", "right_dataset": "products"},
        "orders_refunds": {"left_dataset": "orders", "right_dataset": "refunds"},
        "sales_targets": {"left_dataset": "orders", "right_dataset": "targets"},
    }
    assert first["inventories"]["field_roles"]["orders"]["CUSTOMER_ID"] == [
        "filter",
        "group",
        "join",
        "project",
        "output",
    ]
    assert first["inventories"]["relation_keys"] == {
        "orders_products": {"left_keys": ["PRODUCT_ID"], "right_keys": ["PRODUCT_ID"]},
        "orders_refunds": {
            "left_keys": ["ORDER_ID", "PRODUCT_ID"],
            "right_keys": ["ORDER_ID", "PRODUCT_ID"],
        },
        "sales_targets": {"left_keys": ["PRODUCT_ID"], "right_keys": ["PRODUCT_ID"]},
    }
    assert first["inventories"]["relation_policies"]["orders_products"] == {
        "join_type": "left",
        "cardinality": "many_to_one",
        "null_key_policy": "never_match",
        "multi_match_policy": "fail",
    }
    assert first["inventories"]["grain_keys"] == {
        "customer": ["CUSTOMER_ID"],
        "date_product": ["TARGET_DATE", "PRODUCT_ID"],
        "order": ["ORDER_ID"],
        "product": ["PRODUCT_ID"],
    }
    assert first["inventories"]["grain_display_fields"] == {
        "customer": [],
        "date_product": [],
        "order": [],
        "product": ["PRODUCT_NAME", "CATEGORY"],
    }
    assert first["inventories"]["operations"] == [
        "aggregate",
        "compare_fields",
        "derive",
        "filter",
        "join",
        "project",
        "rank",
        "sort",
    ]
    assert set(first["inventories"]["recipes"]) == {
        "sales.summary",
        "sales.by_product",
        "sales.rank",
        "sales.net_by_product",
        "sales.target_comparison",
        "sales.detail_projection",
    }
    assert len(first["manifest_sha256"]) == 64
    serialized = json.dumps(first, ensure_ascii=False, sort_keys=True)
    assert "source_text" not in first
    assert source not in serialized
    assert "이 도메인은 주문, 상품, 환불, 매출 목표를 분석한다" not in serialized


def test_source_manifest_canonicalizes_bom_line_endings_and_outer_whitespace() -> None:
    source = _source().strip()
    baseline = extract_authoring_source_manifest(source)
    decorated = "\ufeff  \r\n" + source.replace("\n", "\r\n") + "\r\n\t "

    assert extract_authoring_source_manifest(decorated) == baseline


def test_english_explicit_inventory_and_alias_mapping_are_supported() -> None:
    source = """orders dataset is historical orders.
Canonical fields are ORDER_ID, SALES_AMOUNT.
Registered metrics are SALES_AMOUNT.
Relations are orders_products.
Allowed operations are filter, project.
Registered recipe IDs are sales.summary.
Natural-language aliases: sales and order amount -> SALES_AMOUNT, order -> ORDER_ID.
"""
    manifest = extract_authoring_source_manifest(source)

    assert manifest["counts"] == {
        "datasets": 1,
        "fields": 2,
        "field_bindings": 2,
        "field_roles": 0,
        "metrics": 1,
        "grains": 0,
        "grain_keys": 0,
        "grain_display_fields": 0,
        "relations": 1,
        "relation_endpoints": 0,
        "relation_keys": 0,
        "relation_policies": 0,
        "recipes": 1,
        "operations": 2,
        "aliases": 3,
        "alias_targets": 2,
        "alias_bindings": 3,
    }
    assert manifest["inventories"]["alias_bindings"] == [
        {"alias": "order", "target": "ORDER_ID"},
        {"alias": "order amount", "target": "SALES_AMOUNT"},
        {"alias": "sales", "target": "SALES_AMOUNT"},
    ]


def test_korean_explicit_alias_card_extracts_target_key_without_particle_false_positive() -> None:
    source = """기존 주문·매출 도메인의 메인 필터 별칭을 추가합니다.
별칭 카드의 안정 식별자는 field:CATEGORY이고 대상 유형은 field, 대상 키는 CATEGORY입니다.
사용자가 '카테고리', '상품군', '상품 분류'라고 말하면 CATEGORY 필드로 해석하세요.
aliases 섹션만 수정하고 데이터셋, 지표, 관계, 출력 정책은 그대로 유지하세요.
"""

    manifest = extract_authoring_source_manifest(source)

    assert manifest["inventories"]["alias_bindings"] == [
        {"alias": "상품 분류", "target": "CATEGORY"},
        {"alias": "상품군", "target": "CATEGORY"},
        {"alias": "카테고리", "target": "CATEGORY"},
    ]
    assert manifest["inventories"]["alias_targets"] == ["CATEGORY"]
    assert manifest["required_sections"] == ["aliases"]


def test_korean_explicit_alias_card_rejects_identity_target_mismatch() -> None:
    source = """별칭 카드의 안정 식별자는 field:CATEGORY이고 대상 유형은 field, 대상 키는 PRODUCT_ID입니다.
사용자가 '카테고리'라고 말하면 CATEGORY 필드로 해석하세요.
"""

    with pytest.raises(AuthoringSourceManifestError) as raised:
        extract_authoring_source_manifest(source)

    assert raised.value.code == "authoring_alias_card_declaration_invalid"


def test_recipe_id_field_prose_is_not_treated_as_recipe_inventory() -> None:
    source = """RECIPE_ID\ub294 Recipe ID \ud544\ud130\uc57c.
\ubcc4\uce6d \uce74\ub4dc\uc758 \uc548\uc815 \uc2dd\ubcc4\uc790\ub294 field:RECIPE_ID\uc774\uace0 \ub300\uc0c1 \uc720\ud615\uc740 field, \ub300\uc0c1 \ud0a4\ub294 RECIPE_ID\uc785\ub2c8\ub2e4.
\uc0ac\uc6a9\uc790\uac00 'RECIPE_ID', 'Recipe ID', '\ub808\uc2dc\ud53c'\ub77c\uace0 \ub9d0\ud558\uba74 RECIPE_ID \ud544\ub4dc\ub85c \ud574\uc11d\ud558\uc138\uc694.
"""

    manifest = extract_authoring_source_manifest(source)

    assert manifest["inventories"]["recipes"] == []
    assert manifest["required_sections"] == ["aliases"]
    assert manifest["inventories"]["alias_bindings"] == [
        {"alias": "recipe id", "target": "RECIPE_ID"},
        {"alias": "recipe_id", "target": "RECIPE_ID"},
        {"alias": "\ub808\uc2dc\ud53c", "target": "RECIPE_ID"},
    ]


def test_complete_schema_valid_order_sales_draft_passes_with_safe_evidence() -> None:
    manifest = _manifest()
    draft = _covered_draft()
    validate_contract(draft, "metadata-authoring-draft.schema.json")

    evidence = _validate(manifest, draft)

    assert evidence["passed"] is True
    assert all(value == 0 for value in evidence["counts"]["missing"].values())
    assert all(not values for values in evidence["missing"].values())
    serialized = json.dumps(evidence, ensure_ascii=False, sort_keys=True)
    assert _source() not in serialized
    assert "provider_output" not in serialized


@pytest.mark.parametrize("section", ["metrics", "relations", "recipes"])
def test_schema_valid_empty_explicit_section_is_rejected(section: str) -> None:
    manifest = _manifest()
    draft = _covered_draft()
    draft[section] = {}
    validate_contract(draft, "metadata-authoring-draft.schema.json")

    with pytest.raises(AuthoringSourceManifestError) as raised:
        _validate(manifest, draft)

    assert raised.value.code == "authoring_source_coverage_incomplete"
    evidence = raised.value.evidence
    assert evidence["passed"] is False
    assert evidence["counts"]["missing"][section] > 0
    assert section in evidence["missing"]["required_sections"]


def test_one_explicit_identifier_omission_is_rejected() -> None:
    manifest = _manifest()
    draft = _covered_draft()
    draft["metrics"].pop("ACHIEVEMENT_RATE")
    validate_contract(draft, "metadata-authoring-draft.schema.json")

    with pytest.raises(AuthoringSourceManifestError) as raised:
        _validate(manifest, draft)

    evidence = raised.value.evidence
    assert evidence["missing"]["metrics"] == ["ACHIEVEMENT_RATE"]
    assert evidence["counts"]["missing"]["metrics"] == 1
    assert all(len(items) <= 32 for items in evidence["missing"].values())


def test_explicit_alias_target_omission_returns_only_hashed_alias_evidence() -> None:
    manifest = _manifest()
    draft = _covered_draft()
    draft["metrics"]["ACHIEVEMENT_RATE"]["aliases"] = ["target achievement rate"]

    with pytest.raises(AuthoringSourceManifestError) as raised:
        _validate(manifest, draft)

    evidence = raised.value.evidence
    assert evidence["counts"]["missing"]["aliases"] == 1
    assert len(evidence["missing"]["aliases"]) == 1
    assert "달성률" not in json.dumps(evidence, ensure_ascii=False)
    alias_hash, target = evidence["missing"]["aliases"][0].split(":", 1)
    assert len(alias_hash) == 64
    assert target == "ACHIEVEMENT_RATE"


def test_missing_evidence_is_bounded_and_manifest_hash_is_fail_closed() -> None:
    source = "\n".join(
        f"dataset_{index} dataset is declared. Canonical fields are FIELD_{index}."
        for index in range(40)
    )
    manifest = extract_authoring_source_manifest(source)
    with pytest.raises(AuthoringSourceManifestError) as raised:
        validate_draft_inventory_coverage(manifest, {"datasets": {}})
    evidence = raised.value.evidence
    assert len(evidence["missing"]["datasets"]) == 32
    assert evidence["missing_truncated"]["datasets"] == 8
    assert len(evidence["missing"]["fields"]) == 32
    assert evidence["missing_truncated"]["fields"] == 8

    tampered = deepcopy(manifest)
    tampered["counts"]["datasets"] = 39
    with pytest.raises(AuthoringSourceManifestError) as tamper_error:
        validate_draft_inventory_coverage(tampered, {"datasets": {}})
    assert tamper_error.value.code == "authoring_source_manifest_hash_mismatch"


def test_korean_alias_shorthand_compiles_to_schema_valid_canonical_card_without_mutation() -> None:
    manifest = _manifest()
    draft = _draft()
    draft["aliases"] = {"\ub2ec\uc131\ub960": "ACHIEVEMENT_RATE"}
    original = deepcopy(draft)

    normalized = normalize_draft_alias_shorthand(manifest, draft)

    assert draft == original
    assert normalized is not draft
    assert normalized["aliases"] == {
        "metric:ACHIEVEMENT_RATE": {
            "target_type": "metric",
            "target_key": "ACHIEVEMENT_RATE",
            "values": ["\ub2ec\uc131\ub960"],
        }
    }
    validate_contract(normalized, "metadata-authoring-draft.schema.json")


def test_multiple_manifest_backed_shorthand_labels_merge_into_one_card() -> None:
    manifest = _manifest()
    draft = _draft()
    # SALES_AMOUNT is deliberately removed from the field namespace here so
    # its registered metric target has one and only one possible type.
    draft["datasets"]["orders"]["fields"].pop("SALES_AMOUNT")
    draft["aliases"] = {
        "\uc8fc\ubb38\uae08\uc561": "SALES_AMOUNT",
        "\ub9e4\ucd9c": "SALES_AMOUNT",
    }

    normalized = normalize_draft_alias_shorthand(manifest, draft)

    assert normalized["aliases"] == {
        "metric:SALES_AMOUNT": {
            "target_type": "metric",
            "target_key": "SALES_AMOUNT",
            "values": ["\ub9e4\ucd9c", "\uc8fc\ubb38\uae08\uc561"],
        }
    }


def test_alias_shorthand_rejects_manifest_backed_target_missing_from_draft() -> None:
    draft = _draft()
    draft["metrics"].pop("ACHIEVEMENT_RATE")
    draft["aliases"] = {"\ub2ec\uc131\ub960": "ACHIEVEMENT_RATE"}

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_draft_alias_shorthand(_manifest(), draft)

    assert raised.value.code == "authoring_alias_target_unknown"
    assert "\ub2ec\uc131\ub960" not in json.dumps(raised.value.evidence, ensure_ascii=False)


def test_alias_shorthand_rejects_label_not_declared_in_source_manifest() -> None:
    draft = _draft()
    draft["aliases"] = {"\ubbf8\ub4f1\ub85d \ubcc4\uce6d": "ACHIEVEMENT_RATE"}

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_draft_alias_shorthand(_manifest(), draft)

    assert raised.value.code == "authoring_alias_shorthand_unbacked"
    assert "\ubbf8\ub4f1\ub85d \ubcc4\uce6d" not in json.dumps(raised.value.evidence, ensure_ascii=False)


def test_alias_shorthand_rejects_target_registered_in_multiple_namespaces() -> None:
    draft = _draft()
    draft["datasets"]["orders"]["fields"]["ACHIEVEMENT_RATE"] = deepcopy(
        draft["datasets"]["orders"]["fields"]["SALES_AMOUNT"]
    )
    draft["aliases"] = {"\ub2ec\uc131\ub960": "ACHIEVEMENT_RATE"}

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_draft_alias_shorthand(_manifest(), draft)

    assert raised.value.code == "authoring_alias_target_ambiguous"
    assert raised.value.evidence["target_types"] == ["field", "metric"]


def test_alias_shorthand_rejects_object_string_target_collision() -> None:
    draft = _draft()
    draft["aliases"] = {
        "metric:ACHIEVEMENT_RATE": {
            "target_type": "metric",
            "target_key": "ACHIEVEMENT_RATE",
            "values": ["achievement rate"],
        },
        "\ub2ec\uc131\ub960": "ACHIEVEMENT_RATE",
    }

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_draft_alias_shorthand(_manifest(), draft)

    assert raised.value.code == "authoring_alias_object_string_collision"


def test_source_sealed_field_role_representation_is_normalized_and_deduplicated() -> None:
    draft = _draft()
    roles = [
        "filter",
        "compare_fields",
        "aggregate",
        "project",
        "sort",
        "rank",
        "metric",
        "output",
        "compare_fields",
    ]
    draft["datasets"]["orders"]["fields"]["SALES_AMOUNT"]["roles"] = roles
    original = deepcopy(draft)

    normalized = normalize_draft_alias_shorthand(_manifest(), draft)

    assert draft == original
    assert normalized["datasets"]["orders"]["fields"]["SALES_AMOUNT"]["roles"] == [
        "filter",
        "compare",
        "aggregate",
        "project",
        "sort",
        "rank",
        "metric",
        "output",
    ]
    validate_contract(normalized, "metadata-authoring-draft.schema.json")


def test_unknown_field_role_fails_closed_without_raw_role_evidence() -> None:
    draft = _draft()
    draft["datasets"]["orders"]["fields"]["SALES_AMOUNT"]["roles"] = [
        "filter",
        "compare_columns",
        "compare_columns",
        "output",
    ]

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_draft_alias_shorthand(_manifest(), draft)

    assert raised.value.code == "authoring_field_role_value_invalid"
    assert "compare_columns" not in json.dumps(raised.value.evidence, ensure_ascii=False)


def test_relation_endpoints_fill_all_three_cards_and_remove_exact_legacy_keys() -> None:
    manifest = _manifest()
    draft = _draft()
    draft["relations"]["orders_products"]["left_dataset"] = ""
    draft["relations"]["orders_products"]["right_dataset"] = None
    draft["relations"]["orders_refunds"].pop("left_dataset")
    draft["relations"]["orders_refunds"].pop("right_dataset")
    targets = draft["relations"]["sales_targets"]
    targets["left"] = targets.pop("left_dataset")
    targets["right"] = targets.pop("right_dataset")
    original = deepcopy(draft)

    normalized = normalize_authoring_draft_shorthand(manifest, draft)

    assert draft == original
    assert normalized["relations"]["orders_products"]["left_dataset"] == "orders"
    assert normalized["relations"]["orders_products"]["right_dataset"] == "products"
    assert normalized["relations"]["orders_refunds"]["left_dataset"] == "orders"
    assert normalized["relations"]["orders_refunds"]["right_dataset"] == "refunds"
    assert normalized["relations"]["sales_targets"]["left_dataset"] == "orders"
    assert normalized["relations"]["sales_targets"]["right_dataset"] == "targets"
    assert "left" not in normalized["relations"]["sales_targets"]
    assert "right" not in normalized["relations"]["sales_targets"]
    validate_contract(normalized, "metadata-authoring-draft.schema.json")
    assert _validate(manifest, normalized)["passed"] is True


def test_english_relation_endpoint_inventory_accepts_unicode_arrow() -> None:
    source = """orders dataset is declared. Canonical fields are ORDER_ID.
products dataset is declared. Canonical fields are PRODUCT_ID.
Relations are orders_products.
Registered relation endpoints are orders_products=orders\u2192products.
"""

    manifest = extract_authoring_source_manifest(source)

    assert manifest["inventories"]["relation_endpoints"] == {
        "orders_products": {"left_dataset": "orders", "right_dataset": "products"}
    }
    assert manifest["counts"]["relation_endpoints"] == 1


def test_relation_endpoint_nonblank_mismatch_fails_closed_without_raw_value() -> None:
    draft = _draft()
    draft["relations"]["orders_products"]["left_dataset"] = "refunds"

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_authoring_draft_shorthand(_manifest(), draft)

    assert raised.value.code == "authoring_relation_endpoint_mismatch"
    assert "refunds" not in json.dumps(raised.value.evidence, ensure_ascii=False)


def test_relation_endpoint_unknown_draft_dataset_fails_closed() -> None:
    draft = _draft()
    draft["datasets"].pop("products")
    draft["relations"]["orders_products"].pop("left_dataset")
    draft["relations"]["orders_products"].pop("right_dataset")

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_authoring_draft_shorthand(_manifest(), draft)

    assert raised.value.code == "authoring_relation_endpoint_dataset_unknown"


def test_relation_endpoint_source_rejects_unknown_dataset_and_ambiguity() -> None:
    unknown_source = _source().replace(
        "orders_products=orders->products",
        "orders_products=orders->missing_dataset",
        1,
    )
    with pytest.raises(AuthoringSourceManifestError) as unknown:
        extract_authoring_source_manifest(unknown_source)
    assert unknown.value.code == "authoring_relation_endpoint_dataset_unknown"

    ambiguous_source = _source() + (
        "\n\ub4f1\ub85d relation endpoint\ub294 "
        "orders_products=refunds->products\uc774\ub2e4.\n"
    )
    with pytest.raises(AuthoringSourceManifestError) as ambiguous:
        extract_authoring_source_manifest(ambiguous_source)
    assert ambiguous.value.code == "authoring_relation_endpoint_ambiguous"


def test_blank_relation_endpoint_without_source_inventory_fails_closed() -> None:
    source_without_endpoints = (
        _source()
        .replace(ENDPOINT_DECLARATION, "")
        .replace(RELATION_KEY_DECLARATION, "")
    )
    manifest = extract_authoring_source_manifest(source_without_endpoints)
    assert manifest["counts"]["relation_endpoints"] == 0
    draft = _draft()
    draft["relations"]["orders_products"].pop("left_dataset")

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_authoring_draft_shorthand(manifest, draft)

    assert raised.value.code == "authoring_relation_endpoint_inventory_missing"


def test_relation_endpoint_manifest_tamper_is_rejected_before_draft_mutation() -> None:
    manifest = _manifest()
    tampered = deepcopy(manifest)
    tampered["inventories"]["relation_endpoints"]["orders_products"]["left_dataset"] = "refunds"
    draft = _draft()
    original = deepcopy(draft)

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_authoring_draft_shorthand(tampered, draft)

    assert raised.value.code == "authoring_source_manifest_hash_mismatch"
    assert draft == original


def test_missing_manifest_aliases_are_completed_only_on_unique_targets() -> None:
    draft = _draft()
    draft["metrics"]["NET_SALES_AMOUNT"]["aliases"] = []
    draft["metrics"]["ACHIEVEMENT_RATE"]["aliases"] = []

    normalized = normalize_authoring_draft_shorthand(_manifest(), draft)

    assert normalized["aliases"]["metric:NET_SALES_AMOUNT"] == {
        "target_type": "metric",
        "target_key": "NET_SALES_AMOUNT",
        "values": ["\uc21c\ub9e4\ucd9c"],
    }
    assert normalized["aliases"]["metric:ACHIEVEMENT_RATE"] == {
        "target_type": "metric",
        "target_key": "ACHIEVEMENT_RATE",
        "values": ["\ub2ec\uc131\ub960"],
    }
    validate_contract(normalized, "metadata-authoring-draft.schema.json")
    assert _validate(_manifest(), normalized)["passed"] is True


def test_missing_manifest_alias_stably_merges_into_one_existing_target_card() -> None:
    draft = _draft()
    draft["metrics"]["ACHIEVEMENT_RATE"]["aliases"] = []
    draft["aliases"]["metric:ACHIEVEMENT_RATE"] = {
        "target_type": "metric",
        "target_key": "ACHIEVEMENT_RATE",
        "values": ["target achievement rate"],
    }

    normalized = normalize_authoring_draft_shorthand(_manifest(), draft)

    assert normalized["aliases"]["metric:ACHIEVEMENT_RATE"]["values"] == [
        "target achievement rate",
        "\ub2ec\uc131\ub960",
    ]


def test_manifest_alias_completion_rejects_conflict_and_multiple_target_cards() -> None:
    conflict = _draft()
    conflict["metrics"]["ACHIEVEMENT_RATE"]["aliases"] = []
    conflict["aliases"]["wrong:binding"] = {
        "target_type": "metric",
        "target_key": "NET_SALES_AMOUNT",
        "values": ["\ub2ec\uc131\ub960"],
    }
    with pytest.raises(AuthoringSourceManifestError) as conflicting:
        normalize_authoring_draft_shorthand(_manifest(), conflict)
    assert conflicting.value.code == "authoring_alias_label_target_conflict"

    multiple = _draft()
    multiple["aliases"]["net:first"] = {
        "target_type": "metric",
        "target_key": "NET_SALES_AMOUNT",
        "values": ["net sales"],
    }
    multiple["aliases"]["net:second"] = {
        "target_type": "metric",
        "target_key": "NET_SALES_AMOUNT",
        "values": ["net amount"],
    }
    with pytest.raises(AuthoringSourceManifestError) as duplicated:
        normalize_authoring_draft_shorthand(_manifest(), multiple)
    assert duplicated.value.code == "authoring_alias_multiple_target_cards"


def test_source_sealed_field_roles_fill_blank_and_canonicalize_representation() -> None:
    draft = _draft()
    draft["datasets"]["orders"]["fields"]["CUSTOMER_ID"]["roles"] = []
    draft["datasets"]["orders"]["fields"]["SALES_AMOUNT"]["roles"] = [
        "output",
        "metric",
        "rank",
        "sort",
        "project",
        "aggregate",
        "compare_fields",
        "filter",
    ]
    original = deepcopy(draft)

    normalized = normalize_authoring_draft_shorthand(_manifest(), draft)

    assert draft == original
    assert normalized["datasets"]["orders"]["fields"]["CUSTOMER_ID"]["roles"] == [
        "filter",
        "group",
        "join",
        "project",
        "output",
    ]
    assert normalized["datasets"]["orders"]["fields"]["SALES_AMOUNT"]["roles"] == [
        "filter",
        "compare",
        "aggregate",
        "project",
        "sort",
        "rank",
        "metric",
        "output",
    ]
    validate_contract(normalized, "metadata-authoring-draft.schema.json")


def test_source_sealed_field_roles_reject_nonblank_mismatch() -> None:
    draft = _draft()
    draft["datasets"]["orders"]["fields"]["CUSTOMER_ID"]["roles"] = [
        "filter",
        "project",
        "output",
    ]

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_authoring_draft_shorthand(_manifest(), draft)

    assert raised.value.code == "authoring_field_role_mismatch"


def test_field_role_source_rejects_unknown_binding_value_and_ambiguity() -> None:
    unknown_binding = _source().replace("orders.ORDER_ID=", "orders.UNKNOWN_FIELD=", 1)
    with pytest.raises(AuthoringSourceManifestError) as binding_error:
        extract_authoring_source_manifest(unknown_binding)
    assert binding_error.value.code == "authoring_field_role_binding_unknown"

    unknown_value = _source().replace(
        "orders.ORDER_ID=filter|join|project|output",
        "orders.ORDER_ID=filter|identifier|project|output",
        1,
    )
    with pytest.raises(AuthoringSourceManifestError) as value_error:
        extract_authoring_source_manifest(unknown_value)
    assert value_error.value.code == "authoring_field_role_value_invalid"
    assert "identifier" not in json.dumps(value_error.value.evidence, ensure_ascii=False)

    ambiguous = _source() + (
        "\n\ub4f1\ub85d field role\uc740 "
        "orders.CUSTOMER_ID=filter|project|output\uc774\ub2e4.\n"
    )
    with pytest.raises(AuthoringSourceManifestError) as ambiguity_error:
        extract_authoring_source_manifest(ambiguous)
    assert ambiguity_error.value.code == "authoring_field_role_binding_ambiguous"


def test_blank_field_roles_without_source_inventory_fail_closed() -> None:
    source = re.sub(
        r"\s*\ub4f1\ub85d field role\uc740 .*?\uc774\ub2e4\.",
        "",
        _source(),
        count=1,
    )
    manifest = extract_authoring_source_manifest(source)
    assert manifest["counts"]["field_roles"] == 0
    draft = _draft()
    draft["datasets"]["orders"]["fields"]["CUSTOMER_ID"]["roles"] = []

    with pytest.raises(AuthoringSourceManifestError) as raised:
        normalize_authoring_draft_shorthand(manifest, draft)

    assert raised.value.code == "authoring_field_role_inventory_missing"


def test_relation_policies_fill_blank_and_canonicalize_hyphen_representation() -> None:
    draft = _draft()
    draft["relations"]["orders_products"]["join_type"] = ""
    draft["relations"]["orders_products"]["cardinality"] = "many-to-one"
    draft["relations"]["orders_refunds"].pop("null_key_policy")
    draft["relations"]["sales_targets"]["type"] = draft["relations"]["sales_targets"].pop("join_type")
    draft["relations"]["sales_targets"]["cardinality"] = "many-to-one"
    original = deepcopy(draft)

    normalized = normalize_authoring_draft_shorthand(_manifest(), draft)

    assert draft == original
    assert normalized["relations"]["orders_products"]["join_type"] == "left"
    assert normalized["relations"]["orders_products"]["cardinality"] == "many_to_one"
    assert normalized["relations"]["orders_refunds"]["null_key_policy"] == "never_match"
    assert normalized["relations"]["sales_targets"]["join_type"] == "left"
    assert normalized["relations"]["sales_targets"]["cardinality"] == "many_to_one"
    assert "type" not in normalized["relations"]["sales_targets"]
    validate_contract(normalized, "metadata-authoring-draft.schema.json")


def test_relation_policy_rejects_nonblank_mismatch_unknown_and_ambiguity() -> None:
    mismatch = _draft()
    mismatch["relations"]["orders_products"]["cardinality"] = "one_to_many"
    with pytest.raises(AuthoringSourceManifestError) as mismatch_error:
        normalize_authoring_draft_shorthand(_manifest(), mismatch)
    assert mismatch_error.value.code == "authoring_relation_policy_mismatch"

    unknown_value = _source().replace("cardinality:many_to_one", "cardinality:fan_out", 1)
    with pytest.raises(AuthoringSourceManifestError) as value_error:
        extract_authoring_source_manifest(unknown_value)
    assert value_error.value.code == "authoring_relation_policy_value_invalid"
    assert "fan_out" not in json.dumps(value_error.value.evidence, ensure_ascii=False)

    ambiguous = _source() + (
        "\n\ub4f1\ub85d relation policy\ub294 orders_products="
        "join_type:left|cardinality:one_to_many|null_key_policy:never_match|"
        "multi_match_policy:fail\uc774\ub2e4.\n"
    )
    with pytest.raises(AuthoringSourceManifestError) as ambiguity_error:
        extract_authoring_source_manifest(ambiguous)
    assert ambiguity_error.value.code == "authoring_relation_policy_ambiguous"


def test_blank_relation_policy_without_inventory_and_manifest_tamper_fail_closed() -> None:
    source = re.sub(
        r"\s*\ub4f1\ub85d relation policy\ub294 .*?\uc774\ub2e4\.",
        "",
        _source(),
        count=1,
    )
    manifest = extract_authoring_source_manifest(source)
    assert manifest["counts"]["relation_policies"] == 0
    draft = _draft()
    draft["relations"]["orders_products"]["cardinality"] = ""
    with pytest.raises(AuthoringSourceManifestError) as missing:
        normalize_authoring_draft_shorthand(manifest, draft)
    assert missing.value.code == "authoring_relation_policy_inventory_missing"

    tampered = _manifest()
    tampered["inventories"]["field_roles"]["orders"]["CUSTOMER_ID"] = ["project", "output"]
    with pytest.raises(AuthoringSourceManifestError) as field_tamper:
        normalize_authoring_draft_shorthand(tampered, _draft())
    assert field_tamper.value.code == "authoring_source_manifest_hash_mismatch"

    tampered = _manifest()
    tampered["inventories"]["relation_policies"]["orders_products"]["cardinality"] = "one_to_many"
    with pytest.raises(AuthoringSourceManifestError) as policy_tamper:
        normalize_authoring_draft_shorthand(tampered, _draft())
    assert policy_tamper.value.code == "authoring_source_manifest_hash_mismatch"


def test_relation_keys_fill_all_cards_and_remove_exact_legacy_shapes() -> None:
    draft = _draft()
    products = draft["relations"]["orders_products"]
    products.pop("left_keys")
    products.pop("right_keys")
    products["keys"] = ["PRODUCT_ID"]
    refunds = draft["relations"]["orders_refunds"]
    refunds.pop("left_keys")
    refunds.pop("right_keys")
    refunds["key_mappings"] = [
        {"left": "ORDER_ID", "right": "ORDER_ID"},
        {"left": "PRODUCT_ID", "right": "PRODUCT_ID"},
    ]
    targets = draft["relations"]["sales_targets"]
    targets["left_keys"] = ""
    targets["right_keys"] = []
    original = deepcopy(draft)

    normalized = normalize_authoring_draft_shorthand(_manifest(), draft)

    assert draft == original
    assert normalized["relations"]["orders_products"]["left_keys"] == ["PRODUCT_ID"]
    assert normalized["relations"]["orders_products"]["right_keys"] == ["PRODUCT_ID"]
    assert "keys" not in normalized["relations"]["orders_products"]
    assert normalized["relations"]["orders_refunds"]["left_keys"] == ["ORDER_ID", "PRODUCT_ID"]
    assert normalized["relations"]["orders_refunds"]["right_keys"] == ["ORDER_ID", "PRODUCT_ID"]
    assert "key_mappings" not in normalized["relations"]["orders_refunds"]
    assert normalized["relations"]["sales_targets"]["left_keys"] == ["PRODUCT_ID"]
    assert normalized["relations"]["sales_targets"]["right_keys"] == ["PRODUCT_ID"]
    validate_contract(normalized, "metadata-authoring-draft.schema.json")
    assert _validate(_manifest(), normalized)["passed"] is True


def test_relation_key_nonblank_or_legacy_mismatch_fails_closed() -> None:
    draft = _draft()
    draft["relations"]["orders_products"]["left_keys"] = ["ORDER_ID"]
    with pytest.raises(AuthoringSourceManifestError) as nonblank:
        normalize_authoring_draft_shorthand(_manifest(), draft)
    assert nonblank.value.code == "authoring_relation_key_mismatch"

    draft = _draft()
    draft["relations"]["orders_products"].pop("left_keys")
    draft["relations"]["orders_products"].pop("right_keys")
    draft["relations"]["orders_products"]["keys"] = ["ORDER_ID"]
    with pytest.raises(AuthoringSourceManifestError) as legacy:
        normalize_authoring_draft_shorthand(_manifest(), draft)
    assert legacy.value.code == "authoring_relation_key_mismatch"


def test_relation_key_source_rejects_unknown_field_cardinality_and_ambiguity() -> None:
    unknown = _source().replace(
        "orders_products=PRODUCT_ID->PRODUCT_ID",
        "orders_products=UNKNOWN_FIELD->PRODUCT_ID",
        1,
    )
    with pytest.raises(AuthoringSourceManifestError) as field_error:
        extract_authoring_source_manifest(unknown)
    assert field_error.value.code == "authoring_relation_key_field_unknown"
    assert "UNKNOWN_FIELD" not in json.dumps(field_error.value.evidence, ensure_ascii=False)

    wrong_count = _source().replace(
        "orders_refunds=ORDER_ID|PRODUCT_ID->ORDER_ID|PRODUCT_ID",
        "orders_refunds=ORDER_ID|PRODUCT_ID->ORDER_ID",
        1,
    )
    with pytest.raises(AuthoringSourceManifestError) as count_error:
        extract_authoring_source_manifest(wrong_count)
    assert count_error.value.code == "authoring_relation_key_cardinality_invalid"

    ambiguous = _source() + (
        "\n\ub4f1\ub85d relation key\ub294 "
        "orders_products=ORDER_ID->PRODUCT_ID\uc774\ub2e4.\n"
    )
    with pytest.raises(AuthoringSourceManifestError) as ambiguity_error:
        extract_authoring_source_manifest(ambiguous)
    assert ambiguity_error.value.code == "authoring_relation_key_ambiguous"


def test_blank_relation_key_without_inventory_and_manifest_tamper_fail_closed() -> None:
    manifest = extract_authoring_source_manifest(_source().replace(RELATION_KEY_DECLARATION, ""))
    assert manifest["counts"]["relation_keys"] == 0
    draft = _draft()
    draft["relations"]["orders_products"].pop("left_keys")
    with pytest.raises(AuthoringSourceManifestError) as missing:
        normalize_authoring_draft_shorthand(manifest, draft)
    assert missing.value.code == "authoring_relation_key_inventory_missing"

    tampered = _manifest()
    tampered["inventories"]["relation_keys"]["orders_products"]["left_keys"] = ["ORDER_ID"]
    with pytest.raises(AuthoringSourceManifestError) as tamper:
        normalize_authoring_draft_shorthand(tampered, _draft())
    assert tamper.value.code == "authoring_source_manifest_hash_mismatch"
