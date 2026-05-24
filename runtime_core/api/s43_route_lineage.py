from __future__ import annotations
from typing import Any

def build_route_lineage(app: Any) -> dict[str, Any]:
    lineage = []
    for route in getattr(app, "routes", []):
        endpoint = getattr(route, "endpoint", None)
        lineage.append({
            "path": getattr(route, "path", ""),
            "name": getattr(route, "name", ""),
            "module": getattr(endpoint, "__module__", None),
            "endpoint": getattr(endpoint, "__name__", None),
        })
    return {"lineage": lineage, "lineage_total": len(lineage)}

def build_mounted_route_lineage(app: Any) -> dict[str, Any]:
    return build_route_lineage(app)
