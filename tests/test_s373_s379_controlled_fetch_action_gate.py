from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.api.internet_controlled_fetch_action_s373_s379 import (
    build_controlled_fetch_quarantine_action_gate_s373_s379,
    build_s373_controlled_fetch_action_authority,
    build_s374_fetch_request_validation_contract,
    build_s376_quarantine_action_integration,
    build_s377_evidence_capsule_action_integration,
    build_s378_route_registration_proof,
    build_s379_stop_gate,
    execute_s375_controlled_fetch_action,
    register_s373_s379_controlled_fetch_routes,
)


def test_s373_controlled_fetch_authority_requires_quarantine():
    payload = build_s373_controlled_fetch_action_authority()
    authority = payload["action_authority"]
    assert payload["stage_version"] == "S373"
    assert authority["quarantine_required"] is True
    assert authority["live_network_fetch_allowed"] is False


def test_s374_fetch_validation_accepts_https_shape():
    payload = build_s374_fetch_request_validation_contract("https://example.invalid/test")
    assert payload["stage_version"] == "S374"
    assert payload["request_validation"]["allowed_url_shape"] is True


def test_s375_controlled_fetch_action_completes_dry_run_without_network():
    payload = execute_s375_controlled_fetch_action({"source_url": "https://example.invalid/test", "operator_confirmed": True})
    result = payload["fetch_result"]
    assert payload["stage_version"] == "S375"
    assert result["status"] == "completed_dry_run"
    assert result["network_request_performed"] is False
    assert result["runtime_truth_modified"] is False


def test_s376_quarantine_integration_is_unreviewed():
    payload = build_s376_quarantine_action_integration()
    assert payload["stage_version"] == "S376"
    assert payload["quarantine_record"]["promotion_status"] == "unreviewed"


def test_s377_evidence_capsule_integration_requires_review():
    payload = build_s377_evidence_capsule_action_integration()
    assert payload["stage_version"] == "S377"
    assert payload["manual_review_required"] is True
    assert payload["evidence_capsule"]["evidence_id"].startswith("evidence_")


def test_s378_routes_registered():
    payload = build_s378_route_registration_proof()
    assert payload["stage_version"] == "S378"
    assert payload["fetch_route_registered"] is True
    assert payload["status_route_registered"] is True


def test_s378_controlled_fetch_routes_work_with_testclient():
    app = FastAPI()
    register_s373_s379_controlled_fetch_routes(app)
    client = TestClient(app)
    response = client.post("/api/internet/fetch/controlled", json={"source_url": "https://example.invalid/test", "operator_confirmed": True})
    assert response.status_code == 200
    assert response.json()["fetch_result"]["status"] == "completed_dry_run"
    status = client.get("/api/internet/fetch/controlled/status")
    assert status.status_code == 200
    assert status.json()["controlled_fetch_action_enabled"] is True


def test_s379_stop_gate_passes(tmp_path):
    payload = build_s379_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S379"
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["live_network_still_blocked"] is True
    assert "report_path" in payload


def test_s373_s379_rollup_ready():
    payload = build_controlled_fetch_quarantine_action_gate_s373_s379()
    assert payload["stage_version"] == "S379"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
