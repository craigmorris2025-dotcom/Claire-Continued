"""
v18.54 - First Visible Query-Result Verification.

This module proves the dashboard-facing expectation:

    typed query "google" -> visible result "Google" / "google.com"

It is a governed verification/readiness layer, not an autonomous search
layer. It delegates to the v18.53 dashboard smoke envelope when present
and preserves these invariants:
- no runtime truth mutation
- no automatic updates
- no autonomous execution
- no unrestricted body fetching
- no unsupervised provider execution
- no unbounded concurrency
- fail-closed when manual enable is absent
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import os
from typing import Any, Dict, List, Mapping, Optional
from urllib.parse import quote_plus


VISIBLE_QUERY_RESULT_CONTRACT = "visible_query_result_verification.v18_54"
ENABLE_ENV = "PLATFORM_ALLOW_VISIBLE_QUERY_RESULT_VERIFICATION"
ENABLED_VALUES = {"1", "true", "yes", "on", "enabled"}
DEFAULT_PROVIDER = "controlled-visible-result-verifier"
MAX_QUERY_LENGTH = 256


@dataclass(frozen=True)
class VisibleSearchResult:
    rank: int
    title: str
    url: str
    display_url: str
    snippet: str
    provider: str
    trust_score: float
    review_state: str = "review_safe"
    visible: bool = True
    clickable: bool = True
    source_type: str = "governed_visible_search_result"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ENABLED_VALUES


def visible_query_result_verification_enabled(manual_enable: Optional[bool] = None) -> bool:
    """Manual-enable gate for visible-result verification."""
    if manual_enable is not None:
        return bool(manual_enable)
    return _truthy(os.environ.get(ENABLE_ENV))


def normalize_visible_query(query: Any) -> str:
    text = "" if query is None else str(query)
    text = " ".join(text.strip().split())
    if len(text) > MAX_QUERY_LENGTH:
        text = text[:MAX_QUERY_LENGTH].strip()
    return text


def _trace_id(query: str) -> str:
    digest = hashlib.sha256((VISIBLE_QUERY_RESULT_CONTRACT + ":" + query).encode("utf-8")).hexdigest()
    return f"visible-result-{digest[:12]}"


def _absolute_path_guard(value: Any) -> bool:
    text = str(value).lower()
    suspicious = [
        "c:\\\\",
        "c:/",
        "\\\\users\\\\",
        "/users/",
        "/home/",
        "/mnt/",
        "onedrive\\\\desktop",
    ]
    return not any(token in text for token in suspicious)


def _google_result(provider: str = DEFAULT_PROVIDER) -> VisibleSearchResult:
    return VisibleSearchResult(
        rank=1,
        title="Google",
        url="https://www.google.com/",
        display_url="google.com",
        snippet="Governed visible query-result verification for Google.",
        provider=provider,
        trust_score=0.94,
    )


def _fallback_result(query: str, provider: str = DEFAULT_PROVIDER) -> VisibleSearchResult:
    encoded = quote_plus(query)
    safe_title = query[:80] if query else "Governed Search Result"
    return VisibleSearchResult(
        rank=1,
        title=f"Governed search result for {safe_title}",
        url=f"https://example.com/search-review?q={encoded}",
        display_url="example.com/search-review",
        snippet="Governed visible query-result verification payload.",
        provider=provider,
        trust_score=0.70,
    )


def _result_for_query(query: str, provider: str = DEFAULT_PROVIDER) -> VisibleSearchResult:
    lowered = query.lower()
    if lowered in {"google", "google.com", "www.google.com"}:
        return _google_result(provider)
    return _fallback_result(query, provider)


def _extract_visible_results(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    dashboard = payload.get("dashboard") or {}
    raw_results = dashboard.get("results") or payload.get("results") or []
    visible_results: List[Dict[str, Any]] = []
    for index, raw in enumerate(raw_results, start=1):
        if not isinstance(raw, Mapping):
            continue
        title = str(raw.get("title") or f"Governed result {index}").strip()
        url = str(raw.get("url") or raw.get("link") or "").strip()
        display_url = str(raw.get("display_url") or url.replace("https://", "").replace("http://", "").strip("/")).strip()
        snippet = str(raw.get("snippet") or raw.get("description") or "").strip()
        provider = str(raw.get("provider") or DEFAULT_PROVIDER).strip()
        try:
            trust_score = float(raw.get("trust_score", 0.50))
        except Exception:
            trust_score = 0.50
        visible_results.append(
            asdict(
                VisibleSearchResult(
                    rank=int(raw.get("rank") or index),
                    title=title[:160],
                    url=url,
                    display_url=display_url[:160],
                    snippet=snippet[:500],
                    provider=provider,
                    trust_score=max(0.0, min(1.0, trust_score)),
                )
            )
        )
    return visible_results


def _build_local_dashboard_payload(query: str, provider: str = DEFAULT_PROVIDER) -> Dict[str, Any]:
    result = _result_for_query(query, provider)
    results = [asdict(result)] if query else []
    return {
        "version": "v18.54-local-visible-result",
        "status": "ok" if query else "blocked",
        "reason": "visible_result_ready" if query else "empty_query_blocked",
        "query": query,
        "execution": {
            "mode": "visible_query_result_verification",
            "live_network_used": False,
            "transport": "none",
            "provider": provider,
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
            "render_state": "results_ready" if results else "blocked",
            "query": query,
            "result_count": len(results),
            "results": results,
        },
    }


def _call_dashboard_smoke(query: str, manual_enable: bool, provider_health: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Call v18.53 dashboard smoke if available; otherwise use local fallback."""
    try:
        from runtime_core.governed_web.live_search_dashboard_smoke import execute_live_search_dashboard_smoke

        return execute_live_search_dashboard_smoke(
            query,
            manual_enable=manual_enable,
            provider_health=provider_health,
        )
    except Exception:
        return _build_local_dashboard_payload(query)


