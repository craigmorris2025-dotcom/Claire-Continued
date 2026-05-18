from __future__ import annotations

from fastapi.testclient import TestClient

from claire.app import create_app
from claire.api.explicit_one_shot_metadata_probe_runner import build_explicit_one_shot_metadata_probe_runner_status

def test_s33r2_runner_status_is_fail_closed_no_network():
    status = build_explicit_one_shot_metadata_probe_runner_status()
    assert status["network_request_performed_during_install"] is False
    assert status["body_read_performed"] is False
    assert status["browser_execution_performed"] is False
    assert status["runtime_truth_mutation_performed"] is False
    assert status["autonomous_execution_performed"] is False
    assert status["automatic_update_performed"] is False
    assert "response_body" in status["forbidden_capture_fields"]
    assert "status_code" in status["allowed_capture_fields"]
    assert status["authority"]["network_body_read"] == "blocked"

def test_s33r2_dashboard_payload_exposes_runner():
    client = TestClient(create_app())
    response = client.get("/dashboard/payload")
    assert response.status_code == 200
    payload = response.json()
    assert "controlled_metadata_probe_executor" in payload
    assert "explicit_one_shot_metadata_probe_runner" in payload
    runner = payload["explicit_one_shot_metadata_probe_runner"]
    assert runner["network_request_performed_during_install"] is False
    assert runner["body_read_performed"] is False
    assert runner["authority"]["browser_execution_authority"] == "blocked"
    assert runner["quarantine"]["runtime_truth_write_allowed"] is False
