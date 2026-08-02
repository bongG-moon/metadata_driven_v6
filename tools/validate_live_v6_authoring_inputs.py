"""Validate the four v6 natural-language authoring inputs without calling a model."""

from __future__ import annotations

import argparse
import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "metadata" / "authoring" / "v6_inputs"
INPUTS = {
    "domain": INPUT_DIR / "domain_v6.txt",
    "dataset": INPUT_DIR / "dataset_v6.txt",
    "main_filter": INPUT_DIR / "main_filter_v6.txt",
    "domain_policy": INPUT_DIR / "domain_policy_v6.txt",
}
LEGACY_LINEAGE = {
    "domain": ROOT / "metadata" / "authoring" / "domain" / "domain_knowledge.txt",
    "dataset": ROOT / "metadata" / "authoring" / "table_catalog" / "data_catalog.txt",
    "main_filter": ROOT / "metadata" / "authoring" / "main_filters" / "main_variable.txt",
}
_SECRET_PATTERNS = (
    re.compile(r"mongodb(?:\+srv)?://", re.IGNORECASE),
    re.compile(r"(?:gemini|google|langflow)_api_key\s*[=:]", re.IGNORECASE),
    re.compile(r"x-goog-api-key\s*[=:]", re.IGNORECASE),
)
_POLICY_SECTIONS = (
    "[의도 분석 특화 프롬프트]",
    "[답변 생성 특화 프롬프트]",
    "[출력 표시 정책]",
    "[등록형 함수 정책]",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _evidence(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    text = _text(path)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "byte_count": len(payload),
        "line_count": len(text.splitlines()),
        "content_sha256": sha256(payload).hexdigest(),
        "nonempty": bool(text.strip()),
        "secret_literal_absent": not any(pattern.search(text) for pattern in _SECRET_PATTERNS),
    }


def run() -> dict[str, Any]:
    rows: dict[str, dict[str, Any]] = {}
    for kind, path in INPUTS.items():
        row = _evidence(path)
        if kind in LEGACY_LINEAGE:
            source = LEGACY_LINEAGE[kind]
            source_bytes = source.read_bytes()
            row.update(
                {
                    "lineage_path": source.relative_to(ROOT).as_posix(),
                    "lineage_sha256": sha256(source_bytes).hexdigest(),
                    "lineage_source_present": source.is_file(),
                    # v6 is an operator-maintained free-form rewrite. Exact
                    # line equality would reintroduce a hidden authoring
                    # grammar and reject harmless changes in wording/order.
                    # Semantic adequacy is proven by the live
                    # Gemini -> typed IR -> compiler completeness gate.
                    "lineage_relation": "freeform_operator_rewrite",
                    "freeform_rewrite_allowed": True,
                    "exact_line_equality_required": False,
                    "content_differs_from_lineage": source_bytes
                    != path.read_bytes(),
                }
            )
        else:
            policy_text = _text(path)
            row["required_policy_sections_present"] = all(
                section in policy_text for section in _POLICY_SECTIONS
            )
            row["raw_python_registration_prohibited"] = (
                "raw Python 코드" in policy_text
                and "eval" in policy_text
                and "exec" in policy_text
                and "unsupported_operation" in policy_text
            )
        row["passed"] = all(
            value is True
            for key, value in row.items()
            if key
            in {
                "nonempty",
                "secret_literal_absent",
                "lineage_source_present",
                "freeform_rewrite_allowed",
                "required_policy_sections_present",
                "raw_python_registration_prohibited",
            }
        )
        rows[kind] = row

    return {
        "contract_version": "metadata.v6.authoring-input.validation.v1",
        "input_count": len(rows),
        "expected_input_count": 4,
        "raw_text_persisted_in_report": False,
        "rows": rows,
        "all_passed": len(rows) == 4 and all(row["passed"] for row in rows.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs" / "v6_authoring_inputs.json",
    )
    args = parser.parse_args()
    report = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "input_count": report["input_count"],
                "all_passed": report["all_passed"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
