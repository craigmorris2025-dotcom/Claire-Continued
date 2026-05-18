from __future__ import annotations

import importlib
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_s957_s984_visual_payload_has_visible_buttons_and_actions():
    module = importlib.import_module("claire.governance.governed_cockpit_operation_visuals")
    payload = module.build_visual_payload()
    assert payload["phase"] == "S957-S984"
    assert payload["highest_stage"] == "S984"
    assert payload["status"] == "cockpit_operation_buttons_visible"
    assert payload["button_count"] >= 15
    assert payload["action_count"] >= 15
    assert payload["visual_mount"]["force_visible"] is True
    assert all(button["button_visible"] is True for button in payload["buttons"])
    assert all(button["execution_enabled"] is False for button in payload["buttons"])
    assert payload["blocked_capabilities"]["live_web_execution_enabled"] is False
    assert payload["blocked_capabilities"]["search_provider_execution_enabled"] is False
    assert payload["blocked_capabilities"]["body_read_allowed"] is False
    assert payload["blocked_capabilities"]["runtime_mutation_enabled"] is False
    assert payload["blocked_capabilities"]["command_execution_enabled"] is False


def test_s957_s984_visual_routes_return_buttons_and_preview():
    routes = importlib.import_module("claire.api.governed_cockpit_operation_visual_routes")
    app = FastAPI()
    app.include_router(routes.router)
    client = TestClient(app)
    response = client.get("/api/cockpit/operation-visuals/payload")
    assert response.status_code == 200
    payload = response.json()
    assert payload["button_count"] >= 15
    buttons = client.get("/api/cockpit/operation-visuals/buttons")
    assert buttons.status_code == 200
    assert buttons.json()["count"] >= 15
    preview = client.get("/api/cockpit/operation-visuals/preview/compile_query?command=test")
    assert preview.status_code == 200
    assert preview.json()["status"] == "preview_ready"
    assert preview.json()["execution_enabled"] is False


def test_s957_s984_stop_gate_preserves_all_blocks():
    module = importlib.import_module("claire.governance.governed_cockpit_operation_visuals")
    gate = module.build_visual_stop_gate()
    assert gate["passed"] is True
    assert gate["checks"]["visual_buttons_exist"] is True
    assert gate["checks"]["all_buttons_preview_only"] is True
    assert gate["checks"]["live_web_still_blocked"] is True
    assert gate["checks"]["provider_execution_still_blocked"] is True
    assert gate["checks"]["external_network_still_blocked"] is True
    assert gate["checks"]["body_read_still_blocked"] is True
    assert gate["checks"]["runtime_mutation_still_blocked"] is True
    assert gate["checks"]["command_execution_still_blocked"] is True


def test_s957_s984_assets_exist_and_force_mount_operation_controls():
    root = Path(__file__).resolve().parents[1]
    js_path = root / "frontend" / "cockpit" / "assets" / "claire_cockpit_operation_visual_controls.js"
    css_path = root / "frontend" / "cockpit" / "assets" / "claire_cockpit_operation_visual_controls.css"
    assert js_path.exists()
    assert css_path.exists()
    js = js_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    assert "claire-operation-control-mount" in js
    assert "FALLBACK_BUTTONS" in js
    assert "Governed operation buttons" in js
    assert "No web execution" in js
    assert "claire-operation-control-mount" in css


def test_s957_s984_active_html_references_visual_control_assets_or_mount():
    root = Path(__file__).resolve().parents[1]
    html_files = list((root / "frontend").glob("**/*.html")) if (root / "frontend").exists() else []
    assert html_files, "frontend html files are required for cockpit visual mount"
    combined = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in html_files)
    assert "claire_cockpit_operation_visual_controls.js" in combined
    assert "claire_cockpit_operation_visual_controls.css" in combined
    assert "claire-operation-control-mount" in combined


def test_s957_s984_optional_app_registration_does_not_break_create_app():
    app_module = importlib.import_module("claire.app")
    app = app_module.create_app()
    assert app is not None
    paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}
    assert "/api/cockpit/operation-visuals/payload" in paths
