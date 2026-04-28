"""
Fusion Engine — merges multi-source signals into a unified confidence measure.
Evaluates coherence across all prior engine scores and connector data availability.
"""
from typing import Any, Dict
from backend.engines.base import BaseEngine


class FusionEngine(BaseEngine):
    """Domain engine: fusion — cross-signal coherence and data fusion."""

    KEYWORDS = {"aggregate", "blend", "combine", "consolidate", "fusion",
                "integrate", "merge", "unify", "correlate", "synthesize"}

    def get_key(self) -> str:
        return "fusion"

    def get_phase(self) -> str:
        return "ingestion_semantic"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        scores = {k: v for k, v in context.items()
                  if k.endswith("_score") and isinstance(v, (int, float))}

        if scores:
            values = list(scores.values())
            avg = sum(values) / len(values)
            spread = max(values) - min(values) if len(values) > 1 else 0
            coherence = 1.0 - spread
            consistency = 1.0 - (sum((v - avg) ** 2 for v in values) /
                                  len(values)) ** 0.5

            # Connector data availability bonus
            connector_data = context.get("connector_data", {})
            connector_count = sum(1 for v in connector_data.values()
                                  if isinstance(v, dict) and v.get("data"))
            connector_bonus = min(0.15, connector_count * 0.05)

            score = (avg * 0.40 + coherence * 0.25 +
                     consistency * 0.20 + connector_bonus)
        else:
            score = 0.1
            coherence = 0
            connector_count = 0

        context["fusion_coherence"] = round(coherence, 4) if isinstance(coherence, float) else 0
        return self._score_with_detail(context, score, {
            "prior_scores": len(scores),
            "coherence": round(coherence, 3) if isinstance(coherence, float) else 0,
            "connectors_available": connector_count if isinstance(connector_count, int) else 0,
        })
