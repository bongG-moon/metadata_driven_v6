# Metadata Contract

## 1. Authoring과 runtime 분리

v6는 자연어 TXT 입력을 유지하지만 raw text를 runtime 규칙으로 직접 사용하지 않는다.

```text
Free-form natural-language TXT → immutable source block
  ├─ domain: 자유형 도메인 설명 → LLM 최대 1회 → display_name/description annotation only
  ├─ dataset: 자유형 데이터 설명 → LLM 최대 1회 → compact metadata.bootstrap.dataset-ir.v1
  ├─ main_filter: 자유형 조회 표현 → LLM 최대 1회 → target_type 필수 typed alias IR
  │                explicit_inventory proof complete → deterministic alias patch, LLM 0회
  ├─ compiler-owned source-registry.v3
  │    ├─ semantic_vocabulary: LLM에 전달하는 ID/업무 label 후보만
  │    └─ semantic_templates: LLM 비공개 실행 의미 구조와 sealed planner_policy
  ├─ optional high-trust: explicit inventory 또는 trusted Blueprint/external pin
  └─ domain_policy: explicit admin node inputs → LLM 0회
→ branch별 closed schema 검증 → v3 template/descriptor 결정론적 확장·병합
→ full draft JSON Schema validation → semantic lint → dependency/security closure
→ operator diff review → candidate/release hash 계산
→ MongoDB transaction으로 세 current section 동시 교체
→ 세 section release 검증·결합 → runtime metadata bundle
```

기본 Full-domain lane의 세 LLM 출력은 역할이 서로 다르다. Domain branch는 실행 metadata를 작성하지 않고 `metadata-annotation-proposal.schema.json`의 `display_name`과 `description`만 반환한다. Dataset branch는 내부용 compact Dataset IR을, Main Filter branch는 각 항목에 `target_type`, `target_id`, `expressions`를 요구하는 typed IR을 반환한다. 작업자는 이 IR, JSON, canonical ID inventory, relation endpoint/field-role 선언 문법을 알거나 맞출 필요가 없다.

세 branch가 받는 실행 후보는 `metadata.authoring.source-registry.v3`에서 투영한 `metadata.authoring.semantic-vocabulary.v1`뿐이다. 이 축약 어휘에는 semantic ID, dataset family와 업무용 labels만 있고 physical column, type, adapter/config/query ref와 실제 데이터는 없다. 같은 v3 registry의 `metadata.authoring.semantic-templates.v1`은 LLM에 전달하지 않는다. Compiler가 그 hash-pinned template의 metric/relation/grain/ordering/predicate/recipe/entity-group/alias와 `planner_policy`를 Domain annotation에 결정론적으로 결합하고, Dataset descriptor와 Source binding 및 Main Filter alias card를 확장한다. Closed decoder와 compiler가 schema, identity, type, field binding, dependency, join/cardinality, read-only·secret·registry 정책을 검증하고 valid release만 저장한다. LLM은 실행 의미를 새로 만들거나 validator와 writer를 우회할 수 없다.

LLM 경계는 `metadata.authoring.proposal.v1`로 닫는다. `complete` variant만 exact source hash와 `metadata.authoring.draft.v1`을 가지고 compile 단계로 이동한다. `needs_clarification` variant는 exact source hash, 1~3개 질문과 bounded `missing_fields`만 가지며 candidate/writer 단계로 이동하지 않는다.

세 LLM authoring 작업은 각각 별도 공통·특화 Prompt Template pair를 사용한다. 특화 업무 규칙은 각 특화 Template 본문에 직접 작성하고 변수 없이 렌더링한다. 자연어 source와 축약 의미 어휘는 Context Builder에서 Composer의 `runtime_context`로 한 번만 전달하며 Prompt 본문에 복제하지 않는다. Domain Policy는 Prompt/LLM 0회다. Main Filter의 zero-LLM path는 `source_grounding_mode=explicit_inventory`가 명시되고 alias와 canonical target이 모두 유일하게 pin된 경우에만 열린다.

최초 bootstrap은 세 입력 파일을 기계적으로 정형화하라는 뜻이 아니다. 기존 Domain/Dataset/Main Filter TXT를 그대로 합친 bundle이나, 동일 정보를 충분히 담은 자연어 문서를 받는다. 비전문 작업자는 평소 업무 표현, 불규칙한 문장 순서와 줄바꿈으로 입력할 수 있다. 필수 업무 정보가 없으면 `status=needs_clarification`의 `clarification.missing_fields`와 짧은 질문으로 빠진 내용을 설명하며 특정 구문, JSON, ID, 타입, 컬럼 또는 DSL로 다시 쓰라고 요구하지 않는다. 이 상태에는 draft/candidate/persist 산출물이 없어야 한다.

현재 live authoring profile은 v6 전용 `domain_v6.txt`+`dataset_v6.txt`+`main_filter_v6.txt` bundle과 exact `gemini-3.5-flash-lite`, temperature 0, fallback 0, repair 0을 사용한다. Provider 응답이 closed schema를 통과하지 못하면 자동 보정이나 재호출을 하지 않는다.

