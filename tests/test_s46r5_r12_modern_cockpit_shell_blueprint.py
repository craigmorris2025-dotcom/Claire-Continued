from __future__ import annotations

from pathlib import Path

import importlib


ROOT = Path(__file__).resolve().parents[1]
MODERN_ROOT = ROOT / "frontend" / "cockpit" / "modern_shell"
HTML = MODERN_ROOT / "claire_modern_cockpit_shell.html"
JS = MODERN_ROOT / "claire_modern_cockpit_shell.js"
CSS = MODERN_ROOT / "claire_modern_cockpit_shell.css"


def test_s46r5_modern_cockpit_shell_blueprint_is_safe():
    module = importlib.import_module("claire.api.s46_modern_cockpit_shell_blueprint")
    blueprint = module.build_modern_cockpit_shell_blueprint()

    assert blueprint["version"] == "v19.89.8-S46R5-R12"
    assert blueprint["status"] == "modern_cockpit_shell_blueprint_ready"
    assert blueprint["region_count"] == 4
    assert blueprint["backend_owns_truth"] is True
    assert blueprint["cockpit_presentation_only"] is True
    assert blueprint["runtime_truth_mutation_allowed"] is False
    assert blueprint["operator_mutation_enabled"] is False

    for region in blueprint["shell_regions"]:
        assert region["visible"] is True
        assert region["presentation_only"] is True
        assert region["runtime_truth_mutation_allowed"] is False
        assert region["response_mode"] == "read_only_artifact"


def test_s46r8_modern_cockpit_shell_blueprint_verifies_cleanly():
    module = importlib.import_module("claire.api.s46_modern_cockpit_shell_blueprint")
    verification = module.verify_modern_cockpit_shell_blueprint()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["region_count"] == 4


def test_s46r9_r12_modern_shell_assets_exist_and_are_read_only():
    assert HTML.exists()
    assert JS.exists()
    assert CSS.exists()

    html = HTML.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8").lower()

    assert "Claire Modern Cockpit Shell" in html
    assert 'data-runtime-truth-mutation-allowed="false"' in html
    assert "runtimeTruthMutationAllowed: false" in js
    assert "operatorMutationEnabled: false" in js
    assert 'method: "GET"' in js
    assert "read_only_artifact" in js
    assert "presentation-only" in css


def test_s46r12_plateau_report_ready():
    module = importlib.import_module("claire.api.s46_modern_cockpit_shell_blueprint")
    report = module.build_s46r5_r12_plateau_report()

    assert report["status"] == "s46r5_r12_ready"
    assert report["ready"] is True
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["operator_mutation_enabled"] is False
    assert report["next_phase"] == "S47 operator live status zones and cockpit payload aggregation"
