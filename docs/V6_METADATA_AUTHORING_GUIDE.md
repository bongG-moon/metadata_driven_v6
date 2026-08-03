# v6 Metadata 자연어 등록 가이드

## 1. 사용자는 자연어 TXT를 계속 입력한다

사용자는 JSON Schema, `dataset_key`, physical column mapping 구조나 relation/field-role inventory 문법을 직접 작성할 필요가 없다. canonical/등록 ID, 타입과 물리 컬럼을 몰라도 된다. 기존처럼 Domain, Table Catalog, Main Filter 정보를 자신이 아는 업무 표현으로 자유롭게 적는다. 문장 순서, 제목, 표기 방식, 조사, 오탈자와 줄바꿈이 달라도 괜찮다.

기본 full-domain bootstrap에서 작업자는 기존처럼 Domain·Dataset·Main Filter TXT에 자유로운 자연어만 입력한다. Flow 내부의 작업별 공통·특화 Prompt Template pair가 각 원문을 최대 한 번씩 해석한다. 공통·특화 Template은 별도 node/source/hash/edge이고 특화 업무 규칙은 특화 Template 본문에 직접 작성한다. 그러나 세 LLM 출력은 full draft가 아니다. Domain은 `display_name`과 `description` annotation만, Dataset은 compact `metadata.bootstrap.dataset-ir.v1`, Main Filter는 모든 항목에 `target_type`이 필수인 `metadata.bootstrap.main-filter-ir.v1`만 반환한다. 작업자가 보는 입력 계약에는 JSON/DSL, compact IR, canonical ID inventory, 컬럼 타입 표, `config_ref`/`query_ref` 문법이 없다.

결정론적 engine은 `metadata.authoring.source-registry.v3`의 compiler-owned `semantic_templates`, dataset descriptor/Source binding과 alias target으로 세 결과를 확장·병합해 완전한 `metadata.authoring.draft.v1` 후보를 만든다. Domain 실행 metric/relation/grain/ordering/predicate/recipe/entity-group/alias는 LLM이 생성하지 않는다. Dataset용 compact IR과 Main Filter typed IR도 Gemini 내부 중간 계약일 뿐이며 registry membership을 통과해야 full section이 된다. 이 후보는 저장되거나 실행되기 전에 JSON Schema, canonical identity, field binding, type, dependency closure, join/cardinality, read-only·secret·registry 정책과 hash를 모두 검증한다. LLM은 자연어 해석과 승인 후보 선택만 담당하며 정확성 authority나 writer가 아니다.

`semantic_vocabulary`는 LLM에 필요한 최소 의미 후보만 제공한다. dataset은 `id/family/business labels`, field·metric·relation·grain·ordering·predicate·recipe·entity group은 `id/business labels`만 갖는다. 물리 컬럼, 타입, 역할, coercion, source/config/query ref, metric binding, SQL과 실행 payload는 포함하지 않는다. 선택된 ID는 내부 strict proposal에서만 쓰이고 작업자에게 입력하도록 요구하지 않는다.

같은 registry의 `metadata.authoring.semantic-templates.v1`은 LLM에 보내지 않는다. 이는 검토된 executable blueprint/catalog에서 결정적으로 투영된 compiler 전용 구조이며 template/blueprint/executable/projection SHA-256으로 봉인된다. `semantic_templates.planner_policy`의 `planner_profile`과 optional legacy hash도 LLM이나 Domain Policy `output_profile_json`이 변경할 수 없다.

실제 LLM 출력 envelope는 `metadata.authoring.proposal.v1`이다. `status=complete`이면 입력 원문의 `source_sha256`과 closed `draft`가 있고, `status=needs_clarification`이면 같은 source hash와 최대 3개의 확인 질문 및 `missing_fields`만 있다. 두 형태를 섞거나 clarification 응답에 draft/candidate/persist 결과를 넣으면 schema 단계에서 거부한다.

Compiler는 구조적 일관성과 실행 안전성을 보장하지만 작업자의 업무 의도를 대신 확정하지 않는다. 서로 다른 해석이 가능한 문장은 임의 선택하지 않고 clarification/missing-information으로 돌려보내며 이 경우 저장하지 않는다. 확인 질문은 “당일 생산과 생산 이력 중 어느 자료인가요?”처럼 쉬운 업무 선택지를 사용하며 등록 ID, canonical ID, JSON/DSL, 타입, 물리 컬럼 또는 schema 경로를 묻지 않는다. 검증에 성공한 결과는 도메인·테이블 카탈로그·메인필터 collection에 자연어 기반 항목 문서로 transaction 저장한다.

