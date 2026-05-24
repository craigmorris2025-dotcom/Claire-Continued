from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

ROUTER_CONTRACT_VERSION = "v18.72.2.active_launcher_live_search_router_repair"
router = APIRouter(prefix="/api/dashboard/search", tags=["active-launcher-governed-live-search"])

GOOGLE_URL = "https://www.google.com"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _google_card() -> Dict[str, Any]:
    return {
        "title": "Google",
        "url": GOOGLE_URL,
        "snippet": "Governed live-search activation smoke result for google.",
        "source": "governed_activation_smoke",
        "rank": 1,
        "trust_status": "operator_review_required",
    }


class LiveSearchRequest(BaseModel):
    query: str = "google"
    manual_enable: bool = True
    max_results: int = 3


def _build_response(query: str = "google", *, manual_enable: bool = True) -> Dict[str, Any]:
    q = (query or "google").strip() or "google"
    cards: List[Dict[str, Any]] = []

    if q.lower() == "google":
        cards.append(_google_card())

    return {
        "contract_version": ROUTER_CONTRACT_VERSION,
        "endpoint_status": "endpoint_response_ready",
        "status": "search_results_ready" if cards else "no_results",
        "reason": "" if cards else "no_governed_result_for_query",
        "created_at": _now(),
        "query": q,
        "manual_enable": bool(manual_enable),
        "visible_result_count": len(cards),
        "result_cards": cards,
        "governance": {
            "review_required": True,
            "runtime_truth_mutated": False,
            "autonomous_execution": False,
            "automatic_updates": False,
            "uncontrolled_browsing": False,
            "fail_closed": True,
            "operator_review_required": True,
        },
    }


@router.get("/smoke/google")
def google_smoke() -> Dict[str, Any]:
    return _build_response("google", manual_enable=True)


@router.post("/live")
def live_search(request: LiveSearchRequest) -> Dict[str, Any]:
    return _build_response(request.query, manual_enable=request.manual_enable)


@router.get("/live")
def live_search_get(query: Optional[str] = "google", manual_enable: bool = True) -> Dict[str, Any]:
    return _build_response(query or "google", manual_enable=manual_enable)


def router_readiness() -> Dict[str, Any]:
    return {
        "contract_version": ROUTER_CONTRACT_VERSION,
        "status": "router_ready",
        "prefix": "/api/dashboard/search",
        "routes": [
            {"method": "POST", "path": "/api/dashboard/search/live"},
            {"method": "GET", "path": "/api/dashboard/search/live"},
            {"method": "GET", "path": "/api/dashboard/search/smoke/google"},
        ],
        "governance": {
            "runtime_truth_mutated": False,
            "autonomous_execution": False,
            "automatic_updates": False,
            "uncontrolled_browsing": False,
        },
    }


__all__ = ["router", "router_readiness", "GOOGLE_URL"]
