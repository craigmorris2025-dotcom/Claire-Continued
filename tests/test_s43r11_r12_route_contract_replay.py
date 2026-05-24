from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from runtime_core.api.operator_read_only_router import router
from runtime_core.api.s43_route_contract_replay import replay_get


def test_replay_operator_runtime_status_contract():
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    result = replay_get(client, "/operator/runtime/status")
    assert result["status_code"] == 200
    assert isinstance(result["json"], dict)
    assert result["governance"]["mutation_authority"] is False
