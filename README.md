# metadata_driven_v6

범용 Domain Package v2의 자연어 authoring, deterministic compile, MongoDB 3컬렉션 저장 계약은
[`docs/V6_THREE_COLLECTION_METADATA.md`](docs/V6_THREE_COLLECTION_METADATA.md)를 기준으로 한다.

`metadata_driven_v6`는 v5 Data Analysis Flow를 부분 수정해서 이어 붙이는 프로젝트가 아니라, 검증된 기능 요구사항을 typed contract와 결정론적 실행기로 다시 구현하는 Langflow 프로젝트다.

현재 목표 계약은 **정확히 5개 MVP Flow(Data Analysis 1개 + metadata authoring 4개)**다. 기존 18개 standalone source·4개 Flow·75개 projection 증적은 migration baseline이며, Domain Policy Authoring Flow와 새 prompt/registered-function/UI 계약을 반영해 산출물과 evidence를 재생성하기 전에는 최종 구현 완료로 보지 않는다.

## 결론

- Langflow 기준: `langflow==1.9.2`, `langflow-base==0.9.2`, `lfx==0.4.2`, Python 3.12
- custom component: 런타임 sibling import가 없는 standalone 방식
- 결정론적으로 유일하고 완전한 semantic selection을 증명할 수 있는 질문: **Intent LLM 0회**
- 의미 선택이 필요한 질문: **Intent LLM 1회**. 답변 문장화 LLM은 선택 계약만 유지하며 기본 profile에서는 비활성
- 두 경로는 서로 다른 executor를 만들지 않고 동일한 `analysis.intent.v1 → analysis.plan.v1 → typed executor` 경계로 합류
- pandas 코드 생성 LLM과 pandas repair LLM: 기본 경로에서 제거
- 데이터 선택, 날짜 변환, 컬럼 매핑, 집계, join, 존재·부재 비교, 순위, 후속 결과 결합: metadata로 컴파일한 typed Execution IR을 결정론적으로 실행
- 유연 조회: 등록된 canonical field와 typed operator를 조합해 컬럼 선택·필터·그룹 집계·다중 join·상/하위 N·최대/최소 행·동일/상이 컬럼 비교·중복 그룹·파생 지표·상세/이력 조회를 실행
- 유연성 경계: 임의 Python은 허용하지 않으며, metadata에 field role/join/formula가 없거나 operator registry에 없는 요청은 추측 대신 clarification 또는 `unsupported_operation`
- 미지원 요청은 bounded telemetry로 집계하고, 반복 수요는 검토된 metadata recipe·formula·typed operator로 승격
- 자유 pandas 탐색은 미래의 별도 특권 계층 계약만 정의하며 초기 runtime에서는 비활성이다. trusted 5-Flow core의 자동 fallback 또는 결과/state 입력으로 연결하지 않는다.
- 자연어 TXT 기반 Domain/Table Catalog/Main Filter 입력: 유지. 현장 작업자는 JSON·스키마·ID inventory·relation key 문법을 작성하지 않고 기존처럼 자유롭게 설명한다.
- 실행 소스 binding: 작업자와 LLM은 `config_ref`/`query_ref`를 소유하지 않는다. **승인 업무 어휘·Source 참조 레지스트리**는 LLM에는 ID·family·업무용 표현만 제공하고, 물리 컬럼·타입·adapter/config/query binding은 결정론적 컴파일러에만 제공한다.
- 기본 Full-domain 등록: 작업자는 Domain/Dataset/Main Filter TXT에 평소 사용하는 자유로운 업무 문장만 입력한다. 세 LLM 분기가 이를 작은 closed 조각으로 바꾸고, 결정론적 engine이 승인 어휘와 정확히 결합한 뒤 전체 계약을 컴파일한다. 작업자는 JSON·DSL·canonical ID·물리 컬럼 타입·엄격 문법을 작성하지 않으며, 의미가 여러 가지면 저장 대신 비기술적인 확인 질문을 받는다.
- 정보가 부족하거나 모호하면 포맷 오류로 몰지 않고 draft/candidate 없이 `status=needs_clarification`의 누락 항목과 짧은 확인 질문을 반환한다.
- 선택적 고신뢰 등록: `source_grounding_mode=explicit_inventory`를 명시한 운영자 lane에서만 reviewed Blueprint+별도 SHA-256 pin의 annotation-only 방식 또는 완전한 inventory의 zero-LLM compile을 사용한다. 일반 작업자에게 이 문법이나 Blueprint/pin을 요구하지 않는다.
- live authoring model policy: 정확히 `gemini-3.5-flash-lite`, temperature 0, provider/model fallback 0, repair LLM 0. 제조 bootstrap은 v6 전용 `domain_v6.txt`+`dataset_v6.txt`+`main_filter_v6.txt` 자연어 bundle을 사용
- Prompt topology: Runtime Intent/Answer와 Domain/Dataset/Main Filter authoring 모두 공통·특화 Prompt Template을 별도 node/source/hash/edge로 유지한다. 특화 규칙은 각 특화 Template 본문에 직접 작성하고, runtime context는 Composer에만 한 번 연결한다. 동적 특화 본문 포트는 사용하지 않는다.
- Domain Policy Authoring: 별도 Flow의 explicit 관리자 입력 `intent_prompt_extension`, `answer_prompt_extension`, `specialized_functions_json`, `output_profile_json` 전용. Prompt Template/Composer/envelope/LLM 0회
- 특화 함수: descriptor→build-time standalone registry attestation→candidate→Intent→`registered_call` Typed IR→Registered Function Gateway→output schema/lineage 검증의 닫힌 실행 chain을 사용하며 metadata code/dynamic import/fallback은 금지
- v5 사용자 출력 기능: 결과표/근거/다운로드/알림/적용 기준/후속 질문/의도·조회·실행 진단 표시 선택, 구조화 API output, GaiA metadata, CSV ref, 멀티턴을 호환 계약으로 유지
- Langflow UI: Data Analysis node는 `00`~`27`, 네 등록 Flow는 각 Flow의 `00` 입력부터 최종 출력까지 실행 순서가 드러나는 한국어 표시명을 사용한다. 병렬 입력·Prompt·출력만 `A/B/C` 접미사로 구분한다. Metadata loader에는 MongoDB URI·database·timeout만, 실제 source node에는 조회 행 수 제한만 운영 조절값으로 노출한다.
- metadata read: `01 사용 가능 메타데이터 불러오기`가 고정된 도메인·테이블 카탈로그·메인필터 3컬렉션에서 가장 최근의 완전한 동일 release를 자동 탐색·검증·결합한다. domain/environment/source mode/collection 선택은 UI에 없다.
- 요청 시간: `02 요청 및 세션 상태 고정`에는 기준시각·시간대 UI가 없고, 실행 시각을 내부에서 생성해 `Asia/Seoul`로 고정한다. 검증의 고정 시각은 harness fixture다.
- 데이터 source 경계: `11 검증용 더미 데이터 조회`, `12 Oracle 데이터 조회`, `13 H-API 데이터 조회`, `14 Datalake 데이터 조회`, `15 Goodocs 데이터 조회`를 분리한다. 연결된 payload는 각 node가 자기 source 계약으로만 검증하며, 개발 dummy 검증을 실제 원천 조회 완료로 과장하지 않는다.
- 출력 전달 경계: `23 → 24·25·26`은 전송용 해시가 없는 일반 JSON 응답을 전달한다. 24·25·26은 수신 payload의 해시나 전체 응답 schema를 다시 검사하지 않으며, 결과 무결성 hash는 MongoDB result store 내부에서만 유지한다.
- MVP Flow inventory: Data Analysis 1개 + Domain/Dataset/Main Filter/Domain Policy authoring 4개, 총 5개
- metadata write: 자연어 해석 → deterministic compile/validation → 도메인·테이블 카탈로그·메인필터 3컬렉션 transaction 저장
- v5 MongoDB 문서: 직접 덮어쓰지 않고 v6 고정 3컬렉션 current release로 컴파일·이관

