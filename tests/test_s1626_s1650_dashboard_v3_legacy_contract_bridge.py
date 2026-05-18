from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from claire.app import create_app


ROOT = Path(__file__).resolve().parents[1]
MODERN = ROOT / "frontend" / "command_center" / "modern"
INDEX = MODERN / "index.html"
DASHBOARD_MARKER = 'data-dashboard-v3="endpoint-mapped-final-operator-dashboard"'


def test_s1626_dashboard_v3_stays_active_and_legacy_assets_are_linked():
    text = INDEX.read_text(encoding="utf-8")
    assert DASHBOARD_MARKER in text
    assert "operator_action_click_bridge.js" in text
    assert "dashboard_active_control_map.js" in text
    assert "operational_expansion_dock_s312.js" in text


def test_s1626_legacy_assets_exist_and_are_real_bridge_files():
    for name, needle in [
        ("operator_action_click_bridge.js", "ClaireOperatorActionClickBridge"),
        ("dashboard_active_control_map.js", "ClaireDashboardActiveControlMap"),
        ("operational_expansion_dock_s312.js", "ClaireOperationalExpansionDockS312"),
    ]:
        path = MODERN / name
        assert path.exists(), name
        assert needle in path.read_text(encoding="utf-8")


def test_s1626_dashboard_route_serves_v3():
    client = TestClient(create_app())
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert DASHBOARD_MARKER in response.text


def test_s1626_compat_plateau_audit_contracts_are_locked_clean():
    client = TestClient(create_app())
    for path in [
        "/dashboard/plateau-lock",
        "/dashboard/full-project-plateau-lock",
        "/dashboard/direct-create-app-audit-route-mount-repair",
        "/dashboard/risk-review-audit-integration",
    ]:
        response = client.get(path)
        assert response.status_code == 200, path
        payload = response.json()
        assert payload["status"] == "locked", path
        assert payload["summary"]["warning_count"] == 0, path
        assert payload["summary"]["blocker_count"] == 0, path


def test_s1626_existing_dashboard_contracts_still_work():
    client = TestClient(create_app())
    for path in ["/dashboard/payload", "/dashboard/payload/status", "/api/dashboard/active-control-map", "/dashboard/active-control-map", "/dashboard/endpoint-map"]:
        response = client.get(path)
        assert response.status_code == 200, path


def test_s1626_dashboard_route_serves_legacy_bridge_assets():
    client = TestClient(create_app())
    for path, needle in [
        ("/dashboard/v3/assets/operator_action_click_bridge.js", "ClaireOperatorActionClickBridge"),
        ("/dashboard/v3/assets/dashboard_active_control_map.js", "ClaireDashboardActiveControlMap"),
        ("/dashboard/v3/assets/operational_expansion_dock_s312.js", "ClaireOperationalExpansionDockS312"),
    ]:
        response = client.get(path)
        assert response.status_code == 200, path
        assert needle in response.text, path
