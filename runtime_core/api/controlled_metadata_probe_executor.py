from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from runtime_core.config.env import env_true, getenv

LOCKED_EXECUTOR_AUTHORITY = {
    "network_body_read": "blocked",
    "browser_execution_authority": "blocked",
    "runtime_authority": "blocked",
    "runtime_truth_mutation": "blocked",
    "autonomous_agent_execution": "blocked",
    "automatic_update_execution": "blocked",
    "uncontrolled_live_web_execution": "blocked",
}

def _env_bool(name: str) -> bool:
    return env_true(name)

def _provider_declared() -> bool:
    return bool(
        getenv("PLATFORM_SEARCH_PROVIDER")
        or getenv("PLATFORM_WEB_PROVIDER")
        or getenv("PLATFORM_PROVIDER_STATUS")
        or getenv("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER")
    )

def build_controlled_metadata_probe_executor_status() -> dict[str, Any]:
    provider_declared = _provider_declared()
    real_provider_allowed = _env_bool("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER")
    head_probe_allowed = _env_bool("PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE")
    metadata_probe_allowed = _env_bool("PLATFORM_ALLOW_CONTROLLED_METADATA_GET")
    executor_authorized = provider_declared and real_provider_allowed and (head_probe_allowed or metadata_probe_allowed)
    if executor_authorized:
        status = "ready_but_not_executed_during_install"
        execution_state = "armed_metadata_only"
    elif provider_declared:
        status = "provider_configured_executor_switch_off"
        execution_state = "blocked_switch_off"
    else:
        status = "blocked_missing_provider_configuration"
        execution_state = "blocked_missing_provider"
    return {
        "version": "v19.89.8-S33R1",
        "status": status,
        "execution_state": execution_state,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "executor_type": "controlled_metadata_only_probe_executor",
        "network_request_performed": False,
        "body_read_performed": False,
        "browser_execution_performed": False,
        "runtime_truth_mutation_performed": False,
        "autonomous_execution_performed": False,
        "automatic_update_performed": False,
        "provider_declared": provider_declared,
        "real_provider_allowed": real_provider_allowed,
        "controlled_head_probe_allowed": head_probe_allowed,
        "controlled_metadata_get_allowed": metadata_probe_allowed,
        "executor_authorized": executor_authorized,
        "authority": dict(LOCKED_EXECUTOR_AUTHORITY),
        "rate_limit_policy": {
            "required": True,
            "default_interval_seconds": 60,
            "burst_allowed": False,
        },
        "allowlist_policy": {
            "required": True,
            "default_allowlist_only": True,
        },
        "quarantine": {
            "required": True,
            "target": "governed_evidence_basket",
            "metadata_only": True,
            "manual_promotion_required": True,
            "runtime_truth_write_allowed": False,
        },
        "next_safe_step": "S33R2 explicit one-shot metadata probe runner" if executor_authorized else "configure provider and explicit controlled probe gates",
    }
