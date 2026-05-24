from __future__ import annotations

from fastapi import APIRouter, Request

from runtime_core.api.endpoint_reconciliation_report import build_endpoint_reconciliation_report


router = APIRouter(tags=["Endpoint Reconciliation"])


@router.get("/api/system/endpoint-reconciliation")
def get_endpoint_reconciliation(request: Request) -> dict:
    return build_endpoint_reconciliation_report(request.app)


@router.get("/dashboard/system/endpoint-reconciliation")
def get_dashboard_endpoint_reconciliation(request: Request) -> dict:
    return build_endpoint_reconciliation_report(request.app)

