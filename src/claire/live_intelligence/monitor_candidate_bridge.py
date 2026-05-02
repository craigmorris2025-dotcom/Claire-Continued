"""Convert live synthesized solutions into runnable Claire opportunity candidates."""

from __future__ import annotations

from typing import Any, Dict, List


class MonitorCandidateBridge:
    """Build candidate records compatible with OpportunityCandidateStore."""

    def build_candidates(self, monitor_result: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        candidates: List[Dict[str, Any]] = []
        for solution in (monitor_result.get("solutions") or {}).get("candidates", []):
            candidate = self._candidate(solution, context)
            candidates.append(candidate)
        return {
            "status": "success",
            "bridge": "monitor_candidate_bridge_v1",
            "candidate_count": len(candidates),
            "candidates": candidates,
        }

    def _candidate(self, solution: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        title = solution.get("title") or "Live intelligence opportunity"
        market_gap = solution.get("market_gap") or ""
        needed_solution = solution.get("needed_solution") or title
        why_now = solution.get("why_now") or "Live monitor detected a forming opportunity."
        raw_input = (
            f"Evaluate live intelligence opportunity. "
            f"Title: {title}. Market gap: {market_gap}. Needed solution: {needed_solution}. "
            f"Why now: {why_now}. Technical feasibility: {solution.get('technical_feasibility')}. "
            f"Moat/defensibility: {solution.get('moat_defensibility')}. "
            f"Business model: {solution.get('business_model')}. "
            f"Productization path: {solution.get('productization_path')}. "
            f"Strategic positioning: {solution.get('strategic_positioning')}. "
            f"Acquirer logic: {solution.get('acquirer_logic')}. "
            f"Produce an export-ready opportunity package with governance, feasibility, product, portfolio, and acquisition logic."
        )
        return {
            "title": title,
            "market_universe": solution.get("market_universe") or context.get("market_universe", "sp500_public"),
            "industry_domain": solution.get("industry_domain") or context.get("industry_domain", "cross_sector"),
            "buyer_segment": solution.get("buyer_segment") or context.get("buyer_segment", "enterprise_c_suite"),
            "objective": context.get("objective", "discover_market_gaps"),
            "workflow": context.get("workflow", "discover"),
            "execution_mode": context.get("execution_mode", "hybrid"),
            "command_id": context.get("command_id", "discover_market_gaps"),
            "opportunity_direction": solution.get("strategic_positioning"),
            "market_gap": market_gap,
            "needed_solution": needed_solution,
            "why_now": why_now,
            "selection_score": solution.get("solution_score"),
            "confidence_label": "high" if float(solution.get("solution_score", 0.0) or 0.0) >= 0.75 else "medium",
            "live_solution": solution,
            "raw_input": raw_input,
        }
