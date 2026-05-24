from __future__ import annotations

from fastapi import APIRouter

from runtime_core.governance.governed_source_policy_controls import (
    build_source_policy_actions,
    build_source_policy_cards,
    get_source_policy,
    get_source_policy_controls,
    get_source_policy_payload,
    get_source_policy_status,
    get_source_policy_stop_gate,
)

router = APIRouter(tags=["governed-source-policy-controls"])


@router.get("/api/sources/policy/controls")
def source_policy_controls():
    return get_source_policy_controls()


@router.get("/api/sources/policy/cards")
def source_policy_cards():
    return {"status": "ready", "cards": build_source_policy_cards()}


@router.get("/api/sources/policy/actions")
def source_policy_actions():
    return {"status": "ready", "actions": build_source_policy_actions()}


@router.get("/api/sources/policy/rules")
def source_policy_rules():
    return get_source_policy()


@router.get("/api/sources/policy/status")
def source_policy_status():
    return get_source_policy_status()


@router.get("/api/sources/policy/payload")
def source_policy_payload():
    return get_source_policy_payload()


@router.get("/api/sources/policy/stop-gate")
def source_policy_stop_gate():
    return get_source_policy_stop_gate()


@router.get("/api/search/policy/controls")
def search_policy_controls_alias():
    return get_source_policy_controls()


@router.get("/api/search/policy/cards")
def search_policy_cards_alias():
    return {"status": "ready", "cards": build_source_policy_cards()}


@router.get("/api/search/policy/actions")
def search_policy_actions_alias():
    return {"status": "ready", "actions": build_source_policy_actions()}
