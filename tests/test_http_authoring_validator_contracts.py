from __future__ import annotations

import json
import inspect
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest

from reference_runtime.canonical import sha256_json
from reference_runtime.contracts import validate_contract
from reference_runtime.domain_packages import (
    compile_domain_package,
    make_active_pointer_document,
    make_bundle_document,
    validate_domain_package,
)
from reference_runtime.authoring_source_manifest import extract_authoring_source_manifest
from tools.validate_langflow_http_authoring_e2e import (
    AUTHORING_GEMINI_MODEL,
    AUTHORING_INPUT_PATHS,
    AuthoringValidationError,
    BLUEPRINT_PATH,
    DATASET_PATCH_TEXT,
    DEFAULT_SOURCE_SET_ID,
    FLOW_PATHS,
    FREEFORM_CLARIFICATION_PROBE,
    FREEFORM_CLARIFICATION_DATASET_PROBE,
    FREEFORM_CLARIFICATION_MAIN_FILTER_PROBE,
    FREEFORM_REORDERED_INPUT_DIR,
    FREEFORM_REORDERED_SOURCE_SET_ID,
    MANUFACTURING_COMPILED_CATALOG_PATH,
    ORDER_SALES_REQUIRED_MANIFEST,
    _build_approval_event,
    _compose_domain_bootstrap_source,
    _domain_flow_context_tweaks,
    _fresh_environment,
    _flow_defaults,
    _google_authoring_schema_binding_validation,
    _load_v6_authoring_sources,
    _manufacturing_semantic_completeness,
    _expected_prepare_llm_calls,
    _pending_evidence,
    _run_freeform_clarification_probe,
    _section_ownership_checks,
    _safe_failure,
    _semantic_completeness,
    _source_style_evidence,
    _tampered_approval_events,
    _validate_loader_runtime_bundle,
    extract_authoring_evidence,
    run,
)
from tools.validate_live_blueprint_authoring import _load_trusted_blueprint


def _runtime_loader_context() -> dict:
    source_text = (BLUEPRINT_PATH.parents[3] / "validation" / "order_sales_metadata_input.txt").read_text(
        encoding="utf-8"
    )
    from reference_runtime.authoring_source_manifest import extract_authoring_source_manifest

    source_manifest = extract_authoring_source_manifest(source_text)
    blueprint, _, _ = _load_trusted_blueprint(
        blueprint_path=BLUEPRINT_PATH,
        pin_path=BLUEPRINT_PATH.with_suffix(".sha256"),
        source_manifest=source_manifest,
        domain_id="order_sales",
        environment="loader_test",
    )
    draft = {**deepcopy(blueprint["executable"]), **deepcopy(blueprint["default_annotations"])}
    package = compile_domain_package(draft, "order_sales", "loader_test", revision=3)
    catalog = deepcopy(package["runtime_catalog"])
    return {
        "contract_version": "pipeline.context.v1",
        "ok": True,
        "stage": "domain_bundle",
        "domain_bundle": {
            "contract_version": "domain.bundle.runtime.v1",
            "domain_id": "order_sales",
            "environment": "loader_test",
            "revision": "3",
            "source_mode": "v6_active",
            "catalog_sha256": catalog["catalog_sha256"],
            "runtime_catalog": catalog,
            "package_sha256": package["package_sha256"],
            "bundle_sha256": package["bundle_sha256"],
        },
    }


def test_loader_runtime_projection_validates_exact_consumer_contract() -> None:
    context = _runtime_loader_context()
    runtime_bundle = _validate_loader_runtime_bundle(
        context,
        expected_domain_id="order_sales",
        expected_environment="loader_test",
    )
    assert runtime_bundle["contract_version"] == "domain.bundle.runtime.v1"
    assert runtime_bundle["source_mode"] == "v6_active"
    assert runtime_bundle["revision"] == "3"
    assert runtime_bundle["catalog_sha256"] == runtime_bundle["runtime_catalog"]["catalog_sha256"]


def test_loader_runtime_projection_rejects_extra_key_and_identity_mismatch() -> None:
    extra = _runtime_loader_context()
    extra["domain_bundle"]["persisted_package_only"] = True
    with pytest.raises(AuthoringValidationError) as extra_error:
        _validate_loader_runtime_bundle(
            extra,
            expected_domain_id="order_sales",
            expected_environment="loader_test",
        )
    assert extra_error.value.code == "loader_runtime_projection_invalid"
    assert "bundle_keys_exact" in extra_error.value.details["failed_checks"]

    mismatch = _runtime_loader_context()
    mismatch["domain_bundle"]["environment"] = "other_environment"
    with pytest.raises(AuthoringValidationError) as identity_error:
        _validate_loader_runtime_bundle(
            mismatch,
            expected_domain_id="order_sales",
            expected_environment="loader_test",
        )
    assert identity_error.value.code == "loader_runtime_projection_invalid"
    assert "identity_exact" in identity_error.value.details["failed_checks"]


