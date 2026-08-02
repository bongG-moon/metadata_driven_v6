# Intent, Plan, Execution Contract

## 1. Request capsule과 typed literal

LLM 호출 전에 deterministic Request Capsule Builder가 질문의 literal 후보를 만든다. 후보는 반드시 원문 span과 typed value를 함께 가지며, 임의 값 생성은 허용하지 않는다.

```json
{
  "contract_version": "request.capsule.v1",
  "question": "6/27일 W/B공정에서 세부 공정별 생산실적과 아침재공 수량 알려줘",
  "owner_subject_id": "user-or-service:...",
  "session_id": "session:...",
  "reference_instant": "2026-07-30T09:00:00+09:00",
  "timezone": "Asia/Seoul",
  "literal_candidates": [
    {
      "id": "literal:date:0",
      "kind": "LocalDate",
      "source_span": "6/27",
      "value": "2026-06-27",
      "resolver_version": "literal-resolver.v1"
    }
  ]
}
```

`reference_instant`와 `timezone`은 내부 request contract 필드이지 Langflow UI 입력이 아니다. `02 요청 및 세션 상태 고정`은 실행 시 현재 시각을 만들고 시간대를 항상 `Asia/Seoul`로 고정한다. 위 고정 시각은 재현 가능한 검증 fixture에서만 사용한다.

Candidate Selector는 request capsule과 exact metadata/operator registry revision을 결합해 다음 immutable compiler용 bundle을 만든다.

```json
{
  "contract_version": "resolved.candidate.bundle.v1",
  "bundle_sha256": "...",
  "request_evidence_sha256": "...",
  "metadata_bundle_sha256": "...",
  "operator_registry": {
    "version": "operator_registry.v1",
    "sha256": "..."
  },
  "candidates": [
    {
      "candidate_id": "filter_application:process_group.WB",
      "kind": "filter_application",
      "matched_span": "W/B",
      "match_rule": "alias_boundary_longest",
      "applicable_metric_ids": ["PRODUCTION_QTY", "WIP_BOH_QTY"],
      "resolved_semantics": {
        "type": "predicate",
        "metadata_ref": {
          "kind": "process_group",
          "key": "WB",
          "revision": 3,
          "contract_sha256": "..."
        },
        "predicate": {
          "field": "OPER_NAME",
          "operator_id": "in.v1",
          "typed_values": ["W/B1", "W/B2", "W/B3", "W/B4", "W/B5", "W/B6"]
        }
      },
      "semantics_sha256": "..."
    },
    {
      "candidate_id": "literal:date:0",
      "kind": "LocalDate",
      "matched_span": "6/27",
      "applicable_metric_ids": ["PRODUCTION_QTY", "WIP_BOH_QTY"],
      "resolved_semantics": {
        "value": "2026-06-27",
        "resolver_version": "literal-resolver.v1"
      },
      "semantics_sha256": "..."
    }
  ]
}
```

소유권은 다음과 같다.

- Request Capsule Builder: explicit/relative date, timestamp, 정수·소수, quoted value, metadata가 허용한 product token의 원문 span을 typed candidate로 만든다.
- Candidate Selector: metadata alias index로 process group, product group, metric, role-specific field, recipe, formula, operation-application과 registry-attested registered-function application candidate ID를 만들고 immutable `resolved.candidate.bundle.v1`에 resolved semantics를 넣는다. Filter는 metadata가 이미 field/operator/value semantics를 고정한 `filter_application` candidate로 만든다.
- Route Eligibility Gate: request/state evidence와 exact resolved bundle만으로 semantic slot의 유일성·완전성·registry support를 증명해 `analysis.route.v1`을 만든다. source row, model score, 질문별 문자열 branch는 사용하지 않는다.
- Deterministic Intent Builder: `deterministic` proof가 pin한 selection만 공통 `analysis.intent.v1`으로 정규화한다.
- Plan Compiler: normalized intent와 **같은 resolved candidate bundle**을 받아 ordered process range의 endpoint를 확장하고, typed literal을 source parameter format으로 변환한다.
- Intent LLM: `intent_llm` route에서만 이미 생성된 candidate ID와 target slot을 선택한다.

`filter_application`은 자유 형식 filter가 아니다. Candidate Selector가 승인된 metadata record와 operator registry를 사용해 `metadata_ref`, operator ID, typed value/literal candidate, 적용 가능 metric을 결정하고 그 의미의 hash를 `semantics_sha256`에 고정한다. 예를 들어 process group은 metadata에 저장된 closed member predicate 전체를 하나의 application candidate로 만든다. “수율 80 이상” 같은 동적 값은 field alias, allowlisted `gte.v1` operator alias, typed number candidate가 모두 결정적으로 매칭될 때만 `filter_application:YIELD_RATE:gte.v1:literal:number:0` 같은 candidate를 만들며, 그 bundle의 `resolved_semantics`에 canonical field/operator ID/typed value를 넣는다. Intent LLM은 application ID만 선택하며 field, operator 문자열, value를 출력하지 않는다.

유연 조회도 같은 원칙을 사용한다.

- `field_application:<dataset-family>:<field>:<role>`은 질문에서 매칭된 canonical field와 metadata가 허용한 `project|group|sort|rank|compare|join|output` role 하나를 pin한다.
- `operation_application:*`은 operator alias span, role-compatible field application, typed N/value candidate, scope(global/per-group), direction, tie policy를 하나의 resolved semantics로 묶는다.
- `recipe_application:*`은 등록된 join/presence/row-match recipe와 input slot을 pin한다.
- `formula_application:*`은 등록된 `formula.v1` ID와 입력 metric slot을 pin한다.
- `registered_function_application:<function_id>:v<version>:*`은 active Domain Package function card, build-time registry entry, implementation/input/output schema hash, required field/role, typed argument binding과 resource policy를 하나의 resolved semantics로 pin한다. Registry attestation이 없으면 candidate를 만들지 않는다.

