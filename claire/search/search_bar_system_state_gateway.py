"""
Claire Syntalion v18.00
Search Bar System State Gateway

Purpose:
- Creates a governed gateway between the permanent search bar surface
  and Claire system-state awareness.
- System state is exposed read-only.
- No runtime mutation, autonomous execution, or automatic updates.
"""

from __future__ import annotations

from typing import Any, Dict

from claire.search.search_bar_operator_surface import SearchBarOperatorSurface


class SearchBarSystemStateGateway:
    def __init__(self) -> None:
        self.surface = SearchBarOperatorSurface()

    def get_system_state(
        self,
        query: str,
        requested_mode: str | None = None,
    ) -> Dict[str, Any]:
        surface = self.surface.render_surface(query, requested_mode)

        return {
            "version": "v18.00",
            "gateway": "search_bar_system_state_gateway",
            "query": query,
            "requested_mode": requested_mode or "",
            "resolved_mode": surface.get("resolved_mode", "unknown"),
            "operator_status": surface.get("operator_status", "UNKNOWN"),
            "surface": surface,
            "system_state": {
                "search_bar_ready": True,
                "governance_active": True,
                "runtime_truth_read_only": True,
                "agent_execution_enabled": False,
                "automatic_updates_enabled": False,
                "runtime_mutation_enabled": False,
                "dashboard_rewire_performed": False,
            },
            "read_only": True,
            "live_web_execution_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
        }
