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
        thesis = context.get("thesis_formation", {}) if isinstance(context.get("thesis_formation"), dict) else {}
        source_authority = context.get("source_authority", {}) if isinstance(context.get("source_authority"), dict) else {}
        breakthrough_synthesis = context.get("breakthrough_synthesis", {}) if isinstance(context.get("breakthrough_synthesis"), dict) else {}
        route_recommendation = str(thesis.get("route_recommendation") or "").strip()
        design_route_requested = route_recommendation in {
            "breakthrough_design",
            "breakthrough_escalation_candidate",
            "solution_design",
        }

        breakthrough = scores.get("breakthrough_score", 0.0)
        portfolio = scores.get("portfolio_score", 0.0)
        confidence = scores.get("_confidence", portfolio)
        synthesis_score = self._nested_score(breakthrough_synthesis, "breakthrough_synthesis_score")
        source_evidence_present = bool(source_authority.get("source_evidence_present"))
        live_evidence_present = bool(source_authority.get("live_evidence_present"))
        request_source_keys = set(source_authority.get("request_source_keys") or [])
        recursive_memory_keys = set(source_authority.get("recursive_memory_source_keys") or [])
        live_source_keys = set(source_authority.get("live_source_keys") or [])
        recursive_only = (
            source_authority.get("recursive_memory_source_present") is True
            and not source_authority.get("live_evidence_present")
            and not live_source_keys
            and bool(request_source_keys)
            and request_source_keys.issubset(recursive_memory_keys)
        )
        design_route_authorized = design_route_requested and not recursive_only
        signal_activated_breakthrough = (
            source_evidence_present
            and live_evidence_present
            and not recursive_only
            and breakthrough >= 0.82
            and synthesis_score >= 0.64
            and confidence >= 0.70
        )

        market_gap_ok = True
        if isinstance(market_gap, dict) and market_gap.get("status") == "market_gap_failed":
            market_gap_ok = False

        should_route = (
            (design_route_authorized or signal_activated_breakthrough)
            and breakthrough >= 0.75
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
            route_recommendation=route_recommendation,
            design_route_requested=design_route_authorized,
            signal_activated_breakthrough=signal_activated_breakthrough,
            synthesis_score=synthesis_score,
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
                "route_recommendation": route_recommendation,
                "design_route_requested": design_route_requested,
                "design_route_authorized": design_route_authorized,
                "recursive_memory_only": recursive_only,
                "signal_activated_breakthrough": signal_activated_breakthrough,
                "breakthrough_synthesis_score": synthesis_score,
                "source_authority": source_authority,
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
        route_recommendation: str = "",
        design_route_requested: bool = False,
        signal_activated_breakthrough: bool = False,
        synthesis_score: float = 0.0,
    ) -> str:
        if should_route:
            if signal_activated_breakthrough and not design_route_requested:
                return "Runtime signals met breakthrough and synthesis thresholds; design pathway activated."
            return "Thesis requested design escalation and design thresholds were met; design pathway activated."

        if route_recommendation and not design_route_requested:
            return f"Thesis recommended {route_recommendation}; portfolio path preserved."

        if not design_route_requested and not signal_activated_breakthrough:
            if synthesis_score < 0.64:
                return "Breakthrough synthesis below design activation threshold; portfolio path preserved."
            return "Runtime breakthrough conditions not met; portfolio path preserved."

        if breakthrough < 0.75:
            return "Breakthrough score below design threshold."

        if confidence < 0.70:
            return "Confidence below design threshold."

        if system_design.get("status") != "success":
            return "System design unavailable or failed."

        if not market_gap_ok:
            return "Market gap analysis failed or unavailable."

        return "Design pathway not activated."

    def _nested_score(self, payload: Dict[str, Any], key: str) -> float:
        value = payload.get(key) if isinstance(payload, dict) else None
        if isinstance(value, dict):
            value = value.get("score")
        try:
            return float(value or 0.0)
        except Exception:
            return 0.0
