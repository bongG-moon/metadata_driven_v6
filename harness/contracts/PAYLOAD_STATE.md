# Payload and State Contract

## 1. 원칙

v6는 하나의 `payload` dict를 처음부터 끝까지 키를 추가하며 전달하지 않는다. 각 경계는 필요한 데이터만 가진 versioned envelope을 출력한다.

## 2. Envelope 목록

| Contract | 주요 내용 | rows 허용 |
| --- | --- | ---: |
| `request.capsule.v1` | question, subject/session, reference instant, typed candidates, refs | 아니오 |
| `metadata.bundle.v1` | compiled cards, revisions, dependency hash | 아니오 |
| `resolved.candidate.bundle.v1` | request evidence hash, candidate resolved semantics, metadata/operator pins | 아니오 |
| `analysis.route.v1` | deterministic/intent_llm/unsupported, reason, eligibility proof hash | 아니오 |
| `analysis.intent.v1` | semantic selection | 아니오 |
| `analysis.plan.v1` | jobs, operation DAG, lineage | 아니오 |
| `retrieval.job_bundle.v1` | 한 source type의 thin jobs | 아니오 |
| `source.result.v1` | status, schema, row ref 또는 bounded inline rows | 제한 |
| `source.bundle.v1` | executor input refs/frames | 예, 한 번만 |
| `analysis.result.v1` | result ref 또는 bounded rows, schema, lineage | 제한 |
| `executed.result.v1` | follow-up contract | 아니오 |
| `turn.state.v1` | compact inheritance state | 아니오 |
| `answer.facts.v1` | facts, notices, bounded preview | preview만 |
| `display.options.v1` | Message 표시 항목과 preview 제한 | 아니오 |
| `answer.sections.v1` | summary/table descriptor/criteria/evidence/notices/downloads/next questions | 아니오 |
| `download.item.v1` | owner-bound result/source download ref와 expiry | 아니오 |
| `gaia.metadata.v1` | URL/follow-up/trace/usage metadata | 아니오 |
| `response.v1` | stage status, message, answer sections, table preview, refs | preview만 |
| `trace.v1` | stage event와 verbose trace ref | 아니오 |

위 목록의 모든 contract와 중앙 `error.v1`은 machine-readable JSON Schema, canonical serializer, boundary validator를 가진다. 문서 예시만 있고 schema가 없는 envelope은 구현 완료로 보지 않는다.

## 3. Byte budget

| 항목 | 최대 기본값 |
| --- | ---: |
| static intent prompt | 7KB |
| candidate prompt-card projection in intent | 14KB |
| resolved candidate compiler bundle inline | 32KB, 초과 시 immutable ref |
| request + state in intent | 3KB |
| JSON/tool/provider framing reserve | 4KB |
| total intent model input | 28KB |
| answer model input | 12KB |
| persisted turn state | 6KB |
| inline trace | 8KB |
| source job bundle, rows 제외 | 4KB |
| answer preview | 10 rows / 12 columns |
| response inline rows | 20 rows |

Budget 초과 시 관련도 낮은 record를 단순 제거하지 않는다. dependency bundle 단위로 줄이고, 필수 dependency를 보존할 수 없으면 `metadata_budget_exceeded`로 종료한다. `total intent model input`과 `answer model input`은 system/user messages, serialized JSON, tool/schema declaration, provider wrapper까지 포함한 최종 rendered UTF-8 byte 기준이다.

모든 budget은 UTF-8 bytes와 provider tokenizer 추정치를 report에 함께 기록한다.

## 4. Row transport

- raw source row는 Intent/Answer LLM에 전달하지 않는다.
- 각 retriever branch는 전체 request/intent/state가 아니라 job bundle만 받는다.
- `source.result.v1.status`는 `ok|empty|error`만 사용하고 `error`이면 중앙 `error.v1` payload가 필수다.
- source row는 `source.bundle.v1`에서 executor가 한 번 소비한다.
- inline threshold를 넘으면 TTL row store에 저장하고 opaque `source_ref`를 사용한다.
- `source.result.v1`은 source/stored row count, chunk count, truncated flag, row-set completeness, query/filter/schema/content hash, retrieval/expiry time을 가진다.
- executor는 source bundle 소비 후 full source와 full result를 동시에 downstream으로 전달하지 않는다.
- full result는 result store에 저장하고 downstream에는 `result_ref`, schema, row count, bounded preview만 보낸다.
- resolved secret, SQL/query body, provider credential은 envelope이나 trace에 넣지 않고 retriever branch의 trusted node input/메모리 안에서만 사용한다.

