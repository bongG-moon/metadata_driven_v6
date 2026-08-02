"""Deterministic inventory extraction for natural-language metadata authoring.

The authoring model is allowed to translate prose into a closed draft, but it
must not silently omit identifiers that the author explicitly registered.  This
module extracts only those explicit identifiers and compares them with the
resulting draft.  It intentionally keeps no source text or provider payload in
either the manifest or validation evidence.

The implementation uses only the Python standard library so the file can be
embedded verbatim in a standalone Langflow component.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable, Mapping
from copy import deepcopy
from typing import Any


MANIFEST_VERSION = "metadata.authoring.source-manifest.v1"
COVERAGE_VERSION = "metadata.authoring.source-coverage.v1"

# Keep this registry aligned with ``domain_packages._validate_aliases``.  The
# authoring normalizer intentionally does not invent target kinds which the
# deterministic compiler would reject later.
_ALIAS_TARGET_SECTIONS = (
    ("datasets", "dataset"),
    ("fields", "field"),
    ("metrics", "metric"),
    ("relations", "relation"),
    ("grains", "grain"),
    ("predicates", "predicate"),
    ("recipes", "recipe"),
    ("entity_groups", "entity_group"),
)

_FIELD_ROLE_ORDER = (
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
)
_FIELD_ROLE_SET = set(_FIELD_ROLE_ORDER)
_RELATION_POLICY_VALUES = {
    "join_type": {"inner", "left", "right", "outer", "semi", "anti"},
    "cardinality": {"one_to_zero_or_one", "one_to_one", "one_to_many", "many_to_one", "many_to_many"},
    "null_key_policy": {"never_match", "match"},
    "multi_match_policy": {"fail", "error", "aggregate_right_first"},
}

MAX_SOURCE_BYTES = 65_536
MAX_MISSING_EVIDENCE = 32
MAX_INVENTORY = {
    "datasets": 128,
    "fields": 1_024,
    "field_bindings": 4_096,
    "metrics": 512,
    "relations": 256,
    "relation_endpoints": 256,
    "relation_keys": 256,
    "relation_policies": 256,
    "field_roles": 4_096,
    "grains": 256,
    "grain_keys": 256,
    "grain_display_fields": 256,
    "recipes": 256,
    "operations": 64,
    "aliases": 4_096,
}

_IDENTIFIER = r"[A-Za-z][A-Za-z0-9_.-]{0,127}"
_DECLARED_ID = r"[A-Za-z](?:[A-Za-z0-9_.-]{0,126}[A-Za-z0-9_])?"
_IDENTIFIER_RE = re.compile(rf"(?<![A-Za-z0-9_.-])({_IDENTIFIER})(?![A-Za-z0-9_.-])")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

_DATASET_RE = re.compile(
    rf"(?<![A-Za-z0-9_.-])(?P<dataset>{_DECLARED_ID})[ \t]*"
    rf"(?:\ub370\uc774\ud130\uc14b|datasets?)(?![A-Za-z0-9_])"
    rf"(?:[ \t]*(?:\uc740|\ub294|\uc774|\uac00|:|=|is\b))?",
    re.IGNORECASE,
)
_CANONICAL_FIELDS_RE = re.compile(
    r"canonical\s*(?:\ud544\ub4dc(?:\ub4e4)?|fields?)"
    r"(?:\s*(?:\uc740|\ub294|:|=)|\s+(?:are|include|includes)\b)\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_METRICS_RE = re.compile(
    r"(?:\ub4f1\ub85d\s*metrics?|registered\s+metrics?)\s*"
    r"(?:(?:\uc740|\ub294|\uc774|\uac00|:|=)|are\b)?\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_RELATIONS_RE = re.compile(
    r"(?:(?:\ub4f1\ub85d\s*)?relations?|registered\s+relations?)"
    r"(?!\s*(?:endpoints?|keys?|polic(?:y|ies))(?![A-Za-z0-9_]))\s*"
    r"(?:(?:\uc740|\ub294|\uc774|\uac00|:|=)|are\b)?\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_RELATION_ENDPOINTS_RE = re.compile(
    r"(?:(?:\ub4f1\ub85d|registered)\s*)?relation\s*endpoints?\s*"
    r"(?:(?:\uc740|\ub294|\uc774|\uac00|:|=)|are\b)?\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_RELATION_ENDPOINT_ITEM_RE = re.compile(
    rf"(?P<relation>{_DECLARED_ID})\s*=\s*(?P<left>{_DECLARED_ID})\s*(?:->|\u2192)\s*"
    rf"(?P<right>{_DECLARED_ID})",
    re.IGNORECASE,
)
_RELATION_KEYS_RE = re.compile(
    r"(?:(?:\ub4f1\ub85d|registered)\s*)?relation\s*keys?\s*"
    r"(?:(?:\uc740|\ub294|\uc774|\uac00|:|=)|are\b)?\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_RELATION_KEY_ITEM_RE = re.compile(
    rf"(?P<relation>{_DECLARED_ID})\s*=\s*"
    rf"(?P<left>{_DECLARED_ID}(?:\s*\|\s*{_DECLARED_ID})*)\s*(?:->|\u2192)\s*"
    rf"(?P<right>{_DECLARED_ID}(?:\s*\|\s*{_DECLARED_ID})*)",
    re.IGNORECASE,
)
_FIELD_ROLES_RE = re.compile(
    r"(?:(?:\ub4f1\ub85d|registered)\s*)?field\s*roles?\s*"
    r"(?:(?:\uc740|\ub294|\uc774|\uac00|:|=)|are\b)?\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_FIELD_ROLE_ITEM_RE = re.compile(
    rf"(?P<dataset>{_DECLARED_ID})\.(?P<field>{_DECLARED_ID})\s*=\s*"
    rf"(?P<roles>{_DECLARED_ID}(?:\s*\|\s*{_DECLARED_ID})*)",
    re.IGNORECASE,
)
_RELATION_POLICIES_RE = re.compile(
    r"(?:(?:\ub4f1\ub85d|registered)\s*)?relation\s*polic(?:y|ies)\s*"
    r"(?:(?:\uc740|\ub294|\uc774|\uac00|:|=)|are\b)?\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_RELATION_POLICY_ITEM_RE = re.compile(
    rf"(?P<relation>{_DECLARED_ID})\s*=\s*"
    rf"join_type\s*:\s*(?P<join_type>{_DECLARED_ID})\s*\|\s*"
    rf"cardinality\s*:\s*(?P<cardinality>{_DECLARED_ID})\s*\|\s*"
    rf"null_key_policy\s*:\s*(?P<null_key_policy>{_DECLARED_ID})\s*\|\s*"
    rf"multi_match_policy\s*:\s*(?P<multi_match_policy>{_DECLARED_ID})",
    re.IGNORECASE,
)
_GRAIN_KEYS_RE = re.compile(
    r"(?:(?:\ub4f1\ub85d|registered)\s*)?grain\s*keys?\s*"
    r"(?:(?:\uc740|\ub294|\uc774|\uac00|:|=)|are\b)?\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_GRAIN_KEY_ITEM_RE = re.compile(
    rf"(?P<grain>{_DECLARED_ID})\s*=\s*"
    rf"(?P<keys>{_DECLARED_ID}(?:\s*\|\s*{_DECLARED_ID})*)",
    re.IGNORECASE,
)
_GRAIN_DISPLAY_FIELDS_RE = re.compile(
    r"(?:(?:\ub4f1\ub85d|registered)\s*)?grain\s*display\s*fields?\s*"
    r"(?:(?:\uc740|\ub294|\uc774|\uac00|:|=)|are\b)?\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_GRAIN_DISPLAY_FIELD_ITEM_RE = re.compile(
    rf"(?P<grain>{_DECLARED_ID})\s*=\s*"
    rf"(?P<fields>{_DECLARED_ID}(?:\s*\|\s*{_DECLARED_ID})*)",
    re.IGNORECASE,
)
_OPERATIONS_RE = re.compile(
    r"(?:\ud5c8\uc6a9\s*operations?|allowed\s+operations?)\s*"
    r"(?:(?:\uc740|\ub294|\uc774|\uac00|:|=)|are\b)?\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_RECIPE_IDS_RE = re.compile(
    r"(?:(?:\ub4f1\ub85d|registered)\s*)?(?:recipes?|\ub808\uc2dc\ud53c)\s*"
    r"(?:ids?|ID|\uc544\uc774\ub514)\s*"
    # A declaration delimiter is mandatory.  Without it, ordinary field prose
    # such as ``RECIPE_ID\ub294 Recipe ID \ud544\ud130\uc57c`` was mistaken for a recipe
    # inventory and then failed as an empty declaration.  This remains a
    # deliberately narrow declaration parser; it is not a legacy prose parser.
    r"(?:(?:\uc740|\ub294|\uc774|\uac00|:|=)|are\b)\s*(?P<items>[^\n]+)",
    re.IGNORECASE,
)
_NAMED_RECIPE_RE = re.compile(
    rf"(?P<recipe>{_DECLARED_ID})\s+(?:recipe|\ub808\uc2dc\ud53c)\s*"
    rf"(?:(?:\uc740|\ub294|:)|is\b)",
    re.IGNORECASE,
)
_RECIPE_MENTION_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:recipes?|\ub808\uc2dc\ud53c)(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
_KOREAN_ALIAS_CLAUSE_RE = re.compile(
    rf"(?P<labels>[^,.\n]+?)(?:\uc740|\ub294)\s*(?P<target>{_DECLARED_ID})(?:\uc5d0)?"
    rf"(?=\s*(?:,|\uc5f0\uacb0|\.|$))",
    re.IGNORECASE,
)
_ENGLISH_ALIAS_CLAUSE_RE = re.compile(
    rf"(?P<labels>[^,.;\n]+?)(?:\s+(?:map|maps)\s+to|\s+are\s+aliases?\s+for|\s*->\s*)"
    rf"(?P<target>{_DECLARED_ID})(?=\s*(?:,|\.|;|$))",
    re.IGNORECASE,
)
_KOREAN_ALIAS_CARD_RE = re.compile(
    rf"별칭\s*카드.*?안정\s*식별자는\s*"
    rf"(?P<identity_type>{_DECLARED_ID})\s*:\s*(?P<identity_key>{_DECLARED_ID}).*?"
    rf"대상\s*유형은\s*(?P<target_type>{_DECLARED_ID})\s*,\s*"
    rf"대상\s*키는\s*(?P<target_key>{_DECLARED_ID}).*?\n\s*"
    rf"사용자가\s*(?P<labels>[^\n]+?)라고\s*말하면\s*"
    rf"(?P<resolved_target>{_DECLARED_ID})(?:\s*(?:필드|지표|데이터셋))?로\s*해석",
    re.IGNORECASE,
)
_QUOTED_ALIAS_RE = re.compile(r"['\"](?P<label>[^'\"\n]{1,256})['\"]")

_LIST_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "allowed",
    "canonical",
    "field",
    "fields",
    "id",
    "ids",
    "include",
    "includes",
    "is",
    "metric",
    "metrics",
    "operation",
    "operations",
    "recipe",
    "recipes",
    "registered",
    "relation",
    "relations",
    "the",
}


class AuthoringSourceManifestError(ValueError):
    """Fail-closed authoring inventory error with bounded safe evidence."""

    def __init__(self, code: str, evidence: Mapping[str, Any] | None = None) -> None:
        self.code = str(code)
        self.evidence = deepcopy(dict(evidence or {}))
        super().__init__(self.code)


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _normalized_source(source_text: str) -> tuple[str, str]:
    if not isinstance(source_text, str):
        raise AuthoringSourceManifestError("authoring_source_not_text")
    raw_bytes = source_text.encode("utf-8")
    if not raw_bytes or len(raw_bytes) > MAX_SOURCE_BYTES:
        raise AuthoringSourceManifestError(
            "authoring_source_size_invalid",
            {"source_bytes": len(raw_bytes), "max_source_bytes": MAX_SOURCE_BYTES},
        )
    normalized = (
        unicodedata.normalize("NFKC", source_text)
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .lstrip("\ufeff")
        .strip()
    )
    normalized_bytes = normalized.encode("utf-8")
    if not normalized_bytes:
        raise AuthoringSourceManifestError(
            "authoring_source_size_invalid",
            {"source_bytes": 0, "max_source_bytes": MAX_SOURCE_BYTES},
        )
    return normalized, hashlib.sha256(normalized_bytes).hexdigest()


def _declaration_items(raw_items: str) -> list[str]:
    """Parse a bounded comma/conjunction list without interpreting prose."""

    text = str(raw_items or "")
    text = re.split(
        r"(?:\uc774\ub2e4|\uc785\ub2c8\ub2e4|\uc774\uba70|\uc774\uace0)(?:\.|\s|$)"
        r"|;|(?<![A-Za-z0-9_.-])\.(?=\s|$)",
        text,
        maxsplit=1,
    )[0]
    text = text.strip()
    if text.endswith("."):
        text = text[:-1]
    text = re.sub(r"[`'\"\[\](){}]", " ", text)
    text = re.sub(r"\s+(?:\ubc0f|\uadf8\ub9ac\uace0|and)\s+", ",", text, flags=re.IGNORECASE)
    values: list[str] = []
    for segment in text.split(","):
        matches = [
            item
            for item in _IDENTIFIER_RE.findall(segment)
            if item.casefold() not in _LIST_STOPWORDS
        ]
        if len(matches) == 1:
            values.append(matches[0])
        elif len(matches) > 1:
            # An explicit list item must not contain explanatory prose.  Taking
            # only the first token would turn ambiguity into silent omission.
            raise AuthoringSourceManifestError(
                "authoring_inventory_item_ambiguous",
                {"identifier_count": len(matches)},
            )
    return sorted(set(values))


def _bounded(values: Iterable[str], kind: str) -> list[str]:
    normalized = sorted({str(value) for value in values})
    limit = MAX_INVENTORY[kind]
    if len(normalized) > limit:
        raise AuthoringSourceManifestError(
            "authoring_inventory_limit_exceeded",
            {"inventory": kind, "count": len(normalized), "limit": limit},
        )
    for value in normalized:
        if not re.fullmatch(_IDENTIFIER, value):
            raise AuthoringSourceManifestError(
                "authoring_inventory_identifier_invalid",
                {"inventory": kind, "identifier_sha256": hashlib.sha256(value.encode("utf-8")).hexdigest()},
            )
    return normalized


def _normalized_alias(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", str(value or ""))
    normalized = re.sub(r"\s+", " ", normalized).strip(" `\"'[](){}:;.-")
    if not normalized or len(normalized) > 128:
        raise AuthoringSourceManifestError(
            "authoring_alias_invalid",
            {"alias_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest()},
        )
    return normalized.casefold()


def _alias_labels(raw_labels: str) -> list[str]:
    labels = str(raw_labels or "")
    labels = re.sub(
        r"^.*(?:\ubcc4\uce6d|aliases?)(?:\uc73c\ub85c|\uc740|\ub294|\s*:)?\s*",
        "",
        labels,
        flags=re.IGNORECASE,
    )
    parts = re.split(
        r"\s*(?:\uacfc|\uc640|\ubc0f)\s*|\s+and\s+",
        labels,
        flags=re.IGNORECASE,
    )
    return sorted({_normalized_alias(part) for part in parts if str(part).strip()})


def _source_alias_bindings(source: str) -> tuple[list[dict[str, str]], bool]:
    alias_marker = re.compile(r"(?:\ubcc4\uce6d|aliases?)", re.IGNORECASE)
    pairs: dict[str, str] = {}
    declared = False
    protected_spans: list[tuple[int, int]] = []

    def add_pair(label: str, target: str) -> None:
        existing = pairs.get(label)
        if existing is not None and existing != target:
            raise AuthoringSourceManifestError(
                "authoring_alias_target_ambiguous",
                {"alias_sha256": hashlib.sha256(label.encode("utf-8")).hexdigest()},
            )
        pairs[label] = target

    for match in _KOREAN_ALIAS_CARD_RE.finditer(source):
        declared = True
        identity_type = match.group("identity_type").casefold()
        target_type = match.group("target_type").casefold()
        identity_key = match.group("identity_key")
        target_key = match.group("target_key")
        resolved_target = match.group("resolved_target")
        if (
            identity_type != target_type
            or identity_key != target_key
            or target_key != resolved_target
        ):
            raise AuthoringSourceManifestError(
                "authoring_alias_card_declaration_invalid",
                {"card_sha256": _safe_value_sha256(match.group(0))},
            )
        labels = [
            _normalized_alias(item.group("label"))
            for item in _QUOTED_ALIAS_RE.finditer(match.group("labels"))
        ]
        if not labels:
            raise AuthoringSourceManifestError("authoring_alias_card_declaration_invalid")
        for label in labels:
            add_pair(label, target_key)
        protected_spans.append(match.span())

    cursor = 0
    for raw_line in source.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        line_span = (cursor, cursor + len(raw_line))
        cursor = line_span[1]
        if any(line_span[0] < end and start < line_span[1] for start, end in protected_spans):
            continue
        if not alias_marker.search(line):
            continue
        for pattern in (_KOREAN_ALIAS_CLAUSE_RE, _ENGLISH_ALIAS_CLAUSE_RE):
            for match in pattern.finditer(line):
                declared = True
                target = match.group("target").rstrip(".")
                if not re.fullmatch(_IDENTIFIER, target):
                    raise AuthoringSourceManifestError("authoring_alias_target_invalid")
                for label in _alias_labels(match.group("labels")):
                    add_pair(label, target)
    if len(pairs) > MAX_INVENTORY["aliases"]:
        raise AuthoringSourceManifestError(
            "authoring_inventory_limit_exceeded",
            {"inventory": "aliases", "count": len(pairs), "limit": MAX_INVENTORY["aliases"]},
        )
    return [
        {"alias": alias, "target": target}
        for alias, target in sorted(pairs.items())
    ], declared


def _collect_declared_list(pattern: re.Pattern[str], source: str, kind: str) -> tuple[list[str], bool]:
    matches = list(pattern.finditer(source))
    values: list[str] = []
    for match in matches:
        parsed = _declaration_items(match.group("items"))
        if not parsed:
            raise AuthoringSourceManifestError(
                "authoring_inventory_declaration_empty",
                {"inventory": kind},
            )
        values.extend(parsed)
    return _bounded(values, kind), bool(matches)


def _source_relation_endpoints(
    source: str,
    *,
    relations: Iterable[str],
    datasets: Iterable[str],
) -> tuple[dict[str, dict[str, str]], bool]:
    """Extract exact ``relation=left->right`` declarations from source prose."""

    matches = list(_RELATION_ENDPOINTS_RE.finditer(source))
    registered_relations = set(relations)
    registered_datasets = set(datasets)
    endpoints: dict[str, dict[str, str]] = {}
    for declaration in matches:
        raw_items = declaration.group("items")
        # Stop at the Korean declarative ending or an English sentence end.
        raw_items = re.split(
            r"(?:\uc774\ub2e4|\uc785\ub2c8\ub2e4)(?:\.|\s|$)|;|(?<![A-Za-z0-9_.-])\.(?=\s|$)",
            raw_items,
            maxsplit=1,
        )[0]
        segments = re.split(
            r"\s*(?:,|\s+(?:\ubc0f|\uadf8\ub9ac\uace0|and)\s+)\s*",
            raw_items.strip().rstrip("."),
            flags=re.IGNORECASE,
        )
        parsed_count = 0
        for segment in segments:
            if not segment.strip():
                continue
            item = _RELATION_ENDPOINT_ITEM_RE.fullmatch(segment.strip())
            if item is None:
                raise AuthoringSourceManifestError(
                    "authoring_relation_endpoint_declaration_invalid",
                    {"item_sha256": _safe_value_sha256(segment.strip())},
                )
            parsed_count += 1
            relation_id = item.group("relation")
            left_dataset = item.group("left")
            right_dataset = item.group("right")
            if relation_id not in registered_relations:
                raise AuthoringSourceManifestError(
                    "authoring_relation_endpoint_relation_unknown",
                    {"relation_sha256": _safe_value_sha256(relation_id)},
                )
            unknown_datasets = sorted(
                value
                for value in {left_dataset, right_dataset}
                if value not in registered_datasets
            )
            if unknown_datasets:
                raise AuthoringSourceManifestError(
                    "authoring_relation_endpoint_dataset_unknown",
                    {
                        "relation_sha256": _safe_value_sha256(relation_id),
                        "dataset_sha256": [_safe_value_sha256(value) for value in unknown_datasets],
                    },
                )
            card = {
                "left_dataset": left_dataset,
                "right_dataset": right_dataset,
            }
            existing = endpoints.get(relation_id)
            if existing is not None and existing != card:
                raise AuthoringSourceManifestError(
                    "authoring_relation_endpoint_ambiguous",
                    {"relation_sha256": _safe_value_sha256(relation_id)},
                )
            endpoints[relation_id] = card
        if not parsed_count:
            raise AuthoringSourceManifestError("authoring_relation_endpoint_declaration_empty")

    if len(endpoints) > MAX_INVENTORY["relation_endpoints"]:
        raise AuthoringSourceManifestError(
            "authoring_inventory_limit_exceeded",
            {
                "inventory": "relation_endpoints",
                "count": len(endpoints),
                "limit": MAX_INVENTORY["relation_endpoints"],
            },
        )
    return {key: endpoints[key] for key in sorted(endpoints)}, bool(matches)


def _closed_declaration_matches(
    raw_items: str,
    item_pattern: re.Pattern[str],
    *,
    kind: str,
) -> list[re.Match[str]]:
    body = re.split(
        r"(?:\uc774\ub2e4|\uc785\ub2c8\ub2e4)(?:\.|\s|$)|;|(?<![A-Za-z0-9_.-])\.(?=\s|$)",
        str(raw_items or ""),
        maxsplit=1,
    )[0].strip().rstrip(".")
    matches = list(item_pattern.finditer(body))
    if not matches:
        raise AuthoringSourceManifestError(
            "authoring_inventory_declaration_empty",
            {"inventory": kind},
        )
    cursor = 0
    for index, match in enumerate(matches):
        gap = body[cursor : match.start()]
        if index == 0:
            valid_gap = not gap.strip()
        else:
            valid_gap = bool(
                re.fullmatch(r"\s*(?:,|\ubc0f|\uadf8\ub9ac\uace0|and)\s*", gap, flags=re.IGNORECASE)
            )
        if not valid_gap:
            raise AuthoringSourceManifestError(
                "authoring_inventory_declaration_invalid",
                {"inventory": kind, "item_sha256": _safe_value_sha256(gap.strip())},
            )
        cursor = match.end()
    if body[cursor:].strip():
        raise AuthoringSourceManifestError(
            "authoring_inventory_declaration_invalid",
            {"inventory": kind, "item_sha256": _safe_value_sha256(body[cursor:].strip())},
        )
    return matches


def _source_relation_keys(
    source: str,
    *,
    relations: Iterable[str],
    relation_endpoints: Mapping[str, Mapping[str, str]],
    dataset_fields: Mapping[str, Iterable[str]],
) -> tuple[dict[str, dict[str, list[str]]], bool]:
    declarations = list(_RELATION_KEYS_RE.finditer(source))
    registered_relations = set(relations)
    registered_fields = {
        str(dataset_id): {str(field_id) for field_id in fields}
        for dataset_id, fields in dataset_fields.items()
    }
    keys_by_relation: dict[str, dict[str, list[str]]] = {}
    for declaration in declarations:
        for item in _closed_declaration_matches(
            declaration.group("items"),
            _RELATION_KEY_ITEM_RE,
            kind="relation_keys",
        ):
            relation_id = item.group("relation")
            if relation_id not in registered_relations:
                raise AuthoringSourceManifestError(
                    "authoring_relation_key_relation_unknown",
                    {"relation_sha256": _safe_value_sha256(relation_id)},
                )
            endpoints = relation_endpoints.get(relation_id)
            if not isinstance(endpoints, Mapping):
                raise AuthoringSourceManifestError(
                    "authoring_relation_key_endpoint_missing",
                    {"relation_sha256": _safe_value_sha256(relation_id)},
                )
            left_keys = [value.strip() for value in item.group("left").split("|")]
            right_keys = [value.strip() for value in item.group("right").split("|")]
            if not left_keys or len(left_keys) != len(right_keys):
                raise AuthoringSourceManifestError(
                    "authoring_relation_key_cardinality_invalid",
                    {"relation_sha256": _safe_value_sha256(relation_id)},
                )
            left_dataset = str(endpoints.get("left_dataset") or "")
            right_dataset = str(endpoints.get("right_dataset") or "")
            unknown_left = [value for value in left_keys if value not in registered_fields.get(left_dataset, set())]
            unknown_right = [value for value in right_keys if value not in registered_fields.get(right_dataset, set())]
            if unknown_left or unknown_right:
                raise AuthoringSourceManifestError(
                    "authoring_relation_key_field_unknown",
                    {
                        "relation_sha256": _safe_value_sha256(relation_id),
                        "left_key_sha256": [_safe_value_sha256(value) for value in unknown_left],
                        "right_key_sha256": [_safe_value_sha256(value) for value in unknown_right],
                    },
                )
            card = {"left_keys": left_keys, "right_keys": right_keys}
            existing = keys_by_relation.get(relation_id)
            if existing is not None and existing != card:
                raise AuthoringSourceManifestError(
                    "authoring_relation_key_ambiguous",
                    {"relation_sha256": _safe_value_sha256(relation_id)},
                )
            keys_by_relation[relation_id] = card
    if len(keys_by_relation) > MAX_INVENTORY["relation_keys"]:
        raise AuthoringSourceManifestError(
            "authoring_inventory_limit_exceeded",
            {
                "inventory": "relation_keys",
                "count": len(keys_by_relation),
                "limit": MAX_INVENTORY["relation_keys"],
            },
        )
    return {key: keys_by_relation[key] for key in sorted(keys_by_relation)}, bool(declarations)


def _source_field_roles(
    source: str,
    *,
    dataset_fields: Mapping[str, Iterable[str]],
) -> tuple[dict[str, dict[str, list[str]]], bool]:
    declarations = list(_FIELD_ROLES_RE.finditer(source))
    bindings: dict[tuple[str, str], list[str]] = {}
    registered = {
        (str(dataset_id), str(field_id))
        for dataset_id, fields in dataset_fields.items()
        for field_id in fields
    }
    for declaration in declarations:
        for item in _closed_declaration_matches(
            declaration.group("items"),
            _FIELD_ROLE_ITEM_RE,
            kind="field_roles",
        ):
            dataset_id = item.group("dataset")
            field_id = item.group("field")
            binding = (dataset_id, field_id)
            if binding not in registered:
                raise AuthoringSourceManifestError(
                    "authoring_field_role_binding_unknown",
                    {
                        "dataset_sha256": _safe_value_sha256(dataset_id),
                        "field_sha256": _safe_value_sha256(field_id),
                    },
                )
            raw_roles = [value.strip() for value in item.group("roles").split("|")]
            if len(raw_roles) != len(set(raw_roles)) or any(value not in _FIELD_ROLE_SET for value in raw_roles):
                raise AuthoringSourceManifestError(
                    "authoring_field_role_value_invalid",
                    {
                        "dataset_sha256": _safe_value_sha256(dataset_id),
                        "field_sha256": _safe_value_sha256(field_id),
                        "role_sha256": [_safe_value_sha256(value) for value in raw_roles],
                    },
                )
            roles = [role for role in _FIELD_ROLE_ORDER if role in raw_roles]
            existing = bindings.get(binding)
            if existing is not None and existing != roles:
                raise AuthoringSourceManifestError(
                    "authoring_field_role_binding_ambiguous",
                    {
                        "dataset_sha256": _safe_value_sha256(dataset_id),
                        "field_sha256": _safe_value_sha256(field_id),
                    },
                )
            bindings[binding] = roles
    if len(bindings) > MAX_INVENTORY["field_roles"]:
        raise AuthoringSourceManifestError(
            "authoring_inventory_limit_exceeded",
            {
                "inventory": "field_roles",
                "count": len(bindings),
                "limit": MAX_INVENTORY["field_roles"],
            },
        )
    result: dict[str, dict[str, list[str]]] = {}
    for (dataset_id, field_id), roles in sorted(bindings.items()):
        result.setdefault(dataset_id, {})[field_id] = roles
    return result, bool(declarations)


def _source_grain_contract(
    source: str,
    *,
    fields: Iterable[str],
    field_roles: Mapping[str, Mapping[str, Iterable[str]]],
) -> tuple[dict[str, list[str]], dict[str, list[str]], bool, bool]:
    registered_fields = set(fields)
    roles_by_field: dict[str, set[str]] = {}
    for dataset_roles in field_roles.values():
        for field_id, roles in dataset_roles.items():
            roles_by_field.setdefault(str(field_id), set()).update(str(value) for value in roles)

    key_declarations = list(_GRAIN_KEYS_RE.finditer(source))
    grain_keys: dict[str, list[str]] = {}
    for declaration in key_declarations:
        for item in _closed_declaration_matches(
            declaration.group("items"),
            _GRAIN_KEY_ITEM_RE,
            kind="grain_keys",
        ):
            grain_id = item.group("grain")
            keys = [value.strip() for value in item.group("keys").split("|")]
            if len(keys) != len(set(keys)) or any(value not in registered_fields for value in keys):
                raise AuthoringSourceManifestError(
                    "authoring_grain_key_field_unknown",
                    {
                        "grain_sha256": _safe_value_sha256(grain_id),
                        "field_sha256": [_safe_value_sha256(value) for value in keys],
                    },
                )
            # Role compatibility is checked only when the source explicitly
            # seals a field-role inventory.  If no such declaration exists,
            # this extractor must not infer roles from prose or reject an
            # otherwise independently testable grain declaration.
            incompatible = [
                value
                for value in keys
                if roles_by_field and not roles_by_field.get(value, set()) & {"group", "join"}
            ]
            if incompatible:
                raise AuthoringSourceManifestError(
                    "authoring_grain_key_role_invalid",
                    {
                        "grain_sha256": _safe_value_sha256(grain_id),
                        "field_sha256": [_safe_value_sha256(value) for value in incompatible],
                    },
                )
            existing = grain_keys.get(grain_id)
            if existing is not None and existing != keys:
                raise AuthoringSourceManifestError(
                    "authoring_grain_key_ambiguous",
                    {"grain_sha256": _safe_value_sha256(grain_id)},
                )
            grain_keys[grain_id] = keys
    if len(grain_keys) > MAX_INVENTORY["grain_keys"]:
        raise AuthoringSourceManifestError(
            "authoring_inventory_limit_exceeded",
            {"inventory": "grain_keys", "count": len(grain_keys), "limit": MAX_INVENTORY["grain_keys"]},
        )

    display_declarations = list(_GRAIN_DISPLAY_FIELDS_RE.finditer(source))
    grain_display_fields: dict[str, list[str]] = (
        {grain_id: [] for grain_id in grain_keys}
        if display_declarations
        else {}
    )
    seen_display: set[str] = set()
    for declaration in display_declarations:
        for item in _closed_declaration_matches(
            declaration.group("items"),
            _GRAIN_DISPLAY_FIELD_ITEM_RE,
            kind="grain_display_fields",
        ):
            grain_id = item.group("grain")
            values = [value.strip() for value in item.group("fields").split("|")]
            if grain_id not in grain_keys:
                raise AuthoringSourceManifestError(
                    "authoring_grain_display_grain_unknown",
                    {"grain_sha256": _safe_value_sha256(grain_id)},
                )
            if len(values) != len(set(values)) or any(value not in registered_fields for value in values):
                raise AuthoringSourceManifestError(
                    "authoring_grain_display_field_unknown",
                    {
                        "grain_sha256": _safe_value_sha256(grain_id),
                        "field_sha256": [_safe_value_sha256(value) for value in values],
                    },
                )
            if grain_id in seen_display and grain_display_fields[grain_id] != values:
                raise AuthoringSourceManifestError(
                    "authoring_grain_display_ambiguous",
                    {"grain_sha256": _safe_value_sha256(grain_id)},
                )
            seen_display.add(grain_id)
            grain_display_fields[grain_id] = values
    if len(grain_display_fields) > MAX_INVENTORY["grain_display_fields"]:
        raise AuthoringSourceManifestError(
            "authoring_inventory_limit_exceeded",
            {
                "inventory": "grain_display_fields",
                "count": len(grain_display_fields),
                "limit": MAX_INVENTORY["grain_display_fields"],
            },
        )
    return (
        {key: grain_keys[key] for key in sorted(grain_keys)},
        {key: grain_display_fields[key] for key in sorted(grain_display_fields)},
        bool(key_declarations),
        bool(display_declarations),
    )


def _source_relation_policies(
    source: str,
    *,
    relations: Iterable[str],
) -> tuple[dict[str, dict[str, str]], bool]:
    declarations = list(_RELATION_POLICIES_RE.finditer(source))
    registered = set(relations)
    policies: dict[str, dict[str, str]] = {}
    for declaration in declarations:
        for item in _closed_declaration_matches(
            declaration.group("items"),
            _RELATION_POLICY_ITEM_RE,
            kind="relation_policies",
        ):
            relation_id = item.group("relation")
            if relation_id not in registered:
                raise AuthoringSourceManifestError(
                    "authoring_relation_policy_relation_unknown",
                    {"relation_sha256": _safe_value_sha256(relation_id)},
                )
            card = {
                key: item.group(key)
                for key in ("join_type", "cardinality", "null_key_policy", "multi_match_policy")
            }
            invalid = [key for key, value in card.items() if value not in _RELATION_POLICY_VALUES[key]]
            if invalid:
                raise AuthoringSourceManifestError(
                    "authoring_relation_policy_value_invalid",
                    {
                        "relation_sha256": _safe_value_sha256(relation_id),
                        "policy_keys": invalid,
                        "value_sha256": [_safe_value_sha256(card[key]) for key in invalid],
                    },
                )
            existing = policies.get(relation_id)
            if existing is not None and existing != card:
                raise AuthoringSourceManifestError(
                    "authoring_relation_policy_ambiguous",
                    {"relation_sha256": _safe_value_sha256(relation_id)},
                )
            policies[relation_id] = card
    if len(policies) > MAX_INVENTORY["relation_policies"]:
        raise AuthoringSourceManifestError(
            "authoring_inventory_limit_exceeded",
            {
                "inventory": "relation_policies",
                "count": len(policies),
                "limit": MAX_INVENTORY["relation_policies"],
            },
        )
    return {key: policies[key] for key in sorted(policies)}, bool(declarations)


def extract_authoring_source_manifest(source_text: str) -> dict[str, Any]:
    """Extract explicit inventory IDs from Korean or English authoring prose.

    The returned manifest contains identifiers and hashes, never ``source_text``
    or any prose excerpt.  It is content-addressed so a caller cannot alter an
    expected inventory between model invocation and deterministic compilation.
    """

    source, source_sha256 = _normalized_source(source_text)
    dataset_matches = list(_DATASET_RE.finditer(source))
    dataset_fields: dict[str, set[str]] = {}
    for index, match in enumerate(dataset_matches):
        dataset_id = match.group("dataset")
        block_end = dataset_matches[index + 1].start() if index + 1 < len(dataset_matches) else len(source)
        block = source[match.end() : block_end]
        field_matches = list(_CANONICAL_FIELDS_RE.finditer(block))
        fields: set[str] = dataset_fields.setdefault(dataset_id, set())
        for field_match in field_matches:
            parsed = _declaration_items(field_match.group("items"))
            if not parsed:
                raise AuthoringSourceManifestError(
                    "authoring_inventory_declaration_empty",
                    {"inventory": "fields", "dataset_sha256": hashlib.sha256(dataset_id.encode("utf-8")).hexdigest()},
                )
            fields.update(parsed)

    datasets = _bounded(dataset_fields, "datasets")
    normalized_dataset_fields = {
        dataset_id: _bounded(dataset_fields[dataset_id], "fields")
        for dataset_id in datasets
    }
    field_bindings = sum(len(values) for values in normalized_dataset_fields.values())
    if field_bindings > MAX_INVENTORY["field_bindings"]:
        raise AuthoringSourceManifestError(
            "authoring_inventory_limit_exceeded",
            {
                "inventory": "field_bindings",
                "count": field_bindings,
                "limit": MAX_INVENTORY["field_bindings"],
            },
        )
    unique_fields = _bounded(
        (field for values in normalized_dataset_fields.values() for field in values),
        "fields",
    )

    metrics, metrics_declared = _collect_declared_list(_METRICS_RE, source, "metrics")
    relations, relations_declared = _collect_declared_list(_RELATIONS_RE, source, "relations")
    relation_endpoints, relation_endpoints_declared = _source_relation_endpoints(
        source,
        relations=relations,
        datasets=datasets,
    )
    relation_keys, relation_keys_declared = _source_relation_keys(
        source,
        relations=relations,
        relation_endpoints=relation_endpoints,
        dataset_fields=normalized_dataset_fields,
    )
    field_roles, field_roles_declared = _source_field_roles(
        source,
        dataset_fields=normalized_dataset_fields,
    )
    grain_keys, grain_display_fields, grain_keys_declared, grain_display_fields_declared = _source_grain_contract(
        source,
        fields=unique_fields,
        field_roles=field_roles,
    )
    relation_policies, relation_policies_declared = _source_relation_policies(
        source,
        relations=relations,
    )
    operations, operations_declared = _collect_declared_list(_OPERATIONS_RE, source, "operations")
    recipes, recipe_ids_declared = _collect_declared_list(_RECIPE_IDS_RE, source, "recipes")
    recipes = _bounded([*recipes, *(match.group("recipe") for match in _NAMED_RECIPE_RE.finditer(source))], "recipes")
    alias_bindings, aliases_declared = _source_alias_bindings(source)
    aliases = sorted({item["alias"] for item in alias_bindings})
    alias_targets = sorted({item["target"] for item in alias_bindings})

    required_sections = sorted(
        {
            *( ["datasets"] if dataset_matches else [] ),
            *( ["fields"] if field_bindings else [] ),
            *( ["field_roles"] if field_roles_declared else [] ),
            *( ["metrics"] if metrics_declared else [] ),
            *( ["grains"] if grain_keys_declared else [] ),
            *( ["grain_keys"] if grain_keys_declared else [] ),
            *( ["grain_display_fields"] if grain_display_fields_declared else [] ),
            *( ["relations"] if relations_declared else [] ),
            *( ["relation_endpoints"] if relation_endpoints_declared else [] ),
            *( ["relation_keys"] if relation_keys_declared else [] ),
            *( ["relation_policies"] if relation_policies_declared else [] ),
            *( ["operations"] if operations_declared else [] ),
            # Mere prose mentions (for example a RECIPE_ID field description)
            # do not declare an executable recipe inventory.  Only an explicit
            # recipe-ID declaration or a syntactically named recipe can do so.
            *( ["recipes"] if recipe_ids_declared or recipes else [] ),
            *( ["aliases"] if aliases_declared else [] ),
        }
    )
    inventories = {
        "datasets": datasets,
        "dataset_fields": normalized_dataset_fields,
        "fields": unique_fields,
        "field_roles": field_roles,
        "metrics": metrics,
        "grains": sorted(grain_keys),
        "grain_keys": grain_keys,
        "grain_display_fields": grain_display_fields,
        "relations": relations,
        "relation_endpoints": relation_endpoints,
        "relation_keys": relation_keys,
        "relation_policies": relation_policies,
        "recipes": recipes,
        "operations": operations,
        "aliases": aliases,
        "alias_targets": alias_targets,
        "alias_bindings": alias_bindings,
    }
    counts = {
        "datasets": len(datasets),
        "fields": len(unique_fields),
        "field_bindings": field_bindings,
        "field_roles": sum(len(values) for values in field_roles.values()),
        "metrics": len(metrics),
        "grains": len(grain_keys),
        "grain_keys": len(grain_keys),
        "grain_display_fields": len(grain_display_fields),
        "relations": len(relations),
        "relation_endpoints": len(relation_endpoints),
        "relation_keys": len(relation_keys),
        "relation_policies": len(relation_policies),
        "recipes": len(recipes),
        "operations": len(operations),
        "aliases": len(aliases),
        "alias_targets": len(alias_targets),
        "alias_bindings": len(alias_bindings),
    }
    material = {
        "contract_version": MANIFEST_VERSION,
        "source_sha256": source_sha256,
        "inventories": inventories,
        "required_sections": required_sections,
        "counts": counts,
    }
    return {**material, "manifest_sha256": _canonical_sha256(material)}


def _validated_manifest(value: Mapping[str, Any]) -> dict[str, Any]:
    manifest = deepcopy(dict(value))
    expected_keys = {
        "contract_version",
        "source_sha256",
        "inventories",
        "required_sections",
        "counts",
        "manifest_sha256",
    }
    if set(manifest) != expected_keys or manifest.get("contract_version") != MANIFEST_VERSION:
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    if not _SHA256_RE.fullmatch(str(manifest.get("source_sha256") or "")):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    supplied_hash = str(manifest.pop("manifest_sha256", ""))
    expected_hash = _canonical_sha256(manifest)
    if supplied_hash != expected_hash:
        raise AuthoringSourceManifestError(
            "authoring_source_manifest_hash_mismatch",
            {"expected_sha256": expected_hash, "actual_sha256": supplied_hash},
        )
    manifest["manifest_sha256"] = supplied_hash
    return manifest


def validate_authoring_source_manifest(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and copy a sealed source manifest.

    This public boundary is intentionally small.  Trusted executable
    blueprints use the manifest hash as an independently supplied source pin,
    so callers must be able to validate the manifest before trusting that pin.
    """

    if not isinstance(value, Mapping):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    return _validated_manifest(value)


