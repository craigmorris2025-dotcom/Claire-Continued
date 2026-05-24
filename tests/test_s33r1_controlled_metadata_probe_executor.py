from __future__ import annotations

from fastapi.testclient import TestClient

from runtime_core.app import create_app
from runtime_core.api.controlled_metadata_probe_executor import build_controlled_metadata_probe_executor_status

def test_s33r1_executor_status_is_fail_closed_no_network():
    status = build_controlled_metadata_probe_executor_status()
    assert status["network_request_performed"] is False
    assert status["body_read_performed"] is False
    assert status["browser_execution_performed"] is False
    assert status["runtime_truth_mutation_performed"] is False
    assert status["autonomous_execution_performed"] is False
    assert status["automatic_update_performed"] is False
    assert status["authority"]["network_body_read"] == "blocked"
    assert status["quarantine"]["manual_promotion_required"] is True

def test_s33r1_dashboard_payload_exposes_executor():
    client = TestClient(create_app())
    response = client.get("/dashboard/payload")
    assert response.status_code == 200
    payload = response.json()
    assert "controlled_read_only_provider_probe_gate" in payload
    assert "controlled_metadata_probe_executor" in payload
    executor = payload["controlled_metadata_probe_executor"]
    assert executor["network_request_performed"] is False
    assert executor["body_read_performed"] is False
    assert executor["authority"]["browser_execution_authority"] == "blocked"
    assert executor["quarantine"]["runtime_truth_write_allowed"] is False
