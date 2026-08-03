from __future__ import annotations

import ast
import hashlib
import json
import re
import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools.build_standalone_components import GenerationError, build_components
from tools.flow_builder_support import EXPECTED_FLOW_KEYS, flow_export_filename, load_inventory


ROOT = Path(__file__).resolve().parents[1]
COMPONENT_ROOT = ROOT / "langflow_components"
CATALOG_PATH = ROOT / "metadata" / "fixtures" / "compiled" / "runtime_catalog.json"
MANUFACTURING_V1_PATH = ROOT / "metadata" / "domain_packs" / "manufacturing" / "runtime_catalog.v1.json"
MANUFACTURING_V2_PATH = ROOT / "metadata" / "domain_packs" / "manufacturing" / "compiled" / "runtime_catalog.v2.json"
AUTHORING_WORKER_SOURCE_SETS = {
    "baseline": ROOT / "metadata" / "authoring" / "v6_inputs",
    "freeform_reordered_v1": (
        ROOT
        / "validation"
        / "fixtures"
        / "authoring"
        / "freeform_reordered_v1"
    ),
}
MANUFACTURING_DATASET_BUSINESS_LABELS = (
    "당일 생산 실적",
    "생산 이력",
    "현재 재공",
    "재공 이력",
    "생산 계획",
    "장비 배정 현황",
    "장비·제품별 UPH",
    "현재 LOT 현황",
    "HOLD 이력",
    "제품 기준정보",
)

EXPECTED_COMPONENTS = {
    "data_analysis/request_state_capsule.py": "RequestStateCapsule",
    "data_analysis/domain_bundle_loader.py": "DomainBundleLoader",
    "data_analysis/candidate_route_gate.py": "CandidateRouteGate",
    "data_analysis/intent_prompt_context_builder.py": "IntentPromptContextBuilder",
    "data_analysis/common_intent_resolver.py": "CommonIntentResolver",
    "data_analysis/plan_compiler_validator.py": "PlanCompilerValidator",
    "data_analysis/retrieval_job_router.py": "RetrievalJobRouter",
    "data_analysis/dummy_source_retriever.py": "DummySourceRetriever",
    "data_analysis/12_oracle_source_retriever.py": "OracleSourceRetriever",
    "data_analysis/13_h_api_source_retriever.py": "HApiSourceRetriever",
    "data_analysis/14_datalake_source_retriever.py": "DatalakeSourceRetriever",
    "data_analysis/15_goodocs_source_retriever.py": "GoodocsSourceRetriever",
    "data_analysis/source_contract_merger.py": "SourceContractMerger",
    "data_analysis/typed_executor_publisher.py": "TypedExecutorPublisher",
    "data_analysis/answer_facts_context_builder.py": "AnswerFactsContextBuilder",
    "data_analysis/answer_claim_validator.py": "AnswerClaimValidator",
    "data_analysis/response_state_commit.py": "ResponseStateCommit",
    "data_analysis/01_message_presentation.py": "MessagePresentation",
    "data_analysis/02_gaia_output.py": "GaiAOutput",
    "metadata_authoring/00_metadata_authoring_engine.py": "MetadataAuthoringEngine",
    "metadata_authoring/natural_metadata_source_bundle.py": "NaturalMetadataSourceBundle",
    "metadata_authoring/authoring_reference_registry.py": "AuthoringReferenceRegistry",
    "metadata_authoring/authoring_prompt_context_builder.py": "AuthoringPromptContextBuilder",
    "metadata_authoring/simple_metadata_draft_generator.py": "SimpleMetadataDraftGenerator",
    "metadata_authoring/02_simple_metadata_authoring_engine.py": "SimpleMetadataAuthoringEngine",
    "metadata_authoring/01_authoring_message_presentation.py": "AuthoringMessagePresentation",
    "shared/00_api_response_terminal.py": "APIResponseTerminal",
}

DATA_ANALYSIS_SOURCES = {
    f"langflow_components/{relative}"
    for relative in EXPECTED_COMPONENTS
    if relative.startswith("data_analysis/") or relative.startswith("shared/")
}


def _source(relative: str) -> str:
    return (COMPONENT_ROOT / relative).read_text(encoding="utf-8")


def _component_class(relative: str):
    from lfx.custom.eval import eval_custom_component_code

    return eval_custom_component_code(_source(relative))


def _test_semantic_vocabulary(catalog: dict) -> dict:
    dataset_families = {
        dataset_id: str(card["family"])
        for dataset_id, card in catalog["datasets"].items()
    }
    field_families = {
        field_id: sorted(
            {dataset_families[dataset_id] for dataset_id in field["dataset_keys"]}
        )
        for field_id, field in catalog["fields"].items()
    }
    simple_sections = (
        "metrics", "relations", "grains", "orderings", "predicates",
        "recipes", "entity_groups",
    )
    return {
        "contract_version": "metadata.authoring.semantic-vocabulary.v1",
        "datasets": [
            {"id": dataset_id, "family": dataset_families[dataset_id], "labels": []}
            for dataset_id in sorted(dataset_families)
        ],
        "fields": [
            {"id": field_id, "families": field_families[field_id], "labels": []}
            for field_id in sorted(field_families)
        ],
        **{
            section: [
                {"id": item_id, "labels": []}
                for item_id in sorted(catalog.get(section) or {})
            ]
            for section in simple_sections
        },
    }


def _test_semantic_templates(domain_id: str, catalog: dict) -> dict:
    """Build the sealed semantic template half of a synthetic v3 registry.

    Tests use the reviewed executable blueprint as the authority, mirroring the
    production registry builder.  Older fixtures used compact three-key alias
    cards, so normalize those cards to the closed v3 policy here rather than
    teaching the LLM-facing vocabulary any executable alias policy.
    """

    blueprint = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / domain_id
            / "trusted_executable_blueprint.json"
        ).read_text(encoding="utf-8")
    )["executable"]
    identity_keys = {
        "metrics": "metric_id",
        "relations": "relation_id",
        "entity_groups": "group_id",
        "grains": "grain_id",
        "orderings": "ordering_id",
        "predicates": "predicate_id",
        "recipes": "recipe_id",
    }
    sections = {
        section: {
            item_id: {
                key: deepcopy(value)
                for key, value in card.items()
                if key != identity_key
            }
            for item_id, card in sorted((blueprint.get(section) or {}).items())
        }
        for section, identity_key in identity_keys.items()
    }
    assert all(
        set(sections[section]) == set(catalog.get(section) or {})
        for section in identity_keys
    )

    policy = {
        "normalization": [
            "unicode_nfkc",
            "trim",
            "collapse_space",
            "latin_casefold",
        ],
        "match": "bounded_longest",
        "conflict": "fail_ambiguous",
        "provenance_source": "approved_template",
    }
    raw_output_profile = blueprint.get("output_profile") or {}
    planner_profile = str(raw_output_profile.get("planner_profile") or "generic_v2")
    planner_policy = {"planner_profile": planner_profile}
    if planner_profile == "legacy_v1_compat":
        planner_policy["legacy_catalog_sha256"] = str(
            raw_output_profile["legacy_catalog_sha256"]
        )
    aliases = {}
    for alias_id, raw_card in sorted((blueprint.get("aliases") or {}).items()):
        if (
            raw_card.get("target_type") == "status"
            and planner_profile != "legacy_v1_compat"
        ):
            continue
        card = deepcopy(raw_card)
        raw_values = card.get("values") or []
        values = [
            deepcopy(value)
            if isinstance(value, dict)
            else {"text": str(value), "priority": 100}
            for value in raw_values
        ]
        aliases[alias_id] = {
            "target_type": card["target_type"],
            "target_key": card["target_key"],
            "values": values,
            "normalization": deepcopy(card.get("normalization") or policy["normalization"]),
            "match": str(card.get("match") or policy["match"]),
            "conflict": str(card.get("conflict") or policy["conflict"]),
            "provenance_source": str(
                card.get("provenance_source") or policy["provenance_source"]
            ),
        }
    return {
        "contract_version": "metadata.authoring.semantic-templates.v1",
        "locale": str(blueprint["locale"]),
        "timezone": str(blueprint["timezone"]),
        "planner_policy": planner_policy,
        **sections,
        "aliases": aliases,
    }


def _approved_reference_context(domain_id: str):
    catalog = json.loads(
        (ROOT / "metadata" / "domain_packs" / domain_id / "compiled" / "runtime_catalog.v2.json").read_text(
            encoding="utf-8"
        )
    )
    descriptor_keys = (
        "physical_column",
        "semantic_type",
        "roles",
        "physical_aliases",
        "coercion",
        "nullable",
        "required_in_source",
        "timezone",
    )
    exclusions_path = (
        ROOT
        / "metadata"
        / "domain_packs"
        / domain_id
        / "source_registry_exclusions.json"
    )
    proposal_exclusions = (
        json.loads(exclusions_path.read_text(encoding="utf-8"))["datasets"]
        if exclusions_path.is_file()
        else {}
    )
    semantic_templates = _test_semantic_templates(domain_id, catalog)
    semantic_templates_sha256 = hashlib.sha256(
        json.dumps(
            semantic_templates,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    blueprint = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / domain_id
            / "trusted_executable_blueprint.json"
        ).read_text(encoding="utf-8")
    )
    projection_sha256 = hashlib.sha256(
        f"{domain_id}:{semantic_templates_sha256}:synthetic-v3-test".encode("utf-8")
    ).hexdigest()
    registry = {
        "contract_version": "metadata.authoring.source-registry.v3",
        "domain_id": domain_id,
        "semantic_vocabulary": _test_semantic_vocabulary(catalog),
        "semantic_templates": semantic_templates,
        "semantic_templates_sha256": semantic_templates_sha256,
        "semantic_templates_blueprint_sha256": str(blueprint["blueprint_sha256"]),
        "semantic_templates_executable_sha256": str(
            blueprint["executable_sha256"]
        ),
        "semantic_templates_projection_sha256": projection_sha256,
        "datasets": {
            dataset_id: {
                **{
                    key: card[key]
                    for key in ("source_type", "source_adapter", "config_ref", "query_ref")
                },
                "family": card["family"],
                "field_descriptors": {
                    field_id: {
                        key: field[key]
                        for key in descriptor_keys
                        if key in field
                    }
                    for field_id, field in card["fields"].items()
                },
                "proposal_exclusions": deepcopy(
                    proposal_exclusions.get(dataset_id, {})
                ),
                "dataset_template": {
                    key: deepcopy(card[key])
                    for key in (
                        "date_filter_contract",
                        "date_policy",
                        "default_detail_fields",
                        "display_name",
                        "fixture_only",
                        "parameters",
                        "read_policy",
                        "time_scope",
                        "upstream_bindings",
                    )
                    if key in card
                },
                "dataset_template_sha256": hashlib.sha256(
                    json.dumps(
                        {
                            key: deepcopy(card[key])
                            for key in (
                                "date_filter_contract",
                                "date_policy",
                                "default_detail_fields",
                                "display_name",
                                "fixture_only",
                                "parameters",
                                "read_policy",
                                "time_scope",
                                "upstream_bindings",
                            )
                            if key in card
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                        allow_nan=False,
                    ).encode("utf-8")
                ).hexdigest(),
            }
            for dataset_id, card in catalog["datasets"].items()
        },
    }
    component_cls = _component_class("metadata_authoring/authoring_reference_registry.py")
    component = component_cls()
    component.registry_json = json.dumps(registry, ensure_ascii=False)
    component.domain_id = domain_id
    return component.load_registry()


def _bootstrap_prompt_context(
    *,
    kind: str,
    source_text: str,
    domain_id: str,
    environment: str,
    approved_reference_context=None,
    source_grounding_mode: str = "freeform_llm",
    bootstrap_fragment: bool = True,
    trusted_blueprint_json: str = "",
    trusted_blueprint_sha256: str = "",
):
    from lfx.schema.message import Message

    component_cls = _component_class(
        "metadata_authoring/authoring_prompt_context_builder.py"
    )
    component = component_cls()
    component.input_message = Message(text=source_text)
    component.authoring_kind = kind
    component.mode = "prepare"
    component.source_grounding_mode = source_grounding_mode
    component.bootstrap_fragment = bootstrap_fragment
    component.domain_id = domain_id
    component.environment = environment
    component.trusted_blueprint_json = trusted_blueprint_json
    component.trusted_blueprint_sha256 = trusted_blueprint_sha256
    if approved_reference_context is not None:
        component.approved_reference_context = approved_reference_context
    return component.build_context()


def test_manufacturing_dataset_input_is_worker_friendly_and_query_aware() -> None:
    """The baseline may carry reviewed SQL while variants remain plain prose."""

    context = _approved_reference_context("manufacturing").data

    forbidden_registration_syntax = (
        "dataset_id",
        "field_id",
        "source_binding",
        "config_ref",
        "query_ref",
        "physical_column",
        "pandas_function_cases",
    )
    assert len(context["dataset_descriptors"]) == 10
    for source_set, source_dir in AUTHORING_WORKER_SOURCE_SETS.items():
        source = (source_dir / "dataset_v6.txt").read_text(encoding="utf-8")
        assert all(label in source for label in MANUFACTURING_DATASET_BUSINESS_LABELS)
        assert not any(token in source for token in forbidden_registration_syntax)
        if source_set == "baseline":
            assert source.count("query_template:") == 8
            assert "{DATE}" in source and "{LOT_ID}" in source
        else:
            assert "query_template:" not in source


def test_worker_v6_inputs_remain_free_prose_not_compiler_grammar() -> None:
    forbidden_compiler_terms = {
        "contract_version",
        "dataset_id",
        "field_id",
        "target_type",
        "target_id",
        "alias_additions",
        "semantic_templates",
        "semantic_vocabulary",
        "source_binding",
        "physical_column",
        "semantic_type",
        "config_ref",
        "query_ref",
    }
    filenames = ("domain_v6.txt", "dataset_v6.txt", "main_filter_v6.txt")
    source_texts: dict[str, dict[str, str]] = {}
    for source_set, source_dir in AUTHORING_WORKER_SOURCE_SETS.items():
        source_texts[source_set] = {}
        for filename in filenames:
            text = (source_dir / filename).read_text(encoding="utf-8").strip()
            source_texts[source_set][filename] = text
            assert 1 <= len(text.encode("utf-8")) <= 65536
            assert not text.startswith("{")
            assert not text.startswith("[")
            observed_terms = forbidden_compiler_terms & set(re.findall(r"[A-Za-z_]+", text))
            if source_set == "baseline" and filename == "dataset_v6.txt":
                observed_terms -= {"semantic_type"}
            assert not observed_terms
            with pytest.raises(json.JSONDecodeError):
                json.loads(text)

    assert source_texts["baseline"]["domain_v6.txt"].startswith("# ")
    for text in source_texts["freeform_reordered_v1"].values():
        assert not re.search(r"(?m)^\s{0,3}#{1,6}\s+", text)
    for filename in filenames:
        assert hashlib.sha256(
            source_texts["baseline"][filename].encode("utf-8")
        ).hexdigest() != hashlib.sha256(
            source_texts["freeform_reordered_v1"][filename].encode("utf-8")
        ).hexdigest()

    baseline_dataset = source_texts["baseline"]["dataset_v6.txt"]
    reordered_dataset = source_texts["freeform_reordered_v1"]["dataset_v6.txt"]
    baseline_order = sorted(
        MANUFACTURING_DATASET_BUSINESS_LABELS,
        key=baseline_dataset.index,
    )
    reordered_order = sorted(
        MANUFACTURING_DATASET_BUSINESS_LABELS,
        key=reordered_dataset.index,
    )
    assert baseline_order != reordered_order
    assert reordered_order[:2] == ["현재 LOT 현황", "HOLD 이력"]


def _bootstrap_invocation(
    *,
    kind: str,
    source_text: str,
    output_schema: dict,
    runtime_context: dict,
    draft: dict | None = None,
    question: str | None = None,
    direct_compact_ir: bool = False,
    purpose_override: str = "",
):
    from lfx.schema.data import Data

    if direct_compact_ir:
        assert draft is not None
        proposal = deepcopy(draft)
    elif draft is None:
        proposal = {
            "contract_version": "metadata.authoring.proposal.v1",
            "status": "needs_clarification",
            "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            "clarification": {
                "questions": [question or "어떤 업무 데이터가 필요한지 설명해 주세요."],
                "missing_fields": ["required_metadata"],
            },
        }
    else:
        proposal = {
            "contract_version": "metadata.authoring.proposal.v1",
            "status": "complete",
            "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            "draft": draft,
        }
    purpose = purpose_override or {
        "domain": "metadata_domain_draft",
        "dataset": "metadata_dataset_draft",
        "main_filter": "metadata_main_filter_draft",
    }[kind]
    authoritative_schema_sha256 = hashlib.sha256(
        json.dumps(
            output_schema,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    response_text = json.dumps(proposal, ensure_ascii=False)
    runtime_context_material = {
        "authority": "untrusted_data",
        "purpose": runtime_context["purpose"],
        "variables": runtime_context["variables"],
    }
    runtime_context_sha256 = hashlib.sha256(
        json.dumps(
            runtime_context_material,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    return Data(
        data={
            "contract_version": "llm.invocation.v1",
            "purpose": purpose,
            "status": "ok",
            "llm_calls": 1,
            "prompt_bundle_sha256": hashlib.sha256(
                f"test-prompt-bundle:{kind}:{runtime_context_sha256}".encode("utf-8")
            ).hexdigest(),
            "runtime_context_sha256": runtime_context_sha256,
            "provider_schema_binding": "portable_prompt_and_compiler_validation",
            "schema_binding_evidence": {
                "contract_version": "llm.schema-binding.evidence.v1",
                "binding_status": "portable_prompt_and_compiler_validation",
                "projection": "none",
                "authoritative_schema_sha256": authoritative_schema_sha256,
                "provider_schema_sha256": "",
            },
            "response_text": response_text,
            "response_sha256": hashlib.sha256(response_text.encode("utf-8")).hexdigest(),
        }
    )


def _complete_proposal_draft_schema(output_schema: dict) -> dict:
    complete = next(
        branch
        for branch in output_schema["oneOf"]
        if branch["properties"]["status"]["const"] == "complete"
    )
    return complete["properties"]["draft"]


def _compact_dataset_fragment(datasets: dict) -> dict:
    cards = []
    for dataset_id in sorted(datasets):
        source = datasets[dataset_id]
        fields = []
        for field_id in sorted(source["fields"]):
            # The LLM owns only the semantic selection. All executable source,
            # field, coercion and dataset policy is restored from the sealed
            # registry by the deterministic expander/compiler.
            fields.append({"id": field_id, "col": field_id})
        cards.append({"dataset_id": dataset_id, "fields": fields})
    return {"dataset_cards": cards}


def _bootstrap_source_bundle(source_texts: dict[str, str]) -> str:
    return "\n\n".join(
        f"--- {label} 시작 ---\n{source_texts[kind].strip()}\n--- {label} 끝 ---"
        for kind, label in (
            ("domain", "도메인 정보"),
            ("dataset", "데이터셋 정보"),
            ("main_filter", "주요 필터 정보"),
        )
    )


def _embedded_json(relative: str, assignment_name: str) -> dict:
    tree = ast.parse(_source(relative), filename=relative)
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == assignment_name for target in node.targets)
    )
    assert isinstance(assignment.value, ast.Call)
    return json.loads(ast.literal_eval(assignment.value.args[0]))


def test_generated_sources_are_current_and_monolith_is_gone() -> None:
    assert len(build_components(check=True)) == len(EXPECTED_COMPONENTS) == 27
    assert not (COMPONENT_ROOT / "data_analysis" / "00_trusted_analysis_engine.py").exists()


def test_runtime_source_retrievers_restore_v5_operator_inputs() -> None:
    expected_inputs = {
        "data_analysis/12_oracle_source_retriever.py": {"oracle_config", "fetch_limit"},
        "data_analysis/13_h_api_source_retriever.py": {"api_token", "timeout_seconds", "fetch_limit"},
        "data_analysis/14_datalake_source_retriever.py": {
            "module_name", "class_name", "user_id", "token", "s3_access_key", "s3_secret_key", "fetch_limit",
        },
        "data_analysis/15_goodocs_source_retriever.py": {"user_id", "token_source", "token_key", "fetch_limit"},
    }
    for relative, expected in expected_inputs.items():
        source = _source(relative)
        assert 'name="source_payload"' not in source
        assert 'name="source_row_limit"' not in source
        assert "source_memory_limit" not in source
        for name in expected:
            assert f'name="{name}"' in source
        assert "_connector_payload(selected_jobs, catalog)" in source
        assert "_checked_connector_results" in source


def test_oracle_source_retriever_executes_v5_compatible_connector_without_source_payload() -> None:
    from lfx.schema.data import Data

    class FakeCursor:
        description = [("PHYSICAL_VALUE",)]

        def execute(self, sql: str) -> None:
            assert sql == "SELECT PHYSICAL_VALUE\nFROM TEST_TABLE\nWHERE WORK_DATE = '20260803'"

        def fetchmany(self, limit: int):
            assert limit == 5000
            return [(7,)]

        def close(self) -> None:
            return None

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def close(self) -> None:
            return None

    class FakeOracle:
        @staticmethod
        def connect(**kwargs):
            assert kwargs == {"dsn": "TEST_DSN"}
            return FakeConnection()

    component_cls = _component_class("data_analysis/12_oracle_source_retriever.py")
    component_cls.oracledb = FakeOracle
    component = component_cls()
    component.job_bundle = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "stage": "job_routing",
            "data_mode": "live",
            "source_type": "oracle",
            "jobs": [
                {
                    "job_id": "job_test",
                    "dataset_key": "test_dataset",
                    "source_type": "oracle",
                    "parameters": {"DATE": "20260803"},
                    "required_fields": ["VALUE"],
                    "filters": None,
                }
            ],
        }
    )
    component.domain_bundle = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "domain_bundle": {
                "runtime_catalog": {
                    "datasets": {
                        "test_dataset": {
                            "source_type": "oracle",
                            "source_config": {
                                "db_key": "TEST_DB",
                                "query_template": "SELECT PHYSICAL_VALUE\nFROM TEST_TABLE\nWHERE WORK_DATE = {DATE}",
                                "required_params": ["DATE"],
                            },
                            "parameters": {"DATE": {"type": "LocalDate", "required": True}},
                        }
                    }
                }
            },
        }
    )
    component.oracle_config = '{"TEST_DB":{"dsn":"TEST_DSN"}}'
    component.fetch_limit = "5000"

    result = component.retrieve().data

    assert result["ok"] is True
    assert result["status"] == "selected"
    assert result["source_results"][0]["rows"] == [{"PHYSICAL_VALUE": 7}]
    assert result["source_results"][0]["source_type"] == "oracle"


