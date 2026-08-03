from __future__ import annotations

from copy import deepcopy

import pytest

from reference_runtime.canonical import ContractError, sha256_json
from reference_runtime.presenter import (
    api_output,
    assemble_response,
    error_response,
    gaia_output,
    normalize_display_options,
    pandas_equivalent_code,
    render_message,
)
from reference_runtime.state_contracts import InMemoryStateStore


def sample_response() -> dict:
    response = {
        "contract_version": "response.v1",
        "response_type": "data_analysis",
        "status": "ok",
        "stage_status": {"overall": "ok", "intent": "skipped", "retrieval": "ok", "analysis": "ok"},
        "message": "2건입니다.",
        "data_mode": "dummy",
        "analysis_mode": "typed_ir",
        "data": {
            "columns": ["ITEM", "VALUE"],
            "rows": [{"ITEM": "A", "VALUE": 2}, {"ITEM": "B", "VALUE": 1}],
            "row_count": 2,
        },
        "answer_sections": {
            "contract_version": "answer.sections.v1",
            "summary": {"headline": "2건입니다.", "fact_ids": ["fact:row_count"]},
            "result_table": {
                "row_source": "data.rows",
                "columns": ["ITEM", "VALUE"],
                "row_count": 2,
                "data_ref": "result:sample",
            },
            "applied_criteria": {"datasets": ["production_today"]},
            "evidence": {"plan_id": "plan:x"},
            "downloads": [],
            "notices": [],
            "next_questions": [{"id": "f1", "text": "가장 큰 항목만 보여줘"}],
        },
        "request": {
            "request_id": "request:sample",
            "question": "sample",
            "session_id": "s",
            "reference_instant": "2026-07-30T09:00:00+09:00",
            "timezone": "Asia/Seoul",
        },
        "intent_plan": {"semantic_intent": {"analysis_kind": "rank"}},
        "analysis": {
            "execution_ir": [{"id": "rank", "op": "rank", "input": "source:s", "rank_by": [{"field": "VALUE", "direction": "desc"}], "limit": 1}],
            "pandas_code": pandas_equivalent_code([{"id": "rank", "op": "rank", "input": "source:s", "rank_by": [{"field": "VALUE", "direction": "desc"}], "limit": 1}]),
        },
        "clarification": None,
        "data_refs": [],
        "state": None,
        "trace": {
            "retrieval": [{"job_id": "j", "status": "ok"}],
            "trace_id": "trace:sample",
            "route": {"route": "deterministic"},
            "usage": {
                "intent_llm_calls": 0,
                "pandas_code_llm_calls": 0,
                "pandas_repair_llm_calls": 0,
                "answer_llm_calls": 0,
            },
            "commit_order": [],
        },
    }
    return response


def test_display_toggles_change_only_markdown():
    response = sample_response()
    before = sha256_json(response)
    minimal = render_message(response, {"show_result_table": False, "show_download_links": False, "show_applied_criteria": False})
    diagnostic = render_message(response, {"include_diagnostics": True, "show_result_table": True})
    assert "결과 테이블" not in minimal
    assert "실행 계획 진단" in diagnostic
    assert "의도 분석" in diagnostic
    assert sha256_json(response) == before


def test_show_pandas_code_is_a_separate_display_section():
    options = normalize_display_options({"show_pandas_code": True, "table_preview_limit": 999})
    assert options["profile"] == "standard"
    assert options["show_pandas_code"] is True
    assert options["show_execution_plan"] is False
    assert options["table_preview_limit"] == 20
    message = render_message(sample_response(), {"show_pandas_code": True})
    assert "Pandas 등가 코드 (표시용)" in message
    assert "sort_values" in message
    assert "실행 계획 진단" not in message


def test_message_api_and_gaia_consume_same_json_response():
    response = sample_response()
    api_value = api_output(response)
    value = gaia_output(response)
    assert api_value == response and api_value is not response
    assert value["answer"] == "2건입니다."
    assert value["metadata"]["followup_questions"] == [{"id": "f1", "text": "가장 큰 항목만 보여줘"}]
    assert "response_sha256" not in value["metadata"]
    assert value["metadata"]["usage"] == response["trace"]["usage"]


