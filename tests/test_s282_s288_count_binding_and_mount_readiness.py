from __future__ import annotations

from claire.api.cockpit_count_binding_metadata import get_cockpit_count_binding_metadata
from claire.api.operator_workflow_mount_readiness import get_operator_workflow_mount_readiness


def test_s282_s288_count_binding_metadata_is_dashboard_ready():
    payload = get_cockpit_count_binding_metadata()
    bindings = {item["card_id"]: item for item in payload["bindings"]}

    assert payload["stage_version"] == "S288"
    assert payload["ok"] is True
    assert payload["safe_to_bind_frontend_counts"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert "review_queue" in bindings
    assert "bounded_web_jobs" in bindings
    assert "exports" in bindings
    assert "audit_trail" in bindings


def test_s282_s288_mount_readiness_preserves_locks():
    payload = get_operator_workflow_mount_readiness()

    assert payload["status"] == "operator_workflow_mount_readiness_ready"
    assert payload["ok"] is True
    assert payload["ready_to_mount_fastapi_routes"] is True
    assert payload["ready_to_bind_dashboard_counts"] is True
    assert payload["post_handlers_proposal_only"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["runtime_mutation_enabled"] is False
    assert payload["automatic_updates_enabled"] is False

    remaining = set(payload["remaining_before_daily_use"])
    assert "actual FastAPI router registration" in remaining
    assert "dashboard JS count fetch implementation" in remaining
    assert "export artifact writer" in remaining
