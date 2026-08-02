from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "tools" / "generate_contracts_and_cases.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("v6_contract_generator", GENERATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (ROOT / "validation" / "cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def walk_schemas(value: Any, path: str = "$"):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk_schemas(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_schemas(child, f"{path}[{index}]")


def test_generated_artifacts_are_current() -> None:
    expected = GENERATOR.build_artifacts()
    assert len(expected) == 41
    stale = []
    for relative_path, content in expected.items():
        target = ROOT / relative_path
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            stale.append(relative_path.as_posix())
    assert stale == []


def test_all_45_schemas_are_draft_2020_12_and_recursively_closed() -> None:
    schema_paths = sorted((ROOT / "contracts" / "schemas").glob("*.schema.json"))
    assert len(schema_paths) == 45
    names = {path.name for path in schema_paths}
    assert {
        "analysis-route.schema.json",
        "semantic-intent-selection.schema.json",
        "semantic-intent.schema.json",
        "analysis-plan.schema.json",
        "validation-case.schema.json",
        "response.schema.json",
        "turn-state.schema.json",
        "executable-blueprint.schema.json",
        "metadata-annotation-proposal.schema.json",
        "metadata-authoring-proposal.schema.json",
    } <= names

    for path in schema_paths:
        schema = load_json(path)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        jsonschema.Draft202012Validator.check_schema(schema)
        for location, node in walk_schemas(schema):
            if node.get("type") == "object":
                assert node.get("additionalProperties") is False, f"open object schema at {path.name}:{location}"


def test_route_and_intent_contracts_are_canonical() -> None:
    route = load_json(ROOT / "contracts" / "schemas" / "analysis-route.schema.json")
    intent = load_json(ROOT / "contracts" / "schemas" / "semantic-intent.schema.json")
    selection = load_json(ROOT / "contracts" / "schemas" / "semantic-intent-selection.schema.json")
    assert route["properties"]["contract_version"]["const"] == "analysis.route.v1"
    assert route["properties"]["route"]["enum"] == ["deterministic", "intent_llm", "unsupported"]
    assert route["properties"]["route_policy_version"]["const"] == "route-policy.v1"
    assert "eligibility_proof_sha256" in route["required"]
    assert intent["properties"]["contract_version"]["const"] == "analysis.intent.v1"
    assert intent["properties"]["route"]["enum"] == ["deterministic", "intent_llm"]
    assert intent["properties"]["intent_generator"]["enum"] == ["deterministic", "llm"]
    assert selection["additionalProperties"] is False

    route_validator = jsonschema.Draft202012Validator(route)
    invalid_route = {
        "contract_version": "analysis.route.v1",
        "route": "deterministic",
        "reason_code": "unique_complete_selection",
        "resolved_candidate_bundle_sha256": "0" * 64,
        "selected_candidate_ids": ["metric:production_qty"],
        "required_slots": ["metric"],
        "unresolved_slots": [],
        "ambiguity_sets": [],
        "route_policy_version": "route-policy.v1",
        "eligibility_proof_sha256": "1" * 64,
        "provider_suggested_sql": "select *",
    }
    assert list(route_validator.iter_errors(invalid_route))

    selection_validator = jsonschema.Draft202012Validator(selection)
    invalid_selection = {
        "request_scope": "new_analysis",
        "analysis_kind": "aggregate",
        "metric_refs": [{"candidate_id": "metric:production_qty", "target_slots": ["metric"], "raw_field": "PRODUCTION_QTY"}],
        "dimension_refs": [],
        "filter_refs": [],
        "time_refs": [],
        "operation_refs": [],
        "recipe_refs": [],
        "formula_refs": [],
        "followup": {"reference": "none", "inherit": [], "replace": [], "drop": []},
        "unresolved": [],
    }
    assert list(selection_validator.iter_errors(invalid_selection))


def test_registries_validate_and_have_self_consistent_hashes() -> None:
    for artifact_name, schema_name in (
        ("operator_registry.json", "operator-registry.schema.json"),
        ("error_registry.json", "error-registry.schema.json"),
    ):
        artifact = load_json(ROOT / "contracts" / artifact_name)
        schema = load_json(ROOT / "contracts" / "schemas" / schema_name)
        jsonschema.Draft202012Validator(schema).validate(artifact)
        hash_input = {key: value for key, value in artifact.items() if key != "registry_sha256"}
        assert artifact["registry_sha256"] == canonical_hash(hash_input)

    operators = load_json(ROOT / "contracts" / "operator_registry.json")
    errors = load_json(ROOT / "contracts" / "error_registry.json")
    assert [entry["op"] for entry in operators["operations"]] == list(GENERATOR.CORE_OPERATION_NAMES)
    assert [entry["code"] for entry in errors["errors"]] == list(GENERATOR.CORE_ERROR_CODES)
    assert {entry["operator_id"] for entry in operators["operations"]} == {
        f"{name}.v1" for name in GENERATOR.CORE_OPERATION_NAMES
    }


def test_all_70_cases_validate_and_have_frozen_inventory() -> None:
    cases = load_cases()
    case_schema = load_json(ROOT / "contracts" / "schemas" / "validation-case.schema.json")
    validator = jsonschema.Draft202012Validator(case_schema)
    errors = [(case["case_id"], list(validator.iter_errors(case))) for case in cases]
    assert [(case_id, detail) for case_id, detail in errors if detail] == []

    assert len(cases) == 70
    assert Counter(case["suite"] for case in cases) == {
        "single": 30,
        "date": 6,
        "multiturn": 12,
        "operator": 14,
        "branch": 8,
    }
    ids = {case["case_id"] for case in cases}
    assert {f"Q{i:02d}" for i in range(1, 31)} <= ids
    assert {f"D{i:02d}" for i in range(1, 7)} <= ids
    assert {
        "MT01-01", "MT01-02", "MT01-03", "MT01-04", "MT02-01", "MT02-02",
        "MT03-01", "MT03-02", "MT04-01", "MT04-02", "MT05-01", "MT05-02",
    } <= ids
    assert {"OP01", "OP02", "OP03", "OP04", "OP05", "OP05A", "OP06", "OP07", "OP08", "OP09", "OP10", "OP11", "OP12", "OP13"} <= ids


def test_case_routes_calls_and_no_fallback_are_exact() -> None:
    cases = load_cases()
    assert Counter(case["expected_route"] for case in cases) == {
        "deterministic": 65,
        "intent_llm": 3,
        "unsupported": 2,
    }
    for case in cases:
        expected_calls = 1 if case["expected_route"] == "intent_llm" else 0
        assert case["expected_intent_llm_calls"] == expected_calls
        assert case["expected_intent_retry_calls"] == 0
        assert case["fallback_allowed"] is False
        assert case["reference_instant"] == GENERATOR.REFERENCE_INSTANT
        assert case["timezone"] == GENERATOR.REFERENCE_TIMEZONE
        if case["expected_route"] == "unsupported":
            assert case["expected_retrieval_calls"] == 0
            assert case["expected_error_code"] == "unsupported_operation"


def test_case_operators_and_errors_are_registry_bounded() -> None:
    cases = load_cases()
    operator_ids = {entry["operator_id"] for entry in load_json(ROOT / "contracts" / "operator_registry.json")["operations"]}
    error_codes = {entry["code"] for entry in load_json(ROOT / "contracts" / "error_registry.json")["errors"]}
    for case in cases:
        semantic_ops = set(case["expected_semantic_contract"]["operation_ids"])
        result_ops = set(case["expected_result_contract"]["operator_sequence"])
        assert semantic_ops == result_ops
        assert semantic_ops <= operator_ids
        if case["expected_error_code"] is not None:
            assert case["expected_error_code"] in error_codes
        forbidden = {"pandas_code", "python_code", "repair_prompt", "raw_llm_output"}
        assert not any(key in forbidden for _, node in walk_schemas(case) if isinstance(node, dict) for key in node)


def test_explicit_branch_probes_cover_every_control_path() -> None:
    by_id = {case["case_id"]: case for case in load_cases()}
    assert (by_id["BR-D01"]["expected_route"], by_id["BR-D01"]["expected_intent_llm_calls"]) == ("deterministic", 0)
    assert (by_id["BR-L01"]["expected_route"], by_id["BR-L01"]["expected_intent_llm_calls"]) == ("deterministic", 0)
    assert by_id["BR-A01"]["expected_status"] == "needs_clarification"
    assert by_id["BR-A01"]["expected_retrieval_calls"] == 0
    assert by_id["BR-U01"]["expected_retrieval_calls"] == 0
    assert by_id["BR-F01"]["expected_error_code"] == "plan_contract_error"
    assert by_id["BR-F01"]["expected_intent_llm_calls"] == 0
    assert by_id["BR-MT01"]["expected_retrieval_calls"] == 0

    deterministic = by_id["BR-EQD"]
    llm = by_id["BR-EQL"]
    assert deterministic["expected_route"] == "deterministic"
    assert llm["expected_route"] == "intent_llm"
    assert deterministic["equivalence_group_id"] == llm["equivalence_group_id"] == "EQ-DA-TOP3-V1"
    assert deterministic["expected_semantic_contract"] == llm["expected_semantic_contract"]
    assert deterministic["expected_result_contract"] == llm["expected_result_contract"]


def test_multiturn_fast_paths_and_context_rules_are_explicit() -> None:
    by_id = {case["case_id"]: case for case in load_cases()}
    for case_id in ("MT01-03", "MT05-02", "BR-MT01"):
        case = by_id[case_id]
        assert case["expected_route"] == "deterministic"
        assert case["expected_intent_llm_calls"] == 0
        assert case["expected_retrieval_calls"] == 0
        assert case["expected_semantic_contract"]["request_scope"] == "previous_result_transform"
    assert "process_filter_inherited" in by_id["MT03-02"]["expected_result_contract"]["invariant_ids"]
    assert "pop_replaces_mobile" in by_id["MT04-02"]["expected_result_contract"]["invariant_ids"]
    assert by_id["MT04-02"]["expected_retrieval_calls"] is None
    assert {item["analysis_mode"] for item in by_id["MT04-02"]["expected_result_contract"]["variant_oracles"]} == {
        "previous_source_transform", "followup_requery"
    }
    assert "no_stale_da_filter" in by_id["MT01-04"]["expected_result_contract"]["invariant_ids"]


def test_generated_docs_report_the_same_counts_and_branch_ids() -> None:
    acceptance = (ROOT / "validation" / "ACCEPTANCE_MATRIX.md").read_text(encoding="utf-8")
    classification = (ROOT / "validation" / "branch_classification.md").read_text(encoding="utf-8")
    questions = (ROOT / "validation" / "branch_validation_questions.txt").read_text(encoding="utf-8")
    assert "**70**" in acceptance
    assert "**65**" in acceptance and "**3**" in acceptance and "**2**" in acceptance
    for case_id in ("BR-D01", "BR-L01", "BR-A01", "BR-U01", "BR-F01", "BR-MT01", "BR-EQD", "BR-EQL"):
        assert case_id in acceptance
        assert case_id in classification
        assert case_id in questions
