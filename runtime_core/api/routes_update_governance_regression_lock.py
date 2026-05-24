
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.update_governance.update_governance_regression_lock import (
    build_update_governance_regression_lock,
    update_governance_regression_lock_summary,
)

router = APIRouter(tags=["Update Governance"])


@router.get("/updates/regression-lock")
def get_update_governance_regression_lock():
    return build_update_governance_regression_lock()


@router.get("/updates/regression-lock/summary")
def get_update_governance_regression_lock_summary():
    return update_governance_regression_lock_summary()


@router.post("/updates/regression-lock/rebuild")
def rebuild_update_governance_regression_lock():
    return build_update_governance_regression_lock()


@router.get("/updates/governance/lock")
def get_update_governance_lock_alias():
    return update_governance_regression_lock_summary()
