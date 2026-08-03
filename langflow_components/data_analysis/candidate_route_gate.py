# -*- coding: utf-8 -*-
"""GENERATED standalone component: CandidateRouteGate.

Regenerate with tools/build_standalone_components.py.  Do not hand edit.
"""
from __future__ import annotations

import json

EMBEDDED_SOURCE_MANIFEST = json.loads('{"catalog_contract_version":"metadata.runtime.catalog.v1","catalog_declared_sha256":"1f8b6c1522b96425a6a46a3e4dfcf4c5b7c338c6bc0af3c2a0878806ea4a7f8e","catalog_file_sha256":"0b035cefd556b3c37b166e73270dee3e7070a2adf2dd56750b8e1015516bfcce","contract_version":"standalone.source.manifest.v1","reference_sources":{"contracts/schemas/active-domain-pointer.schema.json":"8ff3e114e106d0bc08c83e61947ac967c28cd5390cd0539cb1efdc64b82f9a61","contracts/schemas/analysis-plan.schema.json":"15dbb187f458d03ad4d55063eef898b862529dc68e9f64840d08ab20df9cfb76","contracts/schemas/analysis-result.schema.json":"06e92c0892ff5b209783332f33e4d4ed1855612470b088390e4501591f68065b","contracts/schemas/analysis-route.schema.json":"aadd7504e7f75329b8b6a50634261e073450e6d19d8e14d4a44196c0000e0c04","contracts/schemas/answer-facts.schema.json":"26c573be25f4fade355a37f2ab231f3e0aa8ac83445ee58020a99388648809ed","contracts/schemas/answer-sections.schema.json":"4c1d645c9927879e6a9e877def326ff045b5a01edaf48a566b935bc4734882ab","contracts/schemas/approval-event.schema.json":"4aa6b10eeb875538d00d6de564bdbe24eb093e8727ed57515cbadba63f13d7a9","contracts/schemas/config-registry.schema.json":"2f90dfb2b99e17faa9afecaf1f32295f6d713067aeca66c7dc1544c5713598e9","contracts/schemas/display-options.schema.json":"099ef7c371a2ac015cf7b59ae873d2ff749cdad7fa738bbcccc9b4838ea45866","contracts/schemas/domain-package.schema.json":"f39f433985180636bb3b6dfe054cfb8e63998acbe0112f7082a8233b619517f7","contracts/schemas/download-item.schema.json":"91efd43bf2db00bf5e85071fa2992679c3b2dc050251a5c82e839dcd7f5d4086","contracts/schemas/error-registry.schema.json":"f67a1ab5ef2568626d406cb9feb38acfbb6fc593fa04f3da063f8293da653b64","contracts/schemas/error.schema.json":"1a0c89cc1898a894b0490a59f286c68520c0f74be0811f6c06c4aa3e50fe5602","contracts/schemas/evidence-manifest.schema.json":"2805ed7cce742e96b5e10902b096fbec91e40a8aca7fde7bfe95c1d12a9668bb","contracts/schemas/executable-blueprint.schema.json":"e55dbe8faa2f1f2eb933b1548b2b1c37886a0911ceb4e70838427bac2327f14a","contracts/schemas/executed-result.schema.json":"eaba5818e5fb30e2a572f5a81488d9ba34032adcf3af55dfbb0d4287afc7e435","contracts/schemas/flow-inventory.schema.json":"cdce69d64a9df37a88e139a0fd0900d38d9475d2a8f13ff9a9b5c1bf0777b672","contracts/schemas/gaia-metadata.schema.json":"86d0a11a06a97d573b550a427d26abe9db6e897d3c46681f02e2427735e9f093","contracts/schemas/metadata-annotation-proposal.schema.json":"f0b227cc42a528d6e0b95f1c8c4a1bf6bbb6871d17d32c108d65b47d2b0ddc7f","contracts/schemas/metadata-authoring-draft.schema.json":"035c081be6a0fa719b3dcd589d9090071342b695fa61f80f6781441a4b14aee2","contracts/schemas/metadata-authoring-proposal.schema.json":"8ee3fc86d8f596c554443c16ad619822e63315ed8f2bfd06311987fc63322edd","contracts/schemas/metadata-authoring-response.schema.json":"da776b8a156d007c5bd95e86ad10cfb5a8ac7f06c2cae0c52aeb96b6a36415f6","contracts/schemas/metadata-bootstrap-dataset-ir.schema.json":"351260f7ed418b35f4ca1e5012a353b1d8f820ea21dfc8880483c193880af3b6","contracts/schemas/metadata-bootstrap-main-filter-ir.schema.json":"41c849c88b803d53af9c02c3d50127c47e8ee38e46d7b0a1ad0d09c3638e48fa","contracts/schemas/metadata-bundle.schema.json":"985ffe44974cf14d6c52a8188d54c3b209c00478e83888f00c359cd056d5dc81","contracts/schemas/metadata-envelope.schema.json":"9abca177e22b570f2158dace05256f671c0acbd054705dfe4f34611fbdae2048","contracts/schemas/model-profile.schema.json":"14345c16f629fc03a3de2cdd2fe469bef1fdc82cd2f93954ce1f4204ba82f356","contracts/schemas/operator-registry.schema.json":"acd003c6db66b470a2653fc8a97caaf3856c9d4cfd934bc0f27ef609787c2746","contracts/schemas/pending-metadata-write.schema.json":"af7a0593fafbdcea16f1212ba92484525626e43f2a25d91f9c310a80f5b37a4d","contracts/schemas/query-registry.schema.json":"8422a44035eb2a06381166d69a185036c698f581b17741a8c4686fbeea109040","contracts/schemas/registered-call.schema.json":"219a775c3a514501c66e077ef03a107a71f4d45af15aab2117c3cb1ab8f75811","contracts/schemas/registered-function-card.schema.json":"bc9ca8b01c90d2d11737f1a70586e9227510b67fdab26c8ae605d9e830170dfd","contracts/schemas/request-capsule.schema.json":"675e661653098288d6cc9e6e9b3599ed3bf3e05d6d592ac66d9ed46b9fd2afaf","contracts/schemas/resolved-candidate-bundle.schema.json":"a24b7d2fc3798f1dd69e1af94a7071eae8fb56d93a4191258953fd63b4211568","contracts/schemas/response.schema.json":"40c1e43f2228c04bb9ea652f1107a7ac202405c3321bc2c6af8dbc543b2e7b06","contracts/schemas/retrieval-job-bundle.schema.json":"e73cd6e6c50bb24b528111c36c410af3afe2fe3ff28d3d906cfe023263a12105","contracts/schemas/runtime-catalog-v2.schema.json":"3f7f6c5154c9e7922dd65490e9166ba0038c6a242258ec30d409d8a553948fed","contracts/schemas/semantic-intent-selection.schema.json":"a70c99e36060531fac9730c02f706ffa8d108b872c5abe0e2d05cafa459e6a75","contracts/schemas/semantic-intent.schema.json":"a743b7e26168dda04a7f46205fed67987a587cf3cce939cf57b228b099bfad53","contracts/schemas/source-bundle.schema.json":"a5330ef1b104df5dd0f19385b5e7994ee5469feffa110ee84087b7992258ea92","contracts/schemas/source-result.schema.json":"f342dcf0f948f7f99899335d83f302f2aaa38b05bb246eb06f9c1da0161f516c","contracts/schemas/trace.schema.json":"3f7cb2dd4e88b5f9f09695347ce42d8b98d5c4534d8fab41cca8ea1c9e3d484e","contracts/schemas/turn-state.schema.json":"688ad4f5ac1b133e60e3a2ef2bef56d0b18c87a41d2c6c236264285aeba32280","contracts/schemas/unsupported-telemetry.schema.json":"8c3675797be935d6fd52db2883d433d464df2fdecc5e0d52e795a5fa1e6c8439","contracts/schemas/validation-case.schema.json":"23304f969ca614324f7a74b52edc72c4e6753e76c476a77fc8db68f089941682","reference_runtime/authoring_blueprint.py":"9fc416a04e0da317586ad8abf9831bf650746a7f1907ad62fcaef4012327fe71","reference_runtime/authoring_source_manifest.py":"311bd68482e163a781bf11aa449587879f659fa9c36f7564129ecea44b88170c","reference_runtime/canonical.py":"338b8b013b9311f94d9b5ff7a3d5902576e9dfb88b40d72d37436025806c2d1d","reference_runtime/contracts.py":"5d16082db0bf437e537a24352834548e48e157a4c740659e9c9f1a0e46960d6e","reference_runtime/domain_authoring_patches.py":"4c78c72bc2412cbe78e74372b7c5af658ada8de1b8058b228f02d2b68b41c445","reference_runtime/domain_packages.py":"ae08de3501c92be10bd8f983fa710cc8e4cec6a40dd8051140ab754c9caac04a","reference_runtime/dummy_data.py":"c02824f9ddba81496d99a4b58bda8e6bedf0ce464d47abca682071ab24cae57d","reference_runtime/engine.py":"62df5f1a06c0a2765085826bec3e73f99f02da470850d180f2d7a53078c67606","reference_runtime/generic_v2_candidates.py":"95f5821b05d7d70f70ebd0339a316bcc1367b5499553319b8d8995df251a4c56","reference_runtime/generic_v2_planner.py":"142665c8050c9302830cedf45928a25b73cd34e80bec66de9ba77003209176d3","reference_runtime/metadata_collections.py":"c10d21cab4fdb54e95f1e23b262842be51d1b74f85aedda7b99a7d48f1a84857","reference_runtime/metadata_compiler.py":"99544e6094883b4241d010af2bec5d67e6205d34634ad46d6e2ee173107336e3","reference_runtime/plan_compiler.py":"6dc3bef703732a6cba6734f63970b22ecd599139067fa78a16bf5b3be003e735","reference_runtime/presenter.py":"fee16b71dfaf07be0d27fee14f47aa753ea71350165185071552ff0f30a31101","reference_runtime/registered_functions.py":"03f2ed1e2cb158eee5dd23cd99a408f14fdf3abea7fb630cfb31044cfe8f4d8e","reference_runtime/request_literals.py":"00493f9e342ab3065215805ae32f3068cb594209434bf280f2bb4f23c4be62ff","reference_runtime/source_contracts.py":"c43d8865ff045f4c26c5194262620a50961be5b56552c5cc6e7d580b2c11d7b0","reference_runtime/state_contracts.py":"5a03fff6684850361904add4e4d15ea578617d1fce20564119bbac175fb334ae","reference_runtime/typed_executor.py":"0c1fc3bbb055cd32d1da3446afab0aca5351e844536624ae9ab953c78c5dfe3b"}}')


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


import json
import re
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable

def load_runtime_catalog(path: str | Path | None=None) -> dict[str, Any]:
    return deepcopy(EMBEDDED_RUNTIME_CATALOG)

def _contains(text: str, phrase: str, policy: str='auto') -> list[tuple[int, int]]:
    target = normalize_text(phrase)
    if not target:
        return []
    if re.search('[가-힣]', target):
        return [(match.start(), match.end()) for match in re.finditer(re.escape(target), text, flags=re.I)]
    if re.search('[0-9A-Za-z_]', target):
        pattern = re.compile(f'(?<![0-9A-Za-z_]){re.escape(target)}(?![0-9A-Za-z_])', re.I)
        return [(match.start(), match.end()) for match in pattern.finditer(text)]
    if policy == 'substring' or (policy == 'auto' and re.search('[가-힣]', target) and (len(target) >= 2)):
        return [(match.start(), match.end()) for match in re.finditer(re.escape(target), text, flags=re.I)]
    return candidate_span_matches(text, target)

def _catalog_records(catalog: dict[str, Any], target_type: str) -> dict[str, Any]:
    """Build an alias view without mutating the hash-pinned catalog."""
    registry_names = {'metric': 'metrics', 'field': 'fields', 'process_group': 'process_groups', 'product_group': 'product_groups', 'recipe': 'recipes', 'dataset': 'datasets'}
    registry = catalog.get(registry_names.get(target_type, ''), {})
    records: dict[str, Any] = {str(key): deepcopy(value) if isinstance(value, dict) else {} for key, value in registry.items()} if isinstance(registry, dict) else {}
    alias_registry = catalog.get('aliases') if isinstance(catalog.get('aliases'), dict) else {}
    for alias_record in alias_registry.values():
        if not isinstance(alias_record, dict) or alias_record.get('target_type') != target_type:
            continue
        identity = str(alias_record.get('target_key') or '')
        if not identity:
            continue
        record = records.setdefault(identity, {})
        aliases = record.setdefault('aliases', [])
        seen = {str(item.get('text') if isinstance(item, dict) else item).casefold() for item in aliases}
        for value in alias_record.get('values', []):
            item = deepcopy(value) if isinstance(value, dict) else {'text': str(value)}
            item.setdefault('match', alias_record.get('match') or 'bounded_longest')
            if str(item.get('text') or '').casefold() not in seen:
                aliases.append(item)
            compact = re.sub('\\s+', '', str(item.get('text') or ''))
            if compact != str(item.get('text') or '') and re.search('[가-힣]', compact) and (compact.casefold() not in seen):
                aliases.append({**item, 'text': compact})
        record.setdefault('match_policy', alias_record.get('match') or 'bounded_longest')
    return records

def _process_records(catalog: dict[str, Any]) -> dict[str, Any]:
    records = _catalog_records(catalog, 'process_group')
    exact = _catalog_records(catalog, 'process')
    for identity, record in exact.items():
        value = str(record.get('value') or identity)
        record['members'] = [value]
        record['exact'] = True
        records[f'exact:{identity}'] = record
    return records

