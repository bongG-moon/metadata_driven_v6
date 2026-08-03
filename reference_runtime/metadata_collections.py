"""Simple item-oriented MongoDB persistence for metadata-driven v6.

MongoDB is the human-managed authoring store.  It contains only individually
editable metadata items and their natural-language input.  Runtime-only
contracts, hashes, release manifests, and package identity are compiled in
memory after the three collections are read.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import re
from typing import Any, Mapping, Sequence

from .canonical import ContractError
from .domain_packages import compile_domain_package, validate_domain_package


METADATA_SECTION_VERSION = "metadata.item.v1"
METADATA_RELEASE_VERSION = "runtime_only"
DOMAIN_METADATA_COLLECTION = "agent_v6_domain_metadata"
TABLE_CATALOG_COLLECTION = "agent_v6_table_catalog"
MAIN_FILTER_COLLECTION = "agent_v6_main_filter"
METADATA_COLLECTIONS = {
    "domain": DOMAIN_METADATA_COLLECTION,
    "table_catalog": TABLE_CATALOG_COLLECTION,
    "main_filter": MAIN_FILTER_COLLECTION,
}

_COLLECTION_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
_ITEM_KEYS = {"_id", "section", "key", "natural_text", "payload", "updated_at"}
_DOMAIN_MAP_SECTIONS = (
    "metrics",
    "entity_groups",
    "grains",
    "relations",
    "orderings",
    "predicates",
    "recipes",
)
_ALIAS_PROVENANCE_TO_COLLECTION = {
    "domain": "domain",
    "table_catalog": "table_catalog",
    "main_filters": "main_filter",
}


def _fail(message: str, details: Mapping[str, Any] | None = None) -> None:
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
        _fail(
            "메타데이터 컬렉션 이름은 안전하고 서로 다른 세 이름이어야 합니다.",
            {"invalid_roles": invalid, "actual": actual},
        )
    return actual


def _clean_natural_text(value: Any) -> str:
    text = str(value or "").replace("\r\n", "\n").strip()
    return text[:2000]


def _source_texts(value: Mapping[str, Any] | None) -> dict[str, str]:
    raw = dict(value or {})
    return {
        "domain": str(raw.get("domain") or ""),
        "table_catalog": str(raw.get("table_catalog") or raw.get("dataset") or ""),
        "main_filter": str(raw.get("main_filter") or ""),
    }


def _text_blocks(value: str) -> list[str]:
    text = str(value or "").replace("\r\n", "\n").strip()
    if not text:
        return []
    blocks = [item.strip() for item in re.split(r"\n\s*\n+|(?=^#{1,6}\s)", text, flags=re.M) if item.strip()]
    return blocks or [text]


def _payload_needles(value: Any, result: list[str] | None = None) -> list[str]:
    """Return only identity/alias phrases suitable for source-block matching.

    Execution settings such as a dataset family or aggregation name are
    intentionally ignored.  Matching those generic values can attach an
    unrelated worker paragraph to another metadata item.
    """

    found = result if result is not None else []
    if len(found) >= 64:
        return found
    if isinstance(value, Mapping):
        for name in (
            "aliases",
            "display_name",
            "target_key",
            "metric_id",
            "group_id",
            "grain_id",
            "relation_id",
            "ordering_id",
            "recipe_id",
            "function_id",
            "values",
            "text",
        ):
            if name in value:
                _payload_needles(value[name], found)
    elif isinstance(value, (list, tuple)):
        for child in value[:128]:
            _payload_needles(child, found)
    elif isinstance(value, str):
        text = value.strip()
        generic = {
            "true", "false", "string", "number", "integer", "identifier",
            "filter", "group", "join", "project", "output", "sort", "rank",
            "metric", "aggregate", "sum", "mean", "min", "max", "field",
            "dataset", "domain", "main_filters", "ko-kr", "asia/seoul",
        }
        if 2 <= len(text) <= 128 and text.casefold() not in generic:
            found.append(text.casefold())
    return list(dict.fromkeys(found))[:64]


def _natural_item_summary(section: str, key: str, payload: Any) -> str:
    value = dict(payload) if isinstance(payload, Mapping) else {}
    aliases = value.get("aliases") if isinstance(value.get("aliases"), list) else []
    alias_text = ", ".join(str(item) for item in aliases[:12] if str(item).strip())
    if section == "profile":
        display_name = str(value.get("display_name") or key)
        description = str(value.get("description") or "").strip()
        return _clean_natural_text(
            f"{display_name} 도메인을 등록합니다."
            + (f" 설명: {description}" if description else "")
        )
    if section == "datasets":
        display_name = str(value.get("display_name") or key)
        source_type = str(value.get("source_type") or "").strip()
        fields = ", ".join(str(item) for item in list((value.get("fields") or {}).keys())[:24])
        return _clean_natural_text(
            f"{key} 데이터셋을 {display_name} 이름으로 등록합니다."
            + (f" 데이터 원천은 {source_type}입니다." if source_type else "")
            + (f" 주요 필드는 {fields}입니다." if fields else "")
        )
    if section == "aliases":
        target_type = str(value.get("target_type") or "항목")
        target_key = str(value.get("target_key") or key)
        card_values = value.get("values") if isinstance(value.get("values"), list) else []
        expressions = []
        for item in card_values:
            text = item.get("text") if isinstance(item, Mapping) else item
            if str(text or "").strip():
                expressions.append(str(text).strip())
        expression_text = ", ".join(expressions[:24])
        return _clean_natural_text(
            f"{target_type} {target_key}의 자연어 별칭을 등록합니다."
            + (f" 인식 표현은 {expression_text}입니다." if expression_text else "")
        )
    labels = {
        "metrics": "지표",
        "entity_groups": "대상 그룹",
        "grains": "분석 단위",
        "relations": "조인 관계",
        "orderings": "정렬 기준",
        "predicates": "조건",
        "recipes": "분석 방법",
        "prompt_extensions": "특화 프롬프트",
        "specialized_functions": "특화 함수",
        "output_profile": "출력 설정",
    }
    label = labels.get(section, section)
    summary = f"{key} {label} 항목을 등록합니다."
    if alias_text:
        summary += f" 인식 표현은 {alias_text}입니다."
    elif value:
        compact = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        summary += f" 설정은 {compact[:1200]}입니다."
    return _clean_natural_text(summary)


def _natural_text_for_item(source_text: str, section: str, key: str, payload: Any) -> str:
    blocks = _text_blocks(source_text)
    needles = [str(key).casefold()]
    if ":" in str(key):
        needles.append(str(key).split(":", 1)[1].casefold())
    for block in blocks:
        folded = block.casefold()
        if any(needle and needle in folded for needle in needles):
            return _clean_natural_text(block)
    payload_needles = _payload_needles(payload)
    scored = sorted(
        (
            (sum(1 for needle in payload_needles if needle and needle in block.casefold()), -len(block), block)
            for block in blocks
        ),
        reverse=True,
    )
    if scored and scored[0][0] > 0:
        return _clean_natural_text(scored[0][2])
    return _natural_item_summary(section, key, payload)


def _legacy_natural_text(
    legacy: Mapping[str, Any] | None,
    *,
    document_id: str,
    section: str,
    key: str,
) -> str:
    values = dict(legacy or {})
    folded_values = {str(marker).casefold(): value for marker, value in values.items()}
    for marker in (document_id, f"{section}:{key}", key):
        if marker in values:
            return _clean_natural_text(values[marker])
        if marker.casefold() in folded_values:
            return _clean_natural_text(folded_values[marker.casefold()])
    return ""


def _item_document(
    collection_kind: str,
    section: str,
    key: str,
    payload: Any,
    *,
    source_text: str,
    legacy_natural_texts: Mapping[str, Any] | None,
    updated_at: str,
) -> dict[str, Any]:
    item_key = str(key or "").strip()
    if not item_key:
        _fail("메타데이터 항목 key가 비어 있습니다.", {"section": section})
    document_id = f"{collection_kind}:{section}:{item_key}"
    natural_text = _legacy_natural_text(
        legacy_natural_texts,
        document_id=document_id,
        section=section,
        key=item_key,
    ) or _natural_text_for_item(source_text, section, item_key, payload)
    return {
        "_id": document_id,
        "section": str(section),
        "key": item_key,
        "natural_text": natural_text,
        "payload": deepcopy(payload),
        "updated_at": str(updated_at),
    }


def make_metadata_item_documents(
    package: Mapping[str, Any],
    source_texts: Mapping[str, Any] | None,
    *,
    legacy_natural_texts: Mapping[str, Any] | None = None,
    updated_at: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Split a validated package into independently editable MongoDB items."""

    validated = validate_domain_package(package)
    catalog = deepcopy(validated["runtime_catalog"])
    sources = _source_texts(source_texts)
    timestamp = str(updated_at or datetime.now(timezone.utc).isoformat())
    documents: dict[str, list[dict[str, Any]]] = {
        "domain": [],
        "table_catalog": [],
        "main_filter": [],
    }

    profile = {
        "display_name": str(catalog.get("display_name") or validated["domain_id"]),
        "description": str(catalog.get("description") or ""),
        "locale": str(catalog.get("locale") or "ko-KR"),
        "timezone": str(catalog.get("timezone") or "Asia/Seoul"),
    }
    documents["domain"].append(
        _item_document(
            "domain",
            "profile",
            str(validated["domain_id"]),
            profile,
            source_text=sources["domain"],
            legacy_natural_texts=legacy_natural_texts,
            updated_at=timestamp,
        )
    )

    for section in _DOMAIN_MAP_SECTIONS:
        values = catalog.get(section) if isinstance(catalog.get(section), dict) else {}
        for key in sorted(values):
            documents["domain"].append(
                _item_document(
                    "domain",
                    section,
                    key,
                    values[key],
                    source_text=sources["domain"],
                    legacy_natural_texts=legacy_natural_texts,
                    updated_at=timestamp,
                )
            )

    prompt_extensions = catalog.get("prompt_extensions") if isinstance(catalog.get("prompt_extensions"), dict) else {}
    for key in ("intent", "answer"):
        documents["domain"].append(
            _item_document(
                "domain",
                "prompt_extensions",
                key,
                {"text": str(prompt_extensions.get(key) or "")},
                source_text=sources["domain"],
                legacy_natural_texts=legacy_natural_texts,
                updated_at=timestamp,
            )
        )

    for item in catalog.get("specialized_functions") or []:
        function = deepcopy(dict(item))
        key = f"{function.get('function_id')}:{int(function.get('version') or 1)}"
        documents["domain"].append(
            _item_document(
                "domain",
                "specialized_functions",
                key,
                function,
                source_text=sources["domain"],
                legacy_natural_texts=legacy_natural_texts,
                updated_at=timestamp,
            )
        )

    documents["domain"].append(
        _item_document(
            "domain",
            "output_profile",
            "default",
            catalog.get("output_profile") or {},
            source_text=sources["domain"],
            legacy_natural_texts=legacy_natural_texts,
            updated_at=timestamp,
        )
    )

    datasets = catalog.get("datasets") if isinstance(catalog.get("datasets"), dict) else {}
    for key in sorted(datasets):
        payload = deepcopy(datasets[key])
        payload.pop("key", None)
        documents["table_catalog"].append(
            _item_document(
                "table_catalog",
                "datasets",
                key,
                payload,
                source_text=sources["table_catalog"],
                legacy_natural_texts=legacy_natural_texts,
                updated_at=timestamp,
            )
        )

    aliases = catalog.get("aliases") if isinstance(catalog.get("aliases"), dict) else {}
    for key in sorted(aliases):
        card = deepcopy(aliases[key])
        target = _ALIAS_PROVENANCE_TO_COLLECTION.get(str(card.get("provenance_source") or ""), "domain")
        documents[target].append(
            _item_document(
                target,
                "aliases",
                key,
                card,
                source_text=sources[target],
                legacy_natural_texts=legacy_natural_texts,
                updated_at=timestamp,
            )
        )

    return documents


