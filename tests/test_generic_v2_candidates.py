from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from reference_runtime.canonical import ContractError, sha256_json
from reference_runtime.generic_v2_candidates import (
    build_generic_v2_candidate_bundle,
    build_generic_v2_intent_prompt,
    normalize_generic_v2_intent,
    resolve_generic_v2_intent,
    validate_generic_v2_candidate_bundle,
)
from reference_runtime.generic_v2_planner import compile_generic_v2_plan
from reference_runtime.request_literals import build_request_capsule
from reference_runtime.typed_executor import TypedExecutor


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_INSTANT = "2026-08-01T09:00:00+09:00"


def support_ticket_catalog() -> dict:
    """A third-domain fixture deliberately unrelated to the shipped packs."""

    catalog = {
        "contract_version": "metadata.runtime.catalog.v2",
        "domain_id": "support_tickets",
        "environment": "test",
        "revision": 1,
        "compiler_version": "test.compiler.v1",
        "display_name": "고객 지원 티켓",
        "description": "지원 요청, 담당자, 대기시간 조회",
        "locale": "ko-KR",
        "timezone": "Asia/Seoul",
        "datasets": {
            "ticket_events": {
                "key": "ticket_events",
                "display_name": "지원 요청",
                "family": "case_fact",
                "source_type": "dummy",
                "source_adapter": "dummy.case_fact.v1",
                "query_ref": "query:case_fact@1",
                "config_ref": "config:case_fact@1",
                "date_policy": {"field": "OPEN_DATE", "timezone": "Asia/Seoul"},
                "fields": {
                    "CASE_ID": {"aliases": ["티켓 번호"], "roles": ["join", "project", "output"]},
                    "OPEN_DATE": {"aliases": ["접수일"], "roles": ["filter", "project", "output"]},
                    "QUEUE": {"aliases": ["큐", "지원 큐"], "roles": ["group", "filter", "project", "output"]},
                    "OWNER_ID": {"aliases": ["담당자 ID"], "roles": ["join", "project", "output"]},
                    "WAIT_MINUTES": {"aliases": ["대기시간"], "roles": ["metric", "aggregate", "rank", "project", "output"]},
                    "SUBJECT": {"aliases": ["제목"], "roles": ["project", "output"]},
                },
            },
            "agent_directory": {
                "key": "agent_directory",
                "display_name": "담당자 디렉터리",
                "family": "owner_directory",
                "source_type": "dummy",
                "source_adapter": "dummy.owner_directory.v1",
                "query_ref": "query:owner_directory@1",
                "config_ref": "config:owner_directory@1",
                "date_policy": {},
                "fields": {
                    "OWNER_ID": {"aliases": ["담당자 ID"], "roles": ["join", "project", "output"]},
                    "OWNER_NAME": {"aliases": ["담당자 이름"], "roles": ["group", "project", "output"]},
                },
            },
            "ticket_view": {
                "key": "ticket_view",
                "display_name": "티켓 보기",
                "family": "case_view",
                "source_type": "dummy",
                "source_adapter": "dummy.case_view.v1",
                "query_ref": "query:case_view@1",
                "config_ref": "config:case_view@1",
                "date_policy": {"field": "OPEN_DATE", "timezone": "Asia/Seoul"},
                "fields": {
                    "CASE_ID": {"aliases": ["티켓 번호"], "roles": ["project", "output"]},
                    "OPEN_DATE": {"aliases": ["접수일"], "roles": ["filter", "project", "output"]},
                    "OWNER_NAME": {"aliases": ["담당자 이름"], "roles": ["group", "project", "output"]},
                    "SUBJECT": {"aliases": ["제목"], "roles": ["project", "output"]},
                },
            },
        },
        "fields": {
            "CASE_ID": {"canonical_field": "CASE_ID", "aliases": ["티켓 번호"], "dataset_keys": ["ticket_events", "ticket_view"], "roles": ["join", "project", "output"]},
            "OPEN_DATE": {"canonical_field": "OPEN_DATE", "aliases": ["접수일"], "dataset_keys": ["ticket_events", "ticket_view"], "roles": ["filter", "project", "output"]},
            "QUEUE": {"canonical_field": "QUEUE", "aliases": ["큐", "지원 큐"], "dataset_keys": ["ticket_events"], "roles": ["group", "filter", "project", "output"]},
            "OWNER_ID": {"canonical_field": "OWNER_ID", "aliases": ["담당자 ID"], "dataset_keys": ["ticket_events", "agent_directory"], "roles": ["join", "project", "output"]},
            "OWNER_NAME": {"canonical_field": "OWNER_NAME", "aliases": ["담당자 이름"], "dataset_keys": ["agent_directory", "ticket_view"], "roles": ["group", "project", "output"]},
            "WAIT_MINUTES": {"canonical_field": "WAIT_MINUTES", "aliases": ["대기시간"], "dataset_keys": ["ticket_events"], "roles": ["metric", "aggregate", "rank", "project", "output"]},
            "SUBJECT": {"canonical_field": "SUBJECT", "aliases": ["제목"], "dataset_keys": ["ticket_events", "ticket_view"], "roles": ["project", "output"]},
        },
        "metrics": {
            "WAIT_MINUTES": {
                "metric_id": "WAIT_MINUTES",
                "aliases": ["대기시간", "대기 분"],
                "aggregation": "sum",
                "source_binding": {"dataset_family": "case_fact", "field": "WAIT_MINUTES"},
                "source_field": "WAIT_MINUTES",
                "unit": "minute",
            }
        },
        "entity_groups": {
            "open_cases": {
                "group_id": "open_cases",
                "aliases": ["미해결 티켓"],
                "entity": "CASE_ID",
                "selection": {"operator": "registered_predicate", "predicate_id": "is_open"},
            }
        },
        "grains": {
            "queue": {"grain_id": "queue", "aliases": ["큐별"], "keys": ["QUEUE"]},
            "case": {"grain_id": "case", "aliases": ["티켓별"], "keys": ["CASE_ID"]},
        },
        "relations": {
            "case_owner": {
                "relation_id": "case_owner",
                "aliases": ["담당자 연결"],
                "left_dataset": "ticket_events",
                "right_dataset": "agent_directory",
                "left_keys": ["OWNER_ID"],
                "right_keys": ["OWNER_ID"],
                "join_type": "left",
                "cardinality": "many_to_one",
                "null_key_policy": "never_match",
                "multi_match_policy": "fail",
            }
        },
        "orderings": {},
        "predicates": {"is_open": {"predicate_id": "is_open", "field": "STATUS", "operator": "neq", "value": "closed"}},
        "recipes": {
            "case.rank_wait": {
                "recipe_id": "case.rank_wait",
                "aliases": ["대기시간 상위", "대기시간 하위"],
                "required_slots": ["date_scope", "rank_direction", "rank_limit"],
                "default_operation_template": {
                    "op": "rank",
                    "metric": "WAIT_MINUTES",
                    "grain_id": "queue",
                    "include_ties": True,
                    "stable_tie_break": ["QUEUE"],
                },
            },
            "case.view_projection": {
                "recipe_id": "case.view_projection",
                "aliases": ["티켓 조회"],
                "required_slots": ["project_fields"],
                "default_operation_template": {
                    "op": "project",
                    "dataset_key": "ticket_view",
                    "allowed_fields": ["CASE_ID", "OPEN_DATE", "OWNER_NAME", "SUBJECT"],
                    "fields": ["CASE_ID", "OWNER_NAME"],
                },
            },
            "case.owner_join": {
                "recipe_id": "case.owner_join",
                "aliases": ["티켓 조회"],
                "required_slots": [],
                "default_operation_template": {
                    "op": "join",
                    "relation_id": "case_owner",
                    "next": {"op": "project", "allowed_fields": ["CASE_ID", "OWNER_NAME", "SUBJECT"]},
                },
            },
        },
        "aliases": {
            "dataset:ticket_events": {"target_type": "dataset", "target_key": "ticket_events", "values": ["지원 요청"]},
            "dataset:agent_directory": {"target_type": "dataset", "target_key": "agent_directory", "values": ["담당자 디렉터리"]},
            "dataset:ticket_view": {"target_type": "dataset", "target_key": "ticket_view", "values": ["티켓 보기"]},
            "field:CASE_ID": {"target_type": "field", "target_key": "CASE_ID", "values": ["티켓 번호"]},
            "field:QUEUE": {"target_type": "field", "target_key": "QUEUE", "values": ["큐", "지원 큐"]},
            "field:OWNER_NAME": {"target_type": "field", "target_key": "OWNER_NAME", "values": ["담당자 이름"]},
            "field:SUBJECT": {"target_type": "field", "target_key": "SUBJECT", "values": ["제목"]},
            "metric:WAIT_MINUTES": {"target_type": "metric", "target_key": "WAIT_MINUTES", "values": ["대기시간", "대기 분"]},
            "grain:queue": {"target_type": "grain", "target_key": "queue", "values": ["큐별"]},
            "recipe:rank": {"target_type": "recipe", "target_key": "case.rank_wait", "values": ["대기시간 상위", "대기시간 하위"]},
            "recipe:view": {"target_type": "recipe", "target_key": "case.view_projection", "values": ["티켓 조회"]},
            "recipe:owner": {"target_type": "recipe", "target_key": "case.owner_join", "values": ["티켓 조회"]},
        },
        "prompt_extensions": {"intent": "등록된 지원 티켓 후보만 선택한다.", "answer": "시간 단위와 큐 기준을 표시한다."},
        "specialized_functions": [],
        "output_profile": {"default_row_limit": 20, "null_label": "-"},
        "catalog_sha256": "",
    }
    catalog["catalog_sha256"] = sha256_json({key: value for key, value in catalog.items() if key != "catalog_sha256"})
    return catalog


