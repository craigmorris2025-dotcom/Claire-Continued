from __future__ import annotations

from typing import Any


S51_VERSION = "v19.89.8-S51R1-R8"


ROUTE_OUTPUT_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "route_id": "trend_thesis",
        "title": "Trend / Thesis Output",
        "terminal_state": "trend_thesis_ready",
        "headline": "Trend thesis surface ready for backend-owned evidence.",
        "summary": "Structured trend thesis output with signal context, thesis, confidence, and review state.",
        "required_sections": ["signal_context", "thesis", "confidence", "evidence_requirements", "review_state"],
    },
    {
        "route_id": "portfolio_action",
        "title": "Portfolio Action Output",
        "terminal_state": "portfolio_action_ready",
        "headline": "Portfolio action surface ready for governed recommendations.",
        "summary": "Structured portfolio action output with thesis link, allocation logic, risks, and review state.",
        "required_sections": ["thesis_link", "action_type", "allocation_logic", "risk_notes", "review_state"],
    },
    {
        "route_id": "breakthrough_classification",
        "title": "Breakthrough Classification Output",
        "terminal_state": "breakthrough_classified",
        "headline": "Breakthrough classification surface ready for route-qualified advances.",
        "summary": "Classification output for technological, financial, operational, regulatory, or strategic breakthroughs.",
        "required_sections": ["classification", "why_it_matters", "route_fit", "constraints", "review_state"],
    },
    {
        "route_id": "design_output",
        "title": "Design / AutoDesign Output",
        "terminal_state": "design_output_ready",
        "headline": "Design output surface ready for buildable system concepts.",
        "summary": "Route-aware design output with concept, component map, dependencies, build phases, and validation state.",
        "required_sections": ["concept", "components", "dependencies", "build_phases", "validation_state"],
    },
    {
        "route_id": "acquisition_package",
        "title": "Acquisition Package Output",
        "terminal_state": "acquisition_package_ready",
        "headline": "Acquisition package surface ready for buyer-fit framing.",
        "summary": "Acquisition output with acquirer fit, rationale, moat, evidence requirements, and package status.",
        "required_sections": ["acquirer_fit", "rationale", "moat", "evidence_requirements", "package_status"],
    },
    {
        "route_id": "evidence_review",
        "title": "Evidence Review Output",
        "terminal_state": "manual_review_required",
        "headline": "Evidence review surface ready for quarantined evidence.",
        "summary": "Review output that keeps evidence quarantined until manual promotion.",
        "required_sections": ["evidence_items", "source_lineage", "quarantine_state", "promotion_status", "review_state"],
    },
    {
        "route_id": "governed_web_research",
        "title": "Governed Web Research Output",
        "terminal_state": "controlled_probe_ready",
        "headline": "Governed web research surface ready for controlled operator-triggered probes.",
        "summary": "Web research output surface remains fail-closed, quarantine-first, and manual-promotion-only.",
        "required_sections": ["provider_status", "probe_boundary", "quarantine_state", "body_read_policy", "review_state"],
    },
)


def _base_authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "response_mode": "read_only_artifact",
    }


def build_route_specific_useful_output_surfaces() -> dict[str, Any]:
    surfaces = []
    for definition in ROUTE_OUTPUT_DEFINITIONS:
        surfaces.append({
            **definition,
            **_base_authority(),
            "surface_id": f"s51-{definition['route_id']}",
            "output_state": "surface_ready",
            "confidence": "pending_backend_run",
            "evidence_state": "required_before_runtime_truth",
            "review_state": "operator_review_required",
            "exportable": True,
            "useful_output_ready": True,
            "fabricated_evidence_allowed": False,
        })

    return {
        "version": S51_VERSION,
        "phase": "S51R1-R4",
        "status": "route_specific_useful_output_surfaces_ready",
        "surface_count": len(surfaces),
        "surfaces": surfaces,
        **_base_authority(),
        "next_phase": "S51R5-R8 useful output previews and plateau",
    }


def build_route_output_preview(route_id: str) -> dict[str, Any]:
    surfaces = {
        surface["route_id"]: surface
        for surface in build_route_specific_useful_output_surfaces()["surfaces"]
    }
    if route_id not in surfaces:
        raise KeyError(route_id)

    surface = surfaces[route_id]
    sections = {
        section: {
            "state": "awaiting_backend_run",
            "required": True,
            "runtime_truth_mutation_allowed": False,
        }
        for section in surface["required_sections"]
    }

    return {
        "version": S51_VERSION,
        "phase": "S51R5-R6",
        "status": "route_output_preview_ready",
        "route_id": route_id,
        "surface_id": surface["surface_id"],
        "title": surface["title"],
        "headline": surface["headline"],
        "summary": surface["summary"],
        "terminal_state": surface["terminal_state"],
        "sections": sections,
        "section_count": len(sections),
        "confidence": "pending_backend_run",
        "evidence_state": "required_before_runtime_truth",
        "review_state": "operator_review_required",
        "useful_output_ready": True,
        **_base_authority(),
    }


def build_all_route_output_previews() -> dict[str, Any]:
    previews = [
        build_route_output_preview(definition["route_id"])
        for definition in ROUTE_OUTPUT_DEFINITIONS
    ]
    return {
        "version": S51_VERSION,
        "phase": "S51R5-R6",
        "status": "all_route_output_previews_ready",
        "preview_count": len(previews),
        "previews": previews,
        **_base_authority(),
    }


def verify_route_specific_useful_outputs() -> dict[str, Any]:
    manifest = build_route_specific_useful_output_surfaces()
    previews = build_all_route_output_previews()
    failures: list[str] = []

    if manifest["surface_count"] != 7:
        failures.append("surface count mismatch")
    if previews["preview_count"] != 7:
        failures.append("preview count mismatch")

    seen_route_ids: set[str] = set()
    for surface in manifest["surfaces"]:
        if surface["route_id"] in seen_route_ids:
            failures.append(f"duplicate route {surface['route_id']}")
        seen_route_ids.add(surface["route_id"])
        if not surface["useful_output_ready"]:
            failures.append(f"{surface['route_id']} useful output not ready")
        if surface["runtime_truth_mutation_allowed"]:
            failures.append(f"{surface['route_id']} runtime truth mutation allowed")
        if surface["operator_mutation_enabled"]:
            failures.append(f"{surface['route_id']} operator mutation enabled")
        if surface["fabricated_evidence_allowed"]:
            failures.append(f"{surface['route_id']} fabricated evidence allowed")
        if not surface["required_sections"]:
            failures.append(f"{surface['route_id']} missing required sections")

    return {
        "version": S51_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "surface_count": manifest["surface_count"],
        "preview_count": previews["preview_count"],
        **_base_authority(),
    }


def build_s51r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_route_specific_useful_outputs()
    return {
        "version": S51_VERSION,
        "phase": "S51R7-R8",
        "status": "s51r1_r8_ready" if verification["verification_ok"] else "s51r1_r8_blocked",
        "ready": verification["verification_ok"],
        "surfaces": build_route_specific_useful_output_surfaces(),
        "previews": build_all_route_output_previews(),
        "verification": verification,
        **_base_authority(),
        "next_phase": "S52 useful output quality gate and proof requirements",
    }
