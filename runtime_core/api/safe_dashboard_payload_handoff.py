from __future__ import annotations
from typing import Any
from runtime_core.api.dashboard_payload_bridge import build_dashboard_payload, get_dashboard_payload

def build_safe_dashboard_payload_handoff(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_dashboard_payload()

def get_safe_dashboard_payload_handoff(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return get_dashboard_payload()

router = None
