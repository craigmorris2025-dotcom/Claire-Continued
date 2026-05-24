from __future__ import annotations

from typing import Dict, List


def get_render_safety_contract() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S226-S232",
        "render_safety": {
            "blank_main_result_allowed": False,
            "missing_payload_fallback_required": True,
            "blocked_action_explanation_required": True,
            "diagnostics_hidden_by_default": True,
            "unsafe_button_disable_required": True,
            "backend_state_required_for_enabled_buttons": True,
        },
        "fallback_states": [
            {
                "state_id": "waiting_for_payload",
                "message": "Waiting for backend payload.",
                "allows_operator_action": False,
            },
            {
                "state_id": "payload_unavailable",
                "message": "Backend payload unavailable. Check health and endpoint status.",
                "allows_operator_action": False,
            },
            {
                "state_id": "insufficient_data",
                "message": "Insufficient data for a useful output. Review evidence or request a bounded job.",
                "allows_operator_action": True,
            },
            {
                "state_id": "blocked_by_governance",
                "message": "Requested action is blocked by governance locks.",
                "allows_operator_action": False,
            },
        ],
    }
