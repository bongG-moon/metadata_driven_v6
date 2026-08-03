from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from reference_runtime.canonical import ContractError
from reference_runtime.metadata_collections import (
    DOMAIN_METADATA_COLLECTION,
    MAIN_FILTER_COLLECTION,
    TABLE_CATALOG_COLLECTION,
    assemble_domain_package_from_items,
    load_available_domain_package_from_three_collections,
    load_domain_package_from_three_collections,
    make_metadata_item_documents,
    make_partial_metadata_item_documents,
    metadata_item_set_projection,
    merge_metadata_items_for_write,
    replace_metadata_items,
    upsert_partial_metadata_items,
)


ROOT = Path(__file__).resolve().parents[1]
ITEM_FIELDS = {"_id", "section", "key", "natural_text", "payload", "updated_at"}


def _package() -> dict:
    return json.loads(
        (ROOT / "metadata/domain_packs/manufacturing/compiled/domain_package.json").read_text(
            encoding="utf-8"
        )
    )


class _Collection:
    def __init__(self) -> None:
        self.documents: dict[str, dict] = {}
        self.sessions: list[object] = []
        self.delete_calls = 0
        self.replace_calls = 0

    def find(self, query=None):
        del query
        return [deepcopy(item) for item in self.documents.values()]

    def delete_many(self, query: dict, session=None):
        self.delete_calls += 1
        self.sessions.append(session)
        keep = set(query.get("_id", {}).get("$nin", []))
        self.documents = {key: value for key, value in self.documents.items() if key in keep}

    def replace_one(self, query: dict, document: dict, *, upsert: bool, session=None):
        assert upsert is True
        assert query == {"_id": document["_id"]}
        self.sessions.append(session)
        self.replace_calls += 1
        self.documents[str(document["_id"])] = deepcopy(document)


class _Database:
    def __init__(self) -> None:
        self.collections: dict[str, _Collection] = {}

    def __getitem__(self, name: str) -> _Collection:
        return self.collections.setdefault(name, _Collection())


def _documents() -> dict[str, list[dict]]:
    return make_metadata_item_documents(
        _package(),
        {
            "domain": "WIP_QTY는 재공 수량을 뜻해. 제조 분석 도메인으로 등록해줘.",
            "table_catalog": "production 데이터셋은 생산 실적 조회용이야.",
            "main_filter": "DATE는 날짜와 기준일을 의미해.",
        },
        updated_at="2026-08-02T00:00:00+00:00",
    )


def _item(collection: str, section: str, key: str, payload: dict) -> dict:
    return {
        "_id": f"{collection}:{section}:{key}",
        "section": section,
        "key": key,
        "natural_text": f"{key} 등록",
        "payload": deepcopy(payload),
        "updated_at": "2026-08-03T00:00:00+00:00",
    }


def test_items_round_trip_to_exact_runtime_catalog_without_release_fields() -> None:
    documents = _documents()
    rebuilt = assemble_domain_package_from_items(documents)

    assert rebuilt["runtime_catalog"] == _package()["runtime_catalog"]
    assert rebuilt["domain_id"] == "manufacturing"
    assert rebuilt["environment"] == "production"
    assert all(set(item) == ITEM_FIELDS for items in documents.values() for item in items)
    forbidden = {
        "source_sha256",
        "section_sha256",
        "release_manifest_sha256",
        "package_meta",
        "document_sha256",
        "release_manifest",
        "release_id",
        "contract_version",
        "domain_id",
    }
    assert all(not (set(item) & forbidden) for items in documents.values() for item in items)
    assert len(documents["domain"]) > 1
    assert len(documents["table_catalog"]) > 1
    assert len(documents["main_filter"]) > 1
    assert all(item["natural_text"] for items in documents.values() for item in items)
    production = next(
        item
        for item in documents["table_catalog"]
        if item["section"] == "datasets" and item["key"] == "production"
    )
    source_config = production["payload"]["source_config"]
    assert source_config["db_key"] == "PNT_RPT"
    assert source_config["required_params"] == ["DATE"]
    assert "\nFROM PROD_TABLE2\n" in source_config["query_template"]
    assert source_config["query_template"].endswith("AND WORK_DATE = {DATE}")


def test_main_filter_can_be_saved_first_as_normal_item_documents() -> None:
    alias = deepcopy(_package()["runtime_catalog"]["aliases"]["field:DATE"])
    alias["provenance_source"] = "natural_authoring"
    partial = make_partial_metadata_item_documents(
        "main_filter",
        {"aliases": {"field:DATE": alias}},
        "날짜와 기준일은 DATE를 뜻해.",
        updated_at="2026-08-03T00:00:00+00:00",
    )

    assert partial["domain"] == []
    assert partial["table_catalog"] == []
    assert len(partial["main_filter"]) == 1
    item = partial["main_filter"][0]
    assert set(item) == ITEM_FIELDS
    assert item["_id"] == "main_filter:aliases:field:DATE"
    assert item["natural_text"]
    assert item["payload"]["provenance_source"] == "main_filters"

    database = _Database()
    upsert_partial_metadata_items(database, partial)
    assert len(database[MAIN_FILTER_COLLECTION].documents) == 1
    assert database[DOMAIN_METADATA_COLLECTION].documents == {}
    assert database[TABLE_CATALOG_COLLECTION].documents == {}
    with pytest.raises(ContractError):
        load_available_domain_package_from_three_collections(database)


