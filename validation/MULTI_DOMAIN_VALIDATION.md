# v6 다중 도메인·실제 Gemini 검증 계약

> **과거 검증 스냅샷** — 아래 annotation/manifest 중심 결과는 이전 고신뢰 lane 검증 기록이다. 현재 기본 등록 검증은 자유형 TXT bundle과 `metadata.authoring.proposal.v1`의 complete/needs_clarification 계약을 사용하며, Blueprint/explicit inventory는 선택 검증으로만 유지한다.

## 목적

제조업 질문 70개 회귀 검증과 별도로 `order_sales` 도메인을 사용해 범용 metadata 계약을 검증한다. 검증은 Langflow export의 실제 node 순서와 동일한 standalone component 경로를 사용한다.

## 기준 모델

- Full-domain annotation, Dataset patch 및 non-alias-only Main Filter bounded patch: `gemini-3.5-flash-lite`
- source-sealed alias-only Main Filter patch: deterministic compile, LLM 0회
- Domain Policy: explicit admin node input, LLM 0회
- 모호한 질문의 closed candidate 선택: `gemini-3.5-flash-lite`
- 선택적 narrative 생성: `gemini-3.5-flash-lite`
- pandas code 생성 및 repair: 호출 금지

provider 호출 증거에는 model ID, lane별 호출 횟수, prompt/response SHA-256, provider가 반환한 token count만 저장한다. API key, prompt 원문, 응답 원문, 자연어 metadata 원문은 저장하지 않는다.

## 검증 자료

- `validation/cases.jsonl`: 기존 제조 70개 canonical corpus
- `validation/order_sales_validation_cases.jsonl`: 주문·매출 다중 도메인 corpus
- `metadata/domain_packs/order_sales/`: 등록·활성화할 주문·매출 Domain Package와 fixture

주문·매출 corpus는 다음을 포함한다.

- 합계와 날짜 조건
- 상위·하위 N
- 최대·최소 동률 전체 반환
- 주문·상품·환불·목표 dataset join
- projection과 컬럼 간 값 비교
- 순매출액과 달성률 typed formula
- 이전 결과만 사용하는 무조회 follow-up
- 이전 결과 enrichment와 dimension 전환
- intent LLM, narrative LLM, unsupported의 정확한 호출 횟수

## Offline 검증

```powershell
python tools/validate_langflow_equivalent_pipeline.py --execute-components --execute-multiturn --execute-cases
python tools/validate_order_sales_component_cases.py
python tools/validate_api_terminal_fail_closed.py
python tools/validate_prompt_extension_runtime.py
python tools/validate_generic_v2_support_pipeline.py
pytest tests/test_validation_live_and_multidomain.py tests/test_generic_v2_candidates.py tests/test_generic_v2_p1_boundaries.py tests/test_http_authoring_validator_contracts.py
```

Offline 검증은 외부 provider를 호출하지 않는다. Flow graph, stage 경계, route oracle, typed IR, state, Message/API/GaiA 동치를 확인한다.
`validate_order_sales_component_cases.py`는 OS01~OS14 전부를 실제 sample
rows로 실행한다. 합계, 상·하위 N, 동률, 정렬, projection, 환불/목표 join,
순매출/달성률, 컬럼 비교, 등록된 category value mapping, threshold projection,
claim-safe narrative 1회와 unsupported 0회 호출을 exact row·exact column으로
검증한다. compact 순매출/달성률 probe는 dependency metric이 결과에 불필요하게
노출되지 않는지도 확인한다. API terminal 검증은 유효 응답은
바이트 의미를 바꾸지 않고 통과시키되 hash 변조와 schema 변조는 fail-closed로
차단해야 한다. prompt extension 검증 report에는 원문 대신 SHA-256과 UTF-8
byte count만 남긴다.

`validate_generic_v2_support_pipeline.py`는 배포 domain pack과 무관한 세 번째
`support_tickets` catalog를 사용해 candidate → deterministic route → intent →
plan → typed executor를 끝까지 실행한다. bundle hash, prompt-card extra field,
unknown candidate, catalog hash, unregistered plan operator 변조가 각각
fail-closed인지도 함께 확인한다.

`test_generic_v2_p1_boundaries.py`는 긴 alias 우선 선택, catalog field alias 기반
literal의 job pushdown+typed filter 이중 적용, 최소 required-field closure,
동일 family의 current/history 선택, unpinned `오늘`의 비결정론, intent/catalog
dependency pin, plan fingerprint 변조, legacy compatibility spoof를 검증한다.
anonymous multi-turn은 export 기본값이 꺼져 있어야 하며 offline/HTTP 검증에서만
20자 이상 고유 session ID와 함께 명시적으로 켠다.

