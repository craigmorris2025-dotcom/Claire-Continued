
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_dashboard_actions_routes_exist_without_enabling_execution():
    from runtime_core.api.dashboard_actions_registry_routes import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    registry = client.get("/dashboard/actions/registry")
    summary = client.get("/dashboard/actions/summary")
    preview = client.get("/dashboard/actions/preview/plan_search")

    assert registry.status_code == 200
    assert summary.status_code == 200
    assert preview.status_code == 200

    registry_payload = registry.json()
    summary_payload = summary.json()
    preview_payload = preview.json()

    assert registry_payload["status"] == "ready"
    assert registry_payload["action_count"] > 0
    assert len(registry_payload["actions"]) == registry_payload["action_count"]
    assert registry_payload["empty_state"] is False
    assert registry_payload["execution_enabled"] is False
    assert registry_payload["blocked_authorities"]["live_web_execution_enabled"] is False
    assert registry_payload["blocked_authorities"]["body_read_allowed"] is False
    assert registry_payload["blocked_authorities"]["runtime_mutation_enabled"] is False

    assert summary_payload["count"] == registry_payload["action_count"]
    assert summary_payload["actions_available"] is True
    assert summary_payload["execution_enabled"] is False
    assert preview_payload["status"] == "preview_ready"
    assert preview_payload["network_request_performed"] is False


def test_create_app_serves_dashboard_action_endpoints_when_available():
    from runtime_core.app import create_app

    app = create_app()
    client = TestClient(app)

    registry = client.get("/dashboard/actions/registry")
    summary = client.get("/dashboard/actions/summary")
    api_registry = client.get("/api/dashboard/actions/registry")

    assert registry.status_code == 200
    assert summary.status_code == 200
    assert api_registry.status_code == 200
    assert registry.json()["action_count"] > 0
    assert summary.json()["count"] == registry.json()["action_count"]


def test_dashboard_actions_registry_has_operator_ready_labels_not_only_stage_codes():
    from runtime_core.api.dashboard_actions_registry_routes import build_dashboard_actions_registry

    payload = build_dashboard_actions_registry()
    labels = {action["label"] for action in payload["actions"]}

    assert "Plan a governed search" in labels or "Compile search plan" in labels
    assert payload["visual_contract"]["actions_tab_should_show_controls"] is True
    assert payload["visual_contract"]["actions_chip_should_be_greater_than_zero"] is True
    assert payload["unlock_allowed"] is False
