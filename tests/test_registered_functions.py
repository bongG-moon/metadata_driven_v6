from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path

import pytest

from reference_runtime.canonical import ContractError, sha256_json
from reference_runtime.contracts import validate_contract
from reference_runtime.generic_v2_candidates import (
    build_generic_v2_candidate_bundle,
    resolve_generic_v2_intent,
)
from reference_runtime.generic_v2_planner import (
    compile_generic_v2_plan,
    validate_generic_v2_plan,
)
from reference_runtime.registered_functions import (
    build_registered_call_operation,
    registered_function_descriptor,
    validate_registered_function_card,
)
from reference_runtime.request_literals import build_request_capsule
from reference_runtime.typed_executor import TypedExecutor


ROOT = Path(__file__).resolve().parents[1]
FUNCTION_ID = "core.trim_and_match_tokens"
FUNCTION_VERSION = 1


def registered_card(
    *,
    timeout_ms: int = 1000,
    max_input_rows: int = 100,
    max_output_rows: int = 100,
    max_output_bytes: int = 100_000,
) -> dict:
    descriptor = registered_function_descriptor(FUNCTION_ID, FUNCTION_VERSION)
    return {
        "function_id": FUNCTION_ID,
        "version": FUNCTION_VERSION,
        "execution_mode": "registered_standalone",
        "implementation_sha256": descriptor["implementation_sha256"],
        "input_schema": descriptor["input_schema"],
        "output_schema": descriptor["output_schema"],
        "required_fields": ["LABEL"],
        "limits": {
            "timeout_ms": timeout_ms,
            "max_input_rows": max_input_rows,
            "max_output_rows": max_output_rows,
            "max_output_bytes": max_output_bytes,
        },
        "failure_policy": "fail_closed",
        "aliases": ["priority labels"],
        "call_template": {
            "dataset_ref": "records",
            "field_ref": "LABEL",
            "parameters": {
                "tokens": ["priority"],
                "operator": "equals",
                "match_mode": "any",
                "case_sensitive": False,
            },
            "output_fields": ["RECORD_ID", "LABEL"],
        },
    }


def generic_catalog(card: dict | None = None) -> dict:
    catalog = {
        "contract_version": "metadata.runtime.catalog.v2",
        "domain_id": "generic_records",
        "environment": "test",
        "revision": 1,
        "compiler_version": "test.compiler.v1",
        "display_name": "Generic records",
        "description": "Domain-neutral registered function fixture",
        "locale": "en-US",
        "timezone": "UTC",
        "datasets": {
            "records": {
                "key": "records",
                "display_name": "Records",
                "family": "record_fact",
                "source_type": "dummy",
                "source_adapter": "dummy.records.v1",
                "query_ref": "query:records@1",
                "config_ref": "config:records@1",
                "date_policy": {},
                "fields": {
                    "RECORD_ID": {"aliases": ["record id"], "roles": ["project", "output"]},
                    "LABEL": {"aliases": ["label"], "roles": ["filter", "project", "output"]},
                },
            }
        },
        "fields": {
            "RECORD_ID": {
                "canonical_field": "RECORD_ID",
                "aliases": ["record id"],
                "dataset_keys": ["records"],
                "roles": ["project", "output"],
                "semantic_type": "identifier",
            },
            "LABEL": {
                "canonical_field": "LABEL",
                "aliases": ["label"],
                "dataset_keys": ["records"],
                "roles": ["filter", "project", "output"],
                "semantic_type": "string",
            },
        },
        "metrics": {},
        "entity_groups": {},
        "grains": {},
        "relations": {},
        "orderings": {},
        "predicates": {},
        "recipes": {},
        "aliases": {},
        "prompt_extensions": {"intent": "", "answer": ""},
        "specialized_functions": [deepcopy(card or registered_card())],
        "output_profile": {"default_row_limit": 20},
        "catalog_sha256": "",
    }
    catalog["catalog_sha256"] = sha256_json(
        {key: value for key, value in catalog.items() if key != "catalog_sha256"}
    )
    return catalog


def request() -> dict:
    return build_request_capsule(
        "priority labels show",
        session_id="registered-function-session",
        subject_id="registered-function-user",
        reference_instant="2026-08-02T09:00:00+00:00",
    )


def test_registered_card_and_operation_are_closed_schema_validated() -> None:
    card = validate_registered_function_card(registered_card())
    operation = build_registered_call_operation(
        card,
        operation_id="op_registered",
        input_ref="source:records",
    )

    validate_contract(card, "registered-function-card.schema.json")
    validate_contract(operation, "registered-call.schema.json")
    validate_contract(generic_catalog(card), "runtime-catalog-v2.schema.json")

    unexpected = deepcopy(card)
    unexpected["source"] = "return rows"
    with pytest.raises(ContractError) as raised:
        validate_registered_function_card(unexpected)
    assert raised.value.code == "plan_contract_error"


