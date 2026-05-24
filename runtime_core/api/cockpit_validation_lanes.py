from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


LOCKED_AUTHORITY = {
    "runtime_truth_write": False,
    "runtime_mutation": False,
    "automatic_updates": False,
    "autonomous_execution": False,
    "continuous_crawling": False,
}


@dataclass(frozen=True)
class ValidationLane:
    lane_id: str
    label: str
    purpose: str
    recommended_command: str
    use_case: str
    allowed_for_forward_motion: bool
    plateau_required: bool


def get_validation_lanes() -> Dict[str, object]:
    lanes: List[ValidationLane] = [
        ValidationLane(
            lane_id="fast_smoke",
            label="Fast Smoke Gate",
            purpose="Check importability and critical cockpit contracts before a full suite.",
            recommended_command="pytest tests/test_s191_s197_cockpit_validation_lanes.py -q",
            use_case="Use after small additive cockpit/backend contract installers.",
            allowed_for_forward_motion=True,
            plateau_required=False,
        ),
        ValidationLane(
            lane_id="contract_pack",
            label="Contract Pack Gate",
            purpose="Run focused tests for cockpit contracts, monitoring, review, and governance locks.",
            recommended_command="pytest tests/test_s191_s197_cockpit_validation_lanes.py tests/test_s191_s197_operator_control_safety.py -q",
            use_case="Use during multi-stage packs when touched surfaces are known.",
            allowed_for_forward_motion=True,
            plateau_required=False,
        ),
        ValidationLane(
            lane_id="full_pytest",
            label="Full Pytest Plateau Gate",
            purpose="Run the entire project test suite before declaring a plateau stable.",
            recommended_command="pytest",
            use_case="Mandatory after broad shared-contract packs and at every plateau.",
            allowed_for_forward_motion=True,
            plateau_required=True,
        ),
    ]
    return {
        "version": "v19.89.8-S191-S197",
        "authority_locks": dict(LOCKED_AUTHORITY),
        "lanes": [asdict(lane) for lane in lanes],
        "rule": "Fast lanes may reduce iteration time, but full pytest remains the plateau truth gate.",
    }