def test_datalake_retriever_executes_catalog_query_with_required_parameter() -> None:
    from lfx.schema.data import Data

    class FakeLake:
        def run_sql(self, sql: str):
            assert sql == "SELECT LOT_ID, VALUE\nFROM LAKE_TABLE\nWHERE LOT_ID = 'LOT-001'"
            return [{"LOT_ID": "LOT-001", "VALUE": 9}]

    component_cls = _component_class("data_analysis/14_datalake_source_retriever.py")
    component = component_cls()
    component.client_cls = FakeLake
    component.job_bundle = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "stage": "job_routing",
            "data_mode": "live",
            "source_type": "datalake",
            "jobs": [
                {
                    "job_id": "job_lake",
                    "dataset_key": "lake_dataset",
                    "source_type": "datalake",
                    "parameters": {"LOT_ID": "LOT-001"},
                    "required_fields": ["LOT_ID", "VALUE"],
                    "filters": None,
                }
            ],
        }
    )
    component.domain_bundle = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "domain_bundle": {
                "runtime_catalog": {
                    "datasets": {
                        "lake_dataset": {
                            "source_type": "datalake",
                            "source_config": {
                                "source_type": "datalake",
                                "db_key": "LAKE_MAIN",
                                "query_template": "SELECT LOT_ID, VALUE\nFROM LAKE_TABLE\nWHERE LOT_ID = {LOT_ID}",
                                "required_params": ["LOT_ID"],
                            },
                            "parameters": {"LOT_ID": {"type": "string", "required": True}},
                        }
                    }
                }
            },
        }
    )
    component.module_name = "lakes"
    component.class_name = "LakeHouse"
    component.token = ""
    component.s3_access_key = ""
    component.s3_secret_key = ""
    component.fetch_limit = "5000"

    result = component.retrieve().data

    assert result["ok"] is True
    assert result["status"] == "selected"
    assert result["source_results"][0]["rows"] == [{"LOT_ID": "LOT-001", "VALUE": 9}]


def test_metadata_node_exposes_collection_names_but_hides_domain_selectors() -> None:
    domain_cls = _component_class("data_analysis/domain_bundle_loader.py")
    request_cls = _component_class("data_analysis/request_state_capsule.py")

    assert {item.name for item in domain_cls.inputs} == {
        "mongo_uri",
        "mongo_database",
        "domain_collection",
        "table_collection",
        "main_filter_collection",
        "mongo_timeout_ms",
    }
    values = {item.name: getattr(item, "value", None) for item in domain_cls.inputs}
    assert values["domain_collection"] == "agent_v6_domain_metadata"
    assert values["table_collection"] == "agent_v6_table_catalog"
    assert values["main_filter_collection"] == "agent_v6_main_filter"
    assert {"domain_id", "environment", "metadata_source_mode", "inline_domain_bundle"}.isdisjoint(
        {item.name for item in domain_cls.inputs}
    )
    assert {"reference_instant", "reference_timezone"}.isdisjoint(
        {item.name for item in request_cls.inputs}
    )
    assert 'timezone_name = "Asia/Seoul"' in _source("data_analysis/request_state_capsule.py")


@pytest.mark.parametrize(("relative", "expected_class"), sorted(EXPECTED_COMPONENTS.items()))
def test_each_generated_source_is_self_contained_and_langflow_parseable(relative: str, expected_class: str) -> None:
    from lfx.custom.utils import create_component_template

    source = _source(relative)
    tree = ast.parse(source, filename=relative)
    assert not [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and int(node.level or 0) > 0]
    forbidden_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"exec", "eval"}
    ]
    assert not forbidden_calls
    assert ".read_text(" not in source
    assert ".read_bytes(" not in source

    component_classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == expected_class]
    assert len(component_classes) == 1
    inputs_assignment = next(
        (node for node in component_classes[0].body if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "inputs" for target in node.targets
        )),
        None,
    )
    assert inputs_assignment is not None
    input_names = [
        keyword.value.value
        for item in inputs_assignment.value.elts
        if isinstance(item, ast.Call)
        for keyword in item.keywords
        if keyword.arg == "name" and isinstance(keyword.value, ast.Constant)
    ]
    assert len(input_names) == len(set(input_names)), f"duplicate component inputs in {relative}"

    config, instance = create_component_template(
        {"code": source, "output_types": []},
        module_name=f"standalone_test.{Path(relative).stem}",
    )
    assert instance.__class__.__name__ == expected_class
    assert config["display_name"] == instance.display_name


def test_manifest_pins_generic_runtime_and_compiled_catalog() -> None:
    manifest = _embedded_json("data_analysis/candidate_route_gate.py", "EMBEDDED_SOURCE_MANIFEST")
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assert manifest["contract_version"] == "standalone.source.manifest.v1"
    assert manifest["catalog_declared_sha256"] == catalog["catalog_sha256"]
    assert set(manifest["reference_sources"]) >= {
        "reference_runtime/contracts.py",
        "reference_runtime/domain_packages.py",
        "reference_runtime/domain_authoring_patches.py",
        "reference_runtime/generic_v2_candidates.py",
        "reference_runtime/generic_v2_planner.py",
        "reference_runtime/plan_compiler.py",
        "reference_runtime/source_contracts.py",
        "reference_runtime/typed_executor.py",
        "contracts/schemas/resolved-candidate-bundle.schema.json",
        "contracts/schemas/semantic-intent.schema.json",
        "contracts/schemas/analysis-plan.schema.json",
        "contracts/schemas/response.schema.json",
    }


def test_manufacturing_legacy_profile_is_exactly_hash_pinned() -> None:
    legacy = json.loads(MANUFACTURING_V1_PATH.read_text(encoding="utf-8"))
    compiled = json.loads(MANUFACTURING_V2_PATH.read_text(encoding="utf-8"))
    profile = compiled["output_profile"]
    assert profile["planner_profile"] == "legacy_v1_compat"
    assert profile["legacy_catalog_sha256"] == legacy["catalog_sha256"]
    embedded = _embedded_json("data_analysis/candidate_route_gate.py", "EMBEDDED_RUNTIME_CATALOG")
    assert profile["legacy_catalog_sha256"] == embedded["catalog_sha256"]


def test_manufacturing_legacy_profile_accepts_real_package_and_output_overlays() -> None:
    component_cls = _component_class("data_analysis/candidate_route_gate.py")
    profile_fn = component_cls.select_route.__globals__["_planner_profile"]
    catalog = json.loads(MANUFACTURING_V2_PATH.read_text(encoding="utf-8"))

    assert profile_fn(catalog) == "legacy_v1_compat"
    with_overlay = deepcopy(catalog)
    with_overlay["output_profile"]["validation_policy_marker"] = "release-a"
    with_overlay["output_profile"]["field_labels"] = {"PRODUCTION_QTY": "Production"}
    assert profile_fn(with_overlay) == "legacy_v1_compat"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("legacy_catalog_sha256", "0" * 64),
        ("planner_profile", "legacy_v1_compat_spoof"),
        ("domain_id", "other_domain"),
        ("compiler_version", "metadata-domain-compiler.v6.4"),
    ],
)
def test_manufacturing_legacy_profile_rejects_wrong_control_boundary(
    field: str,
    value: str,
) -> None:
    component_cls = _component_class("data_analysis/candidate_route_gate.py")
    profile_fn = component_cls.select_route.__globals__["_planner_profile"]
    catalog = json.loads(MANUFACTURING_V2_PATH.read_text(encoding="utf-8"))
    if field in {"legacy_catalog_sha256", "planner_profile"}:
        catalog["output_profile"][field] = value
    else:
        catalog[field] = value

    with pytest.raises(Exception) as raised:
        profile_fn(catalog)
    assert getattr(raised.value, "code", "") == "unsupported_operation"
    assert getattr(raised.value, "stage", "") == "planner_profile"


def test_generic_v2_profile_is_unchanged() -> None:
    component_cls = _component_class("data_analysis/candidate_route_gate.py")
    profile_fn = component_cls.select_route.__globals__["_planner_profile"]
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "order_sales"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    assert profile_fn(package["runtime_catalog"]) == "generic_v2"


def test_manufacturing_legacy_profile_survives_three_section_patch_round_trips() -> None:
    from reference_runtime.domain_authoring_patches import (
        apply_authoring_section_patch,
        runtime_catalog_v2_to_authoring_draft,
    )
    from reference_runtime.domain_packages import compile_domain_package

    component_cls = _component_class("data_analysis/candidate_route_gate.py")
    profile_fn = component_cls.select_route.__globals__["_planner_profile"]
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "manufacturing"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    domain_id = package["domain_id"]
    environment = package["environment"]
    revision = int(package["revision"])

    draft = runtime_catalog_v2_to_authoring_draft(package["runtime_catalog"])
    draft = apply_authoring_section_patch(
        draft,
        {"output_profile": {"validation_policy_marker": "roundtrip-1"}},
        "domain_policy",
    )
    revision += 1
    package = compile_domain_package(draft, domain_id, environment, revision=revision)
    assert profile_fn(package["runtime_catalog"]) == "legacy_v1_compat"

    draft = runtime_catalog_v2_to_authoring_draft(package["runtime_catalog"])
    dataset_key = sorted(draft["datasets"])[0]
    draft = apply_authoring_section_patch(
        draft,
        {
            "datasets": {
                dataset_key: {
                    "display_name": str(draft["datasets"][dataset_key]["display_name"])
                }
            }
        },
        "dataset",
    )
    revision += 1
    package = compile_domain_package(draft, domain_id, environment, revision=revision)
    assert profile_fn(package["runtime_catalog"]) == "legacy_v1_compat"

    draft = runtime_catalog_v2_to_authoring_draft(package["runtime_catalog"])
    alias_key = sorted(draft["aliases"])[0]
    draft = apply_authoring_section_patch(
        draft,
        {"aliases": {alias_key: deepcopy(draft["aliases"][alias_key])}},
        "main_filter",
    )
    revision += 1
    package = compile_domain_package(draft, domain_id, environment, revision=revision)
    assert profile_fn(package["runtime_catalog"]) == "legacy_v1_compat"
    assert package["runtime_catalog"]["output_profile"]["legacy_catalog_sha256"] == json.loads(
        MANUFACTURING_V1_PATH.read_text(encoding="utf-8")
    )["catalog_sha256"]
    assert package["runtime_catalog"]["output_profile"]["validation_policy_marker"] == "roundtrip-1"


def test_job_router_preserves_only_a_closed_candidate_lane_with_jobs() -> None:
    from lfx.schema.data import Data

    component_cls = _component_class("data_analysis/retrieval_job_router.py")
    component = component_cls()
    component.plan_context = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "candidate_lane": "legacy_v1_compat",
            "plan": {"retrieval_jobs": [{"job_id": "job:test"}]},
            "unrelated_large_payload": {"rows": [{"secret": "must-not-propagate"}]},
        }
    )
    component.data_mode = "dummy"

    routed = component.route_jobs().data

    assert routed == {
        "contract_version": "pipeline.context.v1",
        "ok": True,
        "stage": "job_routing",
        "data_mode": "dummy",
        "candidate_lane": "legacy_v1_compat",
        "source_type": "dummy",
        "jobs": [{"job_id": "job:test"}],
    }


def test_job_router_splits_live_jobs_by_source_without_payload_duplication() -> None:
    from lfx.schema.data import Data

    component_cls = _component_class("data_analysis/retrieval_job_router.py")
    component = component_cls()
    component.plan_context = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "candidate_lane": "generic_v2",
            "plan": {
                "retrieval_jobs": [
                    {"job_id": "o", "source_type": "oracle"},
                    {"job_id": "h", "source_type": "http"},
                    {"job_id": "d", "source_type": "datalake"},
                    {"job_id": "g", "source_type": "goodocs"},
                ]
            },
            "unrelated_large_payload": {"rows": [{"secret": "must-not-propagate"}]},
        }
    )
    component.data_mode = "live"

    routes = {
        "oracle": component.oracle_jobs_out().data,
        "h_api": component.h_api_jobs_out().data,
        "datalake": component.datalake_jobs_out().data,
        "goodocs": component.goodocs_jobs_out().data,
    }

    assert {name: [item["job_id"] for item in value["jobs"]] for name, value in routes.items()} == {
        "oracle": ["o"],
        "h_api": ["h"],
        "datalake": ["d"],
        "goodocs": ["g"],
    }
    assert all("unrelated_large_payload" not in value for value in routes.values())


@pytest.mark.parametrize("candidate_lane", ["", "unknown", "legacy_v2"])
def test_job_router_rejects_missing_or_unknown_candidate_lane(candidate_lane: str) -> None:
    from lfx.schema.data import Data

    component_cls = _component_class("data_analysis/retrieval_job_router.py")
    component = component_cls()
    component.plan_context = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "candidate_lane": candidate_lane,
            "plan": {"retrieval_jobs": []},
        }
    )
    component.data_mode = "dummy"

    routed = component.route_jobs().data

    assert routed["ok"] is False
    assert routed["error"]["code"] == "plan_contract_error"
    assert routed["error"]["stage"] == "job_routing"


