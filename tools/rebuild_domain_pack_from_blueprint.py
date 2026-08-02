"""Recompile a reviewed domain pack after explicit, audited field overrides."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.authoring_blueprint import validate_executable_blueprint
from reference_runtime.canonical import canonical_bytes, sha256_json
from reference_runtime.domain_packages import (
    compile_domain_package,
    make_active_pointer_document,
    make_bundle_document,
)


DEFAULT_DOMAIN_ROOT = ROOT / "metadata" / "domain_packs" / "manufacturing"
DEFAULT_BLUEPRINT = DEFAULT_DOMAIN_ROOT / "trusted_executable_blueprint.json"
DEFAULT_PIN = DEFAULT_DOMAIN_ROOT / "trusted_executable_blueprint.sha256"
DEFAULT_MANIFEST = DEFAULT_DOMAIN_ROOT / "trusted_source_manifest.json"
DEFAULT_OVERRIDES = DEFAULT_DOMAIN_ROOT / "field_binding_overrides.json"
DEFAULT_OUTPUT_DIR = DEFAULT_DOMAIN_ROOT / "compiled"

OVERRIDE_VERSION = "metadata.authoring.field-binding-overrides.v2"
ALLOWED_BINDING_KEYS = {"physical_column", "physical_aliases"}
BINDING_REPLACEMENT = "replace_binding"
DESCRIPTOR_REMOVAL = "remove_descriptor"
ALLOWED_REASON_CODES = {
    BINDING_REPLACEMENT: {"natural_source_binding_correction"},
    DESCRIPTOR_REMOVAL: {"source_projection_not_registered"},
}


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} must be a readable UTF-8 JSON object") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value


def _apply_overrides(
    draft: dict[str, Any], overrides: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    if set(overrides) != {
        "contract_version", "domain_id", "environment", "datasets",
    } or overrides.get("contract_version") != OVERRIDE_VERSION:
        raise ValueError("field binding override root contract is invalid")
    raw_datasets = overrides.get("datasets")
    draft_datasets = draft.get("datasets")
    if not isinstance(raw_datasets, dict) or not raw_datasets:
        raise ValueError("field binding overrides require at least one dataset")
    if not isinstance(draft_datasets, dict):
        raise ValueError("authoring draft datasets are invalid")

    applied: list[dict[str, str]] = []
    already_current: list[dict[str, str]] = []
    for dataset_id in sorted(raw_datasets):
        raw_fields = raw_datasets[dataset_id]
        dataset = draft_datasets.get(dataset_id)
        if not isinstance(raw_fields, dict) or not raw_fields or not isinstance(dataset, dict):
            raise ValueError("field binding override dataset is invalid")
        fields = dataset.get("fields")
        if not isinstance(fields, dict):
            raise ValueError("field binding override dataset fields are invalid")
        for field_id in sorted(raw_fields):
            policy = raw_fields[field_id]
            field = fields.get(field_id)
            if not isinstance(policy, dict):
                raise ValueError("field binding override target is invalid")
            if set(policy) != {
                "operation", "reason_code", "expected", "replacement",
            }:
                raise ValueError("field binding override policy is not closed")
            operation = policy.get("operation")
            reason_code = policy.get("reason_code")
            if (
                operation not in ALLOWED_REASON_CODES
                or reason_code not in ALLOWED_REASON_CODES[operation]
            ):
                raise ValueError("field binding override reason is unsupported")
            expected = policy.get("expected")
            replacement = policy.get("replacement")
            identity = {
                "dataset_id": dataset_id,
                "field_id": field_id,
                "operation": operation,
                "reason_code": reason_code,
                "expected_sha256": sha256_json(expected),
                "replacement_sha256": sha256_json(replacement),
            }
            if operation == DESCRIPTOR_REMOVAL:
                if not isinstance(expected, dict) or not expected or replacement is not None:
                    raise ValueError("field descriptor removal values are invalid")
                if field is None:
                    already_current.append(identity)
                    continue
                if not isinstance(field, dict):
                    raise ValueError("field descriptor removal target is invalid")
                if field != expected:
                    raise ValueError("field descriptor removal expected value mismatch")
                del fields[field_id]
                applied.append(identity)
                continue

            if not isinstance(field, dict):
                raise ValueError("field binding override target is invalid")
            if (
                not isinstance(expected, dict)
                or not isinstance(replacement, dict)
                or set(expected) != ALLOWED_BINDING_KEYS
                or set(replacement) != ALLOWED_BINDING_KEYS
                or not isinstance(replacement.get("physical_column"), str)
                or not replacement["physical_column"].strip()
                or not isinstance(replacement.get("physical_aliases"), list)
                or any(
                    not isinstance(value, str) or not value.strip()
                    for value in replacement["physical_aliases"]
                )
                or len(replacement["physical_aliases"])
                != len(set(replacement["physical_aliases"]))
            ):
                raise ValueError("field binding override values are invalid")
            current = {key: deepcopy(field.get(key)) for key in ALLOWED_BINDING_KEYS}
            if current == replacement:
                already_current.append(identity)
                continue
            if current != expected:
                raise ValueError("field binding override expected value mismatch")
            for key in sorted(ALLOWED_BINDING_KEYS):
                field[key] = deepcopy(replacement[key])
            applied.append(identity)
    evidence = {
        "contract_version": "metadata.authoring.field-binding-override-evidence.v2",
        "applied_count": len(applied),
        "already_current_count": len(already_current),
        "applied_operations": applied,
        "already_current_operations": already_current,
        "applied_sha256": sha256_json(applied),
        "already_current_sha256": sha256_json(already_current),
        "override_sha256": sha256_json(overrides),
    }
    return draft, evidence


def rebuild(
    *,
    blueprint_path: Path,
    pin_path: Path,
    manifest_path: Path,
    overrides_path: Path,
    output_dir: Path,
    revision: int,
    lifecycle_status: str,
) -> dict[str, Any]:
    blueprint = _load_object(blueprint_path, "trusted executable blueprint")
    source_manifest = _load_object(manifest_path, "trusted source manifest")
    external_pin = pin_path.read_text(encoding="utf-8").strip()
    validated = validate_executable_blueprint(
        blueprint,
        expected_blueprint_sha256=external_pin,
        expected_domain_id=str(blueprint.get("domain_id") or ""),
        expected_environment=str(blueprint.get("environment") or ""),
        source_manifest=source_manifest,
    )
    overrides = _load_object(overrides_path, "field binding overrides")
    if (
        overrides.get("domain_id") != validated["domain_id"]
        or overrides.get("environment") != validated["environment"]
    ):
        raise ValueError("field binding override identity mismatch")
    draft = {
        **deepcopy(validated["executable"]),
        **deepcopy(validated["default_annotations"]),
    }
    corrected, evidence = _apply_overrides(draft, overrides)
    package = compile_domain_package(
        corrected,
        validated["domain_id"],
        validated["environment"],
        revision=revision,
        lifecycle_status=lifecycle_status,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "domain_package": output_dir / "domain_package.json",
        "runtime_catalog": output_dir / "runtime_catalog.v2.json",
        "bundle_document": output_dir / "bundle_document.json",
        "active_pointer": output_dir / "active_pointer.json",
    }
    payloads = {
        "domain_package": package,
        "runtime_catalog": package["runtime_catalog"],
        "bundle_document": make_bundle_document(package),
        "active_pointer": make_active_pointer_document(package),
    }
    for key, path in outputs.items():
        path.write_bytes(canonical_bytes(payloads[key]) + b"\n")
    report = {
        "contract_version": "metadata.reviewed-domain-recompile.report.v1",
        "domain_id": package["domain_id"],
        "environment": package["environment"],
        "revision": package["revision"],
        "package_sha256": package["package_sha256"],
        "bundle_sha256": package["bundle_sha256"],
        "catalog_sha256": package["runtime_catalog"]["catalog_sha256"],
        "override_evidence": evidence,
        "outputs": {key: str(path.resolve()) for key, path in outputs.items()},
    }
    (output_dir / "reviewed_recompile_report.json").write_bytes(
        canonical_bytes(report) + b"\n"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blueprint", type=Path, default=DEFAULT_BLUEPRINT)
    parser.add_argument("--pin", type=Path, default=DEFAULT_PIN)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--revision", type=int, default=1)
    parser.add_argument("--lifecycle-status", default="validated")
    args = parser.parse_args()
    report = rebuild(
        blueprint_path=args.blueprint,
        pin_path=args.pin,
        manifest_path=args.manifest,
        overrides_path=args.overrides,
        output_dir=args.output_dir,
        revision=args.revision,
        lifecycle_status=args.lifecycle_status,
    )
    print(json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
