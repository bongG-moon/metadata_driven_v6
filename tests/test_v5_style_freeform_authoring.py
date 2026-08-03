from __future__ import annotations

import importlib.util
import hashlib
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _authoring_namespace() -> dict:
    path = ROOT / "langflow_components" / "metadata_authoring" / "00_metadata_authoring_engine.py"
    spec = importlib.util.spec_from_file_location("v6_authoring_component_for_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module.MetadataAuthoringEngine._prepare_v2.__globals__


PRODUCTION_TODAY_TEXT = """당일용 생산 실적 데이터는 production_today로 등록해줘.
화면에 보일 이름은 Production Today이면 돼.
당일 생산 실적 질문에 사용하는 Oracle 데이터야.
production_today는 production 계열의 당일용 생산 실적 source야.
selection_criteria의 time_scope는 current_day로 저장해줘.
selection_criteria의 use_when은 오늘 생산, 당일 생산, 현재 생산, 현시간 기준 생산이고 exclude_when은 어제 생산, 전일 생산, 특정 과거일 생산이야.
조회할 때 DATE 값은 WORK_DT 컬럼에 넣어서 조회하고, DATE는 조회 필수 기준일이야.
DATE는 YYYYMMDD 형식이야.
수량은 PRODUCTION 컬럼을 사용하고, 이 값은 생산량이야.
source는 oracle이고 db_key는 PNT_RPT야.

query_template:

--쿼리 작성
SELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1
        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER
        , OPER_NAME, OPER_SEQ, PRODUCTION
FROM PROD_TABLE
WHERE 1=1
AND WORK_DATE = {DATE}

filter_mappings는 DATE -> WORK_DATE, MODE -> MODE, DEN -> DENSITY, TECH -> TECH, ORG -> ORG, PKG_TYPE1 -> PKG1, PKG_TYPE2 -> PKG2, LEAD -> LEAD, MCP_NO -> MCP_NO, TSV_DIE_TYP -> TSV_DIE_TYP, DEVICE -> DEVICE, DEVICE_DESC -> DEVICE_DESC, OPER_NUM -> OPER, OPER_NAME -> OPER_NAME로 연결해줘.
"""


PRODUCTION_HISTORY_TEXT = """이력 생산 실적 데이터는 production으로 등록해줘.
화면에 보일 이름은 Production History이면 돼.
production은 production 계열의 이력 생산 실적 source야.
selection_criteria의 time_scope는 history로 저장해줘.
selection_criteria의 use_when은 어제 생산, 전일 생산, 특정 과거일 생산이고 exclude_when은 오늘 생산, 당일 생산, 현재 생산, 현시간 기준 생산이야.
조회할 때 DATE 값은 WORK_DT 컬럼에 넣어서 조회하고, DATE는 조회 필수 기준일이야. DATE는 YYYYMMDD형식이야
수량은 PRODUCTION 컬럼을 사용하고, 이 값은 생산량이야.
source는 oracle이고 db_key는 PNT_RPT야.

query_template:
SELECT WORK_DATE, SHIFT, FACTORY, FAB, FAMILY, MODE, DENSITY, TECH, ORG, PKG1
        , PKG2, LEAD, MCP_NO, TSV_DIE_TYP, DEVICE, DEVICE_DESC, DIE_ATTACH_QTY, NETDIE_300_CNT, OPER
        , OPER_NAME, OPER_SEQ, PRODUCTION
FROM PROD_TABLE2
WHERE 1=1
AND WORK_DATE = {DATE}

filter_mappings는 DATE -> WORK_DATE, MODE -> MODE, DEN -> DENSITY, TECH -> TECH, ORG -> ORG, PKG_TYPE1 -> PKG1, PKG_TYPE2 -> PKG2, LEAD -> LEAD, MCP_NO -> MCP_NO, TSV_DIE_TYP -> TSV_DIE_TYP, DEVICE -> DEVICE, DEVICE_DESC -> DEVICE_DESC, OPER_NUM -> OPER, OPER_NAME -> OPER_NAME로 연결해줘.
"""


DP_GROUP_TEXT = """DP 공정 그룹을 등록해줘.
display_name은 DP이고 유의어는 DP, D/P, DP공정, D/P공정, DP 공정, D/P 공정이야.
field는 OPER_NAME이야.
포함 공정은 OPER_NAME 값 WET1, WET2, L/T1, L/T2, B/G1, B/G2, H/S1, H/S2, W/S1, W/S2, WSD1, WSD2, WEC1, WEC2, WLS1, WLS2, WVI, UV, C/C1이야.
별칭마다 별도 item을 만들지 말고 공정그룹 하나로 저장해.
"""


TARGET_GOODOCS_TEXT = """PKG 계획 데이터는 target으로 등록해줘.
화면에 보일 이름은 PKG Target Goodocs Plan이면 돼.
Goodocs PKG 계획 문서에서 일자와 제품 속성별 INPUT계획, OUT계획을 가져오는 데이터야.
이 데이터는 Goodocs source이고 별도 필수 조회 파라미터는 없어.
DATE 형식은 YYYY-MM-DD야.
계획 수량은 INPUT 계획과 OUT 계획 두 컬럼에 있는 값을 모두 사용해.
목표2 문서에는 DATE, Mode, DEN, TECH, PKG1, PKG2, LEAD, ORG, MCP NO, INPUT 계획, OUT 계획 컬럼이 있어.
filter_mappings는 DATE -> DATE, MODE -> Mode, DEN -> DEN, TECH -> TECH, ORG -> ORG, PKG_TYPE1 -> PKG1, PKG_TYPE2 -> PKG2, LEAD -> LEAD, MCP_NO -> MCP NO로 연결해줘.
"""


def test_v5_style_dataset_card_is_deterministically_expanded_from_worker_text() -> None:
    namespace = _authoring_namespace()
    compact = {
        "dataset_cards": [
            {
                "dataset_id": "production_today",
                "display_name": "Production Today",
                "family": "production",
                "source_type": "oracle",
                "fields": [
                    {"id": "DATE", "col": "WORK_DT"},
                    {"id": "PRODUCTION", "col": "PRODUCTION", "semantic_type": "number"},
                ],
            }
        ]
    }

    reconciliation: dict = {}
    patch = namespace["_expand_freeform_dataset_fragment"](
        compact,
        PRODUCTION_TODAY_TEXT,
        reconciliation_out=reconciliation,
    )
    patched, query_evidence = namespace["apply_dataset_source_configs_from_text"](
        patch,
        PRODUCTION_TODAY_TEXT,
        require_complete=True,
    )
    dataset = patched["datasets"]["production_today"]

    # The explicit v5 filter_mappings contract wins over a conflicting prose
    # sentence, while the SQL body is copied from the worker text unchanged.
    assert dataset["fields"]["DATE"]["physical_column"] == "WORK_DATE"
    assert dataset["fields"]["DEN"]["physical_column"] == "DENSITY"
    assert dataset["fields"]["DATE"]["semantic_type"] == "date"
    assert dataset["fields"]["DEN"]["semantic_type"] == "string"
    assert dataset["fields"]["MODE"]["semantic_type"] == "string"
    assert dataset["fields"]["OPER_SEQ"]["semantic_type"] == "number"
    assert dataset["fields"]["PRODUCTION"]["semantic_type"] == "number"
    assert dataset["selection_criteria"] == {
        "time_scope": "current_day",
        "use_when": ["오늘 생산", "당일 생산", "현재 생산", "현시간 기준 생산"],
        "exclude_when": ["어제 생산", "전일 생산", "특정 과거일 생산"],
    }
    assert dataset["source_config"]["db_key"] == "PNT_RPT"
    assert dataset["source_config"]["required_params"] == ["DATE"]
    assert dataset["source_config"]["query_template"].startswith("--쿼리 작성\nSELECT WORK_DATE")
    assert dataset["source_config"]["query_template"].endswith("AND WORK_DATE = {DATE}")
    assert query_evidence["query_count"] == 1
    assert reconciliation["filter_mapping_count"] == 14


def test_model_field_types_and_dataset_identity_cannot_override_worker_text() -> None:
    namespace = _authoring_namespace()
    compact = {
        "dataset_cards": [
            {
                "dataset_id": "pkg_target_goodocs_plan",
                "display_name": "wrong model label",
                "family": "wrong_family",
                "source_type": "oracle",
                "fields": [
                    {"id": "DATE", "col": "DATE", "semantic_type": "number"},
                    {"id": "MODE", "col": "Mode", "semantic_type": "number"},
                    {"id": "DEN", "col": "DEN", "semantic_type": "number"},
                    {"id": "INPUT_PLAN_QTY", "col": "INPUT 계획", "semantic_type": "date"},
                    {"id": "OUT_PLAN_QTY", "col": "OUT 계획", "semantic_type": "date"},
                ],
            }
        ]
    }
    reconciliation: dict = {}

    patch = namespace["_expand_freeform_dataset_fragment"](
        compact,
        TARGET_GOODOCS_TEXT,
        reconciliation_out=reconciliation,
    )
    dataset = patch["datasets"]["target"]

    assert set(patch["datasets"]) == {"target"}
    assert dataset["family"] == "target"
    assert dataset["source_type"] == "goodocs"
    assert dataset["fields"]["DATE"]["semantic_type"] == "date"
    assert dataset["fields"]["MODE"]["semantic_type"] == "string"
    assert dataset["fields"]["DEN"]["semantic_type"] == "string"
    assert dataset["fields"]["INPUT_PLAN_QTY"]["semantic_type"] == "number"
    assert dataset["fields"]["OUT_PLAN_QTY"]["semantic_type"] == "number"
    assert reconciliation["dataset_identity_overrides"] == [
        {"proposed": "pkg_target_goodocs_plan", "source_authority": "target"}
    ]
    assert reconciliation["discarded_model_semantic_type_count"] == 5


def test_multi_item_txt_does_not_bleed_fields_between_dataset_cards() -> None:
    namespace = _authoring_namespace()
    compact = {
        "dataset_cards": [
            {
                "dataset_id": "production_today",
                "display_name": "Production Today",
                "family": "production",
                "source_type": "oracle",
                "fields": [
                    {"id": "DATE", "col": "WORK_DATE"},
                    {"id": "PRODUCTION", "col": "PRODUCTION"},
                    {"id": "INPUT_PLAN_QTY", "col": "INPUT 계획"},
                ],
            },
            {
                "dataset_id": "target",
                "display_name": "Target",
                "family": "target",
                "source_type": "goodocs",
                "fields": [
                    {"id": "DATE", "col": "DATE"},
                    {"id": "INPUT_PLAN_QTY", "col": "INPUT 계획"},
                    {"id": "PRODUCTION", "col": "PRODUCTION"},
                ],
            },
        ]
    }

    patch = namespace["_expand_freeform_dataset_fragment"](
        compact,
        PRODUCTION_TODAY_TEXT + "\n\n" + TARGET_GOODOCS_TEXT,
    )

    production_fields = patch["datasets"]["production_today"]["fields"]
    target_fields = patch["datasets"]["target"]["fields"]
    assert "PRODUCTION" in production_fields
    assert "INPUT_PLAN_QTY" not in production_fields
    assert "INPUT_PLAN_QTY" in target_fields
    assert "PRODUCTION" not in target_fields


def test_domain_business_item_discards_redundant_model_profile() -> None:
    namespace = _authoring_namespace()
    reconciliation: dict = {}

    patch = namespace["_expand_freeform_domain_fragment"](
        {
            "items": [
                {
                    "section": "profile",
                    "key": "default",
                    "payload": {"display_name": "Generic profile"},
                },
                {
                    "section": "metrics",
                    "key": "WIP_QTY",
                    "payload": {
                        "metric_id": "WIP_QTY",
                        "value_type": "number",
                        "unit": "unit",
                    },
                },
            ]
        },
        reconciliation_out=reconciliation,
    )

    assert "domain_id" not in patch
    assert set(patch) == {"metrics"}
    assert reconciliation["discarded_redundant_profile_count"] == 1


def test_domain_metric_worker_keys_normalize_to_runtime_metric_contract() -> None:
    namespace = _authoring_namespace()

    patch = namespace["_expand_freeform_domain_fragment"](
        {
            "items": [
                {
                    "section": "metrics",
                    "key": "WIP_QTY",
                    "payload": {
                        "display_name": "재공 수량",
                        "aliases": ["재공", "WIP"],
                        "dataset_family": "wip",
                        "source_field": "WIP",
                        "value_type": "number",
                        "unit": "unit",
                        "exclude_nulls": True,
                        "addable": True,
                        "default_aggregation": "sum",
                        "allowed_aggregations": ["sum"],
                    },
                }
            ]
        }
    )

    assert patch["metrics"]["WIP_QTY"] == {
        "metric_id": "WIP_QTY",
        "value_type": "number",
        "unit": "unit",
        "null_policy": "exclude_from_sum",
        "zero_policy": "preserve_zero",
        "additivity": {"default": "additive", "allowed_rollups": ["sum"]},
        "aliases": ["재공", "WIP"],
        "source_binding": {"dataset_family": "wip", "field": "WIP"},
    }


def test_domain_metric_binding_is_recovered_from_operator_text() -> None:
    namespace = _authoring_namespace()

    patch = namespace["_expand_freeform_domain_fragment"](
        {
            "items": [
                {
                    "section": "metrics",
                    "key": "WIP_QTY",
                    "payload": {
                        "aliases": ["WIP"],
                        "default_aggregation": "sum",
                    },
                }
            ]
        },
        source_text="Use the WIP column from the wip family dataset.",
    )

    assert patch["metrics"]["WIP_QTY"]["source_binding"] == {
        "dataset_family": "wip",
        "field": "WIP",
    }


def test_wip_source_field_is_numeric_metric_binding() -> None:
    namespace = _authoring_namespace()

    semantic_type = namespace["_freeform_field_semantic_type"](
        "WIP", "WIP", "수량은 WIP 컬럼을 사용하고 이 값은 재공 수량이야."
    )
    roles = namespace["_freeform_field_roles"](
        "WIP", "WIP", {}, semantic_type
    )

    assert semantic_type == "number"
    assert roles == ["aggregate", "metric", "output"]


def test_domain_grain_worker_keys_normalize_to_runtime_contract() -> None:
    namespace = _authoring_namespace()

    patch = namespace["_expand_freeform_domain_fragment"](
        {
            "items": [
                {
                    "section": "grains",
                    "key": "product",
                    "payload": {
                        "display_name": "제품",
                        "grain_keys": ["TECH", "DEN", "MODE", "MCP_NO야"],
                    },
                }
            ]
        }
    )

    assert patch["grains"]["product"] == {
        "grain_id": "product",
        "keys": ["TECH", "DEN", "MODE", "MCP_NO"],
    }


def test_domain_recipe_worker_text_builds_typed_aggregate_template() -> None:
    namespace = _authoring_namespace()
    source_text = (
        "Register the product aggregate recipe as product.standard. "
        "grain is product and key is TECH, DEN, MODE, PKG_TYPE1, PKG_TYPE2, LEAD, MCP_NO."
    )

    patch = namespace["_expand_freeform_domain_fragment"](
        {
            "items": [
                {
                    "section": "recipes",
                    "key": "product_standard",
                    "payload": {
                        "aliases": ["by product", "product summary"],
                        "description": "Aggregate by product",
                    },
                }
            ]
        },
        source_text=source_text,
    )

    recipe = patch["recipes"]["product.standard"]
    assert recipe["recipe_id"] == "product.standard"
    assert recipe["required_slots"] == ["dataset_refs", "metric_refs"]
    assert recipe["grain"]["entity_id"] == "product"
    assert recipe["grain"]["keys"] == [
        "TECH", "DEN", "MODE", "PKG_TYPE1", "PKG_TYPE2", "LEAD", "MCP_NO"
    ]
    assert recipe["default_operation_template"] == {
        "op": "aggregate",
        "group_by": [
            "TECH", "DEN", "MODE", "PKG_TYPE1", "PKG_TYPE2", "LEAD", "MCP_NO"
        ],
        "metrics": [
            {
                "as_ref": "$metric.id",
                "field_ref": "$metric.field",
                "function_ref": "$metric.rollup",
            }
        ],
    }


def test_domain_recipe_alias_drops_conversational_sentence_ending() -> None:
    namespace = _authoring_namespace()
    recipe_id, recipe = namespace["_normalize_freeform_recipe"](
        "product.standard",
        {"aliases": ["제품별", "제품 집계야"]},
        "grain is product and key is TECH, DEN, MODE.",
    )

    assert recipe_id == "product.standard"
    assert recipe["aliases"] == ["제품별", "제품 집계"]


def test_dataset_time_scope_is_inferred_from_worker_friendly_source_type() -> None:
    namespace = _authoring_namespace()

    assert namespace["_freeform_selection_criteria"](
        "당일용 재공 데이터는 wip_today로 등록해줘."
    )["time_scope"] == "current_day"
    assert namespace["_freeform_selection_criteria"](
        "이력 재공 데이터는 wip으로 등록해줘."
    )["time_scope"] == "history"


def test_explicit_grain_and_recipe_text_use_deterministic_domain_projection() -> None:
    namespace = _authoring_namespace()
    cases = [
        (
            "Register product grain. key is TECH, DEN, MODE.",
            "grains",
            "product",
        ),
        (
            "Register recipe as product.standard. grain is product and key is TECH, DEN, MODE.",
            "recipes",
            "product.standard",
        ),
    ]
    for source_text, section, key in cases:
        output_schema = namespace["_bootstrap_output_schema"](
            "domain",
            hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            approved_semantic_vocabulary=None,
        )
        proposal = namespace["_deterministic_freeform_authoring_proposal"](
            SimpleNamespace(input_message=source_text),
            "metadata_domain_draft",
            output_schema,
        )
        assert proposal is not None
        assert proposal["draft"]["items"][0]["section"] == section
        assert proposal["draft"]["items"][0]["key"] == key


def test_history_dataset_uses_source_projection_even_when_llm_json_is_truncated() -> None:
    namespace = _authoring_namespace()
    source_sha256 = hashlib.sha256(PRODUCTION_HISTORY_TEXT.strip().encode("utf-8")).hexdigest()
    output_schema = namespace["_bootstrap_output_schema"](
        "dataset", source_sha256, approved_semantic_vocabulary=None
    )
    component = SimpleNamespace(input_message=PRODUCTION_HISTORY_TEXT)

    proposal = namespace["_deterministic_freeform_authoring_proposal"](
        component, "metadata_dataset_draft", output_schema
    )

    assert proposal is not None
    assert proposal["draft"]["dataset_cards"] == [
        {
            "dataset_id": "production",
            "display_name": "Production History",
            "family": "production",
            "source_type": "oracle",
            "fields": [],
            "selection_criteria": {
                "time_scope": "history",
                "use_when": ["어제 생산", "전일 생산", "특정 과거일 생산"],
                "exclude_when": ["오늘 생산", "당일 생산", "현재 생산", "현시간 기준 생산"],
            },
            "time_scope": "history",
        }
    ]
    patch = namespace["_expand_freeform_dataset_fragment"](
        proposal["draft"], PRODUCTION_HISTORY_TEXT
    )
    patched, evidence = namespace["apply_dataset_source_configs_from_text"](
        patch, PRODUCTION_HISTORY_TEXT, require_complete=True
    )
    dataset = patched["datasets"]["production"]
    assert dataset["fields"]["DATE"]["physical_column"] == "WORK_DATE"
    assert dataset["fields"]["PRODUCTION"]["semantic_type"] == "number"
    assert dataset["source_config"]["db_key"] == "PNT_RPT"
    assert dataset["source_config"]["query_template"].endswith("AND WORK_DATE = {DATE}")
    assert evidence["query_count"] == 1


def test_process_group_uses_source_projection_without_domain_profile_input() -> None:
    namespace = _authoring_namespace()
    source_sha256 = hashlib.sha256(DP_GROUP_TEXT.strip().encode("utf-8")).hexdigest()
    output_schema = namespace["_bootstrap_output_schema"](
        "domain", source_sha256, approved_semantic_vocabulary=None
    )
    component = SimpleNamespace(input_message=DP_GROUP_TEXT)

    proposal = namespace["_deterministic_freeform_authoring_proposal"](
        component, "metadata_domain_draft", output_schema
    )

    assert proposal is not None
    patch = namespace["_expand_freeform_domain_fragment"](proposal["draft"])
    group = patch["entity_groups"]["DP"]
    assert group["target_field"] == "OPER_NAME"
    assert group["aliases"] == ["DP", "D/P", "DP공정", "D/P공정", "DP 공정", "D/P 공정"]
    assert group["members"][0:4] == ["WET1", "WET2", "L/T1", "L/T2"]
    assert group["members"][-1] == "C/C1"


def test_actual_draft_boundary_ignores_truncated_model_json_when_source_is_complete() -> None:
    namespace = _authoring_namespace()
    source_text = PRODUCTION_HISTORY_TEXT.strip()
    output_schema = namespace["_bootstrap_output_schema"](
        "dataset",
        hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        approved_semantic_vocabulary=None,
    )
    component = SimpleNamespace(
        input_message=source_text,
        authoring_invocation_result={
            "contract_version": "llm.invocation.v1",
            "purpose": "metadata_dataset_draft",
            "status": "ok",
            "llm_calls": 1,
            "response_text": '{"contract_version":"metadata.authoring.proposal.v1","status":"complete"',
        },
    )

    proposal = namespace["_authoring_invocation_draft"](
        component,
        input_name="authoring_invocation_result",
        expected_purpose="metadata_dataset_draft",
        required=True,
        expected_output_schema=output_schema,
    )

    assert proposal["status"] == "complete"
    assert proposal["draft"]["dataset_cards"][0]["dataset_id"] == "production"
    assert component._observed_authoring_source_projection["status"] == "used"


def test_incomplete_worker_text_is_not_force_saved_when_model_json_is_invalid() -> None:
    namespace = _authoring_namespace()
    source_text = "생산 데이터를 등록해줘."
    output_schema = namespace["_bootstrap_output_schema"](
        "dataset",
        hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        approved_semantic_vocabulary=None,
    )
    component = SimpleNamespace(
        input_message=source_text,
        authoring_invocation_result={
            "contract_version": "llm.invocation.v1",
            "purpose": "metadata_dataset_draft",
            "status": "ok",
            "llm_calls": 1,
            "response_text": "{",
        },
    )

    with pytest.raises(namespace["ContractError"]):
        namespace["_authoring_invocation_draft"](
            component,
            input_name="authoring_invocation_result",
            expected_purpose="metadata_dataset_draft",
            required=True,
            expected_output_schema=output_schema,
        )


def test_main_filter_worker_text_projects_each_filter_as_one_item() -> None:
    namespace = _authoring_namespace()
    source_text = (ROOT / "metadata" / "authoring" / "v6_contract_validation_live" / "main_filter_v6.txt").read_text(encoding="utf-8").strip()
    output_schema = namespace["_bootstrap_output_schema"](
        "main_filter",
        hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        approved_semantic_vocabulary=None,
    )

    proposal = namespace["_deterministic_freeform_authoring_proposal"](
        SimpleNamespace(input_message=source_text),
        "metadata_main_filter_draft",
        output_schema,
    )

    assert proposal is not None
    assert [item["filter_key"] for item in proposal["draft"]["items"]] == ["DATE", "OPER_NAME"]
    assert proposal["draft"]["items"][0]["payload"]["aliases"] == ["날짜", "일자", "기준일", "작업일", "DATE"]


def test_v5_style_domain_and_main_filter_items_expand_to_v6_sections() -> None:
    namespace = _authoring_namespace()
    domain = namespace["_expand_freeform_domain_fragment"](
        {
            "items": [
                {
                    "section": "entity_groups",
                    "key": "DP",
                    "payload": {
                        "display_name": "DP",
                        "field": "OPER_NAME",
                        "processes": ["AA", "BB", "CC"],
                        "aliases": ["DP", "D/P", "DP공정"],
                    },
                }
            ]
        }
    )
    assert domain["entity_groups"]["DP"] == {
        "group_id": "DP",
        "display_name": "DP",
        "target_field": "OPER_NAME",
        "members": ["AA", "BB", "CC"],
        "aliases": ["DP", "D/P", "DP공정"],
    }

    compact_filter = namespace["_expand_freeform_main_filter_fragment"](
        {
            "items": [
                {
                    "filter_key": "OPER_NAME",
                    "payload": {
                        "display_name": "공정명",
                        "aliases": ["공정", "공정명", "OPER_NAME"],
                    },
                }
            ]
        }
    )
    expanded_filter = namespace["_expand_compact_main_filter_fragment"](
        compact_filter,
        approved_semantic_vocabulary=None,
        allow_unresolved=True,
    )
    assert set(expanded_filter) == {"aliases"}
    assert expanded_filter["aliases"]["field:OPER_NAME"]["target_key"] == "OPER_NAME"


def test_freeform_prompt_schemas_use_small_item_contracts() -> None:
    namespace = _authoring_namespace()
    source_sha256 = "a" * 64
    expected = {
        "domain": "items",
        "dataset": "dataset_cards",
        "main_filter": "items",
    }
    for kind, root_key in expected.items():
        proposal = namespace["_bootstrap_output_schema"](
            kind,
            source_sha256,
            approved_semantic_vocabulary=None,
        )
        complete = next(
            branch
            for branch in proposal["oneOf"]
            if branch["properties"]["status"]["const"] == "complete"
        )
        assert set(complete["properties"]["draft"]["properties"]) == {root_key}
