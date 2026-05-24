from __future__ import annotations

from fastapi.testclient import TestClient

from runtime_core.app import create_app
from runtime_core.api.operator_triggered_metadata_probe_endpoint import build_operator_triggered_metadata_probe_endpoint_status

def test_s33r3_endpoint_status_is_boundary_only_no_network():
    status = build_operator_triggered_metadata_probe_endpoint_status()
    assert status["network_request_performed_during_install"] is False
    assert status["endpoint_registered_with_app"] is False
    assert status["body_read_performed"] is False
    assert status["browser_execution_performed"] is False
    assert status["runtime_truth_mutation_performed"] is False
    assert status["automatic_update_performed"] is False
    assert status["method_policy"]["response_body_allowed"] is False
    assert "HEAD" in status["method_policy"]["allowed_methods"]

def test_s33r3_dashboard_payload_exposes_endpoint_boundary():
    client = TestClient(create_app())
    response = client.get("/dashboard/payload")
    assert response.status_code == 200
    payload = response.json()
    assert "explicit_one_shot_metadata_probe_runner" in payload
    assert "operator_triggered_metadata_probe_endpoint" in payload
    endpoint = payload["operator_triggered_metadata_probe_endpoint"]
    assert endpoint["network_request_performed_during_install"] is False
    assert endpoint["endpoint_registered_with_app"] is False
    assert endpoint["body_read_performed"] is False
    assert endpoint["authority"]["browser_execution_authority"] == "blocked"
    assert endpoint["quarantine"]["runtime_truth_write_allowed"] is False
