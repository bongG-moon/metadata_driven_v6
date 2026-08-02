"""Domain-neutral metadata package compiler and Mongo runtime loader.

The LLM-facing authoring Flow produces only ``metadata.authoring.draft.v1``.
This module is the deterministic trust boundary: it validates the draft,
normalizes dataset/field contracts, seals a ``metadata.runtime.catalog.v2``,
and wraps it in one immutable ``domain.package.v1``.  Runtime code loads the
package through a small active pointer and never reparses the natural-language
source or trusts an LLM-produced hash.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping

from .canonical import ContractError, sha256_json
from .contracts import validate_contract


AUTHORING_DRAFT_VERSION = "metadata.authoring.draft.v1"
DOMAIN_PACKAGE_VERSION = "domain.package.v1"
RUNTIME_CATALOG_V2 = "metadata.runtime.catalog.v2"
ACTIVE_POINTER_VERSION = "metadata.active-domain-pointer.v1"
DOMAIN_COMPILER_VERSION = "metadata-domain-compiler.v6.3"

DOMAIN_PACKAGE_COLLECTION = "agent_v6_metadata_bundles"
ACTIVE_POINTER_COLLECTION = "agent_v6_metadata_active"
MIGRATION_QUARANTINE_COLLECTION = "agent_v6_migration_quarantine"

DOMAIN_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
ENVIRONMENT_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,31}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

ALLOWED_FIELD_ROLES = {
    "filter",
    "group",
    "join",
    "compare",
    "aggregate",
    "derive",
    "project",
    "sort",
    "rank",
    "metric",
    "output",
}
ALLOWED_SOURCE_TYPES = {
    "oracle",
    "sql",
    "mongodb",
    "http",
    "datalake",
    "goodocs",
    "file",
    "dummy",
    "previous_result",
}
ALLOWED_OPERATIONS = {
    "filter",
    "ordered_range",
    "product_token_match",
    "project",
    "derive",
    "aggregate",
    "compare_fields",
    "compare_group_attributes",
    "find_duplicate_groups",
    "join",
    "presence_filter",
    "sort",
    "rank",
    "concat_segments",
    "transform_previous_result",
}
GENERIC_V2_OPERATIONS = {
    "filter",
    "project",
    "aggregate",
    "join",
    "derive",
    "compare_fields",
    "sort",
    "rank",
    "transform_previous_result",
}
FILTER_OPERATORS = {
    "is_null",
    "is_not_null",
    "is_blank",
    "is_not_blank",
    "null_or_blank",
    "in",
    "not_in",
    "between",
    "contains",
    "starts_with",
    "ends_with",
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
}
FORMULA_OPERATORS = {
    "add",
    "subtract",
    "multiply",
    "safe_divide",
    "coalesce",
    "coalesce_blank",
    "abs",
    "round",
    "min_pair",
    "max_pair",
}
LEGACY_FORMULA_OPERATORS = FORMULA_OPERATORS | {"datetime_diff_hours"}
FORMULA_ARITY = {
    "add": 2,
    "subtract": 2,
    "multiply": 2,
    "safe_divide": 2,
    "coalesce": 2,
    "coalesce_blank": 2,
    "abs": 1,
    "round": 1,
    "min_pair": 2,
    "max_pair": 2,
    "datetime_diff_hours": 2,
}
SAFE_DIVIDE_ZERO_POLICIES = {"null", "zero", "error"}
FORMULA_RUNTIME_REFS = {"reference_instant"}
NUMERIC_SEMANTIC_TYPES = {
    "number",
    "integer",
    "quantity",
    "currency",
    "rate",
    "percent",
    "percentage",
    "duration",
    "hour",
}
TEXTUAL_SEMANTIC_TYPES = {"string", "identifier", "year_month"}
NUMERIC_ROLLUPS = {"sum", "mean", "min", "max", "median", "std", "var"}
DISTINCT_ROLLUPS = {"count", "nunique", "list_unique"}
GENERIC_REQUIRED_SLOTS = {
    "date_scope",
    "rank_direction",
    "rank_limit",
    "project_fields",
    "request_scope",
    "analysis_kind",
    "metric_refs",
    "dimension_refs",
    "field_refs",
    "dataset_refs",
    "relation_refs",
    "recipe_refs",
    "formula_refs",
    "grain_refs",
    "entity_group_refs",
    "filter_refs",
    "thresholds",
    "date",
    "reference_date",
    "reference_instant",
    "rank",
    "sort",
    "followup",
    "followup_mode",
    "comparison_operator",
}
FORBIDDEN_EXECUTABLE_KEYS = {
    "code",
    "python",
    "python_code",
    "pandas_code",
    "script",
    "eval",
    "exec",
    "callable",
    "lambda",
    "sql",
    "query_template",
    "endpoint_url",
}
SECRET_KEY_PARTS = {
    "password",
    "passwd",
    "token",
    "secret",
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "private_key",
    "connection_string",
    "mongo_uri",
}
ALLOWED_NON_SECRET_TOKEN_KEYS = {
    # Closed registered-function schemas use ``tokens`` for bounded business
    # values to match.  The values are still scanned recursively for secret
    # scalar patterns, while every credential-bearing token key remains
    # fail-closed through the substring check below.
    "tokens",
}
IDENTITY_CONTAINER_KEYS = {
    "datasets",
    "fields",
    "metrics",
    "entity_groups",
    "grains",
    "relations",
    "orderings",
    "predicates",
    "recipes",
    "aliases",
}
SECRET_SCALAR_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
    ("openai_style_key", re.compile(r"\bsk-[0-9A-Za-z_-]{16,}\b")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.I)),
    ("credentialed_uri", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]+@", re.I)),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~-]{16,}", re.I)),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")),
    (
        "named_secret_assignment",
        re.compile(
            r"\b(?:password|passwd|pwd|api[_ -]?key|secret|access[_ -]?token)\s*[:=]\s*"
            r"(?!<[^>]+>|\$\{[^}]+\}|\*{3,}|x{3,}|redacted\b)[^\s,;]{6,}",
            re.I,
        ),
    ),
)


def compile_domain_package(
    authoring_payload: Mapping[str, Any],
    domain_id: str,
    environment: str,
    *,
    revision: int = 1,
    lifecycle_status: str = "validated",
) -> dict[str, Any]:
    """Compile an LLM draft to one immutable domain package.

    The function deliberately accepts a JSON-like mapping instead of raw text.
    Natural-language conversion belongs to the authoring LLM component; this
    function is the model-independent validator/compiler that follows it.
    """

    normalized_domain = _identity(domain_id, "domain_id", DOMAIN_ID_PATTERN)
    normalized_environment = _identity(environment, "environment", ENVIRONMENT_PATTERN)
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        _fail("revision은 1 이상의 정수여야 합니다.", {"revision": revision})
    if lifecycle_status not in {"draft", "validated", "active", "deprecated", "quarantined"}:
        _fail("지원하지 않는 domain package lifecycle입니다.", {"lifecycle_status": lifecycle_status})

    draft = deepcopy(dict(authoring_payload))
    validate_contract(
        draft,
        "metadata-authoring-draft.schema.json",
        stage="metadata_authoring_compile",
        error_code="metadata_dependency_error",
    )
    _reject_executable_or_secret_payload(draft)

    catalog = _catalog_from_draft(
        draft,
        domain_id=normalized_domain,
        environment=normalized_environment,
        revision=revision,
    )
    authoring_sha256 = sha256_json(draft)
    package: dict[str, Any] = {
        "contract_version": DOMAIN_PACKAGE_VERSION,
        "domain_id": normalized_domain,
        "environment": normalized_environment,
        "revision": revision,
        "lifecycle": {"status": lifecycle_status},
        "compiler_version": DOMAIN_COMPILER_VERSION,
        "authoring_sha256": authoring_sha256,
        "runtime_catalog": catalog,
        "package_sha256": "",
        "bundle_sha256": "",
    }
    package["package_sha256"] = compute_package_sha256(package)
    package["bundle_sha256"] = compute_bundle_sha256(package)
    return validate_domain_package(package)


def build_runtime_catalog_v2(package: Mapping[str, Any]) -> dict[str, Any]:
    """Return the sealed v2 runtime catalog from a validated domain package."""

    validated = validate_domain_package(deepcopy(dict(package)))
    return deepcopy(validated["runtime_catalog"])


def validate_runtime_catalog_v2(catalog: Mapping[str, Any]) -> dict[str, Any]:
    value = deepcopy(dict(catalog))
    validate_contract(
        value,
        "runtime-catalog-v2.schema.json",
        stage="metadata_catalog_v2_validation",
        error_code="metadata_dependency_error",
    )
    expected = compute_runtime_catalog_v2_sha256(value)
    if value.get("catalog_sha256") != expected:
        _fail(
            "runtime catalog v2 hash가 일치하지 않습니다.",
            {"expected": expected, "actual": value.get("catalog_sha256")},
        )
    _identity(str(value["domain_id"]), "domain_id", DOMAIN_ID_PATTERN)
    _identity(str(value["environment"]), "environment", ENVIRONMENT_PATTERN)
    _validate_catalog_semantics(value)
    return value


def validate_domain_package(package: Mapping[str, Any]) -> dict[str, Any]:
    value = deepcopy(dict(package))
    validate_contract(
        value,
        "domain-package.schema.json",
        stage="domain_package_validation",
        error_code="metadata_dependency_error",
    )
    catalog = validate_runtime_catalog_v2(value["runtime_catalog"])
    if (
        catalog["domain_id"] != value["domain_id"]
        or catalog["environment"] != value["environment"]
        or catalog["revision"] != value["revision"]
    ):
        _fail("domain package와 runtime catalog identity가 일치하지 않습니다.")
    expected_package = compute_package_sha256(value)
    expected_bundle = compute_bundle_sha256(value)
    if value.get("package_sha256") != expected_package:
        _fail("domain package hash가 일치하지 않습니다.", {"expected": expected_package})
    if value.get("bundle_sha256") != expected_bundle:
        _fail("domain bundle hash가 일치하지 않습니다.", {"expected": expected_bundle})
    return value


def compute_runtime_catalog_v2_sha256(catalog: Mapping[str, Any]) -> str:
    material = {key: deepcopy(value) for key, value in catalog.items() if key != "catalog_sha256"}
    return sha256_json(material)


def compute_package_sha256(package: Mapping[str, Any]) -> str:
    material = {
        key: deepcopy(value)
        for key, value in package.items()
        if key not in {"package_sha256", "bundle_sha256"}
    }
    return sha256_json(material)


def compute_bundle_sha256(package: Mapping[str, Any]) -> str:
    """Seal the exact runtime selector projection, not mutable Mongo fields."""

    material = {
        "contract_version": "metadata.domain-bundle.v1",
        "domain_id": package.get("domain_id"),
        "environment": package.get("environment"),
        "revision": package.get("revision"),
        "package_sha256": package.get("package_sha256"),
        "catalog_sha256": dict(package.get("runtime_catalog") or {}).get("catalog_sha256"),
        "compiler_version": package.get("compiler_version"),
    }
    return sha256_json(material)


def make_bundle_document(package: Mapping[str, Any]) -> dict[str, Any]:
    """Create the immutable Mongo document written by the approval executor."""

    value = validate_domain_package(package)
    return {
        "_id": f"bundle:{value['bundle_sha256']}",
        **deepcopy(value),
    }


def make_active_pointer(package: Mapping[str, Any]) -> dict[str, Any]:
    """Create the small CAS-managed active selector for a validated package."""

    value = validate_domain_package(package)
    if value["lifecycle"]["status"] not in {"validated", "active"}:
        _fail("validated 또는 active package만 active pointer 후보가 될 수 있습니다.")
    pointer = {
        "contract_version": ACTIVE_POINTER_VERSION,
        "domain_id": value["domain_id"],
        "environment": value["environment"],
        "revision": value["revision"],
        "bundle_sha256": value["bundle_sha256"],
        "package_sha256": value["package_sha256"],
        "status": "active",
    }
    validate_contract(
        pointer,
        "active-domain-pointer.schema.json",
        stage="active_domain_pointer_validation",
        error_code="metadata_dependency_error",
    )
    return pointer


def make_active_pointer_document(package: Mapping[str, Any]) -> dict[str, Any]:
    """Return the Mongo representation keyed by environment and domain."""

    pointer = make_active_pointer(package)
    return {
        "_id": f"active:{pointer['environment']}:{pointer['domain_id']}",
        **pointer,
    }


def load_active_domain_bundle(
    database: Any,
    domain_id: str,
    environment: str,
    *,
    active_collection: str = ACTIVE_POINTER_COLLECTION,
    bundle_collection: str = DOMAIN_PACKAGE_COLLECTION,
) -> dict[str, Any]:
    """Load and revalidate one active package using an exact hash-bound pointer."""

    normalized_domain = _identity(domain_id, "domain_id", DOMAIN_ID_PATTERN)
    normalized_environment = _identity(environment, "environment", ENVIRONMENT_PATTERN)
    _assert_v6_collection(active_collection, ACTIVE_POINTER_COLLECTION)
    _assert_v6_collection(bundle_collection, DOMAIN_PACKAGE_COLLECTION)
    pointer = _find_one(
        database[active_collection],
        {
            "_id": f"active:{normalized_environment}:{normalized_domain}",
            "status": "active",
        },
    )
    if not pointer:
        _fail(
            "활성 domain pointer를 찾을 수 없습니다.",
            {"domain_id": normalized_domain, "environment": normalized_environment},
        )
    pointer_material = {key: pointer.get(key) for key in (
        "contract_version",
        "domain_id",
        "environment",
        "revision",
        "bundle_sha256",
        "package_sha256",
        "status",
    )}
    validate_contract(
        pointer_material,
        "active-domain-pointer.schema.json",
        stage="active_domain_pointer_validation",
        error_code="metadata_dependency_error",
    )
    if (
        pointer_material["domain_id"] != normalized_domain
        or pointer_material["environment"] != normalized_environment
    ):
        _fail(
            "active pointer identity does not match the requested domain and environment.",
            {
                "requested_domain_id": normalized_domain,
                "requested_environment": normalized_environment,
                "pointer_domain_id": pointer_material["domain_id"],
                "pointer_environment": pointer_material["environment"],
            },
        )
    bundle = _find_one(database[bundle_collection], {"_id": f"bundle:{pointer['bundle_sha256']}"})
    if not bundle:
        _fail("active pointer가 가리키는 immutable bundle이 없습니다.")
    package = {key: deepcopy(value) for key, value in bundle.items() if key != "_id"}
    validated = validate_domain_package(package)
    if (
        validated["bundle_sha256"] != pointer["bundle_sha256"]
        or validated["package_sha256"] != pointer["package_sha256"]
        or validated["revision"] != pointer["revision"]
        or validated["domain_id"] != normalized_domain
        or validated["environment"] != normalized_environment
    ):
        _fail("active pointer와 domain bundle pin이 일치하지 않습니다.")
    if validated["lifecycle"]["status"] not in {"validated", "active"}:
        _fail("runtime에서 사용할 수 없는 domain bundle lifecycle입니다.")
    return validated


def adapt_legacy_catalog_v1(
    catalog_v1: Mapping[str, Any],
    *,
    domain_id: str = "manufacturing",
    environment: str = "default",
    revision: int = 1,
    display_name: str = "Manufacturing Analysis",
    prompt_extensions: Mapping[str, Any] | None = None,
    specialized_functions: Iterable[Mapping[str, Any]] = (),
    output_profile: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Adapt the frozen manufacturing v1 fixture through the generic v2 contract."""

    datasets = deepcopy(dict(catalog_v1.get("datasets") or {}))
    legacy_output_profile = deepcopy(dict(output_profile or {}))
    legacy_output_profile.setdefault("planner_profile", "legacy_v1_compat")
    legacy_output_profile.setdefault(
        "legacy_catalog_sha256", str(catalog_v1.get("catalog_sha256") or "")
    )
    draft = {
        "contract_version": AUTHORING_DRAFT_VERSION,
        "display_name": display_name,
        "description": "Legacy manufacturing catalog isolated as a versioned domain pack.",
        "locale": "ko-KR",
        "timezone": "Asia/Seoul",
        "datasets": datasets,
        "metrics": deepcopy(dict(catalog_v1.get("metrics") or {})),
        "entity_groups": deepcopy(dict(catalog_v1.get("process_groups") or {})),
        "grains": {
            "product": {
                "keys": deepcopy(list(catalog_v1.get("recipes", {}).get("product.standard", {}).get("grain", {}).get("keys") or []))
            }
        },
        "relations": {},
        "orderings": {"process": {"items": deepcopy(list(catalog_v1.get("process_order") or []))}},
        "predicates": deepcopy(dict(catalog_v1.get("product_groups") or {})),
        "recipes": deepcopy(dict(catalog_v1.get("recipes") or {})),
        "aliases": deepcopy(dict(catalog_v1.get("aliases") or {})),
        "prompt_extensions": deepcopy(dict(prompt_extensions or {"intent": "", "answer": ""})),
        "specialized_functions": [deepcopy(dict(item)) for item in specialized_functions],
        "output_profile": legacy_output_profile,
        "source_provenance": {"legacy_catalog_sha256": str(catalog_v1.get("catalog_sha256") or "")},
    }
    # v1 fields do not carry authoring aliases separately; every other binding
    # key is already accepted by the closed v1/v2 common field contract.
    for dataset in draft["datasets"].values():
        dataset.pop("key", None)
        if dataset.get("source_type") == "fixture":
            dataset["source_type"] = "dummy"
            dataset["fixture_only"] = True
        dataset.setdefault("source_adapter", str(dataset.get("source_type") or ""))
        if "date_filter_contract" in dataset and "date_policy" not in dataset:
            dataset["date_policy"] = deepcopy(dataset["date_filter_contract"])
        for binding in dict(dataset.get("fields") or {}).values():
            binding.setdefault("aliases", [])
    draft["recipes"] = _map_legacy_recipe_ops(draft["recipes"])
    return compile_domain_package(
        draft,
        domain_id,
        environment,
        revision=revision,
        lifecycle_status="validated",
    )


