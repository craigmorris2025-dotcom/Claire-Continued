from __future__ import annotations

from typing import Any

from runtime_core.engines.auto_design import AutoDesignEngine
from runtime_core.engines.system_design_engine import SystemDesignEngine
from runtime_core.engines.technical_feasibility_engine import TechnicalFeasibilityEngine


SCHEMA_VERSION = "claire_live_design_portal_v1"


def _get(payload: dict[str, Any], *path: str, fallback: Any = None) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return fallback
        current = current.get(key)
    return fallback if current is None else current


def _as_text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _score(value: Any, fallback: float = 0.0) -> float:
    try:
        return round(float(value or fallback), 4)
    except (TypeError, ValueError):
        return fallback


def _market_gap(core_output: dict[str, Any]) -> dict[str, Any]:
    gap = _get(core_output, "user_facing_result", "discovery", "opportunity_discovery", "opportunity_map", fallback={})
    discovery = _get(core_output, "user_facing_result", "discovery", "opportunity_discovery", fallback={})
    if not isinstance(gap, dict):
        gap = {}
    if isinstance(discovery, dict):
        gap = {
            **gap,
            "domain": discovery.get("domain") or _get(core_output, "user_facing_result", "trend", "domain", fallback="technology"),
            "sector": discovery.get("sector") or _get(core_output, "user_facing_result", "trend", "sector", fallback="general"),
            "solution_class": gap.get("solution_class") or discovery.get("opportunity_type", {}).get("type", "intelligence platform"),
            "needed_solution": gap.get("unmet_need") or gap.get("target_gap") or "Validated intelligence system",
        }
    return gap


def _scores(core_output: dict[str, Any]) -> dict[str, Any]:
    return {
        "_confidence": _score(_get(core_output, "user_facing_result", "trend", "confidence", fallback=0.5), 0.5),
        "discovery_score": _score(_get(core_output, "user_facing_result", "trend", "discovery_score", "score", fallback=0.0)),
        "thesis_score": _score(_get(core_output, "user_facing_result", "thesis", "thesis_score", "score", fallback=0.0)),
        "opportunity_score": _score(_get(core_output, "user_facing_result", "discovery", "opportunity_discovery", "opportunity_score", "score", fallback=0.0)),
        "buildability_score": _score(_get(core_output, "user_facing_result", "discovery", "opportunity_discovery", "buildability_score", "score", fallback=0.62), 0.62),
        "market_pressure_score": _score(_get(core_output, "user_facing_result", "trend", "discovery_score", "score", fallback=0.0)),
    }


def _build_design_context(core_output: dict[str, Any], technology_base: dict[str, Any]) -> dict[str, Any]:
    market_gap = _market_gap(core_output)
    domain = market_gap.get("domain") or _get(core_output, "user_facing_result", "trend", "domain", fallback="technology")
    query = " ".join(
        part
        for part in [
            _as_text(_get(core_output, "user_facing_result", "headline", fallback="")),
            _as_text(market_gap.get("unmet_need")),
            _as_text(market_gap.get("solution_class")),
        ]
        if part
    )
    tech_results = _get(technology_base, "technology_search", "results", fallback=[])
    return {
        "domain": domain,
        "market_gap": market_gap,
        "scores": _scores(core_output),
        "technology_intelligence": {
            "technologies_considered": tech_results if isinstance(tech_results, list) else [],
            "selected_stack": {
                "runtime": "governed_local_or_hybrid_runtime",
                "evidence": "source_authority_and_technology_base",
                "operator_surface": "design_portal_workbench",
            },
        },
        "query": query or "Claire design candidate",
    }