예를 들어 “MODE별 OUT 계획 상위 3개”는 `MODE:group`, `OUT_PLAN_QTY:rank`, typed integer `3`, `rank.top.per_group.exact_n`을 결합한 application candidate가 있을 때만 실행된다. “A가 B보다 큰 행”도 두 `compare` role field와 `gt`를 묶은 application candidate를 선택한다. Candidate Selector는 질문 evidence와 dependency closure에 관련된 application만 만들고 전체 catalog의 조합을 폭발시키지 않는다. LLM은 application 내부 field/operator/N/join key/formula를 편집하지 못한다.

`request_evidence_sha256`는 question, reference instant/timezone, typed candidate와 resolver version, validated follow-up reference projection을 canonicalize한 hash다. authenticated subject/session은 access-control envelope에 남고 이 semantic hash에서는 제외한다. 각 `semantics_sha256`는 `candidate_id`, kind, origin evidence, applicable metric IDs, resolved semantics, metadata/operator pin을 canonicalize하되 hash 필드 자체와 prompt용 label을 제외해 계산한다. `bundle_sha256`는 그 필드 자체를 제외한 bundle 전체의 schema-aware canonical SHA-256이다.

LLM에는 full `resolved_semantics`가 아니라 `candidate_id`, matched span, 짧은 display label, applicable metric ID만 가진 bounded prompt-card projection을 보낸다. Full bundle은 LLM edge를 통과하지 않고 compiler에 직접 전달하며, inline budget을 넘으면 content-addressed immutable ref와 `bundle_sha256`로 전달한다.

Date resolver v1은 내부 `reference_instant`를 고정 시간대 `Asia/Seoul`의 local date로 바꾼다. `오늘/어제`는 그 local date의 0/-1일, 연도 없는 `6/27`·`7월 1일`은 reference local year, offset이 있는 timestamp는 해당 Instant를 Asia/Seoul로 변환한 local date다. “가장 가까운 날짜” 같은 실행 시점 heuristic을 쓰지 않으며 연도 해석 정책이 맞지 않는 도메인은 clarification을 요구한다.

`L-267`, `D/S1~D/A4`, `오늘`, `어제`, `6/27`, `2026-07-01T00:00:00+09:00`은 이 경계를 통과하는 필수 contract fixture다. 원문에 없는 literal, 허용 pattern을 통과하지 못한 literal, metadata ID로 연결되지 않은 alias는 intent에 들어갈 수 없다.

## 2. Route decision

Route Eligibility Gate는 closed `analysis.route.v1`을 출력한다.

```json
{
  "contract_version": "analysis.route.v1",
  "route": "deterministic",
  "reason_code": "unique_complete_selection",
  "resolved_candidate_bundle_sha256": "...",
  "selected_candidate_ids": ["metric:PRODUCTION_QTY", "filter_application:process_group.DA"],
  "required_slots": ["metric", "process", "time", "operation"],
  "unresolved_slots": [],
  "ambiguity_sets": [],
  "route_policy_version": "route-policy.v1",
  "eligibility_proof_sha256": "..."
}
```

Route는 `deterministic|intent_llm|unsupported`만 허용한다.

- `deterministic`: required slot이 모두 채워지고 각 slot의 applicable selection이 정확히 하나이며 conflict/ambiguity/registry gap이 없음
- `intent_llm`: bounded candidate 안의 semantic 선택이 필요함. source 조회 전 Intent LLM 최대 1회, syntax/schema/candidate/provider 오류 뒤 retry 0회
- `unsupported`: typed registry 밖 의미가 확정적임. 모든 LLM/retrieval/executor/result-store/state-mutation 0, 이전 state 유지

`eligibility_proof_sha256`는 proof hash 필드 자체를 제외한 route object와 request evidence/bundle/policy pin을 schema-aware canonicalize해 계산한다. model/provider profile은 hash material이 아니다. 같은 request/bundle/state에서 model 설정에 따라 route가 바뀌면 contract violation이다.

Fast path를 선택한 뒤 intent/plan/retrieval/execution 오류가 발생해도 `intent_llm`, pandas code, repair 또는 exploration으로 자동 fallback하지 않는다. `fallback_allowed=false`는 모든 canonical validation case의 invariant다.

## 3. Semantic intent

Deterministic Intent Builder와 Intent Decoder는 모두 실행 계획이 아니라 질문 의미의 selection body를 같은 closed schema로 정규화한다. Deterministic builder는 route proof가 pin한 selection을 사용하고, Intent Decoder는 provider가 반환한 closed selection schema를 검증한다. Common Intent Validator가 trusted input의 resolved bundle/route proof hash와 generator를 부착한다. LLM이 이 trust field를 생성하거나 덮어쓸 수 없다.