## 2. 운영 Metadata 3컬렉션 계약

v5 데이터를 보호하면서 운영자가 관리할 metadata collection은 아래 세 개로 제한한다. 각 문서는 비전문 작업자가 입력한 `source_text`, LLM/컴파일러가 만든 `normalized_metadata`, source/section/document hash, 세 문서가 함께 갱신됐음을 증명하는 동일 `release_id`와 manifest를 가진다.

| 용도 | 기본 collection |
| --- | --- |
| 도메인 원문·metric/relation/grain/recipe/공통 정책 | `agent_v6_domain_metadata` |
| 테이블 원문·dataset/field binding | `agent_v6_table_catalog` |
| 메인필터 원문·predicate/alias | `agent_v6_main_filter` |
| session state | `agent_v6_session_state` |
| result/source ref | `agent_v6_result_store` |

운영 database 기본값은 `datagov`다. 자동/라이브 검증은 기본적으로 `MONGODB_VALIDATION_DATABASE=datagov_v6_validation`을 사용해 운영 metadata를 오염시키지 않는다. Data Analysis의 `01 사용 가능 메타데이터 불러오기`에는 MongoDB URI·database·세 metadata collection 이름·timeout이 보이며, domain ID·environment·source mode는 입력으로 노출하지 않는다. Loader는 입력받은 안전하고 서로 다른 3컬렉션에서 가장 최근의 완전한 동일 release를 자동 탐색·결합하고 hash 불일치 시 fail-closed한다. Source config/query의 secret·실제 query는 이 세 collection에 저장하지 않고 기존 승인 adapter/registry 경계에서만 해석한다.

## 3. 공통 envelope

```json
{
  "schema_version": "metadata.v6",
  "kind": "domain.metric|domain.recipe|domain.process_group|domain.process_order|domain.product_group|dataset|filter|entity|grain",
  "identity": {
    "namespace": "manufacturing",
    "key": "wip_boh_quantity"
  },
  "revision": 1,
  "lifecycle": {
    "status": "draft|validated|active|deprecated|quarantined"
  },
  "provenance": {
    "source_id": "source:sha256",
    "source_block": 12,
    "content_sha256": "...",
    "compiler_version": "...",
    "prompt_sha256": "...",
    "model": "..."
  },
  "dependencies": [
    {
      "kind": "dataset",
      "namespace": "manufacturing",
      "key": "wip",
      "revision": 3,
      "contract_sha256": "..."
    }
  ],
  "contract": {},
  "contract_sha256": "...",
  "validation": {
    "schema": {
      "status": "valid",
      "schema_id": "metadata.v6/dataset",
      "schema_sha256": "..."
    },
    "semantic_lint": {
      "status": "valid",
      "ruleset_version": "metadata-lint.v1",
      "issues": []
    },
    "dependency_closure": {
      "status": "valid",
      "bundle_sha256": "...",
      "resolved_at": "2026-07-31T00:00:00Z"
    }
  }
}
```

Runtime loader는 다음 조건을 모두 만족하는 record만 읽는다.

- `schema_version=metadata.v6`
- `lifecycle.status=active`
- 지원 compiler version
- `validation.schema.status=valid`
- `validation.semantic_lint.status=valid`
- `validation.dependency_closure.status=valid`
- dependency record가 존재하고 `namespace/kind/key/revision/contract_sha256`가 모두 일치
- 현재 dependency closure를 다시 계산한 hash가 `validation.dependency_closure.bundle_sha256`와 일치
- dataset record이면 config/query registry의 revision/hash가 source pin과 일치

`contract_sha256`는 envelope 전체가 아니라 **`contract` object만** canonicalize한 JSON bytes의 SHA-256이다. `contract_sha256` 자기 자신, identity/revision/lifecycle/provenance/validation은 hash material에서 제외한다. 배열 순서가 의미 없는 field는 schema가 정한 정렬 규칙을 먼저 적용하고, 의미 있는 ordered member/step/tie-break 배열은 보존한다. `validation.dependency_closure.bundle_sha256`는 dependency의 sorted `(namespace, kind, key, revision, contract_sha256)` tuple과 root contract hash의 canonical projection으로 계산한다. Writer와 loader가 서로 다른 projection/직렬화 방식으로 hash를 계산하는 것을 허용하지 않는다.

## 4. Dataset contract

Dataset은 filter/group/join/output에서 사용할 canonical field binding의 단일 원천이다.

