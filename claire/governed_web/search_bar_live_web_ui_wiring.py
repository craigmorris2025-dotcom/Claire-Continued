from datetime import datetime
from typing import Any, Dict, List


class SearchBarLiveWebUIWiring:
    def __init__(self) -> None:
        self.wiring_version = "v18.39"
        self.fail_closed = True

    def build_search_bar_state(
        self,
        query: str,
        dashboard_payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        safe_results: List[Dict[str, Any]] = dashboard_payload.get(
            "results",
            [],
        )

        return {
            "wiring_version": self.wiring_version,
            "created_utc": datetime.utcnow().isoformat() + "Z",
            "search_bar": {
                "query": query,
                "mode": "governed_live_web_review",
                "live_connectivity_enabled": True,
                "review_required": True,
                "result_count": len(safe_results),
            },
            "results": safe_results,
            "ui_governance_state": {
                "runtime_truth_mutation": False,
                "automatic_updates_enabled": False,
                "agent_execution_enabled": False,
                "response_body_limit_enforced": True,
                "review_gate_visible": True,
                "fail_closed_mode": True,
            },
        }

    def governance_state(self) -> Dict[str, Any]:
        return {
            "ui_wiring_enabled": True,
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "review_required": True,
            "fail_closed_mode": True,
        }
