# metadata_driven_v6 구현 가이드

## 1. 구현 순서

v5 Python 파일을 먼저 복사하지 않는다. contract, case manifest, compiler/operator를 Python 단위에서 검증한 뒤 Langflow component와 Flow JSON을 만든다. 이 문서가 놓인 `metadata_driven_v6` 폴더 자체가 독립 project/repository root다. Phase 1은 이 root에 파일을 추가하며 `metadata_driven_v6/metadata_driven_v6/` 같은 중첩 폴더를 만들지 않는다.

## 2. 목표 디렉터리

아래는 구현 단계에서 생성할 구조다.

```text
metadata_driven_v6/
  AGENTS.md
  README.md
  pyproject.toml
  uv.lock
  harness/
    harness.md
    contracts/
  contracts/
    schemas/
      metadata-envelope.schema.json
      pending-metadata-write.schema.json
      approval-event.schema.json
      config-registry.schema.json
      query-registry.schema.json
      request-capsule.schema.json
      metadata-bundle.schema.json
      resolved-candidate-bundle.schema.json
      analysis-route.schema.json
      semantic-intent-selection.schema.json
      semantic-intent.schema.json
      analysis-plan.schema.json
      retrieval-job-bundle.schema.json
      source-result.schema.json
      source-bundle.schema.json
      analysis-result.schema.json
      executed-result.schema.json
      turn-state.schema.json
      answer-facts.schema.json
      display-options.schema.json
      answer-sections.schema.json
      download-item.schema.json
      gaia-metadata.schema.json
      response.schema.json
      trace.schema.json
      error.schema.json
      validation-case.schema.json
      model-profile.schema.json
      evidence-manifest.schema.json
      operator-registry.schema.json
      error-registry.schema.json
      flow-inventory.schema.json
      unsupported-telemetry.schema.json
      prompt-envelope.schema.json
      authoring-prompt-overlay-approval.schema.json
      registered-function-card.schema.json
      registered-function-registry.schema.json
    future_exploration/
      exploration-request.schema.json
      exploration-job.schema.json
      exploration-response.schema.json
      DISABLED.md
    operator_registry.json
    registered_function_registry.json
    error_registry.json
    flow_inventory.json
  prompts/
    runtime/
      common/
      specialized/
    authoring/
      common/
      overlays/
  approval_contract/
    openapi.yaml
  metadata/
    authoring/
      domain/
      table_catalog/
      main_filters/
    fixtures/
      compiled/
    bootstrap/
      config_registry.example.json
      query_registry.example.json
  langflow_components/
    data_analysis/
    metadata_authoring/
    session_state/
    gaia_io/
  flow_exports/
  import_ready_flows/
  reference_runtime/
    request_literals.py
    metadata_compiler.py
    plan_compiler.py
    typed_executor.py
    source_contracts.py
    state_contracts.py
  validation/
    cases.jsonl
    expected/
    profiles/
    evidence/
  tests/
    support/
      fake_approval_service.py
  tools/
    assets/
      langflow_1_9_2_language_model.py
      runtime_asset_manifest.json
    build_v6_flows.py
    build_import_ready_bundle.py
    compile_metadata.py
    migrate_v5_metadata.py
    validate_contracts.py
    validate_cases.py
    validate_routes.py
    validate_model_conformance.py
    validate_live_sources.py
    validate_flow_component_sources.py
    validate_runtime_assets.py
    validate_langflow_runtime.py
    provision_source_registry.py
    run_pytest_evidence.py
    write_evidence_manifest.py
```

## 3. Phase 0 — 설계 freeze

현재 단계다.

완료 조건:

- AGENTS와 harness contract 작성
- v5 failure taxonomy 기록
- LLM 경계/호출 수 확정
- metadata/intent/plan/payload/state/validation contract 확정
- baseline validation questions migration
- 설계 문서를 Desktop `metadata_driven_v6` project root로 전달하고 v5 staging을 제거
- Phase 1 전에 v6 전용 git repository를 초기화하거나 지정 remote checkout에 연결; 이후 evidence의 git SHA/dirty state는 v5가 아니라 v6 root만 가리킴

## 4. Phase 1 — Canonical case manifest와 schema

### 작업

