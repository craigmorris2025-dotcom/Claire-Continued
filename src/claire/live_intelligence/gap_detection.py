"""Gap detection from trend clusters."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class GapDetectionEngine:
    """Convert trend clusters into unmet needs and opportunity gaps."""

    GAP_MAP = {
        "risk_regulation_compliance": ("Governed compliance visibility gap", "Automated governance and compliance intelligence layer"),
        "ai_infrastructure_pressure": ("AI infrastructure operating pressure", "AI infrastructure planning and risk command center"),
        "market_competition_pressure": ("Market movement detection gap", "Competitive market pressure sensing and response workflow"),
        "technical_feasibility_moat": ("Innovation whitespace and defensibility gap", "Patent-aware solution design and moat mapping layer"),
        "capital_growth_strategy": ("Strategic capital allocation gap", "Executive portfolio signal and investment prioritization dashboard"),
    }

    def detect(self, clusters_payload: Dict[str, Any]) -> Dict[str, Any]:
        gaps: List[Dict[str, Any]] = []
        for cluster in clusters_payload.get("clusters", []):
            market_gap, needed_solution = self.GAP_MAP.get(
                cluster.get("trend_type"),
                ("Public-market intelligence gap", "Live opportunity intelligence workflow"),
            )
            score = round(min(0.98, cluster.get("strength_score", 0.5) + 0.12), 3)
            gaps.append({
                "gap_id": f"gap_{cluster.get('cluster_id')}",
                "cluster_id": cluster.get("cluster_id"),
                "market_universe": cluster.get("market_universe"),
                "industry_domain": cluster.get("industry_domain"),
                "trend_type": cluster.get("trend_type"),
                "market_gap": market_gap,
                "needed_solution": needed_solution,
                "urgency": "high" if score >= 0.72 else "medium",
                "gap_score": score,
                "evidence_signal_count": cluster.get("signal_count", 0),
                "evidence_entity_count": cluster.get("entity_count", 0),
                "why_now": f"{cluster.get('trajectory')} trend with {cluster.get('signal_count')} supporting signal(s).",
            })
        return {
            "status": "success",
            "engine": "gap_detection_engine_v1",
            "gap_count": len(gaps),
            "gaps": sorted(gaps, key=lambda item: item["gap_score"], reverse=True),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
