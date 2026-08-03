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
    replace_metadata_items,
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

    def find(self, query=None):
        del query
        return [deepcopy(item) for item in self.documents.values()]

    def delete_many(self, query: dict, session=None):
        self.sessions.append(session)
        keep = set(query.get("_id", {}).get("$nin", []))
        self.documents = {key: value for key, value in self.documents.items() if key in keep}

    def replace_one(self, query: dict, document: dict, *, upsert: bool, session=None):
        assert upsert is True
        assert query == {"_id": document["_id"]}
        self.sessions.append(session)
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
