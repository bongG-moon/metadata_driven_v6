"""Canonical v6 validation source fixture.

Rows are emitted in each dataset's *physical* schema so every deterministic
test exercises the Source Contract Merger.  The fixture is deliberately small
but covers all 30 baseline shapes, the six date cases, MT-1..MT-5, and the
typed-operator matrix (ranking, presence, joins, nulls, history and comparison).
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from .canonical import sha256_json
from .metadata_compiler import build_runtime_catalog, load_runtime_catalog
from .source_contracts import canonicalize_rows


REFERENCE_INSTANT = "2026-07-30T09:00:00+09:00"
REFERENCE_DATE = "2026-07-30"
REFERENCE_TIMEZONE = "Asia/Seoul"


def _product(
    family: str,
    mode: str,
    density: str,
    tech: str,
    pkg1: str,
    pkg2: str,
    lead: str,
    mcp_no: str,
    device: str,
    tsv: str = "",
    *,
    org: str = "PKG",
) -> dict[str, str]:
    return {
        "FAMILY": family,
        "MODE": mode,
        "DENSITY": density,
        "TECH": tech,
        "ORG": org,
        "PKG1": pkg1,
        "PKG2": pkg2,
        "LEAD": lead,
        "MCP_NO": mcp_no,
        "TSV_DIE_TYP": tsv,
        "DEVICE": device,
        "DEVICE_DESC": f"{device} validation product",
    }


PRODUCTS: dict[str, dict[str, str]] = {
    "MOBILE_A": _product("MOBILE", "LPDDR5X", "32G", "1B", "UFBGA", "MOBILE", "180", "", "DEV-MOBILE-A"),
    "MOBILE_B": _product("MOBILE", "LPDDR5", "16G", "1C", "LFBGA", "MOBILE", "200", "", "DEV-MOBILE-B"),
    "POP_A": _product("MOBILE", "LPDDR5X", "32G", "1B", "UFBGA", "POP", "180", "P-001", "DEV-POP-A"),
    "HBM_A": _product("HBM", "HBM3E", "24G", "1A", "HBM", "TSV", "300", "H-001", "DEV-HBM-A", "12Hi"),
    "HBM_B": _product("HBM", "HBM3", "16G", "1A", "HBM", "TSV", "240", "H-002", "DEV-HBM-B", "8Hi"),
    "L267": _product("MCP", "LPDDR5", "16G", "1C", "LFBGA", "MCP", "267", "L-267A1", "DEV-L267"),
    "L218": _product("MCP", "LPDDR4", "8G", "1Y", "FBGA", "MCP", "218", "L-218K8H", "DEV-L218"),
    "RG": _product("DDR", "DDR4", "32G", "RG", "FBGA", "DDP", "96", "", "DEV-RG-DDR4", org="DDP"),
    "SP": _product("DDR", "DDR5", "16G", "SP", "FCBGA", "SDP", "78", "", "DEV-SP-DDR5", org="4"),
    "RANK_1": _product("RANK", "R1", "8G", "R1", "FBGA", "STD", "64", "R-001", "DEV-RANK-1"),
    "RANK_2": _product("RANK", "R2", "8G", "R2", "FBGA", "STD", "64", "R-002", "DEV-RANK-2"),
    "RANK_3": _product("RANK", "R3", "8G", "R3", "FBGA", "STD", "64", "R-003", "DEV-RANK-3"),
    "RANK_4": _product("RANK", "R4", "8G", "R4", "FBGA", "STD", "64", "R-004", "DEV-RANK-4"),
    "RANK_5": _product("RANK", "R5", "8G", "R5", "FBGA", "STD", "64", "R-005", "DEV-RANK-5"),
    "RANK_6": _product("RANK", "R6", "8G", "R6", "FBGA", "STD", "64", "R-006", "DEV-RANK-6"),
}


PROCESSES: dict[str, tuple[str, int]] = {
    "INPUT": ("INPUT", 10),
    **{f"D/A{i}": (f"DA{i}", 90 + i * 10) for i in range(1, 7)},
    "D/S1": ("DS1", 160),
    **{f"W/B{i}": (f"WB{i}", 190 + i * 10) for i in range(1, 7)},
    "W/BM": ("WBM", 260),
    "FCB1": ("FCB1", 300),
    "FCB2": ("FCB2", 310),
    "FCB/H": ("FCBH", 320),
    "B/G1": ("BG1", 400),
    "B/G2": ("BG2", 410),
    "SBM": ("SBM", 500),
    "PKG OUT": ("PKGOUT", 900),
}


def physical_rows_for_dataset(dataset_key: str) -> list[dict[str, Any]]:
    builders = {
        "production_today": _production_today_rows,
        "production": _production_history_rows,
        "wip_today": _wip_today_rows,
        "wip": _wip_history_rows,
        "target": _target_rows,
        "equipment_assign": _equipment_rows,
        "eqp_uph": _uph_rows,
        "lot_status": _lot_rows,
        "hold_history": _hold_history_rows,
        "product_master": _product_master_rows,
    }
    builder = builders.get(str(dataset_key or "").lower())
    return deepcopy(builder() if builder else [])


def rows_for_dataset(dataset_key: str) -> list[dict[str, Any]]:
    """Compatibility name; v6 rows are intentionally still physical here."""

    return physical_rows_for_dataset(dataset_key)


def canonical_rows_for_dataset(
    dataset_key: str,
    runtime_catalog: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    catalog = runtime_catalog or _default_catalog()
    rows = physical_rows_for_dataset(dataset_key)
    canonical, _ = canonicalize_rows(dataset_key, rows, catalog, physical_schema=_physical_schema(rows))
    return canonical


def source_result_for_dataset(
    dataset_key: str,
    *,
    source_alias: str | None = None,
    rows: list[dict[str, Any]] | None = None,
    chunk_index: int = 0,
) -> dict[str, Any]:
    physical_rows = physical_rows_for_dataset(dataset_key) if rows is None else deepcopy(rows)
    content_sha = sha256_json(physical_rows)
    return {
        "contract_version": "source.result.v1",
        "source_result_id": f"dummy:{dataset_key}:{source_alias or dataset_key}:{chunk_index}:{content_sha[:16]}",
        "source_alias": source_alias or dataset_key,
        "dataset_key": dataset_key,
        "source_type": "dummy",
        "status": "ok" if physical_rows else "empty",
        "physical_schema": _physical_schema(physical_rows),
        "rows": physical_rows,
        "row_count": len(physical_rows),
        "chunk_index": int(chunk_index),
        "chunk_count": 1,
        "truncated": False,
        "row_set_complete": True,
        "content_sha256": content_sha,
    }


def source_results_for_jobs(
    jobs: Iterable[dict[str, Any]],
    runtime_catalog: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Execute thin dummy jobs with canonical parameters and filters."""

    catalog = runtime_catalog or _default_catalog()
    results: list[dict[str, Any]] = []
    for index, job in enumerate(jobs):
        if not isinstance(job, dict):
            raise TypeError("dummy job must be an object")
        dataset_key = str(job.get("dataset_key") or "")
        job_id = str(job.get("job_id") or "")
        # TypedExecutor owns the single ``source:`` namespace prefix.
        alias = str(job.get("source_alias") or job_id or dataset_key)
        physical_rows = physical_rows_for_dataset(dataset_key)
        dataset_bindings = (catalog.get("datasets") or {}).get(dataset_key, {}).get("fields") or {}
        required_fields = [str(field) for field in job.get("required_fields") or dataset_bindings]
        canonical_rows, _ = canonicalize_rows(
            dataset_key,
            physical_rows,
            catalog,
            physical_schema=_physical_schema(physical_rows),
            required_fields=required_fields,
        )
        selected: list[dict[str, Any]] = []
        params = job.get("parameters") if isinstance(job.get("parameters"), dict) else job.get("params") if isinstance(job.get("params"), dict) else {}
        filters = job.get("filters")
        for physical, canonical in zip(physical_rows, canonical_rows, strict=True):
            if _params_match(canonical, params) and _filters_match(canonical, filters):
                bindings = dataset_bindings
                projected: dict[str, Any] = {}
                for field in required_fields:
                    binding = bindings.get(field) or {}
                    candidates = [str(binding.get("physical_column") or ""), *map(str, binding.get("physical_aliases") or [])]
                    present = next((name for name in candidates if name and name in physical), None)
                    if present is not None:
                        projected[present] = physical[present]
                selected.append(projected)
        result = source_result_for_dataset(dataset_key, source_alias=alias, rows=selected, chunk_index=int(job.get("chunk_index") or 0))
        result["source_result_id"] = f"dummy:{job.get('job_id') or index}:{result['content_sha256'][:16]}"
        result["applied_parameters"] = deepcopy(params)
        result["applied_filters_sha256"] = sha256_json(filters or {})
        results.append(result)
    return results


