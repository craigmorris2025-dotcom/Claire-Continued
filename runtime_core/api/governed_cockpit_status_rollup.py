from __future__ import annotations

from typing import Dict


def get_cockpit_status_rollup() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S212-S218",
        "overall_state": "governed_operational_ready",
        "internet_connectivity_state": "operator_controlled_bounded_ready",
        "dashboard_state": "payload_consumable",
        "review_state": "manual_required",
        "update_state": "proposal_only",
        "mutation_state": "blocked",
        "autonomy_state": "blocked",
        "safe_to_continue_builds": True,
        "requires_full_pytest_for_plateau": True,
    }
