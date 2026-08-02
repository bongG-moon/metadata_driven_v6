from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from flow_builder_support import (
    DEFAULT_ASSET_MANIFEST,
    BuildContractError,
    validate_runtime_assets,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the pinned Langflow 1.9.2 Language Model source, LFX index, Python, and package tuple."
    )
    parser.add_argument("--asset-manifest", type=Path, default=DEFAULT_ASSET_MANIFEST)
    parser.add_argument("--strict", action="store_true", help="Require Python 3.12 and the exact package tuple.")
    parser.add_argument(
        "--require-explicit-component-index",
        action="store_true",
        help="Require LANGFLOW_COMPONENT_INDEX_PATH instead of resolving the exact installed LFX asset.",
    )
    args = parser.parse_args()
    try:
        if args.require_explicit_component_index and not str(
            os.getenv("LANGFLOW_COMPONENT_INDEX_PATH") or ""
        ).strip():
            raise BuildContractError(
                "LANGFLOW_COMPONENT_INDEX_PATH is required by --require-explicit-component-index"
            )
        assets = validate_runtime_assets(
            args.asset_manifest.resolve(), strict_versions=args.strict
        )
    except (BuildContractError, Exception) as exc:
        # Keep a single sanitized error surface. No environment values or credentials are printed.
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(
        json.dumps(
            {
                "status": "ok",
                "strict_versions": bool(args.strict),
                "component_index_resolution": (
                    "LANGFLOW_COMPONENT_INDEX_PATH"
                    if str(os.getenv("LANGFLOW_COMPONENT_INDEX_PATH") or "").strip()
                    else "installed_exact_lfx"
                ),
                "runtime_assets": assets.manifest_projection(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