## 실제 Gemini authoring 검증

모든 실제 Gemini 검증은 `gemini-3.5-flash-lite`, temperature `0`, candidate 1개로 고정한다. CLI에 다른 모델을 전달하면 API 호출 전에 실패하며 대체 모델 목록과 provider fallback은 비활성화한다. 보고서에는 요청 모델 계약과 provider `modelVersion` 일치 여부를 함께 남긴다.

실호출 전에 v6 자연어 입력 4종의 존재, legacy 의미 보존, 정책 섹션과 secret 부재를 offline으로 확인한다.

```powershell
python tools/validate_live_v6_authoring_inputs.py `
  --output validation_outputs/v6_authoring_inputs.json
```

```powershell
python tools/validate_live_blueprint_authoring.py `
  --model gemini-3.5-flash-lite `
  --output validation_outputs/live_blueprint_authoring_final.json
```

Full-domain 검증은 자연어 TXT에서 source manifest를 컴파일한 뒤 관리자 Blueprint와 별도 SHA-256 pin을 LLM 호출 전에 검증한다. provider 호출은 `display_name`·`description` annotation 제안 1회, repair 0회이며 executable canonical bytes/hash는 전후 동일해야 한다. missing/wrong pin, domain/environment/source mismatch, 단순·재계산 executable tamper, annotation executable injection은 모두 model 호출 0회로 fail-closed여야 한다. provider 응답은 같은 standalone authoring component에 local replay하여 prepared candidate까지 검증한다.

`tools/validate_live_metadata_authoring.py`는 unconstrained full-draft 변동성을 재현하는 obsolete diagnostic이며 production authoring 통과 증적으로 사용하지 않는다. Dataset provider 호출은 exact active package를 주입한 bounded section-patch 검증에서 1회만 허용한다. Main Filter는 source manifest가 완전한 alias-only binding을 증명하면 provider 0회, 그 외 filter-owned 입력은 최대 1회이며, Domain Policy는 전용 관리자 입력 검증에서 0회여야 한다.

## 실제 Gemini intent 검증

```powershell
python tools/validate_live_intent_models.py --models gemini-3.5-flash-lite --runs 3
```

`intent_llm` case만 provider를 호출한다. deterministic·unsupported case는 별도 full-pipeline 검증에서 provider 호출이 0회임을 확인한다.

## 실제 분리 component 분기 검증

```powershell
python tools/validate_live_component_models.py --model gemini-3.5-flash-lite
```

동일한 export Flow에서 zero-LLM, Intent LLM 1회, Narrative LLM 1회, unsupported 0회 case를 각각 실행한다. 각 custom component는 Langflow edge 순서대로 직접 호출된다.

## 실제 Langflow 1.9.2 HTTP 검증

격리 서버가 staging `.env`를 process environment로 상속한 상태에서 실행한다. provider key는 Flow tweak나 report에 넣지 않는다.

```powershell
python tools/validate_langflow_http_e2e.py `
  --server-url http://127.0.0.1:7873 `
  --environment validation `
  --model gemini-3.5-flash-lite
```

validator는 export를 업로드한 뒤 실제 `/api/v1/run/{uploaded_flow_id}`를 호출한다. deterministic 1건, Intent LLM 1건, 동일 session의 2-turn follow-up을 실행하며 `v6_active` domain pointer, state version `1→2`, pandas LLM 0회, Message/API/GaiA canonical hash 동치를 확인한다. raw HTTP 응답·질문·prompt·provider key는 저장하지 않는다.

Domain Authoring의 실제 등록 흐름은 별도 isolated environment에서 검증한다.

```powershell
python tools/validate_langflow_http_authoring_e2e.py `
  --server-url http://127.0.0.1:7873 `
  --environment e2e_validation `
  --domain-id order_sales
```

validator는 요청한 접두사에 nonce를 붙인 새 environment를 생성한다. 같은 이름의
기존 active metadata를 재사용하지 않으므로 결과 report의 `environment`가 후속 분석
검증에 사용할 실제 값이다. Full-domain Flow tweak에는 관리자 Blueprint JSON과 별도
SHA-256 pin을 함께 전달하되, API key나 secret은 tweak/report에 넣지 않는다.

3개 authoring Flow를 모두 import하고 다음 3개 자연어 source와 1개 관리자 policy 입력을 순서대로 처리한다.

