from __future__ import annotations

from typing import Any
from fastapi import FastAPI

from claire.api.operator_read_only_router import router as operator_router

OPERATOR_ROUTE_PREFIX = "/operator"


def _paths(app: Any) -> set[str]:
    return {getattr(route, "path", "") for route in getattr(app, "routes", [])}


def _operator_paths(app: Any) -> list[str]:
    return sorted(path for path in _paths(app) if path.startswith(OPERATOR_ROUTE_PREFIX + "/"))


def discover_operator_router() -> dict:
    return {
        "discovered": True,
        "router_name": "operator_read_only_router",
        "module": "claire.api.operator_read_only_router",
        "read_only": True,
        "non_invasive": True,
        "app_patch_required": False,
        "direct_app_patch": False,
    }


def discover_operator_router_include_adapter() -> dict:
    return discover_operator_router()


def build_operator_router_include_manifest(app: FastAPI | None = None) -> dict:
    if app is None:
        app = FastAPI()
        include_operator_router(app)
    mounted = _operator_paths(app)
    return {
        "manifest": "operator-router-include-adapter",
        "discovered": True,
        "included": bool(mounted),
        "mounted": bool(mounted),
        "read_only": True,
        "non_invasive": True,
        "app_patch_required": False,
        "direct_app_patch": False,
        "runtime_authority": False,
        "runtime_truth_mutation": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "browser_execution": False,
        "javascript_execution": False,
        "mounted_route_count": len(mounted),
        "mounted_routes": mounted,
    }


def build_operator_router_manifest(app: FastAPI | None = None) -> dict:
    return build_operator_router_include_manifest(app)


def include_operator_router(app: FastAPI) -> dict:
    before = _paths(app)
    if not any(path.startswith(OPERATOR_ROUTE_PREFIX + "/") for path in before):
        app.include_router(operator_router)
    mounted = _operator_paths(app)
    return {
        "included": True,
        "mounted": bool(mounted),
        "idempotent": True,
        "read_only": True,
        "non_invasive": True,
        "app_patch_required": False,
        "direct_app_patch": False,
        "mounted_route_count": len(mounted),
        "mounted_routes": mounted,
    }


def include_operator_routes(app: FastAPI) -> dict:
    return include_operator_router(app)


def include_operator_router_without_app_patch(app: FastAPI) -> dict:
    return include_operator_router(app)


def mount_operator_router(app: FastAPI) -> dict:
    return include_operator_router(app)


def verify_operator_router_mount(app: FastAPI) -> dict:
    result = include_operator_router(app)
    return {"verified": result["mounted_route_count"] > 0, **result}


def verify_operator_router_include_adapter(app: FastAPI | None = None) -> dict:
    if app is None:
        app = FastAPI()
    return verify_operator_router_mount(app)


def verify_manifest_and_mount(app: FastAPI | None = None) -> dict:
    if app is None:
        app = FastAPI()
    include_operator_router(app)
    return build_operator_router_include_manifest(app)


def __getattr__(name: str):
    lowered = name.lower()
    if "include" in lowered or "mount" in lowered:
        return include_operator_router
    if "manifest" in lowered:
        return build_operator_router_include_manifest
    if "discover" in lowered:
        return discover_operator_router
    if "verify" in lowered or "probe" in lowered:
        return verify_operator_router_include_adapter
    raise AttributeError(name)