```json
{
  "contract_version": "analysis.intent.v1",
  "resolved_candidate_bundle_sha256": "...",
  "route": "deterministic",
  "route_reason": "unique_complete_selection",
  "eligibility_proof_sha256": "...",
  "intent_generator": "deterministic",
  "request_scope": "new_analysis",
  "analysis_kind": "aggregate_compare",
  "metric_refs": [
    {"candidate_id": "metric:PRODUCTION_QTY", "target_slots": ["production"]},
    {"candidate_id": "metric:WIP_BOH_QTY", "target_slots": ["wip"]}
  ],
  "dimension_refs": [
    {
      "candidate_id": "field_application:production:OPER_NAME:group",
      "target_slots": ["production", "wip"]
    }
  ],
  "filter_refs": [
    {
      "candidate_id": "filter_application:process_group.WB",
      "target_slots": ["production", "wip"]
    }
  ],
  "time_refs": [
    {
      "candidate_id": "literal:date:0",
      "target_slots": ["production", "wip"]
    }
  ],
  "operation_refs": [
    {
      "candidate_id": "operation_application:aggregate_by_process:0",
      "target_slots": ["production", "wip"]
    }
  ],
  "recipe_refs": [
    {
      "candidate_id": "recipe_application:metric_merge.production_wip:0",
      "target_slots": ["production", "wip"]
    }
  ],
  "formula_refs": [],
  "followup": {
    "reference": "none",
    "inherit": [],
    "replace": [],
    "drop": []
  },
  "unresolved": []
}
```

### Intent에서 금지되는 필드

- `dataset_key`
- `source_alias`
- `source_type`
- SQL/URL/config
- physical column
- raw literal value
- free-form filter field/operator/value 또는 request capsule에 없는 filter application
- provider가 출력한 `resolved_candidate_bundle_sha256` 또는 다른 reserved trust field
- provider가 출력한 `route`, `route_reason`, `eligibility_proof_sha256`, `intent_generator`
- `resolved_date` 또는 source query date
- pandas code
- arbitrary output column
- runtime helper source
- free-form function ID/version/argument 또는 registry 밖 function reference

Provider selection schema와 normalized intent schema는 JSON Schema Draft 2020-12 closed object다. root와 `metric_refs[]`, `dimension_refs[]`, `filter_refs[]`, `time_refs[]`, `operation_refs[]`, `recipe_refs[]`, `formula_refs[]`, `followup` 등 모든 고정 object에 `additionalProperties: false`를 적용하고, 확장 가능한 map이 필요하면 명시적 `patternProperties`와 value schema를 사용한다. 모든 `*_refs[]` item이 허용하는 key는 `candidate_id`, `target_slots`뿐이다.

Common Intent Validator는 생성 경로와 무관하게 모든 `candidate_id`가 같은 resolved candidate bundle에 존재하는지, bundle/candidate/route proof hash와 metadata/operator pin이 유효한지, `target_slots`가 선택 metric과 candidate의 applicable metric 교집합인지 검사한다. Plan Compiler만 application candidate의 `resolved_semantics`를 canonical field/operator/value predicate로 확장한다. 따라서 아래 plan의 `operator`는 LLM 출력이 아니라 pinned operator registry와 metadata에서 결정적으로 생성된 값이다.

Intent ID는 제공된 metadata bundle의 ID만 사용할 수 있다.

## 4. Plan compiler

Compiler는 validated common intent, intent가 pin한 exact `resolved.candidate.bundle.v1`, exact route proof와 metadata revisions를 받아 immutable plan을 만든다. Intent의 bundle/proof hash와 compiler input이 다르면 `intent_contract_error` 또는 `route_contract_error`로 retrieval 전에 종료한다. Route는 plan 의미를 바꾸지 않으므로 동일 semantic selection의 deterministic/LLM 경로는 같은 plan fingerprint를 만든다.

