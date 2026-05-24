"""
Route Contract
==============
ACS2-Claire / Syntalion — v10.3.2

Defines the contract for route selection output. The route contract
ensures that route_selected, confidence, terminal_state, and skipped
stage information is consistent and valid.

Claire supports 3 primary routes (portfolio, breakthrough, acquisition)
and 3 secondary routes (system_redesign, operational_optimization,
business_model). Each route determines which lifecycle stages execute,
which are skipped, and what terminal states are valid.
"""

import json
import hashlib
from typing import Any, Dict, List, Optional, Tuple


class RouteContract:
    """Validates route selection output conformance."""

    VERSION = "10.3.2"

    ROUTES = {
        "portfolio": {
            "description": "Standard portfolio intelligence path",
            "primary": True,
            "min_confidence": 0.4,
            "required_stages": [1, 2, 3, 4, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 26, 27, 28, 29, 30],
            "skippable_stages": [21, 22, 23, 24, 25],
            "valid_terminal_states": ["actionable", "monitoring", "rejected", "deferred"],
        },
        "breakthrough": {
            "description": "Breakthrough classification and escalation path",
            "primary": True,
            "min_confidence": 0.6,
            "required_stages": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 24, 25, 26, 27, 28, 29, 30],
            "skippable_stages": [13, 21, 22, 23],
            "valid_terminal_states": ["actionable", "escalated", "monitoring", "deferred"],
        },
        "acquisition": {
            "description": "Acquisition target identification and packaging",
            "primary": True,
            "min_confidence": 0.5,
            "required_stages": [1, 2, 3, 4, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30],
            "skippable_stages": [14, 15, 24, 25],
            "valid_terminal_states": ["actionable", "monitoring", "rejected", "archived"],
        },
        "system_redesign": {
            "description": "System architecture redesign path",
            "primary": False,
            "min_confidence": 0.55,
            "required_stages": [1, 2, 3, 9, 10, 11, 12, 15, 16, 17, 18, 19, 20, 24, 25, 26, 27, 28, 29, 30],
            "skippable_stages": [13, 14, 21, 22, 23],
            "valid_terminal_states": ["actionable", "escalated", "deferred"],
        },
        "operational_optimization": {
            "description": "Operational efficiency optimization path",
            "primary": False,
            "min_confidence": 0.45,
            "required_stages": [1, 2, 3, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 26, 27, 28, 29, 30],
            "skippable_stages": [14, 21, 22, 23, 24, 25],
            "valid_terminal_states": ["actionable", "monitoring", "deferred"],
        },
        "business_model": {
            "description": "Business model innovation path",
            "primary": False,
            "min_confidence": 0.5,
            "required_stages": [1, 2, 3, 4, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 26, 27, 28, 29, 30],
            "skippable_stages": [14, 15, 21, 22, 23],
            "valid_terminal_states": ["actionable", "monitoring", "rejected", "deferred"],
        },
    }

    REQUIRED_OUTPUT_FIELDS = {
        "route_selected": str,
        "confidence": (int, float),
        "terminal_state": str,
        "skipped_stages": list,
        "route_rationale": str,
        "alternative_routes": list,
        "selection_timestamp": str,
    }

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(self, route_output: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate route selection output against the contract."""
        self.errors = []
        self.warnings = []

        for field, expected in self.REQUIRED_OUTPUT_FIELDS.items():
            if field not in route_output:
                self.errors.append(f"Missing route output field: {field}")
            elif not isinstance(route_output[field], expected):
                self.errors.append(
                    f"Route field '{field}' type mismatch"
                )

        route = route_output.get("route_selected", "")
        if route not in self.ROUTES:
            self.errors.append(f"Unknown route: {route}")
            return len(self.errors) == 0, self.errors.copy(), self.warnings.copy()

        route_def = self.ROUTES[route]
        confidence = route_output.get("confidence", 0)
        if isinstance(confidence, (int, float)):
            if confidence < route_def["min_confidence"]:
                self.warnings.append(
                    f"Confidence {confidence} below minimum {route_def['min_confidence']} for route '{route}'"
                )

        terminal = route_output.get("terminal_state", "")
        if terminal and terminal not in route_def["valid_terminal_states"]:
            self.errors.append(
                f"Terminal state '{terminal}' invalid for route '{route}'. "
                f"Valid: {route_def['valid_terminal_states']}"
            )

        skipped = route_output.get("skipped_stages", [])
        if isinstance(skipped, list):
            allowed_skips = set(route_def["skippable_stages"])
            for s in skipped:
                if s not in allowed_skips:
                    self.warnings.append(
                        f"Stage {s} skipped but not in skippable list for route '{route}'"
                    )

        return len(self.errors) == 0, self.errors.copy(), self.warnings.copy()

    def get_route_definition(self, route: str) -> Optional[Dict[str, Any]]:
        """Return the full definition for a route."""
        return self.ROUTES.get(route)

    def list_routes(self, primary_only: bool = False) -> List[str]:
        """List available routes."""
        if primary_only:
            return [r for r, d in self.ROUTES.items() if d["primary"]]
        return list(self.ROUTES.keys())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize contract for audit/export."""
        return {
            "contract_type": "route_selection",
            "version": self.VERSION,
            "routes": {
                name: {
                    "description": defn["description"],
                    "primary": defn["primary"],
                    "min_confidence": defn["min_confidence"],
                }
                for name, defn in self.ROUTES.items()
            },
            "required_fields": list(self.REQUIRED_OUTPUT_FIELDS.keys()),
        }
