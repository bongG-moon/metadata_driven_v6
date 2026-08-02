from __future__ import annotations

import json
import runpy
from copy import deepcopy
from pathlib import Path

import pytest

from reference_runtime.canonical import ContractError, sha256_json
from reference_runtime.generic_v2_candidates import (
    build_generic_v2_candidate_bundle,
    resolve_generic_v2_intent,
)
from reference_runtime.generic_v2_planner import (
    compile_generic_v2_plan,
    validate_generic_v2_plan,
)
from reference_runtime.request_literals import build_request_capsule
from reference_runtime.typed_executor import TypedExecutor


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_INSTANT = "2026-08-01T09:00:00+09:00"


def _support_catalog() -> dict:
    fixture = runpy.run_path(str(ROOT / "tests" / "test_generic_v2_candidates.py"))
    return fixture["support_ticket_catalog"]()


def _rehash(catalog: dict) -> dict:
    catalog["catalog_sha256"] = sha256_json(
        {key: value for key, value in catalog.items() if key != "catalog_sha256"}
    )
    return catalog


def p1_time_scope_catalog() -> dict:
    """Synthetic v2 catalog for literal, projection and time-scope boundaries."""

    catalog = _support_catalog()
    common_fields = {
        "CASE_ID": {"aliases": ["티켓 번호"], "roles": ["project", "output"]},
        "TECH": {"aliases": ["기술"], "roles": ["filter", "project", "output"]},
        "QUEUE": {"aliases": ["큐", "지원 큐"], "roles": ["group", "project", "output"]},
        "WAIT_MINUTES": {
            "aliases": ["대기시간"],
            "roles": ["metric", "aggregate", "project", "output"],
        },
        "EXTRA_UNUSED": {"aliases": ["미사용"], "roles": ["project", "output"]},
    }
    catalog["datasets"] = {
        "ticket_current": {
            "key": "ticket_current",
            "display_name": "현재 지원 현황",
            "family": "case_fact",
            "time_scope": "current",
            "source_type": "dummy",
            "source_adapter": "dummy.case_current.v1",
            "query_ref": "query:case_current@1",
            "config_ref": "config:case_current@1",
            "date_policy": {},
            "parameters": {},
            "fields": deepcopy(common_fields),
        },
        "ticket_history": {
            "key": "ticket_history",
            "display_name": "지원 이력",
            "family": "case_fact",
            "time_scope": "history",
            "source_type": "dummy",
            "source_adapter": "dummy.case_history.v1",
            "query_ref": "query:case_history@1",
            "config_ref": "config:case_history@1",
            "date_policy": {
                "field": "OPEN_DATE",
                "timezone": "Asia/Seoul",
                "inclusive_start": True,
                "inclusive_end": True,
            },
            "parameters": {"DATE": {"type": "LocalDate", "required": False}},
            "fields": {
                **deepcopy(common_fields),
                "OPEN_DATE": {
                    "aliases": ["접수일"],
                    "roles": ["filter", "project", "output"],
                    "semantic_type": "LocalDate",
                },
            },
        },
    }
    catalog["fields"] = {
        "CASE_ID": {
            "canonical_field": "CASE_ID",
            "aliases": ["티켓 번호"],
            "dataset_keys": ["ticket_current", "ticket_history"],
            "roles": ["project", "output"],
        },
        "TECH": {
            "canonical_field": "TECH",
            "aliases": ["기술"],
            "dataset_keys": ["ticket_current", "ticket_history"],
            "roles": ["filter", "project", "output"],
            "semantic_type": "string",
        },
        "QUEUE": {
            "canonical_field": "QUEUE",
            "aliases": ["큐", "지원 큐"],
            "dataset_keys": ["ticket_current", "ticket_history"],
            "roles": ["group", "project", "output"],
        },
        "WAIT_MINUTES": {
            "canonical_field": "WAIT_MINUTES",
            "aliases": ["대기시간"],
            "dataset_keys": ["ticket_current", "ticket_history"],
            "roles": ["metric", "aggregate", "project", "output"],
            "semantic_type": "number",
        },
        "OPEN_DATE": {
            "canonical_field": "OPEN_DATE",
            "aliases": ["접수일"],
            "dataset_keys": ["ticket_history"],
            "roles": ["filter", "project", "output"],
            "semantic_type": "LocalDate",
        },
        "EXTRA_UNUSED": {
            "canonical_field": "EXTRA_UNUSED",
            "aliases": ["미사용"],
            "dataset_keys": ["ticket_current", "ticket_history"],
            "roles": ["project", "output"],
        },
    }
    catalog["metrics"] = {
        "WAIT_MINUTES": {
            "metric_id": "WAIT_MINUTES",
            "aliases": ["대기시간", "대기 분"],
            "aggregation": "sum",
            "source_binding": {"dataset_family": "case_fact", "field": "WAIT_MINUTES"},
            "source_field": "WAIT_MINUTES",
            "unit": "minute",
        }
    }
    catalog["grains"] = {
        "queue": {"grain_id": "queue", "aliases": ["큐별"], "keys": ["QUEUE"]}
    }
    catalog["relations"] = {}
    catalog["entity_groups"] = {}
    catalog["predicates"] = {}
    catalog["recipes"] = {
        "case.wait_by_queue": {
            "recipe_id": "case.wait_by_queue",
            "aliases": ["큐별 대기시간 합계"],
            "required_slots": [],
            "default_operation_template": {
                "op": "aggregate",
                "metric": "WAIT_MINUTES",
                "grain_id": "queue",
            },
        }
    }
    catalog["aliases"] = {
        "dataset:current": {
            "target_type": "dataset",
            "target_key": "ticket_current",
            "values": ["현재", "실시간", "현황"],
        },
        "dataset:history": {
            "target_type": "dataset",
            "target_key": "ticket_history",
            "values": ["이력", "과거"],
        },
        "field:QUEUE": {"target_type": "field", "target_key": "QUEUE", "values": ["큐"]},
        "metric:WAIT_MINUTES": {
            "target_type": "metric",
            "target_key": "WAIT_MINUTES",
            "values": ["대기시간"],
        },
        "grain:queue": {"target_type": "grain", "target_key": "queue", "values": ["큐별"]},
        "recipe:wait": {
            "target_type": "recipe",
            "target_key": "case.wait_by_queue",
            "values": ["큐별 대기시간 합계"],
        },
    }
    return _rehash(catalog)


