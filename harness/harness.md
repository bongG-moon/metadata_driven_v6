# metadata_driven_v6 Harness

이 문서는 v6를 구현·리뷰·검증할 때 유지해야 하는 행동 기준이다.

## 목표

- 모델이 달라도 같은 질문은 같은 dataset, 날짜, filter, operation, result schema로 실행한다.
- metadata 변경이 특정 질문에 대한 Python patch보다 먼저 작동한다.
- Flow node가 적고 payload가 작아도 source lineage와 follow-up 근거는 잃지 않는다.
- Langflow canvas에서 입력, semantic intent, plan compilation, retrieval, execution, result validation, answer 경계가 보인다.

## 권한 경계

| 주체 | 허용 결정 | 금지 결정 |
| --- | --- | --- |
| Request/Candidate Builder | 원문 근거의 typed literal/date/token/range 후보와 metadata alias 후보 | 원문에 없는 값·업무 의미 생성 |
| Route Eligibility Gate | trusted evidence와 resolved candidate bundle로 semantic selection이 유일·완전한지 증명하고 `deterministic|intent_llm|unsupported` route와 reason/proof hash 확정 | 질문 문자열 shortcut, 확률 threshold만으로 fast path 선택, route 선택 후 자동 fallback |
| Deterministic Intent Builder | route proof가 pin한 candidate ID로 closed `analysis.intent.v1` 생성 | candidate 추가·삭제, 의미 추측, 별도 plan/executor 생성 |
| Intent LLM | `intent_llm` route에서만 candidate ID 중 metric/dimension/filter/time, 분석 종류, follow-up 관계 선택 | raw/resolved literal, dataset, SQL, source config, physical column, pandas code |
| Runtime Common/Specialized Prompt Sources | Intent/Answer의 공통 Prompt와 domain 특화 Prompt를 별도 node/ID/source/hash/edge로 제공 | 두 runtime prompt를 한 Prompt Template에 합치기, custom source 안에 prompt 문구 복제 |
| Authoring Prompt Source | Domain/Dataset/Main Filter별 공통·특화 Prompt를 별도 node/source/hash/edge로 제공; 특화 업무 규칙은 Template 본문에 직접 작성 | 작업자에게 inventory/IR 문법 강제, Domain LLM에 실행 metadata 생성 허용, 특화 본문을 metadata나 사용자 입력으로 동적 교체, Domain Policy에서 prompt 또는 LLM 호출 |
| Prompt Bundle Composer | 공통 Message, 특화 Message, bounded runtime context를 named input으로 받아 authority/purpose/revision/hash/byte budget 검증 | 업무 지시 추가, payload 중복, prompt를 state/trace/result에 저장 |
| Conditional LLM Invoker | route와 narrative/authoring mode가 허용할 때만 검증된 prompt envelope로 provider 호출 | prompt 생성·수정, route 변경, 실패 후 다른 LLM 경로로 자동 fallback |
| Metadata compiler | Source Registry v3의 hash-pinned `semantic_templates`/descriptor로 branch IR을 확장하고 full draft의 schema·type·identity·dependency·security를 검증해 typed runtime package compile | LLM 오류 보정, 승인 template 밖 업무 규칙 추측, sealed planner policy 변경, invalid 후보 저장 |
| Plan compiler | dataset variant, DATE offset, declarative entity-binding spec, mapping, operator DAG, output lineage | state row/value resolve, 질문별 문자열 예외 |
| Parameter Binder | owner/session-bound state ref의 entity value resolve·type/dedupe/chunk와 immutable job bundle | plan 의미·selection rule 변경 |
| Retriever | trusted job 실행, status/row count/schema 반환 | metric 생성, 다른 source 값 대체 |
| Registered Function Registry/Gateway | build-time allowlist의 function ID/version/implementation hash/I/O schema를 검증하고 `registered_call`만 실행 | metadata code 실행, dynamic import/eval, hash가 다른 구현, 미등록 network/file/subprocess 사용 |
| Typed executor | filter/aggregate/join/presence/rank/derive/enrich와 검증된 `registered_call` DAG | 임의 import·network·free-form LLM code |
| Unsupported Telemetry | error code, normalized request shape, missing role/operator/formula와 metadata pin의 bounded count·trend 기록 | raw row, secret, 전체 prompt 저장, runtime에서 operator 자동 생성·승격 |
| Answer LLM | 검증된 fact의 자연어 표현 | 값 계산, 표 변경, 조건 추가 |
| Response assembler | canonical 표·적용 범위·오류·ref 구성 | LLM 문장을 근거로 result 변경 |
| Presentation adapter | `response.v1` schema를 검사하고 node input의 표시 profile로 Message section 선택·Markdown 렌더링 | 응답 hash를 전송 경계처럼 재검사, canonical result/API/state 수정 |
| API/GaiA terminal | 23번의 일반 JSON 응답을 그대로 받아 API Data와 GaiA answer/metadata 출력 | 노드 사이 해시 비교, full source row 재직렬화, Message를 구조화 data로 역파싱 |

