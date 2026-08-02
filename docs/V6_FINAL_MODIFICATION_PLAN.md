# metadata_driven_v6 최종 수정 계획

## 1. 최종 목표

하나의 공유 Data Analysis Flow가 제조·주문/매출·고객지원 등 서로 다른 업무에서 같은 실행 구조를 사용한다. 사용자는 자연어 metadata, domain policy와 Flow의 외부 prompt node만 교체하며, 정확성은 compiled metadata, closed semantic intent, typed Execution IR와 deterministic executor가 책임진다.

다음 기존 기능은 유지한다.

- Langflow 1.9.2 standalone custom component
- 자연어 기반 metadata 등록, `validate_only`, 입력 가능한 3컬렉션 원자적 `save`
- 결정 가능한 질문의 LLM 0회 실행
- 선택적 Intent/Answer LLM
- Top/Bottom N, extrema, filter, aggregate, compare, join, derive와 detail 조회
- Message 표시 항목 선택, structured API, GaiA output, download ref
- owner/session-bound multi-turn state와 이전 result/source 재사용

## 2. 확정 설계 결정

### 2.1 모든 LLM prompt는 외부 node가 소유한다

Intent, Answer narrative, Domain annotation, Dataset compact IR과 Main Filter typed IR prompt를 custom component source에 작성하지 않는다.

Prompt 원문은 `prompts/data_analysis/`와 `prompts/metadata_authoring/` 아래의 purpose별 공통·특화 UTF-8 파일로 분리한다. `flow_inventory.json`의 native Prompt Template node가 `prompt_source`로 읽어 Flow canvas에 표시한다.

- Runtime Intent/Answer는 공통 Prompt Template과 도메인 특화 Prompt Template이 필수 pair다.
- Domain/Dataset/Main Filter authoring도 작업별 공통·특화 Prompt Template이 필수 pair다.
- 특화 업무 규칙은 각 특화 Template 본문에 직접 작성하고 사용자 입력이나 metadata로 동적 교체하지 않는다.
- Domain Policy는 Prompt/LLM 0회다. Main Filter의 zero-LLM compile은 optional `source_grounding_mode=explicit_inventory`의 완전한 binding proof에서만 사용한다.

custom component는 다음만 수행한다.

- typed/allowlisted runtime context를 한 번만 생성
- purpose별 필수 공통·특화 prompt fragment의 named authority/purpose/revision/SHA-256/placeholder/byte budget과 segment cardinality 검증
- route 또는 mode에 따른 provider 조건부 호출
- closed JSON/schema/candidate/fact-claim 검증
- hash와 call telemetry 기록

Runtime 또는 Authoring pair가 누락되거나 pin이 다르면 component 내부 default로 대체하지 않고 provider 호출 전에 fail-closed한다. 상세 계약은 `harness/contracts/PROMPTS.md`를 따른다.

### 2.2 공통 prompt와 domain 지침을 분리한다

Flow에서 다음 항목이 물리적으로 다른 Prompt Template node와 hash를 가진다.

1. 공통 의도 선택 Prompt Template
2. 도메인 특화 의도 해석 Prompt Template
3. 공통 답변 생성 Prompt Template
4. 도메인 특화 답변 생성 Prompt Template
5. 도메인 등록 공통 Prompt Template
6. 도메인 등록 특화 Prompt Template
7. 데이터셋 등록 공통 Prompt Template
8. 데이터셋 등록 특화 Prompt Template
9. 기본 필터 등록 공통 Prompt Template
10. 기본 필터 등록 특화 Prompt Template

공통과 특화를 한 Prompt Template 안의 section이나 placeholder로 합치지 않는다. Runtime과 Authoring Prompt Bundle Composer가 `common_prompt_message`, `specialized_prompt_message`, `runtime_context`를 별도 named input으로 받고 공통=`system`, 특화=`domain_policy`, context=`untrusted_data` authority를 검증한다. question/candidate/facts/schema/source payload는 Prompt Template에 복제하지 않고 runtime context로 정확히 한 번만 전달한다.