def test_pending_write_schema_accepts_valid_domain_keys_with_spaces() -> None:
    root = BLUEPRINT_PATH.parents[3]
    package = validate_domain_package(
        json.loads(
            (
                root
                / "metadata"
                / "domain_packs"
                / "manufacturing"
                / "compiled"
                / "domain_package.json"
            ).read_text(encoding="utf-8")
        )
    )
    assert "process:PKG OUT" in package["runtime_catalog"]["aliases"]
    now = datetime(2026, 8, 1, 1, 2, 3, 123000, tzinfo=timezone.utc)
    expires = now + timedelta(minutes=30)
    hash_material = {
        "contract_version": "pending.domain-package.hash-material.v1",
        "domain_package": package,
        "bundle_document": make_bundle_document(package),
        "active_pointer": make_active_pointer_document(package),
        "expected_active": {"revision": 0, "bundle_sha256": "", "package_sha256": ""},
        "validation": {"schema": "passed"},
        "prepared_at": now.isoformat(),
        "expires_at": expires.isoformat(),
    }
    candidate_sha256 = sha256_json(hash_material)
    payload = {
        "contract_version": "pending.metadata.write.v1",
        "authoring_kind": "domain_policy",
        "domain_id": package["domain_id"],
        "environment": package["environment"],
        "candidate_id": f"candidate:{candidate_sha256}",
        "candidate_sha256": candidate_sha256,
        "status": "prepared",
        "target_revision": int(package["revision"]),
        "base_revision": None,
        "base_bundle_sha256": None,
        "base_package_sha256": None,
        "prepared_at": now.isoformat(),
        "expires_at": expires.isoformat(),
        "hash_material": hash_material,
    }
    assert validate_contract(
        payload,
        "pending-metadata-write.schema.json",
        stage="metadata_prepare",
        error_code="metadata_schema_error",
    ) == payload


def test_authoring_call_budget_keeps_domain_policy_outside_the_llm_path() -> None:
    assert _expected_prepare_llm_calls("domain") == {
        "draft": 3,
        "annotation": 0,
        "repair": 0,
    }
    assert _expected_prepare_llm_calls("dataset") == {
        "draft": 1,
        "annotation": 0,
        "repair": 0,
    }
    assert _expected_prepare_llm_calls("main_filter") == {
        "draft": 1,
        "annotation": 0,
        "repair": 0,
    }
    assert _expected_prepare_llm_calls("domain_policy") == {
        "draft": 0,
        "annotation": 0,
        "repair": 0,
    }
    alias_only = """Natural-language aliases: category and product category -> CATEGORY.
"""
    assert _expected_prepare_llm_calls("main_filter", alias_only) == {
        "draft": 1,
        "annotation": 0,
        "repair": 0,
    }
    assert _expected_prepare_llm_calls(
        "main_filter",
        alias_only,
        source_grounding_mode="explicit_inventory",
    ) == {
        "draft": 0,
        "annotation": 0,
        "repair": 0,
    }
    assert _expected_prepare_llm_calls(
        "domain",
        source_grounding_mode="explicit_inventory",
        trusted_blueprint_configured=True,
    ) == {
        "draft": 0,
        "annotation": 1,
        "repair": 0,
    }


def test_domain_flow_context_tweaks_open_and_close_exact_split_branches() -> None:
    prepared = _domain_flow_context_tweaks(
        mode="prepare",
        domain_id="manufacturing",
        environment="fresh_validation",
        split_prepare=True,
    )
    assert set(prepared) == {
        "authoring_prompt_context_builder",
        "bootstrap_dataset_prompt_context_builder",
        "bootstrap_main_filter_prompt_context_builder",
    }
    assert {
        node_id: values["authoring_kind"]
        for node_id, values in prepared.items()
    } == {
        "authoring_prompt_context_builder": "domain",
        "bootstrap_dataset_prompt_context_builder": "dataset",
        "bootstrap_main_filter_prompt_context_builder": "main_filter",
    }
    assert {values["mode"] for values in prepared.values()} == {"prepare"}
    assert {
        values["environment"] for values in prepared.values()
    } == {"fresh_validation"}
    assert all(values["bootstrap_fragment"] is True for values in prepared.values())

    executed = _domain_flow_context_tweaks(
        mode="execute",
        domain_id="manufacturing",
        environment="fresh_validation",
        split_prepare=False,
    )
    assert {values["mode"] for values in executed.values()} == {"execute"}

    blueprint = _domain_flow_context_tweaks(
        mode="prepare",
        domain_id="manufacturing",
        environment="fresh_validation",
        source_grounding_mode="explicit_inventory",
        split_prepare=False,
        primary_overrides={"trusted_blueprint_sha256": "a" * 64},
    )
    assert blueprint["authoring_prompt_context_builder"]["mode"] == "prepare"
    assert blueprint["authoring_prompt_context_builder"][
        "trusted_blueprint_sha256"
    ] == "a" * 64
    assert blueprint["bootstrap_dataset_prompt_context_builder"]["mode"] == "execute"
    assert blueprint["bootstrap_main_filter_prompt_context_builder"]["mode"] == "execute"