```json
{
  "dataset_key": "target",
  "family": "production_plan",
  "time_scope": "history",
  "source": {
    "type": "goodocs",
    "config_ref": "goodocs:target",
    "config_revision": 2,
    "config_sha256": "...",
    "query_ref": "query:target",
    "query_revision": 5,
    "query_sha256": "..."
  },
  "execution_policy": {
    "access_mode": "read_only",
    "timeout_ms": 30000,
    "max_rows": 50000
  },
  "parameters": {
    "DATE": {
      "required": false,
      "value_type": "LocalDate",
      "input_format": "YYYYMMDD",
      "source_format": "YYYY-MM-DD",
      "timezone": "Asia/Seoul"
    }
  },
  "fields": {
    "MODE": {
      "physical_column": "Mode",
      "semantic_type": "string",
      "roles": ["filter", "group", "join", "compare", "project", "sort", "output"],
      "aliases": ["MODE", "Mode", "모드"],
      "allowed_filter_operators": ["eq", "in", "ne", "not_in", "contains", "starts_with", "ends_with", "is_null", "is_not_blank"],
      "null_policy": "preserve_blank",
      "case_policy": "exact"
    },
    "OUT_PLAN_QTY": {
      "physical_column": "OUT 계획",
      "semantic_type": "quantity",
      "roles": ["metric", "aggregate", "project", "sort", "rank", "output"],
      "aliases": ["OUT_PLAN_QTY", "OUT 계획", "출하 계획 수량"],
      "coercion": "numeric",
      "unit": "count",
      "rollups": ["sum", "min", "max"]
    }
  },
  "default_detail_fields": ["MODE", "OUT_PLAN_QTY"]
}
```

### Binding 규칙

- 한 canonical field는 한 dataset에서 primary physical column 하나를 가진다.
- 호환 alias가 필요하면 ordered alias 목록과 precedence를 metadata에 명시한다.
- runtime row에 primary와 alias가 동시에 존재하면 자동 선택하지 않고 `ambiguous_field_binding`으로 중단한다.
- missing mapping 시 canonical name을 physical name으로 추측하지 않는다.
- retrieval adapter는 physical row와 source schema만 반환한다.
- **Source Contract Merger**가 dataset binding을 적용해 physical→canonical 변환을 정확히 한 번 수행하고, coercion·null policy·collision을 검사한다.
- typed executor는 canonical table만 입력받으며 rename, alias fallback, physical-column 추측을 수행하지 않는다.
- display label은 field name과 분리한다.
- dataset field는 `filter|group|join|compare|aggregate|derive|project|sort|rank|metric|output` 중 허용 role과 role별 operator/rollup을 선언한다.
- 사용자가 등록된 컬럼 alias를 직접 말하면 Candidate Selector는 `field_application:<dataset-family>:<canonical-field>:<role>` candidate를 만든다. Intent LLM은 이 ID만 선택하고 Plan Compiler는 field binding의 role/type/ACL을 재검사한다.
- 같은 field라도 `project`만 허용된 경우 filter/group/rank에 사용할 수 없다. 등록되지 않은 raw column, role 승격, source schema에서 우연히 보인 physical column 사용은 `plan_contract_error`다.

## 5. Source registry와 resolver 경계

`config_ref`와 `query_ref`는 자유 문자열이나 실행 가능한 payload가 아니다. 일반 작업자 TXT의 입력 항목도 아니다. 작업자는 데이터셋과 원천 시스템을 자유로운 자연어로 설명하고, authoring의 별도 **승인 업무 어휘·Source 참조 레지스트리** 노드가 업무 표현을 승인 semantic ID에 연결할 작은 어휘와 dataset별 운영 참조를 분리해 제공한다. LLM에는 작은 어휘만 전달되며, 결정론적 compiler가 exact dataset ID를 운영 참조와 결합한다. LLM이 누락하거나 다르게 쓴 binding 필드는 저장 전에 폐기·교체한다.

### 5.1 Source Registry v3와 `semantic_templates`

승인 레지스트리의 root 계약은 `metadata.authoring.source-registry.v3`다. Root에는 dataset별 실행 binding/descriptor, `semantic_vocabulary`, `semantic_templates`와 template provenance hash가 닫힌 키셋으로 존재한다.

- `semantic_vocabulary`: Domain/Dataset/Main Filter LLM에 제공 가능한 최소 `id/family/labels` projection이다. 실행 참조, 물리 컬럼, 타입, coercion, metric binding과 template 본문은 없다.
- `semantic_templates`: compiler 전용 `metadata.authoring.semantic-templates.v1`이다. `metrics`, `relations`, `grains`, `orderings`, `predicates`, `recipes`, `entity_groups`, `aliases`, locale/timezone과 `planner_policy`를 가진다. 이 object는 prompt/runtime context와 LLM raw output에 넣지 않는다.
- `semantic_templates_sha256`, `semantic_templates_blueprint_sha256`, `semantic_templates_executable_sha256`, `semantic_templates_projection_sha256`: template가 검토된 executable blueprint/catalog projection에서 결정적으로 생성됐음을 검증하는 trust pin이다.

Domain LLM annotation은 `display_name`과 `description`만 소유한다. Compiler가 검증된 `semantic_templates`를 붙여 실행 section을 만들며 template key 추가·삭제·수정, alias 실행 의미 변경과 planner policy 변경을 허용하지 않는다. `semantic_templates.planner_policy`는 실행 호환성 정책으로 봉인된다. Domain Policy Flow의 `output_profile_json`도 `planner_profile`과 `legacy_catalog_sha256`을 덮어쓸 수 없다.

### 5.2 `config_ref`

서버 측 운영 adapter의 versioned descriptor를 가리킨다. v6 저장소의 `approved_source_registry.json`은 비밀 없는 승인 ID 매핑과 hash anchor이며 connection record 자체가 아니다.

