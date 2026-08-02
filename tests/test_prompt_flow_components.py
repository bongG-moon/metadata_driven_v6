from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

import pytest

from tools.flow_builder_support import (
    _build_note_node,
    _find_native_component,
    _hydrate_prompt_template,
    build_edge,
)


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "langflow_components" / "shared"
AUTHORING = ROOT / "langflow_components" / "metadata_authoring"
PROMPTS = ROOT / "prompts"


@lru_cache(maxsize=None)
def _component_class(filename: str):
    from lfx.custom.eval import eval_custom_component_code

    return eval_custom_component_code((SHARED / filename).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _authoring_component_class(filename: str):
    from lfx.custom.eval import eval_custom_component_code

    return eval_custom_component_code((AUTHORING / filename).read_text(encoding="utf-8"))


def _message(text: str):
    from lfx.schema.message import Message

    return Message(text=text)


def _data(payload: dict):
    from lfx.schema.data import Data

    return Data(data=payload)


def _canonical_json_sha256(value) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _runtime_context(*, invoke: bool = True, purpose: str = "intent_selection") -> dict:
    variables = {
        "question": "상위 3개를 보여줘",
        "candidate_ids": ["candidate:one", "candidate:two"],
    }
    if purpose.startswith("metadata_") and purpose != "metadata_execute":
        variables["output_schema"] = {
            "type": "object",
            "additionalProperties": False,
            "required": ["status"],
            "properties": {"status": {"const": "complete"}},
        }
    return {
        "contract_version": "prompt.runtime-context.v1",
        "purpose": purpose,
        "invoke": invoke,
        "variables": variables,
    }


def _compose(
    *,
    specialized: str | None = "DOMAIN",
    invoke: bool = True,
    purpose: str = "intent_selection",
):
    component = _component_class("01_prompt_bundle_composer.py")()
    component.common_prompt_message = _message("COMMON")
    if specialized is not None:
        component.specialized_prompt_message = _message(specialized)
    component.runtime_context = _data(
        _runtime_context(invoke=invoke, purpose=purpose)
    )
    return component.build_prompt_bundle().data


def test_prompt_assets_are_external_utf8_and_have_no_manufacturing_literals() -> None:
    expected = {
        "data_analysis/intent_common_ko.md",
        "data_analysis/intent_specialized_ko.md",
        "data_analysis/answer_common_ko.md",
        "data_analysis/answer_specialized_ko.md",
        "metadata_authoring/domain_common_ko.md",
        "metadata_authoring/dataset_common_ko.md",
        "metadata_authoring/main_filter_common_ko.md",
    }
    actual = {path.relative_to(PROMPTS).as_posix() for path in PROMPTS.rglob("*_ko.md")}
    assert actual == expected
    for relative in actual:
        text = (PROMPTS / relative).read_text(encoding="utf-8")
        assert text.strip()
        assert "manufacturing" not in text.lower()


def test_composer_preserves_authority_roles_and_runtime_context_once() -> None:
    payload = _compose()
    assert [(item["role"], item["authority"], item["segment"]) for item in payload["segments"]] == [
        ("system", "system", "common"),
        ("human", "domain_policy", "specialized"),
        ("human", "untrusted_data", "runtime_context"),
    ]
    assert payload["segments"][0]["content"] == "COMMON"
    assert payload["segments"][1]["content"] == "DOMAIN"
    context_text = payload["segments"][2]["content"]
    assert context_text.count("상위 3개를 보여줘") == 1
    assert "COMMON" not in json.dumps(payload["manifest"], ensure_ascii=False)
    assert "DOMAIN" not in json.dumps(payload["manifest"], ensure_ascii=False)


def test_composer_omits_unconfigured_or_connected_empty_specialization() -> None:
    payload = _compose(specialized=None)
    assert payload["specialization_status"] == "not_configured"
    assert [item["segment"] for item in payload["segments"]] == ["common", "runtime_context"]

    component = _component_class("01_prompt_bundle_composer.py")()
    component.common_prompt_message = _message("COMMON")
    component.specialized_prompt_message = _message("")
    component.runtime_context = _data(_runtime_context())
    empty_connected = component.build_prompt_bundle().data
    assert empty_connected["specialization_status"] == "not_configured"
    assert [item["segment"] for item in empty_connected["segments"]] == ["common", "runtime_context"]


def test_composer_rejects_raw_or_secret_bearing_payloads() -> None:
    component = _component_class("01_prompt_bundle_composer.py")()
    component.common_prompt_message = _message("COMMON")
    for variables in ({"rows": [{"value": 1}]}, {"nested": {"api_key": "secret"}}):
        component.runtime_context = _data({**_runtime_context(), "variables": variables})
        with pytest.raises(ValueError):
            component.build_prompt_bundle()


class _FakeModel:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def test_conditional_invoker_calls_once_with_separate_system_and_human_messages() -> None:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    component = _component_class("02_conditional_llm_invoker.py")()
    component.prompt_bundle = _data(_compose())
    model = _FakeModel(AIMessage(content='{"intent_candidate_id":"candidate:one"}'))
    component.language_model = model
    result = component.invoke_once().data

    assert result["status"] == "ok"
    assert result["llm_calls"] == 1
    assert len(model.calls) == 1
    assert [type(message) for message in model.calls[0]] == [SystemMessage, HumanMessage, HumanMessage]
    assert "segments" not in result
    assert "COMMON" not in json.dumps(result, ensure_ascii=False)
    assert "DOMAIN" not in json.dumps(result, ensure_ascii=False)


def test_conditional_invoker_binds_exact_google_metadata_lane_to_json_mime() -> None:
    from langchain_core.messages import AIMessage

    class ChatGoogleGenerativeAI(_FakeModel):
        __module__ = "langchain_google_genai.chat_models"

        def __init__(self, response):
            super().__init__(response)
            self.bind_calls = []

        def bind(self, **kwargs):
            self.bind_calls.append(kwargs)
            return self

    component = _component_class("02_conditional_llm_invoker.py")()
    bundle = _compose(purpose="metadata_domain_draft", specialized=None)
    component.prompt_bundle = _data(bundle)
    model = ChatGoogleGenerativeAI(AIMessage(content='{"status":"complete"}'))
    component.language_model = model

    result = component.invoke_once().data

    assert result["status"] == "ok"
    assert result["llm_calls"] == 1
    assert result["prompt_bundle_sha256"] == bundle["manifest"]["bundle_sha256"]
    assert result["provider_schema_binding"] == "google_native_json_schema"
    assert model.bind_calls == [
        {
            "response_mime_type": "application/json",
            "response_json_schema": component.invoke_once.__globals__[
                "_simplify_google_schema_maps"
            ](
                component.invoke_once.__globals__["_break_google_schema_cycles"](
                    component.invoke_once.__globals__["_google_provider_schema"](
                        component.invoke_once.__globals__["_inline_provider_schema_refs"](
                            _runtime_context(
                                purpose="metadata_domain_draft"
                            )["variables"]["output_schema"]
                        )
                    )
                )
            ),
        }
    ]
    namespace = component.invoke_once.__globals__
    authoritative_schema = _runtime_context(
        purpose="metadata_domain_draft"
    )["variables"]["output_schema"]
    provider_schema = model.bind_calls[0]["response_json_schema"]
    assert namespace["_GOOGLE_SCHEMA_PROJECTION"] == (
        "google_supported_json_schema_subset.v6"
    )
    assert result["schema_binding_evidence"] == {
        "contract_version": "llm.schema-binding.evidence.v1",
        "binding_status": "google_native_json_schema",
        "projection": "google_supported_json_schema_subset.v6",
        "authoritative_schema_sha256": _canonical_json_sha256(
            authoritative_schema
        ),
        "provider_schema_sha256": _canonical_json_sha256(provider_schema),
    }
    assert len(model.calls) == 1


def test_conditional_invoker_rejects_prompt_bundle_sha256_tamper_before_call() -> None:
    from langchain_core.messages import AIMessage

    bundle = _compose(purpose="metadata_domain_draft", specialized=None)
    bundle["manifest"]["bundle_sha256"] = "0" * 64
    component = _component_class("02_conditional_llm_invoker.py")()
    component.prompt_bundle = _data(bundle)
    model = _FakeModel(AIMessage(content='{"status":"complete"}'))
    component.language_model = model

    with pytest.raises(ValueError):
        component.invoke_once()

    assert model.calls == []


def test_authoring_invocation_consumer_rejects_response_sha256_tamper() -> None:
    from lfx.schema.data import Data

    component_cls = _authoring_component_class("00_metadata_authoring_engine.py")
    namespace = component_cls.run_authoring.__globals__
    output_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["status"],
        "properties": {"status": {"const": "complete"}},
    }
    response_text = '{"status":"complete"}'
    invocation = {
        "contract_version": "llm.invocation.v1",
        "purpose": "metadata_domain_draft",
        "status": "ok",
        "llm_calls": 1,
        "prompt_bundle_sha256": "1" * 64,
        "runtime_context_sha256": "2" * 64,
        "provider_schema_binding": "portable_prompt_and_compiler_validation",
        "schema_binding_evidence": {
            "contract_version": "llm.schema-binding.evidence.v1",
            "binding_status": "portable_prompt_and_compiler_validation",
            "projection": "none",
            "authoritative_schema_sha256": namespace["sha256_json"](
                output_schema
            ),
            "provider_schema_sha256": "",
        },
        "response_text": response_text,
        "response_sha256": hashlib.sha256(response_text.encode("utf-8")).hexdigest(),
    }
    component = component_cls()
    component.authoring_invocation_result = Data(data=deepcopy(invocation))
    consume = namespace["_authoring_invocation_draft"]
    arguments = {
        "input_name": "authoring_invocation_result",
        "expected_purpose": "metadata_domain_draft",
        "required": True,
        "expected_output_schema": output_schema,
        "expected_runtime_context_sha256": "2" * 64,
    }

    assert consume(component, **arguments) == {"status": "complete"}

    component.authoring_invocation_result = Data(data=deepcopy(invocation))
    component.authoring_invocation_result.data["response_sha256"] = "0" * 64
    with pytest.raises(namespace["ContractError"]):
        consume(component, **arguments)


