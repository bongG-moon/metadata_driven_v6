"""Metadata candidate resolver, route gate, intent decoder and plan compiler."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable

from .canonical import ContractError, bounded, sha256_json
from .request_literals import candidate_span_matches, normalize_text


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "metadata" / "fixtures" / "compiled" / "runtime_catalog.json"


def load_runtime_catalog(path: str | Path | None = None) -> dict[str, Any]:
    catalog_path = Path(path) if path else DEFAULT_CATALOG
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if catalog.get("contract_version") != "metadata.runtime.catalog.v1":
        raise ContractError("metadata_dependency_error", "metadata_loader", "지원하지 않는 runtime catalog입니다.")
    expected = str(catalog.get("catalog_sha256") or "")
    material = {key: value for key, value in catalog.items() if key != "catalog_sha256"}
    actual = sha256_json(material)
    if expected and expected != actual:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_loader",
            "runtime catalog hash가 일치하지 않습니다.",
            {"expected": expected, "actual": actual},
        )
    catalog["catalog_sha256"] = actual
    return catalog


def _contains(text: str, phrase: str, policy: str = "auto") -> list[tuple[int, int]]:
    target = normalize_text(phrase)
    if not target:
        return []
    if re.search(r"[가-힣]", target):
        return [(match.start(), match.end()) for match in re.finditer(re.escape(target), text, flags=re.I)]
    if re.search(r"[0-9A-Za-z_]", target):
        pattern = re.compile(rf"(?<![0-9A-Za-z_]){re.escape(target)}(?![0-9A-Za-z_])", re.I)
        return [(match.start(), match.end()) for match in pattern.finditer(text)]
    if policy == "substring" or (policy == "auto" and re.search(r"[가-힣]", target) and len(target) >= 2):
        return [(match.start(), match.end()) for match in re.finditer(re.escape(target), text, flags=re.I)]
    return candidate_span_matches(text, target)


def _catalog_records(catalog: dict[str, Any], target_type: str) -> dict[str, Any]:
    """Build an alias view without mutating the hash-pinned catalog."""

    registry_names = {
        "metric": "metrics",
        "field": "fields",
        "process_group": "process_groups",
        "product_group": "product_groups",
        "recipe": "recipes",
        "dataset": "datasets",
    }
    registry = catalog.get(registry_names.get(target_type, ""), {})
    records: dict[str, Any] = {
        str(key): deepcopy(value) if isinstance(value, dict) else {}
        for key, value in registry.items()
    } if isinstance(registry, dict) else {}
    alias_registry = catalog.get("aliases") if isinstance(catalog.get("aliases"), dict) else {}
    for alias_record in alias_registry.values():
        if not isinstance(alias_record, dict) or alias_record.get("target_type") != target_type:
            continue
        identity = str(alias_record.get("target_key") or "")
        if not identity:
            continue
        record = records.setdefault(identity, {})
        aliases = record.setdefault("aliases", [])
        seen = {
            str(item.get("text") if isinstance(item, dict) else item).casefold()
            for item in aliases
        }
        for value in alias_record.get("values", []):
            item = deepcopy(value) if isinstance(value, dict) else {"text": str(value)}
            item.setdefault("match", alias_record.get("match") or "bounded_longest")
            if str(item.get("text") or "").casefold() not in seen:
                aliases.append(item)
            compact = re.sub(r"\s+", "", str(item.get("text") or ""))
            if compact != str(item.get("text") or "") and re.search(r"[가-힣]", compact) and compact.casefold() not in seen:
                aliases.append({**item, "text": compact})
        record.setdefault("match_policy", alias_record.get("match") or "bounded_longest")
    return records


def _process_records(catalog: dict[str, Any]) -> dict[str, Any]:
    records = _catalog_records(catalog, "process_group")
    exact = _catalog_records(catalog, "process")
    for identity, record in exact.items():
        value = str(record.get("value") or identity)
        record["members"] = [value]
        record["exact"] = True
        records[f"exact:{identity}"] = record
    return records


def _alias_candidates(text: str, records: dict[str, Any], candidate_type: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for identity, record in records.items():
        aliases = record.get("aliases") if isinstance(record.get("aliases"), list) else []
        for alias_value in aliases:
            alias = str(alias_value.get("text") if isinstance(alias_value, dict) else alias_value)
            priority = int(alias_value.get("priority", 100)) if isinstance(alias_value, dict) else 100
            policy = str(alias_value.get("match") or record.get("match_policy") or "auto") if isinstance(alias_value, dict) else str(record.get("match_policy") or "auto")
            for start, end in _contains(text, alias, policy):
                matches.append(
                    {
                        "candidate_id": f"{candidate_type}:{identity}:{start}:{end}",
                        "candidate_type": candidate_type,
                        "identity": identity,
                        "alias": alias,
                        "priority": priority,
                        "evidence": {"text": text[start:end], "start": start, "end": end},
                    }
                )
    matches.sort(key=lambda item: (item["evidence"]["start"], -(item["evidence"]["end"] - item["evidence"]["start"]), -item["priority"], item["identity"]))
    accepted: list[dict[str, Any]] = []
    occupied: list[tuple[int, int]] = []
    for item in matches:
        span = (item["evidence"]["start"], item["evidence"]["end"])
        if any(span[0] >= left and span[1] <= right for left, right in occupied):
            continue
        accepted.append(item)
        occupied.append(span)
    return accepted


def _operation_applicable(text: str, spec: dict[str, Any]) -> bool:
    any_terms = [str(item) for item in spec.get("any", [])]
    all_terms = [str(item) for item in spec.get("all", [])]
    none_terms = [str(item) for item in spec.get("none", [])]
    any_ok = not any_terms or any(_contains(text, term) for term in any_terms)
    all_ok = all(_contains(text, term) for term in all_terms)
    none_ok = not any(_contains(text, term) for term in none_terms)
    return any_ok and all_ok and none_ok


def _dedupe_identities(candidates: list[dict[str, Any]]) -> list[str]:
    result: list[str] = []
    for candidate in candidates:
        identity = str(candidate.get("identity") or "")
        if identity and identity not in result:
            result.append(identity)
    return result


def _typed_literals(request: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    raw = request.get("literal_candidates")
    if isinstance(raw, dict):
        return deepcopy(raw.get(kind) or [])
    result: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict) or item.get("kind") != kind:
            continue
        value = deepcopy(item.get("value"))
        if isinstance(value, dict):
            value.setdefault("candidate_id", item.get("id"))
            value.setdefault("source_span", item.get("source_span"))
            result.append(value)
    return result


def _selected_date(request: dict[str, Any]) -> str:
    candidates = _typed_literals(request, "date")
    explicit = [item for item in candidates if item.get("resolution") == "explicit"]
    selected = explicit[-1] if explicit else candidates[-1] if candidates else None
    if isinstance(selected, dict) and selected.get("value"):
        return str(selected["value"])
    return str(request.get("reference_instant") or "")[:10]


def _dimension_candidates(text: str, catalog: dict[str, Any]) -> list[str]:
    fields = _catalog_records(catalog, "field")
    selected = _alias_candidates(text, fields, "field")
    result: list[str] = []
    for candidate in selected:
        identity = str(candidate.get("identity") or "")
        roles = fields.get(identity, {}).get("roles") or []
        alias = str(candidate.get("alias") or "")
        if identity == "OPER_NAME" and "별" not in alias and alias.upper() != "OPER_NAME":
            continue
        if "group" in roles and identity not in result:
            result.append(identity)
    if _has_any(text, ["제품별", "제품 중", "제품중", "제품 정보"]):
        recipe = (catalog.get("recipes") or {}).get("product.standard", {})
        keys = [str(field) for field in (((recipe.get("grain") or {}).get("keys") or []) if isinstance(recipe, dict) else [])]
        # A product attribute mentioned in the filter (for example MCP_NO) must
        # not reorder the canonical product grain.
        result = [field for field in result if field not in keys]
        result.extend(keys)
    return result


def _field_candidates(text: str, catalog: dict[str, Any]) -> list[str]:
    fields = _catalog_records(catalog, "field")
    result: list[str] = []
    for candidate in _alias_candidates(text, fields, "field"):
        identity = str(candidate.get("identity") or "")
        alias = str(candidate.get("alias") or "")
        if identity == "OPER_NAME" and "별" not in alias and alias.upper() != "OPER_NAME":
            continue
        if identity and identity not in result:
            result.append(identity)
    return result


def _dataset_candidates(text: str, catalog: dict[str, Any]) -> list[str]:
    return _dedupe_identities(_alias_candidates(text, _catalog_records(catalog, "dataset"), "dataset"))


def _lot_ids(text: str) -> list[str]:
    # ``LOT ID`` and ``LOT LIST`` are natural-language labels, not identifiers.
    # Keep the parser permissive for real identifiers such as ``HOLD-A`` and
    # ``L1001`` while explicitly rejecting the bounded vocabulary that follows
    # LOT in generic display requests.
    reserved = {"ID", "IDS", "LIST", "LOT", "NO", "NUMBER"}
    values: list[str] = []
    for match in re.finditer(r"(?<![0-9A-Za-z])LOT\s+([0-9A-Za-z][0-9A-Za-z_-]*)", text, flags=re.I):
        value = match.group(1).upper()
        if value not in reserved and value not in values:
            values.append(value)
    return values


def _registered_boolean_where(text: str, field_ids: list[str], thresholds: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Compile the bounded boolean-filter grammar into a typed predicate tree."""

    clauses: list[dict[str, Any]] = []
    numeric_field = next((field for field in field_ids if field in {"YIELD_RATE", "IN_TAT", "CUM_TAT"}), "")
    if numeric_field and thresholds:
        threshold = thresholds[0]
        clauses.append(
            {
                "field": numeric_field,
                "operator": str(threshold.get("operator") or "gte"),
                "value": threshold.get("value"),
                "semantic_type": "number",
            }
        )
    mode_match = re.search(r"\bMODE\s*(?:가|이)?\s*([0-9A-Za-z_-]+)", text, flags=re.I)
    if mode_match and "MODE" in field_ids:
        clauses.append({"field": "MODE", "operator": "eq", "value": mode_match.group(1), "semantic_type": "string"})
    blank_field = next(
        (field for field in field_ids if re.search(rf"\b{re.escape(field)}\s*(?:가|이)?\s*비어\s*있는", text, flags=re.I)),
        "",
    )
    blank_clause = {"field": blank_field, "operator": "null_or_blank", "semantic_type": "string"} if blank_field else None
    if not clauses and not blank_clause:
        return None
    left: dict[str, Any] = clauses[0] if len(clauses) == 1 else {"op": "all", "clauses": clauses}
    if blank_clause:
        return {"op": "any", "clauses": [left, blank_clause]}
    return left


def _source_scoped_process_refs(
    metric_candidates: list[dict[str, Any]], process_candidates: list[dict[str, Any]]
) -> dict[str, list[str]]:
    """Bind process evidence to the metric clause that immediately follows it.

    This preserves source-specific conditions in questions such as
    "FCB production and W/B2 WIP".  A later metric with no new process evidence
    inherits the previous clause, which covers "W/B production and morning WIP".
    """

    ordered_metrics = sorted(metric_candidates, key=lambda item: int((item.get("evidence") or {}).get("start") or 0))
    ordered_processes = sorted(process_candidates, key=lambda item: int((item.get("evidence") or {}).get("start") or 0))
    result: dict[str, list[str]] = {}
    previous_end = 0
    inherited: list[str] = []
    for metric in ordered_metrics:
        metric_start = int((metric.get("evidence") or {}).get("start") or 0)
        local = [
            str(item.get("identity") or "")
            for item in ordered_processes
            if previous_end <= int((item.get("evidence") or {}).get("start") or 0) < metric_start
        ]
        local = [value for index, value in enumerate(local) if value and value not in local[:index]]
        if local:
            inherited = local
        identity = str(metric.get("identity") or "")
        if identity and inherited:
            result[identity] = deepcopy(inherited)
        previous_end = int((metric.get("evidence") or {}).get("end") or metric_start)
    return result


