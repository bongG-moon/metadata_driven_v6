# V6 특화 함수 Text Input 계약

## 목적

공정 순서 범위와 제품 토큰 매핑은 일반 `filter`, `aggregate`, `join`, `rank`와 구분되는 업무 특화 로직이다. Data Analysis Flow는 이를 `08B 특화 함수 계약 입력` Text Input에서 별도로 선언하고 `09 실행 계획 컴파일 및 검증`에 직접 전달한다.

입력 원본은 `prompts/data_analysis/specialized_functions_ko.json`이며 Flow 빌더가 파일 내용을 Text Input 기본값으로 넣고 source SHA-256을 manifest에 기록한다.

## 실행 계약

- `manufacturing.filter_ordered_range@1`
  - trigger: `ordered_range`
  - binding: `OPER_NAME`, `OPER_SEQ`, process ordering
  - 실행 결과: inclusive 범위에 해당하는 row index
- `manufacturing.match_product_tokens@1`
  - trigger: `product_token`
  - binding: `TECH`, `DEN`, `MODE`, `PKG_TYPE1`, `PKG_TYPE2`, `LEAD`, `MCP_NO`
  - 실행 결과: 모든 실제 토큰 rule을 만족하는 row index

두 함수는 `registered_call.v1`로만 실행한다. Text Input은 Python 실행 입력이 아니며 `eval`, `exec`, dynamic import를 사용하지 않는다. function ID/version/field binding이 standalone allowlist와 맞지 않으면 retrieval 전에 fail-closed한다.

제품 그룹(POP/MOBILE/HBM 등), 공정 그룹, 일반 필터·집계·조인·정렬·상하위 N은 기존 typed primitive를 그대로 사용한다. 질문에 대응하는 typed literal이 없으면 특화 함수는 호출되지 않는다.

## 검증 결과

- canonical 질문: 70/70 통과
- 전체 pytest: 통과
- Flow source parity: 통과
- Langflow 1.9.2 / langflow-base 0.9.2 / LFX 0.4.2 runtime parse: Data Analysis 32/32, 등록 Flow 각각 8/8 통과
- standalone component pipeline, 주문·매출 다중 도메인 pipeline, 멀티턴 pipeline: 통과

검증 증적은 `validation_outputs/langflow_equivalent_pipeline.json`과 `validation_outputs/langflow_1_9_2_runtime.json`에 있다.
