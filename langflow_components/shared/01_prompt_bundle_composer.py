# -*- coding: utf-8 -*-
"""권한이 분리된 LLM 메시지 묶음을 만드는 standalone Langflow component."""
from __future__ import annotations

import hashlib
import json
import math
import re
from copy import deepcopy
from typing import Any

from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, MessageInput, Output
from lfx.schema.data import Data


_CONTRACT_VERSION = "prompt.bundle.v1"
_CONTEXT_VERSION = "prompt.runtime-context.v1"
_MANIFEST_VERSION = "prompt.manifest.v1"
_PURPOSES = {
    "intent_selection",
    "answer_narrative",
    "metadata_domain_draft",
    "metadata_domain_annotation",
    "metadata_dataset_draft",
    "metadata_main_filter_draft",
    "metadata_domain_policy",
    "metadata_execute",
}
_SENSITIVE_KEY = re.compile(
    r"(?:^|_)(?:api_?key|secret|token|password|credential|authorization|connection_?string|mongo_?uri)(?:$|_)",
    re.IGNORECASE,
)
_RAW_SOURCE_KEYS = {
    "binary",
    "csv",
    "dataframe",
    "file_bytes",
    "raw_rows",
    "raw_source",
    "records",
    "rows",
    "source_payload",
}
_COMMON_LIMIT = 12 * 1024
_SPECIALIZED_LIMIT = 8 * 1024
_CONTEXT_LIMIT_BY_PURPOSE = {
    "intent_selection": 32 * 1024,
    "answer_narrative": 16 * 1024,
    "metadata_domain_draft": 196 * 1024,
    "metadata_domain_annotation": 196 * 1024,
    "metadata_dataset_draft": 196 * 1024,
    "metadata_main_filter_draft": 196 * 1024,
    "metadata_domain_policy": 32 * 1024,
    "metadata_execute": 4 * 1024,
}
_BUNDLE_LIMIT = 216 * 1024
_QUERY_MARKER = re.compile(
    r"(?im)^[ \t]*(?:query_template|sql_template|oracle_sql|datalake_sql)[ \t]*:[ \t]*(?:\n|$)"
)
_QUERY_BLOCK_END = re.compile(
    r"(?im)^[ \t]*(?:filter_mappings|required_params|required_param_mappings|"
    r"standard_column_aliases|default_detail_columns|metric_semantics|selection_criteria)"
    r"[ \t]*(?:[:=]|(?:은|는)\b)"
)


def _redact_query_templates(value: str) -> str:
    """Remove executable SQL from the provider projection only."""

    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    markers = list(_QUERY_MARKER.finditer(text))
    if not markers:
        return text
    pieces: list[str] = []
    cursor = 0
    for index, marker in enumerate(markers):
        next_marker_start = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        boundary = _QUERY_BLOCK_END.search(text, marker.end(), next_marker_start)
        query_end = boundary.start() if boundary else next_marker_start
        pieces.append(text[cursor:marker.end()])
        pieces.append("[SQL 원문은 결정론적 등록 컴파일러에서 별도 보존 및 검증됨]\n\n")
        cursor = query_end
    pieces.append(text[cursor:])
    return "".join(pieces)


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_value(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(child) for child in value]
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise ValueError("런타임 컨텍스트에는 NaN 또는 Infinity를 사용할 수 없습니다.")
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ValueError(f"런타임 컨텍스트에 JSON이 아닌 값이 있습니다: {type(value).__name__}")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _json_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _message_text(value: Any, *, label: str, required: bool) -> str | None:
    if value is None:
        if required:
            raise ValueError(f"{label} 입력이 연결되지 않았습니다.")
        return None
    # An optional specialization may be physically wired while the active
    # domain has no registered policy. Omit it instead of creating an empty
    # HumanMessage or spending tokens on a placeholder wrapper.
    if not required and not str(getattr(value, "text", value) or "").strip():
        return None
    text = str(getattr(value, "text", value) or "").strip()
    if not text:
        raise ValueError(f"{label} 입력이 연결되었지만 내용이 비어 있습니다.")
    return text


def _data_payload(value: Any) -> dict[str, Any]:
    raw = getattr(value, "data", value)
    if not isinstance(raw, dict):
        raise ValueError("런타임 컨텍스트는 Data 객체여야 합니다.")
    return _json_value(raw)


