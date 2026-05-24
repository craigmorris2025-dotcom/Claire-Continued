
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.update_governance.automatic_update_runner_gate import (
    automatic_update_runner_gate_summary,
    build_automatic_update_runner_gate,
)

router = APIRouter(tags=["Update Governance"])


@router.get("/updates/runner-gate")
def get_automatic_update_runner_gate():
    return build_automatic_update_runner_gate()


@router.get("/updates/runner-gate/summary")
def get_automatic_update_runner_gate_summary():
    return automatic_update_runner_gate_summary()


@router.post("/updates/runner-gate/rebuild")
def rebuild_automatic_update_runner_gate():
    return build_automatic_update_runner_gate()


@router.get("/updates/automatic/status")
def get_automatic_update_status():
    return automatic_update_runner_gate_summary()
