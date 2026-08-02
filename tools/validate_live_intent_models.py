"""Run only the bounded Intent-LLM branch against real Gemini profiles.

The trusted deterministic executor remains identical to the offline corpus
runner.  The provider sees the compact candidate-card prompt and may return
only one registered candidate ID; it never generates pandas code or an
execution plan.  Reports contain hashes and conformance facts, never keys or
raw provider payloads.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import sha256_json
from reference_runtime.engine import AnalysisEngine
from reference_runtime.plan_compiler import build_candidate_bundle
from reference_runtime.request_literals import build_request_capsule
from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    GeminiJsonModel,
    assert_secret_absent,
    gemini_model_contract_evidence,
    require_exact_gemini_model,
    resolve_gemini_api_key,
)
from tools.validate_runtime_cases import (
    KIND_ALIASES,
    CountingSourceAdapter,
    _actual_datasets,
    _base_failures,
    _clauses,
    _data,
    _new_engine,
    _operations,
    _registered_invariant,
    _semantic,
    load_cases,
)


GeminiIntentSelector = GeminiJsonModel


class RecordingIntentSelector:
    """Proxy that retains only the sealed candidate ID, never provider text."""

    def __init__(self, provider: GeminiJsonModel) -> None:
        self.provider = provider
        self.selected_candidate_ids: list[str] = []

    def invoke(self, prompt: str) -> str:
        text = self.provider.invoke(prompt)
        raw = str(text or "").strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
            raw = raw.rsplit("```", 1)[0].strip()
        try:
            value = json.loads(raw[raw.find("{") : raw.rfind("}") + 1])
        except (ValueError, json.JSONDecodeError):
            value = {}
        candidate_id = value.get("intent_candidate_id") if isinstance(value, dict) else None
        if isinstance(candidate_id, str) and candidate_id and len(candidate_id) <= 192:
            self.selected_candidate_ids.append(candidate_id)
        return text

    def __getattr__(self, name: str) -> Any:
        return getattr(self.provider, name)


def _preceding_cases(case: dict[str, Any], all_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return earlier turns only for an explicitly named multi-turn scenario."""

    scenario_id = case.get("scenario_id")
    turn_index = int(case.get("turn_index") or 1)
    if not scenario_id or turn_index <= 1:
        return []
    return sorted(
        (
            item
            for item in all_cases
            if item.get("scenario_id") == scenario_id
            and int(item.get("turn_index") or 0) < turn_index
        ),
        key=lambda item: int(item.get("turn_index") or 0),
    )


