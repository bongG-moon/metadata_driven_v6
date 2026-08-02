"""Evidence-only request parsing and deterministic route eligibility."""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from .canonical import ContractError, bounded, sha256_json


SEOUL = ZoneInfo("Asia/Seoul")
DATE_PATTERNS = (
    re.compile(r"(?P<y>20\d{2})[-/.](?P<m>\d{1,2})[-/.](?P<d>\d{1,2})(?:T[^\s]+)?", re.I),
    re.compile(r"(?P<y>20\d{2})년\s*(?P<m>\d{1,2})월\s*(?P<d>\d{1,2})일"),
    re.compile(r"(?<!\d)(?P<m>\d{1,2})\s*[/.월]\s*(?P<d>\d{1,2})\s*일?"),
)
RANGE_PATTERN = re.compile(
    r"(?P<start>(?:D/[SA]|W/B|FCB|B/G)\s*\d+|FCB/H)\s*[~～-]\s*(?P<end>(?:D/[SA]|W/B|FCB|B/G)\s*\d+|FCB/H)",
    re.I,
)
TOP_PATTERN = re.compile(r"(?P<mode>상위|하위|top|bottom)\s*(?P<n>\d+)\s*(?:개|건)?", re.I)
THRESHOLD_PATTERN = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>시간|개|건|%|퍼센트)?\s*(?P<cmp>이상|이하|초과|미만)")
MCP_PREFIX_PATTERN = re.compile(r"(?<![A-Z0-9])(?P<prefix>[A-Z]\s*-\s*\d{2,})(?=(?:\s|로|으|인|제|$))", re.I)
LEAD_PATTERN = re.compile(r"(?<![A-Z0-9])F(?P<lead>\d{2,4})(?![A-Z0-9])", re.I)
DESCRIPTOR_TOKEN_PATTERN = re.compile(r"(?<![A-Z0-9])(?P<token>[A-Z][A-Z0-9/-]*|\d{2,4}G|\d{2,4})(?![A-Z0-9])", re.I)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or "")).strip())


def _reference_datetime(value: str | datetime | None, timezone_name: str) -> datetime:
    zone = ZoneInfo(timezone_name)
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value or "").strip()
        if not text:
            parsed = datetime.now(zone)
        else:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=zone)
    return parsed.astimezone(zone)


def extract_date_candidates(question: str, reference_instant: str | datetime | None, timezone_name: str = "Asia/Seoul") -> list[dict[str, Any]]:
    text = normalize_text(question)
    reference = _reference_datetime(reference_instant, timezone_name)
    candidates: list[dict[str, Any]] = []
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            groups = match.groupdict()
            year = int(groups.get("y") or reference.year)
            try:
                parsed = date(year, int(groups["m"]), int(groups["d"]))
            except ValueError:
                raise ContractError(
                    "intent_contract_error",
                    "request_capsule",
                    "질문의 날짜가 올바르지 않습니다.",
                    {"evidence": match.group(0)},
                )
            candidates.append(
                {
                    "candidate_id": f"date:{parsed.isoformat()}",
                    "value_type": "LocalDate",
                    "value": parsed.isoformat(),
                    "evidence": {"text": match.group(0), "start": match.start(), "end": match.end()},
                    "resolution": "explicit",
                }
            )
    relative_terms = (("오늘", 0), ("금일", 0), ("어제", -1), ("전일", -1))
    for term, offset in relative_terms:
        for match in re.finditer(re.escape(term), text, flags=re.I):
            parsed = reference.date() + timedelta(days=offset)
            candidates.append(
                {
                    "candidate_id": f"date:{parsed.isoformat()}:{term}",
                    "value_type": "LocalDate",
                    "value": parsed.isoformat(),
                    "evidence": {"text": match.group(0), "start": match.start(), "end": match.end()},
                    "resolution": "relative",
                    "reference_instant": reference.isoformat(),
                    "offset_days": offset,
                }
            )
    unique: dict[tuple[str, int, int], dict[str, Any]] = {}
    for candidate in candidates:
        evidence = candidate["evidence"]
        unique[(candidate["value"], evidence["start"], evidence["end"])] = candidate
    return sorted(unique.values(), key=lambda item: (item["evidence"]["start"], item["candidate_id"]))


