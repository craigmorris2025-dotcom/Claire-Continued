from __future__ import annotations

from typing import Dict, List


def get_consolidated_cockpit_state() -> Dict[str, object]:
    zones: List[Dict[str, object]] = [
        {
            "zone_id": "top_command_bar",
            "purpose": "Permanent command/search surface with governance lock visibility.",
            "must_remain_visible": True,
            "backend_owned": True,
        },
        {
            "zone_id": "primary_runtime_panel",
            "purpose": "Current run, selected route, terminal state, confidence, next operator action.",
            "must_remain_visible": True,
            "backend_owned": True,
        },
        {
            "zone_id": "operations_strip",
            "purpose": "State-aware buttons for bounded jobs, review, export, lineage, approvals, and proposals.",
            "must_remain_visible": True,
            "backend_owned": True,
        },
        {
            "zone_id": "monitoring_column",
            "purpose": "Health, payload, queues, web jobs, and governance warnings.",
            "must_remain_visible": True,
            "backend_owned": True,
        },
        {
            "zone_id": "lifecycle_evidence_workspace",
            "purpose": "30-stage state, evidence baskets, lineage, candidates, and route outputs.",
            "must_remain_visible": True,
            "backend_owned": True,
        },
        {
            "zone_id": "diagnostics_drawer",
            "purpose": "Raw payload, endpoint status, route owner map, contract validation, debug surfaces.",
            "must_remain_visible": False,
            "backend_owned": True,
        },
    ]
    return {
        "version": "v19.89.8-S198-S204",
        "layout_contract": "precision_consolidated_cockpit",
        "zones": zones,
        "rule": "Dashboard may present and organize state, but backend owns all truth and action eligibility.",
        "unsafe_authority": {
            "runtime_truth_write": False,
            "runtime_mutation": False,
            "automatic_updates": False,
            "autonomous_execution": False,
            "continuous_crawling": False,
        },
    }