def request(question: str, *, state_ref: str = "") -> dict:
    return build_request_capsule(
        question,
        session_id="support-session",
        subject_id="support-user",
        reference_instant=REFERENCE_INSTANT,
        previous_state_ref=state_ref,
    )


def test_support_ticket_top_n_metric_and_grain_is_unique_complete_and_zero_llm() -> None:
    catalog = support_ticket_catalog()
    capsule = request("오늘 큐별 대기시간 상위 2개를 보여줘")
    bundle = build_generic_v2_candidate_bundle(capsule, catalog)

    assert bundle["route_decision"]["route"] == "deterministic"
    assert bundle["route_decision"]["reason_code"] == "unique_complete_selection"
    assert len(bundle["intent_candidates"]) == 1
    semantics = bundle["intent_candidates"][0]["semantics"]
    assert semantics["metric_refs"] == ["WAIT_MINUTES"]
    assert semantics["dimension_refs"] == ["QUEUE"]
    assert semantics["grain_refs"] == ["queue"]
    assert semantics["rank"] == {"mode": "top", "limit": 2}
    assert semantics["recipe_refs"] == ["case.rank_wait"]

    def forbidden_model(_prompt: str) -> str:
        raise AssertionError("deterministic route must not call a model")

    intent, telemetry = resolve_generic_v2_intent(capsule, bundle, llm_callable=forbidden_model)
    assert intent["semantics"] == semantics
    assert intent["intent_generator"] == "deterministic"
    assert telemetry["intent_llm_calls"] == 0


