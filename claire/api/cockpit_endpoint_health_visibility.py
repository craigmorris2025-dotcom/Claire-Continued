from __future__ import annotations

from typing import Dict, List


def get_endpoint_health_visibility_contract() -> Dict[str, object]:
    checks: List[Dict[str, object]] = [
        {"endpoint_id": "canonical_payload", "path": "/dashboard/payload", "display_region": "monitoring_column", "critical": True},
        {"endpoint_id": "payload_status", "path": "/dashboard/payload/status", "display_region": "monitoring_column", "critical": True},
        {"endpoint_id": "health", "path": "/health", "display_region": "monitoring_column", "critical": True},
        {"endpoint_id": "docs", "path": "/docs", "display_region": "diagnostics_drawer", "critical": False},
        {"endpoint_id": "provider_status", "path": "/api/dashboard/search/provider/status", "display_region": "diagnostics_drawer", "critical": False},
    ]
    return {
        "version": "v19.89.8-S233-S239",
        "checks": checks,
        "show_critical_failures_in_main_cockpit": True,
        "hide_noncritical_details_in_diagnostics": True,
    }
