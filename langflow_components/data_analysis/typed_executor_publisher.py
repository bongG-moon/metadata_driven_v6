# -*- coding: utf-8 -*-
"""GENERATED standalone component: TypedExecutorPublisher.

Regenerate with tools/build_standalone_components.py.  Do not hand edit.
"""
from __future__ import annotations

import json

EMBEDDED_SOURCE_MANIFEST = json.loads('{"catalog_contract_version":"metadata.runtime.catalog.v1","catalog_declared_sha256":"6d2c9eaf3a10be1023a5c7aa52c796d5f0caf7287237a488ce38e68840b0e16f","catalog_file_sha256":"c55906d46a8050ee262f970c9c831fc362c48c1bf3b9a184651ceee27a1c9c9d","contract_version":"standalone.source.manifest.v1","reference_sources":{"contracts/schemas/active-domain-pointer.schema.json":"8ff3e114e106d0bc08c83e61947ac967c28cd5390cd0539cb1efdc64b82f9a61","contracts/schemas/analysis-plan.schema.json":"15dbb187f458d03ad4d55063eef898b862529dc68e9f64840d08ab20df9cfb76","contracts/schemas/analysis-result.schema.json":"06e92c0892ff5b209783332f33e4d4ed1855612470b088390e4501591f68065b","contracts/schemas/analysis-route.schema.json":"aadd7504e7f75329b8b6a50634261e073450e6d19d8e14d4a44196c0000e0c04","contracts/schemas/answer-facts.schema.json":"26c573be25f4fade355a37f2ab231f3e0aa8ac83445ee58020a99388648809ed","contracts/schemas/answer-sections.schema.json":"4c1d645c9927879e6a9e877def326ff045b5a01edaf48a566b935bc4734882ab","contracts/schemas/approval-event.schema.json":"4aa6b10eeb875538d00d6de564bdbe24eb093e8727ed57515cbadba63f13d7a9","contracts/schemas/config-registry.schema.json":"2f90dfb2b99e17faa9afecaf1f32295f6d713067aeca66c7dc1544c5713598e9","contracts/schemas/display-options.schema.json":"27bcc5558f8357d2a47d96cd3cdc48535da3643164fd6a539df878301dea08d9","contracts/schemas/domain-package.schema.json":"f39f433985180636bb3b6dfe054cfb8e63998acbe0112f7082a8233b619517f7","contracts/schemas/download-item.schema.json":"91efd43bf2db00bf5e85071fa2992679c3b2dc050251a5c82e839dcd7f5d4086","contracts/schemas/error-registry.schema.json":"f67a1ab5ef2568626d406cb9feb38acfbb6fc593fa04f3da063f8293da653b64","contracts/schemas/error.schema.json":"1a0c89cc1898a894b0490a59f286c68520c0f74be0811f6c06c4aa3e50fe5602","contracts/schemas/evidence-manifest.schema.json":"2805ed7cce742e96b5e10902b096fbec91e40a8aca7fde7bfe95c1d12a9668bb","contracts/schemas/executable-blueprint.schema.json":"e55dbe8faa2f1f2eb933b1548b2b1c37886a0911ceb4e70838427bac2327f14a","contracts/schemas/executed-result.schema.json":"eaba5818e5fb30e2a572f5a81488d9ba34032adcf3af55dfbb0d4287afc7e435","contracts/schemas/flow-inventory.schema.json":"cdce69d64a9df37a88e139a0fd0900d38d9475d2a8f13ff9a9b5c1bf0777b672","contracts/schemas/gaia-metadata.schema.json":"86d0a11a06a97d573b550a427d26abe9db6e897d3c46681f02e2427735e9f093","contracts/schemas/metadata-annotation-proposal.schema.json":"f0b227cc42a528d6e0b95f1c8c4a1bf6bbb6871d17d32c108d65b47d2b0ddc7f","contracts/schemas/metadata-authoring-draft.schema.json":"93b424e2d17205074ab833bed6e0463492c50fc918162ebdaa544561679e027c","contracts/schemas/metadata-authoring-proposal.schema.json":"8ee3fc86d8f596c554443c16ad619822e63315ed8f2bfd06311987fc63322edd","contracts/schemas/metadata-authoring-response.schema.json":"da776b8a156d007c5bd95e86ad10cfb5a8ac7f06c2cae0c52aeb96b6a36415f6","contracts/schemas/metadata-bootstrap-dataset-ir.schema.json":"351260f7ed418b35f4ca1e5012a353b1d8f820ea21dfc8880483c193880af3b6","contracts/schemas/metadata-bootstrap-main-filter-ir.schema.json":"41c849c88b803d53af9c02c3d50127c47e8ee38e46d7b0a1ad0d09c3638e48fa","contracts/schemas/metadata-bundle.schema.json":"985ffe44974cf14d6c52a8188d54c3b209c00478e83888f00c359cd056d5dc81","contracts/schemas/metadata-envelope.schema.json":"9abca177e22b570f2158dace05256f671c0acbd054705dfe4f34611fbdae2048","contracts/schemas/model-profile.schema.json":"14345c16f629fc03a3de2cdd2fe469bef1fdc82cd2f93954ce1f4204ba82f356","contracts/schemas/operator-registry.schema.json":"acd003c6db66b470a2653fc8a97caaf3856c9d4cfd934bc0f27ef609787c2746","contracts/schemas/pending-metadata-write.schema.json":"af7a0593fafbdcea16f1212ba92484525626e43f2a25d91f9c310a80f5b37a4d","contracts/schemas/query-registry.schema.json":"8422a44035eb2a06381166d69a185036c698f581b17741a8c4686fbeea109040","contracts/schemas/registered-call.schema.json":"219a775c3a514501c66e077ef03a107a71f4d45af15aab2117c3cb1ab8f75811","contracts/schemas/registered-function-card.schema.json":"bc9ca8b01c90d2d11737f1a70586e9227510b67fdab26c8ae605d9e830170dfd","contracts/schemas/request-capsule.schema.json":"675e661653098288d6cc9e6e9b3599ed3bf3e05d6d592ac66d9ed46b9fd2afaf","contracts/schemas/resolved-candidate-bundle.schema.json":"a24b7d2fc3798f1dd69e1af94a7071eae8fb56d93a4191258953fd63b4211568","contracts/schemas/response.schema.json":"40c1e43f2228c04bb9ea652f1107a7ac202405c3321bc2c6af8dbc543b2e7b06","contracts/schemas/retrieval-job-bundle.schema.json":"e73cd6e6c50bb24b528111c36c410af3afe2fe3ff28d3d906cfe023263a12105","contracts/schemas/runtime-catalog-v2.schema.json":"3f7f6c5154c9e7922dd65490e9166ba0038c6a242258ec30d409d8a553948fed","contracts/schemas/semantic-intent-selection.schema.json":"a70c99e36060531fac9730c02f706ffa8d108b872c5abe0e2d05cafa459e6a75","contracts/schemas/semantic-intent.schema.json":"a743b7e26168dda04a7f46205fed67987a587cf3cce939cf57b228b099bfad53","contracts/schemas/source-bundle.schema.json":"a5330ef1b104df5dd0f19385b5e7994ee5469feffa110ee84087b7992258ea92","contracts/schemas/source-result.schema.json":"f342dcf0f948f7f99899335d83f302f2aaa38b05bb246eb06f9c1da0161f516c","contracts/schemas/trace.schema.json":"3f7cb2dd4e88b5f9f09695347ce42d8b98d5c4534d8fab41cca8ea1c9e3d484e","contracts/schemas/turn-state.schema.json":"688ad4f5ac1b133e60e3a2ef2bef56d0b18c87a41d2c6c236264285aeba32280","contracts/schemas/unsupported-telemetry.schema.json":"8c3675797be935d6fd52db2883d433d464df2fdecc5e0d52e795a5fa1e6c8439","contracts/schemas/validation-case.schema.json":"23304f969ca614324f7a74b52edc72c4e6753e76c476a77fc8db68f089941682","reference_runtime/authoring_blueprint.py":"9fc416a04e0da317586ad8abf9831bf650746a7f1907ad62fcaef4012327fe71","reference_runtime/authoring_source_manifest.py":"311bd68482e163a781bf11aa449587879f659fa9c36f7564129ecea44b88170c","reference_runtime/canonical.py":"338b8b013b9311f94d9b5ff7a3d5902576e9dfb88b40d72d37436025806c2d1d","reference_runtime/contracts.py":"5d16082db0bf437e537a24352834548e48e157a4c740659e9c9f1a0e46960d6e","reference_runtime/domain_authoring_patches.py":"4c78c72bc2412cbe78e74372b7c5af658ada8de1b8058b228f02d2b68b41c445","reference_runtime/domain_packages.py":"801b2c66191c65fb2d961d40e6e10db50a5d4ffc7be225b1d37a9fc2b4b9f43c","reference_runtime/dummy_data.py":"c02824f9ddba81496d99a4b58bda8e6bedf0ce464d47abca682071ab24cae57d","reference_runtime/engine.py":"62df5f1a06c0a2765085826bec3e73f99f02da470850d180f2d7a53078c67606","reference_runtime/generic_v2_candidates.py":"95f5821b05d7d70f70ebd0339a316bcc1367b5499553319b8d8995df251a4c56","reference_runtime/generic_v2_planner.py":"142665c8050c9302830cedf45928a25b73cd34e80bec66de9ba77003209176d3","reference_runtime/metadata_collections.py":"389341ea84e365e0c8aaddb3d572ddaf3b5af1995756ab8c9fea8eec616c4346","reference_runtime/metadata_compiler.py":"99544e6094883b4241d010af2bec5d67e6205d34634ad46d6e2ee173107336e3","reference_runtime/plan_compiler.py":"6dc3bef703732a6cba6734f63970b22ecd599139067fa78a16bf5b3be003e735","reference_runtime/presenter.py":"7f5d4457d363909c2026cc3b25a2def4a9c9b3db0d52c1996f2a39bb726894ce","reference_runtime/registered_functions.py":"03f2ed1e2cb158eee5dd23cd99a408f14fdf3abea7fb630cfb31044cfe8f4d8e","reference_runtime/request_literals.py":"00493f9e342ab3065215805ae32f3068cb594209434bf280f2bb4f23c4be62ff","reference_runtime/source_contracts.py":"c43d8865ff045f4c26c5194262620a50961be5b56552c5cc6e7d580b2c11d7b0","reference_runtime/state_contracts.py":"5a03fff6684850361904add4e4d15ea578617d1fce20564119bbac175fb334ae","reference_runtime/typed_executor.py":"0c1fc3bbb055cd32d1da3446afab0aca5351e844536624ae9ab953c78c5dfe3b"}}')


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