1. `validation/validation_questions.txt`의 question text/order/turn ID를 기준으로 case skeleton을 만들고, Phase 1의 reviewed target compiled-metadata/candidate fixture와 route policy로 각 case의 `expected_route`, route reason과 exact LLM call count를 review한다. Phase 2 compiler는 이 target fixture를 exact 재현해야 한다.
2. `validation/ACCEPTANCE_MATRIX.md` §5의 모든 `OP-*` question shape를 자연스러운 exact Korean question text와 deterministic subfixture로 구체화해 review하고 case skeleton에 추가한다. 나머지 v6 invariant도 contract oracle의 우선 기준으로 적용한다.
3. v5 expected 문서는 dummy expected row/value를 옮기는 evidence로만 사용한다. v6 fixed reference instant, canonical field, typed operator, source/date contract와 충돌하면 v6 contract가 우선하며 충돌을 migration report에 남긴다. unresolved conflict가 있는 case는 생성하지 않고 review를 요구한다.
4. 검토가 끝난 `validation/cases.jsonl`을 처음 생성하고 이후 단일 source of truth로 승격한다.
5. `PAYLOAD_STATE.md`의 모든 envelope, purpose별 prompt segment cardinality와 authoring-overlay approval, route/unsupported telemetry, metadata/pending approval, registered-function card/registry, validation case/profile/evidence, registry, flow inventory를 포함한 위 JSON Schema 전부를 작성한다. future exploration schema는 별도 namespace로 정의하되 `DISABLED.md`와 manifest가 runtime 미등록을 증명해야 한다.
6. schema hash와 canonical JSON serializer를 구현한다.
7. 사람이 읽는 question/acceptance 문서를 generator로 만든다.
8. `error_registry.json`, `operator_registry.json`, `registered_function_registry.json`을 schema 및 fault case에 연결한다.
9. exact dependency를 `pyproject.toml`에 선언하고 Python 3.12로 `uv lock`을 생성·검토해 `uv.lock`을 고정한다. 이후 CI/validation은 `uv sync --frozen`만 사용한다.

### Gate

- 30 single, 6 date, MT-1~MT-5 모든 turn과 §5 모든 `OP-*` case가 manifest에 존재
- 모든 case에 `expected_route=deterministic|intent_llm|unsupported`, exact reason과 Intent/retry/Answer/code/repair call-count oracle이 존재
- case ID 중복 없음
- expected contract 필수 필드 누락 없음
- generated docs와 manifest parity
- 모든 node boundary envelope가 machine schema와 validator를 가짐
- error ID가 registry/schema/fault case에서 exact parity
- validation case/model profile/evidence/registry/Flow inventory schema validation
- fixed object는 recursive closed schema를 사용하고, `semantic-intent-selection`의 root/nested object에 undeclared property가 들어가면 validation 실패
- operation/filter tree, display options, answer sections, download item, GaiA metadata까지 recursive closed schema 및 negative extra-property test
- `uv.lock` 존재, Python 3.12 resolution, exact `1.9.2/0.9.2/0.4.2`, lock hash evidence

## 5. Phase 2 — Metadata compiler

### 작업

- immutable source block reader
- free-form Domain·Dataset·Main Filter source bundle context builder
- Domain `display_name`/`description` annotation-only decoder
- compact `metadata.bootstrap.dataset-ir.v1` decoder와 Source Registry v3 dataset descriptor/Source binding expander
- `target_type` 필수 `metadata.bootstrap.main-filter-ir.v1` decoder와 typed alias-card expander
- `metadata.authoring.source-registry.v3` root/semantic-vocabulary/semantic-templates/provenance-hash validator
- compiler-owned `metadata.authoring.semantic-templates.v1` Domain expander와 sealed `planner_policy` validator
- 확장된 full draft의 deterministic schema·semantic·dependency·security compiler
- optional `source_grounding_mode=explicit_inventory` compiler와 trusted Blueprint/external SHA pin validator; Blueprint lane도 Domain annotation schema를 넓히지 않음
- Dataset/Main Filter active-package compact/typed section patch decoder
- Domain Policy explicit-admin-input validator(LLM 0회)
- Domain Policy의 `intent_prompt_extension`, `answer_prompt_extension`, `specialized_functions_json`, `output_profile_json` section ownership과 closed input validator
- Domain Policy `output_profile_json`의 `planner_profile`/`legacy_catalog_sha256` 덮어쓰기 차단
- function descriptor와 build-time standalone registry의 exact function/version/implementation/entry/I/O-schema/resource-policy attestor
- Domain/Dataset/Filter JSON Schema validator
- cross-record dependency resolver
- SQL/column/parameter/mapping semantic lint
- immutable candidate/diff hash와 pending-write store
- prepare/approve/execute writer: 외부 승인, expiry, atomic claim, second-run hash 재검증
- versioned active record writer와 audit event
- v5 read-only migration candidate tool
- runtime bundle selector
- restricted query registry와 config-ref ACL resolver
- production approval service의 `approval_contract/openapi.yaml`과 authenticated approval-event client
- test-only `fake_approval_service.py`: approve/reject/expire/hash-mismatch/idempotency 재현
- admin-only `provision_source_registry.py`: non-secret config/query revision을 dry-run diff 후 등록
- v5 catalog에서 config/query candidate를 추출하되 bootstrap example에는 dummy endpoint/query ID만 포함

