from __future__ import annotations

import importlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

def test_operator_experience_payload_is_user_facing_and_blocked():
    module = importlib.import_module("claire.governance.governed_operator_experience_console")
    payload = module.build_operator_experience_payload()
    assert payload["status"] == "ready"
    assert payload["button_count"] >= 10
    assert payload["action_count"] == payload["button_count"]
    assert payload["blocked_authorities"]["live_web_execution_enabled"] is False
    assert payload["blocked_authorities"]["body_read_allowed"] is False
    assert payload["blocked_authorities"]["runtime_mutation_enabled"] is False
    assert payload["blocked_authorities"]["command_execution_enabled"] is False
    assert payload["visual_contract"]["show_user_action_labels"] is True

def test_operator_experience_routes_are_mountable():
    routes = importlib.import_module("claire.api.governed_operator_experience_routes")
    app = FastAPI()
    app.include_router(routes.router)
    client = TestClient(app)
    payload = client.get("/api/cockpit/operator-experience/payload").json()
    assert payload["status"] == "ready"
    assert payload["button_count"] >= 10
    preview = client.get("/api/cockpit/operator-experience/preview/plan_search").json()
    assert preview["status"] == "preview_ready"
    assert preview["execution_enabled"] is False
    assert preview["network_request_performed"] is False

def test_operator_experience_assets_exist_and_remove_dev_labels():
    js_path = Path("frontend/cockpit/assets/claire_operator_experience_console.js")
    css_path = Path("frontend/cockpit/assets/claire_operator_experience_console.css")
    assert js_path.exists()
    assert css_path.exists()
    js = js_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    assert "Operator Command Console" in js
    assert "normalizeDevText" in js
    assert "S957-S984" not in js
    assert "claire-operator-primary-button" in css

def test_optional_create_app_still_imports():
    app_module = importlib.import_module("claire.app")
    if hasattr(app_module, "create_app"):
        app = app_module.create_app()
        assert app is not None
