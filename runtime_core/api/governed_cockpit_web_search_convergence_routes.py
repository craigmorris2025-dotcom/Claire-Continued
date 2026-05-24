from __future__ import annotations

from fastapi import APIRouter

from runtime_core.governance.governed_cockpit_web_search_convergence import (
    build_actions,
    build_cards,
    build_convergence_payload,
    build_status,
    build_stop_gate,
)


router = APIRouter(tags=["cockpit-web-search-convergence"])


@router.get("/api/cockpit/convergence/payload")
def cockpit_convergence_payload():
    return build_convergence_payload()


@router.get("/api/cockpit/convergence/cards")
def cockpit_convergence_cards():
    return {"cards": build_cards()}


@router.get("/api/cockpit/convergence/actions")
def cockpit_convergence_actions():
    actions = build_actions()
    return {"actions": actions, "count": len(actions), "execution_enabled": False}


@router.get("/api/cockpit/convergence/status")
def cockpit_convergence_status():
    return build_status()


@router.get("/api/cockpit/convergence/stop-gate")
def cockpit_convergence_stop_gate():
    return build_stop_gate()


@router.get("/api/cockpit/web-search/readiness")
def cockpit_web_search_readiness():
    payload = build_convergence_payload()
    return {
        "readiness": payload["readiness"],
        "highest_stage": payload["highest_stage"],
        "status": payload["status"],
        "cards": payload["governed_web_cards"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }


@router.get("/api/cockpit/dashboard-sync/payload")
def cockpit_dashboard_sync_payload():
    return build_convergence_payload()


@router.get("/api/internet/dashboard-sync/payload")
def internet_dashboard_sync_payload():
    return build_convergence_payload()


@router.get("/api/internet/s928-stop-gate")
def internet_s928_stop_gate():
    return build_stop_gate()
