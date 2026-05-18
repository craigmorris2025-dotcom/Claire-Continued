from __future__ import annotations

from fastapi.testclient import TestClient

from claire.app import create_app
from claire.api.governed_web_safety_activation import build_governed_web_safety_activation


def test_s32r2r1_safety_module_does_not_perform_network():
    state = build_governed_web_safety_activation()
    assert state["network_request_performed"] is False
    assert state["authority"]["browser_execution_authority"] == "blocked"
    assert state["authority"]["runtime_authority"] == "blocked"
    assert state["authority"]["runtime_truth_mutation"] == "blocked"


def test_s32r2r1_dashboard_payload_exposes_safety_activation():
    client = TestClient(create_app())
    response = client.get("/dashboard/payload")
    assert response.status_code == 200
    payload = response.json()

    assert payload["live_web_execution_enabled"] is False
    assert payload["autonomous_agent_execution_enabled"] is False
    assert payload["runtime_truth_mutation_enabled"] is False
    assert payload["automatic_updates_enabled"] is False

    assert "governed_payload_reconciliation" in payload
    assert "governed_web_safety_activation" in payload

    safety = payload["governed_web_safety_activation"]
    assert safety["network_request_performed"] is False
    assert safety["authority"]["browser_execution_authority"] == "blocked"
    assert safety["authority"]["runtime_authority"] == "blocked"


def test_s32r2r1_dashboard_payload_status_still_healthy():
    client = TestClient(create_app())
    assert client.get("/dashboard/payload/status").status_code == 200
