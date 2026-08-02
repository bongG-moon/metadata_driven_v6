"""Validate catalog prompt extensions and node overlays in the exported Flow.

Only hashes, byte counts and boolean assertions are persisted.  Model prompts
and responses are deliberately excluded from the report.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import runpy
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import sha256_json
from reference_runtime.generic_v2_candidates import build_generic_v2_candidate_bundle
from tools.validate_langflow_equivalent_pipeline import execute_component_pipeline


DEFAULT_FLOW = ROOT / "flow_exports" / "metadata_v6_data_analysis_flow_v6_standalone.json"
DEFAULT_PACKAGE = ROOT / "metadata" / "domain_packs" / "order_sales" / "compiled" / "domain_package.json"
DEFAULT_SAMPLE = ROOT / "metadata" / "domain_packs" / "order_sales" / "sample_rows.json"
DEFAULT_OUTPUT = ROOT / "validation_outputs" / "prompt_extension_runtime.json"
INTENT_NODE_SENTINEL = "NODE_INTENT_SENTINEL_V6"
ANSWER_NODE_SENTINEL = "NODE_ANSWER_SENTINEL_V6"


class CaptureSelectionModel:
    def __init__(self) -> None:
        self.calls = 0
        self.prompts: list[str] = []

    def invoke(self, prompt: Any) -> str:
        text = str(prompt)
        self.calls += 1
        self.prompts.append(text)
        match = re.search(r'"candidate_id"\s*:\s*"([^"]+)"', text)
        if match:
            return json.dumps({"intent_candidate_id": match.group(1)}, ensure_ascii=False)
        return json.dumps(
            {"message": "등록된 실행 결과를 기준으로 요약했습니다.", "fact_ids": ["fact:row_count"]},
            ensure_ascii=False,
        )


def _set_template(flow: dict[str, Any], node_id: str, field_name: str, value: Any) -> None:
    for node in flow.get("data", {}).get("nodes", []):
        if str(node.get("id") or "") != node_id:
            continue
        template = node.get("data", {}).get("node", {}).get("template", {})
        field = template.get(field_name) if isinstance(template, dict) else None
        if not isinstance(field, dict):
            raise RuntimeError(f"template_field_missing:{node_id}:{field_name}")
        field["value"] = value
        return
    raise RuntimeError(f"flow_node_missing:{node_id}")


def _serialized_intent_prompt_probe(
    flow: dict[str, Any], *, catalog_extension: str, node_extension: str
) -> tuple[CaptureSelectionModel, dict[str, Any]]:
    """Run the exported context -> Prompt nodes -> composer -> invoker -> resolver chain."""

    from lfx.custom.eval import eval_custom_component_code
    from lfx.schema.data import Data
    from lfx.schema.message import Message

    fixture = runpy.run_path(str(ROOT / "tests" / "test_generic_v2_candidates.py"))
    catalog = fixture["support_ticket_catalog"]()
    request = fixture["request"]("티켓 조회해줘")
    bundle = build_generic_v2_candidate_bundle(request, catalog)
    if (bundle.get("route_decision") or {}).get("route") != "intent_llm":
        raise RuntimeError("support_ticket_ambiguous_route_missing")

    node_by_id = {
        str(item.get("id") or ""): item
        for item in flow.get("data", {}).get("nodes", [])
        if item.get("id")
    }

    def custom_component(node_id: str):
        node = node_by_id.get(node_id) or {}
        template = (((node.get("data") or {}).get("node") or {}).get("template") or {})
        source = str(((template.get("code") or {}).get("value") or ""))
        if not source:
            raise RuntimeError(f"serialized_component_source_missing:{node_id}")
        return eval_custom_component_code(source)()

    def prompt_message(node_id: str, **variables: str) -> Message:
        node = node_by_id.get(node_id) or {}
        template = (((node.get("data") or {}).get("node") or {}).get("template") or {})
        template_text = str(((template.get("template") or {}).get("value") or ""))
        use_double = bool(((template.get("use_double_brackets") or {}).get("value")))
        if not template_text:
            raise RuntimeError(f"prompt_template_missing:{node_id}")
        return asyncio.run(
            Message.from_template_and_variables(
                template=template_text,
                template_format="mustache" if use_double else "f-string",
                **variables,
            )
        )

    selection = Data(
        data={
            "contract_version": "pipeline.context.v1",
            "ok": True,
            "stage": "candidate_route",
            "request": request,
            "candidate_bundle": bundle,
            "candidate_lane": "generic_v2",
            "domain_prompt_extensions": {"intent": catalog_extension},
        }
    )
    context_builder = custom_component("intent_prompt_context_builder")
    context_builder.selection_context = selection
    runtime_context = context_builder.build_context()
    specialized_text = context_builder.build_specialized_text()
    common_message = prompt_message("intent_common_prompt")
    specialized_message = prompt_message(
        "intent_specialized_prompt",
        domain_prompt_text=str(getattr(specialized_text, "text", "") or ""),
    )
    composer = custom_component("intent_prompt_bundle_composer")
    composer.common_prompt_message = common_message
    composer.specialized_prompt_message = specialized_message
    composer.runtime_context = runtime_context
    prompt_bundle = composer.build_prompt_bundle()

    model = CaptureSelectionModel()
    invoker = custom_component("intent_conditional_llm_invoker")
    invoker.prompt_bundle = prompt_bundle
    invoker.language_model = model
    invocation = invoker.invoke_once()
    resolver = custom_component("common_intent_resolver")
    resolver.selection_context = selection
    resolver.intent_invocation_result = invocation
    value = resolver.resolve()
    context = getattr(value, "data", value)
    return model, context if isinstance(context, dict) else {}


def _prompt_evidence(prompt: str, *, catalog_extension: str, node_sentinel: str, max_bytes: int) -> dict[str, Any]:
    byte_count = len(prompt.encode("utf-8"))
    return {
        "prompt_sha256": sha256_json(prompt),
        "prompt_utf8_bytes": byte_count,
        "catalog_extension_sha256": sha256_json(catalog_extension),
        "catalog_extension_present": bool(catalog_extension) and catalog_extension in prompt,
        "node_overlay_present": node_sentinel in prompt,
        "prompt_within_budget": byte_count <= max_bytes,
    }


def run(flow_path: Path, package_path: Path, sample_path: Path) -> dict[str, Any]:
    base_flow = json.loads(flow_path.read_text(encoding="utf-8"))
    package = json.loads(package_path.read_text(encoding="utf-8"))
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    catalog = package.get("runtime_catalog") if isinstance(package.get("runtime_catalog"), dict) else {}
    extensions = catalog.get("prompt_extensions") if isinstance(catalog.get("prompt_extensions"), dict) else {}
    intent_extension = str(extensions.get("intent") or "")
    answer_extension = str(extensions.get("answer") or "")
    if not intent_extension or not answer_extension:
        raise RuntimeError("order_sales_prompt_extensions_missing")

    intent_flow = deepcopy(base_flow)
    _set_template(
        intent_flow,
        "intent_specialized_prompt",
        "template",
        "{{domain_prompt_text}}\n" + INTENT_NODE_SENTINEL,
    )
    intent_model, intent_context = _serialized_intent_prompt_probe(
        intent_flow,
        catalog_extension=intent_extension,
        node_extension=INTENT_NODE_SENTINEL,
    )
    intent_prompt = intent_model.prompts[0] if len(intent_model.prompts) == 1 else ""
    intent_evidence = _prompt_evidence(
        intent_prompt,
        catalog_extension=intent_extension,
        node_sentinel=INTENT_NODE_SENTINEL,
        max_bytes=48 * 1024,
    )
    intent_evidence.update(
        {
            "model_calls_exactly_one": intent_model.calls == 1,
            "route_intent_llm": ((intent_context.get("route_telemetry") or {}).get("intent_llm_calls") == 1),
            "pipeline_passed": intent_context.get("ok") is True
            and (intent_context.get("intent") or {}).get("intent_generator") == "llm",
            "pipeline_failures": []
            if intent_context.get("ok") is True
            else [str(((intent_context.get("error") or {}).get("code") or "intent_probe_failed"))[:160]],
        }
    )

    answer_flow = deepcopy(base_flow)
    _set_template(
        answer_flow,
        "answer_specialized_prompt",
        "template",
        "{{domain_prompt_text}}\n" + ANSWER_NODE_SENTINEL,
    )
    _set_template(
        answer_flow,
        "answer_facts_context_builder",
        "narrative_enabled",
        True,
    )
    answer_model = CaptureSelectionModel()
    answer_pipeline = execute_component_pipeline(
        answer_flow,
        question="전체 주문의 매출액 합계를 알려줘",
        session_id="prompt-extension-answer",
        domain_id="order_sales",
        inline_domain_bundle=package,
        inline_source_payload=sample,
        language_model=answer_model,
        expected_model_calls=1,
        expected_total=("SALES_AMOUNT", 6200.0),
        expected_narrative_status="verified",
    )
    answer_prompt = answer_model.prompts[0] if len(answer_model.prompts) == 1 else ""
    answer_evidence = _prompt_evidence(
        answer_prompt,
        catalog_extension=answer_extension,
        node_sentinel=ANSWER_NODE_SENTINEL,
        max_bytes=12 * 1024,
    )
    answer_evidence.update(
        {
            "model_calls_exactly_one": answer_model.calls == 1,
            "route_deterministic": (answer_pipeline.get("route") or {}).get("route") == "deterministic",
            "pipeline_passed": answer_pipeline.get("passed") is True,
            "pipeline_failures": [str(item)[:160] for item in (answer_pipeline.get("failures") or [])[:8]],
        }
    )

    checks = {
        "intent_catalog_and_overlay_merged": all(
            bool(value) for key, value in intent_evidence.items() if key != "pipeline_failures"
        ),
        "answer_catalog_and_overlay_merged": all(
            bool(value) for key, value in answer_evidence.items() if key != "pipeline_failures"
        ),
        "prompts_not_persisted": True,
        "raw_extensions_not_persisted": True,
    }
    return {
        "contract_version": "prompt-extension.runtime.validation.v1",
        "domain_id": "order_sales",
        "flow_file": flow_path.name,
        "prompt_payloads_persisted": False,
        "intent": intent_evidence,
        "answer": answer_evidence,
        "checks": checks,
        "all_passed": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow", type=Path, default=DEFAULT_FLOW)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--sample", type=Path, default=DEFAULT_SAMPLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run(args.flow.resolve(), args.package.resolve(), args.sample.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_passed": report["all_passed"], "checks": report["checks"]}, ensure_ascii=False))
    print(f"report: {args.output}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