def test_support_ticket_join_projection_recipe_tie_routes_to_selection_only_llm() -> None:
    catalog = support_ticket_catalog()
    capsule = request("티켓 조회해줘")
    bundle = build_generic_v2_candidate_bundle(capsule, catalog)

    assert bundle["route_decision"]["route"] == "intent_llm"
    assert bundle["route_decision"]["reason_code"] == "ambiguous_candidate_selection"
    assert len(bundle["intent_candidates"]) == 2
    assert {item["semantics"]["analysis_kind"] for item in bundle["intent_candidates"]} == {"join", "projection"}
    assert all(set(card) == {
        "candidate_id",
        "description",
        "analysis_kind",
        "metric_refs",
        "dimension_refs",
        "recipe_refs",
        "function_refs",
        "unresolved_slots",
    } for card in bundle["prompt_cards"])
    selected_id = next(
        item["candidate_id"]
        for item in bundle["intent_candidates"]
        if item["semantics"]["analysis_kind"] == "join"
    )
    seen_prompts: list[str] = []

    def choose_join(prompt: str) -> str:
        seen_prompts.append(prompt)
        return json.dumps({"intent_candidate_id": selected_id})

    intent, telemetry = resolve_generic_v2_intent(capsule, bundle, llm_callable=choose_join)
    assert intent["intent_candidate_id"] == selected_id
    assert intent["intent_generator"] == "llm"
    assert telemetry["intent_llm_calls"] == 1
    assert len(seen_prompts) == 1
    assert "default_operation_template" not in seen_prompts[0]


