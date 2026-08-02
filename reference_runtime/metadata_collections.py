"""Three-collection metadata persistence for metadata-driven v6.

The human-managed source of truth is deliberately limited to domain, table
catalog, and main-filter documents.  Each release replaces the three current
documents in one MongoDB transaction.  Runtime readers accept the release only
when every identity, section seal, and the shared release manifest agree.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import re
from typing import Any, Mapping

from .canonical import ContractError, sha256_json
from .domain_packages import validate_domain_package


METADATA_SECTION_VERSION = "metadata.section.v1"
METADATA_RELEASE_VERSION = "metadata.release.v1"
DOMAIN_METADATA_COLLECTION = "agent_v6_domain_metadata"
TABLE_CATALOG_COLLECTION = "agent_v6_table_catalog"
MAIN_FILTER_COLLECTION = "agent_v6_main_filter"
METADATA_COLLECTIONS = {
    "domain": DOMAIN_METADATA_COLLECTION,
    "table_catalog": TABLE_CATALOG_COLLECTION,
    "main_filter": MAIN_FILTER_COLLECTION,
}
_COLLECTION_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")

_DOMAIN_CATALOG_KEYS = {
    "contract_version",
    "domain_id",
    "environment",
    "revision",
    "compiler_version",
    "display_name",
    "description",
    "locale",
    "timezone",
    "metrics",
    "entity_groups",
    "grains",
    "relations",
    "orderings",
    "recipes",
    "prompt_extensions",
    "specialized_functions",
    "output_profile",
}
_TABLE_CATALOG_KEYS = {"datasets", "fields"}
_MAIN_FILTER_KEYS = {"predicates", "aliases"}


def _metadata_collection_fail(message: str, details: Mapping[str, Any] | None = None) -> None:
    raise ContractError(
        "metadata_dependency_error",
        "metadata_three_collection",
        message,
        deepcopy(dict(details or {})),
    )


def _metadata_collection_names(
    domain_collection: Any,
    table_collection: Any,
    main_filter_collection: Any,
) -> dict[str, str]:
    actual = {
        "domain": str(domain_collection or "").strip(),
        "table_catalog": str(table_collection or "").strip(),
        "main_filter": str(main_filter_collection or "").strip(),
    }
    invalid = [
        role
        for role, name in actual.items()
        if _COLLECTION_NAME_PATTERN.fullmatch(name) is None
        or name.casefold().startswith("system.")
    ]
    if invalid or len(set(actual.values())) != 3:
        _metadata_collection_fail(
            "메타데이터 컬렉션 이름은 안전한 서로 다른 세 이름이어야 합니다.",
            {"invalid_roles": invalid, "actual": actual},
        )
    return actual


def _source_texts(value: Mapping[str, Any] | None) -> dict[str, str]:
    raw = dict(value or {})
    result = {
        "domain": str(raw.get("domain") or ""),
        "table_catalog": str(raw.get("table_catalog") or raw.get("dataset") or ""),
        "main_filter": str(raw.get("main_filter") or ""),
    }
    for kind, text in result.items():
        size = len(text.encode("utf-8"))
        if size > 65536:
            _metadata_collection_fail("자연어 메타데이터 원문이 64 KiB 제한을 초과했습니다.", {"section_kind": kind})
    return result


def _catalog_sections(catalog: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    value = deepcopy(dict(catalog))
    expected = _DOMAIN_CATALOG_KEYS | _TABLE_CATALOG_KEYS | _MAIN_FILTER_KEYS | {"catalog_sha256"}
    if set(value) != expected:
        _metadata_collection_fail(
            "runtime catalog top-level section이 등록 계약과 일치하지 않습니다.",
            {"missing": sorted(expected - set(value)), "unknown": sorted(set(value) - expected)},
        )
    return {
        "domain": {key: deepcopy(value[key]) for key in sorted(_DOMAIN_CATALOG_KEYS)},
        "table_catalog": {key: deepcopy(value[key]) for key in sorted(_TABLE_CATALOG_KEYS)},
        "main_filter": {key: deepcopy(value[key]) for key in sorted(_MAIN_FILTER_KEYS)},
    }


def make_metadata_section_documents(
    package: Mapping[str, Any],
    source_texts: Mapping[str, Any] | None,
    *,
    updated_at: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Split one validated package into three human-managed current documents."""

    validated = validate_domain_package(package)
    catalog = validated["runtime_catalog"]
    sections = _catalog_sections(catalog)
    sources = _source_texts(source_texts)
    timestamp = str(updated_at or datetime.now(timezone.utc).isoformat())
    identity = {
        "domain_id": validated["domain_id"],
        "environment": validated["environment"],
        "revision": int(validated["revision"]),
    }
    current_id = f"{identity['environment']}:{identity['domain_id']}"
    package_meta = {
        key: deepcopy(value)
        for key, value in validated.items()
        if key != "runtime_catalog"
    }
    section_materials: dict[str, dict[str, Any]] = {}
    section_hashes: dict[str, str] = {}
    for kind in ("domain", "table_catalog", "main_filter"):
        source_text = sources[kind]
        material = {
            "contract_version": METADATA_SECTION_VERSION,
            "section_kind": kind,
            **identity,
            "source_text": source_text,
            "source_sha256": sha256_json(source_text),
            "normalized_metadata": sections[kind],
        }
        section_materials[kind] = material
        section_hashes[kind] = sha256_json(material)
    manifest = {
        "contract_version": METADATA_RELEASE_VERSION,
        **identity,
        "section_sha256": deepcopy(section_hashes),
        "catalog_sha256": str(catalog["catalog_sha256"]),
        "package_sha256": str(validated["package_sha256"]),
        "bundle_sha256": str(validated["bundle_sha256"]),
    }
    release_hash = sha256_json(manifest)
    release_id = f"release:{release_hash}"
    documents: dict[str, dict[str, Any]] = {}
    for kind, material in section_materials.items():
        document = {
            "_id": current_id,
            **deepcopy(material),
            "section_sha256": section_hashes[kind],
            "release_id": release_id,
            "release_manifest": deepcopy(manifest),
            "release_manifest_sha256": release_hash,
            "package_meta": deepcopy(package_meta),
            "updated_at": timestamp,
        }
        document["document_sha256"] = sha256_json(
            {key: deepcopy(value) for key, value in document.items() if key != "document_sha256"}
        )
        documents[kind] = document
    return documents


