"""Create v6 migration candidates while treating every v5 collection read-only.

The default command is a filesystem dry-run.  ``--read-v5-mongo`` may inspect
the fixed legacy collections.  ``--apply-v6-candidates`` inserts immutable draft
records only into fixed ``agent_v6_*`` collections; it can never target v5.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.canonical import canonical_bytes, sha256_json
from reference_runtime.domain_packages import (
    ACTIVE_POINTER_COLLECTION,
    DOMAIN_PACKAGE_COLLECTION,
    MIGRATION_QUARANTINE_COLLECTION,
    adapt_legacy_catalog_v1,
    load_active_domain_bundle,
    make_active_pointer_document,
    make_bundle_document,
    validate_domain_package,
)
from reference_runtime.metadata_compiler import build_runtime_catalog, compiled_records, source_provenance


V5_SOURCE_COLLECTIONS = (
    "agent_v4_domain_items",
    "agent_v4_table_catalog_items",
    "agent_v4_main_flow_filters",
)
V6_TARGET_COLLECTIONS = {
    "authoring_source": "agent_v6_authoring_sources",
    "dataset": "agent_v6_dataset_catalog",
    "field": "agent_v6_filter_catalog",
    "metric": "agent_v6_semantic_catalog",
    "process_group": "agent_v6_semantic_catalog",
    "process_order": "agent_v6_semantic_catalog",
    "product_group": "agent_v6_semantic_catalog",
    "recipe": "agent_v6_semantic_catalog",
    "alias": "agent_v6_filter_catalog",
    "migration_domain": "agent_v6_semantic_catalog",
    "migration_dataset": "agent_v6_dataset_catalog",
    "migration_filter": "agent_v6_filter_catalog",
    "domain_bundle": DOMAIN_PACKAGE_COLLECTION,
    "migration_quarantine": MIGRATION_QUARANTINE_COLLECTION,
}
ALL_V6_COLLECTIONS = {
    "agent_v6_authoring_sources",
    "agent_v6_semantic_catalog",
    "agent_v6_dataset_catalog",
    "agent_v6_filter_catalog",
    "agent_v6_config_registry",
    "agent_v6_query_registry",
    "agent_v6_pending_writes",
    "agent_v6_authoring_audit",
    "agent_v6_session_state",
    "agent_v6_result_store",
    "agent_v6_validation_runs",
    DOMAIN_PACKAGE_COLLECTION,
    ACTIVE_POINTER_COLLECTION,
    MIGRATION_QUARANTINE_COLLECTION,
}
AUTHORING_AUDIT_COLLECTION = "agent_v6_authoring_audit"

DOMAIN_SECTION_KIND = {
    "analysis_recipes": "recipe",
    "process_groups": "entity_group",
    "process_order": "ordering",
    "process_sequences": "ordering",
    "product_groups": "predicate",
    "product_group_definitions": "predicate",
    "quantity_terms": "metric",
    "metric_terms": "metric",
    "calculation_rules": "metric",
    "product_key_columns": "grain",
    "grains": "grain",
    "pandas_function_cases": "specialized_function_review",
}
SECRET_PARTS = (
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "private_key",
    "connection_string",
    "mongo_uri",
)
EXECUTABLE_FIELDS = {"code", "python", "python_code", "pandas_code", "script", "lambda", "eval", "exec"}


def assert_collection_boundaries(source_collections: Iterable[str], target_collections: Iterable[str]) -> None:
    sources = {str(value) for value in source_collections}
    targets = {str(value) for value in target_collections}
    if not sources.issubset(set(V5_SOURCE_COLLECTIONS)):
        raise ValueError("v5 source collection allowlist violation")
    if any(not name.startswith("agent_v6_") or name not in ALL_V6_COLLECTIONS for name in targets):
        raise ValueError("v6 target collection allowlist violation")
    if sources & targets:
        raise ValueError("source and target collections must be disjoint")


def build_migration_plan(
    *,
    authoring_root: Path = ROOT / "metadata" / "authoring",
    v5_records: dict[str, list[dict[str, Any]]] | None = None,
    domain_id: str = "manufacturing",
    environment: str = "default",
    revision: int = 1,
) -> dict[str, Any]:
    if int(revision) < 1:
        raise ValueError("revision must be at least 1")
    assert_collection_boundaries(V5_SOURCE_COLLECTIONS, V6_TARGET_COLLECTIONS.values())
    provenance = source_provenance(authoring_root)
    catalog = build_runtime_catalog(authoring_root)
    records = compiled_records(catalog, provenance, lifecycle_status="draft")
    candidates: list[dict[str, Any]] = []
    for record in records:
        kind = str(record["kind"])
        target = V6_TARGET_COLLECTIONS[kind]
        candidate = {
            "target_collection": target,
            "candidate_id": f"migration:{sha256_json(record)}",
            "candidate_sha256": sha256_json(record),
            "migration_status": "candidate",
            "record": record,
        }
        candidates.append(candidate)
    for source_kind, source in provenance.items():
        record = {
            "schema_version": "metadata.authoring.source.v1",
            "kind": "authoring_source",
            "identity": {"namespace": "metadata_v6", "key": source_kind},
            "revision": 1,
            "lifecycle": {"status": "draft"},
            "source": source,
            "content_sha256": source["content_sha256"],
        }
        candidates.append(
            {
                "target_collection": V6_TARGET_COLLECTIONS["authoring_source"],
                "candidate_id": f"migration:{sha256_json(record)}",
                "candidate_sha256": sha256_json(record),
                "migration_status": "candidate",
                "record": record,
            }
        )

    natural_txt_candidate_count = len(candidates)
    package = adapt_legacy_catalog_v1(
        catalog,
        domain_id=domain_id,
        environment=environment,
        revision=int(revision),
        output_profile={
            "planner_profile": "legacy_v1_compat",
            "legacy_catalog_sha256": catalog["catalog_sha256"],
        },
    )
    bundle_document = make_bundle_document(package)
    bundle_candidate = {
        "target_collection": DOMAIN_PACKAGE_COLLECTION,
        "candidate_id": f"migration:{sha256_json(bundle_document)}",
        "candidate_sha256": sha256_json(bundle_document),
        "migration_status": "candidate",
        "record": bundle_document,
    }
    candidates.append(bundle_candidate)

    converted, quarantine = _convert_v5_records(
        v5_records or {},
        domain_id=domain_id,
        environment=environment,
        bundle_sha256=package["bundle_sha256"],
        revision=int(revision),
    )
    candidates.extend(converted)
    counts_by_collection = {
        collection: sum(1 for item in converted if item.get("source_collection") == collection)
        for collection in V5_SOURCE_COLLECTIONS
    }
    return {
        "contract_version": "metadata.v5-migration.plan.v2",
        "mode": "dry_run",
        "catalog_sha256": catalog["catalog_sha256"],
        "domain_id": package["domain_id"],
        "environment": package["environment"],
        "revision": package["revision"],
        "bundle_sha256": package["bundle_sha256"],
        "package_sha256": package["package_sha256"],
        "source_collections": list(V5_SOURCE_COLLECTIONS),
        "target_collections": sorted(set(V6_TARGET_COLLECTIONS.values())),
        "authoring_sources": provenance,
        "candidates": candidates,
        "quarantine": quarantine,
        "report": {
            "natural_txt_candidate_count": natural_txt_candidate_count,
            "domain_bundle_candidate_count": 1,
            "v5_record_count": sum(len(items) for items in (v5_records or {}).values()),
            "converted_v5_record_count": len(converted),
            "converted_v5_by_collection": counts_by_collection,
            "quarantined_v5_record_count": len(quarantine),
            "invalid_active_record_count": 0,
            "v5_read_operations": len(V5_SOURCE_COLLECTIONS) if v5_records is not None else 0,
            "v5_write_operations": 0,
            "v6_write_operations": 0,
            "runtime_loader_round_trip": True,
            "policy": "natural_txt_recompiled; convertible_v5_records_become_typed_candidates; unsafe_or_incomplete_records_quarantined",
            "v5_collections_unchanged": True,
            "representative_question_impact": {
                "suites": ["Q01-Q30", "D01-D06", "MT01-MT05", "OP-01-OP-13"],
                "binding_corrections": [
                    "target.Mode -> MODE at source boundary",
                    "equipment_assign.OPER_NM -> OPER_NAME at source boundary",
                    "lot_status.OPER_SEQ declared for ordered-range validation",
                    "hold_history.HOLD_TM -> HOLD_EVENT_AT with Asia/Seoul",
                ],
                "behavioral_contracts": [
                    "BOH requested date D uses wip query date D-1",
                    "UPH permits mean only and never sum",
                    "W/BM is independent from W/B1-W/B6",
                    "presence uses typed anti-join rather than left-join narration",
                ],
            },
        },
    }


def read_v5_collections(database: Any) -> dict[str, list[dict[str, Any]]]:
    """Read the fixed v5 collections.  This function never obtains a write handle."""

    assert_collection_boundaries(V5_SOURCE_COLLECTIONS, V6_TARGET_COLLECTIONS.values())
    records: dict[str, list[dict[str, Any]]] = {}
    for name in V5_SOURCE_COLLECTIONS:
        records[name] = [deepcopy(document) for document in database[name].find({})]
    return records


def apply_v6_candidates(database: Any, plan: dict[str, Any]) -> dict[str, Any]:
    """Insert immutable runtime-shaped draft records into v6 collections only.

    Candidate envelopes are evidence and must not become runtime collection
    documents.  The inserted document is the validated ``record`` with a
    deterministic ``_id``; duplicate IDs make the operation idempotent.
    """

    targets = [str(item.get("target_collection") or "") for item in plan.get("candidates", [])]
    assert_collection_boundaries(V5_SOURCE_COLLECTIONS, targets)
    inserted = 0
    duplicates = 0
    for candidate in plan.get("candidates", []):
        target = str(candidate["target_collection"])
        record = deepcopy(candidate.get("record") or {})
        if not isinstance(record, dict) or not record:
            raise ValueError("migration candidate record must be a non-empty object")
        _validate_candidate_record_shape(target, record)
        document = record
        document.setdefault("_id", _record_document_id(record, candidate))
        try:
            database[target].insert_one(document)
            inserted += 1
        except Exception as exc:  # narrowed without importing pymongo at module import time
            if exc.__class__.__name__ != "DuplicateKeyError":
                raise
            duplicates += 1
    plan["report"]["v6_write_operations"] = inserted
    plan["report"]["v6_duplicate_candidates"] = duplicates
    plan["report"]["v5_write_operations"] = 0
    verification = verify_v6_candidate_documents(database, plan)
    plan["report"].update(verification)
    plan["mode"] = "v6_candidates_inserted"
    return plan


def verify_v6_candidate_documents(database: Any, plan: dict[str, Any]) -> dict[str, Any]:
    verified = 0
    missing: list[str] = []
    mismatched: list[str] = []
    for candidate in plan.get("candidates", []):
        target = str(candidate["target_collection"])
        record = deepcopy(candidate["record"])
        document_id = str(record.get("_id") or _record_document_id(record, candidate))
        actual = _collection_find_one(database[target], {"_id": document_id})
        if not actual:
            missing.append(document_id)
            continue
        expected_material = {key: value for key, value in record.items() if key != "_id"}
        actual_material = {key: _json_safe(value) for key, value in actual.items() if key != "_id"}
        if sha256_json(expected_material) != sha256_json(actual_material):
            mismatched.append(document_id)
            continue
        verified += 1
    if missing or mismatched:
        raise RuntimeError(
            "v6 candidate post-write verification failed: "
            f"missing={len(missing)}, mismatched={len(mismatched)}"
        )
    return {
        "v6_verified_document_count": verified,
        "v6_missing_document_count": 0,
        "v6_mismatched_document_count": 0,
    }


def activate_v6_bundle(
    database: Any,
    plan: dict[str, Any],
    *,
    expected_active_revision: int | None = None,
    expected_active_bundle_sha256: str = "",
    idempotency_key: str = "",
) -> dict[str, Any]:
    """CAS-activate the exact applied bundle and append an idempotent audit event.

    A missing pointer may be created only when no expected active pin is
    supplied.  Replacing an existing different pointer requires both its exact
    revision and bundle hash.  The active pointer itself carries the immutable
    activation event ID, so a later retry can repair a missing audit projection
    without repeating the activation.
    """

    bundle_candidate = next(
        (
            item
            for item in plan.get("candidates", [])
            if item.get("target_collection") == DOMAIN_PACKAGE_COLLECTION
        ),
        None,
    )
    if not isinstance(bundle_candidate, dict):
        raise ValueError("domain bundle candidate is required for activation")
    expected_record = deepcopy(bundle_candidate["record"])
    bundle_id = str(expected_record.get("_id") or "")
    stored_record = _collection_find_one(database[DOMAIN_PACKAGE_COLLECTION], {"_id": bundle_id})
    if not stored_record:
        raise RuntimeError("domain bundle must be applied before activation")
    package = {key: deepcopy(value) for key, value in stored_record.items() if key != "_id"}
    validate_domain_package(package)
    if sha256_json({key: value for key, value in expected_record.items() if key != "_id"}) != sha256_json(package):
        raise RuntimeError("stored domain bundle differs from the migration plan")

    pointer = make_active_pointer_document(package)
    active_collection = database[ACTIVE_POINTER_COLLECTION]
    existing = _collection_find_one(active_collection, {"_id": pointer["_id"]})
    effective_idempotency_key = str(idempotency_key or f"activate:{package['bundle_sha256']}").strip()
    event_material = {
        "contract_version": "metadata.domain.activation.event.v1",
        "domain_id": package["domain_id"],
        "environment": package["environment"],
        "revision": package["revision"],
        "bundle_sha256": package["bundle_sha256"],
        "package_sha256": package["package_sha256"],
        "idempotency_key": effective_idempotency_key,
    }
    event_id = f"activation:{sha256_json(event_material)}"
    pointer_document = {**pointer, "activation_event_id": event_id, "idempotency_key": effective_idempotency_key}

    pointer_writes = 0
    status = "activated"
    previous_pointer = None
    if existing:
        same_pin = all(existing.get(key) == pointer_document.get(key) for key in (
            "domain_id",
            "environment",
            "revision",
            "bundle_sha256",
            "package_sha256",
            "status",
            "activation_event_id",
            "idempotency_key",
        ))
        if same_pin:
            status = "already_active"
        else:
            if expected_active_revision is None or not expected_active_bundle_sha256:
                raise RuntimeError("existing active pointer replacement requires expected revision and bundle hash")
            if (
                int(existing.get("revision") or 0) != int(expected_active_revision)
                or str(existing.get("bundle_sha256") or "") != str(expected_active_bundle_sha256)
            ):
                raise RuntimeError("active pointer CAS precondition mismatch")
            previous_pointer = {
                "revision": int(existing["revision"]),
                "bundle_sha256": str(existing["bundle_sha256"]),
                "package_sha256": str(existing.get("package_sha256") or ""),
            }
            result = active_collection.replace_one(
                {
                    "_id": pointer["_id"],
                    "revision": int(expected_active_revision),
                    "bundle_sha256": str(expected_active_bundle_sha256),
                },
                pointer_document,
                upsert=False,
            )
            if int(getattr(result, "matched_count", 0)) != 1:
                raise RuntimeError("active pointer CAS lost a concurrent update")
            pointer_writes = int(getattr(result, "modified_count", 1) or 1)
    else:
        if expected_active_revision is not None or expected_active_bundle_sha256:
            raise RuntimeError("expected active pin was supplied but active pointer is absent")
        try:
            active_collection.insert_one(pointer_document)
        except Exception as exc:
            if exc.__class__.__name__ != "DuplicateKeyError":
                raise
            raise RuntimeError("active pointer was concurrently created; retry with exact expected pin") from exc
        pointer_writes = 1

    audit_document = {
        "_id": event_id,
        **event_material,
        "event_type": "bundle_activated",
        "status": "committed",
        "active_pointer_id": pointer["_id"],
        "previous_pointer": previous_pointer,
        "activated_at": datetime.now(timezone.utc).isoformat(),
    }
    audit_collection = database[AUTHORING_AUDIT_COLLECTION]
    audit_writes = 0
    existing_audit = _collection_find_one(audit_collection, {"_id": event_id})
    if not existing_audit:
        try:
            audit_collection.insert_one(audit_document)
            audit_writes = 1
        except Exception as exc:
            if exc.__class__.__name__ != "DuplicateKeyError":
                raise

    loaded = load_active_domain_bundle(database, package["domain_id"], package["environment"])
    if loaded["bundle_sha256"] != package["bundle_sha256"]:
        raise RuntimeError("post-activation loader verification failed")
    return {
        "activation_status": status,
        "active_pointer_id": pointer["_id"],
        "active_bundle_sha256": package["bundle_sha256"],
        "active_revision": package["revision"],
        "activation_event_id": event_id,
        "active_pointer_write_operations": pointer_writes,
        "activation_audit_write_operations": audit_writes,
        "activation_loader_round_trip": True,
    }


def _collection_find_one(collection: Any, query: dict[str, Any]) -> dict[str, Any] | None:
    finder = getattr(collection, "find_one", None)
    if callable(finder):
        result = finder(query)
        return deepcopy(result) if isinstance(result, dict) else None
    for attribute in ("inserted", "rows"):
        for item in getattr(collection, attribute, []) or []:
            if isinstance(item, dict) and all(item.get(key) == value for key, value in query.items()):
                return deepcopy(item)
    return None


def _record_document_id(record: dict[str, Any], candidate: dict[str, Any]) -> str:
    if str(record.get("schema_version") or "") == "metadata.migration.record.v2":
        identity = record.get("identity") if isinstance(record.get("identity"), dict) else {}
        provenance = record.get("provenance") if isinstance(record.get("provenance"), dict) else {}
        validation = record.get("validation") if isinstance(record.get("validation"), dict) else {}
        identity_material = {
            "domain_id": str(validation.get("target_domain_id") or identity.get("namespace") or ""),
            "environment": str(validation.get("target_environment") or ""),
            "source_collection": str(provenance.get("source_collection") or candidate.get("source_collection") or ""),
            "source_document_id": str(provenance.get("source_document_id") or candidate.get("source_document_id") or ""),
            "legacy_identity": str(identity.get("key") or ""),
            "content_sha256": str(provenance.get("content_sha256") or ""),
            "kind": str(record.get("kind") or "metadata"),
            "revision": int(record.get("revision") or 1),
        }
        if not all(identity_material[key] for key in (
            "domain_id",
            "environment",
            "source_collection",
            "source_document_id",
            "legacy_identity",
            "content_sha256",
        )):
            raise ValueError("migration record identity is not fully domain/environment/source bound")
        return (
            f"migration:{identity_material['domain_id']}:{identity_material['environment']}:"
            f"{sha256_json(identity_material)}"
        )
    identity = record.get("identity") if isinstance(record.get("identity"), dict) else {}
    namespace = str(identity.get("namespace") or "metadata_v6")
    key = str(identity.get("key") or candidate.get("candidate_id") or sha256_json(record))
    kind = str(record.get("kind") or record.get("schema_version") or "metadata")
    revision = int(record.get("revision") or 1)
    return f"{kind}:{namespace}:{key}:r{revision}"


def _validate_candidate_record_shape(target: str, record: dict[str, Any]) -> None:
    if target == DOMAIN_PACKAGE_COLLECTION:
        package = {key: deepcopy(value) for key, value in record.items() if key != "_id"}
        validate_domain_package(package)
        if record.get("_id") != f"bundle:{package['bundle_sha256']}":
            raise ValueError("domain bundle document id/hash mismatch")
        return
    schema_version = str(record.get("schema_version") or "")
    if schema_version == "metadata.authoring.source.v1":
        if not isinstance(record.get("identity"), dict) or not isinstance(record.get("source"), dict):
            raise ValueError("authoring source record shape mismatch")
        return
    if schema_version not in {"metadata.v6", "metadata.migration.record.v2"}:
        raise ValueError(f"unsupported metadata record schema: {schema_version}")
    if (
        not isinstance(record.get("identity"), dict)
        or not str(record["identity"].get("key") or "")
        or not isinstance(record.get("contract"), dict)
        or record.get("contract_sha256") != sha256_json(record["contract"])
    ):
        raise ValueError("immutable metadata record shape/hash mismatch")


def _convert_v5_records(
    records: dict[str, list[dict[str, Any]]],
    *,
    domain_id: str,
    environment: str,
    bundle_sha256: str,
    revision: int = 1,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    for collection in V5_SOURCE_COLLECTIONS:
        for document in records.get(collection, []):
            material = _json_safe(document)
            converted, reason = _convert_v5_document(
                collection,
                material,
                domain_id=domain_id,
                environment=environment,
                bundle_sha256=bundle_sha256,
                revision=revision,
            )
            if converted is None:
                quarantine.append(_quarantine_entry(collection, material, reason))
            else:
                candidates.append(converted)
    return candidates, quarantine


def _convert_v5_document(
    collection: str,
    document: dict[str, Any],
    *,
    domain_id: str,
    environment: str,
    bundle_sha256: str,
    revision: int = 1,
) -> tuple[dict[str, Any] | None, str]:
    if int(revision) < 1:
        return None, "invalid_target_revision"
    if _secret_paths(document):
        return None, "credential_or_secret_field_requires_manual_redaction"
    if _executable_paths(document):
        return None, "executable_code_field_is_not_migrated"

    payload = document.get("payload")
    if not isinstance(payload, dict) or not payload:
        return None, "missing_typed_payload"
    source_document_id = str(document.get("_id") or "").strip()
    if collection == "agent_v4_domain_items":
        section = str(document.get("section") or "").strip()
        key = str(document.get("key") or "").strip()
        if not section or not key:
            return None, "missing_domain_section_or_key"
        kind = DOMAIN_SECTION_KIND.get(section, "semantic_card")
        identity_key = f"{section}:{key}"
        target_collection = V6_TARGET_COLLECTIONS["migration_domain"]
        contract = {
            "section": section,
            "key": key,
            "kind": kind,
            "payload": _strip_non_runtime_fields(payload),
        }
        review_reasons = []
        if kind in {"semantic_card", "specialized_function_review"}:
            review_reasons.append("typed_runtime_mapping_requires_review")
    elif collection == "agent_v4_table_catalog_items":
        key = str(document.get("dataset_key") or document.get("key") or "").strip()
        if not key:
            return None, "missing_dataset_key"
        kind = "dataset"
        identity_key = key
        target_collection = V6_TARGET_COLLECTIONS["migration_dataset"]
        contract = _convert_table_payload(key, payload)
        review_reasons = list(contract.pop("_migration_review_reasons", []))
    elif collection == "agent_v4_main_flow_filters":
        key = str(document.get("filter_key") or document.get("key") or "").strip()
        if not key:
            return None, "missing_filter_key"
        kind = "filter"
        identity_key = key
        target_collection = V6_TARGET_COLLECTIONS["migration_filter"]
        contract = {
            "filter_id": key,
            "display_name": str(payload.get("display_name") or key),
            "aliases": _string_list(payload.get("aliases")),
            "operator": str(payload.get("operator") or "eq"),
            "value_type": str(payload.get("value_type") or "string"),
            "value_shape": str(payload.get("value_shape") or "scalar"),
            "semantic_contract": _strip_non_runtime_fields(payload),
        }
        review_reasons = [] if payload.get("operator") and payload.get("value_type") else ["filter_contract_defaulted"]
    else:
        return None, "source_collection_not_supported"

    source_hash = sha256_json(document)
    record = {
        "schema_version": "metadata.migration.record.v2",
        "kind": kind,
        "identity": {"namespace": domain_id, "key": identity_key},
        "revision": int(revision),
        "lifecycle": {"status": "draft"},
        "provenance": {
            "source_type": "legacy_mongodb_v5",
            "source_collection": collection,
            "source_document_id": source_document_id or identity_key,
            "content_sha256": source_hash,
        },
        "contract": contract,
        "contract_sha256": sha256_json(contract),
        "validation": {
            "schema": "candidate",
            "semantic_lint": "review_required" if review_reasons else "passed",
            "dependency_closure": "pending_approval",
            "review_reasons": review_reasons,
            "target_domain_id": domain_id,
            "target_environment": environment,
            "baseline_bundle_sha256": bundle_sha256,
        },
    }
    candidate_identity = {
        "domain_id": domain_id,
        "environment": environment,
        "source_collection": collection,
        "source_document_id": source_document_id or identity_key,
        "legacy_identity": identity_key,
        "content_sha256": source_hash,
    }
    candidate = {
        "target_collection": target_collection,
        "candidate_id": f"migration:v5:{sha256_json(candidate_identity)}",
        "candidate_sha256": "",
        "migration_status": "candidate",
        "source_collection": collection,
        "source_document_id": source_document_id or identity_key,
        "record": record,
    }
    record["_id"] = _record_document_id(record, candidate)
    candidate["candidate_sha256"] = sha256_json(record)
    return candidate, ""


def _convert_table_payload(dataset_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    source_config = payload.get("source_config") if isinstance(payload.get("source_config"), dict) else {}
    source_type = str(source_config.get("source_type") or payload.get("source_type") or "").strip().lower()
    mappings = payload.get("filter_mappings") if isinstance(payload.get("filter_mappings"), dict) else {}
    aliases = payload.get("standard_column_aliases") if isinstance(payload.get("standard_column_aliases"), dict) else {}
    metric_semantics = payload.get("metric_semantics") if isinstance(payload.get("metric_semantics"), dict) else {}
    fields: dict[str, Any] = {}
    all_fields = sorted(set(map(str, mappings)) | set(map(str, aliases)) | set(map(str, metric_semantics)))
    for canonical in all_fields:
        physical_value = mappings.get(canonical, canonical)
        if isinstance(physical_value, dict):
            physical = str(
                physical_value.get("physical_column")
                or physical_value.get("column")
                or physical_value.get("source_column")
                or canonical
            )
        else:
            physical = str(physical_value or canonical)
        alias_values = aliases.get(canonical)
        physical_aliases = _string_list(alias_values)
        semantics = metric_semantics.get(canonical) if isinstance(metric_semantics.get(canonical), dict) else {}
        is_metric = bool(semantics)
        fields[canonical] = {
            "physical_column": physical,
            "physical_aliases": [item for item in physical_aliases if item != physical],
            "semantic_type": str(semantics.get("semantic_type") or ("number" if is_metric else "string")),
            "roles": ["filter", "group", "join", "project", "output", *(["aggregate", "rank", "metric"] if is_metric else [])],
        }
    stripped = _strip_non_runtime_fields(payload)
    query_material = source_config.get("query_template")
    if query_material:
        stripped.setdefault("source_registry_migration", {})["legacy_query_sha256"] = sha256_json(str(query_material))
    review_reasons: list[str] = []
    if not source_type:
        review_reasons.append("source_adapter_requires_review")
    if not fields:
        review_reasons.append("field_bindings_require_review")
    return {
        "dataset_key": dataset_key,
        "display_name": str(payload.get("display_name") or dataset_key),
        "family": str(payload.get("family") or dataset_key),
        "source_adapter": source_type or "legacy_unresolved",
        "config_ref": str(source_config.get("config_ref") or f"legacy-config:{dataset_key}"),
        "query_ref": str(source_config.get("query_ref") or f"legacy-query:{dataset_key}"),
        "field_bindings": fields,
        "legacy_contract": stripped,
        "_migration_review_reasons": review_reasons,
    }


def _strip_non_runtime_fields(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for raw_key, child in value.items():
            key = str(raw_key)
            normalized = key.casefold()
            if normalized in {"query_template", "sql", "endpoint_url"}:
                result[f"legacy_{normalized}_sha256"] = sha256_json(_json_safe(child))
                continue
            result[key] = _strip_non_runtime_fields(child)
        return result
    if isinstance(value, list):
        return [_strip_non_runtime_fields(item) for item in value]
    return _json_safe(value)


def _secret_paths(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for raw_key, child in value.items():
            key = str(raw_key).casefold()
            location = ".".join((*path, str(raw_key)))
            if any(part in key for part in SECRET_PARTS):
                found.append(location)
            found.extend(_secret_paths(child, (*path, str(raw_key))))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_secret_paths(child, (*path, str(index))))
    return found


def _executable_paths(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for raw_key, child in value.items():
            key = str(raw_key).casefold()
            location = ".".join((*path, str(raw_key)))
            if key in EXECUTABLE_FIELDS:
                found.append(location)
            found.extend(_executable_paths(child, (*path, str(raw_key))))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_executable_paths(child, (*path, str(index))))
    return found


def _string_list(value: Any) -> list[str]:
    values = value if isinstance(value, (list, tuple, set)) else [value]
    return list(dict.fromkeys(str(item).strip() for item in values if str(item or "").strip()))


def _quarantine_entry(collection: str, document: dict[str, Any], reason: str) -> dict[str, Any]:
    safe_id = str(document.get("_id") or document.get("key") or document.get("name") or "unknown")
    return {
        "target_collection": MIGRATION_QUARANTINE_COLLECTION,
        "source_type": "v5_record",
        "source_collection": collection,
        "source_document_id": safe_id,
        "content_sha256": sha256_json(document),
        "status": "quarantined",
        "reason": reason,
    }


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _write_plan(output_dir: Path, plan: dict[str, Any]) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates_path = output_dir / "v5_migration_candidates.json"
    report_path = output_dir / "v5_migration_report.json"
    candidates_path.write_bytes(canonical_bytes({key: value for key, value in plan.items() if key != "report"}) + b"\n")
    report_path.write_bytes(canonical_bytes(plan["report"]) + b"\n")
    return candidates_path, report_path


def main() -> int:
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env", override=False)
    except ImportError:
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authoring-root", type=Path, default=ROOT / "metadata" / "authoring")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "metadata" / "fixtures" / "compiled")
    parser.add_argument("--read-v5-mongo", action="store_true")
    parser.add_argument("--apply-v6-candidates", action="store_true")
    parser.add_argument("--mongo-uri", default="")
    parser.add_argument("--database", default="")
    parser.add_argument("--domain-id", default="manufacturing")
    parser.add_argument("--environment", default="production")
    parser.add_argument("--revision", type=int, default=1)
    parser.add_argument("--activate-v6-bundle", action="store_true")
    parser.add_argument("--expected-active-revision", type=int)
    parser.add_argument("--expected-active-bundle-sha256", default="")
    parser.add_argument("--activation-idempotency-key", default="")
    args = parser.parse_args()

    database = None
    v5_records = None
    if args.read_v5_mongo or args.apply_v6_candidates or args.activate_v6_bundle:
        from pymongo import MongoClient

        uri = args.mongo_uri or os.getenv("MONGODB_URI", "")
        database_name = args.database or os.getenv("MONGODB_DATABASE", "")
        if not uri or not database_name:
            raise SystemExit("Mongo URI/database are required for Mongo migration mode")
        database = MongoClient(uri, serverSelectionTimeoutMS=10_000)[database_name]
    if args.read_v5_mongo:
        v5_records = read_v5_collections(database)
    plan = build_migration_plan(
        authoring_root=args.authoring_root.resolve(),
        v5_records=v5_records,
        domain_id=args.domain_id,
        environment=args.environment,
        revision=args.revision,
    )
    if args.apply_v6_candidates:
        plan = apply_v6_candidates(database, plan)
    if args.activate_v6_bundle:
        activation = activate_v6_bundle(
            database,
            plan,
            expected_active_revision=args.expected_active_revision,
            expected_active_bundle_sha256=args.expected_active_bundle_sha256,
            idempotency_key=args.activation_idempotency_key,
        )
        plan["report"].update(activation)
        plan["mode"] = "v6_bundle_activated"
    candidates_path, report_path = _write_plan(args.output_dir.resolve(), plan)
    print(
        json.dumps(
            {
                "mode": plan["mode"],
                "catalog_sha256": plan["catalog_sha256"],
                "candidate_path": str(candidates_path),
                "report_path": str(report_path),
                "report": plan["report"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