Data Analysis와 Authoring의 특화 Prompt Template에는 배포 대상 업무 규칙을 본문으로 직접 작성한다. 모든 Prompt Template은 변수 없이 렌더링하고 Flow 입력으로 본문을 주입하지 않는다. 신규 Domain bootstrap은 작업별 공통·특화 authoring Prompt와 자유형 source bundle을 사용하되 LLM 출력은 Domain 표시명/설명 annotation, compact Dataset IR, `target_type` 필수 Main Filter IR로 제한한다. 입력 TXT가 prompt 원문을 만들거나 변경할 수 없다.

작업자에게 JSON, canonical ID inventory, relation endpoint/field-role 선언, 타입, 컬럼 또는 IR 같은 정형 문법을 요구하지 않는다. 최초 bootstrap은 기존 Domain·Dataset·Main Filter TXT를 합친 bundle 또는 동등하게 완전한 도메인 설명을 받는다. 부족한 업무 정보는 draft/candidate 없는 `status=needs_clarification`의 `missing_fields`/질문으로 설명한다. `source_grounding_mode=explicit_inventory`와 Blueprint/pin은 운영자가 명시적으로 선택하는 고신뢰 lane이다.

실행 의미의 authority는 `metadata.authoring.source-registry.v3`다. LLM에는 최소 `semantic_vocabulary`만 전달하고 compiler-owned `semantic_templates`, dataset descriptor와 Source binding은 전달하지 않는다. Compiler가 Domain annotation과 Dataset/Main Filter IR을 결정론적으로 확장한다. `semantic_templates.planner_policy`는 봉인돼 Domain Policy의 `output_profile_json`도 `planner_profile`이나 legacy catalog hash를 변경할 수 없다.

### 2.3 Generic core와 제조 호환 기능을 분리한다

공유 Flow와 component에는 `manufacturing`, `MCP_NO`, `OPER_NAME`, `production_today`와 embedded 제조 catalog가 없어야 한다. 날짜·순위·임계값 같은 공통 literal만 core가 처리하고, field/value/group/order/relation은 active Domain Package에서 해석한다.

제조 v5 planner, literal parser와 dummy fixture는 compatibility/validation package로 격리한다. 공유 Flow의 `01 사용 가능 메타데이터 불러오기`는 domain/source mode 선택 input을 두지 않고 노드에 지정된 3컬렉션에서 가장 최근의 완전한 release를 자동 선택·결합한다.

### 2.4 metadata policy를 실제 consumer에 연결한다

- `output_profile`의 field label, unit, currency, date/null formatting은 Message Presentation만 소비한다. API raw field/value는 변경하지 않는다.
- 일반 특화 계산은 formulas, recipes, predicates와 typed operators로 표현한다.
- 새 비표준 알고리즘은 function ID/version/implementation hash/registry-entry hash/I/O schema/resource policy가 build-time standalone registry와 일치할 때만 `registered_call`로 실행한다.
- `specialized_functions`는 Domain Policy 관리자 입력→Domain Package function card→registry attestation→candidate selection→Intent `operation_refs`→`registered_call` Typed IR→Registered Function Gateway→output schema/lineage validation까지 연결한다.
- metadata에는 code/module/callable을 저장하지 않는다. Gateway는 build-time allowlist implementation만 사용하며 dynamic import, `eval`/`exec`, arbitrary network/file/subprocess와 secret 접근을 금지한다.
- 위 consumer chain과 positive/negative E2E 검증이 완료되기 전에는 `specialized_functions` input을 실행 가능 기능처럼 노출하거나 active package에 승인하지 않는다.

## 3. 목표 Flow와 node 경계

### 3.1 Data Analysis Flow

