
# Claire Syntalion v18.64
# Dashboard-to-Endpoint Fetch Proof
#
# This module proves the governed dashboard search request payload can be
# handed to the live-search endpoint contract and return dashboard-visible
# result cards. It uses an injected deterministic proof executor only. It does
# not perform real internet calls, mutate runtime truth, enable autonomous
# execution, or perform automatic updates.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Mapping, Optional


CONTRACT_VERSION = "v18.64.dashboard_to_endpoint_fetch_proof"

DEFAULT_ENDPOINT = "/api/dashboard/search/live"
GOOGLE_URL = "https://www.google.com"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        value = value.strip()
        return value if value else default
    return str(value).strip() or default


@dataclass(frozen=True)
class DashboardToEndpointFetchProofPolicy:
    manual_enable_required: bool = True
    real_internet_calls_allowed: bool = False
    injected_executor_only: bool = True
    browser_network_required: bool = False
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    endpoint_contract_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manual_enable_required": self.manual_enable_required,
            "real_internet_calls_allowed": self.real_internet_calls_allowed,
            "injected_executor_only": self.injected_executor_only,
            "browser_network_required": self.browser_network_required,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "endpoint_contract_only": self.endpoint_contract_only,
        }


def _governance(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = {
        "review_required": True,
        "runtime_truth_mutated": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "fail_closed": True,
        "real_internet_calls": False,
    }
    if extra:
        payload.update(extra)
    return payload


def google_fetch_proof_executor(**kwargs: Any) -> Dict[str, Any]:
    query = _string(kwargs.get("query"), "google")
    provider = _string(kwargs.get("provider"), "dashboard-fetch-proof-provider")
    session_id = _string(kwargs.get("session_id"), "dashboard-fetch-proof-session")
    return {
        "provider_status": "ok",
        "query": query,
        "provider": provider,
        "session_id": session_id,
        "results": [
            {
                "title": "Google",
                "url": GOOGLE_URL,
                "snippet": "Google search result returned by governed dashboard-to-endpoint fetch proof.",
                "provider": provider,
                "trust_score": 1.0,
                "result_id": "v18-64-google-fetch-proof-result",
                "evidence_id": "v18-64-google-fetch-proof-evidence",
            }
        ],
    }


def build_dashboard_fetch_request_payload(
    *,
    query: str = "google",
    manual_enable_confirmed: bool = True,
    provider: str = "dashboard-fetch-proof-provider",
    session_id: str = "dashboard-fetch-proof-session",
    max_results: int = 3,
    require_provider_env: bool = False,
    require_limited_body_env: bool = False,
) -> Dict[str, Any]:
    try:
        from .dashboard_live_search_ui_fetch_binding import build_dashboard_live_search_request_payload
    except Exception:
        return {
            "query": _string(query),
            "session_id": _string(session_id),
            "provider": _string(provider, "dashboard-fetch-proof-provider"),
            "manual_enable_confirmed": bool(manual_enable_confirmed),
            "require_provider_env": bool(require_provider_env),
            "require_limited_body_env": bool(require_limited_body_env),
            "max_results": max(1, int(max_results or 3)),
        }

    return build_dashboard_live_search_request_payload(
        query=query,
        manual_enable_confirmed=manual_enable_confirmed,
        provider=provider,
        session_id=session_id,
        max_results=max_results,
        require_provider_env=require_provider_env,
        require_limited_body_env=require_limited_body_env,
    )


def execute_fetch_payload_against_endpoint_contract(
    fetch_payload: Mapping[str, Any],
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    request_id: str = "v18-64-dashboard-fetch-proof",
    executor: Optional[Callable[..., Any]] = None,
) -> Dict[str, Any]:
    policy = DashboardToEndpointFetchProofPolicy()

    try:
        from .dashboard_search_endpoint_result_contract import execute_dashboard_search_endpoint_request
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "dashboard_search_endpoint_contract_unavailable",
            "created_at": _utc_now(),
            "endpoint": endpoint,
            "fetch_payload": dict(fetch_payload),
            "endpoint_response": {},
            "error_type": type(exc).__name__,
            "visible_result_count": 0,
            "policy": policy.to_dict(),
            "governance": _governance(),
        }

    response = execute_dashboard_search_endpoint_request(
        query=_string(fetch_payload.get("query")),
        session_id=_string(fetch_payload.get("session_id"), "dashboard-fetch-proof-session"),
        provider=_string(fetch_payload.get("provider"), "dashboard-fetch-proof-provider"),
        executor=executor,
        manual_enable_confirmed=bool(fetch_payload.get("manual_enable_confirmed")),
        require_provider_env=bool(fetch_payload.get("require_provider_env")),
        require_limited_body_env=bool(fetch_payload.get("require_limited_body_env")),
        max_results=int(fetch_payload.get("max_results") or 3),
        request_context={
            "source": "dashboard_to_endpoint_fetch_proof",
            "browser_network_required": False,
            "real_internet_calls": False,
        },
        endpoint=endpoint,
        request_id=request_id,
    )

    cards = response.get("result_cards") if isinstance(response, dict) else []
    first = cards[0] if isinstance(cards, list) and cards and isinstance(cards[0], dict) else {}

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "endpoint_response_received",
        "reason": response.get("reason", "") if isinstance(response, dict) else "invalid_endpoint_response",
        "created_at": _utc_now(),
        "endpoint": endpoint,
        "fetch_payload": dict(fetch_payload),
        "endpoint_response": response,
        "visible_result_count": int(response.get("visible_result_count") or 0) if isinstance(response, dict) else 0,
        "first_result_title": first.get("title", ""),
        "first_result_url": first.get("url", ""),
        "endpoint_status": response.get("endpoint_status", "") if isinstance(response, dict) else "",
        "http_status": int(response.get("http_status") or 0) if isinstance(response, dict) else 0,
        "policy": policy.to_dict(),
        "governance": _governance({"endpoint_contract_invoked": True}),
    }


