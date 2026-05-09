"""v5.89.8 trend discovery and thesis formation synthesis.

This layer does not replace Claire's existing market, trajectory, or
opportunity engines. It gives lifecycle stages 8-10 a stable artifact surface
that can be validated, exported, and used by later core-completion work.
"""

from __future__ import annotations

from typing import Any, Dict, List


class TrendThesisEngine:
    version = "v5.89.8_trend_discovery_thesis_formation"

    def synthesize(
        self,
        text: str,
        domain: str,
        keywords: List[str],
        governed_signals: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_gap: Dict[str, Any],
        market_formation: Dict[str, Any],
        opportunity_discovery: Dict[str, Any],
    ) -> Dict[str, Any]:
        keywords = keywords or []
        governed_signals = governed_signals or {}
        trend_trajectory = trend_trajectory or {}
        market_gap = market_gap or {}
        market_formation = market_formation or {}
        opportunity_discovery = opportunity_discovery or {}

        trend_discovery = self._trend_discovery(
            text=text or "",
            domain=domain or "general",
            keywords=keywords,
            governed_signals=governed_signals,
            trend_trajectory=trend_trajectory,
            market_gap=market_gap,
            market_formation=market_formation,
        )
        thesis_formation = self._thesis_formation(
            domain=domain or "general",
            keywords=keywords,
            trend_discovery=trend_discovery,
            market_gap=market_gap,
            opportunity_discovery=opportunity_discovery,
        )
        return {
            "status": "success",
            "version": self.version,
            "trend_discovery": trend_discovery,
            "thesis_formation": thesis_formation,
        }

    def _trend_discovery(
        self,
        text: str,
        domain: str,
        keywords: List[str],
        governed_signals: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_gap: Dict[str, Any],
        market_formation: Dict[str, Any],
    ) -> Dict[str, Any]:
        accepted_count = int(governed_signals.get("accepted_signal_count") or 0)
        trajectory_score = self._get_float(trend_trajectory, "trend_direction.score")
        momentum_score = self._get_float(trend_trajectory, "market_momentum.score")
        pressure_score = self._get_float(market_gap, "strategic_pressure.score")
        category_score = self._get_float(market_formation, "category_creation_score.score")
        discovery_score = self._bounded(
            0.18
            + min(0.16, accepted_count * 0.08)
            + trajectory_score * 0.20
            + momentum_score * 0.18
            + pressure_score * 0.20
            + category_score * 0.08
        )

        sector = market_gap.get("sector") or "general_intelligence"
        trend_name = self._trend_name(sector, keywords, text)
        cluster = self._cluster_name(sector, market_gap)
        urgency = "high" if discovery_score >= 0.72 else "medium" if discovery_score >= 0.48 else "low"

        return {
            "status": "success",
            "root_system": "trend_discovery",
            "domain": domain,
            "sector": sector,
            "discovery_score": {"score": round(discovery_score, 4), "level": urgency},
            "discovered_trends": [
                {
                    "name": trend_name,
                    "direction": self._get_text(trend_trajectory, "trend_direction.direction", "emerging"),
                    "momentum_score": round(momentum_score, 4),
                    "pressure_score": round(pressure_score, 4),
                    "source": "governed_signal_plus_existing_engines",
                }
            ],
            "cluster_formation": {
                "cluster": cluster,
                "cluster_basis": self._cluster_basis(keywords, governed_signals),
                "accepted_signal_count": accepted_count,
            },
            "evidence": {
                "governed_signal_summary": governed_signals.get("summary", {}),
                "trend_trajectory_status": trend_trajectory.get("status"),
                "market_gap_status": market_gap.get("status"),
                "market_formation_status": market_formation.get("status"),
            },
            "confidence": round(self._bounded((discovery_score * 0.74) + min(0.20, accepted_count * 0.10)), 4),
        }

    def _thesis_formation(
        self,
        domain: str,
        keywords: List[str],
        trend_discovery: Dict[str, Any],
        market_gap: Dict[str, Any],
        opportunity_discovery: Dict[str, Any],
    ) -> Dict[str, Any]:
        discovery_score = self._get_float(trend_discovery, "discovery_score.score")
        opportunity_score = self._get_float(opportunity_discovery, "opportunity_score.score")
        pressure_score = self._get_float(market_gap, "strategic_pressure.score")
        thesis_score = self._bounded(discovery_score * 0.38 + opportunity_score * 0.42 + pressure_score * 0.20)
        sector = trend_discovery.get("sector") or market_gap.get("sector") or "general_intelligence"
        trend = (trend_discovery.get("discovered_trends") or [{}])[0].get("name") or str(sector).replace("_", " ")
        route_recommendation = "breakthrough_escalation_candidate" if thesis_score >= 0.74 else "portfolio_intelligence"

        return {
            "status": "success",
            "domain": domain,
            "sector": sector,
            "thesis_score": {"score": round(thesis_score, 4), "level": self._level(thesis_score)},
            "route_recommendation": route_recommendation,
            "thesis_statement": (
                f"{trend} is a qualified Claire trend thesis because governed signals, "
                f"market pressure, and opportunity evidence indicate a structural portfolio opportunity."
            ),
            "supporting_points": self._supporting_points(keywords, trend_discovery, market_gap, opportunity_discovery),
            "missing_selections": self._missing_selections(trend_discovery, opportunity_discovery),
            "confidence": round(self._bounded(thesis_score * 0.82 + discovery_score * 0.12), 4),
        }

    def _supporting_points(
        self,
        keywords: List[str],
        trend_discovery: Dict[str, Any],
        market_gap: Dict[str, Any],
        opportunity_discovery: Dict[str, Any],
    ) -> List[str]:
        points = []
        cluster = (trend_discovery.get("cluster_formation") or {}).get("cluster")
        if cluster:
            points.append(f"Trend cluster formed around {cluster}.")
        gap_type = market_gap.get("gap_type")
        if gap_type:
            points.append(f"Market gap is classified as {gap_type}.")
        opportunity_type = opportunity_discovery.get("opportunity_type")
        if opportunity_type:
            points.append(f"Opportunity type is {opportunity_type}.")
        if keywords:
            points.append("Primary keywords: " + ", ".join(keywords[:6]) + ".")
        return points or ["Trend and thesis evidence is present but still sparse."]

    def _missing_selections(self, trend_discovery: Dict[str, Any], opportunity_discovery: Dict[str, Any]) -> List[str]:
        missing = []
        if not (trend_discovery.get("discovered_trends") or []):
            missing.append("discovered_trends")
        if not opportunity_discovery.get("validation_roadmap"):
            missing.append("validation_roadmap")
        if not opportunity_discovery.get("evidence_gaps"):
            missing.append("evidence_gaps")
        return missing

    def _trend_name(self, sector: str, keywords: List[str], text: str) -> str:
        label = str(sector or "general_intelligence").replace("_", " ")
        if keywords:
            return f"{label}: {' '.join(keywords[:3])}"
        words = [word.strip(",.") for word in text.split() if len(word) > 4]
        return f"{label}: {' '.join(words[:3])}" if words else label

    def _cluster_name(self, sector: str, market_gap: Dict[str, Any]) -> str:
        solution_class = market_gap.get("solution_class")
        if solution_class:
            return f"{sector}:{solution_class}"
        return str(sector or "general_intelligence")

    def _cluster_basis(self, keywords: List[str], governed_signals: Dict[str, Any]) -> List[str]:
        basis = [f"keyword:{keyword}" for keyword in keywords[:5]]
        if governed_signals.get("accepted_signal_count"):
            basis.append("accepted_governed_signals")
        return basis or ["raw_input"]

    def _get_float(self, obj: Dict[str, Any], path: str) -> float:
        value = self._get(obj, path, 0.0)
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def _get_text(self, obj: Dict[str, Any], path: str, default: str) -> str:
        value = self._get(obj, path, default)
        return str(value or default)

    def _get(self, obj: Dict[str, Any], path: str, default: Any = None) -> Any:
        cur: Any = obj if isinstance(obj, dict) else {}
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

    def _level(self, score: float) -> str:
        if score >= 0.74:
            return "strong"
        if score >= 0.52:
            return "qualified"
        if score >= 0.34:
            return "partial"
        return "insufficient"

    def _bounded(self, value: float) -> float:
        return max(0.0, min(1.0, float(value or 0.0)))
