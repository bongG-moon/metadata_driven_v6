# v6 메타데이터 작성 구조 경계 최종안

> **과거 검증 스냅샷(현재 기본 계약 아님)** — 이 문서는 Blueprint 필수안을 평가하던 당시의 실패 증적을 보존한다. 현재 작업자 기본 경로는 자유형 TXT → 외부 Prompt → `metadata.authoring.proposal.v1` LLM 1회 → 결정론적 검증/컴파일이며, Blueprint/pin은 선택적 고신뢰 경로다. 현재 계약은 `harness/harness.md`와 `docs/V6_METADATA_AUTHORING_GUIDE.md`를 따른다.

## 결론

LLM이 `metadata.authoring.draft.v1` 전체를 직접 생성하게 두면 동일 모델과 동일 프롬프트에서도 relation, field role, formula, grain, recipe 구조가 달라졌다. 개별 누락을 normalizer로 계속 보정하는 경로는 폐기한다.

이 문서에서 제안한 Full-domain Blueprint 필수안은 현재 기본 경로에서는 채택하지 않았다. 다만 자연어를 입력했다는 사실이 곧 새 실행 semantics를 승인했다는 뜻은 아니며, Dataset/Main Filter의 좁은 active-package section patch와 Domain Policy 전용 관리자 입력은 현재도 별도 ownership 경계로 유지한다.

## 실제 Gemini 검증에서 확인된 변동

동일한 `gemini-3.5-flash-lite`, temperature 0, 동일 standalone Flow 프롬프트를 반복 실행했을 때 실패 지점이 다음처럼 이동했다.

1. relation endpoint 필드가 `left_dataset/right_dataset` 대신 `left/right`로 생성됨
2. field role에 schema 밖 값이 생성됨
3. relation cardinality와 key가 등록 계약과 다르게 생성됨
4. grain key가 등록 field를 벗어남
5. `ACHIEVEMENT_RATE` formula가 누락됨
6. predicate/entity group/recipe 구조가 실행마다 추가되거나 누락됨

따라서 source 문장마다 parser 규칙을 늘리거나 repair LLM을 호출하는 방식으로는 모델 독립적인 실행 정확성을 만들 수 없다.

## Trusted Blueprint 계약

`metadata.executable-blueprint.v1` envelope는 다음 exact field를 가진다.

- `contract_version`
- `domain_id`, `environment`
- `executable`, `default_annotations`
- `source_manifest_sha256`
- `executable_sha256`, `blueprint_sha256`

`executable`은 draft의 다음 section을 모두 포함한다.

- `contract_version`, `locale`, `timezone`
- `datasets`, `metrics`, `entity_groups`, `grains`
- `relations`, `orderings`, `predicates`, `recipes`, `aliases`
- `prompt_extensions`, `specialized_functions`, `output_profile`, `source_provenance`

Source manifest의 inventory와 coverage 검사는 Blueprint가 자연어 기준문서에 등록된 dataset/field/metric/relation/grain/recipe/alias를 빠뜨리지 않았다는 evidence로 유지한다. 그러나 manifest parser가 formula AST, recipe template 등 전체 실행 구조를 원문에서 새로 발명하지는 않는다. 그 구조는 review된 Blueprint가 소유한다.

Blueprint self-hash만으로는 신뢰 경계가 되지 않는다. 공격자는 executable을 바꾸고 내부 hash도 다시 계산할 수 있다. `expected_blueprint_sha256`은 Message/API가 아니라 Langflow 관리자 node config 또는 승인된 registry에서 독립적으로 공급한다. Validator는 다음을 모두 exact match로 확인한다.

- external Blueprint pin
- Blueprint self-hash와 executable hash
- domain ID와 environment pin
- 현재 자연어 source manifest hash
- closed schema, source coverage, semantic compile

## Full-domain 작성 Flow

```text
자연어 TXT
  -> deterministic source manifest
  -> admin-only trusted_blueprint_json + external SHA-256 pin
  -> pin/hash/schema/coverage/semantic pre-validation
  -> Gemini 1회: {display_name, description} only
  -> closed annotation schema
  -> reviewed executable deepcopy + annotation merge
  -> executable canonical bytes/hash exact check
  -> full domain package compile
  -> immutable prepare candidate
  -> external approve
  -> atomic execute / active pointer CAS
```

