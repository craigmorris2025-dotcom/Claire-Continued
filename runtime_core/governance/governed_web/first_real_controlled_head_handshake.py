from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


HEAD_HANDSHAKE_VERSION = "v18.32"
HEAD_HANDSHAKE_NAME = "first_real_controlled_head_handshake"


@dataclass(frozen=True)
class FirstRealControlledHeadHandshakeResult:
    version: str
    name: str
    status: str
    query: str
    normalized_query: str
    provider_id: str
    planned_method: str
    planned_url: Optional[str]
    handshake_executor_created: bool
    transport_guard_active: bool
    outbound_network_allowed: bool
    head_handshake_allowed: bool
    head_handshake_performed: bool
    response_headers_received: bool
    response_body_fetched: bool
    response_status_code: Optional[int]
    runtime_truth_mutated: bool
    automatic_update_performed: bool
    execution_performed: bool
    network_call_performed: bool
    external_request_performed: bool
    decision: str
    reason: str
    timestamp_utc: str
    safeguards: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def execute_first_real_controlled_head_handshake(
    request: Optional[Mapping[str, Any]] = None,
) -> FirstRealControlledHeadHandshakeResult:

    payload: Mapping[str, Any] = request or {}
    normalized_query = _normalize_query(payload.get("query"))

    safeguards = {
        "head_only": True,
        "response_body_fetch_forbidden": True,
        "runtime_truth_mutation_forbidden": True,
        "automatic_updates_forbidden": True,
        "read_only_scope": True,
        "fail_closed": True,
    }

    if not normalized_query:
        status = "invalid_request"
        decision = "hold"
        reason = "Handshake requires a non-empty normalized query."

        return FirstRealControlledHeadHandshakeResult(
            version=HEAD_HANDSHAKE_VERSION,
            name=HEAD_HANDSHAKE_NAME,
            status=status,
            query="",
            normalized_query="",
            provider_id="governed-web-search-provider-stub",
            planned_method="HEAD",
            planned_url=None,
            handshake_executor_created=True,
            transport_guard_active=True,
            outbound_network_allowed=False,
            head_handshake_allowed=False,
            head_handshake_performed=False,
            response_headers_received=False,
            response_body_fetched=False,
            response_status_code=None,
            runtime_truth_mutated=False,
            automatic_update_performed=False,
            execution_performed=False,
            network_call_performed=False,
            external_request_performed=False,
            decision=decision,
            reason=reason,
            timestamp_utc=_utc_now(),
            safeguards=safeguards,
        )

    return FirstRealControlledHeadHandshakeResult(
        version=HEAD_HANDSHAKE_VERSION,
        name=HEAD_HANDSHAKE_NAME,
        status="head_handshake_ready",
        query=str(payload.get("query") or ""),
        normalized_query=normalized_query,
        provider_id="governed-web-search-provider-stub",
        planned_method="HEAD",
        planned_url="https://example.com",
        handshake_executor_created=True,
        transport_guard_active=True,
        outbound_network_allowed=True,
        head_handshake_allowed=True,
        head_handshake_performed=False,
        response_headers_received=False,
        response_body_fetched=False,
        response_status_code=None,
        runtime_truth_mutated=False,
        automatic_update_performed=False,
        execution_performed=False,
        network_call_performed=False,
        external_request_performed=False,
        decision="hold",
        reason="First controlled HEAD handshake is authorized but not auto-executed in installer validation.",
        timestamp_utc=_utc_now(),
        safeguards=safeguards,
    )


def build_dashboard_head_handshake_payload(query: str) -> Dict[str, Any]:
    result = execute_first_real_controlled_head_handshake({"query": query})

    return {
        "dashboard_surface": "search_bar",
        "mode": "first_real_controlled_head_handshake",
        "version": HEAD_HANDSHAKE_VERSION,
        "head_handshake": result.to_dict(),
        "ui_notice": "Controlled HEAD handshake layer installed. Response body fetching remains forbidden.",
    }


__all__ = [
    "HEAD_HANDSHAKE_VERSION",
    "HEAD_HANDSHAKE_NAME",
    "FirstRealControlledHeadHandshakeResult",
    "execute_first_real_controlled_head_handshake",
    "build_dashboard_head_handshake_payload",
]
