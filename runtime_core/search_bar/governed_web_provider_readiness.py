from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]


REQUIRED_PROVIDER_GATES = [
    "provider_declared",
    "allowlist_declared",
    "rate_limits_declared",
    "source_trust_policy_declared",
    "evidence_capture_declared",
    "operator_review_required",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _false_execution_state() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}


@dataclass(frozen=True)
class GovernedWebProviderReadiness:
    provider_name: str
    provider_type: str = "future_live_web_adapter"
    provider_declared: bool = False
    allowlist_declared: bool = False
    rate_limits_declared: bool = False
    source_trust_policy_declared: bool = False
    evidence_capture_declared: bool = False
    operator_review_required: bool = True
    ready_for_live_web: bool = False
    live_web_enabled: bool = False
    execution_enabled: bool = False
    runtime_truth_mutation_enabled: bool = False
    ai_agent_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["execution_state"] = _false_execution_state()
        return data


def assert_provider_readiness_non_executing(report: Mapping[str, Any]) -> bool:
    execution_state = dict(report.get("execution_state") or {})

    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        if bool(execution_state.get(field_name)):
            raise AssertionError(f"execution_state.{field_name} must remain false")
        if bool(report.get(field_name)):
            raise AssertionError(f"{field_name} must remain false")

    if bool(report.get("live_web_enabled")):
        raise AssertionError("live_web_enabled must remain false in v18.12")
    if bool(report.get("execution_enabled")):
        raise AssertionError("execution_enabled must remain false")
    if bool(report.get("runtime_truth_mutation_enabled")):
        raise AssertionError("runtime_truth_mutation_enabled must remain false")
    if bool(report.get("ai_agent_execution_enabled")):
        raise AssertionError("ai_agent_execution_enabled must remain false")
    if bool(report.get("automatic_updates_enabled")):
        raise AssertionError("automatic_updates_enabled must remain false")
    return True


def evaluate_provider_readiness(provider: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluate future provider readiness without performing network calls.

    ready_for_live_web means the provider contract is complete enough for a
    later read-only dry-run build. It does NOT enable live web.
    """
    raw = dict(provider or {})
    provider_name = str(raw.get("provider_name") or raw.get("name") or "undeclared_provider")
    provider_type = str(raw.get("provider_type") or "future_live_web_adapter")

    flags = {
        "provider_declared": provider_name != "undeclared_provider",
        "allowlist_declared": bool(raw.get("allowlist") or raw.get("allowlist_declared")),
        "rate_limits_declared": bool(raw.get("rate_limits") or raw.get("rate_limits_declared")),
        "source_trust_policy_declared": bool(raw.get("source_trust_policy") or raw.get("source_trust_policy_declared")),
        "evidence_capture_declared": bool(raw.get("evidence_capture") or raw.get("evidence_capture_declared")),
        "operator_review_required": bool(raw.get("operator_review_required", True)),
    }

    missing = [gate for gate in REQUIRED_PROVIDER_GATES if not flags.get(gate)]
    contract_ready = len(missing) == 0

    reasons: List[str] = []
    if contract_ready:
        reasons.append("provider_contract_ready_for_future_read_only_dry_run")
    else:
        reasons.extend([f"missing_{gate}" for gate in missing])

    reasons.extend(
        [
            "no_network_call_performed",
            "live_web_remains_disabled",
            "execution_remains_disabled",
            "runtime_truth_mutation_remains_disabled",
            "ai_agent_execution_remains_disabled",
            "automatic_updates_remain_disabled",
        ]
    )

    readiness = GovernedWebProviderReadiness(
        provider_name=provider_name,
        provider_type=provider_type,
        provider_declared=flags["provider_declared"],
        allowlist_declared=flags["allowlist_declared"],
        rate_limits_declared=flags["rate_limits_declared"],
        source_trust_policy_declared=flags["source_trust_policy_declared"],
        evidence_capture_declared=flags["evidence_capture_declared"],
        operator_review_required=flags["operator_review_required"],
        ready_for_live_web=contract_ready,
        live_web_enabled=False,
        execution_enabled=False,
        runtime_truth_mutation_enabled=False,
        ai_agent_execution_enabled=False,
        automatic_updates_enabled=False,
        reasons=reasons,
    ).to_dict()

    report = {
        "build": "v18.12",
        "created_at": _utc_now(),
        "contract": "governed_web_provider_readiness",
        **readiness,
        "network_call_performed": False,
        "safety_state": {
            "read_only_future_path": True,
            "live_web_enabled": False,
            "execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "ai_agent_execution_enabled": False,
            "automatic_updates_enabled": False,
            "operator_review_required": True,
        },
    }

    assert_provider_readiness_non_executing(report)
    return report


def describe_provider_readiness_contract() -> Dict[str, Any]:
    return {
        "build": "v18.12",
        "name": "Governed Web Provider Readiness Contract",
        "required_gates": list(REQUIRED_PROVIDER_GATES),
        "network_calls_enabled": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
    }