def test_domain_profile_can_be_saved_without_registry_or_other_sections() -> None:
    partial = make_partial_metadata_item_documents(
        "domain",
        {
            "domain_id": "default",
            "display_name": "주문 분석",
            "description": "주문과 매출 데이터를 분석한다.",
        },
        "주문과 매출 데이터를 조회하는 업무야.",
        updated_at="2026-08-03T00:00:00+00:00",
    )

    assert partial["table_catalog"] == []
    assert partial["main_filter"] == []
    assert len(partial["domain"]) == 1
    item = partial["domain"][0]
    assert item["_id"] == "domain:profile:default"
    assert item["section"] == "profile"
    assert item["key"] == "default"
    assert item["natural_text"]
    assert item["payload"] == {
        "display_name": "주문 분석",
        "description": "주문과 매출 데이터를 분석한다.",
        "locale": "ko-KR",
        "timezone": "Asia/Seoul",
    }
    assert item["updated_at"] == "2026-08-03T00:00:00+00:00"


def test_process_group_is_one_domain_item_with_one_compiler_derived_alias_card() -> None:
    partial = make_partial_metadata_item_documents(
        "domain",
        {
            "entity_groups": {
                "DP": {
                    "group_id": "DP",
                    "display_name": "DP",
                    "target_field": "OPER_NAME",
                    "members": ["AA", "BB", "CC"],
                    "aliases": ["DP", "D/P", "DP공정", "D/P공정", "DP 공정", "D/P 공정"],
                }
            }
        },
        "DP 공정 그룹은 OPER_NAME의 AA, BB, CC를 포함해.",
        updated_at="2026-08-03T00:00:00+00:00",
    )

    assert partial["table_catalog"] == []
    assert partial["main_filter"] == []
    assert [item["_id"] for item in partial["domain"]] == [
        "domain:entity_groups:DP",
        "domain:aliases:entity_group:DP",
    ]
    group, alias = partial["domain"]
    assert group["payload"]["target_field"] == "OPER_NAME"
    assert group["payload"]["members"] == ["AA", "BB", "CC"]
    assert group["payload"]["selection"] == {
        "operator": "in",
        "value": ["AA", "BB", "CC"],
    }
    assert alias["payload"]["target_type"] == "entity_group"
    assert alias["payload"]["target_key"] == "DP"
    assert [value["text"] for value in alias["payload"]["values"]] == [
        "DP", "D/P", "DP공정", "D/P공정", "DP 공정", "D/P 공정"
    ]
    assert not any(item["key"] == "field:OPER_NAME" for item in partial["domain"])


def test_metric_and_recipe_items_create_domain_owned_alias_cards() -> None:
    partial = make_partial_metadata_item_documents(
        "domain",
        {
            "metrics": {
                "WIP_QTY": {
                    "metric_id": "WIP_QTY",
                    "aliases": ["WIP", "재공"],
                }
            },
            "recipes": {
                "product.standard": {
                    "recipe_id": "product.standard",
                    "aliases": ["제품별", "제품 집계"],
                }
            },
        },
        "WIP 지표와 제품별 recipe를 등록해줘.",
    )

    rows = {item["_id"]: item for item in partial["domain"]}
    assert rows["domain:aliases:metric:WIP_QTY"]["payload"]["target_type"] == "metric"
    assert rows["domain:aliases:recipe:product.standard"]["payload"]["target_type"] == "recipe"
    assert [
        value["text"]
        for value in rows["domain:aliases:metric:WIP_QTY"]["payload"]["values"]
    ] == ["WIP", "재공"]


def test_oper_name_filter_then_dp_group_then_dataset_compiles_without_cross_owner_alias() -> None:
    package = _package()
    profile = make_partial_metadata_item_documents(
        "domain",
        {"domain_id": "default", "display_name": "Manufacturing Analysis"},
        "Manufacturing Analysis 도메인을 등록해줘.",
    )
    group = make_partial_metadata_item_documents(
        "domain",
        {
            "entity_groups": {
                "DP": {
                    "group_id": "DP",
                    "display_name": "DP",
                    "target_field": "OPER_NAME",
                    "members": ["AA", "BB", "CC"],
                    "aliases": ["DP", "D/P", "DP공정", "D/P공정", "DP 공정", "D/P 공정"],
                }
            }
        },
        "DP는 OPER_NAME의 AA, BB, CC 공정 그룹이야.",
    )
    field_alias = deepcopy(package["runtime_catalog"]["aliases"]["field:OPER_NAME"])
    main_filter = make_partial_metadata_item_documents(
        "main_filter",
        {"aliases": {"field:OPER_NAME": field_alias}},
        "공정은 OPER_NAME 필터야.",
    )
    dataset_payload = deepcopy(package["runtime_catalog"]["datasets"]["production"])
    dataset_payload.pop("key", None)
    dataset = make_partial_metadata_item_documents(
        "dataset",
        {"datasets": {"production": dataset_payload}},
        "production 데이터에는 OPER_NAME이 있어.",
    )
    documents = {
        "domain": [*profile["domain"], *group["domain"]],
        "table_catalog": dataset["table_catalog"],
        "main_filter": main_filter["main_filter"],
    }

    compiled = assemble_domain_package_from_items(documents)

    assert compiled["runtime_catalog"]["entity_groups"]["DP"]["members"] == [
        "AA", "BB", "CC"
    ]
    assert compiled["runtime_catalog"]["aliases"]["field:OPER_NAME"]["target_type"] == "field"
    assert compiled["runtime_catalog"]["aliases"]["entity_group:DP"]["target_type"] == "entity_group"


