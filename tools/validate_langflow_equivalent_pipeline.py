"""Validate the exported Flow graph and execute the canonical offline corpus.

The graph check is ID-independent.  Custom components declare
``metadata.logical_stage``; filename inference is retained only as a migration
aid.  This lets the harness prove the same trust/side-effect ordering used by
Langflow without coupling validation to canvas labels or generated UUIDs.
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import json
import os
import sys
from collections import Counter, deque
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_runtime_cases import run_cases
from reference_runtime.canonical import sha256_json


EXPECTED_LOGICAL_STAGES = (
    "request_state",
    "domain_bundle",
    "candidate_route",
    "intent_prompt_context",
    "prompt",
    "llm_invoker",
    "intent_resolver",
    "plan_compiler_validator",
    "job_router",
    "source_retriever",
    "source_merger",
    "typed_executor",
    "answer_facts",
    "narrative_claim",
    "response_state_commit",
    "terminals",
)

_SOURCE_STAGE_MARKERS = {
    "request_state_capsule": "request_state",
    "domain_bundle_loader": "domain_bundle",
    "candidate_route_gate": "candidate_route",
    "common_intent_resolver": "intent_resolver",
    "plan_compiler_validator": "plan_compiler_validator",
    "retrieval_job_router": "job_router",
    "source_retriever": "source_retriever",
    "source_merger": "source_merger",
    "typed_executor": "typed_executor",
    "answer_facts": "answer_facts",
    "narrative": "narrative_claim",
    "response_state_commit": "response_state_commit",
    "message_presentation": "terminals",
    "gaia_output": "terminals",
    "api_response_terminal": "terminals",
}

_STAGE_ALIASES = {
    "intent_prompt_context": "intent_prompt_context",
    "intent_prompt_composition": "prompt",
    "intent_llm_invocation": "llm_invoker",
    "intent_resolution": "intent_resolver",
    "plan_compilation": "plan_compiler_validator",
    "job_routing": "job_router",
    "dummy_retrieval": "source_retriever",
    "oracle_retrieval": "source_retriever",
    "h_api_retrieval": "source_retriever",
    "datalake_retrieval": "source_retriever",
    "goodocs_retrieval": "source_retriever",
    "source_merge": "source_merger",
    "typed_execution": "typed_executor",
    "answer_facts_context": "answer_facts",
    "answer_prompt_composition": "prompt",
    "answer_llm_invocation": "llm_invoker",
    "answer_claim_validation": "narrative_claim",
    "state_commit": "response_state_commit",
}


def _node_config(node: dict[str, Any]) -> dict[str, Any]:
    value = ((node.get("data") or {}).get("node") or {})
    return value if isinstance(value, dict) else {}


def _node_stage(node: dict[str, Any]) -> str:
    node_id = str(node.get("id") or "")
    config = _node_config(node)
    metadata = config.get("metadata") if isinstance(config.get("metadata"), dict) else {}
    explicit = str(metadata.get("logical_stage") or "").strip()
    if explicit:
        return _STAGE_ALIASES.get(explicit, explicit)
    source = f"{metadata.get('source_path', '')} {node_id} {config.get('display_name', '')}".lower()
    native_module = str(metadata.get("module") or "").lower()
    if node.get("type") == "noteNode" or (node.get("data") or {}).get("type") == "note":
        return "annotation"
    if "chatinput" in native_module or node_id == "chat_input":
        return "input"
    if "languagemodel" in native_module or "language_model" in node_id:
        return "model"
    if "promptcomponent" in native_module or node_id.endswith("_prompt"):
        return "prompt"
    if "chatoutput" in native_module or node_id == "chat_output":
        return "terminals"
    for marker, stage in _SOURCE_STAGE_MARKERS.items():
        if marker in source:
            return stage
    return "unclassified"


def _has_path(adjacency: dict[str, set[str]], sources: set[str], targets: set[str]) -> bool:
    queue = deque(sources)
    seen = set(sources)
    while queue:
        current = queue.popleft()
        if current in targets:
            return True
        for following in adjacency.get(current, set()):
            if following not in seen:
                seen.add(following)
                queue.append(following)
    return False


def _acyclic(node_ids: set[str], adjacency: dict[str, set[str]]) -> bool:
    indegree = {node_id: 0 for node_id in node_ids}
    for targets in adjacency.values():
        for target in targets:
            if target in indegree:
                indegree[target] += 1
    queue = deque(sorted(node_id for node_id, count in indegree.items() if count == 0))
    visited = 0
    while queue:
        current = queue.popleft()
        visited += 1
        for target in adjacency.get(current, set()):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return visited == len(node_ids)


def validate_flow_graph(flow: dict[str, Any]) -> dict[str, Any]:
    nodes = flow.get("data", {}).get("nodes", [])
    edges = flow.get("data", {}).get("edges", [])
    node_by_id = {str(node.get("id") or ""): node for node in nodes if node.get("id")}
    stage_by_id = {node_id: _node_stage(node) for node_id, node in node_by_id.items()}
    ids_by_stage: dict[str, set[str]] = {}
    for node_id, stage in stage_by_id.items():
        ids_by_stage.setdefault(stage, set()).add(node_id)
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_by_id}
    edge_pairs: list[tuple[str, str]] = []
    for edge in edges:
        source = str(edge.get("source") or "")
        target = str(edge.get("target") or "")
        if source in node_by_id and target in node_by_id:
            adjacency[source].add(target)
            edge_pairs.append((source, target))

    def present(stage: str) -> bool:
        return bool(ids_by_stage.get(stage))

    def path(left: str, right: str) -> bool:
        return present(left) and present(right) and _has_path(
            adjacency, ids_by_stage[left], ids_by_stage[right]
        )

    checks = {
        "all_nodes_classified": "unclassified" not in ids_by_stage,
        "acyclic": _acyclic(set(node_by_id), adjacency),
        "request_to_route": path("request_state", "candidate_route"),
        "domain_to_route": path("domain_bundle", "candidate_route"),
        "route_to_intent": path("candidate_route", "intent_resolver"),
        "model_to_intent": path("model", "intent_resolver"),
        "intent_to_plan": path("intent_resolver", "plan_compiler_validator"),
        "plan_to_router": path("plan_compiler_validator", "job_router"),
        "router_to_each_retriever": present("source_retriever")
        and all(
            _has_path(adjacency, ids_by_stage["job_router"], {retriever})
            for retriever in ids_by_stage["source_retriever"]
        ),
        "each_retriever_to_merger": present("source_merger")
        and present("source_retriever")
        and all(
            _has_path(adjacency, {retriever}, ids_by_stage["source_merger"])
            for retriever in ids_by_stage["source_retriever"]
        ),
        "merger_to_executor": path("source_merger", "typed_executor"),
        "executor_to_answer_facts": path("typed_executor", "answer_facts"),
        "answer_to_commit": path("answer_facts", "response_state_commit"),
        "commit_to_terminals": path("response_state_commit", "terminals"),
        "three_retrieval_modes": len(ids_by_stage.get("source_retriever", set())) >= 3,
        "single_commit_boundary": len(ids_by_stage.get("response_state_commit", set())) == 1,
    }
    anonymous_state_nodes = ids_by_stage.get("request_state", set()) | ids_by_stage.get("response_state_commit", set())
    checks["anonymous_multiturn_defaults_off"] = len(anonymous_state_nodes) == 2 and all(
        isinstance((_node_config(node_by_id[node_id]).get("template") or {}).get("allow_anonymous_multiturn"), dict)
        and ((_node_config(node_by_id[node_id]).get("template") or {}).get("allow_anonymous_multiturn") or {}).get("value")
        is False
        for node_id in anonymous_state_nodes
    )
    retriever_ids = ids_by_stage.get("source_retriever", set())
    merger_ids = ids_by_stage.get("source_merger", set())
    executor_ids = ids_by_stage.get("typed_executor", set())
    checks["raw_source_rows_retriever_to_merger_only"] = bool(retriever_ids and merger_ids) and all(
        adjacency.get(node_id, set()) and adjacency[node_id] <= merger_ids for node_id in retriever_ids
    )
    checks["merged_source_rows_to_executor_only"] = bool(merger_ids and executor_ids) and all(
        adjacency.get(node_id, set()) and adjacency[node_id] <= executor_ids for node_id in merger_ids
    )
    model_targets = set().union(*(adjacency.get(node_id, set()) for node_id in ids_by_stage.get("model", set())))
    allowed_model_targets = ids_by_stage.get("llm_invoker", set())
    checks["model_edges_are_semantic_or_narrative_only"] = bool(model_targets) and model_targets <= allowed_model_targets
    # The narrative/claim stage may be implemented inside the answer-facts
    # component, but it must be explicitly declared in its metadata.
    answer_nodes = ids_by_stage.get("answer_facts", set())
    narrative_declared = present("narrative_claim") or any(
        "narrative_claim" in (
            (_node_config(node_by_id[node_id]).get("metadata") or {}).get("logical_capabilities") or []
        )
        for node_id in answer_nodes
    )
    checks["narrative_claim_boundary_declared"] = narrative_declared

    return {
        "contract_version": "langflow.pipeline.graph.validation.v1",
        "flow_id": flow.get("id"),
        "endpoint_name": flow.get("endpoint_name"),
        "node_count": len(node_by_id),
        "edge_count": len(edge_pairs),
        "stage_counts": dict(sorted(Counter(stage_by_id.values()).items())),
        "stage_by_node": dict(sorted(stage_by_id.items())),
        "checks": checks,
        "passed": all(checks.values()),
        "failures": sorted(name for name, passed in checks.items() if not passed),
    }


class DenyModel:
    """A zero-LLM oracle for deterministic component-pipeline smoke runs."""

    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, prompt: str) -> str:
        self.calls += 1
        raise RuntimeError("unexpected_model_call")


def _edge_ports(edge: dict[str, Any]) -> tuple[str, str]:
    data = edge.get("data") if isinstance(edge.get("data"), dict) else {}
    source_handle = data.get("sourceHandle") if isinstance(data.get("sourceHandle"), dict) else {}
    target_handle = data.get("targetHandle") if isinstance(data.get("targetHandle"), dict) else {}
    return str(source_handle.get("name") or ""), str(target_handle.get("fieldName") or "")


def _topological_order(node_ids: set[str], edges: list[dict[str, Any]]) -> list[str]:
    adjacency = {node_id: set() for node_id in node_ids}
    indegree = {node_id: 0 for node_id in node_ids}
    for edge in edges:
        source, target = str(edge.get("source") or ""), str(edge.get("target") or "")
        if source in node_ids and target in node_ids and target not in adjacency[source]:
            adjacency[source].add(target)
            indegree[target] += 1
    queue = deque(sorted(node_id for node_id, count in indegree.items() if count == 0))
    ordered: list[str] = []
    while queue:
        current = queue.popleft()
        ordered.append(current)
        for target in sorted(adjacency[current]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(ordered) != len(node_ids):
        raise RuntimeError("flow_graph_cycle")
    return ordered


def _template_value(config: dict[str, Any], field_name: str) -> Any:
    template = config.get("template") if isinstance(config.get("template"), dict) else {}
    field = template.get(field_name) if isinstance(template.get(field_name), dict) else {}
    return deepcopy(field.get("value"))


def _plain(value: Any) -> Any:
    if hasattr(value, "data") and isinstance(getattr(value, "data"), dict):
        return deepcopy(getattr(value, "data"))
    if hasattr(value, "text"):
        return {
            "text": str(getattr(value, "text", "")),
            "data": deepcopy(getattr(value, "data", {}) or {}),
        }
    if isinstance(value, dict):
        return deepcopy(value)
    if isinstance(value, list):
        return deepcopy(value)
    return value


def _contract_versions(value: Any) -> set[str]:
    versions: set[str] = set()

    def visit(item: Any) -> None:
        item = _plain(item)
        if isinstance(item, dict):
            version = item.get("contract_version")
            if isinstance(version, str):
                versions.add(version)
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return versions


def _bounded_status(value: Any) -> dict[str, Any]:
    plain = _plain(value)
    if not isinstance(plain, dict):
        return {}
    error = plain.get("error") if isinstance(plain.get("error"), dict) else {}
    return {
        "ok": plain.get("ok"),
        "status": plain.get("status"),
        "stage": plain.get("stage"),
        "error_code": error.get("code"),
        "error_stage": error.get("stage"),
        "error_message": str(error.get("message") or "")[:160],
        "error_detail_keys": sorted((error.get("details") or {}).keys())
        if isinstance(error.get("details"), dict)
        else [],
    }


def _invoke(method: Any) -> Any:
    value = method()
    if inspect.isawaitable(value):
        return asyncio.run(value)
    return value


def execute_component_pipeline(
    flow: dict[str, Any],
    *,
    question: str,
    session_id: str,
    domain_id: str,
    environment: str | None = None,
    allow_anonymous_multiturn: bool = False,
    inline_domain_bundle: dict[str, Any] | None = None,
    inline_source_payload: dict[str, Any] | None = None,
    expected_total: tuple[str, float] | None = None,
    expected_rows: list[dict[str, Any]] | None = None,
    language_model: Any = None,
    expected_model_calls: int = 0,
    expected_status: str = "ok",
    shared_state_store: Any = None,
    reference_instant: str = "2026-07-30T09:00:00+09:00",
    expected_route: str | None = None,
    expected_datasets: list[str] | None = None,
    expected_operators: list[str] | None = None,
    expected_output_fields: list[str] | None = None,
    expected_retrieval_calls: int | None = None,
    narrative_enabled: bool | None = None,
    expected_narrative_status: str | None = None,
    user_id: str = "",
    anonymous_multiturn_overrides: dict[str, bool] | None = None,
    component_overrides: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    class _ValidationDatalakeClient:
        """Read-only in-memory client used only by the Langflow-equivalent test."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def run_sql(self, sql: str) -> list[dict[str, Any]]:
            datasets = (
                inline_source_payload.get("datasets")
                if isinstance(inline_source_payload, dict)
                and isinstance(inline_source_payload.get("datasets"), dict)
                else {}
            )
            # The cross-domain smoke question reads the orders dataset.  The
            # adapter still receives and executes the compiled retrieval job;
            # only the external LakeHouse boundary is replaced by reviewed
            # fixture rows.
            return deepcopy(datasets.get("orders") or [])

    """Run each serialized standalone component in Flow topological order."""

    from lfx.custom.eval import eval_custom_component_code
    from lfx.schema.data import Data
    from lfx.schema.message import Message

    nodes = flow.get("data", {}).get("nodes", [])
    edges = flow.get("data", {}).get("edges", [])
    node_by_id = {str(node.get("id") or ""): node for node in nodes if node.get("id")}
    order = _topological_order(set(node_by_id), edges)
    incoming: dict[str, list[dict[str, Any]]] = {node_id: [] for node_id in node_by_id}
    required_outputs: dict[str, set[str]] = {node_id: set() for node_id in node_by_id}
    for edge in edges:
        target = str(edge.get("target") or "")
        source = str(edge.get("source") or "")
        if target in incoming:
            incoming[target].append(edge)
        source_port, _ = _edge_ports(edge)
        if source in required_outputs and source_port:
            required_outputs[source].add(source_port)

    outputs: dict[tuple[str, str], Any] = {}
    runtime_environment = str(
        environment
        or ((inline_domain_bundle or {}).get("environment") if isinstance(inline_domain_bundle, dict) else "")
        or "production"
    )
    model = language_model if language_model is not None else DenyModel()
    model_calls_before = int(getattr(model, "calls", 0) or 0)
    invocations: list[dict[str, Any]] = []
    failures: list[str] = []
    previous_validation_mode = os.environ.get("V6_VALIDATION_MODE")
    previous_validation_instant = os.environ.get("V6_VALIDATION_REFERENCE_INSTANT")
    os.environ["V6_VALIDATION_MODE"] = "1"
    os.environ["V6_VALIDATION_REFERENCE_INSTANT"] = reference_instant
    for node_id in order:
        node = node_by_id[node_id]
        config = _node_config(node)
        stage = _node_stage(node)
        try:
            if stage == "annotation":
                invocations.append({"node_id": node_id, "stage": stage, "methods": []})
                continue
            if stage == "input":
                outputs[(node_id, "message")] = Message(
                    text=question,
                    session_id=session_id,
                    data={"metadata": {"domain_id": domain_id}},
                )
                invocations.append({"node_id": node_id, "stage": stage, "methods": ["native_input"]})
                continue
            if stage == "model":
                outputs[(node_id, "model_output")] = model
                outputs[(node_id, "text_output")] = ""
                invocations.append({"node_id": node_id, "stage": stage, "methods": ["native_model"]})
                continue
            if stage == "domain_bundle":
                package = deepcopy(inline_domain_bundle) if isinstance(inline_domain_bundle, dict) else None
                if package is None:
                    package_path = ROOT / "metadata" / "domain_packs" / domain_id / "compiled" / "domain_package.json"
                    if not package_path.exists():
                        raise RuntimeError("validation_available_metadata_missing")
                    package = json.loads(package_path.read_text(encoding="utf-8"))
                catalog = deepcopy(
                    package.get("runtime_catalog")
                    if isinstance(package.get("runtime_catalog"), dict)
                    else package
                )
                if inline_source_payload:
                    # The order-sales corpus supplies reviewed physical rows but
                    # its portable package intentionally declares dummy sources.
                    # Exercise the new per-source live path through Datalake in
                    # this validation-only catalog copy; production metadata is
                    # never changed or persisted.
                    for dataset in (catalog.get("datasets") or {}).values():
                        if isinstance(dataset, dict):
                            dataset["source_type"] = "datalake"
                            dataset["source_adapter"] = "validation.datalake"
                            dataset["query_template"] = "SELECT * FROM validation_fixture"
                    catalog["catalog_sha256"] = sha256_json(
                        {key: value for key, value in catalog.items() if key != "catalog_sha256"}
                    )
                identity = {
                    "contract_version": "pipeline.context.v1",
                    "ok": True,
                    "stage": "domain_bundle",
                    "domain_bundle": {
                        "contract_version": "domain.bundle.runtime.v1",
                        "domain_id": str(package.get("domain_id") or catalog.get("domain_id") or domain_id),
                        "environment": str(package.get("environment") or catalog.get("environment") or runtime_environment),
                        "revision": str(package.get("revision") or catalog.get("revision") or "validation"),
                        "source_mode": "validation_available_metadata",
                        "catalog_sha256": str(catalog.get("catalog_sha256") or ""),
                        "package_sha256": str(package.get("package_sha256") or ""),
                        "bundle_sha256": str(package.get("bundle_sha256") or ""),
                        "runtime_catalog": deepcopy(catalog),
                    },
                }
                outputs[(node_id, "domain_bundle")] = Data(data=identity)
                invocations.append({"node_id": node_id, "stage": stage, "methods": ["validation_available_metadata"]})
                continue
            native_module = str((config.get("metadata") or {}).get("module") or "").lower()
            if stage == "prompt" and "promptcomponent" in native_module:
                template_text = str(_template_value(config, "template") or "")
                if not template_text:
                    raise RuntimeError("prompt_template_missing")
                variables: dict[str, str] = {}
                for edge in incoming[node_id]:
                    source_node = str(edge.get("source") or "")
                    source_port, target_port = _edge_ports(edge)
                    if not source_port or not target_port or (source_node, source_port) not in outputs:
                        raise RuntimeError("prompt_edge_contract_missing")
                    raw_value = outputs[(source_node, source_port)]
                    variables[target_port] = str(getattr(raw_value, "text", raw_value) or "")
                use_double_brackets = bool(_template_value(config, "use_double_brackets"))
                prompt_message = asyncio.run(
                    Message.from_template_and_variables(
                        template=template_text,
                        template_format="mustache" if use_double_brackets else "f-string",
                        **variables,
                    )
                )
                outputs[(node_id, "prompt")] = prompt_message
                invocations.append({"node_id": node_id, "stage": stage, "methods": ["native_prompt"]})
                continue
            if stage == "terminals" and "chatoutput" in str((config.get("metadata") or {}).get("module") or "").lower():
                edge = incoming[node_id][0] if incoming[node_id] else {}
                source_port, _ = _edge_ports(edge)
                value = outputs.get((str(edge.get("source") or ""), source_port))
                outputs[(node_id, "message")] = value
                invocations.append({"node_id": node_id, "stage": stage, "methods": ["native_output"]})
                continue

            template = config.get("template") if isinstance(config.get("template"), dict) else {}
            code_field = template.get("code") if isinstance(template.get("code"), dict) else {}
            source = str(code_field.get("value") or "")
            if not source:
                raise RuntimeError("component_source_missing")
            component_cls = eval_custom_component_code(source)
            component = component_cls()
            if shared_state_store is not None:
                for attribute in component_cls.__dict__.values():
                    globals_value = getattr(attribute, "__globals__", None)
                    if isinstance(globals_value, dict) and "_shared_memory_store" in globals_value:
                        globals_value["_shared_memory_store"] = lambda: shared_state_store
            for field_name in config.get("field_order", []):
                field_name = str(field_name)
                field_value = _template_value(config, field_name)
                if field_name == "user_id" and hasattr(type(component), "user_id"):
                    # Component.user_id is read-only in LFX 0.4.2. Langflow
                    # injects the corresponding graph value through _user_id.
                    component._user_id = field_value
                else:
                    setattr(component, field_name, field_value)
            if hasattr(component, "domain_id"):
                component.domain_id = domain_id
            if hasattr(component, "environment"):
                component.environment = runtime_environment
            if hasattr(component, "allow_anonymous_multiturn"):
                override = (anonymous_multiturn_overrides or {}).get(node_id)
                component.allow_anonymous_multiturn = bool(
                    allow_anonymous_multiturn if override is None else override
                )
            if user_id and hasattr(type(component), "user_id"):
                # LFX 0.4.2 exposes Component.user_id as a read-only runtime
                # property backed by _user_id.  Langflow populates that backing
                # field from the graph context; assigning the property here
                # fails on every component because it intentionally has no
                # setter.  Mirror the runtime injection boundary directly.
                component._user_id = user_id
            if narrative_enabled is not None and hasattr(component, "narrative_enabled"):
                component.narrative_enabled = bool(narrative_enabled)
            if hasattr(component, "session_id"):
                component.session_id = session_id
            if hasattr(component, "data_mode"):
                component.data_mode = "live" if inline_source_payload else "dummy"
            if hasattr(component, "source_payload") and inline_source_payload:
                component.source_payload = Data(data=deepcopy(inline_source_payload))
            if node_id == "datalake_source_retriever" and inline_source_payload:
                component.client_cls = _ValidationDatalakeClient
            for field_name, field_value in (component_overrides or {}).get(node_id, {}).items():
                setattr(component, str(field_name), deepcopy(field_value))

            for edge in incoming[node_id]:
                source_node = str(edge.get("source") or "")
                source_port, target_port = _edge_ports(edge)
                if not source_port or not target_port:
                    raise RuntimeError("edge_port_contract_missing")
                if (source_node, source_port) not in outputs:
                    raise RuntimeError("upstream_output_missing")
                setattr(component, target_port, outputs[(source_node, source_port)])

            output_specs = list(getattr(component_cls, "outputs", []))
            names_to_run = set(required_outputs[node_id])
            if stage == "terminals":
                names_to_run.update(str(item.name) for item in output_specs)
            names_to_run.update(
                str(item.name)
                for item in output_specs
                if bool(getattr(item, "is_output", False))
            )
            if not names_to_run and output_specs:
                names_to_run.add(str(output_specs[0].name))
            by_method: dict[str, list[str]] = {}
            for item in output_specs:
                name = str(item.name)
                if name in names_to_run:
                    by_method.setdefault(str(item.method), []).append(name)
            called: list[str] = []
            for method_name, output_names in by_method.items():
                value = _invoke(getattr(component, method_name))
                called.append(method_name)
                for output_name in output_names:
                    outputs[(node_id, output_name)] = value
            snapshot_values = [outputs[(node_id, name)] for name in names_to_run if (node_id, name) in outputs]
            invocations.append(
                {
                    "node_id": node_id,
                    "stage": stage,
                    "methods": called,
                    "output_names": sorted(names_to_run),
                    "contract_versions": sorted(set().union(*(_contract_versions(item) for item in snapshot_values))) if snapshot_values else [],
                    "bounded_status": _bounded_status(snapshot_values[0]) if snapshot_values else {},
                }
            )
        except Exception as exc:
            failures.append(f"{node_id}:{stage}:{type(exc).__name__}:{str(exc).splitlines()[0][:96]}")
            break

    def stage_value(stage: str, output_name: str) -> Any:
        for row in invocations:
            if row["stage"] == stage and (row["node_id"], output_name) in outputs:
                return outputs[(row["node_id"], output_name)]
        return None

    response = _plain(stage_value("response_state_commit", "response"))
    answer_context = _plain(stage_value("narrative_claim", "answer_context"))
    narrative = (
        answer_context.get("narrative")
        if isinstance(answer_context, dict) and isinstance(answer_context.get("narrative"), dict)
        else {}
    )
    plan_context = _plain(stage_value("plan_compiler_validator", "plan_context"))
    plan = plan_context.get("plan") if isinstance(plan_context, dict) and isinstance(plan_context.get("plan"), dict) else {}
    observed_datasets = [
        str(item.get("dataset_key") or "")
        for item in plan.get("retrieval_jobs", [])
        if isinstance(item, dict) and item.get("dataset_key")
    ]
    observed_operators = [
        str(item.get("op") or "").removesuffix(".v1")
        for item in plan.get("operations", [])
        if isinstance(item, dict) and item.get("op")
    ]
    api_response = None
    presented_message = None
    gaia_response = None
    for row in invocations:
        node_id = row["node_id"]
        for name in row.get("output_names", []):
            value = outputs.get((node_id, name))
            if name == "api_response":
                api_response = _plain(value)
            elif name == "gaia_response":
                gaia_response = _plain(value)
            elif name == "message" and "presentation" in node_id:
                presented_message = _plain(value)

    core_expected = {
        "request_state": 1,
        "domain_bundle": 1,
        "candidate_route": 1,
        "intent_resolver": 1,
        "plan_compiler_validator": 1,
        "job_router": 1,
        "source_retriever": 5,
        "source_merger": 1,
        "typed_executor": 1,
        "answer_facts": 1,
        "response_state_commit": 1,
    }
    stage_counts = Counter(row["stage"] for row in invocations)
    source_contract_stages = {
        row["stage"]
        for row in invocations
        if any(version.startswith(("source.result", "source.bundle", "source.execution")) for version in row.get("contract_versions", []))
    }
    response_json_ok = isinstance(response, dict) and "response_sha256" not in response
    response_errors = []
    if isinstance(response, dict):
        raw_errors = response.get("errors") if isinstance(response.get("errors"), list) else []
        response_errors = [
            {
                "code": str(item.get("code") or ""),
                "stage": str(item.get("stage") or ""),
                "message": str(item.get("message") or "")[:160],
                "detail_keys": sorted((item.get("details") or {}).keys())
                if isinstance(item.get("details"), dict)
                else [],
                "safe_details": {
                    key: str((item.get("details") or {}).get(key) or "")[:400]
                    for key in ("schema", "path", "reason", "error_type", "relation_id")
                    if isinstance(item.get("details"), dict) and key in (item.get("details") or {})
                },
            }
            for item in raw_errors
            if isinstance(item, dict)
        ][:8]
        if not response_errors:
            def collect_errors(value: Any) -> None:
                if len(response_errors) >= 8:
                    return
                value = _plain(value)
                if isinstance(value, dict):
                    if value.get("code") and value.get("stage"):
                        response_errors.append(
                            {
                                "code": str(value.get("code") or ""),
                                "stage": str(value.get("stage") or ""),
                                "message": str(value.get("message") or "")[:160],
                                "detail_keys": sorted((value.get("details") or {}).keys())
                                if isinstance(value.get("details"), dict)
                                else [],
                                # Keep diagnostics useful without copying raw
                                # request/result payloads into validation evidence.
                                "schema": str((value.get("details") or {}).get("schema") or "")[:128]
                                if isinstance(value.get("details"), dict)
                                else "",
                                "path": str((value.get("details") or {}).get("path") or "")[:256]
                                if isinstance(value.get("details"), dict)
                                else "",
                                "reason": str((value.get("details") or {}).get("reason") or "")[:256]
                                if isinstance(value.get("details"), dict)
                                else "",
                                "error_type": str((value.get("details") or {}).get("error_type") or "")[:96]
                                if isinstance(value.get("details"), dict)
                                else "",
                                "safe_details": {
                                    key: str((value.get("details") or {}).get(key) or "")[:400]
                                    for key in ("schema", "path", "reason", "error_type", "relation_id")
                                    if isinstance(value.get("details"), dict)
                                    and key in (value.get("details") or {})
                                },
                            }
                        )
                        return
                    for nested in value.values():
                        collect_errors(nested)
                elif isinstance(value, list):
                    for nested in value:
                        collect_errors(nested)

            collect_errors(response)
    message_response = None
    if isinstance(presented_message, dict):
        message_response = presented_message.get("response")
        if message_response is None and isinstance(presented_message.get("data"), dict):
            message_response = presented_message["data"].get("response")
    gaia_metadata = (gaia_response or {}).get("metadata") if isinstance(gaia_response, dict) else {}
    checks = {
        "all_core_nodes_invoked_once": all(stage_counts.get(stage, 0) == count for stage, count in core_expected.items()),
        "each_core_node_has_required_method": all(
            len(row.get("methods", [])) >= 1 for row in invocations if row["stage"] in core_expected
        ),
        "provider_call_count_exact": int(getattr(model, "calls", 0) or 0) - model_calls_before
        == int(expected_model_calls),
        "response_status_expected": isinstance(response, dict) and response.get("status") == expected_status,
        "response_is_plain_json": response_json_ok,
        "message_uses_canonical_response": message_response == response,
        "api_uses_canonical_response": api_response == response,
        "gaia_uses_plain_metadata": isinstance(gaia_metadata, dict)
        and "response_sha256" not in gaia_metadata,
        "source_contracts_bounded_to_retrieval_merge_execute": source_contract_stages
        <= {"source_retriever", "source_merger", "typed_executor"},
    }
    if expected_total is not None:
        field_name, expected_value = expected_total
        result_rows = (response or {}).get("data", {}).get("rows", []) if isinstance(response, dict) else []
        observed = [row.get(field_name) for row in result_rows if isinstance(row, dict) and field_name in row]
        checks["expected_total"] = len(observed) == 1 and float(observed[0]) == float(expected_value)
    if expected_rows is not None:
        result_rows = (response or {}).get("data", {}).get("rows", []) if isinstance(response, dict) else []
        checks["expected_rows"] = len(result_rows) == len(expected_rows) and all(
            any(
                isinstance(actual, dict)
                and set(actual) == set(expected)
                and actual == expected
                for actual in result_rows
            )
            for expected in expected_rows
        )
    if expected_route is not None:
        checks["expected_route"] = (((response or {}).get("trace") or {}).get("route") or {}).get("route") == expected_route
    if expected_datasets is not None:
        checks["expected_datasets"] = observed_datasets == expected_datasets
    if expected_operators is not None:
        normalized_expected = [str(item).removesuffix(".v1") for item in expected_operators]
        checks["expected_operators"] = all(item in observed_operators for item in normalized_expected)
    if expected_output_fields is not None:
        observed_columns = list((response or {}).get("data", {}).get("columns", [])) if isinstance(response, dict) else []
        checks["expected_output_fields"] = observed_columns == list(expected_output_fields)
    if expected_retrieval_calls is not None:
        checks["expected_retrieval_calls"] = len(observed_datasets) == int(expected_retrieval_calls)
    if expected_narrative_status is not None:
        checks["expected_narrative_status"] = narrative.get("claim_status") == expected_narrative_status
    response_state = response.get("state") if isinstance(response, dict) and isinstance(response.get("state"), dict) else {}
    response_refs = response.get("data_refs") if isinstance(response, dict) and isinstance(response.get("data_refs"), list) else []
    notices = (
        ((response.get("answer_sections") or {}).get("notices") or [])
        if isinstance(response, dict) and isinstance(response.get("answer_sections"), dict)
        else []
    )
    answer_downloads = (
        ((response.get("answer_sections") or {}).get("downloads") or [])
        if isinstance(response, dict) and isinstance(response.get("answer_sections"), dict)
        else []
    )
    result_table = (
        ((response.get("answer_sections") or {}).get("result_table") or {})
        if isinstance(response, dict) and isinstance(response.get("answer_sections"), dict)
        else {}
    )
    report = {
        "contract_version": "langflow.component.pipeline.validation.v1",
        "question_sha256": sha256_json(question),
        "domain_id": domain_id,
        "environment": runtime_environment,
        "anonymous_multiturn_test_opt_in": bool(allow_anonymous_multiturn),
        "session_id_sha256": sha256_json(session_id),
        "reference_instant": reference_instant,
        "stage_counts": dict(sorted(stage_counts.items())),
        "model_calls": {
            "before": model_calls_before,
            "after": int(getattr(model, "calls", 0) or 0),
            "delta": int(getattr(model, "calls", 0) or 0) - model_calls_before,
        },
        "invocations": invocations,
        "checks": checks,
        "failures": failures + sorted(name for name, passed in checks.items() if not passed),
        "passed": not failures and all(checks.values()),
        "response_has_transport_hash": isinstance(response, dict) and "response_sha256" in response,
        "response_status": (response or {}).get("status") if isinstance(response, dict) else None,
        "response_keys": sorted(response.keys()) if isinstance(response, dict) else [],
        "response_errors": response_errors,
        "route": (((response or {}).get("trace") or {}).get("route") or {}) if isinstance(response, dict) else {},
        "usage": (((response or {}).get("trace") or {}).get("usage") or {}) if isinstance(response, dict) else {},
        "state_version": (((response or {}).get("state") or {}).get("state_version")) if isinstance(response, dict) else None,
        "source_contract_stages": sorted(source_contract_stages),
        "result_contract": {
            "columns": list((response or {}).get("data", {}).get("columns", [])) if isinstance(response, dict) else [],
            "row_count": int((response or {}).get("data", {}).get("row_count") or 0) if isinstance(response, dict) else 0,
            "result_sha256": ((response or {}).get("analysis") or {}).get("result_sha256") if isinstance(response, dict) else None,
        },
        "plan_contract": {
            "dataset_keys": observed_datasets,
            "operators": observed_operators,
            "plan_fingerprint": plan.get("plan_fingerprint") if isinstance(plan, dict) else None,
        },
        "narrative_contract": {
            "attempted": bool(narrative.get("attempted")),
            "claim_status": narrative.get("claim_status"),
            "llm_calls": int(narrative.get("llm_calls") or 0),
            "message_sha256": sha256_json(str(narrative.get("message") or "")),
        },
        "state_contract": {
            "state_version": response_state.get("state_version"),
            "has_executed_result_ref": bool(response_state.get("executed_result_ref")),
            "response_state_is_null": isinstance(response, dict) and response.get("state") is None,
            "data_ref_count": len(response_refs),
            "download_count": sum(
                1 for item in response_refs if isinstance(item, dict) and item.get("download_url")
            ),
            "answer_download_count": len(answer_downloads),
            "result_table_has_data_ref": bool(result_table.get("data_ref")),
            "notice_codes": sorted(
                str(item.get("code") or "") for item in notices if isinstance(item, dict) and item.get("code")
            ),
        },
    }
    if previous_validation_mode is None:
        os.environ.pop("V6_VALIDATION_MODE", None)
    else:
        os.environ["V6_VALIDATION_MODE"] = previous_validation_mode
    if previous_validation_instant is None:
        os.environ.pop("V6_VALIDATION_REFERENCE_INSTANT", None)
    else:
        os.environ["V6_VALIDATION_REFERENCE_INSTANT"] = previous_validation_instant
    return report


