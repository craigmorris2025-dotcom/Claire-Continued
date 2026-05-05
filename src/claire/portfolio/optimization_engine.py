"""v5.89.9 portfolio creation and optimization artifact layer."""

from __future__ import annotations

from typing import Any, Dict, List


class PortfolioOptimizationEngine:
    """Builds a small route-aware portfolio optimization artifact.

    This does not replace the portfolio binder. It turns the binder plus
    trend/thesis/opportunity evidence into a testable lifecycle stage-27 output.
    """

    version = "v5.89.9_portfolio_creation_optimization"

    def optimize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context = context or {}
        scores = context.get("scores", {}) or {}
        thesis = context.get("thesis_formation", {}) or {}
        trend = context.get("trend_discovery", {}) or {}
        opportunity = context.get("opportunity_discovery", {}) or {}
        binder = context.get("portfolio_binder", {}) or {}
        acquirers = context.get("acquirer_matches", []) or []

        portfolio_score = self._float(scores.get("portfolio_score"))
        optimization_score = self._bounded(
            0.16
            + portfolio_score * 0.34
            + self._get_float(thesis, "thesis_score.score") * 0.18
            + self._get_float(trend, "discovery_score.score") * 0.14
            + self._get_float(opportunity, "opportunity_score.score") * 0.12
            + (0.04 if binder.get("status") == "success" else 0.0)
            + min(0.02, len(acquirers) * 0.004)
        )
        path = self._path(optimization_score, thesis)

        return {
            "status": "success",
            "version": self.version,
            "portfolio_optimization_score": {
                "score": round(optimization_score, 4),
                "level": self._level(optimization_score),
            },
            "portfolio_path": path,
            "allocation_hypothesis": self._allocation_hypothesis(context, path),
            "optimization_actions": self._optimization_actions(context, path),
            "constraints": self._constraints(context),
            "evidence": {
                "portfolio_score": round(portfolio_score, 4),
                "thesis_score": self._get_float(thesis, "thesis_score.score"),
                "trend_discovery_score": self._get_float(trend, "discovery_score.score"),
                "opportunity_score": self._get_float(opportunity, "opportunity_score.score"),
                "binder_status": binder.get("status"),
                "acquirer_count": len(acquirers),
            },
            "completion": "complete" if optimization_score >= 0.46 and binder.get("status") == "success" else "partial",
            "confidence": round(self._bounded(optimization_score * 0.82 + portfolio_score * 0.12), 4),
        }

    def _allocation_hypothesis(self, context: Dict[str, Any], path: str) -> Dict[str, Any]:
        market_gap = context.get("market_gap", {}) or {}
        strategic = context.get("strategic_positioning", {}) or {}
        sector = market_gap.get("sector") or "general_intelligence"
        category = self._get_text(strategic, "category_positioning.category_name") or str(sector).replace("_", " ")
        return {
            "primary_theme": category,
            "sector": sector,
            "path": path,
            "role": "core_candidate" if path == "optimize_for_core_portfolio" else "watchlist_or_adjacency",
        }

    def _optimization_actions(self, context: Dict[str, Any], path: str) -> List[Dict[str, str]]:
        opportunity = context.get("opportunity_discovery", {}) or {}
        actions = [
            {
                "action": "preserve trend thesis evidence",
                "purpose": "keep stage 8-10 evidence attached to the portfolio decision",
                "priority": "high",
            },
            {
                "action": "compare against adjacent portfolio themes",
                "purpose": "avoid treating a single opportunity as a complete portfolio by default",
                "priority": "medium",
            },
        ]
        if opportunity.get("validation_roadmap"):
            actions.append({
                "action": "run validation roadmap before expansion",
                "purpose": "qualify the thesis before allocating additional portfolio weight",
                "priority": "high",
            })
        if path == "optimize_for_core_portfolio":
            actions.append({
                "action": "prepare portfolio candidate package",
                "purpose": "move the candidate toward acquisition-readiness review",
                "priority": "high",
            })
        return actions

    def _constraints(self, context: Dict[str, Any]) -> List[str]:
        constraints = []
        risk = context.get("risk_regulation", {}) or {}
        blocker = self._get_text(risk, "blocker_assessment.blocker_level")
        if blocker and blocker != "manageable":
            constraints.append(f"risk blocker level: {blocker}")
        business = context.get("business_model", {}) or {}
        commercial_risk = self._get_text(business, "commercial_risk.level")
        if commercial_risk:
            constraints.append(f"commercial risk: {commercial_risk}")
        if not constraints:
            constraints.append("no blocking portfolio constraints surfaced in deterministic run")
        return constraints

    def _path(self, score: float, thesis: Dict[str, Any]) -> str:
        recommendation = thesis.get("route_recommendation")
        if score >= 0.74 and recommendation == "breakthrough_escalation_candidate":
            return "optimize_for_core_portfolio"
        if score >= 0.56:
            return "portfolio_candidate"
        return "watchlist"

    def _level(self, score: float) -> str:
        if score >= 0.74:
            return "strong"
        if score >= 0.56:
            return "qualified"
        if score >= 0.40:
            return "partial"
        return "insufficient"

    def _get_float(self, obj: Dict[str, Any], path: str) -> float:
        return self._float(self._get(obj, path, 0.0))

    def _get_text(self, obj: Dict[str, Any], path: str) -> str:
        value = self._get(obj, path, "")
        return str(value or "")

    def _get(self, obj: Dict[str, Any], path: str, default: Any = None) -> Any:
        cur: Any = obj if isinstance(obj, dict) else {}
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

    def _float(self, value: Any) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def _bounded(self, value: float) -> float:
        return max(0.0, min(1.0, float(value or 0.0)))
