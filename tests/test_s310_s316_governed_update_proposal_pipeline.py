from __future__ import annotations

from claire.api.governed_update_proposal_pipeline_s310_s316 import (
    build_governed_update_proposal_pipeline_s310_s316,
    build_s310_update_candidate_detector,
    build_s311_update_proposal_builder,
    build_s312_review_queue_integration,
    build_s313_approved_update_export_package,
    build_s314_dashboard_update_proposal_surface,
    build_s315_end_to_end_governed_update_run,
    build_s316_stop_gate,
)


def test_s310_update_candidate_requires_review():
    payload = build_s310_update_candidate_detector()
    candidate = payload["update_candidate"]
    assert payload["stage_version"] == "S310"
    assert candidate["requires_review"] is True
    assert candidate["candidate_type"] == "research_note_update"


def test_s311_update_proposal_is_proposal_only():
    payload = build_s311_update_proposal_builder()
    proposal = payload["update_proposal"]
    assert payload["stage_version"] == "S311"
    assert proposal["approval_required"] is True
    assert proposal["self_apply_allowed"] is False
    assert proposal["runtime_truth_write_allowed"] is False


def test_s312_review_queue_integrates_manual_gate():
    payload = build_s312_review_queue_integration()
    item = payload["review_item"]
    assert payload["stage_version"] == "S312"
    assert item["status"] == "review_required"
    assert item["manual_promotion_gate"] is True


def test_s313_export_package_writes_optional_export_files(tmp_path):
    payload = build_s313_approved_update_export_package(export_dir=tmp_path)
    package = payload["export_package"]
    assert payload["stage_version"] == "S313"
    assert package["runtime_truth_modified"] is False
    assert "export_paths" in payload


def test_s314_dashboard_update_surface_exposes_review_state():
    payload = build_s314_dashboard_update_proposal_surface()
    surface = payload["dashboard_surface"]
    assert payload["stage_version"] == "S314"
    assert surface["panel_key"] == "internet_update_proposals"
    assert surface["runtime_mutation_status"] == "blocked"
    assert len(surface["internet_update_proposals"]) == 1


def test_s315_end_to_end_run_never_modifies_runtime_truth(tmp_path):
    payload = build_s315_end_to_end_governed_update_run(export_dir=tmp_path)
    run = payload["run"]
    assert payload["stage_version"] == "S315"
    assert "dashboard_payload_ready" in run["audit_trail"]
    assert run["runtime_truth_modified"] is False


def test_s316_stop_gate_declares_governed_update_readiness(tmp_path):
    payload = build_s316_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S316"
    assert payload["forward_motion_allowed"] is True
    assert payload["readiness_state"] == "governed_internet_update_ready"
    assert payload["checks"]["runtime_mutation_blocked"] is True
    assert payload["checks"]["automatic_updates_blocked"] is True
    assert payload["checks"]["autonomous_crawling_blocked"] is True
    assert payload["checks"]["runtime_truth_not_modified"] is True
    assert "report_path" in payload


def test_s310_s316_rollup_is_ready():
    payload = build_governed_update_proposal_pipeline_s310_s316()
    assert payload["stage_version"] == "S316"
    assert payload["stop_gate"]["readiness_state"] == "governed_internet_update_ready"