def test_projection_cue_disambiguates_to_registered_projection_recipe() -> None:
    catalog = support_ticket_catalog()
    capsule = request("티켓 번호와 제목 컬럼만 보여줘")
    bundle = build_generic_v2_candidate_bundle(capsule, catalog)

    assert bundle["route_decision"]["route"] == "deterministic"
    semantics = bundle["intent_candidates"][0]["semantics"]
    assert semantics["analysis_kind"] == "projection"
    assert semantics["field_refs"] == ["CASE_ID", "SUBJECT"]
    assert semantics["recipe_refs"] == ["case.view_projection"]


def test_unknown_or_predictive_question_fails_closed_without_model_candidate() -> None:
    catalog = support_ticket_catalog()
    for question in ("등록되지 않은 만족도 점수를 알려줘", "다음 주 해결 시간을 예측해줘"):
        capsule = request(question)
        bundle = build_generic_v2_candidate_bundle(capsule, catalog)
        assert bundle["route_decision"]["route"] == "unsupported"
        assert bundle["intent_candidates"] == []
        with pytest.raises(ContractError) as raised:
            resolve_generic_v2_intent(capsule, bundle, llm_callable=lambda _prompt: "never")
        assert raised.value.code == "unsupported_operation"


def test_bundle_hash_route_proof_prompt_cards_and_selection_are_fail_closed() -> None:
    catalog = support_ticket_catalog()
    capsule = request("티켓 조회해줘")
    bundle = build_generic_v2_candidate_bundle(capsule, catalog)
    validate_generic_v2_candidate_bundle(bundle, catalog)

    changed_semantics = deepcopy(bundle)
    changed_semantics["intent_candidates"][0]["semantics"]["metric_refs"] = ["UNKNOWN_METRIC"]
    with pytest.raises(ContractError):
        validate_generic_v2_candidate_bundle(changed_semantics, catalog)

    changed_card = deepcopy(bundle)
    changed_card["prompt_cards"][0]["extra"] = "not allowed"
    with pytest.raises(ContractError):
        validate_generic_v2_candidate_bundle(changed_card, catalog)

    changed_proof = deepcopy(bundle)
    changed_proof["route_decision"]["eligibility_proof_sha256"] = "0" * 64
    with pytest.raises(ContractError):
        validate_generic_v2_candidate_bundle(changed_proof, catalog)

    with pytest.raises(ContractError) as unknown:
        normalize_generic_v2_intent(capsule, bundle, selected_candidate_id="intent:not-registered")
    assert unknown.value.code == "intent_contract_error"


def test_runtime_bundle_has_one_canonical_shape_not_legacy_projection() -> None:
    catalog = support_ticket_catalog()
    bundle = build_generic_v2_candidate_bundle(request("오늘 큐별 대기시간 상위 2개를 보여줘"), catalog)

    assert "intent_candidates" in bundle
    assert "route_decision" in bundle
    assert "prompt_cards" in bundle
    assert "candidates" not in bundle
    assert "metadata_bundle_sha256" not in bundle
    assert "operator_registry_sha256" not in bundle
    assert bundle["bundle_sha256"] == sha256_json({
        "request_id": bundle["request_id"],
        "catalog_sha256": bundle["catalog_sha256"],
        "dataset_candidates": bundle["dataset_candidates"],
        "field_candidates": bundle["field_candidates"],
        "metric_candidates": bundle["metric_candidates"],
        "entity_group_candidates": bundle["entity_group_candidates"],
        "grain_candidates": bundle["grain_candidates"],
        "relation_candidates": bundle["relation_candidates"],
        "recipe_candidates": bundle["recipe_candidates"],
        "function_candidates": bundle["function_candidates"],
        "intent_candidates": bundle["intent_candidates"],
        "prompt_cards": bundle["prompt_cards"],
    })


