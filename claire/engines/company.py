"""
Company Engine — evaluates target company profile, maturity, and sector positioning.
Consumes market connector data for sector benchmarking.
"""
from typing import Any, Dict
from claire.engines.base import BaseEngine


class CompanyEngine(BaseEngine):
    """Domain engine: company — target profile and maturity assessment."""

    KEYWORDS = {"business", "company", "corporation", "enterprise", "firm",
                "organization", "startup", "venture", "conglomerate",
                "subsidiary", "division", "portfolio company"}

    def get_key(self) -> str:
        return "company"

    def get_phase(self) -> str:
        return "intel_scoring"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        maturity_signals = {"established", "growth", "revenue", "profitable",
                           "funded", "series", "public", "ipo", "mature",
                           "track record", "proven", "decades"}
        scale_signals = {"global", "enterprise", "fortune", "billion", "million",
                        "employees", "multinational", "nationwide", "international",
                        "headcount", "workforce", "offices"}
        defense_signals = {"cleared", "classified", "dod", "federal", "government",
                          "military", "defense", "intelligence", "nato"}

        maturity = self._text_signal(text, maturity_signals)
        scale = self._text_signal(text, scale_signals)
        defense_fit = self._text_signal(text, defense_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Market connector: sector market cap informs company scale context
        market = self._get_market_data(context)
        market_boost = 0.0
        sector_context = ""
        if market:
            mc = market.get("total_market_cap_b", 0)
            if mc > 500:
                market_boost = 0.1
            elif mc > 100:
                market_boost = 0.05
            sector_context = market.get("sector", "")

        score = (maturity * 0.25 + scale * 0.20 + defense_fit * 0.15 +
                 base * 0.20 + market_boost + 0.05)

        return self._score_with_detail(context, score, {
            "maturity": round(maturity, 3),
            "scale": round(scale, 3),
            "defense_fit": round(defense_fit, 3),
            "market_boost": round(market_boost, 3),
            "sector_context": sector_context,
        })
