
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

from .governed_web_read_only_dry_run_gate import (
    REQUIRED_CONFIRMATION_TEXT,
    evaluate_read_only_dry_run_eligibility,
)

FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _false_execution_state() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}

def assert_live_adapter_boundary_non_executing(report: Mapping[str, Any]) -> bool:
    execution_state = dict(report.get("execution_state") or {})
    safety_state = dict(report.get("safety_state") or {})

    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        if bool(execution_state.get(field_name)):
            raise AssertionError(f"execution_state.{field_name} must remain false")
        if bool(report.get(field_name)):
            raise AssertionError(f"{field_name} must remain false")

    for field_name in [
        "live_web_enabled",
        "execution_enabled",
        "runtime_truth_mutation_enabled",
        "ai_agent_execution_enabled",
        "automatic_updates_enabled",
    ]:
        if bool(report.get(field_name)):
            raise AssertionError(f"{field_name} must remain false")
        if bool(safety_state.get(field_name)):
            raise AssertionError(f"safety_state.{field_name} must remain false")

    if bool(report.get("network_call_performed")):
        raise AssertionError("network_call_performed must remain false in v18.18")
    return True

class GovernedReadOnlyLiveWebAdapter:
    """
    First live-web adapter boundary.

    v18.18 is intentionally fail-closed:
    - adapter exists
    - eligibility can be evaluated
    - no network call is performed
    - live web is not enabled
    """

    def __init__(self, *, enabled: bool = False) -> None:
        self.enabled = False if enabled else False

    def fetch(self, request: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        raw = dict(request or {})
        eligibility = evaluate_read_only_dry_run_eligibility(raw)
        requested_enable = bool(raw.get("enable_live_web") or raw.get("live_web_enabled") or False)

        report = {
            "build": "v18.18",
            "created_at": _utc_now(),
            "adapter": "governed_read_only_live_web_adapter_boundary",
            "adapter_exists": True,
            "requested_enable_live_web": requested_enable,
            "enable_request_honored": False,
            "eligible_for_future_read_only_live_web_dry_run": bool(
                eligibility.get("eligible_for_future_read_only_live_web_dry_run")
            ),
            "eligibility": eligibility,
            "result": None,
            "network_call_performed": False,
            "live_web_enabled": False,
            "execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "ai_agent_execution_enabled": False,
            "automatic_updates_enabled": False,
            "execution_state": _false_execution_state(),
            "safety_state": {
                "fail_closed": True,
                "approval_equals_execution": False,
                "read_only_future_path": True,
                "live_web_enabled": False,
                "execution_enabled": False,
                "runtime_truth_mutation_enabled": False,
                "ai_agent_execution_enabled": False,
                "automatic_updates_enabled": False,
            },
            "messages": [
                "live_adapter_boundary_created",
                "live_web_enable_request_not_honored",
                "network_call_not_performed",
                "live_web_remains_disabled",
                "execution_remains_disabled",
                "runtime_truth_mutation_remains_disabled",
                "ai_agent_execution_remains_disabled",
                "automatic_updates_remain_disabled",
            ],
        }

        assert_live_adapter_boundary_non_executing(report)
        return report

def build_live_adapter_demo_request() -> Dict[str, Any]:
    return {
        "target": "https://example.com/research",
        "provider": {
            "provider_name": "read_only_web_provider",
            "allowlist": ["https://example.com"],
            "rate_limits": {"per_minute": 5},
            "source_trust_policy": {"minimum_trust": "reviewed"},
            "evidence_capture": {"enabled": True},
            "operator_review_required": True,
        },
        "allowlist": ["example.com"],
        "trust_tier": "official",
        "operator_approved": True,
        "confirmation_text": REQUIRED_CONFIRMATION_TEXT,
        "enable_live_web": True,
    }

def describe_live_adapter_boundary() -> Dict[str, Any]:
    return {
        "build": "v18.18",
        "name": "Governed Read-Only Live Web Adapter Boundary",
        "adapter_exists": True,
        "fail_closed": True,
        "network_calls_enabled": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
    }
