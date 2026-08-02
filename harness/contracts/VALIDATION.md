# Validation Contract

## 1. Canonical case source와 단계

질문 텍스트, expected intent, plan oracle, result oracle, 문서, runner 입력을 수동으로 여러 곳에 복제하지 않는다.

Phase 1 변환은 완료됐고 `validation/cases.jsonl`이 canonical machine-readable source다. 다음 두 문서는 provenance와 사람이 읽는 index로 유지되며 generator로 동기화한다.

- `validation/validation_questions.txt`
- `validation/ACCEPTANCE_MATRIX.md`

초기 migration에서 적용한 우선순위는 다음과 같다.

1. `validation_questions.txt`: question text, order, case/turn identity
2. `ACCEPTANCE_MATRIX.md`: v6 route/call-count/intent/plan/source/date/result invariant
3. v5 expected docs/fixture reports: dummy expected row/value를 옮기는 non-authoritative evidence

v5 evidence는 Phase 1 migration manifest에 path와 SHA-256을 먼저 고정한다. v5 값이 v6 fixed reference instant, canonical field, typed operator, source/date contract와 충돌하면 v6 contract가 우선하고 `migration_conflicts`에 기록한다. 어느 값이 맞는지 결정할 근거가 없으면 case 생성을 중단하고 사람 review를 요구한다. 여러 reviewer가 임의로 다른 v5 report를 고르지 않는다.

이 기준으로 생성한 `validation/cases.jsonl`은 case 누락, 중복, ID, turn 연결 검증을 통과했다. 현재 다음 항목은 JSONL에서 파생되는 생성물이다.

- `validation/validation_questions.txt`
- 사람이 읽는 acceptance matrix
- fixture runner inputs
- model conformance runner inputs
- route classification/call-count runner inputs
- multi-turn scenario definitions

질문·route·oracle을 변경할 때 사람이 TXT/Markdown 생성물만 직접 수정하는 것은 금지한다.

## 2. Validation profile

| Profile | LLM | Metadata | Retrieval | 목적 |
| --- | --- | --- | --- | --- |
| `contract_unit` | 없음 | fixture | fixture | route/compiler/operator 단위 계약 |
| `deterministic_e2e` | provider-call guard | compiled fixture | dummy | 실제 route gate→intent→plan→execution exact oracle |
| `model_conformance` | expected `intent_llm` case만 실제 | 실제 snapshot | dummy | 모델별 semantic intent 안정성; 다른 route는 비호출 검증 |
| `live_source_smoke` | route에 따라 실제/0회 | 실제 | read-only live | source contract와 schema |
| `langflow_import` | 설정 모델, route별 0/1회 | isolated snapshot | dummy/live subset | 실제 1.9.2 Flow 실행 |

모든 LLM profile은 [PROMPTS.md](PROMPTS.md)의 외부 prompt 계약을 사용한다. runtime component가 내부 prompt 또는 내부 retry 문구로 provider를 호출한 run은 의미 결과가 맞아도 실패다.

## 3. 필수 corpus

- 대표 단일 질문 30개
- 날짜 계약 질문 6개
- MT-1~MT-5 모든 turn
- metadata authoring round-trip cases
- 9개 dataset read-only smoke
- Oracle, H-API, Datalake, Goodocs, Dummy 5개 adapter-type contract/security fixture
- failure injection cases
- deterministic/intent_llm/unsupported route classification과 no-fallback cases
- deterministic intent와 LLM intent의 common-contract equivalence cases
- unsupported telemetry와 reviewed operator/recipe promotion cases

현재 corpus의 결정론적 실행과 model conformance는 다음 기준시각을 고정한다.

- reference instant: `2026-07-30T09:00:00+09:00`
- timezone: `Asia/Seoul`
- `오늘`: `2026-07-30`
- `어제`: `2026-07-29`

runner, case oracle, report manifest가 다른 기준시각 또는 시스템 로컬 timezone을 암묵적으로 사용하면 실패다. 이 고정 instant는 검증 harness의 주입 fixture다. 운영 `02 요청 및 세션 상태 고정` node에는 기준시각·시간대 UI input이 없으며 내부 현재 시각을 항상 `Asia/Seoul`로 해석한다.

## 4. Exact oracle

각 case는 해당 의미에 적용되는 다음 항목을 빠짐없이 명시한다. 항목이 적용되지 않으면 누락하지 말고 `not_applicable`과 이유를 기록한다.