def _request(question: str) -> dict:
    return build_request_capsule(
        question,
        session_id="generic-p1-validation-session-123456",
        subject_id="generic-p1-validator",
        reference_instant=REFERENCE_INSTANT,
    )


def _compile(catalog: dict, question: str) -> tuple[dict, dict, dict, dict]:
    request = _request(question)
    bundle = build_generic_v2_candidate_bundle(request, catalog)
    assert bundle["route_decision"]["route"] == "deterministic"
    intent, telemetry = resolve_generic_v2_intent(
        request,
        bundle,
        llm_callable=lambda _prompt: (_ for _ in ()).throw(AssertionError("unexpected LLM call")),
    )
    assert telemetry["intent_llm_calls"] == 0
    plan = compile_generic_v2_plan(intent, bundle, catalog, question=question)
    validate_generic_v2_plan(plan, catalog)
    return request, bundle, intent, plan


def _clauses(value: object) -> list[dict]:
    if not isinstance(value, dict):
        return []
    if value.get("op") == "all" and isinstance(value.get("clauses"), list):
        return [item for item in value["clauses"] if isinstance(item, dict)]
    return [value] if value.get("field") else []


def _execute(plan: dict, rows: list[dict]) -> dict:
    job = plan["retrieval_jobs"][0]
    result = TypedExecutor().execute(plan, {job["job_id"]: rows}).as_contract(plan)
    return result


def test_longest_metric_alias_selects_net_sales_only_and_keeps_dependencies_internal() -> None:
    package = json.loads(
        (ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "domain_package.json").read_text(
            encoding="utf-8"
        )
    )
    _, bundle, intent, plan = _compile(package["runtime_catalog"], "상품별 순매출을 보여줘")

    assert [item["identity"] for item in bundle["metric_candidates"]] == ["NET_SALES_AMOUNT"]
    assert intent["semantics"]["metric_refs"] == ["NET_SALES_AMOUNT"]
    assert plan["result_contract"]["columns"] == ["PRODUCT_ID", "NET_SALES_AMOUNT"]
    assert "SALES_AMOUNT" not in plan["result_contract"]["columns"]
    assert any(item.get("op") == "derive" and item.get("output_field") == "NET_SALES_AMOUNT" for item in plan["operations"])