```text
분석 질문 입력
→ 사용 가능 메타데이터 불러오기 (Mongo URI/DB/세 컬렉션명/timeout, 최신 release 자동 결합)
→ 요청·대화 상태 구성 (기준시각·시간대 UI 없음, Asia/Seoul 고정)
→ 후보·실행 경로 판정
   ├─ deterministic → 결정론적 Intent 생성
   ├─ intent_llm → Bounded Runtime Context Builder
   │                + 공통 의도 선택 Prompt Template
   │                + 도메인 특화 의도 Prompt Template
   │                → Prompt Bundle Composer
   │                → Conditional Intent LLM Invoker
   │                → Intent Decoder
   └─ unsupported → canonical error
→ 공통 Intent 검증
→ Active Function Card + Standalone Registry attestation
→ Typed IR 생성·검증 (`registered_call`은 exact function/registry/schema pin 필수)
→ 데이터 조회 경로 분기
   ├─ 검증용 더미 데이터 조회
   ├─ Oracle 데이터 조회
   ├─ H-API 데이터 조회
   ├─ Datalake 데이터 조회
   └─ Goodocs 데이터 조회
→ Source Contract 병합
→ 결정론적 실행 (built-in typed op + Registered Function Gateway)
→ Answer Facts Builder
   ├─ narrative off → deterministic answer
   └─ narrative on → 공통 답변 생성 Prompt Template
                      + 도메인 특화 답변 Prompt Template
                      + facts runtime context
                      → Prompt Bundle Composer
                      → Conditional Answer LLM Invoker
                      → Fact Claim Validator
→ 응답·멀티턴 상태 저장
→ 채팅 schema 검사 / API·GaiA response hash 검사 후 fan-out
```

Language Model native node는 model object만 제공한다. Prompt를 일반 Language Model node에 직접 연결해 route와 무관하게 provider를 호출하지 않는다.

### 3.2 Metadata authoring Flow

현재 하나의 Authoring Engine이 모든 입력과 prompt 생성을 소유하는 구조를 다음 facade로 나눈다.

- 도메인 자유형 자연어→표시명/설명 annotation only→Source Registry v3 semantic-template expansion
- optional explicit-inventory/Blueprint pin 검증; Blueprint도 annotation schema를 확장하지 않음
- 데이터셋 자유형 자연어→compact Dataset IR→승인 descriptor/Source binding expansion
- 주요 필터 자유형 자연어→`target_type` 필수 typed IR→alias-card expansion과 optional explicit-inventory deterministic gate
- 도메인 정책 입력 검증
- Authoring Runtime Context Builder
- Domain/Dataset/Main Filter별 작업 공통·특화 Prompt Template pair
- Prompt Bundle Composer
- Conditional Authoring LLM Invoker
- branch-owned annotation/IR decoder, Source Registry v3 expander와 full-draft compiler
- prepare/execute writer
- 등록 결과 Message/API terminal

Domain Policy는 Runtime Context Builder, Prompt Composer와 LLM Invoker를 우회하는 것이 아니라 애초에 해당 node를 실행 경로에 포함하지 않는 deterministic 전용 Flow다. Main Filter도 optional `source_grounding_mode=explicit_inventory` proof가 유효할 때만 같은 zero-LLM 경로를 사용한다. 일반 LLM 경로의 공통·특화 Message는 모두 실제 별도 Template 본문에서 온다.

권장 공유 Flow는 다음 다섯 개다.

1. 메타데이터 v6 - 신뢰 기반 데이터 분석
2. 메타데이터 v6 - 도메인 메타데이터 등록
3. 메타데이터 v6 - 데이터셋 카탈로그 등록
4. 메타데이터 v6 - 주요 필터 메타데이터 등록
5. 메타데이터 v6 - 도메인 정책 등록

## 4. 한글 UI와 Sticky Note

내부 node ID, class, input/output `name`, JSON key, enum과 endpoint는 유지하고 Flow 이름/설명, node `display_name`/`description`, input `display_name`/`info`, output label/설명을 한글화한다. Schema ID나 기술 용어는 한국어 설명 뒤 괄호로 병기할 수 있지만 영문 identifier만 단독 노출하지 않는다.

각 input `info`는 최소한 기능, 필수/선택, 기대 contract/type, 값의 소유자와 주요 consumer를 설명한다. 각 output 설명은 반환 contract/type, 다음 연결 대상과 표시 toggle이 canonical result를 변경하는지 여부를 설명한다. Localization은 builder의 inventory overlay가 적용하며 port/edge/API 계약과 component source의 업무 로직을 바꾸지 않는다.