def test_natural_language_function_candidate_compiles_and_executes_without_llm() -> None:
    catalog = generic_catalog()
    capsule = request()
    bundle = build_generic_v2_candidate_bundle(capsule, catalog)
    validate_contract(bundle, "resolved-candidate-bundle.schema.json")

    assert bundle["route_decision"]["route"] == "deterministic"
    assert len(bundle["function_candidates"]) == 1
    semantics = bundle["intent_candidates"][0]["semantics"]
    assert semantics["analysis_kind"] == "registered_call"
    assert semantics["function_refs"] == [f"{FUNCTION_ID}@{FUNCTION_VERSION}"]

    def forbidden_model(_prompt: str) -> str:
        raise AssertionError("a unique registered function candidate must not call an LLM")

    intent, telemetry = resolve_generic_v2_intent(
        capsule,
        bundle,
        llm_callable=forbidden_model,
    )
    assert telemetry["intent_llm_calls"] == 0

    plan = compile_generic_v2_plan(intent, bundle, catalog, question=capsule["question"])
    validate_generic_v2_plan(plan, catalog)
    validate_contract(plan, "analysis-plan.schema.json")
    registered = next(operation for operation in plan["operations"] if operation["op"] == "registered_call")
    assert registered["contract_version"] == "registered_call.v1"
    assert registered["required_fields"] == ["LABEL"]
    assert plan["retrieval_jobs"][0]["required_fields"] == ["LABEL", "RECORD_ID"]

    result = TypedExecutor().execute(
        plan,
        {
            plan["retrieval_jobs"][0]["job_id"]: [
                {"RECORD_ID": "r1", "LABEL": " priority "},
                {"RECORD_ID": "r2", "LABEL": "PRIORITY"},
                {"RECORD_ID": "r3", "LABEL": "normal"},
                {"RECORD_ID": "r4", "LABEL": None},
            ]
        },
    )
    assert result.rows == [
        {"RECORD_ID": "r1", "LABEL": " priority "},
        {"RECORD_ID": "r2", "LABEL": "PRIORITY"},
    ]
    assert [item["operator_id"] for item in result.operation_trace] == [
        "registered_call.v1",
        "project.v1",
    ]


def test_unregistered_or_hash_mismatched_function_fails_closed() -> None:
    wrong_hash = registered_card()
    wrong_hash["implementation_sha256"] = "0" * 64
    with pytest.raises(ContractError) as hash_error:
        build_generic_v2_candidate_bundle(request(), generic_catalog(wrong_hash))
    assert hash_error.value.code == "unsupported_operation"

    operation = build_registered_call_operation(
        registered_card(),
        operation_id="op_registered",
        input_ref="source:records",
    )
    operation["function_ref"]["function_id"] = "core.not_registered"
    with pytest.raises(ContractError) as identity_error:
        TypedExecutor().execute(
            {
                "plan_id": "plan:test",
                "operations": [operation],
                "result_operation_id": "op_registered",
                "result_contract": {"columns": [], "ordering": []},
                "lineage": {},
            },
            {"records": [{"LABEL": "priority"}]},
        )
    assert identity_error.value.code == "unsupported_operation"


@pytest.mark.parametrize(
    "card",
    [
        registered_card(max_input_rows=1),
        registered_card(max_output_rows=1),
        registered_card(max_output_bytes=1),
    ],
)
def test_registered_function_limits_fail_closed(card: dict) -> None:
    operation = build_registered_call_operation(
        card,
        operation_id="op_registered",
        input_ref="source:records",
    )
    with pytest.raises(ContractError) as raised:
        TypedExecutor().execute(
            {
                "plan_id": "plan:test",
                "operations": [operation],
                "result_operation_id": "op_registered",
                "result_contract": {"columns": [], "ordering": []},
                "lineage": {},
            },
            {
                "records": [
                    {"LABEL": "priority"},
                    {"LABEL": " priority "},
                ]
            },
        )
    assert raised.value.code == "execution_memory_limit_exceeded"


def test_registered_function_timeout_ceiling_is_enforced() -> None:
    with pytest.raises(ContractError) as raised:
        validate_registered_function_card(registered_card(timeout_ms=5001))
    assert raised.value.code == "plan_contract_error"


def test_registry_module_has_no_dynamic_source_execution_calls() -> None:
    source = (ROOT / "reference_runtime" / "registered_functions.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_names = {"eval", "exec", "compile", "__import__"}
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not (called_names & forbidden_names)
    assert "importlib" not in imported_modules
