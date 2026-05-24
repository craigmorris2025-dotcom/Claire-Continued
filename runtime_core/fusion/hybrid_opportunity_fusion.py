"""
Hybrid opportunity fusion.

v5.50:
- Fuses deterministic candidate score with connected enrichment score.
- Produces a public-safe hybrid readiness signal for dashboard and launch context.
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_core.fusion.hybrid_fusion_contracts import HybridOpportunityFusion


class HybridOpportunityFusionEngine:
    """Fuse deterministic and connected opportunity evidence."""

    def fuse_candidate(self, candidate: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        candidate = dict(candidate or {})
        fusion = self.fuse(candidate, context or {})
        candidate["hybrid_fusion"] = fusion.to_dict()
        candidate["selection_score"] = self.adjust_selection_score(candidate.get("selection_score"), fusion)
        candidate["confidence_label"] = self.adjust_confidence(candidate.get("confidence_label"), fusion)
        candidate["raw_input"] = self.enrich_raw_input(candidate.get("raw_input", ""), fusion)
        return candidate

    def fuse(self, candidate: Dict[str, Any], context: Dict[str, Any]) -> HybridOpportunityFusion:
        enrichment = candidate.get("connected_enrichment") or {}
        deterministic_score = self._bounded(float(candidate.get("selection_score") or 0.0))
        connected_score = self._bounded(float(enrichment.get("enrichment_score") or 0.0))
        safe_connected = bool(enrichment.get("safe_to_enrich"))
        governance_state = self._governance_state(enrichment)

        if safe_connected:
            hybrid_score = self._bounded((deterministic_score * 0.62) + (connected_score * 0.38))
            status = "hybrid_ready"
        else:
            hybrid_score = deterministic_score
            status = "deterministic_only"

        readiness = self._readiness(hybrid_score, safe_connected)
        recommended_mode = self._recommended_mode(context, readiness, safe_connected)
        confidence_delta = round(hybrid_score - deterministic_score, 3)

        return HybridOpportunityFusion(
            status=status,
            deterministic_score=round(deterministic_score, 3),
            connected_score=round(connected_score, 3),
            hybrid_score=round(hybrid_score, 3),
            hybrid_readiness=readiness,
            recommended_mode=recommended_mode,
            confidence_delta=confidence_delta,
            governance_state=governance_state,
            fusion_summary=self._summary(candidate, enrichment, hybrid_score, readiness, safe_connected),
            evidence={
                "connected_signal_count": enrichment.get("matched_signal_count", 0),
                "top_signal_types": enrichment.get("top_signal_types", []),
                "source_categories": enrichment.get("source_categories", []),
                "timing_window": enrichment.get("timing_window"),
                "opportunity_relevance": enrichment.get("opportunity_relevance"),
            },
            recommended_actions=self._actions(readiness, safe_connected),
        )

    def adjust_selection_score(self, current: Any, fusion: HybridOpportunityFusion) -> float:
        base = float(current or 0.0)
        if fusion.status != "hybrid_ready":
            return round(base, 3)
        boost = min(0.045, max(0.0, fusion.confidence_delta) * 0.50)
        return round(min(0.985, base + boost), 3)

    def adjust_confidence(self, current: Any, fusion: HybridOpportunityFusion) -> str:
        if fusion.hybrid_readiness in {"hybrid_strong", "hybrid_ready"}:
            return "hybrid_high"
        if fusion.hybrid_readiness == "hybrid_watchlist":
            return "hybrid_medium"
        return str(current or "medium")

    def enrich_raw_input(self, raw_input: str, fusion: HybridOpportunityFusion) -> str:
        if fusion.status != "hybrid_ready":
            return raw_input
        return (
            f"{raw_input} "
            f"Hybrid fusion context: deterministic score {fusion.deterministic_score}, "
            f"connected score {fusion.connected_score}, hybrid score {fusion.hybrid_score}. "
            f"Recommended mode: {fusion.recommended_mode}. "
            f"Fusion summary: {fusion.fusion_summary} "
            f"Use hybrid context as governed external evidence, not as deterministic proof."
        )

    def _governance_state(self, enrichment: Dict[str, Any]) -> str:
        signals = enrichment.get("supporting_signals") or []
        states = {str(signal.get("governance_status") or "unknown") for signal in signals}
        if "block" in states:
            return "blocked"
        if "review" in states:
            return "review_required"
        if enrichment.get("safe_to_enrich"):
            return "allow"
        return "not_applicable"

    def _recommended_mode(self, context: Dict[str, Any], readiness: str, safe_connected: bool) -> str:
        requested = context.get("execution_mode") or context.get("mode") or "deterministic"
        if not safe_connected:
            return "deterministic"
        if requested in {"hybrid", "connected"}:
            return "hybrid" if readiness in {"hybrid_strong", "hybrid_ready"} else requested
        return "hybrid_candidate"

    def _readiness(self, score: float, safe_connected: bool) -> str:
        if not safe_connected:
            return "deterministic_only"
        if score >= 0.82:
            return "hybrid_strong"
        if score >= 0.70:
            return "hybrid_ready"
        if score >= 0.56:
            return "hybrid_watchlist"
        return "connected_insufficient"

    def _summary(
        self,
        candidate: Dict[str, Any],
        enrichment: Dict[str, Any],
        hybrid_score: float,
        readiness: str,
        safe_connected: bool,
    ) -> str:
        title = candidate.get("title") or candidate.get("opportunity_direction") or "Opportunity"
        if not safe_connected:
            return f"{title} remains deterministic-only because no safe connected enrichment was available."
        types = ", ".join((enrichment.get("top_signal_types") or [])[:3]) or "connected market"
        timing = enrichment.get("timing_window") or "unconfirmed"
        return (
            f"{title} has {readiness.replace('_', ' ')} status with hybrid score {round(hybrid_score, 3)}. "
            f"Connected evidence is led by {types} signals with {timing} timing."
        )

    def _actions(self, readiness: str, safe_connected: bool) -> List[Dict[str, str]]:
        if not safe_connected:
            return [{
                "action": "run deterministic evaluation",
                "purpose": "preserve current workflow until safe connected evidence is available",
                "priority": "medium",
            }]
        actions = [{
            "action": "run Claire with hybrid context",
            "purpose": "evaluate deterministic opportunity logic against normalized connected signals",
            "priority": "high",
        }]
        if readiness in {"hybrid_strong", "hybrid_ready"}:
            actions.append({
                "action": "include fusion summary in export package",
                "purpose": "preserve provenance for connected/hybrid decision review",
                "priority": "high",
            })
        return actions

    def _bounded(self, value: float) -> float:
        return max(0.0, min(1.0, float(value or 0.0)))


__all__ = ["HybridOpportunityFusionEngine"]
