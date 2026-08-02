# metadata_driven_v6 Langflow 1.9.2 import bundle

이 폴더는 `flow.inventory.v1`에서 생성된 정확히 다섯 개의 standalone Flow를 포함합니다.
`00_metadata_driven_v6_complete_ALL_FLOWS.json`을 한 번에 import하거나 번호 순서대로 개별 JSON을 import합니다.

- Python 3.12
- langflow 1.9.2
- langflow-base 0.9.2
- lfx 0.4.2

Flow JSON에는 credential 값이나 domain-specific blueprint가 없습니다. import 후 운영자가 필요한 Langflow node input 또는 Global Variable을 연결합니다.

기본 Domain Authoring은 작업자가 자유롭게 작성한 Domain/Dataset/Main Filter 자연어 bundle 또는 완전한 도메인 설명을 외부 공통 Prompt로 변환하고, LLM 최대 1회의 closed full draft를 결정론적 compiler가 검증합니다. 작업자에게 JSON, inventory 선언 문법, Blueprint나 pin을 요구하지 마십시오.
`source_grounding_mode=explicit_inventory`를 명시한 optional 고신뢰 lane에서만 승인된 registry의 blueprint JSON과 별도 SHA-256 pin을 Domain Authoring node의 `trusted_blueprint_json`, `trusted_blueprint_sha256` admin 입력에 설정합니다. 이 값은 ChatInput, Run Flow API payload 또는 일반 사용자 tweak에서 받지 마십시오. 공개 gateway는 mode와 admin input의 arbitrary tweak를 차단해야 합니다.
검증용 order_sales Blueprint와 `.sha256` 파일은 이 optional lane의 예시입니다. Dataset Catalog/Main Filter Flow는 MongoDB의 exact active v6 Domain Package를 base로 section-bounded patch를 수행합니다.
Domain Policy Authoring Flow는 Prompt/Language Model 노드 없이 운영자 입력만 검증하며 raw Python 대신 등록된 function descriptor만 허용합니다.
