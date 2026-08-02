"""Real freeform Langflow/Mongo v2 metadata authoring validation.

The default success lane bootstraps a fresh manufacturing domain from the three
separate worker-authored v6 TXT inputs, without injecting an executable
blueprint or explicit-inventory manifest into the Flow.  Every authoring cycle
uses prepare -> externally-approved -> execute and the final package is loaded
through the standalone Data Analysis DomainBundleLoader. Persisted evidence is
hash/status only; raw TXT, provider output, API keys and approval payloads are
never written.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import sha256_json
from reference_runtime.contracts import validate_contract
from reference_runtime.authoring_source_manifest import extract_authoring_source_manifest
from reference_runtime.authoring_blueprint import compute_blueprint_sha256
from reference_runtime.domain_packages import (
    validate_domain_package,
    validate_runtime_catalog_v2,
)
from reference_runtime.registered_functions import registered_function_descriptor
from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    assert_secret_absent,
    gemini_model_contract_evidence,
    langflow_gemini_contract_evidence,
    load_dotenv_values,
    resolve_gemini_api_key,
)
from tools.validate_langflow_http_e2e import _auth_headers, _bounded_error, _run_url, _upload_flow

FLOW_DIR = ROOT / "flow_exports"
FLOW_PATHS = (
    FLOW_DIR / "metadata_v6_domain_authoring_flow_v6_standalone.json",
    FLOW_DIR / "metadata_v6_dataset_catalog_authoring_flow_v6_standalone.json",
    FLOW_DIR / "metadata_v6_main_filter_authoring_flow_v6_standalone.json",
    FLOW_DIR / "metadata_v6_domain_policy_authoring_flow_v6_standalone.json",
)
# The order-sales fixtures remain available to the strict optional
# explicit-inventory/admin-boundary helpers below.  They are deliberately not
# used by the default freeform success lane.
SOURCE_PATH = ROOT / "validation" / "order_sales_metadata_input.txt"
BLUEPRINT_PATH = (
    ROOT / "metadata" / "domain_packs" / "order_sales" / "trusted_executable_blueprint.json"
)
BLUEPRINT_PIN_PATH = BLUEPRINT_PATH.with_suffix(".sha256")

V6_INPUT_DIR = ROOT / "metadata" / "authoring" / "v6_inputs"
FREEFORM_REORDERED_INPUT_DIR = (
    ROOT
    / "validation"
    / "fixtures"
    / "authoring"
    / "freeform_reordered_v1"
)
DEFAULT_SOURCE_SET_ID = "manufacturing_worker_v6"
FREEFORM_REORDERED_SOURCE_SET_ID = "manufacturing_freeform_reordered_v1"
DOMAIN_TEXT_PATH = V6_INPUT_DIR / "domain_v6.txt"
DATASET_TEXT_PATH = V6_INPUT_DIR / "dataset_v6.txt"
MAIN_FILTER_TEXT_PATH = V6_INPUT_DIR / "main_filter_v6.txt"
DOMAIN_POLICY_TEXT_PATH = V6_INPUT_DIR / "domain_policy_v6.txt"
AUTHORING_INPUT_PATHS = {
    "domain": DOMAIN_TEXT_PATH,
    "dataset": DATASET_TEXT_PATH,
    "main_filter": MAIN_FILTER_TEXT_PATH,
    "domain_policy": DOMAIN_POLICY_TEXT_PATH,
}
WORKER_INPUT_FILENAMES = {
    "domain": "domain_v6.txt",
    "dataset": "dataset_v6.txt",
    "main_filter": "main_filter_v6.txt",
}
_SOURCE_SET_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
AUTHORING_GEMINI_MODEL = "gemini-3.5-flash-lite"
AUTHORING_BRANCH_PURPOSES = {
    "domain": "metadata_domain_draft",
    "dataset": "metadata_dataset_draft",
    "main_filter": "metadata_main_filter_draft",
}
MANUFACTURING_COMPILED_CATALOG_PATH = (
    ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "compiled"
    / "runtime_catalog.v2.json"
)
MANUFACTURING_REQUIRED_SECTIONS = (
    "datasets",
    "fields",
    "metrics",
    "recipes",
    "predicates",
    "grains",
    "orderings",
    "entity_groups",
)
DOMAIN_BOOTSTRAP_INPUT_NODE_IDS = {
    "domain": "chat_input",
    "dataset": "dataset_source_input",
    "main_filter": "main_filter_source_input",
}
FREEFORM_CLARIFICATION_PROBE = (
    "새 업무 분석을 만들고 싶은데 어떤 자료를 봐야 하는지와 무엇을 계산해야 하는지는 "
    "아직 정하지 못했어요. 임의로 정하지 말고 제가 업무 용어로 답할 수 있는 "
    "확인 질문만 해 주세요."
)
FREEFORM_CLARIFICATION_DATASET_PROBE = (
    "어떤 업무 자료를 사용할지는 아직 정하지 못했어요. 자료의 이름이나 내부 번호를 "
    "요구하지 말고, 어떤 내용의 자료가 필요한지 쉬운 말로 물어봐 주세요."
)
FREEFORM_CLARIFICATION_MAIN_FILTER_PROBE = (
    "조회할 때 어떤 기준으로 범위를 좁힐지도 아직 정하지 못했어요. 시스템 용어를 "
    "요구하지 말고 날짜, 제품, 공정처럼 제가 고를 수 있는 업무 기준으로 물어봐 주세요."
)

DATASET_PATCH_TEXT = """\
기존 주문·매출 도메인의 데이터셋 메타데이터를 부분 수정합니다.
products 데이터셋의 표시 이름만 '상품 기준정보'로 바꾸세요.
canonical 필드는 PRODUCT_ID, PRODUCT_NAME, CATEGORY입니다.
datasets 섹션만 수정하고 필드, 지표, 관계, 필터, 정책은 그대로 유지하세요.
"""

MAIN_FILTER_PATCH_TEXT = """\
기존 주문·매출 도메인의 메인 필터 별칭을 추가합니다.
별칭 카드의 안정 식별자는 field:CATEGORY이고 대상 유형은 field, 대상 키는 CATEGORY입니다.
사용자가 '카테고리', '상품군', '상품 분류'라고 말하면 CATEGORY 필드로 해석하세요.
aliases 섹션만 수정하고 데이터셋, 지표, 관계, 출력 정책은 그대로 유지하세요.
"""

DOMAIN_POLICY_PATCH_TEXT = """\
기존 주문·매출 도메인의 의도 해석과 답변 표시 정책만 갱신합니다.
등록된 데이터셋, 필드, 지표, 관계, 필터 및 레시피는 변경하지 마세요.
별도 정책 입력에 제공된 의도 문구, 답변 문구, 등록형 함수 카드와 출력 프로필만 적용하세요.
"""

POLICY_INTENT_EXTENSION = (
    "제조 용어는 등록된 dataset, field, metric, recipe 별칭만 사용하고 "
    "모호하면 후보 계약으로 제한한다."
)
POLICY_ANSWER_EXTENSION = (
    "응답은 실행 결과의 검증된 사실만 설명하고 조회 기준, 단위, "
    "빈 결과 여부를 명시한다."
)
_POLICY_FUNCTION_DESCRIPTOR = registered_function_descriptor(
    "core.trim_and_match_tokens",
    1,
)
POLICY_FUNCTION_CARD = {
    "function_id": _POLICY_FUNCTION_DESCRIPTOR["function_id"],
    "version": _POLICY_FUNCTION_DESCRIPTOR["version"],
    "execution_mode": "registered_standalone",
    "implementation_sha256": _POLICY_FUNCTION_DESCRIPTOR["implementation_sha256"],
    "input_schema": deepcopy(_POLICY_FUNCTION_DESCRIPTOR["input_schema"]),
    "output_schema": deepcopy(_POLICY_FUNCTION_DESCRIPTOR["output_schema"]),
    "required_fields": ["MCP_NO"],
    "limits": {
        "timeout_ms": 1000,
        "max_input_rows": 100,
        "max_output_rows": 100,
        "max_output_bytes": 100_000,
    },
    "failure_policy": "fail_closed",
    "aliases": ["priority MCP labels"],
    "call_template": {
        "dataset_ref": "production",
        "field_ref": "MCP_NO",
        "parameters": {
            "tokens": ["priority"],
            "operator": "equals",
            "match_mode": "any",
            "case_sensitive": False,
        },
        "output_fields": ["MCP_NO"],
    },
}
POLICY_OUTPUT_OVERLAY = {"validation_policy_marker": "manufacturing-freeform-v1"}


def _source_style_evidence(text: str) -> dict[str, Any]:
    """Return text-free evidence that distinguishes free-prose fixture styles."""

    lines = text.splitlines()
    nonempty_lines = [line for line in lines if line.strip()]
    style_material = {
        "markdown_heading_count": sum(
            1 for line in nonempty_lines if re.match(r"^\s{0,3}#{1,6}\s+", line)
        ),
        "bullet_line_count": sum(
            1 for line in nonempty_lines if re.match(r"^\s*[-*+]\s+", line)
        ),
        "numbered_line_count": sum(
            1 for line in nonempty_lines if re.match(r"^\s*\d+[.)]\s+", line)
        ),
        "paragraph_count": len(
            [part for part in re.split(r"(?:\r?\n){2,}", text) if part.strip()]
        ),
        "starts_with_markdown_heading": bool(
            nonempty_lines
            and re.match(r"^\s{0,3}#{1,6}\s+", nonempty_lines[0])
        ),
    }
    return {
        **style_material,
        "style_sha256": sha256_json(style_material),
        "raw_text_persisted": False,
    }


def _authoring_input_paths(worker_input_dir: Path) -> dict[str, Path]:
    resolved = worker_input_dir.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise RuntimeError("authoring_worker_input_dir_outside_root") from exc
    return {
        **{
            kind: resolved / filename
            for kind, filename in WORKER_INPUT_FILENAMES.items()
        },
        "domain_policy": DOMAIN_POLICY_TEXT_PATH,
    }


def _load_v6_authoring_sources(
    worker_input_dir: Path = V6_INPUT_DIR,
    source_set_id: str = DEFAULT_SOURCE_SET_ID,
) -> tuple[dict[str, str], dict[str, str], dict[str, Any]]:
    """Load the four v6 worker/admin TXT inputs and return text-free evidence."""

    normalized_source_set_id = str(source_set_id or "").strip()
    if not _SOURCE_SET_ID_PATTERN.fullmatch(normalized_source_set_id):
        raise RuntimeError("authoring_source_set_id_invalid")
    input_paths = _authoring_input_paths(worker_input_dir)
    texts: dict[str, str] = {}
    source_hashes: dict[str, str] = {}
    source_evidence: dict[str, Any] = {}
    for kind, path in input_paths.items():
        if not path.is_file():
            raise RuntimeError(f"v6_authoring_input_missing:{kind}")
        text = path.read_text(encoding="utf-8-sig").strip()
        if not text:
            raise RuntimeError(f"v6_authoring_input_empty:{kind}")
        content_sha256 = sha256(text.encode("utf-8")).hexdigest()
        texts[kind] = text
        source_hashes[kind] = content_sha256
        source_evidence[kind] = {
            "path": path.relative_to(ROOT).as_posix(),
            "content_sha256": content_sha256,
            "byte_count": len(text.encode("utf-8")),
            "line_count": len(text.splitlines()),
            "source_text_persisted": False,
            "source_set_id_sha256": sha256(
                normalized_source_set_id.encode("utf-8")
            ).hexdigest(),
            "style_evidence": _source_style_evidence(text),
        }
    return texts, source_hashes, source_evidence


def _compose_domain_bootstrap_source(
    domain_text: str,
    dataset_text: str,
    main_filter_text: str,
    *,
    require_auxiliary: bool = True,
) -> str:
    """Mirror NaturalMetadataSourceBundle's exact, worker-facing text envelope."""

    parts = (
        ("도메인 정보", str(domain_text or "").strip()),
        ("데이터셋 정보", str(dataset_text or "").strip()),
        ("주요 필터 정보", str(main_filter_text or "").strip()),
    )
    if not parts[0][1]:
        raise ValueError("domain_bootstrap_domain_source_missing")
    if require_auxiliary and any(not text for _, text in parts[1:]):
        raise ValueError("domain_bootstrap_auxiliary_source_missing")
    if sum(len(text.encode("utf-8")) for _, text in parts) > 64 * 1024:
        raise ValueError("domain_bootstrap_source_budget_exceeded")
    return "\n\n".join(
        f"--- {label} 시작 ---\n{text}\n--- {label} 끝 ---"
        for label, text in parts
        if text
    )


def _source_is_alias_only(source_text: str | None) -> bool:
    if not source_text:
        return False
    try:
        manifest = extract_authoring_source_manifest(source_text)
    except Exception:
        return False
    counts = manifest.get("counts") if isinstance(manifest, dict) else None
    if not isinstance(counts, dict):
        return False
    non_alias_kinds = {
        "datasets",
        "fields",
        "field_bindings",
        "field_roles",
        "metrics",
        "grains",
        "grain_keys",
        "grain_display_fields",
        "relations",
        "relation_endpoints",
        "relation_keys",
        "relation_policies",
        "recipes",
        "operations",
    }
    return (
        int(counts.get("aliases") or 0) >= 1
        and int(counts.get("alias_bindings") or 0) == int(counts.get("aliases") or 0)
        and all(int(counts.get(kind) or 0) == 0 for kind in non_alias_kinds)
    )


def _expected_prepare_llm_calls(
    authoring_kind: str,
    source_text: str | None = None,
    *,
    source_grounding_mode: str = "freeform_llm",
    trusted_blueprint_configured: bool = False,
) -> dict[str, int]:
    """Return the closed v6 authoring call budget for one prepare cycle."""

    kind = str(authoring_kind or "").strip().casefold()
    grounding_mode = str(source_grounding_mode or "").strip().casefold()
    if grounding_mode not in {"freeform_llm", "explicit_inventory"}:
        raise ValueError("source_grounding_mode_invalid")
    blueprint_mode = kind == "domain" and bool(trusted_blueprint_configured)
    return {
        "draft": 3
        if (
            kind == "domain"
            and not blueprint_mode
            and grounding_mode == "freeform_llm"
        )
        else 1
        if (
            (kind == "domain" and not blueprint_mode)
            or kind == "dataset"
            or (
                kind == "main_filter"
                and (
                    grounding_mode == "freeform_llm"
                    or not _source_is_alias_only(source_text)
                )
            )
        )
        else 0,
        "annotation": 1 if blueprint_mode else 0,
        "repair": 0,
    }

PATCH_OWNERSHIP = {
    "dataset": frozenset({"datasets"}),
    "main_filter": frozenset(
        {"aliases", "entity_groups", "grains", "orderings", "predicates", "recipes"}
    ),
    "domain_policy": frozenset(
        {"prompt_extensions", "specialized_functions", "output_profile"}
    ),
}

_CATALOG_VOLATILE_FIELDS = frozenset({"catalog_sha256", "revision"})

_APPROVAL_ERROR_INVARIANTS = {
    sha256(message.encode("utf-8")).hexdigest(): label
    for message, label in (
        (
            "Stored pending payload is not bound to the approval event.",
            "pending_candidate_binding",
        ),
        ("Stored pending payload seal is invalid.", "pending_payload_seal"),
        (
            "Stored pending wrapper identity does not match its payload.",
            "pending_wrapper_identity",
        ),
        (
            "Mongo TTL expiry does not match the immutable pending payload.",
            "pending_ttl_identity",
        ),
        (
            "Stored pending hash material does not match its candidate hash.",
            "pending_hash_material",
        ),
        (
            "Approval event does not match the externally sealed approval record.",
            "approval_event_external_seal",
        ),
        (
            "Idempotent replay approval event differs from the committed seal.",
            "idempotent_replay_event_seal",
        ),
        (
            "Pending payload identity pins do not match the sealed domain package.",
            "pending_package_identity_pins",
        ),
        ("Prepared immutable bundle changed after approval.", "prepared_bundle_immutability"),
        ("Prepared active pointer changed after approval.", "prepared_pointer_immutability"),
    )
}


