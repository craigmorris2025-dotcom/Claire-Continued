from __future__ import annotations

from typing import Dict, List


def get_card_region_binding_contract() -> Dict[str, object]:
    bindings: List[Dict[str, object]] = [
        {"card_id": "command_surface", "region_id": "top_command_bar", "required": True},
        {"card_id": "governance_locks", "region_id": "top_command_bar", "required": True},
        {"card_id": "connection_state", "region_id": "top_command_bar", "required": True},
        {"card_id": "current_state", "region_id": "primary_runtime_panel", "required": True},
        {"card_id": "selected_route", "region_id": "primary_runtime_panel", "required": True},
        {"card_id": "terminal_state", "region_id": "primary_runtime_panel", "required": True},
        {"card_id": "next_action", "region_id": "primary_runtime_panel", "required": True},
        {"card_id": "bounded_jobs", "region_id": "operations_strip", "required": True},
        {"card_id": "review_queue", "region_id": "operations_strip", "required": True},
        {"card_id": "promotion_candidates", "region_id": "operations_strip", "required": True},
        {"card_id": "export_ready", "region_id": "operations_strip", "required": True},
        {"card_id": "update_proposals", "region_id": "operations_strip", "required": True},
        {"card_id": "payload_health", "region_id": "monitoring_column", "required": True},
        {"card_id": "web_job_state", "region_id": "monitoring_column", "required": True},
        {"card_id": "queue_state", "region_id": "monitoring_column", "required": True},
        {"card_id": "warnings", "region_id": "monitoring_column", "required": True},
        {"card_id": "raw_payload", "region_id": "diagnostics_drawer", "required": False},
        {"card_id": "endpoint_status", "region_id": "diagnostics_drawer", "required": False},
        {"card_id": "contract_validation", "region_id": "diagnostics_drawer", "required": False},
    ]
    return {
        "version": "v19.89.8-S233-S239",
        "bindings": bindings,
        "frontend_can_reassign_required_cards": False,
    }
