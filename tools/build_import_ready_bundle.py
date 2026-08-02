from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from flow_builder_support import (
    DEFAULT_ASSET_MANIFEST,
    DEFAULT_INVENTORY,
    EXPECTED_FLOW_KEYS,
    PROJECT_ROOT,
    BuildContractError,
    deterministic_zip,
    flow_export_filename,
    indexed_import_filename,
    load_inventory,
    load_json,
    sha256_file,
    validate_flow_identity_and_versions,
    validate_runtime_assets,
    write_json_atomic,
)


DEFAULT_SOURCE_DIR = PROJECT_ROOT / "flow_exports"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "import_ready_flows"
DEFAULT_ZIP = PROJECT_ROOT / "import_ready_flows.zip"
COMBINED_FILENAME = "00_metadata_driven_v6_complete_ALL_FLOWS.json"


def _load_source_manifest(source_dir: Path) -> dict[str, Any]:
    manifest_path = source_dir / "manifest.json"
    manifest = load_json(manifest_path, "v6 source Flow build manifest")
    if manifest.get("contract_version") != "flow.build.manifest.v1":
        raise BuildContractError("flow_exports/manifest.json must use flow.build.manifest.v1")
    if manifest.get("flow_count") != len(EXPECTED_FLOW_KEYS):
        raise BuildContractError("source Flow build manifest must contain exactly five flows")
    return manifest


