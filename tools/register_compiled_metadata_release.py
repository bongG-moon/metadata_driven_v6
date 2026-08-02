"""Publish a reviewed v6 domain package to the fixed three MongoDB collections.

This is the deterministic registration lane used when a natural-language LLM
draft cannot be decoded safely. It never asks an LLM to recreate executable
metadata; it validates the reviewed package, preserves the worker source text,
publishes one atomic release, and reloads it through the public runtime loader.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from hashlib import sha256
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


def _count(value: Any) -> int:
    return len(value) if isinstance(value, (dict, list)) else 0


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
    from reference_runtime.canonical import sha256_json
    from reference_runtime.domain_packages import validate_domain_package
    from reference_runtime.metadata_collections import (
        load_available_domain_package_from_three_collections,
        load_domain_package_from_three_collections,
        make_metadata_section_documents,
        replace_metadata_release,
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
    documents = make_metadata_section_documents(package, source_texts)
    current_id = f"{package['environment']}:{package['domain_id']}"

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    try:
        database = client[target_database]
        client.admin.command("ping")
        existing = {
            kind: database[name].find_one({"_id": current_id}, {"_id": 1, "release_id": 1})
            for kind, name in COLLECTIONS.items()
        }
        if any(isinstance(value, dict) for value in existing.values()) and not allow_replace:
            raise RuntimeError("metadata_release_exists_use_allow_replace")

        with client.start_session() as session:
            with session.start_transaction():
                replace_metadata_release(database, documents, session=session)
                loaded = load_domain_package_from_three_collections(
                    database,
                    package["domain_id"],
                    package["environment"],
                    session=session,
                )
                if sha256_json(loaded) != sha256_json(package):
                    raise RuntimeError("published_package_round_trip_mismatch")

        auto_loaded = load_available_domain_package_from_three_collections(database)
        if sha256_json(auto_loaded) != sha256_json(package):
            raise RuntimeError("latest_available_loader_mismatch")
        stored = {
            kind: database[name].find_one({"_id": current_id})
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
    report = {
        "contract_version": "metadata.compiled-release.registration.v1",
        "status": "ok",
        "mode": "deterministic_compiled_fallback",
        "database": target_database,
        "database_mode": "operational" if target_database == operational_database else "isolated_validation",
        "domain_id": package["domain_id"],
        "environment": package["environment"],
        "revision": package["revision"],
        "current_id": current_id,
        "collections": COLLECTIONS,
        "package_sha256": package["package_sha256"],
        "bundle_sha256": package["bundle_sha256"],
        "catalog_sha256": catalog["catalog_sha256"],
        "source_sha256": {
            kind: sha256(text.encode("utf-8")).hexdigest()
            for kind, text in source_texts.items()
        },
        "counts": counts,
        "storage": {
            "document_count": sum(isinstance(value, dict) for value in stored.values()),
            "release_ids": sorted({str(value.get("release_id") or "") for value in stored.values()}),
            "natural_source_present": {
                kind: bool(str(value.get("source_text") or "").strip())
                for kind, value in stored.items()
            },
        },
        "checks": {
            "package_validated": True,
            "transactional_round_trip": True,
            "latest_available_loader": True,
            "three_documents_present": all(isinstance(value, dict) for value in stored.values()),
            "single_release": len({str(value.get("release_id") or "") for value in stored.values()}) == 1,
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
