from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_s1265_s1292_plateau_lock_confirms_clean_audit_state():
    from claire.audit.plateau_completion_lock import build_plateau_completion_lock

    payload = build_plateau_completion_lock(Path.cwd(), write_audit_report=True)

    assert payload["status"] == "locked"
    assert payload["plateau_ready"] is True
    assert payload["forward_motion_allowed"] is True
    assert payload["blocker_count"] == 0
    assert payload["warning_count"] == 0
    assert payload["issue_count"] == 0
    assert payload["python_syntax"]["failure_count"] == 0
    assert payload["environment"]["dangerous_enabled"] == {}
    assert payload["environment"]["network_probe_enabled"] == {}
    assert payload["static_risk_scan"]["unreviewed_finding_count"] == 0
    assert payload["missing_or_bad_routes"] == {}

    for route, status in payload["key_route_status"].items():
        assert status == 200, route


def test_s1265_s1292_plateau_lock_routes_mount_through_create_app():
    from claire.app import create_app

    client = TestClient(create_app())

    api = client.get("/api/audit/plateau-lock")
    dashboard = client.get("/dashboard/audit/plateau-lock")

    assert api.status_code == 200
    assert dashboard.status_code == 200

    data = api.json()
    assert data["status"] == "locked"
    assert data["forward_motion_allowed"] is True
    assert data["blocked_authority"]["runtime_mutation"] == "blocked"
    assert data["blocked_authority"]["body_reads"] == "blocked"
    assert data["next_phase"]["recommended"].startswith("S1293-S1320")