import time
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from jsonschema import Draft202012Validator
REGISTERED_CALL_VERSION = 'registered_call.v1'
FAILURE_POLICY = 'fail_closed'
_v6rf_CARD_KEYS = {'function_id', 'version', 'execution_mode', 'implementation_sha256', 'input_schema', 'output_schema', 'required_fields', 'limits', 'failure_policy', 'aliases', 'call_template'}
_v6rf_LIMIT_KEYS = {'timeout_ms', 'max_input_rows', 'max_output_rows', 'max_output_bytes'}
_v6rf_CALL_KEYS = {'contract_version', 'id', 'op', 'input', 'function_ref', 'required_fields', 'arguments', 'limits', 'failure_policy'}
_v6rf_FUNCTION_REF_KEYS = {'function_id', 'version', 'implementation_sha256', 'input_schema_sha256', 'output_schema_sha256'}
_v6rf_CALL_TEMPLATE_KEYS = {'dataset_ref', 'field_ref', 'parameters', 'output_fields'}
_v6rf_ARGUMENT_KEYS = {'field_ref', 'tokens', 'operator', 'match_mode', 'case_sensitive'}
_v6rf_TRIM_AND_MATCH_INPUT_SCHEMA: dict[str, Any] = {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'type': 'object', 'additionalProperties': False, 'required': ['values', 'tokens', 'operator', 'match_mode', 'case_sensitive'], 'properties': {'values': {'type': 'array', 'maxItems': 100000, 'items': {'type': ['string', 'null']}}, 'tokens': {'type': 'array', 'minItems': 1, 'maxItems': 64, 'uniqueItems': True, 'items': {'type': 'string', 'minLength': 1, 'maxLength': 256}}, 'operator': {'enum': ['equals', 'contains', 'starts_with', 'ends_with']}, 'match_mode': {'enum': ['any', 'all']}, 'case_sensitive': {'type': 'boolean'}}}
_v6rf_TRIM_AND_MATCH_OUTPUT_SCHEMA: dict[str, Any] = {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'type': 'object', 'additionalProperties': False, 'required': ['selected_indices'], 'properties': {'selected_indices': {'type': 'array', 'maxItems': 100000, 'uniqueItems': True, 'items': {'type': 'integer', 'minimum': 0}}}}

def _v6rf_implementation_pin(function_id: str, version: int, behavior_revision: str, input_schema: Mapping[str, Any], output_schema: Mapping[str, Any]) -> str:
    """Hash the reviewed behavior contract used by the local allowlist."""
    return sha256_json({'function_id': function_id, 'version': version, 'behavior_revision': behavior_revision, 'input_schema': input_schema, 'output_schema': output_schema, 'effect': 'select_rows_by_index'})

def _v6rf_trim_and_match_tokens(payload: Mapping[str, Any], deadline: float) -> dict[str, Any]:
    values = list(payload['values'])
    tokens = [str(value).strip() for value in payload['tokens']]
    if any((not token for token in tokens)):
        _v6rf_contract_error('registered function tokens must remain non-empty after trimming.')
    case_sensitive = bool(payload['case_sensitive'])
    if not case_sensitive:
        tokens = [token.casefold() for token in tokens]
    operator = str(payload['operator'])
    match_mode = str(payload['match_mode'])

    def matches(value: Any, token: str) -> bool:
        normalized = str(value).strip()
        if not case_sensitive:
            normalized = normalized.casefold()
        if operator == 'equals':
            return normalized == token
        if operator == 'contains':
            return token in normalized
        if operator == 'starts_with':
            return normalized.startswith(token)
        if operator == 'ends_with':
            return normalized.endswith(token)
        raise AssertionError(operator)
    selected: list[int] = []
    for index, value in enumerate(values):
        if index % 128 == 0 and time.monotonic() > deadline:
            _v6rf_limit_error('registered function exceeded its timeout.', {'timeout': True})
        if value is None:
            continue
        decisions = [matches(value, token) for token in tokens]
        if all(decisions) if match_mode == 'all' else any(decisions):
            selected.append(index)
    if time.monotonic() > deadline:
        _v6rf_limit_error('registered function exceeded its timeout.', {'timeout': True})
    return {'selected_indices': selected}

@dataclass(frozen=True, slots=True)
class _v6rf_Registration:
    function_id: str
    version: int
    implementation_sha256: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    limit_ceiling: dict[str, int]
    handler: Callable[[Mapping[str, Any], float], dict[str, Any]]
_v6rf_TRIM_AND_MATCH_ID = 'core.trim_and_match_tokens'
_v6rf_TRIM_AND_MATCH_VERSION = 1
_v6rf_TRIM_AND_MATCH_SHA256 = _v6rf_implementation_pin(_v6rf_TRIM_AND_MATCH_ID, _v6rf_TRIM_AND_MATCH_VERSION, 'trim-strip-casefold-match.v1', _v6rf_TRIM_AND_MATCH_INPUT_SCHEMA, _v6rf_TRIM_AND_MATCH_OUTPUT_SCHEMA)
_v6rf_REGISTRY: dict[tuple[str, int], _v6rf_Registration] = {(_v6rf_TRIM_AND_MATCH_ID, _v6rf_TRIM_AND_MATCH_VERSION): _v6rf_Registration(function_id=_v6rf_TRIM_AND_MATCH_ID, version=_v6rf_TRIM_AND_MATCH_VERSION, implementation_sha256=_v6rf_TRIM_AND_MATCH_SHA256, input_schema=_v6rf_TRIM_AND_MATCH_INPUT_SCHEMA, output_schema=_v6rf_TRIM_AND_MATCH_OUTPUT_SCHEMA, limit_ceiling={'timeout_ms': 5000, 'max_input_rows': 100000, 'max_output_rows': 100000, 'max_output_bytes': 8 * 1024 * 1024}, handler=_v6rf_trim_and_match_tokens)}