def _default_catalog() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    path = root / "metadata" / "fixtures" / "compiled" / "runtime_catalog.json"
    if path.is_file():
        return load_runtime_catalog(path)
    return build_runtime_catalog(root / "metadata" / "authoring")


def _production_today_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.append(_production_row("20260730", "L267", "INPUT", 292, shift="1"))
    rows.append(_production_row("20260730", "L218", "INPUT", 440, shift="1"))
    rows.append(_production_row("20260730", "MOBILE_A", "INPUT", 210, shift="1"))
    rows.append(_production_row("20260730", "MOBILE_B", "INPUT", 180, shift="1"))
    rows.extend(
        [
            _production_row("20260730", "L218", "PKG OUT", 300, shift="1"),
            _production_row("20260730", "MOBILE_A", "PKG OUT", 250, shift="1"),
            _production_row("20260730", "RANK_1", "PKG OUT", 80, shift="1"),
            _production_row("20260730", "RANK_2", "PKG OUT", 310, shift="1"),
        ]
    )
    for rank, product_key in enumerate(["RANK_1", "RANK_2", "RANK_3", "RANK_4", "RANK_5", "RANK_6"], start=1):
        rows.append(_production_row("20260730", product_key, "INPUT", 100, shift="1"))
        rows.append(_production_row("20260730", product_key, f"D/A{min(rank, 6)}", 1_300 - rank * 150, shift="1"))
        rows.append(_production_row("20260730", product_key, f"W/B{min(rank, 6)}", 850 - rank * 80, shift="1"))
    rows.extend(
        [
            _production_row("20260730", "SP", "FCB1", 692, shift="1"),
            _production_row("20260730", "HBM_A", "FCB2", 580, shift="1"),
            _production_row("20260730", "MOBILE_A", "W/BM", 37, shift="1"),
            _production_row("20260730", "POP_A", "W/BM", 55, shift="1", quantity=None),
            _production_row("20260730", "HBM_A", "W/BM", 900, shift="2"),
            _production_row("20260730", "RG", "B/G1", 423, shift="1"),
        ]
    )
    rows.extend(_comparison_rows("20260730"))
    return rows


