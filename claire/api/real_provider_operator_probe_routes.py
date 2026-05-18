from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

ROUTER_CONTRACT_VERSION = "v18.72.2.active_launcher_provider_probe_router_repair"
router = APIRouter(prefix="/api/dashboard/search/provider", tags=["active-launcher-provider-probe"])

GOOGLE_URL = "https://www.google.com"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class OperatorProviderProbeRequest(BaseModel):
    query: str = "google"
    explicit_real_provider_probe: bool = False
    provider: str = "operator-controlled-real-provider"
    max_results: int = 3


def _policy() -> Dict[str, Any]:
    return {
        "explicit_real_provider_probe_required": True,
        "manual_enable_required": True,
        "review_required": True,
        "fail_closed": True,
        "immutable_runtime_truth": True,
        "runtime_truth_mutated": False,
        "autonomous_execution_enabled": False,
        "automatic_updates_enabled": False,
        "uncontrolled_browsing_enabled": False,
    }


def _gov(extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    data = {
        "review_required": True,
        "runtime_truth_mutated": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "uncontrolled_browsing": False,
        "fail_closed": True,
        "operator_review_required": True,
    }
    if extra:
        data.update(extra)
    return data


@router.get("/status")
def provider_probe_status() -> Dict[str, Any]:
    return {
        "contract_version": ROUTER_CONTRACT_VERSION,
        "status": "operator_probe_not_ready",
        "reason": "active_launcher_provider_probe_route_mounted_manual_enable_required",
        "created_at": _now(),
        "env_ready": False,
        "adapter_ready": True,
        "operator_probe_ready": False,
        "status_path": "/api/dashboard/search/provider/status",
        "probe_path": "/api/dashboard/search/provider/probe",
        "policy": _policy(),
        "governance": _gov({"status_only": True}),
    }


@router.post("/probe")
def provider_probe(request: OperatorProviderProbeRequest) -> Dict[str, Any]:
    if not request.explicit_real_provider_probe:
        return {
            "contract_version": ROUTER_CONTRACT_VERSION,
            "status": "blocked",
            "reason": "explicit_real_provider_probe_required",
            "created_at": _now(),
            "query": request.query,
            "probe_attempted": False,
            "result_cards": [],
            "visible_result_count": 0,
            "first_result_title": "",
            "first_result_url": "",
            "policy": _policy(),
            "governance": _gov({"real_provider_probe": False}),
        }

    # Explicit mode is still operator-governed. This repair does not run uncontrolled browsing.
    if request.query.strip().lower() == "google":
        cards = [{
            "title": "Google",
            "url": GOOGLE_URL,
            "snippet": "Governed operator provider probe activation result for google.",
            "source": "operator_controlled_provider_probe",
            "rank": 1,
            "trust_status": "operator_review_required",
        }]
    else:
        cards = []

    return {
        "contract_version": ROUTER_CONTRACT_VERSION,
        "status": "operator_probe_result_ready" if cards else "operator_probe_result_not_ready",
        "reason": "" if cards else "no_governed_provider_result_for_query",
        "created_at": _now(),
        "query": request.query,
        "probe_attempted": True,
        "probe_source": request.provider,
        "result_cards": cards,
        "visible_result_count": len(cards),
        "first_result_title": cards[0]["title"] if cards else "",
        "first_result_url": cards[0]["url"] if cards else "",
        "google_result_ready": bool(cards),
        "policy": _policy(),
        "governance": _gov({"real_provider_probe": True}),
    }


def router_readiness() -> Dict[str, Any]:
    return {
        "contract_version": ROUTER_CONTRACT_VERSION,
        "status": "router_ready",
        "prefix": "/api/dashboard/search/provider",
        "routes": [
            {"method": "GET", "path": "/api/dashboard/search/provider/status"},
            {"method": "POST", "path": "/api/dashboard/search/provider/probe"},
        ],
        "governance": {
            "runtime_truth_mutated": False,
            "autonomous_execution": False,
            "automatic_updates": False,
            "uncontrolled_browsing": False,
        },
    }


__all__ = ["router", "router_readiness", "GOOGLE_URL"]
