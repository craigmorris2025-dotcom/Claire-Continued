from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.api.dashboard_action_wiring_refresh_s422_s428 import (
    build_dashboard_action_wiring_refresh_s422_s428,
    build_s422_dashboard_action_endpoint_registry,
    build_s423_frontend_action_binding_manifest,
    build_s424_action_button_state_contract,
    build_s425_dashboard_action_summary,
    build_s426_route_registration_proof,
    build_s427_frontend_asset_visibility_proof,
    build_s428_stop_gate,
    register_s422_s428_dashboard_action_routes,
)


def test_s422_action_registry_lists_operational_endpoints():
    payload = build_s422_dashboard_action_endpoint_registry()
    registry = payload["action_registry"]
    assert payload["stage_version"] == "S422"
    assert "first_metadata_probe" in registry
    assert registry["proposal_export"]["enabled"] is True


def test_s423_frontend_manifest_points_to_assets():
    payload = build_s423_frontend_action_binding_manifest()
    manifest = payload["frontend_manifest"]
    assert payload["stage_version"] == "S423"
    assert manifest["buttons_auto_created"] is True
    assert manifest["action_registry_endpoint"] == "/dashboard/actions/registry"


def test_s424_button_states_block_runtime_truth_write():
    payload = build_s424_action_button_state_contract()
    states = payload["button_states"]
    assert payload["stage_version"] == "S424"
    assert all(item["runtime_truth_write_enabled"] is False for item in states.values())


def test_s425_dashboard_action_summary_blocks_mutation():
    payload = build_s425_dashboard_action_summary()
    summary = payload["action_summary"]
    assert payload["stage_version"] == "S425"
    assert summary["enabled_action_count"] >= 6
    assert summary["runtime_mutation_status"] == "blocked"


def test_s426_routes_work():
    payload = build_s426_route_registration_proof()
    assert payload["stage_version"] == "S426"
    assert payload["registry_route_registered"] is True

    app = FastAPI()
    register_s422_s428_dashboard_action_routes(app)
    client = TestClient(app)
    registry = client.get("/dashboard/actions/registry")
    assert registry.status_code == 200
    assert "first_metadata_probe" in registry.json()
    summary = client.get("/dashboard/actions/summary")
    assert summary.status_code == 200
    assert summary.json()["body_read_status"] == "blocked"
    smoke = client.get("/dashboard/actions/smoke")
    assert smoke.status_code == 200
    assert smoke.json()["status"] == "ok"


def test_s427_frontend_assets_visible():
    payload = build_s427_frontend_asset_visibility_proof()
    assets = payload["assets"]
    assert payload["stage_version"] == "S427"
    assert assets["js_exists"] is True
    assert assets["css_exists"] is True


def test_s428_stop_gate_passes(tmp_path):
    payload = build_s428_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S428"
    assert payload["forward_motion_allowed"] is True
    assert payload["dashboard_actions_operationally_wired"] is True
    assert "report_path" in payload


def test_s422_s428_rollup_ready():
    payload = build_dashboard_action_wiring_refresh_s422_s428()
    assert payload["stage_version"] == "S428"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
