"""Closed, domain-neutral candidate routing for runtime catalog v2.

This module converts request evidence plus a sealed ``metadata.runtime.catalog.v2``
into a small set of *complete* intent candidates.  It never creates source code,
physical columns, datasets, relations, metrics, fields, or formulas.  Every
semantic reference in a candidate must already exist in the supplied catalog.

The routing invariant is intentionally simple and model-independent:

* exactly one complete candidate -> ``deterministic``;
* two or more complete candidates -> ``intent_llm`` (selection only);
* no complete candidate -> ``unsupported``.

An intent model can therefore choose only a sealed ``candidate_id``.  It cannot
author or repair analysis logic.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from itertools import product
from typing import Any, Callable, Iterable, Mapping

from .canonical import ContractError, bounded, sha256_json
from .registered_functions import validate_registered_function_card
from .request_literals import extract_date_candidates, normalize_text


CATALOG_VERSION = "metadata.runtime.catalog.v2"
BUNDLE_VERSION = "resolved.candidate.bundle.v1"
ROUTE_VERSION = "analysis.route.v1"
ROUTE_POLICY_VERSION = "route-policy.v1"
INTENT_VERSION = "analysis.intent.v1"
MAX_MATCHES_PER_TYPE = 64
MAX_INTENT_CANDIDATES = 32
MAX_AMBIGUITY_VARIANTS = 16
MAX_BUNDLE_BYTES = 28 * 1024
DEFAULT_CANDIDATE_IDENTITIES_BY_TYPE = {
    "dataset": 10,
    "entity_group": 10,
}
MIN_CONFIGURED_CANDIDATE_IDENTITIES = 1
MAX_CONFIGURED_CANDIDATE_IDENTITIES = MAX_MATCHES_PER_TYPE

CATALOG_TARGET_SECTIONS = {
    "dataset": "datasets",
    "field": "fields",
    "metric": "metrics",
    "entity_group": "entity_groups",
    "grain": "grains",
    "relation": "relations",
    "recipe": "recipes",
}

MATCH_POOL_KEYS = {
    "dataset": "dataset_candidates",
    "field": "field_candidates",
    "metric": "metric_candidates",
    "entity_group": "entity_group_candidates",
    "grain": "grain_candidates",
    "relation": "relation_candidates",
    "recipe": "recipe_candidates",
    "function": "function_candidates",
}

ALLOWED_TEMPLATE_OPERATIONS = {
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

UNSUPPORTED_LEXEMES = (
    "예측",
    "forecast",
    "원인 분석",
    "왜 발생",
    "root cause",
    "최적화",
    "optimize",
    "시뮬레이션",
    "simulate",
)

OPERATION_LEXEMES = {
    "rank": ("상위", "하위", "top", "bottom", "가장 큰", "가장 작은", "최대", "최소", "highest", "lowest"),
    "project": ("컬럼", "필드", "열만", "column", "field", "projection"),
    "join": ("조인", "join", "붙여", "합쳐", "함께", "연결"),
    # Side-by-side wording such as "대비"/"비교" is not a row-filter
    # instruction.  compare_fields is eligible only when the question states
    # a directional comparison predicate explicitly.
    "compare_fields": (
        "보다 큰",
        "보다 작은",
        "보다 크거나 같은",
        "보다 작거나 같은",
        "초과",
        "미만",
        "이상",
        "이하",
        "greater than",
        "less than",
        "at least",
        "at most",
        "above",
        "below",
    ),
    "sort": ("큰 순", "작은 순", "내림차순", "오름차순", "정렬", "sort"),
    "aggregate": ("합계", "총 ", "전체", "평균", "별", "sum", "total", "average", "aggregate"),
    "detail": ("목록", "상세", "보여", "알려", "list", "detail", "show"),
}

TOP_N_PATTERN = re.compile(r"(?P<mode>상위|하위|top|bottom)\s*(?P<limit>\d+)\s*(?:개|건|rows?)?", re.I)

TOP_LEVEL_KEYS = {
    "contract_version",
    "request_id",
    "dataset_candidates",
    "field_candidates",
    "metric_candidates",
    "entity_group_candidates",
    "grain_candidates",
    "relation_candidates",
    "recipe_candidates",
    "function_candidates",
    "intent_candidates",
    "prompt_cards",
    "bundle_sha256",
    "route_decision",
    "route_evidence",
}

INTENT_CANDIDATE_KEYS = {
    "candidate_id",
    "description",
    "semantics",
    "semantics_sha256",
    "required_slots",
    "resolved_slots",
    "evidence_refs",
}

PROMPT_CARD_KEYS = {
    "candidate_id",
    "description",
    "analysis_kind",
    "metric_refs",
    "dimension_refs",
    "recipe_refs",
    "function_refs",
    "unresolved_slots",
}

ROUTE_KEYS = {
    "contract_version",
    "route",
    "reason_code",
    "resolved_candidate_bundle_sha256",
    "selected_candidate_ids",
    "required_slots",
    "unresolved_slots",
    "ambiguity_sets",
    "route_policy_version",
    "eligibility_proof_sha256",
}


def build_generic_v2_candidate_bundle(
    request: dict[str, Any],
    catalog: dict[str, Any],
    *,
    prior_semantics: dict[str, Any] | None = None,
    prior_result: dict[str, Any] | None = None,
    max_dataset_candidates: int = DEFAULT_CANDIDATE_IDENTITIES_BY_TYPE["dataset"],
    max_entity_group_candidates: int = DEFAULT_CANDIDATE_IDENTITIES_BY_TYPE["entity_group"],
) -> dict[str, Any]:
    """Build the canonical runtime bundle consumed by the v2 intent resolver."""

    _validate_catalog(catalog)
    request_id = str(request.get("request_id") or "")
    if not request_id:
        _fail("intent_contract_error", "candidate_routing", "request_id가 필요합니다.")
    question = normalize_text(str(request.get("question") or ""))
    if not question:
        _fail("intent_contract_error", "candidate_routing", "질문이 비어 있습니다.")

    identity_limits = {
        "dataset": _configured_candidate_limit(
            max_dataset_candidates,
            DEFAULT_CANDIDATE_IDENTITIES_BY_TYPE["dataset"],
        ),
        "entity_group": _configured_candidate_limit(
            max_entity_group_candidates,
            DEFAULT_CANDIDATE_IDENTITIES_BY_TYPE["entity_group"],
        ),
    }
    matches = _collect_registered_matches(question, catalog, identity_limits=identity_limits)
    pools = {
        pool_key: deepcopy(matches.get(target_type, []))
        for target_type, pool_key in MATCH_POOL_KEYS.items()
    }
    ambiguity = _alias_ambiguity(matches)
    unsupported_signals = [term for term in UNSUPPORTED_LEXEMES if _contains(question, term)]
    operation_cues = _operation_cues(question, request)

    evaluations: list[dict[str, Any]] = []
    if not unsupported_signals:
        evaluations.extend(
            _evaluate_registered_functions(
                request,
                catalog,
                matches,
                prior_semantics=prior_semantics,
                prior_result=prior_result,
            )
        )
        evaluations.extend(
            _evaluate_registered_recipes(
                request,
                catalog,
                matches,
                operation_cues,
                prior_semantics=prior_semantics,
                prior_result=prior_result,
            )
        )
        if not evaluations:
            evaluations.extend(
                _evaluate_composition(
                    request,
                    catalog,
                    matches,
                    operation_cues,
                    prior_semantics=prior_semantics,
                    prior_result=prior_result,
                )
            )

    expanded: list[dict[str, Any]] = []
    for evaluation in evaluations:
        expanded.extend(_expand_ambiguous_semantics(evaluation, ambiguity))
    evaluations = _dedupe_evaluations(expanded or evaluations)

    complete = [item for item in evaluations if not item["unresolved_slots"]]
    if complete:
        highest_score = max(int(item["score"]) for item in complete)
        complete = [item for item in complete if int(item["score"]) == highest_score]
    complete = complete[:MAX_INTENT_CANDIDATES]
    intent_candidates = [_seal_candidate(item) for item in complete]

    if unsupported_signals or not intent_candidates:
        route_name = "unsupported"
        reason_code = "unsupported_registry_gap"
    elif len(intent_candidates) == 1:
        route_name = "deterministic"
        reason_code = "unique_complete_selection"
    else:
        route_name = "intent_llm"
        reason_code = "ambiguous_candidate_selection" if ambiguity else "semantic_choice_required"

    prompt_cards = [_prompt_card(item) for item in intent_candidates]
    material = {
        "request_id": request_id,
        **pools,
        "intent_candidates": intent_candidates,
        "prompt_cards": prompt_cards,
    }
    bundle_sha256 = sha256_json(material)
    selected_ids = [intent_candidates[0]["candidate_id"]] if route_name == "deterministic" else []
    required_slots = _stable(
        slot
        for candidate in intent_candidates
        for slot in candidate.get("required_slots") or []
    )
    unresolved_slots = (
        ["intent_candidate_id"]
        if route_name == "intent_llm"
        else (["registry_gap"] if route_name == "unsupported" else [])
    )
    ambiguity_sets = [item["identities"] for item in ambiguity]
    proof_material = _route_proof_material(
        bundle_sha256=bundle_sha256,
        route=route_name,
        reason_code=reason_code,
        candidate_ids=[item["candidate_id"] for item in intent_candidates],
        selected_candidate_ids=selected_ids,
        required_slots=required_slots,
        unresolved_slots=unresolved_slots,
        ambiguity_sets=ambiguity_sets,
        unsupported_signals=unsupported_signals,
    )
    route_decision = {
        "contract_version": ROUTE_VERSION,
        "route": route_name,
        "reason_code": reason_code,
        "resolved_candidate_bundle_sha256": bundle_sha256,
        "selected_candidate_ids": selected_ids,
        "required_slots": required_slots,
        "unresolved_slots": unresolved_slots,
        "ambiguity_sets": ambiguity_sets,
        "route_policy_version": ROUTE_POLICY_VERSION,
        "eligibility_proof_sha256": sha256_json(proof_material),
    }
    registry_gaps = _stable(
        gap
        for item in evaluations
        if item.get("unresolved_slots")
        for gap in item["unresolved_slots"]
    )
    route_evidence = {
        "ambiguity": ambiguity,
        "unsupported_signals": unsupported_signals,
        "registry_gaps": registry_gaps,
        "rejected_candidate_count": len(evaluations) - len(complete),
    }
    bundle = {
        "contract_version": BUNDLE_VERSION,
        **material,
        "bundle_sha256": bundle_sha256,
        "route_decision": route_decision,
        "route_evidence": route_evidence,
    }
    validate_generic_v2_candidate_bundle(bundle, catalog=catalog)
    return bounded(bundle, MAX_BUNDLE_BYTES, "generic_v2_candidate_bundle")


def validate_generic_v2_candidate_bundle(
    bundle: dict[str, Any],
    catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate the entire runtime shape, hashes, references, and route proof."""

    if not isinstance(bundle, dict) or set(bundle) != TOP_LEVEL_KEYS:
        _fail(
            "route_contract_error",
            "candidate_bundle_validation",
            "candidate bundle 최상위 필드가 닫힌 계약과 다릅니다.",
            {"actual_keys": sorted(bundle) if isinstance(bundle, dict) else []},
        )
    if bundle.get("contract_version") != BUNDLE_VERSION:
        _fail("route_contract_error", "candidate_bundle_validation", "candidate bundle 버전이 올바르지 않습니다.")
    if catalog is not None:
        _validate_catalog(catalog)

    for pool_key in MATCH_POOL_KEYS.values():
        pool = bundle.get(pool_key)
        if not isinstance(pool, list) or len(pool) > MAX_MATCHES_PER_TYPE:
            _fail("route_contract_error", "candidate_bundle_validation", "candidate match pool이 올바르지 않습니다.", {"pool": pool_key})
        for match in pool:
            _validate_match(match, catalog)

    candidates = bundle.get("intent_candidates")
    if not isinstance(candidates, list) or len(candidates) > MAX_INTENT_CANDIDATES:
        _fail("route_contract_error", "candidate_bundle_validation", "intent candidate 목록이 올바르지 않습니다.")
    candidate_ids: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, dict) or set(candidate) != INTENT_CANDIDATE_KEYS:
            _fail("route_contract_error", "candidate_bundle_validation", "intent candidate 필드가 닫힌 계약과 다릅니다.")
        candidate_id = str(candidate.get("candidate_id") or "")
        if not candidate_id or candidate_id in candidate_ids:
            _fail("route_contract_error", "candidate_bundle_validation", "intent candidate id가 없거나 중복됩니다.")
        candidate_ids.append(candidate_id)
        semantics = candidate.get("semantics")
        if not isinstance(semantics, dict) or candidate.get("semantics_sha256") != sha256_json(semantics):
            _fail("route_contract_error", "candidate_bundle_validation", "intent candidate semantics hash가 다릅니다.")
        if catalog is not None:
            _validate_semantic_references(semantics, catalog)
        required = candidate.get("required_slots")
        resolved = candidate.get("resolved_slots")
        if not isinstance(required, list) or not isinstance(resolved, list) or not set(required).issubset(set(resolved)):
            _fail("route_contract_error", "candidate_bundle_validation", "완료 candidate의 필수 slot이 해소되지 않았습니다.")

    cards = bundle.get("prompt_cards")
    if not isinstance(cards, list) or len(cards) != len(candidates):
        _fail("route_contract_error", "candidate_bundle_validation", "prompt card 수가 candidate와 다릅니다.")
    for card, candidate in zip(cards, candidates, strict=True):
        if not isinstance(card, dict) or set(card) != PROMPT_CARD_KEYS or card != _prompt_card(candidate):
            _fail("route_contract_error", "candidate_bundle_validation", "prompt card가 닫힌 candidate projection과 다릅니다.")

    material = _bundle_material(bundle)
    if bundle.get("bundle_sha256") != sha256_json(material):
        _fail("route_contract_error", "candidate_bundle_validation", "candidate bundle hash가 다릅니다.")

    route = bundle.get("route_decision")
    if not isinstance(route, dict) or set(route) != ROUTE_KEYS:
        _fail("route_contract_error", "candidate_bundle_validation", "route decision 필드가 닫힌 계약과 다릅니다.")
    if route.get("contract_version") != ROUTE_VERSION or route.get("route_policy_version") != ROUTE_POLICY_VERSION:
        _fail("route_contract_error", "candidate_bundle_validation", "route contract 버전이 올바르지 않습니다.")
    if route.get("resolved_candidate_bundle_sha256") != bundle.get("bundle_sha256"):
        _fail("route_contract_error", "candidate_bundle_validation", "route가 다른 candidate bundle을 참조합니다.")
    route_name = str(route.get("route") or "")
    selected_ids = list(route.get("selected_candidate_ids") or [])
    if route_name == "deterministic":
        if len(candidates) != 1 or selected_ids != candidate_ids or route.get("unresolved_slots"):
            _fail("route_contract_error", "candidate_bundle_validation", "deterministic route는 유일하고 완전한 candidate가 필요합니다.")
        if route.get("reason_code") != "unique_complete_selection":
            _fail("route_contract_error", "candidate_bundle_validation", "deterministic route reason이 올바르지 않습니다.")
    elif route_name == "intent_llm":
        if len(candidates) < 2 or selected_ids or route.get("unresolved_slots") != ["intent_candidate_id"]:
            _fail("route_contract_error", "candidate_bundle_validation", "intent_llm route는 둘 이상의 완전한 candidate만 허용합니다.")
    elif route_name == "unsupported":
        if candidates or selected_ids or route.get("reason_code") != "unsupported_registry_gap":
            _fail("route_contract_error", "candidate_bundle_validation", "unsupported route는 실행 candidate를 포함할 수 없습니다.")
    else:
        _fail("route_contract_error", "candidate_bundle_validation", "알 수 없는 route입니다.")

    route_evidence = bundle.get("route_evidence")
    if not isinstance(route_evidence, dict) or set(route_evidence) != {
        "ambiguity",
        "unsupported_signals",
        "registry_gaps",
        "rejected_candidate_count",
    }:
        _fail("route_contract_error", "candidate_bundle_validation", "route evidence 필드가 닫힌 계약과 다릅니다.")
    proof = _route_proof_material(
        bundle_sha256=str(bundle["bundle_sha256"]),
        route=route_name,
        reason_code=str(route.get("reason_code") or ""),
        candidate_ids=candidate_ids,
        selected_candidate_ids=selected_ids,
        required_slots=list(route.get("required_slots") or []),
        unresolved_slots=list(route.get("unresolved_slots") or []),
        ambiguity_sets=list(route.get("ambiguity_sets") or []),
        unsupported_signals=list(route_evidence.get("unsupported_signals") or []),
    )
    if route.get("eligibility_proof_sha256") != sha256_json(proof):
        _fail("route_contract_error", "candidate_bundle_validation", "route eligibility proof가 다릅니다.")
    return bundle