def test_default_http_authoring_sources_are_four_separate_v6_texts() -> None:
    texts, source_hashes, source_evidence = _load_v6_authoring_sources()

    assert set(AUTHORING_INPUT_PATHS) == {
        "domain",
        "dataset",
        "main_filter",
        "domain_policy",
    }
    assert set(texts) == set(AUTHORING_INPUT_PATHS)
    assert set(source_hashes) == set(texts)
    assert set(source_evidence) == set(texts)
    for kind, path in AUTHORING_INPUT_PATHS.items():
        text = path.read_text(encoding="utf-8-sig").strip()
        assert texts[kind] == text
        assert source_hashes[kind] == sha256(text.encode("utf-8")).hexdigest()
        assert source_evidence[kind]["content_sha256"] == source_hashes[kind]
        assert source_evidence[kind]["source_text_persisted"] is False
        assert source_evidence[kind]["source_set_id_sha256"] == sha256(
            DEFAULT_SOURCE_SET_ID.encode("utf-8")
        ).hexdigest()
        style = source_evidence[kind]["style_evidence"]
        assert len(style["style_sha256"]) == 64
        assert style["raw_text_persisted"] is False


def test_reordered_http_authoring_sources_are_selectable_and_text_free_in_evidence() -> None:
    baseline_texts, baseline_hashes, _ = _load_v6_authoring_sources()
    texts, source_hashes, source_evidence = _load_v6_authoring_sources(
        worker_input_dir=FREEFORM_REORDERED_INPUT_DIR,
        source_set_id=FREEFORM_REORDERED_SOURCE_SET_ID,
    )

    assert texts["domain_policy"] == baseline_texts["domain_policy"]
    assert source_hashes["domain_policy"] == baseline_hashes["domain_policy"]
    for kind in ("domain", "dataset", "main_filter"):
        assert source_hashes[kind] != baseline_hashes[kind]
        row = source_evidence[kind]
        assert row["path"].startswith(
            "validation/fixtures/authoring/freeform_reordered_v1/"
        )
        assert row["source_text_persisted"] is False
        assert row["source_set_id_sha256"] == sha256(
            FREEFORM_REORDERED_SOURCE_SET_ID.encode("utf-8")
        ).hexdigest()
        style = row["style_evidence"]
        assert style["markdown_heading_count"] == 0
        assert style["starts_with_markdown_heading"] is False
        assert len(style["style_sha256"]) == 64
        assert texts[kind] not in json.dumps(row, ensure_ascii=False)


def test_source_style_evidence_is_deterministic_and_contains_no_source_excerpt() -> None:
    first = _source_style_evidence("업무 메모입니다.\n\n- 첫 자료\n- 둘째 자료")
    second = _source_style_evidence("업무 메모입니다.\n\n- 첫 자료\n- 둘째 자료")

    assert first == second
    assert first["markdown_heading_count"] == 0
    assert first["bullet_line_count"] == 2
    assert first["paragraph_count"] == 2
    assert len(first["style_sha256"]) == 64
    assert "업무 메모" not in json.dumps(first, ensure_ascii=False)


def test_domain_bootstrap_source_matches_three_input_node_envelope() -> None:
    texts, source_hashes, _ = _load_v6_authoring_sources()
    bundled = _compose_domain_bootstrap_source(
        texts["domain"],
        texts["dataset"],
        texts["main_filter"],
    )

    assert bundled.startswith("--- 도메인 정보 시작 ---\n")
    assert "\n--- 도메인 정보 끝 ---\n\n--- 데이터셋 정보 시작 ---\n" in bundled
    assert "\n--- 데이터셋 정보 끝 ---\n\n--- 주요 필터 정보 시작 ---\n" in bundled
    assert bundled.endswith("\n--- 주요 필터 정보 끝 ---")
    assert all(text in bundled for text in texts.values() if text != texts["domain_policy"])
    assert source_hashes["dataset"] == sha256(texts["dataset"].encode("utf-8")).hexdigest()


def test_default_http_authoring_run_is_freeform_without_blueprint_injection() -> None:
    source = inspect.getsource(run)

    assert AUTHORING_GEMINI_MODEL == "gemini-3.5-flash-lite"
    assert "_load_v6_authoring_sources" in source
    assert "_compose_domain_bootstrap_source" in source
    assert '"chat_input": {"input_value": texts["domain"]}' in source
    assert '"dataset_source_input": {"input_value": texts["dataset"]}' in source
    assert '"input_value": texts["main_filter"]' in source
    assert '"source_grounding_mode": "explicit_inventory"' not in source
    assert "_load_trusted_blueprint" not in source
    assert "trusted_blueprint=" not in source
    assert "trusted_blueprint_pin=" not in source
    assert "_run_freeform_clarification_probe" in source
    assert {"worker_input_dir", "source_set_id"} <= set(inspect.signature(run).parameters)