현재 live 검증 model policy는 정확히 `gemini-3.5-flash-lite`, temperature `0`, provider/model fallback `0`, repair LLM `0`이다. 모델 응답이 schema를 통과하지 못하면 같은 질문을 고쳐 재호출하지 않고 canonical validation error로 끝낸다.

첫 등록에는 실행 가능한 도메인 전체를 만들 만큼의 정보가 필요하지만, 그 정보를 정해진 항목 순서나 JSON/DSL 문법으로 쓸 필요는 없다. 제조 기본 검증은 `metadata/authoring/v6_inputs/domain_v6.txt`, `dataset_v6.txt`, `main_filter_v6.txt`의 자유형 자연어를 세 입력 노드에 그대로 넣는다. 문장 순서, 말투, 표기 차이는 LLM이 proposal로 정규화한다. 정보가 부족하면 Flow가 엄격한 포맷을 요구하는 대신 `status=needs_clarification`의 `missing_fields`와 짧은 확인 질문을 작업자가 이해할 수 있는 말로 반환한다. 이 응답에는 draft/candidate/persist 산출물이 없다.

다음 두 문장은 모두 허용되는 자유형 입력 예다.

```text
주문 데이터는 주문번호와 상품번호가 있고 상품 데이터와 상품번호로 연결해. 매출은 주문금액 합계를 쓰고 취소 주문은 빼야 해.
```

```text
우리가 보는 생산실적 표에는 작업일, 공정, 제품 속성, 생산수량이 있어요. 작업일 기준으로 공정별 생산량을 합치고 MODE/Mode 같은 표현은 같은 필터로 알아들었으면 합니다.
```

`source_grounding_mode=explicit_inventory`는 선택적 고신뢰 lane이다. 이 mode를 명시한 운영자는 exact identity/binding inventory로 zero-LLM compile을 시도할 수 있다. 검토된 `metadata.executable-blueprint.v1`과 별도 SHA-256 pin을 제공하는 lane은 기본 Domain annotation-only 계약에 executable 불변성 검증을 추가한다. 이는 감사·마이그레이션·규제 환경을 위한 선택 사항이며 일반 작업자의 자연어 입력 조건이 아니다. Blueprint/pin이 없다는 이유만으로 기본 자유형 lane이 `metadata_blueprint_required`로 실패해서는 안 된다.

어느 authoring lane을 사용해도 분석 runtime은 세 current metadata 문서를 검증·결합한 package에서 Typed Execution IR을 결정론적으로 만들고 실행한다. pandas 코드 생성 LLM과 repair LLM 호출 수는 항상 0이며, authoring LLM 출력이 runtime code로 직접 전달되지 않는다.

## 2. Authoring source 종류

| 종류 | 사용자가 설명할 내용 | 실행 구조 authority |
| --- | --- | --- |
| Domain/Semantic | 도메인의 업무 이름과 설명, 승인된 용어를 작업자가 쓰는 맥락 | LLM은 표시명·설명 annotation only; 실행 semantics는 Source Registry v3 `semantic_templates`가 deterministic expansion |
| Dataset Catalog | 자료의 업무 이름과 용도, 포함된 업무 항목, 날짜 기준과 기본 표시 항목처럼 작업자가 아는 사실 | 내부 compact Dataset IR + v3 dataset descriptor/Source binding expansion + exact active package `datasets` patch |
| Main Filter | 날짜·제품·공정 등 조회 기준의 업무 의미와 사용자가 실제로 쓰는 표현 | 내부 `target_type` 필수 typed IR + 승인 vocabulary membership + alias-card expansion |
| Domain Policy | intent/answer prompt extension, registered function descriptor, output profile | 별도 Domain Policy Authoring Flow의 explicit 관리자 node input; Prompt/LLM 0회, sealed planner policy 변경 금지 |

연결 비밀번호나 token은 어떤 TXT에도 쓰지 않는다. 일반 작업자는 `config_ref`/`query_ref` 문법을 알 필요가 없다. Oracle/Datalake 운영 조회가 필요한 항목에는 `db_key는 PNT_RPT야` 같은 설명과 `query_template:` 아래의 여러 줄 SQL, `{DATE}`·`{LOT_ID}` 같은 변수를 함께 적을 수 있다. Flow는 SQL 본문을 LLM에 보내지 않고 원본 TXT에서 직접 추출해 read-only 여부와 필수 변수를 검증한다.

