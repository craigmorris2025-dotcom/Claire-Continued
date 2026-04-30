"""
Interpreter — Intent parsing and response finalization.
Bridges the CLAIRE cognitive layers with the processing core.
"""
import logging
from typing import Any, Dict
logger = logging.getLogger("claire.interpreter")
from claire.domain.contract import ClaireIntent, ClaireResult

class Interpreter:
    """Interprets pipeline results and finalizes the CLAIRE response."""

    DECISION_THRESHOLDS = {"GO": 0.65, "CAUTION": 0.35}
    BREAKTHROUGH_THRESHOLDS = {"HIGH": 0.7, "MODERATE": 0.4}

    def classify_decision(self, score: float) -> str:
        if score >= self.DECISION_THRESHOLDS["GO"]:
            return "GO"
        elif score >= self.DECISION_THRESHOLDS["CAUTION"]:
            return "CAUTION"
        return "NO-GO"

    def classify_breakthrough(self, score: float) -> str:
        if score >= self.BREAKTHROUGH_THRESHOLDS["HIGH"]:
            return "HIGH-BREAKTHROUGH"
        elif score >= self.BREAKTHROUGH_THRESHOLDS["MODERATE"]:
            return "MODERATE"
        return "LOW"

    def finalize(self, result: ClaireResult) -> ClaireResult:
        """Apply classifications, set readiness, finalize the result."""
        ds = result.scores.get("decision_score", 0)
        bs = result.scores.get("breakthrough_score", 0)
        ps = result.scores.get("portfolio_score", 0)

        result.decision_classification = self.classify_decision(ds)
        result.breakthrough_classification = self.classify_breakthrough(bs)

        # Ready for Syntalion if GO or HIGH-BREAKTHROUGH
        result.ready_for_syntalion = (
            result.decision_classification == "GO" or
            result.breakthrough_classification == "HIGH-BREAKTHROUGH"
        )

        # Compliance summary
        result.compliance = {
            "decision_class": result.decision_classification,
            "breakthrough_class": result.breakthrough_classification,
            "portfolio_score": round(ps, 4),
            "syntalion_ready": result.ready_for_syntalion,
            "confidence": result.semantic.confidence if result.semantic else 0,
        }

        logger.info(
            f"Finalized {result.intent_id}: decision={result.decision_classification} "
            f"breakthrough={result.breakthrough_classification} syntalion_ready={result.ready_for_syntalion}"
        )
        return result
