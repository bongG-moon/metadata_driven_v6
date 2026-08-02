from __future__ import annotations

import json
import urllib.error
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    GeminiJsonModel,
    assert_secret_absent,
)
from tools.validate_langflow_equivalent_pipeline import validate_flow_graph
from tools.validate_langflow_http_e2e import extract_terminal_evidence
from tools.validate_domain_extension_safety import validate_specialized_functions
from tools.validate_langflow_http_authoring_e2e import extract_authoring_evidence
from tools.validate_live_metadata_authoring import (
    ReplayModel,
    _draft_structure_evidence,
    _executable_structure_diff,
    _safe_failure,
)
import tools.validate_live_metadata_authoring as live_authoring
from tools.validate_live_component_models import CASES as LIVE_COMPONENT_CASES
from tools.validate_live_intent_models import RecordingIntentSelector, _preceding_cases
from tools.validate_live_v6_authoring_inputs import run as validate_v6_authoring_inputs
from tools.validate_prompt_extension_runtime import _prompt_evidence
from tools.validate_langflow_http_order_sales_e2e import (
    CASES as ORDER_SALES_HTTP_CASES,
    _inline_fixture,
    _json_input_tweak,
    _matches_rows,
)
from reference_runtime.canonical import ContractError
from reference_runtime.state_contracts import InMemoryStateStore


ROOT = Path(__file__).resolve().parents[1]
ORDER_SALES_CASES = ROOT / "validation" / "order_sales_validation_cases.jsonl"


def test_v6_worker_inputs_are_freeform_rewrites_with_recorded_lineage() -> None:
    report = validate_v6_authoring_inputs()

    assert report["all_passed"] is True
    for kind in ("domain", "dataset", "main_filter"):
        row = report["rows"][kind]
        assert row["lineage_relation"] == "freeform_operator_rewrite"
        assert row["freeform_rewrite_allowed"] is True
        assert row["exact_line_equality_required"] is False
        assert row["lineage_source_present"] is True
        assert len(row["lineage_sha256"]) == 64


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self) -> bytes:
        return self.payload


def test_gemini_adapter_uses_exact_requested_model_and_persists_no_secret() -> None:
    secret = "test-only-secret-value"
    observed = {}

    def opener(request, *, timeout):
        observed["url"] = request.full_url
        observed["key"] = request.get_header("X-goog-api-key")
        observed["timeout"] = timeout
        return _FakeResponse(
            {
                "candidates": [{"content": {"parts": [{"text": '{"ok":true}'}]}}],
                "usageMetadata": {
                    "promptTokenCount": 4,
                    "candidatesTokenCount": 3,
                    "totalTokenCount": 7,
                },
                "modelVersion": "gemini-3.5-flash-lite-test",
            }
        )

    model = GeminiJsonModel(api_key=secret, opener=opener)
    assert model.invoke("return JSON") == '{"ok":true}'
    evidence = model.evidence()
    assert DEFAULT_GEMINI_MODEL == "gemini-3.5-flash-lite"
    assert f"/{DEFAULT_GEMINI_MODEL}:generateContent" in observed["url"]
    assert observed["key"] == secret
    assert evidence["model"] == DEFAULT_GEMINI_MODEL
    assert evidence["calls"] == 1
    assert evidence["usage"] == {"prompt_tokens": 4, "candidate_tokens": 3, "total_tokens": 7}
    assert secret not in json.dumps(evidence)
    assert_secret_absent(evidence, secret)


def test_gemini_http_error_and_authoring_failure_are_secret_safe() -> None:
    secret = "never-report-this-key"

    def failing(request, *, timeout):
        raise urllib.error.HTTPError(request.full_url, 429, secret, {}, None)

    model = GeminiJsonModel(api_key=secret, opener=failing)
    with pytest.raises(RuntimeError, match="^gemini_http_429$") as error:
        model.invoke("prompt containing no secret")
    assert secret not in str(error.value)
    assert _safe_failure(RuntimeError(secret)) == {
        "code": "validation_RuntimeError",
        "stage": "validation",
    }


