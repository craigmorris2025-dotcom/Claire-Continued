from datetime import datetime
from typing import Dict, Any, Optional


class GovernanceErrorStateHardening:
    def __init__(self) -> None:
        self.hardening_version = "v18.40"
        self.fail_closed = True

    def build_error_state(
        self,
        error_code: str,
        message: str,
        query: Optional[str] = None,
    ) -> Dict[str, Any]:

        return {
            "hardening_version": self.hardening_version,
            "created_utc": datetime.utcnow().isoformat() + "Z",
            "error": {
                "error_code": error_code,
                "message": message,
                "query": query,
                "review_required": True,
                "operator_visible": True,
            },
            "governance_state": {
                "runtime_truth_mutation": False,
                "automatic_updates_enabled": False,
                "agent_execution_enabled": False,
                "response_body_limit_enforced": True,
                "fail_closed_mode": True,
                "manual_review_required": True,
                "safe_dashboard_rendering": True,
            },
        }

    def build_blocked_state(
        self,
        blocked_reason: str,
    ) -> Dict[str, Any]:

        return self.build_error_state(
            error_code="governed_execution_blocked",
            message=blocked_reason,
        )

    def governance_state(self) -> Dict[str, Any]:
        return {
            "hardening_enabled": True,
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "review_required": True,
            "fail_closed_mode": True,
        }
