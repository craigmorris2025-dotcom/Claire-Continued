from __future__ import annotations

from typing import Any

from claire.api.s45_cockpit_ui_bridge import (
    S45_VERSION,
    build_cockpit_ui_bridge_manifest,
)


PANEL_GROUPS = {
    "operator": ["operator_payload", "operator_routes", "operator_runtime_status"],
    "evidence": ["operator_evidence_review", "operator_evidence_status"],
    "review": ["operator_review_status", "operator_routes_status"],
}


def build_operator_visible_panel_bindings() -> dict[str, Any]:
    bridge = build_cockpit_ui_bridge_manifest()
    surfaces_by_id = {
        surface["surface_id"]: surface
        for surface in bridge["bridge_surfaces"]
    }

    panels = []
    for group_id, surface_ids in PANEL_GROUPS.items():
        for surface_id in surface_ids:
            surface = surfaces_by_id[surface_id]
            panels.append({
                "panel_id": surface["panel_mount"],
                "surface_id": surface_id,
                "group_id": group_id,
                "title": surface_id.replace("_", " ").title(),
                "fetch_path": surface["fetch_path"],
                "render_mode": surface["render_mode"],
                "response_mode": surface["response_mode"],
                "visible_to_operator": True,
                "presentation_only": True,
                "backend_owns_truth": True,
                "read_only": True,
                "runtime_truth_mutation_allowed": False,
                "operator_mutation_enabled": False,
                "automatic_updates_enabled": False,
                "error_state": "backend_payload_unavailable",
                "empty_state": "waiting_for_backend_payload",
            })

    return {
        "version": S45_VERSION,
        "phase": "S45R3-R4",
        "status": "operator_visible_panel_bindings_ready",
        "panel_count": len(panels),
        "groups": PANEL_GROUPS,
        "panels": panels,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "next_phase": "S45R5-R8 frontend bridge assets",
    }


def verify_operator_visible_panel_bindings() -> dict[str, Any]:
    bindings = build_operator_visible_panel_bindings()
    failures: list[str] = []

    if bindings["panel_count"] != 7:
        failures.append("operator panel count mismatch")

    seen_ids: set[str] = set()
    for panel in bindings["panels"]:
        if panel["panel_id"] in seen_ids:
            failures.append(f"duplicate panel id {panel['panel_id']}")
        seen_ids.add(panel["panel_id"])

        if not panel["visible_to_operator"]:
            failures.append(f"{panel['panel_id']} not visible")
        if not panel["presentation_only"]:
            failures.append(f"{panel['panel_id']} presentation drift")
        if panel["runtime_truth_mutation_allowed"]:
            failures.append(f"{panel['panel_id']} runtime truth mutation drift")
        if panel["operator_mutation_enabled"]:
            failures.append(f"{panel['panel_id']} operator mutation enabled")

    return {
        "version": S45_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "panel_count": bindings["panel_count"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
    }


def build_s45r1_r8_plateau_report() -> dict[str, Any]:
    bindings = build_operator_visible_panel_bindings()
    verification = verify_operator_visible_panel_bindings()
    return {
        "version": S45_VERSION,
        "phase": "S45R7-R8",
        "status": "s45r1_r8_ready" if verification["verification_ok"] else "s45r1_r8_blocked",
        "ready": verification["verification_ok"],
        "bindings": bindings,
        "verification": verification,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "next_phase": "S45R9-R16 cockpit shell bridge integration and panel data mounting",
    }
