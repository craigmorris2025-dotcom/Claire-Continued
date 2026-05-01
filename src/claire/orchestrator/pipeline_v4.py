
"""
Claire Orchestrator — Deterministic Intelligence Engine (v5.33 EXPORT WRITER)
"""

from typing import Dict, Any

from claire.domain.contract import ClaireIntent, ClaireResult
from claire.connectors.connector_manager import ConnectorManager
from claire.engines.auto_design import AutoDesignEngine
from claire.engines.acquirer_matching import AcquirerMatchingEngine
from claire.engines.system_design_engine import SystemDesignEngine
from claire.engines.market_gap_engine import MarketGapEngine
from claire.engines.knowledge_ingestion_engine import KnowledgeIngestionEngine
from claire.engines.signal_extraction_engine import SignalExtractionEngine
from claire.engines.trend_trajectory_engine import TrendTrajectoryEngine
from claire.engines.market_formation_engine import MarketFormationEngine
from claire.engines.moat_defensibility_engine import MoatDefensibilityEngine
from claire.engines.risk_regulation_engine import RiskRegulationEngine
from claire.engines.business_model_engine import BusinessModelEngine
from claire.engines.opportunity_discovery_engine import OpportunityDiscoveryEngine
from claire.engines.breakthrough_synthesis_engine import BreakthroughSynthesisEngine
from claire.engines.technical_feasibility_engine import TechnicalFeasibilityEngine
from claire.engines.productization_path_engine import ProductizationPathEngine
from claire.engines.strategic_positioning_engine import StrategicPositioningEngine
from claire.engines.deal_exit_modeling_engine import DealExitModelingEngine
from claire.engines.lifecycle_stage_engine import LifecycleStageEngine
from claire.engines.export_package_engine import ExportPackageEngine
from claire.export.export_writer import ExportWriter
from claire.design.portal import DesignPortal
from claire.portfolio.binder_builder import PortfolioBinderBuilder


