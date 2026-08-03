# v6 검증 가이드

## 1. 핵심 원칙

v6는 “코드가 실행됐다”를 정답으로 보지 않는다. 질문별로 dataset, 날짜, source filter, operation, lineage, result schema, result invariant를 검증한다.

과거 v5의 30/30 fixture 결과는 executor fixture가 통과했다는 증거이며 모델 계획 성공의 증거가 아니다. 과거 Gemini 결과도 현재 HEAD를 다시 검증한 결과가 아니다.

## 2. Corpus

- [validation_questions.txt](../validation/validation_questions.txt)
- [ACCEPTANCE_MATRIX.md](../validation/ACCEPTANCE_MATRIX.md)

포함 범위:

- 30 single-turn
- 6 date-contract
- MT-1~MT-5

Phase 1 변환은 완료됐다. `validation/cases.jsonl`이 70개 canonical case의 single source of truth이며, 질문 목록·acceptance matrix·route classification은 `tools/generate_contracts_and_cases.py`가 생성한다. 각 case에는 `expected_route=deterministic|intent_llm|unsupported`, route reason, exact Intent/retry/Answer/code/repair LLM call count, retrieval count, semantic contract, typed operation 순서와 result invariant가 들어 있다. v5 expected docs는 migration evidence일 뿐 현재 oracle을 덮어쓰지 않는다.

현재 corpus의 기준시각은 아래 값으로 고정한다.

- reference instant: `2026-07-30T09:00:00+09:00`
- timezone: `Asia/Seoul`
- `오늘`: `2026-07-30`
- `어제`: `2026-07-29`

개발 PC 시각이나 provider timezone에 따라 oracle이 달라지면 실패다. 이 고정 instant는 검증 harness의 fixture다. 운영 `02 요청 및 세션 상태 고정` node에는 기준시각·시간대 UI input이 없고 내부 현재 시각을 항상 `Asia/Seoul`로 해석한다.

## 3. 검증 단계

### 3.1 Contract unit

LLM 없이 metadata fixture와 route/intent fixture로 eligibility, common intent, compiler/operator를 검증한다.

확인:

- exact plan JSON
- route/reason/eligibility proof hash와 common intent hash
- plan fingerprint
- source/date/filter binding
- output lineage
- expected error

### 3.2 Deterministic end-to-end

actual Candidate Selector와 Route Eligibility Gate부터 dummy source terminal까지 실행한다. `deterministic|unsupported` case에는 provider-call guard를 설치한다.

확인:

- exact row/column/order
- control row exclusion
- empty/failure 구분
- required failure 전체 error와 declared optional-enrichment failure의 typed-null partial 구분
- follow-up result preservation
- expected route와 exact LLM call counter
- post-selection failure의 다른 route/LLM/pandas/exploration fallback 0

### 3.3 Typed flexibility compatibility

대표 corpus와 별도로 다음 operator matrix를 exact plan/result oracle로 실행한다.

- projection과 filter `all/any`, string/null/numeric operator
- aggregate와 scalar min/max
- global/per-group top·bottom N, exact-N/ties, single/multi-key와 per-metric argmax/argmin
- top+bottom `RESULT_GROUP/RESULT_RANK`
- 등록된 두 컬럼 비교와 duplicate group
- inner/left/right/outer/semi/anti join, 0/1/N match와 cardinality/null/suffix 정책
- formula AST type/rounding/zero-division
- detail/dedupe/history/row-match group

등록되지 않은 field role/join recipe/formula/operator는 retrieval 전에 clarification 또는 `unsupported_operation`으로 끝나야 하며 code fallback은 실패다.

Acceptance Matrix §5의 모든 `OP-*` question shape는 prebuilt intent/plan fixture뿐 아니라 actual candidate→Route Eligibility Gate→deterministic 또는 LLM intent→Common Intent Validator→compiler→imported endpoint 경로로도 검증한다. join match 수나 failure policy 같은 data variant는 같은 semantic plan 아래 deterministic subfixture로 분리한다.

### 3.4 Route classification과 no-fallback

