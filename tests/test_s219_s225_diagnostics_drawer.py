from __future__ import annotations

from runtime_core.api.cockpit_diagnostics_drawer_payload import get_diagnostics_drawer_payload


def test_s219_s225_diagnostics_drawer_is_hidden_read_only_and_non_mutating():
    payload = get_diagnostics_drawer_payload()

    assert payload["drawer_default_open"] is False
    assert payload["allows_runtime_mutation"] is False

    diagnostics = {item["item_id"]: item for item in payload["diagnostics"]}
    for required in ["raw_payload", "endpoint_status", "contract_validation", "blocked_capabilities"]:
        assert required in diagnostics
        assert diagnostics[required]["default_visible"] is False
        assert diagnostics[required]["authority"] == "read_only"
