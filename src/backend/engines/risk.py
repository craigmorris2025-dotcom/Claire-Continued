"""
Risk Engine — comprehensive risk assessment across regulatory, operational, and market dimensions.
Consumes all three connector data sources for multi-dimensional risk analysis.
Higher score = lower risk (risk-adjusted confidence).
"""
from typing import Any, Dict
from backend.engines.base import BaseEngine


class RiskEngine(BaseEngine):
    """Domain engine: risk — multi-dimensional risk assessment."""

    KEYWORDS = {"compliance", "exposure", "liability", "litigation", "regulatory",
                "risk", "threat", "vulnerability", "cybersecurity", "geopolitical",
                "concentration", "dependency"}

    def get_key(self) -> str:
        return "risk"

    def get_phase(self) -> str:
        return "strategic_analysis"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        risk_signals = {"risk", "threat", "vulnerability", "lawsuit", "litigation",
                       "regulatory", "investigation", "sanction", "embargo",
                       "breach", "failure", "default", "bankruptcy"}
        mitigation_signals = {"compliant", "certified", "insured", "audited",
                            "secure", "protected", "redundant", "resilient",
                            "iso 27001", "soc 2", "fedramp", "cmmc"}
        concentration_signals = {"single customer", "sole source", "key person",
                               "dependency", "concentration", "single point"}

        risk_present = self._text_signal(text, risk_signals)
        mitigation = self._text_signal(text, mitigation_signals)
        concentration = self._text_signal(text, concentration_signals)

        base_risk = 0.55  # neutral baseline

        # Market connector: regulatory posture and headwinds
        market = self._get_market_data(context)
        regulatory_adj = 0.0
        headwind_adj = 0.0
        if market:
            reg = market.get("regulatory_posture", {})
            if isinstance(reg, dict):
                itar = reg.get("itar_controlled", False)
                cfius = reg.get("cfius_review", "")
                if itar:
                    regulatory_adj -= 0.05  # ITAR adds complexity
                if cfius == "mandatory":
                    regulatory_adj -= 0.05
            headwinds = market.get("headwinds", [])
            headwind_adj = -min(0.10, len(headwinds) * 0.03)

        # Patent connector: litigation rate
        patent = self._get_patent_data(context)
        litigation_adj = 0.0
        if patent:
            lit_rate = patent.get("litigation_rate", 0)
            if lit_rate > 0.05:
                litigation_adj = -0.08
            elif lit_rate < 0.02:
                litigation_adj = 0.03

        # Financial connector: debt and risk factors
        financial = self._get_financial_data(context)
        financial_risk_adj = 0.0
        if financial:
            de = financial.get("avg_debt_equity", 1.0)
            if de > 2.0:
                financial_risk_adj = -0.08
            elif de < 0.5:
                financial_risk_adj = 0.05
            book_to_bill = financial.get("book_to_bill", 1.0)
            if book_to_bill > 1.1:
                financial_risk_adj += 0.03

        score = (base_risk + mitigation * 0.25 - risk_present * 0.15 -
                 concentration * 0.10 + regulatory_adj + headwind_adj +
                 litigation_adj + financial_risk_adj)

        return self._score_with_detail(context, score, {
            "risk_signals": round(risk_present, 3),
            "mitigation": round(mitigation, 3),
            "concentration_risk": round(concentration, 3),
            "regulatory_adj": round(regulatory_adj, 3),
            "headwind_adj": round(headwind_adj, 3),
            "litigation_adj": round(litigation_adj, 3),
            "financial_risk_adj": round(financial_risk_adj, 3),
        })
