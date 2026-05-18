from __future__ import annotations

from fastapi.testclient import TestClient


def test_operational_control_plane_mounts_required_dashboard_routes():
    from claire.app import create_app

    client = TestClient(create_app())
    payload = client.get("/api/operational/control-plane").json()

    assert payload["schema_version"] == "claire_operational_control_plane_v1"
    assert payload["status"] == "operational_ready"
    assert payload["route_health"]["status"] == "ready"
    assert payload["file_readiness"]["status"] == "ready"
    assert payload["source_lineage"]["status"] == "ready"
    assert payload["internet_authority"]["live_internet_enabled"] is False
    assert payload["update_governance"]["automatic_updates_enabled"] is False
    action_ids = {action["id"] for action in payload["actions"]}
    assert {"start_continuous_runtime", "evaluate_demo_payload", "open_search_plans"} <= action_ids


def test_missing_gap_routes_now_resolve_as_operational_read_only_surfaces():
    from claire.app import create_app

    client = TestClient(create_app())
    expected = [
        "/api/lifecycle/stage-registry",
        "/api/lifecycle/threshold-provenance",
        "/api/source-lineage/status",
        "/api/update/status",
        "/api/platform/update/plan",
    ]

    for path in expected:
        response = client.get(path)
        assert response.status_code == 200, path

    assert client.get("/api/lifecycle/stage-registry").json()["stage_count"] == 30
    assert client.get("/api/lifecycle/threshold-provenance").json()["threshold_rule_count"] > 0
    assert client.get("/api/platform/update/plan").json()["execution_enabled"] is False


def test_dashboard_v5_uses_operational_control_plane_and_callable_actions():
    from claire.app import create_app

    client = TestClient(create_app())
    dashboard = client.get("/api/dashboard/v5/payload").json()
    operational = client.get("/api/operational/control-plane").json()

    assert dashboard["operational_control_plane"]["schema_version"] == "claire_operational_control_plane_v1"
    assert len(operational["actions"]) >= 8
    for action in operational["actions"]:
        if action["method"] == "POST":
            response = client.post(action["endpoint"], json=action.get("body") or {})
        else:
            response = client.get(action["endpoint"])
        assert response.status_code == 200, action["endpoint"]


def test_final_operational_wiring_gate_passes():
    from tools.plateau.final_operational_wiring_gate import run_gate

    report = run_gate()

    assert report["status"] == "complete"
    assert report["completion_percent"] == 100
    assert report["scores"]["dashboard_has_callable_actions"] == 100