def registered_function_descriptor(function_id: str, version: int) -> dict[str, Any]:
    """Return public immutable metadata for one locally allowed implementation."""
    registration = _v6rf_registration(function_id, version)
    return {'function_id': registration.function_id, 'version': registration.version, 'implementation_sha256': registration.implementation_sha256, 'input_schema': deepcopy(registration.input_schema), 'output_schema': deepcopy(registration.output_schema), 'limit_ceiling': deepcopy(registration.limit_ceiling)}

def validate_registered_function_card(card: Mapping[str, Any]) -> dict[str, Any]:
    """Bind a closed catalog card to exactly one local implementation."""
    if not isinstance(card, Mapping) or set(card) != _v6rf_CARD_KEYS:
        _v6rf_contract_error('registered function card does not match the closed contract.', {'actual_keys': sorted(card) if isinstance(card, Mapping) else []})
    function_id = str(card.get('function_id') or '')
    version = _v6rf_positive_int(card.get('version'), 'version')
    registration = _v6rf_registration(function_id, version)
    if card.get('execution_mode') != 'registered_standalone':
        _v6rf_contract_error('registered function execution mode is not allowed.')
    if str(card.get('implementation_sha256') or '') != registration.implementation_sha256:
        _v6rf_unsupported('registered function implementation hash does not match the local allowlist.', {'function_id': function_id, 'version': version})
    if card.get('input_schema') != registration.input_schema or card.get('output_schema') != registration.output_schema:
        _v6rf_contract_error('registered function schemas do not match the local implementation contract.', {'function_id': function_id, 'version': version})
    required_fields = card.get('required_fields')
    if not isinstance(required_fields, list) or not required_fields or len(required_fields) > 16 or (len(required_fields) != len(set(map(str, required_fields)))) or any((not isinstance(field, str) or not field for field in required_fields)):
        _v6rf_contract_error('registered function required_fields are invalid.')
    limits = _v6rf_validate_limits(card.get('limits'), registration.limit_ceiling)
    if card.get('failure_policy') != FAILURE_POLICY:
        _v6rf_contract_error('registered functions currently require fail_closed policy.')
    aliases = card.get('aliases')
    if not isinstance(aliases, list) or not aliases or len(aliases) > 32 or (len(aliases) != len(set(map(str, aliases)))) or any((not isinstance(alias, str) or not alias.strip() for alias in aliases)):
        _v6rf_contract_error('registered function aliases are invalid.')
    call_template = card.get('call_template')
    if not isinstance(call_template, Mapping) or set(call_template) != _v6rf_CALL_TEMPLATE_KEYS:
        _v6rf_contract_error('registered function call_template does not match the closed contract.')
    field_ref = str(call_template.get('field_ref') or '')
    if not isinstance(call_template.get('dataset_ref'), str) or not call_template.get('dataset_ref'):
        _v6rf_contract_error('registered function dataset_ref is required.')
    if field_ref not in set(required_fields):
        _v6rf_contract_error('registered function field_ref is absent from required_fields.')
    parameters = call_template.get('parameters')
    arguments = {'field_ref': field_ref, **dict(parameters or {})}
    _v6rf_validate_arguments(arguments)
    output_fields = call_template.get('output_fields')
    if not isinstance(output_fields, list) or not output_fields or len(output_fields) > 128 or (len(output_fields) != len(set(map(str, output_fields)))) or any((not isinstance(field, str) or not field for field in output_fields)):
        _v6rf_contract_error('registered function output_fields are invalid.')
    normalized = deepcopy(dict(card))
    normalized['version'] = version
    normalized['limits'] = limits
    return normalized

def build_registered_call_operation(card: Mapping[str, Any], *, operation_id: str, input_ref: str) -> dict[str, Any]:
    """Compile one validated card into the closed ``registered_call.v1`` IR."""
    normalized = validate_registered_function_card(card)
    descriptor = registered_function_descriptor(str(normalized['function_id']), int(normalized['version']))
    template = dict(normalized['call_template'])
    arguments = {'field_ref': str(template['field_ref']), **deepcopy(dict(template['parameters']))}
    operation = {'contract_version': REGISTERED_CALL_VERSION, 'id': str(operation_id), 'op': 'registered_call', 'input': str(input_ref), 'function_ref': {'function_id': descriptor['function_id'], 'version': descriptor['version'], 'implementation_sha256': descriptor['implementation_sha256'], 'input_schema_sha256': sha256_json(descriptor['input_schema']), 'output_schema_sha256': sha256_json(descriptor['output_schema'])}, 'required_fields': list(normalized['required_fields']), 'arguments': arguments, 'limits': deepcopy(normalized['limits']), 'failure_policy': FAILURE_POLICY}
    return validate_registered_call_operation(operation, catalog_card=normalized)

def validate_registered_call_operation(operation: Mapping[str, Any], *, catalog_card: Mapping[str, Any] | None=None) -> dict[str, Any]:
    """Validate operation shape, implementation pin, schemas, and limits."""
    if not isinstance(operation, Mapping) or set(operation) != _v6rf_CALL_KEYS:
        _v6rf_contract_error('registered call operation does not match the closed contract.', {'actual_keys': sorted(operation) if isinstance(operation, Mapping) else []})
    if operation.get('contract_version') != REGISTERED_CALL_VERSION or operation.get('op') != 'registered_call':
        _v6rf_contract_error('registered call discriminator is invalid.')
    if not str(operation.get('id') or '') or not str(operation.get('input') or ''):
        _v6rf_contract_error('registered call identity and input are required.')
    function_ref = operation.get('function_ref')
    if not isinstance(function_ref, Mapping) or set(function_ref) != _v6rf_FUNCTION_REF_KEYS:
        _v6rf_contract_error('registered call function_ref does not match the closed contract.')
    function_id = str(function_ref.get('function_id') or '')
    version = _v6rf_positive_int(function_ref.get('version'), 'function_ref.version')
    registration = _v6rf_registration(function_id, version)
    expected_ref = {'function_id': function_id, 'version': version, 'implementation_sha256': registration.implementation_sha256, 'input_schema_sha256': sha256_json(registration.input_schema), 'output_schema_sha256': sha256_json(registration.output_schema)}
    if dict(function_ref) != expected_ref:
        _v6rf_unsupported('registered call function pin does not match the local allowlist.', {'function_id': function_id, 'version': version})
    required_fields = operation.get('required_fields')
    if not isinstance(required_fields, list) or not required_fields or len(required_fields) != len(set(map(str, required_fields))) or any((not isinstance(field, str) or not field for field in required_fields)):
        _v6rf_contract_error('registered call required_fields are invalid.')
    arguments = operation.get('arguments')
    _v6rf_validate_arguments(arguments)
    if str(arguments['field_ref']) not in set(required_fields):
        _v6rf_contract_error('registered call field_ref is absent from required_fields.')
    limits = _v6rf_validate_limits(operation.get('limits'), registration.limit_ceiling)
    if operation.get('failure_policy') != FAILURE_POLICY:
        _v6rf_contract_error('registered call failure policy must be fail_closed.')
    if catalog_card is not None:
        card = validate_registered_function_card(catalog_card)
        if str(card['function_id']) != function_id or int(card['version']) != version or str(card['implementation_sha256']) != registration.implementation_sha256 or (list(card['required_fields']) != list(required_fields)) or (dict(card['limits']) != limits) or ({'field_ref': card['call_template']['field_ref'], **dict(card['call_template']['parameters'])} != dict(arguments)):
            _v6rf_contract_error('registered call differs from its catalog card.')
    return deepcopy(dict(operation))

