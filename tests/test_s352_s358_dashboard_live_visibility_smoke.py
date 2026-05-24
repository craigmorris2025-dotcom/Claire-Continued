from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from runtime_core.api.dashboard_live_visibility_smoke_s352_s358 import (
    build_live_dashboard_visibility_smoke_s352_s358,
    build_s352_payload_endpoint_visibility_smoke,
    build_s353_frontend_asset_visibility_smoke,
    build_s354_panel_content_projection_smoke,
    build_s355_action_disabled_smoke_proof,
    build_s356_no_fake_connected_state_proof,
    build_s357_dashboard_launch_readiness_summary,
    build_s358_stop_gate,
    register_s352_s358_dashboard_visibility_routes,
)


def test_s352_payload_endpoint_visibility_smoke_passes():
    payload = build_s352_payload_endpoint_visibility_smoke()
    assert payload["stage_version"] == "S352"
    assert payload["visibility_ok"] is True
    assert all(payload["visible_key_checks"].values())


def test_s353_frontend_asset_visibility_smoke_passes():
    payload = build_s353_frontend_asset_visibility_smoke()
    assert payload["stage_version"] == "S353"
    assert payload["asset_visibility_ok"] is True


def test_s354_panel_content_projection_smoke_passes():
    payload = build_s354_panel_content_projection_smoke()
    assert payload["stage_version"] == "S354"
    assert payload["projection_ok"] is True
    assert payload["projection"]["runtime_mutation_status"] == "blocked"


def test_s355_action_disabled_smoke_proof_passes():
    payload = build_s355_action_disabled_smoke_proof()
    assert payload["stage_version"] == "S355"
    assert payload["actions_visible_but_disabled"] is True
    assert all(payload["action_checks"].values())


def test_s356_no_fake_connected_state_proof_passes():
    payload = build_s356_no_fake_connected_state_proof()
    assert payload["stage_version"] == "S356"
    assert payload["no_fake_connected_ok"] is True


def test_s357_dashboard_launch_readiness_summary_ready():
    payload = build_s357_dashboard_launch_readiness_summary()
    assert payload["stage_version"] == "S357"
    assert payload["dashboard_visibility_ready"] is True


def test_s358_visibility_routes_return_summary():
    app = FastAPI()
    register_s352_s358_dashboard_visibility_routes(app)
    client = TestClient(app)
    smoke = client.get("/dashboard/visibility/smoke")
    assert smoke.status_code == 200
    assert smoke.json()["dashboard_visibility_ready"] is True
    summary = client.get("/dashboard/visibility/summary")
    assert summary.status_code == 200
    assert summary.json()["readiness_state"] == "governed_internet_update_ready"


def test_s358_stop_gate_allows_forward_motion(tmp_path):
    payload = build_s358_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S358"
    assert payload["forward_motion_allowed"] is True
    assert payload["dashboard_visibility_state"] == "payload_renderer_smoke_ready"
    assert "report_path" in payload


def test_s352_s358_rollup_ready():
    payload = build_live_dashboard_visibility_smoke_s352_s358()
    assert payload["stage_version"] == "S358"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
