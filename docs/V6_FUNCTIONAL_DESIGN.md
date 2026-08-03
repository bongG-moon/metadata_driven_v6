# metadata_driven_v6 기능 설계서

- 작성일: 2026-07-31
- 설계 기준: v5 `bb6df1a` tracked source, 내용상 `f5a2a79`
- 런타임 기준: Langflow 1.9.2 / Langflow Base 0.9.2 / LFX 0.4.2 / Python 3.12
- 상태: 4개 MVP Flow 목표 계약 확정. Data Analysis 1개와 Chat-first metadata authoring 3개를 제공함

## 1. 설계 결론

v6는 의도 분석 LLM이 실행 계획 전체를 만들고, 두 번째 LLM이 pandas code를 만들고, 오류가 나면 다시 LLM으로 code를 고치는 구조를 사용하지 않는다.

Trusted core 정상 경로:

```text
질문
→ deterministic typed literal/evidence candidates
→ 관련 compiled metadata + immutable resolved candidate bundle
→ deterministic route eligibility
   ├─ 유일·완전한 selection 증명: deterministic intent, Intent LLM 0회
   └─ 의미 선택 필요: bounded candidate Intent LLM 1회
→ 동일한 closed analysis.intent.v1로 수렴
→ deterministic plan compiler
→ trusted retrieval
→ deterministic typed executor
→ deterministic result validator/facts
→ 선택적 answer LLM 1회
→ canonical response
```

정확성은 route와 semantic intent 이후의 공통 계약이 책임진다. Answer LLM을 끄면 정상 호출은 route에 따라 0회 또는 1회이고, 기본 balanced mode의 최대 정상 호출은 2회다. fast path는 질문별 keyword shortcut이 아니라 원문/state evidence와 immutable metadata/operator pin으로 selection의 유일성과 완전성을 증명할 때만 사용한다. fast path 선택 뒤 오류가 나면 Intent LLM, pandas 또는 exploration으로 자동 fallback하지 않는다.

계층은 다음처럼 분리한다.

1. trusted core: deterministic route eligibility, optional semantic Intent LLM, typed IR compiler/executor
2. structured flexibility: 같은 core에서 closed field role/operator/formula/recipe registry 확장
3. future privileged exploration: 별도 계약·store·외부 격리 실행. 초기 runtime에서는 disabled이며 trusted 다섯 Flow에 포함하지 않음

## 2. 왜 새로 만드는가

### 2.1 v5의 반복 회귀 패턴

이전 작업 이력에서 다음 순환이 반복됐다.

1. BOH 질문이 production만 선택하거나 WIP를 같은 날짜로 조회
2. temporal contract를 추가한 뒤 컬럼 mapping/pre-filter가 실패
3. canonical column을 맞추자 `MODE/Mode` duplicate output 충돌
4. 존재·부재 질문 실행을 고치자 다른 ordering/output contract가 실패
5. 후속 장비 enrich를 고치자 `DEN/DENSITY`, `PKG_TYPE1/PKG1` join이 변동
6. 공통 fallback을 제거·표준키 실행을 적용했으나 실제 환경에서 이상 동작
7. 마지막 두 기능 변경을 순서대로 revert

각 오류는 별개의 pandas 코드 실수처럼 보였지만 공통 원인은 다음이다.

- LLM이 semantic intent, dataset 선택, 날짜, physical column, pandas code, output schema를 동시에 소유
- normalizer가 LLM 결과를 사후 보정하며 5천 줄 이상으로 성장
- canonical/physical mapping이 여러 단계에 분산
- prompt rule과 deterministic executor 지원 operation이 불일치
- dummy validation이 정답 plan/code를 주입해 모델 계획 오류를 가림
- follow-up state가 exact executed contract가 아니라 요약/heuristic에 의존

### 2.2 현재 v5 기준선

| 항목 | 현재 상태 |
| --- | --- |
| Flow graph | 46 nodes / 71 edges |
| LLM | intent, pandas code, answer + 오류 시 repair |
| prompt 크기 | static 약 95KB |
| source mapping | canonical/physical 혼용 |
| presence | prompt 지시는 있으나 current deterministic executor 미지원 |
| state | compact summary/ref는 있으나 exact executed result contract 불완전 |
| validation | fixture 30/30, 과거 real LLM 34/36, multi-turn 부분 검증 |
| current content | presence/standardization 구현이 revert된 `f5a2a79` 상당 |

## 3. 범위

### 포함