def test_worker_v6_inputs_are_business_prose_not_registration_grammar() -> None:
    forbidden = (
        "section은",
        "key는",
        "status는",
        "canonical",
        "dataset_id",
        "field_id",
        "source_binding",
        "config_ref",
        "query_ref",
        "query_template",
        "filter_mappings",
        "semantic_type",
        "pandas_function_cases",
        "pandas_generation",
        "pandas_execution",
        "function_name",
        "required_columns",
    )
    source_dirs = (
        AUTHORING_INPUT_PATHS["domain"].parent,
        FREEFORM_REORDERED_INPUT_DIR,
    )
    for source_dir in source_dirs:
        for kind in ("domain", "dataset", "main_filter"):
            text = (source_dir / f"{kind}_v6.txt").read_text(encoding="utf-8-sig")
            lowered = text.casefold()
            assert text.strip()
            assert len(text.encode("utf-8")) <= 65536
            assert all(token.casefold() not in lowered for token in forbidden)

    prompt_dir = AUTHORING_INPUT_PATHS["domain"].parents[3] / "prompts" / "metadata_authoring"
    for name in (
        "domain_common_ko.md",
        "dataset_common_ko.md",
        "main_filter_common_ko.md",
    ):
        prompt = (prompt_dir / name).read_text(encoding="utf-8")
        assert "approved_semantic_vocabulary" in prompt
        assert "작업자" in prompt
        assert "strict" in prompt


def test_freeform_clarification_probe_checks_three_calls_and_forbidden_field_absence() -> None:
    source = inspect.getsource(_run_freeform_clarification_probe)

    assert FREEFORM_CLARIFICATION_PROBE
    assert '"draft_llm_three"' in source
    assert '"annotation_llm_zero"' in source
    assert '"repair_llm_zero"' in source
    assert '"candidate_fields_absent"' in source
    assert '"package_fields_absent"' in source
    assert '"persist_fields_absent"' in source
    assert '"mongo_document_count_increase_zero"' in source
    worker_probes = " ".join(
        (
            FREEFORM_CLARIFICATION_PROBE,
            FREEFORM_CLARIFICATION_DATASET_PROBE,
            FREEFORM_CLARIFICATION_MAIN_FILTER_PROBE,
        )
    ).casefold()
    for forbidden in (
        "canonical",
        "dataset_id",
        "field_id",
        "등록 id",
        "물리 컬럼",
        "semantic type",
        "relation",
        "grain",
    ):
        assert forbidden.casefold() not in worker_probes


def test_order_sales_dataset_patch_source_seals_exact_dataset_and_fields() -> None:
    manifest = extract_authoring_source_manifest(DATASET_PATCH_TEXT)

    assert manifest["required_sections"] == ["datasets", "fields"]
    assert manifest["inventories"]["datasets"] == ["products"]
    assert manifest["inventories"]["dataset_fields"] == {
        "products": ["CATEGORY", "PRODUCT_ID", "PRODUCT_NAME"]
    }


def test_approval_event_and_each_tamper_are_schema_exact_but_hash_distinct() -> None:
    event = _build_approval_event(
        nonce="unit-event-0001",
        candidate_id="candidate:" + "a" * 64,
        candidate_sha256="a" * 64,
        subject_id="metadata-approver:test",
        now=datetime(2026, 8, 1, 1, 2, 3, tzinfo=timezone.utc),
    )
    assert set(event) == {
        "contract_version",
        "event_id",
        "candidate_id",
        "candidate_sha256",
        "decision",
        "subject_id",
        "decided_at",
        "expires_at",
        "idempotency_key",
    }
    tampered = _tampered_approval_events(event)
    assert set(tampered) == {"event_id", "subject_id", "decided_at", "idempotency_key"}
    assert all(sha256_json(value) != sha256_json(event) for value in tampered.values())
    assert all(value["candidate_id"] == event["candidate_id"] for value in tampered.values())


def test_fresh_environment_is_valid_bounded_and_nonce_scoped() -> None:
    first = _fresh_environment("E2E Validation", "0123456789abcdef")
    second = _fresh_environment("E2E Validation", "fedcba9876543210")
    assert first == "e2e_validation_01234567"
    assert first != second
    assert len(first) <= 31


def test_authoring_flow_defaults_keep_admin_blueprint_inputs_empty() -> None:
    rows = [_flow_defaults(path) for path in FLOW_PATHS]
    assert all(row["trusted_blueprint_json_default_empty"] is True for row in rows)
    assert all(row["trusted_blueprint_pin_default_empty"] is True for row in rows)
    assert all(row["source_grounding_mode"] == "freeform_llm" for row in rows)
    assert rows[0]["domain_bootstrap_input_node_ids"] == [
        "chat_input",
        "dataset_source_input",
        "main_filter_source_input",
    ]
    assert rows[0]["natural_source_bundle_node_count"] == 1
    assert all(row["natural_source_bundle_node_count"] == 0 for row in rows[1:])
    assert rows[0]["prompt_node_count"] == 3
    assert rows[0]["context_builder_node_count"] == 3
    assert rows[0]["composer_node_count"] == 3
    assert rows[0]["invoker_node_count"] == 3
    assert all(row["prompt_node_count"] == 1 for row in rows[1:-1])
    assert all(row["context_builder_node_count"] == 1 for row in rows[1:-1])
    assert all(row["composer_node_count"] == 1 for row in rows[1:-1])
    assert all(row["invoker_node_count"] == 1 for row in rows[1:-1])


