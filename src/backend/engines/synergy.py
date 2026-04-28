"""
Synergy Engine — evaluates integration potential, synergy value, and acquirer complementarity.
Consumes market and financial connector data for synergy validation.
"""
from typing import Any, Dict
from backend.engines.base import BaseEngine


class SynergyEngine(BaseEngine):
    """Domain engine: synergy — integration potential and value creation."""

    KEYWORDS = {"align", "combined", "complement", "consolidate", "cross-sell",
                "fit", "integration", "merge", "synergy", "accretive",
                "bolt-on", "tuck-in"}

    def get_key(self) -> str:
        return "synergy"

    def get_phase(self) -> str:
        return "strategic_analysis"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        integration_signals = {"complementary", "adjacent", "plug-in", "bolt-on",
                              "tuck-in", "horizontal", "vertical", "platform play",
                              "add-on", "extension", "modular"}
        value_signals = {"cost savings", "revenue synergy", "cross-sell", "shared",
                        "combined", "economies", "eliminate redundancy",
                        "shared services", "back-office", "distribution"}
        strategic_signals = {"portfolio gap", "capability gap", "white space",
                           "adjacency", "new market", "new channel",
                           "geographic expansion", "product extension"}

        integ = self._text_signal(text, integration_signals)
        value = self._text_signal(text, value_signals)
        strategic = self._text_signal(text, strategic_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Domain alignment from semantic layer
        domain_boost = max(context.get("domain_scores", {}).values(), default=0) * 0.10

        # Market connector: sector M&A activity validates synergy thesis
        market = self._get_market_data(context)
        ma_boost = 0.0
        if market:
            deals = market.get("recent_deals", [])
            if len(deals) >= 3:
                ma_boost = 0.08
            timing = market.get("market_timing_signal", 0)
            ma_boost += min(0.07, timing * 0.1)

        # Financial connector: deal premium benchmarks
        financial = self._get_financial_data(context)
        premium_adj = 0.0
        if financial:
            premium = financial.get("avg_deal_premium", 0)
            if 0.2 < premium < 0.5:
                premium_adj = 0.05  # reasonable premium range

        score = (integ * 0.20 + value * 0.20 + strategic * 0.15 +
                 base * 0.15 + domain_boost + ma_boost + premium_adj)

        return self._score_with_detail(context, score, {
            "integration": round(integ, 3),
            "value_creation": round(value, 3),
            "strategic_fit": round(strategic, 3),
            "domain_boost": round(domain_boost, 3),
            "ma_activity_boost": round(ma_boost, 3),
        })
