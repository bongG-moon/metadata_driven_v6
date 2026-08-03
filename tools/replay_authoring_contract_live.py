"""Replay the worker-visible metadata authoring flows against one MongoDB database.

The script backs up and clears only the three configured v6 metadata
collections, invokes the same generated standalone nodes and Gemini model as
the import-ready flows, validates exact stored item identities, and restores
the backup automatically if any step fails.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bson import json_util
from pymongo import MongoClient

from gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    GeminiJsonModel,
    assert_secret_absent,
    load_dotenv_values,
    resolve_gemini_api_key,
)
from validate_three_collection_authoring_live import (
    COLLECTIONS,
    _MessageGemini,
    _component,
    _simple_authoring_context,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "metadata" / "authoring" / "v6_contract_validation"
DEFAULT_REPORT = ROOT / "validation_outputs" / "authoring_contract_live_replay.json"

SEQUENCE = (
    ("main_filter_oper_name", "main_filter", "01_main_filter_oper_name.txt"),
    ("domain_profile", "domain", "02_domain_profile.txt"),
    ("domain_group_dp", "domain", "03_domain_group_dp.txt"),
    ("dataset_process_status", "dataset", "04_dataset_process_status.txt"),
)


def _backup(database: Any, output: Path) -> dict[str, list[dict[str, Any]]]:
    snapshot = {
        kind: list(database[name].find({}))
        for kind, name in COLLECTIONS.items()
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(output, "wt", encoding="utf-8") as handle:
        handle.write(json_util.dumps(snapshot, ensure_ascii=False, indent=2))
    return snapshot


def _restore(database: Any, snapshot: dict[str, list[dict[str, Any]]]) -> None:
    for kind, name in COLLECTIONS.items():
        database[name].delete_many({})
        rows = snapshot.get(kind) or []
        if rows:
            database[name].insert_many(rows, ordered=True)


def _counts(database: Any) -> dict[str, int]:
    return {
        kind: int(database[name].count_documents({}))
        for kind, name in COLLECTIONS.items()
    }


def _run_step(
    *,
    label: str,
    kind: str,
    source_text: str,
    model: _MessageGemini,
    mongo_uri: str,
    database_name: str,
) -> dict[str, Any]:
    context = _simple_authoring_context(kind=kind, source_text=source_text, model=model)
    engine = _component("metadata_authoring/02_simple_metadata_authoring_engine.py")()
    engine.authoring_context = context
    engine.mode = "save"
    engine.mongo_uri = mongo_uri
    engine.mongo_database = database_name
    engine.domain_collection = COLLECTIONS["domain"]
    engine.table_collection = COLLECTIONS["table_catalog"]
    engine.main_filter_collection = COLLECTIONS["main_filter"]
    engine.mongo_timeout_ms = 10000
    response = engine.run_authoring().data
    if response.get("status") != "ok" or response.get("stage") != "committed":
        raise RuntimeError(
            json.dumps(
                {
                    "label": label,
                    "status": response.get("status"),
                    "stage": response.get("stage"),
                    "error": response.get("error"),
                    "clarification": response.get("clarification"),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    return {
        "label": label,
        "kind": kind,
        "stage": response.get("stage"),
        "activation_status": response.get("activation_status"),
        "ready_sections": response.get("ready_sections"),
        "missing_sections": response.get("missing_sections"),
        "revision": response.get("revision"),
        "draft_llm_calls": (response.get("llm_usage") or {}).get("draft_llm_calls"),
    }


def run(*, env_file: Path, report_path: Path, backup_dir: Path) -> dict[str, Any]:
    env = load_dotenv_values(env_file)
    api_key = resolve_gemini_api_key(env_file)
    mongo_uri = str(os.getenv("MONGODB_URI") or env.get("MONGODB_URI") or "").strip()
    database_name = str(
        os.getenv("MONGODB_DATABASE") or env.get("MONGODB_DATABASE") or ""
    ).strip()
    if not mongo_uri or not database_name:
        raise RuntimeError("mongodb_configuration_missing")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = backup_dir / f"v6_metadata_before_replay_{timestamp}.json.gz"
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    database = client[database_name]
    snapshot: dict[str, list[dict[str, Any]]] | None = None
    try:
        before = _counts(database)
        snapshot = _backup(database, backup_path)
        for name in COLLECTIONS.values():
            database[name].delete_many({})
        cleared = _counts(database)
        if any(cleared.values()):
            raise RuntimeError("metadata_collection_clear_failed")

        delegate = GeminiJsonModel(
            api_key=api_key,
            model=DEFAULT_GEMINI_MODEL,
            timeout_seconds=int(env.get("LLM_TIMEOUT_SECONDS") or 90),
            max_output_tokens=32768,
        )
        model = _MessageGemini(delegate)
        steps = []
        for label, kind, filename in SEQUENCE:
            source_text = (INPUT_DIR / filename).read_text(encoding="utf-8").strip()
            steps.append(
                _run_step(
                    label=label,
                    kind=kind,
                    source_text=source_text,
                    model=model,
                    mongo_uri=mongo_uri,
                    database_name=database_name,
                )
            )
            steps[-1]["counts_after"] = _counts(database)

        expected_ids = {
            "main_filter": ["main_filter:aliases:field:OPER_NAME"],
            "domain": sorted([
                "domain:profile:default",
                "domain:entity_groups:DP",
                "domain:aliases:entity_group:DP",
            ]),
            "table_catalog": ["table_catalog:datasets:process_status"],
        }
        stored_ids = {
            kind: sorted(str(row["_id"]) for row in database[name].find({}, {"_id": 1}))
            for kind, name in COLLECTIONS.items()
        }
        if stored_ids != expected_ids:
            raise RuntimeError(
                json.dumps(
                    {"code": "stored_item_identity_mismatch", "expected": expected_ids, "actual": stored_ids},
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
        if database[COLLECTIONS["domain"]].find_one(
            {"_id": "domain:aliases:field:OPER_NAME"}
        ):
            raise RuntimeError("domain_field_alias_must_not_be_created")

        group = database[COLLECTIONS["domain"]].find_one(
            {"_id": "domain:entity_groups:DP"}
        ) or {}
        group_payload = group.get("payload") or {}
        if (
            group_payload.get("target_field") != "OPER_NAME"
            or group_payload.get("members") != ["AA", "BB", "CC"]
        ):
            raise RuntimeError("dp_group_payload_mismatch")

        loader = _component("data_analysis/domain_bundle_loader.py")()
        loader.mongo_uri = mongo_uri
        loader.mongo_database = database_name
        loader.mongo_timeout_ms = 10000
        loaded = loader.load_bundle().data
        if loaded.get("ok") is not True:
            raise RuntimeError(json.dumps(loaded.get("error") or {}, ensure_ascii=False))
        runtime_bundle = loaded.get("domain_bundle") or {}
        report = {
            "status": "ok",
            "contract_version": "metadata.authoring.live-replay.v1",
            "model": DEFAULT_GEMINI_MODEL,
            "database": database_name,
            "collections": COLLECTIONS,
            "backup_path": str(backup_path),
            "before_counts": before,
            "after_counts": _counts(database),
            "steps": steps,
            "stored_ids": stored_ids,
            "dp_group": {
                "target_field": group_payload.get("target_field"),
                "members": group_payload.get("members"),
                "aliases": group_payload.get("aliases"),
            },
            "loader": {
                "ok": loaded.get("ok"),
                "domain_id": runtime_bundle.get("domain_id"),
                "environment": runtime_bundle.get("environment"),
                "source_mode": runtime_bundle.get("source_mode"),
                "catalog_sha256": runtime_bundle.get("catalog_sha256"),
            },
            "llm": delegate.evidence(),
        }
        assert_secret_absent(report, api_key)
        assert_secret_absent(report, mongo_uri)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return report
    except Exception:
        if snapshot is not None:
            _restore(database, snapshot)
        raise
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=ROOT / "validation_outputs" / "mongodb_backups",
    )
    args = parser.parse_args()
    try:
        report = run(
            env_file=args.env_file.resolve(),
            report_path=args.report.resolve(),
            backup_dir=args.backup_dir.resolve(),
        )
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