def _production_history_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for process_index, process in enumerate([f"D/A{i}" for i in range(1, 7)], start=1):
        rows.append(_production_row("20260729", "RANK_1", process, 1_400 - process_index * 100))
    rows.extend(
        [
            _production_row("20260729", "MOBILE_A", "PKG OUT", 504),
            _production_row("20260729", "MOBILE_B", "PKG OUT", 420),
            _production_row("20260729", "POP_A", "PKG OUT", 610),
            _production_row("20260729", "SP", "FCB1", 900),
            _production_row("20260729", "SP", "FCB2", 891),
            _production_row("20260630", "SP", "FCB/H", 608),
            _production_row("20260630", "HBM_A", "FCB/H", 440),
            _production_row("20260624", "L218", "INPUT", 440),
        ]
    )
    for rank, product_key in enumerate(["RANK_1", "RANK_2", "RANK_3", "RANK_4", "RANK_5", "RANK_6"], start=1):
        rows.append(_production_row("20260624", product_key, "INPUT", 100))
    wb_values = [0, 200, 300, 400, 500, 600]
    for index, value in enumerate(wb_values, start=1):
        rows.append(_production_row("20260627", "RANK_1", f"W/B{index}", value))
    for process in ["FCB1", "FCB2", "FCB/H"]:
        rows.append(_production_row("20260705", "SP", process, 500 + PROCESSES[process][1]))
    for process in ["D/A1", "D/A2"]:
        rows.append(_production_row("20260709", "RANK_2", process, 700 + PROCESSES[process][1]))
    rows.extend(
        [
            _production_row("20260701", "L267", "INPUT", 300),
            _production_row("20260701", "MOBILE_A", "INPUT", 640),
            _production_row("20260701", "MOBILE_A", "W/BM", 321),
        ]
    )
    for process in [*[f"D/A{i}" for i in range(1, 7)], "D/S1", *[f"W/B{i}" for i in range(1, 7)]]:
        rows.append(_production_row("20260701", "RANK_1", process, 1_000 - PROCESSES[process][1]))
    return rows


