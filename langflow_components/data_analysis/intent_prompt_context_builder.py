# -*- coding: utf-8 -*-
"""GENERATED standalone component: IntentPromptContextBuilder.

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
from lfx.io import DataInput, Output
from lfx.schema.data import Data


class IntentPromptContextBuilder(Component):
    display_name = "04 의도 분석 런타임 컨텍스트 구성"
    description = "등록 후보와 질문만 bounded runtime context로 만들며 프롬프트 본문은 외부 Prompt Template 노드가 소유합니다."
    icon = "braces"
    metadata = {"logical_stage": "intent_prompt_context"}
    inputs = [DataInput(name="selection_context", display_name="후보 및 분기 컨텍스트", required=True, info="결정론적으로 계산된 의도 후보와 LLM 호출 필요 여부가 담긴 컨텍스트입니다.")]
    outputs = [Output(name="intent_prompt_context", display_name="의도 분석 실행 컨텍스트", method="build_context", types=["Data"])]

    def _selection(self):
        current = _require_context(getattr(self, "selection_context", None), "intent_prompt_context")
        return current

    def build_context(self) -> Data:
        current = self._selection()
        route = (current.get("candidate_bundle") or {}).get("route_decision") or {}
        route_name = str(route.get("route") or "")
        variables = (
            {
                "question": str((current.get("request") or {}).get("question") or ""),
                "candidate_cards": list((current.get("candidate_bundle") or {}).get("prompt_cards") or []),
                "route_reason": str(route.get("reason_code") or ""),
            }
            if current.get("ok")
            else {"upstream_error_code": str((current.get("error") or {}).get("code") or "pipeline_error")}
        )
        encoded = json.dumps(variables, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(encoded) > 28 * 1024:
            raise ContractError("metadata_budget_exceeded", "intent_prompt_context", "의도 분석 runtime context가 28KB를 초과했습니다.")
        return Data(
            data={
                "contract_version": "prompt.runtime-context.v1",
                "purpose": "intent_selection",
                "invoke": bool(current.get("ok")) and route_name == "intent_llm",
                "variables": variables,
            }
        )
