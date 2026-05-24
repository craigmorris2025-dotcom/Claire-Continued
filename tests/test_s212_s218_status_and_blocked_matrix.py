from __future__ import annotations

from runtime_core.api.governed_blocked_capability_matrix import get_blocked_capability_matrix
from runtime_core.api.governed_cockpit_status_rollup import get_cockpit_status_rollup


def test_s212_s218_status_rollup_reports_governed_operational_readiness():
    payload = get_cockpit_status_rollup()

    assert payload["overall_state"] == "governed_operational_ready"
    assert payload["internet_connectivity_state"] == "operator_controlled_bounded_ready"
    assert payload["dashboard_state"] == "payload_consumable"
    assert payload["update_state"] == "proposal_only"
    assert payload["mutation_state"] == "blocked"
    assert payload["autonomy_state"] == "blocked"
    assert payload["safe_to_continue_builds"] is True


def test_s212_s218_blocked_capability_matrix_keeps_all_unsafe_capabilities_blocked():
    payload = get_blocked_capability_matrix()
    blocked = {item["capability"]: item for item in payload["blocked"]}

    assert payload["all_unsafe_capabilities_blocked"] is True
    assert blocked["automatic_updates"]["blocked"] is True
    assert blocked["automatic_updates"]["allowed_substitute"] == "update_proposal_flow"
    assert blocked["runtime_mutation"]["allowed_substitute"] == "mutation_proposal_review"
    assert blocked["continuous_crawling"]["allowed_substitute"] == "bounded_operator_approved_web_job"
    assert blocked["runtime_truth_write"]["allowed_substitute"] == "promotion_candidate_record"