def extract_literal_candidates(question: str) -> dict[str, list[dict[str, Any]]]:
    text = normalize_text(question)
    result: dict[str, list[dict[str, Any]]] = {"rank": [], "threshold": [], "product_token": [], "ordered_range": []}
    for match in TOP_PATTERN.finditer(text):
        mode_text = match.group("mode").casefold()
        mode = "top" if mode_text in {"상위", "top"} else "bottom"
        result["rank"].append(
            {
                "candidate_id": f"rank:{mode}:{int(match.group('n'))}:{match.start()}",
                "mode": mode,
                "limit": int(match.group("n")),
                "evidence": {"text": match.group(0), "start": match.start(), "end": match.end()},
            }
        )
    comparison_map = {"이상": "gte", "이하": "lte", "초과": "gt", "미만": "lt"}
    for match in THRESHOLD_PATTERN.finditer(text):
        result["threshold"].append(
            {
                "candidate_id": f"threshold:{match.start()}",
                "operator": comparison_map[match.group("cmp")],
                "value": float(match.group("value")),
                "unit": match.group("unit") or "",
                "evidence": {"text": match.group(0), "start": match.start(), "end": match.end()},
            }
        )
    for match in MCP_PREFIX_PATTERN.finditer(text):
        prefix = re.sub(r"\s+", "", match.group("prefix")).upper()
        result["product_token"].append(
            {
                "candidate_id": f"token:MCP_NO:starts_with:{prefix}",
                "field": "MCP_NO",
                "operator": "starts_with",
                "value": prefix,
                "evidence": {"text": match.group(0), "start": match.start(), "end": match.end()},
            }
        )
    for match in LEAD_PATTERN.finditer(text):
        result["product_token"].append(
            {
                "candidate_id": f"token:LEAD:eq:{match.group('lead')}",
                "field": "LEAD",
                "operator": "eq",
                "value": match.group("lead"),
                "evidence": {"text": match.group(0), "start": match.start(), "end": match.end()},
            }
        )
    result["product_token"].extend(extract_product_descriptor_tokens(text, result["product_token"]))
    for match in RANGE_PATTERN.finditer(text):
        start = re.sub(r"\s+", "", match.group("start")).upper()
        end = re.sub(r"\s+", "", match.group("end")).upper()
        result["ordered_range"].append(
            {
                "candidate_id": f"process_range:{start}:{end}",
                "start": start,
                "end": end,
                "inclusive": True,
                "evidence": {"text": match.group(0), "start": match.start(), "end": match.end()},
            }
        )
    return result