def _catalog_from_draft(
    draft: Mapping[str, Any],
    *,
    domain_id: str,
    environment: str,
    revision: int,
) -> dict[str, Any]:
    datasets: dict[str, Any] = {}
    fields: dict[str, Any] = {}
    for dataset_key in sorted(draft["datasets"]):
        raw = deepcopy(dict(draft["datasets"][dataset_key]))
        raw["key"] = dataset_key
        raw.setdefault("display_name", dataset_key)
        raw.setdefault("time_scope", "unspecified")
        raw.setdefault("source_adapter", str(raw.get("source_type") or ""))
        raw.setdefault("config_ref", "")
        raw.setdefault("query_ref", "")
        raw.setdefault("parameters", {})
        raw.setdefault("date_policy", {})
        raw.setdefault("default_detail_fields", [])
        raw.setdefault("read_policy", {"read_only": True, "timeout_seconds": 30, "max_rows": 50000})
        policy = dict(raw["read_policy"])
        policy.setdefault("read_only", True)
        policy.setdefault("timeout_seconds", 30)
        policy.setdefault("max_rows", 50000)
        raw["read_policy"] = policy
        normalized_bindings: dict[str, Any] = {}
        for canonical_field in sorted(raw["fields"]):
            binding = deepcopy(dict(raw["fields"][canonical_field]))
            binding.setdefault("physical_aliases", [])
            binding.setdefault("aliases", [])
            binding.setdefault("required_in_source", False)
            binding.setdefault("nullable", True)
            binding.setdefault("coercion", _default_coercion(str(binding["semantic_type"])))
            normalized_bindings[canonical_field] = binding
            field_card = fields.setdefault(
                canonical_field,
                {
                    "canonical_field": canonical_field,
                    "semantic_type": binding["semantic_type"],
                    "aliases": [],
                    "dataset_keys": [],
                    "roles": [],
                },
            )
            if str(field_card["semantic_type"]).casefold() != str(binding["semantic_type"]).casefold():
                _fail(
                    "같은 canonical field의 semantic_type이 dataset마다 다릅니다.",
                    {"field": canonical_field, "dataset_key": dataset_key},
                )
            field_card["dataset_keys"].append(dataset_key)
            field_card["aliases"] = sorted(set(field_card["aliases"]) | set(binding.get("aliases", [])))
            field_card["roles"] = sorted(set(field_card["roles"]) | set(binding["roles"]))
        raw["fields"] = normalized_bindings
        datasets[dataset_key] = raw

    catalog: dict[str, Any] = {
        "contract_version": RUNTIME_CATALOG_V2,
        "domain_id": domain_id,
        "environment": environment,
        "revision": revision,
        "compiler_version": DOMAIN_COMPILER_VERSION,
        "display_name": str(draft["display_name"]),
        "description": str(draft.get("description") or ""),
        "locale": str(draft.get("locale") or "ko-KR"),
        "timezone": str(draft.get("timezone") or "Asia/Seoul"),
        "datasets": datasets,
        "fields": dict(sorted(fields.items())),
        "metrics": _identity_cards(draft.get("metrics"), "metric_id"),
        "entity_groups": _identity_cards(draft.get("entity_groups"), "group_id"),
        "grains": _identity_cards(draft.get("grains"), "grain_id"),
        "relations": _identity_cards(draft.get("relations"), "relation_id"),
        "orderings": _identity_cards(draft.get("orderings"), "ordering_id"),
        "predicates": _identity_cards(draft.get("predicates"), "predicate_id"),
        "recipes": _identity_cards(draft.get("recipes"), "recipe_id"),
        "aliases": dict(sorted(deepcopy(dict(draft.get("aliases") or {})).items())),
        "prompt_extensions": {
            "intent": str(dict(draft.get("prompt_extensions") or {}).get("intent") or ""),
            "answer": str(dict(draft.get("prompt_extensions") or {}).get("answer") or ""),
        },
        "specialized_functions": sorted(
            [deepcopy(dict(item)) for item in draft.get("specialized_functions") or []],
            key=lambda item: (str(item.get("function_id")), int(item.get("version") or 0)),
        ),
        "output_profile": deepcopy(dict(draft.get("output_profile") or {})),
        "catalog_sha256": "",
    }
    catalog["catalog_sha256"] = compute_runtime_catalog_v2_sha256(catalog)
    return validate_runtime_catalog_v2(catalog)


