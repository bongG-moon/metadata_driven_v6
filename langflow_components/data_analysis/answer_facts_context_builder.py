# -*- coding: utf-8 -*-
"""GENERATED standalone component: AnswerFactsContextBuilder.

Regenerate with tools/build_standalone_components.py.  Do not hand edit.
"""
from __future__ import annotations

import json

EMBEDDED_SOURCE_MANIFEST = json.loads('{"catalog_contract_version":"metadata.runtime.catalog.v1","catalog_declared_sha256":"6d2c9eaf3a10be1023a5c7aa52c796d5f0caf7287237a488ce38e68840b0e16f","catalog_file_sha256":"c55906d46a8050ee262f970c9c831fc362c48c1bf3b9a184651ceee27a1c9c9d","contract_version":"standalone.source.manifest.v1","reference_sources":{"contracts/schemas/active-domain-pointer.schema.json":"8ff3e114e106d0bc08c83e61947ac967c28cd5390cd0539cb1efdc64b82f9a61","contracts/schemas/analysis-plan.schema.json":"15dbb187f458d03ad4d55063eef898b862529dc68e9f64840d08ab20df9cfb76","contracts/schemas/analysis-result.schema.json":"06e92c0892ff5b209783332f33e4d4ed1855612470b088390e4501591f68065b","contracts/schemas/analysis-route.schema.json":"aadd7504e7f75329b8b6a50634261e073450e6d19d8e14d4a44196c0000e0c04","contracts/schemas/answer-facts.schema.json":"26c573be25f4fade355a37f2ab231f3e0aa8ac83445ee58020a99388648809ed","contracts/schemas/answer-sections.schema.json":"4c1d645c9927879e6a9e877def326ff045b5a01edaf48a566b935bc4734882ab","contracts/schemas/approval-event.schema.json":"4aa6b10eeb875538d00d6de564bdbe24eb093e8727ed57515cbadba63f13d7a9","contracts/schemas/config-registry.schema.json":"2f90dfb2b99e17faa9afecaf1f32295f6d713067aeca66c7dc1544c5713598e9","contracts/schemas/display-options.schema.json":"27bcc5558f8357d2a47d96cd3cdc48535da3643164fd6a539df878301dea08d9","contracts/schemas/domain-package.schema.json":"f39f433985180636bb3b6dfe054cfb8e63998acbe0112f7082a8233b619517f7","contracts/schemas/download-item.schema.json":"91efd43bf2db00bf5e85071fa2992679c3b2dc050251a5c82e839dcd7f5d4086","contracts/schemas/error-registry.schema.json":"f67a1ab5ef2568626d406cb9feb38acfbb6fc593fa04f3da063f8293da653b64","contracts/schemas/error.schema.json":"1a0c89cc1898a894b0490a59f286c68520c0f74be0811f6c06c4aa3e50fe5602","contracts/schemas/evidence-manifest.schema.json":"2805ed7cce742e96b5e10902b096fbec91e40a8aca7fde7bfe95c1d12a9668bb","contracts/schemas/executable-blueprint.schema.json":"e55dbe8faa2f1f2eb933b1548b2b1c37886a0911ceb4e70838427bac2327f14a","contracts/schemas/executed-result.schema.json":"eaba5818e5fb30e2a572f5a81488d9ba34032adcf3af55dfbb0d4287afc7e435","contracts/schemas/flow-inventory.schema.json":"cdce69d64a9df37a88e139a0fd0900d38d9475d2a8f13ff9a9b5c1bf0777b672","contracts/schemas/gaia-metadata.schema.json":"196264a98d131ca1c5b897a4458c67d875753a7e11d6be059f2078c2e4b67c58","contracts/schemas/metadata-annotation-proposal.schema.json":"f0b227cc42a528d6e0b95f1c8c4a1bf6bbb6871d17d32c108d65b47d2b0ddc7f","contracts/schemas/metadata-authoring-draft.schema.json":"93b424e2d17205074ab833bed6e0463492c50fc918162ebdaa544561679e027c","contracts/schemas/metadata-authoring-proposal.schema.json":"8ee3fc86d8f596c554443c16ad619822e63315ed8f2bfd06311987fc63322edd","contracts/schemas/metadata-authoring-response.schema.json":"da776b8a156d007c5bd95e86ad10cfb5a8ac7f06c2cae0c52aeb96b6a36415f6","contracts/schemas/metadata-bootstrap-dataset-ir.schema.json":"351260f7ed418b35f4ca1e5012a353b1d8f820ea21dfc8880483c193880af3b6","contracts/schemas/metadata-bootstrap-main-filter-ir.schema.json":"41c849c88b803d53af9c02c3d50127c47e8ee38e46d7b0a1ad0d09c3638e48fa","contracts/schemas/metadata-bundle.schema.json":"985ffe44974cf14d6c52a8188d54c3b209c00478e83888f00c359cd056d5dc81","contracts/schemas/metadata-envelope.schema.json":"9abca177e22b570f2158dace05256f671c0acbd054705dfe4f34611fbdae2048","contracts/schemas/model-profile.schema.json":"14345c16f629fc03a3de2cdd2fe469bef1fdc82cd2f93954ce1f4204ba82f356","contracts/schemas/operator-registry.schema.json":"acd003c6db66b470a2653fc8a97caaf3856c9d4cfd934bc0f27ef609787c2746","contracts/schemas/pending-metadata-write.schema.json":"af7a0593fafbdcea16f1212ba92484525626e43f2a25d91f9c310a80f5b37a4d","contracts/schemas/query-registry.schema.json":"8422a44035eb2a06381166d69a185036c698f581b17741a8c4686fbeea109040","contracts/schemas/registered-call.schema.json":"219a775c3a514501c66e077ef03a107a71f4d45af15aab2117c3cb1ab8f75811","contracts/schemas/registered-function-card.schema.json":"bc9ca8b01c90d2d11737f1a70586e9227510b67fdab26c8ae605d9e830170dfd","contracts/schemas/request-capsule.schema.json":"675e661653098288d6cc9e6e9b3599ed3bf3e05d6d592ac66d9ed46b9fd2afaf","contracts/schemas/resolved-candidate-bundle.schema.json":"a24b7d2fc3798f1dd69e1af94a7071eae8fb56d93a4191258953fd63b4211568","contracts/schemas/response.schema.json":"ab971defd116c05407b2de144617f1d99286976960302315855a12fbdc4efd2d","contracts/schemas/retrieval-job-bundle.schema.json":"e73cd6e6c50bb24b528111c36c410af3afe2fe3ff28d3d906cfe023263a12105","contracts/schemas/runtime-catalog-v2.schema.json":"3f7f6c5154c9e7922dd65490e9166ba0038c6a242258ec30d409d8a553948fed","contracts/schemas/semantic-intent-selection.schema.json":"a70c99e36060531fac9730c02f706ffa8d108b872c5abe0e2d05cafa459e6a75","contracts/schemas/semantic-intent.schema.json":"a743b7e26168dda04a7f46205fed67987a587cf3cce939cf57b228b099bfad53","contracts/schemas/source-bundle.schema.json":"a5330ef1b104df5dd0f19385b5e7994ee5469feffa110ee84087b7992258ea92","contracts/schemas/source-result.schema.json":"f342dcf0f948f7f99899335d83f302f2aaa38b05bb246eb06f9c1da0161f516c","contracts/schemas/trace.schema.json":"3f7cb2dd4e88b5f9f09695347ce42d8b98d5c4534d8fab41cca8ea1c9e3d484e","contracts/schemas/turn-state.schema.json":"688ad4f5ac1b133e60e3a2ef2bef56d0b18c87a41d2c6c236264285aeba32280","contracts/schemas/unsupported-telemetry.schema.json":"8c3675797be935d6fd52db2883d433d464df2fdecc5e0d52e795a5fa1e6c8439","contracts/schemas/validation-case.schema.json":"23304f969ca614324f7a74b52edc72c4e6753e76c476a77fc8db68f089941682","reference_runtime/authoring_blueprint.py":"9fc416a04e0da317586ad8abf9831bf650746a7f1907ad62fcaef4012327fe71","reference_runtime/authoring_source_manifest.py":"311bd68482e163a781bf11aa449587879f659fa9c36f7564129ecea44b88170c","reference_runtime/canonical.py":"338b8b013b9311f94d9b5ff7a3d5902576e9dfb88b40d72d37436025806c2d1d","reference_runtime/contracts.py":"5d16082db0bf437e537a24352834548e48e157a4c740659e9c9f1a0e46960d6e","reference_runtime/domain_authoring_patches.py":"4c78c72bc2412cbe78e74372b7c5af658ada8de1b8058b228f02d2b68b41c445","reference_runtime/domain_packages.py":"801b2c66191c65fb2d961d40e6e10db50a5d4ffc7be225b1d37a9fc2b4b9f43c","reference_runtime/dummy_data.py":"c02824f9ddba81496d99a4b58bda8e6bedf0ce464d47abca682071ab24cae57d","reference_runtime/engine.py":"62df5f1a06c0a2765085826bec3e73f99f02da470850d180f2d7a53078c67606","reference_runtime/generic_v2_candidates.py":"95f5821b05d7d70f70ebd0339a316bcc1367b5499553319b8d8995df251a4c56","reference_runtime/generic_v2_planner.py":"142665c8050c9302830cedf45928a25b73cd34e80bec66de9ba77003209176d3","reference_runtime/metadata_compiler.py":"99544e6094883b4241d010af2bec5d67e6205d34634ad46d6e2ee173107336e3","reference_runtime/plan_compiler.py":"6dc3bef703732a6cba6734f63970b22ecd599139067fa78a16bf5b3be003e735","reference_runtime/presenter.py":"7e9baa6ed984a5d46ae06bff614a4a4feb8caeb7e733146bb3db3d7f801ea080","reference_runtime/registered_functions.py":"03f2ed1e2cb158eee5dd23cd99a408f14fdf3abea7fb630cfb31044cfe8f4d8e","reference_runtime/request_literals.py":"00493f9e342ab3065215805ae32f3068cb594209434bf280f2bb4f23c4be62ff","reference_runtime/source_contracts.py":"c43d8865ff045f4c26c5194262620a50961be5b56552c5cc6e7d580b2c11d7b0","reference_runtime/state_contracts.py":"5a03fff6684850361904add4e4d15ea578617d1fce20564119bbac175fb334ae","reference_runtime/typed_executor.py":"0c1fc3bbb055cd32d1da3446afab0aca5351e844536624ae9ab953c78c5dfe3b"}}')