def _validate_section_document(
    document: Mapping[str, Any],
    *,
    expected_kind: str,
    domain_id: str,
    environment: str,
) -> dict[str, Any]:
    value = deepcopy(dict(document))
    if value.get("_id") != f"{environment}:{domain_id}":
        _metadata_collection_fail("메타데이터 문서 ID가 요청한 domain/environment와 일치하지 않습니다.", {"section_kind": expected_kind})
    if value.get("contract_version") != METADATA_SECTION_VERSION or value.get("section_kind") != expected_kind:
        _metadata_collection_fail("메타데이터 section 계약이 일치하지 않습니다.", {"section_kind": expected_kind})
    if value.get("domain_id") != domain_id or value.get("environment") != environment:
        _metadata_collection_fail("메타데이터 section identity가 일치하지 않습니다.", {"section_kind": expected_kind})
    source_text = value.get("source_text")
    if not isinstance(source_text, str) or value.get("source_sha256") != sha256_json(source_text):
        _metadata_collection_fail("자연어 메타데이터 원문 해시가 일치하지 않습니다.", {"section_kind": expected_kind})
    normalized = value.get("normalized_metadata")
    if not isinstance(normalized, dict):
        _metadata_collection_fail("정규화 메타데이터 section이 객체가 아닙니다.", {"section_kind": expected_kind})
    material = {
        "contract_version": value.get("contract_version"),
        "section_kind": value.get("section_kind"),
        "domain_id": value.get("domain_id"),
        "environment": value.get("environment"),
        "revision": value.get("revision"),
        "source_text": source_text,
        "source_sha256": value.get("source_sha256"),
        "normalized_metadata": normalized,
    }
    if value.get("section_sha256") != sha256_json(material):
        _metadata_collection_fail("정규화 메타데이터 section 해시가 일치하지 않습니다.", {"section_kind": expected_kind})
    document_hash_material = {
        key: deepcopy(item) for key, item in value.items() if key != "document_sha256"
    }
    if value.get("document_sha256") != sha256_json(document_hash_material):
        _metadata_collection_fail("메타데이터 문서 봉인 해시가 일치하지 않습니다.", {"section_kind": expected_kind})
    return value


