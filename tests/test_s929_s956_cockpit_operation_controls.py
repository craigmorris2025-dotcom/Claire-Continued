from __future__ import annotations
import importlib
from fastapi import FastAPI
from fastapi.testclient import TestClient

def test_s929_s956_payload_has_operation_buttons_and_blocks_execution():
    module = importlib.import_module("claire.governance.governed_cockpit_operation_controls")
    payload = module.build_operation_payload()
    assert payload["phase"] == "S929-S956"
    assert payload["highest_stage"] == "S956"
    assert payload["cockpit_buttons_exist"] is True
    assert payload["operation_count"] >= 10
    assert payload["action_count"] >= 10
    assert payload["blocked_capabilities"]["live_web_execution_enabled"] is False
    assert payload["blocked_capabilities"]["search_provider_execution_enabled"] is False
    assert payload["blocked_capabilities"]["body_read_allowed"] is False
    assert payload["blocked_capabilities"]["runtime_mutation_enabled"] is False
    assert payload["blocked_capabilities"]["command_execution_enabled"] is False
    assert all(button["execution_enabled"] is False for button in payload["buttons"])

def test_s929_s956_command_surface_exposes_primary_operation_buttons():
    module = importlib.import_module("claire.governance.governed_cockpit_operation_controls")
    surface = module.build_command_surface()
    assert surface["status"] == "command_surface_buttons_ready"
    assert surface["button_count"] >= 10
    assert surface["execution_enabled"] is False
    assert surface["command_execution_enabled"] is False
    assert "metadata_probe_preflight" in surface["primary_buttons"]
    assert "source_ingestion_draft" in surface["primary_buttons"]

def test_s929_s956_button_preview_is_local_and_non_executing():
    module = importlib.import_module("claire.governance.governed_cockpit_operation_controls")
    preview = module.build_button_preview("metadata_probe_preflight", supplied_command="search battery breakthroughs")
    assert preview["status"] == "preview_ready"
    assert preview["operation"]["key"] == "metadata_probe_preflight"
    assert preview["operation"]["execution_enabled"] is False
    assert preview["blocked_capabilities"]["search_provider_execution_enabled"] is False
    assert preview["blocked_capabilities"]["external_network_request_performed"] is False
    assert preview["blocked_capabilities"]["body_read_allowed"] is False

def test_s929_s956_stop_gate_preserves_dangerous_blocks():
    module = importlib.import_module("claire.governance.governed_cockpit_operation_controls")
    gate = module.build_stop_gate()
    assert gate["phase"] == "S929-S956"
    assert gate["passed"] is True
    assert gate["checks"]["operation_buttons_exist"] is True
    assert gate["checks"]["actions_registered"] is True
    assert gate["checks"]["all_buttons_preview_only"] is True
    assert gate["checks"]["live_web_still_blocked"] is True
    assert gate["checks"]["body_read_still_blocked"] is True
    assert gate["checks"]["runtime_mutation_still_blocked"] is True
    assert gate["checks"]["command_execution_still_blocked"] is True

def test_s929_s956_routes_return_buttons_and_preview():
    routes = importlib.import_module("claire.api.governed_cockpit_operation_control_routes")
    app = FastAPI()
    app.include_router(routes.router)
    client = TestClient(app)
    payload_response = client.get("/api/cockpit/operations/payload")
    assert payload_response.status_code == 200
    assert payload_response.json()["operation_count"] >= 10
    buttons_response = client.get("/api/cockpit/operations/buttons")
    assert buttons_response.status_code == 200
    assert buttons_response.json()["count"] >= 10
    assert buttons_response.json()["execution_enabled"] is False
    preview_response = client.get("/api/cockpit/operations/preview/query_compile?command=test")
    assert preview_response.status_code == 200
    assert preview_response.json()["status"] == "preview_ready"
    assert preview_response.json()["operation"]["key"] == "query_compile"

def test_s929_s956_optional_app_registration_does_not_break_create_app():
    app_module = importlib.import_module("claire.app")
    app = app_module.create_app()
    assert app is not None
    paths = {getattr(route, "path", "") for route in getattr(app, "routes", [])}
    assert "/api/cockpit/operations/payload" in paths
