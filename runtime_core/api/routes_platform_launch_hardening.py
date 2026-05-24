
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.platform.launch_hardening import (
    build_platform_launch_hardening,
    platform_launch_hardening_summary,
)

router = APIRouter(tags=["Platform Launch"])


@router.get("/platform/launch-hardening")
def get_platform_launch_hardening():
    return build_platform_launch_hardening()


@router.get("/platform/launch-hardening/summary")
def get_platform_launch_hardening_summary():
    return platform_launch_hardening_summary()


@router.post("/platform/launch-hardening/rebuild")
def rebuild_platform_launch_hardening():
    return build_platform_launch_hardening()


@router.get("/platform/launch/status")
def get_platform_launch_status():
    return platform_launch_hardening_summary()
