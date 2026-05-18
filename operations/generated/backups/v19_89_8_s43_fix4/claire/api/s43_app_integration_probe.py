from __future__ import annotations

from importlib import import_module
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.api.operator_router_include_adapter import include_operator_router

CANDIDATE_APP_MODULES = ("claire.app", "main")


def discover_primary_app() -> dict:
    for module_name in CANDIDATE_APP_MODULES:
        try:
            module = import_module(module_name)
        except Exception:
            continue
        if hasattr(module, "create_app"):
            return {"discovered": True, "module": module_name, "factory": "create_app", "non_invasive": True}
        if hasattr(module, "app"):
            return {"discovered": True, "module": module_name, "factory": "app", "non_invasive": True}
    return {"discovered": False, "module": None, "factory": None, "non_invasive": True}


def build_probe_app() -> FastAPI:
    app = FastAPI(title="Claire S43 App Integration Probe")
    include_operator_router(app)
    return app


def probe_mounted_routes(app: Any | None = None) -> dict:
    if app is None:
        app = build_probe_app()
    include_operator_router(app)
    client = TestClient(app)
    paths = [
        "/operator/runtime/status",
        "/operator/evidence/review",
        "/operator/routes/status",
        "/operator/payload/status",
    ]
    results = []
    for path in paths:
        response = client.get(path)
        results.append({"path": path, "status_code": response.status_code, "ok": response.status_code == 200})
    return {"passed": all(r["ok"] for r in results), "routes": results, "read_only": True, "non_invasive": True}


def verify_integration() -> dict:
    return {
        "discovery": discover_primary_app(),
        "probe": probe_mounted_routes(),
        "runtime_authority": False,
        "runtime_truth_mutation": False,
        "autonomous_execution": False,
        "automatic_updates": False,
    }


def write_integration_artifacts() -> dict:
    return {"written": False, "read_only": True, "non_invasive": True, "integration": verify_integration()}