def test_registered_literal_is_exact_in_job_pushdown_and_typed_filter_and_idempotent_at_execution() -> None:
    catalog = p1_time_scope_catalog()
    _, _bundle, intent, plan = _compile(
        catalog, "기술=ABC인 현재 티켓의 큐별 대기시간 합계를 보여줘"
    )
    literal = {"field": "TECH", "operator": "eq", "value": "ABC"}
    typed_literal = {**literal, "semantic_type": "string"}
    assert any(
        {key: clause.get(key) for key in literal} == literal
        for clause in intent["semantics"]["filter_refs"]
    )
    assert len(plan["retrieval_jobs"]) == 1
    job = plan["retrieval_jobs"][0]
    assert job["dataset_key"] == "ticket_current"
    assert _clauses(job["filters"]) == [typed_literal]
    filter_ops = [item for item in plan["operations"] if item.get("op") == "filter"]
    assert len(filter_ops) == 1
    assert _clauses(filter_ops[0]["where"]) == [typed_literal]
    assert set(job["required_fields"]) == {"TECH", "QUEUE", "WAIT_MINUTES"}

    rows = [
        {"CASE_ID": "C1", "TECH": "ABC", "QUEUE": "billing", "WAIT_MINUTES": 10, "EXTRA_UNUSED": "x"},
        {"CASE_ID": "C2", "TECH": "ABC", "QUEUE": "technical", "WAIT_MINUTES": 20, "EXTRA_UNUSED": "x"},
        {"CASE_ID": "C3", "TECH": "XYZ", "QUEUE": "billing", "WAIT_MINUTES": 100, "EXTRA_UNUSED": "x"},
    ]
    full = _execute(plan, rows)
    pushed_down = _execute(plan, [row for row in rows if row["TECH"] == "ABC"])
    assert full["rows"] == pushed_down["rows"]
    assert sorted(full["rows"], key=lambda row: row["QUEUE"]) == [
        {"QUEUE": "billing", "WAIT_MINUTES": 10},
        {"QUEUE": "technical", "WAIT_MINUTES": 20},
    ]


def test_required_fields_are_a_strict_registered_closure_for_formula_join_date_and_output() -> None:
    package = json.loads(
        (ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "domain_package.json").read_text(
            encoding="utf-8"
        )
    )
    _, _bundle, _intent, plan = _compile(
        package["runtime_catalog"], "2026-07-01 상품별 순매출을 보여줘"
    )
    jobs = {item["dataset_key"]: item for item in plan["retrieval_jobs"]}
    assert set(jobs) == {"orders", "refunds"}
    assert set(jobs["orders"]["required_fields"]) == {
        "ORDER_DATE",
        "ORDER_ID",
        "PRODUCT_ID",
        "SALES_AMOUNT",
    }
    assert set(jobs["refunds"]["required_fields"]) == {
        "ORDER_ID",
        "PRODUCT_ID",
        "REFUND_AMOUNT",
    }
    for dataset_key, job in jobs.items():
        registered = set(package["runtime_catalog"]["datasets"][dataset_key]["fields"])
        assert set(job["required_fields"]) <= registered


def test_same_family_current_and_history_selection_is_preserved_into_plan() -> None:
    catalog = p1_time_scope_catalog()
    _, _, _, current = _compile(catalog, "현재 큐별 대기시간 합계를 보여줘")
    _, _, _, history = _compile(catalog, "2026-07-15 큐별 대기시간 합계를 보여줘")
    current_job = current["retrieval_jobs"][0]
    history_job = history["retrieval_jobs"][0]
    assert current_job["dataset_key"] == "ticket_current"
    assert history_job["dataset_key"] == "ticket_history"
    assert history_job["parameters"] == {"DATE": "2026-07-15"}
    assert any(
        clause.get("field") == "OPEN_DATE"
        and clause.get("operator") == "eq"
        and clause.get("value") == "2026-07-15"
        for clause in _clauses(history_job["filters"])
    )
    assert "OPEN_DATE" in history_job["required_fields"]


def test_today_without_current_context_or_recipe_pin_is_not_deterministic() -> None:
    catalog = p1_time_scope_catalog()
    bundle = build_generic_v2_candidate_bundle(
        _request("오늘 큐별 대기시간 합계를 보여줘"), catalog
    )
    assert bundle["route_decision"]["route"] != "deterministic"


def test_filter_literal_for_a_field_absent_from_selected_dataset_fails_closed() -> None:
    catalog = p1_time_scope_catalog()
    del catalog["datasets"]["ticket_history"]["fields"]["TECH"]
    catalog["fields"]["TECH"]["dataset_keys"] = ["ticket_current"]
    _rehash(catalog)
    request = _request("2026-07-15 기술=ABC인 티켓의 큐별 대기시간 합계를 보여줘")
    bundle = build_generic_v2_candidate_bundle(request, catalog)
    if bundle["route_decision"]["route"] == "deterministic":
        intent, _ = resolve_generic_v2_intent(request, bundle)
        with pytest.raises(ContractError) as raised:
            compile_generic_v2_plan(intent, bundle, catalog, question=request["question"])
        assert raised.value.code == "metadata_dependency_error"
    else:
        assert bundle["route_decision"]["route"] in {"unsupported", "intent_llm"}


