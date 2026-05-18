from __future__ import annotations
from typing import Any

S72_VERSION = "v19.89.8-S72R1-R8"

def _authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_write_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
    }

def build_run_output_operator_review_bridge() -> dict[str, Any]:
    bridge_items = []
    for route in ("trend_thesis","portfolio_action","breakthrough_classification","design_output","acquisition_package"):
        bridge_items.append({
            "bridge_id": f"s72-{route}",
            "route_id": route,
            "review_surface": f"review-{route}",
            "state": "ready_for_operator_review",
            "auto_approval_enabled": False,
            "runtime_truth_write_allowed": False,
            **_authority(),
        })
    return {
        "version": S72_VERSION,
        "status": "run_output_operator_review_bridge_ready",
        "bridge_count": len(bridge_items),
        "bridge_items": bridge_items,
        **_authority(),
        "next_phase": "S73 useful run package composer",
    }

def verify_run_output_operator_review_bridge() -> dict[str, Any]:
    payload = build_run_output_operator_review_bridge()
    failures = []
    if payload["bridge_count"] != 5:
        failures.append("bridge count mismatch")
    for item in payload["bridge_items"]:
        if item["auto_approval_enabled"]:
            failures.append(item["bridge_id"] + " auto approval")
        if item["runtime_truth_write_allowed"]:
            failures.append(item["bridge_id"] + " writes truth")
    return {"verification_ok": failures == [], "failures": failures, **_authority()}

def build_s72r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_run_output_operator_review_bridge()
    return {
        "version": S72_VERSION,
        "status": "s72r1_r8_ready" if verification["verification_ok"] else "s72r1_r8_blocked",
        "ready": verification["verification_ok"],
        "bridge": build_run_output_operator_review_bridge(),
        "verification": verification,
        **_authority(),
        "next_phase": "S73 useful run package composer",
    }