| Category | 판정 |
| --- | --- |
| unique/complete | deterministic, Intent LLM 0, proof-pinned selection |
| semantic choice required | intent_llm, Intent LLM 1, candidate 밖 의미 0 |
| registry gap | unsupported, 모든 LLM/retrieval/executor/result-store/state-mutation 0, 이전 state 유지, bounded telemetry |
| alias/conflict | deterministic 금지, reviewed LLM/clarification oracle |
| downstream fault | 선택 route의 canonical error, route 전환/자유 code/exploration 0 |
| same semantic selection | 두 생성 경로의 common intent hash, plan/result hash 동일 |

동일 request/bundle/state에서 model profile을 바꿔도 route와 proof hash가 달라지면 실패다. 질문별 keyword, model confidence 또는 source row를 route 증거로 사용해도 실패다.

### 3.5 Model conformance

실제 metadata snapshot과 dummy retrieval을 사용한다. 전체 corpus를 각 model profile의 imported endpoint로 보내지만 실제 Intent LLM은 `expected_route=intent_llm` case에서만 호출한다. deterministic/unsupported case는 provider 호출 0을 검증한다.

기본 조건:

- temperature 0
- primary model 3회
- weaker/different model 3회
- 고정 reference instant `2026-07-30T09:00:00+09:00`, timezone `Asia/Seoul`
- 각 run 별도 report

비교:

- route/reason/proof hash와 actual LLM call counter
- intent IDs
- plan fingerprint
- retrieval mode/count와 required param
- result schema
- exact rows 또는 case-specific result invariant
- expected canonical error
- first-pass status

각 모델의 세 endpoint run 모두에서 모든 필수 case가 route/call-count oracle과 일치해야 한다. `intent_llm` case는 자기 exact semantic oracle에도 일치해야 한다. 세 fingerprint가 서로 같다는 것은 보조 안정성 조건일 뿐이며, 같은 오답을 세 번 반환해도 실패다. run 간 성공 항목을 합치거나 transport failure run을 조용히 제외하지 않는다.

### 3.6 Metadata authoring trust boundary

기본 Full-domain bootstrap은 작업자의 Domain·Dataset·Main Filter 자유형 자연어 TXT를 원문별 LLM 최대 1회, 총 3개의 closed fragment로 변환하고 deterministic merge/compiler가 실행 가능성을 판정한다. 검증은 다음을 모두 포함한다.

- 기존 Domain·Dataset·Main Filter 원문 bundle 또는 동등하게 완전한 도메인 설명을 순서·말투·제목·표기가 다른 비정형 fixture로 입력
- 제조 live fixture는 v6 전용 `domain_v6.txt`+`dataset_v6.txt`+`main_filter_v6.txt` bundle과 exact `gemini-3.5-flash-lite`, temperature 0, provider/model fallback 0, repair 0을 사용
- 일반 작업자 입력에 JSON, explicit inventory 문장, relation/field-role 문법, Blueprint/pin을 요구하지 않음
- LLM 출력은 원문별 closed fragment contract, 최초 bootstrap 호출 정확히 3회, repair/fallback 0. 세 작업별 공통·특화 Prompt Template pair가 별도 node/source/hash/edge로 존재하고 특화 규칙은 Template 본문에 직접 작성
- schema·identity·field/source binding·semantic type·relation/cardinality·dependency·read-only/secret/registry security compile 통과 전 candidate 저장 0
- 부족한 설명은 특정 포맷 재작성을 요구하지 않고 `status=needs_clarification`의 누락 항목/질문을 반환하며 draft/candidate/persist는 0
- `metadata.authoring.proposal.v1`의 complete/needs-clarification two-variant contract, exact source hash, recursive closed keys와 mixed/extra-key negative fixture를 검증
- Dataset은 최신 완전 3컬렉션 package의 dataset section만 작업 전용 공통·특화 Prompt pair와 자연어 patch LLM 1회로 변경한다. Main Filter 기본 lane도 작업 전용 공통·특화 Prompt pair와 bounded LLM 최대 1회이며, optional `explicit_inventory` proof가 완전할 때만 Prompt/Composer/envelope/LLM 0회다. 두 경로 모두 나머지 section/hash dependency를 재검증한다.
- Optional `source_grounding_mode=explicit_inventory` profile은 완전한 inventory의 zero-LLM compile과 관리자 검토 `metadata.executable-blueprint.v1`/external SHA-256 pin의 annotation-only merge를 별도로 검증한다. Blueprint/pin 누락·tamper의 provider-call-0 gate는 이 profile에만 적용한다.
- 모든 공통·특화 Template의 예상 변수는 빈 집합이고 사용자 입력·metadata로 특화 본문을 교체하는 dynamic port/edge가 없으며 runtime context가 Composer에 정확히 한 번 연결되는지 검사
- Domain Policy는 별도 Flow의 explicit 관리자 입력 `intent_prompt_extension`, `answer_prompt_extension`, `specialized_functions_json`, `output_profile_json`만 사용하고 prompt node/Composer/envelope/LLM 0회
- 모든 authoring kind가 immutable prepare → external approval → 별도 atomic execute를 사용하며 execute 시 candidate/base/dependency hash를 재검증