```json
{
  "contract_version": "analysis.plan.v1",
  "plan_id": "plan:sha256",
  "resolved_candidate_bundle_sha256": "...",
  "metadata_bundle_sha256": "...",
  "plan_schema_sha256": "...",
  "operator_registry": {"version": "operator_registry.v1", "sha256": "..."},
  "executed_result_contract_sha256": null,
  "retrieval_jobs": [
    {
      "job_id": "production",
      "requirement": "required",
      "dataset_key": "production",
      "dataset_revision": 4,
      "source_alias": "src_1",
      "parameters": {
        "DATE": {
          "value": "20260627",
          "origin_candidate_id": "literal:date:0",
          "parameter_contract": "production.DATE.v1"
        }
      },
      "filters": [
        {"field": "OPER_NAME", "operator": "in", "values": ["W/B1", "W/B2", "W/B3", "W/B4", "W/B5", "W/B6"]}
      ],
      "required_fields": ["OPER_NAME", "PRODUCTION_QTY"]
    },
    {
      "job_id": "wip_boh",
      "requirement": "required",
      "dataset_key": "wip",
      "dataset_revision": 3,
      "source_alias": "src_2",
      "parameters": {
        "DATE": {
          "value": "20260626",
          "origin_candidate_id": "literal:date:0",
          "parameter_contract": "wip.DATE.v1"
        }
      },
      "filters": [
        {"field": "OPER_NAME", "operator": "in", "values": ["W/B1", "W/B2", "W/B3", "W/B4", "W/B5", "W/B6"]}
      ],
      "required_fields": ["OPER_NAME", "WIP_BOH_QTY"]
    }
  ],
  "parameter_binding_specs": [],
  "operations": [
    {
      "id": "op1",
      "op": "aggregate",
      "input": "src_1",
      "group_by": ["OPER_NAME"],
      "metrics": [{"field": "PRODUCTION_QTY", "rollup": "sum", "output": "PRODUCTION_QTY"}]
    },
    {
      "id": "op2",
      "op": "aggregate",
      "input": "src_2",
      "group_by": ["OPER_NAME"],
      "metrics": [{"field": "WIP_BOH_QTY", "rollup": "sum", "output": "WIP_BOH_QTY"}]
    },
    {
      "id": "op3",
      "op": "join",
      "left": "op1",
      "right": "op2",
      "recipe_ref": {
        "recipe_id": "join.operation.production_wip",
        "revision": 2,
        "contract_sha256": "..."
      },
      "join_type": "outer",
      "key_mappings": [
        {"left_field": "OPER_NAME", "right_field": "OPER_NAME"}
      ],
      "cardinality": "one_to_one_after_aggregate",
      "null_key_policy": "never_match",
      "duplicate_policy": {
        "left": "error_after_declared_aggregate",
        "right": "error_after_declared_aggregate"
      },
      "multi_match_policy": "error",
      "empty_side_policy": "preserve_other_side_with_declared_null_metrics",
      "suffix_policy": "forbid",
      "output_fields": ["OPER_NAME", "PRODUCTION_QTY", "WIP_BOH_QTY"]
    }
  ],
  "result_contract": {
    "grain": ["OPER_NAME"],
    "columns": ["OPER_NAME", "PRODUCTION_QTY", "WIP_BOH_QTY"],
    "ordering": [{"field": "OPER_NAME", "direction": "asc"}]
  },
  "lineage": {
    "PRODUCTION_QTY": {
      "semantic_metric_id": "PRODUCTION_QTY",
      "job_id": "production",
      "dataset": {"key": "production", "revision": 4},
      "canonical_field": "PRODUCTION_QTY",
      "physical_source_field": "PRODUCTION",
      "time_scope": {"requested_date": "2026-06-27", "query_date": "2026-06-27"},
      "filter_scope": [{"field": "OPER_NAME", "operator": "in", "values": ["W/B1", "W/B2", "W/B3", "W/B4", "W/B5", "W/B6"]}],
      "aggregation": {"name": "sum", "version": 1},
      "output_grain": ["OPER_NAME"],
      "signature_sha256": "..."
    },
    "WIP_BOH_QTY": {
      "semantic_metric_id": "WIP_BOH_QTY",
      "job_id": "wip_boh",
      "dataset": {"key": "wip", "revision": 3},
      "canonical_field": "WIP_BOH_QTY",
      "physical_source_field": "WIP",
      "time_scope": {"requested_date": "2026-06-27", "query_date": "2026-06-26", "business_timepoint": "BOH"},
      "filter_scope": [{"field": "OPER_NAME", "operator": "in", "values": ["W/B1", "W/B2", "W/B3", "W/B4", "W/B5", "W/B6"]}],
      "aggregation": {"name": "sum", "version": 1},
      "output_grain": ["OPER_NAME"],
      "signature_sha256": "..."
    }
  },
  "dimension_provenance": {
    "OPER_NAME": {
      "canonical_field": "OPER_NAME",
      "source_jobs": ["production", "wip_boh"],
      "grain_role": "group_key",
      "dataset_binding_hashes": ["...", "..."]
    }
  }
}
```

`plan_id`는 `plan_id` 필드를 제외한 위 semantic plan object의 canonical JSON SHA-256이다. hash material에는 resolved candidate bundle hash, plan schema hash, operator registry version/hash, metadata bundle hash, follow-up이면 `executed_result_contract_sha256`, declarative binding spec이 반드시 포함된다. Route, intent generator, eligibility proof와 provider/model 정보는 trace/provenance에는 남지만 semantic plan object와 `plan_id`에는 넣지 않는다. 따라서 동일 selection의 deterministic/LLM equivalence case는 같은 `plan_id`를 가져야 한다.

Canonical serializer는 key ordering, number representation, Unicode normalization과 schema별 array policy를 고정한다.

- semantic set: dependency refs, `required_fields`, `in/not_in` values는 schema comparator로 dedupe/sort
- 실행 순서: operation DAG의 canonical topological order와 deterministic operation ID
- 표시/의미 순서: result columns, ordering keys, tie-breakers는 선언 순서를 보존
- retrieval jobs: deterministic `job_id` 순서

같은 의미인데 LLM 출력 배열 순서만 다른 경우 같은 plan fingerprint가 나와야 한다. 반대로 registry, metadata, state contract, ordered output 의미가 바뀌면 다른 fingerprint여야 한다.

Plan의 filter, required field, operation, result contract에는 canonical field만 사용한다. `physical_source_field`는 audit lineage와 source adapter binding에만 나타날 수 있다.

### Entity/required-parameter binding

이전 결과의 entity를 새 source의 required parameter로 전달하는 작업은 executor operation이 아니다. 책임을 두 단계로 나눈다.

- Plan Compiler: `executed.result.v1`의 contract hash와 metadata transfer contract를 사용해 **declarative binding spec**만 plan에 넣는다. 값을 읽거나 선택하지 않는다.
- Parameter Binder: Plan Validator 통과 후 authenticated owner/session ref를 로드해 실제 값을 resolve, type-check, stable sort/dedupe/chunk하고 immutable `retrieval.job_bundle.v1`을 만든다.

```json
{
  "binding_spec_id": "binding:lot:current-hold",
  "source_result_ref": "result:...",
  "source_result_contract_sha256": "...",
  "source_entity": "lot",
  "source_field": "LOT_ID",
  "selection": {"op": "all_entities", "stable_order": "asc", "dedupe": true},
  "target_job_id": "hold_history",
  "target_parameter": "LOT_ID",
  "operator": "in",
  "chunk_size": 200,
  "max_total_values": 2000
}
```

Parameter Binder 출력:

