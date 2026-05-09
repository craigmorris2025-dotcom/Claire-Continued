"""
Product Engine — evaluates product-market fit, maturity, and differentiation.
Consumes market connector data for competitive landscape context.
"""
from typing import Any, Dict
from claire.engines.base import BaseEngine


class ProductEngine(BaseEngine):
    """Domain engine: product — product-market fit and differentiation."""

    KEYWORDS = {"application", "feature", "offering", "platform", "product",
                "saas", "service", "solution", "tool", "software", "hardware",
                "system", "module", "capability"}

    def get_key(self) -> str:
        return "product"

    def get_phase(self) -> str:
        return "intel_scoring"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        fit_signals = {"market fit", "customers", "users", "adoption", "traction",
                      "revenue", "growth", "pipeline", "demand", "orders",
                      "backlog", "deployment", "production"}
        diff_signals = {"unique", "differentiated", "competitive advantage", "moat",
                       "patent", "proprietary", "first-of-its-kind", "sole source",
                       "exclusive", "best-in-class"}

        fit = self._text_signal(text, fit_signals)
        diff = self._text_signal(text, diff_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Market connector: top segments inform product positioning
        market = self._get_market_data(context)
        segment_boost = 0.0
        if market:
            segments = market.get("top_segments", [])
            for seg in segments:
                if isinstance(seg, str) and seg.lower() in text:
                    segment_boost += 0.05
            segment_boost = min(0.15, segment_boost)

        score = (fit * 0.30 + diff * 0.25 + base * 0.20 + segment_boost + 0.05)

        return self._score_with_detail(context, score, {
            "fit": round(fit, 3),
            "differentiation": round(diff, 3),
            "segment_boost": round(segment_boost, 3),
        })
