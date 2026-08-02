from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from tools.normalized_authoring_source import (
    NormalizedAuthoringSourceError,
    load_verified_normalized_authoring_source,
)


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = (
    ROOT
    / "metadata"
    / "authoring"
    / "main_filters"
    / "main_variable_v6_normalized.provenance.json"
)
DOMAIN_POLICY_PROVENANCE = (
    ROOT
    / "metadata"
    / "authoring"
    / "domain"
    / "domain_policy_v6_normalized.provenance.json"
)
DATASET_PROVENANCE = (
    ROOT
    / "metadata"
    / "authoring"
    / "table_catalog"
    / "data_catalog_v6_normalized.provenance.json"
)


def test_checked_in_v6_main_filter_companion_is_exactly_pinned_and_alias_only() -> None:
    text, evidence = load_verified_normalized_authoring_source(
        root=ROOT,
        provenance_path=PROVENANCE,
        expected_source_kind="main_filter",
    )

    assert "별칭 카드의 안정 식별자는 field:DATE" in text
    assert evidence == {
        "contract_version": "metadata.normalized-authoring-source-provenance.v1",
        "source_kind": "main_filter",
        "original_content_sha256": "c6d8fd3c2e23d4a860b86c0c09f57ea26f5526f78c21697a233a61d3b2d58ae3",
        "normalized_content_sha256": "64ab5b98280fa680bab33004443524c4f369857fa68d94cff7524b548d8a6d77",
        "source_manifest_sha256": "488f4f281e9620afb7fe0fe3deb6be9381e63df2b196667299b52716f205dd89",
        "required_sections": ["aliases"],
        "dataset_count": 0,
        "field_count": 0,
        "field_bindings": 0,
        "alias_bindings": 53,
        "source_text_persisted": False,
    }


def test_checked_in_domain_policy_companion_is_pinned_and_inventory_free() -> None:
    text, evidence = load_verified_normalized_authoring_source(
        root=ROOT,
        provenance_path=DOMAIN_POLICY_PROVENANCE,
        expected_source_kind="domain_policy",
    )

    assert text == (
        "기존 제조 도메인의 실행용 메타데이터는 변경하지 않습니다.\n"
        "운영자가 노드 입력으로 지정한 의도 해석 지침, 답변 표시 지침, 등록 함수 카드와 출력 정책만 갱신합니다.\n"
        "등록되지 않은 사실이나 실행 규칙을 새로 만들지 않습니다.\n"
    )
    assert evidence == {
        "contract_version": "metadata.normalized-authoring-source-provenance.v1",
        "source_kind": "domain_policy",
        "original_content_sha256": "dd5f53b5b6eb5ce92eac447ccdc476ca4d6448224cc0855925536b2087b2faae",
        "normalized_content_sha256": "fbbfe05e6356585a59b989073df641c2d517aa077e2b1489a4a0a2b3b8c3b619",
        "source_manifest_sha256": "4ddc256e723ba1e053a1d19a2831dc246f4478fa8d8a3ae89d7a02be971e0221",
        "required_sections": [],
        "dataset_count": 0,
        "field_count": 0,
        "field_bindings": 0,
        "alias_bindings": 0,
        "source_text_persisted": False,
    }


def test_checked_in_dataset_companion_is_pinned_and_dataset_field_only() -> None:
    text, evidence = load_verified_normalized_authoring_source(
        root=ROOT,
        provenance_path=DATASET_PROVENANCE,
        expected_source_kind="dataset",
    )

    assert "equipment_assign 데이터셋은 장비 배정 현황" in text
    assert evidence == {
        "contract_version": "metadata.normalized-authoring-source-provenance.v1",
        "source_kind": "dataset",
        "original_content_sha256": "8ecbb8dd0b78276a0e5faf0ae468b47075ec3432c88051a4a216ce4fcb56dd9d",
        "normalized_content_sha256": "a7d7e93731723151b35b7d53a684ee53a7d5da2ff355fe620df5dfad332acc8e",
        "source_manifest_sha256": "a8540897f6e160d122628a9c0d9a0a4cd53df683e8af456e536ce664400b5226",
        "required_sections": ["datasets", "fields"],
        "dataset_count": 10,
        "field_count": 47,
        "field_bindings": 196,
        "alias_bindings": 0,
        "source_text_persisted": False,
    }


def _copy_fixture(tmp_path: Path) -> Path:
    target = tmp_path / "metadata" / "authoring" / "main_filters"
    target.mkdir(parents=True)
    for name in (
        "main_variable.txt",
        "main_variable_v6_normalized.txt",
        "main_variable_v6_normalized.provenance.json",
    ):
        shutil.copy2(PROVENANCE.parent / name, target / name)
    return target / PROVENANCE.name


