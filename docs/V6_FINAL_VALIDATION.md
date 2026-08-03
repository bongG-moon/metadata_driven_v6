# metadata_driven_v6 최종 구현·검증 보고서

검증 기준일은 2026-08-01이며 기준 runtime은 Python 3.12.8, Langflow 1.9.2, langflow-base 0.9.2, LFX 0.4.2다.

> 역사 문서: 이 문서는 2026-08-01 당시 구현 증적을 보존한다. 현재 계약은 별도 Domain Policy 등록 Flow를 제거한 4-Flow 구조이며 최신 결과는 `V6_FINAL_VALIDATION_CURRENT.md`를 따른다.

## 1. 구현 결론

trusted core에는 pandas code generation LLM과 repair LLM이 없다. 질문은 아래 단일 경계로 처리한다.

```text
Message/API 입력
→ authenticated request + owner/session state
→ compiled metadata candidate bundle
→ route eligibility
   ├─ unique + complete: deterministic, Intent LLM 0회
   ├─ semantic choice: registered candidate ID 선택만 Intent LLM 1회
   └─ registry gap: unsupported, LLM/조회 0회
→ 공통 analysis.intent.v1
→ deterministic analysis.plan.v1
→ read-only retrieval
→ typed operator executor
→ immutable response.v1
→ Message / API Data / GaiA fan-out
```

등록된 field role과 operator를 조합하므로 조인, 상·하위 N, 최대·최소와 동률, 그룹별 순위, 정확한 컬럼 선택, row-wise 컬럼 비교, 중복 그룹, 존재·부재 비교, 상세·이력 조회를 질문별 pandas code 없이 실행한다. 미등록 field/operator/policy는 자동 pandas fallback 대신 clarification 또는 `unsupported_operation`으로 종료한다.

## 2. 산출물

- Data Analysis Flow: `flow_exports/metadata_v6_data_analysis_flow_v6_standalone.json`
- Domain Authoring Flow: `flow_exports/metadata_v6_domain_authoring_flow_v6_standalone.json`
- Dataset Catalog Authoring Flow: `flow_exports/metadata_v6_dataset_catalog_authoring_flow_v6_standalone.json`
- Main Filter Authoring Flow: `flow_exports/metadata_v6_main_filter_authoring_flow_v6_standalone.json`
- 통합 bundle: `import_ready_flows/00_metadata_driven_v6_complete_ALL_FLOWS.json`
- import ZIP: `import_ready_flows.zip`
- standalone component source: `langflow_components/`
- canonical 질문·oracle: `validation/cases.jsonl`
- route 분류: `validation/branch_classification.md`
- 사용자 기능/구현 가이드: `docs/V6_FUNCTIONAL_DESIGN.md`, `docs/V6_IMPLEMENTATION_GUIDE.md`

모든 custom component는 필요한 runtime helper, compiled catalog, 40개 schema를 source에 embed하며 sibling Python import나 runtime filesystem schema loading을 요구하지 않는다. 배포 physical source는 Data Analysis 15개, Metadata Authoring 2개, Shared 1개로 총 18개다.

## 3. 검증 결과

| Gate | 결과 | 증적 |
| --- | ---: | --- |
| 전체 Python test | 333/333, failure/error/skip 0 | `validation_outputs/pytest_v6_final_latest.xml` |
| machine schema | Draft 2020-12 closed schema 40개 | `contracts/schemas/` |
| canonical 질문 | 70/70 | `validation_outputs/runtime_cases_final.json` |
| route | deterministic 65 / intent_llm 3 / unsupported 2 | 같은 report |
| Langflow-equivalent 전체 pipeline | graph/canonical/component/order-sales/multi-turn 전체 PASS | `validation_outputs/langflow_equivalent_pipeline_http_ready_final.json` |
| 반복 안정성 | 70건 × 3회, mismatch 0 | `validation_outputs/runtime_repeat_stability.json` |
| pandas code/repair LLM | 모든 run에서 0/0 | canonical/repeat report |
| metadata compile | 10 dataset / 47 field / 17 metric / 10 recipe | `metadata/fixtures/compiled/compile_report.json` |
| generated contract freshness | 39/39 current | generator `--check` |
| trusted Blueprint freshness | external pin/source/domain/environment/executable hash verified | `tools/build_executable_blueprint.py --check` |
| standalone physical source | 18/18 current | standalone generator `--check` |
| Flow source parity | 75 custom-node instance / 18 unique / error 0 | `validation_outputs/flow_source_sync_v6_final.json` |
| exact Langflow node parse | 37/37 (19+6+6+6) | `validation_outputs/langflow_runtime_v6_final.json` |
| Flow count/version | 4개, 모든 Flow/node 1.9.2 | flow manifest/runtime report |
| 주문·매출 범용 도메인 | 19/19 + 제조 도메인 session/result-ref 격리 PASS | `validation_outputs/order_sales_component_cases_v6_final.json` |
| historical optional Blueprint authoring | 1/1, annotation 1회, repair 0, executable hash 불변; 현재 기본 free-form lane 증적 아님 | `validation_outputs/live_blueprint_authoring_final.json` |
| 실제 Gemini Intent 선택 | 3 case × 3회 = 9/9, pandas code/repair 0 | `validation_outputs/live_intent_models_candidate_cards_final.json` |
| 실제 Langflow authoring HTTP | 3 Flow import, 4/4 commit, revision 1→2→3→4, draft 1 / annotation 1 / repair 0 | `validation_outputs/langflow_http_authoring_final_pass.json` |
| 실제 Langflow Data Analysis HTTP | revision 4 active metadata, OS01/OS02/OS08 3/3, state 1, terminal hash 동치, 모든 LLM 0 | `validation_outputs/langflow_http_order_sales_final_pass.json` |
| 실제 Langflow 제조 migration→analysis HTTP | normalized companion 3종, revision 1→4, dataset execution projection 불변, Data Analysis 4/4, state 1→2, pandas code/repair 0 | `validation_outputs/langflow_http_migration_final_pass.json` |

