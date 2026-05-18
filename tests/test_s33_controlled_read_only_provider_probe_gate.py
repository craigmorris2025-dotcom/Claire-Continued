from __future__ import annotations

from fastapi.testclient import TestClient

from claire.app import create_app
from claire.api.controlled_read_only_provider_probe_gate import build_controlled_read_only_provider_probe_gate

def test_s33_probe_gate_is_metadata_only_and_no_network():
    gate = build_controlled_read_only_provider_probe_gate()
    assert gate["network_request_performed"] is False
    assert gate["body_scraping_performed"] is False
    assert gate["browser_execution_performed"] is False
    assert gate["runtime_truth_mutation_performed"] is False
    assert gate["autonomous_execution_performed"] is False
    assert gate["automatic_update_performed"] is False
    assert gate["authority"]["network_body_read"] == "blocked"
    assert gate["authority"]["browser_execution_authority"] == "blocked"
    assert gate["quarantine"]["manual_promotion_required"] is True

def test_s33_dashboard_payload_exposes_probe_gate():
    client = TestClient(create_app())
    response = client.get("/dashboard/payload")
    assert response.status_code == 200
    payload = response.json()
    assert payload["live_web_execution_enabled"] is False
    assert payload["autonomous_agent_execution_enabled"] is False
    assert payload["runtime_truth_mutation_enabled"] is False
    assert payload["automatic_updates_enabled"] is False
    assert "governed_web_safety_activation" in payload
    assert "controlled_read_only_provider_probe_gate" in payload
    gate = payload["controlled_read_only_provider_probe_gate"]
    assert gate["network_request_performed"] is False
    assert gate["body_scraping_performed"] is False
    assert gate["authority"]["browser_execution_authority"] == "blocked"
    assert gate["quarantine"]["runtime_truth_write_allowed"] is False