- Data Analysis Flow 재구축
- typed semantic intent와 execution plan
- deterministic pandas-backed operator runtime
- Oracle, H-API, Datalake, Goodocs, Dummy adapter
- compact state와 multi-turn reuse
- result/source TTL reference
- deterministic/optional LLM answer
- Domain/Table Catalog/Main Filter natural-language saving flows
- versioned metadata schema와 migration
- single/date/multi-turn/model/live-source validation harness
- Flow builder/export/import-ready bundle
- unsupported request telemetry와 reviewed typed capability promotion loop

### 제외

- v5 Flow를 in-place 수정
- arbitrary Python/pandas code 실행을 일반 기능으로 제공
- privileged exploration endpoint/worker의 초기 runtime 활성화
- 모든 자연어·모든 모델의 무조건 지원
- source DB write/update
- v5 MongoDB collection in-place migration

## 4. 기능 요구사항

Data Analysis Flow는 `00`~`27` 실행 순서의 한국어 표시명을 사용한다. Domain/Dataset/Main Filter/Domain Policy 등록 Flow도 각자의 `00` 입력부터 최종 출력까지 번호를 붙이고, 같은 단계의 병렬 입력·Prompt·출력만 `A/B/C`로 구분한다. 도메인 초기 등록의 세 context/composer/invoker에는 도메인·초기 데이터셋·초기 주요 필터 분기명을 명시한다. `01 사용 가능 메타데이터 불러오기`는 MongoDB URI·database·도메인/데이터 카탈로그/메인필터 컬렉션명·timeout을 입력받아 해당 3컬렉션의 항목을 typed runtime catalog로 컴파일한다. domain/environment/source mode 선택은 UI에 없다. `02 요청 및 세션 상태 고정`은 기준시각·시간대 UI 없이 내부 현재 시각을 `Asia/Seoul`로 고정한다.

### FR-01. 자연어 질문 이해

- 상대/절대/ISO/slash/Korean/timestamp 날짜를 원문 evidence가 있는 `LocalDate` 또는 `Instant` 후보로 정규화
- 숫자, product token, ordered process range도 원문 span과 typed candidate ID로 생성
- 공정 그룹과 단일 공정 구분
- 제품 token과 표준 filter 구분
- metric, grain, ranking, comparison, presence, detail 요청 구분
- follow-up에서 상속·교체·삭제 조건 구분

Route Eligibility Gate가 위 selection을 정확히 하나로 증명하면 Deterministic Intent Builder가 Intent LLM 없이 `analysis.intent.v1`을 만든다. 증명할 수 없지만 bounded candidate 선택으로 해결 가능하면 LLM은 candidate ID만 선택하며 raw/resolved literal이나 실행 필드를 만들지 않는다. 두 생성기는 같은 closed intent schema, resolved-candidate bundle hash와 route proof hash를 사용하고 같은 compiler로 들어간다.

### FR-02. 결정론적 dataset 및 날짜 선택

- metric contract와 time contract로 dataset family/time scope 선택
- BOH requested date D → history source query date D-1
- 현재 WIP → current source
- source별 DATE format 변환
- 한 질문의 서로 다른 metric에 서로 다른 날짜·source 허용

### FR-03. Canonical field boundary

- Table Catalog의 dataset field binding을 단일 mapping 원천으로 사용
- source row를 executor 진입 전에 canonical key로 한 번 변환
- filter/group/join/output/follow-up에서 canonical key만 사용
- ambiguous 또는 missing mapping은 fail-closed

### FR-04. Typed analysis

지원 operation은 독립 기능 목록이 아니라 typed Execution IR에서 조합할 수 있는 폐쇄형 primitive다.

- filter: `eq/in/ne/not_in/gt/gte/lt/lte/between/contains/starts_with/ends_with/is_null/is_not_null/is_blank/is_not_blank/null_or_blank`, bounded `all/any`
- ordered range, product token match, row-match group
- projection과 canonical column ordering
- sum/mean/min/max/count/nunique/list aggregation
- global/per-group stable sort와 top/bottom N
- scalar extrema와 extrema row 선택(argmax/argmin)
- top+bottom segment 결합
- 등록된 두 컬럼 또는 group attribute 비교
- duplicate group 탐지와 identity/variant comparison
- inner/left/right/outer/semi/anti join, presence anti-join
- allowlisted formula AST 기반 safe derive
- detail/entity list, dedupe, history ordering
- hash-pinned standalone function registry의 `registered_call`
- previous result/source transform, previous result enrich, previous trace explain

