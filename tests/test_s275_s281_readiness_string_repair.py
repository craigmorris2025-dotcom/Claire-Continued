from __future__ import annotations

from claire.api.operator_workflow_route_readiness import get_operator_workflow_route_readiness


def test_s275_s281_readiness_uses_exact_monitoring_refresh_string():
    payload = get_operator_workflow_route_readiness()
    remaining = set(payload["remaining_before_daily_use"])

    assert "mount route handlers in FastAPI app" in remaining
    assert "bind dashboard count cards to shell JS" in remaining
    assert "monitoring panel live refresh" in remaining
    assert "add monitoring panel live refresh" not in remaining
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["automatic_updates_enabled"] is False