def _validate_catalog_shape_compatibility(catalog: Mapping[str, Any]) -> None:
    fields = dict(catalog["fields"])
    physical_owners_by_dataset: dict[str, dict[str, str]] = {}
    for dataset_key, raw_dataset in dict(catalog["datasets"]).items():
        dataset = dict(raw_dataset)
        if dataset.get("key") != dataset_key:
            _fail("dataset key가 object identity와 일치하지 않습니다.", {"dataset_key": dataset_key})
        if dataset.get("source_type") not in ALLOWED_SOURCE_TYPES:
            _fail("지원하지 않는 source_type입니다.", {"dataset_key": dataset_key})
        if dict(dataset.get("read_policy") or {}).get("read_only") is not True:
            _fail("dataset read policy는 read_only여야 합니다.", {"dataset_key": dataset_key})
        bindings = dict(dataset.get("fields") or {})
        if not bindings:
            _fail("dataset field binding이 비어 있습니다.", {"dataset_key": dataset_key})
        owners: dict[str, str] = {}
        for canonical_field, raw_binding in bindings.items():
            binding = dict(raw_binding)
            if canonical_field not in fields:
                _fail("top-level field card가 없습니다.", {"dataset_key": dataset_key, "field": canonical_field})
            roles = set(binding.get("roles") or [])
            if not roles or not roles <= ALLOWED_FIELD_ROLES:
                _fail("field role이 비어 있거나 허용 범위를 벗어났습니다.", {"field": canonical_field})
            physicals = [str(binding.get("physical_column") or ""), *map(str, binding.get("physical_aliases") or [])]
            if not physicals[0] or len(physicals) != len(set(physicals)):
                _fail("physical field binding이 비어 있거나 중복됩니다.", {"field": canonical_field})
            for physical in physicals:
                owner = owners.get(physical)
                if owner and owner != canonical_field:
                    _fail(
                        "한 physical field가 둘 이상의 canonical field에 연결됐습니다.",
                        {"dataset_key": dataset_key, "physical_field": physical, "owners": [owner, canonical_field]},
                    )
                owners[physical] = canonical_field
        if not set(dataset.get("default_detail_fields") or []) <= set(bindings):
            _fail("default detail field가 dataset binding에 없습니다.", {"dataset_key": dataset_key})
        physical_owners_by_dataset[dataset_key] = owners

    families = {str(item.get("family")) for item in catalog["datasets"].values()}
    for metric_id, raw_metric in dict(catalog["metrics"]).items():
        metric = dict(raw_metric)
        binding = metric.get("source_binding")
        if isinstance(binding, dict):
            if binding.get("field") not in fields or binding.get("dataset_family") not in families:
                _fail("metric source binding이 닫힌 catalog를 참조하지 않습니다.", {"metric_id": metric_id})
        additivity = metric.get("additivity")
        if isinstance(additivity, dict) and additivity.get("default") == "non_additive":
            if "sum" in (additivity.get("allowed_rollups") or []):
                _fail("non-additive metric에 sum을 허용할 수 없습니다.", {"metric_id": metric_id})

    for relation_id, raw_relation in dict(catalog.get("relations") or {}).items():
        relation = dict(raw_relation)
        left = str(relation.get("left_dataset") or "")
        right = str(relation.get("right_dataset") or "")
        if left not in catalog["datasets"] or right not in catalog["datasets"]:
            _fail("relation dataset dependency가 닫혀 있지 않습니다.", {"relation_id": relation_id})
        left_keys = list(relation.get("left_keys") or [])
        right_keys = list(relation.get("right_keys") or [])
        if not left_keys or len(left_keys) != len(right_keys):
            _fail("relation join key cardinality가 올바르지 않습니다.", {"relation_id": relation_id})
        if not set(left_keys) <= set(catalog["datasets"][left]["fields"]):
            _fail("relation left key binding이 없습니다.", {"relation_id": relation_id})
        if not set(right_keys) <= set(catalog["datasets"][right]["fields"]):
            _fail("relation right key binding이 없습니다.", {"relation_id": relation_id})
        if relation.get("join_type") not in {"inner", "left", "right", "outer", "semi", "anti"}:
            _fail("relation join_type이 허용되지 않습니다.", {"relation_id": relation_id})
        if relation.get("cardinality") not in {"one_to_zero_or_one", "one_to_one", "one_to_many", "many_to_one", "many_to_many"}:
            _fail("relation cardinality가 명시되지 않았습니다.", {"relation_id": relation_id})

    for recipe_id, raw_recipe in dict(catalog["recipes"]).items():
        for operation in _recipe_operations(raw_recipe):
            if operation not in ALLOWED_OPERATIONS:
                _fail("등록되지 않은 typed operation이 recipe에 포함됐습니다.", {"recipe_id": recipe_id, "op": operation})

    seen_functions: set[tuple[str, int]] = set()
    for function in catalog.get("specialized_functions") or []:
        marker = (str(function["function_id"]), int(function["version"]))
        if marker in seen_functions:
            _fail("specialized function identity가 중복됩니다.", {"function_id": marker[0]})
        seen_functions.add(marker)
        if function.get("execution_mode") != "registered_standalone" or not SHA256_PATTERN.fullmatch(
            str(function.get("implementation_sha256") or "")
        ):
            _fail("specialized function은 hash-pinned registered standalone이어야 합니다.")


