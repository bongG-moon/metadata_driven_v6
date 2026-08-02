from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import re
import sys
import uuid
import zipfile
from copy import deepcopy
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_LANGFLOW_VERSION = "1.9.2"
TARGET_LANGFLOW_BASE_VERSION = "0.9.2"
TARGET_LFX_VERSION = "0.4.2"
TARGET_PYTHON = (3, 12)
EXPECTED_FLOW_KEYS = (
    "metadata_v6_data_analysis",
    "metadata_v6_domain_authoring",
    "metadata_v6_dataset_catalog_authoring",
    "metadata_v6_main_filter_authoring",
    "metadata_v6_domain_policy_authoring",
)
DEFAULT_INVENTORY = PROJECT_ROOT / "contracts" / "flow_inventory.json"
DEFAULT_ASSET_MANIFEST = PROJECT_ROOT / "tools" / "assets" / "runtime_asset_manifest.json"
DEFAULT_LANGUAGE_MODEL_SOURCE = PROJECT_ROOT / "tools" / "assets" / "langflow_1_9_2_language_model.py"

_SENSITIVE_FIELD = re.compile(
    r"(?:^|_)(?:api_?key|secret|token|password|credential|authorization|connection_?string|uri)(?:$|_)",
    re.IGNORECASE,
)
_GLOBAL_VARIABLE = re.compile(r"^[A-Z][A-Z0-9_]{2,127}$")
_NATIVE_DISPLAY_NAMES = {
    "ChatInput": "Chat Input",
    "Chat Input": "Chat Input",
    "ChatOutput": "Chat Output",
    "Chat Output": "Chat Output",
    "TextInput": "Text Input",
    "Text Input": "Text Input",
    "Prompt": "Prompt Template",
    "PromptTemplate": "Prompt Template",
    "Prompt Template": "Prompt Template",
    "LanguageModel": "Language Model",
    "LanguageModelComponent": "Language Model",
    "Language Model": "Language Model",
}
_NOTE_COLORS = {"blue", "green", "grey", "orange", "pink", "purple", "red", "yellow"}


class BuildContractError(RuntimeError):
    """Raised when a generated Flow would violate a frozen v6 contract."""