def _alias_candidates(text: str, records: dict[str, Any], candidate_type: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for identity, record in records.items():
        aliases = record.get('aliases') if isinstance(record.get('aliases'), list) else []
        for alias_value in aliases:
            alias = str(alias_value.get('text') if isinstance(alias_value, dict) else alias_value)
            priority = int(alias_value.get('priority', 100)) if isinstance(alias_value, dict) else 100
            policy = str(alias_value.get('match') or record.get('match_policy') or 'auto') if isinstance(alias_value, dict) else str(record.get('match_policy') or 'auto')
            for start, end in _contains(text, alias, policy):
                matches.append({'candidate_id': f'{candidate_type}:{identity}:{start}:{end}', 'candidate_type': candidate_type, 'identity': identity, 'alias': alias, 'priority': priority, 'evidence': {'text': text[start:end], 'start': start, 'end': end}})
    matches.sort(key=lambda item: (item['evidence']['start'], -(item['evidence']['end'] - item['evidence']['start']), -item['priority'], item['identity']))
    accepted: list[dict[str, Any]] = []
    occupied: list[tuple[int, int]] = []
    for item in matches:
        span = (item['evidence']['start'], item['evidence']['end'])
        if any((span[0] >= left and span[1] <= right for left, right in occupied)):
            continue
        accepted.append(item)
        occupied.append(span)
    return accepted

def _operation_applicable(text: str, spec: dict[str, Any]) -> bool:
    any_terms = [str(item) for item in spec.get('any', [])]
    all_terms = [str(item) for item in spec.get('all', [])]
    none_terms = [str(item) for item in spec.get('none', [])]
    any_ok = not any_terms or any((_contains(text, term) for term in any_terms))
    all_ok = all((_contains(text, term) for term in all_terms))
    none_ok = not any((_contains(text, term) for term in none_terms))
    return any_ok and all_ok and none_ok

def _dedupe_identities(candidates: list[dict[str, Any]]) -> list[str]:
    result: list[str] = []
    for candidate in candidates:
        identity = str(candidate.get('identity') or '')
        if identity and identity not in result:
            result.append(identity)
    return result

def _typed_literals(request: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    raw = request.get('literal_candidates')
    if isinstance(raw, dict):
        return deepcopy(raw.get(kind) or [])
    result: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict) or item.get('kind') != kind:
            continue
        value = deepcopy(item.get('value'))
        if isinstance(value, dict):
            value.setdefault('candidate_id', item.get('id'))
            value.setdefault('source_span', item.get('source_span'))
            result.append(value)
    return result

def _selected_date(request: dict[str, Any]) -> str:
    candidates = _typed_literals(request, 'date')
    explicit = [item for item in candidates if item.get('resolution') == 'explicit']
    selected = explicit[-1] if explicit else candidates[-1] if candidates else None
    if isinstance(selected, dict) and selected.get('value'):
        return str(selected['value'])
    return str(request.get('reference_instant') or '')[:10]

def _dimension_candidates(text: str, catalog: dict[str, Any]) -> list[str]:
    fields = _catalog_records(catalog, 'field')
    selected = _alias_candidates(text, fields, 'field')
    result: list[str] = []
    for candidate in selected:
        identity = str(candidate.get('identity') or '')
        roles = fields.get(identity, {}).get('roles') or []
        alias = str(candidate.get('alias') or '')
        if identity == 'OPER_NAME' and '별' not in alias and (alias.upper() != 'OPER_NAME'):
            continue
        if 'group' in roles and identity not in result:
            result.append(identity)
    if _has_any(text, ['제품별', '제품 중', '제품중', '제품 정보']):
        recipe = (catalog.get('recipes') or {}).get('product.standard', {})
        keys = [str(field) for field in ((recipe.get('grain') or {}).get('keys') or [] if isinstance(recipe, dict) else [])]
        result = [field for field in result if field not in keys]
        result.extend(keys)
    return result

def _field_candidates(text: str, catalog: dict[str, Any]) -> list[str]:
    fields = _catalog_records(catalog, 'field')
    result: list[str] = []
    for candidate in _alias_candidates(text, fields, 'field'):
        identity = str(candidate.get('identity') or '')
        alias = str(candidate.get('alias') or '')
        if identity == 'OPER_NAME' and '별' not in alias and (alias.upper() != 'OPER_NAME'):
            continue
        if identity and identity not in result:
            result.append(identity)
    return result

def _dataset_candidates(text: str, catalog: dict[str, Any]) -> list[str]:
    return _dedupe_identities(_alias_candidates(text, _catalog_records(catalog, 'dataset'), 'dataset'))

def _lot_ids(text: str) -> list[str]:
    reserved = {'ID', 'IDS', 'LIST', 'LOT', 'NO', 'NUMBER'}
    values: list[str] = []
    for match in re.finditer('(?<![0-9A-Za-z])LOT\\s+([0-9A-Za-z][0-9A-Za-z_-]*)', text, flags=re.I):
        value = match.group(1).upper()
        if value not in reserved and value not in values:
            values.append(value)
    return values

def _registered_boolean_where(text: str, field_ids: list[str], thresholds: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Compile the bounded boolean-filter grammar into a typed predicate tree."""
    clauses: list[dict[str, Any]] = []
    numeric_field = next((field for field in field_ids if field in {'YIELD_RATE', 'IN_TAT', 'CUM_TAT'}), '')
    if numeric_field and thresholds:
        threshold = thresholds[0]
        clauses.append({'field': numeric_field, 'operator': str(threshold.get('operator') or 'gte'), 'value': threshold.get('value'), 'semantic_type': 'number'})
    mode_match = re.search('\\bMODE\\s*(?:가|이)?\\s*([0-9A-Za-z_-]+)', text, flags=re.I)
    if mode_match and 'MODE' in field_ids:
        clauses.append({'field': 'MODE', 'operator': 'eq', 'value': mode_match.group(1), 'semantic_type': 'string'})
    blank_field = next((field for field in field_ids if re.search(f'\\b{re.escape(field)}\\s*(?:가|이)?\\s*비어\\s*있는', text, flags=re.I)), '')
    blank_clause = {'field': blank_field, 'operator': 'null_or_blank', 'semantic_type': 'string'} if blank_field else None
    if not clauses and (not blank_clause):
        return None
    left: dict[str, Any] = clauses[0] if len(clauses) == 1 else {'op': 'all', 'clauses': clauses}
    if blank_clause:
        return {'op': 'any', 'clauses': [left, blank_clause]}
    return left

def _source_scoped_process_refs(metric_candidates: list[dict[str, Any]], process_candidates: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Bind process evidence to the metric clause that immediately follows it.

    This preserves source-specific conditions in questions such as
    "FCB production and W/B2 WIP".  A later metric with no new process evidence
    inherits the previous clause, which covers "W/B production and morning WIP".
    """
    ordered_metrics = sorted(metric_candidates, key=lambda item: int((item.get('evidence') or {}).get('start') or 0))
    ordered_processes = sorted(process_candidates, key=lambda item: int((item.get('evidence') or {}).get('start') or 0))
    result: dict[str, list[str]] = {}
    previous_end = 0
    inherited: list[str] = []
    for metric in ordered_metrics:
        metric_start = int((metric.get('evidence') or {}).get('start') or 0)
        local = [str(item.get('identity') or '') for item in ordered_processes if previous_end <= int((item.get('evidence') or {}).get('start') or 0) < metric_start]
        local = [value for index, value in enumerate(local) if value and value not in local[:index]]
        if local:
            inherited = local
        identity = str(metric.get('identity') or '')
        if identity and inherited:
            result[identity] = deepcopy(inherited)
        previous_end = int((metric.get('evidence') or {}).get('end') or metric_start)
    return result

def _build_semantics(request: dict[str, Any], catalog: dict[str, Any], analysis_kind: str, metric_ids: list[str], process_ids: list[str], product_group_ids: list[str]) -> dict[str, Any]:
    text = str(request.get('question') or '')
    metric_ids = list(metric_ids)
    if analysis_kind == 'hold_history' and _has_any(text, ['HOLD 시간', 'Hold 시간', '오래된']):
        if 'HOLD_DURATION_HOURS' not in metric_ids:
            metric_ids.append('HOLD_DURATION_HOURS')
    rank_candidates = _typed_literals(request, 'rank')
    threshold_candidates = _typed_literals(request, 'threshold')
    token_candidates = _typed_literals(request, 'product_token')
    range_candidates = _typed_literals(request, 'ordered_range')
    upper = text.upper()
    inferred_rank = deepcopy(rank_candidates[0]) if rank_candidates else None
    if inferred_rank is None and _has_any(text, ['가장 많은', '가장 큰', '최댓값', '최대값']):
        inferred_rank = {'mode': 'top', 'limit': 1}
    elif inferred_rank is None and _has_any(text, ['가장 적은', '가장 작은']):
        inferred_rank = {'mode': 'bottom', 'limit': 1}
    sort_spec = None
    if _has_any(text, ['큰 순서', '많은 순', '내림차순', '많은 제품']):
        sort_spec = {'field': metric_ids[-1] if metric_ids else '', 'direction': 'desc'}
    elif _has_any(text, ['작은 순서', '적은 순', '낮은 순', '오름차순']):
        sort_spec = {'field': metric_ids[-1] if metric_ids else '', 'direction': 'asc'}
    rank_segments = [deepcopy(item) for item in rank_candidates]
    if _has_any(text, ['잘 나간']) and (not rank_segments):
        inferred_rank = {'mode': 'top', 'limit': 3}
        rank_segments = [deepcopy(inferred_rank)]
    field_ids = _field_candidates(text, catalog)
    boolean_where = _registered_boolean_where(text, field_ids, threshold_candidates)
    comparison_operator = 'gt'
    if _has_any(text, ['보다 작은', '보다 적']):
        comparison_operator = 'lt'
    elif _has_any(text, ['보다 크거나 같은', '이상']):
        comparison_operator = 'gte'
    elif _has_any(text, ['보다 작거나 같은', '이하']):
        comparison_operator = 'lte'
    dimensions = _dimension_candidates(text, catalog)
    equipment_view = ''
    if analysis_kind == 'uph_detail' and 'UPH' in metric_ids:
        equipment_view = 'uph_detail'
        dimensions = ['EQP_MODEL', 'RECIPE_ID', 'OPER_NAME']
    elif analysis_kind == 'equipment_grouped':
        equipment_view = 'equipment_grouped'
        dimensions = ['EQP_MODEL', 'RECIPE_ID']
        if 'EQP_COUNT' not in metric_ids:
            metric_ids.append('EQP_COUNT')
    product_recipe = (catalog.get('recipes') or {}).get('product.standard', {})
    product_dimensions = [str(item) for item in (product_recipe.get('grain') or {}).get('keys') or []]
    product_default_kinds = {'aggregate', 'join', 'presence', 'formula', 'rank', 'group_rank', 'multi_metric_argmax', 'top_bottom', 'field_compare', 'equipment_enrich'}
    explicit_product_scope = bool(product_group_ids or token_candidates) or _has_any(text, ['제품별', '제품 별', '제품 중', '제품중', '제품의', '제품을', '제품과', 'Device', 'DEVICE'])
    if not dimensions and metric_ids and (analysis_kind == 'aggregate') and process_ids and (not explicit_product_scope):
        dimensions = ['OPER_NAME']
    if not dimensions and metric_ids and (analysis_kind in product_default_kinds):
        dimensions = deepcopy(product_dimensions)
    if len(process_ids) >= 2 and metric_ids and ('OPER_NAME' not in dimensions):
        dimensions.insert(0, 'OPER_NAME')
    qualitative_extreme = inferred_rank is not None and (not rank_candidates) and (int(inferred_rank.get('limit') or 0) == 1)
    return {'analysis_kind': analysis_kind, 'metric_refs': metric_ids, 'dimension_refs': dimensions, 'field_refs': field_ids, 'dataset_refs': _dataset_candidates(text, catalog), 'process_refs': process_ids, 'product_group_refs': product_group_ids, 'date': _selected_date(request), 'date_explicit': bool(_typed_literals(request, 'date')), 'reference_date': str(request.get('reference_instant') or '')[:10], 'reference_instant': str(request.get('reference_instant') or ''), 'rank': inferred_rank, 'rank_segments': rank_segments, 'tie_policy': 'include_all' if inferred_rank and (_has_any(text, ['동점', '모두']) or qualitative_extreme) else 'exact_n', 'thresholds': deepcopy(threshold_candidates), 'product_tokens': deepcopy(token_candidates), 'ordered_range': deepcopy(range_candidates[0]) if range_candidates else None, 'sort': sort_spec, 'lot_ids': _lot_ids(text), 'where': boolean_where, 'comparison_operator': comparison_operator, 'followup': bool(request.get('state_ref')), 'qualifiers': {'current_hold': 'HOLD' in upper and _has_any(text, ['현재', 'Hold 된', 'HOLD LOT', 'Hold Lot']), 'hold_history': 'HOLD' in upper and _has_any(text, ['이력', '히스토리', '오래된']), 'equipment': _has_any(text, ['장비', '설비', 'Recipe', 'RECIPE']), 'equipment_view': equipment_view, 'detail': _has_any(text, ['목록', 'LIST', 'Lot ID', 'LOT 알려', '보여줘']), 'preserve_blank_product': _has_any(text, ['제품 정보가 비어', '제품정보가 비어', '비어 있는 제품 정보']), 'fill_metric_zero': _has_any(text, ['생산량이 비어 있으면 0', '수량이 비어 있으면 0', '실적이 비어 있으면 0'])}}

def _has_any(text: str, values: list[str]) -> bool:
    return any((_contains(text, value) for value in values))

def _analysis_kinds(text: str, request: dict[str, Any], metric_ids: list[str], field_ids: list[str]) -> list[str]:
    """Closed grammar over registered metrics/fields; it never creates code."""
    literals = {'rank': _typed_literals(request, 'rank')}
    if request.get('state_ref') and _has_any(text, ['그중']):
        return ['previous_rank']
    if request.get('state_ref') and _has_any(text, ['이 제품들']) and _has_any(text, ['장비', '설비']):
        return ['equipment_enrich']
    if _has_any(text, ['같지만', '서로 다른', '다른 제품']):
        return ['compare_group_attributes']
    if _has_any(text, ['데이터에서']) and _has_any(text, ['컬럼만', '컬럼을', '컬럼']):
        return ['projection']
    if 'UPH' in text.upper() and _has_any(text, ['Recipe', 'RECIPE']) and _has_any(text, ['장비 모델', '장비 기종', '설비 모델', '설비 기종']):
        return ['uph_detail']
    if _has_any(text, ['조합별', '조합 별']) and _has_any(text, ['배정된 장비', '할당된 장비']) and _has_any(text, ['Recipe', 'RECIPE']):
        return ['equipment_grouped']
    if _has_any(text, ['중복된', '중복 그룹', '중복된 그룹']):
        return ['duplicate_groups']
    if _has_any(text, ['각 컬럼별', '각각의 컬럼', '컬럼별로']) and len(metric_ids) >= 2 and _has_any(text, ['가장 큰', '최댓값', '최대값']):
        return ['multi_metric_argmax']
    rank_modes = {str(item.get('mode') or '') for item in _typed_literals(request, 'rank')}
    if {'top', 'bottom'}.issubset(rank_modes):
        return ['top_bottom']
    if len(metric_ids) >= 2 and _has_any(text, ['보다 큰 행', '보다 작은 행', '보다 많', '보다 적']):
        return ['field_compare']
    if _has_any(text, ['left join', 'LEFT JOIN', '레프트 조인']) and _has_any(text, ['장비배정', '장비 배정']):
        return ['production_equipment_join']
    if _has_any(text, ['이상이고', '이하이고', '초과이고', '미만이고', '비어 있는 행', '비어있는 행']) and (not _has_any(text, ['제외하지', '제외하지 말'])):
        return ['boolean_filter']
    if not metric_ids and _has_any(text, ['수량', '현황']) and _has_any(text, ['별', '보여']):
        return ['clarification']
    if 'HOLD' in text.upper() and _has_any(text, ['이력', '히스토리', '오래된']):
        return ['hold_history']
    if 'UPH' in text.upper():
        return ['uph']
    if _has_any(text, ['할당된 장비', '배정된 장비', '장비 대수', '장비 LIST', '장비 목록']):
        return ['equipment_enrich'] if metric_ids and 'PRODUCTION_QTY' in metric_ids else ['equipment_detail']
    if _has_any(text, ['달성률', '계획 대비 실제', '목표 대비 실적']):
        return ['formula']
    if _has_any(text, ['있으나', '있지만', '있고']) and _has_any(text, ['없는', '없음', '없으나']):
        return ['presence']
    if literals.get('rank') or _has_any(text, ['가장 많은', '가장 적은', '가장 큰', '가장 작은', '최댓값', '최대값', '잘 나간']):
        if literals.get('rank') and field_ids and _has_any(text, ['별']):
            return ['group_rank']
        return ['rank']
    if 'HOLD' in text.upper() or _has_any(text, ['LOT 알려', 'LOT 목록', 'LOT LIST', 'LOT와', 'LOT ID']):
        return ['detail']
    if metric_ids and _has_any(text, ['실적이 있는 Device', '실적이 있는 DEVICE', '있는 Device', '있는 DEVICE']):
        return ['metric_presence_detail']
    if len(metric_ids) >= 2 and set(metric_ids).issubset({'INPUT_PLAN_QTY', 'OUT_PLAN_QTY'}):
        return ['aggregate']
    if len(metric_ids) >= 2 or _has_any(text, ['비교해', '대비']):
        return ['join']
    if metric_ids:
        return ['aggregate']
    if field_ids:
        return ['detail']
    return []

def _followup_mode(text: str, request: dict[str, Any]) -> str:
    if not request.get('state_ref'):
        return 'none'
    if _has_any(text, ['그중', '이 제품들', '위 결과', '위의 결과', '어땠어', '이력을']):
        return 'referenced'
    return 'context_switch'

def _inherit_semantics(current: dict[str, Any], prior: dict[str, Any] | None, request: dict[str, Any], mode: str, prior_result: dict[str, Any] | None) -> dict[str, Any]:
    if mode != 'referenced' or not isinstance(prior, dict):
        current['followup_mode'] = mode
        return current
    merged = deepcopy(current)
    for key in ('metric_refs', 'process_refs', 'dimension_refs', 'field_refs'):
        if not merged.get(key):
            merged[key] = deepcopy(prior.get(key) or [])
    if not merged.get('product_group_refs'):
        merged['product_group_refs'] = deepcopy(prior.get('product_group_refs') or [])
    if not _typed_literals(request, 'date'):
        merged['date'] = prior.get('date') or merged.get('date')
        merged['reference_date'] = prior.get('reference_date') or merged.get('reference_date')
    if _has_any(str(request.get('question') or ''), ['위 결과', '제품별']):
        current_dimensions = current.get('dimension_refs') or []
        if current_dimensions:
            merged['dimension_refs'] = deepcopy(current_dimensions)
            merged['field_refs'] = deepcopy(current.get('field_refs') or [])
    if current.get('product_group_refs'):
        merged['product_group_refs'] = deepcopy(current['product_group_refs'])
    if current.get('rank'):
        merged['rank'] = deepcopy(current['rank'])
    rows = (prior_result or {}).get('rows') if isinstance(prior_result, dict) else []
    if merged.get('analysis_kind') == 'hold_history' and isinstance(rows, list):
        merged['prior_lot_ids'] = [str(row.get('LOT_ID')) for row in rows if isinstance(row, dict) and row.get('LOT_ID')][:100]
    merged['followup'] = True
    merged['followup_mode'] = 'referenced'
    return merged

def build_candidate_bundle(request: dict[str, Any], catalog: dict[str, Any], *, prior_semantics: dict[str, Any] | None=None, prior_result: dict[str, Any] | None=None) -> dict[str, Any]:
    text = normalize_text(str(request.get('question') or ''))
    unsupported_terms = ['예측해', '예측값', '원인 분석', '왜 발생', '최적화해']
    unsupported = [item for item in unsupported_terms if _contains(text, item)]
    metric_records = _catalog_records(catalog, 'metric')
    process_records = _process_records(catalog)
    product_records = _catalog_records(catalog, 'product_group')
    field_records = _catalog_records(catalog, 'field')
    metric_candidates = _alias_candidates(text, metric_records, 'metric')
    process_candidates = _alias_candidates(text, process_records, 'process')
    product_candidates = _alias_candidates(text, product_records, 'product_group')
    field_candidates = _alias_candidates(text, field_records, 'field')
    metric_ids = _dedupe_identities(metric_candidates)
    process_ids = _dedupe_identities(process_candidates)
    product_ids = _dedupe_identities(product_candidates)
    field_ids = _dedupe_identities(field_candidates)
    if _has_any(text, ['잘 나간']) and 'PRODUCTION_QTY' not in metric_ids:
        metric_ids.append('PRODUCTION_QTY')
    if _has_any(text, ['생산과', '생산 과']) and _has_any(text, ['재공', 'WIP']):
        if 'PRODUCTION_QTY' not in metric_ids:
            metric_ids.insert(0, 'PRODUCTION_QTY')
    if _has_any(text, ['현재·누적 TAT', '현재/누적 TAT', '현재 및 누적 TAT']):
        if 'IN_TAT' not in metric_ids:
            metric_ids.append('IN_TAT')
        if 'CUM_TAT' not in metric_ids:
            metric_ids.append('CUM_TAT')
    if _has_any(text, ['left join', 'LEFT JOIN', '레프트 조인']) and _has_any(text, ['장비배정', '장비 배정']):
        if 'PRODUCTION_QTY' not in metric_ids:
            metric_ids.insert(0, 'PRODUCTION_QTY')
        if 'EQP_COUNT' not in metric_ids:
            metric_ids.append('EQP_COUNT')
    followup_mode = _followup_mode(text, request)
    primary = _analysis_kinds(text, request, metric_ids, _field_candidates(text, catalog))
    if followup_mode == 'referenced' and _has_any(text, ['위 결과', '위의 결과']):
        primary = ['join']
    elif followup_mode == 'referenced' and product_ids and (not metric_ids):
        primary = ['aggregate', 'detail']
    candidates: list[dict[str, Any]] = []
    for kind in primary:
        semantics = _inherit_semantics(_build_semantics(request, catalog, kind, metric_ids, process_ids, product_ids), prior_semantics, request, followup_mode, prior_result)
        semantics['process_refs_by_metric'] = _source_scoped_process_refs(metric_candidates, process_candidates)
        if kind == 'production_equipment_join':
            semantics['metric_refs'] = ['PRODUCTION_QTY', 'EQP_COUNT']
        if kind == 'boolean_filter' and (not semantics.get('dataset_refs')):
            semantics['dataset_refs'] = ['product_master']
        candidate_id = f'intent:{kind}:{sha256_json(semantics)[:16]}'
        candidates.append({'candidate_id': candidate_id, 'description': kind, 'semantics': semantics, 'semantics_sha256': sha256_json(semantics)})
    ambiguity: list[dict[str, Any]] = []
    for candidate_group, label in ((metric_candidates, 'metric'), (process_candidates, 'process'), (product_candidates, 'product_group')):
        by_span: dict[tuple[int, int], set[str]] = {}
        for candidate in candidate_group:
            evidence = candidate['evidence']
            by_span.setdefault((evidence['start'], evidence['end']), set()).add(candidate['identity'])
        for span, identities in by_span.items():
            if len(identities) > 1:
                ambiguity.append({'type': label, 'span': list(span), 'identities': sorted(identities)})
    forced_llm_kinds = {'clarification'}
    forced_llm = any((kind in forced_llm_kinds for kind in primary)) or _has_any(text, ['잘 나간'])
    if unsupported:
        route = 'unsupported'
        reason = 'unsupported_registry_gap'
    elif ambiguity:
        route = 'intent_llm'
        reason = 'ambiguous_candidate_selection'
    elif not candidates:
        route = 'unsupported'
        reason = 'unsupported_registry_gap'
    elif forced_llm:
        route = 'intent_llm'
        reason = 'forced_equivalence_probe' if _has_any(text, ['잘 나간']) else 'ambiguous_candidate_selection' if primary == ['clarification'] else 'semantic_choice_required'
    elif len(primary) == 1 and len(candidates) == 1:
        route = 'deterministic'
        reason = 'unique_complete_selection'
    else:
        route = 'intent_llm'
        reason = 'semantic_choice_required'
    card_projection = [_intent_prompt_card(item) for item in candidates]
    bundle_material = {'request_id': request.get('request_id'), 'catalog_sha256': catalog.get('catalog_sha256'), 'metric_candidates': metric_candidates, 'process_candidates': process_candidates, 'product_group_candidates': product_candidates, 'field_candidates': field_candidates, 'intent_candidates': candidates}
    bundle_sha = sha256_json(bundle_material)
    decision_material = {'route': route, 'reason': reason, 'bundle_sha256': bundle_sha, 'candidate_ids': [item['candidate_id'] for item in candidates]}
    bundle = {'contract_version': 'resolved.candidate.bundle.v1', **bundle_material, 'bundle_sha256': bundle_sha, 'prompt_cards': card_projection, 'route_decision': {'contract_version': 'analysis.route.v1', 'route': route, 'reason_code': reason, 'resolved_candidate_bundle_sha256': bundle_sha, 'selected_candidate_ids': [item['candidate_id'] for item in candidates] if route == 'deterministic' else [], 'required_slots': [], 'unresolved_slots': ['intent_candidate_id'] if route == 'intent_llm' else ['registry_gap'] if route == 'unsupported' else [], 'ambiguity_sets': [item['identities'] for item in ambiguity], 'route_policy_version': 'route-policy.v1', 'eligibility_proof_sha256': sha256_json(decision_material)}, 'route_evidence': {'ambiguity': ambiguity, 'unsupported_signals': unsupported}}
    return bounded(bundle, 28 * 1024, 'candidate_bundle')

def _intent_prompt_card(candidate: dict[str, Any]) -> dict[str, Any]:
    """Project only the semantic distinctions needed by the intent selector.

    Candidate IDs and executable semantics remain sealed elsewhere. The model
    receives registered identifiers plus a compact result-shape policy so an
    elliptical follow-up cannot accidentally turn a grouped result into raw
    detail rows merely because both candidates share the same filters.
    """
    semantics = candidate.get('semantics') if isinstance(candidate.get('semantics'), dict) else {}
    analysis_kind = str(semantics.get('analysis_kind') or '')
    result_shape = {'aggregate': 'grouped_summary', 'rank': 'ranked_summary', 'detail': 'individual_rows', 'projection': 'selected_columns', 'clarification': 'clarification_required'}.get(analysis_kind, analysis_kind or 'registered_result')
    followup = bool(semantics.get('followup'))
    if followup and analysis_kind == 'aggregate':
        selection_policy = 'replace_newly_mentioned_filter_and_keep_previous_metric_date_dimensions_aggregation'
    elif followup and analysis_kind in {'detail', 'projection'}:
        selection_policy = 'switch_to_individual_rows_only_when_detail_rows_list_or_identifiers_are_explicit'
    elif analysis_kind == 'detail':
        selection_policy = 'individual_rows_require_an_explicit_detail_rows_list_or_identifier_request'
    else:
        selection_policy = 'match_the_question_to_this_registered_result_shape'
    return {'candidate_id': candidate.get('candidate_id'), 'description': candidate.get('description'), 'analysis_kind': analysis_kind, 'result_shape': result_shape, 'followup': followup, 'selection_policy': selection_policy, 'registered_metric_refs': list(semantics.get('metric_refs') or [])[:16], 'registered_dimension_refs': list(semantics.get('dimension_refs') or [])[:16], 'registered_product_group_refs': list(semantics.get('product_group_refs') or [])[:16]}

def normalize_intent_selection(request: dict[str, Any], bundle: dict[str, Any], *, selected_candidate_id: str | None=None, intent_llm_calls: int=0) -> tuple[dict[str, Any], dict[str, Any]]:
    """Normalize a preselected sealed candidate without invoking an LLM.

    Langflow runtime components use this boundary after the external Prompt
    Template/Conditional Invoker path.  Keeping provider invocation outside
    this function prevents prompt text and retry behavior from leaking into
    the standalone intent decoder.
    """
    route = bundle.get('route_decision') if isinstance(bundle.get('route_decision'), dict) else {}
    route_name = str(route.get('route') or '')
    candidates = bundle.get('intent_candidates') if isinstance(bundle.get('intent_candidates'), list) else []
    if route_name == 'unsupported':
        raise ContractError('unsupported_operation', 'route_eligibility', '등록된 metadata와 typed operator로 처리할 수 없는 질문입니다.', {'reason_code': route.get('reason_code')})
    if route_name == 'deterministic':
        if len(candidates) != 1:
            raise ContractError('intent_contract_error', 'intent_routing', 'deterministic 후보가 유일하지 않습니다.')
        if int(intent_llm_calls) != 0:
            raise ContractError('intent_contract_error', 'intent_decoding', 'deterministic 분기에서는 Intent LLM 호출 수가 0이어야 합니다.')
        selected_id = str(candidates[0].get('candidate_id') or '')
        calls = 0
    elif route_name == 'intent_llm':
        selected_id = str(selected_candidate_id or '')
        if not selected_id:
            raise ContractError('intent_contract_error', 'intent_decoding', 'Intent LLM candidate 선택값이 필요합니다.')
        calls = int(intent_llm_calls)
        if calls != 1:
            raise ContractError('intent_contract_error', 'intent_decoding', 'Intent LLM 호출 수는 정확히 1회여야 합니다.')
    else:
        raise ContractError('intent_contract_error', 'intent_routing', '알 수 없는 intent route입니다.')
    selected = next((item for item in candidates if item.get('candidate_id') == selected_id), None)
    if not isinstance(selected, dict):
        raise ContractError('intent_contract_error', 'intent_decoding', 'LLM이 candidate 목록 밖의 값을 선택했습니다.', {'candidate_id': selected_id})
    semantics = deepcopy(selected.get('semantics') or {})
    intent_material = {'contract_version': 'analysis.intent.v1', 'request_id': request.get('request_id'), 'candidate_bundle_sha256': bundle.get('bundle_sha256'), 'intent_candidate_id': selected_id, 'semantics': semantics}
    intent = {**intent_material, 'intent_sha256': sha256_json(intent_material)}
    telemetry = {'route': route_name, 'reason_code': route.get('reason_code'), 'intent_llm_calls': calls, 'fallback_used': False, 'eligibility_proof_sha256': route.get('eligibility_proof_sha256')}
    return (intent, telemetry)

def _metric_dataset(metric: dict[str, Any], requested_date: str, reference_date: str) -> tuple[str, str]:
    temporal = metric.get('temporal_contract') if isinstance(metric.get('temporal_contract'), dict) else {}
    selector = temporal.get('dataset_selector') if isinstance(temporal.get('dataset_selector'), dict) else {}
    query_time = temporal.get('query_time') if isinstance(temporal.get('query_time'), dict) else {}
    offset = int(query_time.get('offset_days') or 0)
    query_date = (date.fromisoformat(requested_date) + timedelta(days=offset)).isoformat()
    key = str(selector.get('dataset_key') or '')
    if not key:
        binding = metric.get('source_binding') if isinstance(metric.get('source_binding'), dict) else {}
        family = str(binding.get('dataset_family') or '')
        key = {'production': 'production_today' if requested_date == reference_date else 'production', 'wip': 'wip_today' if requested_date == reference_date else 'wip', 'target': 'target', 'equipment_uph': 'eqp_uph', 'equipment': 'equipment_assign', 'lot': 'lot_status', 'hold_history': 'hold_history'}.get(family, '')
    if not key:
        raise ContractError('metadata_dependency_error', 'plan_compilation', 'metric dataset binding이 없습니다.')
    return (key, query_date)

def _process_values(semantics: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    values: list[str] = []
    groups = _process_records(catalog)
    for identity in semantics.get('process_refs', []):
        record = groups.get(str(identity), {})
        for member in record.get('members', []):
            value = str(member.get('value') if isinstance(member, dict) else member)
            if value and value not in values:
                values.append(value)
    return values

def _product_clauses(semantics: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    clauses: list[dict[str, Any]] = []
    groups = catalog.get('product_groups') if isinstance(catalog.get('product_groups'), dict) else {}
    for identity in semantics.get('product_group_refs', []):
        predicate = groups.get(str(identity), {}).get('predicate')
        if isinstance(predicate, dict):
            clauses.append(deepcopy(predicate))
    for token in semantics.get('product_tokens', []):
        clauses.append({'field': token.get('field'), 'operator': token.get('operator'), 'value': token.get('value'), 'semantic_type': 'string'})
    return clauses

def _filter_fields(nodes: list[dict[str, Any]] | dict[str, Any]) -> list[str]:
    values = nodes if isinstance(nodes, list) else [nodes]
    result: list[str] = []
    for item in values:
        if not isinstance(item, dict):
            continue
        field = str(item.get('field') or '')
        if field and field not in result:
            result.append(field)
        for nested in _filter_fields(item.get('clauses') or []):
            if nested not in result:
                result.append(nested)
    return result

def _aggregate_operation(source_id: str, operation_id: str, dimensions: list[str], metric_id: str, metric: dict[str, Any]) -> dict[str, Any]:
    binding = metric.get('source_binding') if isinstance(metric.get('source_binding'), dict) else {}
    additivity = metric.get('additivity') if isinstance(metric.get('additivity'), dict) else {}
    default = str(additivity.get('default') or 'additive')
    function = 'sum' if default == 'additive' else 'nunique' if default == 'distinct' else 'mean'
    return {'id': operation_id, 'op': 'aggregate', 'input': source_id, 'group_by': dimensions, 'metrics': [{'field': binding.get('field'), 'function': function, 'as': metric_id, 'dropna': True}]}

def _finalize_plan(intent: dict[str, Any], bundle: dict[str, Any], catalog: dict[str, Any], jobs: list[dict[str, Any]], operations: list[dict[str, Any]], result_operation_id: str, columns: list[str], grain: list[str], lineage: dict[str, Any], *, input_refs: list[str] | None=None) -> dict[str, Any]:
    material = {'contract_version': 'analysis.plan.v1', 'intent_sha256': intent.get('intent_sha256'), 'candidate_bundle_sha256': bundle.get('bundle_sha256'), 'catalog_sha256': catalog.get('catalog_sha256'), 'retrieval_jobs': jobs, 'operations': operations, 'result_operation_id': result_operation_id, 'result_contract': {'columns': columns, 'ordering': [], 'grain': grain}, 'lineage': lineage}
    if input_refs:
        material['input_refs'] = list(dict.fromkeys((str(value) for value in input_refs if str(value))))
    normalized = deepcopy(material)
    normalized['retrieval_jobs'] = sorted(normalized['retrieval_jobs'], key=lambda item: item['job_id'])
    plan_hash = sha256_json(normalized)
    semantic_material = {key: normalized[key] for key in ('catalog_sha256', 'input_refs', 'retrieval_jobs', 'operations', 'result_operation_id', 'result_contract', 'lineage') if key in normalized}
    return {**material, 'plan_id': f'plan:{plan_hash}', 'plan_fingerprint': sha256_json(semantic_material)}

def _range_process_values(ordered_range: dict[str, Any] | None, catalog: dict[str, Any]) -> list[str]:
    if not isinstance(ordered_range, dict):
        return []
    rows = [item for item in catalog.get('process_order', []) if isinstance(item, dict)]
    lookup: dict[str, int] = {}
    for item in rows:
        for name in [item.get('oper_name'), *(item.get('aliases') or [])]:
            lookup[normalize_text(str(name)).upper()] = int(item.get('oper_seq') or 0)
    start = lookup.get(normalize_text(str(ordered_range.get('start'))).upper())
    end = lookup.get(normalize_text(str(ordered_range.get('end'))).upper())
    if start is None or end is None:
        raise ContractError('plan_contract_error', 'plan_compilation', '공정 범위 endpoint가 metadata에 없습니다.')
    low, high = sorted((start, end))
    return [str(item.get('oper_name')) for item in rows if low <= int(item.get('oper_seq') or 0) <= high]

def _compile_operator_special_plan(intent: dict[str, Any], bundle: dict[str, Any], catalog: dict[str, Any], semantics: dict[str, Any]) -> dict[str, Any] | None:
    """Compile closed operator applications that are not plain metric rollups."""
    kind = str(semantics.get('analysis_kind') or '')
    supported = {'projection', 'boolean_filter', 'duplicate_groups', 'metric_presence_detail', 'equipment_enrich', 'production_equipment_join'}
    if kind not in supported:
        return None
    datasets = catalog.get('datasets') if isinstance(catalog.get('datasets'), dict) else {}
    if kind == 'projection':
        dataset_key = next((value for value in semantics.get('dataset_refs', []) if value in datasets), 'production')
        dataset = datasets.get(dataset_key, {})
        available = set((dataset.get('fields') or {}).keys())
        fields = [str(field) for field in semantics.get('field_refs', []) if str(field) in available]
        if not fields:
            raise ContractError('plan_contract_error', 'plan_compilation', 'projection field가 등록되지 않았습니다.')
        job = {'job_id': f'job_1_{dataset_key}', 'dataset_key': dataset_key, 'source_type': str(dataset.get('source_type') or 'dummy'), 'parameters': {}, 'required_fields': fields, 'filters': None, 'requirement': 'required'}
        operations = [{'id': 'op_project', 'op': 'project', 'input': f"source:{job['job_id']}", 'fields': fields}]
        return _finalize_plan(intent, bundle, catalog, [job], operations, 'op_project', fields, fields, {'dataset_key': dataset_key})
    if kind == 'boolean_filter':
        dataset_key = 'product_master'
        dataset = datasets.get(dataset_key, {})
        available = set((dataset.get('fields') or {}).keys())
        fields = [field for field in ['DEVICE', 'YIELD_RATE', 'MODE', 'LEAD'] if field in available]
        where = semantics.get('where') if isinstance(semantics.get('where'), dict) else None
        if not where:
            raise ContractError('intent_contract_error', 'plan_compilation', 'boolean filter predicate가 완전하지 않습니다.')
        required = sorted(set(fields + _filter_fields(where)))
        job = {'job_id': 'job_1_product_master', 'dataset_key': dataset_key, 'source_type': str(dataset.get('source_type') or 'fixture'), 'parameters': {}, 'required_fields': required, 'filters': None, 'requirement': 'required'}
        operations = [{'id': 'op_filter', 'op': 'filter', 'input': 'source:job_1_product_master', 'where': where}, {'id': 'op_project', 'op': 'project', 'input': 'op_filter', 'fields': fields}]
        return _finalize_plan(intent, bundle, catalog, [job], operations, 'op_project', fields, ['DEVICE'], {'dataset_key': dataset_key})
    if kind == 'duplicate_groups':
        dataset_key = 'product_master'
        dataset = datasets.get(dataset_key, {})
        group_fields = [field for field in semantics.get('dimension_refs', []) if field in {'TECH', 'DEN', 'MODE', 'PKG_TYPE1', 'PKG_TYPE2', 'LEAD', 'MCP_NO'}]
        if not group_fields:
            raise ContractError('intent_contract_error', 'plan_compilation', '중복 판단 field가 없습니다.')
        detail_fields = [*group_fields, 'DEVICE']
        job = {'job_id': 'job_1_product_master', 'dataset_key': dataset_key, 'source_type': str(dataset.get('source_type') or 'fixture'), 'parameters': {}, 'required_fields': detail_fields, 'filters': None, 'requirement': 'required'}
        operations = [{'id': 'op_detail', 'op': 'project', 'input': 'source:job_1_product_master', 'fields': detail_fields}, {'id': 'op_dedupe_products', 'op': 'dedupe', 'input': 'op_detail', 'fields': ['DEVICE'], 'keep': 'first'}, {'id': 'op_duplicate_groups', 'op': 'find_duplicate_groups', 'input': 'op_dedupe_products', 'fields': group_fields, 'minimum_count': 2, 'count_field': 'GROUP_COUNT'}, {'id': 'op_duplicate_rows', 'op': 'join', 'left': 'op_dedupe_products', 'right': 'op_duplicate_groups', 'how': 'inner', 'key_mappings': [{'left': field, 'right': field} for field in group_fields], 'cardinality': 'many_to_one', 'null_key_policy': 'match', 'multi_match_policy': 'error', 'empty_side_policy': 'allow', 'output_fields': [*detail_fields, 'GROUP_COUNT']}, {'id': 'op_sort', 'op': 'sort', 'input': 'op_duplicate_rows', 'keys': [{'field': field, 'direction': 'asc', 'nulls': 'last'} for field in [*group_fields, 'DEVICE']]}]
        columns = [*detail_fields, 'GROUP_COUNT']
        return _finalize_plan(intent, bundle, catalog, [job], operations, 'op_sort', columns, group_fields, {'dataset_key': dataset_key})
    if kind == 'metric_presence_detail':
        metric_id = next((str(value) for value in semantics.get('metric_refs', []) if str(value) in (catalog.get('metrics') or {})), '')
        metric = (catalog.get('metrics') or {}).get(metric_id, {})
        dataset_key, query_date = _metric_dataset(metric, str(semantics.get('date')), str(semantics.get('reference_date')))
        dataset = datasets.get(dataset_key, {})
        available = set((dataset.get('fields') or {}).keys())
        binding = metric.get('source_binding') if isinstance(metric.get('source_binding'), dict) else {}
        clauses = deepcopy(binding.get('fixed_filters') or [])
        source_field = str(binding.get('field') or '')
        if source_field:
            clauses.append({'field': source_field, 'operator': 'gt', 'value': 0, 'semantic_type': 'number'})
        process_values = _process_values(semantics, catalog)
        if process_values and (not any((clause.get('field') == 'OPER_NAME' for clause in clauses if isinstance(clause, dict)))):
            clauses.append({'field': 'OPER_NAME', 'operator': 'in', 'values': process_values, 'semantic_type': 'string'})
        fields = [field for field in ['DEVICE'] if field in available]
        required = sorted(set(fields + [str(binding.get('field') or '')] + _filter_fields(clauses)))
        job = {'job_id': f'job_1_{dataset_key}', 'dataset_key': dataset_key, 'source_type': str(dataset.get('source_type') or 'dummy'), 'parameters': {'DATE': query_date}, 'required_fields': [field for field in required if field], 'filters': None, 'requirement': 'required'}
        source = f"source:{job['job_id']}"
        operations: list[dict[str, Any]] = []
        current = source
        if clauses:
            operations.append({'id': 'op_filter', 'op': 'filter', 'input': source, 'where': {'op': 'all', 'clauses': clauses}})
            current = 'op_filter'
        operations.extend([{'id': 'op_project', 'op': 'project', 'input': current, 'fields': fields}, {'id': 'op_dedupe', 'op': 'dedupe', 'input': 'op_project', 'fields': fields, 'keep': 'first'}, {'id': 'op_sort', 'op': 'sort', 'input': 'op_dedupe', 'keys': [{'field': 'DEVICE', 'direction': 'asc', 'nulls': 'last'}]}])
        return _finalize_plan(intent, bundle, catalog, [job], operations, 'op_sort', fields, fields, {metric_id: {'dataset_key': dataset_key}})
    if kind == 'equipment_enrich':
        product_keys = [str(field) for field in ((catalog.get('recipes') or {}).get('product.standard', {}).get('grain') or {}).get('keys') or []]
        production_key = 'production_today' if semantics.get('date') == semantics.get('reference_date') else 'production'
        equipment_key = 'equipment_assign'
        production = datasets.get(production_key, {})
        equipment = datasets.get(equipment_key, {})
        production_fields = set((production.get('fields') or {}).keys())
        equipment_fields = set((equipment.get('fields') or {}).keys())
        if not product_keys or not set(product_keys).issubset(production_fields & equipment_fields):
            raise ContractError('metadata_dependency_error', 'plan_compilation', '생산-장비 제품 grain 계약이 완전하지 않습니다.')
        process_values = _process_values(semantics, catalog)
        production_clauses = [clause for clause in _product_clauses(semantics, catalog) if set(_filter_fields(clause)).issubset(production_fields)]
        equipment_clauses = [clause for clause in _product_clauses(semantics, catalog) if set(_filter_fields(clause)).issubset(equipment_fields)]
        if process_values:
            production_clauses.append({'field': 'OPER_NAME', 'operator': 'in', 'values': process_values, 'semantic_type': 'string'})
            equipment_clauses.append({'field': 'OPER_NAME', 'operator': 'in', 'values': process_values, 'semantic_type': 'string'})
        jobs = [{'job_id': f'job_1_{production_key}', 'dataset_key': production_key, 'source_type': str(production.get('source_type') or 'dummy'), 'parameters': {'DATE': semantics.get('date')} if 'DATE' in (production.get('parameters') or {}) else {}, 'required_fields': sorted(set(product_keys + ['PRODUCTION_QTY'] + _filter_fields(production_clauses))), 'filters': None, 'requirement': 'required'}, {'job_id': 'job_2_equipment_assign', 'dataset_key': equipment_key, 'source_type': str(equipment.get('source_type') or 'dummy'), 'parameters': {}, 'required_fields': sorted(set(product_keys + ['EQP_ID'] + _filter_fields(equipment_clauses))), 'filters': None, 'requirement': 'required'}]
        operations: list[dict[str, Any]] = []
        production_input = f"source:{jobs[0]['job_id']}"
        if production_clauses:
            operations.append({'id': 'op_filter_production', 'op': 'filter', 'input': production_input, 'where': {'op': 'all', 'clauses': production_clauses}})
            production_input = 'op_filter_production'
        operations.append({'id': 'op_production_by_product', 'op': 'aggregate', 'input': production_input, 'group_by': product_keys, 'metrics': [{'field': 'PRODUCTION_QTY', 'function': 'sum', 'as': 'PRODUCTION_QTY', 'dropna': True}]})
        left_input = 'op_production_by_product'
        rank = semantics.get('rank') if isinstance(semantics.get('rank'), dict) else None
        if rank:
            operations.append({'id': 'op_rank_production', 'op': 'rank', 'input': left_input, 'mode': str(rank.get('mode') or 'top'), 'partition_by': [], 'rank_by': [{'field': 'PRODUCTION_QTY', 'direction': 'desc' if rank.get('mode') != 'bottom' else 'asc', 'nulls': 'last'}], 'tie_break_by': [{'field': field, 'direction': 'asc', 'nulls': 'last'} for field in product_keys], 'limit': int(rank.get('limit') or 1), 'tie_policy': str(semantics.get('tie_policy') or 'exact_n'), 'emit_rank_field': 'RESULT_RANK'})
            left_input = 'op_rank_production'
        equipment_input = f"source:{jobs[1]['job_id']}"
        if equipment_clauses:
            operations.append({'id': 'op_filter_equipment', 'op': 'filter', 'input': equipment_input, 'where': {'op': 'all', 'clauses': equipment_clauses}})
            equipment_input = 'op_filter_equipment'
        operations.append({'id': 'op_equipment_by_product', 'op': 'aggregate', 'input': equipment_input, 'group_by': product_keys, 'metrics': [{'field': 'EQP_ID', 'function': 'nunique', 'as': 'EQP_COUNT', 'dropna': True}, {'field': 'EQP_ID', 'function': 'list_unique', 'as': 'EQP_LIST', 'dropna': True}]})
        output_fields = [*product_keys, 'PRODUCTION_QTY', 'EQP_COUNT', 'EQP_LIST', *(['RESULT_RANK'] if rank else [])]
        operations.append({'id': 'op_join_equipment', 'op': 'join', 'left': left_input, 'right': 'op_equipment_by_product', 'how': 'left', 'key_mappings': [{'left': field, 'right': field} for field in product_keys], 'cardinality': 'one_to_one', 'null_key_policy': 'match', 'multi_match_policy': 'error', 'empty_side_policy': 'allow', 'output_fields': output_fields})
        operations.append({'id': 'op_project', 'op': 'project', 'input': 'op_join_equipment', 'fields': output_fields})
        return _finalize_plan(intent, bundle, catalog, jobs, operations, 'op_project', output_fields, product_keys, {'PRODUCTION_QTY': {'dataset_key': production_key, 'source_field': 'PRODUCTION_QTY', 'aggregation': 'sum'}, 'EQP_COUNT': {'dataset_key': equipment_key, 'source_field': 'EQP_ID', 'aggregation': 'nunique'}, 'EQP_LIST': {'dataset_key': equipment_key, 'source_field': 'EQP_ID', 'aggregation': 'list_unique'}})
    production_key = 'production_today' if semantics.get('date') == semantics.get('reference_date') else 'production'
    production = datasets.get(production_key, {})
    equipment = datasets.get('equipment_assign', {})
    jobs = [{'job_id': 'job_1_production', 'dataset_key': production_key, 'source_type': str(production.get('source_type') or 'dummy'), 'parameters': {'DATE': semantics.get('date')}, 'required_fields': ['DEVICE', 'PRODUCTION_QTY'], 'filters': None, 'requirement': 'required'}, {'job_id': 'job_2_equipment', 'dataset_key': 'equipment_assign', 'source_type': str(equipment.get('source_type') or 'dummy'), 'parameters': {}, 'required_fields': ['DEVICE', 'EQP_ID'], 'filters': None, 'requirement': 'required'}]
    columns = ['DEVICE', 'PRODUCTION_QTY', 'EQP_COUNT', 'EQP_LIST']
    operations = [{'id': 'op_production', 'op': 'aggregate', 'input': 'source:job_1_production', 'group_by': ['DEVICE'], 'metrics': [{'field': 'PRODUCTION_QTY', 'function': 'sum', 'as': 'PRODUCTION_QTY', 'dropna': True}]}, {'id': 'op_equipment', 'op': 'aggregate', 'input': 'source:job_2_equipment', 'group_by': ['DEVICE'], 'metrics': [{'field': 'EQP_ID', 'function': 'nunique', 'as': 'EQP_COUNT', 'dropna': True}, {'field': 'EQP_ID', 'function': 'list_unique', 'as': 'EQP_LIST', 'dropna': True}]}, {'id': 'op_join', 'op': 'join', 'left': 'op_production', 'right': 'op_equipment', 'how': 'left', 'key_mappings': [{'left': 'DEVICE', 'right': 'DEVICE'}], 'cardinality': 'one_to_one', 'null_key_policy': 'never_match', 'multi_match_policy': 'error', 'empty_side_policy': 'allow', 'output_fields': columns}, {'id': 'op_project', 'op': 'project', 'input': 'op_join', 'fields': columns}]
    return _finalize_plan(intent, bundle, catalog, jobs, operations, 'op_project', columns, ['DEVICE'], {'PRODUCTION_QTY': {'dataset_key': production_key}, 'EQP_COUNT': {'dataset_key': 'equipment_assign'}})

def _compile_equipment_view_plan(intent: dict[str, Any], bundle: dict[str, Any], catalog: dict[str, Any], semantics: dict[str, Any], equipment_view: str) -> dict[str, Any]:
    """Compile the two registered equipment views without inferred code.

    ``uph_detail`` is the current UPH registry projection.  ``equipment_grouped``
    is a current assignment rollup whose count and list are derived from the
    same EQP_ID population, so the two result fields cannot drift apart.
    """
    dataset_key = 'eqp_uph' if equipment_view == 'uph_detail' else 'equipment_assign'
    dataset = (catalog.get('datasets') or {}).get(dataset_key, {})
    available = set((dataset.get('fields') or {}).keys())
    clauses = [clause for clause in _product_clauses(semantics, catalog) if set(_filter_fields(clause)).issubset(available)]
    process_values = _process_values(semantics, catalog)
    if process_values and 'OPER_NAME' in available:
        clauses.append({'field': 'OPER_NAME', 'operator': 'in', 'values': process_values, 'semantic_type': 'string'})
    if equipment_view == 'uph_detail':
        fields = ['EQP_MODEL', 'RECIPE_ID', 'OPER_NAME', 'UPH']
        missing = [field for field in fields if field not in available]
        if missing:
            raise ContractError('metadata_dependency_error', 'plan_compilation', 'UPH 상세 view에 필요한 field가 없습니다.', {'dataset_key': dataset_key, 'fields': missing})
    else:
        fields = ['EQP_MODEL', 'RECIPE_ID', 'EQP_COUNT', 'EQP_LIST']
        missing = [field for field in ['EQP_MODEL', 'RECIPE_ID', 'EQP_ID'] if field not in available]
        if missing:
            raise ContractError('metadata_dependency_error', 'plan_compilation', '장비 조합 view에 필요한 field가 없습니다.', {'dataset_key': dataset_key, 'fields': missing})
    job_id = f'job_1_{dataset_key}'
    source_id = f'source:{job_id}'
    required = set(_filter_fields(clauses))
    if equipment_view == 'uph_detail':
        required.update(fields)
    else:
        required.update(['EQP_MODEL', 'RECIPE_ID', 'EQP_ID'])
    job = {'job_id': job_id, 'dataset_key': dataset_key, 'source_type': str(dataset.get('source_type') or 'dummy'), 'parameters': {}, 'required_fields': sorted(required), 'filters': None, 'requirement': 'required'}
    operations: list[dict[str, Any]] = []
    current = source_id
    if clauses:
        operations.append({'id': 'op_filter_equipment_view', 'op': 'filter', 'input': current, 'where': {'op': 'all', 'clauses': clauses}})
        current = 'op_filter_equipment_view'
    if equipment_view == 'uph_detail':
        operations.extend([{'id': 'op_project_uph', 'op': 'project', 'input': current, 'fields': fields}, {'id': 'op_sort_uph', 'op': 'sort', 'input': 'op_project_uph', 'keys': [{'field': field, 'direction': 'asc', 'nulls': 'last'} for field in ['EQP_MODEL', 'RECIPE_ID', 'OPER_NAME']]}])
        lineage = {'UPH': {'dataset_key': dataset_key, 'source_field': 'UPH', 'aggregation': 'none', 'grain': ['EQP_MODEL', 'RECIPE_ID', 'OPER_NAME']}}
        return _finalize_plan(intent, bundle, catalog, [job], operations, 'op_sort_uph', fields, ['EQP_MODEL', 'RECIPE_ID', 'OPER_NAME'], lineage)
    operations.extend([{'id': 'op_group_equipment', 'op': 'aggregate', 'input': current, 'group_by': ['EQP_MODEL', 'RECIPE_ID'], 'metrics': [{'field': 'EQP_ID', 'function': 'nunique', 'as': 'EQP_COUNT', 'dropna': True}, {'field': 'EQP_ID', 'function': 'list_unique', 'as': 'EQP_LIST', 'dropna': True}]}, {'id': 'op_sort_equipment', 'op': 'sort', 'input': 'op_group_equipment', 'keys': [{'field': 'EQP_MODEL', 'direction': 'asc', 'nulls': 'last'}, {'field': 'RECIPE_ID', 'direction': 'asc', 'nulls': 'last'}]}, {'id': 'op_project_equipment', 'op': 'project', 'input': 'op_sort_equipment', 'fields': fields}])
    lineage = {'EQP_COUNT': {'dataset_key': dataset_key, 'source_field': 'EQP_ID', 'aggregation': 'nunique'}, 'EQP_LIST': {'dataset_key': dataset_key, 'source_field': 'EQP_ID', 'aggregation': 'list_unique'}}
    return _finalize_plan(intent, bundle, catalog, [job], operations, 'op_project_equipment', fields, ['EQP_MODEL', 'RECIPE_ID'], lineage)

def _compile_special_plan(intent: dict[str, Any], bundle: dict[str, Any], catalog: dict[str, Any], semantics: dict[str, Any]) -> dict[str, Any] | None:
    kind = str(semantics.get('analysis_kind') or '')
    qualifiers = semantics.get('qualifiers') if isinstance(semantics.get('qualifiers'), dict) else {}
    equipment_view = str(qualifiers.get('equipment_view') or '')
    if kind in {'uph_detail', 'equipment_grouped'} and equipment_view in {'uph_detail', 'equipment_grouped'}:
        return _compile_equipment_view_plan(intent, bundle, catalog, semantics, equipment_view)
    if kind not in {'detail', 'hold_history', 'equipment_detail', 'compare_group_attributes'}:
        return None
    if kind == 'hold_history':
        dataset_key = 'hold_history'
    elif kind == 'equipment_detail':
        dataset_key = 'equipment_assign'
    elif kind == 'compare_group_attributes':
        dataset_key = 'product_master'
    else:
        dataset_key = 'lot_status'
    dataset = (catalog.get('datasets') or {}).get(dataset_key, {})
    available = set((dataset.get('fields') or {}).keys())
    ordered_range = semantics.get('ordered_range') if isinstance(semantics.get('ordered_range'), dict) else None
    process_values = [] if ordered_range else _process_values(semantics, catalog)
    clauses = [clause for clause in _product_clauses(semantics, catalog) if set(_filter_fields(clause)).issubset(available)]
    if process_values and 'OPER_NAME' in available:
        clauses.append({'field': 'OPER_NAME', 'operator': 'in', 'values': process_values, 'semantic_type': 'string'})
    if qualifiers.get('current_hold') and 'HOLD_STAT' in available:
        clauses.append({'field': 'HOLD_STAT', 'operator': 'eq', 'value': 'OnHold', 'semantic_type': 'string'})
    prior_lot_ids = [str(value) for value in semantics.get('prior_lot_ids', []) if str(value)]
    explicit_lot_ids = [str(value) for value in semantics.get('lot_ids', []) if str(value)]
    selected_lot_ids = explicit_lot_ids or prior_lot_ids
    if selected_lot_ids and 'LOT_ID' in available:
        clauses.append({'field': 'LOT_ID', 'operator': 'in', 'values': selected_lot_ids, 'semantic_type': 'string'})
    metric_registry = catalog.get('metrics') if isinstance(catalog.get('metrics'), dict) else {}
    metric_ids = [str(item) for item in semantics.get('metric_refs', [])]
    for threshold in semantics.get('thresholds', []):
        if not metric_ids:
            break
        metric = metric_registry.get(metric_ids[0], {})
        source_field = str((metric.get('source_binding') or {}).get('field') or '')
        if source_field in available:
            clauses.append({'field': source_field, 'operator': threshold.get('operator'), 'value': threshold.get('value'), 'semantic_type': 'number'})
    if kind == 'hold_history':
        fields = ['LOT_ID', 'HOLD_EVENT_AT', 'HOLD_CD', 'HOLD_DESC', 'OPER_NAME']
    elif kind == 'equipment_detail':
        product = ((catalog.get('recipes') or {}).get('product.standard', {}).get('grain') or {}).get('keys') or []
        fields = [*product, 'EQP_ID', 'EQP_MODEL', 'RECIPE_ID', 'OPER_NAME']
    elif kind == 'compare_group_attributes':
        fields = ['TECH', 'DEN', 'PKG_TYPE2', 'MCP_NO', 'MODE', 'PKG_TYPE1', 'LEAD', 'DEVICE']
    else:
        fields = ['LOT_ID', 'DEVICE', 'OPER_NAME', 'HOLD_STAT', 'HOLD_REASON', 'IN_TAT', 'CUM_TAT', 'PROD_QTY', 'WF_QTY']
    for field in semantics.get('field_refs', []):
        if str(field) in available and str(field) not in fields:
            fields.append(str(field))
    fields = [field for field in fields if field in available]
    if kind == 'hold_history' and (not explicit_lot_ids):
        fields.append('HOLD_DURATION_HOURS')
    required = set([field for field in fields if field in available] + _filter_fields(clauses))
    if ordered_range and 'OPER_SEQ' in available:
        required.add('OPER_SEQ')
    job_id = f'job_1_{dataset_key}'
    params = {'DATE': semantics.get('date')} if 'DATE' in available else {}
    if kind == 'hold_history' and selected_lot_ids:
        params['LOT_ID'] = selected_lot_ids
    jobs = [{'job_id': job_id, 'dataset_key': dataset_key, 'source_type': str(dataset.get('source_type') or 'dummy'), 'parameters': params, 'required_fields': sorted(required), 'filters': None, 'requirement': 'required'}]
    source_id = f'source:{job_id}'
    operations: list[dict[str, Any]] = []
    current = source_id
    if ordered_range and 'OPER_SEQ' in available:
        range_values = set(_range_process_values(ordered_range, catalog))
        sequences = [int(item.get('oper_seq') or 0) for item in catalog.get('process_order', []) if isinstance(item, dict) and str(item.get('oper_name') or '') in range_values]
        if not sequences:
            raise ContractError('plan_contract_error', 'plan_compilation', '공정 범위 sequence가 metadata에 없습니다.')
        operations.append({'id': 'op_ordered_range', 'op': 'ordered_range', 'input': source_id, 'field': 'OPER_SEQ', 'start': min(sequences), 'end': max(sequences)})
        current = 'op_ordered_range'
    if clauses:
        filter_input = current
        current = 'op_filter_1'
        operations.append({'id': current, 'op': 'filter', 'input': filter_input, 'where': {'op': 'all', 'clauses': clauses}})
    if kind == 'hold_history':
        filtered_history = current
        if explicit_lot_ids:
            operations.append({'id': 'op_sort_hold_history', 'op': 'sort', 'input': filtered_history, 'keys': [{'field': 'HOLD_EVENT_AT', 'direction': 'desc', 'nulls': 'last'}, {'field': 'HOLD_CD', 'direction': 'asc', 'nulls': 'last'}]})
            current = 'op_sort_hold_history'
        else:
            operations.extend([{'id': 'op_latest_hold_event', 'op': 'aggregate', 'input': filtered_history, 'group_by': ['LOT_ID'], 'metrics': [{'field': 'HOLD_EVENT_AT', 'function': 'max', 'as': 'CURRENT_HOLD_STARTED_AT', 'dropna': True}]}, {'id': 'op_hold_duration', 'op': 'derive', 'input': 'op_latest_hold_event', 'output_field': 'HOLD_DURATION_HOURS', 'formula': {'expression': {'op': 'datetime_diff_hours', 'args': [{'literal': semantics.get('reference_instant')}, {'field_ref': 'CURRENT_HOLD_STARTED_AT'}]}, 'rounding': {'digits': 3}}}, {'id': 'op_oldest_hold_lot', 'op': 'rank', 'input': 'op_hold_duration', 'mode': 'top', 'partition_by': [], 'rank_by': [{'field': 'HOLD_DURATION_HOURS', 'direction': 'desc', 'nulls': 'last'}], 'tie_break_by': [{'field': 'LOT_ID', 'direction': 'asc', 'nulls': 'last'}], 'limit': 1, 'tie_policy': 'include_all', 'emit_rank_field': 'RESULT_RANK'}, {'id': 'op_selected_hold_history', 'op': 'join', 'left': filtered_history, 'right': 'op_oldest_hold_lot', 'how': 'inner', 'key_mappings': [{'left': 'LOT_ID', 'right': 'LOT_ID'}], 'cardinality': 'many_to_one', 'null_key_policy': 'never_match', 'multi_match_policy': 'error', 'empty_side_policy': 'allow', 'output_fields': fields}, {'id': 'op_hold_history_detail', 'op': 'detail', 'input': 'op_selected_hold_history', 'fields': fields}, {'id': 'op_sort_hold_history', 'op': 'sort', 'input': 'op_hold_history_detail', 'keys': [{'field': 'HOLD_EVENT_AT', 'direction': 'desc', 'nulls': 'last'}, {'field': 'LOT_ID', 'direction': 'asc', 'nulls': 'last'}]}])
            current = 'op_sort_hold_history'
    elif kind == 'compare_group_attributes':
        compare_id = 'op_compare_group_attributes'
        operations.append({'id': compare_id, 'op': 'compare_group_attributes', 'input': current, 'group_by': [field for field in ['TECH', 'DEN', 'PKG_TYPE2', 'MCP_NO'] if field in fields], 'comparison_fields': [field for field in ['MODE', 'PKG_TYPE1', 'LEAD'] if field in fields], 'comparison_rule': 'any'})
        current = compare_id
    project_id = 'op_project'
    operations.append({'id': project_id, 'op': 'project', 'input': current, 'fields': fields})
    current = project_id
    if kind in {'detail', 'equipment_detail'}:
        dedupe_fields = [field for field in (['LOT_ID'] if kind == 'detail' else fields) if field in fields]
        if dedupe_fields:
            operations.append({'id': 'op_dedupe', 'op': 'dedupe', 'input': current, 'fields': dedupe_fields, 'keep': 'first'})
            current = 'op_dedupe'
    if kind == 'compare_group_attributes':
        sort_fields = [field for field in ['TECH', 'DEN', 'PKG_TYPE2', 'MCP_NO', 'MODE', 'PKG_TYPE1', 'LEAD', 'DEVICE'] if field in fields]
        operations.append({'id': 'op_sort_detail', 'op': 'sort', 'input': current, 'keys': [{'field': field, 'direction': 'asc', 'nulls': 'last'} for field in sort_fields]})
        current = 'op_sort_detail'
    elif kind == 'detail':
        sort_fields = [field for field in (['IN_TAT'] if 'IN_TAT' in fields else ['OPER_NAME', 'LOT_ID']) if field in fields]
        if sort_fields:
            operations.append({'id': 'op_sort_detail', 'op': 'sort', 'input': current, 'keys': [{'field': field, 'direction': 'desc' if field == 'IN_TAT' else 'asc', 'nulls': 'last'} for field in sort_fields]})
            current = 'op_sort_detail'
    return _finalize_plan(intent, bundle, catalog, jobs, operations, current, fields, [field for field in fields if field in {'LOT_ID', 'EQP_ID', 'DEVICE'}], {'dataset_key': dataset_key})

def _compile_previous_plan(intent: dict[str, Any], bundle: dict[str, Any], catalog: dict[str, Any], semantics: dict[str, Any], prior_result: dict[str, Any] | None) -> dict[str, Any] | None:
    kind = str(semantics.get('analysis_kind') or '')
    if kind not in {'previous_rank', 'equipment_enrich'}:
        return None
    if kind == 'equipment_enrich' and semantics.get('followup_mode') != 'referenced':
        return None
    rows = (prior_result or {}).get('rows') if isinstance(prior_result, dict) else None
    columns = [str(value) for value in (prior_result or {}).get('columns') or []] if isinstance(prior_result, dict) else []
    if not isinstance(rows, list) or not columns:
        raise ContractError('state_reference_expired', 'plan_compilation', '이전 분석 결과를 사용할 수 없습니다.')
    if kind == 'previous_rank':
        metric_candidates = [str(value) for value in semantics.get('metric_refs', []) if str(value) in columns]
        rank_field = metric_candidates[0] if metric_candidates else next((field for field in reversed(columns) if field.endswith(('_QTY', '_COUNT', 'UPH'))), '')
        if not rank_field:
            raise ContractError('plan_contract_error', 'plan_compilation', '이전 결과에서 순위 metric을 찾을 수 없습니다.')
        rank = semantics.get('rank') if isinstance(semantics.get('rank'), dict) else {'mode': 'top', 'limit': 1}
        output_columns = [field for field in columns if field != 'RESULT_RANK'] + ['RESULT_RANK']
        operations = [{'id': 'op_previous', 'op': 'transform_previous_result', 'input': 'source:previous'}, {'id': 'op_rank_previous', 'op': 'rank', 'input': 'op_previous', 'mode': str(rank.get('mode') or 'top'), 'partition_by': [], 'rank_by': [{'field': rank_field, 'direction': 'desc' if rank.get('mode') != 'bottom' else 'asc', 'nulls': 'last'}], 'tie_break_by': [{'field': field, 'direction': 'asc', 'nulls': 'last'} for field in columns if field != rank_field][:8], 'limit': int(rank.get('limit') or 1), 'tie_policy': str(semantics.get('tie_policy') or 'exact_n'), 'emit_rank_field': 'RESULT_RANK'}, {'id': 'op_project', 'op': 'project', 'input': 'op_rank_previous', 'fields': output_columns}]
        return _finalize_plan(intent, bundle, catalog, [], operations, 'op_project', output_columns, [], {'previous_result': True}, input_refs=['previous'])
    dataset_key = 'equipment_assign'
    dataset = (catalog.get('datasets') or {}).get(dataset_key, {})
    available = set((dataset.get('fields') or {}).keys())
    product_keys = [field for field in ((catalog.get('recipes') or {}).get('product.standard', {}).get('grain') or {}).get('keys') or [] if field in columns and field in available]
    if not product_keys:
        raise ContractError('plan_contract_error', 'plan_compilation', '이전 결과와 장비 metadata의 제품 key가 겹치지 않습니다.')
    process_values = _process_values(semantics, catalog)
    clauses = [{'field': 'OPER_NAME', 'operator': 'in', 'values': process_values, 'semantic_type': 'string'}] if process_values else []
    job_id = 'job_1_equipment_assign'
    jobs = [{'job_id': job_id, 'dataset_key': dataset_key, 'source_type': str(dataset.get('source_type') or 'dummy'), 'parameters': {}, 'required_fields': sorted(set(product_keys + ['EQP_ID'] + _filter_fields(clauses))), 'filters': None, 'requirement': 'required'}]
    right_input = f'source:{job_id}'
    operations: list[dict[str, Any]] = [{'id': 'op_previous', 'op': 'transform_previous_result', 'input': 'source:previous'}]
    if clauses:
        operations.append({'id': 'op_filter_equipment', 'op': 'filter', 'input': right_input, 'where': {'op': 'all', 'clauses': clauses}})
        right_input = 'op_filter_equipment'
    operations.append({'id': 'op_equipment_by_product', 'op': 'aggregate', 'input': right_input, 'group_by': product_keys, 'metrics': [{'field': 'EQP_ID', 'function': 'nunique', 'as': 'EQP_COUNT', 'dropna': True}, {'field': 'EQP_ID', 'function': 'list_unique', 'as': 'EQP_LIST', 'dropna': True}]})
    output_columns = [field for field in columns if field != 'RESULT_RANK'] + ['EQP_COUNT', 'EQP_LIST']
    operations.append({'id': 'op_enrich_previous', 'op': 'enrich_previous_result', 'left': 'op_previous', 'right': 'op_equipment_by_product', 'key_mappings': [{'left': field, 'right': field} for field in product_keys], 'cardinality': 'one_to_one', 'null_key_policy': 'match', 'multi_match_policy': 'error', 'empty_side_policy': 'allow', 'output_fields': output_columns})
    operations.append({'id': 'op_project', 'op': 'project', 'input': 'op_enrich_previous', 'fields': output_columns})
    return _finalize_plan(intent, bundle, catalog, jobs, operations, 'op_project', output_columns, product_keys, {'EQP_COUNT': {'dataset_key': dataset_key, 'source_field': 'EQP_ID', 'aggregation': 'nunique'}}, input_refs=['previous'])

def compile_plan(intent: dict[str, Any], bundle: dict[str, Any], catalog: dict[str, Any], *, prior_result: dict[str, Any] | None=None) -> dict[str, Any]:
    semantics = intent.get('semantics') if isinstance(intent.get('semantics'), dict) else {}
    if semantics.get('analysis_kind') == 'clarification':
        raise ContractError('needs_clarification', 'intent_validation', '어떤 수량을 조회할지 선택해 주세요: 생산량, INPUT 실적, 재공수량, 계획수량.', {'options': ['PRODUCTION_QTY', 'INPUT_QTY', 'WIP_QTY', 'INPUT_PLAN_QTY', 'OUT_PLAN_QTY']})
    previous = _compile_previous_plan(intent, bundle, catalog, semantics, prior_result)
    if previous is not None:
        return previous
    operator_special = _compile_operator_special_plan(intent, bundle, catalog, semantics)
    if operator_special is not None:
        return operator_special
    special = _compile_special_plan(intent, bundle, catalog, semantics)
    if special is not None:
        return special
    metric_ids = [str(item) for item in semantics.get('metric_refs', [])]
    metric_registry = catalog.get('metrics') if isinstance(catalog.get('metrics'), dict) else {}
    kind = str(semantics.get('analysis_kind') or 'aggregate')
    dimensions = [str(item) for item in semantics.get('dimension_refs', [])]
    product_recipe = (catalog.get('recipes') or {}).get('product.standard', {})
    product_dimensions = [str(item) for item in (product_recipe.get('grain') or {}).get('keys') or []]
    rank_partitions = deepcopy(dimensions) if kind == 'group_rank' else []
    if not dimensions:
        dimensions = deepcopy(product_dimensions)
    elif kind == 'group_rank':
        dimensions = list(dict.fromkeys([*dimensions, *product_dimensions]))
    if isinstance(semantics.get('ordered_range'), dict) and 'OPER_NAME' in dimensions and ('OPER_SEQ' not in dimensions):
        dimensions.append('OPER_SEQ')
    requested_date = str(semantics.get('date') or '')
    reference_date = str(semantics.get('reference_date') or requested_date)
    jobs: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    lineage: dict[str, Any] = {}
    aggregate_ids: list[str] = []
    process_values = _process_values(semantics, catalog)
    if isinstance(semantics.get('ordered_range'), dict):
        process_values = _range_process_values(semantics.get('ordered_range'), catalog)
    product_clauses = _product_clauses(semantics, catalog)
    grouped_metrics: dict[tuple[str, str, str], list[tuple[str, dict[str, Any]]]] = {}
    for metric_id in metric_ids:
        metric = metric_registry.get(metric_id)
        if not isinstance(metric, dict):
            raise ContractError('metadata_dependency_error', 'plan_compilation', '등록되지 않은 metric입니다.', {'metric_id': metric_id})
        if metric.get('source_binding'):
            dataset_key, query_date = _metric_dataset(metric, requested_date, reference_date)
            binding = metric.get('source_binding') if isinstance(metric.get('source_binding'), dict) else {}
            fixed_filters = deepcopy(binding.get('fixed_filters') or [])
            grouped_metrics.setdefault((dataset_key, query_date, sha256_json(fixed_filters)), []).append((metric_id, metric))
    aggregate_metric_groups: list[list[str]] = []
    jobs_by_source: dict[tuple[str, str], dict[str, Any]] = {}
    scoped_processes = semantics.get('process_refs_by_metric') if isinstance(semantics.get('process_refs_by_metric'), dict) else {}
    for index, ((dataset_key, query_date, _), group) in enumerate(grouped_metrics.items(), start=1):
        source_key = (dataset_key, query_date)
        dataset = (catalog.get('datasets') or {}).get(dataset_key, {})
        if source_key not in jobs_by_source:
            job_id = f'job_{len(jobs_by_source) + 1}_{dataset_key}'
            declared_parameters = dataset.get('parameters') if isinstance(dataset.get('parameters'), dict) else {}
            jobs_by_source[source_key] = {'job_id': job_id, 'dataset_key': dataset_key, 'source_type': str(dataset.get('source_type') or 'dummy'), 'parameters': {'DATE': query_date} if 'DATE' in declared_parameters else {}, 'required_fields': [], 'filters': None, 'requirement': 'required'}
            jobs.append(jobs_by_source[source_key])
        job = jobs_by_source[source_key]
        job_id = str(job['job_id'])
        source_id = f'source:{job_id}'
        dataset_fields = set((dataset.get('fields') or {}).keys())
        clauses = [clause for clause in deepcopy(product_clauses) if set(_filter_fields(clause)).issubset(dataset_fields)]
        fixed_filters = deepcopy((group[0][1].get('source_binding') or {}).get('fixed_filters') or [])
        clauses.extend((clause for clause in fixed_filters if isinstance(clause, dict)))
        group_process_refs: list[str] = []
        for metric_id, _metric in group:
            for process_ref in scoped_processes.get(metric_id, []) if isinstance(scoped_processes.get(metric_id), list) else []:
                if str(process_ref) not in group_process_refs:
                    group_process_refs.append(str(process_ref))
        selected_process_values = _process_values({'process_refs': group_process_refs}, catalog) if group_process_refs else process_values
        fixed_process = any((isinstance(clause, dict) and clause.get('field') == 'OPER_NAME' for clause in fixed_filters))
        if selected_process_values and 'OPER_NAME' in dataset_fields and (not fixed_process):
            clauses.append({'field': 'OPER_NAME', 'operator': 'in', 'values': selected_process_values, 'semantic_type': 'string'})
        if 'DATE' not in (dataset.get('parameters') or {}) and isinstance(dataset.get('date_filter_contract'), dict) and ('DATE' in dataset_fields):
            clauses.append({'field': 'DATE', 'operator': 'eq', 'value': query_date, 'semantic_type': 'date'})
        required_fields = set(dimensions + [str((metric.get('source_binding') or {}).get('field')) for _, metric in group] + _filter_fields(clauses))
        job['required_fields'] = sorted(set(job.get('required_fields') or []) | {field for field in required_fields if field})
        current_id = source_id
        if clauses:
            filtered_id = f'op_filter_{index}'
            operations.append({'id': filtered_id, 'op': 'filter', 'input': current_id, 'where': {'op': 'all', 'clauses': clauses}})
            current_id = filtered_id
        qualifiers = semantics.get('qualifiers') if isinstance(semantics.get('qualifiers'), dict) else {}
        if qualifiers.get('preserve_blank_product'):
            for derive_index, field in enumerate([value for value in dimensions if value in product_dimensions], start=1):
                derive_id = f'op_fill_product_{index}_{derive_index}'
                operations.append({'id': derive_id, 'op': 'derive', 'input': current_id, 'output_field': field, 'formula': {'expression': {'op': 'coalesce_blank', 'args': [{'field_ref': field}, {'literal': ''}]}}})
                current_id = derive_id
        if qualifiers.get('fill_metric_zero'):
            for derive_index, (_metric_id, metric) in enumerate(group, start=1):
                source_field = str((metric.get('source_binding') or {}).get('field') or '')
                if not source_field:
                    continue
                derive_id = f'op_fill_metric_{index}_{derive_index}'
                operations.append({'id': derive_id, 'op': 'derive', 'input': current_id, 'output_field': source_field, 'formula': {'expression': {'op': 'coalesce', 'args': [{'metric_ref': source_field}, {'literal': 0}]}}})
                current_id = derive_id
        ordered_range = semantics.get('ordered_range')
        if isinstance(ordered_range, dict):
            order_map: dict[str, Any] = {}
            for item in catalog.get('process_order', []):
                if not isinstance(item, dict):
                    continue
                sequence = item.get('oper_seq')
                for name in [item.get('oper_name'), *(item.get('aliases') or [])]:
                    order_map[normalize_text(str(name)).upper()] = sequence
            start = order_map.get(normalize_text(str(ordered_range.get('start'))).upper())
            end = order_map.get(normalize_text(str(ordered_range.get('end'))).upper())
            if start is None or end is None:
                raise ContractError('plan_contract_error', 'plan_compilation', '공정 범위 endpoint가 metadata에 없습니다.')
            range_id = f'op_range_{index}'
            operations.append({'id': range_id, 'op': 'ordered_range', 'input': current_id, 'field': 'OPER_SEQ', 'start': min(start, end), 'end': max(start, end)})
            current_id = range_id
        aggregate_id = f'op_aggregate_{index}'
        aggregate_metrics: list[dict[str, Any]] = []
        group_metric_ids: list[str] = []
        for metric_id, metric in group:
            binding = metric.get('source_binding') if isinstance(metric.get('source_binding'), dict) else {}
            additivity = metric.get('additivity') if isinstance(metric.get('additivity'), dict) else {}
            default = str(additivity.get('default') or 'additive')
            function = 'sum' if default == 'additive' else 'nunique' if default == 'distinct' else 'mean'
            aggregate_metrics.append({'field': binding.get('field'), 'function': function, 'as': metric_id, 'dropna': True})
            group_metric_ids.append(metric_id)
            lineage[metric_id] = {'dataset_key': dataset_key, 'source_field': binding.get('field'), 'query_date': query_date, 'aggregation': function, 'grain': dimensions}
        operations.append({'id': aggregate_id, 'op': 'aggregate', 'input': current_id, 'group_by': dimensions, 'metrics': aggregate_metrics})
        aggregate_ids.append(aggregate_id)
        aggregate_metric_groups.append(group_metric_ids)
    current_id = aggregate_ids[0] if aggregate_ids else ''
    if len(aggregate_ids) > 1:
        joined_metric_ids = list(aggregate_metric_groups[0])
        for join_index, right_id in enumerate(aggregate_ids[1:], start=2):
            joined_id = f'op_join_{join_index}'
            operations.append({'id': joined_id, 'op': 'join', 'left': current_id, 'right': right_id, 'how': 'left', 'key_mappings': [{'left': field, 'right': field} for field in dimensions], 'cardinality': 'one_to_one', 'null_key_policy': 'match', 'multi_match_policy': 'error', 'empty_side_policy': 'allow', 'output_fields': dimensions + joined_metric_ids + aggregate_metric_groups[join_index - 1]})
            current_id = joined_id
            joined_metric_ids.extend(aggregate_metric_groups[join_index - 1])
    if kind == 'presence' and len(aggregate_ids) >= 2:
        presence_id = 'op_presence'
        operations.append({'id': presence_id, 'op': 'presence_filter', 'left': aggregate_ids[0], 'right': aggregate_ids[1], 'keys': dimensions, 'left_metric': metric_ids[0], 'right_metric': metric_ids[1], 'materialize_right_zero': True})
        current_id = presence_id
    elif kind == 'formula' and len(metric_ids) >= 2:
        formula_metric_id = 'ACHIEVEMENT_RATE' if 'ACHIEVEMENT_RATE' in metric_ids else str(semantics.get('formula_ref') or 'ACHIEVEMENT_RATE')
        formula_record = metric_registry.get(formula_metric_id, {})
        formula_id = 'op_formula'
        operations.append({'id': formula_id, 'op': 'derive', 'input': current_id, 'output_field': formula_metric_id, 'formula': formula_record.get('formula') or {'expression': {'op': 'multiply', 'args': [{'op': 'safe_divide', 'args': [{'metric_ref': metric_ids[1]}, {'metric_ref': metric_ids[0]}], 'zero_division': 'null'}, {'literal': 100}]}, 'rounding': {'digits': 1}}})
        current_id = formula_id
        if formula_metric_id not in metric_ids:
            metric_ids.append(formula_metric_id)
    if kind == 'field_compare' and len(metric_ids) >= 2:
        compare_id = 'op_compare_fields'
        operations.append({'id': compare_id, 'op': 'compare_fields', 'input': current_id, 'left_field': metric_ids[0], 'right_field': metric_ids[1], 'operator': str(semantics.get('comparison_operator') or 'gt'), 'semantic_type': 'number', 'type_compatibility': 'numeric', 'null_policy': 'false'})
        current_id = compare_id
    segmented_rank = kind in {'multi_metric_argmax', 'top_bottom'}
    segment_label_field = ''
    if kind == 'multi_metric_argmax' and len(aggregate_metric_groups) >= 2:
        rank_ids: list[tuple[str, str]] = []
        source_metric_ids = [group[0] for group in aggregate_metric_groups if group]
        for segment_index, metric_id in enumerate(source_metric_ids, start=1):
            rank_id = f'op_rank_metric_{segment_index}'
            operations.append({'id': rank_id, 'op': 'rank', 'input': current_id, 'mode': 'top', 'partition_by': [], 'rank_by': [{'field': metric_id, 'direction': 'desc', 'nulls': 'last'}], 'tie_break_by': [{'field': field, 'direction': 'asc', 'nulls': 'last'} for field in dimensions], 'limit': 1, 'tie_policy': 'include_all', 'emit_rank_field': 'RESULT_RANK'})
            rank_ids.append((rank_id, metric_id))
        segment_label_field = 'RESULT_METRIC'
        operations.append({'id': 'op_concat_segments', 'op': 'concat_segments', 'segments': [{'input': rank_id, 'label': label} for rank_id, label in rank_ids], 'label_field': segment_label_field})
        current_id = 'op_concat_segments'
    elif kind == 'top_bottom' and metric_ids:
        segments = semantics.get('rank_segments') if isinstance(semantics.get('rank_segments'), list) else []
        rank_ids = []
        for segment_index, rank_spec in enumerate(segments, start=1):
            mode = str(rank_spec.get('mode') or 'top')
            rank_id = f'op_rank_{mode}_{segment_index}'
            operations.append({'id': rank_id, 'op': 'rank', 'input': current_id, 'mode': mode, 'partition_by': [], 'rank_by': [{'field': metric_ids[0], 'direction': 'desc' if mode == 'top' else 'asc', 'nulls': 'last'}], 'tie_break_by': [{'field': field, 'direction': 'asc', 'nulls': 'last'} for field in dimensions], 'limit': int(rank_spec.get('limit') or 1), 'tie_policy': 'exact_n', 'emit_rank_field': 'RESULT_RANK'})
            rank_ids.append((rank_id, mode.upper()))
        segment_label_field = 'RESULT_SEGMENT'
        operations.append({'id': 'op_concat_segments', 'op': 'concat_segments', 'segments': [{'input': rank_id, 'label': label} for rank_id, label in rank_ids], 'label_field': segment_label_field})
        current_id = 'op_concat_segments'
    rank = semantics.get('rank') if isinstance(semantics.get('rank'), dict) else None
    if rank and (not segmented_rank):
        rank_metric = metric_ids[0]
        rank_id = 'op_rank'
        direction = 'desc' if rank.get('mode') == 'top' else 'asc'
        operations.append({'id': rank_id, 'op': 'rank', 'input': current_id, 'mode': rank.get('mode'), 'partition_by': rank_partitions, 'rank_by': [{'field': rank_metric, 'direction': direction, 'nulls': 'last'}], 'tie_break_by': [{'field': field, 'direction': 'asc', 'nulls': 'last'} for field in dimensions], 'limit': int(rank.get('limit') or 1), 'tie_policy': str(semantics.get('tie_policy') or 'exact_n'), 'emit_rank_field': 'RESULT_RANK'})
        current_id = rank_id
    sort_spec = semantics.get('sort') if isinstance(semantics.get('sort'), dict) else None
    if sort_spec and (not rank) and str(sort_spec.get('field') or ''):
        sort_id = 'op_sort_metric'
        operations.append({'id': sort_id, 'op': 'sort', 'input': current_id, 'keys': [{'field': str(sort_spec['field']), 'direction': str(sort_spec.get('direction') or 'desc'), 'nulls': 'last'}]})
        current_id = sort_id
    elif 'OPER_SEQ' in dimensions and (not rank):
        sort_id = 'op_sort_process_sequence'
        operations.append({'id': sort_id, 'op': 'sort', 'input': current_id, 'keys': [{'field': 'OPER_SEQ', 'direction': 'asc', 'nulls': 'last'}]})
        current_id = sort_id
    elif dimensions and (not rank) and (not segmented_rank):
        sort_id = 'op_sort_grain'
        operations.append({'id': sort_id, 'op': 'sort', 'input': current_id, 'keys': [{'field': field, 'direction': 'asc', 'nulls': 'last'} for field in dimensions]})
        current_id = sort_id
    fields = [str(item) for item in semantics.get('field_refs', [])]
    output_columns = dimensions + metric_ids + (['RESULT_RANK'] if rank or segmented_rank else [])
    if segment_label_field:
        output_columns = [segment_label_field, *output_columns]
    for field in fields:
        if field not in output_columns:
            output_columns.append(field)
    project_id = 'op_project'
    operations.append({'id': project_id, 'op': 'project', 'input': current_id, 'fields': output_columns})
    current_id = project_id
    plan_material = {'contract_version': 'analysis.plan.v1', 'intent_sha256': intent.get('intent_sha256'), 'candidate_bundle_sha256': bundle.get('bundle_sha256'), 'catalog_sha256': catalog.get('catalog_sha256'), 'retrieval_jobs': jobs, 'operations': operations, 'result_operation_id': current_id, 'result_contract': {'columns': output_columns, 'ordering': [], 'grain': dimensions}, 'lineage': lineage}
    normalized = deepcopy(plan_material)
    normalized['retrieval_jobs'] = sorted(normalized['retrieval_jobs'], key=lambda item: item['job_id'])
    plan_id = f'plan:{sha256_json(normalized)}'
    semantic_material = {key: normalized[key] for key in ('catalog_sha256', 'retrieval_jobs', 'operations', 'result_operation_id', 'result_contract', 'lineage')}
    return {**plan_material, 'plan_id': plan_id, 'plan_fingerprint': sha256_json(semantic_material)}

def validate_plan(plan: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    jobs = plan.get('retrieval_jobs') if isinstance(plan.get('retrieval_jobs'), list) else []
    operations = plan.get('operations') if isinstance(plan.get('operations'), list) else []
    if not operations or (not jobs and 'previous' not in (plan.get('input_refs') or [])):
        raise ContractError('plan_contract_error', 'plan_validation', '조회 작업 또는 operation DAG가 없습니다.')
    job_ids = [str(item.get('job_id') or '') for item in jobs]
    if len(job_ids) != len(set(job_ids)) or any((not item for item in job_ids)):
        raise ContractError('plan_contract_error', 'plan_validation', 'retrieval job ID가 없거나 중복되었습니다.')
    dataset_registry = catalog.get('datasets') if isinstance(catalog.get('datasets'), dict) else {}
    for job in jobs:
        dataset = dataset_registry.get(str(job.get('dataset_key') or ''))
        if not isinstance(dataset, dict):
            raise ContractError('metadata_dependency_error', 'plan_validation', 'dataset contract가 없습니다.')
        available = set(dataset.get('fields', {}).keys()) if isinstance(dataset.get('fields'), dict) else set()
        missing = sorted(set(job.get('required_fields') or []) - available)
        if missing:
            raise ContractError('plan_contract_error', 'plan_validation', 'dataset에 필요한 field role이 없습니다.', {'dataset_key': job.get('dataset_key'), 'fields': missing})
    operation_ids = [str(item.get('id') or '') for item in operations]
    if len(operation_ids) != len(set(operation_ids)) or any((not item for item in operation_ids)):
        raise ContractError('plan_contract_error', 'plan_validation', 'operation ID가 없거나 중복되었습니다.')
    if str(plan.get('result_operation_id') or '') not in operation_ids:
        raise ContractError('plan_contract_error', 'plan_validation', 'result operation이 존재하지 않습니다.')
    available_refs = {f'source:{job_id}' for job_id in job_ids}
    if 'previous' in (plan.get('input_refs') or []):
        available_refs.add('source:previous')
    supported_ops = {'filter', 'ordered_range', 'project', 'detail', 'aggregate', 'sort', 'rank', 'compare_fields', 'compare_group_attributes', 'find_duplicate_groups', 'join', 'presence_filter', 'derive', 'dedupe', 'row_match_groups', 'concat_segments', 'transform_previous_result', 'enrich_previous_result', 'explain_previous'}
    for operation in operations:
        operation_id = str(operation.get('id') or '')
        operator = str(operation.get('op') or '')
        if operator not in supported_ops:
            raise ContractError('unsupported_operation', 'plan_validation', '등록되지 않은 typed operator입니다.', {'operator': operator})
        refs: list[str] = []
        if operator in {'join', 'presence_filter', 'enrich_previous_result'}:
            refs.extend([str(operation.get('left') or ''), str(operation.get('right') or '')])
        elif operator == 'concat_segments':
            refs.extend((str(item.get('input') or '') for item in operation.get('segments', []) if isinstance(item, dict)))
        else:
            input_ref = str(operation.get('input') or '')
            if input_ref:
                refs.append(input_ref)
        missing_refs = [value for value in refs if not value or value not in available_refs]
        if missing_refs:
            raise ContractError('plan_contract_error', 'plan_validation', 'operation DAG 입력이 존재하지 않습니다.', {'operation_id': operation_id, 'missing_inputs': missing_refs})
        if operator == 'join':
            required_policies = {'key_mappings', 'cardinality', 'null_key_policy', 'multi_match_policy', 'empty_side_policy', 'output_fields'}
            missing_policies = sorted((key for key in required_policies if key not in operation))
            if missing_policies:
                raise ContractError('plan_contract_error', 'plan_validation', 'join policy가 완전하지 않습니다.', {'operation_id': operation_id, 'missing': missing_policies})
        available_refs.add(operation_id)
    if set(plan.get('result_contract', {}).get('columns', [])) & {'generated_code', 'pandas_code'}:
        raise ContractError('plan_contract_error', 'plan_validation', 'retired pandas code field는 사용할 수 없습니다.')
    return plan


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


import json
import re
from copy import deepcopy
from itertools import product
from typing import Any, Callable, Iterable, Mapping
_v2cCATALOG_VERSION = 'metadata.runtime.catalog.v2'
_v2cBUNDLE_VERSION = 'resolved.candidate.bundle.v1'
_v2cROUTE_VERSION = 'analysis.route.v1'
_v2cROUTE_POLICY_VERSION = 'route-policy.v1'
_v2cINTENT_VERSION = 'analysis.intent.v1'
_v2cMAX_MATCHES_PER_TYPE = 64
_v2cMAX_INTENT_CANDIDATES = 32
_v2cMAX_AMBIGUITY_VARIANTS = 16
_v2cMAX_BUNDLE_BYTES = 28 * 1024
_v2cCATALOG_TARGET_SECTIONS = {'dataset': 'datasets', 'field': 'fields', 'metric': 'metrics', 'entity_group': 'entity_groups', 'grain': 'grains', 'relation': 'relations', 'recipe': 'recipes'}
_v2cMATCH_POOL_KEYS = {'dataset': 'dataset_candidates', 'field': 'field_candidates', 'metric': 'metric_candidates', 'entity_group': 'entity_group_candidates', 'grain': 'grain_candidates', 'relation': 'relation_candidates', 'recipe': 'recipe_candidates', 'function': 'function_candidates'}
_v2cALLOWED_TEMPLATE_OPERATIONS = {'filter', 'project', 'aggregate', 'join', 'derive', 'compare_fields', 'sort', 'rank', 'transform_previous_result'}
_v2cUNSUPPORTED_LEXEMES = ('예측', 'forecast', '원인 분석', '왜 발생', 'root cause', '최적화', 'optimize', '시뮬레이션', 'simulate')
_v2cOPERATION_LEXEMES = {'rank': ('상위', '하위', 'top', 'bottom', '가장 큰', '가장 작은', '최대', '최소', 'highest', 'lowest'), 'project': ('컬럼', '필드', '열만', 'column', 'field', 'projection'), 'join': ('조인', 'join', '붙여', '합쳐', '함께', '연결'), 'compare_fields': ('보다 큰', '보다 작은', '보다 크거나 같은', '보다 작거나 같은', '초과', '미만', '이상', '이하', 'greater than', 'less than', 'at least', 'at most', 'above', 'below'), 'sort': ('큰 순', '작은 순', '내림차순', '오름차순', '정렬', 'sort'), 'aggregate': ('합계', '총 ', '전체', '평균', '별', 'sum', 'total', 'average', 'aggregate'), 'detail': ('목록', '상세', '보여', '알려', 'list', 'detail', 'show')}
_v2cTOP_N_PATTERN = re.compile('(?P<mode>상위|하위|top|bottom)\\s*(?P<limit>\\d+)\\s*(?:개|건|rows?)?', re.I)
_v2cTOP_LEVEL_KEYS = {'contract_version', 'request_id', 'catalog_sha256', 'dataset_candidates', 'field_candidates', 'metric_candidates', 'entity_group_candidates', 'grain_candidates', 'relation_candidates', 'recipe_candidates', 'function_candidates', 'intent_candidates', 'prompt_cards', 'bundle_sha256', 'route_decision', 'route_evidence'}
_v2cINTENT_CANDIDATE_KEYS = {'candidate_id', 'description', 'semantics', 'semantics_sha256', 'required_slots', 'resolved_slots', 'evidence_refs'}
_v2cPROMPT_CARD_KEYS = {'candidate_id', 'description', 'analysis_kind', 'metric_refs', 'dimension_refs', 'recipe_refs', 'function_refs', 'unresolved_slots'}
_v2cROUTE_KEYS = {'contract_version', 'route', 'reason_code', 'resolved_candidate_bundle_sha256', 'selected_candidate_ids', 'required_slots', 'unresolved_slots', 'ambiguity_sets', 'route_policy_version', 'eligibility_proof_sha256'}

def build_generic_v2_candidate_bundle(request: dict[str, Any], catalog: dict[str, Any], *, prior_semantics: dict[str, Any] | None=None, prior_result: dict[str, Any] | None=None) -> dict[str, Any]:
    """Build the canonical runtime bundle consumed by the v2 intent resolver."""
    _v2c_validate_catalog(catalog)
    request_id = str(request.get('request_id') or '')
    if not request_id:
        _v2c_fail('intent_contract_error', 'candidate_routing', 'request_id가 필요합니다.')
    question = normalize_text(str(request.get('question') or ''))
    if not question:
        _v2c_fail('intent_contract_error', 'candidate_routing', '질문이 비어 있습니다.')
    matches = _v2c_collect_registered_matches(question, catalog)
    pools = {pool_key: deepcopy(matches.get(target_type, [])) for target_type, pool_key in _v2cMATCH_POOL_KEYS.items()}
    ambiguity = _v2c_alias_ambiguity(matches)
    unsupported_signals = [term for term in _v2cUNSUPPORTED_LEXEMES if _v2c_contains(question, term)]
    operation_cues = _v2c_operation_cues(question, request)
    evaluations: list[dict[str, Any]] = []
    if not unsupported_signals:
        evaluations.extend(_v2c_evaluate_registered_functions(request, catalog, matches, prior_semantics=prior_semantics, prior_result=prior_result))
        evaluations.extend(_v2c_evaluate_registered_recipes(request, catalog, matches, operation_cues, prior_semantics=prior_semantics, prior_result=prior_result))
        if not evaluations:
            evaluations.extend(_v2c_evaluate_composition(request, catalog, matches, operation_cues, prior_semantics=prior_semantics, prior_result=prior_result))
    expanded: list[dict[str, Any]] = []
    for evaluation in evaluations:
        expanded.extend(_v2c_expand_ambiguous_semantics(evaluation, ambiguity))
    evaluations = _v2c_dedupe_evaluations(expanded or evaluations)
    complete = [item for item in evaluations if not item['unresolved_slots']]
    if complete:
        highest_score = max((int(item['score']) for item in complete))
        complete = [item for item in complete if int(item['score']) == highest_score]
    complete = complete[:_v2cMAX_INTENT_CANDIDATES]
    intent_candidates = [_v2c_seal_candidate(item) for item in complete]
    if unsupported_signals or not intent_candidates:
        route_name = 'unsupported'
        reason_code = 'unsupported_registry_gap'
    elif len(intent_candidates) == 1:
        route_name = 'deterministic'
        reason_code = 'unique_complete_selection'
    else:
        route_name = 'intent_llm'
        reason_code = 'ambiguous_candidate_selection' if ambiguity else 'semantic_choice_required'
    prompt_cards = [_v2c_prompt_card(item) for item in intent_candidates]
    material = {'request_id': request_id, 'catalog_sha256': str(catalog.get('catalog_sha256') or ''), **pools, 'intent_candidates': intent_candidates, 'prompt_cards': prompt_cards}
    bundle_sha256 = sha256_json(material)
    selected_ids = [intent_candidates[0]['candidate_id']] if route_name == 'deterministic' else []
    required_slots = _v2c_stable((slot for candidate in intent_candidates for slot in candidate.get('required_slots') or []))
    unresolved_slots = ['intent_candidate_id'] if route_name == 'intent_llm' else ['registry_gap'] if route_name == 'unsupported' else []
    ambiguity_sets = [item['identities'] for item in ambiguity]
    proof_material = _v2c_route_proof_material(bundle_sha256=bundle_sha256, route=route_name, reason_code=reason_code, candidate_ids=[item['candidate_id'] for item in intent_candidates], selected_candidate_ids=selected_ids, required_slots=required_slots, unresolved_slots=unresolved_slots, ambiguity_sets=ambiguity_sets, unsupported_signals=unsupported_signals)
    route_decision = {'contract_version': _v2cROUTE_VERSION, 'route': route_name, 'reason_code': reason_code, 'resolved_candidate_bundle_sha256': bundle_sha256, 'selected_candidate_ids': selected_ids, 'required_slots': required_slots, 'unresolved_slots': unresolved_slots, 'ambiguity_sets': ambiguity_sets, 'route_policy_version': _v2cROUTE_POLICY_VERSION, 'eligibility_proof_sha256': sha256_json(proof_material)}
    registry_gaps = _v2c_stable((gap for item in evaluations if item.get('unresolved_slots') for gap in item['unresolved_slots']))
    route_evidence = {'ambiguity': ambiguity, 'unsupported_signals': unsupported_signals, 'registry_gaps': registry_gaps, 'rejected_candidate_count': len(evaluations) - len(complete)}
    bundle = {'contract_version': _v2cBUNDLE_VERSION, **material, 'bundle_sha256': bundle_sha256, 'route_decision': route_decision, 'route_evidence': route_evidence}
    validate_generic_v2_candidate_bundle(bundle, catalog=catalog)
    return bounded(bundle, _v2cMAX_BUNDLE_BYTES, 'generic_v2_candidate_bundle')

def validate_generic_v2_candidate_bundle(bundle: dict[str, Any], catalog: dict[str, Any] | None=None) -> dict[str, Any]:
    """Validate the entire runtime shape, hashes, references, and route proof."""
    if not isinstance(bundle, dict) or set(bundle) != _v2cTOP_LEVEL_KEYS:
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'candidate bundle 최상위 필드가 닫힌 계약과 다릅니다.', {'actual_keys': sorted(bundle) if isinstance(bundle, dict) else []})
    if bundle.get('contract_version') != _v2cBUNDLE_VERSION:
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'candidate bundle 버전이 올바르지 않습니다.')
    if catalog is not None:
        _v2c_validate_catalog(catalog)
        if bundle.get('catalog_sha256') != catalog.get('catalog_sha256'):
            _v2c_fail('metadata_dependency_error', 'candidate_bundle_validation', 'candidate bundle의 catalog hash가 다릅니다.')
    for pool_key in _v2cMATCH_POOL_KEYS.values():
        pool = bundle.get(pool_key)
        if not isinstance(pool, list) or len(pool) > _v2cMAX_MATCHES_PER_TYPE:
            _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'candidate match pool이 올바르지 않습니다.', {'pool': pool_key})
        for match in pool:
            _v2c_validate_match(match, catalog)
    candidates = bundle.get('intent_candidates')
    if not isinstance(candidates, list) or len(candidates) > _v2cMAX_INTENT_CANDIDATES:
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'intent candidate 목록이 올바르지 않습니다.')
    candidate_ids: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict) or set(candidate) != _v2cINTENT_CANDIDATE_KEYS:
            _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'intent candidate 필드가 닫힌 계약과 다릅니다.')
        candidate_id = str(candidate.get('candidate_id') or '')
        if not candidate_id or candidate_id in candidate_ids:
            _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'intent candidate id가 없거나 중복됩니다.')
        candidate_ids.append(candidate_id)
        semantics = candidate.get('semantics')
        if not isinstance(semantics, dict) or candidate.get('semantics_sha256') != sha256_json(semantics):
            _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'intent candidate semantics hash가 다릅니다.')
        if catalog is not None:
            _v2c_validate_semantic_references(semantics, catalog)
        required = candidate.get('required_slots')
        resolved = candidate.get('resolved_slots')
        if not isinstance(required, list) or not isinstance(resolved, list) or (not set(required).issubset(set(resolved))):
            _v2c_fail('route_contract_error', 'candidate_bundle_validation', '완료 candidate의 필수 slot이 해소되지 않았습니다.')
    cards = bundle.get('prompt_cards')
    if not isinstance(cards, list) or len(cards) != len(candidates):
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'prompt card 수가 candidate와 다릅니다.')
    for card, candidate in zip(cards, candidates, strict=True):
        if not isinstance(card, dict) or set(card) != _v2cPROMPT_CARD_KEYS or card != _v2c_prompt_card(candidate):
            _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'prompt card가 닫힌 candidate projection과 다릅니다.')
    material = _v2c_bundle_material(bundle)
    if bundle.get('bundle_sha256') != sha256_json(material):
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'candidate bundle hash가 다릅니다.')
    route = bundle.get('route_decision')
    if not isinstance(route, dict) or set(route) != _v2cROUTE_KEYS:
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'route decision 필드가 닫힌 계약과 다릅니다.')
    if route.get('contract_version') != _v2cROUTE_VERSION or route.get('route_policy_version') != _v2cROUTE_POLICY_VERSION:
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'route contract 버전이 올바르지 않습니다.')
    if route.get('resolved_candidate_bundle_sha256') != bundle.get('bundle_sha256'):
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'route가 다른 candidate bundle을 참조합니다.')
    route_name = str(route.get('route') or '')
    selected_ids = list(route.get('selected_candidate_ids') or [])
    if route_name == 'deterministic':
        if len(candidates) != 1 or selected_ids != candidate_ids or route.get('unresolved_slots'):
            _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'deterministic route는 유일하고 완전한 candidate가 필요합니다.')
        if route.get('reason_code') != 'unique_complete_selection':
            _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'deterministic route reason이 올바르지 않습니다.')
    elif route_name == 'intent_llm':
        if len(candidates) < 2 or selected_ids or route.get('unresolved_slots') != ['intent_candidate_id']:
            _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'intent_llm route는 둘 이상의 완전한 candidate만 허용합니다.')
    elif route_name == 'unsupported':
        if candidates or selected_ids or route.get('reason_code') != 'unsupported_registry_gap':
            _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'unsupported route는 실행 candidate를 포함할 수 없습니다.')
    else:
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', '알 수 없는 route입니다.')
    route_evidence = bundle.get('route_evidence')
    if not isinstance(route_evidence, dict) or set(route_evidence) != {'ambiguity', 'unsupported_signals', 'registry_gaps', 'rejected_candidate_count'}:
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'route evidence 필드가 닫힌 계약과 다릅니다.')
    proof = _v2c_route_proof_material(bundle_sha256=str(bundle['bundle_sha256']), route=route_name, reason_code=str(route.get('reason_code') or ''), candidate_ids=candidate_ids, selected_candidate_ids=selected_ids, required_slots=list(route.get('required_slots') or []), unresolved_slots=list(route.get('unresolved_slots') or []), ambiguity_sets=list(route.get('ambiguity_sets') or []), unsupported_signals=list(route_evidence.get('unsupported_signals') or []))
    if route.get('eligibility_proof_sha256') != sha256_json(proof):
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'route eligibility proof가 다릅니다.')
    return bundle

