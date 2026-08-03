from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from flow_builder_support import (
    DEFAULT_ASSET_MANIFEST,
    DEFAULT_INVENTORY,
    PROJECT_ROOT,
    BuildContractError,
    build_flow,
    contract_hash_inventory,
    flow_export_filename,
    load_component_index,
    load_inventory,
    sha256_file,
    validate_runtime_assets,
    write_json_atomic,
)


DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "flow_exports"


def build_all_flows(
    *,
    inventory_path: Path = DEFAULT_INVENTORY,
    asset_manifest_path: Path = DEFAULT_ASSET_MANIFEST,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    assets = validate_runtime_assets(asset_manifest_path, strict_versions=True)
    inventory, namespace, flow_specs = load_inventory(inventory_path)
    component_index = load_component_index(assets)
    output_dir.mkdir(parents=True, exist_ok=True)

    flow_records: list[dict[str, Any]] = []
    expected_paths: set[Path] = set()
    for flow_spec in flow_specs:
        flow, record = build_flow(flow_spec, namespace, component_index, assets)
        destination = output_dir / flow_export_filename(record["logical_key"])
        write_json_atomic(destination, flow)
        expected_paths.add(destination.resolve())
        record["file"] = destination.name
        record["sha256"] = sha256_file(destination)
        flow_records.append(record)

    unexpected = sorted(
        path.name
        for path in output_dir.glob("metadata_v6_*_flow_v6_standalone.json")
        if path.resolve() not in expected_paths
    )
    if unexpected:
        raise BuildContractError(
            "unexpected generated v6 Flow exports exist; remove or reconcile them explicitly: "
            + ", ".join(unexpected)
        )

    manifest = {
        "contract_version": "flow.build.manifest.v1",
        "flow_count": len(flow_records),
        "uuid_namespace": str(namespace),
        "inventory": {
            "path": inventory_path.resolve().relative_to(PROJECT_ROOT).as_posix(),
            "sha256": sha256_file(inventory_path),
            "contract_version": inventory["contract_version"],
        },
        "runtime_assets": assets.manifest_projection(),
        "contracts": contract_hash_inventory(),
        "flows": flow_records,
    }
    write_json_atomic(output_dir / "manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build exactly four manifest-driven metadata_driven_v6 Langflow 1.9.2 source exports."
    )
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--asset-manifest", type=Path, default=DEFAULT_ASSET_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    try:
        result = build_all_flows(
            inventory_path=args.inventory.resolve(),
            asset_manifest_path=args.asset_manifest.resolve(),
            output_dir=args.output_dir.resolve(),
        )
    except BuildContractError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(
        json.dumps(
            {
                "status": "ok",
                "output_dir": str(args.output_dir.resolve()),
                "flow_count": result["flow_count"],
                "flows": [
                    {
                        "logical_key": item["logical_key"],
                        "id": item["id"],
                        "nodes": item["nodes"],
                        "edges": item["edges"],
                        "sha256": item["sha256"],
                    }
                    for item in result["flows"]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
