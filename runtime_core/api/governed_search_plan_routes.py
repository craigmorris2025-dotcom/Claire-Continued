from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from runtime_core.governance.governed_search_plan import (
    build_search_plan,
    get_governed_search_actions_payload,
    get_governed_search_cards_payload,
    get_governed_search_plan_payload,
    get_governed_search_policy_payload,
)

router = APIRouter(prefix="/api/search/governed", tags=["governed-search-plan"])


@router.get("/plans")
def read_governed_search_plans() -> dict[str, Any]:
    return get_governed_search_plan_payload()


@router.get("/plans/sample")
def read_governed_search_sample(query: str = "Plan an official documentation search without execution") -> dict[str, Any]:
    return {
        "version": "v19.89.8-S583-S589",
        "readiness": "single_search_plan_ready_execution_blocked",
        "plan": build_search_plan(query),
        "execution_allowed": False,
        "network_request_performed": False,
        "body_read_allowed": False,
    }


@router.get("/cards")
def read_governed_search_cards() -> dict[str, Any]:
    return get_governed_search_cards_payload()


@router.get("/actions")
def read_governed_search_actions() -> dict[str, Any]:
    return get_governed_search_actions_payload()


@router.get("/policy")
def read_governed_search_policy() -> dict[str, Any]:
    return get_governed_search_policy_payload()


@router.get("/status")
def read_governed_search_status() -> dict[str, Any]:
    payload = get_governed_search_plan_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "summary": payload["summary"],
        "blocked_capabilities": payload["blocked_capabilities"],
        "stop_gate": payload["stop_gate"],
    }

