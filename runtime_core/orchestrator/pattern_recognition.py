"""
Pattern Recognition — identifies cross-engine signal patterns.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger("claire.orchestrator.patterns")


class PatternRecognizer:
    """Detects patterns across engine outputs."""

    CLUSTER_THRESHOLDS = {"strong": 0.6, "moderate": 0.3}

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        scores = {k: v for k, v in context.items()
                  if k.endswith("_score") and isinstance(v, (int, float))}

        patterns = {
            "strong_signals": [k for k, v in scores.items() if v >= self.CLUSTER_THRESHOLDS["strong"]],
            "moderate_signals": [k for k, v in scores.items()
                                 if self.CLUSTER_THRESHOLDS["moderate"] <= v < self.CLUSTER_THRESHOLDS["strong"]],
            "weak_signals": [k for k, v in scores.items() if v < self.CLUSTER_THRESHOLDS["moderate"]],
        }

        # Detect cross-domain clusters
        clusters = self._detect_clusters(scores)
        patterns["clusters"] = clusters

        # Signal coherence
        values = list(scores.values())
        if values:
            avg = sum(values) / len(values)
            variance = sum((v - avg) ** 2 for v in values) / len(values)
            patterns["coherence"] = round(1.0 - min(1.0, variance * 4), 4)
            patterns["avg_signal"] = round(avg, 4)
        else:
            patterns["coherence"] = 0
            patterns["avg_signal"] = 0

        context["patterns"] = patterns
        logger.info(f"Patterns: {len(patterns['strong_signals'])} strong, "
                     f"{len(patterns['moderate_signals'])} moderate, coherence={patterns['coherence']}")
        return context

    def _detect_clusters(self, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        clusters = []
        # Strategic cluster
        strat_keys = ["synergy_score", "strategy_score", "market_score", "deal_score"]
        strat_vals = [scores.get(k, 0) for k in strat_keys]
        if strat_vals:
            clusters.append({
                "name": "strategic_alignment",
                "avg": round(sum(strat_vals) / len(strat_vals), 4),
                "components": strat_keys,
            })
        # Innovation cluster
        inno_keys = ["innovation_score", "breakthrough_score", "predictive_score", "forecast_score"]
        inno_vals = [scores.get(k, 0) for k in inno_keys]
        if inno_vals:
            clusters.append({
                "name": "innovation_potential",
                "avg": round(sum(inno_vals) / len(inno_vals), 4),
                "components": inno_keys,
            })
        # Operational cluster
        ops_keys = ["company_score", "engineering_score", "operational_score", "financial_score"]
        ops_vals = [scores.get(k, 0) for k in ops_keys]
        if ops_vals:
            clusters.append({
                "name": "operational_strength",
                "avg": round(sum(ops_vals) / len(ops_vals), 4),
                "components": ops_keys,
            })
        return clusters
