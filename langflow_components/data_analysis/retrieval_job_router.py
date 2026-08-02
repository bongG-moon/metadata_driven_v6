# -*- coding: utf-8 -*-
"""GENERATED standalone component: RetrievalJobRouter.

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
from lfx.io import DataInput, DropdownInput, Output
from lfx.schema.data import Data


class RetrievalJobRouter(Component):
    display_name = "10 데이터 조회 작업 라우터"
    description = "실행 계획의 최소 조회 작업을 더미·Oracle·H-API·Datalake·Goodocs 전용 출력으로 분리합니다."
    icon = "split"
    metadata = {"logical_stage": "job_routing"}
    inputs = [
        DataInput(name="plan_context", display_name="검증된 실행 계획 컨텍스트", required=True, info="데이터 조회 작업이 포함된 검증 완료 Typed Execution IR입니다."),
        DropdownInput(name="data_mode", display_name="데이터 조회 방식", options=["dummy", "live"], value="dummy", info="검증용 더미 데이터 또는 원천별 실데이터 조회 경로를 선택합니다."),
    ]
    outputs = [
        Output(name="dummy_jobs", display_name="더미 조회 작업", method="dummy_jobs_out", types=["Data"], group_outputs=True),
        Output(name="oracle_jobs", display_name="Oracle 조회 작업", method="oracle_jobs_out", types=["Data"], group_outputs=True),
        Output(name="h_api_jobs", display_name="H-API 조회 작업", method="h_api_jobs_out", types=["Data"], group_outputs=True),
        Output(name="datalake_jobs", display_name="Datalake 조회 작업", method="datalake_jobs_out", types=["Data"], group_outputs=True),
        Output(name="goodocs_jobs", display_name="Goodocs 조회 작업", method="goodocs_jobs_out", types=["Data"], group_outputs=True),
    ]

    def _routes_once(self):
        current = _payload(getattr(self, "plan_context", None))
        cache_key = id(getattr(self, "plan_context", None))
        if getattr(self, "_routes_cache_key", None) == cache_key:
            return self._routes_cache
        try:
            current = _require_context(current, "job_routing")
            if not current.get("ok"):
                routes = {name: current for name in ("dummy", "oracle", "h_api", "datalake", "goodocs")}
                self._routes_cache_key, self._routes_cache = cache_key, routes
                return routes
            mode = str(getattr(self, "data_mode", "dummy") or "dummy")
            jobs = deepcopy((current.get("plan") or {}).get("retrieval_jobs") or [])
            candidate_lane = str(current.get("candidate_lane") or "")
            if candidate_lane not in {"legacy_v1", "legacy_v1_compat", "generic_v2"}:
                raise ContractError(
                    "plan_contract_error",
                    "job_routing",
                    "A closed candidate lane is required before retrieval routing.",
                    {"candidate_lane": candidate_lane},
                )
            aliases = {
                "oracle": {"oracle", "sql"},
                "h_api": {"h_api", "http"},
                "datalake": {"datalake", "file", "mongodb"},
                "goodocs": {"goodocs"},
            }
            if mode == "live":
                unsupported = sorted(
                    {
                        str(job.get("source_type") or "")
                        for job in jobs
                        if not any(str(job.get("source_type") or "") in values for values in aliases.values())
                    }
                )
                if unsupported:
                    raise ContractError("source_contract_error", "job_routing", "지원하지 않는 실데이터 source type입니다.", {"source_types": unsupported})
            routes = {}
            for source_type in ("dummy", "oracle", "h_api", "datalake", "goodocs"):
                selected = (
                    jobs
                    if source_type == "dummy" and mode == "dummy"
                    else [job for job in jobs if mode == "live" and str(job.get("source_type") or "") in aliases.get(source_type, set())]
                )
                routes[source_type] = {
                    "contract_version": PIPELINE_VERSION,
                    "ok": True,
                    "stage": "job_routing",
                    "data_mode": mode,
                    "candidate_lane": candidate_lane,
                    "source_type": source_type,
                    "jobs": deepcopy(selected),
                }
        except Exception as exc:
            failed = _pipeline_error(current, exc, "job_routing")
            routes = {name: failed for name in ("dummy", "oracle", "h_api", "datalake", "goodocs")}
        self._routes_cache_key, self._routes_cache = cache_key, routes
        return routes

    def dummy_jobs_out(self) -> Data:
        return Data(data=self._routes_once()["dummy"])

    def oracle_jobs_out(self) -> Data:
        return Data(data=self._routes_once()["oracle"])

    def h_api_jobs_out(self) -> Data:
        return Data(data=self._routes_once()["h_api"])

    def datalake_jobs_out(self) -> Data:
        return Data(data=self._routes_once()["datalake"])

    def goodocs_jobs_out(self) -> Data:
        return Data(data=self._routes_once()["goodocs"])

    def route_jobs(self) -> Data:
        """Backward-compatible deterministic entrypoint for local harnesses."""
        routes = self._routes_once()
        mode = str(getattr(self, "data_mode", "dummy") or "dummy")
        return Data(data=routes["dummy"] if mode == "dummy" else {
            "contract_version": PIPELINE_VERSION,
            "ok": all(bool(item.get("ok")) for item in routes.values()),
            "stage": "job_routing",
            "data_mode": mode,
            "candidate_lane": next(iter(routes.values())).get("candidate_lane"),
            "jobs": [job for name in ("oracle", "h_api", "datalake", "goodocs") for job in routes[name].get("jobs", [])],
        })