def run_dashboard_to_endpoint_google_fetch_proof() -> Dict[str, Any]:
    policy = DashboardToEndpointFetchProofPolicy()
    fetch_payload = build_dashboard_fetch_request_payload(
        query="google",
        manual_enable_confirmed=True,
        provider="dashboard-fetch-proof-provider",
        session_id="dashboard-fetch-proof-session",
        max_results=3,
        require_provider_env=False,
        require_limited_body_env=False,
    )

    result = execute_fetch_payload_against_endpoint_contract(
        fetch_payload,
        executor=google_fetch_proof_executor,
        request_id="v18-64-google-fetch-proof",
    )

    endpoint_response = result.get("endpoint_response") if isinstance(result, dict) else {}
    cards = endpoint_response.get("result_cards") if isinstance(endpoint_response, dict) else []
    first = cards[0] if isinstance(cards, list) and cards and isinstance(cards[0], dict) else {}

    passed = (
        result.get("status") == "endpoint_response_received"
        and endpoint_response.get("endpoint_status") == "endpoint_response_ready"
        and int(endpoint_response.get("visible_result_count") or 0) >= 1
        and first.get("title") == "Google"
        and first.get("url") == GOOGLE_URL
    )

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "passed" if passed else "failed",
        "reason": "" if passed else "dashboard_to_endpoint_google_fetch_proof_failed",
        "created_at": _utc_now(),
        "fetch_proof": result,
        "query": "google",
        "visible_result_count": result.get("visible_result_count", 0),
        "first_result_title": result.get("first_result_title", ""),
        "first_result_url": result.get("first_result_url", ""),
        "policy": policy.to_dict(),
        "governance": _governance({"proof_executor": "google_fetch_proof_executor"}),
    }


def run_dashboard_to_endpoint_manual_enable_block_proof() -> Dict[str, Any]:
    policy = DashboardToEndpointFetchProofPolicy()
    fetch_payload = build_dashboard_fetch_request_payload(
        query="google",
        manual_enable_confirmed=False,
        provider="dashboard-fetch-proof-provider",
        session_id="dashboard-fetch-proof-block-session",
        max_results=3,
        require_provider_env=False,
        require_limited_body_env=False,
    )

    result = execute_fetch_payload_against_endpoint_contract(
        fetch_payload,
        executor=google_fetch_proof_executor,
        request_id="v18-64-manual-enable-block-proof",
    )

    endpoint_response = result.get("endpoint_response") if isinstance(result, dict) else {}
    passed = (
        result.get("status") == "endpoint_response_received"
        and endpoint_response.get("endpoint_status") == "endpoint_blocked"
        and endpoint_response.get("reason") == "manual_enable_not_confirmed"
        and int(endpoint_response.get("visible_result_count") or 0) == 0
    )

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "passed" if passed else "failed",
        "reason": "" if passed else "manual_enable_block_fetch_proof_failed",
        "created_at": _utc_now(),
        "fetch_proof": result,
        "query": "google",
        "manual_enable_block_confirmed": passed,
        "policy": policy.to_dict(),
        "governance": _governance({"proof_executor": "google_fetch_proof_executor"}),
    }


__all__ = [
    "CONTRACT_VERSION",
    "DEFAULT_ENDPOINT",
    "GOOGLE_URL",
    "DashboardToEndpointFetchProofPolicy",
    "build_dashboard_fetch_request_payload",
    "execute_fetch_payload_against_endpoint_contract",
    "google_fetch_proof_executor",
    "run_dashboard_to_endpoint_google_fetch_proof",
    "run_dashboard_to_endpoint_manual_enable_block_proof",
]
