"""Registry-driven compiler for ``metadata.runtime.catalog.v2``.

This module is the deterministic v2 planning boundary.  It resolves datasets
from metric source bindings and field ownership, connects them only through
registered relations, applies registered grains/recipes, expands formula
dependencies, and emits typed executor operations.  Domain identifiers never
appear in the implementation.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Iterable, Mapping

from .canonical import ContractError, sha256_json
from .generic_v2_candidates import validate_generic_v2_candidate_bundle
from .registered_functions import (
    build_registered_call_operation,
    validate_registered_call_operation,
    validate_registered_function_card,
)


SUPPORTED_OPERATORS = {
    "filter",
    "project",
    "aggregate",
    "join",
    "derive",
    "compare_fields",
    "sort",
    "rank",
    "transform_previous_result",
    "registered_call",
}
SUPPORTED_AGGREGATIONS = {"sum", "mean", "min", "max", "count", "nunique", "median", "std", "var"}


def compile_generic_v2_plan(
    intent: dict[str, Any],
    bundle: dict[str, Any],
    catalog: dict[str, Any],
    *,
    prior_result: dict[str, Any] | None = None,
    question: str = "",
) -> dict[str, Any]:
    """Compile a closed semantic intent into one immutable typed plan."""

    _validate_compile_dependencies(intent, bundle, catalog)
    semantics = intent.get("semantics") if isinstance(intent.get("semantics"), dict) else {}
    prior = deepcopy(prior_result) if isinstance(prior_result, dict) else {}
    if prior.get("rows") and bool(semantics.get("followup") or semantics.get("followup_mode") == "referenced"):
        return _compile_previous(intent, bundle, catalog, semantics, prior, question)

    recipe = _select_recipe(catalog, semantics, question)
    template = recipe.get("default_operation_template") if isinstance(recipe.get("default_operation_template"), dict) else {}
    registered_card = _selected_registered_function(catalog, semantics)
    requested_metrics = _stable(semantics.get("metric_refs") or [])
    if not requested_metrics and semantics.get("recipe_refs"):
        requested_metrics = _stable(_template_values(template, "metrics") + _template_values(template, "metric"))
    metric_order = _metric_closure(catalog, requested_metrics)
    requested_dimensions = _stable(semantics.get("dimension_refs") or [])
    explicit_fields = _stable(semantics.get("field_refs") or [])
    if str(semantics.get("analysis_kind") or "") not in {"projection", "detail"}:
        explicit_fields = [field for field in explicit_fields if field not in catalog.get("metrics", {})]
    visible_requested_fields = _stable([*requested_dimensions, *explicit_fields])
    registered_required_fields = _stable((registered_card or {}).get("required_fields") or [])
    requested_fields = _stable([*visible_requested_fields, *registered_required_fields])
    grain_fields = _grain_fields(catalog, semantics, template, requested_dimensions)

    if not metric_order:
        return _compile_projection(
            intent,
            bundle,
            catalog,
            semantics,
            visible_requested_fields,
            question,
            source_fields=requested_fields,
            registered_card=registered_card,
        )
    base_metrics = [metric_id for metric_id in metric_order if _metric_binding(catalog, metric_id, required=False)]
    if not base_metrics:
        _fail("No registered source-bound metric is available for the requested formula closure.")

    selected_datasets = _stable(semantics.get("dataset_refs") or [])
    metric_datasets = _stable(
        _metric_dataset(catalog, metric_id, selected_datasets=selected_datasets)
        for metric_id in base_metrics
    )
    relation_preferences = _stable(_template_values(template, "relation_id"))
    anchor = _anchor_dataset(catalog, metric_datasets, relation_preferences)
    field_owners = {
        field: _field_owner(catalog, field, anchor=anchor, preferred=metric_datasets)
        for field in requested_fields
        if field in catalog.get("fields", {})
    }
    required_datasets = set(metric_datasets) | set(field_owners.values())
    relation_steps, connected_datasets = _relation_steps(
        catalog,
        anchor,
        required_datasets,
        grain_fields,
        relation_preferences,
    )
    dataset_order = [anchor, *[step[2] for step in relation_steps]]
    date_dataset = _date_filter_dataset(catalog, dataset_order, anchor, semantics)
    jobs = [_job(catalog, dataset_key, index) for index, dataset_key in enumerate(_stable(dataset_order), start=1)]
    source_refs = {job["dataset_key"]: f"source:{job['job_id']}" for job in jobs}
    operations: list[dict[str, Any]] = []
    states = {
        dataset_key: _source_state(
            catalog,
            dataset_key,
            source_refs[dataset_key],
            base_metrics,
            semantics,
            operations,
            apply_date=dataset_key == date_dataset,
        )
        for dataset_key in _stable(dataset_order)
    }

    state = states[anchor]
    joined = {anchor}
    optional_metrics: set[str] = set()
    for relation_id, current_dataset, new_dataset in relation_steps:
        relation = deepcopy((catalog.get("relations") or {}).get(relation_id) or {})
        forward = relation.get("left_dataset") == current_dataset and relation.get("right_dataset") == new_dataset
        if not forward and not (
            relation.get("right_dataset") == current_dataset and relation.get("left_dataset") == new_dataset
        ):
            _fail("Registered relation path is inconsistent.", {"relation_id": relation_id})
        left_keys = _stable(relation.get("left_keys") if forward else relation.get("right_keys"))
        right_keys = _stable(relation.get("right_keys") if forward else relation.get("left_keys"))
        right_state = states[new_dataset]

        # Coarsen the accumulated side before a relation at the requested grain.
        # Fine-grain relations are deliberately scheduled first by _relation_steps.
        if grain_fields and set(left_keys) <= set(grain_fields) and set(grain_fields) <= state["available"]:
            state = _aggregate_state(state, grain_fields, operations, catalog, label="left_grain")

        source_cardinality = str(relation.get("cardinality") or "many_to_many")
        if not forward:
            source_cardinality = _reverse_cardinality(source_cardinality)
        aggregate_right = str(relation.get("multi_match_policy") or "") == "aggregate_right_first"
        if source_cardinality in {"one_to_many", "many_to_many"} and not aggregate_right:
            _fail(
                "A multi-match metric relation requires multi_match_policy=aggregate_right_first.",
                {"relation_id": relation_id, "cardinality": source_cardinality},
            )
        if aggregate_right:
            if not right_state["metric_fields"]:
                _fail(
                    "A multi-match relation requires registered right-side metrics for deterministic pre-aggregation.",
                    {"relation_id": relation_id},
                )
            right_state = _aggregate_state(right_state, right_keys, operations, catalog, label="right_relation")
            join_cardinality = "many_to_one"
        else:
            right_state = _project_join_side(
                right_state,
                right_keys,
                requested_fields,
                operations,
                label="right_projection",
            )
            join_cardinality = _execution_cardinality(source_cardinality)

        operation_id = _next_id(operations, "join")
        operations.append(
            {
                "id": operation_id,
                "op": "join",
                "left": state["input"],
                "right": right_state["input"],
                "relation_id": relation_id,
                "relation_direction": "forward" if forward else "reverse",
                "how": str(relation.get("join_type") or "left") if forward else "left",
                "key_mappings": [
                    {"left": left_key, "right": right_key}
                    for left_key, right_key in zip(left_keys, right_keys, strict=True)
                ],
                "cardinality": join_cardinality,
                "registered_cardinality": source_cardinality,
                "null_key_policy": str(relation.get("null_key_policy") or "never_match"),
                "empty_side_policy": "allow",
            }
        )
        state = {
            "input": operation_id,
            "available": state["available"] | right_state["available"],
            "metric_fields": {**state["metric_fields"], **right_state["metric_fields"]},
            "grain": list(state.get("grain") or []),
            "aggregated": bool(state.get("aggregated")),
            "datasets": joined | {new_dataset},
        }
        optional_metrics.update(right_state["metric_fields"])
        joined.add(new_dataset)

    if joined != connected_datasets:
        _fail("The registered relation closure was not fully materialized.")

    if registered_card is not None:
        state = _apply_registered_function(state, registered_card, operations)

    final_groups = [field for field in grain_fields if field in state["available"]]
    if requested_dimensions:
        final_groups = [field for field in requested_dimensions if field in state["available"]]
    if final_groups or not state.get("grain"):
        state = _aggregate_state(state, final_groups, operations, catalog, label="result_grain")

    for metric_id in metric_order:
        if metric_id in optional_metrics and metric_id in state["metric_fields"]:
            state = _coalesce_metric(state, metric_id, operations)
        metric = (catalog.get("metrics") or {}).get(metric_id) or {}
        if isinstance(metric.get("formula"), dict):
            state = _derive_metric(state, metric_id, metric, operations)

    state = _apply_compare(state, catalog, semantics, template, requested_metrics, operations)
    state = _apply_sort(state, catalog, semantics, template, requested_metrics, operations)
    state = _apply_rank(state, catalog, semantics, template, requested_metrics, final_groups, operations)

    visible_fields = [field for field in explicit_fields if field in state["available"]]
    if not visible_fields:
        visible_fields = [field for field in requested_dimensions if field in state["available"]]
    columns = _stable(
        [
            *visible_fields,
            *[metric for metric in requested_metrics if metric in state["available"]],
        ]
    )
    if not columns:
        columns = _stable([*final_groups, *[metric for metric in requested_metrics if metric in state["available"]]])
    if not columns:
        _fail("The requested result has no registered output fields.")
    project_id = _next_id(operations, "project")
    operations.append({"id": project_id, "op": "project", "input": state["input"], "fields": columns})
    jobs = _seal_retrieval_jobs(
        catalog,
        jobs,
        semantics=semantics,
        base_metrics=base_metrics,
        requested_fields=requested_fields,
        grain_fields=grain_fields,
        relation_steps=relation_steps,
        date_dataset=date_dataset,
    )
    return _finalize(
        intent,
        bundle,
        catalog,
        jobs,
        operations,
        project_id,
        columns,
        [field for field in final_groups if field in columns],
    )


def validate_generic_v2_plan(plan: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    """Validate source, relation, reference and formula registry closure."""

    _validate_catalog_pin(catalog)
    _validate_plan_hashes(plan)
    if str(plan.get("catalog_sha256") or "") != str(catalog.get("catalog_sha256") or ""):
        _fail("Plan catalog pin does not match the supplied runtime catalog.")

    datasets = set(catalog.get("datasets") or {})
    relations = catalog.get("relations") if isinstance(catalog.get("relations"), dict) else {}
    metrics = catalog.get("metrics") if isinstance(catalog.get("metrics"), dict) else {}
    aliases: set[str] = set()
    for job in plan.get("retrieval_jobs", []):
        dataset_key = str(job.get("dataset_key") or "")
        job_id = str(job.get("job_id") or "")
        if dataset_key not in datasets or not job_id or job_id in aliases:
            _fail("Retrieval job escapes the dataset registry.", {"dataset_key": dataset_key})
        aliases.add(job_id)
        dataset = (catalog.get("datasets") or {}).get(dataset_key) or {}
        registered_fields = set(dataset.get("fields") or {})
        required_fields = set(map(str, job.get("required_fields") or []))
        if not required_fields or not required_fields <= registered_fields:
            _fail(
                "Retrieval job field closure differs from the selected dataset registry.",
                {"dataset_key": dataset_key, "missing": sorted(required_fields - registered_fields)},
            )
        parameter_specs = dataset.get("parameters") if isinstance(dataset.get("parameters"), dict) else {}
        parameters = job.get("parameters") if isinstance(job.get("parameters"), dict) else {}
        if not set(parameters) <= set(parameter_specs):
            _fail("Retrieval job contains an unregistered parameter.", {"dataset_key": dataset_key})
        filter_fields = set(_filter_tree_fields(job.get("filters")))
        if not filter_fields <= required_fields:
            _fail(
                "Retrieval pushdown filter is outside the sealed field closure.",
                {"dataset_key": dataset_key, "fields": sorted(filter_fields - required_fields)},
            )
    known = {f"source:{alias}" for alias in aliases} | ({"source:previous"} if "previous" in (plan.get("input_refs") or []) else set())
    for operation in plan.get("operations", []):
        operator = str(operation.get("op") or "")
        operation_id = str(operation.get("id") or "")
        if operator not in SUPPORTED_OPERATORS or not operation_id or operation_id in known:
            _fail("Plan contains an unregistered typed operation.", {"operator": operator})
        for ref in (operation.get("input"), operation.get("left"), operation.get("right")):
            if ref and str(ref) not in known:
                _fail("Operation input reference is not closed.", {"input": ref})
        if operator == "join":
            relation_id = str(operation.get("relation_id") or "")
            relation = relations.get(relation_id)
            if not isinstance(relation, dict):
                _fail("Join does not reference a registered relation.", {"relation_id": relation_id})
            direction = str(operation.get("relation_direction") or "forward")
            mappings = operation.get("key_mappings") if isinstance(operation.get("key_mappings"), list) else []
            actual_left = [str(item.get("left") or "") for item in mappings if isinstance(item, dict)]
            actual_right = [str(item.get("right") or "") for item in mappings if isinstance(item, dict)]
            forward_keys = (_stable(relation.get("left_keys") or []), _stable(relation.get("right_keys") or []))
            reverse_keys = (forward_keys[1], forward_keys[0])
            expected_pairs = [forward_keys] if direction == "forward" else [reverse_keys] if direction == "reverse" else [forward_keys, reverse_keys]
            if (actual_left, actual_right) not in expected_pairs:
                _fail("Join keys differ from the registered relation.", {"relation_id": relation_id})
            actual_cardinality = str(operation.get("cardinality") or "")
            registered = str(operation.get("registered_cardinality") or "")
            expected_cardinalities = {
                str(relation.get("cardinality") or "")
            } if direction == "forward" else {
                _reverse_cardinality(str(relation.get("cardinality") or ""))
            } if direction == "reverse" else {
                str(relation.get("cardinality") or ""),
                _reverse_cardinality(str(relation.get("cardinality") or "")),
            }
            if registered not in expected_cardinalities:
                _fail("Join cardinality registry pin changed.", {"relation_id": relation_id})
            if actual_cardinality != _execution_cardinality(registered) and not (
                actual_cardinality == "many_to_one" and str(relation.get("multi_match_policy") or "") == "aggregate_right_first"
            ):
                _fail("Join cardinality override is not registry-authorized.", {"relation_id": relation_id})
        if operator == "derive":
            output = str(operation.get("output_field") or "")
            if output not in metrics and not output.startswith("__normalized_"):
                _fail("Derived field is not a registered metric.", {"field": output})
        if operator == "compare_fields" and str(operation.get("operator") or "") not in {"eq", "ne", "gt", "gte", "lt", "lte"}:
            _fail("Field comparison operator is not supported by the typed contract.")
        if operator == "registered_call":
            function_ref = operation.get("function_ref") if isinstance(operation.get("function_ref"), dict) else {}
            raw_version = function_ref.get("version")
            if isinstance(raw_version, bool) or not isinstance(raw_version, int) or raw_version < 1:
                _fail("Registered call function version is invalid.")
            card = _registered_function_card(
                catalog,
                str(function_ref.get("function_id") or ""),
                raw_version,
            )
            try:
                validate_registered_call_operation(operation, catalog_card=card)
            except ContractError as exc:
                _fail(
                    "Registered call is not closed against the catalog and local allowlist.",
                    {"reason": str(exc), "function_id": function_ref.get("function_id")},
                )
            required = set(map(str, operation.get("required_fields") or []))
            if not required <= set(catalog.get("fields") or {}):
                _fail(
                    "Registered call requires an unregistered field.",
                    {"missing": sorted(required - set(catalog.get("fields") or {}))},
                )
            dataset_ref = str((card.get("call_template") or {}).get("dataset_ref") or "")
            bound_jobs = [
                job
                for job in plan.get("retrieval_jobs") or []
                if isinstance(job, dict) and str(job.get("dataset_key") or "") == dataset_ref
            ]
            if not bound_jobs and "previous" not in (plan.get("input_refs") or []):
                _fail(
                    "Registered call dataset binding is absent from the retrieval plan.",
                    {"dataset_ref": dataset_ref},
                )
            if bound_jobs and not any(
                required <= set(map(str, job.get("required_fields") or [])) for job in bound_jobs
            ):
                _fail(
                    "Registered call fields are absent from its bound retrieval job.",
                    {"dataset_ref": dataset_ref, "required_fields": sorted(required)},
                )
        known.add(operation_id)
    if plan.get("result_operation_id") not in known:
        _fail("Result operation reference is not closed.")
    return plan


def _validate_compile_dependencies(
    intent: dict[str, Any],
    bundle: dict[str, Any],
    catalog: dict[str, Any],
) -> None:
    """Verify every upstream pin before producing executable IR."""

    _validate_catalog_pin(catalog)
    validate_generic_v2_candidate_bundle(bundle, catalog=catalog)
    expected_keys = {
        "contract_version",
        "request_id",
        "candidate_bundle_sha256",
        "intent_candidate_id",
        "semantics",
        "route",
        "intent_generator",
        "intent_sha256",
    }
    if not isinstance(intent, dict) or set(intent) != expected_keys:
        _fail("Intent shape differs from the closed analysis.intent.v1 contract.")
    if intent.get("contract_version") != "analysis.intent.v1":
        _fail("analysis.intent.v1 is required for generic v2 compilation.")
    if intent.get("candidate_bundle_sha256") != bundle.get("bundle_sha256"):
        _fail("Intent references a different candidate bundle.")
    if intent.get("request_id") != bundle.get("request_id"):
        _fail("Intent and candidate bundle request identities differ.")
    if intent.get("route") != (bundle.get("route_decision") or {}).get("route"):
        _fail("Intent route differs from the sealed route decision.")
    material = {key: deepcopy(value) for key, value in intent.items() if key != "intent_sha256"}
    if intent.get("intent_sha256") != sha256_json(material):
        _fail("Intent hash does not match its semantic material.")
    selected = next(
        (
            candidate
            for candidate in bundle.get("intent_candidates") or []
            if isinstance(candidate, dict) and candidate.get("candidate_id") == intent.get("intent_candidate_id")
        ),
        None,
    )
    if not isinstance(selected, dict) or selected.get("semantics") != intent.get("semantics"):
        _fail("Intent semantics are not the selected sealed candidate semantics.")


def _validate_catalog_pin(catalog: dict[str, Any]) -> None:
    if not isinstance(catalog, dict) or catalog.get("contract_version") != "metadata.runtime.catalog.v2":
        _fail("A metadata.runtime.catalog.v2 catalog is required.")
    expected = sha256_json({key: value for key, value in catalog.items() if key != "catalog_sha256"})
    if str(catalog.get("catalog_sha256") or "") != expected:
        _fail("Runtime catalog hash does not match its compiled material.")


def _validate_plan_hashes(plan: dict[str, Any]) -> None:
    if not isinstance(plan, dict) or plan.get("contract_version") != "analysis.plan.v1":
        _fail("analysis.plan.v1 is required.")
    material = {key: deepcopy(value) for key, value in plan.items() if key not in {"plan_id", "plan_fingerprint"}}
    jobs = material.get("retrieval_jobs") if isinstance(material.get("retrieval_jobs"), list) else []
    material["retrieval_jobs"] = sorted(jobs, key=lambda item: str(item.get("job_id") or ""))
    expected_id = f"plan:{sha256_json(material)}"
    semantic = {
        key: material[key]
        for key in (
            "catalog_sha256",
            "input_refs",
            "retrieval_jobs",
            "operations",
            "result_operation_id",
            "result_contract",
            "lineage",
        )
        if key in material
    }
    if plan.get("plan_id") != expected_id or plan.get("plan_fingerprint") != sha256_json(semantic):
        _fail("Plan identity or semantic fingerprint does not match its executable material.")


def _filter_tree_fields(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return []
    if value.get("op") in {"all", "any"}:
        return _stable(
            field
            for clause in value.get("clauses") or []
            for field in _filter_tree_fields(clause)
        )
    field = str(value.get("field") or "")
    return [field] if field else []


def _compile_projection(
    intent: dict[str, Any],
    bundle: dict[str, Any],
    catalog: dict[str, Any],
    semantics: dict[str, Any],
    requested_fields: list[str],
    question: str,
    *,
    source_fields: list[str] | None = None,
    registered_card: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not requested_fields:
        _fail("Projection requires registered fields.")
    retrieval_fields = _stable(source_fields or requested_fields)
    dataset_refs = [str(item) for item in semantics.get("dataset_refs") or [] if str(item) in catalog.get("datasets", {})]
    recipe = _select_recipe(catalog, semantics, question)
    template = recipe.get("default_operation_template") if isinstance(recipe.get("default_operation_template"), dict) else {}
    preferences = _stable(semantics.get("relation_refs") or _template_values(template, "relation_id"))
    owners = [_field_owner(catalog, field, anchor=dataset_refs[0] if dataset_refs else "", preferred=dataset_refs) for field in retrieval_fields]
    anchor = dataset_refs[0] if dataset_refs else (
        str(((catalog.get("relations") or {}).get(preferences[0]) or {}).get("left_dataset") or "")
        if preferences
        else owners[0]
    )
    if anchor not in catalog.get("datasets", {}):
        _fail("Projection anchor dataset is not registered.")
    if len(set(owners)) > 1 and not preferences:
        _fail("Cross-dataset detail projection requires a registered recipe relation.")
    relation_steps, _ = _relation_steps(catalog, anchor, set(owners), [], preferences)
    dataset_order = [anchor, *[step[2] for step in relation_steps]]
    date_dataset = _date_filter_dataset(catalog, dataset_order, anchor, semantics)
    jobs = [_job(catalog, dataset_key, index) for index, dataset_key in enumerate(_stable(dataset_order), start=1)]
    operations: list[dict[str, Any]] = []
    refs = {job["dataset_key"]: f"source:{job['job_id']}" for job in jobs}
    states = {
        dataset_key: _source_state(
            catalog,
            dataset_key,
            refs[dataset_key],
            [],
            semantics,
            operations,
            apply_date=dataset_key == date_dataset,
        )
        for dataset_key in _stable(dataset_order)
    }
    state = states[anchor]
    for relation_id, current_dataset, new_dataset in relation_steps:
        relation = deepcopy((catalog.get("relations") or {}).get(relation_id) or {})
        forward = relation.get("left_dataset") == current_dataset and relation.get("right_dataset") == new_dataset
        left_keys = _stable(relation.get("left_keys") if forward else relation.get("right_keys"))
        right_keys = _stable(relation.get("right_keys") if forward else relation.get("left_keys"))
        right = _project_join_side(states[new_dataset], right_keys, retrieval_fields, operations, label="projection_join_side")
        cardinality = str(relation.get("cardinality") or "many_to_many")
        cardinality = cardinality if forward else _reverse_cardinality(cardinality)
        operation_id = _next_id(operations, "join")
        operations.append(
            {
                "id": operation_id,
                "op": "join",
                "left": state["input"],
                "right": right["input"],
                "relation_id": relation_id,
                "relation_direction": "forward" if forward else "reverse",
                "how": str(relation.get("join_type") or "left") if forward else "left",
                "key_mappings": [
                    {"left": left_key, "right": right_key}
                    for left_key, right_key in zip(left_keys, right_keys, strict=True)
                ],
                "cardinality": _execution_cardinality(cardinality),
                "registered_cardinality": cardinality,
                "null_key_policy": str(relation.get("null_key_policy") or "never_match"),
                "empty_side_policy": "allow",
            }
        )
        state = {
            **state,
            "input": operation_id,
            "available": set(state["available"]) | set(right["available"]),
            "datasets": set(state.get("datasets") or set()) | {new_dataset},
        }
    if registered_card is not None:
        state = _apply_registered_function(state, registered_card, operations)
    fields = [field for field in requested_fields if field in state["available"]]
    if not fields:
        _fail("Projection result has no registered output fields.")
    operation_id = _next_id(operations, "project")
    operations.append({"id": operation_id, "op": "project", "input": state["input"], "fields": fields})
    jobs = _seal_retrieval_jobs(
        catalog,
        jobs,
        semantics=semantics,
        base_metrics=[],
        requested_fields=retrieval_fields,
        grain_fields=[],
        relation_steps=relation_steps,
        date_dataset=date_dataset,
    )
    return _finalize(intent, bundle, catalog, jobs, operations, operation_id, fields, [])


def _compile_previous(
    intent: dict[str, Any],
    bundle: dict[str, Any],
    catalog: dict[str, Any],
    semantics: dict[str, Any],
    prior: dict[str, Any],
    question: str,
) -> dict[str, Any]:
    columns = _stable(prior.get("columns") or [])
    requested_metrics = _stable(semantics.get("metric_refs") or [])
    requested_dimensions = _stable(semantics.get("dimension_refs") or [])
    explicit_fields = _stable(semantics.get("field_refs") or [])
    if str(semantics.get("analysis_kind") or "") not in {"projection", "detail"}:
        explicit_fields = [field for field in explicit_fields if field not in catalog.get("metrics", {})]
    requested_fields = _stable([*requested_dimensions, *explicit_fields])
    registered_card = _selected_registered_function(catalog, semantics)
    registered_required_fields = _stable((registered_card or {}).get("required_fields") or [])
    source_fields = _stable([*requested_fields, *registered_required_fields])
    operations: list[dict[str, Any]] = [
        {"id": "op_01_previous", "op": "transform_previous_result", "input": "source:previous"}
    ]
    state = {
        "input": "op_01_previous",
        "available": set(columns),
        "metric_fields": {metric: metric for metric in requested_metrics if metric in columns},
        "grain": [field for field in requested_dimensions if field in columns],
        "aggregated": True,
        "datasets": set(),
    }
    jobs: list[dict[str, Any]] = []

    missing_fields = [field for field in source_fields if field not in state["available"]]
    if missing_fields:
        owner = _field_owner(catalog, missing_fields[0], anchor="", preferred=[])
        relation_id, previous_keys, owner_keys = _relation_for_previous(catalog, state["available"], owner)
        jobs = [_job(catalog, owner, 1)]
        right = _source_state(
            catalog,
            owner,
            f"source:{jobs[0]['job_id']}",
            [],
            semantics,
            operations,
            apply_date=True,
        )
        right = _project_join_side(right, owner_keys, missing_fields, operations, label="previous_enrichment")
        relation = (catalog.get("relations") or {})[relation_id]
        operation_id = _next_id(operations, "join")
        operations.append(
            {
                "id": operation_id,
                "op": "join",
                "left": state["input"],
                "right": right["input"],
                "relation_id": relation_id,
                "relation_direction": "previous",
                "how": "left",
                "key_mappings": [
                    {"left": left_key, "right": right_key}
                    for left_key, right_key in zip(previous_keys, owner_keys, strict=True)
                ],
                "cardinality": "many_to_one",
                "registered_cardinality": str(relation.get("cardinality") or "many_to_one"),
                "null_key_policy": str(relation.get("null_key_policy") or "never_match"),
                "empty_side_policy": "allow",
            }
        )
        state["input"] = operation_id
        state["available"].update(right["available"])

    if registered_card is not None:
        state = _apply_registered_function(state, registered_card, operations)

    groups = [field for field in requested_dimensions if field in state["available"]]
    if groups and groups != state.get("grain"):
        state = _aggregate_state(state, groups, operations, catalog, label="previous_regroup")
    recipe = _select_recipe(catalog, semantics, question)
    template = recipe.get("default_operation_template") if isinstance(recipe.get("default_operation_template"), dict) else {}
    state = _apply_rank(state, catalog, semantics, template, requested_metrics, groups, operations)
    visible_fields = [field for field in explicit_fields if field in state["available"]]
    if not visible_fields:
        visible_fields = [field for field in requested_dimensions if field in state["available"]]
    output = _stable(
        [
            *visible_fields,
            *[metric for metric in requested_metrics if metric in state["available"]],
        ]
    ) or [field for field in columns if field in state["available"]]
    project_id = _next_id(operations, "project")
    operations.append({"id": project_id, "op": "project", "input": state["input"], "fields": output})
    if jobs:
        jobs = _seal_retrieval_jobs(
            catalog,
            jobs,
            semantics=semantics,
            base_metrics=[],
            requested_fields=missing_fields,
            grain_fields=[],
            relation_steps=[],
            date_dataset=str(jobs[0]["dataset_key"]),
            extra_fields={str(jobs[0]["dataset_key"]): owner_keys},
        )
    return _finalize(intent, bundle, catalog, jobs, operations, project_id, output, groups, input_refs=["previous"])


def _source_state(
    catalog: dict[str, Any],
    dataset_key: str,
    input_ref: str,
    base_metrics: Iterable[str],
    semantics: dict[str, Any],
    operations: list[dict[str, Any]],
    *,
    apply_date: bool,
) -> dict[str, Any]:
    dataset = (catalog.get("datasets") or {}).get(dataset_key) or {}
    available = set(dataset.get("fields") or {})
    metric_fields: dict[str, str] = {}
    for metric_id in base_metrics:
        binding = _metric_binding(catalog, metric_id, required=False)
        if binding and _metric_dataset(
            catalog,
            metric_id,
            selected_datasets=semantics.get("dataset_refs") or [],
        ) == dataset_key:
            source_field = str(binding.get("field") or "")
            if source_field not in available:
                _fail("Metric source field is absent from its bound dataset.", {"metric_id": metric_id})
            metric_fields[metric_id] = source_field
    state = {
        "input": input_ref,
        "available": available,
        "metric_fields": metric_fields,
        "grain": [],
        "aggregated": False,
        "datasets": {dataset_key},
    }
    clauses, _parameters = _source_constraints(
        catalog,
        dataset_key,
        base_metrics,
        semantics,
        apply_date=apply_date,
    )
    if clauses:
        operation_id = _next_id(operations, "filter")
        tree = clauses[0] if len(clauses) == 1 else {"op": "all", "clauses": clauses}
        operations.append({"id": operation_id, "op": "filter", "input": state["input"], "where": tree})
        state["input"] = operation_id
    return state


def _source_constraints(
    catalog: dict[str, Any],
    dataset_key: str,
    base_metrics: Iterable[str],
    semantics: dict[str, Any],
    *,
    apply_date: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return the one sealed predicate tree input and source parameters.

    The same helper feeds both the retrieval job and the typed ``filter``
    operation.  Keeping the predicate in the executor makes connector
    pushdown an idempotent optimization rather than a correctness boundary.
    """

    dataset = (catalog.get("datasets") or {}).get(dataset_key) or {}
    available = set(dataset.get("fields") or {})
    clauses: list[dict[str, Any]] = []
    parameters: dict[str, Any] = {}

    if apply_date and bool(semantics.get("date_explicit")):
        value = str(semantics.get("date") or "")
        date_policy = dataset.get("date_policy") if isinstance(dataset.get("date_policy"), dict) else {}
        date_field = str(date_policy.get("field") or "")
        if date_field:
            if date_field not in available:
                _fail("Dataset date policy references an unavailable field.", {"dataset_key": dataset_key, "field": date_field})
            if str(date_policy.get("grain") or "") == "month":
                value = value[:7]
            clauses.append(
                {
                    "field": date_field,
                    "operator": "eq",
                    "value": value,
                    "semantic_type": _semantic_type(catalog, date_field),
                }
            )
        parameter_specs = dataset.get("parameters") if isinstance(dataset.get("parameters"), dict) else {}
        local_date_parameters = [
            str(name)
            for name, spec in parameter_specs.items()
            if isinstance(spec, dict) and str(spec.get("type") or "").casefold() in {"localdate", "date"}
        ]
        for name in sorted(local_date_parameters):
            parameters[name] = value

    for item in semantics.get("filter_refs") or []:
        if not isinstance(item, dict):
            continue
        field = str(item.get("field") or "")
        if field not in available:
            continue
        operator = str(item.get("operator") or "")
        if operator not in {"eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "starts_with", "contains"}:
            _fail("Filter literal uses an unsupported typed operator.", {"field": field, "operator": operator})
        clauses.append(
            {
                "field": field,
                "operator": operator,
                "value": deepcopy(item.get("value")),
                "semantic_type": _semantic_type(catalog, field),
            }
        )

    where = semantics.get("where") if isinstance(semantics.get("where"), dict) else None
    if where and str(where.get("field") or "") in available:
        clauses.append(deepcopy(where))

    metric_fields: dict[str, str] = {}
    for metric_id in base_metrics:
        binding = _metric_binding(catalog, str(metric_id), required=False)
        if not binding:
            continue
        if _metric_dataset(
            catalog,
            str(metric_id),
            selected_datasets=semantics.get("dataset_refs") or [],
        ) == dataset_key:
            metric_fields[str(metric_id)] = str(binding.get("field") or "")
    thresholds = semantics.get("thresholds") if isinstance(semantics.get("thresholds"), list) else []
    for threshold in thresholds:
        if not isinstance(threshold, dict):
            continue
        target = str(threshold.get("metric_ref") or threshold.get("field") or "")
        if target in metric_fields:
            source_field = metric_fields[target]
        elif target in available:
            source_field = target
        else:
            primary = next((str(item) for item in semantics.get("metric_refs") or [] if str(item) in metric_fields), "")
            if not primary:
                continue
            source_field = metric_fields[primary]
        clauses.append(
            {
                "field": source_field,
                "operator": str(threshold.get("operator") or "gt"),
                "value": deepcopy(threshold.get("value")),
                "semantic_type": _semantic_type(catalog, source_field),
            }
        )

    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for clause in clauses:
        marker = sha256_json(clause)
        if marker not in seen:
            seen.add(marker)
            unique.append(clause)
    return unique, parameters


def _seal_retrieval_jobs(
    catalog: dict[str, Any],
    jobs: list[dict[str, Any]],
    *,
    semantics: dict[str, Any],
    base_metrics: Iterable[str],
    requested_fields: Iterable[str],
    grain_fields: Iterable[str],
    relation_steps: Iterable[tuple[str, str, str]],
    date_dataset: str,
    extra_fields: Mapping[str, Iterable[str]] | None = None,
) -> list[dict[str, Any]]:
    """Seal minimum registered field closure and exact pushdown contracts."""

    selected = [str(job.get("dataset_key") or "") for job in jobs]
    selected_set = set(selected)
    for filter_ref in semantics.get("filter_refs") or []:
        if not isinstance(filter_ref, dict):
            continue
        field = str(filter_ref.get("field") or "")
        owners = {
            dataset_key
            for dataset_key in selected
            if field in (((catalog.get("datasets") or {}).get(dataset_key) or {}).get("fields") or {})
        }
        if not owners:
            _fail(
                "Filter field is absent from every selected dataset.",
                {"field": field, "selected_datasets": selected},
            )

    relation_fields: dict[str, set[str]] = {dataset_key: set() for dataset_key in selected}
    for relation_id, current_dataset, new_dataset in relation_steps:
        relation = (catalog.get("relations") or {}).get(relation_id) or {}
        forward = relation.get("left_dataset") == current_dataset and relation.get("right_dataset") == new_dataset
        if forward:
            relation_fields.setdefault(current_dataset, set()).update(_stable(relation.get("left_keys") or []))
            relation_fields.setdefault(new_dataset, set()).update(_stable(relation.get("right_keys") or []))
        else:
            relation_fields.setdefault(current_dataset, set()).update(_stable(relation.get("right_keys") or []))
            relation_fields.setdefault(new_dataset, set()).update(_stable(relation.get("left_keys") or []))

    base_metric_fields: dict[str, set[str]] = {dataset_key: set() for dataset_key in selected}
    for metric_id in base_metrics:
        binding = _metric_binding(catalog, str(metric_id), required=False)
        if not binding:
            continue
        owner = _metric_dataset(catalog, str(metric_id), selected_datasets=selected_set)
        if owner in base_metric_fields:
            base_metric_fields[owner].add(str(binding.get("field") or ""))

    requested = _stable([*requested_fields, *grain_fields])
    extras = extra_fields or {}
    sealed: list[dict[str, Any]] = []
    for job in jobs:
        dataset_key = str(job.get("dataset_key") or "")
        dataset = (catalog.get("datasets") or {}).get(dataset_key) or {}
        registered_fields = set(dataset.get("fields") or {})
        clauses, parameters = _source_constraints(
            catalog,
            dataset_key,
            base_metrics,
            semantics,
            apply_date=dataset_key == date_dataset,
        )
        required = set(base_metric_fields.get(dataset_key) or set())
        required.update(field for field in requested if field in registered_fields)
        required.update(relation_fields.get(dataset_key) or set())
        required.update(str(field) for field in extras.get(dataset_key, ()) if str(field))
        required.update(str(clause.get("field") or "") for clause in clauses)
        required.discard("")
        if not required <= registered_fields:
            _fail(
                "Retrieval field closure escapes the selected dataset registry.",
                {"dataset_key": dataset_key, "missing": sorted(required - registered_fields)},
            )
        if not required:
            _fail("Retrieval job has an empty registered field closure.", {"dataset_key": dataset_key})
        tree: dict[str, Any] | None = None
        if clauses:
            tree = clauses[0] if len(clauses) == 1 else {"op": "all", "clauses": clauses}
        sealed.append(
            {
                **deepcopy(job),
                "parameters": parameters,
                "required_fields": sorted(required),
                "filters": tree,
            }
        )
    return sealed


def _aggregate_state(
    state: dict[str, Any],
    groups: list[str],
    operations: list[dict[str, Any]],
    catalog: dict[str, Any],
    *,
    label: str,
) -> dict[str, Any]:
    groups = _stable(groups)
    if bool(state.get("aggregated")) and groups == list(state.get("grain") or []) and all(
        field == metric for metric, field in state["metric_fields"].items()
    ):
        return state
    if not set(groups) <= set(state["available"]):
        _fail("Aggregate grain fields are not available.", {"group_by": groups})
    metrics: list[dict[str, Any]] = []
    for metric_id, field in state["metric_fields"].items():
        metric = (catalog.get("metrics") or {}).get(metric_id) or {}
        function = str(metric.get("aggregation") or "sum")
        if function not in SUPPORTED_AGGREGATIONS:
            function = "sum"
        metrics.append({"field": field, "function": function, "as": metric_id, "dropna": True})
    if not metrics:
        _fail("Deterministic aggregation requires at least one registered metric.")
    operation_id = _next_id(operations, label)
    operations.append({"id": operation_id, "op": "aggregate", "input": state["input"], "group_by": groups, "metrics": metrics})
    return {
        **state,
        "input": operation_id,
        "available": set(groups) | set(state["metric_fields"]),
        "metric_fields": {metric_id: metric_id for metric_id in state["metric_fields"]},
        "grain": groups,
        "aggregated": True,
    }


def _project_join_side(
    state: dict[str, Any],
    join_keys: list[str],
    requested_fields: list[str],
    operations: list[dict[str, Any]],
    *,
    label: str,
) -> dict[str, Any]:
    fields = _stable(
        [
            *join_keys,
            *[field for field in requested_fields if field in state["available"]],
            *state["metric_fields"].values(),
        ]
    )
    if set(fields) == set(state["available"]):
        return state
    operation_id = _next_id(operations, label)
    operations.append({"id": operation_id, "op": "project", "input": state["input"], "fields": fields})
    return {**state, "input": operation_id, "available": set(fields)}


def _coalesce_metric(state: dict[str, Any], metric_id: str, operations: list[dict[str, Any]]) -> dict[str, Any]:
    operation_id = _next_id(operations, "coalesce")
    operations.append(
        {
            "id": operation_id,
            "op": "derive",
            "input": state["input"],
            "output_field": metric_id,
            "formula": {"expression": {"op": "coalesce", "args": [{"metric_ref": metric_id}, {"literal": 0}]}},
        }
    )
    return {**state, "input": operation_id, "available": set(state["available"]) | {metric_id}}


def _derive_metric(
    state: dict[str, Any],
    metric_id: str,
    metric: dict[str, Any],
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    expression = _formula_expression(metric.get("formula") or {}, metric)
    refs = set(_expression_refs(expression))
    if not refs <= set(state["available"]):
        _fail("Formula dependency is unavailable after registered joins.", {"metric_id": metric_id, "missing": sorted(refs - set(state["available"]))})
    operation_id = _next_id(operations, "derive")
    operations.append(
        {
            "id": operation_id,
            "op": "derive",
            "input": state["input"],
            "output_field": metric_id,
            "formula": {"expression": expression},
        }
    )
    metric_fields = dict(state["metric_fields"])
    metric_fields[metric_id] = metric_id
    return {**state, "input": operation_id, "available": set(state["available"]) | {metric_id}, "metric_fields": metric_fields}


def _formula_expression(formula: Mapping[str, Any], metric: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(formula.get("expression"), dict):
        return deepcopy(formula["expression"])
    operator = str(formula.get("op") or "")
    key_pairs = {
        "subtract": ("left_metric", "right_metric"),
        "add": ("left_metric", "right_metric"),
        "multiply": ("left_metric", "right_metric"),
        "safe_divide": ("numerator_metric", "denominator_metric"),
    }
    if operator not in key_pairs:
        _fail("Formula operator is not supported by the typed executor.", {"formula_op": operator})
    left_key, right_key = key_pairs[operator]
    expression: dict[str, Any] = {
        "op": operator,
        "args": [{"metric_ref": str(formula.get(left_key) or "")}, {"metric_ref": str(formula.get(right_key) or "")}],
    }
    if operator == "safe_divide":
        expression["zero_division"] = str(formula.get("zero_division") or "null")
        if str(metric.get("unit") or "").casefold() in {"percent", "percentage", "%"}:
            expression = {"op": "multiply", "args": [expression, {"literal": 100}]}
    return expression


def _apply_compare(
    state: dict[str, Any],
    catalog: dict[str, Any],
    semantics: dict[str, Any],
    template: dict[str, Any],
    requested_metrics: list[str],
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    kind = str(semantics.get("analysis_kind") or "")
    if kind not in {"field_compare", "compare_fields", "comparison"}:
        return state
    left = next(iter(_template_values(template, "left_field")), "")
    right = next(iter(_template_values(template, "right_field")), "")
    if not left or not right:
        available = [metric for metric in requested_metrics if metric in state["available"]]
        if len(available) < 2:
            _fail("Field comparison requires two registered metrics.")
        left, right = available[0], available[1]
    if left not in state["available"] or right not in state["available"]:
        _fail("Registered comparison fields are unavailable.")
    operator = str(semantics.get("comparison_operator") or "")
    if operator not in {"eq", "ne", "gt", "gte", "lt", "lte"}:
        _fail("Field comparison requires an explicit registered comparison operator.")
    operation_id = _next_id(operations, "compare")
    operations.append(
        {
            "id": operation_id,
            "op": "compare_fields",
            "input": state["input"],
            "left_field": left,
            "right_field": right,
            "operator": operator,
            "semantic_type": "number",
            "null_policy": "false",
        }
    )
    return {**state, "input": operation_id}


def _apply_sort(
    state: dict[str, Any],
    catalog: dict[str, Any],
    semantics: dict[str, Any],
    template: dict[str, Any],
    requested_metrics: list[str],
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    sort = semantics.get("sort") if isinstance(semantics.get("sort"), dict) else None
    if not sort:
        return state
    field = str(sort.get("field") or next((metric for metric in requested_metrics if metric in state["available"]), ""))
    if field not in state["available"]:
        _fail("Sort field is unavailable.", {"field": field})
    operation_id = _next_id(operations, "sort")
    operations.append(
        {
            "id": operation_id,
            "op": "sort",
            "input": state["input"],
            "keys": [{"field": field, "direction": str(sort.get("direction") or "asc"), "nulls": "last"}],
        }
    )
    return {**state, "input": operation_id}


def _apply_rank(
    state: dict[str, Any],
    catalog: dict[str, Any],
    semantics: dict[str, Any],
    template: dict[str, Any],
    requested_metrics: list[str],
    groups: list[str],
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    rank = semantics.get("rank") if isinstance(semantics.get("rank"), dict) else None
    if not rank:
        return state
    template_metric = next(iter(_template_values(template, "metric")), "")
    metric_id = template_metric if template_metric in state["available"] else next(
        (metric for metric in requested_metrics if metric in state["available"]),
        "",
    )
    if not metric_id:
        _fail("Rank requires a registered available metric.")
    tie_break = [field for field in _template_values(template, "stable_tie_break") if field in state["available"]]
    if not tie_break:
        tie_break = [field for field in groups if field in state["available"]]
    operation_id = _next_id(operations, "rank")
    operations.append(
        {
            "id": operation_id,
            "op": "rank",
            "input": state["input"],
            "partition_by": [],
            "rank_by": [
                {
                    "field": metric_id,
                    "direction": "desc" if str(rank.get("mode") or "top") == "top" else "asc",
                    "nulls": "last",
                }
            ],
            "tie_break_by": [{"field": field, "direction": "asc", "nulls": "last"} for field in tie_break],
            "limit": max(1, int(rank.get("limit") or 1)),
            "tie_policy": str(semantics.get("tie_policy") or ("include_all" if template.get("include_ties") else "exact_n")),
        }
    )
    return {**state, "input": operation_id}


def _relation_steps(
    catalog: dict[str, Any],
    anchor: str,
    required: set[str],
    grain_fields: list[str],
    preferences: list[str],
) -> tuple[list[tuple[str, str, str]], set[str]]:
    relations = catalog.get("relations") if isinstance(catalog.get("relations"), dict) else {}
    reached = {anchor}
    target = set(required) | {anchor}
    steps: list[tuple[str, str, str]] = []
    preference_index = {relation_id: index for index, relation_id in enumerate(preferences)}
    while not target <= reached:
        candidates: list[tuple[tuple[int, int, int, str], str, str, str]] = []
        for relation_id, relation in relations.items():
            if not isinstance(relation, dict):
                continue
            left, right = str(relation.get("left_dataset") or ""), str(relation.get("right_dataset") or "")
            if left in reached and right not in reached:
                current, new, keys = left, right, _stable(relation.get("left_keys") or [])
            elif right in reached and left not in reached:
                current, new, keys = right, left, _stable(relation.get("right_keys") or [])
            else:
                continue
            # Fine-key joins happen before joins that coarsen at the requested grain.
            coarsening = 1 if grain_fields and set(keys) <= set(grain_fields) else 0
            distance = _dataset_distance(catalog, new, target - reached)
            preference = preference_index.get(str(relation_id), len(preference_index) + 1)
            candidates.append(((distance, coarsening, preference, str(relation_id)), str(relation_id), current, new))
        if not candidates:
            _fail("Required datasets are not connected by registered relations.", {"required": sorted(target), "reached": sorted(reached)})
        candidates.sort(key=lambda item: item[0])
        useful = [item for item in candidates if _can_reach_required(catalog, reached | {item[3]}, target)]
        _, relation_id, current, new = (useful or candidates)[0]
        steps.append((relation_id, current, new))
        reached.add(new)
    return steps, reached


def _can_reach_required(catalog: dict[str, Any], reached: set[str], target: set[str]) -> bool:
    closure = set(reached)
    changed = True
    while changed:
        changed = False
        for relation in (catalog.get("relations") or {}).values():
            if not isinstance(relation, dict):
                continue
            left, right = str(relation.get("left_dataset") or ""), str(relation.get("right_dataset") or "")
            if left in closure and right not in closure:
                closure.add(right)
                changed = True
            if right in closure and left not in closure:
                closure.add(left)
                changed = True
    return target <= closure


def _dataset_distance(catalog: dict[str, Any], start: str, targets: set[str]) -> int:
    if start in targets:
        return 0
    frontier = {start}
    visited = {start}
    distance = 0
    while frontier:
        distance += 1
        following: set[str] = set()
        for relation in (catalog.get("relations") or {}).values():
            if not isinstance(relation, dict):
                continue
            left, right = str(relation.get("left_dataset") or ""), str(relation.get("right_dataset") or "")
            if left in frontier and right not in visited:
                following.add(right)
            if right in frontier and left not in visited:
                following.add(left)
        if following & targets:
            return distance
        visited.update(following)
        frontier = following
    return 10**6


def _relation_for_previous(catalog: dict[str, Any], available: set[str], owner: str) -> tuple[str, list[str], list[str]]:
    for relation_id, relation in (catalog.get("relations") or {}).items():
        if not isinstance(relation, dict):
            continue
        if relation.get("right_dataset") == owner and set(relation.get("left_keys") or []) <= available:
            return str(relation_id), _stable(relation.get("left_keys") or []), _stable(relation.get("right_keys") or [])
        if relation.get("left_dataset") == owner and set(relation.get("right_keys") or []) <= available:
            return str(relation_id), _stable(relation.get("right_keys") or []), _stable(relation.get("left_keys") or [])
    _fail("Previous result cannot be enriched through a registered relation.", {"dataset": owner})
    raise AssertionError


def _date_filter_dataset(
    catalog: dict[str, Any],
    dataset_order: Iterable[str],
    anchor: str,
    semantics: dict[str, Any],
) -> str:
    """Choose the joined dataset that can prove an explicit date scope.

    Date semantics may only constrain the selected anchor's registered date
    policy.  A joined dataset's date must never be substituted as a proxy for
    a source that has no date policy of its own.  Explicit all-time semantics
    keep ``date_explicit`` false and return no filter dataset.
    """

    if not bool(semantics.get("date_explicit")):
        return ""
    ordered = _stable(dataset_order)

    def has_date_policy(dataset_key: str) -> bool:
        dataset = (catalog.get("datasets") or {}).get(dataset_key) or {}
        policy = dataset.get("date_policy") if isinstance(dataset.get("date_policy"), dict) else {}
        return bool(policy.get("field"))

    return anchor if anchor in ordered and has_date_policy(anchor) else ""


def _anchor_dataset(catalog: dict[str, Any], metric_datasets: list[str], preferences: list[str]) -> str:
    for relation_id in preferences:
        relation = (catalog.get("relations") or {}).get(relation_id)
        if isinstance(relation, dict) and relation.get("left_dataset") in metric_datasets:
            return str(relation["left_dataset"])
    if metric_datasets:
        return metric_datasets[0]
    _fail("No anchor dataset can be resolved.")
    raise AssertionError


def _field_owner(catalog: dict[str, Any], field: str, *, anchor: str, preferred: list[str]) -> str:
    owners = _stable(((catalog.get("fields") or {}).get(field) or {}).get("dataset_keys") or [])
    if not owners:
        _fail("Field has no registered dataset owner.", {"field": field})
    for dataset_key in [anchor, *preferred]:
        if dataset_key and dataset_key in owners:
            return dataset_key
    return owners[0]


def _metric_binding(catalog: dict[str, Any], metric_id: str, *, required: bool = True) -> dict[str, Any]:
    metric = (catalog.get("metrics") or {}).get(metric_id) or {}
    binding = metric.get("source_binding") if isinstance(metric.get("source_binding"), dict) else None
    if binding:
        return deepcopy(binding)
    if required:
        _fail("Metric has no registered source binding.", {"metric_id": metric_id})
    return {}


def _metric_dataset(
    catalog: dict[str, Any],
    metric_id: str,
    *,
    selected_datasets: Iterable[str] = (),
) -> str:
    binding = _metric_binding(catalog, metric_id)
    family = str(binding.get("dataset_family") or "")
    matches = [
        str(dataset_key)
        for dataset_key, dataset in (catalog.get("datasets") or {}).items()
        if isinstance(dataset, dict) and str(dataset.get("family") or "") == family
    ]
    pinned = [dataset_key for dataset_key in _stable(selected_datasets) if dataset_key in matches]
    if len(pinned) == 1:
        return pinned[0]
    if len(pinned) > 1:
        _fail(
            "Metric dataset family has conflicting selected datasets.",
            {"metric_id": metric_id, "family": family, "matches": matches, "selected": pinned},
        )
    if len(matches) != 1:
        _fail("Metric dataset family must resolve uniquely.", {"metric_id": metric_id, "family": family, "matches": matches})
    return matches[0]


def _metric_closure(catalog: dict[str, Any], requested: Iterable[str]) -> list[str]:
    metrics = catalog.get("metrics") if isinstance(catalog.get("metrics"), dict) else {}
    result: list[str] = []
    visiting: set[str] = set()

    def add(metric_id: str) -> None:
        if metric_id in result:
            return
        if metric_id in visiting:
            _fail("Metric formula dependency cycle detected.", {"metric_id": metric_id})
        metric = metrics.get(metric_id)
        if not isinstance(metric, dict):
            _fail("Requested metric is not registered.", {"metric_id": metric_id})
        visiting.add(metric_id)
        for dependency in _formula_dependencies(metric.get("formula") or {}):
            add(dependency)
        visiting.remove(metric_id)
        result.append(metric_id)

    for value in requested:
        add(str(value))
    return result


def _formula_dependencies(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"left_metric", "right_metric", "numerator_metric", "denominator_metric", "metric_ref"} and isinstance(child, str):
                result.append(child)
            else:
                result.extend(_formula_dependencies(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(_formula_dependencies(child))
    return _stable(result)


def _expression_refs(value: Any) -> list[str]:
    return _formula_dependencies(value)


def _select_recipe(catalog: dict[str, Any], semantics: dict[str, Any], question: str) -> dict[str, Any]:
    explicit_refs = _stable(semantics.get("recipe_refs") or [])
    if explicit_refs:
        if len(explicit_refs) != 1:
            _fail("A compiled intent may reference at most one recipe.", {"recipe_refs": explicit_refs})
        recipe = (catalog.get("recipes") or {}).get(explicit_refs[0])
        if not isinstance(recipe, dict):
            _fail("Selected recipe is not registered.", {"recipe_ref": explicit_refs[0]})
        return deepcopy(recipe)
    normalized = _normalize(question)
    requested_metrics = set(map(str, semantics.get("metric_refs") or []))
    requested_fields = set(map(str, [*(semantics.get("dimension_refs") or []), *(semantics.get("field_refs") or [])]))
    kind = str(semantics.get("analysis_kind") or "")
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for recipe_id, value in (catalog.get("recipes") or {}).items():
        if not isinstance(value, dict):
            continue
        template = value.get("default_operation_template") if isinstance(value.get("default_operation_template"), dict) else {}
        aliases = [_normalize(alias) for alias in value.get("aliases") or []]
        score = 100 * sum(1 for alias in aliases if alias and alias in normalized)
        score += 10 * len(requested_metrics & set(_template_values(template, "metrics") + _template_values(template, "metric")))
        score += 3 * len(requested_fields & set(_template_values(template, "group_by") + _template_values(template, "allowed_fields")))
        operations = set(_template_values(template, "op"))
        if kind in operations or (kind == "rank" and "rank" in operations):
            score += 15
        scored.append((score, str(recipe_id), deepcopy(value)))
    if not scored:
        return {}
    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored[0][2] if scored[0][0] > 0 else {}


def _selected_registered_function(
    catalog: dict[str, Any], semantics: dict[str, Any]
) -> dict[str, Any] | None:
    refs = _stable(semantics.get("function_refs") or [])
    if not refs:
        return None
    if len(refs) != 1:
        _fail("A compiled intent may reference exactly one registered function.", {"function_refs": refs})
    function_id, separator, raw_version = refs[0].rpartition("@")
    if not separator or not function_id or not raw_version.isdigit() or int(raw_version) < 1:
        _fail("Registered function reference must use function_id@version.", {"function_ref": refs[0]})
    card = _registered_function_card(catalog, function_id, int(raw_version))
    try:
        normalized = validate_registered_function_card(card)
    except ContractError as exc:
        _fail(
            "Registered function card is not bound to the local allowlist.",
            {"function_ref": refs[0], "reason": str(exc)},
        )
    fields = set(catalog.get("fields") or {})
    referenced = set(normalized.get("required_fields") or []) | set(
        (normalized.get("call_template") or {}).get("output_fields") or []
    )
    if not referenced <= fields:
        _fail(
            "Registered function card references fields outside the catalog.",
            {"function_ref": refs[0], "missing": sorted(referenced - fields)},
        )
    dataset_ref = str((normalized.get("call_template") or {}).get("dataset_ref") or "")
    dataset = (catalog.get("datasets") or {}).get(dataset_ref)
    if not isinstance(dataset, dict) or not referenced <= set(dataset.get("fields") or {}):
        _fail(
            "Registered function dataset binding does not contain its field closure.",
            {"function_ref": refs[0], "dataset_ref": dataset_ref},
        )
    selected_datasets = set(map(str, semantics.get("dataset_refs") or []))
    if selected_datasets and selected_datasets != {dataset_ref}:
        _fail(
            "Registered function semantic dataset differs from its catalog binding.",
            {"function_ref": refs[0], "dataset_ref": dataset_ref},
        )
    return normalized


def _registered_function_card(
    catalog: dict[str, Any], function_id: str, version: int
) -> dict[str, Any]:
    matches = [
        deepcopy(card)
        for card in catalog.get("specialized_functions") or []
        if isinstance(card, dict)
        and str(card.get("function_id") or "") == str(function_id)
        and card.get("version") == version
    ]
    if len(matches) != 1:
        _fail(
            "Registered function identity does not resolve uniquely in the catalog.",
            {"function_id": function_id, "version": version},
        )
    return matches[0]


def _apply_registered_function(
    state: dict[str, Any],
    card: dict[str, Any],
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    required = set(map(str, card.get("required_fields") or []))
    available = set(state.get("available") or set())
    if not required <= available:
        _fail(
            "Registered function required fields are unavailable at its execution stage.",
            {"missing": sorted(required - available)},
        )
    operation_id = _next_id(operations, "registered_call")
    operations.append(
        build_registered_call_operation(
            card,
            operation_id=operation_id,
            input_ref=str(state.get("input") or ""),
        )
    )
    return {**state, "input": operation_id}


def _grain_fields(
    catalog: dict[str, Any],
    semantics: dict[str, Any],
    template: dict[str, Any],
    requested_dimensions: list[str],
) -> list[str]:
    if requested_dimensions:
        return requested_dimensions
    grain_id = next(iter(_template_values(template, "grain_id")), "")
    grain = (catalog.get("grains") or {}).get(grain_id) if grain_id else None
    return _stable((grain or {}).get("keys") or [])


def _template_values(value: Any, key_name: str) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == key_name:
                if isinstance(child, list):
                    result.extend(str(item) for item in child if str(item))
                elif isinstance(child, str) and child:
                    result.append(child)
            result.extend(_template_values(child, key_name))
    elif isinstance(value, list):
        for child in value:
            result.extend(_template_values(child, key_name))
    return _stable(result)


def _job(catalog: dict[str, Any], dataset_key: str, index: int) -> dict[str, Any]:
    dataset = (catalog.get("datasets") or {}).get(dataset_key)
    if not isinstance(dataset, dict):
        _fail("Dataset is not registered.", {"dataset_key": dataset_key})
    return {
        "job_id": f"job_{index}_{_safe_id(dataset_key)}",
        "dataset_key": dataset_key,
        "source_type": str(dataset.get("source_type") or "unknown"),
        "query_ref": str(dataset.get("query_ref") or ""),
        "config_ref": str(dataset.get("config_ref") or ""),
        "parameters": {},
        "required_fields": sorted(dataset.get("fields") or {}),
        "filters": None,
        "requirement": "required",
    }


def _semantic_type(catalog: dict[str, Any], field: str) -> str:
    return str(((catalog.get("fields") or {}).get(field) or {}).get("semantic_type") or "string")


def _reverse_cardinality(value: str) -> str:
    return {"one_to_many": "many_to_one", "many_to_one": "one_to_many"}.get(value, value)


def _execution_cardinality(value: str) -> str:
    return "one_to_one" if value == "one_to_zero_or_one" else value


def _next_id(operations: list[dict[str, Any]], label: str) -> str:
    return f"op_{len(operations) + 1:02d}_{_safe_id(label)}"


def _safe_id(value: Any) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_]+", "_", str(value or "")).strip("_").lower()
    return normalized or "value"


def _normalize(value: Any) -> str:
    return re.sub(r"[\W_]+", "", str(value or "").casefold(), flags=re.UNICODE)


def _stable(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value or "")
        if text and text not in result:
            result.append(text)
    return result


def _finalize(
    intent: dict[str, Any],
    bundle: dict[str, Any],
    catalog: dict[str, Any],
    jobs: list[dict[str, Any]],
    operations: list[dict[str, Any]],
    result_operation_id: str,
    columns: list[str],
    grain: list[str],
    *,
    input_refs: list[str] | None = None,
) -> dict[str, Any]:
    lineage = {
        field: {
            "catalog_sha256": catalog.get("catalog_sha256"),
            "field": field,
            "dataset_keys": _stable(((catalog.get("fields") or {}).get(field) or {}).get("dataset_keys") or []),
        }
        for field in columns
    }
    material = {
        "contract_version": "analysis.plan.v1",
        "intent_sha256": intent.get("intent_sha256"),
        "candidate_bundle_sha256": bundle.get("bundle_sha256"),
        "catalog_sha256": catalog.get("catalog_sha256"),
        "input_refs": list(input_refs or []),
        "retrieval_jobs": jobs,
        "operations": operations,
        "result_operation_id": result_operation_id,
        "result_contract": {"columns": columns, "ordering": [], "grain": grain},
        "lineage": lineage,
    }
    normalized = deepcopy(material)
    normalized["retrieval_jobs"] = sorted(normalized["retrieval_jobs"], key=lambda item: item["job_id"])
    plan_hash = sha256_json(normalized)
    semantic = {
        key: normalized[key]
        for key in (
            "catalog_sha256",
            "input_refs",
            "retrieval_jobs",
            "operations",
            "result_operation_id",
            "result_contract",
            "lineage",
        )
    }
    return {**material, "plan_id": f"plan:{plan_hash}", "plan_fingerprint": sha256_json(semantic)}


def _fail(message: str, details: dict[str, Any] | None = None) -> None:
    raise ContractError("metadata_dependency_error", "plan_compilation", message, details or {})


__all__ = ["compile_generic_v2_plan", "validate_generic_v2_plan"]