## Non-negotiables

1. custom component는 standalone이다.
2. natural-language metadata authoring을 유지한다.
   - 기본 authoring 입력은 비전문 작업자가 평소 업무 용어로 작성한 비정형 자유문이다. JSON, DSL, canonical/등록 ID, relation/field-role 선언, 타입, 물리 컬럼과 source binding 문법을 요구하지 않는다.
   - 최초 bootstrap은 작업자가 자유롭게 작성한 Domain·Dataset·Main Filter 원문을 각각 받는다. 세 내부 LLM branch는 같은 hash로 봉인된 `semantic_vocabulary`의 `id/family/business labels`만 보고 원문 표현을 승인 후보에 매핑한다. Domain은 표시명/설명 annotation only, Dataset은 compact Dataset IR, Main Filter는 `target_type` 필수 typed alias IR을 반환한다. 작업자는 이 내부 형식을 알 필요가 없다.
   - 결정론적 compiler가 `metadata.authoring.source-registry.v3`의 LLM 비공개 `semantic_templates`와 dataset descriptor/Source binding으로 세 결과를 확장·재결합한다. 실행 metric/relation/grain/ordering/predicate/recipe/entity-group/alias와 planner policy는 LLM이 아니라 registry가 소유한다.
   - 정보가 부족하거나 한 표현이 여러 승인 후보에 대응하면 작업자가 고를 수 있는 쉬운 업무 표현으로 `status=needs_clarification`을 반환한다. 작업자용 질문에 내부 ID, JSON/DSL, 타입, 물리 컬럼이나 schema 경로를 노출하지 않는다.
3. MongoDB에는 작업자가 관리하는 자연어 기반 항목 문서만 저장한다. `01 사용 가능 메타데이터 불러오기`는 UI에 MongoDB URI·database·도메인 컬렉션·데이터 카탈로그 컬렉션·메인필터 컬렉션·timeout을 노출하고, 입력받은 서로 다른 3컬렉션의 항목을 실행 시점에 typed Domain Package로 컴파일한다. domain/environment/source mode 선택 input은 두지 않는다.
   - `02 요청 및 세션 상태 고정`은 기준시각·시간대 UI input을 두지 않는다. 실행 시각은 내부에서 생성하고 날짜 해석 시간대는 항상 `Asia/Seoul`이다. 검증용 고정 시각은 harness가 주입하는 test fixture이지 운영 Flow 설정이 아니다.