```json
{
  "config_ref": "config:goodocs:target@2",
  "revision": 2,
  "adapter_type": "goodocs",
  "endpoint_ref": "endpoint:goodocs-prod",
  "required_secret_inputs": ["api_token"],
  "allowed_actions": ["read"],
  "acl": {
    "resolve_roles": ["metadata-runtime"],
    "admin_roles": ["metadata-admin"]
  },
  "contract_sha256": "..."
}
```

Registry에는 token, password, API key, connection string을 저장하지 않는다. `required_secret_inputs`는 Langflow custom component의 secret node input 이름만 선언한다. Runtime resolver는 호출 시 node input에서 secret을 주입하고 adapter call이 끝나면 폐기한다. secret 값은 metadata, state, trace, result ref, LLM prompt에 복사하지 않는다.

### 5.3 `query_ref`

서버 측 운영 adapter의 immutable query/operation revision을 가리킨다. 작업자나 authoring LLM은 template 본문을 소유하지 않는다.

```json
{
  "query_ref": "query:target@5",
  "revision": 5,
  "adapter_type": "goodocs",
  "template": "reviewed server-side template or endpoint operation",
  "parameter_schema": {
    "DATE": {"value_type": "LocalDate", "required": false}
  },
  "field_slots": {
    "DATE": {"physical_expression_id": "date_column", "roles": ["parameter", "filter"], "pushdown": "required"},
    "MODE": {"physical_expression_id": "mode_column", "roles": ["filter", "projection"], "operators": ["eq", "in"], "pushdown": "optional"},
    "OUT_PLAN_QTY": {"physical_expression_id": "out_plan_column", "roles": ["projection", "metric"]}
  },
  "allowed_actions": ["read"],
  "timeout_ms_max": 30000,
  "max_rows_max": 50000,
  "acl": {
    "resolve_roles": ["metadata-runtime"],
    "edit_roles": ["metadata-query-admin"]
  },
  "contract_sha256": "..."
}
```

Source Registry Resolver는 dataset이 pin한 config/query revision과 hash, adapter type, parameter schema를 확인한다. 자유 SQL, 임의 endpoint, dynamic collection 이름은 받지 않는다. Dataset policy와 registry 상한 중 더 엄격한 timeout/row limit을 적용하고, read-only action만 허용한다. Adapter는 가능하면 upstream에 `max_rows+1` 제한을 적용하고 그렇지 않으면 streaming count가 한계를 넘는 즉시 중단한다. 초과 row는 묵시적으로 자르지 않고 `source_row_limit_exceeded`로 실패한다. Query timeout은 `source_timeout`으로 분리한다. ACL 실패는 retrieval 전에 중단한다.

### 5.4 Canonical outbound binding

Plan과 `retrieval.job_bundle.v1`의 filter, required field, parameter ID는 canonical이다. **Trusted Config/Query Resolver**만 이를 branch-local physical query slot으로 낮춘다.

1. Dataset field binding에서 canonical field의 exact physical column/expression ID와 allowed role을 찾는다.
2. Query registry의 reviewed slot이 같은 canonical field, typed operator, parameter type, projection role을 허용하는지 확인한다.
3. 값은 parameterized bind로 전달하고 SQL/URL/document path 문자열에 직접 이어 붙이지 않는다.
4. branch-local resolved job에 dataset/query contract hash와 canonical→physical `binding_proof`를 기록한다.
5. Adapter가 반환한 physical schema는 같은 dataset binding hash를 가진 **Source Contract Merger**가 역방향이 아니라 선언된 physical→canonical mapping으로 한 번 변환한다.

Resolver가 mapping/role/operator를 증명하지 못하면 broad query나 canonical-name fallback을 하지 않고 `source_schema_mismatch` 또는 `plan_contract_error`로 종료한다. Query registry가 명시적으로 `pushdown=optional`을 허용하는 filter만 bounded complete source를 가져온 뒤 canonical executor filter로 처리할 수 있고, 이때 source snapshot은 fetched scope와 post-filter scope를 별도로 기록한다. Required date/tenant/security filter는 항상 `pushdown=required`다.

Resolved job의 physical slot, raw query, secret은 retriever branch 밖으로 직렬화하지 않는다. Trace와 execution evidence에는 canonical job hash, binding proof hash, query revision/hash만 남긴다.

## 6. Main filter, alias, group contract

Main Filter는 dataset physical column mapping이 아니라 canonical semantic selection만 소유한다.

### 6.1 Typed main filter와 alias

```json
{
  "filter_id": "MODE",
  "target_field": "MODE",
  "value_type": "string",
  "allowed_operators": ["eq", "in"],
  "default_operator": "eq",
  "aliases": [
    {"text": "Mode", "locale": "en", "priority": 100},
    {"text": "모드", "locale": "ko", "priority": 100}
  ],
  "alias_policy": {
    "normalization": ["unicode_nfkc", "trim", "collapse_space", "latin_casefold"],
    "match": "bounded_longest",
    "conflict": "fail_ambiguous"
  }
}
```

