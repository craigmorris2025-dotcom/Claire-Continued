from __future__ import annotations

from pathlib import Path
import importlib


ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "frontend" / "cockpit" / "modern_shell" / "claire_useful_output_browser.js"
CSS = ROOT / "frontend" / "cockpit" / "modern_shell" / "claire_useful_output_browser.css"


def test_s53r1_cockpit_useful_output_browser_cards_ready():
    module = importlib.import_module("runtime_core.api.s53_cockpit_useful_output_browser")
    browser = module.build_cockpit_useful_output_browser()

    assert browser["version"] == "v19.89.8-S53R1-R8"
    assert browser["status"] == "cockpit_useful_output_browser_ready"
    assert browser["card_count"] == 7
    assert browser["backend_owns_truth"] is True
    assert browser["runtime_truth_mutation_allowed"] is False

    for card in browser["cards"]:
        assert card["visible_to_operator"] is True
        assert card["display_mode"] == "useful_output_card"
        assert card["section_count"] > 0
        assert card["runtime_truth_mutation_allowed"] is False
        assert card["operator_mutation_enabled"] is False


def test_s53r5_output_export_registry_is_manual_review_only():
    module = importlib.import_module("runtime_core.api.s53_cockpit_useful_output_browser")
    registry = module.build_output_export_registry()

    assert registry["status"] == "output_export_registry_ready"
    assert registry["export_count"] == 7

    for export in registry["exports"]:
        assert "json" in export["allowed_formats"]
        assert "markdown" in export["allowed_formats"]
        assert export["requires_manual_review"] is True
        assert export["runtime_truth_write_allowed"] is False
        assert export["auto_export_enabled"] is False
        assert export["auto_promotion_enabled"] is False


def test_s53r6_frontend_useful_output_assets_exist_and_are_safe():
    assert JS.exists()
    assert CSS.exists()

    js = JS.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8").lower()

    assert "CLAIRE_USEFUL_OUTPUT_BROWSER_CONTRACT" in js
    assert "runtimeTruthMutationAllowed: false" in js
    assert "operatorMutationEnabled: false" in js
    assert "manualPromotionRequired: true" in js
    assert "read_only_artifact" in js
    assert "presentation-only" in css


def test_s53r8_plateau_report_ready():
    module = importlib.import_module("runtime_core.api.s53_cockpit_useful_output_browser")
    report = module.build_s53r1_r8_plateau_report()

    assert report["status"] == "s53r1_r8_ready"
    assert report["ready"] is True
    assert report["verification"]["verification_ok"] is True
    assert report["next_phase"] == "S54 useful output persistence and run history integration"
