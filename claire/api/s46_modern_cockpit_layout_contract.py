from __future__ import annotations

from typing import Any

from claire.api.s45_panel_data_mounting import build_s45r9_r16_plateau_report


S46_VERSION = "v19.89.8-S46R1-R4"


LAYOUT_ZONES = (
    {
        "zone_id": "command_status",
        "title": "Command / System Status",
        "purpose": "top-level system readiness, authority, and route status",
    },
    {
        "zone_id": "operator_surfaces",
        "title": "Operator Surfaces",
        "purpose": "runtime, routes, evidence, and review payload cards",
    },
    {
        "zone_id": "evidence_review",
        "title": "Evidence / Review",
        "purpose": "quarantined evidence and manual review state",
    },
    {
        "zone_id": "system_health",
        "title": "System Health",
        "purpose": "read-only health, failures, warnings, and plateau state",
    },
)


def build_modern_cockpit_layout_contract() -> dict[str, Any]:
    plateau = build_s45r9_r16_plateau_report()
    zones = []
    for zone in LAYOUT_ZONES:
        zones.append({
            **zone,
            "visible": True,
            "presentation_only": True,
            "backend_owns_truth": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "automatic_updates_enabled": False,
            "data_source": "backend_read_only_payload",
        })

    return {
        "version": S46_VERSION,
        "phase": "S46R1-R2",
        "status": "modern_cockpit_layout_contract_ready",
        "source_plateau_status": plateau["status"],
        "zone_count": len(zones),
        "zones": zones,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "next_phase": "S46R5-R8 modern cockpit visible shell consolidation",
    }


def verify_modern_cockpit_layout_contract() -> dict[str, Any]:
    contract = build_modern_cockpit_layout_contract()
    failures: list[str] = []
    if contract["zone_count"] != 4:
        failures.append("zone count mismatch")
    for zone in contract["zones"]:
        if not zone["visible"]:
            failures.append(f"{zone['zone_id']} not visible")
        if not zone["presentation_only"]:
            failures.append(f"{zone['zone_id']} presentation drift")
        if zone["runtime_truth_mutation_allowed"]:
            failures.append(f"{zone['zone_id']} runtime truth mutation drift")
        if zone["operator_mutation_enabled"]:
            failures.append(f"{zone['zone_id']} operator mutation enabled")
    return {
        "version": S46_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "zone_count": contract["zone_count"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
    }
