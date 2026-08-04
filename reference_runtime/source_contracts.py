"""Physical-source to canonical-frame boundary for the typed executor.

Only this module understands physical column names.  A source result is mapped
once, against one pinned dataset contract, then the physical rows are discarded.
"""

from __future__ import annotations

import math
from collections import defaultdict
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from .canonical import ContractError, json_value, sha256_json
from .metadata_compiler import compute_catalog_sha256, validate_runtime_catalog


SOURCE_RESULT_VERSION = "source.result.v1"
SOURCE_BUNDLE_VERSION = "source.bundle.v1"
CANONICALIZER_VERSION = "source-contract-merger.v1"


def _validate_execution_catalog(runtime_catalog: dict[str, Any]) -> dict[str, Any]:
    """Validate catalog structure without exposing a hash in runtime payloads."""

    validation_copy = deepcopy(runtime_catalog)
    if not validation_copy.get("catalog_sha256"):
        validation_copy["catalog_sha256"] = compute_catalog_sha256(validation_copy)
    validate_runtime_catalog(validation_copy)
    return runtime_catalog


def canonicalize_rows(
    dataset_key: str,
    rows: Iterable[dict[str, Any]],
    runtime_catalog: dict[str, Any],
    *,
    physical_schema: Iterable[str] | dict[str, Any] | None = None,
    required_fields: Iterable[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Map physical rows to canonical rows exactly once.

    The return value is ``(rows, schema)``.  No undeclared physical column is
    retained, and no canonical-name fallback is attempted unless that name is
    explicitly registered as the primary physical column or an alias.
    """

    _validate_execution_catalog(runtime_catalog)
    datasets = runtime_catalog["datasets"]
    if dataset_key not in datasets:
        raise ContractError(
            "metadata_dependency_error",
            "source_merge",
            "dataset contract이 runtime catalog에 없습니다.",
            {"dataset_key": dataset_key},
        )
    dataset = datasets[dataset_key]
    all_bindings = dataset["fields"]
    requested = [str(field) for field in required_fields] if required_fields is not None else list(all_bindings)
    if not requested or len(requested) != len(set(requested)):
        raise ContractError(
            "source_schema_mismatch",
            "source_merge",
            "required_fields must be a non-empty unique canonical field list.",
            {"dataset_key": dataset_key},
        )
    unknown = sorted(set(requested) - set(all_bindings))
    if unknown:
        raise ContractError(
            "metadata_dependency_error",
            "source_merge",
            "Retrieval job requests fields outside the dataset registry.",
            {"dataset_key": dataset_key, "fields": unknown},
        )
    bindings = {field: all_bindings[field] for field in requested}
    materialized = list(rows)
    for index, row in enumerate(materialized):
        if not isinstance(row, dict):
            raise ContractError(
                "source_schema_mismatch",
                "source_merge",
                "source row가 object가 아닙니다.",
                {"dataset_key": dataset_key, "row_index": index},
            )
        if row.get("__canonicalized_by") or row.get("contract_version") == SOURCE_BUNDLE_VERSION:
            raise ContractError(
                "source_already_canonicalized",
                "source_merge",
                "이미 canonicalized된 row를 다시 mapping할 수 없습니다.",
                {"dataset_key": dataset_key, "row_index": index},
            )

    schema_fields = _schema_fields(physical_schema)
    if not schema_fields and materialized:
        schema_fields = set().union(*(set(row) for row in materialized))
    _validate_physical_schema(dataset_key, bindings, schema_fields, allow_empty=not materialized)

    canonical_rows: list[dict[str, Any]] = []
    for row_index, row in enumerate(materialized):
        canonical: dict[str, Any] = {}
        for canonical_field, binding in bindings.items():
            candidates = [str(binding["physical_column"]), *[str(value) for value in binding.get("physical_aliases", [])]]
            present = [candidate for candidate in candidates if candidate in row]
            if len(present) > 1:
                raise ContractError(
                    "ambiguous_field_binding",
                    "source_merge",
                    "하나의 canonical field에 복수 physical column이 동시에 존재합니다.",
                    {"dataset_key": dataset_key, "field": canonical_field, "physical_columns": present, "row_index": row_index},
                )
            if not present:
                if bool(binding.get("required_in_source")):
                    raise ContractError(
                        "source_schema_mismatch",
                        "source_merge",
                        "필수 physical field가 source row에 없습니다.",
                        {"dataset_key": dataset_key, "field": canonical_field, "row_index": row_index},
                    )
                canonical[canonical_field] = None
                continue
            value = row[present[0]]
            canonical[canonical_field] = _coerce_value(value, binding, dataset_key, canonical_field, row_index)
        canonical_rows.append(canonical)

    schema = [
        {
            "field": canonical_field,
            "semantic_type": binding["semantic_type"],
            "nullable": bool(binding.get("nullable", True)),
            "roles": list(binding.get("roles", [])),
        }
        for canonical_field, binding in bindings.items()
    ]
    return canonical_rows, schema


def merge_source_results(
    source_results: Iterable[dict[str, Any]],
    runtime_catalog: dict[str, Any],
    retrieval_jobs: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Merge one or more physical source results into a canonical bundle.

    Chunked results with the same ``source_alias`` are combined in deterministic
    chunk order.  Repeating the same source-result identity is rejected.
    """

    _validate_execution_catalog(runtime_catalog)
    results = list(source_results)
    jobs = list(retrieval_jobs) if retrieval_jobs is not None else []
    job_by_alias: dict[str, dict[str, Any]] = {}
    for job in jobs:
        if not isinstance(job, dict):
            raise ContractError("source_schema_mismatch", "source_merge", "retrieval job must be an object.")
        alias = str(job.get("source_alias") or job.get("job_id") or "")
        if not alias or alias in job_by_alias:
            raise ContractError("source_schema_mismatch", "source_merge", "retrieval job alias is missing or duplicated.")
        job_by_alias[alias] = job
    if not results:
        raise ContractError("source_schema_mismatch", "source_merge", "source result가 없습니다.")
    seen_result_ids: set[str] = set()
    grouped: dict[str, list[tuple[int, int, dict[str, Any]]]] = defaultdict(list)
    for position, result in enumerate(results):
        if not isinstance(result, dict):
            raise ContractError("source_schema_mismatch", "source_merge", "source result가 object가 아닙니다.", {"index": position})
        if result.get("canonicalized") or result.get("contract_version") == SOURCE_BUNDLE_VERSION:
            raise ContractError(
                "source_already_canonicalized",
                "source_merge",
                "source bundle/result를 두 번 canonicalize할 수 없습니다.",
                {"index": position},
            )
        result_id = str(result.get("source_result_id") or result.get("result_id") or result.get("job_id") or f"position:{position}")
        if result_id in seen_result_ids:
            raise ContractError(
                "duplicate_source_result",
                "source_merge",
                "동일 source result가 중복 전달됐습니다.",
                {"source_result_id": result_id},
            )
        seen_result_ids.add(result_id)
        alias = str(result.get("source_alias") or result.get("job_id") or "")
        dataset_key = str(result.get("dataset_key") or "")
        if not alias or not dataset_key:
            raise ContractError(
                "source_schema_mismatch",
                "source_merge",
                "source_alias/dataset_key가 필수입니다.",
                {"source_result_id": result_id},
            )
        if jobs:
            job = job_by_alias.get(alias)
            if not isinstance(job, dict):
                raise ContractError(
                    "source_schema_mismatch",
                    "source_merge",
                    "Source result does not correspond to a sealed retrieval job.",
                    {"source_alias": alias},
                )
            if dataset_key != str(job.get("dataset_key") or ""):
                raise ContractError(
                    "source_schema_mismatch",
                    "source_merge",
                    "Source result dataset differs from its sealed retrieval job.",
                    {"source_alias": alias, "dataset_key": dataset_key},
                )
            expected_parameters = deepcopy(job.get("parameters") or {})
            if result.get("applied_parameters") != expected_parameters:
                raise ContractError(
                    "source_schema_mismatch",
                    "source_merge",
                    "Source adapter did not prove the sealed retrieval parameters.",
                    {"source_alias": alias},
                )
            expected_filter_hash = sha256_json(job.get("filters") or {})
            if result.get("applied_filters_sha256") != expected_filter_hash:
                raise ContractError(
                    "source_schema_mismatch",
                    "source_merge",
                    "Source adapter did not prove the sealed retrieval filter.",
                    {"source_alias": alias},
                )
        status = str(result.get("status") or "").lower()
        if status not in {"ok", "empty", "error"}:
            raise ContractError(
                "source_schema_mismatch",
                "source_merge",
                "source result status가 올바르지 않습니다.",
                {"source_result_id": result_id, "status": status},
            )
        if status == "error":
            error = result.get("error") if isinstance(result.get("error"), dict) else {}
            raise ContractError(
                str(error.get("code") or "source_execution_failed"),
                "source_merge",
                "필수 source 조회가 실패했습니다.",
                {"source_alias": alias, "dataset_key": dataset_key, "source_error_code": error.get("code")},
                retryable=bool(error.get("retryable", False)),
            )
        rows = _rows_from_result(result)
        if status == "empty" and rows:
            raise ContractError(
                "source_schema_mismatch",
                "source_merge",
                "empty source result에 row가 포함됐습니다.",
                {"source_alias": alias, "dataset_key": dataset_key},
            )
        chunk_index = _integer(result.get("chunk_index"), default=position)
        grouped[alias].append((chunk_index, position, result))

    if jobs and set(grouped) != set(job_by_alias):
        raise ContractError(
            "source_missing",
            "source_merge",
            "Source result set does not exactly cover the sealed retrieval jobs.",
            {"missing": sorted(set(job_by_alias) - set(grouped)), "extra": sorted(set(grouped) - set(job_by_alias))},
        )

    frames: dict[str, dict[str, Any]] = {}
    source_manifest: list[dict[str, Any]] = []
    for alias in sorted(grouped):
        pieces = sorted(grouped[alias], key=lambda item: (item[0], item[1]))
        dataset_keys = {str(item[2]["dataset_key"]) for item in pieces}
        if len(dataset_keys) != 1:
            raise ContractError(
                "source_schema_mismatch",
                "source_merge",
                "하나의 source_alias에 복수 dataset이 연결됐습니다.",
                {"source_alias": alias, "dataset_keys": sorted(dataset_keys)},
            )
        dataset_key = next(iter(dataset_keys))
        job = job_by_alias.get(alias) if jobs else None
        required_fields = list(job.get("required_fields") or []) if isinstance(job, dict) else None
        combined_rows: list[dict[str, Any]] = []
        schema: list[dict[str, Any]] | None = None
        result_hashes: list[str] = []
        empty_count = 0
        for _, _, result in pieces:
            rows = _rows_from_result(result)
            if not rows:
                empty_count += 1
            canonical_rows, canonical_schema = canonicalize_rows(
                dataset_key,
                rows,
                runtime_catalog,
                physical_schema=result.get("physical_schema") or result.get("schema"),
                required_fields=required_fields,
            )
            if schema is not None and schema != canonical_schema:
                raise ContractError(
                    "source_schema_mismatch",
                    "source_merge",
                    "chunk별 canonical schema가 다릅니다.",
                    {"source_alias": alias, "dataset_key": dataset_key},
                )
            schema = canonical_schema
            combined_rows.extend(canonical_rows)
            result_hashes.append(str(result.get("content_sha256") or sha256_json(rows)))
        schema = schema or []
        frame_material = {
            "dataset_key": dataset_key,
            "schema": schema,
            "rows": [json_value(row) for row in combined_rows],
        }
        content_sha = sha256_json(frame_material)
        frames[alias] = {
            "contract_version": "canonical.frame.v1",
            "source_alias": alias,
            "dataset_key": dataset_key,
            "status": "empty" if not combined_rows else "ok",
            "canonicalized": True,
            "canonicalizer_version": CANONICALIZER_VERSION,
            "schema": schema,
            "rows": frame_material["rows"],
            "row_count": len(combined_rows),
            "chunk_count": len(pieces),
            "content_sha256": content_sha,
        }
        source_manifest.append(
            {
                "source_alias": alias,
                "dataset_key": dataset_key,
                "status": frames[alias]["status"],
                "row_count": len(combined_rows),
                "chunk_count": len(pieces),
                "empty_chunk_count": empty_count,
                "source_content_sha256s": result_hashes,
                "canonical_content_sha256": content_sha,
                "required_fields": list(required_fields or []),
                "applied_parameters": deepcopy((job or {}).get("parameters") or {}),
                "applied_filters_sha256": sha256_json((job or {}).get("filters") or {}),
            }
        )

    bundle: dict[str, Any] = {
        "contract_version": SOURCE_BUNDLE_VERSION,
        "canonicalizer_version": CANONICALIZER_VERSION,
        "canonicalized": True,
        "frames": frames,
        "source_manifest": source_manifest,
        "bundle_sha256": "",
    }
    bundle["bundle_sha256"] = compute_bundle_sha256(bundle)
    return bundle


def compute_bundle_sha256(bundle: dict[str, Any]) -> str:
    return sha256_json({key: value for key, value in bundle.items() if key != "bundle_sha256"})


def validate_source_bundle(bundle: dict[str, Any], runtime_catalog: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(bundle, dict) or bundle.get("contract_version") != SOURCE_BUNDLE_VERSION:
        raise ContractError("source_schema_mismatch", "source_merge", "source bundle version이 올바르지 않습니다.")
    if not bundle.get("canonicalized") or bundle.get("canonicalizer_version") != CANONICALIZER_VERSION:
        raise ContractError("source_schema_mismatch", "source_merge", "source bundle canonicalization marker가 없습니다.")
    if bundle.get("bundle_sha256") != compute_bundle_sha256(bundle):
        raise ContractError("source_schema_mismatch", "source_merge", "source bundle hash가 일치하지 않습니다.")
    if runtime_catalog is not None:
        _validate_execution_catalog(runtime_catalog)
    frames = bundle.get("frames")
    if not isinstance(frames, dict):
        raise ContractError("source_schema_mismatch", "source_merge", "source bundle frames가 object가 아닙니다.")
    for alias, frame in frames.items():
        if not isinstance(frame, dict) or frame.get("source_alias") != alias or not frame.get("canonicalized"):
            raise ContractError("source_schema_mismatch", "source_merge", "canonical frame contract가 올바르지 않습니다.", {"source_alias": alias})
        rows = frame.get("rows")
        if not isinstance(rows, list) or frame.get("row_count") != len(rows):
            raise ContractError("source_schema_mismatch", "source_merge", "canonical frame row count가 일치하지 않습니다.", {"source_alias": alias})
    return bundle


def executor_frames(
    bundle: dict[str, Any],
    runtime_catalog: dict[str, Any] | None = None,
    *,
    copy_rows: bool = True,
) -> dict[str, dict[str, Any]]:
    """Return rows plus the tiny canonical column list required for empty frames.

    The default preserves the public isolation contract. A single Flow stage
    that also owns the immutable source snapshot may set ``copy_rows=False``;
    ``TypedExecutor`` constructs pandas frames from the rows and does not mutate
    the list, avoiding a redundant full-source payload copy at that boundary.
    """

    validate_source_bundle(bundle, runtime_catalog)
    return {
        alias: {
            "rows": deepcopy(frame["rows"]) if copy_rows else frame["rows"],
            "columns": [str(item.get("field")) for item in frame.get("schema", []) if isinstance(item, dict) and item.get("field")],
        }
        for alias, frame in bundle["frames"].items()
    }


def _rows_from_result(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: Any = result.get("rows")
    if rows is None:
        rows = result.get("inline_rows")
    if rows is None and isinstance(result.get("data"), dict):
        rows = result["data"].get("rows")
    if rows is None:
        rows = []
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ContractError("source_schema_mismatch", "source_merge", "source rows가 object list가 아닙니다.")
    return rows


def _schema_fields(schema: Iterable[str] | dict[str, Any] | None) -> set[str]:
    if schema is None:
        return set()
    if isinstance(schema, dict):
        if isinstance(schema.get("fields"), list):
            values = schema["fields"]
            return {str(item.get("name") or item.get("field")) if isinstance(item, dict) else str(item) for item in values}
        return {str(key) for key in schema}
    if isinstance(schema, (str, bytes)):
        raise ContractError("source_schema_mismatch", "source_merge", "physical schema가 list/object가 아닙니다.")
    try:
        return {str(item.get("name") or item.get("field")) if isinstance(item, dict) else str(item) for item in schema}
    except TypeError as exc:
        raise ContractError("source_schema_mismatch", "source_merge", "physical schema가 list/object가 아닙니다.") from exc


def _validate_physical_schema(
    dataset_key: str,
    bindings: dict[str, dict[str, Any]],
    schema_fields: set[str],
    *,
    allow_empty: bool,
) -> None:
    if not schema_fields and allow_empty:
        return
    for canonical_field, binding in bindings.items():
        candidates = [str(binding["physical_column"]), *[str(value) for value in binding.get("physical_aliases", [])]]
        present = [candidate for candidate in candidates if candidate in schema_fields]
        if len(present) > 1:
            raise ContractError(
                "ambiguous_field_binding",
                "source_merge",
                "physical schema에 primary/alias column이 동시에 존재합니다.",
                {"dataset_key": dataset_key, "field": canonical_field, "physical_columns": present},
            )
        if not present and bool(binding.get("required_in_source")):
            raise ContractError(
                "source_schema_mismatch",
                "source_merge",
                "physical schema에 필수 field가 없습니다.",
                {"dataset_key": dataset_key, "field": canonical_field},
            )


def _coerce_value(value: Any, binding: dict[str, Any], dataset_key: str, field: str, row_index: int) -> Any:
    if _is_null(value):
        if not bool(binding.get("nullable", True)):
            raise ContractError(
                "source_schema_mismatch",
                "source_merge",
                "non-null canonical field가 null입니다.",
                {"dataset_key": dataset_key, "field": field, "row_index": row_index},
            )
        return None
    semantic_type = str(binding.get("semantic_type") or "string").lower()
    try:
        if semantic_type in {
            "number",
            "integer",
            "quantity",
            "float",
            "rate",
            "duration",
            "currency",
            "percent",
            "percentage",
            "ratio",
            "decimal",
        }:
            coerced = _number(value)
            multiplier = binding.get("multiplier")
            if multiplier is not None:
                coerced *= Decimal(str(multiplier))
            if semantic_type == "integer":
                if coerced != coerced.to_integral_value():
                    raise ValueError("fractional integer")
                return int(coerced)
            return int(coerced) if coerced == coerced.to_integral_value() else float(coerced)
        if semantic_type == "localdate":
            return _local_date(value).isoformat()
        if semantic_type == "localdatetime":
            timezone_name = str(binding.get("timezone") or "Asia/Seoul")
            parsed = _local_datetime(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=ZoneInfo(timezone_name))
            else:
                parsed = parsed.astimezone(ZoneInfo(timezone_name))
            return parsed.isoformat()
        if semantic_type in {"string", "identifier", "category"}:
            return str(value)
        return json_value(value)
    except (InvalidOperation, TypeError, ValueError, OverflowError) as exc:
        raise ContractError(
            "source_schema_mismatch",
            "source_merge",
            "source value를 canonical type으로 변환할 수 없습니다.",
            {"dataset_key": dataset_key, "field": field, "row_index": row_index, "semantic_type": binding.get("semantic_type")},
        ) from exc


def _number(value: Any) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean is not numeric")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise ValueError("non-finite number")
    text = str(value).strip().replace(",", "")
    if not text:
        raise ValueError("blank number")
    return Decimal(text)


def _local_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if len(text) == 8 and text.isdigit():
        return datetime.strptime(text, "%Y%m%d").date()
    if "T" in text:
        return datetime.fromisoformat(text).date()
    return date.fromisoformat(text)


def _local_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


def _is_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def _integer(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
