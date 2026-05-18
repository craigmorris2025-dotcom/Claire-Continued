
from __future__ import annotations

from fastapi import APIRouter

from claire.platform.launch_candidate_freeze import (
    build_launch_candidate_freeze,
    launch_candidate_freeze_summary,
)

router = APIRouter(tags=["Launch Candidate"])


@router.get("/platform/launch-candidate")
def get_launch_candidate_freeze():
    return build_launch_candidate_freeze()


@router.get("/platform/launch-candidate/summary")
def get_launch_candidate_freeze_summary():
    return launch_candidate_freeze_summary()


@router.post("/platform/launch-candidate/freeze")
def freeze_launch_candidate():
    return build_launch_candidate_freeze()


@router.get("/platform/freeze/status")
def get_platform_freeze_status():
    return launch_candidate_freeze_summary()
