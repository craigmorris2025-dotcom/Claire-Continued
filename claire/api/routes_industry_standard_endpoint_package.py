from __future__ import annotations

from fastapi import APIRouter, Request

from claire.api.industry_standard_endpoint_package import (
    build_endpoint_standard_settings,
    build_industry_standard_endpoint_package,
)


router = APIRouter(tags=["Industry Standard Endpoint Package"])


@router.get("/api/system/industry-standard-endpoint-package")
def get_industry_standard_endpoint_package(request: Request) -> dict:
    return build_industry_standard_endpoint_package(request.app)


@router.get("/dashboard/system/industry-standard-endpoint-package")
def get_dashboard_industry_standard_endpoint_package(request: Request) -> dict:
    return build_industry_standard_endpoint_package(request.app)


@router.get("/api/system/endpoint-standard-settings")
def get_endpoint_standard_settings(request: Request) -> dict:
    return build_endpoint_standard_settings(request.app)