1. Domain Flow: 주문·매출 전체 도메인 최초 등록
2. Dataset Flow: dataset section 자연어 patch
3. Main Filter Flow: main-filter section 자연어 patch
4. Domain Flow의 `authoring_kind=domain_policy`: explicit intent/answer/specialized/output 관리자 입력 patch

1단계는 `자연어 TXT + trusted Blueprint/external pin → Gemini annotation 정확히 1회`,
2단계는 `자연어 TXT + exact active package → bounded dataset patch Gemini 정확히 1회`,
3단계의 alias-only 입력은 `source-sealed alias binding → deterministic patch, LLM 0회`,
4단계는 `explicit admin input → LLM 0회`다. 이 검증의 합계는 draft 1회,
annotation 1회, repair 0회다. 이후에는 모두 deterministic compile →
prepared candidate → 외부 승인 event → execute commit으로 합류하며 repair LLM은
항상 0회여야 한다. validator는 pending wrapper와 immutable payload seal, candidate/hash,
base/target revision, base bundle/package hash, expiry를 확인한다. 승인 event는
`approval.event.v1` exact schema를 사용하고 event ID, subject ID, decided-at,
idempotency-key 각각을 바꾼 네 개의 schema-valid tamper를 실제 execute Flow에 보내
모두 `approval_hash_mismatch`로 거부되는지와 active/pending state가 변하지 않는지를
확인한다. 정확히 같은 승인 event만 원자 claim 및 commit할 수 있다.

4개 commit의 revision은 `1 → 2 → 3 → 4`로 이어지고 각 patch는 담당 section
밖의 compiled metadata를 바꾸면 안 된다. 주문·매출 package는 datasets 4,
fields 10, metrics 5, relations 3, recipes 6과 환불/목표 dataset의 물리 컬럼,
composite join key, entity group, prompt/output policy를 매 단계 다시 검사한다.
마지막으로 Data Analysis의 실제 standalone `DomainBundleLoader`가 revision 4의 같은
package/catalog hash를 읽는지 확인한다. isolated metadata는 TTL pending과 별도
environment key를 사용하며 자동 삭제하지 않는다. v5 collection은 전후 snapshot이
같아야 한다.

authoring commit이 통과한 뒤 같은 실제 Data Analysis Flow에서 주문 도메인을
검증한다. `<effective-environment>`에는 앞 명령 report의 `environment`를 사용한다.
해당 active pointer가 없으면 즉시 실패한다.

```powershell
python tools/validate_langflow_http_order_sales_e2e.py `
  --server-url http://127.0.0.1:7873 `
  --environment <effective-environment> `
  --domain-id order_sales
```

OS01, OS02, OS08을 trusted inline fixture로 실행해 결과행, 조회 dataset,
`filter/aggregate/join/rank/derive/project` typed IR, zero-LLM usage,
Message/API/GaiA canonical response hash 동치를 확인한다.
Langflow JSON/Data tweak의 `NestedDict` source payload도 standalone component 입력으로
정규화하며 compact GaiA의 `metadata.response_sha256`를 같은 canonical hash로 비교한다.
OS08의 source oracle은 매출 1,000, 환불 300, 순매출 700이다.

## 제조 metadata 자연어 이관·분석 통합 검증

기존 제조 compiled package를 새 격리 environment의 revision 1 신뢰 기준으로
transactional seed한 뒤, v6 authoring Flow와 실제 자연어 TXT를 사용해 세 section을
다시 등록하고 같은 active metadata로 Data Analysis Flow까지 실행한다.

```powershell
python tools/validate_langflow_http_migration_patches_e2e.py `
  --server-url http://127.0.0.1:7873 `
  --environment-prefix migration_validation
