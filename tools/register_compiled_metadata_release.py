"""Register a reviewed package as simple natural-language MongoDB items.

The historical filename is kept for existing commands. No release document,
manifest, or persisted hash is created by this implementation.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from pymongo import MongoClient

from gemini_validation_support import assert_secret_absent, load_dotenv_values


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DEFAULT_PACKAGE = ROOT / "metadata/domain_packs/manufacturing/compiled/domain_package.json"
DEFAULT_INPUT_DIR = ROOT / "metadata/authoring/v5_import"
COLLECTIONS = {
    "domain": "agent_v6_domain_metadata",
    "table_catalog": "agent_v6_table_catalog",
    "main_filter": "agent_v6_main_filter",
}
V4_COLLECTIONS = (
    "agent_v4_domain_items",
    "agent_v4_table_catalog_items",
    "agent_v4_main_flow_filters",
)
ALLOWED_ITEM_FIELDS = {"_id", "section", "key", "natural_text", "payload", "updated_at"}


def _count(value: Any) -> int:
    return len(value) if isinstance(value, (dict, list)) else 0


def _legacy_natural_texts(database: Any) -> dict[str, str]:
    """Reuse worker-entered V4 text when an item key can be matched."""

    result: dict[str, str] = {}
    for collection_name in V4_COLLECTIONS:
        for document in database[collection_name].find({}):
            trace = document.get("registration_trace") if isinstance(document.get("registration_trace"), dict) else {}
            text = str(trace.get("raw_text") or "").strip()
            if not text:
                continue
            markers = [str(document.get("_id") or "")]
            if collection_name == V4_COLLECTIONS[0]:
                section = str(document.get("section") or "")
                key = str(document.get("key") or "")
                markers.extend([key, f"{section}:{key}"])
            elif collection_name == V4_COLLECTIONS[1]:
                markers.append(str(document.get("dataset_key") or ""))
            else:
                markers.append(str(document.get("filter_key") or ""))
            for marker in markers:
                if marker:
                    result.setdefault(marker, text)
    return result


def run(
    *,
    env_file: Path,
    package_path: Path,
    input_dir: Path,
    database_name: str | None,
    allow_operational_database: bool,
    allow_replace: bool,
    output: Path,
) -> dict[str, Any]:
    from reference_runtime.domain_packages import validate_domain_package
    from reference_runtime.metadata_collections import (
        load_available_domain_package_from_three_collections,
        make_metadata_item_documents,
        replace_metadata_items,
    )

    env = load_dotenv_values(env_file)
    mongo_uri = str(os.getenv("MONGODB_URI") or env.get("MONGODB_URI") or "").strip()
    if not mongo_uri:
        raise RuntimeError("mongodb_uri_not_configured")
    operational_database = str(
        os.getenv("MONGODB_DATABASE") or env.get("MONGODB_DATABASE") or "datagov"
    ).strip()
    target_database = str(database_name or operational_database).strip()
    if target_database == operational_database and not allow_operational_database:
        raise RuntimeError("operational_database_requires_explicit_opt_in")

    package = validate_domain_package(json.loads(package_path.read_text(encoding="utf-8")))
    source_texts = {
        "domain": (input_dir / "domain_v6.txt").read_text(encoding="utf-8"),
        "table_catalog": (input_dir / "dataset_v6.txt").read_text(encoding="utf-8"),
        "main_filter": (input_dir / "main_filter_v6.txt").read_text(encoding="utf-8"),
    }

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    try:
        database = client[target_database]
        client.admin.command("ping")
        existing_counts = {kind: database[name].count_documents({}) for kind, name in COLLECTIONS.items()}
        if any(existing_counts.values()) and not allow_replace:
            raise RuntimeError("metadata_items_exist_use_allow_replace")
        documents = make_metadata_item_documents(
            package,
            source_texts,
            legacy_natural_texts=_legacy_natural_texts(database),
        )
        with client.start_session() as session:
            with session.start_transaction():
                replace_metadata_items(database, documents, session=session)
                loaded = load_available_domain_package_from_three_collections(database, session=session)
                if loaded["runtime_catalog"] != package["runtime_catalog"]:
                    raise RuntimeError("published_runtime_catalog_round_trip_mismatch")

        auto_loaded = load_available_domain_package_from_three_collections(database)
        if auto_loaded["runtime_catalog"] != package["runtime_catalog"]:
            raise RuntimeError("available_loader_runtime_catalog_mismatch")
        stored = {
            kind: list(database[name].find({}))
            for kind, name in COLLECTIONS.items()
        }
    finally:
        client.close()

    catalog = package["runtime_catalog"]
    counts = {
        "datasets": _count(catalog.get("datasets")),
        "fields": _count(catalog.get("fields")),
        "metrics": _count(catalog.get("metrics")),
        "entity_groups": _count(catalog.get("entity_groups")),
        "grains": _count(catalog.get("grains")),
        "relations": _count(catalog.get("relations")),
        "orderings": _count(catalog.get("orderings")),
        "recipes": _count(catalog.get("recipes")),
        "predicates": _count(catalog.get("predicates")),
        "aliases": _count(catalog.get("aliases")),
        "prompt_extensions": _count(catalog.get("prompt_extensions")),
        "specialized_functions": _count(catalog.get("specialized_functions")),
    }
    actual_fields = {
        kind: sorted({key for document in items for key in document})
        for kind, items in stored.items()
    }
    item_counts = {kind: len(items) for kind, items in stored.items()}
    natural_text_counts = {
        kind: sum(bool(str(document.get("natural_text") or "").strip()) for document in items)
        for kind, items in stored.items()
    }
    report = {
        "contract_version": "metadata.item-registration.v1",
        "status": "ok",
        "mode": "natural_language_items",
        "database": target_database,
        "database_mode": "operational" if target_database == operational_database else "isolated_validation",
        "collections": COLLECTIONS,
        "item_counts": item_counts,
        "natural_text_counts": natural_text_counts,
        "runtime_counts": counts,
        "stored_fields": actual_fields,
        "checks": {
            "runtime_catalog_round_trip": True,
            "available_loader": True,
            "item_fields_only": all(set(fields) == ALLOWED_ITEM_FIELDS for fields in actual_fields.values()),
            "no_release_documents": all(
                not ({"release_id", "release_manifest", "source_sha256", "document_sha256"} & set(fields))
                for fields in actual_fields.values()
            ),
        },
    }
    assert_secret_absent(report, mongo_uri)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--database", default="")
    parser.add_argument("--allow-operational-database", action="store_true")
    parser.add_argument("--allow-replace", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs/compiled_metadata_registration.json",
    )
    args = parser.parse_args()
    report = run(
        env_file=args.env_file.resolve(),
        package_path=args.package.resolve(),
        input_dir=args.input_dir.resolve(),
        database_name=str(args.database or "").strip() or None,
        allow_operational_database=bool(args.allow_operational_database),
        allow_replace=bool(args.allow_replace),
        output=args.output.resolve(),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
