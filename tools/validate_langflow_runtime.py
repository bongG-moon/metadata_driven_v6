from __future__ import annotations

import argparse
import json
import os
import uuid
from pathlib import Path
from typing import Any

import requests
from lfx.custom.eval import eval_custom_component_code
from lfx.custom.utils import create_component_template

from flow_builder_support import (
    DEFAULT_ASSET_MANIFEST,
    DEFAULT_INVENTORY,
    EXPECTED_FLOW_KEYS,
    PROJECT_ROOT,
    BuildContractError,
    flow_export_filename,
    load_inventory,
    load_json,
    sha256_bytes,
    sha256_file,
    validate_flow_identity_and_versions,
    validate_runtime_assets,
    write_json_atomic,
)


DEFAULT_FLOW_DIR = PROJECT_ROOT / "flow_exports"


def validate_node_templates(flow: dict[str, Any]) -> dict[str, Any]:
    passed: list[str] = []
    skipped_notes: list[str] = []
    failures: list[dict[str, str]] = []
    for node in flow.get("data", {}).get("nodes", []):
        node_id = str(node.get("id") or "")
        if node.get("type") == "noteNode" or (node.get("data") or {}).get("type") == "note":
            skipped_notes.append(node_id)
            continue
        config = node.get("data", {}).get("node", {})
        template = config.get("template", {}) if isinstance(config, dict) else {}
        code_field = template.get("code") if isinstance(template, dict) else None
        if template.get("_type") != "Component" or not isinstance(code_field, dict):
            failures.append({"id": node_id, "error": "serialized node has no Component code template"})
            continue
        try:
            code = str(code_field.get("value") or "")
            if not code.strip():
                raise ValueError("embedded component source is empty")
            source_hash = sha256_bytes(code.encode("utf-8"))
            actual_short_hash = str(config.get("metadata", {}).get("code_hash") or "")
            if actual_short_hash != source_hash[:12]:
                raise ValueError(
                    f"code_hash mismatch: {actual_short_hash!r} != {source_hash[:12]!r}"
                )
            component_class = eval_custom_component_code(code)
            create_component_template(
                {"code": code, "output_types": []},
                module_name=f"metadata_v6_runtime_validation.{node_id}",
            )
            expected_inputs = [item.name for item in getattr(component_class, "inputs", [])]
            expected_outputs = [item.name for item in getattr(component_class, "outputs", [])]
            serialized_inputs = list(config.get("field_order", []))
            serialized_outputs = [item.get("name") for item in config.get("outputs", [])]
            if expected_inputs != serialized_inputs:
                raise ValueError(f"input mismatch: {expected_inputs!r} != {serialized_inputs!r}")
            if expected_outputs != serialized_outputs:
                raise ValueError(f"output mismatch: {expected_outputs!r} != {serialized_outputs!r}")
            passed.append(node_id)
        except Exception as exc:
            failures.append({"id": node_id, "error": f"{type(exc).__name__}: {exc}"})
    return {
        "checked": len(passed) + len(failures),
        "passed": len(passed),
        "failed": len(failures),
        "skipped_sticky_notes": skipped_notes,
        "failures": failures,
    }


def _auth_headers(session: requests.Session, server_url: str) -> dict[str, str]:
    base = server_url.rstrip("/") + "/api/v1"
    api_key = str(os.getenv("LANGFLOW_API_KEY") or "").strip()
    if api_key:
        return {"x-api-key": api_key}
    response = session.get(base + "/auto_login", timeout=30)
    response.raise_for_status()
    token = str(response.json().get("access_token") or "")
    if not token:
        raise BuildContractError(
            "isolated Langflow import requires LANGFLOW_API_KEY or an enabled auto_login endpoint"
        )
    return {"Authorization": f"Bearer {token}"}