4. canonical↔physical mapping은 **Source Contract Merger**가 source boundary에서 정확히 한 번 수행한다.
5. metric output 하나마다 source/date/filter/aggregation lineage가 하나 존재한다.
6. presence 비교는 typed anti-join operator다.
7. follow-up은 저장된 `executed_result_contract`를 사용한다.
8. unsupported operation은 fail-closed다.
9. 질문별 prompt patch로 regression corpus를 맞추지 않는다.
10. empty result, missing source, failed source를 서로 다른 상태로 유지한다.
11. 결과 표의 컬럼은 result contract가 정하며 DataFrame의 모든 숫자 컬럼을 자동 표시하지 않는다.
12. full rows와 verbose trace는 ref로 전달하며 state와 LLM prompt에 복제하지 않는다.
13. registered field가 허용한 role 안에서는 filter/group/project/sort/rank/compare를 조합할 수 있어야 하며 질문별 고정 recipe만으로 유연성을 제한하지 않는다.
14. rank/join/derive는 tie, null ordering, cardinality, multi-match, zero-division 정책이 없으면 실행하지 않는다.
15. v5 Message 표시 toggle, structured API output, GaiA metadata, result/download ref와 multi-turn behavior는 compatibility gate 없이 삭제하지 않는다.
16. deterministic route와 Intent LLM route는 같은 `analysis.intent.v1`, Plan Compiler, typed executor와 result/output path를 사용한다.
17. fast path 선택 후 compile/validation/execution 오류는 Intent LLM, pandas 또는 다른 route로 자동 재시도하지 않는다.
18. future exploration 계약은 trusted core와 다른 namespace/store/ref/state를 사용하며 초기 runtime에서는 disabled다. 다섯 core Flow가 이를 자동 호출하거나 exploration 결과를 trusted `result_ref`/state/Answer LLM에 넣지 않는다.
19. Runtime Intent/Answer와 Domain/Dataset/Main Filter authoring은 Flow canvas에 **공통 Prompt Template node와 특화 Prompt Template node를 물리적으로 따로 둔다.** 특화 규칙은 각 특화 Template 본문에 직접 작성하며 모든 Prompt Template의 예상 변수는 빈 집합이다. Domain Policy는 Prompt/LLM 0회다. Main Filter의 zero-LLM compile은 `source_grounding_mode=explicit_inventory`에서 완전한 binding proof가 있을 때만 선택적으로 허용한다.
20. Runtime과 Authoring custom component는 `common_prompt_message`, `specialized_prompt_message`, `runtime_context`를 서로 다른 named input으로 받고 authority/hash/size/purpose 검증·조건부 호출·closed decoder만 수행한다. `runtime_context`는 Context Builder에서 Composer로 정확히 한 번 연결한다.
21. 모든 공통/특화 prompt는 서로 다른 node ID, prompt ID, revision, source SHA, rendered SHA와 edge를 유지한다. 공통은 `system`, 특화는 `domain_policy`, runtime context는 `untrusted_data` authority다. component가 임의 문구를 삽입하거나 내부 default로 대체하지 않는다.
22. 공통·특화 prompt source와 hash는 Flow build manifest가 독립적으로 pin한다. 어느 prompt를 수정해도 해당 revision/hash와 composition hash를 갱신하고 Flow bundle·manifest·검증 증적을 재생성해야 한다.
23. prompt text와 LLM raw output은 direct execution edge에서만 일시 사용하며 state, result, telemetry, verbose trace에 복제하지 않는다. hash, revision, byte length와 호출 결과 status만 남긴다.
24. `specialized_functions`는 설명용 metadata가 아니다. active Domain Package의 function card, build-time hash-pinned standalone registry, candidate selection, `registered_call` Typed IR, executor dispatch와 result/trace validation이 모두 연결된 경우에만 실행 가능하다. 어느 하나라도 없으면 authoring/compile 단계에서 fail-closed한다.
25. metadata에는 Python/source code를 저장하지 않는다. Function ID/version/hash/schema만 registry와 대조하며 runtime dynamic import, `eval`/`exec`, 임의 network/file/subprocess와 secret 접근은 금지한다.
26. 사용자에게 보이는 Flow·node·input·output의 이름과 설명은 한국어를 기본으로 하고 내부 ID/port/schema key는 유지한다. Data Analysis node는 `00`부터 `27`까지, Domain/Dataset/Main Filter/Domain Policy 등록 Flow는 각자의 `00` 입력부터 최종 출력까지 실행 순서가 보이는 번호형 한국어 표시명을 사용한다. 같은 단계의 병렬 입력·Prompt·출력만 `A/B/C` 접미사로 구분하며, 도메인 초기 등록의 반복 context/composer/invoker에는 담당 분기명을 반드시 포함한다. 각 input/output에는 기능, 필수 여부, 계약 type과 연결 대상을 알 수 있는 설명을 제공한다.
27. Flow 목적, 입력, prompt 정책, source, typed execution/registered function, 승인·저장과 Message/API/GaiA 출력을 설명하는 Sticky Note를 builder가 생성한다. Note는 실행 edge와 node count에 포함하지 않고 secret·query·raw row를 포함하지 않는다.
28. 기본 metadata authoring은 `자유형 TXT → 외부 공통·특화 Prompt pair → branch별 closed annotation/IR → Source Registry v3 결정론적 확장 → compile → 3컬렉션 transaction 저장`이다. 최초 Domain bootstrap은 Domain annotation, compact Dataset IR, `target_type` 필수 Main Filter IR을 각각 최대 1회씩, 총 3회 생성하고 한 번에 merge/compile한다. 후속 Dataset/Main Filter 수정은 최대 1회다. `source_grounding_mode=explicit_inventory`와 Blueprint/external pin은 선택적 고신뢰 lane이며 일반 작업자 입력의 전제 조건이 아니다.
29. Deterministic compiler는 schema·dependency·security 일관성을 보장하지만 자연어의 모호한 업무 의도를 임의 확정하지 않는다. 모호하면 assumptions/missing information과 짧은 업무 질문을 반환하고 저장하지 않는다. 성공한 결과만 도메인·테이블 카탈로그·메인필터 collection에 항목 단위로 저장한다.
30. MongoDB metadata 항목은 `_id`, `section`, `key`, `natural_text`, `payload`, `updated_at`만 가진다. release/manifest/package/domain/environment/revision/hash 필드는 저장하지 않으며 runtime contract/hash는 로드 후 메모리에서만 계산한다.
   - Oracle·SQL·Datalake dataset 항목의 `payload.source_config`에는 운영 조회에 필요한 `source_type`, `db_key`, 검증된 여러 줄 `query_template`, `required_params`를 저장할 수 있다. query의 내부 줄바꿈·주석·placeholder 철자는 보존한다.
   - `query_template`은 단일 read-only `SELECT/WITH`만 허용하며 `{NAME}` placeholder마다 typed `parameters.NAME.required=true`가 있어야 한다. 비밀번호·token·접속 문자열은 metadata에 저장하지 않는다.
   - Dataset LLM에는 query 본문을 전달하지 않는다. Prompt Composer가 provider projection에서 query body를 제거하고, 등록 compiler가 원본 TXT에서 별도로 추출·검증·저장한다.