class AuthoringValidationError(RuntimeError):
    """A validation failure whose payload is deliberately safe to persist."""

    def __init__(self, *, code: str, stage: str, details: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.stage = stage
        self.details = deepcopy(details or {})

ORDER_SALES_REQUIRED_MANIFEST = {
    "datasets": ["orders", "products", "refunds", "targets"],
    "fields": [
        "CATEGORY",
        "CUSTOMER_ID",
        "ORDER_DATE",
        "ORDER_ID",
        "PRODUCT_ID",
        "PRODUCT_NAME",
        "REFUND_AMOUNT",
        "SALES_AMOUNT",
        "TARGET_AMOUNT",
        "TARGET_DATE",
    ],
    "metrics": [
        "ACHIEVEMENT_RATE",
        "NET_SALES_AMOUNT",
        "REFUND_AMOUNT",
        "SALES_AMOUNT",
        "TARGET_AMOUNT",
    ],
    "relations": ["orders_products", "orders_refunds", "sales_targets"],
    "recipes": [
        "sales.by_product",
        "sales.detail_projection",
        "sales.net_by_product",
        "sales.rank",
        "sales.summary",
        "sales.target_comparison",
    ],
}
ORDER_SALES_REQUIRED_MANIFEST_SHA256 = sha256_json(ORDER_SALES_REQUIRED_MANIFEST)


def _walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for nested in value.values():
            yield from _walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk(nested)


def _fresh_environment(prefix: str, nonce: str) -> str:
    normalized = "".join(
        character if character.isascii() and (character.isalnum() or character in "_-") else "_"
        for character in str(prefix or "e2e_validation").casefold()
    ).strip("_-")
    if not normalized or not normalized[0].isalpha():
        normalized = f"e2e_{normalized}"
    return f"{normalized[:22]}_{nonce[:8]}"[:31]


def _iso_text(value: Any) -> str:
    if isinstance(value, datetime):
        current = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return current.astimezone(timezone.utc).isoformat()
    return str(value or "")


def _build_approval_event(
    *,
    nonce: str,
    candidate_id: str,
    candidate_sha256: str,
    subject_id: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    decided_at = now or datetime.now(timezone.utc)
    if decided_at.tzinfo is None:
        decided_at = decided_at.replace(tzinfo=timezone.utc)
    event = {
        "contract_version": "approval.event.v1",
        "event_id": f"approval:{nonce}",
        "candidate_id": candidate_id,
        "candidate_sha256": candidate_sha256,
        "decision": "approved",
        "subject_id": subject_id,
        "decided_at": decided_at.astimezone(timezone.utc).isoformat(),
        "expires_at": (decided_at.astimezone(timezone.utc) + timedelta(minutes=30)).isoformat(),
        "idempotency_key": f"idem:{nonce}",
    }
    return validate_contract(
        event,
        "approval-event.schema.json",
        stage="approval_event_validation",
        error_code="approval_contract_error",
    )


def _tampered_approval_events(event: dict[str, Any]) -> dict[str, dict[str, Any]]:
    decided = datetime.fromisoformat(str(event["decided_at"]).replace("Z", "+00:00"))
    mutations = {
        "event_id": f"{event['event_id']}-tampered",
        "subject_id": f"{event['subject_id']}-tampered",
        "decided_at": (decided - timedelta(seconds=1)).isoformat(),
        "idempotency_key": f"{event['idempotency_key']}-tampered",
    }
    result: dict[str, dict[str, Any]] = {}
    for field, value in mutations.items():
        candidate = deepcopy(event)
        candidate[field] = value
        result[field] = validate_contract(
            candidate,
            "approval-event.schema.json",
            stage="approval_event_validation",
            error_code="approval_contract_error",
        )
    return result


def _catalog_section_hashes(package: dict[str, Any]) -> dict[str, str]:
    catalog = package.get("runtime_catalog") if isinstance(package.get("runtime_catalog"), dict) else {}
    return {
        key: sha256_json(value)
        for key, value in sorted(catalog.items())
        if key not in _CATALOG_VOLATILE_FIELDS
    }


def _section_ownership_checks(
    before_package: dict[str, Any],
    after_package: dict[str, Any],
    *,
    authoring_kind: str,
) -> dict[str, Any]:
    owned = PATCH_OWNERSHIP[authoring_kind]
    before = _catalog_section_hashes(before_package)
    after = _catalog_section_hashes(after_package)
    names = sorted(set(before) | set(after))
    unchanged = {
        name: before.get(name) == after.get(name)
        for name in names
        if name not in owned
    }
    owned_changes = {
        name: before.get(name) != after.get(name)
        for name in sorted(owned)
    }
    return {
        "owned_sections": sorted(owned),
        "unchanged_section_count": sum(1 for value in unchanged.values() if value),
        "unchanged_section_names": sorted(name for name, value in unchanged.items() if value),
        "changed_outside_ownership": sorted(name for name, value in unchanged.items() if not value),
        "changed_owned_sections": sorted(name for name, value in owned_changes.items() if value),
        "checks": {
            "other_sections_unchanged": all(unchanged.values()),
            "at_least_one_owned_section_changed": any(owned_changes.values()),
        },
    }


def _pending_payload_from_storage(document: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise RuntimeError("pending_storage_wrapper_missing")
    payload = validate_contract(
        deepcopy(document.get("pending_payload") or {}),
        "pending-metadata-write.schema.json",
        stage="pending_payload_validation",
        error_code="metadata_schema_error",
    )
    if document.get("_id") != payload.get("candidate_id"):
        raise RuntimeError("pending_wrapper_candidate_mismatch")
    if document.get("pending_payload_sha256") != sha256_json(payload):
        raise RuntimeError("pending_payload_seal_mismatch")
    if sha256_json(payload.get("hash_material") or {}) != payload.get("candidate_sha256"):
        raise RuntimeError("pending_candidate_hash_mismatch")
    if document.get("workflow_status") != "prepared" or payload.get("status") != "prepared":
        raise RuntimeError("pending_workflow_status_invalid")
    for name in ("authoring_kind", "domain_id", "environment"):
        if document.get(name) != payload.get(name):
            raise RuntimeError(f"pending_wrapper_identity_mismatch:{name}")
    wrapper_expiry = document.get("expires_at")
    if not isinstance(wrapper_expiry, datetime):
        raise RuntimeError("pending_wrapper_expiry_not_bson_datetime")
    try:
        payload_expiry = datetime.fromisoformat(str(payload.get("expires_at") or "").replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError("pending_payload_expiry_invalid") from exc
    if payload_expiry.tzinfo is None:
        payload_expiry = payload_expiry.replace(tzinfo=timezone.utc)
    wrapper_utc = (
        wrapper_expiry if wrapper_expiry.tzinfo is not None else wrapper_expiry.replace(tzinfo=timezone.utc)
    ).astimezone(timezone.utc)
    payload_utc = payload_expiry.astimezone(timezone.utc)
    if payload_utc.microsecond % 1000 != 0:
        raise RuntimeError("pending_payload_expiry_not_bson_canonical")
    if wrapper_utc != payload_utc:
        raise RuntimeError("pending_wrapper_expiry_mismatch")
    return payload


def _pending_evidence(
    document: dict[str, Any],
    *,
    authoring_kind: str,
    domain_id: str,
    environment: str,
    target_revision: int,
    base_package: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _pending_payload_from_storage(document)
    base_revision = int(base_package.get("revision") or 0)
    expected_base_revision: int | None = base_revision if base_revision > 0 else None
    expected_base_bundle = str(base_package.get("bundle_sha256") or "") or None
    expected_base_package = str(base_package.get("package_sha256") or "") or None
    hash_material = payload.get("hash_material") if isinstance(payload.get("hash_material"), dict) else {}
    expected_active = (
        hash_material.get("expected_active")
        if isinstance(hash_material.get("expected_active"), dict)
        else {}
    )
    checks = {
        "schema_exact": True,
        "wrapper_payload_sha256_exact": document.get("pending_payload_sha256") == sha256_json(payload),
        "candidate_hash_material_exact": sha256_json(hash_material) == payload.get("candidate_sha256"),
        "authoring_kind_exact": payload.get("authoring_kind") == authoring_kind,
        "identity_exact": payload.get("domain_id") == domain_id and payload.get("environment") == environment,
        "target_revision_exact": int(payload.get("target_revision") or 0) == target_revision,
        "base_revision_exact": payload.get("base_revision") == expected_base_revision,
        "base_bundle_hash_exact": payload.get("base_bundle_sha256") == expected_base_bundle,
        "base_package_hash_exact": payload.get("base_package_sha256") == expected_base_package,
        "hash_material_base_pin_exact": {
            "revision": int(expected_active.get("revision") or 0),
            "bundle_sha256": str(expected_active.get("bundle_sha256") or ""),
            "package_sha256": str(expected_active.get("package_sha256") or ""),
        }
        == {
            "revision": base_revision,
            "bundle_sha256": str(expected_base_bundle or ""),
            "package_sha256": str(expected_base_package or ""),
        },
        "workflow_prepared": document.get("workflow_status") == "prepared",
        "bson_expiry_present": isinstance(document.get("expires_at"), datetime),
    }
    evidence = {
        "contract_version": payload.get("contract_version"),
        "candidate_id_sha256": sha256(str(payload.get("candidate_id") or "").encode("utf-8")).hexdigest(),
        "candidate_sha256": payload.get("candidate_sha256"),
        "pending_payload_sha256": document.get("pending_payload_sha256"),
        "authoring_kind": payload.get("authoring_kind"),
        "target_revision": payload.get("target_revision"),
        "base_revision": payload.get("base_revision"),
        "base_bundle_sha256": payload.get("base_bundle_sha256"),
        "base_package_sha256": payload.get("base_package_sha256"),
        "prepared_at_sha256": sha256(str(payload.get("prepared_at") or "").encode("utf-8")).hexdigest(),
        "expires_at_sha256": sha256(str(payload.get("expires_at") or "").encode("utf-8")).hexdigest(),
        "raw_pending_payload_persisted": False,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return payload, evidence


def _authoring_responses(value: Any) -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for item in _walk(value):
        if not isinstance(item, dict) or item.get("contract_version") != "metadata.authoring.response.v1":
            continue
        digest = str(item.get("response_sha256") or "")
        if len(digest) == 64:
            found.setdefault(digest, item)
    return list(found.values())


def _message_response_hashes(value: Any) -> set[str]:
    """Read the canonical-response link from supported Message metadata.

    Langflow's Message serializer intentionally drops arbitrary extra fields.
    The presentation component therefore links its human-readable projection to
    the API terminal through the supported ``session_metadata`` field.
    """

    found: set[str] = set()
    for item in _walk(value):
        if not isinstance(item, dict):
            continue
        metadata = item.get("session_metadata")
        if not isinstance(metadata, dict):
            continue
        if metadata.get("contract_version") != "metadata.authoring.message-link.v1":
            continue
        digest = str(metadata.get("response_sha256") or "")
        if len(digest) == 64 and all(char in "0123456789abcdef" for char in digest):
            found.add(digest)
    return found


def _output_blocks(payload: Any) -> list[dict[str, Any]]:
    return [
        item
        for item in _walk(payload)
        if isinstance(item, dict)
        and (item.get("component_id") or item.get("component_display_name"))
        and any(key in item for key in ("results", "outputs", "artifacts"))
    ]


def _project_authoring_schema_bindings(
    payload: dict[str, Any], invocation_rows: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Project provider-schema evidence without retaining prompts or responses."""

    projected: dict[str, dict[str, Any]] = {}
    walked = list(_walk(payload))
    compact_by_purpose: dict[str, dict[str, dict[str, Any]]] = {}
    compact_keys = {
        "contract_version",
        "purpose",
        "invocation_count",
        "provider_schema_binding",
        "binding_status",
        "projection",
        "authoritative_schema_sha256",
        "provider_schema_sha256",
        "runtime_output_schema_sha256",
        "raw_prompt_persisted",
        "raw_response_persisted",
    }
    for item in walked:
        if (
            not isinstance(item, dict)
            or item.get("contract_version")
            != "metadata.llm-schema-binding-summary.v1"
            or set(item) != compact_keys
        ):
            continue
        purpose = str(item.get("purpose") or "")
        if purpose not in set(AUTHORING_BRANCH_PURPOSES.values()):
            continue
        compact_by_purpose.setdefault(purpose, {})[sha256_json(item)] = item
    for branch, purpose in AUTHORING_BRANCH_PURPOSES.items():
        compact_rows = list((compact_by_purpose.get(purpose) or {}).values())
        if len(compact_rows) == 1:
            summary = compact_rows[0]
            projected[branch] = {
                "purpose": purpose,
                "invocation_count": int(summary.get("invocation_count") or 0),
                "provider_schema_binding": str(
                    summary.get("provider_schema_binding") or ""
                ),
                "provider_schema_binding_distinct_count": 1,
                "binding_status": str(summary.get("binding_status") or ""),
                "binding_status_distinct_count": 1,
                "projection": str(summary.get("projection") or ""),
                "projection_distinct_count": 1,
                "authoritative_schema_sha256": str(
                    summary.get("authoritative_schema_sha256") or ""
                ),
                "authoritative_schema_hash_distinct_count": 1,
                "provider_schema_sha256": str(
                    summary.get("provider_schema_sha256") or ""
                ),
                "provider_schema_hash_distinct_count": 1,
                "runtime_output_schema_sha256": str(
                    summary.get("runtime_output_schema_sha256") or ""
                ),
                "runtime_output_schema_hash_distinct_count": 1,
                "raw_prompt_persisted": summary.get("raw_prompt_persisted"),
                "raw_response_persisted": summary.get("raw_response_persisted"),
            }
            continue
        branch_invocations = [
            item
            for item in invocation_rows
            if str(item.get("purpose") or "") == purpose
        ]
        runtime_schema_hashes: set[str] = set()
        for item in walked:
            if (
                not isinstance(item, dict)
                or item.get("contract_version") != "prompt.runtime-context.v1"
                or item.get("purpose") != purpose
            ):
                continue
            variables = item.get("variables")
            output_schema = (
                variables.get("output_schema")
                if isinstance(variables, dict)
                and isinstance(variables.get("output_schema"), dict)
                else None
            )
            if output_schema is not None:
                runtime_schema_hashes.add(sha256_json(output_schema))

        provider_bindings: set[str] = set()
        binding_statuses: set[str] = set()
        provider_projections: set[str] = set()
        authoritative_hashes: set[str] = set()
        provider_hashes: set[str] = set()
        for invocation in branch_invocations:
            provider_binding = str(invocation.get("provider_schema_binding") or "")
            binding_evidence = (
                invocation.get("schema_binding_evidence")
                if isinstance(invocation.get("schema_binding_evidence"), dict)
                else {}
            )
            binding_status = str(binding_evidence.get("binding_status") or "")
            provider_projection = str(binding_evidence.get("projection") or "")
            authoritative_hash = str(
                binding_evidence.get("authoritative_schema_sha256") or ""
            )
            provider_hash = str(binding_evidence.get("provider_schema_sha256") or "")
            if provider_binding:
                provider_bindings.add(provider_binding)
            if binding_status:
                binding_statuses.add(binding_status)
            if provider_projection:
                provider_projections.add(provider_projection)
            if _is_sha256(authoritative_hash):
                authoritative_hashes.add(authoritative_hash)
            if _is_sha256(provider_hash):
                provider_hashes.add(provider_hash)

        if not branch_invocations and not runtime_schema_hashes:
            continue
        projected[branch] = {
            "purpose": purpose,
            "invocation_count": len(branch_invocations),
            "provider_schema_binding": next(iter(provider_bindings))
            if len(provider_bindings) == 1
            else "",
            "provider_schema_binding_distinct_count": len(provider_bindings),
            "binding_status": next(iter(binding_statuses))
            if len(binding_statuses) == 1
            else "",
            "binding_status_distinct_count": len(binding_statuses),
            "projection": next(iter(provider_projections))
            if len(provider_projections) == 1
            else "",
            "projection_distinct_count": len(provider_projections),
            "authoritative_schema_sha256": next(iter(authoritative_hashes))
            if len(authoritative_hashes) == 1
            else "",
            "authoritative_schema_hash_distinct_count": len(authoritative_hashes),
            "provider_schema_sha256": next(iter(provider_hashes))
            if len(provider_hashes) == 1
            else "",
            "provider_schema_hash_distinct_count": len(provider_hashes),
            "runtime_output_schema_sha256": next(iter(runtime_schema_hashes))
            if len(runtime_schema_hashes) == 1
            else "",
            "runtime_output_schema_hash_distinct_count": len(runtime_schema_hashes),
            "raw_prompt_persisted": False,
            "raw_response_persisted": False,
        }
    return projected


def extract_authoring_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    invocation_rows = [
        item
        for item in _walk(payload)
        if isinstance(item, dict)
        and item.get("contract_version") == "llm.invocation.v1"
        and str(item.get("purpose") or "").startswith("metadata_")
    ]
    invocation_response_sizes = sorted(
        {
            len(str(item.get("response_text") or "").encode("utf-8"))
            for item in invocation_rows
            if item.get("status") == "ok"
        }
    )
    schema_bindings = _project_authoring_schema_bindings(payload, invocation_rows)
    responses = _authoring_responses(payload)
    response = responses[0] if len(responses) == 1 else {}
    digest = str(response.get("response_sha256") or "")
    computed = sha256_json({key: value for key, value in response.items() if key != "response_sha256"}) if response else ""
    terminal_hashes: dict[str, set[str]] = {"message": set(), "api": set()}
    terminal_blocks: dict[str, int] = {"message": 0, "api": 0}
    for block in _output_blocks(payload):
        identity = (
            str(block.get("component_id") or "")
            + " "
            + str(block.get("component_display_name") or "")
        ).casefold()
        kind = ""
        if (
            "message_presentation" in identity
            or "authoring message presentation" in identity
            or "chat_output" in identity
            or "chat output" in identity
        ):
            kind = "message"
        elif "api_response" in identity or "api response" in identity:
            kind = "api"
        if not kind:
            continue
        terminal_blocks[kind] += 1
        if kind == "message":
            terminal_hashes[kind].update(_message_response_hashes(block))
        else:
            terminal_hashes[kind].update(
                str(item.get("response_sha256") or "")
                for item in _authoring_responses(block)
            )
    terminal_projection = {key: sorted(value) for key, value in terminal_hashes.items()}
    unchanged = response.get("unchanged_section_checks") if isinstance(response.get("unchanged_section_checks"), dict) else {}
    validation = response.get("validation") if isinstance(response.get("validation"), dict) else {}
    trusted_blueprint = (
        validation.get("trusted_blueprint")
        if isinstance(validation.get("trusted_blueprint"), dict)
        else {}
    )
    source_coverage = (
        validation.get("source_coverage")
        if isinstance(validation.get("source_coverage"), dict)
        else {}
    )
    authoring_proposal = (
        validation.get("authoring_proposal")
        if isinstance(validation.get("authoring_proposal"), dict)
        else {}
    )
    raw_authoring_proposals = (
        validation.get("authoring_proposals")
        if isinstance(validation.get("authoring_proposals"), dict)
        else {}
    )
    authoring_proposals = {
        branch: {
            "contract_version": str(proposal.get("contract_version") or ""),
            "proposal_contract_version": str(
                proposal.get("proposal_contract_version") or ""
            ),
            "status": str(proposal.get("status") or ""),
            "source_sha256": str(proposal.get("source_sha256") or ""),
            "proposal_sha256": str(proposal.get("proposal_sha256") or ""),
            "draft_sha256": str(proposal.get("draft_sha256") or ""),
        }
        for branch in ("domain", "dataset", "main_filter")
        for proposal in [raw_authoring_proposals.get(branch)]
        if isinstance(proposal, dict)
    }
    clarification = (
        response.get("clarification")
        if isinstance(response.get("clarification"), dict)
        else {}
    )
    clarification_questions = (
        clarification.get("questions")
        if isinstance(clarification.get("questions"), list)
        else []
    )
    clarification_missing_fields = (
        clarification.get("missing_fields")
        if isinstance(clarification.get("missing_fields"), list)
        else []
    )
    safe_missing_fields = [
        str(item)
        for item in clarification_missing_fields
        if isinstance(item, str)
        and 1 <= len(item) <= 128
        and all(character.isalnum() or character in "._-" for character in item)
    ][:32]
    clarification_branches = sorted(
        {
            kind
            for kind in ("domain", "dataset", "main_filter")
            if any(
                isinstance(question, str) and question.startswith(f"[{kind}:")
                for question in clarification_questions
            )
            or any(
                isinstance(field, str) and field.startswith(f"{kind}.")
                for field in clarification_missing_fields
            )
        }
    )
    diff = response.get("diff") if isinstance(response.get("diff"), dict) else {}
    error = response.get("error") if isinstance(response.get("error"), dict) else {}
    error_details = error.get("details") if isinstance(error.get("details"), dict) else {}
    error_type = str(error_details.get("error_type") or "")
    if not error_type.isidentifier():
        error_type = ""
    error_message_sha256 = (
        sha256(str(error.get("message") or "").encode("utf-8")).hexdigest()
        if error.get("message")
        else ""
    )
    raw_error_operator = error_details.get("operator")
    error_operator_sha256 = (
        sha256(raw_error_operator.encode("utf-8")).hexdigest()
        if isinstance(raw_error_operator, str)
        and 1 <= len(raw_error_operator) <= 128
        else ""
    )
    raw_error_metric_id = error_details.get("metric_id")
    error_metric_id_sha256 = (
        sha256(raw_error_metric_id.encode("utf-8")).hexdigest()
        if isinstance(raw_error_metric_id, str)
        and 1 <= len(raw_error_metric_id) <= 128
        else ""
    )
    raw_error_field = error_details.get("field")
    error_field_sha256 = (
        sha256(raw_error_field.encode("utf-8")).hexdigest()
        if isinstance(raw_error_field, str)
        and 1 <= len(raw_error_field) <= 128
        else ""
    )
    manifest_error_code = str(error_details.get("manifest_error_code") or "")
    if not (
        1 <= len(manifest_error_code) <= 128
        and all(
            character.isalnum() or character == "_"
            for character in manifest_error_code
        )
    ):
        manifest_error_code = ""
    raw_error_dataset_id = error_details.get("dataset_id")
    error_dataset_id_sha256 = (
        sha256(raw_error_dataset_id.encode("utf-8")).hexdigest()
        if isinstance(raw_error_dataset_id, str)
        and 1 <= len(raw_error_dataset_id) <= 128
        else ""
    )
    raw_detail_value_sha256 = str(error_details.get("detail_value_sha256") or "")
    error_detail_value_sha256 = (
        raw_detail_value_sha256 if _is_sha256(raw_detail_value_sha256) else ""
    )
    raw_field_id_sha256 = str(error_details.get("field_id_sha256") or "")
    error_field_id_sha256 = (
        raw_field_id_sha256 if _is_sha256(raw_field_id_sha256) else ""
    )
    raw_physical_column_sha256 = str(
        error_details.get("physical_column_sha256") or ""
    )
    error_physical_column_sha256 = (
        raw_physical_column_sha256
        if _is_sha256(raw_physical_column_sha256)
        else ""
    )
    error_candidate_count = int(error_details.get("candidate_count") or 0)
    error_detail_index = int(error_details.get("detail_index") or 0)
    error_location = str(error_details.get("error_location") or "")[:80]
    if not error_location.isidentifier():
        error_location = ""
    framing_reason = str(error_details.get("framing_reason") or "")
    if framing_reason not in {
        "unmatched_closing_brace",
        "unclosed_object",
        "array_wrapper",
    }:
        framing_reason = ""
    raw_error_path = error_details.get("path")
    if isinstance(raw_error_path, list):
        error_path = ".".join(
            str(item)[:64]
            for item in raw_error_path[:16]
            if isinstance(item, (str, int))
        )
    else:
        error_path = str(raw_error_path or "")[:512]
    if not all(
        character.isalnum() or character in "._-[]"
        for character in error_path
    ):
        error_path = ""
    candidate_fields = {"candidate_id", "candidate_sha256"}
    package_fields = {"package_sha256", "bundle_sha256", "catalog_sha256"}
    persistence_fields = {
        "persisted",
        "revision",
        "diff",
        "validation",
        "expires_at",
    }
    return {
        "response_sha256": digest,
        "response_hash_valid": bool(digest) and digest == computed,
        "response_count": len(responses),
        "status": response.get("status"),
        "stage": response.get("stage"),
        "authoring_kind": response.get("authoring_kind"),
        "metadata_contract_mode": response.get("metadata_contract_mode"),
        "domain_id": response.get("domain_id"),
        "environment": response.get("environment"),
        "revision": int(response.get("revision") or 0),
        "candidate_id": str(response.get("candidate_id") or ""),
        "candidate_sha256": str(response.get("candidate_sha256") or ""),
        "package_sha256": str(response.get("package_sha256") or ""),
        "bundle_sha256": str(response.get("bundle_sha256") or ""),
        "catalog_sha256": str(response.get("catalog_sha256") or ""),
        "draft_llm_calls": int((response.get("llm_usage") or {}).get("draft_llm_calls") or 0),
        "annotation_llm_calls": int(
            (response.get("llm_usage") or {}).get("annotation_llm_calls") or 0
        ),
        "repair_llm_calls": int((response.get("llm_usage") or {}).get("repair_llm_calls") or 0),
        "llm_invocation_count": len(invocation_rows),
        "llm_response_byte_sizes": invocation_response_sizes,
        "llm_schema_bindings": schema_bindings,
        "error_code": str(error.get("code") or ""),
        "error_stage": str(error.get("stage") or ""),
        "error_location": error_location,
        "error_reason": str(
            ((error.get("details") or {}).get("reason") or "")
            if isinstance(error.get("details"), dict)
            else ""
        )[:96],
        "error_framing_reason": framing_reason,
        "error_input_name": str(
            ((error.get("details") or {}).get("input_name") or "")
            if isinstance(error.get("details"), dict)
            else ""
        )[:96],
        "error_expected_purpose": str(
            ((error.get("details") or {}).get("expected_purpose") or "")
            if isinstance(error.get("details"), dict)
            else ""
        )[:96],
        "error_response_bytes": int(
            ((error.get("details") or {}).get("response_bytes") or 0)
            if isinstance(error.get("details"), dict)
            else 0
        ),
        "error_path": error_path,
        "error_detail_keys": sorted(str(key) for key in (error.get("details") or {}))
        if isinstance(error.get("details"), dict)
        else [],
        "error_type": error_type[:80],
        "error_message_sha256": error_message_sha256,
        "error_operator_sha256": error_operator_sha256,
        "error_metric_id_sha256": error_metric_id_sha256,
        "error_field_sha256": error_field_sha256,
        "manifest_error_code": manifest_error_code,
        "error_dataset_id_sha256": error_dataset_id_sha256,
        "error_detail_value_sha256": error_detail_value_sha256,
        "error_field_id_sha256": error_field_id_sha256,
        "error_physical_column_sha256": error_physical_column_sha256,
        "error_candidate_count": error_candidate_count,
        "error_detail_index": error_detail_index,
        "error_invariant": _APPROVAL_ERROR_INVARIANTS.get(error_message_sha256, ""),
        "diff_sha256": sha256_json(diff) if diff else "",
        "validation": {str(key): str(value) for key, value in sorted(validation.items())},
        "trusted_blueprint_validation": {
            "contract_version": str(trusted_blueprint.get("contract_version") or ""),
            "blueprint_sha256": str(trusted_blueprint.get("blueprint_sha256") or ""),
            "executable_sha256": str(trusted_blueprint.get("executable_sha256") or ""),
            "annotation_proposal_sha256": str(
                trusted_blueprint.get("annotation_proposal_sha256") or ""
            ),
            "external_pin": str(trusted_blueprint.get("external_pin") or ""),
            "executable_immutable": str(
                trusted_blueprint.get("executable_immutable") or ""
            ),
        },
        "source_grounding_validation": {
            "contract_version": str(source_coverage.get("contract_version") or ""),
            "mode": str(source_coverage.get("mode") or ""),
            "source_sha256": str(source_coverage.get("source_sha256") or ""),
            "structured_proposal_sha256": str(
                source_coverage.get("structured_proposal_sha256") or ""
            ),
            "explicit_inventory_coverage": str(
                source_coverage.get("explicit_inventory_coverage") or ""
            ),
            "schema_validation": str(source_coverage.get("schema_validation") or ""),
            "dependency_closure": str(source_coverage.get("dependency_closure") or ""),
            "human_approval_required": source_coverage.get("human_approval_required"),
            "coverage_sha256": str(source_coverage.get("coverage_sha256") or ""),
        },
        "authoring_proposal_validation": {
            "contract_version": str(authoring_proposal.get("contract_version") or ""),
            "proposal_contract_version": str(
                authoring_proposal.get("proposal_contract_version") or ""
            ),
            "status": str(authoring_proposal.get("status") or ""),
            "source_sha256": str(authoring_proposal.get("source_sha256") or ""),
            "proposal_sha256": str(authoring_proposal.get("proposal_sha256") or ""),
            "draft_sha256": str(authoring_proposal.get("draft_sha256") or ""),
            "compact_ir_sha256": str(
                authoring_proposal.get("compact_ir_sha256") or ""
            ),
            "expanded_draft_sha256": str(
                authoring_proposal.get("expanded_draft_sha256") or ""
            ),
            "section_ir_expander_version": str(
                authoring_proposal.get("section_ir_expander_version") or ""
            ),
        },
        "authoring_proposals_validation": authoring_proposals,
        "clarification_validation": {
            "contract_version": str(clarification.get("contract_version") or ""),
            "source_sha256": str(clarification.get("source_sha256") or ""),
            "proposal_sha256": str(clarification.get("proposal_sha256") or ""),
            "questions_count": len(clarification.get("questions") or [])
            if isinstance(clarification.get("questions"), list)
            else 0,
            "missing_fields_count": len(clarification.get("missing_fields") or [])
            if isinstance(clarification.get("missing_fields"), list)
            else 0,
            "questions_sha256": sha256_json(clarification.get("questions") or []),
            "missing_fields_sha256": sha256_json(
                clarification.get("missing_fields") or []
            ),
            "raw_clarification_persisted": False,
            "branches": clarification_branches,
            "safe_missing_fields": safe_missing_fields,
        },
        "response_field_presence": {
            "candidate_fields": sorted(candidate_fields.intersection(response)),
            "package_fields": sorted(package_fields.intersection(response)),
            "persistence_fields": sorted(persistence_fields.intersection(response)),
        },
        "unchanged_section_count": len(unchanged),
        "unchanged_sections_all": all(value is True for value in unchanged.values()),
        "unchanged_section_names": sorted(str(key) for key in unchanged),
        "terminal_blocks": terminal_blocks,
        "terminal_hashes": terminal_projection,
        "terminal_equivalent": bool(digest)
        and all(terminal_blocks[key] >= 1 for key in ("message", "api"))
        and all(terminal_projection[key] == [digest] for key in ("message", "api")),
    }


def _flow_defaults(path: Path) -> dict[str, Any]:
    flow = json.loads(path.read_text(encoding="utf-8"))
    authoring = next(
        (
            item
            for item in flow.get("data", {}).get("nodes", [])
            if item.get("id") == "metadata_authoring_engine"
        ),
        {},
    )
    template = (((authoring.get("data") or {}).get("node") or {}).get("template") or {})
    model_node = next(
        (
            item
            for item in flow.get("data", {}).get("nodes", [])
            if item.get("id") == "draft_language_model"
        ),
        {},
    )
    model_value = (
        ((((model_node.get("data") or {}).get("node") or {}).get("template") or {}).get("model") or {}).get("value")
        or []
    )
    authoring_kind = (template.get("authoring_kind") or {}).get("value")
    node_ids = [
        str(item.get("id") or "")
        for item in flow.get("data", {}).get("nodes", [])
        if isinstance(item, dict)
    ]
    model_contract = langflow_gemini_contract_evidence(
        flow,
        require_model=authoring_kind != "domain_policy",
    )
    return {
        "file": path.name,
        "endpoint_name": flow.get("endpoint_name"),
        "authoring_kind": authoring_kind,
        "metadata_contract_mode": (template.get("metadata_contract_mode") or {}).get("value"),
        "source_grounding_mode": (template.get("source_grounding_mode") or {}).get("value"),
        "trusted_blueprint_json_default_empty": not bool(
            str((template.get("trusted_blueprint_json") or {}).get("value") or "").strip()
        ),
        "trusted_blueprint_pin_default_empty": not bool(
            str((template.get("trusted_blueprint_sha256") or {}).get("value") or "").strip()
        ),
        "model_names": sorted(
            str(item.get("name") or "")
            for item in model_value
            if isinstance(item, dict) and item.get("name")
        ),
        "model_contract": model_contract,
        "prompt_node_count": sum(
            1
            for node_id in node_ids
            if node_id == "authoring_common_prompt"
            or node_id.endswith("_common_prompt")
            or node_id.endswith("_specialized_prompt")
        ),
        "context_builder_node_count": sum(
            1 for node_id in node_ids if node_id.endswith("prompt_context_builder")
        ),
        "composer_node_count": sum(
            1 for node_id in node_ids if node_id.endswith("prompt_bundle_composer")
        ),
        "invoker_node_count": sum(
            1 for node_id in node_ids if node_id.endswith("conditional_llm_invoker")
        ),
        "domain_bootstrap_input_node_ids": sorted(
            set(DOMAIN_BOOTSTRAP_INPUT_NODE_IDS.values()).intersection(node_ids)
        ),
        "natural_source_bundle_node_count": node_ids.count(
            "natural_metadata_source_bundle"
        ),
        "node_count": len(flow.get("data", {}).get("nodes") or []),
    }


def _post_run(
    client: requests.Session,
    headers: dict[str, str],
    server_url: str,
    flow_id: str,
    *,
    input_value: str,
    session_id: str,
    tweaks: dict[str, Any],
    timeout_seconds: int,
    output_type: str = "any",
) -> tuple[int, str, dict[str, Any]]:
    response = client.post(
        _run_url(server_url, flow_id, headers),
        headers={**headers, "Content-Type": "application/json"},
        json={
            "input_value": input_value,
            "input_type": "chat",
            "output_type": output_type,
            "session_id": session_id,
            "tweaks": tweaks,
        },
        timeout=timeout_seconds,
    )
    response_hash = sha256(response.content).hexdigest()
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("langflow_authoring_response_invalid")
    return response.status_code, response_hash, payload


def _guard_failure_details(result: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for row in result.get("rows") or []:
        if not isinstance(row, dict):
            continue
        checks = row.get("checks") if isinstance(row.get("checks"), dict) else {}
        rows.append(
            {
                "case_id": str(row.get("case_id") or "")[:80],
                "error_code": str(row.get("error_code") or "")[:80],
                "error_stage": str(row.get("error_stage") or "")[:80],
                "error_detail_keys": [
                    str(value)[:80] for value in (row.get("error_detail_keys") or [])[:20]
                ],
                "failed_checks": sorted(
                    str(key)[:80] for key, passed in checks.items() if passed is not True
                ),
            }
        )
    return {"case_count": len(rows), "rows": rows}


def _safe_failure(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, AuthoringValidationError):
        return {
            "type": type(exc).__name__,
            "code": exc.code,
            "stage": exc.stage,
            "details": deepcopy(exc.details),
        }
    contract_code = str(getattr(exc, "code", "") or "")
    contract_stage = str(getattr(exc, "stage", "") or "")
    if contract_code and contract_stage:
        details = getattr(exc, "details", None)
        public_message = str(getattr(exc, "public_message", "") or "")
        return {
            "type": type(exc).__name__[:80],
            "code": contract_code[:80],
            "stage": contract_stage[:80],
            "details": {
                "detail_keys": sorted(str(key)[:80] for key in details)
                if isinstance(details, dict)
                else [],
                "public_message_sha256": sha256(public_message.encode("utf-8")).hexdigest()
                if public_message
                else "",
            },
        }
    runtime_token = str(exc or "")
    safe_runtime_chars = frozenset(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.:-"
    )
    if (
        runtime_token
        and len(runtime_token) <= 160
        and all(char in safe_runtime_chars for char in runtime_token)
    ):
        code, _, stage_suffix = runtime_token.partition(":")
        return {
            "type": type(exc).__name__[:80],
            "code": code[:80],
            "stage": stage_suffix[:80] or "validation_runtime",
            "details": {"runtime_token": runtime_token},
        }
    generic = _bounded_error(exc)
    return {
        **generic,
        "stage": "http_or_runtime",
        "details": {},
    }


_LOADER_CONTEXT_KEYS = {"contract_version", "ok", "stage", "domain_bundle"}
_LOADER_RUNTIME_BUNDLE_KEYS = {
    "contract_version",
    "domain_id",
    "environment",
    "revision",
    "source_mode",
    "catalog_sha256",
    "runtime_catalog",
    "package_sha256",
    "bundle_sha256",
}
_LOWER_HEX = frozenset("0123456789abcdef")


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in _LOWER_HEX for character in value)
    )


def _google_authoring_schema_binding_validation(
    bindings: dict[str, Any],
) -> dict[str, Any]:
    branch_rows: dict[str, Any] = {}
    for branch in AUTHORING_BRANCH_PURPOSES:
        evidence = bindings.get(branch) if isinstance(bindings.get(branch), dict) else {}
        authoritative_hash = str(evidence.get("authoritative_schema_sha256") or "")
        runtime_hash = str(evidence.get("runtime_output_schema_sha256") or "")
        checks = {
            "one_actual_invocation": int(evidence.get("invocation_count") or 0) == 1,
            "google_native_provider_binding": evidence.get("provider_schema_binding")
            == "google_native_json_schema",
            "binding_status_same": evidence.get("binding_status")
            == evidence.get("provider_schema_binding")
            == "google_native_json_schema",
            "provider_projection_exact": evidence.get("projection")
            == "google_supported_json_schema_subset.v6",
            "authoritative_schema_hash_valid": _is_sha256(authoritative_hash),
            "provider_schema_hash_valid": _is_sha256(
                evidence.get("provider_schema_sha256")
            ),
            "one_runtime_output_schema": int(
                evidence.get("runtime_output_schema_hash_distinct_count") or 0
            )
            == 1,
            "runtime_output_schema_hash_valid": _is_sha256(runtime_hash),
            "authoritative_matches_runtime": bool(authoritative_hash)
            and authoritative_hash == runtime_hash,
            "raw_prompt_absent": evidence.get("raw_prompt_persisted") is False,
            "raw_response_absent": evidence.get("raw_response_persisted") is False,
        }
        branch_rows[branch] = {
            "purpose": str(evidence.get("purpose") or ""),
            "provider_schema_binding": str(
                evidence.get("provider_schema_binding") or ""
            ),
            "binding_status": str(evidence.get("binding_status") or ""),
            "projection": str(evidence.get("projection") or ""),
            "authoritative_schema_sha256": authoritative_hash,
            "provider_schema_sha256": str(
                evidence.get("provider_schema_sha256") or ""
            ),
            "runtime_output_schema_sha256": runtime_hash,
            "checks": checks,
            "passed": all(checks.values()),
        }
    top_checks = {
        "three_branches_exact": set(bindings) == set(AUTHORING_BRANCH_PURPOSES),
        "all_branches_passed": all(row["passed"] for row in branch_rows.values()),
    }
    return {
        "branches": branch_rows,
        "checks": top_checks,
        "raw_prompt_persisted": False,
        "raw_response_persisted": False,
        "passed": all(top_checks.values()),
    }


def _validate_loader_runtime_bundle(
    context: Any,
    *,
    expected_domain_id: str,
    expected_environment: str,
) -> dict[str, Any]:
    """Validate the loader's runtime projection without treating it as storage.

    ``DomainBundleLoader`` deliberately emits ``domain.bundle.runtime.v1``.  It
    is a compact consumer-facing projection, not the persisted
    ``domain.package.v1`` envelope.  The HTTP harness validates that exact
    boundary here and validates the nested runtime catalog independently.
    """

    context_value = deepcopy(context) if isinstance(context, dict) else {}
    bundle = (
        deepcopy(context_value.get("domain_bundle"))
        if isinstance(context_value.get("domain_bundle"), dict)
        else {}
    )
    checks = {
        "context_object": isinstance(context, dict),
        "context_keys_exact": set(context_value) == _LOADER_CONTEXT_KEYS,
        "context_contract_exact": context_value.get("contract_version") == "pipeline.context.v1",
        "context_ok": context_value.get("ok") is True,
        "context_stage_exact": context_value.get("stage") == "domain_bundle",
        "bundle_object": isinstance(context_value.get("domain_bundle"), dict),
        "bundle_keys_exact": set(bundle) == _LOADER_RUNTIME_BUNDLE_KEYS,
        "bundle_contract_exact": bundle.get("contract_version") == "domain.bundle.runtime.v1",
        "source_mode_exact": bundle.get("source_mode") == "v6_active",
        "identity_exact": bundle.get("domain_id") == expected_domain_id
        and bundle.get("environment") == expected_environment,
        "package_sha256_valid": _is_sha256(bundle.get("package_sha256")),
        "bundle_sha256_valid": _is_sha256(bundle.get("bundle_sha256")),
        "catalog_sha256_valid": _is_sha256(bundle.get("catalog_sha256")),
    }

    catalog: dict[str, Any] = {}
    try:
        catalog = validate_runtime_catalog_v2(bundle.get("runtime_catalog") or {})
        checks["runtime_catalog_valid"] = True
    except Exception:
        checks["runtime_catalog_valid"] = False

    revision = bundle.get("revision")
    checks["revision_format_valid"] = (
        not isinstance(revision, bool)
        and (
            (isinstance(revision, int) and revision >= 1)
            or (isinstance(revision, str) and revision.isdigit() and int(revision) >= 1)
        )
    )
    checks["catalog_identity_exact"] = bool(catalog) and (
        catalog.get("domain_id") == expected_domain_id
        and catalog.get("environment") == expected_environment
    )
    checks["catalog_revision_exact"] = (
        checks["revision_format_valid"]
        and bool(catalog)
        and int(revision) == int(catalog.get("revision") or 0)
    )
    checks["catalog_hash_exact"] = bool(catalog) and (
        bundle.get("catalog_sha256") == catalog.get("catalog_sha256")
    )

    failed_checks = sorted(name for name, passed in checks.items() if passed is not True)
    if failed_checks:
        raise AuthoringValidationError(
            code="loader_runtime_projection_invalid",
            stage="loader_roundtrip",
            details={"failed_checks": failed_checks},
        )

    return {**bundle, "runtime_catalog": catalog}


def _loader_roundtrip(
    *,
    mongo_uri: str,
    database_name: str,
    domain_id: str,
    environment: str,
) -> dict[str, Any]:
    from lfx.custom.eval import eval_custom_component_code

    source = (ROOT / "langflow_components" / "data_analysis" / "domain_bundle_loader.py").read_text(encoding="utf-8")
    component_cls = eval_custom_component_code(source)
    component = component_cls()
    component.domain_id = domain_id
    component.environment = environment
    component.metadata_source_mode = "v6_active"
    component.inline_domain_bundle = None
    component.mongo_uri = mongo_uri
    component.mongo_database = database_name
    component.active_collection = "agent_v6_metadata_active"
    component.bundle_collection = "agent_v6_metadata_bundles"
    component.mongo_timeout_ms = 10000
    output = component.load_bundle()
    context = getattr(output, "data", output)
    runtime_bundle = _validate_loader_runtime_bundle(
        context,
        expected_domain_id=domain_id,
        expected_environment=environment,
    )
    return {
        "ok": bool(context.get("ok")),
        "stage": context.get("stage"),
        "domain_id": runtime_bundle.get("domain_id"),
        "environment": runtime_bundle.get("environment"),
        "revision": runtime_bundle.get("revision"),
        "package_sha256": runtime_bundle.get("package_sha256"),
        "bundle_sha256": runtime_bundle.get("bundle_sha256"),
        "catalog_sha256": runtime_bundle.get("catalog_sha256"),
    }


def _active_package(database: Any, *, domain_id: str, environment: str) -> tuple[dict[str, Any], dict[str, Any]]:
    pointer = database["agent_v6_metadata_active"].find_one(
        {"_id": f"active:{environment}:{domain_id}"}
    ) or {}
    if not pointer:
        return {}, {}
    bundle = database["agent_v6_metadata_bundles"].find_one(
        {"_id": f"bundle:{str(pointer.get('bundle_sha256') or '')}"}
    ) or {}
    if not bundle:
        raise RuntimeError("active_bundle_missing")
    package = validate_domain_package({key: value for key, value in bundle.items() if key != "_id"})
    pointer_checks = {
        "identity_exact": package.get("domain_id") == domain_id
        and package.get("environment") == environment,
        "revision_exact": int(pointer.get("revision") or 0) == int(package.get("revision") or 0),
        "package_hash_exact": pointer.get("package_sha256") == package.get("package_sha256"),
        "bundle_hash_exact": pointer.get("bundle_sha256") == package.get("bundle_sha256"),
    }
    if not all(pointer_checks.values()):
        raise RuntimeError("active_pointer_package_mismatch")
    return pointer, package


def _active_pointer_snapshot(
    database: Any, *, domain_id: str, environment: str = "production"
) -> dict[str, Any]:
    pointer = database["agent_v6_metadata_active"].find_one(
        {"_id": f"active:{environment}:{domain_id}"}
    ) or {}
    return {
        "environment": environment,
        "domain_id": domain_id,
        "present": bool(pointer),
        "sha256": sha256_json(pointer),
        "raw_pointer_persisted": False,
    }


def _package_evidence(package: dict[str, Any]) -> dict[str, Any]:
    catalog = package.get("runtime_catalog") if isinstance(package.get("runtime_catalog"), dict) else {}
    return {
        "revision": int(package.get("revision") or 0),
        "package_sha256": str(package.get("package_sha256") or ""),
        "bundle_sha256": str(package.get("bundle_sha256") or ""),
        "catalog_sha256": str(catalog.get("catalog_sha256") or ""),
        "section_hashes_sha256": sha256_json(_catalog_section_hashes(package)),
    }


def _semantic_completeness(package: dict[str, Any]) -> dict[str, Any]:
    catalog = package.get("runtime_catalog") if isinstance(package.get("runtime_catalog"), dict) else {}
    identity_sections: dict[str, dict[str, Any]] = {
        name: catalog.get(name) if isinstance(catalog.get(name), dict) else {}
        for name in ORDER_SALES_REQUIRED_MANIFEST
    }
    section_rows: dict[str, Any] = {}
    all_required_present = True
    exact_core_ids = True
    for section, required_values in ORDER_SALES_REQUIRED_MANIFEST.items():
        actual = sorted(str(key) for key in identity_sections[section])
        required = sorted(str(key) for key in required_values)
        missing = sorted(set(required) - set(actual))
        extra = sorted(set(actual) - set(required))
        exact_required = not missing
        if section in {"datasets", "fields", "metrics", "relations"}:
            exact_required = exact_required and not extra
            exact_core_ids = exact_core_ids and not extra
        all_required_present = all_required_present and not missing
        section_rows[section] = {
            "expected_count": len(required),
            "actual_count": len(actual),
            "missing_ids": missing,
            "extra_ids": extra,
            "passed": exact_required,
        }

    datasets = identity_sections["datasets"]
    refunds_fields = sorted(((datasets.get("refunds") or {}).get("fields") or {}).keys())
    targets_fields = sorted(((datasets.get("targets") or {}).get("fields") or {}).keys())
    relations = identity_sections["relations"]
    refunds_relation = relations.get("orders_refunds") if isinstance(relations.get("orders_refunds"), dict) else {}
    aliases = catalog.get("aliases") if isinstance(catalog.get("aliases"), dict) else {}
    metrics = catalog.get("metrics") if isinstance(catalog.get("metrics"), dict) else {}
    entity_groups = catalog.get("entity_groups") if isinstance(catalog.get("entity_groups"), dict) else {}
    aliases_blob = json.dumps(
        {"aliases": aliases, "metrics": metrics, "entity_groups": entity_groups},
        ensure_ascii=False,
        sort_keys=True,
    )
    prompt_extensions = (
        catalog.get("prompt_extensions") if isinstance(catalog.get("prompt_extensions"), dict) else {}
    )
    output_profile = catalog.get("output_profile") if isinstance(catalog.get("output_profile"), dict) else {}
    category_value_aliases: dict[str, set[str]] = {}
    for card in entity_groups.values():
        if not isinstance(card, dict) or card.get("target_field") != "CATEGORY":
            continue
        selection = card.get("selection") if isinstance(card.get("selection"), dict) else {}
        value = str(selection.get("value") or "")
        category_value_aliases.setdefault(value, set()).update(
            str(item) for item in card.get("aliases", []) if str(item)
        )
    capability_checks = {
        "refunds_fields_exact": refunds_fields == ["ORDER_ID", "PRODUCT_ID", "REFUND_AMOUNT"],
        "targets_fields_exact": targets_fields == ["PRODUCT_ID", "TARGET_AMOUNT", "TARGET_DATE"],
        "refund_relation_left_composite": refunds_relation.get("left_keys") == ["ORDER_ID", "PRODUCT_ID"],
        "refund_relation_right_composite": refunds_relation.get("right_keys") == ["ORDER_ID", "PRODUCT_ID"],
        "refund_relation_cardinality_registered": str(refunds_relation.get("cardinality") or "")
        in {"one_to_zero_or_one", "one_to_one_optional"},
        "net_sales_alias_registered": "순매출" in aliases_blob,
        "category_value_aliases_registered": any("전자" in alias for alias in category_value_aliases.get("A", set()))
        and any("생활" in alias for alias in category_value_aliases.get("B", set())),
        "prompt_extensions_present": bool(str(prompt_extensions.get("intent") or "").strip())
        and bool(str(prompt_extensions.get("answer") or "").strip()),
        "output_profile_present": bool(output_profile)
        and str(output_profile.get("currency") or "") == "KRW",
    }
    checks = {
        "required_ids_present": all_required_present,
        "core_ids_exact": exact_core_ids,
        "capabilities_complete": all(capability_checks.values()),
        "no_empty_required_sections": all(bool(identity_sections[name]) for name in identity_sections),
    }
    return {
        "required_manifest_sha256": ORDER_SALES_REQUIRED_MANIFEST_SHA256,
        "sections": section_rows,
        "capability_checks": capability_checks,
        "checks": checks,
        "passed": all(checks.values()) and all(row["passed"] for row in section_rows.values()),
    }


def _manufacturing_reference_catalog() -> dict[str, Any]:
    if not MANUFACTURING_COMPILED_CATALOG_PATH.is_file():
        raise RuntimeError("manufacturing_compiled_catalog_missing")
    raw = json.loads(MANUFACTURING_COMPILED_CATALOG_PATH.read_text(encoding="utf-8"))
    return validate_runtime_catalog_v2(raw)


def _manufacturing_required_manifest(catalog: dict[str, Any]) -> dict[str, list[str]]:
    manifest: dict[str, list[str]] = {}
    for section in MANUFACTURING_REQUIRED_SECTIONS:
        values = catalog.get(section)
        if not isinstance(values, dict) or not values:
            raise RuntimeError(f"manufacturing_reference_section_missing:{section}")
        manifest[section] = sorted(str(key) for key in values)
    return manifest


def _manufacturing_core_projection(catalog: dict[str, Any]) -> dict[str, Any]:
    """Select core executable semantics for hash-only completeness checks."""

    metrics = catalog.get("metrics") if isinstance(catalog.get("metrics"), dict) else {}
    recipes = catalog.get("recipes") if isinstance(catalog.get("recipes"), dict) else {}
    datasets = catalog.get("datasets") if isinstance(catalog.get("datasets"), dict) else {}
    fields = catalog.get("fields") if isinstance(catalog.get("fields"), dict) else {}
    orderings = catalog.get("orderings") if isinstance(catalog.get("orderings"), dict) else {}

    boh = metrics.get("WIP_BOH_QTY") if isinstance(metrics.get("WIP_BOH_QTY"), dict) else {}
    production_wip_join = (
        recipes.get("join.operation.production_wip")
        if isinstance(recipes.get("join.operation.production_wip"), dict)
        else {}
    )
    rank_top = recipes.get("rank.top_n") if isinstance(recipes.get("rank.top_n"), dict) else {}
    rank_bottom = (
        recipes.get("rank.bottom_n")
        if isinstance(recipes.get("rank.bottom_n"), dict)
        else {}
    )
    hold_recipe = (
        recipes.get("hold.oldest_current_history")
        if isinstance(recipes.get("hold.oldest_current_history"), dict)
        else {}
    )
    hold_template = (
        hold_recipe.get("default_operation_template")
        if isinstance(hold_recipe.get("default_operation_template"), dict)
        else {}
    )
    hold_steps = hold_template.get("steps") if isinstance(hold_template.get("steps"), list) else []
    project_steps = [
        deepcopy(step)
        for step in hold_steps
        if isinstance(step, dict) and step.get("op") == "project"
    ]
    return {
        "boh": {
            "source_binding": deepcopy(boh.get("source_binding") or {}),
            "temporal_contract": deepcopy(boh.get("temporal_contract") or {}),
        },
        "join": deepcopy(production_wip_join.get("default_operation_template") or {}),
        "rank": {
            "top": deepcopy(rank_top.get("default_operation_template") or {}),
            "bottom": deepcopy(rank_bottom.get("default_operation_template") or {}),
        },
        "projection": {
            "dataset_default_detail_fields": {
                str(dataset_id): list(card.get("default_detail_fields") or [])
                for dataset_id, card in sorted(datasets.items())
                if isinstance(card, dict)
            },
            "field_roles": {
                str(field_id): sorted(str(role) for role in (card.get("roles") or []))
                for field_id, card in sorted(fields.items())
                if isinstance(card, dict)
            },
            "hold_detail_steps": project_steps,
            "process_ordering": deepcopy(orderings.get("process") or {}),
        },
    }


def _registered_policy_structure(catalog: dict[str, Any]) -> dict[str, Any]:
    cards = catalog.get("specialized_functions")
    prompt_extensions = catalog.get("prompt_extensions")
    output_profile = catalog.get("output_profile")
    if not isinstance(cards, list):
        return {"function_count": 0, "cards_closed": False, "policy_maps_valid": False}

    forbidden_keys = {
        "code",
        "source",
        "source_code",
        "module",
        "module_path",
        "import_path",
        "python",
    }
    cards_closed = True
    for card in cards:
        limits = card.get("limits") if isinstance(card, dict) else None
        cards_closed = cards_closed and bool(
            isinstance(card, dict)
            and isinstance(card.get("function_id"), str)
            and card.get("function_id")
            and isinstance(card.get("version"), int)
            and card.get("version") > 0
            and card.get("execution_mode") == "registered_standalone"
            and _is_sha256(card.get("implementation_sha256"))
            and isinstance(card.get("input_schema"), dict)
            and isinstance(card.get("output_schema"), dict)
            and isinstance(card.get("required_fields"), list)
            and isinstance(limits, dict)
            and card.get("failure_policy") == "fail_closed"
            and not forbidden_keys.intersection(card)
        )
    return {
        "function_count": len(cards),
        "cards_closed": cards_closed,
        "policy_maps_valid": isinstance(prompt_extensions, dict)
        and isinstance(output_profile, dict),
    }


def _manufacturing_semantic_completeness(package: dict[str, Any]) -> dict[str, Any]:
    """Validate manufacturing meaning against the reviewed compiled catalog.

    Evidence contains counts and hashes only; required or missing ID lists are
    never emitted into the persisted HTTP validation report.
    """

    reference = _manufacturing_reference_catalog()
    required_manifest = _manufacturing_required_manifest(reference)
    catalog = package.get("runtime_catalog") if isinstance(package.get("runtime_catalog"), dict) else {}

    section_rows: dict[str, Any] = {}
    for section, required_ids in required_manifest.items():
        values = catalog.get(section) if isinstance(catalog.get(section), dict) else {}
        actual_ids = sorted(str(key) for key in values)
        missing_ids = sorted(set(required_ids) - set(actual_ids))
        extra_ids = sorted(set(actual_ids) - set(required_ids))
        section_rows[section] = {
            "expected_count": len(required_ids),
            "actual_count": len(actual_ids),
            "missing_count": len(missing_ids),
            "missing_ids_sha256": sha256_json(missing_ids),
            "extra_count": len(extra_ids),
            "extra_ids_sha256": sha256_json(extra_ids),
            "passed": not missing_ids,
        }

    expected_projection = _manufacturing_core_projection(reference)
    actual_projection = _manufacturing_core_projection(catalog)
    capability_projection_hashes = {
        name: {
            "expected_sha256": sha256_json(expected_projection[name]),
            "actual_sha256": sha256_json(actual_projection[name]),
        }
        for name in ("boh", "join", "rank", "projection")
    }
    registered_policy = _registered_policy_structure(catalog)
    capability_checks = {
        "boh_contract_exact": capability_projection_hashes["boh"]["expected_sha256"]
        == capability_projection_hashes["boh"]["actual_sha256"],
        "join_policy_exact": capability_projection_hashes["join"]["expected_sha256"]
        == capability_projection_hashes["join"]["actual_sha256"],
        "rank_policy_exact": capability_projection_hashes["rank"]["expected_sha256"]
        == capability_projection_hashes["rank"]["actual_sha256"],
        "projection_policy_exact": capability_projection_hashes["projection"]["expected_sha256"]
        == capability_projection_hashes["projection"]["actual_sha256"],
        "registered_function_cards_closed": registered_policy["cards_closed"] is True,
        "registered_policy_maps_valid": registered_policy["policy_maps_valid"] is True,
    }
    checks = {
        "required_semantic_ids_present": all(
            row["passed"] for row in section_rows.values()
        ),
        "core_capabilities_exact": all(capability_checks.values()),
        "runtime_catalog_valid": bool(catalog),
    }
    return {
        "reference_catalog_sha256": str(reference.get("catalog_sha256") or ""),
        "required_manifest_sha256": sha256_json(required_manifest),
        "sections": section_rows,
        "capability_projection_hashes": capability_projection_hashes,
        "capability_checks": capability_checks,
        "registered_function_count": registered_policy["function_count"],
        "checks": checks,
        "raw_id_lists_persisted": False,
        "passed": all(checks.values()),
    }


def _collection_snapshot(database: Any, names: Iterable[str]) -> dict[str, Any]:
    existing = set(database.list_collection_names())
    rows: dict[str, Any] = {}
    for name in sorted({str(item) for item in names if str(item).strip()}):
        key = sha256(name.encode("utf-8")).hexdigest()
        if name not in existing:
            rows[key] = {"exists": False, "document_count": 0, "indexes_sha256": ""}
            continue
        collection = database[name]
        indexes = collection.index_information()
        rows[key] = {
            "exists": True,
            "document_count": collection.count_documents({}),
            "indexes_sha256": sha256_json(indexes),
        }
    return rows


def _run_freeform_clarification_probe(
    *,
    client: requests.Session,
    headers: dict[str, str],
    server_url: str,
    flow_id: str,
    database: Any,
    database_name: str,
    domain_id: str,
    environment: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    """Prove incomplete freeform prose yields questions and no write material."""

    protected = [
        "agent_v6_pending_writes",
        "agent_v6_authoring_audit",
        "agent_v6_metadata_bundles",
        "agent_v6_metadata_active",
    ]
    before = _collection_snapshot(database, protected)
    sealed_source_text = _compose_domain_bootstrap_source(
        FREEFORM_CLARIFICATION_PROBE,
        FREEFORM_CLARIFICATION_DATASET_PROBE,
        FREEFORM_CLARIFICATION_MAIN_FILTER_PROBE,
    )
    source_sha256 = sha256(sealed_source_text.encode("utf-8")).hexdigest()
    context_tweaks = {
        "authoring_kind": "domain",
        "mode": "prepare",
        "source_grounding_mode": "freeform_llm",
        "domain_id": domain_id,
        "environment": environment,
        "bootstrap_fragment": True,
    }
    status, response_hash, payload = _post_run(
        client,
        headers,
        server_url,
        flow_id,
        input_value=FREEFORM_CLARIFICATION_PROBE,
        session_id=f"freeform-clarification-{uuid.uuid4().hex}",
        tweaks={
            "authoring_prompt_context_builder": context_tweaks,
            "bootstrap_dataset_prompt_context_builder": {
                **context_tweaks,
                "authoring_kind": "dataset",
            },
            "bootstrap_main_filter_prompt_context_builder": {
                **context_tweaks,
                "authoring_kind": "main_filter",
            },
            "dataset_source_input": {
                "input_value": FREEFORM_CLARIFICATION_DATASET_PROBE
            },
            "main_filter_source_input": {
                "input_value": FREEFORM_CLARIFICATION_MAIN_FILTER_PROBE
            },
            "metadata_authoring_engine": {
                "authoring_kind": "domain",
                "source_grounding_mode": "freeform_llm",
                "split_bootstrap": True,
                "metadata_contract_mode": "domain_package_v2",
                "domain_id": domain_id,
                "environment": environment,
                "revision_policy": "auto_next",
                "revision": 1,
                "mongo_database": database_name,
                "mode": "prepare",
                "dry_run": False,
            },
            "draft_language_model": {"temperature": 0.0, "stream": False},
        },
        timeout_seconds=timeout_seconds,
    )
    evidence = extract_authoring_evidence(payload)
    after = _collection_snapshot(database, protected)
    clarification = evidence.get("clarification_validation") or {}
    field_presence = evidence.get("response_field_presence") or {}
    before_count = sum(
        int(row.get("document_count") or 0)
        for row in before.values()
        if isinstance(row, dict)
    )
    after_count = sum(
        int(row.get("document_count") or 0)
        for row in after.values()
        if isinstance(row, dict)
    )
    checks = {
        "http_200": status == 200,
        "status_needs_clarification": evidence.get("status")
        == "needs_clarification",
        "response_hash_valid": evidence.get("response_hash_valid") is True,
        "terminal_equivalent": evidence.get("terminal_equivalent") is True,
        "identity_exact": evidence.get("domain_id") == domain_id
        and evidence.get("environment") == environment,
        "draft_llm_three": evidence.get("draft_llm_calls") == 3,
        "annotation_llm_zero": evidence.get("annotation_llm_calls") == 0,
        "repair_llm_zero": evidence.get("repair_llm_calls") == 0,
        "clarification_contract_exact": clarification.get("contract_version")
        == "metadata.authoring.clarification.v1",
        "source_hash_exact": clarification.get("source_sha256") == source_sha256,
        "proposal_sealed": _is_sha256(clarification.get("proposal_sha256")),
        "question_count_bounded": 1
        <= int(clarification.get("questions_count") or 0)
        <= 3,
        "missing_fields_reported": int(
            clarification.get("missing_fields_count") or 0
        )
        >= 1,
        "candidate_fields_absent": not field_presence.get("candidate_fields"),
        "package_fields_absent": not field_presence.get("package_fields"),
        "persist_fields_absent": not field_presence.get("persistence_fields"),
        "mongo_document_count_increase_zero": after_count == before_count,
        "collections_unchanged": before == after,
    }
    return {
        "source_text_sha256": source_sha256,
        "source_text_persisted": False,
        "http_response_sha256": response_hash,
        "clarification": clarification,
        "forbidden_response_fields": {
            key: list(field_presence.get(key) or [])
            for key in ("candidate_fields", "package_fields", "persistence_fields")
        },
        "mongo_document_count_before": before_count,
        "mongo_document_count_after": after_count,
        "mongo_write_count_increase": after_count - before_count,
        "collection_snapshot_before_sha256": sha256_json(before),
        "collection_snapshot_after_sha256": sha256_json(after),
        "diagnostics": {
            key: evidence.get(key)
            for key in (
                "status",
                "error_code",
                "error_stage",
                "error_reason",
                "error_type",
                "error_path",
                "error_message_sha256",
                "error_operator_sha256",
                "error_metric_id_sha256",
                "error_field_sha256",
                "manifest_error_code",
                "error_dataset_id_sha256",
                "error_detail_value_sha256",
                "error_candidate_count",
                "error_detail_index",
            )
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


def _legacy_collection_names(env: dict[str, str]) -> list[str]:
    v6_names = {
        "agent_v6_pending_writes",
        "agent_v6_authoring_audit",
        "agent_v6_metadata_bundles",
        "agent_v6_metadata_active",
        "agent_v6_result_store",
        "agent_v6_session_state",
    }
    candidates = {
        str(env.get(name) or "").strip()
        for name in (
            "MONGODB_DOMAIN_COLLECTION",
            "MONGODB_TABLE_CATALOG_COLLECTION",
            "MONGODB_MAIN_FLOW_FILTER_COLLECTION",
            "MONGODB_RESULT_COLLECTION",
            "MONGODB_SESSION_STATE_COLLECTION",
        )
    }
    candidates.discard("")
    result = sorted(candidates - v6_names)
    return result or ["agent_metadata_domains_v5_guard_probe"]


def _domain_flow_context_tweaks(
    *,
    mode: str,
    domain_id: str,
    environment: str,
    source_grounding_mode: str = "freeform_llm",
    split_prepare: bool,
    primary_overrides: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Build the three exact context gates used by the split Domain Flow.

    Preflight and execute requests close every LLM branch.  A normal freeform
    prepare opens all three branches, while the trusted-blueprint lane opens
    only the primary domain annotation branch.
    """

    normalized_mode = str(mode or "").strip().casefold()
    if normalized_mode not in {"prepare", "execute"}:
        raise ValueError("domain_context_mode_invalid")
    grounding_mode = str(source_grounding_mode or "").strip().casefold()
    if grounding_mode not in {"freeform_llm", "explicit_inventory"}:
        raise ValueError("domain_context_grounding_mode_invalid")
    base = {
        "domain_id": str(domain_id),
        "environment": str(environment),
        "source_grounding_mode": grounding_mode,
        "bootstrap_fragment": True,
    }
    result: dict[str, dict[str, Any]] = {}
    for node_id, kind in (
        ("authoring_prompt_context_builder", "domain"),
        ("bootstrap_dataset_prompt_context_builder", "dataset"),
        ("bootstrap_main_filter_prompt_context_builder", "main_filter"),
    ):
        branch_mode = (
            normalized_mode
            if kind == "domain" or normalized_mode == "execute" or split_prepare
            else "execute"
        )
        result[node_id] = {
            **base,
            "authoring_kind": kind,
            "mode": branch_mode,
        }
    if primary_overrides:
        result["authoring_prompt_context_builder"].update(
            deepcopy(primary_overrides)
        )
    return result


def _authoring_collection_guard_negatives(
    *,
    client: requests.Session,
    headers: dict[str, str],
    server_url: str,
    flow_id: str,
    database: Any,
    database_name: str,
    domain_id: str,
    environment: str,
    source_text: str,
    legacy_name: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    protected = [
        "agent_v6_pending_writes",
        "agent_v6_authoring_audit",
        "agent_v6_metadata_bundles",
        "agent_v6_metadata_active",
        legacy_name,
    ]
    cases = {
        "legacy_name": {"pending_collection": legacy_name},
        "role_swap": {
            "pending_collection": "agent_v6_authoring_audit",
            "audit_collection": "agent_v6_pending_writes",
        },
        "same_collection": {
            "pending_collection": "agent_v6_pending_writes",
            "audit_collection": "agent_v6_pending_writes",
        },
    }
    rows: list[dict[str, Any]] = []
    for case_id, overrides in cases.items():
        before = _collection_snapshot(database, protected)
        status, response_hash, payload = _post_run(
            client,
            headers,
            server_url,
            flow_id,
            input_value=source_text,
            session_id=f"collection-guard-{case_id}-{uuid.uuid4().hex}",
            tweaks={
                **_domain_flow_context_tweaks(
                    mode="execute",
                    domain_id=domain_id,
                    environment=environment,
                    split_prepare=False,
                ),
                "metadata_authoring_engine": {
                    "authoring_kind": "domain",
                    "metadata_contract_mode": "domain_package_v2",
                    "domain_id": domain_id,
                    "environment": environment,
                    "revision_policy": "auto_next",
                    "mongo_database": database_name,
                    "mode": "prepare",
                    "dry_run": False,
                    **overrides,
                },
                "draft_language_model": {"temperature": 0.0, "stream": False},
            },
            timeout_seconds=timeout_seconds,
        )
        evidence = extract_authoring_evidence(payload)
        after = _collection_snapshot(database, protected)
        checks = {
            "http_200": status == 200,
            "status_error": evidence.get("status") == "error",
            "policy_error": evidence.get("error_code") == "metadata_policy_error",
            "store_config_stage": evidence.get("error_stage") == "metadata_store_config",
            "no_llm_calls": evidence.get("draft_llm_calls") == 0
            and evidence.get("annotation_llm_calls") == 0
            and evidence.get("repair_llm_calls") == 0,
            "collections_unchanged": before == after,
        }
        rows.append(
            {
                "case_id": case_id,
                "override_sha256": sha256_json(overrides),
                "http_response_sha256": response_hash,
                "error_code": evidence.get("error_code"),
                "error_stage": evidence.get("error_stage"),
                "error_detail_keys": evidence.get("error_detail_keys"),
                "error_message_sha256": evidence.get("error_message_sha256"),
                "checks": checks,
                "passed": all(checks.values()),
            }
        )
    return {
        "case_count": len(rows),
        "rows": rows,
        "passed": all(row["passed"] for row in rows),
    }


def _blueprint_guard_http_negatives(
    *,
    client: requests.Session,
    headers: dict[str, str],
    server_url: str,
    flow_id: str,
    database: Any,
    database_name: str,
    domain_id: str,
    environment: str,
    source_text: str,
    blueprint: dict[str, Any],
    blueprint_pin: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    """Prove admin blueprint failures stop before Gemini and MongoDB."""

    protected = [
        "agent_v6_pending_writes",
        "agent_v6_authoring_audit",
        "agent_v6_metadata_bundles",
        "agent_v6_metadata_active",
    ]
    compact = json.dumps(blueprint, ensure_ascii=False, separators=(",", ":"))
    wrong_pin = "0" * 64 if blueprint_pin != "0" * 64 else "1" * 64
    simple_tamper = deepcopy(blueprint)
    simple_tamper["executable"]["output_profile"]["default_row_limit"] = (
        int(simple_tamper["executable"]["output_profile"].get("default_row_limit") or 20)
        + 1
    )
    recomputed_tamper = deepcopy(simple_tamper)
    recomputed_tamper["executable_sha256"] = sha256_json(recomputed_tamper["executable"])
    recomputed_tamper["blueprint_sha256"] = compute_blueprint_sha256(recomputed_tamper)
    cases = (
        (
            "missing_external_pin",
            {"trusted_blueprint_json": compact},
            "metadata_blueprint_invalid",
        ),
        (
            "wrong_external_pin",
            {"trusted_blueprint_json": compact, "trusted_blueprint_sha256": wrong_pin},
            "metadata_dependency_error",
        ),
        (
            "simple_executable_tamper",
            {
                "trusted_blueprint_json": json.dumps(
                    simple_tamper, ensure_ascii=False, separators=(",", ":")
                ),
                "trusted_blueprint_sha256": blueprint_pin,
            },
            "metadata_dependency_error",
        ),
        (
            "recomputed_executable_tamper",
            {
                "trusted_blueprint_json": json.dumps(
                    recomputed_tamper, ensure_ascii=False, separators=(",", ":")
                ),
                "trusted_blueprint_sha256": blueprint_pin,
            },
            "metadata_dependency_error",
        ),
    )
    rows: list[dict[str, Any]] = []
    for case_id, admin_tweaks, expected_code in cases:
        before = _collection_snapshot(database, protected)
        status, response_hash, payload = _post_run(
            client,
            headers,
            server_url,
            flow_id,
            input_value=source_text,
            session_id=f"blueprint-guard-{case_id}-{uuid.uuid4().hex}",
            tweaks={
                **_domain_flow_context_tweaks(
                    mode="execute",
                    domain_id=domain_id,
                    environment=environment,
                    source_grounding_mode="explicit_inventory",
                    split_prepare=False,
                ),
                "metadata_authoring_engine": {
                    "authoring_kind": "domain",
                    "metadata_contract_mode": "domain_package_v2",
                    "domain_id": domain_id,
                    "environment": environment,
                    "source_grounding_mode": "explicit_inventory",
                    "revision_policy": "auto_next",
                    "mongo_database": database_name,
                    "mode": "prepare",
                    "dry_run": False,
                    **admin_tweaks,
                },
                "draft_language_model": {"temperature": 0.0, "stream": False},
            },
            timeout_seconds=timeout_seconds,
        )
        evidence = extract_authoring_evidence(payload)
        after = _collection_snapshot(database, protected)
        checks = {
            "http_200": status == 200,
            "status_error": evidence.get("status") == "error",
            "error_code_exact": evidence.get("error_code") == expected_code,
            "all_llm_calls_zero": evidence.get("draft_llm_calls") == 0
            and evidence.get("annotation_llm_calls") == 0
            and evidence.get("repair_llm_calls") == 0,
            "collections_unchanged": before == after,
        }
        rows.append(
            {
                "case_id": case_id,
                "admin_tweaks_sha256": sha256_json(admin_tweaks),
                "http_response_sha256": response_hash,
                "error_code": evidence.get("error_code"),
                "error_stage": evidence.get("error_stage"),
                "error_reason": evidence.get("error_reason"),
                "error_detail_keys": evidence.get("error_detail_keys"),
                "error_message_sha256": evidence.get("error_message_sha256"),
                "blueprint_payload_persisted": False,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )
    return {
        "case_count": len(rows),
        "rows": rows,
        "passed": all(row["passed"] for row in rows),
    }


def _run_authoring_cycle(
    *,
    client: requests.Session,
    headers: dict[str, str],
    server_url: str,
    flow_id: str,
    database: Any,
    database_name: str,
    domain_id: str,
    environment: str,
    authoring_kind: str,
    source_text: str,
    nonce: str,
    timeout_seconds: int,
    policy_overlays: dict[str, Any] | None = None,
    source_grounding_mode: str = "freeform_llm",
    trusted_blueprint: dict[str, Any] | None = None,
    trusted_blueprint_pin: str = "",
    input_node_tweaks: dict[str, dict[str, Any]] | None = None,
    expected_source_text: str | None = None,
    semantic_completeness_fn: Any = _semantic_completeness,
    require_owned_change: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    grounding_mode = str(source_grounding_mode or "").strip().casefold()
    if grounding_mode not in {"freeform_llm", "explicit_inventory"}:
        raise RuntimeError("source_grounding_mode_invalid")
    blueprint_supplied = isinstance(trusted_blueprint, dict) and bool(
        trusted_blueprint_pin
    )
    blueprint_partial = isinstance(trusted_blueprint, dict) != bool(trusted_blueprint_pin)
    if blueprint_partial:
        raise RuntimeError("trusted_blueprint_admin_config_incomplete")
    if blueprint_supplied and str(authoring_kind or "").strip().casefold() != "domain":
        raise RuntimeError("trusted_blueprint_domain_only")
    blueprint_configured = (
        str(authoring_kind or "").strip().casefold() == "domain" and blueprint_supplied
    )
    if blueprint_configured and grounding_mode != "explicit_inventory":
        raise RuntimeError("trusted_blueprint_requires_explicit_inventory")
    _before_pointer, before_package = _active_package(
        database,
        domain_id=domain_id,
        environment=environment,
    )
    before_revision = int(before_package.get("revision") or 0)
    target_revision = before_revision + 1
    subject_id = "metadata-approver:test"
    session_id = f"v6-authoring-{authoring_kind}-{nonce}"
    effective_source_text = (
        str(expected_source_text)
        if expected_source_text is not None
        else source_text
    )
    source_sha256 = sha256(effective_source_text.encode("utf-8")).hexdigest()
    source_node_tweaks = deepcopy(input_node_tweaks or {})
    reserved_tweak_ids = {
        "metadata_authoring_engine",
        "authoring_prompt_context_builder",
        "draft_language_model",
    }
    if reserved_tweak_ids.intersection(source_node_tweaks):
        raise RuntimeError("source_input_tweak_overrides_control_node")
    if any(
        not isinstance(node_id, str)
        or not node_id.strip()
        or not isinstance(values, dict)
        or set(values) != {"input_value"}
        or not isinstance(values.get("input_value"), str)
        or not values.get("input_value", "").strip()
        for node_id, values in source_node_tweaks.items()
    ):
        raise RuntimeError("source_input_tweak_invalid")
    engine_tweaks: dict[str, Any] = {
        "authoring_kind": authoring_kind,
        "metadata_contract_mode": "domain_package_v2",
        "domain_id": domain_id,
        "environment": environment,
        "source_grounding_mode": grounding_mode,
        "revision_policy": "auto_next",
        "revision": target_revision,
        "mongo_database": database_name,
        "dry_run": False,
    }
    if authoring_kind == "domain" and blueprint_configured:
        engine_tweaks.update(
            {
                "trusted_blueprint_json": json.dumps(
                    trusted_blueprint,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                "trusted_blueprint_sha256": trusted_blueprint_pin,
            }
        )
    prompt_context_tweaks: dict[str, Any] = {
        "authoring_kind": authoring_kind,
        "source_grounding_mode": grounding_mode,
        "domain_id": domain_id,
        "environment": environment,
    }
    if authoring_kind == "domain" and blueprint_configured:
        prompt_context_tweaks.update(
            {
                "trusted_blueprint_json": json.dumps(
                    trusted_blueprint,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                "trusted_blueprint_sha256": trusted_blueprint_pin,
            }
        )
    if policy_overlays:
        engine_tweaks.update(deepcopy(policy_overlays))
    common_tweaks = {
        **source_node_tweaks,
        "metadata_authoring_engine": engine_tweaks,
    }
    if authoring_kind != "domain_policy":
        common_tweaks["draft_language_model"] = {
            "temperature": 0.0,
            "stream": False,
        }

    if authoring_kind == "domain":
        prepare_context_tweaks = _domain_flow_context_tweaks(
            mode="prepare",
            domain_id=domain_id,
            environment=environment,
            source_grounding_mode=grounding_mode,
            split_prepare=not blueprint_configured and grounding_mode == "freeform_llm",
            primary_overrides=prompt_context_tweaks,
        )
    else:
        prepare_context_tweaks = {
            "authoring_prompt_context_builder": {
                **prompt_context_tweaks,
                "mode": "prepare",
            }
        }

    prepare_status, prepare_http_hash, prepare_payload = _post_run(
        client,
        headers,
        server_url,
        flow_id,
        input_value=source_text,
        session_id=session_id,
        tweaks={
            **common_tweaks,
            **prepare_context_tweaks,
            "metadata_authoring_engine": {
                **engine_tweaks,
                "mode": "prepare",
            },
        },
        timeout_seconds=timeout_seconds,
    )
    prepare = extract_authoring_evidence(prepare_payload)
    if not (
        prepare_status == 200
        and prepare.get("status") == "ok"
        and prepare.get("stage") == "prepared"
        and prepare.get("response_hash_valid") is True
    ):
        raise AuthoringValidationError(
            code="authoring_prepare_failed",
            stage=authoring_kind,
            details={
                "http_200": prepare_status == 200,
                "status": str(prepare.get("status") or ""),
                "response_stage": str(prepare.get("stage") or ""),
                "error_code": str(prepare.get("error_code") or ""),
                "error_stage": str(prepare.get("error_stage") or ""),
                "error_type": str(prepare.get("error_type") or ""),
                "error_location": str(prepare.get("error_location") or ""),
                "error_reason": str(prepare.get("error_reason") or ""),
                "error_framing_reason": str(
                    prepare.get("error_framing_reason") or ""
                ),
                "error_input_name": str(prepare.get("error_input_name") or ""),
                "error_expected_purpose": str(
                    prepare.get("error_expected_purpose") or ""
                ),
                "error_response_bytes": int(
                    prepare.get("error_response_bytes") or 0
                ),
                "error_path": str(prepare.get("error_path") or ""),
                "error_detail_keys": list(prepare.get("error_detail_keys") or []),
                "error_message_sha256": str(
                    prepare.get("error_message_sha256") or ""
                ),
                "error_operator_sha256": str(
                    prepare.get("error_operator_sha256") or ""
                ),
                "error_metric_id_sha256": str(
                    prepare.get("error_metric_id_sha256") or ""
                ),
                "error_field_sha256": str(
                    prepare.get("error_field_sha256") or ""
                ),
                "manifest_error_code": str(
                    prepare.get("manifest_error_code") or ""
                ),
                "error_dataset_id_sha256": str(
                    prepare.get("error_dataset_id_sha256") or ""
                ),
                "error_detail_value_sha256": str(
                    prepare.get("error_detail_value_sha256") or ""
                ),
                "error_field_id_sha256": str(
                    prepare.get("error_field_id_sha256") or ""
                ),
                "error_physical_column_sha256": str(
                    prepare.get("error_physical_column_sha256") or ""
                ),
                "error_candidate_count": int(
                    prepare.get("error_candidate_count") or 0
                ),
                "error_detail_index": int(prepare.get("error_detail_index") or 0),
                "response_hash_valid": prepare.get("response_hash_valid") is True,
                "draft_llm_calls": int(prepare.get("draft_llm_calls") or 0),
                "annotation_llm_calls": int(prepare.get("annotation_llm_calls") or 0),
                "repair_llm_calls": int(prepare.get("repair_llm_calls") or 0),
                "llm_invocation_count": int(
                    prepare.get("llm_invocation_count") or 0
                ),
                "llm_response_byte_sizes": list(
                    prepare.get("llm_response_byte_sizes") or []
                ),
                "clarification_branches": list(
                    (prepare.get("clarification_validation") or {}).get("branches")
                    or []
                ),
                "clarification_missing_fields": list(
                    (prepare.get("clarification_validation") or {}).get(
                        "safe_missing_fields"
                    )
                    or []
                ),
            },
        )
    candidate_id = prepare["candidate_id"]
    candidate_hash = prepare["candidate_sha256"]
    pending_wrapper = database["agent_v6_pending_writes"].find_one({"_id": candidate_id}) or {}
    pending_payload, pending = _pending_evidence(
        pending_wrapper,
        authoring_kind=authoring_kind,
        domain_id=domain_id,
        environment=environment,
        target_revision=target_revision,
        base_package=before_package,
    )

    approval_event = _build_approval_event(
        nonce=f"{authoring_kind}-{nonce}",
        candidate_id=candidate_id,
        candidate_sha256=candidate_hash,
        subject_id=subject_id,
    )
    approval_sha256 = sha256_json(approval_event)
    approved = database["agent_v6_pending_writes"].update_one(
        {
            "_id": candidate_id,
            "workflow_status": "prepared",
            "pending_payload_sha256": pending_wrapper.get("pending_payload_sha256"),
        },
        {
            "$set": {
                "workflow_status": "approved",
                "approval_event_sha256": approval_sha256,
                "approval_event_id": approval_event["event_id"],
            }
        },
    )
    approved_wrapper = database["agent_v6_pending_writes"].find_one({"_id": candidate_id}) or {}
    approval_checks = {
        "approval_schema_exact": validate_contract(
            deepcopy(approval_event),
            "approval-event.schema.json",
            stage="approval_event_validation",
            error_code="approval_contract_error",
        )
        == approval_event,
        "transitioned_once": approved.modified_count == 1,
        "workflow_approved": approved_wrapper.get("workflow_status") == "approved",
        "pending_payload_immutable": approved_wrapper.get("pending_payload") == pending_payload,
        "pending_payload_seal_immutable": approved_wrapper.get("pending_payload_sha256")
        == pending_wrapper.get("pending_payload_sha256"),
        "event_hash_exact": approved_wrapper.get("approval_event_sha256") == approval_sha256,
        "event_id_exact": approved_wrapper.get("approval_event_id") == approval_event["event_id"],
    }
    if not all(approval_checks.values()):
        raise AuthoringValidationError(
            code="approval_transition_validation_failed",
            stage=authoring_kind,
            details={
                "failed_checks": sorted(
                    str(key) for key, passed in approval_checks.items() if passed is not True
                )
            },
        )

    tamper_rows: list[dict[str, Any]] = []
    for mutated_field, tampered_event in _tampered_approval_events(approval_event).items():
        if authoring_kind == "domain":
            tamper_context_tweaks = _domain_flow_context_tweaks(
                mode="execute",
                domain_id=domain_id,
                environment=environment,
                source_grounding_mode=grounding_mode,
                split_prepare=False,
                primary_overrides=prompt_context_tweaks,
            )
        else:
            tamper_context_tweaks = {
                "authoring_prompt_context_builder": {
                    **prompt_context_tweaks,
                    "mode": "execute",
                }
            }
        tamper_status, tamper_http_hash, tamper_payload = _post_run(
            client,
            headers,
            server_url,
            flow_id,
            input_value="변조 방지 승인 이벤트 검사",
            session_id=f"{session_id}-tamper-{mutated_field}",
            tweaks={
                **common_tweaks,
                **tamper_context_tweaks,
                "metadata_authoring_engine": {
                    **engine_tweaks,
                    "mode": "execute",
                    "approval_event_json": json.dumps(
                        tampered_event,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                },
            },
            timeout_seconds=timeout_seconds,
        )
        tamper_response = extract_authoring_evidence(tamper_payload)
        tamper_wrapper = database["agent_v6_pending_writes"].find_one({"_id": candidate_id}) or {}
        _tamper_pointer, tamper_active_package = _active_package(
            database,
            domain_id=domain_id,
            environment=environment,
        )
        tamper_checks = {
            "http_200": tamper_status == 200,
            "status_error": tamper_response.get("status") == "error",
            "approval_hash_mismatch": tamper_response.get("error_code") == "approval_hash_mismatch",
            "approval_event_seal_invariant": tamper_response.get("error_invariant")
            == "approval_event_external_seal",
            "no_llm_calls": tamper_response.get("draft_llm_calls") == 0
            and tamper_response.get("annotation_llm_calls") == 0
            and tamper_response.get("repair_llm_calls") == 0,
            "wrapper_still_approved": tamper_wrapper.get("workflow_status") == "approved",
            "wrapper_seal_unchanged": tamper_wrapper.get("approval_event_sha256") == approval_sha256,
            "pending_payload_unchanged": tamper_wrapper.get("pending_payload") == pending_payload,
            "active_revision_unchanged": int(tamper_active_package.get("revision") or 0)
            == before_revision,
            "active_package_unchanged": str(tamper_active_package.get("package_sha256") or "")
            == str(before_package.get("package_sha256") or ""),
        }
        tamper_rows.append(
            {
                "mutated_field": mutated_field,
                "event_sha256": sha256_json(tampered_event),
                "http_response_sha256": tamper_http_hash,
                "error_code": tamper_response.get("error_code"),
                "error_stage": tamper_response.get("error_stage"),
                "error_invariant": tamper_response.get("error_invariant"),
                "error_message_sha256": tamper_response.get("error_message_sha256"),
                "raw_event_persisted": False,
                "checks": tamper_checks,
                "passed": all(tamper_checks.values()),
            }
        )
    if not all(row["passed"] for row in tamper_rows):
        raise AuthoringValidationError(
            code="approval_tamper_validation_failed",
            stage=authoring_kind,
            details={
                "case_count": len(tamper_rows),
                "rows": [
                    {
                        "mutated_field": str(row.get("mutated_field") or "")[:80],
                        "error_code": str(row.get("error_code") or "")[:80],
                        "error_stage": str(row.get("error_stage") or "")[:80],
                        "error_invariant": str(row.get("error_invariant") or "")[:80],
                        "error_message_sha256": str(
                            row.get("error_message_sha256") or ""
                        ),
                        "failed_checks": sorted(
                            str(key)[:80]
                            for key, passed in (row.get("checks") or {}).items()
                            if passed is not True
                        ),
                    }
                    for row in tamper_rows
                ],
            },
        )

    if authoring_kind == "domain":
        execute_context_tweaks = _domain_flow_context_tweaks(
            mode="execute",
            domain_id=domain_id,
            environment=environment,
            source_grounding_mode=grounding_mode,
            split_prepare=False,
            primary_overrides=prompt_context_tweaks,
        )
    else:
        execute_context_tweaks = {
            "authoring_prompt_context_builder": {
                **prompt_context_tweaks,
                "mode": "execute",
            }
        }
    execute_status, execute_http_hash, execute_payload = _post_run(
        client,
        headers,
        server_url,
        flow_id,
        input_value="승인 이벤트에 결합된 메타데이터 후보를 실행하세요.",
        session_id=session_id,
        tweaks={
            **common_tweaks,
            **execute_context_tweaks,
            "metadata_authoring_engine": {
                **engine_tweaks,
                "mode": "execute",
                "approval_event_json": json.dumps(
                    approval_event,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
            },
        },
        timeout_seconds=timeout_seconds,
    )
    execute = extract_authoring_evidence(execute_payload)
    active_pointer, after_package = _active_package(
        database,
        domain_id=domain_id,
        environment=environment,
    )
    prepared_package = validate_domain_package(
        deepcopy((pending_payload.get("hash_material") or {}).get("domain_package") or {})
    )
    prepared_semantic_completeness = (
        semantic_completeness_fn(prepared_package)
        if semantic_completeness_fn is not None
        else {"not_applicable": True, "passed": True}
    )
    committed_semantic_completeness = (
        semantic_completeness_fn(after_package)
        if semantic_completeness_fn is not None
        else {"not_applicable": True, "passed": True}
    )
    expected_calls = _expected_prepare_llm_calls(
        authoring_kind,
        source_text,
        source_grounding_mode=grounding_mode,
        trusted_blueprint_configured=blueprint_configured,
    )
    proposal_validation = prepare.get("authoring_proposal_validation") or {}
    effective_proposal_draft_sha256 = str(
        proposal_validation.get("expanded_draft_sha256")
        or proposal_validation.get("draft_sha256")
        or ""
    )
    freeform_proposal_required = (
        grounding_mode == "freeform_llm"
        and authoring_kind in {"domain", "dataset", "main_filter"}
    )
    proposal_checks = {
        "validation_contract_exact": proposal_validation.get("contract_version")
        == "metadata.authoring.proposal.validation.v1",
        "proposal_contract_exact": proposal_validation.get(
            "proposal_contract_version"
        )
        == "metadata.authoring.proposal.v1",
        "status_complete": proposal_validation.get("status") == "complete",
        "source_hash_exact": proposal_validation.get("source_sha256")
        == source_sha256,
        "proposal_sealed": _is_sha256(proposal_validation.get("proposal_sha256")),
        "draft_sealed": _is_sha256(proposal_validation.get("draft_sha256")),
        "expanded_draft_sealed": authoring_kind not in {"dataset", "main_filter"}
        or _is_sha256(proposal_validation.get("expanded_draft_sha256")),
    }
    split_proposal_checks: dict[str, bool] = {}
    if (
        freeform_proposal_required
        and authoring_kind == "domain"
        and not blueprint_configured
    ):
        split_proposals = prepare.get("authoring_proposals_validation") or {}
        split_source_texts = {
            "domain": str(
                (source_node_tweaks.get("chat_input") or {}).get("input_value")
                or source_text
            ),
            "dataset": str(
                (source_node_tweaks.get("dataset_source_input") or {}).get(
                    "input_value"
                )
                or ""
            ),
            "main_filter": str(
                (source_node_tweaks.get("main_filter_source_input") or {}).get(
                    "input_value"
                )
                or ""
            ),
        }
        split_proposal_checks["branches_exact"] = set(split_proposals) == set(
            split_source_texts
        )
        for branch, branch_source_text in split_source_texts.items():
            branch_proposal = split_proposals.get(branch) or {}
            prefix = f"{branch}_"
            split_proposal_checks[prefix + "validation_contract_exact"] = (
                branch_proposal.get("contract_version")
                == "metadata.authoring.proposal.validation.v1"
            )
            split_proposal_checks[prefix + "proposal_contract_exact"] = (
                branch_proposal.get("proposal_contract_version")
                == "metadata.authoring.proposal.v1"
            )
            split_proposal_checks[prefix + "status_complete"] = (
                branch_proposal.get("status") == "complete"
            )
            split_proposal_checks[prefix + "source_hash_exact"] = (
                branch_proposal.get("source_sha256")
                == sha256(branch_source_text.encode("utf-8")).hexdigest()
            )
            split_proposal_checks[prefix + "proposal_sealed"] = _is_sha256(
                branch_proposal.get("proposal_sha256")
            )
            split_proposal_checks[prefix + "draft_sealed"] = _is_sha256(
                branch_proposal.get("draft_sha256")
            )
    prepare_checks = {
        "http_200": prepare_status == 200,
        "status_prepared": prepare.get("status") == "ok" and prepare.get("stage") == "prepared",
        "authoring_kind_exact": prepare.get("authoring_kind") == authoring_kind,
        "response_hash_valid": prepare.get("response_hash_valid") is True,
        "terminal_equivalent": prepare.get("terminal_equivalent") is True,
        "contract_mode_v2": prepare.get("metadata_contract_mode") == "domain_package_v2",
        "identity_exact": prepare.get("domain_id") == domain_id and prepare.get("environment") == environment,
        "revision_exact": int(prepare.get("revision") or 0) == target_revision,
        "draft_llm_exact": prepare.get("draft_llm_calls") == expected_calls["draft"],
        "annotation_llm_exact": prepare.get("annotation_llm_calls")
        == expected_calls["annotation"],
        "repair_llm_zero": prepare.get("repair_llm_calls") == expected_calls["repair"],
        "section_ownership_reported": authoring_kind == "domain"
        or prepare.get("unchanged_sections_all") is True,
    }
    execute_checks = {
        "http_200": execute_status == 200,
        "status_committed": execute.get("status") == "ok" and execute.get("stage") == "committed",
        "authoring_kind_exact": execute.get("authoring_kind") == authoring_kind,
        "response_hash_valid": execute.get("response_hash_valid") is True,
        "terminal_equivalent": execute.get("terminal_equivalent") is True,
        "draft_llm_zero": execute.get("draft_llm_calls") == 0,
        "annotation_llm_zero": execute.get("annotation_llm_calls") == 0,
        "repair_llm_zero": execute.get("repair_llm_calls") == 0,
        "candidate_hash_exact": execute.get("candidate_sha256") == candidate_hash,
        "revision_exact": int(execute.get("revision") or 0) == target_revision,
    }
    continuity_checks = {
        "fresh_base_for_domain": authoring_kind != "domain" or before_revision == 0,
        "revision_contiguous": int(after_package.get("revision") or 0) == target_revision,
        "active_revision_exact": int(active_pointer.get("revision") or 0) == target_revision,
        "prepared_package_exact": after_package.get("package_sha256") == prepared_package.get("package_sha256"),
        "prepared_bundle_exact": after_package.get("bundle_sha256") == prepared_package.get("bundle_sha256"),
        "response_package_exact": execute.get("package_sha256") == after_package.get("package_sha256"),
        "response_bundle_exact": execute.get("bundle_sha256") == after_package.get("bundle_sha256"),
        "response_catalog_exact": execute.get("catalog_sha256")
        == (after_package.get("runtime_catalog") or {}).get("catalog_sha256"),
        "package_hash_changed": not before_package
        or before_package.get("package_sha256") != after_package.get("package_sha256"),
    }
    blueprint_checks: dict[str, bool] = {}
    if authoring_kind == "domain" and blueprint_configured:
        blueprint_validation = prepare.get("trusted_blueprint_validation") or {}
        blueprint_checks = {
            "contract_exact": blueprint_validation.get("contract_version")
            == "metadata.blueprint.validation.v1",
            "external_pin_exact": blueprint_validation.get("blueprint_sha256")
            == trusted_blueprint_pin,
            "executable_hash_exact": blueprint_validation.get("executable_sha256")
            == (trusted_blueprint or {}).get("executable_sha256"),
            "annotation_proposal_sealed": len(
                str(blueprint_validation.get("annotation_proposal_sha256") or "")
            )
            == 64,
            "external_pin_passed": blueprint_validation.get("external_pin") == "passed",
            "executable_immutable": blueprint_validation.get("executable_immutable")
            == "passed",
        }
    ownership = None
    if authoring_kind in PATCH_OWNERSHIP:
        ownership = _section_ownership_checks(
            before_package,
            after_package,
            authoring_kind=authoring_kind,
        )

    policy_checks: dict[str, bool] = {}
    if authoring_kind == "domain_policy":
        catalog = after_package.get("runtime_catalog") or {}
        functions = catalog.get("specialized_functions") if isinstance(catalog.get("specialized_functions"), list) else []
        expected_functions = json.loads(str((policy_overlays or {}).get("specialized_functions_json") or "[]"))
        expected_output = json.loads(str((policy_overlays or {}).get("output_profile_json") or "{}"))
        expected_function = expected_functions[0] if isinstance(expected_functions, list) and expected_functions else {}
        function = next(
            (
                item
                for item in functions
                if isinstance(item, dict)
                and item.get("function_id") == expected_function.get("function_id")
                and item.get("version") == expected_function.get("version")
            ),
            {},
        ) if expected_function else {}
        policy_checks = {
            "intent_overlay_exact": (catalog.get("prompt_extensions") or {}).get("intent")
            == str((policy_overlays or {}).get("intent_prompt_extension") or ""),
            "answer_overlay_exact": (catalog.get("prompt_extensions") or {}).get("answer")
            == str((policy_overlays or {}).get("answer_prompt_extension") or ""),
            "specialized_function_exact": bool(expected_function) and function == expected_function,
            "output_profile_overlay_exact": bool(expected_output)
            and all((catalog.get("output_profile") or {}).get(key) == value for key, value in expected_output.items()),
        }

    checks = {
        "prepare": all(prepare_checks.values()),
        "pending": pending.get("passed") is True,
        "approval": all(approval_checks.values()),
        "approval_tamper_negatives": all(row["passed"] for row in tamper_rows),
        "execute": all(execute_checks.values()),
        "continuity": all(continuity_checks.values()),
        "trusted_blueprint": not blueprint_checks or all(blueprint_checks.values()),
        "freeform_proposal": not freeform_proposal_required
        or all(proposal_checks.values()),
        "split_freeform_proposals": not split_proposal_checks
        or all(split_proposal_checks.values()),
        "freeform_grounding": grounding_mode != "freeform_llm"
        or authoring_kind == "domain_policy"
        or (
            (prepare.get("source_grounding_validation") or {}).get("mode")
            == "freeform_llm"
            and (prepare.get("source_grounding_validation") or {}).get(
                "source_sha256"
            )
            == source_sha256
            and (prepare.get("source_grounding_validation") or {}).get(
                "structured_proposal_sha256"
            )
            == effective_proposal_draft_sha256
        ),
        "ownership": ownership is None
        or (
            (ownership.get("checks") or {}).get("other_sections_unchanged") is True
            and (
                not require_owned_change
                or (ownership.get("checks") or {}).get("at_least_one_owned_section_changed") is True
            )
        ),
        "policy_overlay": not policy_checks or all(policy_checks.values()),
        "prepared_semantic_completeness": prepared_semantic_completeness.get("passed") is True,
        "committed_semantic_completeness": committed_semantic_completeness.get("passed") is True,
    }
    cycle = {
        "authoring_kind": authoring_kind,
        "source_grounding_mode": grounding_mode,
        "trusted_blueprint_configured": blueprint_configured,
        "flow_id_sha256": sha256(flow_id.encode("utf-8")).hexdigest(),
        "source_text_sha256": source_sha256,
        "source_input_node_hashes": {
            node_id: sha256(str(values["input_value"]).encode("utf-8")).hexdigest()
            for node_id, values in sorted(source_node_tweaks.items())
        },
        "source_text_persisted": False,
        "before": _package_evidence(before_package) if before_package else {"revision": 0},
        "target_revision": target_revision,
        "prepare_http_response_sha256": prepare_http_hash,
        "prepare": prepare,
        "prepare_checks": prepare_checks,
        "pending": pending,
        "approval": {
            "contract_version": approval_event["contract_version"],
            "event_sha256": approval_sha256,
            "event_id_sha256": sha256(approval_event["event_id"].encode("utf-8")).hexdigest(),
            "subject_id_sha256": sha256(approval_event["subject_id"].encode("utf-8")).hexdigest(),
            "idempotency_key_sha256": sha256(approval_event["idempotency_key"].encode("utf-8")).hexdigest(),
            "raw_event_persisted": False,
            "checks": approval_checks,
        },
        "approval_tamper_negatives": tamper_rows,
        "execute_http_response_sha256": execute_http_hash,
        "execute": execute,
        "execute_checks": execute_checks,
        "continuity_checks": continuity_checks,
        "trusted_blueprint_checks": blueprint_checks,
        "authoring_proposal_checks": proposal_checks
        if freeform_proposal_required
        else {},
        "split_authoring_proposal_checks": split_proposal_checks,
        "semantic_completeness": {
            "prepared_provider_candidate": prepared_semantic_completeness,
            "committed_catalog": committed_semantic_completeness,
        },
        "ownership": ownership,
        "policy_checks": policy_checks,
        "after": _package_evidence(after_package),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return cycle, after_package


def run(
    *,
    server_url: str,
    env_path: Path,
    environment: str,
    domain_id: str,
    timeout_seconds: int,
    worker_input_dir: Path = V6_INPUT_DIR,
    source_set_id: str = DEFAULT_SOURCE_SET_ID,
) -> dict[str, Any]:
    from pymongo import MongoClient

    env = load_dotenv_values(env_path)
    gemini_key = resolve_gemini_api_key(env_path)
    langflow_key = str(os.getenv("LANGFLOW_API_KEY") or env.get("LANGFLOW_API_KEY") or "")
    mongo_uri = str(os.getenv("MONGODB_URI") or env.get("MONGODB_URI") or "").strip()
    database_name = str(os.getenv("MONGODB_DATABASE") or env.get("MONGODB_DATABASE") or "datagov").strip()
    if not mongo_uri:
        raise RuntimeError("mongodb_uri_not_configured")
    if DEFAULT_GEMINI_MODEL != AUTHORING_GEMINI_MODEL:
        raise RuntimeError("authoring_gemini_model_constant_drift")

    nonce = uuid.uuid4().hex
    effective_environment = _fresh_environment(environment, nonce)
    normalized_source_set_id = str(source_set_id or "").strip()
    texts, source_hashes, authoring_sources = _load_v6_authoring_sources(
        worker_input_dir=worker_input_dir,
        source_set_id=normalized_source_set_id,
    )
    domain_bootstrap_source = _compose_domain_bootstrap_source(
        texts["domain"],
        texts["dataset"],
        texts["main_filter"],
    )
    domain_bootstrap_sha256 = sha256(
        domain_bootstrap_source.encode("utf-8")
    ).hexdigest()
    defaults = [_flow_defaults(path) for path in FLOW_PATHS]
    expected_kinds = ["domain", "dataset", "main_filter", "domain_policy"]
    defaults_ok = all(
        row["authoring_kind"] == kind
        and row["metadata_contract_mode"] == "domain_package_v2"
        and row["source_grounding_mode"] == "freeform_llm"
        and row["model_names"]
        == ([] if kind == "domain_policy" else [AUTHORING_GEMINI_MODEL])
        and row["model_contract"]["passed"] is True
        and (
            row["prompt_node_count"] == 0
            and row["context_builder_node_count"] == 0
            and row["composer_node_count"] == 0
            and row["invoker_node_count"] == 0
            if kind == "domain_policy"
            else row["prompt_node_count"] == (3 if kind == "domain" else 1)
            and row["context_builder_node_count"]
            == (3 if kind == "domain" else 1)
            and row["composer_node_count"] == (3 if kind == "domain" else 1)
            and row["invoker_node_count"] == (3 if kind == "domain" else 1)
        )
        and row["trusted_blueprint_json_default_empty"] is True
        and row["trusted_blueprint_pin_default_empty"] is True
        and (
            row["domain_bootstrap_input_node_ids"]
            == sorted(DOMAIN_BOOTSTRAP_INPUT_NODE_IDS.values())
            and row["natural_source_bundle_node_count"] == 1
            if kind == "domain"
            else row["natural_source_bundle_node_count"] == 0
        )
        for row, kind in zip(defaults, expected_kinds, strict=True)
    )
    model_contract = gemini_model_contract_evidence()
    exact_gemini_no_fallback = (
        model_contract.get("requested_model") == AUTHORING_GEMINI_MODEL
        and model_contract.get("temperature") == 0
        and model_contract.get("candidate_count") == 1
        and model_contract.get("fallback_enabled") is False
        and model_contract.get("fallback_models") == []
        and all(row.get("model_contract", {}).get("passed") is True for row in defaults)
    )

    client = requests.Session()
    headers = _auth_headers(client, server_url, env)
    uploaded = [
        _upload_flow(client, headers, server_url, path, timeout_seconds)
        for path in FLOW_PATHS
    ]
    imports = [
        {
            "file": path.name,
            "flow_sha256": sha256(path.read_bytes()).hexdigest(),
            "flow_id_sha256": sha256(str(record.get("id") or "").encode("utf-8")).hexdigest(),
            "endpoint_name": str(record.get("endpoint_name") or ""),
            "node_count": len((record.get("data") or {}).get("nodes") or []),
        }
        for path, record in zip(FLOW_PATHS, uploaded, strict=True)
    ]

    mongo = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    database = mongo[database_name]
    production_pointer_before = _active_pointer_snapshot(
        database,
        domain_id=domain_id,
    )
    initial_pointer, initial_package = _active_package(
        database,
        domain_id=domain_id,
        environment=effective_environment,
    )
    if initial_pointer or initial_package:
        mongo.close()
        raise RuntimeError("fresh_validation_environment_not_empty")

    legacy_names = _legacy_collection_names(env)
    legacy_before = _collection_snapshot(database, legacy_names)
    collection_guards = _authoring_collection_guard_negatives(
        client=client,
        headers=headers,
        server_url=server_url,
        flow_id=str(uploaded[0]["id"]),
        database=database,
        database_name=database_name,
        domain_id=domain_id,
        environment=effective_environment,
        source_text=texts["domain"],
        legacy_name=legacy_names[0],
        timeout_seconds=timeout_seconds,
    )
    if not collection_guards["passed"]:
        mongo.close()
        raise AuthoringValidationError(
            code="authoring_collection_guard_validation_failed",
            stage="collection_guard_negatives",
            details={
                **_guard_failure_details(collection_guards),
                "environment": effective_environment,
                "flow_import_count": len(imports),
                "flow_id_sha256": [row["flow_id_sha256"] for row in imports],
            },
        )

    clarification_probe = _run_freeform_clarification_probe(
        client=client,
        headers=headers,
        server_url=server_url,
        flow_id=str(uploaded[0]["id"]),
        database=database,
        database_name=database_name,
        domain_id=domain_id,
        environment=effective_environment,
        timeout_seconds=timeout_seconds,
    )
    if not clarification_probe["passed"]:
        mongo.close()
        raise AuthoringValidationError(
            code="freeform_clarification_probe_failed",
            stage="freeform_clarification",
            details={
                "failed_checks": sorted(
                    str(key)
                    for key, passed in (clarification_probe.get("checks") or {}).items()
                    if passed is not True
                ),
                "environment": effective_environment,
                "flow_import_count": len(imports),
                "flow_id_sha256": [row["flow_id_sha256"] for row in imports],
                "expected_source_sha256": str(
                    clarification_probe.get("source_text_sha256") or ""
                ),
                "actual_source_sha256": str(
                    (clarification_probe.get("clarification") or {}).get(
                        "source_sha256"
                    )
                    or ""
                ),
                "actual_status": str(
                    (clarification_probe.get("diagnostics") or {}).get("status") or ""
                ),
                "error_code": str(
                    (clarification_probe.get("diagnostics") or {}).get("error_code") or ""
                ),
                "error_stage": str(
                    (clarification_probe.get("diagnostics") or {}).get("error_stage") or ""
                ),
                "error_reason": str(
                    (clarification_probe.get("diagnostics") or {}).get("error_reason") or ""
                ),
                "error_type": str(
                    (clarification_probe.get("diagnostics") or {}).get("error_type") or ""
                ),
                "error_path": str(
                    (clarification_probe.get("diagnostics") or {}).get("error_path") or ""
                ),
                "error_message_sha256": str(
                    (clarification_probe.get("diagnostics") or {}).get(
                        "error_message_sha256"
                    )
                    or ""
                ),
                "error_operator_sha256": str(
                    (clarification_probe.get("diagnostics") or {}).get(
                        "error_operator_sha256"
                    )
                    or ""
                ),
                "error_metric_id_sha256": str(
                    (clarification_probe.get("diagnostics") or {}).get(
                        "error_metric_id_sha256"
                    )
                    or ""
                ),
                "error_field_sha256": str(
                    (clarification_probe.get("diagnostics") or {}).get(
                        "error_field_sha256"
                    )
                    or ""
                ),
                "manifest_error_code": str(
                    (clarification_probe.get("diagnostics") or {}).get(
                        "manifest_error_code"
                    )
                    or ""
                ),
                "error_dataset_id_sha256": str(
                    (clarification_probe.get("diagnostics") or {}).get(
                        "error_dataset_id_sha256"
                    )
                    or ""
                ),
                "error_detail_value_sha256": str(
                    (clarification_probe.get("diagnostics") or {}).get(
                        "error_detail_value_sha256"
                    )
                    or ""
                ),
                "error_candidate_count": int(
                    (clarification_probe.get("diagnostics") or {}).get(
                        "error_candidate_count"
                    )
                    or 0
                ),
                "error_detail_index": int(
                    (clarification_probe.get("diagnostics") or {}).get(
                        "error_detail_index"
                    )
                    or 0
                ),
            },
        )

    cycles: list[dict[str, Any]] = []
    cycle_specs = (
        {
            "authoring_kind": "domain",
            "flow_id": str(uploaded[0]["id"]),
            "source_text": texts["domain"],
            "expected_source_text": domain_bootstrap_source,
            "input_node_tweaks": {
                "chat_input": {"input_value": texts["domain"]},
                "dataset_source_input": {"input_value": texts["dataset"]},
                "main_filter_source_input": {
                    "input_value": texts["main_filter"]
                },
            },
            "source_grounding_mode": "freeform_llm",
            "policy_overlays": None,
        },
        {
            "authoring_kind": "dataset",
            "flow_id": str(uploaded[1]["id"]),
            "source_text": texts["dataset"],
            "expected_source_text": texts["dataset"],
            "input_node_tweaks": None,
            "source_grounding_mode": "freeform_llm",
            "policy_overlays": None,
        },
        {
            "authoring_kind": "main_filter",
            "flow_id": str(uploaded[2]["id"]),
            "source_text": texts["main_filter"],
            "expected_source_text": texts["main_filter"],
            "input_node_tweaks": None,
            "source_grounding_mode": "freeform_llm",
            "policy_overlays": None,
        },
        {
            "authoring_kind": "domain_policy",
            "flow_id": str(uploaded[3]["id"]),
            "source_text": texts["domain_policy"],
            "expected_source_text": texts["domain_policy"],
            "input_node_tweaks": None,
            "source_grounding_mode": "freeform_llm",
            "policy_overlays": {
                "intent_prompt_extension": POLICY_INTENT_EXTENSION,
                "answer_prompt_extension": POLICY_ANSWER_EXTENSION,
                "specialized_functions_json": json.dumps(
                    [POLICY_FUNCTION_CARD],
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                "output_profile_json": json.dumps(
                    POLICY_OUTPUT_OVERLAY,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
            },
        },
    )
    latest_package: dict[str, Any] = {}
    for index, spec in enumerate(cycle_specs, start=1):
        cycle, latest_package = _run_authoring_cycle(
            client=client,
            headers=headers,
            server_url=server_url,
            flow_id=str(spec["flow_id"]),
            database=database,
            database_name=database_name,
            domain_id=domain_id,
            environment=effective_environment,
            authoring_kind=str(spec["authoring_kind"]),
            source_text=str(spec["source_text"]),
            nonce=f"{index}-{uuid.uuid4().hex}",
            timeout_seconds=timeout_seconds,
            policy_overlays=spec["policy_overlays"],
            source_grounding_mode=str(spec["source_grounding_mode"]),
            input_node_tweaks=spec["input_node_tweaks"],
            expected_source_text=str(spec["expected_source_text"]),
            semantic_completeness_fn=_manufacturing_semantic_completeness,
            require_owned_change=str(spec["authoring_kind"]) == "domain_policy",
        )
        cycles.append(cycle)
        if not cycle["passed"]:
            mongo.close()
            raise AuthoringValidationError(
                code="authoring_cycle_failed",
                stage=str(spec["authoring_kind"]),
                details={
                    "authoring_kind": str(spec["authoring_kind"]),
                    "environment": effective_environment,
                    "flow_import_count": len(imports),
                    "flow_id_sha256": [row["flow_id_sha256"] for row in imports],
                    "failed_checks": sorted(
                        str(key)
                        for key, passed in (cycle.get("checks") or {}).items()
                        if passed is not True
                    ),
                    "prepare": {
                        "status": str((cycle.get("prepare") or {}).get("status") or ""),
                        "stage": str((cycle.get("prepare") or {}).get("stage") or ""),
                        "error_code": str(
                            (cycle.get("prepare") or {}).get("error_code") or ""
                        ),
                        "error_stage": str(
                            (cycle.get("prepare") or {}).get("error_stage") or ""
                        ),
                        "failed_checks": sorted(
                            str(key)
                            for key, passed in (cycle.get("prepare_checks") or {}).items()
                            if passed is not True
                        ),
                    },
                    "execute": {
                        "status": str((cycle.get("execute") or {}).get("status") or ""),
                        "stage": str((cycle.get("execute") or {}).get("stage") or ""),
                        "error_code": str(
                            (cycle.get("execute") or {}).get("error_code") or ""
                        ),
                        "error_stage": str(
                            (cycle.get("execute") or {}).get("error_stage") or ""
                        ),
                        "error_invariant": str(
                            (cycle.get("execute") or {}).get("error_invariant") or ""
                        ),
                        "error_type": str(
                            (cycle.get("execute") or {}).get("error_type") or ""
                        ),
                        "error_message_sha256": str(
                            (cycle.get("execute") or {}).get("error_message_sha256") or ""
                        ),
                        "failed_checks": sorted(
                            str(key)
                            for key, passed in (cycle.get("execute_checks") or {}).items()
                            if passed is not True
                        ),
                    },
                    "approval_seal": {
                        "pending_storage_checks_passed": bool(
                            (cycle.get("pending") or {}).get("passed") is True
                        ),
                        "external_seal_checks_passed": all(
                            value is True
                            for value in ((cycle.get("approval") or {}).get("checks") or {}).values()
                        ),
                        "tamper_seal_unchanged": all(
                            bool(
                                ((row.get("checks") or {}).get("wrapper_seal_unchanged"))
                                is True
                            )
                            for row in (cycle.get("approval_tamper_negatives") or [])
                            if isinstance(row, dict)
                        ),
                        "approval_event_sha256": str(
                            (cycle.get("approval") or {}).get("event_sha256") or ""
                        ),
                    },
                },
            )

    domain_cycle = next(
        (row for row in cycles if row.get("authoring_kind") == "domain"),
        {},
    )
    schema_binding_validation = _google_authoring_schema_binding_validation(
        (domain_cycle.get("prepare") or {}).get("llm_schema_bindings") or {}
    )
    domain_input_hashes = domain_cycle.get("source_input_node_hashes") or {}
    domain_bootstrap_checks = {
        "freeform_mode": domain_cycle.get("source_grounding_mode") == "freeform_llm",
        "blueprint_not_flow_input": domain_cycle.get("trusted_blueprint_configured")
        is False,
        "composed_source_hash_exact": domain_cycle.get("source_text_sha256")
        == domain_bootstrap_sha256,
        "domain_input_node_hash_exact": domain_input_hashes.get("chat_input")
        == source_hashes["domain"],
        "dataset_input_node_hash_exact": domain_input_hashes.get(
            "dataset_source_input"
        )
        == source_hashes["dataset"],
        "main_filter_input_node_hash_exact": domain_input_hashes.get(
            "main_filter_source_input"
        )
        == source_hashes["main_filter"],
        "draft_llm_three": (domain_cycle.get("prepare") or {}).get(
            "draft_llm_calls"
        )
        == 3,
        "annotation_llm_zero": (domain_cycle.get("prepare") or {}).get(
            "annotation_llm_calls"
        )
        == 0,
        "repair_llm_zero": (domain_cycle.get("prepare") or {}).get(
            "repair_llm_calls"
        )
        == 0,
        "three_google_native_schema_bindings": schema_binding_validation["passed"]
        is True,
    }
    proposal_hash_rows: list[dict[str, Any]] = []
    for cycle, spec in zip(cycles, cycle_specs, strict=True):
        kind = str(spec["authoring_kind"])
        if kind == "domain_policy":
            continue
        proposal = (cycle.get("prepare") or {}).get(
            "authoring_proposal_validation"
        ) or {}
        grounding = (cycle.get("prepare") or {}).get(
            "source_grounding_validation"
        ) or {}
        expected_source_sha256 = sha256(
            str(spec["expected_source_text"]).encode("utf-8")
        ).hexdigest()
        checks = {
            "validation_contract_exact": proposal.get("contract_version")
            == "metadata.authoring.proposal.validation.v1",
            "proposal_contract_exact": proposal.get("proposal_contract_version")
            == "metadata.authoring.proposal.v1",
            "status_complete": proposal.get("status") == "complete",
            "source_hash_exact": proposal.get("source_sha256")
            == expected_source_sha256,
            "proposal_hash_valid": _is_sha256(proposal.get("proposal_sha256")),
            "draft_hash_valid": _is_sha256(proposal.get("draft_sha256")),
            "grounding_source_hash_exact": grounding.get("source_sha256")
            == expected_source_sha256,
            "grounding_draft_hash_exact": grounding.get(
                "structured_proposal_sha256"
            )
            == (
                proposal.get("expanded_draft_sha256")
                or proposal.get("draft_sha256")
            ),
        }
        proposal_hash_rows.append(
            {
                "authoring_kind": kind,
                "source_sha256": expected_source_sha256,
                "proposal_sha256": str(proposal.get("proposal_sha256") or ""),
                "draft_sha256": str(proposal.get("draft_sha256") or ""),
                "checks": checks,
                "passed": all(checks.values()),
            }
        )

    split_proposal_hash_rows: list[dict[str, Any]] = []
    domain_split_proposals = (domain_cycle.get("prepare") or {}).get(
        "authoring_proposals_validation"
    ) or {}
    for branch in ("domain", "dataset", "main_filter"):
        proposal = domain_split_proposals.get(branch) or {}
        expected_source_sha256 = source_hashes[branch]
        checks = {
            "validation_contract_exact": proposal.get("contract_version")
            == "metadata.authoring.proposal.validation.v1",
            "proposal_contract_exact": proposal.get("proposal_contract_version")
            == "metadata.authoring.proposal.v1",
            "status_complete": proposal.get("status") == "complete",
            "source_hash_exact": proposal.get("source_sha256")
            == expected_source_sha256,
            "proposal_hash_valid": _is_sha256(proposal.get("proposal_sha256")),
            "draft_hash_valid": _is_sha256(proposal.get("draft_sha256")),
        }
        split_proposal_hash_rows.append(
            {
                "branch": branch,
                "source_sha256": expected_source_sha256,
                "proposal_sha256": str(proposal.get("proposal_sha256") or ""),
                "draft_sha256": str(proposal.get("draft_sha256") or ""),
                "checks": checks,
                "passed": all(checks.values()),
            }
        )

    legacy_after = _collection_snapshot(database, legacy_names)
    legacy_checks = {
        "collection_count": len(legacy_names),
        "before_sha256": sha256_json(legacy_before),
        "after_sha256": sha256_json(legacy_after),
        "unchanged": legacy_before == legacy_after,
        "collection_names_persisted": False,
    }
    loader = _loader_roundtrip(
        mongo_uri=mongo_uri,
        database_name=database_name,
        domain_id=domain_id,
        environment=effective_environment,
    )
    production_pointer_after = _active_pointer_snapshot(
        database,
        domain_id=domain_id,
    )
    mongo.close()
    production_pointer_checks = {
        "identity_exact": production_pointer_before["environment"] == "production"
        and production_pointer_after["environment"] == "production"
        and production_pointer_before["domain_id"] == domain_id
        and production_pointer_after["domain_id"] == domain_id,
        "presence_unchanged": production_pointer_before["present"]
        == production_pointer_after["present"],
        "hash_unchanged": production_pointer_before["sha256"]
        == production_pointer_after["sha256"],
    }
    loader_checks = {
        "loader_ok": loader["ok"] is True,
        "identity_exact": loader["domain_id"] == domain_id
        and loader["environment"] == effective_environment,
        "revision_exact": int(loader["revision"] or 0) == len(cycle_specs),
        "package_hash_exact": loader["package_sha256"] == latest_package.get("package_sha256"),
        "bundle_hash_exact": loader["bundle_sha256"] == latest_package.get("bundle_sha256"),
        "catalog_hash_exact": loader["catalog_sha256"]
        == (latest_package.get("runtime_catalog") or {}).get("catalog_sha256"),
    }
    cycle_order_exact = [row["authoring_kind"] for row in cycles] == [
        "domain",
        "dataset",
        "main_filter",
        "domain_policy",
    ]
    revision_chain_exact = [row["after"]["revision"] for row in cycles] == [1, 2, 3, 4]
    total_draft_calls = sum(int(row["prepare"].get("draft_llm_calls") or 0) for row in cycles)
    total_annotation_calls = sum(
        int(row["prepare"].get("annotation_llm_calls") or 0) for row in cycles
    )
    total_repair_calls = sum(
        int(row["prepare"].get("repair_llm_calls") or 0)
        + int(row["execute"].get("repair_llm_calls") or 0)
        for row in cycles
    )
    domain_policy_cycle = next(
        (row for row in cycles if row.get("authoring_kind") == "domain_policy"),
        {},
    )
    domain_policy_llm_calls_zero = bool(domain_policy_cycle) and all(
        int((domain_policy_cycle.get(stage) or {}).get(counter) or 0) == 0
        for stage in ("prepare", "execute")
        for counter in ("draft_llm_calls", "annotation_llm_calls", "repair_llm_calls")
    )
    expected_cycle_calls = [
        _expected_prepare_llm_calls(
            str(spec["authoring_kind"]),
            str(spec["source_text"]),
            source_grounding_mode=str(spec["source_grounding_mode"]),
            trusted_blueprint_configured=False,
        )
        for spec in cycle_specs
    ]
    report = {
        "contract_version": "langflow.http.authoring-e2e.validation.v3",
        "model": AUTHORING_GEMINI_MODEL,
        "model_contract": model_contract,
        "exact_gemini_no_fallback": exact_gemini_no_fallback,
        "requested_environment_prefix_sha256": sha256(environment.encode("utf-8")).hexdigest(),
        "environment": effective_environment,
        "fresh_environment": True,
        "domain_id": domain_id,
        "source_set_id": normalized_source_set_id,
        "source_set_id_sha256": sha256(
            normalized_source_set_id.encode("utf-8")
        ).hexdigest(),
        "source_hashes": source_hashes,
        "authoring_sources": authoring_sources,
        "domain_bootstrap_source_sha256": domain_bootstrap_sha256,
        "source_text_persisted": False,
        "trusted_blueprint_json_persisted": False,
        "trusted_inventory_manifest_persisted": False,
        "trusted_blueprint_default_flow_input": False,
        "trusted_inventory_default_flow_input": False,
        "provider_output_persisted": False,
        "approval_payload_persisted": False,
        "secrets_persisted": False,
        "flow_defaults": defaults,
        "flow_defaults_passed": defaults_ok,
        "imports": imports,
        "collection_guard_negatives": collection_guards,
        "optional_explicit_inventory_admin_lane": {
            "executed": False,
            "default_success_evidence": False,
            "validator": "validate_live_blueprint_authoring.py",
        },
        "freeform_clarification_probe": clarification_probe,
        "cycles": cycles,
        "domain_bootstrap_checks": domain_bootstrap_checks,
        "provider_schema_binding_validation": schema_binding_validation,
        "proposal_hash_validation": proposal_hash_rows,
        "split_bootstrap_proposal_hash_validation": split_proposal_hash_rows,
        "cycle_order_exact": cycle_order_exact,
        "revision_chain_exact": revision_chain_exact,
        "draft_llm_calls": total_draft_calls,
        "annotation_llm_calls": total_annotation_calls,
        "repair_llm_calls": total_repair_calls,
        "domain_policy_llm_calls_zero": domain_policy_llm_calls_zero,
        "expected_llm_calls": {
            "draft": sum(item["draft"] for item in expected_cycle_calls),
            "annotation": sum(item["annotation"] for item in expected_cycle_calls),
            "repair": sum(item["repair"] for item in expected_cycle_calls),
        },
        "legacy_collection_checks": legacy_checks,
        "loader_roundtrip": loader,
        "loader_checks": loader_checks,
        "production_pointer": {
            "before": production_pointer_before,
            "after": production_pointer_after,
            "checks": production_pointer_checks,
            "passed": all(production_pointer_checks.values()),
        },
    }
    report["all_passed"] = (
        defaults_ok
        and exact_gemini_no_fallback
        and collection_guards["passed"]
        and clarification_probe["passed"]
        and all(row["passed"] for row in cycles)
        and all(domain_bootstrap_checks.values())
        and len(proposal_hash_rows) == 3
        and all(row["passed"] for row in proposal_hash_rows)
        and len(split_proposal_hash_rows) == 3
        and all(row["passed"] for row in split_proposal_hash_rows)
        and cycle_order_exact
        and revision_chain_exact
        and total_draft_calls == sum(item["draft"] for item in expected_cycle_calls)
        and total_annotation_calls == sum(
            item["annotation"] for item in expected_cycle_calls
        )
        and total_repair_calls == sum(item["repair"] for item in expected_cycle_calls)
        and domain_policy_llm_calls_zero
        and legacy_checks["unchanged"]
        and all(loader_checks.values())
        and all(production_pointer_checks.values())
    )
    assert_secret_absent(report, gemini_key)
    assert_secret_absent(report, langflow_key)
    assert_secret_absent(report, mongo_uri)
    for source_text in texts.values():
        assert_secret_absent(report, source_text)
    assert_secret_absent(report, domain_bootstrap_source)
    assert_secret_absent(report, FREEFORM_CLARIFICATION_PROBE)
    return report

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-url", default="http://127.0.0.1:7873")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--environment", default="e2e_validation")
    parser.add_argument("--domain-id", default="manufacturing")
    parser.add_argument(
        "--worker-input-dir",
        type=Path,
        default=V6_INPUT_DIR,
        help="domain_v6.txt, dataset_v6.txt, main_filter_v6.txt가 있는 프로젝트 내부 폴더",
    )
    parser.add_argument(
        "--source-set-id",
        default=DEFAULT_SOURCE_SET_ID,
        help="검증 report에서 입력 corpus를 식별할 안정 ID",
    )
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs" / "langflow_http_authoring_e2e.json",
    )
    args = parser.parse_args()
    try:
        report = run(
            server_url=args.server_url,
            env_path=args.env_file.resolve(),
            environment=args.environment,
            domain_id=args.domain_id,
            timeout_seconds=max(60, min(args.timeout_seconds, 600)),
            worker_input_dir=args.worker_input_dir.resolve(),
            source_set_id=args.source_set_id,
        )
    except Exception as exc:
        report = {
            "contract_version": "langflow.http.authoring-e2e.validation.v3",
            "model": AUTHORING_GEMINI_MODEL,
            "all_passed": False,
            "failure": _safe_failure(exc),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "model": report.get("model"),
                "imports": len(report.get("imports") or []),
                "all_passed": report.get("all_passed"),
                "failure": report.get("failure"),
            },
            ensure_ascii=False,
        )
    )
    print(f"report: {args.output}")
    return 0 if report.get("all_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