def assemble_domain_package_from_sections(
    documents: Mapping[str, Mapping[str, Any]],
    domain_id: str,
    environment: str,
) -> dict[str, Any]:
    """Validate and join the three current documents into one runtime package."""

    values = {
        kind: _validate_section_document(
            documents.get(kind) or {},
            expected_kind=kind,
            domain_id=domain_id,
            environment=environment,
        )
        for kind in ("domain", "table_catalog", "main_filter")
    }
    release_ids = {str(value.get("release_id") or "") for value in values.values()}
    revisions = {int(value.get("revision") or 0) for value in values.values()}
    manifest_hashes = {str(value.get("release_manifest_sha256") or "") for value in values.values()}
    if len(release_ids) != 1 or len(revisions) != 1 or len(manifest_hashes) != 1:
        _metadata_collection_fail("세 메타데이터 컬렉션의 release가 서로 일치하지 않습니다.")
    manifests = [value.get("release_manifest") for value in values.values()]
    if any(not isinstance(item, dict) for item in manifests):
        _metadata_collection_fail("release manifest가 누락되었습니다.")
    manifest = deepcopy(manifests[0])
    if any(item != manifest for item in manifests[1:]):
        _metadata_collection_fail("세 메타데이터 컬렉션의 release manifest 내용이 다릅니다.")
    release_hash = sha256_json(manifest)
    if release_hash not in manifest_hashes or release_ids != {f"release:{release_hash}"}:
        _metadata_collection_fail("release manifest 봉인값이 일치하지 않습니다.")
    expected_section_hashes = {
        kind: str(values[kind].get("section_sha256") or "")
        for kind in ("domain", "table_catalog", "main_filter")
    }
    if manifest.get("section_sha256") != expected_section_hashes:
        _metadata_collection_fail("release manifest의 section hash가 현재 문서와 일치하지 않습니다.")
    domain_section = deepcopy(values["domain"]["normalized_metadata"])
    catalog = {
        **domain_section,
        **deepcopy(values["table_catalog"]["normalized_metadata"]),
        **deepcopy(values["main_filter"]["normalized_metadata"]),
        "catalog_sha256": str(manifest.get("catalog_sha256") or ""),
    }
    package_meta = values["domain"].get("package_meta")
    if not isinstance(package_meta, dict) or any(value.get("package_meta") != package_meta for value in values.values()):
        _metadata_collection_fail("세 메타데이터 컬렉션의 package metadata가 일치하지 않습니다.")
    package = {**deepcopy(package_meta), "runtime_catalog": catalog}
    validated = validate_domain_package(package)
    if (
        validated["package_sha256"] != manifest.get("package_sha256")
        or validated["bundle_sha256"] != manifest.get("bundle_sha256")
        or validated["runtime_catalog"]["catalog_sha256"] != manifest.get("catalog_sha256")
    ):
        _metadata_collection_fail("결합된 메타데이터 package hash가 release manifest와 일치하지 않습니다.")
    return validated