def _candidate_evidence(
    engine: AnalysisEngine,
    case: dict[str, Any],
    *,
    subject_id: str,
    session_id: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Rebuild the exact sealed candidate bundle before the live selection call."""

    prior_state = engine.state_store.load_state(subject_id, session_id)
    prior_ref = str((prior_state or {}).get("executed_result_ref") or "") if isinstance(prior_state, dict) else ""
    prior_semantics = (
        (((prior_state or {}).get("semantic_context") or {}).get("semantics") or {})
        if isinstance(prior_state, dict)
        else {}
    )
    prior_result: dict[str, Any] = {}
    if prior_ref:
        prior_record = engine.state_store.load_ref(prior_ref, subject_id, session_id)
        prior_result = deepcopy(prior_record.get("payload") or {})
    request = build_request_capsule(
        str(case["question"]),
        session_id=session_id,
        subject_id=subject_id,
        reference_instant=str(case["reference_instant"]),
        previous_state_ref=prior_ref,
    )
    bundle = build_candidate_bundle(
        request,
        engine.catalog,
        prior_semantics=prior_semantics,
        prior_result=prior_result,
    )
    candidates = {
        str(item.get("candidate_id")): item
        for item in bundle.get("intent_candidates") or []
        if isinstance(item, dict) and item.get("candidate_id")
    }
    expected_kind = str((case.get("expected_semantic_contract") or {}).get("analysis_kind") or "")
    accepted_kinds = KIND_ALIASES.get(expected_kind, {expected_kind})
    expected_ids = sorted(
        candidate_id
        for candidate_id, item in candidates.items()
        if str((item.get("semantics") or {}).get("analysis_kind") or "") in accepted_kinds
    )
    evidence = {
        "candidate_bundle_sha256": bundle.get("bundle_sha256"),
        "candidate_count": len(candidates),
        "candidate_ids": sorted(candidates),
        "candidate_semantics_sha256": {
            candidate_id: item.get("semantics_sha256")
            for candidate_id, item in sorted(candidates.items())
        },
        "expected_analysis_kind": expected_kind,
        "expected_candidate_ids": expected_ids,
    }
    return evidence, candidates


def _response_context(case: dict[str, Any], response: dict[str, Any], retrieval_calls: int) -> dict[str, Any]:
    columns, rows = _data(response)
    return {
        "case": case,
        "response": response,
        "route": ((response.get("trace") or {}).get("route") or {}),
        "semantic": _semantic(response),
        "operations": _operations(response),
        "clauses": _clauses(response),
        "columns": columns,
        "rows": rows,
        "datasets": _actual_datasets(response),
        "retrieval_calls": retrieval_calls,
        "state_before": None,
        "state_after": None,
    }


def _execute_case(
    case: dict[str, Any],
    all_cases: list[dict[str, Any]],
    selector: RecordingIntentSelector,
    *,
    run_index: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    engine, counter = _new_engine("")
    scenario = str(case.get("scenario_id") or case["case_id"])
    subject_id = f"live-intent:{selector.model}:{run_index}"
    session_id = f"live-intent:{scenario}:{run_index}"
    turn_index = int(case.get("turn_index") or 1)
    preceding = _preceding_cases(case, all_cases)
    for seed in preceding:
        seed_response = engine.analyze(
            str(seed["question"]),
            session_id=session_id,
            subject_id=subject_id,
            reference_instant=str(seed["reference_instant"]),
        )
        if seed_response.get("status") not in {"ok", "empty"}:
            raise RuntimeError(f"seed_failed:{seed['case_id']}:{seed_response.get('status')}")

    candidate_evidence, candidates = _candidate_evidence(
        engine,
        case,
        subject_id=subject_id,
        session_id=session_id,
    )
    calls_before = counter.calls
    response = engine.analyze(
        str(case["question"]),
        session_id=session_id,
        subject_id=subject_id,
        reference_instant=str(case["reference_instant"]),
        model=selector,
    )
    retrieval_calls = counter.calls - calls_before
    context = _response_context(case, response, retrieval_calls)
    failures = _base_failures(case, response, selector, retrieval_calls)
    for invariant in (case.get("expected_result_contract") or {}).get("invariant_ids", []):
        passed, reason = _registered_invariant(str(invariant), context)
        if not passed:
            failures.append(f"invariant:{reason}")
    route = context["route"]
    error = ((response.get("analysis") or {}).get("error") or {})
    actual_candidate_id = selector.selected_candidate_ids[-1] if selector.selected_candidate_ids else None
    expected_candidate_ids = candidate_evidence["expected_candidate_ids"]
    selected_card = candidates.get(str(actual_candidate_id or ""))
    expected_card = candidates.get(expected_candidate_ids[0]) if len(expected_candidate_ids) == 1 else None
    actual_semantics = context["semantic"]
    semantic_checks = {
        "selected_candidate_registered": actual_candidate_id in candidates,
        "expected_candidate_unique": len(expected_candidate_ids) == 1,
        "selected_candidate_exact": len(expected_candidate_ids) == 1
        and actual_candidate_id == expected_candidate_ids[0],
    }
    reported_candidate_id = (
        actual_candidate_id
        if actual_candidate_id in candidates
        else (f"sha256:{sha256_json(actual_candidate_id)}" if actual_candidate_id else None)
    )
    if response.get("status") in {"ok", "empty"}:
        semantic_checks["selected_semantics_sealed"] = bool(selected_card) and actual_semantics == (
            selected_card.get("semantics") or {}
        )
        semantic_checks["expected_semantics_exact"] = bool(expected_card) and actual_semantics == (
            expected_card.get("semantics") or {}
        )
    failures.extend(name for name, passed in semantic_checks.items() if not passed)
    row = {
        "case_id": case["case_id"],
        "passed": not failures,
        "failures": sorted(set(failures)),
        "actual_status": response.get("status"),
        "actual_route": route.get("route"),
        "actual_route_reason": route.get("reason_code"),
        "actual_selected_candidate_id": reported_candidate_id,
        "candidate_evidence": candidate_evidence,
        "actual_semantics_sha256": sha256_json(actual_semantics) if actual_semantics else None,
        "semantic_checks": semantic_checks,
        "intent_llm_calls": route.get("intent_llm_calls"),
        "retrieval_calls": retrieval_calls,
        "actual_error_code": error.get("code"),
        "analysis_kind": context["semantic"].get("analysis_kind"),
        "plan_fingerprint": ((response.get("analysis") or {}).get("plan_fingerprint")),
        "result_sha256": ((response.get("analysis") or {}).get("result_sha256")),
        "response_sha256": response.get("response_sha256"),
        "provider_response_sha256": selector.response_hashes[-1] if selector.response_hashes else None,
        "provider_usage": selector.evidence()["usage"],
        "provider_model_versions": selector.evidence()["provider_model_versions"],
    }
    return row, response


def run(models: list[str], runs: int, env_path: Path) -> dict[str, Any]:
    normalized_models = [require_exact_gemini_model(model) for model in models]
    if normalized_models != [DEFAULT_GEMINI_MODEL]:
        raise RuntimeError("single_exact_gemini_model_required")
    if int(runs) < 1:
        raise RuntimeError("positive_run_count_required")
    api_key = resolve_gemini_api_key(env_path)
    all_cases = load_cases()
    selected = [case for case in all_cases if case.get("expected_route") == "intent_llm"]
    rows: list[dict[str, Any]] = []
    for model in normalized_models:
        for run_index in range(1, runs + 1):
            for case in selected:
                provider = GeminiJsonModel(
                    api_key=api_key,
                    model=model,
                    timeout_seconds=60,
                    max_output_tokens=256,
                )
                selector = RecordingIntentSelector(provider)
                try:
                    row, _ = _execute_case(case, all_cases, selector, run_index=run_index)
                except Exception as exc:
                    row = {
                        "case_id": case["case_id"],
                        "passed": False,
                        "failures": [str(exc).splitlines()[0][:160]],
                        "actual_status": "validation_error",
                        "actual_route": None,
                        "intent_llm_calls": selector.calls,
                        "provider_response_sha256": selector.response_hashes[-1] if selector.response_hashes else None,
                        "provider_usage": selector.evidence()["usage"],
                        "provider_model_versions": selector.evidence()["provider_model_versions"],
                    }
                provider_evidence = selector.evidence()
                provider_model_exact = provider_evidence.get("provider_model_versions_exact") is True
                row["provider_model_versions_exact"] = provider_model_exact
                if row.get("passed") is True and not provider_model_exact:
                    row["passed"] = False
                    row.setdefault("failures", []).append("provider_model_version_mismatch")
                row["model"] = model
                row["run_index"] = run_index
                rows.append(row)
    report = {
        "contract_version": "live.intent.model.validation.v1",
        "models": normalized_models,
        "model_contract": gemini_model_contract_evidence(),
        "runs_per_model": runs,
        "intent_case_count": len(selected),
        "total_executions": len(rows),
        "passed": sum(1 for row in rows if row["passed"]),
        "failed": sum(1 for row in rows if not row["passed"]),
        "pandas_code_llm_calls": 0,
        "pandas_repair_llm_calls": 0,
        "provider_model_evidence_passed": all(
            row.get("provider_model_versions_exact") is True for row in rows
        ),
        "rows": rows,
    }
    assert_secret_absent(report, api_key)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=[DEFAULT_GEMINI_MODEL])
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--output", type=Path, default=ROOT / "validation_outputs" / "live_intent_models.json")
    args = parser.parse_args()
    report = run([str(model) for model in args.models], int(args.runs), args.env_file)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"live intent validation: {report['passed']}/{report['total_executions']} passed")
    print(f"report: {args.output}")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
