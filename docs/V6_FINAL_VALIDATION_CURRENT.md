# metadata_driven_v6 현재 최종 검증 결과

검증일: 2026-08-04

기준 환경: Python 3.12.13 / Langflow 1.9.2 / langflow-base 0.9.2 / LFX 0.4.2

등록 LLM: `gemini-3.5-flash-lite`, temperature 0, repair LLM 0회

## 1. 현재 Flow 계약

현재 제공하는 Flow는 정확히 네 개다.

| Flow | 실행 노드 | Edge | SHA-256 |
| --- | ---: | ---: | --- |
| Data Analysis | 32 + Sticky Note 4 | 47 | `39a2de9430a3e78862d0a7ebe83e53cc0c1ef0df1f7bac9bc7b7222ba71a77ed` |
| Domain 등록 | 8 + Sticky Note 1 | 7 | `b67444eb9bede53e562b3039e0fdcb0a3bc924534b33d44c758633432d11e3f0` |
| Table Catalog 등록 | 8 + Sticky Note 1 | 7 | `6e9289ee3a16f18a98b3bec55b18a6459d63d98e28a845e7e47fae0928655eae` |
| Main Filter 등록 | 8 + Sticky Note 1 | 7 | `d6da47044f0363b36d3fdd3c5851612b06d7e9758539d6ef607d02fb2eb6c34f` |

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
- LLM은 자연어를 등록 종류별 폐쇄형 초안으로 바꾸고, 결정론적 compiler가 세 MongoDB 컬렉션을 결합해 실제 저장·활성 가능 여부를 판단한다. 작업자 입력과 LLM payload에는 승인 어휘·원천 레지스트리를 넣지 않는다.
- v5식 원문에 실행 필수 사실이 모두 있으면 결정론적 원문 투영이 작은 IR을 만들기 때문에 LLM JSON이 잘려도 저장 후보를 계속 검증할 수 있다. 누락·충돌 정보는 추측하거나 강제 저장하지 않는다.
- 저장 노드는 `save`, `replace`, `validate_only`를 지원하며 등록 유형·도메인 ID·운영 환경·dry-run을 작업자 입력으로 노출하지 않는다.
- MongoDB에는 Domain, Table Catalog, Main Filter 세 컬렉션만 사용하며 항목 단위 문서로 저장한다.
- Table Catalog의 주석·줄바꿈을 포함한 읽기 전용 SQL 원문은 자연어 입력의 일부로 구조화해 항목에 보존하고, compiler가 쿼리 형태·필수 변수·원천 참조를 검증한다.
- `04 검증 및 저장`은 별도 LLM·컬렉션 없이 exact/정규화 key, typed ID, 동일 section 표시명·별칭, dataset `query_ref`·전체 source descriptor, 세 컬렉션 전역 alias target·표현 중복을 결정론적으로 검사한다.
- 충돌 응답은 최대 32건, 항목별 처리 결과는 최대 64건으로 제한하며 SQL·URL·접속 설정은 노출하지 않는다.
- 빈 DB에서도 Main Filter를 먼저 항목 저장할 수 있다. 부분 상태는 `activation_status=waiting_for_sections`와 누락 영역을 반환하며 Data Analysis에는 노출하지 않는다.
- 실제 변경 item만 upsert하고 transaction 직전에 읽은 item set이 중복 검사 시점과 같은지 재확인한다. 세 영역이 완성되는 마지막 write는 전체 compile과 저장 후 loader 동치 검증을 모두 통과해야 한다.

## 3. 검증 결과

### 코드 및 Flow

- 전체 pytest: 566/566 통과
- 메타데이터 항목·중복·부분 저장 정책 단위 테스트: 36/36 통과
- standalone 생성물: 29/29 동기화 통과
- Flow source parity: 4개 Flow, 3개 artifact layer, custom-node instance 99개, 오류 0
- Langflow runtime parse: 4개 Flow의 실행 노드 56/56 통과
- 모든 Flow와 실행 노드의 `lf_version` 및 `last_tested_version`: 1.9.2
- 이번 변경 영향 회귀: standalone·자연어 등록·MongoDB 항목 저장 166/166 통과

### Data Analysis 회귀

- canonical 질문: 70/70 통과
- standalone component pipeline: 통과
- 주문·매출 범용 도메인 pipeline: 통과
- 멀티턴: 1·2차 질문, 상태 전진, 세션/소유자 격리, 비로그인 비영속 처리 모두 통과
- pandas 코드 생성 LLM / repair LLM: 0회

증적: `validation_outputs/langflow_equivalent_pipeline.json`