### 핵심 lint

- query의 날짜 column과 field binding 불일치
- required parameter mapping 누락
- canonical field duplicate
- metric rollup/additivity 불일치
- recipe dependency 누락
- grain/entity mapping 불완전
- temporal format/timezone 누락

### Gate

- natural TXT → compiled record → runtime loader round-trip
- invalid metadata active 저장 차단
- prepare와 execute 사이 candidate/diff가 바뀌면 저장 차단
- 미승인·만료·이미 claim된 approval 저장 차단
- fake approval service로 prepare→approve/reject/expire→atomic execute contract test
- production approval contract가 authenticated subject, candidate hash, decision, expiry, immutable event ID, idempotency를 machine schema로 검증
- non-secret bootstrap config/query fixture round-trip과 admin ACL; runtime/LLM이 registry를 생성·수정하지 못함
- dependency closure byte budget 통과
- v5 collection 변경 0
- Domain Policy와 optional explicit-inventory Main Filter에서 Prompt Template/Composer/envelope/provider 생성·호출 0
- 비정형 문장 순서·말투·표기를 가진 작업자 TXT가 Blueprint/pin이나 inventory 문법 없이 Domain annotation/compact Dataset IR/typed Main Filter IR lane을 통과
- `semantic_templates`가 LLM payload에 없고, registry template/blueprint/executable/projection hash drift와 sealed planner-policy 변경이 candidate 전에 차단됨
- 미등록 function, hash/schema/resource-policy mismatch function card의 prepare/activation 차단

## 6. Phase 3 — Route, intent와 plan compiler

### 작업

- deterministic Request Capsule Builder와 typed literal/evidence candidates
- request evidence, resolved field/operator/value semantics, metadata/operator pins을 가진 immutable `resolved.candidate.bundle.v1`
- unique/complete selection을 증명하는 deterministic Route Eligibility Gate와 closed `analysis.route.v1`
- proof에 pin된 selection만 공통 `analysis.intent.v1`로 만드는 Deterministic Intent Builder
- explicit/relative date, timestamp, number, product token, ordered process-range fixture
- full resolved semantics를 제외한 compact prompt와 candidate ID cards
- registry attestation을 통과한 registered-function candidate card와 exact candidate semantics hash
- `intent_llm` route에서만 실행되는 recursive closed `analysis.intent.selection.v1` validator와 trusted candidate-bundle/route-proof hash를 부착하는 `analysis.intent.v1` decoder
- deterministic/LLM intent가 같은 closed schema와 canonical hash 규칙으로 수렴하는 Common Intent Validator
- generic alias/token/date boundary resolver
- compiler:
  - dataset/time variant
  - required params
  - executed-result contract를 참조하는 declarative entity-binding spec
  - Plan Validator 이후 owner-bound value를 resolve/chunk하는 Parameter Binder와 immutable job-bundle hash
  - source filters
  - canonical fields
  - operation DAG
  - exact function/registry/I/O-schema/resource pin을 가진 `registered_call`
  - result contract
  - lineage
- pre-retrieval validator
- bounded unsupported telemetry writer와 reviewed typed capability promotion report

### Gate