def _reject_disallowed_payload(value: Any, *, path: str = "variables") -> None:
    if isinstance(value, dict):
        for raw_key, child in value.items():
            key = str(raw_key).strip().lower()
            next_path = f"{path}.{raw_key}"
            if _SENSITIVE_KEY.search(key):
                raise ValueError(f"런타임 컨텍스트에 비밀값 필드가 포함되어 있습니다: {next_path}")
            if key in _RAW_SOURCE_KEYS:
                raise ValueError(f"런타임 컨텍스트에 원본 데이터 payload가 포함되어 있습니다: {next_path}")
            _reject_disallowed_payload(child, path=next_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_disallowed_payload(child, path=f"{path}[{index}]")


class PromptBundleComposer(Component):
    display_name = "권한 분리 프롬프트 묶음 구성"
    description = "공통 규칙, 선택적 도메인 규칙, 신뢰하지 않는 런타임 데이터를 서로 다른 메시지로 묶습니다."
    icon = "messages-square"
    metadata = {"logical_stage": "prompt_composition", "automatic_retry_count": 0}

    inputs = [
        MessageInput(name="common_prompt_message", display_name="공통 프롬프트 메시지", required=True),
        MessageInput(
            name="specialized_prompt_message",
            display_name="특화 프롬프트 메시지(선택)",
            required=False,
        ),
        DataInput(name="runtime_context", display_name="런타임 컨텍스트", required=True),
    ]
    outputs = [
        Output(name="prompt_bundle", display_name="권한 분리 프롬프트 묶음", method="build_prompt_bundle", types=["Data"])
    ]

    def build_prompt_bundle(self) -> Data:
        common = _message_text(
            getattr(self, "common_prompt_message", None),
            label="공통 프롬프트 메시지",
            required=True,
        )
        specialized = _message_text(
            getattr(self, "specialized_prompt_message", None),
            label="특화 프롬프트 메시지",
            required=False,
        )
        context = _data_payload(getattr(self, "runtime_context", None))
        if set(context) != {"contract_version", "purpose", "invoke", "variables"}:
            raise ValueError(
                "런타임 컨텍스트는 contract_version, purpose, invoke, variables만 포함해야 합니다."
            )
        if context.get("contract_version") != _CONTEXT_VERSION:
            raise ValueError("런타임 컨텍스트 계약 버전이 prompt.runtime-context.v1이 아닙니다.")
        purpose = str(context.get("purpose") or "")
        if purpose not in _PURPOSES:
            raise ValueError(f"지원하지 않는 프롬프트 목적입니다: {purpose or '(빈 값)'}")
        if not isinstance(context.get("invoke"), bool):
            raise ValueError("런타임 컨텍스트의 invoke는 boolean이어야 합니다.")
        variables = deepcopy(context.get("variables"))
        if not isinstance(variables, dict):
            raise ValueError("런타임 컨텍스트의 variables는 객체여야 합니다.")
        if purpose == "metadata_dataset_draft" and isinstance(variables.get("source_text"), str):
            variables["source_text"] = _redact_query_templates(variables["source_text"])
        _reject_disallowed_payload(variables)

        common_bytes = len(common.encode("utf-8"))
        specialized_bytes = len(specialized.encode("utf-8")) if specialized is not None else 0
        context_envelope = {
            "authority": "untrusted_data",
            "purpose": purpose,
            "variables": variables,
        }
        context_text = _canonical_bytes(context_envelope).decode("utf-8")
        context_bytes = len(context_text.encode("utf-8"))
        if common_bytes > _COMMON_LIMIT:
            raise ValueError("공통 프롬프트가 12 KiB 제한을 초과했습니다.")
        if specialized_bytes > _SPECIALIZED_LIMIT:
            raise ValueError("특화 프롬프트가 8 KiB 제한을 초과했습니다.")
        context_limit = _CONTEXT_LIMIT_BY_PURPOSE[purpose]
        if context_bytes > context_limit:
            raise ValueError(f"런타임 컨텍스트가 목적별 {context_limit // 1024} KiB 제한을 초과했습니다.")

        segments: list[dict[str, str]] = [
            {"role": "system", "authority": "system", "segment": "common", "content": common}
        ]
        if specialized is not None:
            segments.append(
                {
                    "role": "human",
                    "authority": "domain_policy",
                    "segment": "specialized",
                    "content": specialized,
                }
            )
        segments.append(
            {
                "role": "human",
                "authority": "untrusted_data",
                "segment": "runtime_context",
                "content": context_text,
            }
        )
        specialization_status = "configured" if specialized is not None else "not_configured"
        hash_projection = {
            "contract_version": _CONTRACT_VERSION,
            "purpose": purpose,
            "invoke": context["invoke"],
            "specialization_status": specialization_status,
            "segments": segments,
        }
        bundle_bytes = len(_canonical_bytes(hash_projection))
        if bundle_bytes > _BUNDLE_LIMIT:
            raise ValueError("전체 프롬프트 묶음이 216 KiB 제한을 초과했습니다.")
        manifest = {
            "contract_version": _MANIFEST_VERSION,
            "common_sha256": _text_sha256(common),
            "specialized_sha256": _text_sha256(specialized) if specialized is not None else "",
            "runtime_context_sha256": _text_sha256(context_text),
            "bundle_sha256": _sha256(hash_projection),
            "byte_length": bundle_bytes,
            "segment_count": len(segments),
        }
        payload = {**hash_projection, "manifest": manifest}
        self.status = f"{purpose}: {len(segments)}개 메시지, {bundle_bytes} bytes"
        return Data(data=payload)