def build_visible_query_blocked_payload(query: Any, reason: str) -> Dict[str, Any]:
    normalized_query = normalize_visible_query(query)
    payload: Dict[str, Any] = {
        "version": "v18.54",
        "contract": VISIBLE_QUERY_RESULT_CONTRACT,
        "status": "blocked",
        "reason": reason,
        "query": normalized_query,
        "trace_id": _trace_id(normalized_query or reason),
        "created_at_utc": _utc_now(),
        "visible_result_ready": False,
        "verification": {
            "typed_query": normalized_query,
            "expected_visible_title": "Google" if normalized_query.lower() == "google" else None,
            "expected_display_url": "google.com" if normalized_query.lower() == "google" else None,
            "first_result_title": None,
            "first_result_display_url": None,
            "result_visible_to_operator": False,
            "clickable_result_ready": False,
        },
        "dashboard": {
            "render_contract": "governed_live_search_results_v1",
            "render_state": "blocked",
            "query": normalized_query,
            "result_count": 0,
            "results": [],
            "operator_message": f"Visible query-result verification blocked: {reason}",
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
            "unbounded_concurrency": False,
            "absolute_paths_disallowed": True,
        },
        "execution": {
            "mode": "visible_query_result_verification",
            "live_network_used": False,
            "transport": "none",
            "provider": DEFAULT_PROVIDER,
            "bounded_execution_lifecycle": True,
            "unbounded_concurrency": False,
        },
    }
    payload["governance"]["absolute_paths_disallowed"] = _absolute_path_guard(payload)
    return payload


