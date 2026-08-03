# -*- coding: utf-8 -*-
"""GENERATED standalone component: AuthoringMessagePresentation.

Regenerate with tools/build_standalone_components.py.  Do not hand edit.
"""
from __future__ import annotations

import json

EMBEDDED_SOURCE_MANIFEST = json.loads('{"catalog_contract_version":"metadata.runtime.catalog.v1","catalog_declared_sha256":"1f8b6c1522b96425a6a46a3e4dfcf4c5b7c338c6bc0af3c2a0878806ea4a7f8e","catalog_file_sha256":"0b035cefd556b3c37b166e73270dee3e7070a2adf2dd56750b8e1015516bfcce","contract_version":"standalone.source.manifest.v1","reference_sources":{"contracts/schemas/active-domain-pointer.schema.json":"8ff3e114e106d0bc08c83e61947ac967c28cd5390cd0539cb1efdc64b82f9a61","contracts/schemas/analysis-plan.schema.json":"15dbb187f458d03ad4d55063eef898b862529dc68e9f64840d08ab20df9cfb76","contracts/schemas/analysis-result.schema.json":"06e92c0892ff5b209783332f33e4d4ed1855612470b088390e4501591f68065b","contracts/schemas/analysis-route.schema.json":"aadd7504e7f75329b8b6a50634261e073450e6d19d8e14d4a44196c0000e0c04","contracts/schemas/answer-facts.schema.json":"26c573be25f4fade355a37f2ab231f3e0aa8ac83445ee58020a99388648809ed","contracts/schemas/answer-sections.schema.json":"4c1d645c9927879e6a9e877def326ff045b5a01edaf48a566b935bc4734882ab","contracts/schemas/approval-event.schema.json":"4aa6b10eeb875538d00d6de564bdbe24eb093e8727ed57515cbadba63f13d7a9","contracts/schemas/config-registry.schema.json":"2f90dfb2b99e17faa9afecaf1f32295f6d713067aeca66c7dc1544c5713598e9","contracts/schemas/display-options.schema.json":"099ef7c371a2ac015cf7b59ae873d2ff749cdad7fa738bbcccc9b4838ea45866","contracts/schemas/domain-package.schema.json":"f39f433985180636bb3b6dfe054cfb8e63998acbe0112f7082a8233b619517f7","contracts/schemas/download-item.schema.json":"91efd43bf2db00bf5e85071fa2992679c3b2dc050251a5c82e839dcd7f5d4086","contracts/schemas/error-registry.schema.json":"f67a1ab5ef2568626d406cb9feb38acfbb6fc593fa04f3da063f8293da653b64","contracts/schemas/error.schema.json":"1a0c89cc1898a894b0490a59f286c68520c0f74be0811f6c06c4aa3e50fe5602","contracts/schemas/evidence-manifest.schema.json":"2805ed7cce742e96b5e10902b096fbec91e40a8aca7fde7bfe95c1d12a9668bb","contracts/schemas/executable-blueprint.schema.json":"e55dbe8faa2f1f2eb933b1548b2b1c37886a0911ceb4e70838427bac2327f14a","contracts/schemas/executed-result.schema.json":"eaba5818e5fb30e2a572f5a81488d9ba34032adcf3af55dfbb0d4287afc7e435","contracts/schemas/flow-inventory.schema.json":"cdce69d64a9df37a88e139a0fd0900d38d9475d2a8f13ff9a9b5c1bf0777b672","contracts/schemas/gaia-metadata.schema.json":"86d0a11a06a97d573b550a427d26abe9db6e897d3c46681f02e2427735e9f093","contracts/schemas/metadata-annotation-proposal.schema.json":"f0b227cc42a528d6e0b95f1c8c4a1bf6bbb6871d17d32c108d65b47d2b0ddc7f","contracts/schemas/metadata-authoring-draft.schema.json":"035c081be6a0fa719b3dcd589d9090071342b695fa61f80f6781441a4b14aee2","contracts/schemas/metadata-authoring-proposal.schema.json":"8ee3fc86d8f596c554443c16ad619822e63315ed8f2bfd06311987fc63322edd","contracts/schemas/metadata-authoring-response.schema.json":"da776b8a156d007c5bd95e86ad10cfb5a8ac7f06c2cae0c52aeb96b6a36415f6","contracts/schemas/metadata-bootstrap-dataset-ir.schema.json":"351260f7ed418b35f4ca1e5012a353b1d8f820ea21dfc8880483c193880af3b6","contracts/schemas/metadata-bootstrap-main-filter-ir.schema.json":"41c849c88b803d53af9c02c3d50127c47e8ee38e46d7b0a1ad0d09c3638e48fa","contracts/schemas/metadata-bundle.schema.json":"985ffe44974cf14d6c52a8188d54c3b209c00478e83888f00c359cd056d5dc81","contracts/schemas/metadata-envelope.schema.json":"9abca177e22b570f2158dace05256f671c0acbd054705dfe4f34611fbdae2048","contracts/schemas/model-profile.schema.json":"14345c16f629fc03a3de2cdd2fe469bef1fdc82cd2f93954ce1f4204ba82f356","contracts/schemas/operator-registry.schema.json":"acd003c6db66b470a2653fc8a97caaf3856c9d4cfd934bc0f27ef609787c2746","contracts/schemas/pending-metadata-write.schema.json":"af7a0593fafbdcea16f1212ba92484525626e43f2a25d91f9c310a80f5b37a4d","contracts/schemas/query-registry.schema.json":"8422a44035eb2a06381166d69a185036c698f581b17741a8c4686fbeea109040","contracts/schemas/registered-call.schema.json":"41c4152f45577f05c925d5d782a48f8db45f67f8e48aac8805b822269516bd58","contracts/schemas/registered-function-card.schema.json":"bc9ca8b01c90d2d11737f1a70586e9227510b67fdab26c8ae605d9e830170dfd","contracts/schemas/request-capsule.schema.json":"675e661653098288d6cc9e6e9b3599ed3bf3e05d6d592ac66d9ed46b9fd2afaf","contracts/schemas/resolved-candidate-bundle.schema.json":"a24b7d2fc3798f1dd69e1af94a7071eae8fb56d93a4191258953fd63b4211568","contracts/schemas/response.schema.json":"40c1e43f2228c04bb9ea652f1107a7ac202405c3321bc2c6af8dbc543b2e7b06","contracts/schemas/retrieval-job-bundle.schema.json":"e73cd6e6c50bb24b528111c36c410af3afe2fe3ff28d3d906cfe023263a12105","contracts/schemas/runtime-catalog-v2.schema.json":"3f7f6c5154c9e7922dd65490e9166ba0038c6a242258ec30d409d8a553948fed","contracts/schemas/semantic-intent-selection.schema.json":"a70c99e36060531fac9730c02f706ffa8d108b872c5abe0e2d05cafa459e6a75","contracts/schemas/semantic-intent.schema.json":"a743b7e26168dda04a7f46205fed67987a587cf3cce939cf57b228b099bfad53","contracts/schemas/source-bundle.schema.json":"a5330ef1b104df5dd0f19385b5e7994ee5469feffa110ee84087b7992258ea92","contracts/schemas/source-result.schema.json":"f342dcf0f948f7f99899335d83f302f2aaa38b05bb246eb06f9c1da0161f516c","contracts/schemas/trace.schema.json":"3f7cb2dd4e88b5f9f09695347ce42d8b98d5c4534d8fab41cca8ea1c9e3d484e","contracts/schemas/turn-state.schema.json":"688ad4f5ac1b133e60e3a2ef2bef56d0b18c87a41d2c6c236264285aeba32280","contracts/schemas/unsupported-telemetry.schema.json":"8c3675797be935d6fd52db2883d433d464df2fdecc5e0d52e795a5fa1e6c8439","contracts/schemas/validation-case.schema.json":"23304f969ca614324f7a74b52edc72c4e6753e76c476a77fc8db68f089941682","langflow_components/shared/01_prompt_bundle_composer.py":"2a8e80103205136221c87901a1bdeeb7df62f954c9f3f9c407a77a2e41a6b77b","langflow_components/shared/02_conditional_llm_invoker.py":"2b7ee35fb4276b932285a62860b1114b29797698232bfc9523597c103c6ea3d9","metadata/domain_packs/manufacturing/approved_source_registry.json":"241969f12d76c0d616296894dc51ba95553ebf48d5edb15e20480c4beec64587","reference_runtime/authoring_blueprint.py":"9fc416a04e0da317586ad8abf9831bf650746a7f1907ad62fcaef4012327fe71","reference_runtime/authoring_source_manifest.py":"311bd68482e163a781bf11aa449587879f659fa9c36f7564129ecea44b88170c","reference_runtime/canonical.py":"338b8b013b9311f94d9b5ff7a3d5902576e9dfb88b40d72d37436025806c2d1d","reference_runtime/contracts.py":"5d16082db0bf437e537a24352834548e48e157a4c740659e9c9f1a0e46960d6e","reference_runtime/domain_authoring_patches.py":"4c78c72bc2412cbe78e74372b7c5af658ada8de1b8058b228f02d2b68b41c445","reference_runtime/domain_packages.py":"ae08de3501c92be10bd8f983fa710cc8e4cec6a40dd8051140ab754c9caac04a","reference_runtime/dummy_data.py":"c02824f9ddba81496d99a4b58bda8e6bedf0ce464d47abca682071ab24cae57d","reference_runtime/engine.py":"62df5f1a06c0a2765085826bec3e73f99f02da470850d180f2d7a53078c67606","reference_runtime/generic_v2_candidates.py":"95f5821b05d7d70f70ebd0339a316bcc1367b5499553319b8d8995df251a4c56","reference_runtime/generic_v2_planner.py":"142665c8050c9302830cedf45928a25b73cd34e80bec66de9ba77003209176d3","reference_runtime/metadata_collections.py":"c10d21cab4fdb54e95f1e23b262842be51d1b74f85aedda7b99a7d48f1a84857","reference_runtime/metadata_compiler.py":"99544e6094883b4241d010af2bec5d67e6205d34634ad46d6e2ee173107336e3","reference_runtime/plan_compiler.py":"e3782e6e86e41968a7bab1be4056ac2e9459c28188efa92f6532d2898d12abee","reference_runtime/presenter.py":"fee16b71dfaf07be0d27fee14f47aa753ea71350165185071552ff0f30a31101","reference_runtime/registered_functions.py":"d2125d6902ca246b2239e8569959ac37f45847bf17dafaf93b857e088c750e42","reference_runtime/request_literals.py":"00493f9e342ab3065215805ae32f3068cb594209434bf280f2bb4f23c4be62ff","reference_runtime/source_contracts.py":"c43d8865ff045f4c26c5194262620a50961be5b56552c5cc6e7d580b2c11d7b0","reference_runtime/state_contracts.py":"5a03fff6684850361904add4e4d15ea578617d1fce20564119bbac175fb334ae","reference_runtime/typed_executor.py":"0c1fc3bbb055cd32d1da3446afab0aca5351e844536624ae9ab953c78c5dfe3b"}}')


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


