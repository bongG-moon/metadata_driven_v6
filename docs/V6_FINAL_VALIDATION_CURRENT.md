# metadata_driven_v6 최종 검증 결과

검증일: 2026-08-02  
기준 구현: Langflow 1.9.2 / Python 3.12  
실제 등록 모델: `gemini-3.5-flash-lite`

## 1. 최종 판정

현재 5개 Flow와 import-ready bundle은 구현·동기화·실행 검증을 통과했다.

- 작업자 입력은 JSON, DSL, canonical ID 목록 또는 Markdown 제목을 요구하지 않는다.
- Gemini는 자유형 문장을 closed typed proposal로 바꾸는 역할만 맡는다.
- 승인 Source Registry, compiler, typed Execution IR executor가 실행 정확성을 책임진다.
- pandas code 생성 LLM과 repair LLM은 기본 경로에서 0회다.
- Runtime Intent/Answer와 Domain/Dataset/Main Filter authoring의 공통·특화 Prompt는 외부 Prompt Template node로 분리되어 있다. 특화 규칙은 각 특화 Template 본문에 직접 작성하고 runtime context는 Composer에 한 번만 연결한다. Domain Policy의 prompt extension·등록 함수·출력 정책은 별도 관리자 입력으로 관리한다.
- Message 표시 항목 선택, structured API, GaiA, CSV ref와 멀티턴 상태 계약을 유지한다.
- Data Analysis node는 `00`~`27`, 네 등록 Flow는 각자의 `00` 입력부터 최종 출력까지 순서형 한국어 표시명을 사용한다. 병렬 입력·Prompt·출력만 `A/B/C`로 구분하며 도메인 초기 등록의 반복 노드는 담당 분기명까지 표시한다. Metadata loader는 MongoDB URI·database·timeout만 받아 고정 3컬렉션의 최신 완전 release를 자동 결합하고, Request는 기준시각·시간대 UI 없이 `Asia/Seoul`로 고정한다.
- Dummy/Oracle/H-API/Datalake/Goodocs 조회 node는 분리돼 있고 실제 source node의 운영 조절값은 조회 행 수 제한뿐이다. 23→24·25·26은 전송용 hash가 없는 일반 JSON을 전달하며 출력 adapter는 수신 hash나 전체 응답 schema를 재검증하지 않는다.

## 2. Flow 구성

| Flow | 목적 | 노드 / 엣지 | 최종 SHA-256 |
| --- | --- | ---: | --- |
| 신뢰형 데이터 분석 | route → intent → typed plan → source별 retrieval → deterministic execution → output/state | 35 / 46 | `0aef0d77152f9feec80b5f2caac3892c8ac591bc24ec1ad280527f3aac184673` |
| 도메인 등록 | 세 자유형 TXT bootstrap, compile, `save|validate_only` | 26 / 35 | `1bf5fe590c9af2eb58b433e8558832e2a3d9505b19cc7fded48b76ab767ee7eb` |
| 데이터셋 카탈로그 등록 | current package의 dataset 소유 구간 patch | 13 / 13 | `772606191ee0f016cd9de98726bafbedef519bdfea3072bf150b512f8f9c6e63` |
| 기본 필터 등록 | 승인 대상에 대한 자연어 별칭 patch | 13 / 13 | `bbedc16382df22b59e4e5678fc033f7cf7ceda8947ddc1cae32b382d2eb9e7db` |
| 도메인 정책 등록 | 특화 Prompt, 등록 함수, 출력 profile의 관리자 입력 | 7 / 5 | `56adcb0079a556090e0c1aa4cdbc1602f33a5eed09eb7e667fdcc02c92a7e328` |

검증 결과는 5개 Flow, 3개 artifact layer의 custom-node instance 168개, 고유 component source 27개, source export node template 86/86 parse, import 5/5다. 모든 custom component는 runtime sibling import가 없는 standalone source다.

## 3. 작업자 자유형 TXT 계약