def _required_components(system_design: dict[str, Any], technical_feasibility: dict[str, Any], technology_base: dict[str, Any]) -> list[dict[str, Any]]:
    modules = _get(system_design, "architecture_blueprint", "modules", fallback=[])
    required = _get(technical_feasibility, "architecture_readiness", "required_components", fallback=[])
    tech_results = _get(technology_base, "technology_search", "results", fallback=[])
    tech_names = [item.get("name") for item in tech_results if isinstance(item, dict) and item.get("name")]
    components: dict[str, dict[str, Any]] = {}

    for module in modules if isinstance(modules, list) else []:
        if not isinstance(module, dict):
            continue
        component = _as_text(module.get("component") or module.get("name"))
        if not component:
            continue
        components[component] = {
            "id": component,
            "label": component.replace("_", " ").title(),
            "role": module.get("role") or "required runtime component",
            "priority": module.get("priority") or "required",
            "interfaces": module.get("interfaces") if isinstance(module.get("interfaces"), list) else [],
            "needed_to_function": True,
            "current_tech_status": "buildable_now_with_governance",
            "buildability": "ready_for_operator_review",
            "matched_technologies": tech_names[:3],
        }

    for component in required if isinstance(required, list) else []:
        key = _as_text(component)
        if not key:
            continue
        components.setdefault(
            key,
            {
                "id": key,
                "label": key.replace("_", " ").title(),
                "role": "required by technical feasibility profile",
                "priority": "critical",
                "interfaces": [],
                "needed_to_function": True,
                "current_tech_status": "requires_component_mapping",
                "buildability": "requires_validation",
                "matched_technologies": tech_names[:3],
            },
        )

    return list(components.values())


def _architecture(system_design: dict[str, Any]) -> dict[str, Any]:
    modules = _get(system_design, "architecture_blueprint", "modules", fallback=[])
    flows = system_design.get("data_flows") if isinstance(system_design, dict) else []
    nodes = [
        {
            "id": module.get("component"),
            "label": _as_text(module.get("component")).replace("_", " ").title(),
            "role": module.get("role", ""),
            "priority": module.get("priority", "required"),
        }
        for module in modules
        if isinstance(module, dict) and module.get("component")
    ]
    edges = [
        {"from": flow.get("from"), "to": flow.get("to"), "payload": flow.get("payload"), "validation": flow.get("validation")}
        for flow in flows
        if isinstance(flow, dict) and flow.get("from") and flow.get("to")
    ]
    return {
        "style": _get(system_design, "architecture_blueprint", "architecture_style", fallback=system_design.get("architecture", "modular")),
        "summary": "Live design preview of the candidate system before blueprint lock.",
        "nodes": nodes,
        "edges": edges,
        "data_flows": flows if isinstance(flows, list) else [],
    }


def _buildability(technical_feasibility: dict[str, Any], technology_base: dict[str, Any], source_authority: dict[str, Any]) -> dict[str, Any]:
    feasibility_score = _score(_get(technical_feasibility, "technical_feasibility_score", "score", fallback=0.0))
    readiness = _score(_get(technology_base, "readiness", "average_readiness_level", fallback=0.0))
    current_count = int(_get(technology_base, "counts", "current_buildable_records", fallback=0) or 0)
    speculative_count = int(_get(technology_base, "counts", "speculative_or_future_records", fallback=0) or 0)
    live_evidence_present = bool(source_authority.get("live_evidence_present") or source_authority.get("live_truth_eligible"))
    current_compatible = feasibility_score >= 0.48 and readiness >= 6.5 and current_count > 0
    if not current_compatible or current_count == 0:
        sci_fi_risk = "high"
    elif speculative_count > current_count * 2 or not live_evidence_present:
        sci_fi_risk = "medium"
    else:
        sci_fi_risk = "low"
    return {
        "classification": _get(technical_feasibility, "feasibility_classification", "state", fallback="feasible_with_validation"),
        "score": feasibility_score,
        "current_tech_compatible": current_compatible,
        "sci_fi_risk": sci_fi_risk,
        "current_buildable_records": current_count,
        "speculative_or_future_records": speculative_count,
        "average_technology_readiness": readiness,
        "reasons": [
            "System design is mapped to existing runtime architecture components.",
            "Technology base filters science-fiction records away from current buildability counts.",
            "Live evidence must be promoted before runtime truth can treat the design as validated.",
        ],
        "blockers": [] if current_compatible else ["insufficient current-technology grounding"],
        "promotion_recommendation": "promote_to_blueprint_after_live_validation" if current_compatible else "hold_for_component_validation",
    }


