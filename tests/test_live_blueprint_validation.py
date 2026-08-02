from __future__ import annotations

import json
from pathlib import Path

import pytest

import tools.validate_live_blueprint_authoring as live_blueprint
from reference_runtime.authoring_blueprint import (
    build_executable_blueprint,
    merge_blueprint_annotations,
)
from reference_runtime.authoring_source_manifest import extract_authoring_source_manifest
from reference_runtime.domain_packages import compile_domain_package
from tools.gemini_validation_support import DEFAULT_GEMINI_MODEL


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "validation" / "order_sales_metadata_input.txt"
DRAFT = ROOT / "metadata" / "domain_packs" / "order_sales" / "authoring_draft.json"


def _fixture(tmp_path: Path, *, environment: str = "test") -> tuple[Path, Path, dict, dict, str]:
    source_text = SOURCE.read_text(encoding="utf-8-sig").strip()
    manifest = extract_authoring_source_manifest(source_text)
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    blueprint = build_executable_blueprint(
        draft,
        domain_id="order_sales",
        environment=environment,
        source_manifest=manifest,
    )
    blueprint_path = tmp_path / "trusted_executable_blueprint.json"
    pin_path = tmp_path / "trusted_executable_blueprint.sha256"
    blueprint_path.write_text(
        json.dumps(blueprint, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    pin_path.write_text(str(blueprint["blueprint_sha256"]) + "\n", encoding="ascii")
    return blueprint_path, pin_path, blueprint, manifest, source_text


def test_trusted_blueprint_loader_uses_sidecar_then_admin_rebinds(tmp_path: Path) -> None:
    blueprint_path, pin_path, original, manifest, _source_text = _fixture(tmp_path)
    target, target_pin, evidence = live_blueprint._load_trusted_blueprint(
        blueprint_path=blueprint_path,
        pin_path=pin_path,
        source_manifest=manifest,
        domain_id="order_sales",
        environment="isolated_test",
    )
    assert evidence["checked_in_pin_source"] == "separate_admin_sidecar"
    assert evidence["target_pin_source"] == "trusted_admin_build_output"
    assert evidence["environment_rebound_by_admin_build"] is True
    assert evidence["checked_in_blueprint_sha256"] == original["blueprint_sha256"]
    assert target["environment"] == "isolated_test"
    assert target_pin == target["blueprint_sha256"]
    assert target["executable_sha256"] == original["executable_sha256"]


def test_blueprint_negative_matrix_rejects_tamper_before_any_model_call(tmp_path: Path) -> None:
    blueprint_path, pin_path, _original, manifest, source_text = _fixture(tmp_path)
    blueprint, pin, _evidence = live_blueprint._load_trusted_blueprint(
        blueprint_path=blueprint_path,
        pin_path=pin_path,
        source_manifest=manifest,
        domain_id="order_sales",
        environment="test",
    )
    rows = live_blueprint._direct_negative_cases(
        blueprint=blueprint,
        blueprint_pin=pin,
        domain_id="order_sales",
        environment="test",
        source_manifest=manifest,
        source_text=source_text,
    )
    assert len(rows) == 9
    assert all(row["passed"] for row in rows), rows
    assert all(row["model_calls"] == 0 for row in rows)
    by_id = {row["case_id"]: row for row in rows}
    assert by_id["simple_executable_tamper"]["failure"]["reason"] == "executable_hash_mismatch"
    assert by_id["recomputed_executable_tamper"]["failure"]["reason"] == "blueprint_external_pin_mismatch"
    assert by_id["annotation_executable_injection"]["failure"]["reason"] == "annotation_key_not_allowed"


def test_live_blueprint_harness_calls_provider_once_and_persists_hashes_only(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    blueprint_path, pin_path, _original, manifest, source_text = _fixture(tmp_path)

    class FakeProvider:
        def __init__(self, **kwargs):
            self.model = str(kwargs["model"])
            self.calls = 0

        def invoke(self, prompt: str) -> str:
            self.calls += 1
            assert "annotation-only metadata authoring pass" in prompt
            return json.dumps(
                {
                    "display_name": "주문 매출 검증",
                    "description": "등록된 주문 및 매출 메타데이터입니다.",
                },
                ensure_ascii=False,
            )

        def evidence(self):
            return {
                "model": self.model,
                "calls": self.calls,
                "prompt_sha256": ["a" * 64],
                "provider_response_sha256": ["b" * 64],
                "provider_model_versions": ["fake"],
                "finish_reasons": ["STOP"],
                "candidate_text_bytes": [128],
                "usage": {"prompt_tokens": 10, "candidate_tokens": 5, "total_tokens": 15},
            }

    def fake_replay(**kwargs):
        proposal = json.loads(kwargs["raw_response"])
        draft = merge_blueprint_annotations(
            kwargs["blueprint"],
            {
                "display_name": proposal["display_name"],
                "description": proposal["description"],
            },
            expected_blueprint_sha256=kwargs["blueprint_pin"],
            expected_domain_id=kwargs["domain_id"],
            expected_environment=kwargs["environment"],
            source_manifest=manifest,
        )
        package = compile_domain_package(
            draft,
            kwargs["domain_id"],
            kwargs["environment"],
            revision=kwargs["revision"],
            lifecycle_status="validated",
        )
        return (
            {
                "status": "ok",
                "stage": "prepared",
                "package_sha256": package["package_sha256"],
                "bundle_sha256": package["bundle_sha256"],
                "catalog_sha256": package["runtime_catalog"]["catalog_sha256"],
                "llm_usage": {"annotation_llm_calls": 1, "repair_llm_calls": 0},
            },
            1,
        )

    monkeypatch.setattr(live_blueprint, "GeminiJsonModel", FakeProvider)
    monkeypatch.setattr(
        live_blueprint,
        "_annotation_prompt",
        lambda source, defaults: "annotation-only metadata authoring pass",
    )
    monkeypatch.setattr(live_blueprint, "_component_replay", fake_replay)
    monkeypatch.setattr(
        live_blueprint,
        "_component_guard_negatives",
        lambda **kwargs: [{"case_id": "fake", "model_calls": 0, "passed": True}],
    )
    row = live_blueprint.validate_blueprint_source(
        SOURCE,
        blueprint_path=blueprint_path,
        blueprint_pin_path=pin_path,
        api_key="fake-secret-key",
        model=DEFAULT_GEMINI_MODEL,
        timeout_seconds=5,
        domain_id="order_sales",
        environment="test",
        revision=1,
    )
    assert row["passed"] is True, row
    assert row["provider"]["calls"] == 1
    assert row["checks"]["executable_canonical_bytes_unchanged"] is True
    assert row["checks"]["standalone_package_parity"] is True
    serialized = json.dumps(row, ensure_ascii=False)
    assert "fake-secret-key" not in serialized
    assert source_text not in serialized


def test_live_blueprint_harness_rejects_non_exact_model(tmp_path: Path) -> None:
    blueprint_path, pin_path, _original, _manifest, _source_text = _fixture(tmp_path)
    with pytest.raises(RuntimeError, match="^exact_gemini_model_required$"):
        live_blueprint.validate_blueprint_source(
            SOURCE,
            blueprint_path=blueprint_path,
            blueprint_pin_path=pin_path,
            api_key="fake-secret-key",
            model="gemini-other",
            timeout_seconds=5,
            domain_id="order_sales",
            environment="test",
            revision=1,
        )