def _build_semantics(
    request: dict[str, Any],
    catalog: dict[str, Any],
    analysis_kind: str,
    metric_ids: list[str],
    process_ids: list[str],
    product_group_ids: list[str],
) -> dict[str, Any]:
    text = str(request.get("question") or "")
    metric_ids = list(metric_ids)
    if analysis_kind == "hold_history" and _has_any(text, ["HOLD 시간", "Hold 시간", "오래된"]):
        # This is a plan-derived metric, not a physical source column.  Its
        # formula is pinned below as datetime_diff_hours(reference, start).
        if "HOLD_DURATION_HOURS" not in metric_ids:
            metric_ids.append("HOLD_DURATION_HOURS")
    rank_candidates = _typed_literals(request, "rank")
    threshold_candidates = _typed_literals(request, "threshold")
    token_candidates = _typed_literals(request, "product_token")
    range_candidates = _typed_literals(request, "ordered_range")
    upper = text.upper()
    inferred_rank = deepcopy(rank_candidates[0]) if rank_candidates else None
    if inferred_rank is None and _has_any(text, ["가장 많은", "가장 큰", "최댓값", "최대값"]):
        inferred_rank = {"mode": "top", "limit": 1}
    elif inferred_rank is None and _has_any(text, ["가장 적은", "가장 작은"]):
        inferred_rank = {"mode": "bottom", "limit": 1}
    sort_spec = None
    if _has_any(text, ["큰 순서", "많은 순", "내림차순", "많은 제품"]):
        sort_spec = {"field": metric_ids[-1] if metric_ids else "", "direction": "desc"}
    elif _has_any(text, ["작은 순서", "적은 순", "낮은 순", "오름차순"]):
        sort_spec = {"field": metric_ids[-1] if metric_ids else "", "direction": "asc"}
    rank_segments = [deepcopy(item) for item in rank_candidates]
    if _has_any(text, ["잘 나간"]) and not rank_segments:
        inferred_rank = {"mode": "top", "limit": 3}
        rank_segments = [deepcopy(inferred_rank)]
    field_ids = _field_candidates(text, catalog)
    boolean_where = _registered_boolean_where(text, field_ids, threshold_candidates)
    comparison_operator = "gt"
    if _has_any(text, ["보다 작은", "보다 적"]):
        comparison_operator = "lt"
    elif _has_any(text, ["보다 크거나 같은", "이상"]):
        comparison_operator = "gte"
    elif _has_any(text, ["보다 작거나 같은", "이하"]):
        comparison_operator = "lte"
    dimensions = _dimension_candidates(text, catalog)
    equipment_view = ""
    if analysis_kind == "uph_detail" and "UPH" in metric_ids:
        equipment_view = "uph_detail"
        dimensions = ["EQP_MODEL", "RECIPE_ID", "OPER_NAME"]
    elif analysis_kind == "equipment_grouped":
        equipment_view = "equipment_grouped"
        dimensions = ["EQP_MODEL", "RECIPE_ID"]
        if "EQP_COUNT" not in metric_ids:
            metric_ids.append("EQP_COUNT")
    product_recipe = (catalog.get("recipes") or {}).get("product.standard", {})
    product_dimensions = [str(item) for item in ((product_recipe.get("grain") or {}).get("keys") or [])]
    product_default_kinds = {
        "aggregate", "join", "presence", "formula", "rank", "group_rank",
        "multi_metric_argmax", "top_bottom", "field_compare", "equipment_enrich",
    }
    explicit_product_scope = bool(product_group_ids or token_candidates) or _has_any(
        text,
        ["제품별", "제품 별", "제품 중", "제품중", "제품의", "제품을", "제품과", "Device", "DEVICE"],
    )
    if (
        not dimensions
        and metric_ids
        and analysis_kind == "aggregate"
        and process_ids
        and not explicit_product_scope
    ):
        # A plain metric request scoped to a registered process asks for the
        # process rollup.  Product grain is only the default when the question
        # actually asks for products (or a product-oriented operator does).
        dimensions = ["OPER_NAME"]
    if not dimensions and metric_ids and analysis_kind in product_default_kinds:
        dimensions = deepcopy(product_dimensions)
    if len(process_ids) >= 2 and metric_ids and "OPER_NAME" not in dimensions:
        dimensions.insert(0, "OPER_NAME")
    qualitative_extreme = inferred_rank is not None and not rank_candidates and int(inferred_rank.get("limit") or 0) == 1
    return {
        "analysis_kind": analysis_kind,
        "metric_refs": metric_ids,
        "dimension_refs": dimensions,
        "field_refs": field_ids,
        "dataset_refs": _dataset_candidates(text, catalog),
        "process_refs": process_ids,
        "product_group_refs": product_group_ids,
        "date": _selected_date(request),
        "date_explicit": bool(_typed_literals(request, "date")),
        "reference_date": str(request.get("reference_instant") or "")[:10],
        "reference_instant": str(request.get("reference_instant") or ""),
        "rank": inferred_rank,
        "rank_segments": rank_segments,
        "tie_policy": "include_all" if inferred_rank and (_has_any(text, ["동점", "모두"]) or qualitative_extreme) else "exact_n",
        "thresholds": deepcopy(threshold_candidates),
        "product_tokens": deepcopy(token_candidates),
        "ordered_range": deepcopy(range_candidates[0]) if range_candidates else None,
        "sort": sort_spec,
        "lot_ids": _lot_ids(text),
        "where": boolean_where,
        "comparison_operator": comparison_operator,
        "followup": bool(request.get("state_ref")),
        "qualifiers": {
            "current_hold": "HOLD" in upper and _has_any(text, ["현재", "Hold 된", "HOLD LOT", "Hold Lot"]),
            "hold_history": "HOLD" in upper and _has_any(text, ["이력", "히스토리", "오래된"]),
            "equipment": _has_any(text, ["장비", "설비", "Recipe", "RECIPE"]),
            "equipment_view": equipment_view,
            "detail": _has_any(text, ["목록", "LIST", "Lot ID", "LOT 알려", "보여줘"]),
            "preserve_blank_product": _has_any(text, ["제품 정보가 비어", "제품정보가 비어", "비어 있는 제품 정보"]),
            "fill_metric_zero": _has_any(text, ["생산량이 비어 있으면 0", "수량이 비어 있으면 0", "실적이 비어 있으면 0"]),
        },
    }


def _has_any(text: str, values: list[str]) -> bool:
    return any(_contains(text, value) for value in values)


def _analysis_kinds(text: str, request: dict[str, Any], metric_ids: list[str], field_ids: list[str]) -> list[str]:
    """Closed grammar over registered metrics/fields; it never creates code."""

    literals = {"rank": _typed_literals(request, "rank")}
    if request.get("state_ref") and _has_any(text, ["그중"]):
        return ["previous_rank"]
    if request.get("state_ref") and _has_any(text, ["이 제품들"]) and _has_any(text, ["장비", "설비"]):
        return ["equipment_enrich"]
    if _has_any(text, ["같지만", "서로 다른", "다른 제품"]):
        return ["compare_group_attributes"]
    if _has_any(text, ["데이터에서"]) and _has_any(text, ["컬럼만", "컬럼을", "컬럼"]):
        return ["projection"]
    if (
        "UPH" in text.upper()
        and _has_any(text, ["Recipe", "RECIPE"])
        and _has_any(text, ["장비 모델", "장비 기종", "설비 모델", "설비 기종"])
    ):
        return ["uph_detail"]
    if (
        _has_any(text, ["조합별", "조합 별"])
        and _has_any(text, ["배정된 장비", "할당된 장비"])
        and _has_any(text, ["Recipe", "RECIPE"])
    ):
        return ["equipment_grouped"]
    if _has_any(text, ["중복된", "중복 그룹", "중복된 그룹"]):
        return ["duplicate_groups"]
    if _has_any(text, ["각 컬럼별", "각각의 컬럼", "컬럼별로"]) and len(metric_ids) >= 2 and _has_any(text, ["가장 큰", "최댓값", "최대값"]):
        return ["multi_metric_argmax"]
    rank_modes = {str(item.get("mode") or "") for item in _typed_literals(request, "rank")}
    if {"top", "bottom"}.issubset(rank_modes):
        return ["top_bottom"]
    if len(metric_ids) >= 2 and _has_any(text, ["보다 큰 행", "보다 작은 행", "보다 많", "보다 적"]):
        return ["field_compare"]
    if _has_any(text, ["left join", "LEFT JOIN", "레프트 조인"]) and _has_any(text, ["장비배정", "장비 배정"]):
        return ["production_equipment_join"]
    if _has_any(text, ["이상이고", "이하이고", "초과이고", "미만이고", "비어 있는 행", "비어있는 행"]) and not _has_any(text, ["제외하지", "제외하지 말"]):
        return ["boolean_filter"]
    if not metric_ids and _has_any(text, ["수량", "현황"]) and _has_any(text, ["별", "보여"]):
        return ["clarification"]
    if "HOLD" in text.upper() and _has_any(text, ["이력", "히스토리", "오래된"]):
        return ["hold_history"]
    if "UPH" in text.upper():
        return ["uph"]
    if _has_any(text, ["할당된 장비", "배정된 장비", "장비 대수", "장비 LIST", "장비 목록"]):
        return ["equipment_enrich"] if metric_ids and "PRODUCTION_QTY" in metric_ids else ["equipment_detail"]
    if _has_any(text, ["달성률", "계획 대비 실제", "목표 대비 실적"]):
        return ["formula"]
    if _has_any(text, ["있으나", "있지만", "있고"]) and _has_any(text, ["없는", "없음", "없으나"]):
        return ["presence"]
    if literals.get("rank") or _has_any(text, ["가장 많은", "가장 적은", "가장 큰", "가장 작은", "최댓값", "최대값", "잘 나간"]):
        if literals.get("rank") and field_ids and _has_any(text, ["별"]):
            return ["group_rank"]
        return ["rank"]
    if "HOLD" in text.upper() or _has_any(text, ["LOT 알려", "LOT 목록", "LOT LIST", "LOT와", "LOT ID"]):
        return ["detail"]
    if metric_ids and _has_any(text, ["실적이 있는 Device", "실적이 있는 DEVICE", "있는 Device", "있는 DEVICE"]):
        return ["metric_presence_detail"]
    if len(metric_ids) >= 2 and set(metric_ids).issubset({"INPUT_PLAN_QTY", "OUT_PLAN_QTY"}):
        return ["aggregate"]
    if len(metric_ids) >= 2 or _has_any(text, ["비교해", "대비"]):
        return ["join"]
    if metric_ids:
        return ["aggregate"]
    if field_ids:
        return ["detail"]
    return []


def _followup_mode(text: str, request: dict[str, Any]) -> str:
    if not request.get("state_ref"):
        return "none"
    if _has_any(text, ["그중", "이 제품들", "위 결과", "위의 결과", "어땠어", "이력을"]):
        return "referenced"
    return "context_switch"


def _inherit_semantics(
    current: dict[str, Any],
    prior: dict[str, Any] | None,
    request: dict[str, Any],
    mode: str,
    prior_result: dict[str, Any] | None,
) -> dict[str, Any]:
    if mode != "referenced" or not isinstance(prior, dict):
        current["followup_mode"] = mode
        return current
    merged = deepcopy(current)
    for key in ("metric_refs", "process_refs", "dimension_refs", "field_refs"):
        if not merged.get(key):
            merged[key] = deepcopy(prior.get(key) or [])
    if not merged.get("product_group_refs"):
        merged["product_group_refs"] = deepcopy(prior.get("product_group_refs") or [])
    if not _typed_literals(request, "date"):
        merged["date"] = prior.get("date") or merged.get("date")
        merged["reference_date"] = prior.get("reference_date") or merged.get("reference_date")
    if _has_any(str(request.get("question") or ""), ["위 결과", "제품별"]):
        # A dimension switch replaces, rather than appends to, the prior grain.
        current_dimensions = current.get("dimension_refs") or []
        if current_dimensions:
            merged["dimension_refs"] = deepcopy(current_dimensions)
            merged["field_refs"] = deepcopy(current.get("field_refs") or [])
    if current.get("product_group_refs"):
        merged["product_group_refs"] = deepcopy(current["product_group_refs"])
    if current.get("rank"):
        merged["rank"] = deepcopy(current["rank"])
    rows = (prior_result or {}).get("rows") if isinstance(prior_result, dict) else []
    if merged.get("analysis_kind") == "hold_history" and isinstance(rows, list):
        merged["prior_lot_ids"] = [str(row.get("LOT_ID")) for row in rows if isinstance(row, dict) and row.get("LOT_ID")][:100]
    merged["followup"] = True
    merged["followup_mode"] = "referenced"
    return merged