def import_flows(
    paths: list[Path],
    server_url: str,
    *,
    partial_build: bool,
    stop_component_id: str,
    smoke_question: str,
) -> dict[str, Any]:
    base = server_url.rstrip("/") + "/api/v1"
    session = requests.Session()
    headers = _auth_headers(session, server_url)
    imported: list[dict[str, Any]] = []
    for path in paths:
        with path.open("rb") as flow_file:
            response = session.post(
                base + "/flows/upload/",
                headers=headers,
                files={"file": (path.name, flow_file, "application/json")},
                timeout=240,
            )
        response.raise_for_status()
        value = response.json()
        uploaded = value[-1] if isinstance(value, list) else value
        record: dict[str, Any] = {
            "file": path.name,
            "upload_status": response.status_code,
            "flow_id": uploaded.get("id"),
            "flow_name": uploaded.get("name"),
            "endpoint_name": uploaded.get("endpoint_name"),
            "nodes": len(uploaded.get("data", {}).get("nodes", [])),
            "edges": len(uploaded.get("data", {}).get("edges", [])),
        }
        if partial_build:
            if len(paths) != 1 or not stop_component_id:
                raise BuildContractError(
                    "--partial-build requires exactly one --flow and a non-empty --stop-component-id"
                )
            flow_id = str(uploaded.get("id") or "")
            build_response = session.post(
                f"{base}/build/{flow_id}/flow",
                headers={**headers, "Content-Type": "application/json"},
                params={
                    "stop_component_id": stop_component_id,
                    "event_delivery": "direct",
                    "log_builds": "true",
                },
                json={
                    "inputs": {
                        "input_value": smoke_question,
                        "session": "metadata-driven-v6-isolated-runtime-validation",
                        "type": "chat",
                    }
                },
                timeout=300,
            )
            build_response.raise_for_status()
            vertices: list[dict[str, Any]] = []
            for line in build_response.text.splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("event") != "end_vertex":
                    continue
                build_data = event.get("data", {}).get("build_data", {})
                vertices.append(
                    {
                        "id": build_data.get("id"),
                        "valid": build_data.get("valid"),
                        "duration": build_data.get("data", {}).get("duration"),
                    }
                )
            record["partial_build"] = {
                "stop_component_id": stop_component_id,
                "passed": bool(vertices)
                and all(item.get("valid") is True for item in vertices)
                and any(item.get("id") == stop_component_id for item in vertices),
                "vertices": vertices,
            }
        imported.append(record)
    return {
        "warning": "The validator uploads flows and does not delete them; use an isolated Langflow profile.",
        "imports": imported,
    }


def _resolve_paths(
    explicit: list[Path],
    all_flows: bool,
    flow_dir: Path,
    flow_specs: list[dict[str, Any]],
) -> list[Path]:
    if explicit and all_flows:
        raise BuildContractError("use either --flow or --all-flows, not both")
    if explicit:
        paths = [path.resolve() for path in explicit]
    else:
        paths = [
            flow_dir / flow_export_filename(str(spec["logical_key"]))
            for spec in flow_specs
        ]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise BuildContractError("Flow exports are missing: " + ", ".join(missing))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse every v6 node with the exact LFX runtime and optionally import into an isolated Langflow server."
    )
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--asset-manifest", type=Path, default=DEFAULT_ASSET_MANIFEST)
    parser.add_argument("--flow-dir", type=Path, default=DEFAULT_FLOW_DIR)
    parser.add_argument("--flow", type=Path, action="append", default=[])
    parser.add_argument("--all-flows", action="store_true")
    parser.add_argument("--expected-flow-count", type=int, default=5)
    parser.add_argument("--strict-versions", action="store_true")
    parser.add_argument("--server-url", default="")
    parser.add_argument("--partial-build", action="store_true")
    parser.add_argument("--stop-component-id", default="")
    parser.add_argument("--smoke-question", default="오늘 DA공정 WIP 알려줘")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    try:
        assets = validate_runtime_assets(
            args.asset_manifest.resolve(), strict_versions=args.strict_versions
        )
        _, namespace, flow_specs = load_inventory(args.inventory.resolve())
        paths = _resolve_paths(
            args.flow,
            args.all_flows,
            args.flow_dir.resolve(),
            flow_specs,
        )
        if len(paths) != args.expected_flow_count:
            raise BuildContractError(
                f"expected {args.expected_flow_count} Flow files, got {len(paths)}"
            )
        spec_by_key = {str(item["logical_key"]): item for item in flow_specs}
        reports: list[dict[str, Any]] = []
        for path in paths:
            flow = load_json(path, f"Flow export {path.name}")
            logical_key = str(flow.get("endpoint_name") or "")
            if logical_key not in spec_by_key:
                raise BuildContractError(f"{path}: endpoint_name is not in flow inventory: {logical_key!r}")
            identity_errors = validate_flow_identity_and_versions(flow, namespace, logical_key)
            node_report = validate_node_templates(flow)
            reports.append(
                {
                    "file": str(path),
                    "logical_key": logical_key,
                    "id": flow.get("id"),
                    "sha256": sha256_file(path),
                    "identity_errors": identity_errors,
                    "node_templates": node_report,
                }
            )
        result: dict[str, Any] = {
            "status": "ok",
            "runtime_assets": assets.manifest_projection(),
            "flow_count": len(reports),
            "flows": reports,
        }
        if args.server_url:
            result["server"] = import_flows(
                paths,
                args.server_url,
                partial_build=args.partial_build,
                stop_component_id=args.stop_component_id,
                smoke_question=args.smoke_question,
            )
        failed = any(
            report["identity_errors"] or report["node_templates"]["failed"]
            for report in reports
        )
        if args.server_url:
            failed = failed or any(
                not item.get("partial_build", {"passed": True}).get("passed", True)
                for item in result["server"]["imports"]
            )
        if failed:
            result["status"] = "error"
    except (BuildContractError, requests.RequestException, Exception) as exc:
        result = {"status": "error", "error": f"{type(exc).__name__}: {exc}"}
    if args.output:
        write_json_atomic(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