네 authoring 입력 화면은 분리되어 있지만 저장 결과는 하나의 versioned Domain Package다. Domain/Dataset/Main Filter는 자연어 TXT UX를 유지하고, Domain Policy만 별도 explicit 관리자 입력을 사용한다. Dataset Catalog와 Main Filter 입력은 active package의 해당 section만 삭제 없이 upsert하고, 다른 dataset·metric·relation·prompt·output 설정을 보존한 상태에서 전체 package를 다시 컴파일한다. 운영자가 일부 입력을 등록했는데 Data Analysis Flow가 읽지 못하는 별도 legacy pointer만 갱신하는 방식은 v6 기본 경로에서 사용하지 않는다.

최초 Domain bootstrap의 Flow canvas에는 Domain·Dataset·Main Filter용 **공통 Prompt Template node와 특화 Prompt Template node가 각각 하나씩** 있다. 각 pair는 한 템플릿의 section으로 합치지 않으며 각각 별도 Runtime Context Builder, Prompt Bundle Composer, Conditional LLM Invoker와 연결된다. 모든 Template은 변수 없이 렌더링되고 자연어 source context는 Composer의 `runtime_context`에 정확히 한 번 연결된다. 세 Invoker는 같은 승인 Language Model node를 재사용할 수 있지만 proposal과 source hash는 분기별로 봉인한다.

Runtime Intent/Answer와 Authoring은 모두 공통·특화 Prompt Template을 별도 필수 pair로 유지한다. 특화 authoring 지시는 공통 Prompt나 custom component가 아니라 각 특화 Prompt Template 본문에 직접 작성하며 사용자 TXT나 metadata로 동적 교체하지 않는다. Domain Policy와 `source_grounding_mode=explicit_inventory`의 완전한 inventory compile은 Prompt Template, Composer, `prompt.envelope.v1`, provider 호출이 모두 0회다.

## 3. Domain 입력 예시

아래 문장은 자연어 UX 예시이며 복사해야 하는 등록 문법이 아니다. Domain LLM은 이 문장에서 표시명·설명 annotation만 만들고, 실행 규칙은 승인 Source Registry v3 template와 일치하는 경우에만 compiler가 확장한다. 자연어만으로 새로운 metric/relation/recipe/planner 정책을 발명하거나 기존 template를 수정하지 않는다. 실행 규칙을 변경하려면 운영자가 검토된 executable/template projection과 v3 registry hash를 먼저 갱신한 뒤 새 자연어 입력으로 prepare하고 diff를 승인한다.

### BOH 아침재공

```text
BOH 재공과 아침재공 기준일 규칙을 등록해줘.
아침재공, BOH 재공, BOH, 07시 기준 재공은 하루 시작 시점의 재공이야.
사용자가 말한 기준일을 D라고 할 때 실제 조회는 wip 이력 데이터의 D-1 DATE를 사용해.
결과 화면에는 사용자가 요청한 D를 기준일로 표시해.
현재재공, 지금재공은 이 규칙이 아니라 wip_today를 사용해.
재공 수량은 WIP 컬럼 합계야.
```

Compiler가 확인할 항목:

- semantic metric ID
- requested/query date transform
- history/current dataset family
- DATE parameter format/timezone
- metric source binding
- excluded conflicting time scope

Python normalizer가 `"아침재공"` 문자열을 검사해 dataset을 바꾸지 않는다.

### 제품 grain

```text
표준 제품 grain은 TECH, DEN, MODE, PKG_TYPE1, PKG_TYPE2, LEAD, MCP_NO 조합이야.
production, wip, target, equipment 계열을 제품별로 결합할 때 이 grain을 사용해.
DEVICE를 명시적으로 요청한 질문에서만 DEVICE grain을 사용해.
빈 제품 속성의 match 정책은 blank끼리 같음으로 처리해.
```

### Presence recipe

```text
A metric은 양수인데 B metric이 없거나 0인 대상을 찾는 분석 recipe를 등록해줘.
두 source를 같은 요청 grain으로 각각 집계한 뒤 A가 양수인 행만 남겨.
B가 양수인 key는 존재하는 것으로 보고 A 결과에서 anti-join으로 제외해.
왼쪽 A 대상은 보존하고 B 표시값은 0으로 보여줘.
```

질문 예시 문자열을 저장할 수 있지만 runtime Python branch로 변환하지 않는다.

