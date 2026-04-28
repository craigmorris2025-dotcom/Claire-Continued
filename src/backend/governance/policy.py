"""
Policy Engine — enforces business rules and compliance constraints.
Validates pipeline outputs against configurable policy rules.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger("claire.governance.policy")


# Default policy rules
DEFAULT_POLICIES = [
    {
        "id": "min_confidence",
        "name": "Minimum Confidence",
        "description": "All pipeline outputs must meet minimum confidence threshold",
        "check": lambda scores: scores.get("_confidence", 0) >= 0.10,
        "severity": "warning",
    },
    {
        "id": "score_bounds",
        "name": "Score Bounds",
        "description": "All scores must be within 0.0-1.0 range",
        "check": lambda scores: all(0 <= v <= 1 for v in scores.values() if isinstance(v, (int, float))),
        "severity": "error",
    },
    {
        "id": "min_engines",
        "name": "Minimum Engine Coverage",
        "description": "At least 12 engines must produce scores",
        "check": lambda scores: len([k for k in scores if k.endswith("_score")]) >= 12,
        "severity": "warning",
    },
    {
        "id": "decision_present",
        "name": "Decision Score Present",
        "description": "Pipeline must produce a decision_score",
        "check": lambda scores: "decision_score" in scores,
        "severity": "error",
    },
]


class PolicyEngine:
    """Evaluates pipeline output against governance policies."""

    def __init__(self, policies: List[Dict] = None):
        self.policies = policies or DEFAULT_POLICIES

    def evaluate(self, scores: Dict[str, float],
                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        results = []
        passed = 0
        warnings = 0
        errors = 0

        for policy in self.policies:
            try:
                ok = policy["check"](scores)
                result = {
                    "id": policy["id"],
                    "name": policy["name"],
                    "passed": ok,
                    "severity": policy["severity"],
                }
                if ok:
                    passed += 1
                elif policy["severity"] == "error":
                    errors += 1
                else:
                    warnings += 1
                results.append(result)
            except Exception as e:
                results.append({
                    "id": policy["id"],
                    "name": policy["name"],
                    "passed": False,
                    "severity": "error",
                    "error": str(e),
                })
                errors += 1

        compliant = errors == 0
        return {
            "compliant": compliant,
            "passed": passed,
            "warnings": warnings,
            "errors": errors,
            "total": len(self.policies),
            "results": results,
        }

    def add_policy(self, policy_id: str, name: str, check_fn, severity: str = "warning"):
        self.policies.append({
            "id": policy_id, "name": name,
            "check": check_fn, "severity": severity,
            "description": name,
        })