def _validate_catalog_semantics(catalog: Mapping[str, Any]) -> None:
    """Validate the executable closure of one sealed runtime catalog.

    JSON Schema checks shape.  This pass checks that every executable reference
    resolves to a compatible registered object before the package can be
    activated.  It intentionally distinguishes generic v2 metadata from the
    explicitly hash-pinned legacy manufacturing compatibility profile.
    """

    profile = _catalog_planner_profile(catalog)
    fields = dict(catalog["fields"])
    datasets = dict(catalog["datasets"])
    family_datasets: dict[str, list[str]] = {}

    for dataset_key, raw_dataset in datasets.items():
        dataset = dict(raw_dataset)
        if dataset.get("key") != dataset_key:
            _fail("Dataset key does not match object identity.", {"dataset_key": dataset_key})
        if dataset.get("source_type") not in ALLOWED_SOURCE_TYPES:
            _fail("Unsupported dataset source type.", {"dataset_key": dataset_key})
        if dict(dataset.get("read_policy") or {}).get("read_only") is not True:
            _fail("Dataset read policy must be read-only.", {"dataset_key": dataset_key})
        family = str(dataset.get("family") or "").strip()
        if not family:
            _fail("Dataset family is required.", {"dataset_key": dataset_key})
        family_datasets.setdefault(family, []).append(dataset_key)
        bindings = dict(dataset.get("fields") or {})
        if not bindings:
            _fail("Dataset field bindings cannot be empty.", {"dataset_key": dataset_key})
        owners: dict[str, str] = {}
        for canonical_field, raw_binding in bindings.items():
            binding = dict(raw_binding)
            field_card = dict(fields.get(canonical_field) or {})
            if not field_card:
                _fail("Top-level field card is missing.", {"dataset_key": dataset_key, "field": canonical_field})
            if dataset_key not in set(field_card.get("dataset_keys") or []):
                _fail("Field card does not include its dataset owner.", {"dataset_key": dataset_key, "field": canonical_field})
            if not _semantic_types_compatible(field_card.get("semantic_type"), binding.get("semantic_type")):
                _fail("Field semantic types are incompatible.", {"dataset_key": dataset_key, "field": canonical_field})
            roles = set(binding.get("roles") or [])
            if not roles or not roles <= ALLOWED_FIELD_ROLES:
                _fail("Field roles are empty or unsupported.", {"dataset_key": dataset_key, "field": canonical_field})
            if not roles <= set(field_card.get("roles") or []):
                _fail("Field card roles do not cover dataset roles.", {"dataset_key": dataset_key, "field": canonical_field})
            filter_operators = set(binding.get("allowed_filter_operators") or [])
            if not filter_operators <= FILTER_OPERATORS or (filter_operators and "filter" not in roles):
                _fail("Field filter operator contract is invalid.", {"dataset_key": dataset_key, "field": canonical_field})
            physicals = [str(binding.get("physical_column") or ""), *map(str, binding.get("physical_aliases") or [])]
            if not physicals[0] or len(physicals) != len(set(physicals)):
                _fail("Physical field binding is empty or duplicated.", {"dataset_key": dataset_key, "field": canonical_field})
            for physical in physicals:
                owner = owners.get(physical)
                if owner and owner != canonical_field:
                    _fail("One physical field maps to multiple canonical fields.", {"dataset_key": dataset_key, "physical_field": physical})
                owners[physical] = canonical_field
        if not set(dataset.get("default_detail_fields") or []) <= set(bindings):
            _fail("Default detail field is not bound by the dataset.", {"dataset_key": dataset_key})
        date_field = str(dict(dataset.get("date_policy") or {}).get("field") or "")
        if date_field and (
            date_field not in bindings
            or "filter" not in set(bindings[date_field].get("roles") or [])
        ):
            _fail("Dataset date policy field must be a filterable bound field.", {"dataset_key": dataset_key, "field": date_field})

    _validate_grains_and_orderings(catalog, profile)
    _validate_relations(catalog)
    _validate_metrics(catalog, family_datasets, profile)
    _validate_predicates_and_groups(catalog, profile)
    _validate_recipes(catalog, profile)
    _validate_aliases(catalog, profile)
    _validate_specialized_functions(catalog)