## 5. Answer context

Answer LLM 입력은 다음으로 제한한다.

```json
{
  "question": "...",
  "facts": [
    {"fact_id": "row_count", "value": 6},
    {"fact_id": "top_metric", "entity": "D/A1", "value": 1324, "unit": "count"}
  ],
  "scope": {
    "dates": [],
    "filters": [],
    "datasets": []
  },
  "table_preview": [],
  "notices": []
}
```

LLM 출력에는 table을 맡기지 않는다. Response assembler가 canonical rows와 labels로 표를 만든다. 선택적 Answer LLM은 임의 prose가 아니라 다음 구조만 반환한다.

```json
{
  "sentences": [
    {
      "text": "W/B1의 생산량은 1,024입니다.",
      "fact_ids": ["metric:production:row:wb1"],
      "scope_fact_ids": ["scope:date", "scope:process"]
    }
  ]
}
```

Claim Validator는 각 문장의 숫자·날짜·entity·비교 표현을 연결된 fact ID로 재구성할 수 있고 필수 scope fact가 모두 연결된 경우에만 문장을 허용한다. 정성적 주장이나 token을 결정론적으로 증명하지 못하면 문장 하나가 아니라 Answer LLM prose 전체를 폐기하고 deterministic narrative로 fallback한다.

## 6. Turn state

```json
{
  "contract_version": "turn.state.v1",
  "state_version": 7,
  "etag": "state-sha256:...",
  "owner_subject_id": "user-or-service:...",
  "session_id": "...",
  "turn_id": "...",
  "parent_turn_id": "...",
  "parent_state_sha256": "...",
  "last_question": "...",
  "semantic_context": {
    "metric_refs": [],
    "dimension_refs": [],
    "filters": [],
    "time_refs": []
  },
  "executed_result_ref": "executed:...",
  "executed_result_contract_sha256": "...",
  "source_snapshot_refs": [],
  "expires_at": "..."
}
```

State에 저장하지 않는 것:

- full chat history
- full result/source rows
- SQL/query template
- full metadata documents
- pandas code
- answer prompt/LLM raw response
- duplicated preview arrays

최근 대화 표현이 필요하면 bounded user/assistant summary를 별도 필드 하나에 저장하되 실행 계약의 근거로 사용하지 않는다.

`etag`는 `etag` 필드 하나만 제외한 `turn.state.v1` object를 schema-aware canonicalize한 SHA-256(`state-sha256:<hex>`)이다. semantic set 배열은 schema comparator로 정렬하고 turn/order 의미가 있는 배열은 보존한다. Store와 loader는 같은 state schema/serializer hash를 사용하며, persisted timestamp 같은 비계약 storage metadata는 state object 밖에 둔다.

State/ref 접근 규칙:

- `owner_subject_id`는 질문 text나 일반 user input에서 받지 않고 authenticated GaiA/API adapter가 주입한다. 신뢰할 principal이 없으면 persistent follow-up ref를 만들지 않는다.
- standalone 로컬 단일 사용자 검증만 예외적으로 두 state node의 `allow_anonymous_multiturn`을 명시적으로 켤 수 있다. 기본값은 false이며, opt-in 시에도 `default` 또는 20자 미만 session ID는 거부하고 key를 `{environment}:{domain_id}:{session_id}`로 namespace한다. 이는 인증/owner binding의 대체 수단이 아니므로 다중 사용자 운영에서는 금지한다.
- state, result, source ref는 `owner_subject_id + session_id`에 묶으며 다른 subject/session에서는 `state_reference_forbidden`이다.
- load 시 TTL, owner, session, contract hash를 모두 검사한다.
- write는 `(owner_subject_id, session_id, expected_state_version, parent_state_sha256)` compare-and-swap으로 수행한다.
- 동시에 들어온 두 turn 중 하나만 다음 version을 만들 수 있다. 나머지는 `state_conflict`로 재시도 또는 새 분석을 요구한다.
- 이미 claim한 approval/state mutation token은 재사용할 수 없다.

## 7. Trace

Inline trace는 event code 중심이다.

```json
{
  "trace_id": "trace:...",
  "events": [
    {"stage": "route", "status": "ok", "route": "deterministic", "reason_code": "unique_complete_selection", "eligibility_proof_sha256": "..."},
    {"stage": "intent", "status": "ok", "contract_sha256": "...", "generator": "deterministic", "llm_called": false},
    {"stage": "plan", "status": "ok", "plan_id": "..."},
    {"stage": "retrieval", "status": "ok", "jobs": 2, "job_bundle_id": "jobbundle:..."},
    {"stage": "execution", "status": "ok", "operator_count": 3, "execution_id": "execution:..."}
  ],
  "verbose_trace_ref": "traceblob:..."
}
```

