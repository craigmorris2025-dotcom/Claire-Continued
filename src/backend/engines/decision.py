"""
Decision Engine — synthesizes all engine signals into a weighted go/no-go recommendation.
Uses calibrated cross-engine analysis for final decision intelligence.
"""
from typing import Any, Dict, List, Tuple
from backend.engines.base import BaseEngine


class DecisionEngine(BaseEngine):
    """Domain engine: decision — final synthesis and recommendation."""

    KEYWORDS = {"assessment", "conclusion", "decision", "determine", "evaluate",
                "judgment", "recommend", "verdict", "go/no-go", "thesis",
                "conviction"}

    # Tier weights — strategic engines matter more for decision
    TIER_WEIGHTS = {
        "strategy_score": 1.3,
        "market_score": 1.2,
        "financial_score": 1.2,
        "risk_score": 1.3,
        "innovation_score": 1.1,
        "deal_score": 1.2,
        "synergy_score": 1.1,
        "competitive_score": 1.1,
        "breakthrough_score": 1.0,
        "company_score": 1.0,
        "customer_score": 1.0,
        "engineering_score": 1.0,
        "product_score": 1.0,
        "operational_score": 0.9,
        "compliance_score": 1.1,
    }

    def get_key(self) -> str:
        return "decision"

    def get_phase(self) -> str:
        return "deal_construction"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Collect all engine scores with tier weighting
        weighted_scores: List[Tuple[str, float]] = []
        raw_scores: List[float] = []

        for key, val in context.items():
            if (key.endswith("_score") and isinstance(val, (int, float))
                    and key not in ("decision_engine_score", "decision_score")):
                weight = self.TIER_WEIGHTS.get(key, 1.0)
                weighted_scores.append((key, val * weight))
                raw_scores.append(val)

        if weighted_scores:
            # Weighted average
            total_weight = sum(w for _, w in weighted_scores)
            weighted_avg = total_weight / len(weighted_scores)

            # Top-5 average (strongest signals)
            top5 = sorted(raw_scores, reverse=True)[:5]
            top5_avg = sum(top5) / len(top5) if top5 else 0

            # Bottom-3 average (weakest signals = risk)
            bottom3 = sorted(raw_scores)[:3]
            bottom3_avg = sum(bottom3) / len(bottom3) if bottom3 else 0

            # Spread analysis
            spread = max(raw_scores) - min(raw_scores)
            consistency = 1.0 - min(1.0, spread)

            # Composite decision score
            score = (weighted_avg * 0.40 + top5_avg * 0.25 +
                     bottom3_avg * 0.15 + consistency * 0.10 + 0.05)
        else:
            score = 0.1
            weighted_avg = 0
            top5_avg = 0
            bottom3_avg = 0
            consistency = 0

        context["decision_engine_score"] = round(self._clamp(score), 4)
        return self._score_with_detail(context, score, {
            "engines_analyzed": len(weighted_scores),
            "weighted_average": round(weighted_avg, 3),
            "top5_average": round(top5_avg, 3),
            "bottom3_average": round(bottom3_avg, 3),
            "consistency": round(consistency, 3),
        })
