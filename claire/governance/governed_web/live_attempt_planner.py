from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


ATTEMPT_PLANNER_VERSION = "v18.23"
ATTEMPT_PLANNER_NAME = "controlled_read_only_live_attempt_planner"


@dataclass(frozen=True)
class ControlledReadOnlyLiveAttemptPlan:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    plan_created: bool
    eligible_for_future_network_probe: bool
    operator_review_required: bool
    execution_performed: bool
    network_call_performed: bool
    external_request_performed: bool
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    response_body_fetched: bool
    live_web_execution_enabled: bool
    ai_agent_execution_enabled: bool
    decision: str
    reason: str
    timestamp_utc: str
    provider_preview: Dict[str, Any]
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _safe_provider_preview(
    request: Mapping[str, Any],
    live_web_execution_enabled: bool,
    ai_agent_execution_enabled: bool,
) -> Dict[str, Any]:
    try:
        from claire.governance.governed_web.provider_adapter_preview_bridge import (
            build_governed_web_provider_adapter_preview,
        )

        return build_governed_web_provider_adapter_preview(
            request,
            live_web_execution_enabled=live_web_execution_enabled,
            ai_agent_execution_enabled=ai_agent_execution_enabled,
        ).to_dict()
    except Exception as exc:
        return {
            "status": "provider_preview_unavailable",
            "reason": str(exc),
            "query": str(request.get("query") or ""),
            "normalized_query": _normalize_query(request.get("query")),
            "provider_id": request.get("provider_id") or "governed-web-search-provider-stub",
            "provider_preview_url": None,
            "execution_performed": False,
            "network_call_performed": False,
            "external_request_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
            "response_body_fetched": False,
        }


def build_controlled_read_only_live_attempt_plan(
    request: Optional[Mapping[str, Any]] = None,
    *,
    live_web_execution_enabled: bool = False,
    ai_agent_execution_enabled: bool = False,
    operator_approved_planning: bool = False,
) -> ControlledReadOnlyLiveAttemptPlan:
    payload: Mapping[str, Any] = request or {}
    preview = _safe_provider_preview(payload, live_web_execution_enabled, ai_agent_execution_enabled)

    normalized_query = _normalize_query(
        preview.get("normalized_query") or payload.get("query") or payload.get("raw_input")
    )
    provider_id = str(
        preview.get("provider_id") or payload.get("provider_id") or "governed-web-search-provider-stub"
    )
    planned_url = preview.get("provider_preview_url")
    planned_method = str(preview.get("request_method") or "GET")

    safeguards = {
        "planning_only": True,
        "no_http_client_invoked": True,
        "planned_url_is_not_fetched": True,
        "approval_is_not_execution": True,
        "operator_approval_only_allows_planning": True,
        "requires_next_build_network_probe_adapter": True,
        "requires_provider_readiness": True,
        "requires_allowlist_match": True,
        "requires_rate_limit_policy": True,
        "requires_source_trust_policy": True,
        "requires_dry_run_eligibility": True,
        "requires_operator_review": True,
        "fail_closed": True,
    }

    invalid_source = any(
        bool(preview.get(key))
        for key in (
            "execution_performed",
            "network_call_performed",
            "external_request_performed",
            "runtime_truth_mutated",
            "automatic_update_performed",
            "response_body_fetched",
        )
    )

    if invalid_source:
        status = "invalid_preview_rejected"
        decision = "reject"
        reason = "Provider preview reported execution or network activity; planner rejected it."
        eligible = False
        plan_created = False
    elif ai_agent_execution_enabled:
        status = "blocked"
        decision = "reject"
        reason = "AI-agent execution remains disabled for live-read attempt planning."
        eligible = False
        plan_created = bool(normalized_query and planned_url)
    elif not normalized_query or not planned_url:
        status = "invalid_request"
        decision = "hold"
        reason = "A normalized query and planned preview URL are required before planning."
        eligible = False
        plan_created = False
    elif live_web_execution_enabled and operator_approved_planning:
        status = "future_probe_plan_ready_execution_still_disabled"
        decision = "hold"
        reason = "Future network probe plan is ready, but v18.23 still performs no network call."
        eligible = True
        plan_created = True
    else:
        status = "plan_ready_fail_closed"
        decision = "hold"
        reason = "Read-only live attempt plan is ready for review; network execution remains disabled."
        eligible = False
        plan_created = True

    return ControlledReadOnlyLiveAttemptPlan(
        version=ATTEMPT_PLANNER_VERSION,
        name=ATTEMPT_PLANNER_NAME,
        status=status,
        query=str(payload.get("query") or preview.get("query") or ""),
        normalized_query=normalized_query,
        provider_id=provider_id,
        planned_method=planned_method,
        planned_url=str(planned_url) if planned_url is not None else None,
        plan_created=plan_created,
        eligible_for_future_network_probe=eligible,
        operator_review_required=True,
        execution_performed=False,
        network_call_performed=False,
        external_request_performed=False,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        response_body_fetched=False,
        live_web_execution_enabled=bool(live_web_execution_enabled),
        ai_agent_execution_enabled=bool(ai_agent_execution_enabled),
        decision=decision,
        reason=reason,
        timestamp_utc=_utc_now(),
        provider_preview=dict(preview),
        safeguards=safeguards,
    )


def build_dashboard_live_attempt_plan_payload(query: str, provider_id: Optional[str] = None) -> Dict[str, Any]:
    plan = build_controlled_read_only_live_attempt_plan(
        {"query": query, "provider_id": provider_id}
    )
    return {
        "dashboard_surface": "search_bar",
        "mode": "controlled_live_attempt_plan",
        "version": ATTEMPT_PLANNER_VERSION,
        "live_attempt_plan": plan.to_dict(),
        "ui_notice": "Controlled read-only live attempt plan is ready. No network request has been made.",
    }


__all__ = [
    "ATTEMPT_PLANNER_VERSION",
    "ATTEMPT_PLANNER_NAME",
    "ControlledReadOnlyLiveAttemptPlan",
    "build_controlled_read_only_live_attempt_plan",
    "build_dashboard_live_attempt_plan_payload",
]
