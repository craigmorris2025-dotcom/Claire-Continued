"""
Dashboard Contract
==================
ACS2-Claire / Syntalion — v10.3.2

Converts validated runtime output into UI-ready sections for the unified
lifecycle dashboard. This contract defines the transformation rules and
required panel data shapes for each dashboard panel.

The dashboard contract ensures that every panel receives exactly the data
it needs in the format it expects, derived from core_run_output.json.
"""

import json
from typing import Any, Dict, List, Optional


class DashboardContract:
    """Transforms runtime output into UI-ready dashboard sections."""

    VERSION = "10.3.2"

    PANELS = [
        "run",
        "lifecycle",
        "research",
        "discover",
        "trend",
        "portfolio",
        "breakthrough",
        "design",
        "technology",
        "packages",
        "monitor",
        "system",
    ]

    PANEL_DATA_REQUIREMENTS = {
        "run": {
            "fields": ["run_id", "company_name", "ticker", "sector", "thesis",
                        "overall_score", "confidence", "route_selected",
                        "terminal_state", "timestamp"],
            "derived": ["score_badge_data", "status_indicator"],
        },
        "lifecycle": {
            "fields": ["lifecycle_stage", "lifecycle_stage_name",
                        "stages_completed", "stages_skipped"],
            "derived": ["stage_cards", "progress_percentage", "route_path_visual"],
        },
        "research": {
            "fields": ["evidence"],
            "derived": ["evidence_cards", "source_breakdown", "credibility_summary"],
        },
        "discover": {
            "fields": ["metadata"],
            "derived": ["discovery_items", "signal_strength_map", "opportunity_list"],
        },
        "trend": {
            "fields": ["scores", "metadata"],
            "derived": ["trend_indicators", "thesis_timeline", "convergence_map"],
        },
        "portfolio": {
            "fields": ["scores", "overall_score", "confidence", "route_selected"],
            "derived": ["radar_chart_data", "score_cards", "recommendation_summary"],
        },
        "breakthrough": {
            "fields": ["route_selected", "scores", "metadata"],
            "derived": ["classification_badge", "escalation_status", "impact_assessment"],
        },
        "design": {
            "fields": ["route_selected", "metadata"],
            "derived": ["design_portal_status", "auto_design_output", "component_tree"],
        },
        "technology": {
            "fields": ["scores", "metadata"],
            "derived": ["tech_stack_assessment", "compatibility_matrix", "viability_score"],
        },
        "packages": {
            "fields": ["run_id", "terminal_state", "route_selected"],
            "derived": ["export_list", "package_status", "download_links"],
        },
        "monitor": {
            "fields": ["metadata"],
            "derived": ["monitor_timeline", "live_signals", "source_health"],
        },
        "system": {
            "fields": ["metadata"],
            "derived": ["system_health", "governance_status", "update_status", "gap_analysis"],
        },
    }

    def __init__(self):
        self.transform_errors = []

    def transform_for_panel(
        self, panel_name: str, runtime_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform runtime output into the data shape required by a specific panel.

        Returns a dict with 'panel', 'data', 'derived', and 'valid' keys.
        """
        if panel_name not in self.PANELS:
            return {"panel": panel_name, "data": {}, "derived": {}, "valid": False,
                    "error": f"Unknown panel: {panel_name}"}

        requirements = self.PANEL_DATA_REQUIREMENTS[panel_name]
        data = {}
        missing = []

        for field in requirements["fields"]:
            if field in runtime_output:
                data[field] = runtime_output[field]
            else:
                missing.append(field)

        derived = self._compute_derived(panel_name, data, runtime_output)

        return {
            "panel": panel_name,
            "data": data,
            "derived": derived,
            "valid": len(missing) == 0,
            "missing_fields": missing,
        }

    def transform_all_panels(self, runtime_output: Dict[str, Any]) -> Dict[str, Any]:
        """Transform runtime output for all panels at once."""
        result = {}
        for panel in self.PANELS:
            result[panel] = self.transform_for_panel(panel, runtime_output)
        return result

    def _compute_derived(
        self, panel_name: str, data: Dict, full_output: Dict
    ) -> Dict[str, Any]:
        """Compute derived fields for a panel based on available data."""
        derived = {}

        if panel_name == "run":
            score = data.get("overall_score", 0)
            derived["score_badge_data"] = {
                "value": score,
                "label": self._score_label(score),
                "color": self._score_color(score),
            }
            state = data.get("terminal_state", "pending")
            derived["status_indicator"] = {
                "state": state,
                "icon": self._state_icon(state),
            }

        elif panel_name == "lifecycle":
            completed = data.get("stages_completed", [])
            derived["progress_percentage"] = round(len(completed) / 30 * 100, 1)
            derived["stage_cards"] = [
                {"number": i, "status": "completed" if i in completed else "pending"}
                for i in range(1, 31)
            ]

        elif panel_name == "research":
            evidence = data.get("evidence", [])
            derived["evidence_cards"] = [
                {
                    "source": e.get("source", "unknown"),
                    "content": e.get("content", "")[:200],
                    "relevance": e.get("relevance", 0),
                }
                for e in evidence[:20]
            ]
            derived["source_breakdown"] = self._count_sources(evidence)

        elif panel_name == "portfolio":
            scores = data.get("scores", {})
            derived["radar_chart_data"] = {
                "labels": list(scores.keys()),
                "values": list(scores.values()),
            }

        return derived

    @staticmethod
    def _score_label(score: float) -> str:
        if score >= 80:
            return "Strong"
        elif score >= 60:
            return "Moderate"
        elif score >= 40:
            return "Developing"
        return "Weak"

    @staticmethod
    def _score_color(score: float) -> str:
        if score >= 80:
            return "#22c55e"
        elif score >= 60:
            return "#3b82f6"
        elif score >= 40:
            return "#f59e0b"
        return "#ef4444"

    @staticmethod
    def _state_icon(state: str) -> str:
        icons = {
            "actionable": "check-circle",
            "monitoring": "eye",
            "rejected": "x-circle",
            "escalated": "arrow-up-circle",
            "deferred": "clock",
            "archived": "archive",
        }
        return icons.get(state, "help-circle")

    @staticmethod
    def _count_sources(evidence: List[Dict]) -> Dict[str, int]:
        counts = {}
        for e in evidence:
            src = e.get("source", "unknown")
            counts[src] = counts.get(src, 0) + 1
        return counts

    def to_dict(self) -> Dict[str, Any]:
        """Serialize contract for audit/export."""
        return {
            "contract_type": "dashboard",
            "version": self.VERSION,
            "panels": self.PANELS,
            "panel_requirements": {
                name: {
                    "required_fields": req["fields"],
                    "derived_fields": req["derived"],
                }
                for name, req in self.PANEL_DATA_REQUIREMENTS.items()
            },
        }