- semantic intent IDs
- `expected_route=deterministic|intent_llm|unsupported`, exact route reason과 eligibility proof invariant
- expected Intent/Intent retry/Answer/code/repair LLM call count
- request scope/reference mode
- dataset/job count
- source별 required params
- source별 filter
- canonical field bindings
- operation DAG
- output metric lineage
- exact result columns/order
- expected rows 또는 invariant/control exclusion
- new retrieval 여부
- preserved/dropped/replaced condition
- expected error code

최종 자연어 문장 exact match는 요구하지 않는다. 모든 claim이 result fact에 근거하는지는 요구한다.

## 5. Deterministic gate

- 30/30 대표 질문 성공
- 6/6 날짜 질문 성공
- MT-1~MT-5 모든 turn 성공
- plan fingerprint와 result schema exact match
- no metric copy
- no silent source failure
- required source failure는 전체 error, declared optional-enrichment failure만 exact typed-null partial
- no undeclared output column
- deterministic operator 경로에서 `code_llm_calls=0`, `repair_llm_calls=0`
- 모든 case의 actual route/reason과 LLM call counter가 exact oracle과 일치
- `deterministic|unsupported` route의 provider 호출 0

### 5.1 Typed operator flexibility matrix

대표 30+6 corpus와 별도로 operator contract fixture를 모두 실행한다.

- canonical field projection과 column order
- filter `all/any`, string/null/numeric operator, v5 migration alias
- aggregate와 scalar min/max
- global/per-group top·bottom N
- exact-N, include-all-ties, metadata tie-break
- argmax/argmin row와 top+bottom `RESULT_GROUP/RESULT_RANK`
- ordered multi-key rank와 각 컬럼별 extrema `RESULT_METRIC/RESULT_RANK`
- 등록된 임의 두 컬럼 비교와 duplicate group
- inner/left/right/outer/semi/anti join의 0/1/N match
- join cardinality/null/duplicate/multi-match/empty-side/suffix policy
- formula AST type/rounding/zero-division
- detail, dedupe, history order, row-match group
- `registered_call`의 candidate selection, exact function/registry/schema hash, argument binding, standalone execution과 output lineage

각 fixture는 exact plan operation, result schema/order, rows 또는 invariant, notice/error를 가진다. 지원하지 않는 field role, join recipe, formula, operator는 retrieval 전 `unsupported_operation` 또는 명시적 clarification이어야 하며 free-form code fallback은 실패다.

`registered_call` matrix는 최소 다음을 포함한다.

- unique function application의 deterministic selection과 ambiguous application의 Intent LLM candidate-only selection
- function card→candidate→`operation_refs`→`registered_call` IR→Gateway→result/trace positive end-to-end
- registry missing, version/implementation/registry-entry/input/output schema hash mismatch의 package activation 또는 retrieval 전 fail-closed
- unregistered field/role, raw argument, output schema/grain/lineage mismatch negative case
- timeout, row/memory limit, network/file/subprocess attempt의 canonical error와 다른 function/pandas/LLM fallback 0
- 제조·주문/매출·고객지원의 서로 다른 function card가 같은 shared Flow/Gateway contract를 사용하고 공통 Python에 domain ID/field/value 예외 0

`ACCEPTANCE_MATRIX.md` §5의 모든 `OP-*` question shape는 prebuilt plan만 넣는 executor fixture로 끝내지 않는다. Phase 1 canonical case에 `expected_route`를 review해 포함하고 actual Candidate Selector → Route Eligibility Gate → Deterministic Intent Builder 또는 Intent LLM/Decoder → Common Intent Validator → Compiler → imported endpoint 경로를 통과시킨다. join 0/1/N match나 optional failure처럼 같은 질문의 data/policy variant는 semantic selection을 고정한 deterministic subfixture로 분리할 수 있다.

### 5.2 Route decision과 no-fallback gate

다음 route category를 모두 자연스러운 질문과 negative fixture로 검증한다.