### 3.7 Live source smoke

read-only로 source schema와 parameter를 검증한다. 실데이터 값 전체를 golden row로 고정하기보다 schema, non-empty/empty policy, aggregation invariant, required-param 오류를 본다.

live smoke와 별개로 Oracle, H-API, Datalake, Goodocs, Dummy 5개 adapter type 모두 fixture contract와 security test를 가진다. 9개 live dataset이 배포된 일부 adapter만 사용해도 나머지 adapter fixture를 생략하지 않는다.

Flow graph에는 `11 검증용 더미 데이터 조회`, `12 Oracle 데이터 조회`, `13 H-API 데이터 조회`, `14 Datalake 데이터 조회`, `15 Goodocs 데이터 조회`가 각각 하나씩 있어야 한다. 네 실제 source node는 자기 lane의 job과 메타데이터만 처리하고 v5 호환 운영 입력으로 read-only 조회를 실행해야 한다. `source_payload`/`EDIT SOURCE PAYLOAD` 입력은 없어야 하며 export된 credential 기본값은 비어 있어야 한다.

필수 adapter 판정:

- typed param, canonical schema, empty/failure, provenance/coverage, timeout/size limit
- registry/allowlist 밖 SQL, URL, path, query/job/document ID 거부
- Oracle/H-API/Datalake/Goodocs read-only, Dummy egress 0
- URI, credential, token, header, raw query가 Flow/prompt/state/trace/error/test report에 평문으로 남지 않음
- canonical error는 중앙 `error_registry.v1`과 동일한 code/meaning 사용

### 3.8 Langflow import/output과 pytest

isolated exact 1.9.2 environment에 generated Flow를 import하고 Chat/API/GaiA 경로를 실제 실행한다.

필수 환경과 evidence:

