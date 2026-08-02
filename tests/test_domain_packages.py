from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from reference_runtime.canonical import ContractError
from reference_runtime.domain_packages import (
    ACTIVE_POINTER_COLLECTION,
    DOMAIN_PACKAGE_COLLECTION,
    adapt_legacy_catalog_v1,
    build_runtime_catalog_v2,
    compile_domain_package,
    load_active_domain_bundle,
    make_active_pointer_document,
    make_bundle_document,
    validate_domain_package,
)
from reference_runtime.metadata_compiler import build_runtime_catalog
from reference_runtime.registered_functions import registered_function_descriptor
from tools.compile_metadata import compile_authoring_draft
from tools.migrate_v5_metadata import (
    V5_SOURCE_COLLECTIONS,
    activate_v6_bundle,
    apply_v6_candidates,
    build_migration_plan,
)


ROOT = Path(__file__).resolve().parents[1]
ORDER_SALES_DRAFT = ROOT / "metadata" / "domain_packs" / "order_sales" / "authoring_draft.json"


def _draft() -> dict:
    return json.loads(ORDER_SALES_DRAFT.read_text(encoding="utf-8"))


def test_natural_language_draft_contract_compiles_deterministically_to_generic_package() -> None:
    first = compile_domain_package(_draft(), "order_sales", "test", revision=3)
    second = compile_domain_package(_draft(), "order_sales", "test", revision=3)
    assert first == second
    assert first["contract_version"] == "domain.package.v1"
    assert first["domain_id"] == "order_sales"
    assert first["environment"] == "test"
    assert first["revision"] == 3
    catalog = build_runtime_catalog_v2(first)
    assert catalog["contract_version"] == "metadata.runtime.catalog.v2"
    assert set(catalog["datasets"]) == {"orders", "products", "refunds", "targets"}
    assert set(catalog["relations"]) == {"orders_products", "orders_refunds", "sales_targets"}
    assert set(catalog["metrics"]) >= {
        "SALES_AMOUNT",
        "REFUND_AMOUNT",
        "TARGET_AMOUNT",
        "NET_SALES_AMOUNT",
        "ACHIEVEMENT_RATE",
    }
    assert catalog["datasets"]["orders"]["source_adapter"] == "dummy.orders.v1"
    assert "aggregate" in catalog["fields"]["SALES_AMOUNT"]["roles"]


@pytest.mark.parametrize(
    ("path", "secret_value"),
    [
        (
            ("description",),
            "mongodb+srv://" + "runtime_user:" + "real_password@cluster.example/db",
        ),
        (("description",), "AIza" + "A" * 32),
        (("description",), "-----BEGIN " + "PRIVATE KEY----- not-a-real-key"),
        (("description",), "password=" + "supersecret-value"),
    ],
    ids=["mongo_uri", "google_key", "private_key", "password_assignment"],
)
def test_authoring_draft_rejects_credential_like_scalar_values(
    path: tuple[str, ...], secret_value: str
) -> None:
    draft = _draft()
    target = draft
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = secret_value

    with pytest.raises(ContractError) as exc_info:
        compile_domain_package(draft, "order_sales", "test", revision=3)

    assert exc_info.value.code == "metadata_dependency_error"
    assert "secret/credential" in str(exc_info.value)


def test_authoring_draft_allows_redacted_secret_guidance_without_a_value() -> None:
    draft = _draft()
    draft["description"] = "credential 값은 metadata에 저장하지 않으며 password=<redacted>로만 안내한다."

    package = compile_domain_package(draft, "order_sales", "test", revision=3)

    assert package["runtime_catalog"]["description"] == draft["description"]


def test_domain_identity_containing_token_is_not_misclassified_as_secret_key() -> None:
    draft = _draft()
    draft["recipes"]["product_token_match_case"] = deepcopy(
        draft["recipes"]["sales.rank"]
    )

    package = compile_domain_package(draft, "order_sales", "test", revision=3)

    assert "product_token_match_case" in package["runtime_catalog"]["recipes"]


