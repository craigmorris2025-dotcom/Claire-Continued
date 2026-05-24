from __future__ import annotations

from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "frontend" / "cockpit" / "modern_shell" / "claire_output_package_browser.js"

def test_s56r1_package_manifest_is_review_only():
    module = importlib.import_module("runtime_core.api.s56_output_package_export_manifest")
    manifest = module.build_output_package_export_manifest()
    assert manifest["version"] == "v19.89.8-S56R1-R8"
    assert manifest["status"] == "output_package_export_manifest_ready"
    assert manifest["package_count"] == 7
    assert manifest["runtime_truth_write_allowed"] is False
    for package in manifest["packages"]:
        assert package["package_state"] == "available_for_operator_review"
        assert package["requires_manual_review"] is True
        assert package["runtime_truth_write_allowed"] is False
        assert package["auto_package_enabled"] is False
        assert package["auto_promotion_enabled"] is False
        assert "json" in package["allowed_formats"]

def test_s56r5_review_bundles_are_operator_visible_without_auto_submit():
    module = importlib.import_module("runtime_core.api.s56_output_package_export_manifest")
    manifest = module.build_review_bundle_readiness_manifest()
    assert manifest["status"] == "review_bundle_readiness_manifest_ready"
    assert manifest["bundle_count"] == 7
    for bundle in manifest["bundles"]:
        assert bundle["bundle_state"] == "ready_for_review"
        assert bundle["review_required"] is True
        assert bundle["operator_visible"] is True
        assert bundle["runtime_truth_write_allowed"] is False
        assert bundle["auto_submit_enabled"] is False
        assert bundle["auto_promotion_enabled"] is False

def test_s56r6_frontend_output_package_asset_is_safe():
    assert JS.exists()
    text = JS.read_text(encoding="utf-8")
    assert "CLAIRE_OUTPUT_PACKAGE_BROWSER_CONTRACT" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "runtimeTruthWriteAllowed: false" in text
    assert "operatorMutationEnabled: false" in text
    assert "manualPromotionRequired: true" in text

def test_s56r8_plateau_report_ready():
    module = importlib.import_module("runtime_core.api.s56_output_package_export_manifest")
    report = module.build_s56r1_r8_plateau_report()
    assert report["status"] == "s56r1_r8_ready"
    assert report["ready"] is True
    assert report["verification"]["verification_ok"] is True
    assert report["next_phase"] == "S57 output-to-dashboard mounting and useful output cards"
