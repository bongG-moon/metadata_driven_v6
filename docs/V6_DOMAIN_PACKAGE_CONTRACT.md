# v6 Domain Package와 Mongo 저장 계약

## 1. 목적

분석 Core는 특정 공정 이름을 소유하지 않는다. 사용자는 기존처럼 정형화되지 않은 Domain·Dataset·Main Filter 자연어 TXT를 입력한다. 외부 작업별 Authoring Prompt는 각 원문에 LLM을 최대 한 번씩 호출하지만 실행 metadata를 자유 생성하지 않는다. Domain은 표시명·설명 annotation only, Dataset은 compact Dataset IR, Main Filter는 `target_type` 필수 typed alias IR을 반환한다. 결정론적 engine이 `metadata.authoring.source-registry.v3`의 compiler-owned `semantic_templates`, dataset descriptor와 Source binding으로 세 결과를 확장·병합해 full draft를 컴파일한다. 정확성과 저장 권한은 LLM이 아니라 registry hash, schema·semantic·dependency·security compiler와 3컬렉션 transaction writer가 책임진다.

```text
자유형 자연어 TXT bundle
  → immutable source + bounded authoring context
  → Domain annotation / compact Dataset IR / typed Main Filter IR
  → branch별 외부 공통 Prompt + Authoring LLM 최대 1회
  → Source Registry v3 semantic_templates/descriptor deterministic expansion
  → closed full metadata draft
  → compile_domain_package(...)
  → schema + semantic lint + dependency/security closure
  → immutable domain.package.v1
  → domain/table_catalog/main_filter 항목 문서
  → 3컬렉션 transaction save
  → load_domain_package_from_three_collections(...)
```

작업자는 JSON Schema, canonical ID inventory, relation endpoint, field-role 또는 hash 문법을 직접 맞추지 않는다. 최초 bootstrap에는 기존 Domain·Dataset·Main Filter TXT를 합친 bundle 또는 같은 정보를 충분히 담은 완전한 도메인 설명이 필요하다. 정보가 부족하면 `status=needs_clarification`의 `missing_fields`/질문으로 누락 항목을 설명하고 draft/candidate/persist와 repair/fallback LLM 없이 끝낸다.

`source_grounding_mode=explicit_inventory`는 선택적 고신뢰 lane이다. 이 mode에서 운영자는 완전한 inventory로 zero-LLM compile을 시도할 수 있다. 관리자 검토 `metadata.executable-blueprint.v1`과 외부 SHA-256 pin을 쓰는 lane도 Domain의 annotation-only schema는 그대로 유지하면서 executable 불변성과 provenance를 추가 증명한다. Blueprint/pin은 일반 작업자 입력이나 기본 free-form lane의 필수 조건이 아니다.

Authoring 결과는 검증된 Domain Package로만 runtime에 들어간다. 분석 질문은 이 package에서 Typed Execution IR을 컴파일해 결정론적으로 실행하며 pandas 코드 생성 LLM과 repair LLM은 호출하지 않는다.

## 2. 공개 Python API와 optional Blueprint lane

기본 free-form lane의 Langflow 경계는 `Authoring Runtime Context → 외부 공통 Prompt → Conditional LLM Invoker → branch별 annotation/compact-IR decoder → Source Registry v3 expander → compile_domain_package`다. Prompt와 LLM raw output, compiler-owned `semantic_templates`는 provider/state/trace에 복제하지 않고 source/prompt/model/template hash와 compile evidence만 provenance에 남긴다.

Decoder 입력은 `metadata.authoring.proposal.v1`이며 `complete(source_sha256,draft)` 또는 `needs_clarification(source_sha256,clarification)` 둘 중 하나다. 후자에는 1~3개 질문과 bounded missing fields만 허용하고 compile/prepare/writer를 호출하지 않는다.

아래 API는 기본 bootstrap이 아니라 Blueprint/pin 고신뢰 lane에서 동일 Domain annotation에 external executable pin 검증을 추가하는 예다.

```python
from reference_runtime.authoring_blueprint import (
    merge_blueprint_annotations,
    validate_executable_blueprint,
)
from reference_runtime.authoring_source_manifest import extract_authoring_source_manifest
from reference_runtime.domain_packages import (
    build_runtime_catalog_v2,
    compile_domain_package,
    load_active_domain_bundle,
    make_active_pointer_document,
    make_bundle_document,
)

source_manifest = extract_authoring_source_manifest(source_text)
trusted_blueprint = validate_executable_blueprint(
    blueprint,
    expected_blueprint_sha256=admin_configured_blueprint_sha256,
    expected_domain_id="order_sales",
    expected_environment="production",
    source_manifest=source_manifest,
)
authoring_payload = merge_blueprint_annotations(
    trusted_blueprint,
    {"display_name": "주문·매출 분석", "description": "주문과 매출을 분석합니다."},
    expected_blueprint_sha256=admin_configured_blueprint_sha256,
    expected_domain_id="order_sales",
    expected_environment="production",
    source_manifest=source_manifest,
)
package = compile_domain_package(
    authoring_payload,
    domain_id="order_sales",
    environment="production",
    revision=1,
    lifecycle_status="validated",
)
runtime_catalog = build_runtime_catalog_v2(package)
bundle_document = make_bundle_document(package)
active_pointer = make_active_pointer_document(package)
```

