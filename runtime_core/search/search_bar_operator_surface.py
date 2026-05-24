"""
Claire Syntalion v17.99
Search Bar Operator Surface

Purpose:
- Creates a stable operator-facing surface for the permanent search bar.
- Wraps unified context into concise operator status, cards, and controls.
- Does not rewire dashboard HTML.
- Does not enable live web execution, automatic updates, autonomous execution, or mutation.
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_core.search.search_bar_unified_context_layer import SearchBarUnifiedContextLayer


class SearchBarOperatorSurface:
    def __init__(self) -> None:
        self.context_layer = SearchBarUnifiedContextLayer()

    def render_surface(
        self,
        query: str,
        requested_mode: str | None = None,
    ) -> Dict[str, Any]:
        context = self.context_layer.build_context(query, requested_mode)
        dashboard_result = context.get("dashboard_result", {})
        display_state = dashboard_result.get("display_state", "review")

        controls: List[Dict[str, Any]] = [
            {
                "control": "submit_search",
                "enabled": True,
                "execution_type": "governed_route_only",
            },
            {
                "control": "agent_execute",
                "enabled": False,
                "execution_type": "disabled",
            },
            {
                "control": "automatic_update",
                "enabled": False,
                "execution_type": "disabled",
            },
            {
                "control": "runtime_truth_mutation",
                "enabled": False,
                "execution_type": "disabled",
            },
        ]

        return {
            "version": "v17.99",
            "surface": "search_bar_operator_surface",
            "query": query,
            "requested_mode": requested_mode or "",
            "resolved_mode": context.get("resolved_mode", "unknown"),
            "display_state": display_state,
            "operator_status": self._operator_status(display_state),
            "cards": dashboard_result.get("cards", []),
            "controls": controls,
            "context": context,
            "read_only": True,
            "dashboard_rewire_performed": False,
            "live_web_execution_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
        }

    def _operator_status(self, display_state: str) -> str:
        if display_state == "ready":
            return "SEARCH_BAR_READY_FOR_OPERATOR_REVIEW"
        if display_state == "blocked":
            return "SEARCH_BAR_QUERY_BLOCKED_BY_GOVERNANCE"
        if display_state == "empty":
            return "SEARCH_BAR_EMPTY_QUERY"
        return "SEARCH_BAR_REVIEW_REQUIRED"