- intent fixture로 36 single/date와 Acceptance Matrix §5 모든 `OP-*` plan exact match
- actual router로 모든 canonical case의 expected route/reason/call-count exact match
- unique/complete는 Intent LLM 0, semantic choice는 1, unsupported는 모든 LLM/retrieval/executor 0
- deterministic route 선택 후 downstream failure가 다른 route/LLM/pandas/exploration을 호출하지 않음
- 동일 semantic selection의 deterministic/LLM intent hash, plan fingerprint, result hash equivalence
- Plan Compiler가 intent에 pin된 exact resolved candidate bundle만 소비하고, bundle hash가 plan fingerprint에 포함됨
- raw LLM JSON의 root/nested extra property, 모든 `*_refs[]`의 candidate/target 외 field, `filter_refs[].field|operator|value|values`, raw N/join key/formula, reserved bundle hash 주입을 모두 `intent_contract_error`로 거부
- 존재하지 않는 candidate ID, semantics hash mismatch, 허용되지 않은 target slot을 모두 retrieval 전에 거부
- W/BM longest boundary match
- BOH D/D-1 exact
- `L-267`, `D/S1~D/A4`, 상대/절대 날짜가 원문 evidence candidate로만 plan에 들어감
- MT-2 current HOLD 전체 `LOT_ID` set이 retrieval 전 stable chunk job으로 binding되고, oldest 선택은 complete `HOLD_EVENT_AT` history를 조회한 뒤 수행
- plan fingerprint repeatability
- 질문 문자열 특화 Python branch 0
- model/provider profile 변경으로 deterministic route/proof가 바뀌는 case 0
- LLM이 free-form function ID/argument/registry hash를 생성하지 않고 제공된 candidate ID만 선택
- 검증된 function candidate가 Plan Compiler의 `registered_call`까지 exact pin을 유지하며 누락·변조 시 retrieval 전에 실패

## 7. Phase 4 — Typed executor

### 구현 순서

1. recursive filter tree와 null/string/numeric operators
2. project/canonical output ordering
3. aggregate와 scalar extrema
4. global/per-group stable sort, top/bottom N, single/multi-key argmax/argmin, per-metric/top+bottom segments
5. registered-column comparison과 duplicate-group detection
6. ordered range/product token/row-match group
7. inner/left/right/outer/semi/anti join과 cardinality/null/multi-match policy
8. presence anti-join
9. allowlisted formula AST와 safe derive
10. detail/entity list, dedupe, history ordering
11. hash-pinned Registered Function Gateway와 `registered_call` typed argument/output adapter
12. previous result/source transform와 result enrich

### Executor 경계

- input은 canonical source frames와 validated plan만 받는다.
- free-form code/string eval/import를 받지 않는다.
- registered function은 build-time allowlist implementation만 호출하고 arbitrary network/file/subprocess/secret 접근을 허용하지 않는다.
- 각 operator는 input/output grain을 반환한다.
- result validator가 exact output contract를 검사한다.

### Gate

- operator registry unit test 100%
- in-memory canonical frame fixture로 operation DAG/result contract exact match
- global/per-group top·bottom, exact-N/include-all-ties, argmax/argmin, top+bottom segment exact oracle
- 모든 join type의 0/1/N match, declared cardinality, null/duplicate/empty-side/suffix policy exact oracle
- registered arbitrary field comparison, duplicate group, formula type/rounding/zero-division exact oracle
- compound filter `all/any`, string/null/numeric operator와 migration alias exact oracle
- executor 소유 fault injection 전부 expected error
- no suffix/extra/duplicate output
- registered function의 exact hash/schema/field-role/argument/resource 검증, timeout, output contract/lineage positive·negative oracle와 미등록 fallback 0

Phase 4에서는 아직 adapter가 없으므로 30+6 전체 E2E나 multi-turn 완료를 주장하지 않는다.

## 8. Phase 5 — Source adapters와 row store

### 작업

- Oracle/H-API/Datalake/Goodocs/Dummy adapter
- trusted Config/Query Resolver의 canonical filter/projection→reviewed physical query-slot binding과 branch-local secret injection
- physical schema capture
- Source Contract Merger의 exact-once field binding canonicalization
- inline/ref threshold
- TTL source/result store
- download ref

### Gate