def test_group_first_domain_collection_compiles_with_internal_default_profile() -> None:
    package = _package()
    group = make_partial_metadata_item_documents(
        "domain",
        {
            "entity_groups": {
                "DP": {
                    "group_id": "DP",
                    "display_name": "DP",
                    "target_field": "OPER_NAME",
                    "members": ["WET1", "WET2", "C/C1"],
                    "aliases": ["DP", "D/P", "DP 공정"],
                }
            }
        },
        "DP 공정 그룹을 등록해줘.",
    )
    main_filter = make_partial_metadata_item_documents(
        "main_filter",
        {"aliases": {"field:OPER_NAME": deepcopy(package["runtime_catalog"]["aliases"]["field:OPER_NAME"])}},
        "OPER_NAME을 주요 조회 조건으로 등록해줘.",
    )
    dataset_payload = deepcopy(package["runtime_catalog"]["datasets"]["production"])
    dataset_payload.pop("key", None)
    dataset = make_partial_metadata_item_documents(
        "dataset", {"datasets": {"production": dataset_payload}}, "production을 등록해줘."
    )

    compiled = assemble_domain_package_from_items(
        {
            "domain": group["domain"],
            "table_catalog": dataset["table_catalog"],
            "main_filter": main_filter["main_filter"],
        }
    )

    assert compiled["domain_id"] == "default"
    assert compiled["runtime_catalog"]["entity_groups"]["DP"]["members"] == ["WET1", "WET2", "C/C1"]


def test_unrelated_main_filter_target_does_not_block_domain_group_registration() -> None:
    """A stored EQP_ID filter must not invalidate an unrelated DP group write."""

    package = _package()
    group = make_partial_metadata_item_documents(
        "domain",
        {
            "entity_groups": {
                "DP": {
                    "group_id": "DP",
                    "display_name": "DP",
                    "target_field": "OPER_NAME",
                    "members": ["WET1", "WET2", "C/C1"],
                    "aliases": ["DP", "D/P", "DP 공정"],
                }
            }
        },
        "DP 공정 그룹을 등록해줘.",
    )
    dataset_payload = deepcopy(package["runtime_catalog"]["datasets"]["production_today"])
    dataset_payload.pop("key", None)
    dataset = make_partial_metadata_item_documents(
        "dataset",
        {"datasets": {"production_today": dataset_payload}},
        "당일 생산 실적 데이터를 등록해줘.",
    )
    eqp_alias = deepcopy(package["runtime_catalog"]["aliases"]["field:EQP_ID"])
    main_filter = make_partial_metadata_item_documents(
        "main_filter",
        {"aliases": {"field:EQP_ID": eqp_alias}},
        "설비 ID는 EQP_ID 필터야.",
    )
    documents = {
        "domain": group["domain"],
        "table_catalog": dataset["table_catalog"],
        "main_filter": main_filter["main_filter"],
    }
    activation = {}

    compiled = assemble_domain_package_from_items(
        documents,
        alias_activation_out=activation,
    )

    assert compiled["runtime_catalog"]["entity_groups"]["DP"]["target_field"] == "OPER_NAME"
    assert "entity_group:DP" in compiled["runtime_catalog"]["aliases"]
    assert "field:EQP_ID" not in compiled["runtime_catalog"]["aliases"]
    assert activation["deferred"] == [
        {
            "alias_id": "field:EQP_ID",
            "target_type": "field",
            "target_key": "EQP_ID",
        }
    ]
    # Runtime activation is a projection only.  The natural-language item is
    # still stored and can activate automatically after a matching dataset is
    # registered.
    assert documents["main_filter"][0]["key"] == "field:EQP_ID"


