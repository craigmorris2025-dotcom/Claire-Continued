from __future__ import annotations

from typing import Dict, List


def get_frontend_presentation_schema() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S219-S225",
        "schema_id": "cockpit_frontend_presentation_schema",
        "backend_owns_truth": True,
        "frontend_owns_layout_only": True,
        "required_regions": [
            {
                "region_id": "top_command_bar",
                "render_order": 10,
                "sticky": True,
                "required_cards": ["command_surface", "governance_locks", "connection_state"],
            },
            {
                "region_id": "primary_runtime_panel",
                "render_order": 20,
                "sticky": False,
                "required_cards": ["current_state", "selected_route", "terminal_state", "next_action"],
            },
            {
                "region_id": "operations_strip",
                "render_order": 30,
                "sticky": False,
                "required_cards": ["bounded_jobs", "review_queue", "promotion_candidates", "export_ready", "update_proposals"],
            },
            {
                "region_id": "monitoring_column",
                "render_order": 40,
                "sticky": False,
                "required_cards": ["payload_health", "web_job_state", "queue_state", "warnings"],
            },
            {
                "region_id": "lifecycle_evidence_workspace",
                "render_order": 50,
                "sticky": False,
                "required_cards": ["lifecycle_status", "evidence_baskets", "source_lineage", "route_outputs"],
            },
            {
                "region_id": "diagnostics_drawer",
                "render_order": 90,
                "sticky": False,
                "required_cards": ["raw_payload", "endpoint_status", "contract_validation", "blocked_capabilities"],
            },
        ],
    }


def get_region_order() -> List[str]:
    regions = sorted(get_frontend_presentation_schema()["required_regions"], key=lambda item: item["render_order"])
    return [region["region_id"] for region in regions]