엄격한 것은 작업자 TXT가 아니라 LLM 출력과 compiler 입력이다.

1. 작업자는 평소 표현으로 Domain, Dataset, Main Filter 내용을 적는다.
2. 외부 공통·특화 Prompt pair와 Gemini가 작은 closed proposal을 생성한다. 특화 본문은 작업자 TXT나 metadata로 동적으로 바뀌지 않는다.
3. compiler가 승인 레지스트리의 dataset, physical column, semantic type, role, adapter/config/query binding을 결합한다.
4. 불충분하거나 모호하면 후보와 저장 없이 `needs_clarification`을 반환한다.
5. 승인 별칭을 침범하거나 서로 다른 대상에 중복되는 자연어 별칭은 저장 전에 결정론적으로 제거한다.

두 corpus를 실제 Langflow HTTP에서 검증했다.

| corpus | 문서 형태 | 실제 결과 |
| --- | --- | --- |
| `metadata/authoring/v6_inputs` | 현장 입력 예시 | authoring 4/4, revision 0→4 |
| `validation/fixtures/authoring/freeform_reordered_v1` | 제목 0, bullet 0, numbered line 0, 문단 순서·말투 재작성 | authoring 4/4, revision 0→4 |

재작성 corpus의 문단 수는 Domain 14, Dataset 12, Main Filter 6, Domain Policy 10이다. 두 실제 run 모두 exact model, draft LLM 5회, annotation 0회, repair 0회, fallback 0이며 원문·Prompt·provider 응답은 report에 저장하지 않았다.

## 4. 승인 레지스트리와 별칭 안전성

승인 Source Registry v3 파일은 독립 sidecar로 고정한다.

- registry file SHA-256: `2bbafd584fad0ed6e4aa312164880b4545e05a309a90dafc80d99fc2c164d310`
- dataset template SHA-256: `597d689fcfb662c71a33a0f26e45292feb3a3d60312e95b2101e956380fca4d4`
- 재빌드 파일, checked-in 파일, sidecar pin: exact match
- inventory: dataset 10, field 47, metric 17, recipe 10, entity group 25, predicate 7

실제 최종 package의 오라클 검사는 registry dataset binding, compiler derived fields, section hash/count, display annotation, Domain Policy overlay를 모두 exact로 통과했다. 자연어 별칭 증분은 source-grounded, priority 100, closed shape, registered target, baseline preserved, additive only, normalized label unique를 모두 통과했다.

## 5. 조회 유연성과 분기

동일한 typed executor가 다음 조합을 처리한다.

- 지정 컬럼 projection과 순서
- 문자열·숫자·날짜·null 필터와 all/any 조건
- group aggregate, formula, scalar min/max
- 전역/그룹별 상위·하위 N, tie 정책, argmax/argmin 행
- inner/left/right/outer/semi/anti join과 cardinality 정책
- 컬럼 간 비교, 중복 그룹, detail/history, 존재·부재 비교
- 등록된 격리 함수의 `registered_call`

canonical 70개 질문은 65 deterministic, 3 Intent LLM, 2 unsupported로 분기되며 70/70 통과했다. 주문·매출 범용 도메인 component case는 19/19를 통과했다. 지원 정보가 metadata에 없으면 pandas 생성으로 우회하지 않고 clarification 또는 `unsupported_operation`으로 종료한다.

## 6. Langflow 동일 흐름 + Gemini + MongoDB E2E

최신 evidence는 `validation_outputs/three_collection_live_validation.json`과 `validation_outputs/v6_simplified_flow_validation.json`이다.

