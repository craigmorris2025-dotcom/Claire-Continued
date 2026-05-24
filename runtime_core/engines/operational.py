"""
Operational Engine — evaluates operational efficiency, execution capability, and scalability.
"""
from typing import Any, Dict
from runtime_core.engines.base import BaseEngine


class OperationalEngine(BaseEngine):
    """Domain engine: operational — efficiency and execution assessment."""

    KEYWORDS = {"delivery", "efficiency", "execution", "logistics", "manufacturing",
                "operations", "process", "supply chain", "production", "capacity",
                "throughput", "uptime"}

    def get_key(self) -> str:
        return "operational"

    def get_phase(self) -> str:
        return "intel_scoring"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        efficiency_signals = {"automated", "streamlined", "optimized", "lean",
                            "efficient", "scalable", "devops", "ci/cd",
                            "zero downtime", "fault tolerant"}
        execution_signals = {"deployed", "production", "live", "operational",
                           "running", "proven", "battle-tested", "fielded",
                           "operationalized", "in service"}
        scale_signals = {"scalable", "elastic", "multi-region", "global ops",
                        "high availability", "redundant", "distributed"}

        eff = self._text_signal(text, efficiency_signals)
        exe = self._text_signal(text, execution_signals)
        scale = self._text_signal(text, scale_signals)
        base = self._text_signal(text, self.KEYWORDS)

        # Market connector: talent market availability
        market = self._get_market_data(context)
        talent_adj = 0.0
        if market:
            talent = market.get("talent_availability", "")
            if talent == "high":
                talent_adj = 0.05
            elif talent == "critical":
                talent_adj = -0.05

        score = (eff * 0.25 + exe * 0.25 + scale * 0.15 +
                 base * 0.20 + talent_adj + 0.05)

        return self._score_with_detail(context, score, {
            "efficiency": round(eff, 3),
            "execution": round(exe, 3),
            "scalability": round(scale, 3),
            "talent_adj": round(talent_adj, 3),
        })
