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
import unicodedata
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
_DOMAIN_ALIAS_TARGET_TYPES = {
    "metrics": "metric",
    "entity_groups": "entity_group",
    "grains": "grain",
    "relations": "relation",
    "predicates": "predicate",
    "recipes": "recipe",
}
_ALIAS_PROVENANCE_TO_COLLECTION = {
    "domain": "domain",
    "table_catalog": "table_catalog",
    "main_filters": "main_filter",
}
_DUPLICATE_POLICY_VERSION = "metadata.duplicate-policy.v1"
_DUPLICATE_OPERATION_LIMIT = 64
_DUPLICATE_CANDIDATE_LIMIT = 8
_DUPLICATE_CONFLICT_LIMIT = 32
_DOMAIN_SECTION_ID_FIELDS = {
    "metrics": "metric_id",
    "entity_groups": "group_id",
    "grains": "grain_id",
    "relations": "relation_id",
    "orderings": "ordering_id",
    "predicates": "predicate_id",
    "recipes": "recipe_id",
}
_GENERIC_DISPLAY_NAMES = {"default", "unknown", "기본", "기타", "미정", "항목"}
_NUMERIC_METRIC_TYPES = {
    "number",
    "integer",
    "decimal",
    "float",
    "quantity",
    "currency",
    "rate",
    "percent",
    "percentage",
}


def _fail(message: str, details: Mapping[str, Any] | None = None) -> None:
    raise ContractError(
        "metadata_dependency_error",
        "metadata_three_collection",
        message,
        deepcopy(dict(details or {})),
    )


def _duplicate_text(value: Any) -> str:
    """Normalize identifiers conservatively for duplicate comparison only."""

    normalized = unicodedata.normalize("NFKC", str(value or ""))
    return " ".join(normalized.strip().split()).casefold()


def _duplicate_string_values(value: Any) -> set[str]:
    values: list[Any]
    if isinstance(value, (list, tuple)):
        values = list(value)
    else:
        values = [value]
    result: set[str] = set()
    for raw in values:
        if isinstance(raw, Mapping):
            raw = raw.get("text")
        marker = _duplicate_text(raw)
        if marker:
            result.add(marker)
    return result


def _alias_payload_target(payload: Mapping[str, Any]) -> tuple[str, str]:
    return (
        _duplicate_text(payload.get("target_type")),
        _duplicate_text(payload.get("target_key")),
    )


def _alias_payload_expressions(payload: Mapping[str, Any]) -> set[str]:
    values = payload.get("values")
    if not isinstance(values, list):
        values = payload.get("aliases")
    return _duplicate_string_values(values)


def _natural_field_aliases(
    source_text: str,
    field_id: str,
    physical_column: str,
) -> list[str]:
    """Extract only worker-declared field meanings from item natural text.

    This intentionally narrow grammar never invents domain words. It accepts
    labels only from sentences such as ``PRODUCTION 컬럼 ... 이 값은
    생산량이야`` where the physical or canonical field is named explicitly.
    """

    text = str(source_text or "")
    names = {
        str(field_id or "").strip().casefold(),
        str(physical_column or "").strip().casefold(),
    }
    names.discard("")
    result: list[str] = []
    # Match each known field independently. A single broad ``field ... value``
    # expression can otherwise consume an earlier DATE/WORK_DT mention and hide
    # the later metric declaration in the same worker-authored paragraph.
    for name in sorted(names, key=len, reverse=True):
        pattern = re.compile(
            rf"(?<![A-Za-z0-9_.-]){re.escape(name)}(?![A-Za-z0-9_.-])\s*컬럼"
            r".{0,120}?(?:이\s*값|해당\s*값|그\s*값)\s*(?:은|는)\s*"
            r"(?P<label>[가-힣A-Za-z][가-힣A-Za-z0-9 _./-]{0,39}?)"
            r"(?=\s*(?:이야|야|입니다|이다|을\s*의미|를\s*의미))",
            re.IGNORECASE | re.DOTALL,
        )
        for match in pattern.finditer(text):
            label = " ".join(str(match.group("label") or "").strip().split())
            if label and label not in result:
                result.append(label)
    return result


