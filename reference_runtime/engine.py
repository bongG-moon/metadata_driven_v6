"""End-to-end trusted core orchestration used by tests and components."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from .canonical import ContractError, sha256_json
from .contracts import validate_contract
from .plan_compiler import (
    build_candidate_bundle,
    compile_plan,
    load_runtime_catalog,
    resolve_intent,
    validate_plan,
)
from .presenter import assemble_response, build_answer_facts, error_response
from .request_literals import build_request_capsule
from .state_contracts import InMemoryStateStore, StateStore, compact_next_state
from .typed_executor import TypedExecutor


class AnalysisEngine:
    """Fail-closed orchestration with no pandas-code or repair lane."""

    def __init__(
        self,
        *,
        catalog: dict[str, Any] | None = None,
        catalog_path: str | Path | None = None,
        source_adapter: Any = None,
        state_store: StateStore | None = None,
        max_executor_rows: int = 100_000,
        result_ttl_seconds: int = 3600,
        download_base_url: str = "",
        plan_compiler: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        self.catalog = deepcopy(catalog) if isinstance(catalog, dict) else load_runtime_catalog(catalog_path)
        self.source_adapter = source_adapter or self._default_source_adapter()
        self.state_store = state_store or InMemoryStateStore()
        self.executor = TypedExecutor(max_rows=max_executor_rows)
        self.result_ttl_seconds = int(result_ttl_seconds)
        self.download_base_url = str(download_base_url or "")
        self.plan_compiler = plan_compiler or compile_plan

    @staticmethod
    def _default_source_adapter() -> Any:
        from .dummy_data import source_results_for_jobs

        class _DummySourceAdapter:
            def retrieve(self, job: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
                return source_results_for_jobs([job], catalog)[0]

        return _DummySourceAdapter()

    def analyze(
        self,
        question: str,
        *,
        session_id: str = "default",
        subject_id: str = "anonymous",
        reference_instant: str | None = None,
        model: Any = None,
        llm_callable: Callable[[str], Any] | None = None,
        upstream_result_ref: str = "",
        data_mode: str = "dummy",
    ) -> dict[str, Any]:
        request: dict[str, Any] = {}
        route_telemetry: dict[str, Any] = {"intent_llm_calls": 0, "fallback_used": False}
        trace_id = ""
        event_offset = len(getattr(self.state_store, "events", []))
        try:
            prior_state = self.state_store.load_state(subject_id, session_id)
            prior_version = int(prior_state.get("state_version", 0)) if isinstance(prior_state, dict) else 0
            prior_ref = str(upstream_result_ref or (prior_state.get("executed_result_ref") if isinstance(prior_state, dict) else "") or "")
            prior_semantics = (((prior_state or {}).get("semantic_context") or {}).get("semantics") or {}) if isinstance(prior_state, dict) else {}
            prior_result: dict[str, Any] = {}
            if prior_ref:
                prior_record = self.state_store.load_ref(prior_ref, subject_id, session_id)
                prior_result = deepcopy(prior_record.get("payload") or {})
                prior_contract = str(prior_result.get("contract_version") or "")
                if prior_contract == "executed.result.v1":
                    validate_contract(prior_result, "executed-result.schema.json", stage="state_load")
                elif prior_contract == "analysis.result.v1":
                    # Compatibility for explicitly supplied refs created before
                    # the executed-result envelope was introduced.
                    validate_contract(prior_result, "analysis-result.schema.json", stage="state_load")
                else:
                    raise ContractError(
                        "state_reference_forbidden",
                        "state_load",
                        "후속 질문이 참조한 결과 계약을 사용할 수 없습니다.",
                        {"contract_version": prior_contract},
                    )
            request = build_request_capsule(
                question,
                session_id=session_id,
                subject_id=subject_id,
                reference_instant=reference_instant,
                previous_state_ref=prior_ref,
                upstream_result_ref=upstream_result_ref,
            )
            validate_contract(request, "request-capsule.schema.json", stage="request_contract")
            trace_id = f"trace:{sha256_json(request)[:24]}"
            bundle = build_candidate_bundle(
                request,
                self.catalog,
                prior_semantics=prior_semantics,
                prior_result=prior_result,
            )
            route_decision = bundle.get("route_decision") if isinstance(bundle.get("route_decision"), dict) else {}
            validate_contract(route_decision, "analysis-route.schema.json", stage="route_contract")
            route_telemetry = {
                "route": route_decision.get("route"),
                "reason_code": route_decision.get("reason_code"),
                "intent_llm_calls": 0,
                "fallback_used": False,
                "eligibility_proof_sha256": route_decision.get("eligibility_proof_sha256"),
            }
            intent, route_telemetry = resolve_intent(
                request,
                bundle,
                model=model,
                llm_callable=llm_callable,
            )
            validate_contract(intent, "semantic-intent.schema.json", stage="intent_contract")
            plan = validate_plan(self.plan_compiler(intent, bundle, self.catalog, prior_result=prior_result), self.catalog)
            validate_contract(plan, "analysis-plan.schema.json", stage="plan_contract")
            source_results: list[dict[str, Any]] = []
            for job in plan.get("retrieval_jobs", []):
                source_results.append(self._retrieve(job, data_mode))
            if source_results:
                frames, snapshots, diagnostics = self._merge_sources(plan, source_results)
            else:
                frames, snapshots, diagnostics = {}, [], []
            if "previous" in (plan.get("input_refs") or []):
                rows = prior_result.get("rows") if isinstance(prior_result.get("rows"), list) else []
                frames["previous"] = {"rows": deepcopy(rows)}
            execution = self.executor.execute(plan, frames)
            result = execution.as_contract(plan)
            validate_contract(result, "analysis-result.schema.json", stage="result_contract")
            facts = build_answer_facts(request, plan, result)
            next_state = compact_next_state(request, intent, plan, result)
            executed_result = self._executed_result(result, plan, snapshots)
            committed_state, result_ref, source_refs = self.state_store.commit_execution(
                subject_id=subject_id,
                session_id=session_id,
                expected_version=prior_version,
                result=executed_result,
                source_snapshots=snapshots,
                next_state=next_state,
                ttl_seconds=self.result_ttl_seconds,
            )
            validate_contract(committed_state, "turn-state.schema.json", stage="state_commit")
            events = list(getattr(self.state_store, "events", []))[event_offset:]
            events.append("runtime_release")
            events.append("terminal_fanout")
            response = assemble_response(
                request=request,
                intent=intent,
                plan=plan,
                result=result,
                answer_facts=facts,
                state=committed_state,
                result_ref=result_ref,
                source_refs=source_refs,
                route_telemetry=route_telemetry,
                source_diagnostics=diagnostics,
                data_mode=data_mode,
                download_base_url=self.download_base_url,
                events=events,
            )
            return response
        except ContractError as exc:
            return error_response(request, exc.as_dict(trace_id), route_telemetry)
        except Exception as exc:
            unexpected = ContractError(
                "plan_contract_error",
                "runtime",
                "분석 실행 중 계약 오류가 발생했습니다.",
                {"error_type": type(exc).__name__},
            )
            return error_response(request, unexpected.as_dict(trace_id), route_telemetry)

    @staticmethod
    def _executed_result(
        result: dict[str, Any],
        plan: dict[str, Any],
        source_snapshots: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build the immutable, followup-compatible stored result contract.

        Rows and columns intentionally remain top-level so typed follow-up plans
        can consume the prior frame without duplicating the analysis result.
        """

        result_contract = plan.get("result_contract") if isinstance(plan.get("result_contract"), dict) else {}
        criteria = {
            str(job.get("job_id") or ""): {
                "dataset_key": job.get("dataset_key"),
                "parameters": deepcopy(job.get("parameters") or {}),
                "filters": deepcopy(job.get("filters") or {}),
            }
            for job in plan.get("retrieval_jobs", [])
            if isinstance(job, dict) and job.get("job_id")
        }
        material = {
            "contract_version": "executed.result.v1",
            "status": result.get("status"),
            "plan_id": result.get("plan_id"),
            "columns": deepcopy(result.get("columns") or []),
            "rows": deepcopy(result.get("rows") or []),
            "row_count": int(result.get("row_count") or 0),
            "lineage": deepcopy(result.get("lineage") or {}),
            "operation_trace": deepcopy(result.get("operation_trace") or []),
            "result_sha256": result.get("result_sha256"),
            "grain": deepcopy(result_contract.get("grain") or []),
            "entities": deepcopy(result_contract.get("columns") or []),
            "criteria": criteria,
            "source_snapshot_sha256": [sha256_json(item) for item in source_snapshots],
            "analysis_result_sha256": sha256_json(result),
        }
        executed = {**material, "executed_result_contract_sha256": sha256_json(material)}
        return validate_contract(executed, "executed-result.schema.json", stage="executed_result_contract")

    def _retrieve(self, job: dict[str, Any], data_mode: str) -> dict[str, Any]:
        if str(data_mode or "dummy") != "dummy" and hasattr(self.source_adapter, "retrieve_live"):
            result = self.source_adapter.retrieve_live(job, self.catalog)
        elif hasattr(self.source_adapter, "retrieve"):
            result = self.source_adapter.retrieve(job, self.catalog)
        elif callable(self.source_adapter):
            result = self.source_adapter(job, self.catalog)
        else:
            raise ContractError("source_missing", "retrieval", "조회 adapter가 없습니다.")
        if not isinstance(result, dict):
            raise ContractError("source_retrieval_failed", "retrieval", "조회 adapter 결과 형식이 올바르지 않습니다.")
        status = str(result.get("status") or "error")
        if status not in {"ok", "empty", "error"}:
            raise ContractError("source_retrieval_failed", "retrieval", "조회 상태가 올바르지 않습니다.")
        if status == "error" and str(job.get("requirement") or "required") == "required":
            error = result.get("error") if isinstance(result.get("error"), dict) else {}
            raise ContractError(
                str(error.get("code") or "source_retrieval_failed"),
                "retrieval",
                str(error.get("message") or "필수 데이터 조회가 실패했습니다."),
                {"job_id": job.get("job_id")},
            )
        return result

    def _merge_sources(
        self,
        plan: dict[str, Any],
        source_results: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
        try:
            from .source_contracts import executor_frames, merge_source_results

            bundle = merge_source_results(
                source_results,
                self.catalog,
                retrieval_jobs=plan.get("retrieval_jobs") or [],
            )
            frames = executor_frames(bundle, self.catalog)
            snapshots = [deepcopy(frame) for frame in bundle.get("frames", {}).values()]
            diagnostics = [
                {
                    "job_id": item.get("source_alias"),
                    "dataset_key": item.get("dataset_key"),
                    "status": item.get("status"),
                    "row_count": item.get("row_count"),
                    "content_sha256": item.get("canonical_content_sha256"),
                }
                for item in bundle.get("source_manifest", [])
            ]
            return frames, snapshots, diagnostics
        except ImportError:
            pass
        frames: dict[str, Any] = {}
        snapshots: list[dict[str, Any]] = []
        diagnostics: list[dict[str, Any]] = []
        for result in source_results:
            job_id = str(result.get("job_id") or "")
            rows = result.get("rows") if isinstance(result.get("rows"), list) else []
            frames[job_id] = rows
            snapshots.append({"job_id": job_id, "rows": deepcopy(rows), "status": result.get("status")})
            diagnostics.append({"job_id": job_id, "status": result.get("status"), "row_count": len(rows)})
        return frames, snapshots, diagnostics
