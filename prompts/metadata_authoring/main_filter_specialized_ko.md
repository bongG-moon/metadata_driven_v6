[현재 배포의 제조 주요 필터 등록 특화 규칙]

- `OPER_NAME을 주요 필터로 등록`하면 `target_type=field`, `target_id=OPER_NAME`으로 작성합니다.
- 공정, 작업 공정, operation, process 같은 표현은 동일 field 대상의 `expressions` 배열 하나에 넣습니다.
- DP처럼 여러 실제 공정값을 묶는 공정 그룹은 주요 필터 field alias가 아니라 Domain의 `entity_groups`에서 등록합니다.
- 같은 target의 별칭은 하나의 canonical alias card로 저장되며 표현마다 별도 item을 만들지 않습니다.
