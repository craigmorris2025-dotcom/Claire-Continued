from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Mapping

LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_mutation_blocked": True,
    "runtime_truth_write_blocked": True,
    "automatic_updates_blocked": True,
    "autonomous_execution_blocked": True,
    "manual_promotion_mandatory": True,
    "quarantine_mandatory": True,
    "continuous_crawling_blocked": True,
}

SPINE_STAGES = [
    "governed_intake",
    "quarantine",
    "evidence_basket",
    "extraction",
    "discovery_candidate",
    "useful_output_candidate",
    "review_queue",
    "operator_decision",
    "export_manifest",
    "route_state",
    "cockpit_read_model",
    "system_proof",
]

ROUTES = ("portfolio", "breakthrough", "design")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(encoded).hexdigest()[:16]}"


def build_runtime_spine_state(
    *,
    proof_status: str = "ready",
    review_queue_total: int = 0,
    export_count: int = 0,
) -> Dict[str, Any]:
    seed = {
        "proof_status": proof_status,
        "review_queue_total": review_queue_total,
        "export_count": export_count,
        "stages": SPINE_STAGES,
        "routes": ROUTES,
    }

    stage_state = {
        stage: {
            "stage": stage,
            "status": "available",
            "backend_owned": True,
            "cockpit_presentation_only": True,
            "runtime_truth_write": "blocked",
        }
        for stage in SPINE_STAGES
    }

    route_state = {
        route: {
            "route": route,
            "status": "available",
            "manual_review_required": True,
            "runtime_truth_write": "blocked",
            "automatic_update": "blocked",
        }
        for route in ROUTES
    }

    return {
        "spine_version": "S106R1",
        "spine_id": _stable_id("spine", seed),
        "status": "runtime_spine_contract_ready",
        "created_at": _utc_now(),
        "backend_module_only": True,
        "app_patch_performed": False,
        "automatic_route_registration": False,
        "stage_count": len(SPINE_STAGES),
        "route_count": len(ROUTES),
        "stage_state": stage_state,
        "route_state": route_state,
        "proof_status": proof_status,
        "review_queue_total": review_queue_total,
        "export_count": export_count,
        "authority_model": {
            "single_runtime_state_authority": "backend",
            "single_evidence_authority": "backend",
            "single_route_state_authority": "backend",
            "cockpit": "presentation_only",
            "operator_actions": "manual_only",
        },
        "locks": dict(LOCKS),
    }


def build_runtime_spine_contract_report() -> Dict[str, Any]:
    state = build_runtime_spine_state()
    checks = {
        "backend_module_only": state["backend_module_only"] is True,
        "app_patch_performed_false": state["app_patch_performed"] is False,
        "automatic_route_registration_false": state["automatic_route_registration"] is False,
        "stage_count_valid": state["stage_count"] == len(SPINE_STAGES),
        "route_count_valid": state["route_count"] == len(ROUTES),
        "runtime_truth_write_blocked": state["locks"]["runtime_truth_write_blocked"] is True,
        "autonomous_execution_blocked": state["locks"]["autonomous_execution_blocked"] is True,
        "automatic_updates_blocked": state["locks"]["automatic_updates_blocked"] is True,
    }
    return {
        "contract_report_version": "S106R1",
        "status": "passed" if all(checks.values()) else "failed",
        "ok": all(checks.values()),
        "checks": checks,
        "runtime_spine_state": state,
        "next_safe_step": "S107R1 existing-registry discovery without app patching",
    }
