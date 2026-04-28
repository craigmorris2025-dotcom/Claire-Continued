"""
Discovery Engine — identifies hidden patterns, cross-domain insights, and non-obvious opportunities.
Leverages all connector data for pattern detection across dimensions.
"""
from typing import Any, Dict, List
from backend.engines.base import BaseEngine


class DiscoveryEngine(BaseEngine):
    """Domain engine: discovery — hidden patterns and cross-domain insights."""

    KEYWORDS = {"detect", "discover", "find", "identify", "insight", "recognize",
                "reveal", "surface", "uncover", "anomaly", "correlation",
                "hidden", "non-obvious"}

    def get_key(self) -> str:
        return "discovery"

    def get_phase(self) -> str:
        return "deal_construction"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        # Cross-domain coverage (more domains = more discovery potential)
        dims = context.get("domain_scores", {})
        active_domains = sum(1 for v in dims.values() if v > 0.1) if dims else 0
        cross_domain_bonus = min(0.25, active_domains * 0.05)

        # Keyword richness
        keywords = context.get("keywords", [])
        keyword_bonus = min(0.15, len(keywords) * 0.015)

        # Signal from text
        base = self._text_signal(text, self.KEYWORDS)

        # Score divergence detection — large spread = discovery opportunity
        scores = {k: v for k, v in context.items()
                  if k.endswith("_score") and isinstance(v, (int, float))}
        outlier_bonus = 0.0
        outliers: List[str] = []
        if len(scores) > 3:
            avg = sum(scores.values()) / len(scores)
            for k, v in scores.items():
                if abs(v - avg) > 0.25:
                    outlier_bonus += 0.03
                    outliers.append(k)
            outlier_bonus = min(0.12, outlier_bonus)

        # Connector data availability enriches discovery
        connector_data = context.get("connector_data", {})
        connector_richness = sum(
            1 for v in connector_data.values()
            if isinstance(v, dict) and v.get("data")
        )
        connector_bonus = min(0.10, connector_richness * 0.04)

        score = (base * 0.20 + cross_domain_bonus + keyword_bonus +
                 outlier_bonus + connector_bonus + 0.08)

        return self._score_with_detail(context, score, {
            "active_domains": active_domains,
            "keywords_found": len(keywords),
            "outlier_engines": outliers[:5],
            "connector_richness": connector_richness,
        })
