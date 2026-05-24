from __future__ import annotations

from pathlib import Path

from runtime_core.api.governed_dashboard_upgrade_s177_s183 import (
    build_dashboard_core_control_map,
    build_safe_web_update_readiness_contract,
    build_bounded_crawl_job_contract,
    build_runtime_mutation_proposal_contract,
    build_monitoring_and_hardening_readiness,
    build_future_integration_boundary,
    build_s177_s183_stop_gate,
)

def test_s177_dashboard_core_control_map_ready():
    result = build_dashboard_core_control_map()
    assert result["stage_version"] == "S177"
    assert result["ok"] is True
    assert result["visual_rewire_performed"] is False
    assert result["runtime_truth_write"] == "blocked"

def test_s178_safe_web_update_contract_is_proposal_only():
    result = build_safe_web_update_readiness_contract()
    assert result["stage_version"] == "S178"
    assert result["automatic_web_updating_mode"] == "proposal_only"
    assert result["execution_enabled_now"] is False
    assert "automatic_runtime_truth_write" in result["blocked_flow"]

def test_s179_bounded_crawl_contract_blocks_continuous_crawling():
    result = build_bounded_crawl_job_contract()
    assert result["stage_version"] == "S179"
    assert result["autonomous_crawling_enabled"] is False
    assert result["continuous_crawling"] == "blocked"
    assert result["requirements"]["quarantine_required"] is True

def test_s180_runtime_mutation_is_proposal_only():
    result = build_runtime_mutation_proposal_contract()
    assert result["stage_version"] == "S180"
    assert result["runtime_mutation_enabled"] is False
    assert result["allowed"]["generate_update_proposal"] is True
    assert result["blocked"]["self_apply_patch"] is True

def test_s181_monitoring_and_hardening_readiness():
    result = build_monitoring_and_hardening_readiness()
    assert result["stage_version"] == "S181"
    assert result["enterprise_controls"]["rollback_required"] is True
    assert result["enterprise_controls"]["audit_required"] is True

def test_s182_future_integration_boundaries():
    result = build_future_integration_boundary()
    assert result["stage_version"] == "S182"
    assert result["brokerage_integrations"]["trading_execution_enabled"] is False
    assert result["longitudinal_memory_loops"]["hidden_self_modification"] is False
    assert result["thirty_stage_lifecycle_from_live_evidence"]["unapproved_live_evidence_allowed"] is False

def test_s183_stop_gate_passes(tmp_path: Path):
    report = build_s177_s183_stop_gate(report_dir=tmp_path / "reports")
    assert report["stage_version"] == "S183"
    assert report["ok"] is True
    assert report["forward_motion_allowed"] is True
    assert report["next_allowed_phase"] == "S184-S190 visual cockpit controls and monitoring backend"
    assert Path(report["report_path"]).exists()