def normalize_generic_v2_intent(request: dict[str, Any], bundle: dict[str, Any], *, selected_candidate_id: str | None=None) -> dict[str, Any]:
    """Normalize a deterministic or model-selected closed candidate to intent."""
    validate_generic_v2_candidate_bundle(bundle)
    if str(request.get('request_id') or '') != str(bundle.get('request_id') or ''):
        _v2c_fail('intent_contract_error', 'intent_normalization', 'request와 candidate bundle identity가 다릅니다.')
    route = bundle['route_decision']
    route_name = str(route['route'])
    candidates = bundle['intent_candidates']
    if route_name == 'unsupported':
        _v2c_fail('unsupported_operation', 'route_eligibility', '등록된 metadata와 typed operator로 처리할 수 없는 질문입니다.', {'reason_code': route.get('reason_code')})
    if route_name == 'deterministic':
        expected = str(candidates[0]['candidate_id'])
        if selected_candidate_id not in (None, '', expected):
            _v2c_fail('intent_contract_error', 'intent_normalization', 'deterministic candidate 선택값이 route proof와 다릅니다.')
        selected_candidate_id = expected
        generator = 'deterministic'
    else:
        if not selected_candidate_id:
            _v2c_fail('intent_contract_error', 'intent_normalization', 'intent_llm candidate 선택값이 필요합니다.')
        generator = 'llm'
    selected = next((item for item in candidates if item.get('candidate_id') == selected_candidate_id), None)
    if not isinstance(selected, dict):
        _v2c_fail('intent_contract_error', 'intent_decoding', 'candidate 목록 밖의 값을 선택했습니다.', {'candidate_id': str(selected_candidate_id or '')})
    material = {'contract_version': _v2cINTENT_VERSION, 'request_id': request.get('request_id'), 'candidate_bundle_sha256': bundle.get('bundle_sha256'), 'intent_candidate_id': selected_candidate_id, 'semantics': deepcopy(selected['semantics']), 'route': route_name, 'intent_generator': generator}
    return {**material, 'intent_sha256': sha256_json(material)}

