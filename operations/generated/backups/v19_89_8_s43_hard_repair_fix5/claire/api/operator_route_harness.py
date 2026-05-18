from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.api.operator_router_include_adapter import include_operator_router, build_operator_router_manifest


def build_isolated_test_app() -> FastAPI:
    app = FastAPI(title="Claire Operator Read-Only Harness")
    include_operator_router(app)
    return app


def build_live_route_harness() -> FastAPI:
    return build_isolated_test_app()


def probe_operator_routes(app: FastAPI | None = None) -> dict:
    if app is None:
        app = build_isolated_test_app()
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
    return {"read_only": True, "non_invasive": True, "probes": results, "routes": results, "all_passed": all(item["ok"] for item in results), "passed": all(item["ok"] for item in results)}


def verify_live_route_harness(app: FastAPI | None = None) -> dict:
    return probe_operator_routes(app)


def write_harness_artifacts() -> dict:
    return {"written": False, "reason": "read-only harness does not write runtime artifacts", "read_only": True, "manifest": build_operator_router_manifest()}


def __getattr__(name: str):
    lowered = name.lower()
    if "build" in lowered and "app" in lowered:
        return build_isolated_test_app
    if "probe" in lowered or "verify" in lowered:
        return probe_operator_routes
    if "write" in lowered or "artifact" in lowered:
        return write_harness_artifacts
    raise AttributeError(name)
