from __future__ import annotations

from runtime_core.api.operator_workflow_dashboard_counts import get_operator_dashboard_counts
from runtime_core.api.operator_workflow_storage_readiness import get_operator_workflow_storage_readiness


def test_s268_s274_dashboard_counts_are_available_without_runtime_truth_write():
    payload = get_operator_dashboard_counts()

    assert payload["version"] == "v19.89.8-S268-S274"
    assert payload["dashboard_ready"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert isinstance(payload["review_queue_count"], int)
    assert isinstance(payload["bounded_web_job_count"], int)
    assert isinstance(payload["export_count"], int)
    assert isinstance(payload["audit_event_count"], int)


def test_s268_s274_storage_readiness_marks_next_routes_remaining():
    payload = get_operator_workflow_storage_readiness()

    assert payload["local_storage_adapter"] == "ready"
    assert payload["dashboard_counts"] == "ready"
    assert payload["review_queue_persistence"] == "ready"
    assert payload["bounded_job_persistence"] == "ready"
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["runtime_mutation_enabled"] is False

    remaining = set(payload["remaining_before_daily_use"])
    assert "safe API routes for workflow records" in remaining
    assert "frontend queue count rendering" in remaining
    assert "bounded job execution adapter" in remaining
