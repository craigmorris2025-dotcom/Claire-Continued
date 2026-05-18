from __future__ import annotations

from claire.api.cockpit_single_shell_readiness import get_single_shell_readiness


def test_s226_s232_single_shell_readiness_marks_payload_ready_but_visual_work_remaining():
    payload = get_single_shell_readiness()

    assert payload["single_shell_ready"] is True
    assert payload["frontend_payload_ready"] is True
    assert payload["layout_consolidation_ready"] is True
    assert payload["operator_controls_ready_for_visual_binding"] is True
    assert payload["diagnostics_ready_for_hidden_drawer"] is True
    assert payload["authority_locks_preserved"] is True

    remaining = set(payload["remaining_dashboard_work"])
    assert "visual implementation" in remaining
    assert "JS fetch binding" in remaining
    assert "button event binding to safe backend routes" in remaining
    assert "responsive layout polish" in remaining