어떤 LLM을 쓰더라도 field/operator/join/formula를 새로 만들 수 없다. 자연어 질문에서 선택할 수 있는 범위는 metadata compiler가 등록한 canonical field role(`filter/group/join/compare/project/sort/rank/output`), operator, join recipe, formula ID의 조합이다. 따라서 “MODE별 계획수량 상위 5개”, “제품별 실적 상·하위 3개”, “A 컬럼이 B 컬럼보다 큰 행”, “수량 최댓값인 모든 행”, “실적에는 있고 WIP에는 없는 제품”은 질문별 Python 없이 표현된다. 반대로 필요한 role/recipe/formula가 등록되지 않은 요청은 임의 코드로 우회하지 않고 clarification 또는 `unsupported_operation`으로 종료한다.

Ranking/extrema 의미는 다음처럼 고정한다.

- “최댓값/최솟값이 얼마인가”는 scalar aggregate다.
- “값이 가장 큰/작은 행·제품은 무엇인가”는 argmax/argmin rank다.
- “상위/하위 N”은 별도 언급이 없으면 stable exact-N이며, “동점 모두” 요청은 boundary tie 전체를 포함한다.
- global과 group별 ranking을 명시적으로 구분한다.
- exact-N의 동점 순서는 metadata에 등록된 stable tie-break field가 책임진다.
- 명시된 다중 정렬 key는 순서대로 rank하며 tie-break key와 분리한다. “각 컬럼별 최대 행”은 컬럼별 segment를 만들고 불명확한 합산 점수는 생성하지 않는다.
- 상위와 하위를 한 결과에 요청하면 `RESULT_GROUP=TOP|BOTTOM`, `RESULT_RANK`를 붙인 segment 결과를 만든다.

Join은 metadata에 등록된 recipe만 사용한다. recipe는 left/right key, join type, cardinality, null/duplicate/multi-match/empty-side/suffix/output 정책을 모두 pin한다. 선언되지 않은 many-to-many, 암묵적 suffix, 물리 컬럼 직접 join은 plan validation에서 거부한다.

Derived metric은 자유 수식 문자열이 아니라 typed formula AST를 사용한다. 허용 연산, 입력 type, 0 나눗셈 정책, rounding, AST depth/node limit을 compiler가 검증한다.

이전 결과 entity를 `LOT_ID` 같은 required parameter로 전달할 때 Plan Compiler는 declarative binding spec만 만들고, Plan Validator 이후 Parameter Binder가 authenticated owner/session ref에서 실제 값을 resolve·chunk해 immutable job bundle을 만든다. Executor는 이 binding을 수행하지 않는다.

### FR-05. Metric lineage와 결과 schema

- 결과 metric마다 source/dataset revision, source field, date, filter, aggregation, grain 증명
- 결과 column은 plan의 exact ordered list
- display label은 별도 mapping
- 동일 의미 metric duplicate 금지
- 다른 source 실패 시 metric 복사·0 대체 금지
- required source 실패는 전체 error, 사전 선언된 left-preserving optional enrichment만 typed-null partial

### FR-06. Multi-turn

- previous result transform
- previous source re-analysis
- follow-up requery
- previous result enrich
- previous source expand: 저장 snapshot coverage가 충분하면 source transform, 아니면 requery
- previous explain/trace-only: 결과를 재계산하지 않고 이전 scope·lineage·operator trace 설명
- independent new analysis reset
- result/source ref TTL, exact grain/entity/lineage와 source snapshot coverage 저장
- owner/session binding과 compare-and-swap state version
- source 재사용은 complete/non-truncated coverage가 필요한 범위를 포함할 때만 허용

### FR-07. 답변

- row count, extrema, applied scope, warnings, data mode를 deterministic facts로 생성
- 표는 response assembler가 생성
- optional Answer LLM은 문장별 `fact_ids`와 `scope_fact_ids`가 있는 structured narrative만 생성
- claim validator 불합격 시 deterministic answer 사용
- v5 Message 표시 옵션을 `display.options.v1`으로 유지: diagnostics, result table/preview limit, evidence, download, notice, applied criteria, next questions, intent, retrieval, execution plan
- v5 `show_pandas_code` 설정은 migration alias로 받아 typed Execution IR/operator trace 표시 여부로 변환하며 pandas code를 생성·노출하지 않음
- summary/result table/applied criteria/evidence/notices/downloads/next questions를 `answer.sections.v1`으로 생성
- API는 v5의 request/intent_plan/analysis/data/data_refs/state/trace와 `data.rows`/`data_refs[]` wire surface를 bounded projection으로 유지
- Langflow Message, structured API `Data(is_output=True)`, GaiA answer/metadata를 같은 immutable `response.v1`에서 fan-out
- `23 → 24·25·26`은 전송용 hash가 없는 일반 JSON을 전달하고, 24·25·26은 수신 hash나 전체 응답 schema를 재검증하지 않음. 결과 무결성 hash는 MongoDB result store 내부에서만 유지
- Message 표시 옵션은 canonical message, API data/result/state, GaiA answer/metadata를 바꾸지 않음
- result/source store → state CAS → runtime frame release → Message/API/GaiA fan-out 순서를 보장

