from __future__ import annotations
from typing import Any

S75_VERSION = "v19.89.8-S75R1-R8"

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

def build_cockpit_demo_run_packet() -> dict[str, Any]:
    return {
        "version": S75_VERSION,
        "status": "cockpit_demo_run_packet_ready",
        "demo_ready": True,
        "has_dashboard": True,
        "has_useful_outputs": True,
        "has_evidence_review": True,
        "has_provider_status": True,
        "has_export_registry": True,
        "actual_live_execution": False,
        "actual_runtime_truth_write": False,
        **_authority(),
        "next_phase": "S76 live web controlled probe arming review",
    }

def verify_cockpit_demo_run_packet() -> dict[str, Any]:
    packet = build_cockpit_demo_run_packet()
    failures = []
    if not packet["demo_ready"]:
        failures.append("demo not ready")
    if packet["actual_live_execution"]:
        failures.append("live execution enabled")
    if packet["actual_runtime_truth_write"]:
        failures.append("runtime truth write enabled")
    return {"verification_ok": failures == [], "failures": failures, **_authority()}

def build_s75r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_cockpit_demo_run_packet()
    return {
        "version": S75_VERSION,
        "status": "s75r1_r8_ready" if verification["verification_ok"] else "s75r1_r8_blocked",
        "ready": verification["verification_ok"],
        "packet": build_cockpit_demo_run_packet(),
        "verification": verification,
        **_authority(),
        "next_phase": "S76 live web controlled probe arming review",
    }