def _enrich_dataset_item_payload(
    payload: Mapping[str, Any],
    natural_text: str,
) -> dict[str, Any]:
    """Normalize metric-capable fields without trusting provider variability."""

    dataset = deepcopy(dict(payload))
    raw_fields = dataset.get("fields")
    if not isinstance(raw_fields, Mapping):
        return dataset
    fields: dict[str, Any] = {}
    for field_id, raw_binding in raw_fields.items():
        binding = deepcopy(dict(raw_binding)) if isinstance(raw_binding, Mapping) else raw_binding
        if not isinstance(binding, dict):
            fields[str(field_id)] = binding
            continue
        aliases = [str(value).strip() for value in binding.get("aliases") or [] if str(value).strip()]
        declared_aliases = _natural_field_aliases(
            natural_text,
            str(field_id),
            str(binding.get("physical_column") or ""),
        )
        for alias in declared_aliases:
            if alias not in aliases:
                aliases.append(alias)
        if aliases:
            binding["aliases"] = aliases
        semantic_type = str(binding.get("semantic_type") or "").casefold()
        if declared_aliases and semantic_type in _NUMERIC_METRIC_TYPES:
            roles = [str(value) for value in binding.get("roles") or [] if str(value)]
            for role in ("aggregate", "metric", "output"):
                if role not in roles:
                    roles.append(role)
            binding["roles"] = roles
        fields[str(field_id)] = binding
    dataset["fields"] = fields

    parameters = deepcopy(dict(dataset.get("parameters") or {}))
    for name, raw_spec in list(parameters.items()):
        spec = deepcopy(dict(raw_spec)) if isinstance(raw_spec, Mapping) else {}
        binding = fields.get(str(name))
        semantic_type = (
            str(binding.get("semantic_type") or "").casefold()
            if isinstance(binding, Mapping)
            else ""
        )
        if semantic_type in {"localdate", "date"}:
            # Query placeholders bound to canonical date fields are dates even
            # when a smaller authoring model emitted the generic string type.
            spec["type"] = "LocalDate"
            compact_pattern = re.compile(
                rf"(?<![A-Za-z0-9_]){re.escape(str(name))}(?![A-Za-z0-9_])"
                r".{0,80}?YYYYMMDD\s*형식",
                re.IGNORECASE | re.DOTALL,
            )
            dashed_pattern = re.compile(
                rf"(?<![A-Za-z0-9_]){re.escape(str(name))}(?![A-Za-z0-9_])"
                r".{0,80}?YYYY-MM-DD\s*형식",
                re.IGNORECASE | re.DOTALL,
            )
            if compact_pattern.search(str(natural_text or "")):
                spec["format"] = "YYYYMMDD"
            elif dashed_pattern.search(str(natural_text or "")):
                spec["format"] = "YYYY-MM-DD"
        parameters[str(name)] = spec
    if parameters:
        dataset["parameters"] = parameters

    if not isinstance(dataset.get("date_policy"), Mapping):
        for name, spec in parameters.items():
            binding = fields.get(str(name))
            semantic_type = (
                str(binding.get("semantic_type") or "").casefold()
                if isinstance(binding, Mapping)
                else ""
            )
            if semantic_type in {"localdate", "date"} and str(spec.get("type") or "").casefold() in {"localdate", "date"}:
                dataset["date_policy"] = {
                    "field": str(name),
                    "inclusive_start": True,
                    "inclusive_end": True,
                    "timezone": "Asia/Seoul",
                }
                break
    return dataset


def _synthesize_dataset_metrics(draft: dict[str, Any]) -> None:
    """Create safe additive metrics from metric-role dataset fields.

    A metric is synthesized only when exactly one dataset family owns the
    canonical field and every dataset in that family exposes the same numeric
    field. Explicit domain metrics always win.
    """

    datasets = draft.get("datasets") if isinstance(draft.get("datasets"), dict) else {}
    explicit_metrics = draft.get("metrics") if isinstance(draft.get("metrics"), dict) else {}
    families: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for dataset_key, raw_dataset in datasets.items():
        if not isinstance(raw_dataset, Mapping):
            continue
        dataset = raw_dataset if isinstance(raw_dataset, dict) else dict(raw_dataset)
        family = str(dataset.get("family") or dataset_key)
        families.setdefault(family, []).append((str(dataset_key), dataset))

    candidates: dict[str, list[tuple[str, list[dict[str, Any]]]]] = {}
    for family, family_datasets in families.items():
        field_sets = [set(dict(dataset.get("fields") or {})) for _key, dataset in family_datasets]
        common_fields = set.intersection(*field_sets) if field_sets else set()
        for field_id in sorted(common_fields):
            bindings = [dict(dataset.get("fields") or {})[field_id] for _key, dataset in family_datasets]
            if not all(str(binding.get("semantic_type") or "").casefold() in _NUMERIC_METRIC_TYPES for binding in bindings):
                continue
            if not any(set(binding.get("roles") or []) & {"aggregate", "metric"} for binding in bindings):
                continue
            if not any(binding.get("aliases") for binding in bindings):
                continue
            candidates.setdefault(field_id, []).append((family, bindings))

    for field_id, owners in sorted(candidates.items()):
        if field_id in explicit_metrics or len(owners) != 1:
            continue
        family, bindings = owners[0]
        aliases: list[str] = []
        units = {
            str(binding.get("unit") or "").strip()
            for binding in bindings
            if str(binding.get("unit") or "").strip()
        }
        for binding in bindings:
            roles = [str(value) for value in binding.get("roles") or [] if str(value)]
            for role in ("aggregate", "metric", "output"):
                if role not in roles:
                    roles.append(role)
            binding["roles"] = roles
            for alias in binding.get("aliases") or []:
                value = str(alias).strip()
                if value and value not in aliases:
                    aliases.append(value)
        metric = {
            "aliases": aliases,
            "source_binding": {"dataset_family": family, "field": field_id},
            "additivity": {"default": "additive", "allowed_rollups": ["sum"]},
            "null_policy": "exclude_from_sum",
            "zero_policy": "preserve_zero",
            "value_type": "number",
        }
        if len(units) == 1:
            metric["unit"] = next(iter(units))
        explicit_metrics[field_id] = metric
    draft["metrics"] = explicit_metrics


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