def _v2c_collect_registered_matches(question: str, catalog: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    aliases: dict[tuple[str, str], list[dict[str, Any]]] = {}

    def register_values(target_type: str, target_key: str, values: Any, spec: Mapping[str, Any] | None=None) -> None:
        policy = spec or {}
        match_rule = str(policy.get('match') or 'bounded_longest')
        conflict = str(policy.get('conflict') or 'fail_ambiguous')
        for raw in values if isinstance(values, list) else [values]:
            if isinstance(raw, Mapping):
                texts = _v2c_strings(raw)
                priority = int(raw.get('priority') or 100)
            else:
                texts = _v2c_strings(raw)
                priority = 100
            for text in texts:
                if text:
                    aliases.setdefault((target_type, target_key), []).append({'text': text, 'priority': priority, 'match': match_rule, 'conflict': conflict})
    for spec in (catalog.get('aliases') or {}).values():
        if not isinstance(spec, dict):
            continue
        target_type = str(spec.get('target_type') or '')
        target_key = str(spec.get('target_key') or '')
        if _v2c_registered(catalog, target_type, target_key):
            register_values(target_type, target_key, spec.get('values') or [], spec)
    for target_type, section in _v2cCATALOG_TARGET_SECTIONS.items():
        for key, spec in (catalog.get(section) or {}).items():
            if not isinstance(spec, dict):
                continue
            register_values(target_type, str(key), spec.get('aliases') or [])
    for card in catalog.get('specialized_functions') or []:
        if not isinstance(card, dict):
            continue
        identity = _v2c_function_identity(card)
        if identity:
            register_values('function', identity, card.get('aliases') or [])
    raw_result: dict[str, list[dict[str, Any]]] = {target_type: [] for target_type in _v2cMATCH_POOL_KEYS}
    seen: set[tuple[str, str, int, int]] = set()
    for (target_type, identity), values in aliases.items():
        values = sorted(values, key=lambda value: (-len(str(value['text'])), -int(value['priority']), str(value['text']).casefold()))
        for alias_contract in values:
            alias = str(alias_contract['text'])
            for start, end in _v2c_alias_spans(question, alias):
                marker = (target_type, identity, start, end)
                if marker in seen:
                    continue
                seen.add(marker)
                raw_result[target_type].append({'candidate_id': f'match:{target_type}:{identity}:{start}:{end}', 'target_type': target_type, 'identity': identity, 'alias': alias, 'evidence': {'text': question[start:end], 'start': start, 'end': end}, 'match_rule': 'registered_alias', '_registry_match': str(alias_contract['match']), '_priority': int(alias_contract['priority']), '_conflict': str(alias_contract['conflict'])})
    result: dict[str, list[dict[str, Any]]] = {target_type: [] for target_type in _v2cMATCH_POOL_KEYS}
    for target_type, values in raw_result.items():
        selected: list[dict[str, Any]] = []
        for candidate in values:
            start = int(candidate['evidence']['start'])
            end = int(candidate['evidence']['end'])
            length = end - start
            containing = [other for other in values if int(other['evidence']['start']) <= start and int(other['evidence']['end']) >= end and (int(other['evidence']['end']) - int(other['evidence']['start']) > length) and (str(other.get('_registry_match') or '') == 'bounded_longest')]
            if containing:
                continue
            same_span = [other for other in values if int(other['evidence']['start']) == start and int(other['evidence']['end']) == end]
            best_priority = max((int(other.get('_priority') or 0) for other in same_span))
            if int(candidate.get('_priority') or 0) < best_priority:
                continue
            clean = {key: deepcopy(value) for key, value in candidate.items() if not key.startswith('_')}
            selected.append(clean)
        selected.sort(key=lambda item: (int(item['evidence']['start']), -len(str(item['alias'])), str(item['identity'])))
        result[target_type] = selected[:_v2cMAX_MATCHES_PER_TYPE]
    return result

def _v2c_evaluate_registered_functions(request: dict[str, Any], catalog: dict[str, Any], matches: dict[str, list[dict[str, Any]]], *, prior_semantics: dict[str, Any] | None, prior_result: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Create candidates only from directly matched, pinned function cards."""
    date, date_explicit = _v2c_date_semantics(request)
    evaluations: list[dict[str, Any]] = []
    for function_ref in _v2c_matched_ids(matches, 'function'):
        raw_card = _v2c_function_card(catalog, function_ref)
        card = validate_registered_function_card(raw_card)
        required_fields = _v2c_stable(card.get('required_fields') or [])
        output_fields = _v2c_stable((card.get('call_template') or {}).get('output_fields') or [])
        all_fields = _v2c_stable([*required_fields, *output_fields])
        missing = [field for field in all_fields if field not in (catalog.get('fields') or {})]
        dataset_ref = str((card.get('call_template') or {}).get('dataset_ref') or '')
        dataset = (catalog.get('datasets') or {}).get(dataset_ref)
        if not isinstance(dataset, dict):
            missing.append('function_dataset_ref')
            dataset_refs: list[str] = []
        else:
            dataset_refs = [dataset_ref]
            unavailable = [field for field in all_fields if field not in (dataset.get('fields') or {})]
            if unavailable:
                missing.extend((f'function_dataset_field:{field}' for field in unavailable))
        semantics = {'request_scope': _v2c_request_scope(request, set()), 'analysis_kind': 'registered_call', 'metric_refs': [], 'dimension_refs': [], 'field_refs': output_fields, 'dataset_refs': dataset_refs, 'relation_refs': [], 'recipe_refs': [], 'function_refs': [function_ref], 'formula_refs': [], 'grain_refs': [], 'entity_group_refs': [], 'filter_refs': [], 'thresholds': [], 'date': date, 'date_explicit': date_explicit, 'reference_date': str(request.get('reference_instant') or '')[:10], 'reference_instant': str(request.get('reference_instant') or ''), 'rank': None, 'tie_policy': 'exact_n', 'sort': None, 'followup': bool(request.get('state_ref')), 'followup_mode': 'referenced' if request.get('state_ref') else 'none'}
        semantics = _v2c_inherit_prior(semantics, prior_semantics, prior_result)
        evidence_refs = _v2c_stable((item.get('candidate_id') for item in matches.get('function', []) if item.get('identity') == function_ref))
        evaluations.append({'description': f'registered function {function_ref}', 'semantics': semantics, 'required_slots': ['function_ref'], 'resolved_slots': [] if missing else ['function_ref'], 'unresolved_slots': _v2c_stable(missing), 'evidence_refs': evidence_refs, 'score': 200})
    return evaluations

def _v2c_evaluate_registered_recipes(request: dict[str, Any], catalog: dict[str, Any], matches: dict[str, list[dict[str, Any]]], cues: set[str], *, prior_semantics: dict[str, Any] | None, prior_result: dict[str, Any] | None) -> list[dict[str, Any]]:
    recipe_match_ids = set(_v2c_matched_ids(matches, 'recipe'))
    requested_metrics = _v2c_matched_ids(matches, 'metric')
    requested_fields = _v2c_matched_ids(matches, 'field')
    has_registered_evidence = any((matches.get(target_type) for target_type in _v2cMATCH_POOL_KEYS))
    evaluations: list[dict[str, Any]] = []
    for recipe_id, recipe in sorted((catalog.get('recipes') or {}).items()):
        if not isinstance(recipe, dict):
            continue
        template = recipe.get('default_operation_template') if isinstance(recipe.get('default_operation_template'), dict) else {}
        template_ops = _v2c_template_ops(template)
        if not template_ops or not template_ops.issubset(_v2cALLOWED_TEMPLATE_OPERATIONS):
            continue
        template_metrics = _v2c_template_values(template, {'metric', 'metrics', 'left_metric', 'right_metric', 'numerator_metric', 'denominator_metric'})
        template_fields = _v2c_template_values(template, {'group_by', 'allowed_fields', 'left_field', 'right_field', 'stable_tie_break'})
        root_op = str(template.get('op') or '')
        cue_score = _v2c_operation_alignment_score(cues, template_ops, root_op)
        metric_overlap = len(set(requested_metrics) & set(template_metrics))
        field_overlap = len(set(requested_fields) & set(template_fields))
        alias_match = str(recipe_id) in recipe_match_ids
        if not alias_match and (not has_registered_evidence):
            continue
        if not alias_match and cue_score <= 0:
            continue
        if not alias_match and requested_metrics and template_metrics and (not metric_overlap):
            continue
        if root_op == 'project' and (not requested_fields) and (not _v2c_template_values(template, {'fields'})):
            continue
        score = (100 if alias_match else 0) + cue_score + 12 * metric_overlap + 6 * field_overlap
        semantics, unresolved, resolved = _v2c_semantics_for_recipe(request, catalog, matches, cues, str(recipe_id), recipe, prior_semantics=prior_semantics, prior_result=prior_result)
        required = _v2c_stable(recipe.get('required_slots') or [])
        evidence_refs = [item['candidate_id'] for target_type in _v2cMATCH_POOL_KEYS for item in matches.get(target_type, []) if item['identity'] in set(_v2c_semantic_refs(semantics, target_type))]
        evaluations.append({'description': str(recipe.get('display_name') or recipe_id), 'semantics': semantics, 'required_slots': required, 'resolved_slots': resolved, 'unresolved_slots': unresolved, 'evidence_refs': _v2c_stable(evidence_refs), 'score': score})
    return evaluations

def _v2c_evaluate_composition(request: dict[str, Any], catalog: dict[str, Any], matches: dict[str, list[dict[str, Any]]], cues: set[str], *, prior_semantics: dict[str, Any] | None, prior_result: dict[str, Any] | None) -> list[dict[str, Any]]:
    metrics = _v2c_root_metric_refs(catalog, _v2c_matched_ids(matches, 'metric'), request=request, matches=matches)
    raw_fields = _v2c_matched_ids(matches, 'field')
    fields = _v2c_visible_field_refs(request, catalog, matches)
    datasets = _v2c_matched_ids(matches, 'dataset')
    grains = _v2c_matched_ids(matches, 'grain')
    relations = _v2c_matched_ids(matches, 'relation')
    entity_groups = _v2c_matched_ids(matches, 'entity_group')
    filter_refs, thresholds, filter_gaps = _v2c_registered_filter_literals(request, catalog, matches)
    scalar_comparison = any((isinstance(item, dict) and str(item.get('operator') or '') in {'gt', 'gte', 'lt', 'lte'} for item in filter_refs))
    rank = _v2c_rank_semantics(request)
    if rank:
        analysis_kind = 'rank'
    elif 'project' in cues:
        analysis_kind = 'projection'
    elif 'compare_fields' in cues and len(metrics) >= 2:
        analysis_kind = 'compare_fields'
    elif scalar_comparison and fields and ('detail' in cues):
        analysis_kind = 'detail'
    elif 'join' in cues:
        analysis_kind = 'join'
    elif metrics:
        analysis_kind = 'aggregate'
    elif fields:
        analysis_kind = 'detail'
    else:
        return []
    if analysis_kind in {'projection', 'detail'}:
        metrics = []
    dimensions = _v2c_dimension_refs(catalog, fields, grains, analysis_kind)
    formula_refs = [metric for metric in metrics if isinstance((catalog.get('metrics') or {}).get(metric, {}).get('formula'), dict)]
    metric_sources, metric_gaps = _v2c_metric_source_datasets(catalog, metrics, request=request, explicit_datasets=datasets)
    dataset_refs = _v2c_stable([*datasets, *metric_sources])
    field_sources, field_gaps = _v2c_field_source_datasets(catalog, raw_fields, dataset_refs)
    dataset_refs = _v2c_stable([*dataset_refs, *field_sources])
    relation_refs, relation_gaps = _v2c_relation_path_refs(catalog, dataset_refs, relations)
    date, date_explicit = _v2c_date_semantics(request)
    semantics = {'request_scope': _v2c_request_scope(request, cues), 'analysis_kind': analysis_kind, 'metric_refs': metrics, 'dimension_refs': dimensions, 'field_refs': fields, 'dataset_refs': dataset_refs, 'relation_refs': relation_refs, 'recipe_refs': [], 'function_refs': [], 'formula_refs': formula_refs, 'grain_refs': grains, 'entity_group_refs': entity_groups, 'filter_refs': filter_refs, 'thresholds': thresholds, 'date': date, 'date_explicit': date_explicit, 'reference_date': str(request.get('reference_instant') or '')[:10], 'reference_instant': str(request.get('reference_instant') or ''), 'rank': rank, 'tie_policy': _v2c_tie_policy(str(request.get('question') or ''), rank), 'sort': _v2c_sort_semantics(str(request.get('question') or ''), metrics), 'followup': bool(request.get('state_ref')), 'followup_mode': 'referenced' if _v2c_request_scope(request, cues) != 'new_analysis' else 'none'}
    if analysis_kind == 'compare_fields':
        comparison_operator = _v2c_comparison_operator(str(request.get('question') or ''))
        if comparison_operator:
            semantics['comparison_operator'] = comparison_operator
    semantics = _v2c_inherit_prior(semantics, prior_semantics, prior_result)
    unresolved = [*metric_gaps, *field_gaps, *relation_gaps, *filter_gaps]
    if analysis_kind in {'aggregate', 'rank', 'compare_fields'} and (not metrics):
        unresolved.append('metric_ref')
    if analysis_kind == 'rank' and (not rank):
        unresolved.extend(['rank_direction', 'rank_limit'])
    if analysis_kind == 'rank' and (not dimensions):
        unresolved.append('grain_ref')
    if analysis_kind in {'projection', 'detail'} and (not fields):
        unresolved.append('project_fields')
    if analysis_kind == 'join' and (not relation_refs):
        unresolved.append('relation_ref')
    required: list[str] = []
    if analysis_kind in {'aggregate', 'rank', 'compare_fields'}:
        required.append('metric_ref')
    if analysis_kind == 'rank':
        required.extend(['rank_direction', 'rank_limit', 'grain_ref'])
    if analysis_kind in {'projection', 'detail'}:
        required.append('project_fields')
    if analysis_kind == 'join':
        required.append('relation_ref')
    required = _v2c_stable(required)
    resolved = [slot for slot in required if slot not in set(unresolved)]
    return [{'description': f'registered {analysis_kind}', 'semantics': semantics, 'required_slots': required, 'resolved_slots': resolved, 'unresolved_slots': _v2c_stable(unresolved), 'evidence_refs': _v2c_stable((item['candidate_id'] for values in matches.values() for item in values)), 'score': 10 + 5 * len(metrics) + 2 * len(fields)}]

def _v2c_semantics_for_recipe(request: dict[str, Any], catalog: dict[str, Any], matches: dict[str, list[dict[str, Any]]], cues: set[str], recipe_id: str, recipe: dict[str, Any], *, prior_semantics: dict[str, Any] | None, prior_result: dict[str, Any] | None) -> tuple[dict[str, Any], list[str], list[str]]:
    template = deepcopy(recipe.get('default_operation_template') or {})
    ops = _v2c_template_ops(template)
    requested_metrics = _v2c_matched_ids(matches, 'metric')
    template_metrics = _v2c_template_values(template, {'metric', 'metrics', 'left_metric', 'right_metric', 'numerator_metric', 'denominator_metric'})
    metric_refs = _v2c_root_metric_refs(catalog, _v2c_stable(requested_metrics or template_metrics), request=request, matches=matches)
    raw_fields = _v2c_matched_ids(matches, 'field')
    requested_fields = _v2c_visible_field_refs(request, catalog, matches)
    allowed_fields = _v2c_template_values(template, {'allowed_fields'})
    default_fields = _v2c_template_values(template, {'fields'})
    if str(template.get('op') or '') == 'project':
        field_refs = [field for field in requested_fields if field in set(allowed_fields)]
        if not field_refs and default_fields:
            field_refs = [field for field in default_fields if field in (catalog.get('fields') or {})]
    else:
        field_refs = requested_fields
    grain_ids = _v2c_matched_ids(matches, 'grain')
    template_grain = str(template.get('grain_id') or '')
    if template_grain and template_grain in (catalog.get('grains') or {}) and (template_grain not in grain_ids):
        grain_ids.append(template_grain)
    dimensions = _v2c_dimension_refs(catalog, field_refs, grain_ids, _v2c_dominant_operation(ops, cues))
    template_groups = _v2c_template_values(template, {'group_by'})
    if template_groups and (not dimensions):
        dimensions = [field for field in template_groups if field in (catalog.get('fields') or {})]
    analysis_kind = _v2c_dominant_operation(ops, cues)
    if analysis_kind in {'projection', 'detail'}:
        metric_refs = []
    formula_refs = [metric for metric in metric_refs if isinstance((catalog.get('metrics') or {}).get(metric, {}).get('formula'), dict)]
    relation_refs = _v2c_template_values(template, {'relation_id'})
    relation_refs = [relation for relation in relation_refs if relation in (catalog.get('relations') or {})]
    dataset_refs = _v2c_stable([*_v2c_matched_ids(matches, 'dataset'), *_v2c_template_values(template, {'dataset_key', 'dataset_keys'})])
    dataset_refs = [item for item in dataset_refs if item in (catalog.get('datasets') or {})]
    metric_sources, metric_gaps = _v2c_metric_source_datasets(catalog, metric_refs, request=request, explicit_datasets=_v2c_matched_ids(matches, 'dataset'))
    dataset_refs = _v2c_stable([*dataset_refs, *metric_sources])
    field_sources, field_gaps = _v2c_field_source_datasets(catalog, raw_fields, dataset_refs)
    dataset_refs = _v2c_stable([*dataset_refs, *field_sources])
    for relation_id in relation_refs:
        relation = catalog['relations'][relation_id]
        dataset_refs = _v2c_stable([*dataset_refs, relation.get('left_dataset'), relation.get('right_dataset')])
    path_relations, relation_gaps = _v2c_relation_path_refs(catalog, dataset_refs, relation_refs)
    relation_refs = _v2c_stable([*relation_refs, *path_relations])
    filter_refs, thresholds, filter_gaps = _v2c_registered_filter_literals(request, catalog, matches)
    rank = _v2c_rank_semantics(request)
    date, date_explicit = _v2c_date_semantics(request)
    semantics = {'request_scope': _v2c_request_scope(request, cues), 'analysis_kind': analysis_kind, 'metric_refs': metric_refs, 'dimension_refs': dimensions, 'field_refs': field_refs, 'dataset_refs': dataset_refs, 'relation_refs': relation_refs, 'recipe_refs': [recipe_id], 'function_refs': [], 'formula_refs': formula_refs, 'grain_refs': grain_ids, 'entity_group_refs': _v2c_matched_ids(matches, 'entity_group'), 'filter_refs': filter_refs, 'thresholds': thresholds, 'date': date, 'date_explicit': date_explicit, 'reference_date': str(request.get('reference_instant') or '')[:10], 'reference_instant': str(request.get('reference_instant') or ''), 'rank': rank, 'tie_policy': _v2c_tie_policy(str(request.get('question') or ''), rank), 'sort': _v2c_sort_semantics(str(request.get('question') or ''), metric_refs), 'followup': bool(request.get('state_ref')), 'followup_mode': 'referenced' if _v2c_request_scope(request, cues) != 'new_analysis' else 'none'}
    if analysis_kind == 'compare_fields':
        comparison_operator = _v2c_comparison_operator(str(request.get('question') or ''))
        if comparison_operator:
            semantics['comparison_operator'] = comparison_operator
    semantics = _v2c_inherit_prior(semantics, prior_semantics, prior_result)
    required = _v2c_stable(recipe.get('required_slots') or [])
    resolved: list[str] = []
    unresolved: list[str] = [*metric_gaps, *field_gaps, *relation_gaps, *filter_gaps]
    for slot in required:
        if slot == 'date_scope' and date:
            resolved.append(slot)
        elif slot == 'rank_direction' and rank and (rank.get('mode') in {'top', 'bottom'}):
            resolved.append(slot)
        elif slot == 'rank_limit' and rank and (int(rank.get('limit') or 0) > 0):
            resolved.append(slot)
        elif slot == 'project_fields' and field_refs:
            resolved.append(slot)
        elif slot in semantics and semantics.get(slot) not in (None, '', [], {}):
            resolved.append(slot)
        else:
            unresolved.append(slot)
    if 'rank' in ops:
        if not metric_refs:
            unresolved.append('metric_ref')
        if not dimensions:
            unresolved.append('grain_ref')
        if not rank:
            unresolved.extend(['rank_direction', 'rank_limit'])
    if 'project' in ops and str(template.get('op') or '') == 'project' and (not field_refs):
        unresolved.append('project_fields')
    if 'join' in ops and (not relation_refs):
        unresolved.append('relation_ref')
    return (semantics, _v2c_stable(unresolved), _v2c_stable(resolved))

def _v2c_expand_ambiguous_semantics(evaluation: dict[str, Any], ambiguity: list[dict[str, Any]]) -> list[dict[str, Any]]:
    relevant: list[tuple[str, list[str]]] = []
    semantics = evaluation.get('semantics') or {}
    for item in ambiguity:
        ref_key = {'metric': 'metric_refs', 'field': 'field_refs', 'dataset': 'dataset_refs', 'recipe': 'recipe_refs', 'grain': 'grain_refs', 'relation': 'relation_refs', 'entity_group': 'entity_group_refs', 'function': 'function_refs'}.get(str(item.get('target_type') or ''))
        identities = list(item.get('identities') or [])
        if ref_key and len(set(identities) & set(semantics.get(ref_key) or [])) > 1:
            relevant.append((ref_key, identities))
    if not relevant:
        return [evaluation]
    variants: list[dict[str, Any]] = []
    choices = [identities for _ref_key, identities in relevant]
    for selected_values in product(*choices):
        if len(variants) >= _v2cMAX_AMBIGUITY_VARIANTS:
            break
        variant = deepcopy(evaluation)
        for (ref_key, identities), selected in zip(relevant, selected_values, strict=True):
            current = [item for item in variant['semantics'].get(ref_key) or [] if item not in identities]
            variant['semantics'][ref_key] = _v2c_stable([*current, selected])
        variant['score'] = int(variant['score'])
        variants.append(variant)
    return variants

def _v2c_seal_candidate(evaluation: dict[str, Any]) -> dict[str, Any]:
    semantics = deepcopy(evaluation['semantics'])
    semantics_sha = sha256_json(semantics)
    recipe_part = '+'.join(semantics.get('recipe_refs') or semantics.get('function_refs') or [semantics.get('analysis_kind') or 'registered'])
    candidate_id = f'intent:{recipe_part}:{semantics_sha[:16]}'
    return {'candidate_id': candidate_id, 'description': str(evaluation.get('description') or semantics.get('analysis_kind') or 'registered intent'), 'semantics': semantics, 'semantics_sha256': semantics_sha, 'required_slots': _v2c_stable(evaluation.get('required_slots') or []), 'resolved_slots': _v2c_stable(evaluation.get('resolved_slots') or []), 'evidence_refs': _v2c_stable(evaluation.get('evidence_refs') or [])}

def _v2c_prompt_card(candidate: dict[str, Any]) -> dict[str, Any]:
    semantics = candidate.get('semantics') or {}
    return {'candidate_id': candidate.get('candidate_id'), 'description': candidate.get('description'), 'analysis_kind': semantics.get('analysis_kind'), 'metric_refs': list(semantics.get('metric_refs') or []), 'dimension_refs': list(semantics.get('dimension_refs') or []), 'recipe_refs': list(semantics.get('recipe_refs') or []), 'function_refs': list(semantics.get('function_refs') or []), 'unresolved_slots': []}

def _v2c_bundle_material(bundle: dict[str, Any]) -> dict[str, Any]:
    return {'request_id': bundle.get('request_id'), 'catalog_sha256': bundle.get('catalog_sha256'), **{pool_key: bundle.get(pool_key) for pool_key in _v2cMATCH_POOL_KEYS.values()}, 'intent_candidates': bundle.get('intent_candidates'), 'prompt_cards': bundle.get('prompt_cards')}

def _v2c_route_proof_material(*, bundle_sha256: str, route: str, reason_code: str, candidate_ids: list[str], selected_candidate_ids: list[str], required_slots: list[str], unresolved_slots: list[str], ambiguity_sets: list[list[str]], unsupported_signals: list[str]) -> dict[str, Any]:
    return {'route_policy_version': _v2cROUTE_POLICY_VERSION, 'bundle_sha256': bundle_sha256, 'route': route, 'reason_code': reason_code, 'candidate_ids': candidate_ids, 'selected_candidate_ids': selected_candidate_ids, 'required_slots': required_slots, 'unresolved_slots': unresolved_slots, 'ambiguity_sets': ambiguity_sets, 'unsupported_signals': unsupported_signals}

def _v2c_validate_catalog(catalog: dict[str, Any]) -> None:
    if not isinstance(catalog, dict) or catalog.get('contract_version') != _v2cCATALOG_VERSION:
        _v2c_fail('metadata_dependency_error', 'candidate_routing', 'metadata.runtime.catalog.v2가 필요합니다.')
    actual_hash = str(catalog.get('catalog_sha256') or '')
    expected_hash = sha256_json({key: value for key, value in catalog.items() if key != 'catalog_sha256'})
    if actual_hash != expected_hash:
        _v2c_fail('metadata_dependency_error', 'candidate_routing', 'runtime catalog hash가 다릅니다.', {'expected': expected_hash, 'actual': actual_hash})
    for section in _v2cCATALOG_TARGET_SECTIONS.values():
        if not isinstance(catalog.get(section), dict):
            _v2c_fail('metadata_dependency_error', 'candidate_routing', 'runtime catalog registry가 올바르지 않습니다.', {'section': section})
    if not isinstance(catalog.get('specialized_functions'), list):
        _v2c_fail('metadata_dependency_error', 'candidate_routing', 'runtime catalog specialized function registry must be an array.')

def _v2c_validate_match(match: Any, catalog: dict[str, Any] | None) -> None:
    keys = {'candidate_id', 'target_type', 'identity', 'alias', 'evidence', 'match_rule'}
    if not isinstance(match, dict) or set(match) != keys or match.get('match_rule') != 'registered_alias':
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'alias match candidate가 올바르지 않습니다.')
    evidence = match.get('evidence')
    if not isinstance(evidence, dict) or set(evidence) != {'text', 'start', 'end'}:
        _v2c_fail('route_contract_error', 'candidate_bundle_validation', 'alias evidence가 올바르지 않습니다.')
    if catalog is not None and (not _v2c_registered(catalog, str(match.get('target_type') or ''), str(match.get('identity') or ''))):
        _v2c_fail('metadata_dependency_error', 'candidate_bundle_validation', '미등록 alias target입니다.')

def _v2c_validate_semantic_references(semantics: dict[str, Any], catalog: dict[str, Any]) -> None:
    for target_type, key in (('metric', 'metric_refs'), ('field', 'field_refs'), ('field', 'dimension_refs'), ('dataset', 'dataset_refs'), ('relation', 'relation_refs'), ('recipe', 'recipe_refs'), ('grain', 'grain_refs'), ('entity_group', 'entity_group_refs'), ('metric', 'formula_refs'), ('function', 'function_refs')):
        for identity in semantics.get(key) or []:
            if not _v2c_registered(catalog, target_type, str(identity)):
                _v2c_fail('metadata_dependency_error', 'candidate_bundle_validation', 'intent semantics가 미등록 metadata를 참조합니다.', {'target_type': target_type, 'identity': identity})
    for item in semantics.get('filter_refs') or []:
        if not isinstance(item, dict) or not _v2c_registered(catalog, 'field', str(item.get('field') or '')):
            _v2c_fail('metadata_dependency_error', 'candidate_bundle_validation', 'filter literal이 미등록 field를 참조합니다.')

def _v2c_operation_cues(question: str, request: dict[str, Any]) -> set[str]:
    result = {operation for operation, lexemes in _v2cOPERATION_LEXEMES.items() if any((_v2c_contains(question, lexeme) for lexeme in lexemes))}
    if _v2c_rank_semantics(request):
        result.add('rank')
    return result

def _v2c_comparison_operator(question: str) -> str:
    """Return a typed predicate only for explicit directional wording."""
    normalized = normalize_text(question)
    for operator, lexemes in (('gte', ('보다 크거나 같은', '이상', 'at least', 'greater than or equal')), ('lte', ('보다 작거나 같은', '이하', 'at most', 'less than or equal')), ('gt', ('보다 큰', '초과', 'greater than', 'above')), ('lt', ('보다 작은', '미만', 'less than', 'below'))):
        if any((_v2c_contains(normalized, lexeme) for lexeme in lexemes)):
            return operator
    return ''

def _v2c_operation_alignment_score(cues: set[str], template_ops: set[str], root_op: str) -> int:
    score = 0
    structural_cues = cues - {'detail'}
    for cue in cues:
        if cue in template_ops:
            score += 30 if cue == root_op else 20
        elif cue == 'detail' and root_op == 'project' and (not structural_cues):
            score += 5
    if 'rank' in cues and 'rank' not in template_ops:
        score -= 50
    if 'project' in cues and root_op == 'project':
        score += 20
    if 'join' in cues and 'join' in template_ops:
        score += 20
    return score

def _v2c_dominant_operation(ops: set[str], cues: set[str]) -> str:
    for operation, analysis_kind in (('rank', 'rank'), ('compare_fields', 'compare_fields'), ('project', 'projection'), ('join', 'join'), ('aggregate', 'aggregate'), ('sort', 'sort'), ('filter', 'detail')):
        if operation in cues and operation in ops:
            return analysis_kind
    for operation, analysis_kind in (('rank', 'rank'), ('join', 'join'), ('aggregate', 'aggregate'), ('project', 'projection'), ('sort', 'sort'), ('filter', 'detail')):
        if operation in ops:
            return analysis_kind
    return 'detail'

def _v2c_template_ops(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        if isinstance(value.get('op'), str):
            result.add(str(value['op']))
        for item in value.values():
            result.update(_v2c_template_ops(item))
    elif isinstance(value, list):
        for item in value:
            result.update(_v2c_template_ops(item))
    return result

def _v2c_template_values(value: Any, keys: set[str]) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys:
                if isinstance(item, list):
                    result.extend(_v2c_strings(item))
                elif isinstance(item, str):
                    result.append(item)
            result.extend(_v2c_template_values(item, keys))
    elif isinstance(value, list):
        for item in value:
            result.extend(_v2c_template_values(item, keys))
    return _v2c_stable(result)

def _v2c_metric_source_datasets(catalog: dict[str, Any], metric_refs: Iterable[str], *, request: dict[str, Any] | None=None, explicit_datasets: Iterable[str]=()) -> tuple[list[str], list[str]]:
    datasets: list[str] = []
    gaps: list[str] = []
    seen: set[str] = set()

    def visit(metric_id: str) -> None:
        if metric_id in seen:
            return
        seen.add(metric_id)
        metric = (catalog.get('metrics') or {}).get(metric_id)
        if not isinstance(metric, dict):
            gaps.append(f'metric:{metric_id}')
            return
        formula = metric.get('formula') if isinstance(metric.get('formula'), dict) else {}
        dependencies = _v2c_formula_metric_refs(formula)
        if dependencies:
            for dependency in dependencies:
                visit(dependency)
            return
        binding = metric.get('source_binding') if isinstance(metric.get('source_binding'), dict) else {}
        family = str(binding.get('dataset_family') or '')
        matches = [str(key) for key, dataset in (catalog.get('datasets') or {}).items() if isinstance(dataset, dict) and str(dataset.get('family') or '') == family]
        selected = _v2c_select_time_scoped_dataset(catalog, matches, request or {}, explicit_datasets=explicit_datasets)
        if selected:
            datasets.append(selected)
        else:
            gaps.append(f'metric_source:{metric_id}')
    for metric_ref in metric_refs:
        visit(str(metric_ref))
    return (_v2c_stable(datasets), _v2c_stable(gaps))

def _v2c_formula_metric_refs(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key.endswith('_metric') and isinstance(item, str):
                result.append(item)
            else:
                result.extend(_v2c_formula_metric_refs(item))
    elif isinstance(value, list):
        for item in value:
            result.extend(_v2c_formula_metric_refs(item))
    return _v2c_stable(result)

def _v2c_select_time_scoped_dataset(catalog: dict[str, Any], matches: list[str], request: dict[str, Any], *, explicit_datasets: Iterable[str]=()) -> str:
    if len(matches) == 1:
        return matches[0]
    if not matches or not request:
        return ''
    explicit = [dataset for dataset in _v2c_stable(explicit_datasets) if dataset in matches]
    if len(explicit) == 1:
        return explicit[0]
    if len(explicit) > 1:
        return ''
    question = str(request.get('question') or '')
    current_cues = ('현재', '실시간', '현황', 'current', 'real-time', 'realtime')
    if any((_v2c_contains(question, cue) for cue in current_cues)):
        preferred = [dataset_key for dataset_key in matches if str(((catalog.get('datasets') or {}).get(dataset_key) or {}).get('time_scope') or '') == 'current']
        return preferred[0] if len(preferred) == 1 else ''
    requested_date, _explicit = _v2c_date_semantics(request)
    reference_date = str(request.get('reference_instant') or '')[:10]
    date_values = _v2c_typed_values(request, 'date')
    absolute_past = any((str(item.get('resolution') or '') == 'explicit' for item in date_values)) and bool(requested_date and reference_date and (requested_date < reference_date))
    if not absolute_past:
        return ''
    preferred = [dataset_key for dataset_key in matches if str(((catalog.get('datasets') or {}).get(dataset_key) or {}).get('time_scope') or '') == 'history']
    return preferred[0] if len(preferred) == 1 else ''

def _v2c_field_source_datasets(catalog: dict[str, Any], fields: Iterable[str], preferred: Iterable[str]) -> tuple[list[str], list[str]]:
    preferred_list = _v2c_stable(preferred)
    selected: list[str] = []
    gaps: list[str] = []
    for field in fields:
        owners = _v2c_strings(((catalog.get('fields') or {}).get(field) or {}).get('dataset_keys') or [])
        preferred_owners = [owner for owner in owners if owner in preferred_list]
        if len(preferred_owners) == 1:
            selected.append(preferred_owners[0])
        elif len(owners) == 1:
            selected.append(owners[0])
        elif len(preferred_owners) > 1:
            continue
        elif owners:
            gaps.append(f'field_owner:{field}')
        else:
            gaps.append(f'field_owner:{field}')
    return (_v2c_stable(selected), _v2c_stable(gaps))

def _v2c_relation_path_refs(catalog: dict[str, Any], datasets: Iterable[str], explicit_relations: Iterable[str]) -> tuple[list[str], list[str]]:
    selected = _v2c_stable(explicit_relations)
    covered: set[str] = set()
    for relation_id in selected:
        relation = (catalog.get('relations') or {}).get(relation_id) or {}
        covered.update(_v2c_strings([relation.get('left_dataset'), relation.get('right_dataset')]))
    targets = _v2c_stable(datasets)
    if len(targets) <= 1:
        return (selected, [])
    connected = set(covered or targets[:1])
    remaining = [item for item in targets if item not in connected]
    gaps: list[str] = []
    while remaining:
        target = remaining.pop(0)
        paths = _v2c_shortest_relation_paths(catalog, connected, target)
        if len(paths) != 1:
            gaps.append(f'relation_path:{target}')
            continue
        for relation_id in paths[0]:
            if relation_id not in selected:
                selected.append(relation_id)
            relation = catalog['relations'][relation_id]
            connected.update(_v2c_strings([relation.get('left_dataset'), relation.get('right_dataset')]))
        remaining = [item for item in remaining if item not in connected]
    return (selected, gaps)

def _v2c_shortest_relation_paths(catalog: dict[str, Any], starts: set[str], target: str) -> list[list[str]]:
    if target in starts:
        return [[]]
    adjacency: dict[str, list[tuple[str, str]]] = {}
    for relation_id, relation in (catalog.get('relations') or {}).items():
        if not isinstance(relation, dict):
            continue
        left = str(relation.get('left_dataset') or '')
        right = str(relation.get('right_dataset') or '')
        if left and right:
            adjacency.setdefault(left, []).append((right, str(relation_id)))
            adjacency.setdefault(right, []).append((left, str(relation_id)))
    queue: list[tuple[str, list[str], set[str]]] = [(start, [], {start}) for start in sorted(starts)]
    solutions: list[list[str]] = []
    best_length: int | None = None
    while queue:
        node, path, visited = queue.pop(0)
        if best_length is not None and len(path) >= best_length:
            continue
        for neighbor, relation_id in sorted(adjacency.get(node, [])):
            if neighbor in visited:
                continue
            next_path = [*path, relation_id]
            if neighbor == target:
                best_length = len(next_path) if best_length is None else best_length
                if len(next_path) == best_length and next_path not in solutions:
                    solutions.append(next_path)
            else:
                queue.append((neighbor, next_path, {*visited, neighbor}))
    return solutions[:2]

def _v2c_dimension_refs(catalog: dict[str, Any], fields: list[str], grain_ids: list[str], analysis_kind: str) -> list[str]:
    result: list[str] = []
    for grain_id in grain_ids:
        grain = (catalog.get('grains') or {}).get(grain_id) or {}
        result.extend((field for field in _v2c_strings(grain.get('keys') or []) if field in (catalog.get('fields') or {})))
    group_fields = [field for field in fields if 'group' in _v2c_strings(((catalog.get('fields') or {}).get(field) or {}).get('roles') or [])]
    if analysis_kind in {'rank', 'aggregate', 'join', 'compare_fields'}:
        result.extend(group_fields)
    if analysis_kind == 'rank' and (not result):
        matching_grains = [grain for grain in (catalog.get('grains') or {}).values() if isinstance(grain, dict) and set(_v2c_strings(grain.get('keys') or [])) & set(fields)]
        if len(matching_grains) == 1:
            result.extend(_v2c_strings(matching_grains[0].get('keys') or []))
    return _v2c_stable(result)

def _v2c_date_semantics(request: dict[str, Any]) -> tuple[str, bool]:
    question = normalize_text(str(request.get('question') or ''))
    if any((_v2c_contains(question, cue) for cue in ('전체 기간', '모든 기간', '전 기간', 'all time', 'entire period'))):
        return ('__all_time__', False)
    values = _v2c_typed_values(request, 'date')
    if not values:
        values = extract_date_candidates(str(request.get('question') or ''), request.get('reference_instant'), str(request.get('timezone') or 'Asia/Seoul'))
    selected = values[-1] if values else {}
    date_value = str(selected.get('value') or str(request.get('reference_instant') or '')[:10])
    return (date_value, bool(values))

def _v2c_rank_semantics(request: dict[str, Any]) -> dict[str, Any] | None:
    values = _v2c_typed_values(request, 'rank')
    if values:
        selected = values[0]
        mode = str(selected.get('mode') or '')
        limit = int(selected.get('limit') or 0)
        if mode in {'top', 'bottom'} and limit > 0:
            return {'mode': mode, 'limit': limit}
    question = normalize_text(str(request.get('question') or ''))
    match = _v2cTOP_N_PATTERN.search(question)
    if match:
        mode = 'top' if match.group('mode').casefold() in {'상위', 'top'} else 'bottom'
        return {'mode': mode, 'limit': max(1, int(match.group('limit')))}
    if any((_v2c_contains(question, term) for term in ('가장 큰', '최대', 'highest', 'largest'))):
        return {'mode': 'top', 'limit': 1}
    if any((_v2c_contains(question, term) for term in ('가장 작은', '최소', 'lowest', 'smallest'))):
        return {'mode': 'bottom', 'limit': 1}
    return None

def _v2c_sort_semantics(question: str, metric_refs: list[str]) -> dict[str, Any] | None:
    if not metric_refs:
        return None
    if any((_v2c_contains(question, term) for term in ('큰 순', '내림차순', 'descending'))):
        return {'field': metric_refs[-1], 'direction': 'desc'}
    if any((_v2c_contains(question, term) for term in ('작은 순', '오름차순', 'ascending'))):
        return {'field': metric_refs[-1], 'direction': 'asc'}
    return None

def _v2c_tie_policy(question: str, rank: dict[str, Any] | None) -> str:
    if rank and int(rank.get('limit') or 0) == 1:
        return 'include_all'
    if any((_v2c_contains(question, term) for term in ('동률', '동점', '모두', 'ties'))):
        return 'include_all'
    return 'exact_n'

def _v2c_request_scope(request: dict[str, Any], cues: set[str]) -> str:
    if not request.get('state_ref'):
        return 'new_analysis'
    question = normalize_text(str(request.get('question') or ''))
    if not any((_v2c_contains(question, term) for term in ('그중', '그 결과', '위 결과', '이전 결과', 'those', 'previous'))):
        return 'new_analysis'
    if 'join' in cues:
        return 'previous_result_enrich'
    return 'previous_result_transform'

def _v2c_inherit_prior(semantics: dict[str, Any], prior_semantics: dict[str, Any] | None, prior_result: dict[str, Any] | None) -> dict[str, Any]:
    if semantics.get('request_scope') == 'new_analysis' or not isinstance(prior_semantics, dict):
        return semantics
    result = deepcopy(semantics)
    for key in ('metric_refs', 'dimension_refs', 'field_refs', 'dataset_refs', 'relation_refs', 'grain_refs', 'function_refs'):
        if not result.get(key):
            result[key] = deepcopy(prior_semantics.get(key) or [])
    if not result.get('date_explicit'):
        result['date'] = prior_semantics.get('date') or result.get('date')
    if isinstance(prior_result, dict):
        columns = _v2c_strings(prior_result.get('columns') or [])
        if columns:
            result['previous_result_columns'] = columns
    return result

def _v2c_alias_ambiguity(matches: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for target_type, candidates in matches.items():
        by_span: dict[tuple[int, int], set[str]] = {}
        for candidate in candidates:
            evidence = candidate['evidence']
            by_span.setdefault((int(evidence['start']), int(evidence['end'])), set()).add(str(candidate['identity']))
        for (start, end), identities in sorted(by_span.items()):
            if len(identities) > 1:
                result.append({'target_type': target_type, 'matched_span': f'{start}:{end}', 'identities': sorted(identities)})
    return result

def _v2c_dedupe_evaluations(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for value in values:
        marker = sha256_json(value.get('semantics') or {})
        previous = selected.get(marker)
        if previous is None or int(value.get('score') or 0) > int(previous.get('score') or 0):
            selected[marker] = value
    return sorted(selected.values(), key=lambda item: (-int(item.get('score') or 0), sha256_json(item.get('semantics') or {})))

def _v2c_matched_ids(matches: dict[str, list[dict[str, Any]]], target_type: str) -> list[str]:
    return _v2c_stable((item.get('identity') for item in matches.get(target_type, [])))

def _v2c_root_metric_refs(catalog: dict[str, Any], metric_ids: Iterable[str], *, request: dict[str, Any] | None=None, matches: dict[str, list[dict[str, Any]]] | None=None) -> list[str]:
    """Return requested formula roots while keeping dependencies implicit.

    If a question matches a derived metric and also words naming its source
    metrics, the derived metric is the visible result.  Its dependencies remain
    available through the compiler's formula closure, not as extra columns.
    """
    selected = _v2c_stable(metric_ids)
    question = normalize_text(str((request or {}).get('question') or ''))
    metric_matches = [item for item in (matches or {}).get('metric', []) if isinstance(item, dict) and str(item.get('identity') or '') in set(selected)]
    metric_matches.sort(key=lambda item: int((item.get('evidence') or {}).get('start') or 0))
    for left, right in zip(metric_matches, metric_matches[1:]):
        left_end = int((left.get('evidence') or {}).get('end') or 0)
        right_start = int((right.get('evidence') or {}).get('start') or 0)
        separator = question[left_end:right_start]
        if re.search('(?:,|/|\\band\\b|\\bor\\b|및|그리고|와|과)', separator, flags=re.IGNORECASE):
            return selected
    selected_set = set(selected)
    dependencies: set[str] = set()
    for metric_id in selected:
        metric = (catalog.get('metrics') or {}).get(metric_id) or {}
        formula = metric.get('formula') if isinstance(metric.get('formula'), dict) else {}
        dependencies.update((ref for ref in _v2c_formula_metric_refs(formula) if ref in selected_set))
    roots = [metric_id for metric_id in selected if metric_id not in dependencies]
    return roots or selected

def _v2c_visible_field_refs(request: dict[str, Any], catalog: dict[str, Any], matches: dict[str, list[dict[str, Any]]]) -> list[str]:
    """Separate visible result fields from fields used only as qualifiers.

    The original match pool is retained for source/filter closure.  This view
    removes a field mention swallowed by a longer registered entity-group label
    (for example ``electronics category``) and Korean possessive entity nouns
    such as ``product's`` when a later concrete field is requested.
    """
    question = normalize_text(str(request.get('question') or ''))
    field_matches = [item for item in matches.get('field', []) if isinstance(item, dict)]
    group_matches = [item for item in matches.get('entity_group', []) if isinstance(item, dict)]
    result: list[str] = []
    for match in field_matches:
        field = str(match.get('identity') or '')
        evidence = match.get('evidence') if isinstance(match.get('evidence'), dict) else {}
        start = int(evidence.get('start') or 0)
        end = int(evidence.get('end') or 0)
        qualifier_only = False
        same_field_later = any((str(item.get('identity') or '') == field and int((item.get('evidence') or {}).get('start') or 0) > end for item in field_matches if isinstance(item.get('evidence'), dict)))
        if same_field_later and re.match('\\s*(?:이|가|은|는)?\\s*[-+]?(?:\\d+(?:\\.\\d+)?|\\.\\d+)\\s*보다\\s*(?:큰|작은|크|작)', question[end:]):
            qualifier_only = True
        for group_match in group_matches:
            group_id = str(group_match.get('identity') or '')
            group = (catalog.get('entity_groups') or {}).get(group_id) or {}
            target_field = str(group.get('target_field') or group.get('entity') or '')
            group_evidence = group_match.get('evidence') if isinstance(group_match.get('evidence'), dict) else {}
            if target_field == field and int(group_evidence.get('start') or 0) <= start and (int(group_evidence.get('end') or 0) >= end):
                qualifier_only = True
                break
        later_field = any((int((item.get('evidence') or {}).get('start') or 0) > end for item in field_matches if isinstance(item.get('evidence'), dict)))
        if not qualifier_only and later_field and question[end:].lstrip().startswith('의'):
            qualifier_only = True
        if not qualifier_only and field:
            result.append(field)
    return _v2c_stable(result)

def _v2c_semantic_refs(semantics: dict[str, Any], target_type: str) -> list[str]:
    key = {'metric': 'metric_refs', 'field': 'field_refs', 'dataset': 'dataset_refs', 'recipe': 'recipe_refs', 'grain': 'grain_refs', 'relation': 'relation_refs', 'entity_group': 'entity_group_refs', 'function': 'function_refs'}.get(target_type, '')
    return _v2c_strings(semantics.get(key) or []) if key else []

def _v2c_typed_values(request: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    raw = request.get('literal_candidates')
    if isinstance(raw, dict):
        return [deepcopy(item) for item in raw.get(kind) or [] if isinstance(item, dict)]
    result: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict) or item.get('kind') != kind:
            continue
        value = deepcopy(item.get('value'))
        if isinstance(value, dict):
            value.setdefault('candidate_id', item.get('id'))
            value.setdefault('source_span', item.get('source_span'))
            result.append(value)
    return result

def _v2c_registered_filter_literals(request: dict[str, Any], catalog: dict[str, Any], matches: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    filters: list[dict[str, Any]] = []
    gaps: list[str] = []
    question = normalize_text(str(request.get('question') or ''))
    for match in matches.get('field', []):
        field = str(match.get('identity') or '')
        field_spec = (catalog.get('fields') or {}).get(field) or {}
        if 'filter' not in set(_v2c_strings(field_spec.get('roles') or [])):
            continue
        evidence = match.get('evidence') if isinstance(match.get('evidence'), dict) else {}
        start = int(evidence.get('start') or 0)
        end = int(evidence.get('end') or 0)
        suffix = question[end:end + 180]
        value_type = 'number' if str(field_spec.get('coercion') or '').casefold() in {'strict_number', 'number', 'float', 'decimal'} else str(field_spec.get('semantic_type') or 'string')
        directional_match = re.match('\\s*(?:은|는|이|가)?\\s*(?P<value>[-+]?(?:\\d+(?:\\.\\d+)?|\\.\\d+))\\s*보다\\s*(?P<direction>크거나\\s*같은|작거나\\s*같은|큰|작은)', suffix)
        if directional_match:
            operator = {'크거나같은': 'gte', '작거나같은': 'lte', '큰': 'gt', '작은': 'lt'}[re.sub('\\s+', '', str(directional_match.group('direction')))]
            try:
                value = _v2c_coerce_filter_value(str(directional_match.group('value')), value_type)
            except ValueError:
                gaps.append(f'filter_value:{field}')
            else:
                literal_end = end + directional_match.end()
                filters.append({'candidate_id': f'literal:{field}:{operator}:{sha256_json([field, value, start, literal_end])[:16]}', 'field': field, 'operator': operator, 'value': value})
        literal_match = re.match('\\s*(?:=|은|는|이|가)\\s*(?:[\\"“](?P<quoted>[^\\"”]{1,128})[\\"”]|(?P<bare>[^\\s,]{1,128}?))(?=(?:인(?:\\s|$)|이며(?:\\s|$)|이고(?:\\s|$)|,|\\s|$))', suffix)
        if not literal_match:
            continue
        raw_value = str(literal_match.group('quoted') or literal_match.group('bare') or '').strip()
        if not raw_value:
            continue
        trailing = suffix[literal_match.end():].lstrip()
        if raw_value.endswith('로') and trailing.startswith('시작'):
            continue
        if raw_value.endswith('보다') or raw_value.casefold() in {'가장', '상위', '하위', '최대', '최소', '합계', '평균', '전체', 'highest', 'lowest', 'largest', 'smallest'}:
            continue
        try:
            value = _v2c_coerce_filter_value(raw_value, value_type)
        except ValueError:
            gaps.append(f'filter_value:{field}')
            continue
        literal_end = end + literal_match.end()
        filters.append({'candidate_id': f'literal:{field}:eq:{sha256_json([field, value, start, literal_end])[:16]}', 'field': field, 'operator': 'eq', 'value': value})
    for match in matches.get('entity_group', []):
        group_id = str(match.get('identity') or '')
        group = (catalog.get('entity_groups') or {}).get(group_id) or {}
        field = str(group.get('target_field') or group.get('entity') or '')
        selection = group.get('selection') if isinstance(group.get('selection'), dict) else {}
        operator = str(selection.get('operator') or '')
        if not field or not _v2c_registered(catalog, 'field', field) or operator == 'all_registered':
            continue
        if operator not in {'eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'in', 'not_in', 'starts_with', 'contains'}:
            gaps.append(f'entity_group_operator:{group_id}')
            continue
        if 'value' not in selection:
            gaps.append(f'entity_group_value:{group_id}')
            continue
        filters.append({'candidate_id': str(match.get('candidate_id') or f'entity_group:{group_id}'), 'field': field, 'operator': operator, 'value': deepcopy(selection.get('value'))})
    for item in _v2c_typed_values(request, 'product_token'):
        field = str(item.get('field') or '')
        operator = str(item.get('operator') or '')
        if not _v2c_registered(catalog, 'field', field):
            gaps.append(f"filter_field:{field or 'missing'}")
            continue
        filters.append({'candidate_id': str(item.get('candidate_id') or ''), 'field': field, 'operator': operator, 'value': deepcopy(item.get('value'))})
    unique_filters: list[dict[str, Any]] = []
    seen_filters: set[str] = set()
    for item in filters:
        marker = sha256_json({key: item.get(key) for key in ('field', 'operator', 'value')})
        if marker not in seen_filters:
            seen_filters.add(marker)
            unique_filters.append(item)
    thresholds = [{'candidate_id': str(item.get('candidate_id') or ''), 'operator': str(item.get('operator') or ''), 'value': deepcopy(item.get('value')), 'unit': str(item.get('unit') or '')} for item in _v2c_typed_values(request, 'threshold')]
    return (unique_filters, thresholds, _v2c_stable(gaps))

def _v2c_coerce_filter_value(raw: str, semantic_type: str) -> Any:
    kind = semantic_type.casefold()
    if kind in {'number', 'float', 'decimal', 'currency', 'percent', 'percentage', 'ratio', 'quantity'}:
        return float(raw.replace(',', ''))
    if kind in {'integer', 'int'}:
        return int(raw.replace(',', ''))
    if kind in {'boolean', 'bool'}:
        normalized = raw.casefold()
        if normalized in {'true', '1', 'yes', 'y', '예', '네'}:
            return True
        if normalized in {'false', '0', 'no', 'n', '아니오', '아니요'}:
            return False
        raise ValueError('invalid boolean literal')
    if kind in {'localdate', 'date'} and (not re.fullmatch('\\d{4}-\\d{2}-\\d{2}', raw)):
        raise ValueError('invalid LocalDate literal')
    return raw

def _v2c_alias_spans(question: str, alias: str) -> list[tuple[int, int]]:
    target = normalize_text(alias)
    if not target:
        return []
    flags = re.I
    if re.search('[가-힣]', target):
        pattern = re.compile(re.escape(target), flags)
    else:
        pattern = re.compile(f'(?<![0-9A-Za-z_]){re.escape(target)}(?![0-9A-Za-z_])', flags)
    return [(match.start(), match.end()) for match in pattern.finditer(question)]

def _v2c_contains(question: str, lexeme: str) -> bool:
    return bool(_v2c_alias_spans(normalize_text(question), lexeme))

def _v2c_registered(catalog: dict[str, Any], target_type: str, identity: str) -> bool:
    if target_type == 'function':
        return any((_v2c_function_identity(card) == identity for card in catalog.get('specialized_functions') or [] if isinstance(card, dict)))
    section = _v2cCATALOG_TARGET_SECTIONS.get(target_type)
    return bool(section and identity in (catalog.get(section) or {}))

def _v2c_function_identity(card: Mapping[str, Any]) -> str:
    function_id = str(card.get('function_id') or '')
    version = card.get('version')
    if not function_id or isinstance(version, bool) or (not isinstance(version, int)) or (version < 1):
        return ''
    return f'{function_id}@{version}'

def _v2c_function_card(catalog: dict[str, Any], identity: str) -> dict[str, Any]:
    matches = [deepcopy(card) for card in catalog.get('specialized_functions') or [] if isinstance(card, dict) and _v2c_function_identity(card) == identity]
    if len(matches) != 1:
        _v2c_fail('metadata_dependency_error', 'candidate_routing', 'registered function reference does not resolve uniquely.', {'function_ref': identity})
    return matches[0]

def _v2c_strings(values: Iterable[Any] | Any) -> list[str]:
    """Return registered textual values, including compiled alias objects."""
    if values in (None, ''):
        return []
    if isinstance(values, str):
        return [values]
    if isinstance(values, Mapping):
        for key in ('text', 'value', 'alias', 'name'):
            candidate = values.get(key)
            if candidate not in (None, ''):
                return [str(candidate)]
        return []
    result: list[str] = []
    for value in values:
        if value in (None, ''):
            continue
        if isinstance(value, Mapping):
            result.extend(_v2c_strings(value))
        else:
            result.append(str(value))
    return result

def _v2c_stable(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value or '')
        if text and text not in result:
            result.append(text)
    return result

def _v2c_fail(code: str, stage: str, message: str, details: dict[str, Any] | None=None) -> None:
    raise ContractError(code, stage, message, details)
__all__ = ['build_generic_v2_candidate_bundle', 'validate_generic_v2_candidate_bundle', 'normalize_generic_v2_intent', 'build_generic_v2_intent_prompt', 'resolve_generic_v2_intent']


EMBEDDED_RUNTIME_CATALOG = json.loads('{"aliases":{"dataset:eqp_uph":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"eqp_uph","target_type":"dataset","values":[{"priority":100,"text":"UPH"},{"priority":100,"text":"시간당 생산량"}]},"dataset:equipment_assign":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"equipment_assign","target_type":"dataset","values":[{"priority":100,"text":"장비 배정"},{"priority":100,"text":"장비 현황"},{"priority":100,"text":"설비 대수"}]},"dataset:hold_history":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"hold_history","target_type":"dataset","values":[{"priority":100,"text":"HOLD 이력"},{"priority":100,"text":"HOLD 발생 시각"}]},"dataset:lot_status":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"lot_status","target_type":"dataset","values":[{"priority":100,"text":"현재 LOT"},{"priority":100,"text":"LOT 현황"},{"priority":100,"text":"HOLD LOT"}]},"dataset:product_master":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"product_master","target_type":"dataset","values":[{"priority":100,"text":"product master"},{"priority":100,"text":"제품 master"},{"priority":100,"text":"제품 기준정보"},{"priority":100,"text":"제품 마스터"}]},"dataset:production":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"production","target_type":"dataset","values":[{"priority":100,"text":"production"},{"priority":100,"text":"production 데이터"},{"priority":100,"text":"이력 생산"},{"priority":100,"text":"생산 실적"},{"priority":100,"text":"OUTPUT"},{"priority":100,"text":"OUT"}]},"dataset:production_today":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"production_today","target_type":"dataset","values":[{"priority":100,"text":"당일 생산"},{"priority":100,"text":"오늘 생산"},{"priority":100,"text":"현재 생산"}]},"dataset:target":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"target","target_type":"dataset","values":[{"priority":100,"text":"계획"},{"priority":100,"text":"스케줄"},{"priority":100,"text":"스케쥴"},{"priority":100,"text":"SCHD"},{"priority":100,"text":"생산목표"}]},"dataset:wip":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"wip","target_type":"dataset","values":[{"priority":100,"text":"이력 재공"},{"priority":100,"text":"아침 재공"},{"priority":100,"text":"BOH 재공"},{"priority":100,"text":"BOH"}]},"dataset:wip_today":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"wip_today","target_type":"dataset","values":[{"priority":100,"text":"현재 재공"},{"priority":100,"text":"지금 재공"},{"priority":100,"text":"금일 현재 재공"}]},"field:BASE_DATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"BASE_DATE","target_type":"field","values":[{"priority":100,"text":"BASE_DATE"}]},"field:BAY_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"BAY_ID","target_type":"field","values":[{"priority":100,"text":"BAY_ID"}]},"field:CUM_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"CUM_TAT","target_type":"field","values":[{"priority":100,"text":"CUM_TAT"}]},"field:DATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DATE","target_type":"field","values":[{"priority":100,"text":"날짜"},{"priority":100,"text":"일자"},{"priority":100,"text":"기준일"},{"priority":100,"text":"작업일"},{"priority":100,"text":"date"},{"priority":100,"text":"work date"}]},"field:DEN":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DEN","target_type":"field","values":[{"priority":100,"text":"DEN"},{"priority":100,"text":"DENSITY"},{"priority":100,"text":"제품 용량"}]},"field:DEVICE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DEVICE","target_type":"field","values":[{"priority":100,"text":"DEVICE"},{"priority":100,"text":"DEVICE CODE"},{"priority":100,"text":"첨자"}]},"field:DEVICE_DESC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DEVICE_DESC","target_type":"field","values":[{"priority":100,"text":"DEVICE_DESC"},{"priority":100,"text":"제품 설명"}]},"field:DIE_ATTACH_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DIE_ATTACH_QTY","target_type":"field","values":[{"priority":100,"text":"DIE_ATTACH_QTY"}]},"field:EQP_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"EQP_ID","target_type":"field","values":[{"priority":100,"text":"EQP_ID"},{"priority":100,"text":"EQPID"},{"priority":100,"text":"장비 ID"}]},"field:EQP_MODEL":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"EQP_MODEL","target_type":"field","values":[{"priority":100,"text":"EQP_MODEL"},{"priority":100,"text":"equipment model"},{"priority":100,"text":"장비 모델"},{"priority":100,"text":"장비 기종"},{"priority":100,"text":"설비 모델"},{"priority":100,"text":"설비 기종"}]},"field:FAB":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FAB","target_type":"field","values":[{"priority":100,"text":"FAB"}]},"field:FACTORY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FACTORY","target_type":"field","values":[{"priority":100,"text":"FACTORY"}]},"field:FAC_IN_AT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FAC_IN_AT","target_type":"field","values":[{"priority":100,"text":"FAC_IN_AT"}]},"field:FAMILY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FAMILY","target_type":"field","values":[{"priority":100,"text":"FAMILY"}]},"field:HOLD_CD":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_CD","target_type":"field","values":[{"priority":100,"text":"HOLD_CD"}]},"field:HOLD_DESC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_DESC","target_type":"field","values":[{"priority":100,"text":"HOLD_DESC"}]},"field:HOLD_EVENT_AT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_EVENT_AT","target_type":"field","values":[{"priority":100,"text":"HOLD_EVENT_AT"}]},"field:HOLD_REASON":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_REASON","target_type":"field","values":[{"priority":100,"text":"HOLD_REASON"}]},"field:HOLD_STAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_STAT","target_type":"field","values":[{"priority":100,"text":"HOLD_STAT"}]},"field:INPUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"INPUT_PLAN_QTY","target_type":"field","values":[{"priority":100,"text":"INPUT_PLAN_QTY"}]},"field:IN_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"IN_TAT","target_type":"field","values":[{"priority":100,"text":"IN_TAT"}]},"field:LEAD":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LEAD","target_type":"field","values":[{"priority":100,"text":"LEAD"},{"priority":100,"text":"lead count"}]},"field:LOAD_DATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LOAD_DATE","target_type":"field","values":[{"priority":100,"text":"LOAD_DATE"}]},"field:LOT_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LOT_ID","target_type":"field","values":[{"priority":100,"text":"LOT_ID"},{"priority":100,"text":"Lot ID"}]},"field:LOT_STAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LOT_STAT","target_type":"field","values":[{"priority":100,"text":"LOT_STAT"}]},"field:MCP_NO":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"MCP_NO","target_type":"field","values":[{"priority":100,"text":"MCP_NO"},{"priority":100,"text":"MCP NO"},{"priority":100,"text":"MCP_SALES_NO"},{"priority":100,"text":"MCP_SALE_CD"},{"priority":100,"text":"MCPSALENO"}]},"field:MODE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"MODE","target_type":"field","values":[{"priority":100,"text":"MODE"},{"priority":100,"text":"Mode"},{"priority":100,"text":"mode"},{"priority":100,"text":"제품 모드"}]},"field:NETDIE_300_CNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"NETDIE_300_CNT","target_type":"field","values":[{"priority":100,"text":"NETDIE_300_CNT"}]},"field:OPER_IN_AT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OPER_IN_AT","target_type":"field","values":[{"priority":100,"text":"OPER_IN_AT"}]},"field:OPER_NAME":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"OPER_NAME","target_type":"field","values":[{"priority":100,"text":"OPER_NAME"},{"priority":100,"text":"공정"},{"priority":100,"text":"작업공정"},{"priority":100,"text":"operation"},{"priority":100,"text":"process"},{"priority":100,"text":"oper name"},{"priority":100,"text":"세부 공정별"},{"priority":100,"text":"공정별"}]},"field:OPER_NUM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OPER_NUM","target_type":"field","values":[{"priority":100,"text":"공정번호"},{"priority":100,"text":"공정 차수"},{"priority":100,"text":"차수별"},{"priority":100,"text":"oper num"},{"priority":100,"text":"oper no"}]},"field:OPER_SEQ":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OPER_SEQ","target_type":"field","values":[{"priority":100,"text":"OPER_SEQ"}]},"field:ORG":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"ORG","target_type":"field","values":[{"priority":100,"text":"ORG"},{"priority":100,"text":"조직"},{"priority":100,"text":"organization code"}]},"field:OUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OUT_PLAN_QTY","target_type":"field","values":[{"priority":100,"text":"OUT_PLAN_QTY"}]},"field:PKG_TYPE1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PKG_TYPE1","target_type":"field","values":[{"priority":100,"text":"PKG_TYPE1"},{"priority":100,"text":"PKG1"},{"priority":100,"text":"package type 1"}]},"field:PKG_TYPE2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PKG_TYPE2","target_type":"field","values":[{"priority":100,"text":"PKG_TYPE2"},{"priority":100,"text":"PKG2"},{"priority":100,"text":"package type 2"}]},"field:PRESS_CNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PRESS_CNT","target_type":"field","values":[{"priority":100,"text":"PRESS_CNT"}]},"field:PRODUCTION_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PRODUCTION_QTY","target_type":"field","values":[{"priority":100,"text":"PRODUCTION_QTY"}]},"field:PROD_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PROD_QTY","target_type":"field","values":[{"priority":100,"text":"PROD_QTY"}]},"field:RECIPE_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"RECIPE_ID","target_type":"field","values":[{"priority":100,"text":"RECIPE_ID"},{"priority":100,"text":"Recipe ID"},{"priority":100,"text":"레시피"}]},"field:SHIFT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT","target_type":"field","values":[{"priority":100,"text":"SHIFT"}]},"field:TECH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"TECH","target_type":"field","values":[{"priority":100,"text":"TECH"},{"priority":100,"text":"제품 기술"}]},"field:TSV_DIE_TYP":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"TSV_DIE_TYP","target_type":"field","values":[{"priority":100,"text":"TSV_DIE_TYP"},{"priority":100,"text":"HBM"},{"priority":100,"text":"3DS"},{"priority":100,"text":"TSV"}]},"field:UPH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"UPH","target_type":"field","values":[{"priority":100,"text":"UPH"}]},"field:WF_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"WF_QTY","target_type":"field","values":[{"priority":100,"text":"WF_QTY"}]},"field:WIP_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"WIP_QTY","target_type":"field","values":[{"priority":100,"text":"WIP_QTY"}]},"field:YIELD_RATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"YIELD_RATE","target_type":"field","values":[{"priority":100,"text":"YIELD_RATE"},{"priority":100,"text":"YIELD RATE"},{"priority":100,"text":"수율"}]},"metric:ACHIEVEMENT_RATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"ACHIEVEMENT_RATE","target_type":"metric","values":[{"priority":100,"text":"생산달성률"},{"priority":100,"text":"생산달성율"},{"priority":100,"text":"달성률"},{"priority":100,"text":"달성율"}]},"metric:CUM_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"CUM_TAT","target_type":"metric","values":[{"priority":100,"text":"CUM TAT"},{"priority":100,"text":"누적 TAT"}]},"metric:EQP_COUNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"EQP_COUNT","target_type":"metric","values":[{"priority":100,"text":"장비 대수"},{"priority":100,"text":"설비 대수"},{"priority":100,"text":"장비 수"},{"priority":100,"text":"몇 대"}]},"metric:HOLD_DURATION_HOURS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"HOLD_DURATION_HOURS","target_type":"metric","values":[{"priority":100,"text":"HOLD_DURATION_HOURS"}]},"metric:INPUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"INPUT_PLAN_QTY","target_type":"metric","values":[{"priority":100,"text":"INPUT 계획"},{"priority":100,"text":"투입계획"}]},"metric:INPUT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"INPUT_QTY","target_type":"metric","values":[{"priority":100,"text":"투입량"},{"priority":100,"text":"INPUT"},{"priority":100,"text":"input"},{"priority":100,"text":"INPUT 수량"},{"priority":100,"text":"INPUT실적"},{"priority":100,"text":"INPUT 실적"},{"priority":100,"text":"INPUT생산량"},{"priority":100,"text":"투입 실적"},{"priority":100,"text":"INPUT_QTY"}]},"metric:IN_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"IN_TAT","target_type":"metric","values":[{"priority":100,"text":"IN TAT"},{"priority":100,"text":"현재 공정 TAT"},{"priority":100,"text":"현재 TAT"}]},"metric:LOT_COUNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"LOT_COUNT","target_type":"metric","values":[{"priority":100,"text":"LOT 건수"},{"priority":100,"text":"LOT 수"}]},"metric:OUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"OUT_PLAN_QTY","target_type":"metric","values":[{"priority":100,"text":"OUT 계획"},{"priority":100,"text":"TARGET"},{"priority":100,"text":"생산목표"}]},"metric:OUT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"OUT_QTY","target_type":"metric","values":[{"priority":100,"text":"OUT_QTY"}]},"metric:PKG_OUT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PKG_OUT_QTY","target_type":"metric","values":[{"priority":100,"text":"OUTPUT"},{"priority":100,"text":"OUT"},{"priority":100,"text":"Out Put"},{"priority":100,"text":"output 실적"},{"priority":100,"text":"out 실적"},{"priority":100,"text":"PKG OUT실적"},{"priority":100,"text":"PKG OUT 실적"}]},"metric:PRODUCTION_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PRODUCTION_QTY","target_type":"metric","values":[{"priority":100,"text":"생산량"},{"priority":100,"text":"생산실적"},{"priority":100,"text":"실적"},{"priority":100,"text":"PRODUCTION_QTY"}]},"metric:UNIT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"UNIT_QTY","target_type":"metric","values":[{"priority":100,"text":"UNIT 수량"},{"priority":100,"text":"DIE 수량"}]},"metric:UPH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"UPH","target_type":"metric","values":[{"priority":100,"text":"UPH"},{"priority":100,"text":"시간당 생산량"}]},"metric:WAFER_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WAFER_QTY","target_type":"metric","values":[{"priority":100,"text":"Wafer 수량"},{"priority":100,"text":"웨이퍼 수량"}]},"metric:WIP_BOH_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WIP_BOH_QTY","target_type":"metric","values":[{"priority":100,"text":"아침 재공"},{"priority":100,"text":"BOH 재공"},{"priority":100,"text":"BOH"},{"priority":100,"text":"07시 기준 재공"}]},"metric:WIP_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WIP_QTY","target_type":"metric","values":[{"priority":100,"text":"재공"},{"priority":100,"text":"재공수량"},{"priority":100,"text":"WIP"},{"priority":100,"text":"공정 물량"}]},"process:B/G1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"B/G1","target_type":"process","values":[{"priority":140,"text":"B/G1"},{"priority":140,"text":"BG1"},{"priority":140,"text":"B/G1공정"},{"priority":140,"text":"B/G1 공정"},{"priority":140,"text":"B/G 1차"},{"priority":140,"text":"B/G1차"},{"priority":140,"text":"BG 1차"},{"priority":140,"text":"BG1차"}]},"process:B/G2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"B/G2","target_type":"process","values":[{"priority":140,"text":"B/G2"},{"priority":140,"text":"BG2"},{"priority":140,"text":"B/G2공정"},{"priority":140,"text":"B/G2 공정"},{"priority":140,"text":"B/G 2차"},{"priority":140,"text":"B/G2차"},{"priority":140,"text":"BG 2차"},{"priority":140,"text":"BG2차"}]},"process:D/A1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A1","target_type":"process","values":[{"priority":140,"text":"D/A1"},{"priority":140,"text":"DA1"},{"priority":140,"text":"D/A1공정"},{"priority":140,"text":"D/A1 공정"},{"priority":140,"text":"D/A 1차"},{"priority":140,"text":"D/A1차"},{"priority":140,"text":"DA 1차"},{"priority":140,"text":"DA1차"}]},"process:D/A2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A2","target_type":"process","values":[{"priority":140,"text":"D/A2"},{"priority":140,"text":"DA2"},{"priority":140,"text":"D/A2공정"},{"priority":140,"text":"D/A2 공정"},{"priority":140,"text":"D/A 2차"},{"priority":140,"text":"D/A2차"},{"priority":140,"text":"DA 2차"},{"priority":140,"text":"DA2차"}]},"process:D/A3":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A3","target_type":"process","values":[{"priority":140,"text":"D/A3"},{"priority":140,"text":"DA3"},{"priority":140,"text":"D/A3공정"},{"priority":140,"text":"D/A3 공정"},{"priority":140,"text":"D/A 3차"},{"priority":140,"text":"D/A3차"},{"priority":140,"text":"DA 3차"},{"priority":140,"text":"DA3차"}]},"process:D/A4":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A4","target_type":"process","values":[{"priority":140,"text":"D/A4"},{"priority":140,"text":"DA4"},{"priority":140,"text":"D/A4공정"},{"priority":140,"text":"D/A4 공정"},{"priority":140,"text":"D/A 4차"},{"priority":140,"text":"D/A4차"},{"priority":140,"text":"DA 4차"},{"priority":140,"text":"DA4차"}]},"process:D/A5":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A5","target_type":"process","values":[{"priority":140,"text":"D/A5"},{"priority":140,"text":"DA5"},{"priority":140,"text":"D/A5공정"},{"priority":140,"text":"D/A5 공정"},{"priority":140,"text":"D/A 5차"},{"priority":140,"text":"D/A5차"},{"priority":140,"text":"DA 5차"},{"priority":140,"text":"DA5차"}]},"process:D/A6":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A6","target_type":"process","values":[{"priority":140,"text":"D/A6"},{"priority":140,"text":"DA6"},{"priority":140,"text":"D/A6공정"},{"priority":140,"text":"D/A6 공정"},{"priority":140,"text":"D/A 6차"},{"priority":140,"text":"D/A6차"},{"priority":140,"text":"DA 6차"},{"priority":140,"text":"DA6차"}]},"process:D/S1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/S1","target_type":"process","values":[{"priority":140,"text":"D/S1"},{"priority":140,"text":"DS1"},{"priority":140,"text":"D/S1공정"},{"priority":140,"text":"D/S1 공정"},{"priority":140,"text":"D/S 1차"},{"priority":140,"text":"D/S1차"},{"priority":140,"text":"DS 1차"},{"priority":140,"text":"DS1차"}]},"process:FCB/H":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB/H","target_type":"process","values":[{"priority":140,"text":"FCB/H"},{"priority":140,"text":"FCBH"},{"priority":140,"text":"FCB/H공정"},{"priority":140,"text":"FCB/H 공정"}]},"process:FCB1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB1","target_type":"process","values":[{"priority":140,"text":"FCB1"},{"priority":140,"text":"FCB1공정"},{"priority":140,"text":"FCB1 공정"},{"priority":140,"text":"FCB 1차"},{"priority":140,"text":"FCB1차"}]},"process:FCB2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB2","target_type":"process","values":[{"priority":140,"text":"FCB2"},{"priority":140,"text":"FCB2공정"},{"priority":140,"text":"FCB2 공정"},{"priority":140,"text":"FCB 2차"},{"priority":140,"text":"FCB2차"}]},"process:INPUT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"INPUT","target_type":"process","values":[{"priority":140,"text":"INPUT"},{"priority":140,"text":"INPUT공정"},{"priority":140,"text":"INPUT 공정"}]},"process:PKG OUT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PKG OUT","target_type":"process","values":[{"priority":140,"text":"PKG OUT"},{"priority":140,"text":"PKG OUT공정"},{"priority":140,"text":"PKG OUT 공정"}]},"process:SBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SBM","target_type":"process","values":[{"priority":140,"text":"SBM"},{"priority":140,"text":"SBM공정"},{"priority":140,"text":"SBM 공정"}]},"process:W/B1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B1","target_type":"process","values":[{"priority":140,"text":"W/B1"},{"priority":140,"text":"WB1"},{"priority":140,"text":"W/B1공정"},{"priority":140,"text":"W/B1 공정"},{"priority":140,"text":"W/B 1차"},{"priority":140,"text":"W/B1차"},{"priority":140,"text":"WB 1차"},{"priority":140,"text":"WB1차"}]},"process:W/B2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B2","target_type":"process","values":[{"priority":140,"text":"W/B2"},{"priority":140,"text":"WB2"},{"priority":140,"text":"W/B2공정"},{"priority":140,"text":"W/B2 공정"},{"priority":140,"text":"W/B 2차"},{"priority":140,"text":"W/B2차"},{"priority":140,"text":"WB 2차"},{"priority":140,"text":"WB2차"}]},"process:W/B3":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B3","target_type":"process","values":[{"priority":140,"text":"W/B3"},{"priority":140,"text":"WB3"},{"priority":140,"text":"W/B3공정"},{"priority":140,"text":"W/B3 공정"},{"priority":140,"text":"W/B 3차"},{"priority":140,"text":"W/B3차"},{"priority":140,"text":"WB 3차"},{"priority":140,"text":"WB3차"}]},"process:W/B4":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B4","target_type":"process","values":[{"priority":140,"text":"W/B4"},{"priority":140,"text":"WB4"},{"priority":140,"text":"W/B4공정"},{"priority":140,"text":"W/B4 공정"},{"priority":140,"text":"W/B 4차"},{"priority":140,"text":"W/B4차"},{"priority":140,"text":"WB 4차"},{"priority":140,"text":"WB4차"}]},"process:W/B5":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B5","target_type":"process","values":[{"priority":140,"text":"W/B5"},{"priority":140,"text":"WB5"},{"priority":140,"text":"W/B5공정"},{"priority":140,"text":"W/B5 공정"},{"priority":140,"text":"W/B 5차"},{"priority":140,"text":"W/B5차"},{"priority":140,"text":"WB 5차"},{"priority":140,"text":"WB5차"}]},"process:W/B6":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B6","target_type":"process","values":[{"priority":140,"text":"W/B6"},{"priority":140,"text":"WB6"},{"priority":140,"text":"W/B6공정"},{"priority":140,"text":"W/B6 공정"},{"priority":140,"text":"W/B 6차"},{"priority":140,"text":"W/B6차"},{"priority":140,"text":"WB 6차"},{"priority":140,"text":"WB6차"}]},"process:W/BM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/BM","target_type":"process","values":[{"priority":140,"text":"W/BM"},{"priority":140,"text":"WBM"},{"priority":140,"text":"W/BM공정"},{"priority":140,"text":"W/BM 공정"}]},"process_group:BG":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"BG","target_type":"process_group","values":[{"priority":100,"text":"BG"},{"priority":100,"text":"BG공정"},{"priority":100,"text":"BG 공정"},{"priority":100,"text":"B/G"},{"priority":100,"text":"B/G공정"},{"priority":100,"text":"B/G 공정"}]},"process_group:BM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"BM","target_type":"process_group","values":[{"priority":100,"text":"BM"},{"priority":100,"text":"BM공정"},{"priority":100,"text":"BM 공정"},{"priority":100,"text":"B/M"},{"priority":100,"text":"B/M공정"},{"priority":100,"text":"B/M 공정"},{"priority":100,"text":"비엠"},{"priority":100,"text":"비엠공정"},{"priority":100,"text":"비엠 공정"}]},"process_group:DA":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DA","target_type":"process_group","values":[{"priority":100,"text":"DA"},{"priority":100,"text":"DA공정"},{"priority":100,"text":"DA 공정"},{"priority":100,"text":"D/A"},{"priority":100,"text":"D/A공정"},{"priority":100,"text":"D/A 공정"}]},"process_group:DC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DC","target_type":"process_group","values":[{"priority":100,"text":"DC"},{"priority":100,"text":"DC공정"},{"priority":100,"text":"DC 공정"},{"priority":100,"text":"D/C"},{"priority":100,"text":"D/C공정"},{"priority":100,"text":"D/C 공정"}]},"process_group:DI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DI","target_type":"process_group","values":[{"priority":100,"text":"DI"},{"priority":100,"text":"DI공정"},{"priority":100,"text":"DI 공정"},{"priority":100,"text":"D/I"},{"priority":100,"text":"D/I공정"},{"priority":100,"text":"D/I 공정"},{"priority":100,"text":"DVI"},{"priority":100,"text":"DVI공정"},{"priority":100,"text":"DVI 공정"}]},"process_group:DP":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DP","target_type":"process_group","values":[{"priority":100,"text":"DP"},{"priority":100,"text":"DP공정"},{"priority":100,"text":"DP 공정"},{"priority":100,"text":"D/P"},{"priority":100,"text":"D/P공정"},{"priority":100,"text":"D/P 공정"}]},"process_group:DS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DS","target_type":"process_group","values":[{"priority":100,"text":"DS"},{"priority":100,"text":"DS공정"},{"priority":100,"text":"DS 공정"},{"priority":100,"text":"D/S"},{"priority":100,"text":"D/S공정"},{"priority":100,"text":"D/S 공정"}]},"process_group:FCB":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB","target_type":"process_group","values":[{"priority":100,"text":"FCB"},{"priority":100,"text":"FCB공정"},{"priority":100,"text":"FCB 공정"}]},"process_group:FCBH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCBH","target_type":"process_group","values":[{"priority":100,"text":"FCBH"},{"priority":100,"text":"FCBH공정"},{"priority":100,"text":"FCBH 공정"},{"priority":100,"text":"FCB/H"},{"priority":100,"text":"FCB/H공정"},{"priority":100,"text":"FCB/H 공정"}]},"process_group:HS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"HS","target_type":"process_group","values":[{"priority":100,"text":"HS"},{"priority":100,"text":"HS공정"},{"priority":100,"text":"HS 공정"},{"priority":100,"text":"H/S"},{"priority":100,"text":"H/S공정"},{"priority":100,"text":"H/S 공정"}]},"process_group:LT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"LT","target_type":"process_group","values":[{"priority":100,"text":"LT"},{"priority":100,"text":"LT공정"},{"priority":100,"text":"LT 공정"},{"priority":100,"text":"L/T"},{"priority":100,"text":"L/T공정"},{"priority":100,"text":"L/T 공정"}]},"process_group:PC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PC","target_type":"process_group","values":[{"priority":100,"text":"PC"},{"priority":100,"text":"PC공정"},{"priority":100,"text":"PC 공정"},{"priority":100,"text":"P/C"},{"priority":100,"text":"P/C공정"},{"priority":100,"text":"P/C 공정"}]},"process_group:PCO":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PCO","target_type":"process_group","values":[{"priority":100,"text":"PCO"},{"priority":100,"text":"PCO공정"},{"priority":100,"text":"PCO 공정"}]},"process_group:PLH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PLH","target_type":"process_group","values":[{"priority":100,"text":"PLH"},{"priority":100,"text":"PLH공정"},{"priority":100,"text":"PLH 공정"},{"priority":100,"text":"P/L"},{"priority":100,"text":"P/L공정"},{"priority":100,"text":"P/L 공정"}]},"process_group:QCSPC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"QCSPC","target_type":"process_group","values":[{"priority":100,"text":"QCSPC"},{"priority":100,"text":"QCSPC공정"},{"priority":100,"text":"QCSPC 공정"}]},"process_group:SAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SAT","target_type":"process_group","values":[{"priority":100,"text":"SAT"},{"priority":100,"text":"SAT공정"},{"priority":100,"text":"SAT 공정"}]},"process_group:SBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SBM","target_type":"process_group","values":[{"priority":100,"text":"SBM"},{"priority":100,"text":"SBM공정"},{"priority":100,"text":"SBM 공정"}]},"process_group:SG":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SG","target_type":"process_group","values":[{"priority":100,"text":"SG"},{"priority":100,"text":"SG공정"},{"priority":100,"text":"SG 공정"},{"priority":100,"text":"S/G"},{"priority":100,"text":"S/G공정"},{"priority":100,"text":"S/G 공정"}]},"process_group:WB":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WB","target_type":"process_group","values":[{"priority":100,"text":"WB"},{"priority":100,"text":"WB공정"},{"priority":100,"text":"WB 공정"},{"priority":100,"text":"W/B"},{"priority":100,"text":"W/B공정"},{"priority":100,"text":"W/B 공정"}]},"process_group:WBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WBM","target_type":"process_group","values":[{"priority":120,"text":"WBM"},{"priority":120,"text":"WBM공정"},{"priority":120,"text":"WBM 공정"},{"priority":120,"text":"W/BM"},{"priority":120,"text":"W/BM공정"},{"priority":120,"text":"W/BM 공정"}]},"process_group:WEC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WEC","target_type":"process_group","values":[{"priority":100,"text":"WEC"},{"priority":100,"text":"WEC공정"},{"priority":100,"text":"WEC 공정"}]},"process_group:WET":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WET","target_type":"process_group","values":[{"priority":100,"text":"WET"},{"priority":100,"text":"WET공정"},{"priority":100,"text":"WET 공정"}]},"process_group:WLS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WLS","target_type":"process_group","values":[{"priority":100,"text":"WLS"},{"priority":100,"text":"WLS공정"},{"priority":100,"text":"WLS 공정"}]},"process_group:WS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WS","target_type":"process_group","values":[{"priority":100,"text":"WS"},{"priority":100,"text":"WS공정"},{"priority":100,"text":"WS 공정"},{"priority":100,"text":"W/S"},{"priority":100,"text":"W/S공정"},{"priority":100,"text":"W/S 공정"}]},"process_group:WSD":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WSD","target_type":"process_group","values":[{"priority":100,"text":"WSD"},{"priority":100,"text":"WSD공정"},{"priority":100,"text":"WSD 공정"}]},"product_group:AUTO":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"AUTO","target_type":"product_group","values":[{"priority":100,"text":"AUTO향"},{"priority":100,"text":"오토모티브향"},{"priority":100,"text":"오토향"}]},"product_group:HBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"HBM","target_type":"product_group","values":[{"priority":100,"text":"HBM"},{"priority":100,"text":"3DS"},{"priority":100,"text":"TSV"}]},"product_group:MOBILE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"MOBILE","target_type":"product_group","values":[{"priority":100,"text":"Mobile"},{"priority":100,"text":"MOBILE"},{"priority":100,"text":"모바일"}]},"product_group:POP":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"POP","target_type":"product_group","values":[{"priority":100,"text":"POP"},{"priority":100,"text":"pop"},{"priority":100,"text":"Pop"}]},"product_group:STACK_2HI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"STACK_2HI","target_type":"product_group","values":[{"priority":100,"text":"2Hi"}]},"product_group:STACK_4HI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"STACK_4HI","target_type":"product_group","values":[{"priority":100,"text":"4Hi"}]},"product_group:STACK_8HI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"STACK_8HI","target_type":"product_group","values":[{"priority":100,"text":"8Hi"}]},"recipe:achievement.input_actual":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"achievement.input_actual","target_type":"recipe","values":[{"priority":100,"text":"생산달성률"},{"priority":100,"text":"생산달성율"},{"priority":100,"text":"INPUT 계획 대비 실적"}]},"recipe:equipment.assignment_enrich":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"equipment.assignment_enrich","target_type":"recipe","values":[{"priority":100,"text":"할당된 장비 대수와 LIST"},{"priority":100,"text":"장비 배정"},{"priority":100,"text":"장비 목록"}]},"recipe:equipment.assignment_uph":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"equipment.assignment_uph","target_type":"recipe","values":[{"priority":100,"text":"장비별 UPH"},{"priority":100,"text":"배정 장비 UPH"},{"priority":100,"text":"장비와 Recipe UPH"}]},"recipe:hold.oldest_current_history":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"hold.oldest_current_history","target_type":"recipe","values":[{"priority":100,"text":"HOLD 시간이 가장 오래된 LOT"},{"priority":100,"text":"오래된 HOLD 이력"}]},"recipe:join.operation.production_wip":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"join.operation.production_wip","target_type":"recipe","values":[{"priority":100,"text":"생산량과 재공수량"},{"priority":100,"text":"생산 WIP 비교"}]},"recipe:ordered.process.range":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"ordered.process.range","target_type":"recipe","values":[{"priority":100,"text":"공정 구간"},{"priority":100,"text":"공정 범위"},{"priority":100,"text":"OPER_SEQ 범위"}]},"recipe:presence.left_positive_right_zero":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"presence.left_positive_right_zero","target_type":"recipe","values":[{"priority":100,"text":"A는 있으나 B는 없음"},{"priority":100,"text":"실적 있음 재공 없음"},{"priority":100,"text":"존재 미존재"}]},"recipe:product.standard":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"product.standard","target_type":"recipe","values":[{"priority":100,"text":"제품별"},{"priority":100,"text":"제품 기준"},{"priority":100,"text":"제품 집계"}]},"recipe:rank.bottom_n":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"rank.bottom_n","target_type":"recipe","values":[{"priority":100,"text":"하위 N개"},{"priority":100,"text":"가장 적은"},{"priority":100,"text":"BOTTOM N"}]},"recipe:rank.top_n":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"rank.top_n","target_type":"recipe","values":[{"priority":100,"text":"상위 N개"},{"priority":100,"text":"가장 많은"},{"priority":100,"text":"TOP N"}]},"status:SHIFT_A":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT_A","target_type":"status","values":[{"priority":100,"text":"Shift A조"},{"priority":100,"text":"SHIFT A조"},{"priority":100,"text":"Shift A"},{"priority":100,"text":"A조"},{"priority":100,"text":"1조"},{"priority":100,"text":"07:00~15:00"}]},"status:SHIFT_B":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT_B","target_type":"status","values":[{"priority":100,"text":"Shift B조"},{"priority":100,"text":"SHIFT B조"},{"priority":100,"text":"Shift B"},{"priority":100,"text":"B조"},{"priority":100,"text":"2조"},{"priority":100,"text":"15:00~23:00"}]},"status:SHIFT_C":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT_C","target_type":"status","values":[{"priority":100,"text":"Shift C조"},{"priority":100,"text":"SHIFT C조"},{"priority":100,"text":"Shift C"},{"priority":100,"text":"C조"},{"priority":100,"text":"3조"},{"priority":100,"text":"23:00~07:00"}]}},"catalog_sha256":"1f8b6c1522b96425a6a46a3e4dfcf4c5b7c338c6bc0af3c2a0878806ea4a7f8e","contract_version":"metadata.runtime.catalog.v1","datasets":{"eqp_uph":{"config_ref":"config:oracle:GMS_DB@1","default_detail_fields":["EQP_MODEL","RECIPE_ID","OPER_NAME"],"family":"equipment_uph","fields":{"BASE_DATE":{"coercion":"strict_date","nullable":true,"physical_aliases":[],"physical_column":"BASE_DT","required_in_source":false,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"EQP_MODEL":{"coercion":"string","nullable":true,"physical_aliases":["EQP_MODEL"],"physical_column":"EQUIP_MODEL","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOAD_DATE":{"coercion":"strict_date","nullable":true,"physical_aliases":[],"physical_column":"LOAD_DT","required_in_source":false,"roles":["filter","output"],"semantic_type":"LocalDate"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRESS_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRESS_CNT","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"RECIPE_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"RECIPE_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"UPH":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"UPH","required_in_source":true,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"eqp_uph","parameters":{},"query_ref":"query:eqp_uph@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"GMS_DB","query_template":"SELECT \\n\\n  EQUIP_MODEL\\n  ,OPER\\n  ,OPER_NAME\\n  ,PRESS_CNT\\n  ,PROD_TYP AS \\"MODE\\"\\n  ,TECH\\n  ,ORG\\n  ,DENSITY\\n  ,PKG_TYP AS PKG1\\n  ,PKG_TYP_2 AS PKG2\\n  ,LEAD_CNT AS LEAD\\n  ,MCP_NO\\n  ,RECIPE_ID \\n  ,round(AVG_UPH_VAL,2) AS UPH\\n  ,WORK_DT AS LOAD_DT\\n  ,BASE_DT\\nFROM UPH\\nWHERE 1=1","required_params":[],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"equipment_assign":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["EQP_ID"],"family":"equipment","fields":{"BAY_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"BAY_ID","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"EQP_ID":{"coercion":"string","nullable":true,"physical_aliases":["EQP_ID"],"physical_column":"EQUIP_ID","required_in_source":false,"roles":["filter","group","aggregate","join","output"],"semantic_type":"identifier"},"EQP_MODEL":{"coercion":"string","nullable":true,"physical_aliases":["EQP_MODEL"],"physical_column":"EQUIP_MODEL","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOT_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LOT_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NAME"],"physical_column":"OPER_NM","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRESS_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRESS_CNT","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"RECIPE_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"RECIPE_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"}},"key":"equipment_assign","parameters":{},"query_ref":"query:equipment_assign@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"SELECT \\n  BAY_ID, \\n  EQUIP_ID, \\n  EQUIP_MODEL, \\n  PRESS_CNT,\\n  OPER,\\n  OPER_NM,\\n  MODE, \\n  DENSITY, \\n  TECH, \\n  PKG1, \\n  PKG2, \\n  LEAD, \\n  ORG,\\n  PKGSIZE,  \\n  MCP_NO,\\n  DEVICE,\\n  DEVICE_DESC,\\n  LOT_ID,\\n  RECIPE_ID\\nFROM  EQP_TABLE\\nWHERE 1=1","required_params":[],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"hold_history":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["LOT_ID","OPER_NAME","HOLD_EVENT_AT","HOLD_CD","HOLD_DESC"],"family":"hold_history","fields":{"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"HOLD_CD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_CD","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"HOLD_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"HOLD_EVENT_AT":{"coercion":"strict_datetime","nullable":false,"physical_aliases":[],"physical_column":"HOLD_TM","required_in_source":true,"roles":["filter","aggregate","sort","derive","output"],"semantic_type":"LocalDateTime","timezone":"Asia/Seoul"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOT_ID":{"coercion":"string","nullable":false,"physical_aliases":[],"physical_column":"LOT_ID","required_in_source":true,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PROD_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PROD_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"}},"key":"hold_history","parameters":{"LOT_ID":{"chunk_size":200,"max_total_values":2000,"operator":"in","required":true,"type":"list[identifier]"}},"query_ref":"query:hold_history@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"/*HOLD_LOT_HISTORY*/\\n\\n        SELECT\\n\\n            LOT_ID,\\n            PROD_QTY,\\n            OPER,\\n            OPER_NAME,\\n            HOLD_TM,\\n            HOLD_CD,\\n            HOLD_USER,\\n            HOLD_DESC,\\n            FAB,\\n            FAMILY,\\n            MODE,\\n            DENSITY,\\n            TECH,\\n            ORG,\\n            PKG1,\\n            PKG2,\\n            LEAD,\\n            MCP_NO,\\n            GRADE,\\n            OWNER,\\n            \\n            DEVICE,\\n            DEVICE_DESC,\\n            PKG_SIZE,\\n            THK_CD,\\n            flow_id   \\n        FROM HOLD_HIS\\n        WHERE LOT_ID IN ({LOT_ID})","required_params":["LOT_ID"],"source_type":"oracle"},"source_type":"oracle","time_scope":"history","upstream_bindings":[{"chunk_size":200,"dedupe":true,"entity_type":"lot","max_total_values":2000,"operator":"in","sort_values":"asc","source_alias":"previous_result","source_field":"LOT_ID","target_parameter":"LOT_ID"}]},"lot_status":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["LOT_ID","OPER_NAME","PROD_QTY","WF_QTY","IN_TAT","CUM_TAT","HOLD_STAT","HOLD_REASON","LOT_STAT"],"family":"lot","fields":{"CUM_TAT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"CUM_TAT","required_in_source":false,"roles":["filter","aggregate","rank","sort","output"],"semantic_type":"number"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"EQP_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"EQP_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAC_IN_AT":{"coercion":"strict_datetime","nullable":true,"physical_aliases":[],"physical_column":"FAC_IN_TIME","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"LocalDateTime","timezone":"Asia/Seoul"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"HOLD_REASON":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_REASON","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"HOLD_STAT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_STAT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"IN_TAT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"IN_TAT","required_in_source":false,"roles":["filter","aggregate","rank","sort","output"],"semantic_type":"number"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOT_ID":{"coercion":"string","nullable":false,"physical_aliases":[],"physical_column":"LOT_ID","required_in_source":true,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"LOT_STAT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LOT_STAT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OPER_IN_AT":{"coercion":"strict_datetime","nullable":true,"physical_aliases":[],"physical_column":"OPER_IN_TM","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"LocalDateTime","timezone":"Asia/Seoul"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":false,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":true,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PROD_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PROD_QTY","required_in_source":false,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"WF_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"WF_QTY","required_in_source":false,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"lot_status","parameters":{},"query_ref":"query:lot_status@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"/*Current Wip Status*/\\nSELECT\\nERM_ID,OPER,OPER_NAME,FAB,OWNER,GRADE,DEVICE,LOT_ID,SUB_LOT_ID,PROD_QTY,WF_QTY,IN_TAT,CUM_TAT,EQP_ID,FLOW_ID,OPER_IN_TM,FAC_IN_TIME,HOLD_STAT,HOLD_REASON,FAMILY,MODE,DENSITY,TECH,ORG,PKG1,PKG2,PKG3,LEAD,MCP_NO,THK_CD,LOT_STAT,LOT_GRP,PKG_SIZE,HOT_LOT,HOT_LEVEL,PKG_COMPOSIT,DURABLE_ID,DURABLE_TYP,SUB_QTY,TSV_DIE_TYPE,EVENT_DESC,MOVE_IN_TM,PAD_ABNORMAL,SWR_REQ_NO,INSP_TARGET\\nFROM WIP_STATE\\nWHERE 1=1","required_params":[],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"product_master":{"config_ref":"config:fixture:operator_validation@1","default_detail_fields":["DEVICE","YIELD_RATE","MODE","LEAD"],"family":"product_master","fields":{"DEN":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEN","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":false,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":true,"roles":["filter","group","join","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"PKG_TYPE1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"PKG_TYPE2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"YIELD_RATE":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"YIELD_RATE","required_in_source":false,"roles":["filter","rank","output"],"semantic_type":"number"}},"fixture_only":true,"key":"product_master","parameters":{},"query_ref":"query:product_master_fixture@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_type":"fixture","time_scope":"current"},"production":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","PRODUCTION_QTY"],"family":"production","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRODUCTION_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRODUCTION","required_in_source":true,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"}},"key":"production","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:production_history@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"SELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ, PRODUCTION \\nFROM PROD_TABLE2\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"history"},"production_today":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","PRODUCTION_QTY"],"family":"production","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRODUCTION_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRODUCTION","required_in_source":true,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"}},"key":"production_today","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:production_today@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"--쿼리 작성\\nSELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ, PRODUCTION \\nFROM PROD_TABLE\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"target":{"config_ref":"config:goodocs:target@1","date_filter_contract":{"canonical_field":"DATE","source_format":"%Y-%m-%d","timezone":"Asia/Seoul"},"default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DATE","INPUT_PLAN_QTY","OUT_PLAN_QTY"],"family":"target","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":[],"physical_column":"DATE","required_in_source":true,"roles":["filter","sort","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DENSITY"],"physical_column":"DEN","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"INPUT_PLAN_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"INPUT 계획","required_in_source":false,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":["MCP_NO"],"physical_column":"MCP NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":["MODE"],"physical_column":"Mode","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OUT_PLAN_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OUT 계획","required_in_source":false,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"}},"key":"target","parameters":{},"query_ref":"query:target_plan@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_type":"goodocs","time_scope":"history"},"wip":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","WIP_QTY"],"family":"wip","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"WIP_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"WIP","required_in_source":true,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"wip","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:wip_history@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"--쿼리 작성\\nSELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ\\n        , WIP\\nFROM WIP_TABLE2\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"history"},"wip_today":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","WIP_QTY"],"family":"wip","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"WIP_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"WIP","required_in_source":true,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"wip_today","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:wip_today@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"SELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ\\n        , WIP\\nFROM WIP_TABLE\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"}},"fields":{"BASE_DATE":{"datasets":["eqp_uph"],"display_label":"BASE_DATE","key":"BASE_DATE","roles":["filter","output"],"semantic_type":"LocalDate"},"BAY_ID":{"datasets":["equipment_assign"],"display_label":"BAY_ID","key":"BAY_ID","roles":["filter","group","output"],"semantic_type":"string"},"CUM_TAT":{"datasets":["lot_status"],"display_label":"CUM_TAT","key":"CUM_TAT","roles":["aggregate","filter","output","rank","sort"],"semantic_type":"number"},"DATE":{"datasets":["production","production_today","target","wip","wip_today"],"display_label":"DATE","key":"DATE","roles":["filter","output","sort"],"semantic_type":"LocalDate"},"DEN":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"DEN","key":"DEN","roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"datasets":["equipment_assign","hold_history","lot_status","product_master","production","production_today","wip","wip_today"],"display_label":"DEVICE","key":"DEVICE","roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"datasets":["equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"DEVICE_DESC","key":"DEVICE_DESC","roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"DIE_ATTACH_QTY","key":"DIE_ATTACH_QTY","roles":["aggregate","filter","output"],"semantic_type":"number"},"EQP_ID":{"datasets":["equipment_assign","lot_status"],"display_label":"EQP_ID","key":"EQP_ID","roles":["aggregate","filter","group","join","output"],"semantic_type":"identifier"},"EQP_MODEL":{"datasets":["eqp_uph","equipment_assign"],"display_label":"EQP_MODEL","key":"EQP_MODEL","roles":["filter","group","join","output"],"semantic_type":"string"},"FAB":{"datasets":["equipment_assign","lot_status","production","production_today","wip","wip_today"],"display_label":"FAB","key":"FAB","roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"FACTORY","key":"FACTORY","roles":["filter","group","output"],"semantic_type":"string"},"FAC_IN_AT":{"datasets":["lot_status"],"display_label":"FAC_IN_AT","key":"FAC_IN_AT","roles":["filter","output","sort"],"semantic_type":"LocalDateTime"},"FAMILY":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"FAMILY","key":"FAMILY","roles":["filter","group","output"],"semantic_type":"string"},"HOLD_CD":{"datasets":["hold_history"],"display_label":"HOLD_CD","key":"HOLD_CD","roles":["filter","group","output"],"semantic_type":"string"},"HOLD_DESC":{"datasets":["hold_history"],"display_label":"HOLD_DESC","key":"HOLD_DESC","roles":["filter","output"],"semantic_type":"string"},"HOLD_EVENT_AT":{"datasets":["hold_history"],"display_label":"HOLD_EVENT_AT","key":"HOLD_EVENT_AT","roles":["aggregate","derive","filter","output","sort"],"semantic_type":"LocalDateTime"},"HOLD_REASON":{"datasets":["lot_status"],"display_label":"HOLD_REASON","key":"HOLD_REASON","roles":["filter","output"],"semantic_type":"string"},"HOLD_STAT":{"datasets":["lot_status"],"display_label":"HOLD_STAT","key":"HOLD_STAT","roles":["filter","group","output"],"semantic_type":"string"},"INPUT_PLAN_QTY":{"datasets":["target"],"display_label":"INPUT_PLAN_QTY","key":"INPUT_PLAN_QTY","roles":["aggregate","derive","filter","output","rank"],"semantic_type":"number"},"IN_TAT":{"datasets":["lot_status"],"display_label":"IN_TAT","key":"IN_TAT","roles":["aggregate","filter","output","rank","sort"],"semantic_type":"number"},"LEAD":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"LEAD","key":"LEAD","roles":["filter","group","join","output"],"semantic_type":"string"},"LOAD_DATE":{"datasets":["eqp_uph"],"display_label":"LOAD_DATE","key":"LOAD_DATE","roles":["filter","output"],"semantic_type":"LocalDate"},"LOT_ID":{"datasets":["equipment_assign","hold_history","lot_status"],"display_label":"LOT_ID","key":"LOT_ID","roles":["filter","group","join","output"],"semantic_type":"identifier"},"LOT_STAT":{"datasets":["lot_status"],"display_label":"LOT_STAT","key":"LOT_STAT","roles":["filter","group","output"],"semantic_type":"string"},"MCP_NO":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"MCP_NO","key":"MCP_NO","roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"MODE","key":"MODE","roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"NETDIE_300_CNT","key":"NETDIE_300_CNT","roles":["aggregate","derive","filter","output"],"semantic_type":"number"},"OPER_IN_AT":{"datasets":["lot_status"],"display_label":"OPER_IN_AT","key":"OPER_IN_AT","roles":["filter","output","sort"],"semantic_type":"LocalDateTime"},"OPER_NAME":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"OPER_NAME","key":"OPER_NAME","roles":["filter","group","join","output","sort"],"semantic_type":"string"},"OPER_NUM":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"OPER_NUM","key":"OPER_NUM","roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"datasets":["eqp_uph","lot_status","production","production_today","wip","wip_today"],"display_label":"OPER_SEQ","key":"OPER_SEQ","roles":["filter","output","sort"],"semantic_type":"number"},"ORG":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","target","wip","wip_today"],"display_label":"ORG","key":"ORG","roles":["filter","group","join","output"],"semantic_type":"string"},"OUT_PLAN_QTY":{"datasets":["target"],"display_label":"OUT_PLAN_QTY","key":"OUT_PLAN_QTY","roles":["aggregate","derive","filter","output","rank"],"semantic_type":"number"},"PKG_TYPE1":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"PKG_TYPE1","key":"PKG_TYPE1","roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"PKG_TYPE2","key":"PKG_TYPE2","roles":["filter","group","join","output"],"semantic_type":"string"},"PRESS_CNT":{"datasets":["eqp_uph","equipment_assign"],"display_label":"PRESS_CNT","key":"PRESS_CNT","roles":["aggregate","filter","output"],"semantic_type":"number"},"PRODUCTION_QTY":{"datasets":["production","production_today"],"display_label":"PRODUCTION_QTY","key":"PRODUCTION_QTY","roles":["aggregate","derive","filter","output","rank"],"semantic_type":"number"},"PROD_QTY":{"datasets":["hold_history","lot_status"],"display_label":"PROD_QTY","key":"PROD_QTY","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"RECIPE_ID":{"datasets":["eqp_uph","equipment_assign"],"display_label":"RECIPE_ID","key":"RECIPE_ID","roles":["filter","group","join","output"],"semantic_type":"identifier"},"SHIFT":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"SHIFT","key":"SHIFT","roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"TECH","key":"TECH","roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"datasets":["equipment_assign","lot_status","production","production_today","wip","wip_today"],"display_label":"TSV_DIE_TYP","key":"TSV_DIE_TYP","roles":["filter","group","output"],"semantic_type":"string"},"UPH":{"datasets":["eqp_uph"],"display_label":"UPH","key":"UPH","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"WF_QTY":{"datasets":["lot_status"],"display_label":"WF_QTY","key":"WF_QTY","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"WIP_QTY":{"datasets":["wip","wip_today"],"display_label":"WIP_QTY","key":"WIP_QTY","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"YIELD_RATE":{"datasets":["product_master"],"display_label":"YIELD_RATE","key":"YIELD_RATE","roles":["filter","output","rank"],"semantic_type":"number"}},"metrics":{"ACHIEVEMENT_RATE":{"dependencies":["INPUT_QTY","INPUT_PLAN_QTY"],"formula":{"evaluation_stage":"after_aggregate","expression":{"args":[{"args":[{"metric_ref":"INPUT_QTY"},{"metric_ref":"INPUT_PLAN_QTY"}],"op":"safe_divide","zero_division":"null"},{"literal":100,"value_type":"number"}],"op":"multiply"},"max_depth":6,"max_nodes":32,"rounding":{"digits":1,"mode":"half_even"},"version":"formula.v1"},"metric_id":"ACHIEVEMENT_RATE","unit":"percent","value_type":"number"},"CUM_TAT":{"additivity":{"allowed_rollups":["min","max","mean"],"default":"non_additive"},"metric_id":"CUM_TAT","null_policy":"exclude","source_binding":{"dataset_family":"lot","field":"CUM_TAT"},"unit":"hour","value_type":"number","zero_policy":"preserve_zero"},"EQP_COUNT":{"additivity":{"allowed_rollups":["nunique"],"default":"distinct"},"metric_id":"EQP_COUNT","null_policy":"exclude","source_binding":{"dataset_family":"equipment","field":"EQP_ID"},"unit":"equipment","value_type":"integer","zero_policy":"preserve_zero"},"HOLD_DURATION_HOURS":{"additivity":{"allowed_rollups":["min","max"],"default":"non_additive"},"dependencies":["HOLD_EVENT_AT","reference_instant"],"formula":{"evaluation_stage":"after_aggregate","expression":{"args":[{"runtime_ref":"reference_instant"},{"field_ref":"CURRENT_HOLD_STARTED_AT"}],"op":"datetime_diff_hours"},"max_depth":3,"max_nodes":8,"rounding":{"digits":3,"mode":"half_even"},"version":"formula.v1"},"metric_id":"HOLD_DURATION_HOURS","null_policy":"exclude","unit":"hour","value_type":"number","zero_policy":"preserve_zero"},"INPUT_PLAN_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"INPUT_PLAN_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"target","field":"INPUT_PLAN_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"INPUT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"INPUT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY","fixed_filters":[{"field":"OPER_NAME","operator":"eq","semantic_type":"string","value":"INPUT"}]},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"IN_TAT":{"additivity":{"allowed_rollups":["min","max","mean"],"default":"non_additive"},"metric_id":"IN_TAT","null_policy":"exclude","source_binding":{"dataset_family":"lot","field":"IN_TAT"},"unit":"hour","value_type":"number","zero_policy":"preserve_zero"},"LOT_COUNT":{"additivity":{"allowed_rollups":["nunique"],"default":"distinct"},"metric_id":"LOT_COUNT","null_policy":"exclude","source_binding":{"dataset_family":"lot","field":"LOT_ID"},"unit":"lot","value_type":"integer","zero_policy":"preserve_zero"},"OUT_PLAN_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"OUT_PLAN_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"target","field":"OUT_PLAN_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"OUT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"OUT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY","fixed_filters":[{"field":"OPER_NAME","operator":"eq","semantic_type":"string","value":"PKG OUT"}]},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"PKG_OUT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"PKG_OUT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY","fixed_filters":[{"field":"OPER_NAME","operator":"eq","semantic_type":"string","value":"PKG OUT"}]},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"PRODUCTION_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"PRODUCTION_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"UNIT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"UNIT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"lot","field":"PROD_QTY"},"unit":"unit","value_type":"number","zero_policy":"preserve_zero"},"UPH":{"additivity":{"allowed_rollups":["mean"],"default":"non_additive"},"metric_id":"UPH","null_policy":"exclude_from_mean","source_binding":{"dataset_family":"equipment_uph","field":"UPH"},"unit":"unit_per_hour","value_type":"number","zero_policy":"preserve_zero"},"WAFER_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"WAFER_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"lot","field":"WF_QTY"},"unit":"wafer","value_type":"number","zero_policy":"preserve_zero"},"WIP_BOH_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"WIP_BOH_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"wip","field":"WIP_QTY"},"temporal_contract":{"business_timepoint":"BOH","dataset_selector":{"dataset_key":"wip","family":"wip","time_scope":"history"},"disallowed_dataset_keys":["wip_today"],"display_date":"requested_date","inherit_filters":true,"query_time":{"anchor":"requested_date","calendar":"gregorian","offset_days":-1,"timezone":"Asia/Seoul"},"source_parameter":"DATE"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"WIP_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"WIP_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"wip","field":"WIP_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"}},"process_groups":{"BG":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["BG","BG공정","BG 공정","B/G","B/G공정","B/G 공정"],"display_name":"B/G","expansion":"closed_set","group_id":"process_group.BG","members":["B/G1","B/G2"],"target_field":"OPER_NAME"},"BM":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["BM","BM공정","BM 공정","B/M","B/M공정","B/M 공정","비엠","비엠공정","비엠 공정"],"display_name":"B/M","expansion":"closed_set","group_id":"process_group.BM","members":["B/M"],"target_field":"OPER_NAME"},"DA":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DA","DA공정","DA 공정","D/A","D/A공정","D/A 공정"],"display_name":"D/A","expansion":"closed_set","group_id":"process_group.DA","members":["D/A1","D/A2","D/A3","D/A4","D/A5","D/A6"],"target_field":"OPER_NAME"},"DC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DC","DC공정","DC 공정","D/C","D/C공정","D/C 공정"],"display_name":"D/C","expansion":"closed_set","group_id":"process_group.DC","members":["D/C1","D/C2","D/C3","D/C4"],"target_field":"OPER_NAME"},"DI":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DI","DI공정","DI 공정","D/I","D/I공정","D/I 공정","DVI","DVI공정","DVI 공정"],"display_name":"D/I","expansion":"closed_set","group_id":"process_group.DI","members":["D/I"],"target_field":"OPER_NAME"},"DP":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DP","DP공정","DP 공정","D/P","D/P공정","D/P 공정"],"display_name":"DP","expansion":"closed_set","group_id":"process_group.DP","members":["WET1","WET2","L/T1","L/T2","B/G1","B/G2","H/S1","H/S2","W/S1","W/S2","WSD1","WSD2","WEC1","WEC2","WLS1","WLS2","WVI","UV","C/C1"],"target_field":"OPER_NAME"},"DS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DS","DS공정","DS 공정","D/S","D/S공정","D/S 공정"],"display_name":"D/S","expansion":"closed_set","group_id":"process_group.DS","members":["D/S1"],"target_field":"OPER_NAME"},"FCB":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["FCB","FCB공정","FCB 공정"],"display_name":"FCB","expansion":"closed_set","group_id":"process_group.FCB","members":["FCB1","FCB2","FCB/H"],"target_field":"OPER_NAME"},"FCBH":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["FCBH","FCBH공정","FCBH 공정","FCB/H","FCB/H공정","FCB/H 공정"],"display_name":"FCB/H","expansion":"closed_set","group_id":"process_group.FCBH","members":["FCB/H"],"target_field":"OPER_NAME"},"HS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["HS","HS공정","HS 공정","H/S","H/S공정","H/S 공정"],"display_name":"H/S","expansion":"closed_set","group_id":"process_group.HS","members":["H/S1","H/S2"],"target_field":"OPER_NAME"},"LT":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["LT","LT공정","LT 공정","L/T","L/T공정","L/T 공정"],"display_name":"L/T","expansion":"closed_set","group_id":"process_group.LT","members":["L/T1","L/T2"],"target_field":"OPER_NAME"},"PC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["PC","PC공정","PC 공정","P/C","P/C공정","P/C 공정"],"display_name":"P/C","expansion":"closed_set","group_id":"process_group.PC","members":["P/C1","P/C2","P/C3","P/C4","P/C5"],"target_field":"OPER_NAME"},"PCO":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["PCO","PCO공정","PCO 공정"],"display_name":"PCO","expansion":"closed_set","group_id":"process_group.PCO","members":["PCO1","PCO2","PCO3","PCO4","PCO5","PCO6"],"target_field":"OPER_NAME"},"PLH":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["PLH","PLH공정","PLH 공정","P/L","P/L공정","P/L 공정"],"display_name":"P/L","expansion":"closed_set","group_id":"process_group.PLH","members":["PLH"],"target_field":"OPER_NAME"},"QCSPC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["QCSPC","QCSPC공정","QCSPC 공정"],"display_name":"QCSPC","expansion":"closed_set","group_id":"process_group.QCSPC","members":["QCSPC1","QCSPC2","QCSPC3","QCSPC4"],"target_field":"OPER_NAME"},"SAT":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["SAT","SAT공정","SAT 공정"],"display_name":"SAT","expansion":"closed_set","group_id":"process_group.SAT","members":["SAT1","SAT2"],"target_field":"OPER_NAME"},"SBM":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["SBM","SBM공정","SBM 공정"],"display_name":"SBM","expansion":"closed_set","group_id":"process_group.SBM","members":["SBM"],"target_field":"OPER_NAME"},"SG":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["SG","SG공정","SG 공정","S/G","S/G공정","S/G 공정"],"display_name":"S/G","expansion":"closed_set","group_id":"process_group.SG","members":["S/G"],"target_field":"OPER_NAME"},"WB":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WB","WB공정","WB 공정","W/B","W/B공정","W/B 공정"],"display_name":"W/B","expansion":"closed_set","group_id":"process_group.WB","members":["W/B1","W/B2","W/B3","W/B4","W/B5","W/B6"],"target_field":"OPER_NAME"},"WBM":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WBM","WBM공정","WBM 공정","W/BM","W/BM공정","W/BM 공정"],"display_name":"W/BM","expansion":"closed_set","group_id":"process_group.WBM","members":["W/BM"],"target_field":"OPER_NAME"},"WEC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WEC","WEC공정","WEC 공정"],"display_name":"WEC","expansion":"closed_set","group_id":"process_group.WEC","members":["WEC1","WEC2"],"target_field":"OPER_NAME"},"WET":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WET","WET공정","WET 공정"],"display_name":"WET","expansion":"closed_set","group_id":"process_group.WET","members":["WET1","WET2"],"target_field":"OPER_NAME"},"WLS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WLS","WLS공정","WLS 공정"],"display_name":"WLS","expansion":"closed_set","group_id":"process_group.WLS","members":["WLS1","WLS2"],"target_field":"OPER_NAME"},"WS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WS","WS공정","WS 공정","W/S","W/S공정","W/S 공정"],"display_name":"W/S","expansion":"closed_set","group_id":"process_group.WS","members":["W/S1","W/S2"],"target_field":"OPER_NAME"},"WSD":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WSD","WSD공정","WSD 공정"],"display_name":"WSD","expansion":"closed_set","group_id":"process_group.WSD","members":["WSD1","WSD2"],"target_field":"OPER_NAME"}},"process_order":[{"aliases":["INPUT"],"oper_name":"INPUT","oper_seq":10,"revision":1},{"aliases":["DA1"],"oper_name":"D/A1","oper_seq":100,"revision":1},{"aliases":["DA2"],"oper_name":"D/A2","oper_seq":110,"revision":1},{"aliases":["DA3"],"oper_name":"D/A3","oper_seq":120,"revision":1},{"aliases":["DA4"],"oper_name":"D/A4","oper_seq":130,"revision":1},{"aliases":["DA5"],"oper_name":"D/A5","oper_seq":140,"revision":1},{"aliases":["DA6"],"oper_name":"D/A6","oper_seq":150,"revision":1},{"aliases":["DS1"],"oper_name":"D/S1","oper_seq":160,"revision":1},{"aliases":["WB1"],"oper_name":"W/B1","oper_seq":200,"revision":1},{"aliases":["WB2"],"oper_name":"W/B2","oper_seq":210,"revision":1},{"aliases":["WB3"],"oper_name":"W/B3","oper_seq":220,"revision":1},{"aliases":["WB4"],"oper_name":"W/B4","oper_seq":230,"revision":1},{"aliases":["WB5"],"oper_name":"W/B5","oper_seq":240,"revision":1},{"aliases":["WB6"],"oper_name":"W/B6","oper_seq":250,"revision":1},{"aliases":["WBM"],"oper_name":"W/BM","oper_seq":260,"revision":1},{"aliases":["FCB1"],"oper_name":"FCB1","oper_seq":300,"revision":1},{"aliases":["FCB2"],"oper_name":"FCB2","oper_seq":310,"revision":1},{"aliases":["FCBH"],"oper_name":"FCB/H","oper_seq":320,"revision":1},{"aliases":["BG1"],"oper_name":"B/G1","oper_seq":400,"revision":1},{"aliases":["BG2"],"oper_name":"B/G2","oper_seq":410,"revision":1},{"aliases":["SBM"],"oper_name":"SBM","oper_seq":500,"revision":1},{"aliases":["PKG OUT"],"oper_name":"PKG OUT","oper_seq":900,"revision":1}],"product_groups":{"AUTO":{"aliases":["AUTO향","오토모티브향","오토향"],"allowed_operators":["ends_with"],"grain_id":"product.standard","group_id":"product_group.AUTO","predicate":{"clauses":[{"field":"MCP_NO","operator":"ends_with","value":"I"},{"field":"MCP_NO","operator":"ends_with","value":"O"},{"field":"MCP_NO","operator":"ends_with","value":"N"},{"field":"MCP_NO","operator":"ends_with","value":"P"},{"field":"MCP_NO","operator":"ends_with","value":"Q"},{"field":"MCP_NO","operator":"ends_with","value":"V"}],"op":"any"}},"HBM":{"aliases":["HBM","3DS","TSV"],"allowed_operators":["is_not_blank"],"grain_id":"product.standard","group_id":"product_group.HBM","predicate":{"field":"TSV_DIE_TYP","operator":"is_not_blank"}},"MOBILE":{"aliases":["Mobile","MOBILE","모바일"],"allowed_operators":["eq","in","starts_with","null_or_blank","is_not_blank"],"grain_id":"product.standard","group_id":"product_group.MOBILE","predicate":{"clauses":[{"field":"MODE","operator":"starts_with","value":"LP"},{"field":"PKG_TYPE1","operator":"in","values":["LFBGA","TFBGA","UFBGA","VFBGA","WFBGA"]},{"field":"MCP_NO","operator":"null_or_blank"}],"op":"all"}},"POP":{"aliases":["POP","pop","Pop"],"allowed_operators":["eq","in","starts_with","null_or_blank","is_not_blank"],"grain_id":"product.standard","group_id":"product_group.POP","predicate":{"clauses":[{"field":"MODE","operator":"starts_with","value":"LP"},{"field":"PKG_TYPE1","operator":"in","values":["LFBGA","TFBGA","UFBGA","VFBGA","WFBGA"]},{"field":"MCP_NO","operator":"is_not_blank"}],"op":"all"}},"STACK_2HI":{"aliases":["2Hi"],"allowed_operators":["eq"],"grain_id":"product.standard","group_id":"product_group.STACK_2HI","predicate":{"field":"TSV_DIE_TYP","operator":"eq","value":"2Hi"}},"STACK_4HI":{"aliases":["4Hi"],"allowed_operators":["eq"],"grain_id":"product.standard","group_id":"product_group.STACK_4HI","predicate":{"field":"TSV_DIE_TYP","operator":"eq","value":"4Hi"}},"STACK_8HI":{"aliases":["8Hi"],"allowed_operators":["eq"],"grain_id":"product.standard","group_id":"product_group.STACK_8HI","predicate":{"field":"TSV_DIE_TYP","operator":"eq","value":"8Hi"}}},"recipes":{"achievement.input_actual":{"aliases":["생산달성률","생산달성율","INPUT 계획 대비 실적"],"default_operation_template":{"aggregate_before_derive":true,"derive":{"formula_ref":"metric:ACHIEVEMENT_RATE","op":"derive","output_field":"ACHIEVEMENT_RATE"}},"metrics":["INPUT_QTY","INPUT_PLAN_QTY","ACHIEVEMENT_RATE"],"recipe_id":"achievement.input_actual","required_slots":["actual_input","target_input","grain"]},"equipment.assignment_enrich":{"aliases":["할당된 장비 대수와 LIST","장비 배정","장비 목록"],"datasets":["equipment_assign"],"default_operation_template":{"cardinality":"one_to_one_after_aggregate","how":"left","keys":[{"left":"TECH","right":"TECH"},{"left":"DEN","right":"DEN"},{"left":"MODE","right":"MODE"},{"left":"PKG_TYPE1","right":"PKG_TYPE1"},{"left":"PKG_TYPE2","right":"PKG_TYPE2"},{"left":"LEAD","right":"LEAD"},{"left":"MCP_NO","right":"MCP_NO"}],"op":"enrich_previous_result","right_pre_aggregate":[{"as":"EQP_COUNT","field":"EQP_ID","function":"nunique"},{"as":"EQP_LIST","field":"EQP_ID","function":"list_unique"}],"suffix_policy":"forbid"},"recipe_id":"equipment.assignment_enrich","required_slots":["previous_product_result"]},"equipment.assignment_uph":{"aliases":["장비별 UPH","배정 장비 UPH","장비와 Recipe UPH"],"datasets":["equipment_assign","eqp_uph"],"default_operation_template":{"cardinality":"many_to_one","how":"left","keys":[{"left":"EQP_MODEL","right":"EQP_MODEL"},{"left":"RECIPE_ID","right":"RECIPE_ID"},{"left":"OPER_NAME","right":"OPER_NAME"}],"multi_match_policy":"error","null_key_policy":"never_match","op":"join","suffix_policy":"forbid"},"recipe_id":"equipment.assignment_uph","required_slots":["equipment","uph"]},"hold.oldest_current_history":{"aliases":["HOLD 시간이 가장 오래된 LOT","오래된 HOLD 이력"],"datasets":["hold_history"],"default_operation_template":{"steps":[{"group_by":["LOT_ID"],"metrics":[{"as":"CURRENT_HOLD_STARTED_AT","field":"HOLD_EVENT_AT","function":"max"}],"op":"aggregate"},{"formula_ref":"metric:HOLD_DURATION_HOURS","op":"derive","output_field":"HOLD_DURATION_HOURS"},{"include_ties":true,"mode":"top","n":1,"op":"rank","rank_by":[{"direction":"desc","field":"HOLD_DURATION_HOURS"}],"scope":"global","tie_break_by":[{"direction":"asc","field":"LOT_ID"}]},{"cardinality":"many_to_one","how":"inner","keys":[{"left":"LOT_ID","right":"LOT_ID"}],"multi_match_policy":"error","null_key_policy":"never_match","op":"join","suffix_policy":"forbid"},{"history_order":[{"direction":"desc","field":"HOLD_EVENT_AT"},{"direction":"asc","field":"LOT_ID"}],"op":"detail"}]},"derived_metrics":["HOLD_DURATION_HOURS"],"recipe_id":"hold.oldest_current_history","required_fields":["LOT_ID","HOLD_EVENT_AT"],"required_slots":["previous_current_hold_result","reference_instant"]},"join.operation.production_wip":{"aliases":["생산량과 재공수량","생산 WIP 비교"],"datasets":["production","production_today","wip","wip_today"],"default_operation_template":{"cardinality":"one_to_one_after_aggregate","empty_side_policy":"preserve_other_side_with_declared_null_metrics","how":"outer","keys":[{"left":"TECH","right":"TECH"},{"left":"DEN","right":"DEN"},{"left":"MODE","right":"MODE"},{"left":"PKG_TYPE1","right":"PKG_TYPE1"},{"left":"PKG_TYPE2","right":"PKG_TYPE2"},{"left":"LEAD","right":"LEAD"},{"left":"MCP_NO","right":"MCP_NO"}],"multi_match_policy":"error","null_key_policy":"blank_equals_blank","op":"join","suffix_policy":"forbid"},"recipe_id":"join.operation.production_wip","required_slots":["production_metric","wip_metric","grain"]},"ordered.process.range":{"aliases":["공정 구간","공정 범위","OPER_SEQ 범위"],"default_operation_template":{"field":"OPER_SEQ","filter_order":"before_general_filters","inclusive":"both","op":"ordered_range"},"recipe_id":"ordered.process.range","required_fields":["OPER_NAME","OPER_SEQ"],"required_slots":["range_start","range_end","dataset"]},"presence.left_positive_right_zero":{"aliases":["A는 있으나 B는 없음","실적 있음 재공 없음","존재 미존재"],"default_operation_template":{"keys":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO"],"left_metric_ref":"$left_metric.id","materialize_right_zero":true,"op":"presence_filter","right_metric_ref":"$right_metric.id"},"recipe_id":"presence.left_positive_right_zero","required_slots":["left_metric","right_metric","grain"]},"product.standard":{"aliases":["제품별","제품 기준","제품 집계"],"default_operation_template":{"group_by":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO"],"metrics":[{"as_ref":"$metric.id","field_ref":"$metric.field","function_ref":"$metric.rollup"}],"op":"aggregate"},"grain":{"entity_id":"product","grain_id":"product.standard","keys":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO"],"null_match_policy":"blank_equals_blank"},"recipe_id":"product.standard","required_slots":["dataset","metric"]},"rank.bottom_n":{"aliases":["하위 N개","가장 적은","BOTTOM N"],"default_operation_template":{"include_ties":false,"mode":"bottom","op":"rank","scope":"global","stable_tie_break":"declared_keys"},"recipe_id":"rank.bottom_n","required_slots":["metric","n"]},"rank.top_n":{"aliases":["상위 N개","가장 많은","TOP N"],"default_operation_template":{"include_ties":false,"mode":"top","op":"rank","scope":"global","stable_tie_break":"declared_keys"},"recipe_id":"rank.top_n","required_slots":["metric","n"]}}}')


EMBEDDED_SCHEMAS = json.loads('{"analysis-route.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/analysis-route.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"allOf":[{"if":{"properties":{"route":{"const":"deterministic"}},"required":["route"]},"then":{"properties":{"ambiguity_sets":{"maxItems":0},"selected_candidate_ids":{"minItems":1},"unresolved_slots":{"maxItems":0}}}},{"if":{"properties":{"route":{"const":"unsupported"}},"required":["route"]},"then":{"properties":{"reason_code":{"const":"unsupported_registry_gap"}}}}],"properties":{"ambiguity_sets":{"items":{"items":{"minLength":1,"type":"string"},"minItems":2,"type":"array","uniqueItems":true},"maxItems":32,"type":"array"},"contract_version":{"const":"analysis.route.v1","type":"string"},"eligibility_proof_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"reason_code":{"enum":["unique_complete_selection","semantic_choice_required","unsupported_registry_gap","ambiguous_candidate_selection","forced_equivalence_probe"],"type":"string"},"required_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"resolved_candidate_bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"route":{"enum":["deterministic","intent_llm","unsupported"],"type":"string"},"route_policy_version":{"const":"route-policy.v1","type":"string"},"selected_candidate_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"unresolved_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["contract_version","route","reason_code","resolved_candidate_bundle_sha256","selected_candidate_ids","required_slots","unresolved_slots","ambiguity_sets","route_policy_version","eligibility_proof_sha256"],"title":"analysis.route.v1","type":"object"},"resolved-candidate-bundle.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/resolved-candidate-bundle.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"catalog_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"resolved.candidate.bundle.v1","type":"string"},"dataset_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"entity_group_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"field_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"function_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"grain_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"intent_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":32,"type":"array"},"metric_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"prompt_cards":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":32,"type":"array"},"recipe_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"relation_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"request_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"route_decision":{"$ref":"#/$defs/jsonObject"},"route_evidence":{"$ref":"#/$defs/jsonObject"}},"required":["contract_version","request_id","catalog_sha256","dataset_candidates","field_candidates","metric_candidates","entity_group_candidates","grain_candidates","relation_candidates","recipe_candidates","function_candidates","intent_candidates","prompt_cards","bundle_sha256","route_decision","route_evidence"],"title":"resolved.candidate.bundle.v1","type":"object"}}')



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
from lfx.io import DataInput, Output
from lfx.schema.data import Data


class CandidateRouteGate(Component):
    display_name = "03 의도 후보 및 분기 판정"
    description = "질문과 등록 메타데이터를 바탕으로 허용된 의도 후보와 LLM 호출 여부를 결정론적으로 계산합니다."
    icon = "route"
    metadata = {"logical_stage": "candidate_route"}
    inputs = [
        DataInput(name="request_context", display_name="검증된 요청 컨텍스트", required=True, info="질문 원문, 세션 상태, 기준 시각이 검증된 요청 정보입니다."),
        DataInput(name="domain_bundle", display_name="도메인 실행 번들", required=True, info="후보 생성에 사용할 승인된 데이터셋·필드·지표 정의입니다."),
    ]
    outputs = [Output(name="selection_context", display_name="의도 후보 및 분기 컨텍스트", method="select_route", types=["Data"])]

    def select_route(self) -> Data:
        current = _payload(getattr(self, "request_context", None))
        try:
            current = _require_context(current, "candidate_route")
            if not current.get("ok"):
                return Data(data=current)
            domain = _require_context(getattr(self, "domain_bundle", None), "candidate_route")
            if not domain.get("ok"):
                merged = deepcopy(current)
                merged.update({"ok": False, "stage": domain.get("stage"), "error": domain.get("error")})
                return Data(data=merged)
            catalog = (domain.get("domain_bundle") or {}).get("runtime_catalog")
            request = current["request"]
            planner_profile = _planner_profile(catalog)
            if planner_profile == "generic_v2":
                bundle = build_generic_v2_candidate_bundle(
                    request,
                    catalog,
                    prior_semantics=current.get("prior_semantics") or {},
                    prior_result=current.get("prior_result") or {},
                )
                validate_generic_v2_candidate_bundle(bundle, catalog=catalog)
                validate_contract(bundle, "resolved-candidate-bundle.schema.json", stage="candidate_bundle_contract")
                candidate_lane = "generic_v2"
            else:
                planning_catalog = EMBEDDED_RUNTIME_CATALOG if planner_profile == "legacy_v1_compat" else catalog
                bundle = build_candidate_bundle(request, planning_catalog, prior_semantics=current.get("prior_semantics") or {}, prior_result=current.get("prior_result") or {})
                candidate_lane = planner_profile
            route = bundle.get("route_decision") if isinstance(bundle.get("route_decision"), dict) else {}
            validate_contract(route, "analysis-route.schema.json", stage="route_contract")
            current.update(
                {
                    "stage": "candidate_route",
                    "candidate_bundle": bundle,
                    "candidate_lane": candidate_lane,
                    "domain_identity": {key: (domain.get("domain_bundle") or {}).get(key) for key in ("domain_id", "environment", "revision", "catalog_sha256", "package_sha256", "bundle_sha256")},
                    "domain_prompt_extensions": {
                        "intent": str(((catalog.get("prompt_extensions") or {}).get("intent") or "")).encode("utf-8")[:8192].decode("utf-8", errors="ignore"),
                        "answer": str(((catalog.get("prompt_extensions") or {}).get("answer") or "")).encode("utf-8")[:8192].decode("utf-8", errors="ignore"),
                    },
                    "route_telemetry": {
                        "route": route.get("route"),
                        "reason_code": route.get("reason_code"),
                        "intent_llm_calls": 0,
                        "fallback_used": False,
                        "planner_profile": planner_profile,
                        "eligibility_proof_sha256": route.get("eligibility_proof_sha256"),
                    },
                }
            )
        except Exception as exc:
            current = _pipeline_error(current, exc, "candidate_route")
        return Data(data=current)