def test_http_evidence_projects_annotation_and_blueprint_hashes_only() -> None:
    response = {
        "contract_version": "metadata.authoring.response.v1",
        "response_type": "metadata_authoring",
        "status": "ok",
        "stage": "prepared",
        "authoring_kind": "domain",
        "metadata_contract_mode": "domain_package_v2",
        "domain_id": "order_sales",
        "environment": "e2e_validation_01234567",
        "llm_usage": {
            "draft_llm_calls": 0,
            "annotation_llm_calls": 1,
            "repair_llm_calls": 0,
        },
        "validation": {
            "trusted_blueprint": {
                "contract_version": "metadata.blueprint.validation.v1",
                "blueprint_sha256": "a" * 64,
                "executable_sha256": "b" * 64,
                "annotation_proposal_sha256": "c" * 64,
                "external_pin": "passed",
                "executable_immutable": "passed",
            }
        },
    }
    response["response_sha256"] = sha256_json(response)
    evidence = extract_authoring_evidence({"nested": [response]})
    assert evidence["draft_llm_calls"] == 0
    assert evidence["annotation_llm_calls"] == 1
    assert evidence["repair_llm_calls"] == 0
    assert evidence["trusted_blueprint_validation"] == response["validation"]["trusted_blueprint"]


def test_http_evidence_projects_freeform_structured_proposal_seal_only() -> None:
    response = {
        "contract_version": "metadata.authoring.response.v1",
        "response_type": "metadata_authoring",
        "status": "ok",
        "stage": "prepared",
        "authoring_kind": "domain",
        "metadata_contract_mode": "domain_package_v2",
        "domain_id": "manufacturing",
        "environment": "raw_validation_01234567",
        "llm_usage": {
            "draft_llm_calls": 1,
            "annotation_llm_calls": 0,
            "repair_llm_calls": 0,
        },
        "validation": {
            "source_coverage": {
                "contract_version": "source.grounding.evidence.v1",
                "mode": "freeform_llm",
                "source_sha256": "a" * 64,
                "structured_proposal_sha256": "b" * 64,
                "explicit_inventory_coverage": "not_requested",
                "schema_validation": "passed",
                "dependency_closure": "passed",
                "human_approval_required": True,
                "coverage_sha256": "c" * 64,
            },
            "authoring_proposal": {
                "contract_version": "metadata.authoring.proposal.validation.v1",
                "proposal_contract_version": "metadata.authoring.proposal.v1",
                "status": "complete",
                "source_sha256": "a" * 64,
                "proposal_sha256": "d" * 64,
                "draft_sha256": "b" * 64,
                "compact_ir_sha256": "",
                "expanded_draft_sha256": "",
                "section_ir_expander_version": "",
            },
        },
    }
    response["response_sha256"] = sha256_json(response)

    evidence = extract_authoring_evidence({"nested": [response]})

    assert evidence["draft_llm_calls"] == 1
    assert evidence["annotation_llm_calls"] == 0
    assert evidence["repair_llm_calls"] == 0
    assert evidence["source_grounding_validation"] == response["validation"][
        "source_coverage"
    ]
    assert evidence["authoring_proposal_validation"] == response["validation"][
        "authoring_proposal"
    ]
    assert (
        evidence["source_grounding_validation"]["structured_proposal_sha256"]
        == evidence["authoring_proposal_validation"]["draft_sha256"]
    )


def test_http_evidence_projects_three_split_bootstrap_proposal_seals() -> None:
    proposals = {
        branch: {
            "contract_version": "metadata.authoring.proposal.validation.v1",
            "proposal_contract_version": "metadata.authoring.proposal.v1",
            "status": "complete",
            "source_sha256": character * 64,
            "proposal_sha256": chr(ord(character) + 3) * 64,
            "draft_sha256": chr(ord(character) + 6) * 64,
        }
        for branch, character in {
            "domain": "1",
            "dataset": "2",
            "main_filter": "3",
        }.items()
    }
    response = {
        "contract_version": "metadata.authoring.response.v1",
        "response_type": "metadata_authoring",
        "status": "ok",
        "stage": "prepared",
        "authoring_kind": "domain",
        "metadata_contract_mode": "domain_package_v2",
        "domain_id": "manufacturing",
        "environment": "raw_validation_01234567",
        "llm_usage": {
            "draft_llm_calls": 3,
            "annotation_llm_calls": 0,
            "repair_llm_calls": 0,
        },
        "validation": {"authoring_proposals": proposals},
    }
    response["response_sha256"] = sha256_json(response)

    evidence = extract_authoring_evidence({"nested": [response]})

    assert evidence["draft_llm_calls"] == 3
    assert evidence["authoring_proposals_validation"] == proposals
    assert set(evidence["authoring_proposals_validation"]) == {
        "domain",
        "dataset",
        "main_filter",
    }


