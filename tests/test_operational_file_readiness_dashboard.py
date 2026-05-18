from __future__ import annotations

from fastapi.testclient import TestClient


def test_operational_file_readiness_route_reports_required_and_polluted_roots():
    from claire.app import create_app

    client = TestClient(create_app())
    response = client.get("/api/system/file-readiness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["backend_owns_truth"] is True
    assert payload["cleanup_approved"] is False
    assert payload["destructive_cleanup_performed"] is False
    assert "required_roots" in payload
    assert "required_files" in payload
    assert "pollution_summary" in payload
    assert "backend" not in payload["target_missing"]
    assert any(item["name"] == "backend" and item["exists"] for item in payload["desired_target_roots"])
    assert any(item["name"] == "claire" and item["exists"] for item in payload["required_roots"])
    assert any(item["name"] == "frontend" and item["exists"] for item in payload["required_roots"])


def test_dashboard_v3_fetches_operational_file_readiness():
    dashboard_js = "frontend/command_center/modern/dashboard_endpoint_mapped_v3.js"

    with open(dashboard_js, "r", encoding="utf-8") as handle:
        text = handle.read()

    assert "/api/system/file-readiness" in text
    assert "file-readiness" in text
    assert "/api/system/route-integrity" in text
    assert "/api/governed/live-probe/status" in text
    assert "setOpsCard" in text


def test_route_integrity_reports_dashboard_payload_owner_state():
    from claire.app import create_app

    client = TestClient(create_app())
    response = client.get("/api/system/route-integrity")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["dashboard_payload"]["owner_count"] >= 1
    assert payload["dashboard_payload"]["canonical_payload_locked"] is True
    assert payload["dashboard_payload"]["canonical_owner"]["module"] in {
        "claire.app",
        "claire.api.dashboard_payload_bridge",
    }
    assert payload["duplicate_route_count"] == 0
    assert payload["blockers"] == []
