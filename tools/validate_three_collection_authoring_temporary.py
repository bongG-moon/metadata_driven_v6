"""Run live three-collection validation against a temporarily cleared validation DB.

Only the three configured v6 validation collections are touched.  Their full
BSON snapshot is written before deletion and restored in ``finally`` after
success or failure, so repeated contract validations do not inherit stale
documents and do not leave test metadata behind.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import json
import os
from pathlib import Path
from typing import Any

from bson import json_util
from pymongo import MongoClient

from gemini_validation_support import load_dotenv_values
from validate_three_collection_authoring_live import COLLECTIONS, ROOT, run


def _snapshot(database: Any) -> dict[str, list[dict[str, Any]]]:
    return {
        kind: list(database[name].find({}))
        for kind, name in COLLECTIONS.items()
    }


def _restore(database: Any, snapshot: dict[str, list[dict[str, Any]]]) -> None:
    for kind, name in COLLECTIONS.items():
        database[name].delete_many({})
        rows = snapshot.get(kind) or []
        if rows:
            database[name].insert_many(rows, ordered=True)


def run_temporary(*, env_file: Path, input_dir: Path, output: Path, backup_dir: Path) -> dict[str, Any]:
    env = load_dotenv_values(env_file)
    mongo_uri = str(os.getenv("MONGODB_URI") or env.get("MONGODB_URI") or "").strip()
    operational_database = str(
        os.getenv("MONGODB_DATABASE") or env.get("MONGODB_DATABASE") or "datagov"
    ).strip()
    validation_database = str(
        os.getenv("MONGODB_VALIDATION_DATABASE")
        or env.get("MONGODB_VALIDATION_DATABASE")
        or "datagov_v6_validation"
    ).strip()
    if not mongo_uri:
        raise RuntimeError("mongodb_uri_not_configured")
    if not validation_database or validation_database == operational_database:
        raise RuntimeError("temporary_validation_database_must_be_isolated")

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    database = client[validation_database]
    snapshot: dict[str, list[dict[str, Any]]] | None = None
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = backup_dir / f"v6_validation_before_temporary_run_{timestamp}.json.gz"
    try:
        snapshot = _snapshot(database)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(backup_path, "wt", encoding="utf-8") as handle:
            handle.write(json_util.dumps(snapshot, ensure_ascii=False, indent=2))
        for name in COLLECTIONS.values():
            database[name].delete_many({})
        if any(database[name].count_documents({}) for name in COLLECTIONS.values()):
            raise RuntimeError("temporary_validation_collection_clear_failed")

        report = run(
            env_file=env_file,
            input_dir=input_dir,
            output=output,
            database_name=validation_database,
            allow_operational_database=False,
        )
        report["temporary_validation"] = {
            "backup_path": backup_path.relative_to(ROOT).as_posix(),
            "previous_item_counts": {
                kind: len(rows) for kind, rows in snapshot.items()
            },
            "restore_policy": "always",
        }
        output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return report
    finally:
        if snapshot is not None:
            _restore(database, snapshot)
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs/three_collection_temporary_validation.json",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=ROOT / "validation_outputs/mongodb_backups",
    )
    args = parser.parse_args()
    report = run_temporary(
        env_file=args.env_file.resolve(),
        input_dir=args.input_dir.resolve(),
        output=args.output.resolve(),
        backup_dir=args.backup_dir.resolve(),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