## 4. Dataset Catalog 입력 예시

### Production History

```text
이력 생산실적 dataset은 production이야.
source는 Oracle이고 우리가 부르는 DB key는 PNT_RPT야. 조회 내용은 생산 이력 표야.
DATE는 필수 LocalDate parameter이고 사용자는 YYYYMMDD로 입력해.
query에서는 DATE를 WORK_DATE에 적용해.
조회는 read-only, timeout 30초, 최대 5만 행이야.

표준 컬럼과 실제 컬럼은 다음과 같아.
DATE -> WORK_DATE
TECH -> TECH
MODE -> MODE
DEN -> DENSITY
PKG_TYPE1 -> PKG1
PKG_TYPE2 -> PKG2
LEAD -> LEAD
MCP_NO -> MCP_NO
OPER_NAME -> OPER_NAME
OPER_SEQ -> OPER_SEQ
PRODUCTION_QTY -> PRODUCTION

PRODUCTION_QTY는 count 단위의 additive metric이고 sum을 허용해.
```

Compiler는 query가 `WORK_DATE`를 사용하는지와 field binding이 일치하는지 검사한다. `WORK_DT`/`WORK_DATE` 불일치를 warning으로만 넘기지 않는다.

### Goodocs 계획

```text
생산계획 dataset은 target이야.
Goodocs 문서 source이고 config_ref는 goodocs:target, query_ref는 query:target이야.
사용자 DATE는 YYYYMMDD지만 source DATE는 YYYY-MM-DD야.
timezone은 Asia/Seoul이야.
조회는 read-only, timeout 30초, 최대 5만 행이야.

표준 컬럼과 실제 컬럼은 다음과 같아.
DATE -> DATE
TECH -> TECH
MODE -> Mode
DEN -> DEN
PKG_TYPE1 -> PKG1
PKG_TYPE2 -> PKG2
LEAD -> LEAD
MCP_NO -> MCP NO
INPUT_PLAN_QTY -> INPUT 계획
OUT_PLAN_QTY -> OUT 계획

INPUT_PLAN_QTY와 OUT_PLAN_QTY는 numeric coercion 후 sum을 허용해.
source 값이 K 단위라면 multiplier 1000을 적용해.
```

Retrieval adapter는 source의 physical row와 schema를 반환한다. **Source Contract Merger**가 dataset contract에 따라 `Mode → MODE`를 정확히 한 번 수행한다. Executor는 이미 canonicalized된 table만 받고 rename이나 alias fallback을 하지 않는다. Plan과 result는 `MODE`만 사용한다.

### HOLD History

```text
HOLD 이력 dataset은 hold_history야.
Oracle read-only source이고 LOT_ID가 필수 IN parameter야.
LOT_ID 목록은 200개 단위로 조회하되 일부만 조용히 자르지 마.
HOLD_TM -> HOLD_EVENT_AT으로 binding해.
HOLD_EVENT_AT은 Asia/Seoul local timestamp이고 HOLD 발생 시각이야.
LOT_ID, HOLD_EVENT_AT, HOLD_CD, HOLD_DESC를 detail로 제공해.
```

현재 HOLD LOT 중 가장 오래된 LOT은 `lot_status.OPER_IN_TM`이나 `FAC_IN_TIME`으로 추정하지 않는다. 이전 current HOLD 결과의 LOT_ID 전체를 `hold_history`에 조회하고, LOT별 최신 `HOLD_EVENT_AT`을 current hold start로 derive한 뒤 가장 이른 LOT을 선택한다. current LOT 중 history가 누락되면 fail-closed다.

## 5. Main Filter 입력 예시

```text
표준 필터 MODE를 등록해줘.
사용자 표현은 MODE, Mode, mode야.
value type은 string, 기본 operator는 eq야.
alias는 단어 경계에서만 인식하고 겹치면 가장 긴 표현을 우선해.
dataset별 실제 컬럼은 이 항목에 넣지 말고 각 Dataset Catalog의 field binding을 사용해.
```

Main Filter의 `column_candidates`를 dataset mapping fallback으로 사용하지 않는다.

Compiler가 생성하는 typed contract의 핵심은 다음과 같다.

- `filter_id`, canonical `target_field`, `value_type`
- `allowed_operators`, `default_operator`
- locale과 priority가 있는 alias 목록
- `unicode_nfkc → trim → collapse_space → latin_casefold` normalization
- `bounded_longest` match와 `fail_ambiguous` conflict 정책

