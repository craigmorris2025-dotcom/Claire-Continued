"""
Moat Defensibility Engine — sector-aware defensibility, copy-risk,
compounding-asset, vulnerability, and moat-strengthening analysis.

v5.20 sector wording cleanup:
- Removes industrial/supplier/shortage template bleed from non-industrial sectors.
- Adds climate-insurance-specific moat language:
  climate-loss datasets, exposure benchmarks, underwriting workflow footprint,
  catastrophe scenario models, repricing signal history, and risk-transfer logic.
- Keeps the same output contract expected by the orchestrator, binder, lifecycle,
  deal engine, and downstream scoring.
"""

from typing import Any, Dict, List, Optional


class MoatDefensibilityEngine:
    """
    Deterministic moat and defensibility analyzer.
    """

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        market_gap: Optional[Dict[str, Any]] = None,
        trend_trajectory: Optional[Dict[str, Any]] = None,
        market_formation: Optional[Dict[str, Any]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = (text or "").lower()
        keywords = keywords or []
        market_gap = market_gap or {}
        trend_trajectory = trend_trajectory or {}
        market_formation = market_formation or {}
        connector_sources = connector_sources or {}

        signals = self._signals(
            text=text,
            keywords=keywords,
            domain=domain,
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
            market_formation=market_formation,
            connector_sources=connector_sources,
        )

        dimensions = self._dimension_scores(signals)
        moat_type = self._moat_type(signals, dimensions)
        copy_risk = self._copy_risk(signals, moat_type)
        compounding_assets = self._compounding_assets(signals, moat_type)
        vulnerabilities = self._vulnerabilities(signals, dimensions, copy_risk)
        actions = self._moat_strengthening_actions(signals, moat_type, vulnerabilities)

        return {
            "status": "success",
            "domain": signals["domain"],
            "sector": signals["sector"],
            "moat_type": moat_type,
            "defensibility_dimensions": dimensions,
            "copy_risk": copy_risk,
            "compounding_assets": compounding_assets,
            "vulnerabilities": vulnerabilities,
            "moat_strengthening_actions": actions,
            "strategic_defensibility_thesis": self._thesis(signals, moat_type, copy_risk),
            "evidence_signals": signals,
            "confidence": self._confidence(signals, moat_type, dimensions),
        }

    # =========================
    # SIGNALS
    # =========================
    def _signals(
        self,
        text: str,
        keywords: List[str],
        domain: str,
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        combined = f"{text} {' '.join(keywords).lower()}"

        sector = market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general"
        domain = self._domain_for_sector(sector, domain)

        market = connector_sources.get("market", {})
        patent = connector_sources.get("patent", {})
        financial = connector_sources.get("financial", {})

        def count_terms(terms: List[str]) -> int:
            return sum(1 for term in terms if term.lower() in combined)

        integration_terms = [
            "integration",
            "integrates",
            "workflow",
            "system",
            "systems",
            "erp",
            "ehr",
            "underwriting",
            "policy",
            "planning",
            "command",
            "grid",
            "api",
        ]

        data_terms = [
            "data",
            "dataset",
            "datasets",
            "historical",
            "benchmark",
            "benchmarks",
            "signals",
            "exposure",
            "loss",
            "losses",
            "weather",
            "climate",
            "property",
            "catastrophe",
            "claims",
            "sensor",
            "market",
        ]

        workflow_terms = [
            "workflow",
            "workflows",
            "underwriting",
            "repricing",
            "procurement",
            "planning",
            "clinical",
            "mission",
            "portfolio",
            "risk transfer",
            "capacity",
            "operations",
        ]

        network_terms = [
            "network",
            "ecosystem",
            "broker",
            "reinsurer",
            "supplier",
            "partner",
            "platform",
            "marketplace",
        ]

        ip_terms = [
            "novel",
            "patent",
            "proprietary",
            "algorithm",
            "model",
            "simulation",
            "scenario",
            "forecast",
        ]

        speed_terms = [
            "early",
            "accelerating",
            "urgent",
            "near-term",
            "near term",
            "first",
            "before",
        ]

        commodity_terms = [
            "dashboard",
            "reporting",
            "generic",
            "basic analytics",
            "simple",
        ]

        return {
            "domain": domain,
            "sector": sector,
            "integration_term_count": count_terms(integration_terms),
            "data_moat_term_count": count_terms(data_terms),
            "workflow_term_count": count_terms(workflow_terms),
            "network_term_count": count_terms(network_terms),
            "ip_term_count": count_terms(ip_terms),
            "speed_term_count": count_terms(speed_terms),
            "commodity_term_count": count_terms(commodity_terms),
            "market_growth": float(market.get("growth", 0.0) or 0.0),
            "market_volatility": float(market.get("volatility", 0.0) or 0.0),
            "patent_activity": float(patent.get("activity", 0.0) or 0.0),
            "patent_novelty": float(patent.get("novelty", 0.0) or 0.0),
            "financial_health": float(financial.get("health", 0.0) or 0.0),
            "financial_risk": float(financial.get("risk", 0.0) or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "strategic_pressure_score": self._nested(market_gap, "strategic_pressure", "score"),
            "trend_inevitability": self._nested(trend_trajectory, "inevitability_score", "score"),
            "trend_momentum": self._nested(trend_trajectory, "market_momentum", "score"),
            "timing_pressure": self._nested(trend_trajectory, "timing_pressure", "score"),
            "category_creation_score": self._nested(market_formation, "category_creation_score", "score"),
            "buyer_pull_score": self._nested(market_formation, "buyer_pull", "score"),
            "formation_type": self._nested_text(market_formation, "formation_type", "type"),
            "buyer_segment_count": len(market_gap.get("buyer_segments", [])) if isinstance(market_gap, dict) else 0,
            "acquirer_category_count": len(market_gap.get("acquirer_categories", [])) if isinstance(market_gap, dict) else 0,
            "ecosystem_requirement_count": len(market_formation.get("ecosystem_requirements", [])) if isinstance(market_formation, dict) else 0,
        }

    # =========================
    # SCORING
    # =========================
    def _dimension_scores(self, signals: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        sector_boosts = self._sector_dimension_boosts(signals["sector"])

        data_score = self._bounded(
            0.18
            + signals["data_moat_term_count"] * 0.040
            + signals["market_gap_confidence"] * 0.105
            + signals["patent_activity"] * 0.055
            + signals["patent_novelty"] * 0.060
            + signals["category_creation_score"] * 0.060
            + sector_boosts.get("data_advantage", 0.0)
        )

        workflow_score = self._bounded(
            0.15
            + signals["workflow_term_count"] * 0.040
            + signals["integration_term_count"] * 0.022
            + signals["buyer_pull_score"] * 0.110
            + signals["buyer_segment_count"] * 0.015
            + sector_boosts.get("workflow_lock_in", 0.0)
        )

        integration_score = self._bounded(
            0.12
            + signals["integration_term_count"] * 0.045
            + signals["ecosystem_requirement_count"] * 0.020
            + signals["market_gap_confidence"] * 0.050
            + sector_boosts.get("integration_depth", 0.0)
        )

        network_score = self._bounded(
            0.10
            + signals["network_term_count"] * 0.045
            + signals["buyer_segment_count"] * 0.018
            + signals["acquirer_category_count"] * 0.012
            + signals["formation_type"].count("platform") * 0.060
            + sector_boosts.get("network_effects", 0.0)
        )

        ip_score = self._bounded(
            0.12
            + signals["ip_term_count"] * 0.035
            + signals["patent_novelty"] * 0.115
            + signals["patent_activity"] * 0.070
            + sector_boosts.get("ip_position", 0.0)
        )

        category_score = self._bounded(
            0.13
            + signals["category_creation_score"] * 0.175
            + signals["strategic_pressure_score"] * 0.090
            + signals["trend_inevitability"] * 0.055
            + sector_boosts.get("category_position", 0.0)
        )

        speed_score = self._bounded(
            0.12
            + signals["speed_term_count"] * 0.026
            + signals["timing_pressure"] * 0.110
            + signals["trend_momentum"] * 0.075
            + sector_boosts.get("speed_advantage", 0.0)
        )

        dimensions = {
            "data_advantage": {
                "level": self._level(data_score),
                "score": round(data_score, 4),
                "description": self._dimension_description(signals["sector"], "data_advantage"),
            },
            "workflow_lock_in": {
                "level": self._level(workflow_score),
                "score": round(workflow_score, 4),
                "description": self._dimension_description(signals["sector"], "workflow_lock_in"),
            },
            "integration_depth": {
                "level": self._level(integration_score),
                "score": round(integration_score, 4),
                "description": self._dimension_description(signals["sector"], "integration_depth"),
            },
            "network_effects": {
                "level": self._level(network_score),
                "score": round(network_score, 4),
                "description": self._dimension_description(signals["sector"], "network_effects"),
            },
            "ip_position": {
                "level": self._level(ip_score),
                "score": round(ip_score, 4),
                "description": self._dimension_description(signals["sector"], "ip_position"),
            },
            "category_position": {
                "level": self._level(category_score),
                "score": round(category_score, 4),
                "description": self._dimension_description(signals["sector"], "category_position"),
            },
            "speed_advantage": {
                "level": self._level(speed_score),
                "score": round(speed_score, 4),
                "description": self._dimension_description(signals["sector"], "speed_advantage"),
            },
        }

        return dimensions

    def _moat_type(self, signals: Dict[str, Any], dimensions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        ranked = sorted(
            [
                {"dimension": key, "score": val["score"]}
                for key, val in dimensions.items()
            ],
            key=lambda item: item["score"],
            reverse=True,
        )

        primary = ranked[0]["dimension"]
        secondary = [item["dimension"] for item in ranked[1:3] if item["score"] >= 0.60]

        moat_score = self._bounded(
            ranked[0]["score"] * 0.55
            + ranked[1]["score"] * 0.25
            + ranked[2]["score"] * 0.10
            + signals["market_gap_confidence"] * 0.050
            + signals["category_creation_score"] * 0.035
            - signals["commodity_term_count"] * 0.025
        )

        strength = "strong" if moat_score >= 0.75 else "moderate" if moat_score >= 0.55 else "emerging"

        return {
            "primary_moat": primary,
            "secondary_moats": secondary,
            "moat_score": round(moat_score, 4),
            "strength": strength,
            "ranked_dimensions": ranked,
            "rationale": self._moat_rationale(signals, primary, secondary),
        }

    def _copy_risk(self, signals: Dict[str, Any], moat_type: Dict[str, Any]) -> Dict[str, Any]:
        score = self._bounded(
            0.58
            - moat_type["moat_score"] * 0.30
            - signals["data_moat_term_count"] * 0.015
            - signals["integration_term_count"] * 0.012
            - signals["buyer_pull_score"] * 0.045
            + signals["commodity_term_count"] * 0.050
            + (0.040 if signals["patent_novelty"] < 0.35 else 0.0)
        )

        level = "high" if score >= 0.60 else "moderate" if score >= 0.42 else "low"

        return {
            "level": level,
            "score": round(score, 4),
            "copy_vectors": self._copy_vectors(signals, moat_type),
        }

    # =========================
    # SECTOR-SPECIFIC CONTENT
    # =========================
    def _compounding_assets(self, signals: Dict[str, Any], moat_type: Dict[str, Any]) -> List[Dict[str, str]]:
        sector = signals["sector"]

        if sector == "climate_insurance":
            assets = [
                {
                    "asset": "climate-loss and exposure dataset",
                    "why_it_compounds": "Each underwriting, loss-history, exposure, and weather-event record improves climate-risk calibration and repricing signals.",
                    "priority": "high",
                },
                {
                    "asset": "exposure benchmark dataset",
                    "why_it_compounds": "Accumulated property, region, peril, and portfolio benchmarks become reusable premium intelligence products.",
                    "priority": "high",
                },
                {
                    "asset": "underwriting workflow footprint",
                    "why_it_compounds": "Embedding in underwriting review, repricing, and portfolio steering workflows increases switching costs and improves decision context.",
                    "priority": "high",
                },
                {
                    "asset": "catastrophe scenario model history",
                    "why_it_compounds": "Scenario runs, stress tests, and forecast outcomes improve catastrophe-risk and market-withdrawal intelligence over time.",
                    "priority": "medium",
                },
                {
                    "asset": "risk-transfer recommendation history",
                    "why_it_compounds": "Repeated risk-transfer recommendations create a proprietary record of placement logic, coverage gaps, and reinsurance planning outcomes.",
                    "priority": "medium",
                },
            ]

        elif sector == "financial_market_intelligence":
            assets = [
                {
                    "asset": "proprietary market signal history",
                    "why_it_compounds": "Each signal run, backtest, and market outcome improves credit, liquidity, and repricing models.",
                    "priority": "high",
                },
                {
                    "asset": "institutional workflow footprint",
                    "why_it_compounds": "Embedding into research, risk, and portfolio workflows increases usage depth and switching costs.",
                    "priority": "high",
                },
                {
                    "asset": "risk and liquidity benchmark library",
                    "why_it_compounds": "Benchmarks become a reusable premium intelligence layer across funds and risk teams.",
                    "priority": "medium",
                },
            ]

        elif sector == "healthcare_operations":
            assets = [
                {
                    "asset": "capacity and patient-flow dataset",
                    "why_it_compounds": "Each capacity, staffing, and patient-flow cycle improves forecast accuracy and operational recommendations.",
                    "priority": "high",
                },
                {
                    "asset": "hospital workflow footprint",
                    "why_it_compounds": "Embedding into command-center, staffing, and capacity workflows increases switching costs and context quality.",
                    "priority": "high",
                },
                {
                    "asset": "operational benchmark library",
                    "why_it_compounds": "Cross-department capacity, wait-time, staffing, and throughput benchmarks become reusable intelligence.",
                    "priority": "medium",
                },
            ]

        elif sector == "defense_autonomy":
            assets = [
                {
                    "asset": "mission simulation dataset",
                    "why_it_compounds": "Each simulation and mission review improves risk scoring, coordination logic, and edge-decision performance.",
                    "priority": "high",
                },
                {
                    "asset": "secure command workflow footprint",
                    "why_it_compounds": "Embedding into authorized command and review workflows increases switching costs and deployment context.",
                    "priority": "high",
                },
                {
                    "asset": "human-override and audit history",
                    "why_it_compounds": "Override logs and review decisions improve safety, trust, and mission-governance evidence.",
                    "priority": "medium",
                },
            ]

        elif sector == "energy_infrastructure":
            assets = [
                {
                    "asset": "grid event and asset-risk dataset",
                    "why_it_compounds": "Each grid event, asset condition, and demand pattern improves bottleneck and resilience forecasting.",
                    "priority": "high",
                },
                {
                    "asset": "utility planning workflow footprint",
                    "why_it_compounds": "Embedding into planning, asset-risk, and resilience workflows increases switching costs.",
                    "priority": "high",
                },
                {
                    "asset": "infrastructure resilience benchmark library",
                    "why_it_compounds": "Validated benchmarks become reusable intelligence for utilities and infrastructure owners.",
                    "priority": "medium",
                },
            ]

        elif sector == "industrial_supply_chain":
            assets = [
                {
                    "asset": "supplier and shortage event dataset",
                    "why_it_compounds": "Each disruption, shortage, supplier-risk, and production event improves bottleneck and procurement forecasts.",
                    "priority": "high",
                },
                {
                    "asset": "procurement and planning workflow footprint",
                    "why_it_compounds": "Embedding into ERP, procurement, and planning workflows increases switching costs and context quality.",
                    "priority": "high",
                },
                {
                    "asset": "industrial resilience benchmark library",
                    "why_it_compounds": "Supplier, shortage, and bottleneck benchmarks become reusable premium intelligence.",
                    "priority": "medium",
                },
            ]

        else:
            assets = [
                {
                    "asset": "proprietary signal dataset",
                    "why_it_compounds": "Each run improves the signal history, benchmark layer, and opportunity ranking quality.",
                    "priority": "high",
                },
                {
                    "asset": "workflow integration footprint",
                    "why_it_compounds": "Recurring workflow use increases switching costs and improves context quality.",
                    "priority": "high",
                },
                {
                    "asset": "category narrative and positioning",
                    "why_it_compounds": "Early category framing can shape buyer expectations and strategic acquirer perception.",
                    "priority": "medium",
                },
            ]

        if moat_type["primary_moat"] == "ip_position":
            assets.append({
                "asset": "technical novelty layer",
                "why_it_compounds": "Novel methods can support IP, differentiation, and proprietary implementation paths.",
                "priority": "medium",
            })

        if moat_type["primary_moat"] == "category_position":
            assets.append({
                "asset": "category narrative and positioning",
                "why_it_compounds": "Early category framing can shape buyer expectations and strategic acquirer perception.",
                "priority": "medium",
            })

        return self._dedupe(assets, "asset")

    def _vulnerabilities(
        self,
        signals: Dict[str, Any],
        dimensions: Dict[str, Dict[str, Any]],
        copy_risk: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        sector = signals["sector"]
        vulnerabilities: List[Dict[str, str]] = []

        if dimensions["integration_depth"]["score"] < 0.55:
            vulnerabilities.append({
                "vulnerability": self._sector_phrase(sector, "integration_vulnerability"),
                "impact": self._sector_phrase(sector, "integration_impact"),
                "severity": "medium",
            })

        if dimensions["workflow_lock_in"]["score"] < 0.55:
            vulnerabilities.append({
                "vulnerability": self._sector_phrase(sector, "workflow_vulnerability"),
                "impact": self._sector_phrase(sector, "workflow_impact"),
                "severity": "medium",
            })

        if dimensions["network_effects"]["score"] < 0.50:
            vulnerabilities.append({
                "vulnerability": self._sector_phrase(sector, "network_vulnerability"),
                "impact": "value may not compound quickly across ecosystem participants",
                "severity": "low",
            })

        if copy_risk["level"] in {"moderate", "high"}:
            vulnerabilities.append({
                "vulnerability": "fast-follower copy risk",
                "impact": self._sector_phrase(sector, "copy_impact"),
                "severity": "medium" if copy_risk["level"] == "moderate" else "high",
            })

        return vulnerabilities or [{
            "vulnerability": "no major deterministic moat vulnerability surfaced",
            "impact": "continue validating defensibility with buyer workflow evidence and proprietary data loops",
            "severity": "low",
        }]

    def _moat_strengthening_actions(
        self,
        signals: Dict[str, Any],
        moat_type: Dict[str, Any],
        vulnerabilities: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        sector = signals["sector"]

        if sector == "climate_insurance":
            actions = [
                {
                    "action": "build climate-loss and exposure data loops",
                    "purpose": "ensure every underwriting review, weather-loss backtest, and exposure analysis improves the model library",
                    "priority": "high",
                },
                {
                    "action": "embed into underwriting workflow",
                    "purpose": "increase switching costs by becoming part of repricing, portfolio steering, and risk-transfer decisions",
                    "priority": "high",
                },
                {
                    "action": "create proprietary exposure benchmarks",
                    "purpose": "turn regional, peril, and property-risk history into premium benchmark intelligence",
                    "priority": "high",
                },
                {
                    "action": "validate catastrophe scenario models",
                    "purpose": "strengthen trust with actuarial, underwriting, reinsurance, and catastrophe-risk stakeholders",
                    "priority": "high",
                },
            ]

        elif sector == "financial_market_intelligence":
            actions = [
                {
                    "action": "build proprietary market-signal data loops",
                    "purpose": "ensure every signal run and outcome improves credit, liquidity, and repricing models",
                    "priority": "high",
                },
                {
                    "action": "embed into institutional research and risk workflows",
                    "purpose": "increase switching costs and recurring buyer dependency",
                    "priority": "high",
                },
                {
                    "action": "create premium signal benchmarks",
                    "purpose": "make the intelligence layer hard to recreate without proprietary signal history",
                    "priority": "high",
                },
            ]

        elif sector == "healthcare_operations":
            actions = [
                {
                    "action": "build capacity and patient-flow data loops",
                    "purpose": "ensure every operational cycle improves staffing, bottleneck, and capacity forecasts",
                    "priority": "high",
                },
                {
                    "action": "embed into hospital operations workflows",
                    "purpose": "increase switching costs through recurring command-center and workforce planning use",
                    "priority": "high",
                },
                {
                    "action": "create operational benchmark datasets",
                    "purpose": "make health-system comparisons and capacity intelligence difficult to replicate",
                    "priority": "medium",
                },
            ]

        elif sector == "defense_autonomy":
            actions = [
                {
                    "action": "build mission simulation and review data loops",
                    "purpose": "ensure every simulation and authorized review improves coordination and mission-risk intelligence",
                    "priority": "high",
                },
                {
                    "action": "embed into secure command review workflows",
                    "purpose": "increase switching costs and produce deployment governance evidence",
                    "priority": "high",
                },
                {
                    "action": "harden auditability and human-override evidence",
                    "purpose": "make safety, governance, and review controls part of the defensibility story",
                    "priority": "high",
                },
            ]

        elif sector == "energy_infrastructure":
            actions = [
                {
                    "action": "build grid-event and asset-risk data loops",
                    "purpose": "ensure every demand, outage, asset, and resilience event improves infrastructure forecasting",
                    "priority": "high",
                },
                {
                    "action": "embed into utility planning workflows",
                    "purpose": "increase switching costs through recurring resilience and capital-planning use",
                    "priority": "high",
                },
                {
                    "action": "create infrastructure resilience benchmarks",
                    "purpose": "make grid and asset-risk intelligence difficult to reproduce",
                    "priority": "medium",
                },
            ]

        elif sector == "industrial_supply_chain":
            actions = [
                {
                    "action": "build supplier and shortage data loops",
                    "purpose": "ensure every disruption, supplier-risk event, and production bottleneck improves future predictions",
                    "priority": "high",
                },
                {
                    "action": "embed into procurement and planning workflows",
                    "purpose": "increase switching costs and improve context quality",
                    "priority": "high",
                },
                {
                    "action": "create industrial resilience benchmarks",
                    "purpose": "make shortage and supplier-risk intelligence hard to recreate",
                    "priority": "medium",
                },
            ]

        else:
            actions = [
                {
                    "action": "build proprietary data loops",
                    "purpose": "ensure every customer interaction improves predictions and recommendations",
                    "priority": "high",
                },
                {
                    "action": "embed into recurring buyer workflow",
                    "purpose": "increase switching costs and improve context quality",
                    "priority": "high",
                },
                {
                    "action": "create benchmark datasets and taxonomies",
                    "purpose": "make the intelligence layer hard to recreate without proprietary signal history",
                    "priority": "high",
                },
            ]

        if moat_type["primary_moat"] == "category_position":
            actions.append({
                "action": "define category narrative early",
                "purpose": "shape market language around the platform-layer opportunity",
                "priority": "medium",
            })

        return self._dedupe(actions, "action")

    # =========================
    # TEXT HELPERS
    # =========================
    def _dimension_description(self, sector: str, dimension: str) -> str:
        descriptions = {
            "climate_insurance": {
                "data_advantage": "climate-loss, exposure, weather, property, claims, underwriting, and catastrophe scenario data",
                "workflow_lock_in": "embedding into underwriting, repricing, portfolio steering, and risk-transfer workflows",
                "integration_depth": "depth of integration with underwriting workbenches, policy systems, exposure databases, and risk models",
                "network_effects": "value expansion across insurers, reinsurers, brokers, risk pools, and catastrophe-risk partners",
                "ip_position": "protected methods for exposure modeling, repricing signals, catastrophe scenarios, and risk-transfer recommendations",
                "category_position": "ability to define climate-insurance risk intelligence as a platform category",
                "speed_advantage": "timing advantage from accelerating climate exposure and insurance-market withdrawal pressure",
            },
            "financial_market_intelligence": {
                "data_advantage": "proprietary market signals, historical regimes, credit stress, liquidity, and portfolio-risk datasets",
                "workflow_lock_in": "embedding into institutional research, risk, portfolio, and investment workflows",
                "integration_depth": "depth of integration with market data, portfolio systems, and risk platforms",
                "network_effects": "value expansion across research desks, funds, asset managers, and institutional partners",
                "ip_position": "protected signal methods, factor logic, and regime-detection models",
                "category_position": "ability to define a financial signal intelligence layer",
                "speed_advantage": "timing advantage from early detection before market repricing",
            },
            "healthcare_operations": {
                "data_advantage": "capacity, patient-flow, staffing, operational, and department-level performance datasets",
                "workflow_lock_in": "embedding into capacity command, staffing, and hospital operations workflows",
                "integration_depth": "depth of integration with hospital operations systems and clinical workflow tools",
                "network_effects": "value expansion across departments, sites, service lines, and health-system partners",
                "ip_position": "protected forecasting and capacity optimization methods",
                "category_position": "ability to define healthcare operations intelligence as a platform layer",
                "speed_advantage": "timing advantage from urgent staffing and capacity pressure",
            },
            "defense_autonomy": {
                "data_advantage": "mission simulation, sensor, review, audit, and operational scenario datasets",
                "workflow_lock_in": "embedding into authorized mission planning, command review, and human-override workflows",
                "integration_depth": "depth of integration with secure command, simulation, and sensor systems",
                "network_effects": "value expansion across units, programs, platforms, and mission partners",
                "ip_position": "protected coordination, simulation, edge decision, and review-control methods",
                "category_position": "ability to define secure autonomous mission intelligence as a category",
                "speed_advantage": "timing advantage from rapid autonomy adoption and contested-environment pressure",
            },
            "energy_infrastructure": {
                "data_advantage": "grid events, asset-risk, demand, transmission, outage, and resilience datasets",
                "workflow_lock_in": "embedding into utility planning, asset-risk, and resilience workflows",
                "integration_depth": "depth of integration with grid operations, planning, and utility systems",
                "network_effects": "value expansion across utilities, operators, infrastructure owners, and planners",
                "ip_position": "protected bottleneck, asset-risk, and resilience forecasting methods",
                "category_position": "ability to define infrastructure resilience intelligence as a platform layer",
                "speed_advantage": "timing advantage from demand pressure and infrastructure modernization",
            },
            "industrial_supply_chain": {
                "data_advantage": "supplier, shortage, procurement, production, disruption, and resilience datasets",
                "workflow_lock_in": "embedding into procurement, ERP, planning, and manufacturing workflows",
                "integration_depth": "depth of integration with ERP, procurement, supplier, and planning systems",
                "network_effects": "value expansion across suppliers, manufacturers, logistics partners, and procurement teams",
                "ip_position": "protected supplier-risk, shortage, and bottleneck forecasting methods",
                "category_position": "ability to define industrial resilience intelligence as a platform layer",
                "speed_advantage": "timing advantage from early detection before production disruption",
            },
        }

        default = {
            "data_advantage": "proprietary data, signal history, taxonomies, and learned models",
            "workflow_lock_in": "embedding into recurring buyer workflows",
            "integration_depth": "depth of integration into systems of record and operational tools",
            "network_effects": "value expansion across users, partners, or ecosystem participants",
            "ip_position": "technical novelty, protected methods, and algorithmic differentiation",
            "category_position": "ability to define and own a market/category narrative",
            "speed_advantage": "timing, execution speed, and early market capture",
        }

        return descriptions.get(sector, default).get(dimension, default[dimension])

    def _sector_phrase(self, sector: str, key: str) -> str:
        phrases = {
            "climate_insurance": {
                "integration_vulnerability": "underwriting and exposure-system integration is not yet proven",
                "integration_impact": "solution may remain a replaceable climate-risk analytics layer",
                "workflow_vulnerability": "underwriting workflow lock-in is not yet proven",
                "workflow_impact": "insurers may treat the product as an optional report instead of a recurring decision layer",
                "network_vulnerability": "insurance ecosystem network effects are weak or indirect",
                "copy_impact": "insurance analytics or catastrophe-modeling incumbents could replicate visible features",
            },
            "financial_market_intelligence": {
                "integration_vulnerability": "portfolio and risk-system integration is not yet proven",
                "integration_impact": "solution may remain a replaceable research signal layer",
                "workflow_vulnerability": "institutional workflow lock-in is not yet proven",
                "workflow_impact": "buyers may treat the product as a supplemental research tool",
                "network_vulnerability": "institutional ecosystem network effects are weak or indirect",
                "copy_impact": "financial data incumbents could replicate visible signal categories",
            },
            "industrial_supply_chain": {
                "integration_vulnerability": "ERP and planning-system integration is not yet proven",
                "integration_impact": "solution may remain a replaceable analytics layer",
                "workflow_vulnerability": "procurement workflow lock-in is not yet proven",
                "workflow_impact": "buyers may use it as a dashboard instead of an operational decision layer",
                "network_vulnerability": "supplier ecosystem network effects are weak or indirect",
                "copy_impact": "supply-chain software incumbents could bundle similar features",
            },
        }

        default = {
            "integration_vulnerability": "integration moat is not yet proven",
            "integration_impact": "solution may remain a replaceable analytics layer",
            "workflow_vulnerability": "workflow lock-in is not yet proven",
            "workflow_impact": "buyers may treat the product as optional intelligence instead of recurring infrastructure",
            "network_vulnerability": "network effects are weak or indirect",
            "copy_impact": "incumbent platforms could bundle similar features",
        }

        return phrases.get(sector, default).get(key, default[key])

    def _moat_rationale(self, signals: Dict[str, Any], primary: str, secondary: List[str]) -> List[str]:
        rationale = [f"primary moat signal: {primary}"]

        if secondary:
            rationale.append(f"secondary moat signals: {', '.join(secondary)}")

        if signals["market_gap_confidence"] >= 0.80:
            rationale.append("high-confidence market gap supports defensibility")

        if signals["category_creation_score"] >= 0.75:
            rationale.append("category creation strengthens market position")

        if signals["buyer_pull_score"] >= 0.75:
            rationale.append("strong buyer pull supports workflow embedding")

        if signals["patent_novelty"] >= 0.55:
            rationale.append("technical novelty supports differentiation")

        return rationale

    def _copy_vectors(self, signals: Dict[str, Any], moat_type: Dict[str, Any]) -> List[str]:
        sector = signals["sector"]

        sector_vectors = {
            "climate_insurance": [
                "insurance analytics platforms could add climate-risk modules",
                "catastrophe-modeling companies could bundle exposure and repricing features",
                "reinsurers or brokers could build internal advisory tools",
            ],
            "financial_market_intelligence": [
                "financial data platforms could add similar signal products",
                "risk analytics vendors could bundle related models",
                "asset managers could build internal research tools",
            ],
            "healthcare_operations": [
                "EHR or hospital operations platforms could add similar capacity modules",
                "healthcare analytics companies could bundle patient-flow forecasts",
                "large health systems could build internal planning tools",
            ],
            "defense_autonomy": [
                "defense primes could build internal mission-intelligence modules",
                "defense-tech firms could bundle similar autonomy coordination features",
                "secure command platforms could absorb the workflow layer",
            ],
            "energy_infrastructure": [
                "grid technology companies could add resilience intelligence modules",
                "utility software vendors could bundle asset-risk forecasts",
                "infrastructure analytics providers could build adjacent planning tools",
            ],
            "industrial_supply_chain": [
                "ERP platforms could bundle similar planning intelligence",
                "supply-chain software vendors could add shortage forecasting modules",
                "large manufacturers could build internal supplier-risk tools",
            ],
        }

        vectors = sector_vectors.get(sector, [
            "incumbent platforms could bundle similar features",
            "technical implementation may be copied without stronger IP or proprietary process",
            "category attractiveness may invite fast followers",
        ])

        if moat_type["moat_score"] >= 0.70:
            vectors.append("copy risk falls if proprietary data loops and workflow footprint are validated")
        else:
            vectors.append("copy risk rises without stronger proprietary data, workflow embedding, or integration depth")

        return vectors

    def _thesis(self, signals: Dict[str, Any], moat_type: Dict[str, Any], copy_risk: Dict[str, Any]) -> str:
        sector = str(signals.get("sector", "target sector")).replace("_", " ")
        primary = str(moat_type.get("primary_moat", "unknown")).replace("_", " ")
        formation = str(signals.get("formation_type", "market opportunity")).replace("_", " ")

        return (
            f"{sector} shows a {moat_type.get('strength')} defensibility profile led by {primary}. "
            f"The opportunity is forming as a {formation}, with {copy_risk.get('level')} copy risk. "
            f"Defensibility should be strengthened through sector-specific proprietary data loops, workflow embedding, and integration depth."
        )

    # =========================
    # HELPERS
    # =========================
    def _sector_dimension_boosts(self, sector: str) -> Dict[str, float]:
        boosts = {
            "climate_insurance": {
                "data_advantage": 0.105,
                "workflow_lock_in": 0.030,
                "integration_depth": 0.015,
                "network_effects": 0.020,
                "category_position": 0.020,
            },
            "financial_market_intelligence": {
                "data_advantage": 0.095,
                "workflow_lock_in": 0.020,
                "category_position": 0.015,
            },
            "healthcare_operations": {
                "workflow_lock_in": 0.070,
                "integration_depth": 0.045,
                "data_advantage": 0.030,
            },
            "defense_autonomy": {
                "integration_depth": 0.060,
                "ip_position": 0.045,
                "workflow_lock_in": 0.040,
            },
            "energy_infrastructure": {
                "integration_depth": 0.050,
                "data_advantage": 0.045,
                "workflow_lock_in": 0.025,
            },
            "industrial_supply_chain": {
                "workflow_lock_in": 0.060,
                "integration_depth": 0.055,
                "data_advantage": 0.040,
            },
        }
        return boosts.get(sector, {})

    def _level(self, score: float) -> str:
        if score >= 0.75:
            return "strong"
        if score >= 0.58:
            return "moderate"
        if score >= 0.45:
            return "emerging"
        return "weak"

    def _bounded(self, value: float, low: float = 0.0, high: float = 0.96) -> float:
        return max(low, min(high, value))

    def _confidence(
        self,
        signals: Dict[str, Any],
        moat_type: Dict[str, Any],
        dimensions: Dict[str, Dict[str, Any]],
    ) -> float:
        top_dimension_score = max([dim["score"] for dim in dimensions.values()], default=0.0)

        return round(
            self._bounded(
                0.22
                + moat_type.get("moat_score", 0.0) * 0.18
                + top_dimension_score * 0.12
                + signals["market_gap_confidence"] * 0.12
                + signals["buyer_pull_score"] * 0.10
                + signals["category_creation_score"] * 0.08
                + signals["patent_novelty"] * 0.08
                + signals["trend_momentum"] * 0.06
            ),
            4,
        )

    def _domain_for_sector(self, sector: str, fallback: str) -> str:
        return {
            "climate_insurance": "insurance",
            "financial_market_intelligence": "finance",
            "healthcare_operations": "healthcare",
            "defense_autonomy": "technology",
            "energy_infrastructure": "energy",
            "industrial_supply_chain": "industrial",
        }.get(sector, fallback or "general")

    def _nested(self, obj: Dict[str, Any], *path: str) -> float:
        cur: Any = obj
        for key in path:
            if not isinstance(cur, dict):
                return 0.0
            cur = cur.get(key, 0.0)
        try:
            return float(cur or 0.0)
        except Exception:
            return 0.0

    def _nested_text(self, obj: Dict[str, Any], *path: str) -> str:
        cur: Any = obj
        for key in path:
            if not isinstance(cur, dict):
                return ""
            cur = cur.get(key, "")
        return str(cur or "")

    def _dedupe(self, items: List[Dict[str, str]], key: str) -> List[Dict[str, str]]:
        deduped: Dict[str, Dict[str, str]] = {}
        for item in items:
            deduped[item.get(key, "")] = item
        return list(deduped.values())
