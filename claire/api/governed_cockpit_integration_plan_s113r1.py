from __future__ import annotations

from typing import Any, Dict, List

from claire.api.governed_cockpit_stop_gate_s112r1 import build_cockpit_artifact_stop_gate

INTEGRATION_STEPS = [
    {
        "step": 1,
        "id": "preview_payload_registry",
        "action": "register unified cockpit preview as read-only payload fragment",
        "allowed_now": True,
        "writes_runtime_truth": False,
        "patches_app": False,
        "rewires_live_dashboard": False,
    },
    {
        "step": 2,
        "id": "cockpit_fetch_map_preview",
        "action": "expose preview fetch-map contract for cockpit consumption",
        "allowed_now": True,
        "writes_runtime_truth": False,
        "patches_app": False,
        "rewires_live_dashboard": False,
    },
    {
        "step": 3,
        "id": "live_dashboard_attachment_gate",
        "action": "prepare gated attachment decision for live cockpit",
        "allowed_now": False,
        "requires_stop_gate": "S114R1",
        "writes_runtime_truth": False,
        "patches_app": False,
        "rewires_live_dashboard": False,
    },
    {
        "step": 4,
        "id": "direct_app_patch",
        "action": "direct app.py/main.py patching",
        "allowed_now": False,
        "blocked": True,
        "writes_runtime_truth": False,
        "patches_app": True,
        "rewires_live_dashboard": False,
    },
]

def build_controlled_cockpit_integration_plan() -> Dict[str, Any]:
    stop_gate = build_cockpit_artifact_stop_gate()
    checks = {
        "s112_stop_gate_ok": stop_gate.get("ok") is True,
        "no_direct_app_patch": all(not step.get("allowed_now") for step in INTEGRATION_STEPS if step.get("patches_app")),
        "no_live_rewire_yet": all(step.get("rewires_live_dashboard") is False for step in INTEGRATION_STEPS),
        "no_runtime_truth_write": all(step.get("writes_runtime_truth") is False for step in INTEGRATION_STEPS),
    }
    ok = all(checks.values())
    return {
        "integration_plan_version": "S113R1",
        "status": "controlled_integration_plan_ready" if ok else "controlled_integration_plan_blocked",
        "ok": ok,
        "purpose": "Define safe cockpit integration steps before touching live dashboard wiring.",
        "checks": checks,
        "steps": INTEGRATION_STEPS,
        "allowed_current_actions": [step for step in INTEGRATION_STEPS if step.get("allowed_now") is True],
        "blocked_actions": [step for step in INTEGRATION_STEPS if step.get("allowed_now") is False],
        "locks": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_truth_write_blocked": True,
            "runtime_truth_mutation_blocked": True,
            "automatic_updates_blocked": True,
            "autonomous_execution_blocked": True,
        },
        "next_safe_step": "S114R1 read-only preview payload registry module",
    }

def validate_controlled_cockpit_integration_plan() -> Dict[str, Any]:
    plan = build_controlled_cockpit_integration_plan()
    allowed = plan["allowed_current_actions"]
    blocked = plan["blocked_actions"]
    checks = {
        "plan_ok": plan.get("ok") is True,
        "has_allowed_preview_actions": len(allowed) >= 1,
        "has_blocked_live_attachment_gate": any(step.get("id") == "live_dashboard_attachment_gate" for step in blocked),
        "direct_app_patch_blocked": any(step.get("id") == "direct_app_patch" and step.get("blocked") is True for step in blocked),
        "next_step_correct": plan.get("next_safe_step") == "S114R1 read-only preview payload registry module",
    }
    return {
        "validation_version": "S113R1",
        "status": "passed" if all(checks.values()) else "failed",
        "ok": all(checks.values()),
        "checks": checks,
        "plan": plan,
    }
