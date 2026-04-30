"""
Claire Orchestrator — Deterministic Intelligence Engine (v5.8 SYSTEM DESIGN ENGINE)

Adds:
- Signal trace
- Engine details
- Acquirer matching
- Conditional Design Portal routing
- SystemDesignEngine technical blueprint generation
"""

from typing import Dict, Any

from claire.domain.contract import ClaireIntent, ClaireResult
from claire.connectors.connector_manager import ConnectorManager
from claire.engines.auto_design import AutoDesignEngine
from claire.engines.acquirer_matching import AcquirerMatchingEngine
from claire.engines.system_design_engine import SystemDesignEngine
from claire.design.portal import DesignPortal


class PipelineOrchestrator:

    def __init__(self):
        self.connector_manager = ConnectorManager()
        self.auto_designer = AutoDesignEngine()
        self.matcher = AcquirerMatchingEngine()
        self.design_portal = DesignPortal()
        self.system_designer = SystemDesignEngine()

    def execute(self, intent: ClaireIntent) -> ClaireResult:

        print(">>> RUNNING PIPELINE V5.8 (SYSTEM DESIGN ENGINE) <<<")

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
        # ANALYSIS
        # =========================
        analysis_signal = self._amplify(
            0.3 + (len(keywords) * 0.025)
        )

        data["domain"] = domain
        data["keywords"] = keywords

        phase_log.append(self._decision("analysis", analysis_signal))

        # =========================
        # DISCOVERY
        # =========================
        discovery_signal = self._amplify(
            analysis_signal * 0.7 +
            market_growth * 0.25 +
            (0.05 if patent_activity > 0.6 else 0)
        )

        phase_log.append(self._decision("discovery", discovery_signal))

        # =========================
        # BREAKTHROUGH
        # =========================
        base_breakthrough = (
            discovery_signal * 0.45 +
            patent_novelty * 0.35 +
            analysis_signal * 0.20
        )

        spike = 0.0

        if discovery_signal > 0.5 and patent_activity > 0.6:
            spike += 0.20

        if patent_novelty > 0.55:
            spike += 0.12

        if "autonomous" in text or "ai" in text:
            spike += 0.06

        breakthrough_signal = self._amplify(base_breakthrough + spike)

        phase_log.append(self._decision("breakthrough", breakthrough_signal))

        # =========================
        # INNOVATION
        # =========================
        innovation_signal = self._amplify(
            breakthrough_signal * 0.5 +
            discovery_signal * 0.3 +
            analysis_signal * 0.2
        )

        phase_log.append(self._decision("innovation", innovation_signal)) # =========================
        # VIABILITY
        # =========================
        viability_signal = self._amplify(
            innovation_signal * 0.5 +
            financial_health * 0.3 +
            (1 - financial_risk) * 0.2
        )

        phase_log.append(self._decision("viability", viability_signal))

        # =========================
        # BUILDABILITY
        # =========================
        build_signal = self._amplify(
            viability_signal * 0.6 +
            innovation_signal * 0.25 +
            breakthrough_signal * 0.15
        )

        phase_log.append(self._decision("buildability", build_signal))

        # =========================
        # FEASIBILITY
        # =========================
        feasibility_signal = self._amplify(
            build_signal * 0.65 +
            viability_signal * 0.35
        )

        phase_log.append(self._decision("feasibility", feasibility_signal))

        # =========================
        # MATCHING
        # =========================
        match_signal = self._amplify(
            feasibility_signal * 0.7 +
            innovation_signal * 0.3
        )

        phase_log.append(self._decision("matching", match_signal))

        # =========================
        # ACQUISITION
        # =========================
        acquisition_signal = self._amplify(
            match_signal * 0.75 +
            viability_signal * 0.25
        )

        phase_log.append(self._decision("acquisition", acquisition_signal))

        # =========================
        # OPTIMIZATION
        # =========================
        optimization_signal = self._amplify(
            acquisition_signal * 0.8 +
            innovation_signal * 0.2
        )

        phase_log.append(self._decision("optimization", optimization_signal))

        # =========================
        # PORTFOLIO
        # =========================
        portfolio_signal = min(
            0.94,
            self._amplify(
                optimization_signal * 0.85 +
                acquisition_signal * 0.15
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
        }# =========================
        # AUTO DESIGN
        # =========================
        try:
            system_design = self.auto_designer.generate(
                intent=intent,
                context={**data, "scores": scores},
            )
            data["system_design"] = system_design
        except Exception as e:
            system_design = {
                "status": "design_failed",
                "error": str(e),
            }
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
            })
            data["design_portal"] = design_portal
        except Exception as e:
            design_portal = {
                "status": "portal_failed",
                "route_to_design": False,
                "error": str(e),
            }
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
            data["design_output"] = {
                "status": "design_engine_failed",
                "error": str(e),
            }

        # =========================
        # ACQUIRER MATCHING
        # =========================
        try:
            acquirer_matches = self.matcher.match(
                keywords=keywords,
                domain=domain,
            )
        except Exception:
            acquirer_matches = []

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

        if "ai" in t or "machine learning" in t:
            return "technology"

        if "finance" in t or "fintech" in t:
            return "finance"

        if "health" in t or "medical" in t or "clinical" in t:
            return "healthcare"

        if "defense" in t or "military" in t or "battlefield" in t:
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