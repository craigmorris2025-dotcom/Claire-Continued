"""
Claire Orchestrator — Deterministic Intelligence Engine (v5.16 RISK REGULATION)

Adds:
- Signal trace
- Engine details
- TrendTrajectoryEngine timing / momentum / inevitability analysis
- MarketFormationEngine category / buyer-pull / adoption-path analysis
- MoatDefensibilityEngine defensibility / copy-risk / compounding-asset analysis
- RiskRegulationEngine compliance / deployment / blocker analysis
- MarketGapEngine sector gap / needed solution analysis
- Conditional Design Portal routing
- SystemDesignEngine technical blueprint generation
- Market-gap-aware AcquirerMatchingEngine
- PortfolioBinderBuilder structured binder output
- LifecycleStageEngine 21-stage lifecycle visibility
"""

from typing import Dict, Any

from claire.domain.contract import ClaireIntent, ClaireResult
from claire.connectors.connector_manager import ConnectorManager
from claire.engines.auto_design import AutoDesignEngine
from claire.engines.acquirer_matching import AcquirerMatchingEngine
from claire.engines.system_design_engine import SystemDesignEngine
from claire.engines.market_gap_engine import MarketGapEngine
from claire.engines.trend_trajectory_engine import TrendTrajectoryEngine
from claire.engines.market_formation_engine import MarketFormationEngine
from claire.engines.moat_defensibility_engine import MoatDefensibilityEngine
from claire.engines.risk_regulation_engine import RiskRegulationEngine
from claire.engines.lifecycle_stage_engine import LifecycleStageEngine
from claire.design.portal import DesignPortal
from claire.portfolio.binder_builder import PortfolioBinderBuilder


