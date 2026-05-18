from __future__ import annotations

from typing import Any

from claire.api.s45_panel_data_mounting import probe_panel_data_mounts
from claire.api.s46_modern_cockpit_shell_blueprint import build_modern_cockpit_shell_blueprint
from claire.api.s47_live_status_zones import S47_VERSION, build_live_status_zones, verify_live_status_zones


def build_cockpit_operator_payload() -> dict[str, Any]:
    shell = build_modern_cockpit_shell_blueprint()
    zones = build_live_status_zones()
    panel_probe = probe_panel_data_mounts()

    operator_panels = []
    for result in panel_probe["results"]:
        operator_panels.append({
            "panel_id": result["mount_id"],
            "surface_id": result["surface_id"],
            "fetch_path": result["fetch_path"],
            "state": "available" if result["available"] else "unavailable",
            "status_code": result["status_code"],
            "mounted": result["mounted"],
            "renderable": result["renderable"],
            "response_mode": result["response_mode"],
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "presentation_only": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_execution_enabled": False,
        })

    ready = panel_probe["verification_ok"] and verify_live_status_zones()["verification_ok"]

    return {
        "version": S47_VERSION,
        "phase": "S47R5-R6",
        "status": "cockpit_operator_payload_ready" if ready else "cockpit_operator_payload_blocked",
        "ready": ready,
        "shell": shell,
        "status_zones": zones,
        "operator_panel_count": len(operator_panels),
        "operator_panels": operator_panels,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "failures": list(panel_probe["failures"]),
        "next_phase": "S48 dashboard route and payload browser",
    }


def verify_cockpit_operator_payload() -> dict[str, Any]:
    payload = build_cockpit_operator_payload()
    failures: list[str] = []

    if not payload["ready"]:
        failures.append("operator payload not ready")
    if payload["operator_panel_count"] != 7:
        failures.append("operator panel count mismatch")
    if payload["runtime_truth_mutation_allowed"]:
        failures.append("runtime truth mutation allowed")
    for panel in payload["operator_panels"]:
        if panel["state"] != "available":
            failures.append(f"{panel['panel_id']} unavailable")
        if panel["runtime_truth_mutation_allowed"]:
            failures.append(f"{panel['panel_id']} runtime truth mutation drift")
        if panel["operator_mutation_enabled"]:
            failures.append(f"{panel['panel_id']} operator mutation enabled")

    return {
        "version": S47_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "operator_panel_count": payload["operator_panel_count"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
    }


def build_s47r1_r8_plateau_report() -> dict[str, Any]:
    payload = build_cockpit_operator_payload()
    verification = verify_cockpit_operator_payload()
    return {
        "version": S47_VERSION,
        "phase": "S47R7-R8",
        "status": "s47r1_r8_ready" if verification["verification_ok"] else "s47r1_r8_blocked",
        "ready": verification["verification_ok"],
        "payload": payload,
        "verification": verification,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "next_phase": "S48 dashboard route and payload browser",
    }