```

이 validator의 모델은 사용자 지정으로 바꾸지 않고 코드에 pin된
`gemini-3.5-flash-lite`만 사용하며, 최종 report의 `model` 값도 같은 문자열이어야 한다.

provenance source는 `metadata/authoring/domain/domain_knowledge.txt`,
`metadata/authoring/table_catalog/data_catalog.txt`,
`metadata/authoring/main_filters/main_variable.txt`이다. 세 원본 TXT의 byte/hash는 바꾸지 않는다.
HTTP migration은 다음 normalized companion을 사용하기 전에 각 `.provenance.json`으로
원본·companion raw hash와 source-manifest pin을 모두 검증한다.

- domain policy: `metadata/authoring/domain/domain_policy_v6_normalized.txt`
- dataset: `metadata/authoring/table_catalog/data_catalog_v6_normalized.txt`
- main filter: `metadata/authoring/main_filters/main_variable_v6_normalized.txt`

운영자가 Langflow에 입력할 v6 전용 자연어 기준 파일은
`metadata/authoring/v6_inputs/domain_v6.txt`, `dataset_v6.txt`,
`main_filter_v6.txt`, `domain_policy_v6.txt` 네 개다. 앞의 세 파일은 기존
provenance 원문의 의미와 항목 순서를 유지한 LF 사본이고, 기존 원문은 hash
검증을 위해 수정하지 않는다. Domain Policy Flow는 네 번째 파일의 변경 사유를
자연어로 받되 특화 프롬프트·출력 정책·registered function descriptor는 분리된
관리자 입력으로 등록하며 Prompt/Language Model/Composer/Invoker 노드와 LLM 호출이
모두 0개여야 한다.

dataset companion은 dataset/canonical field binding을 명시해 `EQUIP_ID` 같은 physical field가
새 canonical field로 오인되지 않게 한다. main-filter companion은 53개 explicit alias binding과
17개 field target을 가지며 alias-only Main Filter로 LLM 0회 처리된다. 이를 위해 generic legacy
parser를 넓히지 않고 Recipe ID field-prose false-positive만 좁게 차단한다. domain policy는
reviewed explicit admin input과 LLM 0회, dataset patch는 Gemini 1회, main-filter patch는 LLM 0회, repair 0회로
revision `2 → 3 → 4`를 commit해야 한다. 각 단계에서 주문·매출과 같은 pending/approval/tamper/section
ownership 검증을 적용한다. revision 4 loader 검증 후 동일 environment에 대해 실제
Langflow Data Analysis HTTP 경로의 deterministic 질문, Intent LLM 질문, 2-turn
follow-up을 실행한다. 즉 등록 성공만으로 통과하지 않고 등록된 v6 metadata가 실제
typed Execution IR과 결정론적 executor에서 사용되는 것까지 한 report로 확인한다.

제조 `legacy_v1_compat` 실행 경계는 active package를 먼저 catalog/package/bundle/active-pointer
hash chain으로 검증한 뒤, `planner_profile`, embedded v1 catalog hash, `manufacturing` domain ID,
compiler allowlist를 모두 exact match한다. `metadata.runtime.catalog.v2` 계약에 존재하지 않는
authoring provenance 필드를 실행 조건으로 요구하지 않는다. 향후 provenance 자체로 원본
authenticity까지 보장해야 한다면 같은 seal 안의 자기 선언을 추가하는 방식이 아니라,
외부 검증 가능한 compatibility provenance와 execution-projection fingerprint를 별도 계약으로
도입한다.

authoring collection은 역할별로 분리해야 한다. v5 collection 이름 재사용, bundle과
active collection 역할 교환, 동일 collection 중복 지정은 LLM/Mongo 호출 전에
fail-closed되어야 한다. state/result collection도 같은 규칙을 적용하며 offline
검증에서 request/response node 양쪽을 확인한다.

## 도메인 확장 안전성 검증

```powershell
python tools/validate_domain_extension_safety.py
```

active catalog의 `prompt_extensions.intent/answer`는 해당 component의 기본 정책으로 자동 병합하고, node 입력 extension은 UTF-8 byte budget 안의 overlay로만 적용한다. `specialized_functions`는 `registered_standalone` ID/hash/schema 선언만 허용하며 Python·pandas·SQL·URL·callable payload를 포함하거나 typed executor에 새 실행 경로를 만들 수 없다.

## 통과 조건

- 제조 canonical corpus 전부 통과
- 주문·매출 corpus 전부 통과
- deterministic/unsupported: Intent LLM 0회
- intent route: Intent LLM 1회 이하, 정답 candidate 선택
- narrative off 또는 unsupported: Answer LLM 0회
- narrative on 성공 case: Answer LLM 정확히 1회
- pandas code/repair LLM: 항상 0회
- raw source rows: retriever → merger → typed executor 구간 밖으로 전달 금지
- Message, API, GaiA가 같은 canonical response hash를 참조
- active catalog prompt extension과 bounded node overlay가 resolver/narrative prompt에 모두 포함
- Dataset/Main Filter authoring도 v2 active Domain Package section patch 및 전체 hash 재컴파일 사용
- `specialized_functions`는 declarative registration만 허용하며 evaluator 실행 경로가 없음
- domain/subject/session이 다른 state/result reference 교차 접근 금지
- 실제 Gemini report에 key·prompt·응답 원문이 없어야 함
