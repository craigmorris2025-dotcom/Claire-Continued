
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.dashboard.cockpit_dashboard_state import build_cockpit_dashboard_state
from runtime_core.dashboard.operator_dashboard_state import (
    build_operator_dashboard_state,
    operator_dashboard_state_summary,
)

router = APIRouter(tags=["Operator Dashboard"])


@router.get("/operator/dashboard/state")
def get_operator_dashboard_state():
    return build_cockpit_dashboard_state()


@router.get("/dashboard/state")
def get_dashboard_state():
    return build_cockpit_dashboard_state()


@router.get("/api/dashboard/state")
def get_api_dashboard_state():
    return build_cockpit_dashboard_state()


@router.get("/operator/dashboard/summary")
def get_operator_dashboard_summary():
    return operator_dashboard_state_summary()


@router.post("/operator/dashboard/refresh")
def refresh_operator_dashboard_state():
    return build_operator_dashboard_state()
