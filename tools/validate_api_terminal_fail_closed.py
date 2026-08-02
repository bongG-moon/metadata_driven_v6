"""Prove that the exported API terminal rejects mutated canonical responses.

The terminal is evaluated from the serialized Flow source, so this checks the
same standalone component code that Langflow imports rather than a sibling
Python implementation.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import sha256_json
from reference_runtime.engine import AnalysisEngine


DEFAULT_FLOW = ROOT / "flow_exports" / "metadata_v6_data_analysis_flow_v6_standalone.json"
DEFAULT_OUTPUT = ROOT / "validation_outputs" / "api_terminal_fail_closed.json"


def _config(node: dict[str, Any]) -> dict[str, Any]:
    value = node.get("data", {}).get("node", {})
    return value if isinstance(value, dict) else {}


def _api_source(flow: dict[str, Any]) -> str:
    for node in flow.get("data", {}).get("nodes", []):
        config = _config(node)
        identity = " ".join(
            (
                str(node.get("id") or ""),
                str(config.get("display_name") or ""),
                str(config.get("type") or ""),
            )
        ).casefold()
        if "api_response" not in identity and "api response" not in identity:
            continue
        code = ((config.get("template") or {}).get("code") or {}).get("value")
        if isinstance(code, str) and code.strip():
            return code
    raise RuntimeError("api_response_terminal_source_missing")


def _attempt(component_cls: type, response: dict[str, Any]) -> dict[str, Any]:
    from lfx.schema.data import Data

    component = component_cls()
    component.response = Data(data=deepcopy(response))
    try:
        raw = component.build_response()
        value = getattr(raw, "data", raw)
        return {
            "blocked": value != response,
            "exception_type": None,
            "returned_contract": value.get("contract_version") if isinstance(value, dict) else None,
            "returned_sha256": value.get("response_sha256") if isinstance(value, dict) else None,
        }
    except Exception as exc:  # the intended fail-closed behavior
        return {
            "blocked": True,
            "exception_type": type(exc).__name__,
            "returned_contract": None,
            "returned_sha256": None,
        }


def run(flow_path: Path) -> dict[str, Any]:
    from lfx.custom.eval import eval_custom_component_code

    flow = json.loads(flow_path.read_text(encoding="utf-8"))
    component_cls = eval_custom_component_code(_api_source(flow))
    valid = AnalysisEngine().analyze(
        "오늘 투입된 제품중 MCP NO가 L-267로 시작하는 제품의 INPUT 수량 알려줘",
        session_id="api-terminal-validation",
        reference_instant="2026-07-30T09:00:00+09:00",
    )
    if valid.get("status") != "ok":
        raise RuntimeError("valid_response_fixture_failed")

    mutations: list[tuple[str, dict[str, Any]]] = []
    changed_message = deepcopy(valid)
    changed_message["message"] = str(changed_message.get("message") or "") + " [tampered]"
    mutations.append(("message_changed_without_rehash", changed_message))

    corrupt_hash = deepcopy(valid)
    corrupt_hash["response_sha256"] = "0" * 64
    mutations.append(("hash_corrupted", corrupt_hash))

    extra_field = deepcopy(valid)
    extra_field["unregistered_extra"] = True
    extra_material = {key: value for key, value in extra_field.items() if key != "response_sha256"}
    extra_field["response_sha256"] = sha256_json(extra_material)
    mutations.append(("schema_extra_field_rehashed", extra_field))

    missing_field = deepcopy(valid)
    missing_field.pop("analysis_mode", None)
    missing_material = {key: value for key, value in missing_field.items() if key != "response_sha256"}
    missing_field["response_sha256"] = sha256_json(missing_material)
    mutations.append(("schema_required_field_removed_rehashed", missing_field))

    valid_result = _attempt(component_cls, valid)
    valid_check = {
        "accepted_unchanged": valid_result["blocked"] is False,
        "contract_preserved": valid_result["returned_contract"] == "response.v1",
        "hash_preserved": valid_result["returned_sha256"] == valid.get("response_sha256"),
    }
    rows: list[dict[str, Any]] = []
    for case_id, payload in mutations:
        outcome = _attempt(component_cls, payload)
        rows.append(
            {
                "case_id": case_id,
                "input_sha256": sha256_json(payload),
                "blocked": outcome["blocked"],
                "exception_type": outcome["exception_type"],
            }
        )
    checks = {
        "valid_response_accepted_unchanged": all(valid_check.values()),
        "all_mutations_blocked": all(row["blocked"] for row in rows),
        "four_negative_classes_covered": len(rows) == 4,
    }
    return {
        "contract_version": "api-terminal.fail-closed.validation.v1",
        "flow_file": flow_path.name,
        "valid_response_sha256": valid.get("response_sha256"),
        "valid_checks": valid_check,
        "negative_cases": rows,
        "checks": checks,
        "all_passed": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow", type=Path, default=DEFAULT_FLOW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run(args.flow.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_passed": report["all_passed"], "checks": report["checks"]}, ensure_ascii=False))
    print(f"report: {args.output}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
