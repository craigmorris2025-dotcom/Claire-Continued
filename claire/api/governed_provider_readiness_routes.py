"""API routes for S597-S603 governed provider/source readiness."""
from __future__ import annotations

from fastapi import APIRouter

from claire.governance.governed_provider_readiness import (
    build_stop_gate,
    provider_actions,
    provider_cards,
    provider_payload,
    provider_policy,
    provider_registry,
    provider_status,
)

router = APIRouter(tags=["Governed Provider Readiness"])


@router.get("/api/search/providers/readiness")
def get_provider_readiness():
    return provider_registry()


@router.get("/api/search/providers/cards")
def get_provider_cards():
    return provider_cards()


@router.get("/api/search/providers/actions")
def get_provider_actions():
    return provider_actions()


@router.get("/api/search/providers/policy")
def get_provider_policy():
    return provider_policy()


@router.get("/api/search/providers/status")
def get_provider_status():
    return provider_status()


@router.get("/api/search/providers/payload")
def get_provider_payload():
    return provider_payload()


@router.get("/api/search/providers/stop-gate")
def get_provider_stop_gate():
    return build_stop_gate()


@router.get("/api/sources/providers/readiness")
def get_source_provider_readiness_alias():
    return provider_registry()


@router.get("/api/sources/providers/cards")
def get_source_provider_cards_alias():
    return provider_cards()


@router.get("/api/sources/providers/actions")
def get_source_provider_actions_alias():
    return provider_actions()
