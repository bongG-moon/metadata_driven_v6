from __future__ import annotations

import json
from pathlib import Path

import pytest

from reference_runtime.canonical import ContractError, sha256_json
from reference_runtime.metadata_compiler import (
    CATALOG_CONTRACT_VERSION,
    CATALOG_TOP_LEVEL_KEYS,
    PRODUCT_GRAIN,
    build_runtime_catalog,
    compiled_records,
    compute_catalog_sha256,
    load_runtime_catalog,
    source_provenance,
    validate_runtime_catalog,
    write_runtime_catalog,
)
from tools.compile_metadata import compile_baseline
from tools.migrate_v5_metadata import (
    V5_SOURCE_COLLECTIONS,
    apply_v6_candidates,
    assert_collection_boundaries,
    build_migration_plan,
    read_v5_collections,
)


ROOT = Path(__file__).resolve().parents[1]
AUTHORING = ROOT / "metadata" / "authoring"


def test_catalog_is_deterministic_closed_and_hash_sealed() -> None:
    first = build_runtime_catalog(AUTHORING)
    second = build_runtime_catalog(AUTHORING)
    assert first == second
    assert first["contract_version"] == CATALOG_CONTRACT_VERSION
    assert set(first) == CATALOG_TOP_LEVEL_KEYS
    assert first["catalog_sha256"] == compute_catalog_sha256(first)
    assert len(first["datasets"]) == 10
    assert len(first["metrics"]) == 17
    assert len(first["process_groups"]) == 25


def test_catalog_dataset_contracts_have_required_router_shape() -> None:
    catalog = build_runtime_catalog(AUTHORING)
    for key, dataset in catalog["datasets"].items():
        assert dataset["key"] == key
        assert {"key", "family", "source_type", "fields", "parameters", "default_detail_fields"} <= set(dataset)
        assert dataset["read_policy"]["read_only"] is True
        assert set(dataset["default_detail_fields"]) <= set(dataset["fields"])
    assert catalog["datasets"]["production"]["fields"]["PRODUCTION_QTY"]["physical_column"] == "PRODUCTION"
    assert catalog["datasets"]["target"]["fields"]["MODE"]["physical_column"] == "Mode"
    assert catalog["datasets"]["equipment_assign"]["fields"]["OPER_NAME"]["physical_column"] == "OPER_NM"
    assert catalog["datasets"]["hold_history"]["fields"]["HOLD_EVENT_AT"]["physical_column"] == "HOLD_TM"


def test_catalog_contains_model_independent_temporal_metric_and_grain_rules() -> None:
    catalog = build_runtime_catalog(AUTHORING)
    boh = catalog["metrics"]["WIP_BOH_QTY"]
    assert boh["source_binding"] == {"dataset_family": "wip", "field": "WIP_QTY"}
    assert boh["temporal_contract"]["query_time"]["offset_days"] == -1
    assert boh["temporal_contract"]["dataset_selector"]["dataset_key"] == "wip"
    assert boh["temporal_contract"]["disallowed_dataset_keys"] == ["wip_today"]
    assert catalog["metrics"]["UPH"]["additivity"]["allowed_rollups"] == ["mean"]
    hold_duration = catalog["metrics"]["HOLD_DURATION_HOURS"]
    assert hold_duration["formula"]["expression"]["op"] == "datetime_diff_hours"
    assert hold_duration["formula"]["evaluation_stage"] == "after_aggregate"
    hold_recipe = catalog["recipes"]["hold.oldest_current_history"]
    assert hold_recipe["derived_metrics"] == ["HOLD_DURATION_HOURS"]
    rank_step = next(step for step in hold_recipe["default_operation_template"]["steps"] if step["op"] == "rank")
    assert rank_step["include_ties"] is True
    assert catalog["recipes"]["product.standard"]["grain"]["keys"] == PRODUCT_GRAIN
    assert catalog["recipes"]["presence.left_positive_right_zero"]["default_operation_template"]["op"] == "presence_filter"


def test_corpus_aliases_and_exact_process_candidates_are_compiled_from_domain() -> None:
    catalog = build_runtime_catalog(AUTHORING)
    input_aliases = {item["text"] for item in catalog["aliases"]["metric:INPUT_QTY"]["values"]}
    package_out_aliases = {item["text"] for item in catalog["aliases"]["metric:PKG_OUT_QTY"]["values"]}
    operation_aliases = {item["text"] for item in catalog["aliases"]["field:OPER_NAME"]["values"]}
    generation_aliases = {item["text"] for item in catalog["aliases"]["field:OPER_NUM"]["values"]}
    assert {"INPUT 수량", "INPUT실적"} <= input_aliases
    assert "PKG OUT실적" in package_out_aliases
    assert {"세부 공정별", "공정별"} <= operation_aliases
    assert "차수별" in generation_aliases
    for candidate in ["process:D/A1", "process:W/B2", "process:FCB/H"]:
        assert candidate in catalog["aliases"]
        assert catalog["aliases"][candidate]["target_type"] == "process"
        assert catalog["aliases"][candidate]["provenance_source"] == "domain"
    assert catalog["aliases"]["process_group:WBM"]["target_key"] == "WBM"
    assert catalog["process_groups"]["WBM"]["members"] == ["W/BM"]
    assert "W/B1" not in catalog["process_groups"]["WBM"]["members"]


