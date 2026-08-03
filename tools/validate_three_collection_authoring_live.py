"""Run the v6 authoring component chain with real Gemini and MongoDB.

This is the Python-equivalent validation lane for environments where importing
and running a full Langflow server is unavailable.  It executes the generated
standalone natural-language draft node, simple validation/save node,
three-collection compiler/writer, and runtime loader in the same order as each
exported Flow. No approved registry input is injected. The default target remains an isolated
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


def _simple_authoring_context(*, kind: str, source_text: str, model: _MessageGemini):
    file_stem = "dataset" if kind == "dataset" else kind
    component = _component(
        f"metadata_authoring/03_{file_stem}_metadata_draft_generator.py"
    )()
    component.input_message = Message(text=source_text)
    component.common_prompt_message = Message(
        text=(ROOT / f"prompts/metadata_authoring/{kind}_common_ko.md").read_text(
            encoding="utf-8"
        )
    )
    component.specialized_prompt_message = Message(
        text=(ROOT / f"prompts/metadata_authoring/{kind}_specialized_ko.md").read_text(
            encoding="utf-8"
        )
    )
    component.language_model = model
    return component.build_authoring_context()


def run(
    *,
    env_file: Path,
    input_dir: Path,
    output: Path,
    database_name: str | None = None,
    domain_id: str = "default",
    environment: str = "production",
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

    domain_id = str(domain_id or "default").strip()
    environment = str(environment or "production").strip()
    if domain_id != "default" or environment != "production":
        raise RuntimeError("simple_authoring_identity_is_fixed_to_default_production")
    sources = {
        "domain": (input_dir / "domain_v6.txt").read_text(encoding="utf-8"),
        "dataset": (input_dir / "dataset_v6.txt").read_text(encoding="utf-8"),
        "main_filter": (input_dir / "main_filter_v6.txt").read_text(encoding="utf-8"),
    }
    delegate = GeminiJsonModel(
        api_key=api_key,
        model=DEFAULT_GEMINI_MODEL,
        timeout_seconds=int(env.get("LLM_TIMEOUT_SECONDS") or 90),
        max_output_tokens=32768,
    )
    model = _MessageGemini(delegate)

    responses: dict[str, dict[str, Any]] = {}
    bundle_hashes: dict[str, str] = {}
    for kind in ("domain", "dataset", "main_filter"):
        context = _simple_authoring_context(
            kind=kind,
            source_text=sources[kind],
            model=model,
        )
        context_data = context.data
        bundle_hashes[kind] = str(
            (context_data.get("authoring_invocation_result") or {}).get(
                "prompt_bundle_sha256"
            )
            or ""
        )

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
        responses[kind] = response
        if response.get("status") != "ok" or response.get("stage") != "committed":
            error = response.get("error") if isinstance(response.get("error"), dict) else {}
            raise RuntimeError(
                json.dumps(
                    {
                        "kind": kind,
                        "code": str(error.get("code") or "three_collection_commit_failed"),
                        "stage": str(error.get("stage") or response.get("stage") or "unknown"),
                        "message": str(error.get("message") or ""),
                        "details": error.get("details") if isinstance(error.get("details"), dict) else {},
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
    response = responses["main_filter"]

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    try:
        database = client[database_name]
        documents = {
            kind: list(database[name].find({}))
            for kind, name in COLLECTIONS.items()
        }
        if any(not value for value in documents.values()):
            raise RuntimeError("three_collection_items_missing")
        source_present = {
            kind: all(str(item.get("natural_text") or "").strip() for item in values)
            for kind, values in documents.items()
        }
        if not all(source_present.values()):
            raise RuntimeError("three_collection_natural_text_validation_failed")

        loader = _component("data_analysis/domain_bundle_loader.py")()
        loader.mongo_uri = mongo_uri
        loader.mongo_database = database_name
        loader.domain_collection = COLLECTIONS["domain"]
        loader.table_collection = COLLECTIONS["table_catalog"]
        loader.main_filter_collection = COLLECTIONS["main_filter"]
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
            == {
                "mongo_uri", "mongo_database", "domain_collection",
                "table_collection", "main_filter_collection", "mongo_timeout_ms",
            },
        }
        if not all(loader_checks.values()):
            raise RuntimeError(
                json.dumps(
                    {
                        "code": "three_collection_loader_contract_failed",
                        "checks": loader_checks,
                        "response_revision": response.get("revision"),
                        "loader_revision": runtime_bundle.get("revision"),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
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
            "stages": {kind: value.get("stage") for kind, value in responses.items()},
            "activation": {
                kind: value.get("activation_status") for kind, value in responses.items()
            },
        },
        "storage": {
            "collection_count": len(documents),
            "item_count": sum(len(values) for values in documents.values()),
            "item_counts": {kind: len(values) for kind, values in documents.items()},
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
    parser.add_argument("--domain-id", default="default", help=argparse.SUPPRESS)
    parser.add_argument("--environment", default="production", help=argparse.SUPPRESS)
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
