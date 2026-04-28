"""
Engineering Engine — evaluates technical depth, engineering quality, and IP strength.
Consumes patent connector data for technology depth validation.
"""
from typing import Any, Dict
from backend.engines.base import BaseEngine


class EngineeringEngine(BaseEngine):
    """Domain engine: engineering — technical depth and IP assessment."""

    KEYWORDS = {"architecture", "build", "design", "develop", "engineering",
                "infrastructure", "stack", "system", "technical", "hardware",
                "firmware", "embedded", "asic", "fpga"}

    def get_key(self) -> str:
        return "engineering"

    def get_phase(self) -> str:
        return "intel_scoring"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        depth_signals = {"patent", "proprietary", "novel", "custom", "advanced",
                        "cutting-edge", "breakthrough", "trade secret", "algorithm",
                        "invention", "research", "peer-reviewed"}
        stack_signals = {"platform", "framework", "api", "microservice", "cloud",
                        "distributed", "scalable", "kubernetes", "containerized",
                        "edge computing", "real-time", "low-latency"}

        depth = self._text_signal(text, depth_signals)
        stack = self._text_signal(text, stack_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Patent connector: patent density validates engineering claims
        patent = self._get_patent_data(context)
        patent_boost = 0.0
        if patent:
            density = patent.get("patent_density", 0)
            patent_boost = min(0.15, density * 0.15)

        score = (depth * 0.30 + stack * 0.25 + base * 0.20 + patent_boost + 0.05)

        return self._score_with_detail(context, score, {
            "depth": round(depth, 3),
            "stack": round(stack, 3),
            "patent_boost": round(patent_boost, 3),
        })
