from __future__ import annotations

from typing import Any

from runtime_core.api.s44_cockpit_fetch_verification import verify_cockpit_fetch_contract_responses
from runtime_core.api.s44_cockpit_status_aggregation import build_cockpit_status_aggregation
from runtime_core.api.s46_modern_cockpit_shell_blueprint import build_s46r5_r12_plateau_report


S47_VERSION = "v19.89.8-S47R1-R8"


def build_live_status_zones() -> dict[str, Any]:
    fetch = verify_cockpit_fetch_contract_responses()
    aggregation = build_cockpit_status_aggregation()
    shell_plateau = build_s46r5_r12_plateau_report()

    zones = [
        {
            "zone_id": "system_readiness",
            "label": "System Readiness",
            "state": "ready" if aggregation["ready"] and shell_plateau["ready"] else "blocked",
            "summary": "Cockpit shell and operator surfaces are available.",
            "available_count": aggregation["available_count"],
            "surface_count": aggregation["surface_count"],
        },
        {
            "zone_id": "route_availability",
            "label": "Route Availability",
            "state": "available" if fetch["verification_ok"] else "degraded",
            "summary": "Read-only operator routes verified through cockpit fetch contracts.",
            "available_count": fetch["available_count"],
            "surface_count": fetch["probe_count"],
        },
        {
            "zone_id": "authority",
            "label": "Authority",
            "state": "locked",
            "summary": "Runtime mutation, autonomous execution, automatic updates, and browser execution remain blocked.",
            "available_count": 0,
            "surface_count": 0,
        },
        {
            "zone_id": "governed_web",
            "label": "Governed Web",
            "state": "fail_closed",
            "summary": "Web/provider probes remain controlled, operator-triggered, and quarantine-first.",
            "available_count": 0,
            "surface_count": 0,
        },
        {
            "zone_id": "evidence_review",
            "label": "Evidence Review",
            "state": "manual_review",
            "summary": "Evidence promotion remains manual and quarantined before runtime truth.",
            "available_count": 0,
            "surface_count": 0,
        },
    ]

    normalized_zones = []
    for index, zone in enumerate(zones, start=1):
        normalized_zones.append({
            **zone,
            "render_order": index,
            "visible": True,
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "presentation_only": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_execution_enabled": False,
            "browser_execution_enabled": False,
            "response_mode": "read_only_artifact",
        })

    return {
        "version": S47_VERSION,
        "phase": "S47R1-R4",
        "status": "live_status_zones_ready",
        "zone_count": len(normalized_zones),
        "zones": normalized_zones,
        "source_fetch_status": fetch["status"],
        "source_aggregation_status": aggregation["status"],
        "source_shell_status": shell_plateau["status"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "next_phase": "S47R5-R8 cockpit operator payload aggregation",
    }


def verify_live_status_zones() -> dict[str, Any]:
    payload = build_live_status_zones()
    failures: list[str] = []

    if payload["zone_count"] != 5:
        failures.append("status zone count mismatch")
    for zone in payload["zones"]:
        if not zone["visible"]:
            failures.append(f"{zone['zone_id']} not visible")
        if not zone["presentation_only"]:
            failures.append(f"{zone['zone_id']} presentation drift")
        if zone["runtime_truth_mutation_allowed"]:
            failures.append(f"{zone['zone_id']} runtime truth mutation drift")
        if zone["operator_mutation_enabled"]:
            failures.append(f"{zone['zone_id']} operator mutation enabled")
        if zone["response_mode"] != "read_only_artifact":
            failures.append(f"{zone['zone_id']} response mode drift")

    return {
        "version": S47_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "zone_count": payload["zone_count"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
    }
