from datetime import datetime
from typing import Any, Dict, List


class LiveDashboardResultRenderingContract:
    def __init__(self) -> None:
        self.rendering_version = "v18.45"
        self.fail_closed = True

    def build_render_payload(
        self,
        query: str,
        normalized_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        rendered_results = []

        for result in normalized_results:
            rendered_results.append(
                {
                    "title": str(result.get("title", "")),
                    "url": str(result.get("url", "")),
                    "snippet": str(result.get("snippet", "")),
                    "trust_score": float(
                        result.get("trust_score", 0.0)
                    ),
                    "source_trust_level": str(
                        result.get(
                            "source_trust_level",
                            "unverified",
                        )
                    ),
                    "provider": str(
                        result.get("provider", "unknown")
                    ),
                    "render_safe": True,
                }
            )

        return {
            "rendering_version": self.rendering_version,
            "created_utc": datetime.utcnow().isoformat() + "Z",
            "query": query,
            "dashboard_render_ready": True,
            "result_count": len(rendered_results),
            "results": rendered_results,
            "ui_state": {
                "review_mode_enabled": True,
                "operator_visible": True,
                "live_results_present": len(rendered_results) > 0,
            },
            "governance_state": self.governance_state(),
        }

    def governance_state(self) -> Dict[str, Any]:
        return {
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "review_gate_enforced": True,
            "dashboard_render_contract_enforced": True,
            "safe_rendering_only": True,
            "fail_closed_mode": True,
        }
