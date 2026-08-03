# v6 자연어 Metadata 3컬렉션 항목 저장 가이드

## 결정

운영자가 관리하는 metadata는 아래 세 MongoDB collection만 사용한다.

| Collection | 저장 단위 | 예시 section |
| --- | --- | --- |
| `agent_v6_domain_metadata` | 도메인 규칙 한 항목 | `profile`, `metrics`, `entity_groups`, `recipes`, `aliases` |
| `agent_v6_table_catalog` | 데이터셋 또는 데이터셋 alias 한 항목 | `datasets`, `aliases` |
| `agent_v6_main_filter` | 필터·상태·필드 alias 한 항목 | `aliases` |

분석 결과와 멀티턴 상태는 metadata가 아니므로 `agent_v6_result_store`, `agent_v6_session_state`를 계속 사용한다. Source adapter의 secret과 raw data는 metadata collection에 넣지 않는다. Oracle·SQL·Datalake의 검토된 read-only query는 예외적으로 해당 dataset 항목의 `payload.source_config.query_template`에 저장한다.

## 작업자 등록 흐름

1. 작업자는 JSON이나 DSL이 아니라 기존 TXT와 같은 자유로운 업무 문장 한 항목을 입력한다.
2. 외부 공통 Prompt Template과 특화 Prompt Template이 자연어를 closed annotation/IR로 변환한다.
3. 결정론적 compiler가 이번 항목의 schema, 승인 어휘·Source binding, 중복과 security를 검증한다.
4. 모호하면 짧은 업무 확인 질문을 반환하고 저장하지 않는다.
5. 빈 DB에서는 메인 필터부터 저장할 수 있다. 아직 비어 있는 영역이 있으면 정상 항목으로 저장하고 `실행 준비 중`과 누락 영역을 반환한다.
6. 테이블 카탈로그와 도메인 항목까지 채워지는 순간 세 collection 전체를 runtime catalog로 자동 결합·검증한다. 마지막 항목이 dependency closure를 깨면 그 마지막 write는 거부한다.
7. 분석 Flow의 01번 loader는 세 collection이 모두 완전할 때만 typed Domain Package를 메모리에서 컴파일한다. 부분 등록 상태는 분석 실행에 사용하지 않는다.

LLM은 자연어 해석에만 관여한다. MongoDB 항목을 실행 가능한 package로 만드는 작업과 분석 실행은 LLM이 아니라 compiler와 Typed Execution IR 실행기가 담당한다.

## MongoDB 항목 계약

모든 문서는 아래 여섯 필드만 가진다.

```json
{
  "_id": "domain:metrics:WIP_QTY",
  "section": "metrics",
  "key": "WIP_QTY",
  "natural_text": "WIP은 현재 재공 수량을 뜻해.",
  "payload": {},
  "updated_at": "2026-08-02T00:00:00+00:00"
}
```

- `_id`: `collection-role:section:key` 형태의 항목 식별자
- `section`, `key`: 어떤 업무 항목인지 나타내는 읽기 쉬운 식별자
- `natural_text`: 작업자가 입력한 원문. 기존 묶음 문서를 이관하면서 특정 항목과 정확히 연결할 수 없는 경우에는 `key/payload` 기반의 짧은 항목 설명을 저장하며, 이후 작업자가 같은 항목을 다시 등록하면 새 입력 원문으로 교체한다.
- `payload`: LLM 결과를 compiler가 검증한 해당 항목의 typed 값
- `updated_at`: 마지막 저장 시각

Oracle/Datalake dataset 항목의 payload 예시는 다음과 같다. 내부 줄바꿈과 placeholder 철자는 등록 TXT 그대로 보존된다.

```json
{
  "source_type": "oracle",
  "source_config": {
    "source_type": "oracle",
    "db_key": "PNT_RPT",
    "query_template": "SELECT WORK_DATE, PRODUCTION\nFROM PROD_TABLE2\nWHERE WORK_DATE = {DATE}",
    "required_params": ["DATE"]
  },
  "parameters": {
    "DATE": {"type": "LocalDate", "required": true, "source_format": "%Y%m%d"}
  }
}
```

`query_template`은 단일 read-only `SELECT/WITH`만 허용한다. Dataset LLM에는 SQL 본문을 보내지 않으며 compiler가 원본 TXT에서 직접 추출한다. `{DATE}` 같은 모든 placeholder는 같은 dataset의 required typed parameter로 선언되어야 한다.

MongoDB에는 `source_sha256`, `section_sha256`, `release_manifest_sha256`, `package_meta`, `document_sha256`, `release_manifest`, `release_id`, `contract_version`, `domain_id`, `environment`, `revision`을 저장하지 않는다. Domain Package의 contract와 hash는 세 collection을 읽은 뒤 메모리에서 계산하며 DB 관리 항목이 아니다.

도메인 식별자는 별도 `domain_id` 필드가 아니라 `section=profile` 문서의 `key`를 사용한다. 한 세트의 세 collection은 한 업무 도메인을 나타내며 실행 환경은 코드에서 `production`, 시간대는 `Asia/Seoul`로 고정한다.

## Langflow node 계약

- `메타데이터 등록 프롬프트 컨텍스트`: 자유형 TXT를 bounded runtime context로 만든다.
- 외부 공통/특화 Prompt Template: 실제 LLM instruction을 소유한다.
- `조건부 LLM 호출`: 필요한 분기만 호출한다.
- `메타데이터 등록 엔진`: LLM 결과를 closed decode하고 전체 catalog를 결정론적으로 검증한 뒤 항목 문서로 transaction 저장한다.
- `01 사용 가능 메타데이터 불러오기`: URI, database, 세 collection 이름, timeout을 입력받아 모든 항목을 결합·컴파일한다. domain/environment/source mode 입력은 없다.
- `24 채팅 메시지 표시 설정`: 결과표·적용 기준·Pandas 등가 코드·Typed Execution IR 등 표시 항목을 각각 선택한다.

`mode=save`가 기본이다. 신규 `section+key`는 저장하지만 기존 key의 payload가 다르면 안전하게 중단하고 `replace`를 안내한다. `mode=replace`는 동일 `section+key`만 교체하고 입력에서 언급하지 않은 기존 항목은 유지한다. `mode=validate_only`는 같은 항목·중복 검증을 수행하되 MongoDB에는 쓰지 않는다. 세 영역이 모두 준비된 경우에만 `validate_only`도 전체 compile 결과를 함께 반환한다.

등록 유형, 도메인 ID, 운영 환경, dry-run은 작업자 입력이 아니다. 등록 유형은 도메인/테이블 카탈로그/메인 필터 Flow별로 고정되며, 도메인 ID는 승인 레지스트리에서 내부적으로 읽고 운영 환경은 `production`으로 고정한다.

## 정합성과 이력

부분 등록 중에는 이번 항목의 닫힌 구조·승인 대상·중복을 검증하고, 세 영역이 모두 준비되면 저장 전 전체 item set을 메모리에서 다시 컴파일한다. 따라서 잘못된 payload, 누락된 데이터셋, 중복 key, 지원하지 않는 section은 실행 가능 상태가 되기 전에 거부된다. 완성 저장 후에는 같은 loader로 다시 읽어 runtime catalog 동치를 확인한다. Hash를 MongoDB 문서 사이 전달하거나 비교하지 않는다.

이 구조는 자동 revision history나 active pointer rollback을 제공하지 않는다. 이력이 필요하면 MongoDB 백업/change stream 또는 별도 감사 시스템을 사용하며, 그것을 runtime metadata collection으로 추가하지 않는다.