30. 최초 Domain bootstrap의 Prompt 경계는 다음과 같이 고정한다.
   - 작업자는 Domain·Dataset·Main Filter 한글 입력 노드에 자유형 자연어 TXT만 넣는다. JSON/DSL, compact IR, canonical ID 목록, 컬럼 타입 표, `config_ref`/`query_ref`는 일반 작업자 입력 계약이 아니다.
   - Domain·Dataset·Main Filter에는 **공통 Prompt Template node와 특화 Prompt Template node가 각각 하나씩** 있다. 모든 pair는 서로 다른 node/source/hash/edge로 유지하고 한 Prompt Template 안의 section으로 합치지 않는다. 각 분기는 별도의 Context Builder·Composer·Conditional Invoker를 가지며 하나의 승인된 Language Model node를 공유할 수 있다.
   - 세 Context Builder는 `metadata.authoring.source-registry.v3`가 투영한 같은 `metadata.authoring.semantic-vocabulary.v1`과 SHA-256을 사용한다. LLM에 제공하는 항목은 dataset의 `id/family/labels`와 field/metric/relation/grain/ordering/predicate/recipe/entity-group의 `id/labels`뿐이다. physical column, type, role, coercion, source/config/query ref, metric binding, 실행 payload와 `semantic_templates`는 포함하지 않는다.
   - Domain LLM은 `display_name`/`description` 외 실행 section을 출력하지 않는다. Dataset LLM은 compact Dataset IR, Main Filter LLM은 `target_type`·`target_id`·`expressions`만 가진 typed IR을 만든다. Exact source binding과 실행 의미는 compiler가 registry membership/hash를 확인한 뒤 결정론적으로 확정한다.
   - `metadata.authoring.semantic-templates.v1`의 metric/relation/grain/ordering/predicate/recipe/entity-group/alias와 `planner_policy`는 compiler-owned다. Domain Policy의 output profile 입력도 `planner_profile` 또는 `legacy_catalog_sha256`을 덮어쓸 수 없다.
   - 특화 authoring 지시는 공통 Prompt나 custom component에 하드코딩하지 않고 해당 분기의 **별도 특화 Prompt Template 본문**에 직접 작성한다. 작업자 입력이나 Domain metadata가 특화 본문을 만들거나 바꾸지 않는다.
