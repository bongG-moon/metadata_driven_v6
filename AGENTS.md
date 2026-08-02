# metadata_driven_v6 작업 지침

이 지침은 저장소 전체에 적용한다.

## 1. 문서 우선순위

구현 전에 다음 문서를 순서대로 읽는다.

1. `AGENTS.md`
2. `harness/harness.md`
3. `harness/contracts/*.md`
4. `docs/V6_FUNCTIONAL_DESIGN.md`
5. `docs/V5_REBUILD_EVIDENCE.md`
6. `docs/V6_IMPLEMENTATION_GUIDE.md`
7. `docs/V6_METADATA_AUTHORING_GUIDE.md`
8. `docs/V6_VALIDATION_GUIDE.md`

구현과 문서가 다르면 코드를 임의로 정당화하지 말고 contract 또는 코드를 함께 수정한다.

## 2. Langflow 기준

- `langflow==1.9.2`
- `langflow-base==0.9.2`
- `lfx==0.4.2`
- Python 3.10 이상 3.14 미만, 기본 검증 Python 3.12
- 기본 Language Model source는 `tools/assets/langflow_1_9_2_language_model.py`에 고정한다.
- 기본 component index는 exact 1.9.2 환경의 `lfx/_assets/component_index.json`을 사용한다. 다른 환경에서 builder를 실행하면 `LANGFLOW_COMPONENT_INDEX_PATH`로 이 파일을 명시해야 한다.
- builder는 Language Model source와 component index의 SHA-256을 asset manifest에 기록하고, 기대 hash와 다르면 생성 전에 실패한다.
- 모든 export의 `last_tested_version`과 모든 node의 `lf_version`은 `1.9.2`다.
- 더 최신 설치 환경의 기본 template을 우연히 채택하지 않는다.

## 3. 핵심 아키텍처 원칙

1. Deterministic Route Eligibility Gate가 원문 evidence, authenticated state, compiled metadata와 operator pin만으로 유일하고 완전한 semantic selection을 증명하면 Intent LLM을 호출하지 않는다.
2. 위 증명이 불가능한 경우에만 LLM이 질문의 **semantic intent**를 candidate ID에서 선택한다.
3. deterministic selection과 LLM selection은 동일한 closed `analysis.intent.v1`으로 정규화되고 하나의 Plan Compiler·Validator·Executor를 공유한다.
4. LLM이 dataset, source alias, physical column, pandas code, 최종 output column을 발명하게 하지 않는다.
5. metadata compiler가 semantic intent를 immutable `analysis.plan.v1`로 결정론적으로 컴파일한다.
6. fast path를 선택한 뒤 compiler/executor 오류가 발생해도 LLM 또는 자유 code로 자동 fallback하지 않는다.
7. pandas code generation LLM과 repair LLM은 trusted core 실행 경로에 두지 않는다.
8. 지원 operation은 typed executor가 실행한다. 미지원 operation은 임의 code fallback 없이 `unsupported_operation`으로 종료하고 bounded telemetry를 남긴다.
9. 반복되는 미지원 shape는 검토된 metadata recipe·formula·typed operator와 regression case로 승격한다. 실행된 임의 pandas 코드를 trusted operator로 자동 승격하지 않는다.
10. 답변 LLM은 선택 사항이며, 결과의 숫자·표·적용 조건을 바꿀 권한이 없다.
11. 질문별 문자열, 특정 제품·공정·dataset key를 공통 Python component에 하드코딩하지 않는다.
12. 없는 source나 metric을 0으로 대체하거나 다른 metric에서 복사하지 않는다.
13. 정상 조회 후 0행과 조회 실패·source 누락을 구분한다.
14. 한 실행에서 canonical↔physical column 변환은 source boundary에서 정확히 한 번만 수행한다.
15. 유연 조회는 질문별 recipe만 늘리는 방식이 아니라 registered field role과 composable typed operation DAG로 구현한다.
16. top/bottom N, 최대/최소 행, join, 동일/상이 컬럼 비교, 중복 그룹, 파생 지표는 tie/cardinality/null/zero 정책까지 plan에 명시한다.
17. 미래의 자유 pandas 탐색은 별도 `exploration.*` 계약과 외부 격리 계층으로만 고려한다. 초기 v6 runtime에서는 disabled이며 trusted 5-Flow core, 자동 routing, `result_ref`, `turn.state.v1`, Answer LLM에 연결하지 않는다.