Data Analysis Flow에는 입력/최초 설정, 최신 3컬렉션 자동 결합, Runtime 공통·특화 prompt와 LLM route, 분리된 Dummy/Oracle/H-API/Datalake/Goodocs source, Typed IR/`registered_call` 실행, 채팅 schema/API·GaiA hash 경계와 multi-turn 출력 설명 Note를 배치한다. Domain/Dataset/Main Filter Flow에는 자연어 입력, 작업별 공통·특화 prompt pair, 수정 범위, 승인·저장·출력 Note를 배치한다. Domain Policy Flow에는 explicit 관리자 입력, LLM 0회, registered function card는 pre-registered hash만 참조한다는 Note를 배치한다.

Sticky Note는 Langflow 1.9.2의 `noteNode`/`data.type=note` 구조로 builder가 deterministic ID/layout/content revision과 함께 생성하며 edge와 실행 node count에서 제외한다. Note에는 secret, URI, query, raw row, prompt 원문 전체와 실제 환경 값을 넣지 않는다. Flow wiring이 바뀌면 관련 Note revision도 갱신하고 stale-note 검증을 수행한다.

## 5. 파일 단위 구현 순서

### 독립 구조 검토 반영

별도 검토 에이전트는 이 구조를 **조건부 승인**했다. 외부 prompt 자체는 Langflow 1.9.2, standalone과 Typed IR 안전성을 깨지 않지만 다음 조건은 필수다.

- Prompt node만 추가하지 않고 prompt envelope/schema/registry, named-authority composer, conditional invocation과 closed decoder를 함께 구현
- Runtime Intent/Answer와 Domain/Dataset/Main Filter authoring의 공통/특화 Prompt Template을 모두 별도 필수 pair로 만들고, exact Langflow 1.9.2 processor에서 예상 변수 집합을 빈 값으로 유지
- Domain Policy와 optional explicit-inventory Main Filter는 Prompt Template, Prompt Bundle Composer, LLM Invoker와 `prompt.envelope.v1` 생성이 모두 0회인지 정적·동적 검증
- runtime context를 공통·특화 양쪽에 복제하지 않고 Composer의 세 번째 입력으로 한 번만 전달
- Intent malformed JSON/provider 오류의 자동 retry를 제거해 Intent 호출 최대 1회 유지
- 공개 `/run` tweak로 공통·특화 prompt 본문, pin과 model policy를 바꾸지 못하도록 차단
- Authoring은 context builder → 외부 prompt → conditional LLM → closed decoder/compiler로 분리
- source generator가 공통 helper를 flatten하면서 비호출 component에 복제한 prompt/invoke code까지 제거

### Phase 0. Baseline 고정

- 현재 validation corpus, component/Flow/source hash와 HTTP 증적 보존
- 기존 19/6 실행 node count와 28/5 edge 기준을 annotation과 분리
- 변경 전 Message/API/GaiA/multi-turn compatibility snapshot 생성

### Phase 1. External prompt contract와 Flow wiring

- `contracts/schemas/prompt-envelope.schema.json`과 prompt registry/schema 추가
- `prompts/data_analysis/`와 `prompts/metadata_authoring/`로 purpose별 공통·특화 원문을 분리
- Data Analysis에 Intent 공통·특화, Answer 공통·특화 Prompt Template 4개를 추가하고 Domain/Dataset/Main Filter에도 작업별 공통·특화 Prompt Template을 하나씩 연결
- Domain Policy Flow에는 prompt node·Composer·Invoker를 생성하지 않고, optional explicit-inventory Main Filter route는 이 node들을 실행하지 않는다.
- `flow_inventory.json`에 purpose별 segment cardinality, source path, prompt ID/revision/hash/authority와 입력 edge를 추가
- `flow_builder_support.py`의 기존 Prompt Template/`prompt_source` 기능에 exact 1.9.2 빈 변수 집합, purpose별 segment cardinality, authority 검증 추가
- generic Runtime Context Builder, Prompt Bundle Composer, Conditional LLM Invoker/Decoder를 standalone source로 생성
- 내부 `_authoring_prompt`, `_v2_authoring_prompt`, `_v2_domain_annotation_prompt`, Intent/Answer prompt 조립과 retry suffix 제거
- 기존 helper source flattening으로 candidate/plan 등 비호출 component에 복제된 prompt builder와 invoke code도 제거
- 기본 Domain authoring에서 세 free-form TXT→원문별 LLM 최대 1회(총 3회)→Domain annotation/compact Dataset IR/`target_type` 필수 Main Filter IR→Source Registry v3 deterministic expansion/merge→schema/semantic/dependency/security compile을 구현하고 Blueprint/pin 없는 입력을 허용
- v3 registry의 semantic-template/blueprint/executable/projection hash 검증과 sealed planner-policy 변경 차단 구현
- optional `explicit_inventory`/Blueprint external-pin lane을 별도 admin mode와 trust pin으로 격리