```json
{
  "contract_version": "retrieval.job_bundle.v1",
  "job_bundle_id": "jobbundle:sha256",
  "plan_id": "plan:sha256",
  "binding_resolutions": [
    {
      "binding_spec_id": "binding:lot:current-hold",
      "owner_subject_id": "user-or-service:...",
      "session_id": "session:...",
      "values_sha256": "...",
      "value_count": 37,
      "chunk_count": 1
    }
  ],
  "jobs": [
    {
      "job_id": "hold_history:000",
      "dataset_key": "hold_history",
      "parameters": {
        "LOT_ID": {
          "values_ref": "bindingvalues:sha256",
          "values_sha256": "...",
          "value_count": 37
        }
      }
    }
  ]
}
```

`job_bundle_id`는 자신을 제외한 canonical job bundle에 실제 bound-value content hash와 chunk별 typed parameter를 포함해 계산한다. `values_ref`는 owner/session-bound content-addressed TTL ref이며 resolver가 hash와 count를 다시 확인한다. owner/session, result contract hash, entity/grain, stable selection, 최대 개수, expiry를 모두 검증한 뒤 route한다. required parameter가 없거나 일부만 resolve되면 retrieval을 시작하지 않는다.

최종 execution evidence는 `execution_id = SHA256(plan_id + job_bundle_id + ordered source snapshot content hashes)`를 기록한다. 따라서 plan 의미와 실제 bound values/source bytes가 모두 추적되지만 Plan Validator 이후 plan 자체를 변형하지 않는다.

## 5. 지원 operation registry

v6 MVP는 대표 질문 corpus에 필요한 아래 operation을 결정론적으로 구현한다.

| Operation | 용도 |
| --- | --- |
| `filter` | eq/in/ne/not_in/gt/gte/lt/lte/between/contains/starts_with/ends_with/null/blank와 bounded all/any tree |
| `ordered_range` | `OPER_SEQ` 숫자 기준 inclusive 공정 구간 |
| `project` | 등록 field의 exact 선택·순서 지정, label은 별도 |
| `derive` | registry의 closed typed formula AST |
| `aggregate` | sum/mean/min/max/count/nunique/median/std/var/list_unique |
| `compare_fields` | 같은 row의 등록 field 두 개를 typed eq/ne/gt/gte/lt/lte로 비교 |
| `compare_group_attributes` | 사용자가 지정한 동일 key별 비교 field any/all 차이 탐지 |
| `find_duplicate_groups` | 등록 field 조합이 N회 이상 반복된 그룹·행 탐지 |
| `join` | key/cardinality/null/multi-match가 검증된 inner/left/right/outer/semi/anti |
| `presence_filter` | left positive + right missing/zero anti-join |
| `sort` | multi-key typed stable ordering과 명시적 null placement |
| `rank` | global/per-group top·bottom N과 max/min 행 선택 |
| `concat_segments` | 상위/하위 등 독립 결과 구간을 label/rank와 함께 결합 |
| `detail` | 등록 field의 원본/detail/entity/history projection |
| `dedupe` | declared identity/field set 기준 stable distinct |
| `row_match_groups` | 이전 결과 각 행 내부 AND, 행 사이 OR로 새 source 제한 |
| `enrich_previous_result` | previous left-row preserve + declared right count/list/metric enrich |
| `transform_previous_result` | 이전 result만 filter/project/sort/rank/aggregate |
| `explain_previous` | 저장 trace/lineage/criteria/facts 설명, 신규 조회·계산 없음 |
| `registered_call` | hash-pinned standalone registry의 검토된 비표준 알고리즘 호출 |

각 operation은 input/output grain, allowed metric type, null policy, deterministic ordering을 명시한다.

Operation은 고정 질문 recipe가 아니라 closed schema의 composable DAG primitive다. 사용자가 등록된 컬럼을 직접 말하면 field candidate가 `project|filter|group|compare|sort|rank` role 중 허용된 역할로 plan에 들어간다. 따라서 새 컬럼 조합 질문마다 Python이나 새 executor branch를 만들지 않는다. 다만 미등록 field/role, 미등록 join/formula, registry에 없는 계산은 자유 code로 우회하지 않는다.

### 5.1 Filter tree

- canonical operator: `eq|in|ne|not_in|gt|gte|lt|lte|between|contains|starts_with|ends_with|is_null|is_not_null|is_blank|is_not_blank|null_or_blank`
- migration alias: `ge→gte`, `le→lte`, `like→contains`, field-level `or|any→any` group
- 한 leaf는 registered field ID, operator ID, typed value candidate만 가진다.
- `all`은 AND, `any`는 OR이며 최대 depth 3, leaf 32개다. 자유 expression/string eval은 없다.
- string case, date/timezone, numeric coercion, null/blank 의미는 field contract가 결정한다.

### 5.2 Projection, rank와 극값

`project`는 사용자가 요청한 registered output field의 exact ordered list를 만든다. filter에 사용했다는 이유만으로 field를 표에 추가하지 않고, 표시명은 `display_labels`로 분리한다.

```json
{
  "id": "op_rank",
  "op": "rank",
  "input": "op_aggregate",
  "mode": "top",
  "partition_by": [],
  "rank_by": [
    {"field": "PRODUCTION_QTY", "direction": "desc", "nulls": "last"}
  ],
  "tie_break_by": [
    {"field": "DEVICE", "direction": "asc", "nulls": "last"}
  ],
  "limit": 3,
  "tie_policy": "exact_n",
  "emit_rank_field": "RESULT_RANK"
}
```

