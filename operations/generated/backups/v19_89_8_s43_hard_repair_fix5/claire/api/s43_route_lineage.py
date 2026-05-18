from __future__ import annotations
from typing import Any


def build_route_lineage(app: Any) -> dict:
    lineage = []
    for route in getattr(app, "routes", []):
        lineage.append({"path": getattr(route, "path", ""), "name": getattr(route, "name", ""), "module": getattr(getattr(route, "endpoint", None), "__module__", None)})
    return {"lineage": lineage, "lineage_total": len(lineage)}
