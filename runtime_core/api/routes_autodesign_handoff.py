
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.autodesign.handoff_contract import (
    autodesign_handoff_summary,
    build_autodesign_handoff,
)

router = APIRouter(tags=["AutoDesign"])


@router.get("/autodesign/handoff")
def get_autodesign_handoff():
    return build_autodesign_handoff()


@router.get("/autodesign/handoff/summary")
def get_autodesign_handoff_summary():
    return autodesign_handoff_summary()


@router.post("/autodesign/handoff/rebuild")
def rebuild_autodesign_handoff():
    return build_autodesign_handoff()


@router.get("/design/autodesign/handoff")
def get_design_autodesign_handoff():
    return build_autodesign_handoff()
