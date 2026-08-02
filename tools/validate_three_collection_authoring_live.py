"""Run the v6 authoring component chain with real Gemini and MongoDB.

This is the Python-equivalent validation lane for environments where importing
and running a full Langflow server is unavailable.  It executes the generated
standalone Context Builder, Prompt Bundle Composer, Conditional Invoker,
Metadata Authoring Engine, three-collection writer, and runtime loader in the
same order as the exported Flow. The default target remains an isolated
validation database; operational writes require an explicit CLI opt-in.
Reports contain hashes and counts only.
"""

from __future__ import annotations

import argparse
import json
import os
from hashlib import sha256
from pathlib import Path
from typing import Any

from lfx.custom.eval import eval_custom_component_code
from lfx.schema.message import Message
from pymongo import MongoClient

from gemini_validation_support import (
    DEFAULT_GEMINI_MODEL,
    GeminiJsonModel,
    assert_secret_absent,
    load_dotenv_values,
    resolve_gemini_api_key,
)


ROOT = Path(__file__).resolve().parents[1]
COMPONENT_ROOT = ROOT / "langflow_components"
DEFAULT_INPUT_DIR = ROOT / "metadata" / "authoring" / "v6_inputs"
COLLECTIONS = {
    "domain": "agent_v6_domain_metadata",
    "table_catalog": "agent_v6_table_catalog",
    "main_filter": "agent_v6_main_filter",
}


def _component(relative: str):
    source = (COMPONENT_ROOT / relative).read_text(encoding="utf-8")
    return eval_custom_component_code(source)


class _MessageGemini:
    """Adapt LangChain messages to the secret-safe direct Gemini validator."""

    def __init__(self, delegate: GeminiJsonModel) -> None:
        self.delegate = delegate

    def invoke(self, messages: Any) -> str:
        if not isinstance(messages, list):
            return self.delegate.invoke(str(messages))
        segments = []
        for message in messages:
            role = type(message).__name__
            content = str(getattr(message, "content", "") or "")
            segments.append(f"[{role}]\n{content}")
        return self.delegate.invoke("\n\n".join(segments))


def _reference_context(domain_id: str):
    component = _component(
        "metadata_authoring/authoring_reference_registry.py"
    )()
    component.registry_json = (
        ROOT / f"metadata/domain_packs/{domain_id}/approved_source_registry.json"
    ).read_text(encoding="utf-8")
    component.domain_id = domain_id
    return component.load_registry()


def _prompt_context(
    *, kind: str, source_text: str, domain_id: str, environment: str, reference
):
    component = _component(
        "metadata_authoring/authoring_prompt_context_builder.py"
    )()
    component.input_message = Message(text=source_text)
    component.approved_reference_context = reference
    component.bootstrap_fragment = True
    component.authoring_kind = kind
    component.mode = "save"
    component.source_grounding_mode = "freeform_llm"
    component.domain_id = domain_id
    component.environment = environment
    component.trusted_blueprint_json = ""
    component.trusted_blueprint_sha256 = ""
    return component.build_context()


def _invoke_branch(*, kind: str, context, model: _MessageGemini):
    from lfx.schema.message import Message as LangflowMessage

    composer = _component("shared/01_prompt_bundle_composer.py")()
    composer.common_prompt_message = LangflowMessage(
        text=(ROOT / f"prompts/metadata_authoring/{kind}_common_ko.md").read_text(
            encoding="utf-8"
        )
    )
    composer.specialized_prompt_message = LangflowMessage(
        text=(ROOT / f"prompts/metadata_authoring/{kind}_specialized_ko.md").read_text(
            encoding="utf-8"
        )
    )
    composer.runtime_context = context
    bundle = composer.build_prompt_bundle()

    invoker = _component("shared/02_conditional_llm_invoker.py")()
    invoker.prompt_bundle = bundle
    invoker.language_model = model
    result = invoker.invoke_once()
    if result.data.get("status") != "ok" or result.data.get("llm_calls") != 1:
        error = result.data.get("error") if isinstance(result.data.get("error"), dict) else {}
        raise RuntimeError(str(error.get("code") or "gemini_authoring_branch_failed"))
    return result, bundle


