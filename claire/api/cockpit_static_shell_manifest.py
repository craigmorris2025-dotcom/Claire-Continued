from __future__ import annotations

from typing import Dict, List


def get_static_shell_manifest() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S240-S246",
        "shell_files": [
            "frontend/cockpit/modern/claire_cockpit_shell.html",
            "frontend/cockpit/modern/claire_cockpit_shell.css",
            "frontend/cockpit/modern/claire_cockpit_shell.js",
        ],
        "render_regions": [
            "top_command_bar",
            "primary_runtime_panel",
            "operations_strip",
            "monitoring_column",
            "lifecycle_evidence_workspace",
            "diagnostics_drawer",
        ],
        "safe_fetch_endpoints": [
            "/dashboard/payload",
            "/dashboard/payload/status",
            "/health",
        ],
        "blocked_actions": [
            "run_autonomous_update",
            "execute_runtime_mutation",
            "start_continuous_crawl",
            "promote_without_review",
        ],
        "unsafe_authority_enabled": False,
    }
