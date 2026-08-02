# -*- coding: utf-8 -*-
"""LLM 호출 여부를 결정론적으로 지키는 standalone Langflow component."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, HandleInput, Output
from lfx.schema.data import Data


_BUNDLE_VERSION = "prompt.bundle.v1"
_MANIFEST_VERSION = "prompt.manifest.v1"
_RESULT_VERSION = "llm.invocation.v1"
_JSON_RESPONSE_PURPOSES = {
    "metadata_domain_draft",
    "metadata_dataset_draft",
    "metadata_main_filter_draft",
    "metadata_domain_annotation",
}
_DEFAULT_MAX_RESPONSE_BYTES = 32 * 1024
_MAX_RESPONSE_BYTES_BY_PURPOSE = {
    "metadata_domain_draft": 192 * 1024,
    "metadata_dataset_draft": 128 * 1024,
    "metadata_main_filter_draft": 128 * 1024,
}


class _ProviderSchemaBindingError(RuntimeError):
    """Raised before invocation when an exact provider cannot bind the schema."""


_GOOGLE_SCHEMA_KEYS = {
    "$id",
    "$defs",
    "$ref",
    "$anchor",
    "type",
    "format",
    "title",
    "description",
    "enum",
    "items",
    "prefixItems",
    "minItems",
    "minimum",
    "maximum",
    "anyOf",
    "oneOf",
    "properties",
    "additionalProperties",
    "required",
}
_GOOGLE_SCHEMA_PROJECTION = "google_supported_json_schema_subset.v6"


def _bounded_json_value_schema() -> dict[str, Any]:
    scalar = {"type": ["string", "number", "integer", "boolean", "null"]}
    return {
        "anyOf": [
            scalar,
            {"type": "array", "items": scalar, "maxItems": 128},
            {"type": "object", "additionalProperties": scalar},
        ]
    }


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _payload(value: Any) -> dict[str, Any]:
    raw = getattr(value, "data", value)
    if not isinstance(raw, dict):
        raise ValueError("프롬프트 묶음은 Data 객체여야 합니다.")
    return raw


def _response_text(value: Any) -> str:
    content = getattr(value, "content", None)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            elif isinstance(getattr(item, "text", None), str):
                parts.append(item.text)
        if parts:
            return "\n".join(part for part in parts if part).strip()
    text = getattr(value, "text", None)
    if isinstance(text, str):
        return text.strip()
    if isinstance(value, str):
        return value.strip()
    return ""


def _provider_error_diagnostics(exc: Exception) -> dict[str, str]:
    """Return bounded categorical provider facts without exception messages."""

    facts = {"provider_error_type": type(exc).__name__[:80]}
    current: BaseException | None = exc
    for _ in range(4):
        if current is None:
            break
        for source_name, output_name in (
            ("status", "provider_error_status"),
            ("code", "provider_error_code"),
            ("status_code", "provider_error_code"),
        ):
            raw = getattr(current, source_name, None)
            value = str(raw or "")[:80]
            if value and all(character.isalnum() or character in "._-" for character in value):
                facts.setdefault(output_name, value)
        current = current.__cause__ or current.__context__
    return facts


def _runtime_output_schema(segments: list[dict[str, str]], purpose: str) -> dict[str, Any] | None:
    if purpose not in _JSON_RESPONSE_PURPOSES or not segments:
        return None
    try:
        context = json.loads(segments[-1]["content"])
    except (KeyError, TypeError, json.JSONDecodeError):
        return None
    if not isinstance(context, dict) or set(context) != {"authority", "purpose", "variables"}:
        return None
    if context.get("authority") != "untrusted_data" or context.get("purpose") != purpose:
        return None
    variables = context.get("variables")
    schema = variables.get("output_schema") if isinstance(variables, dict) else None
    if not isinstance(schema, dict):
        return None
    # A valid JSON Schema root may be a union (`oneOf`/`anyOf`) and therefore
    # does not have to declare a top-level `type`.  Requiring `type` silently
    # discarded the real metadata-authoring proposal schemas.
    structural_keys = {
        "$ref", "type", "properties", "oneOf", "anyOf", "allOf", "enum", "const"
    }
    if not structural_keys.intersection(schema):
        return None
    if len(_canonical_bytes(schema)) > 256 * 1024:
        return None
    return schema


def _google_provider_schema(value: Any) -> Any:
    """Project the authoritative contract to Google's documented subset.

    The full schema remains the local compiler authority.  Unsupported
    constraints are removed only from the provider hint, and `const` is
    represented as a one-item enum.  A single `patternProperties` rule becomes
    the schema-valued `additionalProperties` form supported by Gemini.

    ``maxItems`` remains authoritative in the local schema but is deliberately
    omitted from the provider hint. Gemini expands that bound into its output
    grammar; a large bound combined with an object item schema can make an
    otherwise small Dataset authoring schema fail with INVALID_ARGUMENT. The
    deterministic post-validator still enforces the exact array limit.
    """

    if isinstance(value, list):
        return [_google_provider_schema(item) for item in value]
    if not isinstance(value, dict):
        return value

    projected: dict[str, Any] = {}
    for key, child in value.items():
        if key == "const":
            if isinstance(child, bool):
                projected["type"] = "boolean"
            elif child is None:
                projected["type"] = "null"
            elif isinstance(child, (str, int, float)):
                projected["enum"] = [_google_provider_schema(child)]
            continue
        if key in {"properties", "$defs"} and isinstance(child, dict):
            projected[key] = {
                str(name): _google_provider_schema(schema)
                for name, schema in child.items()
            }
            continue
        if key == "patternProperties" and isinstance(child, dict) and child:
            candidates = [_google_provider_schema(schema) for schema in child.values()]
            projected["additionalProperties"] = (
                candidates[0] if len(candidates) == 1 else {"anyOf": candidates}
            )
            continue
        if (
            key == "additionalProperties"
            and "additionalProperties" in projected
            and child is False
        ):
            # The projected pattern schema is more informative than the
            # original closed-map marker, which Gemini cannot combine with
            # unsupported `patternProperties`.
            continue
        if key not in _GOOGLE_SCHEMA_KEYS:
            continue
        projected[key] = _google_provider_schema(child)
    return projected


def _inline_provider_schema_refs(schema: dict[str, Any]) -> dict[str, Any]:
    """Inline local `$defs` before embedding schemas into provider unions.

    Authoring builds a proposal schema by embedding a self-contained fragment
    schema under `draft`.  Its `#/$defs/...` references are local by design,
    while Gemini resolves them against the outer request root.  Inline them in
    the provider-only copy and bound recursive tails; the authoritative schema
    and local compiler validation remain unchanged.
    """

    def visit(value: Any, definitions: dict[str, Any], stack: tuple[str, ...]) -> Any:
        if isinstance(value, list):
            return [visit(item, definitions, stack) for item in value]
        if not isinstance(value, dict):
            return value
        local_definitions = (
            value.get("$defs") if isinstance(value.get("$defs"), dict) else definitions
        )
        raw_ref = value.get("$ref")
        if isinstance(raw_ref, str) and raw_ref.startswith("#/$defs/"):
            name = raw_ref.removeprefix("#/$defs/")
            target = local_definitions.get(name)
            if not isinstance(target, dict):
                raise _ProviderSchemaBindingError("provider_schema_ref_undefined")
            if name in stack:
                return _bounded_json_value_schema()
            resolved = visit(target, local_definitions, (*stack, name))
            siblings = {
                key: visit(child, local_definitions, stack)
                for key, child in value.items()
                if key not in {"$ref", "$defs"}
            }
            if isinstance(resolved, dict):
                return {**resolved, **siblings}
            return siblings
        return {
            key: visit(child, local_definitions, stack)
            for key, child in value.items()
            if key != "$defs"
        }

    inlined = visit(schema, {}, ())
    if not isinstance(inlined, dict):
        raise _ProviderSchemaBindingError("provider_schema_inline_invalid")
    return inlined


def _schema_definition_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        raw_ref = value.get("$ref")
        if isinstance(raw_ref, str) and raw_ref.startswith("#/$defs/"):
            refs.add(raw_ref.removeprefix("#/$defs/"))
        for child in value.values():
            refs.update(_schema_definition_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_schema_definition_refs(child))
    return refs


def _break_google_schema_cycles(schema: dict[str, Any]) -> dict[str, Any]:
    """Replace cyclic provider-only definitions with a bounded JSON value hint."""

    definitions = schema.get("$defs")
    if not isinstance(definitions, dict):
        return schema
    graph = {
        str(name): _schema_definition_refs(definition) & set(definitions)
        for name, definition in definitions.items()
    }

    def reaches(start: str, current: str, seen: set[str]) -> bool:
        for target in graph.get(current, set()):
            if target == start:
                return True
            if target not in seen and reaches(start, target, seen | {target}):
                return True
        return False

    cyclic = {
        name for name in graph if reaches(name, name, {name})
    }
    if not cyclic:
        return schema
    bounded_json_value = _bounded_json_value_schema()
    for name in sorted(cyclic):
        definitions[name] = json.loads(json.dumps(bounded_json_value))
    return schema


def _simplify_google_schema_maps(value: Any) -> Any:
    """Bound provider complexity for dynamic maps; local validation stays exact."""

    if isinstance(value, list):
        return [_simplify_google_schema_maps(item) for item in value]
    if not isinstance(value, dict):
        return value
    simplified: dict[str, Any] = {}
    for key, child in value.items():
        if key == "maxItems":
            # Cycle breaking can introduce a fresh bounded array after the
            # first projection pass. Keep every provider-only array unbounded;
            # the authoritative local schema remains exact.
            continue
        if key == "additionalProperties" and isinstance(child, dict):
            simplified[key] = True
        else:
            simplified[key] = _simplify_google_schema_maps(child)
    return simplified


def _flatten_google_authoring_choice(schema: dict[str, Any]) -> dict[str, Any]:
    """Remove provider first-branch bias from the authoring proposal union.

    The authoritative contract is an exact ``oneOf`` between ``complete`` and
    ``needs_clarification``. Gemini can over-select the first branch when that
    union is used directly as an output grammar, even when the prose explicitly
    says that facts are missing. The provider-only hint therefore exposes one
    object with the common fields required and both payloads optional. The
    prompt chooses the status; the unchanged local schema subsequently enforces
    the exact branch and rejects mixed or partial proposals.
    """

    branches = schema.get("oneOf")
    if not isinstance(branches, list) or len(branches) != 2:
        return schema
    if any(
        not isinstance(branch, dict)
        or branch.get("type") != "object"
        or not isinstance(branch.get("properties"), dict)
        or not isinstance(branch.get("required"), list)
        for branch in branches
    ):
        return schema
    statuses: list[str] = []
    for branch in branches:
        status_schema = branch["properties"].get("status")
        values = status_schema.get("enum") if isinstance(status_schema, dict) else None
        if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], str):
            return schema
        statuses.append(values[0])
    if set(statuses) != {"complete", "needs_clarification"}:
        return schema

    merged_properties: dict[str, Any] = {}
    required = set(branches[0]["required"])
    for branch in branches:
        required.intersection_update(branch["required"])
        for key, value in branch["properties"].items():
            if key == "status":
                continue
            existing = merged_properties.get(key)
            if existing is None:
                merged_properties[key] = value
            elif existing != value:
                return schema
    for branch_payload in ("draft", "clarification"):
        payload_schema = merged_properties.get(branch_payload)
        if not isinstance(payload_schema, dict):
            return schema
        merged_properties[branch_payload] = {
            "anyOf": [payload_schema, {"type": "null"}],
        }
    merged_properties["status"] = {
        "type": "string",
        "enum": ["complete", "needs_clarification"],
    }
    root_annotations = {
        key: value
        for key, value in schema.items()
        if key in {"$id", "title", "description"}
    }
    return {
        **root_annotations,
        "type": "object",
        "additionalProperties": False,
        "properties": merged_properties,
        "required": sorted(required | {"draft", "clarification"}),
    }


def _collapse_google_dataset_card_allowlists(value: Any) -> Any:
    """Collapse dataset-specific card branches in the provider-only hint.

    The authoritative schema keeps the exact dataset→field relationship and is
    always enforced locally. Repeating the complete Dataset card ten or more
    times can exceed Gemini's output-grammar complexity limit, so the Google
    hint uses the union of already-approved IDs while retaining closed object
    shapes. This does not invent or broaden the compiler contract.
    """

    if isinstance(value, list):
        return [_collapse_google_dataset_card_allowlists(item) for item in value]
    if not isinstance(value, dict):
        return value

    branches = value.get("oneOf")
    if isinstance(branches, list) and 1 <= len(branches) <= 128:
        signatures = []
        for branch in branches:
            properties = branch.get("properties") if isinstance(branch, dict) else None
            dataset_schema = properties.get("dataset_id") if isinstance(properties, dict) else None
            fields_schema = properties.get("fields") if isinstance(properties, dict) else None
            dataset_values = dataset_schema.get("enum") if isinstance(dataset_schema, dict) else None
            field_item = fields_schema.get("items") if isinstance(fields_schema, dict) else None
            field_properties = field_item.get("properties") if isinstance(field_item, dict) else None
            id_schema = field_properties.get("id") if isinstance(field_properties, dict) else None
            col_schema = field_properties.get("col") if isinstance(field_properties, dict) else None
            id_values = id_schema.get("enum") if isinstance(id_schema, dict) else None
            col_values = col_schema.get("enum") if isinstance(col_schema, dict) else None
            if (
                not isinstance(properties, dict)
                or not isinstance(dataset_values, list)
                or len(dataset_values) != 1
                or not isinstance(dataset_values[0], str)
                or not isinstance(id_values, list)
                or not isinstance(col_values, list)
                or not id_values
                or id_values != col_values
                or any(not isinstance(item, str) for item in id_values)
            ):
                signatures = []
                break
            signatures.append((branch, dataset_values[0], id_values))
        if signatures:
            collapsed = _collapse_google_dataset_card_allowlists(
                deepcopy(signatures[0][0])
            )
            collapsed_properties = collapsed["properties"]
            approved_datasets = sorted({dataset_id for _, dataset_id, _ in signatures})
            approved_fields = sorted(
                {field_id for _, _, field_ids in signatures for field_id in field_ids}
            )
            collapsed_properties["dataset_id"]["enum"] = approved_datasets
            collapsed_field_properties = collapsed_properties["fields"]["items"]["properties"]
            collapsed_field_properties["id"]["enum"] = approved_fields
            collapsed_field_properties["col"]["enum"] = approved_fields
            for detail_key in ("default_detail_fields", "default_detail_columns"):
                detail_schema = collapsed_properties.get(detail_key)
                if isinstance(detail_schema, dict) and isinstance(detail_schema.get("items"), dict):
                    detail_schema["items"]["enum"] = approved_fields
            return collapsed

    return {
        key: _collapse_google_dataset_card_allowlists(child)
        for key, child in value.items()
    }


def _normalize_authoring_choice_response(
    response_text: str,
    purpose: str,
) -> tuple[str, str]:
    """Remove only the provider-required null branch placeholder.

    No candidate content is created, inferred, or repaired here. If the chosen
    branch payload is absent, null, mixed with the other branch, or otherwise
    malformed, the original text is left intact so the authoritative compiler
    rejects it.
    """

    if purpose not in {
        "metadata_domain_draft",
        "metadata_dataset_draft",
        "metadata_main_filter_draft",
    }:
        return response_text, "not_required"
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError:
        return response_text, "not_json"
    if not isinstance(payload, dict):
        return response_text, "not_object"
    status = payload.get("status")
    if (
        status == "complete"
        and isinstance(payload.get("draft"), dict)
        and payload.get("clarification") is None
        and "clarification" in payload
    ):
        payload.pop("clarification")
    elif (
        status == "needs_clarification"
        and isinstance(payload.get("clarification"), dict)
        and payload.get("draft") is None
        and "draft" in payload
    ):
        payload.pop("draft")
    else:
        return response_text, "not_normalized"
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ),
        "removed_unselected_null_branch",
    )


def _json_response_model(
    model: Any,
    purpose: str,
    output_schema: dict[str, Any] | None,
) -> tuple[Any, dict[str, Any]]:
    """Enable provider-native JSON syntax without adding a repair call.

    The compiler remains the schema authority.  This binding only prevents
    JSON framing errors on the exact Google adapter; other model adapters keep
    the same portable prompt-and-validate path.
    """

    if purpose not in _JSON_RESPONSE_PURPOSES:
        return model, {
            "binding_status": "not_required",
            "projection": "none",
            "authoritative_schema_sha256": "",
            "provider_schema_sha256": "",
        }
    if output_schema is None:
        raise _ProviderSchemaBindingError("runtime_output_schema_missing")
    authoritative_schema_sha256 = _sha256(output_schema)
    model_type = type(model)
    google_adapter = any(
        str(getattr(candidate, "__module__", "") or "").casefold()
        == "langchain_google_genai.chat_models"
        and str(getattr(candidate, "__name__", "") or "").casefold()
        == "chatgooglegenerativeai"
        for candidate in getattr(model_type, "__mro__", ())
    )
    if not google_adapter:
        return model, {
            "binding_status": "portable_prompt_and_compiler_validation",
            "projection": "none",
            "authoritative_schema_sha256": authoritative_schema_sha256,
            "provider_schema_sha256": "",
        }
    if not callable(getattr(model, "bind", None)):
        raise _ProviderSchemaBindingError("google_schema_bind_unavailable")
    provider_schema = _simplify_google_schema_maps(
        _collapse_google_dataset_card_allowlists(
            _flatten_google_authoring_choice(
                _break_google_schema_cycles(
                    _google_provider_schema(_inline_provider_schema_refs(output_schema))
                )
            )
        )
    )
    provider_schema_sha256 = _sha256(provider_schema)
    try:
        runner = model.bind(
            response_mime_type="application/json",
            response_json_schema=provider_schema,
        )
    except (AttributeError, NotImplementedError, TypeError, ValueError) as exc:
        raise _ProviderSchemaBindingError("google_schema_bind_failed") from exc
    if runner is None or not callable(getattr(runner, "invoke", None)):
        raise _ProviderSchemaBindingError("google_schema_bound_runner_invalid")
    return runner, {
        "binding_status": "google_native_json_schema",
        "projection": _GOOGLE_SCHEMA_PROJECTION,
        "authoritative_schema_sha256": authoritative_schema_sha256,
        "provider_schema_sha256": provider_schema_sha256,
    }


def _validated_segments(bundle: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    if bundle.get("contract_version") != _BUNDLE_VERSION:
        raise ValueError("프롬프트 묶음 계약 버전이 prompt.bundle.v1이 아닙니다.")
    manifest = bundle.get("manifest")
    if not isinstance(manifest, dict) or manifest.get("contract_version") != _MANIFEST_VERSION:
        raise ValueError("프롬프트 manifest 계약이 올바르지 않습니다.")
    segments = bundle.get("segments")
    if not isinstance(segments, list) or len(segments) not in {2, 3}:
        raise ValueError("프롬프트 메시지는 공통/컨텍스트 또는 공통/특화/컨텍스트 순서여야 합니다.")
    expected = [
        ("system", "system", "common"),
        *(([("human", "domain_policy", "specialized")]) if len(segments) == 3 else []),
        ("human", "untrusted_data", "runtime_context"),
    ]
    normalized: list[dict[str, str]] = []
    for index, (segment, signature) in enumerate(zip(segments, expected, strict=True)):
        if not isinstance(segment, dict):
            raise ValueError(f"프롬프트 메시지 {index}가 객체가 아닙니다.")
        role, authority, name = signature
        if (segment.get("role"), segment.get("authority"), segment.get("segment")) != signature:
            raise ValueError(f"프롬프트 메시지 {index}의 역할 또는 권한 순서가 올바르지 않습니다.")
        content = segment.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"프롬프트 메시지 {index}의 내용이 비어 있습니다.")
        normalized.append({"role": role, "authority": authority, "segment": name, "content": content})

    expected_status = "configured" if len(normalized) == 3 else "not_configured"
    if bundle.get("specialization_status") != expected_status:
        raise ValueError("특화 프롬프트 상태와 메시지 구성이 일치하지 않습니다.")
    if manifest.get("segment_count") != len(normalized):
        raise ValueError("프롬프트 manifest의 메시지 수가 일치하지 않습니다.")
    common = normalized[0]["content"]
    specialized = normalized[1]["content"] if len(normalized) == 3 else None
    context = normalized[-1]["content"]
    if manifest.get("common_sha256") != _text_sha256(common):
        raise ValueError("공통 프롬프트 hash가 일치하지 않습니다.")
    expected_specialized_hash = _text_sha256(specialized) if specialized is not None else ""
    if manifest.get("specialized_sha256") != expected_specialized_hash:
        raise ValueError("특화 프롬프트 hash가 일치하지 않습니다.")
    if manifest.get("runtime_context_sha256") != _text_sha256(context):
        raise ValueError("런타임 컨텍스트 hash가 일치하지 않습니다.")
    projection = {
        "contract_version": bundle.get("contract_version"),
        "purpose": bundle.get("purpose"),
        "invoke": bundle.get("invoke"),
        "specialization_status": bundle.get("specialization_status"),
        "segments": normalized,
    }
    if manifest.get("bundle_sha256") != _sha256(projection):
        raise ValueError("프롬프트 묶음 hash가 일치하지 않습니다.")
    if manifest.get("byte_length") != len(_canonical_bytes(projection)):
        raise ValueError("프롬프트 묶음 byte 길이가 일치하지 않습니다.")
    if not isinstance(bundle.get("invoke"), bool):
        raise ValueError("프롬프트 묶음의 invoke는 boolean이어야 합니다.")
    return normalized, manifest


class ConditionalLLMInvoker(Component):
    display_name = "조건부 LLM 단일 호출"
    description = "호출 플래그가 참일 때만 권한별 메시지를 한 번 호출하며 자동 재시도는 하지 않습니다."
    icon = "bot"
    metadata = {"logical_stage": "conditional_llm_invocation", "automatic_retry_count": 0}

    inputs = [
        DataInput(name="prompt_bundle", display_name="권한 분리 프롬프트 묶음", required=True),
        HandleInput(name="language_model", display_name="언어 모델", input_types=["LanguageModel"], required=False),
    ]
    outputs = [
        Output(name="invocation_result", display_name="LLM 호출 결과", method="invoke_once", types=["Data"])
    ]

    def invoke_once(self) -> Data:
        bundle = _payload(getattr(self, "prompt_bundle", None))
        segments, manifest = _validated_segments(bundle)
        purpose = str(bundle.get("purpose") or "")
        base = {
            "contract_version": _RESULT_VERSION,
            "purpose": purpose,
            "prompt_bundle_sha256": str(manifest["bundle_sha256"]),
            "runtime_context_sha256": str(
                manifest["runtime_context_sha256"]
            ),
            "specialization_status": str(bundle.get("specialization_status")),
        }
        if bundle["invoke"] is False:
            result = {**base, "status": "skipped", "llm_calls": 0, "response_text": "", "response_sha256": ""}
            self.status = f"{purpose}: LLM 호출 생략"
            return Data(data=result)

        model = getattr(self, "language_model", None)
        if model is None or not callable(getattr(model, "invoke", None)):
            result = {
                **base,
                "status": "error",
                "llm_calls": 0,
                "response_text": "",
                "response_sha256": "",
                "error": {"code": "llm_model_missing", "message": "호출 가능한 언어 모델이 연결되지 않았습니다."},
            }
            self.status = f"{purpose}: 언어 모델 미연결"
            return Data(data=result)

        messages = []
        for segment in segments:
            if segment["role"] == "system":
                messages.append(SystemMessage(content=segment["content"]))
            else:
                messages.append(HumanMessage(content=segment["content"]))
        schema_binding = "not_required"
        schema_binding_evidence = {
            "contract_version": "llm.schema-binding.evidence.v1",
            "binding_status": schema_binding,
            "projection": "none",
            "authoritative_schema_sha256": "",
            "provider_schema_sha256": "",
        }
        llm_calls = 0
        try:
            output_schema = _runtime_output_schema(segments, purpose)
            runner, binding = _json_response_model(model, purpose, output_schema)
            schema_binding = str(binding["binding_status"])
            schema_binding_evidence = {
                "contract_version": "llm.schema-binding.evidence.v1",
                **binding,
            }
            llm_calls = 1
            raw_response = runner.invoke(messages)
            response_text = _response_text(raw_response)
            if not response_text:
                raise ValueError("LLM 응답 본문이 비어 있습니다.")
            response_text, envelope_normalization = _normalize_authoring_choice_response(
                response_text,
                purpose,
            )
            response_limit = int(_MAX_RESPONSE_BYTES_BY_PURPOSE.get(purpose, _DEFAULT_MAX_RESPONSE_BYTES))
            if len(response_text.encode("utf-8")) > response_limit:
                raise ValueError(f"LLM 응답이 {response_limit} byte 제한을 초과했습니다.")
            result = {
                **base,
                "status": "ok",
                "llm_calls": 1,
                "provider_schema_binding": schema_binding,
                "schema_binding_evidence": schema_binding_evidence,
                "response_envelope_normalization": envelope_normalization,
                "response_text": response_text,
                "response_sha256": _text_sha256(response_text),
            }
            self.status = f"{purpose}: LLM 1회 호출 완료"
            return Data(data=result)
        except Exception as exc:
            if isinstance(exc, _ProviderSchemaBindingError):
                schema_binding = "provider_native_schema_failed"
                schema_binding_evidence = {
                    **schema_binding_evidence,
                    "binding_status": schema_binding,
                }
            result = {
                **base,
                "status": "error",
                "llm_calls": llm_calls,
                "provider_schema_binding": schema_binding,
                "schema_binding_evidence": schema_binding_evidence,
                "response_text": "",
                "response_sha256": "",
                "error": {
                    "code": "llm_invocation_failed",
                    "message": "언어 모델 호출 또는 응답 검증에 실패했습니다.",
                    **_provider_error_diagnostics(exc),
                },
            }
            self.status = f"{purpose}: LLM 호출 실패"
            return Data(data=result)
