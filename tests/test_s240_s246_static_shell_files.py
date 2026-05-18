from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHELL = ROOT / "frontend" / "cockpit" / "modern"


def test_s240_s246_html_contains_required_regions_and_disabled_unsafe_buttons():
    html = (SHELL / "claire_cockpit_shell.html").read_text(encoding="utf-8")

    for region in [
        "top_command_bar",
        "primary_runtime_panel",
        "operations_strip",
        "monitoring_column",
        "lifecycle_evidence_workspace",
        "diagnostics_drawer",
    ]:
        assert f'id="{region}"' in html

    assert 'data-authority="presentation-only"' in html
    assert 'data-action-id="run_autonomous_update" disabled' in html
    assert 'data-action-id="execute_runtime_mutation" disabled' in html


def test_s240_s246_js_uses_safe_fetch_and_blocks_unsafe_actions():
    js = (SHELL / "claire_cockpit_shell.js").read_text(encoding="utf-8")

    assert 'canonical_payload: "/dashboard/payload"' in js
    assert 'payload_status: "/dashboard/payload/status"' in js
    assert 'health: "/health"' in js
    assert 'run_autonomous_update: "automatic_updates_blocked"' in js
    assert 'execute_runtime_mutation: "runtime_mutation_blocked"' in js
    assert 'method: "GET"' in js
    assert "ClaireCockpitShell" in js


def test_s240_s246_css_defines_single_cockpit_grid_and_responsive_layout():
    css = (SHELL / "claire_cockpit_shell.css").read_text(encoding="utf-8")

    assert "#claire-cockpit" in css
    assert "grid-template-areas" in css
    assert "#top_command_bar" in css
    assert "#primary_runtime_panel" in css
    assert "#operations_strip" in css
    assert "@media (max-width: 900px)" in css