- dummy/live canonical schema parity
- Oracle/H-API/Datalake/Goodocs/Dummy adapter-type fixture: read-only enforcement, timeout, row limit, credential redaction, schema/error mapping
- 9 dataset read-only smoke
- source failure propagation
- required failure 전체 error와 optional-enrichment typed-null partial policy exact oracle
- full rows가 LLM edge에 없음
- 30 single + 6 date와 모든 `OP-*` deterministic E2E exact oracle 100%

실제 배포 catalog에 H-API 또는 Datalake dataset이 없더라도 해당 adapter의 local contract/security fixture는 생략하지 않는다. Live gate는 배포된 source type만 read-only로 실행하고 미배포 type은 `not_deployed` evidence를 남긴다.

## 9. Phase 6 — Follow-up, state, answer

### 작업

- `executed.result.v1`
- `turn.state.v1`
- content-addressed answer facts/operator trace refs를 가진 durable explain evidence
- owner/session-bound refs, TTL, compare-and-swap state version
- 기본 `allow_anonymous_multiturn=false`; 인증 주체가 없는 상태는 turn 간 전역 메모리를 공유하지 않음
- 로컬 단일 사용자 검증에서만 두 state node의 opt-in을 함께 켜며, `default`가 아닌 20자 이상 session ID와 `{environment}:{domain_id}:{session_id}` namespace를 강제
- source snapshot completeness/coverage와 reuse-or-requery decision
- MT modes: result/source transform, enrich, requery, reset, source expand, explain/trace-only
- deterministic answer facts/table/scope
- optional Answer LLM
- claim validator
- `display.options.v1`과 v5 배포 기본 profile
- `answer.sections.v1`, `download.item.v1`, `gaia.metadata.v1`
- `show_pandas_code` → `show_execution_plan` migration
- Message/API/GaiA output fan-out와 store/state/release 선행 순서

### Gate

- MT-1~MT-5 모든 turn scenario-specific oracle
- MT-2 full current-HOLD LOT binding → complete history → oldest current hold start → selected LOT full history
- MT-4 stored coverage에 따른 exact reuse/requery mode
- independent question state reset
- cross-session ref와 concurrent stale-state write 차단
- anonymous opt-in off에서 같은 session 문자열을 사용해도 이전 turn/ref가 공유되지 않고, opt-in on의 짧은 session은 fail-closed
- Answer LLM off에서도 완전한 응답
- invented claim 0
- state 6KB budget
- v5 표시 옵션 각각 on/off에서 Message section visibility exact match
- diagnostics master OR intent/retrieval/execution-plan child precedence exact match
- Message 표시 옵션 변경 전후 canonical `response.v1`, result/state ref, GaiA answer/metadata가 동일
- API terminal의 v5 wire key와 `data.rows`/`data_refs[]` shape exact compatibility
- `show_pandas_code`가 code 생성 없이 typed IR 표시로만 변환
- result/source store → state CAS → runtime release → terminal fan-out 순서 fault test
- follow-up suggestion 최대 3개가 Message section과 GaiA metadata에 같은 ID/text로 매핑
- `explain_previous`가 persisted criteria/lineage/facts/operator hashes만 사용하고 retrieval/executor 호출 0

## 10. Phase 7 — Langflow standalone component

### Physical standalone source inventory 기준

기존 4-Flow 배포본의 18개 unique standalone Python source와 Data Analysis 19 node/28 edge, authoring 각 6 node/5 edge 수치는 migration baseline일 뿐 최종 계약이 아니다. 5-Flow 재생성 뒤 manifest가 최종 physical source/node/edge 수를 소유한다.

- `langflow_components/data_analysis/`: 기능별 standalone source
- `langflow_components/metadata_authoring/`: 공통 authoring engine, Domain Policy validator와 presentation source
- `langflow_components/shared/`: Message/API fan-out, prompt envelope/composer, registered-function registry/gateway에 필요한 standalone source

아래 번호는 요구사항 추적을 위한 **logical stage**이며 파일 개수를 뜻하지 않는다. 서로 강하게 결합된 validation/canonicalization 단계는 한 physical source 안에 포함하되, 데이터 조회 adapter와 route/intent/plan/executor/registered-function gateway/state/output 경계는 별도 source로 유지한다.

### Data Analysis logical stage inventory

