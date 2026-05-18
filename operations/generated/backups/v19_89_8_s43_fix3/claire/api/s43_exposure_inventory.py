from __future__ import annotations

from typing import Any

from claire.api.s43_route_lineage import build_route_lineage
from claire.api.s43_route_visibility_registry import build_route_registry


def build_exposure_inventory(app: Any) -> dict:
    return {
        "visibility": build_route_registry(app),
        "lineage": build_route_lineage(app),
        "governance": {
            "read_only": True,
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": False,
            "runtime_mutation": False,
            "browser_execution": False,
            "javascript_execution": False,
            "automatic_updates": False,
            "continuous_live_crawling": False,
        },
    }
