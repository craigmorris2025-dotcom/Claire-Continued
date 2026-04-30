"""
Portfolio Engine — evaluates portfolio fit, diversification impact, and strategic value-add.
Synthesizes cross-engine signals with connector data for portfolio-level intelligence.
"""
from typing import Any, Dict
from claire.engines.base import BaseEngine


class PortfolioEngine(BaseEngine):
    """Domain engine: portfolio — fit and diversification assessment."""

    KEYWORDS = {"allocation", "balance", "concentration", "diversification",
                "exposure", "mix", "portfolio", "holdings", "thesis",
                "mandate", "fund", "platform"}

    def get_key(self) -> str:
        return "portfolio"

    def get_phase(self) -> str:
        return "portfolio_compliance"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        # Cross-engine synthesis for portfolio decision
        decision_s = context.get("decision_engine_score",
                                 context.get("decision_score", 0.3))
        breakthrough_s = context.get("breakthrough_score", 0.2)
        synergy_s = context.get("synergy_score", 0.2)
        risk_s = context.get("risk_score", 0.5)
        strategy_s = context.get("strategy_score", 0.3)

        # Portfolio-specific signals
        fit_signals = {"strategic fit", "portfolio gap", "adjacency", "complementary",
                      "white space", "capability gap", "new vertical", "platform play"}
        value_signals = {"value creation", "returns", "irr", "moic", "accretive",
                        "synergy value", "multiple expansion"}

        fit = self._text_signal(text, fit_signals)
        value = self._text_signal(text, value_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Domain diversification — more domains covered = better diversification
        dims = context.get("domain_scores", {})
        active_domains = sum(1 for v in dims.values() if v > 0.05) if dims else 0
        diversity_bonus = min(0.10, active_domains * 0.02)

        # Financial connector: deal attractiveness validates portfolio addition
        financial = self._get_financial_data(context)
        deal_quality = 0.0
        if financial:
            attractiveness = financial.get("deal_attractiveness", 0)
            deal_quality = min(0.08, attractiveness * 0.12)

        # Weighted synthesis
        engine_composite = (decision_s * 0.20 + breakthrough_s * 0.15 +
                          synergy_s * 0.10 + risk_s * 0.10 + strategy_s * 0.10)

        score = (engine_composite + fit * 0.10 + value * 0.08 +
                 base * 0.05 + diversity_bonus + deal_quality + 0.03)

        context["portfolio_engine_score"] = round(self._clamp(score), 4)
        return self._score_with_detail(context, score, {
            "engine_composite": round(engine_composite, 3),
            "fit_signal": round(fit, 3),
            "value_signal": round(value, 3),
            "diversity_bonus": round(diversity_bonus, 3),
            "deal_quality": round(deal_quality, 3),
            "active_domains": active_domains,
        })
