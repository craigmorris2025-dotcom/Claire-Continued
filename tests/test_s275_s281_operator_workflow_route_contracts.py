from __future__ import annotations

from claire.api.operator_workflow_route_contracts import get_operator_workflow_route_contracts


def test_s275_s281_operator_workflow_routes_are_safe_contracts():
    payload = get_operator_workflow_route_contracts()
    routes = {route["route_id"]: route for route in payload["route_contracts"]}

    assert payload["version"] == "v19.89.8-S275-S281"
    assert payload["route_count"] >= 7
    assert payload["post_routes_are_proposal_only"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["runtime_mutation_enabled"] is False
    assert payload["automatic_updates_enabled"] is False
    assert payload["autonomous_execution_enabled"] is False

    assert routes["workflow_counts"]["method"] == "GET"
    assert routes["workflow_counts"]["authority"] == "read_only"
    assert routes["review_decision_proposal"]["method"] == "POST"
    assert routes["review_decision_proposal"]["authority"] == "operator_review_proposal_only"
    assert routes["bounded_job_request_proposal"]["writes_runtime_truth"] is False