def test_deferred_main_filter_activates_when_matching_dataset_is_registered() -> None:
    package = _package()
    documents = _documents()
    only_eqp_alias = next(
        deepcopy(item)
        for item in documents["main_filter"]
        if item["key"] == "field:EQP_ID"
    )
    equipment_payload = deepcopy(package["runtime_catalog"]["datasets"]["equipment_assign"])
    equipment_payload.pop("key", None)
    equipment = make_partial_metadata_item_documents(
        "dataset",
        {"datasets": {"equipment_assign": equipment_payload}},
        "설비 배정 데이터를 등록해줘.",
    )
    group = make_partial_metadata_item_documents(
        "domain",
        {
            "entity_groups": {
                "DP": {
                    "group_id": "DP",
                    "display_name": "DP",
                    "target_field": "OPER_NAME",
                    "members": ["WET1"],
                    "aliases": ["DP"],
                }
            }
        },
        "DP 공정 그룹을 등록해줘.",
    )
    activation = {}

    compiled = assemble_domain_package_from_items(
        {
            "domain": group["domain"],
            "table_catalog": equipment["table_catalog"],
            "main_filter": [only_eqp_alias],
        },
        alias_activation_out=activation,
    )

    assert "field:EQP_ID" in compiled["runtime_catalog"]["aliases"]
    assert activation["deferred_count"] == 0


def test_dataset_can_extend_main_filter_partial_store_without_domain_profile() -> None:
    package = _package()
    alias = deepcopy(package["runtime_catalog"]["aliases"]["field:DATE"])
    main_filter = make_partial_metadata_item_documents(
        "main_filter",
        {"aliases": {"field:DATE": alias}},
        "날짜는 DATE야.",
    )
    dataset_payload = deepcopy(package["runtime_catalog"]["datasets"]["production"])
    dataset_payload.pop("key", None)
    dataset = make_partial_metadata_item_documents(
        "dataset",
        {"datasets": {"production": dataset_payload}},
        "production은 생산 실적 테이블이야.",
    )
    database = _Database()
    upsert_partial_metadata_items(database, main_filter)
    upsert_partial_metadata_items(database, dataset)

    assert len(database[MAIN_FILTER_COLLECTION].documents) == 1
    assert len(database[TABLE_CATALOG_COLLECTION].documents) == 1
    assert database[DOMAIN_METADATA_COLLECTION].documents == {}
    with pytest.raises(ContractError):
        load_available_domain_package_from_three_collections(database)


def test_main_filter_then_dataset_then_domain_activates_exact_package() -> None:
    documents = _documents()
    database = _Database()
    upsert_partial_metadata_items(
        database,
        {"domain": [], "table_catalog": [], "main_filter": documents["main_filter"]},
    )
    upsert_partial_metadata_items(
        database,
        {"domain": [], "table_catalog": documents["table_catalog"], "main_filter": documents["main_filter"]},
    )
    with pytest.raises(ContractError):
        load_available_domain_package_from_three_collections(database)

    replace_metadata_items(database, documents)
    loaded = load_available_domain_package_from_three_collections(database)
    assert loaded["runtime_catalog"] == _package()["runtime_catalog"]


def test_loader_and_writer_use_only_registered_three_collections_and_session() -> None:
    database = _Database()
    session = object()
    replace_metadata_items(database, _documents(), session=session)
    loaded = load_domain_package_from_three_collections(
        database, "manufacturing", "production", session=session
    )

    assert loaded["runtime_catalog"] == _package()["runtime_catalog"]
    assert set(database.collections) == {
        DOMAIN_METADATA_COLLECTION,
        TABLE_CATALOG_COLLECTION,
        MAIN_FILTER_COLLECTION,
    }
    assert all(session in collection.sessions for collection in database.collections.values())


def test_available_loader_needs_no_domain_or_release_selector() -> None:
    database = _Database()
    replace_metadata_items(database, _documents())

    loaded = load_available_domain_package_from_three_collections(database)

    assert loaded["domain_id"] == "manufacturing"
    assert loaded["environment"] == "production"
    assert loaded["runtime_catalog"] == _package()["runtime_catalog"]


def test_natural_text_is_editable_but_typed_payload_is_still_compiled() -> None:
    documents = _documents()
    edited = deepcopy(documents)
    edited["domain"][0]["natural_text"] = "작업자가 자유롭게 고친 설명"
    assert assemble_domain_package_from_items(edited)["runtime_catalog"] == _package()["runtime_catalog"]

    broken = deepcopy(documents)
    dataset = next(item for item in broken["table_catalog"] if item["section"] == "datasets")
    dataset["payload"]["fields"] = {}
    with pytest.raises(ContractError):
        assemble_domain_package_from_items(broken)

    extra = deepcopy(documents)
    extra["domain"][0]["release_id"] = "not-allowed"
    with pytest.raises(ContractError):
        assemble_domain_package_from_items(extra)


def test_replace_preserves_existing_natural_text_for_unchanged_items() -> None:
    database = _Database()
    documents = _documents()
    target = documents["domain"][0]
    target["natural_text"] = "기존 작업자 입력"
    replace_metadata_items(database, documents)

    next_documents = _documents()
    next_target = next(item for item in next_documents["domain"] if item["_id"] == target["_id"])
    next_target["natural_text"] = ""
    replace_metadata_items(database, next_documents)

    stored = database[DOMAIN_METADATA_COLLECTION].documents[target["_id"]]
    assert stored["natural_text"] == "기존 작업자 입력"