def run(
    *,
    env_file: Path,
    input_dir: Path,
    output: Path,
    database_name: str | None = None,
    domain_id: str = "manufacturing",
    environment: str = "validation",
    allow_operational_database: bool = False,
) -> dict[str, Any]:
    env = load_dotenv_values(env_file)
    api_key = resolve_gemini_api_key(env_file)
    mongo_uri = str(os.getenv("MONGODB_URI") or env.get("MONGODB_URI") or "").strip()
    if not mongo_uri:
        raise RuntimeError("mongodb_uri_not_configured")
    operational_database = str(
        os.getenv("MONGODB_DATABASE") or env.get("MONGODB_DATABASE") or "datagov"
    ).strip()
    database_name = str(
        database_name
        or os.getenv("MONGODB_VALIDATION_DATABASE")
        or env.get("MONGODB_VALIDATION_DATABASE")
        or "datagov_v6_validation"
    ).strip()
    if database_name == operational_database and not allow_operational_database:
        raise RuntimeError("validation_database_must_be_isolated")

    domain_id = str(domain_id or "manufacturing").strip()
    environment = str(environment or "validation").strip()
    sources = {
        "domain": (input_dir / "domain_v6.txt").read_text(encoding="utf-8"),
        "dataset": (input_dir / "dataset_v6.txt").read_text(encoding="utf-8"),
        "main_filter": (input_dir / "main_filter_v6.txt").read_text(encoding="utf-8"),
    }
    reference = _reference_context(domain_id)
    delegate = GeminiJsonModel(
        api_key=api_key,
        model=DEFAULT_GEMINI_MODEL,
        timeout_seconds=int(env.get("LLM_TIMEOUT_SECONDS") or 90),
        max_output_tokens=32768,
    )
    model = _MessageGemini(delegate)

    contexts = {
        kind: _prompt_context(
            kind=kind,
            source_text=sources[kind if kind != "dataset" else "dataset"],
            domain_id=domain_id,
            environment=environment,
            reference=reference,
        )
        for kind in ("domain", "dataset", "main_filter")
    }
    invocation_results = {}
    bundle_hashes = {}
    for kind in ("domain", "dataset", "main_filter"):
        invocation_results[kind], bundle = _invoke_branch(
            kind=kind, context=contexts[kind], model=model
        )
        bundle_hashes[kind] = str(bundle.data["manifest"]["bundle_sha256"])

    bundler = _component(
        "metadata_authoring/natural_metadata_source_bundle.py"
    )()
    bundler.domain_source = Message(text=sources["domain"])
    bundler.dataset_source = Message(text=sources["dataset"])
    bundler.main_filter_source = Message(text=sources["main_filter"])

    engine = _component("metadata_authoring/00_metadata_authoring_engine.py")()
    engine.input_message = bundler.bundle_sources()
    engine.authoring_source_context = contexts["domain"]
    engine.bootstrap_dataset_source_context = contexts["dataset"]
    engine.bootstrap_main_filter_source_context = contexts["main_filter"]
    engine.authoring_invocation_result = invocation_results["domain"]
    engine.bootstrap_dataset_invocation_result = invocation_results["dataset"]
    engine.bootstrap_main_filter_invocation_result = invocation_results["main_filter"]
    engine.approved_reference_context = reference
    engine.split_bootstrap = True
    engine.authoring_kind = "domain"
    engine.source_grounding_mode = "freeform_llm"
    engine.metadata_contract_mode = "domain_package_v2"
    engine.domain_id = domain_id
    engine.environment = environment
    engine.revision_policy = "auto_next"
    engine.mode = "save"
    engine.mongo_uri = mongo_uri
    engine.mongo_database = database_name
    engine.domain_collection = COLLECTIONS["domain"]
    engine.table_collection = COLLECTIONS["table_catalog"]
    engine.main_filter_collection = COLLECTIONS["main_filter"]
    engine.dry_run = False
    response = engine.run_authoring().data
    if response.get("status") != "ok" or response.get("stage") != "committed":
        error = response.get("error") if isinstance(response.get("error"), dict) else {}
        details = error.get("details") if isinstance(error.get("details"), dict) else {}
        diagnostic = {
            "code": str(error.get("code") or "three_collection_commit_failed"),
            "status": str(response.get("status") or "unknown"),
            "stage": str(response.get("stage") or "unknown"),
            "error_stage": str(error.get("stage") or "unknown"),
            "message": str(error.get("message") or ""),
            "missing_fields": [
                str(item)
                for item in ((response.get("clarification") or {}).get("missing_fields") or [])[:32]
            ],
            "details": {
                key: details.get(key)
                for key in (
                    "dataset_id",
                    "omitted_approved_dataset_ids",
                    "missing",
                    "unknown",
                    "path",
                    "reason",
                )
                if key in details
            },
        }
        raise RuntimeError(json.dumps(diagnostic, ensure_ascii=False, sort_keys=True))

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    try:
        database = client[database_name]
        current_id = f"{environment}:{domain_id}"
        documents = {
            kind: database[name].find_one({"_id": current_id})
            for kind, name in COLLECTIONS.items()
        }
        if any(not isinstance(value, dict) for value in documents.values()):
            raise RuntimeError("three_collection_document_missing")
        release_ids = {str(value.get("release_id") or "") for value in documents.values()}
        source_present = {
            kind: bool(str(value.get("source_text") or "").strip())
            for kind, value in documents.items()
        }
        if len(release_ids) != 1 or not next(iter(release_ids), "") or not all(source_present.values()):
            raise RuntimeError("three_collection_release_validation_failed")

        loader = _component("data_analysis/domain_bundle_loader.py")()
        loader.mongo_uri = mongo_uri
        loader.mongo_database = database_name
        loader.mongo_timeout_ms = 10000
        loader_input_names = {str(item.name) for item in loader.inputs}
        loaded = loader.load_bundle().data
        if loaded.get("ok") is not True:
            raise RuntimeError("three_collection_loader_failed")
        runtime_bundle = (
            loaded.get("domain_bundle")
            if isinstance(loaded.get("domain_bundle"), dict)
            else {}
        )
        loader_checks = {
            "source_mode_exact": runtime_bundle.get("source_mode") == "three_collections",
            "identity_exact": runtime_bundle.get("domain_id") == domain_id
            and runtime_bundle.get("environment") == environment,
            "revision_exact": int(runtime_bundle.get("revision") or 0)
            == int(response.get("revision") or 0),
            "package_sha256_exact": runtime_bundle.get("package_sha256")
            == response.get("package_sha256"),
            "bundle_sha256_exact": runtime_bundle.get("bundle_sha256")
            == response.get("bundle_sha256"),
            "catalog_sha256_exact": runtime_bundle.get("catalog_sha256")
            == response.get("catalog_sha256"),
            "loader_inputs_exact": loader_input_names
            == {"mongo_uri", "mongo_database", "mongo_timeout_ms"},
        }
        if not all(loader_checks.values()):
            raise RuntimeError("three_collection_loader_contract_failed")
    finally:
        client.close()

    report = {
        "status": "ok",
        "contract_version": "three-collection-live-validation.v1",
        "model": DEFAULT_GEMINI_MODEL,
        "database": database_name,
        "database_mode": "operational" if database_name == operational_database else "isolated_validation",
        "environment": environment,
        "domain_id": domain_id,
        "collections": COLLECTIONS,
        "source_sha256": {
            kind: sha256(value.encode("utf-8")).hexdigest()
            for kind, value in sources.items()
        },
        "prompt_bundle_sha256": bundle_hashes,
        "llm": delegate.evidence(),
        "authoring": {
            "stage": response.get("stage"),
            "revision": response.get("revision"),
            "candidate_sha256": response.get("candidate_sha256"),
            "catalog_sha256": response.get("catalog_sha256"),
            "llm_usage": response.get("llm_usage"),
        },
        "storage": {
            "document_count": len(documents),
            "release_id_count": len(release_ids),
            "release_id_sha256": sha256(next(iter(release_ids)).encode("utf-8")).hexdigest(),
            "natural_source_present": source_present,
        },
        "loader": {
            "ok": loaded.get("ok"),
            "selection": "latest_available_release",
            "input_names": sorted(loader_input_names),
            "source_mode": runtime_bundle.get("source_mode"),
            "revision": runtime_bundle.get("revision"),
            "catalog_sha256": runtime_bundle.get("catalog_sha256"),
            "checks": loader_checks,
        },
    }
    assert_secret_absent(report, api_key)
    assert_secret_absent(report, mongo_uri)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--database", default="")
    parser.add_argument("--domain-id", default="manufacturing")
    parser.add_argument("--environment", default="validation")
    parser.add_argument(
        "--allow-operational-database",
        action="store_true",
        help="allow an explicitly named target equal to MONGODB_DATABASE",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation_outputs/three_collection_live_validation.json",
    )
    args = parser.parse_args()
    report = run(
        env_file=args.env_file.resolve(),
        input_dir=args.input_dir.resolve(),
        output=args.output.resolve(),
        database_name=str(args.database or "").strip() or None,
        domain_id=args.domain_id,
        environment=args.environment,
        allow_operational_database=bool(args.allow_operational_database),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