def test_conditional_invoker_accepts_real_union_schema_root() -> None:
    component_cls = _component_class("02_conditional_llm_invoker.py")
    runtime_output_schema = component_cls.invoke_once.__globals__["_runtime_output_schema"]
    union_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": {"complete": {"type": "object"}},
        "oneOf": [{"$ref": "#/$defs/complete"}],
    }
    segments = [
        {
            "content": json.dumps(
                {
                    "authority": "untrusted_data",
                    "purpose": "metadata_domain_draft",
                    "variables": {"output_schema": union_schema},
                }
            )
        }
    ]

    assert runtime_output_schema(segments, "metadata_domain_draft") == union_schema


def test_google_provider_projection_collapses_only_dataset_field_allowlist_branches() -> None:
    component_cls = _component_class("02_conditional_llm_invoker.py")
    collapse = component_cls.invoke_once.__globals__[
        "_collapse_google_dataset_card_allowlists"
    ]
    branch = lambda dataset_id, fields: {
        "type": "object",
        "additionalProperties": False,
        "required": ["dataset_id", "fields"],
        "properties": {
            "dataset_id": {"type": "string", "enum": [dataset_id]},
            "fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "enum": fields},
                        "col": {"type": "string", "enum": fields},
                    },
                },
            },
            "default_detail_fields": {
                "type": "array", "items": {"type": "string", "enum": fields}
            },
            "default_detail_columns": {
                "type": "array", "items": {"type": "string", "enum": fields}
            },
        },
    }
    authoritative = {
        "oneOf": [branch("target", ["MCP_NO"]), branch("production", ["DEVICE"])],
    }

    provider_hint = collapse(authoritative)

    assert "oneOf" not in provider_hint
    assert provider_hint["properties"]["dataset_id"]["enum"] == [
        "production", "target"
    ]
    field_properties = provider_hint["properties"]["fields"]["items"]["properties"]
    assert field_properties["id"]["enum"] == ["DEVICE", "MCP_NO"]
    assert field_properties["col"]["enum"] == ["DEVICE", "MCP_NO"]
    assert authoritative["oneOf"][0]["properties"]["fields"]["items"][
        "properties"
    ]["id"]["enum"] == ["MCP_NO"]


