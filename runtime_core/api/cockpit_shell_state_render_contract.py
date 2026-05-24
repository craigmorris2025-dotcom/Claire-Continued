from __future__ import annotations

from typing import Dict, List


def get_shell_state_render_contract() -> Dict[str, object]:
    render_rules: List[Dict[str, object]] = [
        {
            "field": "status",
            "card_id": "current_state",
            "fallback": "payload available",
            "required": False,
        },
        {
            "field": "selected_route",
            "card_id": "selected_route",
            "fallback": "not selected",
            "required": False,
        },
        {
            "field": "terminal_state",
            "card_id": "terminal_state",
            "fallback": "not reached",
            "required": False,
        },
        {
            "field": "next_action",
            "card_id": "next_action",
            "fallback": "review cockpit state",
            "required": False,
        },
        {
            "field": "confidence",
            "card_id": "confidence",
            "fallback": "pending",
            "required": False,
        },
    ]
    return {
        "version": "v19.89.8-S247-S253",
        "render_rules": render_rules,
        "blank_main_result_allowed": False,
        "frontend_may_mutate_payload": False,
        "unknown_fields_allowed": True,
    }
