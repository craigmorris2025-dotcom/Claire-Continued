"""
FeTTiom — Feature Transformation, Temporal Integration, and Output Modeling.
Applies temporal weighting and feature transformations to engine outputs.
"""
import logging
import math
from typing import Any, Dict

logger = logging.getLogger("claire.orchestrator.fettio")


class FeTTiom:
    """Feature transformation and temporal integration."""

    TEMPORAL_WEIGHTS = {
        "ingestion_score": 1.0, "semantic_score": 1.0, "fusion_score": 0.9,
        "company_score": 0.8, "engineering_score": 0.85, "product_score": 0.85,
        "customer_score": 0.8, "competitive_score": 0.9, "operational_score": 0.75,
        "financial_score": 0.9, "synergy_score": 1.0, "strategy_score": 1.0,
        "risk_score": 0.95, "market_score": 0.95, "innovation_score": 1.1,
        "breakthrough_score": 1.15, "predictive_score": 0.9, "forecast_score": 0.85,
        "deal_score": 1.0, "decision_engine_score": 0.9, "discovery_score": 0.8,
        "acquirer_matching_score": 0.95, "portfolio_engine_score": 0.9,
        "compliance_score": 0.95,
    }

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        scores = {k: v for k, v in context.items()
                  if k.endswith("_score") and isinstance(v, (int, float))}

        transformed = {}
        for key, value in scores.items():
            weight = self.TEMPORAL_WEIGHTS.get(key, 1.0)
            # Apply sigmoid-like transformation for smoothing
            raw = value * weight
            smoothed = 1.0 / (1.0 + math.exp(-6 * (raw - 0.5)))
            transformed[key] = round(max(0.0, min(1.0, smoothed)), 4)

        context["fettio_transformed"] = transformed

        # Compute aggregate FeTTiom score
        if transformed:
            fettio_score = sum(transformed.values()) / len(transformed)
            context["fettio_aggregate"] = round(fettio_score, 4)
        else:
            context["fettio_aggregate"] = 0.0

        logger.info(f"FeTTiom: transformed {len(transformed)} scores, "
                     f"aggregate={context['fettio_aggregate']:.3f}")
        return context