v5 호환 surface는 다음과 같이 이전한다.

| v5 기능 | v6 소유자 | 호환 규칙 |
| --- | --- | --- |
| Answer Message Adapter 표시 토글 | `24 채팅 메시지 표시 설정` | 결과표·근거·적용 기준·Pandas 등가 코드·Typed Execution IR을 각각 선택하며 출력 payload hash 비교는 하지 않음 |
| `show_pandas_code` | `show_execution_plan` | import alias만 유지하고 code 대신 typed IR 표시 |
| Answer Response Builder | Response Assembler | canonical `answer.sections.v1` 생성 |
| API Response Builder | `25 API 표준 응답 출력` | response hash 검증 후 structured `response.v1`을 별도 output으로 반환 |
| MongoDB result/download store | Result/Source Ref Store | TTL, owner/session binding, CSV ref/URL 유지 |
| GaiA Output | `26 GaiA 형식 출력` | response hash 검증 후 answer, URLs, follow-up questions, trace/usage 유지 |
| multi-turn compact state | State Store/Loader | transform/requery/enrich/reset/explain과 CAS 유지 |

### FR-08. Metadata authoring

- 사용자는 정형 문법 없이 TXT에 비정형 자연어로 입력한다. JSON/DSL, canonical/등록 ID, relation endpoint/field-role 선언, 타입, 물리 컬럼과 source binding 문법은 일반 작업자에게 요구하지 않는다.
- Full-domain bootstrap은 작업자가 자유롭게 작성한 Domain·Dataset·Main Filter 원문을 작업별로 물리적으로 분리된 외부 공통·특화 Prompt Template pair에 전달한다. 특화 업무 규칙은 각 특화 Template 본문에 직접 작성하고 자연어 context는 Composer에 한 번만 연결한다. 각 branch는 동일 hash의 `semantic_vocabulary`를 사용하지만 출력은 Domain annotation only, compact Dataset IR, `target_type` 필수 Main Filter typed IR로 분리된다. 각 LLM은 최대 1회, 총 3회이며 작업자가 이 내부 계약을 작성하지 않는다.
- 승인 semantic vocabulary는 `metadata.authoring.source-registry.v3`가 투영한 dataset의 `id/family/business labels`와 field·metric·relation·grain·ordering·predicate·recipe·entity-group의 `id/business labels`만 제공한다. 물리 컬럼, 타입, 역할, coercion, source/config/query ref, metric binding, 실행 payload와 `semantic_templates`는 LLM에 전달하지 않는다.
- Domain 조각은 `metadata-annotation-proposal.schema.json`의 `display_name`과 `description`만 가진다. Compiler가 v3 registry의 hash-pinned `metadata.authoring.semantic-templates.v1`을 결합해 metric/relation/grain/ordering/predicate/recipe/entity-group/alias와 locale/timezone을 확장한다. Domain LLM이 실행 section을 반환하면 실패한다.
- Dataset 조각은 LLM 내부 출력용 `metadata.bootstrap.dataset-ir.v1`을 사용한다. 일반 작업자에게 compact IR 형식을 입력시키지 않는다. 결정론적 expander가 같은 dataset의 승인 Source Registry v3 descriptor와 1:1 대조한 뒤 승인된 family·physical column·semantic type·roles로 full dataset section을 확장한다.
- 최초 bootstrap의 Dataset 처리 순서는 `compact schema → vocabulary membership → duplicate reconciliation → deterministic expansion/type unification → 승인 Source 레지스트리 dataset exact coverage → source binding overlay → full-draft compiler`다. 중복 dataset ID card는 거부한다. 동일 dataset의 동등한 canonical field descriptor 반복은 merge/dedupe하고 충돌하는 descriptor는 거부한다. 모델이 출력한 source binding은 신뢰하지 않는다.
- Dataset은 exact active package의 dataset section만 자연어 기반 bounded LLM 1회로 patch
- Main Filter는 기본적으로 `metadata.bootstrap.main-filter-ir.v1`의 `target_type`·`target_id`·`expressions`만 LLM 최대 1회로 만들고 compiler가 alias card로 확장한다. `source_grounding_mode=explicit_inventory`가 완전한 alias→canonical binding을 증명한 경우에만 선택적으로 LLM 0회 결정론적 patch를 사용한다.
- optional 고신뢰 lane은 reviewed `metadata.executable-blueprint.v1`과 별도 SHA-256 pin으로 기본 Domain annotation 계약에 executable 불변성 증명을 추가할 수 있으나 일반 작업자 입력의 전제 조건이 아니다.
- Domain/Dataset/Main Filter의 LLM 경로는 작업별 공통·특화 Prompt Template node가 각각 하나씩이며 서로 다른 node/source/hash/edge를 유지한다. 모든 Template은 변수 없이 렌더링하고 사용자 입력이나 metadata가 특화 본문을 동적으로 바꾸지 못한다.
- 별도 Domain Policy Authoring Flow는 노출하지 않는다. 등록 해석의 업무별 차이는 세 등록 Flow의 특화 Prompt Template에서 관리하며, 실행 함수 descriptor와 planner policy는 자연어 Chat 등록으로 변경할 수 없는 compiler 소유 경계로 유지한다.
- optional explicit-inventory Main Filter도 Prompt Template/Composer/envelope/LLM은 0회
- JSON Schema와 semantic·dependency·security lint가 실행 가능성을 검증한다. 누락·모호한 정보는 포맷 재작성 요구가 아니라 draft/candidate 없는 `status=needs_clarification`으로 반환하며, 질문은 내부 ID나 타입 대신 작업자가 고를 수 있는 쉬운 업무 label을 사용한다.
- dependency closure 후 전체 runtime catalog를 검증하고 MongoDB 저장용 항목 문서로 분할
- `validate_only`는 실제 current item을 읽고 write 0건으로 중복·compile 결과를 반환한다. `save`는 신규 typed identity만 추가하고 `replace`는 같은 exact `section+key`만 교체한다. 다른 key의 의미 중복은 typed reference 보호를 위해 canonical key를 안내하고 차단한다. 세 모드 모두 언급되지 않은 기존 항목을 보존한다.
- raw source/hash와 compiled runtime record 분리