## 4. Standalone 원칙

- 모든 custom component는 sibling Python 파일을 runtime import하지 않고 단독 실행 가능해야 한다.
- 공통 schema/helper가 필요하면 build 단계에서 component source에 embed한다.
- source of truth schema와 embedded schema의 SHA-256을 build/test에서 대조한다.
- MongoDB URI, database, collection, timeout, row limit, TTL, inline byte limit, executor memory limit 같은 운영 설정은 node input에서 확인·조정 가능해야 한다.
- secret 값은 Flow JSON에 직렬화하지 않는다.

## 5. Metadata 원칙

- 사용자의 자연어 TXT 입력 경로를 유지한다.
- raw TXT는 provenance source이며 runtime contract가 아니다.
- 기본 full-domain bootstrap은 `자유형 자연어 TXT bundle → 외부 공통 Authoring Prompt → LLM 1회 closed full draft → 결정론적 schema·semantic·dependency·security compile → immutable prepare → 외부 승인 → 별도 atomic execute` 순서를 지킨다. 작업자는 JSON, 등록 ID 목록, relation/field-role 선언문 같은 정형 문법을 맞출 필요가 없다. LLM은 후보 draft만 만들며, compiler 검증을 우회하거나 직접 저장·실행할 권한이 없다.
- 최초 bootstrap 입력에는 Domain·Dataset·Main Filter 원문을 합친 자연어 bundle 또는 그 정보를 빠짐없이 설명한 완전한 도메인 문서가 필요하다. 정보가 부족하면 형식을 요구하지 말고 `status=needs_clarification`의 `missing_fields`와 짧은 확인 질문으로 빠진 업무 정보를 설명한다.
- Dataset/Main Filter authoring은 exact active package를 기준으로 자유형 자연어 TXT에서 담당 section만 LLM 최대 1회로 closed patch한다. `source_grounding_mode=explicit_inventory`가 명시되고 모든 identity/binding이 결정론적으로 증명되는 경우에만 선택적 zero-LLM compile을 허용한다. 두 경로 모두 전체 schema·semantic dependency·security policy·hash를 다시 검증한다.
- 관리자 검토 Blueprint와 별도 SHA-256 pin을 사용하는 annotation-only 방식은 의무가 아니라 선택적 고신뢰 lane이다. 이 lane을 명시적으로 선택했을 때만 LLM의 수정 범위를 annotation으로 제한하고 executable byte 불변을 검증한다. 일반 작업자 입력에 Blueprint, pin 또는 엄격한 inventory 문법을 요구하지 않는다.
- 현재 live authoring 검증은 정확히 `gemini-3.5-flash-lite`, temperature `0`, provider/model fallback `0`, repair LLM `0`을 사용한다. 제조 bootstrap은 `metadata/authoring/v6_inputs/domain_v6.txt`, `dataset_v6.txt`, `main_filter_v6.txt`의 자연어 bundle을 기본 source로 사용한다.
- Domain Policy는 전용 관리자 node input만 사용하며 LLM 호출은 0회다. 모든 authoring 경로는 immutable prepare → 외부 승인 → 별도 atomic execute → active runtime projection으로 합류한다.
- Langflow 1.9.2 실행을 멈춰 두는 방식으로 승인 대기를 구현하지 않는다. pending store의 candidate hash를 승인하고 두 번째 run에서 같은 hash를 atomic claim해 저장한다.
- runtime loader는 `schema_version`, lifecycle status, compiler compatibility, dependency revision이 유효한 record만 읽는다.
- `filter_mappings`와 `standard_column_aliases`처럼 같은 의미를 중복 소유하지 않는다. dataset별 field binding 하나가 filter/group/join/output mapping의 단일 원천이다.
- v5 collection을 직접 덮어쓰지 않는다. v6 collection과 migration report를 사용한다.

## 6. Payload·memory 원칙

