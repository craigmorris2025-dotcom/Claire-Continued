"""
Claire Syntalion v18.50
First Fully Governed End-to-End Live Search Flow

Purpose:
- Compose the governed live search layers into one review-safe end-to-end flow.
- Preserve fail-closed behavior, manual enable controls, evidence capture, bounded
  execution lifecycle, and immutable runtime truth.
- This module does not perform autonomous execution, automatic updates, runtime
  truth mutation, or unrestricted network access.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional

try:
    from claire.governed_web.search_evidence_basket import build_governed_search_evidence_basket
except Exception:  # pragma: no cover - installer also writes this module when missing
    build_governed_search_evidence_basket = None  # type: ignore


REQUIRED_MANUAL_FLAGS = (
    "CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE",
    "CLAIRE_ALLOW_CONTROLLED_METADATA_GET",
    "CLAIRE_ALLOW_CONTROLLED_LIMITED_BODY_GET",
    "CLAIRE_ALLOW_REAL_SEARCH_PROVIDER",
)

MAX_QUERY_CHARS = 500
MAX_PROVIDER_RESULTS = 10
FLOW_CONTRACT = "governed_end_to_end_live_search_flow.v18_50"


@dataclass(frozen=True)
class GovernedLiveSearchFlowResult:
    status: str
    query: str
    session_id: str
    provider_status: str
    results: List[Dict[str, Any]]
    evidence_basket: Dict[str, Any]
    dashboard_payload: Dict[str, Any]
    governance_state: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    review_required: bool = True
    runtime_truth_mutation_allowed: bool = False
    automatic_update_allowed: bool = False
    autonomous_execution_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["result_count"] = len(self.results)
        return data


def _clean_text(value: Any, limit: int = MAX_QUERY_CHARS) -> str:
    text = "" if value is None else str(value)
    return " ".join(text.split())[:limit]


def _flag_enabled(env: Mapping[str, str], name: str) -> bool:
    return str(env.get(name, "")).strip().lower() in {"1", "true", "yes", "on", "enabled"}


def build_live_search_governance_state(env: Optional[Mapping[str, str]] = None) -> Dict[str, Any]:
    """Build the operator-visible governance state for the end-to-end flow."""
    import os

    source: Mapping[str, str] = env if env is not None else os.environ
    manual_flags = {name: _flag_enabled(source, name) for name in REQUIRED_MANUAL_FLAGS}
    missing = [name for name, enabled in manual_flags.items() if not enabled]

    return {
        "contract": FLOW_CONTRACT,
        "fail_closed": True,
        "review_required": True,
        "manual_enable_required": True,
        "required_manual_flags": list(REQUIRED_MANUAL_FLAGS),
        "manual_flags": manual_flags,
        "missing_manual_flags": missing,
        "provider_execution_allowed": not missing,
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "autonomous_execution_allowed": False,
        "unrestricted_body_fetch_allowed": False,
        "unbounded_concurrency_allowed": False,
        "max_provider_results": MAX_PROVIDER_RESULTS,
        "bounded_execution_lifecycle": True,
    }


def _normalize_provider_results(raw_results: Optional[Iterable[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    seen_urls = set()
    for index, raw in enumerate(list(raw_results or [])[: MAX_PROVIDER_RESULTS * 2]):
        if len(normalized) >= MAX_PROVIDER_RESULTS:
            break
        if not isinstance(raw, dict):
            continue
        url = _clean_text(raw.get("url") or raw.get("link"), 1000)
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        title = _clean_text(raw.get("title") or raw.get("name") or url, 240)
        snippet = _clean_text(raw.get("snippet") or raw.get("description") or raw.get("summary"), 800)
        provider = _clean_text(raw.get("provider") or raw.get("source") or "controlled-provider", 120)
        try:
            trust_score = float(raw.get("trust_score", raw.get("score", 0.0)))
        except Exception:
            trust_score = 0.0
        trust_score = max(0.0, min(1.0, trust_score))
        normalized.append(
            {
                "rank": int(raw.get("rank") or len(normalized) + 1),
                "title": title,
                "url": url,
                "snippet": snippet,
                "provider": provider,
                "trust_score": trust_score,
                "review_required": True,
                "runtime_truth_mutation_allowed": False,
                "automatic_update_allowed": False,
            }
        )
    return normalized


def _call_provider(provider: Optional[Callable[[str], Iterable[Dict[str, Any]]]], query: str) -> tuple[str, List[Dict[str, Any]], Optional[str]]:
    if provider is None:
        return "no_provider_supplied", [], None
    try:
        raw = provider(query)
    except Exception as exc:  # fail closed, surface error without raising into dashboard
        return "provider_error", [], exc.__class__.__name__
    return "provider_completed", _normalize_provider_results(raw), None


def _build_evidence(query: str, results: List[Dict[str, Any]], governance_state: Dict[str, Any]) -> Dict[str, Any]:
    if build_governed_search_evidence_basket is None:
        return {
            "status": "evidence_basket_unavailable",
            "query": query,
            "evidence_items": [],
            "evidence_count": 0,
            "review_required": True,
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
            "governance_state": dict(governance_state),
        }
    basket = build_governed_search_evidence_basket(query, results, governance_state)
    return basket.to_dict()


def run_fully_governed_live_search_flow(
    query: str,
    provider: Optional[Callable[[str], Iterable[Dict[str, Any]]]] = None,
    env: Optional[Mapping[str, str]] = None,
    session_id: Optional[str] = None,
) -> GovernedLiveSearchFlowResult:
    """Run the first fully governed, review-safe end-to-end live search flow.

    The caller may pass a provider callable. This function only orchestrates
    controlled provider execution after manual-enable gates are satisfied. It
    never mutates runtime truth and never performs automatic updates.
    """
    safe_query = _clean_text(query)
    governance_state = build_live_search_governance_state(env)
    sid = _clean_text(session_id or f"search_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}", 80)

    if not safe_query:
        evidence = _build_evidence("", [], governance_state)
        dashboard = build_dashboard_live_search_payload("blocked_empty_query", "", [], evidence, governance_state, sid)
        return GovernedLiveSearchFlowResult(
            status="blocked_empty_query",
            query="",
            session_id=sid,
            provider_status="not_started",
            results=[],
            evidence_basket=evidence,
            dashboard_payload=dashboard,
            governance_state=governance_state,
        )

    if not governance_state["provider_execution_allowed"]:
        evidence = _build_evidence(safe_query, [], governance_state)
        dashboard = build_dashboard_live_search_payload("blocked_manual_enable_required", safe_query, [], evidence, governance_state, sid)
        return GovernedLiveSearchFlowResult(
            status="blocked_manual_enable_required",
            query=safe_query,
            session_id=sid,
            provider_status="not_started",
            results=[],
            evidence_basket=evidence,
            dashboard_payload=dashboard,
            governance_state=governance_state,
        )

    provider_status, results, provider_error = _call_provider(provider, safe_query)
    if provider_error:
        governance_state["provider_error_type"] = provider_error

    evidence = _build_evidence(safe_query, results, governance_state)
    if provider_status == "provider_completed" and results:
        status = "review_ready"
    elif provider_status == "provider_completed":
        status = "no_results_review_ready"
    elif provider_status == "no_provider_supplied":
        status = "blocked_no_provider"
    else:
        status = "blocked_provider_error"

    dashboard = build_dashboard_live_search_payload(status, safe_query, results, evidence, governance_state, sid)
    return GovernedLiveSearchFlowResult(
        status=status,
        query=safe_query,
        session_id=sid,
        provider_status=provider_status,
        results=results,
        evidence_basket=evidence,
        dashboard_payload=dashboard,
        governance_state=governance_state,
    )


def build_dashboard_live_search_payload(
    status: str,
    query: str,
    results: List[Dict[str, Any]],
    evidence_basket: Dict[str, Any],
    governance_state: Dict[str, Any],
    session_id: str,
) -> Dict[str, Any]:
    """Create the dashboard rendering contract for v18.50."""
    return {
        "contract": "live_dashboard_result_rendering.v18_50",
        "session_id": session_id,
        "status": status,
        "query": query,
        "review_required": True,
        "operator_visible": True,
        "result_count": len(results),
        "results": [dict(item) for item in results],
        "evidence_count": int(evidence_basket.get("evidence_count", 0)),
        "evidence_basket_status": evidence_basket.get("status"),
        "governance_state": dict(governance_state),
        "safety_invariants": {
            "fail_closed": True,
            "manual_enable_controls_preserved": True,
            "runtime_truth_immutable": True,
            "automatic_updates_disabled": True,
            "autonomous_execution_disabled": True,
            "unrestricted_body_fetch_disabled": True,
            "unbounded_concurrency_disabled": True,
        },
    }