- “최댓값/최솟값” 자체는 `aggregate(max|min)` scalar다.
- “값이 가장 큰/작은 행”은 `rank(limit=1, tie_policy=include_all)`이다.
- “한 개/1개만”은 `tie_policy=exact_n`이며 metadata identity/tie-break field로 정확히 1행을 고른다. 유효 tie-break가 없으면 clarification이다.
- “상위/하위 N”은 기본 `exact_n`; “공동 순위 포함”을 명시하면 `include_all`이다.
- numeric metric의 `top`은 `rank_by.direction=desc`, `bottom`은 `asc`다. non-numeric ordered domain은 metadata의 reviewed order를 사용하며 order가 없으면 clarification이다.
- `mode`와 `rank_by.direction`은 독립 값이 아니다. Compiler가 semantic ordering에서 함께 생성하고 validator가 top/bottom 방향 일치를 검사한다. null은 별도 요청이 없으면 두 mode 모두 `last`이며 extreme으로 취급하지 않는다.
- `RESULT_RANK=1`은 top에서 가장 큰/우선인 tuple, bottom에서 가장 작은/후순위인 tuple이다.
- `rank_by`는 사용자 의미의 순위 key이고 `tie_break_by`는 exact-N 재현성만 위한 key다. `include_all`의 경계 동점은 `rank_by`만 비교한다.
- “A 내림차순, 같으면 B 내림차순”처럼 우선순위를 명시한 다중 컬럼 rank는 ordered `rank_by`로 표현한다.
- “A와 B 각 컬럼에서 가장 큰 행”은 두 argmax segment를 독립 실행하고 `RESULT_METRIC`, `RESULT_RANK`를 붙인다. “A와 B를 합친 최대”처럼 결합 공식이 불명확하면 합계를 임의 생성하지 않고 clarification이다.
- “제품별 상위 N”처럼 그룹별이면 `partition_by`가 필수다. global/per-group을 추측해 바꾸지 않는다.
- 상위와 하위를 함께 요청하면 각각 독립 rank를 실행한 뒤 `concat_segments`가 `RESULT_GROUP`, `RESULT_RANK`를 붙여 사용자 요청 순서로 결합한다.

### 5.3 Join, 비교, 파생 지표

`join`은 metadata join recipe와 plan의 canonical key mappings, join type, expected cardinality, null-key policy, duplicate/multi-match policy, empty-side policy, exact output fields를 모두 pin한다. `_x/_y` suffix나 undeclared many-to-many가 생기면 `join_cardinality_violation`이다.

세 개 이상 source의 join은 한 번에 암묵적으로 merge하지 않고 operation DAG에서 검증된 binary join을 순서대로 연결한다. 각 중간 결과는 exact grain/schema/cardinality를 가지며 다음 recipe의 declared input contract와 일치해야 한다.

`compare_fields`는 같은 input row의 `left_field`, `right_field`, `operator=eq|ne|gt|gte|lt|lte`, null policy를 pin한다. 두 field 모두 `compare` role이어야 하고 semantic type/unit이 호환돼야 한다. null 비교 결과는 metadata의 `false|true|error|three_valued` 정책을 따르며 pandas implicit coercion을 사용하지 않는다.

`compare_group_attributes`는 `group_by`와 `comparison_fields`를 분리하며 `comparison_rule=any|all`을 사용한다. `find_duplicate_groups`는 exact group fields와 `minimum_count`를 사용한다. 둘 다 dataset field role이 `compare`인 registered column만 허용하므로 제품 전용 비교에 한정되지 않는다.

`derive`는 metadata의 `formula.v1` AST, operand metric lineage, evaluation stage, unit/type, null/zero-division, rounding을 plan에 pin한다. 비율·차이 표현이 없고 recipe도 없으면 “대비”만으로 파생 metric을 만들지 않는다.

ordered temporal field가 `aggregate` role과 `min|max` rollup을 선언하면 groupwise temporal extrema를 실행할 수 있다. output은 같은 temporal type/timezone을 유지하고 source field, group, rollup lineage를 기록한다. HOLD의 `CURRENT_HOLD_STARTED_AT`은 이 경로이며 arithmetic formula나 임의 datetime code를 사용하지 않는다.

상세/이력은 별도 자유 code가 아니라 `detail → filter → stable sort → optional rank/project` 조합이다. history source는 requested entity 전체 coverage, timestamp coercion/timezone, ascending/descending, earliest/latest와 tie-break를 선언해야 한다.

### 5.4 `registered_call`

`registered_call`은 built-in typed primitive와 metadata formula/recipe로 표현할 수 없는 검토된 알고리즘에만 사용한다. 특정 제품/공정 이름을 공통 executor branch에 하드코딩하는 수단이 아니다.

```json
{
  "id": "op_registered_1",
  "op": "registered_call",
  "input": "source:product_master",
  "function_ref": {
    "function_id": "product.match_tokens",
    "version": 1,
    "implementation_sha256": "<64 lowercase hex>",
    "registry_entry_sha256": "<64 lowercase hex>",
    "input_schema_sha256": "<64 lowercase hex>",
    "output_schema_sha256": "<64 lowercase hex>"
  },
  "argument_bindings": {
    "token_group": {"candidate_ref": "literal:product-token-group:0"}
  },
  "required_fields": ["TECH", "DEN", "MODE"],
  "output_contract": {
    "kind": "table",
    "fields": ["TECH", "DEN", "MODE"],
    "grain_policy": "preserve_input"
  },
  "resource_policy": {
    "timeout_ms": 3000,
    "max_rows": 50000,
    "max_memory_mb": 256,
    "network": "deny",
    "filesystem": "deny",
    "subprocess": "deny"
  }
}
```

Plan Compiler는 `operation_refs`로 선택된 `registered_function_application`의 resolved semantics에서 위 operation을 결정적으로 만든다. LLM selection schema에는 `function_ref`, `argument_bindings`, `required_fields`, output/resource policy가 없고 candidate ID와 target slot만 있다.

