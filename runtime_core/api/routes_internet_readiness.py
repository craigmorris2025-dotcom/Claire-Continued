
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.internet_readiness.readiness_verifier import (
    build_internet_readiness,
    internet_readiness_summary,
)

router = APIRouter(tags=["Internet Readiness"])


@router.get("/internet/readiness")
def get_internet_readiness():
    return build_internet_readiness()


@router.get("/internet/readiness/summary")
def get_internet_readiness_summary():
    return internet_readiness_summary()


@router.post("/internet/readiness/rebuild")
def rebuild_internet_readiness():
    return build_internet_readiness()


@router.get("/internet/operations/status")
def get_internet_operations_status():
    return internet_readiness_summary()
