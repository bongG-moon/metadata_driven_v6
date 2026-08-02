"""Validate bounded domain prompt overlays and declarative function metadata."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "validation_outputs" / "domain_extension_safety.json"
ALLOWED_SPECIALIZED_KEYS = {
    "function_id",
    "version",
    "execution_mode",
    "implementation_sha256",
    "input_schema",
    "output_schema",
    "required_fields",
    "limits",
    "failure_policy",
    "aliases",
    "call_template",
}
FORBIDDEN_EXECUTABLE_KEYS = {
    "code",
    "python",
    "pandas",
    "script",
    "sql",
    "query",
    "url",
    "endpoint",
    "expression",
    "callable",
    "module",
    "import",
    "source",
}
FORBIDDEN_EXECUTABLE_TEXT = re.compile(
    r"(?:\beval\s*\(|\bexec\s*\(|\bimport\s+[A-Za-z_]|\bfrom\s+[A-Za-z_].*\bimport\b|"
    r"\bpandas\b|\bpd\s*\.|\bselect\s+.+\s+from\b|https?://)",
    re.IGNORECASE | re.DOTALL,
)


def _walk_pairs(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key), nested
            yield from _walk_pairs(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_pairs(nested)


def validate_specialized_functions(catalog: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    entries = catalog.get("specialized_functions") or []
    if not isinstance(entries, list):
        return ["specialized_functions_not_list"]
    for index, entry in enumerate(entries):
        prefix = f"specialized_functions[{index}]"
        if not isinstance(entry, dict):
            failures.append(prefix + ":not_object")
            continue
        unexpected = sorted(set(entry) - ALLOWED_SPECIALIZED_KEYS)
        if unexpected:
            failures.append(prefix + ":unexpected_keys:" + ",".join(unexpected))
        if entry.get("execution_mode") != "registered_standalone":
            failures.append(prefix + ":execution_mode")
        digest = str(entry.get("implementation_sha256") or "")
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            failures.append(prefix + ":implementation_sha256")
        for key, value in _walk_pairs(entry):
            if key.casefold() in FORBIDDEN_EXECUTABLE_KEYS:
                failures.append(prefix + ":executable_key:" + key)
            if isinstance(value, str) and FORBIDDEN_EXECUTABLE_TEXT.search(value):
                failures.append(prefix + ":executable_text")
    return sorted(set(failures))


def run(root: Path = ROOT) -> dict[str, Any]:
    package_paths = sorted((root / "metadata" / "domain_packs").glob("*/compiled/domain_package.json"))
    packages: list[dict[str, Any]] = []
    failures: list[str] = []
    for path in package_paths:
        package = json.loads(path.read_text(encoding="utf-8"))
        catalog = package.get("runtime_catalog") if isinstance(package.get("runtime_catalog"), dict) else {}
        prompt_extensions = catalog.get("prompt_extensions") if isinstance(catalog.get("prompt_extensions"), dict) else {}
        specialized_failures = validate_specialized_functions(catalog)
        row = {
            "domain_id": package.get("domain_id"),
            "environment": package.get("environment"),
            "catalog_contract_version": catalog.get("contract_version"),
            "intent_extension_utf8_bytes": len(str(prompt_extensions.get("intent") or "").encode("utf-8")),
            "answer_extension_utf8_bytes": len(str(prompt_extensions.get("answer") or "").encode("utf-8")),
            "specialized_function_count": len(catalog.get("specialized_functions") or []),
            "specialized_function_failures": specialized_failures,
            "passed": not specialized_failures,
        }
        packages.append(row)
        failures.extend(f"{path.parent.parent.name}:{item}" for item in specialized_failures)

    intent_source = (root / "langflow_components" / "data_analysis" / "intent_prompt_context_builder.py").read_text(encoding="utf-8")
    answer_source = (root / "langflow_components" / "data_analysis" / "answer_facts_context_builder.py").read_text(encoding="utf-8")
    composer_source = (root / "langflow_components" / "shared" / "01_prompt_bundle_composer.py").read_text(encoding="utf-8")
    invoker_source = (root / "langflow_components" / "shared" / "02_conditional_llm_invoker.py").read_text(encoding="utf-8")
    registry_source = (root / "reference_runtime" / "registered_functions.py").read_text(encoding="utf-8")
    planner_source = (root / "reference_runtime" / "generic_v2_planner.py").read_text(encoding="utf-8")
    executor_source = (root / "reference_runtime" / "typed_executor.py").read_text(encoding="utf-8")
    component_checks = {
        "intent_reads_catalog_prompt_extension": "prompt_extensions" in intent_source and "intent" in intent_source,
        "intent_extension_utf8_bounded": bool(re.search(r"encode\(\"utf-8\"\)\[:\d+\]", intent_source)),
        "answer_reads_catalog_prompt_extension": "prompt_extensions" in answer_source and "answer" in answer_source,
        "answer_extension_utf8_bounded": bool(re.search(r"encode\(\"utf-8\"\)\[:\d+\]", answer_source)),
        "prompt_authority_segments_are_separate": all(
            token in composer_source for token in ('"authority": "system"', '"authority": "domain_policy"', '"authority": "untrusted_data"')
        ),
        "conditional_invoker_has_zero_retry_contract": "automatic_retry_count\": 0" in invoker_source
        and "llm_calls\": 1" in invoker_source,
        "planner_emits_registered_call_only": "build_registered_call_operation" in planner_source
        and "dispatch_registered_call" not in planner_source,
        "executor_dispatches_static_registry": "dispatch_registered_call" in executor_source,
        "registry_is_static_allowlist": "_REGISTRY" in registry_source
        and "implementation_sha256" in registry_source,
        "executor_has_no_python_eval_path": not re.search(r"\b(?:eval|exec)\s*\(", executor_source),
        "registry_has_no_dynamic_import_path": not re.search(r"\b(?:eval|exec|__import__)\s*\(", registry_source),
    }
    failures.extend(key for key, passed in component_checks.items() if not passed)
    return {
        "contract_version": "domain.extension-safety.validation.v1",
        "package_count": len(packages),
        "packages": packages,
        "component_checks": component_checks,
        "failures": sorted(failures),
        "all_passed": not failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("package_count", "all_passed", "failures")}, ensure_ascii=False))
    print(f"report: {args.output}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
