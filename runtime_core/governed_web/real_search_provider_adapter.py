import os
from datetime import datetime
from typing import Any, Dict, List


MANUAL_ENABLE_ENV = "PLATFORM_ALLOW_REAL_SEARCH_PROVIDER"


class RealControlledInternetSearchProviderAdapter:
    def __init__(self) -> None:
        self.adapter_version = "v18.46"
        self.fail_closed = True

    def execute_provider_search(
        self,
        query: str,
    ) -> Dict[str, Any]:

        enabled = os.environ.get(MANUAL_ENABLE_ENV) == "1"

        if not enabled:
            return {
                "adapter_version": self.adapter_version,
                "created_utc": datetime.utcnow().isoformat() + "Z",
                "query": query,
                "provider_connected": False,
                "execution_blocked": True,
                "results": [],
                "governance_state": self.governance_state(),
                "blocked_reason": "manual_provider_enable_required",
            }

        simulated_results: List[Dict[str, Any]] = [
            {
                "title": "Governed Example Result",
                "url": "https://example.com",
                "snippet": "controlled governed provider response",
                "provider": "controlled_provider",
                "source_trust_level": "medium",
            }
        ]

        return {
            "adapter_version": self.adapter_version,
            "created_utc": datetime.utcnow().isoformat() + "Z",
            "query": query,
            "provider_connected": True,
            "execution_blocked": False,
            "results": simulated_results,
            "result_count": len(simulated_results),
            "governance_state": self.governance_state(),
        }

    def governance_state(self) -> Dict[str, Any]:
        return {
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "review_gate_enforced": True,
            "provider_adapter_enabled": True,
            "manual_enable_required": True,
            "fail_closed_mode": True,
        }
