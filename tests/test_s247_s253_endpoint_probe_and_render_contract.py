from __future__ import annotations

from runtime_core.api.cockpit_endpoint_probe_display_contract import get_endpoint_probe_display_contract
from runtime_core.api.cockpit_shell_state_render_contract import get_shell_state_render_contract


def test_s247_s253_endpoint_probe_display_contract_is_get_only_and_fail_closed():
    payload = get_endpoint_probe_display_contract()
    probes = {probe["probe_id"]: probe for probe in payload["probes"]}

    assert payload["allowed_methods"] == ["GET"]
    assert payload["probe_execution_authority"] == "read_only"
    assert payload["fail_closed_on_critical_probe_failure"] is True
    assert probes["backend_health"]["critical"] is True
    assert probes["canonical_payload"]["endpoint"] == "/dashboard/payload"
    assert probes["provider_status"]["critical"] is False


def test_s247_s253_shell_state_render_contract_prevents_blank_main_result_and_payload_mutation():
    payload = get_shell_state_render_contract()
    rules = {rule["card_id"]: rule for rule in payload["render_rules"]}

    assert payload["blank_main_result_allowed"] is False
    assert payload["frontend_may_mutate_payload"] is False
    assert payload["unknown_fields_allowed"] is True
    assert rules["current_state"]["fallback"] == "payload available"
    assert rules["next_action"]["fallback"] == "review cockpit state"
    assert rules["confidence"]["fallback"] == "pending"
