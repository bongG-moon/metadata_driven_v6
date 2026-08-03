from __future__ import annotations

import json
from copy import deepcopy

import pytest

from reference_runtime.metadata_collections import METADATA_COLLECTIONS
from tools.flow_builder_support import BuildContractError
from tools.validate_langflow_http_authoring_e2e import (
    AUTHORING_GEMINI_MODEL,
    DEFAULT_SOURCE_SET_ID,
    FLOW_PATHS,
    V6_INPUT_DIR,
    AuthoringValidationError,
    _authoring_tweaks,
    _flow_defaults,
    _fresh_environment,
    _load_v6_authoring_sources,
    _validate_loader_runtime_bundle,
)


def _runtime_loader_context() -> dict:
    package_path = (
        V6_INPUT_DIR.parents[1]
        / "domain_packs"
        / "manufacturing"
        / "compiled"
        / "domain_package.json"
    )
    package = json.loads(package_path.read_text(encoding="utf-8"))
    catalog = deepcopy(package["runtime_catalog"])
    return {
        "contract_version": "pipeline.context.v1",
        "ok": True,
        "stage": "domain_bundle",
        "domain_bundle": {
            "contract_version": "domain.bundle.runtime.v1",
            "domain_id": package["domain_id"],
            "environment": package["environment"],
            "revision": str(package["revision"]),
            "source_mode": "three_collections",
            "catalog_sha256": catalog["catalog_sha256"],
            "package_sha256": package["package_sha256"],
            "bundle_sha256": package["bundle_sha256"],
            "runtime_catalog": catalog,
        },
    }


def test_current_authoring_flows_use_save_and_fixed_three_collections() -> None:
    defaults = [_flow_defaults(path) for path in FLOW_PATHS]

    assert {item["authoring_kind"] for item in defaults} == {
        "domain",
        "dataset",
        "main_filter",
    }
    assert all(item["passed"] for item in defaults)
    assert all(item["mode"] == "save" for item in defaults)
    assert all(
        item["collection_defaults"]
        == {
            "domain_collection": METADATA_COLLECTIONS["domain"],
            "table_collection": METADATA_COLLECTIONS["table_catalog"],
            "main_filter_collection": METADATA_COLLECTIONS["main_filter"],
        }
        for item in defaults
    )
    assert all(item["model_names"] == [AUTHORING_GEMINI_MODEL] for item in defaults)


def test_authoring_tweaks_expose_selector_free_save_replace_validate_contract() -> None:
    sources, _, _ = _load_v6_authoring_sources(
        worker_input_dir=V6_INPUT_DIR,
        source_set_id=DEFAULT_SOURCE_SET_ID,
    )
    common = {
        "domain_id": "manufacturing",
        "environment": "validation_001",
        "mongo_uri": "mongodb://example.invalid",
        "mongo_database": "datagov_v6_validation",
        "sources": sources,
    }
    forbidden = {
        "metadata_source_mode",
        "active_collection",
        "bundle_collection",
        "pending_collection",
        "approval_event",
        "reference_instant",
        "reference_timezone",
        "authoring_kind",
        "domain_id",
        "environment",
        "dry_run",
        "registry_json",
    }

    for kind in ("domain", "dataset", "main_filter"):
        for mode in ("save", "replace", "validate_only"):
            tweaks = _authoring_tweaks(kind=kind, mode=mode, **common)
            serialized_keys = {
                key
                for value in tweaks.values()
                if isinstance(value, dict)
                for key in value
            }
            assert forbidden.isdisjoint(serialized_keys)
            assert tweaks["simple_metadata_authoring_engine"]["mode"] == mode
            assert tweaks["draft_language_model"] == {"temperature": 0.0, "stream": False}

    with pytest.raises(ValueError, match="authoring_mode_invalid"):
        _authoring_tweaks(kind="domain", mode="prepare", **common)


def test_worker_sources_remain_three_freeform_text_inputs() -> None:
    sources, hashes, evidence = _load_v6_authoring_sources(
        worker_input_dir=V6_INPUT_DIR,
        source_set_id=DEFAULT_SOURCE_SET_ID,
    )

    assert set(sources) == {"domain", "dataset", "main_filter"}
    assert all(text.strip() for text in sources.values())
    assert all(len(value) == 64 for value in hashes.values())
    assert evidence["raw_source_text_persisted"] is False

    with pytest.raises(BuildContractError, match="authoring_source_set_id_invalid"):
        _load_v6_authoring_sources(worker_input_dir=V6_INPUT_DIR, source_set_id="INVALID VALUE")


def test_selector_free_loader_projection_is_closed_and_hash_bound() -> None:
    context = _runtime_loader_context()
    bundle = _validate_loader_runtime_bundle(
        context,
        expected_domain_id="manufacturing",
        expected_environment="production",
    )

    assert bundle["source_mode"] == "three_collections"
    assert bundle["catalog_sha256"] == bundle["runtime_catalog"]["catalog_sha256"]

    tampered = deepcopy(context)
    tampered["domain_bundle"]["source_mode"] = "v6_active"
    with pytest.raises(AuthoringValidationError) as error:
        _validate_loader_runtime_bundle(
            tampered,
            expected_domain_id="manufacturing",
            expected_environment="production",
        )
    assert error.value.code == "loader_runtime_projection_invalid"
    assert "source_mode_exact" in error.value.details["failed_checks"]


def test_validation_environment_name_is_bounded_and_ascii() -> None:
    value = _fresh_environment("제조 Release 2026", "abcdef0123456789")
    assert value == "release_2026_abcdef012345"
    assert len(value) <= 31
