from __future__ import annotations

from claire.api.governed_fetch_evidence_pipeline_s303_s309 import (
    build_governed_fetch_evidence_pipeline_s303_s309,
    build_s303_operator_triggered_provider_probe,
    build_s304_controlled_fetch_executor,
    build_s305_quarantine_store,
    build_s306_evidence_capsule_builder,
    build_s307_source_lineage_trust_scoring,
    build_s308_internet_evidence_dashboard_card,
    build_s309_stop_gate,
)


def test_s303_operator_probe_is_manual_and_fail_closed():
    payload = build_s303_operator_triggered_provider_probe()
    assert payload["stage_version"] == "S303"
    assert payload["authorized_by_operator"] is True
    assert payload["live_execution_allowed"] is False


def test_s304_controlled_fetch_is_dry_run_contract_not_live_network():
    payload = build_s304_controlled_fetch_executor()
    request = payload["fetch_request"]
    assert request["source_permission_checked"] is True
    assert request["rate_limit_checked"] is True
    assert request["live_network_execution"] is False
    assert request["execution_mode"] == "dry_run_contract"


def test_s305_quarantine_store_blocks_runtime_truth_write():
    payload = build_s305_quarantine_store()
    record = payload["quarantine_record"]
    assert record["promotion_status"] == "unreviewed"
    assert record["runtime_truth_write"] == "blocked"
    assert record["source_lineage_captured"] is True


def test_s306_evidence_capsule_links_to_quarantine_lineage():
    payload = build_s306_evidence_capsule_builder()
    capsule = payload["evidence_capsule"]
    assert capsule["evidence_id"].startswith("evidence_")
    assert capsule["quarantine_id"].startswith("quarantine_")
    assert "sha256" in capsule["lineage"]


def test_s307_trust_scoring_requires_manual_review():
    payload = build_s307_source_lineage_trust_scoring()
    scoring = payload["scoring"]
    assert scoring["requires_manual_review"] is True
    assert scoring["policy_score"] >= 0


def test_s308_dashboard_card_exposes_evidence_state():
    payload = build_s308_internet_evidence_dashboard_card()
    card = payload["dashboard_card"]
    assert card["panel_key"] == "internet_evidence"
    assert card["review_needed_count"] == 1
    assert len(card["latest_evidence_capsules"]) == 1


def test_s309_stop_gate_keeps_live_execution_blocked(tmp_path):
    payload = build_s309_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S309"
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["live_network_execution_still_blocked"] is True
    assert payload["checks"]["runtime_truth_mutation_blocked"] is True
    assert "report_path" in payload


def test_s303_s309_pipeline_rollup_is_ready():
    payload = build_governed_fetch_evidence_pipeline_s303_s309()
    assert payload["stage_version"] == "S309"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