def _wip_today_rows() -> list[dict[str, Any]]:
    rows = [
        _wip_row("20260730", "RANK_1", "D/A1", 300, "WIP-DA-1"),
        _wip_row("20260730", "RANK_2", "D/A2", 0, "WIP-DA-2"),
        _wip_row("20260730", "SP", "W/B2", 135, "WIP-WB2-SP"),
        _wip_row("20260730", "RG", "B/G1", 827, "WIP-BG-RG"),
    ]
    for index, product_key in enumerate(["RANK_1", "RANK_2", "RANK_3", "RANK_4", "RANK_5"], start=1):
        rows.append(_wip_row("20260730", product_key, f"W/B{index}", 900 - index * 100, f"WIP-WB-{index}"))
    return rows


def _wip_history_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, process in enumerate([f"W/B{i}" for i in range(1, 7)], start=1):
        rows.append(_wip_row("20260729", "HBM_A", process, 250 - index * 15, f"HBM-WB-{index}"))
    for index, process in enumerate(["FCB1", "FCB2", "FCB/H"], start=1):
        rows.append(_wip_row("20260729", "HBM_B", process, 300 - index * 25, f"HBM-FCB-{index}"))
    for index, process in enumerate([f"W/B{i}" for i in range(1, 7)], start=1):
        if index != 6:
            rows.append(_wip_row("20260626", "RANK_1", process, 100 + index * 20, f"BOH-WB-{index}"))
    for index, product_key in enumerate(["RANK_1", "RANK_2", "RANK_3", "RANK_4", "RANK_5", "RANK_6"], start=1):
        rows.append(_wip_row("20260624", product_key, "D/S1" if index % 2 else "D/A1", 1_400 - index * 200, f"RANK-WIP-{index}"))
    rows.append(_wip_row("20260729", "RG", "B/G1", 827, "RG-BG-WIP"))
    return rows


def _target_rows() -> list[dict[str, Any]]:
    quantities = [("MOBILE_A", 800, 1_200), ("MOBILE_B", 700, 1_050), ("POP_A", 900, 1_400), ("SP", 600, 950)]
    rows = []
    for work_date in ("2026-07-01", REFERENCE_DATE):
        for product_key, input_plan, out_plan in quantities:
            product = PRODUCTS[product_key]
            rows.append(
                {
                    "DATE": work_date,
                    "Mode": product["MODE"],
                    "DEN": product["DENSITY"],
                    "TECH": product["TECH"],
                    "PKG1": product["PKG1"],
                    "PKG2": product["PKG2"],
                    "LEAD": product["LEAD"],
                    "ORG": product["ORG"],
                    "MCP NO": product["MCP_NO"],
                    "INPUT 계획": input_plan,
                    "OUT 계획": out_plan,
                }
            )
    return rows


