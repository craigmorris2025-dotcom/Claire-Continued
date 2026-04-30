"""
System Design Engine — converts a validated breakthrough/opportunity
into technical specifications, architecture blueprint, implementation phases,
and portfolio-ready design artifacts.

Role:
- AutoDesignEngine = high-level system classification
- DesignPortal = decides whether design should activate
- SystemDesignEngine = produces the actual technical/system blueprint
"""

from typing import Any, Dict, List


class SystemDesignEngine:
    """
    Produces technical design output for breakthroughs that pass the DesignPortal.
    """

    def generate(self, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a technical design package from validated design inputs.
        """

        if not design_context:
            return {
                "status": "design_failed",
                "error": "No design context provided",
            }

        route_to_design = design_context.get("route_to_design", False)

        if not route_to_design:
            return {
                "status": "not_routed",
                "message": "Design portal did not activate.",
            }

        inputs = design_context.get("inputs", {})
        scores = inputs.get("scores", {})
        system_design = inputs.get("system_design", {})
        market_gap = inputs.get("market_gap", {})
        domain = inputs.get("domain", "general")
        keywords = inputs.get("keywords", [])

        design_payload = system_design.get("design", {})

        system_type = design_payload.get("system_type", "unknown_system")
        architecture = design_payload.get("architecture", "modular")
        components = design_payload.get("components", [])

        technical_specs = self._technical_specs(
            domain=domain,
            keywords=keywords,
            system_type=system_type,
            scores=scores,
            market_gap=market_gap,
        )

        architecture_blueprint = self._architecture_blueprint(
            architecture=architecture,
            components=components,
            domain=domain,
            keywords=keywords,
            market_gap=market_gap,
        )

        data_flows = self._data_flows(components=components)

        implementation_phases = self._implementation_phases(
            scores=scores,
            market_gap=market_gap,
        )

        portfolio_artifacts = self._portfolio_artifacts(
            domain=domain,
            system_type=system_type,
            scores=scores,
            market_gap=market_gap,
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
            "data_flows": data_flows,
            "implementation_phases": implementation_phases,
            "portfolio_artifacts": portfolio_artifacts,
            "readiness": self._readiness(scores),
        }

    def _technical_specs(
        self,
        domain: str,
        keywords: List[str],
        system_type: str,
        scores: Dict[str, Any],
        market_gap: Dict[str, Any],
    ) -> Dict[str, Any]:
        breakthrough = scores.get("breakthrough_score", 0.0)
        feasibility = scores.get("feasibility_score", 0.0)
        portfolio = scores.get("portfolio_score", 0.0)

        core_requirements = [
            "modular service architecture",
            "traceable decision pipeline",
            "structured input-output contracts",
            "explainable scoring and design rationale",
            "portfolio-ready artifact generation",
        ]

        if self._has_any(keywords, ["autonomous", "ai-driven", "ai-powered", "ai"]):
            core_requirements.extend([
                "autonomous decision layer",
                "human override controls",
                "model monitoring and audit trail",
                "simulation and scenario testing",
            ])

        if self._has_any(keywords, ["defense", "battlefield", "drone", "swarm"]):
            core_requirements.extend([
                "secure communications model",
                "edge-deployable architecture",
                "fault-tolerant distributed operations",
                "mission-context isolation",
            ])

        if self._has_any(keywords, ["real-time", "multi-sensor", "sensor", "fusion"]):
            core_requirements.extend([
                "low-latency processing layer",
                "multi-source sensor fusion pipeline",
                "event-driven data routing",
            ])

        if isinstance(market_gap, dict):
            for implication in market_gap.get("design_implications", []):
                core_requirements.append(implication)

        return {
            "primary_domain": domain,
            "system_type": system_type,
            "market_gap_sector": market_gap.get("sector") if isinstance(market_gap, dict) else None,
            "needed_solution": market_gap.get("needed_solution") if isinstance(market_gap, dict) else None,
            "solution_class": market_gap.get("solution_class") if isinstance(market_gap, dict) else None,
            "capability_targets": self._capability_targets(keywords, market_gap),
            "performance_targets": {
                "breakthrough_intensity": round(breakthrough, 4),
                "feasibility_threshold": round(feasibility, 4),
                "portfolio_confidence": round(portfolio, 4),
            },
            "core_requirements": sorted(list(dict.fromkeys(core_requirements))),
        }

    def _architecture_blueprint(
        self,
        architecture: str,
        components: List[str],
        domain: str,
        keywords: List[str],
        market_gap: Dict[str, Any],
    ) -> Dict[str, Any]:
        modules = []

        for component in components:
            modules.append({
                "component": component,
                "role": self._component_role(component),
                "interfaces": self._component_interfaces(component),
                "priority": self._component_priority(component),
            })

        if isinstance(market_gap, dict):
            for implication in market_gap.get("design_implications", []):
                modules.append({
                    "component": implication.replace(" ", "_").replace("-", "_"),
                    "role": f"implements market-gap requirement: {implication}",
                    "interfaces": ["market_gap_context", "design_output"],
                    "priority": "high",
                })

        return {
            "architecture_style": architecture,
            "domain_context": domain,
            "market_gap_context": market_gap.get("sector") if isinstance(market_gap, dict) else None,
            "modules": modules,
            "recommended_services": self._recommended_services(keywords, market_gap),
            "security_model": self._security_model(keywords),
            "operational_model": self._operational_model(keywords),
        }

    def _data_flows(self, components: List[str]) -> List[Dict[str, Any]]:
        if not components:
            return []

        flows = []

        for idx in range(len(components) - 1):
            flows.append({
                "from": components[idx],
                "to": components[idx + 1],
                "payload": "structured_context",
                "validation": "contract_checked",
            })

        return flows

    def _implementation_phases(
        self,
        scores: Dict[str, Any],
        market_gap: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        breakthrough = scores.get("breakthrough_score", 0.0)
        feasibility = scores.get("feasibility_score", 0.0)
        solution_class = market_gap.get("solution_class", "validated opportunity platform") if isinstance(market_gap, dict) else "validated opportunity platform"

        phases = [
            {
                "phase": 1,
                "name": "Foundation",
                "objective": "Establish contracts, ingestion, routing, and traceability.",
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
                "name": "Market Gap Intelligence",
                "objective": f"Validate the needed solution class: {solution_class}.",
                "deliverables": [
                    "market gap profile",
                    "needed solution statement",
                    "buyer segment map",
                    "strategic pressure analysis",
                ],
            },
            {
                "phase": 3,
                "name": "Core Intelligence",
                "objective": "Implement analysis engines and signal propagation.",
                "deliverables": [
                    "semantic processing",
                    "signal extraction",
                    "trend and gap analysis",
                    "scoring engine",
                    "breakthrough detection",
                ],
            },
            {
                "phase": 4,
                "name": "System Design",
                "objective": "Generate technical blueprint and design artifacts.",
                "deliverables": [
                    "architecture blueprint",
                    "technical specs",
                    "component map",
                    "data flow map",
                    "implementation plan",
                ],
            },
            {
                "phase": 5,
                "name": "Validation",
                "objective": "De-risk feasibility, value, and implementation assumptions.",
                "deliverables": [
                    "feasibility review",
                    "technical unknowns register",
                    "risk burn-down plan",
                    "validation experiments",
                ],
            },
            {
                "phase": 6,
                "name": "Portfolio Packaging",
                "objective": "Prepare artifacts for portfolio, binder, and strategic review.",
                "deliverables": [
                    "system summary",
                    "opportunity thesis",
                    "technical appendix",
                    "strategic positioning memo",
                    "acquirer-ready overview",
                ],
            },
        ]

        if breakthrough >= 0.9:
            phases.append({
                "phase": 7,
                "name": "Breakthrough Acceleration",
                "objective": "Prioritize advanced validation for high-breakthrough concepts.",
                "deliverables": [
                    "prototype architecture",
                    "defensibility assessment",
                    "strategic urgency memo",
                    "high-conviction build recommendation",
                ],
            })

        if feasibility < 0.65:
            phases.append({
                "phase": 8,
                "name": "Feasibility De-risking",
                "objective": "Resolve technical uncertainty before execution.",
                "deliverables": [
                    "risk burn-down plan",
                    "technical unknowns register",
                    "validation experiments",
                    "dependency map",
                ],
            })

        return phases

    def _portfolio_artifacts(
        self,
        domain: str,
        system_type: str,
        scores: Dict[str, Any],
        market_gap: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "binder_sections": [
                "Executive Thesis",
                "Detected Market / Sector Gap",
                "Needed Solution",
                "Breakthrough Design",
                "Technical Blueprint",
                "Feasibility and Risk",
                "Strategic Positioning",
                "Portfolio Fit",
                "Acquirer / Partner Logic",
            ],
            "summary": {
                "domain": domain,
                "system_type": system_type,
                "market_gap_sector": market_gap.get("sector") if isinstance(market_gap, dict) else None,
                "needed_solution": market_gap.get("needed_solution") if isinstance(market_gap, dict) else None,
                "breakthrough_score": scores.get("breakthrough_score", 0.0),
                "feasibility_score": scores.get("feasibility_score", 0.0),
                "portfolio_score": scores.get("portfolio_score", 0.0),
            },
            "artifact_status": "ready_for_binder_generation",
        }

    def _capability_targets(self, keywords: List[str], market_gap: Dict[str, Any]) -> List[str]:
        targets = []

        keyword_map = {
            "autonomous": "autonomous operation",
            "swarm": "multi-agent coordination",
            "drone": "unmanned platform support",
            "defense": "mission-critical defense readiness",
            "real-time": "low-latency processing",
            "multi-sensor": "sensor fusion",
            "sensor": "sensor fusion",
            "fusion": "sensor/data fusion",
            "edge": "edge deployment",
            "ai-driven": "AI-assisted decision-making",
            "ai-powered": "AI-assisted decision-making",
            "decentralized": "distributed decision architecture",
            "decision-making": "decision intelligence",
        }

        for keyword in keywords:
            if keyword in keyword_map:
                targets.append(keyword_map[keyword])

        if isinstance(market_gap, dict):
            solution_class = market_gap.get("solution_class")
            if solution_class:
                targets.append(solution_class)

        if not targets:
            targets.append("validated system capability")

        return sorted(list(set(targets)))

    def _component_role(self, component: str) -> str:
        mapping = {
            "ingestion": "collects and normalizes input data",
            "semantic_processing": "extracts meaning, entities, and concept signals",
            "analysis_engines": "evaluates trends, gaps, feasibility, and opportunities",
            "decision_layer": "classifies decisions and readiness states",
            "api_gateway": "exposes system capabilities to applications and users",
        }

        return mapping.get(component, "supports system execution")

    def _component_interfaces(self, component: str) -> List[str]:
        mapping = {
            "ingestion": ["raw_input", "source_metadata", "normalized_payload"],
            "semantic_processing": ["normalized_payload", "semantic_context"],
            "analysis_engines": ["semantic_context", "signals", "scores"],
            "decision_layer": ["scores", "decision_state", "readiness_flags"],
            "api_gateway": ["request", "response", "external_clients"],
        }

        return mapping.get(component, ["input", "output"])

    def _component_priority(self, component: str) -> str:
        if component in {"ingestion", "decision_layer"}:
            return "critical"

        if component in {"semantic_processing", "analysis_engines"}:
            return "high"

        return "medium"

    def _recommended_services(self, keywords: List[str], market_gap: Dict[str, Any]) -> List[str]:
        services = [
            "orchestration_service",
            "contract_validation_service",
            "scoring_service",
            "design_output_service",
        ]

        if "real-time" in keywords:
            services.append("stream_processing_service")

        if self._has_any(keywords, ["edge", "drone", "swarm"]):
            services.append("edge_runtime_service")

        if "defense" in keywords:
            services.append("secure_mission_context_service")

        if self._has_any(keywords, ["multi-sensor", "sensor", "fusion"]):
            services.append("sensor_fusion_service")

        if self._has_any(keywords, ["autonomous", "ai-driven", "ai-powered"]):
            services.append("autonomous_decision_service")

        if isinstance(market_gap, dict):
            sector = market_gap.get("sector")
            if sector:
                services.append(f"{sector}_gap_service")

        return sorted(list(set(services)))

    def _security_model(self, keywords: List[str]) -> Dict[str, Any]:
        if self._has_any(keywords, ["defense", "battlefield", "drone", "swarm"]):
            return {
                "level": "high",
                "requirements": [
                    "role-based access control",
                    "audit logging",
                    "secure communication channels",
                    "deployment isolation",
                    "human override controls",
                ],
            }

        return {
            "level": "standard",
            "requirements": [
                "input validation",
                "request logging",
                "access control",
            ],
        }

    def _operational_model(self, keywords: List[str]) -> Dict[str, Any]:
        if self._has_any(keywords, ["real-time", "edge", "drone", "swarm"]):
            return {
                "mode": "distributed_edge",
                "requirements": [
                    "low-latency execution",
                    "local fallback behavior",
                    "resilient network operation",
                    "event-driven coordination",
                ],
            }

        return {
            "mode": "centralized_service",
            "requirements": [
                "API-driven execution",
                "central orchestration",
                "structured monitoring",
            ],
        }

    def _readiness(self, scores: Dict[str, Any]) -> Dict[str, Any]:
        breakthrough = scores.get("breakthrough_score", 0.0)
        feasibility = scores.get("feasibility_score", 0.0)
        portfolio = scores.get("portfolio_score", 0.0)

        if breakthrough >= 0.85 and feasibility >= 0.70 and portfolio >= 0.75:
            state = "ready_for_blueprint"
        elif breakthrough >= 0.75 and portfolio >= 0.70:
            state = "design_candidate"
        else:
            state = "needs_more_validation"

        return {
            "state": state,
            "breakthrough": breakthrough,
            "feasibility": feasibility,
            "portfolio": portfolio,
        }

    def _has_any(self, keywords: List[str], terms: List[str]) -> bool:
        lowered = {k.lower() for k in keywords}
        return any(term.lower() in lowered for term in terms)