def test_http_evidence_projects_three_google_schema_bindings_hash_only() -> None:
    purposes = {
        "domain": "metadata_domain_draft",
        "dataset": "metadata_dataset_draft",
        "main_filter": "metadata_main_filter_draft",
    }
    payload: dict[str, list[dict]] = {"nested": []}
    for index, (branch, purpose) in enumerate(purposes.items(), start=1):
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {"branch": {"const": branch}},
            "required": ["branch"],
        }
        schema_hash = sha256_json(schema)
        runtime_context = {
            "contract_version": "prompt.runtime-context.v1",
            "purpose": purpose,
            "variables": {"output_schema": schema},
        }
        runtime_context_sha256 = sha256_json(
            {
                "authority": "untrusted_data",
                "purpose": purpose,
                "variables": runtime_context["variables"],
            }
        )
        response_text = f"private-provider-response-{branch}"
        payload["nested"].extend(
            [
                runtime_context,
                {
                    "contract_version": "llm.invocation.v1",
                    "purpose": purpose,
                    "status": "ok",
                    "prompt_bundle_sha256": sha256_json(
                        {"branch": branch, "purpose": purpose}
                    ),
                    "runtime_context_sha256": runtime_context_sha256,
                    "provider_schema_binding": "google_native_json_schema",
                    "schema_binding_evidence": {
                        "contract_version": "llm.schema-binding.evidence.v1",
                        "binding_status": "google_native_json_schema",
                        "projection": "google_supported_json_schema_subset.v6",
                        "authoritative_schema_sha256": schema_hash,
                        "provider_schema_sha256": str(index) * 64,
                    },
                    "response_text": response_text,
                    "response_sha256": sha256(response_text.encode("utf-8")).hexdigest(),
                },
            ]
        )

    evidence = extract_authoring_evidence(payload)
    validation = _google_authoring_schema_binding_validation(
        evidence["llm_schema_bindings"]
    )

    assert validation["passed"] is True
    assert set(validation["branches"]) == set(purposes)
    assert all(
        row["authoritative_schema_sha256"]
        == row["runtime_output_schema_sha256"]
        for row in validation["branches"].values()
    )
    assert all(
        row["projection"] == "google_supported_json_schema_subset.v6"
        for row in validation["branches"].values()
    )
    projected_json = json.dumps(
        evidence["llm_schema_bindings"], ensure_ascii=False, sort_keys=True
    )
    assert "private-provider-response" not in projected_json
    assert all(
        row["raw_prompt_persisted"] is False
        and row["raw_response_persisted"] is False
        for row in evidence["llm_schema_bindings"].values()
    )


def test_http_evidence_accepts_compact_schema_binding_summaries_without_raw_invocations() -> None:
    bindings = []
    for index, purpose in enumerate(
        (
            "metadata_domain_draft",
            "metadata_dataset_draft",
            "metadata_main_filter_draft",
        ),
        start=1,
    ):
        schema_hash = str(index) * 64
        bindings.append(
            {
                "contract_version": "metadata.llm-schema-binding-summary.v1",
                "purpose": purpose,
                "invocation_count": 1,
                "provider_schema_binding": "google_native_json_schema",
                "binding_status": "google_native_json_schema",
                "projection": "google_supported_json_schema_subset.v6",
                "authoritative_schema_sha256": schema_hash,
                "provider_schema_sha256": str(index + 3) * 64,
                "runtime_output_schema_sha256": schema_hash,
                "raw_prompt_persisted": False,
                "raw_response_persisted": False,
            }
        )
    response = {
        "contract_version": "metadata.authoring.response.v1",
        "response_type": "metadata_authoring",
        "status": "ok",
        "stage": "prepared",
        "authoring_kind": "domain",
        "metadata_contract_mode": "domain_package_v2",
        "domain_id": "manufacturing",
        "environment": "test",
        "llm_usage": {
            "draft_llm_calls": 3,
            "annotation_llm_calls": 0,
            "repair_llm_calls": 0,
        },
        "validation": {
            "llm_schema_bindings": {
                "contract_version": "metadata.llm-schema-bindings.v1",
                "bindings": bindings,
            }
        },
    }
    response["response_sha256"] = sha256_json(response)

    evidence = extract_authoring_evidence({"nested": [response]})
    validation = _google_authoring_schema_binding_validation(
        evidence["llm_schema_bindings"]
    )

    assert evidence["llm_invocation_count"] == 0
    assert validation["passed"] is True
    assert all(
        row["raw_prompt_persisted"] is False
        and row["raw_response_persisted"] is False
        for row in evidence["llm_schema_bindings"].values()
    )