def _product_master_rows() -> list[dict[str, Any]]:
    return [
        {"DEVICE": "DEV-PM-1", "TECH": "PM", "DEN": "8G", "MODE": "A", "PKG_TYPE1": "FBGA", "PKG_TYPE2": "STD", "LEAD": "96", "MCP_NO": "DUP-1", "YIELD_RATE": 85.0},
        {"DEVICE": "DEV-PM-2", "TECH": "PM", "DEN": "8G", "MODE": "B", "PKG_TYPE1": "FBGA", "PKG_TYPE2": "STD", "LEAD": "", "MCP_NO": "DUP-1", "YIELD_RATE": 76.0},
        {"DEVICE": "DEV-PM-3", "TECH": "PM", "DEN": "8G", "MODE": "A", "PKG_TYPE1": "FBGA", "PKG_TYPE2": "STD", "LEAD": "120", "MCP_NO": "DUP-1", "YIELD_RATE": 70.0},
        {"DEVICE": "DEV-PM-4", "TECH": "PX", "DEN": "16G", "MODE": "A", "PKG_TYPE1": "FCBGA", "PKG_TYPE2": "SDP", "LEAD": "78", "MCP_NO": "UNQ-1", "YIELD_RATE": 91.0},
    ]


def _equipment_rows() -> list[dict[str, Any]]:
    assignments = [
        ("RANK_1", "D/A1", "EQM-R1", "RCP-R1", ["EQP-R1-1", "EQP-R1-2"]),
        ("RANK_2", "D/A2", "EQM-R2", "RCP-R2", ["EQP-R2-1"]),
        ("RANK_3", "D/A3", "EQM-R3", "RCP-R3", ["EQP-R3-1", "EQP-R3-2", "EQP-R3-3"]),
        ("HBM_A", "D/A1", "EQM-HBM", "RCP-002", ["EQP-HBM-1"]),
        ("SP", "FCB1", "EQM-SP", "RCP-SP", ["EQP-SP-1"]),
    ]
    rows: list[dict[str, Any]] = []
    for product_key, process, model, recipe, equipment_ids in assignments:
        product = PRODUCTS[product_key]
        for equipment_id in equipment_ids:
            rows.append(_equipment_row(product, process, model, recipe, equipment_id))
    return rows


def _uph_rows() -> list[dict[str, Any]]:
    definitions = [
        ("SP", "FCB2", "EQM-FCB-A", "RCP-FCB2-A", 140.0),
        ("SP", "FCB2", "EQM-FCB-B", "RCP-FCB2-B", 173.4),
        ("POP_A", "W/B1", "EQM-A", "RCP-L217-A", 123.4, "L-217A"),
        ("POP_A", "W/B2", "EQM-BG", "RCP-L217-B", 97.5, "L-217B"),
        ("MOBILE_B", "W/B1", "EQM-F315", "RCP-L116", 112.0, "L-116F315"),
        ("HBM_A", "D/A1", "EQM-HBM", "RCP-002", 88.2),
    ]
    rows = []
    for item in definitions:
        product_key, process, model, recipe, uph, *mcp_override = item
        product = deepcopy(PRODUCTS[product_key])
        if mcp_override:
            product["MCP_NO"] = mcp_override[0]
        if product["MCP_NO"].startswith("L-116"):
            product["LEAD"] = "315"
        oper, _ = PROCESSES[process]
        rows.append(
            {
                "EQUIP_MODEL": model,
                "OPER": oper,
                "OPER_NAME": process,
                "PRESS_CNT": 2,
                "MODE": product["MODE"],
                "TECH": product["TECH"],
                "ORG": product["ORG"],
                "DENSITY": product["DENSITY"],
                "PKG1": product["PKG1"],
                "PKG2": product["PKG2"],
                "LEAD": product["LEAD"],
                "MCP_NO": product["MCP_NO"],
                "RECIPE_ID": recipe,
                "UPH": uph,
                "LOAD_DT": "20260730",
                "BASE_DT": "20260730",
            }
        )
    return rows