`bounded_longest`는 다음 순서로만 판정한다.

1. alias의 시작과 끝이 문자열 경계이거나 공백·문장부호 경계여야 한다. 영문·숫자·한글 token 내부 substring은 match하지 않는다.
2. 겹치는 후보는 가장 넓은 span, normalized alias가 가장 긴 후보, 높은 `priority` 순으로 고른다.
3. 이 기준까지 같은 서로 다른 identity가 남으면 `ambiguous_alias`로 실패한다.

Alias는 사용자 표현을 semantic identity로 고를 뿐 physical column 후보가 아니다. Compiler는 alias match 뒤 dataset contract의 canonical field binding을 별도로 검증한다.

### 6.2 Process group

```json
{
  "group_id": "process_group.WB",
  "entity_type": "process_group",
  "target_field": "OPER_NAME",
  "member_value_type": "string",
  "aliases": [{"text": "W/B", "priority": 100}, {"text": "WB 공정", "priority": 90}],
  "members": [
    {"value": "W/B1", "operator": "eq"},
    {"value": "W/B2", "operator": "eq"},
    {"value": "W/B3", "operator": "eq"},
    {"value": "W/B4", "operator": "eq"},
    {"value": "W/B5", "operator": "eq"},
    {"value": "W/B6", "operator": "eq"}
  ],
  "expansion": "closed_set",
  "alias_policy": {
    "normalization": ["unicode_nfkc", "trim", "collapse_space", "latin_casefold"],
    "match": "bounded_longest",
    "conflict": "fail_ambiguous"
  }
}
```

Compiler는 group을 dataset별 canonical `OPER_NAME`의 exact closed set으로 확장한다. 사용자가 단일 공정 값을 명시한 경우 그 값과 group alias를 혼합하지 않는다. group member가 없는 dataset, fuzzy member, substring expansion은 실패한다.

### 6.3 Ordered process range

`D/S1~D/A4`, `D/A1~W/B6` 같은 범위는 문자열 정렬이나 LLM 추측으로 확장하지 않는다. `domain.process_order` record가 다음을 소유한다.

- versioned `order_id`
- canonical `OPER_NAME`별 unique process ID와 unique numeric `sequence`
- endpoint alias
- inclusive/exclusive 기본값
- 적용 가능한 dataset family

Request/Candidate Builder는 원문 span의 두 endpoint를 candidate ID로 만들고, Plan Compiler는 pin된 process-order revision에서 numeric sequence를 찾아 inclusive closed range로 확장한다. endpoint 누락·중복 sequence·dataset의 `OPER_NAME`/`OPER_SEQ` binding 누락은 compile error다. Runtime row의 `OPER_SEQ`와 compiled order가 다르면 source schema/order mismatch로 종료하며 lexicographic fallback을 하지 않는다.

### 6.4 Product group

```json
{
  "group_id": "product_group.Mobile",
  "entity_type": "product_group",
  "aliases": [{"text": "Mobile", "priority": 100}, {"text": "모바일", "priority": 90}],
  "grain_id": "product.standard",
  "predicate": {
    "op": "and",
    "clauses": [
      {"field": "MODE", "operator": "starts_with", "value": "LP"},
      {"field": "PKG_TYPE1", "operator": "in", "values": ["LFBGA", "TFBGA", "UFBGA", "VFBGA", "WFBGA"]},
      {"field": "MCP_NO", "operator": "null_or_blank"}
    ]
  },
  "allowed_operators": ["eq", "in", "starts_with", "null_or_blank", "is_not_blank"],
  "alias_policy": {
    "normalization": ["unicode_nfkc", "trim", "collapse_space", "latin_casefold"],
    "match": "bounded_longest",
    "conflict": "fail_ambiguous"
  }
}
```

Product group predicate는 canonical field와 typed operator만 사용하며 dataset physical column을 포함하지 않는다. `product_group.POP`은 위와 같은 `MODE`/`PKG_TYPE1` base predicate에 `MCP_NO is_not_blank`를 사용한다. Compiler는 대상 dataset이 predicate field와 grain을 지원하는지 검사한다. follow-up에서 Mobile→POP처럼 group을 교체하면 이전 group predicate를 제거하고 새 predicate를 추가하며, 두 predicate를 누적하지 않는다.

## 7. Temporal contract

```json
{
  "metric_id": "WIP_BOH_QTY",
  "business_timepoint": "BOH",
  "requested_time_type": "LocalDate",
  "dataset_selector": {
    "family": "wip",
    "time_scope": "history"
  },
  "query_time": {
    "anchor": "requested_date",
    "offset_days": -1,
    "timezone": "Asia/Seoul",
    "calendar": "gregorian"
  },
  "source_parameter": "DATE",
  "display_date": "requested_date",
  "zero_row_policy": "valid_empty",
  "inherit_filters": true
}
```

`6/27 아침재공`은 LLM이 `wip/20260626`을 직접 쓰는 것이 아니다. LLM은 `WIP_BOH_QTY`와 requested date만 선택하고 compiler가 위 contract로 query date를 계산한다.

