from __future__ import annotations

from typing import Dict

from runtime_core.api.operator_workflow_route_handlers import get_mount_ready_operator_workflow_handlers
from runtime_core.api.cockpit_count_binding_metadata import get_cockpit_count_binding_metadata


def get_operator_workflow_mount_readiness() -> Dict[str, object]:
    handlers = get_mount_ready_operator_workflow_handlers()
    binding = get_cockpit_count_binding_metadata()

    return {
        "version": "v19.89.8-S282-S288",
        "status": "operator_workflow_mount_readiness_ready",
        "ok": True,
        "handler_count": handlers["handler_count"],
        "binding_count": binding["binding_count"],
        "ready_to_mount_fastapi_routes": True,
        "ready_to_bind_dashboard_counts": True,
        "post_handlers_proposal_only": True,
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "remaining_before_daily_use": [
            "actual FastAPI router registration",
            "dashboard JS count fetch implementation",
            "operator review decision UI state",
            "bounded job request UI state",
            "export artifact writer",
        ],
    }
