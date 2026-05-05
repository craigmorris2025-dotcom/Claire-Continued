"""Route-aware Claire core output contract.

The core output is the review-ready truth object for a run. Lifecycle stages
feed it, exports package it, and UI/API surfaces can display it without
reconstructing meaning from scattered engine payloads.
"""

from __future__ import annotations

from typing import Any, Dict, List


class CoreOutputBuilder:
    version = "v5.90_core_output_contract"

    def build(
        self,
        run_id: str,
        data: Dict[str, Any],
        scores: Dict[str, Any],
        decision_classification: str,
        breakthrough_classification: str,
        core_lifecycle: Dict[str, Any],
        export_package: Dict[str, Any],
    ) -> Dict[str, Any]:
        data = data or {}
        scores = scores or {}
        core_lifecycle = core_lifecycle or {}
        export_package = export_package or {}
        gate = core_lifecycle.get("completion_gate", {}) or {}
        status = self._status(gate, data)
        route_selected = self._route_selected(core_lifecycle, data, scores, status)

        user_facing_result = self.build_user_facing_result(
            run_id=run_id,
            status=status,
            route_selected=route_selected,
            data=data,
            scores=scores,
            export_package=export_package,
        )
        output = {
            "version": self.version,
            "run_id": run_id or "unknown",
            "status": status,
            "route_selected": route_selected,
            "scan_iterations": data.get("scan_iterations", []),
            "user_facing_result": user_facing_result,
            "run_summary": self._run_summary(data, scores, decision_classification, breakthrough_classification, route_selected),
            "lifecycle_summary": self._lifecycle_summary(core_lifecycle),
            "signal_basis": self._signal_basis(data),
            "trend_discovery": data.get("trend_discovery", {}),
            "thesis": data.get("thesis_formation", {}),
            "discovery": self._discovery(data, scores),
            "portfolio": self._portfolio(data, scores),
            "breakthrough": self._breakthrough(data, scores),
            "advancement_path": self._advancement_path(data, route_selected),
            "technology_intelligence": self._technology_intelligence(data, route_selected),
            "autodesign": self._autodesign(data, route_selected),
            "solution": self._solution(data, route_selected),
            "validation": self._validation(data, scores),
            "design_portal": self._design_portal(data, route_selected),
            "design_output": data.get("design_output", {}),
            "strategy": self._strategy(data, scores),
            "acquisition": self._acquisition(data, scores),
            "final_package": self._final_package(export_package, data),
            "evidence": self._evidence(data, core_lifecycle),
            "confidence": self._confidence(scores, data, core_lifecycle),
            "failures": self._failures(data, core_lifecycle, status),
            "next_actions": self._next_actions(data, status, route_selected),
        }
        output["contract_validation"] = self._validate(output)
        return output

    def build_user_facing_result(
        self,
        run_id: str,
        status: str,
        route_selected: str,
        data: Dict[str, Any],
        scores: Dict[str, Any],
        export_package: Dict[str, Any],
    ) -> Dict[str, Any]:
        trend = data.get("trend_discovery", {}) or {}
        thesis = data.get("thesis_formation", {}) or {}
        portfolio = data.get("portfolio_optimization", {}) or {}
        breakthrough = self._breakthrough(data, scores)
        package_profile = export_package.get("package_profile", {}) if isinstance(export_package, dict) else {}
        headline = self._headline(route_selected, trend, thesis, portfolio, package_profile)
        summary = self._external_summary(route_selected, trend, thesis, portfolio, breakthrough, data)
        return {
            "run_id": run_id or "unknown",
            "status": status,
            "headline": headline,
            "summary": summary,
            "route_selected": route_selected,
            "trend": trend,
            "thesis": thesis,
            "discovery": self._discovery(data, scores),
            "portfolio": self._portfolio(data, scores),
            "breakthrough": breakthrough,
            "advancement_path": self._advancement_path(data, route_selected),
            "technology_intelligence": self._technology_intelligence(data, route_selected),
            "autodesign": self._autodesign(data, route_selected),
            "solution": self._solution(data, route_selected),
            "design_portal": self._design_portal(data, route_selected),
            "strategy": self._strategy(data, scores),
            "acquisition": self._acquisition(data, scores),
            "final_package": self._final_package(export_package, data),
            "confidence": self._confidence(scores, data, data.get("core_lifecycle", {})),
            "next_actions": self._next_actions(data, status, route_selected),
        }

    def _status(self, gate: Dict[str, Any], data: Dict[str, Any]) -> str:
        scan_terminal_state = data.get("scan_terminal_state")
        if scan_terminal_state in {"blocked", "insufficient_data", "failed"}:
            return str(scan_terminal_state)
        if scan_terminal_state == "max_iterations_reached":
            return "incomplete"
        gate_status = gate.get("status")
        if gate_status in {"blocked", "insufficient_data", "failed"}:
            return gate_status
        if gate_status == "incomplete":
            return "incomplete"
        failures = self._engine_failures(data)
        return "failed" if failures else "complete"

    def _route_selected(self, core_lifecycle: Dict[str, Any], data: Dict[str, Any], scores: Dict[str, Any], status: str) -> str:
        if status in {"blocked", "insufficient_data", "failed"}:
            return f"{status}_output"
        route = core_lifecycle.get("route") or "portfolio_only"
        scan_route = data.get("scan_route_selected")
        if scan_route and status not in {"blocked", "insufficient_data", "failed"}:
            return str(scan_route)
        portfolio_path = self._get_text(data.get("portfolio_optimization", {}), "portfolio_path")
        thesis_route = self._get_text(data.get("thesis_formation", {}), "route_recommendation")
        design_status = self._get_text(data.get("design_output", {}), "status")
        acquisition_score = self._float(scores.get("acquisition_score"))

        if design_status in {"success", "design_ready"}:
            return "solution_design"
        if route == "breakthrough_design" or thesis_route == "breakthrough_escalation_candidate":
            return "breakthrough_escalation"
        if acquisition_score >= 0.78:
            return "acquisition_package"
        if portfolio_path:
            return "portfolio_creation_optimization"
        return "trend_thesis"

    def _run_summary(
        self,
        data: Dict[str, Any],
        scores: Dict[str, Any],
        decision: str,
        breakthrough: str,
        route: str,
    ) -> Dict[str, Any]:
        package_profile = self._get(data, "export_package.package_profile", {})
        return {
            "decision": decision,
            "breakthrough_classification": breakthrough,
            "route_selected": route,
            "domain": data.get("domain"),
            "keywords": data.get("keywords", []),
            "category_name": package_profile.get("category_name") if isinstance(package_profile, dict) else None,
            "portfolio_score": self._float(scores.get("portfolio_score")),
            "confidence": self._float(scores.get("_confidence") or scores.get("portfolio_score")),
        }

    def _headline(
        self,
        route: str,
        trend: Dict[str, Any],
        thesis: Dict[str, Any],
        portfolio: Dict[str, Any],
        package_profile: Dict[str, Any],
    ) -> str:
        category = package_profile.get("category_name") if isinstance(package_profile, dict) else ""
        trend_name = ""
        trends = trend.get("discovered_trends") if isinstance(trend, dict) else []
        if trends and isinstance(trends[0], dict):
            trend_name = trends[0].get("name", "")
        label = category or trend_name or "market intelligence opportunity"
        route_label = str(route or "trend_thesis").replace("_", " ")
        if route == "portfolio_creation_optimization":
            path = portfolio.get("portfolio_path") if isinstance(portfolio, dict) else ""
            return f"{label}: {path or 'portfolio optimization'}"
        if route == "breakthrough_escalation":
            return f"{label}: breakthrough escalation candidate"
        if route == "solution_design":
            return f"{label}: solution/design route"
        if route == "acquisition_package":
            return f"{label}: acquisition-ready package"
        if route.endswith("_output"):
            return f"{label}: {route_label}"
        return f"{label}: trend thesis formed"

    def _external_summary(
        self,
        route: str,
        trend: Dict[str, Any],
        thesis: Dict[str, Any],
        portfolio: Dict[str, Any],
        breakthrough: Dict[str, Any],
        data: Dict[str, Any],
    ) -> str:
        thesis_statement = thesis.get("thesis_statement") if isinstance(thesis, dict) else ""
        trend_label = ""
        trends = trend.get("discovered_trends") if isinstance(trend, dict) else []
        if trends and isinstance(trends[0], dict):
            trend_label = trends[0].get("name", "")
        portfolio_path = portfolio.get("portfolio_path") if isinstance(portfolio, dict) else ""
        if route == "portfolio_creation_optimization" and portfolio_path:
            return f"Claire detected {trend_label or 'a qualified trend'} and recommends the {portfolio_path.replace('_', ' ')} path. {thesis_statement}"
        if route == "breakthrough_escalation":
            return f"Claire detected {trend_label or 'a qualified trend'} with breakthrough characteristics. {breakthrough.get('classification_rationale', '')}"
        if route == "solution_design":
            return f"Claire selected a solution/design route from the detected gap and validation path. {thesis_statement}"
        if route == "acquisition_package":
            return f"Claire packaged the opportunity for acquisition-readiness review. {thesis_statement}"
        if route.endswith("_output"):
            return "Claire could not complete a credible external intelligence output. Review missing data and blocked stages before continuing."
        return thesis_statement or f"Claire detected {trend_label or 'a trend'} and formed an initial market intelligence thesis."

    def _lifecycle_summary(self, core_lifecycle: Dict[str, Any]) -> Dict[str, Any]:
        summary = core_lifecycle.get("summary", {}) or {}
        gate = core_lifecycle.get("completion_gate", {}) or {}
        return {
            "route": core_lifecycle.get("route"),
            "stage_count": core_lifecycle.get("stage_count"),
            "status_counts": summary.get("status_counts", {}),
            "completion_gate": gate,
            "stages": [
                {
                    "number": stage.get("number"),
                    "id": stage.get("id"),
                    "name": stage.get("name"),
                    "status": stage.get("status"),
                    "missing_outputs": stage.get("missing_outputs", []),
                }
                for stage in core_lifecycle.get("stages", [])
            ],
        }

    def _signal_basis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        governed = data.get("governed_signals", {}) or {}
        return {
            "governed_signals": governed,
            "knowledge_ingestion": data.get("knowledge_ingestion", {}),
            "signal_extraction": data.get("signal_extraction", {}),
            "source_summary": {
                "connector_sources_present": bool(data.get("connector_sources")),
                "accepted_signal_count": governed.get("accepted_signal_count"),
                "source_count": self._get(data.get("knowledge_ingestion", {}), "source_inventory.source_count", 0),
                "scan_terminal_state": data.get("scan_terminal_state"),
                "scan_terminal_reason": data.get("scan_terminal_reason"),
            },
        }

    def _discovery(self, data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "opportunity_discovery": data.get("opportunity_discovery", {}),
            "scan_terminal_state": data.get("scan_terminal_state"),
            "scan_terminal_reason": data.get("scan_terminal_reason"),
            "scan_iteration_count": len(data.get("scan_iterations", []) or []),
            "confidence": self._float(scores.get("discovery_score") or scores.get("opportunity_score")),
        }

    def _portfolio(self, data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "portfolio_binder": data.get("portfolio_binder", {}),
            "portfolio_optimization": data.get("portfolio_optimization", {}),
            "portfolio_score": self._float(scores.get("portfolio_score")),
            "optimization_score": self._float(scores.get("portfolio_optimization_score")),
            "opportunity_map": self._get(data.get("opportunity_discovery", {}), "opportunity_map", {}),
            "exposure_notes": self._get(data.get("portfolio_optimization", {}), "constraints", []),
        }

    def _breakthrough(self, data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        synthesis = data.get("breakthrough_synthesis", {}) or {}
        classification = self._get_text(synthesis, "breakthrough_classification.classification")
        primary_type = self._primary_breakthrough_type(data, synthesis)
        breakthrough_score = self._float(scores.get("breakthrough_score"))
        is_breakthrough = breakthrough_score >= 0.65 or bool(classification)
        return {
            "is_breakthrough": is_breakthrough,
            "primary_type": primary_type if is_breakthrough else None,
            "secondary_types": self._secondary_breakthrough_types(data, synthesis),
            "classification": classification,
            "classification_rationale": self._breakthrough_rationale(data, scores),
            "route_recommendation": self._get_text(data.get("thesis_formation", {}), "route_recommendation") or "portfolio_intelligence",
            "trigger_signals": self._get(data.get("trend_discovery", {}), "discovered_trends", []),
            "score": breakthrough_score,
        }

    def _advancement_path(self, data: Dict[str, Any], route: str) -> Dict[str, Any]:
        portal = data.get("design_portal", {}) or {}
        portfolio = data.get("portfolio_optimization", {}) or {}
        return {
            "route_selected": route,
            "design_portal": portal,
            "portfolio_path": portfolio.get("portfolio_path"),
            "downstream_action": self._downstream_action(route, data),
        }

    def _solution(self, data: Dict[str, Any], route: str) -> Dict[str, Any]:
        design_output = data.get("design_output", {}) or {}
        system_design = data.get("system_design", {}) or {}
        routed = route == "solution_design" or design_output.get("status") in {"success", "design_ready"}
        return {
            "applicable": routed,
            "trigger": data.get("market_gap", {}),
            "system_design": system_design if routed else {},
            "solution_output": design_output if routed else {},
            "reason": "solution/design route selected" if routed else "solution/design not required for selected route",
        }

    def _design_required(self, route: str, data: Dict[str, Any]) -> bool:
        route_text = " ".join(str(item or "").lower() for item in [
            route,
            self._get_text(data.get("thesis_formation", {}), "route_recommendation"),
            self._get_text(data.get("design_portal", {}), "selected_advancement_path"),
        ])
        design_terms = [
            "design",
            "invention",
            "architecture",
            "software",
            "platform",
            "operational redesign",
            "replacement",
            "technical",
            "business system",
        ]
        return any(term in route_text for term in design_terms) or route == "solution_design"

    def _autodesign(self, data: Dict[str, Any], route: str) -> Dict[str, Any]:
        required = self._design_required(route, data)
        system_design = data.get("system_design", {}) or {}
        system_design_inner = system_design.get("design", {}) if isinstance(system_design.get("design"), dict) else {}
        design_output = data.get("design_output", {}) or {}
        portal = data.get("design_portal", {}) or {}
        technology = self._technology_intelligence(data, route)
        triggered = required and bool(system_design) and system_design.get("status") not in {"not_routed", "design_failed"}
        status = "complete" if triggered and design_output.get("status") in {"success", "design_ready"} else "triggered" if triggered else "not_required"
        if required and not triggered:
            status = "insufficient_data" if not system_design else "blocked"
        return {
            "triggered": triggered,
            "trigger_source": self._get_text(portal, "trigger_source") or self._get_text(data.get("market_gap", {}), "gap_type") or route,
            "selected_advancement_path": route,
            "design_type": self._get_text(system_design_inner, "system_type") or self._get_text(design_output, "design_type"),
            "system_type": self._get_text(system_design_inner, "system_type") or self._get_text(design_output, "system_type"),
            "intended_function": self._get_text(system_design_inner, "intended_function") or "route-aware intelligence/design execution",
            "concept": self._get_text(system_design_inner, "concept") or self._get_text(system_design_inner, "design_concept") or self._get_text(design_output, "concept"),
            "components": self._list_from(system_design_inner, ["components", "core_components"]) or self._list_from(design_output, ["components", "core_components", "component_map"]),
            "dependencies": self._list_from(system_design_inner, ["dependencies"]) or self._list_from(design_output, ["dependencies", "dependency_map"]),
            "constraints": self._list_from(system_design_inner, ["constraints"]) or self._list_from(data.get("technical_feasibility", {}), ["constraints"]),
            "risks": self._list_from(system_design_inner, ["risks"]) or self._list_from(data.get("risk_regulation", {}), ["risks"]),
            "implementation_phases": self._list_from(system_design_inner, ["implementation_phases"]) or self._list_from(design_output, ["implementation_phases", "build_phases"]),
            "selected_technologies": technology.get("technologies_considered", []),
            "selected_stack": technology.get("selected_stack", {}),
            "status": "not_required" if not required else status,
        }

    def _technology_intelligence(self, data: Dict[str, Any], route: str) -> Dict[str, Any]:
        required = self._design_required(route, data)
        existing = data.get("technology_intelligence", {}) if isinstance(data.get("technology_intelligence"), dict) else {}
        if not required:
            return {
                "required": False,
                "technologies_considered": [],
                "selected_stack": {},
                "component_matches": [],
                "compatibility_notes": ["Technology Intelligence skipped by route."],
                "dependency_notes": [],
                "search_queries": [],
                "integration_complexity": "not_required",
                "buildability_notes": ["Design/system/technology route was not selected."],
                "confidence": 0.0,
                "status": "skipped_by_route",
            }
        return {
            "required": True,
            "technologies_considered": existing.get("technologies_considered", []),
            "selected_stack": existing.get("selected_stack", {}),
            "component_matches": existing.get("component_matches", []),
            "compatibility_notes": existing.get("compatibility_notes", ["Technology Intelligence missing."]),
            "dependency_notes": existing.get("dependency_notes", []),
            "search_queries": existing.get("search_queries", data.get("keywords", [])),
            "integration_complexity": existing.get("integration_complexity", "unknown"),
            "buildability_notes": existing.get("buildability_notes", ["Add technology catalog recommendations before design packaging."]),
            "confidence": self._float(existing.get("confidence")),
            "status": existing.get("status", "missing"),
        }

    def _design_portal(self, data: Dict[str, Any], route: str) -> Dict[str, Any]:
        required = self._design_required(route, data)
        portal = data.get("design_portal", {}) or {}
        design_output = data.get("design_output", {}) or {}
        system_design = data.get("system_design", {}) or {}
        available = required and bool(portal) and portal.get("status") not in {"portal_failed", "not_routed"}
        complete = design_output.get("status") in {"success", "design_ready"} or portal.get("status") in {"success", "complete", "design_ready"}
        status = "not_required" if not required else "complete" if complete else "pending" if available else "insufficient_data"
        return {
            "required": required,
            "available": available,
            "architecture_summary": self._get_text(system_design, "architecture_summary") or self._get_text(design_output, "architecture_summary"),
            "blueprint_summary": self._get_text(design_output, "blueprint_summary") or self._get_text(portal, "blueprint_summary"),
            "specifications": self._list_from(design_output, ["specifications", "specs"]),
            "component_map": self._list_from(design_output, ["component_map", "components"]) or self._list_from(system_design, ["component_map", "components"]),
            "dependency_map": self._list_from(design_output, ["dependency_map", "dependencies"]) or self._list_from(system_design, ["dependency_map", "dependencies"]),
            "technology_stack": self._technology_intelligence(data, route).get("selected_stack", {}),
            "build_phases": self._list_from(design_output, ["build_phases", "implementation_phases"]) or self._list_from(system_design, ["build_phases", "implementation_phases"]),
            "validation_status": self._get_text(data.get("technical_feasibility", {}), "feasibility_classification.classification") or self._get_text(data.get("technical_feasibility", {}), "status"),
            "export_path": self._get_text(data.get("export_writer", {}), "output_dir"),
            "status": "not_required" if not required else status,
        }

    def _validation(self, data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "technical_feasibility": data.get("technical_feasibility", {}),
            "productization_path": data.get("productization_path", {}),
            "viability": data.get("business_model", {}),
            "scores": {
                "viability_score": self._float(scores.get("viability_score")),
                "buildability_score": self._float(scores.get("buildability_score")),
                "feasibility_score": self._float(scores.get("feasibility_score")),
                "technical_feasibility_score": self._float(scores.get("technical_feasibility_score")),
            },
        }

    def _strategy(self, data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "strategic_positioning": data.get("strategic_positioning", {}),
            "moat": data.get("moat", {}),
            "business_model": data.get("business_model", {}),
            "market_formation": data.get("market_formation", {}),
            "scores": {
                "strategic_positioning_score": self._float(scores.get("strategic_positioning_score")),
                "narrative_strength_score": self._float(scores.get("narrative_strength_score")),
            },
        }

    def _acquisition(self, data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "deal_exit_modeling": data.get("deal_exit_modeling", {}),
            "acquirer_matches": data.get("acquirer_matches", []),
            "scores": {
                "acquisition_score": self._float(scores.get("acquisition_score")),
                "matching_score": self._float(scores.get("matching_score")),
                "acquirer_positioning_score": self._float(scores.get("acquirer_positioning_score")),
            },
        }

    def _final_package(self, export_package: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        profile = export_package.get("package_profile", {}) or {}
        readiness = export_package.get("export_package_score", {}) or {}
        return {
            "status": export_package.get("status"),
            "package_profile": profile,
            "export_readiness": readiness,
            "quality_checks": export_package.get("quality_checks", {}),
            "document_manifest": export_package.get("package_manifest", []),
            "export_writer": data.get("export_writer", {}),
        }

    def _evidence(self, data: Dict[str, Any], core_lifecycle: Dict[str, Any]) -> List[Dict[str, Any]]:
        items = []
        for key in [
            "governed_signals",
            "trend_discovery",
            "thesis_formation",
            "portfolio_optimization",
            "breakthrough_synthesis",
            "technical_feasibility",
            "strategic_positioning",
            "deal_exit_modeling",
        ]:
            payload = data.get(key)
            if payload:
                items.append({"key": key, "status": payload.get("status") if isinstance(payload, dict) else "present", "payload": payload})
        gate = core_lifecycle.get("completion_gate")
        if gate:
            items.append({"key": "core_completion_gate", "status": gate.get("status"), "payload": gate})
        return items

    def _confidence(self, scores: Dict[str, Any], data: Dict[str, Any], core_lifecycle: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "overall": self._float(scores.get("_confidence") or scores.get("portfolio_score")),
            "trend": self._float(scores.get("trend_discovery_score")),
            "thesis": self._float(scores.get("thesis_score")),
            "portfolio": self._float(scores.get("portfolio_score")),
            "portfolio_optimization": self._float(scores.get("portfolio_optimization_score")),
            "breakthrough": self._float(scores.get("breakthrough_score")),
            "validation": self._float(scores.get("feasibility_score")),
            "acquisition": self._float(scores.get("acquisition_score")),
            "lifecycle_gate": (core_lifecycle.get("completion_gate") or {}).get("status"),
        }

    def _failures(self, data: Dict[str, Any], core_lifecycle: Dict[str, Any], status: str) -> List[Dict[str, Any]]:
        failures = self._engine_failures(data)
        gate = core_lifecycle.get("completion_gate", {}) or {}
        for stage in gate.get("insufficient_data_stages", []) or []:
            failures.append({
                "type": "insufficient_data",
                "stage": stage.get("name"),
                "stage_id": stage.get("stage_id"),
                "missing_data": stage.get("missing_outputs", []),
            })
        for stage in gate.get("blocked_stages", []) or []:
            failures.append({"type": "blocked", "stage": stage.get("name"), "stage_id": stage.get("stage_id")})
        if status in {"blocked", "insufficient_data"} and not failures:
            failures.append({"type": status, "stage": "unknown", "missing_data": []})
        return failures

    def _next_actions(self, data: Dict[str, Any], status: str, route: str) -> List[Dict[str, str]]:
        if status in {"blocked", "insufficient_data", "failed"}:
            return [{
                "action": "resolve missing or blocked lifecycle data",
                "purpose": "restore credible pipeline continuation before packaging the output",
                "priority": "critical",
            }]
        if route == "solution_design":
            return [{"action": "review design output and validation gates", "purpose": "confirm solution route is justified before build work", "priority": "high"}]
        if route == "breakthrough_escalation":
            return [{"action": "review breakthrough type and advancement path", "purpose": "select portfolio, acquisition, business model, operations, regulatory, architecture, or design route", "priority": "high"}]
        if route == "acquisition_package":
            return [{"action": "review acquirer fit and objections", "purpose": "prepare controlled acquisition-readiness package", "priority": "high"}]
        if route == "portfolio_creation_optimization":
            return [{"action": "review portfolio optimization recommendation", "purpose": "decide whether to validate, watchlist, or package the portfolio candidate", "priority": "high"}]
        return [{"action": "review trend thesis", "purpose": "decide whether to continue portfolio intelligence or escalate", "priority": "medium"}]

    def _validate(self, output: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "run_id",
            "status",
            "route_selected",
            "scan_iterations",
            "lifecycle_summary",
            "signal_basis",
            "trend_discovery",
            "thesis",
            "discovery",
            "portfolio",
            "breakthrough",
            "advancement_path",
            "technology_intelligence",
            "autodesign",
            "validation",
            "design_portal",
            "strategy",
            "acquisition",
            "final_package",
            "evidence",
            "confidence",
            "failures",
            "next_actions",
        ]
        missing = [key for key in required if key not in output]
        return {
            "status": "complete" if not missing else "incomplete",
            "required_fields": required,
            "missing_fields": missing,
        }

    def _engine_failures(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        failures = []
        for key, value in data.items():
            if isinstance(value, dict) and str(value.get("status", "")).endswith("_failed"):
                failures.append({"type": "engine_failed", "engine": key, "status": value.get("status"), "error": value.get("error")})
        return failures

    def _primary_breakthrough_type(self, data: Dict[str, Any], synthesis: Dict[str, Any]) -> str:
        text = " ".join(str(item).lower() for item in [
            self._get_text(synthesis, "breakthrough_classification.classification"),
            self._get_text(data.get("market_gap", {}), "solution_class"),
            self._get_text(data.get("portfolio_optimization", {}), "portfolio_path"),
        ])
        if "portfolio" in text:
            return "portfolio_optimization"
        if "regulatory" in text:
            return "regulatory"
        if "business" in text:
            return "business_model"
        if "architecture" in text or "system" in text:
            return "system_architecture"
        if "acquisition" in text:
            return "acquisition_strategy"
        return "structural_advancement"

    def _secondary_breakthrough_types(self, data: Dict[str, Any], synthesis: Dict[str, Any]) -> List[str]:
        types = []
        if data.get("portfolio_optimization"):
            types.append("portfolio_construction")
        if data.get("business_model"):
            types.append("business_model")
        if data.get("strategic_positioning"):
            types.append("market_positioning")
        if data.get("deal_exit_modeling"):
            types.append("acquisition_strategy")
        if data.get("technical_feasibility"):
            types.append("deployability")
        return types

    def _breakthrough_rationale(self, data: Dict[str, Any], scores: Dict[str, Any]) -> str:
        return (
            "Breakthrough qualification is based on trend/thesis evidence, market gap pressure, "
            f"portfolio score {self._float(scores.get('portfolio_score')):.4f}, and breakthrough score "
            f"{self._float(scores.get('breakthrough_score')):.4f}. Breakthrough does not automatically imply invention."
        )

    def _downstream_action(self, route: str, data: Dict[str, Any]) -> str:
        return {
            "trend_thesis": "review thesis and decide whether to continue portfolio intelligence",
            "portfolio_creation_optimization": "review allocation hypothesis and portfolio constraints",
            "breakthrough_escalation": "classify breakthrough type and select downstream route",
            "solution_design": "review design portal output and validation requirements",
            "acquisition_package": "review acquirer fit and package readiness",
            "insufficient_data_output": "supply missing lifecycle data",
            "blocked_output": "resolve blocked lifecycle stage",
            "failed_output": "repair failed engine output",
        }.get(route, "review route output")

    def _get(self, obj: Dict[str, Any], path: str, default: Any = None) -> Any:
        cur: Any = obj if isinstance(obj, dict) else {}
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

    def _get_text(self, obj: Dict[str, Any], path: str) -> str:
        value = self._get(obj, path, "")
        return str(value or "")

    def _float(self, value: Any) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def _list_from(self, obj: Dict[str, Any], keys: List[str]) -> List[Any]:
        if not isinstance(obj, dict):
            return []
        for key in keys:
            value = obj.get(key)
            if isinstance(value, list):
                return value
            if value:
                return [value]
        return []
