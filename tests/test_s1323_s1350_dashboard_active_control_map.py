from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_s1323_s1350_active_control_map_exposes_all_required_capabilities():
    from runtime_core.api.dashboard_active_control_map import build_dashboard_active_control_map

    payload = build_dashboard_active_control_map()

    assert payload["status"] == "ready"
    assert payload["control_count"] == 19
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
        "endpoint_standard_package",
        "endpoint_reconciliation",
        "dependency_chain_proof",
        "design_cad_contract",
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
    from runtime_core.app import create_app

    client = TestClient(create_app())

    api = client.get("/api/dashboard/active-control-map")
    dashboard = client.get("/dashboard/active-control-map")

    assert api.status_code == 200
    assert dashboard.status_code == 200

    data = api.json()
    assert data["control_count"] == 19
    assert data["frontend_contract"]["must_render_visible_buttons"] is True
    assert data["frontend_contract"]["must_fetch_control_primary_endpoint_on_click"] is True

    for control in data["controls"]:
        response = client.get(control["primary_endpoint"])
        assert response.status_code == 200, control["primary_endpoint"]


def test_s1323_s1350_frontend_assets_mount_and_use_fetch_for_active_controls():
    legacy_js = Path("frontend/command_center/modern/dashboard_active_control_map.js")
    legacy_css = Path("frontend/command_center/modern/dashboard_active_control_map.css")
    index = Path("frontend/command_center/modern/index.html")
    dashboard_v3 = Path("frontend/command_center/modern/dashboard_endpoint_mapped_v3.html")
    canonical_html = Path("frontend/command_center/modern/platform_dashboard.html")
    canonical_js = Path("frontend/command_center/modern/platform_dashboard.js")

    assert not legacy_js.exists()
    assert not legacy_css.exists()
    assert not dashboard_v3.exists()
    assert index.exists()
    assert canonical_html.exists()
    assert canonical_js.exists()

    index_text = index.read_text(encoding="utf-8")
    canonical_html_text = canonical_html.read_text(encoding="utf-8")
    canonical_js_text = canonical_js.read_text(encoding="utf-8")

    assert 'content="0; url=/dashboard"' in index_text
    assert "platform_dashboard.js" in canonical_html_text
    assert "platform_dashboard.css" in canonical_html_text
    assert "/api/dashboard/state" in canonical_js_text
    assert "/api/dashboard/active-control-map" in canonical_js_text
    assert "renderActiveControls" in canonical_js_text
    assert "runActiveControl" in canonical_js_text
    assert "claire-active-control-result-pane" in canonical_js_text
    assert "active-control-grid" in (Path("frontend/command_center/modern/platform_dashboard.css").read_text(encoding="utf-8"))
    assert "dashboardState" in canonical_js_text
    assert "renderTechnology" in canonical_js_text
    assert "dashboard_active_control_map.js" not in index_text
    assert "dashboard_active_control_map.css" not in index_text