Dataset의 source date format이 다르면 source adapter가 parameter contract에 따라 변환한다. 모든 날짜를 전역 `YYYYMMDD`로 강제하지 않는다.

## 8. Metric contract

```json
{
  "metric_id": "UPH",
  "unit": "unit_per_hour",
  "value_type": "number",
  "source_binding": {"dataset_family": "equipment_uph", "field": "UPH"},
  "additivity": {
    "default": "non_additive",
    "allowed_rollups": ["mean"]
  },
  "zero_policy": "preserve_zero",
  "null_policy": "exclude_from_mean"
}
```

- metric은 이름 substring으로 찾지 않는다.
- additive, snapshot, rate, average, ratio를 구분한다.
- formula metric은 허용 expression AST 또는 versioned recipe를 참조한다.
- rollup이 등록되지 않은 metric을 자동 `sum` 처리하지 않는다.

Formula metric은 실행 가능한 문자열이 아니라 다음과 같은 closed typed AST다.

```json
{
  "metric_id": "ACHIEVEMENT_RATE",
  "unit": "percent",
  "value_type": "number",
  "formula": {
    "version": "formula.v1",
    "evaluation_stage": "after_aggregate",
    "expression": {
      "op": "multiply",
      "args": [
        {
          "op": "safe_divide",
          "args": [
            {"metric_ref": "ACTUAL_INPUT_QTY"},
            {"metric_ref": "TARGET_INPUT_QTY"}
          ],
          "zero_division": "null"
        },
        {"literal": 100, "value_type": "number"}
      ]
    },
    "rounding": {"digits": 1, "mode": "half_even"},
    "max_depth": 6,
    "max_nodes": 32
  }
}
```

`formula.v1`은 `add|subtract|multiply|safe_divide|abs|round|min_pair|max_pair`와 typed literal/metric ref만 허용한다. attribute access, function name/call, index, import, Python/pandas expression은 금지한다. `safe_divide`는 `zero_division=null|zero|error`를 반드시 선언하고, null propagation, unit compatibility, evaluation stage, rounding은 compile 때 검증한다.

## 9. Entity와 grain

```json
{
  "grain_id": "product.standard",
  "entity_id": "product",
  "keys": ["TECH", "DEN", "MODE", "PKG_TYPE1", "PKG_TYPE2", "LEAD", "MCP_NO"],
  "null_match_policy": "blank_equals_blank",
  "uniqueness": "composite",
  "allowed_dataset_families": ["production", "wip", "equipment", "target"]
}
```

Follow-up row match는 저장된 grain/entity ID와 exact key set을 사용한다. 현재 질문의 표시 컬럼이나 metric을 identity key에 추가하지 않는다.

## 10. Recipe contract

Recipe는 pandas code가 아니라 typed operation DAG다.

```json
{
  "recipe_id": "presence.left_positive_right_zero",
  "input_roles": ["left", "right"],
  "steps": [
    {"op": "aggregate", "role": "left"},
    {"op": "aggregate", "role": "right"},
    {
      "op": "presence_filter",
      "rule": "left_positive_right_missing_or_zero",
      "preserve": "left"
    }
  ],
  "join": {
    "grain_id": "product.standard",
    "cardinality": "one_to_one_after_aggregate"
  }
}
```

Recipe dependency는 connected bundle로 선택한다. recipe만 선택되고 필요한 metric, grain, dataset record가 candidate budget에서 잘리는 상태를 허용하지 않는다.

Join recipe는 최소 다음 실행 의미를 고정한다.

```json
{
  "recipe_id": "join.product.production_wip",
  "op": "join",
  "left_role": "production",
  "right_role": "wip",
  "join_type": "outer",
  "key_mappings": [
    {"left_field": "TECH", "right_field": "TECH"},
    {"left_field": "DEN", "right_field": "DEN"},
    {"left_field": "MODE", "right_field": "MODE"}
  ],
  "cardinality": "one_to_one_after_aggregate",
  "null_key_policy": "blank_equals_blank",
  "duplicate_policy": {
    "left": "error_after_declared_aggregate",
    "right": "error_after_declared_aggregate"
  },
  "multi_match_policy": "error",
  "empty_side_policy": "preserve_other_side_with_declared_null_metrics",
  "suffix_policy": "forbid",
  "output_fields": ["TECH", "DEN", "MODE", "PRODUCTION_QTY", "WIP_QTY"]
}
```

Join key는 canonical field pair만 사용한다. `inner|left|right|outer|semi|anti` 중 recipe/plan schema가 허용한 type, declared cardinality, null-key normalization, duplicate/multi-match policy, empty-side schema와 output projection이 모두 있어야 한다. 오른쪽 다중 행을 count/list로 붙이는 enrich는 join 전에 versioned aggregation을 수행하며, undeclared many-to-many나 `_x/_y` suffix는 실패다.

## 11. Specialized function과 `registered_call` contract

Declarative predicate, formula, recipe와 공통 typed operator로 표현할 수 없는 검토된 알고리즘만 specialized function으로 등록한다. `specialized_functions`는 metadata-only 설명 목록이 아니며 다음 두 artifact가 exact identity/hash로 결합될 때만 실행 가능하다.

