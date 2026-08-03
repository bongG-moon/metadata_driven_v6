# metadata_driven_v6 Langflow 1.9.2 import bundle

이 폴더는 `flow.inventory.v1`에서 생성된 정확히 네 개의 standalone Flow를 포함합니다.
`00_metadata_driven_v6_complete_ALL_FLOWS.json`을 한 번에 import하거나 번호 순서대로 개별 JSON을 import합니다.

- Python 3.12
- langflow 1.9.2
- langflow-base 0.9.2
- lfx 0.4.2

Flow JSON에는 credential 값이나 domain-specific blueprint가 없습니다. import 후 운영자가 필요한 Langflow node input 또는 Global Variable을 연결합니다.

세 등록 Flow는 Chat Input, 공통/특화 Prompt Template, Gemini 1회 변환, 결정론적 검증·저장, Chat Output 순서로 동작합니다. 작업자에게 JSON, inventory 선언 문법, Blueprint나 pin을 요구하지 마십시오.
Dataset Catalog/Main Filter Flow는 MongoDB의 현재 v6 Domain Package를 base로 section-bounded patch를 수행합니다. 별도 Domain Policy Authoring Flow는 제공하지 않으며, 업무별 해석 규칙은 각 Flow의 특화 Prompt Template에서 관리합니다.