def build_candidate_bundle(
    request: dict[str, Any],
    catalog: dict[str, Any],
    *,
    prior_semantics: dict[str, Any] | None = None,
    prior_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    text = normalize_text(str(request.get("question") or ""))
    unsupported_terms = ["예측해", "예측값", "원인 분석", "왜 발생", "최적화해"]
    unsupported = [item for item in unsupported_terms if _contains(text, item)]
    metric_records = _catalog_records(catalog, "metric")
    process_records = _process_records(catalog)
    product_records = _catalog_records(catalog, "product_group")
    field_records = _catalog_records(catalog, "field")
    metric_candidates = _alias_candidates(text, metric_records, "metric")
    process_candidates = _alias_candidates(text, process_records, "process")
    product_candidates = _alias_candidates(text, product_records, "product_group")
    field_candidates = _alias_candidates(text, field_records, "field")
    metric_ids = _dedupe_identities(metric_candidates)
    process_ids = _dedupe_identities(process_candidates)
    product_ids = _dedupe_identities(product_candidates)
    field_ids = _dedupe_identities(field_candidates)
    # Closed colloquial applications still resolve to registered metrics.  The
    # words below do not create a field; they only enable an existing candidate
    # whose full plan is compiled from the catalog.
    if _has_any(text, ["잘 나간"]) and "PRODUCTION_QTY" not in metric_ids:
        metric_ids.append("PRODUCTION_QTY")
    if _has_any(text, ["생산과", "생산 과"]) and _has_any(text, ["재공", "WIP"]):
        if "PRODUCTION_QTY" not in metric_ids:
            metric_ids.insert(0, "PRODUCTION_QTY")
    if _has_any(text, ["현재·누적 TAT", "현재/누적 TAT", "현재 및 누적 TAT"]):
        if "IN_TAT" not in metric_ids:
            metric_ids.append("IN_TAT")
        if "CUM_TAT" not in metric_ids:
            metric_ids.append("CUM_TAT")
    if _has_any(text, ["left join", "LEFT JOIN", "레프트 조인"]) and _has_any(text, ["장비배정", "장비 배정"]):
        if "PRODUCTION_QTY" not in metric_ids:
            metric_ids.insert(0, "PRODUCTION_QTY")
        if "EQP_COUNT" not in metric_ids:
            metric_ids.append("EQP_COUNT")
    followup_mode = _followup_mode(text, request)
    # OPER_NAME can match the generic word "공정" even when the user did not
    # request a per-process partition.  Use the role-aware dimension resolver
    # for operation-kind selection so "제품별 상위 N" remains a global rank.
    primary = _analysis_kinds(text, request, metric_ids, _field_candidates(text, catalog))
    if followup_mode == "referenced" and _has_any(text, ["위 결과", "위의 결과"]):
        primary = ["join"]
    elif followup_mode == "referenced" and product_ids and not metric_ids:
        primary = ["aggregate", "detail"]

    candidates: list[dict[str, Any]] = []
    for kind in primary:
        semantics = _inherit_semantics(
            _build_semantics(request, catalog, kind, metric_ids, process_ids, product_ids),
            prior_semantics,
            request,
            followup_mode,
            prior_result,
        )
        semantics["process_refs_by_metric"] = _source_scoped_process_refs(metric_candidates, process_candidates)
        if kind == "production_equipment_join":
            semantics["metric_refs"] = ["PRODUCTION_QTY", "EQP_COUNT"]
        if kind == "boolean_filter" and not semantics.get("dataset_refs"):
            semantics["dataset_refs"] = ["product_master"]
        candidate_id = f"intent:{kind}:{sha256_json(semantics)[:16]}"
        candidates.append(
            {
                "candidate_id": candidate_id,
                "description": kind,
                "semantics": semantics,
                "semantics_sha256": sha256_json(semantics),
            }
        )

    ambiguity: list[dict[str, Any]] = []
    for candidate_group, label in ((metric_candidates, "metric"), (process_candidates, "process"), (product_candidates, "product_group")):
        by_span: dict[tuple[int, int], set[str]] = {}
        for candidate in candidate_group:
            evidence = candidate["evidence"]
            by_span.setdefault((evidence["start"], evidence["end"]), set()).add(candidate["identity"])
        for span, identities in by_span.items():
            if len(identities) > 1:
                ambiguity.append({"type": label, "span": list(span), "identities": sorted(identities)})

    forced_llm_kinds = {"clarification"}
    forced_llm = (
        any(kind in forced_llm_kinds for kind in primary)
        or _has_any(text, ["잘 나간"])
    )
    if unsupported:
        route = "unsupported"
        reason = "unsupported_registry_gap"
    elif ambiguity:
        route = "intent_llm"
        reason = "ambiguous_candidate_selection"
    elif not candidates:
        route = "unsupported"
        reason = "unsupported_registry_gap"
    elif forced_llm:
        route = "intent_llm"
        reason = (
            "forced_equivalence_probe"
            if _has_any(text, ["잘 나간"])
            else "ambiguous_candidate_selection"
            if primary == ["clarification"]
            else "semantic_choice_required"
        )
    elif len(primary) == 1 and len(candidates) == 1:
        route = "deterministic"
        reason = "unique_complete_selection"
    else:
        route = "intent_llm"
        reason = "semantic_choice_required"

    card_projection = [_intent_prompt_card(item) for item in candidates]
    bundle_material = {
        "request_id": request.get("request_id"),
        "catalog_sha256": catalog.get("catalog_sha256"),
        "metric_candidates": metric_candidates,
        "process_candidates": process_candidates,
        "product_group_candidates": product_candidates,
        "field_candidates": field_candidates,
        "intent_candidates": candidates,
    }
    bundle_sha = sha256_json(bundle_material)
    decision_material = {
        "route": route,
        "reason": reason,
        "bundle_sha256": bundle_sha,
        "candidate_ids": [item["candidate_id"] for item in candidates],
    }
    bundle = {
        "contract_version": "resolved.candidate.bundle.v1",
        **bundle_material,
        "bundle_sha256": bundle_sha,
        "prompt_cards": card_projection,
        "route_decision": {
            "contract_version": "analysis.route.v1",
            "route": route,
            "reason_code": reason,
            "resolved_candidate_bundle_sha256": bundle_sha,
            "selected_candidate_ids": [item["candidate_id"] for item in candidates] if route == "deterministic" else [],
            "required_slots": [],
            "unresolved_slots": ["intent_candidate_id"] if route == "intent_llm" else (["registry_gap"] if route == "unsupported" else []),
            "ambiguity_sets": [item["identities"] for item in ambiguity],
            "route_policy_version": "route-policy.v1",
            "eligibility_proof_sha256": sha256_json(decision_material),
        },
        "route_evidence": {"ambiguity": ambiguity, "unsupported_signals": unsupported},
    }
    return bounded(bundle, 28 * 1024, "candidate_bundle")


def _intent_prompt_card(candidate: dict[str, Any]) -> dict[str, Any]:
    """Project only the semantic distinctions needed by the intent selector.

    Candidate IDs and executable semantics remain sealed elsewhere. The model
    receives registered identifiers plus a compact result-shape policy so an
    elliptical follow-up cannot accidentally turn a grouped result into raw
    detail rows merely because both candidates share the same filters.
    """

    semantics = candidate.get("semantics") if isinstance(candidate.get("semantics"), dict) else {}
    analysis_kind = str(semantics.get("analysis_kind") or "")
    result_shape = {
        "aggregate": "grouped_summary",
        "rank": "ranked_summary",
        "detail": "individual_rows",
        "projection": "selected_columns",
        "clarification": "clarification_required",
    }.get(analysis_kind, analysis_kind or "registered_result")
    followup = bool(semantics.get("followup"))
    if followup and analysis_kind == "aggregate":
        selection_policy = (
            "replace_newly_mentioned_filter_and_keep_previous_metric_date_dimensions_aggregation"
        )
    elif followup and analysis_kind in {"detail", "projection"}:
        selection_policy = (
            "switch_to_individual_rows_only_when_detail_rows_list_or_identifiers_are_explicit"
        )
    elif analysis_kind == "detail":
        selection_policy = "individual_rows_require_an_explicit_detail_rows_list_or_identifier_request"
    else:
        selection_policy = "match_the_question_to_this_registered_result_shape"
    return {
        "candidate_id": candidate.get("candidate_id"),
        "description": candidate.get("description"),
        "analysis_kind": analysis_kind,
        "result_shape": result_shape,
        "followup": followup,
        "selection_policy": selection_policy,
        "registered_metric_refs": list(semantics.get("metric_refs") or [])[:16],
        "registered_dimension_refs": list(semantics.get("dimension_refs") or [])[:16],
        "registered_product_group_refs": list(
            semantics.get("product_group_refs") or []
        )[:16],
    }


def build_intent_prompt(request: dict[str, Any], bundle: dict[str, Any]) -> str:
    cards = bundle.get("prompt_cards") if isinstance(bundle.get("prompt_cards"), list) else []
    return (
        "Select exactly one candidate_id that best matches the question. "
        "Use only the registered candidate cards; never invent a dataset, column, value, operation or ID. "
        "For an elliptical follow-up that only names a replacement filter or entity, such as 'X는 어땠어?', "
        "preserve the previous result shape unless the user explicitly asks for detail, raw rows, a list, "
        "individual records or identifiers. Therefore prefer grouped_summary over individual_rows when no "
        "such detail cue is explicit. Return exactly one JSON object and no explanation: "
        "{\"intent_candidate_id\":\"...\"}.\n"
        f"Question: {request.get('question','')}\n"
        "Registered candidates:\n"
        + json.dumps(cards, ensure_ascii=False, separators=(",", ":"))
    )


def _model_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if hasattr(value, "text"):
        return str(value.text)
    if isinstance(value, dict):
        for key in ("text", "content", "message"):
            if key in value:
                return str(value[key])
    return str(value)


def _parse_selection(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I | re.S).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < start:
        raise ValueError("JSON object not found")
    value = json.loads(raw[start : end + 1])
    if not isinstance(value, dict) or set(value) != {"intent_candidate_id"}:
        raise ValueError("selection must contain only intent_candidate_id")
    return value


def resolve_intent(
    request: dict[str, Any],
    bundle: dict[str, Any],
    *,
    model: Any = None,
    llm_callable: Callable[[str], Any] | None = None,
    allow_syntax_retry: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    route = bundle.get("route_decision") if isinstance(bundle.get("route_decision"), dict) else {}
    route_name = str(route.get("route") or "")
    candidates = bundle.get("intent_candidates") if isinstance(bundle.get("intent_candidates"), list) else []
    if route_name == "unsupported":
        raise ContractError(
            "unsupported_operation",
            "route_eligibility",
            "등록된 metadata와 typed operator로 처리할 수 없는 질문입니다.",
            {"reason_code": route.get("reason_code")},
        )
    if route_name == "needs_clarification":
        raise ContractError("intent_contract_error", "intent_routing", "질문의 의미를 하나로 결정할 수 없습니다.")
    calls = 0
    if route_name == "deterministic":
        if len(candidates) != 1:
            raise ContractError("intent_contract_error", "intent_routing", "deterministic 후보가 유일하지 않습니다.")
        selected_id = str(candidates[0]["candidate_id"])
    elif route_name == "intent_llm":
        prompt = build_intent_prompt(request, bundle)
        if llm_callable is None and model is None:
            raise ContractError("intent_contract_error", "intent_llm", "Intent Language Model 연결이 필요합니다.")

        def call(value: str) -> str:
            nonlocal calls
            calls += 1
            if llm_callable is not None:
                return _model_text(llm_callable(value))
            if hasattr(model, "invoke"):
                return _model_text(model.invoke(value))
            if callable(model):
                return _model_text(model(value))
            raise TypeError("model is not invokable")

        try:
            selection = _parse_selection(call(prompt))
        except Exception as first:
            if not allow_syntax_retry:
                raise ContractError("intent_contract_error", "intent_llm", "Intent LLM 응답 JSON이 올바르지 않습니다.") from first
            retry = prompt + "\n이전 응답은 JSON 형식 오류였습니다. 설명 없이 정확한 JSON 한 개만 다시 반환하세요."
            try:
                selection = _parse_selection(call(retry))
            except Exception as second:
                raise ContractError("intent_contract_error", "intent_llm", "Intent LLM 응답 JSON이 올바르지 않습니다.") from second
        selected_id = str(selection.get("intent_candidate_id") or "")
    else:
        raise ContractError("intent_contract_error", "intent_routing", "알 수 없는 intent route입니다.")

    return normalize_intent_selection(
        request,
        bundle,
        selected_candidate_id=selected_id,
        intent_llm_calls=calls,
    )


def normalize_intent_selection(
    request: dict[str, Any],
    bundle: dict[str, Any],
    *,
    selected_candidate_id: str | None = None,
    intent_llm_calls: int = 0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Normalize a preselected sealed candidate without invoking an LLM.

    Langflow runtime components use this boundary after the external Prompt
    Template/Conditional Invoker path.  Keeping provider invocation outside
    this function prevents prompt text and retry behavior from leaking into
    the standalone intent decoder.
    """

    route = bundle.get("route_decision") if isinstance(bundle.get("route_decision"), dict) else {}
    route_name = str(route.get("route") or "")
    candidates = bundle.get("intent_candidates") if isinstance(bundle.get("intent_candidates"), list) else []
    if route_name == "unsupported":
        raise ContractError(
            "unsupported_operation",
            "route_eligibility",
            "등록된 metadata와 typed operator로 처리할 수 없는 질문입니다.",
            {"reason_code": route.get("reason_code")},
        )
    if route_name == "deterministic":
        if len(candidates) != 1:
            raise ContractError("intent_contract_error", "intent_routing", "deterministic 후보가 유일하지 않습니다.")
        if int(intent_llm_calls) != 0:
            raise ContractError("intent_contract_error", "intent_decoding", "deterministic 분기에서는 Intent LLM 호출 수가 0이어야 합니다.")
        selected_id = str(candidates[0].get("candidate_id") or "")
        calls = 0
    elif route_name == "intent_llm":
        selected_id = str(selected_candidate_id or "")
        if not selected_id:
            raise ContractError("intent_contract_error", "intent_decoding", "Intent LLM candidate 선택값이 필요합니다.")
        calls = int(intent_llm_calls)
        if calls != 1:
            raise ContractError("intent_contract_error", "intent_decoding", "Intent LLM 호출 수는 정확히 1회여야 합니다.")
    else:
        raise ContractError("intent_contract_error", "intent_routing", "알 수 없는 intent route입니다.")

    selected = next((item for item in candidates if item.get("candidate_id") == selected_id), None)
    if not isinstance(selected, dict):
        raise ContractError(
            "intent_contract_error",
            "intent_decoding",
            "LLM이 candidate 목록 밖의 값을 선택했습니다.",
            {"candidate_id": selected_id},
        )
    semantics = deepcopy(selected.get("semantics") or {})
    intent_material = {
        "contract_version": "analysis.intent.v1",
        "request_id": request.get("request_id"),
        "candidate_bundle_sha256": bundle.get("bundle_sha256"),
        "intent_candidate_id": selected_id,
        "semantics": semantics,
    }
    intent = {**intent_material, "intent_sha256": sha256_json(intent_material)}
    telemetry = {
        "route": route_name,
        "reason_code": route.get("reason_code"),
        "intent_llm_calls": calls,
        "fallback_used": False,
        "eligibility_proof_sha256": route.get("eligibility_proof_sha256"),
    }
    return intent, telemetry


def _metric_dataset(metric: dict[str, Any], requested_date: str, reference_date: str) -> tuple[str, str]:
    temporal = metric.get("temporal_contract") if isinstance(metric.get("temporal_contract"), dict) else {}
    selector = temporal.get("dataset_selector") if isinstance(temporal.get("dataset_selector"), dict) else {}
    query_time = temporal.get("query_time") if isinstance(temporal.get("query_time"), dict) else {}
    offset = int(query_time.get("offset_days") or 0)
    query_date = (date.fromisoformat(requested_date) + timedelta(days=offset)).isoformat()
    key = str(selector.get("dataset_key") or "")
    if not key:
        binding = metric.get("source_binding") if isinstance(metric.get("source_binding"), dict) else {}
        family = str(binding.get("dataset_family") or "")
        key = {
            "production": "production_today" if requested_date == reference_date else "production",
            "wip": "wip_today" if requested_date == reference_date else "wip",
            "target": "target",
            "equipment_uph": "eqp_uph",
            "equipment": "equipment_assign",
            "lot": "lot_status",
            "hold_history": "hold_history",
        }.get(family, "")
    if not key:
        raise ContractError("metadata_dependency_error", "plan_compilation", "metric dataset binding이 없습니다.")
    return key, query_date


def _process_values(semantics: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    values: list[str] = []
    groups = _process_records(catalog)
    for identity in semantics.get("process_refs", []):
        record = groups.get(str(identity), {})
        for member in record.get("members", []):
            value = str(member.get("value") if isinstance(member, dict) else member)
            if value and value not in values:
                values.append(value)
    return values


def _product_clauses(semantics: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    clauses: list[dict[str, Any]] = []
    groups = catalog.get("product_groups") if isinstance(catalog.get("product_groups"), dict) else {}
    for identity in semantics.get("product_group_refs", []):
        predicate = groups.get(str(identity), {}).get("predicate")
        if isinstance(predicate, dict):
            clauses.append(deepcopy(predicate))
    for token in semantics.get("product_tokens", []):
        clauses.append(
            {
                "field": token.get("field"),
                "operator": token.get("operator"),
                "value": token.get("value"),
                "semantic_type": "string",
            }
        )
    return clauses


def _filter_fields(nodes: list[dict[str, Any]] | dict[str, Any]) -> list[str]:
    values = nodes if isinstance(nodes, list) else [nodes]
    result: list[str] = []
    for item in values:
        if not isinstance(item, dict):
            continue
        field = str(item.get("field") or "")
        if field and field not in result:
            result.append(field)
        for nested in _filter_fields(item.get("clauses") or []):
            if nested not in result:
                result.append(nested)
    return result


def _aggregate_operation(source_id: str, operation_id: str, dimensions: list[str], metric_id: str, metric: dict[str, Any]) -> dict[str, Any]:
    binding = metric.get("source_binding") if isinstance(metric.get("source_binding"), dict) else {}
    additivity = metric.get("additivity") if isinstance(metric.get("additivity"), dict) else {}
    default = str(additivity.get("default") or "additive")
    function = "sum" if default == "additive" else "nunique" if default == "distinct" else "mean"
    return {
        "id": operation_id,
        "op": "aggregate",
        "input": source_id,
        "group_by": dimensions,
        "metrics": [
            {
                "field": binding.get("field"),
                "function": function,
                "as": metric_id,
                "dropna": True,
            }
        ],
    }


def _finalize_plan(
    intent: dict[str, Any],
    bundle: dict[str, Any],
    catalog: dict[str, Any],
    jobs: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    result_operation_id: str,
    columns: list[str],
    grain: list[str],
    lineage: dict[str, Any],
    *,
    input_refs: list[str] | None = None,
) -> dict[str, Any]:
    material = {
        "contract_version": "analysis.plan.v1",
        "intent_sha256": intent.get("intent_sha256"),
        "candidate_bundle_sha256": bundle.get("bundle_sha256"),
        "catalog_sha256": catalog.get("catalog_sha256"),
        "retrieval_jobs": jobs,
        "operations": operations,
        "result_operation_id": result_operation_id,
        "result_contract": {"columns": columns, "ordering": [], "grain": grain},
        "lineage": lineage,
    }
    if input_refs:
        material["input_refs"] = list(dict.fromkeys(str(value) for value in input_refs if str(value)))
    normalized = deepcopy(material)
    normalized["retrieval_jobs"] = sorted(normalized["retrieval_jobs"], key=lambda item: item["job_id"])
    plan_hash = sha256_json(normalized)
    semantic_material = {
        key: normalized[key]
        for key in (
            "catalog_sha256",
            "input_refs",
            "retrieval_jobs",
            "operations",
            "result_operation_id",
            "result_contract",
            "lineage",
        )
        if key in normalized
    }
    return {**material, "plan_id": f"plan:{plan_hash}", "plan_fingerprint": sha256_json(semantic_material)}


def _range_process_values(ordered_range: dict[str, Any] | None, catalog: dict[str, Any]) -> list[str]:
    if not isinstance(ordered_range, dict):
        return []
    rows = [item for item in catalog.get("process_order", []) if isinstance(item, dict)]
    lookup: dict[str, int] = {}
    for item in rows:
        for name in [item.get("oper_name"), *(item.get("aliases") or [])]:
            lookup[normalize_text(str(name)).upper()] = int(item.get("oper_seq") or 0)
    start = lookup.get(normalize_text(str(ordered_range.get("start"))).upper())
    end = lookup.get(normalize_text(str(ordered_range.get("end"))).upper())
    if start is None or end is None:
        raise ContractError("plan_contract_error", "plan_compilation", "공정 범위 endpoint가 metadata에 없습니다.")
    low, high = sorted((start, end))
    return [str(item.get("oper_name")) for item in rows if low <= int(item.get("oper_seq") or 0) <= high]


def _compile_operator_special_plan(
    intent: dict[str, Any], bundle: dict[str, Any], catalog: dict[str, Any], semantics: dict[str, Any]
) -> dict[str, Any] | None:
    """Compile closed operator applications that are not plain metric rollups."""

    kind = str(semantics.get("analysis_kind") or "")
    supported = {
        "projection",
        "boolean_filter",
        "duplicate_groups",
        "metric_presence_detail",
        "equipment_enrich",
        "production_equipment_join",
    }
    if kind not in supported:
        return None
    datasets = catalog.get("datasets") if isinstance(catalog.get("datasets"), dict) else {}

    if kind == "projection":
        dataset_key = next((value for value in semantics.get("dataset_refs", []) if value in datasets), "production")
        dataset = datasets.get(dataset_key, {})
        available = set((dataset.get("fields") or {}).keys())
        fields = [str(field) for field in semantics.get("field_refs", []) if str(field) in available]
        if not fields:
            raise ContractError("plan_contract_error", "plan_compilation", "projection field가 등록되지 않았습니다.")
        job = {
            "job_id": f"job_1_{dataset_key}",
            "dataset_key": dataset_key,
            "source_type": str(dataset.get("source_type") or "dummy"),
            "parameters": {},
            "required_fields": fields,
            "filters": None,
            "requirement": "required",
        }
        operations = [{"id": "op_project", "op": "project", "input": f"source:{job['job_id']}", "fields": fields}]
        return _finalize_plan(intent, bundle, catalog, [job], operations, "op_project", fields, fields, {"dataset_key": dataset_key})

    if kind == "boolean_filter":
        dataset_key = "product_master"
        dataset = datasets.get(dataset_key, {})
        available = set((dataset.get("fields") or {}).keys())
        fields = [field for field in ["DEVICE", "YIELD_RATE", "MODE", "LEAD"] if field in available]
        where = semantics.get("where") if isinstance(semantics.get("where"), dict) else None
        if not where:
            raise ContractError("intent_contract_error", "plan_compilation", "boolean filter predicate가 완전하지 않습니다.")
        required = sorted(set(fields + _filter_fields(where)))
        job = {
            "job_id": "job_1_product_master",
            "dataset_key": dataset_key,
            "source_type": str(dataset.get("source_type") or "fixture"),
            "parameters": {},
            "required_fields": required,
            "filters": None,
            "requirement": "required",
        }
        operations = [
            {"id": "op_filter", "op": "filter", "input": "source:job_1_product_master", "where": where},
            {"id": "op_project", "op": "project", "input": "op_filter", "fields": fields},
        ]
        return _finalize_plan(intent, bundle, catalog, [job], operations, "op_project", fields, ["DEVICE"], {"dataset_key": dataset_key})

    if kind == "duplicate_groups":
        dataset_key = "product_master"
        dataset = datasets.get(dataset_key, {})
        group_fields = [field for field in semantics.get("dimension_refs", []) if field in {"TECH", "DEN", "MODE", "PKG_TYPE1", "PKG_TYPE2", "LEAD", "MCP_NO"}]
        if not group_fields:
            raise ContractError("intent_contract_error", "plan_compilation", "중복 판단 field가 없습니다.")
        detail_fields = [*group_fields, "DEVICE"]
        job = {
            "job_id": "job_1_product_master",
            "dataset_key": dataset_key,
            "source_type": str(dataset.get("source_type") or "fixture"),
            "parameters": {},
            "required_fields": detail_fields,
            "filters": None,
            "requirement": "required",
        }
        operations = [
            {"id": "op_detail", "op": "project", "input": "source:job_1_product_master", "fields": detail_fields},
            {"id": "op_dedupe_products", "op": "dedupe", "input": "op_detail", "fields": ["DEVICE"], "keep": "first"},
            {"id": "op_duplicate_groups", "op": "find_duplicate_groups", "input": "op_dedupe_products", "fields": group_fields, "minimum_count": 2, "count_field": "GROUP_COUNT"},
            {
                "id": "op_duplicate_rows",
                "op": "join",
                "left": "op_dedupe_products",
                "right": "op_duplicate_groups",
                "how": "inner",
                "key_mappings": [{"left": field, "right": field} for field in group_fields],
                "cardinality": "many_to_one",
                "null_key_policy": "match",
                "multi_match_policy": "error",
                "empty_side_policy": "allow",
                "output_fields": [*detail_fields, "GROUP_COUNT"],
            },
            {"id": "op_sort", "op": "sort", "input": "op_duplicate_rows", "keys": [{"field": field, "direction": "asc", "nulls": "last"} for field in [*group_fields, "DEVICE"]]},
        ]
        columns = [*detail_fields, "GROUP_COUNT"]
        return _finalize_plan(intent, bundle, catalog, [job], operations, "op_sort", columns, group_fields, {"dataset_key": dataset_key})

    if kind == "metric_presence_detail":
        metric_id = next((str(value) for value in semantics.get("metric_refs", []) if str(value) in (catalog.get("metrics") or {})), "")
        metric = (catalog.get("metrics") or {}).get(metric_id, {})
        dataset_key, query_date = _metric_dataset(metric, str(semantics.get("date")), str(semantics.get("reference_date")))
        dataset = datasets.get(dataset_key, {})
        available = set((dataset.get("fields") or {}).keys())
        binding = metric.get("source_binding") if isinstance(metric.get("source_binding"), dict) else {}
        clauses = deepcopy(binding.get("fixed_filters") or [])
        source_field = str(binding.get("field") or "")
        if source_field:
            clauses.append({"field": source_field, "operator": "gt", "value": 0, "semantic_type": "number"})
        process_values = _process_values(semantics, catalog)
        if process_values and not any(clause.get("field") == "OPER_NAME" for clause in clauses if isinstance(clause, dict)):
            clauses.append({"field": "OPER_NAME", "operator": "in", "values": process_values, "semantic_type": "string"})
        fields = [field for field in ["DEVICE"] if field in available]
        required = sorted(set(fields + [str(binding.get("field") or "")] + _filter_fields(clauses)))
        job = {
            "job_id": f"job_1_{dataset_key}",
            "dataset_key": dataset_key,
            "source_type": str(dataset.get("source_type") or "dummy"),
            "parameters": {"DATE": query_date},
            "required_fields": [field for field in required if field],
            "filters": None,
            "requirement": "required",
        }
        source = f"source:{job['job_id']}"
        operations: list[dict[str, Any]] = []
        current = source
        if clauses:
            operations.append({"id": "op_filter", "op": "filter", "input": source, "where": {"op": "all", "clauses": clauses}})
            current = "op_filter"
        operations.extend(
            [
                {"id": "op_project", "op": "project", "input": current, "fields": fields},
                {"id": "op_dedupe", "op": "dedupe", "input": "op_project", "fields": fields, "keep": "first"},
                {"id": "op_sort", "op": "sort", "input": "op_dedupe", "keys": [{"field": "DEVICE", "direction": "asc", "nulls": "last"}]},
            ]
        )
        return _finalize_plan(intent, bundle, catalog, [job], operations, "op_sort", fields, fields, {metric_id: {"dataset_key": dataset_key}})

    if kind == "equipment_enrich":
        product_keys = [str(field) for field in (((catalog.get("recipes") or {}).get("product.standard", {}).get("grain") or {}).get("keys") or [])]
        production_key = "production_today" if semantics.get("date") == semantics.get("reference_date") else "production"
        equipment_key = "equipment_assign"
        production = datasets.get(production_key, {})
        equipment = datasets.get(equipment_key, {})
        production_fields = set((production.get("fields") or {}).keys())
        equipment_fields = set((equipment.get("fields") or {}).keys())
        if not product_keys or not set(product_keys).issubset(production_fields & equipment_fields):
            raise ContractError("metadata_dependency_error", "plan_compilation", "생산-장비 제품 grain 계약이 완전하지 않습니다.")
        process_values = _process_values(semantics, catalog)
        production_clauses = [clause for clause in _product_clauses(semantics, catalog) if set(_filter_fields(clause)).issubset(production_fields)]
        equipment_clauses = [clause for clause in _product_clauses(semantics, catalog) if set(_filter_fields(clause)).issubset(equipment_fields)]
        if process_values:
            production_clauses.append({"field": "OPER_NAME", "operator": "in", "values": process_values, "semantic_type": "string"})
            equipment_clauses.append({"field": "OPER_NAME", "operator": "in", "values": process_values, "semantic_type": "string"})
        jobs = [
            {
                "job_id": f"job_1_{production_key}",
                "dataset_key": production_key,
                "source_type": str(production.get("source_type") or "dummy"),
                "parameters": {"DATE": semantics.get("date")} if "DATE" in (production.get("parameters") or {}) else {},
                "required_fields": sorted(set(product_keys + ["PRODUCTION_QTY"] + _filter_fields(production_clauses))),
                "filters": None,
                "requirement": "required",
            },
            {
                "job_id": "job_2_equipment_assign",
                "dataset_key": equipment_key,
                "source_type": str(equipment.get("source_type") or "dummy"),
                "parameters": {},
                "required_fields": sorted(set(product_keys + ["EQP_ID"] + _filter_fields(equipment_clauses))),
                "filters": None,
                "requirement": "required",
            },
        ]
        operations: list[dict[str, Any]] = []
        production_input = f"source:{jobs[0]['job_id']}"
        if production_clauses:
            operations.append({"id": "op_filter_production", "op": "filter", "input": production_input, "where": {"op": "all", "clauses": production_clauses}})
            production_input = "op_filter_production"
        operations.append({
            "id": "op_production_by_product",
            "op": "aggregate",
            "input": production_input,
            "group_by": product_keys,
            "metrics": [{"field": "PRODUCTION_QTY", "function": "sum", "as": "PRODUCTION_QTY", "dropna": True}],
        })
        left_input = "op_production_by_product"
        rank = semantics.get("rank") if isinstance(semantics.get("rank"), dict) else None
        if rank:
            operations.append({
                "id": "op_rank_production",
                "op": "rank",
                "input": left_input,
                "mode": str(rank.get("mode") or "top"),
                "partition_by": [],
                "rank_by": [{"field": "PRODUCTION_QTY", "direction": "desc" if rank.get("mode") != "bottom" else "asc", "nulls": "last"}],
                "tie_break_by": [{"field": field, "direction": "asc", "nulls": "last"} for field in product_keys],
                "limit": int(rank.get("limit") or 1),
                "tie_policy": str(semantics.get("tie_policy") or "exact_n"),
                "emit_rank_field": "RESULT_RANK",
            })
            left_input = "op_rank_production"
        equipment_input = f"source:{jobs[1]['job_id']}"
        if equipment_clauses:
            operations.append({"id": "op_filter_equipment", "op": "filter", "input": equipment_input, "where": {"op": "all", "clauses": equipment_clauses}})
            equipment_input = "op_filter_equipment"
        operations.append({
            "id": "op_equipment_by_product",
            "op": "aggregate",
            "input": equipment_input,
            "group_by": product_keys,
            "metrics": [
                {"field": "EQP_ID", "function": "nunique", "as": "EQP_COUNT", "dropna": True},
                {"field": "EQP_ID", "function": "list_unique", "as": "EQP_LIST", "dropna": True},
            ],
        })
        output_fields = [*product_keys, "PRODUCTION_QTY", "EQP_COUNT", "EQP_LIST", *(["RESULT_RANK"] if rank else [])]
        operations.append({
            "id": "op_join_equipment",
            "op": "join",
            "left": left_input,
            "right": "op_equipment_by_product",
            "how": "left",
            "key_mappings": [{"left": field, "right": field} for field in product_keys],
            "cardinality": "one_to_one",
            "null_key_policy": "match",
            "multi_match_policy": "error",
            "empty_side_policy": "allow",
            "output_fields": output_fields,
        })
        operations.append({"id": "op_project", "op": "project", "input": "op_join_equipment", "fields": output_fields})
        return _finalize_plan(
            intent,
            bundle,
            catalog,
            jobs,
            operations,
            "op_project",
            output_fields,
            product_keys,
            {
                "PRODUCTION_QTY": {"dataset_key": production_key, "source_field": "PRODUCTION_QTY", "aggregation": "sum"},
                "EQP_COUNT": {"dataset_key": equipment_key, "source_field": "EQP_ID", "aggregation": "nunique"},
                "EQP_LIST": {"dataset_key": equipment_key, "source_field": "EQP_ID", "aggregation": "list_unique"},
            },
        )

    # Registered production -> equipment left join.  The right side is reduced
    # before joining so cardinality is deterministic and suffixes are forbidden.
    production_key = "production_today" if semantics.get("date") == semantics.get("reference_date") else "production"
    production = datasets.get(production_key, {})
    equipment = datasets.get("equipment_assign", {})
    jobs = [
        {"job_id": "job_1_production", "dataset_key": production_key, "source_type": str(production.get("source_type") or "dummy"), "parameters": {"DATE": semantics.get("date")}, "required_fields": ["DEVICE", "PRODUCTION_QTY"], "filters": None, "requirement": "required"},
        {"job_id": "job_2_equipment", "dataset_key": "equipment_assign", "source_type": str(equipment.get("source_type") or "dummy"), "parameters": {}, "required_fields": ["DEVICE", "EQP_ID"], "filters": None, "requirement": "required"},
    ]
    columns = ["DEVICE", "PRODUCTION_QTY", "EQP_COUNT", "EQP_LIST"]
    operations = [
        {"id": "op_production", "op": "aggregate", "input": "source:job_1_production", "group_by": ["DEVICE"], "metrics": [{"field": "PRODUCTION_QTY", "function": "sum", "as": "PRODUCTION_QTY", "dropna": True}]},
        {"id": "op_equipment", "op": "aggregate", "input": "source:job_2_equipment", "group_by": ["DEVICE"], "metrics": [{"field": "EQP_ID", "function": "nunique", "as": "EQP_COUNT", "dropna": True}, {"field": "EQP_ID", "function": "list_unique", "as": "EQP_LIST", "dropna": True}]},
        {"id": "op_join", "op": "join", "left": "op_production", "right": "op_equipment", "how": "left", "key_mappings": [{"left": "DEVICE", "right": "DEVICE"}], "cardinality": "one_to_one", "null_key_policy": "never_match", "multi_match_policy": "error", "empty_side_policy": "allow", "output_fields": columns},
        {"id": "op_project", "op": "project", "input": "op_join", "fields": columns},
    ]
    return _finalize_plan(intent, bundle, catalog, jobs, operations, "op_project", columns, ["DEVICE"], {"PRODUCTION_QTY": {"dataset_key": production_key}, "EQP_COUNT": {"dataset_key": "equipment_assign"}})


def _compile_equipment_view_plan(
    intent: dict[str, Any],
    bundle: dict[str, Any],
    catalog: dict[str, Any],
    semantics: dict[str, Any],
    equipment_view: str,
) -> dict[str, Any]:
    """Compile the two registered equipment views without inferred code.

    ``uph_detail`` is the current UPH registry projection.  ``equipment_grouped``
    is a current assignment rollup whose count and list are derived from the
    same EQP_ID population, so the two result fields cannot drift apart.
    """

    dataset_key = "eqp_uph" if equipment_view == "uph_detail" else "equipment_assign"
    dataset = (catalog.get("datasets") or {}).get(dataset_key, {})
    available = set((dataset.get("fields") or {}).keys())
    clauses = [
        clause
        for clause in _product_clauses(semantics, catalog)
        if set(_filter_fields(clause)).issubset(available)
    ]
    process_values = _process_values(semantics, catalog)
    if process_values and "OPER_NAME" in available:
        clauses.append(
            {
                "field": "OPER_NAME",
                "operator": "in",
                "values": process_values,
                "semantic_type": "string",
            }
        )

    if equipment_view == "uph_detail":
        fields = ["EQP_MODEL", "RECIPE_ID", "OPER_NAME", "UPH"]
        missing = [field for field in fields if field not in available]
        if missing:
            raise ContractError(
                "metadata_dependency_error",
                "plan_compilation",
                "UPH 상세 view에 필요한 field가 없습니다.",
                {"dataset_key": dataset_key, "fields": missing},
            )
    else:
        fields = ["EQP_MODEL", "RECIPE_ID", "EQP_COUNT", "EQP_LIST"]
        missing = [field for field in ["EQP_MODEL", "RECIPE_ID", "EQP_ID"] if field not in available]
        if missing:
            raise ContractError(
                "metadata_dependency_error",
                "plan_compilation",
                "장비 조합 view에 필요한 field가 없습니다.",
                {"dataset_key": dataset_key, "fields": missing},
            )

    job_id = f"job_1_{dataset_key}"
    source_id = f"source:{job_id}"
    required = set(_filter_fields(clauses))
    if equipment_view == "uph_detail":
        required.update(fields)
    else:
        required.update(["EQP_MODEL", "RECIPE_ID", "EQP_ID"])
    job = {
        "job_id": job_id,
        "dataset_key": dataset_key,
        "source_type": str(dataset.get("source_type") or "dummy"),
        "parameters": {},
        "required_fields": sorted(required),
        "filters": None,
        "requirement": "required",
    }
    operations: list[dict[str, Any]] = []
    current = source_id
    if clauses:
        operations.append(
            {
                "id": "op_filter_equipment_view",
                "op": "filter",
                "input": current,
                "where": {"op": "all", "clauses": clauses},
            }
        )
        current = "op_filter_equipment_view"

    if equipment_view == "uph_detail":
        operations.extend(
            [
                {"id": "op_project_uph", "op": "project", "input": current, "fields": fields},
                {
                    "id": "op_sort_uph",
                    "op": "sort",
                    "input": "op_project_uph",
                    "keys": [
                        {"field": field, "direction": "asc", "nulls": "last"}
                        for field in ["EQP_MODEL", "RECIPE_ID", "OPER_NAME"]
                    ],
                },
            ]
        )
        lineage = {
            "UPH": {
                "dataset_key": dataset_key,
                "source_field": "UPH",
                "aggregation": "none",
                "grain": ["EQP_MODEL", "RECIPE_ID", "OPER_NAME"],
            }
        }
        return _finalize_plan(
            intent,
            bundle,
            catalog,
            [job],
            operations,
            "op_sort_uph",
            fields,
            ["EQP_MODEL", "RECIPE_ID", "OPER_NAME"],
            lineage,
        )

    operations.extend(
        [
            {
                "id": "op_group_equipment",
                "op": "aggregate",
                "input": current,
                "group_by": ["EQP_MODEL", "RECIPE_ID"],
                "metrics": [
                    {"field": "EQP_ID", "function": "nunique", "as": "EQP_COUNT", "dropna": True},
                    {"field": "EQP_ID", "function": "list_unique", "as": "EQP_LIST", "dropna": True},
                ],
            },
            {
                "id": "op_sort_equipment",
                "op": "sort",
                "input": "op_group_equipment",
                "keys": [
                    {"field": "EQP_MODEL", "direction": "asc", "nulls": "last"},
                    {"field": "RECIPE_ID", "direction": "asc", "nulls": "last"},
                ],
            },
            {"id": "op_project_equipment", "op": "project", "input": "op_sort_equipment", "fields": fields},
        ]
    )
    lineage = {
        "EQP_COUNT": {"dataset_key": dataset_key, "source_field": "EQP_ID", "aggregation": "nunique"},
        "EQP_LIST": {"dataset_key": dataset_key, "source_field": "EQP_ID", "aggregation": "list_unique"},
    }
    return _finalize_plan(
        intent,
        bundle,
        catalog,
        [job],
        operations,
        "op_project_equipment",
        fields,
        ["EQP_MODEL", "RECIPE_ID"],
        lineage,
    )


def _compile_special_plan(
    intent: dict[str, Any], bundle: dict[str, Any], catalog: dict[str, Any], semantics: dict[str, Any]
) -> dict[str, Any] | None:
    kind = str(semantics.get("analysis_kind") or "")
    qualifiers = semantics.get("qualifiers") if isinstance(semantics.get("qualifiers"), dict) else {}
    equipment_view = str(qualifiers.get("equipment_view") or "")
    if kind in {"uph_detail", "equipment_grouped"} and equipment_view in {"uph_detail", "equipment_grouped"}:
        return _compile_equipment_view_plan(intent, bundle, catalog, semantics, equipment_view)
    if kind not in {"detail", "hold_history", "equipment_detail", "compare_group_attributes"}:
        return None
    if kind == "hold_history":
        dataset_key = "hold_history"
    elif kind == "equipment_detail":
        dataset_key = "equipment_assign"
    elif kind == "compare_group_attributes":
        # This operator is defined over the registered product-master grain,
        # never over whichever transactional dataset happens to contain similar
        # columns.
        dataset_key = "product_master"
    else:
        dataset_key = "lot_status"
    dataset = (catalog.get("datasets") or {}).get(dataset_key, {})
    available = set((dataset.get("fields") or {}).keys())
    ordered_range = semantics.get("ordered_range") if isinstance(semantics.get("ordered_range"), dict) else None
    process_values = [] if ordered_range else _process_values(semantics, catalog)
    clauses = [clause for clause in _product_clauses(semantics, catalog) if set(_filter_fields(clause)).issubset(available)]
    if process_values and "OPER_NAME" in available:
        clauses.append({"field": "OPER_NAME", "operator": "in", "values": process_values, "semantic_type": "string"})
    if qualifiers.get("current_hold") and "HOLD_STAT" in available:
        clauses.append({"field": "HOLD_STAT", "operator": "eq", "value": "OnHold", "semantic_type": "string"})
    prior_lot_ids = [str(value) for value in semantics.get("prior_lot_ids", []) if str(value)]
    explicit_lot_ids = [str(value) for value in semantics.get("lot_ids", []) if str(value)]
    selected_lot_ids = explicit_lot_ids or prior_lot_ids
    if selected_lot_ids and "LOT_ID" in available:
        clauses.append({"field": "LOT_ID", "operator": "in", "values": selected_lot_ids, "semantic_type": "string"})
    metric_registry = catalog.get("metrics") if isinstance(catalog.get("metrics"), dict) else {}
    metric_ids = [str(item) for item in semantics.get("metric_refs", [])]
    for threshold in semantics.get("thresholds", []):
        if not metric_ids:
            break
        metric = metric_registry.get(metric_ids[0], {})
        source_field = str((metric.get("source_binding") or {}).get("field") or "")
        if source_field in available:
            clauses.append({"field": source_field, "operator": threshold.get("operator"), "value": threshold.get("value"), "semantic_type": "number"})
    if kind == "hold_history":
        fields = ["LOT_ID", "HOLD_EVENT_AT", "HOLD_CD", "HOLD_DESC", "OPER_NAME"]
    elif kind == "equipment_detail":
        product = ((catalog.get("recipes") or {}).get("product.standard", {}).get("grain") or {}).get("keys") or []
        fields = [*product, "EQP_ID", "EQP_MODEL", "RECIPE_ID", "OPER_NAME"]
    elif kind == "compare_group_attributes":
        fields = ["TECH", "DEN", "PKG_TYPE2", "MCP_NO", "MODE", "PKG_TYPE1", "LEAD", "DEVICE"]
    else:
        fields = ["LOT_ID", "DEVICE", "OPER_NAME", "HOLD_STAT", "HOLD_REASON", "IN_TAT", "CUM_TAT", "PROD_QTY", "WF_QTY"]
    for field in semantics.get("field_refs", []):
        if str(field) in available and str(field) not in fields:
            fields.append(str(field))
    fields = [field for field in fields if field in available]
    if kind == "hold_history" and not explicit_lot_ids:
        fields.append("HOLD_DURATION_HOURS")
    required = set([field for field in fields if field in available] + _filter_fields(clauses))
    if ordered_range and "OPER_SEQ" in available:
        required.add("OPER_SEQ")
    job_id = f"job_1_{dataset_key}"
    params = {"DATE": semantics.get("date")} if "DATE" in available else {}
    if kind == "hold_history" and selected_lot_ids:
        params["LOT_ID"] = selected_lot_ids
    jobs = [{
        "job_id": job_id,
        "dataset_key": dataset_key,
        "source_type": str(dataset.get("source_type") or "dummy"),
        "parameters": params,
        "required_fields": sorted(required),
        "filters": None,
        "requirement": "required",
    }]
    source_id = f"source:{job_id}"
    operations: list[dict[str, Any]] = []
    current = source_id
    if ordered_range and "OPER_SEQ" in available:
        range_values = set(_range_process_values(ordered_range, catalog))
        sequences = [
            int(item.get("oper_seq") or 0)
            for item in catalog.get("process_order", [])
            if isinstance(item, dict) and str(item.get("oper_name") or "") in range_values
        ]
        if not sequences:
            raise ContractError("plan_contract_error", "plan_compilation", "공정 범위 sequence가 metadata에 없습니다.")
        operations.append({
            "id": "op_ordered_range",
            "op": "ordered_range",
            "input": source_id,
            "field": "OPER_SEQ",
            "start": min(sequences),
            "end": max(sequences),
        })
        current = "op_ordered_range"
    if clauses:
        filter_input = current
        current = "op_filter_1"
        operations.append({"id": current, "op": "filter", "input": filter_input, "where": {"op": "all", "clauses": clauses}})
    if kind == "hold_history":
        filtered_history = current
        if explicit_lot_ids:
            operations.append({"id": "op_sort_hold_history", "op": "sort", "input": filtered_history, "keys": [{"field": "HOLD_EVENT_AT", "direction": "desc", "nulls": "last"}, {"field": "HOLD_CD", "direction": "asc", "nulls": "last"}]})
            current = "op_sort_hold_history"
        else:
            operations.extend([
                {
                    "id": "op_latest_hold_event",
                    "op": "aggregate",
                    "input": filtered_history,
                    "group_by": ["LOT_ID"],
                    "metrics": [{"field": "HOLD_EVENT_AT", "function": "max", "as": "CURRENT_HOLD_STARTED_AT", "dropna": True}],
                },
                {
                    "id": "op_hold_duration",
                    "op": "derive",
                    "input": "op_latest_hold_event",
                    "output_field": "HOLD_DURATION_HOURS",
                    "formula": {
                        "expression": {
                            "op": "datetime_diff_hours",
                            "args": [
                                {"literal": semantics.get("reference_instant")},
                                {"field_ref": "CURRENT_HOLD_STARTED_AT"},
                            ],
                        },
                        "rounding": {"digits": 3},
                    },
                },
                {
                    "id": "op_oldest_hold_lot",
                    "op": "rank",
                    "input": "op_hold_duration",
                    "mode": "top",
                    "partition_by": [],
                    "rank_by": [{"field": "HOLD_DURATION_HOURS", "direction": "desc", "nulls": "last"}],
                    "tie_break_by": [{"field": "LOT_ID", "direction": "asc", "nulls": "last"}],
                    "limit": 1,
                    "tie_policy": "include_all",
                    "emit_rank_field": "RESULT_RANK",
                },
                {
                    "id": "op_selected_hold_history",
                    "op": "join",
                    "left": filtered_history,
                    "right": "op_oldest_hold_lot",
                    "how": "inner",
                    "key_mappings": [{"left": "LOT_ID", "right": "LOT_ID"}],
                    "cardinality": "many_to_one",
                    "null_key_policy": "never_match",
                    "multi_match_policy": "error",
                    "empty_side_policy": "allow",
                    "output_fields": fields,
                },
                {"id": "op_hold_history_detail", "op": "detail", "input": "op_selected_hold_history", "fields": fields},
                {"id": "op_sort_hold_history", "op": "sort", "input": "op_hold_history_detail", "keys": [{"field": "HOLD_EVENT_AT", "direction": "desc", "nulls": "last"}, {"field": "LOT_ID", "direction": "asc", "nulls": "last"}]},
            ])
            current = "op_sort_hold_history"
    elif kind == "compare_group_attributes":
        compare_id = "op_compare_group_attributes"
        operations.append({
            "id": compare_id,
            "op": "compare_group_attributes",
            "input": current,
            "group_by": [field for field in ["TECH", "DEN", "PKG_TYPE2", "MCP_NO"] if field in fields],
            "comparison_fields": [field for field in ["MODE", "PKG_TYPE1", "LEAD"] if field in fields],
            "comparison_rule": "any",
        })
        current = compare_id
    project_id = "op_project"
    operations.append({"id": project_id, "op": "project", "input": current, "fields": fields})
    current = project_id
    if kind in {"detail", "equipment_detail"}:
        dedupe_fields = [field for field in (["LOT_ID"] if kind == "detail" else fields) if field in fields]
        if dedupe_fields:
            operations.append({"id": "op_dedupe", "op": "dedupe", "input": current, "fields": dedupe_fields, "keep": "first"})
            current = "op_dedupe"
    if kind == "compare_group_attributes":
        sort_fields = [field for field in ["TECH", "DEN", "PKG_TYPE2", "MCP_NO", "MODE", "PKG_TYPE1", "LEAD", "DEVICE"] if field in fields]
        operations.append({"id": "op_sort_detail", "op": "sort", "input": current, "keys": [{"field": field, "direction": "asc", "nulls": "last"} for field in sort_fields]})
        current = "op_sort_detail"
    elif kind == "detail":
        sort_fields = [field for field in (["IN_TAT"] if "IN_TAT" in fields else ["OPER_NAME", "LOT_ID"]) if field in fields]
        if sort_fields:
            operations.append({"id": "op_sort_detail", "op": "sort", "input": current, "keys": [{"field": field, "direction": "desc" if field == "IN_TAT" else "asc", "nulls": "last"} for field in sort_fields]})
            current = "op_sort_detail"
    return _finalize_plan(intent, bundle, catalog, jobs, operations, current, fields, [field for field in fields if field in {"LOT_ID", "EQP_ID", "DEVICE"}], {"dataset_key": dataset_key})


def _compile_previous_plan(
    intent: dict[str, Any],
    bundle: dict[str, Any],
    catalog: dict[str, Any],
    semantics: dict[str, Any],
    prior_result: dict[str, Any] | None,
) -> dict[str, Any] | None:
    kind = str(semantics.get("analysis_kind") or "")
    if kind not in {"previous_rank", "equipment_enrich"}:
        return None
    if kind == "equipment_enrich" and semantics.get("followup_mode") != "referenced":
        return None
    rows = (prior_result or {}).get("rows") if isinstance(prior_result, dict) else None
    columns = [str(value) for value in ((prior_result or {}).get("columns") or [])] if isinstance(prior_result, dict) else []
    if not isinstance(rows, list) or not columns:
        raise ContractError("state_reference_expired", "plan_compilation", "이전 분석 결과를 사용할 수 없습니다.")
    if kind == "previous_rank":
        metric_candidates = [str(value) for value in semantics.get("metric_refs", []) if str(value) in columns]
        rank_field = metric_candidates[0] if metric_candidates else next((field for field in reversed(columns) if field.endswith(("_QTY", "_COUNT", "UPH"))), "")
        if not rank_field:
            raise ContractError("plan_contract_error", "plan_compilation", "이전 결과에서 순위 metric을 찾을 수 없습니다.")
        rank = semantics.get("rank") if isinstance(semantics.get("rank"), dict) else {"mode": "top", "limit": 1}
        output_columns = [field for field in columns if field != "RESULT_RANK"] + ["RESULT_RANK"]
        operations = [
            {"id": "op_previous", "op": "transform_previous_result", "input": "source:previous"},
            {
                "id": "op_rank_previous",
                "op": "rank",
                "input": "op_previous",
                "mode": str(rank.get("mode") or "top"),
                "partition_by": [],
                "rank_by": [{"field": rank_field, "direction": "desc" if rank.get("mode") != "bottom" else "asc", "nulls": "last"}],
                "tie_break_by": [{"field": field, "direction": "asc", "nulls": "last"} for field in columns if field != rank_field][:8],
                "limit": int(rank.get("limit") or 1),
                "tie_policy": str(semantics.get("tie_policy") or "exact_n"),
                "emit_rank_field": "RESULT_RANK",
            },
            {"id": "op_project", "op": "project", "input": "op_rank_previous", "fields": output_columns},
        ]
        return _finalize_plan(
            intent,
            bundle,
            catalog,
            [],
            operations,
            "op_project",
            output_columns,
            [],
            {"previous_result": True},
            input_refs=["previous"],
        )

    dataset_key = "equipment_assign"
    dataset = (catalog.get("datasets") or {}).get(dataset_key, {})
    available = set((dataset.get("fields") or {}).keys())
    product_keys = [field for field in (((catalog.get("recipes") or {}).get("product.standard", {}).get("grain") or {}).get("keys") or []) if field in columns and field in available]
    if not product_keys:
        raise ContractError("plan_contract_error", "plan_compilation", "이전 결과와 장비 metadata의 제품 key가 겹치지 않습니다.")
    process_values = _process_values(semantics, catalog)
    clauses = [{"field": "OPER_NAME", "operator": "in", "values": process_values, "semantic_type": "string"}] if process_values else []
    job_id = "job_1_equipment_assign"
    jobs = [{
        "job_id": job_id,
        "dataset_key": dataset_key,
        "source_type": str(dataset.get("source_type") or "dummy"),
        "parameters": {},
        "required_fields": sorted(set(product_keys + ["EQP_ID"] + _filter_fields(clauses))),
        "filters": None,
        "requirement": "required",
    }]
    right_input = f"source:{job_id}"
    operations: list[dict[str, Any]] = [{"id": "op_previous", "op": "transform_previous_result", "input": "source:previous"}]
    if clauses:
        operations.append({"id": "op_filter_equipment", "op": "filter", "input": right_input, "where": {"op": "all", "clauses": clauses}})
        right_input = "op_filter_equipment"
    operations.append({
        "id": "op_equipment_by_product",
        "op": "aggregate",
        "input": right_input,
        "group_by": product_keys,
        "metrics": [
            {"field": "EQP_ID", "function": "nunique", "as": "EQP_COUNT", "dropna": True},
            {"field": "EQP_ID", "function": "list_unique", "as": "EQP_LIST", "dropna": True},
        ],
    })
    output_columns = [field for field in columns if field != "RESULT_RANK"] + ["EQP_COUNT", "EQP_LIST"]
    operations.append({
        "id": "op_enrich_previous",
        "op": "enrich_previous_result",
        "left": "op_previous",
        "right": "op_equipment_by_product",
        "key_mappings": [{"left": field, "right": field} for field in product_keys],
        "cardinality": "one_to_one",
        "null_key_policy": "match",
        "multi_match_policy": "error",
        "empty_side_policy": "allow",
        "output_fields": output_columns,
    })
    operations.append({"id": "op_project", "op": "project", "input": "op_enrich_previous", "fields": output_columns})
    return _finalize_plan(
        intent,
        bundle,
        catalog,
        jobs,
        operations,
        "op_project",
        output_columns,
        product_keys,
        {"EQP_COUNT": {"dataset_key": dataset_key, "source_field": "EQP_ID", "aggregation": "nunique"}},
        input_refs=["previous"],
    )


def compile_plan(
    intent: dict[str, Any],
    bundle: dict[str, Any],
    catalog: dict[str, Any],
    *,
    prior_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    semantics = intent.get("semantics") if isinstance(intent.get("semantics"), dict) else {}
    if semantics.get("analysis_kind") == "clarification":
        raise ContractError(
            "needs_clarification",
            "intent_validation",
            "어떤 수량을 조회할지 선택해 주세요: 생산량, INPUT 실적, 재공수량, 계획수량.",
            {"options": ["PRODUCTION_QTY", "INPUT_QTY", "WIP_QTY", "INPUT_PLAN_QTY", "OUT_PLAN_QTY"]},
        )
    previous = _compile_previous_plan(intent, bundle, catalog, semantics, prior_result)
    if previous is not None:
        return previous
    operator_special = _compile_operator_special_plan(intent, bundle, catalog, semantics)
    if operator_special is not None:
        return operator_special
    special = _compile_special_plan(intent, bundle, catalog, semantics)
    if special is not None:
        return special
    metric_ids = [str(item) for item in semantics.get("metric_refs", [])]
    metric_registry = catalog.get("metrics") if isinstance(catalog.get("metrics"), dict) else {}
    kind = str(semantics.get("analysis_kind") or "aggregate")
    dimensions = [str(item) for item in semantics.get("dimension_refs", [])]
    product_recipe = (catalog.get("recipes") or {}).get("product.standard", {})
    product_dimensions = [str(item) for item in ((product_recipe.get("grain") or {}).get("keys") or [])]
    rank_partitions = deepcopy(dimensions) if kind == "group_rank" else []
    if not dimensions:
        dimensions = deepcopy(product_dimensions)
    elif kind == "group_rank":
        dimensions = list(dict.fromkeys([*dimensions, *product_dimensions]))
    if isinstance(semantics.get("ordered_range"), dict) and "OPER_NAME" in dimensions and "OPER_SEQ" not in dimensions:
        dimensions.append("OPER_SEQ")
    requested_date = str(semantics.get("date") or "")
    reference_date = str(semantics.get("reference_date") or requested_date)
    jobs: list[dict[str, Any]] = []
    operations: list[dict[str, Any]] = []
    lineage: dict[str, Any] = {}
    aggregate_ids: list[str] = []
    process_values = _process_values(semantics, catalog)
    if isinstance(semantics.get("ordered_range"), dict):
        process_values = _range_process_values(semantics.get("ordered_range"), catalog)
    product_clauses = _product_clauses(semantics, catalog)

    grouped_metrics: dict[tuple[str, str, str], list[tuple[str, dict[str, Any]]]] = {}
    for metric_id in metric_ids:
        metric = metric_registry.get(metric_id)
        if not isinstance(metric, dict):
            raise ContractError("metadata_dependency_error", "plan_compilation", "등록되지 않은 metric입니다.", {"metric_id": metric_id})
        if metric.get("source_binding"):
            dataset_key, query_date = _metric_dataset(metric, requested_date, reference_date)
            binding = metric.get("source_binding") if isinstance(metric.get("source_binding"), dict) else {}
            fixed_filters = deepcopy(binding.get("fixed_filters") or [])
            grouped_metrics.setdefault((dataset_key, query_date, sha256_json(fixed_filters)), []).append((metric_id, metric))

    aggregate_metric_groups: list[list[str]] = []
    jobs_by_source: dict[tuple[str, str], dict[str, Any]] = {}
    scoped_processes = semantics.get("process_refs_by_metric") if isinstance(semantics.get("process_refs_by_metric"), dict) else {}
    for index, ((dataset_key, query_date, _), group) in enumerate(grouped_metrics.items(), start=1):
        source_key = (dataset_key, query_date)
        dataset = (catalog.get("datasets") or {}).get(dataset_key, {})
        if source_key not in jobs_by_source:
            job_id = f"job_{len(jobs_by_source) + 1}_{dataset_key}"
            declared_parameters = dataset.get("parameters") if isinstance(dataset.get("parameters"), dict) else {}
            jobs_by_source[source_key] = {
                "job_id": job_id,
                "dataset_key": dataset_key,
                "source_type": str(dataset.get("source_type") or "dummy"),
                "parameters": {"DATE": query_date} if "DATE" in declared_parameters else {},
                "required_fields": [],
                "filters": None,
                "requirement": "required",
            }
            jobs.append(jobs_by_source[source_key])
        job = jobs_by_source[source_key]
        job_id = str(job["job_id"])
        source_id = f"source:{job_id}"
        dataset_fields = set((dataset.get("fields") or {}).keys())
        clauses = [clause for clause in deepcopy(product_clauses) if set(_filter_fields(clause)).issubset(dataset_fields)]
        fixed_filters = deepcopy(((group[0][1].get("source_binding") or {}).get("fixed_filters") or []))
        clauses.extend(clause for clause in fixed_filters if isinstance(clause, dict))
        group_process_refs: list[str] = []
        for metric_id, _metric in group:
            for process_ref in scoped_processes.get(metric_id, []) if isinstance(scoped_processes.get(metric_id), list) else []:
                if str(process_ref) not in group_process_refs:
                    group_process_refs.append(str(process_ref))
        selected_process_values = _process_values({"process_refs": group_process_refs}, catalog) if group_process_refs else process_values
        fixed_process = any(isinstance(clause, dict) and clause.get("field") == "OPER_NAME" for clause in fixed_filters)
        if selected_process_values and "OPER_NAME" in dataset_fields and not fixed_process:
            clauses.append({"field": "OPER_NAME", "operator": "in", "values": selected_process_values, "semantic_type": "string"})
        if "DATE" not in (dataset.get("parameters") or {}) and isinstance(dataset.get("date_filter_contract"), dict) and "DATE" in dataset_fields:
            clauses.append({"field": "DATE", "operator": "eq", "value": query_date, "semantic_type": "date"})
        required_fields = set(dimensions + [str((metric.get("source_binding") or {}).get("field")) for _, metric in group] + _filter_fields(clauses))
        job["required_fields"] = sorted(set(job.get("required_fields") or []) | {field for field in required_fields if field})
        current_id = source_id
        if clauses:
            filtered_id = f"op_filter_{index}"
            operations.append({"id": filtered_id, "op": "filter", "input": current_id, "where": {"op": "all", "clauses": clauses}})
            current_id = filtered_id
        qualifiers = semantics.get("qualifiers") if isinstance(semantics.get("qualifiers"), dict) else {}
        if qualifiers.get("preserve_blank_product"):
            for derive_index, field in enumerate([value for value in dimensions if value in product_dimensions], start=1):
                derive_id = f"op_fill_product_{index}_{derive_index}"
                operations.append({
                    "id": derive_id,
                    "op": "derive",
                    "input": current_id,
                    "output_field": field,
                    "formula": {"expression": {"op": "coalesce_blank", "args": [{"field_ref": field}, {"literal": ""}]}},
                })
                current_id = derive_id
        if qualifiers.get("fill_metric_zero"):
            for derive_index, (_metric_id, metric) in enumerate(group, start=1):
                source_field = str((metric.get("source_binding") or {}).get("field") or "")
                if not source_field:
                    continue
                derive_id = f"op_fill_metric_{index}_{derive_index}"
                operations.append({
                    "id": derive_id,
                    "op": "derive",
                    "input": current_id,
                    "output_field": source_field,
                    "formula": {"expression": {"op": "coalesce", "args": [{"metric_ref": source_field}, {"literal": 0}]}},
                })
                current_id = derive_id
        ordered_range = semantics.get("ordered_range")
        if isinstance(ordered_range, dict):
            order_map: dict[str, Any] = {}
            for item in catalog.get("process_order", []):
                if not isinstance(item, dict):
                    continue
                sequence = item.get("oper_seq")
                for name in [item.get("oper_name"), *(item.get("aliases") or [])]:
                    order_map[normalize_text(str(name)).upper()] = sequence
            start = order_map.get(normalize_text(str(ordered_range.get("start"))).upper())
            end = order_map.get(normalize_text(str(ordered_range.get("end"))).upper())
            if start is None or end is None:
                raise ContractError("plan_contract_error", "plan_compilation", "공정 범위 endpoint가 metadata에 없습니다.")
            range_id = f"op_range_{index}"
            operations.append({"id": range_id, "op": "ordered_range", "input": current_id, "field": "OPER_SEQ", "start": min(start, end), "end": max(start, end)})
            current_id = range_id
        aggregate_id = f"op_aggregate_{index}"
        aggregate_metrics: list[dict[str, Any]] = []
        group_metric_ids: list[str] = []
        for metric_id, metric in group:
            binding = metric.get("source_binding") if isinstance(metric.get("source_binding"), dict) else {}
            additivity = metric.get("additivity") if isinstance(metric.get("additivity"), dict) else {}
            default = str(additivity.get("default") or "additive")
            function = "sum" if default == "additive" else "nunique" if default == "distinct" else "mean"
            aggregate_metrics.append({"field": binding.get("field"), "function": function, "as": metric_id, "dropna": True})
            group_metric_ids.append(metric_id)
            lineage[metric_id] = {
                "dataset_key": dataset_key,
                "source_field": binding.get("field"),
                "query_date": query_date,
                "aggregation": function,
                "grain": dimensions,
            }
        operations.append({"id": aggregate_id, "op": "aggregate", "input": current_id, "group_by": dimensions, "metrics": aggregate_metrics})
        aggregate_ids.append(aggregate_id)
        aggregate_metric_groups.append(group_metric_ids)

    current_id = aggregate_ids[0] if aggregate_ids else ""
    if len(aggregate_ids) > 1:
        joined_metric_ids = list(aggregate_metric_groups[0])
        for join_index, right_id in enumerate(aggregate_ids[1:], start=2):
            joined_id = f"op_join_{join_index}"
            operations.append(
                {
                    "id": joined_id,
                    "op": "join",
                    "left": current_id,
                    "right": right_id,
                    "how": "left",
                    "key_mappings": [{"left": field, "right": field} for field in dimensions],
                    "cardinality": "one_to_one",
                    "null_key_policy": "match",
                    "multi_match_policy": "error",
                    "empty_side_policy": "allow",
                    "output_fields": dimensions + joined_metric_ids + aggregate_metric_groups[join_index - 1],
                }
            )
            current_id = joined_id
            joined_metric_ids.extend(aggregate_metric_groups[join_index - 1])

    if kind == "presence" and len(aggregate_ids) >= 2:
        presence_id = "op_presence"
        operations.append(
            {
                "id": presence_id,
                "op": "presence_filter",
                "left": aggregate_ids[0],
                "right": aggregate_ids[1],
                "keys": dimensions,
                "left_metric": metric_ids[0],
                "right_metric": metric_ids[1],
                "materialize_right_zero": True,
            }
        )
        current_id = presence_id
    elif kind == "formula" and len(metric_ids) >= 2:
        formula_metric_id = "ACHIEVEMENT_RATE" if "ACHIEVEMENT_RATE" in metric_ids else str(semantics.get("formula_ref") or "ACHIEVEMENT_RATE")
        formula_record = metric_registry.get(formula_metric_id, {})
        formula_id = "op_formula"
        operations.append(
            {
                "id": formula_id,
                "op": "derive",
                "input": current_id,
                "output_field": formula_metric_id,
                "formula": formula_record.get("formula")
                or {
                    "expression": {
                        "op": "multiply",
                        "args": [
                            {"op": "safe_divide", "args": [{"metric_ref": metric_ids[1]}, {"metric_ref": metric_ids[0]}], "zero_division": "null"},
                            {"literal": 100},
                        ],
                    },
                    "rounding": {"digits": 1},
                },
            }
        )
        current_id = formula_id
        if formula_metric_id not in metric_ids:
            metric_ids.append(formula_metric_id)

    if kind == "field_compare" and len(metric_ids) >= 2:
        compare_id = "op_compare_fields"
        operations.append(
            {
                "id": compare_id,
                "op": "compare_fields",
                "input": current_id,
                "left_field": metric_ids[0],
                "right_field": metric_ids[1],
                "operator": str(semantics.get("comparison_operator") or "gt"),
                "semantic_type": "number",
                "type_compatibility": "numeric",
                "null_policy": "false",
            }
        )
        current_id = compare_id

    segmented_rank = kind in {"multi_metric_argmax", "top_bottom"}
    segment_label_field = ""
    if kind == "multi_metric_argmax" and len(aggregate_metric_groups) >= 2:
        rank_ids: list[tuple[str, str]] = []
        source_metric_ids = [group[0] for group in aggregate_metric_groups if group]
        for segment_index, metric_id in enumerate(source_metric_ids, start=1):
            rank_id = f"op_rank_metric_{segment_index}"
            operations.append(
                {
                    "id": rank_id,
                    "op": "rank",
                    "input": current_id,
                    "mode": "top",
                    "partition_by": [],
                    "rank_by": [{"field": metric_id, "direction": "desc", "nulls": "last"}],
                    "tie_break_by": [{"field": field, "direction": "asc", "nulls": "last"} for field in dimensions],
                    "limit": 1,
                    "tie_policy": "include_all",
                    "emit_rank_field": "RESULT_RANK",
                }
            )
            rank_ids.append((rank_id, metric_id))
        segment_label_field = "RESULT_METRIC"
        operations.append(
            {
                "id": "op_concat_segments",
                "op": "concat_segments",
                "segments": [{"input": rank_id, "label": label} for rank_id, label in rank_ids],
                "label_field": segment_label_field,
            }
        )
        current_id = "op_concat_segments"
    elif kind == "top_bottom" and metric_ids:
        segments = semantics.get("rank_segments") if isinstance(semantics.get("rank_segments"), list) else []
        rank_ids = []
        for segment_index, rank_spec in enumerate(segments, start=1):
            mode = str(rank_spec.get("mode") or "top")
            rank_id = f"op_rank_{mode}_{segment_index}"
            operations.append(
                {
                    "id": rank_id,
                    "op": "rank",
                    "input": current_id,
                    "mode": mode,
                    "partition_by": [],
                    "rank_by": [{"field": metric_ids[0], "direction": "desc" if mode == "top" else "asc", "nulls": "last"}],
                    "tie_break_by": [{"field": field, "direction": "asc", "nulls": "last"} for field in dimensions],
                    "limit": int(rank_spec.get("limit") or 1),
                    "tie_policy": "exact_n",
                    "emit_rank_field": "RESULT_RANK",
                }
            )
            rank_ids.append((rank_id, mode.upper()))
        segment_label_field = "RESULT_SEGMENT"
        operations.append(
            {
                "id": "op_concat_segments",
                "op": "concat_segments",
                "segments": [{"input": rank_id, "label": label} for rank_id, label in rank_ids],
                "label_field": segment_label_field,
            }
        )
        current_id = "op_concat_segments"

    rank = semantics.get("rank") if isinstance(semantics.get("rank"), dict) else None
    if rank and not segmented_rank:
        rank_metric = metric_ids[0]
        rank_id = "op_rank"
        direction = "desc" if rank.get("mode") == "top" else "asc"
        operations.append(
            {
                "id": rank_id,
                "op": "rank",
                "input": current_id,
                "mode": rank.get("mode"),
                "partition_by": rank_partitions,
                "rank_by": [{"field": rank_metric, "direction": direction, "nulls": "last"}],
                "tie_break_by": [{"field": field, "direction": "asc", "nulls": "last"} for field in dimensions],
                "limit": int(rank.get("limit") or 1),
                "tie_policy": str(semantics.get("tie_policy") or "exact_n"),
                "emit_rank_field": "RESULT_RANK",
            }
        )
        current_id = rank_id

    sort_spec = semantics.get("sort") if isinstance(semantics.get("sort"), dict) else None
    if sort_spec and not rank and str(sort_spec.get("field") or ""):
        sort_id = "op_sort_metric"
        operations.append({"id": sort_id, "op": "sort", "input": current_id, "keys": [{"field": str(sort_spec["field"]), "direction": str(sort_spec.get("direction") or "desc"), "nulls": "last"}]})
        current_id = sort_id
    elif "OPER_SEQ" in dimensions and not rank:
        sort_id = "op_sort_process_sequence"
        operations.append({"id": sort_id, "op": "sort", "input": current_id, "keys": [{"field": "OPER_SEQ", "direction": "asc", "nulls": "last"}]})
        current_id = sort_id
    elif dimensions and not rank and not segmented_rank:
        # Source row order is not a contract.  Every otherwise-unsorted result
        # gets a deterministic canonical-grain ordering.
        sort_id = "op_sort_grain"
        operations.append({
            "id": sort_id,
            "op": "sort",
            "input": current_id,
            "keys": [{"field": field, "direction": "asc", "nulls": "last"} for field in dimensions],
        })
        current_id = sort_id

    fields = [str(item) for item in semantics.get("field_refs", [])]
    output_columns = dimensions + metric_ids + (["RESULT_RANK"] if rank or segmented_rank else [])
    if segment_label_field:
        output_columns = [segment_label_field, *output_columns]
    for field in fields:
        if field not in output_columns:
            output_columns.append(field)
    project_id = "op_project"
    operations.append({"id": project_id, "op": "project", "input": current_id, "fields": output_columns})
    current_id = project_id
    plan_material = {
        "contract_version": "analysis.plan.v1",
        "intent_sha256": intent.get("intent_sha256"),
        "candidate_bundle_sha256": bundle.get("bundle_sha256"),
        "catalog_sha256": catalog.get("catalog_sha256"),
        "retrieval_jobs": jobs,
        "operations": operations,
        "result_operation_id": current_id,
        "result_contract": {
            "columns": output_columns,
            "ordering": [],
            "grain": dimensions,
        },
        "lineage": lineage,
    }
    normalized = deepcopy(plan_material)
    normalized["retrieval_jobs"] = sorted(normalized["retrieval_jobs"], key=lambda item: item["job_id"])
    plan_id = f"plan:{sha256_json(normalized)}"
    semantic_material = {key: normalized[key] for key in ("catalog_sha256", "retrieval_jobs", "operations", "result_operation_id", "result_contract", "lineage")}
    return {**plan_material, "plan_id": plan_id, "plan_fingerprint": sha256_json(semantic_material)}


def validate_plan(plan: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    jobs = plan.get("retrieval_jobs") if isinstance(plan.get("retrieval_jobs"), list) else []
    operations = plan.get("operations") if isinstance(plan.get("operations"), list) else []
    if not operations or (not jobs and "previous" not in (plan.get("input_refs") or [])):
        raise ContractError("plan_contract_error", "plan_validation", "조회 작업 또는 operation DAG가 없습니다.")
    job_ids = [str(item.get("job_id") or "") for item in jobs]
    if len(job_ids) != len(set(job_ids)) or any(not item for item in job_ids):
        raise ContractError("plan_contract_error", "plan_validation", "retrieval job ID가 없거나 중복되었습니다.")
    dataset_registry = catalog.get("datasets") if isinstance(catalog.get("datasets"), dict) else {}
    for job in jobs:
        dataset = dataset_registry.get(str(job.get("dataset_key") or ""))
        if not isinstance(dataset, dict):
            raise ContractError("metadata_dependency_error", "plan_validation", "dataset contract가 없습니다.")
        available = set(dataset.get("fields", {}).keys()) if isinstance(dataset.get("fields"), dict) else set()
        missing = sorted(set(job.get("required_fields") or []) - available)
        if missing:
            raise ContractError("plan_contract_error", "plan_validation", "dataset에 필요한 field role이 없습니다.", {"dataset_key": job.get("dataset_key"), "fields": missing})
    operation_ids = [str(item.get("id") or "") for item in operations]
    if len(operation_ids) != len(set(operation_ids)) or any(not item for item in operation_ids):
        raise ContractError("plan_contract_error", "plan_validation", "operation ID가 없거나 중복되었습니다.")
    if str(plan.get("result_operation_id") or "") not in operation_ids:
        raise ContractError("plan_contract_error", "plan_validation", "result operation이 존재하지 않습니다.")
    available_refs = {f"source:{job_id}" for job_id in job_ids}
    if "previous" in (plan.get("input_refs") or []):
        available_refs.add("source:previous")
    supported_ops = {
        "filter", "ordered_range", "project", "detail", "aggregate", "sort", "rank",
        "compare_fields", "compare_group_attributes", "find_duplicate_groups", "join",
        "presence_filter", "derive", "dedupe", "row_match_groups", "concat_segments",
        "transform_previous_result", "enrich_previous_result", "explain_previous",
    }
    for operation in operations:
        operation_id = str(operation.get("id") or "")
        operator = str(operation.get("op") or "")
        if operator not in supported_ops:
            raise ContractError("unsupported_operation", "plan_validation", "등록되지 않은 typed operator입니다.", {"operator": operator})
        refs: list[str] = []
        if operator in {"join", "presence_filter", "enrich_previous_result"}:
            refs.extend([str(operation.get("left") or ""), str(operation.get("right") or "")])
        elif operator == "concat_segments":
            refs.extend(str(item.get("input") or "") for item in operation.get("segments", []) if isinstance(item, dict))
        else:
            input_ref = str(operation.get("input") or "")
            if input_ref:
                refs.append(input_ref)
        missing_refs = [value for value in refs if not value or value not in available_refs]
        if missing_refs:
            raise ContractError("plan_contract_error", "plan_validation", "operation DAG 입력이 존재하지 않습니다.", {"operation_id": operation_id, "missing_inputs": missing_refs})
        if operator == "join":
            required_policies = {"key_mappings", "cardinality", "null_key_policy", "multi_match_policy", "empty_side_policy", "output_fields"}
            missing_policies = sorted(key for key in required_policies if key not in operation)
            if missing_policies:
                raise ContractError("plan_contract_error", "plan_validation", "join policy가 완전하지 않습니다.", {"operation_id": operation_id, "missing": missing_policies})
        available_refs.add(operation_id)
    if set(plan.get("result_contract", {}).get("columns", [])) & {"generated_code", "pandas_code"}:
        raise ContractError("plan_contract_error", "plan_validation", "retired pandas code field는 사용할 수 없습니다.")
    return plan
