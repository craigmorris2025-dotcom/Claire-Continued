"""
Semantic Engine — evaluates semantic richness, domain coverage, and analytical depth.
"""
from typing import Any, Dict
from backend.engines.base import BaseEngine


class SemanticEngine(BaseEngine):
    """Domain engine: semantic — measures NLP domain coverage."""

    KEYWORDS = {"context", "interpret", "language", "meaning", "model",
                "nlp", "representation", "semantic", "understand",
                "classify", "entity", "sentiment", "taxonomy"}

    def get_key(self) -> str:
        return "semantic"

    def get_phase(self) -> str:
        return "ingestion_semantic"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        dims = context.get("domain_scores", {})
        if not dims:
            dims = context.get("semantic_dimensions", {})

        if dims:
            max_dim = max(dims.values()) if dims else 0
            avg_dim = sum(dims.values()) / len(dims) if dims else 0
            active_domains = sum(1 for v in dims.values() if v > 0.05)
            coverage = active_domains / max(len(dims), 1)

            # Concentration penalty — pure single-domain input gets slight penalty
            concentration = max_dim - avg_dim if len(dims) > 1 else 0
            diversity_bonus = min(0.15, active_domains * 0.03)

            score = (max_dim * 0.30 + avg_dim * 0.20 +
                     coverage * 0.25 + diversity_bonus +
                     0.05 - concentration * 0.05)
        else:
            signal = self._text_signal(context.get("raw_input", ""), self.KEYWORDS)
            score = signal * 0.5 + 0.05
            active_domains = 0
            max_dim = 0
            coverage = 0

        context["semantic_richness"] = round(self._clamp(score), 4)
        return self._score_with_detail(context, score, {
            "domains_active": active_domains,
            "max_dimension": round(max_dim, 3) if isinstance(max_dim, float) else max_dim,
            "coverage": round(coverage, 3) if isinstance(coverage, float) else coverage,
            "primary_domain": context.get("primary_domain", "unknown"),
        })
