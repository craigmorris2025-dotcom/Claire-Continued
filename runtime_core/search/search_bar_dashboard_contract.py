"""
Claire Syntalion v17.96.1
Search Bar Dashboard Contract Repair

Fix:
- Correctly detects blocked inner route results from the runtime policy layer.
- Marks dashboard display_state as blocked when governance blocks a query.
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_core.search.search_bar_runtime_policy_layer import SearchBarRuntimePolicyLayer


class SearchBarDashboardContract:
    def __init__(self) -> None:
        self.policy_layer = SearchBarRuntimePolicyLayer()

    def submit_for_dashboard(
        self,
        query: str,
        requested_mode: str | None = None,
    ) -> Dict[str, Any]:
        policy_result = self.policy_layer.submit(query, requested_mode)

        resolved_mode = policy_result.get("resolved_mode", "unknown")
        outer_status = policy_result.get("status", "UNKNOWN")

        route_result = policy_result.get("route_result", {})
        inner_route = route_result.get("route_result", {}) if isinstance(route_result, dict) else {}
        inner_status = route_result.get("status", "") if isinstance(route_result, dict) else ""

        status_for_display = inner_status if inner_status == "SEARCH_BAR_QUERY_BLOCKED" else outer_status

        result_payload = inner_route.get("result", {}) if isinstance(inner_route, dict) else {}

        cards: List[Dict[str, Any]] = []

        if isinstance(result_payload, dict):
            cards.append(
                {
                    "card_type": "search_result_summary",
                    "title": resolved_mode,
                    "status": result_payload.get("status", status_for_display),
                    "payload": result_payload,
                    "read_only": True,
                }
            )

        return {
            "version": "v17.96.1",
            "dashboard_contract": "search_bar_dashboard_contract",
            "query": query,
            "requested_mode": requested_mode or "",
            "resolved_mode": resolved_mode,
            "status": status_for_display,
            "display_state": self._display_state(status_for_display),
            "cards": cards,
            "raw_policy_result": policy_result,
            "read_only": True,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "dashboard_rewire_performed": False,
        }

    def _display_state(self, status: str) -> str:
        if status == "SEARCH_BAR_QUERY_BLOCKED":
            return "blocked"
        if status == "POLICY_CHECKED_ROUTE_COMPLETE":
            return "ready"
        if "EMPTY" in status:
            return "empty"
        return "review"
