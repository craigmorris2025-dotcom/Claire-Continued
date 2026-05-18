from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


NETWORK_PROBE_ADAPTER_VERSION = "v18.24"
NETWORK_PROBE_ADAPTER_NAME = "controlled_network_probe_adapter_shell"


@dataclass(frozen=True)
class ControlledNetworkProbeAdapterResult:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    adapter_shell_created: bool
    probe_executor_available: bool
    probe_executor_enabled: bool
    probe_attempted: bool
    eligible_for_future_read_only_probe: bool
    operator_review_required: bool
    execution_performed: bool
    network_call_performed: bool
    external_request_performed: bool
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    response_body_fetched: bool
    response_status_code: Optional[int]
    response_headers_captured: bool
    live_web_execution_enabled: bool
    ai_agent_execution_enabled: bool
    decision: str
    reason: str
    timestamp_utc: str
    attempt_plan: Dict[str, Any]
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _safe_attempt_plan(
    request: Mapping[str, Any],
    live_web_execution_enabled: bool,
    ai_agent_execution_enabled: bool,
    operator_approved_planning: bool,
) -> Dict[str, Any]:
    try:
        from claire.governance.governed_web.live_attempt_planner import (
            build_controlled_read_only_live_attempt_plan,
        )

        return build_controlled_read_only_live_attempt_plan(
            request,
            live_web_execution_enabled=live_web_execution_enabled,
            ai_agent_execution_enabled=ai_agent_execution_enabled,
            operator_approved_planning=operator_approved_planning,
        ).to_dict()
    except Exception as exc:
        return {
            "status": "attempt_plan_unavailable",
            "reason": str(exc),
            "query": str(request.get("query") or ""),
            "normalized_query": _normalize_query(request.get("query")),
            "provider_id": request.get("provider_id") or "governed-web-search-provider-stub",
            "planned_method": "GET",
            "planned_url": None,
            "execution_performed": False,
            "network_call_performed": False,
            "external_request_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
            "response_body_fetched": False,
        }


def build_controlled_network_probe_adapter_shell(
    request: Optional[Mapping[str, Any]] = None,
    *,
    live_web_execution_enabled: bool = False,
    ai_agent_execution_enabled: bool = False,
    operator_approved_planning: bool = False,
    probe_executor_enabled: bool = False,
) -> ControlledNetworkProbeAdapterResult:
    payload: Mapping[str, Any] = request or {}
    plan = _safe_attempt_plan(
        payload,
        live_web_execution_enabled=live_web_execution_enabled,
        ai_agent_execution_enabled=ai_agent_execution_enabled,
        operator_approved_planning=operator_approved_planning,
    )

    normalized_query = _normalize_query(
        plan.get("normalized_query") or payload.get("query") or payload.get("raw_input")
    )
    provider_id = str(
        plan.get("provider_id") or payload.get("provider_id") or "governed-web-search-provider-stub"
    )
    planned_method = str(plan.get("planned_method") or "GET")
    planned_url = plan.get("planned_url")

    safeguards = {
        "adapter_shell_only": True,
        "probe_executor_hard_disabled": True,
        "no_http_client_invoked": True,
        "planned_url_is_not_fetched": True,
        "approval_is_not_execution": True,
        "operator_approval_only_allows_shell_creation": True,
        "requires_next_build_probe_execution_gate": True,
        "requires_provider_readiness": True,
        "requires_allowlist_match": True,
        "requires_rate_limit_policy": True,
        "requires_source_trust_policy": True,
        "requires_dry_run_eligibility": True,
        "requires_operator_review": True,
        "fail_closed": True,
    }

    invalid_plan = any(
        bool(plan.get(key))
        for key in (
            "execution_performed",
            "network_call_performed",
            "external_request_performed",
            "runtime_truth_mutated",
            "automatic_update_performed",
            "response_body_fetched",
        )
    )

    if invalid_plan:
        status = "invalid_plan_rejected"
        decision = "reject"
        reason = "Attempt plan reported execution or network activity; adapter shell rejected it."
        eligible = False
        shell_created = False
    elif ai_agent_execution_enabled:
        status = "blocked"
        decision = "reject"
        reason = "AI-agent execution remains disabled for controlled network probe adapter."
        eligible = False
        shell_created = bool(normalized_query and planned_url)
    elif not normalized_query or not planned_url:
        status = "invalid_request"
        decision = "hold"
        reason = "Network probe adapter shell requires a normalized query and planned URL."
        eligible = False
        shell_created = False
    elif live_web_execution_enabled and operator_approved_planning and probe_executor_enabled:
        status = "probe_shell_ready_executor_still_hard_disabled"
        decision = "hold"
        reason = "Probe adapter shell is ready, but v18.24 hard-disables network execution."
        eligible = True
        shell_created = True
    elif live_web_execution_enabled and operator_approved_planning:
        status = "probe_shell_ready_executor_disabled"
        decision = "hold"
        reason = "Probe adapter shell is ready for future read-only execution gate; executor remains disabled."
        eligible = True
        shell_created = True
    else:
        status = "probe_shell_ready_fail_closed"
        decision = "hold"
        reason = "Network probe adapter shell created for review; live probe execution remains disabled."
        eligible = False
        shell_created = True

    return ControlledNetworkProbeAdapterResult(
        version=NETWORK_PROBE_ADAPTER_VERSION,
        name=NETWORK_PROBE_ADAPTER_NAME,
        status=status,
        query=str(payload.get("query") or plan.get("query") or ""),
        normalized_query=normalized_query,
        provider_id=provider_id,
        planned_method=planned_method,
        planned_url=str(planned_url) if planned_url is not None else None,
        adapter_shell_created=shell_created,
        probe_executor_available=True,
        probe_executor_enabled=False,
        probe_attempted=False,
        eligible_for_future_read_only_probe=eligible,
        operator_review_required=True,
        execution_performed=False,
        network_call_performed=False,
        external_request_performed=False,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        response_body_fetched=False,
        response_status_code=None,
        response_headers_captured=False,
        live_web_execution_enabled=bool(live_web_execution_enabled),
        ai_agent_execution_enabled=bool(ai_agent_execution_enabled),
        decision=decision,
        reason=reason,
        timestamp_utc=_utc_now(),
        attempt_plan=dict(plan),
        safeguards=safeguards,
    )


def build_dashboard_network_probe_shell_payload(query: str, provider_id: Optional[str] = None) -> Dict[str, Any]:
    shell = build_controlled_network_probe_adapter_shell(
        {"query": query, "provider_id": provider_id}
    )
    return {
        "dashboard_surface": "search_bar",
        "mode": "controlled_network_probe_shell",
        "version": NETWORK_PROBE_ADAPTER_VERSION,
        "network_probe_shell": shell.to_dict(),
        "ui_notice": "Controlled network probe adapter shell is ready. No network request has been made.",
    }


__all__ = [
    "NETWORK_PROBE_ADAPTER_VERSION",
    "NETWORK_PROBE_ADAPTER_NAME",
    "ControlledNetworkProbeAdapterResult",
    "build_controlled_network_probe_adapter_shell",
    "build_dashboard_network_probe_shell_payload",
]