`compile_domain_package` 결과에는 항상 다음 pin이 함께 있다.

- `domain_id`
- `environment`
- `revision`
- `authoring_sha256`
- `runtime_catalog.catalog_sha256`
- `package_sha256`
- `bundle_sha256`

## 3. CLI

주문·매출 optional trusted Blueprint와 외부 pin의 재현성 검사:

```powershell
python tools/build_executable_blueprint.py --check
```

관리자 검토용 기준 파일은 다음 두 개다.

- `metadata/domain_packs/order_sales/trusted_executable_blueprint.json`
- `metadata/domain_packs/order_sales/trusted_executable_blueprint.sha256`

Blueprint와 Source Registry v3 `semantic_templates` 생성은 배포·관리자 작업이며 webhook/API 요청이나 authoring LLM이 수행하지 않는다. 검토된 executable/source/template projection이 바뀌면 새 blueprint, v3 registry와 provenance hash를 만들고 다시 승인해야 한다. 기본 free-form lane의 작업자에게 이 fixture나 pin 문법을 요구하지 않는다.

주문·매출 package fixture:

```powershell
python tools/compile_metadata.py `
  --draft-json metadata/domain_packs/order_sales/authoring_draft.json `
  --domain-id order_sales `
  --environment test `
  --output-dir metadata/domain_packs/order_sales/compiled
```

제조 v1 호환 catalog와 제조 v2 package 동시 재생성:

```powershell
python tools/compile_metadata.py
```

## 4. Authoring Flow wire shape

기본 Full-domain bootstrap의 LLM 출력은 하나의 full-draft가 아니다. Domain 출력은 `contracts/schemas/metadata-annotation-proposal.schema.json`의 `display_name`/`description` 두 키, Dataset 출력은 `metadata-bootstrap-dataset-ir.schema.json`, Main Filter 출력은 `metadata-bootstrap-main-filter-ir.schema.json`과 정확히 일치해야 한다. Main Filter의 각 항목에는 `target_type`이 필수다. SQL/Python/credential/active pointer/승인 정보와 실행 metric/relation/recipe/planner policy는 어느 branch도 만들 수 없다.

`metadata.authoring.source-registry.v3`는 LLM용 `semantic_vocabulary`와 compiler 전용 `semantic_templates`를 분리한다. Compiler는 Domain annotation에 template의 metric/relation/grain/ordering/predicate/recipe/entity-group/alias를 붙이고 Dataset/Main Filter IR을 승인 descriptor/alias card로 확장한다. 확장된 완전한 draft만 `contracts/schemas/metadata-authoring-draft.schema.json`과 전체 semantic·dependency·security compiler를 통과한 경우 candidate가 된다. Optional Blueprint lane은 이 annotation 계약을 넓히지 않고 검증된 Blueprint의 executable canonical bytes 불변성을 추가 확인한다.

`metadata.executable-blueprint.v1` envelope는 다음 값을 정확히 봉인한다.

- `domain_id`, `environment`
- `executable`, `default_annotations`
- `source_manifest_sha256`
- `executable_sha256`, `blueprint_sha256`

Self-hash만으로는 신뢰할 수 없다. 공격자가 executable과 내부 hash를 함께 다시 계산할 수 있기 때문에 `trusted_blueprint_sha256`은 Langflow 관리자 node config 또는 승인된 registry에서 별도로 공급해야 한다. Validator는 내부 self-hash와 이 외부 pin을 모두 검사한다.

Full draft가 표현하고 compiler가 검증하는 실행 section은 다음과 같다. 기본 bootstrap에서는 Source Registry v3 `semantic_templates`와 dataset descriptor가 이를 소유하며, Blueprint lane에서는 동일 실행 section에 external pin 증명이 추가된다.

- dataset: `source_type`, `source_adapter`, `field bindings`, `date_policy`, read-only policy
- field: `semantic_type`, `roles`, `aliases`, exact physical binding
- metric: source field/binding, aggregation, additivity
- semantic: entities/groups, grains, orderings, predicates
- relation: left/right dataset와 key, join type, cardinality
- recipe: intent aliases, required slots, typed operation template
- 확장 입력: `prompt_extensions`, `specialized_functions`, `output_profile`

