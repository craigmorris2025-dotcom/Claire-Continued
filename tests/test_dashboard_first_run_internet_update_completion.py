from __future__ import annotations

from pathlib import Path

from runtime_core.dashboard.cockpit_dashboard_state import build_cockpit_dashboard_state


def test_dashboard_state_exposes_first_run_internet_and_update_logic():
    payload = build_cockpit_dashboard_state(Path.cwd())

    assert payload["first_run_readiness"]["schema_version"] == "claire.first_run_readiness.v1"
    assert payload["first_run_readiness"]["operator_review_required"] is True
    assert payload["first_run_readiness"]["runtime_truth_mutated"] is False
    assert payload["internet_provider_diagnostics"]["schema_version"] == "claire.internet_provider_diagnostics.v1"
    assert payload["internet_provider_diagnostics"]["metadata_only"] is True
    assert payload["internet_provider_diagnostics"]["body_reads_allowed"] is False
    assert payload["internet_provider_diagnostics"]["fetch_enabled"] is True
    assert payload["internet_provider_diagnostics"]["readiness_percent"] == 100
    assert payload["internet_provider_diagnostics"]["rate_limits"]["max_queries_per_minute"] == 6
    assert payload["update_logic_status"]["schema_version"] == "claire.update_logic_status.v1"
    assert payload["update_logic_status"]["automatic_updates_enabled"] is False
    assert payload["update_logic_status"]["package_install_performed"] is False
    assert payload["operational_conditions"]["status"] == "configured_for_governed_first_run"
    assert payload["operational_conditions"]["internet_provider"]["mode"] == "metadata_only_quarantine_first"
    assert payload["metrics"]["first_run_readiness"]["value"] is not None
    assert "first_run_readiness" in payload["records"]
    assert "internet_provider_diagnostics" in payload["records"]


def test_dashboard_frontend_renders_first_run_internet_and_update_sections():
    js = Path("frontend/command_center/modern/platform_dashboard.js").read_text(encoding="utf-8")

    assert "renderFirstRun" in js
    assert "renderInternet" in js
    assert "renderUpdates" in js
    assert "renderPortalLauncher" in js
    assert "openPortal" in js
    assert "portal-launch-btn" in js
    assert "Portal Launcher" in js
    assert "First-Run Readiness" in js
    assert "Internet Provider Diagnostic" in js
    assert "Update Governance" in js
    assert "automatic_updates_enabled" in js
    assert "Weekly/rate guard" in js
    assert "Live internet pack" in js
    assert "Updates pack" in js


def test_dashboard_frontend_exposes_clickable_portal_launcher_styles():
    css = Path("frontend/command_center/modern/platform_dashboard.css").read_text(encoding="utf-8")

    assert ".portal-grid" in css
    assert ".portal-launch-btn" in css
    assert ".portal-command-btn" in css


def test_main_uses_env_host_and_port_for_direct_launch():
    text = Path("main.py").read_text(encoding="utf-8")

    assert 'os.environ.get("PLATFORM_HOST", "127.0.0.1")' in text
    assert 'os.environ.get("PLATFORM_PORT", "8000")' in text
