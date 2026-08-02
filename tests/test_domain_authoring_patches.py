from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from reference_runtime.canonical import ContractError
from reference_runtime.domain_authoring_patches import (
    apply_authoring_section_patch,
    runtime_catalog_v2_to_authoring_draft,
)
from reference_runtime.domain_packages import (
    adapt_legacy_catalog_v1,
    compile_domain_package,
)
from reference_runtime.metadata_compiler import build_runtime_catalog


ROOT = Path(__file__).resolve().parents[1]
ORDER_SALES_DRAFT = ROOT / "metadata" / "domain_packs" / "order_sales" / "authoring_draft.json"


def _order_sales_draft() -> dict:
    return json.loads(ORDER_SALES_DRAFT.read_text(encoding="utf-8"))


def test_runtime_catalog_round_trip_preserves_order_sales_catalog() -> None:
    package = compile_domain_package(_order_sales_draft(), "order_sales", "test", revision=3)
    reconstructed = runtime_catalog_v2_to_authoring_draft(package["runtime_catalog"])
    rebuilt = compile_domain_package(reconstructed, "order_sales", "test", revision=3)
    assert rebuilt["runtime_catalog"] == package["runtime_catalog"]


def test_runtime_catalog_round_trip_preserves_manufacturing_catalog() -> None:
    catalog_v1 = build_runtime_catalog(ROOT / "metadata" / "authoring")
    package = adapt_legacy_catalog_v1(
        catalog_v1,
        domain_id="manufacturing",
        environment="test",
        revision=2,
    )
    reconstructed = runtime_catalog_v2_to_authoring_draft(package["runtime_catalog"])
    rebuilt = compile_domain_package(reconstructed, "manufacturing", "test", revision=2)
    assert rebuilt["runtime_catalog"] == package["runtime_catalog"]


def test_dataset_patch_is_upsert_only_and_preserves_other_sections() -> None:
    base = _order_sales_draft()
    preserved = {
        key: deepcopy(base[key])
        for key in (
            "metrics",
            "relations",
            "recipes",
            "aliases",
            "prompt_extensions",
            "specialized_functions",
            "output_profile",
        )
    }
    patched = apply_authoring_section_patch(
        base,
        {
            "datasets": {
                "orders": {
                    "source_adapter": "dummy.orders.v2",
                    "fields": {"ORDER_ID": {"aliases": ["order number", "주문 식별자"]}},
                }
            }
        },
        "dataset",
    )
    assert patched["datasets"]["orders"]["source_adapter"] == "dummy.orders.v2"
    assert patched["datasets"]["orders"]["fields"]["ORDER_ID"]["physical_column"] == "order_id"
    assert patched["datasets"]["orders"]["fields"]["ORDER_ID"]["aliases"] == [
        "order number",
        "주문 식별자",
    ]
    for key, value in preserved.items():
        assert patched[key] == value
    compiled = compile_domain_package(patched, "order_sales", "test", revision=4)
    assert compiled["runtime_catalog"]["datasets"]["orders"]["source_adapter"] == "dummy.orders.v2"


def test_main_filter_patch_preserves_datasets_metrics_and_relations() -> None:
    base = _order_sales_draft()
    patched = apply_authoring_section_patch(
        base,
        {
            "aliases": {
                "field:CATEGORY": {
                    "target_type": "field",
                    "target_key": "CATEGORY",
                    "values": ["카테고리", "상품군", "분류"],
                }
            }
        },
        "main_filter",
    )
    assert patched["datasets"] == base["datasets"]
    assert patched["metrics"] == base["metrics"]
    assert patched["relations"] == base["relations"]
    assert patched["aliases"]["field:CATEGORY"]["values"][-1] == "분류"
    compiled = compile_domain_package(patched, "order_sales", "test", revision=4)
    assert compiled["runtime_catalog"]["aliases"]["field:CATEGORY"]["values"][-1] == "분류"


def test_domain_policy_patch_only_updates_owned_sections_and_upserts_functions() -> None:
    base = _order_sales_draft()
    preserved = {
        key: deepcopy(value)
        for key, value in base.items()
        if key
        not in {
            "prompt_extensions",
            "specialized_functions",
            "output_profile",
            "source_provenance",
        }
    }
    function = {
        "function_id": "sales.tax_annotation",
        "version": 1,
        "execution_mode": "registered_standalone",
        "implementation_sha256": "0" * 64,
        "input_schema": {},
        "output_schema": {},
        "required_fields": ["SALES_AMOUNT"],
    }
    patched = apply_authoring_section_patch(
        base,
        {
            "prompt_extensions": {
                "intent": "등록된 매출 후보만 선택한다.",
                "answer": "금액 단위를 반드시 표시한다.",
            },
            "specialized_functions": [function],
            "output_profile": {
                "field_labels": {"SALES_AMOUNT": "총 매출액"},
            },
        },
        "domain_policy",
    )

    for key, value in preserved.items():
        assert patched[key] == value
    assert patched["prompt_extensions"]["intent"] == "등록된 매출 후보만 선택한다."
    assert patched["prompt_extensions"]["answer"] == "금액 단위를 반드시 표시한다."
    assert patched["specialized_functions"] == [function]
    assert patched["output_profile"]["field_labels"]["SALES_AMOUNT"] == "총 매출액"
    assert patched["output_profile"]["field_labels"]["TARGET_AMOUNT"] == "목표금액"

    compiled = compile_domain_package(patched, "order_sales", "test", revision=4)
    assert compiled["runtime_catalog"]["specialized_functions"] == [function]
    assert compiled["runtime_catalog"]["prompt_extensions"]["answer"] == "금액 단위를 반드시 표시한다."


def test_domain_policy_patch_upserts_without_removing_existing_function_identity() -> None:
    base = _order_sales_draft()
    existing = {
        "function_id": "sales.existing",
        "version": 1,
        "execution_mode": "registered_standalone",
        "implementation_sha256": "1" * 64,
        "input_schema": {},
        "output_schema": {},
    }
    added = {
        "function_id": "sales.added",
        "version": 1,
        "execution_mode": "registered_standalone",
        "implementation_sha256": "2" * 64,
        "input_schema": {},
        "output_schema": {},
    }
    base["specialized_functions"] = [existing]
    patched = apply_authoring_section_patch(
        base,
        {"specialized_functions": [added]},
        "domain_policy",
    )
    assert patched["specialized_functions"] == [added, existing]


@pytest.mark.parametrize(
    ("patch", "kind"),
    [
        ({"metrics": {"SALES_AMOUNT": {"aggregation": "mean"}}}, "dataset"),
        ({"datasets": {"orders": {"source_adapter": "dummy.orders.v2"}}}, "main_filter"),
        ({"datasets": {"$delete": ["orders"]}}, "dataset"),
        ({"aliases": {}}, "main_filter"),
        ({"datasets": {"orders": {}}}, "domain_policy"),
        ({"specialized_functions": []}, "domain_policy"),
    ],
)
def test_section_patch_rejects_cross_owned_delete_and_empty_shapes(patch: dict, kind: str) -> None:
    with pytest.raises(ContractError):
        apply_authoring_section_patch(_order_sales_draft(), patch, kind)
