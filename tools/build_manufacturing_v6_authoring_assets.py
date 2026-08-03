"""Build manufacturing-only validation oracles for v6 domain authoring.

``domain_v6.txt`` remains the user's free-form natural-language input.  It is
never rewritten into the narrow source-manifest grammar.  This administrative
tool derives a separate exhaustive inventory declaration and self-hashed
manifest from the reviewed compiled manufacturing package so live validation
can compare a model proposal with a known oracle.  These artifacts are not a
required runtime input and must not become the default contract for new domains.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reference_runtime.authoring_blueprint import (
    build_executable_blueprint,
    validate_executable_blueprint,
)
from reference_runtime.authoring_source_manifest import (
    MAX_SOURCE_BYTES,
    _draft_inventory,
    extract_authoring_source_manifest,
    validate_draft_inventory_coverage,
)
from reference_runtime.domain_authoring_patches import (
    runtime_catalog_v2_to_authoring_draft,
)
from reference_runtime.domain_packages import (
    GENERIC_V2_OPERATIONS,
    validate_domain_package,
)


DEFAULT_PACKAGE = (
    ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "compiled"
    / "domain_package.json"
)
DEFAULT_RAW_SOURCE = ROOT / "metadata" / "authoring" / "v6_inputs" / "domain_v6.txt"
DEFAULT_INVENTORY_SOURCE = (
    ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "compiled"
    / "trusted_authoring_inventory_v6.txt"
)
DEFAULT_MANIFEST = (
    ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "trusted_source_manifest.json"
)
DEFAULT_BLUEPRINT = (
    ROOT
    / "metadata"
    / "domain_packs"
    / "manufacturing"
    / "trusted_executable_blueprint.json"
)
DEFAULT_PIN = DEFAULT_BLUEPRINT.with_suffix(".sha256")


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _render_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_or_check(path: Path, expected: str, *, check: bool) -> None:
    if check:
        actual = path.read_text(encoding="utf-8") if path.is_file() else None
        if actual != expected:
            raise SystemExit(f"stale or missing generated artifact: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8", newline="\n")


def _safe_description(value: Any, fallback: str) -> str:
    text = " ".join(str(value or "").split()).strip()
    # Inventory grammar is deliberately line-oriented.  Keep operator-facing
    # prose useful without letting stored descriptions open another declaration.
    for marker in (" 데이터셋", " dataset", " canonical 필드", " canonical field"):
        text = text.replace(marker, " 자료")
    return text.rstrip(".다") or fallback


def _target_types(draft: Mapping[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    section_types = {
        "datasets": "dataset",
        "metrics": "metric",
        "entity_groups": "entity_group",
        "grains": "grain",
        "relations": "relation",
        "predicates": "predicate",
        "recipes": "recipe",
    }
    for section, target_type in section_types.items():
        cards = draft.get(section)
        if isinstance(cards, Mapping):
            for key in cards:
                result[str(key)].add(target_type)
    datasets = draft.get("datasets")
    if isinstance(datasets, Mapping):
        for dataset in datasets.values():
            fields = dataset.get("fields") if isinstance(dataset, Mapping) else None
            if isinstance(fields, Mapping):
                for field in fields:
                    result[str(field)].add("field")
    aliases = draft.get("aliases")
    if isinstance(aliases, Mapping):
        for card in aliases.values():
            if not isinstance(card, Mapping):
                continue
            target_key = card.get("target_key")
            target_type = card.get("target_type")
            if isinstance(target_key, str) and isinstance(target_type, str):
                result[target_key].add(target_type)
    return result


def _quote_alias(value: str) -> str:
    if "\n" in value or "\r" in value:
        raise ValueError("alias values must be single-line")
    if '"' not in value:
        return f'"{value}"'
    if "'" not in value:
        return f"'{value}'"
    raise ValueError("alias values containing both quote styles cannot be declared safely")


def _render_alias_cards(
    draft: Mapping[str, Any],
    alias_bindings: list[dict[str, str]],
) -> tuple[list[str], dict[str, int]]:
    targets_by_alias: dict[str, set[str]] = defaultdict(set)
    for binding in alias_bindings:
        targets_by_alias[binding["alias"]].add(binding["target"])

    # The source-manifest contract intentionally rejects one natural-language
    # label bound to two targets.  Such legacy collisions remain sealed in the
    # executable blueprint, but are not re-declared as authoring shorthand.
    ambiguous = {alias for alias, targets in targets_by_alias.items() if len(targets) > 1}
    labels_by_target: dict[str, list[str]] = defaultdict(list)
    for alias, targets in sorted(targets_by_alias.items()):
        if alias not in ambiguous:
            labels_by_target[next(iter(targets))].append(alias)

    target_types = _target_types(draft)
    lines: list[str] = []
    for target in sorted(labels_by_target):
        types = sorted(target_types.get(target) or {"alias"})
        target_type = types[0]
        labels = ", ".join(_quote_alias(value) for value in labels_by_target[target])
        lines.append(
            f"별칭 카드의 안정 식별자는 {target_type}:{target}이다. "
            f"대상 유형은 {target_type}, 대상 키는 {target}이다."
        )
        lines.append(f"사용자가 {labels}라고 말하면 {target}로 해석한다.")
    return lines, {
        "runtime_bindings": len(alias_bindings),
        "declared_bindings": sum(len(values) for values in labels_by_target.values()),
        "ambiguous_labels_omitted": len(ambiguous),
    }


def render_trusted_inventory_source(
    draft: Mapping[str, Any],
) -> tuple[str, dict[str, int]]:
    inventory = _draft_inventory(draft, GENERIC_V2_OPERATIONS)
    lines = [
        "# manufacturing v6 검증 전용 trusted inventory",
        "",
        (
            f"도메인 ID는 manufacturing이고 표시 이름은 "
            f'"{draft["display_name"]}"이다. 기본 언어는 {draft["locale"]}이고 '
            f"시간대는 {draft['timezone']}이다. "
            f"{_safe_description(draft.get('description'), '제조 업무 자료를 분석한다')}다."
        ),
        (
            "이 문서는 사용자 입력이 아니라 manufacturing 검증 oracle을 재현하기 위한 내부 선언문이다. "
            "일반 Domain Flow는 자유형 자연어 TXT 하나를 받아 closed draft proposal을 만들고 "
            "deterministic schema와 compiler로 검증한다."
        ),
        "",
        "## 데이터 자료와 canonical field",
        "",
    ]

    datasets = draft["datasets"]
    for dataset_id in inventory["datasets"]:
        dataset = datasets[dataset_id]
        fields = inventory["dataset_fields"][dataset_id]
        family = str(dataset.get("family") or "manufacturing")
        source_type = str(dataset.get("source_type") or "registered")
        time_scope = str(dataset.get("time_scope") or "registered")
        lines.append(
            f"{dataset_id} 데이터셋은 {family} 업무를 위한 검토된 읽기 전용 자료이다. "
            f"소스 유형은 {source_type}이고 시간 범위 정책은 {time_scope}이다. "
            f"canonical 필드는 {', '.join(fields)}이다."
        )

    role_items: list[str] = []
    for dataset_id in sorted(inventory["field_roles"]):
        for field_id in sorted(inventory["field_roles"][dataset_id]):
            roles = "|".join(inventory["field_roles"][dataset_id][field_id])
            role_items.append(f"{dataset_id}.{field_id}={roles}")
    lines.extend(
        [
            "",
            "## 실행 inventory",
            "",
            f"등록 field role은 {', '.join(role_items)}이다.",
            f"등록 metric은 {', '.join(inventory['metrics'])}이다.",
            "데이터 자료 간 별도 결합 관계 목록은 이 도메인 pack에 등록되어 있지 않다.",
            (
                "등록 grain key는 "
                + ", ".join(
                    f"{grain}={'|'.join(keys)}"
                    for grain, keys in inventory["grain_keys"].items()
                )
                + "이다."
            ),
            (
                "product grain의 표시 필드는 빈 목록으로 고정한다. "
                "빈 목록은 선언 문법으로 추론하지 않고 검토된 blueprint byte를 그대로 사용한다."
            ),
            f"허용 operation은 {', '.join(inventory['operations'])}이다.",
            f"등록 recipe ID는 {', '.join(inventory['recipes'])}이다.",
            "",
            "## 자연어 표현",
            "",
        ]
    )
    alias_lines, alias_evidence = _render_alias_cards(draft, inventory["alias_bindings"])
    lines.extend(alias_lines)
    lines.extend(
        [
            "",
            "## 운영 원칙",
            "",
            (
                "상위 N, 하위 N, 최대값과 최소값의 전체 동률, 집계, 정렬, 컬럼 간 비교, "
                "등록된 순차 공정 범위와 presence 조건은 typed Execution IR로만 실행한다."
            ),
            (
                "credential, 연결 문자열, URL, SQL, Python 코드와 임의 실행 코드는 이 입력에 "
                "포함하지 않는다. pandas 코드 생성 모델과 repair 모델은 사용하지 않는다."
            ),
        ]
    )
    source = "\n".join(lines).strip() + "\n"
    source_bytes = len(source.encode("utf-8"))
    if source_bytes > MAX_SOURCE_BYTES:
        raise ValueError(
            f"generated source exceeds manifest budget: {source_bytes} > {MAX_SOURCE_BYTES}"
        )
    return source, {**alias_evidence, "source_bytes": source_bytes}


def _validate_inventory_exactness(
    manifest: Mapping[str, Any],
    draft: Mapping[str, Any],
    coverage: Mapping[str, Any],
) -> dict[str, Any]:
    required = coverage["counts"]["required"]
    actual = coverage["counts"]["actual"]
    exact_sections = (
        "datasets",
        "fields",
        "field_bindings",
        "field_roles",
        "metrics",
        "grains",
        "grain_keys",
        "relations",
        "relation_endpoints",
        "relation_keys",
        "relation_policies",
        "recipes",
        "operations",
    )
    mismatched = {
        section: {"required": required[section], "actual": actual[section]}
        for section in exact_sections
        if required[section] != actual[section]
    }
    if mismatched:
        raise ValueError(f"source inventory is not exhaustive: {mismatched}")
    # An empty grain display list cannot be represented by the deliberately
    # non-empty declaration item grammar; the blueprint preserves that byte.
    expected_display = manifest["inventories"]["grain_display_fields"]
    draft_display = _draft_inventory(draft, GENERIC_V2_OPERATIONS)[
        "grain_display_fields"
    ]
    if expected_display or any(draft_display.values()):
        raise ValueError("manufacturing grain display-field exception changed")
    return {"exact_sections": list(exact_sections), "mismatched": mismatched}


def build_assets(
    *,
    package_path: Path,
    raw_source_path: Path,
    inventory_source_path: Path,
    manifest_path: Path,
    blueprint_path: Path,
    pin_path: Path,
    environment: str,
    check: bool,
) -> dict[str, Any]:
    package = validate_domain_package(_read_object(package_path))
    if package.get("domain_id") != "manufacturing":
        raise ValueError("compiled package must be the manufacturing domain")
    raw_source = raw_source_path.read_text(encoding="utf-8")
    raw_source_bytes = len(raw_source.encode("utf-8"))
    if not raw_source.strip() or raw_source_bytes > MAX_SOURCE_BYTES:
        raise ValueError("free-form domain source is empty or exceeds the input budget")
    if raw_source.lstrip().startswith(("{", "[")):
        raise ValueError("manufacturing domain_v6.txt must remain free-form natural language, not JSON")
    draft = runtime_catalog_v2_to_authoring_draft(package["runtime_catalog"])
    inventory_source, source_evidence = render_trusted_inventory_source(draft)
    manifest = extract_authoring_source_manifest(inventory_source)
    coverage = validate_draft_inventory_coverage(
        manifest,
        draft,
        supported_operations=GENERIC_V2_OPERATIONS,
    )
    exactness = _validate_inventory_exactness(manifest, draft, coverage)
    blueprint = build_executable_blueprint(
        deepcopy(draft),
        domain_id="manufacturing",
        environment=environment,
        source_manifest=manifest,
    )
    pin = str(blueprint["blueprint_sha256"])
    validate_executable_blueprint(
        blueprint,
        expected_blueprint_sha256=pin,
        expected_domain_id="manufacturing",
        expected_environment=environment,
        source_manifest=manifest,
    )

    _write_or_check(inventory_source_path, inventory_source, check=check)
    _write_or_check(manifest_path, _render_json(manifest), check=check)
    _write_or_check(blueprint_path, _render_json(blueprint), check=check)
    _write_or_check(pin_path, pin + "\n", check=check)
    return {
        "status": "verified" if check else "generated",
        "raw_source": str(raw_source_path),
        "raw_source_contract": "free_form_natural_language",
        "raw_source_bytes": raw_source_bytes,
        "raw_source_sha256": hashlib.sha256(raw_source.encode("utf-8")).hexdigest(),
        "trusted_inventory_source": str(inventory_source_path),
        "trusted_inventory_source_sha256": manifest["source_sha256"],
        "trusted_manifest": str(manifest_path),
        "source_manifest_sha256": manifest["manifest_sha256"],
        "source_counts": manifest["counts"],
        "source_evidence": source_evidence,
        "coverage_passed": coverage["passed"],
        "coverage_missing": coverage["counts"]["missing"],
        "inventory_exactness": exactness,
        "blueprint": str(blueprint_path),
        "blueprint_sha256": pin,
        "executable_sha256": blueprint["executable_sha256"],
        "pin": str(pin_path),
        "environment": environment,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--raw-source", type=Path, default=DEFAULT_RAW_SOURCE)
    parser.add_argument(
        "--inventory-source", type=Path, default=DEFAULT_INVENTORY_SOURCE
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--blueprint", type=Path, default=DEFAULT_BLUEPRINT)
    parser.add_argument("--pin", type=Path, default=DEFAULT_PIN)
    parser.add_argument("--environment", default="production")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_assets(
        package_path=args.package,
        raw_source_path=args.raw_source,
        inventory_source_path=args.inventory_source,
        manifest_path=args.manifest,
        blueprint_path=args.blueprint,
        pin_path=args.pin,
        environment=args.environment,
        check=args.check,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
