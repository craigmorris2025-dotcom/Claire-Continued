from __future__ import annotations
from typing import Any
from claire.api._s43_governance import build_governance

READ_ONLY_CLASSIFICATIONS = {"GET", "HEAD"}

def _governance_classification() -> dict[str, Any]:
    governance = build_governance()
    return {
        "runtime_authority": governance["runtime_authority"],
        "mutation_authority": governance["mutation_authority"],
        "runtime_truth_mutation": governance["runtime_truth_mutation"],
        "autonomous_execution": governance["autonomous_execution"],
        "automatic_updates": governance["automatic_updates"],
        "browser_execution": governance["browser_execution"],
        "javascript_execution": governance["javascript_execution"],
        "read_only": governance["read_only"],
    }

def classify_route(route: Any) -> dict[str, Any]:
    methods = sorted(list(getattr(route, "methods", []) or []))
    read_only = all(method in READ_ONLY_CLASSIFICATIONS for method in methods)
    return {
        "path": getattr(route, "path", ""),
        "name": getattr(route, "name", ""),
        "methods": methods,
        "read_only": read_only,
        "operation_id": getattr(route, "operation_id", None),
        "governance_classification": _governance_classification(),
        "exposure_class": "read_only" if read_only else "blocked",
    }

def build_route_registry(app: Any) -> dict[str, Any]:
    routes = []
    for route in getattr(app, "routes", []):
        try:
            routes.append(classify_route(route))
        except Exception:
            continue
    return {"route_total": len(routes), "routes": routes, "governance": _governance_classification()}

def build_visibility_registry(app: Any) -> dict[str, Any]:
    return build_route_registry(app)