- Python 3.12.x
- exact `langflow==1.9.2`, `langflow-base==0.9.2`, `lfx==0.4.2`
- lockfile/installed distribution inventory hash
- pytest full suite exit code 0
- JUnit XML 또는 동등한 machine-readable pytest report와 console log의 path/hash
- unexpected skip/xfail, collection error, mandatory case deselection 0
- MVP logical key/`endpoint_name`이 정확히 `metadata_v6_data_analysis`, `metadata_v6_domain_authoring`, `metadata_v6_dataset_catalog_authoring`, `metadata_v6_main_filter_authoring` 4개
- 다섯 Flow 모두 version/schema/source hash, parse, isolated import 통과
- top-level UUID는 fixed namespace + logical key의 expected UUIDv5와 일치
- physical standalone source/node/edge 수는 재생성 manifest와 일치하며 Flow source/export/import-ready projection의 모든 custom-node instance가 같은 embedded source hash와 일치. 기존 18개 source/75개 instance 수치는 4-Flow migration baseline일 뿐 final oracle이 아님
- imported Data Analysis endpoint는 dummy profile 30 single + 6 date + MT-1~MT-5 + 모든 `OP-*` 전체 route corpus와, 그중 `expected_route=intent_llm` subset의 primary/secondary 각 3회 model conformance를 통과
- 모든 imported run에서 route/reason/call-count와 no-fallback oracle 통과
- imported Data Analysis endpoint는 typed flexibility matrix와 v5 Message 표시/API/GaiA compatibility matrix를 통과
- 세 authoring Flow는 각각 자연어 변환, 결정론적 검증, selector-free 입력, `save|replace|validate_only`, 항목 단위 저장·교체·무저장 smoke를 통과
- Domain Flow의 기본 free-form full-draft lane은 빈 Blueprint/pin으로도 실행하고, optional explicit-inventory profile에서만 missing/tampered Blueprint pin zero-model fail-closed와 annotation allowlist를 통과
- Domain Policy와 optional explicit-inventory Main Filter는 prompt node/Composer/envelope/provider 호출 0을 정적 graph와 runtime counter 양쪽에서 통과
- Runtime Intent/Answer와 Domain/Dataset/Main Filter는 공통·특화 Prompt Template의 node ID/prompt ID/revision/source/hash/edge가 물리적으로 분리되고, 모든 Template의 변수 집합이 비어 있으며 runtime context는 Composer에 한 번만 전달
- `01 사용 가능 메타데이터 불러오기`는 MongoDB URI·database·도메인/데이터 카탈로그/메인필터 컬렉션명·timeout을 노출하고 입력 3컬렉션의 항목 문서를 결합해 메모리에서 실행용 metadata를 컴파일하며, domain/environment/source mode 입력은 없음
- Data Analysis 실행 node는 `00`~`27`, 네 등록 Flow는 각자의 `00` 입력부터 최종 출력까지 순서형 한국어 표시명을 사용하고 병렬 단계만 `A/B/C`로 구분한다. `24` 채팅은 schema만, `25` API와 `26` GaiA는 schema+response hash를 검사
- 각 Flow/node/input/output의 사용자 가시 이름·설명은 한글이고 input `info`/output 설명이 기능·필수 여부·contract/consumer를 명시. 역할별 Sticky Note는 deterministic ID/layout/content revision이며 secret/query/raw row/prompt 원문을 포함하지 않음
- exploration Flow/endpoint/worker는 초기 bundle에 없고 Data Analysis에서 `exploration.*` 자동 호출 edge가 0

### 3.9 Registered function end-to-end

`specialized_functions`는 metadata schema 통과만으로 성공 처리하지 않는다. 최소 한 개의 domain-neutral test function과 서로 다른 두 Domain Package fixture로 다음 전체 chain을 검증한다.

```text
Domain Policy explicit admin input
→ function card validation
→ build-time registry exact attestation
→ active package
→ bounded candidate
→ Intent operation_refs
→ registered_call Typed IR
→ Registered Function Gateway
→ output schema·lineage validator
```

Positive case는 같은 입력에서 동일 result/lineage/hash를 반복 생성해야 한다. Negative case는 unknown function/version, implementation/registry/I/O schema hash mismatch, required field/role 누락, 허용되지 않은 argument binding, timeout/row-limit, output extra/missing/type mismatch를 각각 fail-closed로 확인한다. 모든 negative case에서 dynamic import, `eval`/`exec`, network/file/subprocess, 다른 함수나 built-in operator fallback 호출 수는 0이어야 한다. Descriptor가 UI/metadata에만 있고 candidate/Intent/plan/Gateway consumer가 없으면 gate 실패다.

## 4. 가장 먼저 차단할 P0 질문

| Case | 필수 판정 |
| --- | --- |
| 6/27 W/B 생산 + BOH | `production/D`, `wip/D-1`, 두 metric lineage |
| INPUT 있음 + DA WIP 없음 | anti-join 결과만, 일반 left join 전체 금지 |
| Target plan MODE/Mode | source boundary canonical `MODE`, duplicate 금지 |
| DA top 3 → equipment | 이전 3행 left 보존, count/list, suffix 금지 |
| Mobile → POP | 조건 교체, 이전 Mobile row 오용 금지 |
| HOLD → history | LOT_ID required-param binding |
| W/BM | WB/BM substring over-expansion 금지 |

