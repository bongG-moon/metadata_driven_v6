# -*- coding: utf-8 -*-
"""GENERATED standalone component: RequestStateCapsule.

Regenerate with tools/build_standalone_components.py.  Do not hand edit.
"""
from __future__ import annotations

import json

EMBEDDED_SOURCE_MANIFEST = json.loads('{"catalog_contract_version":"metadata.runtime.catalog.v1","catalog_declared_sha256":"1f8b6c1522b96425a6a46a3e4dfcf4c5b7c338c6bc0af3c2a0878806ea4a7f8e","catalog_file_sha256":"0b035cefd556b3c37b166e73270dee3e7070a2adf2dd56750b8e1015516bfcce","contract_version":"standalone.source.manifest.v1","reference_sources":{"contracts/schemas/active-domain-pointer.schema.json":"8ff3e114e106d0bc08c83e61947ac967c28cd5390cd0539cb1efdc64b82f9a61","contracts/schemas/analysis-plan.schema.json":"15dbb187f458d03ad4d55063eef898b862529dc68e9f64840d08ab20df9cfb76","contracts/schemas/analysis-result.schema.json":"06e92c0892ff5b209783332f33e4d4ed1855612470b088390e4501591f68065b","contracts/schemas/analysis-route.schema.json":"aadd7504e7f75329b8b6a50634261e073450e6d19d8e14d4a44196c0000e0c04","contracts/schemas/answer-facts.schema.json":"26c573be25f4fade355a37f2ab231f3e0aa8ac83445ee58020a99388648809ed","contracts/schemas/answer-sections.schema.json":"4c1d645c9927879e6a9e877def326ff045b5a01edaf48a566b935bc4734882ab","contracts/schemas/approval-event.schema.json":"4aa6b10eeb875538d00d6de564bdbe24eb093e8727ed57515cbadba63f13d7a9","contracts/schemas/config-registry.schema.json":"2f90dfb2b99e17faa9afecaf1f32295f6d713067aeca66c7dc1544c5713598e9","contracts/schemas/display-options.schema.json":"099ef7c371a2ac015cf7b59ae873d2ff749cdad7fa738bbcccc9b4838ea45866","contracts/schemas/domain-package.schema.json":"f39f433985180636bb3b6dfe054cfb8e63998acbe0112f7082a8233b619517f7","contracts/schemas/download-item.schema.json":"91efd43bf2db00bf5e85071fa2992679c3b2dc050251a5c82e839dcd7f5d4086","contracts/schemas/error-registry.schema.json":"f67a1ab5ef2568626d406cb9feb38acfbb6fc593fa04f3da063f8293da653b64","contracts/schemas/error.schema.json":"1a0c89cc1898a894b0490a59f286c68520c0f74be0811f6c06c4aa3e50fe5602","contracts/schemas/evidence-manifest.schema.json":"2805ed7cce742e96b5e10902b096fbec91e40a8aca7fde7bfe95c1d12a9668bb","contracts/schemas/executable-blueprint.schema.json":"e55dbe8faa2f1f2eb933b1548b2b1c37886a0911ceb4e70838427bac2327f14a","contracts/schemas/executed-result.schema.json":"eaba5818e5fb30e2a572f5a81488d9ba34032adcf3af55dfbb0d4287afc7e435","contracts/schemas/flow-inventory.schema.json":"cdce69d64a9df37a88e139a0fd0900d38d9475d2a8f13ff9a9b5c1bf0777b672","contracts/schemas/gaia-metadata.schema.json":"86d0a11a06a97d573b550a427d26abe9db6e897d3c46681f02e2427735e9f093","contracts/schemas/metadata-annotation-proposal.schema.json":"f0b227cc42a528d6e0b95f1c8c4a1bf6bbb6871d17d32c108d65b47d2b0ddc7f","contracts/schemas/metadata-authoring-draft.schema.json":"c2b00a9f4e910220c413c557eaec188d143491f04484533db3d8fe3963ed309d","contracts/schemas/metadata-authoring-proposal.schema.json":"8ee3fc86d8f596c554443c16ad619822e63315ed8f2bfd06311987fc63322edd","contracts/schemas/metadata-authoring-response.schema.json":"da776b8a156d007c5bd95e86ad10cfb5a8ac7f06c2cae0c52aeb96b6a36415f6","contracts/schemas/metadata-bootstrap-dataset-ir.schema.json":"351260f7ed418b35f4ca1e5012a353b1d8f820ea21dfc8880483c193880af3b6","contracts/schemas/metadata-bootstrap-main-filter-ir.schema.json":"41c849c88b803d53af9c02c3d50127c47e8ee38e46d7b0a1ad0d09c3638e48fa","contracts/schemas/metadata-bundle.schema.json":"985ffe44974cf14d6c52a8188d54c3b209c00478e83888f00c359cd056d5dc81","contracts/schemas/metadata-envelope.schema.json":"9abca177e22b570f2158dace05256f671c0acbd054705dfe4f34611fbdae2048","contracts/schemas/metadata-freeform-dataset-ir.schema.json":"1b22d18352b484e2ed847c2859bd4361aef4e9bb7fe52584c17ad5e4381d0642","contracts/schemas/metadata-freeform-domain-ir.schema.json":"28cf27865e798227662a452dd83dba1a1ae4e7ef1a14e706ab17ed22747a970e","contracts/schemas/metadata-freeform-main-filter-ir.schema.json":"d8cacb5b86029087e568b0ee2d5aabf76a8e91866cb3954bd0aa8c6e1d2e4e9f","contracts/schemas/model-profile.schema.json":"14345c16f629fc03a3de2cdd2fe469bef1fdc82cd2f93954ce1f4204ba82f356","contracts/schemas/operator-registry.schema.json":"acd003c6db66b470a2653fc8a97caaf3856c9d4cfd934bc0f27ef609787c2746","contracts/schemas/pending-metadata-write.schema.json":"af7a0593fafbdcea16f1212ba92484525626e43f2a25d91f9c310a80f5b37a4d","contracts/schemas/query-registry.schema.json":"8422a44035eb2a06381166d69a185036c698f581b17741a8c4686fbeea109040","contracts/schemas/registered-call.schema.json":"41c4152f45577f05c925d5d782a48f8db45f67f8e48aac8805b822269516bd58","contracts/schemas/registered-function-card.schema.json":"bc9ca8b01c90d2d11737f1a70586e9227510b67fdab26c8ae605d9e830170dfd","contracts/schemas/request-capsule.schema.json":"675e661653098288d6cc9e6e9b3599ed3bf3e05d6d592ac66d9ed46b9fd2afaf","contracts/schemas/resolved-candidate-bundle.schema.json":"a24b7d2fc3798f1dd69e1af94a7071eae8fb56d93a4191258953fd63b4211568","contracts/schemas/response.schema.json":"40c1e43f2228c04bb9ea652f1107a7ac202405c3321bc2c6af8dbc543b2e7b06","contracts/schemas/retrieval-job-bundle.schema.json":"e73cd6e6c50bb24b528111c36c410af3afe2fe3ff28d3d906cfe023263a12105","contracts/schemas/runtime-catalog-v2.schema.json":"3f7f6c5154c9e7922dd65490e9166ba0038c6a242258ec30d409d8a553948fed","contracts/schemas/semantic-intent-selection.schema.json":"a70c99e36060531fac9730c02f706ffa8d108b872c5abe0e2d05cafa459e6a75","contracts/schemas/semantic-intent.schema.json":"a743b7e26168dda04a7f46205fed67987a587cf3cce939cf57b228b099bfad53","contracts/schemas/source-bundle.schema.json":"a5330ef1b104df5dd0f19385b5e7994ee5469feffa110ee84087b7992258ea92","contracts/schemas/source-result.schema.json":"f342dcf0f948f7f99899335d83f302f2aaa38b05bb246eb06f9c1da0161f516c","contracts/schemas/trace.schema.json":"3f7cb2dd4e88b5f9f09695347ce42d8b98d5c4534d8fab41cca8ea1c9e3d484e","contracts/schemas/turn-state.schema.json":"688ad4f5ac1b133e60e3a2ef2bef56d0b18c87a41d2c6c236264285aeba32280","contracts/schemas/unsupported-telemetry.schema.json":"8c3675797be935d6fd52db2883d433d464df2fdecc5e0d52e795a5fa1e6c8439","contracts/schemas/validation-case.schema.json":"23304f969ca614324f7a74b52edc72c4e6753e76c476a77fc8db68f089941682","langflow_components/shared/01_prompt_bundle_composer.py":"2a8e80103205136221c87901a1bdeeb7df62f954c9f3f9c407a77a2e41a6b77b","langflow_components/shared/02_conditional_llm_invoker.py":"2b7ee35fb4276b932285a62860b1114b29797698232bfc9523597c103c6ea3d9","metadata/domain_packs/manufacturing/approved_source_registry.json":"241969f12d76c0d616296894dc51ba95553ebf48d5edb15e20480c4beec64587","reference_runtime/authoring_blueprint.py":"9fc416a04e0da317586ad8abf9831bf650746a7f1907ad62fcaef4012327fe71","reference_runtime/authoring_source_manifest.py":"311bd68482e163a781bf11aa449587879f659fa9c36f7564129ecea44b88170c","reference_runtime/canonical.py":"338b8b013b9311f94d9b5ff7a3d5902576e9dfb88b40d72d37436025806c2d1d","reference_runtime/contracts.py":"5d16082db0bf437e537a24352834548e48e157a4c740659e9c9f1a0e46960d6e","reference_runtime/domain_authoring_patches.py":"4c78c72bc2412cbe78e74372b7c5af658ada8de1b8058b228f02d2b68b41c445","reference_runtime/domain_packages.py":"ae08de3501c92be10bd8f983fa710cc8e4cec6a40dd8051140ab754c9caac04a","reference_runtime/dummy_data.py":"9d412acfb007f069a1d06eedc718d61cf56bca2844d25d7ade5b21050e6c0b13","reference_runtime/engine.py":"62df5f1a06c0a2765085826bec3e73f99f02da470850d180f2d7a53078c67606","reference_runtime/generic_v2_candidates.py":"5d5d13e1ebc379bee29e8db1d1d103c8f96383ca34923c37879e87bce42a167e","reference_runtime/generic_v2_planner.py":"142665c8050c9302830cedf45928a25b73cd34e80bec66de9ba77003209176d3","reference_runtime/metadata_collections.py":"cb6cc7da54c55c7885569a83d400f38f456698a3d5fdf8fb4e3bfc394641ae54","reference_runtime/metadata_compiler.py":"99544e6094883b4241d010af2bec5d67e6205d34634ad46d6e2ee173107336e3","reference_runtime/plan_compiler.py":"e3782e6e86e41968a7bab1be4056ac2e9459c28188efa92f6532d2898d12abee","reference_runtime/presenter.py":"fee16b71dfaf07be0d27fee14f47aa753ea71350165185071552ff0f30a31101","reference_runtime/registered_functions.py":"d2125d6902ca246b2239e8569959ac37f45847bf17dafaf93b857e088c750e42","reference_runtime/request_literals.py":"00493f9e342ab3065215805ae32f3068cb594209434bf280f2bb4f23c4be62ff","reference_runtime/source_contracts.py":"c43d8865ff045f4c26c5194262620a50961be5b56552c5cc6e7d580b2c11d7b0","reference_runtime/state_contracts.py":"5a03fff6684850361904add4e4d15ea578617d1fce20564119bbac175fb334ae","reference_runtime/typed_executor.py":"af39b2bcfc561fbeed29b62f52d712decf895ef43b41f89ee70c4469507b82fe"}}')


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