def test_output_adapters_accept_response_mutation_without_hash_comparison():
    response = sample_response()
    tampered = deepcopy(response)
    tampered["message"] = "mutated"
    assert api_output(tampered)["message"] == "mutated"
    assert gaia_output(tampered)["answer"] == "mutated"


def test_chat_and_api_output_do_not_fail_on_presentation_changes():
    response = sample_response()
    response["message"] = "표시 단계에서 사용할 답변입니다."

    rendered = render_message(response, {"show_result_table": False})

    assert "표시 단계에서 사용할 답변입니다." in rendered
    assert api_output(response)["message"] == response["message"]


@pytest.mark.parametrize(
    ("code", "stage"),
    (("request_invalid", "request"), ("state_policy_mismatch", "state_store_config")),
)
def test_runtime_boundary_errors_are_registered(code: str, stage: str):
    response = error_response(
        {
            "request_id": "request:error-boundary",
            "question": "invalid request",
            "session_id": "session:error-boundary",
            "reference_instant": "2026-08-01T09:00:00+09:00",
            "timezone": "Asia/Seoul",
        },
        ContractError(code, stage, "fail closed").as_dict("trace:error-boundary"),
    )
    assert response["status"] == "error"
    assert response["analysis"]["error"]["code"] == code
    assert response["analysis"]["error"]["stage"] == stage


def test_result_ref_ownership_ttl_and_state_cas():
    store = InMemoryStateStore()
    state, result_ref, source_refs = store.commit_execution(
        subject_id="u1",
        session_id="s1",
        expected_version=0,
        result={"rows": [{"A": 1}]},
        source_snapshots=[{"rows": [{"A": 1}]}],
        next_state={"last_question": "q"},
        ttl_seconds=3600,
    )
    assert state["state_version"] == 1
    assert store.events == ["result_store", "state_cas"]
    assert store.load_ref(result_ref["ref_id"], "u1", "s1")["payload"]["rows"] == [{"A": 1}]
    with pytest.raises(ContractError) as forbidden:
        store.load_ref(result_ref["ref_id"], "u2", "s1")
    assert forbidden.value.code == "state_reference_forbidden"
    with pytest.raises(ContractError) as conflict:
        store.commit_execution(
            subject_id="u1",
            session_id="s1",
            expected_version=0,
            result={"rows": []},
            source_snapshots=[],
            next_state={},
            ttl_seconds=3600,
        )
    assert conflict.value.code == "state_conflict"


def test_ephemeral_response_has_no_synthetic_download_or_state_reference():
    digest = "a" * 64
    response = assemble_response(
        request={
            "request_id": "request:ephemeral",
            "question": "total sales",
            "session_id": "session:ephemeral",
            "reference_instant": "2026-07-30T09:00:00+09:00",
            "timezone": "Asia/Seoul",
        },
        intent={
            "intent_sha256": digest,
            "intent_candidate_id": "intent:ephemeral",
            "semantics": {},
        },
        plan={
            "plan_id": "plan:ephemeral",
            "plan_fingerprint": digest,
            "retrieval_jobs": [],
            "result_contract": {"grain": []},
            "operations": [],
            "lineage": {},
        },
        result={
            "status": "ok",
            "columns": ["VALUE"],
            "rows": [{"VALUE": 1}],
            "row_count": 1,
            "result_sha256": digest,
            "operation_trace": [],
            "lineage": {},
        },
        answer_facts={"facts_sha256": digest},
        state={},
        result_ref={},
        source_refs=[],
        route_telemetry={"route": "deterministic", "intent_llm_calls": 0},
        source_diagnostics=[],
        data_mode="inline",
    )

    assert response["state"] is None
    assert response["data_refs"] == []
    assert response["answer_sections"]["downloads"] == []
    assert response["answer_sections"]["result_table"]["data_ref"] == ""
