"""Canonical JSON, hashes, bounded payloads, and versioned errors."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any


def json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if hasattr(value, "item") and callable(value.item):
        try:
            return json_value(value.item())
        except Exception:
            pass
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        json_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def byte_size(value: Any) -> int:
    return len(canonical_bytes(value))


def bounded(value: Any, max_bytes: int, label: str) -> Any:
    size = byte_size(value)
    if size > max_bytes:
        raise ContractError(
            "metadata_budget_exceeded",
            "payload_budget",
            f"{label} payload가 허용 크기를 초과했습니다.",
            {"label": label, "actual_bytes": size, "max_bytes": max_bytes},
        )
    return value


@dataclass(slots=True)
class ContractError(Exception):
    code: str
    stage: str
    public_message: str
    details: dict[str, Any] | None = None
    retryable: bool = False

    def __str__(self) -> str:
        return f"{self.code}: {self.public_message}"

    def as_dict(self, trace_id: str = "") -> dict[str, Any]:
        safe_details = self.details if isinstance(self.details, dict) else {}
        payload = {
            "error_registry_version": "error_registry.v1",
            "error_id": f"error:{sha256_json([self.code, self.stage, safe_details])[:24]}",
            "code": self.code,
            "stage": self.stage,
            "message": self.public_message,
            "retryable": bool(self.retryable),
            "details": safe_details,
            "trace_id": trace_id,
        }
        return payload