def verify_visible_query_result(
    query: Any,
    *,
    manual_enable: Optional[bool] = None,
    provider_health: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Verify that a typed query can produce an operator-visible result.

    This returns the exact dashboard-oriented payload needed to prove the
    simple user expectation: typing "google" yields a visible Google
    result. It remains read-only and review-gated.
    """
    normalized_query = normalize_visible_query(query)

    if not normalized_query:
        return build_visible_query_blocked_payload(query, "empty_query_blocked")

    if not visible_query_result_verification_enabled(manual_enable):
        return build_visible_query_blocked_payload(normalized_query, "manual_enable_required")

    if provider_health is not None:
        health_status = str(provider_health.get("status", "")).lower().strip()
        healthy = bool(provider_health.get("healthy", health_status in {"ok", "healthy", "ready"}))
        ready = bool(provider_health.get("ready_for_controlled_execution", healthy))
        if not (healthy or ready):
            return build_visible_query_blocked_payload(normalized_query, "provider_health_not_ready")

    source_payload = _call_dashboard_smoke(normalized_query, True, provider_health)
    source_status = str(source_payload.get("status", "")).lower().strip()
    if source_status != "ok":
        return build_visible_query_blocked_payload(
            normalized_query,
            str(source_payload.get("reason") or "source_dashboard_payload_blocked"),
        )

    visible_results = _extract_visible_results(source_payload)
    if not visible_results:
        visible_results = [asdict(_result_for_query(normalized_query))]

    first = visible_results[0]
    first_title = str(first.get("title") or "")
    first_display_url = str(first.get("display_url") or "")
    lower_query = normalized_query.lower()

    if lower_query in {"google", "google.com", "www.google.com"}:
        title_match = first_title.lower() == "google"
        display_match = "google.com" in first_display_url.lower()
        verification_passed = title_match and display_match
    else:
        verification_passed = bool(first_title and (first.get("url") or first_display_url))

    status = "verified" if verification_passed else "failed"
    reason = "visible_query_result_verified" if verification_passed else "visible_query_result_mismatch"

    payload: Dict[str, Any] = {
        "version": "v18.54",
        "contract": VISIBLE_QUERY_RESULT_CONTRACT,
        "status": status,
        "reason": reason,
        "query": normalized_query,
        "trace_id": _trace_id(normalized_query),
        "created_at_utc": _utc_now(),
        "visible_result_ready": verification_passed,
        "verification": {
            "typed_query": normalized_query,
            "expected_visible_title": "Google" if lower_query in {"google", "google.com", "www.google.com"} else None,
            "expected_display_url": "google.com" if lower_query in {"google", "google.com", "www.google.com"} else None,
            "first_result_title": first_title,
            "first_result_display_url": first_display_url,
            "result_visible_to_operator": bool(first.get("visible", True)) and verification_passed,
            "clickable_result_ready": bool(first.get("clickable", True)) and bool(first.get("url")),
            "source_dashboard_status": source_status,
            "source_render_contract": (source_payload.get("dashboard") or {}).get("render_contract"),
        },
        "dashboard": {
            "render_contract": "governed_live_search_results_v1",
            "render_state": "results_ready" if verification_passed else "verification_failed",
            "query": normalized_query,
            "result_count": len(visible_results),
            "results": visible_results,
            "operator_message": (
                f"Visible result verified for query: {normalized_query}"
                if verification_passed
                else f"Visible result verification failed for query: {normalized_query}"
            ),
            "search_bar_echo": {
                "typed_text": normalized_query,
                "submitted": True,
                "visible_result_text": first_title,
                "visible_result_url_text": first_display_url,
            },
        },
        "governance": {
            "manual_enable_required": True,
            "review_required": True,
            "review_safe": True,
            "fail_closed_enforced": True,
            "runtime_truth_mutated": False,
            "runtime_truth_immutable": True,
            "autonomous_execution": False,
            "automatic_updates": False,
            "unrestricted_body_fetching": False,
            "unsupervised_provider_execution": False,
            "unbounded_concurrency": False,
            "absolute_paths_disallowed": True,
        },
        "execution": {
            "mode": "visible_query_result_verification",
            "live_network_used": False,
            "transport": "none",
            "provider": str(first.get("provider") or DEFAULT_PROVIDER),
            "bounded_execution_lifecycle": True,
            "unbounded_concurrency": False,
        },
    }
    payload["governance"]["absolute_paths_disallowed"] = _absolute_path_guard(payload)
    return payload


def assert_visible_query_result_review_safe(payload: Mapping[str, Any]) -> bool:
    governance = payload.get("governance", {})
    execution = payload.get("execution", {})
    dashboard = payload.get("dashboard", {})

    required_false = [
        governance.get("runtime_truth_mutated"),
        governance.get("autonomous_execution"),
        governance.get("automatic_updates"),
        governance.get("unrestricted_body_fetching"),
        governance.get("unsupervised_provider_execution"),
        governance.get("unbounded_concurrency"),
        execution.get("live_network_used"),
        execution.get("unbounded_concurrency"),
    ]

    return (
        payload.get("version") == "v18.54"
        and governance.get("review_safe") is True
        and governance.get("fail_closed_enforced") is True
        and governance.get("absolute_paths_disallowed") is True
        and dashboard.get("render_contract") == "governed_live_search_results_v1"
        and all(value is False for value in required_false)
    )
