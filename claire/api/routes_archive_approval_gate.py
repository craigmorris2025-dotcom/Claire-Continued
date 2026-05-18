
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from claire.cleanup.archive_approval_gate import (
    archive_approval_summary,
    build_archive_approval_gate,
    execute_approved_archive_moves,
)

router = APIRouter(tags=["Cleanup Proof"])


@router.get("/cleanup/archive-approval")
def get_archive_approval_gate():
    return build_archive_approval_gate()


@router.get("/cleanup/archive-approval/summary")
def get_archive_approval_summary():
    return archive_approval_summary()


@router.post("/cleanup/archive-approval/rebuild")
def rebuild_archive_approval_gate():
    return build_archive_approval_gate()


@router.post("/cleanup/archive/execute-approved")
def execute_archive_approved(payload: Dict[str, Any]):
    return execute_approved_archive_moves(confirm_text=str(payload.get("confirm_text", "")))


@router.get("/cleanup/archive/status")
def get_archive_status():
    return archive_approval_summary()