| Category | 필수 oracle |
| --- | --- |
| `ROUTE-D` unique/complete | `deterministic`, Intent LLM 0, proof에 pin된 selection으로 common intent/plan 실행 |
| `ROUTE-L` semantic choice required | `intent_llm`, Intent LLM 1, candidate 밖 의미 생성 0 |
| `ROUTE-U` registry gap | `unsupported`, 모든 LLM/retrieval/executor/result-store/state-mutation 0, 이전 state 유지, canonical error와 telemetry counter 1 |
| `ROUTE-A` alias/conflict | deterministic 금지; reviewed oracle에 따라 `intent_llm` 또는 clarification, source 호출 0 until resolved |
| `ROUTE-F` post-selection failure | 선택한 route의 canonical error, 다른 route/LLM/pandas/exploration fallback 0 |
| `ROUTE-EQ` same semantic selection | 두 intent 생성 경로의 normalized intent hash, plan fingerprint, result schema/content hash 동일; route/usage trace 차이만 허용 |

Eligibility proof는 selected IDs, required/unresolved slots, ambiguity sets, bundle/policy hash로 재계산 가능해야 한다. 질문별 keyword branch, model confidence threshold, source row 관찰로 `deterministic`을 선택하면 실패다. 동일 request/bundle/state에서 model profile을 바꿔도 route와 proof hash가 바뀌면 실패다.

### 5.3 Unsupported telemetry와 promotion gate

- telemetry에는 normalized shape, missing capability ID, metadata/operator revision, count/time만 있고 row/secret/query/prompt/raw LLM output이 없어야 함
- 같은 unsupported request의 retry는 실행 기능을 자동 생성하지 않고 동일 error 의미를 유지
- promotion은 reviewed metadata recipe/formula/operator, policy semantics와 canonical regression case가 함께 추가된 경우에만 통과
- arbitrary pandas code나 exploration output을 trusted operator로 자동 승격하면 실패

## 6. Model conformance gate

primary model과 더 약하거나 다른 provider/model profile을 각각 temperature 0으로 3회 실행한다. 매 profile에서 전체 corpus를 imported endpoint로 보내되 실제 semantic model conformance 대상은 `expected_route=intent_llm` case다. `deterministic|unsupported` case는 provider가 호출되지 않았음을 검증한다.

필수 조건:

- normalized intent contract valid
- candidate 외 ID 생성 없음
- provider selection의 root/nested object가 recursive closed schema를 통과하고, decoder만 trusted resolved-candidate bundle hash를 부착
- plan fingerprint가 exact resolved-candidate bundle hash를 pin
- 각 모델의 각 3회 run에서 모든 필수 case가 route/call-count oracle과 일치하고, `intent_llm` case는 exact intent/plan/retrieval/result/error oracle과 일치
- 3회 plan fingerprint 동일
- 3회 result schema와 result rows/invariant 동일
- 30 single + 6 date + MT-1~MT-5 모든 turn + §5 모든 OP question shape가 매 endpoint run에서 expected route로 first-pass 성공
- pandas/code repair 호출 0
- transport failure와 semantic failure 별도 집계

세 run의 결과를 합쳐서 한 번이라도 맞은 값을 통과로 만들지 않는다. 서로 동일한 오답 fingerprint를 세 번 반환해도 실패다. transport failure는 semantic failure와 구분해 기록하지만 해당 run을 통과로 간주하거나 조용히 제외하지 않는다.

질문별 prompt 문구를 추가해서 한 모델만 맞추지 않는다. 실패가 alias/token boundary라면 candidate resolver를, schema 누락이라면 generic intent contract를, 실행 의미라면 compiler/operator를 수정한다.

### 6.1 Candidate-only negative gate

모델별 positive corpus와 별도로 다음 provider payload를 직접 주입한다. 모두 source retrieval 호출 수 0과 `intent_contract_error`를 반환해야 한다.

- root의 `dataset_key`, `source_alias`, `physical_column`, `pandas_code`
- 모든 `*_refs[]`의 `candidate_id`, `target_slots` 외 property와 특히 `filter_refs[]`의 `field`, `operator`, `value`, `values`
- provider가 직접 출력한 `resolved_candidate_bundle_sha256`
- resolved bundle에 없는 `candidate_id`
- bundle의 `semantics_sha256`/metadata/operator pin mismatch
- candidate의 applicable metric과 맞지 않는 `target_slots`

Validator는 Candidate Selector matcher를 다시 실행해 잘못된 payload를 보정하지 않는다. exact bundle membership/hash/schema만 검사하며, 실패한 field/operator/value를 prompt string이나 기본 operator로 복원하지 않는다.

### 6.2 External prompt gate