def test_item_write_modes_preserve_unmentioned_and_require_explicit_replace() -> None:
    current = _documents()
    candidate = {"domain": [], "table_catalog": [], "main_filter": []}
    changed = deepcopy(current["domain"][0])
    changed["payload"] = {**changed["payload"], "description": "교체된 설명"}
    changed["natural_text"] = "기존 항목을 새 설명으로 교체합니다."
    candidate["domain"] = [changed]

    save_merged, save_operations = merge_metadata_items_for_write(
        current, candidate, mode="save"
    )
    assert save_operations["conflict_count"] == 1
    assert save_operations["replaced"] == 0
    assert len(save_merged["domain"]) == len(current["domain"])
    save_target = next(item for item in save_merged["domain"] if item["_id"] == changed["_id"])
    assert save_target["payload"] != changed["payload"]

    replace_merged, replace_operations = merge_metadata_items_for_write(
        current, candidate, mode="replace"
    )
    assert replace_operations["conflict_count"] == 0
    assert replace_operations["replaced"] == 1
    assert len(replace_merged["domain"]) == len(current["domain"])
    replace_target = next(item for item in replace_merged["domain"] if item["_id"] == changed["_id"])
    assert replace_target["payload"] == changed["payload"]


def test_validate_only_uses_replace_projection_without_writing_policy_side_effects() -> None:
    current = _documents()
    candidate = {"domain": [], "table_catalog": [], "main_filter": []}
    changed = deepcopy(current["main_filter"][0])
    changed["natural_text"] = "검증 전용 입력"
    changed["payload"] = {**changed["payload"], "description": "검증 전용 변경"}
    candidate["main_filter"] = [changed]

    merged, operations = merge_metadata_items_for_write(
        current, candidate, mode="validate_only"
    )

    assert operations["replaced"] == 1
    assert operations["conflict_count"] == 0
    assert len(merged["main_filter"]) == len(current["main_filter"])


def test_exact_replay_ignores_natural_text_and_updated_at_for_duplicate_identity() -> None:
    current = _documents()
    candidate_item = deepcopy(current["domain"][0])
    candidate_item["natural_text"] = "작업자가 다시 설명한 같은 항목"
    candidate_item["updated_at"] = "2026-08-03T01:00:00+00:00"

    merged, operations = merge_metadata_items_for_write(
        current,
        {"domain": [candidate_item], "table_catalog": [], "main_filter": []},
        mode="save",
    )

    assert operations["unchanged"] == 1
    assert operations["conflict_count"] == 0
    stored = next(item for item in merged["domain"] if item["_id"] == candidate_item["_id"])
    assert stored["natural_text"] != candidate_item["natural_text"]


def test_complete_compiled_package_replay_has_no_semantic_false_positive() -> None:
    current = _documents()

    _merged, operations = merge_metadata_items_for_write(
        current,
        deepcopy(current),
        mode="save",
    )

    assert operations["unchanged"] == sum(len(items) for items in current.values())
    assert operations["inserted"] == 0
    assert operations["conflict_count"] == 0


def test_domain_normalized_key_and_same_section_alias_duplicates_are_blocked() -> None:
    current_item = _item(
        "domain",
        "entity_groups",
        "B/G",
        {
            "group_id": "B/G",
            "legacy_identity": "process_group.BG",
            "aliases": ["B/G", "BG 공정"],
        },
    )
    normalized_key = _item(
        "domain",
        "entity_groups",
        "Ｂ／Ｇ",
        {"group_id": "FULLWIDTH_BG", "aliases": ["별도 표현"]},
    )
    alias_duplicate = _item(
        "domain",
        "entity_groups",
        "BG_DUP",
        {"group_id": "BG_DUP", "aliases": ["BG 공정"]},
    )

    for candidate in (normalized_key, alias_duplicate):
        _merged, operations = merge_metadata_items_for_write(
            {"domain": [current_item], "table_catalog": [], "main_filter": []},
            {"domain": [candidate], "table_catalog": [], "main_filter": []},
            mode="save",
        )
        assert operations["conflict_count"] == 1
        assert operations["conflicts"][0]["canonical_key"] == "B/G"


def test_duplicate_normalization_does_not_strip_slashes_or_punctuation() -> None:
    current_item = _item(
        "domain",
        "entity_groups",
        "B/G",
        {"group_id": "B/G", "aliases": ["B/G"]},
    )
    candidate = _item(
        "domain",
        "entity_groups",
        "BG",
        {"group_id": "BG", "aliases": ["BG"]},
    )

    _merged, operations = merge_metadata_items_for_write(
        {"domain": [current_item], "table_catalog": [], "main_filter": []},
        {"domain": [candidate], "table_catalog": [], "main_filter": []},
        mode="save",
    )

    assert operations["inserted"] == 1
    assert operations["conflict_count"] == 0


def test_domain_alias_matching_multiple_existing_items_fails_ambiguous() -> None:
    existing = [
        _item("domain", "recipes", "recipe.a", {"recipe_id": "recipe.a", "aliases": ["공통 분석"]}),
        _item("domain", "recipes", "recipe.b", {"recipe_id": "recipe.b", "aliases": ["공통 분석"]}),
    ]
    candidate = _item(
        "domain",
        "recipes",
        "recipe.c",
        {"recipe_id": "recipe.c", "aliases": ["공통 분석"]},
    )

    _merged, operations = merge_metadata_items_for_write(
        {"domain": existing, "table_catalog": [], "main_filter": []},
        {"domain": [candidate], "table_catalog": [], "main_filter": []},
        mode="replace",
    )

    conflict = operations["conflicts"][0]
    assert conflict["reason"] == "ambiguous_duplicate_target"
    assert {item["key"] for item in conflict["duplicate_candidates"]} == {
        "recipe.a",
        "recipe.b",
    }


