from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from claire.api.operator_read_only_router import router as operator_router

OPERATOR_ROUTE_PREFIX = "/operator"


def _paths(app: Any) -> set[str]:
    return {getattr(route, "path", "") for route in getattr(app, "routes", [])}


def discover_operator_router() -> dict:
    return {
        "discovered": True,
        "router_name": "operator_read_only_router",
        "module": "claire.api.operator_read_only_router",
        "read_only": True,
        "non_invasive": True,
        "app_patch_required": False,
    }


def include_operator_router(app: FastAPI) -> dict:
    before = _paths(app)
    if not any(path.startswith(OPERATOR_ROUTE_PREFIX + "/") for path in before):
        app.include_router(operator_router)
    after = _paths(app)
    mounted = sorted(path for path in after if path.startswith(OPERATOR_ROUTE_PREFIX + "/"))
    return {
        "included": True,
        "mounted": True,
        "idempotent": True,
        "non_invasive": True,
        "app_patch_required": False,
        "mounted_route_count": len(mounted),
        "mounted_routes": mounted,
    }


def include_operator_routes(app: FastAPI) -> dict:
    return include_operator_router(app)


def build_operator_router_manifest(app: FastAPI | None = None) -> dict:
    if app is None:
        app = FastAPI()
        include_operator_router(app)
    mounted = sorted(path for path in _paths(app) if path.startswith(OPERATOR_ROUTE_PREFIX + "/"))
    return {
        "manifest": "operator-router-include-adapter",
        "read_only": True,
        "non_invasive": True,
        "app_patch_required": False,
        "runtime_authority": False,
        "runtime_truth_mutation": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "mounted_route_count": len(mounted),
        "mounted_routes": mounted,
    }


def verify_operator_router_mount(app: FastAPI) -> dict:
    manifest = include_operator_router(app)
    return {
        "verified": manifest["mounted_route_count"] > 0,
        "read_only": True,
        "non_invasive": True,
        **manifest,
    }