### FR-09. Observability

- inline trace는 stage status/hash/code
- verbose trace는 TTL ref
- first-pass/retry/transport/semantic/execution/answer failure 분리
- plan fingerprint와 metadata snapshot 기록
- route/reason/eligibility proof hash와 actual LLM call counter 기록
- unsupported request는 raw row·secret·prompt 없이 normalized shape와 missing capability ID만 bounded 집계
- 반복 unsupported shape는 사람 review 후 metadata recipe/formula/operator와 regression case를 함께 승격

### FR-10. Future privileged exploration

초기 v6는 `exploration.request.v1`, `exploration.job.v1`, `exploration.response.v1`, `exploration_ref` namespace만 예약하고 runtime은 활성화하지 않는다. 향후 도입하더라도 thin Langflow submit/status/cancel façade와 외부 broker, per-job hypervisor/microVM급 worker를 사용하며 trusted core와 다른 store/ref/state/ACL/TTL을 가진다.

다음 연결은 금지한다.

- core의 자동 route 또는 오류 fallback
- core `source_ref`, 임의 upload, cross-result join을 exploration 입력으로 사용
- exploration 결과를 trusted `response.v1`, `result_ref`, `executed.result.v1`, `turn.state.v1`로 변환
- core Message/API/GaiA, Answer LLM, download, follow-up chaining으로 자동 전달

별도 threat model, adversarial suite와 운영 승인을 통과하기 전에는 endpoint/worker가 없거나 disabled여야 한다.

## 5. 주요 시나리오 설계

### 5.1 6/27 W/B 생산실적 + 아침재공

Semantic intent:

- metrics: production quantity, BOH WIP quantity
- dimension: operation
- filter: WB process group
- requested date: 2026-06-27

Compiler 결과:

- production history DATE=20260627
- WIP history DATE=20260626
- 각 source에 WB process 목록 적용
- 각각 operation별 sum
- operation outer join
- result columns: `OPER_NAME`, `PRODUCTION_QTY`, `WIP_BOH_QTY`

WIP source가 실패하면 결과를 만들지 않는다. 정상 0행이면 WIP zero policy를 적용할 수 있다.

### 5.2 INPUT 실적 있음 + D/A WIP 없음

Compiler가 presence recipe를 선택한다.

- left: `production_today`, INPUT filter, product grain, `INPUT_QTY`
- right: `wip_today`, D/A group filter, product grain, `DA_WIP_QTY`
- `left_positive_right_missing_or_zero`
- result columns: product grain + `INPUT_QTY`, `DA_WIP_QTY`

단순 left join 전체 결과는 validator가 거부한다.

### 5.3 계획 데이터 `MODE/Mode`