- model: exact `gemini-3.5-flash-lite`, temperature 0
- 자유형 Domain/Dataset/Main Filter TXT를 각각 standalone authoring component 순서로 변환
- draft / annotation / repair calls: 3 / 0 / 0
- provider/model fallback: 0
- validation DB: `datagov_v6_validation`
- 저장 대상: `agent_v6_domain_metadata`, `agent_v6_table_catalog`, `agent_v6_main_filter`
- 저장 결과: 자연어 원문 3/3 보존, 동일 release 1개, revision 2
- selector 없는 loader 입력: `mongo_uri`, `mongo_database`, `mongo_timeout_ms`
- loader의 source/section/document/package hash와 identity/revision 검증: 모두 통과
- Data Analysis 동일 component 흐름: canonical 70/70, 주문·매출 범용 case, multi-turn·owner/session 격리 통과
- pandas code / pandas repair LLM: 0
- 채팅 Message는 표시 schema만 검증하고, API/GaiA 외부 경계의 response hash 검증은 유지

실제 Flow JSON은 Langflow 1.9.2 조합에서 5/5 import 구조와 실행 node template 86/86 parse를 검증했다. 실제 등록은 동일한 standalone component와 edge 순서를 Python harness에서 실행했으며, 이 방식은 Langflow 서버를 직접 기동하기 어려울 때 허용한 검증 경로다.

## 7. 회귀·생성물 검증

| 검증 | 결과 | evidence |
| --- | ---: | --- |
| 전체 pytest | 476/476, failure/error/skip 0 | `validation_outputs/pytest_v6_current.xml` |
| generated artifacts | 41/41 current | `generate_contracts_and_cases.py --check` |
| standalone components | 25/25 current | `build_standalone_components.py --check` |
| Flow source parity | 168 instance / 27 unique, error 0 | `validation_outputs/flow_component_sources_current.json` |
| exact Langflow runtime | Python 3.12.13, 1.9.2 / 0.9.2 / 0.4.2, 5개 Flow·86/86 template parse | `validation_outputs/langflow_runtime_current.json` |
| Python 동등 분석 흐름 | 70/70, order-sales, multi-turn 모두 통과 | `validation_outputs/v6_simplified_flow_validation.json` |
| 비정형 실제 authoring | 4/4, exact Gemini, repair 0 | `validation_outputs/langflow_http_authoring_freeform_reordered_current.json` |
| 3컬렉션 실제 등록 | exact Gemini 3회, fallback/repair 0, revision 2, loader 통과 | `validation_outputs/three_collection_live_validation.json` |

## 8. 재현 명령

```powershell
.venv\Scripts\python.exe -m pytest --junitxml validation_outputs\pytest_v6_current.xml -q
.venv\Scripts\python.exe tools\generate_contracts_and_cases.py --check
.venv\Scripts\python.exe tools\build_standalone_components.py --check
.venv\Scripts\python.exe tools\validate_flow_component_sources.py --output validation_outputs\flow_component_sources_current.json
.venv\Scripts\python.exe tools\validate_langflow_runtime.py --all-flows --strict-versions --server-url http://127.0.0.1:7873 --output validation_outputs\langflow_runtime_current.json
.venv\Scripts\python.exe tools\validate_langflow_equivalent_pipeline.py --execute-cases --execute-components --execute-order-sales --execute-multiturn --output validation_outputs\langflow_equivalent_pipeline_current.json
.venv\Scripts\python.exe tools\validate_langflow_http_authoring_e2e.py --server-url http://127.0.0.1:7873 --env-file .env --environment v6_release_pass --timeout-seconds 600 --output validation_outputs\langflow_http_authoring_e2e.json
.venv\Scripts\python.exe tools\validate_langflow_http_authoring_e2e.py --server-url http://127.0.0.1:7873 --env-file .env --worker-input-dir validation\fixtures\authoring\freeform_reordered_v1 --source-set-id manufacturing_freeform_reordered_v1 --environment v6_freeform_final --timeout-seconds 600 --output validation_outputs\langflow_http_authoring_freeform_reordered_current.json
```

과거 4-Flow 수치는 [V6_FINAL_VALIDATION.md](V6_FINAL_VALIDATION.md)에 historical baseline으로 남긴다.
