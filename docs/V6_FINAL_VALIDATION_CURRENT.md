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
- 공통/특화 Runtime Prompt는 외부 Prompt node로 분리되어 있고, Domain Policy의 특화 프롬프트·등록 함수·출력 정책도 외부 입력으로 관리한다.
- Message 표시 항목 선택, structured API, GaiA, CSV ref와 멀티턴 상태 계약을 유지한다.

## 2. Flow 구성

| Flow | 목적 | 노드 / 엣지 | 최종 SHA-256 |
| --- | --- | ---: | --- |
| 신뢰형 데이터 분석 | route → intent → typed plan → retrieval → deterministic execution → output/state | 33 / 42 | `0b8f8a078685448506557345928f413905ab259c003758fb834416fca7d794bd` |
| 도메인 등록 | 세 자유형 TXT bootstrap, compile, prepare/approve/execute | 23 / 32 | `ede31bdbd13d4df8014abf647fad69816f77b7b9ec8370b5308d94f501ce64b0` |
| 데이터셋 카탈로그 등록 | 활성 package의 dataset 소유 구간 patch | 12 / 12 | `4d1ded6087ece8f98354abd22e039acd1e5e7b83d193a22ef98ee3f6fb8a0106` |
| 기본 필터 등록 | 승인 대상에 대한 자연어 별칭 patch | 12 / 12 | `7ede44849a08448f92109e92d8a1b6c2ff89aa136056a2c3b851d0568b070091` |
| 도메인 정책 등록 | 특화 Prompt, 등록 함수, 출력 profile의 관리자 입력 | 7 / 5 | `f9834ffcc7c04cc1622045e788e28ced8ec8d42f6afe839f995c94091784aafc` |

검증 결과는 5개 Flow, custom-node instance 162개, 고유 component source 25개, node template 79/79 parse, import 5/5다. 모든 custom component는 runtime sibling import가 없는 standalone source다.

## 3. 작업자 자유형 TXT 계약

엄격한 것은 작업자 TXT가 아니라 LLM 출력과 compiler 입력이다.

1. 작업자는 평소 표현으로 Domain, Dataset, Main Filter 내용을 적는다.
2. 외부 공통 Prompt node와 Gemini가 작은 closed proposal을 생성한다.
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

## 6. 실제 Langflow + Gemini + MongoDB E2E

최신 evidence: `validation_outputs/langflow_http_migration_current.json`

- environment: `v6_release_pass_e3df1a7d`
- model: exact `gemini-3.5-flash-lite`
- authoring Flow import: 4
- authoring cycle: 4
- revision chain: 0 → 1 → 2 → 3 → 4
- draft / annotation / repair calls: 5 / 0 / 0
- provider/model fallback: 0
- 원문, provider output, approval payload, secret 저장: 0
- Data Analysis HTTP: 4/4
- 포함 경로: deterministic, Intent LLM 1회, authenticated multi-turn state 1→2
- pandas code / pandas repair / answer LLM: 0
- Message/API/GaiA terminal equivalence와 persistent result/state ref: 통과

로컬 검증 서버는 `.env`에 Langflow API key가 없을 때 auto-login Bearer와 `/api/v1/run/session`을 사용한다. Langflow 1.9.2에서 이 route는 `LANGFLOW_AGENTIC_EXPERIENCE=true`인 격리 검증 서버에서만 사용했다. 운영 서버의 API key가 있으면 기본 `/api/v1/run` 경로를 사용한다.

장시간 실행 중인 기존 서버에서 MongoDB SRV `_resolve_uri` 오류가 반복되었지만 새 Python 프로세스의 Mongo ping은 성공했다. 정확히 v6 검증 서버만 재시작한 뒤 실제 E2E가 통과했다. 이 오류는 LLM/typed IR 실패로 분류하지 않는다.

## 7. 회귀·생성물 검증

| 검증 | 결과 | evidence |
| --- | ---: | --- |
| 전체 pytest | 497/497, failure/error/skip 0 | `validation_outputs/pytest_v6_current.xml` |
| generated artifacts | 41/41 current | `generate_contracts_and_cases.py --check` |
| standalone components | 23/23 current | `build_standalone_components.py --check` |
| Flow source parity | 162 instance / 25 unique, error 0 | `validation_outputs/flow_component_sources_current.json` |
| exact Langflow runtime | Python 3.12.13, 1.9.2 / 0.9.2 / 0.4.2, 5/5 import | `validation_outputs/langflow_runtime_current.json` |
| Python 동등 분석 흐름 | 70/70, order-sales, multi-turn 모두 통과 | `validation_outputs/langflow_equivalent_pipeline_current.json` |
| 비정형 실제 authoring | 4/4, exact Gemini, repair 0 | `validation_outputs/langflow_http_authoring_freeform_reordered_current.json` |

## 8. 재현 명령

```powershell
.venv\Scripts\python.exe -m pytest --junitxml validation_outputs\pytest_v6_current.xml -q
.venv\Scripts\python.exe tools\generate_contracts_and_cases.py --check
.venv\Scripts\python.exe tools\build_standalone_components.py --check
.venv\Scripts\python.exe tools\validate_flow_component_sources.py --output validation_outputs\flow_component_sources_current.json
.venv\Scripts\python.exe tools\validate_langflow_runtime.py --all-flows --strict-versions --server-url http://127.0.0.1:7873 --output validation_outputs\langflow_runtime_current.json
.venv\Scripts\python.exe tools\validate_langflow_equivalent_pipeline.py --execute-cases --execute-components --execute-order-sales --execute-multiturn --output validation_outputs\langflow_equivalent_pipeline_current.json
.venv\Scripts\python.exe tools\validate_langflow_http_migration_patches_e2e.py --server-url http://127.0.0.1:7873 --env-file .env --environment-prefix v6_release_pass --timeout-seconds 600 --output validation_outputs\langflow_http_migration_current.json
.venv\Scripts\python.exe tools\validate_langflow_http_authoring_e2e.py --server-url http://127.0.0.1:7873 --env-file .env --worker-input-dir validation\fixtures\authoring\freeform_reordered_v1 --source-set-id manufacturing_freeform_reordered_v1 --environment v6_freeform_final --timeout-seconds 600 --output validation_outputs\langflow_http_authoring_freeform_reordered_current.json
```

과거 4-Flow 수치는 [V6_FINAL_VALIDATION.md](V6_FINAL_VALIDATION.md)에 historical baseline으로 남긴다.