import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo
SEOUL = ZoneInfo('Asia/Seoul')
DATE_PATTERNS = (re.compile('(?P<y>20\\d{2})[-/.](?P<m>\\d{1,2})[-/.](?P<d>\\d{1,2})(?:T[^\\s]+)?', re.I), re.compile('(?P<y>20\\d{2})년\\s*(?P<m>\\d{1,2})월\\s*(?P<d>\\d{1,2})일'), re.compile('(?<!\\d)(?P<m>\\d{1,2})\\s*[/.월]\\s*(?P<d>\\d{1,2})\\s*일?'))
RANGE_PATTERN = re.compile('(?P<start>(?:D/[SA]|W/B|FCB|B/G)\\s*\\d+|FCB/H)\\s*[~～-]\\s*(?P<end>(?:D/[SA]|W/B|FCB|B/G)\\s*\\d+|FCB/H)', re.I)
TOP_PATTERN = re.compile('(?P<mode>상위|하위|top|bottom)\\s*(?P<n>\\d+)\\s*(?:개|건)?', re.I)
THRESHOLD_PATTERN = re.compile('(?P<value>\\d+(?:\\.\\d+)?)\\s*(?P<unit>시간|개|건|%|퍼센트)?\\s*(?P<cmp>이상|이하|초과|미만)')
MCP_PREFIX_PATTERN = re.compile('(?<![A-Z0-9])(?P<prefix>[A-Z]\\s*-\\s*\\d{2,})(?=(?:\\s|로|으|인|제|$))', re.I)
LEAD_PATTERN = re.compile('(?<![A-Z0-9])F(?P<lead>\\d{2,4})(?![A-Z0-9])', re.I)
DESCRIPTOR_TOKEN_PATTERN = re.compile('(?<![A-Z0-9])(?P<token>[A-Z][A-Z0-9/-]*|\\d{2,4}G|\\d{2,4})(?![A-Z0-9])', re.I)

