"""Read-only API route for v16.46 Master Control UI Shell."""
from __future__ import annotations

from fastapi import APIRouter

from claire.ui.master_control_ui_shell import build_master_control_ui_shell

router = APIRouter(prefix="/master-control", tags=["master-control"])

@router.get("/ui-shell")
def get_master_control_ui_shell():
    return build_master_control_ui_shell()
