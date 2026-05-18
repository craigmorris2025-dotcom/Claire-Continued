from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional
from urllib.parse import quote_plus


PROVIDER_BRIDGE_VERSION = "v18.22"
PROVIDER_BRIDGE_NAME = "governed_web_provider_adapter_preview_bridge"


@dataclass(frozen=True)
class GovernedWebProviderAdapterPreview:
    version: str
    name: str
    status: str
    provider_id: str
    query: str
    normalized_query: str
    provider_preview_url: Optional[str]
    request_method: str
    request_headers_preview: Dict[str, str]
    adapter_ready_for_future_read_only_call: bool
    dashboard_preview_ready: bool
    review_required: bool
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
    envelope: Dict[str, Any]
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _build_preview_url(provider_id: str, normalized_query: str) -> Optional[str]:
    if not normalized_query:
        return None

    # Preview-only. This is not fetched.
    if provider_id == "governed-web-search-provider-stub":
        return "https://example.com/search?q=" + quote_plus(normalized_query)

    return "https://example.com/provider/" + quote_plus(provider_id) + "/search?q=" + quote_plus(normalized_query)


def _safe_envelope(request: Mapping[str, Any], live_web_execution_enabled: bool, ai_agent_execution_enabled: bool) -> Dict[str, Any]:
    try:
        from claire.governance.governed_web.search_request_envelope import (
            build_governed_web_search_request_envelope,
        )

        return build_governed_web_search_request_envelope(
            request,
            live_web_execution_enabled=live_web_execution_enabled,
            ai_agent_execution_enabled=ai_agent_execution_enabled,
        ).to_dict()
    except Exception as exc:
        return {
            "status": "envelope_unavailable",
            "reason": str(exc),
            "query": str(request.get("query") or ""),
            "normalized_query": _normalize_query(request.get("query")),
            "provider_id": request.get("provider_id"),
            "dashboard_preview_ready": False,
            "execution_performed": False,
            "network_call_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
        }


def build_governed_web_provider_adapter_preview(
    request: Optional[Mapping[str, Any]] = None,
    *,
    live_web_execution_enabled: bool = False,
    ai_agent_execution_enabled: bool = False,
) -> GovernedWebProviderAdapterPreview:
    payload: Mapping[str, Any] = request or {}
    envelope = _safe_envelope(payload, live_web_execution_enabled, ai_agent_execution_enabled)

    normalized_query = _normalize_query(
        envelope.get("normalized_query") or payload.get("query") or payload.get("raw_input")
    )
    provider_id = str(
        envelope.get("provider_id")
        or payload.get("provider_id")
        or "governed-web-search-provider-stub"
    )

    provider_preview_url = _build_preview_url(provider_id, normalized_query)

    safeguards = {
        "preview_only": True,
        "url_is_not_fetched": True,
        "no_http_client_invoked": True,
        "approval_is_not_execution": True,
        "requires_future_read_only_call_adapter": True,
        "requires_provider_readiness": True,
        "requires_allowlist_match": True,
        "requires_rate_limit_policy": True,
        "requires_source_trust_policy": True,
        "requires_operator_review": True,
        "fail_closed": True,
    }

    if ai_agent_execution_enabled:
        status = "blocked"
        decision = "reject"
        reason = "AI-agent execution remains disabled for governed provider adapter bridge."
        adapter_ready = False
        dashboard_ready = bool(normalized_query)
    elif not normalized_query:
        status = "invalid_request"
        decision = "hold"
        reason = "Provider adapter preview requires a normalized query."
        adapter_ready = False
        dashboard_ready = False
    elif live_web_execution_enabled:
        status = "adapter_preview_ready_execution_still_disabled"
        decision = "hold"
        reason = "Provider adapter preview is ready, but v18.22 still performs no HTTP call."
        adapter_ready = True
        dashboard_ready = True
    else:
        status = "adapter_preview_ready_fail_closed"
        decision = "hold"
        reason = "Provider adapter preview is ready for review; live execution remains disabled."
        adapter_ready = False
        dashboard_ready = True

    return GovernedWebProviderAdapterPreview(
        version=PROVIDER_BRIDGE_VERSION,
        name=PROVIDER_BRIDGE_NAME,
        status=status,
        provider_id=provider_id,
        query=str(payload.get("query") or envelope.get("query") or ""),
        normalized_query=normalized_query,
        provider_preview_url=provider_preview_url,
        request_method="GET",
        request_headers_preview={
            "User-Agent": "Claire-Syntalion-Governed-ReadOnly-Preview/18.22",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        },
        adapter_ready_for_future_read_only_call=adapter_ready,
        dashboard_preview_ready=dashboard_ready,
        review_required=True,
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
        envelope=dict(envelope),
        safeguards=safeguards,
    )


def build_dashboard_provider_preview_payload(query: str, provider_id: Optional[str] = None) -> Dict[str, Any]:
    preview = build_governed_web_provider_adapter_preview(
        {"query": query, "provider_id": provider_id}
    )
    return {
        "dashboard_surface": "search_bar",
        "mode": "governed_provider_preview",
        "version": PROVIDER_BRIDGE_VERSION,
        "provider_preview": preview.to_dict(),
        "ui_notice": "Provider adapter preview is ready. No external request has been made.",
    }


__all__ = [
    "PROVIDER_BRIDGE_VERSION",
    "PROVIDER_BRIDGE_NAME",
    "GovernedWebProviderAdapterPreview",
    "build_governed_web_provider_adapter_preview",
    "build_dashboard_provider_preview_payload",
]
