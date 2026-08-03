[현재 배포의 제조 데이터셋 등록 특화 규칙]

- OPER_NAME 같은 대문자 식별자는 원문이 canonical field로 명시한 경우 그대로 사용합니다.
- 공정명 문자열 필드는 일반적으로 `semantic_type=string`, 역할은 원문 범위 안에서 `filter`, `group`, `join`, `sort`, `output` 중 필요한 것만 사용합니다.
- source type이 previous_result이면 앞 단계 결과를 사용하는 데이터셋으로 해석하고 외부 쿼리나 fixture 경로를 만들지 않습니다.
- Oracle/Datalake/Goodocs/H-API 원천은 원문에 적힌 source type과 조회 정보를 그대로 구조화하며 credential은 출력하지 않습니다.