| 번호 | Component |
| --- | --- |
| 00 | Request Capsule Builder |
| 01 | Session/Executed Result Loader |
| 02 | Compiled Metadata Bundle Loader |
| 03 | Deterministic Route Eligibility Gate |
| 04 | Intent Variables Builder (`intent_llm` branch only) |
| 05 | Deterministic Intent Builder / LLM Intent Decoder |
| 06 | Common Intent Contract Validator |
| 07 | Plan Compiler |
| 08 | Plan Validator |
| 09 | Parameter Binder/Thin Job Router |
| 10 | Trusted Config/Query Resolver |
| 11~15 | Source Adapters |
| 16 | Source Contract Merger |
| 17 | Typed Analysis Executor |
| 17A | Registered Function Registry Attestor / Gateway |
| 18 | Result Contract Validator |
| 19 | Result/Source Ref Store |
| 20 | Answer Facts Builder |
| 21 | Answer Claim Validator/Response Assembler + Unsupported Telemetry |
| 22 | State CAS/Runtime Release Gate |
| 23 | Message Presentation Adapter |
| 24 | API Response Terminal (`Data`, `is_output=True`) |
| 25 | GaiA Output Adapter (`Message` + metadata `Data`) |

Native Prompt/Language Model/Chat Input/Output node는 별도다. Runtime Intent와 Answer에는 각각 물리적으로 분리된 공통·특화 Prompt Template node가 필수다. 두 prompt는 서로 다른 ID/source/revision/hash/edge를 가지며 runtime context를 중복 입력받지 않는다.

05의 두 생성기는 같은 standalone source의 공통 canonicalizer/schema validator를 사용하되 Flow edge는 route별로 분리한다. deterministic branch에서는 Language Model node가 실행되지 않아야 한다. 21의 telemetry는 unsupported/error의 bounded shape만 기록하며 response를 바꾸거나 runtime capability를 생성하지 않는다.

### Metadata authoring logical stage inventory

| 번호 | Component |
| --- | --- |
| A00 | Immutable Source Block Splitter |
| A01 | Domain Annotation / Compact Dataset IR / Typed Main Filter IR Decoder |
| A02 | Source Registry v3 Expander + Schema/Semantic Lint/Dependency Validator |
| A03 | Existing Record Diff + Pending Prepare Writer |
| A04 | Approved Candidate Atomic Executor |
| A05 | Compile/Runtime Loader Round-trip Validator |

`prepare` run은 A00~A03까지만 실행하고 active collection에 쓰지 않는다. 최초 Full-domain bootstrap은 작업자가 자유롭게 작성한 Domain·Dataset·Main Filter TXT를 세 입력으로 받아 작업별 공통 Prompt Template과 LLM을 각각 최대 1회, 총 3회 사용한다. 출력은 Domain 표시명/설명 annotation, compact Dataset IR, `target_type` 필수 Main Filter IR로 고정된다. A02가 Source Registry v3의 hash-pinned `semantic_templates`, dataset descriptor/Source binding과 alias target을 결정론적으로 확장·병합해 full draft를 compile한다. `semantic_templates.planner_policy`는 봉인되며 어떤 LLM 출력이나 Domain Policy output profile도 변경할 수 없다. 후속 Dataset과 Main Filter 수정도 각각 같은 IR/expander 경계에서 LLM 최대 1회다. 사용자에게 정형 inventory, JSON, ID, 타입, 컬럼 또는 IR 문법을 요구하지 않는다. optional authoring overlay는 같은 normalized failure shape의 승인 case 3개 이상, 서로 다른 자연어 source 2개 이상, language-interpretation root cause와 관리자 approval pin을 모두 만족할 때만 별도 node/source/hash/edge로 추가한다. Domain Policy와 optional explicit-inventory Main Filter는 prompt node, Composer, envelope와 LLM 호출이 0회다. Blueprint/pin lane은 Domain annotation 계약에 external executable pin 검증을 추가한다. 외부 승인 서비스가 exact candidate/diff hash를 승인한 뒤 별도 `execute` webhook/run이 A04~A05를 실행한다. A04 하나가 승인/hash/base/dependency를 검사하고 pending claim, immutable revision insert, active pointer 교체, 이전 revision deprecate, audit append를 **한 MongoDB transaction 또는 문서화된 단일-document CAS 대안 안에서** 수행한다. Claim과 commit을 서로 다른 Langflow component로 분리하지 않는다.

