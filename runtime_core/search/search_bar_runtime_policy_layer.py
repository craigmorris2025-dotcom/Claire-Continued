"""
Claire Syntalion v17.95
Search Bar Runtime Policy Layer

Purpose:
- Applies capability policy checks before search bar routes reach runtime-facing bridge behavior.
- Keeps all current search bar capabilities read-only.
- Blocks execution-disabled capabilities from being executed.
- Preserves future AI-agent mode as recognized but disabled.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.search.search_bar_capability_registry import SearchBarCapabilityRegistry
from runtime_core.search.search_bar_runtime_bridge import SearchBarRuntimeBridge


class SearchBarRuntimePolicyLayer:
    def __init__(self) -> None:
        self.registry = SearchBarCapabilityRegistry()
        self.bridge = SearchBarRuntimeBridge()

    def evaluate_policy(self, resolved_mode: str) -> Dict[str, Any]:
        capability = self.registry.get_capability(resolved_mode)

        return {
            "version": "v17.95",
            "capability": capability.get("capability", resolved_mode),
            "enabled": capability.get("enabled", False),
            "execution_allowed": capability.get("execution_allowed", False),
            "read_only": capability.get("read_only", True),
            "policy_status": (
                "CAPABILITY_AVAILABLE_READ_ONLY"
                if capability.get("enabled") and capability.get("read_only") and not capability.get("execution_allowed")
                else "CAPABILITY_EXECUTION_BLOCKED"
            ),
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
        }

    def submit(self, query: str, requested_mode: str | None = None) -> Dict[str, Any]:
        preflight = self.bridge.governance.router.route(query, requested_mode)
        resolved_mode = preflight.get("resolved_mode", "unknown")

        policy = self.evaluate_policy(resolved_mode)

        if policy["execution_allowed"] is True:
            return {
                "version": "v17.95",
                "status": "POLICY_ERROR_EXECUTION_UNEXPECTEDLY_ALLOWED",
                "query": query,
                "requested_mode": requested_mode or "",
                "resolved_mode": resolved_mode,
                "policy": policy,
                "read_only": True,
                "automatic_updates_enabled": False,
                "autonomous_agent_execution_enabled": False,
                "runtime_truth_mutation_enabled": False,
            }

        routed = self.bridge.submit(query, requested_mode)

        return {
            "version": "v17.95",
            "status": "POLICY_CHECKED_ROUTE_COMPLETE",
            "query": query,
            "requested_mode": requested_mode or "",
            "resolved_mode": routed.get("resolved_mode", resolved_mode),
            "policy": policy,
            "route_result": routed,
            "read_only": True,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
        }
