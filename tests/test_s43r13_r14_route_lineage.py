from __future__ import annotations

from fastapi import FastAPI

from claire.api.operator_read_only_router import router
from claire.api.s43_route_lineage import build_route_lineage


def test_route_lineage_builds_for_mounted_operator_routes():
    app = FastAPI()
    app.include_router(router)
    lineage = build_route_lineage(app)
    assert lineage["lineage_total"] > 0
    assert any(item["path"].startswith("/operator/") for item in lineage["lineage"])