def _catalog_planner_profile(catalog: Mapping[str, Any]) -> str:
    output_profile = dict(catalog.get("output_profile") or {})
    profile = str(output_profile.get("planner_profile") or "generic_v2")
    if profile == "generic_v2":
        return profile
    if profile == "legacy_v1_compat":
        if not SHA256_PATTERN.fullmatch(str(output_profile.get("legacy_catalog_sha256") or "")):
            _fail("Legacy planner profile requires an exact catalog hash pin.")
        return profile
    _fail("Unsupported planner profile.", {"planner_profile": profile})
    raise AssertionError("unreachable")


def _validate_relations(catalog: Mapping[str, Any]) -> None:
    datasets = dict(catalog["datasets"])
    for relation_id, raw_relation in dict(catalog.get("relations") or {}).items():
        relation = dict(raw_relation)
        left = str(relation.get("left_dataset") or "")
        right = str(relation.get("right_dataset") or "")
        if left not in datasets or right not in datasets:
            _fail("Relation dataset dependency is missing.", {"relation_id": relation_id})
        left_keys = list(relation.get("left_keys") or [])
        right_keys = list(relation.get("right_keys") or [])
        if not left_keys or len(left_keys) != len(right_keys):
            _fail("Relation join-key cardinality is invalid.", {"relation_id": relation_id})
        left_fields = dict(datasets.get(left, {}).get("fields") or {})
        right_fields = dict(datasets.get(right, {}).get("fields") or {})
        for left_key, right_key in zip(left_keys, right_keys):
            if left_key not in left_fields or right_key not in right_fields:
                _fail("Relation join-key binding is missing.", {"relation_id": relation_id})
            if "join" not in set(left_fields[left_key].get("roles") or []) or "join" not in set(right_fields[right_key].get("roles") or []):
                _fail("Relation keys must carry the join role.", {"relation_id": relation_id})
            if not _semantic_types_compatible(left_fields[left_key].get("semantic_type"), right_fields[right_key].get("semantic_type")):
                _fail("Relation key semantic types are incompatible.", {"relation_id": relation_id})
        if relation.get("join_type") not in {"inner", "left", "right", "outer", "semi", "anti"}:
            _fail("Relation join type is unsupported.", {"relation_id": relation_id})
        if relation.get("cardinality") not in {"one_to_zero_or_one", "one_to_one", "one_to_many", "many_to_one", "many_to_many"}:
            _fail("Relation cardinality is invalid.", {"relation_id": relation_id})


def _validate_metrics(
    catalog: Mapping[str, Any], family_datasets: Mapping[str, list[str]], profile: str
) -> None:
    metrics = dict(catalog.get("metrics") or {})
    datasets = dict(catalog["datasets"])
    dependency_graph: dict[str, set[str]] = {metric_id: set() for metric_id in metrics}
    for metric_id, raw_metric in metrics.items():
        metric = dict(raw_metric)
        binding = metric.get("source_binding")
        formula = metric.get("formula")
        if isinstance(binding, dict):
            family = str(binding.get("dataset_family") or "")
            source_field = str(binding.get("field") or "")
            owners = list(family_datasets.get(family) or [])
            if not owners or not source_field:
                _fail("Metric source family or field is missing.", {"metric_id": metric_id})
            if metric.get("source_field") not in (None, "", source_field):
                _fail("Metric source_field disagrees with source_binding.", {"metric_id": metric_id})
            additivity = dict(metric.get("additivity") or {})
            rollups = set(additivity.get("allowed_rollups") or [])
            aggregation = str(metric.get("aggregation") or "")
            if aggregation:
                rollups.add(aggregation)
            distinct = additivity.get("default") == "distinct" or (bool(rollups) and rollups <= DISTINCT_ROLLUPS)
            for dataset_key in owners:
                dataset_fields = dict(datasets[dataset_key].get("fields") or {})
                field_binding = dict(dataset_fields.get(source_field) or {})
                if not field_binding:
                    _fail(
                        "Metric source field is not present in every dataset of its family.",
                        {"metric_id": metric_id, "dataset_key": dataset_key, "field": source_field},
                    )
                roles = set(field_binding.get("roles") or [])
                compatible_roles = {"aggregate", "group", "join", "metric"} if distinct else {"aggregate", "metric"}
                if not roles & compatible_roles:
                    _fail("Metric source field roles are incompatible with its rollup.", {"metric_id": metric_id, "dataset_key": dataset_key})
                semantic = str(field_binding.get("semantic_type") or "").casefold()
                if (rollups & NUMERIC_ROLLUPS) and semantic not in NUMERIC_SEMANTIC_TYPES:
                    _fail("Numeric metric rollup requires a numeric source field.", {"metric_id": metric_id, "dataset_key": dataset_key})
                for fixed_filter in binding.get("fixed_filters") or []:
                    _validate_filter_leaf(fixed_filter, catalog, allowed_dataset=dataset_key)
        elif not isinstance(formula, dict):
            _fail("Metric must have either a source binding or a formula.", {"metric_id": metric_id})
        additivity = metric.get("additivity")
        if isinstance(additivity, dict) and additivity.get("default") == "non_additive" and "sum" in (additivity.get("allowed_rollups") or []):
            _fail("Non-additive metric cannot allow sum.", {"metric_id": metric_id})
        if isinstance(formula, dict):
            dependency_graph[metric_id].update(_validate_formula(metric_id, formula, catalog, profile))
        for dependency in metric.get("dependencies") or []:
            dependency_id = str(dependency)
            if dependency_id in metrics:
                dependency_graph[metric_id].add(dependency_id)
            elif dependency_id not in catalog["fields"] and not (
                profile == "legacy_v1_compat" and dependency_id in FORMULA_RUNTIME_REFS
            ):
                _fail("Metric dependency is not registered.", {"metric_id": metric_id, "dependency": dependency_id})
    _validate_metric_dependency_dag(dependency_graph)


