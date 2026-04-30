"""
Score Card — formatted text output of pipeline results.
"""
from claire.domain.contract import ClaireResult
from typing import Dict


class ScoreCard:
    """Generates formatted score card text."""

    DISPLAY_SCORES = [
        ("Decision", "decision_score"),
        ("Breakthrough", "breakthrough_score"),
        ("Portfolio", "portfolio_score"),
        ("Synergy", "synergy_score"),
        ("Strategy", "strategy_score"),
        ("Risk", "risk_score"),
        ("Market", "market_score"),
        ("Innovation", "innovation_score"),
        ("Deal", "deal_score"),
        ("Forecast", "forecast_score"),
        ("Predictive", "predictive_score"),
        ("Semantic", "semantic_score"),
        ("Ingestion", "ingestion_score"),
    ]

    def generate(self, result: ClaireResult) -> str:
        """Generate score card from a ClaireResult object."""
        lines = [
            "=" * 60,
            "  CLAIRE SYNTALION — Score Card",
            f"  Intent: {result.intent_id}  |  Mode: {result.mode}",
            "=" * 60, "",
        ]
        for label, key in self.DISPLAY_SCORES:
            val = result.scores.get(key, 0)
            bar = "#" * int(val * 30)
            dot = "." * (30 - len(bar))
            lines.append(f"  {label:15s}  {val:.4f}  [{bar}{dot}]")
        lines.append("")
        lines.append(f"  Decision:     {result.decision_classification}")
        lines.append(f"  Breakthrough: {result.breakthrough_classification}")
        conf = result.scores.get("_confidence", 0)
        lines.append(f"  Confidence:   {conf:.4f}")
        lines.append(f"  Syntalion:    {'READY' if result.ready_for_syntalion else 'NOT READY'}")
        if result.acquirer_matches:
            lines.append(f"\n  Top Acquirers ({len(result.acquirer_matches)}):")
            for a in result.acquirer_matches[:5]:
                lines.append(f"    {a.get('name','?'):20s}  fit={a.get('match_score', a.get('fit',0)):.2f}")
        lines.append("=" * 60)
        return "\n".join(lines)

    def render(self, scores: Dict[str, float]) -> str:
        """Render from a raw scores dict (for API use)."""
        lines = ["=" * 60, "  CLAIRE SYNTALION — Score Card", "=" * 60, ""]
        for label, key in self.DISPLAY_SCORES:
            val = scores.get(key, 0)
            bar = "#" * int(val * 30)
            dot = "." * (30 - len(bar))
            lines.append(f"  {label:15s}  {val:.4f}  [{bar}{dot}]")
        lines.append("=" * 60)
        return "\n".join(lines)
