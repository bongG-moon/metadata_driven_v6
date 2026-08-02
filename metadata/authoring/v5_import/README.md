# v5 메타데이터의 v6 등록 입력

`originals/`에는 v5 루트의 `domain_knowledge.txt`, `data_catalog.txt`, `main_variable.txt`를 byte 단위로 그대로 보존한다.

등록용 파일은 Langflow의 세 자연어 입력과 이름을 맞췄다.

- `domain_v6.txt`: v5 `domain_knowledge.txt` 사본
- `dataset_v6.txt`: v5 `data_catalog.txt` 사본에 v6 승인 Source Registry에만 있던 제품 기준정보 설명을 자연어로 보완한 파일
- `main_filter_v6.txt`: v5 `main_variable.txt` 사본

자유형 LLM bootstrap은 실제 Gemini 응답이 strict metadata proposal 형식을 완성하지 못하면 MongoDB에 쓰기 전에 중단한다. 이 경우 검토 완료 package를 `tools/register_compiled_metadata_release.py`로 게시하는 결정론적 fallback을 사용한다. 이 도구도 등록 Flow와 같은 `make_metadata_section_documents -> replace_metadata_release -> load_domain_package_from_three_collections` 저장·재조회 계약을 사용한다.

MongoDB에는 항목마다 별도 collection을 만들지 않는다. 고정된 세 collection에 domain/environment별 현재 release 문서가 하나씩 저장되고, 문서 내부의 `datasets`, `fields`, `entity_groups`, `predicates`, `aliases`, `recipes`에 개별 항목이 들어간다.
