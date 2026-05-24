from __future__ import annotations

from typing import Dict, List


def get_action_card_ordering() -> Dict[str, object]:
    cards: List[Dict[str, object]] = [
        {"card_id": "governance_locks", "priority": 1, "region_id": "top_command_bar", "always_visible": True},
        {"card_id": "connection_state", "priority": 2, "region_id": "top_command_bar", "always_visible": True},
        {"card_id": "next_action", "priority": 3, "region_id": "primary_runtime_panel", "always_visible": True},
        {"card_id": "bounded_jobs", "priority": 4, "region_id": "operations_strip", "always_visible": True},
        {"card_id": "review_queue", "priority": 5, "region_id": "operations_strip", "always_visible": True},
        {"card_id": "promotion_candidates", "priority": 6, "region_id": "operations_strip", "always_visible": True},
        {"card_id": "export_ready", "priority": 7, "region_id": "operations_strip", "always_visible": True},
        {"card_id": "update_proposals", "priority": 8, "region_id": "operations_strip", "always_visible": True},
        {"card_id": "warnings", "priority": 9, "region_id": "monitoring_column", "always_visible": True},
        {"card_id": "blocked_capabilities", "priority": 90, "region_id": "diagnostics_drawer", "always_visible": False},
    ]
    return {
        "version": "v19.89.8-S219-S225",
        "cards": cards,
        "rule": "Governance, current state, and next operator action must appear before lower-priority diagnostic surfaces.",
    }