def normalize_text(value: str) -> str:
    return re.sub('\\s+', ' ', unicodedata.normalize('NFKC', str(value or '')).strip())

def _reference_datetime(value: str | datetime | None, timezone_name: str) -> datetime:
    zone = ZoneInfo(timezone_name)
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value or '').strip()
        if not text:
            parsed = datetime.now(zone)
        else:
            parsed = datetime.fromisoformat(text.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=zone)
    return parsed.astimezone(zone)

def extract_date_candidates(question: str, reference_instant: str | datetime | None, timezone_name: str='Asia/Seoul') -> list[dict[str, Any]]:
    text = normalize_text(question)
    reference = _reference_datetime(reference_instant, timezone_name)
    candidates: list[dict[str, Any]] = []
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            groups = match.groupdict()
            year = int(groups.get('y') or reference.year)
            try:
                parsed = date(year, int(groups['m']), int(groups['d']))
            except ValueError:
                raise ContractError('intent_contract_error', 'request_capsule', '질문의 날짜가 올바르지 않습니다.', {'evidence': match.group(0)})
            candidates.append({'candidate_id': f'date:{parsed.isoformat()}', 'value_type': 'LocalDate', 'value': parsed.isoformat(), 'evidence': {'text': match.group(0), 'start': match.start(), 'end': match.end()}, 'resolution': 'explicit'})
    relative_terms = (('오늘', 0), ('금일', 0), ('어제', -1), ('전일', -1))
    for term, offset in relative_terms:
        for match in re.finditer(re.escape(term), text, flags=re.I):
            parsed = reference.date() + timedelta(days=offset)
            candidates.append({'candidate_id': f'date:{parsed.isoformat()}:{term}', 'value_type': 'LocalDate', 'value': parsed.isoformat(), 'evidence': {'text': match.group(0), 'start': match.start(), 'end': match.end()}, 'resolution': 'relative', 'reference_instant': reference.isoformat(), 'offset_days': offset})
    unique: dict[tuple[str, int, int], dict[str, Any]] = {}
    for candidate in candidates:
        evidence = candidate['evidence']
        unique[candidate['value'], evidence['start'], evidence['end']] = candidate
    return sorted(unique.values(), key=lambda item: (item['evidence']['start'], item['candidate_id']))