def test_generic_module_contains_no_shipped_domain_identifiers_or_code_generation_lane() -> None:
    source = (ROOT / "reference_runtime" / "generic_v2_candidates.py").read_text(encoding="utf-8")
    forbidden = (
        "order_sales",
        "manufacturing",
        "SALES_AMOUNT",
        "PRODUCT_ID",
        "OPER_NAME",
        "pandas",
        "exec(",
        "eval(",
    )
    assert not {value for value in forbidden if value in source}


def test_intent_prompt_is_available_only_for_llm_route() -> None:
    catalog = support_ticket_catalog()
    ambiguous_request = request("티켓 조회해줘")
    ambiguous = build_generic_v2_candidate_bundle(ambiguous_request, catalog)
    assert "intent_candidate_id" in build_generic_v2_intent_prompt(ambiguous_request, ambiguous)

    deterministic_request = request("오늘 큐별 대기시간 상위 2개를 보여줘")
    deterministic = build_generic_v2_candidate_bundle(deterministic_request, catalog)
    with pytest.raises(ContractError):
        build_generic_v2_intent_prompt(deterministic_request, deterministic)


def test_compiled_structured_alias_values_route_a_representative_existing_domain_question() -> None:
    catalog = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "manufacturing"
            / "compiled"
            / "runtime_catalog.v2.json"
        ).read_text(encoding="utf-8")
    )
    capsule = build_request_capsule(
        # Relative "오늘" alone is intentionally ambiguous when a family has
        # current and history datasets.  "오늘 생산" is the registered dataset
        # alias that seals the current source without domain-specific parsing.
        "오늘 생산에서 MCP NO가 L-267로 시작하는 제품의 INPUT 수량 알려줘",
        session_id="compiled-alias-regression",
        subject_id="test-user",
        reference_instant=REFERENCE_INSTANT,
    )
    bundle = build_generic_v2_candidate_bundle(capsule, catalog)

    assert bundle["route_decision"]["route"] == "deterministic"
    assert {item["identity"] for item in bundle["metric_candidates"]} == {"INPUT_QTY"}
    assert {item["identity"] for item in bundle["field_candidates"]} == {"MCP_NO"}
    semantics = bundle["intent_candidates"][0]["semantics"]
    assert semantics["metric_refs"] == ["INPUT_QTY"]
    assert semantics["dataset_refs"] == ["production_today"]
    assert semantics["filter_refs"] == [
        {
            "candidate_id": "token:MCP_NO:starts_with:L-267",
            "field": "MCP_NO",
            "operator": "starts_with",
            "value": "L-267",
        }
    ]


def _order_sales_execution(question: str) -> tuple[dict, dict, dict]:
    catalog = json.loads(
        (ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "runtime_catalog.v2.json").read_text(
            encoding="utf-8"
        )
    )
    samples = json.loads(
        (ROOT / "metadata" / "domain_packs" / "order_sales" / "sample_rows.json").read_text(encoding="utf-8")
    )["datasets"]
    capsule = build_request_capsule(
        question,
        session_id="target-comparison-direct-0001",
        subject_id="test-user",
        reference_instant="2026-07-01T09:00:00+09:00",
    )
    bundle = build_generic_v2_candidate_bundle(capsule, catalog)
    intent, telemetry = resolve_generic_v2_intent(capsule, bundle)
    assert telemetry["intent_llm_calls"] == 0
    plan = compile_generic_v2_plan(intent, bundle, catalog, question=question)
    frames: dict[str, dict] = {}
    for job in plan["retrieval_jobs"]:
        dataset = catalog["datasets"][job["dataset_key"]]
        rows = [
            {
                canonical: row.get(binding["physical_column"])
                for canonical, binding in dataset["fields"].items()
            }
            for row in samples[job["dataset_key"]]
        ]
        frames[f"source:{job['job_id']}"] = {"rows": rows, "columns": list(dataset["fields"])}
    result = TypedExecutor().execute(plan, frames).as_contract(plan)
    return intent, plan, result