def test_domain_same_section_display_name_requires_existing_canonical_key() -> None:
    existing = _item(
        "domain",
        "entity_groups",
        "LINE_A",
        {"group_id": "LINE_A", "display_name": "조립 라인", "aliases": []},
    )
    candidate = _item(
        "domain",
        "entity_groups",
        "LINE_B",
        {"group_id": "LINE_B", "display_name": "  조립   라인 ", "aliases": []},
    )

    _merged, operations = merge_metadata_items_for_write(
        {"domain": [existing], "table_catalog": [], "main_filter": []},
        {"domain": [candidate], "table_catalog": [], "main_filter": []},
        mode="save",
    )

    assert operations["conflicts"][0]["canonical_key"] == "LINE_A"
    assert operations["conflicts"][0]["match_types"] == ["display_name"]


def test_dataset_query_ref_and_full_source_descriptor_are_strong_duplicates() -> None:
    documents = _documents()
    production = next(
        item
        for item in documents["table_catalog"]
        if item["section"] == "datasets" and item["key"] == "production"
    )
    same_query_ref = deepcopy(production)
    same_query_ref["key"] = "production_copy"
    same_query_ref["_id"] = "table_catalog:datasets:production_copy"
    same_query_ref["payload"]["display_name"] = "생산 복사본"

    _merged, operations = merge_metadata_items_for_write(
        {"domain": [], "table_catalog": [production], "main_filter": []},
        {"domain": [], "table_catalog": [same_query_ref], "main_filter": []},
        mode="save",
    )
    assert operations["conflicts"][0]["match_types"] == ["query_ref"]
    assert "SELECT" not in json.dumps(operations["conflicts"], ensure_ascii=False)

    same_source = deepcopy(same_query_ref)
    same_source["payload"]["query_ref"] = "query:production_copy@1"
    same_source["payload"]["display_name"] = production["payload"].get("display_name")
    _merged, operations = merge_metadata_items_for_write(
        {"domain": [], "table_catalog": [production], "main_filter": []},
        {"domain": [], "table_catalog": [same_source], "main_filter": []},
        mode="save",
    )
    assert operations["conflicts"][0]["match_types"] == ["source_descriptor"]


def test_dataset_config_ref_reuse_and_sql_comment_difference_are_allowed() -> None:
    documents = _documents()
    production = next(
        item
        for item in documents["table_catalog"]
        if item["section"] == "datasets" and item["key"] == "production"
    )
    candidate = deepcopy(production)
    candidate["key"] = "production_comment_variant"
    candidate["_id"] = "table_catalog:datasets:production_comment_variant"
    candidate["payload"]["query_ref"] = "query:production_comment_variant@1"
    original_query = candidate["payload"]["source_config"]["query_template"]
    candidate["payload"]["source_config"]["query_template"] = (
        "/*+ INDEX(PROD_TABLE2 IDX_PROD_DATE) */\n" + original_query
    )

    _merged, operations = merge_metadata_items_for_write(
        {"domain": [], "table_catalog": [production], "main_filter": []},
        {"domain": [], "table_catalog": [candidate], "main_filter": []},
        mode="save",
    )

    assert candidate["payload"]["config_ref"] == production["payload"]["config_ref"]
    assert operations["inserted"] == 1
    assert operations["conflict_count"] == 0
    assert candidate["payload"]["source_config"]["query_template"].startswith("/*+")


def test_alias_duplicate_scope_allows_cross_type_and_blocks_same_type_ambiguity() -> None:
    existing = _item(
        "main_filter",
        "aliases",
        "field:UPH",
        {"target_type": "field", "target_key": "UPH", "values": [{"text": "UPH"}]},
    )
    cross_type = _item(
        "main_filter",
        "aliases",
        "metric:UPH",
        {"target_type": "metric", "target_key": "UPH", "values": [{"text": "UPH"}]},
    )
    same_type_other_target = _item(
        "main_filter",
        "aliases",
        "field:UPH_OTHER",
        {"target_type": "field", "target_key": "UPH_OTHER", "values": [{"text": "UPH"}]},
    )

    _merged, allowed = merge_metadata_items_for_write(
        {"domain": [], "table_catalog": [], "main_filter": [existing]},
        {"domain": [], "table_catalog": [], "main_filter": [cross_type]},
        mode="save",
    )
    assert allowed["inserted"] == 1
    assert allowed["conflict_count"] == 0

    _merged, blocked = merge_metadata_items_for_write(
        {"domain": [], "table_catalog": [], "main_filter": [existing]},
        {"domain": [], "table_catalog": [], "main_filter": [same_type_other_target]},
        mode="save",
    )
    assert blocked["conflicts"][0]["reason"] == "ambiguous_alias_target"