def load_domain_package_from_three_collections(
    database: Any,
    domain_id: str,
    environment: str,
    *,
    domain_collection: str = DOMAIN_METADATA_COLLECTION,
    table_collection: str = TABLE_CATALOG_COLLECTION,
    main_filter_collection: str = MAIN_FILTER_COLLECTION,
    session: Any = None,
) -> dict[str, Any]:
    actual = _metadata_collection_names(
        domain_collection,
        table_collection,
        main_filter_collection,
    )
    current_id = f"{environment}:{domain_id}"
    documents = {
        kind: database[collection].find_one({"_id": current_id}, session=session)
        for kind, collection in actual.items()
    }
    missing = [kind for kind, document in documents.items() if not isinstance(document, dict)]
    if missing:
        _metadata_collection_fail("필수 메타데이터 section을 찾을 수 없습니다.", {"missing_sections": missing})
    return assemble_domain_package_from_sections(documents, domain_id, environment)


def load_available_domain_package_from_three_collections(
    database: Any,
    *,
    domain_collection: str = DOMAIN_METADATA_COLLECTION,
    table_collection: str = TABLE_CATALOG_COLLECTION,
    main_filter_collection: str = MAIN_FILTER_COLLECTION,
    session: Any = None,
) -> dict[str, Any]:
    """Load the newest complete metadata release without a Flow-level selector.

    A deployment publishes its currently usable metadata by replacing the three
    documents for a domain.  The runtime accepts safe, distinct collection
    names from the Langflow node, discovers the newest domain document, and
    validates the matching table-catalog and main-filter documents through the
    normal sealed join.
    """

    actual = _metadata_collection_names(
        domain_collection,
        table_collection,
        main_filter_collection,
    )

    collection = database[actual["domain"]]
    try:
        latest = collection.find_one(
            {},
            sort=[("updated_at", -1), ("revision", -1), ("_id", -1)],
            session=session,
        )
    except TypeError:
        # Small in-memory test doubles may not implement pymongo's sort/session
        # keyword arguments.  Production pymongo always uses the ordered path.
        latest = collection.find_one({})
    if not isinstance(latest, dict):
        _metadata_collection_fail("사용 가능한 도메인 메타데이터가 없습니다.")

    domain_id = str(latest.get("domain_id") or "").strip()
    environment = str(latest.get("environment") or "").strip()
    if not domain_id or not environment or latest.get("_id") != f"{environment}:{domain_id}":
        _metadata_collection_fail("최신 도메인 메타데이터 identity가 올바르지 않습니다.")
    return load_domain_package_from_three_collections(
        database,
        domain_id,
        environment,
        domain_collection=actual["domain"],
        table_collection=actual["table_catalog"],
        main_filter_collection=actual["main_filter"],
        session=session,
    )


def replace_metadata_release(
    database: Any,
    documents: Mapping[str, Mapping[str, Any]],
    *,
    session: Any = None,
    domain_collection: str = DOMAIN_METADATA_COLLECTION,
    table_collection: str = TABLE_CATALOG_COLLECTION,
    main_filter_collection: str = MAIN_FILTER_COLLECTION,
) -> None:
    collections = _metadata_collection_names(
        domain_collection,
        table_collection,
        main_filter_collection,
    )
    for kind, collection in collections.items():
        document = deepcopy(dict(documents[kind]))
        database[str(collection)].replace_one(
            {"_id": document["_id"]},
            document,
            upsert=True,
            session=session,
        )


__all__ = [
    "DOMAIN_METADATA_COLLECTION",
    "MAIN_FILTER_COLLECTION",
    "METADATA_COLLECTIONS",
    "METADATA_RELEASE_VERSION",
    "METADATA_SECTION_VERSION",
    "TABLE_CATALOG_COLLECTION",
    "assemble_domain_package_from_sections",
    "load_available_domain_package_from_three_collections",
    "load_domain_package_from_three_collections",
    "make_metadata_section_documents",
    "replace_metadata_release",
]
