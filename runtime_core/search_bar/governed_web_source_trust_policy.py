from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping


FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]


TRUST_TIERS = {
    "primary": 100,
    "official": 95,
    "high_reliability": 85,
    "reviewed": 70,
    "unknown": 40,
    "blocked": 0,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _false_execution_state() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}


@dataclass(frozen=True)
class SourceTrustAssessment:
    domain: str
    trust_tier: str
    trust_score: int
    citation_required: bool = True
    evidence_capture_required: bool = True
    operator_review_required: bool = True
    read_only_candidate: bool = False
    reasons: List[str] = field(default_factory=list)
    live_web_enabled: bool = False
    execution_enabled: bool = False
    runtime_truth_mutation_enabled: bool = False
    ai_agent_execution_enabled: bool = False
    automatic_updates_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["execution_state"] = _false_execution_state()
        return data


def assert_source_trust_policy_non_executing(report: Mapping[str, Any]) -> bool:
    execution_state = dict(report.get("execution_state") or {})
    safety_state = dict(report.get("safety_state") or {})

    for field_name in FORBIDDEN_EXECUTION_FIELDS:
        if bool(execution_state.get(field_name)):
            raise AssertionError(f"execution_state.{field_name} must remain false")

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

    return True


def assess_source_trust(
    domain: str,
    *,
    trust_tier: str = "unknown",
    citation_required: bool = True,
    evidence_capture_required: bool = True,
    operator_review_required: bool = True,
) -> Dict[str, Any]:
    normalized_tier = trust_tier if trust_tier in TRUST_TIERS else "unknown"
    trust_score = TRUST_TIERS[normalized_tier]

    reasons: List[str] = []
    if normalized_tier == "blocked":
        reasons.append("source_blocked")
    elif normalized_tier == "unknown":
        reasons.append("source_requires_review")
    else:
        reasons.append("source_trust_policy_assessed")

    if citation_required:
        reasons.append("citation_required")
    if evidence_capture_required:
        reasons.append("evidence_capture_required")
    if operator_review_required:
        reasons.append("operator_review_required")

    read_only_candidate = (
        normalized_tier not in {"blocked", "unknown"}
        and citation_required
        and evidence_capture_required
        and operator_review_required
    )

    assessment = SourceTrustAssessment(
        domain=domain.strip().lower(),
        trust_tier=normalized_tier,
        trust_score=trust_score,
        citation_required=bool(citation_required),
        evidence_capture_required=bool(evidence_capture_required),
        operator_review_required=bool(operator_review_required),
        read_only_candidate=read_only_candidate,
        reasons=reasons + [
            "no_network_call_performed",
            "live_web_remains_disabled",
            "execution_remains_disabled",
            "runtime_truth_mutation_remains_disabled",
            "ai_agent_execution_remains_disabled",
            "automatic_updates_remain_disabled",
        ],
        live_web_enabled=False,
        execution_enabled=False,
        runtime_truth_mutation_enabled=False,
        ai_agent_execution_enabled=False,
        automatic_updates_enabled=False,
    ).to_dict()

    report = {
        "build": "v18.15",
        "created_at": _utc_now(),
        "policy": "governed_web_source_trust",
        **assessment,
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

    assert_source_trust_policy_non_executing(report)
    return report


def describe_source_trust_policy_contract() -> Dict[str, Any]:
    return {
        "build": "v18.15",
        "name": "Governed Web Source Trust Policy Contract",
        "trust_tiers": dict(TRUST_TIERS),
        "network_calls_enabled": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
    }
