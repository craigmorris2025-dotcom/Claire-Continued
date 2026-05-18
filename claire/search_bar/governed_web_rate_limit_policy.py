from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping


FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]


DEFAULT_REQUESTS_PER_MINUTE = 5
DEFAULT_REQUESTS_PER_HOUR = 60
DEFAULT_COOLDOWN_SECONDS = 30


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _false_execution_state() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}


@dataclass(frozen=True)
class GovernedRateLimitPolicy:
    requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE
    requests_per_hour: int = DEFAULT_REQUESTS_PER_HOUR
    cooldown_seconds: int = DEFAULT_COOLDOWN_SECONDS
    operator_review_required: bool = True
    live_web_enabled: bool = False
    execution_enabled: bool = False
    runtime_truth_mutation_enabled: bool = False
    ai_agent_execution_enabled: bool = False
    automatic_updates_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["execution_state"] = _false_execution_state()
        return data


def assert_rate_limit_policy_non_executing(report: Mapping[str, Any]) -> bool:
    execution_state = dict(report.get("execution_state") or {})
    safety_state = dict(report.get("safety_state") or {})

    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        if bool(execution_state.get(field_name)):
            raise AssertionError(f"execution_state.{field_name} must remain false")

    if bool(report.get("live_web_enabled")):
        raise AssertionError("live_web_enabled must remain false")
    if bool(report.get("execution_enabled")):
        raise AssertionError("execution_enabled must remain false")
    if bool(report.get("runtime_truth_mutation_enabled")):
        raise AssertionError("runtime_truth_mutation_enabled must remain false")
    if bool(report.get("ai_agent_execution_enabled")):
        raise AssertionError("ai_agent_execution_enabled must remain false")
    if bool(report.get("automatic_updates_enabled")):
        raise AssertionError("automatic_updates_enabled must remain false")

    if bool(safety_state.get("live_web_enabled")):
        raise AssertionError("safety_state.live_web_enabled must remain false")
    if bool(safety_state.get("execution_enabled")):
        raise AssertionError("safety_state.execution_enabled must remain false")
    if bool(safety_state.get("runtime_truth_mutation_enabled")):
        raise AssertionError("safety_state.runtime_truth_mutation_enabled must remain false")
    if bool(safety_state.get("ai_agent_execution_enabled")):
        raise AssertionError("safety_state.ai_agent_execution_enabled must remain false")
    if bool(safety_state.get("automatic_updates_enabled")):
        raise AssertionError("safety_state.automatic_updates_enabled must remain false")

    return True


def build_rate_limit_policy(
    *,
    requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE,
    requests_per_hour: int = DEFAULT_REQUESTS_PER_HOUR,
    cooldown_seconds: int = DEFAULT_COOLDOWN_SECONDS,
    operator_review_required: bool = True,
) -> Dict[str, Any]:
    policy = GovernedRateLimitPolicy(
        requests_per_minute=max(1, int(requests_per_minute)),
        requests_per_hour=max(1, int(requests_per_hour)),
        cooldown_seconds=max(0, int(cooldown_seconds)),
        operator_review_required=bool(operator_review_required),
        live_web_enabled=False,
        execution_enabled=False,
        runtime_truth_mutation_enabled=False,
        ai_agent_execution_enabled=False,
        automatic_updates_enabled=False,
    ).to_dict()

    report = {
        "build": "v18.14",
        "created_at": _utc_now(),
        "policy": "governed_web_rate_limit",
        **policy,
        "network_call_performed": False,
        "safety_state": {
            "operator_review_required": bool(operator_review_required),
            "read_only_future_path": True,
            "live_web_enabled": False,
            "execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "ai_agent_execution_enabled": False,
            "automatic_updates_enabled": False,
        },
        "messages": [
            "rate_limit_policy_ready",
            "no_network_call_performed",
            "live_web_remains_disabled",
            "execution_remains_disabled",
        ],
    }

    assert_rate_limit_policy_non_executing(report)
    return report


def describe_rate_limit_policy_contract() -> Dict[str, Any]:
    return {
        "build": "v18.14",
        "name": "Governed Web Rate Limit Policy Contract",
        "default_requests_per_minute": DEFAULT_REQUESTS_PER_MINUTE,
        "default_requests_per_hour": DEFAULT_REQUESTS_PER_HOUR,
        "default_cooldown_seconds": DEFAULT_COOLDOWN_SECONDS,
        "network_calls_enabled": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
    }
