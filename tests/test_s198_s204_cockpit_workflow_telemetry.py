from __future__ import annotations

from runtime_core.api.cockpit_workflow_telemetry import get_workflow_telemetry_contract


def test_s198_s204_workflow_telemetry_is_dashboard_ready_without_unsafe_execution():
    payload = get_workflow_telemetry_contract()

    assert payload["version"] == "v19.89.8-S198-S204"
    assert payload["dashboard_ready"] is True
    assert payload["unsafe_execution_enabled"] is False
    assert len(payload["signals"]) >= 7

    signals = {signal["signal_id"]: signal for signal in payload["signals"]}
    assert signals["governance_lock_state"]["dashboard_zone"] == "top_command_bar"
    assert signals["quarantine_pending"]["requires_operator_attention"] is True
    assert signals["mutation_proposal_waiting"]["execution_authority"] == "proposal_only"
