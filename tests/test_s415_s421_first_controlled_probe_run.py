from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from runtime_core.api.internet_first_controlled_probe_run_s415_s421 import (
    build_first_controlled_live_metadata_probe_run_s415_s421,
    build_s415_first_probe_run_authority,
    build_s416_probe_run_request_contract,
    build_s418_run_result_contract,
    build_s419_dashboard_first_probe_card,
    build_s420_route_registration_proof,
    build_s421_stop_gate,
    execute_s417_first_controlled_metadata_probe_run,
    register_s415_s421_first_probe_routes,
)


def test_s415_first_probe_authority_metadata_only():
    payload = build_s415_first_probe_run_authority()
    assert payload["stage_version"] == "S415"
    assert payload["authority"]["metadata_only"] is True
    assert payload["authority"]["body_read_allowed"] is False


def test_s416_probe_request_contract_accepts_https():
    payload = build_s416_probe_run_request_contract("https://example.com")
    assert payload["stage_version"] == "S416"
    assert payload["request_contract"]["allowed_shape"] is True


def test_s417_first_probe_run_defaults_no_network():
    payload = execute_s417_first_controlled_metadata_probe_run({"source_url": "https://example.com", "operator_confirmed": True, "allow_live_execution": False})
    assert payload["stage_version"] == "S417"
    assert payload["effective_live_execution"] is False
    assert payload["network_request_performed"] is False
    assert payload["body_read_performed"] is False
    assert payload["runtime_truth_modified"] is False


def test_s418_result_contract_has_required_fields():
    payload = build_s418_run_result_contract()
    assert payload["stage_version"] == "S418"
    assert "effective_live_execution" in payload["result_contract"]["required_fields"]


def test_s419_dashboard_card_enabled_for_operator_run():
    payload = build_s419_dashboard_first_probe_card()
    card = payload["dashboard_card"]
    assert payload["stage_version"] == "S419"
    assert card["enabled"] is True
    assert card["default_live_execution"] is False


def test_s420_routes_work():
    payload = build_s420_route_registration_proof()
    assert payload["stage_version"] == "S420"
    assert payload["run_route_registered"] is True

    app = FastAPI()
    register_s415_s421_first_probe_routes(app)
    client = TestClient(app)
    response = client.post("/api/internet/live-metadata/run", json={"source_url": "https://example.com", "operator_confirmed": True, "allow_live_execution": False})
    assert response.status_code == 200
    assert response.json()["effective_live_execution"] is False
    status = client.get("/api/internet/live-metadata/run/status")
    assert status.status_code == 200
    assert status.json()["dashboard_card"]["enabled"] is True


def test_s421_stop_gate_passes(tmp_path):
    payload = build_s421_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S421"
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["default_no_network"] is True
    assert "report_path" in payload


def test_s415_s421_rollup_ready():
    payload = build_first_controlled_live_metadata_probe_run_s415_s421()
    assert payload["stage_version"] == "S421"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
