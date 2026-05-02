"""Solution synthesis from detected opportunity gaps."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class SolutionSynthesisEngine:
    """Create solution candidates from live-detected gaps."""

    def synthesize(self, gaps_payload: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        candidates: List[Dict[str, Any]] = []
        for index, gap in enumerate(gaps_payload.get("gaps", []), start=1):
            score = gap.get("gap_score", 0.5)
            candidates.append({
                "solution_id": f"solution_{index:03d}",
                "gap_id": gap.get("gap_id"),
                "title": gap.get("needed_solution"),
                "market_gap": gap.get("market_gap"),
                "needed_solution": gap.get("needed_solution"),
                "market_universe": gap.get("market_universe"),
                "industry_domain": gap.get("industry_domain"),
                "buyer_segment": context.get("buyer_segment", "enterprise_c_suite"),
                "technical_feasibility": "high" if score >= 0.72 else "medium",
                "moat_defensibility": "data workflow plus governed source registry",
                "business_model": "enterprise subscription with premium intelligence modules",
                "productization_path": "dashboard module, pilot workflow, monitored signal pack, export-ready portfolio artifact",
                "strategic_positioning": "live governed opportunity intelligence layer",
                "acquirer_logic": "fits platform buyers needing market, governance, AI, compliance, or portfolio signal intelligence",
                "solution_score": round(min(0.99, score + 0.08), 3),
                "why_now": gap.get("why_now"),
                "status": "candidate_ready",
            })
        return {
            "status": "success",
            "engine": "solution_synthesis_engine_v1",
            "candidate_count": len(candidates),
            "candidates": sorted(candidates, key=lambda item: item["solution_score"], reverse=True),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