Verbose debug data는 TTL ref로 보관한다. 같은 state/intent/source summary를 trace와 API에 복제하지 않는다.

## 8. Presentation과 output 호환 계약

v5에서 사용자가 조절하던 Message 표시 옵션은 `display.options.v1`으로 유지한다. v5 배포 Flow와 같은 기본 profile은 다음과 같다.

```json
{
  "contract_version": "display.options.v1",
  "profile": "v5_shipped_compat",
  "include_diagnostics": false,
  "show_result_table": true,
  "table_preview_limit": 10,
  "show_analysis_evidence": false,
  "show_download_links": false,
  "show_notices": false,
  "show_applied_criteria": false,
  "show_next_questions": false,
  "show_intent_analysis": true,
  "show_data_retrieval": false,
  "show_execution_plan": true
}
```

v5 component input `show_pandas_code`는 Flow import/migration용 alias다. Message Presentation Adapter가 envelope 검증 전에 `show_execution_plan`으로 정규화하며, canonical `display.options.v1`에는 중복 field를 남기지 않는다. 사용자에게 pandas code를 생성하거나 노출하지 않고 검증된 typed Execution IR과 operator trace만 표시한다. 두 input이 함께 있고 다르면 canonical `show_execution_plan`이 우선하며 migration warning을 남긴다.

`table_preview_limit`는 정수 1~20, 기본 10이다. 기존 Flow 값이 상한을 넘으면 import migration에서 20으로 clamp하고 warning을 남기며, Message adapter가 full result ref를 다시 읽어 payload를 키우지 않는다.

v5와 같은 diagnostics master precedence를 유지한다.

```text
effective_intent_analysis = include_diagnostics OR show_intent_analysis
effective_data_retrieval = include_diagnostics OR show_data_retrieval
effective_execution_plan = include_diagnostics OR show_execution_plan
```

따라서 `include_diagnostics=true`이면 세 진단 section을 모두 강제로 표시하고, false이면 각 child toggle을 그대로 따른다. result table/evidence/download/notices/criteria/next questions에는 master가 영향을 주지 않는다.

진단 section도 bounded projection만 렌더링한다. Intent는 route/reason, selected candidate ID/hash와 Intent LLM 호출 여부를 표시한다. deterministic route에서도 같은 section을 유지하되 LLM 분석처럼 표현하지 않고 `deterministic selection`으로 명시한다. Retrieval은 job ID/status/row count/ref, execution plan은 operator ID와 canonical field/grain/result schema만 표시한다. prompt, raw LLM output, full metadata/plan, eligibility proof 본문, query/secret, source rows는 표시하지 않는다.

표시 옵션은 Langflow `Message` body의 section visibility에만 영향을 준다. 다음 데이터는 옵션이 꺼져도 생성·검증·저장되며 API/GaiA terminal에서 사라지지 않는다.

- canonical result와 `result_ref`
- compact `turn.state.v1`과 `state_ref`
- `answer.sections.v1`
- download ref 및 expiry
- `trace_id`, stage status, GaiA follow-up metadata

`answer.sections.v1`은 다음 section을 가진다.

| Section | 계약 |
| --- | --- |
| `summary` | 검증된 deterministic 또는 claim-validated prose |
| `result_table` | columns, labels, preview pointer, total row count, result ref를 가진 descriptor |
| `applied_criteria` | canonical `response.scope`를 가리키는 표시 descriptor |
| `analysis_evidence` | lineage/fact/contract ref의 bounded projection |
| `notices` | canonical `response.notices`를 가리키는 표시 descriptor |
| `downloads` | canonical `response.data_refs`를 가리키는 표시 descriptor |
| `next_questions` | 최대 3개의 bounded follow-up suggestion |

`result_table`은 row 배열이나 result ref를 다시 소유하지 않는다. v5 consumer와 같은 `row_source="data.rows"`와 `result_ref_source="data_refs[role=result]"`만 사용한다. `applied_criteria`, `notices`, `downloads`도 canonical top-level source pointer만 가지며 값을 복제하지 않는다.

`download.item.v1`은 `role=result|source`, owner/session-bound opaque `ref`, `url`, `format=csv`, `expires_at`, `row_count`, `content_sha256`, `label`만 가진다. credential, physical query, raw header는 포함하지 않는다. URL이 아직 발급되지 않았으면 ref만 반환할 수 있다.

