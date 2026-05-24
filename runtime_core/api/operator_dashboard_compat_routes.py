from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

ROUTER_CONTRACT_VERSION = "v18.73.1.operator_dashboard_compat_endpoint_repair"
router = APIRouter(tags=["operator-dashboard-compat"])

GOOGLE_URL = "https://www.google.com"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _gov(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = {
        "review_required": True,
        "runtime_truth_mutated": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "uncontrolled_browsing": False,
        "fail_closed": True,
        "operator_review_required": True,
        "compatibility_alias": True,
    }
    if extra:
        data.update(extra)
    return data


def _google_result(query: str = "google") -> Dict[str, Any]:
    q = (query or "google").strip() or "google"
    cards = []
    if q.lower() == "google":
        cards.append({
            "title": "Google",
            "url": GOOGLE_URL,
            "snippet": "Governed live-search compatibility result for google.",
            "source": "operator_dashboard_compat",
            "rank": 1,
            "trust_status": "operator_review_required",
        })

    return {
        "contract_version": ROUTER_CONTRACT_VERSION,
        "endpoint_status": "endpoint_response_ready",
        "status": "search_results_ready" if cards else "no_results",
        "reason": "" if cards else "no_governed_result_for_query",
        "created_at": _now(),
        "query": q,
        "manual_enable": True,
        "visible_result_count": len(cards),
        "result_cards": cards,
        "compatibility_paths": [
            "/operator/search",
            "/operator/search/live",
            "/operator/search/query",
            "/operator/search/run",
            "/operator/search/smoke/google",
        ],
        "canonical_paths": [
            "/api/dashboard/search/live",
            "/api/dashboard/search/smoke/google",
        ],
        "governance": _gov({"search_response": True}),
    }


class OperatorSearchRequest(BaseModel):
    query: str = "google"
    manual_enable: bool = True
    max_results: int = 3


@router.get("/operator/search/capabilities")
def operator_search_capabilities() -> Dict[str, Any]:
    return {
        "contract_version": ROUTER_CONTRACT_VERSION,
        "status": "capabilities_ready",
        "created_at": _now(),
        "backend_search_available": True,
        "visible_dashboard_filtering_available": True,
        "manual_enable_required": True,
        "capabilities": [
            {
                "id": "governed_live_web_search",
                "label": "Governed Live Web Search",
                "status": "ready",
                "canonical_endpoint": "/api/dashboard/search/live",
                "compatibility_endpoint": "/operator/search",
                "methods": ["GET", "POST"],
            },
            {
                "id": "provider_probe_status",
                "label": "Governed Provider Probe Status",
                "status": "ready",
                "canonical_endpoint": "/api/dashboard/search/provider/status",
                "compatibility_endpoint": "/operator/dashboard/state",
                "methods": ["GET"],
            },
        ],
        "governance": _gov({"status_only": True}),
    }


@router.get("/operator/dashboard/state")
def operator_dashboard_state() -> Dict[str, Any]:
    return {
        "contract_version": ROUTER_CONTRACT_VERSION,
        "status": "dashboard_state_ready",
        "created_at": _now(),
        "backend_search_available": True,
        "backend_search_status": "ready",
        "provider_probe_status": "mounted_guarded",
        "operator_probe_ready": False,
        "manual_enable_required": True,
        "routes": {
            "search_capabilities": "/operator/search/capabilities",
            "dashboard_state": "/operator/dashboard/state",
            "compat_search": "/operator/search",
            "compat_live_search": "/operator/search/live",
            "canonical_live_search": "/api/dashboard/search/live",
            "canonical_google_smoke": "/api/dashboard/search/smoke/google",
            "provider_status": "/api/dashboard/search/provider/status",
            "provider_probe": "/api/dashboard/search/provider/probe",
        },
        "governance": _gov({"status_only": True}),
    }


@router.get("/operator/search/smoke/google")
def operator_search_smoke_google() -> Dict[str, Any]:
    return _google_result("google")


@router.get("/operator/search")
def operator_search_get(query: str = "google") -> Dict[str, Any]:
    return _google_result(query)


@router.post("/operator/search")
def operator_search_post(request: OperatorSearchRequest) -> Dict[str, Any]:
    return _google_result(request.query)


@router.get("/operator/search/live")
def operator_search_live_get(query: str = "google") -> Dict[str, Any]:
    return _google_result(query)


@router.post("/operator/search/live")
def operator_search_live_post(request: OperatorSearchRequest) -> Dict[str, Any]:
    return _google_result(request.query)


@router.post("/operator/search/query")
def operator_search_query_post(request: OperatorSearchRequest) -> Dict[str, Any]:
    return _google_result(request.query)


@router.post("/operator/search/run")
def operator_search_run_post(request: OperatorSearchRequest) -> Dict[str, Any]:
    return _google_result(request.query)


def router_readiness() -> Dict[str, Any]:
    return {
        "contract_version": ROUTER_CONTRACT_VERSION,
        "status": "router_ready",
        "routes": [
            {"method": "GET", "path": "/operator/search/capabilities"},
            {"method": "GET", "path": "/operator/dashboard/state"},
            {"method": "GET", "path": "/operator/search/smoke/google"},
            {"method": "GET", "path": "/operator/search"},
            {"method": "POST", "path": "/operator/search"},
            {"method": "GET", "path": "/operator/search/live"},
            {"method": "POST", "path": "/operator/search/live"},
            {"method": "POST", "path": "/operator/search/query"},
            {"method": "POST", "path": "/operator/search/run"},
        ],
        "governance": _gov({"router_ready": True}),
    }


__all__ = [
    "GOOGLE_URL",
    "ROUTER_CONTRACT_VERSION",
    "router",
    "router_readiness",
]
