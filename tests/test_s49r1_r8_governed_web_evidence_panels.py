from __future__ import annotations

import importlib


def test_s49r1_governed_web_panels_are_visible_but_fail_closed():
    module = importlib.import_module("runtime_core.api.s49_governed_web_evidence_panels")
    manifest = module.build_governed_web_panel_manifest()

    assert manifest["version"] == "v19.89.8-S49R1-R8"
    assert manifest["status"] == "governed_web_panel_manifest_ready"
    assert manifest["panel_count"] == 5
    assert manifest["live_web_execution_enabled"] is False
    assert manifest["automatic_updates_enabled"] is False
    assert manifest["runtime_truth_mutation_allowed"] is False
    assert manifest["manual_promotion_required"] is True
    assert manifest["quarantine_required"] is True

    for panel in manifest["panels"]:
        assert panel["visible_to_operator"] is True
        assert panel["runtime_truth_mutation_allowed"] is False
        assert panel["operator_mutation_enabled"] is False
        assert panel["live_web_execution_enabled"] is False
        assert panel["network_request_performed"] is False
        assert panel["body_read_performed"] is False
        assert panel["body_scraping_performed"] is False
        assert panel["response_mode"] == "quarantined_read_only_artifact"


def test_s49r5_evidence_review_panel_requires_manual_promotion():
    module = importlib.import_module("runtime_core.api.s49_governed_web_evidence_panels")
    manifest = module.build_evidence_review_panel_manifest()
    panel = manifest["panel"]

    assert manifest["status"] == "evidence_review_panel_manifest_ready"
    assert panel["state"] == "manual_review_required"
    assert panel["quarantine_required"] is True
    assert panel["manual_promotion_required"] is True
    assert panel["runtime_truth_write_allowed"] is False
    assert panel["auto_promotion_enabled"] is False
    assert panel["promotion_authority"] is False


def test_s49r8_plateau_report_ready():
    module = importlib.import_module("runtime_core.api.s49_governed_web_evidence_panels")
    report = module.build_s49r1_r8_plateau_report()

    assert report["status"] == "s49r1_r8_ready"
    assert report["ready"] is True
    assert report["verification"]["verification_ok"] is True
    assert report["automatic_updates_enabled"] is False
    assert report["autonomous_execution_enabled"] is False
    assert report["next_phase"] == "S50 modern cockpit consolidation and demo readiness"
