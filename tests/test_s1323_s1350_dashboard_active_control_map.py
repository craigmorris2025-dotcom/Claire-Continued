from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_s1323_s1350_active_control_map_exposes_all_required_capabilities():
    from claire.api.dashboard_active_control_map import build_dashboard_active_control_map

    payload = build_dashboard_active_control_map()

    assert payload["status"] == "ready"
    assert payload["control_count"] == 15
    assert payload["authority"]["unsafe_authority_unlocked"] is False
    assert payload["authority"]["blocked"]["body_reads"] == "blocked"

    keys = {control["key"] for control in payload["controls"]}
    expected = {
        "system_health_plateau",
        "dashboard_payload",
        "dashboard_actions",
        "operator_console",
        "cockpit_operations",
        "command_bar",
        "governed_search",
        "provider_readiness",
        "metadata_live_probe",
        "evidence_review",
        "source_registry_policy",
        "body_read_gates",
        "runtime_spine_lifecycle",
        "update_truth_promotion",
        "live_intelligence_catalog",
    }
    assert expected == keys

    for control in payload["controls"]:
        assert control["primary_endpoint"].startswith("/")
        assert control["button_label"]
        assert control["execution_enabled"] is False
        assert control["body_read_allowed"] is False
        assert control["runtime_mutation_allowed"] is False
        assert control["command_execution_allowed"] is False


def test_s1323_s1350_active_control_map_routes_mount_through_create_app():
    from claire.app import create_app

    client = TestClient(create_app())

    api = client.get("/api/dashboard/active-control-map")
    dashboard = client.get("/dashboard/active-control-map")

    assert api.status_code == 200
    assert dashboard.status_code == 200

    data = api.json()
    assert data["control_count"] == 15
    assert data["frontend_contract"]["must_render_visible_buttons"] is True
    assert data["frontend_contract"]["must_fetch_control_primary_endpoint_on_click"] is True

    for control in data["controls"]:
        response = client.get(control["primary_endpoint"])
        assert response.status_code == 200, control["primary_endpoint"]


def test_s1323_s1350_frontend_assets_mount_and_use_fetch_for_active_controls():
    js = Path("frontend/command_center/modern/dashboard_active_control_map.js")
    css = Path("frontend/command_center/modern/dashboard_active_control_map.css")
    index = Path("frontend/command_center/modern/index.html")
    dashboard_v3 = Path("frontend/command_center/modern/dashboard_endpoint_mapped_v3.html")

    assert js.exists()
    assert css.exists()
    assert index.exists()
    assert dashboard_v3.exists()

    js_text = js.read_text(encoding="utf-8")
    index_text = index.read_text(encoding="utf-8")
    dashboard_v3_text = dashboard_v3.read_text(encoding="utf-8")

    assert "/api/dashboard/active-control-map" in js_text
    assert "fetch(url" in js_text
    assert "AUDIT_VISIBLE_BACKEND_BINDINGS" in js_text
    assert "renderControls(payload)" in js_text
    assert "fetchControlResult" in js_text
    assert "data-control-endpoint" in js_text
    assert "claire-active-control-result-pane" in js_text
    assert "/api/search/governed/plans" in js_text
    assert "/api/governed/runtime-spine" in js_text
    assert "body reads blocked" in js_text.lower()
    assert "runtime mutation blocked" in js_text.lower()
    assert "dashboard_active_control_map.js" in index_text
    assert "dashboard_active_control_map.css" in index_text
    assert "dashboard_active_control_map.js" in dashboard_v3_text
    assert "dashboard_active_control_map.css" in dashboard_v3_text
    assert "Active Backend Controls" in dashboard_v3_text
    assert "data-claire-active-control-grid" in dashboard_v3_text
    assert "claire-active-control-result-pane" in dashboard_v3_text