### Standalone build

- `reference_runtime/`은 build/test source of truth일 뿐 Langflow runtime dependency가 아니다.
- builder가 schema, registry뿐 아니라 request literal resolver, metadata/plan compiler, typed executor, source/state helper의 필요한 code block을 각 component source에 생성·embed한다.
- registered function 구현과 registry entry도 builder가 hash-pinned allowlist로 standalone source에 embed하며 runtime sibling import, metadata code, dynamic import를 사용하지 않는다.
- 각 embedded block에 source SHA 기록
- runtime sibling import 없음
- generated standalone source, Flow JSON embedded source, reference-runtime/schema/registry hash를 대조
- `tools/assets/langflow_1_9_2_language_model.py`를 기본 Language Model source로 사용
- exact 1.9.2 `lfx/_assets/component_index.json`을 사용하고, ambient 환경이 다르면 `LANGFLOW_COMPONENT_INDEX_PATH`가 없거나 hash가 다를 때 build 전 실패

### MVP Flow inventory

Phase 8 gate 대상은 정확히 아래 5개다. 이는 v5의 모든 보조 Flow parity를 주장하는 목록이 아니다.

| Logical key / `endpoint_name` | 용도 | 필수 smoke |
| --- | --- | --- |
| `metadata_v6_data_analysis` | single/date/multi-turn 분석 | Chat + API + GaiA |
| `metadata_v6_domain_authoring` | Domain/metric/recipe TXT 등록 | prepare + second-run execute |
| `metadata_v6_dataset_catalog_authoring` | Dataset Catalog TXT 등록 | prepare + second-run execute |
| `metadata_v6_main_filter_authoring` | filter/group/alias TXT 등록 | prepare + second-run execute |
| `metadata_v6_domain_policy_authoring` | explicit 관리자 prompt extension/function descriptor/output profile 등록; Prompt/LLM 0회 | prepare + second-run execute + zero-prompt/provider 계측 |

위 문자열은 Langflow top-level UUID `id`가 아니라 project logical key이자 stable `endpoint_name`이다. `contracts/flow_inventory.json`은 fixed UUID namespace와 각 logical key를 저장하고, builder는 `UUIDv5(namespace, logical_key)`로 top-level Flow `id`를 결정론적으로 만든다. Gate는 logical key, endpoint_name, expected UUIDv5, display name을 모두 검사한다.

Future Exploration은 위 inventory에 포함하지 않는다. 초기 builder/export/import-ready bundle에 exploration Flow, endpoint, worker 설정이나 Data Analysis의 자동 호출 edge가 존재하면 실패다.

`tools/build_v6_flows.py`는 다섯 Flow의 source export와 import-ready JSON을 한 번에 만들며 manifest에 exact count, logical key, endpoint_name, UUID, hash를 기록한다. 모든 사용자 가시 Flow/node/input/output 이름·설명은 한글이고, 각 input `info`와 output 설명 및 역할별 Sticky Note의 deterministic ID/layout/content revision도 manifest 검증 대상이다.

## 11. Phase 8 — Flow/bundle와 validation

재현 가능한 Python 3.12/lock 환경에서 구현된 command surface:

Live authoring validator는 model override를 받지 않고 `gemini-3.5-flash-lite`, temperature `0`, provider fallback `0`, repair LLM `0`을 fail-closed 상수로 검증한다. 기본 제조 bootstrap source는 `metadata/authoring/v6_inputs/domain_v6.txt`, `dataset_v6.txt`, `main_filter_v6.txt`를 합친 자유형 자연어 bundle이다.