def _lot_rows() -> list[dict[str, Any]]:
    return [
        _lot_row("HOLD-A", "HBM_A", "W/B1", "OnHold", 100, 25, 12.5, 40.0, "검증 HOLD A", "2026-07-30 07:10:00"),
        _lot_row("HOLD-B", "SP", "D/A5", "OnHold", 35, 9, 6.0, 18.0, "공정 범위 HOLD B", "2026-07-30 08:00:00"),
        _lot_row("HOLD-C", "RG", "D/S1", "OnHold", 38, 9, 11.0, 19.0, "D/S1 HOLD C", "2026-07-30 08:10:00"),
        _lot_row("RUN-WB2", "MOBILE_A", "W/B2", "NotOnHold", 80, 20, 5.0, 25.0, "", "2026-07-30 06:00:00"),
        _lot_row("WAIT-WB3", "POP_A", "W/B3", "NotOnHold", 60, 18, 11.0, 28.0, "", "2026-07-30 05:00:00"),
        _lot_row("RANGE-END", "HBM_B", "D/A4", "NotOnHold", 30, 8, 3.0, 12.0, "", "2026-07-30 09:00:00"),
    ]


def _hold_history_rows() -> list[dict[str, Any]]:
    return [
        _hold_row("HOLD-A", "HBM_A", "W/B1", "2026-07-30 04:00:00", "HA0", "A 이전 HOLD"),
        _hold_row("HOLD-A", "HBM_A", "W/B1", "2026-07-30 06:00:00", "HA1", "A 현재 HOLD"),
        _hold_row("HOLD-B", "SP", "D/A5", "2026-07-30 02:00:00", "HB0", "B 이전 HOLD"),
        _hold_row("HOLD-B", "SP", "D/A5", "2026-07-30 05:00:00", "HB1", "B 현재 HOLD"),
        _hold_row("HOLD-C", "RG", "D/S1", "2026-07-30 03:00:00", "HC0", "C 이전 HOLD"),
        _hold_row("HOLD-C", "RG", "D/S1", "2026-07-30 05:00:00", "HC1", "C 현재 HOLD"),
        _hold_row("L1001", "MOBILE_A", "W/B1", "2026-07-28 03:00:00", "L1", "L1001 첫 HOLD"),
        _hold_row("L1001", "MOBILE_A", "W/B1", "2026-07-29 09:30:00", "L2", "L1001 재 HOLD"),
        _hold_row("L1001", "MOBILE_A", "W/B1", "2026-07-30 08:20:00", "L3", "L1001 최신 HOLD"),
    ]


def _production_row(
    work_date: str,
    product_key: str,
    process: str,
    base_quantity: int | float,
    *,
    shift: str = "1",
    quantity: int | float | None | object = ...,
) -> dict[str, Any]:
    row = _product_process_row(work_date, PRODUCTS[product_key], process, shift=shift)
    row["PRODUCTION"] = base_quantity if quantity is ... else quantity
    return row


def _wip_row(work_date: str, product_key: str, process: str, quantity: int | float, lot_id: str) -> dict[str, Any]:
    row = _product_process_row(work_date, PRODUCTS[product_key], process)
    row["WIP"] = quantity
    return row


