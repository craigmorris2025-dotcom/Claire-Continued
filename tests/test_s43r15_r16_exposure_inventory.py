from __future__ import annotations

from fastapi import FastAPI

from runtime_core.api.operator_read_only_router import router
from runtime_core.api.s43_exposure_inventory import build_exposure_inventory


def test_exposure_inventory_builds():
    app = FastAPI()
    app.include_router(router)
    inventory = build_exposure_inventory(app)
    assert "visibility" in inventory
    assert "lineage" in inventory


def test_exposure_inventory_remains_read_only():
    app = FastAPI()
    app.include_router(router)
    inventory = build_exposure_inventory(app)
    governance = inventory["governance"]
    assert governance["read_only"] is True
    assert governance["runtime_mutation"] is False
    assert governance["browser_execution"] is False
    assert governance["javascript_execution"] is False