import json
from copy import deepcopy
from typing import Any
from urllib.parse import quote
DEFAULT_DISPLAY_OPTIONS = {'profile': 'standard', 'include_diagnostics': False, 'show_result_table': True, 'table_preview_limit': 10, 'show_analysis_evidence': False, 'show_download_links': True, 'show_notices': True, 'show_applied_criteria': True, 'show_next_questions': False, 'show_intent_analysis': False, 'show_data_retrieval': False, 'show_pandas_code': False, 'show_execution_plan': False}

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
    if result['include_diagnostics']:
        result['show_intent_analysis'] = True
        result['show_data_retrieval'] = True
        result['show_pandas_code'] = True
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

def _frame_expression(reference: Any) -> str:
    value = str(reference or '')
    if value.startswith('source:'):
        return f"source_frames[{value.split(':', 1)[1]!r}]"
    return f'steps[{value!r}]'

def _filter_expression(node: Any, frame_name: str='df') -> str:
    if not isinstance(node, dict):
        return 'pd.Series(False, index=df.index)'
    combinator = str(node.get('op') or '').lower()
    if combinator in {'all', 'any'}:
        clauses = [_filter_expression(item, frame_name) for item in node.get('clauses', [])]
        if not clauses:
            return 'pd.Series(True, index=df.index)'
        joiner = ' & ' if combinator == 'all' else ' | '
        return '(' + joiner.join((f'({item})' for item in clauses)) + ')'
    field = str(node.get('field') or '')
    operator = str(node.get('operator') or 'eq').lower()
    value = repr(node.get('value'))
    series = f'{frame_name}[{field!r}]'
    comparisons = {'eq': '==', 'ne': '!=', 'gt': '>', 'gte': '>=', 'lt': '<', 'lte': '<='}
    if operator in comparisons:
        return f'{series} {comparisons[operator]} {value}'
    if operator in {'in', 'not_in'}:
        expression = f'{series}.isin({value})'
        return f'~({expression})' if operator == 'not_in' else expression
    if operator in {'contains', 'starts_with', 'ends_with'}:
        method = {'contains': 'contains', 'starts_with': 'startswith', 'ends_with': 'endswith'}[operator]
        return f"{series}.astype('string').str.{method}({value}, na=False)"
    if operator == 'is_null':
        return f'{series}.isna()'
    if operator == 'not_null':
        return f'{series}.notna()'
    if operator == 'is_not_blank':
        return f"{series}.notna() & {series}.astype('string').str.strip().ne('')"
    return f'typed_filter_mask({frame_name}, {repr(node)})'