@pytest.mark.parametrize(
    ("candidate_lane", "catalog_path"),
    [
        ("legacy_v1", MANUFACTURING_V1_PATH),
        ("legacy_v1_compat", MANUFACTURING_V2_PATH),
    ],
)
def test_dummy_retriever_uses_embedded_fixture_only_for_valid_legacy_lane(
    candidate_lane: str,
    catalog_path: Path,
) -> None:
    from lfx.schema.data import Data

    component_cls = _component_class("data_analysis/dummy_source_retriever.py")
    component = component_cls()
    component.job_bundle = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "stage": "job_routing",
            "data_mode": "dummy",
            "candidate_lane": candidate_lane,
            "jobs": [],
        }
    )
    component.domain_bundle = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "domain_bundle": {
                "runtime_catalog": json.loads(catalog_path.read_text(encoding="utf-8"))
            },
        }
    )

    result = component.retrieve().data

    assert result["ok"] is True
    assert result["status"] == "selected"
    assert result["candidate_lane"] == candidate_lane
    assert result["source_results"] == []


@pytest.mark.parametrize("candidate_lane", ["generic_v2", "", "unknown"])
def test_dummy_retriever_fails_closed_for_non_fixture_lane(candidate_lane: str) -> None:
    from lfx.schema.data import Data

    component_cls = _component_class("data_analysis/dummy_source_retriever.py")
    component = component_cls()
    component.job_bundle = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "stage": "job_routing",
            "data_mode": "dummy",
            "candidate_lane": candidate_lane,
            "jobs": [],
        }
    )
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "order_sales"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    component.domain_bundle = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "domain_bundle": {"runtime_catalog": package["runtime_catalog"]},
        }
    )

    result = component.retrieve().data

    assert result["ok"] is False
    assert result["error"]["code"] == "source_missing"
    assert result["error"]["stage"] == "dummy_retrieval"
    assert result["error"]["details"]["reason"] == "dummy_fixture_unavailable"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("legacy_catalog_sha256", "0" * 64),
        ("planner_profile", "legacy_v1_compat_spoof"),
        ("domain_id", "other_domain"),
        ("compiler_version", "metadata-domain-compiler.v6.4"),
    ],
)
def test_dummy_retriever_revalidates_compat_controls_against_manual_injection(
    field: str,
    value: str,
) -> None:
    from lfx.schema.data import Data

    component_cls = _component_class("data_analysis/dummy_source_retriever.py")
    catalog = json.loads(MANUFACTURING_V2_PATH.read_text(encoding="utf-8"))
    if field in {"legacy_catalog_sha256", "planner_profile"}:
        catalog["output_profile"][field] = value
    else:
        catalog[field] = value
    component = component_cls()
    component.job_bundle = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "stage": "job_routing",
            "data_mode": "dummy",
            "candidate_lane": "legacy_v1_compat",
            "jobs": [],
        }
    )
    component.domain_bundle = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "domain_bundle": {"runtime_catalog": catalog},
        }
    )

    result = component.retrieve().data

    assert result["ok"] is False
    assert result["error"]["code"] == "source_missing"
    assert result["error"]["details"]["reason"] == "dummy_fixture_unavailable"


def test_generated_runtime_embeds_only_declared_phase_schemas() -> None:
    component_cls = _component_class("data_analysis/candidate_route_gate.py")
    namespace = component_cls.select_route.__globals__
    embedded = namespace["EMBEDDED_SCHEMAS"]
    assert set(embedded) == {"analysis-route.schema.json", "resolved-candidate-bundle.schema.json"}
    loaded = namespace["load_schema"]("resolved-candidate-bundle.schema.json")
    assert loaded == embedded["resolved-candidate-bundle.schema.json"]
    assert loaded is not embedded["resolved-candidate-bundle.schema.json"]


def test_flow_inventory_is_exact_decomposed_architecture() -> None:
    payload, namespace, flows = load_inventory()
    assert payload["contract_version"] == "flow.inventory.v1"
    assert tuple(flow["logical_key"] for flow in flows) == EXPECTED_FLOW_KEYS
    for flow in flows:
        key = flow["logical_key"]
        assert flow["endpoint_name"] == key
        assert flow["expected_uuid"] == str(uuid.uuid5(namespace, key))
        node_count = len(flow["native_nodes"]) + len(flow["custom_nodes"])
        if key == "metadata_v6_data_analysis":
            assert node_count == 32
            assert len(flow["edges"]) == 47
        else:
            assert node_count == 8
            assert len(flow["edges"]) == 7
        native_types = {node["type"] for node in flow["native_nodes"]}
        if key != "metadata_v6_data_analysis":
            assert native_types == {"ChatInput", "LanguageModel", "PromptTemplate", "ChatOutput"}
            model_node = next(node for node in flow["native_nodes"] if node["type"] == "LanguageModel")
            assert model_node["settings"]["model"][0]["name"] == "gemini-3.5-flash-lite"
            assert model_node["settings"]["temperature"] == 0.0
            assert model_node["settings"]["max_tokens"] == 8192
        assert flow["notes"]
        sources = {node["source"] for node in flow["custom_nodes"]}
        assert "langflow_components/data_analysis/00_trusted_analysis_engine.py" not in sources
        if key == "metadata_v6_data_analysis":
            specialized_input = next(node for node in flow["native_nodes"] if node["id"] == "specialized_function_text")
            assert specialized_input["type"] == "TextInput"
            assert "langflow_components/data_analysis/answer_facts_narrative.py" not in sources
            assert {
                "langflow_components/data_analysis/intent_prompt_context_builder.py",
                "langflow_components/data_analysis/answer_facts_context_builder.py",
                "langflow_components/data_analysis/answer_claim_validator.py",
                "langflow_components/shared/01_prompt_bundle_composer.py",
                "langflow_components/shared/02_conditional_llm_invoker.py",
            }.issubset(sources)
            custom_by_id = {node["id"]: node for node in flow["custom_nodes"]}
            assert custom_by_id["request_state_capsule"]["settings"]["allow_anonymous_multiturn"] is False
            assert custom_by_id["response_state_commit"]["settings"]["allow_anonymous_multiturn"] is False
            edges = {
                (edge["source"], edge["source_output"], edge["target"], edge["target_input"])
                for edge in flow["edges"]
            }
            assert ("answer_claim_validator", "answer_context", "response_state_commit", "answer_context") in edges
            assert ("response_state_commit", "response", "api_response", "response") in edges
            assert ("response_state_commit", "response", "gaia_output", "response") in edges
            assert ("intent_prompt_context_builder", "intent_prompt_context", "intent_prompt_bundle_composer", "runtime_context") in edges
            assert ("answer_prompt_context_builder", "answer_prompt_context", "answer_prompt_bundle_composer", "runtime_context") not in edges
            assert ("answer_facts_context_builder", "answer_prompt_context", "answer_prompt_bundle_composer", "runtime_context") in edges
            assert ("specialized_function_text", "text", "plan_compiler_validator", "specialized_function_text") in edges
        else:
            authoring = next(node for node in flow["custom_nodes"] if node["id"] == "simple_metadata_authoring_engine")
            generator = next(node for node in flow["custom_nodes"] if node["id"] == "simple_metadata_draft_generator")
            expected_kind = {
                "metadata_v6_domain_authoring": "domain",
                "metadata_v6_dataset_catalog_authoring": "dataset",
                "metadata_v6_main_filter_authoring": "main_filter",
            }[key]
            assert authoring["settings"]["authoring_kind"] == expected_kind
            assert authoring["settings"]["mode"] == "save"
            assert generator["settings"]["authoring_kind"] == expected_kind
            assert generator["settings"]["registry_source"].endswith("approved_source_registry.json")
            prompt_nodes = [node for node in flow["native_nodes"] if node["type"] == "PromptTemplate"]
            assert len(prompt_nodes) == 2
            assert all(node["expected_prompt_variables"] == [] for node in prompt_nodes)
            assert len([node for node in prompt_nodes if "specialized" in node["id"]]) == 1
            assert {
                "langflow_components/metadata_authoring/simple_metadata_draft_generator.py",
                "langflow_components/metadata_authoring/02_simple_metadata_authoring_engine.py",
                "langflow_components/metadata_authoring/01_authoring_message_presentation.py",
            } == sources
            edges = {
                (edge["source"], edge["source_output"], edge["target"], edge["target_input"])
                for edge in flow["edges"]
            }
            assert ("chat_input", "message", "simple_metadata_draft_generator", "input_message") in edges
            assert ("simple_metadata_draft_generator", "authoring_context", "simple_metadata_authoring_engine", "authoring_context") in edges
            assert ("simple_metadata_authoring_engine", "response", "message_presentation", "response") in edges
            assert ("message_presentation", "message", "chat_output", "input_value") in edges
            assert not [
                node["id"]
                for node in (*flow["native_nodes"], *flow["custom_nodes"])
                if "repair" in node["id"].casefold() or "fallback" in node["id"].casefold()
            ]


def test_flow_json_component_sources_match_canonical_files() -> None:
    _, _, flows = load_inventory()
    for flow_spec in flows:
        flow_path = ROOT / "flow_exports" / flow_export_filename(flow_spec["logical_key"])
        flow = json.loads(flow_path.read_text(encoding="utf-8"))
        nodes = {node["id"]: node for node in flow["data"]["nodes"]}
        for component in flow_spec["custom_nodes"]:
            embedded_source = nodes[component["id"]]["data"]["node"]["template"]["code"]["value"]
            canonical_source = (ROOT / component["source"]).read_text(encoding="utf-8")
            assert embedded_source == canonical_source, component["id"]
            assert nodes[component["id"]]["data"]["node"]["lf_version"] == "1.9.2"
        assert flow["last_tested_version"] == "1.9.2"


def test_answer_context_outputs_render_as_independent_handles() -> None:
    component_cls = _component_class("data_analysis/answer_facts_context_builder.py")
    outputs = {item.name: item for item in component_cls.outputs}
    assert set(outputs) == {"answer_facts_context", "answer_prompt_context"}
    assert all(getattr(item, "group_outputs", False) is True for item in outputs.values())


def test_state_scope_payload_and_prompt_boundaries_are_explicit() -> None:
    request_source = _source("data_analysis/request_state_capsule.py")
    message_source = _source("data_analysis/01_message_presentation.py")
    gaia_source = _source("data_analysis/02_gaia_output.py")
    merger_source = _source("data_analysis/source_contract_merger.py")
    intent_source = _source("data_analysis/common_intent_resolver.py")
    answer_source = _source("data_analysis/answer_facts_context_builder.py")
    assert 'storage_session_id = f"{environment}:{domain_id}:{session_id}"' in request_source
    assert 'name="allow_anonymous_multiturn"' in request_source
    assert 'len(session_id.strip()) < 20' in request_source
    assert '"contract_version": "response.message-link.v1"' in message_source
    assert 'validate_response_hash(' not in message_source
    assert '"response_sha256": str(response.get("response_sha256") or "")' not in message_source
    assert '"contract_version": "response.message-link.v1"' in gaia_source
    assert 'IntInput(name="peak_payload_limit_mb"' not in merger_source
    assert '"source_row_count":' in merger_source
    assert '"row_copy_count": 1' in merger_source
    assert '"raw_rows_in_llm_prompt": False' in merger_source
    assert "snapshots" not in intent_source[intent_source.index("class CommonIntentResolver") :]
    assert "snapshots" not in answer_source[answer_source.index("class AnswerFactsContextBuilder") :]


def test_anonymous_state_is_node_local_unless_explicitly_enabled() -> None:
    request_cls = _component_class("data_analysis/request_state_capsule.py")
    component = request_cls()
    assert next(item for item in request_cls.inputs if item.name == "allow_anonymous_multiturn").value is False
    first = component._state_store("anonymous", False)
    second = component._state_store("anonymous", False)
    assert first is not second
    assert component._state_store("anonymous", True) is component._state_store("anonymous", True)


def test_authoring_component_exposes_v2_full_and_patch_controls() -> None:
    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    values = {item.name: getattr(item, "value", None) for item in component_cls.inputs}
    assert values["metadata_contract_mode"] == "domain_package_v2"
    assert values["revision_policy"] == "auto_next"
    assert values["domain_collection"] == "agent_v6_domain_metadata"
    assert values["table_collection"] == "agent_v6_table_catalog"
    assert values["main_filter_collection"] == "agent_v6_main_filter"
    assert values["mode"] == "save"
    assert "bundle_collection" not in values
    assert "active_collection" not in values
    assert "pending_collection" not in values
    assert "inline_base_domain_bundle" in values
    assert values["trusted_blueprint_json"] == ""
    assert values["trusted_blueprint_sha256"] == ""
    assert "authoring_invocation_result" in values
    assert "language_model" not in values
    assert "domain_id" in values and "environment" in values


def test_authoring_component_accepts_safe_distinct_collection_names() -> None:
    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    component = component_cls()
    component.domain_collection = "orders_domain"
    component.table_collection = "orders_catalog"
    component.main_filter_collection = "orders_filter"

    assert component._collection_names() == {
        "domain_collection": "orders_domain",
        "table_collection": "orders_catalog",
        "main_filter_collection": "orders_filter",
    }

    component.main_filter_collection = "orders_catalog"
    with pytest.raises(Exception, match="safe and distinct"):
        component._collection_names()


def test_generated_authoring_prompt_uses_embedded_schema_without_external_globals() -> None:
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/authoring_prompt_context_builder.py")
    namespace = component_cls.build_context.__globals__
    source_text = "orders dataset canonical fields are ORDER_ID."
    component = component_cls()
    component.input_message = Message(text=source_text)
    component.authoring_kind = "dataset"
    component.mode = "prepare"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.approved_reference_context = _approved_reference_context("order_sales")
    context = component.build_context().data

    assert context["contract_version"] == "prompt.runtime-context.v1"
    assert context["purpose"] == "metadata_dataset_draft"
    assert context["invoke"] is True
    assert context["variables"]["source_text"] == source_text
    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    assert context["variables"]["source_sha256"] == source_sha256
    proposal_schema = context["variables"]["output_schema"]
    complete_schema = next(
        branch
        for branch in proposal_schema["oneOf"]
        if branch["properties"]["status"]["const"] == "complete"
    )
    assert complete_schema["properties"]["source_sha256"]["const"] == source_sha256
    assert set(complete_schema["properties"]["draft"]["properties"]) == {
        "dataset_cards"
    }
    assert "SCHEMAS" not in namespace
    assert "EMBEDDED_SCHEMAS" in namespace
    engine_source = _source("metadata_authoring/00_metadata_authoring_engine.py")
    assert "model.invoke" not in engine_source
    assert "language_model" not in engine_source
    assert "You compile" not in engine_source


def test_dataset_prompt_schema_is_repeatable_in_the_same_component_module() -> None:
    """Schema specialization must never mutate the cached embedded contract."""

    from lfx.schema.message import Message

    component_cls = _component_class(
        "metadata_authoring/authoring_prompt_context_builder.py"
    )
    registry = _approved_reference_context("order_sales")
    source_text = "주문과 상품 데이터에 어떤 업무 항목이 있는지 평소 말로 설명합니다."
    schemas = []
    for _ in range(2):
        component = component_cls()
        component.input_message = Message(text=source_text)
        component.authoring_kind = "dataset"
        component.mode = "prepare"
        component.source_grounding_mode = "freeform_llm"
        component.bootstrap_fragment = True
        component.domain_id = "order_sales"
        component.environment = "test"
        component.approved_reference_context = registry
        schemas.append(component.build_context().data["variables"]["output_schema"])

    assert schemas[0] == schemas[1]
    namespace = component_cls.build_context.__globals__
    pristine = namespace["load_schema"]("metadata-bootstrap-dataset-ir.schema.json")
    assert "properties" in pristine["$defs"]["datasetCard"]
    assert "oneOf" not in pristine["$defs"]["datasetCard"]