def run(
    flow_path: Path,
    *,
    execute_cases: bool,
    execute_components: bool = False,
    execute_order_sales: bool = False,
    execute_multiturn: bool = False,
) -> dict[str, Any]:
    flow = json.loads(flow_path.read_text(encoding="utf-8"))
    graph = validate_flow_graph(flow)
    runtime = run_cases() if execute_cases else None
    components = (
        execute_component_pipeline(
            flow,
            question="오늘 투입된 제품중 MCP NO가 L-267로 시작하는 제품의 INPUT 수량 알려줘",
            session_id="langflow-equivalent-manufacturing",
            domain_id="manufacturing",
        )
        if execute_components
        else None
    )
    order_sales = None
    if execute_order_sales:
        package = json.loads(
            (ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "domain_package.json").read_text(encoding="utf-8")
        )
        sample = json.loads(
            (ROOT / "metadata" / "domain_packs" / "order_sales" / "sample_rows.json").read_text(encoding="utf-8")
        )
        order_sales = execute_component_pipeline(
            flow,
            question="전체 주문의 매출액 합계를 알려줘",
            session_id="langflow-equivalent-order-sales",
            domain_id="order_sales",
            inline_domain_bundle=package,
            inline_source_payload=sample,
            expected_total=("SALES_AMOUNT", 6200.0),
        )
    multiturn = None
    if execute_multiturn:
        from reference_runtime.state_contracts import InMemoryStateStore

        shared_store = InMemoryStateStore()
        first = execute_component_pipeline(
            flow,
            question="오늘 DA공정에서 생산량 상위 5개 제품을 알려줘",
            session_id="langflow-equivalent-multiturn",
            domain_id="manufacturing",
            shared_state_store=shared_store,
            allow_anonymous_multiturn=True,
        )
        second = execute_component_pipeline(
            flow,
            question="그중 생산량이 가장 많은 제품만 보여줘",
            session_id="langflow-equivalent-multiturn",
            domain_id="manufacturing",
            shared_state_store=shared_store,
            allow_anonymous_multiturn=True,
        )
        rejected = execute_component_pipeline(
            flow,
            question="오늘 생산량 합계를 알려줘",
            session_id="default",
            domain_id="manufacturing",
            shared_state_store=shared_store,
            allow_anonymous_multiturn=True,
            expected_status="error",
        )
        nonpersistent = execute_component_pipeline(
            flow,
            question="오늘 생산량 합계를 알려줘",
            session_id="anonymous-default-single-turn-123456",
            domain_id="manufacturing",
            shared_state_store=shared_store,
        )
        mismatch = execute_component_pipeline(
            flow,
            question="오늘 생산량 합계를 알려줘",
            session_id="anonymous-toggle-mismatch-123456",
            domain_id="manufacturing",
            shared_state_store=shared_store,
            anonymous_multiturn_overrides={
                "request_state_capsule": True,
                "response_state_commit": False,
            },
            expected_status="error",
        )
        auth_session = "authenticated-owner-isolation-123456"
        auth_first = execute_component_pipeline(
            flow,
            question="오늘 생산량 합계를 알려줘",
            session_id=auth_session,
            domain_id="manufacturing",
            shared_state_store=shared_store,
            user_id="owner-a",
        )
        auth_second = execute_component_pipeline(
            flow,
            question="그중 가장 큰 제품만 보여줘",
            session_id=auth_session,
            domain_id="manufacturing",
            shared_state_store=shared_store,
            user_id="owner-a",
        )
        auth_other = execute_component_pipeline(
            flow,
            question="오늘 생산량 합계를 알려줘",
            session_id=auth_session,
            domain_id="manufacturing",
            shared_state_store=shared_store,
            user_id="owner-b",
        )
        state_guard_rows = []
        guard_overrides = {
            "legacy_name": {
                "result_collection": "agent_result_store_v5",
                "state_collection": "agent_v6_session_state",
            },
            "role_swap": {
                "result_collection": "agent_v6_session_state",
                "state_collection": "agent_v6_result_store",
            },
            "same_collection": {
                "result_collection": "agent_v6_result_store",
                "state_collection": "agent_v6_result_store",
            },
        }
        for target_node in ("request_state_capsule", "response_state_commit"):
            for case_id, override in guard_overrides.items():
                guard_session = f"state-collection-guard-{target_node}-{case_id}-123456"
                probe = execute_component_pipeline(
                    flow,
                    question="오늘 생산량 합계를 알려줘",
                    session_id=guard_session,
                    domain_id="manufacturing",
                    shared_state_store=shared_store,
                    component_overrides={target_node: override},
                    expected_status="error",
                )
                errors = probe.get("response_errors") or []
                row_checks = {
                    "pipeline_fail_closed": probe.get("passed") is True
                    and probe.get("response_status") == "error",
                    "policy_error_exact": any(
                        item.get("code") == "state_policy_mismatch"
                        and item.get("stage") == "state_store_config"
                        for item in errors
                        if isinstance(item, dict)
                    ),
                    "no_state_mutation": shared_store.load_state(
                        "anonymous",
                        f"production:manufacturing:{guard_session}",
                    )
                    is None,
                    "zero_llm": probe.get("model_calls", {}).get("delta") == 0,
                }
                state_guard_rows.append(
                    {
                        "target_node": target_node,
                        "case_id": case_id,
                        "override_sha256": sha256_json(override),
                        "checks": row_checks,
                        "passed": all(row_checks.values()),
                    }
                )
        rejected_errors = rejected.get("response_errors") or []
        checks = {
            "turn_1_passed": first.get("passed") is True,
            "turn_2_passed": second.get("passed") is True,
            "state_advanced": first.get("state_version") == 1 and second.get("state_version") == 2,
            "followup_no_source_rows": second.get("source_contract_stages") == [],
            "both_zero_llm": first.get("model_calls", {}).get("delta") == 0
            and second.get("model_calls", {}).get("delta") == 0,
            "invalid_session_fail_closed": rejected.get("passed") is True
            and any(
                item.get("code") == "request_invalid" and item.get("stage") == "request"
                for item in rejected_errors
                if isinstance(item, dict)
            ),
            "invalid_session_no_state_mutation": rejected.get("state_version") is None
            and shared_store.load_state("anonymous", "production:manufacturing:default") is None,
            "anonymous_default_is_nonpersistent": nonpersistent.get("passed") is True
            and nonpersistent.get("state_contract", {}).get("has_executed_result_ref") is False
            and nonpersistent.get("state_contract", {}).get("response_state_is_null") is True
            and nonpersistent.get("state_contract", {}).get("data_ref_count") == 0
            and nonpersistent.get("state_contract", {}).get("download_count") == 0
            and nonpersistent.get("state_contract", {}).get("answer_download_count") == 0
            and nonpersistent.get("state_contract", {}).get("result_table_has_data_ref") is False
            and bool(nonpersistent.get("state_contract", {}).get("notice_codes")),
            "anonymous_toggle_mismatch_fails_closed": mismatch.get("passed") is True
            and mismatch.get("response_status") == "error",
            "authenticated_two_turn_and_owner_isolation": auth_first.get("state_version") == 1
            and auth_second.get("state_version") == 2
            and auth_other.get("state_version") == 1,
            "state_collection_guards_fail_closed": all(row["passed"] for row in state_guard_rows),
        }
        multiturn = {
            "contract_version": "langflow.component.multiturn.validation.v1",
            "checks": checks,
            "passed": all(checks.values()),
            "turns": [first, second],
            "invalid_session_probe": rejected,
            "anonymous_default_probe": nonpersistent,
            "toggle_mismatch_probe": mismatch,
            "authenticated_probes": [auth_first, auth_second, auth_other],
            "state_collection_guard_negatives": state_guard_rows,
        }
    runtime_passed = runtime is None or int(runtime.get("failed") or 0) == 0
    components_passed = components is None or components.get("passed") is True
    order_sales_passed = order_sales is None or order_sales.get("passed") is True
    multiturn_passed = multiturn is None or multiturn.get("passed") is True
    return {
        "contract_version": "langflow.equivalent.pipeline.validation.v1",
        "flow_file": flow_path.name,
        "graph": graph,
        "runtime_cases": runtime,
        "component_pipeline": components,
        "order_sales_component_pipeline": order_sales,
        "multiturn_component_pipeline": multiturn,
        "passed": graph["passed"] and runtime_passed and components_passed and order_sales_passed and multiturn_passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--flow",
        type=Path,
        default=ROOT / "flow_exports" / "metadata_v6_data_analysis_flow_v6_standalone.json",
    )
    parser.add_argument("--execute-cases", action="store_true")
    parser.add_argument("--execute-components", action="store_true")
    parser.add_argument("--execute-order-sales", action="store_true")
    parser.add_argument("--execute-multiturn", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs" / "langflow_equivalent_pipeline.json",
    )
    args = parser.parse_args()
    report = run(
        args.flow.resolve(),
        execute_cases=args.execute_cases,
        execute_components=args.execute_components,
        execute_order_sales=args.execute_order_sales,
        execute_multiturn=args.execute_multiturn,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "passed": report["passed"],
                "graph_passed": report["graph"]["passed"],
                "graph_failures": report["graph"]["failures"],
                "runtime_cases": None
                if report["runtime_cases"] is None
                else {
                    key: report["runtime_cases"][key]
                    for key in ("case_count", "passed", "failed")
                },
                "component_pipeline": None
                if report["component_pipeline"] is None
                else {
                    "passed": report["component_pipeline"]["passed"],
                    "failures": report["component_pipeline"]["failures"],
                },
                "order_sales_component_pipeline": None
                if report["order_sales_component_pipeline"] is None
                else {
                    "passed": report["order_sales_component_pipeline"]["passed"],
                    "failures": report["order_sales_component_pipeline"]["failures"],
                },
                "multiturn_component_pipeline": None
                if report["multiturn_component_pipeline"] is None
                else {
                    "passed": report["multiturn_component_pipeline"]["passed"],
                    "checks": report["multiturn_component_pipeline"]["checks"],
                },
            },
            ensure_ascii=False,
        )
    )
    print(f"report: {args.output}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
