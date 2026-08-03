"""Repair v6 dataset identity and semantic types from stored worker text.

The command is dry-run by default.  ``--apply`` writes only exact item IDs in
the configured table catalog collection, after backing up all three metadata
collections and compiling the complete candidate runtime package in memory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bson import json_util
from dotenv import load_dotenv
from lfx.custom.eval import eval_custom_component_code
from pymongo import DeleteOne, MongoClient, ReplaceOne

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.metadata_collections import (
    assemble_domain_package_from_items,
    load_available_domain_package_from_three_collections,
)


COLLECTION_PATTERN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$")


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--mongo-database", default="")
    parser.add_argument("--domain-collection", default="agent_v6_domain_metadata")
    parser.add_argument("--table-collection", default="agent_v6_table_catalog")
    parser.add_argument("--main-filter-collection", default="agent_v6_main_filter")
    parser.add_argument("--mongo-timeout-ms", type=int, default=5000)
    parser.add_argument("--backup-path", default="")
    return parser.parse_args()


def _safe_collection(value: str) -> str:
    name = str(value or "").strip()
    if COLLECTION_PATTERN.fullmatch(name) is None or name.casefold().startswith("system."):
        raise ValueError(f"unsafe collection name: {name!r}")
    return name


def _authoring_globals() -> dict[str, Any]:
    source = (
        ROOT / "langflow_components" / "metadata_authoring" / "00_metadata_authoring_engine.py"
    ).read_text(encoding="utf-8")
    component = eval_custom_component_code(source)
    return component._prepare_v2.__globals__


def _repair_document(document: dict[str, Any], helpers: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    item = deepcopy(document)
    if item.get("section") != "datasets" or not isinstance(item.get("payload"), dict):
        raise ValueError(f"unsupported table catalog item: {item.get('_id')!r}")
    payload = item["payload"]
    fields = payload.get("fields")
    if not isinstance(fields, dict) or not fields:
        raise ValueError(f"dataset has no fields: {item.get('_id')!r}")
    natural_text = str(item.get("natural_text") or "")
    old_key = str(item.get("key") or "")
    new_key = str(helpers["_freeform_dataset_id"](natural_text) or old_key)
    family = str(helpers["_freeform_dataset_family"](natural_text, new_key) or new_key)
    source_type = str(
        helpers["_freeform_source_type"](natural_text)
        or payload.get("source_type")
        or payload.get("source_adapter")
        or ""
    ).casefold()
    if not new_key or not family or not source_type:
        raise ValueError(f"dataset identity is incomplete: {old_key!r}")

    changes: list[dict[str, str]] = []
    payload["family"] = family
    payload["source_type"] = source_type
    payload["source_adapter"] = source_type
    for field_id, binding in fields.items():
        if not isinstance(binding, dict):
            raise ValueError(f"invalid field binding: {old_key}.{field_id}")
        old_type = str(binding.get("semantic_type") or "")
        new_type = str(
            helpers["_freeform_field_semantic_type"](
                field_id,
                binding.get("physical_column") or field_id,
                natural_text,
                old_type,
            )
        )
        if old_type != new_type:
            changes.append({"field": str(field_id), "from": old_type, "to": new_type})
        binding["semantic_type"] = new_type
        binding["coercion"] = helpers["_default_coercion"](new_type)

    if new_key != old_key:
        payload["config_ref"] = f"config:{source_type}:{new_key}@1"
        payload["query_ref"] = f"query:{new_key}@1"
        item["_id"] = f"table_catalog:datasets:{new_key}"
        item["key"] = new_key
    item["updated_at"] = datetime.now(timezone.utc).isoformat()
    return item, {
        "from": old_key,
        "to": new_key,
        "changed_type_count": len(changes),
        "changed_types": changes,
    }


def _backup_path(raw: str) -> Path:
    if raw:
        value = Path(raw).expanduser().resolve()
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        value = (
            ROOT
            / "validation_outputs"
            / "mongodb_backups"
            / f"dataset_catalog_semantics_{stamp}.json"
        ).resolve()
    if ROOT.resolve() not in value.parents:
        raise ValueError("backup path must stay inside the repository")
    return value


def main() -> int:
    args = _args()
    load_dotenv(ROOT / ".env")
    uri = str(os.getenv("MONGODB_URI") or "").strip()
    if not uri:
        raise ValueError("MONGODB_URI is required")
    database_name = str(args.mongo_database or os.getenv("MONGODB_DATABASE") or "datagov").strip()
    names = {
        "domain": _safe_collection(args.domain_collection),
        "table_catalog": _safe_collection(args.table_collection),
        "main_filter": _safe_collection(args.main_filter_collection),
    }
    if len(set(names.values())) != 3:
        raise ValueError("the three metadata collections must be distinct")

    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=max(500, min(int(args.mongo_timeout_ms), 30000)),
    )
    database = client[database_name]
    try:
        current = {
            kind: [dict(item) for item in database[name].find({})]
            for kind, name in names.items()
        }
        helpers = _authoring_globals()
        repaired: list[dict[str, Any]] = []
        changes: list[dict[str, Any]] = []
        for document in current["table_catalog"]:
            candidate, evidence = _repair_document(document, helpers)
            repaired.append(candidate)
            changes.append(evidence)
        candidate_ids = [str(item.get("_id")) for item in repaired]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("repaired dataset IDs are not unique")

        candidate_documents = {
            "domain": current["domain"],
            "table_catalog": repaired,
            "main_filter": current["main_filter"],
        }
        activation: dict[str, Any] = {}
        expected = assemble_domain_package_from_items(
            candidate_documents,
            alias_activation_out=activation,
        )
        stale_ids = sorted(
            {str(item.get("_id")) for item in current["table_catalog"]}
            - set(candidate_ids)
        )

        backup = _backup_path(args.backup_path)
        result = {
            "status": "validated",
            "applied": False,
            "database": database_name,
            "collections": names,
            "changes": changes,
            "stale_ids": stale_ids,
            "dataset_keys": sorted(expected["runtime_catalog"]["datasets"]),
            "deferred_alias_count": int(activation.get("deferred_count") or 0),
            "backup_path": str(backup),
        }
        if not args.apply:
            result["backup_path"] = ""
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(
            json_util.dumps(
                {
                    "created_at": datetime.now(timezone.utc),
                    "database": database_name,
                    "collections": names,
                    "documents": current,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        with client.start_session() as session:
            with session.start_transaction():
                transaction_current = [
                    dict(item)
                    for item in database[names["table_catalog"]].find({}, session=session)
                ]
                if json_util.dumps(transaction_current, sort_keys=True) != json_util.dumps(
                    current["table_catalog"], sort_keys=True
                ):
                    raise RuntimeError("table catalog changed after validation")
                operations = [
                    ReplaceOne({"_id": item["_id"]}, deepcopy(item), upsert=True)
                    for item in repaired
                ]
                operations.extend(DeleteOne({"_id": item_id}) for item_id in stale_ids)
                if operations:
                    database[names["table_catalog"]].bulk_write(
                        operations,
                        ordered=True,
                        session=session,
                    )
                loaded = load_available_domain_package_from_three_collections(
                    database,
                    domain_collection=names["domain"],
                    table_collection=names["table_catalog"],
                    main_filter_collection=names["main_filter"],
                    session=session,
                )
                if loaded["runtime_catalog"] != expected["runtime_catalog"]:
                    raise RuntimeError("post-write runtime catalog differs from validated candidate")
        result["status"] = "applied"
        result["applied"] = True
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
