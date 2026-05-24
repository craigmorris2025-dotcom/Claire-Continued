from __future__ import annotations

from fastapi import APIRouter

from runtime_core.governance.governed_provider_capability_map import (
    build_provider_capability_actions,
    build_provider_capability_cards,
    get_provider_capability_map,
    get_provider_capability_payload,
    get_provider_capability_policy,
    get_provider_capability_status,
    get_provider_capability_stop_gate,
)

router = APIRouter(tags=["governed-provider-capability"])


@router.get("/api/search/providers/capability-map")
def provider_capability_map():
    return get_provider_capability_map()


@router.get("/api/search/providers/capability/cards")
def provider_capability_cards():
    return {"status": "ready", "cards": build_provider_capability_cards()}


@router.get("/api/search/providers/capability/actions")
def provider_capability_actions():
    return {"status": "ready", "actions": build_provider_capability_actions()}


@router.get("/api/search/providers/capability/policy")
def provider_capability_policy():
    return get_provider_capability_policy()


@router.get("/api/search/providers/capability/status")
def provider_capability_status():
    return get_provider_capability_status()


@router.get("/api/search/providers/capability/payload")
def provider_capability_payload():
    return get_provider_capability_payload()


@router.get("/api/search/providers/capability/stop-gate")
def provider_capability_stop_gate():
    return get_provider_capability_stop_gate()


@router.get("/api/sources/providers/capability-map")
def source_provider_capability_map_alias():
    return get_provider_capability_map()


@router.get("/api/sources/providers/capability/cards")
def source_provider_capability_cards_alias():
    return {"status": "ready", "cards": build_provider_capability_cards()}


@router.get("/api/sources/providers/capability/actions")
def source_provider_capability_actions_alias():
    return {"status": "ready", "actions": build_provider_capability_actions()}
