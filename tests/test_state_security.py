from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

import pytest

from reference_runtime import state_contracts
from reference_runtime.canonical import ContractError, sha256_json
from reference_runtime.state_contracts import InMemoryStateStore, MongoStateStore


UTC = timezone.utc


def _commit(
    store: InMemoryStateStore,
    *,
    owner: str = "owner-a",
    session: str = "session-a",
    result: dict | None = None,
):
    return store.commit_execution(
        subject_id=owner,
        session_id=session,
        expected_version=0,
        result=result or {"rows": [{"value": 1}]},
        source_snapshots=[{"rows": [{"source": 1}]}],
        next_state={"last_question": "question"},
        ttl_seconds=3600,
    )


def test_content_refs_bind_role_owner_session_and_full_content_hash():
    store = InMemoryStateStore()
    result = {"rows": [{"value": 1}]}
    _, owner_a_ref, source_refs = _commit(store, result=result)
    _, owner_b_ref, _ = _commit(store, owner="owner-b", result=result)

    assert owner_a_ref["ref_id"].startswith("result:")
    assert owner_a_ref["ref_id"].endswith(sha256_json(result))
    assert source_refs[0]["ref_id"].startswith("source:")
    assert owner_a_ref["ref_id"] != owner_b_ref["ref_id"]
    stored = store.load_ref(owner_a_ref["ref_id"], "owner-a", "session-a")
    assert stored["owner_subject_id"] == "owner-a"
    assert "subject_id" not in stored

    with pytest.raises(ContractError) as wrong_owner:
        store.load_ref(owner_a_ref["ref_id"], "owner-b", "session-a")
    assert wrong_owner.value.code == "state_reference_forbidden"

    with pytest.raises(ContractError) as wrong_session:
        store.load_ref(owner_a_ref["ref_id"], "owner-a", "session-b")
    assert wrong_session.value.code == "state_reference_forbidden"


@pytest.mark.parametrize(
    ("field", "tampered"),
    [
        ("role", "source_snapshot"),
        ("owner_subject_id", "owner-b"),
        ("payload", {"rows": [{"value": 999}]}),
        ("content_sha256", "0" * 64),
    ],
)
def test_ref_load_rejects_role_owner_or_content_tampering(field, tampered):
    store = InMemoryStateStore()
    _, result_ref, _ = _commit(store)
    ref_id = result_ref["ref_id"]
    store._refs[ref_id][field] = tampered

    with pytest.raises(ContractError) as error:
        store.load_ref(ref_id, "owner-a", "session-a")
    assert error.value.code == "state_reference_forbidden"


