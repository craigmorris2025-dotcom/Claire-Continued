"""
Customer Engine — evaluates customer base quality, concentration, and retention.
Consumes financial connector data for customer concentration risk.
"""
from typing import Any, Dict
from backend.engines.base import BaseEngine


class CustomerEngine(BaseEngine):
    """Domain engine: customer — base quality and retention analysis."""

    KEYWORDS = {"buyer", "churn", "client", "consumer", "contract", "customer",
                "enterprise", "retention", "user", "subscriber", "account",
                "tenant", "end-user"}

    def get_key(self) -> str:
        return "customer"

    def get_phase(self) -> str:
        return "intel_scoring"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        quality_signals = {"enterprise", "fortune", "government", "federal",
                          "contract", "recurring", "long-term", "multi-year",
                          "prime contractor", "idiq", "blanket purchase"}
        retention_signals = {"retention", "loyalty", "lifetime", "renewal",
                           "expansion", "upsell", "net revenue retention",
                           "churn rate", "sticky", "embedded"}
        diversity_signals = {"diversified", "broad base", "multiple verticals",
                           "commercial", "public sector", "international"}

        quality = self._text_signal(text, quality_signals)
        retention = self._text_signal(text, retention_signals)
        diversity = self._text_signal(text, diversity_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Financial connector: customer concentration risk
        financial = self._get_financial_data(context)
        concentration_adj = 0.0
        if financial:
            conc = financial.get("customer_concentration", 0)
            # High concentration is a risk — penalize slightly
            if conc > 0.5:
                concentration_adj = -0.1
            elif conc < 0.3:
                concentration_adj = 0.05

        score = (quality * 0.25 + retention * 0.25 + diversity * 0.15 +
                 base * 0.20 + concentration_adj + 0.05)

        return self._score_with_detail(context, score, {
            "quality": round(quality, 3),
            "retention": round(retention, 3),
            "diversity": round(diversity, 3),
            "concentration_adj": round(concentration_adj, 3),
        })