`semantic_templates.planner_policy`는 compiler-owned sealed section이다. `planner_profile`과 optional `legacy_catalog_sha256`은 Domain annotation, Dataset/Main Filter IR 또는 Domain Policy의 `output_profile_json`로 변경할 수 없다.

Specialized function card는 코드를 담지 않고 `function_id`, version, implementation/registry-entry SHA-256, typed input/output schema ref와 hash, selection evidence/ambiguity, required field/role, argument binding, output contract와 resource policy만 담는다. exact build-time standalone registry와 일치하지 않으면 저장·활성화할 수 없다.

### 4.1 분리된 Authoring Flow도 같은 Domain Package를 갱신한다

네 Authoring Flow는 서로 다른 runtime 저장소를 만들지 않는다.

- Domain Authoring: 자유형 source bundle에서 LLM 최대 1회로 표시명·설명 annotation만 만들고, Source Registry v3 `semantic_templates`를 결정론적으로 결합한 뒤 전체 compiler를 실행한다. Optional Blueprint lane도 같은 두 annotation 필드만 허용한다.
- Dataset Catalog Authoring: 현재 세 collection package를 exact hash로 읽고 `datasets` section만 upsert한다.
- Main Filter Authoring: 같은 current package를 읽고 `aliases`, `entity_groups`, `grains`, `orderings`, `predicates`, `recipes` section만 upsert한다.
- Domain Policy Authoring: 별도 Flow의 전용 관리자 입력 `intent_prompt_extension`, `answer_prompt_extension`, `specialized_functions_json`, `output_profile_json`만 적용한다. Prompt Template/Composer/envelope/LLM은 0회이며 Domain annotation이나 Dataset/Main Filter IR은 이 section을 바꿀 수 없다. `output_profile_json`도 sealed planner policy key를 포함하면 거부한다.

부분 등록은 세 current collection의 항목에서 결합한 catalog를 `runtime_catalog_v2_to_authoring_draft()`로 완전한 authoring draft로 복원한 뒤 `apply_authoring_section_patch()`를 적용한다. 삭제 지시, 다른 Flow가 소유한 section, 빈 patch는 거부한다. 결과는 항상 전체 `compile_domain_package()`와 schema·semantic lint·dependency closure를 다시 통과하고 항목 단위로 다시 저장된다. `legacy_projection_v1`은 별도 migration tool에서만 처리하며 Langflow authoring runtime은 `domain_package_v2`만 허용한다.

Domain/Dataset/Main Filter LLM 경로는 작업별 공통·특화 Prompt Template을 별도 node/source/hash/edge로 유지한다. 특화 업무 규칙은 각 특화 Template 본문에 직접 작성하고 모든 Prompt Template은 변수 없이 렌더링한다. 자연어 source context는 Context Builder에서 Composer의 `runtime_context`로 정확히 한 번 전달한다. Domain Policy는 prompt node/Composer/envelope/provider를 실행하지 않는다. Main Filter는 `source_grounding_mode=explicit_inventory`의 완전한 binding proof가 있을 때만 선택적으로 zero-LLM compile한다.

`specialized_functions`의 실행 계약은 card 저장에서 끝나지 않는다. Registry attestation을 통과한 card만 bounded candidate가 되고 Intent는 candidate ID만 선택한다. Plan Compiler는 exact function/registry/I/O-schema/resource pin의 `registered_call` Typed IR을 만들며 Registered Function Gateway가 build-time allowlisted standalone 구현, typed argument, field/role, timeout/row limit, output schema와 lineage를 검증해 실행한다. dynamic import, metadata code, `eval`/`exec`, arbitrary network/file/subprocess와 미등록 fallback은 금지한다. 이 전체 consumer chain과 positive/negative E2E가 없으면 card를 실행 가능 기능으로 노출·활성화하지 않는다.

### 4.2 Generic Flow 기본값과 운영 provisioning

배포되는 generic Domain Authoring Flow의 기본값은 free-form lane이다. `trusted_blueprint_json`과 `trusted_blueprint_sha256`이 비어 있어도 자연어 Domain annotation과 registry-template expansion prepare를 수행해야 한다. 특정 도메인의 template는 공유 core에 하드코딩하지 않고 활성 provisioning의 승인 Source Registry v3로 주입한다.

운영자가 Blueprint 고신뢰 lane을 명시적으로 선택한 경우에만 blueprint와 pin을 관리자 node config 또는 승인된 registry resolver로 함께 주입한다. 이 mode에서만 누락된 Blueprint/pin이 `metadata_blueprint_required`다. 일반 사용자가 입력하는 자연어 Message에는 mode, Blueprint 본문, pin, registry template 또는 canonical ID를 넣지 않는다.

### 4.3 API와 tweak 보안 경계