def test_expiry_comparisons_accept_naive_and_zulu_values(monkeypatch):
    now = datetime(2026, 7, 31, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(state_contracts, "_now", lambda: now)
    store = InMemoryStateStore()
    _, result_ref, _ = _commit(store)
    ref_id = result_ref["ref_id"]

    store._states[("owner-a", "session-a")]["expires_at"] = "2026-07-31T00:01:00"
    assert store.load_state("owner-a", "session-a")["expires_at"].endswith("+00:00")

    store._refs[ref_id]["expires_at"] = "2026-07-31T00:01:00Z"
    assert store.load_ref(ref_id, "owner-a", "session-a")["expires_at"].endswith("+00:00")

    store._refs[ref_id]["expires_at"] = "2026-07-30T23:59:59"
    with pytest.raises(ContractError) as expired:
        store.load_ref(ref_id, "owner-a", "session-a")
    assert expired.value.code == "state_reference_expired"


class _FakeCollection:
    def __init__(self) -> None:
        self.index_calls: list[tuple[str, dict]] = []
        self.find_calls: list[tuple[dict, dict | None]] = []
        self.replace_calls: list[tuple[dict, dict, bool]] = []
        self.delete_calls: list[dict] = []
        self.update_calls: list[tuple[dict, dict, bool]] = []
        self.find_result: dict | None = None

    def create_index(self, key, **kwargs):
        self.index_calls.append((key, kwargs))
        return f"{key}_index"

    def find_one(self, query, projection=None):
        self.find_calls.append((deepcopy(query), deepcopy(projection)))
        return deepcopy(self.find_result)

    def replace_one(self, query, document, upsert=False):
        self.replace_calls.append((deepcopy(query), deepcopy(document), bool(upsert)))
        return object()

    def delete_one(self, query):
        self.delete_calls.append(deepcopy(query))
        return object()

    def find_one_and_update(self, query, update, upsert=False, return_document=None):
        self.update_calls.append((deepcopy(query), deepcopy(update), bool(upsert)))
        return deepcopy(update.get("$set") or {})


class _FakeDatabase:
    def __init__(self) -> None:
        self.collections: dict[str, _FakeCollection] = {}

    def __getitem__(self, name):
        return self.collections.setdefault(str(name), _FakeCollection())


class _FakeClient:
    def __init__(self) -> None:
        self.databases: dict[str, _FakeDatabase] = {}

    def __getitem__(self, name):
        return self.databases.setdefault(str(name), _FakeDatabase())


def test_mongo_client_is_timezone_aware_and_builds_ttl_indexes(monkeypatch):
    pymongo = pytest.importorskip("pymongo")
    captured: dict = {}
    fake_client = _FakeClient()

    def fake_mongo_client(uri, **kwargs):
        captured.update({"uri": uri, **kwargs})
        return fake_client

    monkeypatch.setattr(pymongo, "MongoClient", fake_mongo_client)
    store = MongoStateStore("mongodb://example", database="db", timeout_ms=1234)

    assert captured["tz_aware"] is True
    assert captured["serverSelectionTimeoutMS"] == 1234
    assert store.results.index_calls == [("expires_at", {"expireAfterSeconds": 0})]
    assert store.states.index_calls == [("expires_at", {"expireAfterSeconds": 0})]


def test_mongo_load_state_queries_canonical_owner_field(monkeypatch):
    now = datetime(2026, 7, 31, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(state_contracts, "_now", lambda: now)
    store = object.__new__(MongoStateStore)
    store.states = _FakeCollection()
    store.states.find_result = {
        "owner_subject_id": "owner-a",
        "session_id": "session-a",
        "state_version": 1,
        "expires_at": datetime(2026, 7, 31, 1, 0),
    }

    loaded = store.load_state("owner-a", "session-a")

    query = store.states.find_calls[0][0]
    assert query["owner_subject_id"] == "owner-a"
    assert "subject_id" not in query
    assert loaded["expires_at"] == "2026-07-31T01:00:00+00:00"


def test_mongo_load_ref_queries_owner_and_revalidates_content(monkeypatch):
    now = datetime(2026, 7, 31, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(state_contracts, "_now", lambda: now)
    payload = {"rows": [{"value": 1}]}
    content_hash = sha256_json(payload)
    ref_id = state_contracts._content_ref("analysis_result", "owner-a", "session-a", content_hash)
    store = object.__new__(MongoStateStore)
    store.results = _FakeCollection()
    store.results.find_result = {
        "_id": ref_id,
        "ref_id": ref_id,
        "role": "analysis_result",
        "owner_subject_id": "owner-a",
        "session_id": "session-a",
        "content_sha256": content_hash,
        "payload": payload,
        "expires_at": "2026-07-31T01:00:00Z",
    }

    assert store.load_ref(ref_id, "owner-a", "session-a")["payload"] == payload
    query = store.results.find_calls[0][0]
    assert query["owner_subject_id"] == "owner-a"
    assert query["session_id"] == "session-a"

    store.results.find_result["payload"] = {"rows": [{"value": 2}]}
    with pytest.raises(ContractError) as tampered:
        store.load_ref(ref_id, "owner-a", "session-a")
    assert tampered.value.code == "state_reference_forbidden"


def test_mongo_expired_state_is_deleted_conditionally_then_version_zero_can_commit(monkeypatch):
    pytest.importorskip("pymongo")
    now = datetime(2026, 7, 31, 0, 0, 0, 123456, tzinfo=UTC)
    monkeypatch.setattr(state_contracts, "_now", lambda: now)
    expired_at = datetime(2026, 7, 30, 23, 59, 59)
    store = object.__new__(MongoStateStore)
    store.results = _FakeCollection()
    store.states = _FakeCollection()
    store.states.find_result = {
        "owner_subject_id": "owner-a",
        "session_id": "session-a",
        "state_version": 7,
        "etag": "state-sha256:expired",
        "expires_at": expired_at,
    }
    store.events = []

    assert store.load_state("owner-a", "session-a") is None
    delete_query = store.states.delete_calls[0]
    assert delete_query["owner_subject_id"] == "owner-a"
    assert delete_query["session_id"] == "session-a"
    assert delete_query["state_version"] == 7
    assert delete_query["etag"] == "state-sha256:expired"
    assert delete_query["expires_at"] == expired_at

    committed, _, _ = store.commit_execution(
        subject_id="owner-a",
        session_id="session-a",
        expected_version=0,
        result={"rows": [{"value": 1}]},
        source_snapshots=[],
        next_state={},
        ttl_seconds=3600,
    )

    assert committed["state_version"] == 1
    assert datetime.fromisoformat(committed["expires_at"]).microsecond == 123000
    state_query, _, upsert = store.states.update_calls[0]
    assert state_query["owner_subject_id"] == "owner-a"
    assert state_query["session_id"] == "session-a"
    assert upsert is True


class _RaceStateCollection:
    def find_one(self, query, projection=None):
        return None

    def find_one_and_update(self, *args, **kwargs):
        from pymongo.errors import DuplicateKeyError

        raise DuplicateKeyError("concurrent version-zero insert")


def test_mongo_version_zero_duplicate_key_race_is_state_conflict():
    pytest.importorskip("pymongo")
    store = object.__new__(MongoStateStore)
    store.results = _FakeCollection()
    store.states = _RaceStateCollection()
    store.events = []

    with pytest.raises(ContractError) as conflict:
        store.commit_execution(
            subject_id="owner-a",
            session_id="session-a",
            expected_version=0,
            result={"rows": [{"value": 1}]},
            source_snapshots=[],
            next_state={},
            ttl_seconds=3600,
        )

    assert conflict.value.code == "state_conflict"
    assert conflict.value.retryable is True
    result_filter, result_document, upsert = store.results.replace_calls[0]
    assert result_filter["owner_subject_id"] == "owner-a"
    assert result_filter["role"] == "analysis_result"
    assert result_filter["content_sha256"] == sha256_json(result_document["payload"])
    assert upsert is True


@pytest.mark.parametrize(
    ("result_collection", "state_collection"),
    [
        ("agent_v5_result_store", "agent_v6_session_state"),
        ("agent_v6_result_store", "agent_v5_session_state"),
        ("agent_v6_session_state", "agent_v6_result_store"),
        ("agent_v6_result_store", "agent_v6_result_store"),
        ("arbitrary_results", "arbitrary_state"),
    ],
)
def test_mongo_state_store_rejects_non_v6_role_swaps_before_connect(
    result_collection: str, state_collection: str
) -> None:
    with pytest.raises(ContractError) as raised:
        MongoStateStore(
            "mongodb://not-contacted.invalid",
            result_collection=result_collection,
            state_collection=state_collection,
        )
    assert raised.value.code == "state_policy_mismatch"
    assert raised.value.stage == "state_store_config"
