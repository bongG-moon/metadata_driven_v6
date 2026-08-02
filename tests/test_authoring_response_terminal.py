from __future__ import annotations

from copy import deepcopy

import pytest

from reference_runtime.canonical import ContractError, sha256_json
from reference_runtime.presenter import validate_authoring_response_hash


def _prepared_response() -> dict:
    material = {
        "contract_version": "metadata.authoring.response.v1",
        "response_type": "metadata_authoring",
        "status": "ok",
        "stage": "prepared",
        "authoring_kind": "domain_policy",
        "metadata_contract_mode": "domain_package_v2",
        "domain_id": "order_sales",
        "environment": "validation",
        "candidate_id": "candidate:" + "1" * 64,
        "candidate_sha256": "1" * 64,
        "package_sha256": "2" * 64,
        "bundle_sha256": "3" * 64,
        "catalog_sha256": "4" * 64,
        "revision": 2,
        "persisted": False,
        "diff": {"authoring_kind": "domain_policy"},
        "unchanged_section_checks": {"datasets": True, "metrics": True},
        "validation": {
            "schema": "passed",
            "semantic_lint": "passed",
            "dependency_closure": "passed",
            "hash_seal": "passed",
            "section_ownership": "passed",
        },
        "expires_at": "2026-08-01T12:00:00+00:00",
        "llm_usage": {"draft_llm_calls": 1, "repair_llm_calls": 0},
    }
    return {**material, "response_sha256": sha256_json(material)}


def test_authoring_response_terminal_accepts_closed_hash_sealed_response() -> None:
    response = _prepared_response()
    assert validate_authoring_response_hash(response) is response


@pytest.mark.parametrize("mutation", ["value", "extra", "hash"])
def test_authoring_response_terminal_rejects_tamper_and_unknown_fields(mutation: str) -> None:
    response = deepcopy(_prepared_response())
    if mutation == "value":
        response["revision"] = 99
    elif mutation == "extra":
        response["provider_output"] = "must never pass the terminal"
        material = {key: value for key, value in response.items() if key != "response_sha256"}
        response["response_sha256"] = sha256_json(material)
    else:
        response["response_sha256"] = "f" * 64
    with pytest.raises(ContractError) as raised:
        validate_authoring_response_hash(response)
    assert raised.value.code == "response_contract_error"
