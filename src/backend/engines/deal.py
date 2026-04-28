"""
Deal Engine — evaluates deal structure feasibility, attractiveness, and execution risk.
Primary consumer of financial connector data for comparable transactions and valuation.
"""
from typing import Any, Dict
from backend.engines.base import BaseEngine


class DealEngine(BaseEngine):
    """Domain engine: deal — structure feasibility and attractiveness."""

    KEYWORDS = {"acquisition", "buyout", "deal", "investment", "lbo", "merger",
                "offer", "takeover", "transaction", "carve-out", "spin-off",
                "joint venture", "strategic investment"}

    def get_key(self) -> str:
        return "deal"

    def get_phase(self) -> str:
        return "deal_construction"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        structure_signals = {"acquisition", "merger", "buyout", "investment",
                           "partnership", "joint venture", "carve-out",
                           "spin-off", "asset purchase", "stock deal",
                           "cash offer", "tender"}
        feasibility_signals = {"affordable", "accretive", "synergistic",
                             "strategic", "value-creating", "earnings accretive",
                             "manageable", "financeable", "executable"}
        complexity_signals = {"complex", "cross-border", "multi-party",
                            "regulatory", "antitrust", "hostile",
                            "contested", "restructuring"}

        structure = self._text_signal(text, structure_signals)
        feasibility = self._text_signal(text, feasibility_signals)
        complexity = self._text_signal(text, complexity_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Financial connector: comparable transactions and valuation multiples
        financial = self._get_financial_data(context)
        fin_boost = 0.0
        comparable_context = {}
        if financial:
            mult = financial.get("avg_revenue_multiple", 5)
            if mult < 8:
                fin_boost += min(0.10, (10 - mult) / 40)
            elif mult > 15:
                fin_boost -= 0.05

            attractiveness = financial.get("deal_attractiveness", 0)
            fin_boost += min(0.08, attractiveness * 0.12)

            comps = financial.get("comparable_transactions", [])
            if comps:
                comparable_context["comp_count"] = len(comps)
                avg_comp_value = sum(
                    c.get("value_m", 0) for c in comps if isinstance(c, dict)
                ) / max(len(comps), 1)
                comparable_context["avg_comp_value_m"] = round(avg_comp_value, 1)

            premium = financial.get("avg_deal_premium", 0)
            if 0.15 < premium < 0.40:
                fin_boost += 0.04

        # Cross-engine: strong financial health improves deal feasibility
        fin_health = context.get("financial_score", 0)
        health_boost = fin_health * 0.10

        score = (structure * 0.22 + feasibility * 0.22 + base * 0.15 +
                 fin_boost + health_boost - complexity * 0.08 + 0.05)

        detail = {
            "structure": round(structure, 3),
            "feasibility": round(feasibility, 3),
            "complexity": round(complexity, 3),
            "financial_boost": round(fin_boost, 3),
            "health_crossfeed": round(health_boost, 3),
        }
        detail.update(comparable_context)
        return self._score_with_detail(context, score, detail)
