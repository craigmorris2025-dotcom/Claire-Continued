from __future__ import annotations

from pathlib import Path
import importlib


def test_s78_s84_vertical_slice_ready_and_safe():
    module = importlib.import_module("claire.api.s78_s84_governed_web_vertical_slice")
    report = module.build_s78_s84_plateau_report()
    assert report["status"] == "s78_s84_ready"
    assert report["ready"] is True
    assert report["backend_owns_truth"] is True
    assert report["cockpit_presentation_only"] is True
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["runtime_truth_write_allowed"] is False
    assert report["operator_mutation_enabled"] is False
    assert report["automatic_updates_enabled"] is False
    assert report["autonomous_execution_enabled"] is False
    assert report["live_web_execution_enabled"] is False
    assert report["verification"]["verification_ok"] is True
    assert report["verification"]["failures"] == []


def test_s79_probe_is_manual_and_dry_run_only():
    module = importlib.import_module("claire.api.s78_s84_governed_web_vertical_slice")
    dry_run = module.s79_probe_dry_run("test")
    assert dry_run["dry_run"] is True
    assert dry_run["would_execute_network"] is False
    assert dry_run["network_request_performed"] is False
    assert dry_run["request"]["operator_ack_required"] is True
    assert dry_run["request"]["body_read_allowed"] is False


def test_s81_to_s84_evidence_becomes_visible_but_not_promoted():
    module = importlib.import_module("claire.api.s78_s84_governed_web_vertical_slice")
    basket = module.s81_evidence_basket()
    card = module.s84_dashboard_evidence_card()
    assert basket["evidence_count"] == 1
    assert card["card_count"] == 1
    for evidence in basket["evidence_items"]:
        assert evidence["evidence_state"] == "quarantined"
        assert evidence["promoted_to_runtime_truth"] is False
        assert evidence["runtime_truth_write_allowed"] is False
    for item in card["cards"]:
        assert item["visible_to_operator"] is True
        assert item["promoted_to_runtime_truth"] is False
        assert item["runtime_truth_write_allowed"] is False
        assert item["entities"]


def test_s84_frontend_evidence_card_asset_exists_and_is_safe():
    asset = Path(__file__).resolve().parents[1] / "frontend" / "cockpit" / "modern_shell" / "claire_s84_evidence_card.js"
    assert asset.exists()
    text = asset.read_text(encoding="utf-8")
    assert "runtimeTruthMutationAllowed: false" in text
    assert "runtimeTruthWriteAllowed: false" in text
    assert "manualPromotionRequired: true" in text