def _live_design_events(lifecycle: dict[str, Any]) -> list[dict[str, Any]]:
    stage_labels = {
        16: "portfolio candidate optimization",
        17: "breakthrough expansion check",
        18: "buildability validation",
        19: "technology/component mapping",
        20: "system architecture preview",
        21: "feasibility and controls review",
        22: "design portal handoff",
    }
    stages = lifecycle.get("stages") if isinstance(lifecycle, dict) else []
    by_number = {}
    for stage in stages if isinstance(stages, list) else []:
        if isinstance(stage, dict):
            number = stage.get("number") or stage.get("stage_number")
            if str(number or "").isdigit():
                by_number[int(number)] = stage
    events = []
    for number, label in stage_labels.items():
        stage = by_number.get(number, {})
        events.append(
            {
                "stage": number,
                "label": label,
                "runtime_status": stage.get("status", "design_preview_ready") if isinstance(stage, dict) else "design_preview_ready",
                "operator_visible": True,
            }
        )
    return events


def _required_systems(system_design: dict[str, Any], technical_feasibility: dict[str, Any]) -> list[dict[str, Any]]:
    architecture = _get(system_design, "architecture_blueprint", fallback={})
    return [
        {
            "id": "evidence_ingestion_system",
            "label": "Evidence Ingestion System",
            "purpose": "bring source material into the design process with traceable provenance",
            "status": "required",
            "evidence_needed": "accepted source pack or live promoted evidence",
        },
        {
            "id": "component_mapping_system",
            "label": "Component Mapping System",
            "purpose": "map functional requirements to current technologies and interfaces",
            "status": "ready_for_v1",
            "evidence_needed": ", ".join(architecture.get("recommended_services", [])[:3]) if isinstance(architecture, dict) else "service map",
        },
        {
            "id": "feasibility_governance_system",
            "label": "Feasibility Governance System",
            "purpose": "separate buildable-now systems from speculative or future-state concepts",
            "status": _get(technical_feasibility, "feasibility_classification", "state", fallback="feasible_with_validation"),
            "evidence_needed": "prototype validation, component fit, deployment controls",
        },
        {
            "id": "blueprint_export_system",
            "label": "Blueprint Export System",
            "purpose": "convert reviewed design into technical specs, blueprints, and implementation phases",
            "status": _get(system_design, "readiness", "state", fallback="blueprint_candidate"),
            "evidence_needed": "operator promotion decision",
        },
    ]


