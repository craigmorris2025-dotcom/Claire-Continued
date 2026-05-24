"""
Score Calibrator — normalizes all scores to 0-1, applies weighted averages.
"""
import logging
from typing import Any, Dict

logger = logging.getLogger("claire.scoring.calibrator")

SCORE_WEIGHTS = {
    "synergy_score": 0.10, "strategy_score": 0.12, "risk_score": 0.08,
    "market_score": 0.08, "innovation_score": 0.10, "breakthrough_score": 0.12,
    "deal_score": 0.08, "decision_score": 0.00, "portfolio_score": 0.00,
    "forecast_score": 0.06, "predictive_score": 0.06, "semantic_score": 0.08,
    "ingestion_score": 0.04, "company_score": 0.02, "engineering_score": 0.02,
    "product_score": 0.02, "customer_score": 0.02,
}


class ScoreCalibrator:
    """Normalizes, weights, and derives composite scores."""

    def calibrate(self, raw_scores: Dict[str, float]) -> Dict[str, float]:
        calibrated = {}
        for key, value in raw_scores.items():
            calibrated[key] = round(max(0.0, min(1.0, value)), 4)

        # Weighted decision score
        weighted_sum = 0.0
        weight_total = 0.0
        for key, weight in SCORE_WEIGHTS.items():
            if key in calibrated and weight > 0:
                weighted_sum += calibrated[key] * weight
                weight_total += weight
        if weight_total > 0:
            calibrated["decision_score"] = round(weighted_sum / weight_total, 4)
        else:
            calibrated["decision_score"] = 0.0

        # Portfolio = blend of decision + breakthrough + synergy
        ds = calibrated.get("decision_score", 0)
        bs = calibrated.get("breakthrough_score", 0)
        ss = calibrated.get("synergy_score", 0)
        calibrated["portfolio_score"] = round(ds * 0.4 + bs * 0.35 + ss * 0.25, 4)

        # Confidence = semantic confidence mapped to score
        sem = calibrated.get("semantic_score", 0)
        ing = calibrated.get("ingestion_score", 0)
        calibrated["_confidence"] = round(min(1.0, (sem + ing) / 2 + 0.15), 4)

        logger.info(f"Calibrated {len(calibrated)} scores, decision={calibrated['decision_score']:.3f}")
        return calibrated
