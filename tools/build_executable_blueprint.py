"""Build or verify an externally pinned executable authoring blueprint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.authoring_blueprint import build_executable_blueprint
from reference_runtime.authoring_source_manifest import extract_authoring_source_manifest


DEFAULT_SOURCE = ROOT / "validation" / "order_sales_metadata_input.txt"
DEFAULT_DRAFT = ROOT / "metadata" / "domain_packs" / "order_sales" / "authoring_draft.json"
DEFAULT_OUTPUT = ROOT / "metadata" / "domain_packs" / "order_sales" / "trusted_executable_blueprint.json"
DEFAULT_PIN_OUTPUT = ROOT / "metadata" / "domain_packs" / "order_sales" / "trusted_executable_blueprint.sha256"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _render_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_or_check(path: Path, expected: str, *, check: bool) -> None:
    if check:
        actual = path.read_text(encoding="utf-8") if path.is_file() else None
        if actual != expected:
            raise SystemExit(f"stale or missing generated artifact: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--domain-id", default="order_sales")
    parser.add_argument("--environment", default="test")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pin-output", type=Path, default=DEFAULT_PIN_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source_text = args.source.read_text(encoding="utf-8")
    manifest = extract_authoring_source_manifest(source_text)
    blueprint = build_executable_blueprint(
        _json(args.draft),
        domain_id=args.domain_id,
        environment=args.environment,
        source_manifest=manifest,
    )
    _write_or_check(args.output, _render_json(blueprint), check=args.check)
    _write_or_check(args.pin_output, blueprint["blueprint_sha256"] + "\n", check=args.check)
    print(
        json.dumps(
            {
                "status": "verified" if args.check else "generated",
                "domain_id": blueprint["domain_id"],
                "environment": blueprint["environment"],
                "blueprint_sha256": blueprint["blueprint_sha256"],
                "executable_sha256": blueprint["executable_sha256"],
                "source_manifest_sha256": blueprint["source_manifest_sha256"],
                "output": str(args.output),
                "pin_output": str(args.pin_output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
