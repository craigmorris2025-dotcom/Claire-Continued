from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHELL = ROOT / 'frontend/cockpit/shell/cockpit_shell.html'
REQUIRED_JS = ['continuous_runtime_presence.js', 'governed_search_session.js', 'governed_evidence_basket.js', 'runtime_continuity_visualization.js', 'continuous_browser_runtime_loop.js', 'governed_operator_workflow.js', 'canonical_browser_session_persistence.js', 'multi_panel_runtime_cohesion.js', 'governed_operational_session_orchestration.js', 'governed_runtime_workspace_continuity.js', 'governed_multi_workspace_orchestration.js', 'governed_operational_topology_continuity.js']


def test_s31r_active_shell_exists():
    assert SHELL.exists()


def test_s31r_dashboard_assets_are_linked():
    text = SHELL.read_text(encoding='utf-8')
    for token in REQUIRED_JS:
        assert token in text, token


def test_s31r_visibility_bridge_does_not_patch_app_factory():
    app_file = ROOT / 'claire' / 'app.py'
    assert app_file.exists()
    text = app_file.read_text(encoding='utf-8')
    assert 'v19.89.8-S31R governed optional route registration block' not in text
