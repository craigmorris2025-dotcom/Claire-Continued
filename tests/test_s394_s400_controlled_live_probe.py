from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.api.internet_controlled_live_probe_s394_s400 import (
    build_controlled_live_probe_executor_s394_s400,
    build_s394_probe_executor_authority,
    build_s395_probe_request_validation,
    build_s397_probe_quarantine_draft,
    build_s398_dashboard_action_patch,
    build_s399_route_registration_proof,
    build_s400_stop_gate,
    execute_s396_controlled_live_probe,
    register_s394_s400_live_probe_routes,
)


def test_s394_probe_executor_authority_is_metadata_only():
    payload = build_s394_probe_executor_authority()
    assert payload["stage_version"] == "S394"
    assert payload["authority"]["metadata_only"] is True
    assert payload["authority"]["body_read_allowed"] is False


def test_s395_validation_defaults_to_dry_run():
    payload = build_s395_probe_request_validation("https://example.com", allow_live_execution=False)
    assert payload["stage_version"] == "S395"
    assert payload["validation"]["dry_run_mode"] is True


def test_s396_default_probe_does_not_perform_network():
    payload = execute_s396_controlled_live_probe({"source_url": "https://example.com", "allow_live_execution": False})
    result = payload["probe_result"]
    assert payload["stage_version"] == "S396"
    assert result["mode"] == "dry_run"
    assert result["network_request_performed"] is False
    assert result["body_read_performed"] is False


def test_s397_quarantine_draft_unreviewed():
    payload = build_s397_probe_quarantine_draft()
    assert payload["stage_version"] == "S397"
    assert payload["quarantine_draft"]["promotion_status"] == "unreviewed"


def test_s398_dashboard_action_patch_enabled():
    payload = build_s398_dashboard_action_patch()
    assert payload["stage_version"] == "S398"
    assert payload["action_registry_patch"]["controlled_live_provider_probe"]["enabled"] is True


def test_s399_routes_work():
    payload = build_s399_route_registration_proof()
    assert payload["stage_version"] == "S399"
    assert payload["probe_route_registered"] is True

    app = FastAPI()
    register_s394_s400_live_probe_routes(app)
    client = TestClient(app)
    response = client.post("/api/internet/live-provider/probe", json={"source_url": "https://example.com", "allow_live_execution": False})
    assert response.status_code == 200
    assert response.json()["probe_result"]["mode"] == "dry_run"


def test_s400_stop_gate_passes(tmp_path):
    payload = build_s400_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S400"
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["no_network_in_default_probe"] is True
    assert "report_path" in payload


def test_s394_s400_rollup_ready():
    payload = build_controlled_live_probe_executor_s394_s400()
    assert payload["stage_version"] == "S400"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
