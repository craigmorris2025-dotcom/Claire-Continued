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

        breakthrough = scores.get("breakthrough_score", 0.0)
        portfolio = scores.get("portfolio_score", 0.0)
        confidence = scores.get("_confidence", portfolio)

        should_route = (
            breakthrough >= 0.75
            and confidence >= 0.70
            and system_design.get("status") == "success"
        )

        reason = self._reason(
            breakthrough=breakthrough,
            confidence=confidence,
            system_design=system_design,
            should_route=should_route,
        )

        return {
            "status": "design_ready" if should_route else "not_ready",
            "route_to_design": should_route,
            "domain": domain,
            "keywords": keywords,
            "reason": reason,
            "inputs": {
                "scores": scores,
                "system_design": system_design,
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
    ) -> str:
        if should_route:
            return "Breakthrough and confidence thresholds met; design pathway activated."

        if breakthrough < 0.75:
            return "Breakthrough score below design threshold."

        if confidence < 0.70:
            return "Confidence below design threshold."

        if system_design.get("status") != "success":
            return "System design unavailable or failed."

        return "Design pathway not activated."