- Intent와 Answer마다 공통·특화 Prompt Template node가 정확히 한 개씩 있고 두 node의 ID/purpose/revision/template SHA-256/source/edge가 독립적인지 검사
- Domain/Dataset/Main Filter LLM 경로에도 작업별 공통·특화 Prompt Template node가 정확히 한 개씩 있고 ID/purpose/revision/template SHA-256/source/edge가 독립적인지 검사
- Domain 기본 lane은 문장 순서·말투·제목·표기가 다른 자유형 TXT bundle에서 full closed draft를 만들며 JSON·ID inventory·relation/field-role 문법·Blueprint/pin을 사용자에게 요구하지 않는지 검사
- 기본 예시와 별도로 Markdown 제목·bullet이 0개이고 문단 순서와 말투를 수동으로 바꾼 작업자 TXT corpus를 같은 imported Flow와 새 격리 environment에서 실행한다. 두 corpus 모두 exact model, source hash, closed proposal, compiler completeness, revision chain, loader round-trip을 통과해야 하며 원문·prompt·provider 응답은 evidence에 저장하지 않는다.
- 승인 Source Registry는 내부 self-hash 외에 독립 file SHA-256 sidecar pin과 exact match해야 하며, 임시 deterministic rebuild도 같은 byte hash를 재현해야 한다.
- 자연어 alias delta는 Domain/Dataset/Main Filter 원문 중 하나에 근거해야 하고 priority 100·registered target·baseline preserved·additive-only여야 한다. 승인 baseline의 다른 target을 침범하거나 정규화 후 여러 target에 중복되는 표현은 저장 전에 compiler가 제거하며 LLM repair로 보정하지 않는다.
- 최초 bootstrap source가 Domain·Dataset·Main Filter 원문 bundle 또는 동등하게 완전한 도메인 설명인지 확인하고, 정보 부족은 format error가 아니라 `status=needs_clarification`의 `missing_fields`/질문으로 반환하며 draft/candidate/persist가 없는지 검사
- `metadata.authoring.proposal.v1`의 `complete(source_sha256,draft)`와 `needs_clarification(source_sha256,clarification)` recursive closed variant를 검사하고 mixed/extra-key/wrong-source-hash proposal은 provider 재호출 없이 거부
- 제조 live bootstrap은 v6 전용 `domain_v6.txt`+`dataset_v6.txt`+`main_filter_v6.txt` bundle, exact `gemini-3.5-flash-lite`, temperature 0, fallback 0, repair 0을 검사
- runtime/authoring custom component source와 standalone generator에서 prompt builder와 LLM instruction literal이 0건인지 static scan
- Runtime/Authoring prompt pair 중 하나가 missing/empty이거나 purpose/revision/hash/placeholder/budget이 틀리면 provider 호출 0과 canonical error
- 모든 공통·특화 Prompt Template의 예상 변수는 빈 집합이고 특화 본문을 사용자 입력·metadata로 바꾸는 동적 port/edge가 없음을 검사
- 공통 prompt만 변경하면 특화 prompt와 component source hash가, 특화 prompt만 변경하면 공통 prompt와 component source hash가 동일하고 해당 prompt/Flow/manifest/composition hash만 변경
- Runtime/Authoring common=`system`, specialized=`domain_policy`, runtime context=`untrusted_data` named authority가 유지되고 port swap이 provider 호출 전에 실패
- question/candidate/facts/schema/source runtime context가 Prompt Template에 복제되지 않고 Composer의 별도 입력으로 한 번만 전달
- JSON syntax/schema 오류, candidate 밖 ID와 provider 오류 뒤 Intent/Answer/authoring 자동 retry 및 다른 모델 fallback 0
- prompt/LLM raw output이 state, result, trace, telemetry, error details에 없고 manifest에는 hash/revision/byte length만 존재
- raw source row, full metadata catalog, SQL/query, endpoint, credential, token을 prompt variable에 주입하는 negative fixture가 provider 호출 전에 실패
- deterministic, unsupported, narrative-off, optional explicit-inventory main-filter authoring과 Domain Policy는 provider 호출 0이며 zero-LLM path에서는 prompt envelope도 만들지 않음
- Intent/Answer/domain-authoring/dataset/main-filter의 허용 경로는 각각 provider 최대 1회
- optional `source_grounding_mode=explicit_inventory` profile에서만 exact inventory zero-LLM 또는 Blueprint/pin annotation-only gate를 적용하며, 기본 free-form run은 빈 Blueprint/pin으로 provider 전에 실패하지 않음
- public HTTP tweak로 공통·특화 Prompt Template 본문/pin과 model policy를 변경하려는 요청은 실행 전에 거부