31. 최초 Dataset bootstrap의 compact Dataset IR은 **LLM 내부 출력 계약**이다. 처리 순서는 `compact schema 검증 → 승인 vocabulary membership 검증 → duplicate reconciliation → 동일 dataset의 승인 Source Registry v3 descriptor와 1:1 대조 → 승인 family·physical column·semantic type·roles로 full datasets section 확장 → 승인 dataset 집합 exact coverage → 승인 source binding overlay → full-draft schema/semantic/dependency/security compiler`로 고정한다. Dataset ID가 중복된 card는 거부한다. 같은 dataset의 동일 canonical field descriptor가 반복되면 의미와 선택 속성이 동등한 경우에만 하나로 merge하고 alias를 dedupe하며, 단위·연산자·정책·binding이 충돌하면 거부한다. LLM이 만든 기술 스키마나 source binding은 authority가 아니며 registry 값으로만 봉인한다.
32. 작업자용 clarification은 날짜·자료·수량·제품·공정처럼 답할 수 있는 업무 선택지만 제시한다. `dataset_id`, `field_id`, canonical ID, 등록 ID, schema, JSON, DSL, type, physical column, `config_ref`, `query_ref`를 묻는 응답은 계약 실패다.
33. Main Filter LLM의 모든 alias addition에는 `target_type`이 필수다. Field와 metric처럼 동일 ID가 여러 의미 종류에 존재할 수 있으므로 type 없는 ID 추측, physical-column fallback 또는 fuzzy target 선택은 금지한다.

세부 계약은 [PROMPTS.md](contracts/PROMPTS.md)를 따른다.

## Canonical 실행 순서