def test_alias_same_target_with_different_key_requires_canonical_key() -> None:
    existing = _item(
        "main_filter",
        "aliases",
        "field:ORG",
        {"target_type": "field", "target_key": "ORG", "values": [{"text": "조직"}]},
    )
    candidate = _item(
        "main_filter",
        "aliases",
        "field:ORG_ALIAS",
        {"target_type": "field", "target_key": "ORG", "values": [{"text": "사업 조직"}]},
    )

    _merged, operations = merge_metadata_items_for_write(
        {"domain": [], "table_catalog": [], "main_filter": [existing]},
        {"domain": [], "table_catalog": [], "main_filter": [candidate]},
        mode="replace",
    )

    assert operations["conflicts"][0]["reason"] == "canonical_key_required"
    assert operations["conflicts"][0]["canonical_key"] == "field:ORG"


def test_alias_duplicate_is_blocked_across_collection_ownership_change() -> None:
    current = _documents()
    existing = next(
        item
        for item in current["domain"]
        if item["section"] == "aliases" and item["key"] == "field:OPER_NAME"
    )
    moved = deepcopy(existing)
    moved["_id"] = "main_filter:aliases:field:OPER_NAME"
    moved["payload"]["provenance_source"] = "main_filters"

    _merged, operations = merge_metadata_items_for_write(
        current,
        {"domain": [], "table_catalog": [], "main_filter": [moved]},
        mode="replace",
    )

    conflict = operations["conflicts"][0]
    assert conflict["reason"] == "canonical_key_required"
    assert conflict["duplicate_candidates"] == [
        {
            "collection": "domain",
            "section": "aliases",
            "key": "field:OPER_NAME",
            "source": "existing_other_collection",
        }
    ]


def test_assembler_fails_closed_on_cross_collection_alias_overwrite() -> None:
    documents = _documents()
    duplicated = deepcopy(documents)
    existing = next(
        item
        for item in duplicated["domain"]
        if item["section"] == "aliases" and item["key"] == "field:OPER_NAME"
    )
    moved = deepcopy(existing)
    moved["_id"] = "main_filter:aliases:field:OPER_NAME"
    moved["payload"]["provenance_source"] = "main_filters"
    duplicated["main_filter"].append(moved)

    with pytest.raises(ContractError) as raised:
        assemble_domain_package_from_items(duplicated)

    assert raised.value.details["reason"] == "cross_collection_alias_duplicate"


def test_global_alias_expression_ambiguity_is_blocked_for_initial_package() -> None:
    candidate = _documents()
    domain_alias = next(
        item
        for item in candidate["domain"]
        if item["section"] == "aliases" and item["key"] == "field:OPER_NAME"
    )
    main_filter_alias = next(
        item
        for item in candidate["main_filter"]
        if item["section"] == "aliases" and item["key"] == "field:ORG"
    )
    collision = {"priority": 100, "text": "전역 충돌 표현"}
    domain_alias["payload"]["values"].append(deepcopy(collision))
    main_filter_alias["payload"]["values"].append(deepcopy(collision))

    _merged, operations = merge_metadata_items_for_write(
        {"domain": [], "table_catalog": [], "main_filter": []},
        candidate,
        mode="validate_only",
    )

    conflicts = {
        (item["collection"], item["key"], item["reason"])
        for item in operations["conflicts"]
    }
    assert ("domain", "field:OPER_NAME", "ambiguous_alias_target") in conflicts
    assert ("main_filter", "field:ORG", "ambiguous_alias_target") in conflicts

    with pytest.raises(ContractError) as raised:
        assemble_domain_package_from_items(candidate)
    assert raised.value.details["reason"] == "global_alias_expression_ambiguous"


def test_candidate_to_candidate_duplicate_is_blocked_before_storage() -> None:
    candidates = [
        _item("domain", "metrics", "METRIC_A", {"metric_id": "METRIC_A", "aliases": ["공통 지표"]}),
        _item("domain", "metrics", "METRIC_B", {"metric_id": "METRIC_B", "aliases": ["공통 지표"]}),
    ]

    _merged, operations = merge_metadata_items_for_write(
        {"domain": [], "table_catalog": [], "main_filter": []},
        {"domain": candidates, "table_catalog": [], "main_filter": []},
        mode="save",
    )

    assert operations["inserted"] == 0
    assert operations["conflict_count"] == 2
    assert all(item["reason"] == "submitted_duplicate" for item in operations["conflicts"])
    assert all("canonical_key" not in item for item in operations["conflicts"])


def test_writer_never_deletes_unmentioned_or_concurrently_added_items() -> None:
    database = _Database()
    documents = _documents()
    replace_metadata_items(database, documents)
    extra = _item(
        "domain",
        "metrics",
        "CONCURRENT_METRIC",
        {"metric_id": "CONCURRENT_METRIC", "value_type": "number", "unit": "count"},
    )
    database[DOMAIN_METADATA_COLLECTION].documents[extra["_id"]] = deepcopy(extra)

    replace_metadata_items(database, documents)

    assert extra["_id"] in database[DOMAIN_METADATA_COLLECTION].documents
    assert all(collection.delete_calls == 0 for collection in database.collections.values())


