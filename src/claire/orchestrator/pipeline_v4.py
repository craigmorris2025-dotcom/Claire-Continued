
"""
Claire Orchestrator — Deterministic Intelligence Engine (v5.17 BUSINESS MODEL)
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
from claire.engines.business_model_engine import BusinessModelEngine
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
        self.business_model_engine = BusinessModelEngine()
        self.binder_builder = PortfolioBinderBuilder()
        self.lifecycle_engine = LifecycleStageEngine()

    def execute(self, intent: ClaireIntent) -> ClaireResult:

        print(">>> RUNNING PIPELINE V5.17 (BUSINESS MODEL) <<<")

        data: Dict[str, Any] = {}
        phase_log = []
        text = intent.get_text()
        print(">>> PIPELINE TEXT:", text)

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

        market_gap = self._safe_engine(
            "market_gap_failed",
            lambda: self.market_gap_engine.analyze(text=text, domain=domain, keywords=keywords, connector_sources=external),
        )

        trend_trajectory = self._safe_engine(
            "trend_trajectory_failed",
            lambda: self.trend_engine.analyze(text=text, domain=domain, keywords=keywords, market_gap=market_gap, connector_sources=external),
        )

        market_formation = self._safe_engine(
            "market_formation_failed",
            lambda: self.market_formation_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                connector_sources=external,
            ),
        )

        moat = self._safe_engine(
            "moat_failed",
            lambda: self.moat_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                connector_sources=external,
            ),
        )

        risk_regulation = self._safe_engine(
            "risk_regulation_failed",
            lambda: self.risk_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                moat=moat,
                connector_sources=external,
            ),
        )

        business_model = self._safe_engine(
            "business_model_failed",
            lambda: self.business_model_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                moat=moat,
                risk_regulation=risk_regulation,
                connector_sources=external,
            ),
        )

        data.update({
            "domain": domain,
            "keywords": keywords,
            "market_gap": market_gap,
            "trend_trajectory": trend_trajectory,
            "market_formation": market_formation,
            "moat": moat,
            "risk_regulation": risk_regulation,
            "business_model": business_model,
        })

        analysis_signal = self._amplify(0.3 + (len(keywords) * 0.025))
        phase_log.append(self._decision("analysis", analysis_signal))

        # Pull engine signals
        gap_confidence = self._get(market_gap, "confidence", 0.0)
        pressure_score = self._get(market_gap, "strategic_pressure.score", 0.0)

        trajectory_confidence = self._get(trend_trajectory, "confidence", 0.0)
        momentum_score = self._get(trend_trajectory, "market_momentum.score", 0.0)
        inevitability_score = self._get(trend_trajectory, "inevitability_score.score", 0.0)
        timing_score = self._get(trend_trajectory, "timing_pressure.score", 0.0)

        formation_confidence = self._get(market_formation, "confidence", 0.0)
        category_score = self._get(market_formation, "category_creation_score.score", 0.0)
        buyer_pull_score = self._get(market_formation, "buyer_pull.score", 0.0)

        moat_confidence = self._get(moat, "confidence", 0.0)
        moat_score = self._get(moat, "moat_type.moat_score", 0.0)
        copy_risk_score = self._get(moat, "copy_risk.score", 0.0)

        risk_confidence = self._get(risk_regulation, "confidence", 0.0)
        risk_score = self._get(risk_regulation, "risk_profile.score", 0.0)
        regulatory_score = self._get(risk_regulation, "regulation_profile.score", 0.0)
        blocker_level = self._get(risk_regulation, "blocker_assessment.blocker_level", "unknown")

        business_confidence = self._get(business_model, "confidence", 0.0)
        value_capture_score = self._get(business_model, "value_capture.score", 0.0)
        buyer_roi_score = self._get(business_model, "buyer_roi.score", 0.0)
        commercial_risk_score = self._get(business_model, "commercial_risk.score", 0.0)

        blocker_penalty = 0.030 if blocker_level == "conditional" else 0.010 if blocker_level == "manageable" else 0.0

        discovery_signal = self._amplify(
            analysis_signal * 0.385 +
            market_growth * 0.100 +
            gap_confidence * 0.070 +
            pressure_score * 0.050 +
            trajectory_confidence * 0.050 +
            momentum_score * 0.050 +
            timing_score * 0.032 +
            formation_confidence * 0.040 +
            category_score * 0.032 +
            buyer_pull_score * 0.018 +
            moat_confidence * 0.030 +
            moat_score * 0.018 +
            risk_confidence * 0.018 +
            business_confidence * 0.030 +
            value_capture_score * 0.025 +
            (0.05 if patent_activity > 0.6 else 0)
        )
        phase_log.append(self._decision("discovery", discovery_signal))

        base_breakthrough = (
            discovery_signal * 0.280 +
            patent_novelty * 0.180 +
            analysis_signal * 0.095 +
            gap_confidence * 0.052 +
            inevitability_score * 0.070 +
            momentum_score * 0.060 +
            category_score * 0.052 +
            buyer_pull_score * 0.038 +
            moat_score * 0.045 +
            moat_confidence * 0.026 +
            risk_confidence * 0.018 +
            business_confidence * 0.030 +
            value_capture_score * 0.030 +
            buyer_roi_score * 0.024 -
            blocker_penalty
        )

        spike = 0.0
        if discovery_signal > 0.5 and patent_activity > 0.6:
            spike += 0.115
        if patent_novelty > 0.55:
            spike += 0.070
        if "autonomous" in text or "ai" in text:
            spike += 0.040
        if pressure_score >= 0.65:
            spike += 0.040
        if inevitability_score >= 0.75:
            spike += 0.040
        if momentum_score >= 0.72:
            spike += 0.030
        if category_score >= 0.78:
            spike += 0.030
        if buyer_pull_score >= 0.78:
            spike += 0.025
        if moat_score >= 0.70:
            spike += 0.025
        if value_capture_score >= 0.70:
            spike += 0.030
        if buyer_roi_score >= 0.70:
            spike += 0.020
        if risk_score <= 0.55 and blocker_level != "conditional":
            spike += 0.012

        breakthrough_signal = self._amplify(base_breakthrough + spike)
        phase_log.append(self._decision("breakthrough", breakthrough_signal))

        innovation_signal = self._amplify(
            breakthrough_signal * 0.335 +
            discovery_signal * 0.180 +
            analysis_signal * 0.080 +
            gap_confidence * 0.050 +
            trajectory_confidence * 0.050 +
            inevitability_score * 0.040 +
            formation_confidence * 0.050 +
            category_score * 0.035 +
            moat_score * 0.040 +
            moat_confidence * 0.025 +
            risk_confidence * 0.018 +
            business_confidence * 0.035 +
            value_capture_score * 0.030 -
            blocker_penalty
        )
        phase_log.append(self._decision("innovation", innovation_signal))

        viability_signal = self._amplify(
            innovation_signal * 0.335 +
            financial_health * 0.195 +
            (1 - financial_risk) * 0.110 +
            pressure_score * 0.040 +
            timing_score * 0.050 +
            buyer_pull_score * 0.050 +
            formation_confidence * 0.028 +
            moat_score * 0.040 +
            (1 - copy_risk_score) * 0.018 +
            risk_confidence * 0.025 +
            business_confidence * 0.055 +
            value_capture_score * 0.055 +
            buyer_roi_score * 0.040 -
            risk_score * 0.028 -
            regulatory_score * 0.014 -
            commercial_risk_score * 0.025 -
            blocker_penalty
        )
        phase_log.append(self._decision("viability", viability_signal))

        build_signal = self._amplify(
            viability_signal * 0.505 +
            innovation_signal * 0.175 +
            breakthrough_signal * 0.090 +
            gap_confidence * 0.032 +
            trajectory_confidence * 0.032 +
            formation_confidence * 0.028 +
            moat_confidence * 0.040 +
            risk_confidence * 0.022 +
            business_confidence * 0.030 -
            blocker_penalty
        )
        phase_log.append(self._decision("buildability", build_signal))

        feasibility_signal = self._amplify(
            build_signal * 0.605 +
            viability_signal * 0.315 +
            risk_confidence * 0.028 +
            business_confidence * 0.030 -
            risk_score * 0.018 -
            blocker_penalty
        )
        phase_log.append(self._decision("feasibility", feasibility_signal))

        match_signal = self._amplify(
            feasibility_signal * 0.520 +
            innovation_signal * 0.160 +
            gap_confidence * 0.050 +
            trajectory_confidence * 0.040 +
            buyer_pull_score * 0.040 +
            category_score * 0.030 +
            moat_score * 0.030 +
            moat_confidence * 0.018 +
            risk_confidence * 0.020 +
            business_confidence * 0.040 +
            value_capture_score * 0.030 -
            blocker_penalty
        )
        phase_log.append(self._decision("matching", match_signal))

        acquisition_signal = self._amplify(
            match_signal * 0.590 +
            viability_signal * 0.130 +
            pressure_score * 0.040 +
            inevitability_score * 0.040 +
            category_score * 0.028 +
            buyer_pull_score * 0.028 +
            moat_score * 0.040 +
            risk_confidence * 0.020 +
            business_confidence * 0.045 +
            value_capture_score * 0.035 -
            blocker_penalty
        )
        phase_log.append(self._decision("acquisition", acquisition_signal))

        optimization_signal = self._amplify(
            acquisition_signal * 0.670 +
            innovation_signal * 0.090 +
            gap_confidence * 0.028 +
            momentum_score * 0.028 +
            formation_confidence * 0.040 +
            moat_confidence * 0.040 +
            risk_confidence * 0.025 +
            business_confidence * 0.055 +
            value_capture_score * 0.035 -
            blocker_penalty
        )
        phase_log.append(self._decision("optimization", optimization_signal))

        portfolio_signal = min(
            0.94,
            self._amplify(
                optimization_signal * 0.660 +
                acquisition_signal * 0.075 +
                pressure_score * 0.022 +
                inevitability_score * 0.030 +
                timing_score * 0.018 +
                category_score * 0.022 +
                buyer_pull_score * 0.016 +
                moat_score * 0.030 +
                (1 - copy_risk_score) * 0.008 +
                risk_confidence * 0.020 +
                business_confidence * 0.055 +
                value_capture_score * 0.040 +
                buyer_roi_score * 0.030 -
                risk_score * 0.010 -
                regulatory_score * 0.006 -
                commercial_risk_score * 0.018 -
                blocker_penalty
            )
        )
        phase_log.append(self._decision("portfolio", portfolio_signal))

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
            "business_model_confidence": business_confidence,
            "value_capture_score": value_capture_score,
            "buyer_roi_score": buyer_roi_score,
            "commercial_risk_score": commercial_risk_score,
            "breakthrough_base": base_breakthrough,
            "breakthrough_spike": spike,
            "breakthrough_final": breakthrough_signal,
        }

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
            "business_model": {
                "revenue_model": business_model.get("revenue_model") if isinstance(business_model, dict) else None,
                "pricing_model": business_model.get("pricing_model") if isinstance(business_model, dict) else None,
                "value_capture": business_model.get("value_capture") if isinstance(business_model, dict) else None,
                "buyer_roi": business_model.get("buyer_roi") if isinstance(business_model, dict) else None,
                "commercial_risk": business_model.get("commercial_risk") if isinstance(business_model, dict) else None,
                "confidence": business_model.get("confidence") if isinstance(business_model, dict) else None,
            },
        }

        system_design = self._safe_engine(
            "design_failed",
            lambda: self.auto_designer.generate(intent=intent, context={**data, "scores": scores}),
        )
        data["system_design"] = system_design

        design_portal = self._safe_engine(
            "portal_failed",
            lambda: self.design_portal.evaluate({
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
                "business_model": business_model,
            }),
            fallback={"status": "portal_failed", "route_to_design": False},
        )
        data["design_portal"] = design_portal

        design_output = self._safe_engine(
            "design_engine_failed",
            lambda: self.system_designer.generate(design_portal)
            if design_portal.get("route_to_design", False)
            else {"status": "not_routed", "message": "Design portal did not activate."},
        )
        data["design_output"] = design_output

        try:
            acquirer_matches = self.matcher.match(keywords=keywords, domain=domain, market_gap=market_gap)
        except Exception:
            acquirer_matches = []

        portfolio_binder = self._safe_engine(
            "binder_failed",
            lambda: self.binder_builder.build({
                "scores": scores,
                "domain": domain,
                "keywords": keywords,
                "market_gap": market_gap,
                "trend_trajectory": trend_trajectory,
                "market_formation": market_formation,
                "moat": moat,
                "risk_regulation": risk_regulation,
                "business_model": business_model,
                "system_design": system_design,
                "design_output": data.get("design_output", {}),
                "acquirer_matches": acquirer_matches,
                "signal_trace": data.get("signal_trace", {}),
                "phase_log": phase_log,
            }),
        )
        data["portfolio_binder"] = portfolio_binder

        lifecycle = self._safe_engine(
            "lifecycle_failed",
            lambda: self.lifecycle_engine.evaluate({
                "scores": scores,
                "domain": domain,
                "keywords": keywords,
                "connector_sources": external,
                "market_gap": market_gap,
                "trend_trajectory": trend_trajectory,
                "market_formation": market_formation,
                "moat": moat,
                "risk_regulation": risk_regulation,
                "business_model": business_model,
                "signal_trace": data.get("signal_trace", {}),
                "engine_details": data.get("engine_details", {}),
                "system_design": system_design,
                "design_portal": design_portal,
                "design_output": data.get("design_output", {}),
                "acquirer_matches": acquirer_matches,
                "portfolio_binder": data.get("portfolio_binder", {}),
                "phase_log": phase_log,
            }),
        )
        data["lifecycle"] = lifecycle
        data["lifecycle_stages"] = lifecycle.get("stages", [])
        data["lifecycle_summary"] = lifecycle.get("summary", {})

        final_score = portfolio_signal
        decision = "GO" if final_score > 0.7 else "CONSIDER" if final_score > 0.5 else "NO-GO"

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

    def _safe_engine(self, failure_status: str, fn, fallback=None):
        try:
            return fn()
        except Exception as e:
            base = fallback.copy() if isinstance(fallback, dict) else {}
            base.update({"status": failure_status, "error": str(e)})
            return base

    def _get(self, obj: Dict[str, Any], path: str, default=None):
        cur = obj if isinstance(obj, dict) else {}
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

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