def test_registered_function_tokens_are_not_misclassified_as_credentials() -> None:
    draft = _draft()
    descriptor = registered_function_descriptor("core.trim_and_match_tokens", 1)
    draft["specialized_functions"] = [
        {
            "function_id": "core.trim_and_match_tokens",
            "version": 1,
            "execution_mode": "registered_standalone",
            "implementation_sha256": descriptor["implementation_sha256"],
            "input_schema": descriptor["input_schema"],
            "output_schema": descriptor["output_schema"],
            "required_fields": ["PRODUCT_NAME"],
            "limits": {
                "timeout_ms": 1000,
                "max_input_rows": 1000,
                "max_output_rows": 1000,
                "max_output_bytes": 100000,
            },
            "failure_policy": "fail_closed",
            "aliases": ["상품명 토큰 일치"],
            "call_template": {
                "dataset_ref": "orders",
                "field_ref": "PRODUCT_NAME",
                "parameters": {
                    "tokens": ["priority"],
                    "operator": "equals",
                    "match_mode": "any",
                    "case_sensitive": False,
                },
                "output_fields": ["PRODUCT_NAME", "SALES_AMOUNT"],
            },
        }
    ]

    package = compile_domain_package(draft, "order_sales", "test", revision=3)
    card = package["runtime_catalog"]["specialized_functions"][0]

    assert "tokens" in card["input_schema"]["properties"]
    assert card["call_template"]["parameters"]["tokens"] == ["priority"]


@pytest.mark.parametrize(
    "secret_key",
    ["api_key", "access_token", "refreshToken", "client_secret", "password", "connection_string", "mongo_uri"],
)
def test_authoring_draft_still_rejects_credential_key_names(secret_key: str) -> None:
    draft = _draft()
    draft["output_profile"][secret_key] = "must-not-be-stored"

    with pytest.raises(ContractError) as exc_info:
        compile_domain_package(draft, "order_sales", "test", revision=3)

    assert exc_info.value.code == "metadata_dependency_error"
    assert "secret/credential" in str(exc_info.value)


def test_compiler_rejects_executable_code_secret_and_invalid_relation() -> None:
    draft = _draft()
    draft["recipes"]["bad"] = {
        "aliases": ["bad"],
        "required_slots": [],
        "python_code": "import os",
    }
    with pytest.raises(ContractError):
        compile_domain_package(draft, "order_sales", "test")

    draft = _draft()
    draft["output_profile"]["api_key"] = "must-not-be-stored"
    with pytest.raises(ContractError):
        compile_domain_package(draft, "order_sales", "test")

    draft = _draft()
    draft["relations"]["orders_products"]["right_keys"] = ["UNKNOWN"]
    with pytest.raises(ContractError):
        compile_domain_package(draft, "order_sales", "test")


@pytest.mark.parametrize(
    ("mutation", "expected_message"),
    [
        (
            lambda draft: draft["metrics"]["ACHIEVEMENT_RATE"]["formula"].update(
                {"denominator_metric": "MISSING_METRIC"}
            ),
            "Formula metric reference is not registered",
        ),
        (
            lambda draft: (
                draft["metrics"]["SALES_AMOUNT"]["source_binding"].update(
                    {"field": "PRODUCT_NAME"}
                ),
                draft["metrics"]["SALES_AMOUNT"].update(
                    {"source_field": "PRODUCT_NAME"}
                ),
            ),
            "Metric source field is not present in every dataset of its family",
        ),
        (
            lambda draft: draft["recipes"]["sales.summary"].update(
                {
                    "default_operation_template": {
                        "op": "ordered_range",
                        "field": "ORDER_DATE",
                    }
                }
            ),
            "Recipe uses an operation outside its planner profile",
        ),
    ],
)
def test_generic_compiler_fails_closed_for_semantic_closure_regressions(
    mutation, expected_message: str
) -> None:
    draft = _draft()
    mutation(draft)
    with pytest.raises(ContractError, match=expected_message):
        compile_domain_package(draft, "order_sales", "test")


def test_formula_dag_zero_policy_and_recipe_registry_refs_fail_closed() -> None:
    draft = _draft()
    draft["metrics"]["NET_SALES_AMOUNT"]["formula"] = {
        "op": "add",
        "left_metric": "NET_SALES_AMOUNT",
        "right_metric": "SALES_AMOUNT",
    }
    with pytest.raises(ContractError, match="dependency cycle"):
        compile_domain_package(draft, "order_sales", "test")

    draft = _draft()
    draft["metrics"]["ACHIEVEMENT_RATE"]["formula"]["zero_division"] = "invent"
    with pytest.raises(ContractError, match="zero policy"):
        compile_domain_package(draft, "order_sales", "test")

    draft = _draft()
    draft["recipes"]["sales.by_product"]["default_operation_template"][
        "relation_id"
    ] = "missing_relation"
    with pytest.raises(ContractError, match="reference is not registered"):
        compile_domain_package(draft, "order_sales", "test")


