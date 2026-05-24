from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from runtime_core.config.env import env_true, getenv

LOCKED_PROBE_AUTHORITY = {
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

def build_controlled_read_only_provider_probe_gate() -> dict[str, Any]:
    provider_declared = _provider_declared()
    head_probe_allowed = _env_bool("PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE")
    metadata_probe_allowed = _env_bool("PLATFORM_ALLOW_CONTROLLED_METADATA_GET")
    real_provider_allowed = _env_bool("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER")
    explicit_probe_authorized = provider_declared and real_provider_allowed and (head_probe_allowed or metadata_probe_allowed)
    gates = {
        "provider_declared": provider_declared,
        "real_provider_explicitly_allowed": real_provider_allowed,
        "controlled_head_probe_allowed": head_probe_allowed,
        "controlled_metadata_get_allowed": metadata_probe_allowed,
        "read_only_mode": True,
        "body_scraping_blocked": True,
        "browser_execution_blocked": True,
        "runtime_truth_mutation_blocked": True,
        "evidence_quarantine_required": True,
        "manual_promotion_required": True,
        "rate_limit_policy_required": True,
        "allowlist_policy_required": True,
    }
    if explicit_probe_authorized:
        status = "ready_for_s33_metadata_only_probe"
        next_safe_step = "run S33R1 controlled metadata-only probe executor"
    elif provider_declared:
        status = "provider_configured_probe_switch_off"
        next_safe_step = "enable explicit controlled probe switch only when ready"
    else:
        status = "blocked_missing_provider_configuration"
        next_safe_step = "configure provider without enabling live execution"
    return {
        "version": "v19.89.8-S33",
        "status": status,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "network_request_performed": False,
        "probe_type": "metadata_only_gate",
        "body_scraping_performed": False,
        "browser_execution_performed": False,
        "runtime_truth_mutation_performed": False,
        "autonomous_execution_performed": False,
        "automatic_update_performed": False,
        "explicit_probe_authorized": explicit_probe_authorized,
        "gates": gates,
        "authority": dict(LOCKED_PROBE_AUTHORITY),
        "quarantine": {
            "required": True,
            "target": "governed_evidence_basket",
            "manual_promotion_required": True,
            "runtime_truth_write_allowed": False,
        },
        "next_safe_step": next_safe_step,
    }
