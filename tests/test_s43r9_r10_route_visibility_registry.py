from __future__ import annotations

from fastapi import FastAPI

from runtime_core.api.operator_read_only_router import router
from runtime_core.api.s43_route_visibility_registry import build_route_registry


def test_route_registry_collects_mounted_routes():
    app = FastAPI()
    app.include_router(router)
    registry = build_route_registry(app)
    assert registry["route_total"] > 0


def test_operator_routes_are_read_only():
    app = FastAPI()
    app.include_router(router)
    registry = build_route_registry(app)
    operator_routes = [r for r in registry["routes"] if r["path"].startswith("/operator/")]
    assert operator_routes
    for route in operator_routes:
        assert route["read_only"] is True
        assert route["governance_classification"]["runtime_authority"] is False
