"""
Breakthrough Engine — evaluates potential for category-defining, frontier advancement.
Consumes patent and market connector data for frontier technology validation.
"""
from typing import Any, Dict
from runtime_core.engines.base import BaseEngine


class BreakthroughEngine(BaseEngine):
    """Domain engine: breakthrough — frontier technology assessment."""

    KEYWORDS = {"advanced", "autonomous", "breakthrough", "frontier", "next-gen",
                "quantum", "sovereign", "unprecedented", "generational",
                "moonshot", "zero-to-one"}

    def get_key(self) -> str:
        return "breakthrough"

    def get_phase(self) -> str:
        return "innovation_breakthrough"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        frontier_signals = {"quantum", "autonomous", "ai-native", "self-learning",
                          "sovereign", "mesh", "neuromorphic", "photonic",
                          "fusion", "hypersonic", "directed energy"}
        scale_signals = {"10x", "100x", "exponential", "massive", "unprecedented",
                       "category-defining", "order of magnitude", "step change",
                       "generational leap", "zero to one"}
        defense_frontier = {"stealth", "electronic warfare", "cyber", "space",
                          "c4isr", "sigint", "autonomous weapons",
                          "unmanned", "counter-uas", "directed energy"}

        frontier = self._text_signal(text, frontier_signals)
        scale = self._text_signal(text, scale_signals)
        defense = self._text_signal(text, defense_frontier)
        base = self._text_signal(text, self.KEYWORDS)

        # Innovation engine cross-feed
        innovation_boost = context.get("innovation_score", 0) * 0.12

        # Patent connector: emerging areas and cliff risk
        patent = self._get_patent_data(context)
        patent_frontier_boost = 0.0
        if patent:
            emerging = patent.get("emerging_alignment", 0)
            patent_frontier_boost = min(0.10, emerging * 0.15)
            cliff = patent.get("patent_cliff_risk", "")
            if cliff == "low":
                patent_frontier_boost += 0.03

        # Market connector: sector volatility = disruption opportunity
        market = self._get_market_data(context)
        disruption_boost = 0.0
        if market:
            vol = market.get("volatility", "")
            if vol == "high":
                disruption_boost = 0.06
            elif vol == "moderate":
                disruption_boost = 0.03

        score = (frontier * 0.22 + scale * 0.18 + defense * 0.12 +
                 base * 0.15 + innovation_boost + patent_frontier_boost +
                 disruption_boost + 0.03)

        return self._score_with_detail(context, score, {
            "frontier": round(frontier, 3),
            "scale": round(scale, 3),
            "defense_frontier": round(defense, 3),
            "innovation_crossfeed": round(innovation_boost, 3),
            "patent_frontier": round(patent_frontier_boost, 3),
            "disruption_boost": round(disruption_boost, 3),
        })
