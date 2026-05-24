"""
Competitive Engine — evaluates competitive positioning, moat strength, and market share.
Consumes patent and market connector data for competitive landscape intelligence.
"""
from typing import Any, Dict
from runtime_core.engines.base import BaseEngine


class CompetitiveEngine(BaseEngine):
    """Domain engine: competitive — moat strength and positioning."""

    KEYWORDS = {"advantage", "barrier", "competitive", "competitor", "leader",
                "market share", "moat", "position", "dominance", "defensible",
                "switching cost"}

    def get_key(self) -> str:
        return "competitive"

    def get_phase(self) -> str:
        return "intel_scoring"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        moat_signals = {"patent", "proprietary", "exclusive", "first mover",
                       "network effect", "switching cost", "lock-in", "ecosystem",
                       "certification", "security clearance", "fips", "itar"}
        position_signals = {"leader", "dominant", "top", "leading", "best-in-class",
                          "category", "market leader", "pioneer", "incumbent",
                          "trusted", "established"}

        moat = self._text_signal(text, moat_signals)
        position = self._text_signal(text, position_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Patent connector: key holders and patent density = competitive moat
        patent = self._get_patent_data(context)
        ip_moat_boost = 0.0
        if patent:
            density = patent.get("patent_density", 0)
            freedom = patent.get("freedom_to_operate", 0)
            ip_moat_boost = min(0.15, density * 0.1 + freedom * 0.08)

        # Market connector: market concentration and segment leadership
        market = self._get_market_data(context)
        market_position_boost = 0.0
        if market:
            driver_align = market.get("driver_alignment", 0)
            market_position_boost = min(0.1, driver_align * 0.15)

        score = (moat * 0.25 + position * 0.20 + base * 0.15 +
                 ip_moat_boost + market_position_boost + 0.05)

        return self._score_with_detail(context, score, {
            "moat": round(moat, 3),
            "position": round(position, 3),
            "ip_moat_boost": round(ip_moat_boost, 3),
            "market_position_boost": round(market_position_boost, 3),
        })