def _build_materials_manifest(
    required_components: list[dict[str, Any]],
    required_systems: list[dict[str, Any]],
    system_design: dict[str, Any],
    technical_feasibility: dict[str, Any],
    technology_base: dict[str, Any],
) -> dict[str, Any]:
    tech_records = _get(technology_base, "technology_search", "results", fallback=[])
    software_stack = _get(system_design, "technology_stack", fallback={})
    deployment_controls = _get(technical_feasibility, "deployment_controls", fallback={})
    prototype_plan = _get(technical_feasibility, "prototype_plan", fallback={})
    return {
        "schema": "technology_system_code_component_materials_v1",
        "purpose": "enumerate what the candidate needs before blueprint, portfolio, acquirer, or package promotion",
        "technology_materials": [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "readiness_level": item.get("readiness_level"),
                "manufacturability": item.get("manufacturability"),
                "deployment": item.get("deployment"),
                "status": "current_buildable_reference",
            }
            for item in tech_records[:8]
            if isinstance(item, dict)
        ],
        "system_materials": [
            {
                "id": item["id"],
                "name": item["label"],
                "purpose": item.get("purpose"),
                "needed_to_operate": True,
                "evidence_needed": item.get("evidence_needed"),
            }
            for item in required_systems
        ],
        "component_materials": [
            {
                "id": item["id"],
                "name": item["label"],
                "role": item.get("role"),
                "interfaces": item.get("interfaces", []),
                "priority": item.get("priority"),
                "needed_to_function": item.get("needed_to_function", True),
            }
            for item in required_components
        ],
        "code_materials": [
            {"id": "pipeline_contracts", "name": "Pipeline contracts", "purpose": "carry candidate state across discovery, feasibility, design, portfolio, and package stages"},
            {"id": "component_matcher", "name": "Component matcher", "purpose": "map required functions to buildable technology records and implementation interfaces"},
            {"id": "blueprint_exporter", "name": "Blueprint exporter", "purpose": "turn approved design state into specs, diagrams, and package artifacts"},
            {"id": "portfolio_router", "name": "Portfolio router", "purpose": "send viable designs into portfolio construction and downstream acquirer matching"},
            {"id": "operator_review_gate", "name": "Operator review gate", "purpose": "prevent unvalidated runtime truth mutation or automatic promotion"},
        ],
        "deployment_materials": [
            {"id": "local_runtime", "name": "Local governed runtime", "status": "available"},
            {"id": "dashboard_operator_surface", "name": "Design Portal dashboard surface", "status": "wired"},
            {"id": "validation_controls", "name": "Validation and deployment controls", "status": deployment_controls.get("level", "required") if isinstance(deployment_controls, dict) else "required"},
            {"id": "prototype_plan", "name": "Prototype plan", "status": prototype_plan.get("status", "required") if isinstance(prototype_plan, dict) else "required"},
        ],
    }


def _blueprint_package(system_design: dict[str, Any], buildability: dict[str, Any], materials_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "draft_ready" if buildability.get("current_tech_compatible") else "draft_requires_validation",
        "blueprint_type": "invention_candidate_system_blueprint",
        "technical_specs": system_design.get("technical_specs", {}),
        "architecture_blueprint": system_design.get("architecture_blueprint", {}),
        "implementation_phases": system_design.get("implementation_phases", []),
        "data_flows": system_design.get("data_flows", []),
        "materials_manifest_ref": materials_manifest.get("schema"),
        "exports_required": [
            "technical_specification",
            "component_map",
            "system_architecture_blueprint",
            "materials_manifest",
            "feasibility_and_buildability_report",
            "portfolio_candidate_profile",
            "acquirer_package_inputs",
        ],
    }


def _invention_commitment(buildability: dict[str, Any], context: dict[str, Any], source_authority: dict[str, Any]) -> dict[str, Any]:
    scores = context.get("scores", {})
    viability_score = round(
        (
            _score(scores.get("opportunity_score"), 0.0)
            + _score(scores.get("thesis_score"), 0.0)
            + _score(buildability.get("score"), 0.0)
        )
        / 3,
        4,
    )
    need_solution = bool(context.get("market_gap", {}).get("unmet_need") or context.get("market_gap", {}).get("needed_solution"))
    gap_filler = bool(context.get("market_gap", {}).get("target_gap") or context.get("market_gap", {}).get("proof_to_unlock"))
    innovation_match = buildability.get("current_tech_compatible") and buildability.get("sci_fi_risk") in {"low", "medium"}
    live_ready = bool(source_authority.get("live_evidence_present") or source_authority.get("live_truth_eligible"))
    commit_ready = need_solution and gap_filler and innovation_match and viability_score >= 0.52
    return {
        "status": "commit_candidate_ready" if commit_ready else "needs_more_validation",
        "commit_to_build_attempt": commit_ready,
        "conditions": {
            "realistic": buildability.get("current_tech_compatible"),
            "viable": viability_score >= 0.52,
            "need_solution": need_solution,
            "gap_filler": gap_filler,
            "innovation_candidate": innovation_match,
            "live_evidence_promoted": live_ready,
        },
        "viability_score": viability_score,
        "runtime_policy": "automatic_design_allowed_after_conditions; truth_promotion_requires_operator_or_validated_evidence",
    }


