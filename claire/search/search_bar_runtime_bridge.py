"""
Claire Syntalion v17.93
Search Bar Runtime Bridge

Purpose:
- Bridges the governed search bar layer to a single safe runtime-facing adapter.
- Records search/session events.
- Keeps all actions read-only.
- Does not enable automatic updates or autonomous execution.
"""

from __future__ import annotations

from typing import Any, Dict

from claire.search.search_bar_governance_layer import SearchBarGovernanceLayer
from claire.search.search_bar_session_state import SearchBarSessionState


class SearchBarRuntimeBridge:
    def __init__(self) -> None:
        self.governance = SearchBarGovernanceLayer()
        self.session_state = SearchBarSessionState()

    def submit(
        self,
        query: str,
        requested_mode: str | None = None,
    ) -> Dict[str, Any]:
        routed = self.governance.governed_route(query, requested_mode)

        event = self.session_state.append_event(
            query=query,
            resolved_mode=routed.get("resolved_mode", "blocked_or_unknown"),
            status=routed.get("status", "UNKNOWN"),
        )

        return {
            "version": "v17.93",
            "status": routed.get("status", "UNKNOWN"),
            "query": query,
            "requested_mode": requested_mode or "",
            "resolved_mode": routed.get("resolved_mode", "blocked_or_unknown"),
            "route_result": routed,
            "session_event": event,
            "read_only": True,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "bridge": "search_bar_runtime_bridge",
        }
