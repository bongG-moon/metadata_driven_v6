# v5 Rebuild Evidence

- 확인일: 2026-07-31
- 대상: `C:\Users\qkekt\Desktop\metadata_driven_v5`
- 목적: v6 구현 중 v5의 과거 성공 보고서나 현재 문서가 실제 현재 source와 동일하다고 오해하지 않도록 기준선을 남긴다.

## 1. Git 기준선

- branch: `main`
- HEAD / `origin/main`: `bb6df1a`
- tracked content는 `f5a2a79`와 diff가 없다.
- `a65732a Standardize pandas source columns`는 `3598122`에서 revert됐다.
- `c909330 Enforce presence comparison execution contracts`는 `bb6df1a`에서 revert됐다.
- `validation_outputs` 아래 실제 LLM report와 pytest temp 폴더는 다수 untracked다.

따라서 v5 문서에 “presence 실행 계약 구현 완료”, “표준키 실행 전환 완료”라고 적혀 있어도 현재 source 사실로 사용하지 않는다.

## 2. 현재 Flow 구조

`flow_exports/data_analysis_flow_v5_standalone.json`:

- 46 nodes
- 71 edges
- `last_tested_version=1.9.2`

논리 순서:

```text
Input/State
→ Metadata loaders/candidate builder
→ Intent Prompt/LLM
→ Intent Normalizer/Hydrator/Validator
→ Source Router/Retrievers/Merger
→ Pandas Prompt/LLM
→ Executor/conditional Repair LLM
→ Result Store
→ Answer Prompt/LLM
→ State/Response/Cleanup
```

Builder의 node/LLM registry는 `tools/build_v5_data_analysis_flow.py`에 있다.

## 3. LLM과 prompt 기준선

정상 호출:

1. Intent plan
2. Pandas code
3. Answer

Pandas 실행 오류 시 executor 내부에서 repair model을 호출하므로 최대 4회다.

정적 prompt:

| Prompt | Bytes |
| --- | ---: |
| Intent | 41,200 |
| Pandas | 29,262 |
| Repair | 18,544 |
| Answer | 5,986 |
| 합계 | 94,992 |

과거 Gemini report에서 intent prompt는 약 54K~62K chars, pandas prompt는 약 16K~44K chars, answer prompt는 약 7K~9K chars였다.

## 4. 구조적 실패 근거

### 4.1 BOH 생산/WIP

관찰된 변동:

- production만 사용
- WIP metric을 production 값에서 복사
- production dataset 대신 equipment dataset 선택
- WIP query date가 requested date와 동일
- D-1 temporal contract 적용 후 source schema/filter preamble에서 `OPER_NAME` 미발견

의미 선택부터 code까지 LLM이 소유하고 normalizer가 사후 보정했기 때문에 한 단계 수정이 다음 단계의 assumptions와 충돌했다.

### 4.2 Canonical/physical column

v5는 Main Filter canonical key와 Table Catalog mapping을 갖고도 plan, preamble, generated pandas code, output contract에서 canonical/physical 이름을 섞어 사용했다.

관찰된 오류:

- `DEN/DENSITY`
- `PKG_TYPE1/PKG1`
- `PKG_TYPE2/PKG2`
- `OPER_NAME/OPER_NM`
- `MODE/Mode`

마지막 `MODE/Mode` 수정은 standardization commit과 revert로 이어졌다. v6는 source boundary 1회 canonicalization 외의 mapping을 금지한다.

### 4.3 Presence

Prompt는 `compare_presence`와 anti-join을 요구했지만 current deterministic executor는 이 operation을 일반 경로에서 강제하지 않는다. generated pandas code가 단순 left join을 반환해도 설명은 존재·부재 조건을 만족했다고 말할 수 있었다.

Presence deterministic implementation은 commit 후 revert됐다. v6는 typed `presence_filter`가 없으면 해당 질문을 실행하지 않는다.

### 4.4 Result duplicate

관찰 예:

- `D/A공정 재공수량`
- `재공수량`

같은 값·의미가 이름만 달라 함께 표시됐다. 이름/값 비교가 아니라 metric lineage signature와 exact result contract로 해결해야 한다.

### 4.5 Follow-up

관찰된 변동:

- 이전 result/source data가 비어 있음
- `previous_result_transform`인데 신규 retrieval을 함께 생성
- `reference_mode=none`
- row-match identity 누락
- equipment enrich에서 pandas code 누락
- Mobile→POP에서 이전 Mobile 결과를 잘못 재사용

