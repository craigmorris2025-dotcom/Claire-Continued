"""
Claire Syntalion v17.91
Search Bar Governance Layer
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_core.search.search_bar_mode_router import SearchBarModeRouter

BLOCKED_PATTERNS = [
    "delete system32",
    "self modify",
    "update yourself",
    "autonomous install",
    "disable governance",
    "bypass review",
]


class SearchBarGovernanceLayer:
    def __init__(self) -> None:
        self.router = SearchBarModeRouter()

    def normalize(self, query: str) -> str:
        return (query or "").strip().lower()

    def detect_blocked_patterns(self, query: str) -> List[str]:
        normalized = self.normalize(query)
        return [pattern for pattern in BLOCKED_PATTERNS if pattern in normalized]

    def governed_route(
        self,
        query: str,
        requested_mode: str | None = None,
    ) -> Dict[str, Any]:
        blocked = self.detect_blocked_patterns(query)

        if blocked:
            return {
                "version": "v17.91",
                "status": "SEARCH_BAR_QUERY_BLOCKED",
                "query": query,
                "blocked_patterns": blocked,
                "read_only": True,
                "automatic_updates_enabled": False,
                "autonomous_agent_execution_enabled": False,
                "runtime_truth_mutation_enabled": False,
            }

        routed = self.router.route(query, requested_mode)

        routed["version"] = "v17.91"
        routed["governance_checked"] = True
        routed["blocked_patterns"] = []

        return routed