def normalize_generic_v2_intent(
    request: dict[str, Any],
    bundle: dict[str, Any],
    *,
    selected_candidate_id: str | None = None,
) -> dict[str, Any]:
    """Normalize a deterministic or model-selected closed candidate to intent."""

    validate_generic_v2_candidate_bundle(bundle)
    if str(request.get("request_id") or "") != str(bundle.get("request_id") or ""):
        _fail("intent_contract_error", "intent_normalization", "request와 candidate bundle identity가 다릅니다.")
    route = bundle["route_decision"]
    route_name = str(route["route"])
    candidates = bundle["intent_candidates"]
    if route_name == "unsupported":
        _fail(
            "unsupported_operation",
            "route_eligibility",
            "등록된 metadata와 typed operator로 처리할 수 없는 질문입니다.",
            {"reason_code": route.get("reason_code")},
        )
    if route_name == "deterministic":
        expected = str(candidates[0]["candidate_id"])
        if selected_candidate_id not in (None, "", expected):
            _fail("intent_contract_error", "intent_normalization", "deterministic candidate 선택값이 route proof와 다릅니다.")
        selected_candidate_id = expected
        generator = "deterministic"
    else:
        if not selected_candidate_id:
            _fail("intent_contract_error", "intent_normalization", "intent_llm candidate 선택값이 필요합니다.")
        generator = "llm"
    selected = next((item for item in candidates if item.get("candidate_id") == selected_candidate_id), None)
    if not isinstance(selected, dict):
        _fail(
            "intent_contract_error",
            "intent_decoding",
            "candidate 목록 밖의 값을 선택했습니다.",
            {"candidate_id": str(selected_candidate_id or "")},
        )
    material = {
        "contract_version": INTENT_VERSION,
        "request_id": request.get("request_id"),
        "candidate_bundle_sha256": bundle.get("bundle_sha256"),
        "intent_candidate_id": selected_candidate_id,
        "semantics": deepcopy(selected["semantics"]),
        "route": route_name,
        "intent_generator": generator,
    }
    return {**material, "intent_sha256": sha256_json(material)}


def build_generic_v2_intent_prompt(request: dict[str, Any], bundle: dict[str, Any]) -> str:
    """Return the bounded selection-only prompt for an ``intent_llm`` route."""

    validate_generic_v2_candidate_bundle(bundle)
    if bundle["route_decision"]["route"] != "intent_llm":
        _fail("intent_contract_error", "intent_prompt", "intent_llm route에서만 선택 prompt를 만들 수 있습니다.")
    payload = {
        "question": str(request.get("question") or ""),
        "candidates": bundle["prompt_cards"],
    }
    return (
        "질문과 의미가 같은 candidate_id 하나를 선택하세요. 후보의 의미를 수정하거나 새 필드, metric, dataset, 연산을 만들지 마세요. "
        "설명 없이 {\"intent_candidate_id\":\"...\"} JSON 한 개만 반환하세요.\n"
        + json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )


def resolve_generic_v2_intent(
    request: dict[str, Any],
    bundle: dict[str, Any],
    *,
    model: Any = None,
    llm_callable: Callable[[str], Any] | None = None,
    allow_syntax_retry: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Resolve the route, calling a model only to select a sealed candidate."""

    validate_generic_v2_candidate_bundle(bundle)
    route = bundle["route_decision"]
    route_name = str(route["route"])
    calls = 0
    selected_id: str | None = None
    if route_name == "deterministic":
        selected_id = str(bundle["intent_candidates"][0]["candidate_id"])
    elif route_name == "unsupported":
        normalize_generic_v2_intent(request, bundle)
    else:
        if llm_callable is None and model is None:
            _fail("intent_contract_error", "intent_llm", "Intent Language Model 연결이 필요합니다.")
        prompt = build_generic_v2_intent_prompt(request, bundle)

        def call(value: str) -> str:
            nonlocal calls
            calls += 1
            if llm_callable is not None:
                result = llm_callable(value)
            elif hasattr(model, "invoke"):
                result = model.invoke(value)
            elif callable(model):
                result = model(value)
            else:
                raise TypeError("model is not invokable")
            if isinstance(result, str):
                return result
            if hasattr(result, "text"):
                return str(result.text)
            if isinstance(result, dict):
                for key in ("text", "content", "message"):
                    if key in result:
                        return str(result[key])
            return str(result)

        try:
            selected_id = _parse_selection(call(prompt))
        except Exception as first:
            if not allow_syntax_retry:
                raise ContractError(
                    "intent_contract_error",
                    "intent_llm",
                    "Intent LLM 응답 JSON이 올바르지 않습니다.",
                ) from first
            try:
                selected_id = _parse_selection(
                    call(prompt + "\n이전 응답은 JSON 형식 오류였습니다. 정확한 JSON 한 개만 다시 반환하세요.")
                )
            except Exception as second:
                raise ContractError(
                    "intent_contract_error",
                    "intent_llm",
                    "Intent LLM 응답 JSON이 올바르지 않습니다.",
                ) from second
    intent = normalize_generic_v2_intent(request, bundle, selected_candidate_id=selected_id)
    telemetry = {
        "route": route_name,
        "reason_code": route.get("reason_code"),
        "intent_llm_calls": calls,
        "fallback_used": False,
        "eligibility_proof_sha256": route.get("eligibility_proof_sha256"),
    }
    return intent, telemetry


def _configured_candidate_limit(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = int(default)
    return max(MIN_CONFIGURED_CANDIDATE_IDENTITIES, min(parsed, MAX_CONFIGURED_CANDIDATE_IDENTITIES))


def _collect_registered_matches(
    question: str,
    catalog: dict[str, Any],
    *,
    identity_limits: Mapping[str, int] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    aliases: dict[tuple[str, str], list[dict[str, Any]]] = {}

    def register_values(target_type: str, target_key: str, values: Any, spec: Mapping[str, Any] | None = None) -> None:
        policy = spec or {}
        match_rule = str(policy.get("match") or "bounded_longest")
        conflict = str(policy.get("conflict") or "fail_ambiguous")
        for raw in values if isinstance(values, list) else [values]:
            if isinstance(raw, Mapping):
                texts = _strings(raw)
                priority = int(raw.get("priority") or 100)
            else:
                texts = _strings(raw)
                priority = 100
            for text in texts:
                if text:
                    aliases.setdefault((target_type, target_key), []).append(
                        {"text": text, "priority": priority, "match": match_rule, "conflict": conflict}
                    )

    for spec in (catalog.get("aliases") or {}).values():
        if not isinstance(spec, dict):
            continue
        target_type = str(spec.get("target_type") or "")
        target_key = str(spec.get("target_key") or "")
        if _registered(catalog, target_type, target_key):
            register_values(target_type, target_key, spec.get("values") or [], spec)
    for target_type, section in CATALOG_TARGET_SECTIONS.items():
        for key, spec in (catalog.get(section) or {}).items():
            if not isinstance(spec, dict):
                continue
            register_values(target_type, str(key), spec.get("aliases") or [])
            if target_type == "dataset":
                # Dataset identity, worker-facing label and registered use_when
                # phrases are authoritative retrieval evidence.  This mirrors
                # the v5 bounded table-candidate stage without fuzzy LLM search.
                register_values(
                    target_type,
                    str(key),
                    [
                        {"text": str(key), "priority": 120},
                        {"text": str(spec.get("display_name") or ""), "priority": 110},
                    ],
                )
                criteria = spec.get("selection_criteria") if isinstance(spec.get("selection_criteria"), dict) else {}
                register_values(
                    target_type,
                    str(key),
                    [
                        {"text": value, "priority": 100}
                        for value in criteria.get("use_when") or []
                        if str(value).strip()
                    ],
                )

    for card in catalog.get("specialized_functions") or []:
        if not isinstance(card, dict):
            continue
        identity = _function_identity(card)
        if identity:
            register_values("function", identity, card.get("aliases") or [])

    raw_result: dict[str, list[dict[str, Any]]] = {target_type: [] for target_type in MATCH_POOL_KEYS}
    seen: set[tuple[str, str, int, int]] = set()
    for (target_type, identity), values in aliases.items():
        values = sorted(values, key=lambda value: (-len(str(value["text"])), -int(value["priority"]), str(value["text"]).casefold()))
        for alias_contract in values:
            alias = str(alias_contract["text"])
            for start, end in _alias_spans(question, alias):
                marker = (target_type, identity, start, end)
                if marker in seen:
                    continue
                seen.add(marker)
                raw_result[target_type].append(
                    {
                        "candidate_id": f"match:{target_type}:{identity}:{start}:{end}",
                        "target_type": target_type,
                        "identity": identity,
                        "alias": alias,
                        "evidence": {"text": question[start:end], "start": start, "end": end},
                        # The public match contract remains the closed
                        # ``registered_alias`` discriminator.  Registry
                        # matching policy is compiler-private evidence and
                        # must never widen the exported candidate schema.
                        "match_rule": "registered_alias",
                        "_registry_match": str(alias_contract["match"]),
                        "_priority": int(alias_contract["priority"]),
                        "_conflict": str(alias_contract["conflict"]),
                    }
                )
    result: dict[str, list[dict[str, Any]]] = {target_type: [] for target_type in MATCH_POOL_KEYS}
    for target_type, values in raw_result.items():
        selected: list[dict[str, Any]] = []
        for candidate in values:
            start = int(candidate["evidence"]["start"])
            end = int(candidate["evidence"]["end"])
            length = end - start
            containing = [
                other
                for other in values
                if int(other["evidence"]["start"]) <= start
                and int(other["evidence"]["end"]) >= end
                and int(other["evidence"]["end"]) - int(other["evidence"]["start"]) > length
                and str(other.get("_registry_match") or "") == "bounded_longest"
            ]
            if containing:
                continue
            same_span = [
                other
                for other in values
                if int(other["evidence"]["start"]) == start and int(other["evidence"]["end"]) == end
            ]
            best_priority = max(int(other.get("_priority") or 0) for other in same_span)
            if int(candidate.get("_priority") or 0) < best_priority:
                continue
            clean = {key: deepcopy(value) for key, value in candidate.items() if not key.startswith("_")}
            selected.append(clean)
        selected.sort(key=lambda item: (int(item["evidence"]["start"]), -len(str(item["alias"])), str(item["identity"])))
        identity_limit = (identity_limits or DEFAULT_CANDIDATE_IDENTITIES_BY_TYPE).get(target_type)
        if identity_limit is not None:
            allowed_identities: list[str] = []
            bounded: list[dict[str, Any]] = []
            for candidate in selected:
                identity = str(candidate.get("identity") or "")
                if identity not in allowed_identities:
                    if len(allowed_identities) >= identity_limit:
                        continue
                    allowed_identities.append(identity)
                bounded.append(candidate)
            selected = bounded
        result[target_type] = selected[:MAX_MATCHES_PER_TYPE]
    return result


def _evaluate_registered_functions(
    request: dict[str, Any],
    catalog: dict[str, Any],
    matches: dict[str, list[dict[str, Any]]],
    *,
    prior_semantics: dict[str, Any] | None,
    prior_result: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Create candidates only from directly matched, pinned function cards."""

    date, date_explicit = _date_semantics(request)
    evaluations: list[dict[str, Any]] = []
    for function_ref in _matched_ids(matches, "function"):
        raw_card = _function_card(catalog, function_ref)
        card = validate_registered_function_card(raw_card)
        required_fields = _stable(card.get("required_fields") or [])
        output_fields = _stable((card.get("call_template") or {}).get("output_fields") or [])
        all_fields = _stable([*required_fields, *output_fields])
        missing = [field for field in all_fields if field not in (catalog.get("fields") or {})]
        dataset_ref = str((card.get("call_template") or {}).get("dataset_ref") or "")
        dataset = (catalog.get("datasets") or {}).get(dataset_ref)
        if not isinstance(dataset, dict):
            missing.append("function_dataset_ref")
            dataset_refs: list[str] = []
        else:
            dataset_refs = [dataset_ref]
            unavailable = [field for field in all_fields if field not in (dataset.get("fields") or {})]
            if unavailable:
                missing.extend(f"function_dataset_field:{field}" for field in unavailable)
        semantics = {
            "request_scope": _request_scope(request, set()),
            "analysis_kind": "registered_call",
            "metric_refs": [],
            "dimension_refs": [],
            "field_refs": output_fields,
            "dataset_refs": dataset_refs,
            "relation_refs": [],
            "recipe_refs": [],
            "function_refs": [function_ref],
            "formula_refs": [],
            "grain_refs": [],
            "entity_group_refs": [],
            "filter_refs": [],
            "thresholds": [],
            "date": date,
            "date_explicit": date_explicit,
            "reference_date": str(request.get("reference_instant") or "")[:10],
            "reference_instant": str(request.get("reference_instant") or ""),
            "rank": None,
            "tie_policy": "exact_n",
            "sort": None,
            "followup": bool(request.get("state_ref")),
            "followup_mode": "referenced" if request.get("state_ref") else "none",
        }
        semantics = _inherit_prior(semantics, prior_semantics, prior_result)
        evidence_refs = _stable(
            item.get("candidate_id")
            for item in matches.get("function", [])
            if item.get("identity") == function_ref
        )
        evaluations.append(
            {
                "description": f"registered function {function_ref}",
                "semantics": semantics,
                "required_slots": ["function_ref"],
                "resolved_slots": [] if missing else ["function_ref"],
                "unresolved_slots": _stable(missing),
                "evidence_refs": evidence_refs,
                "score": 200,
            }
        )
    return evaluations


def _evaluate_registered_recipes(
    request: dict[str, Any],
    catalog: dict[str, Any],
    matches: dict[str, list[dict[str, Any]]],
    cues: set[str],
    *,
    prior_semantics: dict[str, Any] | None,
    prior_result: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    recipe_match_ids = set(_matched_ids(matches, "recipe"))
    requested_metrics = _matched_ids(matches, "metric")
    requested_fields = _matched_ids(matches, "field")
    has_registered_evidence = any(matches.get(target_type) for target_type in MATCH_POOL_KEYS)
    evaluations: list[dict[str, Any]] = []
    for recipe_id, recipe in sorted((catalog.get("recipes") or {}).items()):
        if not isinstance(recipe, dict):
            continue
        template = recipe.get("default_operation_template") if isinstance(recipe.get("default_operation_template"), dict) else {}
        template_ops = _template_ops(template)
        if not template_ops or not template_ops.issubset(ALLOWED_TEMPLATE_OPERATIONS):
            continue
        template_metrics = _template_values(template, {"metric", "metrics", "left_metric", "right_metric", "numerator_metric", "denominator_metric"})
        template_fields = _template_values(template, {"group_by", "allowed_fields", "left_field", "right_field", "stable_tie_break"})
        root_op = str(template.get("op") or "")
        cue_score = _operation_alignment_score(cues, template_ops, root_op)
        metric_overlap = len(set(requested_metrics) & set(template_metrics))
        field_overlap = len(set(requested_fields) & set(template_fields))
        alias_match = str(recipe_id) in recipe_match_ids
        if not alias_match and not has_registered_evidence:
            continue
        if not alias_match and cue_score <= 0:
            continue
        if not alias_match and requested_metrics and template_metrics and not metric_overlap:
            continue
        if root_op == "project" and not requested_fields and not _template_values(template, {"fields"}):
            continue
        score = (100 if alias_match else 0) + cue_score + 12 * metric_overlap + 6 * field_overlap
        semantics, unresolved, resolved = _semantics_for_recipe(
            request,
            catalog,
            matches,
            cues,
            str(recipe_id),
            recipe,
            prior_semantics=prior_semantics,
            prior_result=prior_result,
        )
        required = _stable(recipe.get("required_slots") or [])
        evidence_refs = [
            item["candidate_id"]
            for target_type in MATCH_POOL_KEYS
            for item in matches.get(target_type, [])
            if item["identity"] in set(_semantic_refs(semantics, target_type))
        ]
        evaluations.append(
            {
                "description": str(recipe.get("display_name") or recipe_id),
                "semantics": semantics,
                "required_slots": required,
                "resolved_slots": resolved,
                "unresolved_slots": unresolved,
                "evidence_refs": _stable(evidence_refs),
                "score": score,
            }
        )
    return evaluations


def _evaluate_composition(
    request: dict[str, Any],
    catalog: dict[str, Any],
    matches: dict[str, list[dict[str, Any]]],
    cues: set[str],
    *,
    prior_semantics: dict[str, Any] | None,
    prior_result: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    metrics = _root_metric_refs(
        catalog,
        _matched_ids(matches, "metric"),
        request=request,
        matches=matches,
    )
    raw_fields = _matched_ids(matches, "field")
    fields = _visible_field_refs(request, catalog, matches)
    datasets = _matched_ids(matches, "dataset")
    if not metrics and datasets and _question_implies_metric(str(request.get("question") or "")):
        metrics = _root_metric_refs(
            catalog,
            _unique_metrics_for_datasets(catalog, datasets),
            request=request,
            matches=matches,
        )
    grains = _matched_ids(matches, "grain")
    relations = _matched_ids(matches, "relation")
    entity_groups = _matched_ids(matches, "entity_group")
    filter_refs, thresholds, filter_gaps = _registered_filter_literals(request, catalog, matches)
    scalar_comparison = any(
        isinstance(item, dict) and str(item.get("operator") or "") in {"gt", "gte", "lt", "lte"}
        for item in filter_refs
    )
    rank = _rank_semantics(request)
    if rank:
        analysis_kind = "rank"
    elif "project" in cues:
        analysis_kind = "projection"
    elif "compare_fields" in cues and len(metrics) >= 2:
        analysis_kind = "compare_fields"
    elif scalar_comparison and fields and "detail" in cues:
        analysis_kind = "detail"
    elif "join" in cues:
        analysis_kind = "join"
    elif metrics:
        analysis_kind = "aggregate"
    elif fields:
        analysis_kind = "detail"
    else:
        return []

    # A detail/projection request may mention a source-bound metric as a raw
    # column.  It must not silently become an aggregation merely because the
    # canonical field and metric share an ID.
    if analysis_kind in {"projection", "detail"}:
        metrics = []
    dimensions = _dimension_refs(catalog, fields, grains, analysis_kind)
    formula_refs = [metric for metric in metrics if isinstance((catalog.get("metrics") or {}).get(metric, {}).get("formula"), dict)]
    metric_sources, metric_gaps = _metric_source_datasets(
        catalog,
        metrics,
        request=request,
        explicit_datasets=datasets,
    )
    dataset_refs = _stable([*datasets, *metric_sources])
    # Operational filter/qualifier fields still participate in source closure
    # even when they are intentionally absent from the visible result columns.
    field_sources, field_gaps = _field_source_datasets(catalog, raw_fields, dataset_refs)
    dataset_refs = _stable([*dataset_refs, *field_sources])
    relation_refs, relation_gaps = _relation_path_refs(catalog, dataset_refs, relations)
    date, date_explicit = _date_semantics(request)
    semantics = {
        "request_scope": _request_scope(request, cues),
        "analysis_kind": analysis_kind,
        "metric_refs": metrics,
        "dimension_refs": dimensions,
        "field_refs": fields,
        "dataset_refs": dataset_refs,
        "relation_refs": relation_refs,
        "recipe_refs": [],
        "function_refs": [],
        "formula_refs": formula_refs,
        "grain_refs": grains,
        "entity_group_refs": entity_groups,
        "filter_refs": filter_refs,
        "thresholds": thresholds,
        "date": date,
        "date_explicit": date_explicit,
        "reference_date": str(request.get("reference_instant") or "")[:10],
        "reference_instant": str(request.get("reference_instant") or ""),
        "rank": rank,
        "tie_policy": _tie_policy(str(request.get("question") or ""), rank),
        "sort": _sort_semantics(str(request.get("question") or ""), metrics),
        "followup": bool(request.get("state_ref")),
        "followup_mode": "referenced" if _request_scope(request, cues) != "new_analysis" else "none",
    }
    if analysis_kind == "compare_fields":
        comparison_operator = _comparison_operator(str(request.get("question") or ""))
        if comparison_operator:
            semantics["comparison_operator"] = comparison_operator
    semantics = _inherit_prior(semantics, prior_semantics, prior_result)
    unresolved = [*metric_gaps, *field_gaps, *relation_gaps, *filter_gaps]
    if analysis_kind in {"aggregate", "rank", "compare_fields"} and not metrics:
        unresolved.append("metric_ref")
    if analysis_kind == "rank" and not rank:
        unresolved.extend(["rank_direction", "rank_limit"])
    if analysis_kind == "rank" and not dimensions:
        unresolved.append("grain_ref")
    if analysis_kind in {"projection", "detail"} and not fields:
        unresolved.append("project_fields")
    if analysis_kind == "join" and not relation_refs:
        unresolved.append("relation_ref")
    required: list[str] = []
    if analysis_kind in {"aggregate", "rank", "compare_fields"}:
        required.append("metric_ref")
    if analysis_kind == "rank":
        required.extend(["rank_direction", "rank_limit", "grain_ref"])
    if analysis_kind in {"projection", "detail"}:
        required.append("project_fields")
    if analysis_kind == "join":
        required.append("relation_ref")
    required = _stable(required)
    resolved = [slot for slot in required if slot not in set(unresolved)]
    return [
        {
            "description": f"registered {analysis_kind}",
            "semantics": semantics,
            "required_slots": required,
            "resolved_slots": resolved,
            "unresolved_slots": _stable(unresolved),
            "evidence_refs": _stable(item["candidate_id"] for values in matches.values() for item in values),
            "score": 10 + 5 * len(metrics) + 2 * len(fields),
        }
    ]


def _semantics_for_recipe(
    request: dict[str, Any],
    catalog: dict[str, Any],
    matches: dict[str, list[dict[str, Any]]],
    cues: set[str],
    recipe_id: str,
    recipe: dict[str, Any],
    *,
    prior_semantics: dict[str, Any] | None,
    prior_result: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[str], list[str]]:
    template = deepcopy(recipe.get("default_operation_template") or {})
    ops = _template_ops(template)
    requested_metrics = _matched_ids(matches, "metric")
    template_metrics = _template_values(template, {"metric", "metrics", "left_metric", "right_metric", "numerator_metric", "denominator_metric"})
    metric_refs = _root_metric_refs(
        catalog,
        _stable(requested_metrics or template_metrics),
        request=request,
        matches=matches,
    )
    raw_fields = _matched_ids(matches, "field")
    requested_fields = _visible_field_refs(request, catalog, matches)
    allowed_fields = _template_values(template, {"allowed_fields"})
    default_fields = _template_values(template, {"fields"})
    if str(template.get("op") or "") == "project":
        field_refs = [field for field in requested_fields if field in set(allowed_fields)]
        if not field_refs and default_fields:
            field_refs = [field for field in default_fields if field in (catalog.get("fields") or {})]
    else:
        field_refs = requested_fields
    grain_ids = _matched_ids(matches, "grain")
    template_grain = str(template.get("grain_id") or "")
    if template_grain and template_grain in (catalog.get("grains") or {}) and template_grain not in grain_ids:
        grain_ids.append(template_grain)
    dimensions = _dimension_refs(catalog, field_refs, grain_ids, _dominant_operation(ops, cues))
    template_groups = _template_values(template, {"group_by"})
    if template_groups and not dimensions:
        dimensions = [field for field in template_groups if field in (catalog.get("fields") or {})]
    analysis_kind = _dominant_operation(ops, cues)
    if analysis_kind in {"projection", "detail"}:
        metric_refs = []
    formula_refs = [metric for metric in metric_refs if isinstance((catalog.get("metrics") or {}).get(metric, {}).get("formula"), dict)]
    relation_refs = _template_values(template, {"relation_id"})
    relation_refs = [relation for relation in relation_refs if relation in (catalog.get("relations") or {})]
    dataset_refs = _stable(
        [
            *_matched_ids(matches, "dataset"),
            *_template_values(template, {"dataset_key", "dataset_keys"}),
        ]
    )
    dataset_refs = [item for item in dataset_refs if item in (catalog.get("datasets") or {})]
    metric_sources, metric_gaps = _metric_source_datasets(
        catalog,
        metric_refs,
        request=request,
        explicit_datasets=_matched_ids(matches, "dataset"),
    )
    dataset_refs = _stable([*dataset_refs, *metric_sources])
    field_sources, field_gaps = _field_source_datasets(catalog, raw_fields, dataset_refs)
    dataset_refs = _stable([*dataset_refs, *field_sources])
    for relation_id in relation_refs:
        relation = catalog["relations"][relation_id]
        dataset_refs = _stable([*dataset_refs, relation.get("left_dataset"), relation.get("right_dataset")])
    path_relations, relation_gaps = _relation_path_refs(catalog, dataset_refs, relation_refs)
    relation_refs = _stable([*relation_refs, *path_relations])
    filter_refs, thresholds, filter_gaps = _registered_filter_literals(request, catalog, matches)
    rank = _rank_semantics(request)
    date, date_explicit = _date_semantics(request)
    semantics = {
        "request_scope": _request_scope(request, cues),
        "analysis_kind": analysis_kind,
        "metric_refs": metric_refs,
        "dimension_refs": dimensions,
        "field_refs": field_refs,
        "dataset_refs": dataset_refs,
        "relation_refs": relation_refs,
        "recipe_refs": [recipe_id],
        "function_refs": [],
        "formula_refs": formula_refs,
        "grain_refs": grain_ids,
        "entity_group_refs": _matched_ids(matches, "entity_group"),
        "filter_refs": filter_refs,
        "thresholds": thresholds,
        "date": date,
        "date_explicit": date_explicit,
        "reference_date": str(request.get("reference_instant") or "")[:10],
        "reference_instant": str(request.get("reference_instant") or ""),
        "rank": rank,
        "tie_policy": _tie_policy(str(request.get("question") or ""), rank),
        "sort": _sort_semantics(str(request.get("question") or ""), metric_refs),
        "followup": bool(request.get("state_ref")),
        "followup_mode": "referenced" if _request_scope(request, cues) != "new_analysis" else "none",
    }
    if analysis_kind == "compare_fields":
        comparison_operator = _comparison_operator(str(request.get("question") or ""))
        if comparison_operator:
            semantics["comparison_operator"] = comparison_operator
    semantics = _inherit_prior(semantics, prior_semantics, prior_result)
    required = _stable(recipe.get("required_slots") or [])
    resolved: list[str] = []
    unresolved: list[str] = [*metric_gaps, *field_gaps, *relation_gaps, *filter_gaps]
    for slot in required:
        if slot == "date_scope" and date:
            resolved.append(slot)
        elif slot == "rank_direction" and rank and rank.get("mode") in {"top", "bottom"}:
            resolved.append(slot)
        elif slot == "rank_limit" and rank and int(rank.get("limit") or 0) > 0:
            resolved.append(slot)
        elif slot == "project_fields" and field_refs:
            resolved.append(slot)
        elif slot in semantics and semantics.get(slot) not in (None, "", [], {}):
            resolved.append(slot)
        else:
            unresolved.append(slot)
    if "rank" in ops:
        if not metric_refs:
            unresolved.append("metric_ref")
        if not dimensions:
            unresolved.append("grain_ref")
        if not rank:
            unresolved.extend(["rank_direction", "rank_limit"])
    if "project" in ops and str(template.get("op") or "") == "project" and not field_refs:
        unresolved.append("project_fields")
    if "join" in ops and not relation_refs:
        unresolved.append("relation_ref")
    return semantics, _stable(unresolved), _stable(resolved)


def _expand_ambiguous_semantics(evaluation: dict[str, Any], ambiguity: list[dict[str, Any]]) -> list[dict[str, Any]]:
    relevant: list[tuple[str, list[str]]] = []
    semantics = evaluation.get("semantics") or {}
    for item in ambiguity:
        ref_key = {
            "metric": "metric_refs",
            "field": "field_refs",
            "dataset": "dataset_refs",
            "recipe": "recipe_refs",
            "grain": "grain_refs",
            "relation": "relation_refs",
            "entity_group": "entity_group_refs",
            "function": "function_refs",
        }.get(str(item.get("target_type") or ""))
        identities = list(item.get("identities") or [])
        if ref_key and len(set(identities) & set(semantics.get(ref_key) or [])) > 1:
            relevant.append((ref_key, identities))
    if not relevant:
        return [evaluation]
    variants: list[dict[str, Any]] = []
    choices = [identities for _ref_key, identities in relevant]
    for selected_values in product(*choices):
        if len(variants) >= MAX_AMBIGUITY_VARIANTS:
            break
        variant = deepcopy(evaluation)
        for (ref_key, identities), selected in zip(relevant, selected_values, strict=True):
            current = [item for item in variant["semantics"].get(ref_key) or [] if item not in identities]
            variant["semantics"][ref_key] = _stable([*current, selected])
        variant["score"] = int(variant["score"])
        variants.append(variant)
    return variants


def _seal_candidate(evaluation: dict[str, Any]) -> dict[str, Any]:
    semantics = deepcopy(evaluation["semantics"])
    semantics_sha = sha256_json(semantics)
    recipe_part = "+".join(
        semantics.get("recipe_refs")
        or semantics.get("function_refs")
        or [semantics.get("analysis_kind") or "registered"]
    )
    candidate_id = f"intent:{recipe_part}:{semantics_sha[:16]}"
    return {
        "candidate_id": candidate_id,
        "description": str(evaluation.get("description") or semantics.get("analysis_kind") or "registered intent"),
        "semantics": semantics,
        "semantics_sha256": semantics_sha,
        "required_slots": _stable(evaluation.get("required_slots") or []),
        "resolved_slots": _stable(evaluation.get("resolved_slots") or []),
        "evidence_refs": _stable(evaluation.get("evidence_refs") or []),
    }


def _prompt_card(candidate: dict[str, Any]) -> dict[str, Any]:
    semantics = candidate.get("semantics") or {}
    return {
        "candidate_id": candidate.get("candidate_id"),
        "description": candidate.get("description"),
        "analysis_kind": semantics.get("analysis_kind"),
        "metric_refs": list(semantics.get("metric_refs") or []),
        "dimension_refs": list(semantics.get("dimension_refs") or []),
        "recipe_refs": list(semantics.get("recipe_refs") or []),
        "function_refs": list(semantics.get("function_refs") or []),
        "unresolved_slots": [],
    }


def _bundle_material(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": bundle.get("request_id"),
        **{pool_key: bundle.get(pool_key) for pool_key in MATCH_POOL_KEYS.values()},
        "intent_candidates": bundle.get("intent_candidates"),
        "prompt_cards": bundle.get("prompt_cards"),
    }


def _route_proof_material(
    *,
    bundle_sha256: str,
    route: str,
    reason_code: str,
    candidate_ids: list[str],
    selected_candidate_ids: list[str],
    required_slots: list[str],
    unresolved_slots: list[str],
    ambiguity_sets: list[list[str]],
    unsupported_signals: list[str],
) -> dict[str, Any]:
    return {
        "route_policy_version": ROUTE_POLICY_VERSION,
        "bundle_sha256": bundle_sha256,
        "route": route,
        "reason_code": reason_code,
        "candidate_ids": candidate_ids,
        "selected_candidate_ids": selected_candidate_ids,
        "required_slots": required_slots,
        "unresolved_slots": unresolved_slots,
        "ambiguity_sets": ambiguity_sets,
        "unsupported_signals": unsupported_signals,
    }


def _validate_catalog(catalog: dict[str, Any]) -> None:
    if not isinstance(catalog, dict) or catalog.get("contract_version") != CATALOG_VERSION:
        _fail("metadata_dependency_error", "candidate_routing", "metadata.runtime.catalog.v2가 필요합니다.")
    actual_hash = str(catalog.get("catalog_sha256") or "")
    expected_hash = sha256_json({key: value for key, value in catalog.items() if key != "catalog_sha256"})
    if actual_hash and actual_hash != expected_hash:
        _fail(
            "metadata_dependency_error",
            "candidate_routing",
            "runtime catalog hash가 다릅니다.",
            {"expected": expected_hash, "actual": actual_hash},
        )
    for section in CATALOG_TARGET_SECTIONS.values():
        if not isinstance(catalog.get(section), dict):
            _fail("metadata_dependency_error", "candidate_routing", "runtime catalog registry가 올바르지 않습니다.", {"section": section})


    if not isinstance(catalog.get("specialized_functions"), list):
        _fail(
            "metadata_dependency_error",
            "candidate_routing",
            "runtime catalog specialized function registry must be an array.",
        )


def _validate_match(match: Any, catalog: dict[str, Any] | None) -> None:
    keys = {"candidate_id", "target_type", "identity", "alias", "evidence", "match_rule"}
    if not isinstance(match, dict) or set(match) != keys or match.get("match_rule") != "registered_alias":
        _fail("route_contract_error", "candidate_bundle_validation", "alias match candidate가 올바르지 않습니다.")
    evidence = match.get("evidence")
    if not isinstance(evidence, dict) or set(evidence) != {"text", "start", "end"}:
        _fail("route_contract_error", "candidate_bundle_validation", "alias evidence가 올바르지 않습니다.")
    if catalog is not None and not _registered(catalog, str(match.get("target_type") or ""), str(match.get("identity") or "")):
        _fail("metadata_dependency_error", "candidate_bundle_validation", "미등록 alias target입니다.")


def _validate_semantic_references(semantics: dict[str, Any], catalog: dict[str, Any]) -> None:
    for target_type, key in (
        ("metric", "metric_refs"),
        ("field", "field_refs"),
        ("field", "dimension_refs"),
        ("dataset", "dataset_refs"),
        ("relation", "relation_refs"),
        ("recipe", "recipe_refs"),
        ("grain", "grain_refs"),
        ("entity_group", "entity_group_refs"),
        ("metric", "formula_refs"),
        ("function", "function_refs"),
    ):
        for identity in semantics.get(key) or []:
            if not _registered(catalog, target_type, str(identity)):
                _fail(
                    "metadata_dependency_error",
                    "candidate_bundle_validation",
                    "intent semantics가 미등록 metadata를 참조합니다.",
                    {"target_type": target_type, "identity": identity},
                )
    for item in semantics.get("filter_refs") or []:
        if not isinstance(item, dict) or not _registered(catalog, "field", str(item.get("field") or "")):
            _fail(
                "metadata_dependency_error",
                "candidate_bundle_validation",
                "filter literal이 미등록 field를 참조합니다.",
            )


def _operation_cues(question: str, request: dict[str, Any]) -> set[str]:
    result = {
        operation
        for operation, lexemes in OPERATION_LEXEMES.items()
        if any(_contains(question, lexeme) for lexeme in lexemes)
    }
    if _rank_semantics(request):
        result.add("rank")
    return result


def _comparison_operator(question: str) -> str:
    """Return a typed predicate only for explicit directional wording."""

    normalized = normalize_text(question)
    for operator, lexemes in (
        ("gte", ("보다 크거나 같은", "이상", "at least", "greater than or equal")),
        ("lte", ("보다 작거나 같은", "이하", "at most", "less than or equal")),
        ("gt", ("보다 큰", "초과", "greater than", "above")),
        ("lt", ("보다 작은", "미만", "less than", "below")),
    ):
        if any(_contains(normalized, lexeme) for lexeme in lexemes):
            return operator
    return ""


def _operation_alignment_score(cues: set[str], template_ops: set[str], root_op: str) -> int:
    score = 0
    structural_cues = cues - {"detail"}
    for cue in cues:
        if cue in template_ops:
            score += 30 if cue == root_op else 20
        elif cue == "detail" and root_op == "project" and not structural_cues:
            score += 5
    if "rank" in cues and "rank" not in template_ops:
        score -= 50
    if "project" in cues and root_op == "project":
        score += 20
    if "join" in cues and "join" in template_ops:
        score += 20
    return score


def _dominant_operation(ops: set[str], cues: set[str]) -> str:
    for operation, analysis_kind in (
        ("rank", "rank"),
        ("compare_fields", "compare_fields"),
        ("project", "projection"),
        ("join", "join"),
        ("aggregate", "aggregate"),
        ("sort", "sort"),
        ("filter", "detail"),
    ):
        if operation in cues and operation in ops:
            return analysis_kind
    for operation, analysis_kind in (
        ("rank", "rank"),
        ("join", "join"),
        ("aggregate", "aggregate"),
        ("project", "projection"),
        ("sort", "sort"),
        ("filter", "detail"),
    ):
        if operation in ops:
            return analysis_kind
    return "detail"


def _template_ops(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        if isinstance(value.get("op"), str):
            result.add(str(value["op"]))
        for item in value.values():
            result.update(_template_ops(item))
    elif isinstance(value, list):
        for item in value:
            result.update(_template_ops(item))
    return result


def _template_values(value: Any, keys: set[str]) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys:
                if isinstance(item, list):
                    result.extend(_strings(item))
                elif isinstance(item, str):
                    result.append(item)
            result.extend(_template_values(item, keys))
    elif isinstance(value, list):
        for item in value:
            result.extend(_template_values(item, keys))
    return _stable(result)


def _metric_source_datasets(
    catalog: dict[str, Any],
    metric_refs: Iterable[str],
    *,
    request: dict[str, Any] | None = None,
    explicit_datasets: Iterable[str] = (),
) -> tuple[list[str], list[str]]:
    datasets: list[str] = []
    gaps: list[str] = []
    seen: set[str] = set()

    def visit(metric_id: str) -> None:
        if metric_id in seen:
            return
        seen.add(metric_id)
        metric = (catalog.get("metrics") or {}).get(metric_id)
        if not isinstance(metric, dict):
            gaps.append(f"metric:{metric_id}")
            return
        formula = metric.get("formula") if isinstance(metric.get("formula"), dict) else {}
        dependencies = _formula_metric_refs(formula)
        if dependencies:
            for dependency in dependencies:
                visit(dependency)
            return
        binding = metric.get("source_binding") if isinstance(metric.get("source_binding"), dict) else {}
        family = str(binding.get("dataset_family") or "")
        matches = [
            str(key)
            for key, dataset in (catalog.get("datasets") or {}).items()
            if isinstance(dataset, dict) and str(dataset.get("family") or "") == family
        ]
        selected = _select_time_scoped_dataset(
            catalog,
            matches,
            request or {},
            explicit_datasets=explicit_datasets,
        )
        if selected:
            datasets.append(selected)
        else:
            gaps.append(f"metric_source:{metric_id}")

    for metric_ref in metric_refs:
        visit(str(metric_ref))
    return _stable(datasets), _stable(gaps)


def _unique_metrics_for_datasets(catalog: dict[str, Any], dataset_refs: Iterable[str]) -> list[str]:
    """Return a metric only when selected dataset families make it unambiguous."""

    families = {
        str(((catalog.get("datasets") or {}).get(dataset_ref) or {}).get("family") or "")
        for dataset_ref in dataset_refs
    }
    families.discard("")
    metrics = [
        str(metric_id)
        for metric_id, metric in (catalog.get("metrics") or {}).items()
        if isinstance(metric, dict)
        and str((metric.get("source_binding") or {}).get("dataset_family") or "") in families
    ]
    return _stable(metrics) if len(set(metrics)) == 1 else []


def _question_implies_metric(question: str) -> bool:
    return any(
        _contains(question, cue)
        for cue in (
            "실적", "수량", "합계", "총량", "평균", "비율",
            "actual", "amount", "quantity", "total", "average", "rate",
        )
    )


def _formula_metric_refs(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key.endswith("_metric") and isinstance(item, str):
                result.append(item)
            else:
                result.extend(_formula_metric_refs(item))
    elif isinstance(value, list):
        for item in value:
            result.extend(_formula_metric_refs(item))
    return _stable(result)


def _select_time_scoped_dataset(
    catalog: dict[str, Any],
    matches: list[str],
    request: dict[str, Any],
    *,
    explicit_datasets: Iterable[str] = (),
) -> str:
    if len(matches) == 1:
        return matches[0]
    if not matches or not request:
        return ""
    explicit = [dataset for dataset in _stable(explicit_datasets) if dataset in matches]
    if len(explicit) == 1:
        return explicit[0]
    if len(explicit) > 1:
        return ""
    question = str(request.get("question") or "")
    datasets = catalog.get("datasets") or {}
    criteria_matches = []
    for dataset_key in matches:
        criteria = (datasets.get(dataset_key) or {}).get("selection_criteria") or {}
        if not isinstance(criteria, dict):
            continue
        use_when = [str(value) for value in criteria.get("use_when") or [] if str(value)]
        exclude_when = [str(value) for value in criteria.get("exclude_when") or [] if str(value)]
        if (
            use_when
            and any(_selection_cue_matches(question, cue) for cue in use_when)
            and not any(_selection_cue_matches(question, cue) for cue in exclude_when)
        ):
            criteria_matches.append(dataset_key)
    if len(criteria_matches) == 1:
        return criteria_matches[0]
    if len(criteria_matches) > 1:
        return ""
    day_cues = ("오늘", "금일", "당일", "today", "current day")
    current_cues = ("현재", "현시간", "실시간", "현황", "current", "real-time", "realtime")
    if any(_contains(question, cue) for cue in day_cues):
        preferred = [
            dataset_key
            for dataset_key in matches
            if _dataset_time_scope(dataset_key, datasets.get(dataset_key) or {})
            in {"current_day", "today"}
        ]
        return preferred[0] if len(preferred) == 1 else ""
    if any(_contains(question, cue) for cue in current_cues):
        preferred = [
            dataset_key
            for dataset_key in matches
            if _dataset_time_scope(dataset_key, datasets.get(dataset_key) or {})
            in {"current", "current_day", "today"}
        ]
        return preferred[0] if len(preferred) == 1 else ""
    requested_date, _explicit = _date_semantics(request)
    reference_date = str(request.get("reference_instant") or "")[:10]
    date_values = _typed_values(request, "date")
    historical_date = bool(
        date_values and requested_date and reference_date and requested_date < reference_date
    )
    if not historical_date:
        return ""
    preferred = [
        dataset_key
        for dataset_key in matches
        if _dataset_time_scope(dataset_key, datasets.get(dataset_key) or {})
        in {"history", "historical", "past"}
    ]
    return preferred[0] if len(preferred) == 1 else ""


def _selection_cue_matches(question: str, cue: str) -> bool:
    """Match a registered phrase even when a qualifier appears between its words."""

    if _contains(question, cue):
        return True
    parts = re.findall(r"[0-9A-Za-z가-힣]+", normalize_text(cue))
    return len(parts) > 1 and all(_contains(question, part) for part in parts)


def _dataset_time_scope(dataset_key: str, dataset: Mapping[str, Any]) -> str:
    criteria = dataset.get("selection_criteria") if isinstance(dataset.get("selection_criteria"), Mapping) else {}
    scope = str(criteria.get("time_scope") or dataset.get("time_scope") or "").casefold()
    if scope and scope != "unspecified":
        return scope
    identity = " ".join((str(dataset_key), str(dataset.get("display_name") or ""))).casefold()
    if any(token in identity for token in ("today", "current", "오늘", "당일", "현재")):
        return "current_day"
    if any(token in identity for token in ("history", "historical", "past", "이력", "과거")):
        return "history"
    return scope


def _field_source_datasets(
    catalog: dict[str, Any],
    fields: Iterable[str],
    preferred: Iterable[str],
) -> tuple[list[str], list[str]]:
    preferred_list = _stable(preferred)
    selected: list[str] = []
    gaps: list[str] = []
    for field in fields:
        owners = _strings(((catalog.get("fields") or {}).get(field) or {}).get("dataset_keys") or [])
        preferred_owners = [owner for owner in owners if owner in preferred_list]
        if len(preferred_owners) == 1:
            selected.append(preferred_owners[0])
        elif len(owners) == 1:
            selected.append(owners[0])
        elif len(preferred_owners) > 1:
            continue
        elif owners:
            gaps.append(f"field_owner:{field}")
        else:
            gaps.append(f"field_owner:{field}")
    return _stable(selected), _stable(gaps)


def _relation_path_refs(
    catalog: dict[str, Any],
    datasets: Iterable[str],
    explicit_relations: Iterable[str],
) -> tuple[list[str], list[str]]:
    selected = _stable(explicit_relations)
    covered: set[str] = set()
    for relation_id in selected:
        relation = (catalog.get("relations") or {}).get(relation_id) or {}
        covered.update(_strings([relation.get("left_dataset"), relation.get("right_dataset")]))
    targets = _stable(datasets)
    if len(targets) <= 1:
        return selected, []
    connected = set(covered or targets[:1])
    remaining = [item for item in targets if item not in connected]
    gaps: list[str] = []
    while remaining:
        target = remaining.pop(0)
        paths = _shortest_relation_paths(catalog, connected, target)
        if len(paths) != 1:
            gaps.append(f"relation_path:{target}")
            continue
        for relation_id in paths[0]:
            if relation_id not in selected:
                selected.append(relation_id)
            relation = catalog["relations"][relation_id]
            connected.update(_strings([relation.get("left_dataset"), relation.get("right_dataset")]))
        remaining = [item for item in remaining if item not in connected]
    return selected, gaps


def _shortest_relation_paths(catalog: dict[str, Any], starts: set[str], target: str) -> list[list[str]]:
    if target in starts:
        return [[]]
    adjacency: dict[str, list[tuple[str, str]]] = {}
    for relation_id, relation in (catalog.get("relations") or {}).items():
        if not isinstance(relation, dict):
            continue
        left = str(relation.get("left_dataset") or "")
        right = str(relation.get("right_dataset") or "")
        if left and right:
            adjacency.setdefault(left, []).append((right, str(relation_id)))
            adjacency.setdefault(right, []).append((left, str(relation_id)))
    queue: list[tuple[str, list[str], set[str]]] = [(start, [], {start}) for start in sorted(starts)]
    solutions: list[list[str]] = []
    best_length: int | None = None
    while queue:
        node, path, visited = queue.pop(0)
        if best_length is not None and len(path) >= best_length:
            continue
        for neighbor, relation_id in sorted(adjacency.get(node, [])):
            if neighbor in visited:
                continue
            next_path = [*path, relation_id]
            if neighbor == target:
                best_length = len(next_path) if best_length is None else best_length
                if len(next_path) == best_length and next_path not in solutions:
                    solutions.append(next_path)
            else:
                queue.append((neighbor, next_path, {*visited, neighbor}))
    return solutions[:2]


def _dimension_refs(catalog: dict[str, Any], fields: list[str], grain_ids: list[str], analysis_kind: str) -> list[str]:
    result: list[str] = []
    for grain_id in grain_ids:
        grain = (catalog.get("grains") or {}).get(grain_id) or {}
        result.extend(field for field in _strings(grain.get("keys") or []) if field in (catalog.get("fields") or {}))
    group_fields = [
        field
        for field in fields
        if "group" in _strings(((catalog.get("fields") or {}).get(field) or {}).get("roles") or [])
    ]
    if analysis_kind in {"rank", "aggregate", "join", "compare_fields"}:
        result.extend(group_fields)
    if analysis_kind == "rank" and not result:
        matching_grains = [
            grain
            for grain in (catalog.get("grains") or {}).values()
            if isinstance(grain, dict) and set(_strings(grain.get("keys") or [])) & set(fields)
        ]
        if len(matching_grains) == 1:
            result.extend(_strings(matching_grains[0].get("keys") or []))
    if analysis_kind == "rank" and not result:
        # A directly mentioned registered field is a complete rank grain even
        # when the worker did not register a separate grain card.  Temporal
        # qualifiers and metric-valued fields are never promoted.
        for field in fields:
            card = (catalog.get("fields") or {}).get(field) or {}
            semantic_type = str(card.get("semantic_type") or "").casefold()
            roles = set(_strings(card.get("roles") or []))
            if semantic_type in {"date", "localdate", "datetime", "timestamp", "instant"}:
                continue
            if roles.intersection({"metric", "aggregate"}):
                continue
            result.append(field)
    return _stable(result)


def _date_semantics(request: dict[str, Any]) -> tuple[str, bool]:
    question = normalize_text(str(request.get("question") or ""))
    if any(
        _contains(question, cue)
        for cue in ("전체 기간", "모든 기간", "전 기간", "all time", "entire period")
    ):
        # A registered recipe may require the date_scope slot, but an explicit
        # all-time scope is a complete value that must not compile into a
        # reference-date filter.
        return "__all_time__", False
    values = _typed_values(request, "date")
    if not values:
        values = extract_date_candidates(
            str(request.get("question") or ""),
            request.get("reference_instant"),
            str(request.get("timezone") or "Asia/Seoul"),
        )
    selected = values[-1] if values else {}
    date_value = str(selected.get("value") or str(request.get("reference_instant") or "")[:10])
    return date_value, bool(values)


def _rank_semantics(request: dict[str, Any]) -> dict[str, Any] | None:
    values = _typed_values(request, "rank")
    if values:
        selected = values[0]
        mode = str(selected.get("mode") or "")
        limit = int(selected.get("limit") or 0)
        if mode in {"top", "bottom"} and limit > 0:
            return {"mode": mode, "limit": limit}
    question = normalize_text(str(request.get("question") or ""))
    match = TOP_N_PATTERN.search(question)
    if match:
        mode = "top" if match.group("mode").casefold() in {"상위", "top"} else "bottom"
        return {"mode": mode, "limit": max(1, int(match.group("limit")))}
    if any(_contains(question, term) for term in ("가장 큰", "최대", "highest", "largest")):
        return {"mode": "top", "limit": 1}
    if any(_contains(question, term) for term in ("가장 작은", "최소", "lowest", "smallest")):
        return {"mode": "bottom", "limit": 1}
    return None


def _sort_semantics(question: str, metric_refs: list[str]) -> dict[str, Any] | None:
    if not metric_refs:
        return None
    if any(_contains(question, term) for term in ("큰 순", "내림차순", "descending")):
        return {"field": metric_refs[-1], "direction": "desc"}
    if any(_contains(question, term) for term in ("작은 순", "오름차순", "ascending")):
        return {"field": metric_refs[-1], "direction": "asc"}
    return None


def _tie_policy(question: str, rank: dict[str, Any] | None) -> str:
    if rank and int(rank.get("limit") or 0) == 1:
        return "include_all"
    if any(_contains(question, term) for term in ("동률", "동점", "모두", "ties")):
        return "include_all"
    return "exact_n"


def _request_scope(request: dict[str, Any], cues: set[str]) -> str:
    if not request.get("state_ref"):
        return "new_analysis"
    question = normalize_text(str(request.get("question") or ""))
    if not any(_contains(question, term) for term in ("그중", "그 결과", "위 결과", "이전 결과", "those", "previous")):
        return "new_analysis"
    if "join" in cues:
        return "previous_result_enrich"
    return "previous_result_transform"


def _inherit_prior(
    semantics: dict[str, Any],
    prior_semantics: dict[str, Any] | None,
    prior_result: dict[str, Any] | None,
) -> dict[str, Any]:
    if semantics.get("request_scope") == "new_analysis" or not isinstance(prior_semantics, dict):
        return semantics
    result = deepcopy(semantics)
    for key in (
        "metric_refs",
        "dimension_refs",
        "field_refs",
        "dataset_refs",
        "relation_refs",
        "grain_refs",
        "function_refs",
    ):
        if not result.get(key):
            result[key] = deepcopy(prior_semantics.get(key) or [])
    if not result.get("date_explicit"):
        result["date"] = prior_semantics.get("date") or result.get("date")
    if isinstance(prior_result, dict):
        columns = _strings(prior_result.get("columns") or [])
        if columns:
            result["previous_result_columns"] = columns
    return result


def _alias_ambiguity(matches: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for target_type, candidates in matches.items():
        by_span: dict[tuple[int, int], set[str]] = {}
        for candidate in candidates:
            evidence = candidate["evidence"]
            by_span.setdefault((int(evidence["start"]), int(evidence["end"])), set()).add(str(candidate["identity"]))
        for (start, end), identities in sorted(by_span.items()):
            if len(identities) > 1:
                result.append(
                    {
                        "target_type": target_type,
                        "matched_span": f"{start}:{end}",
                        "identities": sorted(identities),
                    }
                )
    return result


def _dedupe_evaluations(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for value in values:
        marker = sha256_json(value.get("semantics") or {})
        previous = selected.get(marker)
        if previous is None or int(value.get("score") or 0) > int(previous.get("score") or 0):
            selected[marker] = value
    return sorted(
        selected.values(),
        key=lambda item: (-int(item.get("score") or 0), sha256_json(item.get("semantics") or {})),
    )


def _matched_ids(matches: dict[str, list[dict[str, Any]]], target_type: str) -> list[str]:
    return _stable(item.get("identity") for item in matches.get(target_type, []))


def _root_metric_refs(
    catalog: dict[str, Any],
    metric_ids: Iterable[str],
    *,
    request: dict[str, Any] | None = None,
    matches: dict[str, list[dict[str, Any]]] | None = None,
) -> list[str]:
    """Return requested formula roots while keeping dependencies implicit.

    If a question matches a derived metric and also words naming its source
    metrics, the derived metric is the visible result.  Its dependencies remain
    available through the compiler's formula closure, not as extra columns.
    """

    selected = _stable(metric_ids)
    # Preserve formula dependencies when the user explicitly enumerates
    # multiple metric columns (``A and B``, ``A, B``).  Formula wording such as
    # ``A compared with B ratio`` has no enumeration separator, so its source
    # metrics remain execution-only dependencies.  This distinction is driven
    # entirely by registered metric match spans and a small language-neutral
    # list-separator grammar; it does not name any domain metric.
    question = normalize_text(str((request or {}).get("question") or ""))
    metric_matches = [
        item
        for item in (matches or {}).get("metric", [])
        if isinstance(item, dict) and str(item.get("identity") or "") in set(selected)
    ]
    metric_matches.sort(key=lambda item: int((item.get("evidence") or {}).get("start") or 0))
    for left, right in zip(metric_matches, metric_matches[1:]):
        left_end = int((left.get("evidence") or {}).get("end") or 0)
        right_start = int((right.get("evidence") or {}).get("start") or 0)
        separator = question[left_end:right_start]
        if re.search(r"(?:,|/|\band\b|\bor\b|및|그리고|와|과)", separator, flags=re.IGNORECASE):
            return selected
    selected_set = set(selected)
    dependencies: set[str] = set()
    for metric_id in selected:
        metric = (catalog.get("metrics") or {}).get(metric_id) or {}
        formula = metric.get("formula") if isinstance(metric.get("formula"), dict) else {}
        dependencies.update(ref for ref in _formula_metric_refs(formula) if ref in selected_set)
    roots = [metric_id for metric_id in selected if metric_id not in dependencies]
    return roots or selected


def _visible_field_refs(
    request: dict[str, Any],
    catalog: dict[str, Any],
    matches: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Separate visible result fields from fields used only as qualifiers.

    The original match pool is retained for source/filter closure.  This view
    removes a field mention swallowed by a longer registered entity-group label
    (for example ``electronics category``) and Korean possessive entity nouns
    such as ``product's`` when a later concrete field is requested.
    """

    question = normalize_text(str(request.get("question") or ""))
    field_matches = [item for item in matches.get("field", []) if isinstance(item, dict)]
    group_matches = [item for item in matches.get("entity_group", []) if isinstance(item, dict)]
    result: list[str] = []
    for match in field_matches:
        field = str(match.get("identity") or "")
        evidence = match.get("evidence") if isinstance(match.get("evidence"), dict) else {}
        start = int(evidence.get("start") or 0)
        end = int(evidence.get("end") or 0)
        qualifier_only = False
        same_field_later = any(
            str(item.get("identity") or "") == field
            and int((item.get("evidence") or {}).get("start") or 0) > end
            for item in field_matches
            if isinstance(item.get("evidence"), dict)
        )
        if same_field_later and re.match(
            r"\s*(?:이|가|은|는)?\s*[-+]?(?:\d+(?:\.\d+)?|\.\d+)\s*보다\s*(?:큰|작은|크|작)",
            question[end:],
        ):
            # The earlier occurrence binds a scalar predicate; the later
            # occurrence is the explicit result-column request and therefore
            # determines visible order.
            qualifier_only = True
        for group_match in group_matches:
            group_id = str(group_match.get("identity") or "")
            group = (catalog.get("entity_groups") or {}).get(group_id) or {}
            target_field = str(group.get("target_field") or group.get("entity") or "")
            group_evidence = (
                group_match.get("evidence") if isinstance(group_match.get("evidence"), dict) else {}
            )
            if (
                target_field == field
                and int(group_evidence.get("start") or 0) <= start
                and int(group_evidence.get("end") or 0) >= end
            ):
                qualifier_only = True
                break
        later_field = any(
            int((item.get("evidence") or {}).get("start") or 0) > end
            for item in field_matches
            if isinstance(item.get("evidence"), dict)
        )
        if not qualifier_only and later_field and question[end:].lstrip().startswith("의"):
            qualifier_only = True
        if not qualifier_only and field:
            result.append(field)
    return _stable(result)


def _semantic_refs(semantics: dict[str, Any], target_type: str) -> list[str]:
    key = {
        "metric": "metric_refs",
        "field": "field_refs",
        "dataset": "dataset_refs",
        "recipe": "recipe_refs",
        "grain": "grain_refs",
        "relation": "relation_refs",
        "entity_group": "entity_group_refs",
        "function": "function_refs",
    }.get(target_type, "")
    return _strings(semantics.get(key) or []) if key else []


def _typed_values(request: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    raw = request.get("literal_candidates")
    if isinstance(raw, dict):
        return [deepcopy(item) for item in raw.get(kind) or [] if isinstance(item, dict)]
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


def _registered_filter_literals(
    request: dict[str, Any],
    catalog: dict[str, Any],
    matches: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    filters: list[dict[str, Any]] = []
    gaps: list[str] = []

    # Generic field-literal grammar.  A value is accepted only when it is
    # anchored immediately after an alias of a registered filter field.  This
    # deliberately does not guess free-form nouns or domain-specific product
    # tokens.  Multi-word strings must be quoted; unquoted literals are bounded
    # by a particle, whitespace, or comma.
    question = normalize_text(str(request.get("question") or ""))
    for match in matches.get("field", []):
        field = str(match.get("identity") or "")
        field_spec = (catalog.get("fields") or {}).get(field) or {}
        if "filter" not in set(_strings(field_spec.get("roles") or [])):
            continue
        evidence = match.get("evidence") if isinstance(match.get("evidence"), dict) else {}
        start = int(evidence.get("start") or 0)
        end = int(evidence.get("end") or 0)
        suffix = question[end : end + 180]
        value_type = (
            "number"
            if str(field_spec.get("coercion") or "").casefold() in {"strict_number", "number", "float", "decimal"}
            else str(field_spec.get("semantic_type") or "string")
        )
        directional_match = re.match(
            r"\s*(?:은|는|이|가)?\s*(?P<value>[-+]?(?:\d+(?:\.\d+)?|\.\d+))\s*보다\s*"
            r"(?P<direction>크거나\s*같은|작거나\s*같은|큰|작은)",
            suffix,
        )
        if directional_match:
            operator = {
                "크거나같은": "gte",
                "작거나같은": "lte",
                "큰": "gt",
                "작은": "lt",
            }[re.sub(r"\s+", "", str(directional_match.group("direction")))]
            try:
                value = _coerce_filter_value(
                    str(directional_match.group("value")),
                    value_type,
                )
            except ValueError:
                gaps.append(f"filter_value:{field}")
            else:
                literal_end = end + directional_match.end()
                filters.append(
                    {
                        "candidate_id": f"literal:{field}:{operator}:{sha256_json([field, value, start, literal_end])[:16]}",
                        "field": field,
                        "operator": operator,
                        "value": value,
                    }
                )
        literal_match = re.match(
            r"\s*(?:=|은|는|이|가)\s*(?:[\"“](?P<quoted>[^\"”]{1,128})[\"”]|(?P<bare>[^\s,]{1,128}?))(?=(?:인(?:\s|$)|이며(?:\s|$)|이고(?:\s|$)|,|\s|$))",
            suffix,
        )
        if not literal_match:
            continue
        raw_value = str(literal_match.group("quoted") or literal_match.group("bare") or "").strip()
        if not raw_value:
            continue
        trailing = suffix[literal_match.end() :].lstrip()
        # ``X가 ABC로 시작`` is a starts_with expression already emitted by
        # the typed request-literal resolver, not an equality literal whose
        # value happens to be ``ABC로``.
        if raw_value.endswith("로") and trailing.startswith("시작"):
            continue
        if raw_value.endswith("보다") or raw_value.casefold() in {
            "가장",
            "상위",
            "하위",
            "최대",
            "최소",
            "합계",
            "평균",
            "전체",
            "highest",
            "lowest",
            "largest",
            "smallest",
        }:
            continue
        try:
            value = _coerce_filter_value(raw_value, value_type)
        except ValueError:
            gaps.append(f"filter_value:{field}")
            continue
        literal_end = end + literal_match.end()
        filters.append(
            {
                "candidate_id": f"literal:{field}:eq:{sha256_json([field, value, start, literal_end])[:16]}",
                "field": field,
                "operator": "eq",
                "value": value,
            }
        )

    # Registered natural-language value groups are compiled metadata, not
    # model guesses.  A matched group may therefore contribute its sealed
    # selection as a typed filter.  This is the generic path for labels such
    # as ``전자 카테고리`` -> ``CATEGORY eq A`` and works for any domain that
    # registers an equivalent entity-group contract.
    for match in matches.get("entity_group", []):
        group_id = str(match.get("identity") or "")
        group = (catalog.get("entity_groups") or {}).get(group_id) or {}
        field = str(group.get("target_field") or group.get("entity") or "")
        selection = group.get("selection") if isinstance(group.get("selection"), dict) else {}
        if not selection:
            members = [str(value) for value in group.get("members") or [] if str(value)]
            if members:
                selection = {"operator": "in", "value": members}
        operator = str(selection.get("operator") or "")
        if not field or not _registered(catalog, "field", field) or operator == "all_registered":
            continue
        if operator not in {"eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "starts_with", "contains"}:
            gaps.append(f"entity_group_operator:{group_id}")
            continue
        if "value" not in selection:
            gaps.append(f"entity_group_value:{group_id}")
            continue
        filters.append(
            {
                "candidate_id": str(match.get("candidate_id") or f"entity_group:{group_id}"),
                "field": field,
                "operator": operator,
                "value": deepcopy(selection.get("value")),
            }
        )

    # Compatibility literals emitted by the request capsule are accepted only
    # when their target is still a registered field.  They are not required by
    # the generic lane and therefore cannot create a field implicitly.
    for item in _typed_values(request, "product_token"):
        field = str(item.get("field") or "")
        operator = str(item.get("operator") or "")
        if not _registered(catalog, "field", field):
            gaps.append(f"filter_field:{field or 'missing'}")
            continue
        filters.append(
            {
                "candidate_id": str(item.get("candidate_id") or ""),
                "field": field,
                "operator": operator,
                "value": deepcopy(item.get("value")),
            }
        )
    unique_filters: list[dict[str, Any]] = []
    seen_filters: set[str] = set()
    for item in filters:
        marker = sha256_json({key: item.get(key) for key in ("field", "operator", "value")})
        if marker not in seen_filters:
            seen_filters.add(marker)
            unique_filters.append(item)

    thresholds = [
        {
            "candidate_id": str(item.get("candidate_id") or ""),
            "operator": str(item.get("operator") or ""),
            "value": deepcopy(item.get("value")),
            "unit": str(item.get("unit") or ""),
        }
        for item in _typed_values(request, "threshold")
    ]
    return unique_filters, thresholds, _stable(gaps)


def _coerce_filter_value(raw: str, semantic_type: str) -> Any:
    kind = semantic_type.casefold()
    if kind in {"number", "float", "decimal", "currency", "percent", "percentage", "ratio", "quantity"}:
        return float(raw.replace(",", ""))
    if kind in {"integer", "int"}:
        return int(raw.replace(",", ""))
    if kind in {"boolean", "bool"}:
        normalized = raw.casefold()
        if normalized in {"true", "1", "yes", "y", "예", "네"}:
            return True
        if normalized in {"false", "0", "no", "n", "아니오", "아니요"}:
            return False
        raise ValueError("invalid boolean literal")
    # Date-shaped values are already canonicalized by request-literals.  At a
    # field equality boundary we only accept the unambiguous ISO representation.
    if kind in {"localdate", "date"} and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        raise ValueError("invalid LocalDate literal")
    return raw


def _alias_spans(question: str, alias: str) -> list[tuple[int, int]]:
    target = normalize_text(alias)
    if not target:
        return []
    flags = re.I
    if re.search(r"[가-힣]", target):
        pattern = re.compile(re.escape(target), flags)
    else:
        pattern = re.compile(rf"(?<![0-9A-Za-z_]){re.escape(target)}(?![0-9A-Za-z_])", flags)
    return [(match.start(), match.end()) for match in pattern.finditer(question)]


def _contains(question: str, lexeme: str) -> bool:
    return bool(_alias_spans(normalize_text(question), lexeme))


def _registered(catalog: dict[str, Any], target_type: str, identity: str) -> bool:
    if target_type == "function":
        return any(
            _function_identity(card) == identity
            for card in catalog.get("specialized_functions") or []
            if isinstance(card, dict)
        )
    section = CATALOG_TARGET_SECTIONS.get(target_type)
    return bool(section and identity in (catalog.get(section) or {}))


def _function_identity(card: Mapping[str, Any]) -> str:
    function_id = str(card.get("function_id") or "")
    version = card.get("version")
    if not function_id or isinstance(version, bool) or not isinstance(version, int) or version < 1:
        return ""
    return f"{function_id}@{version}"


def _function_card(catalog: dict[str, Any], identity: str) -> dict[str, Any]:
    matches = [
        deepcopy(card)
        for card in catalog.get("specialized_functions") or []
        if isinstance(card, dict) and _function_identity(card) == identity
    ]
    if len(matches) != 1:
        _fail(
            "metadata_dependency_error",
            "candidate_routing",
            "registered function reference does not resolve uniquely.",
            {"function_ref": identity},
        )
    return matches[0]


def _strings(values: Iterable[Any] | Any) -> list[str]:
    """Return registered textual values, including compiled alias objects."""

    if values in (None, ""):
        return []
    if isinstance(values, str):
        return [values]
    if isinstance(values, Mapping):
        for key in ("text", "value", "alias", "name"):
            candidate = values.get(key)
            if candidate not in (None, ""):
                return [str(candidate)]
        return []
    result: list[str] = []
    for value in values:
        if value in (None, ""):
            continue
        if isinstance(value, Mapping):
            result.extend(_strings(value))
        else:
            result.append(str(value))
    return result


def _stable(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value or "")
        if text and text not in result:
            result.append(text)
    return result


def _parse_selection(text: str) -> str:
    raw = str(text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I | re.S).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < start:
        raise ValueError("JSON object not found")
    value = json.loads(raw[start : end + 1])
    if not isinstance(value, dict) or set(value) != {"intent_candidate_id"}:
        raise ValueError("selection must contain only intent_candidate_id")
    return str(value["intent_candidate_id"] or "")


def _fail(code: str, stage: str, message: str, details: dict[str, Any] | None = None) -> None:
    raise ContractError(code, stage, message, details)


__all__ = [
    "build_generic_v2_candidate_bundle",
    "validate_generic_v2_candidate_bundle",
    "normalize_generic_v2_intent",
    "build_generic_v2_intent_prompt",
    "resolve_generic_v2_intent",
]