GaiA terminal은 검증된 `response.v1`을 다음과 같이 변환한다.

- `answer`: display toggle을 적용한 Chat body가 아니라 canonical `response.message`
- `metadata.urls`: `response.data_refs`의 허용된 download item URL
- `metadata.followup_questions`: `next_questions` 중 최대 3개
- `metadata.trace_id`는 `response.trace.trace_id`에서, `metadata.usage`는 validated usage projection에서 변환
- 지원하지 않는 `docs`, `images`, `knowhows`는 빈 배열

정상 성공 경로의 side-effect와 output 순서는 반드시 다음과 같다.

1. result/source row ref 저장
2. final `executed.result.v1` content-addressed publish와 compact state compare-and-swap 성공
3. full source/result runtime frame 해제
4. 동일한 immutable `response.v1`에서 Message, API Data, GaiA output을 fan-out

Response assembler는 final `executed.result.v1`, next `turn.state.v1` hash와 opaque refs를 미리 계산해 response candidate에 pin한다. State gate는 immutable executed contract를 idempotent하게 publish하고 `(owner, session, expected version, parent hash)` CAS로 그 exact state/ref만 활성화한다. CAS가 실패한 content-addressed contract는 활성 state에서 참조되지 않으며 TTL로 정리하고, candidate response는 terminal로 보내지 않는다.

Presentation adapter가 Message 문자열을 다시 파싱해 API/GaiA payload를 만들거나, terminal마다 결과를 재계산하는 것은 금지한다.

## 9. Final response

```json
{
  "contract_version": "response.v1",
  "response_type": "data_analysis",
  "status": "ok|partial|empty|error|needs_clarification",
  "stage_status": {
    "route": "ok",
    "intent": "ok",
    "plan": "ok",
    "retrieval": "ok",
    "execution": "ok",
    "answer": "ok"
  },
  "message": "검증된 사용자 표시 문장",
  "error": null,
  "clarification": null,
  "data_mode": "dummy|live",
  "analysis_mode": "fresh_query|previous_result_transform|previous_source_transform|previous_result_enrich|followup_requery|explain_previous",
  "request": {
    "request_id": "request:...",
    "turn_id": "turn:...",
    "question": "사용자 질문"
  },
  "intent_plan": {
    "contract_sha256": "...",
    "selected_candidate_ids": [],
    "route": "deterministic",
    "route_reason": "unique_complete_selection",
    "eligibility_proof_sha256": "..."
  },
  "analysis": {
    "plan_id": "plan:...",
    "plan_fingerprint": "...",
    "operator_ids": [],
    "result_contract_sha256": "...",
    "source_modes": {"production": "dummy"}
  },
  "data": {
    "columns": [],
    "display_labels": {},
    "rows": [],
    "row_count": 0,
    "rows_are_preview": true
  },
  "data_refs": [
    {
      "contract_version": "download.item.v1",
      "role": "result",
      "ref": "result:...",
      "url": null,
      "format": "csv",
      "expires_at": "...",
      "row_count": 0,
      "content_sha256": "...",
      "label": "분석 결과"
    }
  ],
  "answer_sections": {
    "contract_version": "answer.sections.v1",
    "summary": {},
    "result_table": {
      "row_source": "data.rows",
      "result_ref_source": "data_refs[role=result]"
    },
    "applied_criteria": {"source": "response.scope"},
    "analysis_evidence": [],
    "notices": {"source": "response.notices"},
    "downloads": {"source": "response.data_refs"},
    "next_questions": []
  },
  "scope": {},
  "notices": [],
  "state": {
    "state_ref": "state:...",
    "state_version": 8
  },
  "trace": {
    "trace_id": "trace:..."
  },
  "usage": {
    "intent_llm_calls": 0,
    "intent_retry_calls": 0,
    "answer_llm_calls": 0,
    "code_llm_calls": 0,
    "repair_llm_calls": 0,
    "input_tokens": 0,
    "output_tokens": 0
  }
}
```

