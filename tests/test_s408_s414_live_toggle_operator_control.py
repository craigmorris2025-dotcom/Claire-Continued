from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from runtime_core.api.internet_live_toggle_operator_control_s408_s414 import (
    build_operator_visible_live_toggle_s408_s414,
    build_s408_live_toggle_visibility_contract,
    build_s409_live_toggle_state,
    build_s410_operator_instruction_contract,
    build_s412_dashboard_toggle_card,
    build_s413_route_registration_proof,
    build_s414_stop_gate,
    execute_s411_live_toggle_preflight,
    register_s408_s414_live_toggle_routes,
)


def test_s408_live_toggle_visible_but_dashboard_cannot_modify_env():
    payload = build_s408_live_toggle_visibility_contract()
    contract = payload["visibility_contract"]
    assert payload["stage_version"] == "S408"
    assert contract["dashboard_visible"] is True
    assert contract["dashboard_can_modify_env"] is False


def test_s409_live_toggle_defaults_closed():
    payload = build_s409_live_toggle_state(env={})
    assert payload["stage_version"] == "S409"
    assert payload["toggle_state"]["enabled"] is False
    assert payload["toggle_state"]["effective_mode"] == "dry_run_only"


def test_s410_operator_instruction_names_toggle():
    payload = build_s410_operator_instruction_contract()
    instruction = payload["operator_instruction"]
    assert payload["stage_version"] == "S410"
    assert "PLATFORM_ALLOW_CONTROLLED_LIVE_PROVIDER" in instruction["enable_command_powershell"]
    assert instruction["do_not_enable_until_green_gate"] is True


def test_s411_preflight_blocks_when_toggle_closed():
    payload = execute_s411_live_toggle_preflight({"operator_confirmed": True})
    preflight = payload["preflight"]
    assert payload["stage_version"] == "S411"
    assert preflight["body_read_allowed"] is False
    assert preflight["runtime_truth_write_allowed"] is False


def test_s412_dashboard_card_exposes_toggle():
    payload = build_s412_dashboard_toggle_card()
    card = payload["dashboard_card"]
    assert payload["stage_version"] == "S412"
    assert card["panel_key"] == "live_provider_toggle"
    assert card["dashboard_can_enable"] is False


def test_s413_routes_work():
    payload = build_s413_route_registration_proof()
    assert payload["stage_version"] == "S413"
    assert payload["status_route_registered"] is True

    app = FastAPI()
    register_s408_s414_live_toggle_routes(app)
    client = TestClient(app)
    status = client.get("/api/internet/live-toggle/status")
    assert status.status_code == 200
    assert status.json()["status"] == "ok"
    preflight = client.post("/api/internet/live-toggle/preflight", json={"operator_confirmed": True})
    assert preflight.status_code == 200


def test_s414_stop_gate_passes(tmp_path):
    payload = build_s414_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S414"
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["default_closed"] is True
    assert "report_path" in payload


def test_s408_s414_rollup_ready():
    payload = build_operator_visible_live_toggle_s408_s414()
    assert payload["stage_version"] == "S414"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