def _validate_formula(
    metric_id: str, formula: Mapping[str, Any], catalog: Mapping[str, Any], profile: str
) -> set[str]:
    expression = formula.get("expression")
    if not isinstance(expression, dict):
        operator = str(formula.get("op") or "")
        key_pairs = {
            "add": ("left_metric", "right_metric"),
            "subtract": ("left_metric", "right_metric"),
            "multiply": ("left_metric", "right_metric"),
            "safe_divide": ("numerator_metric", "denominator_metric"),
        }
        if operator not in key_pairs:
            _fail("Formula operator is unsupported.", {"metric_id": metric_id, "operator": operator})
        left_key, right_key = key_pairs[operator]
        expression = {
            "op": operator,
            "args": [
                {"metric_ref": str(formula.get(left_key) or "")},
                {"metric_ref": str(formula.get(right_key) or "")},
            ],
        }
        if operator == "safe_divide":
            expression["zero_division"] = str(formula.get("zero_division") or "null")
    refs: set[str] = set()
    nodes, depth = _validate_formula_node(expression, catalog, profile, refs, 1)
    if isinstance(formula.get("max_nodes"), int) and nodes > int(formula["max_nodes"]):
        _fail("Formula exceeds its declared node bound.", {"metric_id": metric_id})
    if isinstance(formula.get("max_depth"), int) and depth > int(formula["max_depth"]):
        _fail("Formula exceeds its declared depth bound.", {"metric_id": metric_id})
    return refs


def _validate_formula_node(
    node: Mapping[str, Any],
    catalog: Mapping[str, Any],
    profile: str,
    metric_refs: set[str],
    depth: int,
) -> tuple[int, int]:
    leaf_kinds = [key for key in ("metric_ref", "field_ref", "runtime_ref", "literal") if key in node]
    if leaf_kinds:
        if len(leaf_kinds) != 1 or node.get("op"):
            _fail("Formula leaf must contain exactly one reference or literal.")
        kind = leaf_kinds[0]
        value = str(node.get(kind) or "") if kind != "literal" else node.get(kind)
        if kind == "metric_ref":
            if value not in catalog["metrics"]:
                _fail("Formula metric reference is not registered.", {"metric_ref": value})
            metric_refs.add(str(value))
        elif kind == "field_ref":
            if not value or (
                profile != "legacy_v1_compat"
                and value not in catalog["fields"]
                and value not in catalog["metrics"]
            ):
                _fail("Formula field reference is not registered.", {"field_ref": value})
        elif kind == "runtime_ref":
            if profile != "legacy_v1_compat" or value not in FORMULA_RUNTIME_REFS:
                _fail("Formula runtime reference is not allowed.", {"runtime_ref": value})
        return 1, depth
    operator = str(node.get("op") or "")
    allowed = LEGACY_FORMULA_OPERATORS if profile == "legacy_v1_compat" else FORMULA_OPERATORS
    if operator not in allowed:
        _fail("Formula expression operator is unsupported.", {"operator": operator})
    args = node.get("args")
    if not isinstance(args, list) or len(args) != FORMULA_ARITY[operator] or not all(isinstance(item, dict) for item in args):
        _fail("Formula expression arity is invalid.", {"operator": operator})
    if operator == "safe_divide" and str(node.get("zero_division") or "null") not in SAFE_DIVIDE_ZERO_POLICIES:
        _fail("safe_divide zero policy is unsupported.")
    nodes = 1
    deepest = depth
    for child in args:
        child_nodes, child_depth = _validate_formula_node(child, catalog, profile, metric_refs, depth + 1)
        nodes += child_nodes
        deepest = max(deepest, child_depth)
    return nodes, deepest


def _validate_metric_dependency_dag(graph: Mapping[str, set[str]]) -> None:
    state: dict[str, int] = {}

    def visit(metric_id: str, path: list[str]) -> None:
        if state.get(metric_id) == 1:
            _fail("Metric formula dependency cycle detected.", {"cycle": [*path, metric_id]})
        if state.get(metric_id) == 2:
            return
        state[metric_id] = 1
        for dependency in graph.get(metric_id, set()):
            visit(dependency, [*path, metric_id])
        state[metric_id] = 2

    for metric_id in graph:
        visit(metric_id, [])


def _validate_grains_and_orderings(catalog: Mapping[str, Any], profile: str) -> None:
    fields = dict(catalog["fields"])
    for grain_id, raw_grain in dict(catalog.get("grains") or {}).items():
        grain = dict(raw_grain)
        keys = list(grain.get("keys") or [])
        if not keys or not set(keys) <= set(fields):
            _fail("Grain keys must reference registered fields.", {"grain_id": grain_id})
        for key in keys:
            if not set(fields[key].get("roles") or []) & {"group", "join"}:
                _fail("Grain key must carry a group or join role.", {"grain_id": grain_id, "field": key})
        if not set(grain.get("display_fields") or []) <= set(fields):
            _fail("Grain display field is not registered.", {"grain_id": grain_id})
    for ordering_id, raw_ordering in dict(catalog.get("orderings") or {}).items():
        for item in dict(raw_ordering).get("keys") or []:
            if not isinstance(item, dict) or str(item.get("field") or "") not in fields:
                _fail("Ordering field is not registered.", {"ordering_id": ordering_id})
            if item.get("direction") not in {"asc", "desc"}:
                _fail("Ordering direction is invalid.", {"ordering_id": ordering_id})


