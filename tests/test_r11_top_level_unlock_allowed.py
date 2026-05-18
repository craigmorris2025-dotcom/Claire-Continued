
from __future__ import annotations

from fastapi.testclient import TestClient


def test_r11_top_level_unlock_allowed_contracts():
    from claire.api.dashboard_actions_registry_routes import build_dashboard_actions_registry
    from claire.app import create_app

    registry = build_dashboard_actions_registry()
    assert registry["unlock_allowed"] is False
    assert registry["visual_contract"]["unlock_allowed"] is False

    client = TestClient(create_app())
    app_registry = client.get("/dashboard/actions/registry").json()
    assert app_registry["unlock_allowed"] is False
    assert app_registry["visual_contract"]["unlock_allowed"] is False

    status = client.get("/api/governed/live-probe/status").json()
    assert status["method_allowed"] == "HEAD"
    assert status["one_shot_only"] is True
    assert status["operator_triggered_only"] is True
