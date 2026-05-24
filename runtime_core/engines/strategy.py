"""
Strategy Engine — evaluates strategic alignment, growth thesis, and long-term value creation.
Consumes market connector data for sector growth and M&A trend validation.
"""
from typing import Any, Dict
from runtime_core.engines.base import BaseEngine


class StrategyEngine(BaseEngine):
    """Domain engine: strategy — alignment and growth thesis evaluation."""

    KEYWORDS = {"expansion", "growth", "initiative", "roadmap", "strategic",
                "strategy", "transformation", "vision", "thesis", "mandate",
                "objective", "priority"}

    def get_key(self) -> str:
        return "strategy"

    def get_phase(self) -> str:
        return "strategic_analysis"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        align_signals = {"aligned", "strategic fit", "core", "mission", "thesis",
                        "portfolio", "mandate", "priority", "pillar",
                        "investment thesis", "value proposition"}
        growth_signals = {"tam", "addressable market", "expansion", "new market",
                        "global", "scale", "penetration", "greenfield",
                        "whitespace", "land and expand"}
        timing_signals = {"inflection", "tipping point", "catalyst", "tailwind",
                        "secular trend", "mega trend", "structural shift"}

        align = self._text_signal(text, align_signals)
        growth = self._text_signal(text, growth_signals)
        timing = self._text_signal(text, timing_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Market connector: sector growth rate and drivers
        market = self._get_market_data(context)
        sector_boost = 0.0
        if market:
            gr = market.get("growth_rate", 0)
            sector_boost += min(0.10, gr * 0.8)
            drivers = market.get("market_drivers", [])
            driver_match = sum(1 for d in drivers
                             if isinstance(d, str) and d.lower() in text)
            sector_boost += min(0.08, driver_match * 0.04)

        score = (align * 0.25 + growth * 0.20 + timing * 0.15 +
                 base * 0.15 + sector_boost + 0.05)

        return self._score_with_detail(context, score, {
            "alignment": round(align, 3),
            "growth_thesis": round(growth, 3),
            "timing": round(timing, 3),
            "sector_boost": round(sector_boost, 3),
        })
