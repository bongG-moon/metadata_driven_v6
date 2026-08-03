from __future__ import annotations

import pytest

from tools.flow_builder_support import BuildContractError
from tools.validate_langflow_http_e2e import (
    REFERENCE_INSTANT,
    _canonical_responses,
    _run_url,
    _validation_clock_evidence,
    extract_terminal_evidence,
)


def test_langflow_1_9_2_run_url_does_not_depend_on_auth_header_type() -> None:
    expected = "http://127.0.0.1:7873/api/v1/run/flow-id"

    assert _run_url("http://127.0.0.1:7873", "flow-id", {"Authorization": "Bearer x"}) == expected
    assert _run_url("http://127.0.0.1:7873", "flow-id", {"x-api-key": "x"}) == expected


def test_validation_clock_accepts_environment_only_seam(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("V6_VALIDATION_MODE", "1")
    monkeypatch.setenv("V6_VALIDATION_REFERENCE_INSTANT", REFERENCE_INSTANT)

    evidence = _validation_clock_evidence({})

    assert evidence["checks"] == {
        "validation_mode_enabled": True,
        "reference_instant_exact": True,
        "timezone_internal": True,
        "flow_clock_tweak_used": False,
    }


def test_validation_clock_rejects_missing_server_seam(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("V6_VALIDATION_MODE", raising=False)
    monkeypatch.delenv("V6_VALIDATION_REFERENCE_INSTANT", raising=False)

    with pytest.raises(BuildContractError, match="validation_clock_environment_not_configured"):
        _validation_clock_evidence({})


def test_terminal_validation_does_not_require_inter_node_response_hash() -> None:
    response = {
        "contract_version": "response.v1",
        "status": "ok",
        "trace": {"route": {"route": "deterministic"}, "usage": {}},
        "state": {"state_version": 1},
        "analysis": {},
        "answer_sections": {},
        "data_refs": [],
    }
    payload = {
        "outputs": [
            {
                "component_id": "chat_output",
                "results": {"message": {"text": "완료"}},
            },
            {
                "component_id": "gaia_output",
                "results": {"gaia": {"contract_version": "gaia.metadata.v1"}},
            },
            {
                "component_id": "api_response_terminal",
                "results": {"api_response": response},
            },
        ]
    }

    assert _canonical_responses(payload) == [response]
    evidence = extract_terminal_evidence(payload)
    assert evidence["canonical_hash_count"] == 1
    assert evidence["canonical_response_sha256"]
    assert evidence["terminal_equivalent"] is True