def _product_process_row(work_date: str, product: dict[str, str], process: str, *, shift: str = "1") -> dict[str, Any]:
    oper, sequence = PROCESSES[process]
    return {
        "WORK_DATE": work_date,
        "SHIFT": shift,
        "FACTORY": "PNT",
        "FAB": "PKG",
        "FAMILY": product["FAMILY"],
        "MODE": product["MODE"],
        "DENSITY": product["DENSITY"],
        "TECH": product["TECH"],
        "ORG": product["ORG"],
        "PKG1": product["PKG1"],
        "PKG2": product["PKG2"],
        "LEAD": product["LEAD"],
        "MCP_NO": product["MCP_NO"],
        "TSV_DIE_TYP": product["TSV_DIE_TYP"],
        "DEVICE": product["DEVICE"],
        "DEVICE_DESC": product["DEVICE_DESC"],
        "DIE_ATTACH_QTY": 1,
        "NETDIE_300_CNT": 100,
        "OPER": oper,
        "OPER_NAME": process,
        "OPER_SEQ": sequence,
    }


def _equipment_row(product: dict[str, str], process: str, model: str, recipe: str, equipment_id: str) -> dict[str, Any]:
    oper, _ = PROCESSES[process]
    return {
        "BAY_ID": "BAY-01",
        "EQUIP_ID": equipment_id,
        "EQUIP_MODEL": model,
        "PRESS_CNT": 2,
        "OPER": oper,
        "OPER_NM": process,
        "MODE": product["MODE"],
        "DENSITY": product["DENSITY"],
        "TECH": product["TECH"],
        "PKG1": product["PKG1"],
        "PKG2": product["PKG2"],
        "LEAD": product["LEAD"],
        "ORG": product["ORG"],
        "MCP_NO": product["MCP_NO"],
        "DEVICE": product["DEVICE"],
        "DEVICE_DESC": product["DEVICE_DESC"],
        "LOT_ID": "",
        "RECIPE_ID": recipe,
    }


def _lot_row(
    lot_id: str,
    product_key: str,
    process: str,
    hold_stat: str,
    prod_qty: int,
    wf_qty: int,
    in_tat: float,
    cum_tat: float,
    hold_reason: str,
    oper_in_at: str,
) -> dict[str, Any]:
    product = PRODUCTS[product_key]
    oper, oper_seq = PROCESSES[process]
    return {
        "FAB": "PKG",
        "FAMILY": product["FAMILY"],
        "MODE": product["MODE"],
        "DENSITY": product["DENSITY"],
        "TECH": product["TECH"],
        "ORG": product["ORG"],
        "PKG1": product["PKG1"],
        "PKG2": product["PKG2"],
        "LEAD": product["LEAD"],
        "MCP_NO": product["MCP_NO"],
        "TSV_DIE_TYPE": product["TSV_DIE_TYP"],
        "DEVICE": product["DEVICE"],
        "DEVICE_DESC": product["DEVICE_DESC"],
        "OPER": oper,
        "OPER_NAME": process,
        "OPER_SEQ": oper_seq,
        "LOT_ID": lot_id,
        "PROD_QTY": prod_qty,
        "WF_QTY": wf_qty,
        "IN_TAT": in_tat,
        "CUM_TAT": cum_tat,
        "HOLD_STAT": hold_stat,
        "HOLD_REASON": hold_reason,
        "LOT_STAT": "WAITING" if hold_stat == "OnHold" else "RUNNING",
        "OPER_IN_TM": oper_in_at,
        "FAC_IN_TIME": "2026-07-30 00:00:00",
        "EQP_ID": "EQP-LOT-1",
    }


def _hold_row(lot_id: str, product_key: str, process: str, timestamp: str, code: str, description: str) -> dict[str, Any]:
    product = PRODUCTS[product_key]
    oper, _ = PROCESSES[process]
    return {
        "LOT_ID": lot_id,
        "PROD_QTY": 100,
        "OPER": oper,
        "OPER_NAME": process,
        "HOLD_TM": timestamp,
        "HOLD_CD": code,
        "HOLD_DESC": description,
        "FAMILY": product["FAMILY"],
        "MODE": product["MODE"],
        "DENSITY": product["DENSITY"],
        "TECH": product["TECH"],
        "ORG": product["ORG"],
        "PKG1": product["PKG1"],
        "PKG2": product["PKG2"],
        "LEAD": product["LEAD"],
        "MCP_NO": product["MCP_NO"],
        "DEVICE": product["DEVICE"],
        "DEVICE_DESC": product["DEVICE_DESC"],
    }