## 5. W/BM alias 검증

Candidate Selector만 production `bounded_longest` matcher를 실행한다. Validator는 matcher를 다시 구현·실행하지 않고 case oracle의 exact candidate ID, matched source span, match-rule ID와 selector output을 비교한다.

Intent provider payload는 recursive closed schema로 검증한다. 모든 `*_refs[]`에는 `candidate_id`와 `target_slots`만 허용하고, raw `field/operator/value/values/N/join_key/formula`, root/nested extra property, provider가 만든 bundle hash는 모두 거부한다. Decoder가 trusted `resolved.candidate.bundle.v1` hash를 normalized intent에 부착하며 compiler는 exact same bundle만 소비한다. Negative fixture는 없는 candidate ID, semantics/metadata/operator hash mismatch, incompatible target slot까지 포함하고 모두 retrieval 전에 `intent_contract_error`여야 한다.

필수 cases:

- `W/BM` → 정확히 W/BM
- `WBM` → metadata alias가 있을 때 정확히 W/BM
- `WB` → WB group
- `W/B` → WB group
- `BM` → BM 또는 등록된 단일/group

`W/BM` 내부 substring `W/B`를 먼저 매칭하지 않는다.

## 6. Multi-turn

### MT-1

- top 3 product
- equipment enrich
- previous result top 1 transform
- independent WB top 5 reset

### MT-2

- current HOLD LOT
- 선행 current HOLD 결과의 전체 `LOT_ID` set을 stable sort/dedupe해 hold_history에 deterministic chunk로 전달
- current LOT 전체의 history coverage와 canonical `HOLD_EVENT_AT` parse 확인
- LOT별 최신 `HOLD_EVENT_AT`을 `CURRENT_HOLD_STARTED_AT`으로 derive
- current hold start 오름차순, `LOT_ID` 오름차순 tie-break로 하나 선택하고 그 LOT의 전체 history 반환
- `OPER_IN_TM`/`FAC_IN_TIME` 대체, 일부 LOT 누락, 임의 first row, LLM 재선택 금지

### MT-3

- process-level production/WIP
- saved source 범위로 product regroup
- WB filter 유지

### MT-4

- Mobile PKG OUT
- POP으로 product filter만 교체
- fixture/runtime의 `source_snapshot.coverage`가 inherited date/process/grain, 필요한 fields와 POP을 모두 포함하면 `previous_source_transform`, 신규 조회 0
- POP이 제외됐거나 coverage가 unknown/incomplete면 `followup_requery`, production 조회 정확히 1
- 두 coverage fixture를 모두 검증하며 각 fixture는 한 mode만 exact oracle로 허용

### MT-5

- top 5 product
- previous result만 top 1

모든 turn은 generic “status ok”가 아니라 scenario-specific oracle을 가진다.

추가 follow-up contract:

- source expand는 complete coverage면 `previous_source_transform`, 불완전하면 `followup_requery`
- “왜 이렇게 나왔어/조건을 보여줘”는 `explain_previous`, retrieval/execution 0, 이전 lineage/operator trace만 설명
- next-question suggestion은 최대 3개이며 Message와 GaiA metadata에서 같은 ID/text를 사용

## 7. Answer grounding

검증 항목:

- 답변의 모든 숫자가 `answer.facts.v1`에 존재
- 가장 많음/적음 주장과 ordering 일치
- 날짜 표현이 requested/query date를 혼동하지 않음
- dummy/live notice 유지
- empty/error를 성공값처럼 표현하지 않음
- 결과 표는 canonical result와 동일

답변 문구의 표현 차이는 허용한다.

### 7.1 v5 표시와 output 호환