`bounded_longest`는 alias 앞뒤가 문자열 끝 또는 공백·문장부호 경계인 경우에만 match한다. token 내부 substring은 match하지 않는다. 겹치는 후보는 가장 넓은 span, 더 긴 normalized alias, 높은 priority 순으로 고르고, 그래도 서로 다른 identity가 남으면 저장과 실행을 모두 차단한다.

### 공정 그룹 입력 예시

```text
W/B 공정 그룹을 등록해줘.
사용자 표현은 W/B, WB 공정이야.
표준 대상 컬럼은 OPER_NAME이야.
구성원은 W/B1, W/B2, W/B3, W/B4, W/B5, W/B6이고 각 값은 exact match해야 해.
목록에 없는 값을 비슷한 문자열로 확장하지 마.
```

Compiled process-group contract는 `group_id`, `target_field=OPER_NAME`, bounded alias, exact `members`, `expansion=closed_set`을 가진다. 단일 공정 요청과 공정 그룹을 동시에 추정하지 않는다. 대상 dataset에 canonical `OPER_NAME` binding이 없으면 compile 또는 plan 단계에서 실패한다.

### 공정 순서 입력 예시

```text
공정 범위 질문에 사용할 표준 공정 순서를 등록해줘.
각 공정의 OPER_NAME, unique numeric OPER_SEQ, 별칭을 순서대로 제공할게.
D/S1에서 D/A4, D/A1에서 W/B6 같은 물결표 범위는 양 끝을 포함해.
Dataset Catalog에는 OPER_NAME과 OPER_SEQ physical binding이 모두 있어야 해.
```

Compiler는 전체 process-order revision을 pin하고 endpoint를 numeric sequence로 확장한다. 문자열 정렬, 질문별 hardcode, source에서 우연히 관찰된 행 순서로 범위를 만들지 않는다.

### 제품 그룹 입력 예시

```text
Mobile 제품 그룹을 등록해줘.
사용자 표현은 Mobile, 모바일이야.
표준 product grain을 사용해.
MODE가 LP로 시작하고 PKG_TYPE1이 LFBGA, TFBGA, UFBGA, VFBGA, WFBGA 중 하나이며 MCP_NO가 비어 있는 제품이라는 canonical predicate로 정의해.
POP 제품 그룹은 같은 MODE/PKG_TYPE1 조건에서 MCP_NO가 비어 있지 않은 제품으로 정의해.
eq, in, starts_with, null_or_blank, is_not_blank 외의 연산자는 허용하지 마.
```

Compiled product-group contract는 canonical field만 쓰는 typed predicate와 `grain_id`를 가진다. physical column이나 자유 expression을 넣지 않는다. 후속 질문에서 Mobile을 POP으로 교체하면 기존 Mobile predicate를 제거한 뒤 POP predicate를 추가한다.

## 6. Domain Policy 관리자 입력

Domain Policy Authoring Flow는 자연어를 LLM으로 변환하는 화면이 아니다. 관리자 ACL이 있는 사용자가 다음 closed JSON/텍스트 입력을 명시적으로 제출하고 deterministic validator가 검증한다.

| 입력 | 허용 범위 | 금지 |
| --- | --- | --- |
| `intent_prompt_extension` | Runtime specialized Intent Prompt의 domain terminology·해석 우선순위 | 공통 안전/출력 계약 변경, 질문별 답 고정 |
| `answer_prompt_extension` | Runtime specialized Answer Prompt의 domain 표현·용어 정책 | fact 없는 주장, API/result 변형 |
| `specialized_functions_json` | 사전 등록된 function descriptor와 exact registry/schema/resource pin | Python source/module/callable/query/endpoint/secret |
| `output_profile_json` | label, unit, currency, date/null 표시 규칙 | canonical API field/value/result 변경 |

이 Flow에는 자연어 source 입력, Prompt Template, Runtime Context Builder, Prompt Bundle Composer, Language Model 또는 `prompt.envelope.v1` 생성 edge가 없다. prepare와 execute 모두 provider call counter가 0이어야 한다.

`specialized_functions_json`의 각 card는 최소한 `function_id`, `version`, `implementation_sha256`, `registry_entry_sha256`, `input_schema_ref/sha256`, `output_schema_ref/sha256`, selection evidence/ambiguity policy, required field/role, argument binding, output contract, timeout/row limit과 network/filesystem/subprocess deny policy를 가진다. 저장 전에 build-time standalone registry의 exact entry와 모두 일치해야 하며, 일치하지 않으면 candidate를 만들지 않는다.