def test_product_groups_are_closed_typed_predicates() -> None:
    catalog = build_runtime_catalog(AUTHORING)
    mobile = catalog["product_groups"]["MOBILE"]["predicate"]
    pop = catalog["product_groups"]["POP"]["predicate"]
    assert mobile["clauses"][-1] == {"field": "MCP_NO", "operator": "null_or_blank"}
    assert pop["clauses"][-1] == {"field": "MCP_NO", "operator": "is_not_blank"}
    assert all("physical_column" not in json.dumps(item) for item in catalog["product_groups"].values())


def test_tampered_catalog_and_invalid_non_additive_rollup_are_rejected() -> None:
    catalog = build_runtime_catalog(AUTHORING)
    catalog["datasets"]["production"]["family"] = "changed"
    with pytest.raises(ContractError) as exc:
        validate_runtime_catalog(catalog)
    assert exc.value.code == "metadata_dependency_error"

    catalog = build_runtime_catalog(AUTHORING)
    catalog["metrics"]["UPH"]["additivity"]["allowed_rollups"].append("sum")
    catalog["catalog_sha256"] = compute_catalog_sha256(catalog)
    with pytest.raises(ContractError) as exc:
        validate_runtime_catalog(catalog)
    assert exc.value.code == "metadata_dependency_error"


def test_compiled_records_are_versioned_hash_linked_and_provenanced() -> None:
    catalog = build_runtime_catalog(AUTHORING)
    provenance = source_provenance(AUTHORING)
    records = compiled_records(catalog, provenance)
    assert records
    assert all(record["schema_version"] == "metadata.v6" for record in records)
    assert all(record["contract_sha256"] == sha256_json(record["contract"]) for record in records)
    assert all(record["validation"]["catalog_sha256"] == catalog["catalog_sha256"] for record in records)
    exact_process = next(record for record in records if record["kind"] == "alias" and record["identity"]["key"] == "process:D/A1")
    assert exact_process["provenance"]["source_id"] == provenance["domain"]["source_id"]


def test_catalog_file_round_trip_and_compile_report(tmp_path: Path) -> None:
    catalog = build_runtime_catalog(AUTHORING)
    path = write_runtime_catalog(tmp_path / "runtime_catalog.json", catalog)
    assert load_runtime_catalog(path) == catalog
    report = compile_baseline(authoring_root=AUTHORING, output_dir=tmp_path / "compiled")
    assert report["round_trip_ok"] is True
    assert report["v5_write_operations"] == 0
    assert report["counts"]["datasets"] == 10
    assert report["counts"]["metrics"] == 17
    assert (tmp_path / "compiled" / "runtime_catalog.json").is_file()
    assert (tmp_path / "compiled" / "metadata_records.jsonl").is_file()


class _FakeCollection:
    def __init__(self, rows: list[dict] | None = None) -> None:
        self.rows = rows or []
        self.find_calls = 0
        self.inserted: list[dict] = []

    def find(self, query: dict) -> list[dict]:
        assert query == {}
        self.find_calls += 1
        return self.rows

    def insert_one(self, document: dict) -> None:
        self.inserted.append(document)


class _FakeDatabase:
    def __init__(self) -> None:
        self.collections: dict[str, _FakeCollection] = {}

    def __getitem__(self, name: str) -> _FakeCollection:
        return self.collections.setdefault(name, _FakeCollection())

    def __setitem__(self, name: str, collection: _FakeCollection) -> None:
        self.collections[name] = collection


def test_v5_migration_reads_legacy_only_and_writes_v6_only() -> None:
    database = _FakeDatabase()
    for name in V5_SOURCE_COLLECTIONS:
        database[name] = _FakeCollection([{"_id": f"{name}:1", "key": "legacy"}])
    records = read_v5_collections(database)
    assert set(records) == set(V5_SOURCE_COLLECTIONS)
    assert all(database[name].find_calls == 1 for name in V5_SOURCE_COLLECTIONS)
    assert all(not database[name].inserted for name in V5_SOURCE_COLLECTIONS)

    plan = build_migration_plan(authoring_root=AUTHORING, v5_records=records)
    assert plan["report"]["v5_write_operations"] == 0
    assert plan["report"]["quarantined_v5_record_count"] == 3
    result = apply_v6_candidates(database, plan)
    assert result["report"]["v5_write_operations"] == 0
    assert result["report"]["v6_write_operations"] == len(plan["candidates"])
    assert all(not database[name].inserted for name in V5_SOURCE_COLLECTIONS)
    written_collections = {name for name, collection in database.collections.items() if collection.inserted}
    assert written_collections
    assert all(name.startswith("agent_v6_") for name in written_collections)


def test_collection_boundary_rejects_v5_target() -> None:
    with pytest.raises(ValueError):
        assert_collection_boundaries(V5_SOURCE_COLLECTIONS, ["agent_v4_domain_items"])
