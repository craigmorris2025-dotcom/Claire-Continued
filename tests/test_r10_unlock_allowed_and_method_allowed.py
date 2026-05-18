
from __future__ import annotations

from fastapi.testclient import TestClient


def test_r10_unlock_allowed_and_method_allowed_contracts():
    from claire.api.dashboard_actions_registry_routes import build_dashboard_actions_registry
    from claire.app import create_app

    registry = build_dashboard_actions_registry()
    visual = registry["visual_contract"]
    assert visual["actions_tab_should_show_controls"] is True
    assert visual["actions_chip_should_be_greater_than_zero"] is True
    assert visual["unlock_allowed"] is False

    client = TestClient(create_app())
    app_registry = client.get("/dashboard/actions/registry").json()
    app_visual = app_registry["visual_contract"]
    assert app_visual["unlock_allowed"] is False

    status = client.get("/api/governed/live-probe/status").json()
    assert status["registered"] is True
    assert status["operator_triggered_only"] is True
    assert status["one_shot_only"] is True
    assert status["method_allowed"] == "HEAD"
    assert status["network_request_performed"] is False
    assert status["body_read_allowed"] is False
    assert status["runtime_truth_mutation_allowed"] is False
