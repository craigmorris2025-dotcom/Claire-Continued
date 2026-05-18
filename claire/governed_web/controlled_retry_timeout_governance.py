from datetime import datetime
from typing import Any, Dict, List


class ControlledSearchRetryTimeoutGovernance:
    def __init__(
        self,
        max_retries: int = 2,
        timeout_seconds: int = 10,
    ) -> None:
        self.governance_version = "v18.47"
        self.max_retries = max(0, int(max_retries))
        self.timeout_seconds = max(1, int(timeout_seconds))
        self.fail_closed = True

    def build_retry_plan(
        self,
        query: str,
        provider: str = "controlled_provider",
    ) -> Dict[str, Any]:

        attempts: List[Dict[str, Any]] = []

        for index in range(self.max_retries + 1):
            attempts.append(
                {
                    "attempt_number": index + 1,
                    "provider": provider,
                    "timeout_seconds": self.timeout_seconds,
                    "allowed": True,
                    "body_fetch_unbounded": False,
                    "runtime_truth_mutation": False,
                }
            )

        return {
            "governance_version": self.governance_version,
            "created_utc": datetime.utcnow().isoformat() + "Z",
            "query": query,
            "provider": provider,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "attempt_count": len(attempts),
            "attempts": attempts,
            "governance_state": self.governance_state(),
        }

    def build_timeout_result(
        self,
        query: str,
        provider: str,
        attempt_number: int,
    ) -> Dict[str, Any]:

        return {
            "governance_version": self.governance_version,
            "created_utc": datetime.utcnow().isoformat() + "Z",
            "query": query,
            "provider": provider,
            "attempt_number": attempt_number,
            "status": "timeout",
            "retry_allowed": attempt_number <= self.max_retries,
            "review_required": True,
            "governance_state": self.governance_state(),
        }

    def governance_state(self) -> Dict[str, Any]:
        return {
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "review_gate_enforced": True,
            "retry_governance_enabled": True,
            "timeout_governance_enabled": True,
            "fail_closed_mode": True,
        }
