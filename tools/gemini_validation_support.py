"""Small, secret-safe Gemini adapter shared by live validation tools.

This module deliberately uses the public REST surface instead of a provider
SDK so a validation run does not depend on an unpinned transitive package.
Only bounded hashes, model identity and token counters are exposed to report
builders.  API keys and raw provider payloads are never included in reports or
exception messages.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable


DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_VALIDATION_TEMPERATURE = 0
GEMINI_VALIDATION_FALLBACK_MODELS: tuple[str, ...] = ()


def require_exact_gemini_model(model: str) -> str:
    """Return the one approved validation model or fail before any API call.

    Live validation is evidence for a named model, not a best-effort provider
    run.  Accepting a different CLI value or silently falling back would make
    that evidence ambiguous, so both are deliberately unsupported.
    """

    normalized = str(model or "").strip().removeprefix("models/")
    if normalized != DEFAULT_GEMINI_MODEL:
        raise RuntimeError("exact_gemini_model_required")
    return normalized


def gemini_model_contract_evidence(model: str = DEFAULT_GEMINI_MODEL) -> dict[str, Any]:
    """Build the stable, secret-free model contract persisted by validators."""

    normalized = require_exact_gemini_model(model)
    return {
        "requested_model": normalized,
        "temperature": GEMINI_VALIDATION_TEMPERATURE,
        "candidate_count": 1,
        "fallback_enabled": False,
        "fallback_models": list(GEMINI_VALIDATION_FALLBACK_MODELS),
    }


def langflow_gemini_contract_evidence(
    flow: dict[str, Any],
    *,
    require_model: bool = True,
) -> dict[str, Any]:
    """Inspect exported native Language Model nodes without exposing secrets."""

    nodes: list[dict[str, Any]] = []
    for raw_node in ((flow.get("data") or {}).get("nodes") or []):
        if not isinstance(raw_node, dict):
            continue
        template = (((raw_node.get("data") or {}).get("node") or {}).get("template") or {})
        if not isinstance(template, dict):
            continue
        model_field = template.get("model")
        model_value = model_field.get("value") if isinstance(model_field, dict) else None
        if not model_value:
            continue
        configured = model_value if isinstance(model_value, list) else [model_value]
        names = sorted(
            str(item.get("name") or "").removeprefix("models/")
            for item in configured
            if isinstance(item, dict) and item.get("name")
        )
        providers = sorted(
            str(item.get("provider") or "")
            for item in configured
            if isinstance(item, dict) and item.get("provider")
        )
        temperature_field = template.get("temperature")
        temperature = (
            temperature_field.get("value")
            if isinstance(temperature_field, dict)
            else None
        )
        stream_field = template.get("stream")
        stream = stream_field.get("value") if isinstance(stream_field, dict) else None
        fallback_fields = sorted(
            str(key)
            for key, value in template.items()
            if ("fallback" in str(key).casefold() or "backup" in str(key).casefold())
            and isinstance(value, dict)
            and value.get("value") not in (None, "", False, [], {})
        )
        try:
            temperature_exact = temperature is not None and float(temperature) == float(
                GEMINI_VALIDATION_TEMPERATURE
            )
        except (TypeError, ValueError):
            temperature_exact = False
        node_evidence = {
            "node_id": str(raw_node.get("id") or "")[:128],
            "model_names": names,
            "providers": providers,
            "temperature": temperature,
            "stream": stream,
            "configured_fallback_fields": fallback_fields,
        }
        node_evidence["passed"] = (
            names == [DEFAULT_GEMINI_MODEL]
            and providers == ["Google Generative AI"]
            and temperature_exact
            and stream is False
            and not fallback_fields
        )
        nodes.append(node_evidence)

    passed = (bool(nodes) or not require_model) and all(
        item.get("passed") is True for item in nodes
    )
    return {
        "contract": gemini_model_contract_evidence(),
        "required": bool(require_model),
        "model_node_count": len(nodes),
        "nodes": nodes,
        "passed": passed,
    }


def load_dotenv_values(path: Path) -> dict[str, str]:
    """Read a dotenv file without mutating the process environment."""

    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            values[key] = value.strip().strip('"').strip("'")
    return values


def resolve_gemini_api_key(env_path: Path) -> str:
    """Resolve a Gemini key while keeping its value out of diagnostics."""

    values = load_dotenv_values(env_path)
    key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or values.get("GEMINI_API_KEY")
        or values.get("GOOGLE_API_KEY")
        or values.get("LLM_API_KEY")
        or ""
    ).strip()
    if not key:
        raise RuntimeError("gemini_api_key_not_configured")
    return key


def _bounded_usage(payload: dict[str, Any]) -> dict[str, int]:
    usage = payload.get("usageMetadata") if isinstance(payload.get("usageMetadata"), dict) else {}
    return {
        "prompt_tokens": max(0, int(usage.get("promptTokenCount") or 0)),
        "candidate_tokens": max(0, int(usage.get("candidatesTokenCount") or 0)),
        "total_tokens": max(0, int(usage.get("totalTokenCount") or 0)),
    }


class GeminiJsonModel:
    """LangChain-compatible ``invoke`` adapter with bounded evidence fields."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = DEFAULT_GEMINI_MODEL,
        timeout_seconds: int = 90,
        max_output_tokens: int = 8192,
        opener: Callable[..., Any] | None = None,
    ) -> None:
        self._api_key = str(api_key)
        self.model = require_exact_gemini_model(model)
        self.temperature = GEMINI_VALIDATION_TEMPERATURE
        self.fallback_models = GEMINI_VALIDATION_FALLBACK_MODELS
        self.timeout_seconds = max(1, min(int(timeout_seconds), 300))
        self.max_output_tokens = max(64, min(int(max_output_tokens), 32768))
        self._opener = opener or urllib.request.urlopen
        self.calls = 0
        self.prompt_hashes: list[str] = []
        self.response_hashes: list[str] = []
        self.usage: list[dict[str, int]] = []
        self.provider_model_versions: list[str] = []
        self.finish_reasons: list[str] = []
        self.candidate_text_bytes: list[int] = []

    def invoke(self, prompt: str) -> str:
        prompt_text = str(prompt)
        self.calls += 1
        self.prompt_hashes.append(sha256(prompt_text.encode("utf-8")).hexdigest())
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        body = json.dumps(
            {
                "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": self.temperature,
                    "candidateCount": 1,
                    "maxOutputTokens": self.max_output_tokens,
                },
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        request = urllib.request.Request(
            endpoint,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "x-goog-api-key": self._api_key},
        )
        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                payload_bytes = response.read()
        except urllib.error.HTTPError as exc:
            # Never read or surface provider error bodies. They can echo input.
            raise RuntimeError(f"gemini_http_{int(exc.code)}") from None
        except (urllib.error.URLError, TimeoutError):
            raise RuntimeError("gemini_transport_error") from None
        except Exception as exc:
            # A bounded type name is sufficient for transport diagnostics and
            # cannot accidentally include a URL containing credentials.
            raise RuntimeError(f"gemini_transport_{type(exc).__name__}") from None

        self.response_hashes.append(sha256(payload_bytes).hexdigest())
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RuntimeError("gemini_invalid_json_response") from None
        if not isinstance(payload, dict):
            raise RuntimeError("gemini_invalid_response_shape")
        candidates = payload.get("candidates")
        if not isinstance(candidates, list) or len(candidates) != 1:
            raise RuntimeError("gemini_missing_candidate")
        candidate = candidates[0] if isinstance(candidates[0], dict) else {}
        content = candidate.get("content") if isinstance(candidate.get("content"), dict) else {}
        parts = content.get("parts") if isinstance(content.get("parts"), list) else []
        text = "".join(
            str(part.get("text") or "") for part in parts if isinstance(part, dict)
        ).strip()
        if not text:
            raise RuntimeError("gemini_missing_text")
        self.usage.append(_bounded_usage(payload))
        self.provider_model_versions.append(str(payload.get("modelVersion") or "")[:128])
        finish_reason = str(candidate.get("finishReason") or "")[:64]
        self.finish_reasons.append(
            finish_reason if all(ch.isalnum() or ch == "_" for ch in finish_reason) else "unknown"
        )
        self.candidate_text_bytes.append(len(text.encode("utf-8")))
        return text

    def evidence(self) -> dict[str, Any]:
        """Return the only provider evidence safe for persisted reports."""

        aggregate = {
            "prompt_tokens": sum(item["prompt_tokens"] for item in self.usage),
            "candidate_tokens": sum(item["candidate_tokens"] for item in self.usage),
            "total_tokens": sum(item["total_tokens"] for item in self.usage),
        }
        provider_versions_exact = len(self.provider_model_versions) == self.calls and all(
            str(version).removeprefix("models/") == self.model
            or str(version).removeprefix("models/").startswith(f"{self.model}-")
            for version in self.provider_model_versions
        )
        return {
            "model": self.model,
            "model_contract": gemini_model_contract_evidence(self.model),
            "fallback_used": False,
            "provider_model_versions_exact": provider_versions_exact,
            "calls": self.calls,
            "prompt_sha256": list(self.prompt_hashes),
            "provider_response_sha256": list(self.response_hashes),
            "provider_model_versions": list(self.provider_model_versions),
            "finish_reasons": list(self.finish_reasons),
            "candidate_text_bytes": list(self.candidate_text_bytes),
            "usage": aggregate,
        }


def assert_secret_absent(value: Any, secret: str) -> None:
    """Fail before writing a report if a configured key leaked into it."""

    if secret and secret in json.dumps(value, ensure_ascii=False, default=str):
        raise RuntimeError("secret_leak_detected")