실행 계층은 다음과 같다.

1. trusted core: deterministic route eligibility, optional Intent LLM, typed IR compiler/executor
2. structured flexibility: 같은 trusted core 안에서 closed operator/formula/recipe registry 확장
3. future privileged exploration: 별도 `exploration.*` 계약과 외부 격리 실행 계층. 초기 v6에서는 disabled이며 다섯 core Flow에 포함하지 않음

Zero-LLM은 단순 키워드 shortcut이 아니다. 원문 evidence, authenticated follow-up state, compiled metadata와 operator pin만으로 **정확히 하나의 완전한 semantic selection**을 증명할 때만 허용한다. 증명하지 못하면 Intent LLM 경로를 처음부터 선택하며, fast path 선택 후 compiler/executor 오류를 LLM이나 pandas로 자동 우회하지 않는다.

## v5에서 확인한 기준선

2026-07-31 확인 시점의 v5 `main`은 `bb6df1a`이며, tracked source 내용은 `f5a2a79`와 같다. 바로 뒤의 `presence comparison` 및 `canonical column standardization` 구현은 revert된 상태다.

| 항목 | v5 기준선 |
| --- | ---: |
| Data Analysis Flow | 46 nodes / 71 edges |
| 정상 LLM 호출 | 3회 |
| 오류 시 최대 LLM 호출 | 4회 |
| 정적 prompt 원문 | 약 95KB |
| 실제 intent prompt | 약 54K~62K chars |
| 실제 pandas prompt | 약 16K~44K chars |
| intent normalizer | 5,405 lines |
| pandas executor | 2,869 lines |

v6의 목표는 단순 node 수 축소가 아니다. LLM이 결정하던 실행 의미를 계약과 compiler로 옮겨, 한 오류를 고쳤을 때 다른 질문이 깨지는 구조를 제거하는 것이다.

