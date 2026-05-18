from __future__ import annotations

import importlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_r6_dashboard_action_contract_has_legacy_and_current_fields():
    from claire.api.dashboard_actions_registry_routes import (
        build_dashboard_actions,
        build_dashboard_actions_registry,
        build_dashboard_action_preview,
        router,
    )

    actions = build_dashboard_actions()
    registry = build_dashboard_actions_registry()
    preview = build_dashboard_action_preview("plan_search")

    assert actions
    assert registry["status"] == "ready"
    assert registry["action_count"] == len(actions)
    assert registry["blocked_authorities"]["network_request_performed"] is False
    assert registry["blocked_authorities"]["body_read_allowed"] is False
    assert registry["execution_enabled"] is False
    assert preview["status"] == "preview_ready"

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    assert client.get("/dashboard/actions/registry").json()["action_count"] > 0
    assert client.get("/dashboard/actions/preview/plan_search").json()["status"] == "preview_ready"


def test_r6_create_app_s36_and_payload_contracts():
    app_module = importlib.import_module("claire.app")
    app = app_module.create_app()
    client = TestClient(app)

    registry = client.get("/dashboard/actions/registry")
    payload = client.get("/dashboard/payload")
    status = client.get("/api/governed/live-probe/status")

    assert registry.status_code == 200
    assert payload.status_code == 200
    assert status.status_code == 200
    assert registry.json()["action_count"] > 0
    assert registry.json()["blocked_authorities"]["network_request_performed"] is False
    assert payload.json()["operator_console"]["user_facing"] is True
    assert status.json()["registered"] is True

    blocked = client.post("/api/governed/live-probe/head", json={"url": "https://example.com", "operator_ack": True, "one_shot": True})
    assert blocked.status_code == 403
    assert "provider gate is disabled" in blocked.text

    text = Path("claire/app.py").read_text(encoding="utf-8")
    assert text.count("Claire v19.89.8-S31R4 governed dashboard payload handoff") == 1
