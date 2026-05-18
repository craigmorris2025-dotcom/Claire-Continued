from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from claire.governance.governed_source_registry import (
    get_source_actions_payload,
    get_source_cards_payload,
    get_source_policy_payload,
    get_source_registry_payload,
)

router = APIRouter(prefix="/api/sources", tags=["governed-source-registry"])


@router.get("/registry")
def read_source_registry() -> dict[str, Any]:
    return get_source_registry_payload()


@router.get("/cards")
def read_source_cards() -> dict[str, Any]:
    return get_source_cards_payload()


@router.get("/actions")
def read_source_actions() -> dict[str, Any]:
    return get_source_actions_payload()


@router.get("/policy")
def read_source_policy() -> dict[str, Any]:
    return get_source_policy_payload()


@router.get("/status")
def read_source_status() -> dict[str, Any]:
    payload = get_source_registry_payload()
    return {
        "version": payload["version"],
        "readiness": payload["readiness"],
        "summary": payload["summary"],
        "blocked_capabilities": payload["blocked_capabilities"],
        "stop_gate": payload["stop_gate"],
    }

