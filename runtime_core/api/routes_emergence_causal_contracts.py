from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from runtime_core.emergence.causal_contracts import assess_causal_emergence, build_causal_contract


router = APIRouter(tags=["Emergence Causal Contracts"])


@router.get("/api/emergence/causal-contract")
def emergence_causal_contract() -> dict[str, Any]:
    return build_causal_contract()


@router.post("/api/emergence/causal-assess")
async def emergence_causal_assess(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return assess_causal_emergence(payload if isinstance(payload, dict) else {})