```powershell
uv sync --frozen --python 3.12
uv run --frozen python -c "from importlib.metadata import version; e={'langflow':'1.9.2','langflow-base':'0.9.2','lfx':'0.4.2'}; assert all(version(k)==v for k,v in e.items()), {k:version(k) for k in e}"
uv run --frozen python tools\validate_runtime_assets.py --strict
uv run --frozen python tools\compile_metadata.py
uv run --frozen python tools\generate_contracts_and_cases.py --check
uv run --frozen python tools\build_executable_blueprint.py --check  # optional explicit-inventory lane
uv run --frozen python tools\build_standalone_components.py --check
uv run --frozen python tools\build_v6_flows.py
uv run --frozen python tools\build_import_ready_bundle.py
uv run --frozen python tools\validate_runtime_cases.py --output validation_outputs\runtime_cases_final.json
uv run --frozen python tools\validate_langflow_equivalent_pipeline.py --execute-cases --execute-components --execute-order-sales --execute-multiturn --output validation_outputs\langflow_equivalent_pipeline_final.json
uv run --frozen python tools\validate_order_sales_component_cases.py --output validation_outputs\order_sales_component_cases_final.json
uv run --frozen python tools\validate_langflow_runtime.py --all-flows --expected-flow-count 5 --strict-versions --output validation_outputs\langflow_runtime_final.json
uv run --frozen python tools\validate_flow_component_sources.py --output validation_outputs\flow_source_sync_final.json
uv run --frozen python tools\validate_langflow_http_authoring_e2e.py --output validation_outputs\langflow_http_authoring_freeform_final.json
uv run --frozen python tools\validate_langflow_http_migration_patches_e2e.py --output validation_outputs\langflow_http_manufacturing_freeform_final.json
uv run --frozen python tools\validate_live_blueprint_authoring.py --model gemini-3.5-flash-lite --output validation_outputs\live_blueprint_authoring_optional.json
uv run --frozen python tools\validate_live_intent_models.py --models gemini-3.5-flash-lite --runs 3 --output validation_outputs\live_intent_models_final.json
uv run --frozen python -m pytest --junitxml validation_outputs\pytest_v6_final.xml -q
```

`validate_runtime_cases.py`는 각 case의 expected route/reason/proof invariant와 exact LLM call counter를 확인한다. `validate_langflow_equivalent_pipeline.py`는 export graph와 분리 component를 같은 edge 순서로 호출하여 single/multi-domain/multi-turn 경계를 검증한다. deterministic/unsupported case에서는 provider 호출을 hard-fail시키고 post-selection fault에서 다른 route, Intent LLM, pandas, exploration 호출 수가 모두 0인지 확인한다. 실제 provider semantic 평가는 `validate_live_intent_models.py`가 `expected_route=intent_llm` subset에만 수행한다.

Future exploration schema는 parse/hash 검증만 한다. worker나 endpoint를 시작하지 않으며 Flow inventory, bundle, trusted state/output compatibility gate에 포함하지 않는다.

기존 command surface와 4개 Flow/export/import-ready bundle은 migration baseline으로 구현되어 있다. 최종 gate는 위 명령의 expected count 5를 만족하는 재생성 산출물만 통과시키며, 5번째 Domain Policy Flow가 없으면 의도적으로 실패한다. 실제 Langflow HTTP 검증은 별도 isolated 1.9.2 server에서 Data Analysis와 네 authoring Flow를 실행한다. 현재 실행 결과와 evidence 파일은 README와 `docs/V6_FINAL_VALIDATION.md`에 기록하되, 과거 4-Flow report는 최종 5-Flow 승인을 대신하지 않는다.

## 12. v5 재사용 정책

재사용 후보:

- source-specific connection behavior
- result/download TTL handling
- GaiA input/output boundary
- exact 1.9.2 builder assets
- security redaction patterns

새로 구현:

- typed request/literal candidate resolver와 compact intent decoder
- metadata candidate resolver
- canonical mapping path
- output schema construction
- follow-up executed contract
- validation manifest와 oracles

재사용 코드는 먼저 standalone/security/contract audit를 통과해야 한다.

명시적으로 폐기하며 구현하지 않는 v5 경로:

- pandas prompt
- pandas code generation LLM
- pandas repair LLM
- free-form code fallback
- 질문 문자열별 normalizer patch

## 13. Review checklist

- 이 코드가 질문 문자열이나 dataset 이름을 직접 검사하는가?
- 이 결정은 metadata/compiler/executor 중 누가 소유해야 하는가?
- canonical/physical 변환이 두 번 일어나는가?
- source 실패가 empty/zero로 바뀌는가?
- result metric에 full lineage가 있는가?
- full rows가 prompt/state/trace에 복제되는가?
- fixture가 모델/metadata compiler를 우회하는가?
- exact Langflow version 검증이 실제로 fail하는가?
