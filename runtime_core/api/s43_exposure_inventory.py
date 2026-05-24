from __future__ import annotations
from typing import Any
from runtime_core.api._s43_governance import build_governance
from runtime_core.api.s43_route_lineage import build_route_lineage
from runtime_core.api.s43_route_visibility_registry import build_route_registry

def build_exposure_inventory(app: Any) -> dict[str, Any]:
    governance = build_governance()
    return {
        "visibility": build_route_registry(app),
        "lineage": build_route_lineage(app),
        "governance": {
            "read_only": True,
            "runtime_mutation": False,
            "runtime_truth_mutation": False,
            "mutation_authority": False,
            "browser_execution": False,
            "javascript_execution": False,
            "autonomous_execution": False,
            "automatic_updates": False,
            **governance,
        },
    }

def build_mounted_exposure_inventory(app: Any) -> dict[str, Any]:
    return build_exposure_inventory(app)