def test_http_evidence_hashes_clarification_text_instead_of_persisting_it() -> None:
    clarification = {
        "contract_version": "metadata.authoring.clarification.v1",
        "questions": ["어떤 데이터셋을 사용하나요?"],
        "missing_fields": ["datasets", "fields"],
        "source_sha256": "a" * 64,
        "proposal_sha256": "b" * 64,
    }
    response = {
        "contract_version": "metadata.authoring.response.v1",
        "response_type": "metadata_authoring",
        "status": "needs_clarification",
        "stage": "clarification",
        "authoring_kind": "domain",
        "metadata_contract_mode": "domain_package_v2",
        "domain_id": "manufacturing",
        "environment": "raw_validation_01234567",
        "llm_usage": {
            "draft_llm_calls": 1,
            "annotation_llm_calls": 0,
            "repair_llm_calls": 0,
        },
        "clarification": clarification,
    }
    response["response_sha256"] = sha256_json(response)

    evidence = extract_authoring_evidence({"nested": [response]})
    projected = evidence["clarification_validation"]

    assert projected["contract_version"] == "metadata.authoring.clarification.v1"
    assert projected["questions_count"] == 1
    assert projected["missing_fields_count"] == 2
    assert projected["source_sha256"] == "a" * 64
    assert projected["proposal_sha256"] == "b" * 64
    assert projected["raw_clarification_persisted"] is False
    assert clarification["questions"][0] not in json.dumps(projected, ensure_ascii=False)
    assert evidence["response_field_presence"] == {
        "candidate_fields": [],
        "package_fields": [],
        "persistence_fields": [],
    }


def test_http_evidence_links_message_and_api_terminals_by_supported_metadata() -> None:
    response = {
        "contract_version": "metadata.authoring.response.v1",
        "response_type": "metadata_authoring",
        "status": "error",
        "stage": "metadata_store_config",
        "authoring_kind": "domain",
        "metadata_contract_mode": "domain_package_v2",
        "domain_id": "order_sales",
        "environment": "e2e_validation_01234567",
        "llm_usage": {"draft_llm_calls": 0, "repair_llm_calls": 0},
        "error": {
            "code": "metadata_policy_error",
            "stage": "metadata_store_config",
            "message": "Approval event does not match the externally sealed approval record.",
            "details": {"actual": {}, "expected": {}},
        },
    }
    response["response_sha256"] = sha256_json(response)
    digest = response["response_sha256"]
    payload = {
        "outputs": [
            {
                "component_id": "authoring_message_presentation",
                "results": {
                    "message": {
                        "session_metadata": {
                            "contract_version": "metadata.authoring.message-link.v1",
                            "response_sha256": digest,
                        }
                    }
                },
            },
            {
                "component_id": "authoring_api_response",
                "artifacts": {"api_response": {"raw": response}},
            },
        ]
    }
    evidence = extract_authoring_evidence(payload)
    assert evidence["response_hash_valid"] is True
    assert evidence["terminal_hashes"] == {"message": [digest], "api": [digest]}
    assert evidence["terminal_equivalent"] is True
    assert evidence["error_detail_keys"] == ["actual", "expected"]
    assert len(evidence["error_message_sha256"]) == 64
    assert evidence["error_invariant"] == "approval_event_external_seal"


def test_safe_failure_preserves_bounded_stage_and_detail_without_exception_text() -> None:
    exc = AuthoringValidationError(
        code="authoring_collection_guard_validation_failed",
        stage="collection_guard_negatives",
        details={
            "case_count": 1,
            "rows": [
                {
                    "case_id": "legacy_name",
                    "error_code": "metadata_policy_error",
                    "error_stage": "metadata_store_config",
                    "error_detail_keys": ["actual", "expected"],
                    "failed_checks": [],
                }
            ],
        },
    )
    failure = _safe_failure(exc)
    assert failure == {
        "type": "AuthoringValidationError",
        "code": "authoring_collection_guard_validation_failed",
        "stage": "collection_guard_negatives",
        "details": exc.details,
    }


def test_pending_storage_wrapper_projects_and_validates_exact_payload() -> None:
    now = datetime(2026, 8, 1, 1, 2, 3, 123000, tzinfo=timezone.utc)
    expires = now + timedelta(minutes=30)
    hash_material = {
        "contract_version": "pending.domain-package.hash-material.v1",
        "expected_active": {"revision": 0, "bundle_sha256": "", "package_sha256": ""},
    }
    candidate_hash = sha256_json(hash_material)
    candidate_id = f"candidate:{candidate_hash}"
    payload = {
        "contract_version": "pending.metadata.write.v1",
        "authoring_kind": "domain",
        "domain_id": "order_sales",
        "environment": "e2e_validation_01234567",
        "candidate_id": candidate_id,
        "candidate_sha256": candidate_hash,
        "status": "prepared",
        "target_revision": 1,
        "base_revision": None,
        "base_bundle_sha256": None,
        "base_package_sha256": None,
        "prepared_at": now.isoformat(),
        "expires_at": expires.isoformat(),
        "hash_material": hash_material,
    }
    wrapper = {
        "_id": candidate_id,
        "pending_payload": payload,
        "pending_payload_sha256": sha256_json(payload),
        "workflow_status": "prepared",
        "expires_at": expires,
        "authoring_kind": "domain",
        "domain_id": "order_sales",
        "environment": "e2e_validation_01234567",
        "storage_only": "ignored-by-canonical-projection",
    }
    canonical, evidence = _pending_evidence(
        wrapper,
        authoring_kind="domain",
        domain_id="order_sales",
        environment="e2e_validation_01234567",
        target_revision=1,
        base_package={},
    )
    assert canonical == payload
    assert evidence["passed"] is True
    assert evidence["checks"]["schema_exact"] is True
    assert "storage_only" not in canonical