활성화된 descriptor의 실제 실행 chain은 다음과 같다.

```text
Domain Policy 관리자 입력
→ function card closed validation
→ build-time registry exact attestation
→ active Domain Package
→ bounded Candidate Selector
→ Intent operation_refs의 candidate ID
→ exact pin의 registered_call Typed IR
→ Registered Function Gateway
→ output schema·lineage validation
```

이 chain의 consumer와 positive/negative E2E가 존재하지 않으면 descriptor를 실행 가능 기능처럼 UI에 노출하거나 active package에 저장하지 않는다. Runtime은 metadata의 code/module path를 import하지 않고 build-time allowlist 구현만 호출한다. dynamic import, `eval`/`exec`, arbitrary network/file/subprocess와 미등록 함수 fallback은 금지한다.

## 7. 저장 결과의 세 층

### Raw source

- 원문 전체
- source file/block
- content hash
- 작성/수정 시각
- 접근 권한

### Closed authoring draft와 선택적 trusted executable blueprint

기본 자유형 lane은 LLM이 반환한 작업별 annotation/compact IR을 저장 후보로 직접 사용하지 않는다. Compiler가 Source Registry v3의 hash-pinned `semantic_templates`, dataset descriptor, Source binding과 승인 alias target으로 이를 결정론적으로 확장·병합하고, 완성된 closed draft가 전체 검증을 통과한 경우에만 저장 후보가 된다.

- `contract_version=metadata.authoring.draft.v1`
- 자연어 provenance와 prompt/model/hash
- dataset/field/metric/relation/grain/recipe/filter의 schema-closed projection
- schema·semantic·dependency·security compile 결과

선택적 `source_grounding_mode=explicit_inventory`의 Blueprint lane은 아래 값을 추가로 봉인한다.

- `contract_version=metadata.executable-blueprint.v1`
- `domain_id`, `environment`, `source_manifest_sha256`
- 모든 실행 section을 포함한 `executable`
- reviewed `default_annotations`
- `executable_sha256`, `blueprint_sha256`
- Langflow 관리자 config/approved registry에 별도로 저장한 external Blueprint pin

Blueprint lane에서는 Blueprint JSON과 external pin을 같은 public API payload에서 받지 않는다. Self-hash만 맞는 재계산 변조도 external pin mismatch로 거부한다. 이 보안 규칙은 optional lane에만 적용되며 기본 자유형 lane이 Blueprint를 요구한다는 뜻이 아니다.

### Compiled runtime record

- versioned identity/revision
- typed contract
- dependency `namespace/kind/key/revision/contract_sha256`
- compiler/prompt/model hash
- schema, semantic lint, dependency-closure validation block와 ruleset/schema hash
- raw `source_id`

Runtime candidate prompt에는 raw source 전체를 넣지 않는다.

## 8. Save와 validate-only

기본은 `mode=save`다. `mode=validate_only` 또는 `dry_run=true`는 같은 item→catalog compile 검증을 수행하지만 MongoDB에는 쓰지 않는다.

기본 full-domain save 순서는 다음과 같다.