Public API request는 자유형 자연어 `input_message`와 공개 authoring context만 받는다. `source_grounding_mode`, `trusted_blueprint_json`, `trusted_blueprint_sha256`, Mongo URI, approval payload, policy 관리자 입력은 public request schema와 일반 tweak allowlist에서 제외한다. Gateway는 해당 node input을 덮어쓰려는 요청을 거부해야 한다. Optional Blueprint lane의 pin을 API body에서 읽어 검증기에 전달하면 공격자가 executable과 hash를 함께 교체할 수 있으므로 외부 trust anchor가 아니다.

관리자 설정을 변경할 권한은 Flow/registry 운영 ACL로 제한하고 audit에 남긴다. Optional Blueprint lane의 설정을 바꾸면 새 Blueprint pin과 회귀 검증을 거쳐야 하며, 이전 `validate_only` 결과를 새 source나 설정에 맞춰 자동 수정하거나 그대로 `save` 입력으로 재사용하지 않는다.

## 5. MongoDB 3컬렉션 계약

| 역할 | collection | key |
| --- | --- | --- |
| 도메인 metadata current | `agent_v6_domain_metadata` | `{environment}:{domain_id}` |
| 테이블 카탈로그 current | `agent_v6_table_catalog` | `{environment}:{domain_id}` |
| 메인필터 current | `agent_v6_main_filter` | `{environment}:{domain_id}` |

세 current collection은 항목 문서를 보관한다. `01 사용 가능 메타데이터 불러오기`는 MongoDB URI·database·세 collection 이름·timeout을 입력받고 모든 항목을 읽어 Domain Package를 메모리에서 컴파일한다. collection 이름은 안전한 형식이며 서로 달라야 한다. domain/environment/source mode는 UI에 노출하지 않으며 필수 항목 누락, 중복 key, 지원하지 않는 section, typed payload 오류가 있으면 실행하지 않는다. active pointer와 immutable bundle/pending collection은 runtime 필수 계약이 아니다.

## 6. 검증 / 저장 연결

1. 기본 Full-domain 등록은 세 자유형 원문을 각각 bounded context로 만들고 작업별 외부 공통·특화 Prompt pair를 통해 LLM을 각각 최대 한 번, 총 3회 호출한다.
2. Domain annotation, compact Dataset IR, `target_type` 필수 Main Filter IR을 각각 closed decode한다. Invalid/missing output은 repair 없이 실패한다.
3. Source Registry v3를 결정론적으로 확장·병합한 뒤 전체 schema·semantic·dependency·security compiler를 실행한다.
4. 성공한 package를 domain/table catalog/main filter section으로 나누고 각 자연어 원문과 hash를 보존한다.
5. 전체 runtime catalog 검증 후 MongoDB 저장용 항목 문서를 만든다. runtime hash는 메모리에서만 사용한다.
6. 한 MongoDB transaction에서 세 current 문서를 교체하고 같은 transaction 안에서 다시 읽어 package 동치를 검증한다.
7. `validate_only` 또는 dry-run이면 동일 검증을 수행하되 write하지 않는다. clarification/error이면 항상 write 0건이다.

세부 문서 필드와 운영 절차는 [V6_THREE_COLLECTION_METADATA.md](V6_THREE_COLLECTION_METADATA.md)를 따른다.

## 7. v5 migration

```powershell
# Mongo read-only, 로컬 plan/evidence만 생성
python tools/migrate_v5_metadata.py --read-v5-mongo `
  --output-dir validation_outputs/live_v5_migration

```

기존 migration tool의 candidate/active-pointer write 옵션은 새 runtime 저장 계약이 아니므로 사용하지 않는다. 승인된 migration 결과는 자연어 Authoring Flow 또는 별도 검토된 3컬렉션 importer로 전체 Domain Package를 다시 compile한 뒤 항목 문서로 저장해야 한다.

고정 v5 source collection은 세 개뿐이며 모든 실행에서 `v5_write_operations=0`이어야 한다.

- `agent_v4_domain_items`
- `agent_v4_table_catalog_items`
- `agent_v4_main_flow_filters`

Migration은 가능한 문서를 domain/dataset/filter typed candidate로 변환한다. 식별자 또는 typed payload가 없거나 credential·실행 코드를 포함한 문서만 quarantine한다. Query body는 v6 metadata에 복사하지 않고 SHA-256과 registry review 대상으로만 남긴다.

## 8. 제공 Domain Pack

- `metadata/domain_packs/manufacturing`: 기존 제조 catalog를 격리한 호환 pack과 v2 compiled package
- `metadata/domain_packs/order_sales`: `orders`, `products`, `refunds`, `targets`로 구성된 비제조 범용성 검증 pack

주문·매출 pack은 aggregate, filter, top/bottom N, argmax/argmin ties, join, projection, field comparison, multi-turn 검증용 canonical field/metric/relation을 제공한다.