## 읽는 순서

1. [AGENTS.md](AGENTS.md)
2. [harness/harness.md](harness/harness.md)
3. [harness/contracts/ARCHITECTURE.md](harness/contracts/ARCHITECTURE.md)
4. [harness/contracts/PROMPTS.md](harness/contracts/PROMPTS.md)
5. [harness/contracts/METADATA.md](harness/contracts/METADATA.md)
6. [harness/contracts/INTENT_PLAN_EXECUTION.md](harness/contracts/INTENT_PLAN_EXECUTION.md)
7. [harness/contracts/PAYLOAD_STATE.md](harness/contracts/PAYLOAD_STATE.md)
8. [harness/contracts/VALIDATION.md](harness/contracts/VALIDATION.md)
9. [docs/V6_THREE_COLLECTION_METADATA.md](docs/V6_THREE_COLLECTION_METADATA.md)
10. [docs/V6_FINAL_MODIFICATION_PLAN.md](docs/V6_FINAL_MODIFICATION_PLAN.md)
11. [docs/V6_FUNCTIONAL_DESIGN.md](docs/V6_FUNCTIONAL_DESIGN.md)
12. [docs/V5_REBUILD_EVIDENCE.md](docs/V5_REBUILD_EVIDENCE.md)
13. [docs/V6_IMPLEMENTATION_GUIDE.md](docs/V6_IMPLEMENTATION_GUIDE.md)
14. [docs/V6_METADATA_AUTHORING_GUIDE.md](docs/V6_METADATA_AUTHORING_GUIDE.md)
15. [docs/V6_VALIDATION_GUIDE.md](docs/V6_VALIDATION_GUIDE.md)

## 구현 상태와 검증 결과

| 영역 | 상태 |
| --- | --- |
| v5 실패 패턴과 회귀 원인 | 설계·회귀 case에 반영 |
| route/LLM 경계 | 65 deterministic / 3 intent_llm / 2 unsupported, canonical 70/70 통과 |
| metadata v6 | 자유형 자연어 TXT→closed draft/section patch→결정론적 compiler 계약; 제조 fixture는 10 dataset, 47 field, 17 metric, 10 recipe |
| machine contract | Draft 2020-12 closed schema 45개, runtime boundary 검증 적용 |
| semantic intent / typed Execution IR | 구현 완료; pandas code/repair fallback 없음 |
| 유연 조회 | projection, typed filter, aggregate, formula, join, presence, top/bottom, argmax ties, group rank, field compare, duplicate group, detail/history 지원 |
| state / multi-turn | owner·session-bound TTL ref, CAS, executed-result contract, MT-1~MT-5 통과 |
| v5 output 호환 | Message 표시 toggle, structured API Data, GaiA, CSV ref, follow-up 유지 |
| Python test | 전체 suite 통과, failure/error 0; 3컬렉션 round-trip/tamper/collection/session 테스트 4건 포함 |
| 반복 안정성 | 70건 × 3회, 70개 case 모두 plan/result signature 동일 |
| Langflow 1.9.2 artifact | standalone component 25/25, 3개 artifact layer의 Flow source parity 168 instance/27 unique, 5개 Flow의 source-export node template 86/86 parse, import-ready 5/5 생성 |
| 주문·매출 범용 도메인 | 19/19 통과, 제조 도메인과 session/result ref 격리 확인 |
| MongoDB metadata | 격리 DB `datagov_v6_validation`에 정확히 도메인·테이블 카탈로그·메인필터 3문서 저장, 자연어 원문 3/3 보존, 동일 release 1개, loader round-trip 통과 |
| 실제 Gemini API | exact `gemini-3.5-flash-lite`, temperature 0, fallback 0. 기본 corpus와 제목·bullet 0개 재작성 corpus 모두 실제 authoring 4/4 cycle 통과; 각 run draft 5, annotation 0, repair 0 |
| 실제 Gemini + Mongo 등록 | exact `gemini-3.5-flash-lite` 3회, fallback/repair 0; 자유형 TXT→standalone Langflow component 순서→compile→3컬렉션 commit revision 2→loader 통과 (`three_collection_live_validation.json`) |
| Langflow runtime | 정확한 1.9.2/0.9.2/0.4.2에서 5개 Flow, 실행 node template 86/86 parse, Flow/source parity 통과 |
| Data Analysis 동등 실행 | canonical 70/70, component pipeline, 멀티턴/state owner 격리, zero-LLM follow-up 모두 통과 (`three_collection_equivalent_pipeline.json`) |

최신 명령과 증적은 [V6_FINAL_VALIDATION_CURRENT.md](docs/V6_FINAL_VALIDATION_CURRENT.md)를 따른다. [V6_FINAL_VALIDATION.md](docs/V6_FINAL_VALIDATION.md)는 2026-08-01의 4-Flow historical baseline이다.
