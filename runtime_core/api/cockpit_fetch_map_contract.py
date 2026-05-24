from __future__ import annotations

from typing import Dict, List


def get_cockpit_fetch_map_contract() -> Dict[str, object]:
    endpoints: List[Dict[str, object]] = [
        {"endpoint_id": "canonical_payload", "path": "/dashboard/payload", "required": True, "authority": "read_only"},
        {"endpoint_id": "payload_status", "path": "/dashboard/payload/status", "required": True, "authority": "read_only"},
        {"endpoint_id": "health", "path": "/health", "required": True, "authority": "read_only"},
        {"endpoint_id": "docs", "path": "/docs", "required": False, "authority": "read_only"},
        {"endpoint_id": "search_provider_status", "path": "/api/dashboard/search/provider/status", "required": False, "authority": "read_only"},
        {"endpoint_id": "governed_live_search", "path": "/api/dashboard/search/live", "required": False, "authority": "operator_requested"},
    ]
    return {
        "version": "v19.89.8-S233-S239",
        "fetch_map_id": "safe_cockpit_fetch_map",
        "endpoints": endpoints,
        "frontend_may_invent_endpoints": False,
        "unsafe_methods_allowed": False,
        "allowed_methods": ["GET"],
    }