canonical 70건에는 기존 Q01-Q30, 날짜 D01-D06, MT-1~MT-5 12개 turn, OP01-OP13(OP05A 포함)과 새 route branch probe 8건이 포함된다.

## 4. v5 입력과 secret 이관

- `.env`의 54개 key와 주석/빈 줄은 v5에서 복사했고, 사용자 지정에 따라 `LLM_MODEL_NAME`만 `gemini-3.5-flash-lite`로 바꿨다. 따라서 byte-for-byte 동일하다고 주장하지 않는다.
- v5 `.env` SHA-256은 `067aa700459d1efbefa42d8b7195ff2c258a81a5161e8c152139d25ac71be245`, v6 `.env` SHA-256은 `5ae4193cb0025b2a04f968d675bd06224b26a483762fad7d8076db57e301c15b`다. secret 값은 report/Flow JSON에 넣지 않았다.
- `domain_knowledge.txt`, `main_variable.txt`, `data_catalog.txt`도 v5 원문 hash를 보존했다.
- `.gitignore`는 `.env`, runtime store, cache와 log를 제외한다.
- metadata compile은 v5 collection에 0회 write하며 v6 candidate/migration report만 만든다.

## 5. 실제 Gemini와 Langflow 검증

`gemini-3.5-flash-lite` 실제 API 호출을 수행했다.

- Historical optional Blueprint lane: 관리자 검토 Blueprint와 별도 SHA-256 pin을 먼저 검증한 뒤 `display_name`·`description` annotation만 1회 생성했다. 이 수치는 현재 기본 free-form full-draft lane의 검증으로 합산하지 않는다. provider 1회, prompt 2,082 token, candidate 76 token, 총 2,158 token, repair 0회다.
- Intent: sealed candidate ID 선택이 필요한 3개 case를 각 3회 실행해 9/9 통과했다. 특히 elliptical multi-turn `MT04-02`도 grouped-summary 유지 정책으로 3/3 통과했다. pandas code/repair 호출은 0/0이다.
- missing/wrong external pin, domain/environment/source mismatch, 단순·재계산 executable tamper, annotation executable injection은 provider 호출 전에 fail-closed했다.

재실행 명령:

```powershell
python tools/validate_live_blueprint_authoring.py `
  --model gemini-3.5-flash-lite `
  --output validation_outputs/live_blueprint_authoring_final.json

python tools/validate_live_intent_models.py `
  --models gemini-3.5-flash-lite `
  --runs 3 `
  --output validation_outputs/live_intent_models_candidate_cards_final.json