def test_normalized_companion_tamper_fails_closed(tmp_path: Path) -> None:
    provenance = _copy_fixture(tmp_path)
    companion = provenance.with_name("main_variable_v6_normalized.txt")
    companion.write_text(companion.read_text(encoding="utf-8") + "\n변조", encoding="utf-8")

    with pytest.raises(NormalizedAuthoringSourceError) as raised:
        load_verified_normalized_authoring_source(
            root=tmp_path,
            provenance_path=provenance,
            expected_source_kind="main_filter",
        )

    assert raised.value.code == "normalized_source_companion_hash_mismatch"


def test_normalized_source_provenance_rejects_unknown_contract_key(tmp_path: Path) -> None:
    provenance = _copy_fixture(tmp_path)
    value = json.loads(provenance.read_text(encoding="utf-8"))
    value["unexpected"] = True
    provenance.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(NormalizedAuthoringSourceError) as raised:
        load_verified_normalized_authoring_source(
            root=tmp_path,
            provenance_path=provenance,
            expected_source_kind="main_filter",
        )

    assert raised.value.code == "normalized_source_provenance_contract_invalid"


def _copy_domain_policy_fixture(tmp_path: Path) -> Path:
    target = tmp_path / "metadata" / "authoring" / "domain"
    target.mkdir(parents=True)
    for name in (
        "domain_knowledge.txt",
        "domain_policy_v6_normalized.txt",
        "domain_policy_v6_normalized.provenance.json",
    ):
        shutil.copy2(DOMAIN_POLICY_PROVENANCE.parent / name, target / name)
    return target / DOMAIN_POLICY_PROVENANCE.name


def test_domain_policy_companion_tamper_fails_closed(tmp_path: Path) -> None:
    provenance = _copy_domain_policy_fixture(tmp_path)
    companion = provenance.with_name("domain_policy_v6_normalized.txt")
    companion.write_bytes(companion.read_bytes() + b"\n")

    with pytest.raises(NormalizedAuthoringSourceError) as raised:
        load_verified_normalized_authoring_source(
            root=tmp_path,
            provenance_path=provenance,
            expected_source_kind="domain_policy",
        )

    assert raised.value.code == "normalized_source_companion_hash_mismatch"


def test_domain_policy_original_tamper_fails_closed(tmp_path: Path) -> None:
    provenance = _copy_domain_policy_fixture(tmp_path)
    original = provenance.with_name("domain_knowledge.txt")
    original.write_bytes(original.read_bytes() + b"\n")

    with pytest.raises(NormalizedAuthoringSourceError) as raised:
        load_verified_normalized_authoring_source(
            root=tmp_path,
            provenance_path=provenance,
            expected_source_kind="domain_policy",
        )

    assert raised.value.code == "normalized_source_original_hash_mismatch"


def _copy_dataset_fixture(tmp_path: Path) -> Path:
    target = tmp_path / "metadata" / "authoring" / "table_catalog"
    target.mkdir(parents=True)
    for name in (
        "data_catalog.txt",
        "data_catalog_v6_normalized.txt",
        "data_catalog_v6_normalized.provenance.json",
    ):
        shutil.copy2(DATASET_PROVENANCE.parent / name, target / name)
    return target / DATASET_PROVENANCE.name


def test_dataset_companion_tamper_fails_closed(tmp_path: Path) -> None:
    provenance = _copy_dataset_fixture(tmp_path)
    companion = provenance.with_name("data_catalog_v6_normalized.txt")
    companion.write_bytes(companion.read_bytes() + b"\n")

    with pytest.raises(NormalizedAuthoringSourceError) as raised:
        load_verified_normalized_authoring_source(
            root=tmp_path,
            provenance_path=provenance,
            expected_source_kind="dataset",
        )

    assert raised.value.code == "normalized_source_companion_hash_mismatch"


def test_dataset_original_tamper_fails_closed(tmp_path: Path) -> None:
    provenance = _copy_dataset_fixture(tmp_path)
    original = provenance.with_name("data_catalog.txt")
    original.write_bytes(original.read_bytes() + b"\n")

    with pytest.raises(NormalizedAuthoringSourceError) as raised:
        load_verified_normalized_authoring_source(
            root=tmp_path,
            provenance_path=provenance,
            expected_source_kind="dataset",
        )

    assert raised.value.code == "normalized_source_original_hash_mismatch"