def test_authoring_failure_evidence_is_bounded_to_metadata_ids_and_hashes() -> None:
    structure = _draft_structure_evidence(
        {
            "datasets": {"orders": {}, "products": {}},
            "relations": {
                "orders_products": {
                    "left": "orders",
                    "right": "not-registered dataset value",
                    "keys": ["PRODUCT_ID"],
                    "type": "many_to_one",
                }
            },
        }
    )
    relation = structure["relations"][0]
    assert relation["attribute_keys"] == ["keys", "left", "right", "type"]
    assert relation["endpoint_candidates"]["left"] == "orders"
    assert str(relation["endpoint_candidates"]["right"]).startswith("sha256:")
    assert "not-registered dataset value" not in json.dumps(structure)

    failure = _safe_failure(
        ContractError(
            "metadata_dependency_error",
            "metadata_source_coverage",
            "coverage failed",
            {
                "counts": {"missing": {"relations": 1}},
                "missing": {"relations": ["orders_products"]},
                "unsafe": "must-not-survive",
            },
        )
    )
    assert failure["safe_details"] == {
        "counts": {"missing": {"relations": 1}},
        "missing": {"relations": ["orders_products"]},
    }


def test_authoring_executable_diff_reports_ids_counts_and_hashes_only() -> None:
    expected = {
        "metrics": {"M": {"formula": {"op": "subtract", "left_metric": "A", "right_metric": "B"}}},
        "grains": {"g": {"keys": ["F"]}},
        "predicates": {},
        "entity_groups": {},
        "recipes": {},
        "aliases": {},
    }
    actual = {
        "metrics": {"M": {"aggregation": "sum"}},
        "grains": {"g": {"keys": ["F"]}},
        "predicates": {"provider secret phrase": {"operator": "eq", "value": "hidden"}},
        "entity_groups": {},
        "recipes": {},
        "aliases": {},
    }
    evidence = _executable_structure_diff(actual, expected)
    assert evidence["all_exact"] is False
    assert evidence["sections"]["metrics"]["mismatched_ids"] == ["M"]
    assert len(evidence["sections"]["predicates"]["unexpected_id_sha256"]) == 1
    assert "provider secret phrase" not in json.dumps(evidence)


def test_replay_model_is_local_and_counted() -> None:
    replay = ReplayModel('{"draft":true}')
    assert replay.invoke("first") == '{"draft":true}'
    assert replay.calls == 1


def test_live_intent_seed_selection_requires_an_explicit_scenario() -> None:
    branch = {"case_id": "BR-A", "scenario_id": None, "turn_index": None}
    unrelated = {"case_id": "BR-SEED", "scenario_id": None, "turn_index": None}
    assert _preceding_cases(branch, [unrelated, branch]) == []

    first = {"case_id": "MT-01", "scenario_id": "MT", "turn_index": 1}
    second = {"case_id": "MT-02", "scenario_id": "MT", "turn_index": 2}
    other = {"case_id": "OTHER-01", "scenario_id": "OTHER", "turn_index": 1}
    assert _preceding_cases(second, [other, second, first]) == [first]


def test_live_intent_recorder_retains_only_candidate_id() -> None:
    class Provider:
        def invoke(self, prompt: str) -> str:
            return '{"intent_candidate_id":"intent:detail:abc"}'

    recorder = RecordingIntentSelector(Provider())
    assert recorder.invoke("prompt") == '{"intent_candidate_id":"intent:detail:abc"}'
    assert recorder.selected_candidate_ids == ["intent:detail:abc"]


def test_full_draft_authoring_harness_is_explicitly_obsolete_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = tmp_path / "metadata.txt"
    source.write_text("주문과 매출 metadata", encoding="utf-8")

    monkeypatch.setattr(
        live_authoring,
        "resolve_gemini_api_key",
        lambda env_path: "fake-secret-key",
    )
    monkeypatch.setattr(
        live_authoring,
        "validate_domain_source",
        lambda *args, **kwargs: {
            "passed": True,
            "provider": {"calls": 1},
            "diagnostic_only": True,
        },
    )
    report = live_authoring.run_v2(
        source,
        env_path=tmp_path / ".env",
        model=DEFAULT_GEMINI_MODEL,
        timeout_seconds=5,
        domain_id="order_sales",
        environment="test",
        revision=1,
    )
    assert report["execution_mode"] == "obsolete_full_draft_diagnostic"
    assert report["production_authoring_path"] is False
    assert report["replacement_validator"] == "tools/validate_live_blueprint_authoring.py"
    assert report["provider_calls"] == 1
    assert "fake-secret-key" not in json.dumps(report)


