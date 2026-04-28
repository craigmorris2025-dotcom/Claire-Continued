"""
Innovation Engine — evaluates innovation depth, novelty, and IP-backed differentiation.
Primary consumer of patent connector data for innovation landscape intelligence.
"""
from typing import Any, Dict
from backend.engines.base import BaseEngine


class InnovationEngine(BaseEngine):
    """Domain engine: innovation — depth, novelty, and IP assessment."""

    KEYWORDS = {"breakthrough", "cutting-edge", "disruptive", "innovation", "novel",
                "paradigm", "pioneer", "revolutionary", "invention", "r&d",
                "research", "development"}

    def get_key(self) -> str:
        return "innovation"

    def get_phase(self) -> str:
        return "innovation_breakthrough"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        novelty_signals = {"first", "novel", "unique", "new approach", "invented",
                          "created", "original", "unprecedented", "one-of-a-kind",
                          "first-ever", "never before"}
        impact_signals = {"disruptive", "transformative", "game-changing",
                        "revolutionary", "paradigm shift", "category-defining",
                        "market-creating", "leap forward"}
        rd_signals = {"r&d", "research", "lab", "prototype", "proof of concept",
                     "peer-reviewed", "published", "phd", "scientist",
                     "technical team", "engineering team"}

        novelty = self._text_signal(text, novelty_signals)
        impact = self._text_signal(text, impact_signals)
        rd_depth = self._text_signal(text, rd_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Patent connector: comprehensive IP landscape
        patent = self._get_patent_data(context)
        patent_boost = 0.0
        innovation_signal = 0.0
        emerging_areas = []
        if patent:
            density = patent.get("patent_density", 0)
            patent_boost = min(0.12, density * 0.15)
            innovation_signal = patent.get("innovation_signal", 0)
            patent_boost += min(0.08, innovation_signal * 0.12)
            emerging_areas = patent.get("emerging_areas", [])
            # Boost if text mentions emerging areas
            for area in emerging_areas:
                if isinstance(area, str) and area.lower() in text:
                    patent_boost += 0.03
            patent_boost = min(0.20, patent_boost)

        score = (novelty * 0.22 + impact * 0.22 + rd_depth * 0.15 +
                 base * 0.15 + patent_boost + 0.05)

        return self._score_with_detail(context, score, {
            "novelty": round(novelty, 3),
            "impact": round(impact, 3),
            "rd_depth": round(rd_depth, 3),
            "patent_boost": round(patent_boost, 3),
            "innovation_signal": round(innovation_signal, 3),
            "emerging_areas_matched": [a for a in emerging_areas
                                       if isinstance(a, str) and a.lower() in text],
        })