## 7. Multi-turn gate

MT-1~MT-5 각각의 모든 turn에서 확인한다.

- 각 turn의 `expected_route`, route reason과 exact LLM call count
- `new_analysis`, `previous_result_transform`, `previous_source_transform`, `followup_requery`, `previous_result_enrich`, `explain_previous` 구분
- 신규 조회 여부
- 조건 상속/삭제/교체
- exact row-match grain/entity
- required param binding
- left-row preservation
- 독립 질문에서 state reset
- MongoDB save/restore/cleanup

MT-2는 선행 current HOLD 결과의 전체 `LOT_ID` set을 stable sort/dedupe해 `hold_history` required param에 deterministic chunk로 bind한다. 전체 LOT coverage를 확인한 뒤 LOT별 최신 canonical `HOLD_EVENT_AT`을 `CURRENT_HOLD_STARTED_AT`으로 derive하고, 그 값 오름차순과 `LOT_ID` 오름차순 tie-break로 LOT 하나를 고른다. 반환 결과는 이미 조회한 history 중 선택 LOT의 전체 이력이다. `OPER_IN_TM`/`FAC_IN_TIME` 대체, 일부 LOT만 조회, 임의 first row, LLM 재선택은 실패다.

MT-4의 mode는 case fixture의 `source_snapshot.coverage`와 runtime `executed.result.v1.source_snapshots[].coverage`로 정확히 결정한다.

- inherited date/process/grain, 필요한 canonical fields와 POP product 범위를 모두 포함하는 complete source면 `previous_source_transform`, 신규 조회 0
- POP 범위가 제외됐거나 coverage가 unknown/incomplete면 `followup_requery`, 필요한 production 조회 정확히 1

각 case는 둘 중 하나의 expected mode와 retrieval count를 oracle에 명시한다. 어느 쪽이든 허용하는 판정은 금지한다.

빈 결과만 반환하고 status가 ok라는 이유로 통과시키지 않는다.

### 7.1 Presentation/output compatibility gate

v5 사용자 기능이 계산 경로 변경으로 사라지지 않는지 별도 matrix로 검증한다.

- `v5_shipped_compat` 기본값 exact match: diagnostics/evidence/download/notices/criteria/next questions/retrieval off, result table/intent/execution plan on, preview 10
- diagnostics, result table, preview limit, evidence, download, notice, criteria, next questions, intent, retrieval, execution plan 토글을 각각 on/off
- `include_diagnostics=true`이면 intent/retrieval/execution plan 모두 true, false이면 세 child toggle 개별값; 다른 section에는 영향 0
- v5 `show_pandas_code` import 값이 code 생성 없이 `show_execution_plan`으로 정규화
- 채팅 표시는 `response.v1` schema만 검사하며 응답 hash mismatch를 presentation 오류로 만들지 않음
- 24·25·26 출력 경계는 `response_sha256`을 요구하거나 비교하지 않고 일반 JSON을 전달
- MongoDB result store의 결과·source snapshot `content_sha256` 검증은 계속 유지
- Message 표시 토글 전후 canonical `response.v1`, result/state ref와 GaiA answer/metadata hash 동일
- API의 bounded request/intent_plan/analysis/data/data_refs/state/trace key와 schema compatibility
- `answer.sections.v1`의 summary/result table descriptor/criteria/evidence/notices/downloads/next questions schema
- preview row가 v5 wire 위치 `response.data.rows`에 한 번만 존재하고 table section은 pointer만 보유
- CSV result/source download의 owner/session, expiry, content hash와 credential redaction
- Langflow Message, API `Data(is_output=True)`, GaiA answer/URL/follow-up/trace/validated usage output
- deterministic route의 intent 표시가 LLM 분석으로 위장되지 않고 route/reason/selected candidate를 표시하며, structured output에는 `intent_llm_calls=0`이 유지
- route가 달라도 canonical data/result/state/GaiA 의미는 유지되고 route/usage trace만 정당하게 다름
- result/source store → state CAS → runtime frame release → 세 terminal fan-out 순서
- follow-up suggestion 최대 3개와 explain/trace-only turn의 persisted criteria/lineage/facts/operator hash 검증, retrieval/executor 0

하나의 terminal이 실패해도 다른 terminal의 response를 다시 계산하지 않는다. Message 문자열을 API/GaiA adapter가 역파싱하면 실패다.