class PipelineOrchestrator:

    def __init__(self):
        self.connector_manager = ConnectorManager()
        self.auto_designer = AutoDesignEngine()
        self.matcher = AcquirerMatchingEngine()
        self.design_portal = DesignPortal()
        self.system_designer = SystemDesignEngine()
        self.market_gap_engine = MarketGapEngine()
        self.trend_engine = TrendTrajectoryEngine()
        self.market_formation_engine = MarketFormationEngine()
        self.moat_engine = MoatDefensibilityEngine()
        self.risk_engine = RiskRegulationEngine()
        self.binder_builder = PortfolioBinderBuilder()
        self.lifecycle_engine = LifecycleStageEngine()

    def execute(self, intent: ClaireIntent) -> ClaireResult:

        print(">>> RUNNING PIPELINE V5.16 (RISK REGULATION) <<<")

        data: Dict[str, Any] = {}
        phase_log = []

        text = intent.get_text()
        print(">>> PIPELINE TEXT:", text)

        # =========================
        # CONNECTORS
        # =========================
        domain = self._detect_domain(text)
        keywords = self._extract_keywords(text)

        external = self.connector_manager.fetch_all({
            "domain": domain,
            "keywords": keywords
        })

        market = external.get("market", {})
        patent = external.get("patent", {})
        financial = external.get("financial", {})

        market_growth = market.get("growth", 0.5)
        patent_activity = patent.get("activity", 0.5)
        patent_novelty = patent.get("novelty", 0.5)
        financial_health = financial.get("health", 0.5)
        financial_risk = financial.get("risk", 0.5)

        # =========================
        # MARKET / SECTOR GAP
        # =========================
        try:
            market_gap = self.market_gap_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                connector_sources=external,
            )
        except Exception as e:
            market_gap = {"status": "market_gap_failed", "error": str(e)}

        # =========================
        # TREND / TRAJECTORY
        # =========================
        try:
            trend_trajectory = self.trend_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                market_gap=market_gap,
                connector_sources=external,
            )
        except Exception as e:
            trend_trajectory = {"status": "trend_trajectory_failed", "error": str(e)}

        # =========================
        # MARKET FORMATION
        # =========================
        try:
            market_formation = self.market_formation_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                connector_sources=external,
            )
        except Exception as e:
            market_formation = {"status": "market_formation_failed", "error": str(e)}

        # =========================
        # MOAT / DEFENSIBILITY
        # =========================
        try:
            moat = self.moat_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                connector_sources=external,
            )
        except Exception as e:
            moat = {"status": "moat_failed", "error": str(e)}

        # =========================
        # RISK / REGULATION
        # =========================
        try:
            risk_regulation = self.risk_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                moat=moat,
                connector_sources=external,
            )
        except Exception as e:
            risk_regulation = {"status": "risk_regulation_failed", "error": str(e)}

        data["domain"] = domain
        data["keywords"] = keywords
        data["market_gap"] = market_gap
        data["trend_trajectory"] = trend_trajectory
        data["market_formation"] = market_formation
        data["moat"] = moat
        data["risk_regulation"] = risk_regulation

        # =========================
        # ANALYSIS
        # =========================
        analysis_signal = self._amplify(0.3 + (len(keywords) * 0.025))
        phase_log.append(self._decision("analysis", analysis_signal))

        # =========================
        # SIGNAL EXTRACTION
        # =========================
        gap_confidence = market_gap.get("confidence", 0.0) if isinstance(market_gap, dict) else 0.0
        pressure_score = (
            market_gap.get("strategic_pressure", {}).get("score", 0.0)
            if isinstance(market_gap, dict)
            else 0.0
        )

        trajectory_confidence = trend_trajectory.get("confidence", 0.0) if isinstance(trend_trajectory, dict) else 0.0
        momentum_score = (
            trend_trajectory.get("market_momentum", {}).get("score", 0.0)
            if isinstance(trend_trajectory, dict)
            else 0.0
        )
        inevitability_score = (
            trend_trajectory.get("inevitability_score", {}).get("score", 0.0)
            if isinstance(trend_trajectory, dict)
            else 0.0
        )
        timing_score = (
            trend_trajectory.get("timing_pressure", {}).get("score", 0.0)
            if isinstance(trend_trajectory, dict)
            else 0.0
        )

        formation_confidence = market_formation.get("confidence", 0.0) if isinstance(market_formation, dict) else 0.0
        category_score = (
            market_formation.get("category_creation_score", {}).get("score", 0.0)
            if isinstance(market_formation, dict)
            else 0.0
        )
        buyer_pull_score = (
            market_formation.get("buyer_pull", {}).get("score", 0.0)
            if isinstance(market_formation, dict)
            else 0.0
        )

        moat_confidence = moat.get("confidence", 0.0) if isinstance(moat, dict) else 0.0
        moat_score = (
            moat.get("moat_type", {}).get("moat_score", 0.0)
            if isinstance(moat, dict)
            else 0.0
        )
        copy_risk_score = (
            moat.get("copy_risk", {}).get("score", 0.0)
            if isinstance(moat, dict)
            else 0.0
        )

        risk_confidence = risk_regulation.get("confidence", 0.0) if isinstance(risk_regulation, dict) else 0.0
        risk_score = (
            risk_regulation.get("risk_profile", {}).get("score", 0.0)
            if isinstance(risk_regulation, dict)
            else 0.0
        )
        regulatory_score = (
            risk_regulation.get("regulation_profile", {}).get("score", 0.0)
            if isinstance(risk_regulation, dict)
            else 0.0
        )
        blocker_level = (
            risk_regulation.get("blocker_assessment", {}).get("blocker_level", "unknown")
            if isinstance(risk_regulation, dict)
            else "unknown"
        )

        blocker_penalty = 0.0
        if blocker_level == "conditional":
            blocker_penalty = 0.035
        elif blocker_level == "manageable":
            blocker_penalty = 0.012

        # =========================
        # DISCOVERY
        # =========================
        discovery_signal = self._amplify(
            analysis_signal * 0.40 +
            market_growth * 0.105 +
            gap_confidence * 0.075 +
            pressure_score * 0.055 +
            trajectory_confidence * 0.055 +
            momentum_score * 0.055 +
            timing_score * 0.035 +
            formation_confidence * 0.045 +
            category_score * 0.035 +
            buyer_pull_score * 0.020 +
            moat_confidence * 0.035 +
            moat_score * 0.020 +
            risk_confidence * 0.020 +
            (0.05 if patent_activity > 0.6 else 0)
        )
        phase_log.append(self._decision("discovery", discovery_signal))

        # =========================
        # BREAKTHROUGH
        # =========================
        base_breakthrough = (
            discovery_signal * 0.29 +
            patent_novelty * 0.19 +
            analysis_signal * 0.10 +
            gap_confidence * 0.055 +
            inevitability_score * 0.075 +
            momentum_score * 0.065 +
            category_score * 0.055 +
            buyer_pull_score * 0.040 +
            moat_score * 0.050 +
            moat_confidence * 0.030 +
            risk_confidence * 0.020 -
            blocker_penalty
        )

        spike = 0.0
        if discovery_signal > 0.5 and patent_activity > 0.6:
            spike += 0.12
        if patent_novelty > 0.55:
            spike += 0.075
        if "autonomous" in text or "ai" in text:
            spike += 0.045
        if pressure_score >= 0.65:
            spike += 0.045
        if inevitability_score >= 0.75:
            spike += 0.045
        if momentum_score >= 0.72:
            spike += 0.035
        if category_score >= 0.78:
            spike += 0.035
        if buyer_pull_score >= 0.78:
            spike += 0.030
        if moat_score >= 0.70:
            spike += 0.030
        if risk_score <= 0.55 and blocker_level != "conditional":
            spike += 0.015

        breakthrough_signal = self._amplify(base_breakthrough + spike)
        phase_log.append(self._decision("breakthrough", breakthrough_signal))

        # =========================
        # INNOVATION
        # =========================
        innovation_signal = self._amplify(
            breakthrough_signal * 0.35 +
            discovery_signal * 0.19 +
            analysis_signal * 0.085 +
            gap_confidence * 0.055 +
            trajectory_confidence * 0.055 +
            inevitability_score * 0.045 +
            formation_confidence * 0.055 +
            category_score * 0.040 +
            moat_score * 0.045 +
            moat_confidence * 0.030 +
            risk_confidence * 0.020 -
            blocker_penalty
        )
        phase_log.append(self._decision("innovation", innovation_signal))

        # =========================
        # VIABILITY
        # =========================
        viability_signal = self._amplify(
            innovation_signal * 0.36 +
            financial_health * 0.21 +
            (1 - financial_risk) * 0.125 +
            pressure_score * 0.045 +
            timing_score * 0.055 +
            buyer_pull_score * 0.055 +
            formation_confidence * 0.030 +
            moat_score * 0.045 +
            (1 - copy_risk_score) * 0.020 +
            risk_confidence * 0.030 -
            risk_score * 0.030 -
            regulatory_score * 0.018 -
            blocker_penalty
        )
        phase_log.append(self._decision("viability", viability_signal))

        # =========================
        # BUILDABILITY
        # =========================
        build_signal = self._amplify(
            viability_signal * 0.52 +
            innovation_signal * 0.19 +
            breakthrough_signal * 0.095 +
            gap_confidence * 0.035 +
            trajectory_confidence * 0.035 +
            formation_confidence * 0.030 +
            moat_confidence * 0.045 +
            risk_confidence * 0.025 -
            blocker_penalty
        )
        phase_log.append(self._decision("buildability", build_signal))

        # =========================
        # FEASIBILITY
        # =========================
        feasibility_signal = self._amplify(
            build_signal * 0.62 +
            viability_signal * 0.33 +
            risk_confidence * 0.03 -
            risk_score * 0.02 -
            blocker_penalty
        )
        phase_log.append(self._decision("feasibility", feasibility_signal))

        # =========================
        # MATCHING
        # =========================
        match_signal = self._amplify(
            feasibility_signal * 0.54 +
            innovation_signal * 0.17 +
            gap_confidence * 0.055 +
            trajectory_confidence * 0.045 +
            buyer_pull_score * 0.045 +
            category_score * 0.035 +
            moat_score * 0.035 +
            moat_confidence * 0.020 +
            risk_confidence * 0.025 -
            blocker_penalty
        )
        phase_log.append(self._decision("matching", match_signal))

        # =========================
        # ACQUISITION
        # =========================
        acquisition_signal = self._amplify(
            match_signal * 0.62 +
            viability_signal * 0.14 +
            pressure_score * 0.045 +
            inevitability_score * 0.045 +
            category_score * 0.030 +
            buyer_pull_score * 0.030 +
            moat_score * 0.045 +
            risk_confidence * 0.025 -
            blocker_penalty
        )
        phase_log.append(self._decision("acquisition", acquisition_signal))

        # =========================
        # OPTIMIZATION
        # =========================
        optimization_signal = self._amplify(
            acquisition_signal * 0.70 +
            innovation_signal * 0.10 +
            gap_confidence * 0.030 +
            momentum_score * 0.030 +
            formation_confidence * 0.045 +
            moat_confidence * 0.045 +
            risk_confidence * 0.030 -
            blocker_penalty
        )
        phase_log.append(self._decision("optimization", optimization_signal))

        # =========================
        # PORTFOLIO
        # =========================
        portfolio_signal = min(
            0.94,
            self._amplify(
                optimization_signal * 0.70 +
                acquisition_signal * 0.080 +
                pressure_score * 0.025 +
                inevitability_score * 0.035 +
                timing_score * 0.020 +
                category_score * 0.025 +
                buyer_pull_score * 0.018 +
                moat_score * 0.035 +
                (1 - copy_risk_score) * 0.010 +
                risk_confidence * 0.025 -
                risk_score * 0.012 -
                regulatory_score * 0.008 -
                blocker_penalty
            )
        )
        phase_log.append(self._decision("portfolio", portfolio_signal))

        # =========================
        # SCORES
        # =========================
        scores = {
            "analysis_score": analysis_signal,
            "discovery_score": discovery_signal,
            "breakthrough_score": breakthrough_signal,
            "innovation_score": innovation_signal,
            "viability_score": viability_signal,
            "buildability_score": build_signal,
            "feasibility_score": feasibility_signal,
            "matching_score": match_signal,
            "acquisition_score": acquisition_signal,
            "optimization_score": optimization_signal,
            "portfolio_score": portfolio_signal,
            "_confidence": portfolio_signal,
        }

        # =========================
        # SIGNAL TRACE
        # =========================
        data["signal_trace"] = {
            "analysis": analysis_signal,
            "discovery": discovery_signal,
            "market_gap_confidence": gap_confidence,
            "market_pressure_score": pressure_score,
            "trajectory_confidence": trajectory_confidence,
            "trajectory_momentum": momentum_score,
            "trajectory_inevitability": inevitability_score,
            "trajectory_timing_pressure": timing_score,
            "market_formation_confidence": formation_confidence,
            "category_creation_score": category_score,
            "buyer_pull_score": buyer_pull_score,
            "moat_confidence": moat_confidence,
            "moat_score": moat_score,
            "copy_risk_score": copy_risk_score,
            "risk_regulation_confidence": risk_confidence,
            "risk_score": risk_score,
            "regulatory_exposure_score": regulatory_score,
            "blocker_level": blocker_level,
            "breakthrough_base": base_breakthrough,
            "breakthrough_spike": spike,
            "breakthrough_final": breakthrough_signal,
        }

        # =========================
        # ENGINE DETAILS
        # =========================
        data["engine_details"] = {
            "signals": {
                "analysis": analysis_signal,
                "discovery": discovery_signal,
                "breakthrough": breakthrough_signal,
                "innovation": innovation_signal,
                "viability": viability_signal,
                "portfolio": portfolio_signal,
            },
            "connectors": {
                "market_growth": market_growth,
                "patent_activity": patent_activity,
                "patent_novelty": patent_novelty,
                "financial_health": financial_health,
                "financial_risk": financial_risk,
            },
            "market_gap": {
                "sector": market_gap.get("sector") if isinstance(market_gap, dict) else None,
                "gap_type": market_gap.get("gap_type") if isinstance(market_gap, dict) else None,
                "solution_class": market_gap.get("solution_class") if isinstance(market_gap, dict) else None,
                "confidence": market_gap.get("confidence") if isinstance(market_gap, dict) else None,
                "pressure": market_gap.get("strategic_pressure") if isinstance(market_gap, dict) else None,
            },
            "trend_trajectory": {
                "trend_direction": trend_trajectory.get("trend_direction") if isinstance(trend_trajectory, dict) else None,
                "market_momentum": trend_trajectory.get("market_momentum") if isinstance(trend_trajectory, dict) else None,
                "inevitability_score": trend_trajectory.get("inevitability_score") if isinstance(trend_trajectory, dict) else None,
                "timing_pressure": trend_trajectory.get("timing_pressure") if isinstance(trend_trajectory, dict) else None,
                "strategic_window": trend_trajectory.get("strategic_window") if isinstance(trend_trajectory, dict) else None,
                "confidence": trend_trajectory.get("confidence") if isinstance(trend_trajectory, dict) else None,
            },
            "market_formation": {
                "formation_type": market_formation.get("formation_type") if isinstance(market_formation, dict) else None,
                "market_stage": market_formation.get("market_stage") if isinstance(market_formation, dict) else None,
                "category_creation_score": market_formation.get("category_creation_score") if isinstance(market_formation, dict) else None,
                "buyer_pull": market_formation.get("buyer_pull") if isinstance(market_formation, dict) else None,
                "confidence": market_formation.get("confidence") if isinstance(market_formation, dict) else None,
            },
            "moat": {
                "moat_type": moat.get("moat_type") if isinstance(moat, dict) else None,
                "copy_risk": moat.get("copy_risk") if isinstance(moat, dict) else None,
                "confidence": moat.get("confidence") if isinstance(moat, dict) else None,
            },
            "risk_regulation": {
                "risk_profile": risk_regulation.get("risk_profile") if isinstance(risk_regulation, dict) else None,
                "regulation_profile": risk_regulation.get("regulation_profile") if isinstance(risk_regulation, dict) else None,
                "blocker_assessment": risk_regulation.get("blocker_assessment") if isinstance(risk_regulation, dict) else None,
                "confidence": risk_regulation.get("confidence") if isinstance(risk_regulation, dict) else None,
            },
        }

        # =========================
        # AUTO DESIGN
        # =========================
        try:
            system_design = self.auto_designer.generate(
                intent=intent,
                context={**data, "scores": scores},
            )
            data["system_design"] = system_design
        except Exception as e:
            system_design = {"status": "design_failed", "error": str(e)}
            data["system_design"] = system_design

        # =========================
        # DESIGN PORTAL
        # =========================
        try:
            design_portal = self.design_portal.evaluate({
                **data,
                "scores": scores,
                "domain": domain,
                "keywords": keywords,
                "system_design": system_design,
                "market_gap": market_gap,
                "trend_trajectory": trend_trajectory,
                "market_formation": market_formation,
                "moat": moat,
                "risk_regulation": risk_regulation,
            })
            data["design_portal"] = design_portal
        except Exception as e:
            design_portal = {"status": "portal_failed", "route_to_design": False, "error": str(e)}
            data["design_portal"] = design_portal

        # =========================
        # SYSTEM DESIGN ENGINE
        # =========================
        try:
            if design_portal.get("route_to_design", False):
                design_output = self.system_designer.generate(design_portal)
            else:
                design_output = {
                    "status": "not_routed",
                    "message": "Design portal did not activate.",
                }

            data["design_output"] = design_output

        except Exception as e:
            data["design_output"] = {"status": "design_engine_failed", "error": str(e)}

        # =========================
        # ACQUIRER MATCHING
        # =========================
        try:
            acquirer_matches = self.matcher.match(
                keywords=keywords,
                domain=domain,
                market_gap=market_gap,
            )
        except Exception:
            acquirer_matches = []

        # =========================
        # PORTFOLIO BINDER
        # =========================
        try:
            portfolio_binder = self.binder_builder.build({
                "scores": scores,
                "domain": domain,
                "keywords": keywords,
                "market_gap": market_gap,
                "trend_trajectory": trend_trajectory,
                "market_formation": market_formation,
                "moat": moat,
                "risk_regulation": risk_regulation,
                "system_design": system_design,
                "design_output": data.get("design_output", {}),
                "acquirer_matches": acquirer_matches,
                "signal_trace": data.get("signal_trace", {}),
                "phase_log": phase_log,
            })
            data["portfolio_binder"] = portfolio_binder
        except Exception as e:
            data["portfolio_binder"] = {"status": "binder_failed", "error": str(e)}

        # =========================
        # LIFECYCLE STAGES
        # =========================
        try:
            lifecycle = self.lifecycle_engine.evaluate({
                "scores": scores,
                "domain": domain,
                "keywords": keywords,
                "connector_sources": external,
                "market_gap": market_gap,
                "trend_trajectory": trend_trajectory,
                "market_formation": market_formation,
                "moat": moat,
                "risk_regulation": risk_regulation,
                "signal_trace": data.get("signal_trace", {}),
                "engine_details": data.get("engine_details", {}),
                "system_design": system_design,
                "design_portal": design_portal,
                "design_output": data.get("design_output", {}),
                "acquirer_matches": acquirer_matches,
                "portfolio_binder": data.get("portfolio_binder", {}),
                "phase_log": phase_log,
            })
            data["lifecycle"] = lifecycle
            data["lifecycle_stages"] = lifecycle.get("stages", [])
            data["lifecycle_summary"] = lifecycle.get("summary", {})
        except Exception as e:
            data["lifecycle"] = {"status": "lifecycle_failed", "error": str(e)}
            data["lifecycle_stages"] = []
            data["lifecycle_summary"] = {}

        # =========================
        # FINAL DECISION
        # =========================
        final_score = portfolio_signal

        decision = (
            "GO" if final_score > 0.7 else
            "CONSIDER" if final_score > 0.5 else
            "NO-GO"
        )

        data["phase_log"] = phase_log
        data["external_signals"] = external

        return ClaireResult(
            status="success",
            mode=intent.mode,
            decision_classification=decision,
            breakthrough_classification="HIGH" if breakthrough_signal > 0.65 else "LOW",
            scores=scores,
            data=data,
            acquirer_matches=acquirer_matches,
            ready_for_syntalion=final_score > 0.65,
        )

    def _extract_keywords(self, text: str):
        return [w.strip(",.") for w in text.lower().split() if len(w) > 4][:10]

    def _detect_domain(self, text: str):
        t = text.lower()

        if "finance" in t or "fintech" in t or "credit" in t or "liquidity" in t:
            return "finance"

        if "health" in t or "medical" in t or "clinical" in t or "hospital" in t:
            return "healthcare"

        if "supply chain" in t or "manufacturing" in t or "industrial" in t or "supplier" in t:
            return "industrial"

        if "energy" in t or "grid" in t or "utilities" in t or "power" in t:
            return "energy"

        if "defense" in t or "military" in t or "battlefield" in t:
            return "technology"

        if "ai" in t or "machine learning" in t or "platform" in t:
            return "technology"

        return "general"

    def _amplify(self, value: float) -> float:
        value = max(0.0, min(value, 1.0))
        scaled = value ** 0.9

        if scaled > 0.92:
            scaled = 0.92 + (scaled - 0.92) * 0.3

        return scaled

    def _decision(self, phase: str, score: float):
        if score > 0.7:
            label = "STRONG"
        elif score > 0.5:
            label = "MODERATE"
        else:
            label = "WEAK"

        return {
            "phase": phase,
            "score": round(score, 3),
            "decision": label,
        }
