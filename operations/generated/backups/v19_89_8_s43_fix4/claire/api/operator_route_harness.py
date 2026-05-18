from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.api.operator_router_include_adapter import include_operator_router, build_operator_router_manifest


def build_isolated_test_app() -> FastAPI:
    app = FastAPI(title="Claire Operator Read-Only Harness")
    include_operator_router(app)
    return app


def probe_operator_routes(app: FastAPI | None = None) -> dict:
    if app is None:
        app = build_isolated_test_app()
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
        results.append({"path": path, "status_code": response.status_code})
    return {
        "read_only": True,
        "probes": results,
        "all_passed": all(item["status_code"] == 200 for item in results),
    }


def write_harness_artifacts() -> dict:
    return {
        "written": False,
        "reason": "read-only harness does not write runtime artifacts",
        "read_only": True,
        "manifest": build_operator_router_manifest(),
    }