```

exact 1.9.2 isolated server에는 4개 Flow를 모두 HTTP 201로 import했고, current export의 37개 node template parse와 75개 custom-node projection source parity도 통과했다. Data Analysis는 같은 Flow edge 순서의 component pipeline에서 제조 70/70, 주문·매출 19/19, authenticated multi-turn/state isolation을 통과했다. 실제 HTTP에서도 authoring으로 만든 revision 4 `order_sales` active metadata를 로드해 OS01·OS02·OS08 3/3을 실행했고, 모두 deterministic route, state version 1, Message/API/compact GaiA canonical hash 동치와 intent/answer/pandas-code/pandas-repair LLM 0회를 확인했다.

Historical authoring HTTP prepare/approve/execute 검증은 실제 authoring Flow 3개를 import하고 domain, dataset, main-filter, domain-policy를 순서대로 commit했다. revision은 `1 → 2 → 3 → 4`, 호출 합계는 draft 1회(dataset), annotation 1회(domain), repair 0회이며 당시 source-sealed alias-only main-filter와 domain-policy는 LLM 0회였다. 이 결과는 현재 기본 free-form Domain full-draft lane과 별도 Domain Policy Flow의 검증으로 합산하지 않는다.

제조 migration→analysis HTTP 검증은 v5 원본 자연어 TXT 3종의 byte/hash를 그대로 보존하고, 각각 source-manifest로 pin한 domain-policy, dataset, main-filter normalized companion을 입력했다. 격리 environment의 seed revision 1에서 세 patch를 commit해 revision 4가 되었고, 호출 수는 dataset draft 1회, domain-policy/main-filter LLM 0회, repair 0회다. dataset의 실행 projection hash는 이관 전후 동일했으며 final loader와 production pointer 불변 gate를 통과했다. 이어 같은 active metadata로 Data Analysis Flow를 4회 실행해 deterministic 3회, Intent LLM 1회, 2-turn state `1 → 2`, pandas code/repair 0회를 확인했다. 증적은 `validation_outputs/langflow_http_migration_final_pass.json`이다.

Data Analysis HTTP validator는 Langflow JSON/Data tweak가 `NestedDict`로 전달되는 경우를 당시 standalone input contract로 복원하고, compact GaiA의 `metadata.response_sha256`도 같은 canonical response hash로 비교했다. OS08 oracle은 연결된 source payload의 매출 1,000, 환불 300에 따라 순매출 700을 기대하며, 잘못된 환불 0/순매출 1,000 fixture를 사용하지 않았다. 원본 source payload, raw HTTP response와 secret은 report에 저장하지 않았다.

격리 Langflow import 재실행:

```powershell
python tools/validate_langflow_runtime.py `
  --all-flows `
  --strict-versions `
  --server-url http://127.0.0.1:7860 `
  --output validation_outputs/langflow_import_final.json
```

validator는 upload한 Flow를 삭제하지 않으므로 운영 DB가 아닌 isolated Langflow profile을 사용한다.

## 6. 바탕화면 최종 배치

검증·게시 원본은 `metadata_driven_v5/v6_implementation_staging`에 있으며, 검증된 최종본은 `Desktop/metadata_driven_v6`에 게시한다. 아래 명령은 cache와 `validation_outputs/langflow_*_profile/` 격리 runtime profile을 제외하고 `.env`까지 최종 폴더에 overlay copy하며 `.env` hash와 Flow 4개를 재검증한다. HTTP report는 v2/exact-model authoring PASS, v1/order-sales Data Analysis PASS, v1/manufacturing migration-to-analysis PASS 세 canonical 파일만 포함하고 이전 실패·진단 report는 복사와 tree hash에서 제외한다. 세 report가 모두 현재 Flow SHA-256과 일치하지 않으면 복사 전에 실패한다. 이전 publish에서 target에 남은 runtime profile과 HTTP 진단 report도 검증된 target 경로 안에서만 제거하며, copy와 tree-hash parity가 같은 exclusion 함수를 사용한다.

Publish 포함 파일을 대상으로 v5 `.env`의 secret-bearing key 값을 exact-match scan한 결과 `.env` 자체 밖의 일치 항목은 0건이다. pytest XML에서 탐지되는 Google-key/credentialed-Mongo/private-key 형태 문자열은 credential 거부 테스트의 명시적 fake parameter이며 실제 `.env` 값과 일치하지 않는다.

```powershell
powershell -ExecutionPolicy Bypass -File tools/publish_to_desktop.ps1
```

스크립트는 대상 폴더명이 정확히 `metadata_driven_v6`일 때만 복사하고 기존 폴더를 재귀 삭제하지 않는다.

## 7. 재현 명령

```powershell
python tools/compile_metadata.py
python tools/generate_contracts_and_cases.py --check
python tools/build_executable_blueprint.py --check
python tools/build_standalone_components.py --check
python tools/validate_runtime_cases.py --output validation_outputs/runtime_cases_final.json
python tools/validate_langflow_equivalent_pipeline.py --execute-cases --execute-components --execute-order-sales --execute-multiturn --output validation_outputs/langflow_equivalent_pipeline_http_ready_final.json
python tools/validate_order_sales_component_cases.py --output validation_outputs/order_sales_component_cases_v6_final.json
python tools/validate_flow_component_sources.py --output validation_outputs/flow_source_sync_v6_final.json
python tools/validate_langflow_runtime.py --all-flows --strict-versions --output validation_outputs/langflow_runtime_v6_final.json
python -m pytest --junitxml validation_outputs/pytest_v6_final_latest.xml -q
```

명령은 exact v6 environment에서 실행한다. 현재 검증에서는 상위 v5의 `.venv`가 정확한 package tuple을 제공했다.