@dataclass(frozen=True)
class RuntimeAssets:
    language_model_source: Path
    language_model_sha256: str
    component_index: Path
    component_index_sha256: str
    distribution_inventory_sha256: str
    distributions: dict[str, str]

    def manifest_projection(self) -> dict[str, Any]:
        return {
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "packages": dict(self.distributions),
            "distribution_inventory_sha256": self.distribution_inventory_sha256,
            "language_model_source": {
                "path": self.language_model_source.relative_to(PROJECT_ROOT).as_posix(),
                "sha256": self.language_model_sha256,
            },
            "component_index": {
                "path": str(self.component_index),
                "sha256": self.component_index_sha256,
            },
        }


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def load_json(path: Path, label: str) -> Any:
    if not path.exists():
        raise BuildContractError(f"{label} file is required but missing: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise BuildContractError(f"{label} must be UTF-8: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BuildContractError(f"{label} is not valid JSON: {path}: {exc}") from exc


def write_json_atomic(path: Path, value: Any, *, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if compact:
        payload = canonical_json_bytes(value)
    else:
        payload = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def resolve_project_path(value: str, *, label: str, required: bool = True) -> Path:
    text = str(value or "").strip()
    if not text:
        raise BuildContractError(f"{label} path is required")
    path = Path(text)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path = path.resolve()
    try:
        path.relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise BuildContractError(f"{label} must stay inside the v6 project root: {path}") from exc
    if required and not path.exists():
        raise BuildContractError(f"{label} file is required but missing: {path}")
    return path


def _installed_distribution_inventory() -> tuple[dict[str, str], str]:
    rows = sorted(
        {
            f"{dist.metadata.get('Name', '').strip().lower()}=={dist.version}"
            for dist in importlib.metadata.distributions()
            if dist.metadata.get("Name")
        }
    )
    selected = {
        name: importlib.metadata.version(name)
        for name in ("langflow", "langflow-base", "lfx")
    }
    return selected, sha256_bytes(("\n".join(rows) + "\n").encode("utf-8"))


def _resolve_component_index() -> Path:
    explicit = str(os.getenv("LANGFLOW_COMPONENT_INDEX_PATH") or "").strip()
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise BuildContractError(
                "LANGFLOW_COMPONENT_INDEX_PATH does not point to a readable component_index.json: "
                f"{path}"
            )
        return path
    spec = find_spec("lfx")
    if spec is None or not spec.origin:
        raise BuildContractError(
            "lfx is unavailable. Use the exact Python 3.12 runtime or set LANGFLOW_COMPONENT_INDEX_PATH."
        )
    path = Path(spec.origin).resolve().parent / "_assets" / "component_index.json"
    if not path.is_file():
        raise BuildContractError(
            "The installed lfx package has no component_index.json. Set LANGFLOW_COMPONENT_INDEX_PATH "
            "to the exact LFX 0.4.2 asset."
        )
    return path


def validate_runtime_assets(
    asset_manifest_path: Path = DEFAULT_ASSET_MANIFEST,
    *,
    strict_versions: bool = True,
) -> RuntimeAssets:
    manifest = load_json(asset_manifest_path, "runtime asset manifest")
    if manifest.get("contract_version") != "runtime.assets.v1":
        raise BuildContractError("runtime asset manifest contract_version must be runtime.assets.v1")

    packages, inventory_hash = _installed_distribution_inventory()
    expected_packages = {
        "langflow": TARGET_LANGFLOW_VERSION,
        "langflow-base": TARGET_LANGFLOW_BASE_VERSION,
        "lfx": TARGET_LFX_VERSION,
    }
    manifest_packages = manifest.get("packages")
    if manifest_packages != expected_packages:
        raise BuildContractError(
            f"runtime asset manifest package tuple is invalid: {manifest_packages!r}; expected {expected_packages!r}"
        )
    if strict_versions and packages != expected_packages:
        raise BuildContractError(
            f"installed Langflow package tuple mismatch: {packages!r}; expected {expected_packages!r}"
        )
    if strict_versions and sys.version_info[:2] != TARGET_PYTHON:
        raise BuildContractError(
            f"Python {TARGET_PYTHON[0]}.{TARGET_PYTHON[1]}.x is required; running {sys.version.split()[0]}"
        )

    language_asset = manifest.get("language_model_source") or {}
    language_path = resolve_project_path(
        str(language_asset.get("path") or ""), label="Language Model source"
    )
    language_hash = sha256_file(language_path)
    expected_language_hash = str(language_asset.get("sha256") or "").lower()
    if language_hash != expected_language_hash:
        raise BuildContractError(
            f"Language Model source hash mismatch: {language_hash}; expected {expected_language_hash}"
        )

    index_path = _resolve_component_index()
    index_hash = sha256_file(index_path)
    expected_index_hash = str((manifest.get("component_index") or {}).get("sha256") or "").lower()
    if index_hash != expected_index_hash:
        source_hint = "LANGFLOW_COMPONENT_INDEX_PATH" if os.getenv("LANGFLOW_COMPONENT_INDEX_PATH") else "installed lfx"
        raise BuildContractError(
            f"component index hash mismatch from {source_hint}: {index_hash}; expected {expected_index_hash}"
        )

    return RuntimeAssets(
        language_model_source=language_path,
        language_model_sha256=language_hash,
        component_index=index_path,
        component_index_sha256=index_hash,
        distribution_inventory_sha256=inventory_hash,
        distributions=packages,
    )


def validate_inventory(payload: Any) -> tuple[uuid.UUID, list[dict[str, Any]]]:
    if not isinstance(payload, dict):
        raise BuildContractError("flow inventory root must be an object")
    if payload.get("contract_version") != "flow.inventory.v1":
        raise BuildContractError("flow inventory contract_version must be flow.inventory.v1")
    if payload.get("last_tested_version") != TARGET_LANGFLOW_VERSION:
        raise BuildContractError("flow inventory last_tested_version must be 1.9.2")
    try:
        namespace = uuid.UUID(str(payload.get("uuid_namespace") or ""))
    except (ValueError, AttributeError) as exc:
        raise BuildContractError("flow inventory uuid_namespace must be a fixed UUID") from exc

    flows = payload.get("flows")
    if not isinstance(flows, list):
        raise BuildContractError("flow inventory flows must be an array")
    keys = [str(item.get("logical_key") or "") for item in flows if isinstance(item, dict)]
    if len(flows) != len(EXPECTED_FLOW_KEYS) or set(keys) != set(EXPECTED_FLOW_KEYS):
        raise BuildContractError(
            f"flow inventory must contain exactly {list(EXPECTED_FLOW_KEYS)!r}; got {keys!r}"
        )
    if len(keys) != len(set(keys)):
        raise BuildContractError("flow inventory logical_key values must be unique")

    normalized: list[dict[str, Any]] = []
    by_key = {str(item.get("logical_key")): item for item in flows if isinstance(item, dict)}
    for logical_key in EXPECTED_FLOW_KEYS:
        item = by_key[logical_key]
        endpoint_name = str(item.get("endpoint_name") or "")
        if endpoint_name != logical_key:
            raise BuildContractError(
                f"{logical_key}: endpoint_name must equal logical_key; got {endpoint_name!r}"
            )
        display_name = str(item.get("display_name") or "").strip()
        purpose = str(item.get("purpose") or "").strip()
        if not display_name or not purpose:
            raise BuildContractError(f"{logical_key}: display_name and purpose are required")
        native_nodes = item.get("native_nodes")
        custom_nodes = item.get("custom_nodes")
        edges = item.get("edges")
        notes = item.get("notes", [])
        if (
            not isinstance(native_nodes, list)
            or not isinstance(custom_nodes, list)
            or not isinstance(edges, list)
            or not isinstance(notes, list)
        ):
            raise BuildContractError(
                f"{logical_key}: native_nodes, custom_nodes, notes, and edges must be arrays"
            )
        node_ids: list[str] = []
        for group_name, specs in (("native_nodes", native_nodes), ("custom_nodes", custom_nodes)):
            for index, spec in enumerate(specs):
                if not isinstance(spec, dict):
                    raise BuildContractError(f"{logical_key}.{group_name}[{index}] must be an object")
                node_id = str(spec.get("id") or "").strip()
                if not node_id:
                    raise BuildContractError(f"{logical_key}.{group_name}[{index}].id is required")
                node_ids.append(node_id)
                if not isinstance(spec.get("position"), dict):
                    raise BuildContractError(f"{logical_key}.{node_id}.position must be an object")
                position = spec["position"]
                if not all(isinstance(position.get(axis), (int, float)) for axis in ("x", "y")):
                    raise BuildContractError(f"{logical_key}.{node_id}.position requires numeric x and y")
                if not isinstance(spec.get("settings", {}), dict):
                    raise BuildContractError(f"{logical_key}.{node_id}.settings must be an object")
                if not isinstance(spec.get("ui", {}), dict):
                    raise BuildContractError(f"{logical_key}.{node_id}.ui must be an object")
                expected_prompt_variables = spec.get("expected_prompt_variables", [])
                if not isinstance(expected_prompt_variables, list) or not all(
                    isinstance(value, str) and value.strip() for value in expected_prompt_variables
                ):
                    raise BuildContractError(
                        f"{logical_key}.{node_id}.expected_prompt_variables must be an array of names"
                    )
                if group_name == "native_nodes" and not str(spec.get("type") or "").strip():
                    raise BuildContractError(f"{logical_key}.{node_id}.type is required")
                if group_name == "custom_nodes" and not str(spec.get("source") or "").strip():
                    raise BuildContractError(f"{logical_key}.{node_id}.source is required")
        note_ids: list[str] = []
        for index, note in enumerate(notes):
            if not isinstance(note, dict):
                raise BuildContractError(f"{logical_key}.notes[{index}] must be an object")
            note_id = str(note.get("id") or "").strip()
            markdown = str(note.get("markdown") or "").strip()
            position = note.get("position")
            if not note_id or not markdown:
                raise BuildContractError(f"{logical_key}.notes[{index}] requires id and markdown")
            if not isinstance(position, dict) or not all(
                isinstance(position.get(axis), (int, float)) for axis in ("x", "y")
            ):
                raise BuildContractError(f"{logical_key}.{note_id}.position requires numeric x and y")
            width = note.get("width", 360)
            height = note.get("height", 300)
            if not isinstance(width, (int, float)) or not 180 <= width <= 1200:
                raise BuildContractError(f"{logical_key}.{note_id}.width must be between 180 and 1200")
            if not isinstance(height, (int, float)) or not 120 <= height <= 1200:
                raise BuildContractError(f"{logical_key}.{note_id}.height must be between 120 and 1200")
            color = str(note.get("color") or "blue").strip().lower()
            if color not in _NOTE_COLORS:
                raise BuildContractError(f"{logical_key}.{note_id}.color is not supported: {color!r}")
            note_ids.append(note_id)
        all_ids = [*node_ids, *note_ids]
        if len(all_ids) != len(set(all_ids)):
            raise BuildContractError(f"{logical_key}: node ids must be unique")
        known = set(node_ids)
        edge_keys: set[tuple[str, str, str, str]] = set()
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                raise BuildContractError(f"{logical_key}.edges[{index}] must be an object")
            values = tuple(str(edge.get(name) or "").strip() for name in (
                "source", "source_output", "target", "target_input"
            ))
            if not all(values):
                raise BuildContractError(
                    f"{logical_key}.edges[{index}] requires source/source_output/target/target_input"
                )
            if values[0] not in known or values[2] not in known:
                raise BuildContractError(f"{logical_key}.edges[{index}] references an unknown node: {values!r}")
            if values in edge_keys:
                raise BuildContractError(f"{logical_key}: duplicate edge {values!r}")
            edge_keys.add(values)

        expected_uuid = str(uuid.uuid5(namespace, logical_key))
        declared_uuid = str(item.get("expected_uuid") or item.get("id") or "").strip()
        if declared_uuid and declared_uuid != expected_uuid:
            raise BuildContractError(
                f"{logical_key}: declared UUID {declared_uuid} != UUIDv5(namespace, logical_key) {expected_uuid}"
            )
        normalized.append(deepcopy(item))
    return namespace, normalized


def load_inventory(path: Path = DEFAULT_INVENTORY) -> tuple[dict[str, Any], uuid.UUID, list[dict[str, Any]]]:
    payload = load_json(path, "flow inventory")
    namespace, flows = validate_inventory(payload)
    return payload, namespace, flows


def _find_native_component(value: Any, display_name: str) -> dict[str, Any]:
    if isinstance(value, dict):
        if value.get("display_name") == display_name and isinstance(value.get("template"), dict):
            return deepcopy(value)
        for child in value.values():
            found = _find_native_component(child, display_name)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_native_component(child, display_name)
            if found:
                return found
    return {}


def load_component_index(assets: RuntimeAssets) -> Any:
    return load_json(assets.component_index, "Langflow 1.9.2 component index")


def _contains_sensitive_mapping(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if _SENSITIVE_FIELD.search(str(key)) and child not in (None, "", [], {}):
                return True
            if _contains_sensitive_mapping(child):
                return True
    elif isinstance(value, list):
        return any(_contains_sensitive_mapping(item) for item in value)
    return False


def _apply_settings(config: dict[str, Any], settings: dict[str, Any], *, node_id: str) -> list[Path]:
    template = config.get("template")
    if not isinstance(template, dict):
        raise BuildContractError(f"{node_id}: component template is missing")
    prompt_sources: list[Path] = []
    for field_name, raw_setting in settings.items():
        if field_name in {"prompt_source", "_prompt_source"}:
            prompt_path = resolve_project_path(str(raw_setting), label=f"{node_id} prompt source")
            prompt_sources.append(prompt_path)
            prompt_text = prompt_path.read_text(encoding="utf-8")
            prompt_field = template.get("template")
            if not isinstance(prompt_field, dict):
                raise BuildContractError(f"{node_id}: prompt_source is only valid for a Prompt Template node")
            prompt_field["value"] = prompt_text
            continue
        if _SENSITIVE_FIELD.search(field_name):
            raise BuildContractError(
                f"{node_id}.{field_name}: secret-bearing settings are not allowed in flow_inventory.json"
            )
        field = template.get(field_name)
        if not isinstance(field, dict):
            raise BuildContractError(f"{node_id}: unknown component setting {field_name!r}")
        if _contains_sensitive_mapping(raw_setting):
            raise BuildContractError(f"{node_id}.{field_name}: nested secret-bearing value is not allowed")
        if isinstance(raw_setting, dict) and set(raw_setting).issubset(
            {"value", "advanced", "show", "required", "load_from_db"}
        ):
            for attribute, attribute_value in raw_setting.items():
                field[attribute] = deepcopy(attribute_value)
        else:
            field["value"] = deepcopy(raw_setting)
    return prompt_sources


def _hydrate_prompt_template(
    config: dict[str, Any],
    *,
    node_id: str,
    expected_variables: list[str],
) -> None:
    """Rebuild Langflow 1.9.2 dynamic Prompt ports after loading an external template."""
    from lfx.base.prompts.api_utils import process_prompt_template
    from lfx.inputs.input_mixin import FieldTypes

    template = config.get("template")
    prompt_field = template.get("template") if isinstance(template, dict) else None
    if not isinstance(prompt_field, dict):
        raise BuildContractError(f"{node_id}: Prompt Template has no template input")
    prompt_text = str(prompt_field.get("value") or "")
    custom_fields = config.get("custom_fields")
    if not isinstance(custom_fields, dict):
        custom_fields = {}
        config["custom_fields"] = custom_fields
    use_double_brackets = bool((template.get("use_double_brackets") or {}).get("value"))
    prompt_field["type"] = (
        FieldTypes.MUSTACHE_PROMPT.value if use_double_brackets else FieldTypes.PROMPT.value
    )
    try:
        variables = process_prompt_template(
            template=prompt_text,
            name="template",
            custom_fields=custom_fields,
            frontend_node_template=template,
            is_mustache=use_double_brackets,
        )
    except Exception as exc:
        raise BuildContractError(f"{node_id}: Prompt Template dynamic input hydration failed: {exc}") from exc
    expected = [str(value).strip() for value in expected_variables]
    if sorted(variables) != sorted(expected):
        raise BuildContractError(
            f"{node_id}: prompt variables {sorted(variables)!r} do not match expected {sorted(expected)!r}"
        )


def _apply_ui_labels(config: dict[str, Any], ui: dict[str, Any], *, node_id: str) -> None:
    if not ui:
        return
    allowed = {"display_name", "description", "input_labels", "output_labels"}
    unknown = sorted(set(ui) - allowed)
    if unknown:
        raise BuildContractError(f"{node_id}.ui contains unsupported keys: {unknown!r}")
    if "display_name" in ui:
        display_name = str(ui["display_name"] or "").strip()
        if not display_name:
            raise BuildContractError(f"{node_id}.ui.display_name must not be empty")
        config["display_name"] = display_name
    if "description" in ui:
        description = str(ui["description"] or "").strip()
        if not description:
            raise BuildContractError(f"{node_id}.ui.description must not be empty")
        config["description"] = description
    template = config.get("template")
    input_labels = ui.get("input_labels", {})
    if not isinstance(input_labels, dict):
        raise BuildContractError(f"{node_id}.ui.input_labels must be an object")
    for field_name, label_value in input_labels.items():
        field = template.get(field_name) if isinstance(template, dict) else None
        label = str(label_value or "").strip()
        if not isinstance(field, dict) or not label:
            raise BuildContractError(f"{node_id}.ui.input_labels.{field_name} is invalid")
        field["display_name"] = label
    output_labels = ui.get("output_labels", {})
    if not isinstance(output_labels, dict):
        raise BuildContractError(f"{node_id}.ui.output_labels must be an object")
    outputs = config.get("outputs")
    for output_name, label_value in output_labels.items():
        output = next(
            (item for item in outputs if isinstance(item, dict) and item.get("name") == output_name),
            None,
        ) if isinstance(outputs, list) else None
        label = str(label_value or "").strip()
        if not isinstance(output, dict) or not label:
            raise BuildContractError(f"{node_id}.ui.output_labels.{output_name} is invalid")
        output["display_name"] = label


def _assert_no_serialized_secrets(config: dict[str, Any], *, node_id: str) -> None:
    template = config.get("template", {})
    for field_name, field in template.items() if isinstance(template, dict) else []:
        if not _SENSITIVE_FIELD.search(str(field_name)) or not isinstance(field, dict):
            continue
        value = field.get("value")
        if value in (None, "", [], {}):
            continue
        if field.get("load_from_db") is True and isinstance(value, str) and _GLOBAL_VARIABLE.fullmatch(value):
            continue
        raise BuildContractError(
            f"{node_id}.{field_name}: a secret-like value would be serialized; use an empty input or Langflow Global Variable"
        )


def _node_shell(node_id: str, node_type: str, position: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    return {
        "data": {"id": node_id, "node": config, "showNode": True, "type": node_type},
        "dragging": False,
        "id": node_id,
        "measured": {"height": 267, "width": 320},
        "position": {"x": float(position["x"]), "y": float(position["y"])},
        "selected": False,
        "type": "genericNode",
    }


def _build_note_node(spec: dict[str, Any]) -> dict[str, Any]:
    node_id = str(spec["id"])
    position = {"x": float(spec["position"]["x"]), "y": float(spec["position"]["y"])}
    width = float(spec.get("width", 360))
    height = float(spec.get("height", 300))
    config = {
        "description": str(spec["markdown"]),
        "display_name": str(spec.get("title") or ""),
        "documentation": "",
        "template": {"backgroundColor": str(spec.get("color") or "blue").lower()},
        "lf_version": TARGET_LANGFLOW_VERSION,
    }
    return {
        "data": {"id": node_id, "node": config, "type": "note"},
        "dragging": False,
        "height": height,
        "id": node_id,
        "position": position,
        "positionAbsolute": deepcopy(position),
        "resizing": False,
        "selected": False,
        "style": {"height": height, "width": width},
        "type": "noteNode",
        "width": width,
    }


def build_custom_node(spec: dict[str, Any], logical_key: str) -> tuple[dict[str, Any], dict[str, Any]]:
    from lfx.custom.utils import create_component_template

    node_id = str(spec["id"])
    source = resolve_project_path(str(spec["source"]), label=f"{logical_key}.{node_id} source")
    component_root = (PROJECT_ROOT / "langflow_components").resolve()
    try:
        source.relative_to(component_root)
    except ValueError as exc:
        raise BuildContractError(f"{logical_key}.{node_id}: custom source must be under langflow_components") from exc
    if source.suffix.lower() != ".py":
        raise BuildContractError(f"{logical_key}.{node_id}: custom source must be a .py file")
    code = source.read_text(encoding="utf-8")
    module_name = f"metadata_v6.{logical_key}.{source.stem}"
    try:
        config, instance = create_component_template({"code": code, "output_types": []}, module_name=module_name)
    except Exception as exc:
        raise BuildContractError(f"{logical_key}.{node_id}: custom component template parse failed: {exc}") from exc
    source_hash = sha256_bytes(code.encode("utf-8"))
    config["lf_version"] = TARGET_LANGFLOW_VERSION
    declared_metadata = spec.get("metadata") if isinstance(spec.get("metadata"), dict) else {}
    config.setdefault("metadata", {}).update(
        {
            **deepcopy(declared_metadata),
            "code_hash": source_hash[:12],
            "source_path": source.relative_to(PROJECT_ROOT).as_posix(),
            "source_sha256": source_hash,
        }
    )
    config["is_output"] = bool(getattr(instance, "is_output", config.get("is_output", False)))
    settings = deepcopy(spec.get("settings", {}))
    registry_source_value = settings.pop("registry_source", None)
    registry_source_metadata: dict[str, str] = {}
    if registry_source_value is not None:
        registry_path = resolve_project_path(
            str(registry_source_value),
            label=f"{logical_key}.{node_id} registry source",
        )
        try:
            registry_path.relative_to((PROJECT_ROOT / "metadata" / "domain_packs").resolve())
        except ValueError as exc:
            raise BuildContractError(
                f"{logical_key}.{node_id}: registry_source must be under metadata/domain_packs"
            ) from exc
        registry_text = registry_path.read_text(encoding="utf-8")
        if len(registry_text.encode("utf-8")) > 256 * 1024:
            raise BuildContractError(f"{logical_key}.{node_id}: registry_source exceeds 256KB")
        try:
            json.loads(registry_text)
        except json.JSONDecodeError as exc:
            raise BuildContractError(f"{logical_key}.{node_id}: registry_source is not valid JSON") from exc
        settings["registry_json"] = registry_text
        registry_source_metadata = {
            "registry_source": registry_path.relative_to(PROJECT_ROOT).as_posix(),
            "registry_source_sha256": sha256_bytes(registry_text.encode("utf-8")),
        }
        config.setdefault("metadata", {}).update(registry_source_metadata)
    prompt_sources = _apply_settings(config, settings, node_id=node_id)
    if prompt_sources:
        raise BuildContractError(f"{logical_key}.{node_id}: prompt_source is invalid for a custom component")
    _apply_ui_labels(config, spec.get("ui", {}), node_id=node_id)
    _assert_no_serialized_secrets(config, node_id=node_id)
    node_type = instance.__class__.__name__
    node = _node_shell(node_id, node_type, spec["position"], config)
    return node, {
        "node_id": node_id,
        "source": source.relative_to(PROJECT_ROOT).as_posix(),
        "sha256": source_hash,
        **registry_source_metadata,
    }


def build_native_node(
    spec: dict[str, Any],
    component_index: Any,
    assets: RuntimeAssets,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    from lfx.custom.eval import eval_custom_component_code

    node_id = str(spec["id"])
    requested_type = str(spec["type"])
    display_name = _NATIVE_DISPLAY_NAMES.get(requested_type, requested_type)
    config = _find_native_component(component_index, display_name)
    if not config:
        raise BuildContractError(f"{node_id}: native Langflow 1.9.2 component not found: {display_name!r}")
    config["lf_version"] = TARGET_LANGFLOW_VERSION
    template = config.get("template", {})
    code_field = template.get("code") if isinstance(template, dict) else None
    if display_name == "Language Model":
        if not isinstance(code_field, dict):
            raise BuildContractError(f"{node_id}: Language Model template has no code field")
        code = assets.language_model_source.read_text(encoding="utf-8")
        code_field["value"] = code
        config.setdefault("metadata", {}).update(
            {
                "code_hash": assets.language_model_sha256[:12],
                "asset_path": assets.language_model_source.relative_to(PROJECT_ROOT).as_posix(),
                "asset_sha256": assets.language_model_sha256,
            }
        )
    settings = spec.get("settings", {})
    prompt_paths = _apply_settings(config, settings, node_id=node_id)
    if len(prompt_paths) > 1:
        raise BuildContractError(f"{node_id}: a Prompt Template may reference only one prompt source")
    if prompt_paths:
        prompt_path = prompt_paths[0]
        prompt_hash = sha256_file(prompt_path)
        config.setdefault("metadata", {}).update(
            {
                "prompt_source_path": prompt_path.relative_to(PROJECT_ROOT).as_posix(),
                "prompt_source_sha256": prompt_hash,
            }
        )
    if display_name == "Prompt Template":
        _hydrate_prompt_template(
            config,
            node_id=node_id,
            expected_variables=spec.get("expected_prompt_variables", []),
        )
    elif spec.get("expected_prompt_variables"):
        raise BuildContractError(f"{node_id}: expected_prompt_variables is only valid for Prompt Template")
    _apply_ui_labels(config, spec.get("ui", {}), node_id=node_id)
    _assert_no_serialized_secrets(config, node_id=node_id)
    code = str((config.get("template", {}).get("code") or {}).get("value") or "")
    if not code:
        raise BuildContractError(f"{node_id}: native component has no embedded source")
    try:
        node_type = eval_custom_component_code(code).__name__
    except Exception as exc:
        raise BuildContractError(f"{node_id}: native component source parse failed: {exc}") from exc
    config.setdefault("metadata", {}).setdefault("code_hash", sha256_bytes(code.encode("utf-8"))[:12])
    node = _node_shell(node_id, node_type, spec["position"], config)
    prompt_records = [
        {"node_id": node_id, "source": path.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256_file(path)}
        for path in prompt_paths
    ]
    return node, prompt_records


def _handle_text(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).replace('"', "œ")


def build_edge(edge_spec: dict[str, Any], node_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source = node_index[str(edge_spec["source"])]
    target = node_index[str(edge_spec["target"])]
    source_name = str(edge_spec["source_output"])
    target_name = str(edge_spec["target_input"])
    outputs = source["data"]["node"].get("outputs", [])
    source_output = next((item for item in outputs if item.get("name") == source_name), None)
    if source_output is None:
        raise BuildContractError(f"{source['id']}.{source_name}: declared source output does not exist")
    target_input = target["data"]["node"].get("template", {}).get(target_name)
    if not isinstance(target_input, dict):
        raise BuildContractError(f"{target['id']}.{target_name}: declared target input does not exist")
    if target_input.get("advanced") is True:
        raise BuildContractError(f"{target['id']}.{target_name}: edges may not target advanced inputs")

    output_types = list(source_output.get("types") or [])
    if not output_types and source_output.get("selected"):
        output_types = [source_output["selected"]]
    input_types = list(target_input.get("input_types") or [])
    if not input_types:
        input_types = ["Message"] if target_input.get("type") == "str" else ["Data"]
    source_handle = {
        "dataType": source["data"]["type"],
        "id": source["id"],
        "name": source_name,
        "output_types": output_types,
    }
    target_handle = {
        "fieldName": target_name,
        "id": target["id"],
        "inputTypes": input_types,
        "type": target_input.get("type") or "other",
    }
    source_text = _handle_text(source_handle)
    target_text = _handle_text(target_handle)
    return {
        "animated": False,
        "className": "",
        "data": {"sourceHandle": source_handle, "targetHandle": target_handle},
        "id": f"xy-edge__{source['id']}{source_text}-{target['id']}{target_text}",
        "selected": False,
        "source": source["id"],
        "sourceHandle": source_text,
        "target": target["id"],
        "targetHandle": target_text,
    }


def validate_acyclic(flow: dict[str, Any]) -> None:
    nodes = {str(node["id"]) for node in flow.get("data", {}).get("nodes", [])}
    indegree = {node_id: 0 for node_id in nodes}
    outgoing = {node_id: [] for node_id in nodes}
    for edge in flow.get("data", {}).get("edges", []):
        source, target = str(edge["source"]), str(edge["target"])
        outgoing[source].append(target)
        indegree[target] += 1
    queue = sorted(node_id for node_id, value in indegree.items() if value == 0)
    visited = 0
    while queue:
        node_id = queue.pop(0)
        visited += 1
        for target in sorted(outgoing[node_id]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort()
    if visited != len(nodes):
        raise BuildContractError(f"{flow.get('endpoint_name')}: Flow graph contains a cycle")


def build_flow(
    flow_spec: dict[str, Any],
    namespace: uuid.UUID,
    component_index: Any,
    assets: RuntimeAssets,
) -> tuple[dict[str, Any], dict[str, Any]]:
    logical_key = str(flow_spec["logical_key"])
    flow_id = str(uuid.uuid5(namespace, logical_key))
    nodes: list[dict[str, Any]] = []
    custom_sources: list[dict[str, Any]] = []
    prompt_sources: list[dict[str, Any]] = []
    for spec in flow_spec["native_nodes"]:
        node, prompts = build_native_node(spec, component_index, assets)
        nodes.append(node)
        prompt_sources.extend(prompts)
    for spec in flow_spec["custom_nodes"]:
        node, source = build_custom_node(spec, logical_key)
        nodes.append(node)
        custom_sources.append(source)
    notes = [_build_note_node(spec) for spec in flow_spec.get("notes", [])]
    nodes.extend(notes)
    node_index = {str(node["id"]): node for node in nodes}
    edges = [build_edge(edge, node_index) for edge in flow_spec["edges"]]
    flow = {
        "description": str(flow_spec["purpose"]),
        "endpoint_name": logical_key,
        "id": flow_id,
        "is_component": False,
        "last_tested_version": TARGET_LANGFLOW_VERSION,
        "locked": False,
        "name": str(flow_spec["display_name"]),
        "tags": sorted(set(["metadata-driven-v6", "standalone", "typed-ir", *flow_spec.get("tags", [])])),
        "data": {
            "edges": edges,
            "nodes": nodes,
            "viewport": deepcopy(flow_spec.get("viewport") or {"x": 0, "y": 0, "zoom": 0.55}),
        },
    }
    validate_acyclic(flow)
    return flow, {
        "logical_key": logical_key,
        "endpoint_name": logical_key,
        "display_name": str(flow_spec["display_name"]),
        "id": flow_id,
        "nodes": len(nodes),
        "executable_nodes": len(nodes) - len(notes),
        "annotation_nodes": len(notes),
        "edges": len(edges),
        "custom_sources": custom_sources,
        "prompt_sources": prompt_sources,
    }


def flow_export_filename(logical_key: str) -> str:
    return f"{logical_key}_flow_v6_standalone.json"


def indexed_import_filename(index: int, logical_key: str) -> str:
    return f"{index:02d}_{logical_key}_flow_v6_standalone.json"


def contract_hash_inventory() -> list[dict[str, str]]:
    contract_root = PROJECT_ROOT / "contracts"
    if not contract_root.exists():
        raise BuildContractError(f"contracts directory is required but missing: {contract_root}")
    paths = sorted(path for path in contract_root.rglob("*.json") if path.is_file())
    if not paths:
        raise BuildContractError(f"no machine-readable contract JSON files found under {contract_root}")
    return [
        {"path": path.relative_to(PROJECT_ROOT).as_posix(), "sha256": sha256_file(path)}
        for path in paths
    ]


def deterministic_zip(zip_path: Path, files: Iterable[Path], *, root: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = zip_path.with_name(f".{zip_path.name}.tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    temporary.replace(zip_path)


def validate_flow_identity_and_versions(
    flow: dict[str, Any],
    namespace: uuid.UUID,
    expected_logical_key: str,
) -> list[str]:
    errors: list[str] = []
    expected_id = str(uuid.uuid5(namespace, expected_logical_key))
    if flow.get("endpoint_name") != expected_logical_key:
        errors.append(f"endpoint_name={flow.get('endpoint_name')!r}, expected {expected_logical_key!r}")
    if flow.get("id") != expected_id:
        errors.append(f"id={flow.get('id')!r}, expected UUIDv5 {expected_id!r}")
    if flow.get("last_tested_version") != TARGET_LANGFLOW_VERSION:
        errors.append(f"last_tested_version={flow.get('last_tested_version')!r}, expected 1.9.2")
    for node in flow.get("data", {}).get("nodes", []):
        node_id = str(node.get("id") or "")
        component = node.get("data", {}).get("node")
        if not isinstance(component, dict):
            errors.append(f"{node_id}: missing serialized component")
        elif component.get("lf_version") != TARGET_LANGFLOW_VERSION:
            errors.append(f"{node_id}: lf_version={component.get('lf_version')!r}, expected 1.9.2")
    return errors
