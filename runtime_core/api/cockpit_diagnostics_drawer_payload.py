from __future__ import annotations

from typing import Dict, List


def get_diagnostics_drawer_payload() -> Dict[str, object]:
    diagnostics: List[Dict[str, object]] = [
        {
            "item_id": "raw_payload",
            "label": "Raw Payload",
            "default_visible": False,
            "purpose": "Inspect backend-owned truth payload without allowing mutation.",
            "authority": "read_only",
        },
        {
            "item_id": "endpoint_status",
            "label": "Endpoint Status",
            "default_visible": False,
            "purpose": "Verify route availability and health.",
            "authority": "read_only",
        },
        {
            "item_id": "contract_validation",
            "label": "Contract Validation",
            "default_visible": False,
            "purpose": "Show contract pass/fail state for cockpit surfaces.",
            "authority": "read_only",
        },
        {
            "item_id": "blocked_capabilities",
            "label": "Blocked Capabilities",
            "default_visible": False,
            "purpose": "Explain why unsafe authority remains unavailable.",
            "authority": "read_only",
        },
    ]
    return {
        "version": "v19.89.8-S219-S225",
        "drawer_default_open": False,
        "diagnostics": diagnostics,
        "allows_runtime_mutation": False,
    }