- `v5_shipped_compat`: result table/intent/execution plan on, preview 10, 나머지 배포 기본 토글 exact match
- `include_diagnostics=true`의 intent/retrieval/execution-plan master OR와 false일 때 child 개별값
- 각 Message 토글 on/off에서 section visibility만 바뀌고 canonical response/API result/data/state와 GaiA answer/metadata는 동일
- `show_pandas_code`는 pandas code가 아니라 typed Execution IR 표시 alias
- `answer.sections.v1`: summary/table descriptor/criteria/evidence/notices/downloads/next questions
- table descriptor가 preview row를 복제하지 않음
- v5 API wire key `request/intent_plan/analysis/data/data_refs/state/trace`, `data.rows`, `data_refs[]` 유지
- result/source CSV ref/URL은 owner/session/expiry/content hash를 가짐
- Message, API `Data(is_output=True)`, GaiA answer/URL/follow-up/trace/usage 모두 존재
- `24 채팅 메시지 표시 설정`은 유효한 `response.v1` schema를 표시하고 top-level response hash mismatch를 presentation 오류로 만들지 않음
- `24·25·26`은 수신 `response_sha256`을 요구하거나 비교하지 않고 일반 JSON 응답을 처리
- MongoDB result store의 결과 및 source snapshot `content_sha256` 검증은 유지
- deterministic intent 진단은 LLM 분석으로 표시하지 않고 route/reason/selected candidate와 `intent_llm_calls=0`을 유지
- result/source store → state CAS → runtime release → output fan-out 순서
- Message body를 API/GaiA가 역파싱하지 않음

## 8. Report 판독

최소 top-level:

```json
{
  "run_manifest": {},
  "summary": {
    "route_counts": {"deterministic": 0, "intent_llm": 0, "unsupported": 0},
    "route_mismatches": 0,
    "unexpected_llm_calls": 0,
    "fallback_violations": 0,
    "first_pass_ok": 0,
    "retry_ok": 0,
    "transport_failures": 0,
    "semantic_failures": 0,
    "execution_failures": 0,
    "answer_failures": 0
  },
  "cases": []
}
```

Retry 성공을 first-pass 성공에 합치지 않는다.

Unsupported telemetry report는 normalized shape/missing capability/version/count만 포함해야 한다. raw row, secret, query, prompt 또는 raw LLM output이 있으면 evidence 자체를 실패 처리한다. reviewed promotion은 metadata recipe/formula/operator와 새 canonical regression case가 함께 연결돼야 한다.

### 8.1 자유형 작업자 입력 변형 실검증

기본 `metadata/authoring/v6_inputs` 외에 제목·bullet이 없고 자료 순서와 말투를 다시 쓴 `validation/fixtures/authoring/freeform_reordered_v1` corpus를 같은 4개 authoring Flow에 넣는다. 이 fixture는 별도 문법을 만드는 것이 아니라 제목·순서 의존성을 검출하기 위한 두 번째 자연어 표본이다.

```powershell
.venv\Scripts\python.exe tools\validate_langflow_http_authoring_e2e.py `
  --worker-input-dir validation\fixtures\authoring\freeform_reordered_v1 `
  --source-set-id manufacturing_freeform_reordered_v1 `
  --environment v6_freeform_reordered_validation `
  --output validation_outputs\langflow_http_authoring_freeform_reordered_current.json
```

Report에는 source-set ID, 경로, 원문 SHA-256, byte/line/paragraph/heading/bullet 수와 style hash만 남긴다. 원문, Prompt, provider 응답, credential은 저장하지 않는다. `status=needs_clarification`은 안전한 정상 분기지만 성공 fixture의 통과로 계산하지 않으며, 작업자 문장을 JSON·ID 목록·고정 제목 형식으로 고쳐서 우회해서는 안 된다.

2026-08-02 최종 run에서는 기본 corpus와 이 재작성 corpus가 모두 exact `gemini-3.5-flash-lite`, 4개 authoring cycle, draft 5회, annotation/repair/fallback 0회로 통과했다. 현재 evidence는 각각 `langflow_http_migration_current.json`과 `langflow_http_authoring_freeform_reordered_current.json`이다.