def test_target_achievement_is_join_derive_projection_without_implicit_comparison_filter() -> None:
    intent, plan, result = _order_sales_execution("상품별 목표 대비 매출 달성률을 보여줘")
    assert intent["semantics"]["analysis_kind"] == "join"
    assert "comparison_operator" not in intent["semantics"]
    assert [job["dataset_key"] for job in plan["retrieval_jobs"]] == ["orders", "targets"]
    assert "compare_fields" not in [operation["op"] for operation in plan["operations"]]
    assert "derive" in [operation["op"] for operation in plan["operations"]]
    assert result["rows"] == [
        {"PRODUCT_ID": "P-100", "ACHIEVEMENT_RATE": 125.0},
        {"PRODUCT_ID": "P-200", "ACHIEVEMENT_RATE": 125.0},
        {"PRODUCT_ID": "P-300", "ACHIEVEMENT_RATE": 100.0},
        {"PRODUCT_ID": "P-400", "ACHIEVEMENT_RATE": 40.0},
    ]


@pytest.mark.parametrize(
    ("question", "expected_columns"),
    [
        (
            "오늘 상품별 매출액과 환불액을 조인해서 순매출액을 계산해줘",
            ["PRODUCT_ID", "SALES_AMOUNT", "REFUND_AMOUNT", "NET_SALES_AMOUNT"],
        ),
        (
            "오늘 상품별 매출액과 목표액, 달성률을 보여줘",
            ["PRODUCT_ID", "SALES_AMOUNT", "TARGET_AMOUNT", "ACHIEVEMENT_RATE"],
        ),
    ],
)
def test_explicit_metric_enumeration_keeps_formula_dependencies_visible(
    question: str,
    expected_columns: list[str],
) -> None:
    intent, _plan, result = _order_sales_execution(question)

    assert intent["semantics"]["metric_refs"] == expected_columns[1:]
    assert result["columns"] == expected_columns


def test_reverse_optional_relation_projection_uses_registered_execution_cardinality() -> None:
    _intent, plan, result = _order_sales_execution(
        "오늘 환불액이 0보다 큰 상품의 상품명과 환불액만 보여줘"
    )

    joins = [operation for operation in plan["operations"] if operation["op"] == "join"]
    refunds_join = next(operation for operation in joins if operation["relation_id"] == "orders_refunds")
    assert refunds_join["relation_direction"] == "reverse"
    assert refunds_join["registered_cardinality"] == "one_to_zero_or_one"
    assert refunds_join["cardinality"] == "one_to_one"
    assert result["columns"] == ["PRODUCT_NAME", "REFUND_AMOUNT"]
    assert all(float(row["REFUND_AMOUNT"]) > 0 for row in result["rows"])


def test_explicit_greater_than_question_is_the_only_comparison_filter_lane() -> None:
    intent, plan, result = _order_sales_execution("오늘 매출액이 목표액보다 큰 상품만 보여줘")
    assert intent["semantics"]["analysis_kind"] == "compare_fields"
    assert intent["semantics"]["comparison_operator"] == "gt"
    comparisons = [operation for operation in plan["operations"] if operation["op"] == "compare_fields"]
    assert len(comparisons) == 1
    assert comparisons[0]["operator"] == "gt"
    assert result["rows"] == [
        {"PRODUCT_ID": "P-100", "SALES_AMOUNT": 2500, "TARGET_AMOUNT": 2000},
        {"PRODUCT_ID": "P-200", "SALES_AMOUNT": 2500, "TARGET_AMOUNT": 2000},
    ]
