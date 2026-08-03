# -*- coding: utf-8 -*-
"""GENERATED standalone component: DomainBundleLoader.

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


import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping
AUTHORING_DRAFT_VERSION = 'metadata.authoring.draft.v1'
DOMAIN_PACKAGE_VERSION = 'domain.package.v1'
RUNTIME_CATALOG_V2 = 'metadata.runtime.catalog.v2'
ACTIVE_POINTER_VERSION = 'metadata.active-domain-pointer.v1'
DOMAIN_COMPILER_VERSION = 'metadata-domain-compiler.v6.3'
DOMAIN_PACKAGE_COLLECTION = 'agent_v6_metadata_bundles'
ACTIVE_POINTER_COLLECTION = 'agent_v6_metadata_active'
MIGRATION_QUARANTINE_COLLECTION = 'agent_v6_migration_quarantine'
DOMAIN_ID_PATTERN = re.compile('^[a-z][a-z0-9_-]{1,63}$')
ENVIRONMENT_PATTERN = re.compile('^[a-z][a-z0-9_-]{1,31}$')
SHA256_PATTERN = re.compile('^[0-9a-f]{64}$')
ALLOWED_FIELD_ROLES = {'filter', 'group', 'join', 'compare', 'aggregate', 'derive', 'project', 'sort', 'rank', 'metric', 'output'}
ALLOWED_SOURCE_TYPES = {'oracle', 'sql', 'mongodb', 'http', 'datalake', 'goodocs', 'file', 'dummy', 'previous_result'}
ALLOWED_OPERATIONS = {'filter', 'ordered_range', 'product_token_match', 'project', 'derive', 'aggregate', 'compare_fields', 'compare_group_attributes', 'find_duplicate_groups', 'join', 'presence_filter', 'sort', 'rank', 'concat_segments', 'transform_previous_result'}
GENERIC_V2_OPERATIONS = {'filter', 'project', 'aggregate', 'join', 'derive', 'compare_fields', 'sort', 'rank', 'transform_previous_result'}
FILTER_OPERATORS = {'is_null', 'is_not_null', 'is_blank', 'is_not_blank', 'null_or_blank', 'in', 'not_in', 'between', 'contains', 'starts_with', 'ends_with', 'eq', 'ne', 'gt', 'gte', 'lt', 'lte'}
FORMULA_OPERATORS = {'add', 'subtract', 'multiply', 'safe_divide', 'coalesce', 'coalesce_blank', 'abs', 'round', 'min_pair', 'max_pair'}
LEGACY_FORMULA_OPERATORS = FORMULA_OPERATORS | {'datetime_diff_hours'}
FORMULA_ARITY = {'add': 2, 'subtract': 2, 'multiply': 2, 'safe_divide': 2, 'coalesce': 2, 'coalesce_blank': 2, 'abs': 1, 'round': 1, 'min_pair': 2, 'max_pair': 2, 'datetime_diff_hours': 2}
SAFE_DIVIDE_ZERO_POLICIES = {'null', 'zero', 'error'}
FORMULA_RUNTIME_REFS = {'reference_instant'}
NUMERIC_SEMANTIC_TYPES = {'number', 'integer', 'quantity', 'currency', 'rate', 'percent', 'percentage', 'duration', 'hour'}
TEXTUAL_SEMANTIC_TYPES = {'string', 'identifier', 'year_month'}
NUMERIC_ROLLUPS = {'sum', 'mean', 'min', 'max', 'median', 'std', 'var'}
DISTINCT_ROLLUPS = {'count', 'nunique', 'list_unique'}
GENERIC_REQUIRED_SLOTS = {'date_scope', 'rank_direction', 'rank_limit', 'project_fields', 'request_scope', 'analysis_kind', 'metric_refs', 'dimension_refs', 'field_refs', 'dataset_refs', 'relation_refs', 'recipe_refs', 'formula_refs', 'grain_refs', 'entity_group_refs', 'filter_refs', 'thresholds', 'date', 'reference_date', 'reference_instant', 'rank', 'sort', 'followup', 'followup_mode', 'comparison_operator'}
FORBIDDEN_EXECUTABLE_KEYS = {'code', 'python', 'python_code', 'pandas_code', 'script', 'eval', 'exec', 'callable', 'lambda', 'sql', 'endpoint_url'}
QUERY_SOURCE_TYPES = {'oracle', 'sql', 'datalake'}
QUERY_TEMPLATE_KEYS = {'query_template', 'sql_template', 'oracle_sql', 'datalake_sql'}
_QUERY_PLACEHOLDER = re.compile('\\{([A-Za-z][A-Za-z0-9_]*)\\}')
_QUERY_MARKER = re.compile('(?im)^[ \\t]*(?:query_template|sql_template|oracle_sql|datalake_sql)[ \\t]*:[ \\t]*(?:\\n|$)')
_QUERY_BLOCK_END = re.compile('(?im)^[ \\t]*(?:filter_mappings|required_params|required_param_mappings|standard_column_aliases|default_detail_columns|metric_semantics|selection_criteria)[ \\t]*(?:[:=]|(?:은|는)\\b)')
_QUERY_FORBIDDEN_VERB = re.compile('\\b(?:INSERT|UPDATE|DELETE|MERGE|ALTER|DROP|CREATE|TRUNCATE|GRANT|REVOKE|EXECUTE|EXEC|CALL|BEGIN|DECLARE|COMMIT|ROLLBACK)\\b', re.IGNORECASE)
SECRET_KEY_PARTS = {'password', 'passwd', 'token', 'secret', 'api_key', 'apikey', 'authorization', 'credential', 'private_key', 'connection_string', 'mongo_uri'}
ALLOWED_NON_SECRET_TOKEN_KEYS = {'tokens'}
IDENTITY_CONTAINER_KEYS = {'datasets', 'fields', 'metrics', 'entity_groups', 'grains', 'relations', 'orderings', 'predicates', 'recipes', 'aliases'}
SECRET_SCALAR_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (('google_api_key', re.compile('\\bAIza[0-9A-Za-z_-]{20,}\\b')), ('openai_style_key', re.compile('\\bsk-[0-9A-Za-z_-]{16,}\\b')), ('aws_access_key', re.compile('\\b(?:AKIA|ASIA)[0-9A-Z]{16}\\b')), ('private_key', re.compile('-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----', re.I)), ('credentialed_uri', re.compile('\\b[a-z][a-z0-9+.-]*://[^\\s/:@]+:[^\\s/@]+@', re.I)), ('bearer_token', re.compile('\\bBearer\\s+[A-Za-z0-9._~-]{16,}', re.I)), ('jwt', re.compile('\\beyJ[A-Za-z0-9_-]{8,}\\.[A-Za-z0-9_-]{8,}\\.[A-Za-z0-9_-]{8,}\\b')), ('named_secret_assignment', re.compile('\\b(?:password|passwd|pwd|api[_ -]?key|secret|access[_ -]?token)\\s*[:=]\\s*(?!<[^>]+>|\\$\\{[^}]+\\}|\\*{3,}|x{3,}|redacted\\b)[^\\s,;]{6,}', re.I)))

def query_template_parameters(query_template: str) -> list[str]:
    """Return unique ``{NAME}`` placeholders in first-occurrence order."""
    normalized = str(query_template or '').replace('\r\n', '\n').replace('\r', '\n')
    values: list[str] = []
    seen: set[str] = set()
    for match in _QUERY_PLACEHOLDER.finditer(normalized):
        name = match.group(1)
        if name not in seen:
            seen.add(name)
            values.append(name)
    return values

def validate_read_only_query_template(query_template: str) -> str:
    """Validate one executable Oracle/Datalake query without rewriting it.

    Only line-ending normalization and surrounding blank-line removal are
    applied.  Indentation, comments, placeholder spelling and internal
    newlines remain byte-for-byte stable after the CRLF-to-LF normalization.
    """
    normalized = str(query_template or '').replace('\r\n', '\n').replace('\r', '\n').strip(' \t\n')
    if not normalized or len(normalized.encode('utf-8')) > 131072:
        _fail('query_template must contain 1 to 131072 UTF-8 bytes.')
    neutral = re.sub('/\\*.*?\\*/', ' ', normalized, flags=re.DOTALL)
    neutral = re.sub('(?m)--[^\\n]*$', ' ', neutral)
    neutral = re.sub("'(?:''|[^'])*'", "''", neutral)
    executable = neutral.strip()
    if not re.match('(?is)^(?:SELECT|WITH)\\b', executable):
        _fail('query_template must be a read-only SELECT or WITH query.')
    forbidden = _QUERY_FORBIDDEN_VERB.search(executable)
    if forbidden or re.search('\\bFOR\\s+UPDATE\\b', executable, re.IGNORECASE):
        _fail('query_template contains a non-read-only SQL operation.', {'keyword': forbidden.group(0).upper() if forbidden else 'FOR UPDATE'})
    statement_body = executable[:-1] if executable.endswith(';') else executable
    if ';' in statement_body:
        _fail('query_template must contain exactly one SQL statement.')
    braces_removed = _QUERY_PLACEHOLDER.sub('', normalized)
    if '{' in braces_removed or '}' in braces_removed:
        _fail('query_template contains an invalid placeholder. Use {NAME} syntax only.')
    return normalized

def apply_dataset_source_configs_from_text(authoring_payload: Mapping[str, Any], source_text: str, *, require_complete: bool=False) -> tuple[dict[str, Any], dict[str, Any]]:
    """Overlay trusted SQL blocks from operator text onto compiled datasets.

    The LLM is intentionally not trusted to copy or modify SQL.  Dataset
    identity is resolved against the already schema-validated draft and the
    exact query body is taken directly from the operator's natural-language
    source text.
    """
    draft = deepcopy(dict(authoring_payload))
    datasets = draft.get('datasets')
    if not isinstance(datasets, dict):
        _fail('datasets must be an object before query extraction.')
    text = str(source_text or '').replace('\r\n', '\n').replace('\r', '\n')
    markers = list(_QUERY_MARKER.finditer(text))
    applied: dict[str, dict[str, Any]] = {}
    previous_end = 0
    for index, marker in enumerate(markers):
        next_marker_start = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        candidate_end = next_marker_start
        boundary = _QUERY_BLOCK_END.search(text, marker.end(), next_marker_start)
        if boundary:
            candidate_end = boundary.start()
        raw_query = text[marker.end():candidate_end].strip(' \t\n')
        query_template = validate_read_only_query_template(raw_query)
        prefix = text[previous_end:marker.start()]
        dataset_key = ''
        latest_position = -1
        for key in sorted(datasets, key=len, reverse=True):
            explicit = re.compile(f'(?<![A-Za-z0-9_]){re.escape(str(key))}(?![A-Za-z0-9_])[ \\t]*(?:으로|로)[ \\t]*등록', re.IGNORECASE)
            matches = list(explicit.finditer(prefix))
            if matches and matches[-1].start() >= latest_position:
                latest_position = matches[-1].start()
                dataset_key = str(key)
        if not dataset_key:
            latest_position = -1
            for key in sorted(datasets, key=len, reverse=True):
                pattern = re.compile(f'(?<![A-Za-z0-9_]){re.escape(str(key))}(?![A-Za-z0-9_])', re.IGNORECASE)
                matches = list(pattern.finditer(prefix))
                if matches and matches[-1].start() >= latest_position:
                    latest_position = matches[-1].start()
                    dataset_key = str(key)
        if not dataset_key:
            _fail('query_template could not be associated with a registered dataset.', {'query_index': index})
        if dataset_key in applied:
            _fail('A dataset may define only one query_template.', {'dataset_key': dataset_key})
        dataset = datasets[dataset_key]
        source_type = str(dataset.get('source_type') or '').casefold()
        if source_type not in QUERY_SOURCE_TYPES:
            _fail('query_template is only allowed for Oracle, SQL or Datalake datasets.', {'dataset_key': dataset_key, 'source_type': source_type})
        db_matches = list(re.finditer('(?i)(?<![A-Za-z0-9_])db_key(?![A-Za-z0-9_])[ \\t]*(?:[:=]|(?:은|는))[ \\t]*([A-Za-z][A-Za-z0-9_.-]{0,127})', prefix))
        source_config = deepcopy(dict(dataset.get('source_config') or {}))
        source_config['source_type'] = source_type
        if db_matches:
            source_config['db_key'] = db_matches[-1].group(1)
        source_config['query_template'] = query_template
        placeholders = query_template_parameters(query_template)
        source_config['required_params'] = placeholders
        dataset['source_config'] = source_config
        parameters = deepcopy(dict(dataset.get('parameters') or {}))
        for name in placeholders:
            card = deepcopy(dict(parameters.get(name) or {}))
            card.setdefault('type', 'string')
            card['required'] = True
            parameters[name] = card
        dataset['parameters'] = parameters
        applied[dataset_key] = {'db_key': str(source_config.get('db_key') or ''), 'required_params': placeholders, 'query_bytes': len(query_template.encode('utf-8')), 'line_count': query_template.count('\n') + 1}
        previous_end = candidate_end
    missing = sorted((key for key, raw_dataset in datasets.items() if str(raw_dataset.get('source_type') or '').casefold() in QUERY_SOURCE_TYPES and (not str(dict(raw_dataset.get('source_config') or {}).get('query_template') or '').strip())))
    if require_complete and missing:
        _fail('Every Oracle, SQL and Datalake dataset requires a query_template.', {'dataset_keys': missing})
    evidence = {'contract_version': 'metadata.source-query-extraction.v1', 'status': 'passed', 'query_count': len(applied), 'dataset_keys': sorted(applied), 'datasets': {key: applied[key] for key in sorted(applied)}, 'missing_query_dataset_keys': missing}
    return (draft, evidence)

def compile_domain_package(authoring_payload: Mapping[str, Any], domain_id: str, environment: str, *, revision: int=1, lifecycle_status: str='validated') -> dict[str, Any]:
    """Compile an LLM draft to one immutable domain package.

    The function deliberately accepts a JSON-like mapping instead of raw text.
    Natural-language conversion belongs to the authoring LLM component; this
    function is the model-independent validator/compiler that follows it.
    """
    normalized_domain = _identity(domain_id, 'domain_id', DOMAIN_ID_PATTERN)
    normalized_environment = _identity(environment, 'environment', ENVIRONMENT_PATTERN)
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        _fail('revision은 1 이상의 정수여야 합니다.', {'revision': revision})
    if lifecycle_status not in {'draft', 'validated', 'active', 'deprecated', 'quarantined'}:
        _fail('지원하지 않는 domain package lifecycle입니다.', {'lifecycle_status': lifecycle_status})
    draft = deepcopy(dict(authoring_payload))
    validate_contract(draft, 'metadata-authoring-draft.schema.json', stage='metadata_authoring_compile', error_code='metadata_dependency_error')
    _reject_executable_or_secret_payload(draft)
    catalog = _catalog_from_draft(draft, domain_id=normalized_domain, environment=normalized_environment, revision=revision)
    authoring_sha256 = sha256_json(draft)
    package: dict[str, Any] = {'contract_version': DOMAIN_PACKAGE_VERSION, 'domain_id': normalized_domain, 'environment': normalized_environment, 'revision': revision, 'lifecycle': {'status': lifecycle_status}, 'compiler_version': DOMAIN_COMPILER_VERSION, 'authoring_sha256': authoring_sha256, 'runtime_catalog': catalog, 'package_sha256': '', 'bundle_sha256': ''}
    package['package_sha256'] = compute_package_sha256(package)
    package['bundle_sha256'] = compute_bundle_sha256(package)
    return validate_domain_package(package)

def build_runtime_catalog_v2(package: Mapping[str, Any]) -> dict[str, Any]:
    """Return the sealed v2 runtime catalog from a validated domain package."""
    validated = validate_domain_package(deepcopy(dict(package)))
    return deepcopy(validated['runtime_catalog'])

def validate_runtime_catalog_v2(catalog: Mapping[str, Any]) -> dict[str, Any]:
    value = deepcopy(dict(catalog))
    validate_contract(value, 'runtime-catalog-v2.schema.json', stage='metadata_catalog_v2_validation', error_code='metadata_dependency_error')
    expected = compute_runtime_catalog_v2_sha256(value)
    if value.get('catalog_sha256') != expected:
        _fail('runtime catalog v2 hash가 일치하지 않습니다.', {'expected': expected, 'actual': value.get('catalog_sha256')})
    _identity(str(value['domain_id']), 'domain_id', DOMAIN_ID_PATTERN)
    _identity(str(value['environment']), 'environment', ENVIRONMENT_PATTERN)
    _validate_catalog_semantics(value)
    return value

def validate_domain_package(package: Mapping[str, Any]) -> dict[str, Any]:
    value = deepcopy(dict(package))
    validate_contract(value, 'domain-package.schema.json', stage='domain_package_validation', error_code='metadata_dependency_error')
    catalog = validate_runtime_catalog_v2(value['runtime_catalog'])
    if catalog['domain_id'] != value['domain_id'] or catalog['environment'] != value['environment'] or catalog['revision'] != value['revision']:
        _fail('domain package와 runtime catalog identity가 일치하지 않습니다.')
    expected_package = compute_package_sha256(value)
    expected_bundle = compute_bundle_sha256(value)
    if value.get('package_sha256') != expected_package:
        _fail('domain package hash가 일치하지 않습니다.', {'expected': expected_package})
    if value.get('bundle_sha256') != expected_bundle:
        _fail('domain bundle hash가 일치하지 않습니다.', {'expected': expected_bundle})
    return value

def compute_runtime_catalog_v2_sha256(catalog: Mapping[str, Any]) -> str:
    material = {key: deepcopy(value) for key, value in catalog.items() if key != 'catalog_sha256'}
    return sha256_json(material)

def compute_package_sha256(package: Mapping[str, Any]) -> str:
    material = {key: deepcopy(value) for key, value in package.items() if key not in {'package_sha256', 'bundle_sha256'}}
    return sha256_json(material)

def compute_bundle_sha256(package: Mapping[str, Any]) -> str:
    """Seal the exact runtime selector projection, not mutable Mongo fields."""
    material = {'contract_version': 'metadata.domain-bundle.v1', 'domain_id': package.get('domain_id'), 'environment': package.get('environment'), 'revision': package.get('revision'), 'package_sha256': package.get('package_sha256'), 'catalog_sha256': dict(package.get('runtime_catalog') or {}).get('catalog_sha256'), 'compiler_version': package.get('compiler_version')}
    return sha256_json(material)

def make_bundle_document(package: Mapping[str, Any]) -> dict[str, Any]:
    """Create the immutable Mongo document written by the approval executor."""
    value = validate_domain_package(package)
    return {'_id': f"bundle:{value['bundle_sha256']}", **deepcopy(value)}

def make_active_pointer(package: Mapping[str, Any]) -> dict[str, Any]:
    """Create the small CAS-managed active selector for a validated package."""
    value = validate_domain_package(package)
    if value['lifecycle']['status'] not in {'validated', 'active'}:
        _fail('validated 또는 active package만 active pointer 후보가 될 수 있습니다.')
    pointer = {'contract_version': ACTIVE_POINTER_VERSION, 'domain_id': value['domain_id'], 'environment': value['environment'], 'revision': value['revision'], 'bundle_sha256': value['bundle_sha256'], 'package_sha256': value['package_sha256'], 'status': 'active'}
    validate_contract(pointer, 'active-domain-pointer.schema.json', stage='active_domain_pointer_validation', error_code='metadata_dependency_error')
    return pointer

def make_active_pointer_document(package: Mapping[str, Any]) -> dict[str, Any]:
    """Return the Mongo representation keyed by environment and domain."""
    pointer = make_active_pointer(package)
    return {'_id': f"active:{pointer['environment']}:{pointer['domain_id']}", **pointer}

def load_active_domain_bundle(database: Any, domain_id: str, environment: str, *, active_collection: str=ACTIVE_POINTER_COLLECTION, bundle_collection: str=DOMAIN_PACKAGE_COLLECTION) -> dict[str, Any]:
    """Load and revalidate one active package using an exact hash-bound pointer."""
    normalized_domain = _identity(domain_id, 'domain_id', DOMAIN_ID_PATTERN)
    normalized_environment = _identity(environment, 'environment', ENVIRONMENT_PATTERN)
    _assert_v6_collection(active_collection, ACTIVE_POINTER_COLLECTION)
    _assert_v6_collection(bundle_collection, DOMAIN_PACKAGE_COLLECTION)
    pointer = _find_one(database[active_collection], {'_id': f'active:{normalized_environment}:{normalized_domain}', 'status': 'active'})
    if not pointer:
        _fail('활성 domain pointer를 찾을 수 없습니다.', {'domain_id': normalized_domain, 'environment': normalized_environment})
    pointer_material = {key: pointer.get(key) for key in ('contract_version', 'domain_id', 'environment', 'revision', 'bundle_sha256', 'package_sha256', 'status')}
    validate_contract(pointer_material, 'active-domain-pointer.schema.json', stage='active_domain_pointer_validation', error_code='metadata_dependency_error')
    if pointer_material['domain_id'] != normalized_domain or pointer_material['environment'] != normalized_environment:
        _fail('active pointer identity does not match the requested domain and environment.', {'requested_domain_id': normalized_domain, 'requested_environment': normalized_environment, 'pointer_domain_id': pointer_material['domain_id'], 'pointer_environment': pointer_material['environment']})
    bundle = _find_one(database[bundle_collection], {'_id': f"bundle:{pointer['bundle_sha256']}"})
    if not bundle:
        _fail('active pointer가 가리키는 immutable bundle이 없습니다.')
    package = {key: deepcopy(value) for key, value in bundle.items() if key != '_id'}
    validated = validate_domain_package(package)
    if validated['bundle_sha256'] != pointer['bundle_sha256'] or validated['package_sha256'] != pointer['package_sha256'] or validated['revision'] != pointer['revision'] or (validated['domain_id'] != normalized_domain) or (validated['environment'] != normalized_environment):
        _fail('active pointer와 domain bundle pin이 일치하지 않습니다.')
    if validated['lifecycle']['status'] not in {'validated', 'active'}:
        _fail('runtime에서 사용할 수 없는 domain bundle lifecycle입니다.')
    return validated

def adapt_legacy_catalog_v1(catalog_v1: Mapping[str, Any], *, domain_id: str='manufacturing', environment: str='default', revision: int=1, display_name: str='Manufacturing Analysis', prompt_extensions: Mapping[str, Any] | None=None, specialized_functions: Iterable[Mapping[str, Any]]=(), output_profile: Mapping[str, Any] | None=None) -> dict[str, Any]:
    """Adapt the frozen manufacturing v1 fixture through the generic v2 contract."""
    datasets = deepcopy(dict(catalog_v1.get('datasets') or {}))
    legacy_output_profile = deepcopy(dict(output_profile or {}))
    legacy_output_profile.setdefault('planner_profile', 'legacy_v1_compat')
    legacy_output_profile.setdefault('legacy_catalog_sha256', str(catalog_v1.get('catalog_sha256') or ''))
    draft = {'contract_version': AUTHORING_DRAFT_VERSION, 'display_name': display_name, 'description': 'Legacy manufacturing catalog isolated as a versioned domain pack.', 'locale': 'ko-KR', 'timezone': 'Asia/Seoul', 'datasets': datasets, 'metrics': deepcopy(dict(catalog_v1.get('metrics') or {})), 'entity_groups': deepcopy(dict(catalog_v1.get('process_groups') or {})), 'grains': {'product': {'keys': deepcopy(list(catalog_v1.get('recipes', {}).get('product.standard', {}).get('grain', {}).get('keys') or []))}}, 'relations': {}, 'orderings': {'process': {'items': deepcopy(list(catalog_v1.get('process_order') or []))}}, 'predicates': deepcopy(dict(catalog_v1.get('product_groups') or {})), 'recipes': deepcopy(dict(catalog_v1.get('recipes') or {})), 'aliases': deepcopy(dict(catalog_v1.get('aliases') or {})), 'prompt_extensions': deepcopy(dict(prompt_extensions or {'intent': '', 'answer': ''})), 'specialized_functions': [deepcopy(dict(item)) for item in specialized_functions], 'output_profile': legacy_output_profile, 'source_provenance': {'legacy_catalog_sha256': str(catalog_v1.get('catalog_sha256') or '')}}
    for dataset in draft['datasets'].values():
        dataset.pop('key', None)
        if dataset.get('source_type') == 'fixture':
            dataset['source_type'] = 'dummy'
            dataset['fixture_only'] = True
        dataset.setdefault('source_adapter', str(dataset.get('source_type') or ''))
        if 'date_filter_contract' in dataset and 'date_policy' not in dataset:
            dataset['date_policy'] = deepcopy(dataset['date_filter_contract'])
        for binding in dict(dataset.get('fields') or {}).values():
            binding.setdefault('aliases', [])
    draft['recipes'] = _map_legacy_recipe_ops(draft['recipes'])
    return compile_domain_package(draft, domain_id, environment, revision=revision, lifecycle_status='validated')

def _catalog_from_draft(draft: Mapping[str, Any], *, domain_id: str, environment: str, revision: int) -> dict[str, Any]:
    datasets: dict[str, Any] = {}
    fields: dict[str, Any] = {}
    for dataset_key in sorted(draft['datasets']):
        raw = deepcopy(dict(draft['datasets'][dataset_key]))
        raw['key'] = dataset_key
        raw.setdefault('display_name', dataset_key)
        raw.setdefault('time_scope', 'unspecified')
        raw.setdefault('source_adapter', str(raw.get('source_type') or ''))
        raw.setdefault('config_ref', '')
        raw.setdefault('query_ref', '')
        raw.setdefault('parameters', {})
        raw.setdefault('date_policy', {})
        raw.setdefault('default_detail_fields', [])
        raw.setdefault('read_policy', {'read_only': True, 'timeout_seconds': 30, 'max_rows': 50000})
        policy = dict(raw['read_policy'])
        policy.setdefault('read_only', True)
        policy.setdefault('timeout_seconds', 30)
        policy.setdefault('max_rows', 50000)
        raw['read_policy'] = policy
        normalized_bindings: dict[str, Any] = {}
        for canonical_field in sorted(raw['fields']):
            binding = deepcopy(dict(raw['fields'][canonical_field]))
            binding.setdefault('physical_aliases', [])
            binding.setdefault('aliases', [])
            binding.setdefault('required_in_source', False)
            binding.setdefault('nullable', True)
            binding.setdefault('coercion', _default_coercion(str(binding['semantic_type'])))
            normalized_bindings[canonical_field] = binding
            field_card = fields.setdefault(canonical_field, {'canonical_field': canonical_field, 'semantic_type': binding['semantic_type'], 'aliases': [], 'dataset_keys': [], 'roles': []})
            if str(field_card['semantic_type']).casefold() != str(binding['semantic_type']).casefold():
                _fail('같은 canonical field의 semantic_type이 dataset마다 다릅니다.', {'field': canonical_field, 'dataset_key': dataset_key})
            field_card['dataset_keys'].append(dataset_key)
            field_card['aliases'] = sorted(set(field_card['aliases']) | set(binding.get('aliases', [])))
            field_card['roles'] = sorted(set(field_card['roles']) | set(binding['roles']))
        raw['fields'] = normalized_bindings
        datasets[dataset_key] = raw
    catalog: dict[str, Any] = {'contract_version': RUNTIME_CATALOG_V2, 'domain_id': domain_id, 'environment': environment, 'revision': revision, 'compiler_version': DOMAIN_COMPILER_VERSION, 'display_name': str(draft['display_name']), 'description': str(draft.get('description') or ''), 'locale': str(draft.get('locale') or 'ko-KR'), 'timezone': str(draft.get('timezone') or 'Asia/Seoul'), 'datasets': datasets, 'fields': dict(sorted(fields.items())), 'metrics': _identity_cards(draft.get('metrics'), 'metric_id'), 'entity_groups': _identity_cards(draft.get('entity_groups'), 'group_id'), 'grains': _identity_cards(draft.get('grains'), 'grain_id'), 'relations': _identity_cards(draft.get('relations'), 'relation_id'), 'orderings': _identity_cards(draft.get('orderings'), 'ordering_id'), 'predicates': _identity_cards(draft.get('predicates'), 'predicate_id'), 'recipes': _identity_cards(draft.get('recipes'), 'recipe_id'), 'aliases': dict(sorted(deepcopy(dict(draft.get('aliases') or {})).items())), 'prompt_extensions': {'intent': str(dict(draft.get('prompt_extensions') or {}).get('intent') or ''), 'answer': str(dict(draft.get('prompt_extensions') or {}).get('answer') or '')}, 'specialized_functions': sorted([deepcopy(dict(item)) for item in draft.get('specialized_functions') or []], key=lambda item: (str(item.get('function_id')), int(item.get('version') or 0))), 'output_profile': deepcopy(dict(draft.get('output_profile') or {})), 'catalog_sha256': ''}
    catalog['catalog_sha256'] = compute_runtime_catalog_v2_sha256(catalog)
    return validate_runtime_catalog_v2(catalog)

def _validate_catalog_shape_compatibility(catalog: Mapping[str, Any]) -> None:
    fields = dict(catalog['fields'])
    physical_owners_by_dataset: dict[str, dict[str, str]] = {}
    for dataset_key, raw_dataset in dict(catalog['datasets']).items():
        dataset = dict(raw_dataset)
        if dataset.get('key') != dataset_key:
            _fail('dataset key가 object identity와 일치하지 않습니다.', {'dataset_key': dataset_key})
        if dataset.get('source_type') not in ALLOWED_SOURCE_TYPES:
            _fail('지원하지 않는 source_type입니다.', {'dataset_key': dataset_key})
        if dict(dataset.get('read_policy') or {}).get('read_only') is not True:
            _fail('dataset read policy는 read_only여야 합니다.', {'dataset_key': dataset_key})
        bindings = dict(dataset.get('fields') or {})
        if not bindings:
            _fail('dataset field binding이 비어 있습니다.', {'dataset_key': dataset_key})
        owners: dict[str, str] = {}
        for canonical_field, raw_binding in bindings.items():
            binding = dict(raw_binding)
            if canonical_field not in fields:
                _fail('top-level field card가 없습니다.', {'dataset_key': dataset_key, 'field': canonical_field})
            roles = set(binding.get('roles') or [])
            if not roles or not roles <= ALLOWED_FIELD_ROLES:
                _fail('field role이 비어 있거나 허용 범위를 벗어났습니다.', {'field': canonical_field})
            physicals = [str(binding.get('physical_column') or ''), *map(str, binding.get('physical_aliases') or [])]
            if not physicals[0] or len(physicals) != len(set(physicals)):
                _fail('physical field binding이 비어 있거나 중복됩니다.', {'field': canonical_field})
            for physical in physicals:
                owner = owners.get(physical)
                if owner and owner != canonical_field:
                    _fail('한 physical field가 둘 이상의 canonical field에 연결됐습니다.', {'dataset_key': dataset_key, 'physical_field': physical, 'owners': [owner, canonical_field]})
                owners[physical] = canonical_field
        if not set(dataset.get('default_detail_fields') or []) <= set(bindings):
            _fail('default detail field가 dataset binding에 없습니다.', {'dataset_key': dataset_key})
        physical_owners_by_dataset[dataset_key] = owners
    families = {str(item.get('family')) for item in catalog['datasets'].values()}
    for metric_id, raw_metric in dict(catalog['metrics']).items():
        metric = dict(raw_metric)
        binding = metric.get('source_binding')
        if isinstance(binding, dict):
            if binding.get('field') not in fields or binding.get('dataset_family') not in families:
                _fail('metric source binding이 닫힌 catalog를 참조하지 않습니다.', {'metric_id': metric_id})
        additivity = metric.get('additivity')
        if isinstance(additivity, dict) and additivity.get('default') == 'non_additive':
            if 'sum' in (additivity.get('allowed_rollups') or []):
                _fail('non-additive metric에 sum을 허용할 수 없습니다.', {'metric_id': metric_id})
    for relation_id, raw_relation in dict(catalog.get('relations') or {}).items():
        relation = dict(raw_relation)
        left = str(relation.get('left_dataset') or '')
        right = str(relation.get('right_dataset') or '')
        if left not in catalog['datasets'] or right not in catalog['datasets']:
            _fail('relation dataset dependency가 닫혀 있지 않습니다.', {'relation_id': relation_id})
        left_keys = list(relation.get('left_keys') or [])
        right_keys = list(relation.get('right_keys') or [])
        if not left_keys or len(left_keys) != len(right_keys):
            _fail('relation join key cardinality가 올바르지 않습니다.', {'relation_id': relation_id})
        if not set(left_keys) <= set(catalog['datasets'][left]['fields']):
            _fail('relation left key binding이 없습니다.', {'relation_id': relation_id})
        if not set(right_keys) <= set(catalog['datasets'][right]['fields']):
            _fail('relation right key binding이 없습니다.', {'relation_id': relation_id})
        if relation.get('join_type') not in {'inner', 'left', 'right', 'outer', 'semi', 'anti'}:
            _fail('relation join_type이 허용되지 않습니다.', {'relation_id': relation_id})
        if relation.get('cardinality') not in {'one_to_zero_or_one', 'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many'}:
            _fail('relation cardinality가 명시되지 않았습니다.', {'relation_id': relation_id})
    for recipe_id, raw_recipe in dict(catalog['recipes']).items():
        for operation in _recipe_operations(raw_recipe):
            if operation not in ALLOWED_OPERATIONS:
                _fail('등록되지 않은 typed operation이 recipe에 포함됐습니다.', {'recipe_id': recipe_id, 'op': operation})
    seen_functions: set[tuple[str, int]] = set()
    for function in catalog.get('specialized_functions') or []:
        marker = (str(function['function_id']), int(function['version']))
        if marker in seen_functions:
            _fail('specialized function identity가 중복됩니다.', {'function_id': marker[0]})
        seen_functions.add(marker)
        if function.get('execution_mode') != 'registered_standalone' or not SHA256_PATTERN.fullmatch(str(function.get('implementation_sha256') or '')):
            _fail('specialized function은 hash-pinned registered standalone이어야 합니다.')

def _validate_catalog_semantics(catalog: Mapping[str, Any]) -> None:
    """Validate the executable closure of one sealed runtime catalog.

    JSON Schema checks shape.  This pass checks that every executable reference
    resolves to a compatible registered object before the package can be
    activated.  It intentionally distinguishes generic v2 metadata from the
    explicitly hash-pinned legacy manufacturing compatibility profile.
    """
    profile = _catalog_planner_profile(catalog)
    fields = dict(catalog['fields'])
    datasets = dict(catalog['datasets'])
    family_datasets: dict[str, list[str]] = {}
    for dataset_key, raw_dataset in datasets.items():
        dataset = dict(raw_dataset)
        if dataset.get('key') != dataset_key:
            _fail('Dataset key does not match object identity.', {'dataset_key': dataset_key})
        if dataset.get('source_type') not in ALLOWED_SOURCE_TYPES:
            _fail('Unsupported dataset source type.', {'dataset_key': dataset_key})
        if dict(dataset.get('read_policy') or {}).get('read_only') is not True:
            _fail('Dataset read policy must be read-only.', {'dataset_key': dataset_key})
        source_config = dataset.get('source_config')
        if source_config is not None:
            if not isinstance(source_config, dict):
                _fail('Dataset source_config must be an object.', {'dataset_key': dataset_key})
            configured_type = str(source_config.get('source_type') or dataset.get('source_type') or '').casefold()
            if configured_type != str(dataset.get('source_type') or '').casefold():
                _fail('Dataset source_config source_type does not match the dataset.', {'dataset_key': dataset_key})
            query_template = source_config.get('query_template')
            if query_template not in (None, ''):
                if configured_type not in QUERY_SOURCE_TYPES:
                    _fail('Only Oracle, SQL and Datalake datasets may store query_template.', {'dataset_key': dataset_key})
                normalized_query = validate_read_only_query_template(str(query_template))
                if normalized_query != query_template:
                    _fail('query_template must already use normalized LF line endings.', {'dataset_key': dataset_key})
                placeholders = query_template_parameters(normalized_query)
                required_params = source_config.get('required_params', placeholders)
                if not isinstance(required_params, list) or any((not isinstance(item, str) for item in required_params)):
                    _fail('source_config.required_params must be a string array.', {'dataset_key': dataset_key})
                if list(required_params) != placeholders:
                    _fail('source_config.required_params must exactly match query placeholders in occurrence order.', {'dataset_key': dataset_key, 'expected': placeholders, 'actual': required_params})
                parameter_cards = dict(dataset.get('parameters') or {})
                missing_cards = [name for name in placeholders if not isinstance(parameter_cards.get(name), dict)]
                optional_cards = [name for name in placeholders if not bool(dict(parameter_cards.get(name) or {}).get('required'))]
                if missing_cards or optional_cards:
                    _fail('Every query placeholder requires a required typed parameter card.', {'dataset_key': dataset_key, 'missing': missing_cards, 'not_required': optional_cards})
        family = str(dataset.get('family') or '').strip()
        if not family:
            _fail('Dataset family is required.', {'dataset_key': dataset_key})
        family_datasets.setdefault(family, []).append(dataset_key)
        bindings = dict(dataset.get('fields') or {})
        if not bindings:
            _fail('Dataset field bindings cannot be empty.', {'dataset_key': dataset_key})
        owners: dict[str, str] = {}
        for canonical_field, raw_binding in bindings.items():
            binding = dict(raw_binding)
            field_card = dict(fields.get(canonical_field) or {})
            if not field_card:
                _fail('Top-level field card is missing.', {'dataset_key': dataset_key, 'field': canonical_field})
            if dataset_key not in set(field_card.get('dataset_keys') or []):
                _fail('Field card does not include its dataset owner.', {'dataset_key': dataset_key, 'field': canonical_field})
            if not _semantic_types_compatible(field_card.get('semantic_type'), binding.get('semantic_type')):
                _fail('Field semantic types are incompatible.', {'dataset_key': dataset_key, 'field': canonical_field})
            roles = set(binding.get('roles') or [])
            if not roles or not roles <= ALLOWED_FIELD_ROLES:
                _fail('Field roles are empty or unsupported.', {'dataset_key': dataset_key, 'field': canonical_field})
            if not roles <= set(field_card.get('roles') or []):
                _fail('Field card roles do not cover dataset roles.', {'dataset_key': dataset_key, 'field': canonical_field})
            filter_operators = set(binding.get('allowed_filter_operators') or [])
            if not filter_operators <= FILTER_OPERATORS or (filter_operators and 'filter' not in roles):
                _fail('Field filter operator contract is invalid.', {'dataset_key': dataset_key, 'field': canonical_field})
            physicals = [str(binding.get('physical_column') or ''), *map(str, binding.get('physical_aliases') or [])]
            if not physicals[0] or len(physicals) != len(set(physicals)):
                _fail('Physical field binding is empty or duplicated.', {'dataset_key': dataset_key, 'field': canonical_field})
            for physical in physicals:
                owner = owners.get(physical)
                if owner and owner != canonical_field:
                    _fail('One physical field maps to multiple canonical fields.', {'dataset_key': dataset_key, 'physical_field': physical})
                owners[physical] = canonical_field
        if not set(dataset.get('default_detail_fields') or []) <= set(bindings):
            _fail('Default detail field is not bound by the dataset.', {'dataset_key': dataset_key})
        date_field = str(dict(dataset.get('date_policy') or {}).get('field') or '')
        if date_field and (date_field not in bindings or 'filter' not in set(bindings[date_field].get('roles') or [])):
            _fail('Dataset date policy field must be a filterable bound field.', {'dataset_key': dataset_key, 'field': date_field})
    _validate_grains_and_orderings(catalog, profile)
    _validate_relations(catalog)
    _validate_metrics(catalog, family_datasets, profile)
    _validate_predicates_and_groups(catalog, profile)
    _validate_recipes(catalog, profile)
    _validate_aliases(catalog, profile)
    _validate_specialized_functions(catalog)

def _catalog_planner_profile(catalog: Mapping[str, Any]) -> str:
    output_profile = dict(catalog.get('output_profile') or {})
    profile = str(output_profile.get('planner_profile') or 'generic_v2')
    if profile == 'generic_v2':
        return profile
    if profile == 'legacy_v1_compat':
        if not SHA256_PATTERN.fullmatch(str(output_profile.get('legacy_catalog_sha256') or '')):
            _fail('Legacy planner profile requires an exact catalog hash pin.')
        return profile
    _fail('Unsupported planner profile.', {'planner_profile': profile})
    raise AssertionError('unreachable')

def _validate_relations(catalog: Mapping[str, Any]) -> None:
    datasets = dict(catalog['datasets'])
    for relation_id, raw_relation in dict(catalog.get('relations') or {}).items():
        relation = dict(raw_relation)
        left = str(relation.get('left_dataset') or '')
        right = str(relation.get('right_dataset') or '')
        if left not in datasets or right not in datasets:
            _fail('Relation dataset dependency is missing.', {'relation_id': relation_id})
        left_keys = list(relation.get('left_keys') or [])
        right_keys = list(relation.get('right_keys') or [])
        if not left_keys or len(left_keys) != len(right_keys):
            _fail('Relation join-key cardinality is invalid.', {'relation_id': relation_id})
        left_fields = dict(datasets.get(left, {}).get('fields') or {})
        right_fields = dict(datasets.get(right, {}).get('fields') or {})
        for left_key, right_key in zip(left_keys, right_keys):
            if left_key not in left_fields or right_key not in right_fields:
                _fail('Relation join-key binding is missing.', {'relation_id': relation_id})
            if 'join' not in set(left_fields[left_key].get('roles') or []) or 'join' not in set(right_fields[right_key].get('roles') or []):
                _fail('Relation keys must carry the join role.', {'relation_id': relation_id})
            if not _semantic_types_compatible(left_fields[left_key].get('semantic_type'), right_fields[right_key].get('semantic_type')):
                _fail('Relation key semantic types are incompatible.', {'relation_id': relation_id})
        if relation.get('join_type') not in {'inner', 'left', 'right', 'outer', 'semi', 'anti'}:
            _fail('Relation join type is unsupported.', {'relation_id': relation_id})
        if relation.get('cardinality') not in {'one_to_zero_or_one', 'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many'}:
            _fail('Relation cardinality is invalid.', {'relation_id': relation_id})

def _validate_metrics(catalog: Mapping[str, Any], family_datasets: Mapping[str, list[str]], profile: str) -> None:
    metrics = dict(catalog.get('metrics') or {})
    datasets = dict(catalog['datasets'])
    dependency_graph: dict[str, set[str]] = {metric_id: set() for metric_id in metrics}
    for metric_id, raw_metric in metrics.items():
        metric = dict(raw_metric)
        binding = metric.get('source_binding')
        formula = metric.get('formula')
        if isinstance(binding, dict):
            family = str(binding.get('dataset_family') or '')
            source_field = str(binding.get('field') or '')
            owners = list(family_datasets.get(family) or [])
            if not owners or not source_field:
                _fail('Metric source family or field is missing.', {'metric_id': metric_id})
            if metric.get('source_field') not in (None, '', source_field):
                _fail('Metric source_field disagrees with source_binding.', {'metric_id': metric_id})
            additivity = dict(metric.get('additivity') or {})
            rollups = set(additivity.get('allowed_rollups') or [])
            aggregation = str(metric.get('aggregation') or '')
            if aggregation:
                rollups.add(aggregation)
            distinct = additivity.get('default') == 'distinct' or (bool(rollups) and rollups <= DISTINCT_ROLLUPS)
            for dataset_key in owners:
                dataset_fields = dict(datasets[dataset_key].get('fields') or {})
                field_binding = dict(dataset_fields.get(source_field) or {})
                if not field_binding:
                    _fail('Metric source field is not present in every dataset of its family.', {'metric_id': metric_id, 'dataset_key': dataset_key, 'field': source_field})
                roles = set(field_binding.get('roles') or [])
                compatible_roles = {'aggregate', 'group', 'join', 'metric'} if distinct else {'aggregate', 'metric'}
                if not roles & compatible_roles:
                    _fail('Metric source field roles are incompatible with its rollup.', {'metric_id': metric_id, 'dataset_key': dataset_key})
                semantic = str(field_binding.get('semantic_type') or '').casefold()
                if rollups & NUMERIC_ROLLUPS and semantic not in NUMERIC_SEMANTIC_TYPES:
                    _fail('Numeric metric rollup requires a numeric source field.', {'metric_id': metric_id, 'dataset_key': dataset_key})
                for fixed_filter in binding.get('fixed_filters') or []:
                    _validate_filter_leaf(fixed_filter, catalog, allowed_dataset=dataset_key)
        elif not isinstance(formula, dict):
            _fail('Metric must have either a source binding or a formula.', {'metric_id': metric_id})
        additivity = metric.get('additivity')
        if isinstance(additivity, dict) and additivity.get('default') == 'non_additive' and ('sum' in (additivity.get('allowed_rollups') or [])):
            _fail('Non-additive metric cannot allow sum.', {'metric_id': metric_id})
        if isinstance(formula, dict):
            dependency_graph[metric_id].update(_validate_formula(metric_id, formula, catalog, profile))
        for dependency in metric.get('dependencies') or []:
            dependency_id = str(dependency)
            if dependency_id in metrics:
                dependency_graph[metric_id].add(dependency_id)
            elif dependency_id not in catalog['fields'] and (not (profile == 'legacy_v1_compat' and dependency_id in FORMULA_RUNTIME_REFS)):
                _fail('Metric dependency is not registered.', {'metric_id': metric_id, 'dependency': dependency_id})
    _validate_metric_dependency_dag(dependency_graph)

def _validate_formula(metric_id: str, formula: Mapping[str, Any], catalog: Mapping[str, Any], profile: str) -> set[str]:
    expression = formula.get('expression')
    if not isinstance(expression, dict):
        operator = str(formula.get('op') or '')
        key_pairs = {'add': ('left_metric', 'right_metric'), 'subtract': ('left_metric', 'right_metric'), 'multiply': ('left_metric', 'right_metric'), 'safe_divide': ('numerator_metric', 'denominator_metric')}
        if operator not in key_pairs:
            _fail('Formula operator is unsupported.', {'metric_id': metric_id, 'operator': operator})
        left_key, right_key = key_pairs[operator]
        expression = {'op': operator, 'args': [{'metric_ref': str(formula.get(left_key) or '')}, {'metric_ref': str(formula.get(right_key) or '')}]}
        if operator == 'safe_divide':
            expression['zero_division'] = str(formula.get('zero_division') or 'null')
    refs: set[str] = set()
    nodes, depth = _validate_formula_node(expression, catalog, profile, refs, 1)
    if isinstance(formula.get('max_nodes'), int) and nodes > int(formula['max_nodes']):
        _fail('Formula exceeds its declared node bound.', {'metric_id': metric_id})
    if isinstance(formula.get('max_depth'), int) and depth > int(formula['max_depth']):
        _fail('Formula exceeds its declared depth bound.', {'metric_id': metric_id})
    return refs

def _validate_formula_node(node: Mapping[str, Any], catalog: Mapping[str, Any], profile: str, metric_refs: set[str], depth: int) -> tuple[int, int]:
    leaf_kinds = [key for key in ('metric_ref', 'field_ref', 'runtime_ref', 'literal') if key in node]
    if leaf_kinds:
        if len(leaf_kinds) != 1 or node.get('op'):
            _fail('Formula leaf must contain exactly one reference or literal.')
        kind = leaf_kinds[0]
        value = str(node.get(kind) or '') if kind != 'literal' else node.get(kind)
        if kind == 'metric_ref':
            if value not in catalog['metrics']:
                _fail('Formula metric reference is not registered.', {'metric_ref': value})
            metric_refs.add(str(value))
        elif kind == 'field_ref':
            if not value or (profile != 'legacy_v1_compat' and value not in catalog['fields'] and (value not in catalog['metrics'])):
                _fail('Formula field reference is not registered.', {'field_ref': value})
        elif kind == 'runtime_ref':
            if profile != 'legacy_v1_compat' or value not in FORMULA_RUNTIME_REFS:
                _fail('Formula runtime reference is not allowed.', {'runtime_ref': value})
        return (1, depth)
    operator = str(node.get('op') or '')
    allowed = LEGACY_FORMULA_OPERATORS if profile == 'legacy_v1_compat' else FORMULA_OPERATORS
    if operator not in allowed:
        _fail('Formula expression operator is unsupported.', {'operator': operator})
    args = node.get('args')
    if not isinstance(args, list) or len(args) != FORMULA_ARITY[operator] or (not all((isinstance(item, dict) for item in args))):
        _fail('Formula expression arity is invalid.', {'operator': operator})
    if operator == 'safe_divide' and str(node.get('zero_division') or 'null') not in SAFE_DIVIDE_ZERO_POLICIES:
        _fail('safe_divide zero policy is unsupported.')
    nodes = 1
    deepest = depth
    for child in args:
        child_nodes, child_depth = _validate_formula_node(child, catalog, profile, metric_refs, depth + 1)
        nodes += child_nodes
        deepest = max(deepest, child_depth)
    return (nodes, deepest)

def _validate_metric_dependency_dag(graph: Mapping[str, set[str]]) -> None:
    state: dict[str, int] = {}

    def visit(metric_id: str, path: list[str]) -> None:
        if state.get(metric_id) == 1:
            _fail('Metric formula dependency cycle detected.', {'cycle': [*path, metric_id]})
        if state.get(metric_id) == 2:
            return
        state[metric_id] = 1
        for dependency in graph.get(metric_id, set()):
            visit(dependency, [*path, metric_id])
        state[metric_id] = 2
    for metric_id in graph:
        visit(metric_id, [])

def _validate_grains_and_orderings(catalog: Mapping[str, Any], profile: str) -> None:
    fields = dict(catalog['fields'])
    for grain_id, raw_grain in dict(catalog.get('grains') or {}).items():
        grain = dict(raw_grain)
        keys = list(grain.get('keys') or [])
        if not keys or not set(keys) <= set(fields):
            _fail('Grain keys must reference registered fields.', {'grain_id': grain_id})
        for key in keys:
            if not set(fields[key].get('roles') or []) & {'group', 'join'}:
                _fail('Grain key must carry a group or join role.', {'grain_id': grain_id, 'field': key})
        if not set(grain.get('display_fields') or []) <= set(fields):
            _fail('Grain display field is not registered.', {'grain_id': grain_id})
    for ordering_id, raw_ordering in dict(catalog.get('orderings') or {}).items():
        for item in dict(raw_ordering).get('keys') or []:
            if not isinstance(item, dict) or str(item.get('field') or '') not in fields:
                _fail('Ordering field is not registered.', {'ordering_id': ordering_id})
            if item.get('direction') not in {'asc', 'desc'}:
                _fail('Ordering direction is invalid.', {'ordering_id': ordering_id})

def _validate_predicates_and_groups(catalog: Mapping[str, Any], profile: str) -> None:
    fields = dict(catalog['fields'])
    grain_ids = set(catalog.get('grains') or {})
    if profile == 'legacy_v1_compat':
        grain_ids.update(_nested_identity_values(catalog.get('recipes') or {}, 'grain_id'))
        grain_ids.update(catalog.get('recipes') or {})
    for predicate_id, raw_card in dict(catalog.get('predicates') or {}).items():
        card = dict(raw_card)
        allowed = set(card.get('allowed_operators') or [])
        if allowed and (not allowed <= FILTER_OPERATORS):
            _fail('Predicate declares an unsupported operator.', {'predicate_id': predicate_id})
        grain_id = str(card.get('grain_id') or '')
        if grain_id and grain_id not in grain_ids:
            _fail('Predicate grain is not registered.', {'predicate_id': predicate_id, 'grain_id': grain_id})
        predicate = card.get('predicate') if isinstance(card.get('predicate'), dict) else card
        _validate_predicate_tree(predicate, catalog, allowed or None, predicate_id)
    for group_id, raw_group in dict(catalog.get('entity_groups') or {}).items():
        group = dict(raw_group)
        target_field = str(group.get('target_field') or group.get('entity') or '')
        if target_field not in fields or not set(fields[target_field].get('roles') or []) & {'filter', 'group'}:
            _fail('Entity group target must be a registered filter/group field.', {'group_id': group_id})
        if group.get('expansion') == 'closed_set' and (not list(group.get('members') or [])):
            _fail('Closed-set entity group must declare members.', {'group_id': group_id})
        selection = group.get('selection')
        if isinstance(selection, dict):
            operator = str(selection.get('operator') or '')
            if operator != 'all_registered':
                _validate_filter_leaf({**selection, 'field': target_field}, catalog)

def _validate_predicate_tree(node: Mapping[str, Any], catalog: Mapping[str, Any], allowed: set[str] | None, predicate_id: str) -> None:
    boolean_op = str(node.get('op') or '')
    if boolean_op:
        clauses = node.get('clauses')
        if boolean_op not in {'all', 'any'} or not isinstance(clauses, list) or (not clauses):
            _fail('Predicate boolean tree is invalid.', {'predicate_id': predicate_id})
        for clause in clauses:
            if not isinstance(clause, dict):
                _fail('Predicate clause must be an object.', {'predicate_id': predicate_id})
            _validate_predicate_tree(clause, catalog, allowed, predicate_id)
        return
    operator = _validate_filter_leaf(node, catalog)
    if allowed is not None and operator not in allowed:
        _fail('Predicate leaf operator is outside the declared allowlist.', {'predicate_id': predicate_id, 'operator': operator})

def _validate_filter_leaf(leaf: Mapping[str, Any], catalog: Mapping[str, Any], *, allowed_dataset: str='') -> str:
    field = str(leaf.get('field') or '')
    operator = str(leaf.get('operator') or '')
    if operator not in FILTER_OPERATORS:
        _fail('Filter operator is unsupported.', {'field': field, 'operator': operator})
    owners = [allowed_dataset] if allowed_dataset else list(dict(catalog.get('fields') or {}).get(field, {}).get('dataset_keys') or [])
    if not owners:
        _fail('Filter field is not registered.', {'field': field})
    matched = False
    for dataset_key in owners:
        binding = dict(dict(dict(catalog['datasets'])[dataset_key].get('fields') or {}).get(field) or {})
        if 'filter' not in set(binding.get('roles') or []):
            continue
        allowed = set(binding.get('allowed_filter_operators') or [])
        if allowed and operator not in allowed:
            continue
        declared_semantic = leaf.get('semantic_type')
        if declared_semantic and (not _semantic_types_compatible(declared_semantic, binding.get('semantic_type'))):
            continue
        matched = True
    if not matched:
        _fail('Filter field role, semantic type, or operator is incompatible.', {'field': field, 'operator': operator})
    return operator

def _validate_recipes(catalog: Mapping[str, Any], profile: str) -> None:
    recipes = dict(catalog.get('recipes') or {})
    allowed_operations = ALLOWED_OPERATIONS if profile == 'legacy_v1_compat' else GENERIC_V2_OPERATIONS
    for recipe_id, raw_recipe in recipes.items():
        recipe = dict(raw_recipe)
        required = list(recipe.get('required_slots') or [])
        if len(required) != len(set(required)) or any((not isinstance(slot, str) or not slot for slot in required)):
            _fail('Recipe required slots are invalid.', {'recipe_id': recipe_id})
        if profile != 'legacy_v1_compat' and (not set(required) <= GENERIC_REQUIRED_SLOTS):
            _fail('Generic recipe uses an unregistered required slot.', {'recipe_id': recipe_id, 'required_slots': required})
        for operation in _recipe_operations(recipe):
            if operation not in allowed_operations:
                _fail('Recipe uses an operation outside its planner profile.', {'recipe_id': recipe_id, 'op': operation, 'planner_profile': profile})
        if profile != 'legacy_v1_compat':
            _validate_generic_recipe_refs(recipe_id, recipe, catalog)

def _validate_generic_recipe_refs(recipe_id: str, recipe: Mapping[str, Any], catalog: Mapping[str, Any]) -> None:
    template = recipe.get('default_operation_template')
    if not isinstance(template, dict):
        _fail('Generic recipe requires a typed operation template.', {'recipe_id': recipe_id})
    registries = {'dataset': set(catalog.get('datasets') or {}), 'relation': set(catalog.get('relations') or {}), 'metric': set(catalog.get('metrics') or {}), 'field': set(catalog.get('fields') or {}) | set(catalog.get('metrics') or {}), 'grain': set(catalog.get('grains') or {}), 'predicate': set(catalog.get('predicates') or {}), 'recipe': set(catalog.get('recipes') or {})}

    def check(kind: str, value: Any, path: str) -> None:
        if not isinstance(value, str) or not value or value.startswith('$'):
            return
        prefix, separator, suffix = value.partition(':')
        normalized = suffix if separator and prefix in registries else value
        if normalized not in registries[kind]:
            _fail('Generic recipe reference is not registered.', {'recipe_id': recipe_id, 'reference_kind': kind, 'reference': value, 'path': path})
    singular = {'dataset': 'dataset', 'dataset_key': 'dataset', 'relation_id': 'relation', 'relation_ref': 'relation', 'metric': 'metric', 'metric_ref': 'metric', 'left_metric_ref': 'metric', 'right_metric_ref': 'metric', 'formula_ref': 'metric', 'grain_id': 'grain', 'grain_ref': 'grain', 'predicate_id': 'predicate', 'predicate_ref': 'predicate', 'recipe_ref': 'recipe', 'field': 'field', 'field_ref': 'field', 'output_field': 'field', 'left': 'field', 'right': 'field'}
    plural = {'datasets': 'dataset', 'dataset_keys': 'dataset', 'metrics': 'metric', 'metric_refs': 'metric', 'fields': 'field', 'allowed_fields': 'field', 'group_by': 'field', 'stable_tie_break': 'field', 'relation_refs': 'relation', 'grain_refs': 'grain', 'predicate_refs': 'predicate', 'recipe_refs': 'recipe'}

    def walk(value: Any, path: str='template') -> None:
        if isinstance(value, dict):
            operation = str(value.get('op') or '')
            if operation == 'join' and (not value.get('relation_id')) and (not value.get('relation_ref')):
                _fail('Generic join recipe must reference a registered relation.', {'recipe_id': recipe_id, 'path': path})
            if operation == 'derive' and (not value.get('metric')) and (not value.get('formula_ref')):
                _fail('Generic derive recipe must reference a registered metric formula.', {'recipe_id': recipe_id, 'path': path})
            for key, child in value.items():
                if key in singular:
                    check(singular[key], child, f'{path}.{key}')
                elif key in plural and isinstance(child, list):
                    for item in child:
                        if isinstance(item, str):
                            check(plural[key], item, f'{path}.{key}')
                if key not in {'aliases', 'description', 'pseudocode'}:
                    walk(child, f'{path}.{key}')
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f'{path}.{index}')
    walk(template)

def _validate_aliases(catalog: Mapping[str, Any], profile: str) -> None:
    if profile == 'legacy_v1_compat':
        return
    registries = {'dataset': set(catalog.get('datasets') or {}), 'field': set(catalog.get('fields') or {}), 'metric': set(catalog.get('metrics') or {}), 'relation': set(catalog.get('relations') or {}), 'grain': set(catalog.get('grains') or {}), 'predicate': set(catalog.get('predicates') or {}), 'recipe': set(catalog.get('recipes') or {}), 'entity_group': set(catalog.get('entity_groups') or {})}
    for alias_id, raw_alias in dict(catalog.get('aliases') or {}).items():
        alias = dict(raw_alias)
        target_type = str(alias.get('target_type') or '')
        target_key = str(alias.get('target_key') or '')
        if target_type not in registries or target_key not in registries[target_type]:
            _fail('Alias target is not registered.', {'alias_id': alias_id, 'target_type': target_type, 'target_key': target_key})

def _validate_specialized_functions(catalog: Mapping[str, Any]) -> None:
    seen_functions: set[tuple[str, int]] = set()
    for function in catalog.get('specialized_functions') or []:
        marker = (str(function['function_id']), int(function['version']))
        if marker in seen_functions:
            _fail('Specialized function identity is duplicated.', {'function_id': marker[0]})
        seen_functions.add(marker)
        if function.get('execution_mode') != 'registered_standalone' or not SHA256_PATTERN.fullmatch(str(function.get('implementation_sha256') or '')):
            _fail('Specialized function must be registered-standalone and hash pinned.')
        if not set(function.get('required_fields') or []) <= set(catalog['fields']):
            _fail('Specialized function required field is not registered.', {'function_id': marker[0]})

def _nested_identity_values(value: Any, identity_key: str) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        if isinstance(value.get(identity_key), str):
            result.add(str(value[identity_key]))
        for child in value.values():
            result.update(_nested_identity_values(child, identity_key))
    elif isinstance(value, list):
        for child in value:
            result.update(_nested_identity_values(child, identity_key))
    return result

def _semantic_types_compatible(left: Any, right: Any) -> bool:
    left_value = str(left or '').casefold()
    right_value = str(right or '').casefold()
    if not left_value or not right_value:
        return False
    return left_value == right_value or (left_value in NUMERIC_SEMANTIC_TYPES and right_value in NUMERIC_SEMANTIC_TYPES) or (left_value in TEXTUAL_SEMANTIC_TYPES and right_value in TEXTUAL_SEMANTIC_TYPES)

def _recipe_operations(value: Any) -> list[str]:
    operations: list[str] = []
    if isinstance(value, dict):
        if isinstance(value.get('op'), str):
            operations.append(str(value['op']))
        for key, child in value.items():
            if key in {'pseudocode', 'description', 'aliases'}:
                continue
            operations.extend(_recipe_operations(child))
    elif isinstance(value, list):
        for child in value:
            operations.extend(_recipe_operations(child))
    return operations

def _map_legacy_recipe_ops(value: Any) -> Any:
    if isinstance(value, dict):
        result = {key: _map_legacy_recipe_ops(child) for key, child in value.items()}
        legacy = str(result.get('op') or '')
        mapped = {'detail': 'project', 'enrich_previous_result': 'join'}.get(legacy)
        if mapped:
            result['legacy_op'] = legacy
            result['op'] = mapped
        return result
    if isinstance(value, list):
        return [_map_legacy_recipe_ops(child) for child in value]
    return deepcopy(value)

def _identity_cards(value: Any, identity_key: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in sorted(dict(value or {})):
        card = deepcopy(dict(dict(value or {})[key]))
        existing_identity = card.get(identity_key)
        if existing_identity not in (None, '', key):
            card.setdefault('legacy_identity', existing_identity)
        card[identity_key] = key
        result[key] = card
    return result

def _reject_executable_or_secret_payload(value: Any, path: tuple[str, ...]=()) -> None:
    if isinstance(value, dict):
        for raw_key, child in value.items():
            key = str(raw_key).strip().casefold()
            location = '.'.join((*path, str(raw_key)))
            identity_key = bool(path) and str(path[-1]).casefold() in IDENTITY_CONTAINER_KEYS
            if not identity_key:
                if key in FORBIDDEN_EXECUTABLE_KEYS:
                    _fail('authoring draft에는 실행 코드/자유 query를 저장할 수 없습니다.', {'path': location})
                if key in QUERY_TEMPLATE_KEYS:
                    allowed_query_path = key == 'query_template' and len(path) == 3 and (str(path[0]).casefold() == 'datasets') and (str(path[2]).casefold() == 'source_config')
                    if not allowed_query_path or not isinstance(child, str):
                        _fail('query_template is only allowed at datasets.<id>.source_config.query_template.', {'path': location})
                    validate_read_only_query_template(child)
                if any((part in key for part in SECRET_KEY_PARTS if part != 'token' or key not in ALLOWED_NON_SECRET_TOKEN_KEYS)):
                    _fail('authoring draft에는 secret/credential 값을 저장할 수 없습니다.', {'path': location})
            _reject_executable_or_secret_payload(child, (*path, str(raw_key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_executable_or_secret_payload(child, (*path, str(index)))
    elif isinstance(value, str):
        for pattern_id, pattern in SECRET_SCALAR_PATTERNS:
            if pattern.search(value):
                _fail('authoring draft에는 secret/credential 값을 저장할 수 없습니다.', {'path': '.'.join(path), 'pattern_id': pattern_id})

def _default_coercion(semantic_type: str) -> str:
    normalized = semantic_type.casefold()
    if normalized in {'number', 'quantity', 'currency', 'rate', 'integer'}:
        return 'strict_number' if normalized != 'integer' else 'strict_integer'
    if normalized in {'localdate', 'date'}:
        return 'strict_date'
    if normalized in {'localdatetime', 'datetime'}:
        return 'strict_datetime'
    return 'string'

def _identity(value: str, label: str, pattern: re.Pattern[str]) -> str:
    normalized = str(value or '').strip().casefold()
    if not pattern.fullmatch(normalized):
        _fail(f'{label} 형식이 올바르지 않습니다.', {label: value})
    return normalized

def _assert_v6_collection(actual: str, expected: str) -> None:
    if actual != expected or not actual.startswith('agent_v6_'):
        raise ValueError(f'collection boundary violation: expected {expected}')

def _find_one(collection: Any, query: dict[str, Any]) -> dict[str, Any] | None:
    result = collection.find_one(query)
    return deepcopy(result) if isinstance(result, dict) else None

def _fail(message: str, details: Mapping[str, Any] | None=None) -> None:
    raise ContractError('metadata_dependency_error', 'metadata_domain_compile', message, dict(details or {}))
__all__ = ['ACTIVE_POINTER_COLLECTION', 'ACTIVE_POINTER_VERSION', 'AUTHORING_DRAFT_VERSION', 'DOMAIN_COMPILER_VERSION', 'DOMAIN_PACKAGE_COLLECTION', 'DOMAIN_PACKAGE_VERSION', 'MIGRATION_QUARANTINE_COLLECTION', 'RUNTIME_CATALOG_V2', 'adapt_legacy_catalog_v1', 'apply_dataset_source_configs_from_text', 'build_runtime_catalog_v2', 'compile_domain_package', 'compute_bundle_sha256', 'compute_package_sha256', 'compute_runtime_catalog_v2_sha256', 'load_active_domain_bundle', 'load_domain_package_file', 'make_active_pointer', 'make_active_pointer_document', 'make_bundle_document', 'query_template_parameters', 'validate_domain_package', 'validate_read_only_query_template', 'validate_runtime_catalog_v2']


from copy import deepcopy
from datetime import datetime, timezone
import json
import re
from typing import Any, Mapping, Sequence
METADATA_SECTION_VERSION = 'metadata.item.v1'
METADATA_RELEASE_VERSION = 'runtime_only'
DOMAIN_METADATA_COLLECTION = 'agent_v6_domain_metadata'
TABLE_CATALOG_COLLECTION = 'agent_v6_table_catalog'
MAIN_FILTER_COLLECTION = 'agent_v6_main_filter'
METADATA_COLLECTIONS = {'domain': DOMAIN_METADATA_COLLECTION, 'table_catalog': TABLE_CATALOG_COLLECTION, 'main_filter': MAIN_FILTER_COLLECTION}
_COLLECTION_NAME_PATTERN = re.compile('^[A-Za-z][A-Za-z0-9_.-]{0,127}$')
_ITEM_KEYS = {'_id', 'section', 'key', 'natural_text', 'payload', 'updated_at'}
_DOMAIN_MAP_SECTIONS = ('metrics', 'entity_groups', 'grains', 'relations', 'orderings', 'predicates', 'recipes')
_ALIAS_PROVENANCE_TO_COLLECTION = {'domain': 'domain', 'table_catalog': 'table_catalog', 'main_filters': 'main_filter'}

def _fail(message: str, details: Mapping[str, Any] | None=None) -> None:
    raise ContractError('metadata_dependency_error', 'metadata_three_collection', message, deepcopy(dict(details or {})))

def _metadata_collection_names(domain_collection: Any, table_collection: Any, main_filter_collection: Any) -> dict[str, str]:
    actual = {'domain': str(domain_collection or '').strip(), 'table_catalog': str(table_collection or '').strip(), 'main_filter': str(main_filter_collection or '').strip()}
    invalid = [role for role, name in actual.items() if _COLLECTION_NAME_PATTERN.fullmatch(name) is None or name.casefold().startswith('system.')]
    if invalid or len(set(actual.values())) != 3:
        _fail('메타데이터 컬렉션 이름은 안전하고 서로 다른 세 이름이어야 합니다.', {'invalid_roles': invalid, 'actual': actual})
    return actual

def _clean_natural_text(value: Any) -> str:
    text = str(value or '').replace('\r\n', '\n').strip()
    return text[:2000]

def _source_texts(value: Mapping[str, Any] | None) -> dict[str, str]:
    raw = dict(value or {})
    return {'domain': str(raw.get('domain') or ''), 'table_catalog': str(raw.get('table_catalog') or raw.get('dataset') or ''), 'main_filter': str(raw.get('main_filter') or '')}

def _text_blocks(value: str) -> list[str]:
    text = str(value or '').replace('\r\n', '\n').strip()
    if not text:
        return []
    blocks = [item.strip() for item in re.split('\\n\\s*\\n+|(?=^#{1,6}\\s)', text, flags=re.M) if item.strip()]
    return blocks or [text]

def _payload_needles(value: Any, result: list[str] | None=None) -> list[str]:
    """Return only identity/alias phrases suitable for source-block matching.

    Execution settings such as a dataset family or aggregation name are
    intentionally ignored.  Matching those generic values can attach an
    unrelated worker paragraph to another metadata item.
    """
    found = result if result is not None else []
    if len(found) >= 64:
        return found
    if isinstance(value, Mapping):
        for name in ('aliases', 'display_name', 'target_key', 'metric_id', 'group_id', 'grain_id', 'relation_id', 'ordering_id', 'recipe_id', 'function_id', 'values', 'text'):
            if name in value:
                _payload_needles(value[name], found)
    elif isinstance(value, (list, tuple)):
        for child in value[:128]:
            _payload_needles(child, found)
    elif isinstance(value, str):
        text = value.strip()
        generic = {'true', 'false', 'string', 'number', 'integer', 'identifier', 'filter', 'group', 'join', 'project', 'output', 'sort', 'rank', 'metric', 'aggregate', 'sum', 'mean', 'min', 'max', 'field', 'dataset', 'domain', 'main_filters', 'ko-kr', 'asia/seoul'}
        if 2 <= len(text) <= 128 and text.casefold() not in generic:
            found.append(text.casefold())
    return list(dict.fromkeys(found))[:64]

def _natural_item_summary(section: str, key: str, payload: Any) -> str:
    value = dict(payload) if isinstance(payload, Mapping) else {}
    aliases = value.get('aliases') if isinstance(value.get('aliases'), list) else []
    alias_text = ', '.join((str(item) for item in aliases[:12] if str(item).strip()))
    if section == 'profile':
        display_name = str(value.get('display_name') or key)
        description = str(value.get('description') or '').strip()
        return _clean_natural_text(f'{display_name} 도메인을 등록합니다.' + (f' 설명: {description}' if description else ''))
    if section == 'datasets':
        display_name = str(value.get('display_name') or key)
        source_type = str(value.get('source_type') or '').strip()
        fields = ', '.join((str(item) for item in list((value.get('fields') or {}).keys())[:24]))
        return _clean_natural_text(f'{key} 데이터셋을 {display_name} 이름으로 등록합니다.' + (f' 데이터 원천은 {source_type}입니다.' if source_type else '') + (f' 주요 필드는 {fields}입니다.' if fields else ''))
    if section == 'aliases':
        target_type = str(value.get('target_type') or '항목')
        target_key = str(value.get('target_key') or key)
        card_values = value.get('values') if isinstance(value.get('values'), list) else []
        expressions = []
        for item in card_values:
            text = item.get('text') if isinstance(item, Mapping) else item
            if str(text or '').strip():
                expressions.append(str(text).strip())
        expression_text = ', '.join(expressions[:24])
        return _clean_natural_text(f'{target_type} {target_key}의 자연어 별칭을 등록합니다.' + (f' 인식 표현은 {expression_text}입니다.' if expression_text else ''))
    labels = {'metrics': '지표', 'entity_groups': '대상 그룹', 'grains': '분석 단위', 'relations': '조인 관계', 'orderings': '정렬 기준', 'predicates': '조건', 'recipes': '분석 방법', 'prompt_extensions': '특화 프롬프트', 'specialized_functions': '특화 함수', 'output_profile': '출력 설정'}
    label = labels.get(section, section)
    summary = f'{key} {label} 항목을 등록합니다.'
    if alias_text:
        summary += f' 인식 표현은 {alias_text}입니다.'
    elif value:
        compact = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        summary += f' 설정은 {compact[:1200]}입니다.'
    return _clean_natural_text(summary)

def _natural_text_for_item(source_text: str, section: str, key: str, payload: Any) -> str:
    blocks = _text_blocks(source_text)
    needles = [str(key).casefold()]
    if ':' in str(key):
        needles.append(str(key).split(':', 1)[1].casefold())
    for block in blocks:
        folded = block.casefold()
        if any((needle and needle in folded for needle in needles)):
            return _clean_natural_text(block)
    payload_needles = _payload_needles(payload)
    scored = sorted(((sum((1 for needle in payload_needles if needle and needle in block.casefold())), -len(block), block) for block in blocks), reverse=True)
    if scored and scored[0][0] > 0:
        return _clean_natural_text(scored[0][2])
    return _natural_item_summary(section, key, payload)

def _legacy_natural_text(legacy: Mapping[str, Any] | None, *, document_id: str, section: str, key: str) -> str:
    values = dict(legacy or {})
    folded_values = {str(marker).casefold(): value for marker, value in values.items()}
    for marker in (document_id, f'{section}:{key}', key):
        if marker in values:
            return _clean_natural_text(values[marker])
        if marker.casefold() in folded_values:
            return _clean_natural_text(folded_values[marker.casefold()])
    return ''

def _item_document(collection_kind: str, section: str, key: str, payload: Any, *, source_text: str, legacy_natural_texts: Mapping[str, Any] | None, updated_at: str) -> dict[str, Any]:
    item_key = str(key or '').strip()
    if not item_key:
        _fail('메타데이터 항목 key가 비어 있습니다.', {'section': section})
    document_id = f'{collection_kind}:{section}:{item_key}'
    natural_text = _legacy_natural_text(legacy_natural_texts, document_id=document_id, section=section, key=item_key) or _natural_text_for_item(source_text, section, item_key, payload)
    return {'_id': document_id, 'section': str(section), 'key': item_key, 'natural_text': natural_text, 'payload': deepcopy(payload), 'updated_at': str(updated_at)}

def make_metadata_item_documents(package: Mapping[str, Any], source_texts: Mapping[str, Any] | None, *, legacy_natural_texts: Mapping[str, Any] | None=None, updated_at: str | None=None) -> dict[str, list[dict[str, Any]]]:
    """Split a validated package into independently editable MongoDB items."""
    validated = validate_domain_package(package)
    catalog = deepcopy(validated['runtime_catalog'])
    sources = _source_texts(source_texts)
    timestamp = str(updated_at or datetime.now(timezone.utc).isoformat())
    documents: dict[str, list[dict[str, Any]]] = {'domain': [], 'table_catalog': [], 'main_filter': []}
    profile = {'display_name': str(catalog.get('display_name') or validated['domain_id']), 'description': str(catalog.get('description') or ''), 'locale': str(catalog.get('locale') or 'ko-KR'), 'timezone': str(catalog.get('timezone') or 'Asia/Seoul')}
    documents['domain'].append(_item_document('domain', 'profile', str(validated['domain_id']), profile, source_text=sources['domain'], legacy_natural_texts=legacy_natural_texts, updated_at=timestamp))
    for section in _DOMAIN_MAP_SECTIONS:
        values = catalog.get(section) if isinstance(catalog.get(section), dict) else {}
        for key in sorted(values):
            documents['domain'].append(_item_document('domain', section, key, values[key], source_text=sources['domain'], legacy_natural_texts=legacy_natural_texts, updated_at=timestamp))
    prompt_extensions = catalog.get('prompt_extensions') if isinstance(catalog.get('prompt_extensions'), dict) else {}
    for key in ('intent', 'answer'):
        documents['domain'].append(_item_document('domain', 'prompt_extensions', key, {'text': str(prompt_extensions.get(key) or '')}, source_text=sources['domain'], legacy_natural_texts=legacy_natural_texts, updated_at=timestamp))
    for item in catalog.get('specialized_functions') or []:
        function = deepcopy(dict(item))
        key = f"{function.get('function_id')}:{int(function.get('version') or 1)}"
        documents['domain'].append(_item_document('domain', 'specialized_functions', key, function, source_text=sources['domain'], legacy_natural_texts=legacy_natural_texts, updated_at=timestamp))
    documents['domain'].append(_item_document('domain', 'output_profile', 'default', catalog.get('output_profile') or {}, source_text=sources['domain'], legacy_natural_texts=legacy_natural_texts, updated_at=timestamp))
    datasets = catalog.get('datasets') if isinstance(catalog.get('datasets'), dict) else {}
    for key in sorted(datasets):
        payload = deepcopy(datasets[key])
        payload.pop('key', None)
        documents['table_catalog'].append(_item_document('table_catalog', 'datasets', key, payload, source_text=sources['table_catalog'], legacy_natural_texts=legacy_natural_texts, updated_at=timestamp))
    aliases = catalog.get('aliases') if isinstance(catalog.get('aliases'), dict) else {}
    for key in sorted(aliases):
        card = deepcopy(aliases[key])
        target = _ALIAS_PROVENANCE_TO_COLLECTION.get(str(card.get('provenance_source') or ''), 'domain')
        documents[target].append(_item_document(target, 'aliases', key, card, source_text=sources[target], legacy_natural_texts=legacy_natural_texts, updated_at=timestamp))
    return documents

def _validated_item(document: Mapping[str, Any], expected_prefix: str) -> dict[str, Any]:
    value = deepcopy(dict(document))
    unknown = set(value) - _ITEM_KEYS
    missing = _ITEM_KEYS - set(value)
    if unknown or missing:
        _fail('메타데이터 항목 문서 형식이 올바르지 않습니다.', {'unknown': sorted(unknown), 'missing': sorted(missing)})
    section = str(value.get('section') or '').strip()
    key = str(value.get('key') or '').strip()
    if not section or not key or value.get('_id') != f'{expected_prefix}:{section}:{key}':
        _fail('메타데이터 항목 ID와 section/key가 일치하지 않습니다.', {'_id': value.get('_id')})
    if not isinstance(value.get('payload'), dict):
        _fail('메타데이터 항목 payload는 object여야 합니다.', {'_id': value.get('_id')})
    if not isinstance(value.get('natural_text'), str):
        _fail('메타데이터 자연어 입력은 문자열이어야 합니다.', {'_id': value.get('_id')})
    return value

def assemble_domain_package_from_items(documents: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    """Compile three simple item collections into the typed runtime package."""
    values = {kind: [_validated_item(item, kind) for item in documents.get(kind, [])] for kind in ('domain', 'table_catalog', 'main_filter')}
    profiles = [item for item in values['domain'] if item['section'] == 'profile']
    if len(profiles) != 1:
        _fail('도메인 프로필 항목은 정확히 하나여야 합니다.', {'profile_count': len(profiles)})
    profile = profiles[0]
    domain_id = str(profile['key'])
    profile_payload = deepcopy(profile['payload'])
    draft: dict[str, Any] = {'contract_version': 'metadata.authoring.draft.v1', 'display_name': str(profile_payload.get('display_name') or domain_id), 'description': str(profile_payload.get('description') or ''), 'locale': str(profile_payload.get('locale') or 'ko-KR'), 'timezone': str(profile_payload.get('timezone') or 'Asia/Seoul'), 'datasets': {}, 'metrics': {}, 'entity_groups': {}, 'grains': {}, 'relations': {}, 'orderings': {}, 'predicates': {}, 'recipes': {}, 'aliases': {}, 'prompt_extensions': {'intent': '', 'answer': ''}, 'specialized_functions': [], 'output_profile': {}}
    seen: set[tuple[str, str, str]] = set()
    for collection_kind, items in values.items():
        for item in items:
            marker = (collection_kind, item['section'], item['key'])
            if marker in seen:
                _fail('중복된 메타데이터 항목이 있습니다.', {'item': marker})
            seen.add(marker)
            section = item['section']
            key = item['key']
            payload = deepcopy(item['payload'])
            if collection_kind == 'domain' and section in _DOMAIN_MAP_SECTIONS:
                draft[section][key] = payload
            elif collection_kind == 'table_catalog' and section == 'datasets':
                draft['datasets'][key] = payload
            elif section == 'aliases':
                draft['aliases'][key] = payload
            elif collection_kind == 'domain' and section == 'prompt_extensions' and (key in {'intent', 'answer'}):
                draft['prompt_extensions'][key] = str(payload.get('text') or '')
            elif collection_kind == 'domain' and section == 'specialized_functions':
                draft['specialized_functions'].append(payload)
            elif collection_kind == 'domain' and section == 'output_profile' and (key == 'default'):
                draft['output_profile'] = payload
            elif collection_kind == 'domain' and section == 'profile':
                continue
            else:
                _fail('지원하지 않는 메타데이터 항목 section입니다.', {'collection': collection_kind, 'section': section, 'key': key})
    if not draft['datasets']:
        _fail('등록된 데이터셋 항목이 없습니다.')
    return compile_domain_package(draft, domain_id, 'production', revision=1, lifecycle_status='active')

def _find_items(collection: Any, session: Any=None) -> list[dict[str, Any]]:
    try:
        cursor = collection.find({}, session=session)
    except TypeError:
        cursor = collection.find()
    return [deepcopy(dict(item)) for item in cursor if isinstance(item, Mapping)]

def load_available_domain_package_from_three_collections(database: Any, *, domain_collection: str=DOMAIN_METADATA_COLLECTION, table_collection: str=TABLE_CATALOG_COLLECTION, main_filter_collection: str=MAIN_FILTER_COLLECTION, session: Any=None) -> dict[str, Any]:
    actual = _metadata_collection_names(domain_collection, table_collection, main_filter_collection)
    documents = {kind: _find_items(database[name], session=session) for kind, name in actual.items()}
    missing = [kind for kind, items in documents.items() if not items]
    if missing:
        _fail('필수 메타데이터 컬렉션에 등록 항목이 없습니다.', {'missing_collections': missing})
    return assemble_domain_package_from_items(documents)

def load_domain_package_from_three_collections(database: Any, domain_id: str, environment: str, *, domain_collection: str=DOMAIN_METADATA_COLLECTION, table_collection: str=TABLE_CATALOG_COLLECTION, main_filter_collection: str=MAIN_FILTER_COLLECTION, session: Any=None) -> dict[str, Any]:
    package = load_available_domain_package_from_three_collections(database, domain_collection=domain_collection, table_collection=table_collection, main_filter_collection=main_filter_collection, session=session)
    if domain_id and package['domain_id'] != str(domain_id):
        _fail('요청한 도메인과 등록된 도메인 프로필이 다릅니다.')
    if environment and str(environment) != 'production':
        _fail('항목형 메타데이터의 실행 환경은 production으로 고정됩니다.')
    return package

def replace_metadata_items(database: Any, documents: Mapping[str, Sequence[Mapping[str, Any]]], *, session: Any=None, domain_collection: str=DOMAIN_METADATA_COLLECTION, table_collection: str=TABLE_CATALOG_COLLECTION, main_filter_collection: str=MAIN_FILTER_COLLECTION) -> None:
    """Replace the three item sets after a complete in-memory compile check."""
    actual = _metadata_collection_names(domain_collection, table_collection, main_filter_collection)
    prepared = {kind: [_validated_item(item, kind) for item in documents.get(kind, [])] for kind in actual}
    assemble_domain_package_from_items(prepared)
    for kind, collection_name in actual.items():
        collection = database[collection_name]
        existing = {str(item.get('_id')): item for item in _find_items(collection, session=session)}
        items = []
        for source in prepared[kind]:
            document = deepcopy(source)
            if not document.get('natural_text') and isinstance(existing.get(document['_id']), dict):
                document['natural_text'] = _clean_natural_text(existing[document['_id']].get('natural_text'))
            items.append(document)
        ids = [item['_id'] for item in items]
        collection.delete_many({'_id': {'$nin': ids}}, session=session)
        for document in items:
            collection.replace_one({'_id': document['_id']}, document, upsert=True, session=session)
make_metadata_section_documents = make_metadata_item_documents
replace_metadata_release = replace_metadata_items

def assemble_domain_package_from_sections(documents: Mapping[str, Sequence[Mapping[str, Any]]], domain_id: str='', environment: str='production') -> dict[str, Any]:
    package = assemble_domain_package_from_items(documents)
    if domain_id and package['domain_id'] != str(domain_id):
        _fail('요청한 도메인과 등록된 도메인 프로필이 다릅니다.')
    if environment and str(environment) != 'production':
        _fail('항목형 메타데이터의 실행 환경은 production으로 고정됩니다.')
    return package
__all__ = ['DOMAIN_METADATA_COLLECTION', 'MAIN_FILTER_COLLECTION', 'METADATA_COLLECTIONS', 'METADATA_RELEASE_VERSION', 'METADATA_SECTION_VERSION', 'TABLE_CATALOG_COLLECTION', 'assemble_domain_package_from_items', 'assemble_domain_package_from_sections', 'load_available_domain_package_from_three_collections', 'load_domain_package_from_three_collections', 'make_metadata_item_documents', 'make_metadata_section_documents', 'replace_metadata_items', 'replace_metadata_release']


EMBEDDED_RUNTIME_CATALOG = json.loads('{"aliases":{"dataset:eqp_uph":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"eqp_uph","target_type":"dataset","values":[{"priority":100,"text":"UPH"},{"priority":100,"text":"시간당 생산량"}]},"dataset:equipment_assign":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"equipment_assign","target_type":"dataset","values":[{"priority":100,"text":"장비 배정"},{"priority":100,"text":"장비 현황"},{"priority":100,"text":"설비 대수"}]},"dataset:hold_history":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"hold_history","target_type":"dataset","values":[{"priority":100,"text":"HOLD 이력"},{"priority":100,"text":"HOLD 발생 시각"}]},"dataset:lot_status":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"lot_status","target_type":"dataset","values":[{"priority":100,"text":"현재 LOT"},{"priority":100,"text":"LOT 현황"},{"priority":100,"text":"HOLD LOT"}]},"dataset:product_master":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"product_master","target_type":"dataset","values":[{"priority":100,"text":"product master"},{"priority":100,"text":"제품 master"},{"priority":100,"text":"제품 기준정보"},{"priority":100,"text":"제품 마스터"}]},"dataset:production":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"production","target_type":"dataset","values":[{"priority":100,"text":"production"},{"priority":100,"text":"production 데이터"},{"priority":100,"text":"이력 생산"},{"priority":100,"text":"생산 실적"},{"priority":100,"text":"OUTPUT"},{"priority":100,"text":"OUT"}]},"dataset:production_today":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"production_today","target_type":"dataset","values":[{"priority":100,"text":"당일 생산"},{"priority":100,"text":"오늘 생산"},{"priority":100,"text":"현재 생산"}]},"dataset:target":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"target","target_type":"dataset","values":[{"priority":100,"text":"계획"},{"priority":100,"text":"스케줄"},{"priority":100,"text":"스케쥴"},{"priority":100,"text":"SCHD"},{"priority":100,"text":"생산목표"}]},"dataset:wip":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"wip","target_type":"dataset","values":[{"priority":100,"text":"이력 재공"},{"priority":100,"text":"아침 재공"},{"priority":100,"text":"BOH 재공"},{"priority":100,"text":"BOH"}]},"dataset:wip_today":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"wip_today","target_type":"dataset","values":[{"priority":100,"text":"현재 재공"},{"priority":100,"text":"지금 재공"},{"priority":100,"text":"금일 현재 재공"}]},"field:BASE_DATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"BASE_DATE","target_type":"field","values":[{"priority":100,"text":"BASE_DATE"}]},"field:BAY_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"BAY_ID","target_type":"field","values":[{"priority":100,"text":"BAY_ID"}]},"field:CUM_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"CUM_TAT","target_type":"field","values":[{"priority":100,"text":"CUM_TAT"}]},"field:DATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DATE","target_type":"field","values":[{"priority":100,"text":"날짜"},{"priority":100,"text":"일자"},{"priority":100,"text":"기준일"},{"priority":100,"text":"작업일"},{"priority":100,"text":"date"},{"priority":100,"text":"work date"}]},"field:DEN":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DEN","target_type":"field","values":[{"priority":100,"text":"DEN"},{"priority":100,"text":"DENSITY"},{"priority":100,"text":"제품 용량"}]},"field:DEVICE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DEVICE","target_type":"field","values":[{"priority":100,"text":"DEVICE"},{"priority":100,"text":"DEVICE CODE"},{"priority":100,"text":"첨자"}]},"field:DEVICE_DESC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DEVICE_DESC","target_type":"field","values":[{"priority":100,"text":"DEVICE_DESC"},{"priority":100,"text":"제품 설명"}]},"field:DIE_ATTACH_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DIE_ATTACH_QTY","target_type":"field","values":[{"priority":100,"text":"DIE_ATTACH_QTY"}]},"field:EQP_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"EQP_ID","target_type":"field","values":[{"priority":100,"text":"EQP_ID"},{"priority":100,"text":"EQPID"},{"priority":100,"text":"장비 ID"}]},"field:EQP_MODEL":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"EQP_MODEL","target_type":"field","values":[{"priority":100,"text":"EQP_MODEL"},{"priority":100,"text":"equipment model"},{"priority":100,"text":"장비 모델"},{"priority":100,"text":"장비 기종"},{"priority":100,"text":"설비 모델"},{"priority":100,"text":"설비 기종"}]},"field:FAB":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FAB","target_type":"field","values":[{"priority":100,"text":"FAB"}]},"field:FACTORY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FACTORY","target_type":"field","values":[{"priority":100,"text":"FACTORY"}]},"field:FAC_IN_AT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FAC_IN_AT","target_type":"field","values":[{"priority":100,"text":"FAC_IN_AT"}]},"field:FAMILY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FAMILY","target_type":"field","values":[{"priority":100,"text":"FAMILY"}]},"field:HOLD_CD":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_CD","target_type":"field","values":[{"priority":100,"text":"HOLD_CD"}]},"field:HOLD_DESC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_DESC","target_type":"field","values":[{"priority":100,"text":"HOLD_DESC"}]},"field:HOLD_EVENT_AT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_EVENT_AT","target_type":"field","values":[{"priority":100,"text":"HOLD_EVENT_AT"}]},"field:HOLD_REASON":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_REASON","target_type":"field","values":[{"priority":100,"text":"HOLD_REASON"}]},"field:HOLD_STAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_STAT","target_type":"field","values":[{"priority":100,"text":"HOLD_STAT"}]},"field:INPUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"INPUT_PLAN_QTY","target_type":"field","values":[{"priority":100,"text":"INPUT_PLAN_QTY"}]},"field:IN_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"IN_TAT","target_type":"field","values":[{"priority":100,"text":"IN_TAT"}]},"field:LEAD":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LEAD","target_type":"field","values":[{"priority":100,"text":"LEAD"},{"priority":100,"text":"lead count"}]},"field:LOAD_DATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LOAD_DATE","target_type":"field","values":[{"priority":100,"text":"LOAD_DATE"}]},"field:LOT_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LOT_ID","target_type":"field","values":[{"priority":100,"text":"LOT_ID"},{"priority":100,"text":"Lot ID"}]},"field:LOT_STAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LOT_STAT","target_type":"field","values":[{"priority":100,"text":"LOT_STAT"}]},"field:MCP_NO":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"MCP_NO","target_type":"field","values":[{"priority":100,"text":"MCP_NO"},{"priority":100,"text":"MCP NO"},{"priority":100,"text":"MCP_SALES_NO"},{"priority":100,"text":"MCP_SALE_CD"},{"priority":100,"text":"MCPSALENO"}]},"field:MODE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"MODE","target_type":"field","values":[{"priority":100,"text":"MODE"},{"priority":100,"text":"Mode"},{"priority":100,"text":"mode"},{"priority":100,"text":"제품 모드"}]},"field:NETDIE_300_CNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"NETDIE_300_CNT","target_type":"field","values":[{"priority":100,"text":"NETDIE_300_CNT"}]},"field:OPER_IN_AT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OPER_IN_AT","target_type":"field","values":[{"priority":100,"text":"OPER_IN_AT"}]},"field:OPER_NAME":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"OPER_NAME","target_type":"field","values":[{"priority":100,"text":"OPER_NAME"},{"priority":100,"text":"공정"},{"priority":100,"text":"작업공정"},{"priority":100,"text":"operation"},{"priority":100,"text":"process"},{"priority":100,"text":"oper name"},{"priority":100,"text":"세부 공정별"},{"priority":100,"text":"공정별"}]},"field:OPER_NUM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OPER_NUM","target_type":"field","values":[{"priority":100,"text":"공정번호"},{"priority":100,"text":"공정 차수"},{"priority":100,"text":"차수별"},{"priority":100,"text":"oper num"},{"priority":100,"text":"oper no"}]},"field:OPER_SEQ":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OPER_SEQ","target_type":"field","values":[{"priority":100,"text":"OPER_SEQ"}]},"field:ORG":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"ORG","target_type":"field","values":[{"priority":100,"text":"ORG"},{"priority":100,"text":"조직"},{"priority":100,"text":"organization code"}]},"field:OUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OUT_PLAN_QTY","target_type":"field","values":[{"priority":100,"text":"OUT_PLAN_QTY"}]},"field:PKG_TYPE1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PKG_TYPE1","target_type":"field","values":[{"priority":100,"text":"PKG_TYPE1"},{"priority":100,"text":"PKG1"},{"priority":100,"text":"package type 1"}]},"field:PKG_TYPE2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PKG_TYPE2","target_type":"field","values":[{"priority":100,"text":"PKG_TYPE2"},{"priority":100,"text":"PKG2"},{"priority":100,"text":"package type 2"}]},"field:PRESS_CNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PRESS_CNT","target_type":"field","values":[{"priority":100,"text":"PRESS_CNT"}]},"field:PRODUCTION_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PRODUCTION_QTY","target_type":"field","values":[{"priority":100,"text":"PRODUCTION_QTY"}]},"field:PROD_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PROD_QTY","target_type":"field","values":[{"priority":100,"text":"PROD_QTY"}]},"field:RECIPE_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"RECIPE_ID","target_type":"field","values":[{"priority":100,"text":"RECIPE_ID"},{"priority":100,"text":"Recipe ID"},{"priority":100,"text":"레시피"}]},"field:SHIFT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT","target_type":"field","values":[{"priority":100,"text":"SHIFT"}]},"field:TECH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"TECH","target_type":"field","values":[{"priority":100,"text":"TECH"},{"priority":100,"text":"제품 기술"}]},"field:TSV_DIE_TYP":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"TSV_DIE_TYP","target_type":"field","values":[{"priority":100,"text":"TSV_DIE_TYP"},{"priority":100,"text":"HBM"},{"priority":100,"text":"3DS"},{"priority":100,"text":"TSV"}]},"field:UPH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"UPH","target_type":"field","values":[{"priority":100,"text":"UPH"}]},"field:WF_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"WF_QTY","target_type":"field","values":[{"priority":100,"text":"WF_QTY"}]},"field:WIP_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"WIP_QTY","target_type":"field","values":[{"priority":100,"text":"WIP_QTY"}]},"field:YIELD_RATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"YIELD_RATE","target_type":"field","values":[{"priority":100,"text":"YIELD_RATE"},{"priority":100,"text":"YIELD RATE"},{"priority":100,"text":"수율"}]},"metric:ACHIEVEMENT_RATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"ACHIEVEMENT_RATE","target_type":"metric","values":[{"priority":100,"text":"생산달성률"},{"priority":100,"text":"생산달성율"},{"priority":100,"text":"달성률"},{"priority":100,"text":"달성율"}]},"metric:CUM_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"CUM_TAT","target_type":"metric","values":[{"priority":100,"text":"CUM TAT"},{"priority":100,"text":"누적 TAT"}]},"metric:EQP_COUNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"EQP_COUNT","target_type":"metric","values":[{"priority":100,"text":"장비 대수"},{"priority":100,"text":"설비 대수"},{"priority":100,"text":"장비 수"},{"priority":100,"text":"몇 대"}]},"metric:HOLD_DURATION_HOURS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"HOLD_DURATION_HOURS","target_type":"metric","values":[{"priority":100,"text":"HOLD_DURATION_HOURS"}]},"metric:INPUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"INPUT_PLAN_QTY","target_type":"metric","values":[{"priority":100,"text":"INPUT 계획"},{"priority":100,"text":"투입계획"}]},"metric:INPUT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"INPUT_QTY","target_type":"metric","values":[{"priority":100,"text":"투입량"},{"priority":100,"text":"INPUT"},{"priority":100,"text":"input"},{"priority":100,"text":"INPUT 수량"},{"priority":100,"text":"INPUT실적"},{"priority":100,"text":"INPUT 실적"},{"priority":100,"text":"INPUT생산량"},{"priority":100,"text":"투입 실적"},{"priority":100,"text":"INPUT_QTY"}]},"metric:IN_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"IN_TAT","target_type":"metric","values":[{"priority":100,"text":"IN TAT"},{"priority":100,"text":"현재 공정 TAT"},{"priority":100,"text":"현재 TAT"}]},"metric:LOT_COUNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"LOT_COUNT","target_type":"metric","values":[{"priority":100,"text":"LOT 건수"},{"priority":100,"text":"LOT 수"}]},"metric:OUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"OUT_PLAN_QTY","target_type":"metric","values":[{"priority":100,"text":"OUT 계획"},{"priority":100,"text":"TARGET"},{"priority":100,"text":"생산목표"}]},"metric:OUT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"OUT_QTY","target_type":"metric","values":[{"priority":100,"text":"OUT_QTY"}]},"metric:PKG_OUT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PKG_OUT_QTY","target_type":"metric","values":[{"priority":100,"text":"OUTPUT"},{"priority":100,"text":"OUT"},{"priority":100,"text":"Out Put"},{"priority":100,"text":"output 실적"},{"priority":100,"text":"out 실적"},{"priority":100,"text":"PKG OUT실적"},{"priority":100,"text":"PKG OUT 실적"}]},"metric:PRODUCTION_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PRODUCTION_QTY","target_type":"metric","values":[{"priority":100,"text":"생산량"},{"priority":100,"text":"생산실적"},{"priority":100,"text":"실적"},{"priority":100,"text":"PRODUCTION_QTY"}]},"metric:UNIT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"UNIT_QTY","target_type":"metric","values":[{"priority":100,"text":"UNIT 수량"},{"priority":100,"text":"DIE 수량"}]},"metric:UPH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"UPH","target_type":"metric","values":[{"priority":100,"text":"UPH"},{"priority":100,"text":"시간당 생산량"}]},"metric:WAFER_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WAFER_QTY","target_type":"metric","values":[{"priority":100,"text":"Wafer 수량"},{"priority":100,"text":"웨이퍼 수량"}]},"metric:WIP_BOH_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WIP_BOH_QTY","target_type":"metric","values":[{"priority":100,"text":"아침 재공"},{"priority":100,"text":"BOH 재공"},{"priority":100,"text":"BOH"},{"priority":100,"text":"07시 기준 재공"}]},"metric:WIP_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WIP_QTY","target_type":"metric","values":[{"priority":100,"text":"재공"},{"priority":100,"text":"재공수량"},{"priority":100,"text":"WIP"},{"priority":100,"text":"공정 물량"}]},"process:B/G1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"B/G1","target_type":"process","values":[{"priority":140,"text":"B/G1"},{"priority":140,"text":"BG1"},{"priority":140,"text":"B/G1공정"},{"priority":140,"text":"B/G1 공정"},{"priority":140,"text":"B/G 1차"},{"priority":140,"text":"B/G1차"},{"priority":140,"text":"BG 1차"},{"priority":140,"text":"BG1차"}]},"process:B/G2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"B/G2","target_type":"process","values":[{"priority":140,"text":"B/G2"},{"priority":140,"text":"BG2"},{"priority":140,"text":"B/G2공정"},{"priority":140,"text":"B/G2 공정"},{"priority":140,"text":"B/G 2차"},{"priority":140,"text":"B/G2차"},{"priority":140,"text":"BG 2차"},{"priority":140,"text":"BG2차"}]},"process:D/A1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A1","target_type":"process","values":[{"priority":140,"text":"D/A1"},{"priority":140,"text":"DA1"},{"priority":140,"text":"D/A1공정"},{"priority":140,"text":"D/A1 공정"},{"priority":140,"text":"D/A 1차"},{"priority":140,"text":"D/A1차"},{"priority":140,"text":"DA 1차"},{"priority":140,"text":"DA1차"}]},"process:D/A2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A2","target_type":"process","values":[{"priority":140,"text":"D/A2"},{"priority":140,"text":"DA2"},{"priority":140,"text":"D/A2공정"},{"priority":140,"text":"D/A2 공정"},{"priority":140,"text":"D/A 2차"},{"priority":140,"text":"D/A2차"},{"priority":140,"text":"DA 2차"},{"priority":140,"text":"DA2차"}]},"process:D/A3":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A3","target_type":"process","values":[{"priority":140,"text":"D/A3"},{"priority":140,"text":"DA3"},{"priority":140,"text":"D/A3공정"},{"priority":140,"text":"D/A3 공정"},{"priority":140,"text":"D/A 3차"},{"priority":140,"text":"D/A3차"},{"priority":140,"text":"DA 3차"},{"priority":140,"text":"DA3차"}]},"process:D/A4":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A4","target_type":"process","values":[{"priority":140,"text":"D/A4"},{"priority":140,"text":"DA4"},{"priority":140,"text":"D/A4공정"},{"priority":140,"text":"D/A4 공정"},{"priority":140,"text":"D/A 4차"},{"priority":140,"text":"D/A4차"},{"priority":140,"text":"DA 4차"},{"priority":140,"text":"DA4차"}]},"process:D/A5":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A5","target_type":"process","values":[{"priority":140,"text":"D/A5"},{"priority":140,"text":"DA5"},{"priority":140,"text":"D/A5공정"},{"priority":140,"text":"D/A5 공정"},{"priority":140,"text":"D/A 5차"},{"priority":140,"text":"D/A5차"},{"priority":140,"text":"DA 5차"},{"priority":140,"text":"DA5차"}]},"process:D/A6":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A6","target_type":"process","values":[{"priority":140,"text":"D/A6"},{"priority":140,"text":"DA6"},{"priority":140,"text":"D/A6공정"},{"priority":140,"text":"D/A6 공정"},{"priority":140,"text":"D/A 6차"},{"priority":140,"text":"D/A6차"},{"priority":140,"text":"DA 6차"},{"priority":140,"text":"DA6차"}]},"process:D/S1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/S1","target_type":"process","values":[{"priority":140,"text":"D/S1"},{"priority":140,"text":"DS1"},{"priority":140,"text":"D/S1공정"},{"priority":140,"text":"D/S1 공정"},{"priority":140,"text":"D/S 1차"},{"priority":140,"text":"D/S1차"},{"priority":140,"text":"DS 1차"},{"priority":140,"text":"DS1차"}]},"process:FCB/H":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB/H","target_type":"process","values":[{"priority":140,"text":"FCB/H"},{"priority":140,"text":"FCBH"},{"priority":140,"text":"FCB/H공정"},{"priority":140,"text":"FCB/H 공정"}]},"process:FCB1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB1","target_type":"process","values":[{"priority":140,"text":"FCB1"},{"priority":140,"text":"FCB1공정"},{"priority":140,"text":"FCB1 공정"},{"priority":140,"text":"FCB 1차"},{"priority":140,"text":"FCB1차"}]},"process:FCB2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB2","target_type":"process","values":[{"priority":140,"text":"FCB2"},{"priority":140,"text":"FCB2공정"},{"priority":140,"text":"FCB2 공정"},{"priority":140,"text":"FCB 2차"},{"priority":140,"text":"FCB2차"}]},"process:INPUT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"INPUT","target_type":"process","values":[{"priority":140,"text":"INPUT"},{"priority":140,"text":"INPUT공정"},{"priority":140,"text":"INPUT 공정"}]},"process:PKG OUT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PKG OUT","target_type":"process","values":[{"priority":140,"text":"PKG OUT"},{"priority":140,"text":"PKG OUT공정"},{"priority":140,"text":"PKG OUT 공정"}]},"process:SBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SBM","target_type":"process","values":[{"priority":140,"text":"SBM"},{"priority":140,"text":"SBM공정"},{"priority":140,"text":"SBM 공정"}]},"process:W/B1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B1","target_type":"process","values":[{"priority":140,"text":"W/B1"},{"priority":140,"text":"WB1"},{"priority":140,"text":"W/B1공정"},{"priority":140,"text":"W/B1 공정"},{"priority":140,"text":"W/B 1차"},{"priority":140,"text":"W/B1차"},{"priority":140,"text":"WB 1차"},{"priority":140,"text":"WB1차"}]},"process:W/B2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B2","target_type":"process","values":[{"priority":140,"text":"W/B2"},{"priority":140,"text":"WB2"},{"priority":140,"text":"W/B2공정"},{"priority":140,"text":"W/B2 공정"},{"priority":140,"text":"W/B 2차"},{"priority":140,"text":"W/B2차"},{"priority":140,"text":"WB 2차"},{"priority":140,"text":"WB2차"}]},"process:W/B3":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B3","target_type":"process","values":[{"priority":140,"text":"W/B3"},{"priority":140,"text":"WB3"},{"priority":140,"text":"W/B3공정"},{"priority":140,"text":"W/B3 공정"},{"priority":140,"text":"W/B 3차"},{"priority":140,"text":"W/B3차"},{"priority":140,"text":"WB 3차"},{"priority":140,"text":"WB3차"}]},"process:W/B4":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B4","target_type":"process","values":[{"priority":140,"text":"W/B4"},{"priority":140,"text":"WB4"},{"priority":140,"text":"W/B4공정"},{"priority":140,"text":"W/B4 공정"},{"priority":140,"text":"W/B 4차"},{"priority":140,"text":"W/B4차"},{"priority":140,"text":"WB 4차"},{"priority":140,"text":"WB4차"}]},"process:W/B5":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B5","target_type":"process","values":[{"priority":140,"text":"W/B5"},{"priority":140,"text":"WB5"},{"priority":140,"text":"W/B5공정"},{"priority":140,"text":"W/B5 공정"},{"priority":140,"text":"W/B 5차"},{"priority":140,"text":"W/B5차"},{"priority":140,"text":"WB 5차"},{"priority":140,"text":"WB5차"}]},"process:W/B6":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B6","target_type":"process","values":[{"priority":140,"text":"W/B6"},{"priority":140,"text":"WB6"},{"priority":140,"text":"W/B6공정"},{"priority":140,"text":"W/B6 공정"},{"priority":140,"text":"W/B 6차"},{"priority":140,"text":"W/B6차"},{"priority":140,"text":"WB 6차"},{"priority":140,"text":"WB6차"}]},"process:W/BM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/BM","target_type":"process","values":[{"priority":140,"text":"W/BM"},{"priority":140,"text":"WBM"},{"priority":140,"text":"W/BM공정"},{"priority":140,"text":"W/BM 공정"}]},"process_group:BG":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"BG","target_type":"process_group","values":[{"priority":100,"text":"BG"},{"priority":100,"text":"BG공정"},{"priority":100,"text":"BG 공정"},{"priority":100,"text":"B/G"},{"priority":100,"text":"B/G공정"},{"priority":100,"text":"B/G 공정"}]},"process_group:BM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"BM","target_type":"process_group","values":[{"priority":100,"text":"BM"},{"priority":100,"text":"BM공정"},{"priority":100,"text":"BM 공정"},{"priority":100,"text":"B/M"},{"priority":100,"text":"B/M공정"},{"priority":100,"text":"B/M 공정"},{"priority":100,"text":"비엠"},{"priority":100,"text":"비엠공정"},{"priority":100,"text":"비엠 공정"}]},"process_group:DA":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DA","target_type":"process_group","values":[{"priority":100,"text":"DA"},{"priority":100,"text":"DA공정"},{"priority":100,"text":"DA 공정"},{"priority":100,"text":"D/A"},{"priority":100,"text":"D/A공정"},{"priority":100,"text":"D/A 공정"}]},"process_group:DC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DC","target_type":"process_group","values":[{"priority":100,"text":"DC"},{"priority":100,"text":"DC공정"},{"priority":100,"text":"DC 공정"},{"priority":100,"text":"D/C"},{"priority":100,"text":"D/C공정"},{"priority":100,"text":"D/C 공정"}]},"process_group:DI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DI","target_type":"process_group","values":[{"priority":100,"text":"DI"},{"priority":100,"text":"DI공정"},{"priority":100,"text":"DI 공정"},{"priority":100,"text":"D/I"},{"priority":100,"text":"D/I공정"},{"priority":100,"text":"D/I 공정"},{"priority":100,"text":"DVI"},{"priority":100,"text":"DVI공정"},{"priority":100,"text":"DVI 공정"}]},"process_group:DP":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DP","target_type":"process_group","values":[{"priority":100,"text":"DP"},{"priority":100,"text":"DP공정"},{"priority":100,"text":"DP 공정"},{"priority":100,"text":"D/P"},{"priority":100,"text":"D/P공정"},{"priority":100,"text":"D/P 공정"}]},"process_group:DS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DS","target_type":"process_group","values":[{"priority":100,"text":"DS"},{"priority":100,"text":"DS공정"},{"priority":100,"text":"DS 공정"},{"priority":100,"text":"D/S"},{"priority":100,"text":"D/S공정"},{"priority":100,"text":"D/S 공정"}]},"process_group:FCB":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB","target_type":"process_group","values":[{"priority":100,"text":"FCB"},{"priority":100,"text":"FCB공정"},{"priority":100,"text":"FCB 공정"}]},"process_group:FCBH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCBH","target_type":"process_group","values":[{"priority":100,"text":"FCBH"},{"priority":100,"text":"FCBH공정"},{"priority":100,"text":"FCBH 공정"},{"priority":100,"text":"FCB/H"},{"priority":100,"text":"FCB/H공정"},{"priority":100,"text":"FCB/H 공정"}]},"process_group:HS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"HS","target_type":"process_group","values":[{"priority":100,"text":"HS"},{"priority":100,"text":"HS공정"},{"priority":100,"text":"HS 공정"},{"priority":100,"text":"H/S"},{"priority":100,"text":"H/S공정"},{"priority":100,"text":"H/S 공정"}]},"process_group:LT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"LT","target_type":"process_group","values":[{"priority":100,"text":"LT"},{"priority":100,"text":"LT공정"},{"priority":100,"text":"LT 공정"},{"priority":100,"text":"L/T"},{"priority":100,"text":"L/T공정"},{"priority":100,"text":"L/T 공정"}]},"process_group:PC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PC","target_type":"process_group","values":[{"priority":100,"text":"PC"},{"priority":100,"text":"PC공정"},{"priority":100,"text":"PC 공정"},{"priority":100,"text":"P/C"},{"priority":100,"text":"P/C공정"},{"priority":100,"text":"P/C 공정"}]},"process_group:PCO":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PCO","target_type":"process_group","values":[{"priority":100,"text":"PCO"},{"priority":100,"text":"PCO공정"},{"priority":100,"text":"PCO 공정"}]},"process_group:PLH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PLH","target_type":"process_group","values":[{"priority":100,"text":"PLH"},{"priority":100,"text":"PLH공정"},{"priority":100,"text":"PLH 공정"},{"priority":100,"text":"P/L"},{"priority":100,"text":"P/L공정"},{"priority":100,"text":"P/L 공정"}]},"process_group:QCSPC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"QCSPC","target_type":"process_group","values":[{"priority":100,"text":"QCSPC"},{"priority":100,"text":"QCSPC공정"},{"priority":100,"text":"QCSPC 공정"}]},"process_group:SAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SAT","target_type":"process_group","values":[{"priority":100,"text":"SAT"},{"priority":100,"text":"SAT공정"},{"priority":100,"text":"SAT 공정"}]},"process_group:SBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SBM","target_type":"process_group","values":[{"priority":100,"text":"SBM"},{"priority":100,"text":"SBM공정"},{"priority":100,"text":"SBM 공정"}]},"process_group:SG":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SG","target_type":"process_group","values":[{"priority":100,"text":"SG"},{"priority":100,"text":"SG공정"},{"priority":100,"text":"SG 공정"},{"priority":100,"text":"S/G"},{"priority":100,"text":"S/G공정"},{"priority":100,"text":"S/G 공정"}]},"process_group:WB":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WB","target_type":"process_group","values":[{"priority":100,"text":"WB"},{"priority":100,"text":"WB공정"},{"priority":100,"text":"WB 공정"},{"priority":100,"text":"W/B"},{"priority":100,"text":"W/B공정"},{"priority":100,"text":"W/B 공정"}]},"process_group:WBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WBM","target_type":"process_group","values":[{"priority":120,"text":"WBM"},{"priority":120,"text":"WBM공정"},{"priority":120,"text":"WBM 공정"},{"priority":120,"text":"W/BM"},{"priority":120,"text":"W/BM공정"},{"priority":120,"text":"W/BM 공정"}]},"process_group:WEC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WEC","target_type":"process_group","values":[{"priority":100,"text":"WEC"},{"priority":100,"text":"WEC공정"},{"priority":100,"text":"WEC 공정"}]},"process_group:WET":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WET","target_type":"process_group","values":[{"priority":100,"text":"WET"},{"priority":100,"text":"WET공정"},{"priority":100,"text":"WET 공정"}]},"process_group:WLS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WLS","target_type":"process_group","values":[{"priority":100,"text":"WLS"},{"priority":100,"text":"WLS공정"},{"priority":100,"text":"WLS 공정"}]},"process_group:WS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WS","target_type":"process_group","values":[{"priority":100,"text":"WS"},{"priority":100,"text":"WS공정"},{"priority":100,"text":"WS 공정"},{"priority":100,"text":"W/S"},{"priority":100,"text":"W/S공정"},{"priority":100,"text":"W/S 공정"}]},"process_group:WSD":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WSD","target_type":"process_group","values":[{"priority":100,"text":"WSD"},{"priority":100,"text":"WSD공정"},{"priority":100,"text":"WSD 공정"}]},"product_group:AUTO":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"AUTO","target_type":"product_group","values":[{"priority":100,"text":"AUTO향"},{"priority":100,"text":"오토모티브향"},{"priority":100,"text":"오토향"}]},"product_group:HBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"HBM","target_type":"product_group","values":[{"priority":100,"text":"HBM"},{"priority":100,"text":"3DS"},{"priority":100,"text":"TSV"}]},"product_group:MOBILE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"MOBILE","target_type":"product_group","values":[{"priority":100,"text":"Mobile"},{"priority":100,"text":"MOBILE"},{"priority":100,"text":"모바일"}]},"product_group:POP":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"POP","target_type":"product_group","values":[{"priority":100,"text":"POP"},{"priority":100,"text":"pop"},{"priority":100,"text":"Pop"}]},"product_group:STACK_2HI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"STACK_2HI","target_type":"product_group","values":[{"priority":100,"text":"2Hi"}]},"product_group:STACK_4HI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"STACK_4HI","target_type":"product_group","values":[{"priority":100,"text":"4Hi"}]},"product_group:STACK_8HI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"STACK_8HI","target_type":"product_group","values":[{"priority":100,"text":"8Hi"}]},"recipe:achievement.input_actual":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"achievement.input_actual","target_type":"recipe","values":[{"priority":100,"text":"생산달성률"},{"priority":100,"text":"생산달성율"},{"priority":100,"text":"INPUT 계획 대비 실적"}]},"recipe:equipment.assignment_enrich":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"equipment.assignment_enrich","target_type":"recipe","values":[{"priority":100,"text":"할당된 장비 대수와 LIST"},{"priority":100,"text":"장비 배정"},{"priority":100,"text":"장비 목록"}]},"recipe:equipment.assignment_uph":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"equipment.assignment_uph","target_type":"recipe","values":[{"priority":100,"text":"장비별 UPH"},{"priority":100,"text":"배정 장비 UPH"},{"priority":100,"text":"장비와 Recipe UPH"}]},"recipe:hold.oldest_current_history":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"hold.oldest_current_history","target_type":"recipe","values":[{"priority":100,"text":"HOLD 시간이 가장 오래된 LOT"},{"priority":100,"text":"오래된 HOLD 이력"}]},"recipe:join.operation.production_wip":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"join.operation.production_wip","target_type":"recipe","values":[{"priority":100,"text":"생산량과 재공수량"},{"priority":100,"text":"생산 WIP 비교"}]},"recipe:ordered.process.range":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"ordered.process.range","target_type":"recipe","values":[{"priority":100,"text":"공정 구간"},{"priority":100,"text":"공정 범위"},{"priority":100,"text":"OPER_SEQ 범위"}]},"recipe:presence.left_positive_right_zero":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"presence.left_positive_right_zero","target_type":"recipe","values":[{"priority":100,"text":"A는 있으나 B는 없음"},{"priority":100,"text":"실적 있음 재공 없음"},{"priority":100,"text":"존재 미존재"}]},"recipe:product.standard":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"product.standard","target_type":"recipe","values":[{"priority":100,"text":"제품별"},{"priority":100,"text":"제품 기준"},{"priority":100,"text":"제품 집계"}]},"recipe:rank.bottom_n":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"rank.bottom_n","target_type":"recipe","values":[{"priority":100,"text":"하위 N개"},{"priority":100,"text":"가장 적은"},{"priority":100,"text":"BOTTOM N"}]},"recipe:rank.top_n":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"rank.top_n","target_type":"recipe","values":[{"priority":100,"text":"상위 N개"},{"priority":100,"text":"가장 많은"},{"priority":100,"text":"TOP N"}]},"status:SHIFT_A":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT_A","target_type":"status","values":[{"priority":100,"text":"Shift A조"},{"priority":100,"text":"SHIFT A조"},{"priority":100,"text":"Shift A"},{"priority":100,"text":"A조"},{"priority":100,"text":"1조"},{"priority":100,"text":"07:00~15:00"}]},"status:SHIFT_B":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT_B","target_type":"status","values":[{"priority":100,"text":"Shift B조"},{"priority":100,"text":"SHIFT B조"},{"priority":100,"text":"Shift B"},{"priority":100,"text":"B조"},{"priority":100,"text":"2조"},{"priority":100,"text":"15:00~23:00"}]},"status:SHIFT_C":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT_C","target_type":"status","values":[{"priority":100,"text":"Shift C조"},{"priority":100,"text":"SHIFT C조"},{"priority":100,"text":"Shift C"},{"priority":100,"text":"C조"},{"priority":100,"text":"3조"},{"priority":100,"text":"23:00~07:00"}]}},"catalog_sha256":"1f8b6c1522b96425a6a46a3e4dfcf4c5b7c338c6bc0af3c2a0878806ea4a7f8e","contract_version":"metadata.runtime.catalog.v1","datasets":{"eqp_uph":{"config_ref":"config:oracle:GMS_DB@1","default_detail_fields":["EQP_MODEL","RECIPE_ID","OPER_NAME"],"family":"equipment_uph","fields":{"BASE_DATE":{"coercion":"strict_date","nullable":true,"physical_aliases":[],"physical_column":"BASE_DT","required_in_source":false,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"EQP_MODEL":{"coercion":"string","nullable":true,"physical_aliases":["EQP_MODEL"],"physical_column":"EQUIP_MODEL","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOAD_DATE":{"coercion":"strict_date","nullable":true,"physical_aliases":[],"physical_column":"LOAD_DT","required_in_source":false,"roles":["filter","output"],"semantic_type":"LocalDate"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRESS_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRESS_CNT","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"RECIPE_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"RECIPE_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"UPH":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"UPH","required_in_source":true,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"eqp_uph","parameters":{},"query_ref":"query:eqp_uph@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"GMS_DB","query_template":"SELECT \\n\\n  EQUIP_MODEL\\n  ,OPER\\n  ,OPER_NAME\\n  ,PRESS_CNT\\n  ,PROD_TYP AS \\"MODE\\"\\n  ,TECH\\n  ,ORG\\n  ,DENSITY\\n  ,PKG_TYP AS PKG1\\n  ,PKG_TYP_2 AS PKG2\\n  ,LEAD_CNT AS LEAD\\n  ,MCP_NO\\n  ,RECIPE_ID \\n  ,round(AVG_UPH_VAL,2) AS UPH\\n  ,WORK_DT AS LOAD_DT\\n  ,BASE_DT\\nFROM UPH\\nWHERE 1=1","required_params":[],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"equipment_assign":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["EQP_ID"],"family":"equipment","fields":{"BAY_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"BAY_ID","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"EQP_ID":{"coercion":"string","nullable":true,"physical_aliases":["EQP_ID"],"physical_column":"EQUIP_ID","required_in_source":false,"roles":["filter","group","aggregate","join","output"],"semantic_type":"identifier"},"EQP_MODEL":{"coercion":"string","nullable":true,"physical_aliases":["EQP_MODEL"],"physical_column":"EQUIP_MODEL","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOT_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LOT_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NAME"],"physical_column":"OPER_NM","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRESS_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRESS_CNT","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"RECIPE_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"RECIPE_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"}},"key":"equipment_assign","parameters":{},"query_ref":"query:equipment_assign@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"SELECT \\n  BAY_ID, \\n  EQUIP_ID, \\n  EQUIP_MODEL, \\n  PRESS_CNT,\\n  OPER,\\n  OPER_NM,\\n  MODE, \\n  DENSITY, \\n  TECH, \\n  PKG1, \\n  PKG2, \\n  LEAD, \\n  ORG,\\n  PKGSIZE,  \\n  MCP_NO,\\n  DEVICE,\\n  DEVICE_DESC,\\n  LOT_ID,\\n  RECIPE_ID\\nFROM  EQP_TABLE\\nWHERE 1=1","required_params":[],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"hold_history":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["LOT_ID","OPER_NAME","HOLD_EVENT_AT","HOLD_CD","HOLD_DESC"],"family":"hold_history","fields":{"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"HOLD_CD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_CD","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"HOLD_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"HOLD_EVENT_AT":{"coercion":"strict_datetime","nullable":false,"physical_aliases":[],"physical_column":"HOLD_TM","required_in_source":true,"roles":["filter","aggregate","sort","derive","output"],"semantic_type":"LocalDateTime","timezone":"Asia/Seoul"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOT_ID":{"coercion":"string","nullable":false,"physical_aliases":[],"physical_column":"LOT_ID","required_in_source":true,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PROD_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PROD_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"}},"key":"hold_history","parameters":{"LOT_ID":{"chunk_size":200,"max_total_values":2000,"operator":"in","required":true,"type":"list[identifier]"}},"query_ref":"query:hold_history@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"/*HOLD_LOT_HISTORY*/\\n\\n        SELECT\\n\\n            LOT_ID,\\n            PROD_QTY,\\n            OPER,\\n            OPER_NAME,\\n            HOLD_TM,\\n            HOLD_CD,\\n            HOLD_USER,\\n            HOLD_DESC,\\n            FAB,\\n            FAMILY,\\n            MODE,\\n            DENSITY,\\n            TECH,\\n            ORG,\\n            PKG1,\\n            PKG2,\\n            LEAD,\\n            MCP_NO,\\n            GRADE,\\n            OWNER,\\n            \\n            DEVICE,\\n            DEVICE_DESC,\\n            PKG_SIZE,\\n            THK_CD,\\n            flow_id   \\n        FROM HOLD_HIS\\n        WHERE LOT_ID IN ({LOT_ID})","required_params":["LOT_ID"],"source_type":"oracle"},"source_type":"oracle","time_scope":"history","upstream_bindings":[{"chunk_size":200,"dedupe":true,"entity_type":"lot","max_total_values":2000,"operator":"in","sort_values":"asc","source_alias":"previous_result","source_field":"LOT_ID","target_parameter":"LOT_ID"}]},"lot_status":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["LOT_ID","OPER_NAME","PROD_QTY","WF_QTY","IN_TAT","CUM_TAT","HOLD_STAT","HOLD_REASON","LOT_STAT"],"family":"lot","fields":{"CUM_TAT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"CUM_TAT","required_in_source":false,"roles":["filter","aggregate","rank","sort","output"],"semantic_type":"number"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"EQP_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"EQP_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAC_IN_AT":{"coercion":"strict_datetime","nullable":true,"physical_aliases":[],"physical_column":"FAC_IN_TIME","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"LocalDateTime","timezone":"Asia/Seoul"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"HOLD_REASON":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_REASON","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"HOLD_STAT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_STAT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"IN_TAT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"IN_TAT","required_in_source":false,"roles":["filter","aggregate","rank","sort","output"],"semantic_type":"number"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOT_ID":{"coercion":"string","nullable":false,"physical_aliases":[],"physical_column":"LOT_ID","required_in_source":true,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"LOT_STAT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LOT_STAT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OPER_IN_AT":{"coercion":"strict_datetime","nullable":true,"physical_aliases":[],"physical_column":"OPER_IN_TM","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"LocalDateTime","timezone":"Asia/Seoul"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":false,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":true,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PROD_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PROD_QTY","required_in_source":false,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"WF_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"WF_QTY","required_in_source":false,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"lot_status","parameters":{},"query_ref":"query:lot_status@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"/*Current Wip Status*/\\nSELECT\\nERM_ID,OPER,OPER_NAME,FAB,OWNER,GRADE,DEVICE,LOT_ID,SUB_LOT_ID,PROD_QTY,WF_QTY,IN_TAT,CUM_TAT,EQP_ID,FLOW_ID,OPER_IN_TM,FAC_IN_TIME,HOLD_STAT,HOLD_REASON,FAMILY,MODE,DENSITY,TECH,ORG,PKG1,PKG2,PKG3,LEAD,MCP_NO,THK_CD,LOT_STAT,LOT_GRP,PKG_SIZE,HOT_LOT,HOT_LEVEL,PKG_COMPOSIT,DURABLE_ID,DURABLE_TYP,SUB_QTY,TSV_DIE_TYPE,EVENT_DESC,MOVE_IN_TM,PAD_ABNORMAL,SWR_REQ_NO,INSP_TARGET\\nFROM WIP_STATE\\nWHERE 1=1","required_params":[],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"product_master":{"config_ref":"config:fixture:operator_validation@1","default_detail_fields":["DEVICE","YIELD_RATE","MODE","LEAD"],"family":"product_master","fields":{"DEN":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEN","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":false,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":true,"roles":["filter","group","join","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"PKG_TYPE1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"PKG_TYPE2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"YIELD_RATE":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"YIELD_RATE","required_in_source":false,"roles":["filter","rank","output"],"semantic_type":"number"}},"fixture_only":true,"key":"product_master","parameters":{},"query_ref":"query:product_master_fixture@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_type":"fixture","time_scope":"current"},"production":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","PRODUCTION_QTY"],"family":"production","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRODUCTION_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRODUCTION","required_in_source":true,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"}},"key":"production","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:production_history@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"SELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ, PRODUCTION \\nFROM PROD_TABLE2\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"history"},"production_today":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","PRODUCTION_QTY"],"family":"production","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRODUCTION_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRODUCTION","required_in_source":true,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"}},"key":"production_today","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:production_today@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"--쿼리 작성\\nSELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ, PRODUCTION \\nFROM PROD_TABLE\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"target":{"config_ref":"config:goodocs:target@1","date_filter_contract":{"canonical_field":"DATE","source_format":"%Y-%m-%d","timezone":"Asia/Seoul"},"default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DATE","INPUT_PLAN_QTY","OUT_PLAN_QTY"],"family":"target","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":[],"physical_column":"DATE","required_in_source":true,"roles":["filter","sort","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DENSITY"],"physical_column":"DEN","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"INPUT_PLAN_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"INPUT 계획","required_in_source":false,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":["MCP_NO"],"physical_column":"MCP NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":["MODE"],"physical_column":"Mode","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OUT_PLAN_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OUT 계획","required_in_source":false,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"}},"key":"target","parameters":{},"query_ref":"query:target_plan@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_type":"goodocs","time_scope":"history"},"wip":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","WIP_QTY"],"family":"wip","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"WIP_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"WIP","required_in_source":true,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"wip","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:wip_history@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"--쿼리 작성\\nSELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ\\n        , WIP\\nFROM WIP_TABLE2\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"history"},"wip_today":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","WIP_QTY"],"family":"wip","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"WIP_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"WIP","required_in_source":true,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"wip_today","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:wip_today@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"SELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ\\n        , WIP\\nFROM WIP_TABLE\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"}},"fields":{"BASE_DATE":{"datasets":["eqp_uph"],"display_label":"BASE_DATE","key":"BASE_DATE","roles":["filter","output"],"semantic_type":"LocalDate"},"BAY_ID":{"datasets":["equipment_assign"],"display_label":"BAY_ID","key":"BAY_ID","roles":["filter","group","output"],"semantic_type":"string"},"CUM_TAT":{"datasets":["lot_status"],"display_label":"CUM_TAT","key":"CUM_TAT","roles":["aggregate","filter","output","rank","sort"],"semantic_type":"number"},"DATE":{"datasets":["production","production_today","target","wip","wip_today"],"display_label":"DATE","key":"DATE","roles":["filter","output","sort"],"semantic_type":"LocalDate"},"DEN":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"DEN","key":"DEN","roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"datasets":["equipment_assign","hold_history","lot_status","product_master","production","production_today","wip","wip_today"],"display_label":"DEVICE","key":"DEVICE","roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"datasets":["equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"DEVICE_DESC","key":"DEVICE_DESC","roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"DIE_ATTACH_QTY","key":"DIE_ATTACH_QTY","roles":["aggregate","filter","output"],"semantic_type":"number"},"EQP_ID":{"datasets":["equipment_assign","lot_status"],"display_label":"EQP_ID","key":"EQP_ID","roles":["aggregate","filter","group","join","output"],"semantic_type":"identifier"},"EQP_MODEL":{"datasets":["eqp_uph","equipment_assign"],"display_label":"EQP_MODEL","key":"EQP_MODEL","roles":["filter","group","join","output"],"semantic_type":"string"},"FAB":{"datasets":["equipment_assign","lot_status","production","production_today","wip","wip_today"],"display_label":"FAB","key":"FAB","roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"FACTORY","key":"FACTORY","roles":["filter","group","output"],"semantic_type":"string"},"FAC_IN_AT":{"datasets":["lot_status"],"display_label":"FAC_IN_AT","key":"FAC_IN_AT","roles":["filter","output","sort"],"semantic_type":"LocalDateTime"},"FAMILY":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"FAMILY","key":"FAMILY","roles":["filter","group","output"],"semantic_type":"string"},"HOLD_CD":{"datasets":["hold_history"],"display_label":"HOLD_CD","key":"HOLD_CD","roles":["filter","group","output"],"semantic_type":"string"},"HOLD_DESC":{"datasets":["hold_history"],"display_label":"HOLD_DESC","key":"HOLD_DESC","roles":["filter","output"],"semantic_type":"string"},"HOLD_EVENT_AT":{"datasets":["hold_history"],"display_label":"HOLD_EVENT_AT","key":"HOLD_EVENT_AT","roles":["aggregate","derive","filter","output","sort"],"semantic_type":"LocalDateTime"},"HOLD_REASON":{"datasets":["lot_status"],"display_label":"HOLD_REASON","key":"HOLD_REASON","roles":["filter","output"],"semantic_type":"string"},"HOLD_STAT":{"datasets":["lot_status"],"display_label":"HOLD_STAT","key":"HOLD_STAT","roles":["filter","group","output"],"semantic_type":"string"},"INPUT_PLAN_QTY":{"datasets":["target"],"display_label":"INPUT_PLAN_QTY","key":"INPUT_PLAN_QTY","roles":["aggregate","derive","filter","output","rank"],"semantic_type":"number"},"IN_TAT":{"datasets":["lot_status"],"display_label":"IN_TAT","key":"IN_TAT","roles":["aggregate","filter","output","rank","sort"],"semantic_type":"number"},"LEAD":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"LEAD","key":"LEAD","roles":["filter","group","join","output"],"semantic_type":"string"},"LOAD_DATE":{"datasets":["eqp_uph"],"display_label":"LOAD_DATE","key":"LOAD_DATE","roles":["filter","output"],"semantic_type":"LocalDate"},"LOT_ID":{"datasets":["equipment_assign","hold_history","lot_status"],"display_label":"LOT_ID","key":"LOT_ID","roles":["filter","group","join","output"],"semantic_type":"identifier"},"LOT_STAT":{"datasets":["lot_status"],"display_label":"LOT_STAT","key":"LOT_STAT","roles":["filter","group","output"],"semantic_type":"string"},"MCP_NO":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"MCP_NO","key":"MCP_NO","roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"MODE","key":"MODE","roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"NETDIE_300_CNT","key":"NETDIE_300_CNT","roles":["aggregate","derive","filter","output"],"semantic_type":"number"},"OPER_IN_AT":{"datasets":["lot_status"],"display_label":"OPER_IN_AT","key":"OPER_IN_AT","roles":["filter","output","sort"],"semantic_type":"LocalDateTime"},"OPER_NAME":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"OPER_NAME","key":"OPER_NAME","roles":["filter","group","join","output","sort"],"semantic_type":"string"},"OPER_NUM":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"OPER_NUM","key":"OPER_NUM","roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"datasets":["eqp_uph","lot_status","production","production_today","wip","wip_today"],"display_label":"OPER_SEQ","key":"OPER_SEQ","roles":["filter","output","sort"],"semantic_type":"number"},"ORG":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","target","wip","wip_today"],"display_label":"ORG","key":"ORG","roles":["filter","group","join","output"],"semantic_type":"string"},"OUT_PLAN_QTY":{"datasets":["target"],"display_label":"OUT_PLAN_QTY","key":"OUT_PLAN_QTY","roles":["aggregate","derive","filter","output","rank"],"semantic_type":"number"},"PKG_TYPE1":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"PKG_TYPE1","key":"PKG_TYPE1","roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"PKG_TYPE2","key":"PKG_TYPE2","roles":["filter","group","join","output"],"semantic_type":"string"},"PRESS_CNT":{"datasets":["eqp_uph","equipment_assign"],"display_label":"PRESS_CNT","key":"PRESS_CNT","roles":["aggregate","filter","output"],"semantic_type":"number"},"PRODUCTION_QTY":{"datasets":["production","production_today"],"display_label":"PRODUCTION_QTY","key":"PRODUCTION_QTY","roles":["aggregate","derive","filter","output","rank"],"semantic_type":"number"},"PROD_QTY":{"datasets":["hold_history","lot_status"],"display_label":"PROD_QTY","key":"PROD_QTY","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"RECIPE_ID":{"datasets":["eqp_uph","equipment_assign"],"display_label":"RECIPE_ID","key":"RECIPE_ID","roles":["filter","group","join","output"],"semantic_type":"identifier"},"SHIFT":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"SHIFT","key":"SHIFT","roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"TECH","key":"TECH","roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"datasets":["equipment_assign","lot_status","production","production_today","wip","wip_today"],"display_label":"TSV_DIE_TYP","key":"TSV_DIE_TYP","roles":["filter","group","output"],"semantic_type":"string"},"UPH":{"datasets":["eqp_uph"],"display_label":"UPH","key":"UPH","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"WF_QTY":{"datasets":["lot_status"],"display_label":"WF_QTY","key":"WF_QTY","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"WIP_QTY":{"datasets":["wip","wip_today"],"display_label":"WIP_QTY","key":"WIP_QTY","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"YIELD_RATE":{"datasets":["product_master"],"display_label":"YIELD_RATE","key":"YIELD_RATE","roles":["filter","output","rank"],"semantic_type":"number"}},"metrics":{"ACHIEVEMENT_RATE":{"dependencies":["INPUT_QTY","INPUT_PLAN_QTY"],"formula":{"evaluation_stage":"after_aggregate","expression":{"args":[{"args":[{"metric_ref":"INPUT_QTY"},{"metric_ref":"INPUT_PLAN_QTY"}],"op":"safe_divide","zero_division":"null"},{"literal":100,"value_type":"number"}],"op":"multiply"},"max_depth":6,"max_nodes":32,"rounding":{"digits":1,"mode":"half_even"},"version":"formula.v1"},"metric_id":"ACHIEVEMENT_RATE","unit":"percent","value_type":"number"},"CUM_TAT":{"additivity":{"allowed_rollups":["min","max","mean"],"default":"non_additive"},"metric_id":"CUM_TAT","null_policy":"exclude","source_binding":{"dataset_family":"lot","field":"CUM_TAT"},"unit":"hour","value_type":"number","zero_policy":"preserve_zero"},"EQP_COUNT":{"additivity":{"allowed_rollups":["nunique"],"default":"distinct"},"metric_id":"EQP_COUNT","null_policy":"exclude","source_binding":{"dataset_family":"equipment","field":"EQP_ID"},"unit":"equipment","value_type":"integer","zero_policy":"preserve_zero"},"HOLD_DURATION_HOURS":{"additivity":{"allowed_rollups":["min","max"],"default":"non_additive"},"dependencies":["HOLD_EVENT_AT","reference_instant"],"formula":{"evaluation_stage":"after_aggregate","expression":{"args":[{"runtime_ref":"reference_instant"},{"field_ref":"CURRENT_HOLD_STARTED_AT"}],"op":"datetime_diff_hours"},"max_depth":3,"max_nodes":8,"rounding":{"digits":3,"mode":"half_even"},"version":"formula.v1"},"metric_id":"HOLD_DURATION_HOURS","null_policy":"exclude","unit":"hour","value_type":"number","zero_policy":"preserve_zero"},"INPUT_PLAN_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"INPUT_PLAN_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"target","field":"INPUT_PLAN_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"INPUT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"INPUT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY","fixed_filters":[{"field":"OPER_NAME","operator":"eq","semantic_type":"string","value":"INPUT"}]},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"IN_TAT":{"additivity":{"allowed_rollups":["min","max","mean"],"default":"non_additive"},"metric_id":"IN_TAT","null_policy":"exclude","source_binding":{"dataset_family":"lot","field":"IN_TAT"},"unit":"hour","value_type":"number","zero_policy":"preserve_zero"},"LOT_COUNT":{"additivity":{"allowed_rollups":["nunique"],"default":"distinct"},"metric_id":"LOT_COUNT","null_policy":"exclude","source_binding":{"dataset_family":"lot","field":"LOT_ID"},"unit":"lot","value_type":"integer","zero_policy":"preserve_zero"},"OUT_PLAN_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"OUT_PLAN_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"target","field":"OUT_PLAN_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"OUT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"OUT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY","fixed_filters":[{"field":"OPER_NAME","operator":"eq","semantic_type":"string","value":"PKG OUT"}]},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"PKG_OUT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"PKG_OUT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY","fixed_filters":[{"field":"OPER_NAME","operator":"eq","semantic_type":"string","value":"PKG OUT"}]},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"PRODUCTION_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"PRODUCTION_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"UNIT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"UNIT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"lot","field":"PROD_QTY"},"unit":"unit","value_type":"number","zero_policy":"preserve_zero"},"UPH":{"additivity":{"allowed_rollups":["mean"],"default":"non_additive"},"metric_id":"UPH","null_policy":"exclude_from_mean","source_binding":{"dataset_family":"equipment_uph","field":"UPH"},"unit":"unit_per_hour","value_type":"number","zero_policy":"preserve_zero"},"WAFER_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"WAFER_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"lot","field":"WF_QTY"},"unit":"wafer","value_type":"number","zero_policy":"preserve_zero"},"WIP_BOH_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"WIP_BOH_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"wip","field":"WIP_QTY"},"temporal_contract":{"business_timepoint":"BOH","dataset_selector":{"dataset_key":"wip","family":"wip","time_scope":"history"},"disallowed_dataset_keys":["wip_today"],"display_date":"requested_date","inherit_filters":true,"query_time":{"anchor":"requested_date","calendar":"gregorian","offset_days":-1,"timezone":"Asia/Seoul"},"source_parameter":"DATE"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"WIP_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"WIP_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"wip","field":"WIP_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"}},"process_groups":{"BG":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["BG","BG공정","BG 공정","B/G","B/G공정","B/G 공정"],"display_name":"B/G","expansion":"closed_set","group_id":"process_group.BG","members":["B/G1","B/G2"],"target_field":"OPER_NAME"},"BM":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["BM","BM공정","BM 공정","B/M","B/M공정","B/M 공정","비엠","비엠공정","비엠 공정"],"display_name":"B/M","expansion":"closed_set","group_id":"process_group.BM","members":["B/M"],"target_field":"OPER_NAME"},"DA":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DA","DA공정","DA 공정","D/A","D/A공정","D/A 공정"],"display_name":"D/A","expansion":"closed_set","group_id":"process_group.DA","members":["D/A1","D/A2","D/A3","D/A4","D/A5","D/A6"],"target_field":"OPER_NAME"},"DC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DC","DC공정","DC 공정","D/C","D/C공정","D/C 공정"],"display_name":"D/C","expansion":"closed_set","group_id":"process_group.DC","members":["D/C1","D/C2","D/C3","D/C4"],"target_field":"OPER_NAME"},"DI":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DI","DI공정","DI 공정","D/I","D/I공정","D/I 공정","DVI","DVI공정","DVI 공정"],"display_name":"D/I","expansion":"closed_set","group_id":"process_group.DI","members":["D/I"],"target_field":"OPER_NAME"},"DP":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DP","DP공정","DP 공정","D/P","D/P공정","D/P 공정"],"display_name":"DP","expansion":"closed_set","group_id":"process_group.DP","members":["WET1","WET2","L/T1","L/T2","B/G1","B/G2","H/S1","H/S2","W/S1","W/S2","WSD1","WSD2","WEC1","WEC2","WLS1","WLS2","WVI","UV","C/C1"],"target_field":"OPER_NAME"},"DS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DS","DS공정","DS 공정","D/S","D/S공정","D/S 공정"],"display_name":"D/S","expansion":"closed_set","group_id":"process_group.DS","members":["D/S1"],"target_field":"OPER_NAME"},"FCB":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["FCB","FCB공정","FCB 공정"],"display_name":"FCB","expansion":"closed_set","group_id":"process_group.FCB","members":["FCB1","FCB2","FCB/H"],"target_field":"OPER_NAME"},"FCBH":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["FCBH","FCBH공정","FCBH 공정","FCB/H","FCB/H공정","FCB/H 공정"],"display_name":"FCB/H","expansion":"closed_set","group_id":"process_group.FCBH","members":["FCB/H"],"target_field":"OPER_NAME"},"HS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["HS","HS공정","HS 공정","H/S","H/S공정","H/S 공정"],"display_name":"H/S","expansion":"closed_set","group_id":"process_group.HS","members":["H/S1","H/S2"],"target_field":"OPER_NAME"},"LT":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["LT","LT공정","LT 공정","L/T","L/T공정","L/T 공정"],"display_name":"L/T","expansion":"closed_set","group_id":"process_group.LT","members":["L/T1","L/T2"],"target_field":"OPER_NAME"},"PC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["PC","PC공정","PC 공정","P/C","P/C공정","P/C 공정"],"display_name":"P/C","expansion":"closed_set","group_id":"process_group.PC","members":["P/C1","P/C2","P/C3","P/C4","P/C5"],"target_field":"OPER_NAME"},"PCO":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["PCO","PCO공정","PCO 공정"],"display_name":"PCO","expansion":"closed_set","group_id":"process_group.PCO","members":["PCO1","PCO2","PCO3","PCO4","PCO5","PCO6"],"target_field":"OPER_NAME"},"PLH":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["PLH","PLH공정","PLH 공정","P/L","P/L공정","P/L 공정"],"display_name":"P/L","expansion":"closed_set","group_id":"process_group.PLH","members":["PLH"],"target_field":"OPER_NAME"},"QCSPC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["QCSPC","QCSPC공정","QCSPC 공정"],"display_name":"QCSPC","expansion":"closed_set","group_id":"process_group.QCSPC","members":["QCSPC1","QCSPC2","QCSPC3","QCSPC4"],"target_field":"OPER_NAME"},"SAT":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["SAT","SAT공정","SAT 공정"],"display_name":"SAT","expansion":"closed_set","group_id":"process_group.SAT","members":["SAT1","SAT2"],"target_field":"OPER_NAME"},"SBM":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["SBM","SBM공정","SBM 공정"],"display_name":"SBM","expansion":"closed_set","group_id":"process_group.SBM","members":["SBM"],"target_field":"OPER_NAME"},"SG":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["SG","SG공정","SG 공정","S/G","S/G공정","S/G 공정"],"display_name":"S/G","expansion":"closed_set","group_id":"process_group.SG","members":["S/G"],"target_field":"OPER_NAME"},"WB":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WB","WB공정","WB 공정","W/B","W/B공정","W/B 공정"],"display_name":"W/B","expansion":"closed_set","group_id":"process_group.WB","members":["W/B1","W/B2","W/B3","W/B4","W/B5","W/B6"],"target_field":"OPER_NAME"},"WBM":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WBM","WBM공정","WBM 공정","W/BM","W/BM공정","W/BM 공정"],"display_name":"W/BM","expansion":"closed_set","group_id":"process_group.WBM","members":["W/BM"],"target_field":"OPER_NAME"},"WEC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WEC","WEC공정","WEC 공정"],"display_name":"WEC","expansion":"closed_set","group_id":"process_group.WEC","members":["WEC1","WEC2"],"target_field":"OPER_NAME"},"WET":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WET","WET공정","WET 공정"],"display_name":"WET","expansion":"closed_set","group_id":"process_group.WET","members":["WET1","WET2"],"target_field":"OPER_NAME"},"WLS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WLS","WLS공정","WLS 공정"],"display_name":"WLS","expansion":"closed_set","group_id":"process_group.WLS","members":["WLS1","WLS2"],"target_field":"OPER_NAME"},"WS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WS","WS공정","WS 공정","W/S","W/S공정","W/S 공정"],"display_name":"W/S","expansion":"closed_set","group_id":"process_group.WS","members":["W/S1","W/S2"],"target_field":"OPER_NAME"},"WSD":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WSD","WSD공정","WSD 공정"],"display_name":"WSD","expansion":"closed_set","group_id":"process_group.WSD","members":["WSD1","WSD2"],"target_field":"OPER_NAME"}},"process_order":[{"aliases":["INPUT"],"oper_name":"INPUT","oper_seq":10,"revision":1},{"aliases":["DA1"],"oper_name":"D/A1","oper_seq":100,"revision":1},{"aliases":["DA2"],"oper_name":"D/A2","oper_seq":110,"revision":1},{"aliases":["DA3"],"oper_name":"D/A3","oper_seq":120,"revision":1},{"aliases":["DA4"],"oper_name":"D/A4","oper_seq":130,"revision":1},{"aliases":["DA5"],"oper_name":"D/A5","oper_seq":140,"revision":1},{"aliases":["DA6"],"oper_name":"D/A6","oper_seq":150,"revision":1},{"aliases":["DS1"],"oper_name":"D/S1","oper_seq":160,"revision":1},{"aliases":["WB1"],"oper_name":"W/B1","oper_seq":200,"revision":1},{"aliases":["WB2"],"oper_name":"W/B2","oper_seq":210,"revision":1},{"aliases":["WB3"],"oper_name":"W/B3","oper_seq":220,"revision":1},{"aliases":["WB4"],"oper_name":"W/B4","oper_seq":230,"revision":1},{"aliases":["WB5"],"oper_name":"W/B5","oper_seq":240,"revision":1},{"aliases":["WB6"],"oper_name":"W/B6","oper_seq":250,"revision":1},{"aliases":["WBM"],"oper_name":"W/BM","oper_seq":260,"revision":1},{"aliases":["FCB1"],"oper_name":"FCB1","oper_seq":300,"revision":1},{"aliases":["FCB2"],"oper_name":"FCB2","oper_seq":310,"revision":1},{"aliases":["FCBH"],"oper_name":"FCB/H","oper_seq":320,"revision":1},{"aliases":["BG1"],"oper_name":"B/G1","oper_seq":400,"revision":1},{"aliases":["BG2"],"oper_name":"B/G2","oper_seq":410,"revision":1},{"aliases":["SBM"],"oper_name":"SBM","oper_seq":500,"revision":1},{"aliases":["PKG OUT"],"oper_name":"PKG OUT","oper_seq":900,"revision":1}],"product_groups":{"AUTO":{"aliases":["AUTO향","오토모티브향","오토향"],"allowed_operators":["ends_with"],"grain_id":"product.standard","group_id":"product_group.AUTO","predicate":{"clauses":[{"field":"MCP_NO","operator":"ends_with","value":"I"},{"field":"MCP_NO","operator":"ends_with","value":"O"},{"field":"MCP_NO","operator":"ends_with","value":"N"},{"field":"MCP_NO","operator":"ends_with","value":"P"},{"field":"MCP_NO","operator":"ends_with","value":"Q"},{"field":"MCP_NO","operator":"ends_with","value":"V"}],"op":"any"}},"HBM":{"aliases":["HBM","3DS","TSV"],"allowed_operators":["is_not_blank"],"grain_id":"product.standard","group_id":"product_group.HBM","predicate":{"field":"TSV_DIE_TYP","operator":"is_not_blank"}},"MOBILE":{"aliases":["Mobile","MOBILE","모바일"],"allowed_operators":["eq","in","starts_with","null_or_blank","is_not_blank"],"grain_id":"product.standard","group_id":"product_group.MOBILE","predicate":{"clauses":[{"field":"MODE","operator":"starts_with","value":"LP"},{"field":"PKG_TYPE1","operator":"in","values":["LFBGA","TFBGA","UFBGA","VFBGA","WFBGA"]},{"field":"MCP_NO","operator":"null_or_blank"}],"op":"all"}},"POP":{"aliases":["POP","pop","Pop"],"allowed_operators":["eq","in","starts_with","null_or_blank","is_not_blank"],"grain_id":"product.standard","group_id":"product_group.POP","predicate":{"clauses":[{"field":"MODE","operator":"starts_with","value":"LP"},{"field":"PKG_TYPE1","operator":"in","values":["LFBGA","TFBGA","UFBGA","VFBGA","WFBGA"]},{"field":"MCP_NO","operator":"is_not_blank"}],"op":"all"}},"STACK_2HI":{"aliases":["2Hi"],"allowed_operators":["eq"],"grain_id":"product.standard","group_id":"product_group.STACK_2HI","predicate":{"field":"TSV_DIE_TYP","operator":"eq","value":"2Hi"}},"STACK_4HI":{"aliases":["4Hi"],"allowed_operators":["eq"],"grain_id":"product.standard","group_id":"product_group.STACK_4HI","predicate":{"field":"TSV_DIE_TYP","operator":"eq","value":"4Hi"}},"STACK_8HI":{"aliases":["8Hi"],"allowed_operators":["eq"],"grain_id":"product.standard","group_id":"product_group.STACK_8HI","predicate":{"field":"TSV_DIE_TYP","operator":"eq","value":"8Hi"}}},"recipes":{"achievement.input_actual":{"aliases":["생산달성률","생산달성율","INPUT 계획 대비 실적"],"default_operation_template":{"aggregate_before_derive":true,"derive":{"formula_ref":"metric:ACHIEVEMENT_RATE","op":"derive","output_field":"ACHIEVEMENT_RATE"}},"metrics":["INPUT_QTY","INPUT_PLAN_QTY","ACHIEVEMENT_RATE"],"recipe_id":"achievement.input_actual","required_slots":["actual_input","target_input","grain"]},"equipment.assignment_enrich":{"aliases":["할당된 장비 대수와 LIST","장비 배정","장비 목록"],"datasets":["equipment_assign"],"default_operation_template":{"cardinality":"one_to_one_after_aggregate","how":"left","keys":[{"left":"TECH","right":"TECH"},{"left":"DEN","right":"DEN"},{"left":"MODE","right":"MODE"},{"left":"PKG_TYPE1","right":"PKG_TYPE1"},{"left":"PKG_TYPE2","right":"PKG_TYPE2"},{"left":"LEAD","right":"LEAD"},{"left":"MCP_NO","right":"MCP_NO"}],"op":"enrich_previous_result","right_pre_aggregate":[{"as":"EQP_COUNT","field":"EQP_ID","function":"nunique"},{"as":"EQP_LIST","field":"EQP_ID","function":"list_unique"}],"suffix_policy":"forbid"},"recipe_id":"equipment.assignment_enrich","required_slots":["previous_product_result"]},"equipment.assignment_uph":{"aliases":["장비별 UPH","배정 장비 UPH","장비와 Recipe UPH"],"datasets":["equipment_assign","eqp_uph"],"default_operation_template":{"cardinality":"many_to_one","how":"left","keys":[{"left":"EQP_MODEL","right":"EQP_MODEL"},{"left":"RECIPE_ID","right":"RECIPE_ID"},{"left":"OPER_NAME","right":"OPER_NAME"}],"multi_match_policy":"error","null_key_policy":"never_match","op":"join","suffix_policy":"forbid"},"recipe_id":"equipment.assignment_uph","required_slots":["equipment","uph"]},"hold.oldest_current_history":{"aliases":["HOLD 시간이 가장 오래된 LOT","오래된 HOLD 이력"],"datasets":["hold_history"],"default_operation_template":{"steps":[{"group_by":["LOT_ID"],"metrics":[{"as":"CURRENT_HOLD_STARTED_AT","field":"HOLD_EVENT_AT","function":"max"}],"op":"aggregate"},{"formula_ref":"metric:HOLD_DURATION_HOURS","op":"derive","output_field":"HOLD_DURATION_HOURS"},{"include_ties":true,"mode":"top","n":1,"op":"rank","rank_by":[{"direction":"desc","field":"HOLD_DURATION_HOURS"}],"scope":"global","tie_break_by":[{"direction":"asc","field":"LOT_ID"}]},{"cardinality":"many_to_one","how":"inner","keys":[{"left":"LOT_ID","right":"LOT_ID"}],"multi_match_policy":"error","null_key_policy":"never_match","op":"join","suffix_policy":"forbid"},{"history_order":[{"direction":"desc","field":"HOLD_EVENT_AT"},{"direction":"asc","field":"LOT_ID"}],"op":"detail"}]},"derived_metrics":["HOLD_DURATION_HOURS"],"recipe_id":"hold.oldest_current_history","required_fields":["LOT_ID","HOLD_EVENT_AT"],"required_slots":["previous_current_hold_result","reference_instant"]},"join.operation.production_wip":{"aliases":["생산량과 재공수량","생산 WIP 비교"],"datasets":["production","production_today","wip","wip_today"],"default_operation_template":{"cardinality":"one_to_one_after_aggregate","empty_side_policy":"preserve_other_side_with_declared_null_metrics","how":"outer","keys":[{"left":"TECH","right":"TECH"},{"left":"DEN","right":"DEN"},{"left":"MODE","right":"MODE"},{"left":"PKG_TYPE1","right":"PKG_TYPE1"},{"left":"PKG_TYPE2","right":"PKG_TYPE2"},{"left":"LEAD","right":"LEAD"},{"left":"MCP_NO","right":"MCP_NO"}],"multi_match_policy":"error","null_key_policy":"blank_equals_blank","op":"join","suffix_policy":"forbid"},"recipe_id":"join.operation.production_wip","required_slots":["production_metric","wip_metric","grain"]},"ordered.process.range":{"aliases":["공정 구간","공정 범위","OPER_SEQ 범위"],"default_operation_template":{"field":"OPER_SEQ","filter_order":"before_general_filters","inclusive":"both","op":"ordered_range"},"recipe_id":"ordered.process.range","required_fields":["OPER_NAME","OPER_SEQ"],"required_slots":["range_start","range_end","dataset"]},"presence.left_positive_right_zero":{"aliases":["A는 있으나 B는 없음","실적 있음 재공 없음","존재 미존재"],"default_operation_template":{"keys":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO"],"left_metric_ref":"$left_metric.id","materialize_right_zero":true,"op":"presence_filter","right_metric_ref":"$right_metric.id"},"recipe_id":"presence.left_positive_right_zero","required_slots":["left_metric","right_metric","grain"]},"product.standard":{"aliases":["제품별","제품 기준","제품 집계"],"default_operation_template":{"group_by":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO"],"metrics":[{"as_ref":"$metric.id","field_ref":"$metric.field","function_ref":"$metric.rollup"}],"op":"aggregate"},"grain":{"entity_id":"product","grain_id":"product.standard","keys":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO"],"null_match_policy":"blank_equals_blank"},"recipe_id":"product.standard","required_slots":["dataset","metric"]},"rank.bottom_n":{"aliases":["하위 N개","가장 적은","BOTTOM N"],"default_operation_template":{"include_ties":false,"mode":"bottom","op":"rank","scope":"global","stable_tie_break":"declared_keys"},"recipe_id":"rank.bottom_n","required_slots":["metric","n"]},"rank.top_n":{"aliases":["상위 N개","가장 많은","TOP N"],"default_operation_template":{"include_ties":false,"mode":"top","op":"rank","scope":"global","stable_tie_break":"declared_keys"},"recipe_id":"rank.top_n","required_slots":["metric","n"]}}}')


EMBEDDED_SCHEMAS = json.loads('{"domain-package.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":4096,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/domain-package.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"authoring_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"compiler_version":{"minLength":1,"type":"string"},"contract_version":{"const":"domain.package.v1"},"domain_id":{"pattern":"^[a-z][a-z0-9_-]{1,63}$","type":"string"},"environment":{"pattern":"^[a-z][a-z0-9_-]{1,31}$","type":"string"},"lifecycle":{"additionalProperties":false,"properties":{"status":{"enum":["draft","validated","active","deprecated","quarantined"]}},"required":["status"],"type":"object"},"package_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"revision":{"minimum":1,"type":"integer"},"runtime_catalog":{"$ref":"#/$defs/jsonObject"}},"required":["contract_version","domain_id","environment","revision","lifecycle","compiler_version","authoring_sha256","runtime_catalog","package_sha256","bundle_sha256"],"title":"domain.package.v1","type":"object"},"runtime-catalog-v2.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":4096,"type":"array"},{"$ref":"#/$defs/jsonObject"}]},"registeredFunctionCallTemplate":{"additionalProperties":false,"properties":{"dataset_ref":{"maxLength":128,"minLength":1,"type":"string"},"field_ref":{"maxLength":128,"minLength":1,"type":"string"},"output_fields":{"items":{"maxLength":128,"minLength":1,"type":"string"},"maxItems":128,"minItems":1,"type":"array","uniqueItems":true},"parameters":{"additionalProperties":false,"properties":{"case_sensitive":{"type":"boolean"},"match_mode":{"enum":["any","all"]},"operator":{"enum":["equals","contains","starts_with","ends_with"]},"tokens":{"items":{"maxLength":256,"minLength":1,"type":"string"},"maxItems":64,"minItems":1,"type":"array","uniqueItems":true}},"required":["tokens","operator","match_mode","case_sensitive"],"type":"object"}},"required":["dataset_ref","field_ref","parameters","output_fields"],"type":"object"},"registeredFunctionLimits":{"additionalProperties":false,"properties":{"max_input_rows":{"maximum":100000,"minimum":1,"type":"integer"},"max_output_bytes":{"maximum":8388608,"minimum":1,"type":"integer"},"max_output_rows":{"maximum":100000,"minimum":1,"type":"integer"},"timeout_ms":{"maximum":5000,"minimum":1,"type":"integer"}},"required":["timeout_ms","max_input_rows","max_output_rows","max_output_bytes"],"type":"object"},"specializedFunction":{"additionalProperties":false,"properties":{"aliases":{"items":{"maxLength":200,"minLength":1,"type":"string"},"maxItems":32,"minItems":1,"type":"array","uniqueItems":true},"call_template":{"$ref":"#/$defs/registeredFunctionCallTemplate"},"execution_mode":{"const":"registered_standalone"},"failure_policy":{"const":"fail_closed"},"function_id":{"pattern":"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$","type":"string"},"implementation_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"input_schema":{"$ref":"#/$defs/jsonObject"},"limits":{"$ref":"#/$defs/registeredFunctionLimits"},"output_schema":{"$ref":"#/$defs/jsonObject"},"required_fields":{"items":{"minLength":1,"type":"string"},"maxItems":128,"type":"array","uniqueItems":true},"version":{"minimum":1,"type":"integer"}},"required":["function_id","version","execution_mode","implementation_sha256","input_schema","output_schema"],"type":"object"}},"$id":"https://metadata-driven-v6.local/schemas/runtime-catalog-v2.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"aliases":{"$ref":"#/$defs/jsonObject"},"catalog_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"compiler_version":{"minLength":1,"type":"string"},"contract_version":{"const":"metadata.runtime.catalog.v2"},"datasets":{"additionalProperties":false,"minProperties":1,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"description":{"type":"string"},"display_name":{"minLength":1,"type":"string"},"domain_id":{"pattern":"^[a-z][a-z0-9_-]{1,63}$","type":"string"},"entity_groups":{"$ref":"#/$defs/jsonObject"},"environment":{"pattern":"^[a-z][a-z0-9_-]{1,31}$","type":"string"},"fields":{"additionalProperties":false,"minProperties":1,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"grains":{"$ref":"#/$defs/jsonObject"},"locale":{"type":"string"},"metrics":{"$ref":"#/$defs/jsonObject"},"orderings":{"$ref":"#/$defs/jsonObject"},"output_profile":{"$ref":"#/$defs/jsonObject"},"predicates":{"$ref":"#/$defs/jsonObject"},"prompt_extensions":{"$ref":"#/$defs/jsonObject"},"recipes":{"$ref":"#/$defs/jsonObject"},"relations":{"$ref":"#/$defs/jsonObject"},"revision":{"minimum":1,"type":"integer"},"specialized_functions":{"items":{"$ref":"#/$defs/specializedFunction"},"maxItems":64,"type":"array"},"timezone":{"type":"string"}},"required":["contract_version","domain_id","environment","revision","compiler_version","display_name","locale","timezone","datasets","fields","metrics","entity_groups","grains","relations","orderings","predicates","recipes","aliases","prompt_extensions","specialized_functions","output_profile","catalog_sha256"],"title":"metadata.runtime.catalog.v2","type":"object"}}')



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



import os

from lfx.custom.custom_component.component import Component
from lfx.io import IntInput, Output, SecretStrInput, StrInput
from lfx.schema.data import Data


def _secret_text(value):
    if hasattr(value, "get_secret_value"):
        value = value.get_secret_value()
    return str(value or "").strip()


def _validate_catalog(catalog):
    if not isinstance(catalog, dict):
        raise ContractError("metadata_dependency_error", "domain_bundle", "runtime catalog를 찾을 수 없습니다.")
    if catalog.get("contract_version") == "metadata.runtime.catalog.v2":
        return validate_runtime_catalog_v2(catalog)
    missing = {"contract_version", "datasets", "fields", "metrics", "catalog_sha256"} - set(catalog)
    if missing:
        raise ContractError("metadata_dependency_error", "domain_bundle", "runtime catalog 필수 필드가 없습니다.", {"missing": sorted(missing)})
    for key in ("datasets", "fields", "metrics"):
        if not isinstance(catalog.get(key), dict):
            raise ContractError("metadata_dependency_error", "domain_bundle", f"runtime catalog {key}는 object여야 합니다.")
    return catalog


class DomainBundleLoader(Component):
    display_name = "01 사용 가능 메타데이터 불러오기"
    description = "가장 최근 등록된 도메인·테이블 카탈로그·메인필터의 동일 release를 자동으로 찾아 하나의 실행 카탈로그로 결합합니다."
    icon = "package-open"
    metadata = {"logical_stage": "domain_bundle"}

    inputs = [
        SecretStrInput(name="mongo_uri", display_name="MongoDB 연결 URI", value="", required=False, info="세 메타데이터 컬렉션을 읽을 MongoDB 연결 문자열입니다."),
        StrInput(name="mongo_database", display_name="MongoDB 데이터베이스", value="datagov", info="운영 메타데이터가 저장된 데이터베이스입니다."),
        StrInput(name="domain_collection", display_name="도메인 메타데이터 컬렉션", value="agent_v6_domain_metadata", info="도메인 원문과 검증된 공통 업무 규칙을 읽을 컬렉션입니다."),
        StrInput(name="table_collection", display_name="데이터 카탈로그 컬렉션", value="agent_v6_table_catalog", info="데이터셋·필드·원천 조회 계약을 읽을 컬렉션입니다."),
        StrInput(name="main_filter_collection", display_name="메인필터 메타데이터 컬렉션", value="agent_v6_main_filter", info="주요 필터·별칭·predicate를 읽을 컬렉션입니다."),
        IntInput(name="mongo_timeout_ms", display_name="MongoDB 제한 시간(ms)", value=5000, info="MongoDB 연결 및 조회에 적용할 제한 시간(밀리초)입니다."),
    ]
    outputs = [Output(name="domain_bundle", display_name="검증된 도메인 실행 번들", method="load_bundle", types=["Data"])]

    def load_bundle(self) -> Data:
        context = {"contract_version": PIPELINE_VERSION, "ok": True, "stage": "domain_bundle"}
        try:
            uri = _secret_text(getattr(self, "mongo_uri", "")) or os.getenv("MONGODB_URI", "").strip()
            if not uri:
                raise ContractError("metadata_dependency_error", "domain_bundle", "사용 가능한 메타데이터를 읽으려면 MongoDB URI가 필요합니다.")
            try:
                from pymongo import MongoClient
            except ImportError as exc:
                raise ContractError("metadata_dependency_error", "domain_bundle", "pymongo를 사용할 수 없습니다.") from exc
            client = MongoClient(uri, serverSelectionTimeoutMS=max(500, min(int(getattr(self, "mongo_timeout_ms", 5000)), 30000)))
            try:
                database = client[str(getattr(self, "mongo_database", "") or os.getenv("MONGODB_DATABASE", "datagov"))]
                package = load_available_domain_package_from_three_collections(
                    database,
                    domain_collection=str(getattr(self, "domain_collection", "agent_v6_domain_metadata") or "").strip(),
                    table_collection=str(getattr(self, "table_collection", "agent_v6_table_catalog") or "").strip(),
                    main_filter_collection=str(getattr(self, "main_filter_collection", "agent_v6_main_filter") or "").strip(),
                )
            finally:
                client.close()
            domain_id = str(package["domain_id"])
            environment = str(package["environment"])
            revision = str(package["revision"])
            catalog = deepcopy(package["runtime_catalog"])
            catalog = _validate_catalog(catalog)
            context["domain_bundle"] = {
                "contract_version": "domain.bundle.runtime.v1",
                "domain_id": domain_id,
                "environment": environment,
                "revision": revision,
                "source_mode": "three_collections",
                "catalog_sha256": str(catalog.get("catalog_sha256") or sha256_json(catalog)),
                "runtime_catalog": catalog,
            }
            context["domain_bundle"].update(
                {"package_sha256": package.get("package_sha256"), "bundle_sha256": package.get("bundle_sha256")}
            )
        except Exception as exc:
            context = _pipeline_error(context, exc, "domain_bundle")
        return Data(data=context)