def extract_literal_candidates(question: str) -> dict[str, list[dict[str, Any]]]:
    text = normalize_text(question)
    result: dict[str, list[dict[str, Any]]] = {'rank': [], 'threshold': [], 'product_token': [], 'ordered_range': []}
    for match in TOP_PATTERN.finditer(text):
        mode_text = match.group('mode').casefold()
        mode = 'top' if mode_text in {'상위', 'top'} else 'bottom'
        result['rank'].append({'candidate_id': f"rank:{mode}:{int(match.group('n'))}:{match.start()}", 'mode': mode, 'limit': int(match.group('n')), 'evidence': {'text': match.group(0), 'start': match.start(), 'end': match.end()}})
    comparison_map = {'이상': 'gte', '이하': 'lte', '초과': 'gt', '미만': 'lt'}
    for match in THRESHOLD_PATTERN.finditer(text):
        result['threshold'].append({'candidate_id': f'threshold:{match.start()}', 'operator': comparison_map[match.group('cmp')], 'value': float(match.group('value')), 'unit': match.group('unit') or '', 'evidence': {'text': match.group(0), 'start': match.start(), 'end': match.end()}})
    for match in MCP_PREFIX_PATTERN.finditer(text):
        prefix = re.sub('\\s+', '', match.group('prefix')).upper()
        result['product_token'].append({'candidate_id': f'token:MCP_NO:starts_with:{prefix}', 'field': 'MCP_NO', 'operator': 'starts_with', 'value': prefix, 'evidence': {'text': match.group(0), 'start': match.start(), 'end': match.end()}})
    for match in LEAD_PATTERN.finditer(text):
        result['product_token'].append({'candidate_id': f"token:LEAD:eq:{match.group('lead')}", 'field': 'LEAD', 'operator': 'eq', 'value': match.group('lead'), 'evidence': {'text': match.group(0), 'start': match.start(), 'end': match.end()}})
    result['product_token'].extend(extract_product_descriptor_tokens(text, result['product_token']))
    for match in RANGE_PATTERN.finditer(text):
        start = re.sub('\\s+', '', match.group('start')).upper()
        end = re.sub('\\s+', '', match.group('end')).upper()
        result['ordered_range'].append({'candidate_id': f'process_range:{start}:{end}', 'start': start, 'end': end, 'inclusive': True, 'evidence': {'text': match.group(0), 'start': match.start(), 'end': match.end()}})
    return result

