"""
System Design Engine — generates sector-aware technical blueprints,
technical specs, component maps, and implementation plans.

v5.20 sector wording cleanup:
- Removes generic/autonomy template bleed from non-autonomy sectors.
- Adds climate-insurance-specific architecture, requirements, controls, and
  implementation phases.
- Keeps the same design_output contract expected by the binder and lifecycle.
"""

from typing import Any, Dict, List


class SystemDesignEngine:
    """
    Deterministic sector-aware system design generator.
    """

    def generate(self, design_portal: Dict[str, Any]) -> Dict[str, Any]:
        design_portal = design_portal or {}

        inputs = design_portal.get("inputs", {}) if isinstance(design_portal, dict) else {}

        market_gap = (
            design_portal.get("market_gap")
            or inputs.get("market_gap")
            or {}
        )

        scores = inputs.get("scores") or design_portal.get("scores") or {}

        system_design = (
            inputs.get("system_design")
            or design_portal.get("system_design")
            or {}
        )
        technology_intelligence = (
            design_portal.get("technology_intelligence")
            or inputs.get("technology_intelligence")
            or {}
        )

        system_design_inner = system_design.get("design", {}) if isinstance(system_design, dict) else {}

        domain = (
            design_portal.get("domain")
            or inputs.get("domain")
            or market_gap.get("domain")
            or system_design_inner.get("inferred_domain")
            or "general"
        )

        sector = market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general"
        solution_class = market_gap.get("solution_class", "intelligence platform") if isinstance(market_gap, dict) else "intelligence platform"
        needed_solution = market_gap.get("needed_solution", "Validated intelligence system") if isinstance(market_gap, dict) else "Validated intelligence system"

        system_type = system_design_inner.get("system_type", "ai_platform")
        architecture = system_design_inner.get("architecture", "modular")

        technical_specs = self._technical_specs(
            domain=domain,
            sector=sector,
            system_type=system_type,
            market_gap=market_gap,
            scores=scores,
        )

        architecture_blueprint = self._architecture_blueprint(
            domain=domain,
            sector=sector,
            architecture=architecture,
            market_gap=market_gap,
        )

        implementation_phases = self._implementation_phases(
            domain=domain,
            sector=sector,
            solution_class=solution_class,
        )

        portfolio_artifacts = self._portfolio_artifacts(
            domain=domain,
            sector=sector,
            system_type=system_type,
            market_gap=market_gap,
            scores=scores,
        )

        return {
            "status": "success",
            "design_type": "technical_system_blueprint",
            "domain": domain,
            "system_type": system_type,
            "architecture": architecture,
            "market_gap": market_gap,
            "technical_specs": technical_specs,
            "architecture_blueprint": architecture_blueprint,
            "technology_stack": technology_intelligence.get("selected_stack", {}),
            "component_matches": technology_intelligence.get("component_matches", []),
            "compatibility_notes": technology_intelligence.get("compatibility_notes", []),
            "dependency_notes": technology_intelligence.get("dependency_notes", []),
            "data_flows": self._data_flows(sector),
            "implementation_phases": implementation_phases,
            "portfolio_artifacts": portfolio_artifacts,
            "readiness": self._readiness(scores),
        }

    # =========================
    # TECHNICAL SPECS
    # =========================
    def _technical_specs(
        self,
        domain: str,
        sector: str,
        system_type: str,
        market_gap: Dict[str, Any],
        scores: Dict[str, Any],
    ) -> Dict[str, Any]:
        sector_specs = self._sector_specs(sector)
        design_implications = market_gap.get("design_implications", []) if isinstance(market_gap, dict) else []

        core_requirements = [
            "modular service architecture",
            "structured input-output contracts",
            "traceable decision pipeline",
            "explainable scoring and design rationale",
            "model monitoring and audit trail",
            "portfolio-ready artifact generation",
        ]

        core_requirements.extend(sector_specs["core_requirements"])

        for item in design_implications:
            normalized = self._slug_to_phrase(item)
            if normalized not in core_requirements:
                core_requirements.append(normalized)

        return {
            "primary_domain": domain,
            "system_type": system_type,
            "market_gap_sector": sector,
            "needed_solution": market_gap.get("needed_solution"),
            "solution_class": market_gap.get("solution_class"),
            "capability_targets": sector_specs["capability_targets"],
            "performance_targets": {
                "breakthrough_intensity": round(float(scores.get("breakthrough_score", 0.0) or 0.0), 4),
                "feasibility_threshold": round(float(scores.get("feasibility_score", 0.0) or 0.0), 4),
                "portfolio_confidence": round(float(scores.get("portfolio_score", 0.0) or 0.0), 4),
            },
            "core_requirements": sorted(list(dict.fromkeys(core_requirements))),
            "sector_controls": sector_specs["sector_controls"],
            "validation_targets": sector_specs["validation_targets"],
        }

    def _architecture_blueprint(
        self,
        domain: str,
        sector: str,
        architecture: str,
        market_gap: Dict[str, Any],
    ) -> Dict[str, Any]:
        sector_specs = self._sector_specs(sector)

        modules = [
            {
                "component": "ingestion",
                "role": "collects, validates, and normalizes source data",
                "interfaces": ["raw_input", "source_metadata", "normalized_payload"],
                "priority": "critical",
            },
            {
                "component": "semantic_processing",
                "role": "extracts entities, domain concepts, risk signals, and opportunity context",
                "interfaces": ["normalized_payload", "semantic_context"],
                "priority": "high",
            },
            {
                "component": "analysis_engines",
                "role": "evaluates trends, gaps, market formation, risk, feasibility, moat, and deal readiness",
                "interfaces": ["semantic_context", "signals", "scores"],
                "priority": "high",
            },
            {
                "component": "decision_layer",
                "role": "classifies decision states, readiness, blocker status, and routing outcomes",
                "interfaces": ["scores", "decision_state", "readiness_flags"],
                "priority": "critical",
            },
            {
                "component": "api_gateway",
                "role": "exposes system capabilities to applications and users",
                "interfaces": ["request", "response", "external_clients"],
                "priority": "medium",
            },
        ]

        modules.extend(sector_specs["modules"])

        return {
            "architecture_style": architecture,
            "domain_context": domain,
            "market_gap_context": sector,
            "modules": self._dedupe_modules(modules),
            "recommended_services": sector_specs["recommended_services"],
            "security_model": sector_specs["security_model"],
            "operational_model": sector_specs["operational_model"],
        }

    def _data_flows(self, sector: str) -> List[Dict[str, str]]:
        flows = [
            {
                "from": "ingestion",
                "to": "semantic_processing",
                "payload": "validated_structured_context",
                "validation": "schema_and_source_checked",
            },
            {
                "from": "semantic_processing",
                "to": "analysis_engines",
                "payload": "semantic_context_and_domain_signals",
                "validation": "contract_checked",
            },
            {
                "from": "analysis_engines",
                "to": "decision_layer",
                "payload": "scores_risk_states_and_recommendations",
                "validation": "traceable_score_bundle",
            },
            {
                "from": "decision_layer",
                "to": "api_gateway",
                "payload": "structured_response_and_artifacts",
                "validation": "response_contract_checked",
            },
        ]

        if sector == "climate_insurance":
            flows.extend([
                {
                    "from": "weather_loss_ingestion",
                    "to": "exposure_modeling_service",
                    "payload": "weather_loss_property_and_exposure_records",
                    "validation": "lineage_and_quality_checked",
                },
                {
                    "from": "catastrophe_scenario_engine",
                    "to": "underwriting_repricing_detector",
                    "payload": "scenario_outputs_and_repricing_signals",
                    "validation": "model_confidence_checked",
                },
                {
                    "from": "underwriting_repricing_detector",
                    "to": "risk_transfer_recommendation_layer",
                    "payload": "repricing_pressure_and_exposure_concentration",
                    "validation": "underwriter_review_required",
                },
            ])

        elif sector == "defense_autonomy":
            flows.extend([
                {
                    "from": "mission_context_ingestion",
                    "to": "mission_simulation_engine",
                    "payload": "mission_context_sensor_inputs_operational_constraints",
                    "validation": "allowed_use_and_source_authorization_checked",
                },
                {
                    "from": "mission_simulation_engine",
                    "to": "coordination_risk_model",
                    "payload": "scenario_outputs_coordination_risks_decision_options",
                    "validation": "simulation_confidence_and_scenario_version_checked",
                },
                {
                    "from": "coordination_risk_model",
                    "to": "secure_command_adapter",
                    "payload": "ranked_advisory_recommendations_and_evidence_trace",
                    "validation": "secure_command_policy_checked",
                },
                {
                    "from": "secure_command_adapter",
                    "to": "human_override_layer",
                    "payload": "review_queue_authorization_state_and_required_controls",
                    "validation": "human_authorization_required",
                },
                {
                    "from": "human_override_layer",
                    "to": "mission_audit_service",
                    "payload": "approval_state_override_log_allowed_use_trace",
                    "validation": "audit_trail_retained",
                },
            ])

        elif sector == "financial_market_intelligence":
            flows.extend([
                {
                    "from": "market_signal_ingestion",
                    "to": "regime_modeling_service",
                    "payload": "market_credit_liquidity_and_macro_signals",
                    "validation": "timestamp_and_source_checked",
                },
                {
                    "from": "regime_modeling_service",
                    "to": "risk_signal_ranking",
                    "payload": "risk_scores_and_repricing_probabilities",
                    "validation": "model_governance_checked",
                },
            ])

        elif sector == "industrial_supply_chain":
            flows.extend([
                {
                    "from": "supplier_data_connector",
                    "to": "supplier_dependency_graph",
                    "payload": "supplier_component_and_procurement_records",
                    "validation": "erp_permission_checked",
                },
                {
                    "from": "shortage_forecast_engine",
                    "to": "procurement_recommendation_layer",
                    "payload": "shortage_risk_and_countermeasures",
                    "validation": "operator_review_required",
                },
            ])

        return flows

    # =========================
    # IMPLEMENTATION / ARTIFACTS
    # =========================
    def _implementation_phases(self, domain: str, sector: str, solution_class: str) -> List[Dict[str, Any]]:
        sector_specs = self._sector_specs(sector)

        phases = [
            {
                "phase": 1,
                "name": "Foundation",
                "objective": "Establish contracts, ingestion, routing, traceability, and result schema.",
                "deliverables": [
                    "domain contracts",
                    "pipeline routing",
                    "input validation",
                    "baseline scoring trace",
                    "structured result schema",
                ],
            },
            {
                "phase": 2,
                "name": "Sector Data Foundation",
                "objective": sector_specs["phase_2_objective"],
                "deliverables": sector_specs["phase_2_deliverables"],
            },
            {
                "phase": 3,
                "name": "Core Intelligence",
                "objective": "Implement sector-aware analysis engines and signal propagation.",
                "deliverables": [
                    "semantic processing",
                    "signal extraction",
                    "trend and gap analysis",
                    "market formation scoring",
                    "breakthrough detection",
                ],
            },
            {
                "phase": 4,
                "name": "Sector Design Layer",
                "objective": sector_specs["phase_4_objective"],
                "deliverables": sector_specs["phase_4_deliverables"],
            },
            {
                "phase": 5,
                "name": "Validation",
                "objective": sector_specs["phase_5_objective"],
                "deliverables": sector_specs["phase_5_deliverables"],
            },
            {
                "phase": 6,
                "name": "Portfolio Packaging",
                "objective": "Prepare artifacts for portfolio, binder, strategic review, and buyer-specific diligence.",
                "deliverables": [
                    "system summary",
                    "opportunity thesis",
                    "technical appendix",
                    "strategic positioning memo",
                    "acquirer-ready overview",
                ],
            },
            {
                "phase": 7,
                "name": "Breakthrough Acceleration",
                "objective": f"Prioritize advanced validation for the {solution_class}.",
                "deliverables": sector_specs["phase_7_deliverables"],
            },
        ]

        return phases

    def _portfolio_artifacts(
        self,
        domain: str,
        sector: str,
        system_type: str,
        market_gap: Dict[str, Any],
        scores: Dict[str, Any],
    ) -> Dict[str, Any]:
        sector_specs = self._sector_specs(sector)

        return {
            "binder_sections": [
                "Executive Thesis",
                "Detected Market / Sector Gap",
                "Needed Solution",
                "Trend + Trajectory",
                "Market Formation",
                "Moat / Defensibility",
                "Risk / Regulation / Compliance",
                "Business Model + Value Capture",
                "Deal / Exit Modeling",
                "Technical Blueprint",
                "Feasibility and Risk",
                "Strategic Positioning",
                "Acquirer / Partner Logic",
            ],
            "sector_appendices": sector_specs["portfolio_appendices"],
            "summary": {
                "domain": domain,
                "system_type": system_type,
                "market_gap_sector": sector,
                "needed_solution": market_gap.get("needed_solution"),
                "solution_class": market_gap.get("solution_class"),
                "breakthrough_score": float(scores.get("breakthrough_score", 0.0) or 0.0),
                "feasibility_score": float(scores.get("feasibility_score", 0.0) or 0.0),
                "portfolio_score": float(scores.get("portfolio_score", 0.0) or 0.0),
            },
            "artifact_status": "ready_for_binder_generation",
        }

    def _readiness(self, scores: Dict[str, Any]) -> Dict[str, Any]:
        breakthrough = float(scores.get("breakthrough_score", 0.0) or 0.0)
        feasibility = float(scores.get("feasibility_score", 0.0) or 0.0)
        portfolio = float(scores.get("portfolio_score", 0.0) or 0.0)

        if breakthrough >= 0.80 and feasibility >= 0.70 and portfolio >= 0.75:
            state = "ready_for_blueprint"
        elif portfolio >= 0.65:
            state = "blueprint_candidate"
        else:
            state = "needs_more_validation"

        return {
            "state": state,
            "breakthrough": breakthrough,
            "feasibility": feasibility,
            "portfolio": portfolio,
        }

    # =========================
    # SECTOR SPECS
    # =========================
    def _sector_specs(self, sector: str) -> Dict[str, Any]:
        if sector == "climate_insurance":
            return {
                "capability_targets": [
                    "climate insurance risk intelligence",
                    "weather-loss and exposure analysis",
                    "underwriting repricing decision support",
                    "catastrophe scenario modeling",
                    "risk-transfer recommendation support",
                ],
                "core_requirements": [
                    "weather loss ingestion",
                    "property exposure model",
                    "catastrophe scenario engine",
                    "underwriting repricing detector",
                    "market withdrawal risk map",
                    "risk-transfer recommendation layer",
                    "underwriter review controls",
                    "model confidence thresholds",
                    "exposure-data provenance",
                    "underwriting decision audit trail",
                ],
                "sector_controls": [
                    "underwriter approval gate",
                    "actuarial model review trail",
                    "exposure-data lineage",
                    "scenario versioning",
                    "pricing-impact audit log",
                ],
                "validation_targets": [
                    "historical weather-loss backtesting",
                    "repricing signal accuracy",
                    "catastrophe scenario calibration",
                    "underwriter workflow adoption",
                    "false-positive / false-negative review",
                ],
                "modules": [
                    {
                        "component": "weather_loss_ingestion",
                        "role": "ingests historical weather losses, peril events, claims context, and hazard records",
                        "interfaces": ["weather_loss_records", "peril_taxonomy", "loss_history"],
                        "priority": "high",
                    },
                    {
                        "component": "exposure_modeling_service",
                        "role": "maps property exposure, regional climate concentration, and portfolio risk",
                        "interfaces": ["property_records", "geospatial_context", "exposure_scores"],
                        "priority": "high",
                    },
                    {
                        "component": "catastrophe_scenario_engine",
                        "role": "runs catastrophe and climate stress scenarios for underwriting and portfolio review",
                        "interfaces": ["exposure_scores", "scenario_parameters", "stress_outputs"],
                        "priority": "high",
                    },
                    {
                        "component": "underwriting_repricing_detector",
                        "role": "detects repricing pressure, premium adequacy gaps, and market-withdrawal risk",
                        "interfaces": ["loss_history", "scenario_outputs", "repricing_signals"],
                        "priority": "critical",
                    },
                    {
                        "component": "risk_transfer_recommendation_layer",
                        "role": "recommends risk-transfer, reinsurance, or underwriting countermeasures for human review",
                        "interfaces": ["repricing_signals", "portfolio_context", "review_queue"],
                        "priority": "high",
                    },
                    {
                        "component": "underwriter_review_console",
                        "role": "presents explainable outputs, confidence thresholds, and required human review actions",
                        "interfaces": ["recommendations", "evidence_trace", "approval_state"],
                        "priority": "critical",
                    },
                ],
                "recommended_services": [
                    "weather_loss_ingestion_service",
                    "exposure_modeling_service",
                    "catastrophe_scenario_service",
                    "underwriting_repricing_service",
                    "risk_transfer_recommendation_service",
                    "underwriter_review_service",
                    "audit_and_model_governance_service",
                ],
                "security_model": {
                    "level": "regulated-business-data",
                    "requirements": [
                        "role-based access control",
                        "source-level permissions",
                        "data lineage tracking",
                        "model versioning",
                        "audit logging",
                        "encryption in transit and at rest",
                    ],
                },
                "operational_model": {
                    "mode": "advisory_decision_support",
                    "requirements": [
                        "underwriter review required before pricing or withdrawal action",
                        "scenario outputs must retain versioned assumptions",
                        "confidence thresholds must be visible in workflow",
                        "risk-transfer recommendations must include evidence traces",
                    ],
                },
                "phase_2_objective": "Establish climate-loss, exposure, underwriting, and catastrophe-risk data foundations.",
                "phase_2_deliverables": [
                    "weather-loss ingestion connector",
                    "property exposure schema",
                    "peril and region taxonomy",
                    "underwriting decision context map",
                    "catastrophe scenario input contract",
                ],
                "phase_4_objective": "Generate the climate-insurance risk intelligence design layer.",
                "phase_4_deliverables": [
                    "exposure model design",
                    "catastrophe scenario engine design",
                    "underwriting repricing detector",
                    "market withdrawal risk map",
                    "risk-transfer recommendation layer",
                    "underwriter review console",
                ],
                "phase_5_objective": "Validate underwriting, repricing, exposure, and catastrophe-risk outputs before operational deployment.",
                "phase_5_deliverables": [
                    "historical weather-loss backtest",
                    "repricing signal validation",
                    "catastrophe scenario calibration report",
                    "false-positive / false-negative review",
                    "underwriter workflow acceptance test",
                ],
                "phase_7_deliverables": [
                    "prototype underwriting review console",
                    "climate exposure benchmark appendix",
                    "catastrophe scenario validation memo",
                    "reinsurance and risk-transfer use-case package",
                    "strategic acquirer rationale pack",
                ],
                "portfolio_appendices": [
                    "Climate-loss backtesting appendix",
                    "Exposure benchmark appendix",
                    "Underwriting workflow appendix",
                    "Catastrophe scenario validation appendix",
                    "Risk-transfer recommendation appendix",
                ],
            }

        if sector == "financial_market_intelligence":
            return {
                "capability_targets": [
                    "financial market signal intelligence",
                    "credit and liquidity stress detection",
                    "portfolio risk decision support",
                ],
                "core_requirements": [
                    "market signal ingestion",
                    "historical regime model",
                    "credit stress detector",
                    "liquidity deterioration monitor",
                    "portfolio risk adjustment layer",
                    "model governance controls",
                ],
                "sector_controls": [
                    "model governance review",
                    "research-versus-advice separation",
                    "data source lineage",
                    "signal backtesting log",
                ],
                "validation_targets": [
                    "historical regime backtesting",
                    "signal precision and recall",
                    "false-positive / false-negative review",
                    "portfolio workflow adoption",
                ],
                "modules": [
                    {
                        "component": "market_signal_ingestion",
                        "role": "ingests market, credit, liquidity, and macro signals",
                        "interfaces": ["market_data", "credit_signals", "liquidity_signals"],
                        "priority": "high",
                    },
                    {
                        "component": "regime_modeling_service",
                        "role": "models historical regimes and repricing pressure",
                        "interfaces": ["market_signals", "regime_features", "risk_scores"],
                        "priority": "high",
                    },
                    {
                        "component": "portfolio_risk_console",
                        "role": "presents explainable risk signals and portfolio review actions",
                        "interfaces": ["risk_scores", "evidence_trace", "review_state"],
                        "priority": "high",
                    },
                ],
                "recommended_services": [
                    "market_signal_service",
                    "regime_model_service",
                    "risk_signal_service",
                    "portfolio_review_service",
                    "model_governance_service",
                ],
                "security_model": {
                    "level": "financial-data",
                    "requirements": [
                        "role-based access control",
                        "data source lineage",
                        "audit logging",
                        "model versioning",
                    ],
                },
                "operational_model": {
                    "mode": "research_decision_support",
                    "requirements": [
                        "human review before portfolio action",
                        "research-versus-advice boundary visible",
                        "model assumptions retained",
                    ],
                },
                "phase_2_objective": "Establish market signal, credit, liquidity, and regime-history data foundations.",
                "phase_2_deliverables": [
                    "market signal schema",
                    "credit stress input contract",
                    "liquidity signal map",
                    "regime backtesting dataset",
                ],
                "phase_4_objective": "Generate the financial signal intelligence design layer.",
                "phase_4_deliverables": [
                    "regime model design",
                    "credit stress detector",
                    "liquidity deterioration monitor",
                    "portfolio review console",
                ],
                "phase_5_objective": "Validate signal quality, risk-model governance, and workflow fit.",
                "phase_5_deliverables": [
                    "historical regime backtest",
                    "signal precision report",
                    "false-positive / false-negative review",
                    "model governance memo",
                ],
                "phase_7_deliverables": [
                    "institutional pilot package",
                    "signal benchmark appendix",
                    "risk model validation memo",
                    "strategic acquirer rationale pack",
                ],
                "portfolio_appendices": [
                    "Signal backtesting appendix",
                    "Model governance appendix",
                    "Portfolio workflow appendix",
                ],
            }

        if sector == "industrial_supply_chain":
            return {
                "capability_targets": [
                    "industrial resilience intelligence",
                    "supplier dependency mapping",
                    "shortage and bottleneck forecasting",
                    "procurement decision support",
                ],
                "core_requirements": [
                    "supplier graph",
                    "shortage forecast engine",
                    "ERP integration",
                    "procurement recommendation layer",
                    "production risk dashboard",
                    "operator review controls",
                ],
                "sector_controls": [
                    "ERP permission checks",
                    "operator approval gate",
                    "source data lineage",
                    "recommendation audit log",
                ],
                "validation_targets": [
                    "historical disruption backtesting",
                    "shortage forecast accuracy",
                    "procurement workflow adoption",
                    "ERP integration reliability",
                ],
                "modules": [
                    {
                        "component": "supplier_data_connector",
                        "role": "ingests supplier, component, procurement, and production planning records",
                        "interfaces": ["supplier_records", "component_catalog", "procurement_events"],
                        "priority": "high",
                    },
                    {
                        "component": "supplier_dependency_graph",
                        "role": "maps supplier dependencies and bottleneck exposure",
                        "interfaces": ["supplier_records", "component_catalog", "dependency_graph"],
                        "priority": "high",
                    },
                    {
                        "component": "shortage_forecast_engine",
                        "role": "forecasts component shortages and production bottlenecks",
                        "interfaces": ["dependency_graph", "market_signals", "shortage_scores"],
                        "priority": "critical",
                    },
                    {
                        "component": "procurement_recommendation_layer",
                        "role": "recommends procurement and sequencing countermeasures for human review",
                        "interfaces": ["shortage_scores", "countermeasures", "review_queue"],
                        "priority": "high",
                    },
                ],
                "recommended_services": [
                    "supplier_ingestion_service",
                    "dependency_graph_service",
                    "shortage_forecast_service",
                    "procurement_recommendation_service",
                    "operator_review_service",
                ],
                "security_model": {
                    "level": "enterprise-operational-data",
                    "requirements": [
                        "role-based access control",
                        "ERP integration scoping",
                        "source data lineage",
                        "audit logging",
                    ],
                },
                "operational_model": {
                    "mode": "advisory_operations_support",
                    "requirements": [
                        "operator review before procurement action",
                        "ERP writeback disabled until validated",
                        "forecast confidence visible in workflow",
                    ],
                },
                "phase_2_objective": "Establish supplier, component, procurement, and production-planning data foundations.",
                "phase_2_deliverables": [
                    "supplier data connector",
                    "component taxonomy",
                    "procurement event schema",
                    "ERP integration contract",
                ],
                "phase_4_objective": "Generate the industrial resilience design layer.",
                "phase_4_deliverables": [
                    "supplier dependency graph",
                    "shortage forecast engine",
                    "procurement recommendation layer",
                    "production risk dashboard",
                ],
                "phase_5_objective": "Validate forecasts, ERP integration, and procurement workflow fit.",
                "phase_5_deliverables": [
                    "historical disruption backtest",
                    "shortage forecast validation",
                    "ERP integration test",
                    "operator workflow acceptance test",
                ],
                "phase_7_deliverables": [
                    "industrial pilot package",
                    "supplier-risk benchmark appendix",
                    "shortage forecast validation memo",
                    "strategic acquirer rationale pack",
                ],
                "portfolio_appendices": [
                    "Supplier dependency appendix",
                    "Shortage forecast appendix",
                    "ERP integration appendix",
                ],
            }

        if sector == "healthcare_operations":
            return {
                "capability_targets": [
                    "healthcare operations intelligence",
                    "patient-flow forecasting",
                    "staffing and capacity decision support",
                ],
                "core_requirements": [
                    "patient-flow model",
                    "capacity forecast engine",
                    "staffing-risk detector",
                    "privacy controls",
                    "clinical workflow review layer",
                    "operator review controls",
                ],
                "sector_controls": [
                    "privacy impact assessment",
                    "clinical workflow review",
                    "minimum necessary data policy",
                    "human review before patient-impacting decisions",
                ],
                "validation_targets": [
                    "historical patient-flow backtesting",
                    "capacity forecast accuracy",
                    "staffing recommendation review",
                    "clinical workflow signoff",
                ],
                "modules": [
                    {
                        "component": "patient_flow_model",
                        "role": "forecasts patient-flow bottlenecks and capacity pressure",
                        "interfaces": ["capacity_data", "department_context", "flow_scores"],
                        "priority": "high",
                    },
                    {
                        "component": "staffing_risk_detector",
                        "role": "detects staffing gaps and workforce allocation risk",
                        "interfaces": ["staffing_data", "capacity_scores", "risk_flags"],
                        "priority": "high",
                    },
                    {
                        "component": "operations_review_console",
                        "role": "presents explainable capacity and staffing recommendations for review",
                        "interfaces": ["recommendations", "evidence_trace", "review_state"],
                        "priority": "critical",
                    },
                ],
                "recommended_services": [
                    "patient_flow_service",
                    "capacity_forecast_service",
                    "staffing_risk_service",
                    "operations_review_service",
                    "privacy_governance_service",
                ],
                "security_model": {
                    "level": "sensitive-health-operations-data",
                    "requirements": [
                        "role-based access control",
                        "minimum necessary data policy",
                        "audit logging",
                        "data retention controls",
                    ],
                },
                "operational_model": {
                    "mode": "clinical_operations_decision_support",
                    "requirements": [
                        "clinical review before patient-impacting workflow changes",
                        "privacy controls visible in workflow",
                        "forecast confidence visible to operators",
                    ],
                },
                "phase_2_objective": "Establish capacity, staffing, and patient-flow data foundations.",
                "phase_2_deliverables": [
                    "capacity data schema",
                    "patient-flow event model",
                    "staffing-risk input contract",
                    "privacy control map",
                ],
                "phase_4_objective": "Generate the healthcare operations design layer.",
                "phase_4_deliverables": [
                    "patient-flow model",
                    "capacity forecast engine",
                    "staffing-risk detector",
                    "operations review console",
                ],
                "phase_5_objective": "Validate forecast quality, privacy controls, and clinical workflow fit.",
                "phase_5_deliverables": [
                    "historical flow backtest",
                    "capacity forecast validation",
                    "privacy impact review",
                    "clinical workflow signoff",
                ],
                "phase_7_deliverables": [
                    "health-system pilot package",
                    "capacity benchmark appendix",
                    "workflow validation memo",
                    "strategic acquirer rationale pack",
                ],
                "portfolio_appendices": [
                    "Patient-flow backtesting appendix",
                    "Capacity benchmark appendix",
                    "Privacy controls appendix",
                ],
            }

        if sector == "defense_autonomy":
            return {
                "capability_targets": [
                    "secure mission intelligence",
                    "autonomy coordination decision support",
                    "human-reviewed mission-risk analysis",
                ],
                "core_requirements": [
                    "secure command integration",
                    "mission context ingestion",
                    "mission simulation dataset",
                    "coordination risk model",
                    "human override layer",
                    "edge decision engine",
                    "mission audit trail",
                    "allowed-use policy controls",
                    "secure command policy checks",
                    "authorization-state tracking",
                ],
                "sector_controls": [
                    "human authorization gate",
                    "secure deployment boundary",
                    "mission-use audit log",
                    "restricted-use policy",
                ],
                "validation_targets": [
                    "mission simulation validation",
                    "coordination-risk model validation",
                    "human override review",
                    "secure command integration test",
                    "allowed-use review",
                    "mission audit trace replay",
                ],
                "modules": [
                    {
                        "component": "mission_context_ingestion",
                        "role": "ingests authorized mission context, sensor inputs, operational constraints, and allowed-use metadata",
                        "interfaces": ["mission_context", "sensor_inputs", "allowed_use_metadata"],
                        "priority": "high",
                    },
                    {
                        "component": "mission_simulation_engine",
                        "role": "runs authorized mission scenarios and coordination simulations",
                        "interfaces": ["mission_context", "simulation_parameters", "scenario_outputs"],
                        "priority": "high",
                    },
                    {
                        "component": "coordination_risk_model",
                        "role": "scores coordination risk, mission uncertainty, and decision-option confidence for advisory review",
                        "interfaces": ["scenario_outputs", "risk_scores", "decision_options"],
                        "priority": "high",
                    },
                    {
                        "component": "secure_command_adapter",
                        "role": "integrates advisory outputs into secure command review workflows",
                        "interfaces": ["review_queue", "authorization_state", "audit_log"],
                        "priority": "critical",
                    },
                    {
                        "component": "human_override_layer",
                        "role": "enforces human review, authorization, and override before high-impact use",
                        "interfaces": ["recommendations", "approval_state", "override_log"],
                        "priority": "critical",
                    },
                    {
                        "component": "mission_audit_service",
                        "role": "records allowed-use decisions, authorization state, override events, evidence traces, and deployment constraints",
                        "interfaces": ["allowed_use_trace", "override_log", "audit_evidence"],
                        "priority": "critical",
                    },
                ],
                "recommended_services": [
                    "mission_context_ingestion_service",
                    "mission_simulation_service",
                    "coordination_risk_model_service",
                    "secure_command_adapter_service",
                    "human_override_service",
                    "mission_audit_service",
                    "allowed_use_policy_service",
                ],
                "security_model": {
                    "level": "secure-mission-data",
                    "requirements": [
                        "restricted access environments",
                        "mission-use audit logging",
                        "role-based authorization",
                        "secure deployment boundary",
                    ],
                },
                "operational_model": {
                    "mode": "human_reviewed_mission_support",
                    "requirements": [
                        "human authorization required",
                        "allowed-use constraints enforced",
                        "audit trail retained for all recommendations",
                    ],
                },
                "phase_2_objective": "Establish mission, simulation, sensor, and review-control data foundations.",
                "phase_2_deliverables": [
                    "mission context schema",
                    "simulation input contract",
                    "secure command interface design",
                    "allowed-use policy map",
                ],
                "phase_4_objective": "Generate the secure mission-intelligence design layer.",
                "phase_4_deliverables": [
                    "mission simulation engine",
                    "secure command adapter",
                    "human override layer",
                    "mission audit trail",
                ],
                "phase_5_objective": "Validate simulation quality, secure deployment controls, and human-review requirements.",
                "phase_5_deliverables": [
                    "mission simulation test",
                    "secure command integration review",
                    "human override validation",
                    "allowed-use policy review",
                ],
                "phase_7_deliverables": [
                    "secure pilot package",
                    "mission simulation validation memo",
                    "human-review controls appendix",
                    "strategic acquirer rationale pack",
                ],
                "portfolio_appendices": [
                    "Mission simulation appendix",
                    "Human override appendix",
                    "Secure deployment appendix",
                ],
            }

        if sector == "energy_infrastructure":
            return {
                "capability_targets": [
                    "energy infrastructure intelligence",
                    "grid bottleneck forecasting",
                    "asset-risk and resilience planning",
                ],
                "core_requirements": [
                    "grid data ingestion",
                    "asset-risk model",
                    "demand forecast engine",
                    "transmission bottleneck map",
                    "resilience planning module",
                    "operator review controls",
                ],
                "sector_controls": [
                    "utility operations review",
                    "simulation before live use",
                    "asset data lineage",
                    "resilience-plan audit trail",
                ],
                "validation_targets": [
                    "historical grid event backtesting",
                    "asset-risk model calibration",
                    "demand forecast accuracy",
                    "utility workflow acceptance",
                ],
                "modules": [
                    {
                        "component": "grid_data_ingestion",
                        "role": "ingests grid, asset, demand, and transmission records",
                        "interfaces": ["grid_events", "asset_records", "demand_signals"],
                        "priority": "high",
                    },
                    {
                        "component": "asset_risk_model",
                        "role": "models utility asset risk and resilience priorities",
                        "interfaces": ["asset_records", "risk_scores", "maintenance_context"],
                        "priority": "high",
                    },
                    {
                        "component": "resilience_planning_console",
                        "role": "presents bottleneck and resilience recommendations for operator review",
                        "interfaces": ["bottleneck_scores", "investment_options", "review_state"],
                        "priority": "high",
                    },
                ],
                "recommended_services": [
                    "grid_ingestion_service",
                    "asset_risk_service",
                    "demand_forecast_service",
                    "resilience_planning_service",
                    "operator_review_service",
                ],
                "security_model": {
                    "level": "critical-infrastructure-data",
                    "requirements": [
                        "role-based access control",
                        "source-level permissions",
                        "audit logging",
                        "deployment boundary controls",
                    ],
                },
                "operational_model": {
                    "mode": "utility_planning_decision_support",
                    "requirements": [
                        "simulation before live infrastructure use",
                        "operator review required",
                        "confidence thresholds visible",
                    ],
                },
                "phase_2_objective": "Establish grid, asset, demand, and transmission data foundations.",
                "phase_2_deliverables": [
                    "grid event schema",
                    "asset-risk input contract",
                    "demand signal map",
                    "utility operations review model",
                ],
                "phase_4_objective": "Generate the infrastructure resilience design layer.",
                "phase_4_deliverables": [
                    "asset-risk model",
                    "demand forecast engine",
                    "transmission bottleneck map",
                    "resilience planning console",
                ],
                "phase_5_objective": "Validate grid-risk forecasts, asset model quality, and utility workflow fit.",
                "phase_5_deliverables": [
                    "historical grid event backtest",
                    "asset-risk validation",
                    "utility workflow acceptance test",
                    "simulation review",
                ],
                "phase_7_deliverables": [
                    "utility pilot package",
                    "resilience benchmark appendix",
                    "asset-risk validation memo",
                    "strategic acquirer rationale pack",
                ],
                "portfolio_appendices": [
                    "Grid event backtesting appendix",
                    "Asset-risk appendix",
                    "Resilience planning appendix",
                ],
            }

        return {
            "capability_targets": [
                "cross-sector opportunity intelligence",
                "signal analysis",
                "decision support",
                "portfolio packaging",
            ],
            "core_requirements": [
                "signal ingestion",
                "gap detection",
                "opportunity ranking",
                "design synthesis",
                "portfolio packaging",
                "human review controls",
            ],
            "sector_controls": [
                "audit logging",
                "model monitoring",
                "data lineage",
                "human review gates",
            ],
            "validation_targets": [
                "historical backtesting",
                "workflow adoption",
                "false-positive / false-negative review",
                "buyer validation",
            ],
            "modules": [
                {
                    "component": "opportunity_ranking_engine",
                    "role": "ranks opportunities by gap, trend, feasibility, and strategic value",
                    "interfaces": ["signals", "scores", "ranked_opportunities"],
                    "priority": "high",
                },
                {
                    "component": "portfolio_packaging_service",
                    "role": "converts validated outputs into binder-ready artifacts",
                    "interfaces": ["ranked_opportunities", "artifact_bundle", "binder_sections"],
                    "priority": "high",
                },
            ],
            "recommended_services": [
                "signal_ingestion_service",
                "opportunity_ranking_service",
                "design_output_service",
                "portfolio_packaging_service",
                "audit_service",
            ],
            "security_model": {
                "level": "standard",
                "requirements": [
                    "input validation",
                    "request logging",
                    "access control",
                    "data lineage",
                ],
            },
            "operational_model": {
                "mode": "centralized_service",
                "requirements": [
                    "API-driven execution",
                    "central orchestration",
                    "structured monitoring",
                ],
            },
            "phase_2_objective": "Establish sector data foundations and opportunity context.",
            "phase_2_deliverables": [
                "source schema",
                "signal taxonomy",
                "gap profile",
                "buyer segment map",
            ],
            "phase_4_objective": "Generate the opportunity intelligence design layer.",
            "phase_4_deliverables": [
                "opportunity ranking engine",
                "design synthesis layer",
                "portfolio packaging service",
            ],
            "phase_5_objective": "Validate feasibility, value, and workflow fit.",
            "phase_5_deliverables": [
                "historical backtest",
                "workflow validation",
                "buyer review",
                "risk burn-down plan",
            ],
            "phase_7_deliverables": [
                "prototype architecture",
                "defensibility assessment",
                "strategic urgency memo",
                "high-conviction build recommendation",
            ],
            "portfolio_appendices": [
                "Validation appendix",
                "Workflow appendix",
                "Strategic positioning appendix",
            ],
        }

    # =========================
    # HELPERS
    # =========================
    def _slug_to_phrase(self, value: str) -> str:
        return str(value or "").replace("_", " ").strip()

    def _dedupe_modules(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        deduped: Dict[str, Dict[str, Any]] = {}
        for module in modules:
            deduped[module.get("component", "")] = module
        return list(deduped.values())