def _downstream_route_contract(invention_commitment: dict[str, Any], blueprint_package: dict[str, Any]) -> dict[str, Any]:
    design_ready = invention_commitment.get("commit_to_build_attempt") and blueprint_package.get("status") in {"draft_ready", "draft_requires_validation"}
    return {
        "status": "route_ready" if design_ready else "route_after_validation",
        "normal_path": [
            "discovery_or_breakthrough_candidate",
            "buildability_and_feasibility_gate",
            "auto_design_and_materials_manifest",
            "blueprint_and_spec_generation",
            "portfolio_candidate_construction",
            "acquirer_identification",
            "acquisition_fit_rationale",
            "final_package_construction",
        ],
        "route": "breakthrough_design" if design_ready else "portfolio_creation_optimization_until_design_validated",
        "portfolio_required": True,
        "acquirer_matching_required": True,
        "package_required": True,
        "blocked_from_runtime_truth": not bool(invention_commitment.get("conditions", {}).get("live_evidence_promoted")),
        "next_runtime_action": "promote validated evidence then route through portfolio/acquirer/package" if design_ready else "validate design conditions before promotion",
    }


def _runtime_design_alert(invention_commitment: dict[str, Any], buildability: dict[str, Any], route_selected: str) -> dict[str, Any]:
    trigger = bool(invention_commitment.get("commit_to_build_attempt")) or "breakthrough" in str(route_selected) or buildability.get("current_tech_compatible")
    return {
        "status": "active" if trigger else "watching",
        "trigger_type": "discovery_or_breakthrough_design_candidate" if trigger else "no_design_alert",
        "severity": "high" if invention_commitment.get("commit_to_build_attempt") else "medium" if trigger else "low",
        "operator_message": (
            "Discovery/build candidate is ready for Design Portal review, artifact generation, CAD/video asset slots, and route validation."
            if trigger
            else "Design Portal is watching runtime outputs for a buildable discovery or breakthrough trigger."
        ),
        "opens_surface": "design_portal",
        "conditional_triggers": [
            "realistic_current_technology_match",
            "viable_need_solution",
            "gap_filler_or_innovation_candidate",
            "blueprint_or_materials_package_ready",
            "breakthrough_or_discovery_route_signal",
        ],
    }


def _portal_actions(invention_commitment: dict[str, Any], downstream_route: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": "prepare_cad_viewer",
            "label": "Prepare CAD Viewer",
            "kind": "viewer",
            "enabled": True,
            "effect": "creates or refreshes the CAD artifact registry and viewer contract",
            "endpoint": "/api/design-portal/action",
        },
        {
            "id": "prepare_video_viewer",
            "label": "Prepare Video Viewer",
            "kind": "viewer",
            "enabled": True,
            "effect": "creates or refreshes the video/simulation registry and viewer contract",
            "endpoint": "/api/design-portal/action",
        },
        {
            "id": "prepare_asset_import_slots",
            "label": "Prepare Import Slots",
            "kind": "artifact",
            "enabled": True,
            "effect": "marks CAD/video import slots ready for attached or generated assets",
            "endpoint": "/api/design-portal/action",
        },
        {
            "id": "hold_design_package",
            "label": "Hold",
            "kind": "review",
            "enabled": True,
            "effect": "records an operator hold decision without mutating runtime truth",
            "endpoint": "/api/design-portal/action",
        },
        {
            "id": "approve_design_package",
            "label": "Approve Review",
            "kind": "review",
            "enabled": True,
            "effect": "records review approval for downstream validation handoff",
            "endpoint": "/api/design-portal/action",
        },
        {
            "id": "validate_design_route",
            "label": "Validate Route",
            "kind": "validation",
            "enabled": bool(invention_commitment.get("commit_to_build_attempt")) or downstream_route.get("portfolio_required"),
            "effect": "checks discovery -> design -> portfolio -> acquirer -> package continuity",
            "endpoint": "/api/design-portal/action",
        },
        {
            "id": "promote_design_package",
            "label": "Promote",
            "kind": "promotion",
            "enabled": False,
            "effect": "blocked until evidence and operator promotion requirements are satisfied",
            "endpoint": "/api/design-portal/action",
        },
    ]