v6 state는 heuristic summary가 아니라 exact `executed_result_contract`를 저장한다.

## 5. Validation evidence 판독

### Deterministic fixture

`tools/validate_representative_questions.py` 기본 경로는 predefined intent plan과 pandas code를 주입한다. 30/30은 해당 fixture/executor 경로의 증거다.

### Real LLM

과거 snapshot:

- single/date final report: 34/36
- transient timeout/503와 semantic failure가 혼재
- 한 WBM case는 validator substring false positive
- explicit-date W/BM case는 실제 `W/BM + B/M` over-expansion

이 report는 현재 HEAD를 재검증한 것이 아니다.

### Multi-turn

- MT-1 validator가 가장 상세하지만 deterministic execution에서 LLM code가 비어 있는 정상 case도 실패로 봤다.
- MT-2~MT-5는 같은 수준의 scenario-specific oracle이 없었다.
- MT-1 전체 turn과 MT-5는 최신 authoritative evidence가 없다.

## 6. v5 사용자 기능 호환 기준

v6에서 pandas code 경로를 제거하더라도 다음 surface는 제거하지 않는다.

### 분석 표현 범위

`02_intent_variables_builder.py`와 intent prompt는 filter, group/aggregate, sort/top-N, join, presence, group attribute 비교, duplicate group, row-match group, registered function case를 표현했다. 실제 실행이 LLM pandas에 의존했다는 문제가 있었을 뿐, 사용자가 기대한 조합형 조회 범위는 v6 typed operator registry로 이전한다.

v6에는 특히 다음 generic contract를 명시적으로 둔다.

- 등록된 canonical field의 filter/group/project/sort/rank/compare
- global/per-group top·bottom N과 argmax/argmin tie policy
- top+bottom 결과 segment
- registered join recipe와 cardinality/null/multi-match policy
- generic two-column/group-attribute comparison과 duplicate group
- allowlisted formula AST, detail/history/row-match

### Message 표시 선택

`langflow_components/data_analysis_flow/21_answer_message_adapter.py`의 표시 기능을 유지한다.

- diagnostics
- result table와 preview row limit
- analysis evidence
- download links
- notices
- applied criteria
- next questions
- intent analysis
- data retrieval
- pandas code

배포 Flow JSON의 기본값은 diagnostics/evidence/download/notices/criteria/next questions/retrieval off, result table/intent/pandas-code section on, preview 10이었다. v6는 이를 `v5_shipped_compat` profile로 보존한다. 단 `show_pandas_code`는 typed Execution IR/operator trace를 보여 주는 `show_execution_plan` migration alias이며 pandas code는 생성하거나 노출하지 않는다.

### Structured output와 GaiA

- `20_answer_response_builder.py`: summary, result table descriptor, applied criteria, evidence, notices, downloads, next questions와 compact next-turn state
- `22_api_response_builder.py`: response type/status/stage/message/data mode/sections/request/intent/analysis/data/refs/state/trace를 가진 별도 structured output
- `23_mongodb_result_store.py`: TTL CSV result/source ref와 URL
- `01_gaia_output.py`: Message, GaiA answer, URL/follow-up metadata
- `24_runtime_payload_cleanup.py`: 저장·state 처리 후 full runtime payload 정리

v6는 계산 결과를 Message에만 넣지 않는다. 같은 immutable `response.v1`에서 Langflow Message, API Data terminal, GaiA answer/metadata를 fan-out하고 Message 표시 토글이 structured output을 지우지 못하게 한다.

### Multi-turn

v5가 제공하려던 previous result/source transform, follow-up requery, result enrich, independent reset, compact state를 유지한다. v6는 여기에 coverage 기반 source expand와 결과를 재계산하지 않는 explain/trace-only mode를 명시하고 owner/session-bound ref, TTL, CAS로 정확성을 강화한다.

## 7. v5에서 재사용 가능한 것

- exact Langflow 1.9.2 asset pinning/build pattern
- source-specific credential redaction과 read-only adapter behavior
- result/download TTL ref 개념
- GaiA input/output boundary
- source row buffer를 LLM control payload와 분리하려는 방향

## 8. 새로 구현해야 하는 것

- versioned metadata compiler
- dependency-closed candidate bundle
- small semantic intent schema
- deterministic plan compiler
- canonical source contract
- typed executor/operator registry
- metric lineage/result contract
- executed follow-up contract
- canonical validation manifest와 scenario oracles

v5의 `04_intent_plan_normalizer.py`, pandas prompt/code/repair 경로를 v6의 기반으로 복사하지 않는다.
