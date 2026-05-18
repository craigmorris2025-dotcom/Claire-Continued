"""
Claire Syntalion v17.90
Search Bar Mode Router Foundation

Purpose:
- Permanent search bar routing foundation.
- Supports mode classification for:
  normal_web_search, governed_research_search, claire_system_search,
  runtime_truth_search, future_agent_command.
- Future agent command mode is recognized but execution remains disabled.
- No autonomous execution.
- No automatic updates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from claire.search.runtime_truth_search_adapter import RuntimeTruthSearchAdapter


SUPPORTED_MODES = {
    "normal_web_search",
    "governed_research_search",
    "claire_system_search",
    "runtime_truth_search",
    "future_agent_command",
}


@dataclass
class SearchBarRouteResult:
    version: str
    query: str
    requested_mode: str
    resolved_mode: str
    status: str
    read_only: bool
    automatic_updates_enabled: bool
    autonomous_agent_execution_enabled: bool
    result: Dict[str, Any]
    warnings: List[str]


class SearchBarModeRouter:
    def __init__(self) -> None:
        self.runtime_truth_adapter = RuntimeTruthSearchAdapter()

    def normalize_query(self, query: str) -> str:
        return (query or "").strip()

    def resolve_mode(self, query: str, requested_mode: str | None = None) -> str:
        mode = (requested_mode or "").strip().lower()
        normalized = self.normalize_query(query).lower()

        if mode in SUPPORTED_MODES:
            return mode

        if normalized.startswith("/truth ") or normalized.startswith("truth:"):
            return "runtime_truth_search"

        if normalized.startswith("/research ") or normalized.startswith("research:"):
            return "governed_research_search"

        if normalized.startswith("/system ") or normalized.startswith("system:"):
            return "claire_system_search"

        if normalized.startswith("/agent ") or normalized.startswith("agent:"):
            return "future_agent_command"

        return "normal_web_search"

    def route(self, query: str, requested_mode: str | None = None) -> Dict[str, Any]:
        clean_query = self.normalize_query(query)
        resolved_mode = self.resolve_mode(clean_query, requested_mode)
        warnings: List[str] = []

        if not clean_query:
            return {
                "version": "v17.90",
                "query": query,
                "requested_mode": requested_mode or "",
                "resolved_mode": resolved_mode,
                "status": "EMPTY_QUERY_NO_ACTION",
                "read_only": True,
                "automatic_updates_enabled": False,
                "autonomous_agent_execution_enabled": False,
                "result": {},
                "warnings": ["empty_query"],
            }

        if resolved_mode == "runtime_truth_search":
            result = self.runtime_truth_adapter.search(clean_query)
            status = "ROUTED_TO_RUNTIME_TRUTH_SEARCH"

        elif resolved_mode == "normal_web_search":
            result = {
                "mode": "normal_web_search",
                "status": "WEB_SEARCH_MODE_PREPARED_NOT_EXECUTED",
                "query": clean_query,
                "note": "Normal web search routing is prepared. Execution remains governed and disabled in this adapter.",
            }
            status = "WEB_SEARCH_ROUTE_PREPARED"

        elif resolved_mode == "governed_research_search":
            result = {
                "mode": "governed_research_search",
                "status": "GOVERNED_RESEARCH_MODE_PREPARED_NOT_EXECUTED",
                "query": clean_query,
                "note": "Governed research routing is prepared. Evidence capture must remain review-gated.",
            }
            status = "GOVERNED_RESEARCH_ROUTE_PREPARED"

        elif resolved_mode == "claire_system_search":
            result = {
                "mode": "claire_system_search",
                "status": "CLAIRE_SYSTEM_SEARCH_MODE_PREPARED_NOT_EXECUTED",
                "query": clean_query,
                "note": "Claire system search routing is prepared for local project/runtime state search.",
            }
            status = "CLAIRE_SYSTEM_SEARCH_ROUTE_PREPARED"

        elif resolved_mode == "future_agent_command":
            result = {
                "mode": "future_agent_command",
                "status": "AGENT_COMMAND_RECOGNIZED_EXECUTION_DISABLED",
                "query": clean_query,
                "agent_execution_allowed": False,
            }
            status = "AGENT_COMMAND_BLOCKED_EXECUTION_DISABLED"
            warnings.append("future_agent_command_execution_disabled")

        else:
            result = {
                "mode": "unknown",
                "status": "UNSUPPORTED_MODE",
                "query": clean_query,
            }
            status = "UNSUPPORTED_SEARCH_BAR_MODE"
            warnings.append("unsupported_mode")

        return {
            "version": "v17.90",
            "query": query,
            "requested_mode": requested_mode or "",
            "resolved_mode": resolved_mode,
            "status": status,
            "read_only": True,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "result": result,
            "warnings": warnings,
        }
