"""
Claire Syntalion v17.94
Search Bar Capability Registry
"""

from __future__ import annotations

from typing import Any, Dict, List


DEFAULT_CAPABILITIES = [
    {
        "capability": "normal_web_search",
        "enabled": False,
        "execution_allowed": False,
        "read_only": True,
    },
    {
        "capability": "governed_research_search",
        "enabled": True,
        "execution_allowed": False,
        "read_only": True,
    },
    {
        "capability": "runtime_truth_search",
        "enabled": True,
        "execution_allowed": False,
        "read_only": True,
    },
    {
        "capability": "claire_system_search",
        "enabled": False,
        "execution_allowed": False,
        "read_only": True,
    },
    {
        "capability": "future_agent_command",
        "enabled": False,
        "execution_allowed": False,
        "read_only": True,
    },
]


class SearchBarCapabilityRegistry:
    def __init__(self) -> None:
        self.capabilities = DEFAULT_CAPABILITIES

    def list_capabilities(self) -> List[Dict[str, Any]]:
        return self.capabilities

    def get_capability(self, name: str) -> Dict[str, Any]:
        for capability in self.capabilities:
            if capability["capability"] == name:
                return capability

        return {
            "capability": name,
            "enabled": False,
            "execution_allowed": False,
            "read_only": True,
            "status": "UNKNOWN_CAPABILITY",
        }
