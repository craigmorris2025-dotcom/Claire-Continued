from __future__ import annotations

from typing import Any

READ_ONLY_METHODS = {"GET", "HEAD", "OPTIONS"}


def classify_route(route: Any) -> dict:
    methods = sorted(list(getattr(route, "methods", []) or []))
    read_only = bool(methods) and all(method in READ_ONLY_METHODS for method in methods)
    return {
        "path": getattr(route, "path", ""),
        "name": getattr(route, "name", ""),
        "methods": methods,
        "read_only": read_only,
        "operation_id": getattr(route, "operation_id", None),
        "exposure_class": "read_only" if read_only else "blocked_or_mutating",
        "governance_classification": {
            "mutation_authority": False if read_only else None,
            "runtime_authority": False,
            "autonomous_execution": False,
        },
    }


def build_route_registry(app: Any) -> dict:
    routes = []
    for route in getattr(app, "routes", []):
        try:
            routes.append(classify_route(route))
        except Exception:
            continue
    return {
        "route_total": len(routes),
        "routes": routes,
        "governance": {
            "read_only_inventory": True,
            "mutation_authority": False,
            "runtime_authority": False,
            "autonomous_execution": False,
            "browser_execution": False,
            "javascript_execution": False,
            "automatic_updates": False,
        },
    }