def _comparison_rows(work_date: str) -> list[dict[str, Any]]:
    base = _product("CMP", "DDR4", "16G", "CMP", "FBGA", "SDP", "64", "", "DEV-COMPARE-BASE")
    variants = [
        base,
        {**base, "MODE": "DDR5", "DEVICE": "DEV-COMPARE-MODE"},
        {**base, "PKG1": "VFBGA", "DEVICE": "DEV-COMPARE-PKG1"},
        {**base, "LEAD": "78", "DEVICE": "DEV-COMPARE-LEAD"},
    ]
    rows = []
    for product in variants:
        row = _product_process_row(work_date, product, "D/A1")
        row["PRODUCTION"] = 10
        rows.append(row)
    return rows


def _physical_schema(rows: list[dict[str, Any]]) -> list[str]:
    return sorted(set().union(*(set(row) for row in rows))) if rows else []


def _params_match(row: dict[str, Any], params: dict[str, Any]) -> bool:
    for field, value in params.items():
        if field not in row:
            continue
        actual = row[field]
        if field == "DATE":
            try:
                desired = _date_value(value)
                current = _date_value(actual)
            except ValueError:
                return False
            if current != desired:
                return False
        elif isinstance(value, list):
            if actual not in value:
                return False
        elif actual != value:
            return False
    return True


def _filters_match(row: dict[str, Any], filters: Any) -> bool:
    if filters is None or filters == {} or filters == []:
        return True
    if isinstance(filters, list):
        return all(_filters_match(row, item) for item in filters)
    if not isinstance(filters, dict):
        return False
    connective = str(filters.get("op") or "").lower()
    if connective in {"all", "any"}:
        clauses = filters.get("clauses") if isinstance(filters.get("clauses"), list) else []
        values = [_filters_match(row, clause) for clause in clauses]
        return all(values) if connective == "all" else any(values)
    if "field" in filters:
        return _condition(row.get(str(filters["field"])), filters)
    return all(_condition(row.get(field), condition if isinstance(condition, dict) else {"operator": "eq", "value": condition}) for field, condition in filters.items())


def _condition(actual: Any, condition: dict[str, Any]) -> bool:
    operator = str(condition.get("operator") or condition.get("op") or "eq").lower()
    operator = {"ge": "gte", "le": "lte"}.get(operator, operator)
    value = condition.get("value")
    values = (
        condition.get("values")
        if isinstance(condition.get("values"), list)
        else value
        if isinstance(value, list)
        else []
    )
    if operator == "eq":
        return actual == value
    if operator == "ne":
        return actual != value
    if operator == "in":
        return actual in values
    if operator == "not_in":
        return actual not in values
    if operator == "starts_with":
        return str(actual or "").startswith(str(value))
    if operator == "ends_with":
        return str(actual or "").endswith(str(value))
    if operator == "contains":
        return str(value) in str(actual or "")
    if operator in {"is_null", "is_blank", "null_or_blank"}:
        return actual is None or str(actual).strip() == ""
    if operator == "is_not_null":
        return actual is not None
    if operator == "is_not_blank":
        return actual is not None and str(actual).strip() != ""
    try:
        left, right = float(actual), float(value)
    except (TypeError, ValueError):
        left, right = str(actual), str(value)
    if operator == "gt":
        return left > right
    if operator == "gte":
        return left >= right
    if operator == "lt":
        return left < right
    if operator == "lte":
        return left <= right
    if operator == "between":
        pair = values or (value if isinstance(value, list) else [])
        return len(pair) == 2 and pair[0] <= actual <= pair[1]
    return False


def _date_value(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if len(text) == 8 and text.isdigit():
        return datetime.strptime(text, "%Y%m%d").date()
    if "T" in text:
        return datetime.fromisoformat(text).date()
    return date.fromisoformat(text)