def test_live_authoring_harness_normalizes_manifest_backed_alias_shorthand(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from reference_runtime.domain_packages import compile_domain_package

    provider_draft = json.loads(
        (ROOT / "metadata" / "domain_packs" / "order_sales" / "authoring_draft.json").read_text(
            encoding="utf-8"
        )
    )
    provider_draft["aliases"]["달성률"] = "ACHIEVEMENT_RATE"

    class ShorthandProvider:
        def __init__(self, **kwargs):
            self.calls = 0

        def invoke(self, prompt: str) -> str:
            self.calls += 1
            return json.dumps(provider_draft, ensure_ascii=False)

        def evidence(self):
            return {
                "model": DEFAULT_GEMINI_MODEL,
                "calls": self.calls,
                "prompt_sha256": ["a" * 64],
                "provider_response_sha256": ["b" * 64],
                "provider_model_versions": ["fake"],
                "usage": {"prompt_tokens": 1, "candidate_tokens": 1, "total_tokens": 2},
            }

    def replay(raw_response, source_text, draft, *, domain_id, environment, revision):
        assert "달성률" not in draft["aliases"]
        assert draft["aliases"]["metric:ACHIEVEMENT_RATE"] == {
            "target_type": "metric",
            "target_key": "ACHIEVEMENT_RATE",
            "values": ["달성률"],
        }
        embedded = compile_domain_package(draft, domain_id, environment, revision=revision)
        return embedded, {
            "available": True,
            "prepare_invoked": True,
            "replay_calls": 1,
            "prepare_status": "ok",
            "prepare_stage": "prepared",
            "llm_usage": {"draft_llm_calls": 1, "repair_llm_calls": 0},
        }

    monkeypatch.setattr(live_authoring, "GeminiJsonModel", ShorthandProvider)
    monkeypatch.setattr(live_authoring, "_v2_prompt", lambda source_text: "exact-flow-prompt")
    monkeypatch.setattr(live_authoring, "_component_v2_replay", replay)
    source = tmp_path / "order_sales_metadata_input.txt"
    source.write_text(
        (ROOT / "validation" / "order_sales_metadata_input.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    row = live_authoring.validate_domain_source(
        source,
        api_key="fake-secret-key",
        model=DEFAULT_GEMINI_MODEL,
        timeout_seconds=5,
        domain_id="order_sales",
        environment="test",
        revision=1,
    )
    assert row["passed"] is True, json.dumps(row.get("checks"), ensure_ascii=False, indent=2)
    assert row["alias_shorthand_normalized"] is True


def test_live_component_matrix_covers_zero_intent_narrative_and_unsupported() -> None:
    by_id = {case["case_id"]: case for case in LIVE_COMPONENT_CASES}
    assert by_id["LIVE-ZERO"]["expected_calls"] == 0
    assert by_id["LIVE-INTENT"]["expected_intent_calls"] == 1
    assert by_id["LIVE-NARRATIVE"]["expected_answer_calls"] == 1
    assert by_id["LIVE-UNSUPPORTED"]["expected_calls"] == 0
    assert all(case["expected_calls"] <= 1 for case in LIVE_COMPONENT_CASES)


def _node(node_id: str, stage: str, capabilities: list[str] | None = None) -> dict:
    metadata = {"logical_stage": stage}
    if capabilities is not None:
        metadata["logical_capabilities"] = capabilities
    config: dict = {"metadata": metadata}
    if stage in {"request_state", "state_commit"}:
        config["template"] = {"allow_anonymous_multiturn": {"value": False}}
    return {"id": node_id, "data": {"node": config}}


def _edge(source: str, target: str) -> dict:
    return {"source": source, "target": target}


def test_langflow_graph_validator_accepts_split_stage_aliases_and_fanout() -> None:
    nodes = [
        _node("input", "input"),
        _node("model", "model"),
        _node("request", "request_state"),
        _node("domain", "domain_bundle"),
        _node("route", "candidate_route"),
        _node("intent_context", "intent_prompt_context"),
        _node("intent_common_prompt", "intent_prompt_composition"),
        _node("intent_specialized_prompt", "intent_prompt_composition"),
        _node("intent_composer", "intent_prompt_composition"),
        _node("intent_invoker", "intent_llm_invocation"),
        _node("intent", "intent_resolution"),
        _node("plan", "plan_compilation"),
        _node("router", "job_routing"),
        _node("dummy", "dummy_retrieval"),
        _node("inline", "inline_retrieval"),
        _node("live", "live_retrieval"),
        _node("merge", "source_merge"),
        _node("execute", "typed_execution"),
        _node("answer", "answer_facts", ["answer_facts", "narrative_claim"]),
        _node("answer_common_prompt", "answer_prompt_composition"),
        _node("answer_specialized_prompt", "answer_prompt_composition"),
        _node("answer_composer", "answer_prompt_composition"),
        _node("answer_invoker", "answer_llm_invocation"),
        _node("claim", "answer_claim_validation"),
        _node("commit", "state_commit"),
        _node("terminal", "terminals"),
    ]
    edges = [
        _edge("input", "request"),
        _edge("request", "route"),
        _edge("domain", "route"),
        _edge("route", "intent_context"),
        _edge("intent_context", "intent_composer"),
        _edge("intent_common_prompt", "intent_composer"),
        _edge("intent_specialized_prompt", "intent_composer"),
        _edge("intent_composer", "intent_invoker"),
        _edge("model", "intent_invoker"),
        _edge("intent_invoker", "intent"),
        _edge("intent", "plan"),
        _edge("plan", "router"),
        _edge("router", "dummy"),
        _edge("router", "inline"),
        _edge("router", "live"),
        _edge("dummy", "merge"),
        _edge("inline", "merge"),
        _edge("live", "merge"),
        _edge("merge", "execute"),
        _edge("execute", "answer"),
        _edge("answer", "answer_composer"),
        _edge("answer_common_prompt", "answer_composer"),
        _edge("answer_specialized_prompt", "answer_composer"),
        _edge("answer_composer", "answer_invoker"),
        _edge("model", "answer_invoker"),
        _edge("answer_invoker", "claim"),
        _edge("claim", "commit"),
        _edge("commit", "terminal"),
    ]
    report = validate_flow_graph({"id": "flow:test", "endpoint_name": "test", "data": {"nodes": nodes, "edges": edges}})
    assert report["passed"] is True, report["failures"]
    assert report["stage_counts"]["source_retriever"] == 3
    assert report["stage_counts"]["response_state_commit"] == 1


def test_langflow_graph_validator_rejects_anonymous_multiturn_enabled_by_default() -> None:
    nodes = [
        _node("request", "request_state"),
        _node("commit", "state_commit"),
    ]
    nodes[0]["data"]["node"]["template"]["allow_anonymous_multiturn"]["value"] = True
    report = validate_flow_graph(
        {"id": "flow:unsafe", "endpoint_name": "unsafe", "data": {"nodes": nodes, "edges": []}}
    )
    assert report["checks"]["anonymous_multiturn_defaults_off"] is False


def test_order_sales_suite_covers_routes_llm_counts_and_multiturn() -> None:
    rows = [json.loads(line) for line in ORDER_SALES_CASES.read_text(encoding="utf-8").splitlines() if line.strip()]
    schema = json.loads((ROOT / "validation" / "order_sales_case.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    assert not [error.message for row in rows for error in validator.iter_errors(row)]
    assert len(rows) >= 20
    assert len({row["case_id"] for row in rows}) == len(rows)
    assert {row["domain_id"] for row in rows} == {"order_sales"}
    assert [row["case_id"] for row in rows[:3]] == ["OS01", "OS02", "OS03"]
    assert {row["case_id"] for row in rows} >= {"OS01", "OS02", "OS08"}
    assert {row["expected_route"] for row in rows} == {"deterministic", "intent_llm", "unsupported"}
    assert all(row["expected_intent_llm_calls"] == (1 if row["expected_route"] == "intent_llm" else 0) for row in rows)
    assert all(row["expected_answer_llm_calls"] == (1 if row["narrative_enabled"] and row["expected_route"] != "unsupported" else 0) for row in rows)
    assert any(row["expected_retrieval_calls"] == 0 for row in rows)
    assert any(len(row["expected_datasets"]) >= 3 for row in rows)
    assert {row["capability"] for row in rows} >= {
        "aggregate",
        "top_n_join",
        "bottom_n",
        "argmax_all_ties",
        "argmin_all_ties",
        "projection",
        "compare_fields",
        "previous_result_argmax",
        "unsupported_forecast",
    }
    scenarios = {row["scenario_id"] for row in rows if row["scenario_id"]}
    assert scenarios == {"OSMT01", "OSMT02"}
    for scenario in scenarios:
        turns = sorted(row["turn_index"] for row in rows if row["scenario_id"] == scenario)
        assert turns == list(range(1, len(turns) + 1))


def test_prompt_extension_evidence_is_hash_only_and_utf8_bounded() -> None:
    prompt = "catalog-policy\nnode-overlay\n질문"
    evidence = _prompt_evidence(
        prompt,
        catalog_extension="catalog-policy",
        node_sentinel="node-overlay",
        max_bytes=128,
    )
    assert evidence["catalog_extension_present"] is True
    assert evidence["node_overlay_present"] is True
    assert evidence["prompt_within_budget"] is True
    assert prompt not in json.dumps(evidence, ensure_ascii=False)


def test_order_sales_http_fixture_enriches_refund_join_key_in_memory() -> None:
    fixture = _inline_fixture(ROOT / "metadata" / "domain_packs" / "order_sales" / "sample_rows.json")
    refunds = fixture["datasets"]["refunds"]
    assert {row["order_id"]: row["product_id"] for row in refunds} == {
        "O-002": "P-100",
        "O-003": "P-200",
        "O-005": "P-300",
    }
    assert _matches_rows(
        [{"PRODUCT_ID": "P-300", "SALES_AMOUNT": 1000.0}],
        [{"PRODUCT_ID": "P-300", "SALES_AMOUNT": 1000.0}],
    )
    assert not _matches_rows(
        [{"PRODUCT_ID": "P-300", "SALES_AMOUNT": 999.0}],
        [{"PRODUCT_ID": "P-300", "SALES_AMOUNT": 1000.0}],
    )


def test_order_sales_http_uses_utf8_questions_and_langflow_json_input_wrapper() -> None:
    expected_questions = {
        "OS01": "오늘 전체 주문의 매출액 합계를 알려줘",
        "OS02": "오늘 매출액 상위 3개 상품을 상품명과 함께 보여줘",
        "OS08": "오늘 상품별 매출액과 환불액을 조인해서 순매출액을 계산해줘",
    }
    assert {row["case_id"]: row["question"] for row in ORDER_SALES_HTTP_CASES} == expected_questions
    assert all("\ufffd" not in question for question in expected_questions.values())
    os08 = next(row for row in ORDER_SALES_HTTP_CASES if row["case_id"] == "OS08")
    assert os08["expected_rows"][0] == {
        "PRODUCT_ID": "P-300",
        "SALES_AMOUNT": 1000.0,
        "REFUND_AMOUNT": 300.0,
        "NET_SALES_AMOUNT": 700.0,
    }

    payload = {"contract_version": "source.inline.payload.v1", "datasets": {"orders": []}}
    wrapped = _json_input_tweak(payload)
    assert wrapped == payload
    assert wrapped is not payload


def test_domain_sessions_and_result_references_are_isolated() -> None:
    store = InMemoryStateStore()
    manufacturing_state, manufacturing_ref, _ = store.commit_execution(
        subject_id="same-user",
        session_id="domain:manufacturing",
        expected_version=0,
        result={"domain_id": "manufacturing", "rows": [{"PRODUCT_ID": "M1"}]},
        source_snapshots=[],
        next_state={"semantic_context": {"domain_id": "manufacturing"}, "last_question": "제조 질문"},
        ttl_seconds=3600,
    )
    sales_state, sales_ref, _ = store.commit_execution(
        subject_id="same-user",
        session_id="domain:order_sales",
        expected_version=0,
        result={"domain_id": "order_sales", "rows": [{"PRODUCT_ID": "P1"}]},
        source_snapshots=[],
        next_state={"semantic_context": {"domain_id": "order_sales"}, "last_question": "매출 질문"},
        ttl_seconds=3600,
    )
    assert manufacturing_state["state_version"] == sales_state["state_version"] == 1
    assert store.load_state("same-user", "domain:manufacturing")["semantic_context"]["domain_id"] == "manufacturing"
    assert store.load_state("same-user", "domain:order_sales")["semantic_context"]["domain_id"] == "order_sales"
    assert store.load_ref(manufacturing_ref["ref_id"], "same-user", "domain:manufacturing")["payload"]["domain_id"] == "manufacturing"
    assert store.load_ref(sales_ref["ref_id"], "same-user", "domain:order_sales")["payload"]["domain_id"] == "order_sales"
    with pytest.raises(ContractError) as crossed:
        store.load_ref(manufacturing_ref["ref_id"], "same-user", "domain:order_sales")
    assert crossed.value.code == "state_reference_forbidden"


def test_http_terminal_evidence_requires_message_api_and_gaia_hash_equivalence() -> None:
    digest = "c" * 64
    response = {
        "contract_version": "response.v1",
        "response_sha256": digest,
        "status": "ok",
        "state": {"state_version": 2, "executed_result_ref": "result:abc"},
        "trace": {
            "route": {"route": "deterministic"},
            "usage": {
                "intent_llm_calls": 0,
                "intent_retry_calls": 0,
                "answer_llm_calls": 0,
                "pandas_code_llm_calls": 0,
                "pandas_repair_llm_calls": 0,
            },
        },
    }
    payload = {
        "outputs": [
            {
                "outputs": [
                    {
                        "component_id": "message_presentation",
                        "component_display_name": "Message Presentation",
                        "results": {
                            "message": {
                                "session_metadata": {
                                    "contract_version": "response.message-link.v1",
                                    "response_sha256": digest,
                                }
                            }
                        },
                    },
                    {
                        "component_id": "gaia_output",
                        "component_display_name": "GaiA Output",
                        "results": {
                            "message": {
                                "data": {
                                    "gaia": {
                                        "answer": "ok",
                                        "metadata": {
                                            "contract_version": "gaia.metadata.v1",
                                            "response_sha256": digest,
                                        },
                                    },
                                }
                            }
                        },
                    },
                    {
                        "component_id": "api_response",
                        "component_display_name": "API Response",
                        "results": {"api_response": {"data": response}},
                    },
                ]
            }
        ]
    }
    evidence = extract_terminal_evidence(payload)
    assert evidence["terminal_equivalent"] is True
    assert evidence["canonical_response_sha256"] == digest
    assert evidence["state_version"] == 2
    assert evidence["usage"]["pandas_code_llm_calls"] == 0


def test_http_terminal_evidence_distinguishes_persistent_and_ephemeral_refs() -> None:
    digest = "d" * 64
    analysis_ref = "analysis_result:abcd1234"
    source_ref = "source_snapshot:abcd1234"
    persistent = {
        "contract_version": "response.v1",
        "response_sha256": digest,
        "status": "ok",
        "state": {"state_version": 1, "executed_result_ref": analysis_ref},
        "data_refs": [
            {"ref_id": analysis_ref, "role": "analysis_result"},
            {"ref_id": source_ref, "role": "source_snapshot"},
        ],
        "answer_sections": {
            "result_table": {"data_ref": analysis_ref},
            "downloads": [
                {"ref_id": analysis_ref, "role": "analysis_result", "url": ""},
                {"ref_id": source_ref, "role": "source_snapshot", "url": ""},
            ],
        },
        "trace": {"route": {}, "usage": {}},
    }
    persistent_evidence = extract_terminal_evidence({"api_response": persistent})
    contract = persistent_evidence["persistence_contract"]
    assert contract["state_present"] is True
    assert contract["data_ref_count"] == 2
    assert contract["answer_download_count"] == 2
    assert contract["all_data_ref_ids_valid"] is True
    assert contract["all_download_ref_ids_valid"] is True
    assert contract["download_refs_match_data_refs"] is True
    assert contract["one_analysis_result_ref"] is True
    assert contract["state_ref_matches_analysis_result"] is True
    assert contract["result_table_ref_matches_analysis_result"] is True

    ephemeral = json.loads(json.dumps(persistent))
    ephemeral["state"] = None
    ephemeral["data_refs"] = []
    ephemeral["answer_sections"]["result_table"]["data_ref"] = ""
    ephemeral["answer_sections"]["downloads"] = []
    ephemeral_evidence = extract_terminal_evidence({"api_response": ephemeral})
    ephemeral_contract = ephemeral_evidence["persistence_contract"]
    assert ephemeral_contract["state_present"] is False
    assert ephemeral_contract["data_ref_count"] == 0
    assert ephemeral_contract["answer_download_count"] == 0
    assert ephemeral_contract["one_analysis_result_ref"] is False
    assert ephemeral_contract["state_ref_matches_analysis_result"] is False
    assert ephemeral_contract["result_table_ref_matches_analysis_result"] is False


def test_specialized_functions_are_declarative_and_cannot_embed_code() -> None:
    safe = {
        "specialized_functions": [
            {
                "function_id": "sales.tax.v1",
                "version": 1,
                "execution_mode": "registered_standalone",
                "implementation_sha256": "d" * 64,
                "input_schema": {"amount": "number"},
                "output_schema": {"tax": "number"},
                "required_fields": ["amount"],
            }
        ]
    }
    assert validate_specialized_functions(safe) == []
    unsafe = json.loads(json.dumps(safe))
    unsafe["specialized_functions"][0]["code"] = "import pandas as pd"
    failures = validate_specialized_functions(unsafe)
    assert any("unexpected_keys:code" in item for item in failures)
    assert any("executable_key:code" in item for item in failures)
    assert any("executable_text" in item for item in failures)


def test_http_authoring_evidence_validates_hash_and_terminal_equivalence() -> None:
    from reference_runtime.canonical import sha256_json

    material = {
        "contract_version": "metadata.authoring.response.v1",
        "response_type": "metadata_authoring",
        "status": "ok",
        "stage": "prepared",
        "authoring_kind": "domain",
        "metadata_contract_mode": "domain_package_v2",
        "domain_id": "order_sales",
        "environment": "e2e_validation",
        "revision": 1,
        "candidate_id": "candidate:" + "a" * 64,
        "candidate_sha256": "a" * 64,
        "package_sha256": "b" * 64,
        "bundle_sha256": "c" * 64,
        "catalog_sha256": "d" * 64,
        "llm_usage": {"draft_llm_calls": 1, "repair_llm_calls": 0},
    }
    response = {**material, "response_sha256": sha256_json(material)}
    payload = {
        "outputs": [
            {
                "outputs": [
                    {
                        "component_id": "chat_output",
                        "component_display_name": "Chat Output",
                        "results": {
                            "message": {
                                "text": "Metadata prepare 완료",
                                "session_metadata": {
                                    "contract_version": "metadata.authoring.message-link.v1",
                                    "response_sha256": response["response_sha256"],
                                },
                            }
                        },
                    },
                    {
                        "component_id": "api_response",
                        "component_display_name": "API Response",
                        "results": {"api_response": {"data": response}},
                    },
                ]
            }
        ]
    }
    evidence = extract_authoring_evidence(payload)
    assert evidence["response_hash_valid"] is True
    assert evidence["terminal_equivalent"] is True
    assert evidence["draft_llm_calls"] == 1