1. `00 분석 질문 입력`과 `01 사용 가능 메타데이터 불러오기`가 사용자 질문과 3컬렉션 항목에서 컴파일한 runtime catalog를 준비
2. `02 요청 및 세션 상태 고정`이 내부 현재 시각·고정 `Asia/Seoul` 기준의 request capsule과 이전 turn state/result contract를 구성
3. metadata dependency bundle, hash-pinned registered-function registry와 immutable resolved candidate bundle 선택
4. Route Eligibility Gate가 `analysis.route.v1`의 `deterministic|intent_llm|unsupported`, reason과 proof hash 확정
5. `deterministic`이면 proof에 pin된 selection으로 Deterministic Intent Builder가 `analysis.intent.v1` 생성
6. `intent_llm`이면 공통 Intent Prompt Template과 특화 Intent Prompt Template을 각각 렌더링한다. Prompt Bundle Composer가 두 Message와 bounded candidate runtime context를 named input으로 받아 검증된 `prompt.envelope.v1`을 만들고 Conditional Intent LLM Invoker가 이를 호출한다.
7. Intent Decoder가 동일한 `analysis.intent.v1`을 생성한다. syntax/schema 오류, candidate 밖 ID 또는 provider 오류는 재호출 없이 canonical `intent_contract_error`로 fail-closed한다.
8. 두 route의 closed intent schema/hash 동등성 검증. `unsupported`이면 retrieval 없이 canonical error와 telemetry를 만들고 종료
9. metadata resolver와 공통 plan compiler로 `analysis.plan.v1` 생성. 선택된 registered function은 exact registry pin을 가진 `registered_call`로만 확장
10. plan의 declarative binding spec validation
11. owner-bound entity value resolve와 immutable job bundle validation 후 `11 검증용 더미 데이터 조회`, `12 Oracle 데이터 조회`, `13 H-API 데이터 조회`, `14 Datalake 데이터 조회`, `15 Goodocs 데이터 조회`가 각자 배정된 source만 실제 read-only 방식으로 조회한다. 실제 source node는 v5와 같은 운영 입력을 노출하며 빈 값은 환경변수 fallback을 사용할 수 있다. 비밀값은 export JSON 기본값으로 저장하지 않고, 조회 결과 행을 운영자가 `EDIT SOURCE PAYLOAD`로 직접 입력하는 경로는 사용하지 않는다.
12. Source Contract Merger의 exact-once canonicalization 및 source contract validation
13. 공통 typed operation DAG 실행. `registered_call`은 Registered Function Gateway가 implementation hash·I/O schema·resource policy를 재검증한 뒤 standalone allowlist 구현만 호출
14. result lineage/schema/ordering validation
15. result/source snapshot ref 저장
16. deterministic answer facts 생성
17. narrative가 켜진 경우 공통 Answer Prompt Template과 특화 Answer Prompt Template을 각각 렌더링하고, Prompt Bundle Composer가 두 Message와 facts runtime context를 받아 만든 prompt envelope로 Conditional Answer LLM Invoker가 호출
18. fact-ID claim validation, canonical response/final executed-result contract/next-turn state 조립
19. content-addressed executed contract publish와 owner/session-bound state CAS commit
20. runtime buffer release
21. `23 표준 응답 및 세션 상태 저장`은 전송용 hash가 없는 일반 JSON 응답을 만들고 24·25·26으로 fan-out한다. `24 채팅 메시지 표시 설정`, `25 API 표준 응답 출력`, `26 GaiA 형식 출력`은 수신 hash나 전체 응답 schema를 다시 검증하지 않으며, `27 분석 답변 출력`이 채팅 Message를 반환한다.

## 변경 작업 절차

1. Phase 1 전에는 TXT/acceptance migration source에서 실패를 재현한다. `validation/cases.jsonl` 승인 후에는 그 manifest에 contract oracle과 함께 추가하거나 기존 case를 재현한다.
2. 실패 단계가 metadata compile, intent parse, plan compile, retrieval, execution, rendering 중 어디인지 분류한다.
3. question-specific string 없이 해당 단계의 generic contract를 수정한다.
4. component source와 embedded schema를 재생성한다.
5. targeted unit/contract test를 실행한다.
6. 전체 deterministic corpus를 실행한다.
7. imported endpoint에서 전체 corpus의 route/call-count oracle을 확인하고, `expected_route=intent_llm` case만 두 모델 이상으로 semantic conformance profile을 3회 실행한다.
8. Flow JSON·bundle·manifest를 재생성한다.
9. exact 1.9.2 parse/import/API smoke를 수행한다.

## 금지되는 수정 패턴