1. active Domain Package의 **function card**: 언제 선택할지와 어떤 typed I/O/resource contract를 요구하는지 선언
2. build-time **standalone function registry**: 실제 standalone implementation source와 immutable hash를 allowlist

Function card 예시는 다음과 같다.

```json
{
  "function_id": "product.match_tokens",
  "version": 1,
  "execution_mode": "registered_standalone",
  "implementation_sha256": "<64 lowercase hex>",
  "registry_entry_sha256": "<64 lowercase hex>",
  "selection": {
    "aliases": ["제품 속성 토큰 매칭"],
    "required_evidence_kinds": ["product_token_sequence"],
    "applicable_dataset_families": ["product_master"],
    "ambiguity_policy": "intent_llm_or_unsupported"
  },
  "required_fields": ["TECH", "DEN", "MODE"],
  "required_roles": {"TECH": ["filter"], "DEN": ["filter"], "MODE": ["filter"]},
  "input_schema_ref": "registered-function-input:product.match_tokens.v1",
  "input_schema_sha256": "<64 lowercase hex>",
  "output_schema_ref": "registered-function-output:product.match_tokens.v1",
  "output_schema_sha256": "<64 lowercase hex>",
  "output_contract": {
    "kind": "table",
    "grain_policy": "preserve_input",
    "lineage_policy": "append_function_ref"
  },
  "resource_policy": {
    "timeout_ms": 3000,
    "max_rows": 50000,
    "max_memory_mb": 256,
    "network": "deny",
    "filesystem": "deny",
    "subprocess": "deny"
  },
  "failure_policy": "fail_closed"
}
```

Function card와 authoring input에는 Python source, module path, import statement, callable object, SQL/query, endpoint 또는 secret을 넣지 않는다. Domain Policy Flow의 명시적 관리자 입력만 function card를 추가·upsert할 수 있고 LLM은 0회다. Compiler는 card를 저장하기 전에 build manifest가 pin한 registry에서 exact `(function_id, version)`을 찾고 다음 값이 모두 같은지 검증한다.

- implementation source SHA-256
- registry-entry SHA-256
- input/output schema ID와 SHA-256
- deterministic capability와 허용 side-effect policy
- timeout, row, memory 상한

Registry entry는 source-of-truth implementation 파일, standalone component/class ID, 위 hash와 build manifest hash를 가진다. Builder는 implementation과 registry projection을 standalone execution source에 embed하되, Flow JSON에 code를 input value로 넣거나 runtime에 sibling module을 import하지 않는다. Registry에 없는 card, hash/schema 불일치, 필요한 canonical field/role 누락은 candidate를 활성화하지 않고 package compile/activation을 `metadata_dependency_error`로 종료한다.

Runtime은 다음 순서를 지킨다.

1. Candidate Selector가 question evidence, function card의 selection rule과 attested registry를 결합해 `registered_function_application:<function_id>:v<version>:<index>` candidate를 만든다.
2. Deterministic route 또는 Intent LLM은 그 candidate ID를 `operation_refs`로 선택한다. LLM은 function ID, argument, code 또는 output field를 직접 출력하지 않는다.
3. Plan Compiler가 candidate의 resolved semantics와 typed literal/metadata refs에서 closed argument binding을 만들고 exact pins가 포함된 `op=registered_call`을 생성한다.
4. Typed Executor의 Registered Function Gateway가 registry pin, canonical input schema, required field/role와 resource policy를 재검증하고 build-time allowlist implementation만 호출한다.
5. output schema, grain, row count와 lineage를 검증하고 operator trace에 function ID/version, implementation/registry hash, input/output contract hash만 남긴다.

Dynamic import, `eval`/`exec`, metadata code 실행, arbitrary network/file/subprocess와 secret 접근은 금지한다. 실패를 일반 filter, 다른 function, pandas code 또는 LLM으로 대체하지 않는다. Gateway와 executor consumer가 구현되기 전에는 function card 입력을 실행 가능 옵션으로 표시하거나 active package에 승인하지 않는다.

## 12. Follow-up transfer contract

```json
{
  "entity_id": "lot",
  "source_result_role": "previous_result",
  "source_grain_id": "lot.id",
  "source_field": "LOT_ID",
  "target_dataset": "hold_history",
  "target_parameter": "LOT_ID",
  "operator": "in",
  "dedupe": true,
  "sort_values": "asc",
  "chunk_size": 200,
  "max_total_values": 2000,
  "null_policy": "drop",
  "freshness_seconds": 3600
}
```

후속 전달에는 실행 당시 metadata revision과 result contract hash를 함께 저장한다. Parameter Binder는 current HOLD 결과의 전체 LOT_ID set을 stable sort/dedupe하고 200개씩 job으로 분할한다. 일부 값만 자르지 않으며 `max_total_values`를 넘으면 `parameter_value_limit_exceeded`로 종료한다.

`HOLD 시간이 가장 오래된 LOT의 이력`은 `lot_status`에 존재하지 않는 `HOLD_STARTED_AT`을 추측하거나 `OPER_IN_TM`/`FAC_IN_TIME`으로 대체하지 않는다. 다음 typed recipe를 사용한다.

