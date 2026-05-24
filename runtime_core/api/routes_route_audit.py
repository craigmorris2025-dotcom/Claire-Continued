
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.routing.discovery_breakthrough_innovation_route_audit import (
    build_route_audit,
    route_audit_summary,
)

router = APIRouter(tags=["Route Audit"])


@router.get("/routes/audit")
def get_route_audit():
    return build_route_audit()


@router.get("/routes/audit/summary")
def get_route_audit_summary():
    return route_audit_summary()


@router.post("/routes/audit/rebuild")
def rebuild_route_audit():
    return build_route_audit()


@router.get("/discovery/route-audit")
def get_discovery_route_audit():
    return build_route_audit()
