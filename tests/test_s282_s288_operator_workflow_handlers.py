from __future__ import annotations

from claire.api.operator_workflow_route_handlers import (
    get_mount_ready_operator_workflow_handlers,
    read_bounded_jobs_handler,
    read_review_queue_handler,
    read_workflow_counts_handler,
    record_bounded_job_request_proposal_handler,
    record_review_decision_proposal_handler,
)


def test_s282_s288_handlers_are_mount_ready_and_safe():
    counts = read_workflow_counts_handler()
    review = read_review_queue_handler()
    bounded = read_bounded_jobs_handler()
    decision = record_review_decision_proposal_handler(review_id="test-review", decision="approved")
    job = record_bounded_job_request_proposal_handler(query="test query")
    ready = get_mount_ready_operator_workflow_handlers()

    assert counts["stage_version"] == "S282"
    assert counts["ok"] is True
    assert review["stage_version"] == "S283"
    assert bounded["stage_version"] == "S284"
    assert decision["stage_version"] == "S285"
    assert decision["proposal_only"] is True
    assert job["stage_version"] == "S286"
    assert job["proposal_only"] is True
    assert ready["stage_version"] == "S288"
    assert ready["handler_count"] >= 6

    for payload in [counts, review, bounded, decision, job, ready]:
        assert payload["runtime_truth_write_enabled"] is False
        assert payload["runtime_mutation_enabled"] is False
        assert payload["automatic_updates_enabled"] is False