def test_predicate_and_entity_group_fields_require_filter_compatible_registry_entries() -> None:
    draft = _draft()
    draft["predicates"]["bad_product"] = {
        "grain_id": "product",
        "allowed_operators": ["eq"],
        "predicate": {"field": "MISSING_FIELD", "operator": "eq", "value": "x"},
    }
    with pytest.raises(ContractError, match="Filter field is not registered"):
        compile_domain_package(draft, "order_sales", "test")

    draft = _draft()
    draft["entity_groups"]["all_products"]["entity"] = "SALES_AMOUNT"
    draft["datasets"]["orders"]["fields"]["SALES_AMOUNT"]["roles"] = [
        role
        for role in draft["datasets"]["orders"]["fields"]["SALES_AMOUNT"]["roles"]
        if role not in {"filter", "group"}
    ]
    with pytest.raises(ContractError, match="Entity group target"):
        compile_domain_package(draft, "order_sales", "test")


def test_package_and_active_pointer_are_hash_bound() -> None:
    package = compile_domain_package(_draft(), "order_sales", "production", lifecycle_status="active")
    database = _FakeDatabase()
    pointer = make_active_pointer_document(package)
    bundle = make_bundle_document(package)
    database[ACTIVE_POINTER_COLLECTION].rows.append(pointer)
    database[DOMAIN_PACKAGE_COLLECTION].rows.append(bundle)
    assert load_active_domain_bundle(database, "order_sales", "production") == package
    assert pointer["_id"] == "active:production:order_sales"

    tampered = deepcopy(bundle)
    tampered["runtime_catalog"]["display_name"] = "tampered"
    database[DOMAIN_PACKAGE_COLLECTION].rows = [tampered]
    with pytest.raises(ContractError):
        load_active_domain_bundle(database, "order_sales", "production")
    with pytest.raises(ContractError):
        load_active_domain_bundle(database, "order_sales", "other")


def test_active_loader_rejects_cross_domain_pointer_identity() -> None:
    order_sales = compile_domain_package(
        _draft(), "order_sales", "validation", lifecycle_status="active"
    )
    database = _FakeDatabase()
    pointer = make_active_pointer_document(order_sales)
    pointer["domain_id"] = "manufacturing"
    database[ACTIVE_POINTER_COLLECTION].rows.append(pointer)
    database[DOMAIN_PACKAGE_COLLECTION].rows.append(make_bundle_document(order_sales))

    with pytest.raises(ContractError):
        load_active_domain_bundle(database, "order_sales", "validation")


def test_active_loader_rejects_bundle_with_different_domain_identity() -> None:
    other_domain = compile_domain_package(
        _draft(), "other_sales", "validation", lifecycle_status="active"
    )
    database = _FakeDatabase()
    pointer = make_active_pointer_document(other_domain)
    pointer["_id"] = "active:validation:order_sales"
    pointer["domain_id"] = "order_sales"
    database[ACTIVE_POINTER_COLLECTION].rows.append(pointer)
    database[DOMAIN_PACKAGE_COLLECTION].rows.append(make_bundle_document(other_domain))

    with pytest.raises(ContractError):
        load_active_domain_bundle(database, "order_sales", "validation")


def test_manufacturing_v1_isolated_pack_adapts_to_v2_without_changing_v1() -> None:
    catalog_v1 = build_runtime_catalog(ROOT / "metadata" / "authoring")
    package = adapt_legacy_catalog_v1(catalog_v1)
    validate_domain_package(package)
    assert catalog_v1["contract_version"] == "metadata.runtime.catalog.v1"
    assert package["runtime_catalog"]["contract_version"] == "metadata.runtime.catalog.v2"
    assert len(package["runtime_catalog"]["datasets"]) == 10
    assert len(package["runtime_catalog"]["fields"]) == 47


def test_compile_cli_api_writes_package_catalog_bundle_and_pointer(tmp_path: Path) -> None:
    output = tmp_path / "compiled"
    report = compile_authoring_draft(
        ORDER_SALES_DRAFT,
        domain_id="order_sales",
        environment="test",
        revision=1,
        lifecycle_status="validated",
        output_dir=output,
    )
    assert report["v5_write_operations"] == 0
    assert report["bundle_sha256"]
    for name in ["domain_package.json", "runtime_catalog.v2.json", "bundle_document.json", "active_pointer.json"]:
        assert (output / name).is_file()


