from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


AUTHORIZATION_AUDIT_VERSION = "v18.26"
AUTHORIZATION_AUDIT_NAME = "pre_live_probe_authorization_audit"


@dataclass(frozen=True)
class PreLiveProbeAuthorizationAuditResult:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    audit_created: bool
    authorization_ready_for_next_build: bool
    authorization_granted: bool
    required_controls_present: bool
    missing_controls: List[str]
    failed_controls: List[str]
    operator_review_required: bool
    execution_gate_passed: bool
    execution_permitted: bool
    execution_performed: bool
    network_call_performed: bool
    external_request_performed: bool
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    response_body_fetched: bool
    response_status_code: Optional[int]
    decision: str
    reason: str
    timestamp_utc: str
    probe_execution_gate: Dict[str, Any]
    controls: Dict[str, bool]
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _safe_execution_gate(
    request: Mapping[str, Any],
    live_web_execution_enabled: bool,
    ai_agent_execution_enabled: bool,
    operator_approved_planning: bool,
    explicit_operator_enablement_present: bool,
    probe_executor_enabled: bool,
) -> Dict[str, Any]:
    try:
        from runtime_core.governance.governed_web.probe_execution_gate import (
            evaluate_controlled_probe_execution_gate,
        )

        return evaluate_controlled_probe_execution_gate(
            request,
            live_web_execution_enabled=live_web_execution_enabled,
            ai_agent_execution_enabled=ai_agent_execution_enabled,
            operator_approved_planning=operator_approved_planning,
            explicit_operator_enablement_present=explicit_operator_enablement_present,
            probe_executor_enabled=probe_executor_enabled,
        ).to_dict()
    except Exception as exc:
        return {
            "status": "probe_execution_gate_unavailable",
            "reason": str(exc),
            "query": str(request.get("query") or ""),
            "normalized_query": _normalize_query(request.get("query")),
            "provider_id": request.get("provider_id") or "governed-web-search-provider-stub",
            "planned_method": "GET",
            "planned_url": None,
            "execution_gate_passed": False,
            "execution_permitted": False,
            "execution_performed": False,
            "network_call_performed": False,
            "external_request_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
            "response_body_fetched": False,
            "response_status_code": None,
        }