class PipelineOrchestrator:

    def __init__(self):
        self.connector_manager = ConnectorManager()
        self.auto_designer = AutoDesignEngine()
        self.matcher = AcquirerMatchingEngine()
        self.design_portal = DesignPortal()
        self.system_designer = SystemDesignEngine()
        self.knowledge_ingestion_engine = KnowledgeIngestionEngine()
        self.signal_extraction_engine = SignalExtractionEngine()
        self.market_gap_engine = MarketGapEngine()
        self.trend_engine = TrendTrajectoryEngine()
        self.market_formation_engine = MarketFormationEngine()
        self.moat_engine = MoatDefensibilityEngine()
        self.risk_engine = RiskRegulationEngine()
        self.business_model_engine = BusinessModelEngine()
        self.opportunity_engine = OpportunityDiscoveryEngine()
        self.breakthrough_synthesis_engine = BreakthroughSynthesisEngine()
        self.technical_feasibility_engine = TechnicalFeasibilityEngine()
        self.productization_engine = ProductizationPathEngine()
        self.strategic_positioning_engine = StrategicPositioningEngine()
        self.deal_exit_engine = DealExitModelingEngine()
        self.binder_builder = PortfolioBinderBuilder()
        self.lifecycle_engine = LifecycleStageEngine()
        self.export_package_engine = ExportPackageEngine()
        self.export_writer = ExportWriter()

    def execute(self, intent: ClaireIntent) -> ClaireResult:

        print(">>> RUNNING PIPELINE V5.33 (EXPORT WRITER) <<<")

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

        intent_metadata = intent.metadata.to_dict() if hasattr(intent, "metadata") and hasattr(intent.metadata, "to_dict") else {}

        knowledge_ingestion = self._safe_engine(
            "knowledge_ingestion_failed",
            lambda: self.knowledge_ingestion_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                connector_sources=external,
                metadata=intent_metadata,
            ),
        )

        knowledge_ingestion_confidence = self._get(knowledge_ingestion, "confidence", 0.0) or 0.0
        knowledge_quality_score = self._get(knowledge_ingestion, "knowledge_quality_score.score", 0.0) or 0.0
        source_quality_score = self._get(knowledge_ingestion, "source_quality.score", 0.0) or 0.0
        coverage_score = self._get(knowledge_ingestion, "coverage_assessment.score", 0.0) or 0.0
        source_count = self._get(knowledge_ingestion, "source_inventory.source_count", 0) or 0

        signal_extraction = self._safe_engine(
            "signal_extraction_failed",
            lambda: self.signal_extraction_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                connector_sources=external,
            ),
        )

        signal_extraction_confidence = self._get(signal_extraction, "confidence", 0.0) or 0.0
        signal_quality_score = self._get(signal_extraction, "signal_quality_score.score", 0.0) or 0.0
        semantic_density_score = self._get(signal_extraction, "semantic_profile.semantic_density_score", 0.0) or 0.0
        routing_confidence_score = self._get(signal_extraction, "routing_evidence.routing_confidence_score", 0.0) or 0.0
        evidence_signal_score = self._get(signal_extraction, "evidence_signals.score", 0.0) or 0.0
        control_signal_score = self._get(signal_extraction, "control_signals.score", 0.0) or 0.0

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

        opportunity_discovery = self._safe_engine(
            "opportunity_discovery_failed",
            lambda: self.opportunity_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                moat=moat,
                risk_regulation=risk_regulation,
                business_model=business_model,
                connector_sources=external,
            ),
        )

        data.update({
            "domain": domain,
            "keywords": keywords,
            "knowledge_ingestion": knowledge_ingestion,
            "connector_sources": external,
            "signal_extraction": signal_extraction,
            "market_gap": market_gap,
            "trend_trajectory": trend_trajectory,
            "market_formation": market_formation,
            "moat": moat,
            "risk_regulation": risk_regulation,
            "business_model": business_model,
            "opportunity_discovery": opportunity_discovery,
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

        opportunity_confidence = self._get(opportunity_discovery, "confidence", 0.0)
        opportunity_score = self._get(opportunity_discovery, "opportunity_score.score", 0.0)
        opportunity_priority_score = self._get(opportunity_discovery, "priority_assessment.score", 0.0)
        validation_urgency_score = self._get(opportunity_discovery, "validation_urgency.score", 0.0)

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
            opportunity_confidence * 0.030 +
            opportunity_score * 0.035 +
            opportunity_priority_score * 0.020 +
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
            buyer_roi_score * 0.024 +
            opportunity_score * 0.040 +
            opportunity_priority_score * 0.030 +
            validation_urgency_score * 0.012 -
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
        if opportunity_score >= 0.78:
            spike += 0.030
        if opportunity_priority_score >= 0.78:
            spike += 0.020
        if validation_urgency_score >= 0.72:
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
            value_capture_score * 0.030 +
            opportunity_confidence * 0.025 +
            opportunity_score * 0.030 -
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
            buyer_roi_score * 0.040 +
            opportunity_score * 0.025 +
            opportunity_priority_score * 0.018 -
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
            value_capture_score * 0.030 +
            opportunity_score * 0.024 -
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
            value_capture_score * 0.035 +
            opportunity_score * 0.020 -
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
            value_capture_score * 0.035 +
            opportunity_confidence * 0.020 +
            opportunity_score * 0.020 -
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
                buyer_roi_score * 0.030 +
                opportunity_score * 0.030 +
                opportunity_priority_score * 0.018 -
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
            "opportunity_score": opportunity_score,
            "opportunity_priority_score": opportunity_priority_score,
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
            "knowledge_quality_score": knowledge_quality_score,
            "source_quality_score": source_quality_score,
            "coverage_score": coverage_score,
            "source_count": source_count,
            "signal_quality_score": signal_quality_score,
            "semantic_density_score": semantic_density_score,
            "routing_confidence_score": routing_confidence_score,
            "evidence_signal_score": evidence_signal_score,
            "control_signal_score": control_signal_score,
        }

        breakthrough_synthesis = self._safe_engine(
            "breakthrough_synthesis_failed",
            lambda: self.breakthrough_synthesis_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                scores=scores,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                opportunity_discovery=opportunity_discovery,
                moat=moat,
                risk_regulation=risk_regulation,
                business_model=business_model,
                connector_sources=external,
            ),
        )
        data["breakthrough_synthesis"] = breakthrough_synthesis

        synthesis_confidence = self._get(breakthrough_synthesis, "confidence", 0.0) or 0.0
        synthesis_score = self._get(breakthrough_synthesis, "breakthrough_synthesis_score.score", 0.0) or 0.0
        novelty_score = self._get(breakthrough_synthesis, "novelty_assessment.score", 0.0) or 0.0
        non_obviousness_score = self._get(breakthrough_synthesis, "non_obviousness.score", 0.0) or 0.0
        mechanism_score = self._get(breakthrough_synthesis, "breakthrough_mechanism.mechanism_score", 0.0) or 0.0

        scores["breakthrough_synthesis_score"] = synthesis_score
        scores["novelty_score"] = novelty_score
        scores["non_obviousness_score"] = non_obviousness_score

        technical_feasibility = self._safe_engine(
            "technical_feasibility_failed",
            lambda: self.technical_feasibility_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                scores=scores,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                opportunity_discovery=opportunity_discovery,
                breakthrough_synthesis=breakthrough_synthesis,
                moat=moat,
                risk_regulation=risk_regulation,
                business_model=business_model,
                connector_sources=external,
            ),
        )
        data["technical_feasibility"] = technical_feasibility

        technical_feasibility_confidence = self._get(technical_feasibility, "confidence", 0.0) or 0.0
        technical_feasibility_score = self._get(technical_feasibility, "technical_feasibility_score.score", 0.0) or 0.0
        architecture_readiness_score = self._get(technical_feasibility, "architecture_readiness.score", 0.0) or 0.0
        implementation_complexity_score = self._get(technical_feasibility, "implementation_complexity.score", 0.0) or 0.0
        integration_readiness_score = self._get(technical_feasibility, "integration_readiness.score", 0.0) or 0.0
        data_readiness_score = self._get(technical_feasibility, "data_readiness.score", 0.0) or 0.0
        validation_burden_score = self._get(technical_feasibility, "validation_burden.score", 0.0) or 0.0

        scores["technical_feasibility_score"] = technical_feasibility_score
        scores["architecture_readiness_score"] = architecture_readiness_score
        scores["implementation_complexity_score"] = implementation_complexity_score
        scores["integration_readiness_score"] = integration_readiness_score
        scores["data_readiness_score"] = data_readiness_score
        scores["validation_burden_score"] = validation_burden_score

        data["signal_trace"] = {
            "knowledge_ingestion_confidence": knowledge_ingestion_confidence,
            "knowledge_quality_score": knowledge_quality_score,
            "source_quality_score": source_quality_score,
            "coverage_score": coverage_score,
            "source_count": source_count,
            "signal_extraction_confidence": signal_extraction_confidence,
            "signal_quality_score": signal_quality_score,
            "semantic_density_score": semantic_density_score,
            "routing_confidence_score": routing_confidence_score,
            "evidence_signal_score": evidence_signal_score,
            "control_signal_score": control_signal_score,
            "analysis": analysis_signal,
            "discovery": discovery_signal,
            "opportunity_confidence": opportunity_confidence,
            "opportunity_score": opportunity_score,
            "opportunity_priority_score": opportunity_priority_score,
            "validation_urgency_score": validation_urgency_score,
            "breakthrough_synthesis_confidence": synthesis_confidence,
            "breakthrough_synthesis_score": synthesis_score,
            "novelty_score": novelty_score,
            "non_obviousness_score": non_obviousness_score,
            "breakthrough_mechanism_score": mechanism_score,
            "technical_feasibility_confidence": technical_feasibility_confidence,
            "technical_feasibility_score": technical_feasibility_score,
            "architecture_readiness_score": architecture_readiness_score,
            "implementation_complexity_score": implementation_complexity_score,
            "integration_readiness_score": integration_readiness_score,
            "data_readiness_score": data_readiness_score,
            "validation_burden_score": validation_burden_score,
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
                "knowledge_ingestion": knowledge_quality_score,
                "signal_extraction": signal_quality_score,
                "analysis": analysis_signal,
                "discovery": discovery_signal,
                "breakthrough": breakthrough_signal,
            "opportunity": opportunity_score,
                "innovation": innovation_signal,
                "viability": viability_signal,
                "portfolio": portfolio_signal,
            },
            "knowledge_ingestion": {
                "knowledge_quality_score": knowledge_ingestion.get("knowledge_quality_score") if isinstance(knowledge_ingestion, dict) else None,
                "source_quality": knowledge_ingestion.get("source_quality") if isinstance(knowledge_ingestion, dict) else None,
                "coverage_assessment": knowledge_ingestion.get("coverage_assessment") if isinstance(knowledge_ingestion, dict) else None,
                "source_inventory": knowledge_ingestion.get("source_inventory") if isinstance(knowledge_ingestion, dict) else None,
                "confidence": knowledge_ingestion.get("confidence") if isinstance(knowledge_ingestion, dict) else None,
            },
            "signal_extraction": {
                "signal_quality_score": signal_extraction.get("signal_quality_score") if isinstance(signal_extraction, dict) else None,
                "semantic_profile": signal_extraction.get("semantic_profile") if isinstance(signal_extraction, dict) else None,
                "dominant_sector": signal_extraction.get("dominant_sector") if isinstance(signal_extraction, dict) else None,
                "routing_evidence": signal_extraction.get("routing_evidence") if isinstance(signal_extraction, dict) else None,
                "confidence": signal_extraction.get("confidence") if isinstance(signal_extraction, dict) else None,
            },
            "connectors": {
                "market_growth": market_growth,
                "patent_activity": patent_activity,
                "patent_novelty": patent_novelty,
                "financial_health": financial_health,
                "financial_risk": financial_risk,
            },
            "opportunity_discovery": {
                "opportunity_score": opportunity_discovery.get("opportunity_score") if isinstance(opportunity_discovery, dict) else None,
                "opportunity_type": opportunity_discovery.get("opportunity_type") if isinstance(opportunity_discovery, dict) else None,
                "priority_assessment": opportunity_discovery.get("priority_assessment") if isinstance(opportunity_discovery, dict) else None,
                "validation_urgency": opportunity_discovery.get("validation_urgency") if isinstance(opportunity_discovery, dict) else None,
                "confidence": opportunity_discovery.get("confidence") if isinstance(opportunity_discovery, dict) else None,
            },
            "breakthrough_synthesis": {
                "breakthrough_synthesis_score": breakthrough_synthesis.get("breakthrough_synthesis_score") if isinstance(breakthrough_synthesis, dict) else None,
                "breakthrough_classification": breakthrough_synthesis.get("breakthrough_classification") if isinstance(breakthrough_synthesis, dict) else None,
                "novelty_assessment": breakthrough_synthesis.get("novelty_assessment") if isinstance(breakthrough_synthesis, dict) else None,
                "non_obviousness": breakthrough_synthesis.get("non_obviousness") if isinstance(breakthrough_synthesis, dict) else None,
                "confidence": breakthrough_synthesis.get("confidence") if isinstance(breakthrough_synthesis, dict) else None,
            },
            "technical_feasibility": {
                "technical_feasibility_score": technical_feasibility.get("technical_feasibility_score") if isinstance(technical_feasibility, dict) else None,
                "feasibility_classification": technical_feasibility.get("feasibility_classification") if isinstance(technical_feasibility, dict) else None,
                "architecture_readiness": technical_feasibility.get("architecture_readiness") if isinstance(technical_feasibility, dict) else None,
                "implementation_complexity": technical_feasibility.get("implementation_complexity") if isinstance(technical_feasibility, dict) else None,
                "diligence_readiness": technical_feasibility.get("diligence_readiness") if isinstance(technical_feasibility, dict) else None,
                "confidence": technical_feasibility.get("confidence") if isinstance(technical_feasibility, dict) else None,
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
                "signal_extraction": signal_extraction,
                "signal_extraction": signal_extraction,
                "market_gap": market_gap,
                "trend_trajectory": trend_trajectory,
                "market_formation": market_formation,
                "moat": moat,
                "risk_regulation": risk_regulation,
                "business_model": business_model,
                "opportunity_discovery": opportunity_discovery,
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

        productization_path = self._safe_engine(
            "productization_path_failed",
            lambda: self.productization_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                scores=scores,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                opportunity_discovery=opportunity_discovery,
                breakthrough_synthesis=breakthrough_synthesis,
                technical_feasibility=technical_feasibility,
                moat=moat,
                risk_regulation=risk_regulation,
                business_model=business_model,
                design_output=design_output,
                connector_sources=external,
            ),
        )
        data["productization_path"] = productization_path

        productization_path_confidence = self._get(productization_path, "confidence", 0.0) or 0.0
        productization_score = self._get(productization_path, "productization_score.score", 0.0) or 0.0
        pilot_readiness_score = self._get(productization_path, "go_to_market_readiness.score", 0.0) or 0.0
        packaging_readiness_score = productization_score
        launch_control_level = self._get(productization_path, "launch_controls.control_level", "")
        productization_state = self._get(productization_path, "productization_classification.state", "")

        scores["productization_score"] = productization_score
        scores["pilot_readiness_score"] = pilot_readiness_score
        scores["packaging_readiness_score"] = packaging_readiness_score

        data["signal_trace"].update({
            "productization_path_confidence": productization_path_confidence,
            "productization_score": productization_score,
            "pilot_readiness_score": pilot_readiness_score,
            "packaging_readiness_score": packaging_readiness_score,
            "launch_control_level": launch_control_level,
            "productization_state": productization_state,
        })

        data["engine_details"]["signals"]["productization"] = productization_score
        data["engine_details"]["productization_path"] = {
            "productization_score": productization_path.get("productization_score") if isinstance(productization_path, dict) else None,
            "productization_classification": productization_path.get("productization_classification") if isinstance(productization_path, dict) else None,
            "pilot_strategy": productization_path.get("pilot_strategy") if isinstance(productization_path, dict) else None,
            "go_to_market_readiness": productization_path.get("go_to_market_readiness") if isinstance(productization_path, dict) else None,
            "confidence": productization_path.get("confidence") if isinstance(productization_path, dict) else None,
        }

        try:
            acquirer_matches = self.matcher.match(keywords=keywords, domain=domain, market_gap=market_gap)
        except Exception:
            acquirer_matches = []

        deal_exit_modeling = self._safe_engine(
            "deal_exit_modeling_failed",
            lambda: self.deal_exit_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                scores=scores,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                moat=moat,
                risk_regulation=risk_regulation,
                business_model=business_model,
                acquirer_matches=acquirer_matches,
                connector_sources=external,
            ),
        )
        data["deal_exit_modeling"] = deal_exit_modeling

        deal_confidence = self._get(deal_exit_modeling, "confidence", 0.0) or 0.0
        exit_readiness_score = self._get(deal_exit_modeling, "exit_readiness.score", 0.0) or 0.0
        strategic_fit_score = self._get(deal_exit_modeling, "strategic_fit.score", 0.0) or 0.0
        valuation_signal_score = self._get(deal_exit_modeling, "valuation_logic.valuation_signal.score", 0.0) or 0.0

        data["signal_trace"].update({
            "deal_exit_confidence": deal_confidence,
            "exit_readiness_score": exit_readiness_score,
            "strategic_fit_score": strategic_fit_score,
            "valuation_signal_score": valuation_signal_score,
        })

        data["engine_details"]["deal_exit_modeling"] = {
            "exit_readiness": deal_exit_modeling.get("exit_readiness") if isinstance(deal_exit_modeling, dict) else None,
            "strategic_fit": deal_exit_modeling.get("strategic_fit") if isinstance(deal_exit_modeling, dict) else None,
            "valuation_logic": deal_exit_modeling.get("valuation_logic") if isinstance(deal_exit_modeling, dict) else None,
            "confidence": deal_exit_modeling.get("confidence") if isinstance(deal_exit_modeling, dict) else None,
        }

        strategic_positioning = self._safe_engine(
            "strategic_positioning_failed",
            lambda: self.strategic_positioning_engine.analyze(
                text=text,
                domain=domain,
                keywords=keywords,
                scores=scores,
                market_gap=market_gap,
                trend_trajectory=trend_trajectory,
                market_formation=market_formation,
                opportunity_discovery=opportunity_discovery,
                breakthrough_synthesis=breakthrough_synthesis,
                technical_feasibility=technical_feasibility,
                productization_path=productization_path,
                moat=moat,
                risk_regulation=risk_regulation,
                business_model=business_model,
                deal_exit_modeling=deal_exit_modeling,
                design_output=design_output,
                acquirer_matches=acquirer_matches,
                connector_sources=external,
            ),
        )
        data["strategic_positioning"] = strategic_positioning

        strategic_positioning_confidence = self._get(strategic_positioning, "confidence", 0.0) or 0.0
        strategic_positioning_score = self._get(strategic_positioning, "strategic_positioning_score.score", 0.0) or 0.0
        narrative_strength_score = strategic_positioning_score
        acquirer_positioning_score = self._get(strategic_positioning, "acquirer_positioning.top_acquirer_score", 0.0) or 0.0
        positioning_state = self._get(strategic_positioning, "positioning_classification.state", "")
        narrative_posture = self._get(strategic_positioning, "positioning_classification.narrative_posture", "")

        scores["strategic_positioning_score"] = strategic_positioning_score
        scores["narrative_strength_score"] = narrative_strength_score
        scores["acquirer_positioning_score"] = acquirer_positioning_score

        data["signal_trace"].update({
            "strategic_positioning_confidence": strategic_positioning_confidence,
            "strategic_positioning_score": strategic_positioning_score,
            "narrative_strength_score": narrative_strength_score,
            "acquirer_positioning_score": acquirer_positioning_score,
            "positioning_state": positioning_state,
            "narrative_posture": narrative_posture,
        })

        data["engine_details"]["signals"]["strategic_positioning"] = strategic_positioning_score
        data["engine_details"]["strategic_positioning"] = {
            "strategic_positioning_score": strategic_positioning.get("strategic_positioning_score") if isinstance(strategic_positioning, dict) else None,
            "positioning_classification": strategic_positioning.get("positioning_classification") if isinstance(strategic_positioning, dict) else None,
            "category_positioning": strategic_positioning.get("category_positioning") if isinstance(strategic_positioning, dict) else None,
            "buyer_positioning": strategic_positioning.get("buyer_positioning") if isinstance(strategic_positioning, dict) else None,
            "acquirer_positioning": strategic_positioning.get("acquirer_positioning") if isinstance(strategic_positioning, dict) else None,
            "confidence": strategic_positioning.get("confidence") if isinstance(strategic_positioning, dict) else None,
        }

        portfolio_binder = self._safe_engine(
            "binder_failed",
            lambda: self.binder_builder.build({
                "scores": scores,
                "domain": domain,
                "keywords": keywords,
                "knowledge_ingestion": knowledge_ingestion,
                "signal_extraction": signal_extraction,
                "market_gap": market_gap,
                "trend_trajectory": trend_trajectory,
                "market_formation": market_formation,
                "moat": moat,
                "risk_regulation": risk_regulation,
                "business_model": business_model,
                "opportunity_discovery": opportunity_discovery,
                "breakthrough_synthesis": breakthrough_synthesis,
                "technical_feasibility": technical_feasibility,
                "productization_path": productization_path,
                "deal_exit_modeling": deal_exit_modeling,
                "strategic_positioning": strategic_positioning,
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
                "knowledge_ingestion": knowledge_ingestion,
                "signal_extraction": signal_extraction,
                "connector_sources": external,
                "market_gap": market_gap,
                "trend_trajectory": trend_trajectory,
                "market_formation": market_formation,
                "moat": moat,
                "risk_regulation": risk_regulation,
                "business_model": business_model,
                "opportunity_discovery": opportunity_discovery,
                "breakthrough_synthesis": breakthrough_synthesis,
                "technical_feasibility": technical_feasibility,
                "productization_path": productization_path,
                "deal_exit_modeling": deal_exit_modeling,
                "strategic_positioning": strategic_positioning,
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
        data["connector_sources"] = external
        data["external_signals"] = external

        export_package = self._safe_engine(
            "export_package_failed",
            lambda: self.export_package_engine.build({
                "scores": scores,
                "data": data,
                "domain": domain,
                "keywords": keywords,
                "decision_classification": "GO" if portfolio_signal > 0.7 else "CONSIDER" if portfolio_signal > 0.5 else "NO-GO",
                "breakthrough_classification": "HIGH" if breakthrough_signal > 0.65 else "LOW",
                "acquirer_matches": acquirer_matches,
            }),
        )
        data["export_package"] = export_package

        export_package_confidence = self._get(export_package, "confidence", 0.0) or 0.0
        export_package_score = self._get(export_package, "export_package_score.score", 0.0) or 0.0
        export_package_level = self._get(export_package, "export_package_score.level", "")

        scores["export_package_score"] = export_package_score

        data["signal_trace"].update({
            "export_package_confidence": export_package_confidence,
            "export_package_score": export_package_score,
            "export_package_level": export_package_level,
        })

        data["engine_details"]["signals"]["export_package"] = export_package_score
        data["engine_details"]["export_package"] = {
            "export_package_score": export_package.get("export_package_score") if isinstance(export_package, dict) else None,
            "package_profile": export_package.get("package_profile") if isinstance(export_package, dict) else None,
            "package_manifest": export_package.get("package_manifest") if isinstance(export_package, dict) else None,
            "quality_checks": export_package.get("quality_checks") if isinstance(export_package, dict) else None,
            "confidence": export_package.get("confidence") if isinstance(export_package, dict) else None,
        }

        export_writer = self._safe_engine(
            "export_writer_failed",
            lambda: self.export_writer.write(
                export_package=export_package,
                output_root="exports",
                run_id=getattr(intent, "run_id", None) or "unknown",
                context={
                    "decision_classification": decision,
                    "breakthrough_classification": "HIGH" if breakthrough_signal > 0.65 else "LOW",
                    "domain": domain,
                    "keywords": keywords,
                },
            ),
        )
        data["export_writer"] = export_writer

        export_writer_score = self._get(export_writer, "export_writer_score.score", 0.0) or 0.0
        export_writer_level = self._get(export_writer, "export_writer_score.level", "")

        scores["export_writer_score"] = export_writer_score

        data["signal_trace"].update({
            "export_writer_score": export_writer_score,
            "export_writer_level": export_writer_level,
            "export_output_dir": export_writer.get("output_dir") if isinstance(export_writer, dict) else None,
        })

        data["engine_details"]["signals"]["export_writer"] = export_writer_score
        data["engine_details"]["export_writer"] = {
            "export_writer_score": export_writer.get("export_writer_score") if isinstance(export_writer, dict) else None,
            "output_dir": export_writer.get("output_dir") if isinstance(export_writer, dict) else None,
            "written_file_count": export_writer.get("written_file_count") if isinstance(export_writer, dict) else None,
            "manifest_path": export_writer.get("manifest_path") if isinstance(export_writer, dict) else None,
            "index_path": export_writer.get("index_path") if isinstance(export_writer, dict) else None,
            "confidence": export_writer.get("confidence") if isinstance(export_writer, dict) else None,
        }

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
        """
        Conservative plain-text domain router.

        Hotfix:
        - Avoids regex word-boundary issues entirely.
        - Prevents "AI-powered" from triggering energy via "power".
        - Routes insurance / climate insurance before finance or energy.
        - Routes defense/autonomy before energy when defense terms are present.
        """
        t = self._normalize_text(text)

        def contains_word(word: str) -> bool:
            return word.lower() in t.split()

        def contains_phrase(phrase: str) -> bool:
            phrase = self._normalize_text(phrase).strip()
            return f" {phrase} " in f" {t} "

        def has_any_words(words):
            return any(contains_word(word) for word in words)

        def has_any_phrases(phrases):
            return any(contains_phrase(phrase) for phrase in phrases)

        if has_any_phrases([
            "climate insurance",
            "weather losses",
            "property risk",
            "risk transfer",
            "premium repricing",
            "market withdrawal",
            "catastrophe model",
            "cat model",
        ]) or has_any_words([
            "insurance",
            "insurer",
            "insurers",
            "reinsurance",
            "reinsurer",
            "reinsurers",
            "underwriting",
            "underwriter",
            "underwriters",
            "catastrophe",
            "actuarial",
            "claims",
            "broker",
            "brokers",
        ]):
            return "insurance"

        if has_any_phrases([
            "battlefield",
            "secure command",
            "command systems",
            "mission risk",
            "drone coordination",
            "border security",
        ]) or has_any_words([
            "defense",
            "military",
            "mission",
            "drone",
            "drones",
            "uav",
            "surveillance",
            "autonomy",
            "autonomous",
        ]):
            return "technology"

        if has_any_phrases([
            "health system",
            "health systems",
            "care delivery",
            "patient flow",
            "staffing shortages",
        ]) or has_any_words([
            "healthcare",
            "medical",
            "clinical",
            "hospital",
            "hospitals",
            "patient",
            "patients",
        ]):
            return "healthcare"

        if has_any_phrases([
            "supply chain",
            "planning system",
            "planning systems",
            "component shortage",
            "component shortages",
            "production failure",
            "production failures",
        ]) or has_any_words([
            "manufacturing",
            "industrial",
            "supplier",
            "suppliers",
            "erp",
            "procurement",
            "factory",
            "factories",
            "production",
        ]):
            return "industrial"

        if has_any_phrases([
            "capital markets",
            "market intelligence",
            "institutional research",
            "asset manager",
            "asset managers",
            "financial market",
            "financial markets",
        ]) or has_any_words([
            "finance",
            "fintech",
            "financial",
            "credit",
            "liquidity",
            "portfolio",
            "portfolios",
        ]):
            return "finance"

        if has_any_phrases([
            "power grid",
            "power system",
            "power systems",
            "power demand",
            "electric infrastructure",
            "grid instability",
            "transmission bottleneck",
            "transmission bottlenecks",
            "utility operations",
        ]) or has_any_words([
            "energy",
            "grid",
            "utility",
            "utilities",
            "transmission",
        ]):
            return "energy"

        if has_any_phrases([
            "machine learning",
            "ai platform",
            "software platform",
        ]) or has_any_words([
            "ai",
            "platform",
            "software",
        ]):
            return "technology"

        return "general"

    def _normalize_text(self, text: str) -> str:
        chars = []
        for ch in (text or "").lower():
            if ch.isalnum():
                chars.append(ch)
            else:
                chars.append(" ")
        return " ".join("".join(chars).split())

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
