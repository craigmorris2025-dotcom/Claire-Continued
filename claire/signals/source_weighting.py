"""Source weighting for governed run-level signals."""

from __future__ import annotations


SOURCE_WEIGHTS = {
    "user_input": 0.72,
    "prior_claire_output": 0.70,
    "export_artifact": 0.66,
    "public_metadata": 0.62,
    "connector": 0.60,
    "unknown": 0.40,
}


def source_weight(source_type: str | None) -> float:
    key = str(source_type or "unknown").lower()
    return SOURCE_WEIGHTS.get(key, SOURCE_WEIGHTS["unknown"])
