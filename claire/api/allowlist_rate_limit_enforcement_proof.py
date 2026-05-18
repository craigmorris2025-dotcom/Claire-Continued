"""Allowlist and rate-limit enforcement proof.

S33R10 is passive proof only. It defines defaults and exposes readiness.
"""

from __future__ import annotations

from typing import Any, Dict, List


DEFAULT_ALLOWLIST: List[Dict[str, Any]] = [
    {
        "host": "www.googleapis.com",
        "provider": "google_custom_search",
        "metadata_only": True,
        "body_read_allowed": False,
        "browser_allowed": False,
    },
    {
        "host": "serpapi.com",
        "provider": "serpapi",
        "metadata_only": True,
        "body_read_allowed": False,
        "browser_allowed": False,
    },
]

DEFAULT_RATE_LIMIT = {
    "minimum_interval_seconds": 60,
    "burst_allowed": False,
    "max_attempts_per_operator_trigger": 1,
    "continuous_loop_enabled": False,
}


def get_allowlist_rate_limit_enforcement_proof() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R10",
        "status": "allowlist_rate_limit_contract_visible",
        "allowlist_policy_present": True,
        "rate_limit_policy_present": True,
        "allowlist": DEFAULT_ALLOWLIST,
        "rate_limit": DEFAULT_RATE_LIMIT,
        "execution_enabled": False,
        "route_registered": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "manual_promotion_required": True,
        "evidence_quarantine_required": True,
        "next_safe_step": "register metadata-only HEAD probe endpoint only after router proof is approved",
    }
