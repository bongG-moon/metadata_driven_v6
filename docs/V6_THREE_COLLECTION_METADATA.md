# v6 자연어 Metadata 3컬렉션 구현 가이드

## 결정

v6 runtime metadata는 active pointer나 bundle/pending collection을 요구하지 않는다. 운영자가 관리하는 current metadata는 아래 세 MongoDB collection으로 고정한다.

| Collection | 자연어 원문 | 정규화 영역 |
| --- | --- | --- |
| `agent_v6_domain_metadata` | 도메인 TXT와 정책 변경 사유 | domain identity, metric, relation, grain, ordering, recipe, prompt extension, 등록 함수 descriptor, output profile |
| `agent_v6_table_catalog` | Dataset/Table TXT | dataset와 canonical field binding |
| `agent_v6_main_filter` | Main Filter TXT | predicate와 alias |

분석 결과와 멀티턴 상태는 metadata가 아니므로 기존 `agent_v6_result_store`, `agent_v6_session_state`를 그대로 사용한다. Source adapter의 secret, 실제 query와 raw data는 세 metadata collection에 넣지 않는다.

## 자연어 등록 흐름

1. 작업자는 기존 TXT처럼 자유로운 업무 문장을 입력한다. JSON, ID, 컬럼 타입, DSL을 요구하지 않는다.
2. Domain/Dataset/Main Filter별 외부 공통 Prompt Template과 특화 Prompt Template이 자연어를 closed annotation/IR로 변환한다. 두 Template은 별도 node/source/hash/edge이며 특화 업무 규칙은 특화 Template 본문에 직접 작성한다. 자연어 runtime context는 Composer에 한 번만 연결하고 프롬프트 지시문은 custom component 안에 두지 않는다.
3. 기본 Full-domain bootstrap은 Gemini `gemini-3.5-flash-lite`를 분기별 1회, 총 3회까지 사용한다. 후속 Dataset/Main Filter 등록은 최대 1회, Domain Policy는 0회다. 자동 retry, repair, pandas code generation은 없다.
4. 결정론적 compiler가 승인 Source Registry의 template/descriptor를 결합하고 schema, identity, field binding, dependency, join/cardinality, security와 section ownership을 검증한다.
5. 모호하거나 누락된 의미가 있으면 `needs_clarification`을 반환하고 MongoDB write는 수행하지 않는다.
6. 성공한 full package를 세 section으로 나누고 MongoDB transaction에서 같은 `_id=environment:domain_id`로 함께 교체한다.

## 문서 계약

세 문서는 공통으로 다음 필드를 가진다.

- `contract_version=metadata.section.v1`
- `section_kind=domain|table_catalog|main_filter`
- `domain_id`, `environment`, `revision`
- `source_text`, `source_sha256`
- `normalized_metadata`, `section_sha256`
- 동일한 `release_id`와 `release_manifest`
- `release_manifest_sha256`, `document_sha256`
- runtime package의 공통 identity/hash인 `package_meta`

`release_manifest`는 세 section hash와 `catalog_sha256`, `package_sha256`, `bundle_sha256`를 봉인한다. Loader는 domain collection의 최신 문서에서 identity를 자동 선택하고, 같은 identity의 table catalog/main filter 문서를 읽어 세 문서의 revision/release/manifest/hash가 모두 일치할 때만 하나의 Domain Package로 결합한다. 한 collection만 수동 수정하거나 일부 write만 반영되면 분석을 실행하지 않는다.

## Langflow node 계약

- `메타데이터 등록 프롬프트 컨텍스트`: 자유형 TXT를 bounded runtime context로 만든다.
- 외부 공통/특화 Prompt Template: 실제 LLM instruction을 소유한다.
- `조건부 LLM 호출`: 필요한 분기만 호출한다.
- `메타데이터 등록 엔진`: LLM 결과를 closed decode하고 deterministic compile/validation 후 세 collection을 transaction 저장한다.
- `01 사용 가능 메타데이터 불러오기`: MongoDB URI·database·timeout만 입력받고, 고정된 세 collection에서 가장 최근의 완전한 동일 release를 자동 검증·결합해 Data Analysis Flow에 전달한다. domain/environment/source mode/collection 이름은 UI 입력이 아니다.
- `메타데이터 등록 메시지 구성`: 저장/검증/clarification/error 결과를 한글 Message로 표시한다.

등록 엔진의 `mode=save`가 기본이다. `mode=validate_only` 또는 `dry_run=true`는 동일한 compile/release 검증을 수행하되 write하지 않는다.

## 검증 DB

운영 기본 DB는 `MONGODB_DATABASE=datagov`다. 자동화 및 live 검증은 `MONGODB_VALIDATION_DATABASE=datagov_v6_validation`을 우선 사용한다. DB를 분리하는 이유는 테스트 revision, 실패 주입, 임시 도메인이 운영 current 문서를 교체하지 않도록 하기 위해서다. collection schema와 loader 경로는 운영과 동일하므로 DB 분리는 기능 차이가 아니라 데이터 안전 경계다.

## 단순화의 트레이드오프

이 구조는 조회와 운영 관리가 단순하지만 자동 revision history, 승인 대기열, active pointer 기반 rollback을 제공하지 않는다. 이력이 필요하면 MongoDB change stream/백업 또는 별도 감사 시스템을 붙인다. 이것을 runtime metadata 조회의 필수 collection으로 되돌리지는 않는다.
