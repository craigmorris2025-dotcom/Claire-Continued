
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.proof.platform_endpoint_smoke_proof import (
    build_platform_endpoint_smoke_proof,
    platform_endpoint_smoke_summary,
)

router = APIRouter(tags=["Platform Proof"])


@router.get("/proof/platform-smoke")
def get_platform_endpoint_smoke_proof():
    return build_platform_endpoint_smoke_proof()


@router.get("/proof/platform-smoke/summary")
def get_platform_endpoint_smoke_summary():
    return platform_endpoint_smoke_summary()


@router.post("/proof/platform-smoke/rebuild")
def rebuild_platform_endpoint_smoke_proof():
    return build_platform_endpoint_smoke_proof()


@router.get("/platform/stop-go")
def get_platform_stop_go():
    return platform_endpoint_smoke_summary()