- source contract: canonical `MODE`, physical `Mode`
- Source Contract Merger가 source boundary에서 `Mode → MODE`
- executor와 result는 `MODE`만 사용
- raw source에 `MODE`와 `Mode`가 동시에 있으면 자동 선택하지 않고 mapping ambiguity 오류
- label 변경은 column 복사가 아니라 `display_labels.MODE`에 기록

### 5.4 DA 상위 제품 → 장비 enrich

Turn 1은 `executed_result_contract`에 product grain과 3행 result ref를 저장한다.

Turn 2:

- `previous_result_enrich`
- 이전 3행 left 보존
- equipment source는 같은 canonical product grain으로 집계
- `EQP_ID nunique`, `EQP_ID list_unique`
- 장비 없는 제품도 count 0/list empty
- suffix column 금지

### 5.5 Mobile → POP follow-up

- 날짜, PKG OUT 공정, product grain은 상속
- Mobile filter는 drop
- POP filter는 add
- 이전 Mobile 최종 row를 POP source로 사용하지 않음
- 저장 source가 complete/non-truncated snapshot이고 POP 범위를 포함할 때만 source transform, 그렇지 않으면 requery

## 6. Metadata saving flow

세 authoring Flow를 분리해 유지한다.

1. Domain/semantic authoring
2. Dataset catalog authoring
3. Main filter authoring
4. Domain Policy authoring

네 Flow는 같은 typed 검증과 `save|replace|validate_only` 저장 경계를 공유하지만 변경 가능한 metadata 구간은 다음처럼 분리한다.

```text
Free-form Raw Text Input
→ Immutable Source/Bounded Context Builder
   ├─ Domain bootstrap
   │  → 작업자가 작성한 Domain·Dataset·Main Filter 자유형 자연어 TXT
   │  → 세 branch 공통의 hash-pinned approved semantic vocabulary
   │  → 서로 분리된 Domain/Dataset/Main Filter 공통·특화 Prompt pair 3개
   │  → 각 Context Builder의 runtime_context를 해당 Composer에 정확히 1회 연결
   │  → Domain annotation only / compact Dataset IR / target_type 필수 Main Filter IR
   │  → 각 LLM 최대 1회 → branch별 closed decoder
   │  → Source Registry v3 semantic_templates + dataset descriptor deterministic expansion
   │  → Dataset vocabulary/duplicate reconciliation/type unification
   │  → 세 branch deterministic merge
   │  → 승인 Source Registry v3 dataset exact coverage → source binding overlay
   │  → full-draft schema/semantic/dependency/security compiler
   │  → optional explicit_inventory: zero-LLM / Blueprint: annotation + external pin
   ├─ Dataset
   │  → 최신 완전 3컬렉션 package load → Dataset Authoring 공통·특화 Prompt pair
   │  → LLM 1회 → compact Dataset IR decoder + v3 descriptor expander
   ├─ Main Filter
   │  → exact active package load
   │  → explicit_inventory complete proof: deterministic patch, LLM 0회
   │  → 기본 free-form filter-owned input: Main Filter Authoring 공통·특화 Prompt pair, LLM 최대 1회
   │  → target_type 필수 Main Filter IR decoder + alias expander
   └─ Domain Policy 전용 Flow
      → explicit admin node inputs
      → prompt node/Composer/envelope/LLM 0회
      → prompt extension/output profile closed validation
      → sealed semantic_templates.planner_policy 변경 거부
      → registered function descriptor와 build-time registry exact attestation
→ JSON Schema Validator
→ Semantic Linter
→ Dependency Resolver
→ Existing Record Diff
→ Impact Validation
→ Candidate Canonicalizer/Hasher
→ Pending Candidate Writer
```

LLM review나 repair 호출은 두지 않는다. Domain annotation 확장, Dataset/Main Filter IR 확장, full-draft/section ownership, schema, semantic, dependency, security, diff와 hash 판정은 deterministic component가 소유한다. Source Registry v3 template/provenance hash와 sealed planner policy, optional Blueprint pin과 annotation allowlist도 같은 component 경계에서 처리한다.

`specialized_functions`는 metadata-only 설명 필드가 아니다. Domain Policy 관리자 입력의 descriptor는 build-time standalone registry의 exact function/version/implementation/entry/I/O-schema hash와 일치해야 저장·활성화할 수 있다. Runtime에서는 검증된 card만 Candidate Selector에 들어가고, Intent는 candidate ID만 선택하며, Plan Compiler가 exact pin의 `registered_call` Typed IR을 만든다. Registered Function Gateway는 allowlisted 구현, typed argument binding, field/role, resource policy, output schema와 lineage를 검증해 실행한다. dynamic import, `eval`/`exec`, arbitrary network/file/subprocess와 미등록 fallback은 금지한다.