### 8.2 승인 Source Registry와 자연어 별칭 gate

- `metadata/domain_packs/manufacturing/approved_source_registry.json`은 동일 폴더의 `approved_source_registry.sha256`과 파일 byte SHA-256이 exact여야 한다.
- registry 내부 self-hash만으로 trust를 주장하지 않는다. 임시 재빌드 결과, checked-in file, 독립 pin을 세 방향으로 비교한다.
- 자연어 별칭은 Domain/Dataset/Main Filter 세 작업자 TXT 중 하나에 정규화된 표현이 실제로 있어야 한다.
- 승인 baseline과 다른 target을 가리키거나 여러 신규 target에 동시에 제안된 표현은 compiler가 저장 전에 제거한다.
- 저장 결과의 delta는 priority 100, registered target, baseline preserved, additive-only, normalized label unique를 모두 만족해야 한다.
- report에는 별칭 원문이나 TXT를 넣지 않고 count와 canonical hash만 남긴다.

### 8.3 로컬 Langflow 1.9.2 실행 인증

운영 API key가 있으면 검증기는 `/api/v1/run/{flow}`를 사용한다. 격리된 로컬 서버가 auto-login Bearer만 제공하면 `/api/v1/run/session/{flow}`를 사용하며, Langflow 1.9.2 서버를 `LANGFLOW_AGENTIC_EXPERIENCE=true`로 시작해야 한다. Flow 업로드와 실행 사용자가 달라 생기는 403을 모델 실패로 분류하지 않는다.

MongoDB SRV `_resolve_uri`가 장시간 실행 프로세스에서 반복되지만 같은 URI의 새 프로세스 ping이 성공하면, 검증된 v6 Langflow 프로세스만 재시작하고 새 격리 environment에서 전체 run을 다시 수행한다. 성공한 일부 cycle을 이어 붙이거나 Python 결과를 실제 HTTP 결과로 표기하지 않는다.

## 9. 완료 판정

- deterministic corpus 100%
- expected route/reason/call count 100%, unexpected provider call과 automatic fallback 0
- model conformance 2개 이상 모델, `intent_llm` subset 각 3회
- 각 모델·각 run의 `intent_llm` case exact semantic oracle 100%, deterministic/unsupported case provider 호출 0
- plan/result repeat invariant
- repair/code LLM 호출 0
- typed operator flexibility matrix 100%
- v5 Message/API/GaiA output compatibility matrix 100%
- live source 9 dataset smoke
- Oracle/H-API/Datalake/Goodocs/Dummy adapter contract/security fixture
- Python 3.12.x와 exact package tuple
- 정확히 4개 MVP Flow import와 Data Analysis Chat/API/GaiA gate
- 재생성 manifest의 physical standalone source/node/edge count와 모든 Flow custom-node source instance parity
- Full-domain 자유형 TXT→closed full draft→deterministic compile gate, Dataset/Main Filter section ownership, Domain Policy prompt/envelope/provider 0회, optional explicit-inventory/Blueprint annotation-only profile
- 제목·bullet 없는 수동 재작성 자유형 corpus까지 실제 Langflow authoring HTTP에서 성공하고, 모호한 입력은 repair나 임의 저장 없이 `needs_clarification`으로 종료
- Runtime과 authoring의 고정 공통·특화 Prompt pair, 직접 작성된 특화 본문, 빈 변수 집합과 단일 runtime-context edge
- registered function descriptor→registry→candidate→Intent→`registered_call`→Gateway→output/lineage positive·negative E2E
- 4개 Flow의 사용자 가시 한글 이름/설명/input `info`/output 설명과 역할별 Sticky Note 정적·import 검증
- exploration runtime/Flow/edge 0; future schema는 disabled namespace로만 존재
- full pytest exit 0과 machine-readable evidence
- authoritative evidence manifest 생성

실제 구현 후 command는 [V6_IMPLEMENTATION_GUIDE.md](V6_IMPLEMENTATION_GUIDE.md)의 planned tool surface를 사용한다.