## 8. Fault injection과 canonical error registry

fault case는 자체 오류 문자열 namespace를 만들지 않는다. Phase 1에서 생성하는 중앙 `error_registry.v1`의 canonical code를 참조하고, [ARCHITECTURE.md](ARCHITECTURE.md)의 Error boundary와 동일한 의미를 유지한다. runner, component, API adapter가 같은 원인을 서로 다른 code로 번역하면 실패다. 아래 표는 registry에 등록할 초기 논리 code와 fault mapping이다.

| Fault | Expected |
| --- | --- |
| route object/schema/proof hash 불일치 | `route_contract_error` |
| Intent JSON/schema 또는 candidate ID 위반 | `intent_contract_error` |
| metadata dependency revision/hash 누락·불일치 | `metadata_dependency_error` |
| plan DAG/result contract 불완전 | `plan_contract_error` |
| required source missing | `source_missing` |
| 존재하는 source의 provider/transport 실패 | `source_retrieval_failed` |
| successful source 0 rows | `empty` 또는 valid zero policy |
| 동일 normalized alias가 서로 다른 identity에 같은 우선순위로 등록 | `ambiguous_alias` |
| canonical mapping 2개 동시 존재 | `ambiguous_field_binding` |
| required physical column 없음 | `source_schema_mismatch` |
| expected entity/time/filter source coverage 일부 누락 | `source_coverage_incomplete` |
| required param 없음 | `missing_required_param` |
| entity binding 값이 declared max_total_values 초과 | `parameter_value_limit_exceeded` |
| source timeout | `source_timeout` |
| source max-row 초과 | `source_row_limit_exceeded` |
| config/query ACL 거부 | `source_acl_denied` |
| registry에 없는 operation 요청 | `unsupported_operation` |
| operator estimate 또는 runtime peak가 node memory 상한 초과 | `execution_memory_limit_exceeded` |
| UPH sum 요청 | `metric_rollup_violation` |
| output metric lineage 누락·signature 불일치 | `metric_lineage_violation` |
| join key/cardinality 불완전 | `join_cardinality_violation` |
| extra result metric | `result_schema_violation` |
| answer가 없는 숫자 주장 | `answer_claim_violation` |
| expired follow-up ref | `state_reference_expired` |
| 다른 session/subject ref | `state_reference_forbidden` |
| stale state CAS write | `state_conflict` |
| metadata dependency bundle budget 초과 | `metadata_budget_exceeded` |
| 미승인 candidate execute | `approval_not_found` |
| 만료된 approval execute | `approval_expired` |
| candidate/approval hash 불일치 | `approval_hash_mismatch` |
| 이미 claim된 candidate를 다른 idempotency key로 execute | `approval_already_claimed` |
| prepare 이후 active/dependency revision 변경 | `stale_candidate` |

오류 payload는 최소한 `error_registry_version`, `error_id`, `code`, `stage`, `message`, `retryable`, `details`, `trace_id`를 포함한다. `source_job_id` 같은 stage별 정보는 `details`에 두며 원본 credential, query, row payload를 포함하지 않는다.

## 9. Source adapter gate

### 9.1 Adapter-type fixture와 security

live 배포 여부와 관계없이 Oracle, H-API, Datalake, Goodocs, Dummy 5개 adapter type 모두 contract fixture와 security gate를 통과해야 한다.

공통 contract fixture:

- typed required param validation
- physical-to-canonical schema binding
- success/empty/failure 구분과 canonical error mapping
- timeout, row/byte limit, provenance, coverage metadata
- Dummy와 동일한 canonical result contract
- Flow에는 `11 검증용 더미 데이터 조회`, `12 Oracle 데이터 조회`, `13 H-API 데이터 조회`, `14 Datalake 데이터 조회`, `15 Goodocs 데이터 조회`가 각각 하나씩 존재하고 job lane이 교차 연결되지 않음
- source payload는 연결 Data 계약으로만 받고, 운영자가 조절하는 source scalar input은 각 실제 source node의 `조회 행 수 제한` 하나뿐임

공통 security gate:

- 사용자 텍스트에서 임의 SQL, URL, collection/path, executable expression을 직접 만들지 않음
- 승인된 connection/query/job/document ID registry와 allowlist만 사용
- Oracle은 read-only query, H-API는 허용된 read method/endpoint, Datalake와 Goodocs는 read-only object/document operation만 허용
- Dummy는 network egress 0
- URI, credential, token, header, raw query가 Flow JSON, prompt, state/ref, trace, error, pytest/report artifact에 평문으로 없음
- timeout, TLS 검증, result size limit을 adapter contract에서 강제

