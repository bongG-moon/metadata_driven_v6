"""Compile the reviewed natural-language v6 baseline into one runtime catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import canonical_bytes, sha256_json
from reference_runtime.metadata_compiler import (
    COMPILER_VERSION,
    build_runtime_catalog,
    compiled_records,
    load_runtime_catalog,
    source_provenance,
    write_runtime_catalog,
)
from reference_runtime.domain_packages import (
    adapt_legacy_catalog_v1,
    compile_domain_package,
    make_active_pointer_document,
    make_bundle_document,
)


def _report_path(path: Path) -> str:
    """Return a stable path without assuming callers write below the repo root."""

    resolved = path.resolve()
    if resolved.is_relative_to(ROOT):
        return resolved.relative_to(ROOT).as_posix()
    return resolved.as_posix()


def compile_baseline(
    *,
    authoring_root: Path = ROOT / "metadata" / "authoring",
    output_dir: Path = ROOT / "metadata" / "fixtures" / "compiled",
) -> dict[str, Any]:
    provenance = source_provenance(authoring_root)
    catalog = build_runtime_catalog(authoring_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = write_runtime_catalog(output_dir / "runtime_catalog.json", catalog)
    records = compiled_records(catalog, provenance, lifecycle_status="active")
    records_path = output_dir / "metadata_records.jsonl"
    records_path.write_bytes(b"".join(canonical_bytes(record) + b"\n" for record in records))
    round_trip = load_runtime_catalog(catalog_path)
    manufacturing_package = adapt_legacy_catalog_v1(
        catalog,
        domain_id="manufacturing",
        environment="production",
        revision=1,
        output_profile={
            "planner_profile": "legacy_v1_compat",
            "legacy_catalog_sha256": catalog["catalog_sha256"],
        },
    )
    manufacturing_dir = ROOT / "metadata" / "domain_packs" / "manufacturing" / "compiled"
    manufacturing_dir.mkdir(parents=True, exist_ok=True)
    manufacturing_package_path = manufacturing_dir / "domain_package.json"
    manufacturing_package_path.write_bytes(canonical_bytes(manufacturing_package) + b"\n")
    (manufacturing_dir / "runtime_catalog.v2.json").write_bytes(
        canonical_bytes(manufacturing_package["runtime_catalog"]) + b"\n"
    )
    (manufacturing_dir / "bundle_document.json").write_bytes(
        canonical_bytes(make_bundle_document(manufacturing_package)) + b"\n"
    )
    (manufacturing_dir / "active_pointer.json").write_bytes(
        canonical_bytes(make_active_pointer_document(manufacturing_package)) + b"\n"
    )
    report = {
        "contract_version": "metadata.compile.report.v1",
        "compiler_version": COMPILER_VERSION,
        "authoring_sources": provenance,
        "catalog_path": _report_path(catalog_path),
        "catalog_sha256": catalog["catalog_sha256"],
        "catalog_file_sha256": sha256_json(json.loads(catalog_path.read_text(encoding="utf-8"))),
        "record_path": _report_path(records_path),
        "record_count": len(records),
        "counts": {
            "datasets": len(catalog["datasets"]),
            "fields": len(catalog["fields"]),
            "metrics": len(catalog["metrics"]),
            "process_groups": len(catalog["process_groups"]),
            "process_order": len(catalog["process_order"]),
            "product_groups": len(catalog["product_groups"]),
            "recipes": len(catalog["recipes"]),
            "aliases": len(catalog["aliases"]),
        },
        "round_trip_ok": round_trip["catalog_sha256"] == catalog["catalog_sha256"],
        "domain_package": {
            "domain_id": manufacturing_package["domain_id"],
            "environment": manufacturing_package["environment"],
            "revision": manufacturing_package["revision"],
            "bundle_sha256": manufacturing_package["bundle_sha256"],
            "package_path": _report_path(manufacturing_package_path),
        },
        "v5_write_operations": 0,
    }
    report_path = output_dir / "compile_report.json"
    report_path.write_bytes(canonical_bytes(report) + b"\n")
    return report


def compile_authoring_draft(
    draft_path: Path,
    *,
    domain_id: str,
    environment: str,
    revision: int,
    lifecycle_status: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Compile an Authoring LLM JSON draft without invoking any model."""

    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    package = compile_domain_package(
        draft,
        domain_id,
        environment,
        revision=revision,
        lifecycle_status=lifecycle_status,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "domain_package": output_dir / "domain_package.json",
        "runtime_catalog": output_dir / "runtime_catalog.v2.json",
        "bundle_document": output_dir / "bundle_document.json",
        "active_pointer": output_dir / "active_pointer.json",
    }
    paths["domain_package"].write_bytes(canonical_bytes(package) + b"\n")
    paths["runtime_catalog"].write_bytes(canonical_bytes(package["runtime_catalog"]) + b"\n")
    paths["bundle_document"].write_bytes(canonical_bytes(make_bundle_document(package)) + b"\n")
    paths["active_pointer"].write_bytes(canonical_bytes(make_active_pointer_document(package)) + b"\n")
    report = {
        "contract_version": "metadata.domain-compile.report.v1",
        "compiler_version": package["compiler_version"],
        "domain_id": package["domain_id"],
        "environment": package["environment"],
        "revision": package["revision"],
        "authoring_sha256": package["authoring_sha256"],
        "catalog_sha256": package["runtime_catalog"]["catalog_sha256"],
        "package_sha256": package["package_sha256"],
        "bundle_sha256": package["bundle_sha256"],
        "paths": {key: _report_path(value) for key, value in paths.items()},
        "v5_write_operations": 0,
    }
    (output_dir / "compile_report.json").write_bytes(canonical_bytes(report) + b"\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authoring-root", type=Path, default=ROOT / "metadata" / "authoring")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "metadata" / "fixtures" / "compiled")
    parser.add_argument("--draft-json", type=Path)
    parser.add_argument("--domain-id", default="")
    parser.add_argument("--environment", default="default")
    parser.add_argument("--revision", type=int, default=1)
    parser.add_argument("--lifecycle-status", choices=["draft", "validated", "active"], default="validated")
    args = parser.parse_args()
    if args.draft_json:
        if not args.domain_id:
            parser.error("--domain-id is required with --draft-json")
        report = compile_authoring_draft(
            args.draft_json.resolve(),
            domain_id=args.domain_id,
            environment=args.environment,
            revision=args.revision,
            lifecycle_status=args.lifecycle_status,
            output_dir=args.output_dir.resolve(),
        )
    else:
        report = compile_baseline(authoring_root=args.authoring_root.resolve(), output_dir=args.output_dir.resolve())
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
