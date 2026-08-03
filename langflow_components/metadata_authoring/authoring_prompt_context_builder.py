# -*- coding: utf-8 -*-
"""GENERATED standalone component: AuthoringPromptContextBuilder.

Regenerate with tools/build_standalone_components.py.  Do not hand edit.
"""
from __future__ import annotations

import json

EMBEDDED_SOURCE_MANIFEST = json.loads('{"catalog_contract_version":"metadata.runtime.catalog.v1","catalog_declared_sha256":"1f8b6c1522b96425a6a46a3e4dfcf4c5b7c338c6bc0af3c2a0878806ea4a7f8e","catalog_file_sha256":"0b035cefd556b3c37b166e73270dee3e7070a2adf2dd56750b8e1015516bfcce","contract_version":"standalone.source.manifest.v1","reference_sources":{"contracts/schemas/active-domain-pointer.schema.json":"8ff3e114e106d0bc08c83e61947ac967c28cd5390cd0539cb1efdc64b82f9a61","contracts/schemas/analysis-plan.schema.json":"15dbb187f458d03ad4d55063eef898b862529dc68e9f64840d08ab20df9cfb76","contracts/schemas/analysis-result.schema.json":"06e92c0892ff5b209783332f33e4d4ed1855612470b088390e4501591f68065b","contracts/schemas/analysis-route.schema.json":"aadd7504e7f75329b8b6a50634261e073450e6d19d8e14d4a44196c0000e0c04","contracts/schemas/answer-facts.schema.json":"26c573be25f4fade355a37f2ab231f3e0aa8ac83445ee58020a99388648809ed","contracts/schemas/answer-sections.schema.json":"4c1d645c9927879e6a9e877def326ff045b5a01edaf48a566b935bc4734882ab","contracts/schemas/approval-event.schema.json":"4aa6b10eeb875538d00d6de564bdbe24eb093e8727ed57515cbadba63f13d7a9","contracts/schemas/config-registry.schema.json":"2f90dfb2b99e17faa9afecaf1f32295f6d713067aeca66c7dc1544c5713598e9","contracts/schemas/display-options.schema.json":"099ef7c371a2ac015cf7b59ae873d2ff749cdad7fa738bbcccc9b4838ea45866","contracts/schemas/domain-package.schema.json":"f39f433985180636bb3b6dfe054cfb8e63998acbe0112f7082a8233b619517f7","contracts/schemas/download-item.schema.json":"91efd43bf2db00bf5e85071fa2992679c3b2dc050251a5c82e839dcd7f5d4086","contracts/schemas/error-registry.schema.json":"f67a1ab5ef2568626d406cb9feb38acfbb6fc593fa04f3da063f8293da653b64","contracts/schemas/error.schema.json":"1a0c89cc1898a894b0490a59f286c68520c0f74be0811f6c06c4aa3e50fe5602","contracts/schemas/evidence-manifest.schema.json":"2805ed7cce742e96b5e10902b096fbec91e40a8aca7fde7bfe95c1d12a9668bb","contracts/schemas/executable-blueprint.schema.json":"e55dbe8faa2f1f2eb933b1548b2b1c37886a0911ceb4e70838427bac2327f14a","contracts/schemas/executed-result.schema.json":"eaba5818e5fb30e2a572f5a81488d9ba34032adcf3af55dfbb0d4287afc7e435","contracts/schemas/flow-inventory.schema.json":"cdce69d64a9df37a88e139a0fd0900d38d9475d2a8f13ff9a9b5c1bf0777b672","contracts/schemas/gaia-metadata.schema.json":"86d0a11a06a97d573b550a427d26abe9db6e897d3c46681f02e2427735e9f093","contracts/schemas/metadata-annotation-proposal.schema.json":"f0b227cc42a528d6e0b95f1c8c4a1bf6bbb6871d17d32c108d65b47d2b0ddc7f","contracts/schemas/metadata-authoring-draft.schema.json":"035c081be6a0fa719b3dcd589d9090071342b695fa61f80f6781441a4b14aee2","contracts/schemas/metadata-authoring-proposal.schema.json":"8ee3fc86d8f596c554443c16ad619822e63315ed8f2bfd06311987fc63322edd","contracts/schemas/metadata-authoring-response.schema.json":"da776b8a156d007c5bd95e86ad10cfb5a8ac7f06c2cae0c52aeb96b6a36415f6","contracts/schemas/metadata-bootstrap-dataset-ir.schema.json":"351260f7ed418b35f4ca1e5012a353b1d8f820ea21dfc8880483c193880af3b6","contracts/schemas/metadata-bootstrap-main-filter-ir.schema.json":"41c849c88b803d53af9c02c3d50127c47e8ee38e46d7b0a1ad0d09c3638e48fa","contracts/schemas/metadata-bundle.schema.json":"985ffe44974cf14d6c52a8188d54c3b209c00478e83888f00c359cd056d5dc81","contracts/schemas/metadata-envelope.schema.json":"9abca177e22b570f2158dace05256f671c0acbd054705dfe4f34611fbdae2048","contracts/schemas/model-profile.schema.json":"14345c16f629fc03a3de2cdd2fe469bef1fdc82cd2f93954ce1f4204ba82f356","contracts/schemas/operator-registry.schema.json":"acd003c6db66b470a2653fc8a97caaf3856c9d4cfd934bc0f27ef609787c2746","contracts/schemas/pending-metadata-write.schema.json":"af7a0593fafbdcea16f1212ba92484525626e43f2a25d91f9c310a80f5b37a4d","contracts/schemas/query-registry.schema.json":"8422a44035eb2a06381166d69a185036c698f581b17741a8c4686fbeea109040","contracts/schemas/registered-call.schema.json":"41c4152f45577f05c925d5d782a48f8db45f67f8e48aac8805b822269516bd58","contracts/schemas/registered-function-card.schema.json":"bc9ca8b01c90d2d11737f1a70586e9227510b67fdab26c8ae605d9e830170dfd","contracts/schemas/request-capsule.schema.json":"675e661653098288d6cc9e6e9b3599ed3bf3e05d6d592ac66d9ed46b9fd2afaf","contracts/schemas/resolved-candidate-bundle.schema.json":"a24b7d2fc3798f1dd69e1af94a7071eae8fb56d93a4191258953fd63b4211568","contracts/schemas/response.schema.json":"40c1e43f2228c04bb9ea652f1107a7ac202405c3321bc2c6af8dbc543b2e7b06","contracts/schemas/retrieval-job-bundle.schema.json":"e73cd6e6c50bb24b528111c36c410af3afe2fe3ff28d3d906cfe023263a12105","contracts/schemas/runtime-catalog-v2.schema.json":"3f7f6c5154c9e7922dd65490e9166ba0038c6a242258ec30d409d8a553948fed","contracts/schemas/semantic-intent-selection.schema.json":"a70c99e36060531fac9730c02f706ffa8d108b872c5abe0e2d05cafa459e6a75","contracts/schemas/semantic-intent.schema.json":"a743b7e26168dda04a7f46205fed67987a587cf3cce939cf57b228b099bfad53","contracts/schemas/source-bundle.schema.json":"a5330ef1b104df5dd0f19385b5e7994ee5469feffa110ee84087b7992258ea92","contracts/schemas/source-result.schema.json":"f342dcf0f948f7f99899335d83f302f2aaa38b05bb246eb06f9c1da0161f516c","contracts/schemas/trace.schema.json":"3f7cb2dd4e88b5f9f09695347ce42d8b98d5c4534d8fab41cca8ea1c9e3d484e","contracts/schemas/turn-state.schema.json":"688ad4f5ac1b133e60e3a2ef2bef56d0b18c87a41d2c6c236264285aeba32280","contracts/schemas/unsupported-telemetry.schema.json":"8c3675797be935d6fd52db2883d433d464df2fdecc5e0d52e795a5fa1e6c8439","contracts/schemas/validation-case.schema.json":"23304f969ca614324f7a74b52edc72c4e6753e76c476a77fc8db68f089941682","langflow_components/shared/01_prompt_bundle_composer.py":"2a8e80103205136221c87901a1bdeeb7df62f954c9f3f9c407a77a2e41a6b77b","langflow_components/shared/02_conditional_llm_invoker.py":"2b7ee35fb4276b932285a62860b1114b29797698232bfc9523597c103c6ea3d9","metadata/domain_packs/manufacturing/approved_source_registry.json":"241969f12d76c0d616296894dc51ba95553ebf48d5edb15e20480c4beec64587","reference_runtime/authoring_blueprint.py":"9fc416a04e0da317586ad8abf9831bf650746a7f1907ad62fcaef4012327fe71","reference_runtime/authoring_source_manifest.py":"311bd68482e163a781bf11aa449587879f659fa9c36f7564129ecea44b88170c","reference_runtime/canonical.py":"338b8b013b9311f94d9b5ff7a3d5902576e9dfb88b40d72d37436025806c2d1d","reference_runtime/contracts.py":"5d16082db0bf437e537a24352834548e48e157a4c740659e9c9f1a0e46960d6e","reference_runtime/domain_authoring_patches.py":"4c78c72bc2412cbe78e74372b7c5af658ada8de1b8058b228f02d2b68b41c445","reference_runtime/domain_packages.py":"ae08de3501c92be10bd8f983fa710cc8e4cec6a40dd8051140ab754c9caac04a","reference_runtime/dummy_data.py":"c02824f9ddba81496d99a4b58bda8e6bedf0ce464d47abca682071ab24cae57d","reference_runtime/engine.py":"62df5f1a06c0a2765085826bec3e73f99f02da470850d180f2d7a53078c67606","reference_runtime/generic_v2_candidates.py":"95f5821b05d7d70f70ebd0339a316bcc1367b5499553319b8d8995df251a4c56","reference_runtime/generic_v2_planner.py":"142665c8050c9302830cedf45928a25b73cd34e80bec66de9ba77003209176d3","reference_runtime/metadata_collections.py":"164dee7c88789aacdb98b6f52ec12da399f2237b7f98075dc9b4b9ea05a74172","reference_runtime/metadata_compiler.py":"99544e6094883b4241d010af2bec5d67e6205d34634ad46d6e2ee173107336e3","reference_runtime/plan_compiler.py":"e3782e6e86e41968a7bab1be4056ac2e9459c28188efa92f6532d2898d12abee","reference_runtime/presenter.py":"fee16b71dfaf07be0d27fee14f47aa753ea71350165185071552ff0f30a31101","reference_runtime/registered_functions.py":"d2125d6902ca246b2239e8569959ac37f45847bf17dafaf93b857e088c750e42","reference_runtime/request_literals.py":"00493f9e342ab3065215805ae32f3068cb594209434bf280f2bb4f23c4be62ff","reference_runtime/source_contracts.py":"c43d8865ff045f4c26c5194262620a50961be5b56552c5cc6e7d580b2c11d7b0","reference_runtime/state_contracts.py":"5a03fff6684850361904add4e4d15ea578617d1fce20564119bbac175fb334ae","reference_runtime/typed_executor.py":"0c1fc3bbb055cd32d1da3446afab0aca5351e844536624ae9ab953c78c5dfe3b"}}')


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


import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable
CATALOG_CONTRACT_VERSION = 'metadata.runtime.catalog.v1'
COMPILER_VERSION = 'metadata-compiler.v6.1'
CATALOG_TOP_LEVEL_KEYS = {'contract_version', 'datasets', 'fields', 'metrics', 'process_groups', 'process_order', 'product_groups', 'recipes', 'aliases', 'catalog_sha256'}
PRODUCT_GRAIN = ['TECH', 'DEN', 'MODE', 'PKG_TYPE1', 'PKG_TYPE2', 'LEAD', 'MCP_NO']

def build_runtime_catalog(authoring_root: str | Path | None=None) -> dict[str, Any]:
    return deepcopy(EMBEDDED_RUNTIME_CATALOG)

def compute_catalog_sha256(catalog: dict[str, Any]) -> str:
    material = {key: value for key, value in catalog.items() if key != 'catalog_sha256'}
    return sha256_json(material)

def validate_runtime_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(catalog, dict):
        raise ContractError('metadata_dependency_error', 'metadata_compile', 'runtime catalog가 object가 아닙니다.')
    actual_keys = set(catalog)
    if actual_keys != CATALOG_TOP_LEVEL_KEYS:
        raise ContractError('metadata_dependency_error', 'metadata_compile', 'runtime catalog top-level contract가 일치하지 않습니다.', {'missing': sorted(CATALOG_TOP_LEVEL_KEYS - actual_keys), 'extra': sorted(actual_keys - CATALOG_TOP_LEVEL_KEYS)})
    if catalog.get('contract_version') != CATALOG_CONTRACT_VERSION:
        raise ContractError('metadata_dependency_error', 'metadata_compile', 'runtime catalog version이 일치하지 않습니다.')
    expected_hash = compute_catalog_sha256(catalog)
    if catalog.get('catalog_sha256') != expected_hash:
        raise ContractError('metadata_dependency_error', 'metadata_compile', 'runtime catalog hash가 일치하지 않습니다.', {'expected': expected_hash, 'actual': catalog.get('catalog_sha256')})
    for collection_name in ['datasets', 'fields', 'metrics', 'process_groups', 'product_groups', 'recipes', 'aliases']:
        if not isinstance(catalog.get(collection_name), dict) or not catalog[collection_name]:
            raise ContractError('metadata_dependency_error', 'metadata_compile', f'{collection_name} catalog이 비어 있습니다.')
    if not isinstance(catalog.get('process_order'), list) or not catalog['process_order']:
        raise ContractError('metadata_dependency_error', 'metadata_compile', 'process_order가 비어 있습니다.')
    fields = catalog['fields']
    for key, dataset in catalog['datasets'].items():
        required_keys = {'key', 'family', 'source_type', 'fields', 'parameters', 'default_detail_fields'}
        missing = required_keys - set(dataset)
        if missing or dataset.get('key') != key:
            raise ContractError('metadata_dependency_error', 'metadata_compile', 'dataset contract가 완전하지 않습니다.', {'dataset_key': key, 'missing': sorted(missing)})
        _validate_dataset_bindings(key, dataset, fields)
    sequences: set[int] = set()
    names: set[str] = set()
    for item in catalog['process_order']:
        name = str(item.get('oper_name') or '')
        try:
            sequence = int(item.get('oper_seq'))
        except (TypeError, ValueError) as exc:
            raise ContractError('metadata_dependency_error', 'metadata_compile', 'OPER_SEQ가 numeric이 아닙니다.') from exc
        if not name or name in names or sequence in sequences:
            raise ContractError('metadata_dependency_error', 'metadata_compile', 'process_order identity/sequence가 중복됩니다.')
        names.add(name)
        sequences.add(sequence)
    metric_fields = set(fields)
    families = {str(item.get('family')) for item in catalog['datasets'].values()}
    for metric_id, metric in catalog['metrics'].items():
        if metric.get('metric_id') != metric_id:
            raise ContractError('metadata_dependency_error', 'metadata_compile', 'metric identity가 일치하지 않습니다.', {'metric_id': metric_id})
        binding = metric.get('source_binding')
        if isinstance(binding, dict):
            if binding.get('field') not in metric_fields or binding.get('dataset_family') not in families:
                raise ContractError('metadata_dependency_error', 'metadata_compile', 'metric source binding이 유효하지 않습니다.', {'metric_id': metric_id})
        additivity = metric.get('additivity')
        if isinstance(additivity, dict) and additivity.get('default') == 'non_additive' and ('sum' in additivity.get('allowed_rollups', [])):
            raise ContractError('metadata_dependency_error', 'metadata_compile', 'non-additive metric에 sum이 허용됐습니다.', {'metric_id': metric_id})
    for group_type in ['process_groups', 'product_groups']:
        for key, group in catalog[group_type].items():
            if not group.get('aliases'):
                raise ContractError('metadata_dependency_error', 'metadata_compile', 'group alias가 비어 있습니다.', {'group': key})
    for key, recipe in catalog['recipes'].items():
        if recipe.get('recipe_id') != key or not isinstance(recipe.get('required_slots'), list):
            raise ContractError('metadata_dependency_error', 'metadata_compile', 'recipe contract가 완전하지 않습니다.', {'recipe': key})
    return catalog

def _validate_dataset_bindings(dataset_key: str, dataset: dict[str, Any], fields: dict[str, Any]) -> None:
    bindings = dataset.get('fields')
    if not isinstance(bindings, dict) or not bindings:
        raise ContractError('metadata_dependency_error', 'metadata_compile', 'dataset field binding이 비어 있습니다.', {'dataset_key': dataset_key})
    physical_owners: dict[str, str] = {}
    for canonical_field, binding in bindings.items():
        if canonical_field not in fields:
            raise ContractError('metadata_dependency_error', 'metadata_compile', '미등록 canonical field입니다.', {'dataset_key': dataset_key, 'field': canonical_field})
        physical = str(binding.get('physical_column') or '')
        candidates = [physical, *[str(value) for value in binding.get('physical_aliases', [])]]
        if not physical or len(candidates) != len(set(candidates)):
            raise ContractError('metadata_dependency_error', 'metadata_compile', 'physical field binding이 모호합니다.', {'dataset_key': dataset_key, 'field': canonical_field})
        for candidate in candidates:
            owner = physical_owners.get(candidate)
            if owner and owner != canonical_field:
                raise ContractError('metadata_dependency_error', 'metadata_compile', 'physical field가 둘 이상 canonical field에 binding됐습니다.', {'dataset_key': dataset_key, 'physical_field': candidate, 'fields': [owner, canonical_field]})
            physical_owners[candidate] = canonical_field
    for field in dataset.get('default_detail_fields', []):
        if field not in bindings:
            raise ContractError('metadata_dependency_error', 'metadata_compile', 'default detail field binding이 없습니다.', {'dataset_key': dataset_key, 'field': field})

def compiled_records(catalog: dict[str, Any], provenance: dict[str, dict[str, Any]], *, lifecycle_status: str='active') -> list[dict[str, Any]]:
    """Project a validated catalog into immutable revisioned records."""
    validate_runtime_catalog(catalog)
    source_for_kind = {'dataset': 'table_catalog', 'field': 'table_catalog', 'metric': 'domain', 'process_group': 'domain', 'process_order': 'domain', 'product_group': 'domain', 'recipe': 'domain', 'alias': 'main_filters'}
    groups: list[tuple[str, Iterable[tuple[str, Any]]]] = [('dataset', catalog['datasets'].items()), ('field', catalog['fields'].items()), ('metric', catalog['metrics'].items()), ('process_group', catalog['process_groups'].items()), ('process_order', ((str(item['oper_name']), item) for item in catalog['process_order'])), ('product_group', catalog['product_groups'].items()), ('recipe', catalog['recipes'].items()), ('alias', catalog['aliases'].items())]
    records: list[dict[str, Any]] = []
    for kind, items in groups:
        for key, contract in items:
            source_kind = source_for_kind[kind]
            if kind == 'alias' and isinstance(contract, dict):
                source_kind = str(contract.get('provenance_source') or source_kind)
            source = provenance[source_kind]
            material = deepcopy(contract)
            contract_sha = sha256_json(material)
            records.append({'schema_version': 'metadata.v6', 'kind': kind, 'identity': {'namespace': 'metadata_v6', 'key': str(key)}, 'revision': 1, 'lifecycle': {'status': lifecycle_status}, 'provenance': {'source_id': source['source_id'], 'source_block': str(key), 'content_sha256': source['content_sha256'], 'compiler_version': COMPILER_VERSION, 'prompt_sha256': 'not_applicable_deterministic_compile', 'model': 'deterministic', 'source_type': 'natural_language_txt'}, 'dependencies': [], 'contract': material, 'contract_sha256': contract_sha, 'validation': {'schema': 'passed', 'semantic_lint': 'passed', 'dependency_closure': 'passed', 'catalog_sha256': catalog['catalog_sha256']}})
    return records
__all__ = ['CATALOG_CONTRACT_VERSION', 'CATALOG_TOP_LEVEL_KEYS', 'COMPILER_VERSION', 'MANUFACTURING_PACK_CATALOG', 'PRODUCT_GRAIN', 'build_runtime_catalog', 'compiled_records', 'compute_catalog_sha256', 'load_runtime_catalog', 'source_provenance', 'validate_authoring_sources', 'validate_runtime_catalog', 'write_runtime_catalog']


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


import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable, Mapping
from copy import deepcopy
from typing import Any
_v6mMANIFEST_VERSION = 'metadata.authoring.source-manifest.v1'
_v6mCOVERAGE_VERSION = 'metadata.authoring.source-coverage.v1'
_v6m_ALIAS_TARGET_SECTIONS = (('datasets', 'dataset'), ('fields', 'field'), ('metrics', 'metric'), ('relations', 'relation'), ('grains', 'grain'), ('predicates', 'predicate'), ('recipes', 'recipe'), ('entity_groups', 'entity_group'))
_v6m_FIELD_ROLE_ORDER = ('filter', 'group', 'join', 'compare', 'aggregate', 'derive', 'project', 'sort', 'rank', 'metric', 'output')
_v6m_FIELD_ROLE_SET = set(_v6m_FIELD_ROLE_ORDER)
_v6m_RELATION_POLICY_VALUES = {'join_type': {'inner', 'left', 'right', 'outer', 'semi', 'anti'}, 'cardinality': {'one_to_zero_or_one', 'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many'}, 'null_key_policy': {'never_match', 'match'}, 'multi_match_policy': {'fail', 'error', 'aggregate_right_first'}}
_v6mMAX_SOURCE_BYTES = 65536
_v6mMAX_MISSING_EVIDENCE = 32
_v6mMAX_INVENTORY = {'datasets': 128, 'fields': 1024, 'field_bindings': 4096, 'metrics': 512, 'relations': 256, 'relation_endpoints': 256, 'relation_keys': 256, 'relation_policies': 256, 'field_roles': 4096, 'grains': 256, 'grain_keys': 256, 'grain_display_fields': 256, 'recipes': 256, 'operations': 64, 'aliases': 4096}
_v6m_IDENTIFIER = '[A-Za-z][A-Za-z0-9_.-]{0,127}'
_v6m_DECLARED_ID = '[A-Za-z](?:[A-Za-z0-9_.-]{0,126}[A-Za-z0-9_])?'
_v6m_IDENTIFIER_RE = re.compile(f'(?<![A-Za-z0-9_.-])({_v6m_IDENTIFIER})(?![A-Za-z0-9_.-])')
_v6m_SHA256_RE = re.compile('^[0-9a-f]{64}$')
_v6m_DATASET_RE = re.compile(f'(?<![A-Za-z0-9_.-])(?P<dataset>{_v6m_DECLARED_ID})[ \\t]*(?:\\ub370\\uc774\\ud130\\uc14b|datasets?)(?![A-Za-z0-9_])(?:[ \\t]*(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=|is\\b))?', re.IGNORECASE)
_v6m_CANONICAL_FIELDS_RE = re.compile('canonical\\s*(?:\\ud544\\ub4dc(?:\\ub4e4)?|fields?)(?:\\s*(?:\\uc740|\\ub294|:|=)|\\s+(?:are|include|includes)\\b)\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_METRICS_RE = re.compile('(?:\\ub4f1\\ub85d\\s*metrics?|registered\\s+metrics?)\\s*(?:(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=)|are\\b)?\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_RELATIONS_RE = re.compile('(?:(?:\\ub4f1\\ub85d\\s*)?relations?|registered\\s+relations?)(?!\\s*(?:endpoints?|keys?|polic(?:y|ies))(?![A-Za-z0-9_]))\\s*(?:(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=)|are\\b)?\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_RELATION_ENDPOINTS_RE = re.compile('(?:(?:\\ub4f1\\ub85d|registered)\\s*)?relation\\s*endpoints?\\s*(?:(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=)|are\\b)?\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_RELATION_ENDPOINT_ITEM_RE = re.compile(f'(?P<relation>{_v6m_DECLARED_ID})\\s*=\\s*(?P<left>{_v6m_DECLARED_ID})\\s*(?:->|\\u2192)\\s*(?P<right>{_v6m_DECLARED_ID})', re.IGNORECASE)
_v6m_RELATION_KEYS_RE = re.compile('(?:(?:\\ub4f1\\ub85d|registered)\\s*)?relation\\s*keys?\\s*(?:(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=)|are\\b)?\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_RELATION_KEY_ITEM_RE = re.compile(f'(?P<relation>{_v6m_DECLARED_ID})\\s*=\\s*(?P<left>{_v6m_DECLARED_ID}(?:\\s*\\|\\s*{_v6m_DECLARED_ID})*)\\s*(?:->|\\u2192)\\s*(?P<right>{_v6m_DECLARED_ID}(?:\\s*\\|\\s*{_v6m_DECLARED_ID})*)', re.IGNORECASE)
_v6m_FIELD_ROLES_RE = re.compile('(?:(?:\\ub4f1\\ub85d|registered)\\s*)?field\\s*roles?\\s*(?:(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=)|are\\b)?\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_FIELD_ROLE_ITEM_RE = re.compile(f'(?P<dataset>{_v6m_DECLARED_ID})\\.(?P<field>{_v6m_DECLARED_ID})\\s*=\\s*(?P<roles>{_v6m_DECLARED_ID}(?:\\s*\\|\\s*{_v6m_DECLARED_ID})*)', re.IGNORECASE)
_v6m_RELATION_POLICIES_RE = re.compile('(?:(?:\\ub4f1\\ub85d|registered)\\s*)?relation\\s*polic(?:y|ies)\\s*(?:(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=)|are\\b)?\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_RELATION_POLICY_ITEM_RE = re.compile(f'(?P<relation>{_v6m_DECLARED_ID})\\s*=\\s*join_type\\s*:\\s*(?P<join_type>{_v6m_DECLARED_ID})\\s*\\|\\s*cardinality\\s*:\\s*(?P<cardinality>{_v6m_DECLARED_ID})\\s*\\|\\s*null_key_policy\\s*:\\s*(?P<null_key_policy>{_v6m_DECLARED_ID})\\s*\\|\\s*multi_match_policy\\s*:\\s*(?P<multi_match_policy>{_v6m_DECLARED_ID})', re.IGNORECASE)
_v6m_GRAIN_KEYS_RE = re.compile('(?:(?:\\ub4f1\\ub85d|registered)\\s*)?grain\\s*keys?\\s*(?:(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=)|are\\b)?\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_GRAIN_KEY_ITEM_RE = re.compile(f'(?P<grain>{_v6m_DECLARED_ID})\\s*=\\s*(?P<keys>{_v6m_DECLARED_ID}(?:\\s*\\|\\s*{_v6m_DECLARED_ID})*)', re.IGNORECASE)
_v6m_GRAIN_DISPLAY_FIELDS_RE = re.compile('(?:(?:\\ub4f1\\ub85d|registered)\\s*)?grain\\s*display\\s*fields?\\s*(?:(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=)|are\\b)?\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_GRAIN_DISPLAY_FIELD_ITEM_RE = re.compile(f'(?P<grain>{_v6m_DECLARED_ID})\\s*=\\s*(?P<fields>{_v6m_DECLARED_ID}(?:\\s*\\|\\s*{_v6m_DECLARED_ID})*)', re.IGNORECASE)
_v6m_OPERATIONS_RE = re.compile('(?:\\ud5c8\\uc6a9\\s*operations?|allowed\\s+operations?)\\s*(?:(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=)|are\\b)?\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_RECIPE_IDS_RE = re.compile('(?:(?:\\ub4f1\\ub85d|registered)\\s*)?(?:recipes?|\\ub808\\uc2dc\\ud53c)\\s*(?:ids?|ID|\\uc544\\uc774\\ub514)\\s*(?:(?:\\uc740|\\ub294|\\uc774|\\uac00|:|=)|are\\b)\\s*(?P<items>[^\\n]+)', re.IGNORECASE)
_v6m_NAMED_RECIPE_RE = re.compile(f'(?P<recipe>{_v6m_DECLARED_ID})\\s+(?:recipe|\\ub808\\uc2dc\\ud53c)\\s*(?:(?:\\uc740|\\ub294|:)|is\\b)', re.IGNORECASE)
_v6m_RECIPE_MENTION_RE = re.compile('(?<![A-Za-z0-9_])(?:recipes?|\\ub808\\uc2dc\\ud53c)(?![A-Za-z0-9_])', re.IGNORECASE)
_v6m_KOREAN_ALIAS_CLAUSE_RE = re.compile(f'(?P<labels>[^,.\\n]+?)(?:\\uc740|\\ub294)\\s*(?P<target>{_v6m_DECLARED_ID})(?:\\uc5d0)?(?=\\s*(?:,|\\uc5f0\\uacb0|\\.|$))', re.IGNORECASE)
_v6m_ENGLISH_ALIAS_CLAUSE_RE = re.compile(f'(?P<labels>[^,.;\\n]+?)(?:\\s+(?:map|maps)\\s+to|\\s+are\\s+aliases?\\s+for|\\s*->\\s*)(?P<target>{_v6m_DECLARED_ID})(?=\\s*(?:,|\\.|;|$))', re.IGNORECASE)
_v6m_KOREAN_ALIAS_CARD_RE = re.compile(f'별칭\\s*카드.*?안정\\s*식별자는\\s*(?P<identity_type>{_v6m_DECLARED_ID})\\s*:\\s*(?P<identity_key>{_v6m_DECLARED_ID}).*?대상\\s*유형은\\s*(?P<target_type>{_v6m_DECLARED_ID})\\s*,\\s*대상\\s*키는\\s*(?P<target_key>{_v6m_DECLARED_ID}).*?\\n\\s*사용자가\\s*(?P<labels>[^\\n]+?)라고\\s*말하면\\s*(?P<resolved_target>{_v6m_DECLARED_ID})(?:\\s*(?:필드|지표|데이터셋))?로\\s*해석', re.IGNORECASE)
_v6m_QUOTED_ALIAS_RE = re.compile('[\'\\"](?P<label>[^\'\\"\\n]{1,256})[\'\\"]')
_v6m_LIST_STOPWORDS = {'a', 'an', 'and', 'are', 'allowed', 'canonical', 'field', 'fields', 'id', 'ids', 'include', 'includes', 'is', 'metric', 'metrics', 'operation', 'operations', 'recipe', 'recipes', 'registered', 'relation', 'relations', 'the'}

class AuthoringSourceManifestError(ValueError):
    """Fail-closed authoring inventory error with bounded safe evidence."""

    def __init__(self, code: str, evidence: Mapping[str, Any] | None=None) -> None:
        self.code = str(code)
        self.evidence = deepcopy(dict(evidence or {}))
        super().__init__(self.code)

def _v6m_canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()

def _v6m_normalized_source(source_text: str) -> tuple[str, str]:
    if not isinstance(source_text, str):
        raise AuthoringSourceManifestError('authoring_source_not_text')
    raw_bytes = source_text.encode('utf-8')
    if not raw_bytes or len(raw_bytes) > _v6mMAX_SOURCE_BYTES:
        raise AuthoringSourceManifestError('authoring_source_size_invalid', {'source_bytes': len(raw_bytes), 'max_source_bytes': _v6mMAX_SOURCE_BYTES})
    normalized = unicodedata.normalize('NFKC', source_text).replace('\r\n', '\n').replace('\r', '\n').lstrip('\ufeff').strip()
    normalized_bytes = normalized.encode('utf-8')
    if not normalized_bytes:
        raise AuthoringSourceManifestError('authoring_source_size_invalid', {'source_bytes': 0, 'max_source_bytes': _v6mMAX_SOURCE_BYTES})
    return (normalized, hashlib.sha256(normalized_bytes).hexdigest())

def _v6m_declaration_items(raw_items: str) -> list[str]:
    """Parse a bounded comma/conjunction list without interpreting prose."""
    text = str(raw_items or '')
    text = re.split('(?:\\uc774\\ub2e4|\\uc785\\ub2c8\\ub2e4|\\uc774\\uba70|\\uc774\\uace0)(?:\\.|\\s|$)|;|(?<![A-Za-z0-9_.-])\\.(?=\\s|$)', text, maxsplit=1)[0]
    text = text.strip()
    if text.endswith('.'):
        text = text[:-1]
    text = re.sub('[`\'\\"\\[\\](){}]', ' ', text)
    text = re.sub('\\s+(?:\\ubc0f|\\uadf8\\ub9ac\\uace0|and)\\s+', ',', text, flags=re.IGNORECASE)
    values: list[str] = []
    for segment in text.split(','):
        matches = [item for item in _v6m_IDENTIFIER_RE.findall(segment) if item.casefold() not in _v6m_LIST_STOPWORDS]
        if len(matches) == 1:
            values.append(matches[0])
        elif len(matches) > 1:
            raise AuthoringSourceManifestError('authoring_inventory_item_ambiguous', {'identifier_count': len(matches)})
    return sorted(set(values))

def _v6m_bounded(values: Iterable[str], kind: str) -> list[str]:
    normalized = sorted({str(value) for value in values})
    limit = _v6mMAX_INVENTORY[kind]
    if len(normalized) > limit:
        raise AuthoringSourceManifestError('authoring_inventory_limit_exceeded', {'inventory': kind, 'count': len(normalized), 'limit': limit})
    for value in normalized:
        if not re.fullmatch(_v6m_IDENTIFIER, value):
            raise AuthoringSourceManifestError('authoring_inventory_identifier_invalid', {'inventory': kind, 'identifier_sha256': hashlib.sha256(value.encode('utf-8')).hexdigest()})
    return normalized

def _v6m_normalized_alias(value: str) -> str:
    normalized = unicodedata.normalize('NFKC', str(value or ''))
    normalized = re.sub('\\s+', ' ', normalized).strip(' `"\'[](){}:;.-')
    if not normalized or len(normalized) > 128:
        raise AuthoringSourceManifestError('authoring_alias_invalid', {'alias_sha256': hashlib.sha256(normalized.encode('utf-8')).hexdigest()})
    return normalized.casefold()

def _v6m_alias_labels(raw_labels: str) -> list[str]:
    labels = str(raw_labels or '')
    labels = re.sub('^.*(?:\\ubcc4\\uce6d|aliases?)(?:\\uc73c\\ub85c|\\uc740|\\ub294|\\s*:)?\\s*', '', labels, flags=re.IGNORECASE)
    parts = re.split('\\s*(?:\\uacfc|\\uc640|\\ubc0f)\\s*|\\s+and\\s+', labels, flags=re.IGNORECASE)
    return sorted({_v6m_normalized_alias(part) for part in parts if str(part).strip()})

def _v6m_source_alias_bindings(source: str) -> tuple[list[dict[str, str]], bool]:
    alias_marker = re.compile('(?:\\ubcc4\\uce6d|aliases?)', re.IGNORECASE)
    pairs: dict[str, str] = {}
    declared = False
    protected_spans: list[tuple[int, int]] = []

    def add_pair(label: str, target: str) -> None:
        existing = pairs.get(label)
        if existing is not None and existing != target:
            raise AuthoringSourceManifestError('authoring_alias_target_ambiguous', {'alias_sha256': hashlib.sha256(label.encode('utf-8')).hexdigest()})
        pairs[label] = target
    for match in _v6m_KOREAN_ALIAS_CARD_RE.finditer(source):
        declared = True
        identity_type = match.group('identity_type').casefold()
        target_type = match.group('target_type').casefold()
        identity_key = match.group('identity_key')
        target_key = match.group('target_key')
        resolved_target = match.group('resolved_target')
        if identity_type != target_type or identity_key != target_key or target_key != resolved_target:
            raise AuthoringSourceManifestError('authoring_alias_card_declaration_invalid', {'card_sha256': _v6m_safe_value_sha256(match.group(0))})
        labels = [_v6m_normalized_alias(item.group('label')) for item in _v6m_QUOTED_ALIAS_RE.finditer(match.group('labels'))]
        if not labels:
            raise AuthoringSourceManifestError('authoring_alias_card_declaration_invalid')
        for label in labels:
            add_pair(label, target_key)
        protected_spans.append(match.span())
    cursor = 0
    for raw_line in source.splitlines(keepends=True):
        line = raw_line.rstrip('\r\n')
        line_span = (cursor, cursor + len(raw_line))
        cursor = line_span[1]
        if any((line_span[0] < end and start < line_span[1] for start, end in protected_spans)):
            continue
        if not alias_marker.search(line):
            continue
        for pattern in (_v6m_KOREAN_ALIAS_CLAUSE_RE, _v6m_ENGLISH_ALIAS_CLAUSE_RE):
            for match in pattern.finditer(line):
                declared = True
                target = match.group('target').rstrip('.')
                if not re.fullmatch(_v6m_IDENTIFIER, target):
                    raise AuthoringSourceManifestError('authoring_alias_target_invalid')
                for label in _v6m_alias_labels(match.group('labels')):
                    add_pair(label, target)
    if len(pairs) > _v6mMAX_INVENTORY['aliases']:
        raise AuthoringSourceManifestError('authoring_inventory_limit_exceeded', {'inventory': 'aliases', 'count': len(pairs), 'limit': _v6mMAX_INVENTORY['aliases']})
    return ([{'alias': alias, 'target': target} for alias, target in sorted(pairs.items())], declared)

def _v6m_collect_declared_list(pattern: re.Pattern[str], source: str, kind: str) -> tuple[list[str], bool]:
    matches = list(pattern.finditer(source))
    values: list[str] = []
    for match in matches:
        parsed = _v6m_declaration_items(match.group('items'))
        if not parsed:
            raise AuthoringSourceManifestError('authoring_inventory_declaration_empty', {'inventory': kind})
        values.extend(parsed)
    return (_v6m_bounded(values, kind), bool(matches))

def _v6m_source_relation_endpoints(source: str, *, relations: Iterable[str], datasets: Iterable[str]) -> tuple[dict[str, dict[str, str]], bool]:
    """Extract exact ``relation=left->right`` declarations from source prose."""
    matches = list(_v6m_RELATION_ENDPOINTS_RE.finditer(source))
    registered_relations = set(relations)
    registered_datasets = set(datasets)
    endpoints: dict[str, dict[str, str]] = {}
    for declaration in matches:
        raw_items = declaration.group('items')
        raw_items = re.split('(?:\\uc774\\ub2e4|\\uc785\\ub2c8\\ub2e4)(?:\\.|\\s|$)|;|(?<![A-Za-z0-9_.-])\\.(?=\\s|$)', raw_items, maxsplit=1)[0]
        segments = re.split('\\s*(?:,|\\s+(?:\\ubc0f|\\uadf8\\ub9ac\\uace0|and)\\s+)\\s*', raw_items.strip().rstrip('.'), flags=re.IGNORECASE)
        parsed_count = 0
        for segment in segments:
            if not segment.strip():
                continue
            item = _v6m_RELATION_ENDPOINT_ITEM_RE.fullmatch(segment.strip())
            if item is None:
                raise AuthoringSourceManifestError('authoring_relation_endpoint_declaration_invalid', {'item_sha256': _v6m_safe_value_sha256(segment.strip())})
            parsed_count += 1
            relation_id = item.group('relation')
            left_dataset = item.group('left')
            right_dataset = item.group('right')
            if relation_id not in registered_relations:
                raise AuthoringSourceManifestError('authoring_relation_endpoint_relation_unknown', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
            unknown_datasets = sorted((value for value in {left_dataset, right_dataset} if value not in registered_datasets))
            if unknown_datasets:
                raise AuthoringSourceManifestError('authoring_relation_endpoint_dataset_unknown', {'relation_sha256': _v6m_safe_value_sha256(relation_id), 'dataset_sha256': [_v6m_safe_value_sha256(value) for value in unknown_datasets]})
            card = {'left_dataset': left_dataset, 'right_dataset': right_dataset}
            existing = endpoints.get(relation_id)
            if existing is not None and existing != card:
                raise AuthoringSourceManifestError('authoring_relation_endpoint_ambiguous', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
            endpoints[relation_id] = card
        if not parsed_count:
            raise AuthoringSourceManifestError('authoring_relation_endpoint_declaration_empty')
    if len(endpoints) > _v6mMAX_INVENTORY['relation_endpoints']:
        raise AuthoringSourceManifestError('authoring_inventory_limit_exceeded', {'inventory': 'relation_endpoints', 'count': len(endpoints), 'limit': _v6mMAX_INVENTORY['relation_endpoints']})
    return ({key: endpoints[key] for key in sorted(endpoints)}, bool(matches))

def _v6m_closed_declaration_matches(raw_items: str, item_pattern: re.Pattern[str], *, kind: str) -> list[re.Match[str]]:
    body = re.split('(?:\\uc774\\ub2e4|\\uc785\\ub2c8\\ub2e4)(?:\\.|\\s|$)|;|(?<![A-Za-z0-9_.-])\\.(?=\\s|$)', str(raw_items or ''), maxsplit=1)[0].strip().rstrip('.')
    matches = list(item_pattern.finditer(body))
    if not matches:
        raise AuthoringSourceManifestError('authoring_inventory_declaration_empty', {'inventory': kind})
    cursor = 0
    for index, match in enumerate(matches):
        gap = body[cursor:match.start()]
        if index == 0:
            valid_gap = not gap.strip()
        else:
            valid_gap = bool(re.fullmatch('\\s*(?:,|\\ubc0f|\\uadf8\\ub9ac\\uace0|and)\\s*', gap, flags=re.IGNORECASE))
        if not valid_gap:
            raise AuthoringSourceManifestError('authoring_inventory_declaration_invalid', {'inventory': kind, 'item_sha256': _v6m_safe_value_sha256(gap.strip())})
        cursor = match.end()
    if body[cursor:].strip():
        raise AuthoringSourceManifestError('authoring_inventory_declaration_invalid', {'inventory': kind, 'item_sha256': _v6m_safe_value_sha256(body[cursor:].strip())})
    return matches

def _v6m_source_relation_keys(source: str, *, relations: Iterable[str], relation_endpoints: Mapping[str, Mapping[str, str]], dataset_fields: Mapping[str, Iterable[str]]) -> tuple[dict[str, dict[str, list[str]]], bool]:
    declarations = list(_v6m_RELATION_KEYS_RE.finditer(source))
    registered_relations = set(relations)
    registered_fields = {str(dataset_id): {str(field_id) for field_id in fields} for dataset_id, fields in dataset_fields.items()}
    keys_by_relation: dict[str, dict[str, list[str]]] = {}
    for declaration in declarations:
        for item in _v6m_closed_declaration_matches(declaration.group('items'), _v6m_RELATION_KEY_ITEM_RE, kind='relation_keys'):
            relation_id = item.group('relation')
            if relation_id not in registered_relations:
                raise AuthoringSourceManifestError('authoring_relation_key_relation_unknown', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
            endpoints = relation_endpoints.get(relation_id)
            if not isinstance(endpoints, Mapping):
                raise AuthoringSourceManifestError('authoring_relation_key_endpoint_missing', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
            left_keys = [value.strip() for value in item.group('left').split('|')]
            right_keys = [value.strip() for value in item.group('right').split('|')]
            if not left_keys or len(left_keys) != len(right_keys):
                raise AuthoringSourceManifestError('authoring_relation_key_cardinality_invalid', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
            left_dataset = str(endpoints.get('left_dataset') or '')
            right_dataset = str(endpoints.get('right_dataset') or '')
            unknown_left = [value for value in left_keys if value not in registered_fields.get(left_dataset, set())]
            unknown_right = [value for value in right_keys if value not in registered_fields.get(right_dataset, set())]
            if unknown_left or unknown_right:
                raise AuthoringSourceManifestError('authoring_relation_key_field_unknown', {'relation_sha256': _v6m_safe_value_sha256(relation_id), 'left_key_sha256': [_v6m_safe_value_sha256(value) for value in unknown_left], 'right_key_sha256': [_v6m_safe_value_sha256(value) for value in unknown_right]})
            card = {'left_keys': left_keys, 'right_keys': right_keys}
            existing = keys_by_relation.get(relation_id)
            if existing is not None and existing != card:
                raise AuthoringSourceManifestError('authoring_relation_key_ambiguous', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
            keys_by_relation[relation_id] = card
    if len(keys_by_relation) > _v6mMAX_INVENTORY['relation_keys']:
        raise AuthoringSourceManifestError('authoring_inventory_limit_exceeded', {'inventory': 'relation_keys', 'count': len(keys_by_relation), 'limit': _v6mMAX_INVENTORY['relation_keys']})
    return ({key: keys_by_relation[key] for key in sorted(keys_by_relation)}, bool(declarations))

def _v6m_source_field_roles(source: str, *, dataset_fields: Mapping[str, Iterable[str]]) -> tuple[dict[str, dict[str, list[str]]], bool]:
    declarations = list(_v6m_FIELD_ROLES_RE.finditer(source))
    bindings: dict[tuple[str, str], list[str]] = {}
    registered = {(str(dataset_id), str(field_id)) for dataset_id, fields in dataset_fields.items() for field_id in fields}
    for declaration in declarations:
        for item in _v6m_closed_declaration_matches(declaration.group('items'), _v6m_FIELD_ROLE_ITEM_RE, kind='field_roles'):
            dataset_id = item.group('dataset')
            field_id = item.group('field')
            binding = (dataset_id, field_id)
            if binding not in registered:
                raise AuthoringSourceManifestError('authoring_field_role_binding_unknown', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id)})
            raw_roles = [value.strip() for value in item.group('roles').split('|')]
            if len(raw_roles) != len(set(raw_roles)) or any((value not in _v6m_FIELD_ROLE_SET for value in raw_roles)):
                raise AuthoringSourceManifestError('authoring_field_role_value_invalid', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id), 'role_sha256': [_v6m_safe_value_sha256(value) for value in raw_roles]})
            roles = [role for role in _v6m_FIELD_ROLE_ORDER if role in raw_roles]
            existing = bindings.get(binding)
            if existing is not None and existing != roles:
                raise AuthoringSourceManifestError('authoring_field_role_binding_ambiguous', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id)})
            bindings[binding] = roles
    if len(bindings) > _v6mMAX_INVENTORY['field_roles']:
        raise AuthoringSourceManifestError('authoring_inventory_limit_exceeded', {'inventory': 'field_roles', 'count': len(bindings), 'limit': _v6mMAX_INVENTORY['field_roles']})
    result: dict[str, dict[str, list[str]]] = {}
    for (dataset_id, field_id), roles in sorted(bindings.items()):
        result.setdefault(dataset_id, {})[field_id] = roles
    return (result, bool(declarations))

def _v6m_source_grain_contract(source: str, *, fields: Iterable[str], field_roles: Mapping[str, Mapping[str, Iterable[str]]]) -> tuple[dict[str, list[str]], dict[str, list[str]], bool, bool]:
    registered_fields = set(fields)
    roles_by_field: dict[str, set[str]] = {}
    for dataset_roles in field_roles.values():
        for field_id, roles in dataset_roles.items():
            roles_by_field.setdefault(str(field_id), set()).update((str(value) for value in roles))
    key_declarations = list(_v6m_GRAIN_KEYS_RE.finditer(source))
    grain_keys: dict[str, list[str]] = {}
    for declaration in key_declarations:
        for item in _v6m_closed_declaration_matches(declaration.group('items'), _v6m_GRAIN_KEY_ITEM_RE, kind='grain_keys'):
            grain_id = item.group('grain')
            keys = [value.strip() for value in item.group('keys').split('|')]
            if len(keys) != len(set(keys)) or any((value not in registered_fields for value in keys)):
                raise AuthoringSourceManifestError('authoring_grain_key_field_unknown', {'grain_sha256': _v6m_safe_value_sha256(grain_id), 'field_sha256': [_v6m_safe_value_sha256(value) for value in keys]})
            incompatible = [value for value in keys if roles_by_field and (not roles_by_field.get(value, set()) & {'group', 'join'})]
            if incompatible:
                raise AuthoringSourceManifestError('authoring_grain_key_role_invalid', {'grain_sha256': _v6m_safe_value_sha256(grain_id), 'field_sha256': [_v6m_safe_value_sha256(value) for value in incompatible]})
            existing = grain_keys.get(grain_id)
            if existing is not None and existing != keys:
                raise AuthoringSourceManifestError('authoring_grain_key_ambiguous', {'grain_sha256': _v6m_safe_value_sha256(grain_id)})
            grain_keys[grain_id] = keys
    if len(grain_keys) > _v6mMAX_INVENTORY['grain_keys']:
        raise AuthoringSourceManifestError('authoring_inventory_limit_exceeded', {'inventory': 'grain_keys', 'count': len(grain_keys), 'limit': _v6mMAX_INVENTORY['grain_keys']})
    display_declarations = list(_v6m_GRAIN_DISPLAY_FIELDS_RE.finditer(source))
    grain_display_fields: dict[str, list[str]] = {grain_id: [] for grain_id in grain_keys} if display_declarations else {}
    seen_display: set[str] = set()
    for declaration in display_declarations:
        for item in _v6m_closed_declaration_matches(declaration.group('items'), _v6m_GRAIN_DISPLAY_FIELD_ITEM_RE, kind='grain_display_fields'):
            grain_id = item.group('grain')
            values = [value.strip() for value in item.group('fields').split('|')]
            if grain_id not in grain_keys:
                raise AuthoringSourceManifestError('authoring_grain_display_grain_unknown', {'grain_sha256': _v6m_safe_value_sha256(grain_id)})
            if len(values) != len(set(values)) or any((value not in registered_fields for value in values)):
                raise AuthoringSourceManifestError('authoring_grain_display_field_unknown', {'grain_sha256': _v6m_safe_value_sha256(grain_id), 'field_sha256': [_v6m_safe_value_sha256(value) for value in values]})
            if grain_id in seen_display and grain_display_fields[grain_id] != values:
                raise AuthoringSourceManifestError('authoring_grain_display_ambiguous', {'grain_sha256': _v6m_safe_value_sha256(grain_id)})
            seen_display.add(grain_id)
            grain_display_fields[grain_id] = values
    if len(grain_display_fields) > _v6mMAX_INVENTORY['grain_display_fields']:
        raise AuthoringSourceManifestError('authoring_inventory_limit_exceeded', {'inventory': 'grain_display_fields', 'count': len(grain_display_fields), 'limit': _v6mMAX_INVENTORY['grain_display_fields']})
    return ({key: grain_keys[key] for key in sorted(grain_keys)}, {key: grain_display_fields[key] for key in sorted(grain_display_fields)}, bool(key_declarations), bool(display_declarations))

def _v6m_source_relation_policies(source: str, *, relations: Iterable[str]) -> tuple[dict[str, dict[str, str]], bool]:
    declarations = list(_v6m_RELATION_POLICIES_RE.finditer(source))
    registered = set(relations)
    policies: dict[str, dict[str, str]] = {}
    for declaration in declarations:
        for item in _v6m_closed_declaration_matches(declaration.group('items'), _v6m_RELATION_POLICY_ITEM_RE, kind='relation_policies'):
            relation_id = item.group('relation')
            if relation_id not in registered:
                raise AuthoringSourceManifestError('authoring_relation_policy_relation_unknown', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
            card = {key: item.group(key) for key in ('join_type', 'cardinality', 'null_key_policy', 'multi_match_policy')}
            invalid = [key for key, value in card.items() if value not in _v6m_RELATION_POLICY_VALUES[key]]
            if invalid:
                raise AuthoringSourceManifestError('authoring_relation_policy_value_invalid', {'relation_sha256': _v6m_safe_value_sha256(relation_id), 'policy_keys': invalid, 'value_sha256': [_v6m_safe_value_sha256(card[key]) for key in invalid]})
            existing = policies.get(relation_id)
            if existing is not None and existing != card:
                raise AuthoringSourceManifestError('authoring_relation_policy_ambiguous', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
            policies[relation_id] = card
    if len(policies) > _v6mMAX_INVENTORY['relation_policies']:
        raise AuthoringSourceManifestError('authoring_inventory_limit_exceeded', {'inventory': 'relation_policies', 'count': len(policies), 'limit': _v6mMAX_INVENTORY['relation_policies']})
    return ({key: policies[key] for key in sorted(policies)}, bool(declarations))

def extract_authoring_source_manifest(source_text: str) -> dict[str, Any]:
    """Extract explicit inventory IDs from Korean or English authoring prose.

    The returned manifest contains identifiers and hashes, never ``source_text``
    or any prose excerpt.  It is content-addressed so a caller cannot alter an
    expected inventory between model invocation and deterministic compilation.
    """
    source, source_sha256 = _v6m_normalized_source(source_text)
    dataset_matches = list(_v6m_DATASET_RE.finditer(source))
    dataset_fields: dict[str, set[str]] = {}
    for index, match in enumerate(dataset_matches):
        dataset_id = match.group('dataset')
        block_end = dataset_matches[index + 1].start() if index + 1 < len(dataset_matches) else len(source)
        block = source[match.end():block_end]
        field_matches = list(_v6m_CANONICAL_FIELDS_RE.finditer(block))
        fields: set[str] = dataset_fields.setdefault(dataset_id, set())
        for field_match in field_matches:
            parsed = _v6m_declaration_items(field_match.group('items'))
            if not parsed:
                raise AuthoringSourceManifestError('authoring_inventory_declaration_empty', {'inventory': 'fields', 'dataset_sha256': hashlib.sha256(dataset_id.encode('utf-8')).hexdigest()})
            fields.update(parsed)
    datasets = _v6m_bounded(dataset_fields, 'datasets')
    normalized_dataset_fields = {dataset_id: _v6m_bounded(dataset_fields[dataset_id], 'fields') for dataset_id in datasets}
    field_bindings = sum((len(values) for values in normalized_dataset_fields.values()))
    if field_bindings > _v6mMAX_INVENTORY['field_bindings']:
        raise AuthoringSourceManifestError('authoring_inventory_limit_exceeded', {'inventory': 'field_bindings', 'count': field_bindings, 'limit': _v6mMAX_INVENTORY['field_bindings']})
    unique_fields = _v6m_bounded((field for values in normalized_dataset_fields.values() for field in values), 'fields')
    metrics, metrics_declared = _v6m_collect_declared_list(_v6m_METRICS_RE, source, 'metrics')
    relations, relations_declared = _v6m_collect_declared_list(_v6m_RELATIONS_RE, source, 'relations')
    relation_endpoints, relation_endpoints_declared = _v6m_source_relation_endpoints(source, relations=relations, datasets=datasets)
    relation_keys, relation_keys_declared = _v6m_source_relation_keys(source, relations=relations, relation_endpoints=relation_endpoints, dataset_fields=normalized_dataset_fields)
    field_roles, field_roles_declared = _v6m_source_field_roles(source, dataset_fields=normalized_dataset_fields)
    grain_keys, grain_display_fields, grain_keys_declared, grain_display_fields_declared = _v6m_source_grain_contract(source, fields=unique_fields, field_roles=field_roles)
    relation_policies, relation_policies_declared = _v6m_source_relation_policies(source, relations=relations)
    operations, operations_declared = _v6m_collect_declared_list(_v6m_OPERATIONS_RE, source, 'operations')
    recipes, recipe_ids_declared = _v6m_collect_declared_list(_v6m_RECIPE_IDS_RE, source, 'recipes')
    recipes = _v6m_bounded([*recipes, *(match.group('recipe') for match in _v6m_NAMED_RECIPE_RE.finditer(source))], 'recipes')
    alias_bindings, aliases_declared = _v6m_source_alias_bindings(source)
    aliases = sorted({item['alias'] for item in alias_bindings})
    alias_targets = sorted({item['target'] for item in alias_bindings})
    required_sections = sorted({*(['datasets'] if dataset_matches else []), *(['fields'] if field_bindings else []), *(['field_roles'] if field_roles_declared else []), *(['metrics'] if metrics_declared else []), *(['grains'] if grain_keys_declared else []), *(['grain_keys'] if grain_keys_declared else []), *(['grain_display_fields'] if grain_display_fields_declared else []), *(['relations'] if relations_declared else []), *(['relation_endpoints'] if relation_endpoints_declared else []), *(['relation_keys'] if relation_keys_declared else []), *(['relation_policies'] if relation_policies_declared else []), *(['operations'] if operations_declared else []), *(['recipes'] if recipe_ids_declared or recipes else []), *(['aliases'] if aliases_declared else [])})
    inventories = {'datasets': datasets, 'dataset_fields': normalized_dataset_fields, 'fields': unique_fields, 'field_roles': field_roles, 'metrics': metrics, 'grains': sorted(grain_keys), 'grain_keys': grain_keys, 'grain_display_fields': grain_display_fields, 'relations': relations, 'relation_endpoints': relation_endpoints, 'relation_keys': relation_keys, 'relation_policies': relation_policies, 'recipes': recipes, 'operations': operations, 'aliases': aliases, 'alias_targets': alias_targets, 'alias_bindings': alias_bindings}
    counts = {'datasets': len(datasets), 'fields': len(unique_fields), 'field_bindings': field_bindings, 'field_roles': sum((len(values) for values in field_roles.values())), 'metrics': len(metrics), 'grains': len(grain_keys), 'grain_keys': len(grain_keys), 'grain_display_fields': len(grain_display_fields), 'relations': len(relations), 'relation_endpoints': len(relation_endpoints), 'relation_keys': len(relation_keys), 'relation_policies': len(relation_policies), 'recipes': len(recipes), 'operations': len(operations), 'aliases': len(aliases), 'alias_targets': len(alias_targets), 'alias_bindings': len(alias_bindings)}
    material = {'contract_version': _v6mMANIFEST_VERSION, 'source_sha256': source_sha256, 'inventories': inventories, 'required_sections': required_sections, 'counts': counts}
    return {**material, 'manifest_sha256': _v6m_canonical_sha256(material)}

def _v6m_validated_manifest(value: Mapping[str, Any]) -> dict[str, Any]:
    manifest = deepcopy(dict(value))
    expected_keys = {'contract_version', 'source_sha256', 'inventories', 'required_sections', 'counts', 'manifest_sha256'}
    if set(manifest) != expected_keys or manifest.get('contract_version') != _v6mMANIFEST_VERSION:
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    if not _v6m_SHA256_RE.fullmatch(str(manifest.get('source_sha256') or '')):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    supplied_hash = str(manifest.pop('manifest_sha256', ''))
    expected_hash = _v6m_canonical_sha256(manifest)
    if supplied_hash != expected_hash:
        raise AuthoringSourceManifestError('authoring_source_manifest_hash_mismatch', {'expected_sha256': expected_hash, 'actual_sha256': supplied_hash})
    manifest['manifest_sha256'] = supplied_hash
    return manifest

def validate_authoring_source_manifest(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and copy a sealed source manifest.

    This public boundary is intentionally small.  Trusted executable
    blueprints use the manifest hash as an independently supplied source pin,
    so callers must be able to validate the manifest before trusting that pin.
    """
    if not isinstance(value, Mapping):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    return _v6m_validated_manifest(value)

def _v6m_safe_value_sha256(value: Any) -> str:
    """Hash untrusted authoring values without retaining them in evidence."""
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest()

def _v6m_manifest_alias_targets(manifest: Mapping[str, Any]) -> dict[str, str]:
    inventories = manifest.get('inventories')
    bindings = inventories.get('alias_bindings') if isinstance(inventories, Mapping) else None
    if not isinstance(bindings, list):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    targets: dict[str, str] = {}
    for raw_binding in bindings:
        if not isinstance(raw_binding, Mapping) or set(raw_binding) != {'alias', 'target'}:
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        raw_alias = raw_binding.get('alias')
        raw_target = raw_binding.get('target')
        if not isinstance(raw_alias, str) or not isinstance(raw_target, str):
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        alias = _v6m_normalized_alias(raw_alias)
        if alias != raw_alias or not re.fullmatch(_v6m_IDENTIFIER, raw_target):
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        existing = targets.get(alias)
        if existing is not None and existing != raw_target:
            raise AuthoringSourceManifestError('authoring_alias_target_ambiguous', {'alias_sha256': _v6m_safe_value_sha256(alias)})
        targets[alias] = raw_target
    return targets

def _v6m_manifest_relation_endpoints(manifest: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    inventories = manifest.get('inventories')
    if not isinstance(inventories, Mapping):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    raw_endpoints = inventories.get('relation_endpoints')
    if not isinstance(raw_endpoints, Mapping):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    raw_relations = inventories.get('relations')
    raw_datasets = inventories.get('datasets')
    if not isinstance(raw_relations, list) or not isinstance(raw_datasets, list):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    relations = {str(value) for value in raw_relations}
    datasets = {str(value) for value in raw_datasets}
    endpoints: dict[str, dict[str, str]] = {}
    for relation_id, raw_card in raw_endpoints.items():
        if not isinstance(relation_id, str) or not isinstance(raw_card, Mapping):
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        if set(raw_card) != {'left_dataset', 'right_dataset'}:
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        left_dataset = raw_card.get('left_dataset')
        right_dataset = raw_card.get('right_dataset')
        if relation_id not in relations or not isinstance(left_dataset, str) or (not isinstance(right_dataset, str)) or (left_dataset not in datasets) or (right_dataset not in datasets):
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        endpoints[relation_id] = {'left_dataset': left_dataset, 'right_dataset': right_dataset}
    return {key: endpoints[key] for key in sorted(endpoints)}

def _v6m_manifest_field_roles(manifest: Mapping[str, Any]) -> dict[str, dict[str, list[str]]]:
    inventories = manifest.get('inventories')
    raw_roles = inventories.get('field_roles') if isinstance(inventories, Mapping) else None
    raw_dataset_fields = inventories.get('dataset_fields') if isinstance(inventories, Mapping) else None
    if not isinstance(raw_roles, Mapping) or not isinstance(raw_dataset_fields, Mapping):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    result: dict[str, dict[str, list[str]]] = {}
    for dataset_id, raw_fields in raw_roles.items():
        registered_fields = raw_dataset_fields.get(dataset_id)
        if not isinstance(dataset_id, str) or not isinstance(raw_fields, Mapping) or (not isinstance(registered_fields, list)):
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        for field_id, raw_values in raw_fields.items():
            if not isinstance(field_id, str) or field_id not in registered_fields or (not isinstance(raw_values, list)) or (not raw_values) or (not all((isinstance(value, str) for value in raw_values))):
                raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
            values = [role for role in _v6m_FIELD_ROLE_ORDER if role in raw_values]
            if len(values) != len(raw_values) or values != raw_values:
                raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
            result.setdefault(dataset_id, {})[field_id] = values
    return {dataset_id: {field_id: result[dataset_id][field_id] for field_id in sorted(result[dataset_id])} for dataset_id in sorted(result)}

def _v6m_manifest_relation_keys(manifest: Mapping[str, Any]) -> dict[str, dict[str, list[str]]]:
    inventories = manifest.get('inventories')
    raw_keys = inventories.get('relation_keys') if isinstance(inventories, Mapping) else None
    raw_relations = inventories.get('relations') if isinstance(inventories, Mapping) else None
    raw_endpoints = inventories.get('relation_endpoints') if isinstance(inventories, Mapping) else None
    raw_dataset_fields = inventories.get('dataset_fields') if isinstance(inventories, Mapping) else None
    if not isinstance(raw_keys, Mapping) or not isinstance(raw_relations, list) or (not isinstance(raw_endpoints, Mapping)) or (not isinstance(raw_dataset_fields, Mapping)):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    result: dict[str, dict[str, list[str]]] = {}
    for relation_id, raw_card in raw_keys.items():
        endpoints = raw_endpoints.get(relation_id)
        if not isinstance(relation_id, str) or relation_id not in raw_relations or (not isinstance(raw_card, Mapping)) or (set(raw_card) != {'left_keys', 'right_keys'}) or (not isinstance(endpoints, Mapping)):
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        left_keys = raw_card.get('left_keys')
        right_keys = raw_card.get('right_keys')
        if not isinstance(left_keys, list) or not isinstance(right_keys, list) or (not left_keys) or (len(left_keys) != len(right_keys)) or (not all((isinstance(value, str) for value in [*left_keys, *right_keys]))):
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        left_fields = raw_dataset_fields.get(endpoints.get('left_dataset'))
        right_fields = raw_dataset_fields.get(endpoints.get('right_dataset'))
        if not isinstance(left_fields, list) or not isinstance(right_fields, list) or (not set(left_keys) <= set(left_fields)) or (not set(right_keys) <= set(right_fields)):
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        result[relation_id] = {'left_keys': list(left_keys), 'right_keys': list(right_keys)}
    return {key: result[key] for key in sorted(result)}

def _v6m_manifest_relation_policies(manifest: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    inventories = manifest.get('inventories')
    raw_policies = inventories.get('relation_policies') if isinstance(inventories, Mapping) else None
    raw_relations = inventories.get('relations') if isinstance(inventories, Mapping) else None
    if not isinstance(raw_policies, Mapping) or not isinstance(raw_relations, list):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    policies: dict[str, dict[str, str]] = {}
    required_keys = set(_v6m_RELATION_POLICY_VALUES)
    for relation_id, raw_card in raw_policies.items():
        if not isinstance(relation_id, str) or relation_id not in raw_relations or (not isinstance(raw_card, Mapping)) or (set(raw_card) != required_keys):
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        card: dict[str, str] = {}
        for key in _v6m_RELATION_POLICY_VALUES:
            value = raw_card.get(key)
            if not isinstance(value, str) or value not in _v6m_RELATION_POLICY_VALUES[key]:
                raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
            card[key] = value
        policies[relation_id] = card
    return {key: policies[key] for key in sorted(policies)}

def _v6m_manifest_grain_contract(manifest: Mapping[str, Any]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    inventories = manifest.get('inventories')
    raw_grains = inventories.get('grains') if isinstance(inventories, Mapping) else None
    raw_keys = inventories.get('grain_keys') if isinstance(inventories, Mapping) else None
    raw_display = inventories.get('grain_display_fields') if isinstance(inventories, Mapping) else None
    raw_fields = inventories.get('fields') if isinstance(inventories, Mapping) else None
    if not isinstance(raw_grains, list) or not isinstance(raw_keys, Mapping) or (not isinstance(raw_display, Mapping)) or (not isinstance(raw_fields, list)) or (sorted(raw_keys) != raw_grains) or (raw_display and set(raw_display) != set(raw_grains)):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    registered_fields = set(raw_fields)
    keys: dict[str, list[str]] = {}
    display: dict[str, list[str]] = {}
    for grain_id in raw_grains:
        values = raw_keys.get(grain_id)
        if not isinstance(grain_id, str) or not isinstance(values, list) or (not values) or (len(values) != len(set(values))) or (not all((isinstance(value, str) and value in registered_fields for value in values))):
            raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
        keys[grain_id] = list(values)
        if raw_display:
            display_values = raw_display.get(grain_id)
            if not isinstance(display_values, list) or len(display_values) != len(set(display_values)) or (not all((isinstance(value, str) and value in registered_fields for value in display_values))):
                raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
            display[grain_id] = list(display_values)
    return (keys, display)

def _v6m_draft_alias_target_index(draft: Mapping[str, Any]) -> dict[str, set[str]]:
    """Return registered target types keyed by target ID.

    A field repeated in multiple datasets remains one ``field`` target.  The
    same ID registered as, for example, both a field and a metric is ambiguous
    for shorthand and therefore retains both types in the index.
    """
    index: dict[str, set[str]] = {}

    def add(target_key: Any, target_type: str) -> None:
        if isinstance(target_key, str):
            index.setdefault(target_key, set()).add(target_type)
    for section, target_type in _v6m_ALIAS_TARGET_SECTIONS:
        cards = draft.get(section)
        if cards is None:
            continue
        if not isinstance(cards, Mapping):
            raise AuthoringSourceManifestError('authoring_alias_target_registry_invalid', {'section': section})
        for target_key in cards:
            add(target_key, target_type)
    datasets = draft.get('datasets')
    if isinstance(datasets, Mapping):
        for dataset in datasets.values():
            if not isinstance(dataset, Mapping):
                continue
            fields = dataset.get('fields')
            if fields is None:
                continue
            if not isinstance(fields, Mapping):
                raise AuthoringSourceManifestError('authoring_alias_target_registry_invalid', {'section': 'datasets.fields'})
            for field_key in fields:
                add(field_key, 'field')
    return index

def _v6m_alias_target_index_with_context(draft: Mapping[str, Any], target_context: Mapping[str, Any] | None=None) -> dict[str, set[str]]:
    """Union read-only target namespaces without copying context into output."""
    index = _v6m_draft_alias_target_index(draft)
    if target_context is None:
        return index
    if not isinstance(target_context, Mapping):
        raise AuthoringSourceManifestError('authoring_target_context_invalid')
    for target_key, target_types in _v6m_draft_alias_target_index(target_context).items():
        index.setdefault(target_key, set()).update(target_types)
    return index

def _v6m_mapping_upsert(base: Mapping[str, Any], patch: Mapping[str, Any]) -> dict[str, Any]:
    result = deepcopy(dict(base))
    for key, value in patch.items():
        if isinstance(result.get(key), Mapping) and isinstance(value, Mapping):
            result[key] = _v6m_mapping_upsert(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result

def _v6m_merge_alias_values(base_values: Any, patch_values: Any, *, alias_id: str) -> list[Any]:
    """Preserve legacy alias cards while appending source-sealed text values.

    Generic v2 packages normally store alias values as strings.  A migrated v5
    package may retain ``{"text": ..., "priority": ...}`` value cards.  Section
    authoring must not discard those priorities merely because a new alias is
    supplied in the compact string form.
    """
    if not isinstance(base_values, list) or not isinstance(patch_values, list):
        raise AuthoringSourceManifestError('authoring_alias_card_invalid', {'alias_sha256': _v6m_safe_value_sha256(alias_id)})

    def text_of(value: Any, *, allow_mapping: bool) -> str:
        if isinstance(value, str):
            return value
        if allow_mapping and isinstance(value, Mapping) and isinstance(value.get('text'), str):
            return str(value['text'])
        raise AuthoringSourceManifestError('authoring_alias_card_invalid', {'alias_sha256': _v6m_safe_value_sha256(alias_id)})
    if all((isinstance(value, str) for value in base_values)):
        if not all((isinstance(value, str) for value in patch_values)):
            raise AuthoringSourceManifestError('authoring_alias_card_invalid', {'alias_sha256': _v6m_safe_value_sha256(alias_id)})
        return sorted(set(base_values) | set(patch_values))
    merged = deepcopy(base_values)
    seen = {_v6m_normalized_alias(text_of(value, allow_mapping=True)) for value in base_values}
    additions: list[str] = []
    for value in patch_values:
        text = text_of(value, allow_mapping=False)
        normalized = _v6m_normalized_alias(text)
        if normalized not in seen:
            seen.add(normalized)
            additions.append(text)
    merged.extend(sorted(additions, key=lambda value: (_v6m_normalized_alias(value), value)))
    return merged

def _v6m_normalize_dataset_field_roles(manifest: Mapping[str, Any], draft: dict[str, Any]) -> None:
    """Normalize field roles only against dataset/field roles sealed in source."""
    expected_roles = _v6m_manifest_field_roles(manifest)
    datasets = draft.get('datasets')
    if not isinstance(datasets, Mapping):
        return
    for dataset_id, raw_dataset in datasets.items():
        fields = raw_dataset.get('fields') if isinstance(raw_dataset, Mapping) else None
        if not isinstance(fields, Mapping):
            continue
        for field_id, raw_field in fields.items():
            roles = raw_field.get('roles') if isinstance(raw_field, Mapping) else None
            if (roles is None or roles == []) and field_id not in expected_roles.get(dataset_id, {}):
                raise AuthoringSourceManifestError('authoring_field_role_inventory_missing', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id)})
    for dataset_id, fields_by_id in expected_roles.items():
        dataset = datasets.get(dataset_id)
        if not isinstance(dataset, Mapping):
            continue
        fields = dataset.get('fields')
        if not isinstance(fields, Mapping):
            continue
        for field_id, sealed_roles in fields_by_id.items():
            field = fields.get(field_id)
            if not isinstance(field, dict):
                continue
            raw_roles = field.get('roles')
            if raw_roles is None or raw_roles == []:
                field['roles'] = deepcopy(sealed_roles)
                continue
            if not isinstance(raw_roles, list):
                raise AuthoringSourceManifestError('authoring_field_role_value_invalid', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id)})
            normalized: list[str] = []
            for raw_role in raw_roles:
                if not isinstance(raw_role, str):
                    raise AuthoringSourceManifestError('authoring_field_role_value_invalid', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id), 'role_sha256': _v6m_safe_value_sha256(raw_role)})
                candidates = [raw_role, raw_role.replace('-', '_')]
                if raw_role.endswith('_fields'):
                    candidates.append(raw_role[:-len('_fields')])
                role = next((value for value in candidates if value in sealed_roles), '')
                if not role:
                    raise AuthoringSourceManifestError('authoring_field_role_value_invalid', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id), 'role_sha256': _v6m_safe_value_sha256(raw_role)})
                if role not in normalized:
                    normalized.append(role)
            if set(normalized) != set(sealed_roles):
                raise AuthoringSourceManifestError('authoring_field_role_mismatch', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id), 'expected_sha256': _v6m_canonical_sha256(sealed_roles), 'actual_sha256': _v6m_canonical_sha256(normalized)})
            field['roles'] = deepcopy(sealed_roles)

def _v6m_normalize_dataset_patch_against_base(manifest: Mapping[str, Any], draft: dict[str, Any], base_draft: Mapping[str, Any] | None) -> None:
    """Close provider dataset/field keys against source inventory and base.

    Existing physical column names and physical aliases may be mapped back to
    one canonical field only when that mapping is unique.  Existing cards are
    deep-merged before schema validation so an annotation-sized provider patch
    cannot accidentally erase required execution semantics.  A genuinely new
    dataset or field remains possible only when its identifier is explicitly
    sealed by the reviewed source manifest.
    """
    datasets = draft.get('datasets')
    if datasets is None:
        return
    if not isinstance(datasets, Mapping):
        raise AuthoringSourceManifestError('authoring_dataset_registry_invalid')
    inventories = manifest.get('inventories')
    if not isinstance(inventories, Mapping):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    raw_declared_datasets = inventories.get('datasets')
    raw_declared_fields = inventories.get('dataset_fields')
    if not isinstance(raw_declared_datasets, list) or not isinstance(raw_declared_fields, Mapping):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    declared_datasets = {str(value) for value in raw_declared_datasets}
    declared_fields = {str(dataset_id): {str(value) for value in values} for dataset_id, values in raw_declared_fields.items() if isinstance(dataset_id, str) and isinstance(values, list)}
    base_datasets = base_draft.get('datasets') if isinstance(base_draft, Mapping) and isinstance(base_draft.get('datasets'), Mapping) else {}
    normalized_datasets: dict[str, Any] = {}
    for raw_dataset_id, raw_dataset in datasets.items():
        dataset_id = str(raw_dataset_id)
        if dataset_id not in declared_datasets:
            raise AuthoringSourceManifestError('authoring_dataset_target_unknown', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id)})
        if not isinstance(raw_dataset, Mapping):
            raise AuthoringSourceManifestError('authoring_dataset_card_invalid', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id)})
        provider_dataset = deepcopy(dict(raw_dataset))
        base_dataset = base_datasets.get(dataset_id)
        base_fields = base_dataset.get('fields') if isinstance(base_dataset, Mapping) and isinstance(base_dataset.get('fields'), Mapping) else {}
        provider_fields = provider_dataset.get('fields')
        if provider_fields is not None:
            if not isinstance(provider_fields, Mapping):
                raise AuthoringSourceManifestError('authoring_dataset_fields_invalid', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id)})
            normalized_fields: dict[str, Any] = {}
            allowed_fields = declared_fields.get(dataset_id, set())
            for raw_field_id, raw_field in provider_fields.items():
                field_id = str(raw_field_id)
                canonical_field = field_id if field_id in base_fields else ''
                resolved_from_noncanonical_key = False
                if not canonical_field and base_fields:
                    token = field_id.casefold()
                    matches: list[str] = []
                    for candidate_id, candidate_card in base_fields.items():
                        if not isinstance(candidate_card, Mapping):
                            continue
                        physical_values = [str(candidate_id), str(candidate_card.get('physical_column') or ''), *[str(value) for value in candidate_card.get('physical_aliases') or [] if isinstance(value, str)]]
                        if token and token in {value.casefold() for value in physical_values if value}:
                            matches.append(str(candidate_id))
                    matches = sorted(set(matches))
                    if len(matches) > 1:
                        raise AuthoringSourceManifestError('authoring_dataset_field_target_ambiguous', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id), 'candidate_count': len(matches)})
                    if matches:
                        canonical_field = matches[0]
                        resolved_from_noncanonical_key = canonical_field != field_id
                if not canonical_field:
                    canonical_field = field_id
                if canonical_field not in allowed_fields:
                    raise AuthoringSourceManifestError('authoring_dataset_field_target_unknown', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id)})
                if canonical_field in normalized_fields:
                    raise AuthoringSourceManifestError('authoring_dataset_field_target_duplicate', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(canonical_field)})
                base_field = base_fields.get(canonical_field)
                if resolved_from_noncanonical_key:
                    if not isinstance(base_field, Mapping) or not isinstance(raw_field, Mapping):
                        raise AuthoringSourceManifestError('authoring_dataset_physical_alias_rebind_forbidden', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id), 'canonical_field_sha256': _v6m_safe_value_sha256(canonical_field)})
                    raw_field_value = dict(raw_field)
                    if raw_field_value and raw_field_value != dict(base_field):
                        raise AuthoringSourceManifestError('authoring_dataset_physical_alias_rebind_forbidden', {'dataset_sha256': _v6m_safe_value_sha256(dataset_id), 'field_sha256': _v6m_safe_value_sha256(field_id), 'canonical_field_sha256': _v6m_safe_value_sha256(canonical_field)})
                    raw_field = {}
                normalized_fields[canonical_field] = _v6m_mapping_upsert(base_field, raw_field) if isinstance(base_field, Mapping) and isinstance(raw_field, Mapping) else deepcopy(raw_field)
            provider_dataset['fields'] = {key: normalized_fields[key] for key in sorted(normalized_fields)}
        normalized_datasets[dataset_id] = _v6m_mapping_upsert(base_dataset, provider_dataset) if isinstance(base_dataset, Mapping) else provider_dataset
    draft['datasets'] = {key: normalized_datasets[key] for key in sorted(normalized_datasets)}

def _v6m_normalize_relation_policies(manifest: Mapping[str, Any], draft: dict[str, Any]) -> None:
    """Fill or canonicalize only relation policies sealed in source."""
    expected_policies = _v6m_manifest_relation_policies(manifest)
    relations = draft.get('relations')
    if relations is None:
        return
    if not isinstance(relations, Mapping):
        raise AuthoringSourceManifestError('authoring_relation_registry_invalid')
    for relation_id, raw_relation in relations.items():
        if not isinstance(raw_relation, Mapping) or relation_id in expected_policies:
            continue
        if any((raw_relation.get(key) is None or (isinstance(raw_relation.get(key), str) and (not raw_relation.get(key).strip())) for key in _v6m_RELATION_POLICY_VALUES)):
            raise AuthoringSourceManifestError('authoring_relation_policy_inventory_missing', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
    for relation_id, sealed_policy in expected_policies.items():
        relation = relations.get(relation_id)
        if not isinstance(relation, dict):
            continue
        for policy_key, expected_value in sealed_policy.items():
            legacy_key = 'type' if policy_key == 'join_type' else ''
            actual_value = relation.get(policy_key)
            legacy_present = bool(legacy_key and legacy_key in relation)
            legacy_value = relation.get(legacy_key) if legacy_present else None
            supplied = [value for value in (actual_value, legacy_value) if value is not None and (not (isinstance(value, str) and (not value.strip())))]
            for raw_value in supplied:
                normalized_value = raw_value.replace('-', '_') if isinstance(raw_value, str) else raw_value
                if normalized_value != expected_value:
                    raise AuthoringSourceManifestError('authoring_relation_policy_mismatch', {'relation_sha256': _v6m_safe_value_sha256(relation_id), 'policy_key': policy_key, 'expected_sha256': _v6m_safe_value_sha256(expected_value), 'actual_sha256': _v6m_safe_value_sha256(raw_value)})
            relation[policy_key] = expected_value
            if legacy_present:
                relation.pop(legacy_key, None)

def _v6m_normalize_relation_keys(manifest: Mapping[str, Any], draft: dict[str, Any]) -> None:
    """Fill relation key lists only from exact source-sealed mappings."""
    expected_keys = _v6m_manifest_relation_keys(manifest)
    relations = draft.get('relations')
    datasets = draft.get('datasets')
    if relations is None:
        return
    if not isinstance(relations, Mapping):
        raise AuthoringSourceManifestError('authoring_relation_registry_invalid')

    def blank(value: Any) -> bool:
        return value is None or value == [] or (isinstance(value, str) and (not value.strip()))

    def key_list(value: Any) -> list[str] | None:
        if isinstance(value, str) and value.strip():
            return [item.strip() for item in value.split('|') if item.strip()]
        if isinstance(value, list) and all((isinstance(item, str) for item in value)):
            return list(value)
        return None
    for relation_id, raw_relation in relations.items():
        if not isinstance(raw_relation, Mapping) or relation_id in expected_keys:
            continue
        if blank(raw_relation.get('left_keys')) or blank(raw_relation.get('right_keys')):
            raise AuthoringSourceManifestError('authoring_relation_key_inventory_missing', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
    for relation_id, sealed in expected_keys.items():
        relation = relations.get(relation_id)
        if not isinstance(relation, dict):
            continue
        left_dataset = str(relation.get('left_dataset') or '')
        right_dataset = str(relation.get('right_dataset') or '')
        left_fields = (datasets.get(left_dataset) or {}).get('fields') or {} if isinstance(datasets, Mapping) and isinstance(datasets.get(left_dataset), Mapping) else {}
        right_fields = (datasets.get(right_dataset) or {}).get('fields') or {} if isinstance(datasets, Mapping) and isinstance(datasets.get(right_dataset), Mapping) else {}
        if not set(sealed['left_keys']) <= set(left_fields) or not set(sealed['right_keys']) <= set(right_fields):
            raise AuthoringSourceManifestError('authoring_relation_key_field_unknown', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
        legacy_present = 'keys' in relation
        legacy_keys = key_list(relation.get('keys')) if legacy_present else None
        if legacy_present and (legacy_keys is None or legacy_keys != sealed['left_keys'] or legacy_keys != sealed['right_keys']):
            raise AuthoringSourceManifestError('authoring_relation_key_mismatch', {'relation_sha256': _v6m_safe_value_sha256(relation_id), 'key_side': 'legacy_keys'})
        mappings_present = 'key_mappings' in relation
        mappings = relation.get('key_mappings')
        if mappings_present:
            if not isinstance(mappings, list) or not all((isinstance(item, Mapping) for item in mappings)):
                raise AuthoringSourceManifestError('authoring_relation_key_mismatch', {'relation_sha256': _v6m_safe_value_sha256(relation_id), 'key_side': 'key_mappings'})
            mapped_left = [str(item.get('left') or '') for item in mappings]
            mapped_right = [str(item.get('right') or '') for item in mappings]
            if mapped_left != sealed['left_keys'] or mapped_right != sealed['right_keys']:
                raise AuthoringSourceManifestError('authoring_relation_key_mismatch', {'relation_sha256': _v6m_safe_value_sha256(relation_id), 'key_side': 'key_mappings'})
        for key_side in ('left_keys', 'right_keys'):
            actual = relation.get(key_side)
            if not blank(actual):
                normalized = key_list(actual)
                if normalized != sealed[key_side]:
                    raise AuthoringSourceManifestError('authoring_relation_key_mismatch', {'relation_sha256': _v6m_safe_value_sha256(relation_id), 'key_side': key_side})
            relation[key_side] = deepcopy(sealed[key_side])
        if legacy_present:
            relation.pop('keys', None)
        if mappings_present:
            relation.pop('key_mappings', None)

def _v6m_normalize_relation_endpoints(manifest: Mapping[str, Any], draft: dict[str, Any]) -> None:
    """Fill only source-sealed blank relation endpoints on a draft copy."""
    expected_endpoints = _v6m_manifest_relation_endpoints(manifest)
    relations = draft.get('relations')
    if relations is None:
        return
    if not isinstance(relations, Mapping):
        raise AuthoringSourceManifestError('authoring_relation_registry_invalid')
    datasets = draft.get('datasets')
    dataset_ids = set(datasets) if isinstance(datasets, Mapping) else set()

    def blank(value: Any) -> bool:
        return value is None or (isinstance(value, str) and (not value.strip()))
    for relation_id, raw_card in relations.items():
        if not isinstance(relation_id, str) or not isinstance(raw_card, dict):
            if relation_id in expected_endpoints:
                raise AuthoringSourceManifestError('authoring_relation_endpoint_card_invalid', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
            continue
        expected = expected_endpoints.get(relation_id)
        standard_missing = any((key not in raw_card or blank(raw_card.get(key)) for key in ('left_dataset', 'right_dataset')))
        if expected is None:
            if standard_missing:
                raise AuthoringSourceManifestError('authoring_relation_endpoint_inventory_missing', {'relation_sha256': _v6m_safe_value_sha256(relation_id)})
            continue
        missing_datasets = sorted((value for value in expected.values() if value not in dataset_ids))
        if missing_datasets:
            raise AuthoringSourceManifestError('authoring_relation_endpoint_dataset_unknown', {'relation_sha256': _v6m_safe_value_sha256(relation_id), 'dataset_sha256': [_v6m_safe_value_sha256(value) for value in missing_datasets]})
        for standard_key, legacy_key in (('left_dataset', 'left'), ('right_dataset', 'right')):
            expected_value = expected[standard_key]
            actual_value = raw_card.get(standard_key)
            legacy_present = legacy_key in raw_card
            legacy_value = raw_card.get(legacy_key)
            for supplied_value in (*([actual_value] if not blank(actual_value) else []), *([legacy_value] if legacy_present and (not blank(legacy_value)) else [])):
                if not isinstance(supplied_value, str) or supplied_value != expected_value:
                    raise AuthoringSourceManifestError('authoring_relation_endpoint_mismatch', {'relation_sha256': _v6m_safe_value_sha256(relation_id), 'endpoint': standard_key, 'expected_sha256': _v6m_safe_value_sha256(expected_value), 'actual_sha256': _v6m_safe_value_sha256(supplied_value)})
            if blank(actual_value):
                raw_card[standard_key] = expected_value
            if legacy_present:
                raw_card.pop(legacy_key, None)

def _v6m_normalize_grains(manifest: Mapping[str, Any], draft: dict[str, Any], target_context: Mapping[str, Any] | None=None) -> None:
    """Normalize grain keys/display fields only from the sealed source contract."""
    expected_keys, expected_display = _v6m_manifest_grain_contract(manifest)
    grains = draft.get('grains')
    if grains is None:
        return
    if not isinstance(grains, Mapping):
        raise AuthoringSourceManifestError('authoring_grain_registry_invalid')
    unbacked = sorted((str(grain_id) for grain_id in grains if grain_id not in expected_keys))
    if unbacked:
        raise AuthoringSourceManifestError('authoring_grain_inventory_unbacked', {'grain_sha256': [_v6m_safe_value_sha256(value) for value in unbacked]})
    target_index = _v6m_alias_target_index_with_context(draft, target_context)

    def blank(value: Any) -> bool:
        return value is None or value == [] or (isinstance(value, str) and (not value.strip()))

    def field_list(value: Any) -> list[str] | None:
        if isinstance(value, str) and value.strip():
            return [item.strip() for item in value.split('|') if item.strip()]
        if isinstance(value, list) and all((isinstance(item, str) for item in value)):
            return list(value)
        return None
    for grain_id, sealed_keys in expected_keys.items():
        grain = grains.get(grain_id)
        if not isinstance(grain, dict):
            continue
        unknown_fields = [value for value in [*sealed_keys, *expected_display.get(grain_id, [])] if 'field' not in target_index.get(value, set())]
        if unknown_fields:
            raise AuthoringSourceManifestError('authoring_grain_field_unknown', {'grain_sha256': _v6m_safe_value_sha256(grain_id), 'field_sha256': [_v6m_safe_value_sha256(value) for value in unknown_fields]})
        legacy_key_names = [name for name in ('key', 'grain_keys') if name in grain]
        for legacy_name in legacy_key_names:
            if field_list(grain.get(legacy_name)) != sealed_keys:
                raise AuthoringSourceManifestError('authoring_grain_key_mismatch', {'grain_sha256': _v6m_safe_value_sha256(grain_id)})
        actual_keys = grain.get('keys')
        if not blank(actual_keys) and field_list(actual_keys) != sealed_keys:
            raise AuthoringSourceManifestError('authoring_grain_key_mismatch', {'grain_sha256': _v6m_safe_value_sha256(grain_id)})
        grain['keys'] = deepcopy(sealed_keys)
        for legacy_name in legacy_key_names:
            grain.pop(legacy_name, None)
        if expected_display:
            sealed_display = expected_display[grain_id]
            legacy_display_names = [name for name in ('display', 'display_field') if name in grain]
            for legacy_name in legacy_display_names:
                if field_list(grain.get(legacy_name)) != sealed_display:
                    raise AuthoringSourceManifestError('authoring_grain_display_mismatch', {'grain_sha256': _v6m_safe_value_sha256(grain_id)})
            actual_display = grain.get('display_fields')
            if not blank(actual_display) and field_list(actual_display) != sealed_display:
                raise AuthoringSourceManifestError('authoring_grain_display_mismatch', {'grain_sha256': _v6m_safe_value_sha256(grain_id)})
            grain['display_fields'] = deepcopy(sealed_display)
            for legacy_name in legacy_display_names:
                grain.pop(legacy_name, None)

def _v6m_complete_manifest_aliases(manifest: Mapping[str, Any], draft: dict[str, Any], target_context: Mapping[str, Any] | None=None) -> None:
    """Complete only missing source-declared aliases on uniquely typed targets."""
    expected_targets = _v6m_manifest_alias_targets(manifest)
    aliases = draft.get('aliases')
    if not isinstance(aliases, dict):
        raise AuthoringSourceManifestError('authoring_aliases_not_object')
    target_index = _v6m_alias_target_index_with_context(draft, target_context)
    cards_by_target: dict[tuple[str, str], list[tuple[str, dict[str, Any]]]] = {}
    explicit_targets_by_alias: dict[str, set[str]] = {}
    for alias_id, raw_card in aliases.items():
        if not isinstance(alias_id, str) or not isinstance(raw_card, dict):
            continue
        target_type = raw_card.get('target_type')
        target_key = raw_card.get('target_key')
        if isinstance(target_type, str) and isinstance(target_key, str):
            cards_by_target.setdefault((target_type, target_key), []).append((alias_id, raw_card))
            values = raw_card.get('values')
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, str):
                        explicit_targets_by_alias.setdefault(_v6m_normalized_alias(value), set()).add(target_key)
    for (target_type, target_key), cards in cards_by_target.items():
        if len(cards) > 1:
            raise AuthoringSourceManifestError('authoring_alias_multiple_target_cards', {'target_type': target_type, 'target_sha256': _v6m_safe_value_sha256(target_key)})
    actual_inventory = _v6m_draft_inventory(draft, ())
    actual_targets_by_alias: dict[str, set[str]] = {}
    for binding in actual_inventory['alias_bindings']:
        actual_targets_by_alias.setdefault(binding['alias'], set()).add(binding['target'])
    for alias, expected_target in sorted(expected_targets.items()):
        actual_targets = actual_targets_by_alias.get(alias, set())
        if expected_target in actual_targets:
            continue
        explicit_targets = explicit_targets_by_alias.get(alias, set())
        if explicit_targets and explicit_targets != {expected_target}:
            raise AuthoringSourceManifestError('authoring_alias_label_target_conflict', {'alias_sha256': _v6m_safe_value_sha256(alias), 'expected_target_sha256': _v6m_safe_value_sha256(expected_target), 'actual_target_sha256': sorted((_v6m_safe_value_sha256(value) for value in explicit_targets))})
        target_types = sorted(target_index.get(expected_target, set()))
        if not target_types:
            raise AuthoringSourceManifestError('authoring_alias_target_unknown', {'target_sha256': _v6m_safe_value_sha256(expected_target)})
        if len(target_types) != 1:
            raise AuthoringSourceManifestError('authoring_alias_target_ambiguous', {'target_sha256': _v6m_safe_value_sha256(expected_target), 'target_types': target_types})
        target_type = target_types[0]
        target_pair = (target_type, expected_target)
        cards = cards_by_target.get(target_pair, [])
        if cards:
            _, card = cards[0]
            values = card.get('values')
            if not isinstance(values, list) or not all((isinstance(value, str) for value in values)):
                raise AuthoringSourceManifestError('authoring_alias_card_invalid', {'target_type': target_type, 'target_sha256': _v6m_safe_value_sha256(expected_target)})
            if alias not in {_v6m_normalized_alias(value) for value in values}:
                values.append(alias)
        else:
            canonical_key = f'{target_type}:{expected_target}'
            if canonical_key in aliases:
                raise AuthoringSourceManifestError('authoring_alias_card_collision', {'target_type': target_type, 'target_sha256': _v6m_safe_value_sha256(expected_target)})
            card = {'target_type': target_type, 'target_key': expected_target, 'values': [alias]}
            aliases[canonical_key] = card
            cards_by_target[target_pair] = [(canonical_key, card)]
        actual_targets_by_alias[alias] = {expected_target}
    draft['aliases'] = {key: aliases[key] for key in sorted(aliases)}

def _v6mnormalize_authoring_draft_shorthand(manifest: Mapping[str, Any], draft: Mapping[str, Any], target_context: Mapping[str, Any] | None=None) -> dict[str, Any]:
    """Normalize only source-sealed authoring shorthand before schema checks.

    The model may use a compact string form inside ``draft.aliases``.  This
    function accepts it only when the exact normalized label/target binding was
    extracted from the natural-language source and the target resolves to one
    registered draft namespace.  No target type is guessed.

    Existing object aliases are copied unchanged.  Mixing an object alias with
    shorthand for the same canonical target fails closed instead of silently
    choosing or merging two provider representations.  Multiple backed string
    labels for one target are merged into one deterministic canonical card.

    The same single pre-schema pass also maps the closed field-role synonym
    ``compare_fields`` to schema role ``compare`` and removes duplicate roles.
    All unknown role values remain untouched so schema validation still rejects
    them instead of this helper guessing at provider intent.
    """
    if not isinstance(manifest, Mapping):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    sealed_manifest = _v6m_validated_manifest(manifest)
    expected_targets = _v6m_manifest_alias_targets(sealed_manifest)
    if not isinstance(draft, Mapping):
        raise AuthoringSourceManifestError('authoring_draft_not_object')
    result = deepcopy(dict(draft))
    _v6m_normalize_dataset_field_roles(sealed_manifest, result)
    _v6m_normalize_relation_endpoints(sealed_manifest, result)
    _v6m_normalize_relation_keys(sealed_manifest, result)
    _v6m_normalize_relation_policies(sealed_manifest, result)
    _v6m_normalize_grains(sealed_manifest, result, target_context)
    raw_aliases = result.get('aliases')
    if raw_aliases is None:
        raw_aliases = {}
    if not isinstance(raw_aliases, Mapping):
        raise AuthoringSourceManifestError('authoring_aliases_not_object')
    target_index = _v6m_alias_target_index_with_context(result, target_context)
    object_aliases: dict[str, Any] = {}
    object_targets: set[tuple[str, str]] = set()
    shorthand: list[tuple[str, str]] = []
    for raw_label, raw_value in raw_aliases.items():
        if not isinstance(raw_label, str):
            raise AuthoringSourceManifestError('authoring_alias_entry_invalid')
        if isinstance(raw_value, Mapping):
            object_aliases[raw_label] = deepcopy(dict(raw_value))
            target_type = raw_value.get('target_type')
            target_key = raw_value.get('target_key')
            if isinstance(target_type, str) and isinstance(target_key, str):
                object_targets.add((target_type, target_key))
            continue
        if isinstance(raw_value, str):
            shorthand.append((raw_label, raw_value))
            continue
        raise AuthoringSourceManifestError('authoring_alias_entry_invalid', {'alias_sha256': _v6m_safe_value_sha256(raw_label)})
    generated: dict[str, dict[str, Any]] = {}
    for raw_label, raw_target in sorted(shorthand, key=lambda item: (_v6m_normalized_alias(item[0]), item[1])):
        alias = _v6m_normalized_alias(raw_label)
        expected_target = expected_targets.get(alias)
        if expected_target is None:
            raise AuthoringSourceManifestError('authoring_alias_shorthand_unbacked', {'alias_sha256': _v6m_safe_value_sha256(alias)})
        if raw_target != expected_target:
            raise AuthoringSourceManifestError('authoring_alias_shorthand_unbacked', {'alias_sha256': _v6m_safe_value_sha256(alias), 'target_sha256': _v6m_safe_value_sha256(raw_target)})
        target_types = sorted(target_index.get(raw_target, set()))
        if not target_types:
            raise AuthoringSourceManifestError('authoring_alias_target_unknown', {'target_sha256': _v6m_safe_value_sha256(raw_target)})
        if len(target_types) != 1:
            raise AuthoringSourceManifestError('authoring_alias_target_ambiguous', {'target_sha256': _v6m_safe_value_sha256(raw_target), 'target_types': target_types})
        target_type = target_types[0]
        canonical_key = f'{target_type}:{raw_target}'
        if canonical_key in object_aliases or (target_type, raw_target) in object_targets:
            raise AuthoringSourceManifestError('authoring_alias_object_string_collision', {'target_sha256': _v6m_safe_value_sha256(raw_target), 'target_type': target_type})
        card = generated.setdefault(canonical_key, {'target_type': target_type, 'target_key': raw_target, 'values': []})
        card['values'].append(alias)
    for card in generated.values():
        card['values'] = sorted(set(card['values']))
    result['aliases'] = {**{key: object_aliases[key] for key in sorted(object_aliases)}, **{key: generated[key] for key in sorted(generated)}}
    _v6m_complete_manifest_aliases(sealed_manifest, result, target_context)
    return result

def _v6mnormalize_authoring_section_patch_shorthand(manifest: Mapping[str, Any], patch: Mapping[str, Any], authoring_kind: str, base_draft: Mapping[str, Any] | None=None) -> dict[str, Any]:
    """Normalize only shorthand owned by one bounded authoring Flow.

    Dataset authoring owns only ``datasets``.  Running its response through the
    full-draft normalizer would synthesize an empty ``aliases`` section and then
    make the deterministic ownership gate reject an otherwise valid patch.
    This helper deliberately preserves provider root keys so an explicitly
    emitted cross-owner section is still rejected by ``apply_authoring_section_patch``.

    Main-filter authoring owns aliases and may therefore use the complete
    source-sealed alias normalization.  The full normalizer's empty synthetic
    alias object is removed only when the provider did not emit ``aliases`` and
    the source manifest did not require any aliases to be completed.
    """
    if not isinstance(manifest, Mapping):
        raise AuthoringSourceManifestError('authoring_source_manifest_invalid')
    sealed_manifest = _v6m_validated_manifest(manifest)
    if not isinstance(patch, Mapping):
        raise AuthoringSourceManifestError('authoring_draft_not_object')
    kind = str(authoring_kind or '').strip().casefold()
    result = deepcopy(dict(patch))
    if kind == 'dataset':
        _v6m_normalize_dataset_patch_against_base(sealed_manifest, result, base_draft)
        _v6m_normalize_dataset_field_roles(sealed_manifest, result)
        return result
    if kind == 'main_filter':
        owned = {'aliases', 'entity_groups', 'grains', 'orderings', 'predicates', 'recipes'}
        if set(result) - owned:
            return result
        if not isinstance(base_draft, Mapping):
            raise AuthoringSourceManifestError('authoring_target_context_invalid')
        base_snapshot = deepcopy(dict(base_draft))
        base_aliases = base_snapshot.get('aliases')
        if not isinstance(base_aliases, Mapping):
            raise AuthoringSourceManifestError('authoring_aliases_not_object')
        provider_aliases = result.get('aliases')
        if isinstance(provider_aliases, Mapping):
            prepared_aliases: dict[str, Any] = {}
            for alias_id, raw_card in provider_aliases.items():
                base_card = base_aliases.get(alias_id)
                if isinstance(base_card, Mapping) and isinstance(raw_card, Mapping):
                    prepared_aliases[str(alias_id)] = _v6m_mapping_upsert(base_card, raw_card)
                else:
                    prepared_aliases[str(alias_id)] = deepcopy(raw_card)
            result['aliases'] = prepared_aliases
        result = _v6mnormalize_authoring_draft_shorthand(sealed_manifest, result, target_context=base_snapshot)
        normalized_aliases = result.get('aliases')
        if isinstance(normalized_aliases, Mapping):
            alias_delta: dict[str, Any] = {}
            for alias_id, raw_card in normalized_aliases.items():
                card = deepcopy(raw_card)
                base_card = base_aliases.get(alias_id)
                if isinstance(base_card, Mapping) and isinstance(card, Mapping):
                    for identity_key in ('target_type', 'target_key'):
                        base_value = base_card.get(identity_key)
                        card_value = card.get(identity_key)
                        if base_value != card_value:
                            raise AuthoringSourceManifestError('authoring_alias_target_mismatch', {'alias_sha256': _v6m_safe_value_sha256(alias_id), 'identity_key': identity_key})
                    card['values'] = _v6m_merge_alias_values(base_card.get('values'), card.get('values'), alias_id=str(alias_id))
                if base_card != card:
                    alias_delta[str(alias_id)] = card
            if alias_delta:
                result['aliases'] = {key: alias_delta[key] for key in sorted(alias_delta)}
            else:
                result.pop('aliases', None)
        if base_snapshot != dict(base_draft):
            raise AuthoringSourceManifestError('authoring_target_context_mutated')
        return result
    raise AuthoringSourceManifestError('authoring_section_patch_kind_invalid', {'authoring_kind': kind})

def _v6mnormalize_draft_alias_shorthand(manifest: Mapping[str, Any], draft: Mapping[str, Any]) -> dict[str, Any]:
    """Backward-compatible name for :func:`normalize_authoring_draft_shorthand`."""
    return _v6mnormalize_authoring_draft_shorthand(manifest, draft)

def _v6m_draft_operations(draft: Mapping[str, Any], supported_operations: Iterable[str]) -> list[str]:
    values: list[str] = [str(value) for value in supported_operations]
    for key in ('operations', 'allowed_operations'):
        raw = draft.get(key)
        if isinstance(raw, Mapping):
            values.extend((str(value) for value in raw))
        elif isinstance(raw, list):
            values.extend((str(value) for value in raw))
    output_profile = draft.get('output_profile')
    if isinstance(output_profile, Mapping):
        raw = output_profile.get('allowed_operations')
        if isinstance(raw, Mapping):
            values.extend((str(value) for value in raw))
        elif isinstance(raw, list):
            values.extend((str(value) for value in raw))

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            if isinstance(value.get('op'), str):
                values.append(str(value['op']))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(draft.get('recipes'))
    return _v6m_bounded(values, 'operations')

def _v6m_draft_inventory(draft: Mapping[str, Any], supported_operations: Iterable[str]) -> dict[str, Any]:
    if not isinstance(draft, Mapping):
        raise AuthoringSourceManifestError('authoring_draft_not_object')
    datasets_value = draft.get('datasets')
    datasets = datasets_value if isinstance(datasets_value, Mapping) else {}
    dataset_ids = _v6m_bounded((str(value) for value in datasets), 'datasets')
    dataset_fields: dict[str, list[str]] = {}
    field_roles: dict[str, dict[str, list[str]]] = {}
    for dataset_id in dataset_ids:
        dataset = datasets.get(dataset_id)
        fields = dataset.get('fields') if isinstance(dataset, Mapping) else {}
        dataset_fields[dataset_id] = _v6m_bounded((str(value) for value in fields) if isinstance(fields, Mapping) else (), 'fields')
        if isinstance(fields, Mapping):
            for field_id, raw_field in fields.items():
                roles = raw_field.get('roles') if isinstance(raw_field, Mapping) else None
                if isinstance(roles, list) and all((isinstance(value, str) for value in roles)):
                    canonical = [role for role in _v6m_FIELD_ROLE_ORDER if role in roles]
                    canonical.extend(sorted(set(roles) - _v6m_FIELD_ROLE_SET))
                    field_roles.setdefault(dataset_id, {})[str(field_id)] = canonical
    root_fields = draft.get('fields')
    unique_fields = {field for values in dataset_fields.values() for field in values}
    if isinstance(root_fields, Mapping):
        unique_fields.update((str(value) for value in root_fields))

    def keys(name: str, kind: str) -> list[str]:
        value = draft.get(name)
        return _v6m_bounded((str(item) for item in value) if isinstance(value, Mapping) else (), kind)
    grain_keys: dict[str, list[str]] = {}
    grain_display_fields: dict[str, list[str]] = {}
    raw_grains = draft.get('grains')
    if isinstance(raw_grains, Mapping):
        for grain_id, raw_grain in raw_grains.items():
            if not isinstance(grain_id, str) or not isinstance(raw_grain, Mapping):
                continue
            raw_keys = raw_grain.get('keys')
            if isinstance(raw_keys, list) and raw_keys and all((isinstance(value, str) for value in raw_keys)):
                grain_keys[grain_id] = list(raw_keys)
            raw_display = raw_grain.get('display_fields')
            if raw_display is None:
                grain_display_fields[grain_id] = []
            elif isinstance(raw_display, list) and all((isinstance(value, str) for value in raw_display)):
                grain_display_fields[grain_id] = list(raw_display)
    relation_endpoints: dict[str, dict[str, str]] = {}
    relation_keys: dict[str, dict[str, list[str]]] = {}
    relation_policies: dict[str, dict[str, str]] = {}
    raw_relations = draft.get('relations')
    if isinstance(raw_relations, Mapping):
        for relation_id, raw_relation in raw_relations.items():
            if not isinstance(relation_id, str) or not isinstance(raw_relation, Mapping):
                continue
            left_dataset = raw_relation.get('left_dataset')
            right_dataset = raw_relation.get('right_dataset')
            if isinstance(left_dataset, str) and left_dataset and isinstance(right_dataset, str) and right_dataset:
                relation_endpoints[relation_id] = {'left_dataset': left_dataset, 'right_dataset': right_dataset}
            left_keys = raw_relation.get('left_keys')
            right_keys = raw_relation.get('right_keys')
            if isinstance(left_keys, list) and isinstance(right_keys, list) and left_keys and (len(left_keys) == len(right_keys)) and all((isinstance(value, str) for value in [*left_keys, *right_keys])):
                relation_keys[relation_id] = {'left_keys': list(left_keys), 'right_keys': list(right_keys)}
            policy = {key: raw_relation.get(key) for key in _v6m_RELATION_POLICY_VALUES}
            if all((isinstance(value, str) and value for value in policy.values())):
                relation_policies[relation_id] = policy
    alias_pairs: set[tuple[str, str]] = set()

    def add_alias_card(target: str, card: Any) -> None:
        if not isinstance(card, Mapping) or not re.fullmatch(_v6m_IDENTIFIER, str(target or '')):
            return
        raw_aliases = card.get('aliases')
        if not isinstance(raw_aliases, list):
            raw_aliases = card.get('values')
        if not isinstance(raw_aliases, list):
            return
        for raw_alias in raw_aliases:
            alias_text = raw_alias if isinstance(raw_alias, str) else None
            if alias_text is None and isinstance(raw_alias, Mapping) and isinstance(raw_alias.get('text'), str):
                alias_text = raw_alias['text']
            if alias_text is not None:
                alias_pairs.add((_v6m_normalized_alias(alias_text), str(target)))
    for dataset_id in dataset_ids:
        dataset = datasets.get(dataset_id)
        add_alias_card(dataset_id, dataset)
        fields = dataset.get('fields') if isinstance(dataset, Mapping) else {}
        if isinstance(fields, Mapping):
            for field_id, card in fields.items():
                add_alias_card(str(field_id), card)
    for section in ('fields', 'metrics', 'entity_groups', 'grains', 'relations', 'recipes'):
        cards = draft.get(section)
        if isinstance(cards, Mapping):
            for target, card in cards.items():
                add_alias_card(str(target), card)
    explicit_aliases = draft.get('aliases')
    if isinstance(explicit_aliases, Mapping):
        for card in explicit_aliases.values():
            if isinstance(card, Mapping):
                add_alias_card(str(card.get('target_key') or ''), card)
    if len(alias_pairs) > _v6mMAX_INVENTORY['aliases']:
        raise AuthoringSourceManifestError('authoring_inventory_limit_exceeded', {'inventory': 'aliases', 'count': len(alias_pairs), 'limit': _v6mMAX_INVENTORY['aliases']})
    alias_bindings = [{'alias': alias, 'target': target} for alias, target in sorted(alias_pairs)]
    return {'datasets': dataset_ids, 'dataset_fields': dataset_fields, 'field_roles': {dataset_id: {field_id: field_roles[dataset_id][field_id] for field_id in sorted(field_roles[dataset_id])} for dataset_id in sorted(field_roles)}, 'fields': _v6m_bounded(unique_fields, 'fields'), 'metrics': keys('metrics', 'metrics'), 'grains': keys('grains', 'grains'), 'grain_keys': {key: grain_keys[key] for key in sorted(grain_keys)}, 'grain_display_fields': {key: grain_display_fields[key] for key in sorted(grain_display_fields)}, 'relations': keys('relations', 'relations'), 'relation_endpoints': {key: relation_endpoints[key] for key in sorted(relation_endpoints)}, 'relation_keys': {key: relation_keys[key] for key in sorted(relation_keys)}, 'relation_policies': {key: relation_policies[key] for key in sorted(relation_policies)}, 'recipes': keys('recipes', 'recipes'), 'operations': _v6m_draft_operations(draft, supported_operations), 'aliases': sorted({item['alias'] for item in alias_bindings}), 'alias_targets': sorted({item['target'] for item in alias_bindings}), 'alias_bindings': alias_bindings}

def _v6m_bounded_missing(values: Iterable[str]) -> tuple[list[str], int]:
    ordered = sorted(set((str(value) for value in values)))
    return (ordered[:_v6mMAX_MISSING_EVIDENCE], max(0, len(ordered) - _v6mMAX_MISSING_EVIDENCE))

def validate_draft_inventory_coverage(manifest: Mapping[str, Any], draft: Mapping[str, Any], *, supported_operations: Iterable[str]=()) -> dict[str, Any]:
    """Validate that a draft covers every explicitly declared source ID.

    On success the function returns only hashes, integer counts and empty
    bounded ``missing`` evidence.  On failure it raises
    :class:`AuthoringSourceManifestError`; the same safe evidence is available
    on ``exc.evidence``.
    """
    sealed_manifest = _v6m_validated_manifest(manifest)
    expected = sealed_manifest['inventories']
    actual = _v6m_draft_inventory(draft, supported_operations)
    missing_fields = []
    for dataset_id, fields in expected['dataset_fields'].items():
        actual_fields = set(actual['dataset_fields'].get(dataset_id, []))
        missing_fields.extend((f'{dataset_id}:{field_id}' for field_id in fields if field_id not in actual_fields))
    actual_alias_pairs = {(item['alias'], item['target']) for item in actual['alias_bindings']}
    expected_relation_endpoints = {f"{relation_id}={card['left_dataset']}->{card['right_dataset']}" for relation_id, card in expected['relation_endpoints'].items()}
    actual_relation_endpoints = {f"{relation_id}={card['left_dataset']}->{card['right_dataset']}" for relation_id, card in actual['relation_endpoints'].items()}
    expected_relation_keys = {f"{relation_id}={'|'.join(card['left_keys'])}->{'|'.join(card['right_keys'])}" for relation_id, card in expected['relation_keys'].items()}
    actual_relation_keys = {f"{relation_id}={'|'.join(card['left_keys'])}->{'|'.join(card['right_keys'])}" for relation_id, card in actual['relation_keys'].items()}
    expected_field_roles = {f"{dataset_id}.{field_id}={'|'.join(roles)}" for dataset_id, fields in expected['field_roles'].items() for field_id, roles in fields.items()}
    actual_field_roles = {f"{dataset_id}.{field_id}={'|'.join(roles)}" for dataset_id, fields in actual['field_roles'].items() for field_id, roles in fields.items()}
    policy_keys = ('join_type', 'cardinality', 'null_key_policy', 'multi_match_policy')
    expected_relation_policies = {f'{relation_id}=' + '|'.join((f'{key}:{card[key]}' for key in policy_keys)) for relation_id, card in expected['relation_policies'].items()}
    actual_relation_policies = {f'{relation_id}=' + '|'.join((f'{key}:{card[key]}' for key in policy_keys)) for relation_id, card in actual['relation_policies'].items()}
    expected_grain_keys = {f"{grain_id}={'|'.join(values)}" for grain_id, values in expected['grain_keys'].items()}
    actual_grain_keys = {f"{grain_id}={'|'.join(values)}" for grain_id, values in actual['grain_keys'].items()}
    expected_grain_display = {f"{grain_id}={'|'.join(values)}" for grain_id, values in expected['grain_display_fields'].items()}
    actual_grain_display = {f"{grain_id}={'|'.join(values)}" for grain_id, values in actual['grain_display_fields'].items()}
    raw_missing = {'datasets': set(expected['datasets']) - set(actual['datasets']), 'fields': missing_fields, 'field_roles': expected_field_roles - actual_field_roles, 'metrics': set(expected['metrics']) - set(actual['metrics']), 'grains': set(expected['grains']) - set(actual['grains']), 'grain_keys': expected_grain_keys - actual_grain_keys, 'grain_display_fields': expected_grain_display - actual_grain_display, 'relations': set(expected['relations']) - set(actual['relations']), 'relation_endpoints': expected_relation_endpoints - actual_relation_endpoints, 'relation_keys': expected_relation_keys - actual_relation_keys, 'relation_policies': expected_relation_policies - actual_relation_policies, 'recipes': set(expected['recipes']) - set(actual['recipes']), 'operations': set(expected['operations']) - set(actual['operations']), 'aliases': {hashlib.sha256(item['alias'].encode('utf-8')).hexdigest() + ':' + item['target'] for item in expected['alias_bindings'] if (item['alias'], item['target']) not in actual_alias_pairs}, 'required_sections': []}
    for section in sealed_manifest['required_sections']:
        section_values = actual.get(section)
        if not isinstance(section_values, (list, dict)) or not section_values:
            raw_missing['required_sections'].append(section)
    missing: dict[str, list[str]] = {}
    truncated: dict[str, int] = {}
    missing_counts: dict[str, int] = {}
    for kind, values in raw_missing.items():
        bounded_values, omitted = _v6m_bounded_missing(values)
        missing[kind] = bounded_values
        truncated[kind] = omitted
        missing_counts[kind] = len(set(values))
    expected_counts = deepcopy(sealed_manifest['counts'])
    actual_counts = {'datasets': len(actual['datasets']), 'fields': len(actual['fields']), 'field_bindings': sum((len(values) for values in actual['dataset_fields'].values())), 'field_roles': sum((len(values) for values in actual['field_roles'].values())), 'metrics': len(actual['metrics']), 'grains': len(actual['grains']), 'grain_keys': len(actual['grain_keys']), 'grain_display_fields': len(actual['grain_display_fields']), 'relations': len(actual['relations']), 'relation_endpoints': len(actual['relation_endpoints']), 'relation_keys': len(actual['relation_keys']), 'relation_policies': len(actual['relation_policies']), 'recipes': len(actual['recipes']), 'operations': len(actual['operations']), 'aliases': len(actual['aliases']), 'alias_targets': len(actual['alias_targets']), 'alias_bindings': len(actual['alias_bindings'])}
    evidence = {'contract_version': _v6mCOVERAGE_VERSION, 'passed': not any(missing_counts.values()), 'source_sha256': sealed_manifest['source_sha256'], 'manifest_sha256': sealed_manifest['manifest_sha256'], 'draft_inventory_sha256': _v6m_canonical_sha256(actual), 'counts': {'required': expected_counts, 'actual': actual_counts, 'missing': missing_counts}, 'missing': missing, 'missing_truncated': truncated}
    if not evidence['passed']:
        raise AuthoringSourceManifestError('authoring_source_coverage_incomplete', evidence)
    return evidence
__all__ = ['AuthoringSourceManifestError', 'COVERAGE_VERSION', 'MANIFEST_VERSION', 'extract_authoring_source_manifest', 'normalize_authoring_draft_shorthand', 'normalize_authoring_section_patch_shorthand', 'normalize_draft_alias_shorthand', 'validate_authoring_source_manifest', 'validate_draft_inventory_coverage']


import re
from collections.abc import Mapping
from copy import deepcopy
from typing import Any
_v6bBLUEPRINT_VERSION = 'metadata.executable-blueprint.v1'
_v6bAUTHORING_DRAFT_VERSION = 'metadata.authoring.draft.v1'
_v6bEXECUTABLE_KEYS = ('contract_version', 'locale', 'timezone', 'datasets', 'metrics', 'entity_groups', 'grains', 'relations', 'orderings', 'predicates', 'recipes', 'aliases', 'prompt_extensions', 'specialized_functions', 'output_profile', 'source_provenance')
_v6bANNOTATION_KEYS = ('display_name', 'description')
_v6bBLUEPRINT_KEYS = ('contract_version', 'domain_id', 'environment', 'executable', 'default_annotations', 'source_manifest_sha256', 'executable_sha256', 'blueprint_sha256')
_v6b_BLUEPRINT_KEY_SET = set(_v6bBLUEPRINT_KEYS)
_v6b_EXECUTABLE_KEY_SET = set(_v6bEXECUTABLE_KEYS)
_v6b_ANNOTATION_KEY_SET = set(_v6bANNOTATION_KEYS)
_v6b_DRAFT_KEY_SET = _v6b_EXECUTABLE_KEY_SET | _v6b_ANNOTATION_KEY_SET
_v6b_SHA256_PATTERN = re.compile('^[0-9a-f]{64}$')
_v6b_DOMAIN_ID_PATTERN = re.compile('^[a-z][a-z0-9_-]{1,63}$')
_v6b_ENVIRONMENT_PATTERN = re.compile('^[a-z][a-z0-9_-]{1,31}$')

def _v6b_fail(reason: str, details: Mapping[str, Any] | None=None) -> None:
    raise ContractError('metadata_dependency_error', 'metadata_blueprint_validation', '신뢰된 metadata blueprint 검증에 실패했습니다.', {'reason': reason, **deepcopy(dict(details or {}))})

def _v6b_identity(value: Any, *, label: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        _v6b_fail('identity_invalid', {'field': label})
    return value

def _v6b_sha256(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not _v6b_SHA256_PATTERN.fullmatch(value):
        _v6b_fail('sha256_invalid', {'field': label})
    return value

def _v6b_validated_manifest_sha256(source_manifest: Mapping[str, Any]) -> str:
    try:
        manifest = validate_authoring_source_manifest(source_manifest)
    except (AuthoringSourceManifestError, TypeError, ValueError) as exc:
        _v6b_fail('source_manifest_invalid')
        raise AssertionError('unreachable') from exc
    return _v6b_sha256(manifest.get('manifest_sha256'), label='source_manifest_sha256')

def _v6b_validate_source_coverage(source_manifest: Mapping[str, Any], draft: Mapping[str, Any]) -> dict[str, Any]:
    try:
        return validate_draft_inventory_coverage(source_manifest, draft, supported_operations=GENERIC_V2_OPERATIONS)
    except AuthoringSourceManifestError as exc:
        _v6b_fail('source_coverage_incomplete', exc.evidence)
        raise AssertionError('unreachable') from exc

def _v6b_executable_projection(draft: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(draft, Mapping):
        _v6b_fail('draft_not_object')
    actual_keys = set(draft)
    if actual_keys != _v6b_DRAFT_KEY_SET:
        _v6b_fail('draft_top_level_keys_mismatch', {'missing': sorted(_v6b_DRAFT_KEY_SET - actual_keys), 'extra': sorted(actual_keys - _v6b_DRAFT_KEY_SET)})
    return {key: deepcopy(draft[key]) for key in _v6bEXECUTABLE_KEYS}

def _v6b_default_annotations(draft: Mapping[str, Any]) -> dict[str, str]:
    display_name = draft.get('display_name')
    description = draft.get('description')
    if not isinstance(display_name, str) or not display_name:
        _v6b_fail('default_annotation_invalid', {'field': 'display_name'})
    annotations = {'display_name': display_name}
    if not isinstance(description, str):
        _v6b_fail('default_annotation_invalid', {'field': 'description'})
    annotations['description'] = description
    return annotations

def _v6bcompute_blueprint_sha256(blueprint: Mapping[str, Any]) -> str:
    """Hash the exact blueprint envelope, excluding only its self-hash."""
    if not isinstance(blueprint, Mapping):
        _v6b_fail('blueprint_not_object')
    material = {key: deepcopy(value) for key, value in blueprint.items() if key != 'blueprint_sha256'}
    return sha256_json(material)

def _v6bbuild_executable_blueprint(draft: Mapping[str, Any], *, domain_id: str, environment: str, source_manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Seal a reviewed full-domain draft into a trusted blueprint.

    This helper belongs to the administrative build path.  Runtime requests
    must load the resulting artifact and validate it against an external hash
    pin; they must not build a blueprint from request or LLM payloads.
    """
    normalized_domain = _v6b_identity(domain_id, label='domain_id', pattern=_v6b_DOMAIN_ID_PATTERN)
    normalized_environment = _v6b_identity(environment, label='environment', pattern=_v6b_ENVIRONMENT_PATTERN)
    source_manifest_sha256 = _v6b_validated_manifest_sha256(source_manifest)
    draft_copy = deepcopy(dict(draft)) if isinstance(draft, Mapping) else draft
    validate_contract(draft_copy, 'metadata-authoring-draft.schema.json', stage='metadata_blueprint_build', error_code='metadata_dependency_error')
    executable = _v6b_executable_projection(draft_copy)
    annotations = _v6b_default_annotations(draft_copy)
    _v6b_validate_source_coverage(source_manifest, draft_copy)
    compile_domain_package(draft_copy, normalized_domain, normalized_environment)
    material: dict[str, Any] = {'contract_version': _v6bBLUEPRINT_VERSION, 'domain_id': normalized_domain, 'environment': normalized_environment, 'executable': executable, 'default_annotations': annotations, 'source_manifest_sha256': source_manifest_sha256, 'executable_sha256': sha256_json(executable)}
    blueprint = {**material, 'blueprint_sha256': sha256_json(material)}
    validate_contract(blueprint, 'executable-blueprint.schema.json', stage='metadata_blueprint_build', error_code='metadata_dependency_error')
    return deepcopy(blueprint)

def validate_executable_blueprint(blueprint: Mapping[str, Any], *, expected_blueprint_sha256: str, expected_domain_id: str, expected_environment: str, source_manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a blueprint against independently supplied trust pins."""
    if not isinstance(blueprint, Mapping):
        _v6b_fail('blueprint_not_object')
    value = deepcopy(dict(blueprint))
    actual_keys = set(value)
    if actual_keys != _v6b_BLUEPRINT_KEY_SET:
        _v6b_fail('blueprint_top_level_keys_mismatch', {'missing': sorted(_v6b_BLUEPRINT_KEY_SET - actual_keys), 'extra': sorted(actual_keys - _v6b_BLUEPRINT_KEY_SET)})
    validate_contract(value, 'executable-blueprint.schema.json', stage='metadata_blueprint_validation', error_code='metadata_dependency_error')
    pinned_blueprint_sha256 = _v6b_sha256(expected_blueprint_sha256, label='expected_blueprint_sha256')
    pinned_domain = _v6b_identity(expected_domain_id, label='expected_domain_id', pattern=_v6b_DOMAIN_ID_PATTERN)
    pinned_environment = _v6b_identity(expected_environment, label='expected_environment', pattern=_v6b_ENVIRONMENT_PATTERN)
    pinned_source_manifest_sha256 = _v6b_validated_manifest_sha256(source_manifest)
    if value['contract_version'] != _v6bBLUEPRINT_VERSION:
        _v6b_fail('blueprint_version_mismatch')
    if value['domain_id'] != pinned_domain:
        _v6b_fail('domain_pin_mismatch')
    if value['environment'] != pinned_environment:
        _v6b_fail('environment_pin_mismatch')
    if value['source_manifest_sha256'] != pinned_source_manifest_sha256:
        _v6b_fail('source_manifest_pin_mismatch')
    executable = value['executable']
    if not isinstance(executable, Mapping) or set(executable) != _v6b_EXECUTABLE_KEY_SET:
        _v6b_fail('executable_keys_mismatch')
    expected_executable_sha256 = sha256_json(executable)
    if value['executable_sha256'] != expected_executable_sha256:
        _v6b_fail('executable_hash_mismatch')
    expected_self_hash = _v6bcompute_blueprint_sha256(value)
    if value['blueprint_sha256'] != expected_self_hash:
        _v6b_fail('blueprint_self_hash_mismatch')
    if value['blueprint_sha256'] != pinned_blueprint_sha256:
        _v6b_fail('blueprint_external_pin_mismatch')
    defaults = value['default_annotations']
    if not isinstance(defaults, Mapping) or set(defaults) != _v6b_ANNOTATION_KEY_SET:
        _v6b_fail('default_annotations_keys_mismatch')
    default_draft = {**deepcopy(dict(executable)), **deepcopy(dict(defaults))}
    if canonical_bytes(_v6b_executable_projection(default_draft)) != canonical_bytes(executable):
        _v6b_fail('executable_projection_changed')
    validate_contract(default_draft, 'metadata-authoring-draft.schema.json', stage='metadata_blueprint_validation', error_code='metadata_dependency_error')
    _v6b_validate_source_coverage(source_manifest, default_draft)
    compile_domain_package(default_draft, pinned_domain, pinned_environment)
    return value

def _v6bmerge_blueprint_annotations(blueprint: Mapping[str, Any], annotations: Mapping[str, Any] | None, *, expected_blueprint_sha256: str, expected_domain_id: str, expected_environment: str, source_manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Overlay allowlisted annotations and return a compiled-valid full draft.

    ``display_name`` and ``description`` are the only accepted LLM-produced
    fields.  Missing values retain the reviewed defaults.  All executable
    sections are copied from the validated blueprint and checked byte-for-byte
    (canonical UTF-8 JSON) before and after the merge and semantic compile.
    """
    sealed = validate_executable_blueprint(blueprint, expected_blueprint_sha256=expected_blueprint_sha256, expected_domain_id=expected_domain_id, expected_environment=expected_environment, source_manifest=source_manifest)
    if annotations is None:
        proposal: dict[str, Any] = {}
    elif isinstance(annotations, Mapping):
        proposal = deepcopy(dict(annotations))
    else:
        _v6b_fail('annotations_not_object')
    extra = set(proposal) - _v6b_ANNOTATION_KEY_SET
    if extra:
        _v6b_fail('annotation_key_not_allowed', {'extra': sorted(extra)})
    if 'display_name' in proposal:
        display_name = proposal['display_name']
        if not isinstance(display_name, str) or not display_name or len(display_name) > 200:
            _v6b_fail('annotation_value_invalid', {'field': 'display_name'})
    if 'description' in proposal:
        description = proposal['description']
        if not isinstance(description, str) or len(description) > 4000:
            _v6b_fail('annotation_value_invalid', {'field': 'description'})
    executable = deepcopy(sealed['executable'])
    before_bytes = canonical_bytes(executable)
    merged_annotations = deepcopy(sealed['default_annotations'])
    merged_annotations.update(proposal)
    draft = {**executable, **merged_annotations}
    validate_contract(draft, 'metadata-authoring-draft.schema.json', stage='metadata_blueprint_merge', error_code='metadata_dependency_error')
    compile_domain_package(draft, expected_domain_id, expected_environment)
    after_projection = _v6b_executable_projection(draft)
    after_bytes = canonical_bytes(after_projection)
    if after_bytes != before_bytes:
        _v6b_fail('executable_bytes_changed')
    if sha256_json(after_projection) != sealed['executable_sha256']:
        _v6b_fail('executable_hash_changed')
    return deepcopy(draft)
_v6bapply_domain_blueprint_annotations = _v6bmerge_blueprint_annotations
__all__ = ['ANNOTATION_KEYS', 'AUTHORING_DRAFT_VERSION', 'BLUEPRINT_KEYS', 'BLUEPRINT_VERSION', 'EXECUTABLE_KEYS', 'apply_domain_blueprint_annotations', 'build_executable_blueprint', 'compute_blueprint_sha256', 'merge_blueprint_annotations', 'validate_executable_blueprint']


EMBEDDED_RUNTIME_CATALOG = json.loads('{"aliases":{"dataset:eqp_uph":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"eqp_uph","target_type":"dataset","values":[{"priority":100,"text":"UPH"},{"priority":100,"text":"시간당 생산량"}]},"dataset:equipment_assign":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"equipment_assign","target_type":"dataset","values":[{"priority":100,"text":"장비 배정"},{"priority":100,"text":"장비 현황"},{"priority":100,"text":"설비 대수"}]},"dataset:hold_history":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"hold_history","target_type":"dataset","values":[{"priority":100,"text":"HOLD 이력"},{"priority":100,"text":"HOLD 발생 시각"}]},"dataset:lot_status":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"lot_status","target_type":"dataset","values":[{"priority":100,"text":"현재 LOT"},{"priority":100,"text":"LOT 현황"},{"priority":100,"text":"HOLD LOT"}]},"dataset:product_master":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"product_master","target_type":"dataset","values":[{"priority":100,"text":"product master"},{"priority":100,"text":"제품 master"},{"priority":100,"text":"제품 기준정보"},{"priority":100,"text":"제품 마스터"}]},"dataset:production":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"production","target_type":"dataset","values":[{"priority":100,"text":"production"},{"priority":100,"text":"production 데이터"},{"priority":100,"text":"이력 생산"},{"priority":100,"text":"생산 실적"},{"priority":100,"text":"OUTPUT"},{"priority":100,"text":"OUT"}]},"dataset:production_today":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"production_today","target_type":"dataset","values":[{"priority":100,"text":"당일 생산"},{"priority":100,"text":"오늘 생산"},{"priority":100,"text":"현재 생산"}]},"dataset:target":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"target","target_type":"dataset","values":[{"priority":100,"text":"계획"},{"priority":100,"text":"스케줄"},{"priority":100,"text":"스케쥴"},{"priority":100,"text":"SCHD"},{"priority":100,"text":"생산목표"}]},"dataset:wip":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"wip","target_type":"dataset","values":[{"priority":100,"text":"이력 재공"},{"priority":100,"text":"아침 재공"},{"priority":100,"text":"BOH 재공"},{"priority":100,"text":"BOH"}]},"dataset:wip_today":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"table_catalog","target_key":"wip_today","target_type":"dataset","values":[{"priority":100,"text":"현재 재공"},{"priority":100,"text":"지금 재공"},{"priority":100,"text":"금일 현재 재공"}]},"field:BASE_DATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"BASE_DATE","target_type":"field","values":[{"priority":100,"text":"BASE_DATE"}]},"field:BAY_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"BAY_ID","target_type":"field","values":[{"priority":100,"text":"BAY_ID"}]},"field:CUM_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"CUM_TAT","target_type":"field","values":[{"priority":100,"text":"CUM_TAT"}]},"field:DATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DATE","target_type":"field","values":[{"priority":100,"text":"날짜"},{"priority":100,"text":"일자"},{"priority":100,"text":"기준일"},{"priority":100,"text":"작업일"},{"priority":100,"text":"date"},{"priority":100,"text":"work date"}]},"field:DEN":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DEN","target_type":"field","values":[{"priority":100,"text":"DEN"},{"priority":100,"text":"DENSITY"},{"priority":100,"text":"제품 용량"}]},"field:DEVICE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DEVICE","target_type":"field","values":[{"priority":100,"text":"DEVICE"},{"priority":100,"text":"DEVICE CODE"},{"priority":100,"text":"첨자"}]},"field:DEVICE_DESC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DEVICE_DESC","target_type":"field","values":[{"priority":100,"text":"DEVICE_DESC"},{"priority":100,"text":"제품 설명"}]},"field:DIE_ATTACH_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"DIE_ATTACH_QTY","target_type":"field","values":[{"priority":100,"text":"DIE_ATTACH_QTY"}]},"field:EQP_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"EQP_ID","target_type":"field","values":[{"priority":100,"text":"EQP_ID"},{"priority":100,"text":"EQPID"},{"priority":100,"text":"장비 ID"}]},"field:EQP_MODEL":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"EQP_MODEL","target_type":"field","values":[{"priority":100,"text":"EQP_MODEL"},{"priority":100,"text":"equipment model"},{"priority":100,"text":"장비 모델"},{"priority":100,"text":"장비 기종"},{"priority":100,"text":"설비 모델"},{"priority":100,"text":"설비 기종"}]},"field:FAB":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FAB","target_type":"field","values":[{"priority":100,"text":"FAB"}]},"field:FACTORY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FACTORY","target_type":"field","values":[{"priority":100,"text":"FACTORY"}]},"field:FAC_IN_AT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FAC_IN_AT","target_type":"field","values":[{"priority":100,"text":"FAC_IN_AT"}]},"field:FAMILY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"FAMILY","target_type":"field","values":[{"priority":100,"text":"FAMILY"}]},"field:HOLD_CD":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_CD","target_type":"field","values":[{"priority":100,"text":"HOLD_CD"}]},"field:HOLD_DESC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_DESC","target_type":"field","values":[{"priority":100,"text":"HOLD_DESC"}]},"field:HOLD_EVENT_AT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_EVENT_AT","target_type":"field","values":[{"priority":100,"text":"HOLD_EVENT_AT"}]},"field:HOLD_REASON":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_REASON","target_type":"field","values":[{"priority":100,"text":"HOLD_REASON"}]},"field:HOLD_STAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"HOLD_STAT","target_type":"field","values":[{"priority":100,"text":"HOLD_STAT"}]},"field:INPUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"INPUT_PLAN_QTY","target_type":"field","values":[{"priority":100,"text":"INPUT_PLAN_QTY"}]},"field:IN_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"IN_TAT","target_type":"field","values":[{"priority":100,"text":"IN_TAT"}]},"field:LEAD":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LEAD","target_type":"field","values":[{"priority":100,"text":"LEAD"},{"priority":100,"text":"lead count"}]},"field:LOAD_DATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LOAD_DATE","target_type":"field","values":[{"priority":100,"text":"LOAD_DATE"}]},"field:LOT_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LOT_ID","target_type":"field","values":[{"priority":100,"text":"LOT_ID"},{"priority":100,"text":"Lot ID"}]},"field:LOT_STAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"LOT_STAT","target_type":"field","values":[{"priority":100,"text":"LOT_STAT"}]},"field:MCP_NO":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"MCP_NO","target_type":"field","values":[{"priority":100,"text":"MCP_NO"},{"priority":100,"text":"MCP NO"},{"priority":100,"text":"MCP_SALES_NO"},{"priority":100,"text":"MCP_SALE_CD"},{"priority":100,"text":"MCPSALENO"}]},"field:MODE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"MODE","target_type":"field","values":[{"priority":100,"text":"MODE"},{"priority":100,"text":"Mode"},{"priority":100,"text":"mode"},{"priority":100,"text":"제품 모드"}]},"field:NETDIE_300_CNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"NETDIE_300_CNT","target_type":"field","values":[{"priority":100,"text":"NETDIE_300_CNT"}]},"field:OPER_IN_AT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OPER_IN_AT","target_type":"field","values":[{"priority":100,"text":"OPER_IN_AT"}]},"field:OPER_NAME":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"OPER_NAME","target_type":"field","values":[{"priority":100,"text":"OPER_NAME"},{"priority":100,"text":"공정"},{"priority":100,"text":"작업공정"},{"priority":100,"text":"operation"},{"priority":100,"text":"process"},{"priority":100,"text":"oper name"},{"priority":100,"text":"세부 공정별"},{"priority":100,"text":"공정별"}]},"field:OPER_NUM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OPER_NUM","target_type":"field","values":[{"priority":100,"text":"공정번호"},{"priority":100,"text":"공정 차수"},{"priority":100,"text":"차수별"},{"priority":100,"text":"oper num"},{"priority":100,"text":"oper no"}]},"field:OPER_SEQ":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OPER_SEQ","target_type":"field","values":[{"priority":100,"text":"OPER_SEQ"}]},"field:ORG":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"ORG","target_type":"field","values":[{"priority":100,"text":"ORG"},{"priority":100,"text":"조직"},{"priority":100,"text":"organization code"}]},"field:OUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"OUT_PLAN_QTY","target_type":"field","values":[{"priority":100,"text":"OUT_PLAN_QTY"}]},"field:PKG_TYPE1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PKG_TYPE1","target_type":"field","values":[{"priority":100,"text":"PKG_TYPE1"},{"priority":100,"text":"PKG1"},{"priority":100,"text":"package type 1"}]},"field:PKG_TYPE2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PKG_TYPE2","target_type":"field","values":[{"priority":100,"text":"PKG_TYPE2"},{"priority":100,"text":"PKG2"},{"priority":100,"text":"package type 2"}]},"field:PRESS_CNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PRESS_CNT","target_type":"field","values":[{"priority":100,"text":"PRESS_CNT"}]},"field:PRODUCTION_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PRODUCTION_QTY","target_type":"field","values":[{"priority":100,"text":"PRODUCTION_QTY"}]},"field:PROD_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"PROD_QTY","target_type":"field","values":[{"priority":100,"text":"PROD_QTY"}]},"field:RECIPE_ID":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"RECIPE_ID","target_type":"field","values":[{"priority":100,"text":"RECIPE_ID"},{"priority":100,"text":"Recipe ID"},{"priority":100,"text":"레시피"}]},"field:SHIFT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT","target_type":"field","values":[{"priority":100,"text":"SHIFT"}]},"field:TECH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"TECH","target_type":"field","values":[{"priority":100,"text":"TECH"},{"priority":100,"text":"제품 기술"}]},"field:TSV_DIE_TYP":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"TSV_DIE_TYP","target_type":"field","values":[{"priority":100,"text":"TSV_DIE_TYP"},{"priority":100,"text":"HBM"},{"priority":100,"text":"3DS"},{"priority":100,"text":"TSV"}]},"field:UPH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"UPH","target_type":"field","values":[{"priority":100,"text":"UPH"}]},"field:WF_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"WF_QTY","target_type":"field","values":[{"priority":100,"text":"WF_QTY"}]},"field:WIP_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"WIP_QTY","target_type":"field","values":[{"priority":100,"text":"WIP_QTY"}]},"field:YIELD_RATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"YIELD_RATE","target_type":"field","values":[{"priority":100,"text":"YIELD_RATE"},{"priority":100,"text":"YIELD RATE"},{"priority":100,"text":"수율"}]},"metric:ACHIEVEMENT_RATE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"ACHIEVEMENT_RATE","target_type":"metric","values":[{"priority":100,"text":"생산달성률"},{"priority":100,"text":"생산달성율"},{"priority":100,"text":"달성률"},{"priority":100,"text":"달성율"}]},"metric:CUM_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"CUM_TAT","target_type":"metric","values":[{"priority":100,"text":"CUM TAT"},{"priority":100,"text":"누적 TAT"}]},"metric:EQP_COUNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"EQP_COUNT","target_type":"metric","values":[{"priority":100,"text":"장비 대수"},{"priority":100,"text":"설비 대수"},{"priority":100,"text":"장비 수"},{"priority":100,"text":"몇 대"}]},"metric:HOLD_DURATION_HOURS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"HOLD_DURATION_HOURS","target_type":"metric","values":[{"priority":100,"text":"HOLD_DURATION_HOURS"}]},"metric:INPUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"INPUT_PLAN_QTY","target_type":"metric","values":[{"priority":100,"text":"INPUT 계획"},{"priority":100,"text":"투입계획"}]},"metric:INPUT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"INPUT_QTY","target_type":"metric","values":[{"priority":100,"text":"투입량"},{"priority":100,"text":"INPUT"},{"priority":100,"text":"input"},{"priority":100,"text":"INPUT 수량"},{"priority":100,"text":"INPUT실적"},{"priority":100,"text":"INPUT 실적"},{"priority":100,"text":"INPUT생산량"},{"priority":100,"text":"투입 실적"},{"priority":100,"text":"INPUT_QTY"}]},"metric:IN_TAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"IN_TAT","target_type":"metric","values":[{"priority":100,"text":"IN TAT"},{"priority":100,"text":"현재 공정 TAT"},{"priority":100,"text":"현재 TAT"}]},"metric:LOT_COUNT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"LOT_COUNT","target_type":"metric","values":[{"priority":100,"text":"LOT 건수"},{"priority":100,"text":"LOT 수"}]},"metric:OUT_PLAN_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"OUT_PLAN_QTY","target_type":"metric","values":[{"priority":100,"text":"OUT 계획"},{"priority":100,"text":"TARGET"},{"priority":100,"text":"생산목표"}]},"metric:OUT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"OUT_QTY","target_type":"metric","values":[{"priority":100,"text":"OUT_QTY"}]},"metric:PKG_OUT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PKG_OUT_QTY","target_type":"metric","values":[{"priority":100,"text":"OUTPUT"},{"priority":100,"text":"OUT"},{"priority":100,"text":"Out Put"},{"priority":100,"text":"output 실적"},{"priority":100,"text":"out 실적"},{"priority":100,"text":"PKG OUT실적"},{"priority":100,"text":"PKG OUT 실적"}]},"metric:PRODUCTION_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PRODUCTION_QTY","target_type":"metric","values":[{"priority":100,"text":"생산량"},{"priority":100,"text":"생산실적"},{"priority":100,"text":"실적"},{"priority":100,"text":"PRODUCTION_QTY"}]},"metric:UNIT_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"UNIT_QTY","target_type":"metric","values":[{"priority":100,"text":"UNIT 수량"},{"priority":100,"text":"DIE 수량"}]},"metric:UPH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"UPH","target_type":"metric","values":[{"priority":100,"text":"UPH"},{"priority":100,"text":"시간당 생산량"}]},"metric:WAFER_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WAFER_QTY","target_type":"metric","values":[{"priority":100,"text":"Wafer 수량"},{"priority":100,"text":"웨이퍼 수량"}]},"metric:WIP_BOH_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WIP_BOH_QTY","target_type":"metric","values":[{"priority":100,"text":"아침 재공"},{"priority":100,"text":"BOH 재공"},{"priority":100,"text":"BOH"},{"priority":100,"text":"07시 기준 재공"}]},"metric:WIP_QTY":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WIP_QTY","target_type":"metric","values":[{"priority":100,"text":"재공"},{"priority":100,"text":"재공수량"},{"priority":100,"text":"WIP"},{"priority":100,"text":"공정 물량"}]},"process:B/G1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"B/G1","target_type":"process","values":[{"priority":140,"text":"B/G1"},{"priority":140,"text":"BG1"},{"priority":140,"text":"B/G1공정"},{"priority":140,"text":"B/G1 공정"},{"priority":140,"text":"B/G 1차"},{"priority":140,"text":"B/G1차"},{"priority":140,"text":"BG 1차"},{"priority":140,"text":"BG1차"}]},"process:B/G2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"B/G2","target_type":"process","values":[{"priority":140,"text":"B/G2"},{"priority":140,"text":"BG2"},{"priority":140,"text":"B/G2공정"},{"priority":140,"text":"B/G2 공정"},{"priority":140,"text":"B/G 2차"},{"priority":140,"text":"B/G2차"},{"priority":140,"text":"BG 2차"},{"priority":140,"text":"BG2차"}]},"process:D/A1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A1","target_type":"process","values":[{"priority":140,"text":"D/A1"},{"priority":140,"text":"DA1"},{"priority":140,"text":"D/A1공정"},{"priority":140,"text":"D/A1 공정"},{"priority":140,"text":"D/A 1차"},{"priority":140,"text":"D/A1차"},{"priority":140,"text":"DA 1차"},{"priority":140,"text":"DA1차"}]},"process:D/A2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A2","target_type":"process","values":[{"priority":140,"text":"D/A2"},{"priority":140,"text":"DA2"},{"priority":140,"text":"D/A2공정"},{"priority":140,"text":"D/A2 공정"},{"priority":140,"text":"D/A 2차"},{"priority":140,"text":"D/A2차"},{"priority":140,"text":"DA 2차"},{"priority":140,"text":"DA2차"}]},"process:D/A3":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A3","target_type":"process","values":[{"priority":140,"text":"D/A3"},{"priority":140,"text":"DA3"},{"priority":140,"text":"D/A3공정"},{"priority":140,"text":"D/A3 공정"},{"priority":140,"text":"D/A 3차"},{"priority":140,"text":"D/A3차"},{"priority":140,"text":"DA 3차"},{"priority":140,"text":"DA3차"}]},"process:D/A4":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A4","target_type":"process","values":[{"priority":140,"text":"D/A4"},{"priority":140,"text":"DA4"},{"priority":140,"text":"D/A4공정"},{"priority":140,"text":"D/A4 공정"},{"priority":140,"text":"D/A 4차"},{"priority":140,"text":"D/A4차"},{"priority":140,"text":"DA 4차"},{"priority":140,"text":"DA4차"}]},"process:D/A5":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A5","target_type":"process","values":[{"priority":140,"text":"D/A5"},{"priority":140,"text":"DA5"},{"priority":140,"text":"D/A5공정"},{"priority":140,"text":"D/A5 공정"},{"priority":140,"text":"D/A 5차"},{"priority":140,"text":"D/A5차"},{"priority":140,"text":"DA 5차"},{"priority":140,"text":"DA5차"}]},"process:D/A6":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/A6","target_type":"process","values":[{"priority":140,"text":"D/A6"},{"priority":140,"text":"DA6"},{"priority":140,"text":"D/A6공정"},{"priority":140,"text":"D/A6 공정"},{"priority":140,"text":"D/A 6차"},{"priority":140,"text":"D/A6차"},{"priority":140,"text":"DA 6차"},{"priority":140,"text":"DA6차"}]},"process:D/S1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"D/S1","target_type":"process","values":[{"priority":140,"text":"D/S1"},{"priority":140,"text":"DS1"},{"priority":140,"text":"D/S1공정"},{"priority":140,"text":"D/S1 공정"},{"priority":140,"text":"D/S 1차"},{"priority":140,"text":"D/S1차"},{"priority":140,"text":"DS 1차"},{"priority":140,"text":"DS1차"}]},"process:FCB/H":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB/H","target_type":"process","values":[{"priority":140,"text":"FCB/H"},{"priority":140,"text":"FCBH"},{"priority":140,"text":"FCB/H공정"},{"priority":140,"text":"FCB/H 공정"}]},"process:FCB1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB1","target_type":"process","values":[{"priority":140,"text":"FCB1"},{"priority":140,"text":"FCB1공정"},{"priority":140,"text":"FCB1 공정"},{"priority":140,"text":"FCB 1차"},{"priority":140,"text":"FCB1차"}]},"process:FCB2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB2","target_type":"process","values":[{"priority":140,"text":"FCB2"},{"priority":140,"text":"FCB2공정"},{"priority":140,"text":"FCB2 공정"},{"priority":140,"text":"FCB 2차"},{"priority":140,"text":"FCB2차"}]},"process:INPUT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"INPUT","target_type":"process","values":[{"priority":140,"text":"INPUT"},{"priority":140,"text":"INPUT공정"},{"priority":140,"text":"INPUT 공정"}]},"process:PKG OUT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PKG OUT","target_type":"process","values":[{"priority":140,"text":"PKG OUT"},{"priority":140,"text":"PKG OUT공정"},{"priority":140,"text":"PKG OUT 공정"}]},"process:SBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SBM","target_type":"process","values":[{"priority":140,"text":"SBM"},{"priority":140,"text":"SBM공정"},{"priority":140,"text":"SBM 공정"}]},"process:W/B1":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B1","target_type":"process","values":[{"priority":140,"text":"W/B1"},{"priority":140,"text":"WB1"},{"priority":140,"text":"W/B1공정"},{"priority":140,"text":"W/B1 공정"},{"priority":140,"text":"W/B 1차"},{"priority":140,"text":"W/B1차"},{"priority":140,"text":"WB 1차"},{"priority":140,"text":"WB1차"}]},"process:W/B2":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B2","target_type":"process","values":[{"priority":140,"text":"W/B2"},{"priority":140,"text":"WB2"},{"priority":140,"text":"W/B2공정"},{"priority":140,"text":"W/B2 공정"},{"priority":140,"text":"W/B 2차"},{"priority":140,"text":"W/B2차"},{"priority":140,"text":"WB 2차"},{"priority":140,"text":"WB2차"}]},"process:W/B3":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B3","target_type":"process","values":[{"priority":140,"text":"W/B3"},{"priority":140,"text":"WB3"},{"priority":140,"text":"W/B3공정"},{"priority":140,"text":"W/B3 공정"},{"priority":140,"text":"W/B 3차"},{"priority":140,"text":"W/B3차"},{"priority":140,"text":"WB 3차"},{"priority":140,"text":"WB3차"}]},"process:W/B4":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B4","target_type":"process","values":[{"priority":140,"text":"W/B4"},{"priority":140,"text":"WB4"},{"priority":140,"text":"W/B4공정"},{"priority":140,"text":"W/B4 공정"},{"priority":140,"text":"W/B 4차"},{"priority":140,"text":"W/B4차"},{"priority":140,"text":"WB 4차"},{"priority":140,"text":"WB4차"}]},"process:W/B5":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B5","target_type":"process","values":[{"priority":140,"text":"W/B5"},{"priority":140,"text":"WB5"},{"priority":140,"text":"W/B5공정"},{"priority":140,"text":"W/B5 공정"},{"priority":140,"text":"W/B 5차"},{"priority":140,"text":"W/B5차"},{"priority":140,"text":"WB 5차"},{"priority":140,"text":"WB5차"}]},"process:W/B6":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/B6","target_type":"process","values":[{"priority":140,"text":"W/B6"},{"priority":140,"text":"WB6"},{"priority":140,"text":"W/B6공정"},{"priority":140,"text":"W/B6 공정"},{"priority":140,"text":"W/B 6차"},{"priority":140,"text":"W/B6차"},{"priority":140,"text":"WB 6차"},{"priority":140,"text":"WB6차"}]},"process:W/BM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"W/BM","target_type":"process","values":[{"priority":140,"text":"W/BM"},{"priority":140,"text":"WBM"},{"priority":140,"text":"W/BM공정"},{"priority":140,"text":"W/BM 공정"}]},"process_group:BG":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"BG","target_type":"process_group","values":[{"priority":100,"text":"BG"},{"priority":100,"text":"BG공정"},{"priority":100,"text":"BG 공정"},{"priority":100,"text":"B/G"},{"priority":100,"text":"B/G공정"},{"priority":100,"text":"B/G 공정"}]},"process_group:BM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"BM","target_type":"process_group","values":[{"priority":100,"text":"BM"},{"priority":100,"text":"BM공정"},{"priority":100,"text":"BM 공정"},{"priority":100,"text":"B/M"},{"priority":100,"text":"B/M공정"},{"priority":100,"text":"B/M 공정"},{"priority":100,"text":"비엠"},{"priority":100,"text":"비엠공정"},{"priority":100,"text":"비엠 공정"}]},"process_group:DA":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DA","target_type":"process_group","values":[{"priority":100,"text":"DA"},{"priority":100,"text":"DA공정"},{"priority":100,"text":"DA 공정"},{"priority":100,"text":"D/A"},{"priority":100,"text":"D/A공정"},{"priority":100,"text":"D/A 공정"}]},"process_group:DC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DC","target_type":"process_group","values":[{"priority":100,"text":"DC"},{"priority":100,"text":"DC공정"},{"priority":100,"text":"DC 공정"},{"priority":100,"text":"D/C"},{"priority":100,"text":"D/C공정"},{"priority":100,"text":"D/C 공정"}]},"process_group:DI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DI","target_type":"process_group","values":[{"priority":100,"text":"DI"},{"priority":100,"text":"DI공정"},{"priority":100,"text":"DI 공정"},{"priority":100,"text":"D/I"},{"priority":100,"text":"D/I공정"},{"priority":100,"text":"D/I 공정"},{"priority":100,"text":"DVI"},{"priority":100,"text":"DVI공정"},{"priority":100,"text":"DVI 공정"}]},"process_group:DP":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DP","target_type":"process_group","values":[{"priority":100,"text":"DP"},{"priority":100,"text":"DP공정"},{"priority":100,"text":"DP 공정"},{"priority":100,"text":"D/P"},{"priority":100,"text":"D/P공정"},{"priority":100,"text":"D/P 공정"}]},"process_group:DS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"DS","target_type":"process_group","values":[{"priority":100,"text":"DS"},{"priority":100,"text":"DS공정"},{"priority":100,"text":"DS 공정"},{"priority":100,"text":"D/S"},{"priority":100,"text":"D/S공정"},{"priority":100,"text":"D/S 공정"}]},"process_group:FCB":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCB","target_type":"process_group","values":[{"priority":100,"text":"FCB"},{"priority":100,"text":"FCB공정"},{"priority":100,"text":"FCB 공정"}]},"process_group:FCBH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"FCBH","target_type":"process_group","values":[{"priority":100,"text":"FCBH"},{"priority":100,"text":"FCBH공정"},{"priority":100,"text":"FCBH 공정"},{"priority":100,"text":"FCB/H"},{"priority":100,"text":"FCB/H공정"},{"priority":100,"text":"FCB/H 공정"}]},"process_group:HS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"HS","target_type":"process_group","values":[{"priority":100,"text":"HS"},{"priority":100,"text":"HS공정"},{"priority":100,"text":"HS 공정"},{"priority":100,"text":"H/S"},{"priority":100,"text":"H/S공정"},{"priority":100,"text":"H/S 공정"}]},"process_group:LT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"LT","target_type":"process_group","values":[{"priority":100,"text":"LT"},{"priority":100,"text":"LT공정"},{"priority":100,"text":"LT 공정"},{"priority":100,"text":"L/T"},{"priority":100,"text":"L/T공정"},{"priority":100,"text":"L/T 공정"}]},"process_group:PC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PC","target_type":"process_group","values":[{"priority":100,"text":"PC"},{"priority":100,"text":"PC공정"},{"priority":100,"text":"PC 공정"},{"priority":100,"text":"P/C"},{"priority":100,"text":"P/C공정"},{"priority":100,"text":"P/C 공정"}]},"process_group:PCO":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PCO","target_type":"process_group","values":[{"priority":100,"text":"PCO"},{"priority":100,"text":"PCO공정"},{"priority":100,"text":"PCO 공정"}]},"process_group:PLH":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"PLH","target_type":"process_group","values":[{"priority":100,"text":"PLH"},{"priority":100,"text":"PLH공정"},{"priority":100,"text":"PLH 공정"},{"priority":100,"text":"P/L"},{"priority":100,"text":"P/L공정"},{"priority":100,"text":"P/L 공정"}]},"process_group:QCSPC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"QCSPC","target_type":"process_group","values":[{"priority":100,"text":"QCSPC"},{"priority":100,"text":"QCSPC공정"},{"priority":100,"text":"QCSPC 공정"}]},"process_group:SAT":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SAT","target_type":"process_group","values":[{"priority":100,"text":"SAT"},{"priority":100,"text":"SAT공정"},{"priority":100,"text":"SAT 공정"}]},"process_group:SBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SBM","target_type":"process_group","values":[{"priority":100,"text":"SBM"},{"priority":100,"text":"SBM공정"},{"priority":100,"text":"SBM 공정"}]},"process_group:SG":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"SG","target_type":"process_group","values":[{"priority":100,"text":"SG"},{"priority":100,"text":"SG공정"},{"priority":100,"text":"SG 공정"},{"priority":100,"text":"S/G"},{"priority":100,"text":"S/G공정"},{"priority":100,"text":"S/G 공정"}]},"process_group:WB":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WB","target_type":"process_group","values":[{"priority":100,"text":"WB"},{"priority":100,"text":"WB공정"},{"priority":100,"text":"WB 공정"},{"priority":100,"text":"W/B"},{"priority":100,"text":"W/B공정"},{"priority":100,"text":"W/B 공정"}]},"process_group:WBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WBM","target_type":"process_group","values":[{"priority":120,"text":"WBM"},{"priority":120,"text":"WBM공정"},{"priority":120,"text":"WBM 공정"},{"priority":120,"text":"W/BM"},{"priority":120,"text":"W/BM공정"},{"priority":120,"text":"W/BM 공정"}]},"process_group:WEC":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WEC","target_type":"process_group","values":[{"priority":100,"text":"WEC"},{"priority":100,"text":"WEC공정"},{"priority":100,"text":"WEC 공정"}]},"process_group:WET":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WET","target_type":"process_group","values":[{"priority":100,"text":"WET"},{"priority":100,"text":"WET공정"},{"priority":100,"text":"WET 공정"}]},"process_group:WLS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WLS","target_type":"process_group","values":[{"priority":100,"text":"WLS"},{"priority":100,"text":"WLS공정"},{"priority":100,"text":"WLS 공정"}]},"process_group:WS":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WS","target_type":"process_group","values":[{"priority":100,"text":"WS"},{"priority":100,"text":"WS공정"},{"priority":100,"text":"WS 공정"},{"priority":100,"text":"W/S"},{"priority":100,"text":"W/S공정"},{"priority":100,"text":"W/S 공정"}]},"process_group:WSD":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"WSD","target_type":"process_group","values":[{"priority":100,"text":"WSD"},{"priority":100,"text":"WSD공정"},{"priority":100,"text":"WSD 공정"}]},"product_group:AUTO":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"AUTO","target_type":"product_group","values":[{"priority":100,"text":"AUTO향"},{"priority":100,"text":"오토모티브향"},{"priority":100,"text":"오토향"}]},"product_group:HBM":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"HBM","target_type":"product_group","values":[{"priority":100,"text":"HBM"},{"priority":100,"text":"3DS"},{"priority":100,"text":"TSV"}]},"product_group:MOBILE":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"MOBILE","target_type":"product_group","values":[{"priority":100,"text":"Mobile"},{"priority":100,"text":"MOBILE"},{"priority":100,"text":"모바일"}]},"product_group:POP":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"POP","target_type":"product_group","values":[{"priority":100,"text":"POP"},{"priority":100,"text":"pop"},{"priority":100,"text":"Pop"}]},"product_group:STACK_2HI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"STACK_2HI","target_type":"product_group","values":[{"priority":100,"text":"2Hi"}]},"product_group:STACK_4HI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"STACK_4HI","target_type":"product_group","values":[{"priority":100,"text":"4Hi"}]},"product_group:STACK_8HI":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"STACK_8HI","target_type":"product_group","values":[{"priority":100,"text":"8Hi"}]},"recipe:achievement.input_actual":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"achievement.input_actual","target_type":"recipe","values":[{"priority":100,"text":"생산달성률"},{"priority":100,"text":"생산달성율"},{"priority":100,"text":"INPUT 계획 대비 실적"}]},"recipe:equipment.assignment_enrich":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"equipment.assignment_enrich","target_type":"recipe","values":[{"priority":100,"text":"할당된 장비 대수와 LIST"},{"priority":100,"text":"장비 배정"},{"priority":100,"text":"장비 목록"}]},"recipe:equipment.assignment_uph":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"equipment.assignment_uph","target_type":"recipe","values":[{"priority":100,"text":"장비별 UPH"},{"priority":100,"text":"배정 장비 UPH"},{"priority":100,"text":"장비와 Recipe UPH"}]},"recipe:hold.oldest_current_history":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"hold.oldest_current_history","target_type":"recipe","values":[{"priority":100,"text":"HOLD 시간이 가장 오래된 LOT"},{"priority":100,"text":"오래된 HOLD 이력"}]},"recipe:join.operation.production_wip":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"join.operation.production_wip","target_type":"recipe","values":[{"priority":100,"text":"생산량과 재공수량"},{"priority":100,"text":"생산 WIP 비교"}]},"recipe:ordered.process.range":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"ordered.process.range","target_type":"recipe","values":[{"priority":100,"text":"공정 구간"},{"priority":100,"text":"공정 범위"},{"priority":100,"text":"OPER_SEQ 범위"}]},"recipe:presence.left_positive_right_zero":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"presence.left_positive_right_zero","target_type":"recipe","values":[{"priority":100,"text":"A는 있으나 B는 없음"},{"priority":100,"text":"실적 있음 재공 없음"},{"priority":100,"text":"존재 미존재"}]},"recipe:product.standard":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"product.standard","target_type":"recipe","values":[{"priority":100,"text":"제품별"},{"priority":100,"text":"제품 기준"},{"priority":100,"text":"제품 집계"}]},"recipe:rank.bottom_n":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"rank.bottom_n","target_type":"recipe","values":[{"priority":100,"text":"하위 N개"},{"priority":100,"text":"가장 적은"},{"priority":100,"text":"BOTTOM N"}]},"recipe:rank.top_n":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"domain","target_key":"rank.top_n","target_type":"recipe","values":[{"priority":100,"text":"상위 N개"},{"priority":100,"text":"가장 많은"},{"priority":100,"text":"TOP N"}]},"status:SHIFT_A":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT_A","target_type":"status","values":[{"priority":100,"text":"Shift A조"},{"priority":100,"text":"SHIFT A조"},{"priority":100,"text":"Shift A"},{"priority":100,"text":"A조"},{"priority":100,"text":"1조"},{"priority":100,"text":"07:00~15:00"}]},"status:SHIFT_B":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT_B","target_type":"status","values":[{"priority":100,"text":"Shift B조"},{"priority":100,"text":"SHIFT B조"},{"priority":100,"text":"Shift B"},{"priority":100,"text":"B조"},{"priority":100,"text":"2조"},{"priority":100,"text":"15:00~23:00"}]},"status:SHIFT_C":{"conflict":"fail_ambiguous","match":"bounded_longest","normalization":["unicode_nfkc","trim","collapse_space","latin_casefold"],"provenance_source":"main_filters","target_key":"SHIFT_C","target_type":"status","values":[{"priority":100,"text":"Shift C조"},{"priority":100,"text":"SHIFT C조"},{"priority":100,"text":"Shift C"},{"priority":100,"text":"C조"},{"priority":100,"text":"3조"},{"priority":100,"text":"23:00~07:00"}]}},"catalog_sha256":"1f8b6c1522b96425a6a46a3e4dfcf4c5b7c338c6bc0af3c2a0878806ea4a7f8e","contract_version":"metadata.runtime.catalog.v1","datasets":{"eqp_uph":{"config_ref":"config:oracle:GMS_DB@1","default_detail_fields":["EQP_MODEL","RECIPE_ID","OPER_NAME"],"family":"equipment_uph","fields":{"BASE_DATE":{"coercion":"strict_date","nullable":true,"physical_aliases":[],"physical_column":"BASE_DT","required_in_source":false,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"EQP_MODEL":{"coercion":"string","nullable":true,"physical_aliases":["EQP_MODEL"],"physical_column":"EQUIP_MODEL","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOAD_DATE":{"coercion":"strict_date","nullable":true,"physical_aliases":[],"physical_column":"LOAD_DT","required_in_source":false,"roles":["filter","output"],"semantic_type":"LocalDate"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRESS_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRESS_CNT","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"RECIPE_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"RECIPE_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"UPH":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"UPH","required_in_source":true,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"eqp_uph","parameters":{},"query_ref":"query:eqp_uph@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"GMS_DB","query_template":"SELECT \\n\\n  EQUIP_MODEL\\n  ,OPER\\n  ,OPER_NAME\\n  ,PRESS_CNT\\n  ,PROD_TYP AS \\"MODE\\"\\n  ,TECH\\n  ,ORG\\n  ,DENSITY\\n  ,PKG_TYP AS PKG1\\n  ,PKG_TYP_2 AS PKG2\\n  ,LEAD_CNT AS LEAD\\n  ,MCP_NO\\n  ,RECIPE_ID \\n  ,round(AVG_UPH_VAL,2) AS UPH\\n  ,WORK_DT AS LOAD_DT\\n  ,BASE_DT\\nFROM UPH\\nWHERE 1=1","required_params":[],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"equipment_assign":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["EQP_ID"],"family":"equipment","fields":{"BAY_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"BAY_ID","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"EQP_ID":{"coercion":"string","nullable":true,"physical_aliases":["EQP_ID"],"physical_column":"EQUIP_ID","required_in_source":false,"roles":["filter","group","aggregate","join","output"],"semantic_type":"identifier"},"EQP_MODEL":{"coercion":"string","nullable":true,"physical_aliases":["EQP_MODEL"],"physical_column":"EQUIP_MODEL","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOT_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LOT_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NAME"],"physical_column":"OPER_NM","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRESS_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRESS_CNT","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"RECIPE_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"RECIPE_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"}},"key":"equipment_assign","parameters":{},"query_ref":"query:equipment_assign@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"SELECT \\n  BAY_ID, \\n  EQUIP_ID, \\n  EQUIP_MODEL, \\n  PRESS_CNT,\\n  OPER,\\n  OPER_NM,\\n  MODE, \\n  DENSITY, \\n  TECH, \\n  PKG1, \\n  PKG2, \\n  LEAD, \\n  ORG,\\n  PKGSIZE,  \\n  MCP_NO,\\n  DEVICE,\\n  DEVICE_DESC,\\n  LOT_ID,\\n  RECIPE_ID\\nFROM  EQP_TABLE\\nWHERE 1=1","required_params":[],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"hold_history":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["LOT_ID","OPER_NAME","HOLD_EVENT_AT","HOLD_CD","HOLD_DESC"],"family":"hold_history","fields":{"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"HOLD_CD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_CD","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"HOLD_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"HOLD_EVENT_AT":{"coercion":"strict_datetime","nullable":false,"physical_aliases":[],"physical_column":"HOLD_TM","required_in_source":true,"roles":["filter","aggregate","sort","derive","output"],"semantic_type":"LocalDateTime","timezone":"Asia/Seoul"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOT_ID":{"coercion":"string","nullable":false,"physical_aliases":[],"physical_column":"LOT_ID","required_in_source":true,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PROD_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PROD_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"}},"key":"hold_history","parameters":{"LOT_ID":{"chunk_size":200,"max_total_values":2000,"operator":"in","required":true,"type":"list[identifier]"}},"query_ref":"query:hold_history@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"/*HOLD_LOT_HISTORY*/\\n\\n        SELECT\\n\\n            LOT_ID,\\n            PROD_QTY,\\n            OPER,\\n            OPER_NAME,\\n            HOLD_TM,\\n            HOLD_CD,\\n            HOLD_USER,\\n            HOLD_DESC,\\n            FAB,\\n            FAMILY,\\n            MODE,\\n            DENSITY,\\n            TECH,\\n            ORG,\\n            PKG1,\\n            PKG2,\\n            LEAD,\\n            MCP_NO,\\n            GRADE,\\n            OWNER,\\n            \\n            DEVICE,\\n            DEVICE_DESC,\\n            PKG_SIZE,\\n            THK_CD,\\n            flow_id   \\n        FROM HOLD_HIS\\n        WHERE LOT_ID IN ({LOT_ID})","required_params":["LOT_ID"],"source_type":"oracle"},"source_type":"oracle","time_scope":"history","upstream_bindings":[{"chunk_size":200,"dedupe":true,"entity_type":"lot","max_total_values":2000,"operator":"in","sort_values":"asc","source_alias":"previous_result","source_field":"LOT_ID","target_parameter":"LOT_ID"}]},"lot_status":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["LOT_ID","OPER_NAME","PROD_QTY","WF_QTY","IN_TAT","CUM_TAT","HOLD_STAT","HOLD_REASON","LOT_STAT"],"family":"lot","fields":{"CUM_TAT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"CUM_TAT","required_in_source":false,"roles":["filter","aggregate","rank","sort","output"],"semantic_type":"number"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"EQP_ID":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"EQP_ID","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAC_IN_AT":{"coercion":"strict_datetime","nullable":true,"physical_aliases":[],"physical_column":"FAC_IN_TIME","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"LocalDateTime","timezone":"Asia/Seoul"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"HOLD_REASON":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_REASON","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"HOLD_STAT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"HOLD_STAT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"IN_TAT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"IN_TAT","required_in_source":false,"roles":["filter","aggregate","rank","sort","output"],"semantic_type":"number"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"LOT_ID":{"coercion":"string","nullable":false,"physical_aliases":[],"physical_column":"LOT_ID","required_in_source":true,"roles":["filter","group","join","output"],"semantic_type":"identifier"},"LOT_STAT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LOT_STAT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OPER_IN_AT":{"coercion":"strict_datetime","nullable":true,"physical_aliases":[],"physical_column":"OPER_IN_TM","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"LocalDateTime","timezone":"Asia/Seoul"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":false,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":true,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PROD_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PROD_QTY","required_in_source":false,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"WF_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"WF_QTY","required_in_source":false,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"lot_status","parameters":{},"query_ref":"query:lot_status@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"/*Current Wip Status*/\\nSELECT\\nERM_ID,OPER,OPER_NAME,FAB,OWNER,GRADE,DEVICE,LOT_ID,SUB_LOT_ID,PROD_QTY,WF_QTY,IN_TAT,CUM_TAT,EQP_ID,FLOW_ID,OPER_IN_TM,FAC_IN_TIME,HOLD_STAT,HOLD_REASON,FAMILY,MODE,DENSITY,TECH,ORG,PKG1,PKG2,PKG3,LEAD,MCP_NO,THK_CD,LOT_STAT,LOT_GRP,PKG_SIZE,HOT_LOT,HOT_LEVEL,PKG_COMPOSIT,DURABLE_ID,DURABLE_TYP,SUB_QTY,TSV_DIE_TYPE,EVENT_DESC,MOVE_IN_TM,PAD_ABNORMAL,SWR_REQ_NO,INSP_TARGET\\nFROM WIP_STATE\\nWHERE 1=1","required_params":[],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"product_master":{"config_ref":"config:fixture:operator_validation@1","default_detail_fields":["DEVICE","YIELD_RATE","MODE","LEAD"],"family":"product_master","fields":{"DEN":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEN","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":false,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":true,"roles":["filter","group","join","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"PKG_TYPE1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"PKG_TYPE2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"YIELD_RATE":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"YIELD_RATE","required_in_source":false,"roles":["filter","rank","output"],"semantic_type":"number"}},"fixture_only":true,"key":"product_master","parameters":{},"query_ref":"query:product_master_fixture@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_type":"fixture","time_scope":"current"},"production":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","PRODUCTION_QTY"],"family":"production","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRODUCTION_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRODUCTION","required_in_source":true,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"}},"key":"production","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:production_history@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"SELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ, PRODUCTION \\nFROM PROD_TABLE2\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"history"},"production_today":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","PRODUCTION_QTY"],"family":"production","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PRODUCTION_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"PRODUCTION","required_in_source":true,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"}},"key":"production_today","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:production_today@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"--쿼리 작성\\nSELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ, PRODUCTION \\nFROM PROD_TABLE\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"},"target":{"config_ref":"config:goodocs:target@1","date_filter_contract":{"canonical_field":"DATE","source_format":"%Y-%m-%d","timezone":"Asia/Seoul"},"default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DATE","INPUT_PLAN_QTY","OUT_PLAN_QTY"],"family":"target","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":[],"physical_column":"DATE","required_in_source":true,"roles":["filter","sort","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DENSITY"],"physical_column":"DEN","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"INPUT_PLAN_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"INPUT 계획","required_in_source":false,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":["MCP_NO"],"physical_column":"MCP NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":["MODE"],"physical_column":"Mode","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"OUT_PLAN_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OUT 계획","required_in_source":false,"roles":["filter","aggregate","rank","derive","output"],"semantic_type":"number"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"}},"key":"target","parameters":{},"query_ref":"query:target_plan@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_type":"goodocs","time_scope":"history"},"wip":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","WIP_QTY"],"family":"wip","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"WIP_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"WIP","required_in_source":true,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"wip","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:wip_history@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"--쿼리 작성\\nSELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ\\n        , WIP\\nFROM WIP_TABLE2\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"history"},"wip_today":{"config_ref":"config:oracle:PNT_RPT@1","default_detail_fields":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO","DEVICE","OPER_NAME","WIP_QTY"],"family":"wip","fields":{"DATE":{"coercion":"strict_date","nullable":false,"physical_aliases":["WORK_DT"],"physical_column":"WORK_DATE","required_in_source":true,"roles":["filter","output"],"semantic_type":"LocalDate"},"DEN":{"coercion":"string","nullable":true,"physical_aliases":["DEN"],"physical_column":"DENSITY","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"DEVICE_DESC","required_in_source":false,"roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"DIE_ATTACH_QTY","required_in_source":false,"roles":["filter","aggregate","output"],"semantic_type":"number"},"FAB":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAB","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FACTORY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"FAMILY":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"FAMILY","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"LEAD":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"LEAD","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MCP_NO":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MCP_NO","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"MODE","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"NETDIE_300_CNT","required_in_source":false,"roles":["filter","aggregate","derive","output"],"semantic_type":"number"},"OPER_NAME":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NM"],"physical_column":"OPER_NAME","required_in_source":false,"roles":["filter","group","join","sort","output"],"semantic_type":"string"},"OPER_NUM":{"coercion":"string","nullable":true,"physical_aliases":["OPER_NUM"],"physical_column":"OPER","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"OPER_SEQ","required_in_source":false,"roles":["filter","sort","output"],"semantic_type":"number"},"ORG":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"ORG","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE1":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE1"],"physical_column":"PKG1","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"coercion":"string","nullable":true,"physical_aliases":["PKG_TYPE2"],"physical_column":"PKG2","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"SHIFT":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"SHIFT","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"coercion":"string","nullable":true,"physical_aliases":[],"physical_column":"TECH","required_in_source":false,"roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"coercion":"string","nullable":true,"physical_aliases":["TSV_DIE_TYPE"],"physical_column":"TSV_DIE_TYP","required_in_source":false,"roles":["filter","group","output"],"semantic_type":"string"},"WIP_QTY":{"coercion":"strict_number","nullable":true,"physical_aliases":[],"physical_column":"WIP","required_in_source":true,"roles":["filter","aggregate","rank","output"],"semantic_type":"number"}},"key":"wip_today","parameters":{"DATE":{"physical_column":"WORK_DATE","required":true,"source_format":"%Y%m%d","timezone":"Asia/Seoul","type":"LocalDate"}},"query_ref":"query:wip_today@1","read_policy":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"source_config":{"db_key":"PNT_RPT","query_template":"SELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1\\n        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER\\n        , OPER_NAME, OPER_SEQ\\n        , WIP\\nFROM WIP_TABLE\\nWHERE 1=1\\nAND WORK_DATE = {DATE}","required_params":["DATE"],"source_type":"oracle"},"source_type":"oracle","time_scope":"current"}},"fields":{"BASE_DATE":{"datasets":["eqp_uph"],"display_label":"BASE_DATE","key":"BASE_DATE","roles":["filter","output"],"semantic_type":"LocalDate"},"BAY_ID":{"datasets":["equipment_assign"],"display_label":"BAY_ID","key":"BAY_ID","roles":["filter","group","output"],"semantic_type":"string"},"CUM_TAT":{"datasets":["lot_status"],"display_label":"CUM_TAT","key":"CUM_TAT","roles":["aggregate","filter","output","rank","sort"],"semantic_type":"number"},"DATE":{"datasets":["production","production_today","target","wip","wip_today"],"display_label":"DATE","key":"DATE","roles":["filter","output","sort"],"semantic_type":"LocalDate"},"DEN":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"DEN","key":"DEN","roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE":{"datasets":["equipment_assign","hold_history","lot_status","product_master","production","production_today","wip","wip_today"],"display_label":"DEVICE","key":"DEVICE","roles":["filter","group","join","output"],"semantic_type":"string"},"DEVICE_DESC":{"datasets":["equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"DEVICE_DESC","key":"DEVICE_DESC","roles":["filter","output"],"semantic_type":"string"},"DIE_ATTACH_QTY":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"DIE_ATTACH_QTY","key":"DIE_ATTACH_QTY","roles":["aggregate","filter","output"],"semantic_type":"number"},"EQP_ID":{"datasets":["equipment_assign","lot_status"],"display_label":"EQP_ID","key":"EQP_ID","roles":["aggregate","filter","group","join","output"],"semantic_type":"identifier"},"EQP_MODEL":{"datasets":["eqp_uph","equipment_assign"],"display_label":"EQP_MODEL","key":"EQP_MODEL","roles":["filter","group","join","output"],"semantic_type":"string"},"FAB":{"datasets":["equipment_assign","lot_status","production","production_today","wip","wip_today"],"display_label":"FAB","key":"FAB","roles":["filter","group","output"],"semantic_type":"string"},"FACTORY":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"FACTORY","key":"FACTORY","roles":["filter","group","output"],"semantic_type":"string"},"FAC_IN_AT":{"datasets":["lot_status"],"display_label":"FAC_IN_AT","key":"FAC_IN_AT","roles":["filter","output","sort"],"semantic_type":"LocalDateTime"},"FAMILY":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"FAMILY","key":"FAMILY","roles":["filter","group","output"],"semantic_type":"string"},"HOLD_CD":{"datasets":["hold_history"],"display_label":"HOLD_CD","key":"HOLD_CD","roles":["filter","group","output"],"semantic_type":"string"},"HOLD_DESC":{"datasets":["hold_history"],"display_label":"HOLD_DESC","key":"HOLD_DESC","roles":["filter","output"],"semantic_type":"string"},"HOLD_EVENT_AT":{"datasets":["hold_history"],"display_label":"HOLD_EVENT_AT","key":"HOLD_EVENT_AT","roles":["aggregate","derive","filter","output","sort"],"semantic_type":"LocalDateTime"},"HOLD_REASON":{"datasets":["lot_status"],"display_label":"HOLD_REASON","key":"HOLD_REASON","roles":["filter","output"],"semantic_type":"string"},"HOLD_STAT":{"datasets":["lot_status"],"display_label":"HOLD_STAT","key":"HOLD_STAT","roles":["filter","group","output"],"semantic_type":"string"},"INPUT_PLAN_QTY":{"datasets":["target"],"display_label":"INPUT_PLAN_QTY","key":"INPUT_PLAN_QTY","roles":["aggregate","derive","filter","output","rank"],"semantic_type":"number"},"IN_TAT":{"datasets":["lot_status"],"display_label":"IN_TAT","key":"IN_TAT","roles":["aggregate","filter","output","rank","sort"],"semantic_type":"number"},"LEAD":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"LEAD","key":"LEAD","roles":["filter","group","join","output"],"semantic_type":"string"},"LOAD_DATE":{"datasets":["eqp_uph"],"display_label":"LOAD_DATE","key":"LOAD_DATE","roles":["filter","output"],"semantic_type":"LocalDate"},"LOT_ID":{"datasets":["equipment_assign","hold_history","lot_status"],"display_label":"LOT_ID","key":"LOT_ID","roles":["filter","group","join","output"],"semantic_type":"identifier"},"LOT_STAT":{"datasets":["lot_status"],"display_label":"LOT_STAT","key":"LOT_STAT","roles":["filter","group","output"],"semantic_type":"string"},"MCP_NO":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"MCP_NO","key":"MCP_NO","roles":["filter","group","join","output"],"semantic_type":"string"},"MODE":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"MODE","key":"MODE","roles":["filter","group","join","output"],"semantic_type":"string"},"NETDIE_300_CNT":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"NETDIE_300_CNT","key":"NETDIE_300_CNT","roles":["aggregate","derive","filter","output"],"semantic_type":"number"},"OPER_IN_AT":{"datasets":["lot_status"],"display_label":"OPER_IN_AT","key":"OPER_IN_AT","roles":["filter","output","sort"],"semantic_type":"LocalDateTime"},"OPER_NAME":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"OPER_NAME","key":"OPER_NAME","roles":["filter","group","join","output","sort"],"semantic_type":"string"},"OPER_NUM":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","wip","wip_today"],"display_label":"OPER_NUM","key":"OPER_NUM","roles":["filter","group","output"],"semantic_type":"string"},"OPER_SEQ":{"datasets":["eqp_uph","lot_status","production","production_today","wip","wip_today"],"display_label":"OPER_SEQ","key":"OPER_SEQ","roles":["filter","output","sort"],"semantic_type":"number"},"ORG":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","production","production_today","target","wip","wip_today"],"display_label":"ORG","key":"ORG","roles":["filter","group","join","output"],"semantic_type":"string"},"OUT_PLAN_QTY":{"datasets":["target"],"display_label":"OUT_PLAN_QTY","key":"OUT_PLAN_QTY","roles":["aggregate","derive","filter","output","rank"],"semantic_type":"number"},"PKG_TYPE1":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"PKG_TYPE1","key":"PKG_TYPE1","roles":["filter","group","join","output"],"semantic_type":"string"},"PKG_TYPE2":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"PKG_TYPE2","key":"PKG_TYPE2","roles":["filter","group","join","output"],"semantic_type":"string"},"PRESS_CNT":{"datasets":["eqp_uph","equipment_assign"],"display_label":"PRESS_CNT","key":"PRESS_CNT","roles":["aggregate","filter","output"],"semantic_type":"number"},"PRODUCTION_QTY":{"datasets":["production","production_today"],"display_label":"PRODUCTION_QTY","key":"PRODUCTION_QTY","roles":["aggregate","derive","filter","output","rank"],"semantic_type":"number"},"PROD_QTY":{"datasets":["hold_history","lot_status"],"display_label":"PROD_QTY","key":"PROD_QTY","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"RECIPE_ID":{"datasets":["eqp_uph","equipment_assign"],"display_label":"RECIPE_ID","key":"RECIPE_ID","roles":["filter","group","join","output"],"semantic_type":"identifier"},"SHIFT":{"datasets":["equipment_assign","production","production_today","wip","wip_today"],"display_label":"SHIFT","key":"SHIFT","roles":["filter","group","output"],"semantic_type":"string"},"TECH":{"datasets":["eqp_uph","equipment_assign","hold_history","lot_status","product_master","production","production_today","target","wip","wip_today"],"display_label":"TECH","key":"TECH","roles":["filter","group","join","output"],"semantic_type":"string"},"TSV_DIE_TYP":{"datasets":["equipment_assign","lot_status","production","production_today","wip","wip_today"],"display_label":"TSV_DIE_TYP","key":"TSV_DIE_TYP","roles":["filter","group","output"],"semantic_type":"string"},"UPH":{"datasets":["eqp_uph"],"display_label":"UPH","key":"UPH","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"WF_QTY":{"datasets":["lot_status"],"display_label":"WF_QTY","key":"WF_QTY","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"WIP_QTY":{"datasets":["wip","wip_today"],"display_label":"WIP_QTY","key":"WIP_QTY","roles":["aggregate","filter","output","rank"],"semantic_type":"number"},"YIELD_RATE":{"datasets":["product_master"],"display_label":"YIELD_RATE","key":"YIELD_RATE","roles":["filter","output","rank"],"semantic_type":"number"}},"metrics":{"ACHIEVEMENT_RATE":{"dependencies":["INPUT_QTY","INPUT_PLAN_QTY"],"formula":{"evaluation_stage":"after_aggregate","expression":{"args":[{"args":[{"metric_ref":"INPUT_QTY"},{"metric_ref":"INPUT_PLAN_QTY"}],"op":"safe_divide","zero_division":"null"},{"literal":100,"value_type":"number"}],"op":"multiply"},"max_depth":6,"max_nodes":32,"rounding":{"digits":1,"mode":"half_even"},"version":"formula.v1"},"metric_id":"ACHIEVEMENT_RATE","unit":"percent","value_type":"number"},"CUM_TAT":{"additivity":{"allowed_rollups":["min","max","mean"],"default":"non_additive"},"metric_id":"CUM_TAT","null_policy":"exclude","source_binding":{"dataset_family":"lot","field":"CUM_TAT"},"unit":"hour","value_type":"number","zero_policy":"preserve_zero"},"EQP_COUNT":{"additivity":{"allowed_rollups":["nunique"],"default":"distinct"},"metric_id":"EQP_COUNT","null_policy":"exclude","source_binding":{"dataset_family":"equipment","field":"EQP_ID"},"unit":"equipment","value_type":"integer","zero_policy":"preserve_zero"},"HOLD_DURATION_HOURS":{"additivity":{"allowed_rollups":["min","max"],"default":"non_additive"},"dependencies":["HOLD_EVENT_AT","reference_instant"],"formula":{"evaluation_stage":"after_aggregate","expression":{"args":[{"runtime_ref":"reference_instant"},{"field_ref":"CURRENT_HOLD_STARTED_AT"}],"op":"datetime_diff_hours"},"max_depth":3,"max_nodes":8,"rounding":{"digits":3,"mode":"half_even"},"version":"formula.v1"},"metric_id":"HOLD_DURATION_HOURS","null_policy":"exclude","unit":"hour","value_type":"number","zero_policy":"preserve_zero"},"INPUT_PLAN_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"INPUT_PLAN_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"target","field":"INPUT_PLAN_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"INPUT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"INPUT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY","fixed_filters":[{"field":"OPER_NAME","operator":"eq","semantic_type":"string","value":"INPUT"}]},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"IN_TAT":{"additivity":{"allowed_rollups":["min","max","mean"],"default":"non_additive"},"metric_id":"IN_TAT","null_policy":"exclude","source_binding":{"dataset_family":"lot","field":"IN_TAT"},"unit":"hour","value_type":"number","zero_policy":"preserve_zero"},"LOT_COUNT":{"additivity":{"allowed_rollups":["nunique"],"default":"distinct"},"metric_id":"LOT_COUNT","null_policy":"exclude","source_binding":{"dataset_family":"lot","field":"LOT_ID"},"unit":"lot","value_type":"integer","zero_policy":"preserve_zero"},"OUT_PLAN_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"OUT_PLAN_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"target","field":"OUT_PLAN_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"OUT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"OUT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY","fixed_filters":[{"field":"OPER_NAME","operator":"eq","semantic_type":"string","value":"PKG OUT"}]},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"PKG_OUT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"PKG_OUT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY","fixed_filters":[{"field":"OPER_NAME","operator":"eq","semantic_type":"string","value":"PKG OUT"}]},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"PRODUCTION_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"PRODUCTION_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"production","field":"PRODUCTION_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"UNIT_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"UNIT_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"lot","field":"PROD_QTY"},"unit":"unit","value_type":"number","zero_policy":"preserve_zero"},"UPH":{"additivity":{"allowed_rollups":["mean"],"default":"non_additive"},"metric_id":"UPH","null_policy":"exclude_from_mean","source_binding":{"dataset_family":"equipment_uph","field":"UPH"},"unit":"unit_per_hour","value_type":"number","zero_policy":"preserve_zero"},"WAFER_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"WAFER_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"lot","field":"WF_QTY"},"unit":"wafer","value_type":"number","zero_policy":"preserve_zero"},"WIP_BOH_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"WIP_BOH_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"wip","field":"WIP_QTY"},"temporal_contract":{"business_timepoint":"BOH","dataset_selector":{"dataset_key":"wip","family":"wip","time_scope":"history"},"disallowed_dataset_keys":["wip_today"],"display_date":"requested_date","inherit_filters":true,"query_time":{"anchor":"requested_date","calendar":"gregorian","offset_days":-1,"timezone":"Asia/Seoul"},"source_parameter":"DATE"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"},"WIP_QTY":{"additivity":{"allowed_rollups":["sum"],"default":"additive"},"metric_id":"WIP_QTY","null_policy":"exclude_from_sum","source_binding":{"dataset_family":"wip","field":"WIP_QTY"},"unit":"count","value_type":"number","zero_policy":"preserve_zero"}},"process_groups":{"BG":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["BG","BG공정","BG 공정","B/G","B/G공정","B/G 공정"],"display_name":"B/G","expansion":"closed_set","group_id":"process_group.BG","members":["B/G1","B/G2"],"target_field":"OPER_NAME"},"BM":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["BM","BM공정","BM 공정","B/M","B/M공정","B/M 공정","비엠","비엠공정","비엠 공정"],"display_name":"B/M","expansion":"closed_set","group_id":"process_group.BM","members":["B/M"],"target_field":"OPER_NAME"},"DA":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DA","DA공정","DA 공정","D/A","D/A공정","D/A 공정"],"display_name":"D/A","expansion":"closed_set","group_id":"process_group.DA","members":["D/A1","D/A2","D/A3","D/A4","D/A5","D/A6"],"target_field":"OPER_NAME"},"DC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DC","DC공정","DC 공정","D/C","D/C공정","D/C 공정"],"display_name":"D/C","expansion":"closed_set","group_id":"process_group.DC","members":["D/C1","D/C2","D/C3","D/C4"],"target_field":"OPER_NAME"},"DI":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DI","DI공정","DI 공정","D/I","D/I공정","D/I 공정","DVI","DVI공정","DVI 공정"],"display_name":"D/I","expansion":"closed_set","group_id":"process_group.DI","members":["D/I"],"target_field":"OPER_NAME"},"DP":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DP","DP공정","DP 공정","D/P","D/P공정","D/P 공정"],"display_name":"DP","expansion":"closed_set","group_id":"process_group.DP","members":["WET1","WET2","L/T1","L/T2","B/G1","B/G2","H/S1","H/S2","W/S1","W/S2","WSD1","WSD2","WEC1","WEC2","WLS1","WLS2","WVI","UV","C/C1"],"target_field":"OPER_NAME"},"DS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["DS","DS공정","DS 공정","D/S","D/S공정","D/S 공정"],"display_name":"D/S","expansion":"closed_set","group_id":"process_group.DS","members":["D/S1"],"target_field":"OPER_NAME"},"FCB":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["FCB","FCB공정","FCB 공정"],"display_name":"FCB","expansion":"closed_set","group_id":"process_group.FCB","members":["FCB1","FCB2","FCB/H"],"target_field":"OPER_NAME"},"FCBH":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["FCBH","FCBH공정","FCBH 공정","FCB/H","FCB/H공정","FCB/H 공정"],"display_name":"FCB/H","expansion":"closed_set","group_id":"process_group.FCBH","members":["FCB/H"],"target_field":"OPER_NAME"},"HS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["HS","HS공정","HS 공정","H/S","H/S공정","H/S 공정"],"display_name":"H/S","expansion":"closed_set","group_id":"process_group.HS","members":["H/S1","H/S2"],"target_field":"OPER_NAME"},"LT":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["LT","LT공정","LT 공정","L/T","L/T공정","L/T 공정"],"display_name":"L/T","expansion":"closed_set","group_id":"process_group.LT","members":["L/T1","L/T2"],"target_field":"OPER_NAME"},"PC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["PC","PC공정","PC 공정","P/C","P/C공정","P/C 공정"],"display_name":"P/C","expansion":"closed_set","group_id":"process_group.PC","members":["P/C1","P/C2","P/C3","P/C4","P/C5"],"target_field":"OPER_NAME"},"PCO":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["PCO","PCO공정","PCO 공정"],"display_name":"PCO","expansion":"closed_set","group_id":"process_group.PCO","members":["PCO1","PCO2","PCO3","PCO4","PCO5","PCO6"],"target_field":"OPER_NAME"},"PLH":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["PLH","PLH공정","PLH 공정","P/L","P/L공정","P/L 공정"],"display_name":"P/L","expansion":"closed_set","group_id":"process_group.PLH","members":["PLH"],"target_field":"OPER_NAME"},"QCSPC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["QCSPC","QCSPC공정","QCSPC 공정"],"display_name":"QCSPC","expansion":"closed_set","group_id":"process_group.QCSPC","members":["QCSPC1","QCSPC2","QCSPC3","QCSPC4"],"target_field":"OPER_NAME"},"SAT":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["SAT","SAT공정","SAT 공정"],"display_name":"SAT","expansion":"closed_set","group_id":"process_group.SAT","members":["SAT1","SAT2"],"target_field":"OPER_NAME"},"SBM":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["SBM","SBM공정","SBM 공정"],"display_name":"SBM","expansion":"closed_set","group_id":"process_group.SBM","members":["SBM"],"target_field":"OPER_NAME"},"SG":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["SG","SG공정","SG 공정","S/G","S/G공정","S/G 공정"],"display_name":"S/G","expansion":"closed_set","group_id":"process_group.SG","members":["S/G"],"target_field":"OPER_NAME"},"WB":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WB","WB공정","WB 공정","W/B","W/B공정","W/B 공정"],"display_name":"W/B","expansion":"closed_set","group_id":"process_group.WB","members":["W/B1","W/B2","W/B3","W/B4","W/B5","W/B6"],"target_field":"OPER_NAME"},"WBM":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WBM","WBM공정","WBM 공정","W/BM","W/BM공정","W/BM 공정"],"display_name":"W/BM","expansion":"closed_set","group_id":"process_group.WBM","members":["W/BM"],"target_field":"OPER_NAME"},"WEC":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WEC","WEC공정","WEC 공정"],"display_name":"WEC","expansion":"closed_set","group_id":"process_group.WEC","members":["WEC1","WEC2"],"target_field":"OPER_NAME"},"WET":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WET","WET공정","WET 공정"],"display_name":"WET","expansion":"closed_set","group_id":"process_group.WET","members":["WET1","WET2"],"target_field":"OPER_NAME"},"WLS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WLS","WLS공정","WLS 공정"],"display_name":"WLS","expansion":"closed_set","group_id":"process_group.WLS","members":["WLS1","WLS2"],"target_field":"OPER_NAME"},"WS":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WS","WS공정","WS 공정","W/S","W/S공정","W/S 공정"],"display_name":"W/S","expansion":"closed_set","group_id":"process_group.WS","members":["W/S1","W/S2"],"target_field":"OPER_NAME"},"WSD":{"alias_policy":{"conflict":"fail_ambiguous","match":"bounded_longest"},"aliases":["WSD","WSD공정","WSD 공정"],"display_name":"WSD","expansion":"closed_set","group_id":"process_group.WSD","members":["WSD1","WSD2"],"target_field":"OPER_NAME"}},"process_order":[{"aliases":["INPUT"],"oper_name":"INPUT","oper_seq":10,"revision":1},{"aliases":["DA1"],"oper_name":"D/A1","oper_seq":100,"revision":1},{"aliases":["DA2"],"oper_name":"D/A2","oper_seq":110,"revision":1},{"aliases":["DA3"],"oper_name":"D/A3","oper_seq":120,"revision":1},{"aliases":["DA4"],"oper_name":"D/A4","oper_seq":130,"revision":1},{"aliases":["DA5"],"oper_name":"D/A5","oper_seq":140,"revision":1},{"aliases":["DA6"],"oper_name":"D/A6","oper_seq":150,"revision":1},{"aliases":["DS1"],"oper_name":"D/S1","oper_seq":160,"revision":1},{"aliases":["WB1"],"oper_name":"W/B1","oper_seq":200,"revision":1},{"aliases":["WB2"],"oper_name":"W/B2","oper_seq":210,"revision":1},{"aliases":["WB3"],"oper_name":"W/B3","oper_seq":220,"revision":1},{"aliases":["WB4"],"oper_name":"W/B4","oper_seq":230,"revision":1},{"aliases":["WB5"],"oper_name":"W/B5","oper_seq":240,"revision":1},{"aliases":["WB6"],"oper_name":"W/B6","oper_seq":250,"revision":1},{"aliases":["WBM"],"oper_name":"W/BM","oper_seq":260,"revision":1},{"aliases":["FCB1"],"oper_name":"FCB1","oper_seq":300,"revision":1},{"aliases":["FCB2"],"oper_name":"FCB2","oper_seq":310,"revision":1},{"aliases":["FCBH"],"oper_name":"FCB/H","oper_seq":320,"revision":1},{"aliases":["BG1"],"oper_name":"B/G1","oper_seq":400,"revision":1},{"aliases":["BG2"],"oper_name":"B/G2","oper_seq":410,"revision":1},{"aliases":["SBM"],"oper_name":"SBM","oper_seq":500,"revision":1},{"aliases":["PKG OUT"],"oper_name":"PKG OUT","oper_seq":900,"revision":1}],"product_groups":{"AUTO":{"aliases":["AUTO향","오토모티브향","오토향"],"allowed_operators":["ends_with"],"grain_id":"product.standard","group_id":"product_group.AUTO","predicate":{"clauses":[{"field":"MCP_NO","operator":"ends_with","value":"I"},{"field":"MCP_NO","operator":"ends_with","value":"O"},{"field":"MCP_NO","operator":"ends_with","value":"N"},{"field":"MCP_NO","operator":"ends_with","value":"P"},{"field":"MCP_NO","operator":"ends_with","value":"Q"},{"field":"MCP_NO","operator":"ends_with","value":"V"}],"op":"any"}},"HBM":{"aliases":["HBM","3DS","TSV"],"allowed_operators":["is_not_blank"],"grain_id":"product.standard","group_id":"product_group.HBM","predicate":{"field":"TSV_DIE_TYP","operator":"is_not_blank"}},"MOBILE":{"aliases":["Mobile","MOBILE","모바일"],"allowed_operators":["eq","in","starts_with","null_or_blank","is_not_blank"],"grain_id":"product.standard","group_id":"product_group.MOBILE","predicate":{"clauses":[{"field":"MODE","operator":"starts_with","value":"LP"},{"field":"PKG_TYPE1","operator":"in","values":["LFBGA","TFBGA","UFBGA","VFBGA","WFBGA"]},{"field":"MCP_NO","operator":"null_or_blank"}],"op":"all"}},"POP":{"aliases":["POP","pop","Pop"],"allowed_operators":["eq","in","starts_with","null_or_blank","is_not_blank"],"grain_id":"product.standard","group_id":"product_group.POP","predicate":{"clauses":[{"field":"MODE","operator":"starts_with","value":"LP"},{"field":"PKG_TYPE1","operator":"in","values":["LFBGA","TFBGA","UFBGA","VFBGA","WFBGA"]},{"field":"MCP_NO","operator":"is_not_blank"}],"op":"all"}},"STACK_2HI":{"aliases":["2Hi"],"allowed_operators":["eq"],"grain_id":"product.standard","group_id":"product_group.STACK_2HI","predicate":{"field":"TSV_DIE_TYP","operator":"eq","value":"2Hi"}},"STACK_4HI":{"aliases":["4Hi"],"allowed_operators":["eq"],"grain_id":"product.standard","group_id":"product_group.STACK_4HI","predicate":{"field":"TSV_DIE_TYP","operator":"eq","value":"4Hi"}},"STACK_8HI":{"aliases":["8Hi"],"allowed_operators":["eq"],"grain_id":"product.standard","group_id":"product_group.STACK_8HI","predicate":{"field":"TSV_DIE_TYP","operator":"eq","value":"8Hi"}}},"recipes":{"achievement.input_actual":{"aliases":["생산달성률","생산달성율","INPUT 계획 대비 실적"],"default_operation_template":{"aggregate_before_derive":true,"derive":{"formula_ref":"metric:ACHIEVEMENT_RATE","op":"derive","output_field":"ACHIEVEMENT_RATE"}},"metrics":["INPUT_QTY","INPUT_PLAN_QTY","ACHIEVEMENT_RATE"],"recipe_id":"achievement.input_actual","required_slots":["actual_input","target_input","grain"]},"equipment.assignment_enrich":{"aliases":["할당된 장비 대수와 LIST","장비 배정","장비 목록"],"datasets":["equipment_assign"],"default_operation_template":{"cardinality":"one_to_one_after_aggregate","how":"left","keys":[{"left":"TECH","right":"TECH"},{"left":"DEN","right":"DEN"},{"left":"MODE","right":"MODE"},{"left":"PKG_TYPE1","right":"PKG_TYPE1"},{"left":"PKG_TYPE2","right":"PKG_TYPE2"},{"left":"LEAD","right":"LEAD"},{"left":"MCP_NO","right":"MCP_NO"}],"op":"enrich_previous_result","right_pre_aggregate":[{"as":"EQP_COUNT","field":"EQP_ID","function":"nunique"},{"as":"EQP_LIST","field":"EQP_ID","function":"list_unique"}],"suffix_policy":"forbid"},"recipe_id":"equipment.assignment_enrich","required_slots":["previous_product_result"]},"equipment.assignment_uph":{"aliases":["장비별 UPH","배정 장비 UPH","장비와 Recipe UPH"],"datasets":["equipment_assign","eqp_uph"],"default_operation_template":{"cardinality":"many_to_one","how":"left","keys":[{"left":"EQP_MODEL","right":"EQP_MODEL"},{"left":"RECIPE_ID","right":"RECIPE_ID"},{"left":"OPER_NAME","right":"OPER_NAME"}],"multi_match_policy":"error","null_key_policy":"never_match","op":"join","suffix_policy":"forbid"},"recipe_id":"equipment.assignment_uph","required_slots":["equipment","uph"]},"hold.oldest_current_history":{"aliases":["HOLD 시간이 가장 오래된 LOT","오래된 HOLD 이력"],"datasets":["hold_history"],"default_operation_template":{"steps":[{"group_by":["LOT_ID"],"metrics":[{"as":"CURRENT_HOLD_STARTED_AT","field":"HOLD_EVENT_AT","function":"max"}],"op":"aggregate"},{"formula_ref":"metric:HOLD_DURATION_HOURS","op":"derive","output_field":"HOLD_DURATION_HOURS"},{"include_ties":true,"mode":"top","n":1,"op":"rank","rank_by":[{"direction":"desc","field":"HOLD_DURATION_HOURS"}],"scope":"global","tie_break_by":[{"direction":"asc","field":"LOT_ID"}]},{"cardinality":"many_to_one","how":"inner","keys":[{"left":"LOT_ID","right":"LOT_ID"}],"multi_match_policy":"error","null_key_policy":"never_match","op":"join","suffix_policy":"forbid"},{"history_order":[{"direction":"desc","field":"HOLD_EVENT_AT"},{"direction":"asc","field":"LOT_ID"}],"op":"detail"}]},"derived_metrics":["HOLD_DURATION_HOURS"],"recipe_id":"hold.oldest_current_history","required_fields":["LOT_ID","HOLD_EVENT_AT"],"required_slots":["previous_current_hold_result","reference_instant"]},"join.operation.production_wip":{"aliases":["생산량과 재공수량","생산 WIP 비교"],"datasets":["production","production_today","wip","wip_today"],"default_operation_template":{"cardinality":"one_to_one_after_aggregate","empty_side_policy":"preserve_other_side_with_declared_null_metrics","how":"outer","keys":[{"left":"TECH","right":"TECH"},{"left":"DEN","right":"DEN"},{"left":"MODE","right":"MODE"},{"left":"PKG_TYPE1","right":"PKG_TYPE1"},{"left":"PKG_TYPE2","right":"PKG_TYPE2"},{"left":"LEAD","right":"LEAD"},{"left":"MCP_NO","right":"MCP_NO"}],"multi_match_policy":"error","null_key_policy":"blank_equals_blank","op":"join","suffix_policy":"forbid"},"recipe_id":"join.operation.production_wip","required_slots":["production_metric","wip_metric","grain"]},"ordered.process.range":{"aliases":["공정 구간","공정 범위","OPER_SEQ 범위"],"default_operation_template":{"field":"OPER_SEQ","filter_order":"before_general_filters","inclusive":"both","op":"ordered_range"},"recipe_id":"ordered.process.range","required_fields":["OPER_NAME","OPER_SEQ"],"required_slots":["range_start","range_end","dataset"]},"presence.left_positive_right_zero":{"aliases":["A는 있으나 B는 없음","실적 있음 재공 없음","존재 미존재"],"default_operation_template":{"keys":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO"],"left_metric_ref":"$left_metric.id","materialize_right_zero":true,"op":"presence_filter","right_metric_ref":"$right_metric.id"},"recipe_id":"presence.left_positive_right_zero","required_slots":["left_metric","right_metric","grain"]},"product.standard":{"aliases":["제품별","제품 기준","제품 집계"],"default_operation_template":{"group_by":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO"],"metrics":[{"as_ref":"$metric.id","field_ref":"$metric.field","function_ref":"$metric.rollup"}],"op":"aggregate"},"grain":{"entity_id":"product","grain_id":"product.standard","keys":["TECH","DEN","MODE","PKG_TYPE1","PKG_TYPE2","LEAD","MCP_NO"],"null_match_policy":"blank_equals_blank"},"recipe_id":"product.standard","required_slots":["dataset","metric"]},"rank.bottom_n":{"aliases":["하위 N개","가장 적은","BOTTOM N"],"default_operation_template":{"include_ties":false,"mode":"bottom","op":"rank","scope":"global","stable_tie_break":"declared_keys"},"recipe_id":"rank.bottom_n","required_slots":["metric","n"]},"rank.top_n":{"aliases":["상위 N개","가장 많은","TOP N"],"default_operation_template":{"include_ties":false,"mode":"top","op":"rank","scope":"global","stable_tie_break":"declared_keys"},"recipe_id":"rank.top_n","required_slots":["metric","n"]}}}')


EMBEDDED_SCHEMAS = json.loads('{"active-domain-pointer.schema.json":{"$id":"https://metadata-driven-v6.local/schemas/active-domain-pointer.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"metadata.active-domain-pointer.v1"},"domain_id":{"pattern":"^[a-z][a-z0-9_-]{1,63}$","type":"string"},"environment":{"pattern":"^[a-z][a-z0-9_-]{1,31}$","type":"string"},"package_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"revision":{"minimum":1,"type":"integer"},"status":{"const":"active"}},"required":["contract_version","domain_id","environment","revision","bundle_sha256","package_sha256","status"],"title":"metadata.active-domain-pointer.v1","type":"object"},"analysis-plan.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/analysis-plan.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"candidate_bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"catalog_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"analysis.plan.v1","type":"string"},"input_refs":{"items":{"minLength":1,"type":"string"},"maxItems":4,"type":"array","uniqueItems":true},"intent_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"lineage":{"$ref":"#/$defs/jsonObject"},"operations":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"minItems":1,"type":"array"},"plan_fingerprint":{"pattern":"^[0-9a-f]{64}$","type":"string"},"plan_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"result_contract":{"$ref":"#/$defs/jsonObject"},"result_operation_id":{"minLength":1,"type":"string"},"retrieval_jobs":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":32,"type":"array"}},"required":["contract_version","intent_sha256","candidate_bundle_sha256","catalog_sha256","retrieval_jobs","operations","result_operation_id","result_contract","lineage","plan_id","plan_fingerprint"],"title":"analysis.plan.v1","type":"object"},"analysis-result.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/analysis-result.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"columns":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"contract_version":{"const":"analysis.result.v1","type":"string"},"lineage":{"$ref":"#/$defs/jsonObject"},"operation_trace":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"plan_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"result_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"row_count":{"minimum":0,"type":"integer"},"rows":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":100000,"type":"array"},"status":{"enum":["ok","empty","partial"],"type":"string"}},"required":["contract_version","status","plan_id","columns","rows","row_count","lineage","operation_trace","result_sha256"],"title":"analysis.result.v1","type":"object"},"analysis-route.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/analysis-route.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"allOf":[{"if":{"properties":{"route":{"const":"deterministic"}},"required":["route"]},"then":{"properties":{"ambiguity_sets":{"maxItems":0},"selected_candidate_ids":{"minItems":1},"unresolved_slots":{"maxItems":0}}}},{"if":{"properties":{"route":{"const":"unsupported"}},"required":["route"]},"then":{"properties":{"reason_code":{"const":"unsupported_registry_gap"}}}}],"properties":{"ambiguity_sets":{"items":{"items":{"minLength":1,"type":"string"},"minItems":2,"type":"array","uniqueItems":true},"maxItems":32,"type":"array"},"contract_version":{"const":"analysis.route.v1","type":"string"},"eligibility_proof_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"reason_code":{"enum":["unique_complete_selection","semantic_choice_required","unsupported_registry_gap","ambiguous_candidate_selection","forced_equivalence_probe"],"type":"string"},"required_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"resolved_candidate_bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"route":{"enum":["deterministic","intent_llm","unsupported"],"type":"string"},"route_policy_version":{"const":"route-policy.v1","type":"string"},"selected_candidate_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"unresolved_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["contract_version","route","reason_code","resolved_candidate_bundle_sha256","selected_candidate_ids","required_slots","unresolved_slots","ambiguity_sets","route_policy_version","eligibility_proof_sha256"],"title":"analysis.route.v1","type":"object"},"answer-facts.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/answer-facts.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"answer.facts.v1","type":"string"},"facts":{"items":{"additionalProperties":false,"properties":{"fact_id":{"minLength":1,"type":"string"},"type":{"minLength":1,"type":"string"},"value":{"$ref":"#/$defs/jsonValue"}},"required":["fact_id","type","value"],"type":"object"},"maxItems":512,"type":"array"},"facts_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"plan_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"question":{"type":"string"},"result_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"}},"required":["contract_version","question","facts","result_sha256","plan_id","facts_sha256"],"title":"answer.facts.v1","type":"object"},"answer-sections.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/answer-sections.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"applied_criteria":{"$ref":"#/$defs/jsonObject"},"contract_version":{"const":"answer.sections.v1","type":"string"},"downloads":{"items":{"additionalProperties":false,"properties":{"label":{"minLength":1,"type":"string"},"ref_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"role":{"enum":["analysis_result","source_snapshot"],"type":"string"},"url":{"type":"string"}},"required":["ref_id","role","label","url"],"type":"object"},"maxItems":32,"type":"array"},"evidence":{"$ref":"#/$defs/jsonObject"},"next_questions":{"items":{"additionalProperties":false,"properties":{"id":{"minLength":1,"type":"string"},"text":{"minLength":1,"type":"string"}},"required":["id","text"],"type":"object"},"maxItems":3,"type":"array"},"notices":{"items":{"additionalProperties":false,"properties":{"code":{"minLength":1,"type":"string"},"message":{"minLength":1,"type":"string"}},"required":["code","message"],"type":"object"},"maxItems":64,"type":"array"},"result_table":{"additionalProperties":false,"properties":{"columns":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"data_ref":{"type":"string"},"row_count":{"minimum":0,"type":"integer"},"row_source":{"const":"data.rows","type":"string"}},"required":["row_source","columns","row_count","data_ref"],"type":"object"},"summary":{"additionalProperties":false,"properties":{"fact_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"headline":{"type":"string"}},"required":["headline","fact_ids"],"type":"object"}},"required":["contract_version","summary","result_table","applied_criteria","evidence","notices","downloads","next_questions"],"title":"answer.sections.v1","type":"object"},"approval-event.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/approval-event.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"candidate_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"candidate_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"approval.event.v1","type":"string"},"decided_at":{"format":"date-time","type":"string"},"decision":{"enum":["approved","rejected"],"type":"string"},"event_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"expires_at":{"format":"date-time","type":"string"},"idempotency_key":{"minLength":1,"type":"string"},"subject_id":{"minLength":1,"type":"string"}},"required":["contract_version","event_id","candidate_id","candidate_sha256","decision","subject_id","decided_at","expires_at","idempotency_key"],"title":"approval.event.v1","type":"object"},"config-registry.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/config-registry.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"acl_roles":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"adapter_type":{"enum":["oracle","h_api","datalake","goodocs","dummy"],"type":"string"},"config_ref":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"contract_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"config.registry.v1","type":"string"},"descriptor":{"$ref":"#/$defs/jsonObject"},"read_only":{"const":true},"revision":{"minimum":1,"type":"integer"}},"required":["contract_version","config_ref","adapter_type","revision","read_only","acl_roles","descriptor","contract_sha256"],"title":"config.registry.v1","type":"object"},"display-options.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/display-options.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"display.options.v1","type":"string"},"include_diagnostics":{"type":"boolean"},"profile":{"minLength":1,"type":"string"},"show_analysis_evidence":{"type":"boolean"},"show_applied_criteria":{"type":"boolean"},"show_data_retrieval":{"type":"boolean"},"show_download_links":{"type":"boolean"},"show_execution_plan":{"type":"boolean"},"show_intent_analysis":{"type":"boolean"},"show_next_questions":{"type":"boolean"},"show_notices":{"type":"boolean"},"show_pandas_code":{"type":"boolean"},"show_result_table":{"type":"boolean"},"table_preview_limit":{"maximum":20,"minimum":1,"type":"integer"}},"required":["contract_version","profile","include_diagnostics","show_result_table","table_preview_limit","show_analysis_evidence","show_download_links","show_notices","show_applied_criteria","show_next_questions","show_intent_analysis","show_data_retrieval","show_pandas_code","show_execution_plan"],"title":"display.options.v1","type":"object"},"domain-package.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":4096,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/domain-package.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"authoring_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"compiler_version":{"minLength":1,"type":"string"},"contract_version":{"const":"domain.package.v1"},"domain_id":{"pattern":"^[a-z][a-z0-9_-]{1,63}$","type":"string"},"environment":{"pattern":"^[a-z][a-z0-9_-]{1,31}$","type":"string"},"lifecycle":{"additionalProperties":false,"properties":{"status":{"enum":["draft","validated","active","deprecated","quarantined"]}},"required":["status"],"type":"object"},"package_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"revision":{"minimum":1,"type":"integer"},"runtime_catalog":{"$ref":"#/$defs/jsonObject"}},"required":["contract_version","domain_id","environment","revision","lifecycle","compiler_version","authoring_sha256","runtime_catalog","package_sha256","bundle_sha256"],"title":"domain.package.v1","type":"object"},"download-item.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/download-item.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"content_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"download.item.v1","type":"string"},"expires_at":{"format":"date-time","type":"string"},"format":{"const":"csv","type":"string"},"label":{"minLength":1,"type":"string"},"ref":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"role":{"enum":["result","source"],"type":"string"},"row_count":{"minimum":0,"type":"integer"},"url":{"anyOf":[{"minLength":1,"type":"string"},{"type":"null"}]}},"required":["contract_version","role","ref","url","format","expires_at","row_count","content_sha256","label"],"title":"download.item.v1","type":"object"},"error-registry.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/error-registry.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"error_registry.v1","type":"string"},"errors":{"items":{"additionalProperties":false,"properties":{"code":{"enum":["request_invalid","route_contract_error","intent_contract_error","metadata_dependency_error","metadata_budget_exceeded","plan_contract_error","missing_required_param","parameter_value_limit_exceeded","ambiguous_alias","ambiguous_field_binding","source_missing","source_retrieval_failed","source_timeout","source_row_limit_exceeded","source_acl_denied","source_schema_mismatch","source_coverage_incomplete","unsupported_operation","execution_memory_limit_exceeded","metric_rollup_violation","metric_lineage_violation","join_cardinality_violation","result_schema_violation","state_reference_expired","state_reference_forbidden","state_conflict","state_policy_mismatch","answer_claim_violation","approval_not_found","approval_expired","approval_hash_mismatch","approval_already_claimed","stale_candidate"],"type":"string"},"public_message":{"minLength":1,"type":"string"},"retryable":{"type":"boolean"},"stage":{"minLength":1,"type":"string"}},"required":["code","stage","retryable","public_message"],"type":"object"},"minItems":33,"type":"array","uniqueItems":true},"registry_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"}},"required":["contract_version","registry_sha256","errors"],"title":"error_registry.v1","type":"object"},"error.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/error.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"code":{"enum":["request_invalid","route_contract_error","intent_contract_error","metadata_dependency_error","metadata_budget_exceeded","plan_contract_error","missing_required_param","parameter_value_limit_exceeded","ambiguous_alias","ambiguous_field_binding","source_missing","source_retrieval_failed","source_timeout","source_row_limit_exceeded","source_acl_denied","source_schema_mismatch","source_coverage_incomplete","unsupported_operation","execution_memory_limit_exceeded","metric_rollup_violation","metric_lineage_violation","join_cardinality_violation","result_schema_violation","state_reference_expired","state_reference_forbidden","state_conflict","state_policy_mismatch","answer_claim_violation","approval_not_found","approval_expired","approval_hash_mismatch","approval_already_claimed","stale_candidate"],"type":"string"},"contract_version":{"const":"error.v1","type":"string"},"details":{"$ref":"#/$defs/jsonObject"},"error_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"error_registry_version":{"const":"error_registry.v1","type":"string"},"message":{"minLength":1,"type":"string"},"retryable":{"type":"boolean"},"stage":{"minLength":1,"type":"string"},"trace_id":{"minLength":1,"type":"string"}},"required":["contract_version","error_registry_version","error_id","code","stage","message","retryable","details","trace_id"],"title":"error.v1","type":"object"},"evidence-manifest.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/evidence-manifest.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"artifact_hashes":{"$ref":"#/$defs/jsonObject"},"contract_version":{"const":"evidence.manifest.v1","type":"string"},"dirty":{"type":"boolean"},"generated_at":{"format":"date-time","type":"string"},"git_sha":{"minLength":1,"type":"string"},"route_counts":{"$ref":"#/$defs/jsonObject"},"test_summary":{"$ref":"#/$defs/jsonObject"}},"required":["contract_version","git_sha","dirty","generated_at","artifact_hashes","route_counts","test_summary"],"title":"evidence.manifest.v1","type":"object"},"executable-blueprint.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"maxProperties":4096,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":4096,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/executable-blueprint.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"blueprint_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"metadata.executable-blueprint.v1"},"default_annotations":{"additionalProperties":false,"properties":{"description":{"maxLength":4000,"type":"string"},"display_name":{"maxLength":200,"minLength":1,"type":"string"}},"required":["display_name","description"],"type":"object"},"domain_id":{"pattern":"^[a-z][a-z0-9_-]{1,63}$","type":"string"},"environment":{"pattern":"^[a-z][a-z0-9_-]{1,31}$","type":"string"},"executable":{"additionalProperties":false,"properties":{"aliases":{"$ref":"#/$defs/jsonObject"},"contract_version":{"const":"metadata.authoring.draft.v1"},"datasets":{"$ref":"#/$defs/jsonObject"},"entity_groups":{"$ref":"#/$defs/jsonObject"},"grains":{"$ref":"#/$defs/jsonObject"},"locale":{"maxLength":32,"minLength":2,"type":"string"},"metrics":{"$ref":"#/$defs/jsonObject"},"orderings":{"$ref":"#/$defs/jsonObject"},"output_profile":{"$ref":"#/$defs/jsonObject"},"predicates":{"$ref":"#/$defs/jsonObject"},"prompt_extensions":{"$ref":"#/$defs/jsonObject"},"recipes":{"$ref":"#/$defs/jsonObject"},"relations":{"$ref":"#/$defs/jsonObject"},"source_provenance":{"$ref":"#/$defs/jsonObject"},"specialized_functions":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"timezone":{"maxLength":64,"minLength":1,"type":"string"}},"required":["contract_version","locale","timezone","datasets","metrics","entity_groups","grains","relations","orderings","predicates","recipes","aliases","prompt_extensions","specialized_functions","output_profile","source_provenance"],"type":"object"},"executable_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"source_manifest_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"}},"required":["contract_version","domain_id","environment","executable","default_annotations","source_manifest_sha256","executable_sha256","blueprint_sha256"],"title":"metadata.executable-blueprint.v1","type":"object"},"executed-result.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/executed-result.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"analysis_result_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"columns":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"contract_version":{"const":"executed.result.v1","type":"string"},"criteria":{"$ref":"#/$defs/jsonObject"},"entities":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"executed_result_contract_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"grain":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"lineage":{"$ref":"#/$defs/jsonObject"},"operation_trace":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"plan_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"result_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"row_count":{"minimum":0,"type":"integer"},"rows":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":100000,"type":"array"},"source_snapshot_sha256":{"items":{"pattern":"^[0-9a-f]{64}$","type":"string"},"maxItems":32,"type":"array"},"status":{"enum":["ok","empty","partial"],"type":"string"}},"required":["contract_version","status","plan_id","columns","rows","row_count","lineage","operation_trace","result_sha256","grain","entities","criteria","source_snapshot_sha256","analysis_result_sha256","executed_result_contract_sha256"],"title":"executed.result.v1","type":"object"},"flow-inventory.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/flow-inventory.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"flow.inventory.v1","type":"string"},"flows":{"items":{"additionalProperties":false,"properties":{"display_name":{"minLength":1,"type":"string"},"endpoint_name":{"minLength":1,"type":"string"},"flow_uuid":{"minLength":1,"type":"string"},"logical_key":{"minLength":1,"type":"string"},"trusted_core":{"const":true}},"required":["logical_key","endpoint_name","flow_uuid","display_name","trusted_core"],"type":"object"},"maxItems":5,"minItems":5,"type":"array"},"namespace_uuid":{"minLength":1,"type":"string"}},"required":["contract_version","namespace_uuid","flows"],"title":"flow.inventory.v1","type":"object"},"gaia-metadata.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/gaia-metadata.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"gaia.metadata.v1","type":"string"},"docs":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":0,"type":"array"},"followup_questions":{"items":{"additionalProperties":false,"properties":{"id":{"minLength":1,"type":"string"},"text":{"minLength":1,"type":"string"}},"required":["id","text"],"type":"object"},"maxItems":3,"type":"array"},"images":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":0,"type":"array"},"knowhows":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":0,"type":"array"},"trace_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"urls":{"items":{"additionalProperties":false,"properties":{"title":{"minLength":1,"type":"string"},"url":{"minLength":1,"type":"string"}},"required":["title","url"],"type":"object"},"maxItems":16,"type":"array"},"usage":{"additionalProperties":false,"properties":{"answer_llm_calls":{"maximum":1,"minimum":0,"type":"integer"},"intent_llm_calls":{"maximum":2,"minimum":0,"type":"integer"},"pandas_code_llm_calls":{"maximum":0,"minimum":0,"type":"integer"},"pandas_repair_llm_calls":{"maximum":0,"minimum":0,"type":"integer"}},"required":["intent_llm_calls","pandas_code_llm_calls","pandas_repair_llm_calls","answer_llm_calls"],"type":"object"}},"required":["contract_version","urls","followup_questions","trace_id","usage","docs","images","knowhows"],"title":"gaia.metadata.v1","type":"object"},"metadata-annotation-proposal.schema.json":{"$id":"https://metadata-driven-v6.local/schemas/metadata-annotation-proposal.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"description":{"maxLength":4000,"type":"string"},"display_name":{"maxLength":200,"minLength":1,"type":"string"}},"required":["display_name","description"],"title":"metadata authoring annotation proposal","type":"object"},"metadata-authoring-draft.schema.json":{"$defs":{"dataset":{"additionalProperties":false,"properties":{"config_ref":{"maxLength":256,"type":"string"},"date_filter_contract":{"additionalProperties":false,"maxProperties":32,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"type":"object"},"date_policy":{"additionalProperties":false,"default":{},"maxProperties":32,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"type":"object"},"default_detail_fields":{"default":[],"items":{"type":"string"},"maxItems":128,"type":"array","uniqueItems":true},"display_name":{"maxLength":200,"type":"string"},"family":{"maxLength":128,"minLength":1,"type":"string"},"fields":{"additionalProperties":false,"maxProperties":1024,"minProperties":1,"patternProperties":{"^[A-Za-z][A-Za-z0-9_.-]{0,127}$":{"$ref":"#/$defs/fieldBinding"}},"type":"object"},"fixture_only":{"type":"boolean"},"parameters":{"additionalProperties":false,"default":{},"maxProperties":128,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"query_ref":{"maxLength":256,"type":"string"},"read_policy":{"additionalProperties":false,"default":{"max_rows":50000,"read_only":true,"timeout_seconds":30},"properties":{"max_rows":{"maximum":1000000,"minimum":1,"type":"integer"},"read_only":{"const":true},"timeout_seconds":{"maximum":120,"minimum":1,"type":"integer"}},"type":"object"},"source_adapter":{"pattern":"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$","type":"string"},"source_config":{"$ref":"#/$defs/jsonObject"},"source_type":{"enum":["oracle","sql","mongodb","http","datalake","goodocs","file","dummy","previous_result"]},"time_scope":{"maxLength":64,"type":"string"},"upstream_bindings":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"}},"required":["family","source_type","fields"],"type":"object"},"fieldBinding":{"additionalProperties":false,"properties":{"aliases":{"default":[],"items":{"maxLength":256,"minLength":1,"type":"string"},"maxItems":64,"type":"array","uniqueItems":true},"allowed_filter_operators":{"items":{"type":"string"},"maxItems":32,"type":"array","uniqueItems":true},"allowed_rollups":{"items":{"type":"string"},"maxItems":16,"type":"array","uniqueItems":true},"case_policy":{"maxLength":64,"type":"string"},"coercion":{"maxLength":64,"type":"string"},"multiplier":{"type":"number"},"null_policy":{"maxLength":64,"type":"string"},"nullable":{"default":true,"type":"boolean"},"physical_aliases":{"default":[],"items":{"maxLength":256,"minLength":1,"type":"string"},"maxItems":32,"type":"array","uniqueItems":true},"physical_column":{"maxLength":256,"minLength":1,"type":"string"},"required_in_source":{"default":false,"type":"boolean"},"roles":{"items":{"enum":["filter","group","join","compare","aggregate","derive","project","sort","rank","metric","output"]},"maxItems":16,"minItems":1,"type":"array","uniqueItems":true},"semantic_type":{"maxLength":64,"minLength":1,"type":"string"},"timezone":{"maxLength":64,"type":"string"},"unit":{"maxLength":64,"type":"string"}},"required":["physical_column","semantic_type","roles"],"type":"object"},"jsonObject":{"additionalProperties":false,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":4096,"type":"array"},{"$ref":"#/$defs/jsonObject"}]},"promptExtensions":{"additionalProperties":false,"default":{"answer":"","intent":""},"properties":{"answer":{"default":"","maxLength":12000,"type":"string"},"intent":{"default":"","maxLength":12000,"type":"string"}},"type":"object"},"registeredFunctionCallTemplate":{"additionalProperties":false,"properties":{"dataset_ref":{"maxLength":128,"minLength":1,"type":"string"},"field_ref":{"maxLength":128,"minLength":1,"type":"string"},"output_fields":{"items":{"maxLength":128,"minLength":1,"type":"string"},"maxItems":128,"minItems":1,"type":"array","uniqueItems":true},"parameters":{"additionalProperties":false,"properties":{"case_sensitive":{"type":"boolean"},"match_mode":{"enum":["any","all"]},"operator":{"enum":["equals","contains","starts_with","ends_with"]},"tokens":{"items":{"maxLength":256,"minLength":1,"type":"string"},"maxItems":64,"minItems":1,"type":"array","uniqueItems":true}},"required":["tokens","operator","match_mode","case_sensitive"],"type":"object"}},"required":["dataset_ref","field_ref","parameters","output_fields"],"type":"object"},"registeredFunctionLimits":{"additionalProperties":false,"properties":{"max_input_rows":{"maximum":100000,"minimum":1,"type":"integer"},"max_output_bytes":{"maximum":8388608,"minimum":1,"type":"integer"},"max_output_rows":{"maximum":100000,"minimum":1,"type":"integer"},"timeout_ms":{"maximum":5000,"minimum":1,"type":"integer"}},"required":["timeout_ms","max_input_rows","max_output_rows","max_output_bytes"],"type":"object"},"specializedFunction":{"additionalProperties":false,"properties":{"aliases":{"items":{"maxLength":200,"minLength":1,"type":"string"},"maxItems":32,"minItems":1,"type":"array","uniqueItems":true},"call_template":{"$ref":"#/$defs/registeredFunctionCallTemplate"},"execution_mode":{"const":"registered_standalone"},"failure_policy":{"const":"fail_closed"},"function_id":{"pattern":"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$","type":"string"},"implementation_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"input_schema":{"$ref":"#/$defs/jsonObject"},"limits":{"$ref":"#/$defs/registeredFunctionLimits"},"output_schema":{"$ref":"#/$defs/jsonObject"},"required_fields":{"default":[],"items":{"type":"string"},"maxItems":128,"type":"array","uniqueItems":true},"version":{"minimum":1,"type":"integer"}},"required":["function_id","version","execution_mode","implementation_sha256","input_schema","output_schema"],"type":"object"}},"$id":"https://metadata-driven-v6.local/schemas/metadata-authoring-draft.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"aliases":{"additionalProperties":false,"default":{},"maxProperties":4096,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"contract_version":{"const":"metadata.authoring.draft.v1"},"datasets":{"additionalProperties":false,"maxProperties":128,"minProperties":1,"patternProperties":{"^[A-Za-z][A-Za-z0-9_.-]{0,127}$":{"$ref":"#/$defs/dataset"}},"type":"object"},"description":{"maxLength":4000,"type":"string"},"display_name":{"maxLength":200,"minLength":1,"type":"string"},"entity_groups":{"additionalProperties":false,"default":{},"maxProperties":512,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"grains":{"additionalProperties":false,"default":{},"maxProperties":256,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"locale":{"default":"ko-KR","maxLength":32,"minLength":2,"type":"string"},"metrics":{"additionalProperties":false,"default":{},"maxProperties":512,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"orderings":{"additionalProperties":false,"default":{},"maxProperties":128,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"output_profile":{"additionalProperties":false,"default":{},"maxProperties":128,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"type":"object"},"predicates":{"additionalProperties":false,"default":{},"maxProperties":256,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"prompt_extensions":{"$ref":"#/$defs/promptExtensions"},"recipes":{"additionalProperties":false,"default":{},"maxProperties":256,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"relations":{"additionalProperties":false,"default":{},"maxProperties":256,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"source_provenance":{"additionalProperties":false,"default":{},"maxProperties":64,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"type":"object"},"specialized_functions":{"default":[],"items":{"$ref":"#/$defs/specializedFunction"},"maxItems":64,"type":"array"},"timezone":{"default":"Asia/Seoul","maxLength":64,"minLength":1,"type":"string"}},"required":["contract_version","display_name","datasets"],"title":"metadata.authoring.draft.v1","type":"object"},"metadata-authoring-proposal.schema.json":{"$defs":{"clarificationPayload":{"additionalProperties":false,"properties":{"missing_fields":{"items":{"maxLength":128,"minLength":1,"type":"string"},"maxItems":32,"type":"array","uniqueItems":true},"questions":{"items":{"maxLength":400,"minLength":1,"type":"string"},"maxItems":3,"minItems":1,"type":"array","uniqueItems":true}},"required":["questions","missing_fields"],"type":"object"}},"$id":"https://metadata-driven-v6.local/schemas/metadata-authoring-proposal.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","description":"자유형 자연어 메타데이터 입력을 한 번의 LLM 변환으로 만든 폐쇄형 제안 계약이다. 완성 초안 또는 최대 3개의 추가 확인 질문 중 하나만 허용한다.","oneOf":[{"additionalProperties":false,"properties":{"contract_version":{"const":"metadata.authoring.proposal.v1","type":"string"},"draft":{"$ref":"metadata-authoring-draft.schema.json"},"source_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"status":{"const":"complete","type":"string"}},"required":["contract_version","status","source_sha256","draft"],"type":"object"},{"additionalProperties":false,"properties":{"clarification":{"$ref":"#/$defs/clarificationPayload"},"contract_version":{"const":"metadata.authoring.proposal.v1","type":"string"},"source_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"status":{"const":"needs_clarification","type":"string"}},"required":["contract_version","status","source_sha256","clarification"],"type":"object"}],"title":"metadata.authoring.proposal.v1"},"metadata-authoring-response.schema.json":{"$defs":{"clarificationPayload":{"additionalProperties":false,"properties":{"contract_version":{"const":"metadata.authoring.clarification.v1","type":"string"},"missing_fields":{"items":{"maxLength":128,"minLength":1,"type":"string"},"maxItems":32,"type":"array","uniqueItems":true},"proposal_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"questions":{"items":{"maxLength":400,"minLength":1,"type":"string"},"maxItems":3,"minItems":1,"type":"array","uniqueItems":true},"source_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"}},"required":["contract_version","questions","missing_fields","source_sha256","proposal_sha256"],"type":"object"},"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/metadata-authoring-response.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"allOf":[{"if":{"properties":{"status":{"const":"error"}},"required":["status"]},"then":{"required":["error"]}},{"if":{"properties":{"status":{"const":"ok"}},"required":["status"]},"then":{"required":["candidate_id","candidate_sha256"]}},{"else":{"not":{"required":["clarification"]}},"if":{"properties":{"status":{"const":"needs_clarification"}},"required":["status"]},"then":{"not":{"anyOf":[{"required":["candidate_id"]},{"required":["candidate_sha256"]},{"required":["package_sha256"]},{"required":["bundle_sha256"]},{"required":["catalog_sha256"]},{"required":["revision"]},{"required":["persisted"]},{"required":["diff"]},{"required":["unchanged_section_checks"]},{"required":["validation"]},{"required":["expires_at"]},{"required":["idempotent_replay"]},{"required":["error"]}]},"required":["clarification"]}},{"if":{"properties":{"stage":{"const":"prepared"}},"required":["stage"]},"then":{"required":["persisted","diff","validation","expires_at"]}},{"if":{"properties":{"stage":{"const":"committed"}},"required":["stage"]},"then":{"required":["revision","idempotent_replay"]}}],"properties":{"authoring_kind":{"enum":["domain","dataset","main_filter","domain_policy"],"type":"string"},"bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"candidate_id":{"pattern":"^candidate:[0-9a-f]{64}$","type":"string"},"candidate_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"catalog_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"clarification":{"$ref":"#/$defs/clarificationPayload"},"contract_version":{"const":"metadata.authoring.response.v1","type":"string"},"diff":{"$ref":"#/$defs/jsonObject"},"domain_id":{"pattern":"^[a-z][a-z0-9_-]{1,63}$","type":"string"},"environment":{"pattern":"^[a-z][a-z0-9_-]{1,31}$","type":"string"},"error":{"$ref":"#/$defs/jsonObject"},"expires_at":{"format":"date-time","type":"string"},"idempotent_replay":{"type":"boolean"},"llm_usage":{"additionalProperties":false,"properties":{"annotation_llm_calls":{"maximum":1,"minimum":0,"type":"integer"},"draft_llm_calls":{"maximum":3,"minimum":0,"type":"integer"},"repair_llm_calls":{"const":0,"type":"integer"}},"required":["draft_llm_calls","repair_llm_calls"],"type":"object"},"metadata_contract_mode":{"const":"domain_package_v2","type":"string"},"package_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"persisted":{"type":"boolean"},"response_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"response_type":{"const":"metadata_authoring","type":"string"},"revision":{"minimum":0,"type":"integer"},"stage":{"maxLength":128,"minLength":1,"type":"string"},"status":{"enum":["ok","error","needs_clarification"],"type":"string"},"unchanged_section_checks":{"$ref":"#/$defs/jsonObject"},"validation":{"$ref":"#/$defs/jsonObject"}},"required":["contract_version","response_type","status","stage","authoring_kind","metadata_contract_mode","domain_id","environment","llm_usage","response_sha256"],"title":"metadata.authoring.response.v1","type":"object"},"metadata-bootstrap-dataset-ir.schema.json":{"$defs":{"datasetCard":{"additionalProperties":false,"properties":{"dataset_id":{"pattern":"^[A-Za-z][A-Za-z0-9_.-]{0,127}$","type":"string"},"display_name":{"maxLength":200,"minLength":1,"type":"string"},"fields":{"items":{"$ref":"#/$defs/fieldCard"},"maxItems":1024,"minItems":1,"type":"array"}},"required":["dataset_id","fields"],"type":"object"},"fieldCard":{"additionalProperties":false,"properties":{"col":{"maxLength":256,"minLength":1,"type":"string"},"id":{"pattern":"^[A-Za-z][A-Za-z0-9_.-]{0,127}$","type":"string"}},"required":["id","col"],"type":"object"}},"$id":"https://metadata-driven.local/contracts/metadata-bootstrap-dataset-ir.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"dataset_cards":{"items":{"$ref":"#/$defs/datasetCard"},"maxItems":128,"minItems":1,"type":"array"}},"required":["dataset_cards"],"title":"Compact Dataset Bootstrap Authoring IR v1","type":"object"},"metadata-bootstrap-main-filter-ir.schema.json":{"$id":"https://metadata-driven-v6.local/contracts/metadata-bootstrap-main-filter-ir.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"alias_additions":{"items":{"additionalProperties":false,"properties":{"expressions":{"items":{"maxLength":512,"minLength":1,"type":"string"},"maxItems":64,"minItems":1,"type":"array","uniqueItems":true},"target_id":{"maxLength":256,"minLength":1,"type":"string"},"target_type":{"enum":["dataset","field","metric","relation","grain","predicate","recipe","entity_group"],"type":"string"}},"required":["target_type","target_id","expressions"],"type":"object"},"maxItems":256,"minItems":1,"type":"array"}},"required":["alias_additions"],"title":"Metadata Bootstrap Main Filter IR","type":"object"},"metadata-bundle.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/metadata-bundle.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"compiler_compatibility":{"minLength":1,"type":"string"},"contract_version":{"const":"metadata.bundle.v1","type":"string"},"operator_registry_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"records":{"items":{"additionalProperties":false,"properties":{"contract_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"key":{"minLength":1,"type":"string"},"kind":{"minLength":1,"type":"string"},"revision":{"minimum":1,"type":"integer"}},"required":["kind","key","revision","contract_sha256"],"type":"object"},"maxItems":512,"minItems":1,"type":"array"}},"required":["contract_version","bundle_sha256","records","operator_registry_sha256","compiler_compatibility"],"title":"metadata.bundle.v1","type":"object"},"metadata-envelope.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/metadata-envelope.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"compiled_at":{"format":"date-time","type":"string"},"content_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"metadata.envelope.v1","type":"string"},"dependencies":{"items":{"additionalProperties":false,"properties":{"contract_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"key":{"minLength":1,"type":"string"},"kind":{"minLength":1,"type":"string"},"revision":{"minimum":1,"type":"integer"}},"required":["kind","key","revision","contract_sha256"],"type":"object"},"maxItems":256,"type":"array"},"key":{"minLength":1,"type":"string"},"payload":{"$ref":"#/$defs/jsonObject"},"record_type":{"minLength":1,"type":"string"},"revision":{"minimum":1,"type":"integer"},"status":{"enum":["draft","active","deprecated"],"type":"string"}},"required":["contract_version","record_type","key","revision","status","compiled_at","content_sha256","dependencies","payload"],"title":"metadata.envelope.v1","type":"object"},"model-profile.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/model-profile.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"model.profile.v1","type":"string"},"intent_route_only":{"const":true},"model":{"minLength":1,"type":"string"},"profile_id":{"minLength":1,"type":"string"},"provider":{"minLength":1,"type":"string"},"runs":{"minimum":3,"type":"integer"},"temperature":{"const":0,"type":"number"}},"required":["contract_version","profile_id","provider","model","temperature","runs","intent_route_only"],"title":"model.profile.v1","type":"object"},"operator-registry.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/operator-registry.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"aggregation_functions":{"items":{"enum":["sum","mean","min","max","count","nunique","median","std","var","list_unique"],"type":"string"},"minItems":10,"type":"array","uniqueItems":true},"contract_version":{"const":"operator_registry.v1","type":"string"},"filter_connectives":{"items":{"enum":["all","any"],"type":"string"},"minItems":2,"type":"array","uniqueItems":true},"filter_operators":{"items":{"enum":["eq","in","ne","not_in","gt","gte","lt","lte","between","contains","starts_with","ends_with","is_null","is_not_null","is_blank","is_not_blank","null_or_blank"],"type":"string"},"minItems":17,"type":"array","uniqueItems":true},"formula_operators":{"items":{"enum":["add","subtract","multiply","safe_divide","abs","round","min_pair","max_pair","coalesce","coalesce_blank","datetime_diff_hours"],"type":"string"},"minItems":11,"type":"array","uniqueItems":true},"join_types":{"items":{"enum":["inner","left","right","outer","semi","anti"],"type":"string"},"minItems":6,"type":"array","uniqueItems":true},"limits":{"additionalProperties":false,"properties":{"filter_max_depth":{"minimum":1,"type":"integer"},"filter_max_leaves":{"minimum":1,"type":"integer"},"formula_max_depth":{"minimum":1,"type":"integer"},"formula_max_nodes":{"minimum":1,"type":"integer"},"operation_max_count":{"minimum":1,"type":"integer"}},"required":["filter_max_depth","filter_max_leaves","formula_max_depth","formula_max_nodes","operation_max_count"],"type":"object"},"operations":{"items":{"additionalProperties":false,"properties":{"description":{"minLength":1,"type":"string"},"input_kinds":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"op":{"enum":["filter","ordered_range","product_token_match","project","derive","aggregate","compare_fields","compare_group_attributes","find_duplicate_groups","join","presence_filter","sort","rank","concat_segments","detail","dedupe","row_match_groups","enrich_previous_result","transform_previous_result","explain_previous","registered_call"],"type":"string"},"operator_id":{"pattern":"^[a-z][a-z0-9_]*\\\\.v[0-9]+$","type":"string"},"output_kind":{"enum":["frame","facts","scalar"],"type":"string"},"required_policy_keys":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["operator_id","op","input_kinds","output_kind","required_policy_keys","description"],"type":"object"},"minItems":21,"type":"array","uniqueItems":true},"registry_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"}},"required":["contract_version","registry_sha256","operations","filter_operators","filter_connectives","aggregation_functions","join_types","formula_operators","limits"],"title":"operator_registry.v1","type":"object"},"pending-metadata-write.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":4096,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/pending-metadata-write.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"authoring_kind":{"enum":["domain","dataset","main_filter","domain_policy"],"type":"string"},"base_bundle_sha256":{"anyOf":[{"pattern":"^[0-9a-f]{64}$","type":"string"},{"type":"null"}]},"base_package_sha256":{"anyOf":[{"pattern":"^[0-9a-f]{64}$","type":"string"},{"type":"null"}]},"base_revision":{"anyOf":[{"minimum":1,"type":"integer"},{"type":"null"}]},"candidate_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"candidate_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"pending.metadata.write.v1","type":"string"},"domain_id":{"pattern":"^[a-z][a-z0-9_-]{1,63}$","type":"string"},"environment":{"pattern":"^[a-z][a-z0-9_-]{1,31}$","type":"string"},"expires_at":{"format":"date-time","type":"string"},"hash_material":{"$ref":"#/$defs/jsonObject"},"prepared_at":{"format":"date-time","type":"string"},"status":{"const":"prepared","type":"string"},"target_revision":{"minimum":1,"type":"integer"}},"required":["contract_version","authoring_kind","domain_id","environment","candidate_id","candidate_sha256","status","target_revision","base_revision","base_bundle_sha256","base_package_sha256","prepared_at","expires_at","hash_material"],"title":"pending.metadata.write.v1","type":"object"},"query-registry.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/query-registry.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"action":{"enum":["read","list","get"],"type":"string"},"adapter_type":{"enum":["oracle","h_api","datalake","goodocs","dummy"],"type":"string"},"contract_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"query.registry.v1","type":"string"},"max_rows":{"minimum":1,"type":"integer"},"parameter_schema":{"$ref":"#/$defs/jsonObject"},"query_ref":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"revision":{"minimum":1,"type":"integer"},"timeout_seconds":{"minimum":1,"type":"integer"}},"required":["contract_version","query_ref","adapter_type","revision","action","parameter_schema","timeout_seconds","max_rows","contract_sha256"],"title":"query.registry.v1","type":"object"},"registered-call.schema.json":{"$id":"https://metadata-driven-v6.local/schemas/registered-call.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"arguments":{"oneOf":[{"additionalProperties":false,"properties":{"case_sensitive":{"type":"boolean"},"field_ref":{"maxLength":128,"minLength":1,"type":"string"},"match_mode":{"enum":["any","all"],"type":"string"},"operator":{"enum":["equals","contains","starts_with","ends_with"],"type":"string"},"tokens":{"items":{"maxLength":256,"minLength":1,"type":"string"},"maxItems":64,"minItems":1,"type":"array","uniqueItems":true}},"required":["field_ref","tokens","operator","match_mode","case_sensitive"],"type":"object"},{"additionalProperties":false,"properties":{"case_sensitive":{"type":"boolean"},"match_mode":{"const":"all"},"rules":{"items":{"additionalProperties":false,"properties":{"field_ref":{"maxLength":128,"minLength":1,"type":"string"},"operator":{"enum":["equals","starts_with","contains","ends_with"],"type":"string"},"value":{"maxLength":256,"minLength":1,"type":"string"}},"required":["field_ref","operator","value"],"type":"object"},"maxItems":32,"minItems":1,"type":"array"}},"required":["rules","match_mode","case_sensitive"],"type":"object"},{"additionalProperties":false,"properties":{"end":{"maxLength":128,"minLength":1,"type":"string"},"field_ref":{"maxLength":128,"minLength":1,"type":"string"},"ordering_items":{"items":{"additionalProperties":false,"properties":{"aliases":{"items":{"maxLength":128,"minLength":1,"type":"string"},"maxItems":32,"type":"array"},"label":{"maxLength":128,"minLength":1,"type":"string"},"sequence":{"type":"number"}},"required":["label","aliases","sequence"],"type":"object"},"maxItems":512,"minItems":1,"type":"array"},"start":{"maxLength":128,"minLength":1,"type":"string"}},"required":["field_ref","start","end","ordering_items"],"type":"object"}]},"contract_version":{"const":"registered_call.v1","type":"string"},"failure_policy":{"const":"fail_closed"},"function_ref":{"additionalProperties":false,"properties":{"function_id":{"enum":["core.trim_and_match_tokens","manufacturing.match_product_tokens","manufacturing.filter_ordered_range"]},"implementation_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"input_schema_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"output_schema_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"version":{"const":1}},"required":["function_id","version","implementation_sha256","input_schema_sha256","output_schema_sha256"],"type":"object"},"id":{"maxLength":128,"minLength":1,"type":"string"},"input":{"maxLength":256,"minLength":1,"type":"string"},"limits":{"additionalProperties":false,"properties":{"max_input_rows":{"maximum":100000,"minimum":1,"type":"integer"},"max_output_bytes":{"maximum":8388608,"minimum":1,"type":"integer"},"max_output_rows":{"maximum":100000,"minimum":1,"type":"integer"},"timeout_ms":{"maximum":5000,"minimum":1,"type":"integer"}},"required":["timeout_ms","max_input_rows","max_output_rows","max_output_bytes"],"type":"object"},"op":{"const":"registered_call"},"required_fields":{"items":{"maxLength":128,"minLength":1,"type":"string"},"maxItems":16,"minItems":1,"type":"array","uniqueItems":true}},"required":["contract_version","id","op","input","function_ref","required_fields","arguments","limits","failure_policy"],"title":"registered_call.v1","type":"object"},"registered-function-card.schema.json":{"$defs":{"callTemplate":{"additionalProperties":false,"properties":{"dataset_ref":{"maxLength":128,"minLength":1,"type":"string"},"field_ref":{"maxLength":128,"minLength":1,"type":"string"},"output_fields":{"items":{"maxLength":128,"minLength":1,"type":"string"},"maxItems":128,"minItems":1,"type":"array","uniqueItems":true},"parameters":{"additionalProperties":false,"properties":{"case_sensitive":{"type":"boolean"},"match_mode":{"enum":["any","all"],"type":"string"},"operator":{"enum":["equals","contains","starts_with","ends_with"],"type":"string"},"tokens":{"items":{"maxLength":256,"minLength":1,"type":"string"},"maxItems":64,"minItems":1,"type":"array","uniqueItems":true}},"required":["tokens","operator","match_mode","case_sensitive"],"type":"object"}},"required":["dataset_ref","field_ref","parameters","output_fields"],"type":"object"},"limits":{"additionalProperties":false,"properties":{"max_input_rows":{"maximum":100000,"minimum":1,"type":"integer"},"max_output_bytes":{"maximum":8388608,"minimum":1,"type":"integer"},"max_output_rows":{"maximum":100000,"minimum":1,"type":"integer"},"timeout_ms":{"maximum":5000,"minimum":1,"type":"integer"}},"required":["timeout_ms","max_input_rows","max_output_rows","max_output_bytes"],"type":"object"},"schemaObject":{"additionalProperties":false,"patternProperties":{"^.{1,128}$":{"$ref":"#/$defs/schemaValue"}},"properties":{},"required":[],"type":"object"},"schemaValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/schemaValue"},"maxItems":256,"type":"array"},{"$ref":"#/$defs/schemaObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/registered-function-card.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"aliases":{"items":{"maxLength":200,"minLength":1,"type":"string"},"maxItems":32,"minItems":1,"type":"array","uniqueItems":true},"call_template":{"$ref":"#/$defs/callTemplate"},"execution_mode":{"const":"registered_standalone"},"failure_policy":{"const":"fail_closed"},"function_id":{"const":"core.trim_and_match_tokens"},"implementation_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"input_schema":{"$ref":"#/$defs/schemaObject"},"limits":{"$ref":"#/$defs/limits"},"output_schema":{"$ref":"#/$defs/schemaObject"},"required_fields":{"items":{"maxLength":128,"minLength":1,"type":"string"},"maxItems":16,"minItems":1,"type":"array","uniqueItems":true},"version":{"const":1}},"required":["function_id","version","execution_mode","implementation_sha256","input_schema","output_schema","required_fields","limits","failure_policy","aliases","call_template"],"title":"registered.function.card.v1","type":"object"},"request-capsule.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/request-capsule.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"request.capsule.v1","type":"string"},"literal_candidates":{"items":{"additionalProperties":false,"properties":{"id":{"minLength":1,"type":"string"},"kind":{"minLength":1,"type":"string"},"resolver_version":{"minLength":1,"type":"string"},"source_span":{"minLength":1,"type":"string"},"value":{"$ref":"#/$defs/jsonValue"}},"required":["id","kind","source_span","value","resolver_version"],"type":"object"},"maxItems":64,"type":"array"},"owner_subject_id":{"minLength":1,"type":"string"},"question":{"minLength":1,"type":"string"},"reference_instant":{"format":"date-time","type":"string"},"request_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"session_id":{"minLength":1,"type":"string"},"state_ref":{"anyOf":[{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},{"type":"null"}]},"timezone":{"minLength":1,"type":"string"}},"required":["contract_version","request_id","question","owner_subject_id","session_id","reference_instant","timezone","literal_candidates","state_ref"],"title":"request.capsule.v1","type":"object"},"resolved-candidate-bundle.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/resolved-candidate-bundle.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"catalog_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"resolved.candidate.bundle.v1","type":"string"},"dataset_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"entity_group_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"field_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"function_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"grain_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"intent_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":32,"type":"array"},"metric_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"prompt_cards":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":32,"type":"array"},"recipe_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"relation_candidates":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"type":"array"},"request_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"route_decision":{"$ref":"#/$defs/jsonObject"},"route_evidence":{"$ref":"#/$defs/jsonObject"}},"required":["contract_version","request_id","catalog_sha256","dataset_candidates","field_candidates","metric_candidates","entity_group_candidates","grain_candidates","relation_candidates","recipe_candidates","function_candidates","intent_candidates","prompt_cards","bundle_sha256","route_decision","route_evidence"],"title":"resolved.candidate.bundle.v1","type":"object"},"response.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/response.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"allOf":[{"else":{"properties":{"clarification":{"type":"null"}}},"if":{"properties":{"status":{"const":"needs_clarification"}},"required":["status"]},"then":{"properties":{"clarification":{"additionalProperties":false,"properties":{"options":{"items":{"minLength":1,"type":"string"},"maxItems":20,"type":"array"},"question":{"minLength":1,"type":"string"}},"required":["question","options"],"type":"object"},"state":{"type":"null"}}}},{"if":{"properties":{"status":{"const":"error"}},"required":["status"]},"then":{"properties":{"state":{"type":"null"}}}}],"properties":{"analysis":{"$ref":"#/$defs/jsonObject"},"analysis_mode":{"const":"typed_ir","type":"string"},"answer_sections":{"$ref":"#/$defs/jsonObject"},"clarification":{"anyOf":[{"additionalProperties":false,"properties":{"options":{"items":{"minLength":1,"type":"string"},"maxItems":20,"type":"array"},"question":{"minLength":1,"type":"string"}},"required":["question","options"],"type":"object"},{"type":"null"}]},"contract_version":{"const":"response.v1","type":"string"},"data":{"additionalProperties":false,"properties":{"columns":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"row_count":{"minimum":0,"type":"integer"},"rows":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":50,"type":"array"}},"required":["columns","rows","row_count"],"type":"object"},"data_mode":{"enum":["dummy","inline","live"],"type":"string"},"data_refs":{"items":{"additionalProperties":false,"properties":{"content_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"download_url":{"type":"string"},"expires_at":{"format":"date-time","type":"string"},"path":{"const":"payload.rows","type":"string"},"ref_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"role":{"enum":["analysis_result","source_snapshot"],"type":"string"},"store":{"const":"agent_v6_result_store","type":"string"}},"required":["ref_id","role","content_sha256","expires_at","store","path","download_url"],"type":"object"},"maxItems":32,"type":"array"},"intent_plan":{"$ref":"#/$defs/jsonObject"},"message":{"type":"string"},"request":{"additionalProperties":false,"properties":{"question":{"anyOf":[{"type":"string"},{"type":"null"}]},"reference_instant":{"anyOf":[{"format":"date-time","type":"string"},{"type":"null"}]},"request_id":{"anyOf":[{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},{"type":"null"}]},"session_id":{"anyOf":[{"type":"string"},{"type":"null"}]},"timezone":{"anyOf":[{"type":"string"},{"type":"null"}]}},"required":["request_id","question","session_id","reference_instant","timezone"],"type":"object"},"response_type":{"const":"data_analysis","type":"string"},"stage_status":{"additionalProperties":false,"properties":{"analysis":{"enum":["ok","partial","empty","error","needs_clarification","not_called"],"type":"string"},"intent":{"enum":["ok","skipped","error","needs_clarification"],"type":"string"},"overall":{"enum":["ok","partial","empty","error","needs_clarification"],"type":"string"},"retrieval":{"enum":["ok","empty","error","not_called"],"type":"string"}},"required":["overall","intent","retrieval","analysis"],"type":"object"},"state":{"anyOf":[{"additionalProperties":false,"properties":{"executed_result_ref":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"expires_at":{"format":"date-time","type":"string"},"state_version":{"minimum":1,"type":"integer"}},"required":["state_version","executed_result_ref","expires_at"],"type":"object"},{"type":"null"}]},"status":{"enum":["ok","partial","empty","error","needs_clarification"],"type":"string"},"trace":{"additionalProperties":false,"properties":{"commit_order":{"items":{"minLength":1,"type":"string"},"maxItems":32,"type":"array"},"retrieval":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":32,"type":"array"},"route":{"$ref":"#/$defs/jsonObject"},"trace_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"usage":{"additionalProperties":false,"properties":{"answer_llm_calls":{"maximum":1,"minimum":0,"type":"integer"},"intent_llm_calls":{"maximum":2,"minimum":0,"type":"integer"},"pandas_code_llm_calls":{"maximum":0,"minimum":0,"type":"integer"},"pandas_repair_llm_calls":{"maximum":0,"minimum":0,"type":"integer"}},"required":["intent_llm_calls","pandas_code_llm_calls","pandas_repair_llm_calls","answer_llm_calls"],"type":"object"}},"required":["trace_id","route","retrieval","usage","commit_order"],"type":"object"}},"required":["contract_version","response_type","status","stage_status","message","data_mode","analysis_mode","request","intent_plan","analysis","clarification","data","data_refs","answer_sections","state","trace"],"title":"response.v1","type":"object"},"retrieval-job-bundle.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/retrieval-job-bundle.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"bindings":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":32,"type":"array"},"contract_version":{"const":"retrieval.job_bundle.v1","type":"string"},"job_bundle_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"jobs":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":64,"minItems":1,"type":"array"},"plan_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"}},"required":["contract_version","job_bundle_id","plan_id","bindings","jobs"],"title":"retrieval.job_bundle.v1","type":"object"},"runtime-catalog-v2.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonValue"}},"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":4096,"type":"array"},{"$ref":"#/$defs/jsonObject"}]},"registeredFunctionCallTemplate":{"additionalProperties":false,"properties":{"dataset_ref":{"maxLength":128,"minLength":1,"type":"string"},"field_ref":{"maxLength":128,"minLength":1,"type":"string"},"output_fields":{"items":{"maxLength":128,"minLength":1,"type":"string"},"maxItems":128,"minItems":1,"type":"array","uniqueItems":true},"parameters":{"additionalProperties":false,"properties":{"case_sensitive":{"type":"boolean"},"match_mode":{"enum":["any","all"]},"operator":{"enum":["equals","contains","starts_with","ends_with"]},"tokens":{"items":{"maxLength":256,"minLength":1,"type":"string"},"maxItems":64,"minItems":1,"type":"array","uniqueItems":true}},"required":["tokens","operator","match_mode","case_sensitive"],"type":"object"}},"required":["dataset_ref","field_ref","parameters","output_fields"],"type":"object"},"registeredFunctionLimits":{"additionalProperties":false,"properties":{"max_input_rows":{"maximum":100000,"minimum":1,"type":"integer"},"max_output_bytes":{"maximum":8388608,"minimum":1,"type":"integer"},"max_output_rows":{"maximum":100000,"minimum":1,"type":"integer"},"timeout_ms":{"maximum":5000,"minimum":1,"type":"integer"}},"required":["timeout_ms","max_input_rows","max_output_rows","max_output_bytes"],"type":"object"},"specializedFunction":{"additionalProperties":false,"properties":{"aliases":{"items":{"maxLength":200,"minLength":1,"type":"string"},"maxItems":32,"minItems":1,"type":"array","uniqueItems":true},"call_template":{"$ref":"#/$defs/registeredFunctionCallTemplate"},"execution_mode":{"const":"registered_standalone"},"failure_policy":{"const":"fail_closed"},"function_id":{"pattern":"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$","type":"string"},"implementation_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"input_schema":{"$ref":"#/$defs/jsonObject"},"limits":{"$ref":"#/$defs/registeredFunctionLimits"},"output_schema":{"$ref":"#/$defs/jsonObject"},"required_fields":{"items":{"minLength":1,"type":"string"},"maxItems":128,"type":"array","uniqueItems":true},"version":{"minimum":1,"type":"integer"}},"required":["function_id","version","execution_mode","implementation_sha256","input_schema","output_schema"],"type":"object"}},"$id":"https://metadata-driven-v6.local/schemas/runtime-catalog-v2.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"aliases":{"$ref":"#/$defs/jsonObject"},"catalog_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"compiler_version":{"minLength":1,"type":"string"},"contract_version":{"const":"metadata.runtime.catalog.v2"},"datasets":{"additionalProperties":false,"minProperties":1,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"description":{"type":"string"},"display_name":{"minLength":1,"type":"string"},"domain_id":{"pattern":"^[a-z][a-z0-9_-]{1,63}$","type":"string"},"entity_groups":{"$ref":"#/$defs/jsonObject"},"environment":{"pattern":"^[a-z][a-z0-9_-]{1,31}$","type":"string"},"fields":{"additionalProperties":false,"minProperties":1,"patternProperties":{"^.{1,256}$":{"$ref":"#/$defs/jsonObject"}},"type":"object"},"grains":{"$ref":"#/$defs/jsonObject"},"locale":{"type":"string"},"metrics":{"$ref":"#/$defs/jsonObject"},"orderings":{"$ref":"#/$defs/jsonObject"},"output_profile":{"$ref":"#/$defs/jsonObject"},"predicates":{"$ref":"#/$defs/jsonObject"},"prompt_extensions":{"$ref":"#/$defs/jsonObject"},"recipes":{"$ref":"#/$defs/jsonObject"},"relations":{"$ref":"#/$defs/jsonObject"},"revision":{"minimum":1,"type":"integer"},"specialized_functions":{"items":{"$ref":"#/$defs/specializedFunction"},"maxItems":64,"type":"array"},"timezone":{"type":"string"}},"required":["contract_version","domain_id","environment","revision","compiler_version","display_name","locale","timezone","datasets","fields","metrics","entity_groups","grains","relations","orderings","predicates","recipes","aliases","prompt_extensions","specialized_functions","output_profile","catalog_sha256"],"title":"metadata.runtime.catalog.v2","type":"object"},"semantic-intent-selection.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/semantic-intent-selection.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"analysis_kind":{"minLength":1,"type":"string"},"dimension_refs":{"items":{"additionalProperties":false,"properties":{"candidate_id":{"minLength":1,"type":"string"},"target_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["candidate_id","target_slots"],"type":"object"},"maxItems":32,"type":"array"},"filter_refs":{"items":{"additionalProperties":false,"properties":{"candidate_id":{"minLength":1,"type":"string"},"target_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["candidate_id","target_slots"],"type":"object"},"maxItems":32,"type":"array"},"followup":{"additionalProperties":false,"properties":{"drop":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"inherit":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"reference":{"minLength":1,"type":"string"},"replace":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["reference","inherit","replace","drop"],"type":"object"},"formula_refs":{"items":{"additionalProperties":false,"properties":{"candidate_id":{"minLength":1,"type":"string"},"target_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["candidate_id","target_slots"],"type":"object"},"maxItems":32,"type":"array"},"function_refs":{"items":{"additionalProperties":false,"properties":{"candidate_id":{"minLength":1,"type":"string"},"target_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["candidate_id","target_slots"],"type":"object"},"maxItems":32,"type":"array"},"metric_refs":{"items":{"additionalProperties":false,"properties":{"candidate_id":{"minLength":1,"type":"string"},"target_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["candidate_id","target_slots"],"type":"object"},"maxItems":32,"type":"array"},"operation_refs":{"items":{"additionalProperties":false,"properties":{"candidate_id":{"minLength":1,"type":"string"},"target_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["candidate_id","target_slots"],"type":"object"},"maxItems":64,"type":"array"},"recipe_refs":{"items":{"additionalProperties":false,"properties":{"candidate_id":{"minLength":1,"type":"string"},"target_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["candidate_id","target_slots"],"type":"object"},"maxItems":32,"type":"array"},"request_scope":{"enum":["new_analysis","previous_result_transform","previous_source_transform","previous_source_expand","followup_requery","previous_result_enrich","explain_previous"],"type":"string"},"time_refs":{"items":{"additionalProperties":false,"properties":{"candidate_id":{"minLength":1,"type":"string"},"target_slots":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["candidate_id","target_slots"],"type":"object"},"maxItems":16,"type":"array"},"unresolved":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true}},"required":["request_scope","analysis_kind","metric_refs","dimension_refs","filter_refs","time_refs","operation_refs","recipe_refs","function_refs","formula_refs","followup","unresolved"],"title":"analysis.intent.selection.v1","type":"object"},"semantic-intent.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/semantic-intent.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"candidate_bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"analysis.intent.v1","type":"string"},"intent_candidate_id":{"minLength":1,"type":"string"},"intent_generator":{"enum":["deterministic","llm"],"type":"string"},"intent_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"request_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"route":{"enum":["deterministic","intent_llm"],"type":"string"},"semantics":{"$ref":"#/$defs/jsonObject"}},"required":["contract_version","request_id","candidate_bundle_sha256","intent_candidate_id","semantics","intent_sha256"],"title":"analysis.intent.v1","type":"object"},"source-bundle.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/source-bundle.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"bundle_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"canonicalized":{"const":true},"content_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"contract_version":{"const":"source.bundle.v1","type":"string"},"sources":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":32,"minItems":1,"type":"array"}},"required":["contract_version","bundle_id","sources","canonicalized","content_sha256"],"title":"source.bundle.v1","type":"object"},"source-result.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/source-result.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"content_sha256":{"anyOf":[{"pattern":"^[0-9a-f]{64}$","type":"string"},{"type":"null"}]},"contract_version":{"const":"source.result.v1","type":"string"},"error":{"anyOf":[{"$ref":"#/$defs/jsonObject"},{"type":"null"}]},"job_id":{"minLength":1,"type":"string"},"row_count":{"minimum":0,"type":"integer"},"rows":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":20,"type":"array"},"schema":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":256,"type":"array"},"source_ref":{"anyOf":[{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},{"type":"null"}]},"status":{"enum":["ok","empty","error"],"type":"string"},"truncated":{"type":"boolean"}},"required":["contract_version","job_id","status","schema","rows","source_ref","row_count","truncated","content_sha256","error"],"title":"source.result.v1","type":"object"},"trace.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/trace.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"trace.v1","type":"string"},"events":{"items":{"$ref":"#/$defs/jsonObject"},"maxItems":128,"type":"array"},"trace_id":{"minLength":1,"type":"string"},"verbose_trace_ref":{"anyOf":[{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},{"type":"null"}]}},"required":["contract_version","trace_id","events","verbose_trace_ref"],"title":"trace.v1","type":"object"},"turn-state.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/turn-state.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"contract_version":{"const":"turn.state.v1","type":"string"},"etag":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"executed_result_ref":{"anyOf":[{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},{"type":"null"}]},"expires_at":{"format":"date-time","type":"string"},"last_question":{"minLength":1,"type":"string"},"owner_subject_id":{"minLength":1,"type":"string"},"parent_state_sha256":{"anyOf":[{"pattern":"^[0-9a-f]{64}$","type":"string"},{"type":"null"}]},"parent_turn_id":{"anyOf":[{"minLength":1,"type":"string"},{"type":"null"}]},"semantic_context":{"$ref":"#/$defs/jsonObject"},"session_id":{"minLength":1,"type":"string"},"state_version":{"minimum":1,"type":"integer"},"turn_id":{"minLength":1,"type":"string"}},"required":["contract_version","state_version","etag","owner_subject_id","session_id","turn_id","parent_turn_id","parent_state_sha256","last_question","semantic_context","executed_result_ref","expires_at"],"title":"turn.state.v1","type":"object"},"unsupported-telemetry.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/unsupported-telemetry.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"case_ref":{"anyOf":[{"minLength":1,"type":"string"},{"type":"null"}]},"contract_version":{"const":"unsupported.telemetry.v1","type":"string"},"first_seen_at":{"format":"date-time","type":"string"},"last_seen_at":{"format":"date-time","type":"string"},"metadata_bundle_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"missing_capability_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"normalized_shape_id":{"pattern":"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$","type":"string"},"occurrence_count":{"minimum":1,"type":"integer"},"operator_registry_sha256":{"pattern":"^[0-9a-f]{64}$","type":"string"},"route_policy_version":{"const":"route-policy.v1","type":"string"}},"required":["contract_version","normalized_shape_id","missing_capability_ids","metadata_bundle_sha256","operator_registry_sha256","route_policy_version","occurrence_count","first_seen_at","last_seen_at","case_ref"],"title":"unsupported.telemetry.v1","type":"object"},"validation-case.schema.json":{"$defs":{"jsonObject":{"additionalProperties":false,"patternProperties":{"^[A-Za-z_][A-Za-z0-9_.:/-]{0,127}$":{"$ref":"#/$defs/jsonValue"}},"properties":{},"required":[],"type":"object"},"jsonValue":{"anyOf":[{"type":["string","number","boolean","null"]},{"items":{"$ref":"#/$defs/jsonValue"},"maxItems":2048,"type":"array"},{"$ref":"#/$defs/jsonObject"}]}},"$id":"https://metadata-driven-v6.local/schemas/validation-case.schema.json","$schema":"https://json-schema.org/draft/2020-12/schema","additionalProperties":false,"properties":{"capability":{"minLength":1,"type":"string"},"case_id":{"pattern":"^[A-Z][A-Z0-9-]{1,31}$","type":"string"},"contract_version":{"const":"validation.case.v1","type":"string"},"equivalence_group_id":{"anyOf":[{"minLength":1,"type":"string"},{"type":"null"}]},"expected_answer_llm_calls":{"maximum":1,"minimum":0,"type":"integer"},"expected_error_code":{"anyOf":[{"enum":["request_invalid","route_contract_error","intent_contract_error","metadata_dependency_error","metadata_budget_exceeded","plan_contract_error","missing_required_param","parameter_value_limit_exceeded","ambiguous_alias","ambiguous_field_binding","source_missing","source_retrieval_failed","source_timeout","source_row_limit_exceeded","source_acl_denied","source_schema_mismatch","source_coverage_incomplete","unsupported_operation","execution_memory_limit_exceeded","metric_rollup_violation","metric_lineage_violation","join_cardinality_violation","result_schema_violation","state_reference_expired","state_reference_forbidden","state_conflict","state_policy_mismatch","answer_claim_violation","approval_not_found","approval_expired","approval_hash_mismatch","approval_already_claimed","stale_candidate"],"type":"string"},{"type":"null"}]},"expected_intent_llm_calls":{"maximum":1,"minimum":0,"type":"integer"},"expected_intent_retry_calls":{"maximum":1,"minimum":0,"type":"integer"},"expected_result_contract":{"additionalProperties":false,"properties":{"dataset_keys":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"error_stage":{"anyOf":[{"minLength":1,"type":"string"},{"type":"null"}]},"grain":{"minLength":1,"type":"string"},"invariant_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"operator_sequence":{"items":{"pattern":"^[a-z][a-z0-9_]*\\\\.v[0-9]+$","type":"string"},"maxItems":256,"type":"array"},"output_fields":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"row_oracle":{"enum":["contract_invariants","exact_fixture","not_applicable"],"type":"string"},"variant_oracles":{"items":{"additionalProperties":false,"properties":{"analysis_mode":{"minLength":1,"type":"string"},"invariant_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"retrieval_calls":{"minimum":0,"type":"integer"},"variant_id":{"minLength":1,"type":"string"}},"required":["variant_id","analysis_mode","retrieval_calls","invariant_ids"],"type":"object"},"maxItems":8,"type":"array"}},"required":["dataset_keys","operator_sequence","output_fields","grain","row_oracle","invariant_ids","variant_oracles","error_stage"],"type":"object"},"expected_retrieval_calls":{"anyOf":[{"minimum":0,"type":"integer"},{"type":"null"}]},"expected_route":{"enum":["deterministic","intent_llm","unsupported"],"type":"string"},"expected_semantic_contract":{"additionalProperties":false,"properties":{"analysis_kind":{"minLength":1,"type":"string"},"dimension_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"drop":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"filter_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"followup_mode":{"minLength":1,"type":"string"},"formula_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"inherit":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"metric_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"operation_ids":{"items":{"pattern":"^[a-z][a-z0-9_]*\\\\.v[0-9]+$","type":"string"},"maxItems":256,"type":"array"},"recipe_ids":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"replace":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"request_scope":{"minLength":1,"type":"string"}},"required":["request_scope","analysis_kind","metric_ids","dimension_ids","filter_ids","operation_ids","recipe_ids","formula_ids","followup_mode","inherit","replace","drop"],"type":"object"},"expected_status":{"enum":["ok","empty","error","needs_clarification"],"type":"string"},"fallback_allowed":{"const":false},"fixture_setup":{"additionalProperties":false,"properties":{"plan_fault_id":{"anyOf":[{"enum":["invalid_join_input"],"type":"string"},{"type":"null"}]},"seed_question":{"anyOf":[{"minLength":1,"type":"string"},{"type":"null"}]}},"required":["seed_question","plan_fault_id"],"type":"object"},"question":{"minLength":1,"type":"string"},"reference_instant":{"const":"2026-07-30T09:00:00+09:00","type":"string"},"route_reason":{"minLength":1,"type":"string"},"scenario_id":{"anyOf":[{"minLength":1,"type":"string"},{"type":"null"}]},"suite":{"enum":["single","date","multiturn","operator","branch"],"type":"string"},"tags":{"items":{"minLength":1,"type":"string"},"maxItems":256,"type":"array","uniqueItems":true},"timezone":{"const":"Asia/Seoul","type":"string"},"turn_index":{"anyOf":[{"minimum":1,"type":"integer"},{"type":"null"}]}},"required":["contract_version","case_id","suite","scenario_id","turn_index","question","capability","reference_instant","timezone","expected_route","route_reason","expected_intent_llm_calls","expected_intent_retry_calls","expected_answer_llm_calls","fallback_allowed","expected_retrieval_calls","expected_status","expected_error_code","expected_semantic_contract","expected_result_contract","fixture_setup","equivalence_group_id","tags"],"title":"validation.case.v1","type":"object"}}')



import math
import re


_SEMANTIC_VOCABULARY_SECTIONS = (
    "datasets", "fields", "metrics", "relations", "grains", "orderings",
    "predicates", "recipes", "entity_groups",
)
_SEMANTIC_VOCABULARY_LIMITS = {
    "datasets": (1, 128),
    "fields": (1, 4096),
    "metrics": (0, 1024),
    "relations": (0, 256),
    "grains": (0, 256),
    "orderings": (0, 128),
    "predicates": (0, 256),
    "recipes": (0, 256),
    "entity_groups": (0, 512),
}


def _validated_semantic_vocabulary(
    value,
    *,
    expected_dataset_families=None,
    expected_field_families=None,
):
    expected_root = {"contract_version", *_SEMANTIC_VOCABULARY_SECTIONS}
    if not isinstance(value, dict) or set(value) != expected_root:
        raise ValueError("Approved semantic vocabulary root contract is invalid.")
    if value.get("contract_version") != "metadata.authoring.semantic-vocabulary.v1":
        raise ValueError("Approved semantic vocabulary version is invalid.")
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    if len(encoded) > 64 * 1024:
        raise ValueError("Approved semantic vocabulary exceeds 65536 UTF-8 bytes.")

    id_pattern = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,127}")
    forbidden = (
        "http://", "https://", "mongodb://", "mongodb+srv://", "select ",
        "insert ", "update ", "delete ", "password", "secret", "token=", "api_key",
    )
    normalized = {"contract_version": "metadata.authoring.semantic-vocabulary.v1"}
    for section in _SEMANTIC_VOCABULARY_SECTIONS:
        cards = value.get(section)
        lower, upper = _SEMANTIC_VOCABULARY_LIMITS[section]
        if not isinstance(cards, list) or not lower <= len(cards) <= upper:
            raise ValueError(f"Approved semantic vocabulary {section} count is invalid.")
        expected_keys = (
            {"id", "family", "labels"}
            if section == "datasets"
            else ({"id", "families", "labels"} if section == "fields" else {"id", "labels"})
        )
        seen_ids = set()
        label_owners = {}
        normalized_cards = []
        for card in cards:
            if not isinstance(card, dict) or set(card) != expected_keys:
                raise ValueError(f"Approved semantic vocabulary {section} card is invalid.")
            item_id = card.get("id")
            if not isinstance(item_id, str) or not id_pattern.fullmatch(item_id) or item_id in seen_ids:
                raise ValueError(f"Approved semantic vocabulary {section} id is invalid or duplicated.")
            seen_ids.add(item_id)
            labels = card.get("labels")
            if not isinstance(labels, list) or len(labels) > 64:
                raise ValueError(f"Approved semantic vocabulary {section} labels are invalid.")
            folded_labels = set()
            normalized_labels = []
            for label in labels:
                if not isinstance(label, str):
                    raise ValueError(f"Approved semantic vocabulary {section} label is invalid.")
                normalized_label = re.sub(r"\s+", " ", label.strip())
                folded = normalized_label.casefold()
                owner = label_owners.setdefault(folded, item_id)
                if (
                    not normalized_label
                    or len(normalized_label.encode("utf-8")) > 512
                    or any(ord(character) < 32 for character in normalized_label)
                    or any(fragment in folded for fragment in forbidden)
                    or normalized_label != label
                    or folded in folded_labels
                    or owner != item_id
                ):
                    raise ValueError(f"Approved semantic vocabulary {section} label is invalid, duplicated, or ambiguous.")
                folded_labels.add(folded)
                normalized_labels.append(normalized_label)
            normalized_card = {"id": item_id, "labels": normalized_labels}
            if section == "datasets":
                family = card.get("family")
                if not isinstance(family, str) or not id_pattern.fullmatch(family):
                    raise ValueError("Approved semantic vocabulary dataset family is invalid.")
                normalized_card["family"] = family
            elif section == "fields":
                families = card.get("families")
                if (
                    not isinstance(families, list)
                    or not 1 <= len(families) <= 128
                    or families != sorted(set(families))
                    or any(not isinstance(family, str) or not id_pattern.fullmatch(family) for family in families)
                ):
                    raise ValueError("Approved semantic vocabulary field families are invalid.")
                normalized_card["families"] = list(families)
            normalized_cards.append(normalized_card)
        if [card["id"] for card in normalized_cards] != sorted(seen_ids):
            raise ValueError(f"Approved semantic vocabulary {section} cards must be sorted by id.")
        normalized[section] = normalized_cards

    if expected_dataset_families is not None:
        expected_datasets = {
            str(dataset_id): str(family)
            for dataset_id, family in expected_dataset_families.items()
        }
        vocabulary_datasets = {card["id"]: card["family"] for card in normalized["datasets"]}
        if vocabulary_datasets != expected_datasets:
            raise ValueError("Approved semantic vocabulary datasets do not match the source registry.")
    if expected_field_families is not None:
        expected_fields = {
            str(field_id): sorted({str(family) for family in families})
            for field_id, families in expected_field_families.items()
        }
        vocabulary_fields = {card["id"]: card["families"] for card in normalized["fields"]}
        if vocabulary_fields != expected_fields:
            raise ValueError("Approved semantic vocabulary fields do not match the source registry.")
    return normalized


def _semantic_maps_from_descriptors(dataset_descriptors):
    dataset_families = {}
    field_families = {}
    for dataset_id, descriptor in (dataset_descriptors or {}).items():
        if not isinstance(descriptor, dict):
            continue
        family = str(descriptor.get("family") or "")
        dataset_families[str(dataset_id)] = family
        for field_id in (descriptor.get("fields") or {}):
            field_families.setdefault(str(field_id), set()).add(family)
    return dataset_families, field_families


def _dataset_field_allowlists_from_vocabulary(
    semantic_vocabulary, dataset_descriptors=None
):
    dataset_families = {
        str(card["id"]): str(card["family"])
        for card in (semantic_vocabulary or {}).get("datasets") or []
        if isinstance(card, dict)
    }
    field_families = {
        str(card["id"]): set(card.get("families") or [])
        for card in (semantic_vocabulary or {}).get("fields") or []
        if isinstance(card, dict)
    }
    if isinstance(dataset_descriptors, dict):
        if set(dataset_descriptors) != set(dataset_families):
            raise ValueError(
                "Approved dataset descriptors do not match the semantic vocabulary."
            )
        allowlists = {}
        for dataset_id, family in sorted(dataset_families.items()):
            descriptor = dataset_descriptors.get(dataset_id)
            fields = descriptor.get("fields") if isinstance(descriptor, dict) else None
            if not isinstance(fields, dict) or not fields:
                raise ValueError(
                    "Approved dataset descriptor has no exact field allowlist."
                )
            field_ids = sorted(str(field_id) for field_id in fields)
            if any(
                family not in field_families.get(field_id, set())
                for field_id in field_ids
            ):
                raise ValueError(
                    "Approved dataset descriptor field does not belong to its family."
                )
            allowlists[dataset_id] = field_ids
    else:
        allowlists = {
            dataset_id: sorted(
                field_id
                for field_id, families in field_families.items()
                if family in families
            )
            for dataset_id, family in sorted(dataset_families.items())
        }
    if not allowlists or any(not field_ids for field_ids in allowlists.values()):
        raise ValueError("Approved semantic vocabulary dataset field allowlists are empty.")
    return allowlists


_MAIN_FILTER_TARGET_SECTIONS = {
    "dataset": "datasets",
    "field": "fields",
    "metric": "metrics",
    "relation": "relations",
    "grain": "grains",
    "predicate": "predicates",
    "recipe": "recipes",
    "entity_group": "entity_groups",
}


def _main_filter_target_allowlists(semantic_vocabulary):
    allowlists = {}
    for target_type, section in _MAIN_FILTER_TARGET_SECTIONS.items():
        ids = sorted(
            {
                str(card["id"])
                for card in (semantic_vocabulary or {}).get(section) or []
                if isinstance(card, dict) and isinstance(card.get("id"), str)
            }
        )
        if ids:
            allowlists[target_type] = ids
    if not allowlists:
        raise ValueError("Approved Main Filter target allowlists are empty.")
    return allowlists


def _apply_main_filter_ir_allowlists(schema, semantic_vocabulary):
    projected = deepcopy(schema)
    additions = (projected.get("properties") or {}).get("alias_additions")
    base_item = additions.get("items") if isinstance(additions, dict) else None
    if not isinstance(base_item, dict) or not isinstance(base_item.get("properties"), dict):
        raise ValueError("Main Filter IR item schema is invalid.")
    branches = []
    for target_type, target_ids in sorted(
        _main_filter_target_allowlists(semantic_vocabulary).items()
    ):
        branch = deepcopy(base_item)
        branch["properties"]["target_type"] = {
            "type": "string",
            "enum": [target_type],
        }
        branch["properties"]["target_id"] = {
            "type": "string",
            "enum": target_ids,
        }
        branches.append(branch)
    additions["items"] = {"oneOf": branches}
    return projected


_SEMANTIC_TEMPLATE_SECTIONS = (
    "metrics", "relations", "entity_groups", "grains", "orderings",
    "predicates", "recipes",
)
_SEMANTIC_TEMPLATE_SPECS = {
    "metrics": ("metric_id", {
        "additivity", "aggregation", "aliases", "dependencies", "formula",
        "metric_id", "null_policy", "source_binding", "source_field",
        "temporal_contract", "unit", "value_type", "zero_policy",
    }, 1024),
    "relations": ("relation_id", {
        "aliases", "cardinality", "join_type", "key_mappings",
        "left_dataset", "left_keys", "multi_match_policy",
        "null_key_policy", "relation_id", "right_dataset", "right_keys",
    }, 2048),
    "entity_groups": ("group_id", {
        "alias_policy", "aliases", "display_name", "entity", "expansion",
        "group_id", "legacy_identity", "members", "selection",
        "target_field",
    }, 2048),
    "grains": ("grain_id", {"display_fields", "grain_id", "keys"}, 2048),
    "orderings": ("ordering_id", {"items", "keys", "ordering_id"}, 2048),
    "predicates": ("predicate_id", {
        "aliases", "allowed_operators", "grain_id", "group_id",
        "predicate", "predicate_id",
    }, 2048),
    "recipes": ("recipe_id", {
        "aliases", "datasets", "default_operation_template",
        "derived_metrics", "grain", "metrics", "recipe_id",
        "required_fields", "required_slots",
    }, 2048),
}
_SEMANTIC_TEMPLATE_LEGACY_ALIAS_TYPES = {
    "dataset", "field", "metric", "process_group", "process",
    "product_group", "recipe", "status",
}
_SEMANTIC_TEMPLATE_GENERIC_ALIAS_TYPES = {
    "dataset", "field", "metric", "relation", "grain", "predicate",
    "recipe", "entity_group",
}
_SEMANTIC_TEMPLATE_LEGACY_RECIPE_OPS = {
    "filter", "ordered_range", "product_token_match", "project", "derive",
    "aggregate", "compare_fields", "compare_group_attributes",
    "find_duplicate_groups", "join", "presence_filter", "sort", "rank",
    "concat_segments", "transform_previous_result",
}
_SEMANTIC_TEMPLATE_GENERIC_RECIPE_OPS = {
    "filter", "project", "aggregate", "join", "derive", "compare_fields",
    "sort", "rank", "transform_previous_result",
}

_DATASET_TEMPLATE_KEYS = {
    "date_filter_contract", "date_policy", "default_detail_fields",
    "display_name", "fixture_only", "parameters", "read_policy",
    "time_scope", "upstream_bindings",
}
_DATASET_TEMPLATE_REQUIRED_KEYS = {
    "date_policy", "default_detail_fields", "display_name", "parameters",
    "read_policy", "time_scope",
}


def _semantic_sha256_json(value):
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _validated_dataset_template(
    dataset_id, value, declared_sha256, approved_field_ids
):
    if (
        not isinstance(value, dict)
        or not _DATASET_TEMPLATE_REQUIRED_KEYS <= set(value) <= _DATASET_TEMPLATE_KEYS
        or not re.fullmatch(r"[0-9a-f]{64}", str(declared_sha256 or ""))
        or _semantic_sha256_json(value) != declared_sha256
    ):
        raise ValueError("Approved dataset template contract or hash is invalid.")
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    if not encoded or len(encoded) > 32 * 1024:
        raise ValueError("Approved dataset template exceeds the bounded payload size.")

    forbidden_keys = {
        "code", "source", "source_code", "module", "module_path",
        "import_path", "python", "sql", "url", "uri", "credential",
        "secret", "password", "token", "api_key", "config_ref", "query_ref",
        "source_type", "source_adapter", "fields", "family",
    }
    forbidden_values = (
        "http://", "https://", "mongodb://", "mongodb+srv://", "select ",
        "insert ", "update ", "delete ", "import ", "e" + "xec(", "e" + "val(",
        "password", "secret", "token=", "api_key",
    )

    def visit(current, depth=0):
        if depth > 20:
            raise ValueError("Approved dataset template nesting is too deep.")
        if isinstance(current, dict):
            if len(current) > 512:
                raise ValueError("Approved dataset template object is too large.")
            for raw_key, child in current.items():
                key = str(raw_key or "").strip()
                if (
                    not key
                    or len(key) > 256
                    or key.casefold() in forbidden_keys
                ):
                    raise ValueError("Approved dataset template contains a forbidden key.")
                visit(child, depth + 1)
            return
        if isinstance(current, list):
            if len(current) > 4096:
                raise ValueError("Approved dataset template list is too large.")
            for child in current:
                visit(child, depth + 1)
            return
        if isinstance(current, str):
            folded = current.casefold()
            if (
                not current.strip()
                or len(current) > 4096
                or any(marker in folded for marker in forbidden_values)
            ):
                raise ValueError("Approved dataset template contains a forbidden value.")
            return
        if current is None or isinstance(current, (bool, int)):
            return
        if isinstance(current, float) and math.isfinite(current):
            return
        raise ValueError("Approved dataset template contains a non-JSON value.")

    visit(value)
    approved_fields = {str(item) for item in approved_field_ids or ()}
    detail_fields = value.get("default_detail_fields")
    read_policy = value.get("read_policy")
    if (
        not isinstance(detail_fields, list)
        or len(detail_fields) > 128
        or len(detail_fields) != len(set(detail_fields))
        or any(item not in approved_fields for item in detail_fields)
        or not isinstance(value.get("display_name"), str)
        or not 1 <= len(value["display_name"]) <= 200
        or not isinstance(value.get("time_scope"), str)
        or not 1 <= len(value["time_scope"]) <= 64
        or not isinstance(value.get("parameters"), dict)
        or len(value["parameters"]) > 128
        or not isinstance(value.get("date_policy"), dict)
        or len(value["date_policy"]) > 32
        or not isinstance(read_policy, dict)
        or set(read_policy) - {"read_only", "timeout_seconds", "max_rows"}
        or read_policy.get("read_only") is not True
        or isinstance(read_policy.get("timeout_seconds"), bool)
        or not isinstance(read_policy.get("timeout_seconds"), int)
        or not 1 <= read_policy["timeout_seconds"] <= 120
        or isinstance(read_policy.get("max_rows"), bool)
        or not isinstance(read_policy.get("max_rows"), int)
        or not 1 <= read_policy["max_rows"] <= 1_000_000
    ):
        raise ValueError("Approved dataset template policies are invalid.")
    if "date_filter_contract" in value and (
        not isinstance(value["date_filter_contract"], dict)
        or len(value["date_filter_contract"]) > 32
    ):
        raise ValueError("Approved dataset template date filter is invalid.")
    if "fixture_only" in value and not isinstance(value["fixture_only"], bool):
        raise ValueError("Approved dataset template fixture policy is invalid.")
    if "upstream_bindings" in value and (
        not isinstance(value["upstream_bindings"], list)
        or len(value["upstream_bindings"]) > 64
        or any(not isinstance(card, dict) for card in value["upstream_bindings"])
    ):
        raise ValueError("Approved dataset template upstream bindings are invalid.")
    return deepcopy(value)


def _validated_semantic_templates(value, semantic_vocabulary):
    expected_root = {
        "contract_version", "locale", "timezone", "planner_policy",
        *_SEMANTIC_TEMPLATE_SECTIONS,
        "aliases",
    }
    if not isinstance(value, dict) or set(value) != expected_root:
        raise ValueError("Approved semantic templates root contract is invalid.")
    if value.get("contract_version") != "metadata.authoring.semantic-templates.v1":
        raise ValueError("Approved semantic templates version is invalid.")
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    if not encoded or len(encoded) > 128 * 1024:
        raise ValueError("Approved semantic templates exceed the bounded payload size.")
    locale = value.get("locale")
    timezone = value.get("timezone")
    if (
        not isinstance(locale, str)
        or not 1 <= len(locale) <= 64
        or not isinstance(timezone, str)
        or not 1 <= len(timezone) <= 128
    ):
        raise ValueError("Approved semantic template locale or timezone is invalid.")
    planner_policy = value.get("planner_policy")
    if not isinstance(planner_policy, dict):
        raise ValueError("Approved semantic template planner policy is invalid.")
    planner_profile = planner_policy.get("planner_profile")
    if planner_profile == "generic_v2":
        if set(planner_policy) != {"planner_profile"}:
            raise ValueError("Generic planner policy contains an unknown key.")
    elif planner_profile == "legacy_v1_compat":
        if (
            set(planner_policy) != {
                "planner_profile", "legacy_catalog_sha256"
            }
            or not re.fullmatch(
                r"[0-9a-f]{64}",
                str(planner_policy.get("legacy_catalog_sha256") or ""),
            )
        ):
            raise ValueError("Legacy planner policy pin is invalid.")
    else:
        raise ValueError("Approved semantic template planner profile is invalid.")

    forbidden_keys = {
        "source_type", "source_adapter", "config_ref", "query_ref",
        "physical_column", "physical_aliases", "coercion", "credential",
        "credentials", "password", "secret", "api_key", "token", "code",
        "python", "script", "sql",
    }
    forbidden_values = (
        "http://", "https://", "mongodb://", "mongodb+srv://", "select ",
        "insert ", "update ", "delete ", "import pandas", "def ", "lambda ",
        "api_key", "password", "secret", "token=",
    )

    forbidden_value_patterns = (
        re.compile(r"(?:https?|mongodb(?:\+srv)?|jdbc)://", re.IGNORECASE),
        re.compile(
            r"\b(?:select\s+.+\s+from|insert\s+into|delete\s+from|update\s+.+\s+set)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:import\s+[A-Za-z_]|from\s+[A-Za-z_][A-Za-z0-9_.]*\s+import|def\s+[A-Za-z_]\w*\s*\(|lambda\s+)"
        ),
    )

    def validate_safe_json(current, path=()):
        if len(path) > 24:
            raise ValueError("Approved semantic templates exceed the nesting depth limit.")
        if isinstance(current, dict):
            if len(current) > 8192 or any(
                str(key).casefold() in forbidden_keys for key in current
            ):
                raise ValueError("Approved semantic templates contain a forbidden execution key.")
            for key, child in current.items():
                if not isinstance(key, str) or not key or len(key) > 256:
                    raise ValueError("Approved semantic template key is invalid.")
                validate_safe_json(child, (*path, key))
            return
        if isinstance(current, list):
            if len(current) > 8192:
                raise ValueError("Approved semantic template array is too large.")
            for index, child in enumerate(current):
                validate_safe_json(child, (*path, str(index)))
            return
        if current is None or isinstance(current, (bool, int, float)):
            return
        if isinstance(current, str):
            folded = current.casefold()
            if (
                not current
                or len(current) > 4096
                or any(fragment in folded for fragment in forbidden_values)
                or any(pattern.search(current) for pattern in forbidden_value_patterns)
            ):
                raise ValueError("Approved semantic templates contain a forbidden execution value.")
            return
        raise ValueError("Approved semantic templates contain a non-JSON value.")

    vocabulary_ids = {
        section: {
            str(card["id"])
            for card in (semantic_vocabulary or {}).get(section) or []
            if isinstance(card, dict) and isinstance(card.get("id"), str)
        }
        for section in _SEMANTIC_TEMPLATE_SECTIONS
    }
    normalized = {
        "contract_version": "metadata.authoring.semantic-templates.v1",
        "locale": locale,
        "timezone": timezone,
        "planner_policy": deepcopy(planner_policy),
    }
    for section in _SEMANTIC_TEMPLATE_SECTIONS:
        cards = value.get(section)
        identity_key, allowed_keys, section_limit = _SEMANTIC_TEMPLATE_SPECS[section]
        if (
            not isinstance(cards, dict)
            or len(cards) > min(
                _SEMANTIC_VOCABULARY_LIMITS[section][1], section_limit
            )
            or set(cards) != vocabulary_ids[section]
        ):
            raise ValueError(
                f"Approved semantic template {section} IDs do not match the vocabulary."
            )
        for item_id, card in cards.items():
            if (
                not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,127}", str(item_id))
                or not isinstance(card, dict)
                or identity_key in card
                or not set(card).issubset(allowed_keys - {identity_key})
            ):
                raise ValueError(
                    f"Approved semantic template {section} card is open or invalid."
                )
        validate_safe_json(cards, (section,))
        normalized[section] = {
            str(item_id): cards[item_id] for item_id in sorted(cards)
        }

    registered_families = {
        str(card.get("family") or "")
        for card in (semantic_vocabulary or {}).get("datasets") or []
        if isinstance(card, dict)
    }
    field_families = {
        str(card.get("id") or ""): set(card.get("families") or [])
        for card in (semantic_vocabulary or {}).get("fields") or []
        if isinstance(card, dict)
    }
    for metric in normalized["metrics"].values():
        binding = metric.get("source_binding")
        if binding is None:
            continue
        if (
            not isinstance(binding, dict)
            or not {"dataset_family", "field"}.issubset(binding)
            or not set(binding).issubset(
                {"dataset_family", "field", "fixed_filters"}
            )
        ):
            raise ValueError("Approved metric source binding is open or incomplete.")
        family = str(binding.get("dataset_family") or "")
        field_id = str(binding.get("field") or "")
        if (
            family not in registered_families
            or family not in field_families.get(field_id, set())
        ):
            raise ValueError("Approved metric source binding is not registered.")
        fixed_filters = binding.get("fixed_filters", [])
        if not isinstance(fixed_filters, list) or len(fixed_filters) > 64:
            raise ValueError("Approved metric fixed filters are invalid.")
        for fixed_filter in fixed_filters:
            if (
                not isinstance(fixed_filter, dict)
                or set(fixed_filter)
                != {"field", "operator", "semantic_type", "value"}
                or family
                not in field_families.get(
                    str(fixed_filter.get("field") or ""), set()
                )
            ):
                raise ValueError("Approved metric fixed filter is not registered.")

    def recipe_operations(current):
        operations = set()
        if isinstance(current, dict):
            operation = current.get("op")
            if isinstance(operation, str) and operation:
                operations.add(operation)
            for child in current.values():
                operations.update(recipe_operations(child))
        elif isinstance(current, list):
            for child in current:
                operations.update(recipe_operations(child))
        return operations

    allowed_recipe_ops = (
        _SEMANTIC_TEMPLATE_LEGACY_RECIPE_OPS
        if planner_profile == "legacy_v1_compat"
        else _SEMANTIC_TEMPLATE_GENERIC_RECIPE_OPS
    )
    for recipe in normalized["recipes"].values():
        if not recipe_operations(
            recipe.get("default_operation_template")
        ).issubset(allowed_recipe_ops):
            raise ValueError("Approved recipe is incompatible with the planner policy.")
    aliases = value.get("aliases")
    if not isinstance(aliases, dict) or not 1 <= len(aliases) <= 8192:
        raise ValueError("Approved semantic template aliases are invalid.")
    target_ids = {
        "dataset": {
            str(card.get("id") or "")
            for card in (semantic_vocabulary or {}).get("datasets") or []
            if isinstance(card, dict)
        },
        "field": set(field_families),
        "metric": set(normalized["metrics"]),
        "relation": set(normalized["relations"]),
        "grain": set(normalized["grains"]),
        "predicate": set(normalized["predicates"]),
        "recipe": set(normalized["recipes"]),
        "entity_group": set(normalized["entity_groups"]),
        "process_group": set(normalized["entity_groups"]),
        "product_group": set(normalized["predicates"]),
    }
    process_targets = set()
    for ordering in normalized["orderings"].values():
        for item in ordering.get("items") or []:
            if isinstance(item, dict) and isinstance(item.get("oper_name"), str):
                process_targets.add(item["oper_name"])
    target_ids["process"] = process_targets
    allowed_alias_types = (
        _SEMANTIC_TEMPLATE_LEGACY_ALIAS_TYPES
        if planner_profile == "legacy_v1_compat"
        else _SEMANTIC_TEMPLATE_GENERIC_ALIAS_TYPES
    )
    for alias_id, card in aliases.items():
        if (
            not isinstance(alias_id, str)
            or not alias_id
            or len(alias_id) > 256
            or not isinstance(card, dict)
            or set(card) != {
                "target_type", "target_key", "values", "normalization",
                "match", "conflict", "provenance_source",
            }
        ):
            raise ValueError("Approved semantic template alias card is invalid.")
        target_type = str(card.get("target_type") or "")
        target_key = str(card.get("target_key") or "")
        normalization = card.get("normalization")
        values = card.get("values")
        if (
            alias_id != f"{target_type}:{target_key}"
            or target_type not in allowed_alias_types
            or (
                target_type != "status"
                and target_key not in target_ids.get(target_type, set())
            )
            or not isinstance(normalization, list)
            or not 1 <= len(normalization) <= 16
            or len(normalization) != len(set(normalization))
            or any(
                not isinstance(item, str)
                or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", item)
                for item in normalization
            )
            or any(
                not isinstance(card.get(key), str)
                or not card.get(key)
                or len(card.get(key)) > 128
                for key in ("match", "conflict", "provenance_source")
            )
            or not isinstance(values, list)
            or not 1 <= len(values) <= 128
        ):
            raise ValueError("Approved semantic template alias policy is invalid.")
        for alias_value in values:
            if (
                not isinstance(alias_value, dict)
                or set(alias_value) != {"text", "priority"}
                or not isinstance(alias_value.get("text"), str)
                or not alias_value.get("text")
                or len(alias_value.get("text")) > 256
                or isinstance(alias_value.get("priority"), bool)
                or not isinstance(alias_value.get("priority"), int)
                or not 0 <= alias_value.get("priority") <= 1_000_000
            ):
                raise ValueError("Approved semantic template alias value is invalid.")
    validate_safe_json(aliases, ("aliases",))
    normalized["aliases"] = {
        str(alias_id): aliases[alias_id] for alias_id in sorted(aliases)
    }
    return normalized



import hashlib
import json
import re
import unicodedata
from copy import deepcopy

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, DropdownInput, MessageInput, MultilineInput, Output, StrInput
from lfx.schema.data import Data


def _authoring_schema_refs(value):
    refs = set()
    if isinstance(value, dict):
        raw_ref = value.get("$ref")
        prefix = "#/$defs/"
        if isinstance(raw_ref, str) and raw_ref.startswith(prefix):
            refs.add(raw_ref[len(prefix) :])
        for child in value.values():
            refs.update(_authoring_schema_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_authoring_schema_refs(child))
    return refs


def _authoring_reachable_defs(properties, available_defs):
    pending = set(_authoring_schema_refs(properties))
    selected = {}
    while pending:
        name = sorted(pending)[0]
        pending.remove(name)
        if name in selected:
            continue
        definition = available_defs.get(name)
        if not isinstance(definition, dict):
            raise ContractError("metadata_schema_error", "metadata_prompt_context", "Schema definition reference is missing.", {"definition": name})
        selected[name] = deepcopy(definition)
        pending.update(_authoring_schema_refs(definition) - set(selected))
    return {name: selected[name] for name in sorted(selected)}


def _authoring_partial_schema(value):
    if isinstance(value, list):
        return [_authoring_partial_schema(child) for child in value]
    if not isinstance(value, dict):
        return deepcopy(value)
    result = {key: _authoring_partial_schema(child) for key, child in value.items() if key != "required"}
    raw_type = result.get("type")
    if raw_type == "object" or (isinstance(raw_type, list) and "object" in raw_type):
        current_min = result.get("minProperties")
        result["minProperties"] = max(1, int(current_min) if isinstance(current_min, int) else 0)
    return result


def _authoring_output_schema(
    kind,
    *,
    annotation_only=False,
    proposal_source_sha256="",
    bootstrap_fragment=False,
    approved_dataset_ids=(),
    approved_dataset_field_ids=None,
    approved_semantic_vocabulary=None,
):
    if kind == "domain" and annotation_only:
        return load_schema("metadata-annotation-proposal.schema.json")
    full_schema = load_schema("metadata-authoring-draft.schema.json")
    if kind == "domain" and not bootstrap_fragment:
        draft_schema = full_schema
    elif kind == "domain" and bootstrap_fragment:
        # Executable semantic cards are compiler-owned templates from the
        # approved registry. The LLM only annotates the worker's prose.
        draft_schema = load_schema("metadata-annotation-proposal.schema.json")
    elif kind == "dataset":
        # The worker still writes unrestricted natural language.  Only the
        # internal LLM-facing representation is compact so a large field
        # catalog does not consume the provider's output ceiling.  The engine
        # expands this closed IR before the full authoring/compiler gates.
        draft_schema = load_schema("metadata-bootstrap-dataset-ir.schema.json")
    elif kind == "main_filter":
        # The provider returns a closed list rather than a dynamic aliases map.
        # Requiring target_type removes ambiguity when a field and metric share
        # the same canonical ID. The engine expands this IR into alias cards.
        draft_schema = load_schema("metadata-bootstrap-main-filter-ir.schema.json")
        if approved_semantic_vocabulary is not None:
            draft_schema = _apply_main_filter_ir_allowlists(
                draft_schema,
                approved_semantic_vocabulary,
            )
    else:
        sections = (
            {
                "domain": (
                    "display_name", "description", "locale", "timezone",
                    "metrics", "relations", "aliases", "entity_groups", "grains",
                    "orderings", "predicates", "recipes",
                ),
                "dataset": ("datasets", "aliases"),
                "main_filter": ("aliases",),
            }.get(kind)
            if bootstrap_fragment
            else {
                "dataset": ("datasets",),
                "main_filter": ("aliases", "entity_groups", "grains", "orderings", "predicates", "recipes"),
            }.get(kind)
        )
        if sections is None:
            return {}
        owned = {section: deepcopy(full_schema["properties"][section]) for section in sections}
        draft_schema = {
            "$schema": full_schema.get("$schema"),
            "title": f"metadata.authoring.{kind}.section-patch.v1",
            "type": "object",
            "additionalProperties": False,
            "minProperties": 1,
            "maxProperties": len(sections),
            "properties": (
                deepcopy(owned)
                if bootstrap_fragment
                else _authoring_partial_schema(owned)
            ),
            "$defs": (
                _authoring_reachable_defs(owned, full_schema.get("$defs") or {})
                if bootstrap_fragment
                else _authoring_partial_schema(
                    _authoring_reachable_defs(owned, full_schema.get("$defs") or {})
                )
            ),
        }
        if kind == "domain" and bootstrap_fragment:
            draft_schema["required"] = ["display_name"]
        elif kind == "dataset":
            draft_schema["required"] = ["datasets"]
        elif kind == "main_filter" and bootstrap_fragment:
            draft_schema["required"] = ["aliases"]

    approved_ids = sorted(
        {
            str(item).strip()
            for item in (approved_dataset_ids or ())
            if str(item).strip()
        }
    )
    if kind == "dataset" and approved_ids:
        if "datasetCard" in (draft_schema.get("$defs") or {}):
            field_allowlists = {
                dataset_id: sorted(
                    {
                        str(field_id).strip()
                        for field_id in (
                            (approved_dataset_field_ids or {}).get(dataset_id) or []
                        )
                        if str(field_id).strip()
                    }
                )
                for dataset_id in approved_ids
            }
            if any(not field_ids for field_ids in field_allowlists.values()):
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_prompt_context",
                    "승인 dataset별 field allowlist가 비어 있습니다.",
                )
            base_dataset_card = deepcopy(draft_schema["$defs"]["datasetCard"])
            base_field_card = deepcopy(draft_schema["$defs"]["fieldCard"])
            dataset_branches = []
            for dataset_id in approved_ids:
                allowed_fields = field_allowlists[dataset_id]
                dataset_card = deepcopy(base_dataset_card)
                dataset_card["properties"]["dataset_id"] = {
                    "type": "string",
                    "enum": [dataset_id],
                }
                field_card = deepcopy(base_field_card)
                field_card["properties"]["id"] = {
                    "type": "string",
                    "enum": allowed_fields,
                }
                field_card["properties"]["col"] = {
                    "type": "string",
                    "enum": allowed_fields,
                }
                dataset_card["properties"]["fields"]["items"] = field_card
                dataset_branches.append(dataset_card)
            draft_schema["$defs"]["datasetCard"] = {
                "oneOf": dataset_branches
            }
        else:
            draft_schema["properties"]["datasets"]["propertyNames"] = {
                "enum": approved_ids
            }

    source_sha256 = str(proposal_source_sha256 or "").strip()
    if not source_sha256:
        return draft_schema
    proposal_schema = deepcopy(load_schema("metadata-authoring-proposal.schema.json"))
    for branch in proposal_schema.get("oneOf") or []:
        if not isinstance(branch, dict):
            continue
        properties = branch.get("properties")
        required = branch.get("required")
        if not isinstance(properties, dict) or not isinstance(required, list):
            continue
        properties["source_sha256"] = {
            "type": "string",
            "const": source_sha256,
            "description": "입력 원문의 결정론적 SHA-256. runtime_context 값을 그대로 복사합니다.",
        }
        if "source_sha256" not in required:
            required.append("source_sha256")
        status = ((properties.get("status") or {}).get("const"))
        if status == "complete":
            properties["draft"] = deepcopy(draft_schema)
    return proposal_schema


def _authoring_alias_only_manifest_patch(source_manifest):
    counts = source_manifest.get("counts") if isinstance(source_manifest, dict) else None
    inventories = source_manifest.get("inventories") if isinstance(source_manifest, dict) else None
    if not isinstance(counts, dict) or not isinstance(inventories, dict):
        return None
    non_alias_kinds = (
        "datasets", "fields", "field_bindings", "field_roles", "metrics", "grains",
        "grain_keys", "grain_display_fields", "relations", "relation_endpoints",
        "relation_keys", "relation_policies", "recipes", "operations",
    )
    if any(int(counts.get(item) or 0) != 0 for item in non_alias_kinds):
        return None
    bindings = inventories.get("alias_bindings")
    if int(counts.get("aliases") or 0) < 1 or not isinstance(bindings, list):
        return None
    aliases = {}
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"alias", "target"}:
            return None
        alias = binding.get("alias")
        target = binding.get("target")
        if not isinstance(alias, str) or not alias or not isinstance(target, str) or not target:
            return None
        if alias in aliases and aliases[alias] != target:
            return None
        aliases[alias] = target
    return {"aliases": {key: aliases[key] for key in sorted(aliases)}}


def _freeform_source_manifest(source_text):
    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    inventories = {
        "datasets": [], "dataset_fields": {}, "fields": [], "field_roles": {},
        "metrics": [], "grains": [], "grain_keys": {}, "grain_display_fields": {},
        "relations": [], "relation_endpoints": {}, "relation_keys": {},
        "relation_policies": {}, "recipes": [], "operations": [], "aliases": [],
        "alias_targets": [], "alias_bindings": [],
    }
    counts = {
        "datasets": 0, "fields": 0, "field_bindings": 0, "field_roles": 0,
        "metrics": 0, "grains": 0, "grain_keys": 0, "grain_display_fields": 0,
        "relations": 0, "relation_endpoints": 0, "relation_keys": 0,
        "relation_policies": 0, "recipes": 0, "operations": 0, "aliases": 0,
        "alias_targets": 0, "alias_bindings": 0,
    }
    material = {
        "contract_version": "metadata.authoring.source-manifest.v1",
        "source_sha256": source_sha256,
        "inventories": inventories,
        "required_sections": [],
        "counts": counts,
    }
    material["manifest_sha256"] = hashlib.sha256(
        json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return material


class AuthoringPromptContextBuilder(Component):
    display_name = "메타데이터 등록 프롬프트 컨텍스트"
    description = "자연어 TXT와 신뢰된 구조 정보를 제한된 데이터 컨텍스트로 만들며, 프롬프트 지시문과 LLM 호출은 외부 노드가 담당합니다."
    icon = "file-json-2"
    metadata = {"logical_stage": "authoring_prompt_context"}
    inputs = [
        MessageInput(name="input_message", display_name="자연어 메타데이터 TXT", required=True, info="비전문 작업자가 업무 정보를 자유 형식으로 작성한 TXT 원문입니다."),
        DataInput(name="approved_reference_context", display_name="승인 원천 참조 컨텍스트", required=False, info="LLM에는 승인 데이터셋 ID allowlist와 hash만 제공하고, 실행 참조는 엔진이 별도 입력에서 봉인하는 운영자 승인 정보입니다."),
        BoolInput(name="bootstrap_fragment", display_name="초기 등록 분할 제안", value=False, advanced=True, info="도메인 최초 등록에서 원문 종류별 작은 폐쇄형 조각만 제안해 모델 응답 크기를 제한합니다."),
        DropdownInput(name="authoring_kind", display_name="등록 유형", options=["domain", "dataset", "main_filter", "domain_policy"], value="domain", info="도메인, 데이터셋, 주요 필터, 관리자 정책 중 이번에 등록할 항목을 선택합니다."),
        DropdownInput(name="mode", display_name="저장 모드", options=["save", "replace", "validate_only"], value="save", info="save는 신규 key만 허용하고, replace는 동일 section+key를 교체하며, validate_only는 저장 없이 검증합니다."),
        DropdownInput(name="source_grounding_mode", display_name="자연어 입력 해석 방식", options=["freeform_llm", "explicit_inventory"], value="freeform_llm", advanced=True, info="일반 작업자 입력은 freeform_llm을 사용합니다. explicit_inventory는 관리자 검증 경로 전용입니다."),
        StrInput(name="domain_id", display_name="도메인 ID", value="default", info="등록 대상 업무 도메인의 고유 식별자입니다. 공유 시 대상 도메인 ID로 바꿉니다."),
        StrInput(name="environment", display_name="운영 환경", value="production", info="메타데이터 리비전을 구분할 운영 환경 이름입니다."),
        MultilineInput(name="trusted_blueprint_json", display_name="신뢰 실행 블루프린트 JSON", value="", required=False, advanced=True, info="관리자 전용 결정론적 등록 경로에서만 사용하는 검토 완료 블루프린트입니다."),
        StrInput(name="trusted_blueprint_sha256", display_name="블루프린트 SHA-256 고정값", value="", required=False, advanced=True, info="신뢰 실행 블루프린트가 변조되지 않았는지 확인할 SHA-256 값입니다."),
    ]
    outputs = [Output(name="authoring_prompt_context", display_name="등록 LLM 실행 컨텍스트", method="build_context", types=["Data"])]

    def build_context(self) -> Data:
        kind = str(getattr(self, "authoring_kind", "domain") or "domain").strip()
        mode = str(getattr(self, "mode", "save") or "save").strip()
        # Read-only compatibility for older test/API callers.  The canvas no
        # longer exposes prepare and this alias never creates pending state.
        if mode == "prepare":
            mode = "validate_only"
        if kind not in {"domain", "dataset", "main_filter", "domain_policy"} or mode not in {"save", "replace", "validate_only"}:
            raise ContractError("metadata_schema_error", "metadata_prompt_context", "등록 유형 또는 실행 모드가 유효하지 않습니다.")
        source_text = str(getattr(getattr(self, "input_message", None), "text", getattr(self, "input_message", "")) or "").strip()
        if not source_text or len(source_text.encode("utf-8")) > 65536:
            raise ContractError("metadata_schema_error", "metadata_prompt_context", "메타데이터 TXT는 1~65536 UTF-8 바이트여야 합니다.")
        grounding_mode = str(getattr(self, "source_grounding_mode", "freeform_llm") or "freeform_llm").strip()
        if grounding_mode not in {"freeform_llm", "explicit_inventory"}:
            raise ContractError("metadata_schema_error", "metadata_prompt_context", "자연어 입력 해석 방식이 유효하지 않습니다.")
        blueprint_text = str(getattr(self, "trusted_blueprint_json", "") or "").strip()
        blueprint_pin = str(getattr(self, "trusted_blueprint_sha256", "") or "").strip()
        if kind == "domain" and bool(blueprint_text) != bool(blueprint_pin):
            raise ContractError("metadata_blueprint_invalid", "metadata_prompt_context", "블루프린트 JSON과 SHA-256 핀은 함께 설정해야 합니다.")
        annotation_only = kind == "domain" and bool(blueprint_text) and bool(blueprint_pin)
        bootstrap_fragment = bool(getattr(self, "bootstrap_fragment", False))
        if bootstrap_fragment and (annotation_only or kind == "domain_policy"):
            raise ContractError("metadata_policy_error", "metadata_prompt_context", "초기 등록 분할 제안은 자유형 domain/dataset/main_filter 등록에서만 사용할 수 있습니다.")
        strict_inventory = grounding_mode == "explicit_inventory" or annotation_only
        source_manifest = (
            extract_authoring_source_manifest(source_text)
            if strict_inventory
            else _freeform_source_manifest(source_text)
        )
        raw_reference = getattr(self, "approved_reference_context", None)
        reference_context = getattr(raw_reference, "data", raw_reference)
        if reference_context in (None, {}, ""):
            reference_context = {}
        if not isinstance(reference_context, dict):
            raise ContractError("metadata_dependency_error", "metadata_prompt_context", "승인 Source 참조 컨텍스트가 Data 객체가 아닙니다.")
        if reference_context:
            if set(reference_context) != {
                "contract_version", "domain_id", "bindings", "dataset_descriptors",
                "semantic_vocabulary", "semantic_templates",
                "semantic_templates_sha256",
                "semantic_templates_blueprint_sha256",
                "semantic_templates_executable_sha256",
                "semantic_templates_projection_sha256", "registry_sha256",
            }:
                raise ContractError("metadata_dependency_error", "metadata_prompt_context", "승인 Source 참조 컨텍스트 root 계약이 닫혀 있지 않습니다.")
            reference_material = {
                "contract_version": reference_context.get("contract_version"),
                "domain_id": reference_context.get("domain_id"),
                "bindings": reference_context.get("bindings"),
                "dataset_descriptors": reference_context.get("dataset_descriptors"),
                "semantic_vocabulary": reference_context.get("semantic_vocabulary"),
                "semantic_templates": reference_context.get("semantic_templates"),
                "semantic_templates_sha256": reference_context.get("semantic_templates_sha256"),
                "semantic_templates_blueprint_sha256": reference_context.get("semantic_templates_blueprint_sha256"),
                "semantic_templates_executable_sha256": reference_context.get("semantic_templates_executable_sha256"),
                "semantic_templates_projection_sha256": reference_context.get("semantic_templates_projection_sha256"),
            }
            expected_registry_sha256 = hashlib.sha256(
                json.dumps(reference_material, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
            ).hexdigest()
            try:
                dataset_families, field_families = _semantic_maps_from_descriptors(
                    reference_context.get("dataset_descriptors")
                )
                semantic_vocabulary = _validated_semantic_vocabulary(
                    reference_context.get("semantic_vocabulary"),
                    expected_dataset_families=dataset_families,
                    expected_field_families=field_families,
                )
                semantic_templates = _validated_semantic_templates(
                    reference_context.get("semantic_templates"),
                    semantic_vocabulary,
                )
            except ValueError as exc:
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_prompt_context",
                    "승인 축약 의미 어휘가 유효하지 않습니다.",
                ) from exc
            if (
                reference_context.get("contract_version") != "metadata.authoring.source-registry-context.v3"
                or reference_context.get("domain_id") != str(getattr(self, "domain_id", "") or "").strip()
                or not isinstance(reference_context.get("bindings"), dict)
                or not isinstance(reference_context.get("dataset_descriptors"), dict)
                or set(reference_context.get("bindings") or {}) != set(reference_context.get("dataset_descriptors") or {})
                or reference_context.get("semantic_vocabulary") != semantic_vocabulary
                or reference_context.get("semantic_templates") != semantic_templates
                or reference_context.get("semantic_templates_sha256")
                != hashlib.sha256(
                    json.dumps(semantic_templates, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
                ).hexdigest()
                or any(
                    not re.fullmatch(r"[0-9a-f]{64}", str(reference_context.get(key) or ""))
                    for key in (
                        "semantic_templates_blueprint_sha256",
                        "semantic_templates_executable_sha256",
                        "semantic_templates_projection_sha256",
                    )
                )
                or reference_context.get("registry_sha256") != expected_registry_sha256
            ):
                raise ContractError("metadata_dependency_error", "metadata_prompt_context", "승인 Source 참조 컨텍스트 hash 또는 도메인 결합이 유효하지 않습니다.")
        if bootstrap_fragment and not reference_context:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_prompt_context",
                "분할 초기 등록에는 승인 축약 의미 어휘가 필요합니다.",
            )
        invoke = kind in {"domain", "dataset"}
        if kind == "main_filter" and strict_inventory:
            invoke = _authoring_alias_only_manifest_patch(source_manifest) is None
        elif kind == "main_filter":
            invoke = True
        purpose = {
            "domain": "metadata_domain_annotation" if annotation_only else "metadata_domain_draft",
            "dataset": "metadata_dataset_draft",
            "main_filter": "metadata_main_filter_draft",
            "domain_policy": "metadata_domain_policy",
        }[kind]
        variables = {
            "authoring_kind": kind,
            "domain_id": str(getattr(self, "domain_id", "") or "").strip(),
            "environment": str(getattr(self, "environment", "") or "").strip(),
            "source_grounding_mode": grounding_mode,
            "source_text": source_text,
            "source_sha256": str(source_manifest.get("source_sha256") or ""),
            "source_manifest": source_manifest,
            "bootstrap_fragment": bootstrap_fragment,
        }
        approved_dataset_ids = sorted(
            str(card["id"])
            for card in ((reference_context.get("semantic_vocabulary") or {}).get("datasets") or [])
        )
        if reference_context and kind in {"domain", "dataset", "main_filter"}:
            variables["approved_semantic_vocabulary"] = deepcopy(
                reference_context["semantic_vocabulary"]
            )
            variables["source_registry_sha256"] = str(reference_context.get("registry_sha256") or "")
        if invoke:
            variables["output_schema"] = _authoring_output_schema(
                kind,
                annotation_only=annotation_only,
                bootstrap_fragment=bootstrap_fragment,
                approved_dataset_ids=approved_dataset_ids,
                approved_dataset_field_ids=(
                    _dataset_field_allowlists_from_vocabulary(
                        semantic_vocabulary,
                        reference_context.get("dataset_descriptors"),
                    )
                    if reference_context and kind == "dataset"
                    else None
                ),
                approved_semantic_vocabulary=(
                    semantic_vocabulary if reference_context else None
                ),
                proposal_source_sha256=(
                    str(source_manifest.get("source_sha256") or "")
                    if grounding_mode == "freeform_llm" and not annotation_only
                    else ""
                ),
            )
        if annotation_only:
            try:
                parsed = json.loads(blueprint_text)
            except json.JSONDecodeError as exc:
                raise ContractError("metadata_blueprint_invalid", "metadata_prompt_context", "블루프린트 JSON이 유효하지 않습니다.", {"line": exc.lineno}) from exc
            trusted = validate_executable_blueprint(
                parsed,
                expected_blueprint_sha256=blueprint_pin,
                expected_domain_id=variables["domain_id"],
                expected_environment=variables["environment"],
                source_manifest=source_manifest,
            )
            variables["default_annotations"] = trusted["default_annotations"]
            variables["blueprint_sha256"] = trusted["blueprint_sha256"]
        encoded = json.dumps(variables, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(encoded) > 192 * 1024:
            raise ContractError("metadata_budget_exceeded", "metadata_prompt_context", "등록 LLM 컨텍스트가 192KB를 초과했습니다.")
        return Data(data={"contract_version": "prompt.runtime-context.v1", "purpose": purpose, "invoke": bool(invoke), "variables": variables})
