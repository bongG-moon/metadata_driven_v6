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
    assemble_domain_package_from_sections,
    load_available_domain_package_from_three_collections,
    load_domain_package_from_three_collections,
    make_metadata_section_documents,
    replace_metadata_release,
)


ROOT = Path(__file__).resolve().parents[1]


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

    def find_one(self, query: dict, session=None, sort=None):
        self.sessions.append(session)
        if "_id" in query:
            value = self.documents.get(str(query.get("_id")))
        else:
            values = sorted(
                self.documents.values(),
                key=lambda item: (
                    str(item.get("updated_at") or ""),
                    int(item.get("revision") or 0),
                    str(item.get("_id") or ""),
                ),
                reverse=True,
            )
            value = values[0] if values else None
        return deepcopy(value) if value is not None else None

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


def _documents() -> dict[str, dict]:
    return make_metadata_section_documents(
        _package(),
        {
            "domain": "현장 작업자가 자유롭게 작성한 도메인 설명",
            "table_catalog": "테이블과 컬럼을 자연어로 설명한 원문",
            "main_filter": "조회 필터와 별칭을 자연어로 설명한 원문",
        },
        updated_at="2026-08-02T00:00:00+00:00",
    )


def test_three_sections_round_trip_to_exact_package() -> None:
    documents = _documents()
    rebuilt = assemble_domain_package_from_sections(
        documents, "manufacturing", "production"
    )

    assert rebuilt == _package()
    assert {item["section_kind"] for item in documents.values()} == {
        "domain",
        "table_catalog",
        "main_filter",
    }
    assert len({item["release_id"] for item in documents.values()}) == 1
    assert documents["domain"]["source_text"].startswith("현장 작업자")


def test_loader_and_writer_use_only_registered_three_collections_and_session() -> None:
    database = _Database()
    session = object()
    documents = _documents()

    replace_metadata_release(database, documents, session=session)
    loaded = load_domain_package_from_three_collections(
        database, "manufacturing", "production", session=session
    )

    assert loaded == _package()
    assert set(database.collections) == {
        DOMAIN_METADATA_COLLECTION,
        TABLE_CATALOG_COLLECTION,
        MAIN_FILTER_COLLECTION,
    }
    assert all(session in collection.sessions for collection in database.collections.values())


def test_available_loader_discovers_the_latest_complete_release_without_flow_selector() -> None:
    database = _Database()
    session = object()
    replace_metadata_release(database, _documents(), session=session)

    loaded = load_available_domain_package_from_three_collections(database, session=session)

    assert loaded == _package()
    assert loaded["domain_id"] == "manufacturing"
    assert loaded["environment"] == "production"


def test_tampered_natural_source_or_mixed_release_is_rejected() -> None:
    documents = _documents()
    tampered = deepcopy(documents)
    tampered["domain"]["source_text"] += " 변조"
    with pytest.raises(ContractError):
        assemble_domain_package_from_sections(tampered, "manufacturing", "production")

    mixed = deepcopy(documents)
    mixed["main_filter"]["release_id"] = "release:" + "0" * 64
    with pytest.raises(ContractError):
        assemble_domain_package_from_sections(mixed, "manufacturing", "production")


def test_loader_rejects_collection_name_drift() -> None:
    database = _Database()
    replace_metadata_release(database, _documents())

    with pytest.raises(ContractError):
        load_domain_package_from_three_collections(
            database,
            "manufacturing",
            "production",
            domain_collection="custom_domain",
        )
