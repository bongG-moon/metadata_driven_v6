"""Owner/session-bound result references and compare-and-swap turn state."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any, Protocol

from .canonical import ContractError, sha256_json


UTC = timezone.utc

_REF_PREFIXES = {
    "analysis_result": "result",
    "source_snapshot": "source",
}


def _now() -> datetime:
    return datetime.now(UTC)


def _utc_datetime(value: Any) -> datetime | None:
    """Normalize Mongo/string expiries before comparing them with an aware UTC clock."""

    parsed: datetime
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        text = value.strip()
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _bson_millisecond(value: datetime) -> datetime:
    """Match MongoDB's BSON datetime precision before hashing or persisting state."""

    normalized = _utc_datetime(value)
    if normalized is None:
        raise ValueError("A datetime value is required")
    return normalized.replace(microsecond=(normalized.microsecond // 1000) * 1000)


def _content_ref(role: str, subject_id: str, session_id: str, content_hash: str) -> str:
    """Build an opaque ref from role, owner, session, and the full content hash."""

    prefix = _REF_PREFIXES.get(role)
    if not prefix:
        raise ValueError(f"Unsupported state reference role: {role}")
    scope_hash = sha256_json(
        {
            "role": role,
            "owner_subject_id": str(subject_id),
            "session_id": str(session_id),
        }
    )
    return f"{prefix}:{scope_hash}:{content_hash}"


def _state_reference_error(code: str, message: str) -> ContractError:
    return ContractError(code, "state_load", message)


def _validate_ref_record(
    value: dict[str, Any],
    *,
    ref_id: str,
    subject_id: str,
    session_id: str,
) -> dict[str, Any]:
    """Fail closed when a persisted content-addressed reference is inconsistent."""

    owner = str(value.get("owner_subject_id") or "")
    stored_session = str(value.get("session_id") or "")
    if owner != str(subject_id) or stored_session != str(session_id):
        raise _state_reference_error(
            "state_reference_forbidden",
            "The stored reference belongs to another owner or session.",
        )

    role = str(value.get("role") or "")
    content_hash = str(value.get("content_sha256") or "")
    payload_hash = sha256_json(value.get("payload"))
    try:
        expected_ref = _content_ref(role, owner, stored_session, content_hash)
    except ValueError as exc:
        raise _state_reference_error(
            "state_reference_forbidden",
            "The stored reference role is invalid.",
        ) from exc
    if (
        not content_hash
        or content_hash != payload_hash
        or str(value.get("ref_id") or "") != str(ref_id)
        or expected_ref != str(ref_id)
    ):
        raise _state_reference_error(
            "state_reference_forbidden",
            "The stored reference failed its identity or content hash check.",
        )

    expiry = _utc_datetime(value.get("expires_at"))
    if expiry is None or expiry <= _now():
        raise _state_reference_error(
            "state_reference_expired",
            "The stored reference has expired.",
        )
    normalized = deepcopy(value)
    normalized.pop("_id", None)
    normalized["expires_at"] = expiry.isoformat()
    return normalized


def _state_conflict(*, expected_version: int, actual_version: int | None = None) -> ContractError:
    details: dict[str, Any] = {"expected_version": int(expected_version)}
    if actual_version is not None:
        details["actual_version"] = int(actual_version)
    return ContractError(
        "state_conflict",
        "state_commit",
        "Another request changed the session state first.",
        details,
        retryable=True,
    )


class StateStore(Protocol):
    def load_state(self, subject_id: str, session_id: str) -> dict[str, Any] | None: ...

    def commit_execution(
        self,
        *,
        subject_id: str,
        session_id: str,
        expected_version: int,
        result: dict[str, Any],
        source_snapshots: list[dict[str, Any]],
        next_state: dict[str, Any],
        ttl_seconds: int,
    ) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]: ...

    def load_ref(self, ref_id: str, subject_id: str, session_id: str) -> dict[str, Any]: ...


class InMemoryStateStore:
    """Deterministic test store with the same ownership/CAS rules as Mongo."""

    def __init__(self) -> None:
        self._states: dict[tuple[str, str], dict[str, Any]] = {}
        self._refs: dict[str, dict[str, Any]] = {}
        self._lock = RLock()
        self.events: list[str] = []

    def load_state(self, subject_id: str, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            value = self._states.get((subject_id, session_id))
            if not value:
                return None
            expiry = _utc_datetime(value.get("expires_at"))
            if expiry is None or expiry <= _now():
                self._states.pop((subject_id, session_id), None)
                return None
            normalized = deepcopy(value)
            normalized["expires_at"] = expiry.isoformat()
            return normalized

    def load_ref(self, ref_id: str, subject_id: str, session_id: str) -> dict[str, Any]:
        with self._lock:
            value = self._refs.get(str(ref_id))
            if not value:
                raise ContractError("state_reference_expired", "state_load", "저장된 분석 결과를 찾을 수 없습니다.")
            return _validate_ref_record(
                value,
                ref_id=str(ref_id),
                subject_id=subject_id,
                session_id=session_id,
            )

    def commit_execution(
        self,
        *,
        subject_id: str,
        session_id: str,
        expected_version: int,
        result: dict[str, Any],
        source_snapshots: list[dict[str, Any]],
        next_state: dict[str, Any],
        ttl_seconds: int,
    ) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
        expiry = _bson_millisecond(
            _now() + timedelta(seconds=max(60, int(ttl_seconds)))
        ).isoformat()
        with self._lock:
            current = self._states.get((subject_id, session_id))
            current_version = int(current.get("state_version", 0)) if current else 0
            if current_version != int(expected_version):
                raise _state_conflict(expected_version=expected_version, actual_version=current_version)
            result_hash = sha256_json(result)
            result_ref = _content_ref("analysis_result", subject_id, session_id, result_hash)
            result_record = {
                "ref_id": result_ref,
                "role": "analysis_result",
                "owner_subject_id": subject_id,
                "session_id": session_id,
                "content_sha256": result_hash,
                "payload": deepcopy(result),
                "expires_at": expiry,
            }
            existing_result = self._refs.get(result_ref)
            if existing_result and (
                existing_result.get("owner_subject_id") != subject_id
                or existing_result.get("session_id") != session_id
                or existing_result.get("role") != "analysis_result"
                or existing_result.get("content_sha256") != result_hash
                or sha256_json(existing_result.get("payload")) != result_hash
            ):
                raise _state_conflict(expected_version=expected_version, actual_version=current_version)
            self._refs[result_ref] = result_record
            self.events.append("result_store")
            source_refs: list[dict[str, Any]] = []
            for source in source_snapshots:
                content_hash = sha256_json(source)
                source_ref = _content_ref("source_snapshot", subject_id, session_id, content_hash)
                source_record = {
                    "ref_id": source_ref,
                    "role": "source_snapshot",
                    "owner_subject_id": subject_id,
                    "session_id": session_id,
                    "content_sha256": content_hash,
                    "payload": deepcopy(source),
                    "expires_at": expiry,
                }
                existing_source = self._refs.get(source_ref)
                if existing_source and (
                    existing_source.get("owner_subject_id") != subject_id
                    or existing_source.get("session_id") != session_id
                    or existing_source.get("role") != "source_snapshot"
                    or existing_source.get("content_sha256") != content_hash
                    or sha256_json(existing_source.get("payload")) != content_hash
                ):
                    raise _state_conflict(expected_version=expected_version, actual_version=current_version)
                self._refs[source_ref] = source_record
                source_refs.append({key: source_record[key] for key in ("ref_id", "role", "content_sha256", "expires_at")})
            committed = deepcopy(next_state)
            committed.setdefault("last_question", "(empty)")
            committed.setdefault("semantic_context", {})
            committed.update(
                {
                    "contract_version": "turn.state.v1",
                    "owner_subject_id": subject_id,
                    "session_id": session_id,
                    "state_version": current_version + 1,
                    "executed_result_ref": result_ref,
                    "expires_at": expiry,
                    "turn_id": f"turn:{sha256_json([subject_id, session_id, current_version + 1, result_hash])[:24]}",
                    "parent_turn_id": current.get("turn_id") if current else None,
                    "parent_state_sha256": sha256_json(current) if current else None,
                }
            )
            state_material = {key: value for key, value in committed.items() if key != "etag"}
            committed["etag"] = f"state-sha256:{sha256_json(state_material)}"
            self._states[(subject_id, session_id)] = committed
            self.events.append("state_cas")
            return deepcopy(committed), {key: result_record[key] for key in ("ref_id", "role", "content_sha256", "expires_at")}, source_refs


V6_RESULT_COLLECTION = "agent_v6_result_store"
V6_STATE_COLLECTION = "agent_v6_session_state"


def validate_state_collection_names(
    result_collection: str, state_collection: str
) -> tuple[str, str]:
    """Bind Mongo write roles to distinct v6-only collections."""

    result_name = str(result_collection or "").strip()
    state_name = str(state_collection or "").strip()
    if (
        result_name != V6_RESULT_COLLECTION
        or state_name != V6_STATE_COLLECTION
        or result_name == state_name
    ):
        raise ContractError(
            "state_policy_mismatch",
            "state_store_config",
            "Mongo state collections are role-bound to distinct v6-only names.",
            {
                "expected": {
                    "result_collection": V6_RESULT_COLLECTION,
                    "state_collection": V6_STATE_COLLECTION,
                },
                "actual": {
                    "result_collection": result_name,
                    "state_collection": state_name,
                },
            },
        )
    return result_name, state_name


class MongoStateStore:
    """Mongo implementation using one result collection and CAS state update."""

    def __init__(
        self,
        uri: str,
        database: str = "datagov",
        result_collection: str = V6_RESULT_COLLECTION,
        state_collection: str = V6_STATE_COLLECTION,
        timeout_ms: int = 5000,
    ) -> None:
        if not str(uri or "").strip():
            raise ValueError("MongoDB URI is required")
        result_name, state_name = validate_state_collection_names(
            result_collection, state_collection
        )
        from pymongo import MongoClient

        self.client = MongoClient(
            uri,
            serverSelectionTimeoutMS=int(timeout_ms),
            connectTimeoutMS=int(timeout_ms),
            tz_aware=True,
        )
        db = self.client[str(database)]
        self.results = db[result_name]
        self.states = db[state_name]
        self.results.create_index("expires_at", expireAfterSeconds=0)
        self.states.create_index("expires_at", expireAfterSeconds=0)
        self.events: list[str] = []

    @staticmethod
    def _state_id(subject_id: str, session_id: str) -> str:
        return f"state:{sha256_json([subject_id, session_id])[:32]}"

    def load_state(self, subject_id: str, session_id: str) -> dict[str, Any] | None:
        identity = {
            "_id": self._state_id(subject_id, session_id),
            "owner_subject_id": subject_id,
            "session_id": session_id,
        }
        value = self.states.find_one(identity, {"_id": 0})
        if not value:
            return None
        expiry = _utc_datetime(value.get("expires_at"))
        if expiry is None or expiry <= _now():
            cleanup_query = deepcopy(identity)
            for key in ("state_version", "etag", "expires_at"):
                if key in value:
                    cleanup_query[key] = value[key]
            self.states.delete_one(cleanup_query)
            return None
        value["expires_at"] = expiry.isoformat()
        return value

    def load_ref(self, ref_id: str, subject_id: str, session_id: str) -> dict[str, Any]:
        value = self.results.find_one(
            {
                "_id": str(ref_id),
                "owner_subject_id": subject_id,
                "session_id": session_id,
            }
        )
        if not value:
            exists = self.results.find_one({"_id": str(ref_id)}, {"_id": 1})
            raise _state_reference_error(
                "state_reference_forbidden" if exists else "state_reference_expired",
                "The stored reference is unavailable or expired.",
            )
        return _validate_ref_record(
            value,
            ref_id=str(ref_id),
            subject_id=subject_id,
            session_id=session_id,
        )

    def commit_execution(
        self,
        *,
        subject_id: str,
        session_id: str,
        expected_version: int,
        result: dict[str, Any],
        source_snapshots: list[dict[str, Any]],
        next_state: dict[str, Any],
        ttl_seconds: int,
    ) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
        from pymongo import ReturnDocument
        from pymongo.errors import DuplicateKeyError

        expiry = _bson_millisecond(
            _now() + timedelta(seconds=max(60, int(ttl_seconds)))
        )
        result_hash = sha256_json(result)
        result_ref = _content_ref("analysis_result", subject_id, session_id, result_hash)
        result_record = {
            "_id": result_ref,
            "ref_id": result_ref,
            "role": "analysis_result",
            "owner_subject_id": subject_id,
            "session_id": session_id,
            "content_sha256": result_hash,
            "payload": deepcopy(result),
            "expires_at": expiry,
        }
        result_identity = {
            "_id": result_ref,
            "ref_id": result_ref,
            "role": "analysis_result",
            "owner_subject_id": subject_id,
            "session_id": session_id,
            "content_sha256": result_hash,
        }
        try:
            self.results.replace_one(result_identity, result_record, upsert=True)
        except DuplicateKeyError as exc:
            raise _state_conflict(expected_version=expected_version) from exc
        self.events.append("result_store")
        source_refs: list[dict[str, Any]] = []
        for source in source_snapshots:
            content_hash = sha256_json(source)
            source_ref = _content_ref("source_snapshot", subject_id, session_id, content_hash)
            record = {
                "_id": source_ref,
                "ref_id": source_ref,
                "role": "source_snapshot",
                "owner_subject_id": subject_id,
                "session_id": session_id,
                "content_sha256": content_hash,
                "payload": deepcopy(source),
                "expires_at": expiry,
            }
            source_identity = {
                "_id": source_ref,
                "ref_id": source_ref,
                "role": "source_snapshot",
                "owner_subject_id": subject_id,
                "session_id": session_id,
                "content_sha256": content_hash,
            }
            try:
                self.results.replace_one(source_identity, record, upsert=True)
            except DuplicateKeyError as exc:
                raise _state_conflict(expected_version=expected_version) from exc
            source_refs.append({"ref_id": source_ref, "role": "source_snapshot", "content_sha256": content_hash, "expires_at": expiry.isoformat()})
        state_id = self._state_id(subject_id, session_id)
        committed = deepcopy(next_state)
        committed.setdefault("last_question", "(empty)")
        committed.setdefault("semantic_context", {})
        committed.update(
            {
                "contract_version": "turn.state.v1",
                "owner_subject_id": subject_id,
                "session_id": session_id,
                "state_version": int(expected_version) + 1,
                "executed_result_ref": result_ref,
                "expires_at": expiry,
                "turn_id": f"turn:{sha256_json([subject_id, session_id, int(expected_version) + 1, result_hash])[:24]}",
                "parent_turn_id": None,
                "parent_state_sha256": None,
            }
        )
        state_identity = {
            "_id": state_id,
            "owner_subject_id": subject_id,
            "session_id": session_id,
        }
        previous = self.states.find_one(state_identity, {"_id": 0}) if int(expected_version) else None
        committed["parent_turn_id"] = previous.get("turn_id") if previous else None
        committed["parent_state_sha256"] = sha256_json(previous) if previous else None
        committed["etag"] = f"state-sha256:{sha256_json({key: value for key, value in committed.items() if key != 'etag'})}"
        if int(expected_version) == 0:
            query = {
                **state_identity,
                "$or": [{"state_version": {"$exists": False}}, {"state_version": 0}],
            }
        else:
            query = {**state_identity, "state_version": int(expected_version)}
        try:
            updated = self.states.find_one_and_update(
                query,
                {"$set": committed, "$setOnInsert": {"_id": state_id}},
                upsert=int(expected_version) == 0,
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError as exc:
            # A concurrent version-0 upsert can lose the race after Mongo decides to insert.
            raise _state_conflict(expected_version=expected_version) from exc
        if not updated:
            raise _state_conflict(expected_version=expected_version)
        self.events.append("state_cas")
        committed["expires_at"] = expiry.isoformat()
        return committed, {"ref_id": result_ref, "role": "analysis_result", "content_sha256": result_hash, "expires_at": expiry.isoformat()}, source_refs


def compact_next_state(request: dict[str, Any], intent: dict[str, Any], plan: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "last_question": str(request.get("question") or "")[:2000],
        "semantic_context": {
            "intent_sha256": intent.get("intent_sha256"),
            "plan_id": plan.get("plan_id"),
            "semantics": deepcopy(intent.get("semantics") or {}),
            "grain": plan.get("result_contract", {}).get("grain", []),
            "columns": result.get("columns", []),
            "row_count": int(result.get("row_count") or 0),
            "datasets": [item.get("dataset_key") for item in plan.get("retrieval_jobs", [])],
            "parameters": {item.get("job_id"): item.get("parameters", {}) for item in plan.get("retrieval_jobs", [])},
        },
    }
