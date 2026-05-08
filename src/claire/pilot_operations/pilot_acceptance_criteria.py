from __future__ import annotations
from typing import Any, Dict

class PilotAcceptanceCriteria:
    REQUIRED = {
        "operator_review_count": 5,
        "benchmark_replay_count": 5,
        "accepted_output_count": 3,
        "critical_false_positive_count": 0,
    }

    def evaluate(self, evidence: Dict[str, int]) -> Dict[str, Any]:
        failures = []
        for key, required in self.REQUIRED.items():
            actual = int(evidence.get(key, 0))
            if key == "critical_false_positive_count":
                passed = actual <= required
            else:
                passed = actual >= required
            if not passed:
                failures.append({"metric": key, "required": required, "actual": actual})
        return {"status": "pass" if not failures else "blocked", "failures": failures}
