from __future__ import annotations

from runtime_core.api.cockpit_shell_payload_assembler import get_cockpit_shell_payload, get_shell_region_ids


def test_s226_s232_shell_payload_has_single_consolidated_cockpit_regions():
    payload = get_cockpit_shell_payload()

    assert payload["payload_id"] == "single_cockpit_shell_payload"
    assert payload["render_mode"] == "single_consolidated_cockpit"
    assert payload["backend_owns_truth"] is True
    assert payload["frontend_owns_presentation"] is True

    assert get_shell_region_ids() == [
        "top_command_bar",
        "primary_runtime_panel",
        "operations_strip",
        "monitoring_column",
        "lifecycle_evidence_workspace",
        "diagnostics_drawer",
    ]


def test_s226_s232_shell_payload_preserves_unsafe_authority_locks():
    locks = get_cockpit_shell_payload()["unsafe_authority"]

    assert locks["runtime_truth_write"] is False
    assert locks["runtime_mutation"] is False
    assert locks["automatic_updates"] is False
    assert locks["autonomous_execution"] is False
    assert locks["continuous_crawling"] is False