import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

def json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if hasattr(value, 'item') and callable(value.item):
        try:
            return json_value(value.item())
        except Exception:
            pass
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(json_value(value), ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')

def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()

def byte_size(value: Any) -> int:
    return len(canonical_bytes(value))

def bounded(value: Any, max_bytes: int, label: str) -> Any:
    size = byte_size(value)
    if size > max_bytes:
        raise ContractError('metadata_budget_exceeded', 'payload_budget', f'{label} payload가 허용 크기를 초과했습니다.', {'label': label, 'actual_bytes': size, 'max_bytes': max_bytes})
    return value

@dataclass(slots=True)
class ContractError(Exception):
    code: str
    stage: str
    public_message: str
    details: dict[str, Any] | None = None
    retryable: bool = False

    def __str__(self) -> str:
        return f'{self.code}: {self.public_message}'

    def as_dict(self, trace_id: str='') -> dict[str, Any]:
        safe_details = self.details if isinstance(self.details, dict) else {}
        payload = {'error_registry_version': 'error_registry.v1', 'error_id': f'error:{sha256_json([self.code, self.stage, safe_details])[:24]}', 'code': self.code, 'stage': self.stage, 'message': self.public_message, 'retryable': bool(self.retryable), 'details': safe_details, 'trace_id': trace_id}
        return payload


import json
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator, FormatChecker
ERROR_CODE_BY_SCHEMA = {'request-capsule.schema.json': 'intent_contract_error', 'analysis-route.schema.json': 'route_contract_error', 'semantic-intent.schema.json': 'intent_contract_error', 'analysis-plan.schema.json': 'plan_contract_error', 'source-result.schema.json': 'source_schema_mismatch', 'analysis-result.schema.json': 'result_schema_violation', 'executed-result.schema.json': 'result_schema_violation', 'turn-state.schema.json': 'state_conflict', 'answer-facts.schema.json': 'answer_claim_violation', 'answer-sections.schema.json': 'answer_claim_violation', 'display-options.schema.json': 'answer_claim_violation', 'response.schema.json': 'answer_claim_violation', 'gaia-metadata.schema.json': 'answer_claim_violation', 'error.schema.json': 'answer_claim_violation', 'metadata-authoring-draft.schema.json': 'metadata_dependency_error', 'executable-blueprint.schema.json': 'metadata_dependency_error', 'runtime-catalog-v2.schema.json': 'metadata_dependency_error', 'registered-function-card.schema.json': 'metadata_dependency_error', 'registered-call.schema.json': 'plan_contract_error', 'domain-package.schema.json': 'metadata_dependency_error', 'active-domain-pointer.schema.json': 'metadata_dependency_error'}

@lru_cache(maxsize=64)
def _load_schema_cached(name: str) -> dict[str, Any]:
    if name not in EMBEDDED_SCHEMAS:
        raise FileNotFoundError(name)
    return EMBEDDED_SCHEMAS[name]

def load_schema(name: str) -> dict[str, Any]:
    """Return an isolated schema copy so callers cannot mutate the cache."""
    return deepcopy(_load_schema_cached(name))

@lru_cache(maxsize=64)
def contract_validator(name: str) -> Draft202012Validator:
    schema = _load_schema_cached(name)
    Draft202012Validator.check_schema(schema)
    format_checker = FormatChecker()

    @format_checker.checks('date-time', raises=(TypeError, ValueError))
    def _date_time_with_offset(value: object) -> bool:
        if not isinstance(value, str):
            return False
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed.tzinfo is not None
    return Draft202012Validator(schema, format_checker=format_checker)

def validate_contract(value: Any, schema_name: str, *, stage: str='contract_validation', error_code: str | None=None) -> Any:
    """Validate a boundary payload without mutating it.

    ``FormatChecker`` is deliberately enabled: ``date-time`` and other format
    declarations are executable parts of the boundary contract, not comments.
    """
    errors = sorted(contract_validator(schema_name).iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        path = '.'.join((str(part) for part in first.absolute_path)) or '$'
        raise ContractError(error_code or ERROR_CODE_BY_SCHEMA.get(schema_name, 'plan_contract_error'), stage, '계약 형식이 올바르지 않습니다.', {'schema': schema_name, 'path': path, 'reason': first.message[:400]})
    return value


from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any, Protocol
UTC = timezone.utc
_REF_PREFIXES = {'analysis_result': 'result', 'source_snapshot': 'source'}

def _now() -> datetime:
    return datetime.now(UTC)

def _utc_datetime(value: Any) -> datetime | None:
    """Normalize Mongo/string expiries before comparing them with an aware UTC clock."""
    parsed: datetime
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        text = value.strip()
        if text.endswith('Z'):
            text = f'{text[:-1]}+00:00'
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
        raise ValueError('A datetime value is required')
    return normalized.replace(microsecond=normalized.microsecond // 1000 * 1000)

def _content_ref(role: str, subject_id: str, session_id: str, content_hash: str) -> str:
    """Build an opaque ref from role, owner, session, and the full content hash."""
    prefix = _REF_PREFIXES.get(role)
    if not prefix:
        raise ValueError(f'Unsupported state reference role: {role}')
    scope_hash = sha256_json({'role': role, 'owner_subject_id': str(subject_id), 'session_id': str(session_id)})
    return f'{prefix}:{scope_hash}:{content_hash}'

def _state_reference_error(code: str, message: str) -> ContractError:
    return ContractError(code, 'state_load', message)

def _validate_ref_record(value: dict[str, Any], *, ref_id: str, subject_id: str, session_id: str) -> dict[str, Any]:
    """Fail closed when a persisted content-addressed reference is inconsistent."""
    owner = str(value.get('owner_subject_id') or '')
    stored_session = str(value.get('session_id') or '')
    if owner != str(subject_id) or stored_session != str(session_id):
        raise _state_reference_error('state_reference_forbidden', 'The stored reference belongs to another owner or session.')
    role = str(value.get('role') or '')
    content_hash = str(value.get('content_sha256') or '')
    payload_hash = sha256_json(value.get('payload'))
    try:
        expected_ref = _content_ref(role, owner, stored_session, content_hash)
    except ValueError as exc:
        raise _state_reference_error('state_reference_forbidden', 'The stored reference role is invalid.') from exc
    if not content_hash or content_hash != payload_hash or str(value.get('ref_id') or '') != str(ref_id) or (expected_ref != str(ref_id)):
        raise _state_reference_error('state_reference_forbidden', 'The stored reference failed its identity or content hash check.')
    expiry = _utc_datetime(value.get('expires_at'))
    if expiry is None or expiry <= _now():
        raise _state_reference_error('state_reference_expired', 'The stored reference has expired.')
    normalized = deepcopy(value)
    normalized.pop('_id', None)
    normalized['expires_at'] = expiry.isoformat()
    return normalized

def _state_conflict(*, expected_version: int, actual_version: int | None=None) -> ContractError:
    details: dict[str, Any] = {'expected_version': int(expected_version)}
    if actual_version is not None:
        details['actual_version'] = int(actual_version)
    return ContractError('state_conflict', 'state_commit', 'Another request changed the session state first.', details, retryable=True)

class StateStore(Protocol):

    def load_state(self, subject_id: str, session_id: str) -> dict[str, Any] | None:
        ...

    def commit_execution(self, *, subject_id: str, session_id: str, expected_version: int, result: dict[str, Any], source_snapshots: list[dict[str, Any]], next_state: dict[str, Any], ttl_seconds: int) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
        ...

    def load_ref(self, ref_id: str, subject_id: str, session_id: str) -> dict[str, Any]:
        ...

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
            expiry = _utc_datetime(value.get('expires_at'))
            if expiry is None or expiry <= _now():
                self._states.pop((subject_id, session_id), None)
                return None
            normalized = deepcopy(value)
            normalized['expires_at'] = expiry.isoformat()
            return normalized

    def load_ref(self, ref_id: str, subject_id: str, session_id: str) -> dict[str, Any]:
        with self._lock:
            value = self._refs.get(str(ref_id))
            if not value:
                raise ContractError('state_reference_expired', 'state_load', '저장된 분석 결과를 찾을 수 없습니다.')
            return _validate_ref_record(value, ref_id=str(ref_id), subject_id=subject_id, session_id=session_id)

    def commit_execution(self, *, subject_id: str, session_id: str, expected_version: int, result: dict[str, Any], source_snapshots: list[dict[str, Any]], next_state: dict[str, Any], ttl_seconds: int) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
        expiry = _bson_millisecond(_now() + timedelta(seconds=max(60, int(ttl_seconds)))).isoformat()
        with self._lock:
            current = self._states.get((subject_id, session_id))
            current_version = int(current.get('state_version', 0)) if current else 0
            if current_version != int(expected_version):
                raise _state_conflict(expected_version=expected_version, actual_version=current_version)
            result_hash = sha256_json(result)
            result_ref = _content_ref('analysis_result', subject_id, session_id, result_hash)
            result_record = {'ref_id': result_ref, 'role': 'analysis_result', 'owner_subject_id': subject_id, 'session_id': session_id, 'content_sha256': result_hash, 'payload': deepcopy(result), 'expires_at': expiry}
            existing_result = self._refs.get(result_ref)
            if existing_result and (existing_result.get('owner_subject_id') != subject_id or existing_result.get('session_id') != session_id or existing_result.get('role') != 'analysis_result' or (existing_result.get('content_sha256') != result_hash) or (sha256_json(existing_result.get('payload')) != result_hash)):
                raise _state_conflict(expected_version=expected_version, actual_version=current_version)
            self._refs[result_ref] = result_record
            self.events.append('result_store')
            source_refs: list[dict[str, Any]] = []
            for source in source_snapshots:
                content_hash = sha256_json(source)
                source_ref = _content_ref('source_snapshot', subject_id, session_id, content_hash)
                source_record = {'ref_id': source_ref, 'role': 'source_snapshot', 'owner_subject_id': subject_id, 'session_id': session_id, 'content_sha256': content_hash, 'payload': deepcopy(source), 'expires_at': expiry}
                existing_source = self._refs.get(source_ref)
                if existing_source and (existing_source.get('owner_subject_id') != subject_id or existing_source.get('session_id') != session_id or existing_source.get('role') != 'source_snapshot' or (existing_source.get('content_sha256') != content_hash) or (sha256_json(existing_source.get('payload')) != content_hash)):
                    raise _state_conflict(expected_version=expected_version, actual_version=current_version)
                self._refs[source_ref] = source_record
                source_refs.append({key: source_record[key] for key in ('ref_id', 'role', 'content_sha256', 'expires_at')})
            committed = deepcopy(next_state)
            committed.setdefault('last_question', '(empty)')
            committed.setdefault('semantic_context', {})
            committed.update({'contract_version': 'turn.state.v1', 'owner_subject_id': subject_id, 'session_id': session_id, 'state_version': current_version + 1, 'executed_result_ref': result_ref, 'expires_at': expiry, 'turn_id': f'turn:{sha256_json([subject_id, session_id, current_version + 1, result_hash])[:24]}', 'parent_turn_id': current.get('turn_id') if current else None, 'parent_state_sha256': sha256_json(current) if current else None})
            state_material = {key: value for key, value in committed.items() if key != 'etag'}
            committed['etag'] = f'state-sha256:{sha256_json(state_material)}'
            self._states[subject_id, session_id] = committed
            self.events.append('state_cas')
            return (deepcopy(committed), {key: result_record[key] for key in ('ref_id', 'role', 'content_sha256', 'expires_at')}, source_refs)
V6_RESULT_COLLECTION = 'agent_v6_result_store'
V6_STATE_COLLECTION = 'agent_v6_session_state'

def validate_state_collection_names(result_collection: str, state_collection: str) -> tuple[str, str]:
    """Bind Mongo write roles to distinct v6-only collections."""
    result_name = str(result_collection or '').strip()
    state_name = str(state_collection or '').strip()
    if result_name != V6_RESULT_COLLECTION or state_name != V6_STATE_COLLECTION or result_name == state_name:
        raise ContractError('state_policy_mismatch', 'state_store_config', 'Mongo state collections are role-bound to distinct v6-only names.', {'expected': {'result_collection': V6_RESULT_COLLECTION, 'state_collection': V6_STATE_COLLECTION}, 'actual': {'result_collection': result_name, 'state_collection': state_name}})
    return (result_name, state_name)

class MongoStateStore:
    """Mongo implementation using one result collection and CAS state update."""

    def __init__(self, uri: str, database: str='datagov', result_collection: str=V6_RESULT_COLLECTION, state_collection: str=V6_STATE_COLLECTION, timeout_ms: int=5000) -> None:
        if not str(uri or '').strip():
            raise ValueError('MongoDB URI is required')
        result_name, state_name = validate_state_collection_names(result_collection, state_collection)
        from pymongo import MongoClient
        self.client = MongoClient(uri, serverSelectionTimeoutMS=int(timeout_ms), connectTimeoutMS=int(timeout_ms), tz_aware=True)
        db = self.client[str(database)]
        self.results = db[result_name]
        self.states = db[state_name]
        self.results.create_index('expires_at', expireAfterSeconds=0)
        self.states.create_index('expires_at', expireAfterSeconds=0)
        self.events: list[str] = []

    @staticmethod
    def _state_id(subject_id: str, session_id: str) -> str:
        return f'state:{sha256_json([subject_id, session_id])[:32]}'

    def load_state(self, subject_id: str, session_id: str) -> dict[str, Any] | None:
        identity = {'_id': self._state_id(subject_id, session_id), 'owner_subject_id': subject_id, 'session_id': session_id}
        value = self.states.find_one(identity, {'_id': 0})
        if not value:
            return None
        expiry = _utc_datetime(value.get('expires_at'))
        if expiry is None or expiry <= _now():
            cleanup_query = deepcopy(identity)
            for key in ('state_version', 'etag', 'expires_at'):
                if key in value:
                    cleanup_query[key] = value[key]
            self.states.delete_one(cleanup_query)
            return None
        value['expires_at'] = expiry.isoformat()
        return value

    def load_ref(self, ref_id: str, subject_id: str, session_id: str) -> dict[str, Any]:
        value = self.results.find_one({'_id': str(ref_id), 'owner_subject_id': subject_id, 'session_id': session_id})
        if not value:
            exists = self.results.find_one({'_id': str(ref_id)}, {'_id': 1})
            raise _state_reference_error('state_reference_forbidden' if exists else 'state_reference_expired', 'The stored reference is unavailable or expired.')
        return _validate_ref_record(value, ref_id=str(ref_id), subject_id=subject_id, session_id=session_id)

    def commit_execution(self, *, subject_id: str, session_id: str, expected_version: int, result: dict[str, Any], source_snapshots: list[dict[str, Any]], next_state: dict[str, Any], ttl_seconds: int) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
        from pymongo import ReturnDocument
        from pymongo.errors import DuplicateKeyError
        expiry = _bson_millisecond(_now() + timedelta(seconds=max(60, int(ttl_seconds))))
        result_hash = sha256_json(result)
        result_ref = _content_ref('analysis_result', subject_id, session_id, result_hash)
        result_record = {'_id': result_ref, 'ref_id': result_ref, 'role': 'analysis_result', 'owner_subject_id': subject_id, 'session_id': session_id, 'content_sha256': result_hash, 'payload': deepcopy(result), 'expires_at': expiry}
        result_identity = {'_id': result_ref, 'ref_id': result_ref, 'role': 'analysis_result', 'owner_subject_id': subject_id, 'session_id': session_id, 'content_sha256': result_hash}
        try:
            self.results.replace_one(result_identity, result_record, upsert=True)
        except DuplicateKeyError as exc:
            raise _state_conflict(expected_version=expected_version) from exc
        self.events.append('result_store')
        source_refs: list[dict[str, Any]] = []
        for source in source_snapshots:
            content_hash = sha256_json(source)
            source_ref = _content_ref('source_snapshot', subject_id, session_id, content_hash)
            record = {'_id': source_ref, 'ref_id': source_ref, 'role': 'source_snapshot', 'owner_subject_id': subject_id, 'session_id': session_id, 'content_sha256': content_hash, 'payload': deepcopy(source), 'expires_at': expiry}
            source_identity = {'_id': source_ref, 'ref_id': source_ref, 'role': 'source_snapshot', 'owner_subject_id': subject_id, 'session_id': session_id, 'content_sha256': content_hash}
            try:
                self.results.replace_one(source_identity, record, upsert=True)
            except DuplicateKeyError as exc:
                raise _state_conflict(expected_version=expected_version) from exc
            source_refs.append({'ref_id': source_ref, 'role': 'source_snapshot', 'content_sha256': content_hash, 'expires_at': expiry.isoformat()})
        state_id = self._state_id(subject_id, session_id)
        committed = deepcopy(next_state)
        committed.setdefault('last_question', '(empty)')
        committed.setdefault('semantic_context', {})
        committed.update({'contract_version': 'turn.state.v1', 'owner_subject_id': subject_id, 'session_id': session_id, 'state_version': int(expected_version) + 1, 'executed_result_ref': result_ref, 'expires_at': expiry, 'turn_id': f'turn:{sha256_json([subject_id, session_id, int(expected_version) + 1, result_hash])[:24]}', 'parent_turn_id': None, 'parent_state_sha256': None})
        state_identity = {'_id': state_id, 'owner_subject_id': subject_id, 'session_id': session_id}
        previous = self.states.find_one(state_identity, {'_id': 0}) if int(expected_version) else None
        committed['parent_turn_id'] = previous.get('turn_id') if previous else None
        committed['parent_state_sha256'] = sha256_json(previous) if previous else None
        committed['etag'] = f"state-sha256:{sha256_json({key: value for key, value in committed.items() if key != 'etag'})}"
        if int(expected_version) == 0:
            query = {**state_identity, '$or': [{'state_version': {'$exists': False}}, {'state_version': 0}]}
        else:
            query = {**state_identity, 'state_version': int(expected_version)}
        try:
            updated = self.states.find_one_and_update(query, {'$set': committed, '$setOnInsert': {'_id': state_id}}, upsert=int(expected_version) == 0, return_document=ReturnDocument.AFTER)
        except DuplicateKeyError as exc:
            raise _state_conflict(expected_version=expected_version) from exc
        if not updated:
            raise _state_conflict(expected_version=expected_version)
        self.events.append('state_cas')
        committed['expires_at'] = expiry.isoformat()
        return (committed, {'ref_id': result_ref, 'role': 'analysis_result', 'content_sha256': result_hash, 'expires_at': expiry.isoformat()}, source_refs)

def compact_next_state(request: dict[str, Any], intent: dict[str, Any], plan: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {'last_question': str(request.get('question') or '')[:2000], 'semantic_context': {'intent_sha256': intent.get('intent_sha256'), 'plan_id': plan.get('plan_id'), 'semantics': deepcopy(intent.get('semantics') or {}), 'grain': plan.get('result_contract', {}).get('grain', []), 'columns': result.get('columns', []), 'row_count': int(result.get('row_count') or 0), 'datasets': [item.get('dataset_key') for item in plan.get('retrieval_jobs', [])], 'parameters': {item.get('job_id'): item.get('parameters', {}) for item in plan.get('retrieval_jobs', [])}}}


import json
from copy import deepcopy
from typing import Any
from urllib.parse import quote
DEFAULT_DISPLAY_OPTIONS = {'profile': 'standard', 'include_diagnostics': False, 'show_result_table': True, 'table_preview_limit': 10, 'show_analysis_evidence': False, 'show_download_links': True, 'show_notices': True, 'show_applied_criteria': True, 'show_next_questions': False, 'show_intent_analysis': False, 'show_data_retrieval': False, 'show_execution_plan': False}

def normalize_display_options(value: Any) -> dict[str, Any]:
    """Normalize the v5-compatible toggles into the closed v6 contract."""
    raw = value if isinstance(value, dict) else {}
    result = deepcopy(DEFAULT_DISPLAY_OPTIONS)
    profile = str(raw.get('profile') or result['profile']).strip()
    result['profile'] = profile or 'standard'
    for key in result:
        if key in {'profile', 'table_preview_limit'}:
            continue
        if key in raw:
            result[key] = bool(raw[key])
    if 'show_pandas_code' in raw and 'show_execution_plan' not in raw:
        result['show_execution_plan'] = bool(raw.get('show_pandas_code'))
    if result['include_diagnostics']:
        result['show_intent_analysis'] = True
        result['show_data_retrieval'] = True
        result['show_execution_plan'] = True
    try:
        result['table_preview_limit'] = max(1, min(20, int(raw.get('table_preview_limit', 10))))
    except (TypeError, ValueError):
        result['table_preview_limit'] = 10
    normalized = {'contract_version': 'display.options.v1', **result}
    return validate_contract(normalized, 'display-options.schema.json', stage='display_options')

def build_answer_facts(request: dict[str, Any], plan: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    row_count = int(result.get('row_count') or 0)
    columns = [str(item) for item in result.get('columns', [])]
    datasets = [str(item.get('dataset_key') or '') for item in plan.get('retrieval_jobs', [])]
    parameters = {str(item.get('job_id')): item.get('parameters', {}) for item in plan.get('retrieval_jobs', [])}
    fact_items = [{'fact_id': 'fact:row_count', 'type': 'integer', 'value': row_count}, {'fact_id': 'fact:columns', 'type': 'string_list', 'value': columns}, {'fact_id': 'fact:datasets', 'type': 'string_list', 'value': datasets}, {'fact_id': 'fact:parameters', 'type': 'object', 'value': parameters}]
    material = {'contract_version': 'answer.facts.v1', 'question': str(request.get('question') or ''), 'facts': fact_items, 'result_sha256': str(result.get('result_sha256') or ''), 'plan_id': str(plan.get('plan_id') or '')}
    facts = {**material, 'facts_sha256': sha256_json(material)}
    return validate_contract(facts, 'answer-facts.schema.json', stage='answer_facts')

def _next_questions(plan: dict[str, Any], result: dict[str, Any]) -> list[dict[str, str]]:
    suggestions: list[str] = []
    if int(result.get('row_count') or 0) > 1:
        suggestions.append('이 결과에서 값이 가장 큰 항목만 보여줘')
    suggestions.append('적용한 조회 조건과 계산 근거를 설명해줘')
    if any((item.get('dataset_key') == 'production_today' for item in plan.get('retrieval_jobs', []))):
        suggestions.append('같은 조건으로 어제 결과도 보여줘')
    return [{'id': f'followup:{index}', 'text': text} for index, text in enumerate(suggestions[:3], start=1)]

def _usage(route: dict[str, Any]) -> dict[str, int]:
    return {'intent_llm_calls': int(route.get('intent_llm_calls') or 0), 'pandas_code_llm_calls': 0, 'pandas_repair_llm_calls': 0, 'answer_llm_calls': 0}

def _response_hash_material(response: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in response.items() if key != 'response_sha256'}

def validate_response_hash(response: dict[str, Any]) -> dict[str, Any]:
    """Reject adapter input that is not the immutable engine response."""
    if not isinstance(response, dict) or response.get('contract_version') != 'response.v1':
        raise ContractError('answer_claim_violation', 'response_adapter', 'response.v1 payload가 필요합니다.')
    expected = sha256_json(_response_hash_material(response))
    if response.get('response_sha256') != expected:
        raise ContractError('answer_claim_violation', 'response_adapter', '응답 해시가 일치하지 않습니다.', {'expected_sha256': expected, 'actual_sha256': response.get('response_sha256')})
    validate_contract(response, 'response.schema.json', stage='response_adapter')
    return response

def validate_authoring_response_hash(response: dict[str, Any]) -> dict[str, Any]:
    """Validate the closed authoring terminal contract and its immutable hash."""
    if not isinstance(response, dict):
        raise ContractError('response_contract_error', 'authoring_terminal', 'Metadata authoring response must be an object.')
    validate_contract(response, 'metadata-authoring-response.schema.json', stage='authoring_terminal', error_code='response_contract_error')
    expected = sha256_json({key: value for key, value in response.items() if key != 'response_sha256'})
    if response.get('response_sha256') != expected:
        raise ContractError('response_contract_error', 'authoring_terminal', 'Metadata authoring response hash does not match its payload.')
    return response

def _finalize_response(material: dict[str, Any]) -> dict[str, Any]:
    bounded(material, 256 * 1024 - 128, 'response')
    response = {**material, 'response_sha256': sha256_json(material)}
    validate_contract(response, 'response.schema.json', stage='response_assembly')
    return bounded(response, 256 * 1024, 'response')

def assemble_response(*, request: dict[str, Any], intent: dict[str, Any], plan: dict[str, Any], result: dict[str, Any], answer_facts: dict[str, Any], state: dict[str, Any], result_ref: dict[str, Any], source_refs: list[dict[str, Any]], route_telemetry: dict[str, Any], source_diagnostics: list[dict[str, Any]], data_mode: str, download_base_url: str='', events: list[str] | None=None) -> dict[str, Any]:
    rows = result.get('rows') if isinstance(result.get('rows'), list) else []
    columns = [str(item) for item in result.get('columns', [])]
    row_count = int(result.get('row_count') or 0)
    result_status = str(result.get('status') or ('empty' if row_count == 0 else 'ok'))
    status = 'empty' if row_count == 0 and result_status in {'ok', 'empty'} else result_status
    headline = '조회 결과가 없습니다.' if status == 'empty' else f'요청한 분석 결과는 총 {row_count}건입니다.'
    persistent = bool(isinstance(result_ref, dict) and result_ref.get('ref_id'))
    refs = [deepcopy(result_ref)] + [deepcopy(item) for item in source_refs] if persistent else []
    for item in refs:
        ref_id = str(item.get('ref_id') or '')
        item['store'] = 'agent_v6_result_store'
        item['path'] = 'payload.rows'
        item['download_url'] = f"{download_base_url.rstrip('/')}/download.csv?download_ref={quote(ref_id)}" if download_base_url and ref_id else ''
    notices: list[dict[str, str]] = []
    next_questions = _next_questions(plan, result)
    answer_sections = {'contract_version': 'answer.sections.v1', 'summary': {'headline': headline, 'fact_ids': ['fact:row_count']}, 'result_table': {'row_source': 'data.rows', 'columns': columns, 'row_count': row_count, 'data_ref': str(result_ref.get('ref_id') or '')}, 'applied_criteria': {'datasets': [item.get('dataset_key') for item in plan.get('retrieval_jobs', [])], 'required_params': {item.get('job_id'): item.get('parameters', {}) for item in plan.get('retrieval_jobs', [])}, 'analysis_filters': [item.get('filters') for item in plan.get('retrieval_jobs', []) if item.get('filters')], 'group_by': plan.get('result_contract', {}).get('grain', []), 'metrics': list(plan.get('lineage', {}).keys())}, 'evidence': {'facts_sha256': answer_facts.get('facts_sha256'), 'plan_id': plan.get('plan_id'), 'result_sha256': result.get('result_sha256')}, 'notices': notices, 'downloads': [{'ref_id': str(item.get('ref_id') or ''), 'role': str(item.get('role') or ''), 'label': '분석 결과' if item.get('role') == 'analysis_result' else '조회 원본', 'url': str(item.get('download_url') or '')} for item in refs], 'next_questions': next_questions}
    validate_contract(answer_sections, 'answer-sections.schema.json', stage='answer_sections')
    trace_id = f"trace:{sha256_json([request.get('request_id'), plan.get('plan_id'), result.get('result_sha256')])[:24]}"
    usage = _usage(route_telemetry)
    material = {'contract_version': 'response.v1', 'response_type': 'data_analysis', 'status': status, 'stage_status': {'overall': status, 'intent': 'skipped' if route_telemetry.get('intent_llm_calls') == 0 else 'ok', 'retrieval': 'ok', 'analysis': status}, 'message': headline, 'data_mode': str(data_mode or 'dummy'), 'analysis_mode': 'typed_ir', 'answer_sections': answer_sections, 'request': {'request_id': request.get('request_id'), 'question': request.get('question'), 'session_id': request.get('session_id'), 'reference_instant': request.get('reference_instant'), 'timezone': request.get('timezone')}, 'intent_plan': {'intent_sha256': intent.get('intent_sha256'), 'intent_candidate_id': intent.get('intent_candidate_id'), 'plan_id': plan.get('plan_id'), 'plan_fingerprint': plan.get('plan_fingerprint'), 'semantic_intent': intent.get('semantics', {})}, 'analysis': {'status': status, 'result_sha256': result.get('result_sha256'), 'operation_trace': result.get('operation_trace', []), 'execution_ir': plan.get('operations', []), 'lineage': result.get('lineage', {})}, 'clarification': None, 'data': {'columns': columns, 'rows': rows[:50], 'row_count': row_count}, 'data_refs': refs, 'state': {'state_version': state.get('state_version'), 'executed_result_ref': state.get('executed_result_ref'), 'expires_at': state.get('expires_at')} if persistent else None, 'trace': {'trace_id': trace_id, 'route': deepcopy(route_telemetry), 'retrieval': deepcopy(source_diagnostics), 'usage': usage, 'commit_order': list(events or [])}}
    return _finalize_response(material)

def _error_stage_status(stage: str, status: str, route: dict[str, Any]) -> dict[str, str]:
    intent_status = 'skipped' if int(route.get('intent_llm_calls') or 0) == 0 else 'ok'
    if stage in {'request_capsule', 'request_contract', 'route_contract', 'route_eligibility', 'candidate_selection', 'intent_routing', 'intent_llm', 'intent_decoding', 'intent_validation', 'plan_compilation', 'plan_validation', 'parameter_binding', 'metadata_resolution'}:
        intent_status = status if stage.startswith('intent') or stage in {'route_contract', 'route_eligibility', 'candidate_selection', 'request_capsule', 'request_contract'} else intent_status
        return {'overall': status, 'intent': intent_status, 'retrieval': 'not_called', 'analysis': 'not_called'}
    if stage in {'retrieval', 'source_merge', 'source_contract'}:
        return {'overall': status, 'intent': intent_status, 'retrieval': 'error', 'analysis': 'not_called'}
    return {'overall': status, 'intent': intent_status, 'retrieval': 'ok', 'analysis': 'error'}

def error_response(request: dict[str, Any], error: dict[str, Any], route_telemetry: dict[str, Any] | None=None) -> dict[str, Any]:
    route = deepcopy(route_telemetry or {})
    message = str(error.get('message') or '분석을 완료하지 못했습니다.')
    is_clarification = str(error.get('code') or '') == 'needs_clarification'
    status = 'needs_clarification' if is_clarification else 'error'
    options = (error.get('details') or {}).get('options') or [] if isinstance(error.get('details'), dict) else []
    trace_id = str(error.get('trace_id') or f"trace:{sha256_json([request.get('request_id'), error])[:24]}")
    normalized_error = None if is_clarification else {'contract_version': 'error.v1', **deepcopy(error), 'trace_id': trace_id}
    if normalized_error is not None:
        validate_contract(normalized_error, 'error.schema.json', stage='error_mapping')
    notices = [] if is_clarification else [{'code': str(error.get('code') or 'unknown'), 'message': message}]
    answer_sections = {'contract_version': 'answer.sections.v1', 'summary': {'headline': message, 'fact_ids': []}, 'result_table': {'row_source': 'data.rows', 'columns': [], 'row_count': 0, 'data_ref': ''}, 'applied_criteria': {}, 'evidence': {}, 'notices': notices, 'downloads': [], 'next_questions': []}
    validate_contract(answer_sections, 'answer-sections.schema.json', stage='answer_sections')
    usage = _usage(route)
    material = {'contract_version': 'response.v1', 'response_type': 'data_analysis', 'status': status, 'stage_status': _error_stage_status(str(error.get('stage') or 'runtime'), status, route), 'message': message, 'data_mode': 'dummy', 'analysis_mode': 'typed_ir', 'answer_sections': answer_sections, 'request': {'request_id': request.get('request_id'), 'question': request.get('question'), 'session_id': request.get('session_id'), 'reference_instant': request.get('reference_instant'), 'timezone': request.get('timezone')}, 'intent_plan': {}, 'analysis': {'status': status, 'error': normalized_error}, 'clarification': {'question': message, 'options': [str(item) for item in options[:20]]} if is_clarification else None, 'data': {'columns': [], 'rows': [], 'row_count': 0}, 'data_refs': [], 'state': None, 'trace': {'trace_id': trace_id, 'route': route, 'retrieval': [], 'usage': usage, 'commit_order': []}}
    return _finalize_response(material)

def _cell(value: Any) -> str:
    if value is None:
        return ''
    text = json.dumps(value, ensure_ascii=False, separators=(',', ':')) if isinstance(value, (dict, list)) else str(value)
    return text.replace('|', '\\|').replace('\n', ' ')[:160]

def _table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = '| ' + ' | '.join(columns) + ' |'
    rule = '| ' + ' | '.join(('---' for _ in columns)) + ' |'
    body = ['| ' + ' | '.join((_cell(row.get(column)) for column in columns)) + ' |' for row in rows]
    return '\n'.join([header, rule, *body])

def render_message(response: dict[str, Any], options: Any=None) -> str:
    if response.get('contract_version') == 'response.v1':
        validate_response_hash(response)
    display = normalize_display_options(options)
    sections = [f"### 응답\n{response.get('message', '')}".strip()]
    data = response.get('data') if isinstance(response.get('data'), dict) else {}
    rows = data.get('rows') if isinstance(data.get('rows'), list) else []
    columns = [str(item) for item in data.get('columns', [])]
    if display['show_result_table'] and columns:
        preview = rows[:int(display['table_preview_limit'])]
        sections.append('### 결과 테이블\n' + (_table(preview, columns) if preview else '표시할 결과 행이 없습니다.') + f"\n\n총 {int(data.get('row_count') or 0)}건입니다.")
    answer_sections = response.get('answer_sections') if isinstance(response.get('answer_sections'), dict) else {}
    if display['show_applied_criteria'] and answer_sections.get('applied_criteria'):
        sections.append('### 적용 기준\n```json\n' + json.dumps(answer_sections['applied_criteria'], ensure_ascii=False, indent=2) + '\n```')
    if display['show_analysis_evidence'] and answer_sections.get('evidence'):
        sections.append('### 분석 근거\n```json\n' + json.dumps(answer_sections['evidence'], ensure_ascii=False, indent=2) + '\n```')
    if display['show_download_links']:
        downloads = [item for item in answer_sections.get('downloads', []) if item.get('url')]
        if downloads:
            sections.append('### 다운로드\n' + '\n'.join((f"- [{item.get('label', '다운로드')}]({item['url']})" for item in downloads)))
    if display['show_notices'] and answer_sections.get('notices'):
        sections.append('### 알림\n' + '\n'.join((f"- {item.get('message', item)}" for item in answer_sections['notices'])))
    if display['show_next_questions'] and answer_sections.get('next_questions'):
        sections.append('### 후속 질문\n' + '\n'.join((f"- {item['text']}" for item in answer_sections['next_questions'][:3])))
    if display['show_intent_analysis']:
        sections.append('### 의도 분석\n```json\n' + json.dumps(response.get('intent_plan', {}).get('semantic_intent', {}), ensure_ascii=False, indent=2) + '\n```')
    if display['show_data_retrieval']:
        sections.append('### 조회 진단\n```json\n' + json.dumps(response.get('trace', {}).get('retrieval', []), ensure_ascii=False, indent=2) + '\n```')
    if display['show_execution_plan']:
        sections.append('### 실행 계획 진단\n```json\n' + json.dumps(response.get('analysis', {}).get('execution_ir', []), ensure_ascii=False, indent=2) + '\n```')
    return '\n\n'.join((section for section in sections if section))

def api_output(response: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(validate_response_hash(response))

def gaia_output(response: dict[str, Any]) -> dict[str, Any]:
    canonical = validate_response_hash(response)
    sections = canonical.get('answer_sections') if isinstance(canonical.get('answer_sections'), dict) else {}
    urls = [{'title': str(item.get('label') or '다운로드'), 'url': str(item.get('url') or '')} for item in sections.get('downloads', []) if item.get('url')]
    metadata = {'contract_version': 'gaia.metadata.v1', 'docs': [], 'images': [], 'knowhows': [], 'followup_questions': [deepcopy(item) for item in sections.get('next_questions', [])[:3]], 'urls': urls, 'trace_id': str(canonical.get('trace', {}).get('trace_id') or ''), 'usage': deepcopy(canonical.get('trace', {}).get('usage', {})), 'response_sha256': str(canonical.get('response_sha256') or '')}
    validate_contract(metadata, 'gaia-metadata.schema.json', stage='gaia_output')
    return {'answer': str(canonical.get('message') or ''), 'metadata': metadata}


EMBEDDED_SCHEMAS = json.loads('{"answer-facts.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/answer-facts.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"answer.facts.v1","type":"string"},"facts":{"items":{"additionalProperties":false,"properties":{"fact_id":{"minLength":1,"type":"string"},"type":{"minLength":1,"type":"string"},"value":{"$ref":"#/$defs/jsonValue"}},"required":["fact_id","type","value"],"type":"object"},"maxItems":512,"type":"array"},"facts_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"plan_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"question":{"type":"string"},"result_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"}},"required":["contract_version","question","facts","result_sha256","plan_id","facts_sha256"],"title":"answer.facts.v1","type":"object"}}')



from copy import deepcopy


PIPELINE_VERSION = "pipeline.context.v1"


def _payload(value):
    raw = getattr(value, "data", value)
    # Pipeline contexts are immutable-by-contract.  Copy only the top-level
    # envelope so large source/result row arrays stay shared between adjacent
    # nodes; components that intentionally mutate nested material must take an
    # explicit local deepcopy at that mutation boundary.
    return dict(raw) if isinstance(raw, dict) else {}


def _pipeline_error(current, exc, stage):
    context = _payload(current)
    request = context.get("request") if isinstance(context.get("request"), dict) else {}
    trace_id = str(context.get("trace_id") or "")
    if isinstance(exc, ContractError):
        error = exc.as_dict(trace_id)
    else:
        error = ContractError(
            "plan_contract_error",
            stage,
            "분석 파이프라인 계약 오류가 발생했습니다.",
            {"error_type": type(exc).__name__},
        ).as_dict(trace_id)
    context.update(
        {
            "contract_version": PIPELINE_VERSION,
            "ok": False,
            "stage": stage,
            "request": request,
            "error": error,
        }
    )
    return context


def _require_context(value, stage):
    context = _payload(value)
    if context.get("contract_version") != PIPELINE_VERSION:
        raise ContractError("plan_contract_error", stage, "pipeline.context.v1 입력이 필요합니다.")
    return context


def _registered_recipe_ops(value):
    result = []
    if isinstance(value, dict):
        if isinstance(value.get("op"), str):
            result.append(str(value["op"]))
        for child in value.values():
            result.extend(_registered_recipe_ops(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(_registered_recipe_ops(child))
    return result


def _planner_profile(catalog):
    if not isinstance(catalog, dict) or catalog.get("contract_version") != "metadata.runtime.catalog.v2":
        return "legacy_v1"
    allowed = {
        "filter", "project", "aggregate", "join", "derive", "compare_fields",
        "sort", "rank", "transform_previous_result", "registered_call",
    }
    recipe_values = list((catalog.get("recipes") or {}).values())
    operations = {op for value in recipe_values for op in _registered_recipe_ops(value)}
    has_legacy_marker = any("legacy_op" in json.dumps(value, ensure_ascii=False) for value in recipe_values)
    if operations <= allowed and not has_legacy_marker:
        return "generic_v2"
    profile = catalog.get("output_profile") if isinstance(catalog.get("output_profile"), dict) else {}
    if profile.get("planner_profile") == "legacy_v1_compat":
        expected = str(profile.get("legacy_catalog_sha256") or "")
        actual = str(EMBEDDED_RUNTIME_CATALOG.get("catalog_sha256") or "")
        identity_ok = str(catalog.get("domain_id") or "") == "manufacturing"
        compiler_ok = str(catalog.get("compiler_version") or "") in {
            "metadata-domain-compiler.v6.2", "metadata-domain-compiler.v6.3"
        }
        # metadata.runtime.catalog.v2 does not expose authoring provenance.  The
        # executable boundary is instead the validated package/bundle/catalog
        # hash chain plus this exact embedded-v1 pin, domain identity and
        # compiler allowlist.  Requiring a non-contract field here would make
        # every valid migrated manufacturing package impossible to execute.
        if expected and expected == actual and identity_ok and compiler_ok:
            return "legacy_v1_compat"
    raise ContractError(
        "unsupported_operation",
        "planner_profile",
        "The active domain requires typed operators that are not supported by the generic v2 planner.",
        {"registered_operations": sorted(operations), "profile": profile.get("planner_profile")},
    )



import json

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, Output
from lfx.schema.data import Data
from lfx.schema.message import Message


class AnswerFactsContextBuilder(Component):
    display_name = "답변 사실 및 프롬프트 컨텍스트"
    description = "실행 결과에서 검증 가능한 사실을 만들고, 선택적 답변 LLM에 전달할 제한된 컨텍스트와 도메인 특화 문구를 분리해 제공합니다."
    icon = "text-quote"
    metadata = {"logical_stage": "answer_facts_context", "logical_capabilities": ["answer_facts", "prompt_context"]}
    inputs = [
        DataInput(name="result_context", display_name="실행 결과 컨텍스트", required=True, info="Typed IR 실행 결과와 질문·계획·출처 정보가 결합된 검증 완료 컨텍스트입니다."),
        BoolInput(name="narrative_enabled", display_name="LLM 답변 문장 사용", value=False, info="활성화하면 결정론적 사실만 전달해 선택적으로 자연어 답변 문장을 생성합니다."),
    ]
    outputs = [
        Output(name="answer_facts_context", display_name="답변 사실 컨텍스트", method="build_facts_context", types=["Data"]),
        Output(name="answer_prompt_context", display_name="답변 LLM 실행 컨텍스트", method="build_prompt_context", types=["Data"]),
        Output(name="answer_specialized_prompt_text", display_name="답변 특화 프롬프트 원문", method="build_specialized_text", types=["Message"]),
    ]

    def _current_and_facts(self):
        current = _require_context(getattr(self, "result_context", None), "answer_facts_context")
        if not current.get("ok"):
            return current, None
        facts = build_answer_facts(current["request"], current["plan"], current["result"])
        return current, facts

    def build_facts_context(self) -> Data:
        current = _payload(getattr(self, "result_context", None))
        try:
            current, facts = self._current_and_facts()
            if not current.get("ok"):
                return Data(data=current)
            requested = bool(getattr(self, "narrative_enabled", False))
            current.update(
                {
                    "stage": "answer_facts_context",
                    "answer_facts": facts,
                    "narrative": {
                        "requested": requested,
                        "attempted": False,
                        "llm_calls": 0,
                        "claim_status": "pending" if requested else "deterministic",
                        "message": "",
                    },
                }
            )
        except Exception as exc:
            current = _pipeline_error(current, exc, "answer_facts_context")
        return Data(data=current)

    def build_prompt_context(self) -> Data:
        try:
            current, facts = self._current_and_facts()
            variables = (
                {"answer_facts": facts}
                if current.get("ok")
                else {"upstream_error_code": str((current.get("error") or {}).get("code") or "pipeline_error")}
            )
            encoded = json.dumps(variables, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            if len(encoded) > 12 * 1024:
                raise ContractError("metadata_budget_exceeded", "answer_prompt_context", "답변 LLM 컨텍스트가 12KB를 초과했습니다.")
            return Data(
                data={
                    "contract_version": "prompt.runtime-context.v1",
                    "purpose": "answer_narrative",
                    "invoke": bool(current.get("ok")) and bool(getattr(self, "narrative_enabled", False)),
                    "variables": variables,
                }
            )
        except Exception as exc:
            return Data(data=_pipeline_error({}, exc, "answer_prompt_context"))

    def build_specialized_text(self) -> Message:
        try:
            current, _ = self._current_and_facts()
            text = str(((current.get("domain_prompt_extensions") or {}).get("answer") or "")) if current.get("ok") else ""
            text = text.encode("utf-8")[:8192].decode("utf-8", errors="ignore")
            return Message(text=text)
        except Exception:
            return Message(text="")
