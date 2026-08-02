# v6 검증 질문 분기 분류

이 문서는 사람이 검증 범위를 빠르게 확인하기 위한 인덱스다. 기존 executable oracle의 단일 기준은 `cases.jsonl`이며 상세 case별 분류는 `branch_classification.md`를 따른다. 등록 함수 격리 경로는 제조 기본 메타데이터를 오염시키지 않도록 별도 generic fixture로 검증한다.

## 기존 질문셋

| 질문군 | ID | 기본 분기 | 예외 또는 핵심 검증 |
|---|---|---|---|
| 대표 단일 질문 | Q01-Q30 | deterministic | 단일·다중 source, join, top/bottom N, argmax, field 비교, 장비 enrich를 모두 Typed IR로 실행 |
| 날짜 계약 | D01-D06 | deterministic | 날짜 표기와 timezone을 deterministic하게 정규화 |
| 멀티턴 | MT01-01-MT05-02 | deterministic | `MT04-02`만 생략된 제품 범주 선택 때문에 intent_llm 1회, 이전 결과 fast path는 retrieval 0회 |
| operator | OP01-OP12, OP05A | deterministic | 등록 operator 조합과 결과 invariant 검증 |
| 미등록 연산 | OP13 | unsupported | LLM·retrieval 0회, `unsupported_operation`으로 종료 |

## 분기 판단 추가 질문셋

| ID | 분기 | Intent LLM | Retrieval | 목적 |
|---|---|---:|---:|---|
| BR-D01 | deterministic | 0 | 1 | 단일 source unique-complete 선택 |
| BR-L01 | deterministic | 0 | 2 | 다중 source unique-complete 선택 |
| BR-A01 | intent_llm | 1 | 0 | metric 모호성의 bounded 선택·명확화 |
| BR-U01 | unsupported | 0 | 0 | 미등록 field/formula의 조기 거부 |
| BR-F01 | deterministic error | 0 | 0 | compiler 실패 시 LLM fallback 금지 |
| BR-MT01 | deterministic | 0 | 0 | 이전 결과만 다시 분석하는 fast path |
| BR-EQD | deterministic | 0 | 1 | 교차 분기 동등성 기준 절반 |
| BR-EQL | intent_llm | 1 | 1 | semantic candidate 1회 선택 후 BR-EQD와 동일 plan/result |

## registered_call 격리 질문셋

상세 입력과 oracle은 `registered_call_validation_questions.txt`에 있다.

| ID | 분기 | 기대 상태 | fail-closed 경계 |
|---|---|---|---|
| RC-S01 | deterministic | ok | allowlist ID·version·구현 hash·schema hash가 모두 일치할 때만 실행 |
| RC-H01 | deterministic error | unsupported_operation | implementation hash 불일치 |
| RC-U01 | deterministic error | unsupported_operation | allowlist에 없는 function ID |
| RC-C01 | deterministic error | plan_contract_error | extra key 또는 schema hash 불일치 |
| RC-L01 | deterministic error | execution_memory_limit_exceeded | 입력/출력 행 또는 byte 한도 초과 |

모든 RC case의 Intent/Answer/code/repair LLM 호출 수는 0이고, 실패 시 다른 함수나 자유 코드로 fallback하지 않는다.