1. Domain·Dataset·Main Filter 자유형 원문과 세 원문의 결정론적 합성 hash를 immutable source evidence로 고정한다.
2. 원문별 공통·특화 Prompt Template pair와 Composer의 단일 bounded source context, 동일 SHA-256의 승인 semantic vocabulary로 Gemini를 각각 최대 한 번, 총 3회 호출한다.
3. 세 LLM 응답을 목적별 closed proposal schema로 decode하고 source hash를 검증한다. Domain은 `display_name`/`description` 외 key를 거부하고, Dataset은 compact Dataset IR, Main Filter는 `target_type`·`target_id`·`expressions` typed IR만 허용한다. 누락/모호한 입력은 repair 호출 없이 `status=needs_clarification`, 충돌·schema 오류는 canonical validation error로 반환한다.
4. Source Registry v3 root와 `semantic_templates_sha256`, blueprint/executable/projection hash를 검증한다. `semantic_templates` 본문은 LLM payload에 포함하지 않는다.
5. Domain annotation에 registry의 locale/timezone과 metric/relation/grain/ordering/predicate/recipe/entity-group/alias template를 결정론적으로 붙인다. `semantic_templates.planner_policy`도 그대로 봉인하며 LLM 또는 Domain Policy 입력의 변경을 거부한다.
6. Dataset 분기는 `metadata.bootstrap.dataset-ir.v1` compact schema와 승인 vocabulary membership을 검사한다. `dataset_cards[]/fields[]`는 LLM 내부 출력이며 일반 작업자에게 그 형식이나 컬럼 타입을 요구하지 않는다.
7. Dataset expander는 중복 dataset ID card를 거부한다. 같은 dataset 안의 동일 canonical field descriptor가 반복되면 의미와 선택 속성이 동등한 경우 하나로 merge하고 alias를 dedupe하지만 단위·연산자·정책·binding이 충돌하면 거부한다. 이후 각 field를 동일 dataset의 승인 Source Registry v3 descriptor와 1:1로 대조하고, 승인 family·physical column·semantic type·roles를 사용해 정렬된 full `datasets` section으로 확장한다.
8. Main Filter expander는 각 항목의 `target_type`과 `target_id` 조합을 승인 vocabulary에서 정확히 확인하고 source expression만 canonical alias card로 확장한다. Type 없는 동일 ID 추측과 physical-column fallback은 허용하지 않는다.
9. Domain → Dataset → Main Filter 순서로 확장된 소유 section을 충돌 없이 merge한다.
10. 최초 bootstrap에서는 확장된 dataset ID 집합과 운영자 승인 Source 레지스트리 집합이 정확히 같은지 검사한다. 누락·미승인 dataset이 하나라도 있으면 candidate를 만들지 않는다.
11. Exact coverage를 통과한 dataset에만 registry의 `source_type`, `source_adapter`, `config_ref`, `query_ref`를 결정론적으로 overlay하고 registry hash를 봉인한다. LLM이 같은 필드를 출력해도 실행 authority로 사용하지 않는다.
12. 완성 draft에 full-draft JSON Schema, semantic lint, dependency closure, field/source binding, join/cardinality, read-only·secret·registered-function security compiler를 실행한다.
13. valid draft만 typed diff와 저장용 item set을 만든다. LLM이 직접 MongoDB metadata를 쓰지 않는다.

`source_grounding_mode=explicit_inventory`의 optional zero-LLM lane은 완전한 binding proof를 먼저 검증한다. Blueprint lane은 기본과 같은 Domain annotation output을 사용하되 provider 호출 전에 external pin, Blueprint self-hash, executable hash와 source identity를 추가 검증한다. Pin이 없거나 틀리면 provider 호출 0으로 fail-closed한다. 주문·매출 fixture와 `build_executable_blueprint.py --check`는 이 고신뢰 lane의 재현성 검사다.

Dry-run 결과:

- 생성/변경 후보
- 기존 current package와 typed diff
- missing information
- assumptions
- schema errors
- semantic lint errors
- dependency changes
- 영향받는 validation cases

Compiler는 저장 전에 전체 runtime catalog를 검증한다. 응답의 `candidate_id`와 hash는 실행 중 결과 추적용이며 MongoDB metadata 문서에 기록하지 않고 별도 pending collection도 만들지 않는다. `needs_clarification`, schema/dependency/security 오류는 MongoDB write 0건으로 끝난다.

## 9. 3컬렉션 atomic save

1. Domain Package를 도메인 규칙, 데이터셋, alias 등 실제 등록 항목 단위로 나눈다.
2. 각 문서는 `_id`, `section`, `key`, `natural_text`, `payload`, `updated_at`만 가진다.
3. `domain_id`, environment, revision, contract, release, manifest, hash는 MongoDB에 저장하지 않는다.
4. MongoDB transaction에서 세 collection의 current item set을 `replace_one(upsert=true)`로 교체한다.
5. 같은 transaction 안에서 모든 항목을 다시 읽고 Domain Package를 메모리에서 컴파일해 원래 runtime catalog와 동치인지 확인한다.
6. 하나라도 다르면 transaction 전체를 중단한다. `01 사용 가능 메타데이터 불러오기`는 MongoDB URI·database·세 collection 이름·timeout을 입력받고 같은 item compile을 수행한다. domain/environment/source mode는 UI에 없다.

이 단순 current 구조에는 자동 승인 대기열, active pointer, revision archive나 자동 rollback이 없다. 이력이 필요한 조직은 MongoDB change stream/backup 또는 별도 감사 서비스를 사용한다. 세부 계약은 [V6_THREE_COLLECTION_METADATA.md](V6_THREE_COLLECTION_METADATA.md)를 따른다.

## 10. 수정 방식

