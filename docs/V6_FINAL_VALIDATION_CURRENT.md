# metadata_driven_v6 현재 최종 검증 결과

검증일: 2026-08-03

기준 환경: Python 3.12.13 / Langflow 1.9.2 / langflow-base 0.9.2 / LFX 0.4.2

등록 LLM: `gemini-3.5-flash-lite`, temperature 0, repair LLM 0회

## 1. 현재 Flow 계약

현재 제공하는 Flow는 정확히 네 개다.

| Flow | 실행 노드 | Edge | SHA-256 |
| --- | ---: | ---: | --- |
| Data Analysis | 32 + Sticky Note 4 | 47 | `331482f34fc203c3d173517ff5a66af9b2d290b9b91c4df80be47dc81ab4f46d` |
| Domain 등록 | 8 + Sticky Note 1 | 7 | `233ef61e91c6be78c30036b75decc24860527f5b93476b1a5df4b69fae654e95` |
| Table Catalog 등록 | 8 + Sticky Note 1 | 7 | `aa7ddf8916c26666588132ffba2f5d67031a0d836a8cdadeedf73f07cd5f0a81` |
| Main Filter 등록 | 8 + Sticky Note 1 | 7 | `70afdf2177b65967ab6e7450db16247d445c5cdc67d086d9d95c24136813cf50` |

별도 Domain Policy 등록 Flow는 제거했다. 업무별 해석 차이는 Domain/Table Catalog/Main Filter 각 Flow의 특화 Prompt Template에서 관리한다. 실행 함수 descriptor와 planner policy 같은 실행 권한 계약은 자연어 등록으로 변경하지 않는다.

## 2. 간결 등록 Flow

세 등록 Flow는 동일한 구조를 사용한다.

```text
Chat Input
  ├─ 공통 Prompt Template ─┐
  ├─ 특화 Prompt Template ─┼─ 자연어 메타데이터 변환 ─ 메타데이터 검증 및 저장 ─ 결과 메시지 ─ Chat Output
  └─ Language Model ───────┘
```

- 작업자는 Chat Input에 평소 문장으로 등록 내용을 입력한다.
- 공통 Prompt와 업무별 특화 Prompt는 서로 다른 Prompt Template 노드다.
- Gemini 호출은 등록 1회당 최대 1회이며 pandas 코드 생성 및 repair LLM은 호출하지 않는다.
- LLM은 자연어를 제한된 등록 초안으로 바꾸고, 승인된 Source Registry와 결정론적 compiler가 실제 저장 가능 여부를 판단한다.
- 저장 노드는 `save`, `replace`, `validate_only`를 지원하며 등록 유형·도메인 ID·운영 환경·dry-run을 작업자 입력으로 노출하지 않는다.
- MongoDB에는 Domain, Table Catalog, Main Filter 세 컬렉션만 사용하며 항목 단위 문서로 저장한다.
- Table Catalog의 주석·줄바꿈을 포함한 SQL 원문은 LLM payload에서 제외하고 compiler가 승인된 registry binding으로 결합한다.
- `04 검증 및 저장`은 별도 LLM·컬렉션 없이 exact/정규화 key, typed ID, 동일 section 표시명·별칭, dataset `query_ref`·전체 source descriptor, 세 컬렉션 전역 alias target·표현 중복을 결정론적으로 검사한다.
- 충돌 응답은 최대 32건, 항목별 처리 결과는 최대 64건으로 제한하며 SQL·URL·접속 설정은 노출하지 않는다.
- 빈 DB에서도 Main Filter를 먼저 항목 저장할 수 있다. 부분 상태는 `activation_status=waiting_for_sections`와 누락 영역을 반환하며 Data Analysis에는 노출하지 않는다.
- 실제 변경 item만 upsert하고 transaction 직전에 읽은 item set이 중복 검사 시점과 같은지 재확인한다. 세 영역이 완성되는 마지막 write는 전체 compile과 저장 후 loader 동치 검증을 모두 통과해야 한다.

## 3. 검증 결과

### 코드 및 Flow

- 전체 pytest: 525/525 통과
- 메타데이터 항목·중복·부분 저장 정책 단위 테스트: 35/35 통과
- standalone 생성물: 29/29 동기화 통과
- Flow source parity: 4개 Flow, 3개 artifact layer, custom-node instance 99개, 오류 0
- Langflow runtime parse: 4개 Flow의 실행 노드 56/56 통과
- 모든 Flow와 실행 노드의 `lf_version` 및 `last_tested_version`: 1.9.2

### Data Analysis 회귀

- canonical 질문: 70/70 통과
- standalone component pipeline: 통과
- 주문·매출 범용 도메인 pipeline: 통과
- 멀티턴: 1·2차 질문, 상태 전진, 세션/소유자 격리, 비로그인 비영속 처리 모두 통과
- pandas 코드 생성 LLM / repair LLM: 0회

증적: `validation_outputs/langflow_equivalent_pipeline.json`

### 실제 Gemini 등록 경로

간결 Domain 등록 Flow를 `gemini-3.5-flash-lite`와 Google native JSON schema binding으로 실행해 다음을 확인했다.

- model 호출 1회
- provider fallback 0회
- repair 호출 0회
- 결정론적 compiler 검증 통과
- `validate_only`로 실행하여 MongoDB 쓰기 없음

빈 DB Main Filter 최초 등록 경로는 standalone component의 실제 `save` transaction으로 직접 검증했다. 결과는 `status=ok`, `stage=committed`, `persisted=true`, `revision=0`, `activation_status=waiting_for_sections`, `ready_sections=[main_filter]`, `missing_sections=[domain, table_catalog]`이며 기존의 `Section patches require ...` 오류는 발생하지 않는다. 이후 Table Catalog와 Domain 항목이 채워지면 전체 package를 자동 compile한다. 이번 검증에서는 운영 MongoDB를 변경하지 않았다.

## 4. 최종 산출물

- 개별 Flow: `flow_exports/`
- Langflow import-ready 개별/통합 JSON: `import_ready_flows/`
- import-ready ZIP: `import_ready_flows.zip`
- 통합 bundle SHA-256: `ed957ac8e788e287346912632c39bc8ed61cc78361bccf05d83d147297215a0f`
- ZIP SHA-256: `4a4570acb005dde077e13d160333dcbfd5af396d1937042a7032ec860c58efce`

## 5. 재현 명령

```powershell
.venv\Scripts\python.exe tools\build_standalone_components.py --check
.venv\Scripts\python.exe tools\validate_flow_component_sources.py
.venv\Scripts\python.exe tools\validate_langflow_runtime.py
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.venv\Scripts\python.exe tools\validate_langflow_equivalent_pipeline.py --execute-cases --execute-components --execute-order-sales --execute-multiturn
```