def test_google_schema_projection_keeps_shape_and_removes_unsupported_constraints() -> None:
    component_cls = _component_class("02_conditional_llm_invoker.py")
    namespace = component_cls.invoke_once.__globals__
    project = namespace["_google_provider_schema"]
    authoritative = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "oneOf": [
            {
                "type": "object",
                "properties": {
                    "status": {"const": "complete"},
                    "values": {
                        "type": "object",
                        "patternProperties": {
                            "^.{1,32}$": {"type": "string", "minLength": 1}
                        },
                        "additionalProperties": False,
                    },
                    "rows": {
                        "type": "array",
                        "items": {"type": "object", "additionalProperties": True},
                        "minItems": 1,
                        "maxItems": 1024,
                    },
                },
                "required": ["status"],
            }
        ],
    }

    projected = project(authoritative)

    assert "$schema" not in projected
    assert projected["oneOf"][0]["properties"]["status"] == {
        "enum": ["complete"]
    }
    values = projected["oneOf"][0]["properties"]["values"]
    assert "patternProperties" not in values
    assert values["additionalProperties"] == {"type": "string"}
    rows = projected["oneOf"][0]["properties"]["rows"]
    assert rows["minItems"] == 1
    assert "maxItems" not in rows

    simplified = namespace["_simplify_google_schema_maps"](projected)
    assert simplified["oneOf"][0]["properties"]["values"][
        "additionalProperties"
    ] is True
    assert project({"const": True}) == {"type": "boolean"}