def dispatch_registered_call(operation: Mapping[str, Any], rows: list[dict[str, Any]]) -> list[int]:
    """Run one validated local implementation and return selected row indices."""
    normalized = validate_registered_call_operation(operation)
    limits = dict(normalized['limits'])
    if len(rows) > int(limits['max_input_rows']):
        _v6rf_limit_error('registered function input row limit was exceeded.', {'actual_rows': len(rows), 'max_input_rows': limits['max_input_rows']})
    field_ref = str(normalized['arguments']['field_ref'])
    missing = [index for index, row in enumerate(rows) if field_ref not in row]
    if missing:
        raise ContractError('source_schema_mismatch', 'registered_function_dispatch', 'registered function required field is missing.', {'field': field_ref, 'first_missing_row': missing[0]})
    payload = {'values': [json_value(row[field_ref]) for row in rows], 'tokens': deepcopy(normalized['arguments']['tokens']), 'operator': normalized['arguments']['operator'], 'match_mode': normalized['arguments']['match_mode'], 'case_sensitive': normalized['arguments']['case_sensitive']}
    function_ref = normalized['function_ref']
    registration = _v6rf_registration(str(function_ref['function_id']), int(function_ref['version']))
    _v6rf_validate_payload(registration.input_schema, payload, 'input')
    deadline = time.monotonic() + int(limits['timeout_ms']) / 1000.0
    result = registration.handler(payload, deadline)
    if time.monotonic() > deadline:
        _v6rf_limit_error('registered function exceeded its timeout.', {'timeout': True})
    _v6rf_validate_payload(registration.output_schema, result, 'output')
    if byte_size(result) > int(limits['max_output_bytes']):
        _v6rf_limit_error('registered function output byte limit was exceeded.', {'max_output_bytes': limits['max_output_bytes']})
    selected = list(result['selected_indices'])
    if len(selected) > int(limits['max_output_rows']):
        _v6rf_limit_error('registered function output row limit was exceeded.', {'actual_rows': len(selected), 'max_output_rows': limits['max_output_rows']})
    if selected != sorted(selected) or any((index >= len(rows) for index in selected)):
        _v6rf_contract_error('registered function returned invalid row indices.')
    return selected

def _v6rf_registration(function_id: str, version: int) -> _v6rf_Registration:
    registration = _v6rf_REGISTRY.get((str(function_id), int(version)))
    if registration is None:
        _v6rf_unsupported('registered function identity is absent from the local allowlist.', {'function_id': str(function_id), 'version': int(version)})
    return registration

