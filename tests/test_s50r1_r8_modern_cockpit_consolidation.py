from __future__ import annotations

from pathlib import Path

import importlib


ROOT = Path(__file__).resolve().parents[1]
MODERN_ROOT = ROOT / "frontend" / "cockpit" / "modern_shell"
HTML = MODERN_ROOT / "claire_consolidated_cockpit.html"
JS = MODERN_ROOT / "claire_consolidated_cockpit.js"
CSS = MODERN_ROOT / "claire_consolidated_cockpit.css"
ROUTE_JS = MODERN_ROOT / "claire_route_payload_browser.js"
WEB_JS = MODERN_ROOT / "claire_governed_web_panels.js"


def test_s50r1_consolidation_manifest_ready():
    module = importlib.import_module("runtime_core.api.s50_modern_cockpit_consolidation")
    manifest = module.build_modern_cockpit_consolidation_manifest()

    assert manifest["version"] == "v19.89.8-S50R1-R8"
    assert manifest["status"] == "modern_cockpit_consolidation_manifest_ready"
    assert manifest["ready"] is True
    assert manifest["section_count"] == 5
    assert manifest["backend_owns_truth"] is True
    assert manifest["cockpit_presentation_only"] is True
    assert manifest["runtime_truth_mutation_allowed"] is False
    assert manifest["automatic_updates_enabled"] is False
    assert manifest["live_web_execution_enabled"] is False

    for section in manifest["sections"]:
        assert section["visible"] is True
        assert section["presentation_only"] is True
        assert section["runtime_truth_mutation_allowed"] is False
        assert section["operator_mutation_enabled"] is False


def test_s50r4_consolidation_manifest_verifies_cleanly():
    module = importlib.import_module("runtime_core.api.s50_modern_cockpit_consolidation")
    verification = module.verify_modern_cockpit_consolidation_manifest()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["section_count"] == 5


def test_s50r5_demo_readiness_snapshot_is_honest_about_remaining_gap():
    module = importlib.import_module("runtime_core.api.s50_modern_cockpit_consolidation")
    snapshot = module.build_demo_readiness_snapshot()

    assert snapshot["status"] == "demo_readiness_snapshot_ready"
    assert snapshot["dashboard_ready"] is True
    assert snapshot["operator_panels_ready"] is True
    assert snapshot["route_browser_ready"] is True
    assert snapshot["governed_web_visible"] is True
    assert snapshot["evidence_review_visible"] is True
    assert snapshot["useful_outputs_ready"] is False
    assert snapshot["live_web_updates_enabled"] is False
    assert snapshot["next_gap"] == "route-specific useful output surfaces"


def test_s50r6_frontend_consolidated_assets_exist_and_are_safe():
    for path in (HTML, JS, CSS, ROUTE_JS, WEB_JS):
        assert path.exists()

    html = HTML.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    route_js = ROUTE_JS.read_text(encoding="utf-8")
    web_js = WEB_JS.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8").lower()

    assert "Claire Consolidated Modern Cockpit" in html
    assert 'data-runtime-truth-mutation-allowed="false"' in html
    assert 'data-live-web-execution-enabled="false"' in html
    assert "runtimeTruthMutationAllowed: false" in js
    assert "operatorMutationEnabled: false" in js
    assert "liveWebExecutionEnabled: false" in js
    assert "runtimeTruthMutationAllowed: false" in route_js
    assert "quarantineRequired: true" in web_js
    assert "presentation-only" in css


def test_s50r8_plateau_report_points_to_useful_outputs():
    module = importlib.import_module("runtime_core.api.s50_modern_cockpit_consolidation")
    report = module.build_s50r1_r8_plateau_report()

    assert report["status"] == "s50r1_r8_ready"
    assert report["ready"] is True
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["operator_mutation_enabled"] is False
    assert report["automatic_updates_enabled"] is False
    assert report["autonomous_execution_enabled"] is False
    assert report["next_phase"] == "S51 route-specific useful output surfaces"