def test_v5_documents_are_converted_when_possible_and_only_unsafe_rows_are_quarantined() -> None:
    records = {
        "agent_v4_domain_items": [
            {
                "_id": "domain:analysis_recipes:sales_rank",
                "section": "analysis_recipes",
                "key": "sales_rank",
                "payload": {"display_name": "매출 순위", "aliases": ["상위 매출"]},
            }
        ],
        "agent_v4_table_catalog_items": [
            {
                "_id": "table_catalog:orders",
                "dataset_key": "orders",
                "payload": {
                    "display_name": "주문",
                    "source_config": {"source_type": "oracle", "query_template": "SELECT reviewed"},
                    "filter_mappings": {"ORDER_DATE": "ORDER_DT", "SALES_AMOUNT": "AMT"},
                    "metric_semantics": {
                        "SALES_AMOUNT": {"semantic_type": "currency", "additive": True, "default_rollup": "sum"}
                    },
                },
            }
        ],
        "agent_v4_main_flow_filters": [
            {
                "_id": "main_flow_filter:ORDER_DATE",
                "filter_key": "ORDER_DATE",
                "payload": {
                    "display_name": "주문일",
                    "aliases": ["날짜"],
                    "operator": "between",
                    "value_type": "LocalDate",
                    "value_shape": "range",
                },
            },
            {
                "_id": "main_flow_filter:unsafe",
                "filter_key": "unsafe",
                "payload": {"display_name": "unsafe", "api_key": "secret"},
            },
        ],
    }
    plan = build_migration_plan(v5_records=records)
    assert plan["report"]["v5_record_count"] == 4
    assert plan["report"]["converted_v5_record_count"] == 3
    assert plan["report"]["quarantined_v5_record_count"] == 1
    assert plan["report"]["v5_write_operations"] == 0
    converted = [item for item in plan["candidates"] if item.get("source_collection")]
    assert {item["source_collection"] for item in converted} == set(V5_SOURCE_COLLECTIONS)
    table_contract = next(
        item["record"]["contract"]
        for item in converted
        if item["source_collection"] == "agent_v4_table_catalog_items"
    )
    assert "SELECT reviewed" not in json.dumps(table_contract)
    assert table_contract["legacy_contract"]["source_config"]["legacy_query_template_sha256"]


def test_bundle_activation_is_cas_bound_audited_and_idempotent() -> None:
    plan = build_migration_plan(domain_id="manufacturing", environment="production")
    bundle_candidate = next(
        item for item in plan["candidates"] if item["target_collection"] == DOMAIN_PACKAGE_COLLECTION
    )
    database = _FakeDatabase()
    database[DOMAIN_PACKAGE_COLLECTION].insert_one(deepcopy(bundle_candidate["record"]))

    first = activate_v6_bundle(database, plan, idempotency_key="test-activate-1")
    assert first["activation_status"] == "activated"
    assert first["active_pointer_write_operations"] == 1
    assert first["activation_audit_write_operations"] == 1
    assert first["active_pointer_id"] == "active:production:manufacturing"

    second = activate_v6_bundle(database, plan, idempotency_key="test-activate-1")
    assert second["activation_status"] == "already_active"
    assert second["active_pointer_write_operations"] == 0
    assert second["activation_audit_write_operations"] == 0

    conflicting = deepcopy(plan)
    conflicting["candidates"] = [
        item for item in conflicting["candidates"] if item["target_collection"] != DOMAIN_PACKAGE_COLLECTION
    ]
    different_package = compile_domain_package(_draft(), "manufacturing", "production", revision=2)
    different_record = make_bundle_document(different_package)
    database[DOMAIN_PACKAGE_COLLECTION].insert_one(deepcopy(different_record))
    conflicting["candidates"].append(
        {"target_collection": DOMAIN_PACKAGE_COLLECTION, "record": different_record}
    )
    with pytest.raises(RuntimeError, match="expected revision"):
        activate_v6_bundle(database, conflicting, idempotency_key="test-activate-2")
    replaced = activate_v6_bundle(
        database,
        conflicting,
        expected_active_revision=1,
        expected_active_bundle_sha256=first["active_bundle_sha256"],
        idempotency_key="test-activate-2",
    )
    assert replaced["activation_status"] == "activated"
    assert replaced["active_pointer_write_operations"] == 1
    assert replaced["active_revision"] == 2


