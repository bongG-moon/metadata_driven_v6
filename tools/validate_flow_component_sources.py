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
    canonical_json_bytes,
    flow_export_filename,
    indexed_import_filename,
    load_inventory,
    load_json,
    resolve_project_path,
    sha256_bytes,
    sha256_file,
    validate_flow_identity_and_versions,
    validate_runtime_assets,
)


DEFAULT_SOURCE_DIR = PROJECT_ROOT / "flow_exports"
DEFAULT_IMPORT_DIR = PROJECT_ROOT / "import_ready_flows"
COMBINED_FILENAME = "00_metadata_driven_v6_complete_ALL_FLOWS.json"
EMBEDDED_ONLY_COMPONENT_SOURCES = {
    "langflow_components/metadata_authoring/00_metadata_authoring_engine.py",
    "langflow_components/metadata_authoring/authoring_prompt_context_builder.py",
    "langflow_components/metadata_authoring/authoring_reference_registry.py",
    "langflow_components/metadata_authoring/natural_metadata_source_bundle.py",
}


def _artifact_flows(
    source_dir: Path,
    import_dir: Path,
    flow_specs: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    source: dict[str, dict[str, Any]] = {}
    individual: dict[str, dict[str, Any]] = {}
    for index, spec in enumerate(flow_specs, start=1):
        logical_key = str(spec["logical_key"])
        source[logical_key] = load_json(
            source_dir / flow_export_filename(logical_key), f"source export {logical_key}"
        )
        individual[logical_key] = load_json(
            import_dir / indexed_import_filename(index, logical_key),
            f"individual import-ready Flow {logical_key}",
        )
    combined_payload = load_json(import_dir / COMBINED_FILENAME, "combined import-ready bundle")
    combined_values = combined_payload.get("flows") if isinstance(combined_payload, dict) else None
    if not isinstance(combined_values, list):
        raise BuildContractError("combined import-ready bundle must contain a flows array")
    combined = {
        str(flow.get("endpoint_name") or ""): flow
        for flow in combined_values
        if isinstance(flow, dict)
    }
    if set(combined) != set(EXPECTED_FLOW_KEYS) or len(combined_values) != len(EXPECTED_FLOW_KEYS):
        raise BuildContractError(
            f"combined import-ready bundle must contain exactly the four v6 flows; got {sorted(combined)!r}"
        )
    return {"source_exports": source, "individual_imports": individual, "combined_bundle": combined}


def audit_repository(
    *,
    inventory_path: Path = DEFAULT_INVENTORY,
    asset_manifest_path: Path = DEFAULT_ASSET_MANIFEST,
    source_dir: Path = DEFAULT_SOURCE_DIR,
    import_dir: Path = DEFAULT_IMPORT_DIR,
) -> dict[str, Any]:
    assets = validate_runtime_assets(asset_manifest_path, strict_versions=True)
    _, namespace, flow_specs = load_inventory(inventory_path)
    layers = _artifact_flows(source_dir, import_dir, flow_specs)
    errors: list[dict[str, Any]] = []
    expected_sources: set[str] = set()
    custom_instances = 0

    for spec in flow_specs:
        logical_key = str(spec["logical_key"])
        expected_custom: dict[str, tuple[str, str, str]] = {}
        expected_prompts: dict[str, tuple[str, str, str]] = {}
        for node_spec in spec["custom_nodes"]:
            node_id = str(node_spec["id"])
            path = resolve_project_path(
                str(node_spec["source"]), label=f"{logical_key}.{node_id} custom source"
            )
            relative = path.relative_to(PROJECT_ROOT).as_posix()
            expected_sources.add(relative)
            code = path.read_text(encoding="utf-8")
            expected_custom[node_id] = (relative, code, sha256_bytes(code.encode("utf-8")))
        for node_spec in spec["native_nodes"]:
            node_id = str(node_spec["id"])
            prompt_source = node_spec.get("settings", {}).get("prompt_source")
            if not prompt_source:
                continue
            path = resolve_project_path(
                str(prompt_source), label=f"{logical_key}.{node_id} prompt source"
            )
            relative = path.relative_to(PROJECT_ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            expected_prompts[node_id] = (relative, text, sha256_bytes(text.encode("utf-8")))

        baseline = layers["source_exports"][logical_key]
        for layer_name, layer in layers.items():
            flow = layer[logical_key]
            for message in validate_flow_identity_and_versions(flow, namespace, logical_key):
                errors.append({"layer": layer_name, "flow": logical_key, "type": "flow_contract", "message": message})
            if canonical_json_bytes(flow) != canonical_json_bytes(baseline):
                errors.append({"layer": layer_name, "flow": logical_key, "type": "artifact_flow_mismatch"})
            nodes = {str(node.get("id") or ""): node for node in flow.get("data", {}).get("nodes", [])}
            if set(expected_custom) - set(nodes):
                errors.append(
                    {
                        "layer": layer_name,
                        "flow": logical_key,
                        "type": "missing_custom_nodes",
                        "nodes": sorted(set(expected_custom) - set(nodes)),
                    }
                )
            for node_id, (relative, code, source_hash) in expected_custom.items():
                node = nodes.get(node_id)
                if node is None:
                    continue
                custom_instances += 1
                config = node.get("data", {}).get("node", {})
                embedded = config.get("template", {}).get("code", {}).get("value")
                metadata = config.get("metadata", {})
                if embedded != code:
                    errors.append({"layer": layer_name, "flow": logical_key, "node": node_id, "type": "embedded_source_mismatch"})
                if metadata.get("source_path") != relative:
                    errors.append(
                        {
                            "layer": layer_name,
                            "flow": logical_key,
                            "node": node_id,
                            "type": "source_path_mismatch",
                            "expected": relative,
                            "actual": metadata.get("source_path"),
                        }
                    )
                if metadata.get("source_sha256") != source_hash or metadata.get("code_hash") != source_hash[:12]:
                    errors.append({"layer": layer_name, "flow": logical_key, "node": node_id, "type": "source_hash_mismatch"})

            expected_native = {str(item["id"]): item for item in spec["native_nodes"]}
            for node_id, native_spec in expected_native.items():
                node = nodes.get(node_id)
                if node is None:
                    errors.append({"layer": layer_name, "flow": logical_key, "node": node_id, "type": "missing_native_node"})
                    continue
                config = node.get("data", {}).get("node", {})
                if str(native_spec.get("type")) in {"Language Model", "LanguageModel", "LanguageModelComponent"}:
                    embedded = config.get("template", {}).get("code", {}).get("value")
                    expected_code = assets.language_model_source.read_text(encoding="utf-8")
                    if embedded != expected_code or config.get("metadata", {}).get("asset_sha256") != assets.language_model_sha256:
                        errors.append({"layer": layer_name, "flow": logical_key, "node": node_id, "type": "language_model_asset_mismatch"})
                if node_id in expected_prompts:
                    relative, prompt_text, prompt_hash = expected_prompts[node_id]
                    metadata = config.get("metadata", {})
                    embedded_prompt = config.get("template", {}).get("template", {}).get("value")
                    if embedded_prompt != prompt_text:
                        errors.append({"layer": layer_name, "flow": logical_key, "node": node_id, "type": "prompt_source_mismatch"})
                    if (
                        metadata.get("prompt_source_path") != relative
                        or metadata.get("prompt_source_sha256") != prompt_hash
                    ):
                        errors.append({"layer": layer_name, "flow": logical_key, "node": node_id, "type": "prompt_source_hash_mismatch"})

    component_root = PROJECT_ROOT / "langflow_components"
    actual_sources = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in component_root.rglob("*.py")
        if path.name != "__init__.py" and "__pycache__" not in path.parts
    } if component_root.exists() else set()
    inactive = sorted(actual_sources - expected_sources - EMBEDDED_ONLY_COMPONENT_SOURCES)
    missing_embedded = sorted(EMBEDDED_ONLY_COMPONENT_SOURCES - actual_sources)
    missing = sorted(expected_sources - actual_sources)
    if inactive:
        errors.append({"type": "unreferenced_component_sources", "paths": inactive})
    if missing:
        errors.append({"type": "inventory_sources_outside_component_set", "paths": missing})
    if missing_embedded:
        errors.append({"type": "missing_embedded_only_component_sources", "paths": missing_embedded})

    source_manifest_path = source_dir / "manifest.json"
    bundle_manifest_path = import_dir / "manifest.json"
    for label, path, version in (
        ("source", source_manifest_path, "flow.build.manifest.v1"),
        ("bundle", bundle_manifest_path, "flow.bundle.manifest.v1"),
    ):
        manifest = load_json(path, f"{label} manifest")
        if manifest.get("contract_version") != version or manifest.get("flow_count") != len(EXPECTED_FLOW_KEYS):
            errors.append({"type": f"{label}_manifest_contract_mismatch"})

    return {
        "status": "ok" if not errors else "error",
        "flow_count": len(EXPECTED_FLOW_KEYS),
        "artifact_layers": list(layers),
        "custom_node_instances_checked": custom_instances,
        "active_unique_component_sources": len(expected_sources),
        "embedded_only_component_sources": sorted(EMBEDDED_ONLY_COMPONENT_SOURCES),
        "all_component_sources": len(actual_sources),
        "runtime_asset_hashes": {
            "language_model": assets.language_model_sha256,
            "component_index": assets.component_index_sha256,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate v6 custom Python source parity across source exports and import-ready artifacts."
    )
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--asset-manifest", type=Path, default=DEFAULT_ASSET_MANIFEST)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--import-dir", type=Path, default=DEFAULT_IMPORT_DIR)
    parser.add_argument("--output", type=Path, help="write the JSON audit report to this path")
    args = parser.parse_args()
    try:
        result = audit_repository(
            inventory_path=args.inventory.resolve(),
            asset_manifest_path=args.asset_manifest.resolve(),
            source_dir=args.source_dir.resolve(),
            import_dir=args.import_dir.resolve(),
        )
    except BuildContractError as exc:
        result = {"status": "error", "errors": [{"type": "contract_error", "message": str(exc)}]}
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