`request`, `intent_plan`, `analysis`, `data`, `data_refs`, `state`, `trace`는 v5 structured API consumer와 같은 wire key다. 각 control object는 bounded compatibility projection만 가지며 full request capsule, metadata bundle, plan DAG, state object, verbose trace를 복제하지 않는다. `intent_plan.route`는 `deterministic|intent_llm|unsupported`다. deterministic에서도 공통 `analysis.intent.v1`이 정상 생성되므로 기존 의미를 보존해 `stage_status.intent=ok`를 사용하고 `intent_plan.route`, trace의 `generator/llm_called`, usage counter로 LLM 비호출을 표현한다. Intent LLM 경로의 intent status는 `ok|error`, unsupported는 `not_applicable`이다. `usage`는 provider가 보고한 token과 실제 stage call counter를 정규화한 closed projection이며 prompt/response 본문을 포함하지 않는다. route별 exact call counter는 `deterministic|unsupported=0`, `intent_llm=1`, `intent_retry_calls=0`이다. syntax/schema/provider 오류는 재호출 없이 canonical error로 종료한다.

v5 호환 `data_mode`는 source 결과 중 하나라도 Dummy이면 `dummy`, 모두 실제 source이면 `live`다. source별 정밀 값은 `analysis.source_modes`에 두고, follow-up/실행 경로는 별도 `analysis_mode`로 표현해 기존 필드 의미를 바꾸지 않는다.

`data.columns`는 canonical field이며 label은 `display_labels`로 분리한다. 같은 데이터를 다른 이름의 컬럼으로 복제하지 않는다. v5 web/API consumer 호환을 위해 bounded row의 canonical 위치는 `data.rows`, ref의 canonical 위치는 `data_refs[]`다. 전체 row count가 `data.rows`보다 크면 `rows_are_preview=true`이고 full result는 result-role ref에서 읽는다. `answer_sections`는 top-level data/data_refs/scope/notices를 pointer로 참조한다.

`status=error`이면 `data`는 null이고 `error`는 `ARCHITECTURE.md`의 canonical `error.v1` payload다. `status=needs_clarification`이면 `data`와 `error`는 null이고 `clarification`은 아래처럼 candidate ID만 노출한다.

`intent_plan.route=unsupported`인 error는 result/source store와 state CAS를 실행하지 않는다. 이전 state가 있으면 response에는 동일한 `state_ref/state_version`의 bounded pointer만 유지하고, 없으면 state는 null이다. Unsupported telemetry write는 분석 state mutation과 별도이며 실패해도 요청을 다른 실행 route로 전환하지 않는다.

`status=partial`은 plan/result contract가 해당 source/metric을 optional로 명시했고 나머지 결과가 lineage를 완전히 만족할 때만 허용한다. 누락 metric을 0이나 다른 source 값으로 채우지 않으며 `stage_status`와 canonical notice에 빠진 scope/error ID를 기록한다. required source 실패는 항상 `status=error`다.

```json
{
  "question": "어느 공정 범위를 의미하나요?",
  "candidate_ids": ["process_group.WB", "process_exact.WBM"],
  "reason": "ambiguous_metadata_candidate"
}
```

## 10. Langflow terminal surface

Data Analysis Flow는 하나의 validated `response.v1`에서 다음 세 output surface를 제공한다.

| Surface | Langflow type | 내용 |
| --- | --- | --- |
| 사용자 Message | `Message` | `display.options.v1`을 적용한 section body |
| API terminal | `Data`, `is_output=True` | 전체 `response.v1`; Message를 역파싱하지 않음 |
| GaiA terminal | `Message` + `Data` | `{answer, metadata: gaia.metadata.v1}` |

API 호출자는 Message 표시 옵션과 무관하게 동일한 structured status/data/sections/refs를 받는다. Chat Output은 사용자 Message를, GaiA consumer는 answer와 metadata를 사용한다.

## 11. Future exploration payload 격리

초기 v6 runtime에는 exploration envelope이나 terminal이 없다. 미래 계약의 `exploration.request.v1`, `exploration.job.v1`, `exploration.response.v1`, `exploration_ref`는 이 문서의 trusted `request/analysis/result/response/state` namespace와 호환되지 않는 별도 계층이다.

- `exploration_ref`를 `result_ref`, `source_ref`, `state_ref`로 파싱하거나 승격하지 않는다.
- `exploration.response.v1`을 `response.v1`, `analysis.result.v1`, `executed.result.v1`로 변환하지 않는다.
- exploration row/preview를 Answer LLM, core Message/API/GaiA, download, follow-up state에 넣지 않는다.
- 별도 store/prefix/signing key/TTL/ACL과 명시적 `untrusted_exploration` classification을 사용한다.

이 namespace 예약은 runtime 활성화를 의미하지 않는다. 별도 보안·운영 승인이 없으면 submit/status endpoint와 worker는 존재하지 않거나 disabled여야 한다.
