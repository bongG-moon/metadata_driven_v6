from __future__ import annotations

import json

from reference_runtime.plan_compiler import (
    build_candidate_bundle,
    build_intent_prompt,
    resolve_intent,
)
from reference_runtime.request_literals import build_request_capsule
from tools.validate_live_intent_models import _preceding_cases
from tools.validate_runtime_cases import _new_engine, load_cases


def _mt04_bundle():
    cases = load_cases()
    case = next(item for item in cases if item["case_id"] == "MT04-02")
    engine, _counter = _new_engine("")
    subject_id = "intent-card:test"
    session_id = "intent-card:mt04"
    for seed in _preceding_cases(case, cases):
        response = engine.analyze(
            seed["question"],
            session_id=session_id,
            subject_id=subject_id,
            reference_instant=seed["reference_instant"],
        )
        assert response["status"] == "ok"
    prior_state = engine.state_store.load_state(subject_id, session_id)
    assert prior_state
    prior_ref = prior_state["executed_result_ref"]
    prior_record = engine.state_store.load_ref(prior_ref, subject_id, session_id)
    request = build_request_capsule(
        case["question"],
        session_id=session_id,
        subject_id=subject_id,
        reference_instant=case["reference_instant"],
        previous_state_ref=prior_ref,
    )
    bundle = build_candidate_bundle(
        request,
        engine.catalog,
        prior_semantics=prior_state["semantic_context"]["semantics"],
        prior_result=prior_record["payload"],
    )
    return request, bundle


def test_elliptical_followup_cards_distinguish_summary_from_raw_detail() -> None:
    request, bundle = _mt04_bundle()
    cards = {card["analysis_kind"]: card for card in bundle["prompt_cards"]}
    assert set(cards) == {"aggregate", "detail"}
    assert cards["aggregate"]["result_shape"] == "grouped_summary"
    assert cards["aggregate"]["selection_policy"] == (
        "replace_newly_mentioned_filter_and_keep_previous_metric_date_dimensions_aggregation"
    )
    assert cards["detail"]["result_shape"] == "individual_rows"
    assert cards["detail"]["selection_policy"] == (
        "switch_to_individual_rows_only_when_detail_rows_list_or_identifiers_are_explicit"
    )
    assert cards["aggregate"]["registered_product_group_refs"] == ["POP"]
    assert cards["detail"]["registered_product_group_refs"] == ["POP"]

    prompt = build_intent_prompt(request, bundle)
    assert "prefer grouped_summary over individual_rows" in prompt
    assert "explicitly asks for detail, raw rows" in prompt
    assert "reference_instant" not in prompt
    assert len(prompt.encode("utf-8")) < 4096


def test_enriched_prompt_does_not_change_candidate_ids_or_executable_semantics() -> None:
    request, bundle = _mt04_bundle()
    candidates = {
        item["semantics"]["analysis_kind"]: item
        for item in bundle["intent_candidates"]
    }
    assert candidates["aggregate"]["candidate_id"] == "intent:aggregate:5dc4557967bcc159"
    assert candidates["detail"]["candidate_id"] == "intent:detail:e5eb4c0eb669b529"

    class Selector:
        def invoke(self, prompt: str) -> str:
            cards = json.loads(prompt.split("Registered candidates:\n", 1)[1])
            selected = next(card for card in cards if card["result_shape"] == "grouped_summary")
            return json.dumps({"intent_candidate_id": selected["candidate_id"]})

    intent, telemetry = resolve_intent(request, bundle, model=Selector())
    assert telemetry["intent_llm_calls"] == 1
    assert intent["intent_candidate_id"] == candidates["aggregate"]["candidate_id"]
    assert intent["semantics"] == candidates["aggregate"]["semantics"]
