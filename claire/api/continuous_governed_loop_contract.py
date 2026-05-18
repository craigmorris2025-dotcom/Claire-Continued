"""Continuous governed loop contract.

S33R16 prepares the continuous check loop but keeps it disabled by default.
"""

from __future__ import annotations

from typing import Any, Dict


def get_continuous_governed_loop_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S33R16",
        "status": "continuous_loop_contract_visible_disabled",
        "continuous_loop_enabled": False,
        "scheduler_enabled": False,
        "automatic_execution_enabled": False,
        "automatic_updates_enabled": False,
        "operator_trigger_required": True,
        "minimum_interval_seconds": 900,
        "max_checks_per_day": 0,
        "allowed_when_enabled_later": [
            "metadata_only_provider_health_check",
            "allowlist_policy_check",
            "rate_limit_policy_check",
            "quarantine_queue_health_check",
        ],
        "forbidden_even_when_enabled_later": [
            "response_body_read",
            "browser_rendering",
            "autonomous_runtime_mutation",
            "automatic_update_apply",
            "unreviewed_evidence_promotion",
        ],
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
