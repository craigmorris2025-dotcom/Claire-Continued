from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from runtime_core.lifecycle.route_contracts import (
    build_center_route_contract,
    build_route_contracts,
    select_route_by_center_contract,
)


router = APIRouter(tags=["Lifecycle Route Contracts"])


@router.get("/api/lifecycle/center-route-contract")
def center_route_contract() -> dict[str, Any]:
    return build_center_route_contract()


@router.get("/api/lifecycle/route-contracts")
def lifecycle_route_contracts() -> dict[str, Any]:
    return build_route_contracts()


@router.post("/api/lifecycle/select-route")
async def lifecycle_select_route(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return select_route_by_center_contract(payload if isinstance(payload, dict) else {})
