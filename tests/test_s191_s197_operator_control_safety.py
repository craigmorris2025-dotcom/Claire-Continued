from __future__ import annotations

from runtime_core.api.cockpit_monitoring_snapshot import get_monitoring_snapshot
from runtime_core.api.cockpit_operator_control_readiness import get_operator_control_readiness


def test_s191_s197_operator_controls_are_contract_ready_without_unsafe_authority():
    payload = get_operator_control_readiness()

    assert payload["stage_range"] == "S191-S197"
    assert payload["unsafe_authority_enabled"] is False
    assert len(payload["controls"]) >= 7

    controls = {control["control_id"]: control for control in payload["controls"]}
    assert controls["request_mutation_proposal"]["execution_authority"] == "proposal_only"
    assert controls["approve_promotion_candidate"]["execution_authority"] == "manual_promotion_only"
    assert controls["inspect_source_lineage"]["execution_authority"] == "read_only"

    for blocked in [
        "runtime_truth_write",
        "runtime_mutation",
        "automatic_updates",
        "autonomous_execution",
        "continuous_crawling",
    ]:
        assert blocked in payload["blocked_capabilities"]


def test_s191_s197_monitoring_snapshot_reports_active_governance_locks():
    payload = get_monitoring_snapshot()

    assert payload["monitoring_backend"]["governance_locks"] == "active"
    assert payload["operator_cockpit"]["visual_controls"] == "contract_ready"
    assert payload["authority"]["backend_owns_truth"] is True
    assert payload["authority"]["cockpit_presentation_only"] is True
    assert payload["authority"]["runtime_mutation_blocked"] is True
    assert payload["authority"]["automatic_updates_blocked"] is True
    assert payload["authority"]["autonomous_execution_blocked"] is True
