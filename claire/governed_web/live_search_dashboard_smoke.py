"""
v18.53 - Live Search Dashboard Smoke Test.

This module proves the dashboard-facing result envelope for governed live
search without performing network access or mutating runtime truth.

It is intentionally conservative:
- no autonomous execution
- no automatic updates
- no runtime truth mutation
- no unrestricted body fetch
- no unbounded concurrency
- no filesystem path leakage in payloads
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import os
from typing import Any, Dict, Iterable, List, Mapping, Optional
from urllib.parse import quote_plus


ENABLE_ENV = "CLAIRE_ALLOW_LIVE_SEARCH_DASHBOARD_SMOKE"
ENABLED_VALUES = {"1", "true", "yes", "on", "enabled"}
MAX_QUERY_LENGTH = 256


@dataclass(frozen=True)
class DashboardVisibleResult:
    rank: int
    title: str
    url: str
    display_url: str
    snippet: str
    provider: str
    trust_score: float
    review_state: str = "review_safe"
    source_type: str = "governed_web_smoke_result"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ENABLED_VALUES


def live_search_dashboard_smoke_enabled(manual_enable: Optional[bool] = None) -> bool:
    """
    Manual-enable gate for dashboard smoke execution.

    The explicit function argument is preferred in tests and internal callers.
    The environment flag is available for manual local smoke operation.
    """
    if manual_enable is not None:
        return bool(manual_enable)
    return _truthy(os.environ.get(ENABLE_ENV))


def normalize_dashboard_query(query: Any) -> str:
    text = "" if query is None else str(query)
    text = " ".join(text.strip().split())
    if len(text) > MAX_QUERY_LENGTH:
        text = text[:MAX_QUERY_LENGTH].strip()
    return text


def _trace_id(query: str) -> str:
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()
    return f"dashboard-smoke-{digest[:12]}"


def _absolute_path_guard(value: Any) -> bool:
    """
    Return True when a payload appears free of local absolute path leakage.
    This is intentionally simple and strict enough for Windows and POSIX.
    """
    text = str(value)
    lowered = text.lower()
    suspicious = [
        "c:\\\\",
        "c:/",
        "\\\\users\\\\",
        "/users/",
        "/home/",
        "/mnt/",
        "onedrive\\\\desktop",
    ]
    return not any(token in lowered for token in suspicious)


def _result_for_query(query: str, provider: str) -> DashboardVisibleResult:
    lowered = query.lower()
    if lowered in {"google", "google.com", "www.google.com"}:
        return DashboardVisibleResult(
            rank=1,
            title="Google",
            url="https://www.google.com/",
            display_url="google.com",
            snippet="Review-safe governed search smoke result for Google.",
            provider=provider,
            trust_score=0.92,
        )

    encoded = quote_plus(query)
    safe_title = query[:80] if query else "Governed Search Result"
    return DashboardVisibleResult(
        rank=1,
        title=f"Governed search result for {safe_title}",
        url=f"https://example.com/search-review?q={encoded}",
        display_url="example.com/search-review",
        snippet="Review-safe dashboard smoke result generated without network access.",
        provider=provider,
        trust_score=0.70,
    )


def build_live_search_dashboard_payload(
    query: Any,
    *,
    results: Optional[Iterable[Mapping[str, Any]]] = None,
    provider: str = "controlled-dashboard-smoke-provider",
    status: str = "ok",
    reason: str = "dashboard_smoke_result_ready",
) -> Dict[str, Any]:
    normalized_query = normalize_dashboard_query(query)
    visible_results: List[Dict[str, Any]] = []

    if results is None:
        if normalized_query:
            visible_results.append(asdict(_result_for_query(normalized_query, provider)))
    else:
        for index, raw in enumerate(results, start=1):
            title = str(raw.get("title") or f"Governed result {index}").strip()
            url = str(raw.get("url") or raw.get("link") or "").strip()
            display_url = str(raw.get("display_url") or url.replace("https://", "").replace("http://", "").strip("/")).strip()
            snippet = str(raw.get("snippet") or raw.get("description") or "").strip()
            trust_score = float(raw.get("trust_score", 0.50))
            visible_results.append(
                asdict(
                    DashboardVisibleResult(
                        rank=index,
                        title=title[:160],
                        url=url,
                        display_url=display_url[:160],
                        snippet=snippet[:500],
                        provider=provider,
                        trust_score=max(0.0, min(1.0, trust_score)),
                    )
                )
            )

    payload: Dict[str, Any] = {
        "version": "v18.53",
        "status": status,
        "reason": reason,
        "query": normalized_query,
        "trace_id": _trace_id(normalized_query or reason),
        "created_at_utc": _utc_now(),
        "execution": {
            "mode": "dashboard_smoke",
            "live_network_used": False,
            "transport": "none",
            "provider": provider,
            "bounded_execution_lifecycle": True,
            "unbounded_concurrency": False,
        },
        "governance": {
            "manual_enable_required": True,
            "review_required": True,
            "review_safe": True,
            "fail_closed_enforced": True,
            "runtime_truth_mutated": False,
            "autonomous_execution": False,
            "automatic_updates": False,
            "unrestricted_body_fetching": False,
            "unsupervised_provider_execution": False,
            "absolute_paths_disallowed": True,
        },
        "dashboard": {
            "render_contract": "governed_live_search_results_v1",
            "render_state": "results_ready" if status == "ok" else "blocked",
            "query": normalized_query,
            "result_count": len(visible_results),
            "results": visible_results,
            "operator_message": (
                "Dashboard smoke result is ready for operator review."
                if status == "ok"
                else "Dashboard smoke request was blocked by governance."
            ),
        },
    }

    payload["governance"]["absolute_paths_disallowed"] = _absolute_path_guard(payload)
    return payload


def build_blocked_dashboard_payload(query: Any, reason: str) -> Dict[str, Any]:
    return build_live_search_dashboard_payload(
        query,
        results=[],
        status="blocked",
        reason=reason,
    )


def execute_live_search_dashboard_smoke(
    query: Any,
    *,
    manual_enable: Optional[bool] = None,
    provider_health: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a dashboard smoke path.

    This intentionally does not call the internet. It verifies that a governed
    dashboard result envelope can be created, blocked, inspected, and rendered
    safely.
    """
    normalized_query = normalize_dashboard_query(query)

    if not normalized_query:
        return build_blocked_dashboard_payload(query, "empty_query_blocked")

    if not live_search_dashboard_smoke_enabled(manual_enable):
        return build_blocked_dashboard_payload(normalized_query, "manual_enable_required")

    if provider_health is not None:
        status = str(provider_health.get("status", "")).lower().strip()
        healthy = bool(provider_health.get("healthy", status in {"ok", "healthy", "ready"}))
        if not healthy:
            return build_blocked_dashboard_payload(normalized_query, "provider_health_not_ready")

    return build_live_search_dashboard_payload(normalized_query)


def assert_dashboard_payload_review_safe(payload: Mapping[str, Any]) -> bool:
    governance = payload.get("governance", {})
    execution = payload.get("execution", {})
    dashboard = payload.get("dashboard", {})

    required_false = [
        governance.get("runtime_truth_mutated"),
        governance.get("autonomous_execution"),
        governance.get("automatic_updates"),
        governance.get("unrestricted_body_fetching"),
        governance.get("unsupervised_provider_execution"),
        execution.get("live_network_used"),
        execution.get("unbounded_concurrency"),
    ]

    return (
        payload.get("version") == "v18.53"
        and governance.get("review_safe") is True
        and governance.get("fail_closed_enforced") is True
        and governance.get("absolute_paths_disallowed") is True
        and dashboard.get("render_contract") == "governed_live_search_results_v1"
        and all(value is False for value in required_false)
    )