def extract_product_descriptor_tokens(question: str, existing: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Parse registered product-token shapes described by the natural-domain guide."""

    text = normalize_text(question)
    # Free-form descriptors are bounded by the word 제품.  This avoids treating
    # dates, ranks and process endpoints elsewhere in a question as product keys.
    product_index = text.find("제품")
    if product_index < 0:
        return []
    left = text[:product_index]
    boundary = max(left.rfind("공정에서"), left.rfind("공정"), left.rfind("에서"))
    if boundary < 0:
        segment_start = 0
    elif left[boundary:].startswith("공정에서"):
        segment_start = boundary + len("공정에서")
    elif left[boundary:].startswith("공정"):
        segment_start = boundary + len("공정")
    else:
        segment_start = boundary + len("에서")
    segment = left[segment_start:].strip()
    base_offset = text.find(segment, max(0, segment_start)) if segment else -1
    if not segment or base_offset < 0:
        return []
    reserved = {
        "INPUT", "OUTPUT", "OUT", "WIP", "UPH", "LOT", "HOLD", "DA", "WB", "FCB", "BG",
        "TOP", "BOTTOM", "MCP", "NO", "PKG", "MOBILE", "POP", "HBM", "AUTO",
        # Registered field/dataset words can occur immediately before "제품"
        # (for example, "MODE별 ... 제품").  They are query grammar, not free
        # product descriptors, so they must never become a TECH equality filter.
        "MODE", "TECH", "DEN", "LEAD", "DEVICE", "OPER", "OPER_NAME",
        "PRODUCTION", "PRODUCTION_QTY", "INPUT_QTY", "OUT_QTY", "YIELD_RATE",
    }
    existing_markers = {
        (str(item.get("field")), str(item.get("operator")), str(item.get("value")))
        for item in (existing or [])
    }
    result: list[dict[str, Any]] = []
    for match in DESCRIPTOR_TOKEN_PATTERN.finditer(segment):
        raw = match.group("token")
        token = raw.upper()
        field = ""
        if re.fullmatch(r"\d{2,4}G", token):
            field = "DEN"
        elif re.fullmatch(r"(?:LP)?DDR\d[A-Z0-9]*", token) or re.fullmatch(r"HBM\d+[A-Z0-9]*", token):
            field = "MODE"
        elif token.endswith("BGA"):
            field = "PKG_TYPE1"
        elif token in {"SDP", "DDP", "TSV"}:
            field = "PKG_TYPE2"
        elif re.fullmatch(r"\d{2,4}", token):
            field = "LEAD"
        elif re.fullmatch(r"[A-Z]{1,4}", token) and token not in reserved:
            field = "TECH"
        if not field:
            continue
        value = token
        marker = (field, "eq", value)
        if marker in existing_markers:
            continue
        existing_markers.add(marker)
        start = base_offset + match.start()
        result.append(
            {
                "candidate_id": f"token:{field}:eq:{value}:{start}",
                "field": field,
                "operator": "eq",
                "value": value,
                "evidence": {"text": raw, "start": start, "end": base_offset + match.end()},
            }
        )
    if result and not any(item.get("field") in {"TECH", "DEN", "MODE", "PKG_TYPE1", "PKG_TYPE2"} for item in result):
        return []
    return result


def build_request_capsule(
    question: str,
    *,
    session_id: str,
    subject_id: str,
    reference_instant: str | datetime | None,
    timezone_name: str = "Asia/Seoul",
    previous_state_ref: str = "",
    upstream_result_ref: str = "",
) -> dict[str, Any]:
    normalized = normalize_text(question)
    if not normalized:
        raise ContractError("intent_contract_error", "request_capsule", "질문을 입력해 주세요.")
    request_id = f"request:{sha256_json([subject_id, session_id, normalized, str(reference_instant)])[:24]}"
    typed_candidates: list[dict[str, Any]] = []
    for item in extract_date_candidates(normalized, reference_instant, timezone_name):
        evidence = item.get("evidence") or {}
        typed_candidates.append(
            {
                "id": str(item.get("candidate_id")),
                "kind": "date",
                "source_span": f"{int(evidence.get('start') or 0)}:{int(evidence.get('end') or 0)}",
                "value": {key: value for key, value in item.items() if key not in {"candidate_id", "evidence"}},
                "resolver_version": "request-literals.v1",
            }
        )
    for kind, values in extract_literal_candidates(normalized).items():
        for item in values:
            evidence = item.get("evidence") or {}
            typed_candidates.append(
                {
                    "id": str(item.get("candidate_id")),
                    "kind": str(kind),
                    "source_span": f"{int(evidence.get('start') or 0)}:{int(evidence.get('end') or 0)}",
                    "value": {key: value for key, value in item.items() if key not in {"candidate_id", "evidence"}},
                    "resolver_version": "request-literals.v1",
                }
            )
    capsule = {
        "contract_version": "request.capsule.v1",
        "request_id": request_id,
        "question": normalized,
        "owner_subject_id": str(subject_id or "anonymous"),
        "session_id": str(session_id or "default"),
        "reference_instant": _reference_datetime(reference_instant, timezone_name).isoformat(),
        "timezone": timezone_name,
        "literal_candidates": typed_candidates,
        "state_ref": str(upstream_result_ref or previous_state_ref or "") or None,
    }
    return bounded(capsule, 12 * 1024, "request_capsule")


def candidate_span_matches(text: str, alias: str) -> list[tuple[int, int]]:
    """Boundary-aware longest matching primitive used by metadata candidates."""
    normalized = normalize_text(text)
    target = normalize_text(alias)
    if not target:
        return []
    pattern = re.compile(rf"(?<![0-9A-Za-z_가-힣]){re.escape(target)}(?![0-9A-Za-z_가-힣])", re.I)
    return [(match.start(), match.end()) for match in pattern.finditer(normalized)]
