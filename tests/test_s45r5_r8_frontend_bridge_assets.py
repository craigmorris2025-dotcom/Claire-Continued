from __future__ import annotations

from pathlib import Path

import importlib


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = ROOT / "frontend" / "cockpit" / "s45_bridge"
JS = BRIDGE_DIR / "s45_cockpit_bridge.js"
CSS = BRIDGE_DIR / "s45_cockpit_bridge.css"
README = BRIDGE_DIR / "README.md"


def test_s45r5_frontend_bridge_assets_exist():
    assert JS.exists()
    assert CSS.exists()
    assert README.exists()


def test_s45r6_frontend_bridge_js_is_presentation_only():
    text = JS.read_text(encoding="utf-8")

    assert "presentationOnly: true" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "operatorMutationEnabled: false" in text
    assert 'method: "GET"' in text
    assert "read_only_artifact" in text
    assert "automaticUpdatesEnabled: false" in text
    assert "autonomousExecutionEnabled: false" in text


def test_s45r7_frontend_bridge_css_is_presentation_only():
    text = CSS.read_text(encoding="utf-8").lower()

    assert "presentation only" in text
    assert "runtime authority" in text


def test_s45r8_plateau_report_ready():
    module = importlib.import_module("runtime_core.api.s45_operator_visible_panels")
    report = module.build_s45r1_r8_plateau_report()

    assert report["version"] == "v19.89.8-S45R1-R8"
    assert report["status"] == "s45r1_r8_ready"
    assert report["ready"] is True
    assert report["backend_owns_truth"] is True
    assert report["cockpit_presentation_only"] is True
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["next_phase"] == "S45R9-R16 cockpit shell bridge integration and panel data mounting"