Plan Validator는 실행 전에 다음을 모두 검증한다.

- active Domain Package function card와 build manifest registry의 `(function_id, version)`이 정확히 일치
- implementation, registry-entry와 input/output schema SHA-256이 모두 일치
- argument value가 request/state의 typed candidate 또는 reviewed metadata ref에서만 유래하고 input schema를 만족
- source canonical schema가 required field/role을 만족
- output field/grain/lineage와 resource policy가 function card보다 넓지 않음
- DAG의 전후 operation schema/grain이 function input/output과 닫혀 있음

Typed Executor는 build-time allowlist dispatcher만 사용한다. Metadata/Flow input에서 code/module/callable을 읽거나 dynamic import, `eval`/`exec`를 수행하지 않는다. Gateway는 timeout, peak memory, row limit, return type/schema/grain을 검사하며 trace에 row나 argument 원문 대신 function/ref hash와 input/output contract hash만 남긴다. Timeout은 `registered_function_timeout`, 반환 계약 위반은 `registered_function_contract_violation`이다. 어느 실패도 일반 filter, 다른 function, LLM 또는 pandas code로 fallback하지 않는다.

## 6. Column normalization

1. Retriever는 physical schema를 반환한다.
2. **Source Contract Merger**가 dataset field binding을 사용해 canonical column으로 정확히 한 번 rename한다.
3. duplicate physical candidates, missing required field, dtype/coercion 오류를 검사한다.
4. Executor, result contract, follow-up state는 canonical column만 사용한다.
5. 사용자 표시명은 `display_labels` mapping으로만 처리한다.

`MODE`와 `Mode`를 실행 중 여러 node가 번갈아 바꾸는 구조를 금지한다.

## 7. Metric lineage

결과 metric signature는 최소 다음을 포함한다.

```text
semantic_metric_id
+ source job/dataset revision
+ source field
+ time scope/query date
+ filter scope
+ aggregation/formula version
+ output grain
```

signature가 같은 output 두 개는 semantic duplicate다. signature가 다르면 값이 같아도 별도 metric일 수 있다. 이름이나 값만으로 dedupe하지 않는다.

모든 output metric은 result 생성 전 lineage proof를 가져야 한다. `WIP_BOH_QTY = PRODUCTION_QTY`처럼 다른 binding에서 직접 복사하는 operation은 formula metadata가 없으면 거부한다.

## 8. Presence contract

`A는 있으나 B는 없는` 분석은 아래 순서가 고정이다.

1. left와 right를 동일 canonical grain으로 각각 집계
2. `left_metric > 0`만 유지
3. `right_metric > 0` key set 생성
4. left key에서 right positive key를 anti-join
5. result의 right metric은 표시 정책에 따라 0으로 materialize
6. exact result columns로 project

단순 left join 후 전체 행을 반환하면 contract violation이다.

## 9. Follow-up contract

저장되는 `executed_result_contract`:

```json
{
  "contract_version": "executed.result.v1",
  "executed_result_contract_sha256": "...",
  "result_ref": "result:...",
  "result_content_sha256": "...",
  "source_snapshots": [
    {
      "source_ref": "source:...",
      "job_id": "production",
      "dataset": {"key": "production", "revision": 4},
      "query_parameters_sha256": "...",
      "filters_sha256": "...",
      "canonical_schema_sha256": "...",
      "content_sha256": "...",
      "coverage": {
        "row_set_complete": true,
        "truncated": false,
        "source_row_count": 120,
        "stored_row_count": 120,
        "chunk_count": 1,
        "time_scope": {"from": "2026-07-29", "to": "2026-07-29"},
        "filter_scope": [
          {"field": "OPER_NAME", "operator": "in", "values": ["W/B1", "W/B2", "W/B3", "W/B4", "W/B5", "W/B6"]}
        ]
      },
      "retrieved_at": "...",
      "expires_at": "..."
    }
  ],
  "plan_id": "plan:...",
  "retrieval_job_bundle_id": "jobbundle:...",
  "execution_id": "execution:...",
  "metadata_bundle_sha256": "...",
  "entity_id": "product",
  "grain_id": "product.standard",
  "columns": ["TECH", "DEN", "MODE", "PRODUCTION_QTY"],
  "lineage": {},
  "filters": {},
  "time_scope": {},
  "explanation_evidence": {
    "criteria_sha256": "...",
    "lineage_sha256": "...",
    "answer_facts_ref": "facts:...",
    "answer_facts_sha256": "...",
    "operator_trace": [
      {
        "operation_id": "op1",
        "operator_id": "aggregate.v1",
        "input_contract_sha256": "...",
        "output_contract_sha256": "..."
      }
    ],
    "verbose_trace_ref": "traceblob:..."
  },
  "row_count": 3,
  "expires_at": "..."
}
```

`executed_result_contract_sha256`는 그 hash 필드 자체와 storage-only timestamps를 제외한 executed contract의 schema-aware canonical SHA-256이다. `result_ref`/`source_ref`/facts/trace ref는 owner/session-bound content-addressed immutable bytes와 연결되고 contract에는 result/source content hash, metadata/plan/job bundle hash, coverage, grain/entity/lineage가 포함된다. `operator_trace`는 최대 32개 operation의 ID와 input/output contract hash만 가지며 rows나 full plan을 포함하지 않는다. facts/trace expiry는 state expiry보다 짧을 수 없다. Follow-up plan은 이 contract hash를 pin한다.

