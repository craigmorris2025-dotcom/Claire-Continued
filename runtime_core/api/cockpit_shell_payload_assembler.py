from __future__ import annotations

from typing import Dict, List


def get_cockpit_shell_payload() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S226-S232",
        "payload_id": "single_cockpit_shell_payload",
        "backend_owns_truth": True,
        "frontend_owns_presentation": True,
        "render_mode": "single_consolidated_cockpit",
        "regions": [
            {
                "region_id": "top_command_bar",
                "title": "Command",
                "layout_role": "persistent_header",
                "cards": ["command_surface", "governance_locks", "connection_state"],
            },
            {
                "region_id": "primary_runtime_panel",
                "title": "Runtime",
                "layout_role": "primary_status",
                "cards": ["current_state", "selected_route", "terminal_state", "confidence", "next_action"],
            },
            {
                "region_id": "operations_strip",
                "title": "Operator Controls",
                "layout_role": "action_strip",
                "cards": ["bounded_jobs", "review_queue", "promotion_candidates", "export_ready", "update_proposals"],
            },
            {
                "region_id": "monitoring_column",
                "title": "Monitoring",
                "layout_role": "side_status",
                "cards": ["payload_health", "web_job_state", "queue_state", "warnings"],
            },
            {
                "region_id": "lifecycle_evidence_workspace",
                "title": "Lifecycle + Evidence",
                "layout_role": "main_workspace",
                "cards": ["lifecycle_status", "evidence_baskets", "source_lineage", "route_outputs"],
            },
            {
                "region_id": "diagnostics_drawer",
                "title": "Diagnostics",
                "layout_role": "hidden_drawer",
                "cards": ["raw_payload", "endpoint_status", "contract_validation", "blocked_capabilities"],
            },
        ],
        "unsafe_authority": {
            "runtime_truth_write": False,
            "runtime_mutation": False,
            "automatic_updates": False,
            "autonomous_execution": False,
            "continuous_crawling": False,
        },
    }


def get_shell_region_ids() -> List[str]:
    return [region["region_id"] for region in get_cockpit_shell_payload()["regions"]]
