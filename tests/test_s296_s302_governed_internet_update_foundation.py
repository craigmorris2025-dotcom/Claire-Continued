from __future__ import annotations

from runtime_core.api.governed_internet_update_foundation_s296_s302 import (
    authority_locks,
    build_governed_internet_update_foundation_s296_s302,
    build_s296_clean_plateau_checkpoint,
    build_s297_internet_update_authority_contract,
    build_s298_source_policy_registry,
    build_s299_provider_adapter_readiness_contract,
    build_s300_internet_update_job_model,
    build_s301_dashboard_internet_update_surface_contract,
    build_s302_stop_gate,
)


def test_s296_clean_plateau_checkpoint_locks_current_layout():
    payload = build_s296_clean_plateau_checkpoint()
    assert payload["stage_version"] == "S296"
    assert payload["ok"] is True
    assert "claire" in payload["active_layout"]
    assert "tests" in payload["active_layout"]
    assert payload["old_layout_assumptions_blocked"] is True


def test_s297_authority_blocks_autonomous_update_modes():
    payload = build_s297_internet_update_authority_contract()
    locks = payload["authority_locks"]
    assert payload["internet_access_mode"] == "governed_operator_controlled"
    assert locks["runtime_mutation_allowed"] is False
    assert locks["automatic_updates_allowed"] is False
    assert locks["autonomous_crawling_allowed"] is False
    assert "authorized_controlled_fetch" in payload["allowed_internet_actions"]


def test_s298_source_policy_registry_has_allow_and_block_paths():
    payload = build_s298_source_policy_registry()
    assert payload["stage_version"] == "S298"
    assert payload["approved_source_count"] >= 1
    assert payload["blocked_source_count"] >= 1


def test_s299_provider_readiness_is_fail_closed():
    payload = build_s299_provider_adapter_readiness_contract()
    assert payload["stage_version"] == "S299"
    assert payload["live_provider_count"] == 0
    assert payload["dry_run_provider_count"] >= 1
    assert all(provider["failure_mode"] == "fail_closed" for provider in payload["provider_registry"])


def test_s300_job_model_defines_review_lifecycle():
    payload = build_s300_internet_update_job_model()
    lifecycle = payload["job_model"]["status_lifecycle"]
    assert "quarantined" in lifecycle
    assert "evidence_ready" in lifecycle
    assert "review_required" in lifecycle
    assert "approved" in payload["job_model"]["terminal_statuses"]


def test_s301_dashboard_surface_contract_is_backend_truth_only():
    payload = build_s301_dashboard_internet_update_surface_contract()
    surface = payload["dashboard_surface"]
    assert surface["panel_count"] >= 3
    assert "internet_update_readiness" in surface["panels"]
    assert surface["dashboard_truth_policy"] == "backend_payload_only"


def test_s302_stop_gate_allows_forward_motion_without_enabling_mutation(tmp_path):
    payload = build_s302_stop_gate(report_dir=tmp_path)
    assert payload["stage_version"] == "S302"
    assert payload["ok"] is True
    assert payload["forward_motion_allowed"] is True
    assert payload["checks"]["runtime_truth_mutation_blocked"] is True
    assert payload["checks"]["automatic_updates_blocked"] is True
    assert payload["checks"]["autonomous_crawling_blocked"] is True
    assert "report_path" in payload


def test_s296_s302_foundation_rollup_is_ready():
    payload = build_governed_internet_update_foundation_s296_s302()
    assert payload["stage_version"] == "S302"
    assert payload["stop_gate"]["forward_motion_allowed"] is True
    assert authority_locks()["failure_mode"] == "fail_closed"
