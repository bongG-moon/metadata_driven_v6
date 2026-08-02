from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "contracts" / "schemas"
PROPOSAL_SCHEMA_PATH = SCHEMA_DIR / "metadata-authoring-proposal.schema.json"
RESPONSE_SCHEMA_PATH = SCHEMA_DIR / "metadata-authoring-response.schema.json"
DRAFT_SCHEMA_PATH = SCHEMA_DIR / "metadata-authoring-draft.schema.json"
DRAFT_PATH = ROOT / "metadata" / "domain_packs" / "order_sales" / "authoring_draft.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _proposal_validator() -> Draft202012Validator:
    draft_schema = _load(DRAFT_SCHEMA_PATH)
    registry = Registry().with_resource(
        draft_schema["$id"],
        Resource.from_contents(draft_schema),
    )
    return Draft202012Validator(_load(PROPOSAL_SCHEMA_PATH), registry=registry)


def _response_validator() -> Draft202012Validator:
    return Draft202012Validator(_load(RESPONSE_SCHEMA_PATH))


def _clarification_proposal() -> dict:
    return {
        "contract_version": "metadata.authoring.proposal.v1",
        "status": "needs_clarification",
        "source_sha256": "b" * 64,
        "clarification": {
            "questions": [
                "주문 데이터에서 주문 금액으로 사용할 컬럼 이름은 무엇인가요?",
                "주문일시는 어느 시간대를 기준으로 해석해야 하나요?",
            ],
            "missing_fields": ["datasets.orders.fields.amount", "timezone"],
        },
    }


def _response(status: str) -> dict:
    response = {
        "contract_version": "metadata.authoring.response.v1",
        "response_type": "metadata_authoring",
        "status": status,
        "stage": "compiled",
        "authoring_kind": "domain",
        "metadata_contract_mode": "domain_package_v2",
        "domain_id": "order_sales",
        "environment": "validation",
        "llm_usage": {"draft_llm_calls": 1, "repair_llm_calls": 0},
        "response_sha256": "f" * 64,
    }
    if status == "ok":
        response.update(
            candidate_id="candidate:" + "a" * 64,
            candidate_sha256="a" * 64,
        )
    elif status == "error":
        response["error"] = {"code": "authoring_failed"}
    else:
        response.update(
            stage="metadata_clarification",
            clarification={
                "contract_version": "metadata.authoring.clarification.v1",
                **_clarification_proposal()["clarification"],
                "source_sha256": "b" * 64,
                "proposal_sha256": "c" * 64,
            },
        )
    return response


def test_new_and_existing_authoring_schemas_are_valid_draft_2020_12() -> None:
    Draft202012Validator.check_schema(_load(PROPOSAL_SCHEMA_PATH))
    Draft202012Validator.check_schema(_load(RESPONSE_SCHEMA_PATH))


def test_proposal_accepts_exactly_complete_draft_or_bounded_clarification() -> None:
    validator = _proposal_validator()
    validator.validate(
        {
            "contract_version": "metadata.authoring.proposal.v1",
            "status": "complete",
            "source_sha256": "b" * 64,
            "draft": _load(DRAFT_PATH),
        }
    )
    validator.validate(_clarification_proposal())


@pytest.mark.parametrize("status", ["ok", "error", "partial", ""])
def test_proposal_rejects_any_status_outside_closed_two_state_contract(status: str) -> None:
    proposal = _clarification_proposal()
    proposal["status"] = status
    with pytest.raises(ValidationError):
        _proposal_validator().validate(proposal)


@pytest.mark.parametrize("source_sha256", [None, "", "B" * 64, "a" * 63, "a" * 65])
def test_proposal_requires_exact_lowercase_source_sha256(source_sha256: str | None) -> None:
    proposal = _clarification_proposal()
    if source_sha256 is None:
        proposal.pop("source_sha256")
    else:
        proposal["source_sha256"] = source_sha256
    with pytest.raises(ValidationError):
        _proposal_validator().validate(proposal)


@pytest.mark.parametrize(
    ("forbidden_key", "value"),
    [
        ("draft", {}),
        ("candidate_id", "candidate:" + "a" * 64),
        ("candidate_sha256", "a" * 64),
        ("persisted", False),
    ],
)
def test_clarification_proposal_cannot_carry_draft_candidate_or_persistence_material(
    forbidden_key: str,
    value: object,
) -> None:
    proposal = _clarification_proposal()
    proposal[forbidden_key] = value
    with pytest.raises(ValidationError):
        _proposal_validator().validate(proposal)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("questions", []),
        ("questions", ["질문 1", "질문 2", "질문 3", "질문 4"]),
        ("questions", ["가" * 401]),
        ("missing_fields", [f"field_{index}" for index in range(33)]),
        ("missing_fields", ["f" * 129]),
    ],
)
def test_clarification_proposal_enforces_question_and_missing_field_bounds(
    field: str,
    value: list[str],
) -> None:
    proposal = _clarification_proposal()
    proposal["clarification"][field] = value
    with pytest.raises(ValidationError):
        _proposal_validator().validate(proposal)


def test_response_preserves_existing_ok_and_error_statuses() -> None:
    validator = _response_validator()
    validator.validate(_response("ok"))
    validator.validate(_response("error"))


def test_response_allows_three_split_bootstrap_calls_but_rejects_four() -> None:
    validator = _response_validator()
    response = _response("ok")
    response["llm_usage"]["draft_llm_calls"] = 3
    validator.validate(response)

    response["llm_usage"]["draft_llm_calls"] = 4
    with pytest.raises(ValidationError):
        validator.validate(response)


def test_response_accepts_needs_clarification_without_candidate_or_persistence() -> None:
    response = _response("needs_clarification")
    _response_validator().validate(response)
    assert "candidate_id" not in response
    assert "persisted" not in response


@pytest.mark.parametrize(
    ("forbidden_key", "value"),
    [
        ("candidate_id", "candidate:" + "a" * 64),
        ("candidate_sha256", "a" * 64),
        ("persisted", False),
        ("revision", 1),
        ("diff", {}),
        ("validation", {}),
        ("expires_at", "2026-08-02T12:00:00+00:00"),
        ("error", {"code": "not_an_error"}),
    ],
)
def test_response_clarification_cannot_leak_into_candidate_or_persistence_path(
    forbidden_key: str,
    value: object,
) -> None:
    response = deepcopy(_response("needs_clarification"))
    response[forbidden_key] = value
    with pytest.raises(ValidationError):
        _response_validator().validate(response)


def test_response_requires_bounded_clarification_payload_only_for_that_status() -> None:
    validator = _response_validator()

    missing = _response("needs_clarification")
    missing.pop("clarification")
    with pytest.raises(ValidationError):
        validator.validate(missing)

    too_many = _response("needs_clarification")
    too_many["clarification"]["questions"] = ["1", "2", "3", "4"]
    with pytest.raises(ValidationError):
        validator.validate(too_many)

    accidental = _response("ok")
    accidental["clarification"] = _clarification_proposal()["clarification"]
    with pytest.raises(ValidationError):
        validator.validate(accidental)
