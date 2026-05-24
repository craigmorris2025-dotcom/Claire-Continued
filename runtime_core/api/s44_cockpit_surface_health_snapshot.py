from __future__ import annotations

from typing import Any

from runtime_core.api.s44_cockpit_fetch_verification import (
    S44_R9_R16_VERSION,
    verify_cockpit_fetch_contract_responses,
)
from runtime_core.api.s44_cockpit_status_aggregation import build_cockpit_status_aggregation


def build_cockpit_surface_health_snapshot() -> dict[str, Any]:
    verification = verify_cockpit_fetch_contract_responses()
    surface_health = []

    for result in verification["results"]:
        state = "available" if result["available"] else "unavailable"
        surface_health.append({
            "surface_id": result["surface_id"],
            "path": result["path"],
            "state": state,
            "status_code": result["status_code"],
            "read_only": True,
            "mutating": False,
            "runtime_truth_mutation_allowed": False,
            "response_mode": "read_only_artifact",
        })

    return {
        "version": S44_R9_R16_VERSION,
        "phase": "S44R13-R14",
        "status": "cockpit_surface_health_snapshot_ready",
        "surface_count": len(surface_health),
        "available_count": sum(1 for item in surface_health if item["state"] == "available"),
        "surface_health": surface_health,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "next_phase": "S44R15-R16 cockpit verification plateau report",
    }


def verify_cockpit_surface_health_snapshot() -> dict[str, Any]:
    snapshot = build_cockpit_surface_health_snapshot()
    failures = []
    for item in snapshot["surface_health"]:
        if item["state"] != "available":
            failures.append({"surface_id": item["surface_id"], "state": item["state"]})
        if item["runtime_truth_mutation_allowed"]:
            failures.append({"surface_id": item["surface_id"], "authority": "runtime_truth_mutation_allowed"})
    return {
        "version": S44_R9_R16_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "surface_count": snapshot["surface_count"],
        "available_count": snapshot["available_count"],
    }


def build_s44r9_r16_plateau_report() -> dict[str, Any]:
    aggregation = build_cockpit_status_aggregation()
    snapshot = build_cockpit_surface_health_snapshot()
    snapshot_verification = verify_cockpit_surface_health_snapshot()

    failures: list[Any] = []
    if aggregation["failures"]:
        failures.extend(aggregation["failures"])
    if not snapshot_verification["verification_ok"]:
        failures.extend(snapshot_verification["failures"])

    ready = failures == []

    return {
        "version": S44_R9_R16_VERSION,
        "status": "s44r9_r16_ready" if ready else "s44r9_r16_blocked",
        "ready": ready,
        "phase": "S44R15-R16",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "aggregation": aggregation,
        "snapshot": snapshot,
        "snapshot_verification": snapshot_verification,
        "failures": failures,
        "next_phase": "S45 cockpit UI bridge and operator-visible panel wiring",
    }