def test_section_ownership_detects_outside_change() -> None:
    before = {
        "runtime_catalog": {
            "revision": 1,
            "catalog_sha256": "a" * 64,
            "datasets": {"orders": {"display_name": "주문"}},
            "metrics": {"SALES_AMOUNT": {}},
            "aliases": {},
        }
    }
    valid_after = deepcopy(before)
    valid_after["runtime_catalog"]["revision"] = 2
    valid_after["runtime_catalog"]["catalog_sha256"] = "b" * 64
    valid_after["runtime_catalog"]["datasets"]["orders"]["display_name"] = "주문 기준"
    valid = _section_ownership_checks(before, valid_after, authoring_kind="dataset")
    assert valid["checks"] == {
        "other_sections_unchanged": True,
        "at_least_one_owned_section_changed": True,
    }

    invalid_after = deepcopy(valid_after)
    invalid_after["runtime_catalog"]["metrics"]["SALES_AMOUNT"]["unit"] = "USD"
    invalid = _section_ownership_checks(before, invalid_after, authoring_kind="dataset")
    assert invalid["checks"]["other_sections_unchanged"] is False
    assert invalid["changed_outside_ownership"] == ["metrics"]


def test_order_sales_semantic_completeness_rejects_empty_or_missing_sections() -> None:
    catalog = {
        section: {identity: {} for identity in identities}
        for section, identities in ORDER_SALES_REQUIRED_MANIFEST.items()
    }
    catalog["datasets"]["refunds"] = {
        "fields": {"ORDER_ID": {}, "PRODUCT_ID": {}, "REFUND_AMOUNT": {}}
    }
    catalog["datasets"]["targets"] = {
        "fields": {"PRODUCT_ID": {}, "TARGET_AMOUNT": {}, "TARGET_DATE": {}}
    }
    catalog["relations"]["orders_refunds"] = {
        "left_keys": ["ORDER_ID", "PRODUCT_ID"],
        "right_keys": ["ORDER_ID", "PRODUCT_ID"],
        "cardinality": "one_to_zero_or_one",
    }
    catalog["aliases"] = {
        "metric:NET_SALES_AMOUNT": {"values": ["순매출"]},
    }
    catalog["entity_groups"] = {
        "electronics_category": {
            "target_field": "CATEGORY",
            "aliases": ["전자 카테고리"],
            "selection": {"value": "A"},
        },
        "living_category": {
            "target_field": "CATEGORY",
            "aliases": ["생활 카테고리"],
            "selection": {"value": "B"},
        },
    }
    catalog["prompt_extensions"] = {"intent": "registered", "answer": "registered"}
    catalog["output_profile"] = {"currency": "KRW"}
    complete = _semantic_completeness({"runtime_catalog": catalog})
    assert complete["passed"] is True
    assert all(not row["missing_ids"] for row in complete["sections"].values())

    incomplete = deepcopy(catalog)
    incomplete["metrics"].pop("NET_SALES_AMOUNT")
    failed = _semantic_completeness({"runtime_catalog": incomplete})
    assert failed["passed"] is False
    assert failed["sections"]["metrics"]["missing_ids"] == ["NET_SALES_AMOUNT"]


def test_manufacturing_semantic_completeness_uses_hash_only_reference_oracle() -> None:
    catalog = json.loads(
        MANUFACTURING_COMPILED_CATALOG_PATH.read_text(encoding="utf-8")
    )
    complete = _manufacturing_semantic_completeness({"runtime_catalog": catalog})

    assert complete["passed"] is True
    assert complete["raw_id_lists_persisted"] is False
    assert all(
        set(row) == {
            "expected_count",
            "actual_count",
            "missing_count",
            "missing_ids_sha256",
            "extra_count",
            "extra_ids_sha256",
            "passed",
        }
        for row in complete["sections"].values()
    )

    missing_metric = deepcopy(catalog)
    missing_metric["metrics"].pop("WIP_BOH_QTY")
    failed = _manufacturing_semantic_completeness(
        {"runtime_catalog": missing_metric}
    )
    assert failed["passed"] is False
    assert failed["sections"]["metrics"]["missing_count"] == 1
    assert len(failed["sections"]["metrics"]["missing_ids_sha256"]) == 64
    assert "WIP_BOH_QTY" not in json.dumps(failed, ensure_ascii=False)

    changed_boh = deepcopy(catalog)
    changed_boh["metrics"]["WIP_BOH_QTY"]["temporal_contract"]["query_time"][
        "offset_days"
    ] = 0
    changed = _manufacturing_semantic_completeness(
        {"runtime_catalog": changed_boh}
    )
    assert changed["passed"] is False
    assert changed["capability_checks"]["boh_contract_exact"] is False
    _compose_domain_bootstrap_source,
    _run_freeform_clarification_probe,