### Phase 2. Generic core 분리

- 공통 literal parser와 제조 compatibility literal parser 분리
- generic component에서 legacy planner/catalog/dummy source embed 제거
- domain/timezone/environment identity를 active package에서 검증
- Metadata loader의 UI에 MongoDB URI·database·세 컬렉션명·timeout을 제공하고 입력 3컬렉션의 최신 완전 release 자동 결합을 fail-closed로 구현
- 제조 validation Flow/package는 exact hash pin과 명시적 opt-in 유지

### Phase 3. Domain policy와 authoring UX

- 도메인 정책 등록 Flow 추가
- Domain/Dataset/Main Filter/Policy별 thin facade로 visible input 축소
- Metadata collection 이름과 domain/environment/source mode는 UI에서 제거하고, Request의 기준시각·시간대 input도 제거해 `Asia/Seoul`로 고정
- Dummy/Oracle/H-API/Datalake/Goodocs node를 분리하고 실제 source node에는 조회 행 수 제한만 운영 조절값으로 노출
- Domain Policy Flow의 public 입력은 explicit 관리자 전용 `intent_prompt_extension`, `answer_prompt_extension`, `specialized_functions_json`, `output_profile_json`과 저장/승인 식별자로 제한하고 자연어 authoring, Prompt/LLM/envelope 입력은 제공하지 않음
- `specialized_functions` descriptor를 exact `(function_id, version, implementation_sha256, registry_entry_sha256, input_schema_sha256, output_schema_sha256)`로 build-time standalone registry와 attestation
- Candidate Selector가 검증된 function card만 후보로 제공하고 Intent는 candidate ID만 선택하며, Plan Compiler가 exact pin을 가진 `registered_call` Typed IR로 컴파일
- Registered Function Gateway가 allowlisted standalone implementation, argument binding, field/role, resource policy, output schema와 lineage를 검증해 실행. dynamic import, `eval`/`exec`, arbitrary network/file/subprocess와 미등록 fallback은 금지
- `output_profile` Message consumer와 registered function의 positive/negative E2E를 함께 구현하고, 전체 consumer chain 전에는 해당 입력을 실행 가능 기능으로 노출·활성화하지 않음

### Phase 4. 한글 UI와 Sticky Note

- inventory 기반 native/custom UI localization overlay
- standalone component input `info`와 output 설명 추가
- Flow 목적·node 이름·description 한글화
- builder 기반 Sticky Note 생성과 layout 적용

### Phase 5. 산출물 재생성과 검증

- standalone component 재생성 및 source parity
- 정확히 5개 MVP Flow(Data Analysis, Domain Authoring, Dataset Authoring, Main Filter Authoring, Domain Policy Authoring)의 export/import-ready JSON, ZIP, manifest 재생성
- exact Langflow 1.9.2/LFX 0.4.2 parse/import
- 실제 HTTP authoring/data-analysis/multi-turn/output 검증
- 실제 Gemini model conformance는 expected `intent_llm`/narrative/authoring case에만 수행하고 exact `gemini-3.5-flash-lite`, temperature 0, fallback 0, repair 0을 검증. 제조 bootstrap은 v6 전용 `domain_v6.txt`+`dataset_v6.txt`+`main_filter_v6.txt` 자연어 bundle 사용

## 6. 최종 승인 기준