def _validation_chain(workbench_parts: dict[str, Any]) -> dict[str, Any]:
    candidate = workbench_parts.get("candidate", {})
    architecture = workbench_parts.get("architecture", {})
    materials = workbench_parts.get("materials_manifest", {})
    blueprint = workbench_parts.get("blueprint_package", {})
    downstream = workbench_parts.get("downstream_route_contract", {})
    checks = [
        {"id": "discovery_candidate", "label": "Discovery or breakthrough candidate", "passed": bool(candidate.get("title"))},
        {"id": "auto_design", "label": "Automatic design state", "passed": bool(architecture.get("nodes"))},
        {"id": "materials_manifest", "label": "Materials/components/code manifest", "passed": bool(materials.get("component_materials"))},
        {"id": "blueprint_package", "label": "Blueprint/spec package", "passed": bool(blueprint.get("exports_required"))},
        {"id": "portfolio_route", "label": "Portfolio route handoff", "passed": downstream.get("portfolio_required") is True},
        {"id": "acquirer_route", "label": "Acquirer matching handoff", "passed": downstream.get("acquirer_matching_required") is True},
        {"id": "final_package_route", "label": "Final package handoff", "passed": downstream.get("package_required") is True},
    ]
    passed = len([item for item in checks if item["passed"]])
    return {
        "status": "validated" if passed == len(checks) else "partial",
        "passed": passed,
        "total": len(checks),
        "completion_percent": round((passed / max(1, len(checks))) * 100, 1),
        "checks": checks,
    }


def _promotion_gates(buildability: dict[str, Any], source_authority: dict[str, Any]) -> list[dict[str, Any]]:
    live_ready = bool(source_authority.get("live_evidence_present") or source_authority.get("live_truth_eligible"))
    return [
        {
            "gate": "current technology compatibility",
            "status": "pass" if buildability.get("current_tech_compatible") else "review",
            "required_evidence": "current buildable records and feasibility score",
            "reason": buildability.get("classification", "feasible_with_validation"),
        },
        {
            "gate": "science fiction filter",
            "status": "pass" if buildability.get("sci_fi_risk") in {"low", "medium"} else "hold",
            "required_evidence": "speculative/future records separated from current buildability",
            "reason": f"sci_fi_risk={buildability.get('sci_fi_risk')}",
        },
        {
            "gate": "live evidence promotion",
            "status": "pass" if live_ready else "hold",
            "required_evidence": "fresh connected/hybrid validation or promoted local source pack",
            "reason": "local preview is not runtime truth until evidence is promoted",
        },
    ]


