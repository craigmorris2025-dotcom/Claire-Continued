"""
Market Engine — evaluates market opportunity, timing, and sector dynamics.
Primary consumer of market connector data for sector intelligence.
"""
from typing import Any, Dict
from claire.engines.base import BaseEngine


class MarketEngine(BaseEngine):
    """Domain engine: market — opportunity and timing assessment."""

    KEYWORDS = {"addressable", "demand", "industry", "landscape", "market",
                "opportunity", "sector", "tam", "trend", "segment",
                "penetration", "share"}

    def get_key(self) -> str:
        return "market"

    def get_phase(self) -> str:
        return "strategic_analysis"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        opportunity_signals = {"growing", "emerging", "underserved", "untapped",
                             "expanding", "booming", "massive", "trillion",
                             "billion dollar", "greenfield", "whitespace"}
        timing_signals = {"early", "first mover", "inflection", "tipping point",
                        "adoption", "mainstream", "catalyst", "inflection point",
                        "wave", "cycle"}
        maturity_signals = {"mature", "consolidating", "saturated", "commoditized",
                          "declining", "disrupted", "legacy"}

        opp = self._text_signal(text, opportunity_signals)
        timing = self._text_signal(text, timing_signals)
        maturity_risk = self._text_signal(text, maturity_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Market connector: comprehensive sector intelligence
        market = self._get_market_data(context)
        connector_boost = 0.0
        sector_detail = {}
        if market:
            gr = market.get("growth_rate", 0)
            connector_boost += min(0.12, gr * 0.8)
            driver_align = market.get("driver_alignment", 0)
            connector_boost += min(0.08, driver_align * 0.12)
            timing_sig = market.get("market_timing_signal", 0)
            connector_boost += min(0.05, timing_sig * 0.08)
            sector_detail = {
                "sector": market.get("sector", ""),
                "growth_rate": gr,
                "volatility": market.get("volatility", ""),
                "market_cap_b": market.get("total_market_cap_b", 0),
                "avg_deal_size_m": market.get("avg_deal_size_m", 0),
            }

        score = (opp * 0.25 + timing * 0.20 + base * 0.15 +
                 connector_boost - maturity_risk * 0.10 + 0.05)

        detail = {
            "opportunity": round(opp, 3),
            "timing": round(timing, 3),
            "maturity_risk": round(maturity_risk, 3),
            "connector_boost": round(connector_boost, 3),
        }
        detail.update(sector_detail)
        return self._score_with_detail(context, score, detail)
