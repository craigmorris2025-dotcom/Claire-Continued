from __future__ import annotations
from typing import Any

S71_VERSION = "v19.89.8-S71R1-R8"

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
        "scheduled_updates_enabled": False,
    }

def build_governed_continuous_runtime_observation() -> dict[str, Any]:
    observers = []
    for name in ("system_health","route_state","output_state","evidence_state","provider_state","dashboard_state"):
        observers.append({
            "observer_id": f"s71-{name}",
            "observation_mode": "read_only_snapshot",
            "continuous_execution_enabled": False,
            "scheduled_execution_enabled": False,
            "writes_runtime_truth": False,
            "operator_visible": True,
            **_authority(),
        })
    return {
        "version": S71_VERSION,
        "status": "governed_continuous_runtime_observation_ready",
        "observer_count": len(observers),
        "observers": observers,
        **_authority(),
        "next_phase": "S72 run output bridge to operator review",
    }

def verify_governed_continuous_runtime_observation() -> dict[str, Any]:
    payload = build_governed_continuous_runtime_observation()
    failures = []
    if payload["observer_count"] != 6:
        failures.append("observer count mismatch")
    for item in payload["observers"]:
        if item["continuous_execution_enabled"]:
            failures.append(item["observer_id"] + " continuous execution enabled")
        if item["scheduled_execution_enabled"]:
            failures.append(item["observer_id"] + " scheduled execution enabled")
        if item["writes_runtime_truth"]:
            failures.append(item["observer_id"] + " writes truth")
    return {"verification_ok": failures == [], "failures": failures, **_authority()}

def build_s71r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_governed_continuous_runtime_observation()
    return {
        "version": S71_VERSION,
        "status": "s71r1_r8_ready" if verification["verification_ok"] else "s71r1_r8_blocked",
        "ready": verification["verification_ok"],
        "observation": build_governed_continuous_runtime_observation(),
        "verification": verification,
        **_authority(),
        "next_phase": "S72 run output bridge to operator review",
    }
