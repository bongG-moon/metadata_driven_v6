from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "tools" / "build_standalone_components.py"
API_TERMINAL_PATH = ROOT / "langflow_components" / "shared" / "00_api_response_terminal.py"
HANGUL = re.compile(r"[가-힣]")

ACTIVE_COMPONENT_CONSTANTS = (
    "REQUEST_STATE_COMPONENT",
    "DOMAIN_BUNDLE_COMPONENT",
    "CANDIDATE_ROUTE_COMPONENT",
    "INTENT_PROMPT_CONTEXT_COMPONENT",
    "INTENT_RESOLVER_COMPONENT",
    "PLAN_COMPILER_COMPONENT",
    "JOB_ROUTER_COMPONENT",
    "DUMMY_RETRIEVER_COMPONENT",
    "SOURCE_MERGER_COMPONENT",
    "TYPED_EXECUTOR_COMPONENT",
    "ANSWER_FACTS_CONTEXT_COMPONENT",
    "ANSWER_CLAIM_VALIDATOR_COMPONENT",
    "RESPONSE_COMMIT_COMPONENT",
    "MESSAGE_PRESENTATION_COMPONENT",
    "GAIA_OUTPUT_COMPONENT",
    "API_RESPONSE_COMPONENT",
    "NATURAL_METADATA_SOURCE_BUNDLE_COMPONENT",
    "AUTHORING_REFERENCE_REGISTRY_COMPONENT",
    "AUTHORING_PROMPT_CONTEXT_COMPONENT",
    "AUTHORING_COMPONENT",
    "AUTHORING_MESSAGE_COMPONENT",
)


def _load_builder():
    spec = importlib.util.spec_from_file_location("v6_component_builder_ui_test", BUILDER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _literal_keyword(call: ast.Call, name: str) -> str | None:
    for keyword in call.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
            return keyword.value.value
    return None


def _call_name(call: ast.Call) -> str:
    target = call.func
    return target.id if isinstance(target, ast.Name) else target.attr if isinstance(target, ast.Attribute) else ""


def _component_class(source: str) -> ast.ClassDef:
    classes = [node for node in ast.parse(source).body if isinstance(node, ast.ClassDef)]
    assert len(classes) == 1
    return classes[0]


def _assigned_text(component: ast.ClassDef, name: str) -> str:
    for node in component.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            assert isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
            return node.value.value
    raise AssertionError(f"{component.name}.{name} is missing")


def _assert_korean_component_ui(source: str) -> None:
    component = _component_class(source)
    assert HANGUL.search(_assigned_text(component, "display_name")), component.name
    assert HANGUL.search(_assigned_text(component, "description")), component.name

    calls = [node for node in ast.walk(component) if isinstance(node, ast.Call)]
    inputs = [call for call in calls if _call_name(call).endswith("Input")]
    outputs = [call for call in calls if _call_name(call) == "Output"]
    assert inputs, component.name
    assert outputs, component.name

    for call in inputs:
        display_name = _literal_keyword(call, "display_name")
        info = _literal_keyword(call, "info")
        assert display_name and HANGUL.search(display_name), (component.name, _literal_keyword(call, "name"), "display_name")
        assert info and HANGUL.search(info), (component.name, _literal_keyword(call, "name"), "info")
    for call in outputs:
        display_name = _literal_keyword(call, "display_name")
        assert display_name and HANGUL.search(display_name), (component.name, _literal_keyword(call, "name"), "display_name")


def test_active_generator_components_have_korean_user_facing_ui() -> None:
    builder = _load_builder()
    for constant_name in ACTIVE_COMPONENT_CONSTANTS:
        _assert_korean_component_ui(getattr(builder, constant_name))


def test_manual_api_terminal_matches_korean_user_facing_ui() -> None:
    source = API_TERMINAL_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    component = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "APIResponseTerminal")
    class_source = ast.get_source_segment(source, component)
    assert class_source is not None
    _assert_korean_component_ui(class_source)


def test_generated_source_specific_retrievers_have_korean_user_facing_ui() -> None:
    for relative in (
        "12_oracle_source_retriever.py",
        "13_h_api_source_retriever.py",
        "14_datalake_source_retriever.py",
        "15_goodocs_source_retriever.py",
    ):
        source = (ROOT / "langflow_components" / "data_analysis" / relative).read_text(encoding="utf-8")
        tree = ast.parse(source)
        component = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name.endswith("SourceRetriever"))
        class_source = ast.get_source_segment(source, component)
        assert class_source is not None
        _assert_korean_component_ui(class_source)