def extract_product_descriptor_tokens(question: str, existing: list[dict[str, Any]] | None=None) -> list[dict[str, Any]]:
    """Parse registered product-token shapes described by the natural-domain guide."""
    text = normalize_text(question)
    product_index = text.find('제품')
    if product_index < 0:
        return []
    left = text[:product_index]
    boundary = max(left.rfind('공정에서'), left.rfind('공정'), left.rfind('에서'))
    if boundary < 0:
        segment_start = 0
    elif left[boundary:].startswith('공정에서'):
        segment_start = boundary + len('공정에서')
    elif left[boundary:].startswith('공정'):
        segment_start = boundary + len('공정')
    else:
        segment_start = boundary + len('에서')
    segment = left[segment_start:].strip()
    base_offset = text.find(segment, max(0, segment_start)) if segment else -1
    if not segment or base_offset < 0:
        return []
    reserved = {'INPUT', 'OUTPUT', 'OUT', 'WIP', 'UPH', 'LOT', 'HOLD', 'DA', 'WB', 'FCB', 'BG', 'TOP', 'BOTTOM', 'MCP', 'NO', 'PKG', 'MOBILE', 'POP', 'HBM', 'AUTO', 'MODE', 'TECH', 'DEN', 'LEAD', 'DEVICE', 'OPER', 'OPER_NAME', 'PRODUCTION', 'PRODUCTION_QTY', 'INPUT_QTY', 'OUT_QTY', 'YIELD_RATE'}
    existing_markers = {(str(item.get('field')), str(item.get('operator')), str(item.get('value'))) for item in existing or []}
    result: list[dict[str, Any]] = []
    for match in DESCRIPTOR_TOKEN_PATTERN.finditer(segment):
        raw = match.group('token')
        token = raw.upper()
        field = ''
        if re.fullmatch('\\d{2,4}G', token):
            field = 'DEN'
        elif re.fullmatch('(?:LP)?DDR\\d[A-Z0-9]*', token) or re.fullmatch('HBM\\d+[A-Z0-9]*', token):
            field = 'MODE'
        elif token.endswith('BGA'):
            field = 'PKG_TYPE1'
        elif token in {'SDP', 'DDP', 'TSV'}:
            field = 'PKG_TYPE2'
        elif re.fullmatch('\\d{2,4}', token):
            field = 'LEAD'
        elif re.fullmatch('[A-Z]{1,4}', token) and token not in reserved:
            field = 'TECH'
        if not field:
            continue
        value = token
        marker = (field, 'eq', value)
        if marker in existing_markers:
            continue
        existing_markers.add(marker)
        start = base_offset + match.start()
        result.append({'candidate_id': f'token:{field}:eq:{value}:{start}', 'field': field, 'operator': 'eq', 'value': value, 'evidence': {'text': raw, 'start': start, 'end': base_offset + match.end()}})
    if result and (not any((item.get('field') in {'TECH', 'DEN', 'MODE', 'PKG_TYPE1', 'PKG_TYPE2'} for item in result))):
        return []
    return result

def build_request_capsule(question: str, *, session_id: str, subject_id: str, reference_instant: str | datetime | None, timezone_name: str='Asia/Seoul', previous_state_ref: str='', upstream_result_ref: str='') -> dict[str, Any]:
    normalized = normalize_text(question)
    if not normalized:
        raise ContractError('intent_contract_error', 'request_capsule', '질문을 입력해 주세요.')
    request_id = f'request:{sha256_json([subject_id, session_id, normalized, str(reference_instant)])[:24]}'
    typed_candidates: list[dict[str, Any]] = []
    for item in extract_date_candidates(normalized, reference_instant, timezone_name):
        evidence = item.get('evidence') or {}
        typed_candidates.append({'id': str(item.get('candidate_id')), 'kind': 'date', 'source_span': f"{int(evidence.get('start') or 0)}:{int(evidence.get('end') or 0)}", 'value': {key: value for key, value in item.items() if key not in {'candidate_id', 'evidence'}}, 'resolver_version': 'request-literals.v1'})
    for kind, values in extract_literal_candidates(normalized).items():
        for item in values:
            evidence = item.get('evidence') or {}
            typed_candidates.append({'id': str(item.get('candidate_id')), 'kind': str(kind), 'source_span': f"{int(evidence.get('start') or 0)}:{int(evidence.get('end') or 0)}", 'value': {key: value for key, value in item.items() if key not in {'candidate_id', 'evidence'}}, 'resolver_version': 'request-literals.v1'})
    capsule = {'contract_version': 'request.capsule.v1', 'request_id': request_id, 'question': normalized, 'owner_subject_id': str(subject_id or 'anonymous'), 'session_id': str(session_id or 'default'), 'reference_instant': _reference_datetime(reference_instant, timezone_name).isoformat(), 'timezone': timezone_name, 'literal_candidates': typed_candidates, 'state_ref': str(upstream_result_ref or previous_state_ref or '') or None}
    return bounded(capsule, 12 * 1024, 'request_capsule')

