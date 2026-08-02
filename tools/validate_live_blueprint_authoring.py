"""Validate the production full-domain authoring boundary with one Gemini call.

The reviewed executable blueprint and its independently stored SHA-256 pin are
validated before a model is reachable.  Gemini may propose only the display
name and description.  The deterministic compiler then proves that canonical
executable bytes are unchanged and replays the same provider response through
the generated standalone Langflow component.

Reports intentionally exclude source text, prompts, provider text, blueprint
JSON, annotations, credentials and MongoDB configuration.  Only bounded hashes,
counts, model usage and pass/fail evidence are persisted.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.authoring_blueprint import (
    ANNOTATION_KEYS,
    EXECUTABLE_KEYS,
    build_executable_blueprint,
    compute_blueprint_sha256,
    merge_blueprint_annotations,
    validate_executable_blueprint,
)
from reference_runtime.authoring_source_manifest import extract_authoring_source_manifest
from reference_runtime.canonical import ContractError, canonical_bytes, sha256_json
from reference_runtime.contracts import validate_contract
from reference_runtime.domain_packages import (
    compile_domain_package,
    make_active_pointer_document,
    make_bundle_document,
    validate_domain_package,
    validate_runtime_catalog_v2,
)
from tools.gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    GeminiJsonModel,
    assert_secret_absent,
    gemini_model_contract_evidence,
    require_exact_gemini_model,
    resolve_gemini_api_key,
)


DEFAULT_SOURCE = ROOT / "validation" / "order_sales_metadata_input.txt"
DEFAULT_BLUEPRINT = (
    ROOT
    / "metadata"
    / "domain_packs"
    / "order_sales"
    / "trusted_executable_blueprint.json"
)
DEFAULT_BLUEPRINT_PIN = DEFAULT_BLUEPRINT.with_suffix(".sha256")
AUTHORING_COMPONENT = (
    ROOT
    / "langflow_components"
    / "metadata_authoring"
    / "00_metadata_authoring_engine.py"
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ReplayModel:
    """Replay one already-paid response without making another provider call."""

    def __init__(self, response: str) -> None:
        self.response = str(response)
        self.calls = 0

    def invoke(self, prompt: str) -> str:
        self.calls += 1
        return self.response


class GuardModel:
    """Detect whether a fail-closed blueprint case reaches the LLM boundary."""

    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, prompt: str) -> str:
        self.calls += 1
        raise RuntimeError("guard_model_called")


def _response_data(value: Any) -> dict[str, Any]:
    raw = getattr(value, "data", value)
    if not isinstance(raw, dict):
        raise RuntimeError("authoring_component_non_object_response")
    return raw


def _json_object_text(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0].strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < start:
        raise RuntimeError("annotation_json_missing")
    try:
        value = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        raise RuntimeError("annotation_json_invalid") from None
    if not isinstance(value, dict):
        raise RuntimeError("annotation_not_object")
    return value


def _safe_reason(exc: BaseException) -> dict[str, Any]:
    if isinstance(exc, ContractError):
        details = exc.details if isinstance(exc.details, dict) else {}
        reason = str(details.get("reason") or "")
        if not reason or len(reason) > 96 or not all(
            character.isalnum() or character == "_" for character in reason
        ):
            reason = "contract_rejected"
        return {
            "code": str(exc.code)[:96],
            "stage": str(exc.stage)[:96],
            "reason": reason,
        }
    message = str(exc).splitlines()[0][:96]
    if message.startswith("gemini_") and all(
        character.isalnum() or character == "_" for character in message
    ):
        return {"code": message, "stage": "provider", "reason": "provider_failure"}
    if message in {
        "annotation_json_missing",
        "annotation_json_invalid",
        "annotation_not_object",
        "authoring_component_non_object_response",
        "authoring_component_blueprint_contract_missing",
        "trusted_blueprint_missing",
        "trusted_blueprint_pin_missing",
        "trusted_blueprint_pin_invalid",
    }:
        return {"code": message, "stage": "validation", "reason": message}
    return {
        "code": f"validation_{type(exc).__name__}",
        "stage": "validation",
        "reason": "bounded_failure",
    }


def _component_contract() -> tuple[type, dict[str, Any]]:
    from lfx.custom.eval import eval_custom_component_code

    source = AUTHORING_COMPONENT.read_text(encoding="utf-8")
    component_cls = eval_custom_component_code(source)
    method = getattr(component_cls, "run_authoring", None)
    if method is None:
        raise RuntimeError("authoring_component_blueprint_contract_missing")
    namespace = method.__globals__
    required = {
        "_v2_domain_annotation_prompt",
        "merge_blueprint_annotations",
        "validate_executable_blueprint",
    }
    if any(not callable(namespace.get(name)) for name in required):
        raise RuntimeError("authoring_component_blueprint_contract_missing")
    input_names = {str(item.name) for item in getattr(component_cls, "inputs", [])}
    if not {"trusted_blueprint_json", "trusted_blueprint_sha256"} <= input_names:
        raise RuntimeError("authoring_component_blueprint_contract_missing")
    return component_cls, namespace


def _annotation_prompt(source_text: str, default_annotations: dict[str, str]) -> str:
    """Return the exact helper embedded in the generated standalone node."""

    _component_cls, namespace = _component_contract()
    return str(namespace["_v2_domain_annotation_prompt"](source_text, default_annotations))


def _read_external_pin(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError("trusted_blueprint_pin_missing")
    pin = path.read_text(encoding="ascii").strip()
    if not _SHA256_RE.fullmatch(pin):
        raise RuntimeError("trusted_blueprint_pin_invalid")
    return pin


def _load_trusted_blueprint(
    *,
    blueprint_path: Path,
    pin_path: Path,
    source_manifest: dict[str, Any],
    domain_id: str,
    environment: str,
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    """Load the reviewed artifact and derive an isolated-env admin artifact.

    The sidecar pin is the trust anchor for the checked-in artifact.  When a
    validator requests a fresh environment, the already validated executable
    is rebound only through the trusted administrative build helper.  Its pin
    is passed to the component as a separate configuration input.
    """

    if not blueprint_path.is_file():
        raise RuntimeError("trusted_blueprint_missing")
    external_pin = _read_external_pin(pin_path)
    raw = json.loads(blueprint_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError("trusted_blueprint_missing")
    base_domain = str(raw.get("domain_id") or "")
    base_environment = str(raw.get("environment") or "")
    base = validate_executable_blueprint(
        raw,
        expected_blueprint_sha256=external_pin,
        expected_domain_id=base_domain,
        expected_environment=base_environment,
        source_manifest=source_manifest,
    )
    target = base
    target_pin = external_pin
    rebound = base_domain != domain_id or base_environment != environment
    if rebound:
        reviewed_draft = {
            **deepcopy(base["executable"]),
            **deepcopy(base["default_annotations"]),
        }
        target = build_executable_blueprint(
            reviewed_draft,
            domain_id=domain_id,
            environment=environment,
            source_manifest=source_manifest,
        )
        target_pin = str(target["blueprint_sha256"])
        validate_executable_blueprint(
            target,
            expected_blueprint_sha256=target_pin,
            expected_domain_id=domain_id,
            expected_environment=environment,
            source_manifest=source_manifest,
        )
    evidence = {
        "checked_in_blueprint_sha256": external_pin,
        "target_blueprint_sha256": target_pin,
        "executable_sha256": str(target.get("executable_sha256") or ""),
        "source_manifest_sha256": str(target.get("source_manifest_sha256") or ""),
        "environment_rebound_by_admin_build": rebound,
        "checked_in_pin_source": "separate_admin_sidecar",
        "target_pin_source": (
            "trusted_admin_build_output" if rebound else "separate_admin_sidecar"
        ),
    }
    return target, target_pin, evidence


def _component_instance(
    component_cls: type,
    *,
    source_text: str,
    model: Any,
    blueprint_json: str,
    blueprint_pin: str,
    domain_id: str,
    environment: str,
    revision: int,
) -> Any:
    from lfx.schema.message import Message

    component = component_cls()
    component.input_message = Message(
        text=source_text,
        session_id=f"blueprint-authoring-{domain_id}",
    )
    component.language_model = model
    component.authoring_kind = "domain"
    component.metadata_contract_mode = "domain_package_v2"
    component.domain_id = domain_id
    component.environment = environment
    component.revision_policy = "explicit"
    component.revision = revision
    component.trusted_blueprint_json = blueprint_json
    component.trusted_blueprint_sha256 = blueprint_pin
    component.mode = "prepare"
    component.dry_run = True
    component.candidate_ttl_seconds = 3600
    return component


def _component_replay(
    *,
    raw_response: str,
    source_text: str,
    blueprint: dict[str, Any],
    blueprint_pin: str,
    domain_id: str,
    environment: str,
    revision: int,
) -> tuple[dict[str, Any], int]:
    component_cls, _namespace = _component_contract()
    replay = ReplayModel(raw_response)
    component = _component_instance(
        component_cls,
        source_text=source_text,
        model=replay,
        blueprint_json=json.dumps(blueprint, ensure_ascii=False, separators=(",", ":")),
        blueprint_pin=blueprint_pin,
        domain_id=domain_id,
        environment=environment,
        revision=revision,
    )
    return _response_data(component.run_authoring()), replay.calls


def _error_reason_from_response(response: dict[str, Any]) -> str:
    error = response.get("error") if isinstance(response.get("error"), dict) else {}
    details = error.get("details") if isinstance(error.get("details"), dict) else {}
    reason = str(details.get("reason") or "")
    return reason if len(reason) <= 96 else ""


def _negative_row(
    case_id: str,
    action: Callable[[], Any],
    *,
    expected_reason: str,
) -> dict[str, Any]:
    try:
        action()
    except Exception as exc:
        failure = _safe_reason(exc)
        checks = {
            "rejected": True,
            "reason_exact": failure.get("reason") == expected_reason,
            "model_calls_zero": True,
        }
        return {
            "case_id": case_id,
            "failure": failure,
            "model_calls": 0,
            "checks": checks,
            "passed": all(checks.values()),
        }
    return {
        "case_id": case_id,
        "model_calls": 0,
        "checks": {"rejected": False, "reason_exact": False, "model_calls_zero": True},
        "passed": False,
    }


def _direct_negative_cases(
    *,
    blueprint: dict[str, Any],
    blueprint_pin: str,
    domain_id: str,
    environment: str,
    source_manifest: dict[str, Any],
    source_text: str,
) -> list[dict[str, Any]]:
    simple_tamper = deepcopy(blueprint)
    output_profile = simple_tamper["executable"].get("output_profile")
    if not isinstance(output_profile, dict):
        raise RuntimeError("trusted_blueprint_missing")
    current_limit = int(output_profile.get("default_row_limit") or 20)
    output_profile["default_row_limit"] = current_limit + 1

    recomputed_tamper = deepcopy(simple_tamper)
    recomputed_tamper["executable_sha256"] = sha256_json(recomputed_tamper["executable"])
    recomputed_tamper["blueprint_sha256"] = compute_blueprint_sha256(recomputed_tamper)
    wrong_manifest = extract_authoring_source_manifest(
        source_text + "\n검증용 비실행 설명 문장을 추가합니다."
    )
    wrong_pin = "0" * 64 if blueprint_pin != "0" * 64 else "1" * 64

    shared = {
        "expected_domain_id": domain_id,
        "expected_environment": environment,
        "source_manifest": source_manifest,
    }
    cases = [
        _negative_row(
            "missing_blueprint",
            lambda: validate_executable_blueprint(
                None, expected_blueprint_sha256=blueprint_pin, **shared
            ),
            expected_reason="blueprint_not_object",
        ),
        _negative_row(
            "missing_external_pin",
            lambda: validate_executable_blueprint(
                blueprint, expected_blueprint_sha256="", **shared
            ),
            expected_reason="sha256_invalid",
        ),
        _negative_row(
            "wrong_external_pin",
            lambda: validate_executable_blueprint(
                blueprint, expected_blueprint_sha256=wrong_pin, **shared
            ),
            expected_reason="blueprint_external_pin_mismatch",
        ),
        _negative_row(
            "simple_executable_tamper",
            lambda: validate_executable_blueprint(
                simple_tamper, expected_blueprint_sha256=blueprint_pin, **shared
            ),
            expected_reason="executable_hash_mismatch",
        ),
        _negative_row(
            "recomputed_executable_tamper",
            lambda: validate_executable_blueprint(
                recomputed_tamper, expected_blueprint_sha256=blueprint_pin, **shared
            ),
            expected_reason="blueprint_external_pin_mismatch",
        ),
        _negative_row(
            "wrong_domain_pin",
            lambda: validate_executable_blueprint(
                blueprint,
                expected_blueprint_sha256=blueprint_pin,
                expected_domain_id=f"{domain_id}_wrong"[:64],
                expected_environment=environment,
                source_manifest=source_manifest,
            ),
            expected_reason="domain_pin_mismatch",
        ),
        _negative_row(
            "wrong_environment_pin",
            lambda: validate_executable_blueprint(
                blueprint,
                expected_blueprint_sha256=blueprint_pin,
                expected_domain_id=domain_id,
                expected_environment=f"{environment[:25]}_wrong"[:31],
                source_manifest=source_manifest,
            ),
            expected_reason="environment_pin_mismatch",
        ),
        _negative_row(
            "wrong_source_manifest",
            lambda: validate_executable_blueprint(
                blueprint,
                expected_blueprint_sha256=blueprint_pin,
                expected_domain_id=domain_id,
                expected_environment=environment,
                source_manifest=wrong_manifest,
            ),
            expected_reason="source_manifest_pin_mismatch",
        ),
        _negative_row(
            "annotation_executable_injection",
            lambda: merge_blueprint_annotations(
                blueprint,
                {"display_name": "safe", "description": "safe", "metrics": {}},
                expected_blueprint_sha256=blueprint_pin,
                expected_domain_id=domain_id,
                expected_environment=environment,
                source_manifest=source_manifest,
            ),
            expected_reason="annotation_key_not_allowed",
        ),
    ]
    return cases


def _component_guard_negatives(
    *,
    blueprint: dict[str, Any],
    blueprint_pin: str,
    domain_id: str,
    environment: str,
    source_text: str,
    revision: int,
) -> list[dict[str, Any]]:
    component_cls, _namespace = _component_contract()
    simple_tamper = deepcopy(blueprint)
    simple_tamper["executable"]["output_profile"]["default_row_limit"] = (
        int(simple_tamper["executable"]["output_profile"].get("default_row_limit") or 20)
        + 1
    )
    recomputed_tamper = deepcopy(simple_tamper)
    recomputed_tamper["executable_sha256"] = sha256_json(recomputed_tamper["executable"])
    recomputed_tamper["blueprint_sha256"] = compute_blueprint_sha256(recomputed_tamper)
    wrong_pin = "0" * 64 if blueprint_pin != "0" * 64 else "1" * 64
    specs = (
        ("missing_blueprint", "", blueprint_pin),
        (
            "missing_external_pin",
            json.dumps(blueprint, ensure_ascii=False, separators=(",", ":")),
            "",
        ),
        (
            "wrong_external_pin",
            json.dumps(blueprint, ensure_ascii=False, separators=(",", ":")),
            wrong_pin,
        ),
        (
            "simple_executable_tamper",
            json.dumps(simple_tamper, ensure_ascii=False, separators=(",", ":")),
            blueprint_pin,
        ),
        (
            "recomputed_executable_tamper",
            json.dumps(recomputed_tamper, ensure_ascii=False, separators=(",", ":")),
            blueprint_pin,
        ),
    )
    rows: list[dict[str, Any]] = []
    for case_id, blueprint_json, pin in specs:
        guard = GuardModel()
        component = _component_instance(
            component_cls,
            source_text=source_text,
            model=guard,
            blueprint_json=blueprint_json,
            blueprint_pin=pin,
            domain_id=domain_id,
            environment=environment,
            revision=revision,
        )
        response = _response_data(component.run_authoring())
        checks = {
            "status_error": response.get("status") == "error",
            "model_calls_zero": guard.calls == 0,
            "repair_calls_zero": int((response.get("llm_usage") or {}).get("repair_llm_calls") or 0)
            == 0,
        }
        rows.append(
            {
                "case_id": case_id,
                "error_code": str(((response.get("error") or {}).get("code") or ""))[:96],
                "error_stage": str(((response.get("error") or {}).get("stage") or ""))[:96],
                "error_reason": _error_reason_from_response(response),
                "model_calls": guard.calls,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )
    return rows


def validate_blueprint_source(
    source_path: Path,
    *,
    blueprint_path: Path,
    blueprint_pin_path: Path,
    api_key: str,
    model: str,
    timeout_seconds: int,
    domain_id: str,
    environment: str,
    revision: int,
) -> dict[str, Any]:
    normalized_model = str(model).removeprefix("models/")
    if normalized_model != DEFAULT_GEMINI_MODEL:
        raise RuntimeError("exact_gemini_model_required")
    # Match the standalone Flow's canonical natural-TXT boundary exactly.
    source_text = source_path.read_text(encoding="utf-8-sig").strip()
    if not source_text:
        raise RuntimeError("metadata_source_empty")
    source_bytes = source_text.encode("utf-8")
    source_manifest = extract_authoring_source_manifest(source_text)
    blueprint, blueprint_pin, trust = _load_trusted_blueprint(
        blueprint_path=blueprint_path,
        pin_path=blueprint_pin_path,
        source_manifest=source_manifest,
        domain_id=domain_id,
        environment=environment,
    )
    before_executable = canonical_bytes(blueprint["executable"])
    direct_negatives = _direct_negative_cases(
        blueprint=blueprint,
        blueprint_pin=blueprint_pin,
        domain_id=domain_id,
        environment=environment,
        source_manifest=source_manifest,
        source_text=source_text,
    )
    component_negatives = _component_guard_negatives(
        blueprint=blueprint,
        blueprint_pin=blueprint_pin,
        domain_id=domain_id,
        environment=environment,
        source_text=source_text,
        revision=revision,
    )
    provider = GeminiJsonModel(
        api_key=api_key,
        model=normalized_model,
        timeout_seconds=timeout_seconds,
        max_output_tokens=1024,
    )
    row: dict[str, Any] = {
        "domain_id": domain_id,
        "environment": environment,
        "revision": revision,
        "source_file": (
            source_path.relative_to(ROOT).as_posix()
            if source_path.is_relative_to(ROOT)
            else source_path.name
        ),
        "source_bytes": len(source_bytes),
        "source_sha256": sha256(source_bytes).hexdigest(),
        "source_manifest_sha256": str(source_manifest.get("manifest_sha256") or ""),
        "trust": trust,
        "expected_external_provider_calls": 1,
        "expected_repair_calls": 0,
        "direct_fail_closed_negatives": direct_negatives,
        "standalone_fail_closed_negatives": component_negatives,
    }
    try:
        prompt = _annotation_prompt(source_text, deepcopy(blueprint["default_annotations"]))
        raw_response = provider.invoke(prompt)
        proposal = validate_contract(
            _json_object_text(raw_response),
            "metadata-annotation-proposal.schema.json",
            stage="metadata_annotation_validation",
            error_code="metadata_schema_error",
        )
        annotations = {key: deepcopy(proposal[key]) for key in ANNOTATION_KEYS}
        draft = merge_blueprint_annotations(
            blueprint,
            annotations,
            expected_blueprint_sha256=blueprint_pin,
            expected_domain_id=domain_id,
            expected_environment=environment,
            source_manifest=source_manifest,
        )
        after_projection = {key: deepcopy(draft[key]) for key in EXECUTABLE_KEYS}
        after_executable = canonical_bytes(after_projection)
        package = validate_domain_package(
            compile_domain_package(
                draft,
                domain_id,
                environment,
                revision=revision,
                lifecycle_status="validated",
            )
        )
        catalog = validate_runtime_catalog_v2(package["runtime_catalog"])
        bundle_document = make_bundle_document(package)
        active_pointer = make_active_pointer_document(package)
        replay_response, replay_calls = _component_replay(
            raw_response=raw_response,
            source_text=source_text,
            blueprint=blueprint,
            blueprint_pin=blueprint_pin,
            domain_id=domain_id,
            environment=environment,
            revision=revision,
        )
        replay_usage = (
            replay_response.get("llm_usage")
            if isinstance(replay_response.get("llm_usage"), dict)
            else {}
        )
        replay_authoring_calls = int(
            replay_usage.get(
                "annotation_llm_calls",
                replay_usage.get("draft_llm_calls", 0),
            )
            or 0
        )
        provider_evidence = provider.evidence()
        checks = {
            "exact_model": provider.model == DEFAULT_GEMINI_MODEL,
            "provider_model_versions_exact": provider_evidence.get(
                "provider_model_versions_exact", True
            )
            is True,
            "external_provider_call_exact": provider.calls == 1,
            "proposal_contract_exact": set(proposal) == set(ANNOTATION_KEYS),
            "annotation_allowlist_exact": set(annotations) == set(ANNOTATION_KEYS),
            "blueprint_validated_with_external_pin": bool(blueprint_pin)
            and blueprint_pin == blueprint.get("blueprint_sha256"),
            "executable_canonical_bytes_unchanged": before_executable == after_executable,
            "executable_hash_unchanged": sha256_json(after_projection)
            == blueprint.get("executable_sha256"),
            "domain_package_valid": package.get("contract_version") == "domain.package.v1",
            "runtime_catalog_v2": catalog.get("contract_version")
            == "metadata.runtime.catalog.v2",
            "identity_pinned": package.get("domain_id") == domain_id
            and package.get("environment") == environment
            and int(package.get("revision") or 0) == revision,
            "bundle_hash_pinned": bundle_document.get("bundle_sha256")
            == package.get("bundle_sha256"),
            "active_pointer_pinned": active_pointer.get("bundle_sha256")
            == package.get("bundle_sha256")
            and active_pointer.get("package_sha256") == package.get("package_sha256"),
            "standalone_prepare_replayed": replay_response.get("status") == "ok"
            and replay_response.get("stage") == "prepared"
            and replay_calls == 1,
            "standalone_package_parity": replay_response.get("package_sha256")
            == package.get("package_sha256")
            and replay_response.get("bundle_sha256") == package.get("bundle_sha256")
            and replay_response.get("catalog_sha256") == catalog.get("catalog_sha256"),
            "standalone_annotation_call_exact": replay_authoring_calls == 1,
            "repair_llm_zero": int(replay_usage.get("repair_llm_calls") or 0) == 0,
            "direct_negatives_passed": all(item["passed"] for item in direct_negatives),
            "standalone_negatives_passed": all(
                item["passed"] for item in component_negatives
            ),
        }
        row.update(
            {
                "passed": all(checks.values()),
                "prompt_sha256": sha256(prompt.encode("utf-8")).hexdigest(),
                "proposal_contract": "metadata-annotation-proposal.schema.json",
                "proposal_keys": sorted(proposal),
                "annotation_values_persisted": False,
                "executable_bytes_before_sha256": sha256(before_executable).hexdigest(),
                "executable_bytes_after_sha256": sha256(after_executable).hexdigest(),
                "package_sha256": package.get("package_sha256"),
                "bundle_sha256": package.get("bundle_sha256"),
                "catalog_sha256": catalog.get("catalog_sha256"),
                "counts": {
                    key: len(catalog.get(key) or {})
                    for key in (
                        "datasets",
                        "fields",
                        "metrics",
                        "relations",
                        "recipes",
                        "aliases",
                    )
                },
                "standalone_replay": {
                    "status": replay_response.get("status"),
                    "stage": replay_response.get("stage"),
                    "replay_calls": replay_calls,
                    "llm_usage": replay_usage,
                    "package_sha256": replay_response.get("package_sha256"),
                    "bundle_sha256": replay_response.get("bundle_sha256"),
                    "catalog_sha256": replay_response.get("catalog_sha256"),
                },
                "provider": provider_evidence,
                "checks": checks,
            }
        )
    except Exception as exc:
        row.update(
            {
                "passed": False,
                "failure": _safe_reason(exc),
                "provider": provider.evidence(),
            }
        )
    assert_secret_absent(row, api_key)
    return row


def run(
    source_path: Path,
    *,
    blueprint_path: Path,
    blueprint_pin_path: Path,
    env_path: Path,
    model: str,
    timeout_seconds: int,
    domain_id: str,
    environment: str,
    revision: int,
) -> dict[str, Any]:
    model = require_exact_gemini_model(model)
    api_key = resolve_gemini_api_key(env_path)
    row = validate_blueprint_source(
        source_path.resolve(),
        blueprint_path=blueprint_path.resolve(),
        blueprint_pin_path=blueprint_pin_path.resolve(),
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
        domain_id=domain_id,
        environment=environment,
        revision=revision,
    )
    report = {
        "contract_version": "live.blueprint-authoring.validation.v1",
        "model": model,
        "model_contract": gemini_model_contract_evidence(model),
        "execution_mode": "trusted_blueprint_annotation_only",
        "full_draft_generation_used": False,
        "provider_payloads_persisted": False,
        "prompts_persisted": False,
        "source_text_persisted": False,
        "blueprint_json_persisted": False,
        "annotation_values_persisted": False,
        "case_count": 1,
        "passed": 1 if row.get("passed") is True else 0,
        "failed": 0 if row.get("passed") is True else 1,
        "external_provider_calls": int((row.get("provider") or {}).get("calls") or 0),
        "repair_llm_calls": 0,
        "rows": [row],
    }
    assert_secret_absent(report, api_key)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--blueprint", type=Path, default=DEFAULT_BLUEPRINT)
    parser.add_argument("--blueprint-pin", type=Path, default=DEFAULT_BLUEPRINT_PIN)
    parser.add_argument("--domain-id", default="order_sales")
    parser.add_argument("--environment", default="blueprint_validation")
    parser.add_argument("--revision", type=int, default=1)
    parser.add_argument("--model", default=DEFAULT_GEMINI_MODEL)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs" / "live_blueprint_authoring.json",
    )
    args = parser.parse_args()
    try:
        report = run(
            args.source,
            blueprint_path=args.blueprint,
            blueprint_pin_path=args.blueprint_pin,
            env_path=args.env_file.resolve(),
            model=args.model,
            timeout_seconds=max(1, min(args.timeout_seconds, 300)),
            domain_id=args.domain_id,
            environment=args.environment,
            revision=max(1, args.revision),
        )
    except Exception as exc:
        report = {
            "contract_version": "live.blueprint-authoring.validation.v1",
            "model": str(args.model).removeprefix("models/"),
            "execution_mode": "trusted_blueprint_annotation_only",
            "full_draft_generation_used": False,
            "all_passed": False,
            "failure": _safe_reason(exc),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "model": report.get("model"),
                "passed": report.get("passed", 0),
                "failed": report.get("failed", 1),
                "external_provider_calls": report.get("external_provider_calls", 0),
            },
            ensure_ascii=False,
        )
    )
    print(f"report: {args.output}")
    return 0 if int(report.get("failed", 1)) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
