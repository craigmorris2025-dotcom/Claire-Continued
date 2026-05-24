"""
Forecasting Engine — generates forward-looking growth projections and trajectory analysis.
Consumes market and financial connector data for growth forecasting.
"""
from typing import Any, Dict
from runtime_core.engines.base import BaseEngine


class ForecastingEngine(BaseEngine):
    """Domain engine: forecasting — growth trajectory projection."""

    KEYWORDS = {"compound", "forecast", "growth rate", "outlook", "projection",
                "trajectory", "trend", "future", "cagr", "runway",
                "momentum", "acceleration"}

    def get_key(self) -> str:
        return "forecasting"

    def get_phase(self) -> str:
        return "innovation_breakthrough"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        growth_signals = {"growing", "accelerating", "expanding", "scaling",
                        "compound", "trajectory", "hockey stick", "inflection",
                        "doubling", "tripling", "rapid growth"}
        stability_signals = {"consistent", "stable", "recurring", "predictable",
                           "sustainable", "durable", "resilient",
                           "counter-cyclical", "non-discretionary"}
        risk_signals = {"cyclical", "volatile", "seasonal", "dependent",
                       "uncertain", "speculative", "unproven"}

        growth = self._text_signal(text, growth_signals)
        stability = self._text_signal(text, stability_signals)
        risk = self._text_signal(text, risk_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Market connector: sector growth rate is primary forecast input
        market = self._get_market_data(context)
        market_boost = 0.0
        sector_growth = 0.0
        if market:
            sector_growth = market.get("growth_rate", 0)
            market_boost += min(0.12, sector_growth * 0.8)
            timing = market.get("market_timing_signal", 0)
            market_boost += min(0.05, timing * 0.08)

        # Financial connector: revenue growth and R&D spend
        financial = self._get_financial_data(context)
        financial_boost = 0.0
        if financial:
            rd = financial.get("avg_rd_spend_pct", 0)
            if rd > 0.15:
                financial_boost = 0.06
            elif rd > 0.08:
                financial_boost = 0.03
            book = financial.get("book_to_bill", 1.0)
            if book > 1.1:
                financial_boost += 0.04

        score = (growth * 0.22 + stability * 0.18 + base * 0.12 +
                 market_boost + financial_boost - risk * 0.08 + 0.05)

        return self._score_with_detail(context, score, {
            "growth_signals": round(growth, 3),
            "stability": round(stability, 3),
            "risk": round(risk, 3),
            "sector_growth": round(sector_growth, 3),
            "market_boost": round(market_boost, 3),
            "financial_boost": round(financial_boost, 3),
        })