def candidate_span_matches(text: str, alias: str) -> list[tuple[int, int]]:
    """Boundary-aware longest matching primitive used by metadata candidates."""
    normalized = normalize_text(text)
    target = normalize_text(alias)
    if not target:
        return []
    pattern = re.compile(f'(?<![0-9A-Za-z_가-힣]){re.escape(target)}(?![0-9A-Za-z_가-힣])', re.I)
    return [(match.start(), match.end()) for match in pattern.finditer(normalized)]


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


EMBEDDED_SCHEMAS = json.loads('{"analysis-result.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/analysis-result.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"columns":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"contract_version":{"const":"analysis.result.v1","type":"string"},"lineage":{"$ref":"#/$defs/jsonObject"},"operation_trace":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"plan_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"result_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"row_count":{"minimum":0,"type":"integer"},"rows":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":100000,"type":"array"},"status":{"enum":["ok","empty","partial"],"type":"string"}},"required":["contract_version","status","plan_id","columns","rows","row_count","lineage","operation_trace","result_sha256"],"title":"analysis.result.v1","type":"object"},"executed-result.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/executed-result.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"analysis_result_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"columns":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"contract_version":{"const":"executed.result.v1","type":"string"},"criteria":{"$ref":"#/$defs/jsonObject"},"entities":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"executed_result_contract_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"grain":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"lineage":{"$ref":"#/$defs/jsonObject"},"operation_trace":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"plan_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"result_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"row_count":{"minimum":0,"type":"integer"},"rows":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":100000,"type":"array"},"source_snapshot_sha256":{"items":{"pattern":"^[0-9a-f]{64}$","type":"string"},"maxItems":32,"type":"array"},"status":{"enum":["ok","empty","partial"],"type":"string"}},"required":["contract_version","status","plan_id","columns","rows","row_count","lineage","operation_trace","result_sha256","grain","entities","criteria","source_snapshot_sha256","analysis_result_sha256","executed_result_contract_sha256"],"title":"executed.result.v1","type":"object"},"request-capsule.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/request-capsule.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"request.capsule.v1","type":"string"},"literal_candidates":{"items":{"additionalProperties":false,"properties":{"id":{"minLength":1,"type":"string"},"kind":{"minLength":1,"type":"string"},"resolver_version":{"minLength":1,"type":"string"},"source_span":{"minLength":1,"type":"string"},"value":{"$ref":"#/$defs/jsonValue"}},"required":["id","kind","source_span","value","resolver_version"],"type":"object"},"maxItems":64,"type":"array"},"owner_subject_id":{"minLength":1,"type":"string"},"question":{"minLength":1,"type":"string"},"reference_instant":{"format":"date-time","type":"string"},"request_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"session_id":{"minLength":1,"type":"string"},"state_ref":{"anyOf":[{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},{"type":"null"}]},"timezone":{"minLength":1,"type":"string"}},"required":["contract_version","request_id","question","owner_subject_id","session_id","reference_instant","timezone","literal_candidates","state_ref"],"title":"request.capsule.v1","type":"object"}}')



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



import builtins
import os

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, IntInput, MessageInput, Output, SecretStrInput, StrInput
from lfx.schema.data import Data


def _secret_text(value):
    if hasattr(value, "get_secret_value"):
        value = value.get_secret_value()
    return str(value or "").strip()


def _message_context(value):
    text = str(getattr(value, "text", value) or "").strip()
    data = getattr(value, "data", None)
    data = data if isinstance(data, dict) else {}
    metadata_candidates = []
    for name in ("a2a_metadata", "framework2_metadata", "metadata"):
        candidate = getattr(value, name, None)
        if isinstance(candidate, dict):
            metadata_candidates.append(candidate)
        nested = data.get(name)
        if isinstance(nested, dict):
            metadata_candidates.append(nested)
    metadata = metadata_candidates[0] if metadata_candidates else {}
    session_id = str(getattr(value, "session_id", "") or data.get("session_id") or "")
    if not session_id:
        for candidate in metadata_candidates:
            session_id = str(candidate.get("session_id") or candidate.get("sessionId") or candidate.get("conversation_id") or candidate.get("thread_id") or "")
            if session_id:
                break
    upstream_ref = str(metadata.get("upstream_result_ref") or data.get("upstream_result_ref") or "")
    return text, session_id or "default", upstream_ref