def evaluate_pre_live_probe_authorization_audit(
    request: Optional[Mapping[str, Any]] = None,
    *,
    live_web_execution_enabled: bool = False,
    ai_agent_execution_enabled: bool = False,
    operator_approved_planning: bool = False,
    explicit_operator_enablement_present: bool = False,
    probe_executor_enabled: bool = False,
    provider_readiness_passed: bool = False,
    allowlist_policy_passed: bool = False,
    rate_limit_policy_passed: bool = False,
    source_trust_policy_passed: bool = False,
    dry_run_eligibility_passed: bool = False,
) -> PreLiveProbeAuthorizationAuditResult:
    payload: Mapping[str, Any] = request or {}
    gate = _safe_execution_gate(
        payload,
        live_web_execution_enabled=live_web_execution_enabled,
        ai_agent_execution_enabled=ai_agent_execution_enabled,
        operator_approved_planning=operator_approved_planning,
        explicit_operator_enablement_present=explicit_operator_enablement_present,
        probe_executor_enabled=probe_executor_enabled,
    )

    normalized_query = _normalize_query(
        gate.get("normalized_query") or payload.get("query") or payload.get("raw_input")
    )
    provider_id = str(
        gate.get("provider_id") or payload.get("provider_id") or "governed-web-search-provider-stub"
    )
    planned_method = str(gate.get("planned_method") or "GET")
    planned_url = gate.get("planned_url")

    controls = {
        "normalized_query_present": bool(normalized_query),
        "planned_url_present": bool(planned_url),
        "planned_method_is_get": planned_method.upper() == "GET",
        "provider_readiness_passed": bool(provider_readiness_passed),
        "allowlist_policy_passed": bool(allowlist_policy_passed),
        "rate_limit_policy_passed": bool(rate_limit_policy_passed),
        "source_trust_policy_passed": bool(source_trust_policy_passed),
        "dry_run_eligibility_passed": bool(dry_run_eligibility_passed),
        "operator_approved_planning": bool(operator_approved_planning),
        "explicit_operator_enablement_present": bool(explicit_operator_enablement_present),
        "live_web_execution_enabled": bool(live_web_execution_enabled),
        "ai_agent_execution_disabled": not bool(ai_agent_execution_enabled),
        "probe_executor_requested": bool(probe_executor_enabled),
    }

    safeguards = {
        "audit_only": True,
        "authorization_grant_disabled_this_build": True,
        "no_http_client_invoked": True,
        "planned_url_is_not_fetched": True,
        "approval_is_not_execution": True,
        "next_build_may_add_first_read_only_probe": True,
        "runtime_truth_mutation_forbidden": True,
        "automatic_updates_forbidden": True,
        "requires_operator_review": True,
        "fail_closed": True,
    }

    failed_controls = [name for name, passed in controls.items() if not passed]
    missing_controls = failed_controls[:]

    invalid_gate = any(
        bool(gate.get(key))
        for key in (
            "execution_gate_passed",
            "execution_permitted",
            "execution_performed",
            "network_call_performed",
            "external_request_performed",
            "runtime_truth_mutated",
            "automatic_update_performed",
            "response_body_fetched",
        )
    )

    if invalid_gate:
        status = "invalid_gate_rejected"
        decision = "reject"
        reason = "Execution gate reported execution, permission, or network activity; audit rejected it."
        audit_created = False
        ready_next = False
    elif ai_agent_execution_enabled:
        status = "blocked"
        decision = "reject"
        reason = "AI-agent execution remains disabled for pre-live probe authorization."
        audit_created = bool(normalized_query and planned_url)
        ready_next = False
    elif not normalized_query or not planned_url:
        status = "invalid_request"
        decision = "hold"
        reason = "Pre-live audit requires a normalized query and planned URL."
        audit_created = False
        ready_next = False
    elif failed_controls:
        status = "controls_incomplete"
        decision = "hold"
        reason = "Pre-live probe controls are incomplete; authorization remains withheld."
        audit_created = True
        ready_next = False
    else:
        status = "ready_for_next_build_probe_but_not_authorized_here"
        decision = "hold"
        reason = "All pre-live controls are present; v18.26 records readiness only and grants no execution."
        audit_created = True
        ready_next = True

    return PreLiveProbeAuthorizationAuditResult(
        version=AUTHORIZATION_AUDIT_VERSION,
        name=AUTHORIZATION_AUDIT_NAME,
        status=status,
        query=str(payload.get("query") or gate.get("query") or ""),
        normalized_query=normalized_query,
        provider_id=provider_id,
        planned_method=planned_method,
        planned_url=str(planned_url) if planned_url is not None else None,
        audit_created=audit_created,
        authorization_ready_for_next_build=ready_next,
        authorization_granted=False,
        required_controls_present=(not failed_controls),
        missing_controls=missing_controls,
        failed_controls=failed_controls,
        operator_review_required=True,
        execution_gate_passed=False,
        execution_permitted=False,
        execution_performed=False,
        network_call_performed=False,
        external_request_performed=False,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        response_body_fetched=False,
        response_status_code=None,
        decision=decision,
        reason=reason,
        timestamp_utc=_utc_now(),
        probe_execution_gate=dict(gate),
        controls=controls,
        safeguards=safeguards,
    )


def build_dashboard_pre_live_authorization_payload(query: str, provider_id: Optional[str] = None) -> Dict[str, Any]:
    audit = evaluate_pre_live_probe_authorization_audit(
        {"query": query, "provider_id": provider_id}
    )
    return {
        "dashboard_surface": "search_bar",
        "mode": "pre_live_probe_authorization_audit",
        "version": AUTHORIZATION_AUDIT_VERSION,
        "pre_live_authorization_audit": audit.to_dict(),
        "ui_notice": "Pre-live probe authorization audit is available. No network request has been made.",
    }


__all__ = [
    "AUTHORIZATION_AUDIT_VERSION",
    "AUTHORIZATION_AUDIT_NAME",
    "PreLiveProbeAuthorizationAuditResult",
    "evaluate_pre_live_probe_authorization_audit",
    "build_dashboard_pre_live_authorization_payload",
]