def test_writer_skips_unchanged_documents_except_shared_profile_lock() -> None:
    database = _Database()
    documents = _documents()
    replace_metadata_items(database, documents)
    for collection in database.collections.values():
        collection.replace_calls = 0

    replace_metadata_items(database, deepcopy(documents))

    assert database[DOMAIN_METADATA_COLLECTION].replace_calls == 1
    assert database[TABLE_CATALOG_COLLECTION].replace_calls == 0
    assert database[MAIN_FILTER_COLLECTION].replace_calls == 0


def test_operation_records_are_bounded_while_total_count_is_preserved() -> None:
    candidates = [
        _item(
            "domain",
            "metrics",
            f"METRIC_{index:03d}",
            {"metric_id": f"METRIC_{index:03d}"},
        )
        for index in range(100)
    ]

    _merged, operations = merge_metadata_items_for_write(
        {"domain": [], "table_catalog": [], "main_filter": []},
        {"domain": candidates, "table_catalog": [], "main_filter": []},
        mode="save",
    )

    assert operations["inserted"] == 100
    assert operations["operation_record_count"] == 100
    assert len(operations["operation_by_key"]) == 64
    assert operations["operation_records_truncated"] is True


def test_conflict_payload_is_bounded_while_true_count_is_preserved() -> None:
    candidates = [
        _item(
            "domain",
            "metrics",
            f"DUPLICATE_{index:03d}",
            {"metric_id": f"DUPLICATE_{index:03d}", "aliases": ["같은 지표"]},
        )
        for index in range(40)
    ]

    _merged, operations = merge_metadata_items_for_write(
        {"domain": [], "table_catalog": [], "main_filter": []},
        {"domain": candidates, "table_catalog": [], "main_filter": []},
        mode="save",
    )

    assert operations["conflict_count"] == 40
    assert len(operations["conflicts"]) == 32
    assert operations["conflicts_truncated"] is True


def test_item_snapshot_projection_detects_transaction_time_changes() -> None:
    current = _documents()
    same = deepcopy(current)
    changed = deepcopy(current)
    changed["main_filter"][0]["natural_text"] = "동시에 수정된 작업자 원문"

    assert metadata_item_set_projection(current) == metadata_item_set_projection(same)
    assert metadata_item_set_projection(current) != metadata_item_set_projection(changed)


def test_unmatched_migration_text_uses_an_item_specific_natural_summary() -> None:
    documents = make_metadata_item_documents(
        _package(),
        {
            "domain": "POP 제품 조건만 등록합니다.",
            "table_catalog": "임시 데이터셋 설명입니다.",
            "main_filter": "ORG 조직 코드 필터만 등록합니다.",
        },
        updated_at="2026-08-02T00:00:00+00:00",
    )
    achievement = next(
        item
        for item in documents["domain"]
        if item["section"] == "metrics" and item["key"] == "ACHIEVEMENT_RATE"
    )
    base_date = next(
        item
        for item in documents["main_filter"]
        if item["section"] == "aliases" and item["key"] == "field:BASE_DATE"
    )

    assert "ACHIEVEMENT_RATE" in achievement["natural_text"]
    assert "POP 제품 조건만" not in achievement["natural_text"]
    assert "BASE_DATE" in base_date["natural_text"]
    assert "ORG 조직 코드 필터만" not in base_date["natural_text"]


def test_new_item_source_text_replaces_an_existing_generated_summary() -> None:
    database = _Database()
    original = make_metadata_item_documents(
        _package(),
        {"domain": "관련 없는 문장", "table_catalog": "", "main_filter": ""},
    )
    replace_metadata_items(database, original)

    worker_text = "EQP_COUNT 장비 대수 지표를 등록합니다."
    updated = make_metadata_item_documents(
        _package(),
        {"domain": worker_text, "table_catalog": "", "main_filter": ""},
    )
    replace_metadata_items(database, updated)

    stored = database[DOMAIN_METADATA_COLLECTION].documents["domain:metrics:EQP_COUNT"]
    assert stored["natural_text"] == worker_text


def test_loader_supports_safe_distinct_collection_names() -> None:
    database = _Database()
    names = {
        "domain_collection": "custom_domain",
        "table_collection": "custom_catalog",
        "main_filter_collection": "custom_filter",
    }
    replace_metadata_items(database, _documents(), **names)

    loaded = load_available_domain_package_from_three_collections(database, **names)
    assert loaded["runtime_catalog"] == _package()["runtime_catalog"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"domain_collection": "same", "table_collection": "same"},
        {"domain_collection": "$invalid"},
        {"domain_collection": "system.profile"},
    ],
)
def test_loader_rejects_unsafe_or_duplicate_collection_names(overrides: dict[str, str]) -> None:
    database = _Database()
    values = {
        "domain_collection": "custom_domain",
        "table_collection": "custom_catalog",
        "main_filter_collection": "custom_filter",
        **overrides,
    }
    with pytest.raises(ContractError):
        load_available_domain_package_from_three_collections(database, **values)