def build_live_design_portal_workbench(
    *,
    core_output: dict[str, Any] | None = None,
    lifecycle: dict[str, Any] | None = None,
    technology_base: dict[str, Any] | None = None,
) -> dict[str, Any]:
    core_output = core_output or {}
    lifecycle = lifecycle or {}
    technology_base = technology_base or {}
    context = _build_design_context(core_output, technology_base)
    auto_design = AutoDesignEngine().generate(context)
    design_portal = {
        "inputs": {
            "market_gap": context["market_gap"],
            "scores": context["scores"],
            "system_design": auto_design,
            "technology_intelligence": context["technology_intelligence"],
            "domain": context["domain"],
        },
        "market_gap": context["market_gap"],
        "domain": context["domain"],
        "technology_intelligence": context["technology_intelligence"],
    }
    system_design = SystemDesignEngine().generate(design_portal)
    technical_feasibility = TechnicalFeasibilityEngine().analyze(
        text=context["query"],
        domain=_as_text(context.get("domain"), "technology"),
        scores=context["scores"],
        market_gap=context["market_gap"],
        connector_sources=_get(core_output, "source_authority", fallback={}) if isinstance(core_output, dict) else {},
    )
    source_authority = core_output.get("source_authority", {}) if isinstance(core_output, dict) else {}
    buildability = _buildability(technical_feasibility, technology_base, source_authority if isinstance(source_authority, dict) else {})
    architecture = _architecture(system_design)
    required_components = _required_components(system_design, technical_feasibility, technology_base)
    required_systems = _required_systems(system_design, technical_feasibility)
    materials_manifest = _build_materials_manifest(required_components, required_systems, system_design, technical_feasibility, technology_base)
    blueprint_package = _blueprint_package(system_design, buildability, materials_manifest)
    invention_commitment = _invention_commitment(buildability, context, source_authority if isinstance(source_authority, dict) else {})
    downstream_route = _downstream_route_contract(invention_commitment, blueprint_package)
    route_selected = lifecycle.get("route_selected") or core_output.get("route_selected") or ""
    title = _get(core_output, "user_facing_result", "headline", fallback=context["market_gap"].get("solution_class", "Design candidate"))
    blueprint_ready = bool(buildability.get("current_tech_compatible")) and bool(required_components)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "preview_ready" if required_components else "insufficient_design_context",
        "mode": "live_system_design_workbench",
        "candidate": {
            "title": title,
            "route": route_selected,
            "domain": context.get("domain", "technology"),
            "sector": context["market_gap"].get("sector", "general"),
            "source_run_id": core_output.get("run_id") or lifecycle.get("run_id"),
            "summary": _get(core_output, "user_facing_result", "summary", fallback=context["market_gap"].get("needed_solution", "")),
        },
        "runtime_stage": {
            "design_route_activated": "design" in str(route_selected),
            "active_stage_window": "16-22",
            "route_selected": route_selected,
            "operator_interpretation": "design_preview_available_before_blueprint_lock",
        },
        "architecture": architecture,
        "required_components": required_components,
        "required_systems": required_systems,
        "materials_manifest": materials_manifest,
        "blueprint_package": blueprint_package,
        "invention_commitment": invention_commitment,
        "downstream_route_contract": downstream_route,
        "runtime_design_alert": _runtime_design_alert(invention_commitment, buildability, route_selected),
        "portal_actions": _portal_actions(invention_commitment, downstream_route),
        "buildability": buildability,
        "feasibility": {
            "technical_feasibility_score": technical_feasibility.get("technical_feasibility_score", {}),
            "feasibility_classification": technical_feasibility.get("feasibility_classification", {}),
            "architecture_readiness": technical_feasibility.get("architecture_readiness", {}),
            "implementation_complexity": technical_feasibility.get("implementation_complexity", {}),
            "integration_readiness": technical_feasibility.get("integration_readiness", {}),
            "data_readiness": technical_feasibility.get("data_readiness", {}),
            "validation_burden": technical_feasibility.get("validation_burden", {}),
            "deployment_controls": technical_feasibility.get("deployment_controls", {}),
            "technical_risks": technical_feasibility.get("technical_risks", []),
            "prototype_plan": technical_feasibility.get("prototype_plan", {}),
        },
        "technology_basis": {
            "records": _get(technology_base, "counts", "records", fallback=0),
            "current_buildable_records": _get(technology_base, "counts", "current_buildable_records", fallback=0),
            "speculative_or_future_records": _get(technology_base, "counts", "speculative_or_future_records", fallback=0),
            "average_readiness_level": _get(technology_base, "readiness", "average_readiness_level", fallback=0),
            "matched_records": _get(technology_base, "technology_search", "results", fallback=[]),
        },
        "live_design_events": _live_design_events(lifecycle),
        "promotion_gates": _promotion_gates(buildability, source_authority if isinstance(source_authority, dict) else {}),
        "blueprint_readiness": {
            "ready": blueprint_ready,
            "state": "blueprint_candidate" if blueprint_ready else "needs_more_validation",
            "missing_before_blueprint": [] if blueprint_ready else ["component validation", "live evidence promotion"],
        },
        "authority": {
            "network_request_performed": False,
            "runtime_truth_mutation": False,
            "manual_promotion_required": True,
            "dashboard_can_render_preview": True,
            "blueprint_requires_operator_promotion": True,
        },
    }
    payload["validation_chain"] = _validation_chain(payload)
    return payload
