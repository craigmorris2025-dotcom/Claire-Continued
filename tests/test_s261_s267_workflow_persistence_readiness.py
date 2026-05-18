from __future__ import annotations

from claire.api.workflow_persistence_readiness import get_workflow_persistence_readiness


def test_s261_s267_workflow_persistence_ready_for_storage_but_not_daily_use_complete():
    payload = get_workflow_persistence_readiness()

    assert payload["review_queue_record"] == "contract_ready"
    assert payload["bounded_web_job_record"] == "contract_ready"
    assert payload["export_artifact_record"] == "contract_ready"
    assert payload["operator_audit_trail"] == "contract_ready"
    assert payload["ready_for_storage_adapter"] is True
    assert payload["ready_for_dashboard_queue_counts"] is True
    assert payload["runtime_mutation_enabled"] is False
    assert payload["automatic_updates_enabled"] is False
    assert payload["continuous_crawling_enabled"] is False

    remaining = set(payload["remaining_before_daily_use"])
    assert "storage adapter implementation" in remaining
    assert "actual queue read/write routes" in remaining
    assert "dashboard live counts" in remaining
