from datetime import datetime
from typing import Any, Dict, List


class DashboardSearchAPIAdapter:
    def __init__(self) -> None:
        self.adapter_version = "v18.38"
        self.fail_closed = True

    def build_dashboard_payload(
        self,
        query: str,
        parsed_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        safe_results = []

        for result in parsed_results:
            safe_results.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", ""),
                    "source_trust_level": result.get(
                        "source_trust_level",
                        "unverified",
                    ),
                    "metadata": result.get("metadata", {}),
                }
            )

        return {
            "adapter_version": self.adapter_version,
            "created_utc": datetime.utcnow().isoformat() + "Z",
            "query": query,
            "result_count": len(safe_results),
            "results": safe_results,
            "dashboard_state": {
                "live_search_connected": False,
                "review_mode_enabled": True,
                "runtime_truth_mutation": False,
                "automatic_updates_enabled": False,
                "agent_execution_enabled": False,
                "fail_closed_mode": True,
            },
        }

    def governance_state(self) -> Dict[str, Any]:
        return {
            "dashboard_adapter_enabled": True,
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "review_required": True,
            "fail_closed_mode": True,
        }
