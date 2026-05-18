from __future__ import annotations

from typing import Dict, List


def get_endpoint_probe_display_contract() -> Dict[str, object]:
    probes: List[Dict[str, object]] = [
        {
            "probe_id": "backend_health",
            "endpoint": "/health",
            "method": "GET",
            "display_card": "payload_health",
            "critical": True,
            "failure_message": "Backend health unavailable.",
        },
        {
            "probe_id": "canonical_payload",
            "endpoint": "/dashboard/payload",
            "method": "GET",
            "display_card": "current_state",
            "critical": True,
            "failure_message": "Canonical payload unavailable.",
        },
        {
            "probe_id": "payload_status",
            "endpoint": "/dashboard/payload/status",
            "method": "GET",
            "display_card": "connection_state",
            "critical": True,
            "failure_message": "Payload status unavailable.",
        },
        {
            "probe_id": "provider_status",
            "endpoint": "/api/dashboard/search/provider/status",
            "method": "GET",
            "display_card": "web_job_state",
            "critical": False,
            "failure_message": "Provider status unavailable.",
        },
    ]
    return {
        "version": "v19.89.8-S247-S253",
        "probes": probes,
        "allowed_methods": ["GET"],
        "probe_execution_authority": "read_only",
        "fail_closed_on_critical_probe_failure": True,
    }