def make_partial_metadata_item_documents(
    authoring_kind: str,
    patch: Mapping[str, Any],
    source_text: str,
    *,
    updated_at: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Convert one independently authored section into normal item documents.

    Initial authoring is intentionally order-independent.  Domain, main-filter,
    and dataset items may therefore be stored before the other sections exist.  The
    documents use the exact same six-field shape as fully compiled metadata;
    once all three collections are populated the normal package assembler is
    the only activation gate.
    """

    kind = str(authoring_kind or "").strip().casefold()
    if kind not in {"domain", "dataset", "main_filter"}:
        _fail("부분 메타데이터 항목으로 저장할 수 없는 등록 유형입니다.", {"authoring_kind": kind})
    if not isinstance(patch, Mapping):
        _fail("부분 메타데이터 patch는 object여야 합니다.", {"authoring_kind": kind})

    timestamp = str(updated_at or datetime.now(timezone.utc).isoformat())
    documents: dict[str, list[dict[str, Any]]] = {
        "domain": [],
        "table_catalog": [],
        "main_filter": [],
    }
    if kind == "domain":
        profile_keys = {"domain_id", "display_name", "description", "locale", "timezone"}
        allowed = {*profile_keys, *_DOMAIN_MAP_SECTIONS}
        if not set(patch) <= allowed or not patch:
            _fail("도메인 등록 patch에 허용되지 않은 section이 있습니다.")
        section_keys = set(patch) & set(_DOMAIN_MAP_SECTIONS)
        if section_keys:
            if set(patch) != section_keys:
                _fail("도메인 프로필과 업무 항목 section은 한 번에 섞어 저장할 수 없습니다.")
            for section in sorted(section_keys):
                entries = patch.get(section)
                if not isinstance(entries, Mapping) or not entries:
                    _fail("도메인 section은 비어 있지 않은 항목 object여야 합니다.", {"section": section})
                for key in sorted(entries):
                    raw_payload = entries[key]
                    if not isinstance(raw_payload, Mapping):
                        _fail("도메인 항목 payload는 object여야 합니다.", {"section": section, "key": str(key)})
                    payload = deepcopy(dict(raw_payload))
                    if section == "entity_groups":
                        required = {"group_id", "display_name", "target_field", "members", "aliases"}
                        if set(payload) != required:
                            _fail(
                                "공정 그룹에는 group_id, display_name, target_field, members, aliases만 필요합니다.",
                                {"key": str(key), "missing": sorted(required - set(payload)), "unknown": sorted(set(payload) - required)},
                            )
                        group_id = str(payload.get("group_id") or "").strip()
                        target_field = str(payload.get("target_field") or "").strip()
                        display_name = str(payload.get("display_name") or "").strip()
                        members = [str(value).strip() for value in payload.get("members") or []]
                        aliases = [str(value).strip() for value in payload.get("aliases") or []]
                        safe_id = r"[A-Za-z][A-Za-z0-9_.-]{0,127}"
                        if (
                            re.fullmatch(safe_id, str(key)) is None
                            or group_id != str(key)
                            or re.fullmatch(safe_id, group_id) is None
                            or re.fullmatch(safe_id, target_field) is None
                            or not display_name or not members or not aliases
                            or any(not value for value in members + aliases)
                            or len(members) != len(set(members))
                            or len(aliases) != len(set(aliases))
                        ):
                            _fail("공정 그룹 식별자, 대상 필드, 구성원 또는 별칭이 올바르지 않습니다.", {"key": str(key)})
                        payload = {
                            "group_id": group_id,
                            "display_name": display_name,
                            "target_field": target_field,
                            "expansion": "closed_set",
                            "members": members,
                            "selection": {"operator": "in", "value": members},
                            "aliases": aliases,
                            "alias_policy": {"match": "bounded_longest", "conflict": "fail_ambiguous"},
                            "legacy_identity": f"process_group.{group_id}",
                        }
                    documents["domain"].append(
                        _item_document(
                            "domain", section, str(key), payload,
                            source_text=str(source_text or ""), legacy_natural_texts=None,
                            updated_at=timestamp,
                        )
                    )
                    alias_target_type = _DOMAIN_ALIAS_TARGET_TYPES.get(section)
                    alias_values = (
                        payload.get("aliases")
                        if isinstance(payload.get("aliases"), list)
                        else []
                    )
                    alias_values = list(dict.fromkeys(
                        str(value).strip()
                        for value in alias_values
                        if str(value).strip()
                    ))
                    if alias_target_type and alias_values:
                        alias_key = f"{alias_target_type}:{key}"
                        alias_payload = {
                            "target_type": alias_target_type,
                            "target_key": str(key),
                            "values": [{"text": value, "priority": 100} for value in alias_values],
                            "normalization": ["unicode_nfkc", "trim", "collapse_space", "latin_casefold"],
                            "match": "bounded_longest",
                            "conflict": "fail_ambiguous",
                            "provenance_source": "domain",
                        }
                        documents["domain"].append(
                            _item_document(
                                "domain", "aliases", alias_key, alias_payload,
                                source_text=str(source_text or ""), legacy_natural_texts=None,
                                updated_at=timestamp,
                            )
                        )
        else:
            if not set(patch) <= profile_keys or not str(patch.get("display_name") or "").strip():
                _fail("도메인 프로필에는 표시 이름과 선택적인 설명·언어·시간대만 허용합니다.")
            domain_id = str(patch.get("domain_id") or "default").strip()
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,127}", domain_id) is None:
                _fail("자동 생성된 도메인 식별자가 올바르지 않습니다.")
            payload = {
                "display_name": str(patch.get("display_name") or domain_id).strip(),
                "description": str(patch.get("description") or "").strip(),
                "locale": str(patch.get("locale") or "ko-KR").strip(),
                "timezone": str(patch.get("timezone") or "Asia/Seoul").strip(),
            }
            documents["domain"].append(
                _item_document(
                    "domain", "profile", domain_id, payload,
                    source_text=str(source_text or ""), legacy_natural_texts=None,
                    updated_at=timestamp,
                )
            )
    elif kind == "dataset":
        if set(patch) != {"datasets"} or not isinstance(patch.get("datasets"), Mapping) or not patch["datasets"]:
            _fail("최초 데이터셋 등록 patch에는 비어 있지 않은 datasets만 있어야 합니다.")
        for key in sorted(patch["datasets"]):
            payload = deepcopy(patch["datasets"][key])
            if not isinstance(payload, Mapping):
                _fail("데이터셋 항목 payload는 object여야 합니다.", {"key": str(key)})
            payload = deepcopy(dict(payload))
            payload.pop("key", None)
            fields = payload.get("fields")
            if not isinstance(fields, Mapping) or not fields:
                _fail("데이터셋 항목에는 비어 있지 않은 fields가 필요합니다.", {"key": str(key)})
            documents["table_catalog"].append(
                _item_document(
                    "table_catalog",
                    "datasets",
                    str(key),
                    payload,
                    source_text=str(source_text or ""),
                    legacy_natural_texts=None,
                    updated_at=timestamp,
                )
            )
    else:
        if set(patch) != {"aliases"} or not isinstance(patch.get("aliases"), Mapping) or not patch["aliases"]:
            _fail("최초 메인 필터 등록 patch에는 비어 있지 않은 aliases만 있어야 합니다.")
        for key in sorted(patch["aliases"]):
            raw_payload = patch["aliases"][key]
            if not isinstance(raw_payload, Mapping):
                _fail("메인 필터 alias payload는 object여야 합니다.", {"key": str(key)})
            payload = deepcopy(dict(raw_payload))
            target_type, target_key = _alias_payload_target(payload)
            expressions = _alias_payload_expressions(payload)
            expected_key = f"{target_type}:{target_key}" if target_type and target_key else ""
            if not expected_key or _duplicate_text(key) != _duplicate_text(expected_key) or not expressions:
                _fail(
                    "메인 필터 alias의 key, target 또는 표현식이 완전하지 않습니다.",
                    {"key": str(key)},
                )
            # Collection ownership is a storage concern.  Natural authoring
            # evidence remains in ``natural_text``; the runtime provenance must
            # identify this card as a Main Filter item so later full-package
            # projections keep it in the same collection.
            payload["provenance_source"] = "main_filters"
            documents["main_filter"].append(
                _item_document(
                    "main_filter",
                    "aliases",
                    str(key),
                    payload,
                    source_text=str(source_text or ""),
                    legacy_natural_texts=None,
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
    *,
    alias_activation_out: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile three simple item collections into the typed runtime package."""

    values = {
        kind: [_validated_item(item, kind) for item in documents.get(kind, [])]
        for kind in ("domain", "table_catalog", "main_filter")
    }
    profiles = [item for item in values["domain"] if item["section"] == "profile"]
    if len(profiles) > 1:
        _fail("도메인 프로필 항목은 최대 하나여야 합니다.", {"profile_count": len(profiles)})
    # 작업자는 공정 그룹 같은 업무 항목부터 자유롭게 등록할 수 있다.
    # 별도 프로필이 없으면 저장 문서를 늘리지 않고 실행 번들 결합 시에만
    # 서울 시간대의 기본 프로필을 적용한다.
    profile = profiles[0] if profiles else {
        "key": "default",
        "payload": {
            "display_name": "Default Domain",
            "description": "",
            "locale": "ko-KR",
            "timezone": "Asia/Seoul",
        },
    }
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
    alias_owners: dict[str, tuple[str, str]] = {}
    alias_target_owners: dict[tuple[str, str], tuple[str, str]] = {}
    alias_expression_owners: dict[tuple[str, str], tuple[str, str, str]] = {}
    for collection_kind, items in values.items():
        for item in items:
            marker = (collection_kind, item["section"], item["key"])
            if marker in seen:
                _fail("중복된 메타데이터 항목이 있습니다.", {"item": marker})
            seen.add(marker)
            section = item["section"]
            key = item["key"]
            payload = deepcopy(item["payload"])
            if collection_kind == "table_catalog" and section == "datasets":
                payload = _enrich_dataset_item_payload(payload, item["natural_text"])
            if section == "aliases":
                alias_marker = _duplicate_text(key)
                previous_owner = alias_owners.get(alias_marker)
                if previous_owner is not None:
                    _fail(
                        "정규화한 같은 alias key가 메타데이터 전역에 둘 이상 등록되어 있습니다.",
                        {
                            "alias_key": key,
                            "current_collection": collection_kind,
                            "previous_collection": previous_owner[0],
                            "previous_key": previous_owner[1],
                            "reason": "cross_collection_alias_duplicate",
                        },
                    )
                alias_owners[alias_marker] = (collection_kind, key)
                target_type, target_key = _alias_payload_target(payload)
                if not target_type or not target_key:
                    _fail(
                        "alias card의 target_type과 target_key가 비어 있습니다.",
                        {"collection": collection_kind, "key": key},
                    )
                target_marker = (target_type, target_key)
                previous_target_owner = alias_target_owners.get(target_marker)
                if previous_target_owner is not None:
                    _fail(
                        "같은 alias target이 여러 card에 등록되어 있습니다.",
                        {
                            "collection": collection_kind,
                            "key": key,
                            "previous_collection": previous_target_owner[0],
                            "previous_key": previous_target_owner[1],
                            "reason": "global_alias_target_duplicate",
                        },
                    )
                alias_target_owners[target_marker] = (collection_kind, key)
                for expression in _alias_payload_expressions(payload):
                    expression_marker = (target_type, expression)
                    previous_expression_owner = alias_expression_owners.get(
                        expression_marker
                    )
                    if (
                        previous_expression_owner is not None
                        and previous_expression_owner[0] != target_key
                    ):
                        _fail(
                            "같은 target_type의 alias 표현이 여러 target을 가리킵니다.",
                            {
                                "collection": collection_kind,
                                "key": key,
                                "previous_collection": previous_expression_owner[1],
                                "previous_key": previous_expression_owner[2],
                                "reason": "global_alias_expression_ambiguous",
                            },
                        )
                    alias_expression_owners[expression_marker] = (
                        target_key,
                        collection_kind,
                        key,
                    )
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

    _synthesize_dataset_metrics(draft)

    if not draft["datasets"]:
        _fail("등록된 데이터셋 항목이 없습니다.")

    # Main Filter는 대응 데이터셋보다 먼저 등록할 수 있다. 현재 dataset
    # catalog에 target이 없는 alias를 잘못된 값으로 간주해 버리면, 전혀
    # 관계없는 Domain 항목을 추가하는 순간 전체 저장이 막힌다. 저장된
    # alias card는 보존하되 현재 runtime에서 실제 target이 존재하는
    # card만 활성화하고, 나머지는 향후 dataset 등록까지 대기시킨다.
    registered_fields = {
        _duplicate_text(field_id)
        for dataset in draft["datasets"].values()
        if isinstance(dataset, Mapping)
        for field_id in (dataset.get("fields") or {})
    }
    registries = {
        "dataset": {_duplicate_text(value) for value in draft["datasets"]},
        "field": registered_fields,
        "metric": {_duplicate_text(value) for value in draft["metrics"]},
        "relation": {_duplicate_text(value) for value in draft["relations"]},
        "grain": {_duplicate_text(value) for value in draft["grains"]},
        "predicate": {_duplicate_text(value) for value in draft["predicates"]},
        "recipe": {_duplicate_text(value) for value in draft["recipes"]},
        "entity_group": {_duplicate_text(value) for value in draft["entity_groups"]},
    }
    active_aliases: dict[str, Any] = {}
    deferred_aliases: list[dict[str, str]] = []
    for alias_id, payload in draft["aliases"].items():
        target_type, target_key = _alias_payload_target(payload)
        registered = registries.get(target_type)
        if registered is not None and target_key not in registered:
            deferred_aliases.append(
                {
                    "alias_id": str(alias_id),
                    "target_type": str(payload.get("target_type") or "").strip(),
                    "target_key": str(payload.get("target_key") or "").strip(),
                }
            )
            continue
        active_aliases[str(alias_id)] = payload
    draft["aliases"] = active_aliases
    if isinstance(alias_activation_out, dict):
        alias_activation_out.clear()
        alias_activation_out.update(
            {
                "contract_version": "metadata.alias-activation.v1",
                "active_count": len(active_aliases),
                "deferred_count": len(deferred_aliases),
                "deferred": deferred_aliases,
            }
        )
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


def _alias_target(item: Mapping[str, Any]) -> tuple[str, str]:
    payload = item.get("payload") if isinstance(item.get("payload"), Mapping) else {}
    return _alias_payload_target(payload)


def _alias_expressions(item: Mapping[str, Any]) -> set[str]:
    payload = item.get("payload") if isinstance(item.get("payload"), Mapping) else {}
    return _alias_payload_expressions(payload)


def _dataset_query_ref(item: Mapping[str, Any]) -> str:
    payload = item.get("payload") if isinstance(item.get("payload"), Mapping) else {}
    return _duplicate_text(payload.get("query_ref"))


def _dataset_source_descriptor(item: Mapping[str, Any]) -> str:
    """Return an in-memory physical-source descriptor without changing SQL.

    Query text, including comments and Oracle optimizer hints, is compared as
    an exact value.  ``config_ref`` is included only as part of the complete
    descriptor and can never identify a duplicate by itself.
    """

    payload = item.get("payload") if isinstance(item.get("payload"), Mapping) else {}
    source_config = (
        deepcopy(dict(payload.get("source_config")))
        if isinstance(payload.get("source_config"), Mapping)
        else {}
    )
    location_keys = (
        "query_template",
        "path",
        "uri",
        "url",
        "endpoint",
        "table",
        "table_name",
        "document_id",
        "dataset_id",
        "object_name",
        "resource",
    )
    has_location = any(
        str(source_config.get(name) or payload.get(name) or "").strip()
        for name in location_keys
    )
    if not has_location:
        return ""
    descriptor = {
        "source_type": _duplicate_text(
            payload.get("source_type") or source_config.get("source_type")
        ),
        "source_adapter": _duplicate_text(
            payload.get("source_adapter")
            or payload.get("source_type")
            or source_config.get("source_type")
        ),
        "config_ref": _duplicate_text(payload.get("config_ref")),
        "source_config": source_config,
        "parameters": deepcopy(
            payload.get("parameters")
            or payload.get("parameter_contract")
            or source_config.get("required_params")
            or []
        ),
        "fields": deepcopy(payload.get("fields") or {}),
        "time_scope": deepcopy(payload.get("time_scope") or {}),
    }
    return json.dumps(
        descriptor,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _semantic_duplicate_match(
    collection_kind: str,
    candidate: Mapping[str, Any],
    existing: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Return safe evidence for a strong semantic duplicate candidate."""

    if str(candidate.get("section")) != str(existing.get("section")):
        return None
    section = str(candidate.get("section") or "")
    if _duplicate_text(candidate.get("key")) == _duplicate_text(existing.get("key")):
        return {"match_type": "normalized_key", "evidence": ["normalized_key"]}

    if section == "aliases":
        candidate_type, candidate_target = _alias_target(candidate)
        existing_type, existing_target = _alias_target(existing)
        if not candidate_type or candidate_type != existing_type:
            return None
        if candidate_target and candidate_target == existing_target:
            return {"match_type": "alias_target", "evidence": ["same_alias_target"]}
        overlap = _alias_expressions(candidate) & _alias_expressions(existing)
        if overlap:
            return {
                "match_type": "ambiguous_alias_target",
                "evidence": ["alias_expression_overlap"],
            }
        return None

    if collection_kind == "table_catalog" and section == "datasets":
        candidate_query_ref = _dataset_query_ref(candidate)
        existing_query_ref = _dataset_query_ref(existing)
        if candidate_query_ref and candidate_query_ref == existing_query_ref:
            return {"match_type": "query_ref", "evidence": ["same_query_ref"]}
        candidate_descriptor = _dataset_source_descriptor(candidate)
        existing_descriptor = _dataset_source_descriptor(existing)
        if candidate_descriptor and candidate_descriptor == existing_descriptor:
            return {
                "match_type": "source_descriptor",
                "evidence": ["same_source_descriptor"],
            }
        return None

    if collection_kind == "domain" and section in _DOMAIN_MAP_SECTIONS:
        candidate_payload = (
            candidate.get("payload") if isinstance(candidate.get("payload"), Mapping) else {}
        )
        existing_payload = (
            existing.get("payload") if isinstance(existing.get("payload"), Mapping) else {}
        )
        identity_field = _DOMAIN_SECTION_ID_FIELDS.get(section)
        if identity_field:
            candidate_identity = _duplicate_text(candidate_payload.get(identity_field))
            existing_identities = {
                _duplicate_text(existing.get("key")),
                _duplicate_text(existing_payload.get(identity_field)),
            }
            if candidate_identity and candidate_identity in existing_identities:
                return {
                    "match_type": "typed_identity",
                    "evidence": ["same_typed_identity"],
                }
        candidate_legacy = _duplicate_text(candidate_payload.get("legacy_identity"))
        existing_legacy = _duplicate_text(existing_payload.get("legacy_identity"))
        if candidate_legacy and candidate_legacy == existing_legacy:
            return {
                "match_type": "legacy_identity",
                "evidence": ["same_legacy_identity"],
            }
        candidate_display = _duplicate_text(candidate_payload.get("display_name"))
        existing_display = _duplicate_text(existing_payload.get("display_name"))
        if (
            candidate_display
            and candidate_display not in _GENERIC_DISPLAY_NAMES
            and candidate_display == existing_display
        ):
            return {
                "match_type": "display_name",
                "evidence": ["same_section_display_name"],
            }
        alias_overlap = _duplicate_string_values(candidate_payload.get("aliases")) & _duplicate_string_values(
            existing_payload.get("aliases")
        )
        if alias_overlap:
            return {"match_type": "section_alias", "evidence": ["same_section_alias"]}
        return None

    if collection_kind == "domain" and section == "specialized_functions":
        candidate_payload = (
            candidate.get("payload") if isinstance(candidate.get("payload"), Mapping) else {}
        )
        existing_payload = (
            existing.get("payload") if isinstance(existing.get("payload"), Mapping) else {}
        )
        candidate_identity = (
            _duplicate_text(candidate_payload.get("function_id")),
            int(candidate_payload.get("version") or 1),
        )
        existing_identity = (
            _duplicate_text(existing_payload.get("function_id")),
            int(existing_payload.get("version") or 1),
        )
        if candidate_identity[0] and candidate_identity == existing_identity:
            return {
                "match_type": "specialized_function_identity",
                "evidence": ["same_function_id_and_version"],
            }
    return None


def metadata_item_set_projection(
    documents: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """Return a deterministic full-item snapshot for transaction conflict checks."""

    return {
        collection_kind: sorted(
            (
                _validated_item(item, collection_kind)
                for item in documents.get(collection_kind, [])
            ),
            key=lambda item: str(item["_id"]),
        )
        for collection_kind in ("domain", "table_catalog", "main_filter")
    }


def merge_metadata_items_for_write(
    current_documents: Mapping[str, Sequence[Mapping[str, Any]]],
    candidate_documents: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    mode: str,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Resolve exact and semantic duplicates without LLM calls or new storage.

    ``natural_text`` is deliberately excluded from identity decisions.  The
    resolver compares only typed payloads in the same collection and section,
    preserves every unmentioned item, and blocks ambiguous or cross-key
    replacements so typed references cannot be silently broken.
    """

    write_mode = str(mode or "").strip()
    if write_mode not in {"save", "replace", "validate_only"}:
        raise ValueError("metadata write mode must be save, replace, or validate_only")

    collection_kinds = ("domain", "table_catalog", "main_filter")
    validated_current = {
        collection_kind: [
            _validated_item(item, collection_kind)
            for item in current_documents.get(collection_kind, [])
        ]
        for collection_kind in collection_kinds
    }
    validated_candidates = {
        collection_kind: [
            _validated_item(item, collection_kind)
            for item in candidate_documents.get(collection_kind, [])
        ]
        for collection_kind in collection_kinds
    }
    current_by_collection = {
        collection_kind: {
            str(item["_id"]): item for item in validated_current[collection_kind]
        }
        for collection_kind in collection_kinds
    }
    global_existing_aliases = [
        (collection_kind, item)
        for collection_kind in collection_kinds
        for item in validated_current[collection_kind]
        if item["section"] == "aliases"
    ]
    global_changed_candidate_aliases = [
        (collection_kind, item)
        for collection_kind in collection_kinds
        for item in validated_candidates[collection_kind]
        if item["section"] == "aliases"
        and (
            str(item["_id"]) not in current_by_collection[collection_kind]
            or current_by_collection[collection_kind][str(item["_id"])]["payload"]
            != item["payload"]
        )
    ]

    merged: dict[str, list[dict[str, Any]]] = {}
    operations: dict[str, Any] = {
        "policy_version": _DUPLICATE_POLICY_VERSION,
        "identity": "typed_item_identity",
        "inserted": 0,
        "replaced": 0,
        "unchanged": 0,
        "conflict_count": 0,
        "conflicts": [],
    }
    important_operation_records: list[dict[str, Any]] = []
    unchanged_operation_records: list[dict[str, Any]] = []
    operation_record_count = 0

    def record(
        item: Mapping[str, Any],
        collection_kind: str,
        operation: str,
        reason: str,
        *,
        canonical_key: str = "",
    ) -> None:
        nonlocal operation_record_count
        operation_record_count += 1
        value = {
            "collection": collection_kind,
            "section": str(item.get("section") or ""),
            "key": str(item.get("key") or ""),
            "operation": operation,
            "reason": reason,
        }
        if canonical_key:
            value["canonical_key"] = canonical_key
        target = (
            unchanged_operation_records
            if operation == "unchanged"
            else important_operation_records
        )
        if len(target) < _DUPLICATE_OPERATION_LIMIT:
            target.append(value)

    def conflict(
        item: Mapping[str, Any],
        collection_kind: str,
        reason: str,
        matches: Sequence[tuple[Mapping[str, Any], Mapping[str, Any], str]],
    ) -> None:
        unique_candidates: list[dict[str, str]] = []
        seen_candidates: set[tuple[str, str, str]] = set()
        evidence: list[str] = []
        match_types: list[str] = []
        for matched_item, match, source in matches:
            matched_collection = str(matched_item.get("_id") or "").split(":", 1)[0]
            marker = (
                matched_collection,
                str(matched_item.get("section") or ""),
                str(matched_item.get("key") or ""),
            )
            if marker not in seen_candidates and len(unique_candidates) < _DUPLICATE_CANDIDATE_LIMIT:
                seen_candidates.add(marker)
                unique_candidates.append(
                    {
                        "collection": marker[0],
                        "section": marker[1],
                        "key": marker[2],
                        "source": source,
                    }
                )
            match_types.append(str(match.get("match_type") or "semantic"))
            evidence.extend(str(value) for value in match.get("evidence") or [])
        details: dict[str, Any] = {
            "collection": collection_kind,
            "section": str(item.get("section") or ""),
            "key": str(item.get("key") or ""),
            "reason": reason,
            "resolution": "blocked",
            "match_types": list(dict.fromkeys(match_types)),
            "evidence": list(dict.fromkeys(evidence)),
            "duplicate_candidates": unique_candidates,
        }
        if (
            len(unique_candidates) == 1
            and unique_candidates[0]["source"].startswith("existing")
        ):
            details["canonical_key"] = unique_candidates[0]["key"]
        operations["conflict_count"] += 1
        if len(operations["conflicts"]) < _DUPLICATE_CONFLICT_LIMIT:
            operations["conflicts"].append(details)
        record(
            item,
            collection_kind,
            "blocked",
            reason,
            canonical_key=str(details.get("canonical_key") or ""),
        )

    for collection_kind in collection_kinds:
        existing_by_id = current_by_collection[collection_kind]
        merged_by_id = deepcopy(existing_by_id)
        candidate_by_id: dict[str, dict[str, Any]] = {}
        duplicate_candidate_ids: set[str] = set()
        for candidate in validated_candidates[collection_kind]:
            candidate_id = str(candidate["_id"])
            if candidate_id in candidate_by_id:
                duplicate_candidate_ids.add(candidate_id)
                continue
            candidate_by_id[candidate_id] = candidate

        changed_candidates = {
            candidate_id: candidate
            for candidate_id, candidate in candidate_by_id.items()
            if candidate_id not in existing_by_id
            or existing_by_id[candidate_id]["payload"] != candidate["payload"]
        }
        for candidate_id in sorted(candidate_by_id):
            candidate = candidate_by_id[candidate_id]
            if candidate_id in duplicate_candidate_ids:
                conflict(candidate, collection_kind, "duplicate_candidate_id", [])
                continue
            existing = existing_by_id.get(candidate_id)
            unchanged = bool(
                existing is not None
                and existing["section"] == candidate["section"]
                and existing["key"] == candidate["key"]
                and existing["payload"] == candidate["payload"]
            )
            if unchanged:
                operations["unchanged"] += 1
                record(candidate, collection_kind, "unchanged", "exact_payload_replay")
                continue
            if existing is not None and write_mode == "save":
                conflict(
                    candidate,
                    collection_kind,
                    "exact_key_changed",
                    [(existing, {"match_type": "exact_key", "evidence": ["same_exact_key"]}, "existing")],
                )
                continue

            semantic_matches: list[tuple[Mapping[str, Any], Mapping[str, Any], str]] = []
            for existing_id, existing_item in existing_by_id.items():
                if existing_id == candidate_id:
                    continue
                match = _semantic_duplicate_match(collection_kind, candidate, existing_item)
                if match:
                    semantic_matches.append((existing_item, match, "existing"))
            if candidate["section"] == "aliases":
                for other_collection, existing_item in global_existing_aliases:
                    if other_collection == collection_kind:
                        continue
                    match = _semantic_duplicate_match(
                        collection_kind, candidate, existing_item
                    )
                    if match:
                        semantic_matches.append(
                            (existing_item, match, "existing_other_collection")
                        )
                for other_collection, peer_item in global_changed_candidate_aliases:
                    if other_collection == collection_kind:
                        continue
                    match = _semantic_duplicate_match(
                        collection_kind, candidate, peer_item
                    )
                    if match:
                        semantic_matches.append(
                            (peer_item, match, "candidate_other_collection")
                        )
            for peer_id, peer_item in changed_candidates.items():
                if peer_id == candidate_id:
                    continue
                match = _semantic_duplicate_match(collection_kind, candidate, peer_item)
                if match:
                    semantic_matches.append((peer_item, match, "candidate"))
            if semantic_matches:
                match_ids = {
                    (str(item.get("section") or ""), str(item.get("key") or ""))
                    for item, _match, _source in semantic_matches
                }
                has_alias_ambiguity = any(
                    str(match.get("match_type") or "") == "ambiguous_alias_target"
                    for _item, match, _source in semantic_matches
                )
                reason = (
                    "ambiguous_alias_target"
                    if has_alias_ambiguity
                    else "ambiguous_duplicate_target"
                    if len(match_ids) > 1
                    else "submitted_duplicate"
                    if not any(
                        source.startswith("existing")
                        for _item, _match, source in semantic_matches
                    )
                    else "canonical_key_required"
                )
                conflict(candidate, collection_kind, reason, semantic_matches)
                continue

            if existing is None:
                merged_by_id[candidate_id] = candidate
                operations["inserted"] += 1
                record(
                    candidate,
                    collection_kind,
                    "would_insert" if write_mode == "validate_only" else "inserted",
                    "new_typed_identity",
                )
            else:
                merged_by_id[candidate_id] = candidate
                operations["replaced"] += 1
                record(
                    candidate,
                    collection_kind,
                    "would_replace" if write_mode == "validate_only" else "replaced",
                    "exact_key_replace",
                )
        merged[collection_kind] = [merged_by_id[item_id] for item_id in sorted(merged_by_id)]
    operations["conflicts_truncated"] = (
        operations["conflict_count"] > len(operations["conflicts"])
    )
    remaining = max(0, _DUPLICATE_OPERATION_LIMIT - len(important_operation_records))
    operations["operation_record_count"] = operation_record_count
    operations["operation_by_key"] = [
        *important_operation_records,
        *unchanged_operation_records[:remaining],
    ]
    operations["operation_records_truncated"] = (
        operation_record_count > len(operations["operation_by_key"])
    )
    return merged, operations


def upsert_partial_metadata_items(
    database: Any,
    documents: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    session: Any = None,
    domain_collection: str = DOMAIN_METADATA_COLLECTION,
    table_collection: str = TABLE_CATALOG_COLLECTION,
    main_filter_collection: str = MAIN_FILTER_COLLECTION,
) -> None:
    """Upsert validated item documents without requiring a complete package.

    This is used only while one or more of the three authoring collections are
    still empty.  It never deletes existing documents and never marks a partial
    set executable.  Full-package assembly remains mandatory as soon as all
    collections contain items and for every Data Analysis load.
    """

    actual = _metadata_collection_names(domain_collection, table_collection, main_filter_collection)
    prepared = {
        kind: [_validated_item(item, kind) for item in documents.get(kind, [])]
        for kind in actual
    }
    for kind, collection_name in actual.items():
        collection = database[collection_name]
        existing = {str(item.get("_id")): item for item in _find_items(collection, session=session)}
        for document in prepared[kind]:
            current = existing.get(document["_id"])
            if isinstance(current, Mapping) and _validated_item(current, kind) == document:
                continue
            collection.replace_one(
                {"_id": document["_id"]},
                deepcopy(document),
                upsert=True,
                session=session,
            )


def replace_metadata_items(
    database: Any,
    documents: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    session: Any = None,
    domain_collection: str = DOMAIN_METADATA_COLLECTION,
    table_collection: str = TABLE_CATALOG_COLLECTION,
    main_filter_collection: str = MAIN_FILTER_COLLECTION,
) -> None:
    """Upsert a complete checked projection without deleting concurrent items.

    Normal registration never treats absence from the candidate as a deletion
    request.  Full-set deletion belongs to an explicit migration workflow, not
    to natural-language item authoring.
    """

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
        for document in items:
            serialization_lock = kind == "domain" and document["section"] == "profile"
            if serialization_lock:
                # Every registration transaction writes the one required
                # profile item.  This creates a shared MongoDB write-conflict
                # boundary for otherwise disjoint item updates without adding
                # a lock collection or a persisted lock-only field.
                document["updated_at"] = datetime.now(timezone.utc).isoformat()
            if (
                not serialization_lock
                and isinstance(existing.get(document["_id"]), dict)
                and _validated_item(existing[document["_id"]], kind) == document
            ):
                continue
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
    "metadata_item_set_projection",
    "merge_metadata_items_for_write",
    "make_partial_metadata_item_documents",
    "make_metadata_item_documents",
    "make_metadata_section_documents",
    "replace_metadata_items",
    "replace_metadata_release",
    "upsert_partial_metadata_items",
]
