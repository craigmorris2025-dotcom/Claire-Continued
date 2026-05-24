"""Safe mounted-router comparator for guarded metadata endpoint.

S34R4 compares discovered routers against the explicit allowlist contract.
It does not patch app.py or register any endpoint.
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_core.api.mounted_router_proof_audit import get_mounted_router_proof_audit
from runtime_core.api.safe_router_allowlist_contract import get_safe_router_allowlist_contract


def _allowed_router_imports() -> List[str]:
    contract = get_safe_router_allowlist_contract()
    allowed: List[str] = []
    for item in contract.get("safe_router_allowlist", []):
        if item.get("guarded_registration_allowed") is True:
            router_import = item.get("router_import")
            if router_import:
                allowed.append(router_import)
    return allowed


def get_safe_mounted_router_comparator() -> Dict[str, Any]:
    audit = get_mounted_router_proof_audit()
    allowed = _allowed_router_imports()

    candidates = []
    proof = audit.get("proof", {})
    for candidate in proof.get("candidate_matches", []):
        include_call = candidate.get("include_call", {})
        router_import = include_call.get("router_import") or include_call.get("router_expression")
        candidates.append(
            {
                "router_import_or_expression": router_import,
                "allowed_for_guarded_registration": router_import in allowed,
                "include_call": include_call,
            }
        )

    safe_router_approved = any(item["allowed_for_guarded_registration"] for item in candidates)

    return {
        "version": "v19.89.8-S34R4",
        "status": "safe_router_approved" if safe_router_approved else "blocked_no_approved_safe_router",
        "safe_router_approved": safe_router_approved,
        "approved_router_imports": allowed,
        "candidate_results": candidates,
        "route_registration_allowed": safe_router_approved,
        "app_py_patch_allowed": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "reason": (
            "No guarded endpoint may be registered unless a mounted router matches "
            "an explicit allowlist entry with guarded_registration_allowed=true."
        ),
    }