def _v6rf_validate_arguments(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _v6rf_ARGUMENT_KEYS:
        _v6rf_contract_error('registered function arguments do not match the closed contract.', {'actual_keys': sorted(value) if isinstance(value, Mapping) else []})
    if not isinstance(value.get('field_ref'), str) or not value.get('field_ref'):
        _v6rf_contract_error('registered function field_ref is required.')
    tokens = value.get('tokens')
    if not isinstance(tokens, list) or not 1 <= len(tokens) <= 64 or len(tokens) != len(set(map(str, tokens))) or any((not isinstance(token, str) or not token.strip() or len(token) > 256 for token in tokens)):
        _v6rf_contract_error('registered function tokens are invalid.')
    if value.get('operator') not in {'equals', 'contains', 'starts_with', 'ends_with'}:
        _v6rf_contract_error('registered function operator is invalid.')
    if value.get('match_mode') not in {'any', 'all'}:
        _v6rf_contract_error('registered function match_mode is invalid.')
    if not isinstance(value.get('case_sensitive'), bool):
        _v6rf_contract_error('registered function case_sensitive must be boolean.')
    return deepcopy(dict(value))

def _v6rf_validate_limits(value: Any, ceiling: Mapping[str, int]) -> dict[str, int]:
    if not isinstance(value, Mapping) or set(value) != _v6rf_LIMIT_KEYS:
        _v6rf_contract_error('registered function limits do not match the closed contract.')
    result: dict[str, int] = {}
    for key in sorted(_v6rf_LIMIT_KEYS):
        number = _v6rf_positive_int(value.get(key), f'limits.{key}')
        if number > int(ceiling[key]):
            _v6rf_contract_error('registered function limit exceeds the local ceiling.', {'limit': key, 'value': number, 'ceiling': int(ceiling[key])})
        result[key] = number
    return result

def _v6rf_validate_payload(schema: Mapping[str, Any], value: Any, direction: str) -> None:
    errors = sorted(Draft202012Validator(dict(schema)).iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        path = '.'.join(map(str, first.absolute_path)) or '$'
        _v6rf_contract_error(f'registered function {direction} schema validation failed.', {'path': path, 'reason': first.message[:300]})

def _v6rf_positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _v6rf_contract_error(f'{label} must be a positive integer.')
    return int(value)

def _v6rf_contract_error(message: str, details: dict[str, Any] | None=None) -> None:
    raise ContractError('plan_contract_error', 'registered_function_contract', message, details or {})

def _v6rf_unsupported(message: str, details: dict[str, Any] | None=None) -> None:
    raise ContractError('unsupported_operation', 'registered_function_allowlist', message, details or {})

def _v6rf_limit_error(message: str, details: dict[str, Any] | None=None) -> None:
    raise ContractError('execution_memory_limit_exceeded', 'registered_function_dispatch', message, details or {})
__all__ = ['FAILURE_POLICY', 'REGISTERED_CALL_VERSION', 'build_registered_call_operation', 'dispatch_registered_call', 'registered_function_descriptor', 'validate_registered_call_operation', 'validate_registered_function_card']


import math
from dataclasses import dataclass
from typing import Any, Iterable
import pandas as pd
FILTER_ALIASES = {'ge': 'gte', 'le': 'lte', 'like': 'contains'}
FILTER_OPERATORS = {'eq', 'in', 'ne', 'not_in', 'gt', 'gte', 'lt', 'lte', 'between', 'contains', 'starts_with', 'ends_with', 'is_null', 'is_not_null', 'is_blank', 'is_not_blank', 'null_or_blank'}
AGGREGATIONS = {'sum', 'mean', 'min', 'max', 'count', 'nunique', 'median', 'std', 'var', 'list_unique'}
JOIN_TYPES = {'inner', 'left', 'right', 'outer', 'semi', 'anti'}
COMPARE_OPERATORS = {'eq', 'ne', 'gt', 'gte', 'lt', 'lte'}

def validate_plan_integrity(plan: dict[str, Any]) -> dict[str, Any]:
    """Reject mutation of a sealed plan before any frame is touched.

    Small unit-test plans without ``analysis.plan.v1`` remain supported.  Every
    production plan carrying that version must have both identities recomputed
    from its complete executable material.
    """
    if not isinstance(plan, dict):
        raise ContractError('plan_contract_error', 'execution', 'Plan payload must be an object.')
    if plan.get('contract_version') != 'analysis.plan.v1':
        return plan
    material = {key: value for key, value in plan.items() if key not in {'plan_id', 'plan_fingerprint'}}
    jobs = material.get('retrieval_jobs') if isinstance(material.get('retrieval_jobs'), list) else []
    material = {**material, 'retrieval_jobs': sorted(jobs, key=lambda item: str(item.get('job_id') or ''))}
    expected_id = f'plan:{sha256_json(material)}'
    semantic = {key: material[key] for key in ('catalog_sha256', 'input_refs', 'retrieval_jobs', 'operations', 'result_operation_id', 'result_contract', 'lineage') if key in material}
    if plan.get('plan_id') != expected_id or plan.get('plan_fingerprint') != sha256_json(semantic):
        raise ContractError('plan_contract_error', 'execution', 'Plan identity or semantic fingerprint does not match executable material.')
    return plan

def _frame(value: Any) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value.copy(deep=False)
    if isinstance(value, list):
        return pd.DataFrame(value)
    if isinstance(value, dict) and isinstance(value.get('rows'), list):
        columns = [str(item) for item in value.get('columns', [])] if isinstance(value.get('columns'), list) else None
        return pd.DataFrame(value['rows'], columns=columns or None)
    raise ContractError('plan_contract_error', 'execution', '실행 입력 테이블이 올바르지 않습니다.')

def _require_columns(frame: pd.DataFrame, fields: Iterable[str], operation_id: str) -> None:
    required = [str(field) for field in fields]
    missing = [field for field in required if field not in frame.columns]
    if missing:
        raise ContractError('source_schema_mismatch', 'execution', '실행에 필요한 canonical field가 없습니다.', {'operation_id': operation_id, 'missing_fields': missing})

def _is_blank(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype('string').fillna('').str.strip().eq('')

def _typed_series(series: pd.Series, semantic_type: str | None) -> pd.Series:
    kind = str(semantic_type or '').lower()
    if kind in {'number', 'quantity', 'integer', 'float', 'rate', 'duration', 'currency', 'percent', 'percentage', 'ratio', 'decimal'}:
        return pd.to_numeric(series, errors='coerce')
    if kind in {'date', 'datetime', 'timestamp'}:
        return pd.to_datetime(series, errors='coerce', utc=False)
    if kind in {'string', 'identifier', 'category', ''}:
        return series.astype('string')
    return series

def _filter_mask(frame: pd.DataFrame, tree: dict[str, Any], depth: int=0) -> pd.Series:
    if depth > 3:
        raise ContractError('plan_contract_error', 'execution', 'filter tree 깊이가 허용 범위를 초과했습니다.')
    connective = str(tree.get('op') or '').lower()
    if connective in {'all', 'any'}:
        clauses = tree.get('clauses')
        if not isinstance(clauses, list) or not clauses or len(clauses) > 32:
            raise ContractError('plan_contract_error', 'execution', 'filter clause 개수가 올바르지 않습니다.')
        masks = [_filter_mask(frame, clause, depth + 1) for clause in clauses if isinstance(clause, dict)]
        if len(masks) != len(clauses):
            raise ContractError('plan_contract_error', 'execution', 'filter clause 형식이 올바르지 않습니다.')
        result = masks[0]
        for mask in masks[1:]:
            result = result & mask if connective == 'all' else result | mask
        return result.fillna(False)
    field = str(tree.get('field') or '')
    if not field or field not in frame.columns:
        raise ContractError('source_schema_mismatch', 'execution', 'filter canonical field가 없습니다.', {'field': field})
    operator = FILTER_ALIASES.get(str(tree.get('operator') or connective).lower(), str(tree.get('operator') or connective).lower())
    if operator not in FILTER_OPERATORS:
        raise ContractError('unsupported_operation', 'execution', '지원하지 않는 filter operator입니다.', {'operator': operator})
    raw = frame[field]
    series = _typed_series(raw, tree.get('semantic_type'))
    value = tree.get('value')
    values = tree.get('values') if isinstance(tree.get('values'), list) else []
    if operator == 'is_null':
        return raw.isna()
    if operator == 'is_not_null':
        return raw.notna()
    if operator == 'is_blank':
        return _is_blank(raw)
    if operator == 'is_not_blank':
        return ~_is_blank(raw)
    if operator == 'null_or_blank':
        return _is_blank(raw)
    if operator in {'in', 'not_in'}:
        mask = series.isin(values)
        return ~mask if operator == 'not_in' else mask
    if operator == 'between':
        pair = values if len(values) == 2 else value if isinstance(value, list) and len(value) == 2 else []
        if len(pair) != 2:
            raise ContractError('plan_contract_error', 'execution', 'between은 두 경계값이 필요합니다.')
        return series.between(pair[0], pair[1], inclusive=str(tree.get('inclusive') or 'both'))
    if operator == 'contains':
        return series.astype('string').str.contains(str(value), regex=False, na=False)
    if operator == 'starts_with':
        return series.astype('string').str.startswith(str(value), na=False)
    if operator == 'ends_with':
        return series.astype('string').str.endswith(str(value), na=False)
    if operator == 'eq':
        return series.eq(value).fillna(False)
    if operator == 'ne':
        return series.ne(value).fillna(False)
    if operator == 'gt':
        return series.gt(value).fillna(False)
    if operator == 'gte':
        return series.ge(value).fillna(False)
    if operator == 'lt':
        return series.lt(value).fillna(False)
    if operator == 'lte':
        return series.le(value).fillna(False)
    raise AssertionError(operator)

def _stable_unique(values: pd.Series) -> list[Any]:
    result: list[Any] = []
    seen: set[str] = set()
    for value in values.tolist():
        if pd.isna(value):
            continue
        marker = sha256_json(json_value(value))
        if marker in seen:
            continue
        seen.add(marker)
        result.append(value)
    return result

def _aggregate(frame: pd.DataFrame, op: dict[str, Any], operation_id: str) -> pd.DataFrame:
    groups = [str(field) for field in op.get('group_by', [])]
    metrics = op.get('metrics') if isinstance(op.get('metrics'), list) else []
    if not metrics:
        raise ContractError('plan_contract_error', 'execution', 'aggregate metric이 없습니다.', {'operation_id': operation_id})
    required = list(groups)
    for item in metrics:
        if isinstance(item, dict) and str(item.get('function') or '') != 'count':
            required.append(str(item.get('field') or ''))
    _require_columns(frame, required, operation_id)

    def calculate(part: pd.DataFrame, metric: dict[str, Any]) -> Any:
        function = str(metric.get('function') or '').lower()
        field = str(metric.get('field') or '')
        if function not in AGGREGATIONS:
            raise ContractError('unsupported_operation', 'execution', '지원하지 않는 집계입니다.', {'function': function})
        if function == 'count':
            return int(len(part)) if not field else int(part[field].count())
        series = part[field]
        if function == 'sum':
            return pd.to_numeric(series, errors='coerce').sum(min_count=1)
        if function == 'mean':
            return pd.to_numeric(series, errors='coerce').mean()
        if function == 'min':
            return series.min()
        if function == 'max':
            return series.max()
        if function == 'nunique':
            return int(series.nunique(dropna=bool(metric.get('dropna', True))))
        if function == 'median':
            return pd.to_numeric(series, errors='coerce').median()
        if function == 'std':
            return pd.to_numeric(series, errors='coerce').std(ddof=int(metric.get('ddof', 1)))
        if function == 'var':
            return pd.to_numeric(series, errors='coerce').var(ddof=int(metric.get('ddof', 1)))
        if function == 'list_unique':
            return _stable_unique(series)
        raise AssertionError(function)
    rows: list[dict[str, Any]] = []
    if groups:
        grouped = frame.groupby(groups, dropna=False, sort=False, observed=False)
        for keys, part in grouped:
            key_values = keys if isinstance(keys, tuple) else (keys,)
            row = {field: value for field, value in zip(groups, key_values, strict=True)}
            for metric in metrics:
                row[str(metric.get('as') or metric.get('field') or metric.get('function'))] = calculate(part, metric)
            rows.append(row)
    else:
        row = {}
        for metric in metrics:
            row[str(metric.get('as') or metric.get('field') or metric.get('function'))] = calculate(frame, metric)
        rows.append(row)
    return pd.DataFrame(rows, columns=groups + [str(item.get('as') or item.get('field') or item.get('function')) for item in metrics])

def _sort_frame(frame: pd.DataFrame, keys: list[dict[str, Any]], operation_id: str) -> pd.DataFrame:
    if not keys:
        return frame.reset_index(drop=True)
    fields = [str(item.get('field') or '') for item in keys]
    _require_columns(frame, fields, operation_id)
    directions = [str(item.get('direction') or 'asc').lower() != 'desc' for item in keys]
    null_values = {str(item.get('nulls') or 'last').lower() for item in keys}
    if len(null_values) > 1:
        current = frame.copy()
        for item in reversed(keys):
            current = current.sort_values(by=[str(item.get('field'))], ascending=str(item.get('direction') or 'asc').lower() != 'desc', na_position=str(item.get('nulls') or 'last').lower(), kind='mergesort')
        return current.reset_index(drop=True)
    return frame.sort_values(fields, ascending=directions, na_position=next(iter(null_values)), kind='mergesort').reset_index(drop=True)

def _rank_partition(part: pd.DataFrame, op: dict[str, Any], operation_id: str) -> pd.DataFrame:
    rank_by = op.get('rank_by') if isinstance(op.get('rank_by'), list) else []
    tie_break = op.get('tie_break_by') if isinstance(op.get('tie_break_by'), list) else []
    limit = int(op.get('limit') or 1)
    if limit < 1:
        raise ContractError('plan_contract_error', 'execution', 'rank limit은 1 이상이어야 합니다.')
    sorted_part = _sort_frame(part, rank_by + tie_break, operation_id)
    tie_policy = str(op.get('tie_policy') or 'exact_n')
    if tie_policy not in {'exact_n', 'include_all'}:
        raise ContractError('plan_contract_error', 'execution', 'rank tie policy가 올바르지 않습니다.')
    selected = sorted_part.head(limit)
    if tie_policy == 'include_all' and len(sorted_part) > limit and (not selected.empty):
        rank_fields = [str(item.get('field') or '') for item in rank_by]
        boundary = selected.iloc[-1]
        mask = pd.Series(True, index=sorted_part.index)
        for field in rank_fields:
            if pd.isna(boundary[field]):
                mask &= sorted_part[field].isna()
            else:
                mask &= sorted_part[field].eq(boundary[field])
        boundary_indices = sorted_part.index[mask]
        if len(boundary_indices):
            last_position = max((sorted_part.index.get_loc(index) for index in boundary_indices))
            selected = sorted_part.iloc[:last_position + 1]
    result = selected.copy()
    rank_field = str(op.get('emit_rank_field') or '')
    if rank_field:
        rank_fields = [str(item.get('field') or '') for item in rank_by]
        tuples = [tuple((row[field] for field in rank_fields)) for _, row in result.iterrows()]
        ranks: list[int] = []
        prior: Any = object()
        current_rank = 0
        for index, value in enumerate(tuples, start=1):
            if value != prior:
                current_rank = index
                prior = value
            ranks.append(current_rank)
        result[rank_field] = ranks
    return result.reset_index(drop=True)

def _rank(frame: pd.DataFrame, op: dict[str, Any], operation_id: str) -> pd.DataFrame:
    partition_by = [str(field) for field in op.get('partition_by', [])]
    rank_by = op.get('rank_by') if isinstance(op.get('rank_by'), list) else []
    _require_columns(frame, partition_by + [str(item.get('field') or '') for item in rank_by], operation_id)
    if not partition_by:
        return _rank_partition(frame, op, operation_id)
    pieces: list[pd.DataFrame] = []
    for _, part in frame.groupby(partition_by, dropna=False, sort=False, observed=False):
        pieces.append(_rank_partition(part, op, operation_id))
    return pd.concat(pieces, ignore_index=True) if pieces else frame.head(0).copy()

def _compare_fields(frame: pd.DataFrame, op: dict[str, Any], operation_id: str) -> pd.DataFrame:
    left = str(op.get('left_field') or '')
    right = str(op.get('right_field') or '')
    operator = str(op.get('operator') or 'eq').lower()
    _require_columns(frame, [left, right], operation_id)
    if operator not in COMPARE_OPERATORS:
        raise ContractError('unsupported_operation', 'execution', '지원하지 않는 field 비교입니다.')
    left_s = _typed_series(frame[left], op.get('semantic_type'))
    right_s = _typed_series(frame[right], op.get('semantic_type'))
    nulls = left_s.isna() | right_s.isna()
    comparisons = {'eq': left_s.eq(right_s), 'ne': left_s.ne(right_s), 'gt': left_s.gt(right_s), 'gte': left_s.ge(right_s), 'lt': left_s.lt(right_s), 'lte': left_s.le(right_s)}
    mask = comparisons[operator]
    policy = str(op.get('null_policy') or 'false')
    if policy == 'error' and bool(nulls.any()):
        raise ContractError('plan_contract_error', 'execution', 'null field 비교가 금지되어 있습니다.')
    if policy == 'true':
        mask = mask | nulls
    elif policy in {'false', 'three_valued'}:
        mask = mask & ~nulls
    else:
        raise ContractError('plan_contract_error', 'execution', 'field 비교 null policy가 올바르지 않습니다.')
    return frame.loc[mask.fillna(False)].reset_index(drop=True)

def _join(left: pd.DataFrame, right: pd.DataFrame, op: dict[str, Any], operation_id: str) -> pd.DataFrame:
    how = str(op.get('how') or 'inner').lower()
    if how not in JOIN_TYPES:
        raise ContractError('unsupported_operation', 'execution', '지원하지 않는 join 방식입니다.', {'how': how})
    mappings = op.get('key_mappings') if isinstance(op.get('key_mappings'), list) else []
    left_on = [str(item.get('left') or '') for item in mappings]
    right_on = [str(item.get('right') or '') for item in mappings]
    if not left_on or len(left_on) != len(right_on):
        raise ContractError('plan_contract_error', 'execution', 'join key mapping이 필요합니다.')
    _require_columns(left, left_on, operation_id)
    _require_columns(right, right_on, operation_id)
    null_policy = str(op.get('null_key_policy') or 'never_match')
    if null_policy == 'error' and (left[left_on].isna().any(axis=None) or right[right_on].isna().any(axis=None)):
        raise ContractError('join_cardinality_violation', 'execution', 'null join key가 허용되지 않습니다.')
    if null_policy == 'never_match':
        left = left.loc[~left[left_on].isna().any(axis=1)].copy()
        right = right.loc[~right[right_on].isna().any(axis=1)].copy()
    elif null_policy not in {'match', 'error'}:
        raise ContractError('plan_contract_error', 'execution', 'join null policy가 올바르지 않습니다.')
    cardinality = str(op.get('cardinality') or 'many_to_many')
    validate_map = {'one_to_zero_or_one': 'one_to_one', 'one_to_one': 'one_to_one', 'one_to_many': 'one_to_many', 'many_to_one': 'many_to_one', 'many_to_many': 'many_to_many', 'one_to_one_after_aggregate': 'one_to_one'}
    if cardinality not in validate_map:
        raise ContractError('plan_contract_error', 'execution', 'join cardinality가 올바르지 않습니다.')
    try:
        if how in {'semi', 'anti'}:
            right_keys = right[right_on].drop_duplicates()
            marker = left.merge(right_keys, how='left', left_on=left_on, right_on=right_on, indicator=True, sort=False)['_merge'].eq('both')
            return left.loc[marker if how == 'semi' else ~marker].reset_index(drop=True)
        merged = left.merge(right, how=how, left_on=left_on, right_on=right_on, validate=validate_map[cardinality], sort=False, suffixes=('', '__right'))
    except Exception as exc:
        raise ContractError('join_cardinality_violation', 'execution', 'join cardinality를 만족하지 못했습니다.', {'operation_id': operation_id, 'cardinality': cardinality, 'reason': str(exc)[:300]}) from exc
    collision_columns = [column for column in merged.columns if str(column).endswith('__right')]
    output_fields = [str(field) for field in op.get('output_fields', [])]
    if collision_columns and (not output_fields):
        raise ContractError('join_cardinality_violation', 'execution', '선언되지 않은 join suffix가 생성되었습니다.')
    if output_fields:
        _require_columns(merged, output_fields, operation_id)
        merged = merged[output_fields]
    empty_policy = str(op.get('empty_side_policy') or 'allow')
    if empty_policy == 'error' and merged.empty:
        raise ContractError('source_coverage_incomplete', 'execution', 'join 결과가 비어 있습니다.')
    return merged.reset_index(drop=True)

def _formula_value(frame: pd.DataFrame, expression: dict[str, Any], depth: int=0) -> Any:
    if depth > 6:
        raise ContractError('plan_contract_error', 'execution', 'formula 깊이가 허용 범위를 초과했습니다.')
    if 'metric_ref' in expression:
        field = str(expression.get('metric_ref') or '')
        _require_columns(frame, [field], 'formula')
        return pd.to_numeric(frame[field], errors='coerce')
    if 'field_ref' in expression:
        field = str(expression.get('field_ref') or '')
        _require_columns(frame, [field], 'formula')
        return frame[field].copy()
    if 'literal' in expression:
        return expression.get('literal')
    op = str(expression.get('op') or '')
    args = expression.get('args') if isinstance(expression.get('args'), list) else []
    values = [_formula_value(frame, item, depth + 1) for item in args if isinstance(item, dict)]
    if len(values) != len(args):
        raise ContractError('plan_contract_error', 'execution', 'formula argument 형식이 올바르지 않습니다.')
    if op == 'add' and len(values) == 2:
        return values[0] + values[1]
    if op == 'subtract' and len(values) == 2:
        return values[0] - values[1]
    if op == 'multiply' and len(values) == 2:
        return values[0] * values[1]
    if op in {'coalesce', 'coalesce_blank'} and len(values) == 2:
        primary, fallback = values
        if isinstance(primary, pd.Series):
            missing = primary.isna()
            if op == 'coalesce_blank':
                missing = missing | primary.astype('string').str.strip().eq('').fillna(True)
            return primary.mask(missing, fallback)
        missing = primary is None or (isinstance(primary, float) and math.isnan(primary))
        if op == 'coalesce_blank' and isinstance(primary, str):
            missing = missing or not primary.strip()
        return fallback if missing else primary
    if op == 'safe_divide' and len(values) == 2:
        denominator = values[1]
        zero = denominator.eq(0) if isinstance(denominator, pd.Series) else denominator == 0
        policy = str(expression.get('zero_division') or 'null')
        if policy == 'error' and (bool(zero.any()) if isinstance(zero, pd.Series) else bool(zero)):
            raise ContractError('plan_contract_error', 'execution', '0으로 나눌 수 없습니다.')
        if isinstance(denominator, pd.Series):
            safe = denominator.mask(zero)
            result = values[0] / safe
            return result.fillna(0) if policy == 'zero' else result
        if zero:
            return 0 if policy == 'zero' else math.nan
        return values[0] / denominator
    if op == 'datetime_diff_hours' and len(values) == 2:
        try:
            left = pd.to_datetime(values[0], errors='coerce', utc=True)
            right = pd.to_datetime(values[1], errors='coerce', utc=True)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ContractError('plan_contract_error', 'execution', 'datetime_diff_hours 입력을 datetime으로 변환할 수 없습니다.') from exc
        if not isinstance(values[0], pd.Series) and values[0] is not None and pd.isna(left):
            raise ContractError('plan_contract_error', 'execution', 'datetime_diff_hours 기준 시각이 올바르지 않습니다.')
        if not isinstance(values[1], pd.Series) and values[1] is not None and pd.isna(right):
            raise ContractError('plan_contract_error', 'execution', 'datetime_diff_hours 대상 시각이 올바르지 않습니다.')
        delta = left - right
        if isinstance(delta, pd.Series):
            return delta.dt.total_seconds() / 3600.0
        if isinstance(delta, pd.TimedeltaIndex):
            index = values[0].index if isinstance(values[0], pd.Series) else values[1].index if isinstance(values[1], pd.Series) else None
            return pd.Series(delta.total_seconds() / 3600.0, index=index)
        return delta.total_seconds() / 3600.0
    if op == 'abs' and len(values) == 1:
        return values[0].abs() if isinstance(values[0], pd.Series) else abs(values[0])
    if op == 'round' and len(values) == 1:
        return values[0].round(int(expression.get('digits') or 0))
    if op == 'min_pair' and len(values) == 2:
        return pd.concat([pd.Series(values[0]), pd.Series(values[1])], axis=1).min(axis=1)
    if op == 'max_pair' and len(values) == 2:
        return pd.concat([pd.Series(values[0]), pd.Series(values[1])], axis=1).max(axis=1)
    raise ContractError('unsupported_operation', 'execution', '지원하지 않는 formula 연산입니다.', {'operator': op})

@dataclass(slots=True)
class ExecutionResult:
    rows: list[dict[str, Any]]
    columns: list[str]
    row_count: int
    operation_trace: list[dict[str, Any]]
    result_sha256: str

    def as_contract(self, plan: dict[str, Any]) -> dict[str, Any]:
        return {'contract_version': 'analysis.result.v1', 'status': 'empty' if self.row_count == 0 else 'ok', 'plan_id': plan.get('plan_id', ''), 'columns': self.columns, 'rows': self.rows, 'row_count': self.row_count, 'lineage': plan.get('lineage', {}), 'operation_trace': self.operation_trace, 'result_sha256': self.result_sha256}

class TypedExecutor:
    """Execute a closed operation DAG over canonical pandas frames."""

    def __init__(self, max_rows: int=100000, max_operations: int=64):
        self.max_rows = int(max_rows)
        self.max_operations = int(max_operations)

    def execute(self, plan: dict[str, Any], frames: dict[str, Any]) -> ExecutionResult:
        validate_plan_integrity(plan)
        operations = plan.get('operations') if isinstance(plan.get('operations'), list) else []
        if not operations or len(operations) > self.max_operations:
            raise ContractError('plan_contract_error', 'execution', 'operation DAG 크기가 올바르지 않습니다.')
        values: dict[str, pd.DataFrame] = {str(key) if str(key).startswith('source:') else f'source:{key}': _frame(value) for key, value in frames.items()}
        trace: list[dict[str, Any]] = []
        last_id = ''
        for operation in operations:
            if not isinstance(operation, dict):
                raise ContractError('plan_contract_error', 'execution', 'operation 형식이 올바르지 않습니다.')
            operation_id = str(operation.get('id') or '')
            operator = str(operation.get('op') or '')
            if not operation_id or operation_id in values:
                raise ContractError('plan_contract_error', 'execution', 'operation ID가 없거나 중복되었습니다.')
            input_id = str(operation.get('input') or last_id)
            input_frame = values.get(input_id)
            input_hashes: list[str] = []
            if input_frame is not None:
                input_hashes.append(sha256_json(input_frame.to_dict(orient='records')))
            if operator == 'filter':
                current = self._one(values, input_id, operation_id)
                output = current.loc[_filter_mask(current, operation.get('where') or {})].reset_index(drop=True)
            elif operator == 'ordered_range':
                current = self._one(values, input_id, operation_id)
                field = str(operation.get('field') or 'OPER_SEQ')
                _require_columns(current, [field], operation_id)
                numeric = pd.to_numeric(current[field], errors='coerce')
                start, end = (operation.get('start'), operation.get('end'))
                output = current.loc[numeric.between(start, end, inclusive='both')].reset_index(drop=True)
            elif operator == 'project' or operator == 'detail':
                current = self._one(values, input_id, operation_id)
                fields = [str(field) for field in operation.get('fields', [])]
                _require_columns(current, fields, operation_id)
                output = current[fields].copy()
            elif operator == 'aggregate':
                output = _aggregate(self._one(values, input_id, operation_id), operation, operation_id)
            elif operator == 'sort':
                output = _sort_frame(self._one(values, input_id, operation_id), operation.get('keys') or [], operation_id)
            elif operator == 'rank':
                output = _rank(self._one(values, input_id, operation_id), operation, operation_id)
            elif operator == 'compare_fields':
                output = _compare_fields(self._one(values, input_id, operation_id), operation, operation_id)
            elif operator == 'compare_group_attributes':
                current = self._one(values, input_id, operation_id)
                groups = [str(field) for field in operation.get('group_by', [])]
                fields = [str(field) for field in operation.get('comparison_fields', [])]
                _require_columns(current, groups + fields, operation_id)
                counts = current.groupby(groups, dropna=False, sort=False)[fields].nunique(dropna=False)
                rule = str(operation.get('comparison_rule') or 'any')
                mask = counts.gt(1).any(axis=1) if rule == 'any' else counts.gt(1).all(axis=1)
                keys = counts.loc[mask].reset_index()[groups]
                output = current.merge(keys, how='inner', on=groups, validate='many_to_one').reset_index(drop=True)
            elif operator == 'find_duplicate_groups':
                current = self._one(values, input_id, operation_id)
                fields = [str(field) for field in operation.get('fields', [])]
                _require_columns(current, fields, operation_id)
                counts = current.groupby(fields, dropna=False, sort=False).size().reset_index(name=str(operation.get('count_field') or 'DUPLICATE_COUNT'))
                output = counts.loc[counts.iloc[:, -1].ge(int(operation.get('minimum_count') or 2))].reset_index(drop=True)
            elif operator == 'join':
                left_id = str(operation.get('left') or input_id)
                right_id = str(operation.get('right') or '')
                left = self._one(values, left_id, operation_id)
                right = self._one(values, right_id, operation_id)
                input_hashes = [sha256_json(left.to_dict(orient='records')), sha256_json(right.to_dict(orient='records'))]
                output = _join(left, right, operation, operation_id)
            elif operator == 'presence_filter':
                left = self._one(values, str(operation.get('left') or ''), operation_id)
                right = self._one(values, str(operation.get('right') or ''), operation_id)
                left_metric = str(operation.get('left_metric') or '')
                right_metric = str(operation.get('right_metric') or '')
                keys = [str(field) for field in operation.get('keys', [])]
                _require_columns(left, keys + [left_metric], operation_id)
                _require_columns(right, keys + [right_metric], operation_id)
                left_positive = left.loc[pd.to_numeric(left[left_metric], errors='coerce').fillna(0).gt(0)]
                right_positive = right.loc[pd.to_numeric(right[right_metric], errors='coerce').fillna(0).gt(0), keys].drop_duplicates()
                marker = left_positive.merge(right_positive.assign(__present=True), on=keys, how='left', validate='many_to_one')
                output = marker.loc[marker['__present'].isna()].drop(columns='__present').reset_index(drop=True)
                if bool(operation.get('materialize_right_zero', True)):
                    output[right_metric] = 0
            elif operator == 'derive':
                current = self._one(values, input_id, operation_id).copy()
                output_field = str(operation.get('output_field') or '')
                formula = operation.get('formula') if isinstance(operation.get('formula'), dict) else {}
                current[output_field] = _formula_value(current, formula.get('expression') or formula)
                rounding = formula.get('rounding') if isinstance(formula.get('rounding'), dict) else {}
                if rounding:
                    current[output_field] = pd.to_numeric(current[output_field], errors='coerce').round(int(rounding.get('digits') or 0))
                output = current
            elif operator == 'dedupe':
                current = self._one(values, input_id, operation_id)
                fields = [str(field) for field in operation.get('fields', [])]
                _require_columns(current, fields, operation_id)
                output = current.drop_duplicates(subset=fields, keep=str(operation.get('keep') or 'first')).reset_index(drop=True)
            elif operator == 'row_match_groups':
                current = self._one(values, input_id, operation_id)
                groups = operation.get('groups') if isinstance(operation.get('groups'), list) else []
                masks = []
                for group in groups:
                    if not isinstance(group, dict):
                        continue
                    masks.append(_filter_mask(current, {'op': 'all', 'clauses': group.get('clauses') or []}))
                output = current.loc[pd.concat(masks, axis=1).any(axis=1) if masks else pd.Series(False, index=current.index)].reset_index(drop=True)
            elif operator == 'concat_segments':
                segments = operation.get('segments') if isinstance(operation.get('segments'), list) else []
                pieces = []
                for segment in segments:
                    source = self._one(values, str(segment.get('input') or ''), operation_id).copy()
                    source[str(operation.get('label_field') or 'RESULT_GROUP')] = str(segment.get('label') or '')
                    pieces.append(source)
                output = pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame()
            elif operator in {'transform_previous_result', 'enrich_previous_result'}:
                if operator == 'transform_previous_result':
                    output = self._one(values, input_id, operation_id).copy()
                else:
                    left = self._one(values, str(operation.get('left') or input_id), operation_id)
                    right = self._one(values, str(operation.get('right') or ''), operation_id)
                    output = _join(left, right, {**operation, 'op': 'join', 'how': 'left'}, operation_id)
            elif operator == 'explain_previous':
                output = self._one(values, input_id, operation_id).copy()
            elif operator == 'registered_call':
                current = self._one(values, input_id, operation_id)
                required_fields = [str(field) for field in operation.get('required_fields') or []]
                _require_columns(current, required_fields, operation_id)
                records = current.to_dict(orient='records')
                for row in records:
                    for field in required_fields:
                        try:
                            if bool(pd.isna(row[field])):
                                row[field] = None
                        except (TypeError, ValueError):
                            pass
                selected_indices = dispatch_registered_call(operation, records)
                output = current.iloc[selected_indices].reset_index(drop=True)
            else:
                raise ContractError('unsupported_operation', 'execution', '지원하지 않는 typed operation입니다.', {'operator': operator})
            if len(output) > self.max_rows:
                raise ContractError('execution_memory_limit_exceeded', 'execution', '실행 결과 행 수가 허용 범위를 초과했습니다.')
            values[operation_id] = output
            output_hash = sha256_json(output.to_dict(orient='records'))
            trace.append({'operation_id': operation_id, 'operator_id': f'{operator}.v1', 'input_contract_sha256': sha256_json(input_hashes), 'output_contract_sha256': output_hash, 'row_count': int(len(output))})
            last_id = operation_id
        final_id = str(plan.get('result_operation_id') or last_id)
        final = self._one(values, final_id, final_id)
        result_contract = plan.get('result_contract') if isinstance(plan.get('result_contract'), dict) else {}
        columns = [str(field) for field in result_contract.get('columns', [])]
        if columns:
            _require_columns(final, columns, final_id)
            final = final[columns]
        else:
            columns = [str(field) for field in final.columns]
        ordering = result_contract.get('ordering') if isinstance(result_contract.get('ordering'), list) else []
        if ordering:
            final = _sort_frame(final, ordering, 'result_contract')
        rows = [json_value(row) for row in final.to_dict(orient='records')]
        return ExecutionResult(rows, columns, len(rows), trace, sha256_json({'columns': columns, 'rows': rows}))

    @staticmethod
    def _one(values: dict[str, pd.DataFrame], identifier: str, operation_id: str) -> pd.DataFrame:
        if identifier not in values:
            raise ContractError('plan_contract_error', 'execution', 'operation 입력이 존재하지 않습니다.', {'operation_id': operation_id, 'input': identifier})
        return values[identifier]


EMBEDDED_SCHEMAS = json.loads('{"analysis-result.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/analysis-result.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"columns":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"contract_version":{"const":"analysis.result.v1","type":"string"},"lineage":{"$ref":"#/$defs/jsonObject"},"operation_trace":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"plan_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"result_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"row_count":{"minimum":0,"type":"integer"},"rows":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":100000,"type":"array"},"status":{"enum":["ok","empty","partial"],"type":"string"}},"required":["contract_version","status","plan_id","columns","rows","row_count","lineage","operation_trace","result_sha256"],"title":"analysis.result.v1","type":"object"}}')



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



from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, IntInput, Output
from lfx.schema.data import Data


class TypedExecutorPublisher(Component):
    display_name = "17 Typed IR 실행 및 결과 발행"
    description = "등록된 타입 연산자 DAG만 결정론적으로 실행하고 해시가 포함된 불변 분석 결과를 발행합니다."
    icon = "play-circle"
    metadata = {"logical_stage": "typed_execution"}
    inputs = [
        DataInput(name="execution_context", display_name="Typed IR 실행 컨텍스트", required=True, info="검증된 실행 계획과 표준화된 데이터 프레임이 포함된 컨텍스트입니다."),
        IntInput(name="executor_row_limit", display_name="실행 결과 행 수 제한", value=100000, info="결정론적 실행기가 처리·발행할 수 있는 최대 행 수입니다."),
    ]
    outputs = [Output(name="result_context", display_name="불변 분석 결과 컨텍스트", method="execute", types=["Data"])]

    def execute(self) -> Data:
        current = _payload(getattr(self, "execution_context", None))
        try:
            current = _require_context(current, "typed_execution")
            if not current.get("ok"):
                return Data(data=current)
            limit = max(1, min(int(getattr(self, "executor_row_limit", 100000)), 100000))
            execution = TypedExecutor(max_rows=limit).execute(current["plan"], current.get("frames") or {})
            result = execution.as_contract(current["plan"])
            validate_contract(result, "analysis-result.schema.json", stage="result_contract")
            current.update({"stage": "typed_execution", "result": result})
            current.pop("frames", None)
            current.pop("prior_result", None)
            current.pop("prior_semantics", None)
        except Exception as exc:
            current = _pipeline_error(current, exc, "typed_execution")
        return Data(data=current)