### 6.1 Compiled record와 typed authoring contract

모든 compiled record는 identity/revision 외에 다음 값을 가진다.

- `contract_sha256`
- dependency별 `namespace/kind/key/revision/contract_sha256`
- schema validation status와 schema hash
- semantic lint status와 ruleset version
- dependency-closure status와 bundle hash

Main Filter는 canonical target field, value type, allowed/default operator, locale/priority alias를 가진다. Alias match는 Unicode normalization 뒤 token 경계를 지키는 `bounded_longest`만 허용한다. 겹치는 후보는 span, alias 길이, priority 순으로 고르고 끝까지 충돌하면 `ambiguous_alias`로 실패한다.

Process group은 canonical `OPER_NAME`에 대한 exact closed member set이다. Product group은 canonical product field와 allowlisted typed operator로 만든 predicate와 grain을 가진다. Physical column, substring 확장, 자유 expression은 group/filter contract에 저장하지 않는다.

Canonicalization 책임자는 typed executor가 아니라 **Source Contract Merger**다. Retrieval adapter가 physical rows/schema를 반환하면 Merger가 pin된 dataset binding으로 physical→canonical 변환, coercion, collision 검사를 한 번 수행한다. Executor는 canonical table만 받는다.

### 6.2 Source registry와 안전 경계

Dataset은 자유 연결 정보 대신 다음 versioned reference를 revision/hash와 함께 pin한다. 이 ID는 작업자나 LLM이 작성하지 않고 별도 운영자 승인 Source 레지스트리가 dataset ID로 결정론적으로 주입한다.

- `config_ref` → 서버 측 운영 adapter registry: adapter, endpoint ref, secret node-input 이름, ACL, read-only action
- Oracle·SQL·Datalake → 테이블 카탈로그 `payload.source_config`: reviewed read-only `query_template`, `db_key`, `required_params`. credential/connection string은 노드 입력 또는 환경변수 경계에 남긴다. 다른 adapter는 필요하면 기존 `query_ref`를 사용할 수 있다.

저장소의 승인 Source 레지스트리에는 credential 값을 넣지 않는다. 범용 Flow는 `11 검증용 더미 데이터 조회`, `12 Oracle 데이터 조회`, `13 H-API 데이터 조회`, `14 Datalake 데이터 조회`, `15 Goodocs 데이터 조회`를 분리한다. 네 실제 source node는 v5 호환 운영 입력 또는 환경변수 fallback으로 직접 read-only 조회를 실행하고 결과를 `source.result.v1`로 변환한다. 운영자가 이미 조회된 행을 `EDIT SOURCE PAYLOAD`에 수동 입력하는 구조는 사용하지 않는다. credential/token 기본값은 export JSON에서 비워 두고 metadata/state/trace/result/LLM에 복사하지 않으며, 승인 metadata 밖의 write action은 허용하지 않는다.

### 6.3 Langflow 1.9.2 저장 프로토콜

현재 기본 등록 Flow는 `save`, `replace`, `validate_only` 세 모드를 제공한다. 세 모드 모두 자연어 TXT를 LLM으로 typed 등록 IR로 바꾼 뒤 동일한 schema·참조·중복 검증을 수행한다. 중복 판정은 `04 검증 및 저장` 내부의 결정론적 substage이므로 새 노드, 새 LLM 호출, 새 MongoDB 컬렉션이 필요 없다. `save`는 변경 충돌을 차단하고, `replace`는 동일 exact `section+key`를 명시적으로 교체하며, `validate_only`는 MongoDB를 읽되 저장하지 않는다.

- `validate_only`: 변환·컴파일·기존 항목 중복 검증 결과만 반환하고 MongoDB를 변경하지 않는다.
- `save`: 검증된 도메인, 테이블 카탈로그, 메인필터 항목 문서를 노드에 지정된 서로 다른 3개 컬렉션에 transaction으로 upsert한다. transaction 시작 뒤 current snapshot이 달라졌으면 동시 변경 충돌로 중단하며, 언급되지 않은 item은 삭제하지 않는다.

별도의 pending collection이나 active pointer는 사용하지 않는다. 각 문서는 `_id`, `section`, `key`, `natural_text`, `payload`, `updated_at`만 가진다. 분석 Flow의 selector-free loader는 세 컬렉션의 항목 전체를 결합한 뒤 Domain Package를 메모리에서 다시 컴파일한다. 필수 항목 누락, 중복 key, 지원하지 않는 section, typed payload 오류가 있으면 저장 결과를 사용하지 않는다.

