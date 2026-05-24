"""Explicit safe-router allowlist proof contract.

S33R7 is passive-only governance state.
No route registration.
No network execution.
No response body reads.
No browser execution.
No runtime truth mutation.
No autonomous execution.
No automatic updates.
"""

from __future__ import annotations

from typing import Any, Dict, List


SAFE_ROUTER_ALLOWLIST: List[Dict[str, Any]] = [
    {
        "router_import": "runtime_core.api.dashboard_payload_bridge.router",
        "classification": "presentation_payload_only",
        "guarded_registration_allowed": False,
        "reason": (
            "Payload presentation router is not yet approved for guarded "
            "metadata probe registration."
        ),
    },
    {
        "router_import": "runtime_core.api.governed_payload_reconciliation",
        "classification": "payload_composition_only",
        "guarded_registration_allowed": False,
        "reason": (
            "Payload composition modules are not executable route surfaces."
        ),
    },
]


def get_safe_router_allowlist_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R7",
        "status": "safe_router_allowlist_visible",
        "route_registered": False,
        "endpoint_registration_allowed": False,
        "allowlist_active": True,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "manual_promotion_required": True,
        "evidence_quarantine_required": True,
        "safe_router_allowlist": SAFE_ROUTER_ALLOWLIST,
        "allowlist_policy": (
            "Only explicitly governed routers may ever become candidates for "
            "guarded registration. S33R7 still approves none."
        ),
        "next_allowed_step": (
            "Future builds may compare mounted_router_proof_audit results "
            "against this allowlist contract, while remaining fail-closed."
        ),
    }
