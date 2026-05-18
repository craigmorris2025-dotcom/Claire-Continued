from __future__ import annotations
from typing import Any
from claire.api.s43_route_visibility_registry import build_route_registry
from claire.api.s43_route_lineage import build_route_lineage


def build_exposure_inventory(app: Any) -> dict:
    return {"visibility": build_route_registry(app), "lineage": build_route_lineage(app), "governance": {"read_only": True, "runtime_mutation": False, "browser_execution": False, "javascript_execution": False}}