### 9.2 Live dataset smoke

- `production_today`
- `production`
- `wip_today`
- `wip`
- `target`
- `equipment_assign`
- `eqp_uph`
- `lot_status`
- `hold_history`

각 dataset은 배포된 adapter type에서 read-only schema/row smoke를 가진다. 9개 live dataset이 5개 adapter type을 모두 사용하지 않더라도 9개 live smoke와 5개 adapter fixture는 둘 다 필수다. `hold_history`는 LOT_ID 없는 호출이 실패하는지, 선행 LOT_ID binding 호출은 성공하는지 모두 확인한다. Dummy와 live는 canonical schema parity를 가져야 한다.

## 10. Langflow/package gate

- Python `3.12.x`와 exact `langflow==1.9.2`, `langflow-base==0.9.2`, `lfx==0.4.2`가 아니면 실패
- lockfile과 installed distribution inventory hash 기록
- MVP Flow inventory logical key/`endpoint_name`은 정확히 다음 5개이며 누락, 중복, 예상 밖 여섯 번째 Flow가 있으면 실패
  - `metadata_v6_data_analysis`
  - `metadata_v6_domain_authoring`
  - `metadata_v6_dataset_catalog_authoring`
  - `metadata_v6_main_filter_authoring`
  - `metadata_v6_domain_policy_authoring`
- exploration flow/endpoint/worker는 초기 bundle에 없어야 하며 Data Analysis가 `exploration.*`를 자동 호출하는 edge/source가 있으면 실패
- 모든 Flow의 `last_tested_version=1.9.2`
- 모든 node의 `lf_version=1.9.2`
- 각 top-level Flow `id`가 `flow_inventory.json` fixed namespace와 logical key의 expected UUIDv5와 일치
- 모든 node template parse
- 모든 사용자 표시 Flow/node/input/output의 이름·description·input info·output 설명이 한국어 localization inventory와 일치하고 internal ID/port/schema key는 변경되지 않음
- Data Analysis와 네 authoring Flow의 필수 Sticky Note ID/content revision이 존재하고 `noteNode`/`data.type=note`, edge 0, execution node count 제외, secret/query/raw row/prompt 원문 0을 만족
- source/prompt/schema/export/import-ready parity
- isolated Langflow import
- imported `metadata_v6_data_analysis` dummy profile에서 30 single + 6 date + MT-1~MT-5 전체 corpus의 boundary output/exact oracle 실행
- imported Data Analysis에서 operator flexibility matrix와 Message/API/GaiA compatibility matrix 실행
- primary/secondary profile의 전체 route corpus와 `intent_llm` subset model conformance도 reference-runtime 직접 호출이 아니라 imported Data Analysis endpoint를 통해 각 3회 실행
- 네 authoring Flow 각각 immutable prepare와 승인 후 second-run atomic execute smoke. Domain Policy와 optional explicit-inventory Main Filter는 provider/envelope 0회
- full pytest suite exit code 0
- pytest의 JUnit XML 또는 동등한 machine-readable report와 console log를 evidence manifest에 연결
- unexpected skip/xfail, collection error, deselected mandatory case 0

## 11. Evidence manifest

각 run은 다음을 기록한다.

- git SHA와 dirty state
- manifest SHA
- component/prompt/schema hashes
- Flow hash
- model/provider/temperature
- reference date/timezone
- metadata counts와 snapshot IDs/hashes
- dummy seed 또는 live profile
- attempt number
- first-pass 결과와 모든 자동 retry call counter 0 assertion
- route/reason/proof hash별 count, expected/actual LLM call counter와 no-fallback assertion
- transport/semantic/execution/answer failure 분류
- unsupported capability별 bounded telemetry count와 reviewed promotion reference
- Python과 exact package tuple, lock/inventory hash
- pytest command, exit code, collected/passed/skipped/failed counts
- pytest machine-readable report와 console log의 path/hash
- 5개 MVP Flow inventory와 각 Flow hash
- Korean localization inventory hash와 Sticky Note inventory/content hash
- registered function registry/build manifest hash와 `registered_call` positive/negative matrix summary

가장 최근 report 하나를 authoritative manifest가 가리키며 임시 pytest 폴더를 evidence로 취급하지 않는다.
