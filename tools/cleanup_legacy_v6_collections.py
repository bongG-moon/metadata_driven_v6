"""Remove only obsolete pre-three-collection v6 MongoDB collections.

The command is dry-run by default.  ``--execute`` first proves that the
current three-collection release can be loaded and then drops the exact closed
allowlist below.  Session and result collections are always protected.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from pymongo import MongoClient

from gemini_validation_support import load_dotenv_values


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEGACY_COLLECTIONS = (
    "agent_v6_authoring_audit",
    "agent_v6_authoring_sources",
    "agent_v6_dataset_catalog",
    "agent_v6_filter_catalog",
    "agent_v6_metadata_active",
    "agent_v6_metadata_bundles",
    "agent_v6_pending_writes",
    "agent_v6_semantic_catalog",
)
PROTECTED_COLLECTIONS = (
    "agent_v6_domain_metadata",
    "agent_v6_table_catalog",
    "agent_v6_main_filter",
    "agent_v6_session_state",
    "agent_v6_result_store",
)


def run(*, env_file: Path, database_name: str, execute: bool) -> dict[str, Any]:
    from reference_runtime.metadata_collections import (
        load_available_domain_package_from_three_collections,
    )

    env = load_dotenv_values(env_file)
    uri = str(os.getenv("MONGODB_URI") or env.get("MONGODB_URI") or "").strip()
    if not uri:
        raise RuntimeError("mongodb_uri_not_configured")
    database = str(
        database_name
        or os.getenv("MONGODB_DATABASE")
        or env.get("MONGODB_DATABASE")
        or "datagov"
    ).strip()

    client = MongoClient(uri, serverSelectionTimeoutMS=10_000)
    try:
        client.admin.command("ping")
        db = client[database]
        before_names = set(db.list_collection_names())
        missing_protected = [name for name in PROTECTED_COLLECTIONS if name not in before_names]
        if missing_protected:
            raise RuntimeError(f"protected_collections_missing:{','.join(missing_protected)}")

        package = load_available_domain_package_from_three_collections(db)
        existing_legacy = [name for name in LEGACY_COLLECTIONS if name in before_names]
        before_counts = {
            name: int(db[name].estimated_document_count()) for name in existing_legacy
        }

        dropped: list[str] = []
        if execute:
            for name in existing_legacy:
                db.drop_collection(name)
                dropped.append(name)

        after_names = set(db.list_collection_names())
        if execute and any(name in after_names for name in dropped):
            raise RuntimeError("legacy_collection_drop_incomplete")
        if any(name not in after_names for name in PROTECTED_COLLECTIONS):
            raise RuntimeError("protected_collection_changed")

        return {
            "contract_version": "metadata.legacy-collection-cleanup.v1",
            "status": "ok",
            "mode": "execute" if execute else "dry_run",
            "database": database,
            "domain_id": package["domain_id"],
            "environment": package["environment"],
            "revision": package["revision"],
            "legacy_candidates": list(LEGACY_COLLECTIONS),
            "existing_legacy_before": existing_legacy,
            "document_counts_before": before_counts,
            "dropped": dropped,
            "protected_present_after": [
                name for name in PROTECTED_COLLECTIONS if name in after_names
            ],
            "remaining_agent_v6_collections": sorted(
                name for name in after_names if name.startswith("agent_v6_")
            ),
        }
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--database", default="")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    report = run(
        env_file=args.env_file.resolve(),
        database_name=str(args.database or "").strip(),
        execute=bool(args.execute),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