### 실제 Gemini 등록 경로

사용자가 제시한 `production` 이력 데이터, DP 공정 그룹, DATE/OPER_NAME 메인 필터 원문을 전용 `metadata/authoring/v6_user_regression_live/` 입력으로 보존하고, 세 간결 등록 Flow와 `gemini-3.5-flash-lite` 및 실제 MongoDB transaction으로 실행했다.

- model 호출 3회(Flow별 1회)
- provider fallback 0회
- repair 호출 0회
- provider finish reason 3건 모두 `STOP`
- candidate 출력 966/817/1132 bytes로 장문 JSON 반복 제거 확인
- DP 공정 그룹+별칭 2건, production 테이블 1건, 메인 필터 2건을 항목 단위로 transaction 저장
- 도메인 프로필 문서 없이 내부 `default` 프로필로 전체 runtime package compile 및 loader hash 동치 검증 통과
- 원래 검증 DB의 1/1/1 항목은 사전 백업 후 항상 복원

증적: `validation_outputs/three_collection_user_regression_live.json`, `validation_outputs/langflow_runtime_v5_style_authoring.json`

빈 DB Main Filter 최초 등록 경로는 standalone component의 실제 `save` transaction으로 직접 검증했다. 결과는 `status=ok`, `stage=committed`, `persisted=true`, `revision=0`, `activation_status=waiting_for_sections`, `ready_sections=[main_filter]`, `missing_sections=[domain, table_catalog]`이며 기존의 `Section patches require ...` 오류는 발생하지 않는다. 이후 Table Catalog와 Domain 항목이 채워지면 전체 package를 자동 compile한다. 이번 검증에서는 운영 MongoDB를 변경하지 않았다.

### 실제 Langflow 전체 연결 검증

정확한 Langflow 1.9.2 서버에 네 Flow를 업로드하고, 완전히 빈 `datagov_v6_connected_20260804_014124` MongoDB에 다음 순서로 실제 실행했다.

1. Main Filter 자연어 등록
2. Domain profile 등록
3. `wip_today` Table Catalog 등록
4. DA 공정 그룹 등록
5. `WIP_QTY` metric 등록
6. product grain 등록
7. `product.standard` recipe 등록
8. 세 컬렉션 자동 compile
9. `오늘 DA공정 WIP을 제품별로 알려줘` Data Analysis 실행

등록 7건은 모두 Chat Output의 저장 완료 메시지와 `gemini-3.5-flash-lite` 비변경 검증 호출 `draft_llm_calls=1`, `repair_llm_calls=0`을 확인했다. 실제 저장 결과는 Domain 8건, Table Catalog 1건, Main Filter 2건이다. `wip_today` SQL 원문의 줄바꿈·`{DATE}`와 필수 파라미터, `WIP_QTY -> wip/WIP`, DA `in` 선택, product grain, typed aggregate recipe를 MongoDB 문서에서 다시 확인했다.

Data Analysis는 결정론 경로와 LLM 0회로 끝났고, 원천 2행과 최종 2행을 반환했다. 최종 값은 `R-001 WIP_QTY=300`, `R-002 WIP_QTY=0`이다. 이 검증의 조회 adapter는 동일 Flow의 `dummy` 모드이며, 등록된 Oracle source/query 계약과 Typed IR 전체 실행을 검증한다. 실제 Oracle 접속은 운영 접속 설정이 주입된 환경에서 별도 실행해야 한다.

증적: `validation_outputs/connected_langflow_chain_20260804_014124.json`

## 4. 최종 산출물

- 개별 Flow: `flow_exports/`
- Langflow import-ready 개별/통합 JSON: `import_ready_flows/`
- import-ready ZIP: `import_ready_flows.zip`
- 통합 bundle SHA-256: `fec59f00c19c2d64fb9e300c51409e2adb52f6d94758bc2b84752b60d3d244a4`
- ZIP SHA-256: `ce5c5d27483d2844eaf78d109361fe0466bf085b34be5d507430b034b21a92b0`

## 5. 재현 명령

```powershell
.venv\Scripts\python.exe tools\build_standalone_components.py --check
.venv\Scripts\python.exe tools\validate_flow_component_sources.py
.venv\Scripts\python.exe tools\validate_langflow_runtime.py
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.venv\Scripts\python.exe tools\validate_langflow_equivalent_pipeline.py --execute-cases --execute-components --execute-order-sales --execute-multiturn
.venv\Scripts\python.exe tools\validate_connected_langflow_chain_e2e.py --server-url http://127.0.0.1:7873
```
