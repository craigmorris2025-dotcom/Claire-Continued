from __future__ import annotations

import os
from datetime import datetime
from typing import Any

LOCKED_ENDPOINT_AUTHORITY = {
    "network_body_read": "blocked",
    "browser_execution_authority": "blocked",
    "runtime_authority": "blocked",
    "runtime_truth_mutation": "blocked",
    "autonomous_agent_execution": "blocked",
    "automatic_update_execution": "blocked",
    "uncontrolled_live_web_execution": "blocked",
}

def _env_bool(name: str) -> bool:
    return str(os.getenv(name, "")).strip().lower() in {"1", "true", "yes", "on"}

def _provider_declared() -> bool:
    return bool(
        os.getenv("PLATFORM_SEARCH_PROVIDER")
        or os.getenv("PLATFORM_WEB_PROVIDER")
        or os.getenv("PLATFORM_PROVIDER_STATUS")
        or os.getenv("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER")
    )

def build_operator_triggered_metadata_probe_endpoint_status() -> dict[str, Any]:
    provider_declared = _provider_declared()
    real_provider_allowed = _env_bool("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER")
    head_probe_allowed = _env_bool("PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE")
    metadata_probe_allowed = _env_bool("PLATFORM_ALLOW_CONTROLLED_METADATA_GET")
    one_shot_allowed = _env_bool("PLATFORM_ALLOW_ONE_SHOT_METADATA_PROBE")
    operator_trigger_allowed = _env_bool("PLATFORM_ALLOW_OPERATOR_TRIGGERED_METADATA_PROBE")
    allowlist_ready = _env_bool("PLATFORM_ALLOWLIST_READY") or _env_bool("PLATFORM_SOURCE_ALLOWLIST_READY")
    rate_limit_ready = _env_bool("PLATFORM_RATE_LIMIT_READY") or _env_bool("PLATFORM_RATE_LIMIT_POLICY_READY")
    endpoint_authorized = all([provider_declared, real_provider_allowed, one_shot_allowed, operator_trigger_allowed, allowlist_ready, rate_limit_ready, (head_probe_allowed or metadata_probe_allowed)])
    if endpoint_authorized:
        status = "ready_for_operator_triggered_metadata_probe_endpoint"
        endpoint_state = "armed_waiting_for_operator_request"
    elif provider_declared:
        status = "blocked_missing_operator_trigger_or_policy_gates"
        endpoint_state = "blocked_gates_incomplete"
    else:
        status = "blocked_missing_provider_configuration"
        endpoint_state = "blocked_missing_provider"
    gates = {
        "provider_declared": provider_declared,
        "real_provider_allowed": real_provider_allowed,
        "controlled_head_probe_allowed": head_probe_allowed,
        "controlled_metadata_get_allowed": metadata_probe_allowed,
        "one_shot_metadata_probe_allowed": one_shot_allowed,
        "operator_trigger_allowed": operator_trigger_allowed,
        "allowlist_ready": allowlist_ready,
        "rate_limit_ready": rate_limit_ready,
        "body_read_blocked": True,
        "browser_execution_blocked": True,
        "runtime_truth_mutation_blocked": True,
        "manual_promotion_required": True,
    }
    return {
        "version": "v19.89.8-S33R3",
        "status": status,
        "endpoint_state": endpoint_state,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "endpoint_type": "operator_triggered_one_shot_metadata_probe_endpoint",
        "network_request_performed_during_install": False,
        "endpoint_registered_with_app": False,
        "body_read_performed": False,
        "browser_execution_performed": False,
        "runtime_truth_mutation_performed": False,
        "autonomous_execution_performed": False,
        "automatic_update_performed": False,
        "endpoint_authorized": endpoint_authorized,
        "gates": gates,
        "method_policy": {
            "allowed_methods": ["HEAD"],
            "metadata_get_allowed_only_when_explicit": metadata_probe_allowed,
            "response_body_allowed": False,
        },
        "allowed_capture_fields": ["status_code", "response_headers", "content_type", "server", "date", "elapsed_ms", "final_url", "redirect_count"],
        "forbidden_capture_fields": ["response_body", "rendered_dom", "browser_screenshot", "script_execution", "runtime_truth_write"],
        "authority": dict(LOCKED_ENDPOINT_AUTHORITY),
        "quarantine": {
            "required": True,
            "target": "governed_evidence_basket",
            "metadata_only": True,
            "manual_promotion_required": True,
            "runtime_truth_write_allowed": False,
        },
        "next_safe_step": "S33R4 register guarded operator endpoint after route-level auth design" if endpoint_authorized else "complete provider, allowlist, rate-limit, one-shot, and operator-trigger gates",
    }
