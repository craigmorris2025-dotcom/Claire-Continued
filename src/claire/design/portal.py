"""
Design Portal — conditional gateway into system/technology design.

This module does NOT replace the main Claire pipeline.
It only activates when a breakthrough, needed solution, gap fill,
or opportunity is strong enough to justify design work.
"""

from typing import Any, Dict


class DesignPortal:
    """
    Routes validated opportunities into the design pathway when appropriate.
    """

    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        scores = context.get("scores", {})
        domain = context.get("domain", "general")
        keywords = context.get("keywords", [])
        system_design = context.get("system_design", {})
        market_gap = context.get("market_gap", {})

        breakthrough = scores.get("breakthrough_score", 0.0)
        portfolio = scores.get("portfolio_score", 0.0)
        confidence = scores.get("_confidence", portfolio)

        market_gap_ok = True
        if isinstance(market_gap, dict) and market_gap.get("status") == "market_gap_failed":
            market_gap_ok = False

        should_route = (
            breakthrough >= 0.75
            and confidence >= 0.70
            and system_design.get("status") == "success"
            and market_gap_ok
        )

        reason = self._reason(
            breakthrough=breakthrough,
            confidence=confidence,
            system_design=system_design,
            should_route=should_route,
            market_gap_ok=market_gap_ok,
        )

        return {
            "status": "design_ready" if should_route else "not_ready",
            "route_to_design": should_route,
            "domain": domain,
            "keywords": keywords,
            "market_gap": market_gap,
            "reason": reason,
            "inputs": {
                "scores": scores,
                "system_design": system_design,
                "market_gap": market_gap,
                "domain": domain,
                "keywords": keywords,
            },
        }

    def _reason(
        self,
        breakthrough: float,
        confidence: float,
        system_design: Dict[str, Any],
        should_route: bool,
        market_gap_ok: bool = True,
    ) -> str:
        if should_route:
            return "Breakthrough, confidence, system design, and market gap thresholds met; design pathway activated."

        if breakthrough < 0.75:
            return "Breakthrough score below design threshold."

        if confidence < 0.70:
            return "Confidence below design threshold."

        if system_design.get("status") != "success":
            return "System design unavailable or failed."

        if not market_gap_ok:
            return "Market gap analysis failed or unavailable."

        return "Design pathway not activated."