def _validate_predicates_and_groups(catalog: Mapping[str, Any], profile: str) -> None:
    fields = dict(catalog["fields"])
    grain_ids = set(catalog.get("grains") or {})
    if profile == "legacy_v1_compat":
        grain_ids.update(_nested_identity_values(catalog.get("recipes") or {}, "grain_id"))
        grain_ids.update(catalog.get("recipes") or {})
    for predicate_id, raw_card in dict(catalog.get("predicates") or {}).items():
        card = dict(raw_card)
        allowed = set(card.get("allowed_operators") or [])
        if allowed and not allowed <= FILTER_OPERATORS:
            _fail("Predicate declares an unsupported operator.", {"predicate_id": predicate_id})
        grain_id = str(card.get("grain_id") or "")
        if grain_id and grain_id not in grain_ids:
            _fail("Predicate grain is not registered.", {"predicate_id": predicate_id, "grain_id": grain_id})
        predicate = card.get("predicate") if isinstance(card.get("predicate"), dict) else card
        _validate_predicate_tree(predicate, catalog, allowed or None, predicate_id)
    for group_id, raw_group in dict(catalog.get("entity_groups") or {}).items():
        group = dict(raw_group)
        target_field = str(group.get("target_field") or group.get("entity") or "")
        if target_field not in fields or not set(fields[target_field].get("roles") or []) & {"filter", "group"}:
            _fail("Entity group target must be a registered filter/group field.", {"group_id": group_id})
        if group.get("expansion") == "closed_set" and not list(group.get("members") or []):
            _fail("Closed-set entity group must declare members.", {"group_id": group_id})
        selection = group.get("selection")
        if isinstance(selection, dict):
            operator = str(selection.get("operator") or "")
            if operator != "all_registered":
                _validate_filter_leaf({**selection, "field": target_field}, catalog)


def _validate_predicate_tree(
    node: Mapping[str, Any],
    catalog: Mapping[str, Any],
    allowed: set[str] | None,
    predicate_id: str,
) -> None:
    boolean_op = str(node.get("op") or "")
    if boolean_op:
        clauses = node.get("clauses")
        if boolean_op not in {"all", "any"} or not isinstance(clauses, list) or not clauses:
            _fail("Predicate boolean tree is invalid.", {"predicate_id": predicate_id})
        for clause in clauses:
            if not isinstance(clause, dict):
                _fail("Predicate clause must be an object.", {"predicate_id": predicate_id})
            _validate_predicate_tree(clause, catalog, allowed, predicate_id)
        return
    operator = _validate_filter_leaf(node, catalog)
    if allowed is not None and operator not in allowed:
        _fail("Predicate leaf operator is outside the declared allowlist.", {"predicate_id": predicate_id, "operator": operator})


def _validate_filter_leaf(
    leaf: Mapping[str, Any], catalog: Mapping[str, Any], *, allowed_dataset: str = ""
) -> str:
    field = str(leaf.get("field") or "")
    operator = str(leaf.get("operator") or "")
    if operator not in FILTER_OPERATORS:
        _fail("Filter operator is unsupported.", {"field": field, "operator": operator})
    owners = [allowed_dataset] if allowed_dataset else list(dict(catalog.get("fields") or {}).get(field, {}).get("dataset_keys") or [])
    if not owners:
        _fail("Filter field is not registered.", {"field": field})
    matched = False
    for dataset_key in owners:
        binding = dict(dict(dict(catalog["datasets"])[dataset_key].get("fields") or {}).get(field) or {})
        if "filter" not in set(binding.get("roles") or []):
            continue
        allowed = set(binding.get("allowed_filter_operators") or [])
        if allowed and operator not in allowed:
            continue
        declared_semantic = leaf.get("semantic_type")
        if declared_semantic and not _semantic_types_compatible(declared_semantic, binding.get("semantic_type")):
            continue
        matched = True
    if not matched:
        _fail("Filter field role, semantic type, or operator is incompatible.", {"field": field, "operator": operator})
    return operator


def _validate_recipes(catalog: Mapping[str, Any], profile: str) -> None:
    recipes = dict(catalog.get("recipes") or {})
    allowed_operations = ALLOWED_OPERATIONS if profile == "legacy_v1_compat" else GENERIC_V2_OPERATIONS
    for recipe_id, raw_recipe in recipes.items():
        recipe = dict(raw_recipe)
        required = list(recipe.get("required_slots") or [])
        if len(required) != len(set(required)) or any(not isinstance(slot, str) or not slot for slot in required):
            _fail("Recipe required slots are invalid.", {"recipe_id": recipe_id})
        if profile != "legacy_v1_compat" and not set(required) <= GENERIC_REQUIRED_SLOTS:
            _fail("Generic recipe uses an unregistered required slot.", {"recipe_id": recipe_id, "required_slots": required})
        for operation in _recipe_operations(recipe):
            if operation not in allowed_operations:
                _fail("Recipe uses an operation outside its planner profile.", {"recipe_id": recipe_id, "op": operation, "planner_profile": profile})
        if profile != "legacy_v1_compat":
            _validate_generic_recipe_refs(recipe_id, recipe, catalog)


def _validate_generic_recipe_refs(
    recipe_id: str, recipe: Mapping[str, Any], catalog: Mapping[str, Any]
) -> None:
    template = recipe.get("default_operation_template")
    if not isinstance(template, dict):
        _fail("Generic recipe requires a typed operation template.", {"recipe_id": recipe_id})
    registries = {
        "dataset": set(catalog.get("datasets") or {}),
        "relation": set(catalog.get("relations") or {}),
        "metric": set(catalog.get("metrics") or {}),
        "field": set(catalog.get("fields") or {}) | set(catalog.get("metrics") or {}),
        "grain": set(catalog.get("grains") or {}),
        "predicate": set(catalog.get("predicates") or {}),
        "recipe": set(catalog.get("recipes") or {}),
    }

    def check(kind: str, value: Any, path: str) -> None:
        if not isinstance(value, str) or not value or value.startswith("$"):
            return
        prefix, separator, suffix = value.partition(":")
        normalized = suffix if separator and prefix in registries else value
        if normalized not in registries[kind]:
            _fail("Generic recipe reference is not registered.", {"recipe_id": recipe_id, "reference_kind": kind, "reference": value, "path": path})

    singular = {
        "dataset": "dataset", "dataset_key": "dataset", "relation_id": "relation", "relation_ref": "relation",
        "metric": "metric", "metric_ref": "metric", "left_metric_ref": "metric", "right_metric_ref": "metric",
        "formula_ref": "metric", "grain_id": "grain", "grain_ref": "grain", "predicate_id": "predicate",
        "predicate_ref": "predicate", "recipe_ref": "recipe", "field": "field", "field_ref": "field",
        "output_field": "field", "left": "field", "right": "field",
    }
    plural = {
        "datasets": "dataset", "dataset_keys": "dataset", "metrics": "metric", "metric_refs": "metric",
        "fields": "field", "allowed_fields": "field", "group_by": "field", "stable_tie_break": "field",
        "relation_refs": "relation", "grain_refs": "grain", "predicate_refs": "predicate", "recipe_refs": "recipe",
    }

    def walk(value: Any, path: str = "template") -> None:
        if isinstance(value, dict):
            operation = str(value.get("op") or "")
            if operation == "join" and not value.get("relation_id") and not value.get("relation_ref"):
                _fail("Generic join recipe must reference a registered relation.", {"recipe_id": recipe_id, "path": path})
            if operation == "derive" and not value.get("metric") and not value.get("formula_ref"):
                _fail("Generic derive recipe must reference a registered metric formula.", {"recipe_id": recipe_id, "path": path})
            for key, child in value.items():
                if key in singular:
                    check(singular[key], child, f"{path}.{key}")
                elif key in plural and isinstance(child, list):
                    for item in child:
                        if isinstance(item, str):
                            check(plural[key], item, f"{path}.{key}")
                if key not in {"aliases", "description", "pseudocode"}:
                    walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}.{index}")

    walk(template)


