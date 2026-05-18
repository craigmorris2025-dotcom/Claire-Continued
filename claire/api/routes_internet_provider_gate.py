
from __future__ import annotations

from fastapi import APIRouter

from claire.internet.provider_configuration_gate import (
    build_internet_provider_gate,
    internet_provider_gate_summary,
)

router = APIRouter(tags=["Internet Provider"])


@router.get("/internet/provider-gate")
def get_internet_provider_gate():
    return build_internet_provider_gate()


@router.get("/internet/provider-gate/summary")
def get_internet_provider_gate_summary():
    return internet_provider_gate_summary()


@router.post("/internet/provider-gate/rebuild")
def rebuild_internet_provider_gate():
    return build_internet_provider_gate()


@router.get("/internet/search/provider/status")
def get_internet_search_provider_status():
    return internet_provider_gate_summary()
