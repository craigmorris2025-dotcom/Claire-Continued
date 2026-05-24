from __future__ import annotations

from fastapi.testclient import TestClient


def test_operational_readiness_exposes_12_gap_remediation_tracker():
    from runtime_core.app import create_app

    client = TestClient(create_app())
    payload = client.get("/api/operational/readiness").json()

    remediation = payload["twelve_gap_remediation"]
    assert remediation["schema_version"] == "claire_12_gap_remediation_v1"
    assert remediation["local_remediation_percent"] == 100
    assert remediation["activation_percent"] == 100
    assert remediation["status"] == "remediation_complete"
    assert len(remediation["gaps"]) == 12
    gaps = {item["gap_id"]: item for item in remediation["gaps"]}
    assert gaps[1]["local_remediation_percent"] == 100
    assert gaps[1]["blockers"] == []
    assert gaps[5]["local_remediation_percent"] == 100
    assert gaps[11]["local_remediation_percent"] == 100
    assert gaps[12]["local_remediation_percent"] == 100
    assert gaps[12]["activation_percent"] == 100
    assert gaps[12]["blockers"] == []
    assert "archive review complete" in gaps[12]["next_actions"][0]


def test_operational_readiness_exposes_operator_surface_next_actions():
    from runtime_core.app import create_app

    client = TestClient(create_app())
    payload = client.get("/api/operational/readiness").json()

    surface = payload["operator_surface"]
    assert surface["schema_version"] == "claire_operator_surface_v1"
    assert surface["mission_state"]["route"] == payload["route_selected"]
    assert surface["mission_state"]["blocker"] in {"governed_provider_ready", "none"}
    assert surface["command_surface"]["ask_claire_endpoint"] == "/api/ask-claire"
    assert surface["evidence_workflow"]["metadata_query"] == "/api/search/provider/query"
    assert surface["evidence_workflow"]["promotion"] == "/api/search/evidence/promote"
    assert surface["route_decision"]["portfolio_first_policy_respected"] is True
    assert "operator_decision_brief" in surface["final_output_lanes"]
    actions = {item["action_id"]: item for item in surface["next_action_queue"]}
    assert "run_connected_or_hybrid_cycle" in actions
    assert actions["run_connected_or_hybrid_cycle"]["status"] == "ready"