`explain_previous`는 state의 `executed_result_ref`로 이 exact contract를 읽고 criteria, lineage, answer facts, operator trace의 hash를 검증한 뒤 설명한다. evidence ref가 없거나 만료/불일치하면 추측하지 않고 `state_reference_expired` 또는 `state_reference_forbidden`으로 종료하며 retrieval job과 typed executor 호출 수는 모두 0이다.

후속 모드:

- `previous_result_transform`: 신규 조회 없이 이전 결과 filter/sort/rank
- `previous_source_transform`: 저장 source 범위 안에서 재집계
- `followup_requery`: 조건을 상속/교체한 새 조회
- `previous_result_enrich`: 이전 row를 left로 보존하며 새 source metric 결합
- `previous_source_expand`: v5 `followup_expand_source` 호환 의미다. 저장 source coverage가 충분하면 `previous_source_transform`, 부족하면 `followup_requery`로 compile한다.
- `followup_explain`: v5 `followup_explain/previous_trace` 호환 의미다. `explain_previous`만 실행하고 result/source row를 재계산하지 않는다.
- `new_analysis`: 이전 상태를 상속하지 않음

Mobile→POP처럼 제품 조건이 바뀌면 이전 Mobile 최종 행을 POP filter source로 사용하지 않는다. 유지 가능한 날짜·공정·grain만 상속하고 product condition은 교체한 뒤 source 범위가 부족하면 requery한다.

`previous_source_transform`은 필요한 row/filter/time 범위가 snapshot `coverage` 안에 있고 `row_set_complete=true`, `truncated=false`, source/stored row count가 같고 schema/revision/hash가 일치할 때만 허용한다. 어느 조건이든 증명할 수 없으면 `followup_requery`다. 따라서 MT-4의 mode는 둘 중 임의 선택이 아니라 저장된 coverage oracle로 결정된다.

## 10. Fail-closed validation

### Retrieval 전

- 모든 metric slot에 dataset binding 존재
- required parameter 값과 source format valid
- entity/required-parameter binding의 selection, session, expiry valid
- source alias/job ID unique
- required canonical fields가 dataset contract에 존재
- operation dependency DAG acyclic
- join grain/cardinality declared
- 모든 `registered_call`의 active function card, registry identity/hash/schema, argument binding과 resource policy가 exact match
- output metric마다 metric lineage 존재
- output dimension/key마다 dimension provenance와 grain binding 존재

### Execution 후

- 모든 required `source.result.v1.status`가 expected `ok|empty` 상태이고 required error source가 없음
- optional error는 plan의 `optional_enrichment` dependency/policy와 exact nullable output field가 일치
- result columns/order exact match
- no suffix columns
- no undeclared metric
- ordering contract satisfied
- row preservation/cardinality satisfied
- output lineage fingerprint match
- `registered_call` output schema/grain/row/resource measurement와 function lineage pin match

`source.result.v1.status`는 `ok|empty|error`만 허용한다. 성공 0행은 `empty`이고 metadata의 zero-row policy를 함께 기록한다. 누락·transport·schema·coverage 문제는 모두 `status=error`와 중앙 `error.v1.code`(`source_missing`, `source_retrieval_failed`, `source_schema_mismatch`, `source_coverage_incomplete` 등)로 표현한다. 별도 `failed|missing|schema_mismatch` status namespace를 만들지 않는다.

기본적으로 모든 source job은 `requirement=required`이며 하나라도 error면 결과를 만들지 않는다. `requirement=optional_enrichment`는 compiled metadata recipe가 미리 선언한 경우에만 허용하고 다음을 모두 만족해야 한다.

- primary row set, filter, grain, group, rank, join presence, formula의 의미에 영향을 주지 않는 left-preserving enrichment
- result contract가 실패 시 nullable인 exact optional columns와 availability lineage/error ID를 선언
- 실패 시 primary rows를 유지하고 그 optional columns만 typed null로 materialize
- 값 0 대체, 다른 metric 복사, optional column 자동 제거 금지

이 경우에만 response는 `status=partial`이고 canonical notice/error ID를 가진다. optional source가 row 선택이나 계산 의미에 관여하면 required로 승격되며 실패는 전체 `status=error`다.

## 11. Unsupported operation

MVP registry에 없는 분석은 free-form pandas LLM으로 우회하지 않는다.

```json
{
  "status": "error",
  "error": {
    "error_registry_version": "error_registry.v1",
    "error_id": "error:...",
    "code": "unsupported_operation",
    "stage": "route_eligibility",
    "message": "지원 registry에 없는 분석입니다.",
    "retryable": false,
    "details": {
      "normalized_shape_id": "shape:...",
      "missing_capability_id": "operator:...",
      "metadata_refs": []
    },
    "trace_id": "trace:..."
  }
}
```

동시에 `unsupported.telemetry.v1`에는 normalized shape ID, missing role/operator/formula/recipe ID, metadata/operator/route-policy version, count와 최초/최근 시각만 기록한다. 질문 원문 전체, source/result row, query, secret, prompt, raw LLM output은 기록하지 않는다. Telemetry 실패도 다른 route로 전환할 근거가 아니다.

새 built-in operation은 의미·grain·null/cardinality/zero/tie 정책을 review하고 implementation, schema, unit tests, representative canonical case를 함께 추가한 뒤 registry version을 올린다. 비표준 알고리즘은 같은 review 뒤 active function card와 hash-pinned standalone registry를 함께 등록하고 `registered_call` end-to-end case를 통과해야 한다. arbitrary pandas/exploration output 또는 생성 코드를 trusted operator/function으로 자동 승격하지 않는다.
