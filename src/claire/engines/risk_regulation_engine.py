"""
Risk Regulation Engine — evaluates regulatory, compliance, operational,
security, privacy, safety, and deployment risks for a Claire opportunity.

Purpose:
- Activate Claire Stage 12: Risk / Regulation / Compliance
- Convert opportunity/design context into a structured risk profile
- Identify likely compliance requirements, blockers, deployment constraints,
  validation requirements, and mitigation actions

This version is deterministic/local. Later versions can plug into live legal,
standards, sector-regulation, cybersecurity, procurement, export-control,
privacy, medical, financial, and industrial-safety datasets.
"""

from typing import Any, Dict, List, Optional


class RiskRegulationEngine:
    """
    Deterministic risk, regulation, and compliance analyzer.
    """

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        market_gap: Optional[Dict[str, Any]] = None,
        trend_trajectory: Optional[Dict[str, Any]] = None,
        market_formation: Optional[Dict[str, Any]] = None,
        moat: Optional[Dict[str, Any]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = (text or "").lower()
        keywords = keywords or []
        market_gap = market_gap or {}
        trend_trajectory = trend_trajectory or {}
        market_formation = market_formation or {}
        moat = moat or {}
        connector_sources = connector_sources or {}

        signals = self._signals(
            text=text,
            keywords=keywords,
            domain=domain,
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
            market_formation=market_formation,
            moat=moat,
            connector_sources=connector_sources,
        )

        risk_profile = self._risk_profile(signals)
        regulation_profile = self._regulation_profile(signals)
        compliance_requirements = self._compliance_requirements(signals)
        operational_risks = self._operational_risks(signals)
        security_privacy = self._security_privacy(signals)
        deployment_constraints = self._deployment_constraints(signals)
        blocker_assessment = self._blocker_assessment(signals, risk_profile, regulation_profile)
        mitigation_actions = self._mitigation_actions(
            signals=signals,
            risk_profile=risk_profile,
            regulation_profile=regulation_profile,
            blocker_assessment=blocker_assessment,
        )

        return {
            "status": "success",
            "domain": domain,
            "sector": market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general",
            "risk_profile": risk_profile,
            "regulation_profile": regulation_profile,
            "compliance_requirements": compliance_requirements,
            "operational_risks": operational_risks,
            "data_security_privacy": security_privacy,
            "deployment_constraints": deployment_constraints,
            "blocker_assessment": blocker_assessment,
            "mitigation_actions": mitigation_actions,
            "validation_requirements": self._validation_requirements(signals, compliance_requirements),
            "risk_regulation_thesis": self._risk_regulation_thesis(
                signals=signals,
                risk_profile=risk_profile,
                regulation_profile=regulation_profile,
                blocker_assessment=blocker_assessment,
            ),
            "evidence_signals": signals,
            "confidence": self._confidence(signals),
        }

    # =========================
    # SIGNAL EXTRACTION
    # =========================
    def _signals(
        self,
        text: str,
        keywords: List[str],
        domain: str,
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        moat: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        combined = f"{text} {' '.join(keywords).lower()}"

        market = connector_sources.get("market", {})
        financial = connector_sources.get("financial", {})

        sector = market_gap.get("sector", "general") if isinstance(market_gap, dict) else "general"

        pressure = market_gap.get("strategic_pressure", {}) if isinstance(market_gap, dict) else {}
        pressure_score = pressure.get("score", 0.0) if isinstance(pressure, dict) else 0.0

        formation_type = (
            market_formation.get("formation_type", {}).get("type", "")
            if isinstance(market_formation, dict)
            else ""
        )

        buyer_pull_score = (
            market_formation.get("buyer_pull", {}).get("score", 0.0)
            if isinstance(market_formation, dict)
            else 0.0
        )

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

        timing_pressure = (
            trend_trajectory.get("timing_pressure", {}).get("score", 0.0)
            if isinstance(trend_trajectory, dict)
            else 0.0
        )

        security_terms = [
            "secure",
            "security",
            "cyber",
            "encryption",
            "access control",
            "audit",
            "zero trust",
            "threat",
            "breach",
            "vulnerability",
        ]

        privacy_terms = [
            "privacy",
            "personal data",
            "pii",
            "patient",
            "clinical",
            "health data",
            "customer data",
            "sensitive data",
        ]

        compliance_terms = [
            "compliance",
            "regulatory",
            "regulation",
            "audit",
            "certification",
            "standard",
            "standards",
            "governance",
            "controls",
            "policy",
        ]

        safety_terms = [
            "safety",
            "failure",
            "production failures",
            "mission-critical",
            "critical infrastructure",
            "industrial operations",
            "grid",
            "hospital",
            "battlefield",
            "autonomous",
            "human override",
        ]

        industrial_terms = [
            "industrial",
            "manufacturing",
            "supplier",
            "procurement",
            "logistics",
            "factory",
            "erp",
            "planning-system",
            "planning system",
            "operations",
        ]

        finance_terms = [
            "finance",
            "financial",
            "credit",
            "liquidity",
            "capital",
            "asset manager",
            "portfolio",
            "risk model",
        ]

        healthcare_terms = [
            "healthcare",
            "medical",
            "clinical",
            "hospital",
            "patient",
            "diagnosis",
            "care",
        ]

        defense_terms = [
            "defense",
            "military",
            "battlefield",
            "drone",
            "weapon",
            "mission",
            "surveillance",
            "border",
        ]

        energy_terms = [
            "energy",
            "grid",
            "utility",
            "utilities",
            "power",
            "transmission",
            "infrastructure",
        ]

        data_terms = [
            "data",
            "dataset",
            "historical",
            "benchmark",
            "graph",
            "signals",
            "model",
            "forecast",
            "predict",
            "maps",
        ]

        autonomy_terms = [
            "autonomous",
            "ai-powered",
            "ai-driven",
            "decision-making",
            "recommend",
            "recommends",
            "human override",
        ]

        def count_terms(terms: List[str]) -> int:
            return sum(1 for term in terms if term.lower() in combined)

        sector_regulatory_weight = self._sector_regulatory_weight(
            domain=domain,
            sector=sector,
            finance_terms=count_terms(finance_terms),
            healthcare_terms=count_terms(healthcare_terms),
            defense_terms=count_terms(defense_terms),
            energy_terms=count_terms(energy_terms),
            industrial_terms=count_terms(industrial_terms),
        )

        return {
            "domain": domain,
            "sector": sector,
            "formation_type": formation_type,
            "security_term_count": count_terms(security_terms),
            "privacy_term_count": count_terms(privacy_terms),
            "compliance_term_count": count_terms(compliance_terms),
            "safety_term_count": count_terms(safety_terms),
            "industrial_term_count": count_terms(industrial_terms),
            "finance_term_count": count_terms(finance_terms),
            "healthcare_term_count": count_terms(healthcare_terms),
            "defense_term_count": count_terms(defense_terms),
            "energy_term_count": count_terms(energy_terms),
            "data_term_count": count_terms(data_terms),
            "autonomy_term_count": count_terms(autonomy_terms),
            "sector_regulatory_weight": sector_regulatory_weight,
            "market_volatility": float(market.get("volatility", 0.0) or 0.0),
            "financial_risk": float(financial.get("risk", 0.0) or 0.0),
            "financial_health": float(financial.get("health", 0.0) or 0.0),
            "strategic_pressure_score": float(pressure_score or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "buyer_pull_score": float(buyer_pull_score or 0.0),
            "timing_pressure": float(timing_pressure or 0.0),
            "moat_score": float(moat_score or 0.0),
            "copy_risk_score": float(copy_risk_score or 0.0),
            "buyer_segment_count": len(market_gap.get("buyer_segments", [])) if isinstance(market_gap, dict) else 0,
            "ecosystem_requirement_count": len(market_formation.get("ecosystem_requirements", [])) if isinstance(market_formation, dict) else 0,
        }

    # =========================
    # OUTPUT BUILDERS
    # =========================
    def _risk_profile(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        score = min(
            0.94,
            0.18
            + signals["sector_regulatory_weight"] * 0.20
            + signals["safety_term_count"] * 0.025
            + signals["security_term_count"] * 0.020
            + signals["privacy_term_count"] * 0.030
            + signals["compliance_term_count"] * 0.018
            + signals["market_volatility"] * 0.10
            + signals["financial_risk"] * 0.08
            + signals["autonomy_term_count"] * 0.016
            + max(0.0, 0.45 - signals["moat_score"]) * 0.08
        )

        if score >= 0.70:
            level = "high"
        elif score >= 0.48:
            level = "moderate"
        else:
            level = "low"

        return {
            "level": level,
            "score": round(score, 4),
            "risk_drivers": self._risk_drivers(signals),
        }

    def _regulation_profile(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        score = min(
            0.96,
            0.14
            + signals["sector_regulatory_weight"] * 0.34
            + signals["compliance_term_count"] * 0.035
            + signals["privacy_term_count"] * 0.035
            + signals["safety_term_count"] * 0.025
            + signals["defense_term_count"] * 0.050
            + signals["healthcare_term_count"] * 0.040
            + signals["finance_term_count"] * 0.035
            + signals["energy_term_count"] * 0.030
        )

        if score >= 0.72:
            exposure = "high"
        elif score >= 0.48:
            exposure = "moderate"
        else:
            exposure = "low"

        return {
            "exposure": exposure,
            "score": round(score, 4),
            "regulatory_categories": self._regulatory_categories(signals),
        }

    def _compliance_requirements(self, signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        requirements = [
            {
                "requirement": "audit logging and traceability",
                "why": "Claire decisions and recommendations should be explainable, reviewable, and reproducible.",
                "priority": "high",
            },
            {
                "requirement": "data governance and access controls",
                "why": "The system uses operational and/or strategic business data.",
                "priority": "high",
            },
            {
                "requirement": "model monitoring and performance validation",
                "why": "Predictions and recommendations must be checked against real outcomes.",
                "priority": "high",
            },
        ]

        if signals["privacy_term_count"] > 0 or signals["healthcare_term_count"] > 0:
            requirements.append({
                "requirement": "privacy impact assessment",
                "why": "The opportunity may process sensitive, personal, patient, or customer data.",
                "priority": "high",
            })

        if signals["finance_term_count"] > 0:
            requirements.append({
                "requirement": "financial model governance",
                "why": "Financial risk, credit, liquidity, and capital-related recommendations need documented validation.",
                "priority": "high",
            })

        if signals["healthcare_term_count"] > 0:
            requirements.append({
                "requirement": "clinical safety and health-data compliance review",
                "why": "Healthcare workflows can affect patients, clinicians, capacity, or care delivery.",
                "priority": "high",
            })

        if signals["defense_term_count"] > 0:
            requirements.append({
                "requirement": "secure deployment, export-control, and mission-use review",
                "why": "Defense, mission, autonomy, surveillance, or battlefield contexts require stricter controls.",
                "priority": "high",
            })

        if signals["energy_term_count"] > 0:
            requirements.append({
                "requirement": "critical infrastructure and utility-operations review",
                "why": "Grid, utility, and power systems can carry reliability and infrastructure obligations.",
                "priority": "high",
            })

        if signals["industrial_term_count"] > 0:
            requirements.append({
                "requirement": "industrial operations change-control review",
                "why": "Manufacturing, procurement, ERP, supplier, and planning integrations can affect production decisions.",
                "priority": "medium",
            })

        if signals["autonomy_term_count"] > 0:
            requirements.append({
                "requirement": "human oversight and override policy",
                "why": "AI-assisted or autonomous recommendations should remain reviewable in high-impact workflows.",
                "priority": "high",
            })

        return self._dedupe_dicts(requirements, "requirement")

    def _operational_risks(self, signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        risks = []

        if signals["industrial_term_count"] > 0:
            risks.extend([
                {
                    "risk": "bad forecast or recommendation disrupts production planning",
                    "severity": "medium",
                    "mitigation": "run shadow-mode validation before operational automation",
                },
                {
                    "risk": "ERP or planning-system data quality creates false bottleneck signals",
                    "severity": "medium",
                    "mitigation": "implement source-quality scoring and confidence thresholds",
                },
            ])

        if signals["autonomy_term_count"] > 0:
            risks.append({
                "risk": "over-reliance on AI-generated recommendations",
                "severity": "medium",
                "mitigation": "require human review for high-impact recommendations",
            })

        if signals["healthcare_term_count"] > 0:
            risks.append({
                "risk": "recommendations affect clinical or patient-flow decisions",
                "severity": "high",
                "mitigation": "require clinical validation and workflow signoff",
            })

        if signals["defense_term_count"] > 0:
            risks.append({
                "risk": "mission or surveillance deployment misuse",
                "severity": "high",
                "mitigation": "enforce mission-use constraints and human authorization",
            })

        if signals["energy_term_count"] > 0:
            risks.append({
                "risk": "utility or grid operations dependency",
                "severity": "high",
                "mitigation": "validate in simulation and limited-scope pilots",
            })

        if not risks:
            risks.append({
                "risk": "operational assumptions require validation",
                "severity": "low",
                "mitigation": "validate with pilot users and historical backtesting",
            })

        return risks

    def _security_privacy(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        data_sensitivity = min(
            0.95,
            0.18
            + signals["data_term_count"] * 0.025
            + signals["privacy_term_count"] * 0.08
            + signals["healthcare_term_count"] * 0.05
            + signals["finance_term_count"] * 0.04
            + signals["defense_term_count"] * 0.05
            + signals["industrial_term_count"] * 0.018
        )

        if data_sensitivity >= 0.70:
            level = "high"
        elif data_sensitivity >= 0.45:
            level = "moderate"
        else:
            level = "standard"

        controls = [
            "role-based access control",
            "audit logging",
            "data lineage tracking",
            "source-level permissions",
            "encryption in transit and at rest",
        ]

        if signals["privacy_term_count"] > 0:
            controls.extend([
                "data minimization",
                "privacy impact assessment",
                "retention and deletion policy",
            ])

        if signals["defense_term_count"] > 0:
            controls.extend([
                "secure deployment boundary",
                "restricted access environments",
                "mission-use authorization logs",
            ])

        if signals["industrial_term_count"] > 0:
            controls.extend([
                "ERP integration access scoping",
                "operational data quality monitoring",
            ])

        return {
            "data_sensitivity": {
                "level": level,
                "score": round(data_sensitivity, 4),
            },
            "recommended_controls": sorted(list(dict.fromkeys(controls))),
        }

    def _deployment_constraints(self, signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        constraints = [
            {
                "constraint": "do not automate high-impact decisions until validated",
                "applies_to": "all high-confidence but unvalidated recommendations",
                "priority": "high",
            },
            {
                "constraint": "require explainability for scoring and recommendations",
                "applies_to": "buyer, compliance, and internal review workflows",
                "priority": "high",
            },
        ]

        if signals["industrial_term_count"] > 0:
            constraints.append({
                "constraint": "deploy first in advisory / shadow mode",
                "applies_to": "manufacturing, procurement, ERP, and planning-system integrations",
                "priority": "high",
            })

        if signals["healthcare_term_count"] > 0:
            constraints.append({
                "constraint": "avoid direct clinical decision automation without clinical validation",
                "applies_to": "patient, clinician, capacity, or care-delivery workflows",
                "priority": "high",
            })

        if signals["finance_term_count"] > 0:
            constraints.append({
                "constraint": "separate research signals from regulated financial advice",
                "applies_to": "credit, capital, portfolio, liquidity, and investment workflows",
                "priority": "high",
            })

        if signals["defense_term_count"] > 0:
            constraints.append({
                "constraint": "restrict mission-critical or surveillance use without authorization and controls",
                "applies_to": "defense, autonomy, drone, battlefield, or border contexts",
                "priority": "high",
            })

        if signals["energy_term_count"] > 0:
            constraints.append({
                "constraint": "validate in simulation before live critical infrastructure use",
                "applies_to": "grid, utility, transmission, power, and infrastructure workflows",
                "priority": "high",
            })

        return constraints

    def _blocker_assessment(
        self,
        signals: Dict[str, Any],
        risk_profile: Dict[str, Any],
        regulation_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        blockers = []

        if regulation_profile["exposure"] == "high" and risk_profile["level"] == "high":
            blockers.append("high regulatory exposure plus high operational risk")

        if signals["healthcare_term_count"] > 0 and signals["privacy_term_count"] > 0:
            blockers.append("health or patient data compliance must be resolved before deployment")

        if signals["defense_term_count"] > 0:
            blockers.append("defense/security deployment constraints require review")

        if signals["autonomy_term_count"] > 0 and signals["safety_term_count"] > 1:
            blockers.append("AI autonomy in high-impact workflow requires human override policy")

        if blockers:
            level = "conditional"
        elif risk_profile["level"] == "moderate" or regulation_profile["exposure"] == "moderate":
            level = "manageable"
        else:
            level = "low"

        return {
            "blocker_level": level,
            "blockers": blockers,
            "go_forward_condition": self._go_forward_condition(level, blockers),
        }

    def _mitigation_actions(
        self,
        signals: Dict[str, Any],
        risk_profile: Dict[str, Any],
        regulation_profile: Dict[str, Any],
        blocker_assessment: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        actions = [
            {
                "action": "document model assumptions and decision logic",
                "purpose": "support auditability, validation, and buyer trust",
                "priority": "high",
            },
            {
                "action": "launch in advisory mode before automation",
                "purpose": "reduce operational risk while gathering validation evidence",
                "priority": "high",
            },
            {
                "action": "create confidence thresholds and human-review gates",
                "purpose": "prevent unsupported recommendations from driving high-impact decisions",
                "priority": "high",
            },
            {
                "action": "establish data lineage and source-quality scoring",
                "purpose": "make forecasts and recommendations traceable back to source inputs",
                "priority": "high",
            },
        ]

        if regulation_profile["exposure"] in {"moderate", "high"}:
            actions.append({
                "action": "perform sector-specific compliance review",
                "purpose": "confirm regulatory obligations before buyer deployment",
                "priority": "high",
            })

        if signals["industrial_term_count"] > 0:
            actions.append({
                "action": "pilot with limited operational scope",
                "purpose": "validate supply-chain predictions without disrupting production planning",
                "priority": "high",
            })

        if signals["privacy_term_count"] > 0 or signals["healthcare_term_count"] > 0:
            actions.append({
                "action": "complete privacy and sensitive-data assessment",
                "purpose": "define data minimization, retention, access, and deletion requirements",
                "priority": "high",
            })

        if signals["defense_term_count"] > 0:
            actions.append({
                "action": "define allowed-use and restricted-use policy",
                "purpose": "prevent misuse in surveillance, mission, or security-sensitive settings",
                "priority": "high",
            })

        if blocker_assessment["blocker_level"] == "conditional":
            actions.append({
                "action": "resolve blockers before go-to-market packaging",
                "purpose": "avoid advancing a concept with unresolved compliance or deployment constraints",
                "priority": "critical",
            })

        return self._dedupe_dicts(actions, "action")

    def _validation_requirements(
        self,
        signals: Dict[str, Any],
        compliance_requirements: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        requirements = [
            {
                "validation": "historical backtesting",
                "purpose": "test forecast and recommendation quality against past events",
                "priority": "high",
            },
            {
                "validation": "shadow-mode pilot",
                "purpose": "compare system recommendations with real operator decisions without automating outcomes",
                "priority": "high",
            },
            {
                "validation": "false-positive / false-negative analysis",
                "purpose": "understand failure modes before operational deployment",
                "priority": "high",
            },
            {
                "validation": "user acceptance and workflow-fit testing",
                "purpose": "confirm the system improves decisions in the buyer workflow",
                "priority": "medium",
            },
        ]

        if signals["industrial_term_count"] > 0:
            requirements.append({
                "validation": "ERP and planning-system integration test",
                "purpose": "validate source quality, permissions, latency, and operational safety",
                "priority": "high",
            })

        if signals["healthcare_term_count"] > 0:
            requirements.append({
                "validation": "clinical workflow review",
                "purpose": "confirm no patient-impacting deployment occurs without proper clinical validation",
                "priority": "high",
            })

        if signals["finance_term_count"] > 0:
            requirements.append({
                "validation": "financial model governance review",
                "purpose": "validate risk, credit, liquidity, or capital assumptions",
                "priority": "high",
            })

        if signals["defense_term_count"] > 0:
            requirements.append({
                "validation": "secure mission-use review",
                "purpose": "define allowed deployment conditions and oversight requirements",
                "priority": "high",
            })

        return self._dedupe_dicts(requirements, "validation")

    def _risk_regulation_thesis(
        self,
        signals: Dict[str, Any],
        risk_profile: Dict[str, Any],
        regulation_profile: Dict[str, Any],
        blocker_assessment: Dict[str, Any],
    ) -> str:
        sector = signals.get("sector", "target sector").replace("_", " ")
        return (
            f"{sector} shows {risk_profile.get('level')} risk and "
            f"{regulation_profile.get('exposure')} regulatory exposure. "
            f"Blocker level is {blocker_assessment.get('blocker_level')}. "
            f"The opportunity can move forward if deployment starts in advisory/shadow mode, "
            f"with auditability, data governance, human review gates, and sector-specific compliance review."
        )

    # =========================
    # HELPERS
    # =========================
    def _sector_regulatory_weight(
        self,
        domain: str,
        sector: str,
        finance_terms: int,
        healthcare_terms: int,
        defense_terms: int,
        energy_terms: int,
        industrial_terms: int,
    ) -> float:
        domain = (domain or "").lower()
        sector = (sector or "").lower()

        weight = 0.15

        if domain == "healthcare" or healthcare_terms > 0:
            weight = max(weight, 0.82)

        if domain == "finance" or finance_terms > 0:
            weight = max(weight, 0.70)

        if "defense" in sector or defense_terms > 0:
            weight = max(weight, 0.88)

        if domain == "energy" or "energy" in sector or energy_terms > 0:
            weight = max(weight, 0.68)

        if domain == "industrial" or "industrial" in sector or industrial_terms > 0:
            weight = max(weight, 0.46)

        return weight

    def _risk_drivers(self, signals: Dict[str, Any]) -> List[str]:
        drivers = []

        if signals["sector_regulatory_weight"] >= 0.65:
            drivers.append("regulated or high-impact sector")

        if signals["industrial_term_count"] > 0:
            drivers.append("industrial operations / ERP integration exposure")

        if signals["autonomy_term_count"] > 0:
            drivers.append("AI-assisted recommendations require human oversight")

        if signals["privacy_term_count"] > 0:
            drivers.append("sensitive or personal data exposure")

        if signals["safety_term_count"] > 0:
            drivers.append("operational safety implications")

        if signals["market_volatility"] >= 0.25:
            drivers.append("market volatility")

        if not drivers:
            drivers.append("no major deterministic risk driver surfaced")

        return drivers

    def _regulatory_categories(self, signals: Dict[str, Any]) -> List[str]:
        categories = ["AI governance / model risk", "data governance"]

        if signals["industrial_term_count"] > 0:
            categories.extend(["industrial operations", "ERP / operational-system integration"])

        if signals["privacy_term_count"] > 0:
            categories.append("privacy / sensitive data")

        if signals["finance_term_count"] > 0:
            categories.append("financial model governance")

        if signals["healthcare_term_count"] > 0:
            categories.append("healthcare / clinical workflow")

        if signals["defense_term_count"] > 0:
            categories.extend(["defense / mission use", "export-control / secure deployment"])

        if signals["energy_term_count"] > 0:
            categories.append("critical infrastructure / utility operations")

        if signals["autonomy_term_count"] > 0:
            categories.append("human oversight for AI recommendations")

        return sorted(list(dict.fromkeys(categories)))

    def _go_forward_condition(self, level: str, blockers: List[str]) -> str:
        if level == "conditional":
            return "Proceed only after documented mitigation plan resolves identified blockers."

        if level == "manageable":
            return "Proceed with compliance review, shadow-mode validation, and human-review gates."

        return "Proceed with standard auditability, data governance, and validation controls."

    def _confidence(self, signals: Dict[str, Any]) -> float:
        return round(
            min(
                0.96,
                0.26
                + signals["market_gap_confidence"] * 0.14
                + signals["buyer_pull_score"] * 0.10
                + signals["moat_score"] * 0.10
                + signals["sector_regulatory_weight"] * 0.16
                + min(0.10, signals["compliance_term_count"] * 0.025)
                + min(0.08, signals["data_term_count"] * 0.012)
                + min(0.06, signals["industrial_term_count"] * 0.010),
            ),
            4,
        )

    def _dedupe_dicts(self, items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
        deduped = {}
        for item in items:
            deduped[item.get(key, "")] = item
        return list(deduped.values())
