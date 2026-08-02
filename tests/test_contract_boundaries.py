from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

import pytest

import reference_runtime.engine as engine_module
from reference_runtime.canonical import ContractError, sha256_json
from reference_runtime.contracts import validate_contract
from reference_runtime.dummy_data import source_result_for_dataset
from reference_runtime.engine import AnalysisEngine
from reference_runtime.plan_compiler import build_candidate_bundle, compile_plan, resolve_intent, validate_plan
from reference_runtime.presenter import api_output, gaia_output, normalize_display_options
from reference_runtime.request_literals import build_request_capsule
from reference_runtime.state_contracts import InMemoryStateStore


ROOT = Path(__file__).resolve().parents[1]


def case(case_id: str) -> dict:
    for line in (ROOT / "validation" / "cases.jsonl").read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        if item["case_id"] == case_id:
            return item
    raise AssertionError(case_id)


def clarification_selector(prompt: str) -> str:
    candidate_ids = re.findall(r'"candidate_id":"([^"]+)"', prompt)
    selected = next(item for item in candidate_ids if "clarification" in item)
    return json.dumps({"intent_candidate_id": selected})


def test_success_validates_every_trusted_runtime_boundary(monkeypatch: pytest.MonkeyPatch):
    selected = case("BR-D01")
    state_store = InMemoryStateStore()
    observed: list[str] = []
    original = engine_module.validate_contract

    def recording_validate(value, schema_name, **kwargs):
        observed.append(schema_name)
        return original(value, schema_name, **kwargs)

    monkeypatch.setattr(engine_module, "validate_contract", recording_validate)
    engine = AnalysisEngine(state_store=state_store)
    response = engine.analyze(
        selected["question"],
        session_id="boundary-success",
        subject_id="owner",
        reference_instant=selected["reference_instant"],
    )
    assert response["status"] == "ok"
    assert {
        "request-capsule.schema.json",
        "analysis-route.schema.json",
        "semantic-intent.schema.json",
        "analysis-plan.schema.json",
        "analysis-result.schema.json",
        "executed-result.schema.json",
        "turn-state.schema.json",
    } <= set(observed)
    validate_contract(response, "response.schema.json", stage="test")
    assert api_output(response) == response
    gaia = gaia_output(response)
    validate_contract(gaia["metadata"], "gaia-metadata.schema.json", stage="test")
    assert "response_sha256" not in gaia["metadata"]

    state = state_store.load_state("owner", "boundary-success")
    validate_contract(state, "turn-state.schema.json", stage="test")
    stored = state_store.load_ref(state["executed_result_ref"], "owner", "boundary-success")["payload"]
    validate_contract(stored, "executed-result.schema.json", stage="test")
    assert stored["rows"] == response["data"]["rows"]


class EmptyAdapter:
    def retrieve(self, job: dict, catalog: dict) -> dict:
        result = source_result_for_dataset(
            str(job["dataset_key"]),
            source_alias=str(job.get("source_alias") or job["job_id"]),
            rows=[],
        )
        result["applied_parameters"] = deepcopy(job.get("parameters") or {})
        result["applied_filters_sha256"] = sha256_json(job.get("filters") or {})
        return result


class FailingAdapter:
    def retrieve(self, job: dict, catalog: dict) -> dict:
        return {
            "status": "error",
            "error": {"code": "source_timeout", "message": "source timeout"},
        }


def test_empty_error_unsupported_and_clarification_responses_are_contract_valid():
    selected = case("BR-D01")
    empty = AnalysisEngine(source_adapter=EmptyAdapter()).analyze(
        selected["question"],
        session_id="empty",
        subject_id="owner",
        reference_instant=selected["reference_instant"],
    )
    assert empty["status"] == "empty"
    assert empty["stage_status"]["analysis"] == "empty"
    validate_contract(empty, "response.schema.json", stage="test")

    failure = AnalysisEngine(source_adapter=FailingAdapter()).analyze(
        selected["question"],
        session_id="error",
        subject_id="owner",
        reference_instant=selected["reference_instant"],
    )
    assert failure["status"] == "error"
    assert failure["analysis"]["error"]["code"] == "source_timeout"
    assert failure["stage_status"]["retrieval"] == "error"
    validate_contract(failure, "response.schema.json", stage="test")

    unsupported_case = case("BR-U01")
    unsupported = AnalysisEngine().analyze(
        unsupported_case["question"],
        session_id="unsupported",
        subject_id="owner",
        reference_instant=unsupported_case["reference_instant"],
    )
    assert unsupported["status"] == "error"
    assert unsupported["analysis"]["error"]["code"] == "unsupported_operation"
    assert unsupported["stage_status"]["retrieval"] == "not_called"
    validate_contract(unsupported, "response.schema.json", stage="test")

    clarification_case = case("BR-A01")
    clarification = AnalysisEngine().analyze(
        clarification_case["question"],
        session_id="clarification",
        subject_id="owner",
        reference_instant=clarification_case["reference_instant"],
        llm_callable=clarification_selector,
    )
    assert clarification["status"] == "needs_clarification"
    assert clarification["analysis"]["error"] is None
    assert clarification["clarification"]["options"]
    validate_contract(clarification, "response.schema.json", stage="test")


def test_request_route_intent_plan_and_format_checker_are_authoritative():
    selected = case("BR-D01")
    engine = AnalysisEngine()
    request = build_request_capsule(
        selected["question"],
        session_id="direct",
        subject_id="owner",
        reference_instant=selected["reference_instant"],
    )
    validate_contract(request, "request-capsule.schema.json", stage="test")
    bundle = build_candidate_bundle(request, engine.catalog)
    validate_contract(bundle["route_decision"], "analysis-route.schema.json", stage="test")
    intent, _ = resolve_intent(request, bundle)
    validate_contract(intent, "semantic-intent.schema.json", stage="test")
    plan = validate_plan(compile_plan(intent, bundle, engine.catalog), engine.catalog)
    validate_contract(plan, "analysis-plan.schema.json", stage="test")

    malformed = {**request, "reference_instant": "not-a-date"}
    with pytest.raises(ContractError) as invalid:
        validate_contract(malformed, "request-capsule.schema.json", stage="test")
    assert invalid.value.code == "intent_contract_error"
    assert invalid.value.details["path"] == "reference_instant"


def test_display_contract_is_closed_and_preview_is_bounded():
    options = normalize_display_options(
        {"profile": "diagnostic", "include_diagnostics": True, "table_preview_limit": 10_000}
    )
    validate_contract(options, "display-options.schema.json", stage="test")
    assert options["profile"] == "diagnostic"
    assert options["table_preview_limit"] == 20
    assert options["show_execution_plan"] is True

    with pytest.raises(ContractError):
        validate_contract({**options, "unknown_toggle": True}, "display-options.schema.json", stage="test")


def test_output_adapters_do_not_reject_post_execution_json_changes():
    selected = case("BR-D01")
    response = AnalysisEngine().analyze(
        selected["question"],
        session_id="hash",
        subject_id="owner",
        reference_instant=selected["reference_instant"],
    )
    assert "response_sha256" not in response
    response["trace"]["commit_order"].append("post_hash_mutation")
    assert api_output(response)["trace"]["commit_order"][-1] == "post_hash_mutation"