def _validated_item(document: Mapping[str, Any], expected_prefix: str) -> dict[str, Any]:
    value = deepcopy(dict(document))
    unknown = set(value) - _ITEM_KEYS
    missing = _ITEM_KEYS - set(value)
    if unknown or missing:
        _fail(
            "메타데이터 항목 문서 형식이 올바르지 않습니다.",
            {"unknown": sorted(unknown), "missing": sorted(missing)},
        )
    section = str(value.get("section") or "").strip()
    key = str(value.get("key") or "").strip()
    if not section or not key or value.get("_id") != f"{expected_prefix}:{section}:{key}":
        _fail("메타데이터 항목 ID와 section/key가 일치하지 않습니다.", {"_id": value.get("_id")})
    if not isinstance(value.get("payload"), dict):
        _fail("메타데이터 항목 payload는 object여야 합니다.", {"_id": value.get("_id")})
    if not isinstance(value.get("natural_text"), str):
        _fail("메타데이터 자연어 입력은 문자열이어야 합니다.", {"_id": value.get("_id")})
    return value


def assemble_domain_package_from_items(
    documents: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    """Compile three simple item collections into the typed runtime package."""

    values = {
        kind: [_validated_item(item, kind) for item in documents.get(kind, [])]
        for kind in ("domain", "table_catalog", "main_filter")
    }
    profiles = [item for item in values["domain"] if item["section"] == "profile"]
    if len(profiles) != 1:
        _fail("도메인 프로필 항목은 정확히 하나여야 합니다.", {"profile_count": len(profiles)})
    profile = profiles[0]
    domain_id = str(profile["key"])
    profile_payload = deepcopy(profile["payload"])

    draft: dict[str, Any] = {
        "contract_version": "metadata.authoring.draft.v1",
        "display_name": str(profile_payload.get("display_name") or domain_id),
        "description": str(profile_payload.get("description") or ""),
        "locale": str(profile_payload.get("locale") or "ko-KR"),
        "timezone": str(profile_payload.get("timezone") or "Asia/Seoul"),
        "datasets": {},
        "metrics": {},
        "entity_groups": {},
        "grains": {},
        "relations": {},
        "orderings": {},
        "predicates": {},
        "recipes": {},
        "aliases": {},
        "prompt_extensions": {"intent": "", "answer": ""},
        "specialized_functions": [],
        "output_profile": {},
    }
    seen: set[tuple[str, str, str]] = set()
    for collection_kind, items in values.items():
        for item in items:
            marker = (collection_kind, item["section"], item["key"])
            if marker in seen:
                _fail("중복된 메타데이터 항목이 있습니다.", {"item": marker})
            seen.add(marker)
            section = item["section"]
            key = item["key"]
            payload = deepcopy(item["payload"])
            if collection_kind == "domain" and section in _DOMAIN_MAP_SECTIONS:
                draft[section][key] = payload
            elif collection_kind == "table_catalog" and section == "datasets":
                draft["datasets"][key] = payload
            elif section == "aliases":
                draft["aliases"][key] = payload
            elif collection_kind == "domain" and section == "prompt_extensions" and key in {"intent", "answer"}:
                draft["prompt_extensions"][key] = str(payload.get("text") or "")
            elif collection_kind == "domain" and section == "specialized_functions":
                draft["specialized_functions"].append(payload)
            elif collection_kind == "domain" and section == "output_profile" and key == "default":
                draft["output_profile"] = payload
            elif collection_kind == "domain" and section == "profile":
                continue
            else:
                _fail("지원하지 않는 메타데이터 항목 section입니다.", {"collection": collection_kind, "section": section, "key": key})

    if not draft["datasets"]:
        _fail("등록된 데이터셋 항목이 없습니다.")
    return compile_domain_package(
        draft,
        domain_id,
        "production",
        revision=1,
        lifecycle_status="active",
    )


def _find_items(collection: Any, session: Any = None) -> list[dict[str, Any]]:
    try:
        cursor = collection.find({}, session=session)
    except TypeError:
        cursor = collection.find()
    return [deepcopy(dict(item)) for item in cursor if isinstance(item, Mapping)]


def load_available_domain_package_from_three_collections(
    database: Any,
    *,
    domain_collection: str = DOMAIN_METADATA_COLLECTION,
    table_collection: str = TABLE_CATALOG_COLLECTION,
    main_filter_collection: str = MAIN_FILTER_COLLECTION,
    session: Any = None,
) -> dict[str, Any]:
    actual = _metadata_collection_names(domain_collection, table_collection, main_filter_collection)
    documents = {kind: _find_items(database[name], session=session) for kind, name in actual.items()}
    missing = [kind for kind, items in documents.items() if not items]
    if missing:
        _fail("필수 메타데이터 컬렉션에 등록 항목이 없습니다.", {"missing_collections": missing})
    return assemble_domain_package_from_items(documents)


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
    package = load_available_domain_package_from_three_collections(
        database,
        domain_collection=domain_collection,
        table_collection=table_collection,
        main_filter_collection=main_filter_collection,
        session=session,
    )
    if domain_id and package["domain_id"] != str(domain_id):
        _fail("요청한 도메인과 등록된 도메인 프로필이 다릅니다.")
    if environment and str(environment) != "production":
        _fail("항목형 메타데이터의 실행 환경은 production으로 고정됩니다.")
    return package


def replace_metadata_items(
    database: Any,
    documents: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    session: Any = None,
    domain_collection: str = DOMAIN_METADATA_COLLECTION,
    table_collection: str = TABLE_CATALOG_COLLECTION,
    main_filter_collection: str = MAIN_FILTER_COLLECTION,
) -> None:
    """Replace the three item sets after a complete in-memory compile check."""

    actual = _metadata_collection_names(domain_collection, table_collection, main_filter_collection)
    prepared = {
        kind: [_validated_item(item, kind) for item in documents.get(kind, [])]
        for kind in actual
    }
    assemble_domain_package_from_items(prepared)
    for kind, collection_name in actual.items():
        collection = database[collection_name]
        existing = {str(item.get("_id")): item for item in _find_items(collection, session=session)}
        items = []
        for source in prepared[kind]:
            document = deepcopy(source)
            if not document.get("natural_text") and isinstance(existing.get(document["_id"]), dict):
                document["natural_text"] = _clean_natural_text(existing[document["_id"]].get("natural_text"))
            items.append(document)
        ids = [item["_id"] for item in items]
        collection.delete_many({"_id": {"$nin": ids}}, session=session)
        for document in items:
            collection.replace_one(
                {"_id": document["_id"]},
                document,
                upsert=True,
                session=session,
            )


# Backward-compatible Python names.  Their behavior is item-oriented; no
# release document or persisted hash is produced.
make_metadata_section_documents = make_metadata_item_documents
replace_metadata_release = replace_metadata_items


def assemble_domain_package_from_sections(
    documents: Mapping[str, Sequence[Mapping[str, Any]]],
    domain_id: str = "",
    environment: str = "production",
) -> dict[str, Any]:
    package = assemble_domain_package_from_items(documents)
    if domain_id and package["domain_id"] != str(domain_id):
        _fail("요청한 도메인과 등록된 도메인 프로필이 다릅니다.")
    if environment and str(environment) != "production":
        _fail("항목형 메타데이터의 실행 환경은 production으로 고정됩니다.")
    return package


__all__ = [
    "DOMAIN_METADATA_COLLECTION",
    "MAIN_FILTER_COLLECTION",
    "METADATA_COLLECTIONS",
    "METADATA_RELEASE_VERSION",
    "METADATA_SECTION_VERSION",
    "TABLE_CATALOG_COLLECTION",
    "assemble_domain_package_from_items",
    "assemble_domain_package_from_sections",
    "load_available_domain_package_from_three_collections",
    "load_domain_package_from_three_collections",
    "make_metadata_item_documents",
    "make_metadata_section_documents",
    "replace_metadata_items",
    "replace_metadata_release",
]
