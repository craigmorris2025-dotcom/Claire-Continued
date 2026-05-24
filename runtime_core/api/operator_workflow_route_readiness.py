from __future__ import annotations

from typing import Dict

from runtime_core.api.operator_workflow_route_contracts import get_operator_workflow_route_contracts
from runtime_core.api.operator_workflow_dashboard_count_payload import build_dashboard_live_count_payload


def get_operator_workflow_route_readiness() -> Dict[str, object]:
    contracts = get_operator_workflow_route_contracts()
    counts = build_dashboard_live_count_payload()

    return {
        "version": "v19.89.8-S275-S281",
        "workflow_route_contracts_ready": True,
        "dashboard_count_payload_ready": True,
        "route_count": contracts["route_count"],
        "count_cards": list(counts["cards"].keys()),
        "safe_to_bind_frontend_counts": True,
        "post_routes_proposal_only": contracts["post_routes_are_proposal_only"],
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "remaining_before_daily_use": [
            "mount route handlers in FastAPI app",
            "bind dashboard count cards to shell JS",
            "add operator review decision persistence semantics",
            "add bounded job request persistence semantics",
            "add export artifact writer",
            "monitoring panel live refresh",
        ],
    }
