"""
Claire Syntalion v17.98
Search Bar Unified Context Layer

Purpose:
- Creates a unified context payload for the permanent search bar.
- Aggregates dashboard contract state, capability registry state,
  and session-state awareness into one read-only context object.
- Does not enable execution, updates, or mutation.
"""

from __future__ import annotations

from typing import Any, Dict

from claire.search.search_bar_dashboard_contract import SearchBarDashboardContract
from claire.search.search_bar_capability_registry import SearchBarCapabilityRegistry
from claire.search.search_bar_session_state import SearchBarSessionState


class SearchBarUnifiedContextLayer:
    def __init__(self) -> None:
        self.dashboard_contract = SearchBarDashboardContract()
        self.registry = SearchBarCapabilityRegistry()
        self.session_state = SearchBarSessionState()

    def build_context(
        self,
        query: str,
        requested_mode: str | None = None,
    ) -> Dict[str, Any]:
        dashboard_result = self.dashboard_contract.submit_for_dashboard(
            query=query,
            requested_mode=requested_mode,
        )

        session_history = self.session_state.get_session_history()

        return {
            "version": "v17.98",
            "query": query,
            "requested_mode": requested_mode or "",
            "resolved_mode": dashboard_result.get("resolved_mode", "unknown"),
            "dashboard_result": dashboard_result,
            "capabilities": self.registry.list_capabilities(),
            "session_history_count": len(session_history),
            "context_ready": True,
            "read_only": True,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "dashboard_rewire_performed": False,
            "live_web_execution_enabled": False,
        }
