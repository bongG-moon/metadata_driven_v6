"""Compatibility loader and deterministic validator for metadata catalogs.

Manufacturing-specific definitions live in
``metadata/domain_packs/manufacturing/runtime_catalog.v1.json``.  This module
contains only domain-neutral hash, validation, provenance and record-projection
logic.  New domains use :mod:`reference_runtime.domain_packages` and
``metadata.runtime.catalog.v2``.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

from .canonical import ContractError, canonical_bytes, sha256_json


CATALOG_CONTRACT_VERSION = "metadata.runtime.catalog.v1"
COMPILER_VERSION = "metadata-compiler.v6.1"
CATALOG_TOP_LEVEL_KEYS = {
    "contract_version",
    "datasets",
    "fields",
    "metrics",
    "process_groups",
    "process_order",
    "product_groups",
    "recipes",
    "aliases",
    "catalog_sha256",
}
PRODUCT_GRAIN = ["TECH", "DEN", "MODE", "PKG_TYPE1", "PKG_TYPE2", "LEAD", "MCP_NO"]
MANUFACTURING_PACK_CATALOG = (
    Path(__file__).resolve().parents[1]
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "runtime_catalog.v1.json"
)


def build_runtime_catalog(authoring_root: str | Path | None = None) -> dict[str, Any]:
    """Load the frozen manufacturing v1 compatibility Domain Pack."""

    if authoring_root is not None:
        validate_authoring_sources(authoring_root)
    if not MANUFACTURING_PACK_CATALOG.is_file():
        raise ContractError(
            "metadata_dependency_error",
            "metadata_compile",
            "manufacturing Domain Pack runtime catalog가 없습니다.",
            {"path": str(MANUFACTURING_PACK_CATALOG)},
        )
    try:
        catalog = json.loads(MANUFACTURING_PACK_CATALOG.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_compile",
            "manufacturing Domain Pack을 읽을 수 없습니다.",
            {"path": str(MANUFACTURING_PACK_CATALOG)},
        ) from exc
    return deepcopy(validate_runtime_catalog(catalog))


def compute_catalog_sha256(catalog: dict[str, Any]) -> str:
    material = {key: value for key, value in catalog.items() if key != "catalog_sha256"}
    return sha256_json(material)


def validate_runtime_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(catalog, dict):
        raise ContractError("metadata_dependency_error", "metadata_compile", "runtime catalog가 object가 아닙니다.")
    actual_keys = set(catalog)
    if actual_keys != CATALOG_TOP_LEVEL_KEYS:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_compile",
            "runtime catalog top-level contract가 일치하지 않습니다.",
            {"missing": sorted(CATALOG_TOP_LEVEL_KEYS - actual_keys), "extra": sorted(actual_keys - CATALOG_TOP_LEVEL_KEYS)},
        )
    if catalog.get("contract_version") != CATALOG_CONTRACT_VERSION:
        raise ContractError("metadata_dependency_error", "metadata_compile", "runtime catalog version이 일치하지 않습니다.")
    expected_hash = compute_catalog_sha256(catalog)
    if catalog.get("catalog_sha256") != expected_hash:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_compile",
            "runtime catalog hash가 일치하지 않습니다.",
            {"expected": expected_hash, "actual": catalog.get("catalog_sha256")},
        )

    for collection_name in ["datasets", "fields", "metrics", "process_groups", "product_groups", "recipes", "aliases"]:
        if not isinstance(catalog.get(collection_name), dict) or not catalog[collection_name]:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                f"{collection_name} catalog이 비어 있습니다.",
            )
    if not isinstance(catalog.get("process_order"), list) or not catalog["process_order"]:
        raise ContractError("metadata_dependency_error", "metadata_compile", "process_order가 비어 있습니다.")

    fields = catalog["fields"]
    for key, dataset in catalog["datasets"].items():
        required_keys = {"key", "family", "source_type", "fields", "parameters", "default_detail_fields"}
        missing = required_keys - set(dataset)
        if missing or dataset.get("key") != key:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "dataset contract가 완전하지 않습니다.",
                {"dataset_key": key, "missing": sorted(missing)},
            )
        _validate_dataset_bindings(key, dataset, fields)

    sequences: set[int] = set()
    names: set[str] = set()
    for item in catalog["process_order"]:
        name = str(item.get("oper_name") or "")
        try:
            sequence = int(item.get("oper_seq"))
        except (TypeError, ValueError) as exc:
            raise ContractError("metadata_dependency_error", "metadata_compile", "OPER_SEQ가 numeric이 아닙니다.") from exc
        if not name or name in names or sequence in sequences:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "process_order identity/sequence가 중복됩니다.",
            )
        names.add(name)
        sequences.add(sequence)

    metric_fields = set(fields)
    families = {str(item.get("family")) for item in catalog["datasets"].values()}
    for metric_id, metric in catalog["metrics"].items():
        if metric.get("metric_id") != metric_id:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "metric identity가 일치하지 않습니다.",
                {"metric_id": metric_id},
            )
        binding = metric.get("source_binding")
        if isinstance(binding, dict):
            if binding.get("field") not in metric_fields or binding.get("dataset_family") not in families:
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_compile",
                    "metric source binding이 유효하지 않습니다.",
                    {"metric_id": metric_id},
                )
        additivity = metric.get("additivity")
        if (
            isinstance(additivity, dict)
            and additivity.get("default") == "non_additive"
            and "sum" in additivity.get("allowed_rollups", [])
        ):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "non-additive metric에 sum이 허용됐습니다.",
                {"metric_id": metric_id},
            )

    for group_type in ["process_groups", "product_groups"]:
        for key, group in catalog[group_type].items():
            if not group.get("aliases"):
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_compile",
                    "group alias가 비어 있습니다.",
                    {"group": key},
                )
    for key, recipe in catalog["recipes"].items():
        if recipe.get("recipe_id") != key or not isinstance(recipe.get("required_slots"), list):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "recipe contract가 완전하지 않습니다.",
                {"recipe": key},
            )
    return catalog


def _validate_dataset_bindings(dataset_key: str, dataset: dict[str, Any], fields: dict[str, Any]) -> None:
    bindings = dataset.get("fields")
    if not isinstance(bindings, dict) or not bindings:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_compile",
            "dataset field binding이 비어 있습니다.",
            {"dataset_key": dataset_key},
        )
    physical_owners: dict[str, str] = {}
    for canonical_field, binding in bindings.items():
        if canonical_field not in fields:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "미등록 canonical field입니다.",
                {"dataset_key": dataset_key, "field": canonical_field},
            )
        physical = str(binding.get("physical_column") or "")
        candidates = [physical, *[str(value) for value in binding.get("physical_aliases", [])]]
        if not physical or len(candidates) != len(set(candidates)):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "physical field binding이 모호합니다.",
                {"dataset_key": dataset_key, "field": canonical_field},
            )
        for candidate in candidates:
            owner = physical_owners.get(candidate)
            if owner and owner != canonical_field:
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_compile",
                    "physical field가 둘 이상 canonical field에 binding됐습니다.",
                    {"dataset_key": dataset_key, "physical_field": candidate, "fields": [owner, canonical_field]},
                )
            physical_owners[candidate] = canonical_field
    for field in dataset.get("default_detail_fields", []):
        if field not in bindings:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "default detail field binding이 없습니다.",
                {"dataset_key": dataset_key, "field": field},
            )


def validate_authoring_sources(authoring_root: str | Path) -> dict[str, dict[str, Any]]:
    root = Path(authoring_root)
    expected = {
        "domain": root / "domain" / "domain_knowledge.txt",
        "table_catalog": root / "table_catalog" / "data_catalog.txt",
        "main_filters": root / "main_filters" / "main_variable.txt",
    }
    # These markers validate the isolated manufacturing compatibility source.
    # New domain authoring uses metadata-authoring-draft.schema.json instead.
    markers = {
        "domain": ["W/BM", "analysis_recipes", "BOH"],
        "table_catalog": ["production_today", "hold_history", "filter_mappings"],
        "main_filters": ["DATE", "OPER_NAME", "MCP_NO"],
    }
    result: dict[str, dict[str, Any]] = {}
    for source_type, path in expected.items():
        if not path.is_file():
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "필수 자연어 metadata source가 없습니다.",
                {"source_type": source_type, "path": str(path)},
            )
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "metadata source는 UTF-8이어야 합니다.",
                {"source_type": source_type},
            ) from exc
        missing = [marker for marker in markers[source_type] if marker not in text]
        if missing:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_compile",
                "metadata source 필수 블록이 없습니다.",
                {"source_type": source_type, "missing_markers": missing},
            )
        result[source_type] = {
            "source_id": f"authoring:{source_type}:{hashlib.sha256(raw).hexdigest()}",
            "relative_path": path.relative_to(root.parent).as_posix(),
            "content_sha256": hashlib.sha256(raw).hexdigest(),
            "byte_count": len(raw),
        }
    return result


def source_provenance(authoring_root: str | Path) -> dict[str, dict[str, Any]]:
    return validate_authoring_sources(authoring_root)


def compiled_records(
    catalog: dict[str, Any],
    provenance: dict[str, dict[str, Any]],
    *,
    lifecycle_status: str = "active",
) -> list[dict[str, Any]]:
    """Project a validated catalog into immutable revisioned records."""

    validate_runtime_catalog(catalog)
    source_for_kind = {
        "dataset": "table_catalog",
        "field": "table_catalog",
        "metric": "domain",
        "process_group": "domain",
        "process_order": "domain",
        "product_group": "domain",
        "recipe": "domain",
        "alias": "main_filters",
    }
    groups: list[tuple[str, Iterable[tuple[str, Any]]]] = [
        ("dataset", catalog["datasets"].items()),
        ("field", catalog["fields"].items()),
        ("metric", catalog["metrics"].items()),
        ("process_group", catalog["process_groups"].items()),
        ("process_order", ((str(item["oper_name"]), item) for item in catalog["process_order"])),
        ("product_group", catalog["product_groups"].items()),
        ("recipe", catalog["recipes"].items()),
        ("alias", catalog["aliases"].items()),
    ]
    records: list[dict[str, Any]] = []
    for kind, items in groups:
        for key, contract in items:
            source_kind = source_for_kind[kind]
            if kind == "alias" and isinstance(contract, dict):
                source_kind = str(contract.get("provenance_source") or source_kind)
            source = provenance[source_kind]
            material = deepcopy(contract)
            contract_sha = sha256_json(material)
            records.append(
                {
                    "schema_version": "metadata.v6",
                    "kind": kind,
                    "identity": {"namespace": "metadata_v6", "key": str(key)},
                    "revision": 1,
                    "lifecycle": {"status": lifecycle_status},
                    "provenance": {
                        "source_id": source["source_id"],
                        "source_block": str(key),
                        "content_sha256": source["content_sha256"],
                        "compiler_version": COMPILER_VERSION,
                        "prompt_sha256": "not_applicable_deterministic_compile",
                        "model": "deterministic",
                        "source_type": "natural_language_txt",
                    },
                    "dependencies": [],
                    "contract": material,
                    "contract_sha256": contract_sha,
                    "validation": {
                        "schema": "passed",
                        "semantic_lint": "passed",
                        "dependency_closure": "passed",
                        "catalog_sha256": catalog["catalog_sha256"],
                    },
                }
            )
    return records


def load_runtime_catalog(path: str | Path) -> dict[str, Any]:
    catalog = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_runtime_catalog(catalog)


def write_runtime_catalog(path: str | Path, catalog: dict[str, Any]) -> Path:
    validate_runtime_catalog(catalog)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(canonical_bytes(catalog) + b"\n")
    return target


__all__ = [
    "CATALOG_CONTRACT_VERSION",
    "CATALOG_TOP_LEVEL_KEYS",
    "COMPILER_VERSION",
    "MANUFACTURING_PACK_CATALOG",
    "PRODUCT_GRAIN",
    "build_runtime_catalog",
    "compiled_records",
    "compute_catalog_sha256",
    "load_runtime_catalog",
    "source_provenance",
    "validate_authoring_sources",
    "validate_runtime_catalog",
    "write_runtime_catalog",
]