def test_google_authoring_choice_projection_keeps_choice_without_first_branch_bias() -> None:
    component_cls = _component_class("02_conditional_llm_invoker.py")
    flatten = component_cls.invoke_once.__globals__["_flatten_google_authoring_choice"]
    proposal = {
        "oneOf": [
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "contract_version": {"enum": ["metadata.authoring.proposal.v1"]},
                    "status": {"enum": ["complete"]},
                    "source_sha256": {"type": "string"},
                    "draft": {"type": "object"},
                },
                "required": ["contract_version", "status", "source_sha256", "draft"],
            },
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "contract_version": {"enum": ["metadata.authoring.proposal.v1"]},
                    "status": {"enum": ["needs_clarification"]},
                    "source_sha256": {"type": "string"},
                    "clarification": {"type": "object"},
                },
                "required": [
                    "contract_version",
                    "status",
                    "source_sha256",
                    "clarification",
                ],
            },
        ]
    }

    provider = flatten(proposal)

    assert "oneOf" not in provider
    assert provider["properties"]["status"]["enum"] == [
        "complete",
        "needs_clarification",
    ]
    assert set(provider["properties"]) == {
        "contract_version",
        "status",
        "source_sha256",
        "draft",
        "clarification",
    }
    assert set(provider["required"]) == {
        "contract_version",
        "status",
        "source_sha256",
        "draft",
        "clarification",
    }
    assert provider["properties"]["draft"]["anyOf"][1] == {"type": "null"}
    assert provider["properties"]["clarification"]["anyOf"][1] == {
        "type": "null"
    }


def test_authoring_choice_normalization_only_removes_unselected_null_branch() -> None:
    component_cls = _component_class("02_conditional_llm_invoker.py")
    normalize = component_cls.invoke_once.__globals__["_normalize_authoring_choice_response"]
    complete = {
        "contract_version": "metadata.authoring.proposal.v1",
        "status": "complete",
        "source_sha256": "a" * 64,
        "draft": {"datasets": {}},
        "clarification": None,
    }
    clarification = {
        "contract_version": "metadata.authoring.proposal.v1",
        "status": "needs_clarification",
        "source_sha256": "b" * 64,
        "draft": None,
        "clarification": {
            "questions": ["어떤 자료를 뜻하나요?"],
            "missing_fields": ["dataset"],
        },
    }

    complete_text, complete_status = normalize(
        json.dumps(complete), "metadata_domain_draft"
    )
    clarification_text, clarification_status = normalize(
        json.dumps(clarification), "metadata_dataset_draft"
    )

    assert complete_status == "removed_unselected_null_branch"
    assert "clarification" not in json.loads(complete_text)
    assert clarification_status == "removed_unselected_null_branch"
    assert "draft" not in json.loads(clarification_text)
    malformed = {**clarification, "draft": {"datasets": {}}}
    unchanged, status = normalize(
        json.dumps(malformed), "metadata_dataset_draft"
    )
    assert json.loads(unchanged) == malformed
    assert status == "not_normalized"


def test_google_schema_projection_breaks_recursive_defs_for_provider_only() -> None:
    component_cls = _component_class("02_conditional_llm_invoker.py")
    namespace = component_cls.invoke_once.__globals__
    authoritative = {
        "type": "object",
        "$defs": {
            "jsonValue": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "array", "items": {"$ref": "#/$defs/jsonValue"}},
                ]
            }
        },
        "properties": {"value": {"$ref": "#/$defs/jsonValue"}},
        "required": ["value"],
    }

    projected = namespace["_break_google_schema_cycles"](
        namespace["_google_provider_schema"](authoritative)
    )

    assert "#/$defs/jsonValue" not in json.dumps(
        projected["$defs"]["jsonValue"], sort_keys=True
    )
    assert authoritative["$defs"]["jsonValue"]["anyOf"][1]["items"] == {
        "$ref": "#/$defs/jsonValue"
    }