def pandas_equivalent_code(operations: Any) -> str:
    """Render inspectable pandas-equivalent code from the executed Typed IR.

    This is intentionally a presentation artifact. The TypedExecutor remains
    the only execution authority, so displaying code cannot change results.
    """
    values = operations if isinstance(operations, list) else []
    lines = ['# 표시용 Pandas 등가 코드입니다.', '# 실제 계산은 검증된 Typed Execution IR 실행기가 수행합니다.', 'import pandas as pd', 'steps = {}']
    for index, raw in enumerate(values, start=1):
        if not isinstance(raw, dict):
            continue
        operation = deepcopy(raw)
        operation_id = str(operation.get('id') or f'step_{index}')
        operator = str(operation.get('op') or '')
        source = _frame_expression(operation.get('input'))
        target = f'steps[{operation_id!r}]'
        lines.append('')
        lines.append(f'# {index}. {operator} ({operation_id})')
        if operator == 'filter':
            lines.append(f'df = {source}')
            lines.append(f"{target} = df.loc[{_filter_expression(operation.get('where') or {})}].reset_index(drop=True)")
        elif operator in {'project', 'detail'}:
            lines.append(f"{target} = {source}[{list(operation.get('fields') or [])!r}].copy()")
        elif operator == 'ordered_range':
            field = str(operation.get('field') or 'OPER_SEQ')
            lines.append(f'df = {source}')
            lines.append(f"numeric = pd.to_numeric(df[{field!r}], errors='coerce')")
            lines.append(f"{target} = df.loc[numeric.between({operation.get('start')!r}, {operation.get('end')!r}, inclusive='both')].reset_index(drop=True)")
        elif operator == 'aggregate':
            groups = list(operation.get('group_by') or [])
            metrics = operation.get('metrics') if isinstance(operation.get('metrics'), list) else []
            named = {str(item.get('as') or item.get('field') or item.get('function')): (str(item.get('field') or ''), str(item.get('function') or 'count')) for item in metrics if isinstance(item, dict)}
            if groups:
                lines.append(f'{target} = {source}.groupby({groups!r}, dropna=False, sort=False).agg(**{named!r}).reset_index()')
            else:
                lines.append(f'{target} = pd.DataFrame([typed_aggregate({source}, {metrics!r})])')
        elif operator == 'sort':
            keys = operation.get('keys') if isinstance(operation.get('keys'), list) else []
            fields = [str(item.get('field') or '') for item in keys if isinstance(item, dict)]
            ascending = [str(item.get('direction') or 'asc').lower() != 'desc' for item in keys if isinstance(item, dict)]
            lines.append(f"{target} = {source}.sort_values({fields!r}, ascending={ascending!r}, kind='mergesort').reset_index(drop=True)")
        elif operator == 'rank':
            keys = list(operation.get('rank_by') or []) + list(operation.get('tie_break_by') or [])
            fields = [str(item.get('field') or '') for item in keys if isinstance(item, dict)]
            ascending = [str(item.get('direction') or 'asc').lower() != 'desc' for item in keys if isinstance(item, dict)]
            limit = int(operation.get('limit') or 1)
            partitions = list(operation.get('partition_by') or [])
            lines.append(f"ranked = {source}.sort_values({fields!r}, ascending={ascending!r}, kind='mergesort')")
            if partitions:
                lines.append(f'{target} = ranked.groupby({partitions!r}, dropna=False, sort=False).head({limit}).reset_index(drop=True)')
            else:
                lines.append(f'{target} = ranked.head({limit}).reset_index(drop=True)')
        elif operator == 'join':
            left = _frame_expression(operation.get('left') or operation.get('input'))
            right = _frame_expression(operation.get('right'))
            mappings = operation.get('key_mappings') if isinstance(operation.get('key_mappings'), list) else []
            left_on = [str(item.get('left') or '') for item in mappings if isinstance(item, dict)]
            right_on = [str(item.get('right') or '') for item in mappings if isinstance(item, dict)]
            lines.append(f"{target} = {left}.merge({right}, how={str(operation.get('how') or 'inner')!r}, left_on={left_on!r}, right_on={right_on!r})")
        elif operator == 'dedupe':
            lines.append(f"{target} = {source}.drop_duplicates(subset={list(operation.get('fields') or [])!r}, keep={str(operation.get('keep') or 'first')!r}).reset_index(drop=True)")
        else:
            lines.append(f'{target} = typed_ir_step({source}, {operation!r})')
    if values:
        last_id = str(values[-1].get('id') or f'step_{len(values)}') if isinstance(values[-1], dict) else f'step_{len(values)}'
        lines.extend(['', f'result_df = steps[{last_id!r}]'])
    return '\n'.join(lines)

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
    response = deepcopy(material)
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
    material = {'contract_version': 'response.v1', 'response_type': 'data_analysis', 'status': status, 'stage_status': {'overall': status, 'intent': 'skipped' if route_telemetry.get('intent_llm_calls') == 0 else 'ok', 'retrieval': 'ok', 'analysis': status}, 'message': headline, 'data_mode': str(data_mode or 'dummy'), 'analysis_mode': 'typed_ir', 'answer_sections': answer_sections, 'request': {'request_id': request.get('request_id'), 'question': request.get('question'), 'session_id': request.get('session_id'), 'reference_instant': request.get('reference_instant'), 'timezone': request.get('timezone')}, 'intent_plan': {'intent_sha256': intent.get('intent_sha256'), 'intent_candidate_id': intent.get('intent_candidate_id'), 'plan_id': plan.get('plan_id'), 'plan_fingerprint': plan.get('plan_fingerprint'), 'semantic_intent': intent.get('semantics', {})}, 'analysis': {'status': status, 'result_sha256': result.get('result_sha256'), 'operation_trace': result.get('operation_trace', []), 'execution_ir': plan.get('operations', []), 'pandas_code': pandas_equivalent_code(plan.get('operations', [])), 'lineage': result.get('lineage', {})}, 'clarification': None, 'data': {'columns': columns, 'rows': rows[:50], 'row_count': row_count}, 'data_refs': refs, 'state': {'state_version': state.get('state_version'), 'executed_result_ref': state.get('executed_result_ref'), 'expires_at': state.get('expires_at')} if persistent else None, 'trace': {'trace_id': trace_id, 'route': deepcopy(route_telemetry), 'retrieval': deepcopy(source_diagnostics), 'usage': usage, 'commit_order': list(events or [])}}
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
    response = deepcopy(response) if isinstance(response, dict) else {}
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
    if display['show_pandas_code']:
        pandas_code = str(response.get('analysis', {}).get('pandas_code') or '').strip()
        if pandas_code:
            sections.append('### Pandas 등가 코드 (표시용)\n```python\n' + pandas_code + '\n```')
    if display['show_execution_plan']:
        sections.append('### 실행 계획 진단\n```json\n' + json.dumps(response.get('analysis', {}).get('execution_ir', []), ensure_ascii=False, indent=2) + '\n```')
    return '\n\n'.join((section for section in sections if section))

