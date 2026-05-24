
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

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

SIMULATED_EVIDENCE = [
    {
        "title": "Simulated Source Result",
        "url": "https://example.com/simulated",
        "classification": "simulated_read_only_result",
        "trust": "official",
    }
]

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _false_execution_state() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}

def assert_dry_run_simulator_non_executing(report: Mapping[str, Any]) -> bool:
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
        raise AssertionError("network_call_performed must remain false")

    return True

def simulate_governed_read_only_web_request(
    request: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    raw = dict(request or {})
    eligibility = evaluate_read_only_dry_run_eligibility(raw)
    eligible = bool(eligibility.get("eligible_for_future_read_only_live_web_dry_run"))

    simulated_steps: List[str] = [
        "request_received",
        "provider_validated",
        "allowlist_validated",
        "rate_limit_policy_checked",
        "source_trust_checked",
        "operator_review_checked",
        "confirmation_text_checked",
        "simulation_completed",
    ]

    evidence_packets: List[Dict[str, Any]] = []
    if eligible:
        evidence_packets = list(SIMULATED_EVIDENCE)

    report = {
        "build": "v18.17.1",
        "created_at": _utc_now(),
        "simulation": "governed_read_only_live_web_dry_run",
        "eligible_for_future_read_only_live_web_dry_run": eligible,
        "eligibility": eligibility,
        "simulated_steps": simulated_steps,
        "simulated_evidence_packets": evidence_packets,
        "simulated_result_count": len(evidence_packets),
        "simulation_only": True,
        "network_call_performed": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
        "execution_state": _false_execution_state(),
        "safety_state": {
            "simulation_only": True,
            "approval_equals_execution": False,
            "read_only_future_path": True,
            "live_web_enabled": False,
            "execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "ai_agent_execution_enabled": False,
            "automatic_updates_enabled": False,
        },
        "messages": [
            "simulation_completed",
            "no_network_call_performed",
            "live_web_remains_disabled",
            "execution_remains_disabled",
            "runtime_truth_mutation_remains_disabled",
            "ai_agent_execution_remains_disabled",
            "automatic_updates_remain_disabled",
        ],
    }

    assert_dry_run_simulator_non_executing(report)
    return report

def build_demo_request() -> Dict[str, Any]:
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
    }

def describe_dry_run_simulator() -> Dict[str, Any]:
    return {
        "build": "v18.17.1",
        "name": "Governed Read-Only Live Web Dry-Run Simulator Repair",
        "simulation_only": True,
        "network_calls_enabled": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
    }