def build_bundle(
    *,
    inventory_path: Path = DEFAULT_INVENTORY,
    asset_manifest_path: Path = DEFAULT_ASSET_MANIFEST,
    source_dir: Path = DEFAULT_SOURCE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    zip_path: Path = DEFAULT_ZIP,
) -> dict[str, Any]:
    assets = validate_runtime_assets(asset_manifest_path, strict_versions=True)
    _, namespace, flow_specs = load_inventory(inventory_path)
    source_manifest = _load_source_manifest(source_dir)
    source_records = {
        str(item.get("logical_key")): item
        for item in source_manifest.get("flows", [])
        if isinstance(item, dict)
    }
    if set(source_records) != set(EXPECTED_FLOW_KEYS):
        raise BuildContractError(
            f"source Flow manifest inventory mismatch: {sorted(source_records)!r}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    expected_individual_paths: set[Path] = set()
    flows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for index, flow_spec in enumerate(flow_specs, start=1):
        logical_key = str(flow_spec["logical_key"])
        source = source_dir / flow_export_filename(logical_key)
        flow = load_json(source, f"source Flow {logical_key}")
        errors = validate_flow_identity_and_versions(flow, namespace, logical_key)
        if errors:
            raise BuildContractError(f"{logical_key}: " + "; ".join(errors))
        source_hash = sha256_file(source)
        declared_hash = str(source_records[logical_key].get("sha256") or "")
        if source_hash != declared_hash:
            raise BuildContractError(
                f"{logical_key}: source Flow hash {source_hash} != build manifest {declared_hash}"
            )
        destination = output_dir / indexed_import_filename(index, logical_key)
        write_json_atomic(destination, flow)
        expected_individual_paths.add(destination.resolve())
        flows.append(flow)
        records.append(
            {
                "order": index,
                "logical_key": logical_key,
                "endpoint_name": logical_key,
                "display_name": str(flow_spec["display_name"]),
                "id": str(flow["id"]),
                "file": destination.name,
                "nodes": len(flow.get("data", {}).get("nodes", [])),
                "edges": len(flow.get("data", {}).get("edges", [])),
                "source_sha256": source_hash,
                "sha256": sha256_file(destination),
            }
        )

    unexpected = sorted(
        path.name
        for path in output_dir.glob("[0-9][0-9]_metadata_v6_*_flow_v6_standalone.json")
        if path.resolve() not in expected_individual_paths
    )
    if unexpected:
        raise BuildContractError(
            "unexpected v6 individual import files exist; remove or reconcile them explicitly: "
            + ", ".join(unexpected)
        )

    combined_path = output_dir / COMBINED_FILENAME
    write_json_atomic(combined_path, {"flows": flows}, compact=True)
    bundle_manifest = {
        "contract_version": "flow.bundle.manifest.v1",
        "bundle": "metadata_driven_v6_complete",
        "flow_count": len(records),
        "uuid_namespace": str(namespace),
        "langflow_version": "1.9.2",
        "langflow_base_version": "0.9.2",
        "lfx_version": "0.4.2",
        "runtime_assets": assets.manifest_projection(),
        "inventory": {
            "path": inventory_path.resolve().relative_to(PROJECT_ROOT).as_posix(),
            "sha256": sha256_file(inventory_path),
        },
        "source_build_manifest": {
            "path": (source_dir / "manifest.json").resolve().relative_to(PROJECT_ROOT).as_posix(),
            "sha256": sha256_file(source_dir / "manifest.json"),
        },
        "single_file_ui_import": combined_path.name,
        "single_file_ui_import_sha256": sha256_file(combined_path),
        "flows": records,
    }
    manifest_path = output_dir / "manifest.json"
    write_json_atomic(manifest_path, bundle_manifest)
    readme_path = output_dir / "README_IMPORT.md"
    readme = (
        "# metadata_driven_v6 Langflow 1.9.2 import bundle\n\n"
        "이 폴더는 `flow.inventory.v1`에서 생성된 정확히 다섯 개의 standalone Flow를 포함합니다.\n"
        "`00_metadata_driven_v6_complete_ALL_FLOWS.json`을 한 번에 import하거나 번호 순서대로 개별 JSON을 import합니다.\n\n"
        "- Python 3.12\n"
        "- langflow 1.9.2\n"
        "- langflow-base 0.9.2\n"
        "- lfx 0.4.2\n\n"
        "Flow JSON에는 credential 값이나 domain-specific blueprint가 없습니다. import 후 운영자가 필요한 Langflow node input 또는 Global Variable을 연결합니다.\n\n"
        "기본 Domain Authoring은 작업자가 자유롭게 작성한 Domain/Dataset/Main Filter 자연어 bundle 또는 완전한 도메인 설명을 외부 공통 Prompt로 "
        "변환하고, LLM 최대 1회의 closed full draft를 결정론적 compiler가 검증합니다. 작업자에게 JSON, inventory 선언 문법, Blueprint나 pin을 요구하지 마십시오.\n"
        "`source_grounding_mode=explicit_inventory`를 명시한 optional 고신뢰 lane에서만 승인된 registry의 blueprint JSON과 별도 SHA-256 pin을 "
        "Domain Authoring node의 `trusted_blueprint_json`, `trusted_blueprint_sha256` admin 입력에 설정합니다. 이 값은 ChatInput, Run Flow API payload 또는 "
        "일반 사용자 tweak에서 받지 마십시오. 공개 gateway는 mode와 admin input의 arbitrary tweak를 차단해야 합니다.\n"
        "검증용 order_sales Blueprint와 `.sha256` 파일은 이 optional lane의 예시입니다. "
        "Dataset Catalog/Main Filter Flow는 MongoDB의 exact active v6 Domain Package를 base로 section-bounded patch를 수행합니다.\n"
        "Domain Policy Authoring Flow는 Prompt/Language Model 노드 없이 운영자 입력만 검증하며 raw Python 대신 등록된 function descriptor만 허용합니다.\n"
    )
    readme_path.write_bytes(readme.encode("utf-8"))
    deterministic_zip(
        zip_path,
        [
            combined_path,
            manifest_path,
            readme_path,
            *[output_dir / record["file"] for record in records],
        ],
        root=output_dir,
    )
    result = dict(bundle_manifest)
    result["output_dir"] = str(output_dir)
    result["zip"] = {"path": str(zip_path), "sha256": sha256_file(zip_path)}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the deterministic five-Flow metadata_driven_v6 import-ready bundle and ZIP."
    )
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--asset-manifest", type=Path, default=DEFAULT_ASSET_MANIFEST)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--zip", type=Path, default=DEFAULT_ZIP)
    args = parser.parse_args()
    try:
        result = build_bundle(
            inventory_path=args.inventory.resolve(),
            asset_manifest_path=args.asset_manifest.resolve(),
            source_dir=args.source_dir.resolve(),
            output_dir=args.output_dir.resolve(),
            zip_path=args.zip.resolve(),
        )
    except BuildContractError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(
        json.dumps(
            {
                "status": "ok",
                "flow_count": result["flow_count"],
                "output_dir": result["output_dir"],
                "combined_sha256": result["single_file_ui_import_sha256"],
                "zip": result["zip"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