def _safe_value_sha256(value: Any) -> str:
    """Hash untrusted authoring values without retaining them in evidence."""

    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _manifest_alias_targets(manifest: Mapping[str, Any]) -> dict[str, str]:
    inventories = manifest.get("inventories")
    bindings = inventories.get("alias_bindings") if isinstance(inventories, Mapping) else None
    if not isinstance(bindings, list):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")

    targets: dict[str, str] = {}
    for raw_binding in bindings:
        if not isinstance(raw_binding, Mapping) or set(raw_binding) != {"alias", "target"}:
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        raw_alias = raw_binding.get("alias")
        raw_target = raw_binding.get("target")
        if not isinstance(raw_alias, str) or not isinstance(raw_target, str):
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        alias = _normalized_alias(raw_alias)
        if alias != raw_alias or not re.fullmatch(_IDENTIFIER, raw_target):
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        existing = targets.get(alias)
        if existing is not None and existing != raw_target:
            raise AuthoringSourceManifestError(
                "authoring_alias_target_ambiguous",
                {"alias_sha256": _safe_value_sha256(alias)},
            )
        targets[alias] = raw_target
    return targets


def _manifest_relation_endpoints(manifest: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    inventories = manifest.get("inventories")
    if not isinstance(inventories, Mapping):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    raw_endpoints = inventories.get("relation_endpoints")
    if not isinstance(raw_endpoints, Mapping):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    raw_relations = inventories.get("relations")
    raw_datasets = inventories.get("datasets")
    if not isinstance(raw_relations, list) or not isinstance(raw_datasets, list):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    relations = {str(value) for value in raw_relations}
    datasets = {str(value) for value in raw_datasets}

    endpoints: dict[str, dict[str, str]] = {}
    for relation_id, raw_card in raw_endpoints.items():
        if not isinstance(relation_id, str) or not isinstance(raw_card, Mapping):
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        if set(raw_card) != {"left_dataset", "right_dataset"}:
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        left_dataset = raw_card.get("left_dataset")
        right_dataset = raw_card.get("right_dataset")
        if (
            relation_id not in relations
            or not isinstance(left_dataset, str)
            or not isinstance(right_dataset, str)
            or left_dataset not in datasets
            or right_dataset not in datasets
        ):
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        endpoints[relation_id] = {
            "left_dataset": left_dataset,
            "right_dataset": right_dataset,
        }
    return {key: endpoints[key] for key in sorted(endpoints)}


def _manifest_field_roles(manifest: Mapping[str, Any]) -> dict[str, dict[str, list[str]]]:
    inventories = manifest.get("inventories")
    raw_roles = inventories.get("field_roles") if isinstance(inventories, Mapping) else None
    raw_dataset_fields = inventories.get("dataset_fields") if isinstance(inventories, Mapping) else None
    if not isinstance(raw_roles, Mapping) or not isinstance(raw_dataset_fields, Mapping):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    result: dict[str, dict[str, list[str]]] = {}
    for dataset_id, raw_fields in raw_roles.items():
        registered_fields = raw_dataset_fields.get(dataset_id)
        if not isinstance(dataset_id, str) or not isinstance(raw_fields, Mapping) or not isinstance(registered_fields, list):
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        for field_id, raw_values in raw_fields.items():
            if (
                not isinstance(field_id, str)
                or field_id not in registered_fields
                or not isinstance(raw_values, list)
                or not raw_values
                or not all(isinstance(value, str) for value in raw_values)
            ):
                raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
            values = [role for role in _FIELD_ROLE_ORDER if role in raw_values]
            if len(values) != len(raw_values) or values != raw_values:
                raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
            result.setdefault(dataset_id, {})[field_id] = values
    return {
        dataset_id: {field_id: result[dataset_id][field_id] for field_id in sorted(result[dataset_id])}
        for dataset_id in sorted(result)
    }


def _manifest_relation_keys(manifest: Mapping[str, Any]) -> dict[str, dict[str, list[str]]]:
    inventories = manifest.get("inventories")
    raw_keys = inventories.get("relation_keys") if isinstance(inventories, Mapping) else None
    raw_relations = inventories.get("relations") if isinstance(inventories, Mapping) else None
    raw_endpoints = inventories.get("relation_endpoints") if isinstance(inventories, Mapping) else None
    raw_dataset_fields = inventories.get("dataset_fields") if isinstance(inventories, Mapping) else None
    if (
        not isinstance(raw_keys, Mapping)
        or not isinstance(raw_relations, list)
        or not isinstance(raw_endpoints, Mapping)
        or not isinstance(raw_dataset_fields, Mapping)
    ):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    result: dict[str, dict[str, list[str]]] = {}
    for relation_id, raw_card in raw_keys.items():
        endpoints = raw_endpoints.get(relation_id)
        if (
            not isinstance(relation_id, str)
            or relation_id not in raw_relations
            or not isinstance(raw_card, Mapping)
            or set(raw_card) != {"left_keys", "right_keys"}
            or not isinstance(endpoints, Mapping)
        ):
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        left_keys = raw_card.get("left_keys")
        right_keys = raw_card.get("right_keys")
        if (
            not isinstance(left_keys, list)
            or not isinstance(right_keys, list)
            or not left_keys
            or len(left_keys) != len(right_keys)
            or not all(isinstance(value, str) for value in [*left_keys, *right_keys])
        ):
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        left_fields = raw_dataset_fields.get(endpoints.get("left_dataset"))
        right_fields = raw_dataset_fields.get(endpoints.get("right_dataset"))
        if (
            not isinstance(left_fields, list)
            or not isinstance(right_fields, list)
            or not set(left_keys) <= set(left_fields)
            or not set(right_keys) <= set(right_fields)
        ):
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        result[relation_id] = {
            "left_keys": list(left_keys),
            "right_keys": list(right_keys),
        }
    return {key: result[key] for key in sorted(result)}


def _manifest_relation_policies(manifest: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    inventories = manifest.get("inventories")
    raw_policies = inventories.get("relation_policies") if isinstance(inventories, Mapping) else None
    raw_relations = inventories.get("relations") if isinstance(inventories, Mapping) else None
    if not isinstance(raw_policies, Mapping) or not isinstance(raw_relations, list):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    policies: dict[str, dict[str, str]] = {}
    required_keys = set(_RELATION_POLICY_VALUES)
    for relation_id, raw_card in raw_policies.items():
        if (
            not isinstance(relation_id, str)
            or relation_id not in raw_relations
            or not isinstance(raw_card, Mapping)
            or set(raw_card) != required_keys
        ):
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        card: dict[str, str] = {}
        for key in _RELATION_POLICY_VALUES:
            value = raw_card.get(key)
            if not isinstance(value, str) or value not in _RELATION_POLICY_VALUES[key]:
                raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
            card[key] = value
        policies[relation_id] = card
    return {key: policies[key] for key in sorted(policies)}


def _manifest_grain_contract(
    manifest: Mapping[str, Any],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    inventories = manifest.get("inventories")
    raw_grains = inventories.get("grains") if isinstance(inventories, Mapping) else None
    raw_keys = inventories.get("grain_keys") if isinstance(inventories, Mapping) else None
    raw_display = inventories.get("grain_display_fields") if isinstance(inventories, Mapping) else None
    raw_fields = inventories.get("fields") if isinstance(inventories, Mapping) else None
    if (
        not isinstance(raw_grains, list)
        or not isinstance(raw_keys, Mapping)
        or not isinstance(raw_display, Mapping)
        or not isinstance(raw_fields, list)
        or sorted(raw_keys) != raw_grains
        or (raw_display and set(raw_display) != set(raw_grains))
    ):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    registered_fields = set(raw_fields)
    keys: dict[str, list[str]] = {}
    display: dict[str, list[str]] = {}
    for grain_id in raw_grains:
        values = raw_keys.get(grain_id)
        if (
            not isinstance(grain_id, str)
            or not isinstance(values, list)
            or not values
            or len(values) != len(set(values))
            or not all(isinstance(value, str) and value in registered_fields for value in values)
        ):
            raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
        keys[grain_id] = list(values)
        if raw_display:
            display_values = raw_display.get(grain_id)
            if (
                not isinstance(display_values, list)
                or len(display_values) != len(set(display_values))
                or not all(isinstance(value, str) and value in registered_fields for value in display_values)
            ):
                raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
            display[grain_id] = list(display_values)
    return keys, display


def _draft_alias_target_index(draft: Mapping[str, Any]) -> dict[str, set[str]]:
    """Return registered target types keyed by target ID.

    A field repeated in multiple datasets remains one ``field`` target.  The
    same ID registered as, for example, both a field and a metric is ambiguous
    for shorthand and therefore retains both types in the index.
    """

    index: dict[str, set[str]] = {}

    def add(target_key: Any, target_type: str) -> None:
        if isinstance(target_key, str):
            index.setdefault(target_key, set()).add(target_type)

    for section, target_type in _ALIAS_TARGET_SECTIONS:
        cards = draft.get(section)
        if cards is None:
            continue
        if not isinstance(cards, Mapping):
            raise AuthoringSourceManifestError(
                "authoring_alias_target_registry_invalid",
                {"section": section},
            )
        for target_key in cards:
            add(target_key, target_type)

    datasets = draft.get("datasets")
    if isinstance(datasets, Mapping):
        for dataset in datasets.values():
            if not isinstance(dataset, Mapping):
                continue
            fields = dataset.get("fields")
            if fields is None:
                continue
            if not isinstance(fields, Mapping):
                raise AuthoringSourceManifestError(
                    "authoring_alias_target_registry_invalid",
                    {"section": "datasets.fields"},
                )
            for field_key in fields:
                add(field_key, "field")
    return index


def _alias_target_index_with_context(
    draft: Mapping[str, Any],
    target_context: Mapping[str, Any] | None = None,
) -> dict[str, set[str]]:
    """Union read-only target namespaces without copying context into output."""

    index = _draft_alias_target_index(draft)
    if target_context is None:
        return index
    if not isinstance(target_context, Mapping):
        raise AuthoringSourceManifestError("authoring_target_context_invalid")
    for target_key, target_types in _draft_alias_target_index(target_context).items():
        index.setdefault(target_key, set()).update(target_types)
    return index


def _mapping_upsert(base: Mapping[str, Any], patch: Mapping[str, Any]) -> dict[str, Any]:
    result = deepcopy(dict(base))
    for key, value in patch.items():
        if isinstance(result.get(key), Mapping) and isinstance(value, Mapping):
            result[key] = _mapping_upsert(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _merge_alias_values(base_values: Any, patch_values: Any, *, alias_id: str) -> list[Any]:
    """Preserve legacy alias cards while appending source-sealed text values.

    Generic v2 packages normally store alias values as strings.  A migrated v5
    package may retain ``{"text": ..., "priority": ...}`` value cards.  Section
    authoring must not discard those priorities merely because a new alias is
    supplied in the compact string form.
    """

    if not isinstance(base_values, list) or not isinstance(patch_values, list):
        raise AuthoringSourceManifestError(
            "authoring_alias_card_invalid",
            {"alias_sha256": _safe_value_sha256(alias_id)},
        )

    def text_of(value: Any, *, allow_mapping: bool) -> str:
        if isinstance(value, str):
            return value
        if allow_mapping and isinstance(value, Mapping) and isinstance(value.get("text"), str):
            return str(value["text"])
        raise AuthoringSourceManifestError(
            "authoring_alias_card_invalid",
            {"alias_sha256": _safe_value_sha256(alias_id)},
        )

    if all(isinstance(value, str) for value in base_values):
        if not all(isinstance(value, str) for value in patch_values):
            raise AuthoringSourceManifestError(
                "authoring_alias_card_invalid",
                {"alias_sha256": _safe_value_sha256(alias_id)},
            )
        return sorted(set(base_values) | set(patch_values))

    merged = deepcopy(base_values)
    seen = {_normalized_alias(text_of(value, allow_mapping=True)) for value in base_values}
    additions: list[str] = []
    for value in patch_values:
        text = text_of(value, allow_mapping=False)
        normalized = _normalized_alias(text)
        if normalized not in seen:
            seen.add(normalized)
            additions.append(text)
    merged.extend(sorted(additions, key=lambda value: (_normalized_alias(value), value)))
    return merged


def _normalize_dataset_field_roles(
    manifest: Mapping[str, Any],
    draft: dict[str, Any],
) -> None:
    """Normalize field roles only against dataset/field roles sealed in source."""

    expected_roles = _manifest_field_roles(manifest)
    datasets = draft.get("datasets")
    if not isinstance(datasets, Mapping):
        return
    for dataset_id, raw_dataset in datasets.items():
        fields = raw_dataset.get("fields") if isinstance(raw_dataset, Mapping) else None
        if not isinstance(fields, Mapping):
            continue
        for field_id, raw_field in fields.items():
            roles = raw_field.get("roles") if isinstance(raw_field, Mapping) else None
            if (roles is None or roles == []) and field_id not in expected_roles.get(dataset_id, {}):
                raise AuthoringSourceManifestError(
                    "authoring_field_role_inventory_missing",
                    {
                        "dataset_sha256": _safe_value_sha256(dataset_id),
                        "field_sha256": _safe_value_sha256(field_id),
                    },
                )
    for dataset_id, fields_by_id in expected_roles.items():
        dataset = datasets.get(dataset_id)
        if not isinstance(dataset, Mapping):
            continue
        fields = dataset.get("fields")
        if not isinstance(fields, Mapping):
            continue
        for field_id, sealed_roles in fields_by_id.items():
            field = fields.get(field_id)
            if not isinstance(field, dict):
                continue
            raw_roles = field.get("roles")
            if raw_roles is None or raw_roles == []:
                field["roles"] = deepcopy(sealed_roles)
                continue
            if not isinstance(raw_roles, list):
                raise AuthoringSourceManifestError(
                    "authoring_field_role_value_invalid",
                    {
                        "dataset_sha256": _safe_value_sha256(dataset_id),
                        "field_sha256": _safe_value_sha256(field_id),
                    },
                )
            normalized: list[str] = []
            for raw_role in raw_roles:
                if not isinstance(raw_role, str):
                    raise AuthoringSourceManifestError(
                        "authoring_field_role_value_invalid",
                        {
                            "dataset_sha256": _safe_value_sha256(dataset_id),
                            "field_sha256": _safe_value_sha256(field_id),
                            "role_sha256": _safe_value_sha256(raw_role),
                        },
                    )
                candidates = [raw_role, raw_role.replace("-", "_")]
                if raw_role.endswith("_fields"):
                    candidates.append(raw_role[: -len("_fields")])
                role = next((value for value in candidates if value in sealed_roles), "")
                if not role:
                    raise AuthoringSourceManifestError(
                        "authoring_field_role_value_invalid",
                        {
                            "dataset_sha256": _safe_value_sha256(dataset_id),
                            "field_sha256": _safe_value_sha256(field_id),
                            "role_sha256": _safe_value_sha256(raw_role),
                        },
                    )
                if role not in normalized:
                    normalized.append(role)
            if set(normalized) != set(sealed_roles):
                raise AuthoringSourceManifestError(
                    "authoring_field_role_mismatch",
                    {
                        "dataset_sha256": _safe_value_sha256(dataset_id),
                        "field_sha256": _safe_value_sha256(field_id),
                        "expected_sha256": _canonical_sha256(sealed_roles),
                        "actual_sha256": _canonical_sha256(normalized),
                    },
                )
            field["roles"] = deepcopy(sealed_roles)


def _normalize_dataset_patch_against_base(
    manifest: Mapping[str, Any],
    draft: dict[str, Any],
    base_draft: Mapping[str, Any] | None,
) -> None:
    """Close provider dataset/field keys against source inventory and base.

    Existing physical column names and physical aliases may be mapped back to
    one canonical field only when that mapping is unique.  Existing cards are
    deep-merged before schema validation so an annotation-sized provider patch
    cannot accidentally erase required execution semantics.  A genuinely new
    dataset or field remains possible only when its identifier is explicitly
    sealed by the reviewed source manifest.
    """

    datasets = draft.get("datasets")
    if datasets is None:
        return
    if not isinstance(datasets, Mapping):
        raise AuthoringSourceManifestError("authoring_dataset_registry_invalid")

    inventories = manifest.get("inventories")
    if not isinstance(inventories, Mapping):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    raw_declared_datasets = inventories.get("datasets")
    raw_declared_fields = inventories.get("dataset_fields")
    if not isinstance(raw_declared_datasets, list) or not isinstance(raw_declared_fields, Mapping):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    declared_datasets = {str(value) for value in raw_declared_datasets}
    declared_fields = {
        str(dataset_id): {str(value) for value in values}
        for dataset_id, values in raw_declared_fields.items()
        if isinstance(dataset_id, str) and isinstance(values, list)
    }

    base_datasets = (
        base_draft.get("datasets")
        if isinstance(base_draft, Mapping) and isinstance(base_draft.get("datasets"), Mapping)
        else {}
    )
    normalized_datasets: dict[str, Any] = {}
    for raw_dataset_id, raw_dataset in datasets.items():
        dataset_id = str(raw_dataset_id)
        if dataset_id not in declared_datasets:
            raise AuthoringSourceManifestError(
                "authoring_dataset_target_unknown",
                {"dataset_sha256": _safe_value_sha256(dataset_id)},
            )
        if not isinstance(raw_dataset, Mapping):
            raise AuthoringSourceManifestError(
                "authoring_dataset_card_invalid",
                {"dataset_sha256": _safe_value_sha256(dataset_id)},
            )

        provider_dataset = deepcopy(dict(raw_dataset))
        base_dataset = base_datasets.get(dataset_id)
        base_fields = (
            base_dataset.get("fields")
            if isinstance(base_dataset, Mapping) and isinstance(base_dataset.get("fields"), Mapping)
            else {}
        )
        provider_fields = provider_dataset.get("fields")
        if provider_fields is not None:
            if not isinstance(provider_fields, Mapping):
                raise AuthoringSourceManifestError(
                    "authoring_dataset_fields_invalid",
                    {"dataset_sha256": _safe_value_sha256(dataset_id)},
                )
            normalized_fields: dict[str, Any] = {}
            allowed_fields = declared_fields.get(dataset_id, set())
            for raw_field_id, raw_field in provider_fields.items():
                field_id = str(raw_field_id)
                canonical_field = field_id if field_id in base_fields else ""
                resolved_from_noncanonical_key = False
                if not canonical_field and base_fields:
                    token = field_id.casefold()
                    matches: list[str] = []
                    for candidate_id, candidate_card in base_fields.items():
                        if not isinstance(candidate_card, Mapping):
                            continue
                        physical_values = [
                            str(candidate_id),
                            str(candidate_card.get("physical_column") or ""),
                            *[
                                str(value)
                                for value in (candidate_card.get("physical_aliases") or [])
                                if isinstance(value, str)
                            ],
                        ]
                        if token and token in {value.casefold() for value in physical_values if value}:
                            matches.append(str(candidate_id))
                    matches = sorted(set(matches))
                    if len(matches) > 1:
                        raise AuthoringSourceManifestError(
                            "authoring_dataset_field_target_ambiguous",
                            {
                                "dataset_sha256": _safe_value_sha256(dataset_id),
                                "field_sha256": _safe_value_sha256(field_id),
                                "candidate_count": len(matches),
                            },
                        )
                    if matches:
                        canonical_field = matches[0]
                        resolved_from_noncanonical_key = canonical_field != field_id
                if not canonical_field:
                    canonical_field = field_id
                if canonical_field not in allowed_fields:
                    raise AuthoringSourceManifestError(
                        "authoring_dataset_field_target_unknown",
                        {
                            "dataset_sha256": _safe_value_sha256(dataset_id),
                            "field_sha256": _safe_value_sha256(field_id),
                        },
                    )
                if canonical_field in normalized_fields:
                    raise AuthoringSourceManifestError(
                        "authoring_dataset_field_target_duplicate",
                        {
                            "dataset_sha256": _safe_value_sha256(dataset_id),
                            "field_sha256": _safe_value_sha256(canonical_field),
                        },
                    )
                base_field = base_fields.get(canonical_field)
                if resolved_from_noncanonical_key:
                    if not isinstance(base_field, Mapping) or not isinstance(raw_field, Mapping):
                        raise AuthoringSourceManifestError(
                            "authoring_dataset_physical_alias_rebind_forbidden",
                            {
                                "dataset_sha256": _safe_value_sha256(dataset_id),
                                "field_sha256": _safe_value_sha256(field_id),
                                "canonical_field_sha256": _safe_value_sha256(canonical_field),
                            },
                        )
                    raw_field_value = dict(raw_field)
                    if raw_field_value and raw_field_value != dict(base_field):
                        raise AuthoringSourceManifestError(
                            "authoring_dataset_physical_alias_rebind_forbidden",
                            {
                                "dataset_sha256": _safe_value_sha256(dataset_id),
                                "field_sha256": _safe_value_sha256(field_id),
                                "canonical_field_sha256": _safe_value_sha256(canonical_field),
                            },
                        )
                    # A physical name is a read-only reference to its canonical
                    # base card.  Only the source-declared canonical key may
                    # carry an actual field-card delta.
                    raw_field = {}
                normalized_fields[canonical_field] = (
                    _mapping_upsert(base_field, raw_field)
                    if isinstance(base_field, Mapping) and isinstance(raw_field, Mapping)
                    else deepcopy(raw_field)
                )
            provider_dataset["fields"] = {
                key: normalized_fields[key] for key in sorted(normalized_fields)
            }

        normalized_datasets[dataset_id] = (
            _mapping_upsert(base_dataset, provider_dataset)
            if isinstance(base_dataset, Mapping)
            else provider_dataset
        )
    draft["datasets"] = {
        key: normalized_datasets[key] for key in sorted(normalized_datasets)
    }


def _normalize_relation_policies(
    manifest: Mapping[str, Any],
    draft: dict[str, Any],
) -> None:
    """Fill or canonicalize only relation policies sealed in source."""

    expected_policies = _manifest_relation_policies(manifest)
    relations = draft.get("relations")
    if relations is None:
        return
    if not isinstance(relations, Mapping):
        raise AuthoringSourceManifestError("authoring_relation_registry_invalid")
    for relation_id, raw_relation in relations.items():
        if not isinstance(raw_relation, Mapping) or relation_id in expected_policies:
            continue
        if any(
            raw_relation.get(key) is None
            or (isinstance(raw_relation.get(key), str) and not raw_relation.get(key).strip())
            for key in _RELATION_POLICY_VALUES
        ):
            raise AuthoringSourceManifestError(
                "authoring_relation_policy_inventory_missing",
                {"relation_sha256": _safe_value_sha256(relation_id)},
            )
    for relation_id, sealed_policy in expected_policies.items():
        relation = relations.get(relation_id)
        if not isinstance(relation, dict):
            continue
        for policy_key, expected_value in sealed_policy.items():
            legacy_key = "type" if policy_key == "join_type" else ""
            actual_value = relation.get(policy_key)
            legacy_present = bool(legacy_key and legacy_key in relation)
            legacy_value = relation.get(legacy_key) if legacy_present else None
            supplied = [
                value
                for value in (actual_value, legacy_value)
                if value is not None and not (isinstance(value, str) and not value.strip())
            ]
            for raw_value in supplied:
                normalized_value = raw_value.replace("-", "_") if isinstance(raw_value, str) else raw_value
                if normalized_value != expected_value:
                    raise AuthoringSourceManifestError(
                        "authoring_relation_policy_mismatch",
                        {
                            "relation_sha256": _safe_value_sha256(relation_id),
                            "policy_key": policy_key,
                            "expected_sha256": _safe_value_sha256(expected_value),
                            "actual_sha256": _safe_value_sha256(raw_value),
                        },
                    )
            relation[policy_key] = expected_value
            if legacy_present:
                relation.pop(legacy_key, None)


def _normalize_relation_keys(
    manifest: Mapping[str, Any],
    draft: dict[str, Any],
) -> None:
    """Fill relation key lists only from exact source-sealed mappings."""

    expected_keys = _manifest_relation_keys(manifest)
    relations = draft.get("relations")
    datasets = draft.get("datasets")
    if relations is None:
        return
    if not isinstance(relations, Mapping):
        raise AuthoringSourceManifestError("authoring_relation_registry_invalid")

    def blank(value: Any) -> bool:
        return value is None or value == [] or (isinstance(value, str) and not value.strip())

    def key_list(value: Any) -> list[str] | None:
        if isinstance(value, str) and value.strip():
            return [item.strip() for item in value.split("|") if item.strip()]
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return list(value)
        return None

    for relation_id, raw_relation in relations.items():
        if not isinstance(raw_relation, Mapping) or relation_id in expected_keys:
            continue
        if blank(raw_relation.get("left_keys")) or blank(raw_relation.get("right_keys")):
            raise AuthoringSourceManifestError(
                "authoring_relation_key_inventory_missing",
                {"relation_sha256": _safe_value_sha256(relation_id)},
            )

    for relation_id, sealed in expected_keys.items():
        relation = relations.get(relation_id)
        if not isinstance(relation, dict):
            continue
        left_dataset = str(relation.get("left_dataset") or "")
        right_dataset = str(relation.get("right_dataset") or "")
        left_fields = (
            ((datasets.get(left_dataset) or {}).get("fields") or {})
            if isinstance(datasets, Mapping) and isinstance(datasets.get(left_dataset), Mapping)
            else {}
        )
        right_fields = (
            ((datasets.get(right_dataset) or {}).get("fields") or {})
            if isinstance(datasets, Mapping) and isinstance(datasets.get(right_dataset), Mapping)
            else {}
        )
        if not set(sealed["left_keys"]) <= set(left_fields) or not set(sealed["right_keys"]) <= set(right_fields):
            raise AuthoringSourceManifestError(
                "authoring_relation_key_field_unknown",
                {"relation_sha256": _safe_value_sha256(relation_id)},
            )

        legacy_present = "keys" in relation
        legacy_keys = key_list(relation.get("keys")) if legacy_present else None
        if legacy_present and (
            legacy_keys is None
            or legacy_keys != sealed["left_keys"]
            or legacy_keys != sealed["right_keys"]
        ):
            raise AuthoringSourceManifestError(
                "authoring_relation_key_mismatch",
                {"relation_sha256": _safe_value_sha256(relation_id), "key_side": "legacy_keys"},
            )

        mappings_present = "key_mappings" in relation
        mappings = relation.get("key_mappings")
        if mappings_present:
            if not isinstance(mappings, list) or not all(isinstance(item, Mapping) for item in mappings):
                raise AuthoringSourceManifestError(
                    "authoring_relation_key_mismatch",
                    {"relation_sha256": _safe_value_sha256(relation_id), "key_side": "key_mappings"},
                )
            mapped_left = [str(item.get("left") or "") for item in mappings]
            mapped_right = [str(item.get("right") or "") for item in mappings]
            if mapped_left != sealed["left_keys"] or mapped_right != sealed["right_keys"]:
                raise AuthoringSourceManifestError(
                    "authoring_relation_key_mismatch",
                    {"relation_sha256": _safe_value_sha256(relation_id), "key_side": "key_mappings"},
                )

        for key_side in ("left_keys", "right_keys"):
            actual = relation.get(key_side)
            if not blank(actual):
                normalized = key_list(actual)
                if normalized != sealed[key_side]:
                    raise AuthoringSourceManifestError(
                        "authoring_relation_key_mismatch",
                        {"relation_sha256": _safe_value_sha256(relation_id), "key_side": key_side},
                    )
            relation[key_side] = deepcopy(sealed[key_side])
        if legacy_present:
            relation.pop("keys", None)
        if mappings_present:
            relation.pop("key_mappings", None)


def _normalize_relation_endpoints(
    manifest: Mapping[str, Any],
    draft: dict[str, Any],
) -> None:
    """Fill only source-sealed blank relation endpoints on a draft copy."""

    expected_endpoints = _manifest_relation_endpoints(manifest)
    relations = draft.get("relations")
    if relations is None:
        return
    if not isinstance(relations, Mapping):
        raise AuthoringSourceManifestError("authoring_relation_registry_invalid")
    datasets = draft.get("datasets")
    dataset_ids = set(datasets) if isinstance(datasets, Mapping) else set()

    def blank(value: Any) -> bool:
        return value is None or (isinstance(value, str) and not value.strip())

    for relation_id, raw_card in relations.items():
        if not isinstance(relation_id, str) or not isinstance(raw_card, dict):
            if relation_id in expected_endpoints:
                raise AuthoringSourceManifestError(
                    "authoring_relation_endpoint_card_invalid",
                    {"relation_sha256": _safe_value_sha256(relation_id)},
                )
            continue
        expected = expected_endpoints.get(relation_id)
        standard_missing = any(
            key not in raw_card or blank(raw_card.get(key))
            for key in ("left_dataset", "right_dataset")
        )
        if expected is None:
            if standard_missing:
                raise AuthoringSourceManifestError(
                    "authoring_relation_endpoint_inventory_missing",
                    {"relation_sha256": _safe_value_sha256(relation_id)},
                )
            continue

        missing_datasets = sorted(
            value for value in expected.values() if value not in dataset_ids
        )
        if missing_datasets:
            raise AuthoringSourceManifestError(
                "authoring_relation_endpoint_dataset_unknown",
                {
                    "relation_sha256": _safe_value_sha256(relation_id),
                    "dataset_sha256": [_safe_value_sha256(value) for value in missing_datasets],
                },
            )

        for standard_key, legacy_key in (
            ("left_dataset", "left"),
            ("right_dataset", "right"),
        ):
            expected_value = expected[standard_key]
            actual_value = raw_card.get(standard_key)
            legacy_present = legacy_key in raw_card
            legacy_value = raw_card.get(legacy_key)
            for supplied_value in (
                *( [actual_value] if not blank(actual_value) else [] ),
                *( [legacy_value] if legacy_present and not blank(legacy_value) else [] ),
            ):
                if not isinstance(supplied_value, str) or supplied_value != expected_value:
                    raise AuthoringSourceManifestError(
                        "authoring_relation_endpoint_mismatch",
                        {
                            "relation_sha256": _safe_value_sha256(relation_id),
                            "endpoint": standard_key,
                            "expected_sha256": _safe_value_sha256(expected_value),
                            "actual_sha256": _safe_value_sha256(supplied_value),
                        },
                    )
            if blank(actual_value):
                raw_card[standard_key] = expected_value
            if legacy_present:
                raw_card.pop(legacy_key, None)


def _normalize_grains(
    manifest: Mapping[str, Any],
    draft: dict[str, Any],
    target_context: Mapping[str, Any] | None = None,
) -> None:
    """Normalize grain keys/display fields only from the sealed source contract."""

    expected_keys, expected_display = _manifest_grain_contract(manifest)
    grains = draft.get("grains")
    if grains is None:
        return
    if not isinstance(grains, Mapping):
        raise AuthoringSourceManifestError("authoring_grain_registry_invalid")
    unbacked = sorted(str(grain_id) for grain_id in grains if grain_id not in expected_keys)
    if unbacked:
        raise AuthoringSourceManifestError(
            "authoring_grain_inventory_unbacked",
            {"grain_sha256": [_safe_value_sha256(value) for value in unbacked]},
        )
    target_index = _alias_target_index_with_context(draft, target_context)

    def blank(value: Any) -> bool:
        return value is None or value == [] or (isinstance(value, str) and not value.strip())

    def field_list(value: Any) -> list[str] | None:
        if isinstance(value, str) and value.strip():
            return [item.strip() for item in value.split("|") if item.strip()]
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return list(value)
        return None

    for grain_id, sealed_keys in expected_keys.items():
        grain = grains.get(grain_id)
        if not isinstance(grain, dict):
            continue
        unknown_fields = [
            value
            for value in [*sealed_keys, *expected_display.get(grain_id, [])]
            if "field" not in target_index.get(value, set())
        ]
        if unknown_fields:
            raise AuthoringSourceManifestError(
                "authoring_grain_field_unknown",
                {
                    "grain_sha256": _safe_value_sha256(grain_id),
                    "field_sha256": [_safe_value_sha256(value) for value in unknown_fields],
                },
            )

        legacy_key_names = [name for name in ("key", "grain_keys") if name in grain]
        for legacy_name in legacy_key_names:
            if field_list(grain.get(legacy_name)) != sealed_keys:
                raise AuthoringSourceManifestError(
                    "authoring_grain_key_mismatch",
                    {"grain_sha256": _safe_value_sha256(grain_id)},
                )
        actual_keys = grain.get("keys")
        if not blank(actual_keys) and field_list(actual_keys) != sealed_keys:
            raise AuthoringSourceManifestError(
                "authoring_grain_key_mismatch",
                {"grain_sha256": _safe_value_sha256(grain_id)},
            )
        grain["keys"] = deepcopy(sealed_keys)
        for legacy_name in legacy_key_names:
            grain.pop(legacy_name, None)

        if expected_display:
            sealed_display = expected_display[grain_id]
            legacy_display_names = [
                name for name in ("display", "display_field") if name in grain
            ]
            for legacy_name in legacy_display_names:
                if field_list(grain.get(legacy_name)) != sealed_display:
                    raise AuthoringSourceManifestError(
                        "authoring_grain_display_mismatch",
                        {"grain_sha256": _safe_value_sha256(grain_id)},
                    )
            actual_display = grain.get("display_fields")
            if not blank(actual_display) and field_list(actual_display) != sealed_display:
                raise AuthoringSourceManifestError(
                    "authoring_grain_display_mismatch",
                    {"grain_sha256": _safe_value_sha256(grain_id)},
                )
            grain["display_fields"] = deepcopy(sealed_display)
            for legacy_name in legacy_display_names:
                grain.pop(legacy_name, None)


def _complete_manifest_aliases(
    manifest: Mapping[str, Any],
    draft: dict[str, Any],
    target_context: Mapping[str, Any] | None = None,
) -> None:
    """Complete only missing source-declared aliases on uniquely typed targets."""

    expected_targets = _manifest_alias_targets(manifest)
    aliases = draft.get("aliases")
    if not isinstance(aliases, dict):
        raise AuthoringSourceManifestError("authoring_aliases_not_object")
    target_index = _alias_target_index_with_context(draft, target_context)

    cards_by_target: dict[tuple[str, str], list[tuple[str, dict[str, Any]]]] = {}
    explicit_targets_by_alias: dict[str, set[str]] = {}
    for alias_id, raw_card in aliases.items():
        if not isinstance(alias_id, str) or not isinstance(raw_card, dict):
            continue
        target_type = raw_card.get("target_type")
        target_key = raw_card.get("target_key")
        if isinstance(target_type, str) and isinstance(target_key, str):
            cards_by_target.setdefault((target_type, target_key), []).append((alias_id, raw_card))
            values = raw_card.get("values")
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, str):
                        explicit_targets_by_alias.setdefault(_normalized_alias(value), set()).add(target_key)
    for (target_type, target_key), cards in cards_by_target.items():
        if len(cards) > 1:
            raise AuthoringSourceManifestError(
                "authoring_alias_multiple_target_cards",
                {"target_type": target_type, "target_sha256": _safe_value_sha256(target_key)},
            )

    actual_inventory = _draft_inventory(draft, ())
    actual_targets_by_alias: dict[str, set[str]] = {}
    for binding in actual_inventory["alias_bindings"]:
        actual_targets_by_alias.setdefault(binding["alias"], set()).add(binding["target"])

    for alias, expected_target in sorted(expected_targets.items()):
        actual_targets = actual_targets_by_alias.get(alias, set())
        if expected_target in actual_targets:
            continue
        explicit_targets = explicit_targets_by_alias.get(alias, set())
        if explicit_targets and explicit_targets != {expected_target}:
            raise AuthoringSourceManifestError(
                "authoring_alias_label_target_conflict",
                {
                    "alias_sha256": _safe_value_sha256(alias),
                    "expected_target_sha256": _safe_value_sha256(expected_target),
                    "actual_target_sha256": sorted(_safe_value_sha256(value) for value in explicit_targets),
                },
            )
        target_types = sorted(target_index.get(expected_target, set()))
        if not target_types:
            raise AuthoringSourceManifestError(
                "authoring_alias_target_unknown",
                {"target_sha256": _safe_value_sha256(expected_target)},
            )
        if len(target_types) != 1:
            raise AuthoringSourceManifestError(
                "authoring_alias_target_ambiguous",
                {
                    "target_sha256": _safe_value_sha256(expected_target),
                    "target_types": target_types,
                },
            )

        target_type = target_types[0]
        target_pair = (target_type, expected_target)
        cards = cards_by_target.get(target_pair, [])
        if cards:
            _, card = cards[0]
            values = card.get("values")
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                raise AuthoringSourceManifestError(
                    "authoring_alias_card_invalid",
                    {"target_type": target_type, "target_sha256": _safe_value_sha256(expected_target)},
                )
            if alias not in {_normalized_alias(value) for value in values}:
                values.append(alias)
        else:
            canonical_key = f"{target_type}:{expected_target}"
            if canonical_key in aliases:
                raise AuthoringSourceManifestError(
                    "authoring_alias_card_collision",
                    {"target_type": target_type, "target_sha256": _safe_value_sha256(expected_target)},
                )
            card = {
                "target_type": target_type,
                "target_key": expected_target,
                "values": [alias],
            }
            aliases[canonical_key] = card
            cards_by_target[target_pair] = [(canonical_key, card)]
        actual_targets_by_alias[alias] = {expected_target}

    draft["aliases"] = {key: aliases[key] for key in sorted(aliases)}


def normalize_authoring_draft_shorthand(
    manifest: Mapping[str, Any],
    draft: Mapping[str, Any],
    target_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize only source-sealed authoring shorthand before schema checks.

    The model may use a compact string form inside ``draft.aliases``.  This
    function accepts it only when the exact normalized label/target binding was
    extracted from the natural-language source and the target resolves to one
    registered draft namespace.  No target type is guessed.

    Existing object aliases are copied unchanged.  Mixing an object alias with
    shorthand for the same canonical target fails closed instead of silently
    choosing or merging two provider representations.  Multiple backed string
    labels for one target are merged into one deterministic canonical card.

    The same single pre-schema pass also maps the closed field-role synonym
    ``compare_fields`` to schema role ``compare`` and removes duplicate roles.
    All unknown role values remain untouched so schema validation still rejects
    them instead of this helper guessing at provider intent.
    """

    if not isinstance(manifest, Mapping):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    sealed_manifest = _validated_manifest(manifest)
    expected_targets = _manifest_alias_targets(sealed_manifest)
    if not isinstance(draft, Mapping):
        raise AuthoringSourceManifestError("authoring_draft_not_object")

    result = deepcopy(dict(draft))
    _normalize_dataset_field_roles(sealed_manifest, result)
    _normalize_relation_endpoints(sealed_manifest, result)
    _normalize_relation_keys(sealed_manifest, result)
    _normalize_relation_policies(sealed_manifest, result)
    _normalize_grains(sealed_manifest, result, target_context)
    raw_aliases = result.get("aliases")
    if raw_aliases is None:
        raw_aliases = {}
    if not isinstance(raw_aliases, Mapping):
        raise AuthoringSourceManifestError("authoring_aliases_not_object")

    target_index = _alias_target_index_with_context(result, target_context)
    object_aliases: dict[str, Any] = {}
    object_targets: set[tuple[str, str]] = set()
    shorthand: list[tuple[str, str]] = []

    for raw_label, raw_value in raw_aliases.items():
        if not isinstance(raw_label, str):
            raise AuthoringSourceManifestError("authoring_alias_entry_invalid")
        if isinstance(raw_value, Mapping):
            object_aliases[raw_label] = deepcopy(dict(raw_value))
            target_type = raw_value.get("target_type")
            target_key = raw_value.get("target_key")
            if isinstance(target_type, str) and isinstance(target_key, str):
                object_targets.add((target_type, target_key))
            continue
        if isinstance(raw_value, str):
            shorthand.append((raw_label, raw_value))
            continue
        raise AuthoringSourceManifestError(
            "authoring_alias_entry_invalid",
            {"alias_sha256": _safe_value_sha256(raw_label)},
        )

    generated: dict[str, dict[str, Any]] = {}
    for raw_label, raw_target in sorted(shorthand, key=lambda item: (_normalized_alias(item[0]), item[1])):
        alias = _normalized_alias(raw_label)
        expected_target = expected_targets.get(alias)
        if expected_target is None:
            raise AuthoringSourceManifestError(
                "authoring_alias_shorthand_unbacked",
                {"alias_sha256": _safe_value_sha256(alias)},
            )
        if raw_target != expected_target:
            raise AuthoringSourceManifestError(
                "authoring_alias_shorthand_unbacked",
                {
                    "alias_sha256": _safe_value_sha256(alias),
                    "target_sha256": _safe_value_sha256(raw_target),
                },
            )

        target_types = sorted(target_index.get(raw_target, set()))
        if not target_types:
            raise AuthoringSourceManifestError(
                "authoring_alias_target_unknown",
                {"target_sha256": _safe_value_sha256(raw_target)},
            )
        if len(target_types) != 1:
            raise AuthoringSourceManifestError(
                "authoring_alias_target_ambiguous",
                {
                    "target_sha256": _safe_value_sha256(raw_target),
                    "target_types": target_types,
                },
            )

        target_type = target_types[0]
        canonical_key = f"{target_type}:{raw_target}"
        if canonical_key in object_aliases or (target_type, raw_target) in object_targets:
            raise AuthoringSourceManifestError(
                "authoring_alias_object_string_collision",
                {"target_sha256": _safe_value_sha256(raw_target), "target_type": target_type},
            )
        card = generated.setdefault(
            canonical_key,
            {
                "target_type": target_type,
                "target_key": raw_target,
                "values": [],
            },
        )
        card["values"].append(alias)

    for card in generated.values():
        card["values"] = sorted(set(card["values"]))
    result["aliases"] = {
        **{key: object_aliases[key] for key in sorted(object_aliases)},
        **{key: generated[key] for key in sorted(generated)},
    }
    _complete_manifest_aliases(sealed_manifest, result, target_context)
    return result


def normalize_authoring_section_patch_shorthand(
    manifest: Mapping[str, Any],
    patch: Mapping[str, Any],
    authoring_kind: str,
    base_draft: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize only shorthand owned by one bounded authoring Flow.

    Dataset authoring owns only ``datasets``.  Running its response through the
    full-draft normalizer would synthesize an empty ``aliases`` section and then
    make the deterministic ownership gate reject an otherwise valid patch.
    This helper deliberately preserves provider root keys so an explicitly
    emitted cross-owner section is still rejected by ``apply_authoring_section_patch``.

    Main-filter authoring owns aliases and may therefore use the complete
    source-sealed alias normalization.  The full normalizer's empty synthetic
    alias object is removed only when the provider did not emit ``aliases`` and
    the source manifest did not require any aliases to be completed.
    """

    if not isinstance(manifest, Mapping):
        raise AuthoringSourceManifestError("authoring_source_manifest_invalid")
    sealed_manifest = _validated_manifest(manifest)
    if not isinstance(patch, Mapping):
        raise AuthoringSourceManifestError("authoring_draft_not_object")

    kind = str(authoring_kind or "").strip().casefold()
    result = deepcopy(dict(patch))
    if kind == "dataset":
        _normalize_dataset_patch_against_base(sealed_manifest, result, base_draft)
        _normalize_dataset_field_roles(sealed_manifest, result)
        return result
    if kind == "main_filter":
        owned = {"aliases", "entity_groups", "grains", "orderings", "predicates", "recipes"}
        if set(result) - owned:
            # Preserve an explicit cross-owner provider response byte-for-byte
            # so the downstream ownership gate rejects it.
            return result
        if not isinstance(base_draft, Mapping):
            raise AuthoringSourceManifestError("authoring_target_context_invalid")
        base_snapshot = deepcopy(dict(base_draft))
        base_aliases = base_snapshot.get("aliases")
        if not isinstance(base_aliases, Mapping):
            raise AuthoringSourceManifestError("authoring_aliases_not_object")

        provider_aliases = result.get("aliases")
        if isinstance(provider_aliases, Mapping):
            prepared_aliases: dict[str, Any] = {}
            for alias_id, raw_card in provider_aliases.items():
                base_card = base_aliases.get(alias_id)
                if isinstance(base_card, Mapping) and isinstance(raw_card, Mapping):
                    prepared_aliases[str(alias_id)] = _mapping_upsert(base_card, raw_card)
                else:
                    prepared_aliases[str(alias_id)] = deepcopy(raw_card)
            result["aliases"] = prepared_aliases

        result = normalize_authoring_draft_shorthand(
            sealed_manifest,
            result,
            target_context=base_snapshot,
        )
        normalized_aliases = result.get("aliases")
        if isinstance(normalized_aliases, Mapping):
            alias_delta: dict[str, Any] = {}
            for alias_id, raw_card in normalized_aliases.items():
                card = deepcopy(raw_card)
                base_card = base_aliases.get(alias_id)
                if isinstance(base_card, Mapping) and isinstance(card, Mapping):
                    for identity_key in ("target_type", "target_key"):
                        base_value = base_card.get(identity_key)
                        card_value = card.get(identity_key)
                        if base_value != card_value:
                            raise AuthoringSourceManifestError(
                                "authoring_alias_target_mismatch",
                                {
                                    "alias_sha256": _safe_value_sha256(alias_id),
                                    "identity_key": identity_key,
                                },
                            )
                    card["values"] = _merge_alias_values(
                        base_card.get("values"),
                        card.get("values"),
                        alias_id=str(alias_id),
                    )
                if base_card != card:
                    alias_delta[str(alias_id)] = card
            if alias_delta:
                result["aliases"] = {key: alias_delta[key] for key in sorted(alias_delta)}
            else:
                result.pop("aliases", None)
        if base_snapshot != dict(base_draft):
            raise AuthoringSourceManifestError("authoring_target_context_mutated")
        return result
    raise AuthoringSourceManifestError(
        "authoring_section_patch_kind_invalid",
        {"authoring_kind": kind},
    )


def normalize_draft_alias_shorthand(
    manifest: Mapping[str, Any],
    draft: Mapping[str, Any],
) -> dict[str, Any]:
    """Backward-compatible name for :func:`normalize_authoring_draft_shorthand`."""

    return normalize_authoring_draft_shorthand(manifest, draft)


def _draft_operations(draft: Mapping[str, Any], supported_operations: Iterable[str]) -> list[str]:
    values: list[str] = [str(value) for value in supported_operations]
    for key in ("operations", "allowed_operations"):
        raw = draft.get(key)
        if isinstance(raw, Mapping):
            values.extend(str(value) for value in raw)
        elif isinstance(raw, list):
            values.extend(str(value) for value in raw)
    output_profile = draft.get("output_profile")
    if isinstance(output_profile, Mapping):
        raw = output_profile.get("allowed_operations")
        if isinstance(raw, Mapping):
            values.extend(str(value) for value in raw)
        elif isinstance(raw, list):
            values.extend(str(value) for value in raw)

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            if isinstance(value.get("op"), str):
                values.append(str(value["op"]))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(draft.get("recipes"))
    return _bounded(values, "operations")


def _draft_inventory(draft: Mapping[str, Any], supported_operations: Iterable[str]) -> dict[str, Any]:
    if not isinstance(draft, Mapping):
        raise AuthoringSourceManifestError("authoring_draft_not_object")
    datasets_value = draft.get("datasets")
    datasets = datasets_value if isinstance(datasets_value, Mapping) else {}
    dataset_ids = _bounded((str(value) for value in datasets), "datasets")
    dataset_fields: dict[str, list[str]] = {}
    field_roles: dict[str, dict[str, list[str]]] = {}
    for dataset_id in dataset_ids:
        dataset = datasets.get(dataset_id)
        fields = dataset.get("fields") if isinstance(dataset, Mapping) else {}
        dataset_fields[dataset_id] = _bounded(
            (str(value) for value in fields) if isinstance(fields, Mapping) else (),
            "fields",
        )
        if isinstance(fields, Mapping):
            for field_id, raw_field in fields.items():
                roles = raw_field.get("roles") if isinstance(raw_field, Mapping) else None
                if isinstance(roles, list) and all(isinstance(value, str) for value in roles):
                    canonical = [role for role in _FIELD_ROLE_ORDER if role in roles]
                    canonical.extend(sorted(set(roles) - _FIELD_ROLE_SET))
                    field_roles.setdefault(dataset_id, {})[str(field_id)] = canonical
    root_fields = draft.get("fields")
    unique_fields = {
        field
        for values in dataset_fields.values()
        for field in values
    }
    if isinstance(root_fields, Mapping):
        unique_fields.update(str(value) for value in root_fields)

    def keys(name: str, kind: str) -> list[str]:
        value = draft.get(name)
        return _bounded((str(item) for item in value) if isinstance(value, Mapping) else (), kind)

    grain_keys: dict[str, list[str]] = {}
    grain_display_fields: dict[str, list[str]] = {}
    raw_grains = draft.get("grains")
    if isinstance(raw_grains, Mapping):
        for grain_id, raw_grain in raw_grains.items():
            if not isinstance(grain_id, str) or not isinstance(raw_grain, Mapping):
                continue
            raw_keys = raw_grain.get("keys")
            if isinstance(raw_keys, list) and raw_keys and all(isinstance(value, str) for value in raw_keys):
                grain_keys[grain_id] = list(raw_keys)
            raw_display = raw_grain.get("display_fields")
            if raw_display is None:
                grain_display_fields[grain_id] = []
            elif isinstance(raw_display, list) and all(isinstance(value, str) for value in raw_display):
                grain_display_fields[grain_id] = list(raw_display)

    relation_endpoints: dict[str, dict[str, str]] = {}
    relation_keys: dict[str, dict[str, list[str]]] = {}
    relation_policies: dict[str, dict[str, str]] = {}
    raw_relations = draft.get("relations")
    if isinstance(raw_relations, Mapping):
        for relation_id, raw_relation in raw_relations.items():
            if not isinstance(relation_id, str) or not isinstance(raw_relation, Mapping):
                continue
            left_dataset = raw_relation.get("left_dataset")
            right_dataset = raw_relation.get("right_dataset")
            if isinstance(left_dataset, str) and left_dataset and isinstance(right_dataset, str) and right_dataset:
                relation_endpoints[relation_id] = {
                    "left_dataset": left_dataset,
                    "right_dataset": right_dataset,
                }
            left_keys = raw_relation.get("left_keys")
            right_keys = raw_relation.get("right_keys")
            if (
                isinstance(left_keys, list)
                and isinstance(right_keys, list)
                and left_keys
                and len(left_keys) == len(right_keys)
                and all(isinstance(value, str) for value in [*left_keys, *right_keys])
            ):
                relation_keys[relation_id] = {
                    "left_keys": list(left_keys),
                    "right_keys": list(right_keys),
                }
            policy = {
                key: raw_relation.get(key)
                for key in _RELATION_POLICY_VALUES
            }
            if all(isinstance(value, str) and value for value in policy.values()):
                relation_policies[relation_id] = policy

    alias_pairs: set[tuple[str, str]] = set()

    def add_alias_card(target: str, card: Any) -> None:
        if not isinstance(card, Mapping) or not re.fullmatch(_IDENTIFIER, str(target or "")):
            return
        raw_aliases = card.get("aliases")
        if not isinstance(raw_aliases, list):
            raw_aliases = card.get("values")
        if not isinstance(raw_aliases, list):
            return
        for raw_alias in raw_aliases:
            alias_text = raw_alias if isinstance(raw_alias, str) else None
            if (
                alias_text is None
                and isinstance(raw_alias, Mapping)
                and isinstance(raw_alias.get("text"), str)
            ):
                # Migrated v5 packages retain ranked alias value cards such
                # as {"text": "...", "priority": 100}.  Coverage consumes
                # only the exact string value; it never coerces nested values
                # or lets a value card rebind the enclosing target identity.
                alias_text = raw_alias["text"]
            if alias_text is not None:
                alias_pairs.add((_normalized_alias(alias_text), str(target)))

    for dataset_id in dataset_ids:
        dataset = datasets.get(dataset_id)
        add_alias_card(dataset_id, dataset)
        fields = dataset.get("fields") if isinstance(dataset, Mapping) else {}
        if isinstance(fields, Mapping):
            for field_id, card in fields.items():
                add_alias_card(str(field_id), card)
    for section in ("fields", "metrics", "entity_groups", "grains", "relations", "recipes"):
        cards = draft.get(section)
        if isinstance(cards, Mapping):
            for target, card in cards.items():
                add_alias_card(str(target), card)
    explicit_aliases = draft.get("aliases")
    if isinstance(explicit_aliases, Mapping):
        for card in explicit_aliases.values():
            if isinstance(card, Mapping):
                add_alias_card(str(card.get("target_key") or ""), card)
    if len(alias_pairs) > MAX_INVENTORY["aliases"]:
        raise AuthoringSourceManifestError(
            "authoring_inventory_limit_exceeded",
            {"inventory": "aliases", "count": len(alias_pairs), "limit": MAX_INVENTORY["aliases"]},
        )
    alias_bindings = [
        {"alias": alias, "target": target}
        for alias, target in sorted(alias_pairs)
    ]

    return {
        "datasets": dataset_ids,
        "dataset_fields": dataset_fields,
        "field_roles": {
            dataset_id: {
                field_id: field_roles[dataset_id][field_id]
                for field_id in sorted(field_roles[dataset_id])
            }
            for dataset_id in sorted(field_roles)
        },
        "fields": _bounded(unique_fields, "fields"),
        "metrics": keys("metrics", "metrics"),
        "grains": keys("grains", "grains"),
        "grain_keys": {key: grain_keys[key] for key in sorted(grain_keys)},
        "grain_display_fields": {
            key: grain_display_fields[key]
            for key in sorted(grain_display_fields)
        },
        "relations": keys("relations", "relations"),
        "relation_endpoints": {
            key: relation_endpoints[key]
            for key in sorted(relation_endpoints)
        },
        "relation_keys": {
            key: relation_keys[key]
            for key in sorted(relation_keys)
        },
        "relation_policies": {
            key: relation_policies[key]
            for key in sorted(relation_policies)
        },
        "recipes": keys("recipes", "recipes"),
        "operations": _draft_operations(draft, supported_operations),
        "aliases": sorted({item["alias"] for item in alias_bindings}),
        "alias_targets": sorted({item["target"] for item in alias_bindings}),
        "alias_bindings": alias_bindings,
    }


def _bounded_missing(values: Iterable[str]) -> tuple[list[str], int]:
    ordered = sorted(set(str(value) for value in values))
    return ordered[:MAX_MISSING_EVIDENCE], max(0, len(ordered) - MAX_MISSING_EVIDENCE)


def validate_draft_inventory_coverage(
    manifest: Mapping[str, Any],
    draft: Mapping[str, Any],
    *,
    supported_operations: Iterable[str] = (),
) -> dict[str, Any]:
    """Validate that a draft covers every explicitly declared source ID.

    On success the function returns only hashes, integer counts and empty
    bounded ``missing`` evidence.  On failure it raises
    :class:`AuthoringSourceManifestError`; the same safe evidence is available
    on ``exc.evidence``.
    """

    sealed_manifest = _validated_manifest(manifest)
    expected = sealed_manifest["inventories"]
    actual = _draft_inventory(draft, supported_operations)

    missing_fields = []
    for dataset_id, fields in expected["dataset_fields"].items():
        actual_fields = set(actual["dataset_fields"].get(dataset_id, []))
        missing_fields.extend(
            f"{dataset_id}:{field_id}"
            for field_id in fields
            if field_id not in actual_fields
        )
    actual_alias_pairs = {
        (item["alias"], item["target"])
        for item in actual["alias_bindings"]
    }
    expected_relation_endpoints = {
        f"{relation_id}={card['left_dataset']}->{card['right_dataset']}"
        for relation_id, card in expected["relation_endpoints"].items()
    }
    actual_relation_endpoints = {
        f"{relation_id}={card['left_dataset']}->{card['right_dataset']}"
        for relation_id, card in actual["relation_endpoints"].items()
    }
    expected_relation_keys = {
        f"{relation_id}={'|'.join(card['left_keys'])}->{'|'.join(card['right_keys'])}"
        for relation_id, card in expected["relation_keys"].items()
    }
    actual_relation_keys = {
        f"{relation_id}={'|'.join(card['left_keys'])}->{'|'.join(card['right_keys'])}"
        for relation_id, card in actual["relation_keys"].items()
    }
    expected_field_roles = {
        f"{dataset_id}.{field_id}={'|'.join(roles)}"
        for dataset_id, fields in expected["field_roles"].items()
        for field_id, roles in fields.items()
    }
    actual_field_roles = {
        f"{dataset_id}.{field_id}={'|'.join(roles)}"
        for dataset_id, fields in actual["field_roles"].items()
        for field_id, roles in fields.items()
    }
    policy_keys = ("join_type", "cardinality", "null_key_policy", "multi_match_policy")
    expected_relation_policies = {
        f"{relation_id}=" + "|".join(f"{key}:{card[key]}" for key in policy_keys)
        for relation_id, card in expected["relation_policies"].items()
    }
    actual_relation_policies = {
        f"{relation_id}=" + "|".join(f"{key}:{card[key]}" for key in policy_keys)
        for relation_id, card in actual["relation_policies"].items()
    }
    expected_grain_keys = {
        f"{grain_id}={'|'.join(values)}"
        for grain_id, values in expected["grain_keys"].items()
    }
    actual_grain_keys = {
        f"{grain_id}={'|'.join(values)}"
        for grain_id, values in actual["grain_keys"].items()
    }
    expected_grain_display = {
        f"{grain_id}={'|'.join(values)}"
        for grain_id, values in expected["grain_display_fields"].items()
    }
    actual_grain_display = {
        f"{grain_id}={'|'.join(values)}"
        for grain_id, values in actual["grain_display_fields"].items()
    }
    raw_missing = {
        "datasets": set(expected["datasets"]) - set(actual["datasets"]),
        "fields": missing_fields,
        "field_roles": expected_field_roles - actual_field_roles,
        "metrics": set(expected["metrics"]) - set(actual["metrics"]),
        "grains": set(expected["grains"]) - set(actual["grains"]),
        "grain_keys": expected_grain_keys - actual_grain_keys,
        "grain_display_fields": expected_grain_display - actual_grain_display,
        "relations": set(expected["relations"]) - set(actual["relations"]),
        "relation_endpoints": expected_relation_endpoints - actual_relation_endpoints,
        "relation_keys": expected_relation_keys - actual_relation_keys,
        "relation_policies": expected_relation_policies - actual_relation_policies,
        "recipes": set(expected["recipes"]) - set(actual["recipes"]),
        "operations": set(expected["operations"]) - set(actual["operations"]),
        "aliases": {
            hashlib.sha256(item["alias"].encode("utf-8")).hexdigest() + ":" + item["target"]
            for item in expected["alias_bindings"]
            if (item["alias"], item["target"]) not in actual_alias_pairs
        },
        "required_sections": [],
    }
    for section in sealed_manifest["required_sections"]:
        section_values = actual.get(section)
        if not isinstance(section_values, (list, dict)) or not section_values:
            raw_missing["required_sections"].append(section)
    missing: dict[str, list[str]] = {}
    truncated: dict[str, int] = {}
    missing_counts: dict[str, int] = {}
    for kind, values in raw_missing.items():
        bounded_values, omitted = _bounded_missing(values)
        missing[kind] = bounded_values
        truncated[kind] = omitted
        missing_counts[kind] = len(set(values))

    expected_counts = deepcopy(sealed_manifest["counts"])
    actual_counts = {
        "datasets": len(actual["datasets"]),
        "fields": len(actual["fields"]),
        "field_bindings": sum(len(values) for values in actual["dataset_fields"].values()),
        "field_roles": sum(len(values) for values in actual["field_roles"].values()),
        "metrics": len(actual["metrics"]),
        "grains": len(actual["grains"]),
        "grain_keys": len(actual["grain_keys"]),
        "grain_display_fields": len(actual["grain_display_fields"]),
        "relations": len(actual["relations"]),
        "relation_endpoints": len(actual["relation_endpoints"]),
        "relation_keys": len(actual["relation_keys"]),
        "relation_policies": len(actual["relation_policies"]),
        "recipes": len(actual["recipes"]),
        "operations": len(actual["operations"]),
        "aliases": len(actual["aliases"]),
        "alias_targets": len(actual["alias_targets"]),
        "alias_bindings": len(actual["alias_bindings"]),
    }
    evidence = {
        "contract_version": COVERAGE_VERSION,
        "passed": not any(missing_counts.values()),
        "source_sha256": sealed_manifest["source_sha256"],
        "manifest_sha256": sealed_manifest["manifest_sha256"],
        "draft_inventory_sha256": _canonical_sha256(actual),
        "counts": {
            "required": expected_counts,
            "actual": actual_counts,
            "missing": missing_counts,
        },
        "missing": missing,
        "missing_truncated": truncated,
    }
    if not evidence["passed"]:
        raise AuthoringSourceManifestError("authoring_source_coverage_incomplete", evidence)
    return evidence


__all__ = [
    "AuthoringSourceManifestError",
    "COVERAGE_VERSION",
    "MANIFEST_VERSION",
    "extract_authoring_source_manifest",
    "normalize_authoring_draft_shorthand",
    "normalize_authoring_section_patch_shorthand",
    "normalize_draft_alias_shorthand",
    "validate_authoring_source_manifest",
    "validate_draft_inventory_coverage",
]
