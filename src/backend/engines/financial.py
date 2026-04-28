"""
Financial Engine — evaluates financial health, investment attractiveness, and valuation.
Consumes financial connector data for sector benchmarks and comparable transactions.
"""
from typing import Any, Dict
from backend.engines.base import BaseEngine


class FinancialEngine(BaseEngine):
    """Domain engine: financial — health and valuation analysis."""

    KEYWORDS = {"cash flow", "ebitda", "financial", "growth", "margin", "profit",
                "revenue", "roi", "valuation", "capital", "funding", "balance sheet",
                "earnings", "burn rate"}

    def get_key(self) -> str:
        return "financial"

    def get_phase(self) -> str:
        return "intel_scoring"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        health_signals = {"profitable", "revenue", "margin", "cash flow", "positive",
                         "growing", "sustainable", "cash positive", "self-funded",
                         "gross margin", "operating income"}
        attract_signals = {"undervalued", "high growth", "recurring revenue", "saas",
                         "arpu", "ltv", "net retention", "rule of 40",
                         "capital efficient", "unit economics"}
        risk_signals = {"burn rate", "cash runway", "debt", "loss", "negative",
                       "declining", "covenant"}

        health = self._text_signal(text, health_signals)
        attract = self._text_signal(text, attract_signals)
        risk_present = self._text_signal(text, risk_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Financial connector: sector valuation benchmarks
        financial = self._get_financial_data(context)
        deal_boost = 0.0
        valuation_context = {}
        if financial:
            attractiveness = financial.get("deal_attractiveness", 0)
            deal_boost = min(0.15, attractiveness * 0.2)
            valuation_context = {
                "sector_rev_multiple": financial.get("avg_revenue_multiple", 0),
                "sector_ebitda_multiple": financial.get("avg_ebitda_multiple", 0),
                "sector_gross_margin": financial.get("avg_gross_margin", 0),
            }

        score = (health * 0.25 + attract * 0.25 + base * 0.15 +
                 deal_boost - risk_present * 0.10 + 0.05)

        detail = {
            "health": round(health, 3),
            "attractiveness": round(attract, 3),
            "risk_signals": round(risk_present, 3),
            "deal_boost": round(deal_boost, 3),
        }
        detail.update(valuation_context)
        return self._score_with_detail(context, score, detail)
