from __future__ import annotations
from typing import Any
READ_ONLY_CLASSIFICATIONS = {"GET", "HEAD"}

def classify_route(route: Any) -> dict:
    methods = sorted(list(getattr(route, "methods", []) or []))
    return {
        "path": getattr(route, "path", ""),
        "name": getattr(route, "name", ""),
        "methods": methods,
        "read_only": all(method in READ_ONLY_CLASSIFICATIONS for method in methods),
        "operation_id": getattr(route, "operation_id", None),
    }

def build_route_registry(app: Any) -> dict:
    routes = []
    for route in getattr(app, "routes", []):
        try:
            routes.append(classify_route(route))
        except Exception:
            continue
    return {"route_total": len(routes), "routes": routes, "governance": {"mutation_authority": False, "runtime_authority": False, "autonomous_execution": False}}
