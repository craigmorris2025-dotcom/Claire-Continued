from __future__ import annotations

import importlib
from pathlib import Path


def test_s985_control_surface_payload_has_visible_buttons_and_blocks():
    module = importlib.import_module("runtime_core.governance.governed_cockpit_control_surface_force_mount")
    payload = module.get_cockpit_control_surface_payload()
    assert payload["stage"] == "S985-S1012"
    assert payload["status"] == "control_surface_ready"
    assert payload["action_count"] >= 12
    assert payload["control_surface"]["button_count"] == payload["action_count"]
    assert payload["dangerous_authority_preserved"] is True
    assert payload["blocked_flags"]["live_web_execution_enabled"] is False
    assert payload["blocked_flags"]["body_read_allowed"] is False
    assert payload["blocked_flags"]["runtime_mutation_enabled"] is False
    assert payload["blocked_flags"]["command_execution_enabled"] is False


def test_s985_preview_operation_is_preview_only():
    module = importlib.import_module("runtime_core.governance.governed_cockpit_control_surface_force_mount")
    preview = module.preview_operation("compile_search_plan")
    assert preview["status"] == "preview_packet_ready"
    assert preview["execution_enabled"] is False
    assert preview["network_request_performed"] is False
    assert preview["body_read_performed"] is False
    assert preview["runtime_mutation_performed"] is False
    assert preview["command_execution_performed"] is False


def test_s985_routes_expose_assets_and_payload_on_local_app():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from runtime_core.api.governed_cockpit_control_surface_force_routes import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    payload = client.get("/api/cockpit/control-surface/payload")
    assert payload.status_code == 200
    assert payload.json()["action_count"] >= 12
    js = client.get("/api/cockpit/control-surface/assets/js")
    assert js.status_code == 200
    assert "claire-s985-s1012-control-surface" in js.text
    css = client.get("/api/cockpit/control-surface/assets/css")
    assert css.status_code == 200
    assert ".claire-s985-s1012-control-surface" in css.text


def test_s985_create_app_registers_control_surface_route_when_available():
    app_module = importlib.import_module("runtime_core.app")
    app = app_module.create_app()
    route_paths = {getattr(route, "path", "") for route in app.routes}
    assert "/api/cockpit/control-surface/payload" in route_paths
    assert "/api/cockpit/control-surface/assets/js" in route_paths


def test_s985_frontend_has_force_mount_asset_and_report():
    root = Path(__file__).resolve().parents[1]
    js = root / "frontend" / "cockpit" / "assets" / "claire_cockpit_control_surface_force_mount.js"
    css = root / "frontend" / "cockpit" / "assets" / "claire_cockpit_control_surface_force_mount.css"
    report = root / "reports" / "s985_s1012_active_cockpit_control_surface_force_mount_report.json"
    assert js.exists()
    assert css.exists()
    assert report.exists()
    report_text = report.read_text(encoding="utf-8")
    assert "S985-S1012" in report_text
    assert "html_patched" in report_text


def test_s985_active_html_or_injector_contains_script_endpoint():
    root = Path(__file__).resolve().parents[1]
    candidates = list((root / "frontend").rglob("*.html")) if (root / "frontend").exists() else []
    html_hits = [p for p in candidates if "/api/cockpit/control-surface/assets/js" in p.read_text(encoding="utf-8", errors="ignore")]
    injector = root / "claire" / "api" / "cockpit_control_surface_force_injector.py"
    assert html_hits or "/api/cockpit/control-surface/assets/js" in injector.read_text(encoding="utf-8")
