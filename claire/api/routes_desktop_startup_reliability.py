
from __future__ import annotations

from fastapi import APIRouter

from claire.desktop.startup_reliability import (
    build_desktop_startup_reliability,
    desktop_startup_reliability_summary,
    package_manifest,
)

router = APIRouter(tags=["Desktop Startup"])


@router.get("/desktop/startup")
def get_desktop_startup_reliability():
    return build_desktop_startup_reliability()


@router.get("/desktop/startup/summary")
def get_desktop_startup_reliability_summary():
    return desktop_startup_reliability_summary()


@router.post("/desktop/startup/rebuild")
def rebuild_desktop_startup_reliability():
    return build_desktop_startup_reliability()


@router.get("/desktop/package-manifest")
def get_desktop_package_manifest():
    return package_manifest(__import__("pathlib").Path.cwd())


@router.get("/desktop/launch/status")
def get_desktop_launch_status():
    return desktop_startup_reliability_summary()