def test_google_schema_projection_inlines_nested_local_defs_without_mutating_authority() -> None:
    component_cls = _component_class("02_conditional_llm_invoker.py")
    namespace = component_cls.invoke_once.__globals__
    authoritative = {
        "oneOf": [
            {
                "type": "object",
                "properties": {
                    "draft": {
                        "type": "object",
                        "$defs": {"name": {"type": "string", "minLength": 1}},
                        "properties": {"name": {"$ref": "#/$defs/name"}},
                    }
                },
            }
        ]
    }

    inlined = namespace["_inline_provider_schema_refs"](authoritative)
    projected = namespace["_google_provider_schema"](inlined)

    draft = projected["oneOf"][0]["properties"]["draft"]
    assert "$defs" not in draft
    assert draft["properties"]["name"] == {"type": "string"}
    assert authoritative["oneOf"][0]["properties"]["draft"]["$defs"]


def test_conditional_invoker_fails_closed_before_google_call_when_schema_bind_fails() -> None:
    from langchain_core.messages import AIMessage

    class ChatGoogleGenerativeAI(_FakeModel):
        __module__ = "langchain_google_genai.chat_models"

        def bind(self, **kwargs):
            raise ValueError("unsupported schema")

    component = _component_class("02_conditional_llm_invoker.py")()
    component.prompt_bundle = _data(
        _compose(purpose="metadata_domain_draft", specialized=None)
    )
    model = ChatGoogleGenerativeAI(AIMessage(content='{"status":"complete"}'))
    component.language_model = model

    result = component.invoke_once().data

    assert result["status"] == "error"
    assert result["llm_calls"] == 0
    assert result["provider_schema_binding"] == "provider_native_schema_failed"
    assert model.calls == []


def test_conditional_invoker_skips_without_model_and_never_retries_failure() -> None:
    component = _component_class("02_conditional_llm_invoker.py")()
    component.prompt_bundle = _data(_compose(invoke=False))
    skipped = component.invoke_once().data
    assert skipped["status"] == "skipped"
    assert skipped["llm_calls"] == 0

    component = _component_class("02_conditional_llm_invoker.py")()
    component.prompt_bundle = _data(_compose())
    model = _FakeModel(RuntimeError("provider failure"))
    component.language_model = model
    failed = component.invoke_once().data
    assert failed["status"] == "error"
    assert failed["llm_calls"] == 1
    assert len(model.calls) == 1
    assert "provider failure" not in json.dumps(failed, ensure_ascii=False)

    component = _component_class("02_conditional_llm_invoker.py")()
    component.prompt_bundle = _data(_compose())
    malformed = _FakeModel("JSON 형식이 아닌 단일 응답")
    component.language_model = malformed
    forwarded = component.invoke_once().data
    assert forwarded["status"] == "ok"
    assert forwarded["llm_calls"] == 1
    assert len(malformed.calls) == 1


def test_langflow_1_9_2_prompt_dynamic_port_is_hydrated_and_connectable() -> None:
    import lfx

    index_path = Path(lfx.__file__).resolve().parent / "_assets" / "component_index.json"
    component_index = json.loads(index_path.read_text(encoding="utf-8"))
    config = _find_native_component(component_index, "Prompt Template")
    config["template"]["template"]["value"] = "도메인 정책: {{domain_prompt_text}}"
    config["template"]["use_double_brackets"]["value"] = True
    _hydrate_prompt_template(config, node_id="specialized_prompt", expected_variables=["domain_prompt_text"])
    assert config["custom_fields"]["template"] == ["domain_prompt_text"]
    assert config["template"]["template"]["type"] == "mustache"
    assert config["template"]["domain_prompt_text"]["input_types"]

    source = {
        "id": "source",
        "data": {
            "type": "ContextBuilder",
            "node": {"outputs": [{"name": "specialized", "types": ["Message"]}]},
        },
    }
    target = {"id": "target", "data": {"type": "Prompt", "node": config}}
    edge = build_edge(
        {
            "source": "source",
            "source_output": "specialized",
            "target": "target",
            "target_input": "domain_prompt_text",
        },
        {"source": source, "target": target},
    )
    assert edge["data"]["targetHandle"]["fieldName"] == "domain_prompt_text"


def test_sticky_note_uses_langflow_1_9_2_note_node_shape() -> None:
    note = _build_note_node(
        {
            "id": "guide_note",
            "title": "사용 안내",
            "markdown": "## 사용 안내\n\n한국어 설명",
            "position": {"x": 10, "y": 20},
            "width": 360,
            "height": 240,
            "color": "blue",
        }
    )
    assert note["type"] == "noteNode"
    assert note["data"]["type"] == "note"
    assert note["data"]["node"]["lf_version"] == "1.9.2"
    assert note["position"] == note["positionAbsolute"]
    assert note["style"] == {"height": 240.0, "width": 360.0}