- 하나의 거대 payload를 모든 node가 누적 수정하지 않는다. 단계별 versioned envelope을 사용한다.
- raw source rows는 LLM에 전달하지 않는다.
- source branch에는 해당 job bundle만 전달한다.
- state에는 inline rows나 전체 chat history를 저장하지 않는다.
- full result/source는 TTL reference로 보관하고, Flow에는 ref·schema·row count·lineage·bounded preview만 전달한다.
- intent total input 28KB, answer LLM input 12KB, state capsule 6KB, inline trace 8KB budget을 자동 검증한다.

## 6.1 사용자 출력 호환성

- v5의 메시지 표시 선택 기능을 유지한다: 결과 테이블, 미리보기 행 수, 분석 근거, 다운로드, 알림, 적용 기준, 후속 질문, 의도 분석, 조회 진단, 실행 계획 진단.
- v5 `show_pandas_code` 설정은 migration alias로 읽되 v6에서는 생성 코드가 아니라 typed Execution IR과 operator trace를 표시한다.
- 표시 toggle은 Chat/Markdown presentation만 바꾸며 canonical result/message, API data, result/state 저장, GaiA answer/metadata를 삭제하거나 바꾸지 않는다.
- 최종 surface는 Langflow `Message`, structured API `Data` output, GaiA `answer/metadata`를 모두 유지한다.
- `answer_sections`는 summary, result table descriptor, applied criteria, evidence, notices, downloads, next questions를 가진다. v5 wire 호환 위치인 `data.rows`/`data_refs[]`를 가리키며 행·ref를 중복 저장하지 않는다.
- 실행 순서는 result/source store → state CAS commit → runtime row release → Message/API/GaiA fan-out이다.

## 7. 검증 원칙

- Phase 0에서는 `validation/validation_questions.txt`와 `validation/ACCEPTANCE_MATRIX.md`가 migration source다. Phase 1에서 `validation/cases.jsonl`을 생성·검토한 뒤에만 질문·expected contract·runner·문서의 canonical source로 승격한다.
- 모든 canonical case는 `expected_route=deterministic|intent_llm|unsupported`와 exact Intent/Answer/code/repair LLM 호출 수, route reason oracle을 가진다.
- deterministic core는 30개 대표 질문, 6개 날짜 질문, MT-1~MT-5 모든 turn을 100% 통과해야 한다.
- fixture가 미리 만든 intent/pandas code를 주입하는 테스트만으로 완료 판정하지 않는다.
- primary model과 더 약하거나 다른 provider/model profile에서 temperature 0으로 전체 corpus를 imported endpoint를 통해 3회 반복한다. `expected_route=deterministic|unsupported` case는 provider 호출이 0이어야 하며, `intent_llm` case만 model semantic conformance 대상이다.
- 각 run은 case별 route/call-count oracle과 일치해야 한다. 성공 case의 normalized intent, plan fingerprint, result schema도 반복 간 동일해야 한다.
- deterministic과 LLM 양쪽에서 동일 semantic selection을 만드는 equivalence fixture는 같은 normalized intent hash, plan fingerprint와 result hash를 내야 한다. route/usage trace 차이는 허용한다.
- HTTP 429/503/timeout은 semantic failure와 분리 기록한다.
- 실제 source smoke는 최소 9개 dataset과 required-param failure를 포함한다.
- operator matrix와 v5 presentation/output compatibility matrix를 모두 통과해야 한다.
- exact Langflow package tuple 검증은 “출력”이 아니라 불일치 시 실패해야 한다.

## 8. 구현·Flow JSON 동기화

- Python custom component, prompt, schema, Flow builder, export/import-ready JSON을 함께 수정한다.
- 생성물은 직접 손으로 수정하지 않는다.
- source/prompt/schema hash를 manifest에 기록한다.
- 모든 Flow와 node template을 exact 1.9.2 runtime에서 parse하고 isolated import smoke를 수행한다.

## 9. 완료 정의

코드 작성만으로 완료가 아니다. 변경 범위에 맞는 contract test, representative question, multi-turn, source/export parity, exact runtime parse, artifact manifest 검증까지 끝나야 한다.
