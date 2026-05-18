from __future__ import annotations

from typing import Dict, List


def get_cockpit_route_handoff_manifest() -> Dict[str, object]:
    routes: List[Dict[str, object]] = [
        {
            "route_id": "static_modern_cockpit",
            "path": "frontend/cockpit/modern/claire_cockpit_shell.html",
            "purpose": "Modern consolidated cockpit shell.",
            "launch_priority": 1,
            "requires_backend": True,
        },
        {
            "route_id": "canonical_payload",
            "path": "/dashboard/payload",
            "purpose": "Backend-owned canonical payload truth.",
            "launch_priority": 2,
            "requires_backend": True,
        },
        {
            "route_id": "payload_status",
            "path": "/dashboard/payload/status",
            "purpose": "Payload availability and status.",
            "launch_priority": 3,
            "requires_backend": True,
        },
        {
            "route_id": "health",
            "path": "/health",
            "purpose": "Backend health.",
            "launch_priority": 4,
            "requires_backend": True,
        },
    ]
    return {
        "version": "v19.89.8-S247-S253",
        "handoff_id": "modern_cockpit_route_handoff",
        "routes": routes,
        "preferred_cockpit_shell": "frontend/cockpit/modern/claire_cockpit_shell.html",
        "backend_required": True,
        "unsafe_authority_enabled": False,
    }