def _shared_memory_store():
    key = "_metadata_driven_v6_pipeline_state_store_v1"
    store = getattr(builtins, key, None)
    if store is None or not all(hasattr(store, name) for name in ("load_state", "load_ref", "commit_execution")):
        store = InMemoryStateStore()
        setattr(builtins, key, store)
    return store


class RequestStateCapsule(Component):
    display_name = "02 요청 및 세션 상태 고정"
    description = "질문 원문과 인증된 세션 상태를 검증해 이후 노드가 사용하는 간결한 요청 컨텍스트로 고정합니다."
    icon = "scan-text"
    metadata = {"logical_stage": "request_state"}

    inputs = [
        MessageInput(name="input_message", display_name="사용자 질문", required=True, info="분석할 자연어 질문과 세션 식별 정보가 담긴 메시지입니다."),
        DataInput(name="domain_bundle", display_name="도메인 실행 번들", required=True, info="승인된 데이터셋·필드·지표 정의가 포함된 불변 도메인 번들입니다."),
        SecretStrInput(name="mongo_uri", display_name="MongoDB 연결 URI", value="", required=False, info="인증된 멀티턴 상태와 결과를 저장할 MongoDB 연결 문자열입니다."),
        StrInput(name="mongo_database", display_name="MongoDB 데이터베이스", value="datagov", info="세션 상태 및 결과 컬렉션이 위치한 데이터베이스 이름입니다."),
        StrInput(name="result_collection", display_name="분석 결과 컬렉션", value="agent_v6_result_store", info="불변 분석 결과를 저장하는 v6 전용 컬렉션입니다."),
        StrInput(name="state_collection", display_name="세션 상태 컬렉션", value="agent_v6_session_state", info="멀티턴 세션 상태를 저장하는 v6 전용 컬렉션입니다."),
        IntInput(name="mongo_timeout_ms", display_name="MongoDB 제한 시간(ms)", value=5000, info="MongoDB 연결 및 조회에 적용할 제한 시간(밀리초)입니다."),
        BoolInput(
            name="allow_anonymous_multiturn",
            display_name="익명 멀티턴 허용",
            value=False,
            advanced=True,
            info="신뢰된 단일 사용자 환경에서만 활성화합니다. 20자 이상의 추측 불가능한 session_id가 필요합니다.",
        ),
    ]
    outputs = [Output(name="request_context", display_name="검증된 요청 컨텍스트", method="build_context", types=["Data"])]

    def _state_collection_names(self):
        values = {
            "result_collection": str(getattr(self, "result_collection", "agent_v6_result_store") or "").strip(),
            "state_collection": str(getattr(self, "state_collection", "agent_v6_session_state") or "").strip(),
        }
        expected = {
            "result_collection": "agent_v6_result_store",
            "state_collection": "agent_v6_session_state",
        }
        if values != expected or len(set(values.values())) != 2:
            raise ContractError(
                "state_policy_mismatch",
                "state_store_config",
                "State collections are role-bound to the registered distinct v6-only names.",
                {"expected": expected, "actual": values},
            )
        return values

    def _state_store(self, subject_id, allow_anonymous_multiturn=False):
        collections = self._state_collection_names()
        uri = _secret_text(getattr(self, "mongo_uri", "")) or os.getenv("MONGODB_URI", "").strip()
        if subject_id == "anonymous":
            return _shared_memory_store() if allow_anonymous_multiturn else InMemoryStateStore()
        if not uri:
            return _shared_memory_store()
        return MongoStateStore(
            uri,
            database=str(getattr(self, "mongo_database", "") or os.getenv("MONGODB_DATABASE", "datagov")),
            result_collection=collections["result_collection"],
            state_collection=collections["state_collection"],
            timeout_ms=max(500, min(int(getattr(self, "mongo_timeout_ms", 5000)), 30000)),
        )

    def build_context(self) -> Data:
        context = {"contract_version": PIPELINE_VERSION, "ok": True, "stage": "request_state"}
        try:
            question, session_id, upstream_ref = _message_context(getattr(self, "input_message", None))
            runtime_session = str(getattr(getattr(self, "graph", None), "session_id", "") or getattr(self, "_session_id", "") or "")
            if session_id == "default" and runtime_session:
                session_id = runtime_session
            runtime_user = str(getattr(self, "user_id", "") or "").strip()
            subject_id = f"langflow:{runtime_user}" if runtime_user and runtime_user.lower() not in {"none", "null", "undefined"} else "anonymous"
            if not question:
                raise ContractError("request_invalid", "request", "질문이 비어 있습니다.")
            anonymous_multiturn_enabled = subject_id == "anonymous" and bool(
                getattr(self, "allow_anonymous_multiturn", False)
            )
            if anonymous_multiturn_enabled and (session_id == "default" or len(session_id.strip()) < 20):
                raise ContractError(
                    "request_invalid",
                    "request",
                    "anonymous multi-turn에는 20자 이상의 추측 불가능한 session_id가 필요합니다.",
                )
            domain_context = _require_context(getattr(self, "domain_bundle", None), "request_state")
            if not domain_context.get("ok"):
                context.update({"ok": False, "stage": domain_context.get("stage"), "error": domain_context.get("error")})
                return Data(data=context)
            domain_identity = domain_context.get("domain_bundle") if isinstance(domain_context.get("domain_bundle"), dict) else {}
            domain_id = str(domain_identity.get("domain_id") or "default")
            environment = str(domain_identity.get("environment") or "production")
            storage_session_id = f"{environment}:{domain_id}:{session_id}"
            state_mode = (
                "persistent_anonymous_opt_in"
                if anonymous_multiturn_enabled
                else "ephemeral_anonymous"
                if subject_id == "anonymous"
                else "persistent_authenticated"
            )
            state_policy_material = {
                "contract_version": "state.policy.v1",
                "mode": state_mode,
                "subject_id": subject_id,
                "storage_session_id": storage_session_id,
                "anonymous_multiturn_enabled": anonymous_multiturn_enabled,
            }
            state_policy = {**state_policy_material, "policy_sha256": sha256_json(state_policy_material)}
            timezone_name = "Asia/Seoul"
            store = self._state_store(subject_id, anonymous_multiturn_enabled)
            prior_state = store.load_state(subject_id, storage_session_id)
            prior_version = int(prior_state.get("state_version", 0)) if isinstance(prior_state, dict) else 0
            prior_ref = str(upstream_ref or (prior_state.get("executed_result_ref") if isinstance(prior_state, dict) else "") or "")
            prior_semantics = (((prior_state or {}).get("semantic_context") or {}).get("semantics") or {}) if isinstance(prior_state, dict) else {}
            prior_result = {}
            if prior_ref:
                prior_record = store.load_ref(prior_ref, subject_id, storage_session_id)
                prior_result = deepcopy(prior_record.get("payload") or {})
                contract = str(prior_result.get("contract_version") or "")
                schema = "executed-result.schema.json" if contract == "executed.result.v1" else "analysis-result.schema.json" if contract == "analysis.result.v1" else ""
                if not schema:
                    raise ContractError("state_reference_forbidden", "state_load", "후속 질문이 참조한 결과 계약을 사용할 수 없습니다.")
                validate_contract(prior_result, schema, stage="state_load")
            request = build_request_capsule(
                question,
                session_id=session_id,
                subject_id=subject_id,
                reference_instant=(
                    str(os.getenv("V6_VALIDATION_REFERENCE_INSTANT", "") or "")
                    if os.getenv("V6_VALIDATION_MODE", "") == "1"
                    else ""
                ) or None,
                timezone_name=timezone_name,
                previous_state_ref=prior_ref,
                upstream_result_ref=upstream_ref,
            )
            validate_contract(request, "request-capsule.schema.json", stage="request_contract")
            context.update(
                {
                    "request": request,
                    "trace_id": f"trace:{sha256_json(request)[:24]}",
                    "subject_id": subject_id,
                    "session_id": session_id,
                    "storage_session_id": storage_session_id,
                    "anonymous_multiturn_enabled": anonymous_multiturn_enabled,
                    "state_policy": state_policy,
                    "domain_identity": {key: domain_identity.get(key) for key in ("domain_id", "environment", "revision", "catalog_sha256", "package_sha256", "bundle_sha256")},
                    "prior_version": prior_version,
                    "prior_result": prior_result,
                    "prior_semantics": prior_semantics,
                    "route_telemetry": {"intent_llm_calls": 0, "fallback_used": False},
                }
            )
        except Exception as exc:
            context = _pipeline_error(context, exc, "request_state")
        return Data(data=context)
