from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from runtime_core.api.dashboard_payload_live_integration_s338_s344 import (
    build_canonical_dashboard_payload_integration_s338_s344,
    build_s338_existing_payload_reader,
    build_s339_payload_merge_owner,
    build_s340_integrated_status_endpoint_contract,
    build_s341_route_registration_contract,
    build_s342_app_mount_proof,
    build_s343_payload_schema_smoke_proof,
    build_s344_stop_gate,
    get_s338_s344_integrated_dashboard_payload,
    register_s338_s344_dashboard_payload_routes,
)


def test_s338_existing_payload_reader_returns_dict():
    payload = build_s338_existing_payload_reader()
    assert payload["stage_version"] == "S338"
    assert isinstance(payload["existing_payload"], dict)


def test_s339_payload_merge_owner_has_internet_dashboard_keys():
    payload = build_s339_payload_merge_owner()
    merged = payload["merged_payload"]
    assert payload["stage_version"] == "S339"
    assert "internet_update_readiness" in merged
    assert "internet_evidence" in merged
    assert "internet_update_proposals" in merged
    assert "dashboard_action_panel_consolidation" in merged


def test_s340_status_endpoint_contract_reports_required_keys_present():
    payload = build_s340_integrated_status_endpoint_contract()
    status = payload["status_payload"]
    assert payload["stage_version"] == "S340"
    assert status["ok"] is True
    assert all(status["required_keys_present"].values())


def test_s341_route_registration_mounts_payload_and_status():
    payload = build_s341_route_registration_contract()
    assert payload["stage_version"] == "S341"
    assert payload["payload_registered"] is True
    assert payload["status_registered"] is True


def test_s342_app_mount_replaces_existing_dashboard_payload_routes():
    payload = build_s342_app_mount_proof()
    assert payload["stage_version"] == "S342"
    assert payload["before_dashboard_route_count"] == 2
    assert payload["after_dashboard_route_count"] == 2
    assert payload["removed_count"] == 2


def test_s343_payload_schema_smoke_passes():
    payload = build_s343_payload_schema_smoke_proof()
    assert payload["stage_version"] == "S343"
    assert payload["schema_ok"] is True
    assert all(payload["checks"].values())


def test_s344_stop_gate_allows_forward_motion(tmp_path):
    payload = build_s344_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S344"
    assert payload["forward_motion_allowed"] is True
    assert "report_path" in payload


def test_s338_s344_route_returns_integrated_payload_with_testclient():
    app = FastAPI()
    register_s338_s344_dashboard_payload_routes(app)
    client = TestClient(app)
    response = client.get("/dashboard/payload")
    assert response.status_code == 200
    data = response.json()
    assert data["internet_update_readiness"]["readiness_state"] == "governed_internet_update_ready"
    status = client.get("/dashboard/payload/status").json()
    assert status["ok"] is True


def test_s338_s344_rollup_ready():
    payload = build_canonical_dashboard_payload_integration_s338_s344()
    assert payload["stage_version"] == "S344"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
    assert "internet_evidence" in get_s338_s344_integrated_dashboard_payload()