def test_dataset_prompt_field_enums_are_exact_per_dataset_not_family_union() -> None:
    """Two datasets may share a family without sharing every physical field."""

    from lfx.schema.data import Data
    from lfx.schema.message import Message

    reference = deepcopy(_approved_reference_context("order_sales").data)
    # Add a second sales_actual dataset with a strict subset of fields. This
    # leaves every approved semantic template/source binding untouched while
    # exposing the family-union over-authorization bug.
    narrow_dataset_id = "orders_summary"
    narrow_descriptor = deepcopy(reference["dataset_descriptors"]["orders"])
    narrow_descriptor["fields"] = {
        "CUSTOMER_ID": deepcopy(narrow_descriptor["fields"]["CUSTOMER_ID"])
    }
    reference["dataset_descriptors"][narrow_dataset_id] = narrow_descriptor
    reference["bindings"][narrow_dataset_id] = deepcopy(reference["bindings"]["orders"])
    reference["semantic_vocabulary"]["datasets"].append(
        {"id": narrow_dataset_id, "family": "sales_actual", "labels": []}
    )
    reference["semantic_vocabulary"]["datasets"] = sorted(
        reference["semantic_vocabulary"]["datasets"], key=lambda card: card["id"]
    )
    registry_material = {
        key: deepcopy(value)
        for key, value in reference.items()
        if key != "registry_sha256"
    }
    reference["registry_sha256"] = hashlib.sha256(
        json.dumps(
            registry_material,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()

    component_cls = _component_class(
        "metadata_authoring/authoring_prompt_context_builder.py"
    )
    component = component_cls()
    component.input_message = Message(
        text="주문 내역과 상품 기준정보에 들어 있는 항목을 등록해 주세요."
    )
    component.authoring_kind = "dataset"
    component.mode = "prepare"
    component.source_grounding_mode = "freeform_llm"
    component.bootstrap_fragment = True
    component.domain_id = "order_sales"
    component.environment = "test"
    component.approved_reference_context = Data(data=reference)

    draft_schema = _complete_proposal_draft_schema(
        component.build_context().data["variables"]["output_schema"]
    )
    branches = draft_schema["$defs"]["datasetCard"]["oneOf"]
    allowed_by_dataset = {
        branch["properties"]["dataset_id"]["enum"][0]: set(
            branch["properties"]["fields"]["items"]["properties"]["id"]["enum"]
        )
        for branch in branches
    }
    expected_by_dataset = {
        dataset_id: set(descriptor["fields"])
        for dataset_id, descriptor in reference["dataset_descriptors"].items()
    }

    assert allowed_by_dataset == expected_by_dataset
    assert allowed_by_dataset[narrow_dataset_id] == {"CUSTOMER_ID"}
    assert "ORDER_ID" not in allowed_by_dataset[narrow_dataset_id]


def test_main_filter_prompt_binds_target_id_enum_to_each_target_type() -> None:
    from lfx.schema.message import Message

    registry = _approved_reference_context("manufacturing")
    component_cls = _component_class(
        "metadata_authoring/authoring_prompt_context_builder.py"
    )
    component = component_cls()
    component.input_message = Message(
        text="현장 작업자가 자주 말하는 조회 조건과 표현을 등록해 주세요."
    )
    component.authoring_kind = "main_filter"
    component.mode = "prepare"
    component.source_grounding_mode = "freeform_llm"
    component.bootstrap_fragment = True
    component.domain_id = "manufacturing"
    component.environment = "test"
    component.approved_reference_context = registry

    draft_schema = _complete_proposal_draft_schema(
        component.build_context().data["variables"]["output_schema"]
    )
    item_schema = draft_schema["properties"]["alias_additions"]["items"]
    section_by_type = {
        "dataset": "datasets",
        "field": "fields",
        "metric": "metrics",
        "relation": "relations",
        "grain": "grains",
        "predicate": "predicates",
        "recipe": "recipes",
        "entity_group": "entity_groups",
    }
    expected = {
        target_type: sorted(
            card["id"]
            for card in registry.data["semantic_vocabulary"][section]
        )
        for target_type, section in section_by_type.items()
        if registry.data["semantic_vocabulary"][section]
    }
    observed = {}
    for branch in item_schema["oneOf"]:
        type_schema = branch["properties"]["target_type"]
        target_type = type_schema.get("const")
        if target_type is None:
            assert len(type_schema["enum"]) == 1
            target_type = type_schema["enum"][0]
        observed[target_type] = branch["properties"]["target_id"]["enum"]

    assert observed == expected
    assert "UPH" in observed["field"]
    assert "UPH" in observed["metric"]
    assert observed["field"] != observed["metric"]


def test_section_authoring_prompts_expose_only_owned_root_sections() -> None:
    component_cls = _component_class("metadata_authoring/authoring_prompt_context_builder.py")
    namespace = component_cls.build_context.__globals__

    dataset_schema = namespace["_authoring_output_schema"]("dataset")
    main_filter_schema = namespace["_authoring_output_schema"]("main_filter")
    full_schema = namespace["load_schema"]("metadata-authoring-draft.schema.json")

    def schema_refs(value: object) -> set[str]:
        refs: set[str] = set()
        if isinstance(value, dict):
            raw_ref = value.get("$ref")
            if isinstance(raw_ref, str) and raw_ref.startswith("#/$defs/"):
                refs.add(raw_ref.removeprefix("#/$defs/"))
            for child in value.values():
                refs.update(schema_refs(child))
        elif isinstance(value, list):
            for child in value:
                refs.update(schema_refs(child))
        return refs

    def compact_bytes(value: object) -> int:
        return len(
            json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        )

    assert set(dataset_schema["properties"]) == {"dataset_cards"}
    assert dataset_schema["required"] == ["dataset_cards"]
    assert dataset_schema["$defs"]["datasetCard"]["required"] == [
        "dataset_id",
        "fields",
    ]
    assert dataset_schema["$defs"]["fieldCard"]["required"] == ["id", "col"]
    assert set(main_filter_schema["properties"]) == {"alias_additions"}
    assert main_filter_schema["required"] == ["alias_additions"]
    main_filter_item = main_filter_schema["properties"]["alias_additions"]["items"]
    assert main_filter_item["required"] == [
        "target_type",
        "target_id",
        "expressions",
    ]
    for schema in (dataset_schema, main_filter_schema):
        assert schema_refs(schema) <= set(schema.get("$defs", {}))
        assert compact_bytes(schema) < compact_bytes(full_schema)
    dataset_prompt = (ROOT / "prompts" / "metadata_authoring" / "dataset_common_ko.md").read_text(encoding="utf-8")
    main_filter_prompt = (ROOT / "prompts" / "metadata_authoring" / "main_filter_common_ko.md").read_text(encoding="utf-8")
    assert "비전문 작업자" in dataset_prompt and "자유롭게" in dataset_prompt
    assert "비전문 작업자" in main_filter_prompt and "target_type" in main_filter_prompt


def test_bootstrap_prompt_fragments_are_closed_small_and_registry_minimal() -> None:
    component_cls = _component_class(
        "metadata_authoring/authoring_prompt_context_builder.py"
    )
    namespace = component_cls.build_context.__globals__
    source_sha256 = "a" * 64
    expected_properties = {
        "domain": {"display_name", "description"},
        "dataset": {"dataset_cards"},
        "main_filter": {"alias_additions"},
    }
    full_schema = namespace["load_schema"]("metadata-authoring-draft.schema.json")
    fragment_schemas = {}
    for kind, properties in expected_properties.items():
        proposal_schema = namespace["_authoring_output_schema"](
            kind,
            proposal_source_sha256=source_sha256,
            bootstrap_fragment=True,
        )
        complete_branch = next(
            branch
            for branch in proposal_schema["oneOf"]
            if branch["properties"]["status"]["const"] == "complete"
        )
        draft_schema = complete_branch["properties"]["draft"]
        fragment_schemas[kind] = draft_schema
        assert set(draft_schema["properties"]) == properties
        assert len(json.dumps(draft_schema, ensure_ascii=False)) < len(
            json.dumps(full_schema, ensure_ascii=False)
        )
    assert fragment_schemas["domain"]["required"] == [
        "display_name",
        "description",
    ]
    assert "contract_version" not in fragment_schemas["domain"]["properties"]
    domain_validator = namespace["Draft202012Validator"](
        fragment_schemas["domain"]
    )
    domain_validator.validate(
        {"display_name": "주문 매출 분석", "description": "주문과 매출을 분석합니다."}
    )
    assert list(
        domain_validator.iter_errors(
            {
                "display_name": "주문 매출 분석",
                "description": "주문과 매출을 분석합니다.",
                "metrics": {"MODEL_OWNED": {"aggregation": "sum"}},
            }
        )
    )
    assert fragment_schemas["dataset"]["required"] == ["dataset_cards"]
    assert fragment_schemas["main_filter"]["required"] == ["alias_additions"]
    alias_addition = fragment_schemas["main_filter"]["properties"][
        "alias_additions"
    ]["items"]
    assert set(alias_addition["properties"]) == {
        "target_type",
        "target_id",
        "expressions",
    }
    assert alias_addition["required"] == [
        "target_type",
        "target_id",
        "expressions",
    ]
    dataset_card = fragment_schemas["dataset"]["$defs"]["datasetCard"]
    field_card = fragment_schemas["dataset"]["$defs"]["fieldCard"]
    assert dataset_card["required"] == ["dataset_id", "fields"]
    assert "family" not in dataset_card["properties"]
    assert field_card["required"] == ["id", "col"]
    assert "roles" not in field_card["properties"]
    assert "type" not in field_card["properties"]
    assert not {
        "physical_aliases",
        "required_in_source",
        "nullable",
        "coercion",
        "timezone",
    } & set(field_card["properties"])
    assert set(dataset_card["properties"]) == {
        "dataset_id",
        "display_name",
        "fields",
    }
    assert set(field_card["properties"]) == {"id", "col"}
    assert not {
        "source_type",
        "source_adapter",
        "config_ref",
        "query_ref",
        "read_policy",
        "date_filter_contract",
        "date_policy",
        "default_detail_fields",
        "default_detail_columns",
        "fixture_only",
        "parameters",
        "time_scope",
        "upstream_bindings",
    } & set(dataset_card["properties"])

    manufacturing = json.loads(MANUFACTURING_V2_PATH.read_text(encoding="utf-8"))
    compact_dataset_ir = _compact_dataset_fragment(manufacturing["datasets"])
    namespace["Draft202012Validator"](
        fragment_schemas["dataset"]
    ).validate(compact_dataset_ir)
    compact_bytes = len(
        json.dumps(
            compact_dataset_ir,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    full_bytes = len(
        json.dumps(
            manufacturing["datasets"],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    assert compact_bytes < 32 * 1024
    assert compact_bytes < full_bytes * 0.60

    engine_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    engine_namespace = engine_cls.run_authoring.__globals__
    expand = engine_namespace["_expand_compact_dataset_fragment"]
    manufacturing_registry = _approved_reference_context("manufacturing").data
    dataset_descriptors = manufacturing_registry["dataset_descriptors"]
    canonical_card = deepcopy(compact_dataset_ir["dataset_cards"][0])
    reconciliation = {}
    canonical_expanded = expand(
        {"dataset_cards": [canonical_card]},
        dataset_descriptors=dataset_descriptors,
        reconciliation_out=reconciliation,
    )
    dataset_id = canonical_card["dataset_id"]
    expanded_dataset = canonical_expanded["datasets"][dataset_id]
    descriptor = dataset_descriptors[dataset_id]
    for key, value in descriptor["dataset_template"].items():
        assert expanded_dataset[key] == value
    assert expanded_dataset["family"] == descriptor["family"]
    assert expanded_dataset["fields"] == descriptor["fields"]
    assert reconciliation["compiler_owned_dataset_template_count"] == 1
    assert len(reconciliation["compiler_owned_dataset_templates_sha256"]) == 64

    model_policy_injection = deepcopy(canonical_card)
    model_policy_injection["default_detail_fields"] = [
        canonical_card["fields"][0]["id"]
    ]
    assert list(
        namespace["Draft202012Validator"](
            fragment_schemas["dataset"]
        ).iter_errors({"dataset_cards": [model_policy_injection]})
    )

    registry_completed_card = deepcopy(
        next(
            card
            for card in compact_dataset_ir["dataset_cards"]
            if card["dataset_id"] == "lot_status"
        )
    )
    registry_completed_field = "HOLD_STAT"
    registry_completed_card["fields"] = [
        field
        for field in registry_completed_card["fields"]
        if field["id"] != registry_completed_field
    ]
    reconciliation = {}
    registry_completed_expanded = expand(
        {"dataset_cards": [registry_completed_card]},
        dataset_descriptors=dataset_descriptors,
        reconciliation_out=reconciliation,
    )
    completed_field = registry_completed_expanded["datasets"]["lot_status"][
        "fields"
    ][registry_completed_field]
    approved_completed_field = dataset_descriptors["lot_status"]["fields"][
        registry_completed_field
    ]
    assert completed_field["physical_column"] == approved_completed_field[
        "physical_column"
    ]
    assert completed_field["semantic_type"] == approved_completed_field[
        "semantic_type"
    ]
    assert completed_field["roles"] == approved_completed_field["roles"]
    assert {"filter", "group", "output"} <= set(completed_field["roles"])
    assert registry_completed_expanded["datasets"]["lot_status"][
        "default_detail_fields"
    ] == dataset_descriptors["lot_status"]["dataset_template"][
        "default_detail_fields"
    ]
    assert reconciliation["completed_field_count"] >= 1
    assert len(reconciliation["completed_fields_sha256"]) == 64

    mismatched_binding = deepcopy(registry_completed_card)
    mismatched_binding["fields"][0]["col"] = "UNAPPROVED_PHYSICAL_COLUMN"
    with pytest.raises(engine_namespace["ContractError"]) as registry_drift:
        expand(
            {"dataset_cards": [mismatched_binding]},
            dataset_descriptors=dataset_descriptors,
        )
    assert registry_drift.value.code == "metadata_registry_drift"

    corrected_id = deepcopy(registry_completed_card)
    corrected_id["fields"][0]["id"] = "MODEL_INVENTED_ID"
    corrected_reconciliation = {}
    corrected_binding = expand(
        {"dataset_cards": [corrected_id]},
        dataset_descriptors=dataset_descriptors,
        reconciliation_out=corrected_reconciliation,
    )
    corrected_field_id = registry_completed_card["fields"][0]["id"]
    assert corrected_binding["datasets"]["lot_status"]["fields"][corrected_field_id][
        "physical_column"
    ] == dataset_descriptors["lot_status"]["fields"][corrected_field_id]["physical_column"]
    assert corrected_reconciliation["corrected_binding_count"] == 1
    assert len(corrected_reconciliation["corrected_bindings_sha256"]) == 64

    source_alias_card = deepcopy(
        next(
            card
            for card in compact_dataset_ir["dataset_cards"]
            if card["dataset_id"] == "eqp_uph"
        )
    )
    source_alias_mode = next(
        field for field in source_alias_card["fields"] if field["id"] == "MODE"
    )
    source_alias_mode["col"] = "PROD_TYP"
    source_alias_reconciliation = {}
    source_alias_expanded = expand(
        {"dataset_cards": [source_alias_card]},
        dataset_descriptors=dataset_descriptors,
        reconciliation_out=source_alias_reconciliation,
    )
    assert source_alias_expanded["datasets"]["eqp_uph"]["fields"]["MODE"][
        "physical_column"
    ] == "MODE"
    assert source_alias_reconciliation["applied_exclusion_count"] == 1

    conflicting_known_binding = deepcopy(registry_completed_card)
    first_field = conflicting_known_binding["fields"][0]
    second_field = conflicting_known_binding["fields"][1]
    first_field["col"] = second_field["col"]
    with pytest.raises(engine_namespace["ContractError"]):
        expand(
            {"dataset_cards": [conflicting_known_binding]},
            dataset_descriptors=dataset_descriptors,
        )

    unapproved_card = deepcopy(
        next(
            card
            for card in compact_dataset_ir["dataset_cards"]
            if card["dataset_id"] == "equipment_assign"
        )
    )
    unapproved_card["fields"].append({"id": "PKGSIZE", "col": "PKGSIZE"})
    unapproved_reconciliation = {}
    unapproved_expanded = expand(
        {"dataset_cards": [unapproved_card]},
        dataset_descriptors=dataset_descriptors,
        reconciliation_out=unapproved_reconciliation,
    )
    assert "PKGSIZE" not in unapproved_expanded["datasets"]["equipment_assign"]["fields"]
    assert unapproved_reconciliation["applied_exclusion_count"] == 1
    assert len(unapproved_reconciliation["applied_exclusions_sha256"]) == 64

    unlisted_card = deepcopy(unapproved_card)
    unlisted_card["fields"][-1] = {
        "id": "UNLISTED_SOURCE_COLUMN",
        "col": "UNLISTED_SOURCE_COLUMN",
    }
    with pytest.raises(engine_namespace["ContractError"]) as unlisted_drift:
        expand(
            {"dataset_cards": [unlisted_card]},
            dataset_descriptors=dataset_descriptors,
        )
    assert unlisted_drift.value.code == "metadata_registry_drift"

    cross_dataset_exclusion = deepcopy(registry_completed_card)
    cross_dataset_exclusion["fields"].append({"id": "PKGSIZE", "col": "PKGSIZE"})
    with pytest.raises(engine_namespace["ContractError"]) as dataset_scoped:
        expand(
            {"dataset_cards": [cross_dataset_exclusion]},
            dataset_descriptors=dataset_descriptors,
        )
    assert dataset_scoped.value.code == "metadata_registry_drift"

    colliding_exclusion_descriptors = deepcopy(dataset_descriptors)
    colliding_exclusion_descriptors["equipment_assign"]["proposal_exclusions"][
        "EQP_ID"
    ] = {"reason_code": "source_projection_not_registered"}
    with pytest.raises(engine_namespace["ContractError"]):
        expand(
            {"dataset_cards": [unapproved_card]},
            dataset_descriptors=colliding_exclusion_descriptors,
        )

    missing_same_dataset_descriptor = deepcopy(dataset_descriptors)
    missing_same_dataset_descriptor["lot_status"]["fields"].pop(
        registry_completed_field
    )
    with pytest.raises(engine_namespace["ContractError"]):
        expand(
            {"dataset_cards": [registry_completed_card]},
            dataset_descriptors=missing_same_dataset_descriptor,
        )

    registry = _approved_reference_context("order_sales")
    source_texts = {
        "domain": "주문과 매출을 분석하는 업무 도메인입니다.",
        "dataset": "주문과 상품 데이터셋 및 컬럼을 사용합니다.",
        "main_filter": "상품 분류를 주요 필터로 사용합니다.",
    }
    contexts = {
        kind: _bootstrap_prompt_context(
            kind=kind,
            source_text=source_text,
            domain_id="order_sales",
            environment="test",
            approved_reference_context=registry,
        ).data
        for kind, source_text in source_texts.items()
    }
    expected_vocabulary = registry.data["semantic_vocabulary"]
    expected_registry_sha256 = registry.data["registry_sha256"]
    forbidden_registry_payload = (
        "semantic_templates",
        "formula",
        "source_binding",
        "config_ref",
        "query_ref",
        "dataset_descriptors",
        "field_descriptors",
        "physical_column",
        "semantic_type",
        "proposal_exclusions",
        "source_adapter",
        "source_type",
    )
    for kind in ("domain", "dataset", "main_filter"):
        variables = contexts[kind]["variables"]
        assert variables["approved_semantic_vocabulary"] == expected_vocabulary
        assert variables["source_registry_sha256"] == expected_registry_sha256
        assert "approved_dataset_ids" not in variables
        vocabulary_serialized = json.dumps(
            variables["approved_semantic_vocabulary"], ensure_ascii=False
        )
        for forbidden in forbidden_registry_payload:
            assert forbidden not in vocabulary_serialized
        serialized_variables = json.dumps(variables, ensure_ascii=False)
        for forbidden in forbidden_registry_payload:
            assert forbidden not in serialized_variables
    dataset_output_schema = contexts["dataset"]["variables"]["output_schema"]
    complete_branch = next(
        branch
        for branch in dataset_output_schema["oneOf"]
        if branch["properties"]["status"]["const"] == "complete"
    )
    dataset_card_branches = complete_branch["properties"]["draft"]["$defs"][
        "datasetCard"
    ]["oneOf"]
    assert sorted(
        branch["properties"]["dataset_id"]["enum"][0]
        for branch in dataset_card_branches
    ) == sorted(registry.data["bindings"])
    serialized_dataset_variables = json.dumps(contexts["dataset"]["variables"], ensure_ascii=False)
    assert "config_ref" not in serialized_dataset_variables
    assert "query_ref" not in serialized_dataset_variables
    assert "dataset_descriptors" not in serialized_dataset_variables
    assert "field_descriptors" not in serialized_dataset_variables
    assert "physical_column" not in serialized_dataset_variables
    assert "semantic_type" not in serialized_dataset_variables
    assert "proposal_exclusions" not in serialized_dataset_variables
    assert "PKGSIZE" not in serialized_dataset_variables
    assert "source_projection_not_registered" not in serialized_dataset_variables

    manufacturing_registry = _approved_reference_context("manufacturing")
    manufacturing_dataset_context = _bootstrap_prompt_context(
        kind="dataset",
        source_text="작업자는 제조 데이터와 업무 항목을 평소 말로 설명합니다.",
        domain_id="manufacturing",
        environment="test",
        approved_reference_context=manufacturing_registry,
    ).data
    manufacturing_complete = next(
        branch
        for branch in manufacturing_dataset_context["variables"]["output_schema"][
            "oneOf"
        ]
        if branch["properties"]["status"]["const"] == "complete"
    )
    manufacturing_dataset_branches = manufacturing_complete["properties"][
        "draft"
    ]["$defs"]["datasetCard"]["oneOf"]
    target_branch = next(
        branch
        for branch in manufacturing_dataset_branches
        if branch["properties"]["dataset_id"]["enum"] == ["target"]
    )
    target_fields = target_branch["properties"]["fields"]["items"][
        "properties"
    ]
    for field_key in ("id", "col"):
        assert "MCP_NO" in target_fields[field_key]["enum"]
        assert "DEVICE" not in target_fields[field_key]["enum"]
    # Dataset presentation/detail policy is compiler-owned and therefore does
    # not cross the LLM-facing compact IR boundary.
    assert "default_detail_fields" not in target_branch["properties"]
    assert "default_detail_columns" not in target_branch["properties"]

    tampered = deepcopy(contexts["domain"])
    tampered["variables"]["approved_semantic_vocabulary"]["metrics"][0]["labels"] = ["변조"]
    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    component = component_cls()
    component.approved_reference_context = registry
    component.authoring_source_context = tampered
    namespace = component_cls.run_authoring.__globals__
    with pytest.raises(namespace["ContractError"]) as vocabulary_tamper:
        namespace["_bootstrap_context_payload"](
            component,
            input_name="authoring_source_context",
            kind="domain",
            purpose="metadata_domain_draft",
            domain_id="order_sales",
            environment="test",
        )
    assert vocabulary_tamper.value.stage == "metadata_source_context"

    template_tampered_registry = deepcopy(registry.data)
    first_metric_id = sorted(template_tampered_registry["semantic_templates"]["metrics"])[0]
    template_tampered_registry["semantic_templates"]["metrics"][first_metric_id][
        "unit"
    ] = "tampered-unit"
    component = component_cls()
    component.approved_reference_context = template_tampered_registry
    component.authoring_source_context = contexts["domain"]
    with pytest.raises(namespace["ContractError"]) as template_tamper:
        namespace["_bootstrap_context_payload"](
            component,
            input_name="authoring_source_context",
            kind="domain",
            purpose="metadata_domain_draft",
            domain_id="order_sales",
            environment="test",
        )
    assert template_tamper.value.stage == "metadata_source_context"

    input_names = {
        "domain": "authoring_source_context",
        "dataset": "bootstrap_dataset_source_context",
        "main_filter": "bootstrap_main_filter_source_context",
    }
    purposes = {
        "domain": "metadata_domain_draft",
        "dataset": "metadata_dataset_draft",
        "main_filter": "metadata_main_filter_draft",
    }
    for kind in ("domain", "dataset", "main_filter"):
        hash_tampered = deepcopy(contexts[kind])
        hash_tampered["variables"]["source_registry_sha256"] = "0" * 64
        component = component_cls()
        component.approved_reference_context = registry
        setattr(component, input_names[kind], hash_tampered)
        with pytest.raises(namespace["ContractError"]) as registry_hash_tamper:
            namespace["_bootstrap_context_payload"](
                component,
                input_name=input_names[kind],
                kind=kind,
                purpose=purposes[kind],
                domain_id="order_sales",
                environment="test",
            )
        assert registry_hash_tamper.value.stage == "metadata_source_context"


def test_authoring_json_parser_accepts_one_framed_object_and_rejects_repairs() -> None:
    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    namespace = component_cls.run_authoring.__globals__
    parse = namespace["_json_object"]
    contract_error = namespace["ContractError"]

    assert parse('result:\n```json\n{"label":"{정상}"}\n```\ndone') == {
        "label": "{정상}"
    }
    assert parse({"datasets": {"products": {"display_name": "상품"}}}) == {
        "datasets": {"products": {"display_name": "상품"}}
    }

    invalid_values = (
        '{} {}',
        '[{"ok":true}]',
        r'{"label":"\u12G4"}',
        "{'label':'single quotes'}",
        '{"truncated":true',
        '{"trailing":true,}',
    )
    for raw in invalid_values:
        with pytest.raises(contract_error):
            parse(raw)

    source = _source("metadata_authoring/00_metadata_authoring_engine.py")
    assert source.count("\ndef _json_object(text):") == 1
    assert "_legacy_json_object" not in source


def test_authoring_engine_has_no_provider_specific_invoke_path() -> None:
    source = _source("metadata_authoring/00_metadata_authoring_engine.py")
    assert "ChatGoogleGenerativeAI" not in source
    assert "response_mime_type" not in source
    assert ".invoke(" not in source
    assert "authoring_invocation_result" in source


def test_shared_invoker_is_the_only_single_call_boundary() -> None:
    source = _source("shared/02_conditional_llm_invoker.py")
    assert source.count("runner.invoke(messages)") == 1
    assert '"automatic_retry_count": 0' in source
    assert "for attempt" not in source.casefold()


def test_alias_only_main_filter_prepare_compiles_source_manifest_with_zero_llm_calls() -> None:
    from lfx.schema.data import Data
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "order_sales"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    source_text = """기존 주문·매출 도메인의 메인 필터 별칭을 추가합니다.
별칭 카드의 안정 식별자는 field:CATEGORY이고 대상 유형은 field, 대상 키는 CATEGORY입니다.
사용자가 '카테고리', '상품군', '상품 분류'라고 말하면 CATEGORY 필드로 해석하세요.
aliases 섹션만 수정하고 데이터셋, 지표, 관계, 출력 정책은 그대로 유지하세요.
"""
    namespace = component_cls.run_authoring.__globals__
    standalone_manifest = namespace["extract_authoring_source_manifest"](source_text)
    assert standalone_manifest["inventories"]["alias_bindings"] == [
        {"alias": "상품 분류", "target": "CATEGORY"},
        {"alias": "상품군", "target": "CATEGORY"},
        {"alias": "카테고리", "target": "CATEGORY"},
    ]
    assert namespace["_v2_alias_only_manifest_patch"](standalone_manifest) == {
        "aliases": {
            "상품 분류": "CATEGORY",
            "상품군": "CATEGORY",
            "카테고리": "CATEGORY",
        }
    }
    component = component_cls()
    component.input_message = Message(text=source_text)
    component.language_model = None
    component.authoring_kind = "main_filter"
    component.source_grounding_mode = "explicit_inventory"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.inline_base_domain_bundle = Data(data=package)
    component.approved_reference_context = _approved_reference_context("order_sales")
    component.mode = "prepare"
    component.dry_run = True

    response = component.run_authoring().data

    assert response["status"] == "ok", json.dumps(response, ensure_ascii=False, indent=2)
    assert response["llm_usage"] == {
        "draft_llm_calls": 0,
        "annotation_llm_calls": 0,
        "repair_llm_calls": 0,
    }


def test_dataset_prepare_rejects_empty_explicit_inventory_before_model_call() -> None:
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")

    class NeverModel:
        calls = 0

        def invoke(self, prompt: str) -> str:
            self.calls += 1
            return '{}'

    model = NeverModel()
    component = component_cls()
    component.input_message = Message(text="products의 표시 이름을 바꿔 주세요.")
    component.language_model = model
    component.authoring_kind = "dataset"
    component.source_grounding_mode = "explicit_inventory"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.mode = "prepare"
    component.dry_run = True

    response = component.run_authoring().data

    assert response["status"] == "error"
    assert response["stage"] == "metadata_source_inventory"
    assert response["error"]["code"] == "metadata_dependency_error"
    assert response["error"]["details"]["dataset_count"] == 0
    assert response["error"]["details"]["field_bindings"] == 0
    assert model.calls == 0


def test_freeform_dataset_patch_authorization_uses_only_active_catalog_ids() -> None:
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "manufacturing"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    base = namespace["runtime_catalog_v2_to_authoring_draft"](
        package["runtime_catalog"]
    )
    source_manifest = namespace["_freeform_authoring_manifest"](
        "생산 데이터셋의 표시 이름을 현장 용어에 맞게 바꿔 주세요."
    )
    authorization = namespace[
        "_freeform_dataset_patch_authorization_manifest"
    ](source_manifest, base)

    assert authorization["source_sha256"] == source_manifest["source_sha256"]
    assert set(authorization["inventories"]["datasets"]) == set(
        base["datasets"]
    )
    assert authorization["inventories"]["dataset_fields"]["production"] == sorted(
        base["datasets"]["production"]["fields"]
    )
    assert authorization["manifest_sha256"] == namespace["sha256_json"](
        {key: value for key, value in authorization.items() if key != "manifest_sha256"}
    )

    normalize = namespace["normalize_authoring_section_patch_shorthand"]
    normalized = normalize(
        authorization,
        {"datasets": {"production": {"display_name": "생산 실적 이력"}}},
        "dataset",
        base_draft=base,
    )
    assert normalized["datasets"]["production"]["display_name"] == "생산 실적 이력"

    with pytest.raises(namespace["AuthoringSourceManifestError"]) as unknown:
        normalize(
            authorization,
            {"datasets": {"invented_dataset": {"display_name": "금지"}}},
            "dataset",
            base_draft=base,
        )
    assert unknown.value.code == "authoring_dataset_target_unknown"


def test_metric_binding_string_requires_exact_approved_semantic_reference() -> None:
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "manufacturing"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    draft = namespace["runtime_catalog_v2_to_authoring_draft"](
        package["runtime_catalog"]
    )
    draft["metrics"]["WIP_QTY"]["source_binding"] = "wip.WIP_QTY"
    draft["metrics"]["WIP_BOH_QTY"]["source_binding"] = "wip.WIP_QTY"
    vocabulary = _approved_reference_context("manufacturing").data[
        "semantic_vocabulary"
    ]

    completed, evidence = namespace[
        "_complete_unambiguous_metric_bindings"
    ](draft, vocabulary)

    assert completed["metrics"]["WIP_QTY"]["source_binding"] == {
        "dataset_family": "wip",
        "field": "WIP_QTY",
    }
    assert completed["metrics"]["WIP_BOH_QTY"]["source_binding"] == {
        "dataset_family": "wip",
        "field": "WIP_QTY",
    }
    assert evidence["completed_count"] == 2
    assert evidence["corrected_count"] == 0
    unknown = deepcopy(draft)
    unknown["metrics"]["WIP_QTY"]["source_binding"] = "wip.NOT_REGISTERED"
    with pytest.raises(namespace["ContractError"]) as unresolved:
        namespace["_complete_unambiguous_metric_bindings"](unknown, vocabulary)
    assert unresolved.value.stage == "metadata_semantic_reference_normalization"


def test_metric_binding_full_card_is_preserved_without_guessing() -> None:
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "manufacturing"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    draft = namespace["runtime_catalog_v2_to_authoring_draft"](
        package["runtime_catalog"]
    )
    before = deepcopy(draft["metrics"]["WIP_BOH_QTY"]["source_binding"])

    reconciled, evidence = namespace[
        "_complete_unambiguous_metric_bindings"
    ](
        draft,
        _approved_reference_context("manufacturing").data["semantic_vocabulary"],
    )

    assert reconciled["metrics"]["WIP_BOH_QTY"]["source_binding"] == before
    assert evidence["completed_count"] == 0
    assert evidence["corrected_count"] == 0
    assert evidence["preserved_full_card_count"] >= 1


def test_bootstrap_domain_annotation_expands_only_approved_templates_with_hash_evidence() -> None:
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    registry = _approved_reference_context("order_sales").data
    annotation = {
        "display_name": "주문·매출 분석",
        "description": "주문, 환불, 목표를 함께 분석하는 업무 영역입니다.",
    }

    expanded, evidence = namespace["_expand_bootstrap_domain_annotation"](
        annotation,
        semantic_templates=registry["semantic_templates"],
        semantic_vocabulary=registry["semantic_vocabulary"],
    )

    templates = registry["semantic_templates"]
    assert expanded["display_name"] == annotation["display_name"]
    assert expanded["description"] == annotation["description"]
    assert expanded["locale"] == templates["locale"]
    assert expanded["timezone"] == templates["timezone"]
    assert expanded["output_profile"] == templates["planner_policy"]
    for section in (
        "metrics",
        "relations",
        "entity_groups",
        "grains",
        "orderings",
        "predicates",
        "recipes",
        "aliases",
    ):
        assert expanded[section] == templates[section]
        assert evidence["section_counts"][section] == len(templates[section])
    assert evidence == {
        "contract_version": "metadata.domain-template-expansion.v1",
        "template_contract_version": "metadata.authoring.semantic-templates.v1",
        "annotation_sha256": namespace["sha256_json"](annotation),
        "semantic_templates_sha256": namespace["sha256_json"](templates),
        "planner_policy_sha256": namespace["sha256_json"](
            templates["planner_policy"]
        ),
        "section_counts": evidence["section_counts"],
    }

    executable_injection = {
        **annotation,
        "metrics": {"MODEL_OWNED": {"aggregation": "sum"}},
    }
    with pytest.raises(namespace["ContractError"]) as rejected:
        namespace["_expand_bootstrap_domain_annotation"](
            executable_injection,
            semantic_templates=templates,
            semantic_vocabulary=registry["semantic_vocabulary"],
        )
    assert rejected.value.stage == "metadata_authoring"


def test_bootstrap_main_filter_ir_requires_typed_targets_and_disambiguates_duplicate_ids() -> None:
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    vocabulary = deepcopy(
        _approved_reference_context("manufacturing").data["semantic_vocabulary"]
    )
    assert "UPH" in {card["id"] for card in vocabulary["fields"]}
    assert "UPH" in {card["id"] for card in vocabulary["metrics"]}
    fragment = {
        "alias_additions": [
            {
                "target_type": "field",
                "target_id": "UPH",
                "expressions": ["원본 UPH 값"],
            },
            {
                "target_type": "metric",
                "target_id": "UPH",
                "expressions": ["시간당 생산성 지표"],
            },
        ]
    }
    evidence = {}

    expanded = namespace["_expand_compact_main_filter_fragment"](
        fragment,
        approved_semantic_vocabulary=vocabulary,
        reconciliation_out=evidence,
    )

    assert set(expanded["aliases"]) == {"field:UPH", "metric:UPH"}
    assert expanded["aliases"]["field:UPH"]["target_type"] == "field"
    assert expanded["aliases"]["field:UPH"]["target_key"] == "UPH"
    assert expanded["aliases"]["metric:UPH"]["target_type"] == "metric"
    assert expanded["aliases"]["metric:UPH"]["target_key"] == "UPH"
    assert evidence == {
        "contract_version": "metadata.main-filter-ir-expansion.v1",
        "input_count": 2,
        "canonical_alias_count": 2,
        "canonical_targets_sha256": namespace["sha256_json"](
            ["field:UPH", "metric:UPH"]
        ),
    }

    missing_target_type = {
        "alias_additions": [
            {"target_id": "UPH", "expressions": ["모호한 UPH"]}
        ]
    }
    with pytest.raises(namespace["ContractError"]) as rejected:
        namespace["_validate_bootstrap_fragment"](
            missing_target_type,
            "main_filter",
            semantic_vocabulary=vocabulary,
        )
    assert rejected.value.code == "metadata_schema_error"


def test_bootstrap_alias_shorthand_is_exact_and_collision_safe() -> None:
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    package = json.loads(
        (
            ROOT / "metadata" / "domain_packs" / "manufacturing"
            / "compiled" / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    draft = namespace["runtime_catalog_v2_to_authoring_draft"](
        package["runtime_catalog"]
    )
    compiler_patch_base = deepcopy(draft)
    vocabulary = _approved_reference_context("manufacturing").data[
        "semantic_vocabulary"
    ]
    draft["aliases"] = {"DATE": {"expressions": ["  날짜 ", "날짜", " 기준일 "]}}

    normalized, evidence = namespace["_normalize_bootstrap_alias_shorthand"](
        draft, vocabulary
    )
    expected = {
        "target_type": "field",
        "target_key": "DATE",
        "values": [
            {"text": "기준일", "priority": 100},
            {"text": "날짜", "priority": 100},
        ],
        "normalization": ["unicode_nfkc", "trim", "collapse_space", "latin_casefold"],
        "match": "bounded_longest",
        "conflict": "fail_ambiguous",
        "provenance_source": "natural_authoring",
    }
    assert normalized["aliases"] == {"field:DATE": expected}
    assert evidence["normalized_count"] == 1

    collision = deepcopy(draft)
    collision["aliases"]["field:DATE"] = {
        **deepcopy(expected),
        "values": [{"text": "작업일", "priority": 100}],
        "provenance_source": "main_filters",
    }
    merged, _ = namespace["_normalize_bootstrap_alias_shorthand"](
        collision, vocabulary
    )
    assert merged["aliases"]["field:DATE"]["values"] == [
        {"text": "작업일", "priority": 100},
        {"text": "기준일", "priority": 100},
        {"text": "날짜", "priority": 100},
    ]
    assert merged["aliases"]["field:DATE"]["provenance_source"] == "main_filters"

    typed_patch = namespace["_expand_compact_main_filter_fragment"](
        {
            "alias_additions": [
                {
                    "target_type": "field",
                    "target_id": "MODE",
                    "expressions": ["현장 모드 기준"],
                }
            ]
        },
        approved_semantic_vocabulary=vocabulary,
    )
    merged_typed_patch = namespace["_merge_typed_main_filter_patch"](
        compiler_patch_base, typed_patch
    )
    assert merged_typed_patch["aliases"]["field:MODE"]["values"][-1] == {
        "text": "현장 모드 기준",
        "priority": 100,
    }
    assert merged_typed_patch["aliases"]["field:MODE"]["provenance_source"] == (
        "main_filters"
    )

    conflict = deepcopy(collision)
    conflict["aliases"]["field:DATE"]["match"] = "exact"
    with pytest.raises(namespace["ContractError"]):
        namespace["_normalize_bootstrap_alias_shorthand"](conflict, vocabulary)

    preserved = deepcopy(draft)
    preserved["aliases"] = {
        "field:DATE": {
            "target_type": "field",
            "target_key": "DATE",
            "values": ["날짜"],
        }
    }
    preserved_before = deepcopy(preserved["aliases"])
    preserved_after, _ = namespace["_normalize_bootstrap_alias_shorthand"](
        preserved, vocabulary
    )
    assert preserved_after["aliases"] == preserved_before

    unicode_variant = deepcopy(draft)
    unicode_variant["aliases"] = {
        "DATE": {"expressions": ["ＤＡＴＥ", "date", " Date "]}
    }
    unicode_normalized, unicode_evidence = namespace[
        "_normalize_bootstrap_alias_shorthand"
    ](unicode_variant, vocabulary)
    assert unicode_normalized["aliases"]["field:DATE"]["values"] == [
        {"text": "DATE", "priority": 100}
    ]
    assert unicode_normalized["aliases"]["field:DATE"]["normalization"] == [
        "unicode_nfkc",
        "trim",
        "collapse_space",
        "latin_casefold",
    ]
    assert unicode_evidence["normalized_count"] == 1


def test_natural_alias_conflicts_preserve_baseline_and_drop_cross_target_values() -> None:
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    policy = {
        "normalization": ["unicode_nfkc", "trim", "collapse_space", "latin_casefold"],
        "match": "bounded_longest",
        "conflict": "fail_ambiguous",
        "provenance_source": "natural_authoring",
    }
    baseline = {
        "field:BASE": {
            "target_type": "field",
            "target_key": "BASE",
            "values": [{"text": "승인 공통 표현", "priority": 10}],
            **policy,
        }
    }
    candidate = deepcopy(baseline)
    candidate["field:BASE"]["values"].extend(
        [
            {"text": "안전한 기준", "priority": 100},
            {"text": "  안전한   기준 ", "priority": 100},
        ]
    )
    candidate["field:OTHER"] = {
        "target_type": "field",
        "target_key": "OTHER",
        "values": [
            {"text": "승인 공통 표현", "priority": 100},
            {"text": "교차 표현", "priority": 100},
            {"text": "다른 안전 표현", "priority": 100},
        ],
        **policy,
    }
    candidate["metric:THIRD"] = {
        "target_type": "metric",
        "target_key": "THIRD",
        "values": [
            {"text": "교차 표현", "priority": 100},
            {"text": "지표 안전 표현", "priority": 100},
        ],
        **policy,
    }

    resolved, evidence = namespace["_resolve_natural_alias_conflicts"](
        candidate, baseline
    )

    assert resolved["field:BASE"]["values"][0] == baseline["field:BASE"]["values"][0]
    assert len(resolved["field:BASE"]["values"]) == 2
    assert resolved["field:OTHER"]["values"] == [
        {"text": "다른 안전 표현", "priority": 100}
    ]
    assert resolved["metric:THIRD"]["values"] == [
        {"text": "지표 안전 표현", "priority": 100}
    ]
    assert evidence["discarded_baseline_conflict_count"] == 1
    assert evidence["discarded_cross_target_count"] == 2
    assert evidence["duplicate_same_target_count"] == 1


def test_bootstrap_alias_shorthand_zero_or_multiple_exact_targets_fail_closed() -> None:
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    package = json.loads(
        (
            ROOT / "metadata" / "domain_packs" / "manufacturing"
            / "compiled" / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    draft = namespace["runtime_catalog_v2_to_authoring_draft"](
        package["runtime_catalog"]
    )
    vocabulary = deepcopy(
        _approved_reference_context("manufacturing").data["semantic_vocabulary"]
    )
    draft["aliases"] = {"NOT_REGISTERED": {"expressions": ["없는 대상"]}}
    with pytest.raises(namespace["ContractError"]) as missing:
        namespace["_normalize_bootstrap_alias_shorthand"](draft, vocabulary)
    assert missing.value.details["candidate_count"] == 0

    draft["aliases"] = {"DATE": {"expressions": ["날짜"]}}
    draft["metrics"]["DATE"] = {"metric_id": "DATE"}
    vocabulary["metrics"].append({"id": "DATE", "labels": []})
    vocabulary["metrics"] = sorted(vocabulary["metrics"], key=lambda card: card["id"])
    with pytest.raises(namespace["ContractError"]) as ambiguous:
        namespace["_normalize_bootstrap_alias_shorthand"](draft, vocabulary)
    assert ambiguous.value.details["candidate_count"] == 2


def test_split_invocation_requires_matching_schema_binding_evidence() -> None:
    from lfx.schema.data import Data

    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    schema = {"type": "object", "additionalProperties": False, "properties": {}}
    schema_sha256 = namespace["sha256_json"](schema)
    runtime_context_sha256 = "2" * 64
    component = component_cls()
    component.authoring_invocation_result = Data(data={
        "contract_version": "llm.invocation.v1",
        "purpose": "metadata_domain_draft",
        "status": "ok",
        "llm_calls": 1,
        "prompt_bundle_sha256": "1" * 64,
        "runtime_context_sha256": runtime_context_sha256,
        "provider_schema_binding": "portable_prompt_and_compiler_validation",
        "schema_binding_evidence": {
            "contract_version": "llm.schema-binding.evidence.v1",
            "binding_status": "portable_prompt_and_compiler_validation",
            "projection": "none",
            "authoritative_schema_sha256": schema_sha256,
            "provider_schema_sha256": "",
        },
        "response_text": "{}",
        "response_sha256": hashlib.sha256(b"{}").hexdigest(),
    })
    assert namespace["_authoring_invocation_draft"](
        component,
        input_name="authoring_invocation_result",
        expected_purpose="metadata_domain_draft",
        required=True,
        expected_output_schema=schema,
        expected_runtime_context_sha256=runtime_context_sha256,
    ) == {}
    component.authoring_invocation_result.data["runtime_context_sha256"] = "3" * 64
    with pytest.raises(namespace["ContractError"]):
        namespace["_authoring_invocation_draft"](
            component,
            input_name="authoring_invocation_result",
            expected_purpose="metadata_domain_draft",
            required=True,
            expected_output_schema=schema,
            expected_runtime_context_sha256=runtime_context_sha256,
        )
    component.authoring_invocation_result.data[
        "runtime_context_sha256"
    ] = runtime_context_sha256
    component.authoring_invocation_result.data["schema_binding_evidence"][
        "authoritative_schema_sha256"
    ] = "0" * 64
    with pytest.raises(namespace["ContractError"]) as mismatch:
        namespace["_authoring_invocation_draft"](
            component,
            input_name="authoring_invocation_result",
            expected_purpose="metadata_domain_draft",
            required=True,
            expected_output_schema=schema,
            expected_runtime_context_sha256=runtime_context_sha256,
        )
    assert mismatch.value.stage == "metadata_llm_schema_binding"


def test_split_invocation_accepts_closed_google_native_schema_binding_evidence() -> None:
    from lfx.schema.data import Data

    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"status": {"type": "string"}},
        "required": ["status"],
    }
    schema_sha256 = namespace["sha256_json"](schema)
    runtime_context_sha256 = "2" * 64
    response_text = '{"status":"complete"}'
    invocation = {
        "contract_version": "llm.invocation.v1",
        "purpose": "metadata_domain_draft",
        "status": "ok",
        "llm_calls": 1,
        "prompt_bundle_sha256": "1" * 64,
        "runtime_context_sha256": runtime_context_sha256,
        "provider_schema_binding": "google_native_json_schema",
        "schema_binding_evidence": {
            "contract_version": "llm.schema-binding.evidence.v1",
            "binding_status": "google_native_json_schema",
            "projection": "google_supported_json_schema_subset.v6",
            "authoritative_schema_sha256": schema_sha256,
            "provider_schema_sha256": "1" * 64,
        },
        "response_text": response_text,
        "response_sha256": hashlib.sha256(response_text.encode("utf-8")).hexdigest(),
    }
    component = component_cls()
    component.authoring_invocation_result = Data(data=invocation)

    assert namespace["_authoring_invocation_draft"](
        component,
        input_name="authoring_invocation_result",
        expected_purpose="metadata_domain_draft",
        required=True,
        expected_output_schema=schema,
        expected_runtime_context_sha256=runtime_context_sha256,
    ) == {"status": "complete"}
    summary = component._observed_authoring_schema_bindings[
        "metadata_domain_draft"
    ]
    assert summary["contract_version"] == "metadata.llm-schema-binding-summary.v1"
    assert summary["projection"] == "google_supported_json_schema_subset.v6"
    assert summary["authoritative_schema_sha256"] == schema_sha256
    assert summary["runtime_output_schema_sha256"] == schema_sha256
    assert summary["raw_prompt_persisted"] is False
    assert summary["raw_response_persisted"] is False


def test_split_invocation_rejects_malformed_or_mismatched_google_schema_evidence() -> None:
    from lfx.schema.data import Data

    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {},
    }
    schema_sha256 = namespace["sha256_json"](schema)
    runtime_context_sha256 = "2" * 64
    valid = {
        "contract_version": "llm.invocation.v1",
        "purpose": "metadata_domain_draft",
        "status": "ok",
        "llm_calls": 1,
        "prompt_bundle_sha256": "1" * 64,
        "runtime_context_sha256": runtime_context_sha256,
        "provider_schema_binding": "google_native_json_schema",
        "schema_binding_evidence": {
            "contract_version": "llm.schema-binding.evidence.v1",
            "binding_status": "google_native_json_schema",
            "projection": "google_supported_json_schema_subset.v6",
            "authoritative_schema_sha256": schema_sha256,
            "provider_schema_sha256": "1" * 64,
        },
        "response_text": "{}",
        "response_sha256": hashlib.sha256(b"{}").hexdigest(),
    }
    invalid_invocations = []

    malformed = deepcopy(valid)
    malformed["schema_binding_evidence"] = "not-an-object"
    invalid_invocations.append(malformed)

    extra_key = deepcopy(valid)
    extra_key["schema_binding_evidence"]["untrusted_extra"] = True
    invalid_invocations.append(extra_key)

    status_mismatch = deepcopy(valid)
    status_mismatch["provider_schema_binding"] = (
        "portable_prompt_and_compiler_validation"
    )
    invalid_invocations.append(status_mismatch)

    authoritative_mismatch = deepcopy(valid)
    authoritative_mismatch["schema_binding_evidence"][
        "authoritative_schema_sha256"
    ] = "0" * 64
    invalid_invocations.append(authoritative_mismatch)

    invalid_provider_hash = deepcopy(valid)
    invalid_provider_hash["schema_binding_evidence"]["provider_schema_sha256"] = (
        "not-a-sha256"
    )
    invalid_invocations.append(invalid_provider_hash)

    invalid_projection = deepcopy(valid)
    invalid_projection["schema_binding_evidence"]["projection"] = "none"
    invalid_invocations.append(invalid_projection)

    plausible_but_wrong_projection = deepcopy(valid)
    plausible_but_wrong_projection["schema_binding_evidence"]["projection"] = (
        "google_supported_json_schema_subset.v7"
    )
    invalid_invocations.append(plausible_but_wrong_projection)

    for invocation in invalid_invocations:
        component = component_cls()
        component.authoring_invocation_result = Data(data=invocation)
        with pytest.raises(namespace["ContractError"]) as rejected:
            namespace["_authoring_invocation_draft"](
                component,
                input_name="authoring_invocation_result",
                expected_purpose="metadata_domain_draft",
                required=True,
                expected_output_schema=schema,
                expected_runtime_context_sha256=runtime_context_sha256,
            )
        assert rejected.value.stage == "metadata_llm_schema_binding"


@pytest.mark.parametrize(
    ("kind", "valid_draft", "invalid_drafts"),
    (
        (
            "dataset",
            {
                "dataset_cards": [
                    {
                        "dataset_id": "orders",
                        "fields": [{"id": "ORDER_ID", "col": "ORDER_ID"}],
                    }
                ]
            },
            (
                {"dataset_cards": [{}]},
                {
                    "dataset_cards": [
                        {
                            "dataset_id": "orders",
                            "fields": [{"id": "ORDER_ID", "col": "ORDER_ID"}],
                        }
                    ],
                    "aliases": {},
                },
            ),
        ),
        (
            "main_filter",
            {
                "alias_additions": [
                    {
                        "target_type": "field",
                        "target_id": "PRODUCT_ID",
                        "expressions": ["판매 상품 코드"],
                    }
                ]
            },
            (
                {"alias_additions": [{}]},
                {
                    "alias_additions": [
                        {
                            "target_type": "field",
                            "target_id": "PRODUCT_ID",
                            "expressions": ["판매 상품 코드"],
                        }
                    ],
                    "aliases": {},
                },
            ),
        ),
    ),
)
def test_non_split_section_authoring_validates_bound_schema_before_expansion(
    kind: str,
    valid_draft: dict,
    invalid_drafts: tuple[dict, ...],
) -> None:
    """Malformed or cross-owner compact IR must never reach a section expander."""

    from lfx.schema.data import Data
    from lfx.schema.message import Message

    registry = _approved_reference_context("order_sales")
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "order_sales"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    source_text = {
        "dataset": "주문 데이터에 주문번호 항목이 있다는 내용을 평소 쓰는 말로 등록합니다.",
        "main_filter": "판매 상품 코드라는 말을 상품 코드 조회 조건으로 알아듣게 등록합니다.",
    }[kind]
    context = _bootstrap_prompt_context(
        kind=kind,
        source_text=source_text,
        domain_id="order_sales",
        environment="test",
        approved_reference_context=registry,
        bootstrap_fragment=False,
    )
    output_schema = context.data["variables"]["output_schema"]
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )

    def run(draft: dict, *, evidence_tamper: str = "") -> dict:
        invocation = _bootstrap_invocation(
            kind=kind,
            source_text=source_text,
            output_schema=output_schema,
            runtime_context=context.data,
            draft=draft,
        )
        if evidence_tamper == "missing":
            invocation.data.pop("schema_binding_evidence")
        elif evidence_tamper == "forged":
            invocation.data["schema_binding_evidence"][
                "authoritative_schema_sha256"
            ] = "0" * 64
        component = component_cls()
        component.input_message = Message(text=source_text)
        component.authoring_source_context = context
        component.authoring_invocation_result = invocation
        component.authoring_kind = kind
        component.source_grounding_mode = "freeform_llm"
        component.domain_id = "order_sales"
        component.environment = "test"
        component.revision_policy = "explicit"
        component.revision = 2
        component.mode = "prepare"
        component.dry_run = True
        component.inline_base_domain_bundle = Data(data=package)
        component.approved_reference_context = registry
        return component.run_authoring().data

    for invalid_draft in invalid_drafts:
        response = run(invalid_draft)
        assert response["status"] == "error", response
        assert response["error"]["code"] == "metadata_schema_error", response
        assert response["stage"] != "metadata_runtime", response
        assert "candidate_id" not in response

    for tamper in ("missing", "forged"):
        response = run(valid_draft, evidence_tamper=tamper)
        assert response["status"] == "error", response
        assert response["error"]["code"] == "metadata_dependency_error", response
        assert response["stage"] == "metadata_llm_schema_binding", response
        assert "candidate_id" not in response

    response = run(valid_draft)
    assert response["status"] == "ok", response
    proposal = response["validation"]["authoring_proposal"]
    assert response["validation"]["source_coverage"][
        "structured_proposal_sha256"
    ] == proposal["expanded_draft_sha256"]


def test_explicit_inventory_section_authoring_validates_and_expands_compact_ir() -> None:
    """The administrator lane uses the same compact IR before deterministic compilation."""

    from lfx.schema.data import Data
    from lfx.schema.message import Message

    registry = _approved_reference_context("order_sales")
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "order_sales"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    drafts = {
        "dataset": _compact_dataset_fragment(
            {"orders": package["runtime_catalog"]["datasets"]["orders"]}
        ),
        "main_filter": {
            "alias_additions": [
                {
                    "target_type": "field",
                    "target_id": "CATEGORY",
                    "expressions": ["대표 상품 분류"],
                }
            ]
        },
    }
    sources = {
        "dataset": (
            "orders 데이터셋은 주문 내역 조회용입니다.\n"
            "canonical 필드는 CUSTOMER_ID, ORDER_DATE, ORDER_ID, PRODUCT_ID, "
            "SALES_AMOUNT입니다."
        ),
        "main_filter": (
            "orders 데이터셋은 주문 내역 조회용입니다.\n"
            "canonical 필드는 ORDER_ID입니다.\n"
            "별칭 카드의 안정 식별자는 field:CATEGORY이고 대상 유형은 field, "
            "대상 키는 CATEGORY입니다.\n"
            "사용자가 '대표 상품 분류'라고 말하면 CATEGORY 필드로 해석하세요."
        ),
    }
    expander_by_kind = {
        "dataset": "_expand_compact_dataset_fragment",
        "main_filter": "_expand_compact_main_filter_fragment",
    }

    for kind in ("dataset", "main_filter"):
        source_text = sources[kind]
        context = _bootstrap_prompt_context(
            kind=kind,
            source_text=source_text,
            domain_id="order_sales",
            environment="test",
            approved_reference_context=registry,
            source_grounding_mode="explicit_inventory",
            bootstrap_fragment=False,
        )
        invocation = _bootstrap_invocation(
            kind=kind,
            source_text=source_text,
            output_schema=context.data["variables"]["output_schema"],
            runtime_context=context.data,
            draft=drafts[kind],
            direct_compact_ir=True,
        )
        component = component_cls()
        component.input_message = Message(text=source_text)
        component.authoring_source_context = context
        component.authoring_invocation_result = invocation
        component.authoring_kind = kind
        component.source_grounding_mode = "explicit_inventory"
        component.domain_id = "order_sales"
        component.environment = "test"
        component.revision_policy = "explicit"
        component.revision = 2
        component.mode = "prepare"
        component.dry_run = True
        component.inline_base_domain_bundle = Data(data=package)
        component.approved_reference_context = registry

        observed = []
        expander_name = expander_by_kind[kind]
        original_expander = namespace[expander_name]

        def record_expansion(fragment, *args, __original=original_expander, **kwargs):
            observed.append(deepcopy(fragment))
            return __original(fragment, *args, **kwargs)

        namespace[expander_name] = record_expansion
        try:
            response = component.run_authoring().data
        finally:
            namespace[expander_name] = original_expander

        assert response["status"] == "ok", json.dumps(
            response, ensure_ascii=False, indent=2
        )
        assert observed == [drafts[kind]]
        assert response["llm_usage"] == {
            "draft_llm_calls": 1,
            "annotation_llm_calls": 0,
            "repair_llm_calls": 0,
        }
        assert response["validation"]["source_coverage"]["passed"] is True
        assert not any(
            response["validation"]["source_coverage"]["counts"]["missing"].values()
        )


def test_filter_operator_alias_normalization_is_closed_and_deterministic() -> None:
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    draft = {
        "predicates": {
            "ACTIVE": {
                "allowed_operators": ["not_blank", "equals"],
                "predicate": {
                    "field": "STATUS",
                    "operator": "not-blank",
                },
            }
        },
        "datasets": {
            "items": {
                "fields": {
                    "STATUS": {
                        "allowed_filter_operators": ["startswith", "in"]
                    }
                }
            }
        },
    }

    normalized, evidence = namespace[
        "_normalize_filter_operator_aliases"
    ](draft)

    assert normalized["predicates"]["ACTIVE"]["allowed_operators"] == [
        "is_not_blank",
        "eq",
    ]
    assert normalized["predicates"]["ACTIVE"]["predicate"]["operator"] == (
        "is_not_blank"
    )
    assert normalized["datasets"]["items"]["fields"]["STATUS"][
        "allowed_filter_operators"
    ] == ["starts_with", "in"]
    assert evidence["replacement_count"] == 3
    assert len(evidence["replacements_sha256"]) == 64
    assert draft["predicates"]["ACTIVE"]["predicate"]["operator"] == "not-blank"


def test_domain_annotation_prompt_exposes_no_executable_schema() -> None:
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/authoring_prompt_context_builder.py")
    blueprint_path = ROOT / "metadata" / "domain_packs" / "order_sales" / "trusted_executable_blueprint.json"
    pin_path = ROOT / "metadata" / "domain_packs" / "order_sales" / "trusted_executable_blueprint.sha256"
    component = component_cls()
    component.input_message = Message(text=(ROOT / "validation" / "order_sales_metadata_input.txt").read_text(encoding="utf-8"))
    component.authoring_kind = "domain"
    component.mode = "prepare"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.trusted_blueprint_json = blueprint_path.read_text(encoding="utf-8")
    component.trusted_blueprint_sha256 = pin_path.read_text(encoding="utf-8").strip()
    component.approved_reference_context = _approved_reference_context("order_sales")

    context = component.build_context().data
    schema = context["variables"]["output_schema"]
    prompt = (ROOT / "prompts" / "metadata_authoring" / "domain_common_ko.md").read_text(encoding="utf-8")
    assert set(schema["properties"]) == {"display_name", "description"}
    assert schema["required"] == ["display_name", "description"]
    assert "annotation만" in prompt
    assert '"datasets"' not in json.dumps(context["variables"]["default_annotations"], ensure_ascii=False)


def test_freeform_domain_prepare_requires_one_external_invocation_without_blueprint() -> None:
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")

    class NeverModel:
        calls = 0

        def invoke(self, prompt: str) -> str:
            self.calls += 1
            return '{}'

    model = NeverModel()
    source_text = "주문 분석 도메인이다."
    registry = _approved_reference_context("order_sales")
    context = _bootstrap_prompt_context(
        kind="domain",
        source_text=source_text,
        domain_id="order_sales",
        environment="test",
        approved_reference_context=registry,
        bootstrap_fragment=False,
    )
    component = component_cls()
    component.input_message = Message(text=source_text)
    component.authoring_source_context = context
    component.language_model = model
    component.authoring_kind = "domain"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.mode = "prepare"
    component.dry_run = True
    component.trusted_blueprint_json = ""
    component.trusted_blueprint_sha256 = ""
    component.approved_reference_context = registry

    response = component.run_authoring().data

    assert response["status"] == "error"
    assert response["error"]["code"] == "metadata_llm_unavailable"
    assert response["error"]["details"]["expected_purpose"] == "metadata_domain_draft"
    assert model.calls == 0


def test_freeform_domain_prepare_compiles_closed_full_draft_without_blueprint() -> None:
    from lfx.schema.data import Data
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    namespace = component_cls.run_authoring.__globals__
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "order_sales"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    draft = namespace["runtime_catalog_v2_to_authoring_draft"](package["runtime_catalog"])
    draft["prompt_extensions"] = {"intent": "", "answer": ""}
    draft["specialized_functions"] = []
    draft["output_profile"] = {}
    # The worker/LLM does not own physical execution references.  Prove that
    # omitted and even conflicting values are discarded in favor of the sealed
    # operator registry before compilation.
    sample_dataset_id = sorted(draft["datasets"])[0]
    sample_dataset = draft["datasets"][sample_dataset_id]
    approved_source_type = package["runtime_catalog"]["datasets"][sample_dataset_id]["source_type"]
    sample_dataset["source_type"] = "file" if approved_source_type != "file" else "dummy"
    sample_dataset.pop("source_adapter", None)
    sample_dataset.pop("config_ref", None)
    sample_dataset.pop("query_ref", None)
    source_text = (ROOT / "validation" / "order_sales_metadata_input.txt").read_text(encoding="utf-8").strip()
    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    proposal = {
        "contract_version": "metadata.authoring.proposal.v1",
        "status": "complete",
        "source_sha256": source_sha256,
        "draft": draft,
    }
    registry = _approved_reference_context("order_sales")
    context = _bootstrap_prompt_context(
        kind="domain",
        source_text=source_text,
        domain_id="order_sales",
        environment="test",
        approved_reference_context=registry,
        bootstrap_fragment=False,
    )
    component = component_cls()
    component.input_message = Message(text=source_text)
    component.authoring_source_context = context
    component.authoring_invocation_result = _bootstrap_invocation(
        kind="domain",
        source_text=source_text,
        output_schema=context.data["variables"]["output_schema"],
        runtime_context=context.data,
        draft=draft,
    )
    component.authoring_kind = "domain"
    component.source_grounding_mode = "freeform_llm"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.revision_policy = "explicit"
    component.revision = 1
    component.mode = "prepare"
    component.dry_run = True
    component.trusted_blueprint_json = ""
    component.trusted_blueprint_sha256 = ""

    component.approved_reference_context = registry
    response = component.run_authoring().data

    assert response["status"] == "ok", json.dumps(response, ensure_ascii=False, indent=2)
    assert response["llm_usage"] == {
        "draft_llm_calls": 1,
        "annotation_llm_calls": 0,
        "repair_llm_calls": 0,
    }
    assert response["validation"]["source_coverage"]["mode"] == "freeform_llm"
    assert response["validation"]["source_coverage"]["human_approval_required"] is True
    assert response["validation"]["dependency_closure"] == "passed"
    assert response["validation"]["source_bindings"]["status"] == "approved_registry_exact"
    assert response["validation"]["source_bindings"]["registry_resolution"] == "passed"
    assert response["validation"]["source_bindings"]["binding_authority"] == "approved_registry"
    summaries = response["validation"]["llm_schema_bindings"]
    assert summaries["contract_version"] == "metadata.llm-schema-bindings.v1"
    assert [item["purpose"] for item in summaries["bindings"]] == [
        "metadata_domain_draft"
    ]
    assert f"datasets.{sample_dataset_id}.source_type" in response["validation"]["source_bindings"]["discarded_untrusted_fields"]
    assert response["validation"]["authoring_proposal"]["source_sha256"] == source_sha256
    assert response["validation"]["authoring_proposal"]["draft_sha256"] == namespace["sha256_json"](draft)


def test_split_bootstrap_merges_three_sealed_fragments_and_compiles_once() -> None:
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    namespace = component_cls.run_authoring.__globals__
    package = json.loads(
        (
            ROOT
            / "metadata"
            / "domain_packs"
            / "order_sales"
            / "compiled"
            / "domain_package.json"
        ).read_text(encoding="utf-8")
    )
    draft = namespace["runtime_catalog_v2_to_authoring_draft"](
        package["runtime_catalog"]
    )
    registry = _approved_reference_context("order_sales")
    annotation = {
        "display_name": "주문·매출 분석",
        "description": "주문, 환불, 목표를 함께 분석하는 업무 영역입니다.",
    }
    main_filter_ir = {
        "alias_additions": [
            {
                "target_type": "field",
                "target_id": "CATEGORY",
                "expressions": ["대표 상품군"],
            }
        ]
    }
    fragments = {
        "domain": annotation,
        "dataset": _compact_dataset_fragment(draft["datasets"]),
        "main_filter": main_filter_ir,
    }
    assert "contract_version" not in fragments["domain"]
    assert set(fragments["domain"]) == {"display_name", "description"}
    dataset_descriptors = registry.data["dataset_descriptors"]
    expanded_domain, expected_template_evidence = namespace[
        "_expand_bootstrap_domain_annotation"
    ](
        annotation,
        semantic_templates=registry.data["semantic_templates"],
        semantic_vocabulary=registry.data["semantic_vocabulary"],
    )
    expanded_fragments = {
        **deepcopy(fragments),
        "domain": expanded_domain,
    }
    dataset_reconciliation = {}
    main_filter_reconciliation = {}
    merged = namespace["_merge_bootstrap_fragments"](
        expanded_fragments,
        dataset_descriptors=dataset_descriptors,
        semantic_vocabulary=registry.data["semantic_vocabulary"],
        reconciliation_out=dataset_reconciliation,
        main_filter_reconciliation_out=main_filter_reconciliation,
        domain_already_expanded=True,
    )
    assert merged["contract_version"] == "metadata.authoring.draft.v1"
    assert merged["metrics"] == registry.data["semantic_templates"]["metrics"]
    assert main_filter_reconciliation["contract_version"] == (
        "metadata.main-filter-ir-expansion.v1"
    )
    first_dataset_id = sorted(merged["datasets"])[0]
    assert "source_type" not in merged["datasets"][first_dataset_id]
    inferred_fragment = deepcopy(expanded_fragments)
    inferred_row = next(
        row
        for card in inferred_fragment["dataset"]["dataset_cards"]
        for row in card["fields"]
    )
    inferred_dataset_id = next(
        card["dataset_id"]
        for card in inferred_fragment["dataset"]["dataset_cards"]
        if inferred_row in card["fields"]
    )
    inferred_field_id = inferred_row["id"]
    assert namespace["_merge_bootstrap_fragments"](
        inferred_fragment,
        dataset_descriptors=dataset_descriptors,
        semantic_vocabulary=registry.data["semantic_vocabulary"],
        domain_already_expanded=True,
    )["datasets"][
        inferred_dataset_id
    ]["fields"][inferred_field_id]["semantic_type"] == dataset_descriptors[
        inferred_dataset_id
    ]["fields"][inferred_field_id]["semantic_type"]
    forbidden_fragment = deepcopy(expanded_fragments)
    forbidden_fragment["dataset"]["dataset_cards"][0]["source_type"] = "file"
    with pytest.raises(namespace["ContractError"]):
        namespace["_merge_bootstrap_fragments"](
            forbidden_fragment,
            dataset_descriptors=dataset_descriptors,
            semantic_vocabulary=registry.data["semantic_vocabulary"],
            domain_already_expanded=True,
        )
    source_texts = {
        "domain": "주문, 상품, 환불과 목표를 함께 분석하는 업무입니다.",
        "dataset": "주문·상품·환불·목표 데이터와 각 업무 항목을 사용합니다.",
        "main_filter": "상품 분류를 주요 조회 조건으로 사용합니다.",
    }
    incomplete = deepcopy(merged)
    incomplete["datasets"].pop(first_dataset_id)
    with pytest.raises(namespace["ContractError"]) as exact_set_error:
        namespace["_validate_authoring_source_bindings"](
            incomplete,
            approved_reference_context=registry,
            domain_id="order_sales",
            require_registry_exact_set=True,
        )
    assert exact_set_error.value.code == "metadata_dependency_error"
    assert exact_set_error.value.stage == "metadata_source_bindings"
    contexts = {
        kind: _bootstrap_prompt_context(
            kind=kind,
            source_text=source_text,
            domain_id="order_sales",
            environment="test",
            approved_reference_context=registry,
        )
        for kind, source_text in source_texts.items()
    }
    bundled_source = _bootstrap_source_bundle(source_texts)
    component = component_cls()
    component.input_message = Message(text=bundled_source)
    component.authoring_source_context = contexts["domain"]
    component.bootstrap_dataset_source_context = contexts["dataset"]
    component.bootstrap_main_filter_source_context = contexts["main_filter"]
    component.authoring_invocation_result = _bootstrap_invocation(
        kind="domain",
        source_text=source_texts["domain"],
        output_schema=contexts["domain"].data["variables"]["output_schema"],
        runtime_context=contexts["domain"].data,
        draft=fragments["domain"],
    )
    component.bootstrap_dataset_invocation_result = _bootstrap_invocation(
        kind="dataset",
        source_text=source_texts["dataset"],
        output_schema=contexts["dataset"].data["variables"]["output_schema"],
        runtime_context=contexts["dataset"].data,
        draft=fragments["dataset"],
    )
    component.bootstrap_main_filter_invocation_result = _bootstrap_invocation(
        kind="main_filter",
        source_text=source_texts["main_filter"],
        output_schema=contexts["main_filter"].data["variables"]["output_schema"],
        runtime_context=contexts["main_filter"].data,
        draft=fragments["main_filter"],
    )
    component.split_bootstrap = True
    component.authoring_kind = "domain"
    component.source_grounding_mode = "freeform_llm"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.revision_policy = "explicit"
    component.revision = 1
    component.mode = "prepare"
    component.dry_run = True
    component.trusted_blueprint_json = ""
    component.trusted_blueprint_sha256 = ""
    component.approved_reference_context = registry

    compiled_drafts = []
    original_compile = namespace["compile_domain_package"]

    def compile_after_normalization(*args, **kwargs):
        compiled_drafts.append(deepcopy(args[0]))
        return original_compile(*args, **kwargs)

    namespace["compile_domain_package"] = compile_after_normalization
    try:
        response = component.run_authoring().data
    finally:
        namespace["compile_domain_package"] = original_compile

    assert response["status"] == "ok", json.dumps(
        response, ensure_ascii=False, indent=2
    )
    assert response["llm_usage"] == {
        "draft_llm_calls": 3,
        "annotation_llm_calls": 0,
        "repair_llm_calls": 0,
    }
    proposals = response["validation"]["authoring_proposals"]
    assert set(proposals) == {"domain", "dataset", "main_filter"}
    for kind in proposals:
        assert proposals[kind]["source_sha256"] == hashlib.sha256(
            source_texts[kind].encode("utf-8")
        ).hexdigest()
    assert proposals["dataset"]["dataset_ir_sha256"] == namespace["sha256_json"](
        fragments["dataset"]
    )
    assert proposals["dataset"]["dataset_ir_expander_version"] == (
        "metadata.dataset-ir-expander.v1"
    )
    assert proposals["domain"]["draft_sha256"] == namespace["sha256_json"](
        annotation
    )
    assert proposals["domain"]["template_expansion"] == (
        expected_template_evidence
    )
    assert proposals["main_filter"]["draft_sha256"] == namespace["sha256_json"](
        main_filter_ir
    )
    assert proposals["main_filter"]["main_filter_ir_expansion"] == (
        main_filter_reconciliation
    )
    aggregate = response["validation"]["authoring_proposal"]
    assert aggregate["source_sha256"] == hashlib.sha256(
        bundled_source.encode("utf-8")
    ).hexdigest()
    expected_merged = namespace["_merge_bootstrap_fragments"](
        expanded_fragments,
        dataset_descriptors=dataset_descriptors,
        semantic_vocabulary=registry.data["semantic_vocabulary"],
        domain_already_expanded=True,
    )
    expected_merged, _ = namespace["_complete_unambiguous_metric_bindings"](
        expected_merged,
        registry.data["semantic_vocabulary"],
    )
    expected_merged, _ = namespace["_normalize_bootstrap_alias_shorthand"](
        expected_merged,
        registry.data["semantic_vocabulary"],
    )
    assert aggregate["draft_sha256"] == namespace["sha256_json"](expected_merged)
    assert aggregate["expanded_draft_sha256"] == aggregate["draft_sha256"]
    assert aggregate["dataset_ir_sha256"] == proposals["dataset"][
        "dataset_ir_sha256"
    ]
    assert aggregate["dataset_ir_expander_version"] == (
        "metadata.dataset-ir-expander.v1"
    )
    assert aggregate["domain_template_expander_version"] == (
        "metadata.domain-template-expansion.v1"
    )
    assert aggregate["semantic_templates_sha256"] == namespace["sha256_json"](
        registry.data["semantic_templates"]
    )
    assert response["validation"]["domain_template_expansion"] == (
        expected_template_evidence
    )
    assert len(aggregate["sealed_authoring_sha256"]) == 64
    assert response["validation"]["source_coverage"][
        "structured_proposal_sha256"
    ] == aggregate["draft_sha256"]
    assert response["validation"]["source_bindings"]["status"] == (
        "approved_registry_exact"
    )
    assert response["validation"]["source_bindings"][
        "discarded_untrusted_fields"
    ] == []
    assert response["validation"]["metric_binding_completion"][
        "resolution_mode"
    ] == "approved_semantic_vocabulary_exact"
    assert response["validation"]["metric_binding_completion"][
        "completed_count"
    ] == 0
    assert response["validation"]["semantic_alias_normalization"][
        "resolution_mode"
    ] == "approved_semantic_vocabulary_exact"
    assert response["validation"]["semantic_alias_normalization"][
        "normalized_count"
    ] == 0
    assert len(compiled_drafts) == 1
    assert compiled_drafts[0]["metrics"]["SALES_AMOUNT"]["source_binding"] == {
        "dataset_family": "sales_actual",
        "field": "SALES_AMOUNT",
    }
    assert "CATEGORY" not in compiled_drafts[0]["aliases"]
    assert any(
        value["text"] == "대표 상품군"
        for value in compiled_drafts[0]["aliases"]["field:CATEGORY"]["values"]
    )


def test_split_bootstrap_clarification_counts_all_calls_and_never_opens_mongo() -> None:
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    source_texts = {
        "domain": "새 업무 분석을 만들고 싶지만 지표와 관계는 아직 모릅니다.",
        "dataset": "데이터셋과 컬럼은 아직 정하지 못했습니다.",
        "main_filter": "주요 필터와 별칭도 아직 정하지 못했습니다.",
    }
    registry = _approved_reference_context("order_sales")
    contexts = {
        kind: _bootstrap_prompt_context(
            kind=kind,
            source_text=source_text,
            domain_id="order_sales",
            environment="test",
            approved_reference_context=registry,
        )
        for kind, source_text in source_texts.items()
    }
    bundled_source = _bootstrap_source_bundle(source_texts)
    component = component_cls()
    component.input_message = Message(text=bundled_source)
    component.authoring_source_context = contexts["domain"]
    component.bootstrap_dataset_source_context = contexts["dataset"]
    component.bootstrap_main_filter_source_context = contexts["main_filter"]
    component.authoring_invocation_result = _bootstrap_invocation(
        kind="domain",
        source_text=source_texts["domain"],
        output_schema=contexts["domain"].data["variables"]["output_schema"],
        runtime_context=contexts["domain"].data,
        question="canonical field_id와 physical column을 JSON으로 알려 주세요.",
    )
    component.bootstrap_dataset_invocation_result = _bootstrap_invocation(
        kind="dataset",
        source_text=source_texts["dataset"],
        output_schema=contexts["dataset"].data["variables"]["output_schema"],
        runtime_context=contexts["dataset"].data,
    )
    component.bootstrap_main_filter_invocation_result = _bootstrap_invocation(
        kind="main_filter",
        source_text=source_texts["main_filter"],
        output_schema=contexts["main_filter"].data["variables"]["output_schema"],
        runtime_context=contexts["main_filter"].data,
    )
    component.split_bootstrap = True
    component.authoring_kind = "domain"
    component.source_grounding_mode = "freeform_llm"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.mode = "prepare"
    component.dry_run = False
    component.trusted_blueprint_json = ""
    component.trusted_blueprint_sha256 = ""
    component.approved_reference_context = registry
    component._mongo = lambda: (_ for _ in ()).throw(
        AssertionError("clarification must not access MongoDB")
    )

    response = component.run_authoring().data

    assert response["status"] == "needs_clarification"
    assert response["llm_usage"] == {
        "draft_llm_calls": 3,
        "annotation_llm_calls": 0,
        "repair_llm_calls": 0,
    }
    assert response["clarification"]["source_sha256"] == hashlib.sha256(
        bundled_source.encode("utf-8")
    ).hexdigest()
    assert response["clarification"]["questions"]
    clarification_text = json.dumps(
        response["clarification"]["questions"], ensure_ascii=False
    ).casefold()
    for technical_term in (
        "canonical", "field_id", "dataset_id", "physical", "json", "dsl",
        "schema", "registry", "정규 id", "물리 컬럼", "스키마", "레지스트리",
    ):
        assert technical_term not in clarification_text
    for forbidden in (
        "candidate_id",
        "candidate_sha256",
        "package_sha256",
        "persisted",
        "validation",
    ):
        assert forbidden not in response


def test_worker_clarification_sanitizer_replaces_technical_text_and_preserves_business_text() -> None:
    component_cls = _component_class(
        "metadata_authoring/00_metadata_authoring_engine.py"
    )
    namespace = component_cls.run_authoring.__globals__
    safe_business_question = "어느 기간의 매출 수치를 확인하고 싶은가요?"

    questions, missing_fields = namespace["_worker_safe_clarification"](
        [
            "canonical field_id와 physical column을 JSON schema로 알려 주세요.",
            safe_business_question,
        ],
        [
            "metrics.WIP_QTY.source_binding",
            "datasets.orders.fields.ORDER_ID",
            "relations.order_product.join_keys",
        ],
    )

    assert questions == [
        "어떤 업무 데이터나 수치를 뜻하는지 자연어로 설명해 주세요.",
        safe_business_question,
    ]
    assert missing_fields == [
        "업무 수치 설명",
        "업무 데이터 설명",
        "업무 데이터 관계 설명",
    ]
    serialized = json.dumps(
        {"questions": questions, "missing_fields": missing_fields},
        ensure_ascii=False,
    ).casefold()
    for technical_token in (
        "canonical",
        "field_id",
        "physical",
        "json",
        "schema",
        "source_binding",
        "order_id",
        "join_keys",
    ):
        assert technical_token not in serialized


def test_freeform_domain_clarification_never_reaches_candidate_or_mongo() -> None:
    from lfx.schema.data import Data
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    source_text = "주문 데이터를 분석하고 싶은데 실제 테이블과 컬럼은 아직 확인하지 못했습니다."
    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    proposal = {
        "contract_version": "metadata.authoring.proposal.v1",
        "status": "needs_clarification",
        "source_sha256": source_sha256,
        "clarification": {
            "questions": ["주문 데이터셋의 등록 ID와 물리 컬럼 목록은 무엇인가요?"],
            "missing_fields": ["datasets"],
        },
    }
    registry = _approved_reference_context("order_sales")
    context = _bootstrap_prompt_context(
        kind="domain",
        source_text=source_text,
        domain_id="order_sales",
        environment="test",
        approved_reference_context=registry,
        bootstrap_fragment=False,
    )
    component = component_cls()
    component.input_message = Message(text=source_text)
    component.authoring_source_context = context
    component.authoring_invocation_result = _bootstrap_invocation(
        kind="domain",
        source_text=source_text,
        output_schema=context.data["variables"]["output_schema"],
        runtime_context=context.data,
        question="주문 데이터셋의 등록 ID와 물리 컬럼 목록은 무엇인가요?",
    )
    component.authoring_kind = "domain"
    component.source_grounding_mode = "freeform_llm"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.mode = "prepare"
    component.dry_run = False
    component.approved_reference_context = registry
    component._mongo = lambda: (_ for _ in ()).throw(AssertionError("clarification must not access MongoDB"))

    response = component.run_authoring().data

    assert response["status"] == "needs_clarification"
    assert response["stage"] == "metadata_clarification"
    assert response["llm_usage"] == {
        "draft_llm_calls": 1,
        "annotation_llm_calls": 0,
        "repair_llm_calls": 0,
    }
    assert response["clarification"]["source_sha256"] == source_sha256
    assert len(response["clarification"]["questions"]) == 1
    clarification_text = json.dumps(
        response["clarification"]["questions"], ensure_ascii=False
    ).casefold()
    for technical_term in (
        "canonical", "field_id", "dataset_id", "physical", "json", "dsl",
        "schema", "registry", "등록 id", "물리 컬럼", "스키마", "레지스트리",
    ):
        assert technical_term not in clarification_text
    for forbidden in ("candidate_id", "candidate_sha256", "persisted", "validation"):
        assert forbidden not in response


def test_freeform_domain_invalid_complete_fails_compile_before_mongo() -> None:
    from lfx.schema.data import Data
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    namespace = component_cls.run_authoring.__globals__
    package = json.loads(
        (ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "domain_package.json").read_text(
            encoding="utf-8"
        )
    )
    draft = namespace["runtime_catalog_v2_to_authoring_draft"](package["runtime_catalog"])
    draft["prompt_extensions"] = {"intent": "", "answer": ""}
    draft["specialized_functions"] = []
    draft["output_profile"] = {}
    first_relation = sorted(draft["relations"])[0]
    draft["relations"][first_relation]["left_dataset"] = "unregistered_dataset"
    source_text = "주문과 상품 데이터를 자유롭게 설명한 작업자 입력입니다."
    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    proposal = {
        "contract_version": "metadata.authoring.proposal.v1",
        "status": "complete",
        "source_sha256": source_sha256,
        "draft": draft,
    }
    registry = _approved_reference_context("order_sales")
    context = _bootstrap_prompt_context(
        kind="domain",
        source_text=source_text,
        domain_id="order_sales",
        environment="test",
        approved_reference_context=registry,
        bootstrap_fragment=False,
    )
    component = component_cls()
    component.input_message = Message(text=source_text)
    component.authoring_source_context = context
    component.authoring_invocation_result = _bootstrap_invocation(
        kind="domain",
        source_text=source_text,
        output_schema=context.data["variables"]["output_schema"],
        runtime_context=context.data,
        draft=draft,
    )
    component.authoring_kind = "domain"
    component.source_grounding_mode = "freeform_llm"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.mode = "prepare"
    component.dry_run = False
    component.approved_reference_context = registry
    component._mongo = lambda: (_ for _ in ()).throw(AssertionError("invalid draft must not access MongoDB"))

    response = component.run_authoring().data

    assert response["status"] == "error"
    assert response["stage"] != "metadata_runtime", response
    assert "candidate_id" not in response


def test_freeform_domain_llm_cannot_inject_domain_policy_sections() -> None:
    from lfx.schema.data import Data
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    namespace = component_cls.run_authoring.__globals__
    package = json.loads(
        (ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "domain_package.json").read_text(
            encoding="utf-8"
        )
    )
    draft = namespace["runtime_catalog_v2_to_authoring_draft"](package["runtime_catalog"])
    source_text = "주문 데이터셋과 필드를 등록한다."
    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    proposal = {
        "contract_version": "metadata.authoring.proposal.v1",
        "status": "complete",
        "source_sha256": source_sha256,
        "draft": draft,
    }
    registry = _approved_reference_context("order_sales")
    context = _bootstrap_prompt_context(
        kind="domain",
        source_text=source_text,
        domain_id="order_sales",
        environment="test",
        approved_reference_context=registry,
        bootstrap_fragment=False,
    )
    component = component_cls()
    component.input_message = Message(text=source_text)
    component.authoring_source_context = context
    component.authoring_invocation_result = _bootstrap_invocation(
        kind="domain",
        source_text=source_text,
        output_schema=context.data["variables"]["output_schema"],
        runtime_context=context.data,
        draft=draft,
    )
    component.authoring_kind = "domain"
    component.source_grounding_mode = "freeform_llm"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.mode = "prepare"
    component.dry_run = True
    component.approved_reference_context = registry

    response = component.run_authoring().data

    assert response["status"] == "error"
    assert response["error"]["code"] == "metadata_policy_error"
    assert response["stage"] == "metadata_domain_policy_boundary"
    assert response["llm_usage"]["draft_llm_calls"] == 1
    assert "candidate_id" not in response


def test_full_domain_prepare_uses_only_annotation_llm_and_preserves_blueprint() -> None:
    from lfx.schema.data import Data
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")

    blueprint_path = ROOT / "metadata" / "domain_packs" / "order_sales" / "trusted_executable_blueprint.json"
    pin_path = ROOT / "metadata" / "domain_packs" / "order_sales" / "trusted_executable_blueprint.sha256"
    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    blueprint_text = blueprint_path.read_text(encoding="utf-8")
    blueprint_sha256 = pin_path.read_text(encoding="utf-8").strip()
    source_text = (ROOT / "validation" / "order_sales_metadata_input.txt").read_text(
        encoding="utf-8"
    )
    annotations = {
        "display_name": "주문 매출 분석",
        "description": "주문, 상품, 환불, 목표를 분석한다.",
    }
    registry = _approved_reference_context("order_sales")
    context = _bootstrap_prompt_context(
        kind="domain",
        source_text=source_text,
        domain_id="order_sales",
        environment="test",
        approved_reference_context=registry,
        bootstrap_fragment=False,
        trusted_blueprint_json=blueprint_text,
        trusted_blueprint_sha256=blueprint_sha256,
    )
    component = component_cls()
    component.input_message = Message(text=source_text)
    component.authoring_source_context = context
    component.authoring_invocation_result = _bootstrap_invocation(
        kind="domain",
        source_text=source_text,
        output_schema=context.data["variables"]["output_schema"],
        runtime_context=context.data,
        draft=annotations,
        direct_compact_ir=True,
        purpose_override="metadata_domain_annotation",
    )
    component.authoring_kind = "domain"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.revision_policy = "explicit"
    component.revision = 1
    component.mode = "prepare"
    component.dry_run = True
    component.trusted_blueprint_json = blueprint_text
    component.trusted_blueprint_sha256 = blueprint_sha256
    component.approved_reference_context = registry

    response = component.run_authoring().data

    assert response["status"] == "ok", json.dumps(response, ensure_ascii=False, indent=2)
    assert response["llm_usage"] == {
        "draft_llm_calls": 0,
        "annotation_llm_calls": 1,
        "repair_llm_calls": 0,
    }
    assert response["validation"]["trusted_blueprint"]["blueprint_sha256"] == blueprint["blueprint_sha256"]
    assert response["validation"]["trusted_blueprint"]["executable_sha256"] == blueprint["executable_sha256"]
    assert response["validation"]["trusted_blueprint"]["executable_immutable"] == "passed"
    assert "language_model" not in {item.name for item in component_cls.inputs}

    presenter_cls = _component_class("metadata_authoring/01_authoring_message_presentation.py")
    presenter = presenter_cls()
    presenter.response = Data(data=response)
    message = presenter.build_message()
    assert message.session_metadata == {
        "contract_version": "metadata.authoring.message-link.v1",
        "response_sha256": response["response_sha256"],
    }
    assert message.data["response"]["response_sha256"] == response["response_sha256"]


def test_authoring_generated_source_has_no_pending_or_active_writer() -> None:
    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    values = {item.name: getattr(item, "value", None) for item in component_cls.inputs}
    source = _source("metadata_authoring/00_metadata_authoring_engine.py")
    assert set(values).isdisjoint({"pending_collection", "active_collection", "bundle_collection"})
    assert "def _pending_payload(" not in source
    assert "def _execute_v2(" not in source
    assert "replace_metadata_items(" in source
    assert "release_manifest_sha256" not in source
    assert "load_domain_package_from_three_collections(" in source


def test_domain_policy_prepare_is_explicit_operator_input_only() -> None:
    from lfx.schema.data import Data
    from lfx.schema.message import Message

    component_cls = _component_class("metadata_authoring/00_metadata_authoring_engine.py")
    package = json.loads(
        (ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "domain_package.json").read_text(
            encoding="utf-8"
        )
    )
    component = component_cls()
    component.input_message = Message(text="운영자가 intent 설명 정책을 갱신한다.")
    component.authoring_kind = "domain_policy"
    component.domain_id = "order_sales"
    component.environment = "test"
    component.inline_base_domain_bundle = Data(data=package)
    component.approved_reference_context = _approved_reference_context("order_sales")
    component.intent_prompt_extension = "등록된 후보 ID 안에서만 선택한다."
    component.answer_prompt_extension = ""
    component.specialized_functions_json = ""
    component.output_profile_json = ""
    component.mode = "prepare"
    component.dry_run = True

    response = component.run_authoring().data

    assert response["status"] == "ok", json.dumps(response, ensure_ascii=False, indent=2)
    assert response["llm_usage"] == {
        "draft_llm_calls": 0,
        "annotation_llm_calls": 0,
        "repair_llm_calls": 0,
    }


def test_api_terminal_returns_ordinary_json_without_hash_validation() -> None:
    from lfx.schema.data import Data

    component_cls = _component_class("shared/00_api_response_terminal.py")
    component = component_cls()
    payload = {"contract_version": "response.v1", "message": "ordinary json"}
    component.response = Data(data=payload)
    assert component.build_response().data == payload


def test_generator_fails_clearly_when_compiled_catalog_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    import tools.build_standalone_components as generator

    monkeypatch.setattr(generator, "CATALOG_PATH", ROOT / "tests" / "__missing_catalog__.json")
    with pytest.raises(GenerationError, match="compiled runtime catalog is missing"):
        generator.build_components(check=True)
