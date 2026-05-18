from __future__ import annotations

from typing import Any


def build_route_lineage(app: Any) -> dict:
    lineage = []
    for route in getattr(app, "routes", []):
        endpoint = getattr(route, "endpoint", None)
        lineage.append({
            "path": getattr(route, "path", ""),
            "name": getattr(route, "name", ""),
            "module": getattr(endpoint, "__module__", None),
            "callable": getattr(endpoint, "__name__", None),
        })
    return {
        "lineage_total": len(lineage),
        "lineage": lineage,
        "governance": {
            "read_only_lineage": True,
            "mutation_authority": False,
            "runtime_authority": False,
        },
    }
