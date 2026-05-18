from datetime import datetime
from typing import Any, Dict, List
import uuid


class GovernedLiveSearchSessionLifecycle:
    VALID_STATES = [
        "initialized",
        "authorized",
        "executing",
        "review_pending",
        "completed",
        "blocked",
        "failed",
    ]

    def __init__(self) -> None:
        self.lifecycle_version = "v18.42"
        self.fail_closed = True

    def create_session(self, query: str) -> Dict[str, Any]:
        return {
            "session_id": f"search-session-{uuid.uuid4().hex[:8]}",
            "query": query,
            "state": "initialized",
            "created_utc": datetime.utcnow().isoformat() + "Z",
            "events": [
                {
                    "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                    "event": "session_initialized",
                }
            ],
            "governance_state": self.governance_state(),
        }

    def transition_state(
        self,
        session: Dict[str, Any],
        new_state: str,
    ) -> Dict[str, Any]:

        if new_state not in self.VALID_STATES:
            raise ValueError(f"invalid_state:{new_state}")

        updated = dict(session)

        updated["state"] = new_state

        events: List[Dict[str, Any]] = list(
            updated.get("events", [])
        )

        events.append(
            {
                "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                "event": f"state_transition:{new_state}",
            }
        )

        updated["events"] = events
        updated["governance_state"] = self.governance_state()

        return updated

    def governance_state(self) -> Dict[str, Any]:
        return {
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "review_gate_enforced": True,
            "session_lifecycle_tracking_enabled": True,
            "fail_closed_mode": True,
        }
