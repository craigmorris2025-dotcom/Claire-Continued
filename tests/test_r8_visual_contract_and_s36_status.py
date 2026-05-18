from __future__ import annotations

from fastapi.testclient import TestClient


def test_r8_visual_contract_and_s36_status_are_exact():
    from claire.api.dashboard_actions_registry_routes import build_dashboard_actions_registry
    from claire.app import create_app

    registry = build_dashboard_actions_registry()
    assert registry["visual_contract"]["actions_tab_should_show_controls"] is True

    client = TestClient(create_app())
    app_registry = client.get("/dashboard/actions/registry").json()
    assert app_registry["visual_contract"]["actions_tab_should_show_controls"] is True

    status = client.get("/api/governed/live-probe/status").json()
    assert status["registered"] is True
    assert status["operator_triggered_only"] is True
    assert status["network_request_performed"] is False
    assert status["body_read_allowed"] is False
    assert status["runtime_truth_mutation_allowed"] is False
