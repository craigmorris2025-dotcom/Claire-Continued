from __future__ import annotations

from typing import Dict, List


def get_card_state_normalizer_contract() -> Dict[str, object]:
    states: List[Dict[str, object]] = [
        {"state": "ready", "display": "Ready", "operator_action_allowed": True},
        {"state": "pending_review", "display": "Review Required", "operator_action_allowed": True},
        {"state": "proposal_only", "display": "Proposal Only", "operator_action_allowed": True},
        {"state": "quarantined", "display": "Quarantined", "operator_action_allowed": True},
        {"state": "blocked", "display": "Blocked", "operator_action_allowed": False},
        {"state": "read_only", "display": "Read Only", "operator_action_allowed": False},
        {"state": "unavailable", "display": "Unavailable", "operator_action_allowed": False},
    ]
    return {
        "version": "v19.89.8-S226-S232",
        "normalized_states": states,
        "rule": "Frontend must use normalized states rather than inventing button status locally.",
    }
