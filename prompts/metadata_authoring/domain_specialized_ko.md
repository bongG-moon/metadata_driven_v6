[현재 배포의 제조 도메인 등록 특화 규칙]

- `공정 그룹`, `공정 묶음`, `포함 공정`이 나오면 하나의 `entity_groups` 항목으로 해석합니다.
- `field는 OPER_NAME`, `기준 컬럼은 OPER_NAME` 같은 문장은 그룹의 `target_field=OPER_NAME`을 뜻합니다.
- `포함 공정은 AA, BB, CC`는 `members=["AA", "BB", "CC"]`로 보존합니다.
- DP, D/P, DP공정처럼 같은 그룹을 가리키는 표현은 하나의 그룹 card 안 `aliases` 배열로 보존합니다.
- 그룹 요청에서 `field:OPER_NAME` 같은 field alias card를 만들지 않습니다. 그룹 alias card는 compiler가 `entity_group:<group_id>` 하나로 파생합니다.
- 공정 그룹과 도메인 프로필을 한 요청에서 동시에 등록하지 않습니다.