def test_intent_bundle_and_catalog_dependency_pins_fail_closed() -> None:
    catalog = p1_time_scope_catalog()
    question = "현재 큐별 대기시간 합계를 보여줘"
    request, bundle, intent, _plan = _compile(catalog, question)

    bad_intent_bundle_ref = deepcopy(intent)
    bad_intent_bundle_ref["candidate_bundle_sha256"] = "0" * 64
    bad_bundle = deepcopy(bundle)
    bad_bundle["bundle_sha256"] = "1" * 64
    bad_catalog = deepcopy(catalog)
    bad_catalog["catalog_sha256"] = "2" * 64
    bad_semantics = deepcopy(intent)
    bad_semantics["semantics"]["dimension_refs"] = []

    for changed_intent, changed_bundle, changed_catalog in (
        (bad_intent_bundle_ref, bundle, catalog),
        (intent, bad_bundle, catalog),
        (intent, bundle, bad_catalog),
        (bad_semantics, bundle, catalog),
    ):
        with pytest.raises(ContractError):
            compile_generic_v2_plan(
                changed_intent,
                changed_bundle,
                changed_catalog,
                question=str(request["question"]),
            )


def _frames_for_integrity_probe(plan: dict) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {}
    for job in plan.get("retrieval_jobs", []):
        row = {}
        for field in job.get("required_fields", []):
            if field.endswith(("DATE", "_DATE")):
                row[field] = "2026-08-01"
            elif field.endswith(("AMOUNT", "MINUTES")):
                row[field] = 1.0
            else:
                row[field] = "X"
        result[str(job["job_id"])] = [row]
    return result


def _assert_plan_tamper_blocked(plan: dict, catalog: dict) -> None:
    with pytest.raises(ContractError):
        validate_generic_v2_plan(plan, catalog)
    with pytest.raises(ContractError):
        TypedExecutor().execute(plan, _frames_for_integrity_probe(plan))


def test_plan_filter_job_and_required_field_tampering_with_old_fingerprint_fails_closed() -> None:
    catalog = p1_time_scope_catalog()
    _, _, _, plan = _compile(
        catalog, "기술=ABC인 현재 티켓의 큐별 대기시간 합계를 보여줘"
    )

    changed_filter = deepcopy(plan)
    filter_op = next(item for item in changed_filter["operations"] if item.get("op") == "filter")
    _clauses(filter_op["where"])[0]["value"] = "XYZ"

    changed_dataset = deepcopy(plan)
    changed_dataset["retrieval_jobs"][0]["dataset_key"] = "ticket_history"

    changed_required = deepcopy(plan)
    changed_required["retrieval_jobs"][0]["required_fields"].remove("TECH")

    for changed in (changed_filter, changed_dataset, changed_required):
        assert changed["plan_id"] == plan["plan_id"]
        assert changed["plan_fingerprint"] == plan["plan_fingerprint"]
        _assert_plan_tamper_blocked(changed, catalog)


def test_plan_compare_operator_tampering_with_old_fingerprint_fails_closed() -> None:
    package = json.loads(
        (ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "domain_package.json").read_text(
            encoding="utf-8"
        )
    )
    _, _, _, plan = _compile(
        package["runtime_catalog"], "오늘 매출액이 목표액보다 큰 상품만 보여줘"
    )
    changed = deepcopy(plan)
    compare = next(item for item in changed["operations"] if item.get("op") == "compare_fields")
    compare["operator"] = "lt"
    assert changed["plan_id"] == plan["plan_id"]
    assert changed["plan_fingerprint"] == plan["plan_fingerprint"]
    _assert_plan_tamper_blocked(changed, package["runtime_catalog"])


def test_legacy_compat_profile_cannot_be_spoofed_by_another_domain() -> None:
    from lfx.custom.eval import eval_custom_component_code

    source = (
        ROOT / "langflow_components" / "data_analysis" / "candidate_route_gate.py"
    ).read_text(encoding="utf-8")
    component_cls = eval_custom_component_code(source)
    profile_fn = component_cls.select_route.__globals__["_planner_profile"]
    embedded = component_cls.select_route.__globals__["EMBEDDED_RUNTIME_CATALOG"]
    package = json.loads(
        (ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "domain_package.json").read_text(
            encoding="utf-8"
        )
    )
    spoof = deepcopy(package["runtime_catalog"])
    spoof["domain_id"] = "spoofed_other_domain"
    spoof["recipes"]["spoof.legacy"] = {
        "recipe_id": "spoof.legacy",
        "aliases": ["spoof"],
        "required_slots": [],
        "default_operation_template": {"op": "legacy_op"},
    }
    spoof["output_profile"] = {
        **deepcopy(spoof.get("output_profile") or {}),
        "planner_profile": "legacy_v1_compat",
        "legacy_catalog_sha256": embedded["catalog_sha256"],
    }
    _rehash(spoof)
    with pytest.raises(Exception) as raised:
        profile_fn(spoof)
    assert getattr(raised.value, "code", "") == "unsupported_operation"
