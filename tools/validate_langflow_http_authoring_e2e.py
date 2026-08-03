"""Validate the current v6 metadata-authoring Flows through Langflow HTTP.

The validator exercises the direct ``save`` contract for domain, dataset,
and main-filter authoring, plus one write-free
``validate_only`` probe.  Runtime metadata is verified through the fixed
domain/table-catalog/main-filter collections and through the selector-free
Domain Bundle Loader.  Persisted evidence contains hashes and counts only;
source text, provider output, HTTP bodies, and secrets are never written.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import sha256_json
from reference_runtime.domain_packages import validate_runtime_catalog_v2
from reference_runtime.metadata_collections import (
    METADATA_COLLECTIONS,
    load_available_domain_package_from_three_collections,
    load_domain_package_from_three_collections,
)
from tools.flow_builder_support import BuildContractError, sha256_file, write_json_atomic
from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    assert_secret_absent,
    gemini_model_contract_evidence,
    langflow_gemini_contract_evidence,
    load_dotenv_values,
    resolve_gemini_api_key,
)
from tools.validate_langflow_http_e2e import (
    _auth_headers,
    _bounded_error,
    _run_url,
    _upload_flow,
)


V6_INPUT_DIR = ROOT / "metadata" / "authoring" / "v6_inputs"
FREEFORM_REORDERED_INPUT_DIR = (
    ROOT / "validation" / "fixtures" / "authoring" / "freeform_reordered_v1"
)
DEFAULT_SOURCE_SET_ID = "manufacturing_worker_v6"
FREEFORM_REORDERED_SOURCE_SET_ID = "manufacturing_freeform_reordered_v1"
WORKER_INPUT_FILENAMES = {
    "domain": "domain_v6.txt",
    "dataset": "dataset_v6.txt",
    "main_filter": "main_filter_v6.txt",
}
AUTHORING_INPUT_PATHS = {
    kind: V6_INPUT_DIR / filename for kind, filename in WORKER_INPUT_FILENAMES.items()
}
AUTHORING_GEMINI_MODEL = "gemini-3.5-flash-lite"
FLOW_PATHS = (
    ROOT / "flow_exports" / "metadata_v6_domain_authoring_flow_v6_standalone.json",
    ROOT / "flow_exports" / "metadata_v6_dataset_catalog_authoring_flow_v6_standalone.json",
    ROOT / "flow_exports" / "metadata_v6_main_filter_authoring_flow_v6_standalone.json",
)
DEFAULT_OUTPUT = ROOT / "validation_outputs" / "langflow_http_authoring_e2e.json"
_SOURCE_SET_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_LOWER_HEX = frozenset("0123456789abcdef")
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


class AuthoringValidationError(RuntimeError):
    """Bounded validation failure safe to project into an evidence report."""

    def __init__(self, *, code: str, stage: str, details: dict[str, Any] | None = None):
        super().__init__(f"{code}:{stage}")
        self.code = str(code)[:80]
        self.stage = str(stage)[:80]
        self.details = deepcopy(details or {})


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in _LOWER_HEX for character in value)
    )


def _walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for nested in value.values():
            yield from _walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk(nested)


def _authoring_responses(value: Any) -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for item in _walk(value):
        if not isinstance(item, dict):
            continue
        if item.get("contract_version") != "metadata.authoring.response.v1":
            continue
        digest = str(item.get("response_sha256") or "")
        if _is_sha256(digest):
            found.setdefault(digest, item)
    return list(found.values())


def _message_response_hashes(value: Any) -> set[str]:
    hashes: set[str] = set()
    for item in _walk(value):
        if not isinstance(item, dict):
            continue
        metadata = item.get("session_metadata")
        if not isinstance(metadata, dict):
            continue
        if metadata.get("contract_version") != "metadata.authoring.message-link.v1":
            continue
        digest = str(metadata.get("response_sha256") or "")
        if _is_sha256(digest):
            hashes.add(digest)
    return hashes


def _output_blocks(value: Any) -> list[dict[str, Any]]:
    return [
        item
        for item in _walk(value)
        if isinstance(item, dict)
        and (item.get("component_id") or item.get("component_display_name"))
        and any(key in item for key in ("results", "outputs", "artifacts"))
    ]


def extract_authoring_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    """Project one canonical authoring response without retaining raw content."""

    responses = _authoring_responses(payload)
    response = responses[0] if len(responses) == 1 else {}
    digest = str(response.get("response_sha256") or "")
    computed = (
        sha256_json({key: value for key, value in response.items() if key != "response_sha256"})
        if response
        else ""
    )
    terminal_hashes: dict[str, set[str]] = {"message": set(), "api": set()}
    terminal_blocks = {"message": 0, "api": 0}
    for block in _output_blocks(payload):
        identity = (
            str(block.get("component_id") or "")
            + " "
            + str(block.get("component_display_name") or "")
        ).casefold()
        if (
            "message_presentation" in identity
            or "authoring message presentation" in identity
            or "chat_output" in identity
            or "chat output" in identity
        ):
            terminal_blocks["message"] += 1
            terminal_hashes["message"].update(_message_response_hashes(block))
        elif "api_response" in identity or "api response" in identity:
            terminal_blocks["api"] += 1
            terminal_hashes["api"].update(
                str(item.get("response_sha256") or "")
                for item in _authoring_responses(block)
            )

    terminal_projection = {
        key: sorted(values) for key, values in terminal_hashes.items()
    }
    usage = response.get("llm_usage") if isinstance(response.get("llm_usage"), dict) else {}
    error = response.get("error") if isinstance(response.get("error"), dict) else {}
    details = error.get("details") if isinstance(error.get("details"), dict) else {}
    unchanged = (
        response.get("unchanged_section_checks")
        if isinstance(response.get("unchanged_section_checks"), dict)
        else {}
    )
    validation = response.get("validation") if isinstance(response.get("validation"), dict) else {}
    diff = response.get("diff") if isinstance(response.get("diff"), dict) else {}
    return {
        "response_sha256": digest,
        "response_count": len(responses),
        "response_hash_valid": bool(digest) and digest == computed,
        "status": response.get("status"),
        "stage": response.get("stage"),
        "authoring_kind": response.get("authoring_kind"),
        "metadata_contract_mode": response.get("metadata_contract_mode"),
        "domain_id": response.get("domain_id"),
        "environment": response.get("environment"),
        "revision": int(response.get("revision") or 0),
        "candidate_id_sha256": (
            sha256(str(response.get("candidate_id") or "").encode("utf-8")).hexdigest()
            if response.get("candidate_id")
            else ""
        ),
        "candidate_sha256": str(response.get("candidate_sha256") or ""),
        "package_sha256": str(response.get("package_sha256") or ""),
        "bundle_sha256": str(response.get("bundle_sha256") or ""),
        "catalog_sha256": str(response.get("catalog_sha256") or ""),
        "persisted": response.get("persisted"),
        "idempotent_replay": response.get("idempotent_replay"),
        "draft_llm_calls": int(usage.get("draft_llm_calls") or 0),
        "annotation_llm_calls": int(usage.get("annotation_llm_calls") or 0),
        "repair_llm_calls": int(usage.get("repair_llm_calls") or 0),
        "diff_sha256": sha256_json(diff) if diff else "",
        "validation_sha256": sha256_json(validation) if validation else "",
        "unchanged_section_count": len(unchanged),
        "unchanged_sections_all": all(value is True for value in unchanged.values()),
        "error_code": str(error.get("code") or "")[:80],
        "error_stage": str(error.get("stage") or "")[:80],
        "error_detail_keys": sorted(str(key)[:80] for key in details)[:32],
        "terminal_blocks": terminal_blocks,
        "terminal_hashes": terminal_projection,
        "terminal_equivalent": bool(digest)
        and all(terminal_blocks[key] >= 1 for key in ("message", "api"))
        and all(terminal_projection[key] == [digest] for key in ("message", "api")),
        "raw_provider_output_persisted": False,
        "raw_http_response_persisted": False,
    }


def _field_value(template: dict[str, Any], name: str) -> Any:
    field = template.get(name)
    return field.get("value") if isinstance(field, dict) else None


def _flow_defaults(path: Path) -> dict[str, Any]:
    flow = json.loads(path.read_text(encoding="utf-8"))
    nodes = {
        str(node.get("id") or ""): node
        for node in flow.get("data", {}).get("nodes", [])
        if isinstance(node, dict)
    }
    engine = nodes.get("simple_metadata_authoring_engine", {})
    template = (((engine.get("data") or {}).get("node") or {}).get("template") or {})
    generator = nodes.get("simple_metadata_draft_generator", {})
    generator_node = ((generator.get("data") or {}).get("node") or {})
    generator_metadata = generator_node.get("metadata") or {}
    kind = str(generator_metadata.get("authoring_kind") or "")
    model_contract = langflow_gemini_contract_evidence(flow, require_model=True)
    model_node = nodes.get("draft_language_model", {})
    model_template = (((model_node.get("data") or {}).get("node") or {}).get("template") or {})
    model_rows = _field_value(model_template, "model") or []
    model_names = sorted(
        str(row.get("name") or "")
        for row in model_rows
        if isinstance(row, dict) and row.get("name")
    )
    collection_defaults = {
        "domain_collection": _field_value(template, "domain_collection"),
        "table_collection": _field_value(template, "table_collection"),
        "main_filter_collection": _field_value(template, "main_filter_collection"),
    }
    checks = {
        "mode_save": _field_value(template, "mode") == "save",
        "selector_inputs_absent": all(
            _field_value(template, name) is None
            for name in ("authoring_kind", "domain_id", "environment", "dry_run")
        ),
        "fixed_three_collections": collection_defaults
        == {
            "domain_collection": METADATA_COLLECTIONS["domain"],
            "table_collection": METADATA_COLLECTIONS["table_catalog"],
            "main_filter_collection": METADATA_COLLECTIONS["main_filter"],
        },
        "model_contract": model_contract.get("passed") is True,
        "model_exact": model_names == [AUTHORING_GEMINI_MODEL],
    }
    return {
        "file": path.name,
        "flow_sha256": sha256_file(path),
        "endpoint_name": str(flow.get("endpoint_name") or ""),
        "authoring_kind": kind,
        "mode": _field_value(template, "mode"),
        "collection_defaults": collection_defaults,
        "model_names": model_names,
        "model_contract": model_contract,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _fresh_environment(prefix: str, nonce: str) -> str:
    normalized = "".join(
        character if character.isascii() and (character.isalnum() or character in "_-") else "_"
        for character in str(prefix or "validation").casefold()
    ).strip("_-")
    normalized = normalized or "validation"
    return f"{normalized[:18]}_{nonce[:12]}"


def _load_v6_authoring_sources(
    *, worker_input_dir: Path, source_set_id: str
) -> tuple[dict[str, str], dict[str, str], dict[str, Any]]:
    normalized_source_set_id = str(source_set_id or "").strip().casefold()
    if not _SOURCE_SET_ID_PATTERN.fullmatch(normalized_source_set_id):
        raise BuildContractError("authoring_source_set_id_invalid")
    sources: dict[str, str] = {}
    resolved_paths: dict[str, Path] = {}
    for kind, filename in WORKER_INPUT_FILENAMES.items():
        candidate = worker_input_dir / filename
        if not candidate.is_file():
            raise BuildContractError(f"authoring_source_missing:{kind}")
        text = candidate.read_text(encoding="utf-8").strip()
        if not text:
            raise BuildContractError(f"authoring_source_empty:{kind}")
        sources[kind] = text
        resolved_paths[kind] = candidate
    hashes = {
        kind: sha256(text.encode("utf-8")).hexdigest()
        for kind, text in sources.items()
    }
    evidence = {
        "source_set_id": normalized_source_set_id,
        "source_set_id_sha256": sha256(normalized_source_set_id.encode("utf-8")).hexdigest(),
        "worker_input_dir_sha256": sha256(str(worker_input_dir).encode("utf-8")).hexdigest(),
        "raw_source_text_persisted": False,
    }
    return sources, hashes, evidence


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
) -> tuple[int, str, dict[str, Any]]:
    response = client.post(
        _run_url(server_url, flow_id, headers),
        headers={**headers, "Content-Type": "application/json"},
        json={
            "input_value": input_value,
            "input_type": "chat",
            "output_type": "any",
            "session_id": session_id,
            "tweaks": tweaks,
        },
        timeout=timeout_seconds,
    )
    response_sha256 = sha256(response.content).hexdigest()
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise BuildContractError("langflow_authoring_response_invalid")
    return response.status_code, response_sha256, payload


def _authoring_tweaks(
    *,
    kind: str,
    mode: str,
    domain_id: str,
    environment: str,
    mongo_uri: str,
    mongo_database: str,
    sources: dict[str, str],
) -> dict[str, Any]:
    if mode not in {"save", "replace", "validate_only"}:
        raise ValueError("authoring_mode_invalid")
    tweaks: dict[str, Any] = {
        "simple_metadata_authoring_engine": {
            "mode": mode,
            "mongo_uri": mongo_uri,
            "mongo_database": mongo_database,
            "mongo_timeout_ms": 10000,
        },
    }
    del kind, domain_id, environment
    tweaks["draft_language_model"] = {"temperature": 0.0, "stream": False}
    return tweaks


def _document_snapshot(database: Any, *, domain_id: str, environment: str) -> dict[str, Any]:
    current_id = f"{environment}:{domain_id}"
    rows: dict[str, Any] = {}
    for kind, collection_name in METADATA_COLLECTIONS.items():
        document = database[collection_name].find_one({"_id": current_id}) or {}
        rows[kind] = {
            "present": bool(document),
            "revision": int(document.get("revision") or 0),
            "release_id_sha256": (
                sha256(str(document.get("release_id") or "").encode("utf-8")).hexdigest()
                if document.get("release_id")
                else ""
            ),
            "document_sha256": str(document.get("document_sha256") or ""),
        }
    return {
        "rows": rows,
        "snapshot_sha256": sha256_json(rows),
        "document_count": sum(1 for row in rows.values() if row["present"]),
    }


def _release_evidence(database: Any, *, domain_id: str, environment: str) -> tuple[dict[str, Any], dict[str, Any]]:
    package = load_domain_package_from_three_collections(database, domain_id, environment)
    current_id = f"{environment}:{domain_id}"
    documents = {
        kind: database[name].find_one({"_id": current_id}) or {}
        for kind, name in METADATA_COLLECTIONS.items()
    }
    release_ids = {str(document.get("release_id") or "") for document in documents.values()}
    revisions = {int(document.get("revision") or 0) for document in documents.values()}
    source_present = {
        kind: bool(str(document.get("source_text") or "").strip())
        for kind, document in documents.items()
    }
    release_id = next(iter(release_ids), "")
    checks = {
        "three_documents_present": all(bool(document) for document in documents.values()),
        "one_release": len(release_ids) == 1 and bool(release_id),
        "one_revision": revisions == {int(package.get("revision") or 0)},
        "source_text_present": all(source_present.values()),
        "identity_exact": package.get("domain_id") == domain_id
        and package.get("environment") == environment,
    }
    if not all(checks.values()):
        raise AuthoringValidationError(
            code="three_collection_release_invalid",
            stage="metadata_three_collection",
            details={"failed_checks": sorted(key for key, value in checks.items() if not value)},
        )
    evidence = {
        "domain_id": domain_id,
        "environment": environment,
        "revision": int(package["revision"]),
        "package_sha256": str(package["package_sha256"]),
        "bundle_sha256": str(package["bundle_sha256"]),
        "catalog_sha256": str((package.get("runtime_catalog") or {}).get("catalog_sha256") or ""),
        "release_id_sha256": sha256(release_id.encode("utf-8")).hexdigest(),
        "source_present": source_present,
        "checks": checks,
    }
    return package, evidence


def _validate_loader_runtime_bundle(
    context: Any,
    *,
    expected_domain_id: str,
    expected_environment: str,
) -> dict[str, Any]:
    context_value = deepcopy(context) if isinstance(context, dict) else {}
    bundle = (
        deepcopy(context_value.get("domain_bundle"))
        if isinstance(context_value.get("domain_bundle"), dict)
        else {}
    )
    checks = {
        "context_keys_exact": set(context_value) == _LOADER_CONTEXT_KEYS,
        "context_contract_exact": context_value.get("contract_version") == "pipeline.context.v1",
        "context_ok": context_value.get("ok") is True,
        "context_stage_exact": context_value.get("stage") == "domain_bundle",
        "bundle_keys_exact": set(bundle) == _LOADER_RUNTIME_BUNDLE_KEYS,
        "bundle_contract_exact": bundle.get("contract_version") == "domain.bundle.runtime.v1",
        "source_mode_exact": bundle.get("source_mode") == "three_collections",
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
    failed = sorted(key for key, value in checks.items() if value is not True)
    if failed:
        raise AuthoringValidationError(
            code="loader_runtime_projection_invalid",
            stage="loader_roundtrip",
            details={"failed_checks": failed},
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

    source = (
        ROOT / "langflow_components" / "data_analysis" / "domain_bundle_loader.py"
    ).read_text(encoding="utf-8")
    component_cls = eval_custom_component_code(source)
    component = component_cls()
    input_names = {str(item.name) for item in component.inputs}
    expected_inputs = {"mongo_uri", "mongo_database", "mongo_timeout_ms"}
    if input_names != expected_inputs:
        raise AuthoringValidationError(
            code="loader_input_contract_invalid",
            stage="loader_roundtrip",
            details={"input_names": sorted(input_names)},
        )
    component.mongo_uri = mongo_uri
    component.mongo_database = database_name
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
        "selection": "latest_available_release",
        "input_names": sorted(input_names),
        "domain_id": runtime_bundle.get("domain_id"),
        "environment": runtime_bundle.get("environment"),
        "revision": runtime_bundle.get("revision"),
        "package_sha256": runtime_bundle.get("package_sha256"),
        "bundle_sha256": runtime_bundle.get("bundle_sha256"),
        "catalog_sha256": runtime_bundle.get("catalog_sha256"),
    }


def _run_authoring_case(
    *,
    client: requests.Session,
    headers: dict[str, str],
    server_url: str,
    flow_id: str,
    kind: str,
    mode: str,
    input_value: str,
    expected_revision: int,
    expected_draft_calls: int,
    domain_id: str,
    environment: str,
    mongo_uri: str,
    mongo_database: str,
    sources: dict[str, str],
    timeout_seconds: int,
) -> dict[str, Any]:
    status, http_hash, payload = _post_run(
        client,
        headers,
        server_url,
        flow_id,
        input_value=input_value,
        session_id=f"v6-authoring-{kind}-{mode}-{uuid.uuid4().hex}",
        tweaks=_authoring_tweaks(
            kind=kind,
            mode=mode,
            domain_id=domain_id,
            environment=environment,
            mongo_uri=mongo_uri,
            mongo_database=mongo_database,
            sources=sources,
        ),
        timeout_seconds=timeout_seconds,
    )
    evidence = extract_authoring_evidence(payload)
    expected_stage = "committed" if mode == "save" else "validated"
    expected_persisted = mode == "save"
    checks = {
        "http_200": status == 200,
        "one_response": evidence["response_count"] == 1,
        "response_hash_valid": evidence["response_hash_valid"] is True,
        "status_ok": evidence["status"] == "ok",
        "stage_exact": evidence["stage"] == expected_stage,
        "kind_exact": evidence["authoring_kind"] == kind,
        "contract_mode_v2": evidence["metadata_contract_mode"] == "domain_package_v2",
        "identity_exact": evidence["domain_id"] == domain_id
        and evidence["environment"] == environment,
        "revision_exact": evidence["revision"] == expected_revision,
        "persisted_exact": evidence["persisted"] is expected_persisted,
        "candidate_hash_valid": _is_sha256(evidence["candidate_sha256"]),
        "package_hash_valid": _is_sha256(evidence["package_sha256"]),
        "bundle_hash_valid": _is_sha256(evidence["bundle_sha256"]),
        "catalog_hash_valid": _is_sha256(evidence["catalog_sha256"]),
        "draft_llm_exact": evidence["draft_llm_calls"] == expected_draft_calls,
        "annotation_llm_zero": evidence["annotation_llm_calls"] == 0,
        "repair_llm_zero": evidence["repair_llm_calls"] == 0,
        "terminal_equivalent": evidence["terminal_equivalent"] is True,
    }
    return {
        "authoring_kind": kind,
        "mode": mode,
        "http_status": status,
        "http_response_sha256": http_hash,
        "evidence": evidence,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _safe_failure(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, AuthoringValidationError):
        details = exc.details if isinstance(exc.details, dict) else {}
        return {
            "type": "AuthoringValidationError",
            "code": exc.code,
            "stage": exc.stage,
            "details": {
                str(key)[:80]: value
                for key, value in details.items()
                if key in {"failed_checks", "input_names"}
            },
        }
    bounded = _bounded_error(exc)
    return {**bounded, "stage": "http_or_runtime", "details": {}}


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
    mongo_database = str(
        os.getenv("MONGODB_DATABASE")
        or env.get("MONGODB_DATABASE")
        or os.getenv("MONGODB_VALIDATION_DATABASE")
        or env.get("MONGODB_VALIDATION_DATABASE")
        or "datagov_v6_validation"
    ).strip()
    if not mongo_uri:
        raise BuildContractError("mongodb_uri_not_configured")
    if DEFAULT_GEMINI_MODEL != AUTHORING_GEMINI_MODEL:
        raise BuildContractError("authoring_gemini_model_constant_drift")

    if str(domain_id or "default").strip() != "default" or str(
        environment or "production"
    ).strip() != "production":
        raise BuildContractError("simple_authoring_identity_is_fixed_to_default_production")
    domain_id = "default"
    effective_environment = "production"
    sources, source_hashes, source_evidence = _load_v6_authoring_sources(
        worker_input_dir=worker_input_dir,
        source_set_id=source_set_id,
    )
    defaults = [_flow_defaults(path) for path in FLOW_PATHS]
    defaults_ok = [row["authoring_kind"] for row in defaults] == [
        "domain",
        "dataset",
        "main_filter",
    ] and all(row["passed"] for row in defaults)
    model_contract = gemini_model_contract_evidence()
    exact_gemini_no_fallback = (
        model_contract.get("requested_model") == AUTHORING_GEMINI_MODEL
        and model_contract.get("temperature") == 0
        and model_contract.get("candidate_count") == 1
        and model_contract.get("fallback_enabled") is False
        and model_contract.get("fallback_models") == []
    )

    http = requests.Session()
    headers = _auth_headers(http, server_url, env)
    uploaded = [
        _upload_flow(http, headers, server_url, path, timeout_seconds)
        for path in FLOW_PATHS
    ]
    imports = [
        {
            "file": path.name,
            "flow_sha256": sha256_file(path),
            "flow_id_sha256": sha256(str(record.get("id") or "").encode("utf-8")).hexdigest(),
            "endpoint_name": str(record.get("endpoint_name") or ""),
            "node_count": len((record.get("data") or {}).get("nodes") or []),
        }
        for path, record in zip(FLOW_PATHS, uploaded, strict=True)
    ]

    mongo = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    database = mongo[mongo_database]
    try:
        initial_snapshot = _document_snapshot(
            database, domain_id=domain_id, environment=effective_environment
        )
        if initial_snapshot["document_count"] != 0:
            raise AuthoringValidationError(
                code="fresh_validation_release_not_empty",
                stage="metadata_three_collection",
            )

        specs = (
            ("domain", 0, 1, 1),
            ("dataset", 1, 2, 1),
            ("main_filter", 2, 3, 1),
        )
        save_rows: list[dict[str, Any]] = []
        releases: list[dict[str, Any]] = []
        for kind, flow_index, revision, draft_calls in specs:
            row = _run_authoring_case(
                client=http,
                headers=headers,
                server_url=server_url,
                flow_id=str(uploaded[flow_index]["id"]),
                kind=kind,
                mode="save",
                input_value=sources[kind],
                expected_revision=revision,
                expected_draft_calls=draft_calls,
                domain_id=domain_id,
                environment=effective_environment,
                mongo_uri=mongo_uri,
                mongo_database=mongo_database,
                sources=sources,
                timeout_seconds=timeout_seconds,
            )
            package, release = _release_evidence(
                database, domain_id=domain_id, environment=effective_environment
            )
            row["release_checks"] = {
                "revision_exact": release["revision"] == revision,
                "package_hash_exact": release["package_sha256"]
                == row["evidence"]["package_sha256"],
                "bundle_hash_exact": release["bundle_sha256"]
                == row["evidence"]["bundle_sha256"],
                "catalog_hash_exact": release["catalog_sha256"]
                == row["evidence"]["catalog_sha256"],
            }
            row["passed"] = row["passed"] and all(row["release_checks"].values())
            save_rows.append(row)
            releases.append(release)

        before_validate_only = _document_snapshot(
            database, domain_id=domain_id, environment=effective_environment
        )
        validate_only = _run_authoring_case(
            client=http,
            headers=headers,
            server_url=server_url,
            flow_id=str(uploaded[2]["id"]),
            kind="main_filter",
            mode="validate_only",
            input_value=sources["main_filter"],
            expected_revision=4,
            expected_draft_calls=1,
            domain_id=domain_id,
            environment=effective_environment,
            mongo_uri=mongo_uri,
            mongo_database=mongo_database,
            sources=sources,
            timeout_seconds=timeout_seconds,
        )
        after_validate_only = _document_snapshot(
            database, domain_id=domain_id, environment=effective_environment
        )
        validate_only_checks = {
            "documents_unchanged": before_validate_only == after_validate_only,
            "stored_revision_still_three": all(
                row["revision"] == 3
                for row in after_validate_only["rows"].values()
            ),
        }
        validate_only["write_free_checks"] = validate_only_checks
        validate_only["passed"] = validate_only["passed"] and all(
            validate_only_checks.values()
        )

        latest_package, latest_release = _release_evidence(
            database, domain_id=domain_id, environment=effective_environment
        )

        auto_selected = load_available_domain_package_from_three_collections(database)
        auto_selection_checks = {
            "identity_exact": auto_selected.get("domain_id") == domain_id
            and auto_selected.get("environment") == effective_environment,
            "revision_exact": int(auto_selected.get("revision") or 0) == 3,
            "package_hash_exact": auto_selected.get("package_sha256")
            == latest_package.get("package_sha256"),
        }
        loader = _loader_roundtrip(
            mongo_uri=mongo_uri,
            database_name=mongo_database,
            domain_id=domain_id,
            environment=effective_environment,
        )
    finally:
        mongo.close()

    loader_checks = {
        "loader_ok": loader["ok"] is True,
        "identity_exact": loader["domain_id"] == domain_id
        and loader["environment"] == effective_environment,
        "revision_exact": int(loader["revision"] or 0) == 3,
        "package_hash_exact": loader["package_sha256"] == latest_release["package_sha256"],
        "bundle_hash_exact": loader["bundle_sha256"] == latest_release["bundle_sha256"],
        "catalog_hash_exact": loader["catalog_sha256"] == latest_release["catalog_sha256"],
    }
    revision_chain_exact = [row["revision"] for row in releases] == [1, 2, 3]
    report = {
        "contract_version": "langflow.http.authoring-e2e.validation.v4",
        "model": AUTHORING_GEMINI_MODEL,
        "model_contract": model_contract,
        "exact_gemini_no_fallback": exact_gemini_no_fallback,
        "environment": effective_environment,
        "domain_id": domain_id,
        "database_sha256": sha256(mongo_database.encode("utf-8")).hexdigest(),
        "source_set": source_evidence,
        "source_hashes": source_hashes,
        "metadata_authority": "three_collections",
        "source_text_persisted": False,
        "provider_output_persisted": False,
        "raw_http_responses_persisted": False,
        "secrets_persisted": False,
        "flow_defaults": defaults,
        "flow_defaults_passed": defaults_ok,
        "imports": imports,
        "initial_release_empty": initial_snapshot["document_count"] == 0,
        "save_cycles": save_rows,
        "validate_only_probe": validate_only,
        "revision_chain_exact": revision_chain_exact,
        "latest_release": latest_release,
        "auto_selection_checks": auto_selection_checks,
        "loader_roundtrip": loader,
        "loader_checks": loader_checks,
    }
    report["all_passed"] = (
        defaults_ok
        and exact_gemini_no_fallback
        and report["initial_release_empty"]
        and all(row["passed"] for row in save_rows)
        and validate_only["passed"]
        and revision_chain_exact
        and all(auto_selection_checks.values())
        and all(loader_checks.values())
    )
    assert_secret_absent(report, gemini_key)
    assert_secret_absent(report, langflow_key)
    assert_secret_absent(report, mongo_uri)
    serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
    if any(source in serialized for source in sources.values()):
        raise AuthoringValidationError(
            code="raw_source_text_leaked",
            stage="report_redaction",
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-url", default="http://127.0.0.1:7873")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--environment", default="production", help=argparse.SUPPRESS)
    parser.add_argument("--domain-id", default="default", help=argparse.SUPPRESS)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--worker-input-dir", type=Path, default=V6_INPUT_DIR)
    parser.add_argument("--source-set-id", default=DEFAULT_SOURCE_SET_ID)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        report = run(
            server_url=args.server_url,
            env_path=args.env_file.resolve(),
            environment=args.environment,
            domain_id=args.domain_id,
            timeout_seconds=max(60, min(args.timeout_seconds, 900)),
            worker_input_dir=args.worker_input_dir.resolve(),
            source_set_id=args.source_set_id,
        )
    except Exception as exc:
        report = {
            "contract_version": "langflow.http.authoring-e2e.validation.v4",
            "model": AUTHORING_GEMINI_MODEL,
            "all_passed": False,
            "failure": _safe_failure(exc),
            "source_text_persisted": False,
            "provider_output_persisted": False,
            "raw_http_responses_persisted": False,
            "secrets_persisted": False,
        }
    write_json_atomic(args.output.resolve(), report)
    print(
        json.dumps(
            {
                key: report.get(key)
                for key in (
                    "model",
                    "domain_id",
                    "environment",
                    "revision_chain_exact",
                    "all_passed",
                )
            },
            ensure_ascii=False,
        )
    )
    print(f"report: {args.output}")
    return 0 if report.get("all_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