- `"아침재공"` 문자열을 normalizer에서 검사해 dataset을 덮어쓰기
- `DEN/DENSITY`, `MODE/Mode`를 공통 fallback dict로 하드코딩
- pandas code 실패 후 다른 metric을 복사해 required column을 채우기
- 결과에 없는 metric을 answer builder가 이름만 만들어 표시
- validator가 `W/BM` 안의 `W/B` substring을 공정 그룹으로 판단
- dummy fixture에 정답 plan/code를 넣고 LLM 검증이 완료됐다고 판단
- retired `generated_code` 필드의 존재/비어 있지 않음을 deterministic execution 성공 조건으로 사용
- retry 성공만 최종 성공으로 합산하고 first-pass failure를 숨김
- custom component의 `_authoring_prompt`, `build_intent_prompt`, `prompt = (...)` 같은 함수/상수에 LLM instruction을 작성
- 공통 prompt와 특화 prompt를 하나의 Prompt Template node에 section/placeholder로 합치기
- 같은 question/candidate/facts/schema/source payload를 공통·특화 Prompt Template 양쪽에 중복 전달
- Prompt Template 출력을 native Language Model 입력에 직접 연결해 route gate를 우회
- 외부 prompt input이 비어 있거나 hash가 다른데 component 내부 기본 prompt로 계속 실행
- JSON 오류 retry 문구를 component가 문자열로 덧붙이기
- Intent/Answer/authoring LLM 실패 후 같은 모델이나 다른 모델을 자동 재호출하기
- raw source row, full metadata catalog, secret/query/credential을 prompt variable로 전달
- 특화 Prompt 본문을 사용자 입력·metadata 변수로 동적 교체하거나 공통 Prompt와 한 Template에 합치기
- `specialized_functions` card를 candidate/plan/executor consumer 없이 UI에 실행 가능 기능으로 노출하기
- metadata의 함수 source/code를 `eval`/`exec`하거나 function name만으로 dynamic import하기
- 사용자 표시 node/input/output을 영문 이름·설명만으로 배포하거나 Sticky Note를 수동 JSON에만 추가하기

## Definition of Done

- contract와 구현이 동기화됨
- 새 질문이 canonical case corpus에 있음
- deterministic suite 100%
- route classification/call-count/no-fallback suite 100%
- model conformance 대상 case의 모든 run이 exact oracle 및 반복 안정성 통과
- payload budget 통과
- source/prompt/schema/export hash 일치
- runtime/authoring custom component source의 LLM instruction literal 0건과 외부 prompt node/edge/pin 완전성 통과
- Runtime Intent/Answer와 Authoring 작업별 공통·특화 Prompt pair의 고정 본문·빈 변수 집합·named authority/runtime-context edge 완전성 통과
- deterministic/unsupported/narrative-off 경로에서 prompt 구성 여부와 무관하게 provider 호출 0회
- Intent/Answer 및 후속 authoring 경로의 provider 호출 최대 1회, 최초 Domain bootstrap의 분리 호출 정확히 3회, 모든 경로 retry 0회
- 비정형 표현·순서·누락 정도가 다른 작업자 TXT corpus가 기본 free-form lane에서 Domain annotation, compact Dataset IR, `target_type` 필수 Main Filter IR로 변환되고, Source Registry v3 template/descriptor 확장 뒤 invalid dependency·binding·security 후보는 compiler가 저장 전에 거부
- optional `explicit_inventory`/Blueprint lane을 사용하지 않은 기본 run에서 Blueprint/pin 또는 inventory 선언문을 요구하지 않음
- exact package tuple과 모든 Flow parse/import 통과
- composable operator matrix와 v5 presentation/output compatibility matrix 통과
- `registered_call` candidate→intent→plan→registry lookup→standalone execution→result/trace의 positive/negative end-to-end matrix 통과
- 모든 사용자 표시 label/description/input info/output 설명의 한국어 localization과 필수 Sticky Note inventory 통과
- 결과 report에 git SHA, dirty state, manifest SHA, metadata snapshot, model, attempt가 기록됨
