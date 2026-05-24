from __future__ import annotations

from runtime_core.api.operator_workflow_dashboard_count_payload import build_dashboard_live_count_payload
from runtime_core.api.operator_workflow_route_readiness import get_operator_workflow_route_readiness


def test_s275_s281_dashboard_live_count_payload_is_ready_and_non_mutating():
    payload = build_dashboard_live_count_payload()

    assert payload["payload_id"] == "operator_workflow_dashboard_live_counts"
    assert payload["dashboard_ready"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["runtime_mutation_enabled"] is False

    cards = payload["cards"]
    assert "review_queue" in cards
    assert "bounded_web_jobs" in cards
    assert "exports" in cards
    assert "audit_trail" in cards
    assert isinstance(cards["review_queue"]["count"], int)


def test_s275_s281_route_readiness_marks_frontend_count_binding_ready():
    payload = get_operator_workflow_route_readiness()

    assert payload["workflow_route_contracts_ready"] is True
    assert payload["dashboard_count_payload_ready"] is True
    assert payload["safe_to_bind_frontend_counts"] is True
    assert payload["post_routes_proposal_only"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["automatic_updates_enabled"] is False

    remaining = set(payload["remaining_before_daily_use"])
    assert "mount route handlers in FastAPI app" in remaining
    assert "bind dashboard count cards to shell JS" in remaining
    assert "monitoring panel live refresh" in remaining