def test_v5_migration_ids_are_domain_environment_and_source_bound() -> None:
    records = {
        "agent_v4_domain_items": [
            {
                "_id": "domain:analysis_recipes:rank_sales",
                "section": "analysis_recipes",
                "key": "rank_sales",
                "payload": {"display_name": "매출 순위", "aliases": ["상위 매출"]},
            }
        ],
        "agent_v4_table_catalog_items": [
            {
                "_id": "table_catalog:orders",
                "dataset_key": "orders",
                "payload": {
                    "display_name": "주문",
                    "source_config": {"source_type": "oracle"},
                    "filter_mappings": {"SALES_AMOUNT": "AMT"},
                },
            }
        ],
        "agent_v4_main_flow_filters": [
            {
                "_id": "main_flow_filter:DATE",
                "filter_key": "DATE",
                "payload": {
                    "display_name": "날짜",
                    "aliases": ["기준일"],
                    "operator": "eq",
                    "value_type": "LocalDate",
                    "value_shape": "scalar",
                },
            }
        ],
    }
    production = build_migration_plan(
        v5_records=records,
        domain_id="manufacturing",
        environment="production",
    )
    validation = build_migration_plan(
        v5_records=records,
        domain_id="manufacturing",
        environment="validation",
    )
    prod_v5 = [item for item in production["candidates"] if item.get("source_collection")]
    validation_v5 = [item for item in validation["candidates"] if item.get("source_collection")]
    assert len(prod_v5) == len(validation_v5) == 3
    assert {item["candidate_id"] for item in prod_v5}.isdisjoint(
        {item["candidate_id"] for item in validation_v5}
    )

    database = _FakeDatabase()
    first = apply_v6_candidates(database, production)
    second = apply_v6_candidates(database, validation)
    assert first["report"]["v6_mismatched_document_count"] == 0
    assert second["report"]["v6_mismatched_document_count"] == 0
    assert second["report"]["v6_missing_document_count"] == 0
    assert second["report"]["v6_verified_document_count"] == len(validation["candidates"])

    stored_migration_ids = {
        row["_id"]
        for collection in database.collections.values()
        for row in collection.rows
        if str(row.get("schema_version") or "") == "metadata.migration.record.v2"
    }
    assert len(stored_migration_ids) == 6
    assert any(":production:" in value for value in stored_migration_ids)
    assert any(":validation:" in value for value in stored_migration_ids)


def test_v5_migration_revision_creates_a_new_immutable_bundle_and_record_set() -> None:
    records = {
        "agent_v4_domain_items": [
            {
                "_id": "domain:analysis_recipes:rank_sales",
                "section": "analysis_recipes",
                "key": "rank_sales",
                "payload": {"display_name": "rank sales", "aliases": ["top sales"]},
            }
        ],
        "agent_v4_table_catalog_items": [],
        "agent_v4_main_flow_filters": [],
    }
    revision_1 = build_migration_plan(
        v5_records=records,
        domain_id="manufacturing",
        environment="validation",
        revision=1,
    )
    revision_2 = build_migration_plan(
        v5_records=records,
        domain_id="manufacturing",
        environment="validation",
        revision=2,
    )

    assert revision_1["revision"] == 1
    assert revision_2["revision"] == 2
    assert revision_1["bundle_sha256"] != revision_2["bundle_sha256"]
    revision_1_records = {
        item["record"]["_id"] for item in revision_1["candidates"] if item.get("source_collection")
    }
    revision_2_records = {
        item["record"]["_id"] for item in revision_2["candidates"] if item.get("source_collection")
    }
    assert revision_1_records.isdisjoint(revision_2_records)

    database = _FakeDatabase()
    first = apply_v6_candidates(database, revision_1)
    second = apply_v6_candidates(database, revision_2)
    assert first["report"]["v6_mismatched_document_count"] == 0
    assert second["report"]["v6_mismatched_document_count"] == 0


class _FakeCollection:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def find_one(self, query: dict) -> dict | None:
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return deepcopy(row)
        return None

    def insert_one(self, document: dict) -> None:
        if any(row.get("_id") == document.get("_id") for row in self.rows):
            raise DuplicateKeyError()
        self.rows.append(deepcopy(document))

    def replace_one(self, query: dict, document: dict, upsert: bool = False):
        for index, row in enumerate(self.rows):
            if all(row.get(key) == value for key, value in query.items()):
                modified = row != document
                self.rows[index] = deepcopy(document)
                return _WriteResult(1, int(modified))
        return _WriteResult(0, 0)


class _FakeDatabase:
    def __init__(self) -> None:
        self.collections: dict[str, _FakeCollection] = {}

    def __getitem__(self, name: str) -> _FakeCollection:
        return self.collections.setdefault(name, _FakeCollection())


class _WriteResult:
    def __init__(self, matched_count: int, modified_count: int) -> None:
        self.matched_count = matched_count
        self.modified_count = modified_count


class DuplicateKeyError(Exception):
    pass
