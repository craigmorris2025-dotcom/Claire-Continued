"""
Lifecycle Stage Engine — maps Claire pipeline output onto the full
21-stage Claire Intelligence Lifecycle.

Purpose:
- Make the full lifecycle visible in every run
- Separate "implemented", "active", "partial", and "pending" stages
- Prevent fake completeness while giving a clear build roadmap
"""

from typing import Any, Dict, List


class LifecycleStageEngine:
    """
    Evaluates which of Claire's 21 lifecycle stages are active,
    partially implemented, implemented, or pending for a given run.
    """

    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        context = context or {}

        stages = []
        for stage_def in self._stage_definitions():
            status_info = self._stage_status(stage_def, context)
            stages.append({
                "stage": stage_def["stage"],
                "name": stage_def["name"],
                "category": stage_def["category"],
                "status": status_info["status"],
                "active_in_run": status_info["active_in_run"],
                "evidence": status_info["evidence"],
                "output_key": stage_def.get("output_key"),
                "next_build": stage_def.get("next_build", False),
            })

        summary = self._summary(stages)

        return {
            "status": "success",
            "lifecycle_name": "Claire Intelligence Lifecycle",
            "total_stages": len(stages),
            "implemented_stage_count": summary["implemented_stage_count"],
            "active_stage_count": summary["active_stage_count"],
            "partial_stage_count": summary["partial_stage_count"],
            "pending_stage_count": summary["pending_stage_count"],
            "next_recommended_stage": self._next_recommended_stage(stages),
            "summary": summary,
            "stages": stages,
        }

    def _stage_definitions(self) -> List[Dict[str, Any]]:
        return [
            {"stage": 1, "name": "Knowledge Ingestion", "category": "knowledge", "output_key": "connector_sources"},
            {"stage": 2, "name": "Signal Extraction", "category": "knowledge", "output_key": "signal_trace"},
            {"stage": 3, "name": "Trend + Trajectory Modeling", "category": "discovery", "output_key": "trend_trajectory"},
            {"stage": 4, "name": "Market / Sector / Industry Mapping", "category": "discovery", "output_key": "market_gap"},
            {"stage": 5, "name": "Gap Detection", "category": "discovery", "output_key": "market_gap"},
            {"stage": 6, "name": "Needed Solutions Layer", "category": "discovery", "output_key": "market_gap"},
            {"stage": 7, "name": "Opportunity Discovery", "category": "discovery", "output_key": "opportunity_discovery", "next_build": True},
            {"stage": 8, "name": "Breakthrough Synthesis", "category": "breakthrough", "output_key": "scores"},
            {"stage": 9, "name": "Technical Feasibility", "category": "validation", "output_key": "scores"},
            {"stage": 10, "name": "Market Formation Analysis", "category": "validation", "output_key": "market_formation"},
            {"stage": 11, "name": "Moat / Defensibility", "category": "validation", "output_key": "moat", "next_build": True},
            {"stage": 12, "name": "Risk / Regulation / Compliance", "category": "validation", "output_key": "risk_regulation", "next_build": True},
            {"stage": 13, "name": "Productization Path", "category": "design", "output_key": "design_output"},
            {"stage": 14, "name": "Design Portal Routing", "category": "design", "output_key": "design_portal"},
            {"stage": 15, "name": "System / Technology Design Engine", "category": "design", "output_key": "design_output"},
            {"stage": 16, "name": "Technical Specs + Build Blueprint Generation", "category": "design", "output_key": "design_output"},
            {"stage": 17, "name": "Business Model + Value Capture", "category": "strategy", "output_key": "business_model", "next_build": True},
            {"stage": 18, "name": "Strategic Positioning", "category": "strategy", "output_key": "portfolio_binder"},
            {"stage": 19, "name": "Portfolio / Binder Assembly", "category": "portfolio", "output_key": "portfolio_binder"},
            {"stage": 20, "name": "Acquirer Discovery", "category": "outcome", "output_key": "acquirer_matches"},
            {"stage": 21, "name": "Deal / Exit Modeling", "category": "outcome", "output_key": "deal_modeling", "next_build": True},
        ]

    def _stage_status(self, stage_def: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        stage = stage_def["stage"]
        evidence = []
        status = "pending"
        active = False

        if stage == 1:
            connector_sources = context.get("connector_sources") or context.get("external_signals") or {}
            if connector_sources:
                status = "partial"
                active = True
                evidence.append("connector_sources available")

        elif stage == 2:
            if context.get("signal_trace") and context.get("engine_details"):
                status = "partial"
                active = True
                evidence.append("signal_trace and engine_details available")

        elif stage == 3:
            trend = context.get("trend_trajectory", {})
            if trend.get("status") == "success":
                status = "active"
                active = True
                evidence.append("trend_trajectory generated successfully")
                if trend.get("trend_direction"):
                    evidence.append(f"trend direction: {trend.get('trend_direction', {}).get('direction')}")
                if trend.get("strategic_window"):
                    evidence.append(f"strategic window: {trend.get('strategic_window', {}).get('window')}")
            else:
                evidence.append("dedicated trend_trajectory_engine unavailable")

        elif stage == 4:
            market_gap = context.get("market_gap", {})
            if market_gap.get("status") == "success" and market_gap.get("sector"):
                status = "active"
                active = True
                evidence.append(f"sector mapped: {market_gap.get('sector')}")

        elif stage == 5:
            market_gap = context.get("market_gap", {})
            if market_gap.get("market_gap"):
                status = "active"
                active = True
                evidence.append("market_gap generated")

        elif stage == 6:
            market_gap = context.get("market_gap", {})
            if market_gap.get("needed_solution") and market_gap.get("solution_class"):
                status = "active"
                active = True
                evidence.append("needed_solution and solution_class generated")

        elif stage == 7:
            market_gap = context.get("market_gap", {})
            trend = context.get("trend_trajectory", {})
            formation = context.get("market_formation", {})
            if market_gap.get("portfolio_relevance") and trend.get("status") == "success" and formation.get("status") == "success":
                status = "partial"
                active = True
                evidence.append("portfolio_relevance, trend trajectory, and market formation available, but dedicated opportunity engine pending")
            elif market_gap.get("portfolio_relevance"):
                status = "partial"
                active = True
                evidence.append("portfolio_relevance available, but dedicated opportunity engine pending")
            else:
                evidence.append("dedicated opportunity_discovery_engine not yet implemented")

        elif stage == 8:
            scores = context.get("scores", {})
            signal_trace = context.get("signal_trace", {})
            if scores.get("breakthrough_score") is not None:
                status = "partial"
                active = True
                evidence.append("breakthrough_score available")
                if signal_trace.get("breakthrough_final") is not None:
                    evidence.append("breakthrough signal trace available")

        elif stage == 9:
            scores = context.get("scores", {})
            if scores.get("feasibility_score") is not None and scores.get("buildability_score") is not None:
                status = "partial"
                active = True
                evidence.append("feasibility_score and buildability_score available")

        elif stage == 10:
            formation = context.get("market_formation", {})
            if formation.get("status") == "success":
                status = "active"
                active = True
                evidence.append("market_formation generated successfully")
                if formation.get("formation_type"):
                    evidence.append(f"formation type: {formation.get('formation_type', {}).get('type')}")
                if formation.get("market_stage"):
                    evidence.append(f"market stage: {formation.get('market_stage', {}).get('stage')}")
            else:
                evidence.append("dedicated market_formation_engine not yet implemented or unavailable")

        elif stage == 11:
            evidence.append("dedicated moat_defensibility_engine not yet implemented")

        elif stage == 12:
            evidence.append("dedicated risk_regulation_engine not yet implemented")

        elif stage == 13:
            design_output = context.get("design_output", {})
            if design_output.get("implementation_phases"):
                status = "partial"
                active = True
                evidence.append("implementation phases available from design_output")

        elif stage == 14:
            design_portal = context.get("design_portal", {})
            if design_portal.get("status"):
                status = "active" if design_portal.get("route_to_design") else "partial"
                active = bool(design_portal.get("route_to_design"))
                evidence.append(f"design_portal status: {design_portal.get('status')}")

        elif stage == 15:
            design_output = context.get("design_output", {})
            if design_output.get("status") == "success":
                status = "active"
                active = True
                evidence.append("system design engine returned success")

        elif stage == 16:
            design_output = context.get("design_output", {})
            if design_output.get("technical_specs") and design_output.get("architecture_blueprint"):
                status = "active"
                active = True
                evidence.append("technical_specs and architecture_blueprint generated")

        elif stage == 17:
            evidence.append("dedicated business_model_engine not yet implemented")

        elif stage == 18:
            binder = context.get("portfolio_binder", {})
            if self._binder_has_section(binder, "strategic_positioning"):
                status = "partial"
                active = True
                evidence.append("strategic positioning section available in binder")

        elif stage == 19:
            binder = context.get("portfolio_binder", {})
            if binder.get("status") == "success":
                status = "active"
                active = True
                evidence.append("portfolio_binder generated successfully")

        elif stage == 20:
            matches = context.get("acquirer_matches", [])
            if matches:
                status = "active"
                active = True
                evidence.append(f"{len(matches)} acquirer matches generated")

        elif stage == 21:
            evidence.append("dedicated deal_exit_modeling_engine not yet implemented")

        if status == "pending" and not evidence:
            evidence.append(f"{stage_def.get('output_key') or 'stage output'} not available")

        return {"status": status, "active_in_run": active, "evidence": evidence}

    def _binder_has_section(self, binder: Dict[str, Any], section_id: str) -> bool:
        if not isinstance(binder, dict):
            return False
        return any(section.get("id") == section_id for section in binder.get("sections", []))

    def _summary(self, stages: List[Dict[str, Any]]) -> Dict[str, Any]:
        active = [s for s in stages if s["active_in_run"]]
        partial = [s for s in stages if s["status"] == "partial"]
        pending = [s for s in stages if s["status"] == "pending"]
        implemented = [s for s in stages if s["status"] in {"active", "partial"}]

        categories = {}
        for stage in stages:
            category = stage["category"]
            categories.setdefault(category, {"total": 0, "active": 0, "partial": 0, "pending": 0})
            categories[category]["total"] += 1
            if stage["status"] == "active":
                categories[category]["active"] += 1
            elif stage["status"] == "partial":
                categories[category]["partial"] += 1
            elif stage["status"] == "pending":
                categories[category]["pending"] += 1

        return {
            "implemented_stage_count": len(implemented),
            "active_stage_count": len(active),
            "partial_stage_count": len(partial),
            "pending_stage_count": len(pending),
            "categories": categories,
            "message": (
                f"{len(implemented)} of {len(stages)} stages are implemented or partially implemented; "
                f"{len(active)} were active in this run; {len(pending)} remain pending."
            ),
        }

    def _next_recommended_stage(self, stages: List[Dict[str, Any]]) -> Dict[str, Any]:
        preferred_order = [11, 12, 17, 21]

        for preferred_stage in preferred_order:
            for stage in stages:
                if stage["stage"] == preferred_stage and stage["status"] == "pending":
                    return {
                        "stage": stage["stage"],
                        "name": stage["name"],
                        "reason": "Highest-priority missing lifecycle engine.",
                    }

        for stage in stages:
            if stage["status"] == "pending":
                return {"stage": stage["stage"], "name": stage["name"], "reason": "Next pending lifecycle stage."}

        return {"stage": None, "name": "Lifecycle complete", "reason": "No pending lifecycle stages detected."}
