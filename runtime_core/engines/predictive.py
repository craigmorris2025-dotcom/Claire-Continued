"""
Predictive Engine — evaluates predictability, data-driven confidence, and forecast reliability.
Consumes financial connector data for historical benchmarks.
"""
from typing import Any, Dict
from runtime_core.engines.base import BaseEngine


class PredictiveEngine(BaseEngine):
    """Domain engine: predictive — forecast confidence assessment."""

    KEYWORDS = {"estimate", "forecast", "model", "predict", "probability",
                "project", "scenario", "simulate", "confidence", "baseline",
                "benchmark", "trend"}

    def get_key(self) -> str:
        return "predictive"

    def get_phase(self) -> str:
        return "innovation_breakthrough"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        data_signals = {"historical", "data-driven", "quantitative", "measured",
                       "tracked", "benchmarked", "verified", "validated",
                       "evidence-based", "empirical"}
        model_signals = {"model", "algorithm", "regression", "neural", "bayesian",
                        "monte carlo", "machine learning", "deep learning",
                        "simulation", "digital twin"}
        consistency_signals = {"consistent", "repeatable", "stable", "predictable",
                             "reliable", "deterministic", "well-understood"}

        data_q = self._text_signal(text, data_signals)
        model_q = self._text_signal(text, model_signals)
        consistency = self._text_signal(text, consistency_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Financial connector: contract visibility improves predictability
        financial = self._get_financial_data(context)
        visibility_boost = 0.0
        if financial:
            vis = financial.get("contract_visibility", 0)
            visibility_boost = min(0.10, vis * 0.12)
            backlog = financial.get("backlog_months", 0)
            if backlog > 12:
                visibility_boost += 0.05

        score = (data_q * 0.25 + model_q * 0.20 + consistency * 0.15 +
                 base * 0.15 + visibility_boost + 0.05)

        return self._score_with_detail(context, score, {
            "data_quality": round(data_q, 3),
            "model_quality": round(model_q, 3),
            "consistency": round(consistency, 3),
            "visibility_boost": round(visibility_boost, 3),
        })
