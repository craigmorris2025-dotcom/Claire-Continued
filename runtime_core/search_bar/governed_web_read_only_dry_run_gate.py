from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

try:
    from .governed_web_provider_readiness import evaluate_provider_readiness
except Exception:
    evaluate_provider_readiness = None

try:
    from .governed_web_rate_limit_policy import build_rate_limit_policy
except Exception:
    build_rate_limit_policy = None

try:
    from .governed_web_source_trust_policy import assess_source_trust
except Exception:
    assess_source_trust = None


FORBIDDEN_EXECUTION_FIELDS = [
    "execution_performed",
    "live_web_execution_performed",
    "runtime_truth_mutated",
    "autonomous_agent_execution_performed",
    "automatic_update_performed",
]


REQUIRED_CONFIRMATION_TEXT = "I understand this is a read-only live web dry-run eligibility review only"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _false_execution_state() -> Dict[str, bool]:
    return {field_name: False for field_name in FORBIDDEN_EXECUTION_FIELDS}


def _domain_from_url_or_domain(value: str) -> str:
    cleaned = (value or "").strip().lower()
    cleaned = cleaned.replace("https://", "").replace("http://", "")
    cleaned = cleaned.split("/", 1)[0]
    return cleaned


def assert_read_only_dry_run_gate_non_executing(report: Mapping[str, Any]) -> bool:
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
        raise AssertionError("network_call_performed must remain false in v18.16")

    return True


def evaluate_read_only_dry_run_eligibility(request: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    raw = dict(request or {})
    target = str(raw.get("target") or raw.get("url") or raw.get("domain") or "")
    domain = _domain_from_url_or_domain(target)

    provider = dict(raw.get("provider") or {})
    allowlist = [str(item).strip().lower() for item in raw.get("allowlist", [])]
    trust_tier = str(raw.get("trust_tier") or "unknown")
    confirmation_text = str(raw.get("confirmation_text") or "").strip()
    operator_approved = bool(raw.get("operator_approved") or raw.get("approval_recorded") or False)

    provider_report = (
        evaluate_provider_readiness(provider)
        if evaluate_provider_readiness is not None
        else {"ready_for_live_web": False, "reasons": ["provider_readiness_module_missing"]}
    )

    rate_policy = (
        build_rate_limit_policy(**dict(raw.get("rate_limits") or {}))
        if build_rate_limit_policy is not None
        else {"requests_per_minute": 0, "requests_per_hour": 0, "reasons": ["rate_limit_module_missing"]}
    )

    source_trust = (
        assess_source_trust(domain or "unknown-domain", trust_tier=trust_tier)
        if assess_source_trust is not None
        else {"read_only_candidate": False, "reasons": ["source_trust_module_missing"]}
    )

    allowlist_match = bool(domain and domain in allowlist)
    confirmation_valid = confirmation_text == REQUIRED_CONFIRMATION_TEXT

    reasons: List[str] = []
    if not domain:
        reasons.append("target_domain_missing")
    if not bool(provider_report.get("ready_for_live_web")):
        reasons.append("provider_not_ready_for_future_dry_run")
    if not allowlist_match:
        reasons.append("target_not_in_allowlist")
    if not bool(source_trust.get("read_only_candidate")):
        reasons.append("source_not_read_only_candidate")
    if not operator_approved:
        reasons.append("operator_approval_missing")
    if not confirmation_text:
        reasons.append("confirmation_text_missing")
    elif not confirmation_valid:
        reasons.append("confirmation_text_invalid")

    eligible = bool(
        domain
        and provider_report.get("ready_for_live_web")
        and allowlist_match
        and source_trust.get("read_only_candidate")
        and operator_approved
        and confirmation_valid
    )

    if eligible:
        reasons.append("eligible_for_future_read_only_live_web_dry_run")
    else:
        reasons.append("not_eligible_for_future_read_only_live_web_dry_run")

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

    report = {
        "build": "v18.16",
        "created_at": _utc_now(),
        "gate": "governed_web_read_only_dry_run_eligibility",
        "target": target,
        "domain": domain,
        "allowlist_match": allowlist_match,
        "operator_approved": operator_approved,
        "confirmation_text_valid": confirmation_valid,
        "eligible_for_future_read_only_live_web_dry_run": eligible,
        "provider_report": provider_report,
        "rate_limit_policy": rate_policy,
        "source_trust": source_trust,
        "reasons": reasons,
        "network_call_performed": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
        "execution_state": _false_execution_state(),
        "safety_state": {
            "read_only_future_path": True,
            "live_web_enabled": False,
            "execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "ai_agent_execution_enabled": False,
            "automatic_updates_enabled": False,
            "operator_review_required": True,
            "approval_equals_execution": False,
        },
    }

    assert_read_only_dry_run_gate_non_executing(report)
    return report


def describe_read_only_dry_run_gate() -> Dict[str, Any]:
    return {
        "build": "v18.16",
        "name": "Governed Web Read-Only Dry-Run Eligibility Gate",
        "required_confirmation_text": REQUIRED_CONFIRMATION_TEXT,
        "network_calls_enabled": False,
        "live_web_enabled": False,
        "execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "ai_agent_execution_enabled": False,
        "automatic_updates_enabled": False,
    }
