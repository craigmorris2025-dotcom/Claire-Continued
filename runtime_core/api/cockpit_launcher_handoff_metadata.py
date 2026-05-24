from __future__ import annotations

from typing import Dict


def get_launcher_handoff_metadata() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S247-S253",
        "launcher_target": "frontend/cockpit/modern/claire_cockpit_shell.html",
        "backend_base_url": "http://127.0.0.1:8000",
        "must_check_before_open": ["/health", "/dashboard/payload/status"],
        "fallback_message": "Backend must be running before the modern cockpit can show live state.",
        "file_url_allowed_as_static_shell": True,
        "live_payload_requires_backend": True,
        "unsafe_authority_enabled": False,
    }
