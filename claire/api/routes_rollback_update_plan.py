
from __future__ import annotations

from fastapi import APIRouter

from claire.update_governance.rollback_update_plan import (
    build_rollback_update_plan,
    rollback_update_plan_summary,
)

router = APIRouter(tags=["Update Governance"])


@router.get("/updates/rollback-plan")
def get_rollback_update_plan():
    return build_rollback_update_plan()


@router.get("/updates/rollback-plan/summary")
def get_rollback_update_plan_summary():
    return rollback_update_plan_summary()


@router.post("/updates/rollback-plan/create")
def create_rollback_update_plan():
    return build_rollback_update_plan()


@router.get("/updates/rollback/status")
def get_rollback_status():
    return rollback_update_plan_summary()