조직 정책상 사전 승인이 필요하면 등록 Flow 바깥의 배포·승인 서비스가 `validate_only` 결과를 검토한 다음 별도의 인증된 `save` 실행을 호출할 수 있다. 이는 선택 가능한 운영 래퍼이며, 기본 Flow나 MongoDB 스키마에 pending/active 컬렉션을 추가하지 않는다.

## 7. Payload와 memory

주요 개선:

- pandas LLM source preview 제거
- raw source rows의 LLM 전달 0
- metadata top-N array 대신 dependency bundle
- source branch에 thin job만 전달
- state에서 full chat/rows 제거
- answer input은 facts와 최대 10행 preview
- source/result/verbose trace는 ref로 저장

목표 budget은 [PAYLOAD_STATE.md](../harness/contracts/PAYLOAD_STATE.md)를 따른다.

## 8. 검증 전략

### Layer A: compiler/operator

LLM 없이 metadata record와 intent fixture로 exact plan/result를 검증한다.

### Layer B: full deterministic

30 single + 6 date + MT-1~MT-5와 모든 `OP-*` 유연 조회 case를 imported endpoint의 실제 Route Gate부터 exact oracle로 실행한다. 모든 case에 expected route/reason과 exact LLM call count를 둔다.

### Layer C: model conformance

실제 metadata snapshot과 dummy retrieval을 사용해 primary + weaker/different model profile에서 3회 반복한다. 전체 corpus를 endpoint로 실행하되 `expected_route=intent_llm` case만 모델을 호출하고 exact semantic oracle을 검사한다. deterministic/unsupported case는 매 profile에서 provider 호출 0과 같은 route proof/plan/result를 확인한다. 같은 오답의 반복은 안정성 통과가 아니다.

### Layer D: live source

Oracle/H-API/Datalake/Goodocs/Dummy 5개 adapter contract/security fixture와 배포된 9개 dataset의 read-only query/schema/required-param를 확인한다.

### Layer E: Langflow

exact package tuple에서 정확히 4개 MVP Flow(Data Analysis, Domain Authoring, Dataset Authoring, Main Filter Authoring)의 parse/import를 수행한다. Data Analysis는 Chat/API/GaiA를, 세 authoring Flow는 Chat Input부터 Chat Output까지 direct save와 validate-only를 smoke한다. 기본 제조 등록은 v6 전용 `domain_v6.txt`, `dataset_v6.txt`, `main_filter_v6.txt`를 각각 해당 Flow에 입력하고 exact `gemini-3.5-flash-lite`, temperature 0, fallback/repair 0으로 실행한다.

Exploration Flow/endpoint/worker가 초기 bundle에 없고 Data Analysis에서 이를 호출하는 edge가 0인지도 확인한다.

## 9. 성공 기준

- 대표/날짜/multi-turn/typed flexibility deterministic 100%
- 모든 case의 expected route/reason/LLM call count exact 일치와 no-fallback gate 통과
- 두 모델 이상 각 3회의 `intent_llm` case exact oracle 일치, deterministic/unsupported case provider 호출 0, plan/result schema 안정
- 정상 pandas/code repair 호출 0
- unsupported operation 명시 실패
- source failure를 empty/zero로 숨긴 case 0
- output semantic duplicate 0
- prompt/state/trace byte budget 통과
- Runtime Intent/Answer와 Domain/Dataset/Main Filter는 물리적으로 분리된 공통·특화 Prompt pair를 사용하고 특화 규칙을 Template 본문에 직접 작성하며 runtime context를 Composer에 한 번만 연결
- Domain Policy와 optional explicit-inventory Main Filter의 prompt/envelope/provider 호출 0
- registered function descriptor→registry attestation→candidate→Intent→`registered_call`→Gateway→output schema/lineage positive/negative E2E 통과
- 4개 MVP Flow의 사용자 가시 Flow/node/input/output 이름·설명 한글화와 역할별 Sticky Note 정적·import 검증 통과
- exact 1.9.2 export/import parity 통과

## 10. 구현 원칙 요약

v6에서 LLM 성능 차이는 deterministic route로 증명하지 못한 질문의 “후보 선택”에만 영향을 줄 수 있다. source, 날짜, 컬럼, 계산, 결과 schema는 공통 deterministic contract가 고정한다. 약한 모델을 지원하기 위해 prompt에 질문별 예외를 늘리지 않고, route proof·작은 semantic schema·metadata candidate 품질을 개선한다. 반복 미지원 수요는 arbitrary pandas fallback이 아니라 reviewed typed capability로 승격한다.