| 요청 | 동작 |
| --- | --- |
| 신규 항목 등록 | `collection-role:section:key` ID로 항목 하나를 upsert |
| 같은 항목 수정 | 해당 항목의 `natural_text`와 검증된 `payload`를 새 입력으로 교체 |
| 전체 도메인 재등록 | 컴파일된 전체 항목 집합으로 세 current collection을 transaction 교체 |
| 저장하지 않음 | `validate_only` 결과만 반환하고 MongoDB write 0건 |
| 모호하거나 잘못된 입력 | 저장 차단 후 확인 질문 또는 오류 반환 |

별도 revision 문서, active pointer, release archive는 만들지 않는다. 변경 이력이 필요하면 MongoDB change stream·backup 또는 별도 감사 시스템에서 관리한다.

## 11. Secret, registry, 실행 경계

- token/password/API key는 raw TXT에도 입력하지 않는 것을 원칙으로 한다.
- authoring Flow의 LLM용 `approved_source_registry.json`에는 secret, endpoint, SQL/query 본문을 저장하지 않는다. Oracle·SQL·Datalake query는 작업자 원본에서 결정론적으로 추출해 테이블 카탈로그 dataset 항목의 `payload.source_config`에만 저장한다.
- Data Analysis Flow는 `11 검증용 더미 데이터 조회`, `12 Oracle 데이터 조회`, `13 H-API 데이터 조회`, `14 Datalake 데이터 조회`, `15 Goodocs 데이터 조회`를 분리한다. 각 node는 연결된 자기 source payload만 검증하며 exported Flow 자체가 ref를 SQL이나 credential로 해석하지 않는다. 운영자가 source node에서 조절하는 scalar는 실제 source별 `조회 행 수 제한`뿐이다.
- 실제 운영 adapter의 credential과 ACL은 서버 측 배포 책임이다. Oracle·Datalake 노드는 저장된 `db_key`와 `query_template`을 읽고 node input/환경변수에서 연결 정보를 주입한 뒤 필수 변수를 치환해 실행한다.
- Dataset contract는 승인 ID와 authoring registry hash를 pin하며, 서버 측 adapter는 같은 ID의 revision/hash·parameter schema·ACL을 다시 확인해야 한다.
- Dataset policy와 registry 중 더 엄격한 read-only, timeout, max-row 한계를 적용한다. Node input은 이 한계를 더 줄일 수 있지만 늘리거나 write로 바꿀 수 없다.
- 임의 SQL, 임의 endpoint, dynamic collection 이름, mutation query는 받지 않는다.
- Adapter는 가능하면 upstream에 `max_rows+1`을 요청하고, 그렇지 않으면 streaming count가 한계를 넘는 즉시 중단한다. Row limit 초과를 조용히 truncate하지 않고 `source_row_limit_exceeded`, timeout은 `source_timeout`, 권한 실패는 `source_acl_denied`로 보고한다.
- Intent/Answer LLM 후보에는 SQL, endpoint headers, credential을 전달하지 않는다.
- Metadata, state, trace, result ref에도 secret을 복사하지 않는다.
- Public webhook/API와 일반 tweak allowlist는 `trusted_blueprint_json`, `trusted_blueprint_sha256`, Mongo URI, approval payload, Domain Policy 관리자 입력을 받을 수 없다.
- Blueprint와 pin은 Flow 관리자 ACL 또는 approved registry resolver만 설정한다. 일반 사용자가 Message나 API body에서 두 값을 함께 덮어쓸 수 있으면 external trust anchor가 아니므로 요청을 거부한다.

Dataset Catalog LLM은 SQL을 생성하거나 수정하지 않는다. 작업자가 제공한 query 원문은 deterministic compiler가 단일 read-only `SELECT/WITH`, placeholder 문법, typed required parameter의 일치를 검사한다. production secret/URI는 repository와 MongoDB에 두지 않으며, query가 필요한 Oracle·Datalake dataset에 query가 없으면 조회 단계에서 dependency error로 종료한다.

## 12. Migration

v5의 `domain_knowledge.txt`, `data_catalog.txt`, `main_variable.txt`를 우선 source로 사용한다. MongoDB에만 있는 record는 별도 migration candidate로 추출한다.

Migration 완료 판정:

- source block과 compiled record hash 연결
- temporal/mapping/metric/grain/recipe dependency valid
- invalid record quarantined
- 대표 질문 영향 report
- v5 collection write 0
- v6 loader round-trip 성공