- custom component와 standalone generator 내부 runtime LLM instruction literal 및 retry suffix 0건
- Runtime Intent/Answer LLM 호출은 각각 별도의 공통·특화 Prompt Template pair, valid `prompt.envelope.v1`, route/mode gate를 통과
- Domain/Dataset/Main Filter authoring LLM 호출은 작업별 공통·특화 Prompt pair를 사용하고 특화 규칙은 Template 본문에 직접 작성
- deterministic/unsupported/narrative-off/optional explicit-inventory Main Filter와 Domain Policy는 provider, prompt node, Composer와 prompt envelope 생성 0회
- 기본 Domain authoring은 비정형 사용자 TXT로 표시명/설명 annotation만 생성하고 Source Registry v3 template로 full draft를 확장한다. Blueprint/pin·inventory 문법을 요구하지 않으며 invalid template/IR/binding 후보는 compiler가 저장 전에 차단한다.
- Intent/Answer/authoring의 허용 경로별 provider 최대 1회, 자동 retry와 다른 모델 fallback 0
- 공통 prompt 변경 시 특화/component source hash가, 특화 prompt 변경 시 공통/component source hash가 불변
- source row/full catalog/secret/query가 LLM edge와 prompt/state/trace에 없음
- public HTTP tweak allowlist가 Runtime/Authoring 공통·특화 Prompt Template 본문, 모든 prompt pin과 model policy 변경을 거부
- Generic core의 제조 identifier와 embedded legacy catalog 0건
- `specialized_functions`는 Domain Policy 관리자 입력부터 hash-pinned registry, candidate selection, Intent `operation_refs`, `registered_call` Typed IR, Gateway 실행, output schema/lineage 검증까지 끊김 없이 연결되고 metadata-only 선언·dynamic import·미등록 fallback 0건
- 제조·주문/매출·고객지원 Domain Package가 같은 공유 Flow로 동작
- top/bottom N, extrema, projection, filter, aggregate, compare, join, derive, detail과 multi-turn corpus 통과
- Message 표시 toggle, structured API, GaiA output, download ref와 multi-turn compatibility 유지
- 23→24·25·26은 일반 JSON을 전달하고 출력 adapter는 수신 hash나 전체 응답 schema를 재검증하지 않음; 결과 hash는 MongoDB 저장 무결성에만 사용
- Data Analysis node의 `00`~`27` 및 네 등록 Flow의 Flow별 순서형 한국어 표시명, 최신 3컬렉션 자동 loader, 고정 `Asia/Seoul` Request와 분리된 5개 source node 계약 일치
- 정확히 5개 MVP Flow가 `last_tested_version=1.9.2`이고 모든 실행 node의 `lf_version=1.9.2`
- Flow/node/input/output의 사용자 가시 이름·설명은 한글이며 각 input `info`와 output 설명이 기능, 필수 여부, 계약/consumer를 명시
- Data Analysis와 네 authoring Flow의 역할·입력·수정 범위·LLM 0/1회 조건·승인/저장·출력·`registered_call` 주의사항 Sticky Note가 deterministic ID/layout/revision으로 존재하고 secret/query/raw row/prompt 원문을 포함하지 않음
- 한글 UI와 Sticky Note가 internal ID/port/API 계약을 변경하지 않음
- Python source, Flow JSON, prompt source, schemas, import bundle과 evidence manifest hash 동기화
- Langflow 1.9.2 실제 import와 endpoint smoke 통과

## 7. 구현 중단 조건

다음 중 하나라도 발생하면 내부 fallback을 추가하지 않고 해당 Phase를 중단해 계약 또는 metadata를 수정한다.

- 외부 prompt 없이도 component가 LLM을 호출함
- deterministic route에서 provider call이 발생함
- Domain Policy 또는 선택된 explicit-inventory Main Filter가 prompt node, Composer, envelope 또는 provider를 실행함
- Authoring 기본 export의 공통·특화 pair가 누락되거나 특화 본문이 동적 input으로 연결됨
- prompt variable에 raw row, secret, query 또는 full catalog가 포함됨
- generic core에서 제조 전용 literal/column/dataset이 발견됨
- specialized function이 registry/hash/schema 검증 없이 실행됨
- specialized function descriptor가 실제 candidate/Intent/`registered_call`/Gateway/output consumer 없이 metadata나 UI에만 존재함
- Message/UI 변경이 API/GaiA/state hash를 변경함
- Langflow import-ready JSON이 source inventory와 달라짐
