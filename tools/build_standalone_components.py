"""Build the self-contained Langflow 1.9.2 components for metadata-driven v6.

The reference runtime remains the reviewable source of truth.  This generator
mechanically flattens the selected modules, embeds the compiled catalog and
records every source hash.  Generated components never import another project
file at runtime and never use ``exec`` or ``eval``.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = PROJECT_ROOT / "reference_runtime"
CATALOG_PATH = PROJECT_ROOT / "metadata" / "fixtures" / "compiled" / "runtime_catalog.json"
SCHEMA_ROOT = PROJECT_ROOT / "contracts" / "schemas"
OUTPUT_ROOT = PROJECT_ROOT / "langflow_components"

CORE_MODULES = (
    "canonical.py",
    "contracts.py",
    "metadata_compiler.py",
    "source_contracts.py",
    "dummy_data.py",
    "request_literals.py",
    "typed_executor.py",
    "plan_compiler.py",
    "state_contracts.py",
    "presenter.py",
    "engine.py",
)


class GenerationError(RuntimeError):
    """Raised when an immutable source dependency is missing or malformed."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise GenerationError(f"{label} is missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GenerationError(f"{label} is not valid UTF-8 JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GenerationError(f"{label} must be a JSON object: {path}")
    return value


def _method_body(source: str) -> list[ast.stmt]:
    tree = ast.parse("def _generated():\n" + "\n".join(f"    {line}" for line in source.splitlines()))
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)
    return function.body


class _RuntimePatcher(ast.NodeTransformer):
    """Replace the only two reference-runtime sibling-import fallbacks."""

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        self.generic_visit(node)
        if node.name != "AnalysisEngine":
            return node
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if item.name == "_default_source_adapter":
                item.body = _method_body("return StandaloneSourceAdapter()")
            elif item.name == "_merge_sources":
                item.body = _method_body(
                    """bundle = merge_source_results(source_results, self.catalog, retrieval_jobs=plan.get("retrieval_jobs") or [])
frames = executor_frames(bundle, self.catalog)
snapshots = [deepcopy(frame) for frame in bundle.get(\"frames\", {}).values()]
diagnostics = [
    {
        \"job_id\": item.get(\"source_alias\"),
        \"dataset_key\": item.get(\"dataset_key\"),
        \"status\": item.get(\"status\"),
        \"row_count\": item.get(\"row_count\"),
        \"content_sha256\": item.get(\"canonical_content_sha256\"),
    }
    for item in bundle.get(\"source_manifest\", [])
]
return frames, snapshots, diagnostics"""
                )
        return node


def _clean_module(
    path: Path,
    *,
    drop_functions: set[str] | None = None,
    drop_assignments: set[str] | None = None,
    patch_analysis_engine: bool = False,
    patch_catalog_loader: bool = False,
    patch_default_catalog: bool = False,
    patch_schema_loader: bool = False,
) -> str:
    if not path.is_file():
        raise GenerationError(f"reference source is missing: {path}")
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise GenerationError(f"reference source does not parse: {path}: {exc}") from exc

    dropped_functions = set(drop_functions or ())
    dropped_assignments = set(drop_assignments or ())
    body: list[ast.stmt] = []
    for index, node in enumerate(tree.body):
        if index == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        if isinstance(node, ast.ImportFrom) and (node.module == "__future__" or int(node.level or 0) > 0):
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in dropped_functions:
            continue
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = {target.id for target in targets if isinstance(target, ast.Name)}
            if names & dropped_assignments:
                continue
        if patch_catalog_loader and isinstance(node, ast.FunctionDef) and node.name in {"load_runtime_catalog", "build_runtime_catalog"}:
            node.body = _method_body("return deepcopy(EMBEDDED_RUNTIME_CATALOG)")
        if patch_default_catalog and isinstance(node, ast.FunctionDef) and node.name == "_default_catalog":
            node.body = _method_body("return deepcopy(EMBEDDED_RUNTIME_CATALOG)")
        if patch_schema_loader and isinstance(node, ast.FunctionDef) and node.name == "_load_schema_cached":
            node.body = _method_body(
                """if name not in EMBEDDED_SCHEMAS:
    raise FileNotFoundError(name)
return EMBEDDED_SCHEMAS[name]"""
            )
        body.append(node)
    tree.body = body
    if patch_analysis_engine:
        tree = _RuntimePatcher().visit(tree)  # type: ignore[assignment]
    ast.fix_missing_locations(tree)
    cleaned = ast.unparse(tree).strip() + "\n"
    if "from ." in cleaned:
        raise GenerationError(f"relative import survived flattening: {path}")
    return cleaned


def _namespace_flattened_module(source: str, prefix: str, public_names: set[str]) -> str:
    """Prefix private globals so independently flattened modules cannot collide."""

    tree = ast.parse(source)
    rename: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name not in public_names and node.name != "__all__":
                rename[node.name] = f"{prefix}{node.name}"
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id != "__all__" and target.id not in public_names:
                    rename[target.id] = f"{prefix}{target.id}"

    class Renamer(ast.NodeTransformer):
        def visit_Name(self, node: ast.Name) -> ast.AST:
            if node.id in rename:
                node.id = rename[node.id]
            return node

        def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
            if node.name in rename:
                node.name = rename[node.name]
            return self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
            if node.name in rename:
                node.name = rename[node.name]
            return self.generic_visit(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
            if node.name in rename:
                node.name = rename[node.name]
            return self.generic_visit(node)

    tree = Renamer().visit(tree)  # type: ignore[assignment]
    ast.fix_missing_locations(tree)
    return ast.unparse(tree).strip() + "\n"


def _catalog_literal(catalog: dict[str, Any]) -> str:
    # JSON is smaller and more stable than pprint output.  JSON literals are
    # decoded once while the standalone component module is loaded.
    compact = json.dumps(catalog, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "EMBEDDED_RUNTIME_CATALOG = json.loads(" + repr(compact) + ")\n"


def _schemas_literal(schemas: dict[str, dict[str, Any]]) -> str:
    compact = json.dumps(schemas, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "EMBEDDED_SCHEMAS = json.loads(" + repr(compact) + ")\n"


def _manifest(paths: list[Path], catalog: dict[str, Any]) -> dict[str, Any]:
    records = {
        path.relative_to(PROJECT_ROOT).as_posix(): _sha256_file(path)
        for path in sorted(paths, key=lambda item: item.as_posix())
    }
    catalog_hash = _sha256_file(CATALOG_PATH)
    return {
        "contract_version": "standalone.source.manifest.v1",
        "catalog_contract_version": catalog.get("contract_version"),
        "catalog_declared_sha256": catalog.get("catalog_sha256"),
        "catalog_file_sha256": catalog_hash,
        "reference_sources": records,
    }


def _header(manifest: dict[str, Any], component_name: str) -> str:
    manifest_json = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return f'''# -*- coding: utf-8 -*-
"""GENERATED standalone component: {component_name}.

Regenerate with tools/build_standalone_components.py.  Do not hand edit.
"""
from __future__ import annotations

import json

EMBEDDED_SOURCE_MANIFEST = json.loads({manifest_json!r})
'''


EMBEDDED_SOURCE_ADAPTER = r'''
class StandaloneSourceAdapter:
    """Bounded adapter for trusted, already-authorized canonical source rows.

    The adapter intentionally does not accept SQL, URLs, paths or dynamic
    collection names.  A deployment can inject canonical rows through the
    component Data input after its reviewed source resolver has run.  Missing
    rows fail closed instead of fabricating business data.
    """

    def __init__(self, payload=None, *, max_rows=50000, max_memory_bytes=67108864):
        raw = getattr(payload, "data", payload)
        self.payload = deepcopy(raw) if isinstance(raw, dict) else {}
        self.max_rows = max(1, min(int(max_rows), 100000))
        self.max_memory_bytes = max(1048576, min(int(max_memory_bytes), 536870912))

    def _rows(self, job):
        job_id = str(job.get("job_id") or "")
        dataset_key = str(job.get("dataset_key") or "")
        value = None
        jobs = self.payload.get("jobs")
        datasets = self.payload.get("datasets")
        if isinstance(jobs, dict) and job_id in jobs:
            value = jobs[job_id]
        elif isinstance(datasets, dict) and dataset_key in datasets:
            value = datasets[dataset_key]
        elif dataset_key in self.payload:
            value = self.payload[dataset_key]
        elif isinstance(self.payload.get("rows"), list):
            value = self.payload.get("rows")
        if isinstance(value, dict) and isinstance(value.get("rows"), list):
            value = value.get("rows")
        if value is None:
            raise ContractError(
                "source_missing",
                "retrieval",
                "승인된 canonical source rows가 제공되지 않았습니다.",
                {"job_id": job_id, "dataset_key": dataset_key},
            )
        if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
            raise ContractError("source_contract_error", "retrieval", "source rows는 object 배열이어야 합니다.")
        if len(value) > self.max_rows:
            raise ContractError(
                "source_row_limit_exceeded",
                "retrieval",
                "source row limit을 초과했습니다.",
                {"limit": self.max_rows},
            )
        rows = deepcopy(value)
        if len(canonical_bytes(rows)) > self.max_memory_bytes:
            raise ContractError(
                "executor_memory_limit_exceeded",
                "retrieval",
                "source payload memory limit을 초과했습니다.",
                {"limit_bytes": self.max_memory_bytes},
            )
        return rows

    def _source_result(self, job, rows):
        dataset_key = str(job.get("dataset_key") or "")
        source_alias = str(job.get("source_alias") or job.get("job_id") or dataset_key)
        result = source_result_for_dataset(dataset_key, source_alias=source_alias, rows=rows)
        result["source_result_id"] = f"inline:{job.get('job_id') or source_alias}:{result['content_sha256'][:16]}"
        result["source_type"] = "trusted_inline"
        return result

    def retrieve(self, job, catalog):
        if not self.payload:
            return source_results_for_jobs([job], catalog)[0]
        rows = self._rows(job)
        return self._source_result(job, rows)

    def retrieve_live(self, job, catalog):
        # Live adapters must resolve credentials and reviewed query slots before
        # this boundary.  The component only consumes their canonical rows.
        rows = self._rows(job)
        return self._source_result(job, rows)
'''


TRUSTED_ANALYSIS_COMPONENT = r'''
import os
from copy import deepcopy

from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, DropdownInput, HandleInput, IntInput, MessageInput, Output, SecretStrInput, StrInput
from lfx.schema.data import Data


def _secret_text(value):
    if hasattr(value, "get_secret_value"):
        value = value.get_secret_value()
    return str(value or "").strip()


def _message_context(value):
    text = str(getattr(value, "text", value) or "").strip()
    data = getattr(value, "data", None)
    data = data if isinstance(data, dict) else {}
    metadata_candidates = []
    for name in ("a2a_metadata", "framework2_metadata", "metadata"):
        candidate = getattr(value, name, None)
        if isinstance(candidate, dict):
            metadata_candidates.append(candidate)
        nested = data.get(name)
        if isinstance(nested, dict):
            metadata_candidates.append(nested)
    metadata = metadata_candidates[0] if metadata_candidates else {}
    session_id = str(getattr(value, "session_id", "") or data.get("session_id") or "")
    if not session_id:
        for candidate in metadata_candidates:
            session_id = str(
                candidate.get("session_id")
                or candidate.get("sessionId")
                or candidate.get("conversation_id")
                or candidate.get("thread_id")
                or ""
            )
            if session_id:
                break
    upstream_ref = str(metadata.get("upstream_result_ref") or data.get("upstream_result_ref") or "")
    session_id = session_id or "default"
    # Ownership is a server-side authentication concern. Message fields are
    # request payload and must never select another owner's persistent state,
    # even when named owner_subject_id or authenticated_subject_id.
    return text, session_id, upstream_ref


class TrustedAnalysisEngine(Component):
    display_name = "Trusted Analysis Engine"
    description = "Compiled metadata와 typed Execution IR로 분석하며, 모호한 의도에서만 연결된 LLM을 호출합니다."
    icon = "shield-check"

    inputs = [
        MessageInput(name="input_message", display_name="질문", required=True),
        HandleInput(name="language_model", display_name="Intent Language Model", input_types=["LanguageModel"], required=False),
        DataInput(name="source_payload", display_name="Trusted Canonical Source Rows", required=False, advanced=True),
        DropdownInput(name="data_mode", display_name="Data Mode", options=["dummy", "inline", "live"], value="dummy"),
        StrInput(name="reference_instant", display_name="Reference Instant", value="", required=False),
        StrInput(name="reference_timezone", display_name="Timezone", value="Asia/Seoul"),
        SecretStrInput(name="mongo_uri", display_name="MongoDB URI", value="", required=False),
        StrInput(name="mongo_database", display_name="MongoDB Database", value="", required=False),
        StrInput(name="result_collection", display_name="Result Collection", value="agent_v6_result_store"),
        StrInput(name="state_collection", display_name="State Collection", value="agent_v6_session_state"),
        IntInput(name="mongo_timeout_ms", display_name="MongoDB Timeout (ms)", value=5000),
        IntInput(name="result_ttl_seconds", display_name="Result TTL (seconds)", value=3600),
        IntInput(name="source_row_limit", display_name="Source Row Limit", value=50000),
        IntInput(name="executor_row_limit", display_name="Executor Row Limit", value=100000),
        IntInput(name="executor_memory_limit_mb", display_name="Executor Memory Limit (MiB)", value=64),
        StrInput(name="download_base_url", display_name="Download Base URL", value="", required=False),
    ]
    outputs = [Output(name="response", display_name="Canonical Response", method="run_analysis", types=["Data"])]

    def _state_store(self, subject_id):
        uri = _secret_text(getattr(self, "mongo_uri", "")) or os.getenv("MONGODB_URI", "").strip()
        # Persistent refs require a trusted principal.  Anonymous chat keeps an
        # in-memory state and cannot accidentally share owner-bound references.
        if not uri or subject_id == "anonymous":
            return InMemoryStateStore()
        database = str(getattr(self, "mongo_database", "") or os.getenv("MONGODB_DATABASE", "datagov"))
        return MongoStateStore(
            uri,
            database=database,
            result_collection=str(getattr(self, "result_collection", "agent_v6_result_store")),
            state_collection=str(getattr(self, "state_collection", "agent_v6_session_state")),
            timeout_ms=max(500, min(int(getattr(self, "mongo_timeout_ms", 5000)), 30000)),
        )

    def run_analysis(self) -> Data:
        question, session_id, upstream_ref = _message_context(getattr(self, "input_message", None))
        runtime_session = str(getattr(getattr(self, "graph", None), "session_id", "") or getattr(self, "_session_id", "") or "")
        if session_id == "default" and runtime_session:
            session_id = runtime_session
        runtime_user_value = getattr(self, "user_id", "")
        runtime_user = "" if runtime_user_value is None else str(runtime_user_value).strip()
        if runtime_user.lower() in {"none", "null", "undefined"}:
            runtime_user = ""
        subject_id = f"langflow:{runtime_user}" if runtime_user else "anonymous"
        if not question:
            request = {"question": "", "session_id": session_id}
            response = error_response(request, ContractError("request_invalid", "request", "질문이 비어 있습니다.").as_dict())
            return Data(data=response)
        source_limit = max(1, min(int(getattr(self, "source_row_limit", 50000)), 100000))
        executor_limit = max(1, min(int(getattr(self, "executor_row_limit", 100000)), 100000))
        memory_mb = max(1, min(int(getattr(self, "executor_memory_limit_mb", 64)), 512))
        timezone_name = str(getattr(self, "reference_timezone", "") or os.getenv("AGENT_TIMEZONE", "Asia/Seoul"))
        if timezone_name != "Asia/Seoul":
            request = {"question": question, "session_id": session_id}
            response = error_response(request, ContractError("request_invalid", "request", "v6 기준 timezone은 Asia/Seoul이어야 합니다.").as_dict())
            return Data(data=response)
        source_adapter = StandaloneSourceAdapter(
            getattr(self, "source_payload", None),
            max_rows=source_limit,
            max_memory_bytes=memory_mb * 1024 * 1024,
        )
        engine = AnalysisEngine(
            catalog=EMBEDDED_RUNTIME_CATALOG,
            source_adapter=source_adapter,
            state_store=self._state_store(subject_id),
            max_executor_rows=executor_limit,
            result_ttl_seconds=max(60, min(int(getattr(self, "result_ttl_seconds", 3600)), 604800)),
            download_base_url=str(getattr(self, "download_base_url", "") or os.getenv("DATA_REF_DOWNLOAD_BASE_URL", "")),
        )
        response = engine.analyze(
            question,
            session_id=session_id,
            subject_id=subject_id,
            reference_instant=str(getattr(self, "reference_instant", "") or os.getenv("AGENT_DEFAULT_DATE", "")) or None,
            model=getattr(self, "language_model", None),
            upstream_result_ref=upstream_ref,
            data_mode=str(getattr(self, "data_mode", "dummy") or "dummy"),
        )
        # AnalysisEngine owns canonical response assembly and hashing. The
        # standalone adapter must fan out this value without mutating trace or
        # invalidating response_sha256.
        return Data(data=response)
'''


PIPELINE_HELPERS = r'''
from copy import deepcopy


PIPELINE_VERSION = "pipeline.context.v1"


def _payload(value):
    raw = getattr(value, "data", value)
    # Pipeline contexts are immutable-by-contract.  Copy only the top-level
    # envelope so large source/result row arrays stay shared between adjacent
    # nodes; components that intentionally mutate nested material must take an
    # explicit local deepcopy at that mutation boundary.
    return dict(raw) if isinstance(raw, dict) else {}


def _pipeline_error(current, exc, stage):
    context = _payload(current)
    request = context.get("request") if isinstance(context.get("request"), dict) else {}
    trace_id = str(context.get("trace_id") or "")
    if isinstance(exc, ContractError):
        error = exc.as_dict(trace_id)
    else:
        error = ContractError(
            "plan_contract_error",
            stage,
            "분석 파이프라인 계약 오류가 발생했습니다.",
            {"error_type": type(exc).__name__},
        ).as_dict(trace_id)
    context.update(
        {
            "contract_version": PIPELINE_VERSION,
            "ok": False,
            "stage": stage,
            "request": request,
            "error": error,
        }
    )
    return context


def _require_context(value, stage):
    context = _payload(value)
    if context.get("contract_version") != PIPELINE_VERSION:
        raise ContractError("plan_contract_error", stage, "pipeline.context.v1 입력이 필요합니다.")
    return context


def _registered_recipe_ops(value):
    result = []
    if isinstance(value, dict):
        if isinstance(value.get("op"), str):
            result.append(str(value["op"]))
        for child in value.values():
            result.extend(_registered_recipe_ops(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(_registered_recipe_ops(child))
    return result


def _planner_profile(catalog):
    if not isinstance(catalog, dict) or catalog.get("contract_version") != "metadata.runtime.catalog.v2":
        return "legacy_v1"
    allowed = {
        "filter", "project", "aggregate", "join", "derive", "compare_fields",
        "sort", "rank", "transform_previous_result", "registered_call",
    }
    recipe_values = list((catalog.get("recipes") or {}).values())
    operations = {op for value in recipe_values for op in _registered_recipe_ops(value)}
    has_legacy_marker = any("legacy_op" in json.dumps(value, ensure_ascii=False) for value in recipe_values)
    if operations <= allowed and not has_legacy_marker:
        return "generic_v2"
    profile = catalog.get("output_profile") if isinstance(catalog.get("output_profile"), dict) else {}
    if profile.get("planner_profile") == "legacy_v1_compat":
        expected = str(profile.get("legacy_catalog_sha256") or "")
        actual = str(EMBEDDED_RUNTIME_CATALOG.get("catalog_sha256") or "")
        identity_ok = str(catalog.get("domain_id") or "") == "manufacturing"
        compiler_ok = str(catalog.get("compiler_version") or "") in {
            "metadata-domain-compiler.v6.2", "metadata-domain-compiler.v6.3"
        }
        # metadata.runtime.catalog.v2 does not expose authoring provenance.  The
        # executable boundary is instead the validated package/bundle/catalog
        # hash chain plus this exact embedded-v1 pin, domain identity and
        # compiler allowlist.  Requiring a non-contract field here would make
        # every valid migrated manufacturing package impossible to execute.
        if expected and expected == actual and identity_ok and compiler_ok:
            return "legacy_v1_compat"
    raise ContractError(
        "unsupported_operation",
        "planner_profile",
        "The active domain requires typed operators that are not supported by the generic v2 planner.",
        {"registered_operations": sorted(operations), "profile": profile.get("planner_profile")},
    )
'''


REQUEST_STATE_COMPONENT = r'''
import builtins
import os

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, IntInput, MessageInput, Output, SecretStrInput, StrInput
from lfx.schema.data import Data


def _secret_text(value):
    if hasattr(value, "get_secret_value"):
        value = value.get_secret_value()
    return str(value or "").strip()


def _message_context(value):
    text = str(getattr(value, "text", value) or "").strip()
    data = getattr(value, "data", None)
    data = data if isinstance(data, dict) else {}
    metadata_candidates = []
    for name in ("a2a_metadata", "framework2_metadata", "metadata"):
        candidate = getattr(value, name, None)
        if isinstance(candidate, dict):
            metadata_candidates.append(candidate)
        nested = data.get(name)
        if isinstance(nested, dict):
            metadata_candidates.append(nested)
    metadata = metadata_candidates[0] if metadata_candidates else {}
    session_id = str(getattr(value, "session_id", "") or data.get("session_id") or "")
    if not session_id:
        for candidate in metadata_candidates:
            session_id = str(candidate.get("session_id") or candidate.get("sessionId") or candidate.get("conversation_id") or candidate.get("thread_id") or "")
            if session_id:
                break
    upstream_ref = str(metadata.get("upstream_result_ref") or data.get("upstream_result_ref") or "")
    return text, session_id or "default", upstream_ref


def _shared_memory_store():
    key = "_metadata_driven_v6_pipeline_state_store_v1"
    store = getattr(builtins, key, None)
    if store is None or not all(hasattr(store, name) for name in ("load_state", "load_ref", "commit_execution")):
        store = InMemoryStateStore()
        setattr(builtins, key, store)
    return store


class RequestStateCapsule(Component):
    display_name = "요청 및 세션 상태 고정"
    description = "질문 원문과 인증된 세션 상태를 검증해 이후 노드가 사용하는 간결한 요청 컨텍스트로 고정합니다."
    icon = "scan-text"
    metadata = {"logical_stage": "request_state"}

    inputs = [
        MessageInput(name="input_message", display_name="사용자 질문", required=True, info="분석할 자연어 질문과 세션 식별 정보가 담긴 메시지입니다."),
        DataInput(name="domain_bundle", display_name="도메인 실행 번들", required=True, info="승인된 데이터셋·필드·지표 정의가 포함된 불변 도메인 번들입니다."),
        StrInput(name="reference_instant", display_name="기준 시각", value="", required=False, info="상대 날짜 해석의 기준 시각입니다. 비워 두면 런타임 기본값을 사용합니다."),
        StrInput(name="reference_timezone", display_name="기준 시간대", value="Asia/Seoul", info="기준 시각과 날짜 조건을 해석할 시간대입니다. v6 기본값은 Asia/Seoul입니다."),
        SecretStrInput(name="mongo_uri", display_name="MongoDB 연결 URI", value="", required=False, info="인증된 멀티턴 상태와 결과를 저장할 MongoDB 연결 문자열입니다."),
        StrInput(name="mongo_database", display_name="MongoDB 데이터베이스", value="datagov", info="세션 상태 및 결과 컬렉션이 위치한 데이터베이스 이름입니다."),
        StrInput(name="result_collection", display_name="분석 결과 컬렉션", value="agent_v6_result_store", info="불변 분석 결과를 저장하는 v6 전용 컬렉션입니다."),
        StrInput(name="state_collection", display_name="세션 상태 컬렉션", value="agent_v6_session_state", info="멀티턴 세션 상태를 저장하는 v6 전용 컬렉션입니다."),
        IntInput(name="mongo_timeout_ms", display_name="MongoDB 제한 시간(ms)", value=5000, info="MongoDB 연결 및 조회에 적용할 제한 시간(밀리초)입니다."),
        BoolInput(
            name="allow_anonymous_multiturn",
            display_name="익명 멀티턴 허용",
            value=False,
            advanced=True,
            info="신뢰된 단일 사용자 환경에서만 활성화합니다. 20자 이상의 추측 불가능한 session_id가 필요합니다.",
        ),
    ]
    outputs = [Output(name="request_context", display_name="검증된 요청 컨텍스트", method="build_context", types=["Data"])]

    def _state_collection_names(self):
        values = {
            "result_collection": str(getattr(self, "result_collection", "agent_v6_result_store") or "").strip(),
            "state_collection": str(getattr(self, "state_collection", "agent_v6_session_state") or "").strip(),
        }
        expected = {
            "result_collection": "agent_v6_result_store",
            "state_collection": "agent_v6_session_state",
        }
        if values != expected or len(set(values.values())) != 2:
            raise ContractError(
                "state_policy_mismatch",
                "state_store_config",
                "State collections are role-bound to the registered distinct v6-only names.",
                {"expected": expected, "actual": values},
            )
        return values

    def _state_store(self, subject_id, allow_anonymous_multiturn=False):
        collections = self._state_collection_names()
        uri = _secret_text(getattr(self, "mongo_uri", "")) or os.getenv("MONGODB_URI", "").strip()
        if subject_id == "anonymous":
            return _shared_memory_store() if allow_anonymous_multiturn else InMemoryStateStore()
        if not uri:
            return _shared_memory_store()
        return MongoStateStore(
            uri,
            database=str(getattr(self, "mongo_database", "") or os.getenv("MONGODB_DATABASE", "datagov")),
            result_collection=collections["result_collection"],
            state_collection=collections["state_collection"],
            timeout_ms=max(500, min(int(getattr(self, "mongo_timeout_ms", 5000)), 30000)),
        )

    def build_context(self) -> Data:
        context = {"contract_version": PIPELINE_VERSION, "ok": True, "stage": "request_state"}
        try:
            question, session_id, upstream_ref = _message_context(getattr(self, "input_message", None))
            runtime_session = str(getattr(getattr(self, "graph", None), "session_id", "") or getattr(self, "_session_id", "") or "")
            if session_id == "default" and runtime_session:
                session_id = runtime_session
            runtime_user = str(getattr(self, "user_id", "") or "").strip()
            subject_id = f"langflow:{runtime_user}" if runtime_user and runtime_user.lower() not in {"none", "null", "undefined"} else "anonymous"
            if not question:
                raise ContractError("request_invalid", "request", "질문이 비어 있습니다.")
            anonymous_multiturn_enabled = subject_id == "anonymous" and bool(
                getattr(self, "allow_anonymous_multiturn", False)
            )
            if anonymous_multiturn_enabled and (session_id == "default" or len(session_id.strip()) < 20):
                raise ContractError(
                    "request_invalid",
                    "request",
                    "anonymous multi-turn에는 20자 이상의 추측 불가능한 session_id가 필요합니다.",
                )
            domain_context = _require_context(getattr(self, "domain_bundle", None), "request_state")
            if not domain_context.get("ok"):
                context.update({"ok": False, "stage": domain_context.get("stage"), "error": domain_context.get("error")})
                return Data(data=context)
            domain_identity = domain_context.get("domain_bundle") if isinstance(domain_context.get("domain_bundle"), dict) else {}
            domain_id = str(domain_identity.get("domain_id") or "default")
            environment = str(domain_identity.get("environment") or "production")
            storage_session_id = f"{environment}:{domain_id}:{session_id}"
            state_mode = (
                "persistent_anonymous_opt_in"
                if anonymous_multiturn_enabled
                else "ephemeral_anonymous"
                if subject_id == "anonymous"
                else "persistent_authenticated"
            )
            state_policy_material = {
                "contract_version": "state.policy.v1",
                "mode": state_mode,
                "subject_id": subject_id,
                "storage_session_id": storage_session_id,
                "anonymous_multiturn_enabled": anonymous_multiturn_enabled,
            }
            state_policy = {**state_policy_material, "policy_sha256": sha256_json(state_policy_material)}
            timezone_name = str(getattr(self, "reference_timezone", "") or os.getenv("AGENT_TIMEZONE", "Asia/Seoul"))
            if timezone_name != "Asia/Seoul":
                raise ContractError("request_invalid", "request", "v6 기준 timezone은 Asia/Seoul이어야 합니다.")
            store = self._state_store(subject_id, anonymous_multiturn_enabled)
            prior_state = store.load_state(subject_id, storage_session_id)
            prior_version = int(prior_state.get("state_version", 0)) if isinstance(prior_state, dict) else 0
            prior_ref = str(upstream_ref or (prior_state.get("executed_result_ref") if isinstance(prior_state, dict) else "") or "")
            prior_semantics = (((prior_state or {}).get("semantic_context") or {}).get("semantics") or {}) if isinstance(prior_state, dict) else {}
            prior_result = {}
            if prior_ref:
                prior_record = store.load_ref(prior_ref, subject_id, storage_session_id)
                prior_result = deepcopy(prior_record.get("payload") or {})
                contract = str(prior_result.get("contract_version") or "")
                schema = "executed-result.schema.json" if contract == "executed.result.v1" else "analysis-result.schema.json" if contract == "analysis.result.v1" else ""
                if not schema:
                    raise ContractError("state_reference_forbidden", "state_load", "후속 질문이 참조한 결과 계약을 사용할 수 없습니다.")
                validate_contract(prior_result, schema, stage="state_load")
            request = build_request_capsule(
                question,
                session_id=session_id,
                subject_id=subject_id,
                reference_instant=str(getattr(self, "reference_instant", "") or os.getenv("AGENT_DEFAULT_DATE", "")) or None,
                previous_state_ref=prior_ref,
                upstream_result_ref=upstream_ref,
            )
            validate_contract(request, "request-capsule.schema.json", stage="request_contract")
            context.update(
                {
                    "request": request,
                    "trace_id": f"trace:{sha256_json(request)[:24]}",
                    "subject_id": subject_id,
                    "session_id": session_id,
                    "storage_session_id": storage_session_id,
                    "anonymous_multiturn_enabled": anonymous_multiturn_enabled,
                    "state_policy": state_policy,
                    "domain_identity": {key: domain_identity.get(key) for key in ("domain_id", "environment", "revision", "catalog_sha256", "package_sha256", "bundle_sha256")},
                    "prior_version": prior_version,
                    "prior_result": prior_result,
                    "prior_semantics": prior_semantics,
                    "route_telemetry": {"intent_llm_calls": 0, "fallback_used": False},
                }
            )
        except Exception as exc:
            context = _pipeline_error(context, exc, "request_state")
        return Data(data=context)
'''


DOMAIN_BUNDLE_COMPONENT = r'''
import os

from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, DropdownInput, IntInput, Output, SecretStrInput, StrInput
from lfx.schema.data import Data


def _secret_text(value):
    if hasattr(value, "get_secret_value"):
        value = value.get_secret_value()
    return str(value or "").strip()


def _runtime_catalog(value):
    if not isinstance(value, dict):
        return None
    for candidate in (
        value,
        value.get("runtime_catalog"),
        value.get("compiled_catalog"),
        value.get("catalog"),
        (value.get("domain_bundle") or {}).get("runtime_catalog") if isinstance(value.get("domain_bundle"), dict) else None,
    ):
        if isinstance(candidate, dict) and {"datasets", "fields", "metrics"}.issubset(candidate):
            return deepcopy(candidate)
    return None


def _validate_catalog(catalog):
    if not isinstance(catalog, dict):
        raise ContractError("metadata_dependency_error", "domain_bundle", "runtime catalog를 찾을 수 없습니다.")
    if catalog.get("contract_version") == "metadata.runtime.catalog.v2":
        return validate_runtime_catalog_v2(catalog)
    missing = {"contract_version", "datasets", "fields", "metrics", "catalog_sha256"} - set(catalog)
    if missing:
        raise ContractError("metadata_dependency_error", "domain_bundle", "runtime catalog 필수 필드가 없습니다.", {"missing": sorted(missing)})
    for key in ("datasets", "fields", "metrics"):
        if not isinstance(catalog.get(key), dict):
            raise ContractError("metadata_dependency_error", "domain_bundle", f"runtime catalog {key}는 object여야 합니다.")
    return catalog


class DomainBundleLoader(Component):
    display_name = "도메인 실행 번들 불러오기"
    description = "승인된 v6 활성 번들 또는 인라인 번들을 검증해 하나의 불변 실행 카탈로그로 제공합니다. 내장 제조 기준본은 회귀 검증 전용입니다."
    icon = "package-open"
    metadata = {"logical_stage": "domain_bundle"}

    inputs = [
        StrInput(name="domain_id", display_name="도메인 ID", value="default", info="불러올 업무 도메인의 고유 식별자입니다. 공유 Flow에서는 각 업무 도메인 ID로 바꿉니다."),
        StrInput(name="environment", display_name="운영 환경", value="production", info="활성 번들을 구분하는 실행 환경 이름입니다."),
        DropdownInput(name="metadata_source_mode", display_name="메타데이터 원본 방식", options=["v6_active", "inline", "embedded_baseline"], value="v6_active", info="일반 운영은 MongoDB 활성 번들을 사용합니다. embedded_baseline은 내장 제조 회귀 fixture 전용입니다."),
        DataInput(name="inline_domain_bundle", display_name="인라인 도메인 번들", required=False, info="원본 방식이 inline일 때 직접 전달할 검증 대상 도메인 번들입니다."),
        SecretStrInput(name="mongo_uri", display_name="MongoDB 연결 URI", value="", required=False, info="v6 활성 번들을 읽을 MongoDB 연결 문자열입니다."),
        StrInput(name="mongo_database", display_name="MongoDB 데이터베이스", value="datagov", info="활성 포인터와 도메인 번들이 저장된 데이터베이스입니다."),
        StrInput(name="active_collection", display_name="활성 포인터 컬렉션", value="agent_v6_metadata_active", info="도메인별 현재 활성 리비전을 가리키는 컬렉션입니다."),
        StrInput(name="bundle_collection", display_name="도메인 번들 컬렉션", value="agent_v6_metadata_bundles", info="검증·컴파일된 불변 도메인 번들을 저장하는 컬렉션입니다."),
        IntInput(name="mongo_timeout_ms", display_name="MongoDB 제한 시간(ms)", value=5000, info="MongoDB 연결 및 조회에 적용할 제한 시간(밀리초)입니다."),
    ]
    outputs = [Output(name="domain_bundle", display_name="검증된 도메인 실행 번들", method="load_bundle", types=["Data"])]

    def load_bundle(self) -> Data:
        context = {"contract_version": PIPELINE_VERSION, "ok": True, "stage": "domain_bundle"}
        try:
            mode = str(getattr(self, "metadata_source_mode", "v6_active") or "v6_active")
            domain_id = str(getattr(self, "domain_id", "") or "default").strip()
            environment = str(getattr(self, "environment", "") or "production").strip()
            revision = "embedded"
            source = mode
            package = None
            if mode == "embedded_baseline":
                catalog = deepcopy(EMBEDDED_RUNTIME_CATALOG)
            elif mode == "inline":
                inline_value = _payload(getattr(self, "inline_domain_bundle", None))
                inline_package = inline_value.get("domain_package") if isinstance(inline_value.get("domain_package"), dict) else inline_value
                if inline_package.get("contract_version") == "domain.package.v1":
                    package = validate_domain_package(inline_package)
                    if package["domain_id"] != domain_id or package["environment"] != environment:
                        raise ContractError("metadata_dependency_error", "domain_bundle", "inline package identity가 node domain/environment와 일치하지 않습니다.")
                    catalog = deepcopy(package["runtime_catalog"])
                    revision = str(package["revision"])
                else:
                    catalog = _runtime_catalog(inline_value)
                    revision = "inline"
            elif mode == "v6_active":
                uri = _secret_text(getattr(self, "mongo_uri", "")) or os.getenv("MONGODB_URI", "").strip()
                if not uri:
                    raise ContractError("metadata_dependency_error", "domain_bundle", "v6_active mode에는 MongoDB URI가 필요합니다.")
                try:
                    from pymongo import MongoClient
                except ImportError as exc:
                    raise ContractError("metadata_dependency_error", "domain_bundle", "pymongo를 사용할 수 없습니다.") from exc
                client = MongoClient(uri, serverSelectionTimeoutMS=max(500, min(int(getattr(self, "mongo_timeout_ms", 5000)), 30000)))
                database = client[str(getattr(self, "mongo_database", "") or os.getenv("MONGODB_DATABASE", "datagov"))]
                package = load_active_domain_bundle(
                    database,
                    domain_id,
                    environment,
                    active_collection=str(getattr(self, "active_collection", "agent_v6_metadata_active")),
                    bundle_collection=str(getattr(self, "bundle_collection", "agent_v6_metadata_bundles")),
                )
                catalog = deepcopy(package["runtime_catalog"])
                revision = str(package["revision"])
            else:
                raise ContractError("metadata_dependency_error", "domain_bundle", "지원하지 않는 metadata source mode입니다.")
            catalog = _validate_catalog(catalog)
            context["domain_bundle"] = {
                "contract_version": "domain.bundle.runtime.v1",
                "domain_id": domain_id,
                "environment": environment,
                "revision": revision,
                "source_mode": source,
                "catalog_sha256": str(catalog.get("catalog_sha256") or sha256_json(catalog)),
                "runtime_catalog": catalog,
            }
            if isinstance(package, dict):
                context["domain_bundle"].update(
                    {"package_sha256": package.get("package_sha256"), "bundle_sha256": package.get("bundle_sha256")}
                )
        except Exception as exc:
            context = _pipeline_error(context, exc, "domain_bundle")
        return Data(data=context)
'''


CANDIDATE_ROUTE_COMPONENT = r'''
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema.data import Data


class CandidateRouteGate(Component):
    display_name = "의도 후보 및 분기 판정"
    description = "질문과 등록 메타데이터를 바탕으로 허용된 의도 후보와 LLM 호출 여부를 결정론적으로 계산합니다."
    icon = "route"
    metadata = {"logical_stage": "candidate_route"}
    inputs = [
        DataInput(name="request_context", display_name="검증된 요청 컨텍스트", required=True, info="질문 원문, 세션 상태, 기준 시각이 검증된 요청 정보입니다."),
        DataInput(name="domain_bundle", display_name="도메인 실행 번들", required=True, info="후보 생성에 사용할 승인된 데이터셋·필드·지표 정의입니다."),
    ]
    outputs = [Output(name="selection_context", display_name="의도 후보 및 분기 컨텍스트", method="select_route", types=["Data"])]

    def select_route(self) -> Data:
        current = _payload(getattr(self, "request_context", None))
        try:
            current = _require_context(current, "candidate_route")
            if not current.get("ok"):
                return Data(data=current)
            domain = _require_context(getattr(self, "domain_bundle", None), "candidate_route")
            if not domain.get("ok"):
                merged = deepcopy(current)
                merged.update({"ok": False, "stage": domain.get("stage"), "error": domain.get("error")})
                return Data(data=merged)
            catalog = (domain.get("domain_bundle") or {}).get("runtime_catalog")
            request = current["request"]
            planner_profile = _planner_profile(catalog)
            if planner_profile == "generic_v2":
                bundle = build_generic_v2_candidate_bundle(
                    request,
                    catalog,
                    prior_semantics=current.get("prior_semantics") or {},
                    prior_result=current.get("prior_result") or {},
                )
                validate_generic_v2_candidate_bundle(bundle, catalog=catalog)
                validate_contract(bundle, "resolved-candidate-bundle.schema.json", stage="candidate_bundle_contract")
                candidate_lane = "generic_v2"
            else:
                planning_catalog = EMBEDDED_RUNTIME_CATALOG if planner_profile == "legacy_v1_compat" else catalog
                bundle = build_candidate_bundle(request, planning_catalog, prior_semantics=current.get("prior_semantics") or {}, prior_result=current.get("prior_result") or {})
                candidate_lane = planner_profile
            route = bundle.get("route_decision") if isinstance(bundle.get("route_decision"), dict) else {}
            validate_contract(route, "analysis-route.schema.json", stage="route_contract")
            current.update(
                {
                    "stage": "candidate_route",
                    "candidate_bundle": bundle,
                    "candidate_lane": candidate_lane,
                    "domain_identity": {key: (domain.get("domain_bundle") or {}).get(key) for key in ("domain_id", "environment", "revision", "catalog_sha256", "package_sha256", "bundle_sha256")},
                    "domain_prompt_extensions": {
                        "intent": str(((catalog.get("prompt_extensions") or {}).get("intent") or "")).encode("utf-8")[:8192].decode("utf-8", errors="ignore"),
                        "answer": str(((catalog.get("prompt_extensions") or {}).get("answer") or "")).encode("utf-8")[:8192].decode("utf-8", errors="ignore"),
                    },
                    "route_telemetry": {
                        "route": route.get("route"),
                        "reason_code": route.get("reason_code"),
                        "intent_llm_calls": 0,
                        "fallback_used": False,
                        "planner_profile": planner_profile,
                        "eligibility_proof_sha256": route.get("eligibility_proof_sha256"),
                    },
                }
            )
        except Exception as exc:
            current = _pipeline_error(current, exc, "candidate_route")
        return Data(data=current)
'''


INTENT_PROMPT_CONTEXT_COMPONENT = r'''
import json

from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema.data import Data
from lfx.schema.message import Message


class IntentPromptContextBuilder(Component):
    display_name = "의도 분석 프롬프트 컨텍스트"
    description = "등록 후보와 질문만 bounded runtime context로 만들고 도메인 특화 지침을 별도 Message로 분리합니다."
    icon = "braces"
    metadata = {"logical_stage": "intent_prompt_context"}
    inputs = [DataInput(name="selection_context", display_name="후보 및 분기 컨텍스트", required=True, info="결정론적으로 계산된 의도 후보와 LLM 호출 필요 여부가 담긴 컨텍스트입니다.")]
    outputs = [
        Output(name="intent_prompt_context", display_name="의도 분석 실행 컨텍스트", method="build_context", types=["Data"]),
        Output(name="intent_specialized_prompt_text", display_name="의도 분석 특화 프롬프트 원문", method="build_specialized_text", types=["Message"]),
    ]

    def _selection(self):
        current = _require_context(getattr(self, "selection_context", None), "intent_prompt_context")
        return current

    def build_context(self) -> Data:
        current = self._selection()
        route = (current.get("candidate_bundle") or {}).get("route_decision") or {}
        route_name = str(route.get("route") or "")
        variables = (
            {
                "question": str((current.get("request") or {}).get("question") or ""),
                "candidate_cards": list((current.get("candidate_bundle") or {}).get("prompt_cards") or []),
                "route_reason": str(route.get("reason_code") or ""),
            }
            if current.get("ok")
            else {"upstream_error_code": str((current.get("error") or {}).get("code") or "pipeline_error")}
        )
        encoded = json.dumps(variables, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(encoded) > 28 * 1024:
            raise ContractError("metadata_budget_exceeded", "intent_prompt_context", "의도 분석 runtime context가 28KB를 초과했습니다.")
        return Data(
            data={
                "contract_version": "prompt.runtime-context.v1",
                "purpose": "intent_selection",
                "invoke": bool(current.get("ok")) and route_name == "intent_llm",
                "variables": variables,
            }
        )

    def build_specialized_text(self) -> Message:
        current = self._selection()
        text = str(((current.get("domain_prompt_extensions") or {}).get("intent") or "")) if current.get("ok") else ""
        text = text.encode("utf-8")[:8192].decode("utf-8", errors="ignore")
        return Message(text=text)
'''


INTENT_RESOLVER_COMPONENT = r'''
import json
import re

from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema.data import Data


def _intent_selection_id(response_text):
    raw = str(response_text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I | re.S).strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError("intent_contract_error", "intent_decoding", "Intent LLM 응답 JSON이 올바르지 않습니다.") from exc
    if not isinstance(value, dict) or set(value) != {"intent_candidate_id"}:
        raise ContractError("intent_contract_error", "intent_decoding", "Intent LLM 응답은 intent_candidate_id 하나만 포함해야 합니다.")
    selected = str(value.get("intent_candidate_id") or "").strip()
    if not selected:
        raise ContractError("intent_contract_error", "intent_decoding", "Intent LLM candidate 선택값이 비어 있습니다.")
    return selected


class CommonIntentResolver(Component):
    display_name = "공통 의도 결과 검증기"
    description = "외부 조건부 LLM 결과 또는 결정론적 후보를 동일한 closed semantic intent로 검증합니다."
    icon = "brain-circuit"
    metadata = {"logical_stage": "intent_resolution"}
    inputs = [
        DataInput(name="selection_context", display_name="후보 및 분기 컨텍스트", required=True, info="허용된 의도 후보와 분기 판정 근거가 담긴 컨텍스트입니다."),
        DataInput(name="intent_invocation_result", display_name="의도 LLM 호출 결과", required=True, info="외부 조건부 LLM 노드가 반환한 후보 ID입니다. LLM을 건너뛴 경우에도 호출 횟수 0인 결과를 연결합니다."),
    ]
    outputs = [Output(name="intent_context", display_name="검증된 의도 컨텍스트", method="resolve", types=["Data"])]

    def resolve(self) -> Data:
        current = _payload(getattr(self, "selection_context", None))
        try:
            current = _require_context(current, "intent_resolution")
            if not current.get("ok"):
                return Data(data=current)
            route = (current.get("candidate_bundle") or {}).get("route_decision") or {}
            route_name = str(route.get("route") or "")
            invocation = _payload(getattr(self, "intent_invocation_result", None))
            selected_id = None
            calls = 0
            if route_name == "intent_llm":
                if (
                    invocation.get("contract_version") != "llm.invocation.v1"
                    or invocation.get("purpose") != "intent_selection"
                    or invocation.get("status") != "ok"
                    or int(invocation.get("llm_calls") or 0) != 1
                ):
                    raise ContractError("intent_contract_error", "intent_llm", "검증된 Intent LLM 1회 호출 결과가 필요합니다.")
                selected_id = _intent_selection_id(invocation.get("response_text"))
                calls = 1
            else:
                if invocation and int(invocation.get("llm_calls") or 0) != 0:
                    raise ContractError("intent_contract_error", "intent_llm", "비 LLM 분기에서 Intent LLM이 호출되었습니다.")
            if current.get("candidate_lane") == "generic_v2":
                intent = normalize_generic_v2_intent(
                    current["request"],
                    current["candidate_bundle"],
                    selected_candidate_id=selected_id,
                )
                telemetry = {
                    "route": route_name,
                    "reason_code": route.get("reason_code"),
                    "intent_llm_calls": calls,
                    "fallback_used": False,
                    "eligibility_proof_sha256": route.get("eligibility_proof_sha256"),
                }
            else:
                intent, telemetry = normalize_intent_selection(
                    current["request"],
                    current["candidate_bundle"],
                    selected_candidate_id=selected_id,
                    intent_llm_calls=calls,
                )
            telemetry["planner_profile"] = str(current.get("candidate_lane") or "")
            validate_contract(intent, "semantic-intent.schema.json", stage="intent_contract")
            current.update({"stage": "intent_resolution", "intent": intent, "route_telemetry": telemetry})
        except Exception as exc:
            current = _pipeline_error(current, exc, "intent_resolution")
        return Data(data=current)
'''


PLAN_COMPILER_COMPONENT = r'''
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema.data import Data


class PlanCompilerValidator(Component):
    display_name = "실행 계획 컴파일 및 검증"
    description = "검증된 의미 의도를 허용된 연산자로만 구성된 불변 Typed Execution IR로 컴파일하고 계약을 검증합니다."
    icon = "list-checks"
    metadata = {"logical_stage": "plan_compilation"}
    inputs = [
        DataInput(name="intent_context", display_name="검증된 의도 컨텍스트", required=True, info="허용된 후보 중 하나로 확정되고 계약 검증을 통과한 의미 의도입니다."),
        DataInput(name="domain_bundle", display_name="도메인 실행 번들", required=True, info="계획 컴파일 시 사용할 승인된 데이터셋·필드·지표 및 연산 규칙입니다."),
    ]
    outputs = [Output(name="plan_context", display_name="검증된 실행 계획 컨텍스트", method="compile", types=["Data"])]

    def compile(self) -> Data:
        current = _payload(getattr(self, "intent_context", None))
        try:
            current = _require_context(current, "plan_compilation")
            if not current.get("ok"):
                return Data(data=current)
            domain = _require_context(getattr(self, "domain_bundle", None), "plan_compilation")
            if not domain.get("ok"):
                raise ContractError("metadata_dependency_error", "plan_compilation", "domain bundle을 사용할 수 없습니다.")
            catalog = (domain.get("domain_bundle") or {}).get("runtime_catalog")
            planner_profile = str(current.get("candidate_lane") or _planner_profile(catalog))
            if planner_profile == "generic_v2":
                plan = validate_generic_v2_plan(
                    compile_generic_v2_plan(
                        current["intent"],
                        current["candidate_bundle"],
                        catalog,
                        prior_result=current.get("prior_result") or {},
                        question=str((current.get("request") or {}).get("question") or ""),
                    ),
                    catalog,
                )
            else:
                planning_catalog = EMBEDDED_RUNTIME_CATALOG if planner_profile == "legacy_v1_compat" else catalog
                plan = validate_plan(
                    compile_plan(current["intent"], current["candidate_bundle"], planning_catalog, prior_result=current.get("prior_result") or {}),
                    planning_catalog,
                )
            validate_contract(plan, "analysis-plan.schema.json", stage="plan_contract")
            current.update({"stage": "plan_compilation", "plan": plan})
            current.pop("candidate_bundle", None)
        except Exception as exc:
            current = _pipeline_error(current, exc, "plan_compilation")
        return Data(data=current)
'''


JOB_ROUTER_COMPONENT = r'''
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, DropdownInput, Output
from lfx.schema.data import Data


class RetrievalJobRouter(Component):
    display_name = "데이터 조회 작업 분기"
    description = "실행 계획에 포함된 최소 조회 작업만 선택된 더미·인라인·실데이터 경로로 전달합니다."
    icon = "split"
    metadata = {"logical_stage": "job_routing"}
    inputs = [
        DataInput(name="plan_context", display_name="검증된 실행 계획 컨텍스트", required=True, info="데이터 조회 작업이 포함된 검증 완료 Typed Execution IR입니다."),
        DropdownInput(name="data_mode", display_name="데이터 조회 방식", options=["dummy", "inline", "live"], value="dummy", info="검증용 더미 데이터, 전달된 인라인 데이터, 외부 도구가 조회한 실데이터 중 하나를 선택합니다."),
    ]
    outputs = [Output(name="job_bundle", display_name="조회 작업 묶음", method="route_jobs", types=["Data"])]

    def route_jobs(self) -> Data:
        current = _payload(getattr(self, "plan_context", None))
        try:
            current = _require_context(current, "job_routing")
            if not current.get("ok"):
                return Data(data=current)
            mode = str(getattr(self, "data_mode", "dummy") or "dummy")
            jobs = deepcopy((current.get("plan") or {}).get("retrieval_jobs") or [])
            candidate_lane = str(current.get("candidate_lane") or "")
            if candidate_lane not in {"legacy_v1", "legacy_v1_compat", "generic_v2"}:
                raise ContractError(
                    "plan_contract_error",
                    "job_routing",
                    "A closed candidate lane is required before retrieval routing.",
                    {"candidate_lane": candidate_lane},
                )
            return Data(data={
                "contract_version": PIPELINE_VERSION,
                "ok": True,
                "stage": "job_routing",
                "data_mode": mode,
                "candidate_lane": candidate_lane,
                "jobs": jobs,
            })
        except Exception as exc:
            return Data(data=_pipeline_error(current, exc, "job_routing"))
'''


DUMMY_RETRIEVER_COMPONENT = r'''
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema.data import Data


class DummySourceRetriever(Component):
    display_name = "검증용 더미 데이터 조회"
    description = "테스트와 검증 환경에서만 실행 계획에 맞는 결정론적 더미 원천 결과를 생성합니다."
    icon = "database-zap"
    metadata = {"logical_stage": "dummy_retrieval"}
    inputs = [
        DataInput(name="job_bundle", display_name="조회 작업 묶음", required=True, info="선택된 데이터 경로와 최소 조회 조건이 포함된 작업 묶음입니다."),
        DataInput(name="domain_bundle", display_name="도메인 실행 번들", required=True, info="더미 행을 생성하고 결과 계약을 검증할 도메인 메타데이터입니다."),
    ]
    outputs = [Output(name="dummy_results", display_name="더미 원천 조회 결과", method="retrieve", types=["Data"])]

    def retrieve(self) -> Data:
        jobs = _payload(getattr(self, "job_bundle", None))
        lane = {"contract_version": PIPELINE_VERSION, "ok": True, "stage": "dummy_retrieval", "lane": "dummy", "status": "skipped", "source_results": []}
        try:
            jobs = _require_context(jobs, "dummy_retrieval")
            if not jobs.get("ok"):
                return Data(data=jobs)
            if jobs.get("data_mode") != "dummy":
                return Data(data=lane)
            domain = _require_context(getattr(self, "domain_bundle", None), "dummy_retrieval")
            if not domain.get("ok"):
                raise ContractError("metadata_dependency_error", "dummy_retrieval", "domain bundle을 사용할 수 없습니다.")
            active_catalog = (domain.get("domain_bundle") or {}).get("runtime_catalog")
            candidate_lane = str(jobs.get("candidate_lane") or "")
            embedded_hash = str(EMBEDDED_RUNTIME_CATALOG.get("catalog_sha256") or "")
            if candidate_lane == "legacy_v1":
                fixture_allowed = (
                    isinstance(active_catalog, dict)
                    and active_catalog.get("contract_version") == "metadata.runtime.catalog.v1"
                    and str(active_catalog.get("catalog_sha256") or "") == embedded_hash
                )
            elif candidate_lane == "legacy_v1_compat":
                profile = (
                    active_catalog.get("output_profile")
                    if isinstance(active_catalog, dict)
                    and isinstance(active_catalog.get("output_profile"), dict)
                    else {}
                )
                fixture_allowed = (
                    isinstance(active_catalog, dict)
                    and active_catalog.get("contract_version") == "metadata.runtime.catalog.v2"
                    and str(active_catalog.get("domain_id") or "") == "manufacturing"
                    and str(active_catalog.get("compiler_version") or "") in {
                        "metadata-domain-compiler.v6.2", "metadata-domain-compiler.v6.3"
                    }
                    and profile.get("planner_profile") == "legacy_v1_compat"
                    and str(profile.get("legacy_catalog_sha256") or "") == embedded_hash
                )
            else:
                fixture_allowed = False
            if not fixture_allowed:
                raise ContractError(
                    "source_missing",
                    "dummy_retrieval",
                    "The embedded manufacturing fixture is unavailable for this candidate lane or domain pin.",
                    {
                        "reason": "dummy_fixture_unavailable",
                        "candidate_lane": candidate_lane,
                    },
                )
            lane.update({
                "status": "selected",
                "source_results": source_results_for_jobs(
                    jobs.get("jobs") or [],
                    EMBEDDED_RUNTIME_CATALOG,
                ),
                "data_mode": "dummy",
                "candidate_lane": candidate_lane,
            })
        except Exception as exc:
            lane = _pipeline_error(lane, exc, "dummy_retrieval")
        return Data(data=lane)
'''


BOUNDED_RETRIEVER_HELPER = r'''
def _physical_schema(rows):
    return sorted({str(key) for row in rows for key in row}) if rows else []


def _comparable(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value)


def _filter_match(row, tree):
    if not isinstance(tree, dict) or not tree:
        return True
    connective = str(tree.get("op") or "")
    if connective in {"all", "any"}:
        matches = [_filter_match(row, clause) for clause in tree.get("clauses") or []]
        return all(matches) if connective == "all" else any(matches)
    field = str(tree.get("field") or "")
    operator = str(tree.get("operator") or tree.get("op") or "eq")
    actual, expected = row.get(field), tree.get("value")
    values = tree.get("values") if isinstance(tree.get("values"), list) else expected if isinstance(expected, list) else []
    if operator == "eq": return actual == expected
    if operator == "ne": return actual != expected
    if operator == "in": return actual in values
    if operator == "not_in": return actual not in values
    if operator in {"gt", "gte", "lt", "lte"}:
        left, right = _comparable(actual), _comparable(expected)
        if left is None or right is None or type(left) is not type(right): return False
        return {"gt": left > right, "gte": left >= right, "lt": left < right, "lte": left <= right}[operator]
    text, target = "" if actual is None else str(actual), "" if expected is None else str(expected)
    if operator == "starts_with": return text.startswith(target)
    if operator == "ends_with": return text.endswith(target)
    if operator == "contains": return target in text
    if operator == "is_null": return actual is None
    if operator == "is_not_null": return actual is not None
    if operator == "is_blank": return actual is None or not text.strip()
    if operator == "is_not_blank": return actual is not None and bool(text.strip())
    if operator == "null_or_blank": return actual is None or not text.strip()
    raise ContractError("source_contract_error", "retrieval", "Unsupported retrieval filter operator.", {"operator": operator})


def _parameter_match(row, job, catalog):
    parameters = job.get("parameters") if isinstance(job.get("parameters"), dict) else {}
    dataset = (catalog.get("datasets") or {}).get(str(job.get("dataset_key") or "")) or {}
    date_policy = dataset.get("date_policy") if isinstance(dataset.get("date_policy"), dict) else {}
    date_field = str(date_policy.get("field") or "")
    for name, expected in parameters.items():
        upper = str(name).upper()
        field = str(name) if str(name) in row else date_field if upper in {"DATE", "DATE_FROM", "DATE_TO"} else ""
        if not field:
            raise ContractError("source_contract_error", "retrieval", "Adapter parameter cannot be proven against rows.", {"parameter": name})
        actual = row.get(field)
        if upper.endswith("_FROM") and (actual is None or str(actual) < str(expected)): return False
        if upper.endswith("_TO") and (actual is None or str(actual) > str(expected)): return False
        if not upper.endswith(("_FROM", "_TO")) and actual != expected and str(actual) != str(expected): return False
    return True


def _project_physical(row, job, catalog):
    dataset = (catalog.get("datasets") or {}).get(str(job.get("dataset_key") or "")) or {}
    bindings = dataset.get("fields") or {}
    projected = {}
    for field in job.get("required_fields") or []:
        binding = bindings.get(str(field)) or {}
        candidates = [str(binding.get("physical_column") or ""), *[str(item) for item in binding.get("physical_aliases") or []]]
        present = next((name for name in candidates if name and name in row), None)
        if present is not None:
            projected[present] = row[present]
    return projected


def _source_rows(payload, job, catalog, max_rows, max_bytes):
    job_id = str(job.get("job_id") or "")
    dataset_key = str(job.get("dataset_key") or "")
    value = None
    for container_name, lookup in (("jobs", job_id), ("datasets", dataset_key)):
        container = payload.get(container_name)
        if isinstance(container, dict) and lookup in container:
            value = container[lookup]
            break
    if value is None and dataset_key in payload:
        value = payload[dataset_key]
    if value is None and isinstance(payload.get("rows"), list):
        value = payload.get("rows")
    if isinstance(value, dict) and isinstance(value.get("rows"), list):
        value = value.get("rows")
    if value is None:
        raise ContractError("source_missing", "retrieval", "승인된 physical source rows가 제공되지 않았습니다.", {"job_id": job_id, "dataset_key": dataset_key})
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ContractError("source_contract_error", "retrieval", "source rows는 object 배열이어야 합니다.")
    if len(value) > max_rows:
        raise ContractError("source_row_limit_exceeded", "retrieval", "source row limit을 초과했습니다.", {"limit": max_rows})
    rows = deepcopy(value)
    if len(canonical_bytes(rows)) > max_bytes:
        raise ContractError("executor_memory_limit_exceeded", "retrieval", "source payload memory limit을 초과했습니다.", {"limit_bytes": max_bytes})
    required_fields = [str(field) for field in job.get("required_fields") or []]
    canonical_rows, _ = canonicalize_rows(
        dataset_key,
        rows,
        catalog,
        physical_schema=_physical_schema(rows),
        required_fields=required_fields,
    )
    selected = [
        _project_physical(physical, job, catalog)
        for physical, canonical in zip(rows, canonical_rows, strict=True)
        if _parameter_match(canonical, job, catalog) and _filter_match(canonical, job.get("filters") or {})
    ]
    if len(canonical_bytes(selected)) > max_bytes:
        raise ContractError("executor_memory_limit_exceeded", "retrieval", "Projected source payload exceeds the configured limit.", {"limit_bytes": max_bytes})
    return selected


def _physical_result(job, rows, source_type):
    dataset_key = str(job.get("dataset_key") or "")
    alias = str(job.get("source_alias") or job.get("job_id") or dataset_key)
    content_hash = sha256_json(rows)
    return {
        "contract_version": "source.result.v1",
        "source_result_id": f"{source_type}:{job.get('job_id') or alias}:{content_hash[:16]}",
        "source_alias": alias,
        "dataset_key": dataset_key,
        "source_type": source_type,
        "status": "ok" if rows else "empty",
        "physical_schema": _physical_schema(rows),
        "rows": rows,
        "row_count": len(rows),
        "chunk_index": 0,
        "chunk_count": 1,
        "truncated": False,
        "row_set_complete": True,
        "content_sha256": content_hash,
        "applied_parameters": deepcopy(job.get("parameters") or {}),
        "applied_filters_sha256": sha256_json(job.get("filters") or {}),
    }
'''


CATALOG_VALIDATOR_DISPATCH = r'''
_validate_runtime_catalog_v1 = validate_runtime_catalog


def validate_runtime_catalog(catalog):
    if isinstance(catalog, dict) and catalog.get("contract_version") == "metadata.runtime.catalog.v2":
        return validate_runtime_catalog_v2(catalog)
    return _validate_runtime_catalog_v1(catalog)
'''


INLINE_RETRIEVER_COMPONENT = r'''
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, IntInput, NestedDictInput, Output
from lfx.schema.data import Data


class InlineSourceRetriever(Component):
    display_name = "인라인 데이터 조회"
    description = "이미 승인되어 전달된 인라인 행을 크기 제한과 계약 검증을 거쳐 표준 원천 결과로 변환합니다."
    icon = "rows-3"
    metadata = {"logical_stage": "inline_retrieval"}
    inputs = [
        DataInput(name="job_bundle", display_name="조회 작업 묶음", required=True, info="선택된 데이터 경로와 최소 조회 조건이 포함된 작업 묶음입니다."),
        DataInput(name="domain_bundle", display_name="도메인 실행 번들", required=True, info="인라인 행의 데이터셋·필드 계약을 검증할 도메인 메타데이터입니다."),
        NestedDictInput(
            name="source_payload",
            display_name="인라인 원천 데이터",
            value={},
            required=False,
            info="데이터셋별 승인된 원천 행을 직접 전달합니다. 실행 계획에 없는 데이터는 사용되지 않습니다.",
        ),
        IntInput(name="source_row_limit", display_name="원천 행 수 제한", value=50000, info="인라인 원천에서 허용할 최대 전체 행 수입니다."),
        IntInput(name="source_memory_limit_mb", display_name="원천 메모리 제한(MiB)", value=64, info="인라인 원천 payload에 허용할 최대 메모리 크기입니다."),
    ]
    outputs = [Output(name="inline_results", display_name="인라인 원천 조회 결과", method="retrieve", types=["Data"])]

    def retrieve(self) -> Data:
        jobs = _payload(getattr(self, "job_bundle", None))
        lane = {"contract_version": PIPELINE_VERSION, "ok": True, "stage": "inline_retrieval", "lane": "inline", "status": "skipped", "source_results": []}
        try:
            jobs = _require_context(jobs, "inline_retrieval")
            if not jobs.get("ok"):
                return Data(data=jobs)
            if jobs.get("data_mode") != "inline":
                return Data(data=lane)
            domain = _require_context(getattr(self, "domain_bundle", None), "inline_retrieval")
            catalog = (domain.get("domain_bundle") or {}).get("runtime_catalog")
            payload = _payload(getattr(self, "source_payload", None))
            max_rows = max(1, min(int(getattr(self, "source_row_limit", 50000)), 100000))
            max_bytes = max(1, min(int(getattr(self, "source_memory_limit_mb", 64)), 512)) * 1024 * 1024
            results = [_physical_result(job, _source_rows(payload, job, catalog, max_rows, max_bytes), "trusted_inline") for job in jobs.get("jobs") or []]
            lane.update({"status": "selected", "source_results": results, "data_mode": "inline"})
        except Exception as exc:
            lane = _pipeline_error(lane, exc, "inline_retrieval")
        return Data(data=lane)
'''


LIVE_RETRIEVER_COMPONENT = r'''
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, IntInput, NestedDictInput, Output, StrInput
from lfx.schema.data import Data


class LiveSourceRetriever(Component):
    display_name = "실데이터 조회 결과 수신"
    description = "별도 Oracle·API·데이터레이크 도구가 조회한 행을 신뢰 경계에서 받아 크기와 계약을 검증합니다."
    icon = "radio-tower"
    metadata = {"logical_stage": "live_retrieval"}
    inputs = [
        DataInput(name="job_bundle", display_name="조회 작업 묶음", required=True, info="외부 데이터 도구가 수행해야 할 최소 조회 조건과 선택 경로입니다."),
        DataInput(name="domain_bundle", display_name="도메인 실행 번들", required=True, info="수신한 실데이터의 데이터셋·필드 계약을 검증할 도메인 메타데이터입니다."),
        NestedDictInput(
            name="source_payload",
            display_name="실데이터 어댑터 결과",
            value={},
            required=False,
            info="검토된 외부 조회 도구가 데이터셋별로 반환한 원천 행입니다.",
        ),
        StrInput(name="adapter_id", display_name="승인된 어댑터 ID", value="external_source_tools", info="실데이터를 조회한 서버 측 검토 완료 어댑터 식별자입니다."),
        IntInput(name="source_row_limit", display_name="원천 행 수 제한", value=50000, info="수신할 수 있는 최대 전체 원천 행 수입니다."),
        IntInput(name="source_memory_limit_mb", display_name="원천 메모리 제한(MiB)", value=64, info="실데이터 payload에 허용할 최대 메모리 크기입니다."),
    ]
    outputs = [Output(name="live_results", display_name="검증된 실데이터 조회 결과", method="retrieve", types=["Data"])]

    def retrieve(self) -> Data:
        jobs = _payload(getattr(self, "job_bundle", None))
        lane = {"contract_version": PIPELINE_VERSION, "ok": True, "stage": "live_retrieval", "lane": "live", "status": "skipped", "source_results": []}
        try:
            jobs = _require_context(jobs, "live_retrieval")
            if not jobs.get("ok"):
                return Data(data=jobs)
            if jobs.get("data_mode") != "live":
                return Data(data=lane)
            domain = _require_context(getattr(self, "domain_bundle", None), "live_retrieval")
            catalog = (domain.get("domain_bundle") or {}).get("runtime_catalog")
            payload = _payload(getattr(self, "source_payload", None))
            max_rows = max(1, min(int(getattr(self, "source_row_limit", 50000)), 100000))
            max_bytes = max(1, min(int(getattr(self, "source_memory_limit_mb", 64)), 512)) * 1024 * 1024
            adapter_id = str(getattr(self, "adapter_id", "") or "external_source_tools")
            results = [_physical_result(job, _source_rows(payload, job, catalog, max_rows, max_bytes), f"live:{adapter_id}") for job in jobs.get("jobs") or []]
            lane.update({"status": "selected", "source_results": results, "data_mode": "live"})
        except Exception as exc:
            lane = _pipeline_error(lane, exc, "live_retrieval")
        return Data(data=lane)
'''


SOURCE_MERGER_COMPONENT = r'''
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, IntInput, Output
from lfx.schema.data import Data


class SourceContractMerger(Component):
    display_name = "원천 결과 계약 병합"
    description = "선택된 데이터 경로의 결과만 표준화하고 Typed IR 실행기가 소비하는 프레임으로 변환합니다."
    icon = "combine"
    metadata = {"logical_stage": "source_merge"}
    inputs = [
        DataInput(name="plan_context", display_name="검증된 실행 계획 컨텍스트", required=True, info="선택된 조회 작업과 Typed Execution IR이 포함된 컨텍스트입니다."),
        DataInput(name="domain_bundle", display_name="도메인 실행 번들", required=True, info="원천 결과를 표준화할 데이터셋·필드 계약입니다."),
        DataInput(name="dummy_results", display_name="더미 원천 조회 결과", required=True, info="더미 경로가 선택되지 않았으면 skipped 상태로 연결합니다."),
        DataInput(name="inline_results", display_name="인라인 원천 조회 결과", required=True, info="인라인 경로가 선택되지 않았으면 skipped 상태로 연결합니다."),
        DataInput(name="live_results", display_name="실데이터 원천 조회 결과", required=True, info="실데이터 경로가 선택되지 않았으면 skipped 상태로 연결합니다."),
        IntInput(name="peak_payload_limit_mb", display_name="병합 payload 제한(MB)", value=128, info="병합된 실행 프레임에 허용할 최대 payload 크기입니다."),
    ]
    outputs = [Output(name="execution_context", display_name="Typed IR 실행 컨텍스트", method="merge", types=["Data"])]

    def merge(self) -> Data:
        current = _payload(getattr(self, "plan_context", None))
        try:
            current = _require_context(current, "source_merge")
            if not current.get("ok"):
                return Data(data=current)
            domain = _require_context(getattr(self, "domain_bundle", None), "source_merge")
            catalog = (domain.get("domain_bundle") or {}).get("runtime_catalog")
            lanes = {name: _payload(getattr(self, f"{name}_results", None)) for name in ("dummy", "inline", "live")}
            selected = next((value for value in lanes.values() if value.get("status") == "selected"), None)
            jobs = (current.get("plan") or {}).get("retrieval_jobs") or []
            if jobs and not selected:
                failed = next((value for value in lanes.values() if value.get("ok") is False), None)
                if failed:
                    current.update({"ok": False, "stage": failed.get("stage"), "error": failed.get("error")})
                    return Data(data=current)
                raise ContractError("source_missing", "source_merge", "선택된 source lane 결과가 없습니다.")
            source_results = (selected or {}).get("source_results") or []
            if source_results:
                bundle = merge_source_results(source_results, catalog, retrieval_jobs=jobs)
                # The immutable source bundle owns row lists.  Executor frame
                # descriptors share those lists until pandas materialization;
                # no second full-row deepcopy is retained in the pipeline.
                snapshots = list(bundle.get("frames", {}).values())
                payload_bytes = sum(len(canonical_bytes(item.get("rows") or [])) for item in snapshots)
                payload_limit = max(1, min(int(getattr(self, "peak_payload_limit_mb", 128)), 512)) * 1024 * 1024
                if payload_bytes > payload_limit:
                    raise ContractError(
                        "executor_memory_limit_exceeded",
                        "source_merge",
                        "Merged source payload exceeds the configured budget.",
                        {"payload_bytes": payload_bytes, "limit_bytes": payload_limit},
                    )
                frames = executor_frames(bundle, catalog, copy_rows=False)
                diagnostics = [
                    {
                        "job_id": item.get("source_alias"),
                        "dataset_key": item.get("dataset_key"),
                        "status": item.get("status"),
                        "row_count": item.get("row_count"),
                        "content_sha256": item.get("canonical_content_sha256"),
                    }
                    for item in bundle.get("source_manifest", [])
                ]
            else:
                frames, snapshots, diagnostics, payload_bytes = {}, [], [], 0
            if "previous" in ((current.get("plan") or {}).get("input_refs") or []):
                prior = current.get("prior_result") or {}
                frames["previous"] = {"rows": deepcopy(prior.get("rows") or [])}
            current.update(
                {
                    "stage": "source_merge",
                    "frames": frames,
                    "source_snapshots": snapshots,
                    "source_diagnostics": diagnostics,
                    "payload_telemetry": {
                        "source_row_bytes": payload_bytes,
                        "row_copy_count": 1,
                        "raw_rows_in_llm_prompt": False,
                    },
                    "data_mode": str((selected or {}).get("data_mode") or "dummy"),
                }
            )
        except Exception as exc:
            current = _pipeline_error(current, exc, "source_merge")
        return Data(data=current)
'''


TYPED_EXECUTOR_COMPONENT = r'''
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, IntInput, Output
from lfx.schema.data import Data


class TypedExecutorPublisher(Component):
    display_name = "Typed IR 실행 및 결과 발행"
    description = "등록된 타입 연산자 DAG만 결정론적으로 실행하고 해시가 포함된 불변 분석 결과를 발행합니다."
    icon = "play-circle"
    metadata = {"logical_stage": "typed_execution"}
    inputs = [
        DataInput(name="execution_context", display_name="Typed IR 실행 컨텍스트", required=True, info="검증된 실행 계획과 표준화된 데이터 프레임이 포함된 컨텍스트입니다."),
        IntInput(name="executor_row_limit", display_name="실행 결과 행 수 제한", value=100000, info="결정론적 실행기가 처리·발행할 수 있는 최대 행 수입니다."),
    ]
    outputs = [Output(name="result_context", display_name="불변 분석 결과 컨텍스트", method="execute", types=["Data"])]

    def execute(self) -> Data:
        current = _payload(getattr(self, "execution_context", None))
        try:
            current = _require_context(current, "typed_execution")
            if not current.get("ok"):
                return Data(data=current)
            limit = max(1, min(int(getattr(self, "executor_row_limit", 100000)), 100000))
            execution = TypedExecutor(max_rows=limit).execute(current["plan"], current.get("frames") or {})
            result = execution.as_contract(current["plan"])
            validate_contract(result, "analysis-result.schema.json", stage="result_contract")
            current.update({"stage": "typed_execution", "result": result})
            current.pop("frames", None)
            current.pop("prior_result", None)
            current.pop("prior_semantics", None)
        except Exception as exc:
            current = _pipeline_error(current, exc, "typed_execution")
        return Data(data=current)
'''


LEGACY_ANSWER_FACTS_COMPONENT = r'''
import json
import re

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, HandleInput, MultilineInput, Output
from lfx.schema.data import Data


def _model_text(value):
    if isinstance(value, str):
        return value
    for field in ("text", "content"):
        text = getattr(value, field, None)
        if isinstance(text, str):
            return text
    return str(value or "")


def _json_object(text):
    raw = str(text or "").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0].strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < start:
        raise ValueError("narrative JSON object missing")
    value = json.loads(raw[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("narrative response must be object")
    return value


class AnswerFactsNarrative(Component):
    display_name = "Answer Facts + Optional Narrative"
    description = "deterministic facts를 만들고 선택적으로만 bounded narrative를 생성한 뒤 claim을 검증합니다."
    icon = "text-quote"
    metadata = {"logical_stage": "answer_facts", "logical_capabilities": ["answer_facts", "narrative_claim"]}
    inputs = [
        DataInput(name="result_context", display_name="Result Context", required=True),
        HandleInput(name="language_model", display_name="Answer Language Model", input_types=["LanguageModel"], required=False),
        BoolInput(name="narrative_enabled", display_name="Enable Answer Narrative", value=False),
        MultilineInput(name="answer_prompt_extension", display_name="Answer Prompt Extension", value="", required=False),
    ]
    outputs = [Output(name="answer_context", display_name="Answer Context", method="build_answer", types=["Data"])]

    def build_answer(self) -> Data:
        current = _payload(getattr(self, "result_context", None))
        try:
            current = _require_context(current, "answer_facts")
            if not current.get("ok"):
                return Data(data=current)
            facts = build_answer_facts(current["request"], current["plan"], current["result"])
            narrative = {"attempted": False, "llm_calls": 0, "claim_status": "deterministic", "message": ""}
            if bool(getattr(self, "narrative_enabled", False)):
                model = getattr(self, "language_model", None)
                if model is None:
                    narrative.update({"attempted": True, "claim_status": "fallback", "notice": "Answer Language Model이 연결되지 않았습니다."})
                else:
                    narrative.update({"attempted": True, "llm_calls": 1})
                    source = {
                        "facts": facts,
                        "columns": current["result"].get("columns", []),
                        "rows": (current["result"].get("rows") or [])[:20],
                    }
                    domain_extension = str(((current.get("domain_prompt_extensions") or {}).get("answer") or ""))
                    node_extension = str(getattr(self, "answer_prompt_extension", "") or "")
                    domain_extension = domain_extension.encode("utf-8")[:8192].decode("utf-8", errors="ignore")
                    node_extension = node_extension.encode("utf-8")[:4096].decode("utf-8", errors="ignore")
                    extension = (
                        "[REGISTERED_DOMAIN_POLICY]\n" + domain_extension + "\n[NODE_POLICY_OVERLAY]\n" + node_extension
                    ).strip()
                    prompt = (
                        "Return one JSON object only: {\"message\":\"...\",\"fact_ids\":[\"fact:row_count\"]}. "
                        "Use only supplied facts/result rows. Do not change numbers, conditions, units, identifiers or claim facts that are absent. "
                        "The policy extension controls wording only.\nPOLICY_EXTENSION:\n"
                        + extension
                        + "\nFACT_PAYLOAD:\n"
                        + json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                    )
                    if len(prompt.encode("utf-8")) > 12 * 1024:
                        raise ContractError("answer_claim_violation", "answer_facts", "Answer LLM payload budget을 초과했습니다.")
                    try:
                        draft = _json_object(_model_text(model.invoke(prompt)))
                        message = str(draft.get("message") or "").strip()
                        fact_ids = draft.get("fact_ids") if isinstance(draft.get("fact_ids"), list) else []
                        allowed_ids = {str(item.get("fact_id")) for item in facts.get("facts", [])}
                        allowed_text = json.dumps(source, ensure_ascii=False, sort_keys=True)
                        numeric_claims = set(re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", message))
                        if not message or not set(map(str, fact_ids)).issubset(allowed_ids) or any(token not in allowed_text for token in numeric_claims):
                            raise ValueError("unverified narrative claim")
                        narrative.update({"claim_status": "verified", "message": message, "fact_ids": list(map(str, fact_ids))})
                    except Exception:
                        narrative.update({"claim_status": "fallback", "message": "", "notice": "Narrative claim 검증 실패로 deterministic 답변을 사용했습니다."})
            current.update({"stage": "answer_facts", "answer_facts": facts, "narrative": narrative})
        except Exception as exc:
            current = _pipeline_error(current, exc, "answer_facts")
        return Data(data=current)
'''


ANSWER_FACTS_CONTEXT_COMPONENT = r'''
import json

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, Output
from lfx.schema.data import Data
from lfx.schema.message import Message


class AnswerFactsContextBuilder(Component):
    display_name = "답변 사실 및 프롬프트 컨텍스트"
    description = "실행 결과에서 검증 가능한 사실을 만들고, 선택적 답변 LLM에 전달할 제한된 컨텍스트와 도메인 특화 문구를 분리해 제공합니다."
    icon = "text-quote"
    metadata = {"logical_stage": "answer_facts_context", "logical_capabilities": ["answer_facts", "prompt_context"]}
    inputs = [
        DataInput(name="result_context", display_name="실행 결과 컨텍스트", required=True, info="Typed IR 실행 결과와 질문·계획·출처 정보가 결합된 검증 완료 컨텍스트입니다."),
        BoolInput(name="narrative_enabled", display_name="LLM 답변 문장 사용", value=False, info="활성화하면 결정론적 사실만 전달해 선택적으로 자연어 답변 문장을 생성합니다."),
    ]
    outputs = [
        Output(name="answer_facts_context", display_name="답변 사실 컨텍스트", method="build_facts_context", types=["Data"]),
        Output(name="answer_prompt_context", display_name="답변 LLM 실행 컨텍스트", method="build_prompt_context", types=["Data"]),
        Output(name="answer_specialized_prompt_text", display_name="답변 특화 프롬프트 원문", method="build_specialized_text", types=["Message"]),
    ]

    def _current_and_facts(self):
        current = _require_context(getattr(self, "result_context", None), "answer_facts_context")
        if not current.get("ok"):
            return current, None
        facts = build_answer_facts(current["request"], current["plan"], current["result"])
        return current, facts

    def build_facts_context(self) -> Data:
        current = _payload(getattr(self, "result_context", None))
        try:
            current, facts = self._current_and_facts()
            if not current.get("ok"):
                return Data(data=current)
            requested = bool(getattr(self, "narrative_enabled", False))
            current.update(
                {
                    "stage": "answer_facts_context",
                    "answer_facts": facts,
                    "narrative": {
                        "requested": requested,
                        "attempted": False,
                        "llm_calls": 0,
                        "claim_status": "pending" if requested else "deterministic",
                        "message": "",
                    },
                }
            )
        except Exception as exc:
            current = _pipeline_error(current, exc, "answer_facts_context")
        return Data(data=current)

    def build_prompt_context(self) -> Data:
        try:
            current, facts = self._current_and_facts()
            variables = (
                {"answer_facts": facts}
                if current.get("ok")
                else {"upstream_error_code": str((current.get("error") or {}).get("code") or "pipeline_error")}
            )
            encoded = json.dumps(variables, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            if len(encoded) > 12 * 1024:
                raise ContractError("metadata_budget_exceeded", "answer_prompt_context", "답변 LLM 컨텍스트가 12KB를 초과했습니다.")
            return Data(
                data={
                    "contract_version": "prompt.runtime-context.v1",
                    "purpose": "answer_narrative",
                    "invoke": bool(current.get("ok")) and bool(getattr(self, "narrative_enabled", False)),
                    "variables": variables,
                }
            )
        except Exception as exc:
            return Data(data=_pipeline_error({}, exc, "answer_prompt_context"))

    def build_specialized_text(self) -> Message:
        try:
            current, _ = self._current_and_facts()
            text = str(((current.get("domain_prompt_extensions") or {}).get("answer") or "")) if current.get("ok") else ""
            text = text.encode("utf-8")[:8192].decode("utf-8", errors="ignore")
            return Message(text=text)
        except Exception:
            return Message(text="")
'''


ANSWER_CLAIM_VALIDATOR_COMPONENT = r'''
import json
import re

from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema.data import Data


def _answer_json_object(text):
    raw = str(text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I | re.S).strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("answer narrative must be one valid JSON object") from exc
    if not isinstance(value, dict) or set(value) != {"message", "fact_ids"}:
        raise ValueError("answer narrative keys must be exactly message and fact_ids")
    return value


class AnswerClaimValidator(Component):
    display_name = "답변 문장 주장 검증기"
    description = "외부 Prompt/LLM 노드의 JSON 답변이 결정론적 사실만 인용하는지 검증하고, 실패하면 안전한 기본 답변으로 전환합니다."
    icon = "badge-check"
    metadata = {"logical_stage": "answer_claim_validation", "logical_capabilities": ["narrative_claim"]}
    inputs = [
        DataInput(name="answer_facts_context", display_name="답변 사실 컨텍스트", required=True, info="실행 결과에서 결정론적으로 추출한 인용 가능한 사실 목록입니다."),
        DataInput(name="answer_invocation_result", display_name="답변 LLM 호출 결과", required=True, info="외부 조건부 LLM이 생성한 메시지와 인용 사실 ID입니다. 비활성 시 호출 횟수 0인 결과를 연결합니다."),
    ]
    outputs = [Output(name="answer_context", display_name="검증된 답변 컨텍스트", method="validate_answer", types=["Data"])]

    def validate_answer(self) -> Data:
        current = _payload(getattr(self, "answer_facts_context", None))
        try:
            current = _require_context(current, "answer_claim_validation")
            if not current.get("ok"):
                return Data(data=current)
            narrative = current.get("narrative") if isinstance(current.get("narrative"), dict) else {}
            requested = bool(narrative.get("requested"))
            invocation = _payload(getattr(self, "answer_invocation_result", None))
            if not requested:
                if invocation and int(invocation.get("llm_calls") or 0) != 0:
                    raise ContractError("answer_claim_violation", "answer_llm", "비활성 답변 LLM이 호출되었습니다.")
                narrative.update({"attempted": False, "llm_calls": 0, "claim_status": "deterministic", "message": ""})
            elif (
                invocation.get("contract_version") == "llm.invocation.v1"
                and invocation.get("purpose") == "answer_narrative"
                and invocation.get("status") == "ok"
                and int(invocation.get("llm_calls") or 0) == 1
            ):
                try:
                    draft = _answer_json_object(invocation.get("response_text"))
                    message = str(draft.get("message") or "").strip()
                    fact_ids = draft.get("fact_ids") if isinstance(draft.get("fact_ids"), list) else []
                    facts = current.get("answer_facts") if isinstance(current.get("answer_facts"), dict) else {}
                    allowed_ids = {str(item.get("fact_id")) for item in facts.get("facts", []) if isinstance(item, dict)}
                    normalized_ids = [str(item) for item in fact_ids]
                    allowed_text = json.dumps(facts, ensure_ascii=False, sort_keys=True)
                    numeric_claims = set(re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", message))
                    if (
                        not message
                        or not normalized_ids
                        or not set(normalized_ids).issubset(allowed_ids)
                        or any(token not in allowed_text for token in numeric_claims)
                    ):
                        raise ValueError("unverified narrative claim")
                    narrative.update(
                        {
                            "attempted": True,
                            "llm_calls": 1,
                            "claim_status": "verified",
                            "message": message,
                            "fact_ids": normalized_ids,
                        }
                    )
                except Exception:
                    narrative.update(
                        {
                            "attempted": True,
                            "llm_calls": 1,
                            "claim_status": "fallback",
                            "message": "",
                            "notice": "LLM 답변의 사실 주장을 검증하지 못해 결정론적 기본 답변을 사용했습니다.",
                        }
                    )
            else:
                calls = max(0, int(invocation.get("llm_calls") or 0)) if isinstance(invocation, dict) else 0
                narrative.update(
                    {
                        "attempted": True,
                        "llm_calls": min(calls, 1),
                        "claim_status": "fallback",
                        "message": "",
                        "notice": "답변 LLM을 사용할 수 없어 결정론적 기본 답변을 사용했습니다.",
                    }
                )
            current.update({"stage": "answer_claim_validation", "narrative": narrative})
        except Exception as exc:
            current = _pipeline_error(current, exc, "answer_claim_validation")
        return Data(data=current)
'''


RESPONSE_COMMIT_COMPONENT = r'''
import builtins
import os

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, IntInput, Output, SecretStrInput, StrInput
from lfx.schema.data import Data


def _secret_text(value):
    if hasattr(value, "get_secret_value"):
        value = value.get_secret_value()
    return str(value or "").strip()


def _shared_memory_store():
    key = "_metadata_driven_v6_pipeline_state_store_v1"
    store = getattr(builtins, key, None)
    if store is None or not all(hasattr(store, name) for name in ("load_state", "load_ref", "commit_execution")):
        store = InMemoryStateStore()
        setattr(builtins, key, store)
    return store


def _executed_result(result, plan, source_snapshots):
    result_contract = plan.get("result_contract") if isinstance(plan.get("result_contract"), dict) else {}
    criteria = {
        str(job.get("job_id") or ""): {
            "dataset_key": job.get("dataset_key"),
            "parameters": deepcopy(job.get("parameters") or {}),
            "filters": deepcopy(job.get("filters") or {}),
        }
        for job in plan.get("retrieval_jobs", [])
        if isinstance(job, dict) and job.get("job_id")
    }
    material = {
        "contract_version": "executed.result.v1",
        "status": result.get("status"),
        "plan_id": result.get("plan_id"),
        "columns": deepcopy(result.get("columns") or []),
        "rows": deepcopy(result.get("rows") or []),
        "row_count": int(result.get("row_count") or 0),
        "lineage": deepcopy(result.get("lineage") or {}),
        "operation_trace": deepcopy(result.get("operation_trace") or []),
        "result_sha256": result.get("result_sha256"),
        "grain": deepcopy(result_contract.get("grain") or []),
        "entities": deepcopy(result_contract.get("columns") or []),
        "criteria": criteria,
        "source_snapshot_sha256": [sha256_json(item) for item in source_snapshots],
        "analysis_result_sha256": sha256_json(result),
    }
    executed = {**material, "executed_result_contract_sha256": sha256_json(material)}
    return validate_contract(executed, "executed-result.schema.json", stage="executed_result_contract")


class ResponseStateCommit(Component):
    display_name = "응답 조립 및 세션 상태 저장"
    description = "검증된 답변과 분석 결과를 표준 응답으로 조립하고 결과 저장 및 멀티턴 세션 상태 갱신을 원자적으로 수행합니다."
    icon = "save"
    metadata = {"logical_stage": "state_commit"}
    inputs = [
        DataInput(name="answer_context", display_name="검증된 답변 컨텍스트", required=True, info="결정론적 사실 또는 주장 검증을 통과한 선택적 LLM 문장이 포함된 컨텍스트입니다."),
        SecretStrInput(name="mongo_uri", display_name="MongoDB 연결 URI", value="", required=False, info="인증된 멀티턴 상태와 결과를 저장할 MongoDB 연결 문자열입니다."),
        StrInput(name="mongo_database", display_name="MongoDB 데이터베이스", value="datagov", info="세션 상태 및 결과 컬렉션이 위치한 데이터베이스 이름입니다."),
        StrInput(name="result_collection", display_name="분석 결과 컬렉션", value="agent_v6_result_store", info="불변 분석 결과와 다운로드 원본을 저장하는 v6 전용 컬렉션입니다."),
        StrInput(name="state_collection", display_name="세션 상태 컬렉션", value="agent_v6_session_state", info="후속 질문에 사용할 멀티턴 상태를 저장하는 v6 전용 컬렉션입니다."),
        IntInput(name="mongo_timeout_ms", display_name="MongoDB 제한 시간(ms)", value=5000, info="MongoDB 저장 및 상태 갱신에 적용할 제한 시간(밀리초)입니다."),
        IntInput(name="result_ttl_seconds", display_name="분석 결과 보존 시간(초)", value=3600, info="저장된 분석 결과와 다운로드 원본의 유효 시간입니다."),
        StrInput(name="download_base_url", display_name="다운로드 기준 URL", value="", required=False, info="결과 다운로드 링크를 만들 때 사용할 외부 기준 URL입니다. 비워 두면 링크를 생성하지 않습니다."),
        BoolInput(
            name="allow_anonymous_multiturn",
            display_name="익명 멀티턴 허용",
            value=False,
            advanced=True,
            info="Request node와 함께 신뢰된 단일 사용자 환경에서만 활성화합니다.",
        ),
    ]
    outputs = [Output(name="response", display_name="표준 분석 응답", method="commit", types=["Data"])]

    def _state_collection_names(self):
        values = {
            "result_collection": str(getattr(self, "result_collection", "agent_v6_result_store") or "").strip(),
            "state_collection": str(getattr(self, "state_collection", "agent_v6_session_state") or "").strip(),
        }
        expected = {
            "result_collection": "agent_v6_result_store",
            "state_collection": "agent_v6_session_state",
        }
        if values != expected or len(set(values.values())) != 2:
            raise ContractError(
                "state_policy_mismatch",
                "state_store_config",
                "State collections are role-bound to the registered distinct v6-only names.",
                {"expected": expected, "actual": values},
            )
        return values

    def _state_store(self, subject_id, allow_anonymous_multiturn=False):
        collections = self._state_collection_names()
        uri = _secret_text(getattr(self, "mongo_uri", "")) or os.getenv("MONGODB_URI", "").strip()
        if subject_id == "anonymous":
            return _shared_memory_store() if allow_anonymous_multiturn else InMemoryStateStore()
        if not uri:
            return _shared_memory_store()
        return MongoStateStore(
            uri,
            database=str(getattr(self, "mongo_database", "") or os.getenv("MONGODB_DATABASE", "datagov")),
            result_collection=collections["result_collection"],
            state_collection=collections["state_collection"],
            timeout_ms=max(500, min(int(getattr(self, "mongo_timeout_ms", 5000)), 30000)),
        )

    def commit(self) -> Data:
        current = _payload(getattr(self, "answer_context", None))
        try:
            current = _require_context(current, "state_commit")
            if not current.get("ok"):
                return Data(data=error_response(current.get("request") or {}, current.get("error") or {}, current.get("route_telemetry") or {}))
            # Validate role-bound collection names even for ephemeral responses.
            # Otherwise a bad production node configuration can remain latent
            # until the first authenticated or opted-in persistent request.
            self._state_collection_names()
            request, intent, plan, result = current["request"], current["intent"], current["plan"], current["result"]
            next_state = compact_next_state(request, intent, plan, result)
            subject_id = str(current.get("subject_id") or "anonymous")
            state_policy = current.get("state_policy") if isinstance(current.get("state_policy"), dict) else {}
            policy_material = {key: deepcopy(value) for key, value in state_policy.items() if key != "policy_sha256"}
            if state_policy.get("contract_version") != "state.policy.v1" or state_policy.get("policy_sha256") != sha256_json(policy_material):
                raise ContractError("state_policy_mismatch", "state_commit", "State policy is missing or was modified.")
            if state_policy.get("subject_id") != subject_id or state_policy.get("storage_session_id") != current.get("storage_session_id"):
                raise ContractError("state_policy_mismatch", "state_commit", "State policy identity does not match the request context.")
            request_anonymous_toggle = bool(state_policy.get("anonymous_multiturn_enabled"))
            response_anonymous_toggle = bool(getattr(self, "allow_anonymous_multiturn", False))
            if subject_id == "anonymous" and request_anonymous_toggle != response_anonymous_toggle:
                raise ContractError("state_policy_mismatch", "state_commit", "Anonymous multi-turn settings differ between request and commit nodes.")
            persistent = str(state_policy.get("mode") or "") in {"persistent_authenticated", "persistent_anonymous_opt_in"}
            if persistent:
                store = self._state_store(subject_id, request_anonymous_toggle)
                committed_state, result_ref, source_refs = store.commit_execution(
                    subject_id=subject_id,
                    session_id=str(current.get("storage_session_id") or current.get("session_id") or request.get("session_id") or "default"),
                    expected_version=int(current.get("prior_version") or 0),
                    result=_executed_result(result, plan, current.get("source_snapshots") or []),
                    source_snapshots=current.get("source_snapshots") or [],
                    next_state=next_state,
                    ttl_seconds=max(60, min(int(getattr(self, "result_ttl_seconds", 3600)), 604800)),
                )
                validate_contract(committed_state, "turn-state.schema.json", stage="state_commit")
                response = assemble_response(
                    request=request, intent=intent, plan=plan, result=result, answer_facts=current["answer_facts"],
                    state=committed_state, result_ref=result_ref, source_refs=source_refs,
                    route_telemetry=current.get("route_telemetry") or {}, source_diagnostics=current.get("source_diagnostics") or [],
                    data_mode=str(current.get("data_mode") or "dummy"),
                    download_base_url=str(getattr(self, "download_base_url", "") or os.getenv("DATA_REF_DOWNLOAD_BASE_URL", "")),
                    events=["result_store", "state_cas", "runtime_release", "terminal_fanout"],
                )
            else:
                response = assemble_response(
                    request=request, intent=intent, plan=plan, result=result, answer_facts=current["answer_facts"],
                    state={}, result_ref={}, source_refs=[], route_telemetry=current.get("route_telemetry") or {},
                    source_diagnostics=current.get("source_diagnostics") or [], data_mode=str(current.get("data_mode") or "dummy"),
                    download_base_url="", events=["ephemeral_inline_response", "runtime_release", "terminal_fanout"],
                )
                ephemeral = {key: deepcopy(value) for key, value in response.items() if key != "response_sha256"}
                ephemeral["data_refs"] = []
                ephemeral["state"] = None
                ephemeral["answer_sections"]["result_table"]["data_ref"] = ""
                ephemeral["answer_sections"]["downloads"] = []
                ephemeral["answer_sections"]["notices"].append(
                    {"code": "anonymous_ephemeral", "message": "Anonymous default mode returns inline results without persistent references."}
                )
                response = _finalize_response(ephemeral)
            narrative = current.get("narrative") if isinstance(current.get("narrative"), dict) else {}
            if narrative.get("attempted"):
                material = {key: deepcopy(value) for key, value in response.items() if key != "response_sha256"}
                material["trace"]["usage"]["answer_llm_calls"] = int(narrative.get("llm_calls") or 0)
                if narrative.get("claim_status") == "verified" and narrative.get("message"):
                    material["message"] = str(narrative["message"])
                    material["answer_sections"]["summary"]["headline"] = str(narrative["message"])
                elif narrative.get("notice"):
                    material["answer_sections"]["notices"].append({"code": "answer_narrative_fallback", "message": str(narrative["notice"])})
                response = _finalize_response(material)
            return Data(data=response)
        except ContractError as exc:
            return Data(data=error_response(current.get("request") or {}, exc.as_dict(str(current.get("trace_id") or "")), current.get("route_telemetry") or {}))
        except Exception as exc:
            error = ContractError("plan_contract_error", "runtime", "분석 실행 중 계약 오류가 발생했습니다.", {"error_type": type(exc).__name__})
            return Data(data=error_response(current.get("request") or {}, error.as_dict(str(current.get("trace_id") or "")), current.get("route_telemetry") or {}))
'''


MESSAGE_PRESENTATION_COMPONENT = r'''
from copy import deepcopy

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, IntInput, Output
from lfx.schema.message import Message


class MessagePresentation(Component):
    display_name = "채팅 메시지 표시 설정"
    description = "표준 응답 데이터는 그대로 보존하면서 채팅 Markdown에 표시할 결과·근거·진단 항목을 선택합니다."
    icon = "message-square-text"

    inputs = [
        DataInput(name="response", display_name="표준 분석 응답", required=True, info="표시할 답변·결과·근거·진단 정보를 모두 포함한 원본 응답입니다."),
        BoolInput(name="include_diagnostics", display_name="모든 진단 표시", value=False, info="의도 분석, 조회 진단, 실행 계획을 한 번에 표시합니다."),
        BoolInput(name="show_result_table", display_name="결과표 표시", value=True, info="분석 결과의 표 미리보기를 채팅 메시지에 포함합니다."),
        IntInput(name="table_preview_limit", display_name="표 미리보기 행 수", value=10, info="채팅 메시지에 표시할 결과표의 최대 행 수입니다."),
        BoolInput(name="show_analysis_evidence", display_name="분석 근거 표시", value=False, info="사용한 데이터와 연산에 대한 검증 가능한 근거를 표시합니다."),
        BoolInput(name="show_download_links", display_name="다운로드 링크 표시", value=True, info="응답에 생성된 결과 다운로드 링크를 표시합니다."),
        BoolInput(name="show_notices", display_name="알림 표시", value=True, info="제한, 생략, 주의 사항 등 사용자 알림을 표시합니다."),
        BoolInput(name="show_applied_criteria", display_name="적용 기준 표시", value=True, info="날짜·필터·정렬·순위 등 실제 적용된 조회 기준을 표시합니다."),
        BoolInput(name="show_next_questions", display_name="후속 질문 표시", value=False, info="현재 결과에서 이어서 물을 수 있는 후속 질문 제안을 표시합니다."),
        BoolInput(name="show_intent_analysis", display_name="의도 분석 표시", value=False, info="선택된 의도 후보와 분기 판정 정보를 진단용으로 표시합니다."),
        BoolInput(name="show_data_retrieval", display_name="조회 진단 표시", value=False, info="선택된 데이터 경로와 원천 조회 결과 요약을 표시합니다."),
        BoolInput(name="show_execution_plan", display_name="Typed Execution IR 표시", value=False, info="컴파일된 결정론적 실행 계획을 진단용으로 표시합니다."),
    ]
    outputs = [Output(name="message", display_name="채팅 답변 메시지", method="build_message", types=["Message"])]

    def build_message(self) -> Message:
        raw = getattr(getattr(self, "response", None), "data", getattr(self, "response", None))
        response = deepcopy(raw) if isinstance(raw, dict) else {}
        options = {
            "include_diagnostics": bool(getattr(self, "include_diagnostics", False)),
            "show_result_table": bool(getattr(self, "show_result_table", True)),
            "table_preview_limit": int(getattr(self, "table_preview_limit", 10)),
            "show_analysis_evidence": bool(getattr(self, "show_analysis_evidence", False)),
            "show_download_links": bool(getattr(self, "show_download_links", True)),
            "show_notices": bool(getattr(self, "show_notices", True)),
            "show_applied_criteria": bool(getattr(self, "show_applied_criteria", True)),
            "show_next_questions": bool(getattr(self, "show_next_questions", False)),
            "show_intent_analysis": bool(getattr(self, "show_intent_analysis", False)),
            "show_data_retrieval": bool(getattr(self, "show_data_retrieval", False)),
            "show_execution_plan": bool(getattr(self, "show_execution_plan", False)),
        }
        message = Message(
            text=render_message(response, options),
            sender="Machine",
            sender_name="Metadata Analysis",
            session_id=str(response.get("request", {}).get("session_id") or ""),
            session_metadata={
                "contract_version": "response.message-link.v1",
                "response_sha256": str(response.get("response_sha256") or ""),
            },
        )
        message.data = {"response": response, "display_options": normalize_display_options(options)}
        return message
'''


GAIA_OUTPUT_COMPONENT = r'''
from copy import deepcopy

from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema.data import Data
from lfx.schema.message import Message


class GaiAOutput(Component):
    display_name = "GaiA 형식 출력"
    description = "표준 분석 응답을 직접 사용해 GaiA 연동용 답변 메시지와 구조화된 메타데이터를 생성합니다."
    icon = "bot"
    group_outputs = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_output = True

    inputs = [DataInput(name="response", display_name="표준 분석 응답", required=True, info="GaiA 답변과 메타데이터로 변환할 검증 완료 표준 응답입니다.")]
    outputs = [
        Output(name="message", display_name="GaiA 채팅 메시지", method="build_message", types=["Message"]),
        Output(name="gaia_response", display_name="GaiA 구조화 응답", method="build_gaia", types=["Data"]),
    ]

    def _values(self):
        raw = getattr(getattr(self, "response", None), "data", getattr(self, "response", None))
        response = deepcopy(raw) if isinstance(raw, dict) else {}
        return response, gaia_output(response)

    def build_message(self) -> Message:
        response, gaia = self._values()
        message = Message(
            text=str(response.get("message") or ""),
            sender="Machine",
            sender_name="Metadata Analysis",
            session_id=str((response.get("request") or {}).get("session_id") or ""),
            session_metadata={
                "contract_version": "response.message-link.v1",
                "response_sha256": str(response.get("response_sha256") or ""),
            },
        )
        message.data = {"response": response, "gaia": deepcopy(gaia)}
        message.metadata = deepcopy(gaia.get("metadata", {}))
        return message

    def build_gaia(self) -> Data:
        _, gaia = self._values()
        return Data(data=gaia)
'''


API_RESPONSE_COMPONENT = r'''
from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema.data import Data


class APIResponseTerminal(Component):
    display_name = "API 표준 응답 출력"
    description = "검증된 표준 분석 또는 메타데이터 등록 응답을 변경 없이 API용 Data 출력으로 제공합니다."
    icon = "braces"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_output = True

    inputs = [DataInput(name="response", display_name="표준 응답", required=True, info="계약과 해시 검증을 거쳐 API 호출자에게 반환할 표준 응답입니다.")]
    outputs = [Output(name="api_response", display_name="API용 표준 응답", method="build_response", types=["Data"])]

    def build_response(self) -> Data:
        raw = getattr(getattr(self, "response", None), "data", getattr(self, "response", None))
        if not isinstance(raw, dict):
            raise ContractError("response_contract_error", "api_terminal", "Canonical response must be an object.")
        contract_version = str(raw.get("contract_version") or "")
        if contract_version == "response.v1":
            validated = validate_response_hash(raw)
        elif contract_version == "metadata.authoring.response.v1":
            validated = validate_authoring_response_hash(raw)
        else:
            raise ContractError(
                "response_contract_error",
                "api_terminal",
                "Unsupported canonical response contract.",
                {"contract_version": contract_version},
            )
        return Data(data=validated)
'''


NATURAL_METADATA_SOURCE_BUNDLE_COMPONENT = r'''
from lfx.custom.custom_component.component import Component
from lfx.io import MessageInput, Output
from lfx.schema.message import Message


def _message_text(value):
    text = getattr(value, "text", value)
    return str(text or "").strip()


class NaturalMetadataSourceBundle(Component):
    display_name = "자유형 메타데이터 입력 묶음"
    description = "작업자가 자유롭게 작성한 도메인·데이터셋·주요 필터 자연어를 한 번의 도메인 초기 등록 입력으로 묶으며 JSON이나 고정 문법을 요구하지 않습니다."
    icon = "files"
    metadata = {"logical_stage": "natural_metadata_source_bundle"}
    inputs = [
        MessageInput(name="domain_source", display_name="도메인 자연어", required=True, info="업무 목적, 용어, 분석 범위를 작업자가 자유롭게 작성한 도메인 설명입니다."),
        MessageInput(name="dataset_source", display_name="데이터셋 자연어", required=False, info="사용 가능한 데이터셋, 주요 컬럼, 관계를 작업자가 자유롭게 작성한 설명입니다."),
        MessageInput(name="main_filter_source", display_name="주요 필터 자연어", required=False, info="자주 쓰는 조건, 값의 의미, 날짜 기준을 작업자가 자유롭게 작성한 설명입니다."),
    ]
    outputs = [Output(name="bundled_source", display_name="자연어 초기 등록 묶음", method="bundle_sources", types=["Message"])]

    def bundle_sources(self) -> Message:
        parts = [
            ("도메인 정보", _message_text(getattr(self, "domain_source", None))),
            ("데이터셋 정보", _message_text(getattr(self, "dataset_source", None))),
            ("주요 필터 정보", _message_text(getattr(self, "main_filter_source", None))),
        ]
        if not parts[0][1]:
            raise ValueError("도메인 자연어 입력이 필요합니다.")
        encoded_total = sum(len(text.encode("utf-8")) for _, text in parts)
        if encoded_total > 64 * 1024:
            raise ValueError("메타데이터 자연어 입력 합계는 64KB 이하여야 합니다.")
        sections = [
            f"--- {label} 시작 ---\n{text}\n--- {label} 끝 ---"
            for label, text in parts
            if text
        ]
        return Message(text="\n\n".join(sections))
'''


SEMANTIC_VOCABULARY_HELPERS = r'''
import math
import re


_SEMANTIC_VOCABULARY_SECTIONS = (
    "datasets", "fields", "metrics", "relations", "grains", "orderings",
    "predicates", "recipes", "entity_groups",
)
_SEMANTIC_VOCABULARY_LIMITS = {
    "datasets": (1, 128),
    "fields": (1, 4096),
    "metrics": (0, 1024),
    "relations": (0, 256),
    "grains": (0, 256),
    "orderings": (0, 128),
    "predicates": (0, 256),
    "recipes": (0, 256),
    "entity_groups": (0, 512),
}


def _validated_semantic_vocabulary(
    value,
    *,
    expected_dataset_families=None,
    expected_field_families=None,
):
    expected_root = {"contract_version", *_SEMANTIC_VOCABULARY_SECTIONS}
    if not isinstance(value, dict) or set(value) != expected_root:
        raise ValueError("Approved semantic vocabulary root contract is invalid.")
    if value.get("contract_version") != "metadata.authoring.semantic-vocabulary.v1":
        raise ValueError("Approved semantic vocabulary version is invalid.")
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    if len(encoded) > 64 * 1024:
        raise ValueError("Approved semantic vocabulary exceeds 65536 UTF-8 bytes.")

    id_pattern = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,127}")
    forbidden = (
        "http://", "https://", "mongodb://", "mongodb+srv://", "select ",
        "insert ", "update ", "delete ", "password", "secret", "token=", "api_key",
    )
    normalized = {"contract_version": "metadata.authoring.semantic-vocabulary.v1"}
    for section in _SEMANTIC_VOCABULARY_SECTIONS:
        cards = value.get(section)
        lower, upper = _SEMANTIC_VOCABULARY_LIMITS[section]
        if not isinstance(cards, list) or not lower <= len(cards) <= upper:
            raise ValueError(f"Approved semantic vocabulary {section} count is invalid.")
        expected_keys = (
            {"id", "family", "labels"}
            if section == "datasets"
            else ({"id", "families", "labels"} if section == "fields" else {"id", "labels"})
        )
        seen_ids = set()
        label_owners = {}
        normalized_cards = []
        for card in cards:
            if not isinstance(card, dict) or set(card) != expected_keys:
                raise ValueError(f"Approved semantic vocabulary {section} card is invalid.")
            item_id = card.get("id")
            if not isinstance(item_id, str) or not id_pattern.fullmatch(item_id) or item_id in seen_ids:
                raise ValueError(f"Approved semantic vocabulary {section} id is invalid or duplicated.")
            seen_ids.add(item_id)
            labels = card.get("labels")
            if not isinstance(labels, list) or len(labels) > 64:
                raise ValueError(f"Approved semantic vocabulary {section} labels are invalid.")
            folded_labels = set()
            normalized_labels = []
            for label in labels:
                if not isinstance(label, str):
                    raise ValueError(f"Approved semantic vocabulary {section} label is invalid.")
                normalized_label = re.sub(r"\s+", " ", label.strip())
                folded = normalized_label.casefold()
                owner = label_owners.setdefault(folded, item_id)
                if (
                    not normalized_label
                    or len(normalized_label.encode("utf-8")) > 512
                    or any(ord(character) < 32 for character in normalized_label)
                    or any(fragment in folded for fragment in forbidden)
                    or normalized_label != label
                    or folded in folded_labels
                    or owner != item_id
                ):
                    raise ValueError(f"Approved semantic vocabulary {section} label is invalid, duplicated, or ambiguous.")
                folded_labels.add(folded)
                normalized_labels.append(normalized_label)
            normalized_card = {"id": item_id, "labels": normalized_labels}
            if section == "datasets":
                family = card.get("family")
                if not isinstance(family, str) or not id_pattern.fullmatch(family):
                    raise ValueError("Approved semantic vocabulary dataset family is invalid.")
                normalized_card["family"] = family
            elif section == "fields":
                families = card.get("families")
                if (
                    not isinstance(families, list)
                    or not 1 <= len(families) <= 128
                    or families != sorted(set(families))
                    or any(not isinstance(family, str) or not id_pattern.fullmatch(family) for family in families)
                ):
                    raise ValueError("Approved semantic vocabulary field families are invalid.")
                normalized_card["families"] = list(families)
            normalized_cards.append(normalized_card)
        if [card["id"] for card in normalized_cards] != sorted(seen_ids):
            raise ValueError(f"Approved semantic vocabulary {section} cards must be sorted by id.")
        normalized[section] = normalized_cards

    if expected_dataset_families is not None:
        expected_datasets = {
            str(dataset_id): str(family)
            for dataset_id, family in expected_dataset_families.items()
        }
        vocabulary_datasets = {card["id"]: card["family"] for card in normalized["datasets"]}
        if vocabulary_datasets != expected_datasets:
            raise ValueError("Approved semantic vocabulary datasets do not match the source registry.")
    if expected_field_families is not None:
        expected_fields = {
            str(field_id): sorted({str(family) for family in families})
            for field_id, families in expected_field_families.items()
        }
        vocabulary_fields = {card["id"]: card["families"] for card in normalized["fields"]}
        if vocabulary_fields != expected_fields:
            raise ValueError("Approved semantic vocabulary fields do not match the source registry.")
    return normalized


def _semantic_maps_from_descriptors(dataset_descriptors):
    dataset_families = {}
    field_families = {}
    for dataset_id, descriptor in (dataset_descriptors or {}).items():
        if not isinstance(descriptor, dict):
            continue
        family = str(descriptor.get("family") or "")
        dataset_families[str(dataset_id)] = family
        for field_id in (descriptor.get("fields") or {}):
            field_families.setdefault(str(field_id), set()).add(family)
    return dataset_families, field_families


def _dataset_field_allowlists_from_vocabulary(
    semantic_vocabulary, dataset_descriptors=None
):
    dataset_families = {
        str(card["id"]): str(card["family"])
        for card in (semantic_vocabulary or {}).get("datasets") or []
        if isinstance(card, dict)
    }
    field_families = {
        str(card["id"]): set(card.get("families") or [])
        for card in (semantic_vocabulary or {}).get("fields") or []
        if isinstance(card, dict)
    }
    if isinstance(dataset_descriptors, dict):
        if set(dataset_descriptors) != set(dataset_families):
            raise ValueError(
                "Approved dataset descriptors do not match the semantic vocabulary."
            )
        allowlists = {}
        for dataset_id, family in sorted(dataset_families.items()):
            descriptor = dataset_descriptors.get(dataset_id)
            fields = descriptor.get("fields") if isinstance(descriptor, dict) else None
            if not isinstance(fields, dict) or not fields:
                raise ValueError(
                    "Approved dataset descriptor has no exact field allowlist."
                )
            field_ids = sorted(str(field_id) for field_id in fields)
            if any(
                family not in field_families.get(field_id, set())
                for field_id in field_ids
            ):
                raise ValueError(
                    "Approved dataset descriptor field does not belong to its family."
                )
            allowlists[dataset_id] = field_ids
    else:
        allowlists = {
            dataset_id: sorted(
                field_id
                for field_id, families in field_families.items()
                if family in families
            )
            for dataset_id, family in sorted(dataset_families.items())
        }
    if not allowlists or any(not field_ids for field_ids in allowlists.values()):
        raise ValueError("Approved semantic vocabulary dataset field allowlists are empty.")
    return allowlists


_MAIN_FILTER_TARGET_SECTIONS = {
    "dataset": "datasets",
    "field": "fields",
    "metric": "metrics",
    "relation": "relations",
    "grain": "grains",
    "predicate": "predicates",
    "recipe": "recipes",
    "entity_group": "entity_groups",
}


def _main_filter_target_allowlists(semantic_vocabulary):
    allowlists = {}
    for target_type, section in _MAIN_FILTER_TARGET_SECTIONS.items():
        ids = sorted(
            {
                str(card["id"])
                for card in (semantic_vocabulary or {}).get(section) or []
                if isinstance(card, dict) and isinstance(card.get("id"), str)
            }
        )
        if ids:
            allowlists[target_type] = ids
    if not allowlists:
        raise ValueError("Approved Main Filter target allowlists are empty.")
    return allowlists


def _apply_main_filter_ir_allowlists(schema, semantic_vocabulary):
    projected = deepcopy(schema)
    additions = (projected.get("properties") or {}).get("alias_additions")
    base_item = additions.get("items") if isinstance(additions, dict) else None
    if not isinstance(base_item, dict) or not isinstance(base_item.get("properties"), dict):
        raise ValueError("Main Filter IR item schema is invalid.")
    branches = []
    for target_type, target_ids in sorted(
        _main_filter_target_allowlists(semantic_vocabulary).items()
    ):
        branch = deepcopy(base_item)
        branch["properties"]["target_type"] = {
            "type": "string",
            "enum": [target_type],
        }
        branch["properties"]["target_id"] = {
            "type": "string",
            "enum": target_ids,
        }
        branches.append(branch)
    additions["items"] = {"oneOf": branches}
    return projected


_SEMANTIC_TEMPLATE_SECTIONS = (
    "metrics", "relations", "entity_groups", "grains", "orderings",
    "predicates", "recipes",
)
_SEMANTIC_TEMPLATE_SPECS = {
    "metrics": ("metric_id", {
        "additivity", "aggregation", "aliases", "dependencies", "formula",
        "metric_id", "null_policy", "source_binding", "source_field",
        "temporal_contract", "unit", "value_type", "zero_policy",
    }, 1024),
    "relations": ("relation_id", {
        "aliases", "cardinality", "join_type", "key_mappings",
        "left_dataset", "left_keys", "multi_match_policy",
        "null_key_policy", "relation_id", "right_dataset", "right_keys",
    }, 2048),
    "entity_groups": ("group_id", {
        "alias_policy", "aliases", "display_name", "entity", "expansion",
        "group_id", "legacy_identity", "members", "selection",
        "target_field",
    }, 2048),
    "grains": ("grain_id", {"display_fields", "grain_id", "keys"}, 2048),
    "orderings": ("ordering_id", {"items", "keys", "ordering_id"}, 2048),
    "predicates": ("predicate_id", {
        "aliases", "allowed_operators", "grain_id", "group_id",
        "predicate", "predicate_id",
    }, 2048),
    "recipes": ("recipe_id", {
        "aliases", "datasets", "default_operation_template",
        "derived_metrics", "grain", "metrics", "recipe_id",
        "required_fields", "required_slots",
    }, 2048),
}
_SEMANTIC_TEMPLATE_LEGACY_ALIAS_TYPES = {
    "dataset", "field", "metric", "process_group", "process",
    "product_group", "recipe", "status",
}
_SEMANTIC_TEMPLATE_GENERIC_ALIAS_TYPES = {
    "dataset", "field", "metric", "relation", "grain", "predicate",
    "recipe", "entity_group",
}
_SEMANTIC_TEMPLATE_LEGACY_RECIPE_OPS = {
    "filter", "ordered_range", "product_token_match", "project", "derive",
    "aggregate", "compare_fields", "compare_group_attributes",
    "find_duplicate_groups", "join", "presence_filter", "sort", "rank",
    "concat_segments", "transform_previous_result",
}
_SEMANTIC_TEMPLATE_GENERIC_RECIPE_OPS = {
    "filter", "project", "aggregate", "join", "derive", "compare_fields",
    "sort", "rank", "transform_previous_result",
}

_DATASET_TEMPLATE_KEYS = {
    "date_filter_contract", "date_policy", "default_detail_fields",
    "display_name", "fixture_only", "parameters", "read_policy",
    "time_scope", "upstream_bindings",
}
_DATASET_TEMPLATE_REQUIRED_KEYS = {
    "date_policy", "default_detail_fields", "display_name", "parameters",
    "read_policy", "time_scope",
}


def _semantic_sha256_json(value):
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _validated_dataset_template(
    dataset_id, value, declared_sha256, approved_field_ids
):
    if (
        not isinstance(value, dict)
        or not _DATASET_TEMPLATE_REQUIRED_KEYS <= set(value) <= _DATASET_TEMPLATE_KEYS
        or not re.fullmatch(r"[0-9a-f]{64}", str(declared_sha256 or ""))
        or _semantic_sha256_json(value) != declared_sha256
    ):
        raise ValueError("Approved dataset template contract or hash is invalid.")
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    if not encoded or len(encoded) > 32 * 1024:
        raise ValueError("Approved dataset template exceeds the bounded payload size.")

    forbidden_keys = {
        "code", "source", "source_code", "module", "module_path",
        "import_path", "python", "sql", "url", "uri", "credential",
        "secret", "password", "token", "api_key", "config_ref", "query_ref",
        "source_type", "source_adapter", "fields", "family",
    }
    forbidden_values = (
        "http://", "https://", "mongodb://", "mongodb+srv://", "select ",
        "insert ", "update ", "delete ", "import ", "e" + "xec(", "e" + "val(",
        "password", "secret", "token=", "api_key",
    )

    def visit(current, depth=0):
        if depth > 20:
            raise ValueError("Approved dataset template nesting is too deep.")
        if isinstance(current, dict):
            if len(current) > 512:
                raise ValueError("Approved dataset template object is too large.")
            for raw_key, child in current.items():
                key = str(raw_key or "").strip()
                if (
                    not key
                    or len(key) > 256
                    or key.casefold() in forbidden_keys
                ):
                    raise ValueError("Approved dataset template contains a forbidden key.")
                visit(child, depth + 1)
            return
        if isinstance(current, list):
            if len(current) > 4096:
                raise ValueError("Approved dataset template list is too large.")
            for child in current:
                visit(child, depth + 1)
            return
        if isinstance(current, str):
            folded = current.casefold()
            if (
                not current.strip()
                or len(current) > 4096
                or any(marker in folded for marker in forbidden_values)
            ):
                raise ValueError("Approved dataset template contains a forbidden value.")
            return
        if current is None or isinstance(current, (bool, int)):
            return
        if isinstance(current, float) and math.isfinite(current):
            return
        raise ValueError("Approved dataset template contains a non-JSON value.")

    visit(value)
    approved_fields = {str(item) for item in approved_field_ids or ()}
    detail_fields = value.get("default_detail_fields")
    read_policy = value.get("read_policy")
    if (
        not isinstance(detail_fields, list)
        or len(detail_fields) > 128
        or len(detail_fields) != len(set(detail_fields))
        or any(item not in approved_fields for item in detail_fields)
        or not isinstance(value.get("display_name"), str)
        or not 1 <= len(value["display_name"]) <= 200
        or not isinstance(value.get("time_scope"), str)
        or not 1 <= len(value["time_scope"]) <= 64
        or not isinstance(value.get("parameters"), dict)
        or len(value["parameters"]) > 128
        or not isinstance(value.get("date_policy"), dict)
        or len(value["date_policy"]) > 32
        or not isinstance(read_policy, dict)
        or set(read_policy) - {"read_only", "timeout_seconds", "max_rows"}
        or read_policy.get("read_only") is not True
        or isinstance(read_policy.get("timeout_seconds"), bool)
        or not isinstance(read_policy.get("timeout_seconds"), int)
        or not 1 <= read_policy["timeout_seconds"] <= 120
        or isinstance(read_policy.get("max_rows"), bool)
        or not isinstance(read_policy.get("max_rows"), int)
        or not 1 <= read_policy["max_rows"] <= 1_000_000
    ):
        raise ValueError("Approved dataset template policies are invalid.")
    if "date_filter_contract" in value and (
        not isinstance(value["date_filter_contract"], dict)
        or len(value["date_filter_contract"]) > 32
    ):
        raise ValueError("Approved dataset template date filter is invalid.")
    if "fixture_only" in value and not isinstance(value["fixture_only"], bool):
        raise ValueError("Approved dataset template fixture policy is invalid.")
    if "upstream_bindings" in value and (
        not isinstance(value["upstream_bindings"], list)
        or len(value["upstream_bindings"]) > 64
        or any(not isinstance(card, dict) for card in value["upstream_bindings"])
    ):
        raise ValueError("Approved dataset template upstream bindings are invalid.")
    return deepcopy(value)


def _validated_semantic_templates(value, semantic_vocabulary):
    expected_root = {
        "contract_version", "locale", "timezone", "planner_policy",
        *_SEMANTIC_TEMPLATE_SECTIONS,
        "aliases",
    }
    if not isinstance(value, dict) or set(value) != expected_root:
        raise ValueError("Approved semantic templates root contract is invalid.")
    if value.get("contract_version") != "metadata.authoring.semantic-templates.v1":
        raise ValueError("Approved semantic templates version is invalid.")
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    if not encoded or len(encoded) > 128 * 1024:
        raise ValueError("Approved semantic templates exceed the bounded payload size.")
    locale = value.get("locale")
    timezone = value.get("timezone")
    if (
        not isinstance(locale, str)
        or not 1 <= len(locale) <= 64
        or not isinstance(timezone, str)
        or not 1 <= len(timezone) <= 128
    ):
        raise ValueError("Approved semantic template locale or timezone is invalid.")
    planner_policy = value.get("planner_policy")
    if not isinstance(planner_policy, dict):
        raise ValueError("Approved semantic template planner policy is invalid.")
    planner_profile = planner_policy.get("planner_profile")
    if planner_profile == "generic_v2":
        if set(planner_policy) != {"planner_profile"}:
            raise ValueError("Generic planner policy contains an unknown key.")
    elif planner_profile == "legacy_v1_compat":
        if (
            set(planner_policy) != {
                "planner_profile", "legacy_catalog_sha256"
            }
            or not re.fullmatch(
                r"[0-9a-f]{64}",
                str(planner_policy.get("legacy_catalog_sha256") or ""),
            )
        ):
            raise ValueError("Legacy planner policy pin is invalid.")
    else:
        raise ValueError("Approved semantic template planner profile is invalid.")

    forbidden_keys = {
        "source_type", "source_adapter", "config_ref", "query_ref",
        "physical_column", "physical_aliases", "coercion", "credential",
        "credentials", "password", "secret", "api_key", "token", "code",
        "python", "script", "sql",
    }
    forbidden_values = (
        "http://", "https://", "mongodb://", "mongodb+srv://", "select ",
        "insert ", "update ", "delete ", "import pandas", "def ", "lambda ",
        "api_key", "password", "secret", "token=",
    )

    forbidden_value_patterns = (
        re.compile(r"(?:https?|mongodb(?:\+srv)?|jdbc)://", re.IGNORECASE),
        re.compile(
            r"\b(?:select\s+.+\s+from|insert\s+into|delete\s+from|update\s+.+\s+set)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:import\s+[A-Za-z_]|from\s+[A-Za-z_][A-Za-z0-9_.]*\s+import|def\s+[A-Za-z_]\w*\s*\(|lambda\s+)"
        ),
    )

    def validate_safe_json(current, path=()):
        if len(path) > 24:
            raise ValueError("Approved semantic templates exceed the nesting depth limit.")
        if isinstance(current, dict):
            if len(current) > 8192 or any(
                str(key).casefold() in forbidden_keys for key in current
            ):
                raise ValueError("Approved semantic templates contain a forbidden execution key.")
            for key, child in current.items():
                if not isinstance(key, str) or not key or len(key) > 256:
                    raise ValueError("Approved semantic template key is invalid.")
                validate_safe_json(child, (*path, key))
            return
        if isinstance(current, list):
            if len(current) > 8192:
                raise ValueError("Approved semantic template array is too large.")
            for index, child in enumerate(current):
                validate_safe_json(child, (*path, str(index)))
            return
        if current is None or isinstance(current, (bool, int, float)):
            return
        if isinstance(current, str):
            folded = current.casefold()
            if (
                not current
                or len(current) > 4096
                or any(fragment in folded for fragment in forbidden_values)
                or any(pattern.search(current) for pattern in forbidden_value_patterns)
            ):
                raise ValueError("Approved semantic templates contain a forbidden execution value.")
            return
        raise ValueError("Approved semantic templates contain a non-JSON value.")

    vocabulary_ids = {
        section: {
            str(card["id"])
            for card in (semantic_vocabulary or {}).get(section) or []
            if isinstance(card, dict) and isinstance(card.get("id"), str)
        }
        for section in _SEMANTIC_TEMPLATE_SECTIONS
    }
    normalized = {
        "contract_version": "metadata.authoring.semantic-templates.v1",
        "locale": locale,
        "timezone": timezone,
        "planner_policy": deepcopy(planner_policy),
    }
    for section in _SEMANTIC_TEMPLATE_SECTIONS:
        cards = value.get(section)
        identity_key, allowed_keys, section_limit = _SEMANTIC_TEMPLATE_SPECS[section]
        if (
            not isinstance(cards, dict)
            or len(cards) > min(
                _SEMANTIC_VOCABULARY_LIMITS[section][1], section_limit
            )
            or set(cards) != vocabulary_ids[section]
        ):
            raise ValueError(
                f"Approved semantic template {section} IDs do not match the vocabulary."
            )
        for item_id, card in cards.items():
            if (
                not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,127}", str(item_id))
                or not isinstance(card, dict)
                or identity_key in card
                or not set(card).issubset(allowed_keys - {identity_key})
            ):
                raise ValueError(
                    f"Approved semantic template {section} card is open or invalid."
                )
        validate_safe_json(cards, (section,))
        normalized[section] = {
            str(item_id): cards[item_id] for item_id in sorted(cards)
        }

    registered_families = {
        str(card.get("family") or "")
        for card in (semantic_vocabulary or {}).get("datasets") or []
        if isinstance(card, dict)
    }
    field_families = {
        str(card.get("id") or ""): set(card.get("families") or [])
        for card in (semantic_vocabulary or {}).get("fields") or []
        if isinstance(card, dict)
    }
    for metric in normalized["metrics"].values():
        binding = metric.get("source_binding")
        if binding is None:
            continue
        if (
            not isinstance(binding, dict)
            or not {"dataset_family", "field"}.issubset(binding)
            or not set(binding).issubset(
                {"dataset_family", "field", "fixed_filters"}
            )
        ):
            raise ValueError("Approved metric source binding is open or incomplete.")
        family = str(binding.get("dataset_family") or "")
        field_id = str(binding.get("field") or "")
        if (
            family not in registered_families
            or family not in field_families.get(field_id, set())
        ):
            raise ValueError("Approved metric source binding is not registered.")
        fixed_filters = binding.get("fixed_filters", [])
        if not isinstance(fixed_filters, list) or len(fixed_filters) > 64:
            raise ValueError("Approved metric fixed filters are invalid.")
        for fixed_filter in fixed_filters:
            if (
                not isinstance(fixed_filter, dict)
                or set(fixed_filter)
                != {"field", "operator", "semantic_type", "value"}
                or family
                not in field_families.get(
                    str(fixed_filter.get("field") or ""), set()
                )
            ):
                raise ValueError("Approved metric fixed filter is not registered.")

    def recipe_operations(current):
        operations = set()
        if isinstance(current, dict):
            operation = current.get("op")
            if isinstance(operation, str) and operation:
                operations.add(operation)
            for child in current.values():
                operations.update(recipe_operations(child))
        elif isinstance(current, list):
            for child in current:
                operations.update(recipe_operations(child))
        return operations

    allowed_recipe_ops = (
        _SEMANTIC_TEMPLATE_LEGACY_RECIPE_OPS
        if planner_profile == "legacy_v1_compat"
        else _SEMANTIC_TEMPLATE_GENERIC_RECIPE_OPS
    )
    for recipe in normalized["recipes"].values():
        if not recipe_operations(
            recipe.get("default_operation_template")
        ).issubset(allowed_recipe_ops):
            raise ValueError("Approved recipe is incompatible with the planner policy.")
    aliases = value.get("aliases")
    if not isinstance(aliases, dict) or not 1 <= len(aliases) <= 8192:
        raise ValueError("Approved semantic template aliases are invalid.")
    target_ids = {
        "dataset": {
            str(card.get("id") or "")
            for card in (semantic_vocabulary or {}).get("datasets") or []
            if isinstance(card, dict)
        },
        "field": set(field_families),
        "metric": set(normalized["metrics"]),
        "relation": set(normalized["relations"]),
        "grain": set(normalized["grains"]),
        "predicate": set(normalized["predicates"]),
        "recipe": set(normalized["recipes"]),
        "entity_group": set(normalized["entity_groups"]),
        "process_group": set(normalized["entity_groups"]),
        "product_group": set(normalized["predicates"]),
    }
    process_targets = set()
    for ordering in normalized["orderings"].values():
        for item in ordering.get("items") or []:
            if isinstance(item, dict) and isinstance(item.get("oper_name"), str):
                process_targets.add(item["oper_name"])
    target_ids["process"] = process_targets
    allowed_alias_types = (
        _SEMANTIC_TEMPLATE_LEGACY_ALIAS_TYPES
        if planner_profile == "legacy_v1_compat"
        else _SEMANTIC_TEMPLATE_GENERIC_ALIAS_TYPES
    )
    for alias_id, card in aliases.items():
        if (
            not isinstance(alias_id, str)
            or not alias_id
            or len(alias_id) > 256
            or not isinstance(card, dict)
            or set(card) != {
                "target_type", "target_key", "values", "normalization",
                "match", "conflict", "provenance_source",
            }
        ):
            raise ValueError("Approved semantic template alias card is invalid.")
        target_type = str(card.get("target_type") or "")
        target_key = str(card.get("target_key") or "")
        normalization = card.get("normalization")
        values = card.get("values")
        if (
            alias_id != f"{target_type}:{target_key}"
            or target_type not in allowed_alias_types
            or (
                target_type != "status"
                and target_key not in target_ids.get(target_type, set())
            )
            or not isinstance(normalization, list)
            or not 1 <= len(normalization) <= 16
            or len(normalization) != len(set(normalization))
            or any(
                not isinstance(item, str)
                or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", item)
                for item in normalization
            )
            or any(
                not isinstance(card.get(key), str)
                or not card.get(key)
                or len(card.get(key)) > 128
                for key in ("match", "conflict", "provenance_source")
            )
            or not isinstance(values, list)
            or not 1 <= len(values) <= 128
        ):
            raise ValueError("Approved semantic template alias policy is invalid.")
        for alias_value in values:
            if (
                not isinstance(alias_value, dict)
                or set(alias_value) != {"text", "priority"}
                or not isinstance(alias_value.get("text"), str)
                or not alias_value.get("text")
                or len(alias_value.get("text")) > 256
                or isinstance(alias_value.get("priority"), bool)
                or not isinstance(alias_value.get("priority"), int)
                or not 0 <= alias_value.get("priority") <= 1_000_000
            ):
                raise ValueError("Approved semantic template alias value is invalid.")
    validate_safe_json(aliases, ("aliases",))
    normalized["aliases"] = {
        str(alias_id): aliases[alias_id] for alias_id in sorted(aliases)
    }
    return normalized
'''


AUTHORING_REFERENCE_REGISTRY_COMPONENT = r'''
import hashlib
import json
import re
import unicodedata

from lfx.custom.custom_component.component import Component
from lfx.io import MultilineInput, Output, StrInput
from lfx.schema.data import Data


def _registry_sha256(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AuthoringReferenceRegistry(Component):
    display_name = "승인 업무 어휘·원천 레지스트리"
    description = "세 등록 LLM에는 ID·family·업무용 표현만 담은 축약 의미 어휘를 제공하고, 물리 컬럼·타입·어댑터·설정·조회 ID는 결정론적 컴파일러에만 봉인합니다."
    icon = "database-zap"
    metadata = {"logical_stage": "authoring_reference_registry"}
    inputs = [
        MultilineInput(name="registry_json", display_name="승인 업무 어휘·원천 레지스트리 JSON", value="", required=True, info="운영자가 검토한 축약 업무 어휘와 데이터셋별 어댑터·설정·조회 식별자를 포함합니다. 비밀값이나 실행 쿼리는 입력하지 않습니다."),
        StrInput(name="domain_id", display_name="도메인 ID", value="default", required=True, info="레지스트리가 적용되는 업무 도메인의 고유 식별자입니다. 공유 시 대상 도메인 ID로 바꿉니다."),
    ]
    outputs = [
        Output(name="reference_context", display_name="검증된 업무 어휘·원천 컨텍스트", method="load_registry", types=["Data"])
    ]

    def load_registry(self) -> Data:
        raw = str(getattr(self, "registry_json", "") or "").strip()
        if not raw or len(raw.encode("utf-8")) > 256 * 1024:
            raise ValueError("승인 Source 레지스트리는 1~262144 UTF-8 bytes여야 합니다.")
        try:
            registry = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("승인 Source 레지스트리 JSON이 올바르지 않습니다.") from exc
        if not isinstance(registry, dict) or set(registry) != {
            "contract_version", "domain_id", "datasets", "semantic_vocabulary",
            "semantic_templates", "semantic_templates_sha256",
            "semantic_templates_blueprint_sha256",
            "semantic_templates_executable_sha256",
            "semantic_templates_projection_sha256",
        }:
            raise ValueError("승인 Source 레지스트리 root 계약이 닫혀 있지 않습니다.")
        domain_id = str(getattr(self, "domain_id", "") or "").strip()
        if (
            registry.get("contract_version") != "metadata.authoring.source-registry.v3"
            or registry.get("domain_id") != domain_id
            or not re.fullmatch(r"[a-z][a-z0-9_-]{1,63}", domain_id)
        ):
            raise ValueError("승인 Source 레지스트리의 계약 버전 또는 도메인 ID가 일치하지 않습니다.")
        datasets = registry.get("datasets")
        if not isinstance(datasets, dict) or not 1 <= len(datasets) <= 128:
            raise ValueError("승인 Source 레지스트리에는 1~128개의 dataset binding이 필요합니다.")
        id_pattern = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,127}")
        adapter_pattern = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,127}")
        ref_pattern = re.compile(r"(?:config|query):[A-Za-z0-9_.:-]{1,220}@[1-9][0-9]{0,8}")
        source_types = {"oracle", "sql", "mongodb", "http", "datalake", "goodocs", "file", "dummy", "previous_result"}
        semantic_type_pattern = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,63}")
        field_roles = {"filter", "group", "join", "compare", "aggregate", "derive", "project", "sort", "rank", "metric", "output"}
        forbidden = ("http://", "https://", "mongodb://", "mongodb+srv://", "select ", "insert ", "update ", "delete ", "password", "secret", "token=", "api_key")
        bindings = {}
        dataset_descriptors = {}
        for dataset_id in sorted(datasets):
            card = datasets.get(dataset_id)
            if not id_pattern.fullmatch(str(dataset_id)) or not isinstance(card, dict):
                raise ValueError("승인 Source 레지스트리 dataset ID가 유효하지 않습니다.")
            required = {
                "source_type", "source_adapter", "config_ref", "query_ref",
                "family", "field_descriptors", "proposal_exclusions",
                "dataset_template", "dataset_template_sha256",
            }
            if set(card) != required:
                raise ValueError("승인 Source binding은 실행 참조, family, field_descriptors만 포함해야 합니다.")
            normalized = {
                key: str(card.get(key) or "").strip()
                for key in ("source_type", "source_adapter", "config_ref", "query_ref")
            }
            joined = json.dumps(normalized, ensure_ascii=False).casefold()
            if (
                normalized["source_type"] not in source_types
                or not adapter_pattern.fullmatch(normalized["source_adapter"])
                or not ref_pattern.fullmatch(normalized["config_ref"])
                or not normalized["config_ref"].startswith("config:")
                or not ref_pattern.fullmatch(normalized["query_ref"])
                or not normalized["query_ref"].startswith("query:")
                or any(fragment in joined for fragment in forbidden)
            ):
                raise ValueError("승인 Source binding에 비허용 참조, 실행 payload 또는 credential 모양이 포함되어 있습니다.")
            family = str(card.get("family") or "").strip()
            raw_descriptors = card.get("field_descriptors")
            raw_exclusions = card.get("proposal_exclusions")
            if not id_pattern.fullmatch(family) or not isinstance(raw_descriptors, dict) or not 1 <= len(raw_descriptors) <= 2048:
                raise ValueError("승인 Source descriptor에는 유효한 family와 1~2048개 field가 필요합니다.")
            if not isinstance(raw_exclusions, dict) or len(raw_exclusions) > 2048:
                raise ValueError("승인 proposal exclusion은 0~2048개 이름의 object여야 합니다.")
            descriptors = {}
            for field_id in sorted(raw_descriptors):
                descriptor = raw_descriptors.get(field_id)
                descriptor_required = {"physical_column", "semantic_type", "roles"}
                descriptor_optional = {"physical_aliases", "coercion", "nullable", "required_in_source", "timezone"}
                if (
                    not id_pattern.fullmatch(str(field_id))
                    or not isinstance(descriptor, dict)
                    or not descriptor_required <= set(descriptor) <= descriptor_required | descriptor_optional
                ):
                    raise ValueError("승인 field descriptor의 ID 또는 닫힌 key 계약이 유효하지 않습니다.")
                physical_column = str(descriptor.get("physical_column") or "").strip()
                semantic_type = str(descriptor.get("semantic_type") or "").strip()
                roles = descriptor.get("roles")
                aliases = descriptor.get("physical_aliases") or []
                if (
                    not physical_column
                    or len(physical_column) > 256
                    or not semantic_type_pattern.fullmatch(semantic_type)
                    or not isinstance(roles, list)
                    or not roles
                    or len(roles) != len(set(roles))
                    or not set(roles) <= field_roles
                    or not isinstance(aliases, list)
                    or len(aliases) != len(set(aliases))
                    or any(not isinstance(value, str) or not value.strip() or len(value) > 256 for value in aliases)
                ):
                    raise ValueError("승인 field descriptor의 물리 컬럼, 타입, 역할 또는 alias가 유효하지 않습니다.")
                normalized_descriptor = {
                    "physical_column": physical_column,
                    "semantic_type": semantic_type,
                    "roles": list(roles),
                }
                for key in sorted(descriptor_optional):
                    if key in descriptor:
                        normalized_descriptor[key] = descriptor[key]
                serialized = json.dumps(normalized_descriptor, ensure_ascii=False).casefold()
                if any(fragment in serialized for fragment in forbidden):
                    raise ValueError("승인 field descriptor에 실행 payload 또는 credential 모양이 포함되어 있습니다.")
                descriptors[str(field_id)] = normalized_descriptor
            try:
                dataset_template = _validated_dataset_template(
                    dataset_id,
                    card.get("dataset_template"),
                    card.get("dataset_template_sha256"),
                    descriptors,
                )
            except ValueError as exc:
                raise ValueError(
                    "승인 dataset template 또는 hash가 유효하지 않습니다."
                ) from exc
            approved_names = {
                re.sub(r"\s+", " ", str(_name).strip()).casefold()
                for field_id, descriptor in descriptors.items()
                for _name in (
                    field_id,
                    descriptor["physical_column"],
                    *(descriptor.get("physical_aliases") or []),
                )
            }
            exclusion_reasons = {
                "source_projection_not_registered",
                "source_expression_before_alias",
                "legacy_source_name",
            }
            proposal_exclusions = {}
            folded_exclusions = set()
            for exclusion_name in sorted(raw_exclusions):
                policy = raw_exclusions.get(exclusion_name)
                if not isinstance(policy, dict):
                    raise ValueError("승인 proposal exclusion policy는 object여야 합니다.")
                reason = policy.get("reason_code")
                expected_policy_keys = (
                    {"reason_code", "target_field_id"}
                    if reason in {"source_expression_before_alias", "legacy_source_name"}
                    else {"reason_code"}
                )
                folded = re.sub(
                    r"\s+", " ", str(exclusion_name).strip()
                ).casefold()
                if (
                    not isinstance(exclusion_name, str)
                    or not exclusion_name.strip()
                    or len(exclusion_name) > 256
                    or any(ord(character) < 32 for character in exclusion_name)
                    or reason not in exclusion_reasons
                    or set(policy) != expected_policy_keys
                    or folded in folded_exclusions
                    or folded in approved_names
                ):
                    raise ValueError("승인 proposal exclusion 이름 또는 사유가 유효하지 않습니다.")
                target_field_id = policy.get("target_field_id")
                if target_field_id is not None and target_field_id not in descriptors:
                    raise ValueError("승인 proposal exclusion target field가 존재하지 않습니다.")
                folded_exclusions.add(folded)
                proposal_exclusions[exclusion_name] = {
                    key: policy[key] for key in sorted(policy)
                }
            bindings[str(dataset_id)] = normalized
            dataset_descriptors[str(dataset_id)] = {
                "family": family,
                "fields": descriptors,
                "proposal_exclusions": proposal_exclusions,
                "dataset_template": dataset_template,
                "dataset_template_sha256": str(
                    card.get("dataset_template_sha256") or ""
                ),
            }
        dataset_families, field_families = _semantic_maps_from_descriptors(
            dataset_descriptors
        )
        semantic_vocabulary = _validated_semantic_vocabulary(
            registry.get("semantic_vocabulary"),
            expected_dataset_families=dataset_families,
            expected_field_families=field_families,
        )
        semantic_templates = _validated_semantic_templates(
            registry.get("semantic_templates"), semantic_vocabulary
        )
        semantic_templates_sha256 = _registry_sha256(semantic_templates)
        template_provenance = {
            key: str(registry.get(key) or "")
            for key in (
                "semantic_templates_sha256",
                "semantic_templates_blueprint_sha256",
                "semantic_templates_executable_sha256",
                "semantic_templates_projection_sha256",
            )
        }
        if (
            template_provenance["semantic_templates_sha256"]
            != semantic_templates_sha256
            or any(
                not re.fullmatch(r"[0-9a-f]{64}", value)
                for value in template_provenance.values()
            )
        ):
            raise ValueError("승인 의미 템플릿 provenance hash가 유효하지 않습니다.")
        material = {
            "contract_version": "metadata.authoring.source-registry-context.v3",
            "domain_id": domain_id,
            "bindings": bindings,
            "dataset_descriptors": dataset_descriptors,
            "semantic_vocabulary": semantic_vocabulary,
            "semantic_templates": semantic_templates,
            **template_provenance,
        }
        material["registry_sha256"] = _registry_sha256(material)
        return Data(data=material)
'''


AUTHORING_PROMPT_CONTEXT_COMPONENT = r'''
import hashlib
import json
import re
import unicodedata
from copy import deepcopy

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, DropdownInput, MessageInput, MultilineInput, Output, StrInput
from lfx.schema.data import Data


def _authoring_schema_refs(value):
    refs = set()
    if isinstance(value, dict):
        raw_ref = value.get("$ref")
        prefix = "#/$defs/"
        if isinstance(raw_ref, str) and raw_ref.startswith(prefix):
            refs.add(raw_ref[len(prefix) :])
        for child in value.values():
            refs.update(_authoring_schema_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_authoring_schema_refs(child))
    return refs


def _authoring_reachable_defs(properties, available_defs):
    pending = set(_authoring_schema_refs(properties))
    selected = {}
    while pending:
        name = sorted(pending)[0]
        pending.remove(name)
        if name in selected:
            continue
        definition = available_defs.get(name)
        if not isinstance(definition, dict):
            raise ContractError("metadata_schema_error", "metadata_prompt_context", "Schema definition reference is missing.", {"definition": name})
        selected[name] = deepcopy(definition)
        pending.update(_authoring_schema_refs(definition) - set(selected))
    return {name: selected[name] for name in sorted(selected)}


def _authoring_partial_schema(value):
    if isinstance(value, list):
        return [_authoring_partial_schema(child) for child in value]
    if not isinstance(value, dict):
        return deepcopy(value)
    result = {key: _authoring_partial_schema(child) for key, child in value.items() if key != "required"}
    raw_type = result.get("type")
    if raw_type == "object" or (isinstance(raw_type, list) and "object" in raw_type):
        current_min = result.get("minProperties")
        result["minProperties"] = max(1, int(current_min) if isinstance(current_min, int) else 0)
    return result


def _authoring_output_schema(
    kind,
    *,
    annotation_only=False,
    proposal_source_sha256="",
    bootstrap_fragment=False,
    approved_dataset_ids=(),
    approved_dataset_field_ids=None,
    approved_semantic_vocabulary=None,
):
    if kind == "domain" and annotation_only:
        return load_schema("metadata-annotation-proposal.schema.json")
    full_schema = load_schema("metadata-authoring-draft.schema.json")
    if kind == "domain" and not bootstrap_fragment:
        draft_schema = full_schema
    elif kind == "domain" and bootstrap_fragment:
        # Executable semantic cards are compiler-owned templates from the
        # approved registry. The LLM only annotates the worker's prose.
        draft_schema = load_schema("metadata-annotation-proposal.schema.json")
    elif kind == "dataset":
        # The worker still writes unrestricted natural language.  Only the
        # internal LLM-facing representation is compact so a large field
        # catalog does not consume the provider's output ceiling.  The engine
        # expands this closed IR before the full authoring/compiler gates.
        draft_schema = load_schema("metadata-bootstrap-dataset-ir.schema.json")
    elif kind == "main_filter":
        # The provider returns a closed list rather than a dynamic aliases map.
        # Requiring target_type removes ambiguity when a field and metric share
        # the same canonical ID. The engine expands this IR into alias cards.
        draft_schema = load_schema("metadata-bootstrap-main-filter-ir.schema.json")
        if approved_semantic_vocabulary is not None:
            draft_schema = _apply_main_filter_ir_allowlists(
                draft_schema,
                approved_semantic_vocabulary,
            )
    else:
        sections = (
            {
                "domain": (
                    "display_name", "description", "locale", "timezone",
                    "metrics", "relations", "aliases", "entity_groups", "grains",
                    "orderings", "predicates", "recipes",
                ),
                "dataset": ("datasets", "aliases"),
                "main_filter": ("aliases",),
            }.get(kind)
            if bootstrap_fragment
            else {
                "dataset": ("datasets",),
                "main_filter": ("aliases", "entity_groups", "grains", "orderings", "predicates", "recipes"),
            }.get(kind)
        )
        if sections is None:
            return {}
        owned = {section: deepcopy(full_schema["properties"][section]) for section in sections}
        draft_schema = {
            "$schema": full_schema.get("$schema"),
            "title": f"metadata.authoring.{kind}.section-patch.v1",
            "type": "object",
            "additionalProperties": False,
            "minProperties": 1,
            "maxProperties": len(sections),
            "properties": (
                deepcopy(owned)
                if bootstrap_fragment
                else _authoring_partial_schema(owned)
            ),
            "$defs": (
                _authoring_reachable_defs(owned, full_schema.get("$defs") or {})
                if bootstrap_fragment
                else _authoring_partial_schema(
                    _authoring_reachable_defs(owned, full_schema.get("$defs") or {})
                )
            ),
        }
        if kind == "domain" and bootstrap_fragment:
            draft_schema["required"] = ["display_name"]
        elif kind == "dataset":
            draft_schema["required"] = ["datasets"]
        elif kind == "main_filter" and bootstrap_fragment:
            draft_schema["required"] = ["aliases"]

    approved_ids = sorted(
        {
            str(item).strip()
            for item in (approved_dataset_ids or ())
            if str(item).strip()
        }
    )
    if kind == "dataset" and approved_ids:
        if "datasetCard" in (draft_schema.get("$defs") or {}):
            field_allowlists = {
                dataset_id: sorted(
                    {
                        str(field_id).strip()
                        for field_id in (
                            (approved_dataset_field_ids or {}).get(dataset_id) or []
                        )
                        if str(field_id).strip()
                    }
                )
                for dataset_id in approved_ids
            }
            if any(not field_ids for field_ids in field_allowlists.values()):
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_prompt_context",
                    "승인 dataset별 field allowlist가 비어 있습니다.",
                )
            base_dataset_card = deepcopy(draft_schema["$defs"]["datasetCard"])
            base_field_card = deepcopy(draft_schema["$defs"]["fieldCard"])
            dataset_branches = []
            for dataset_id in approved_ids:
                allowed_fields = field_allowlists[dataset_id]
                dataset_card = deepcopy(base_dataset_card)
                dataset_card["properties"]["dataset_id"] = {
                    "type": "string",
                    "enum": [dataset_id],
                }
                field_card = deepcopy(base_field_card)
                field_card["properties"]["id"] = {
                    "type": "string",
                    "enum": allowed_fields,
                }
                field_card["properties"]["col"] = {
                    "type": "string",
                    "enum": allowed_fields,
                }
                dataset_card["properties"]["fields"]["items"] = field_card
                dataset_branches.append(dataset_card)
            draft_schema["$defs"]["datasetCard"] = {
                "oneOf": dataset_branches
            }
        else:
            draft_schema["properties"]["datasets"]["propertyNames"] = {
                "enum": approved_ids
            }

    source_sha256 = str(proposal_source_sha256 or "").strip()
    if not source_sha256:
        return draft_schema
    proposal_schema = deepcopy(load_schema("metadata-authoring-proposal.schema.json"))
    for branch in proposal_schema.get("oneOf") or []:
        if not isinstance(branch, dict):
            continue
        properties = branch.get("properties")
        required = branch.get("required")
        if not isinstance(properties, dict) or not isinstance(required, list):
            continue
        properties["source_sha256"] = {
            "type": "string",
            "const": source_sha256,
            "description": "입력 원문의 결정론적 SHA-256. runtime_context 값을 그대로 복사합니다.",
        }
        if "source_sha256" not in required:
            required.append("source_sha256")
        status = ((properties.get("status") or {}).get("const"))
        if status == "complete":
            properties["draft"] = deepcopy(draft_schema)
    return proposal_schema


def _authoring_alias_only_manifest_patch(source_manifest):
    counts = source_manifest.get("counts") if isinstance(source_manifest, dict) else None
    inventories = source_manifest.get("inventories") if isinstance(source_manifest, dict) else None
    if not isinstance(counts, dict) or not isinstance(inventories, dict):
        return None
    non_alias_kinds = (
        "datasets", "fields", "field_bindings", "field_roles", "metrics", "grains",
        "grain_keys", "grain_display_fields", "relations", "relation_endpoints",
        "relation_keys", "relation_policies", "recipes", "operations",
    )
    if any(int(counts.get(item) or 0) != 0 for item in non_alias_kinds):
        return None
    bindings = inventories.get("alias_bindings")
    if int(counts.get("aliases") or 0) < 1 or not isinstance(bindings, list):
        return None
    aliases = {}
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"alias", "target"}:
            return None
        alias = binding.get("alias")
        target = binding.get("target")
        if not isinstance(alias, str) or not alias or not isinstance(target, str) or not target:
            return None
        if alias in aliases and aliases[alias] != target:
            return None
        aliases[alias] = target
    return {"aliases": {key: aliases[key] for key in sorted(aliases)}}


def _freeform_source_manifest(source_text):
    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    inventories = {
        "datasets": [], "dataset_fields": {}, "fields": [], "field_roles": {},
        "metrics": [], "grains": [], "grain_keys": {}, "grain_display_fields": {},
        "relations": [], "relation_endpoints": {}, "relation_keys": {},
        "relation_policies": {}, "recipes": [], "operations": [], "aliases": [],
        "alias_targets": [], "alias_bindings": [],
    }
    counts = {
        "datasets": 0, "fields": 0, "field_bindings": 0, "field_roles": 0,
        "metrics": 0, "grains": 0, "grain_keys": 0, "grain_display_fields": 0,
        "relations": 0, "relation_endpoints": 0, "relation_keys": 0,
        "relation_policies": 0, "recipes": 0, "operations": 0, "aliases": 0,
        "alias_targets": 0, "alias_bindings": 0,
    }
    material = {
        "contract_version": "metadata.authoring.source-manifest.v1",
        "source_sha256": source_sha256,
        "inventories": inventories,
        "required_sections": [],
        "counts": counts,
    }
    material["manifest_sha256"] = hashlib.sha256(
        json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return material


class AuthoringPromptContextBuilder(Component):
    display_name = "메타데이터 등록 프롬프트 컨텍스트"
    description = "자연어 TXT와 신뢰된 구조 정보를 제한된 데이터 컨텍스트로 만들며, 프롬프트 지시문과 LLM 호출은 외부 노드가 담당합니다."
    icon = "file-json-2"
    metadata = {"logical_stage": "authoring_prompt_context"}
    inputs = [
        MessageInput(name="input_message", display_name="자연어 메타데이터 TXT", required=True, info="비전문 작업자가 업무 정보를 자유 형식으로 작성한 TXT 원문입니다."),
        DataInput(name="approved_reference_context", display_name="승인 원천 참조 컨텍스트", required=False, info="LLM에는 승인 데이터셋 ID allowlist와 hash만 제공하고, 실행 참조는 엔진이 별도 입력에서 봉인하는 운영자 승인 정보입니다."),
        BoolInput(name="bootstrap_fragment", display_name="초기 등록 분할 제안", value=False, advanced=True, info="도메인 최초 등록에서 원문 종류별 작은 폐쇄형 조각만 제안해 모델 응답 크기를 제한합니다."),
        DropdownInput(name="authoring_kind", display_name="등록 유형", options=["domain", "dataset", "main_filter", "domain_policy"], value="domain", info="도메인, 데이터셋, 주요 필터, 관리자 정책 중 이번에 등록할 항목을 선택합니다."),
        DropdownInput(name="mode", display_name="실행 모드", options=["prepare", "execute"], value="prepare", info="prepare는 후보를 생성하고 execute는 승인된 후보를 저장합니다. LLM 해석은 prepare에서만 수행합니다."),
        DropdownInput(name="source_grounding_mode", display_name="자연어 입력 해석 방식", options=["freeform_llm", "explicit_inventory"], value="freeform_llm", advanced=True, info="일반 작업자 입력은 freeform_llm을 사용합니다. explicit_inventory는 관리자 검증 경로 전용입니다."),
        StrInput(name="domain_id", display_name="도메인 ID", value="default", info="등록 대상 업무 도메인의 고유 식별자입니다. 공유 시 대상 도메인 ID로 바꿉니다."),
        StrInput(name="environment", display_name="운영 환경", value="production", info="메타데이터 리비전을 구분할 운영 환경 이름입니다."),
        MultilineInput(name="trusted_blueprint_json", display_name="신뢰 실행 블루프린트 JSON", value="", required=False, advanced=True, info="관리자 전용 결정론적 등록 경로에서만 사용하는 검토 완료 블루프린트입니다."),
        StrInput(name="trusted_blueprint_sha256", display_name="블루프린트 SHA-256 고정값", value="", required=False, advanced=True, info="신뢰 실행 블루프린트가 변조되지 않았는지 확인할 SHA-256 값입니다."),
    ]
    outputs = [Output(name="authoring_prompt_context", display_name="등록 LLM 실행 컨텍스트", method="build_context", types=["Data"])]

    def build_context(self) -> Data:
        kind = str(getattr(self, "authoring_kind", "domain") or "domain").strip()
        mode = str(getattr(self, "mode", "prepare") or "prepare").strip()
        if kind not in {"domain", "dataset", "main_filter", "domain_policy"} or mode not in {"prepare", "execute"}:
            raise ContractError("metadata_schema_error", "metadata_prompt_context", "등록 유형 또는 실행 모드가 유효하지 않습니다.")
        if mode == "execute":
            return Data(data={"contract_version": "prompt.runtime-context.v1", "purpose": "metadata_execute", "invoke": False, "variables": {}})
        source_text = str(getattr(getattr(self, "input_message", None), "text", getattr(self, "input_message", "")) or "").strip()
        if not source_text or len(source_text.encode("utf-8")) > 65536:
            raise ContractError("metadata_schema_error", "metadata_prompt_context", "메타데이터 TXT는 1~65536 UTF-8 바이트여야 합니다.")
        grounding_mode = str(getattr(self, "source_grounding_mode", "freeform_llm") or "freeform_llm").strip()
        if grounding_mode not in {"freeform_llm", "explicit_inventory"}:
            raise ContractError("metadata_schema_error", "metadata_prompt_context", "자연어 입력 해석 방식이 유효하지 않습니다.")
        blueprint_text = str(getattr(self, "trusted_blueprint_json", "") or "").strip()
        blueprint_pin = str(getattr(self, "trusted_blueprint_sha256", "") or "").strip()
        if kind == "domain" and bool(blueprint_text) != bool(blueprint_pin):
            raise ContractError("metadata_blueprint_invalid", "metadata_prompt_context", "블루프린트 JSON과 SHA-256 핀은 함께 설정해야 합니다.")
        annotation_only = kind == "domain" and bool(blueprint_text) and bool(blueprint_pin)
        bootstrap_fragment = bool(getattr(self, "bootstrap_fragment", False))
        if bootstrap_fragment and (annotation_only or kind == "domain_policy"):
            raise ContractError("metadata_policy_error", "metadata_prompt_context", "초기 등록 분할 제안은 자유형 domain/dataset/main_filter prepare에서만 사용할 수 있습니다.")
        strict_inventory = grounding_mode == "explicit_inventory" or annotation_only
        source_manifest = (
            extract_authoring_source_manifest(source_text)
            if strict_inventory
            else _freeform_source_manifest(source_text)
        )
        raw_reference = getattr(self, "approved_reference_context", None)
        reference_context = getattr(raw_reference, "data", raw_reference)
        if reference_context in (None, {}, ""):
            reference_context = {}
        if not isinstance(reference_context, dict):
            raise ContractError("metadata_dependency_error", "metadata_prompt_context", "승인 Source 참조 컨텍스트가 Data 객체가 아닙니다.")
        if reference_context:
            if set(reference_context) != {
                "contract_version", "domain_id", "bindings", "dataset_descriptors",
                "semantic_vocabulary", "semantic_templates",
                "semantic_templates_sha256",
                "semantic_templates_blueprint_sha256",
                "semantic_templates_executable_sha256",
                "semantic_templates_projection_sha256", "registry_sha256",
            }:
                raise ContractError("metadata_dependency_error", "metadata_prompt_context", "승인 Source 참조 컨텍스트 root 계약이 닫혀 있지 않습니다.")
            reference_material = {
                "contract_version": reference_context.get("contract_version"),
                "domain_id": reference_context.get("domain_id"),
                "bindings": reference_context.get("bindings"),
                "dataset_descriptors": reference_context.get("dataset_descriptors"),
                "semantic_vocabulary": reference_context.get("semantic_vocabulary"),
                "semantic_templates": reference_context.get("semantic_templates"),
                "semantic_templates_sha256": reference_context.get("semantic_templates_sha256"),
                "semantic_templates_blueprint_sha256": reference_context.get("semantic_templates_blueprint_sha256"),
                "semantic_templates_executable_sha256": reference_context.get("semantic_templates_executable_sha256"),
                "semantic_templates_projection_sha256": reference_context.get("semantic_templates_projection_sha256"),
            }
            expected_registry_sha256 = hashlib.sha256(
                json.dumps(reference_material, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
            ).hexdigest()
            try:
                dataset_families, field_families = _semantic_maps_from_descriptors(
                    reference_context.get("dataset_descriptors")
                )
                semantic_vocabulary = _validated_semantic_vocabulary(
                    reference_context.get("semantic_vocabulary"),
                    expected_dataset_families=dataset_families,
                    expected_field_families=field_families,
                )
                semantic_templates = _validated_semantic_templates(
                    reference_context.get("semantic_templates"),
                    semantic_vocabulary,
                )
            except ValueError as exc:
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_prompt_context",
                    "승인 축약 의미 어휘가 유효하지 않습니다.",
                ) from exc
            if (
                reference_context.get("contract_version") != "metadata.authoring.source-registry-context.v3"
                or reference_context.get("domain_id") != str(getattr(self, "domain_id", "") or "").strip()
                or not isinstance(reference_context.get("bindings"), dict)
                or not isinstance(reference_context.get("dataset_descriptors"), dict)
                or set(reference_context.get("bindings") or {}) != set(reference_context.get("dataset_descriptors") or {})
                or reference_context.get("semantic_vocabulary") != semantic_vocabulary
                or reference_context.get("semantic_templates") != semantic_templates
                or reference_context.get("semantic_templates_sha256")
                != hashlib.sha256(
                    json.dumps(semantic_templates, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
                ).hexdigest()
                or any(
                    not re.fullmatch(r"[0-9a-f]{64}", str(reference_context.get(key) or ""))
                    for key in (
                        "semantic_templates_blueprint_sha256",
                        "semantic_templates_executable_sha256",
                        "semantic_templates_projection_sha256",
                    )
                )
                or reference_context.get("registry_sha256") != expected_registry_sha256
            ):
                raise ContractError("metadata_dependency_error", "metadata_prompt_context", "승인 Source 참조 컨텍스트 hash 또는 도메인 결합이 유효하지 않습니다.")
        if bootstrap_fragment and not reference_context:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_prompt_context",
                "분할 초기 등록에는 승인 축약 의미 어휘가 필요합니다.",
            )
        invoke = kind in {"domain", "dataset"}
        if kind == "main_filter" and strict_inventory:
            invoke = _authoring_alias_only_manifest_patch(source_manifest) is None
        elif kind == "main_filter":
            invoke = True
        purpose = {
            "domain": "metadata_domain_annotation" if annotation_only else "metadata_domain_draft",
            "dataset": "metadata_dataset_draft",
            "main_filter": "metadata_main_filter_draft",
            "domain_policy": "metadata_domain_policy",
        }[kind]
        variables = {
            "authoring_kind": kind,
            "domain_id": str(getattr(self, "domain_id", "") or "").strip(),
            "environment": str(getattr(self, "environment", "") or "").strip(),
            "source_grounding_mode": grounding_mode,
            "source_text": source_text,
            "source_sha256": str(source_manifest.get("source_sha256") or ""),
            "source_manifest": source_manifest,
            "bootstrap_fragment": bootstrap_fragment,
        }
        approved_dataset_ids = sorted(
            str(card["id"])
            for card in ((reference_context.get("semantic_vocabulary") or {}).get("datasets") or [])
        )
        if reference_context and kind in {"domain", "dataset", "main_filter"}:
            variables["approved_semantic_vocabulary"] = deepcopy(
                reference_context["semantic_vocabulary"]
            )
            variables["source_registry_sha256"] = str(reference_context.get("registry_sha256") or "")
        if invoke:
            variables["output_schema"] = _authoring_output_schema(
                kind,
                annotation_only=annotation_only,
                bootstrap_fragment=bootstrap_fragment,
                approved_dataset_ids=approved_dataset_ids,
                approved_dataset_field_ids=(
                    _dataset_field_allowlists_from_vocabulary(
                        semantic_vocabulary,
                        reference_context.get("dataset_descriptors"),
                    )
                    if reference_context and kind == "dataset"
                    else None
                ),
                approved_semantic_vocabulary=(
                    semantic_vocabulary if reference_context else None
                ),
                proposal_source_sha256=(
                    str(source_manifest.get("source_sha256") or "")
                    if grounding_mode == "freeform_llm" and not annotation_only
                    else ""
                ),
            )
        if annotation_only:
            try:
                parsed = json.loads(blueprint_text)
            except json.JSONDecodeError as exc:
                raise ContractError("metadata_blueprint_invalid", "metadata_prompt_context", "블루프린트 JSON이 유효하지 않습니다.", {"line": exc.lineno}) from exc
            trusted = validate_executable_blueprint(
                parsed,
                expected_blueprint_sha256=blueprint_pin,
                expected_domain_id=variables["domain_id"],
                expected_environment=variables["environment"],
                source_manifest=source_manifest,
            )
            variables["default_annotations"] = trusted["default_annotations"]
            variables["blueprint_sha256"] = trusted["blueprint_sha256"]
        encoded = json.dumps(variables, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(encoded) > 192 * 1024:
            raise ContractError("metadata_budget_exceeded", "metadata_prompt_context", "등록 LLM 컨텍스트가 192KB를 초과했습니다.")
        return Data(data={"contract_version": "prompt.runtime-context.v1", "purpose": purpose, "invoke": bool(invoke), "variables": variables})
'''


AUTHORING_COMPONENT = r'''
import hashlib
import json
import os
import re
import unicodedata
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DataInput, DropdownInput, IntInput, MessageInput, MultilineInput, Output, SecretStrInput, StrInput
from lfx.schema.data import Data


AUTHORING_ALLOWED_KINDS = {
    "domain": {"metric", "process_group", "process_order", "product_group", "recipe"},
    "dataset": {"dataset", "field"},
    "main_filter": {"alias"},
}
CATALOG_COLLECTIONS = {
    "dataset": "datasets",
    "field": "fields",
    "metric": "metrics",
    "process_group": "process_groups",
    "product_group": "product_groups",
    "recipe": "recipes",
    "alias": "aliases",
}
V6_AUTHORING_COLLECTIONS = {
    "pending_collection": "agent_v6_pending_writes",
    "revision_collection": "agent_v6_metadata_revisions",
    "bundle_collection": "agent_v6_metadata_bundles",
    "active_collection": "agent_v6_metadata_active",
    "audit_collection": "agent_v6_authoring_audit",
}
AUTHORING_SUPPORTED_OPERATIONS = (
    "aggregate", "compare_fields", "derive", "filter", "join", "project", "rank", "sort",
    "transform_previous_result", "registered_call",
)
AUTHORING_FIELD_ROLE_ORDER = (
    "filter", "group", "join", "compare", "aggregate", "derive",
    "project", "sort", "rank", "metric", "output",
)


def _secret_text(value):
    if hasattr(value, "get_secret_value"):
        value = value.get_secret_value()
    return str(value or "").strip()


def _model_text(value):
    if isinstance(value, str):
        return value
    text = getattr(value, "text", None)
    if isinstance(text, str):
        return text
    content = getattr(value, "content", None)
    if isinstance(content, str):
        return content
    return str(value or "")


MAX_AUTHORING_MODEL_RESPONSE_BYTES = 192 * 1024


def _json_object(text):
    """Extract exactly one balanced, syntactically valid JSON object.

    Preamble, suffix text and Markdown fences are framing only. We never repair
    invalid escapes, single quotes, trailing commas, truncated JSON or multiple
    candidate objects.
    """

    if isinstance(text, dict):
        value = deepcopy(text)
        response_bytes = len(
            json.dumps(
                value,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        )
        if response_bytes > MAX_AUTHORING_MODEL_RESPONSE_BYTES:
            raise ContractError(
                "metadata_schema_error",
                "metadata_draft",
                "LLM draft exceeds the bounded response size.",
                {
                    "response_bytes": response_bytes,
                    "max_bytes": MAX_AUTHORING_MODEL_RESPONSE_BYTES,
                },
            )
        return value

    raw = str(text or "").strip()
    response_bytes = len(raw.encode("utf-8"))
    if not raw or response_bytes > MAX_AUTHORING_MODEL_RESPONSE_BYTES:
        raise ContractError(
            "metadata_schema_error",
            "metadata_draft",
            "LLM draft response size is invalid.",
            {
                "response_bytes": response_bytes,
                "max_bytes": MAX_AUTHORING_MODEL_RESPONSE_BYTES,
            },
        )

    spans = []
    start = None
    depth = 0
    in_string = False
    escaped = False
    for index, character in enumerate(raw):
        if start is None:
            if character == "{":
                start = index
                depth = 1
                in_string = False
                escaped = False
            elif character == "}":
                raise ContractError(
                    "metadata_schema_error",
                    "metadata_draft",
                    "LLM draft JSON framing is unbalanced.",
                    {"framing_reason": "unmatched_closing_brace"},
                )
            continue
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                spans.append((start, index + 1))
                start = None

    if start is not None:
        raise ContractError(
            "metadata_schema_error",
            "metadata_draft",
            "LLM draft JSON framing is incomplete.",
            {"framing_reason": "unclosed_object"},
        )
    if len(spans) != 1:
        raise ContractError(
            "metadata_schema_error",
            "metadata_draft",
            "LLM draft must contain exactly one JSON object.",
            {"object_count": len(spans)},
        )
    prefix = raw[: spans[0][0]]
    suffix = raw[spans[0][1] :]
    if any(character in "[]" for character in prefix + suffix):
        raise ContractError(
            "metadata_schema_error",
            "metadata_draft",
            "LLM draft JSON framing is invalid.",
            {"framing_reason": "array_wrapper"},
        )
    candidate = raw[spans[0][0] : spans[0][1]]
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ContractError(
            "metadata_schema_error",
            "metadata_draft",
            "LLM draft JSON is invalid.",
            {"line": exc.lineno, "column": exc.colno},
        ) from exc
    if not isinstance(value, dict):
        raise ContractError(
            "metadata_schema_error",
            "metadata_draft",
            "LLM draft must be an object.",
        )
    return value


def _invoke_authoring_json(model, prompt):
    """Invoke once, enabling JSON MIME mode only for the exact Google adapter."""

    model_type = type(model)
    google_adapter = any(
        str(getattr(candidate, "__module__", "") or "").casefold()
        == "langchain_google_genai.chat_models"
        and str(getattr(candidate, "__name__", "") or "").casefold()
        == "chatgooglegenerativeai"
        for candidate in getattr(model_type, "__mro__", ())
    )
    runner = model
    if (
        google_adapter
        and callable(getattr(model, "bind", None))
    ):
        try:
            runner = model.bind(response_mime_type="application/json")
        except (AttributeError, NotImplementedError, TypeError, ValueError):
            runner = model
    response = runner.invoke(prompt)
    if isinstance(response, dict):
        return _json_object(response)
    return _json_object(_model_text(response))


def _strict_json_value(text, *, label, expected_type):
    raw = str(text or "").strip()
    if not raw:
        return None
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else ""
        raw = raw.rsplit("```", 1)[0].strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError(
            "metadata_schema_error", "metadata_policy_input", f"{label} must be valid JSON.", {"line": exc.lineno}
        ) from exc
    if not isinstance(value, expected_type):
        expected = "array" if expected_type is list else "object"
        raise ContractError("metadata_schema_error", "metadata_policy_input", f"{label} must be a JSON {expected}.")
    return value


BOOTSTRAP_FRAGMENT_SECTIONS = {
    "domain": (
        "display_name", "description", "locale", "timezone",
        "metrics", "relations", "aliases", "entity_groups", "grains",
        "orderings", "predicates", "recipes", "output_profile",
    ),
    "dataset": ("datasets",),
    "main_filter": ("aliases",),
}
BOOTSTRAP_FRAGMENT_REQUIRED = {
    "domain": ("display_name",),
    "dataset": ("dataset_cards",),
    "main_filter": ("aliases",),
}
BOOTSTRAP_BRANCH_ORDER = ("domain", "dataset", "main_filter")

COMPACT_DATASET_CARD_OPTIONAL = (
    "display_name",
)
COMPACT_FIELD_CARD_OPTIONAL = ()


def _bootstrap_schema_refs(value):
    refs = set()
    if isinstance(value, dict):
        raw_ref = value.get("$ref")
        prefix = "#/$defs/"
        if isinstance(raw_ref, str) and raw_ref.startswith(prefix):
            refs.add(raw_ref[len(prefix) :])
        for child in value.values():
            refs.update(_bootstrap_schema_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_bootstrap_schema_refs(child))
    return refs


def _bootstrap_reachable_defs(properties, available_defs):
    pending = set(_bootstrap_schema_refs(properties))
    selected = {}
    while pending:
        name = sorted(pending)[0]
        pending.remove(name)
        if name in selected:
            continue
        definition = available_defs.get(name)
        if not isinstance(definition, dict):
            raise ContractError(
                "metadata_schema_error",
                "metadata_authoring",
                "분할 초기 등록 schema definition 참조가 유효하지 않습니다.",
                {"definition": name},
            )
        selected[name] = deepcopy(definition)
        pending.update(_bootstrap_schema_refs(definition) - set(selected))
    return {name: selected[name] for name in sorted(selected)}


def _bootstrap_partial_schema(value):
    if isinstance(value, list):
        return [_bootstrap_partial_schema(child) for child in value]
    if not isinstance(value, dict):
        return deepcopy(value)
    result = {
        key: _bootstrap_partial_schema(child)
        for key, child in value.items()
        if key != "required"
    }
    raw_type = result.get("type")
    if raw_type == "object" or (isinstance(raw_type, list) and "object" in raw_type):
        current_min = result.get("minProperties")
        result["minProperties"] = max(
            1,
            int(current_min) if isinstance(current_min, int) else 0,
        )
    return result


def _bootstrap_fragment_draft_schema(kind):
    sections = BOOTSTRAP_FRAGMENT_SECTIONS.get(kind)
    if sections is None:
        raise ContractError(
            "metadata_schema_error",
            "metadata_authoring",
            "분할 초기 등록 제안 종류가 유효하지 않습니다.",
            {"authoring_branch": str(kind or "")},
        )
    if kind == "domain":
        return load_schema("metadata-annotation-proposal.schema.json")
    if kind == "dataset":
        return load_schema("metadata-bootstrap-dataset-ir.schema.json")
    if kind == "main_filter":
        return load_schema("metadata-bootstrap-main-filter-ir.schema.json")
    full_schema = load_schema("metadata-authoring-draft.schema.json")
    owned = {section: deepcopy(full_schema["properties"][section]) for section in sections}
    return {
        "$schema": full_schema.get("$schema"),
        "title": f"metadata.authoring.{kind}.section-patch.v1",
        "type": "object",
        "additionalProperties": False,
        "minProperties": 1,
        "maxProperties": len(sections),
        "properties": deepcopy(owned),
        "$defs": _bootstrap_reachable_defs(owned, full_schema.get("$defs") or {}),
        "required": list(BOOTSTRAP_FRAGMENT_REQUIRED[kind]),
    }


def _bootstrap_output_schema(
    kind,
    source_sha256,
    approved_dataset_ids=(),
    approved_dataset_field_ids=None,
    approved_semantic_vocabulary=None,
):
    proposal_schema = deepcopy(load_schema("metadata-authoring-proposal.schema.json"))
    draft_schema = _bootstrap_fragment_draft_schema(kind)
    if kind == "main_filter" and approved_semantic_vocabulary is not None:
        draft_schema = _apply_main_filter_ir_allowlists(
            draft_schema, approved_semantic_vocabulary
        )
    approved_ids = sorted(
        {
            str(item).strip()
            for item in (approved_dataset_ids or ())
            if str(item).strip()
        }
    )
    if kind == "dataset" and approved_ids:
        field_allowlists = {
            dataset_id: sorted(
                {
                    str(field_id).strip()
                    for field_id in (
                        (approved_dataset_field_ids or {}).get(dataset_id) or []
                    )
                    if str(field_id).strip()
                }
            )
            for dataset_id in approved_ids
        }
        if any(not field_ids for field_ids in field_allowlists.values()):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_context",
                "승인 dataset별 field allowlist가 비어 있습니다.",
            )
        base_dataset_card = deepcopy(draft_schema["$defs"]["datasetCard"])
        base_field_card = deepcopy(draft_schema["$defs"]["fieldCard"])
        dataset_branches = []
        for dataset_id in approved_ids:
            allowed_fields = field_allowlists[dataset_id]
            dataset_card = deepcopy(base_dataset_card)
            dataset_card["properties"]["dataset_id"] = {
                "type": "string",
                "enum": [dataset_id],
            }
            field_card = deepcopy(base_field_card)
            field_card["properties"]["id"] = {
                "type": "string",
                "enum": allowed_fields,
            }
            field_card["properties"]["col"] = {
                "type": "string",
                "enum": allowed_fields,
            }
            dataset_card["properties"]["fields"]["items"] = field_card
            dataset_branches.append(dataset_card)
        draft_schema["$defs"]["datasetCard"] = {
            "oneOf": dataset_branches
        }
    for branch in proposal_schema.get("oneOf") or []:
        properties = branch.get("properties") if isinstance(branch, dict) else None
        required = branch.get("required") if isinstance(branch, dict) else None
        if not isinstance(properties, dict) or not isinstance(required, list):
            continue
        properties["source_sha256"] = {
            "type": "string",
            "const": source_sha256,
        }
        if "source_sha256" not in required:
            required.append("source_sha256")
        if (properties.get("status") or {}).get("const") == "complete":
            properties["draft"] = deepcopy(draft_schema)
    return proposal_schema


def _authoring_section_output_schema(
    kind,
    *,
    source_sha256,
    grounding_mode,
    annotation_only=False,
    approved_dataset_ids=(),
    approved_dataset_field_ids=None,
    approved_semantic_vocabulary=None,
):
    if kind == "domain":
        draft_schema = load_schema(
            "metadata-annotation-proposal.schema.json"
            if annotation_only
            else "metadata-authoring-draft.schema.json"
        )
    elif kind == "dataset":
        draft_schema = load_schema("metadata-bootstrap-dataset-ir.schema.json")
    elif kind == "main_filter":
        draft_schema = load_schema("metadata-bootstrap-main-filter-ir.schema.json")
        if approved_semantic_vocabulary is not None:
            draft_schema = _apply_main_filter_ir_allowlists(
                draft_schema,
                approved_semantic_vocabulary,
            )
    else:
        return {}

    approved_ids = sorted(
        {
            str(item).strip()
            for item in (approved_dataset_ids or ())
            if str(item).strip()
        }
    )
    if kind == "dataset" and approved_ids:
        field_allowlists = {
            dataset_id: sorted(
                {
                    str(field_id).strip()
                    for field_id in (
                        (approved_dataset_field_ids or {}).get(dataset_id) or []
                    )
                    if str(field_id).strip()
                }
            )
            for dataset_id in approved_ids
        }
        if any(not field_ids for field_ids in field_allowlists.values()):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_context",
                "승인 dataset별 field allowlist가 비어 있습니다.",
            )
        base_dataset_card = deepcopy(draft_schema["$defs"]["datasetCard"])
        base_field_card = deepcopy(draft_schema["$defs"]["fieldCard"])
        branches = []
        for dataset_id in approved_ids:
            card = deepcopy(base_dataset_card)
            card["properties"]["dataset_id"] = {
                "type": "string",
                "enum": [dataset_id],
            }
            field_card = deepcopy(base_field_card)
            field_card["properties"]["id"] = {
                "type": "string",
                "enum": field_allowlists[dataset_id],
            }
            field_card["properties"]["col"] = {
                "type": "string",
                "enum": field_allowlists[dataset_id],
            }
            card["properties"]["fields"]["items"] = field_card
            branches.append(card)
        draft_schema["$defs"]["datasetCard"] = {"oneOf": branches}

    if grounding_mode != "freeform_llm" or annotation_only:
        return draft_schema
    proposal_schema = deepcopy(
        load_schema("metadata-authoring-proposal.schema.json")
    )
    for branch in proposal_schema.get("oneOf") or []:
        properties = branch.get("properties") if isinstance(branch, dict) else None
        required = branch.get("required") if isinstance(branch, dict) else None
        if not isinstance(properties, dict) or not isinstance(required, list):
            continue
        properties["source_sha256"] = {
            "type": "string",
            "const": source_sha256,
        }
        if "source_sha256" not in required:
            required.append("source_sha256")
        if (properties.get("status") or {}).get("const") == "complete":
            properties["draft"] = deepcopy(draft_schema)
    return proposal_schema


def _bootstrap_schema_material(value):
    if isinstance(value, list):
        return [_bootstrap_schema_material(child) for child in value]
    if isinstance(value, dict):
        return {
            key: _bootstrap_schema_material(child)
            for key, child in value.items()
            if key != "description"
        }
    return deepcopy(value)


def _compact_detail_field_ids(raw_values, raw_fields, dataset_id):
    """Resolve compact detail entries to canonical field IDs, fail closed."""

    lookup = {}
    for raw_field in raw_fields:
        field_id = str(raw_field["id"])
        names = [field_id, raw_field.get("col")]
        names.extend(raw_field.get("physical_aliases") or [])
        names.extend(raw_field.get("aliases") or [])
        for name in names:
            key = re.sub(r"\s+", " ", str(name or "").strip()).casefold()
            if key:
                lookup.setdefault(key, set()).add(field_id)

    resolved = []
    seen = set()
    for detail_index, raw_value in enumerate(raw_values or []):
        key = re.sub(r"\s+", " ", str(raw_value or "").strip()).casefold()
        candidates = sorted(lookup.get(key) or [])
        if len(candidates) != 1:
            raise ContractError(
                "metadata_schema_error",
                "metadata_authoring",
                "기본 상세 필드를 데이터셋 내부 canonical field 하나로 확정할 수 없습니다.",
                {
                    "dataset_id": dataset_id,
                    "detail_index": detail_index,
                    "candidate_count": len(candidates),
                    "detail_value_sha256": hashlib.sha256(
                        str(raw_value or "").encode("utf-8")
                    ).hexdigest(),
                },
            )
        field_id = candidates[0]
        if field_id in seen:
            raise ContractError(
                "metadata_schema_error",
                "metadata_authoring",
                "기본 상세 필드가 canonical field 기준으로 중복되었습니다.",
                {
                    "dataset_id": dataset_id,
                    "detail_index": detail_index,
                    "field_id": field_id,
                },
            )
        seen.add(field_id)
        resolved.append(field_id)
    return resolved


def _normalized_descriptor_name(value):
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def _validated_dataset_descriptor(dataset_id, raw_descriptor):
    """Validate the engine-side source descriptor without trusting the UI node."""

    id_pattern = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    semantic_type_pattern = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
    allowed_descriptor_keys = {
        "physical_column", "semantic_type", "roles", "physical_aliases",
        "coercion", "nullable", "required_in_source", "timezone",
    }
    if not isinstance(raw_descriptor, dict) or set(raw_descriptor) != {
        "family", "fields", "proposal_exclusions", "dataset_template",
        "dataset_template_sha256",
    }:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_descriptors",
            "승인 dataset descriptor 계약이 닫혀 있지 않습니다.",
            {"dataset_id": str(dataset_id)},
        )
    family = str(raw_descriptor.get("family") or "").strip()
    raw_fields = raw_descriptor.get("fields")
    raw_exclusions = raw_descriptor.get("proposal_exclusions")
    if (
        not id_pattern.fullmatch(family)
        or not isinstance(raw_fields, dict)
        or not raw_fields
        or not isinstance(raw_exclusions, dict)
        or len(raw_exclusions) > 2048
    ):
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_descriptors",
            "승인 dataset family 또는 field descriptor가 유효하지 않습니다.",
            {"dataset_id": str(dataset_id)},
        )
    fields = {}
    for field_id in sorted(raw_fields):
        raw_field = raw_fields.get(field_id)
        if (
            not id_pattern.fullmatch(str(field_id))
            or not isinstance(raw_field, dict)
            or not {"physical_column", "semantic_type", "roles"} <= set(raw_field) <= allowed_descriptor_keys
        ):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "승인 field descriptor의 ID 또는 key 계약이 유효하지 않습니다.",
                {"dataset_id": str(dataset_id), "field_id": str(field_id)},
            )
        physical_column = str(raw_field.get("physical_column") or "").strip()
        semantic_type = str(raw_field.get("semantic_type") or "").strip()
        roles = raw_field.get("roles")
        physical_aliases = raw_field.get("physical_aliases") or []
        if (
            not physical_column
            or len(physical_column) > 256
            or not semantic_type_pattern.fullmatch(semantic_type)
            or not isinstance(roles, list)
            or not roles
            or len(roles) != len(set(roles))
            or not set(roles) <= set(AUTHORING_FIELD_ROLE_ORDER)
            or not isinstance(physical_aliases, list)
            or len(physical_aliases) != len(set(physical_aliases))
            or any(not isinstance(value, str) or not value.strip() for value in physical_aliases)
        ):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "승인 field descriptor의 물리 컬럼, 타입 또는 역할이 유효하지 않습니다.",
                {"dataset_id": str(dataset_id), "field_id": str(field_id)},
            )
        normalized = deepcopy(raw_field)
        normalized["physical_column"] = physical_column
        normalized["semantic_type"] = semantic_type
        normalized["roles"] = [
            role for role in AUTHORING_FIELD_ROLE_ORDER if role in roles
        ]
        if physical_aliases:
            normalized["physical_aliases"] = list(physical_aliases)
        fields[str(field_id)] = normalized
    try:
        dataset_template = _validated_dataset_template(
            dataset_id,
            raw_descriptor.get("dataset_template"),
            raw_descriptor.get("dataset_template_sha256"),
            fields,
        )
    except ValueError as exc:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_descriptors",
            "승인 dataset template 또는 hash가 유효하지 않습니다.",
            {"dataset_id": str(dataset_id)},
        ) from exc
    approved_names = {
        _normalized_descriptor_name(name)
        for field_id, descriptor in fields.items()
        for name in (
            field_id,
            descriptor.get("physical_column"),
            *(descriptor.get("physical_aliases") or []),
        )
        if _normalized_descriptor_name(name)
    }
    exclusion_reasons = {
        "source_projection_not_registered",
        "source_expression_before_alias",
        "legacy_source_name",
    }
    proposal_exclusions = {}
    folded_exclusions = set()
    for raw_name in sorted(raw_exclusions):
        folded = _normalized_descriptor_name(raw_name)
        policy = raw_exclusions.get(raw_name)
        if not isinstance(policy, dict):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "승인 proposal exclusion policy는 object여야 합니다.",
                {"dataset_id": str(dataset_id)},
            )
        reason = policy.get("reason_code")
        expected_policy_keys = (
            {"reason_code", "target_field_id"}
            if reason in {"source_expression_before_alias", "legacy_source_name"}
            else {"reason_code"}
        )
        if (
            not isinstance(raw_name, str)
            or not raw_name.strip()
            or len(raw_name) > 256
            or any(ord(character) < 32 for character in raw_name)
            or reason not in exclusion_reasons
            or set(policy) != expected_policy_keys
            or folded in folded_exclusions
            or folded in approved_names
        ):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "승인 proposal exclusion 이름 또는 사유가 유효하지 않습니다.",
                {"dataset_id": str(dataset_id)},
            )
        target_field_id = policy.get("target_field_id")
        if target_field_id is not None and target_field_id not in fields:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "승인 proposal exclusion target field가 존재하지 않습니다.",
                {"dataset_id": str(dataset_id)},
            )
        folded_exclusions.add(folded)
        proposal_exclusions[raw_name] = {
            key: policy[key] for key in sorted(policy)
        }
    return {
        "family": family,
        "fields": fields,
        "proposal_exclusions": proposal_exclusions,
        "dataset_template": dataset_template,
        "dataset_template_sha256": str(
            raw_descriptor.get("dataset_template_sha256") or ""
        ),
    }


def _descriptor_field_lookup(descriptor_fields):
    lookup = {}
    for field_id, descriptor in descriptor_fields.items():
        names = [field_id, descriptor.get("physical_column")]
        names.extend(descriptor.get("physical_aliases") or [])
        for name in names:
            key = _normalized_descriptor_name(name)
            if key:
                lookup.setdefault(key, set()).add(str(field_id))
    return lookup


def _resolve_compact_field_card(raw_field, dataset_descriptor, dataset_id, field_index):
    descriptor_fields = dataset_descriptor["fields"]
    exclusion_lookup = {
        _normalized_descriptor_name(name): policy
        for name, policy in dataset_descriptor["proposal_exclusions"].items()
    }
    lookup = _descriptor_field_lookup(descriptor_fields)
    id_name = _normalized_descriptor_name(raw_field.get("id"))
    col_name = _normalized_descriptor_name(raw_field.get("col"))
    id_candidates = set(lookup.get(id_name) or [])
    col_candidates = set(lookup.get(col_name) or [])

    def fail_resolution(code, stage, message, candidate_count):
        raise ContractError(
            code,
            stage,
            message,
            {
                "dataset_id": str(dataset_id),
                "field_index": field_index,
                "candidate_count": candidate_count,
                "field_id_sha256": hashlib.sha256(
                    str(raw_field.get("id") or "").encode("utf-8")
                ).hexdigest(),
                "physical_column_sha256": hashlib.sha256(
                    str(raw_field.get("col") or "").encode("utf-8")
                ).hexdigest(),
                "operator_action": "review_source_registry_descriptor_or_exclusion",
            },
        )

    if len(col_candidates) > 1 or len(id_candidates) > 1:
        fail_resolution(
            "metadata_dependency_error",
            "metadata_source_descriptors",
            "LLM field card를 동일 dataset의 승인 descriptor 하나로 확정할 수 없습니다.",
            max(len(col_candidates), len(id_candidates)),
        )

    applied_exclusion = None
    binding_corrected = False
    if col_candidates:
        field_id = sorted(col_candidates)[0]
        if id_candidates and field_id not in id_candidates:
            fail_resolution(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "LLM field id와 물리 col이 서로 다른 승인 descriptor를 가리킵니다.",
                0,
            )
        binding_corrected = not id_candidates
    else:
        col_policy = exclusion_lookup.get(col_name)
        if col_policy is None:
            fail_resolution(
                "metadata_registry_drift",
                "metadata_source_registry",
                "LLM이 제안한 물리 col이 승인 descriptor나 명시적 exclusion에 없습니다. 작업자가 아니라 운영자가 Source Registry를 검토해야 합니다.",
                0,
            )
        reason_code = str(col_policy.get("reason_code") or "")
        target_field_id = col_policy.get("target_field_id")
        applied_exclusion = {
            "name_sha256": hashlib.sha256(
                str(raw_field.get("col") or "").encode("utf-8")
            ).hexdigest(),
            "reason_code": reason_code,
            "target_field_id": str(target_field_id or ""),
        }
        if target_field_id is None:
            if id_candidates:
                fail_resolution(
                    "metadata_dependency_error",
                    "metadata_source_descriptors",
                    "노출 제외된 물리 col을 승인 field id에 결합할 수 없습니다.",
                    0,
                )
            return None, False, applied_exclusion
        field_id = str(target_field_id)
        if id_candidates and field_id not in id_candidates:
            fail_resolution(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "원천 alias exclusion target과 LLM field id가 충돌합니다.",
                0,
            )
        binding_corrected = True

    descriptor = descriptor_fields[field_id]
    proposed_roles = set(raw_field.get("roles") or [])
    approved_roles = set(descriptor.get("roles") or [])
    if not proposed_roles <= approved_roles:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_descriptors",
            "LLM field role이 승인 descriptor 역할 범위를 벗어났습니다.",
            {"dataset_id": str(dataset_id), "field_id": field_id},
        )
    proposed_aliases = set(raw_field.get("physical_aliases") or [])
    approved_names = {
        str(field_id),
        str(descriptor.get("physical_column") or ""),
        *[str(value) for value in descriptor.get("physical_aliases") or []],
    }
    if proposed_aliases and not proposed_aliases <= approved_names:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_descriptors",
            "LLM physical alias가 승인 descriptor 범위를 벗어났습니다.",
            {"dataset_id": str(dataset_id), "field_id": field_id},
        )
    for key in ("coercion", "timezone"):
        if key in raw_field and raw_field.get(key) != descriptor.get(key):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "LLM 기술 field 속성이 승인 descriptor와 충돌합니다.",
                {"dataset_id": str(dataset_id), "field_id": field_id, "attribute": key},
            )
    if raw_field.get("required_in_source") is True and descriptor.get("required_in_source") is not True:
        raise ContractError(
            "metadata_dependency_error", "metadata_source_descriptors",
            "LLM required_in_source가 승인 descriptor와 충돌합니다.",
            {"dataset_id": str(dataset_id), "field_id": field_id},
        )
    if raw_field.get("nullable") is False and descriptor.get("nullable") is not False:
        raise ContractError(
            "metadata_dependency_error", "metadata_source_descriptors",
            "LLM nullable이 승인 descriptor와 충돌합니다.",
            {"dataset_id": str(dataset_id), "field_id": field_id},
        )
    return field_id, binding_corrected, applied_exclusion


def _merge_equivalent_compact_field_cards(existing, incoming, dataset_id, field_id):
    """Merge duplicate provider cards only after one approved descriptor wins."""

    merged = deepcopy(existing)
    additive_list_keys = {"aliases"}
    bounded_list_keys = {"allowed_filter_operators", "allowed_rollups"}
    scalar_keys = {"unit", "null_policy", "case_policy", "multiplier"}
    for key in sorted(additive_list_keys):
        left = merged.get(key) or []
        right = incoming.get(key) or []
        if not isinstance(left, list) or not isinstance(right, list):
            raise ContractError(
                "metadata_schema_error", "metadata_authoring",
                "동일 승인 field의 선택 목록 속성을 병합할 수 없습니다.",
                {"dataset_id": str(dataset_id), "field_id": str(field_id), "attribute": key},
            )
        if left or right:
            merged[key] = sorted(
                {str(value) for value in [*left, *right] if str(value)}
            )
    for key in sorted(bounded_list_keys):
        if key not in incoming:
            continue
        right = incoming.get(key)
        if not isinstance(right, list):
            raise ContractError(
                "metadata_schema_error", "metadata_authoring",
                "동일 승인 field의 허용 목록 속성을 병합할 수 없습니다.",
                {"dataset_id": str(dataset_id), "field_id": str(field_id), "attribute": key},
            )
        if key in merged:
            left = merged.get(key)
            if not isinstance(left, list) or set(left) != set(right):
                raise ContractError(
                    "metadata_schema_error", "metadata_authoring",
                    "동일 승인 field의 허용 목록이 서로 충돌합니다.",
                    {"dataset_id": str(dataset_id), "field_id": str(field_id), "attribute": key},
                )
        merged[key] = sorted({str(value) for value in right if str(value)})
    for key in sorted(scalar_keys):
        if key not in incoming:
            continue
        if key in merged and merged.get(key) != incoming.get(key):
            raise ContractError(
                "metadata_schema_error", "metadata_authoring",
                "동일 승인 field의 선택 속성이 서로 충돌합니다.",
                {"dataset_id": str(dataset_id), "field_id": str(field_id), "attribute": key},
            )
        merged[key] = deepcopy(incoming[key])
    return merged


def _expand_compact_dataset_fragment(fragment, dataset_descriptors=None, reconciliation_out=None):
    """Expand the LLM-facing compact Dataset IR into the full draft section.

    The LLM never receives physical/type/role descriptors.  This deterministic
    step resolves its compact field cards against the operator-approved source
    registry and fills omitted cards from that same dataset only.
    """

    dataset_descriptors = dataset_descriptors if isinstance(dataset_descriptors, dict) else {}
    datasets = {}
    completed_pairs = []
    normalized_pairs = []
    applied_exclusion_rows = []
    corrected_binding_pairs = []
    applied_dataset_templates = []
    approved_field_count = 0
    model_field_count = 0
    for dataset_index, raw_card in enumerate(fragment.get("dataset_cards") or []):
        dataset_id = str(raw_card["dataset_id"])
        if dataset_id in datasets:
            raise ContractError(
                "metadata_schema_error",
                "metadata_authoring",
                "압축 데이터셋 등록 IR에 중복 dataset_id가 있습니다.",
                {"dataset_id": dataset_id, "dataset_index": dataset_index},
            )
        if dataset_id not in dataset_descriptors:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "동일 dataset의 승인 source descriptor가 없습니다.",
                {"dataset_id": dataset_id},
            )
        descriptor = _validated_dataset_descriptor(
            dataset_id, dataset_descriptors[dataset_id]
        )
        applied_dataset_templates.append(
            {
                "dataset_id": dataset_id,
                "dataset_template_sha256": descriptor[
                    "dataset_template_sha256"
                ],
            }
        )
        descriptor_fields = descriptor["fields"]
        approved_field_count += len(descriptor_fields)
        resolved_model_fields = {}
        for field_index, raw_field in enumerate(raw_card["fields"]):
            field_id, binding_corrected, applied_exclusion = _resolve_compact_field_card(
                raw_field, descriptor, dataset_id, field_index
            )
            if applied_exclusion is not None:
                applied_exclusion_rows.append(
                    {"dataset_id": dataset_id, **applied_exclusion}
                )
            if field_id is None:
                model_field_count += 1
                continue
            if binding_corrected:
                corrected_binding_pairs.append(
                    {
                        "dataset_id": dataset_id,
                        "field_id": field_id,
                        "proposed_id_sha256": hashlib.sha256(
                            str(raw_field.get("id") or "").encode("utf-8")
                        ).hexdigest(),
                        "proposed_column_sha256": hashlib.sha256(
                            str(raw_field.get("col") or "").encode("utf-8")
                        ).hexdigest(),
                    }
                )
            if field_id in resolved_model_fields:
                resolved_model_fields[field_id] = _merge_equivalent_compact_field_cards(
                    resolved_model_fields[field_id],
                    raw_field,
                    dataset_id,
                    field_id,
                )
            else:
                resolved_model_fields[field_id] = raw_field
            model_field_count += 1
            normalized_pairs.append({"dataset_id": dataset_id, "field_id": field_id})

        fields = {}
        for field_id in sorted(descriptor_fields):
            approved = descriptor_fields[field_id]
            binding = deepcopy(approved)
            raw_field = resolved_model_fields.get(field_id)
            if raw_field is None:
                completed_pairs.append({"dataset_id": dataset_id, "field_id": field_id})
                fields[field_id] = binding
                continue
            fields[field_id] = binding
        dataset = deepcopy(descriptor["dataset_template"])
        dataset["family"] = descriptor["family"]
        dataset["fields"] = {key: fields[key] for key in sorted(fields)}
        for key in COMPACT_DATASET_CARD_OPTIONAL:
            if key in raw_card:
                dataset[key] = deepcopy(raw_card[key])
        datasets[dataset_id] = dataset
    evidence = {
        "contract_version": "metadata.dataset-registry-reconciliation.v1",
        "approved_field_count": approved_field_count,
        "model_field_count": model_field_count,
        "completed_field_count": len(completed_pairs),
        "applied_exclusion_count": len(applied_exclusion_rows),
        "applied_exclusions_sha256": sha256_json(
            sorted(
                applied_exclusion_rows,
                key=lambda item: (
                    item["dataset_id"],
                    item["name_sha256"],
                    item["reason_code"],
                    item["target_field_id"],
                ),
            )
        ),
        "corrected_binding_count": len(corrected_binding_pairs),
        "corrected_bindings_sha256": sha256_json(
            sorted(
                corrected_binding_pairs,
                key=lambda item: (
                    item["dataset_id"],
                    item["field_id"],
                    item["proposed_id_sha256"],
                    item["proposed_column_sha256"],
                ),
            )
        ),
        "compiler_owned_dataset_template_count": len(applied_dataset_templates),
        "compiler_owned_dataset_templates_sha256": sha256_json(
            sorted(
                applied_dataset_templates,
                key=lambda item: item["dataset_id"],
            )
        ),
        "completed_fields_sha256": sha256_json(
            sorted(completed_pairs, key=lambda item: (item["dataset_id"], item["field_id"]))
        ),
        "normalized_fields_sha256": sha256_json(
            sorted(normalized_pairs, key=lambda item: (item["dataset_id"], item["field_id"]))
        ),
    }
    if isinstance(reconciliation_out, dict):
        reconciliation_out.clear()
        reconciliation_out.update(evidence)
    return {"datasets": {key: datasets[key] for key in sorted(datasets)}}


def _validate_bootstrap_fragment(
    fragment,
    kind,
    dataset_descriptors=None,
    semantic_vocabulary=None,
    reconciliation_out=None,
    main_filter_reconciliation_out=None,
    domain_already_expanded=False,
):
    if kind == "domain" and domain_already_expanded:
        expected = set(BOOTSTRAP_FRAGMENT_SECTIONS["domain"])
        if not isinstance(fragment, dict) or set(fragment) != expected:
            raise ContractError(
                "metadata_schema_error",
                "metadata_semantic_templates",
                "승인 도메인 템플릿 확장 결과의 root 계약이 닫혀 있지 않습니다.",
            )
        return deepcopy(fragment)
    schema = _bootstrap_fragment_draft_schema(kind)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(fragment),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        first = errors[0]
        path = ".".join(str(part) for part in first.absolute_path) or "$"
        raise ContractError(
            "metadata_schema_error",
            "metadata_authoring",
            "분할 초기 등록 제안 조각이 폐쇄형 소유권 계약과 일치하지 않습니다.",
            {
                "authoring_branch": kind,
                "path": path,
                "reason": first.message[:400],
            },
        )
    if kind == "dataset":
        return _expand_compact_dataset_fragment(
            fragment,
            dataset_descriptors=dataset_descriptors,
            reconciliation_out=reconciliation_out,
        )
    if kind == "main_filter":
        return _expand_compact_main_filter_fragment(
            fragment,
            approved_semantic_vocabulary=semantic_vocabulary,
            reconciliation_out=main_filter_reconciliation_out,
        )
    return deepcopy(fragment)


def _merge_bootstrap_fragments(
    fragments,
    dataset_descriptors=None,
    semantic_vocabulary=None,
    reconciliation_out=None,
    main_filter_reconciliation_out=None,
    domain_already_expanded=False,
):
    # Contract identity is compiler-owned, never model-authored.  This avoids
    # relying on provider-specific handling of JSON Schema ``const`` while the
    # closed fragment schemas still reject any model-supplied root header.
    merged = {"contract_version": "metadata.authoring.draft.v1"}
    section_owners = {}
    merged_aliases = {}
    alias_owners = {}
    for kind in BOOTSTRAP_BRANCH_ORDER:
        fragment = _validate_bootstrap_fragment(
            fragments.get(kind),
            kind,
            dataset_descriptors=dataset_descriptors if kind == "dataset" else None,
            semantic_vocabulary=(
                semantic_vocabulary if kind == "main_filter" else None
            ),
            reconciliation_out=reconciliation_out if kind == "dataset" else None,
            main_filter_reconciliation_out=(
                main_filter_reconciliation_out if kind == "main_filter" else None
            ),
            domain_already_expanded=(
                bool(domain_already_expanded) if kind == "domain" else False
            ),
        )
        for section in BOOTSTRAP_FRAGMENT_SECTIONS[kind]:
            if section not in fragment:
                continue
            value = fragment[section]
            if section == "aliases":
                for alias in sorted(value):
                    if alias in merged_aliases and merged_aliases[alias] != value[alias]:
                        merged_aliases[alias] = _merge_natural_alias_card(
                            merged_aliases[alias], value[alias], alias
                        )
                    if alias not in merged_aliases:
                        merged_aliases[alias] = deepcopy(value[alias])
                        alias_owners[alias] = kind
                continue
            if section in merged:
                raise ContractError(
                    "metadata_schema_error",
                    "metadata_authoring",
                    "분할 초기 등록 root section 소유권이 충돌합니다.",
                    {
                        "section": section,
                        "first_branch": section_owners[section],
                        "second_branch": kind,
                    },
                )
            merged[section] = deepcopy(value)
            section_owners[section] = kind
    if merged_aliases:
        baseline_aliases = (
            fragments.get("domain", {}).get("aliases")
            if domain_already_expanded
            and isinstance(fragments.get("domain"), dict)
            else {}
        )
        merged_aliases, alias_conflict_resolution = _resolve_natural_alias_conflicts(
            merged_aliases,
            baseline_aliases if isinstance(baseline_aliases, dict) else {},
        )
        if isinstance(main_filter_reconciliation_out, dict):
            main_filter_reconciliation_out["alias_conflict_resolution"] = (
                alias_conflict_resolution
            )
        merged["aliases"] = {
            alias: merged_aliases[alias]
            for alias in sorted(merged_aliases)
        }
    return merged


def _expand_bootstrap_domain_annotation(
    annotation,
    *,
    semantic_templates,
    semantic_vocabulary,
):
    """Attach only operator-approved executable semantics to LLM annotations."""

    annotation_schema = load_schema("metadata-annotation-proposal.schema.json")
    annotation_errors = sorted(
        Draft202012Validator(annotation_schema).iter_errors(annotation),
        key=lambda item: (list(item.absolute_path), item.message),
    )
    if annotation_errors:
        exc = annotation_errors[0]
        raise ContractError(
            "metadata_schema_error",
            "metadata_authoring",
            "도메인 자연어 제안은 표시 이름과 설명만 포함해야 합니다.",
            {"path": list(exc.absolute_path)},
        )
    try:
        templates = _validated_semantic_templates(
            semantic_templates, semantic_vocabulary
        )
    except ValueError as exc:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_semantic_templates",
            "승인된 도메인 의미 템플릿이 유효하지 않습니다.",
        ) from exc
    fragment = {
        "display_name": str(annotation["display_name"]),
        "description": str(annotation["description"]),
        "locale": str(templates["locale"]),
        "timezone": str(templates["timezone"]),
        **{
            section: deepcopy(templates[section])
            for section in _SEMANTIC_TEMPLATE_SECTIONS
        },
        "aliases": deepcopy(templates["aliases"]),
        # Execution-lane compatibility is compiler-owned. Presentation and
        # specialized policy remain separate Domain Policy Flow inputs.
        "output_profile": deepcopy(templates["planner_policy"]),
    }
    evidence = {
        "contract_version": "metadata.domain-template-expansion.v1",
        "template_contract_version": templates["contract_version"],
        "annotation_sha256": sha256_json(annotation),
        "semantic_templates_sha256": sha256_json(templates),
        "planner_policy_sha256": sha256_json(templates["planner_policy"]),
        "section_counts": {
            section: len(fragment[section])
            for section in (*_SEMANTIC_TEMPLATE_SECTIONS, "aliases")
        },
    }
    return fragment, evidence


def _authoring_invocation_draft(
    component,
    *,
    input_name,
    expected_purpose,
    required,
    expected_output_schema=None,
    expected_runtime_context_sha256="",
):
    raw = getattr(component, input_name, None)
    invocation = getattr(raw, "data", raw)
    invocation = invocation if isinstance(invocation, dict) else {}
    calls = int(invocation.get("llm_calls") or 0) if invocation else 0
    usage = deepcopy(getattr(component, "_observed_authoring_llm_usage", None) or {})
    usage.setdefault("draft_llm_calls", 0)
    usage.setdefault("annotation_llm_calls", 0)
    bucket = "annotation_llm_calls" if expected_purpose == "metadata_domain_annotation" else "draft_llm_calls"
    usage[bucket] = int(usage.get(bucket) or 0) + calls
    usage["repair_llm_calls"] = 0
    component._observed_authoring_llm_usage = usage
    if not required:
        if calls != 0:
            raise ContractError(
                "metadata_policy_error",
                "metadata_llm_boundary",
                "결정론적 등록 분기에서 LLM이 호출되었습니다.",
                {"input_name": input_name, "expected_purpose": expected_purpose, "llm_calls": calls},
            )
        return None
    if (
        invocation.get("contract_version") != "llm.invocation.v1"
        or invocation.get("purpose") != expected_purpose
        or invocation.get("status") != "ok"
        or calls != 1
    ):
        invocation_error = (
            invocation.get("error") if isinstance(invocation.get("error"), dict) else {}
        )
        provider_error_type = str(
            invocation_error.get("provider_error_type") or ""
        )[:80]
        if not provider_error_type.isidentifier():
            provider_error_type = ""
        provider_error_status = str(
            invocation_error.get("provider_error_status") or ""
        )[:80]
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", provider_error_status):
            provider_error_status = ""
        provider_error_code = str(
            invocation_error.get("provider_error_code") or ""
        )[:80]
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", provider_error_code):
            provider_error_code = ""
        provider_binding = str(
            invocation.get("provider_schema_binding") or ""
        )[:80]
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,79}", provider_binding):
            provider_binding = ""
        raise ContractError(
            "metadata_llm_unavailable",
            "metadata_draft",
            "외부 Prompt/LLM 노드의 검증된 단일 호출 결과가 필요합니다.",
            {
                "input_name": input_name,
                "expected_purpose": expected_purpose,
                "llm_calls": calls,
                "error_type": provider_error_type,
                "reason": provider_error_status,
                "provider_error_code": provider_error_code,
                "provider_schema_binding": provider_binding,
                "invocation_error_code": str(
                    invocation_error.get("code") or ""
                )[:80],
            },
        )
    prompt_bundle_sha256 = str(invocation.get("prompt_bundle_sha256") or "")
    runtime_context_sha256 = str(
        invocation.get("runtime_context_sha256") or ""
    )
    if not re.fullmatch(r"[0-9a-f]{64}", prompt_bundle_sha256):
        raise ContractError(
            "metadata_dependency_error",
            "metadata_llm_prompt_binding",
            "LLM invocation prompt bundle evidence is invalid.",
            {
                "input_name": input_name,
                "expected_purpose": expected_purpose,
            },
        )
    if expected_runtime_context_sha256:
        if (
            not re.fullmatch(
                r"[0-9a-f]{64}", str(expected_runtime_context_sha256)
            )
            or runtime_context_sha256 != expected_runtime_context_sha256
        ):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_llm_prompt_binding",
                "LLM invocation runtime context evidence does not match the authoritative context.",
                {
                    "input_name": input_name,
                    "expected_purpose": expected_purpose,
                },
            )
    if expected_output_schema is not None:
        expected_schema_sha256 = sha256_json(expected_output_schema)
        evidence = invocation.get("schema_binding_evidence")
        binding_status = (
            str(evidence.get("binding_status") or "")
            if isinstance(evidence, dict)
            else ""
        )
        provider_binding = str(invocation.get("provider_schema_binding") or "")
        provider_schema_sha256 = (
            str(evidence.get("provider_schema_sha256") or "")
            if isinstance(evidence, dict)
            else ""
        )
        projection = (
            str(evidence.get("projection") or "")
            if isinstance(evidence, dict)
            else ""
        )
        google_projection_valid = (
            binding_status == "google_native_json_schema"
            and projection == "google_supported_json_schema_subset.v6"
            and bool(re.fullmatch(r"[0-9a-f]{64}", provider_schema_sha256))
        )
        portable_projection_valid = (
            binding_status == "portable_prompt_and_compiler_validation"
            and projection == "none"
            and provider_schema_sha256 == ""
        )
        if (
            not isinstance(evidence, dict)
            or set(evidence) != {
                "contract_version", "binding_status", "projection",
                "authoritative_schema_sha256", "provider_schema_sha256",
            }
            or evidence.get("contract_version") != "llm.schema-binding.evidence.v1"
            or provider_binding != binding_status
            or evidence.get("authoritative_schema_sha256") != expected_schema_sha256
            or not (google_projection_valid or portable_projection_valid)
        ):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_llm_schema_binding",
                "LLM 호출의 스키마 결합 증적이 authoritative runtime schema와 일치하지 않습니다.",
                {
                    "input_name": input_name,
                    "expected_purpose": expected_purpose,
                    "expected_schema_sha256": expected_schema_sha256,
                    "binding_status": binding_status,
                },
            )
    response_text = str(invocation.get("response_text") or "")
    response_bytes = len(response_text.encode("utf-8"))
    observed_response_sha256 = hashlib.sha256(
        response_text.encode("utf-8")
    ).hexdigest()
    if invocation.get("response_sha256") != observed_response_sha256:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_llm_response_binding",
            "LLM invocation response hash does not match the response body.",
            {
                "input_name": input_name,
                "expected_purpose": expected_purpose,
                "response_bytes": response_bytes,
            },
        )
    try:
        parsed = _json_object(response_text)
    except ContractError as exc:
        details = deepcopy(exc.details) if isinstance(exc.details, dict) else {}
        details.update(
            {
                "input_name": input_name,
                "expected_purpose": expected_purpose,
                "response_bytes": response_bytes,
                "response_sha256": hashlib.sha256(
                    response_text.encode("utf-8")
                ).hexdigest(),
            }
        )
        raise ContractError(
            exc.code,
            exc.stage,
            exc.public_message,
            details,
            exc.retryable,
        ) from exc
    if expected_output_schema is not None:
        schema_errors = sorted(
            Draft202012Validator(expected_output_schema).iter_errors(parsed),
            key=lambda item: (list(item.absolute_path), item.validator or ""),
        )
        if schema_errors:
            exc = schema_errors[0]
            raise ContractError(
                "metadata_schema_error",
                "metadata_llm_schema_validation",
                "LLM output does not satisfy the authoritative metadata schema.",
                {
                    "input_name": input_name,
                    "expected_purpose": expected_purpose,
                    "path": list(exc.absolute_path),
                    "validator": str(exc.validator or "")[:80],
                    "response_bytes": response_bytes,
                    "response_sha256": observed_response_sha256,
                },
            )
        observed_bindings = deepcopy(
            getattr(component, "_observed_authoring_schema_bindings", None) or {}
        )
        if expected_purpose in observed_bindings:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_llm_schema_binding",
                "Duplicate LLM schema-binding evidence was observed for one authoring purpose.",
                {"expected_purpose": expected_purpose},
            )
        observed_bindings[expected_purpose] = {
            "contract_version": "metadata.llm-schema-binding-summary.v1",
            "purpose": expected_purpose,
            "invocation_count": 1,
            "provider_schema_binding": provider_binding,
            "binding_status": binding_status,
            "projection": projection,
            "authoritative_schema_sha256": expected_schema_sha256,
            "provider_schema_sha256": provider_schema_sha256,
            "runtime_output_schema_sha256": expected_schema_sha256,
            "raw_prompt_persisted": False,
            "raw_response_persisted": False,
        }
        component._observed_authoring_schema_bindings = observed_bindings
    return parsed


_CLARIFICATION_TECHNICAL_PATTERN = re.compile(
    r"(?:canonical|dataset[ _-]?id|field[ _-]?id|physical(?:[ _-]?column)?|"
    r"semantic(?:[ _-]?type)?|json|dsl|config_ref|query_ref|schema|"
    r"source[ _-]?registry|registry|물리\s*컬럼|시맨틱\s*타입|"
    r"기술\s*문법|내부\s*ID|레지스트리|스키마)",
    re.IGNORECASE,
)
_GENERIC_BUSINESS_CLARIFICATION = (
    "어떤 업무 데이터나 수치를 뜻하는지 자연어로 설명해 주세요."
)


def _worker_safe_clarification(questions, missing_fields):
    safe_questions = []
    for raw_question in questions if isinstance(questions, list) else []:
        question = re.sub(r"\s+", " ", str(raw_question or "").strip())
        if not question:
            continue
        if _CLARIFICATION_TECHNICAL_PATTERN.search(question):
            question = _GENERIC_BUSINESS_CLARIFICATION
        if question not in safe_questions:
            safe_questions.append(question[:400])
        if len(safe_questions) == 3:
            break
    if not safe_questions:
        safe_questions = [_GENERIC_BUSINESS_CLARIFICATION]

    safe_missing = []
    for raw_field in missing_fields if isinstance(missing_fields, list) else []:
        token = str(raw_field or "").casefold()
        if any(marker in token for marker in ("metric", "formula", "수치", "계산")):
            label = "업무 수치 설명"
        elif any(marker in token for marker in ("relation", "join", "관계", "연결")):
            label = "업무 데이터 관계 설명"
        elif any(marker in token for marker in ("filter", "alias", "predicate", "조건", "별칭")):
            label = "조회 조건 설명"
        else:
            label = "업무 데이터 설명"
        if label not in safe_missing:
            safe_missing.append(label)
    if not safe_missing:
        safe_missing = ["업무 데이터 설명"]
    return safe_questions, safe_missing


def _unwrap_freeform_authoring_proposal(raw_proposal, *, source_sha256):
    """Validate the model's two-state proposal and return its complete draft.

    This gate deliberately runs before the metadata compiler and before any
    MongoDB write.  A worker may write arbitrary prose; the model may either
    produce one closed candidate or ask up to three factual questions.  It may
    never emit a partial candidate that silently enters the approval path.
    """

    proposal = deepcopy(raw_proposal) if isinstance(raw_proposal, dict) else {}
    status = str(proposal.get("status") or "")
    expected_source_sha256 = str(source_sha256 or "")
    common_keys = {"contract_version", "status", "source_sha256"}
    if (
        proposal.get("contract_version") != "metadata.authoring.proposal.v1"
        or not re.fullmatch(r"[0-9a-f]{64}", expected_source_sha256)
        or proposal.get("source_sha256") != expected_source_sha256
    ):
        raise ContractError(
            "metadata_schema_error",
            "metadata_authoring_proposal",
            "자유형 자연어 등록 제안이 원문 SHA-256과 결합되지 않았습니다.",
            {"expected_source_sha256": expected_source_sha256},
        )
    proposal_sha256 = sha256_json(proposal)
    if status == "complete":
        if set(proposal) != common_keys | {"draft"} or not isinstance(proposal.get("draft"), dict):
            raise ContractError(
                "metadata_schema_error",
                "metadata_authoring_proposal",
                "완료 제안은 폐쇄형 draft 하나만 포함해야 합니다.",
            )
        draft = deepcopy(proposal["draft"])
        evidence = {
            "contract_version": "metadata.authoring.proposal.validation.v1",
            "proposal_contract_version": "metadata.authoring.proposal.v1",
            "status": "complete",
            "source_sha256": expected_source_sha256,
            "proposal_sha256": proposal_sha256,
            "draft_sha256": sha256_json(draft),
        }
        return draft, evidence
    if status == "needs_clarification":
        if set(proposal) != common_keys | {"clarification"}:
            raise ContractError(
                "metadata_schema_error",
                "metadata_authoring_proposal",
                "확인 질문 제안에는 draft 또는 저장 후보 필드를 포함할 수 없습니다.",
            )
        clarification = proposal.get("clarification")
        if not isinstance(clarification, dict) or set(clarification) != {"questions", "missing_fields"}:
            raise ContractError(
                "metadata_schema_error",
                "metadata_authoring_proposal",
                "확인 질문 payload가 폐쇄형 계약과 일치하지 않습니다.",
            )
        questions = clarification.get("questions")
        missing_fields = clarification.get("missing_fields")
        if (
            not isinstance(questions, list)
            or not 1 <= len(questions) <= 3
            or len(set(questions)) != len(questions)
            or any(not isinstance(item, str) or not item.strip() or len(item) > 400 for item in questions)
            or not isinstance(missing_fields, list)
            or len(missing_fields) > 32
            or len(set(missing_fields)) != len(missing_fields)
            or any(not isinstance(item, str) or not item.strip() or len(item) > 128 for item in missing_fields)
        ):
            raise ContractError(
                "metadata_schema_error",
                "metadata_authoring_proposal",
                "확인 질문의 개수 또는 길이가 허용 범위를 벗어났습니다.",
            )
        raise ContractError(
            "metadata_clarification_required",
            "metadata_clarification",
            "메타데이터를 추측하지 않고 작업자 확인이 필요한 항목을 반환했습니다.",
            {
                "contract_version": "metadata.authoring.clarification.v1",
                "questions": [item.strip() for item in questions],
                "missing_fields": [item.strip() for item in missing_fields],
                "source_sha256": expected_source_sha256,
                "proposal_sha256": proposal_sha256,
            },
        )
    raise ContractError(
        "metadata_schema_error",
        "metadata_authoring_proposal",
        "자유형 자연어 등록 제안 status가 유효하지 않습니다.",
        {"status": status},
    )


def _unwrap_bootstrap_authoring_proposal(
    raw_proposal,
    *,
    kind,
    source_sha256,
    composite_source_sha256,
):
    try:
        return _unwrap_freeform_authoring_proposal(
            raw_proposal,
            source_sha256=source_sha256,
        )
    except ContractError as exc:
        if exc.code != "metadata_clarification_required" or not isinstance(exc.details, dict):
            raise
        details = deepcopy(exc.details)
        questions = list(details.get("questions") or [])
        branch_label = {
            "domain": "업무 정의",
            "dataset": "업무 데이터",
            "main_filter": "조회 조건",
        }.get(kind, "업무 설명")
        details["questions"] = [
            f"[{branch_label} {index}] {question}"[:400]
            for index, question in enumerate(questions, start=1)
        ]
        details["missing_fields"] = [
            f"{branch_label}: {field}"[:128]
            for field in list(details.get("missing_fields") or [])
        ]
        original_proposal_sha256 = str(details.get("proposal_sha256") or "")
        details["source_sha256"] = composite_source_sha256
        details["proposal_sha256"] = sha256_json(
            {
                "authoring_branch": kind,
                "proposal_sha256": original_proposal_sha256,
            }
        )
        raise ContractError(
            exc.code,
            exc.stage,
            exc.public_message,
            details,
            exc.retryable,
        ) from exc


def _enforce_domain_policy_boundary(
    draft,
    *,
    source_sha256,
    proposal_sha256="",
    grounding_mode="freeform_llm",
    approved_planner_policy=None,
):
    """Keep prompt/function/output policy exclusively owned by Domain Policy Flow."""

    current = deepcopy(draft) if isinstance(draft, dict) else {}
    prompt_extensions = current.get("prompt_extensions")
    specialized_functions = current.get("specialized_functions")
    output_profile = current.get("output_profile")
    sealed_planner_policy = (
        deepcopy(approved_planner_policy)
        if isinstance(approved_planner_policy, dict)
        else {}
    )
    non_empty_prompt = isinstance(prompt_extensions, dict) and any(
        str(prompt_extensions.get(key) or "").strip() for key in ("intent", "answer")
    )
    if (
        non_empty_prompt
        or (specialized_functions not in (None, []))
        or (
            output_profile not in (None, {})
            and output_profile != sealed_planner_policy
        )
    ):
        raise ContractError(
            "metadata_policy_error",
            "metadata_domain_policy_boundary",
            "도메인 자연어 LLM은 특화 프롬프트, 등록 함수 또는 출력 정책을 작성할 수 없습니다. Domain Policy Flow를 사용하세요.",
        )
    current["prompt_extensions"] = {"intent": "", "answer": ""}
    current["specialized_functions"] = []
    current["output_profile"] = sealed_planner_policy
    current["source_provenance"] = {
        "source_sha256": str(source_sha256 or ""),
        "grounding_mode": str(grounding_mode or "freeform_llm"),
        "proposal_sha256": str(proposal_sha256 or ""),
    }
    return current


def _complete_unambiguous_metric_bindings(draft, approved_semantic_vocabulary=None):
    """Expand only exact ``<dataset_family>.<field>`` refs; never infer or repair."""

    current = deepcopy(draft) if isinstance(draft, dict) else {}
    datasets = current.get("datasets")
    metrics = current.get("metrics")
    vocabulary = (
        approved_semantic_vocabulary
        if isinstance(approved_semantic_vocabulary, dict)
        else {}
    )
    completed = []
    preserved = []
    if not isinstance(datasets, dict) or not isinstance(metrics, dict):
        metrics = {}
    vocabulary_metric_ids = [
        card.get("id")
        for card in (vocabulary.get("metrics") or [])
        if isinstance(card, dict)
    ]
    vocabulary_fields = [
        card
        for card in (vocabulary.get("fields") or [])
        if isinstance(card, dict)
    ]
    draft_candidates = {
        (str(card.get("family") or ""), str(field_id))
        for card in (datasets or {}).values()
        if isinstance(card, dict)
        for field_id in (
            (card.get("fields") or {})
            if isinstance(card.get("fields"), dict)
            else {}
        )
    }
    for metric_id, raw_metric in metrics.items():
        if not isinstance(raw_metric, dict):
            continue
        existing_binding = raw_metric.get("source_binding")
        if isinstance(existing_binding, dict):
            preserved.append(str(metric_id))
            continue
        if existing_binding is None:
            continue
        if not isinstance(existing_binding, str):
            continue
        semantic_candidates = []
        if vocabulary_metric_ids.count(metric_id) == 1:
            for field_card in vocabulary_fields:
                field_id = field_card.get("id")
                for family in field_card.get("families") or []:
                    if existing_binding == f"{family}.{field_id}":
                        semantic_candidates.append((str(family), str(field_id)))
        candidates = sorted(
            {
                candidate
                for candidate in semantic_candidates
                if candidate in draft_candidates
            }
        )
        if len(candidates) != 1:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_semantic_reference_normalization",
                "지표 원천 참조가 승인된 의미 필드 하나로 정확히 결정되지 않습니다.",
                {
                    "metric_id_sha256": sha256_json(str(metric_id)),
                    "source_binding_sha256": sha256_json(existing_binding),
                    "candidate_count": len(candidates),
                },
            )
        family, field_id = candidates[0]
        raw_metric["source_binding"] = {
            "dataset_family": family,
            "field": field_id,
        }
        completed.append(str(metric_id))

    completed = sorted(completed)
    preserved = sorted(preserved)
    return current, {
        "contract_version": "metadata.metric-binding-reconciliation.v1",
        "resolution_mode": "approved_semantic_vocabulary_exact",
        "completed_count": len(completed),
        "completed_metric_ids_sha256": sha256_json(completed),
        "corrected_count": 0,
        "corrected_metric_ids_sha256": sha256_json([]),
        "preserved_full_card_count": len(preserved),
        "preserved_full_card_ids_sha256": sha256_json(preserved),
    }


_SEMANTIC_ALIAS_TARGET_SECTIONS = (
    ("datasets", "dataset"),
    ("fields", "field"),
    ("metrics", "metric"),
    ("relations", "relation"),
    ("grains", "grain"),
    ("predicates", "predicate"),
    ("recipes", "recipe"),
    ("entity_groups", "entity_group"),
)
_NATURAL_ALIAS_POLICY = {
    "normalization": ["unicode_nfkc", "trim", "collapse_space", "latin_casefold"],
    "match": "bounded_longest",
    "conflict": "fail_ambiguous",
    "provenance_source": "natural_authoring",
}


def _semantic_alias_target_candidates(draft, vocabulary, target_id):
    candidates = []
    datasets = draft.get("datasets") if isinstance(draft, dict) else {}
    for section, target_type in _SEMANTIC_ALIAS_TARGET_SECTIONS:
        cards = vocabulary.get(section) if isinstance(vocabulary, dict) else []
        matches = [
            card for card in (cards or [])
            if isinstance(card, dict) and card.get("id") == target_id
        ]
        if not matches:
            continue
        if section == "datasets":
            registered = isinstance(datasets, dict) and target_id in datasets
        elif section == "fields":
            registered = any(
                isinstance(dataset, dict)
                and isinstance(dataset.get("fields"), dict)
                and target_id in dataset["fields"]
                for dataset in (datasets or {}).values()
            )
        else:
            registered = (
                isinstance(draft.get(section), dict)
                and target_id in draft[section]
            )
        if registered:
            candidates.extend((target_type, target_id) for _ in matches)
    return candidates


def _normalized_natural_alias_expressions(expressions, target_id):
    if not isinstance(expressions, list) or not 1 <= len(expressions) <= 64:
        raise ContractError(
            "metadata_schema_error",
            "metadata_semantic_reference_normalization",
            "자연어 별칭 표현은 bounded non-empty list여야 합니다.",
            {
                "target_id_sha256": sha256_json(str(target_id)),
                "expression_count": len(expressions) if isinstance(expressions, list) else 0,
            },
        )
    forbidden = (
        "http://", "https://", "mongodb://", "mongodb+srv://", "select ",
        "insert ", "update ", "delete ", "password", "secret", "token=", "api_key",
    )
    result = {}
    for raw_expression in expressions:
        if not isinstance(raw_expression, str):
            raise ContractError(
                "metadata_schema_error",
                "metadata_semantic_reference_normalization",
                "자연어 별칭 표현은 text여야 합니다.",
                {"target_id_sha256": sha256_json(str(target_id))},
            )
        expression = re.sub(
            r"\s+", " ", unicodedata.normalize("NFKC", raw_expression).strip()
        )
        folded = expression.casefold()
        if (
            not expression
            or len(expression.encode("utf-8")) > 512
            or any(ord(character) < 32 for character in expression)
            or any(fragment in folded for fragment in forbidden)
        ):
            raise ContractError(
                "metadata_schema_error",
                "metadata_semantic_reference_normalization",
                "자연어 별칭 표현이 비어 있거나 허용 범위를 벗어났습니다.",
                {"target_id_sha256": sha256_json(str(target_id))},
            )
        result.setdefault(folded, expression)
    return [result[key] for key in sorted(result, key=lambda key: (key, result[key]))]


def _alias_value_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and set(value) == {"text", "priority"}:
        text = value.get("text")
        priority = value.get("priority")
        if isinstance(text, str) and isinstance(priority, int) and not isinstance(priority, bool):
            return text
    return None


def _merge_natural_alias_card(existing, generated, canonical_key):
    identity_keys = {"target_type", "target_key"}
    policy_keys = {"normalization", "match", "conflict"}
    if (
        not isinstance(existing, dict)
        or any(existing.get(key) != generated.get(key) for key in identity_keys)
        or any(
            key in existing and existing.get(key) != generated.get(key)
            for key in policy_keys
        )
        or not isinstance(existing.get("values"), list)
    ):
        raise ContractError(
            "metadata_dependency_error",
            "metadata_semantic_reference_normalization",
            "canonical alias card가 다른 대상 또는 정책과 충돌합니다.",
            {"alias_key_sha256": sha256_json(canonical_key)},
        )
    merged = deepcopy(existing)
    seen = set()
    for value in merged["values"]:
        text = _alias_value_text(value)
        if text is None:
            raise ContractError(
                "metadata_schema_error",
                "metadata_semantic_reference_normalization",
                "기존 canonical alias value가 유효하지 않습니다.",
                {"alias_key_sha256": sha256_json(canonical_key)},
            )
        normalized = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).strip())
        seen.add(normalized.casefold())
    append_as_strings = bool(merged["values"]) and all(
        isinstance(value, str) for value in merged["values"]
    )
    for value in generated["values"]:
        marker = value["text"].casefold()
        if marker not in seen:
            seen.add(marker)
            merged["values"].append(value["text"] if append_as_strings else value)
    return merged


def _resolve_natural_alias_conflicts(candidate_aliases, baseline_aliases):
    """Preserve approved aliases and discard ambiguous natural additions."""

    if not isinstance(candidate_aliases, dict) or not isinstance(baseline_aliases, dict):
        raise ContractError(
            "metadata_dependency_error",
            "metadata_semantic_reference_normalization",
            "Alias conflict inputs must be closed dictionaries.",
        )

    def marker(value):
        text = _alias_value_text(value)
        if text is None:
            return ""
        return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).strip()).casefold()

    baseline_targets = {}
    baseline_markers_by_key = {}
    for canonical_key, card in sorted(baseline_aliases.items()):
        values = card.get("values") if isinstance(card, dict) else None
        if not isinstance(values, list):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_semantic_reference_normalization",
                "Approved baseline alias card is invalid.",
                {"alias_key_sha256": sha256_json(str(canonical_key))},
            )
        markers = {marker(value) for value in values}
        if "" in markers:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_semantic_reference_normalization",
                "Approved baseline alias value is invalid.",
                {"alias_key_sha256": sha256_json(str(canonical_key))},
            )
        baseline_markers_by_key[canonical_key] = markers
        for normalized in markers:
            baseline_targets.setdefault(normalized, set()).add(canonical_key)

    delta_rows = []
    redundant_count = 0
    for canonical_key, card in sorted(candidate_aliases.items()):
        values = card.get("values") if isinstance(card, dict) else None
        if not isinstance(values, list):
            raise ContractError(
                "metadata_schema_error",
                "metadata_semantic_reference_normalization",
                "Candidate alias card is invalid.",
                {"alias_key_sha256": sha256_json(str(canonical_key))},
            )
        same_target_baseline = baseline_markers_by_key.get(canonical_key, set())
        for value in values:
            normalized = marker(value)
            if not normalized:
                raise ContractError(
                    "metadata_schema_error",
                    "metadata_semantic_reference_normalization",
                    "Candidate alias value is invalid.",
                    {"alias_key_sha256": sha256_json(str(canonical_key))},
                )
            if normalized in same_target_baseline:
                if canonical_key not in baseline_aliases or value not in baseline_aliases[canonical_key]["values"]:
                    redundant_count += 1
                continue
            delta_rows.append((canonical_key, normalized, deepcopy(value)))

    delta_targets = {}
    for canonical_key, normalized, _ in delta_rows:
        delta_targets.setdefault(normalized, set()).add(canonical_key)

    accepted_by_key = {}
    discarded_baseline_conflict_count = 0
    discarded_cross_target_count = 0
    duplicate_same_target_count = 0
    seen_by_key = {}
    for canonical_key, normalized, value in sorted(
        delta_rows, key=lambda row: (row[0], row[1], sha256_json(row[2]))
    ):
        approved_targets = baseline_targets.get(normalized, set())
        if approved_targets and approved_targets != {canonical_key}:
            discarded_baseline_conflict_count += 1
            continue
        if len(delta_targets.get(normalized, set())) != 1:
            discarded_cross_target_count += 1
            continue
        if normalized in seen_by_key.setdefault(canonical_key, set()):
            duplicate_same_target_count += 1
            continue
        seen_by_key[canonical_key].add(normalized)
        accepted_by_key.setdefault(canonical_key, []).append(value)

    resolved = {key: deepcopy(card) for key, card in sorted(baseline_aliases.items())}
    for canonical_key, card in sorted(candidate_aliases.items()):
        accepted = accepted_by_key.get(canonical_key, [])
        if canonical_key in resolved:
            append_as_strings = bool(resolved[canonical_key]["values"]) and all(
                isinstance(value, str) for value in resolved[canonical_key]["values"]
            )
            for value in accepted:
                text = _alias_value_text(value)
                resolved[canonical_key]["values"].append(text if append_as_strings else value)
        elif accepted:
            resolved[canonical_key] = deepcopy(card)
            resolved[canonical_key]["values"] = accepted

    evidence = {
        "contract_version": "metadata.alias-conflict-resolution.v1",
        "baseline_card_count": len(baseline_aliases),
        "candidate_card_count": len(candidate_aliases),
        "resolved_card_count": len(resolved),
        "accepted_delta_count": sum(len(values) for values in accepted_by_key.values()),
        "redundant_delta_count": redundant_count,
        "discarded_baseline_conflict_count": discarded_baseline_conflict_count,
        "discarded_cross_target_count": discarded_cross_target_count,
        "duplicate_same_target_count": duplicate_same_target_count,
        "resolved_aliases_sha256": sha256_json(resolved),
    }
    return resolved, evidence


def _expand_compact_main_filter_fragment(
    fragment,
    *,
    approved_semantic_vocabulary,
    reconciliation_out=None,
):
    """Compile typed natural-language alias additions into canonical cards."""

    try:
        vocabulary = _validated_semantic_vocabulary(
            approved_semantic_vocabulary
        )
    except ValueError as exc:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_semantic_reference_normalization",
            "승인 축약 업무 어휘가 유효하지 않습니다.",
        ) from exc
    additions = fragment.get("alias_additions") if isinstance(fragment, dict) else None
    if not isinstance(additions, list) or not additions:
        raise ContractError(
            "metadata_schema_error",
            "metadata_semantic_reference_normalization",
            "주요 필터 별칭 추가 목록이 비어 있습니다.",
        )
    section_by_type = {
        target_type: section
        for section, target_type in _SEMANTIC_ALIAS_TARGET_SECTIONS
    }
    allowed_ids = {
        target_type: {
            str(card.get("id") or "")
            for card in vocabulary.get(section) or []
            if isinstance(card, dict)
        }
        for target_type, section in section_by_type.items()
    }
    aliases = {}
    normalized_targets = []
    for index, addition in enumerate(additions):
        if not isinstance(addition, dict) or set(addition) != {
            "target_type", "target_id", "expressions"
        }:
            raise ContractError(
                "metadata_schema_error",
                "metadata_semantic_reference_normalization",
                "주요 필터 별칭 추가 항목의 계약이 닫혀 있지 않습니다.",
                {"addition_index": index},
            )
        target_type = str(addition.get("target_type") or "")
        target_id = str(addition.get("target_id") or "")
        if (
            target_type not in allowed_ids
            or target_id not in allowed_ids[target_type]
        ):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_semantic_reference_normalization",
                "주요 필터 별칭 대상이 승인 업무 어휘에 없습니다.",
                {
                    "addition_index": index,
                    "target_type": target_type,
                    "target_id_sha256": sha256_json(target_id),
                },
            )
        canonical_key = f"{target_type}:{target_id}"
        generated = {
            "target_type": target_type,
            "target_key": target_id,
            "values": [
                {"text": text, "priority": 100}
                for text in _normalized_natural_alias_expressions(
                    addition.get("expressions"), target_id
                )
            ],
            **deepcopy(_NATURAL_ALIAS_POLICY),
        }
        if canonical_key in aliases:
            aliases[canonical_key] = _merge_natural_alias_card(
                aliases[canonical_key], generated, canonical_key
            )
        else:
            aliases[canonical_key] = generated
        normalized_targets.append(canonical_key)
    evidence = {
        "contract_version": "metadata.main-filter-ir-expansion.v1",
        "input_count": len(additions),
        "canonical_alias_count": len(aliases),
        "canonical_targets_sha256": sha256_json(sorted(set(normalized_targets))),
    }
    if isinstance(reconciliation_out, dict):
        reconciliation_out.clear()
        reconciliation_out.update(evidence)
    return {"aliases": {key: aliases[key] for key in sorted(aliases)}}


def _merge_typed_main_filter_patch(base_draft, expanded_patch):
    """Merge registry-bound alias IR without reinterpreting it as legacy shorthand."""

    if not isinstance(expanded_patch, dict) or set(expanded_patch) != {"aliases"}:
        raise ContractError(
            "metadata_schema_error",
            "metadata_semantic_reference_normalization",
            "Expanded Main Filter IR must contain only aliases.",
        )
    base_aliases = (
        base_draft.get("aliases") if isinstance(base_draft, dict) else None
    )
    patch_aliases = expanded_patch.get("aliases")
    if not isinstance(base_aliases, dict) or not isinstance(patch_aliases, dict):
        raise ContractError(
            "metadata_dependency_error",
            "metadata_semantic_reference_normalization",
            "Main Filter alias catalogs are unavailable.",
        )
    candidate_aliases = deepcopy(base_aliases)
    for canonical_key in sorted(patch_aliases):
        generated = patch_aliases[canonical_key]
        if canonical_key in base_aliases:
            candidate_aliases[canonical_key] = _merge_natural_alias_card(
                base_aliases[canonical_key], generated, canonical_key
            )
        else:
            candidate_aliases[canonical_key] = deepcopy(generated)
    resolved_aliases, _ = _resolve_natural_alias_conflicts(
        candidate_aliases, base_aliases
    )
    merged_patch = {
        canonical_key: resolved_aliases[canonical_key]
        for canonical_key in sorted(patch_aliases)
        if canonical_key in resolved_aliases
    }
    return {"aliases": merged_patch}


def _normalize_bootstrap_alias_shorthand(draft, approved_semantic_vocabulary):
    current = deepcopy(draft) if isinstance(draft, dict) else {}
    aliases = current.get("aliases")
    if aliases is None:
        aliases = {}
    if not isinstance(aliases, dict):
        raise ContractError(
            "metadata_schema_error",
            "metadata_semantic_reference_normalization",
            "aliases는 object여야 합니다.",
        )
    full_cards = {}
    shorthand = []
    for alias_key in sorted(aliases):
        card = aliases[alias_key]
        if isinstance(card, dict) and "expressions" in card:
            if set(card) != {"expressions"}:
                raise ContractError(
                    "metadata_schema_error",
                    "metadata_semantic_reference_normalization",
                    "자연어 alias shorthand에 비허용 key가 있습니다.",
                    {"target_id_sha256": sha256_json(str(alias_key))},
                )
            shorthand.append((str(alias_key), card["expressions"]))
        else:
            full_cards[str(alias_key)] = deepcopy(card)
    normalized_ids = []
    for target_id, expressions in shorthand:
        candidates = _semantic_alias_target_candidates(
            current, approved_semantic_vocabulary, target_id
        )
        if len(candidates) != 1:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_semantic_reference_normalization",
                "자연어 alias 대상이 승인된 draft 대상 하나로 정확히 결정되지 않습니다.",
                {
                    "target_id_sha256": sha256_json(target_id),
                    "candidate_count": len(candidates),
                },
            )
        target_type, target_key = candidates[0]
        canonical_key = f"{target_type}:{target_key}"
        values = [
            {"text": text, "priority": 100}
            for text in _normalized_natural_alias_expressions(expressions, target_id)
        ]
        generated = {
            "target_type": target_type,
            "target_key": target_key,
            "values": values,
            **deepcopy(_NATURAL_ALIAS_POLICY),
        }
        if canonical_key in full_cards:
            full_cards[canonical_key] = _merge_natural_alias_card(
                full_cards[canonical_key], generated, canonical_key
            )
        else:
            full_cards[canonical_key] = generated
        normalized_ids.append(canonical_key)
    current["aliases"] = {key: full_cards[key] for key in sorted(full_cards)}
    return current, {
        "contract_version": "metadata.alias-semantic-reconciliation.v1",
        "resolution_mode": "approved_semantic_vocabulary_exact",
        "normalized_count": len(normalized_ids),
        "normalized_alias_ids_sha256": sha256_json(sorted(normalized_ids)),
    }


def _normalize_filter_operator_aliases(draft):
    """Canonicalize a small provider-independent filter vocabulary."""

    aliases = {
        "equals": "eq",
        "equal": "eq",
        "not_equals": "ne",
        "not_equal": "ne",
        "not_null": "is_not_null",
        "not_blank": "is_not_blank",
        "null": "is_null",
        "blank": "is_blank",
        "startswith": "starts_with",
        "endswith": "ends_with",
        "notin": "not_in",
        "greater_than": "gt",
        "greater_than_or_equal": "gte",
        "less_than": "lt",
        "less_than_or_equal": "lte",
    }
    current = deepcopy(draft) if isinstance(draft, dict) else {}
    replacements = []

    def canonical(value):
        if not isinstance(value, str):
            return value
        token = re.sub(r"[\s-]+", "_", value.strip().casefold())
        return aliases.get(token, value)

    def visit(value, path):
        if isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, [*path, index])
            return
        if not isinstance(value, dict):
            return
        if "operator" in value and "field" in value:
            before = value.get("operator")
            after = canonical(before)
            if after != before:
                value["operator"] = after
                replacements.append({"path": [*path, "operator"], "canonical": after})
        for list_key in ("allowed_operators", "allowed_filter_operators"):
            raw_items = value.get(list_key)
            if not isinstance(raw_items, list):
                continue
            normalized = [canonical(item) for item in raw_items]
            if normalized != raw_items:
                value[list_key] = normalized
                replacements.append({"path": [*path, list_key], "canonical": normalized})
        for key, child in value.items():
            visit(child, [*path, str(key)])

    visit(current, [])
    return current, {
        "contract_version": "metadata.filter-operator-normalization.v1",
        "replacement_count": len(replacements),
        "replacements_sha256": sha256_json(replacements),
    }


def _validate_authoring_source_bindings(
    draft,
    *,
    source_sha256="",
    proposal_sha256="",
    approved_reference_context=None,
    domain_id="",
    require_registry_exact_set=False,
):
    """Overlay and seal execution bindings from an operator-approved registry.

    Workers and the LLM never own config/query identifiers.  The LLM only has
    to identify a dataset.  This deterministic gate replaces any omitted or
    untrusted binding fields with the sealed registry values, then verifies the
    resulting closed draft before compilation.
    """

    datasets = draft.get("datasets") if isinstance(draft, dict) else None
    if not isinstance(datasets, dict):
        raise ContractError("metadata_schema_error", "metadata_source_bindings", "datasets 계약이 필요합니다.")
    raw_registry = getattr(approved_reference_context, "data", approved_reference_context)
    registry = raw_registry if isinstance(raw_registry, dict) else {}
    if not registry:
        clarification_material = {
            "questions": ["이 도메인에서 사용할 승인 Source 레지스트리를 운영자가 먼저 연결해 주세요."],
            "missing_fields": ["approved_reference_context"],
            "source_sha256": str(source_sha256 or ""),
        }
        raise ContractError(
            "metadata_clarification_required",
            "metadata_clarification",
            "작업자 자연어에서 source registry ID를 추측하지 않도록 운영자 레지스트리 연결이 필요합니다.",
            {
                "contract_version": "metadata.authoring.clarification.v1",
                **clarification_material,
                "proposal_sha256": str(proposal_sha256 or "") or sha256_json(clarification_material),
            },
        )
    if set(registry) != {
        "contract_version", "domain_id", "bindings", "dataset_descriptors",
        "semantic_vocabulary", "semantic_templates",
        "semantic_templates_sha256",
        "semantic_templates_blueprint_sha256",
        "semantic_templates_executable_sha256",
        "semantic_templates_projection_sha256", "registry_sha256",
    }:
        raise ContractError("metadata_dependency_error", "metadata_source_bindings", "승인 Source 레지스트리 컨텍스트 root 계약이 닫혀 있지 않습니다.")
    registry_material = {
        "contract_version": registry.get("contract_version"),
        "domain_id": registry.get("domain_id"),
        "bindings": registry.get("bindings"),
        "dataset_descriptors": registry.get("dataset_descriptors"),
        "semantic_vocabulary": registry.get("semantic_vocabulary"),
        "semantic_templates": registry.get("semantic_templates"),
        "semantic_templates_sha256": registry.get("semantic_templates_sha256"),
        "semantic_templates_blueprint_sha256": registry.get("semantic_templates_blueprint_sha256"),
        "semantic_templates_executable_sha256": registry.get("semantic_templates_executable_sha256"),
        "semantic_templates_projection_sha256": registry.get("semantic_templates_projection_sha256"),
    }
    try:
        dataset_families, field_families = _semantic_maps_from_descriptors(
            registry.get("dataset_descriptors")
        )
        semantic_vocabulary = _validated_semantic_vocabulary(
            registry.get("semantic_vocabulary"),
            expected_dataset_families=dataset_families,
            expected_field_families=field_families,
        )
        semantic_templates = _validated_semantic_templates(
            registry.get("semantic_templates"), semantic_vocabulary
        )
    except ValueError as exc:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_bindings",
            "승인 축약 업무 어휘 계약이 유효하지 않습니다.",
        ) from exc
    if (
        registry.get("contract_version") != "metadata.authoring.source-registry-context.v3"
        or registry.get("domain_id") != str(domain_id or "")
        or not isinstance(registry.get("bindings"), dict)
        or not isinstance(registry.get("dataset_descriptors"), dict)
        or set(registry.get("bindings") or {}) != set(registry.get("dataset_descriptors") or {})
        or registry.get("semantic_vocabulary") != semantic_vocabulary
        or registry.get("semantic_templates") != semantic_templates
        or registry.get("semantic_templates_sha256") != sha256_json(semantic_templates)
        or any(
            not re.fullmatch(r"[0-9a-f]{64}", str(registry.get(key) or ""))
            for key in (
                "semantic_templates_blueprint_sha256",
                "semantic_templates_executable_sha256",
                "semantic_templates_projection_sha256",
            )
        )
        or registry.get("registry_sha256") != sha256_json(registry_material)
    ):
        raise ContractError("metadata_dependency_error", "metadata_source_bindings", "승인 Source 레지스트리 hash 또는 도메인 결합이 유효하지 않습니다.")
    registry_bindings = registry["bindings"]
    registry_descriptors = registry["dataset_descriptors"]
    id_pattern = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
    adapter_pattern = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")
    ref_pattern = re.compile(r"^(?:config|query):[A-Za-z0-9_.:-]{1,220}@[1-9][0-9]{0,8}$")
    source_types = {"oracle", "sql", "mongodb", "http", "datalake", "goodocs", "file", "dummy", "previous_result"}
    forbidden = ("http://", "https://", "mongodb://", "mongodb+srv://", "select ", "insert ", "update ", "delete ", "password", "secret", "token=", "api_key")
    for dataset_id, expected in registry_bindings.items():
        required = {"source_type", "source_adapter", "config_ref", "query_ref"}
        normalized = {key: str((expected or {}).get(key) or "").strip() for key in required} if isinstance(expected, dict) else {}
        joined = json.dumps(normalized, ensure_ascii=False).casefold()
        if (
            not id_pattern.fullmatch(str(dataset_id))
            or not isinstance(expected, dict)
            or set(expected) != required
            or normalized.get("source_type") not in source_types
            or not adapter_pattern.fullmatch(normalized.get("source_adapter") or "")
            or not ref_pattern.fullmatch(normalized.get("config_ref") or "")
            or not normalized.get("config_ref", "").startswith("config:")
            or not ref_pattern.fullmatch(normalized.get("query_ref") or "")
            or not normalized.get("query_ref", "").startswith("query:")
            or any(fragment in joined for fragment in forbidden)
        ):
            raise ContractError("metadata_dependency_error", "metadata_source_bindings", "승인 Source 레지스트리 binding 계약이 유효하지 않습니다.", {"dataset_id": str(dataset_id)})
    unresolved = [dataset_id for dataset_id in sorted(datasets) if dataset_id not in registry_bindings]
    if unresolved:
        clarification_material = {
            "questions": ["새 데이터셋의 승인 Source adapter/config/query binding을 운영자가 등록해 주세요."],
            "missing_fields": [f"approved_reference_context.bindings.{item}" for item in unresolved[:31]],
            "source_sha256": str(source_sha256 or ""),
        }
        raise ContractError(
            "metadata_clarification_required",
            "metadata_clarification",
            "승인 Source 레지스트리에 없는 dataset binding은 활성 후보로 만들 수 없습니다.",
            {
                "contract_version": "metadata.authoring.clarification.v1",
                **clarification_material,
                "proposal_sha256": str(proposal_sha256 or "") or sha256_json(clarification_material),
            },
        )
    omitted_approved = [
        dataset_id
        for dataset_id in sorted(registry_bindings)
        if dataset_id not in datasets
    ]
    if require_registry_exact_set and omitted_approved:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_bindings",
            "초기 도메인 등록의 데이터셋 집합이 승인 Source 레지스트리와 정확히 일치하지 않습니다.",
            {"omitted_approved_dataset_ids": omitted_approved[:32]},
        )
    exact_fields = ("source_type", "source_adapter", "config_ref", "query_ref")
    bindings = []
    discarded_untrusted_fields = []
    completed_registry_fields = []
    descriptor_rows = []
    for dataset_id in sorted(datasets):
        card = datasets.get(dataset_id)
        if not isinstance(card, dict):
            raise ContractError("metadata_schema_error", "metadata_source_bindings", "dataset binding 대상이 object가 아닙니다.", {"dataset_id": dataset_id})
        expected = registry_bindings[dataset_id]
        descriptor = _validated_dataset_descriptor(
            dataset_id, registry_descriptors.get(dataset_id)
        )
        if str(card.get("family") or "") != descriptor["family"]:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "dataset family가 승인 source descriptor와 일치하지 않습니다.",
                {"dataset_id": dataset_id},
            )
        card_fields = card.get("fields")
        if not isinstance(card_fields, dict) or set(card_fields) != set(descriptor["fields"]):
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_descriptors",
                "dataset field 집합이 승인 source descriptor와 정확히 일치하지 않습니다.",
                {"dataset_id": dataset_id},
            )
        technical_keys = {
            "physical_column", "semantic_type", "roles", "physical_aliases",
            "coercion", "nullable", "required_in_source", "timezone",
        }
        for field_id, approved_field in descriptor["fields"].items():
            actual_field = card_fields.get(field_id)
            if not isinstance(actual_field, dict):
                raise ContractError(
                    "metadata_dependency_error", "metadata_source_descriptors",
                    "dataset field binding이 object가 아닙니다.",
                    {"dataset_id": dataset_id, "field_id": field_id},
                )
            for key in technical_keys:
                if key not in actual_field and key in approved_field:
                    actual_field[key] = deepcopy(approved_field[key])
                    completed_registry_fields.append(
                        f"datasets.{dataset_id}.fields.{field_id}.{key}"
                    )
                    continue
                actual_value = actual_field.get(key)
                approved_value = approved_field.get(key)
                if key in {"roles", "physical_aliases"}:
                    values_match = (
                        isinstance(actual_value, list)
                        and isinstance(approved_value, list)
                        and len(actual_value) == len(set(actual_value))
                        and set(actual_value) == set(approved_value)
                    )
                else:
                    values_match = actual_value == approved_value
                if not values_match:
                    raise ContractError(
                        "metadata_dependency_error", "metadata_source_descriptors",
                        "dataset 기술 field 속성이 승인 source descriptor와 일치하지 않습니다.",
                        {"dataset_id": dataset_id, "field_id": field_id, "attribute": key},
                    )
                if key in {"roles", "physical_aliases"}:
                    actual_field[key] = deepcopy(approved_value)
        for field in exact_fields:
            supplied = card.get(field)
            approved = str(expected.get(field) or "")
            if supplied is not None and str(supplied).strip() != approved:
                discarded_untrusted_fields.append(f"datasets.{dataset_id}.{field}")
            card[field] = approved
        bindings.append({"dataset_id": dataset_id, **{field: card[field] for field in exact_fields}})
        descriptor_rows.append(
            {
                "dataset_id": dataset_id,
                "family": descriptor["family"],
                "fields_sha256": sha256_json(descriptor["fields"]),
            }
        )
    return {
        "contract_version": "metadata.source-binding.validation.v1",
        "status": "approved_registry_exact",
        "binding_authority": "approved_registry",
        "dataset_count": len(bindings),
        "bindings_sha256": sha256_json(bindings),
        "registry_sha256": str(registry["registry_sha256"]),
        "dataset_descriptors_sha256": sha256_json(descriptor_rows),
        "registry_resolution": "passed",
        "discarded_untrusted_fields": discarded_untrusted_fields[:128],
        "completed_registry_field_count": len(completed_registry_fields),
        "completed_registry_fields_sha256": sha256_json(
            sorted(completed_registry_fields)
        ),
    }


def _freeform_authoring_manifest(source_text):
    """Build hash-only source evidence without imposing syntax on a worker's TXT."""

    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    inventories = {
        "datasets": [], "dataset_fields": {}, "fields": [], "field_roles": {},
        "metrics": [], "grains": [], "grain_keys": {}, "grain_display_fields": {},
        "relations": [], "relation_endpoints": {}, "relation_keys": {},
        "relation_policies": {}, "recipes": [], "operations": [], "aliases": [],
        "alias_targets": [], "alias_bindings": [],
    }
    counts = {
        "datasets": 0, "fields": 0, "field_bindings": 0, "field_roles": 0,
        "metrics": 0, "grains": 0, "grain_keys": 0, "grain_display_fields": 0,
        "relations": 0, "relation_endpoints": 0, "relation_keys": 0,
        "relation_policies": 0, "recipes": 0, "operations": 0, "aliases": 0,
        "alias_targets": 0, "alias_bindings": 0,
    }
    material = {
        "contract_version": "metadata.authoring.source-manifest.v1",
        "source_sha256": source_sha256,
        "inventories": inventories,
        "required_sections": [],
        "counts": counts,
    }
    material["manifest_sha256"] = sha256_json(material)
    return material


def _freeform_dataset_patch_authorization_manifest(source_manifest, base_draft):
    """Authorize freeform Dataset patches only against the active base catalog.

    The worker's prose remains hash-only evidence and is never regex-parsed as
    a DSL.  This separate, sealed manifest is derived from already compiled
    metadata so an LLM may refer to existing dataset/field IDs but cannot mint
    a new target.  Source execution bindings remain controlled by the approved
    registry gate after patch application.
    """

    if not isinstance(source_manifest, dict) or not isinstance(base_draft, dict):
        raise ContractError(
            "metadata_dependency_error",
            "metadata_patch_authorization",
            "자유형 데이터셋 수정에 사용할 활성 메타데이터가 없습니다.",
        )
    datasets = base_draft.get("datasets")
    if not isinstance(datasets, dict) or not datasets:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_patch_authorization",
            "자유형 데이터셋 수정 대상 목록이 비어 있습니다.",
        )

    authorization = deepcopy(source_manifest)
    inventories = deepcopy(authorization.get("inventories") or {})
    counts = deepcopy(authorization.get("counts") or {})
    dataset_ids = sorted(str(key) for key in datasets)
    dataset_fields = {}
    field_roles = {}
    for dataset_id in dataset_ids:
        dataset = datasets.get(dataset_id)
        fields = dataset.get("fields") if isinstance(dataset, dict) else None
        if not isinstance(fields, dict) or not fields:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_patch_authorization",
                "활성 데이터셋의 field catalog가 비어 있습니다.",
                {"dataset_id_sha256": hashlib.sha256(dataset_id.encode("utf-8")).hexdigest()},
            )
        field_ids = sorted(str(key) for key in fields)
        dataset_fields[dataset_id] = field_ids
        role_cards = {}
        for field_id in field_ids:
            field = fields.get(field_id)
            roles = field.get("roles") if isinstance(field, dict) else None
            if isinstance(roles, list) and roles:
                normalized_roles = [
                    role for role in AUTHORING_FIELD_ROLE_ORDER if role in roles
                ]
                if len(normalized_roles) != len(roles):
                    raise ContractError(
                        "metadata_dependency_error",
                        "metadata_patch_authorization",
                        "활성 field role 계약이 유효하지 않습니다.",
                        {
                            "dataset_id_sha256": hashlib.sha256(dataset_id.encode("utf-8")).hexdigest(),
                            "field_id_sha256": hashlib.sha256(field_id.encode("utf-8")).hexdigest(),
                        },
                    )
                role_cards[field_id] = normalized_roles
        if role_cards:
            field_roles[dataset_id] = role_cards

    inventories["datasets"] = dataset_ids
    inventories["dataset_fields"] = dataset_fields
    inventories["fields"] = sorted(
        {field_id for values in dataset_fields.values() for field_id in values}
    )
    inventories["field_roles"] = field_roles
    counts["datasets"] = len(dataset_ids)
    counts["fields"] = len(inventories["fields"])
    counts["field_bindings"] = sum(len(values) for values in dataset_fields.values())
    counts["field_roles"] = sum(len(values) for values in field_roles.values())
    authorization["inventories"] = inventories
    authorization["counts"] = counts
    authorization.pop("manifest_sha256", None)
    authorization["manifest_sha256"] = sha256_json(authorization)
    return authorization


def _bootstrap_context_payload(
    component,
    *,
    input_name,
    kind,
    purpose,
    domain_id,
    environment,
    bootstrap_fragment=True,
    grounding_mode="freeform_llm",
    annotation_only=False,
    expected_invoke=True,
):
    raw_context = getattr(component, input_name, None)
    context = getattr(raw_context, "data", raw_context)
    expected_root_keys = {"contract_version", "purpose", "invoke", "variables"}
    if not isinstance(context, dict) or set(context) != expected_root_keys:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_context",
            "분할 초기 등록 runtime context root 계약이 정확히 일치하지 않습니다.",
            {"input_name": input_name, "authoring_branch": kind},
        )
    variables = context.get("variables")
    raw_registry = getattr(component, "approved_reference_context", None)
    registry = getattr(raw_registry, "data", raw_registry)
    registry = registry if isinstance(registry, dict) else {}
    expected_registry_keys = {
        "contract_version", "domain_id", "bindings", "dataset_descriptors",
        "semantic_vocabulary", "semantic_templates",
        "semantic_templates_sha256",
        "semantic_templates_blueprint_sha256",
        "semantic_templates_executable_sha256",
        "semantic_templates_projection_sha256", "registry_sha256",
    }
    if set(registry) != expected_registry_keys:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_context",
            "분할 초기 등록의 승인 참조 컨텍스트가 유효하지 않습니다.",
            {"input_name": input_name, "authoring_branch": kind},
        )
    registry_material = {
        key: registry.get(key)
        for key in (
            "contract_version", "domain_id", "bindings", "dataset_descriptors",
            "semantic_vocabulary", "semantic_templates",
            "semantic_templates_sha256",
            "semantic_templates_blueprint_sha256",
            "semantic_templates_executable_sha256",
            "semantic_templates_projection_sha256",
        )
    }
    expected_registry_sha256 = hashlib.sha256(
        json.dumps(
            registry_material,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    try:
        dataset_families, field_families = _semantic_maps_from_descriptors(
            registry.get("dataset_descriptors")
        )
        expected_semantic_vocabulary = _validated_semantic_vocabulary(
            registry.get("semantic_vocabulary"),
            expected_dataset_families=dataset_families,
            expected_field_families=field_families,
        )
        expected_semantic_templates = _validated_semantic_templates(
            registry.get("semantic_templates"), expected_semantic_vocabulary
        )
    except ValueError as exc:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_context",
            "분할 초기 등록의 승인 축약 의미 어휘가 유효하지 않습니다.",
            {"input_name": input_name, "authoring_branch": kind},
        ) from exc
    if (
        registry.get("contract_version") != "metadata.authoring.source-registry-context.v3"
        or registry.get("domain_id") != domain_id
        or not isinstance(registry.get("bindings"), dict)
        or not isinstance(registry.get("dataset_descriptors"), dict)
        or set(registry.get("bindings") or {})
        != set(registry.get("dataset_descriptors") or {})
        or registry.get("semantic_templates") != expected_semantic_templates
        or registry.get("semantic_templates_sha256")
        != sha256_json(expected_semantic_templates)
        or any(
            not re.fullmatch(r"[0-9a-f]{64}", str(registry.get(key) or ""))
            for key in (
                "semantic_templates_blueprint_sha256",
                "semantic_templates_executable_sha256",
                "semantic_templates_projection_sha256",
            )
        )
        or registry.get("registry_sha256") != expected_registry_sha256
    ):
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_context",
            "분할 초기 등록의 승인 참조 컨텍스트 hash 또는 identity가 유효하지 않습니다.",
            {"input_name": input_name, "authoring_branch": kind},
        )
    expected_variable_keys = {
        "authoring_kind",
        "domain_id",
        "environment",
        "source_grounding_mode",
        "source_text",
        "source_sha256",
        "source_manifest",
        "bootstrap_fragment",
        "approved_semantic_vocabulary",
        "source_registry_sha256",
    }
    context_invoke = context.get("invoke")
    if context_invoke is True:
        expected_variable_keys.add("output_schema")
    if annotation_only:
        expected_variable_keys.update({"default_annotations", "blueprint_sha256"})
    if not isinstance(variables, dict) or set(variables) != expected_variable_keys:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_context",
            "분할 초기 등록 runtime context variables 계약이 정확히 일치하지 않습니다.",
            {"input_name": input_name, "authoring_branch": kind},
        )
    source_text = variables.get("source_text")
    source_sha256 = variables.get("source_sha256")
    if not isinstance(source_text, str) or not source_text or source_text != source_text.strip():
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_context",
            "분할 초기 등록 원문이 비어 있거나 정규화되지 않았습니다.",
            {"input_name": input_name, "authoring_branch": kind},
        )
    expected_source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    try:
        expected_manifest = (
            _freeform_authoring_manifest(source_text)
            if grounding_mode == "freeform_llm" and not annotation_only
            else extract_authoring_source_manifest(source_text)
        )
    except AuthoringSourceManifestError as exc:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_context",
            "등록 runtime context의 source manifest가 유효하지 않습니다.",
            {"input_name": input_name, "authoring_branch": kind},
        ) from exc
    expected_dataset_ids = sorted(
        str(card["id"])
        for card in expected_semantic_vocabulary["datasets"]
    )
    exact_field_allowlists = (
        _dataset_field_allowlists_from_vocabulary(
            expected_semantic_vocabulary,
            registry.get("dataset_descriptors"),
        )
        if kind == "dataset"
        else None
    )
    expected_output_schema = (
        _bootstrap_output_schema(
            kind,
            expected_source_sha256,
            approved_dataset_ids=expected_dataset_ids,
            approved_dataset_field_ids=exact_field_allowlists,
            approved_semantic_vocabulary=expected_semantic_vocabulary,
        )
        if bootstrap_fragment and context_invoke is True
        else _authoring_section_output_schema(
            kind,
            source_sha256=expected_source_sha256,
            grounding_mode=grounding_mode,
            annotation_only=annotation_only,
            approved_dataset_ids=expected_dataset_ids,
            approved_dataset_field_ids=exact_field_allowlists,
            approved_semantic_vocabulary=expected_semantic_vocabulary,
        )
        if context_invoke is True
        else None
    )
    registry_payload_valid = (
        variables.get("approved_semantic_vocabulary")
        == expected_semantic_vocabulary
        and variables.get("source_registry_sha256") == expected_registry_sha256
    )
    context_valid = (
        context.get("contract_version") == "prompt.runtime-context.v1"
        and context.get("purpose") == purpose
        and isinstance(context_invoke, bool)
        and (expected_invoke is None or context_invoke is expected_invoke)
        and variables.get("authoring_kind") == kind
        and variables.get("domain_id") == domain_id
        and variables.get("environment") == environment
        and variables.get("source_grounding_mode") == grounding_mode
        and variables.get("bootstrap_fragment") is bool(bootstrap_fragment)
        and source_sha256 == expected_source_sha256
        and variables.get("source_manifest") == expected_manifest
        and registry_payload_valid
        and (
            context_invoke is False
            or _bootstrap_schema_material(variables.get("output_schema"))
            == _bootstrap_schema_material(expected_output_schema)
        )
    )
    if not context_valid:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_context",
            "분할 초기 등록 runtime context의 목적, 해시 또는 bootstrap 결합이 유효하지 않습니다.",
            {
                "input_name": input_name,
                "authoring_branch": kind,
                "expected_purpose": purpose,
                "expected_source_sha256": expected_source_sha256,
            },
        )
    return {
        "source_text": source_text,
        "source_sha256": expected_source_sha256,
        "invoke": context_invoke,
        "output_schema": (
            deepcopy(variables["output_schema"])
            if context_invoke is True
            else None
        ),
        "output_schema_sha256": (
            sha256_json(variables["output_schema"])
            if context_invoke is True
            else ""
        ),
        "runtime_context_sha256": sha256_json(
            {
                "authority": "untrusted_data",
                "purpose": purpose,
                "variables": variables,
            }
        ),
    }


def _split_bootstrap_source(component, *, domain_id, environment):
    specifications = {
        "domain": ("authoring_source_context", "metadata_domain_draft", "도메인 정보"),
        "dataset": (
            "bootstrap_dataset_source_context",
            "metadata_dataset_draft",
            "데이터셋 정보",
        ),
        "main_filter": (
            "bootstrap_main_filter_source_context",
            "metadata_main_filter_draft",
            "주요 필터 정보",
        ),
    }
    branches = {}
    sections = []
    for kind in BOOTSTRAP_BRANCH_ORDER:
        input_name, purpose, label = specifications[kind]
        branch = _bootstrap_context_payload(
            component,
            input_name=input_name,
            kind=kind,
            purpose=purpose,
            domain_id=domain_id,
            environment=environment,
        )
        branches[kind] = branch
        sections.append(
            f"--- {label} 시작 ---\n{branch['source_text']}\n--- {label} 끝 ---"
        )
    bundled_source = "\n\n".join(sections)
    raw_message = getattr(component, "input_message", None)
    input_message = getattr(raw_message, "text", raw_message)
    if not isinstance(input_message, str) or input_message != bundled_source:
        actual_text = input_message if isinstance(input_message, str) else ""
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_context",
            "분할 초기 등록 input_message가 세 runtime context의 정확한 원문 묶음과 일치하지 않습니다.",
            {
                "expected_source_sha256": hashlib.sha256(
                    bundled_source.encode("utf-8")
                ).hexdigest(),
                "actual_source_sha256": hashlib.sha256(
                    actual_text.encode("utf-8")
                ).hexdigest(),
            },
        )
    return branches, bundled_source


def _authoring_source_text(component):
    raw_context = getattr(component, "authoring_source_context", None)
    context = getattr(raw_context, "data", raw_context)
    if isinstance(context, dict) and context:
        if context.get("contract_version") != "prompt.runtime-context.v1":
            raise ContractError(
                "metadata_schema_error",
                "metadata_source_context",
                "Authoring source context contract is invalid.",
            )
        variables = context.get("variables")
        source_text = str((variables or {}).get("source_text") or "").strip() if isinstance(variables, dict) else ""
        context_mode = str((variables or {}).get("source_grounding_mode") or "").strip() if isinstance(variables, dict) else ""
        configured_mode = str(getattr(component, "source_grounding_mode", "freeform_llm") or "freeform_llm").strip()
        if context_mode and context_mode != configured_mode:
            raise ContractError(
                "metadata_policy_error",
                "metadata_source_context",
                "Prompt context and compiler grounding modes do not match.",
            )
        if source_text:
            return source_text
    message = getattr(component, "input_message", None)
    return str(getattr(message, "text", message) or "").strip()


SOURCE_INVENTORY_VALIDATOR_VERSION = "source-inventory-coverage.v1"
SOURCE_ALLOWED_OPERATIONS = {
    "filter", "project", "derive", "aggregate", "compare_fields", "join", "sort", "rank",
    "transform_previous_result",
}


def _declared_ids(source_text, label):
    match = re.search(rf"{re.escape(label)}\s*(?:은|는)\s*(?P<body>[^.\n]+)", source_text, re.IGNORECASE)
    if not match:
        return []
    return sorted(set(re.findall(r"\b[A-Za-z][A-Za-z0-9_.-]*\b", match.group("body"))))


def _source_inventory(source_text):
    text = str(source_text or "")
    datasets = sorted(set(match.group(1) for match in re.finditer(r"\b([a-z][a-z0-9_]*)\s+데이터셋", text)))
    fields = set()
    for match in re.finditer(r"canonical\s*필드는\s*(?P<body>[^.\n]+)", text, re.IGNORECASE):
        fields.update(re.findall(r"\b[A-Z][A-Z0-9_]*\b", match.group("body")))
    aliases = {}
    alias_source = text.split("자연어 별칭으로", 1)[1] if "자연어 별칭으로" in text else ""
    for sentence in re.split(r"[.\n]", alias_source):
        for clause in sentence.split(","):
            matched = re.search(r"(?P<labels>.+?)(?:은|는)\s+(?P<target>[A-Z][A-Z0-9_]*)에", clause.strip())
            if not matched:
                continue
            labels = [
                item.strip().strip('"“”')
                for item in re.split(r"\s*(?:과|와|및)\s*", matched.group("labels"))
                if item.strip().strip('"“”')
            ]
            if labels:
                aliases.setdefault(matched.group("target"), []).extend(labels)
    inventory = {
        "contract_version": "source.inventory.v1",
        "datasets": datasets,
        "fields": sorted(fields),
        "metrics": _declared_ids(text, "등록 metric"),
        "relations": _declared_ids(text, "relations"),
        "recipes": _declared_ids(text, "등록 recipe ID"),
        "operations": _declared_ids(text, "허용 operation"),
        "alias_bindings": {key: sorted(set(values)) for key, values in sorted(aliases.items())},
    }
    inventory["inventory_sha256"] = sha256_json(inventory)
    return inventory


def _operation_ids(value):
    result = set()
    if isinstance(value, dict):
        if isinstance(value.get("op"), str):
            result.add(str(value["op"]))
        for child in value.values():
            result.update(_operation_ids(child))
    elif isinstance(value, list):
        for child in value:
            result.update(_operation_ids(child))
    return result


def _metadata_aliases(metadata, target):
    values = set()
    for dataset in (metadata.get("datasets") or {}).values():
        field = (dataset.get("fields") or {}).get(target) if isinstance(dataset, dict) else None
        if isinstance(field, dict):
            values.update(str(item) for item in field.get("aliases") or [])
    for section in ("fields", "metrics"):
        card = (metadata.get(section) or {}).get(target)
        if isinstance(card, dict):
            values.update(str(item) for item in card.get("aliases") or [])
    for card in (metadata.get("aliases") or {}).values():
        if isinstance(card, dict) and str(card.get("target_key") or "") == target:
            values.update(
                str(item.get("text") if isinstance(item, dict) else item)
                for item in card.get("values") or []
            )
    return values


def _validate_source_inventory_coverage(metadata, inventory, *, authoring_kind):
    datasets = set((metadata.get("datasets") or {}).keys())
    fields = {
        str(field)
        for dataset in (metadata.get("datasets") or {}).values()
        if isinstance(dataset, dict)
        for field in (dataset.get("fields") or {})
    }
    fields.update(str(field) for field in (metadata.get("fields") or {}))
    actual = {
        "datasets": datasets,
        "fields": fields,
        "metrics": set((metadata.get("metrics") or {}).keys()),
        "relations": set((metadata.get("relations") or {}).keys()),
        "recipes": set((metadata.get("recipes") or {}).keys()),
    }
    missing = []
    unexpected = []
    full_replace = str(authoring_kind) == "domain"
    for section in ("datasets", "fields", "metrics", "relations", "recipes"):
        required = set(inventory.get(section) or [])
        missing.extend(f"{section}:{item}" for item in sorted(required - actual[section]))
        if full_replace and required:
            unexpected.extend(f"{section}:{item}" for item in sorted(actual[section] - required))
    declared_operations = set(inventory.get("operations") or [])
    actual_operations = _operation_ids(metadata.get("recipes") or {})
    unexpected.extend(f"operations:{item}" for item in sorted(declared_operations - SOURCE_ALLOWED_OPERATIONS))
    if declared_operations:
        unexpected.extend(f"operations:{item}" for item in sorted(actual_operations - declared_operations))
    for target, required_aliases in (inventory.get("alias_bindings") or {}).items():
        actual_aliases = _metadata_aliases(metadata, str(target))
        missing.extend(f"aliases:{target}:{alias}" for alias in required_aliases if str(alias) not in actual_aliases)
    if missing or unexpected:
        raise ContractError(
            "metadata_dependency_error",
            "metadata_source_coverage",
            "Compiled metadata does not cover the explicit source inventory.",
            {
                "missing": missing[:32],
                "unexpected": unexpected[:32],
                "missing_count": len(missing),
                "unexpected_count": len(unexpected),
                "required_inventory_sha256": inventory.get("inventory_sha256"),
            },
        )
    required_counts = {
        section: len(inventory.get(section) or [])
        for section in ("datasets", "fields", "metrics", "relations", "recipes", "operations")
    }
    required_counts["aliases"] = sum(len(values) for values in (inventory.get("alias_bindings") or {}).values())
    compiled_counts = {section: len(values) for section, values in actual.items()}
    compiled_counts["operations"] = len(actual_operations)
    compiled_counts["aliases"] = sum(
        len(_metadata_aliases(metadata, target)) for target in (inventory.get("alias_bindings") or {})
    )
    evidence = {
        "contract_version": "source.inventory.coverage.v1",
        "required_inventory_sha256": inventory.get("inventory_sha256"),
        "required_counts": required_counts,
        "compiled_counts": compiled_counts,
        "missing_count": 0,
        "unexpected_count": 0,
        "coverage_passed": True,
        "validator_version": SOURCE_INVENTORY_VALIDATOR_VERSION,
    }
    evidence["coverage_sha256"] = sha256_json(evidence)
    return evidence


def _authoring_prompt(kind, source_text):
    allowed = sorted(AUTHORING_ALLOWED_KINDS[kind])
    existing = {
        name: sorted(EMBEDDED_RUNTIME_CATALOG.get(CATALOG_COLLECTIONS.get(name, ""), {}).keys())[:80]
        for name in allowed
        if name != "process_order"
    }
    contract = {
        "authoring_kind": kind,
        "identity": {"key": "stable_key"},
        "summary": "short summary",
        "records": [{"kind": allowed[0], "key": "stable_key", "contract": {}}],
        "assumptions": [],
        "missing_information": [],
    }
    return (
        "You compile Korean natural-language metadata into a closed JSON draft. "
        "Return exactly one JSON object, no markdown and no executable text. "
        f"Allowed record kinds: {allowed}. Existing keys: {json.dumps(existing, ensure_ascii=False)}. "
        f"Required shape: {json.dumps(contract, ensure_ascii=False)}. "
        "Use only explicit source facts. Do not invent credentials, SQL, URLs, paths, collection names or expressions.\n"
        f"SOURCE_TEXT:\n{source_text}"
    )


def _v2_section_patch_schema(authoring_kind):
    """Return a closed partial-upsert schema for the selected Flow ownership."""

    full_schema = load_schema("metadata-authoring-draft.schema.json")
    kind = str(authoring_kind or "").strip().casefold()
    sections = {
        "dataset": ("datasets",),
        "main_filter": (
            "aliases",
            "entity_groups",
            "grains",
            "orderings",
            "predicates",
            "recipes",
        ),
    }.get(kind)
    if sections is None:
        return full_schema
    owned_properties = {
        section: deepcopy(full_schema["properties"][section])
        for section in sections
    }
    reachable_defs = _v2_reachable_schema_defs(
        owned_properties,
        full_schema.get("$defs") or {},
    )
    schema = {
        "$schema": full_schema.get("$schema"),
        "title": f"metadata.authoring.{kind}.section-patch.v1",
        "type": "object",
        "additionalProperties": False,
        "minProperties": 1,
        "maxProperties": len(sections),
        "properties": _v2_partial_upsert_schema(owned_properties),
        "$defs": _v2_partial_upsert_schema(reachable_defs),
    }
    if kind == "dataset":
        schema["required"] = ["datasets"]
    return schema


def _v2_schema_refs(value):
    refs = set()
    if isinstance(value, dict):
        raw_ref = value.get("$ref")
        prefix = "#/$defs/"
        if isinstance(raw_ref, str) and raw_ref.startswith(prefix):
            refs.add(raw_ref[len(prefix) :])
        for child in value.values():
            refs.update(_v2_schema_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_v2_schema_refs(child))
    return refs


def _v2_reachable_schema_defs(properties, available_defs):
    pending = set(_v2_schema_refs(properties))
    selected = {}
    while pending:
        name = sorted(pending)[0]
        pending.remove(name)
        if name in selected:
            continue
        definition = available_defs.get(name)
        if not isinstance(definition, dict):
            raise ContractError(
                "metadata_schema_error",
                "metadata_prompt_contract",
                "Section patch schema contains a dangling definition reference.",
                {"definition": name},
            )
        selected[name] = deepcopy(definition)
        pending.update(_v2_schema_refs(definition) - set(selected))
    return {name: selected[name] for name in sorted(selected)}


def _v2_partial_upsert_schema(value):
    """Remove nested completeness requirements while retaining closed shapes."""

    if isinstance(value, list):
        return [_v2_partial_upsert_schema(child) for child in value]
    if not isinstance(value, dict):
        return deepcopy(value)
    result = {
        key: _v2_partial_upsert_schema(child)
        for key, child in value.items()
        if key != "required"
    }
    raw_type = result.get("type")
    if raw_type == "object" or (
        isinstance(raw_type, list) and "object" in raw_type
    ):
        current_min = result.get("minProperties")
        result["minProperties"] = max(
            1,
            int(current_min) if isinstance(current_min, int) else 0,
        )
    return result


def _v2_alias_only_manifest_patch(source_manifest):
    """Compile a source-sealed alias-only manifest without an LLM call."""

    if not isinstance(source_manifest, dict):
        return None
    counts = source_manifest.get("counts")
    inventories = source_manifest.get("inventories")
    if not isinstance(counts, dict) or not isinstance(inventories, dict):
        return None
    non_alias_kinds = (
        "datasets",
        "fields",
        "field_bindings",
        "field_roles",
        "metrics",
        "grains",
        "grain_keys",
        "grain_display_fields",
        "relations",
        "relation_endpoints",
        "relation_keys",
        "relation_policies",
        "recipes",
        "operations",
    )
    if any(int(counts.get(kind) or 0) != 0 for kind in non_alias_kinds):
        return None
    bindings = inventories.get("alias_bindings")
    if (
        int(counts.get("aliases") or 0) < 1
        or not isinstance(bindings, list)
        or len(bindings) != int(counts.get("alias_bindings") or 0)
    ):
        return None
    aliases = {}
    for raw_binding in bindings:
        if not isinstance(raw_binding, dict) or set(raw_binding) != {"alias", "target"}:
            return None
        alias = raw_binding.get("alias")
        target = raw_binding.get("target")
        if not isinstance(alias, str) or not alias or not isinstance(target, str) or not target:
            return None
        existing = aliases.get(alias)
        if existing is not None and existing != target:
            return None
        aliases[alias] = target
    return {"aliases": {key: aliases[key] for key in sorted(aliases)}}


def _v2_authoring_prompt(source_text, authoring_kind="domain", source_manifest=None):
    kind = str(authoring_kind or "domain").strip().casefold()
    schema = _v2_section_patch_schema(kind)
    required_inventory = source_manifest or extract_authoring_source_manifest(source_text)
    if kind == "dataset":
        shape = (
            "Return a section patch object with exactly one top-level key, datasets. "
            "For an existing dataset or field card, emit only keys explicitly changed by SOURCE_TEXT. "
            "If SOURCE_TEXT changes only a dataset display_name, omit fields entirely. "
            "Physical column names and physical aliases are read-only references; never use them as "
            "field object keys and emit field changes only under source-declared canonical IDs. "
            "For a new card, emit every field required by the complete metadata contract. "
            "Never use ellipses, placeholders, comments or empty objects. "
            "Do not repeat or edit other sections. "
        )
    elif kind == "main_filter":
        shape = (
            "Return an upsert-only section patch containing one or more of aliases, entity_groups, grains, "
            "orderings, predicates, recipes. For an existing card, emit only keys explicitly changed by "
            "SOURCE_TEXT; a new card must be complete. Never use ellipses, placeholders, comments or empty "
            "objects. Do not emit delete/remove directives or any other top-level key. "
        )
    elif kind == "domain_policy":
        shape = (
            "Return an upsert-only section patch containing one or more of prompt_extensions, "
            "specialized_functions, output_profile. Do not emit datasets, metrics, relations, filters, "
            "delete/remove directives or any other top-level key. Specialized functions are declarative "
            "registered cards only; never emit Python, SQL or executable expressions. "
        )
    else:
        shape = "Return one complete metadata.authoring.draft.v1 object. "
    return (
        "You compile natural-language business metadata into the closed "
        "metadata v6 contract. "
        + shape
        + "Return exactly one JSON object using literal UTF-8 text. Never emit malformed \\u escapes. "
        "without markdown, explanations, hashes or executable text. Use only facts "
        "explicitly present in SOURCE_TEXT. Never invent credentials, URLs, paths, "
        "collection names, SQL, Python, endpoint values or free-form expressions. "
        "Preserve canonical field and metric identifiers, and stable lowercase "
        "dataset, relation and recipe identifiers. Every relation, formula, grain "
        "and recipe dependency must resolve inside the returned object. "
        "Every relations.<relation_id> object must use the exact keys relation_id, "
        "left_dataset, right_dataset, left_keys, right_keys, join_type, cardinality, "
        "null_key_policy and multi_match_policy; never substitute endpoint names such "
        "as from, to, left or right. Cardinality must use exactly one of one_to_one, "
        "one_to_zero_or_one, one_to_many, many_to_one or many_to_many with underscores, "
        "never hyphenated prose. "
        "Field roles are closed: identifier fields use filter, group, join, project, output; "
        "LocalDate fields use filter, group, sort, project, output; currency or numeric metric "
        "fields use filter, aggregate, compare, sort, rank, metric, project, output; ordinary "
        "string fields use filter, group, project, sort, output. Add join only to an actual "
        "registered relation key. Use group, never dimension or group_by, and use compare, "
        "never compare_fields, as a field role. "
        "The REQUIRED_SOURCE_INVENTORY was deterministically extracted from SOURCE_TEXT; every listed ID and alias binding must be present exactly. "
        "Copy every source-sealed structural inventory exactly, including field_roles, "
        "relation_endpoints, relation_keys, relation_policies, grain_keys and "
        "grain_display_fields; do not add, remove, reorder or paraphrase those values. "
        "prompt_extensions.intent and prompt_extensions.answer are optional domain wording policies only.\n"
        "REQUIRED_SOURCE_INVENTORY:\n"
        + json.dumps(required_inventory, ensure_ascii=False, separators=(",", ":"))
        + "\n"
        "JSON_SCHEMA:\n"
        + json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        + "\nSOURCE_TEXT:\n"
        + source_text
    )


def _v2_domain_annotation_prompt(source_text, default_annotations):
    schema = load_schema("metadata-annotation-proposal.schema.json")
    return (
        "Return one JSON object and no markdown. This is an annotation-only metadata authoring pass. "
        "You may set only display_name and description. Never emit a contract version, datasets, fields, "
        "metrics, formulas, relations, joins, grains, predicates, recipes, aliases, prompts, functions, "
        "output policy, credentials, URLs, SQL or Python. The trusted executable blueprint is compiled "
        "outside the model and cannot be changed by this response. Keep the description factual and "
        "grounded only in SOURCE_TEXT.\nJSON_SCHEMA:\n"
        + json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        + "\nDEFAULT_ANNOTATIONS:\n"
        + json.dumps(default_annotations, ensure_ascii=False, separators=(",", ":"))
        + "\nSOURCE_TEXT:\n"
        + source_text
    )


def _validated_projection(kind, draft, source_text):
    allowed_root = {"authoring_kind", "identity", "summary", "records", "assumptions", "missing_information"}
    if set(draft) != allowed_root or draft.get("authoring_kind") != kind:
        raise ContractError("metadata_schema_error", "metadata_compile", "authoring draft root contract가 일치하지 않습니다.")
    identity = draft.get("identity")
    if not isinstance(identity, dict) or set(identity) != {"key"} or not str(identity.get("key") or "").strip():
        raise ContractError("metadata_schema_error", "metadata_compile", "stable identity key가 필요합니다.")
    records = draft.get("records")
    if not isinstance(records, list) or not records or len(records) > 128:
        raise ContractError("metadata_schema_error", "metadata_compile", "records는 1~128개여야 합니다.")
    projection = deepcopy(EMBEDDED_RUNTIME_CATALOG)
    normalized = []
    for record in records:
        if not isinstance(record, dict) or set(record) != {"kind", "key", "contract"}:
            raise ContractError("metadata_schema_error", "metadata_compile", "record contract가 닫혀 있지 않습니다.")
        record_kind = str(record.get("kind") or "")
        key = str(record.get("key") or "").strip()
        contract = record.get("contract")
        if record_kind not in AUTHORING_ALLOWED_KINDS[kind] or not key or not isinstance(contract, dict):
            raise ContractError("metadata_schema_error", "metadata_compile", "record kind/key/contract가 유효하지 않습니다.")
        forbidden_fragments = ("select ", "insert ", "update ", "delete ", "http://", "https://", "e" + "val(", "e" + "xec(")
        if any(token in json.dumps(contract, ensure_ascii=False).lower() for token in forbidden_fragments):
            raise ContractError("metadata_policy_error", "metadata_compile", "실행 가능한 query/URL/expression은 metadata draft에 허용되지 않습니다.")
        if record_kind == "process_order":
            items = projection.get("process_order") if isinstance(projection.get("process_order"), list) else []
            items = [item for item in items if str(item.get("oper_name") or "") != key]
            items.append(deepcopy(contract))
            projection["process_order"] = items
        else:
            collection = projection.get(CATALOG_COLLECTIONS[record_kind])
            if not isinstance(collection, dict):
                raise ContractError("metadata_dependency_error", "metadata_compile", "runtime catalog collection이 없습니다.")
            collection[key] = deepcopy(contract)
        normalized.append({"kind": record_kind, "key": key, "contract": deepcopy(contract)})
    projection.pop("catalog_sha256", None)
    projection["catalog_sha256"] = compute_catalog_sha256(projection)
    validate_runtime_catalog(projection)
    source_sha = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    compiled = {
        "contract_version": "metadata.authoring.compiled.v1",
        "schema_version": "metadata.v6",
        "authoring_kind": kind,
        "identity": {"key": str(identity["key"])},
        "source_text_sha256": source_sha,
        "summary": str(draft.get("summary") or "")[:1000],
        "records": normalized,
        "assumptions": [str(item)[:500] for item in draft.get("assumptions", [])[:20]],
        "missing_information": [str(item)[:500] for item in draft.get("missing_information", [])[:20]],
        "projected_catalog_sha256": projection["catalog_sha256"],
    }
    return compiled


def _bson_millisecond_utc(value):
    """Canonicalize a UTC instant to MongoDB BSON datetime precision."""
    if not isinstance(value, datetime):
        raise ContractError("metadata_schema_error", "metadata_prepare", "Candidate timestamp must be a datetime.")
    current = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    return current.replace(microsecond=(current.microsecond // 1000) * 1000)


def _safe_exception_location(exc):
    """Return only the final Python function name, never an exception message."""

    current = getattr(exc, "__traceback__", None)
    location = ""
    while current is not None:
        candidate = str(current.tb_frame.f_code.co_name or "")[:80]
        if candidate.isidentifier():
            location = candidate
        current = current.tb_next
    return location


class MetadataAuthoringEngine(Component):
    display_name = "메타데이터 등록·컴파일 엔진"
    description = "외부 Prompt/LLM 결과 또는 결정론적 정책 입력을 검증해 메타데이터 패키지를 컴파일하고 승인 기반 prepare/execute를 수행합니다."
    icon = "book-lock"

    inputs = [
        MessageInput(name="input_message", display_name="자연어 메타데이터 TXT", required=False, info="작업자가 자유 형식으로 작성한 원문입니다. 프롬프트 컨텍스트와 동일 원문인지 해시로 확인합니다."),
        DataInput(name="authoring_source_context", display_name="등록 원문 컨텍스트", required=False, info="외부 프롬프트 컨텍스트 노드가 봉인한 원문·유형·해시 정보입니다."),
        BoolInput(name="split_bootstrap", display_name="초기 등록 3분할 컴파일", value=False, advanced=True, info="도메인 최초 등록에서 도메인·데이터셋·주요 필터 제안 세 개를 결정론적으로 병합합니다."),
        DataInput(name="bootstrap_dataset_source_context", display_name="초기 데이터셋 원문 컨텍스트", required=False, info="분할 초기 등록의 데이터셋 원문·해시·목적을 봉인한 런타임 컨텍스트입니다."),
        DataInput(name="bootstrap_main_filter_source_context", display_name="초기 주요 필터 원문 컨텍스트", required=False, info="분할 초기 등록의 주요 필터 원문·해시·목적을 봉인한 런타임 컨텍스트입니다."),
        DataInput(name="approved_reference_context", display_name="승인 원천 참조 컨텍스트", required=False, info="제안서의 원천 식별자가 운영자 승인 레지스트리와 정확히 일치하는지 검증하는 정보입니다."),
        DataInput(name="authoring_invocation_result", display_name="등록 LLM 호출 결과", required=False, info="외부 LLM 노드가 반환한 단일 메타데이터 제안서 또는 추가 확인 요청입니다."),
        DataInput(name="bootstrap_dataset_invocation_result", display_name="초기 데이터셋 LLM 호출 결과", required=False, info="분할 초기 등록의 데이터셋 제안서 또는 추가 확인 요청입니다."),
        DataInput(name="bootstrap_main_filter_invocation_result", display_name="초기 주요 필터 LLM 호출 결과", required=False, info="분할 초기 등록의 주요 필터 제안서 또는 추가 확인 요청입니다."),
        DropdownInput(name="authoring_kind", display_name="등록 유형", options=["domain", "dataset", "main_filter", "domain_policy"], value="domain", info="도메인, 데이터셋, 주요 필터, 관리자 정책 중 처리할 등록 계약을 선택합니다."),
        DropdownInput(name="source_grounding_mode", display_name="자연어 입력 해석 방식", options=["freeform_llm", "explicit_inventory"], value="freeform_llm", advanced=True, info="일반 작업자 입력은 freeform_llm을 사용하며, explicit_inventory는 관리자 검증 경로 전용입니다."),
        DropdownInput(name="metadata_contract_mode", display_name="메타데이터 계약", options=["domain_package_v2"], value="domain_package_v2", info="컴파일과 저장에 적용할 메타데이터 패키지 계약 버전입니다."),
        StrInput(name="domain_id", display_name="도메인 ID", value="default", info="등록·패치할 업무 도메인의 고유 식별자입니다. 공유 시 대상 도메인 ID로 바꿉니다."),
        StrInput(name="environment", display_name="운영 환경", value="production", info="메타데이터 리비전과 활성 포인터를 구분할 환경 이름입니다."),
        DropdownInput(name="revision_policy", display_name="리비전 정책", options=["auto_next", "explicit"], value="auto_next", info="다음 리비전을 자동 계산하거나 명시적 리비전 번호를 사용할지 선택합니다."),
        IntInput(name="revision", display_name="명시적 도메인 리비전", value=1, info="리비전 정책이 explicit일 때 사용할 양의 정수 리비전입니다."),
        DataInput(name="inline_base_domain_bundle", display_name="인라인 기준 도메인 번들(패치 Dry Run)", required=False, info="데이터셋·필터 패치를 저장 없이 검증할 때 사용할 기준 도메인 번들입니다."),
        MultilineInput(
            name="trusted_blueprint_json",
            display_name="신뢰 실행 블루프린트 JSON(관리자 전용)",
            value="",
            required=False,
            advanced=True,
            info="관리자 전용 결정론적 등록 경로에서만 사용하는 검토 완료 블루프린트입니다.",
        ),
        StrInput(
            name="trusted_blueprint_sha256",
            display_name="신뢰 블루프린트 SHA-256 핀(관리자 전용)",
            value="",
            required=False,
            advanced=True,
            info="신뢰 실행 블루프린트가 변조되지 않았는지 확인할 SHA-256 값입니다.",
        ),
        MultilineInput(name="intent_prompt_extension", display_name="의도 분석 특화 프롬프트", value="", required=False, info="공통 의도 분석 프롬프트 뒤에 연결할 도메인별 용어·판단 규칙입니다."),
        MultilineInput(name="answer_prompt_extension", display_name="결과 생성 특화 프롬프트", value="", required=False, info="공통 결과 생성 프롬프트 뒤에 연결할 도메인별 표현·주의 규칙입니다."),
        MultilineInput(name="specialized_functions_json", display_name="등록 특화 함수 JSON", value="", required=False, info="Typed IR 기본 연산으로 표현하기 어려운 검토 완료 격리 함수 등록 정보입니다."),
        MultilineInput(name="output_profile_json", display_name="출력 프로필 JSON", value="", required=False, info="표시 컬럼, 표 미리보기, 다운로드 등 도메인별 기본 출력 설정입니다."),
        DropdownInput(name="mode", display_name="실행 모드", options=["prepare", "execute"], value="prepare", info="prepare는 후보를 만들고 execute는 외부 승인 이벤트를 검증한 뒤 저장합니다."),
        MultilineInput(name="approval_event_json", display_name="외부 승인 이벤트 JSON", value="", required=False, info="execute에서 후보 해시와 승인 주체를 확인할 외부 승인 이벤트입니다."),
        SecretStrInput(name="mongo_uri", display_name="MongoDB 연결 URI", value="", required=False, info="승인 후보, 리비전, 번들, 감사 이력을 저장할 MongoDB 연결 문자열입니다."),
        StrInput(name="mongo_database", display_name="MongoDB 데이터베이스", value="", required=False, info="v6 메타데이터 컬렉션이 위치한 데이터베이스 이름입니다."),
        StrInput(name="pending_collection", display_name="승인 대기 컬렉션", value="agent_v6_pending_writes", info="prepare 후보와 만료 시각을 저장하는 컬렉션입니다."),
        StrInput(name="revision_collection", display_name="리비전 컬렉션", value="agent_v6_metadata_revisions", info="도메인별 메타데이터 리비전 기록을 저장하는 컬렉션입니다."),
        StrInput(name="bundle_collection", display_name="불변 도메인 번들 컬렉션", value="agent_v6_metadata_bundles", info="컴파일과 검증을 마친 불변 도메인 번들을 저장하는 컬렉션입니다."),
        StrInput(name="active_collection", display_name="활성 포인터 컬렉션", value="agent_v6_metadata_active", info="환경·도메인별 현재 활성 리비전을 가리키는 컬렉션입니다."),
        StrInput(name="audit_collection", display_name="등록 감사 컬렉션", value="agent_v6_authoring_audit", info="등록 준비·승인 실행·거부 이력을 추적하는 감사 컬렉션입니다."),
        IntInput(name="mongo_timeout_ms", display_name="MongoDB 제한 시간(ms)", value=5000, info="MongoDB 연결과 등록 트랜잭션에 적용할 제한 시간(밀리초)입니다."),
        IntInput(name="candidate_ttl_seconds", display_name="후보 유효 시간(초)", value=86400, info="prepare 후보가 외부 승인을 기다릴 수 있는 최대 시간입니다."),
        BoolInput(name="dry_run", display_name="저장 없는 준비 검증", value=False, info="활성화하면 prepare 결과를 MongoDB에 저장하지 않고 컴파일·계약 검증만 수행합니다."),
    ]
    outputs = [Output(name="response", display_name="메타데이터 등록 응답", method="run_authoring", types=["Data"])]

    def _mongo(self):
        uri = _secret_text(getattr(self, "mongo_uri", "")) or os.getenv("MONGODB_URI", "").strip()
        if not uri:
            raise ContractError("metadata_store_unavailable", "metadata_store", "MongoDB URI가 필요합니다.")
        from pymongo import MongoClient
        client = MongoClient(uri, serverSelectionTimeoutMS=max(500, min(int(getattr(self, "mongo_timeout_ms", 5000)), 30000)))
        database = str(getattr(self, "mongo_database", "") or os.getenv("MONGODB_DATABASE", "datagov"))
        return client, client[database]

    def _collection_names(self):
        values = {
            role: str(getattr(self, role, expected) or "").strip()
            for role, expected in V6_AUTHORING_COLLECTIONS.items()
        }
        if values != V6_AUTHORING_COLLECTIONS or len(set(values.values())) != len(values):
            raise ContractError(
                "metadata_policy_error",
                "metadata_store_config",
                "Authoring collections are role-bound to the registered v6-only names.",
                {"expected": V6_AUTHORING_COLLECTIONS, "actual": values},
            )
        return values

    def _pending_payload(self, *, kind, domain_id, environment, revision, expected_active, candidate_id, candidate_hash, hash_material, now, expires):
        base_revision = int(expected_active.get("revision") or 0)
        payload = {
            "contract_version": "pending.metadata.write.v1",
            "authoring_kind": kind,
            "domain_id": domain_id,
            "environment": environment,
            "candidate_id": candidate_id,
            "candidate_sha256": candidate_hash,
            "status": "prepared",
            "target_revision": int(revision),
            "base_revision": base_revision if base_revision > 0 else None,
            "base_bundle_sha256": str(expected_active.get("bundle_sha256") or "") or None,
            "base_package_sha256": str(expected_active.get("package_sha256") or "") or None,
            "prepared_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "hash_material": deepcopy(hash_material),
        }
        return validate_contract(
            payload,
            "pending-metadata-write.schema.json",
            stage="metadata_prepare",
            error_code="metadata_schema_error",
        )

    def _pending_from_storage(self, document, *, candidate_id, candidate_hash):
        if not isinstance(document, dict) or document.get("_id") != candidate_id:
            raise ContractError("approval_not_found", "metadata_execute", "Pending v2 domain package candidate was not found.")
        payload = validate_contract(
            deepcopy(document.get("pending_payload") or {}),
            "pending-metadata-write.schema.json",
            stage="metadata_execute",
            error_code="approval_contract_error",
        )
        if payload.get("candidate_id") != candidate_id or payload.get("candidate_sha256") != candidate_hash:
            raise ContractError("approval_hash_mismatch", "metadata_execute", "Stored pending payload is not bound to the approval event.")
        if document.get("pending_payload_sha256") != sha256_json(payload):
            raise ContractError("approval_hash_mismatch", "metadata_execute", "Stored pending payload seal is invalid.")
        for key in ("authoring_kind", "domain_id", "environment"):
            if document.get(key) != payload.get(key):
                raise ContractError("approval_hash_mismatch", "metadata_execute", "Stored pending wrapper identity does not match its payload.", {"field": key})
        try:
            payload_expiry = datetime.fromisoformat(str(payload["expires_at"]).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ContractError("approval_contract_error", "metadata_execute", "Pending payload expiry is invalid.") from exc
        storage_expiry = document.get("expires_at")
        if isinstance(storage_expiry, datetime):
            # PyMongo decodes BSON UTC datetimes as naive values unless its
            # client is configured timezone-aware. Treat that documented shape
            # as UTC; aware values are converted normally. Equality remains
            # exact after canonicalization (no tolerance window).
            storage_expiry_utc = (
                storage_expiry.replace(tzinfo=timezone.utc)
                if storage_expiry.tzinfo is None
                else storage_expiry.astimezone(timezone.utc)
            )
        else:
            storage_expiry_utc = None
        if storage_expiry_utc != payload_expiry.astimezone(timezone.utc):
            raise ContractError("approval_hash_mismatch", "metadata_execute", "Mongo TTL expiry does not match the immutable pending payload.")
        if sha256_json(payload.get("hash_material") or {}) != candidate_hash:
            raise ContractError("approval_hash_mismatch", "metadata_execute", "Stored pending hash material does not match its candidate hash.")
        return payload

    def _response(self, status, *, stage, **values):
        material = {
            "contract_version": "metadata.authoring.response.v1",
            "response_type": "metadata_authoring",
            "status": status,
            "stage": stage,
            "authoring_kind": str(getattr(self, "authoring_kind", "domain")),
            "metadata_contract_mode": str(getattr(self, "metadata_contract_mode", "domain_package_v2")),
            "domain_id": str(getattr(self, "domain_id", "default")),
            "environment": str(getattr(self, "environment", "production")),
            **values,
        }
        material["response_sha256"] = sha256_json(material)
        return Data(data=validate_authoring_response_hash(material))

    def _prepare_v2_full_compat(self):
        source_text = _authoring_source_text(self)
        if not source_text or len(source_text.encode("utf-8")) > 65536:
            raise ContractError("metadata_schema_error", "metadata_prepare", "metadata TXT must contain 1 to 65536 UTF-8 bytes.")
        source_manifest = extract_authoring_source_manifest(source_text)
        model = getattr(self, "language_model", None)
        if model is None or not hasattr(model, "invoke"):
            raise ContractError("metadata_llm_unavailable", "metadata_draft", "A connected Language Model is required for prepare.")
        domain_id = str(getattr(self, "domain_id", "default") or "").strip()
        environment = str(getattr(self, "environment", "production") or "").strip()
        revision = int(getattr(self, "revision", 1))
        draft = _json_object(_model_text(model.invoke(_v2_authoring_prompt(source_text))))
        package = compile_domain_package(
            draft,
            domain_id,
            environment,
            revision=revision,
            lifecycle_status="validated",
        )
        bundle_document = make_bundle_document(package)
        active_pointer = make_active_pointer_document(package)
        # BSON persists datetimes at millisecond precision.  Seal the immutable
        # payload and TTL wrapper from that exact precision so a Mongo roundtrip
        # cannot change bytes between prepare and execute.
        now = _bson_millisecond_utc(datetime.now(timezone.utc))
        expires = now + timedelta(seconds=max(300, min(int(getattr(self, "candidate_ttl_seconds", 86400)), 604800)))
        expected_active = {"revision": 0, "bundle_sha256": "", "package_sha256": ""}
        client = db = None
        dry_run = bool(getattr(self, "dry_run", False))
        if not dry_run:
            client, db = self._mongo()
            active = db[str(getattr(self, "active_collection", "agent_v6_metadata_active"))].find_one(
                {"_id": f"active:{environment}:{domain_id}"}
            ) or {}
            expected_active = {
                "revision": int(active.get("revision") or 0),
                "bundle_sha256": str(active.get("bundle_sha256") or ""),
                "package_sha256": str(active.get("package_sha256") or ""),
            }
            if revision <= expected_active["revision"]:
                client.close()
                raise ContractError(
                    "metadata_revision_conflict",
                    "metadata_prepare",
                    "Domain revision must be greater than the active revision.",
                    {"active_revision": expected_active["revision"], "requested_revision": revision},
                )
        validation = {
            "schema": "passed",
            "semantic_lint": "passed",
            "dependency_closure": "passed",
            "hash_seal": "passed",
        }
        hash_material = {
            "contract_version": "pending.domain-package.hash-material.v1",
            "domain_package": package,
            "bundle_document": bundle_document,
            "active_pointer": active_pointer,
            "expected_active": expected_active,
            "validation": validation,
            "prepared_at": now.isoformat(),
            "expires_at": expires.isoformat(),
        }
        candidate_hash = sha256_json(hash_material)
        candidate_id = f"candidate:{candidate_hash}"
        envelope = {
            "_id": candidate_id,
            "candidate_id": candidate_id,
            "candidate_sha256": candidate_hash,
            "authoring_kind": "domain",
            "metadata_contract_mode": "domain_package_v2",
            "domain_id": domain_id,
            "environment": environment,
            "status": "prepared",
            "hash_material": hash_material,
            "prepared_at": now,
            "expires_at": expires,
        }
        if not dry_run:
            pending = db[str(getattr(self, "pending_collection", "agent_v6_pending_writes"))]
            audit = db[str(getattr(self, "audit_collection", "agent_v6_authoring_audit"))]
            pending.create_index("expires_at", expireAfterSeconds=0)
            existing = pending.find_one({"_id": candidate_id})
            if existing and str(existing.get("candidate_sha256")) != candidate_hash:
                client.close()
                raise ContractError("metadata_hash_conflict", "metadata_prepare", "Candidate ID and hash do not match.")
            if not existing:
                pending.insert_one(envelope)
                audit.insert_one(
                    {
                        "event_type": "prepared",
                        "candidate_id": candidate_id,
                        "candidate_sha256": candidate_hash,
                        "metadata_contract_mode": "domain_package_v2",
                        "domain_id": domain_id,
                        "environment": environment,
                        "package_sha256": package["package_sha256"],
                        "bundle_sha256": package["bundle_sha256"],
                        "occurred_at": now,
                    }
                )
            client.close()
        catalog = package["runtime_catalog"]
        return self._response(
            "ok",
            stage="prepared",
            candidate_id=candidate_id,
            candidate_sha256=candidate_hash,
            package_sha256=package["package_sha256"],
            bundle_sha256=package["bundle_sha256"],
            catalog_sha256=catalog["catalog_sha256"],
            revision=package["revision"],
            persisted=not dry_run,
            diff={
                "datasets": len(catalog.get("datasets") or {}),
                "fields": len(catalog.get("fields") or {}),
                "metrics": len(catalog.get("metrics") or {}),
                "relations": len(catalog.get("relations") or {}),
                "recipes": len(catalog.get("recipes") or {}),
            },
            validation=validation,
            expires_at=expires.isoformat(),
            llm_usage={"draft_llm_calls": 1, "annotation_llm_calls": 0, "repair_llm_calls": 0},
        )

    def _prepare_v2(self):
        collections = self._collection_names()
        kind = str(getattr(self, "authoring_kind", "domain") or "domain")
        if kind not in {"domain", "dataset", "main_filter", "domain_policy"}:
            raise ContractError("metadata_schema_error", "metadata_prepare", "Unsupported v2 authoring kind.")
        domain_id = str(getattr(self, "domain_id", "default") or "").strip()
        environment = str(getattr(self, "environment", "production") or "").strip()
        grounding_mode = str(getattr(self, "source_grounding_mode", "freeform_llm") or "freeform_llm").strip()
        if grounding_mode not in {"freeform_llm", "explicit_inventory"}:
            raise ContractError(
                "metadata_schema_error",
                "metadata_source_grounding",
                "source_grounding_mode must be freeform_llm or explicit_inventory.",
            )
        blueprint_text = str(getattr(self, "trusted_blueprint_json", "") or "").strip()
        trusted_blueprint_pin = str(getattr(self, "trusted_blueprint_sha256", "") or "").strip()
        if kind == "domain" and bool(blueprint_text) != bool(trusted_blueprint_pin):
            raise ContractError(
                "metadata_blueprint_invalid",
                "metadata_blueprint",
                "Trusted blueprint JSON and its external SHA-256 pin must be configured together.",
            )
        annotation_only = kind == "domain" and bool(blueprint_text) and bool(trusted_blueprint_pin)
        split_bootstrap = bool(getattr(self, "split_bootstrap", False))
        if split_bootstrap and (
            kind != "domain"
            or grounding_mode != "freeform_llm"
            or bool(blueprint_text)
            or bool(trusted_blueprint_pin)
        ):
            raise ContractError(
                "metadata_policy_error",
                "metadata_authoring",
                "분할 초기 등록은 blueprint가 없는 domain/freeform_llm prepare에서만 사용할 수 있습니다.",
            )
        bootstrap_branches = None
        section_context = None
        expected_purpose = {
            "domain": "metadata_domain_annotation" if annotation_only else "metadata_domain_draft",
            "dataset": "metadata_dataset_draft",
            "main_filter": "metadata_main_filter_draft",
            "domain_policy": "metadata_domain_policy",
        }[kind]
        if split_bootstrap:
            bootstrap_branches, source_text = _split_bootstrap_source(
                self,
                domain_id=domain_id,
                environment=environment,
            )
        elif kind != "domain_policy":
            raw_section_context = getattr(self, "authoring_source_context", None)
            section_context_payload = getattr(
                raw_section_context, "data", raw_section_context
            )
            if isinstance(section_context_payload, dict) and section_context_payload:
                section_context = _bootstrap_context_payload(
                    self,
                    input_name="authoring_source_context",
                    kind=kind,
                    purpose=expected_purpose,
                    domain_id=domain_id,
                    environment=environment,
                    bootstrap_fragment=False,
                    grounding_mode=grounding_mode,
                    annotation_only=annotation_only,
                    expected_invoke=None,
                )
                source_text = section_context["source_text"]
            else:
                # Deterministic no-LLM paths and early source-inventory errors do
                # not require a prompt context. Any path that actually invokes a
                # model is rejected below unless the sealed context is present.
                source_text = _authoring_source_text(self)
        else:
            source_text = _authoring_source_text(self)
        if not source_text or len(source_text.encode("utf-8")) > 65536:
            raise ContractError("metadata_schema_error", "metadata_prepare", "metadata TXT must contain 1 to 65536 UTF-8 bytes.")
        strict_inventory = grounding_mode == "explicit_inventory" or annotation_only
        if strict_inventory:
            try:
                source_manifest = extract_authoring_source_manifest(source_text)
            except AuthoringSourceManifestError as exc:
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_source_inventory",
                    "Explicit-inventory metadata is ambiguous or invalid.",
                    deepcopy(exc.evidence),
                ) from exc
        else:
            source_manifest = _freeform_authoring_manifest(source_text)
        if kind == "dataset" and strict_inventory:
            inventories = source_manifest.get("inventories")
            datasets = inventories.get("datasets") if isinstance(inventories, dict) else None
            dataset_fields = (
                inventories.get("dataset_fields") if isinstance(inventories, dict) else None
            )
            valid_dataset_inventory = (
                isinstance(datasets, list)
                and bool(datasets)
                and isinstance(dataset_fields, dict)
                and set(dataset_fields) == set(datasets)
                and all(
                    isinstance(dataset_fields.get(dataset_id), list)
                    and bool(dataset_fields[dataset_id])
                    for dataset_id in datasets
                )
            )
            if not valid_dataset_inventory:
                counts = source_manifest.get("counts")
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_source_inventory",
                    "Dataset authoring requires explicit dataset IDs and canonical field declarations.",
                    {
                        "source_manifest_sha256": str(
                            source_manifest.get("manifest_sha256") or ""
                        ),
                        "dataset_count": int(counts.get("datasets") or 0)
                        if isinstance(counts, dict)
                        else 0,
                        "field_bindings": int(counts.get("field_bindings") or 0)
                        if isinstance(counts, dict)
                        else 0,
                    },
                )
        trusted_blueprint = None
        if annotation_only:
            if len(blueprint_text.encode("utf-8")) > 1048576 or not re.fullmatch(r"[0-9a-f]{64}", trusted_blueprint_pin):
                raise ContractError(
                    "metadata_blueprint_invalid",
                    "metadata_blueprint",
                    "Trusted executable blueprint configuration is invalid.",
                )
            try:
                parsed_blueprint = json.loads(blueprint_text)
            except json.JSONDecodeError as exc:
                raise ContractError(
                    "metadata_blueprint_invalid",
                    "metadata_blueprint",
                    "Trusted executable blueprint JSON is invalid.",
                    {"line": exc.lineno},
                ) from exc
            trusted_blueprint = validate_executable_blueprint(
                parsed_blueprint,
                expected_blueprint_sha256=trusted_blueprint_pin,
                expected_domain_id=domain_id,
                expected_environment=environment,
                source_manifest=source_manifest,
            )
        deterministic_alias_patch = (
            _v2_alias_only_manifest_patch(source_manifest)
            if kind == "main_filter" and strict_inventory
            else None
        )
        model_required = kind in {"domain", "dataset"} or (
            kind == "main_filter" and deterministic_alias_patch is None
        )
        if model_required and not split_bootstrap and section_context is None:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_context",
                "A sealed authoring runtime context is required before any LLM invocation.",
                {"authoring_kind": kind, "expected_purpose": expected_purpose},
            )
        if section_context is not None and section_context["invoke"] is not model_required:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_source_context",
                "등록 runtime context의 invoke 결정이 compiler 경로와 일치하지 않습니다.",
                {"authoring_kind": kind, "expected_purpose": expected_purpose},
            )
        authoring_proposal_validation = None
        authoring_proposals_validation = None
        bootstrap_raw_draft_sha256 = ""
        metric_binding_completion = None
        semantic_alias_normalization = None
        domain_template_expansion = None
        approved_planner_policy = {}
        if split_bootstrap:
            invocation_specs = {
                "domain": ("authoring_invocation_result", "metadata_domain_draft"),
                "dataset": (
                    "bootstrap_dataset_invocation_result",
                    "metadata_dataset_draft",
                ),
                "main_filter": (
                    "bootstrap_main_filter_invocation_result",
                    "metadata_main_filter_draft",
                ),
            }
            raw_proposals = {}
            invocation_error = None
            for branch_kind in BOOTSTRAP_BRANCH_ORDER:
                input_name, branch_purpose = invocation_specs[branch_kind]
                try:
                    raw_proposals[branch_kind] = _authoring_invocation_draft(
                        self,
                        input_name=input_name,
                        expected_purpose=branch_purpose,
                        required=True,
                        expected_output_schema=bootstrap_branches[branch_kind]["output_schema"],
                        expected_runtime_context_sha256=bootstrap_branches[
                            branch_kind
                        ]["runtime_context_sha256"],
                    )
                except ContractError as exc:
                    if invocation_error is None:
                        invocation_error = exc
            if invocation_error is not None:
                raise invocation_error
            fragments = {}
            proposal_evidence = {}
            for branch_kind in BOOTSTRAP_BRANCH_ORDER:
                fragment, evidence = _unwrap_bootstrap_authoring_proposal(
                    raw_proposals[branch_kind],
                    kind=branch_kind,
                    source_sha256=bootstrap_branches[branch_kind]["source_sha256"],
                    composite_source_sha256=str(source_manifest.get("source_sha256") or ""),
                )
                fragments[branch_kind] = fragment
                if branch_kind == "dataset":
                    evidence = {
                        **evidence,
                        "dataset_ir_contract_version": "metadata.bootstrap.dataset-ir.v1",
                        "dataset_ir_expander_version": "metadata.dataset-ir-expander.v1",
                        "dataset_ir_sha256": str(evidence.get("draft_sha256") or ""),
                    }
                proposal_evidence[branch_kind] = evidence
            raw_reference = getattr(self, "approved_reference_context", None)
            registry_context = getattr(raw_reference, "data", raw_reference)
            registry_context = registry_context if isinstance(registry_context, dict) else {}
            approved_planner_policy = deepcopy(
                (registry_context.get("semantic_templates") or {}).get(
                    "planner_policy"
                )
                or {}
            )
            (
                fragments["domain"],
                domain_template_expansion,
            ) = _expand_bootstrap_domain_annotation(
                fragments["domain"],
                semantic_templates=registry_context.get("semantic_templates"),
                semantic_vocabulary=registry_context.get("semantic_vocabulary"),
            )
            proposal_evidence["domain"] = {
                **proposal_evidence["domain"],
                "template_expansion": deepcopy(domain_template_expansion),
            }
            dataset_reconciliation = {}
            main_filter_reconciliation = {}
            invocation_draft = _merge_bootstrap_fragments(
                fragments,
                dataset_descriptors=registry_context.get("dataset_descriptors"),
                semantic_vocabulary=registry_context.get("semantic_vocabulary"),
                reconciliation_out=dataset_reconciliation,
                main_filter_reconciliation_out=main_filter_reconciliation,
                domain_already_expanded=True,
            )
            (
                invocation_draft,
                metric_binding_completion,
            ) = _complete_unambiguous_metric_bindings(
                invocation_draft,
                registry_context.get("semantic_vocabulary"),
            )
            (
                invocation_draft,
                semantic_alias_normalization,
            ) = _normalize_bootstrap_alias_shorthand(
                invocation_draft,
                registry_context.get("semantic_vocabulary"),
            )
            proposal_evidence["dataset"] = {
                **proposal_evidence["dataset"],
                "registry_reconciliation": dataset_reconciliation,
            }
            proposal_evidence["main_filter"] = {
                **proposal_evidence["main_filter"],
                "main_filter_ir_expansion": main_filter_reconciliation,
            }
            bootstrap_raw_draft_sha256 = sha256_json(invocation_draft)
            proposal_hashes = {
                branch_kind: proposal_evidence[branch_kind]["proposal_sha256"]
                for branch_kind in BOOTSTRAP_BRANCH_ORDER
            }
            authoring_proposals_validation = {
                branch_kind: deepcopy(proposal_evidence[branch_kind])
                for branch_kind in BOOTSTRAP_BRANCH_ORDER
            }
            authoring_proposal_validation = {
                "contract_version": "metadata.authoring.proposal.validation.v1",
                "proposal_contract_version": "metadata.authoring.proposal.v1",
                "status": "complete",
                "source_sha256": str(source_manifest.get("source_sha256") or ""),
                "proposal_sha256": sha256_json(proposal_hashes),
                "draft_sha256": bootstrap_raw_draft_sha256,
                "expanded_draft_sha256": bootstrap_raw_draft_sha256,
                "dataset_ir_sha256": str(
                    proposal_evidence["dataset"].get("dataset_ir_sha256") or ""
                ),
                "dataset_ir_expander_version": "metadata.dataset-ir-expander.v1",
                "domain_template_expander_version": (
                    "metadata.domain-template-expansion.v1"
                ),
                "semantic_templates_sha256": str(
                    (domain_template_expansion or {}).get(
                        "semantic_templates_sha256"
                    )
                    or ""
                ),
            }
        else:
            invocation_draft = _authoring_invocation_draft(
                self,
                input_name="authoring_invocation_result",
                expected_purpose=expected_purpose,
                required=model_required,
                expected_output_schema=(
                    section_context.get("output_schema")
                    if section_context is not None and model_required
                    else None
                ),
                expected_runtime_context_sha256=(
                    section_context.get("runtime_context_sha256")
                    if section_context is not None and model_required
                    else ""
                ),
            )
            if model_required and grounding_mode == "freeform_llm" and not annotation_only:
                invocation_draft, authoring_proposal_validation = _unwrap_freeform_authoring_proposal(
                    invocation_draft,
                    source_sha256=str(source_manifest.get("source_sha256") or ""),
                )
            if model_required and kind in {"dataset", "main_filter"}:
                raw_reference = getattr(self, "approved_reference_context", None)
                registry_context = getattr(raw_reference, "data", raw_reference)
                registry_context = (
                    registry_context
                    if isinstance(registry_context, dict)
                    else {}
                )
                compact_ir_sha256 = sha256_json(invocation_draft)
                section_ir_reconciliation = {}
                if kind == "dataset":
                    invocation_draft = _expand_compact_dataset_fragment(
                        invocation_draft,
                        dataset_descriptors=registry_context.get(
                            "dataset_descriptors"
                        ),
                        reconciliation_out=section_ir_reconciliation,
                    )
                    expander_version = "metadata.dataset-ir-expander.v1"
                else:
                    invocation_draft = _expand_compact_main_filter_fragment(
                        invocation_draft,
                        approved_semantic_vocabulary=registry_context.get(
                            "semantic_vocabulary"
                        ),
                        reconciliation_out=section_ir_reconciliation,
                    )
                    expander_version = "metadata.main-filter-ir-expansion.v1"
                if authoring_proposal_validation is not None:
                    authoring_proposal_validation = {
                        **(authoring_proposal_validation or {}),
                        "compact_ir_sha256": compact_ir_sha256,
                        "expanded_draft_sha256": sha256_json(invocation_draft),
                        "section_ir_expander_version": expander_version,
                        "section_ir_reconciliation": section_ir_reconciliation,
                    }
        prevalidated_domain_draft = None
        prevalidated_source_binding = None
        filter_operator_normalization = None
        if kind == "domain" and not annotation_only:
            prevalidated_domain_draft = _enforce_domain_policy_boundary(
                invocation_draft,
                source_sha256=str(source_manifest.get("source_sha256") or ""),
                proposal_sha256=str((authoring_proposal_validation or {}).get("proposal_sha256") or ""),
                grounding_mode=grounding_mode,
                approved_planner_policy=approved_planner_policy,
            )
            if split_bootstrap:
                # Fragment schemas intentionally permit omitted execution refs.
                # Seal every dataset with the operator registry before the final
                # full-draft schema and compiler gates; model-supplied refs never
                # become authoritative.
                prevalidated_source_binding = _validate_authoring_source_bindings(
                    prevalidated_domain_draft,
                    source_sha256=str(source_manifest.get("source_sha256") or ""),
                    proposal_sha256=str((authoring_proposal_validation or {}).get("proposal_sha256") or ""),
                    approved_reference_context=getattr(self, "approved_reference_context", None),
                    domain_id=domain_id,
                    require_registry_exact_set=True,
                )
            if not split_bootstrap:
                raw_reference = getattr(self, "approved_reference_context", None)
                registry_context = getattr(raw_reference, "data", raw_reference)
                registry_context = registry_context if isinstance(registry_context, dict) else {}
                (
                    prevalidated_domain_draft,
                    metric_binding_completion,
                ) = _complete_unambiguous_metric_bindings(
                    prevalidated_domain_draft,
                    registry_context.get("semantic_vocabulary"),
                )
            (
                prevalidated_domain_draft,
                filter_operator_normalization,
            ) = _normalize_filter_operator_aliases(prevalidated_domain_draft)
            prevalidated_domain_draft = validate_contract(
                prevalidated_domain_draft,
                "metadata-authoring-draft.schema.json",
                stage="metadata_section_patch",
                error_code="metadata_schema_error",
            )
            if prevalidated_source_binding is None:
                prevalidated_source_binding = _validate_authoring_source_bindings(
                    prevalidated_domain_draft,
                    source_sha256=str(source_manifest.get("source_sha256") or ""),
                    proposal_sha256=str((authoring_proposal_validation or {}).get("proposal_sha256") or ""),
                    approved_reference_context=getattr(self, "approved_reference_context", None),
                    domain_id=domain_id,
                )
        draft_llm_calls = 0
        dry_run = bool(getattr(self, "dry_run", False))
        active_package = None
        client = db = None

        inline_value = getattr(getattr(self, "inline_base_domain_bundle", None), "data", getattr(self, "inline_base_domain_bundle", None))
        if isinstance(inline_value, dict) and inline_value:
            inline_package = inline_value.get("domain_package") if isinstance(inline_value.get("domain_package"), dict) else inline_value
            active_package = validate_domain_package(inline_package)
            if active_package["domain_id"] != domain_id or active_package["environment"] != environment:
                raise ContractError("metadata_dependency_error", "metadata_prepare", "Inline base package identity does not match node inputs.")

        # Section patches need the exact active base before their owned patch
        # can be checked.  Keep this read short-lived: no LLM/schema/compiler
        # work runs while a Mongo client remains open.
        if not dry_run and kind != "domain":
            client, db = self._mongo()
            try:
                active_name = collections["active_collection"]
                bundle_name = collections["bundle_collection"]
                pointer = db[active_name].find_one({"_id": f"active:{environment}:{domain_id}"})
                if pointer:
                    active_package = load_active_domain_bundle(
                        db,
                        domain_id,
                        environment,
                        active_collection=active_name,
                        bundle_collection=bundle_name,
                    )
            finally:
                client.close()
                client = db = None
        if kind != "domain" and active_package is None:
            raise ContractError(
                "metadata_dependency_error",
                "metadata_prepare",
                "Section patches require an exact active v2 domain package or inline dry-run base.",
            )
        base_draft = (
            runtime_catalog_v2_to_authoring_draft(active_package["runtime_catalog"])
            if kind != "domain"
            else None
        )

        blueprint_validation = None
        if kind == "domain":
            if annotation_only:
                raw_annotations = deepcopy(invocation_draft)
                annotations = validate_contract(
                    raw_annotations,
                    "metadata-annotation-proposal.schema.json",
                    stage="metadata_annotation_proposal",
                    error_code="metadata_schema_error",
                )
                raw_patch = merge_blueprint_annotations(
                    trusted_blueprint,
                    annotations,
                    expected_blueprint_sha256=trusted_blueprint_pin,
                    expected_domain_id=domain_id,
                    expected_environment=environment,
                    source_manifest=source_manifest,
                )
                blueprint_validation = {
                    "contract_version": "metadata.blueprint.validation.v1",
                    "blueprint_sha256": trusted_blueprint["blueprint_sha256"],
                    "executable_sha256": trusted_blueprint["executable_sha256"],
                    "annotation_proposal_sha256": sha256_json(annotations),
                    "external_pin": "passed",
                    "executable_immutable": "passed",
                }
            else:
                # The normal lane uses one full-domain proposal. Split initial
                # bootstrap uses three independently sealed fragments; both
                # converge on this same deterministic full-draft pipeline.
                raw_patch = deepcopy(prevalidated_domain_draft)
                draft_llm_calls = 3 if split_bootstrap else 1
        elif kind in {"dataset", "main_filter"}:
            if kind == "main_filter" and deterministic_alias_patch is not None:
                raw_patch = deepcopy(deterministic_alias_patch)
            else:
                raw_patch = deepcopy(invocation_draft)
                draft_llm_calls = 1
            normalization_manifest = source_manifest
            if kind == "dataset" and grounding_mode == "freeform_llm":
                normalization_manifest = _freeform_dataset_patch_authorization_manifest(
                    source_manifest,
                    base_draft,
                )
            if kind == "main_filter" and model_required:
                # The typed IR was already schema-bound to the approved target
                # vocabulary. Merge its full alias cards directly so legacy
                # shorthand normalization cannot reinterpret value-card shape.
                raw_patch = _merge_typed_main_filter_patch(base_draft, raw_patch)
            else:
                try:
                    raw_patch = normalize_authoring_section_patch_shorthand(
                        normalization_manifest,
                        raw_patch,
                        kind,
                        base_draft=base_draft,
                    )
                except AuthoringSourceManifestError as exc:
                    raise ContractError(
                        "metadata_dependency_error",
                        "metadata_alias_normalization",
                        "Compiled metadata contains an alias shorthand that is not bound by the source inventory.",
                        {**deepcopy(exc.evidence), "manifest_error_code": exc.code},
                    ) from exc
        else:
            # Domain policy is an operator-controlled patch.  Natural-language
            # messages and connected models cannot author prompt text,
            # registered functions or output policy.
            raw_patch = {}
        policy_input_values = {
            "intent": str(getattr(self, "intent_prompt_extension", "") or "").strip(),
            "answer": str(getattr(self, "answer_prompt_extension", "") or "").strip(),
            "specialized_functions": str(getattr(self, "specialized_functions_json", "") or "").strip(),
            "output_profile": str(getattr(self, "output_profile_json", "") or "").strip(),
        }
        if kind != "domain_policy" and any(policy_input_values.values()):
            raise ContractError(
                "metadata_schema_error",
                "metadata_policy_input",
                "Domain policy inputs may only be used when Authoring Kind is domain_policy.",
            )
        if kind == "domain_policy":
            if not any(policy_input_values.values()):
                raise ContractError(
                    "metadata_schema_error",
                    "metadata_policy_input",
                    "Domain policy prepare requires at least one explicit operator input.",
                )
            prompt_patch = raw_patch.get("prompt_extensions")
            if prompt_patch is None:
                prompt_patch = {}
            if not isinstance(prompt_patch, dict):
                raise ContractError(
                    "metadata_schema_error",
                    "metadata_policy_input",
                    "prompt_extensions must be an object.",
                )
            if policy_input_values["intent"]:
                prompt_patch["intent"] = policy_input_values["intent"]
            if policy_input_values["answer"]:
                prompt_patch["answer"] = policy_input_values["answer"]
            if prompt_patch:
                raw_patch["prompt_extensions"] = prompt_patch
            functions_value = _strict_json_value(
                policy_input_values["specialized_functions"],
                label="Specialized Functions JSON",
                expected_type=list,
            )
            if functions_value is not None:
                raw_patch["specialized_functions"] = functions_value
            output_value = _strict_json_value(
                policy_input_values["output_profile"],
                label="Output Profile JSON",
                expected_type=dict,
            )
            if output_value is not None:
                reserved_planner_keys = {
                    "planner_profile", "legacy_catalog_sha256"
                }
                if reserved_planner_keys.intersection(output_value):
                    raise ContractError(
                        "metadata_policy_error",
                        "metadata_policy_input",
                        "실행 planner 호환 정책은 승인 템플릿이 소유하며 출력 프로필 입력으로 변경할 수 없습니다.",
                    )
                raw_patch["output_profile"] = output_value
        if kind == "domain":
            if not annotation_only and prevalidated_domain_draft is None:
                raw_patch = _enforce_domain_policy_boundary(
                    raw_patch,
                    source_sha256=str(source_manifest.get("source_sha256") or ""),
                    proposal_sha256=str((authoring_proposal_validation or {}).get("proposal_sha256") or ""),
                    grounding_mode=grounding_mode,
                    approved_planner_policy=approved_planner_policy,
                )
            draft = validate_contract(
                raw_patch,
                "metadata-authoring-draft.schema.json",
                stage="metadata_section_patch",
                error_code="metadata_schema_error",
            )
            unchanged_sections = {}
        else:
            if not isinstance(base_draft, dict):
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_section_patch",
                    "Validated active authoring draft is unavailable.",
                )
            draft = apply_authoring_section_patch(base_draft, raw_patch, kind)
            owned = (
                {"datasets"}
                if kind == "dataset"
                else (
                    {"aliases", "entity_groups", "grains", "orderings", "predicates", "recipes"}
                    if kind == "main_filter"
                    else {"prompt_extensions", "specialized_functions", "output_profile"}
                )
            )
            unchanged_sections = {
                section: sha256_json(base_draft.get(section)) == sha256_json(draft.get(section))
                for section in base_draft
                if section not in owned and section not in {"source_provenance"}
            }
            if not all(unchanged_sections.values()):
                if client is not None:
                    client.close()
                raise ContractError("metadata_schema_error", "metadata_section_patch", "A section patch changed bytes outside its ownership.")

        source_binding_validation = prevalidated_source_binding or _validate_authoring_source_bindings(
            draft,
            source_sha256=str(source_manifest.get("source_sha256") or ""),
            proposal_sha256=str((authoring_proposal_validation or {}).get("proposal_sha256") or ""),
            approved_reference_context=getattr(self, "approved_reference_context", None),
            domain_id=domain_id,
        )

        if strict_inventory:
            try:
                coverage = validate_draft_inventory_coverage(
                    source_manifest,
                    draft,
                    supported_operations=AUTHORING_SUPPORTED_OPERATIONS,
                )
            except AuthoringSourceManifestError as exc:
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_source_coverage",
                    "Compiled metadata does not cover the explicit source inventory.",
                    deepcopy(exc.evidence),
                ) from exc
        else:
            proposal_grounding_sha256 = (
                bootstrap_raw_draft_sha256
                if split_bootstrap
                else str(
                    (authoring_proposal_validation or {}).get(
                        "expanded_draft_sha256"
                    )
                    or (authoring_proposal_validation or {}).get("draft_sha256")
                    or sha256_json(draft)
                )
            )
            coverage = {
                "contract_version": "source.grounding.evidence.v1",
                "mode": "freeform_llm",
                "source_sha256": str(source_manifest.get("source_sha256") or ""),
                # Bind grounding to the exact LLM proposal after deterministic
                # compact-IR expansion, not to unchanged sections inherited
                # from the active package.
                "structured_proposal_sha256": proposal_grounding_sha256,
                "explicit_inventory_coverage": "not_requested",
                "schema_validation": "passed",
                "dependency_closure": "passed",
                "human_approval_required": True,
            }

        active_revision = int((active_package or {}).get("revision") or 0)
        revision_policy = str(getattr(self, "revision_policy", "auto_next") or "auto_next")
        revision = active_revision + 1 if revision_policy == "auto_next" else int(getattr(self, "revision", 1))
        if revision <= active_revision:
            if client is not None:
                client.close()
            raise ContractError(
                "metadata_revision_conflict",
                "metadata_prepare",
                "Prepared revision must be greater than the active revision.",
                {"active_revision": active_revision, "requested_revision": revision},
            )
        package = compile_domain_package(draft, domain_id, environment, revision=revision, lifecycle_status="validated")
        package = validate_domain_package(package)
        validate_runtime_catalog_v2(package["runtime_catalog"])
        if strict_inventory:
            try:
                coverage = validate_draft_inventory_coverage(
                    source_manifest,
                    package["runtime_catalog"],
                    supported_operations=AUTHORING_SUPPORTED_OPERATIONS,
                )
            except AuthoringSourceManifestError as exc:
                raise ContractError(
                    "metadata_dependency_error",
                    "metadata_source_coverage",
                    "Compiled metadata does not cover the explicit source inventory.",
                    deepcopy(exc.evidence),
                ) from exc
        else:
            coverage = {
                **coverage,
                "compiled_catalog_sha256": str(package["runtime_catalog"].get("catalog_sha256") or ""),
            }
        coverage = {**coverage, "coverage_sha256": sha256_json(coverage)}
        bundle_document = make_bundle_document(package)
        active_pointer = make_active_pointer_document(package)
        expected_active = {
            "revision": active_revision,
            "bundle_sha256": str((active_package or {}).get("bundle_sha256") or ""),
            "package_sha256": str((active_package or {}).get("package_sha256") or ""),
        }
        # BSON persists datetimes at millisecond precision. Seal the payload
        # and TTL wrapper from the same exact instant before hashing.
        now = _bson_millisecond_utc(datetime.now(timezone.utc))
        expires = now + timedelta(seconds=max(300, min(int(getattr(self, "candidate_ttl_seconds", 86400)), 604800)))
        validation = {
            "schema": "passed",
            "semantic_lint": "passed",
            "dependency_closure": "passed",
            "hash_seal": "passed",
            "section_ownership": "passed",
            "source_coverage": coverage,
            "source_bindings": source_binding_validation,
        }
        observed_schema_bindings = deepcopy(
            getattr(self, "_observed_authoring_schema_bindings", None) or {}
        )
        if observed_schema_bindings:
            validation["llm_schema_bindings"] = {
                "contract_version": "metadata.llm-schema-bindings.v1",
                "bindings": [
                    observed_schema_bindings[purpose]
                    for purpose in sorted(observed_schema_bindings)
                ],
            }
        if split_bootstrap and authoring_proposal_validation is not None:
            authoring_proposal_validation = {
                **authoring_proposal_validation,
                "sealed_authoring_sha256": sha256_json(draft),
            }
        if authoring_proposal_validation is not None:
            validation["authoring_proposal"] = authoring_proposal_validation
        if authoring_proposals_validation is not None:
            validation["authoring_proposals"] = authoring_proposals_validation
        if metric_binding_completion is not None:
            validation["metric_binding_completion"] = metric_binding_completion
        if semantic_alias_normalization is not None:
            validation["semantic_alias_normalization"] = semantic_alias_normalization
        if domain_template_expansion is not None:
            validation["domain_template_expansion"] = domain_template_expansion
        if filter_operator_normalization is not None:
            validation[
                "filter_operator_normalization"
            ] = filter_operator_normalization
        if blueprint_validation is not None:
            validation["trusted_blueprint"] = blueprint_validation
        hash_material = {
            "contract_version": "pending.domain-package.hash-material.v1",
            "authoring_kind": kind,
            "domain_package": package,
            "bundle_document": bundle_document,
            "active_pointer": active_pointer,
            "expected_active": expected_active,
            "validation": validation,
            "prepared_at": now.isoformat(),
            "expires_at": expires.isoformat(),
        }
        candidate_hash = sha256_json(hash_material)
        candidate_id = f"candidate:{candidate_hash}"
        pending_payload = self._pending_payload(
            kind=kind,
            domain_id=domain_id,
            environment=environment,
            revision=package["revision"],
            expected_active=expected_active,
            candidate_id=candidate_id,
            candidate_hash=candidate_hash,
            hash_material=hash_material,
            now=now,
            expires=expires,
        )
        storage_document = {
            "_id": candidate_id,
            "pending_payload": deepcopy(pending_payload),
            "pending_payload_sha256": sha256_json(pending_payload),
            "workflow_status": "prepared",
            "expires_at": expires,
            "authoring_kind": kind,
            "domain_id": domain_id,
            "environment": environment,
        }
        if not dry_run:
            client, db = self._mongo()
            try:
                pending = db[collections["pending_collection"]]
                audit = db[collections["audit_collection"]]
                pending.create_index("expires_at", expireAfterSeconds=0)
                existing = pending.find_one({"_id": candidate_id})
                if existing:
                    existing_payload = self._pending_from_storage(
                        existing,
                        candidate_id=candidate_id,
                        candidate_hash=candidate_hash,
                    )
                    if sha256_json(existing_payload) != sha256_json(pending_payload):
                        raise ContractError("metadata_hash_conflict", "metadata_prepare", "Candidate ID already stores different pending bytes.")
                if not existing:
                    pending.insert_one(storage_document)
                    audit.insert_one(
                        {
                            "event_type": "prepared",
                            "candidate_id": candidate_id,
                            "candidate_sha256": candidate_hash,
                            "pending_payload_sha256": sha256_json(pending_payload),
                            "authoring_kind": kind,
                            "metadata_contract_mode": "domain_package_v2",
                            "domain_id": domain_id,
                            "environment": environment,
                            "package_sha256": package["package_sha256"],
                            "bundle_sha256": package["bundle_sha256"],
                            "occurred_at": now,
                        }
                    )
            finally:
                client.close()
        catalog = package["runtime_catalog"]
        return self._response(
            "ok",
            stage="prepared",
            candidate_id=candidate_id,
            candidate_sha256=candidate_hash,
            package_sha256=package["package_sha256"],
            bundle_sha256=package["bundle_sha256"],
            catalog_sha256=catalog["catalog_sha256"],
            revision=package["revision"],
            persisted=not dry_run,
            diff={
                "authoring_kind": kind,
                "datasets": len(catalog.get("datasets") or {}),
                "fields": len(catalog.get("fields") or {}),
                "metrics": len(catalog.get("metrics") or {}),
                "relations": len(catalog.get("relations") or {}),
                "recipes": len(catalog.get("recipes") or {}),
            },
            unchanged_section_checks=unchanged_sections,
            validation=validation,
            expires_at=expires.isoformat(),
            llm_usage={
                "draft_llm_calls": draft_llm_calls,
                "annotation_llm_calls": 1 if annotation_only else 0,
                "repair_llm_calls": 0,
            },
        )

    def _prepare_legacy(self):
        kind = str(getattr(self, "authoring_kind", "domain"))
        if kind not in AUTHORING_ALLOWED_KINDS:
            raise ContractError("metadata_schema_error", "metadata_prepare", "authoring_kind가 유효하지 않습니다.")
        source_text = str(getattr(getattr(self, "input_message", None), "text", getattr(self, "input_message", "")) or "").strip()
        if not source_text or len(source_text.encode("utf-8")) > 65536:
            raise ContractError("metadata_schema_error", "metadata_prepare", "metadata TXT는 1~65536 bytes여야 합니다.")
        model = getattr(self, "language_model", None)
        if model is None or not hasattr(model, "invoke"):
            raise ContractError("metadata_llm_unavailable", "metadata_draft", "prepare run에는 연결된 Language Model이 필요합니다.")
        draft = _json_object(_model_text(model.invoke(_authoring_prompt(kind, source_text))))
        compiled = _validated_projection(kind, draft, source_text)
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=max(300, min(int(getattr(self, "candidate_ttl_seconds", 86400)), 604800)))
        expected_active = {"revision": 0, "contract_sha256": ""}
        client = db = None
        dry_run = bool(getattr(self, "dry_run", False))
        if not dry_run:
            client, db = self._mongo()
            active = db[str(getattr(self, "active_collection", "agent_v6_metadata_active"))].find_one({"_id": f"active:{kind}"}) or {}
            expected_active = {"revision": int(active.get("revision") or 0), "contract_sha256": str(active.get("contract_sha256") or "")}
        hash_material = {
            "contract_version": "pending.metadata.hash-material.v1",
            "compiled_candidate": compiled,
            "expected_active": expected_active,
            "dependency_pins": {"runtime_catalog_sha256": EMBEDDED_RUNTIME_CATALOG.get("catalog_sha256")},
            "validation": {"schema": "passed", "semantic_lint": "passed", "dependency_closure": "passed"},
            "prepared_at": now.isoformat(),
            "expires_at": expires.isoformat(),
        }
        candidate_hash = sha256_json(hash_material)
        candidate_id = f"candidate:{candidate_hash}"
        envelope = {
            "_id": candidate_id,
            "candidate_id": candidate_id,
            "candidate_sha256": candidate_hash,
            "authoring_kind": kind,
            "status": "prepared",
            "hash_material": hash_material,
            "prepared_at": now,
            "expires_at": expires,
        }
        if not dry_run:
            pending = db[str(getattr(self, "pending_collection", "agent_v6_pending_writes"))]
            audit = db[str(getattr(self, "audit_collection", "agent_v6_authoring_audit"))]
            pending.create_index("expires_at", expireAfterSeconds=0)
            existing = pending.find_one({"_id": candidate_id})
            if existing and str(existing.get("candidate_sha256")) != candidate_hash:
                raise ContractError("metadata_hash_conflict", "metadata_prepare", "동일 candidate ID의 hash가 일치하지 않습니다.")
            if not existing:
                pending.insert_one(envelope)
                audit.insert_one({"event_type": "prepared", "candidate_id": candidate_id, "candidate_sha256": candidate_hash, "occurred_at": now})
            client.close()
        return self._response(
            "ok",
            stage="prepared",
            candidate_id=candidate_id,
            candidate_sha256=candidate_hash,
            persisted=not dry_run,
            diff={"record_keys": [f"{item['kind']}:{item['key']}" for item in compiled["records"]]},
            validation=hash_material["validation"],
            expires_at=expires.isoformat(),
            llm_usage={"draft_llm_calls": 1, "repair_llm_calls": 0},
        )

    def _prepare(self):
        contract_mode = str(getattr(self, "metadata_contract_mode", "domain_package_v2"))
        if contract_mode != "domain_package_v2":
            raise ContractError(
                "metadata_policy_error",
                "metadata_contract_mode",
                "Only domain_package_v2 authoring is executable; legacy projection is migration-tool only.",
            )
        return self._prepare_v2()

    def _execute_v2(self):
        collections = self._collection_names()
        event = validate_contract(
            _json_object(str(getattr(self, "approval_event_json", "") or "")),
            "approval-event.schema.json",
            stage="metadata_execute",
            error_code="approval_contract_error",
        )
        candidate_id = str(event["candidate_id"])
        candidate_hash = str(event["candidate_sha256"])
        idem = str(event["idempotency_key"])
        approval_event_sha256 = sha256_json(event)
        if event["decision"] != "approved":
            raise ContractError("approval_not_found", "metadata_execute", "An approved event is required.")
        try:
            decided_at = datetime.fromisoformat(str(event["decided_at"]).replace("Z", "+00:00"))
            approval_expiry = datetime.fromisoformat(str(event["expires_at"]).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ContractError("approval_contract_error", "metadata_execute", "Approval timestamps must be ISO-8601.") from exc
        now = datetime.now(timezone.utc)
        if decided_at > now + timedelta(minutes=5) or decided_at >= approval_expiry:
            raise ContractError("approval_contract_error", "metadata_execute", "Approval decision time is outside its valid window.")
        if approval_expiry <= now:
            raise ContractError("approval_expired", "metadata_execute", "Approval event has expired.")

        client, db = self._mongo()
        pending_collection = db[collections["pending_collection"]]
        active_collection = db[collections["active_collection"]]
        bundle_collection = db[collections["bundle_collection"]]
        audit = db[collections["audit_collection"]]
        sealed_document = pending_collection.find_one({"_id": candidate_id})
        self._pending_from_storage(
            sealed_document,
            candidate_id=candidate_id,
            candidate_hash=candidate_hash,
        )
        if (
            str(sealed_document.get("approval_event_id") or "") != str(event["event_id"])
            or str(sealed_document.get("approval_event_sha256") or "") != approval_event_sha256
        ):
            client.close()
            raise ContractError("approval_hash_mismatch", "metadata_execute", "Approval event does not match the externally sealed approval record.")
        already = audit.find_one({"event_type": "committed", "idempotency_key": idem})
        if already:
            if str(already.get("candidate_id") or "") != candidate_id or str(already.get("candidate_sha256") or "") != candidate_hash:
                client.close()
                raise ContractError("idempotency_conflict", "metadata_execute", "Idempotency key is already bound to another candidate.")
            if (
                str(already.get("approval_event_id") or "") != str(event["event_id"])
                or str(already.get("approval_event_sha256") or "") != approval_event_sha256
            ):
                client.close()
                raise ContractError("approval_hash_mismatch", "metadata_execute", "Idempotent replay approval event differs from the committed seal.")
            client.close()
            return self._response(
                "ok",
                stage="committed",
                candidate_id=candidate_id,
                candidate_sha256=candidate_hash,
                revision=int(already.get("revision") or 0),
                package_sha256=str(already.get("package_sha256") or ""),
                bundle_sha256=str(already.get("bundle_sha256") or ""),
                catalog_sha256=str(already.get("catalog_sha256") or ""),
                idempotent_replay=True,
                llm_usage={"draft_llm_calls": 0, "repair_llm_calls": 0},
            )

        with client.start_session() as session:
            with session.start_transaction():
                pending = pending_collection.find_one({"_id": candidate_id}, session=session)
                pending_payload = self._pending_from_storage(
                    pending,
                    candidate_id=candidate_id,
                    candidate_hash=candidate_hash,
                )
                hash_material = pending_payload["hash_material"]
                expiry = pending.get("expires_at")
                expiry_utc = _bson_millisecond_utc(expiry) if isinstance(expiry, datetime) else None
                if expiry_utc is None or expiry_utc <= now:
                    raise ContractError("approval_expired", "metadata_execute", "Pending candidate has expired.")
                if pending.get("workflow_status") != "approved":
                    code = "approval_already_claimed" if pending.get("workflow_status") in {"executing", "committed"} else "approval_not_found"
                    raise ContractError(code, "metadata_execute", "Pending candidate is not in approved state.")
                if (
                    str(pending.get("approval_event_id") or "") != str(event["event_id"])
                    or str(pending.get("approval_event_sha256") or "") != approval_event_sha256
                ):
                    raise ContractError("approval_hash_mismatch", "metadata_execute", "Approval event does not match the externally sealed approval record.")

                package = validate_domain_package(hash_material.get("domain_package") or {})
                expected = hash_material.get("expected_active") if isinstance(hash_material.get("expected_active"), dict) else {}
                payload_identity = {
                    "authoring_kind": str(hash_material.get("authoring_kind") or "domain"),
                    "domain_id": str(package.get("domain_id") or ""),
                    "environment": str(package.get("environment") or ""),
                    "target_revision": int(package.get("revision") or 0),
                    "base_revision": int(expected.get("revision") or 0) or None,
                    "base_bundle_sha256": str(expected.get("bundle_sha256") or "") or None,
                    "base_package_sha256": str(expected.get("package_sha256") or "") or None,
                }
                if any(pending_payload.get(key) != value for key, value in payload_identity.items()):
                    raise ContractError("approval_hash_mismatch", "metadata_execute", "Pending payload identity pins do not match the sealed domain package.")
                bundle_document = make_bundle_document(package)
                pointer_document = make_active_pointer_document(package)
                if sha256_json(bundle_document) != sha256_json(hash_material.get("bundle_document") or {}):
                    raise ContractError("approval_hash_mismatch", "metadata_execute", "Prepared immutable bundle changed after approval.")
                if sha256_json(pointer_document) != sha256_json(hash_material.get("active_pointer") or {}):
                    raise ContractError("approval_hash_mismatch", "metadata_execute", "Prepared active pointer changed after approval.")

                active_id = str(pointer_document["_id"])
                active = active_collection.find_one({"_id": active_id}, session=session) or {}
                actual_pin = {
                    "revision": int(active.get("revision") or 0),
                    "bundle_sha256": str(active.get("bundle_sha256") or ""),
                    "package_sha256": str(active.get("package_sha256") or ""),
                }
                expected_pin = {
                    "revision": int(expected.get("revision") or 0),
                    "bundle_sha256": str(expected.get("bundle_sha256") or ""),
                    "package_sha256": str(expected.get("package_sha256") or ""),
                }
                if actual_pin != expected_pin:
                    raise ContractError("stale_candidate", "metadata_execute", "The active domain pointer changed after prepare.")
                if int(package["revision"]) <= actual_pin["revision"]:
                    raise ContractError("metadata_revision_conflict", "metadata_execute", "Prepared revision is no longer newer than active.")

                claimed = pending_collection.update_one(
                    {"_id": candidate_id, "workflow_status": "approved", "pending_payload.candidate_sha256": candidate_hash},
                    {"$set": {"workflow_status": "executing", "claim": {"idempotency_key": idem, "claimed_at": now}}},
                    session=session,
                )
                if claimed.modified_count != 1:
                    raise ContractError("approval_already_claimed", "metadata_execute", "Candidate could not be claimed atomically.")

                existing_bundle = bundle_collection.find_one({"_id": bundle_document["_id"]}, session=session)
                if existing_bundle and sha256_json(existing_bundle) != sha256_json(bundle_document):
                    raise ContractError("metadata_hash_conflict", "metadata_execute", "Immutable bundle ID already contains different bytes.")
                if not existing_bundle:
                    bundle_collection.insert_one(deepcopy(bundle_document), session=session)
                active_collection.replace_one(
                    {"_id": active_id},
                    deepcopy(pointer_document),
                    upsert=True,
                    session=session,
                )
                audit.insert_one(
                    {
                        "event_type": "committed",
                        "candidate_id": candidate_id,
                        "candidate_sha256": candidate_hash,
                        "pending_payload_sha256": sha256_json(pending_payload),
                        "approval_event_id": event["event_id"],
                        "approval_event_sha256": approval_event_sha256,
                        "approval_subject_id": event["subject_id"],
                        "approval_decided_at": event["decided_at"],
                        "idempotency_key": idem,
                        "metadata_contract_mode": "domain_package_v2",
                        "domain_id": package["domain_id"],
                        "environment": package["environment"],
                        "revision": package["revision"],
                        "package_sha256": package["package_sha256"],
                        "bundle_sha256": package["bundle_sha256"],
                        "catalog_sha256": package["runtime_catalog"]["catalog_sha256"],
                        "occurred_at": now,
                    },
                    session=session,
                )
                pending_collection.update_one(
                    {"_id": candidate_id, "workflow_status": "executing"},
                    {"$set": {"workflow_status": "committed", "commit": {"revision": package["revision"], "revision_ref": bundle_document["_id"], "committed_at": now}}},
                    session=session,
                )
        client.close()
        return self._response(
            "ok",
            stage="committed",
            candidate_id=candidate_id,
            candidate_sha256=candidate_hash,
            revision=package["revision"],
            package_sha256=package["package_sha256"],
            bundle_sha256=package["bundle_sha256"],
            catalog_sha256=package["runtime_catalog"]["catalog_sha256"],
            idempotent_replay=False,
            llm_usage={"draft_llm_calls": 0, "repair_llm_calls": 0},
        )

    def _execute_legacy(self):
        candidate_id = str(getattr(self, "candidate_id", "") or "").strip()
        candidate_hash = str(getattr(self, "candidate_sha256", "") or "").strip()
        idem = str(getattr(self, "idempotency_key", "") or "").strip()
        event = _json_object(str(getattr(self, "approval_event_json", "") or ""))
        required = {"event_id", "candidate_id", "candidate_sha256", "decision", "approver_id", "approver_roles", "approved_at", "expires_at"}
        if set(event) != required or not candidate_id or not candidate_hash or not idem:
            raise ContractError("approval_contract_error", "metadata_execute", "execute input contract가 완전하지 않습니다.")
        if event["candidate_id"] != candidate_id or event["candidate_sha256"] != candidate_hash:
            raise ContractError("approval_hash_mismatch", "metadata_execute", "approval event hash가 candidate와 일치하지 않습니다.")
        if event["decision"] != "approved":
            raise ContractError("approval_not_found", "metadata_execute", "승인된 event가 아닙니다.")
        role = str(getattr(self, "approval_required_role", "metadata_approver"))
        if not isinstance(event["approver_roles"], list) or role not in event["approver_roles"]:
            raise ContractError("approval_acl_denied", "metadata_execute", "승인자 역할이 부족합니다.")
        try:
            approval_expiry = datetime.fromisoformat(str(event["expires_at"]).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ContractError("approval_contract_error", "metadata_execute", "approval expiry가 ISO-8601이 아닙니다.") from exc
        if approval_expiry <= datetime.now(timezone.utc):
            raise ContractError("approval_expired", "metadata_execute", "approval event가 만료되었습니다.")
        client, db = self._mongo()
        pending_collection = db[str(getattr(self, "pending_collection", "agent_v6_pending_writes"))]
        revisions = db[str(getattr(self, "revision_collection", "agent_v6_metadata_revisions"))]
        active_collection = db[str(getattr(self, "active_collection", "agent_v6_metadata_active"))]
        audit = db[str(getattr(self, "audit_collection", "agent_v6_authoring_audit"))]
        already = audit.find_one({"event_type": "committed", "idempotency_key": idem})
        if already:
            if str(already.get("candidate_id") or "") != candidate_id or str(already.get("candidate_sha256") or "") != candidate_hash:
                client.close()
                raise ContractError("idempotency_conflict", "metadata_execute", "Idempotency key is already bound to another candidate.")
            client.close()
            return self._response(
                "ok",
                stage="committed",
                candidate_id=candidate_id,
                candidate_sha256=candidate_hash,
                idempotent_replay=True,
                revision=int(already.get("revision") or 0),
                package_sha256=str(already.get("package_sha256") or ""),
                bundle_sha256=str(already.get("bundle_sha256") or ""),
                catalog_sha256=str(already.get("catalog_sha256") or ""),
                llm_usage={"draft_llm_calls": 0, "repair_llm_calls": 0},
            )
        now = datetime.now(timezone.utc)
        committed_values = {}
        with client.start_session() as session:
            with session.start_transaction():
                pending = pending_collection.find_one({"_id": candidate_id}, session=session)
                if not pending:
                    raise ContractError("approval_not_found", "metadata_execute", "pending candidate가 없습니다.")
                if str(pending.get("candidate_sha256")) != candidate_hash or sha256_json(pending.get("hash_material")) != candidate_hash:
                    raise ContractError("approval_hash_mismatch", "metadata_execute", "pending candidate bytes/hash가 일치하지 않습니다.")
                expiry = pending.get("expires_at")
                expiry_utc = _bson_millisecond_utc(expiry) if isinstance(expiry, datetime) else None
                if expiry_utc is not None and expiry_utc <= now:
                    raise ContractError("approval_expired", "metadata_execute", "pending candidate가 만료되었습니다.")
                if pending.get("status") != "approved":
                    code = "approval_already_claimed" if pending.get("status") in {"executing", "committed"} else "approval_not_found"
                    raise ContractError(code, "metadata_execute", "pending candidate status가 approved가 아닙니다.")
                kind = str(pending.get("authoring_kind") or "")
                active = active_collection.find_one({"_id": f"active:{kind}"}, session=session) or {}
                expected = pending["hash_material"].get("expected_active", {})
                if int(active.get("revision") or 0) != int(expected.get("revision") or 0) or str(active.get("contract_sha256") or "") != str(expected.get("contract_sha256") or ""):
                    pending_collection.update_one({"_id": candidate_id}, {"$set": {"status": "stale"}}, session=session)
                    raise ContractError("stale_candidate", "metadata_execute", "active metadata pin이 prepare 이후 변경됐습니다.")
                revision = int(active.get("revision") or 0) + 1
                claimed = pending_collection.update_one(
                    {"_id": candidate_id, "status": "approved", "candidate_sha256": candidate_hash},
                    {"$set": {"status": "executing", "claim": {"idempotency_key": idem, "claimed_at": now}}},
                    session=session,
                )
                if claimed.modified_count != 1:
                    raise ContractError("approval_already_claimed", "metadata_execute", "candidate를 atomic claim하지 못했습니다.")
                revision_id = f"revision:{kind}:{revision}:{candidate_hash[:16]}"
                revision_record = {
                    "_id": revision_id,
                    "authoring_kind": kind,
                    "revision": revision,
                    "contract_sha256": candidate_hash,
                    "compiled_candidate": deepcopy(pending["hash_material"]["compiled_candidate"]),
                    "lifecycle": {"status": "active"},
                    "committed_at": now,
                }
                revisions.insert_one(revision_record, session=session)
                active_collection.replace_one(
                    {"_id": f"active:{kind}"},
                    {"_id": f"active:{kind}", "revision": revision, "contract_sha256": candidate_hash, "revision_ref": revision_id, "commit_marker": "committed", "updated_at": now},
                    upsert=True,
                    session=session,
                )
                audit.insert_one({"event_type": "committed", "candidate_id": candidate_id, "candidate_sha256": candidate_hash, "approval_event_id": event["event_id"], "approver_id": event["approver_id"], "idempotency_key": idem, "revision": revision, "occurred_at": now}, session=session)
                pending_collection.update_one({"_id": candidate_id, "status": "executing"}, {"$set": {"status": "committed", "commit": {"revision": revision, "revision_ref": revision_id, "committed_at": now}}}, session=session)
        client.close()
        return self._response("ok", stage="committed", candidate_id=candidate_id, candidate_sha256=candidate_hash, revision=revision, idempotent_replay=False, llm_usage={"draft_llm_calls": 0, "repair_llm_calls": 0})

    def _execute(self):
        contract_mode = str(getattr(self, "metadata_contract_mode", "domain_package_v2"))
        if contract_mode != "domain_package_v2":
            raise ContractError(
                "metadata_policy_error",
                "metadata_contract_mode",
                "Only domain_package_v2 authoring is executable; legacy projection is migration-tool only.",
            )
        return self._execute_v2()

    def run_authoring(self) -> Data:
        self._observed_authoring_llm_usage = {
            "draft_llm_calls": 0,
            "annotation_llm_calls": 0,
            "repair_llm_calls": 0,
        }
        self._observed_authoring_schema_bindings = {}
        try:
            if str(getattr(self, "metadata_contract_mode", "domain_package_v2")) != "domain_package_v2":
                raise ContractError(
                    "metadata_policy_error",
                    "metadata_contract_mode",
                    "Only domain_package_v2 authoring is executable; legacy projection is migration-tool only.",
                )
            self._collection_names()
            validate_runtime_catalog(EMBEDDED_RUNTIME_CATALOG)
            if str(getattr(self, "mode", "prepare")) == "execute":
                return self._execute()
            return self._prepare()
        except ContractError as exc:
            usage = deepcopy(getattr(self, "_observed_authoring_llm_usage", None) or {})
            usage.setdefault("draft_llm_calls", 0)
            usage.setdefault("annotation_llm_calls", 0)
            usage["repair_llm_calls"] = 0
            if exc.code == "metadata_clarification_required" and isinstance(exc.details, dict):
                safe_questions, safe_missing_fields = _worker_safe_clarification(
                    list(exc.details.get("questions") or [])[:3],
                    list(exc.details.get("missing_fields") or [])[:32],
                )
                clarification = {
                    "contract_version": "metadata.authoring.clarification.v1",
                    "questions": safe_questions,
                    "missing_fields": safe_missing_fields,
                    "source_sha256": str(exc.details.get("source_sha256") or ""),
                    "proposal_sha256": str(exc.details.get("proposal_sha256") or ""),
                }
                return self._response(
                    "needs_clarification",
                    stage="metadata_clarification",
                    clarification=clarification,
                    llm_usage=usage,
                )
            return self._response("error", stage=exc.stage, error=exc.as_dict(), llm_usage=usage)
        except Exception as exc:
            error = ContractError(
                "metadata_authoring_failed",
                "metadata_runtime",
                "metadata authoring 실행 중 계약 오류가 발생했습니다.",
                {
                    "error_type": type(exc).__name__,
                    "error_location": _safe_exception_location(exc),
                },
            )
            usage = deepcopy(getattr(self, "_observed_authoring_llm_usage", None) or {})
            usage.setdefault("draft_llm_calls", 0)
            usage.setdefault("annotation_llm_calls", 0)
            usage["repair_llm_calls"] = 0
            return self._response("error", stage=error.stage, error=error.as_dict(), llm_usage=usage)
'''


AUTHORING_MESSAGE_COMPONENT = r'''
from copy import deepcopy

from lfx.custom.custom_component.component import Component
from lfx.io import DataInput, Output
from lfx.schema.message import Message


class AuthoringMessagePresentation(Component):
    display_name = "메타데이터 등록 메시지 구성"
    description = "준비·승인 실행·추가 확인 결과를 짧은 한글 메시지로 표시하고 canonical response를 data에 보존합니다."
    icon = "file-check-2"

    inputs = [DataInput(name="response", display_name="메타데이터 등록 응답", required=True, info="준비 완료, 승인 실행 완료, 추가 확인 필요, 오류 중 하나의 표준 등록 응답입니다.")]
    outputs = [Output(name="message", display_name="등록 결과 채팅 메시지", method="build_message", types=["Message"])]

    def build_message(self) -> Message:
        raw = getattr(getattr(self, "response", None), "data", getattr(self, "response", None))
        response = deepcopy(validate_authoring_response_hash(raw)) if isinstance(raw, dict) else {}
        if response.get("status") == "ok" and response.get("stage") == "prepared":
            text = "### Metadata prepare 완료\n\n" + f"- Candidate: `{response.get('candidate_id', '')}`\n- Hash: `{response.get('candidate_sha256', '')}`\n- Expires: {response.get('expires_at', '')}"
        elif response.get("status") == "ok":
            text = "### Metadata execute 완료\n\n" + f"- Candidate: `{response.get('candidate_id', '')}`\n- Revision: {response.get('revision', '')}"
        elif response.get("status") == "needs_clarification":
            clarification = response.get("clarification") if isinstance(response.get("clarification"), dict) else {}
            questions = [str(item) for item in (clarification.get("questions") or [])[:3]]
            text = "### 메타데이터 등록 전 확인이 필요합니다\n\n" + "\n".join(
                f"{index}. {question}" for index, question in enumerate(questions, 1)
            )
        else:
            error = response.get("error") if isinstance(response.get("error"), dict) else {}
            text = "### Metadata authoring 실패\n\n" + f"- Code: `{error.get('code', 'metadata_authoring_failed')}`\n- Message: {error.get('message', '')}"
        message = Message(
            text=text,
            sender="Machine",
            sender_name="Metadata Authoring",
            session_metadata={
                "contract_version": "metadata.authoring.message-link.v1",
                "response_sha256": str(response.get("response_sha256") or ""),
            },
        )
        message.data = {"response": response}
        return message
'''


def _core_source(
    catalog: dict[str, Any], schemas: dict[str, dict[str, Any]], manifest: dict[str, Any]
) -> str:
    blocks = [_header(manifest, "TrustedAnalysisEngine")]
    for name in CORE_MODULES:
        path = REFERENCE_ROOT / name
        metadata_compiler = name == "metadata_compiler.py"
        blocks.append(
            _clean_module(
                path,
                drop_functions={"validate_authoring_sources", "source_provenance", "load_runtime_catalog", "write_runtime_catalog"}
                if metadata_compiler
                else set(),
                patch_catalog_loader=name in {"metadata_compiler.py", "plan_compiler.py"},
                patch_default_catalog=name == "dummy_data.py",
                patch_analysis_engine=name == "engine.py",
                patch_schema_loader=name == "contracts.py",
                drop_assignments={"ROOT", "SCHEMA_ROOT"}
                if name == "contracts.py"
                else (
                    {"ROOT", "DEFAULT_CATALOG"}
                    if name == "plan_compiler.py"
                    else ({"MANUFACTURING_PACK_CATALOG"} if metadata_compiler else set())
                ),
            )
        )
    # Catalog is defined after the flattened functions; callers only resolve it
    # when invoked, after module initialization has completed.
    blocks.extend(
        [_catalog_literal(catalog), _schemas_literal(schemas), EMBEDDED_SOURCE_ADAPTER, TRUSTED_ANALYSIS_COMPONENT]
    )
    return "\n\n".join(blocks).strip() + "\n"


def _analysis_phase_source(
    component_name: str,
    modules: tuple[str, ...],
    body: str,
    *,
    catalog: dict[str, Any] | None,
    schemas: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
    schema_names: tuple[str, ...] = (),
    extra_blocks: tuple[str, ...] = (),
) -> str:
    """Flatten only the runtime modules needed by one standalone phase."""

    blocks = [_header(manifest, component_name)]
    for name in modules:
        metadata_compiler = name == "metadata_compiler.py"
        dropped_functions = (
            {"validate_authoring_sources", "source_provenance", "load_runtime_catalog", "write_runtime_catalog"}
            if metadata_compiler
            else (
                {"load_domain_package_file"}
                if name == "domain_packages.py"
                else (
                    {"build_intent_prompt", "_model_text", "_parse_selection", "resolve_intent"}
                    if name == "plan_compiler.py"
                    else (
                        {"build_generic_v2_intent_prompt", "resolve_generic_v2_intent", "_parse_selection"}
                        if name == "generic_v2_candidates.py"
                        else set()
                    )
                )
            )
        )
        cleaned = _clean_module(
            REFERENCE_ROOT / name,
            drop_functions=dropped_functions,
            patch_catalog_loader=name in {"metadata_compiler.py", "plan_compiler.py"},
            patch_default_catalog=name == "dummy_data.py",
            patch_schema_loader=name == "contracts.py",
            drop_assignments={"ROOT", "SCHEMA_ROOT"}
            if name == "contracts.py"
            else (
                {"ROOT", "DEFAULT_CATALOG"}
                if name == "plan_compiler.py"
                else ({"MANUFACTURING_PACK_CATALOG"} if metadata_compiler else set())
            ),
        )
        if name == "generic_v2_candidates.py":
            cleaned = _namespace_flattened_module(
                cleaned,
                "_v2c",
                {
                    "build_generic_v2_candidate_bundle",
                    "validate_generic_v2_candidate_bundle",
                    "normalize_generic_v2_intent",
                },
            )
        elif name == "registered_functions.py":
            cleaned = _namespace_flattened_module(
                cleaned,
                "_v6rf",
                {
                    "FAILURE_POLICY",
                    "REGISTERED_CALL_VERSION",
                    "build_registered_call_operation",
                    "dispatch_registered_call",
                    "registered_function_descriptor",
                    "validate_registered_call_operation",
                    "validate_registered_function_card",
                },
            )
        elif name == "generic_v2_planner.py":
            cleaned = _namespace_flattened_module(
                cleaned,
                "_v2p",
                {"compile_generic_v2_plan", "validate_generic_v2_plan"},
            )
        blocks.append(cleaned)
    if catalog is not None:
        blocks.append(_catalog_literal(catalog))
    if "contracts.py" in modules:
        selected = {name: schemas[name] for name in schema_names if name in schemas}
        if not selected:
            raise GenerationError(f"{component_name}: at least one embedded schema is required")
        blocks.append(_schemas_literal(selected))
    blocks.append(PIPELINE_HELPERS)
    blocks.extend(extra_blocks)
    blocks.append(body)
    return "\n\n".join(blocks).strip() + "\n"


def _presenter_source(
    schemas: dict[str, dict[str, Any]], manifest: dict[str, Any], *, gaia: bool = False
) -> str:
    blocks = [_header(manifest, "GaiAOutput" if gaia else "MessagePresentation")]
    for name in ("canonical.py", "contracts.py", "presenter.py"):
        blocks.append(
            _clean_module(
                REFERENCE_ROOT / name,
                drop_assignments={"ROOT", "SCHEMA_ROOT"} if name == "contracts.py" else set(),
                patch_schema_loader=name == "contracts.py",
            )
        )
    blocks.append(_schemas_literal(schemas))
    blocks.append(GAIA_OUTPUT_COMPONENT if gaia else MESSAGE_PRESENTATION_COMPONENT)
    return "\n\n".join(blocks).strip() + "\n"


def _authoring_prompt_context_source(
    catalog: dict[str, Any], schemas: dict[str, dict[str, Any]], manifest: dict[str, Any]
) -> str:
    blocks = [
        _header(manifest, "AuthoringPromptContextBuilder"),
        _clean_module(REFERENCE_ROOT / "canonical.py"),
        _clean_module(
            REFERENCE_ROOT / "contracts.py",
            drop_assignments={"ROOT", "SCHEMA_ROOT"},
            patch_schema_loader=True,
        ),
        _clean_module(
            REFERENCE_ROOT / "metadata_compiler.py",
            drop_functions={"validate_authoring_sources", "source_provenance", "load_runtime_catalog", "write_runtime_catalog"},
            patch_catalog_loader=True,
            drop_assignments={"MANUFACTURING_PACK_CATALOG"},
        ),
        _clean_module(
            REFERENCE_ROOT / "domain_packages.py",
            drop_functions={"load_domain_package_file"},
        ),
        _namespace_flattened_module(
            _clean_module(REFERENCE_ROOT / "authoring_source_manifest.py"),
            "_v6m",
            {
                "AuthoringSourceManifestError",
                "extract_authoring_source_manifest",
                "validate_authoring_source_manifest",
                "validate_draft_inventory_coverage",
            },
        ),
        _namespace_flattened_module(
            _clean_module(REFERENCE_ROOT / "authoring_blueprint.py"),
            "_v6b",
            {"validate_executable_blueprint"},
        ),
        _catalog_literal(catalog),
        _schemas_literal(schemas),
        SEMANTIC_VOCABULARY_HELPERS,
        AUTHORING_PROMPT_CONTEXT_COMPONENT,
    ]
    return "\n\n".join(blocks).strip() + "\n"


def _authoring_source(
    catalog: dict[str, Any], schemas: dict[str, dict[str, Any]], manifest: dict[str, Any]
) -> str:
    compiler_path = REFERENCE_ROOT / "metadata_compiler.py"
    blocks = [_header(manifest, "MetadataAuthoringEngine"), _clean_module(REFERENCE_ROOT / "canonical.py")]
    blocks.append(
        _clean_module(
            REFERENCE_ROOT / "contracts.py",
            drop_assignments={"ROOT", "SCHEMA_ROOT"},
            patch_schema_loader=True,
        )
    )
    blocks.append(
        _clean_module(
            compiler_path,
            drop_functions={"validate_authoring_sources", "source_provenance", "load_runtime_catalog", "write_runtime_catalog"},
            patch_catalog_loader=True,
            drop_assignments={"MANUFACTURING_PACK_CATALOG"},
        )
    )
    blocks.append(
        _clean_module(
            REFERENCE_ROOT / "domain_packages.py",
            drop_functions={"load_domain_package_file"},
        )
    )
    blocks.append(
        _namespace_flattened_module(
            _clean_module(REFERENCE_ROOT / "authoring_source_manifest.py"),
            "_v6m",
            {
                "AuthoringSourceManifestError",
                "extract_authoring_source_manifest",
                "normalize_authoring_draft_shorthand",
                "normalize_authoring_section_patch_shorthand",
                "normalize_draft_alias_shorthand",
                "validate_authoring_source_manifest",
                "validate_draft_inventory_coverage",
            },
        )
    )
    blocks.append(
        _namespace_flattened_module(
            _clean_module(REFERENCE_ROOT / "authoring_blueprint.py"),
            "_v6b",
            {
                "apply_domain_blueprint_annotations",
                "compute_blueprint_sha256",
                "merge_blueprint_annotations",
                "validate_executable_blueprint",
            },
        )
    )
    blocks.append(_clean_module(REFERENCE_ROOT / "presenter.py"))
    blocks.append(
        _namespace_flattened_module(
            _clean_module(REFERENCE_ROOT / "domain_authoring_patches.py"),
            "_v2a",
            {"runtime_catalog_v2_to_authoring_draft", "apply_authoring_section_patch"},
        )
    )
    blocks.append(SEMANTIC_VOCABULARY_HELPERS)
    component_body = AUTHORING_COMPONENT
    temporary_start = component_body.find('SOURCE_INVENTORY_VALIDATOR_VERSION = "source-inventory-coverage.v1"')
    temporary_end = component_body.find("def _authoring_prompt", temporary_start)
    if temporary_start >= 0 and temporary_end > temporary_start:
        # Runtime uses the canonical flattened authoring_source_manifest.py.
        # Remove the earlier in-builder draft helper so generated standalone
        # components contain exactly one inventory parser and validator.
        component_body = component_body[:temporary_start] + component_body[temporary_end:]

    # v6 authoring is deliberately domain-package-v2 only.  The original
    # implementation kept unreachable v1 projection helpers inside the raw
    # builder literal while the v2 migration settled.  Do not ship those old
    # storage/approval paths in a standalone component: besides wasting node
    # payload, their obsolete input and Mongo document shapes are unsafe audit
    # surface even when routing cannot currently reach them.
    def _drop_between(source: str, start_marker: str, end_marker: str) -> str:
        start = source.find(start_marker)
        end = source.find(end_marker, start + len(start_marker)) if start >= 0 else -1
        if start < 0 or end <= start:
            raise GenerationError(
                f"v2-only authoring cleanup markers are missing: {start_marker!r} -> {end_marker!r}"
            )
        return source[:start] + source[end:]

    component_body = _drop_between(
        component_body,
        "AUTHORING_ALLOWED_KINDS =",
        "V6_AUTHORING_COLLECTIONS =",
    )
    component_body = _drop_between(
        component_body,
        "def _authoring_prompt(",
        "def _v2_section_patch_schema(",
    )
    component_body = _drop_between(
        component_body,
        "def _v2_section_patch_schema(",
        "def _v2_alias_only_manifest_patch(",
    )
    component_body = _drop_between(
        component_body,
        "def _v2_authoring_prompt(",
        "def _validated_projection(",
    )
    component_body = _drop_between(
        component_body,
        "def _validated_projection(",
        "def _bson_millisecond_utc(",
    )
    component_body = _drop_between(
        component_body,
        "def _model_text(",
        "MAX_AUTHORING_MODEL_RESPONSE_BYTES =",
    )
    component_body = _drop_between(
        component_body,
        "def _invoke_authoring_json(",
        "def _strict_json_value(",
    )
    for obsolete_method, next_method in (
        ("_prepare_v2_full_compat", "_prepare_v2"),
        ("_prepare_legacy", "_prepare"),
        ("_execute_legacy", "_execute"),
    ):
        component_body = _drop_between(
            component_body,
            f"    def {obsolete_method}(",
            f"    def {next_method}(",
        )
    blocks.extend([_catalog_literal(catalog), _schemas_literal(schemas), component_body])
    return "\n\n".join(blocks).strip() + "\n"


def _authoring_message_source(
    schemas: dict[str, dict[str, Any]], manifest: dict[str, Any]
) -> str:
    selected = {
        "metadata-authoring-response.schema.json": schemas["metadata-authoring-response.schema.json"]
    }
    blocks = [_header(manifest, "AuthoringMessagePresentation")]
    for name in ("canonical.py", "contracts.py", "presenter.py"):
        blocks.append(
            _clean_module(
                REFERENCE_ROOT / name,
                drop_assignments={"ROOT", "SCHEMA_ROOT"} if name == "contracts.py" else set(),
                patch_schema_loader=name == "contracts.py",
            )
        )
    blocks.extend([_schemas_literal(selected), AUTHORING_MESSAGE_COMPONENT])
    return "\n\n".join(blocks).strip() + "\n"


def _assert_safe_generated(path: Path, source: str) -> None:
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise GenerationError(f"generated source does not parse: {path}: {exc}") from exc
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for statement in node.body:
            if not isinstance(statement, ast.Assign) or not any(
                isinstance(target, ast.Name) and target.id == "inputs" for target in statement.targets
            ):
                continue
            if not isinstance(statement.value, (ast.List, ast.Tuple)):
                continue
            names: list[str] = []
            for item in statement.value.elts:
                if not isinstance(item, ast.Call):
                    continue
                keyword = next((value for value in item.keywords if value.arg == "name"), None)
                if keyword and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                    names.append(keyword.value.value)
            duplicates = sorted({name for name in names if names.count(name) > 1})
            if duplicates:
                raise GenerationError(f"generated component has duplicate input names {duplicates}: {path}")
    compact = source.replace(" ", "")
    banned = ("from.", "exec(", "eval(", "Path(__file__)", ".read_text(", ".read_bytes(", ".write_text(", ".write_bytes(")
    found = [token for token in banned if token in compact]
    if found:
        raise GenerationError(f"generated source contains forbidden runtime construct {found}: {path}")


def build_components(*, check: bool = False) -> list[Path]:
    catalog = _read_json(CATALOG_PATH, "compiled runtime catalog")
    required_catalog_keys = {"contract_version", "datasets", "fields", "metrics", "catalog_sha256"}
    if not required_catalog_keys.issubset(catalog):
        raise GenerationError(f"compiled runtime catalog is incomplete; missing {sorted(required_catalog_keys - set(catalog))}")
    schema_paths = sorted(SCHEMA_ROOT.glob("*.schema.json"), key=lambda item: item.name)
    if not schema_paths:
        raise GenerationError(f"generated contract schemas are missing: {SCHEMA_ROOT}")
    schemas = {path.name: _read_json(path, f"contract schema {path.name}") for path in schema_paths}
    paths = [
        REFERENCE_ROOT / name
        for name in (
            *CORE_MODULES,
            "domain_packages.py",
            "domain_authoring_patches.py",
            "authoring_source_manifest.py",
            "authoring_blueprint.py",
            "generic_v2_candidates.py",
            "registered_functions.py",
            "generic_v2_planner.py",
        )
    ] + schema_paths
    for path in paths:
        if not path.is_file():
            raise GenerationError(f"required reference source is missing: {path}")
    manifest = _manifest(paths, catalog)
    sources = {
        OUTPUT_ROOT / "data_analysis" / "request_state_capsule.py": _analysis_phase_source(
            "RequestStateCapsule",
            ("canonical.py", "contracts.py", "request_literals.py", "state_contracts.py"),
            REQUEST_STATE_COMPONENT,
            catalog=None,
            schemas=schemas,
            manifest=manifest,
            schema_names=("request-capsule.schema.json", "executed-result.schema.json", "analysis-result.schema.json"),
        ),
        OUTPUT_ROOT / "data_analysis" / "domain_bundle_loader.py": _analysis_phase_source(
            "DomainBundleLoader",
            ("canonical.py", "contracts.py", "domain_packages.py"),
            DOMAIN_BUNDLE_COMPONENT,
            catalog=catalog,
            schemas=schemas,
            manifest=manifest,
            schema_names=("runtime-catalog-v2.schema.json", "domain-package.schema.json", "active-domain-pointer.schema.json"),
        ),
        OUTPUT_ROOT / "data_analysis" / "candidate_route_gate.py": _analysis_phase_source(
            "CandidateRouteGate",
            ("canonical.py", "contracts.py", "request_literals.py", "plan_compiler.py", "registered_functions.py", "generic_v2_candidates.py"),
            CANDIDATE_ROUTE_COMPONENT,
            catalog=catalog,
            schemas=schemas,
            manifest=manifest,
            schema_names=("analysis-route.schema.json", "resolved-candidate-bundle.schema.json"),
        ),
        OUTPUT_ROOT / "data_analysis" / "intent_prompt_context_builder.py": _analysis_phase_source(
            "IntentPromptContextBuilder",
            ("canonical.py",),
            INTENT_PROMPT_CONTEXT_COMPONENT,
            catalog=None,
            schemas=schemas,
            manifest=manifest,
        ),
        OUTPUT_ROOT / "data_analysis" / "common_intent_resolver.py": _analysis_phase_source(
            "CommonIntentResolver",
            ("canonical.py", "contracts.py", "request_literals.py", "plan_compiler.py", "registered_functions.py", "generic_v2_candidates.py"),
            INTENT_RESOLVER_COMPONENT,
            catalog=catalog,
            schemas=schemas,
            manifest=manifest,
            schema_names=("semantic-intent.schema.json",),
        ),
        OUTPUT_ROOT / "data_analysis" / "plan_compiler_validator.py": _analysis_phase_source(
            "PlanCompilerValidator",
            (
                "canonical.py",
                "contracts.py",
                "request_literals.py",
                "plan_compiler.py",
                "generic_v2_candidates.py",
                "registered_functions.py",
                "generic_v2_planner.py",
            ),
            PLAN_COMPILER_COMPONENT,
            catalog=catalog,
            schemas=schemas,
            manifest=manifest,
            schema_names=("analysis-plan.schema.json",),
        ),
        OUTPUT_ROOT / "data_analysis" / "retrieval_job_router.py": _analysis_phase_source(
            "RetrievalJobRouter",
            ("canonical.py",),
            JOB_ROUTER_COMPONENT,
            catalog=None,
            schemas=schemas,
            manifest=manifest,
        ),
        OUTPUT_ROOT / "data_analysis" / "dummy_source_retriever.py": _analysis_phase_source(
            "DummySourceRetriever",
            ("canonical.py", "metadata_compiler.py", "source_contracts.py", "dummy_data.py"),
            DUMMY_RETRIEVER_COMPONENT,
            catalog=catalog,
            schemas=schemas,
            manifest=manifest,
        ),
        OUTPUT_ROOT / "data_analysis" / "inline_source_retriever.py": _analysis_phase_source(
            "InlineSourceRetriever",
            ("canonical.py", "contracts.py", "metadata_compiler.py", "domain_packages.py", "source_contracts.py"),
            INLINE_RETRIEVER_COMPONENT,
            catalog=catalog,
            schemas=schemas,
            manifest=manifest,
            schema_names=("runtime-catalog-v2.schema.json", "domain-package.schema.json", "active-domain-pointer.schema.json"),
            extra_blocks=(CATALOG_VALIDATOR_DISPATCH, BOUNDED_RETRIEVER_HELPER),
        ),
        OUTPUT_ROOT / "data_analysis" / "live_source_retriever.py": _analysis_phase_source(
            "LiveSourceRetriever",
            ("canonical.py", "contracts.py", "metadata_compiler.py", "domain_packages.py", "source_contracts.py"),
            LIVE_RETRIEVER_COMPONENT,
            catalog=catalog,
            schemas=schemas,
            manifest=manifest,
            schema_names=("runtime-catalog-v2.schema.json", "domain-package.schema.json", "active-domain-pointer.schema.json"),
            extra_blocks=(CATALOG_VALIDATOR_DISPATCH, BOUNDED_RETRIEVER_HELPER),
        ),
        OUTPUT_ROOT / "data_analysis" / "source_contract_merger.py": _analysis_phase_source(
            "SourceContractMerger",
            ("canonical.py", "contracts.py", "metadata_compiler.py", "domain_packages.py", "source_contracts.py"),
            SOURCE_MERGER_COMPONENT,
            catalog=catalog,
            schemas=schemas,
            manifest=manifest,
            schema_names=("runtime-catalog-v2.schema.json", "domain-package.schema.json", "active-domain-pointer.schema.json"),
            extra_blocks=(CATALOG_VALIDATOR_DISPATCH,),
        ),
        OUTPUT_ROOT / "data_analysis" / "typed_executor_publisher.py": _analysis_phase_source(
            "TypedExecutorPublisher",
            ("canonical.py", "contracts.py", "registered_functions.py", "typed_executor.py"),
            TYPED_EXECUTOR_COMPONENT,
            catalog=None,
            schemas=schemas,
            manifest=manifest,
            schema_names=("analysis-result.schema.json",),
        ),
        OUTPUT_ROOT / "data_analysis" / "answer_facts_context_builder.py": _analysis_phase_source(
            "AnswerFactsContextBuilder",
            ("canonical.py", "contracts.py", "state_contracts.py", "presenter.py"),
            ANSWER_FACTS_CONTEXT_COMPONENT,
            catalog=None,
            schemas=schemas,
            manifest=manifest,
            schema_names=("answer-facts.schema.json",),
        ),
        OUTPUT_ROOT / "data_analysis" / "answer_claim_validator.py": _analysis_phase_source(
            "AnswerClaimValidator",
            ("canonical.py",),
            ANSWER_CLAIM_VALIDATOR_COMPONENT,
            catalog=None,
            schemas=schemas,
            manifest=manifest,
        ),
        OUTPUT_ROOT / "data_analysis" / "response_state_commit.py": _analysis_phase_source(
            "ResponseStateCommit",
            ("canonical.py", "contracts.py", "state_contracts.py", "presenter.py"),
            RESPONSE_COMMIT_COMPONENT,
            catalog=None,
            schemas=schemas,
            manifest=manifest,
            schema_names=(
                "analysis-result.schema.json",
                "executed-result.schema.json",
                "turn-state.schema.json",
                "answer-facts.schema.json",
                "answer-sections.schema.json",
                "response.schema.json",
                "error.schema.json",
            ),
        ),
        OUTPUT_ROOT / "data_analysis" / "01_message_presentation.py": _presenter_source(schemas, manifest),
        OUTPUT_ROOT / "data_analysis" / "02_gaia_output.py": _presenter_source(schemas, manifest, gaia=True),
        OUTPUT_ROOT / "shared" / "00_api_response_terminal.py": _analysis_phase_source(
            "APIResponseTerminal",
            ("canonical.py", "contracts.py", "presenter.py"),
            API_RESPONSE_COMPONENT,
            catalog=None,
            schemas=schemas,
            manifest=manifest,
            schema_names=("response.schema.json", "metadata-authoring-response.schema.json"),
        ),
        OUTPUT_ROOT / "metadata_authoring" / "natural_metadata_source_bundle.py": _analysis_phase_source(
            "NaturalMetadataSourceBundle",
            (),
            NATURAL_METADATA_SOURCE_BUNDLE_COMPONENT,
            catalog=None,
            schemas=schemas,
            manifest=manifest,
        ),
        OUTPUT_ROOT / "metadata_authoring" / "authoring_reference_registry.py": _analysis_phase_source(
            "AuthoringReferenceRegistry",
            (),
            AUTHORING_REFERENCE_REGISTRY_COMPONENT,
            catalog=None,
            schemas=schemas,
            manifest=manifest,
            extra_blocks=(SEMANTIC_VOCABULARY_HELPERS,),
        ),
        OUTPUT_ROOT / "metadata_authoring" / "authoring_prompt_context_builder.py": _authoring_prompt_context_source(
            catalog, schemas, manifest
        ),
        OUTPUT_ROOT / "metadata_authoring" / "00_metadata_authoring_engine.py": _authoring_source(
            catalog, schemas, manifest
        ),
        OUTPUT_ROOT / "metadata_authoring" / "01_authoring_message_presentation.py": _authoring_message_source(
            schemas, manifest
        ),
    }
    changed: list[Path] = []
    for path, source in sources.items():
        _assert_safe_generated(path, source)
        existing = path.read_text(encoding="utf-8") if path.is_file() else None
        if existing != source:
            changed.append(path)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source, encoding="utf-8", newline="\n")
    if check and changed:
        relative = ", ".join(path.relative_to(PROJECT_ROOT).as_posix() for path in changed)
        raise GenerationError(f"generated standalone components are stale: {relative}")
    return sorted(sources)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated sources differ")
    args = parser.parse_args()
    try:
        paths = build_components(check=args.check)
    except GenerationError as exc:
        print(f"ERROR: {exc}")
        return 1
    action = "verified" if args.check else "generated"
    print(f"{action} {len(paths)} standalone components")
    for path in paths:
        print(path.relative_to(PROJECT_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