def api_output(response: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(response) if isinstance(response, dict) else {}

def gaia_output(response: dict[str, Any]) -> dict[str, Any]:
    canonical = deepcopy(response) if isinstance(response, dict) else {}
    sections = canonical.get('answer_sections') if isinstance(canonical.get('answer_sections'), dict) else {}
    trace = canonical.get('trace') if isinstance(canonical.get('trace'), dict) else {}
    urls = [{'title': str(item.get('label') or '다운로드'), 'url': str(item.get('url') or '')} for item in sections.get('downloads', []) if item.get('url')]
    metadata = {'contract_version': 'gaia.metadata.v1', 'docs': [], 'images': [], 'knowhows': [], 'followup_questions': [deepcopy(item) for item in sections.get('next_questions', [])[:3]], 'urls': urls, 'trace_id': str(trace.get('trace_id') or ''), 'usage': deepcopy(trace.get('usage', {}))}
    validate_contract(metadata, 'gaia-metadata.schema.json', stage='gaia_output')
    return {'answer': str(canonical.get('message') or ''), 'metadata': metadata}


EMBEDDED_SCHEMAS = json.loads('{"metadata-authoring-response.schema.json":{"$defs":{"clarificationPayload":{"additionalProperties":false,"properties":{"contract_version":{"const":"metadata.authoring.clarification.v1","type":"string"},"missing_fields":{"items":{"maxLength":128,"minLength":1,"type":"string"},"maxItems":32,"type":"array","uniqueItems":true},"proposal_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"questions":{"items":{"maxLength":400,"minLength":1,"type":"string"},"maxItems":3,"minItems":1,"type":"array","uniqueItems":true},"source_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"}},"required":["contract_version","questions","missing_fields","source_sha256","proposal_sha256"],"type":"object"},"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/metadata-authoring-response.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"allOf":[{"if":{"properties":{"status":{"const":"error"}},"required":["status"]},"then":{"required":["error"]}},{"if":{"properties":{"status":{"const":"ok"}},"required":["status"]},"then":{"required":["candidate_id","candidate_sha256"]}},{"else":{"not":{"required":["clarification"]}},"if":{"properties":{"status":{"const":"needs_clarification"}},"required":["status"]},"then":{"not":{"anyOf":[{"required":["candidate_id"]},{"required":["candidate_sha256"]},{"required":["package_sha256"]},{"required":["bundle_sha256"]},{"required":["catalog_sha256"]},{"required":["revision"]},{"required":["persisted"]},{"required":["diff"]},{"required":["unchanged_section_checks"]},{"required":["validation"]},{"required":["expires_at"]},{"required":["idempotent_replay"]},{"required":["error"]}]},"required":["clarification"]}},{"if":{"properties":{"stage":{"const":"prepared"}},"required":["stage"]},"then":{"required":["persisted","diff","validation","expires_at"]}},{"if":{"properties":{"stage":{"const":"committed"}},"required":["stage"]},"then":{"required":["revision","idempotent_replay"]}}],"properties":{"authoring_kind":{"enum":["domain","dataset","main_filter","domain_policy"],"type":"string"},"bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"candidate_id":{"pattern":"^candidate:[0-9a-f]{64}$","type":"string"},"candidate_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"catalog_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"clarification":{"$ref":"#/$defs/clarificationPayload"},"contract_version":{"const":"metadata.authoring.response.v1","type":"string"},"diff":{"$ref":"#/$defs/jsonObject"},"domain_id":{"pattern":"^[a-z][a-z0-9_-]{1,63}$","type":"string"},"environment":{"pattern":"^[a-z][a-z0-9_-]{1,31}$","type":"string"},"error":{"$ref":"#/$defs/jsonObject"},"expires_at":{"format":"date-time","type":"string"},"idempotent_replay":{"type":"boolean"},"llm_usage":{"additionalProperties":false,"properties":{"annotation_llm_calls":{"maximum":1,"minimum":0,"type":"integer"},"draft_llm_calls":{"maximum":3,"minimum":0,"type":"integer"},"repair_llm_calls":{"const":0,"type":"integer"}},"required":["draft_llm_calls","repair_llm_calls"],"type":"object"},"metadata_contract_mode":{"const":"domain_package_v2","type":"string"},"package_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"persisted":{"type":"boolean"},"response_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"response_type":{"const":"metadata_authoring","type":"string"},"revision":{"minimum":0,"type":"integer"},"stage":{"maxLength":128,"minLength":1,"type":"string"},"status":{"enum":["ok","error","needs_clarification"],"type":"string"},"unchanged_section_checks":{"$ref":"#/$defs/jsonObject"},"validation":{"$ref":"#/$defs/jsonObject"}},"required":["contract_version","response_type","status","stage","authoring_kind","metadata_contract_mode","domain_id","environment","llm_usage","response_sha256"],"title":"metadata.authoring.response.v1","type":"object"}}')



from copy import deepcopy

from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema.message import Message


class AuthoringMessagePresentation(Component):
    display_name = "메타데이터 등록 메시지 구성"
    description = "저장·검증·추가 확인 결과를 짧은 한글 메시지로 표시하고 canonical response를 data에 보존합니다."
    icon = "file-check-2"

    inputs = [DataInput(name="response", display_name="메타데이터 등록 응답", required=True, info="저장 완료, 검증 완료, 추가 확인 필요, 오류 중 하나의 표준 등록 응답입니다.")]
    outputs = [Output(name="message", display_name="등록 결과 채팅 메시지", method="build_message", types=["Message"])]

    def build_message(self) -> Message:
        raw = getattr(getattr(self, "response", None), "data", getattr(self, "response", None))
        response = deepcopy(validate_authoring_response_hash(raw)) if isinstance(raw, dict) else {}
        if response.get("status") == "ok" and response.get("stage") == "validated":
            text = "### 메타데이터 검증 완료\n\n" + f"- Candidate: `{response.get('candidate_id', '')}`\n- Revision: {response.get('revision', '')}\n- MongoDB 저장: 안 함"
        elif response.get("status") == "ok":
            text = "### 메타데이터 저장 완료\n\n" + f"- Candidate: `{response.get('candidate_id', '')}`\n- Revision: {response.get('revision', '')}\n- 저장 구조: 도메인·테이블 카탈로그·메인필터"
        elif response.get("status") == "needs_clarification":
            clarification = response.get("clarification") if isinstance(response.get("clarification"), dict) else {}
            questions = [str(item) for item in (clarification.get("questions") or [])[:3]]
            text = "### 메타데이터 등록 전 확인이 필요합니다\n\n" + "\n".join(
                f"{index}. {question}" for index, question in enumerate(questions, 1)
            )
        else:
            error = response.get("error") if isinstance(response.get("error"), dict) else {}
            text = "### 메타데이터 등록 실패\n\n" + f"- Code: `{error.get('code', 'metadata_authoring_failed')}`\n- Message: {error.get('message', '')}"
        message = Message(
            text=text,
            sender="Machine",
            sender_name="Metadata Authoring",
            session_metadata={
                "contract_version": "metadata.authoring.message-link.v1",
                "response_sha256": str(response.get("response_sha256") or ""),
            },
        )
        message.data = {"response": response}
        return message
