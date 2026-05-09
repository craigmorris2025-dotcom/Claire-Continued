"""
Policy Engine — compliance policy enforcement.
Defines and evaluates policies for pipeline governance.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger("claire.governance.policy")


class PolicyRule:
    """Single compliance policy rule."""

    def __init__(self, name: str, description: str, threshold: float, field: str, operator: str = "gte"):
        self.name = name
        self.description = description
        self.threshold = threshold
        self.field = field
        self.operator = operator

    def evaluate(self, scores: Dict[str, float]) -> Dict[str, Any]:
        value = scores.get(self.field, 0)
        if self.operator == "gte":
            passed = value >= self.threshold
        elif self.operator == "lte":
            passed = value <= self.threshold
        elif self.operator == "gt":
            passed = value > self.threshold
        else:
            passed = value >= self.threshold

        return {
            "rule": self.name,
            "description": self.description,
            "field": self.field,
            "value": round(value, 4),
            "threshold": self.threshold,
            "operator": self.operator,
            "passed": passed,
        }


class PolicyEngine:
    """Evaluates a set of compliance policies against pipeline results."""

    DEFAULT_POLICIES = [
        PolicyRule("minimum_confidence", "Confidence must meet minimum threshold", 0.25, "_confidence"),
        PolicyRule("decision_quality", "Decision score must be above floor", 0.10, "decision_score"),
        PolicyRule("risk_ceiling", "Risk score must not exceed ceiling", 0.90, "risk_score", "lte"),
        PolicyRule("compliance_floor", "Compliance score must meet minimum", 0.15, "compliance_score"),
        PolicyRule("semantic_validity", "Semantic score must indicate valid input", 0.05, "semantic_score"),
    ]

    def __init__(self, policies: List[PolicyRule] = None):
        self.policies = policies or self.DEFAULT_POLICIES

    def evaluate(self, scores: Dict[str, float]) -> Dict[str, Any]:
        results = []
        for policy in self.policies:
            result = policy.evaluate(scores)
            results.append(result)

        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        compliant = all(r["passed"] for r in results)

        summary = {
            "compliant": compliant,
            "passed": passed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total > 0 else 0,
            "results": results,
            "violations": [r for r in results if not r["passed"]],
        }

        logger.info(f"Policy evaluation: {passed}/{total} passed, compliant={compliant}")
        return summary
