from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.api.dashboard_status_shell_cleanup_s359_s365 import (
    build_dashboard_status_shell_cleanup_s359_s365,
    build_s359_dashboard_status_version_harmonization,
    build_s360_expansion_dock_disable_contract,
    build_s361_cockpit_shell_cleanup_asset_manifest,
    build_s362_dashboard_payload_shell_cleanup_extension,
    build_s363_shell_cleanup_visibility_proof,
    build_s364_route_registration_proof,
    build_s365_stop_gate,
    register_s359_s365_dashboard_status_cleanup_routes,
)


def test_s359_harmonized_status_supersedes_legacy_label():
    payload = build_s359_dashboard_status_version_harmonization()
    status = payload["harmonized_status"]
    assert payload["stage_version"] == "S359"
    assert status["status"] == "ok"
    assert status["stage_version"] == "S359"
    assert status["current_plateau"] == "v19.89.8-S358-dashboard-visibility-green"


def test_s360_expansion_dock_is_disabled_and_removed():
    payload = build_s360_expansion_dock_disable_contract()
    dock = payload["expansion_dock"]
    assert payload["stage_version"] == "S360"
    assert dock["enabled"] is False
    assert dock["visible"] is False
    assert dock["removed_from_primary_cockpit"] is True
    assert "#expansion-dock" in dock["hide_selectors"]


def test_s361_cleanup_assets_exist_and_shell_injection_is_safe():
    payload = build_s361_cockpit_shell_cleanup_asset_manifest()
    assets = payload["assets"]
    assert payload["stage_version"] == "S361"
    assert assets["css_exists"] is True
    assert assets["js_exists"] is True
    assert assets["shell_injection_present_or_shell_absent"] is True


def test_s362_payload_extension_marks_expansion_dock_removed():
    payload = build_s362_dashboard_payload_shell_cleanup_extension()
    cleanup = payload["shell_cleanup_extension"]["dashboard_shell_cleanup"]
    assert payload["stage_version"] == "S362"
    assert cleanup["expansion_dock_enabled"] is False
    assert cleanup["expansion_dock_removed"] is True
    assert cleanup["legacy_s43_status_superseded"] is True


def test_s363_shell_cleanup_visibility_proof_passes():
    payload = build_s363_shell_cleanup_visibility_proof()
    assert payload["stage_version"] == "S363"
    assert payload["shell_cleanup_visible"] is True
    assert all(payload["checks"].values())


def test_s364_routes_register_for_status_and_cleanup():
    payload = build_s364_route_registration_proof()
    assert payload["stage_version"] == "S364"
    assert payload["harmonized_status_registered"] is True
    assert payload["shell_cleanup_registered"] is True


def test_s364_routes_work_with_testclient():
    app = FastAPI()
    register_s359_s365_dashboard_status_cleanup_routes(app)
    client = TestClient(app)
    status = client.get("/dashboard/status/harmonized")
    assert status.status_code == 200
    assert status.json()["status"] == "ok"
    cleanup = client.get("/dashboard/shell/cleanup/status")
    assert cleanup.status_code == 200
    assert cleanup.json()["expansion_dock_removed"] is True


def test_s365_stop_gate_allows_forward_motion(tmp_path):
    payload = build_s365_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S365"
    assert payload["forward_motion_allowed"] is True
    assert payload["dashboard_status_harmonized"] is True
    assert payload["expansion_dock_removed"] is True
    assert "report_path" in payload


def test_s359_s365_rollup_ready():
    payload = build_dashboard_status_shell_cleanup_s359_s365()
    assert payload["stage_version"] == "S365"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
