"""Upload and exercise the v6 analysis Flow through Langflow's public API.

The persisted report is intentionally evidence-only. API keys, prompts, raw
Langflow responses and model text are never written. The validator keeps the
response in memory just long enough to verify the canonical response.v1 payload,
the Message/API/GaiA terminal presence and response.v1 usage counters.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from flow_builder_support import BuildContractError, sha256_file, write_json_atomic
except ModuleNotFoundError:  # Imported as ``tools.validate_langflow_http_e2e``.
    from tools.flow_builder_support import BuildContractError, sha256_file, write_json_atomic
from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    assert_secret_absent,
    gemini_model_contract_evidence,
    langflow_gemini_contract_evidence,
    load_dotenv_values,
    require_exact_gemini_model,
    resolve_gemini_api_key,
)
from reference_runtime.metadata_collections import (
    METADATA_COLLECTIONS,
    load_available_domain_package_from_three_collections,
)

DEFAULT_FLOW = ROOT / "flow_exports" / "metadata_v6_data_analysis_flow_v6_standalone.json"
REFERENCE_INSTANT = "2026-07-30T09:00:00+09:00"
CONTENT_REF_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,31}:[A-Za-z0-9._:-]{4,256}$")


def _validation_clock_evidence(
    env: dict[str, str], *, reference_instant: str = REFERENCE_INSTANT
) -> dict[str, Any]:
    """Require the server-side-only deterministic clock seam for relative dates.

    ``request_state_capsule`` intentionally exposes no clock or timezone Flow
    input.  The Langflow server used by this validator must therefore be
    started with the same two validation-only environment values.
    """

    mode = str(os.getenv("V6_VALIDATION_MODE") or env.get("V6_VALIDATION_MODE") or "").strip()
    reference = str(
        os.getenv("V6_VALIDATION_REFERENCE_INSTANT")
        or env.get("V6_VALIDATION_REFERENCE_INSTANT")
        or ""
    ).strip()
    checks = {
        "validation_mode_enabled": mode == "1",
        "reference_instant_exact": reference == reference_instant,
        "timezone_internal": True,
        "flow_clock_tweak_used": False,
    }
    # ``flow_clock_tweak_used`` is an explicit negative invariant: the
    # production Flow must not expose a clock input, and the validation seam
    # is supplied only through the server environment.  Treating this mapping
    # with ``all(checks.values())`` made every correctly configured run fail
    # because the expected value of that one field is ``False``.
    if not (
        checks["validation_mode_enabled"]
        and checks["reference_instant_exact"]
        and checks["timezone_internal"]
        and checks["flow_clock_tweak_used"] is False
    ):
        raise BuildContractError("validation_clock_environment_not_configured")
    return {
        "mode": "environment_only",
        "reference_instant": reference,
        "timezone": "Asia/Seoul",
        "checks": checks,
    }


def _three_collection_release_evidence(
    mongo_uri: str,
    database_name: str,
    *,
    expected_domain_id: str,
    expected_environment: str,
    timeout_ms: int = 10000,
) -> dict[str, Any]:
    """Validate the same auto-selected three-collection release as the Flow."""

    from pymongo import MongoClient

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=timeout_ms)
    try:
        database = client[database_name]
        package = load_available_domain_package_from_three_collections(database)
        documents = {
            kind: list(
                database[name].find(
                    {},
                    {
                        "_id": 1,
                        "section": 1,
                        "key": 1,
                        "natural_text": 1,
                        "payload": 1,
                    },
                )
            )
            for kind, name in METADATA_COLLECTIONS.items()
        }
    finally:
        client.close()

    item_counts = {kind: len(rows) for kind, rows in documents.items()}
    item_ids = {
        kind: sorted(str(document.get("_id") or "") for document in rows)
        for kind, rows in documents.items()
    }
    item_set_sha256 = sha256(
        json.dumps(item_ids, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
    revision = int(package.get("revision") or 0)
    checks = {
        "three_collections_nonempty": all(count > 0 for count in item_counts.values()),
        "fixed_collection_roles": set(documents) == set(METADATA_COLLECTIONS),
        "typed_item_documents": all(
            isinstance(document.get("section"), str)
            and bool(document.get("section"))
            and isinstance(document.get("key"), str)
            and bool(document.get("key"))
            and isinstance(document.get("natural_text"), str)
            and bool(document.get("natural_text"))
            and isinstance(document.get("payload"), dict)
            for rows in documents.values()
            for document in rows
        ),
        "expected_domain": package.get("domain_id") == expected_domain_id,
        "expected_environment": package.get("environment") == expected_environment,
        "revision_positive": revision >= 1,
        "package_sha256_valid": len(str(package.get("package_sha256") or "")) == 64,
        "bundle_sha256_valid": len(str(package.get("bundle_sha256") or "")) == 64,
        "catalog_sha256_valid": len(
            str((package.get("runtime_catalog") or {}).get("catalog_sha256") or "")
        )
        == 64,
    }
    if not all(checks.values()):
        raise BuildContractError("three_collection_release_precondition_failed")
    catalog = package.get("runtime_catalog") if isinstance(package.get("runtime_catalog"), dict) else {}
    datasets = catalog.get("datasets") if isinstance(catalog.get("datasets"), dict) else {}
    return {
        "selection": "latest_available_release",
        "domain_id": str(package["domain_id"]),
        "environment": str(package["environment"]),
        "revision": revision,
        "package_sha256": str(package["package_sha256"]),
        "bundle_sha256": str(package["bundle_sha256"]),
        "catalog_sha256": str((package.get("runtime_catalog") or {}).get("catalog_sha256") or ""),
        "dataset_source_types": {
            str(key): str(value.get("source_type") or "")
            for key, value in sorted(datasets.items())
            if isinstance(value, dict)
        },
        "item_set_sha256": item_set_sha256,
        "item_counts": item_counts,
        "collections": dict(METADATA_COLLECTIONS),
        "checks": checks,
    }


CASES: tuple[dict[str, Any], ...] = (
    {
        "case_id": "HTTP-DETERMINISTIC",
        "question": "오늘 DA공정 WIP을 제품별로 알려줘",
        "session_group": "deterministic",
        "expected_route": "deterministic",
        "expected_intent_calls": 0,
        "expected_state_version": 1,
    },
    {
        "case_id": "HTTP-INTENT",
        "question": "오늘 DA 쪽에서 잘 나간 제품 세 개만 보면?",
        "session_group": "intent",
        "expected_route": "intent_llm",
        "expected_intent_calls": 1,
        "expected_state_version": 1,
    },
    {
        "case_id": "HTTP-MULTITURN-1",
        "question": "오늘 DA공정 WIP을 제품별로 알려줘",
        "session_group": "multiturn",
        "expected_route": "deterministic",
        "expected_intent_calls": 0,
        "expected_state_version": 1,
    },
    {
        "case_id": "HTTP-MULTITURN-2",
        "question": "그중 가장 많은 제품을 동률 포함해서 보여줘",
        "session_group": "multiturn",
        "expected_route": "deterministic",
        "expected_intent_calls": 0,
        "expected_state_version": 2,
    },
)


def _bounded_error(exc: Exception) -> dict[str, str]:
    if isinstance(exc, requests.Timeout):
        return {"type": "Timeout", "code": "langflow_timeout"}
    if isinstance(exc, requests.ConnectionError):
        return {"type": "ConnectionError", "code": "langflow_connection_error"}
    if isinstance(exc, requests.HTTPError):
        status = int(exc.response.status_code) if exc.response is not None else 0
        return {"type": "HTTPError", "code": f"langflow_http_{status}"}
    return {"type": type(exc).__name__[:80], "code": "langflow_validation_error"}


def _auth_headers(session: requests.Session, server_url: str, env: dict[str, str]) -> dict[str, str]:
    # Validation servers are deliberately isolated and expose Langflow's
    # auto-login endpoint.  Prefer that server-local identity so an unrelated
    # API key inherited from the source v5 .env cannot authenticate against
    # (or be sent to) the fresh profile.  Production servers normally disable
    # auto-login; in that case the explicitly configured API key remains the
    # fallback.
    api_key = str(os.getenv("LANGFLOW_API_KEY") or env.get("LANGFLOW_API_KEY") or "").strip()
    response = session.get(server_url.rstrip("/") + "/api/v1/auto_login", timeout=30)
    if response.ok:
        token = str((response.json() if response.content else {}).get("access_token") or "")
        if token:
            return {"Authorization": f"Bearer {token}"}
    if api_key:
        return {"x-api-key": api_key}
    response.raise_for_status()
    raise BuildContractError("langflow_auth_not_configured")


def _run_url(server_url: str, flow_id: str, headers: dict[str, str]) -> str:
    """Return the public Langflow 1.9.2 Flow execution route."""

    del headers
    return f"{server_url.rstrip('/')}/api/v1/run/{flow_id}"


def _walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for nested in value.values():
            yield from _walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk(nested)


def _output_blocks(payload: Any) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for value in _walk(payload):
        if not isinstance(value, dict):
            continue
        if not any(key in value for key in ("results", "artifacts", "outputs")):
            continue
        component_id = str(value.get("component_id") or value.get("componentId") or "")
        display_name = str(value.get("component_display_name") or value.get("componentDisplayName") or "")
        if component_id or display_name:
            blocks.append(value)
    return blocks


def _canonical_responses(value: Any) -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for item in _walk(value):
        if not isinstance(item, dict) or item.get("contract_version") != "response.v1":
            continue
        digest = sha256(
            json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
        found.setdefault(digest, item)
    return list(found.values())


def _gaia_hashes(value: Any) -> list[str]:
    hashes: set[str] = set()
    for item in _walk(value):
        if not isinstance(item, dict) or item.get("contract_version") != "gaia.metadata.v1":
            continue
        digest = str(item.get("response_sha256") or "")
        if len(digest) == 64:
            hashes.add(digest)
    return sorted(hashes)


def _message_link_hashes(value: Any) -> set[str]:
    hashes: set[str] = set()
    for item in _walk(value):
        if not isinstance(item, dict):
            continue
        metadata = item.get("session_metadata")
        if not isinstance(metadata, dict):
            continue
        if metadata.get("contract_version") != "response.message-link.v1":
            continue
        digest = str(metadata.get("response_sha256") or "")
        if len(digest) == 64 and all(char in "0123456789abcdef" for char in digest):
            hashes.add(digest)
    return hashes


def _classify_block(block: dict[str, Any]) -> str:
    component_id = str(block.get("component_id") or block.get("componentId") or "").casefold()
    display = str(block.get("component_display_name") or block.get("componentDisplayName") or "").casefold()
    identity = component_id + " " + display
    if "message_presentation" in identity or "message presentation" in identity:
        return "message"
    if "gaia_output" in identity or "gaia output" in identity:
        return "gaia"
    if "api_response" in identity or "api response" in identity:
        return "api"
    if "chat_output" in identity or "chat output" in identity:
        # Chat Output is the transport wrapper for Message Presentation.
        # Langflow strips arbitrary Message extras, so the canonical link is
        # carried in supported session_metadata rather than Message.data.
        return "message"
    return "other"


def extract_terminal_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    blocks = _output_blocks(payload)
    by_terminal: dict[str, set[str]] = {
        "message": set(),
        "gaia": set(),
        "api": set(),
        "chat_output": set(),
    }
    block_counts: dict[str, int] = {key: 0 for key in by_terminal}
    for block in blocks:
        kind = _classify_block(block)
        if kind not in by_terminal:
            continue
        block_counts[kind] += 1
        if kind == "message":
            by_terminal[kind].update(_message_link_hashes(block))
        elif kind == "gaia":
            # GaiA intentionally carries only the compact metadata link, not a
            # duplicate response.v1 payload.  Its response hash is still the
            # canonical cross-terminal identity.
            by_terminal[kind].update(_gaia_hashes(block))
        else:
            by_terminal[kind].update(
                sha256(
                    json.dumps(
                        item,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
                for item in _canonical_responses(block)
            )
    all_responses = _canonical_responses(payload)
    canonical_hashes = sorted(
        sha256(
            json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
        for item in all_responses
    )
    gaia_hashes = _gaia_hashes(payload)
    # Some serializers expose custom output keys without a component wrapper.
    # Only explicit terminal labels are accepted as fallback evidence.
    for item in _walk(payload):
        if not isinstance(item, dict):
            continue
        for key, terminal in (("api_response", "api"), ("message", "message")):
            if key not in item:
                continue
            by_terminal[terminal].update(
                sha256(
                    json.dumps(
                        value,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
                for value in _canonical_responses(item[key])
            )
        if "gaia_response" in item:
            by_terminal["gaia"].update(_gaia_hashes(item["gaia_response"]))
    primary = all_responses[0] if len(canonical_hashes) == 1 else {}
    response_hash = canonical_hashes[0] if len(canonical_hashes) == 1 else ""
    trace = primary.get("trace") if isinstance(primary.get("trace"), dict) else {}
    usage = trace.get("usage") if isinstance(trace.get("usage"), dict) else {}
    route = trace.get("route") if isinstance(trace.get("route"), dict) else {}
    state = primary.get("state") if isinstance(primary.get("state"), dict) else {}
    analysis = primary.get("analysis") if isinstance(primary.get("analysis"), dict) else {}
    raw_error = analysis.get("error") if isinstance(analysis.get("error"), dict) else {}
    raw_error_details = (
        raw_error.get("details") if isinstance(raw_error.get("details"), dict) else {}
    )
    data_refs = primary.get("data_refs") if isinstance(primary.get("data_refs"), list) else []
    answer_sections = (
        primary.get("answer_sections") if isinstance(primary.get("answer_sections"), dict) else {}
    )
    downloads = (
        answer_sections.get("downloads") if isinstance(answer_sections.get("downloads"), list) else []
    )
    result_table = (
        answer_sections.get("result_table")
        if isinstance(answer_sections.get("result_table"), dict)
        else {}
    )
    data_ref_ids = [
        str(item.get("ref_id") or "") for item in data_refs if isinstance(item, dict)
    ]
    download_ref_ids = [
        str(item.get("ref_id") or "") for item in downloads if isinstance(item, dict)
    ]
    analysis_ref_ids = [
        str(item.get("ref_id") or "")
        for item in data_refs
        if isinstance(item, dict) and item.get("role") == "analysis_result"
    ]
    state_result_ref = str(state.get("executed_result_ref") or "")
    result_table_ref = str(result_table.get("data_ref") or "")
    terminal_hashes = {key: sorted(value) for key, value in by_terminal.items()}
    # Message and GaiA are presentation adapters, so they do not need to echo
    # the API payload or a cross-node hash. Integrity is checked after final
    # response.v1 serialization; terminal completeness is structural.
    terminal_equivalent = (
        bool(response_hash)
        and len(canonical_hashes) == 1
        and all(block_counts[key] >= 1 for key in ("message", "gaia", "api"))
        and by_terminal["api"] == {response_hash}
        and any(
            isinstance(item, dict) and item.get("contract_version") == "gaia.metadata.v1"
            for item in _walk(payload)
        )
    )
    return {
        "canonical_response_sha256": response_hash,
        "canonical_hash_count": len(canonical_hashes),
        "terminal_hashes": terminal_hashes,
        "gaia_metadata_response_sha256": gaia_hashes,
        "terminal_block_counts": block_counts,
        "terminal_equivalent": terminal_equivalent,
        "status": primary.get("status") if isinstance(primary, dict) else None,
        "route": route.get("route") if isinstance(route, dict) else None,
        "error": {
            "code": str(raw_error.get("code") or "")[:128],
            "stage": str(raw_error.get("stage") or "")[:128],
            "detail_keys": sorted(str(key)[:128] for key in raw_error_details)[:32],
        },
        "usage": {
            "intent_llm_calls": int(usage.get("intent_llm_calls") or 0),
            "intent_retry_calls": int(usage.get("intent_retry_calls") or 0),
            "answer_llm_calls": int(usage.get("answer_llm_calls") or 0),
            "pandas_code_llm_calls": int(usage.get("pandas_code_llm_calls") or 0),
            "pandas_repair_llm_calls": int(usage.get("pandas_repair_llm_calls") or 0),
        },
        "state_version": int(state.get("state_version") or 0),
        "executed_result_ref_sha256": (
            sha256(str(state.get("executed_result_ref") or "").encode("utf-8")).hexdigest()
            if state.get("executed_result_ref")
            else ""
        ),
        "persistence_contract": {
            "state_present": bool(state),
            "data_ref_count": len(data_refs),
            "data_ref_roles": sorted(
                str(item.get("role") or "") for item in data_refs if isinstance(item, dict)
            ),
            "answer_download_count": len(downloads),
            "download_url_count": sum(
                1 for item in downloads if isinstance(item, dict) and item.get("url")
            ),
            "all_data_ref_ids_valid": bool(data_ref_ids)
            and all(CONTENT_REF_PATTERN.fullmatch(value) for value in data_ref_ids),
            "all_download_ref_ids_valid": bool(download_ref_ids)
            and all(CONTENT_REF_PATTERN.fullmatch(value) for value in download_ref_ids),
            "download_refs_match_data_refs": sorted(download_ref_ids) == sorted(data_ref_ids),
            "one_analysis_result_ref": len(analysis_ref_ids) == 1,
            "state_ref_matches_analysis_result": len(analysis_ref_ids) == 1
            and state_result_ref == analysis_ref_ids[0],
            "result_table_ref_matches_analysis_result": len(analysis_ref_ids) == 1
            and result_table_ref == analysis_ref_ids[0],
        },
    }


def _upload_flow(
    session: requests.Session,
    headers: dict[str, str],
    server_url: str,
    flow_path: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    with flow_path.open("rb") as handle:
        response = session.post(
            server_url.rstrip("/") + "/api/v1/flows/upload/",
            headers=headers,
            files={"file": (flow_path.name, handle, "application/json")},
            timeout=timeout_seconds,
        )
    response.raise_for_status()
    value = response.json()
    uploaded = value[-1] if isinstance(value, list) else value
    if not isinstance(uploaded, dict) or not uploaded.get("id"):
        raise BuildContractError("langflow_upload_response_invalid")
    return uploaded


def _run_case(
    session: requests.Session,
    headers: dict[str, str],
    server_url: str,
    flow_id: str,
    case: dict[str, Any],
    *,
    session_id: str,
    mongo_uri: str,
    mongo_database: str,
    mongo_timeout_ms: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    tweaks = {
        "domain_bundle_loader": {
            "mongo_uri": mongo_uri,
            "mongo_database": mongo_database,
            "mongo_timeout_ms": mongo_timeout_ms,
        },
        "request_state_capsule": {
            # Validation-only opt-in. Production Flow export must stay false.
            "allow_anonymous_multiturn": True,
        },
        # The isolated Langflow server inherits its provider environment.
        # Never put a provider secret in a tweak, build payload or build log.
        "intent_language_model": {"temperature": 0.0, "stream": False},
        "retrieval_job_router": {"data_mode": "dummy"},
        "answer_facts_narrative": {"narrative_enabled": False},
        "response_state_commit": {"allow_anonymous_multiturn": True},
    }
    response = session.post(
        _run_url(server_url, flow_id, headers),
        headers={**headers, "Content-Type": "application/json"},
        json={
            "input_value": str(case["question"]),
            "input_type": "chat",
            "output_type": "any",
            "session_id": session_id,
            "tweaks": tweaks,
        },
        timeout=timeout_seconds,
    )
    body_hash = sha256(response.content).hexdigest()
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise BuildContractError("langflow_run_response_invalid")
    evidence = extract_terminal_evidence(payload)
    persistence = evidence.get("persistence_contract") or {}
    checks = {
        "http_200": response.status_code == 200,
        "status_ok_or_empty": evidence["status"] in {"ok", "empty"},
        "route_exact": evidence["route"] == case["expected_route"],
        "intent_calls_exact": (
            evidence["usage"]["intent_llm_calls"] == case["expected_intent_calls"]
        ),
        "intent_retry_zero": evidence["usage"]["intent_retry_calls"] == 0,
        "answer_calls_zero": evidence["usage"]["answer_llm_calls"] == 0,
        "pandas_code_calls_zero": evidence["usage"]["pandas_code_llm_calls"] == 0,
        "pandas_repair_calls_zero": evidence["usage"]["pandas_repair_llm_calls"] == 0,
        "state_version_exact": evidence["state_version"] == case["expected_state_version"],
        "persistent_state_present": persistence.get("state_present") is True,
        "persistent_data_refs_present": int(persistence.get("data_ref_count") or 0) >= 1,
        "persistent_download_entries_present": int(persistence.get("answer_download_count") or 0)
        == int(persistence.get("data_ref_count") or 0),
        "persistent_ref_ids_valid": persistence.get("all_data_ref_ids_valid") is True
        and persistence.get("all_download_ref_ids_valid") is True,
        "persistent_ref_sets_exact": persistence.get("download_refs_match_data_refs") is True,
        "persistent_analysis_ref_exact": persistence.get("one_analysis_result_ref") is True
        and persistence.get("state_ref_matches_analysis_result") is True
        and persistence.get("result_table_ref_matches_analysis_result") is True,
        "terminal_equivalent": evidence["terminal_equivalent"] is True,
    }
    return {
        "case_id": case["case_id"],
        "session_group": case["session_group"],
        "http_status": response.status_code,
        "http_response_sha256": body_hash,
        "expected_route": case["expected_route"],
        "expected_intent_llm_calls": case["expected_intent_calls"],
        "evidence": evidence,
        "checks": checks,
        "passed": all(checks.values()),
    }


def run(
    flow_path: Path,
    *,
    server_url: str,
    env_path: Path,
    model: str,
    domain_id: str,
    environment: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    try:
        model = require_exact_gemini_model(model)
    except RuntimeError as exc:
        raise BuildContractError("unexpected_gemini_model") from exc
    env = load_dotenv_values(env_path)
    gemini_api_key = resolve_gemini_api_key(env_path)
    langflow_api_key = str(
        os.getenv("LANGFLOW_API_KEY") or env.get("LANGFLOW_API_KEY") or ""
    )
    mongo_uri = str(os.getenv("MONGODB_URI") or env.get("MONGODB_URI") or "").strip()
    mongo_database = str(
        os.getenv("MONGODB_DATABASE") or env.get("MONGODB_DATABASE") or "datagov"
    ).strip()
    mongo_timeout_ms = 10000
    if not mongo_uri:
        raise BuildContractError("mongodb_uri_not_configured")
    validation_clock = _validation_clock_evidence(env)
    metadata_release = _three_collection_release_evidence(
        mongo_uri,
        mongo_database,
        expected_domain_id=domain_id,
        expected_environment=environment,
        timeout_ms=mongo_timeout_ms,
    )
    flow = json.loads(flow_path.read_text(encoding="utf-8"))
    flow_model_contract = langflow_gemini_contract_evidence(flow)
    if flow_model_contract.get("passed") is not True:
        raise BuildContractError("flow_gemini_model_contract_failed")
    model_node = next(
        (
            item
            for item in flow.get("data", {}).get("nodes", [])
            if item.get("id") == "intent_language_model"
        ),
        {},
    )
    configured_models = (
        (((model_node.get("data") or {}).get("node") or {}).get("template") or {})
        .get("model", {})
        .get("value")
        or []
    )
    exported_model_names = sorted(
        str(item.get("name") or "")
        for item in configured_models
        if isinstance(item, dict) and item.get("name")
    )
    if exported_model_names != [DEFAULT_GEMINI_MODEL]:
        raise BuildContractError("flow_gemini_model_mismatch")
    state_defaults = {}
    for node_id in ("request_state_capsule", "response_state_commit"):
        node = next((item for item in flow.get("data", {}).get("nodes", []) if item.get("id") == node_id), {})
        template = (((node.get("data") or {}).get("node") or {}).get("template") or {})
        field = template.get("allow_anonymous_multiturn") if isinstance(template, dict) else None
        state_defaults[node_id] = field.get("value") if isinstance(field, dict) else None
    if state_defaults != {"request_state_capsule": False, "response_state_commit": False}:
        raise BuildContractError("anonymous_multiturn_export_default_not_false")

    client = requests.Session()
    headers = _auth_headers(client, server_url, env)
    uploaded = _upload_flow(client, headers, server_url, flow_path, timeout_seconds)
    run_nonce = uuid.uuid4().hex
    sessions = {
        "deterministic": f"v6-http-det-{run_nonce}",
        "intent": f"v6-http-intent-{run_nonce}",
        "multiturn": f"v6-http-mt-{run_nonce}",
    }
    rows: list[dict[str, Any]] = []
    for case in CASES:
        try:
            row = _run_case(
                client,
                headers,
                server_url,
                str(uploaded["id"]),
                case,
                session_id=sessions[str(case["session_group"])],
                mongo_uri=mongo_uri,
                mongo_database=mongo_database,
                mongo_timeout_ms=mongo_timeout_ms,
                timeout_seconds=timeout_seconds,
            )
        except Exception as exc:
            row = {
                "case_id": case["case_id"],
                "session_group": case["session_group"],
                "expected_route": case["expected_route"],
                "expected_intent_llm_calls": case["expected_intent_calls"],
                "failure": _bounded_error(exc),
                "passed": False,
            }
        rows.append(row)
    multiturn = [row for row in rows if row.get("session_group") == "multiturn"]
    multiturn_check = len(multiturn) == 2 and [
        row.get("evidence", {}).get("state_version") for row in multiturn
    ] == [1, 2]
    report = {
        "contract_version": "langflow.http.e2e.validation.v1",
        "server_url_sha256": sha256(server_url.rstrip("/").encode("utf-8")).hexdigest(),
        "flow_file": flow_path.name,
        "flow_sha256": sha256_file(flow_path),
        "uploaded_flow_id": str(uploaded.get("id") or ""),
        "uploaded_endpoint_name": str(uploaded.get("endpoint_name") or ""),
        "upload_node_count": len((uploaded.get("data") or {}).get("nodes") or []),
        "model": DEFAULT_GEMINI_MODEL,
        "model_contract": gemini_model_contract_evidence(model),
        "flow_model_contract": flow_model_contract,
        "domain_id": metadata_release["domain_id"],
        "environment": metadata_release["environment"],
        "metadata_release": metadata_release,
        "metadata_source_mode": "three_collections_auto_latest",
        "validation_clock": validation_clock,
        "anonymous_multiturn_export_defaults": state_defaults,
        "anonymous_multiturn_validation_opt_in": True,
        "raw_langflow_responses_persisted": False,
        "prompts_persisted": False,
        "secrets_persisted": False,
        "case_count": len(rows),
        "passed": sum(1 for row in rows if row.get("passed") is True),
        "failed": sum(1 for row in rows if row.get("passed") is not True),
        "multiturn_state_progression": multiturn_check,
        "rows": rows,
    }
    report["all_passed"] = report["failed"] == 0 and multiturn_check
    assert_secret_absent(report, gemini_api_key)
    assert_secret_absent(report, langflow_api_key)
    assert_secret_absent(report, mongo_uri)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow", type=Path, default=DEFAULT_FLOW)
    parser.add_argument("--server-url", default="http://127.0.0.1:7873")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--model", default=DEFAULT_GEMINI_MODEL)
    parser.add_argument(
        "--domain-id",
        default="manufacturing",
        help="Expected identity of the latest usable three-collection release.",
    )
    parser.add_argument(
        "--environment",
        default="validation",
        help="Expected environment of the latest usable three-collection release.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs" / "langflow_http_e2e.json",
    )
    args = parser.parse_args()
    try:
        report = run(
            args.flow.resolve(),
            server_url=args.server_url,
            env_path=args.env_file.resolve(),
            model=args.model,
            domain_id=args.domain_id,
            environment=args.environment,
            timeout_seconds=max(30, min(args.timeout_seconds, 600)),
        )
    except Exception as exc:
        report = {
            "contract_version": "langflow.http.e2e.validation.v1",
            "all_passed": False,
            "failure": _bounded_error(exc),
        }
    write_json_atomic(args.output.resolve(), report)
    print(
        json.dumps(
            {
                key: report.get(key)
                for key in ("model", "case_count", "passed", "failed", "all_passed")
            },
            ensure_ascii=False,
        )
    )
    print(f"report: {args.output}")
    return 0 if report.get("all_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