def _validate_aliases(catalog: Mapping[str, Any], profile: str) -> None:
    if profile == "legacy_v1_compat":
        return
    registries = {
        "dataset": set(catalog.get("datasets") or {}),
        "field": set(catalog.get("fields") or {}),
        "metric": set(catalog.get("metrics") or {}),
        "relation": set(catalog.get("relations") or {}),
        "grain": set(catalog.get("grains") or {}),
        "predicate": set(catalog.get("predicates") or {}),
        "recipe": set(catalog.get("recipes") or {}),
        "entity_group": set(catalog.get("entity_groups") or {}),
    }
    for alias_id, raw_alias in dict(catalog.get("aliases") or {}).items():
        alias = dict(raw_alias)
        target_type = str(alias.get("target_type") or "")
        target_key = str(alias.get("target_key") or "")
        if target_type not in registries or target_key not in registries[target_type]:
            _fail("Alias target is not registered.", {"alias_id": alias_id, "target_type": target_type, "target_key": target_key})


def _validate_specialized_functions(catalog: Mapping[str, Any]) -> None:
    seen_functions: set[tuple[str, int]] = set()
    for function in catalog.get("specialized_functions") or []:
        marker = (str(function["function_id"]), int(function["version"]))
        if marker in seen_functions:
            _fail("Specialized function identity is duplicated.", {"function_id": marker[0]})
        seen_functions.add(marker)
        if function.get("execution_mode") != "registered_standalone" or not SHA256_PATTERN.fullmatch(str(function.get("implementation_sha256") or "")):
            _fail("Specialized function must be registered-standalone and hash pinned.")
        if not set(function.get("required_fields") or []) <= set(catalog["fields"]):
            _fail("Specialized function required field is not registered.", {"function_id": marker[0]})


def _nested_identity_values(value: Any, identity_key: str) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        if isinstance(value.get(identity_key), str):
            result.add(str(value[identity_key]))
        for child in value.values():
            result.update(_nested_identity_values(child, identity_key))
    elif isinstance(value, list):
        for child in value:
            result.update(_nested_identity_values(child, identity_key))
    return result


def _semantic_types_compatible(left: Any, right: Any) -> bool:
    left_value = str(left or "").casefold()
    right_value = str(right or "").casefold()
    if not left_value or not right_value:
        return False
    return (
        left_value == right_value
        or left_value in NUMERIC_SEMANTIC_TYPES and right_value in NUMERIC_SEMANTIC_TYPES
        or left_value in TEXTUAL_SEMANTIC_TYPES and right_value in TEXTUAL_SEMANTIC_TYPES
    )


def _recipe_operations(value: Any) -> list[str]:
    operations: list[str] = []
    if isinstance(value, dict):
        if isinstance(value.get("op"), str):
            operations.append(str(value["op"]))
        for key, child in value.items():
            if key in {"pseudocode", "description", "aliases"}:
                continue
            operations.extend(_recipe_operations(child))
    elif isinstance(value, list):
        for child in value:
            operations.extend(_recipe_operations(child))
    return operations


def _map_legacy_recipe_ops(value: Any) -> Any:
    if isinstance(value, dict):
        result = {key: _map_legacy_recipe_ops(child) for key, child in value.items()}
        legacy = str(result.get("op") or "")
        mapped = {"detail": "project", "enrich_previous_result": "join"}.get(legacy)
        if mapped:
            result["legacy_op"] = legacy
            result["op"] = mapped
        return result
    if isinstance(value, list):
        return [_map_legacy_recipe_ops(child) for child in value]
    return deepcopy(value)


def _identity_cards(value: Any, identity_key: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in sorted(dict(value or {})):
        card = deepcopy(dict(dict(value or {})[key]))
        existing_identity = card.get(identity_key)
        if existing_identity not in (None, "", key):
            card.setdefault("legacy_identity", existing_identity)
        card[identity_key] = key
        result[key] = card
    return result


def _reject_executable_or_secret_payload(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for raw_key, child in value.items():
            key = str(raw_key).strip().casefold()
            location = ".".join((*path, str(raw_key)))
            # Registry-map keys are domain identities, not payload field names.
            # For example, ``product_token_match_case`` is a legitimate recipe
            # ID even though it contains the word ``token``.  Continue scanning
            # the identity's value recursively so secret-bearing inner keys and
            # scalar credential patterns remain fail-closed.
            identity_key = bool(path) and str(path[-1]).casefold() in IDENTITY_CONTAINER_KEYS
            if not identity_key:
                if key in FORBIDDEN_EXECUTABLE_KEYS:
                    _fail("authoring draft에는 실행 코드/자유 query를 저장할 수 없습니다.", {"path": location})
                if any(
                    part in key
                    for part in SECRET_KEY_PARTS
                    if part != "token" or key not in ALLOWED_NON_SECRET_TOKEN_KEYS
                ):
                    _fail("authoring draft에는 secret/credential 값을 저장할 수 없습니다.", {"path": location})
            _reject_executable_or_secret_payload(child, (*path, str(raw_key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_executable_or_secret_payload(child, (*path, str(index)))
    elif isinstance(value, str):
        for pattern_id, pattern in SECRET_SCALAR_PATTERNS:
            if pattern.search(value):
                _fail(
                    "authoring draft에는 secret/credential 값을 저장할 수 없습니다.",
                    {"path": ".".join(path), "pattern_id": pattern_id},
                )


def _default_coercion(semantic_type: str) -> str:
    normalized = semantic_type.casefold()
    if normalized in {"number", "quantity", "currency", "rate", "integer"}:
        return "strict_number" if normalized != "integer" else "strict_integer"
    if normalized in {"localdate", "date"}:
        return "strict_date"
    if normalized in {"localdatetime", "datetime"}:
        return "strict_datetime"
    return "string"


def _identity(value: str, label: str, pattern: re.Pattern[str]) -> str:
    normalized = str(value or "").strip().casefold()
    if not pattern.fullmatch(normalized):
        _fail(f"{label} 형식이 올바르지 않습니다.", {label: value})
    return normalized


def _assert_v6_collection(actual: str, expected: str) -> None:
    if actual != expected or not actual.startswith("agent_v6_"):
        raise ValueError(f"collection boundary violation: expected {expected}")


def _find_one(collection: Any, query: dict[str, Any]) -> dict[str, Any] | None:
    result = collection.find_one(query)
    return deepcopy(result) if isinstance(result, dict) else None


def load_domain_package_file(path: str | Path) -> dict[str, Any]:
    return validate_domain_package(json.loads(Path(path).read_text(encoding="utf-8")))


def _fail(message: str, details: Mapping[str, Any] | None = None) -> None:
    raise ContractError("metadata_dependency_error", "metadata_domain_compile", message, dict(details or {}))


__all__ = [
    "ACTIVE_POINTER_COLLECTION",
    "ACTIVE_POINTER_VERSION",
    "AUTHORING_DRAFT_VERSION",
    "DOMAIN_COMPILER_VERSION",
    "DOMAIN_PACKAGE_COLLECTION",
    "DOMAIN_PACKAGE_VERSION",
    "MIGRATION_QUARANTINE_COLLECTION",
    "RUNTIME_CATALOG_V2",
    "adapt_legacy_catalog_v1",
    "build_runtime_catalog_v2",
    "compile_domain_package",
    "compute_bundle_sha256",
    "compute_package_sha256",
    "compute_runtime_catalog_v2_sha256",
    "load_active_domain_bundle",
    "load_domain_package_file",
    "make_active_pointer",
    "make_active_pointer_document",
    "make_bundle_document",
    "validate_domain_package",
    "validate_runtime_catalog_v2",
]