Blueprint 또는 external pin이 없거나 잘못되면 `metadata_blueprint_required` 또는 Blueprint validation error로 모델 호출 전에 실패한다. Annotation에 dataset, metric, relation, alias, prompt, function, output policy 등 다른 키가 하나라도 있거나 두 문자열 계약이 잘못되면 저장하지 않는다. Repair LLM은 호출하지 않는다.

Generic export의 `trusted_blueprint_json`과 `trusted_blueprint_sha256` 기본값은 빈 값이다. 운영 provisioning 전에는 어떤 특정 도메인도 암묵적으로 등록하지 않는다. 주문·매출 검증 fixture는 다음 위치에 있다.

- `metadata/domain_packs/order_sales/trusted_executable_blueprint.json`
- `metadata/domain_packs/order_sales/trusted_executable_blueprint.sha256`
- 재현성 검사: `python tools/build_executable_blueprint.py --check`

## 부분 갱신 ownership

- Dataset Catalog: exact active package를 읽고 `datasets` section만 upsert한다.
- Main Filter: exact active package를 읽고 `aliases`, `entity_groups`, `grains`, `orderings`, `predicates`, `recipes`만 upsert한다.
- Domain Policy: `authoring_kind=domain_policy` 전용 관리자 입력만 `prompt_extensions`, `specialized_functions`, `output_profile`에 적용한다.

부분 갱신은 다른 section을 byte-exact 보존하고 전체 schema, source coverage, semantic lint, dependency closure와 domain package compile을 다시 실행한다. 별도 `active:{kind}` 저장소를 만들지 않고 하나의 `active:{environment}:{domain_id}`를 갱신한다.

## API와 tweak 경계

Public webhook/API에는 자연어 Message와 공개 authoring context만 허용한다. 다음 값은 request body와 일반 Langflow tweak allowlist에서 제외한다.

- `trusted_blueprint_json`, `trusted_blueprint_sha256`
- Mongo URI와 registry secret
- approval event/pending payload 내부 값
- Domain Policy 관리자 입력

Blueprint와 pin을 같은 API 요청에서 받으면 공격자가 둘을 함께 다시 계산할 수 있으므로 external trust anchor가 아니다. Gateway와 Flow 운영 ACL은 해당 node input override를 거부하고 관리자 변경을 audit해야 한다.

## Prepare / approve / execute hash 불변성

Prepare candidate에는 compiled package와 bundle document뿐 아니라 Blueprint/executable 검증 결과, source-manifest coverage, expected active revision/hash, dependency pin, 준비/만료 시각을 포함한다. 이 material 전체의 canonical JSON hash가 `candidate_sha256`이다.

Approve는 candidate hash만 승인하며 draft나 Blueprint 수정 API를 제공하지 않는다. Execute는 저장된 candidate bytes와 package/catalog/bundle/active-base hash를 다시 계산하고, 새 Blueprint나 annotation payload를 받지 않는다. 불일치나 만료는 stale/failed로 종료한다. 변경된 Blueprint를 반영하려면 새 prepare와 새 승인이 필요하다.

## 검증 기준

- Full-domain natural-language authoring: Domain·Dataset·Main Filter 분기별 Gemini 1회, 총 정확히 3회, repair 0회
- missing/wrong Blueprint, source/domain/environment mismatch: Gemini 0회 fail-closed
- annotation proposal closed schema와 executable before/after byte/hash exact
- 공격자가 executable과 내부 hash를 함께 재계산해도 external pin mismatch로 거부
- source manifest coverage와 full draft/package/catalog standalone compiler parity
- 기준 질문의 typed Execution IR 및 결과 row/column exact 검증
- deterministic/unsupported 질문의 Intent LLM 0회
- ambiguity 질문의 Intent LLM은 sealed candidate ID 선택 1회만 허용
- pandas code/repair LLM은 항상 0회
- raw source, provider prompt/response, credential은 report에 저장하지 않음
- 실제 Mongo 검증은 nonce가 붙은 격리 environment만 사용하고 production active pointer는 변경하지 않음