`hold_history` dataset에는 아래 field binding이 필수다.

```json
{
  "HOLD_EVENT_AT": {
    "physical_column": "HOLD_TM",
    "semantic_type": "LocalDateTime",
    "timezone": "Asia/Seoul",
    "roles": ["filter", "aggregate", "sort", "derive", "output"],
    "rollups": ["max"],
    "null_policy": "error_when_current_hold_candidate",
    "coercion": "strict_datetime"
  }
}
```

1. 이전 current HOLD 결과의 모든 `LOT_ID`를 위 transfer contract로 `hold_history`에 bind한다.
2. `hold_history.HOLD_TM`을 canonical `HOLD_EVENT_AT`으로 parse한다. 이 field는 `Asia/Seoul`의 local timestamp이고 invalid/null은 silent drop하지 않는다.
3. current HOLD LOT마다 `aggregate(group_by=LOT_ID, max(HOLD_EVENT_AT), output=CURRENT_HOLD_STARTED_AT)` typed temporal-extrema operation을 실행한다. 이는 arithmetic `formula.v1`이 아니며 output type/timezone을 유지하고 groupwise-max lineage를 기록한다. `lot_status.HOLD_STAT=OnHold`와 latest hold event가 current episode라는 업무 규칙은 versioned recipe dependency로 명시한다.
4. `CURRENT_HOLD_STARTED_AT` 오름차순, `LOT_ID` 오름차순 tie-break로 LOT 하나를 고른다.
5. 이미 조회한 `hold_history` source에서 선택 LOT의 전체 history rows를 반환한다.

현재 HOLD LOT 중 하나라도 valid `HOLD_EVENT_AT` history가 없거나 요청한 LOT_ID set 전체 coverage를 증명하지 못하면 `source_coverage_incomplete`로 종료한다. 이 방식은 현재 catalog에 없는 hold-start physical column을 만들지 않으면서 실제 `HOLD_TM`을 근거로 선택한다.

## 13. 검증 후 3컬렉션 저장

Langflow 등록 Flow는 자연어 해석과 결정론적 검증이 성공한 한 번의 실행에서 current metadata를 저장한다. 별도 active pointer, bundle archive, pending write collection은 runtime 필수 계약이 아니다.

1. Full-domain 등록은 자유형 Domain·Dataset·Main Filter 원문을 작업별 공통·특화 Prompt pair로 각각 해석해 LLM 정확히 3개의 branch 결과를 만든다. Domain은 표시명/설명 annotation only, Dataset은 compact Dataset IR, Main Filter는 `target_type` 필수 typed alias IR이다. 후속 Dataset/Main Filter는 최대 1회, Domain Policy는 0회다.
2. Compiler가 `source-registry.v3`의 hash-pinned template/descriptor를 결합하고 전체 package schema, semantic lint, dependency/security closure, section ownership을 검증한다. 실패 또는 clarification이면 MongoDB write는 0건이다.
3. 검증된 runtime catalog를 domain, table catalog, main filter section으로 분할한다. 각 문서에 해당 자연어 `source_text`, `source_sha256`, `normalized_metadata`, `section_sha256`, 공통 package metadata를 기록한다.
4. 세 section hash와 package/catalog/bundle hash를 한 `metadata.release.v1` manifest로 묶고 `release_id=release:<manifest_sha256>`를 만든다.
5. MongoDB transaction에서 `environment:domain_id`의 세 current 문서를 `replace_one(upsert=true)`로 교체한다. transaction 안에서 다시 읽고 세 release/manifest/identity/revision/hash를 검증해 동일 Domain Package로 결합되지 않으면 전체 transaction을 중단한다.
6. `mode=validate_only` 또는 `dry_run=true`이면 같은 컴파일·release 검증을 수행하지만 MongoDB write는 하지 않는다.

Runtime loader는 domain metadata collection에서 `updated_at`, revision, `_id` 순으로 가장 최근 문서를 찾고 그 identity와 같은 table catalog/main filter 문서를 자동으로 읽는다. 세 문서의 `_id`, domain/environment/revision, release ID, manifest, section/document/source hash가 모두 일치할 때만 package를 제공한다. 한 문서가 누락됐거나 이전 release이거나 운영자가 `normalized_metadata`를 직접 수정하면 fail-closed한다. 단순 current 구조이므로 자동 revision history/rollback은 제공하지 않으며, 이력이 필요하면 세 current 문서의 변경 스트림·백업 또는 별도 운영 감사 시스템을 사용한다.

## 14. v5 migration 원칙

1. v5 collection은 read-only source로 사용한다.
2. TXT 원본을 가능한 경우 다시 compile한다.
3. 기존 JSON만 있는 record는 migration candidate로 변환하되 provenance에 `source_type=v5_record`를 기록한다.
4. mapping/temporal/metric/dependency lint를 통과하지 못한 record는 `quarantined`로 둔다.
5. active 전환 전 diff report와 validation case 영향을 검토한다.
6. 자동 overwrite나 in-place schema upgrade를 하지 않는다.
