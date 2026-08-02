# v6 자연어 등록 입력

이 폴더의 TXT는 비전문 작업자가 Langflow 등록 Flow에 넣는 실제 자유형 업무 설명 예시다. 작업자는 JSON, DSL, compact IR, canonical/등록 ID, 컬럼 타입, 물리 컬럼 매핑, SQL 또는 엄격한 문장 형식을 배울 필요가 없다. 아는 업무 사실을 평소 쓰는 문장이나 bullet로 적으면 된다. 문장 순서, 제목, 말투와 가벼운 오탈자가 달라도 허용한다.

이 파일의 제목과 bullet은 읽기 편한 예시일 뿐 등록 문법이 아니다. 같은 업무 사실을 제목 없이 문단으로 섞어 쓴 수동 재작성 검증본은 `validation/fixtures/authoring/freeform_reordered_v1/`에 있으며, 기본 예시와 동일한 Langflow authoring 경로로 검증한다.

- `domain_v6.txt`: 업무 목적, 용어, 계산 의미, 데이터 관계와 분석 방법을 설명한다.
- `dataset_v6.txt`: 어떤 업무 자료가 있고 무엇을 확인할 수 있는지, 날짜 기준과 기본 표시 항목 등 아는 범위만 설명한다.
- `main_filter_v6.txt`: 날짜·제품·공정 같은 조회 기준과 현장에서 실제로 쓰는 표현을 설명한다.
- `domain_policy_v6.txt`: 운영자 소유의 특화 프롬프트·출력 정책·등록 함수 descriptor를 별도 Domain Policy Flow로 관리한다. 일반 작업자 입력이 아니다.

최초 Domain bootstrap에서는 앞의 세 작업자 TXT를 각자의 한글 입력 노드에 함께 연결한다. Flow canvas에는 Domain·Dataset·Main Filter용 공통 Prompt Template node가 세 개로 분리되어 있고, 각 원문은 출처 hash를 봉인한 뒤 Gemini에 최대 한 번씩 전달된다. 세 branch는 같은 hash의 `approved_semantic_vocabulary`에서 작업자 표현과 같은 업무 label을 찾아 내부 strict proposal 세 개를 만든다.

승인 semantic vocabulary는 dataset의 `id/family/business labels`와 field·metric·relation·grain·ordering·predicate·recipe·entity-group의 `id/business labels`만 포함한다. 물리 컬럼, 타입, 역할, coercion, source/config/query ref, metric binding, SQL과 실행 payload는 Gemini에 보내지 않는다. 내부 ID는 LLM과 compiler 사이의 후보 선택용이며 작업자가 입력할 항목이 아니다.

Dataset용 compact IR 역시 Gemini 내부 출력 형식이다. 일반 작업자가 작성하는 TXT 문법이 아니다. 결정론적 engine은 vocabulary membership과 schema를 확인하고, dataset ID가 중복된 card는 거부한다. 같은 dataset의 동일 field descriptor가 반복된 경우 의미와 선택 속성이 동등하면 하나로 합치고 alias를 dedupe하지만, 단위·연산자·정책·binding이 충돌하면 저장하지 않는다. 그 뒤 승인 Source Registry와 정확히 결합해 실제 family·physical column·semantic type·roles와 실행 참조를 주입하고 전체 package를 컴파일한다.

표현이 여러 승인 후보에 해당하거나 필수 업무 정보가 빠지면 Flow는 추측 저장하지 않는다. “당일 생산과 생산 이력 중 어느 자료인가요?”처럼 작업자가 답할 수 있는 쉬운 질문만 돌려준다. 등록 ID, canonical ID, JSON/DSL, 타입, 물리 컬럼이나 schema 경로를 작업자에게 묻는 질문은 올바른 UX가 아니다.

`metadata/domain_packs/manufacturing/approved_source_registry.json`은 운영자가 검토한 비밀 없는 소스 매핑이다. 실제 자격 증명과 실행 가능한 쿼리 본문은 exported Flow나 TXT에 저장하지 않고 서버 측 실행 어댑터가 관리한다. 기존 v5 원문은 migration provenance와 hash 검증을 위해 수정하지 않으며, 이 폴더의 TXT에도 API key나 MongoDB URI 같은 비밀값을 넣지 않는다.

`trusted_source_manifest.json`과 `trusted_executable_blueprint.json`은 제조 패키지 검증용 오라클일 뿐 일반 작업자의 기본 자유형 등록 입력이 아니다.
