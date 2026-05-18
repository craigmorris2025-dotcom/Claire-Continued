from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


REQUEST_ENVELOPE_VERSION = "v18.21"
REQUEST_ENVELOPE_NAME = "accelerated_governed_web_search_request_envelope"


@dataclass(frozen=True)
class GovernedWebSearchRequestEnvelope:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: Optional[str]
    requested_url: Optional[str]
    route: str
    dashboard_preview_ready: bool
    eligible_for_future_live_read: bool
    review_required: bool
    execution_performed: bool
    network_call_performed: bool
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    ai_agent_execution_enabled: bool
    live_web_execution_enabled: bool
    decision: str
    reason: str
    timestamp_utc: str
    governance: Dict[str, Any]
    handshake: Dict[str, Any]
    review_record: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _provider_from_query(normalized_query: str) -> Optional[str]:
    if not normalized_query:
        return None
    return "governed-web-search-provider-stub"


def _safe_import_handshake(request: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        from claire.governance.governed_web.live_connectivity_handshake import (
            evaluate_controlled_read_only_live_connectivity_handshake,
        )

        return evaluate_controlled_read_only_live_connectivity_handshake(request).to_dict()
    except Exception as exc:
        return {
            "status": "handshake_unavailable",
            "reason": str(exc),
            "execution_performed": False,
            "network_call_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
        }


def _safe_import_review_record(handshake: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        from claire.governance.governed_web.live_connectivity_handshake_review_record import (
            create_controlled_live_connectivity_handshake_review_record,
        )

        return create_controlled_live_connectivity_handshake_review_record(handshake).to_dict()
    except Exception as exc:
        return {
            "status": "review_record_unavailable",
            "reason": str(exc),
            "review_required": True,
            "approved_for_execution": False,
            "execution_performed": False,
            "network_call_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
        }


def build_governed_web_search_request_envelope(
    request: Optional[Mapping[str, Any]] = None,
    *,
    live_web_execution_enabled: bool = False,
    ai_agent_execution_enabled: bool = False,
) -> GovernedWebSearchRequestEnvelope:
    payload: Mapping[str, Any] = request or {}
    query = payload.get("query") or payload.get("raw_input") or payload.get("search") or ""
    normalized_query = _normalize_query(query)
    requested_url = payload.get("url") or payload.get("requested_url")
    provider_id = payload.get("provider_id") or _provider_from_query(normalized_query)

    governed_request = {
        "query": normalized_query,
        "provider_id": provider_id,
        "requested_url": requested_url,
        "url": requested_url,
    }

    handshake = _safe_import_handshake(governed_request)
    review_record = _safe_import_review_record(handshake)

    governance = {
        "search_bar_permanent": True,
        "normal_web_search_foundation": True,
        "governed_research_routing": True,
        "runtime_truth_search_not_mutated": True,
        "future_ai_agent_command_surface": True,
        "review_gate_only": True,
        "approval_is_not_execution": True,
        "requires_provider_readiness": True,
        "requires_allowlist_match": True,
        "requires_rate_limit_policy": True,
        "requires_source_trust_policy": True,
        "requires_dry_run_eligibility": True,
        "requires_future_live_adapter_enablement": True,
        "fail_closed": True,
    }

    if ai_agent_execution_enabled:
        status = "blocked"
        decision = "reject"
        reason = "AI-agent execution is disabled for governed web search."
        eligible = False
        preview_ready = bool(normalized_query)
    elif not normalized_query:
        status = "invalid_request"
        decision = "hold"
        reason = "Search query is required before governed web review can continue."
        eligible = False
        preview_ready = False
    elif live_web_execution_enabled:
        status = "preview_ready_execution_still_disabled"
        decision = "hold"
        reason = "Dashboard preview envelope is ready, but v18.21 still performs no live request."
        eligible = True
        preview_ready = True
    else:
        status = "preview_ready_fail_closed"
        decision = "hold"
        reason = "Governed web search request envelope is ready for review; live execution remains disabled."
        eligible = False
        preview_ready = True

    return GovernedWebSearchRequestEnvelope(
        version=REQUEST_ENVELOPE_VERSION,
        name=REQUEST_ENVELOPE_NAME,
        status=status,
        query=str(query or ""),
        normalized_query=normalized_query,
        provider_id=str(provider_id) if provider_id is not None else None,
        requested_url=str(requested_url) if requested_url is not None else None,
        route="governed_web_search_preview",
        dashboard_preview_ready=preview_ready,
        eligible_for_future_live_read=eligible,
        review_required=True,
        execution_performed=False,
        network_call_performed=False,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        ai_agent_execution_enabled=bool(ai_agent_execution_enabled),
        live_web_execution_enabled=bool(live_web_execution_enabled),
        decision=decision,
        reason=reason,
        timestamp_utc=_utc_now(),
        governance=governance,
        handshake=dict(handshake),
        review_record=dict(review_record),
    )


def build_dashboard_search_preview_payload(
    query: str,
    *,
    provider_id: Optional[str] = None,
) -> Dict[str, Any]:
    envelope = build_governed_web_search_request_envelope(
        {"query": query, "provider_id": provider_id}
    )
    return {
        "dashboard_surface": "search_bar",
        "mode": "governed_web_preview",
        "version": REQUEST_ENVELOPE_VERSION,
        "envelope": envelope.to_dict(),
        "ui_notice": (
            "Governed web search preview is ready. "
            "No external request has been made."
        ),
    }


__all__ = [
    "REQUEST_ENVELOPE_VERSION",
    "REQUEST_ENVELOPE_NAME",
    "GovernedWebSearchRequestEnvelope",
    "build_governed_web_search_request_envelope",
    "build_dashboard_search_preview_payload",
]
