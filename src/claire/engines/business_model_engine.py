
"""
Business Model Engine — evaluates value capture, pricing logic, commercial motion,
unit economics, buyer economics, and revenue model.

Purpose:
- Activate Claire Stage 17: Business Model + Value Capture
- Convert market gap, trend, formation, moat, and risk context into a commercial strategy
"""

from typing import Any, Dict, List, Optional


class BusinessModelEngine:
    """Deterministic business model and value-capture analyzer."""

    def analyze(
        self,
        text: str,
        domain: str = "general",
        keywords: Optional[List[str]] = None,
        market_gap: Optional[Dict[str, Any]] = None,
        trend_trajectory: Optional[Dict[str, Any]] = None,
        market_formation: Optional[Dict[str, Any]] = None,
        moat: Optional[Dict[str, Any]] = None,
        risk_regulation: Optional[Dict[str, Any]] = None,
        connector_sources: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        text = (text or "").lower()
        keywords = keywords or []
        market_gap = market_gap or {}
        trend_trajectory = trend_trajectory or {}
        market_formation = market_formation or {}
        moat = moat or {}
        risk_regulation = risk_regulation or {}
        connector_sources = connector_sources or {}

        signals = self._signals(
            text=text,
            keywords=keywords,
            domain=domain,
            market_gap=market_gap,
            trend_trajectory=trend_trajectory,
            market_formation=market_formation,
            moat=moat,
            risk_regulation=risk_regulation,
            connector_sources=connector_sources,
        )

        revenue_model = self._revenue_model(signals)
        pricing_model = self._pricing_model(signals, revenue_model)
        value_capture = self._value_capture(signals)
        buyer_roi = self._buyer_roi(signals)
        go_to_market = self._go_to_market(signals, market_gap)
        commercial_risk = self._commercial_risk(signals)
        unit_economics = self._unit_economics(signals, commercial_risk)

        return {
            "status": "success",
            "domain": domain,
            "sector": signals["sector"],
            "revenue_model": revenue_model,
            "pricing_model": pricing_model,
            "value_capture": value_capture,
            "buyer_roi": buyer_roi,
            "go_to_market": go_to_market,
            "unit_economics": unit_economics,
            "commercial_risk": commercial_risk,
            "commercialization_path": self._commercialization_path(signals, commercial_risk),
            "business_model_thesis": self._business_model_thesis(
                signals, revenue_model, value_capture, buyer_roi, commercial_risk
            ),
            "recommended_next_actions": self._recommended_next_actions(signals, value_capture, commercial_risk),
            "evidence_signals": signals,
            "confidence": self._confidence(signals),
        }

    def _signals(
        self,
        text: str,
        keywords: List[str],
        domain: str,
        market_gap: Dict[str, Any],
        trend_trajectory: Dict[str, Any],
        market_formation: Dict[str, Any],
        moat: Dict[str, Any],
        risk_regulation: Dict[str, Any],
        connector_sources: Dict[str, Any],
    ) -> Dict[str, Any]:
        blob = f"{text} {' '.join(keywords).lower()}"

        def count(terms: List[str]) -> int:
            return sum(1 for term in terms if term in blob)

        market = connector_sources.get("market", {})
        financial = connector_sources.get("financial", {})
        sector = market_gap.get("sector", "general")

        return {
            "domain": domain,
            "sector": sector,
            "formation_type": market_formation.get("formation_type", {}).get("type", ""),
            "market_stage": market_formation.get("market_stage", {}).get("stage", ""),
            "pricing_term_count": count(["subscription", "saas", "license", "enterprise", "usage", "api", "platform", "seat", "workflow", "module"]),
            "value_term_count": count(["cost", "savings", "roi", "efficiency", "risk reduction", "resilience", "shortage", "bottleneck", "downtime", "capacity", "production", "forecast", "procurement"]),
            "enterprise_term_count": count(["enterprise", "erp", "planning system", "planning-system", "procurement", "operations", "manufacturing", "supplier", "workflow", "integration", "dashboard"]),
            "scale_term_count": count(["platform", "network", "data", "benchmark", "api", "automation", "operating system", "command layer", "marketplace"]),
            "service_term_count": count(["implementation", "consulting", "professional services", "integration", "pilot", "validation", "deployment"]),
            "procurement_friction_term_count": count(["regulated", "compliance", "security", "audit", "approval", "procurement", "mission-critical", "industrial operations"]),
            "buyer_segment_count": len(market_gap.get("buyer_segments", [])),
            "acquirer_category_count": len(market_gap.get("acquirer_categories", [])),
            "market_growth": float(market.get("growth", 0.0) or 0.0),
            "market_volatility": float(market.get("volatility", 0.0) or 0.0),
            "financial_health": float(financial.get("health", 0.0) or 0.0),
            "financial_risk": float(financial.get("risk", 0.0) or 0.0),
            "market_gap_confidence": float(market_gap.get("confidence", 0.0) or 0.0),
            "buyer_pull_score": float(market_formation.get("buyer_pull", {}).get("score", 0.0) or 0.0),
            "category_creation_score": float(market_formation.get("category_creation_score", {}).get("score", 0.0) or 0.0),
            "timing_pressure": float(trend_trajectory.get("timing_pressure", {}).get("score", 0.0) or 0.0),
            "market_momentum": float(trend_trajectory.get("market_momentum", {}).get("score", 0.0) or 0.0),
            "moat_score": float(moat.get("moat_type", {}).get("moat_score", 0.0) or 0.0),
            "copy_risk_score": float(moat.get("copy_risk", {}).get("score", 0.0) or 0.0),
            "risk_score": float(risk_regulation.get("risk_profile", {}).get("score", 0.0) or 0.0),
            "regulatory_exposure_score": float(risk_regulation.get("regulation_profile", {}).get("score", 0.0) or 0.0),
            "blocker_level": risk_regulation.get("blocker_assessment", {}).get("blocker_level", "unknown"),
        }

    def _revenue_model(self, s: Dict[str, Any]) -> Dict[str, Any]:
        models = []

        def add(model: str, fit: float, why: str):
            models.append({"model": model, "fit_score": round(self._clamp(fit), 4), "why": why})

        if s["enterprise_term_count"] >= 3 or s["sector"] == "industrial_supply_chain":
            add(
                "enterprise_subscription",
                0.42 + s["buyer_pull_score"] * 0.18 + s["enterprise_term_count"] * 0.025 + s["market_gap_confidence"] * 0.12,
                "Recurring operational intelligence sold into enterprise workflows.",
            )

        if s["formation_type"] in {"platform_layer", "infrastructure_layer", "category_expansion"}:
            add(
                "platform_license_plus_modules",
                0.38 + s["category_creation_score"] * 0.18 + s["scale_term_count"] * 0.025 + s["moat_score"] * 0.10,
                "Platform-layer opportunity can monetize core access plus paid modules.",
            )

        if s["service_term_count"] >= 1 or s["blocker_level"] == "conditional":
            add(
                "pilot_to_enterprise_contract",
                0.36 + s["buyer_pull_score"] * 0.14 + s["risk_score"] * 0.08 + s["service_term_count"] * 0.03,
                "Conditional deployment risk favors paid pilots before full platform expansion.",
            )

        add(
            "usage_based_intelligence_api",
            0.26 + s["scale_term_count"] * 0.02 + s["market_momentum"] * 0.10 + s["moat_score"] * 0.08,
            "Later-stage expansion can monetize repeated forecasts and intelligence calls.",
        )

        ranked = sorted(models, key=lambda x: x["fit_score"], reverse=True)
        return {
            "primary_model": ranked[0]["model"],
            "secondary_models": [m["model"] for m in ranked[1:3]],
            "ranked_models": ranked,
            "revenue_logic": self._revenue_logic(ranked[0]["model"]),
        }

    def _pricing_model(self, s: Dict[str, Any], revenue_model: Dict[str, Any]) -> Dict[str, Any]:
        primary = revenue_model.get("primary_model", "")
        if primary == "enterprise_subscription":
            pricing = "annual enterprise subscription"
            metric = "site count, supplier volume, modules, and workflow users"
        elif primary == "platform_license_plus_modules":
            pricing = "base platform license plus paid intelligence modules"
            metric = "module count, operational coverage, and data integrations"
        elif primary == "pilot_to_enterprise_contract":
            pricing = "paid pilot converting to annual platform contract"
            metric = "pilot scope, workflows, data integrations, and validated ROI"
        else:
            pricing = "usage-based API pricing"
            metric = "forecast volume, data calls, and intelligence events"

        score = self._clamp(
            0.28
            + s["buyer_pull_score"] * 0.20
            + s["moat_score"] * 0.18
            + s["category_creation_score"] * 0.14
            + (1 - s["copy_risk_score"]) * 0.10
            - s["risk_score"] * 0.06
        )

        return {
            "recommended_pricing": pricing,
            "pricing_metric": metric,
            "pricing_power": self._level(score),
            "packaging": self._packaging(s),
        }

    def _value_capture(self, s: Dict[str, Any]) -> Dict[str, Any]:
        score = self._clamp(
            0.24
            + s["buyer_pull_score"] * 0.20
            + s["market_gap_confidence"] * 0.16
            + s["category_creation_score"] * 0.12
            + s["moat_score"] * 0.16
            + s["value_term_count"] * 0.02
            + (1 - s["copy_risk_score"]) * 0.08
            - s["risk_score"] * 0.05
        )
        return {
            "strength": self._strength(score),
            "score": round(score, 4),
            "value_drivers": self._value_drivers(s),
            "capture_mechanisms": self._capture_mechanisms(s),
        }

    def _buyer_roi(self, s: Dict[str, Any]) -> Dict[str, Any]:
        score = self._clamp(
            0.22
            + s["buyer_pull_score"] * 0.26
            + s["value_term_count"] * 0.025
            + s["market_gap_confidence"] * 0.14
            + s["timing_pressure"] * 0.10
            + s["enterprise_term_count"] * 0.012
        )
        if score >= 0.78:
            level = "high"
        elif score >= 0.60:
            level = "moderate"
        else:
            level = "unproven"

        return {
            "roi_strength": level,
            "score": round(score, 4),
            "economic_benefits": self._economic_benefits(s),
            "proof_points_needed": self._proof_points_needed(s),
        }

    def _go_to_market(self, s: Dict[str, Any], market_gap: Dict[str, Any]) -> Dict[str, Any]:
        if s["blocker_level"] == "conditional":
            motion = "advisory pilot to enterprise expansion"
        elif s["buyer_pull_score"] >= 0.78 and s["enterprise_term_count"] >= 3:
            motion = "direct enterprise sales with anchor-customer pilots"
        elif s["formation_type"] in {"platform_layer", "category_expansion"}:
            motion = "category wedge with design partners"
        else:
            motion = "focused pilot-led validation"

        return {
            "motion": motion,
            "first_customers": market_gap.get("buyer_segments", [])[:3],
            "sales_cycle": "medium_to_long" if s["blocker_level"] == "conditional" or s["procurement_friction_term_count"] >= 3 else "medium",
            "procurement_complexity": self._burden(
                0.20 + s["enterprise_term_count"] * 0.018 + s["procurement_friction_term_count"] * 0.030 + s["risk_score"] * 0.10 + (0.10 if s["blocker_level"] == "conditional" else 0.0)
            ),
            "entry_offer": "paid advisory pilot with human-review controls and auditability" if s["blocker_level"] == "conditional" else "focused intelligence pilot",
            "expansion_motion": self._expansion_motion(s),
        }

    def _unit_economics(self, s: Dict[str, Any], commercial_risk: Dict[str, Any]) -> Dict[str, Any]:
        gross_margin = self._clamp(0.54 + s["scale_term_count"] * 0.015 + s["moat_score"] * 0.08 - s["service_term_count"] * 0.020 - s["risk_score"] * 0.04)
        implementation = self._clamp(0.22 + s["enterprise_term_count"] * 0.018 + s["service_term_count"] * 0.035 + s["risk_score"] * 0.10 + (0.08 if s["blocker_level"] == "conditional" else 0.0))
        expansion = self._clamp(0.30 + s["buyer_segment_count"] * 0.030 + s["category_creation_score"] * 0.16 + s["market_momentum"] * 0.12 + s["moat_score"] * 0.10)

        return {
            "gross_margin_signal": self._level(gross_margin),
            "implementation_burden": self._burden(implementation),
            "expansion_potential": self._level(expansion),
            "economics_interpretation": (
                f"Gross-margin signal is {self._level(gross_margin)['level']}; "
                f"implementation burden is {self._burden(implementation)['level']}; "
                f"expansion potential is {self._level(expansion)['level']}; "
                f"commercial risk is {commercial_risk.get('level')}."
            ),
        }

    def _commercial_risk(self, s: Dict[str, Any]) -> Dict[str, Any]:
        score = self._clamp(
            0.20
            + s["procurement_friction_term_count"] * 0.018
            + s["risk_score"] * 0.14
            + s["financial_risk"] * 0.10
            + s["market_volatility"] * 0.08
            + (0.10 if s["blocker_level"] == "conditional" else 0.0)
            - s["buyer_pull_score"] * 0.08
            - s["moat_score"] * 0.05
        )

        if score >= 0.62:
            level = "high"
        elif score >= 0.42:
            level = "moderate"
        else:
            level = "low"

        return {
            "level": level,
            "score": round(score, 4),
            "risk_factors": self._commercial_risk_factors(s),
        }

    def _commercialization_path(self, s: Dict[str, Any], commercial_risk: Dict[str, Any]) -> List[Dict[str, Any]]:
        path = [
            {
                "step": 1,
                "name": "Anchor pain validation",
                "objective": "Confirm buyer pain, budget owner, and measurable ROI baseline.",
                "exit_criteria": "At least one high-pain buyer segment validates urgency and economic value.",
            },
            {
                "step": 2,
                "name": "Paid advisory pilot",
                "objective": "Deploy in advisory/shadow mode with traceability and human review.",
                "exit_criteria": "Pilot demonstrates forecast accuracy, workflow fit, and risk controls.",
            },
            {
                "step": 3,
                "name": "Enterprise platform conversion",
                "objective": "Convert validated pilots to annual platform subscription or license.",
                "exit_criteria": "Signed recurring contract with expansion modules identified.",
            },
            {
                "step": 4,
                "name": "Module and data-loop expansion",
                "objective": "Increase value capture through additional workflows, data integrations, and intelligence modules.",
                "exit_criteria": "Expansion revenue tied to proprietary data loops and operational dependency.",
            },
        ]

        if commercial_risk.get("level") == "high":
            path.insert(2, {
                "step": 3,
                "name": "Commercial risk burn-down",
                "objective": "Resolve procurement, compliance, and deployment blockers before full-scale sale.",
                "exit_criteria": "Documented blocker mitigation plan accepted by buyer.",
            })
            for idx, item in enumerate(path, start=1):
                item["step"] = idx

        return path

    def _business_model_thesis(self, s: Dict[str, Any], revenue_model: Dict[str, Any], value_capture: Dict[str, Any], buyer_roi: Dict[str, Any], commercial_risk: Dict[str, Any]) -> str:
        sector = s.get("sector", "target sector").replace("_", " ")
        return (
            f"{sector} supports a {revenue_model.get('primary_model')} business model. "
            f"Value capture is {value_capture.get('strength')} with buyer ROI rated "
            f"{buyer_roi.get('roi_strength')}. Commercial risk is {commercial_risk.get('level')}. "
            f"The strongest path is a paid advisory pilot that converts into an enterprise platform contract "
            f"with expansion through workflow modules, data integrations, and proprietary intelligence loops."
        )

    def _recommended_next_actions(self, s: Dict[str, Any], value_capture: Dict[str, Any], commercial_risk: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = [
            {"action": "define anchor buyer and budget owner", "purpose": "connect the opportunity to a specific economic buyer and procurement path", "priority": "high"},
            {"action": "build ROI model around avoided shortages and reduced production disruption", "purpose": "turn the value thesis into a quantifiable sales case", "priority": "high"},
            {"action": "package advisory pilot with clear success metrics", "purpose": "commercialize while risk/regulation constraints are still being validated", "priority": "high"},
            {"action": "design expansion modules", "purpose": "create a path from initial wedge to platform-level value capture", "priority": "medium"},
        ]

        if s["blocker_level"] == "conditional":
            actions.append({"action": "tie commercial launch to blocker mitigation", "purpose": "avoid selling full automation before human-review and auditability controls are accepted", "priority": "high"})

        if value_capture.get("strength") != "strong":
            actions.append({"action": "strengthen pricing proof", "purpose": "validate willingness-to-pay before assuming strong value capture", "priority": "medium"})

        if commercial_risk.get("level") != "low":
            actions.append({"action": "map procurement friction", "purpose": "identify approval gates, security requirements, and deployment constraints early", "priority": "medium"})

        return actions

    # =========================
    # TEXT HELPERS
    # =========================
    def _revenue_logic(self, primary_model: str) -> str:
        logic = {
            "enterprise_subscription": "Recurring enterprise subscription captures value from ongoing monitoring, forecasting, and workflow dependency.",
            "platform_license_plus_modules": "Base platform license captures core access; modules monetize expanding intelligence layers and operational coverage.",
            "pilot_to_enterprise_contract": "Paid pilot proves ROI and risk controls before converting into recurring enterprise platform revenue.",
            "usage_based_intelligence_api": "Usage-based pricing monetizes repeated intelligence calls, forecasts, and decision events.",
        }
        return logic.get(primary_model, "Business model requires additional validation.")

    def _packaging(self, s: Dict[str, Any]) -> List[Dict[str, Any]]:
        pilot_contents = ["limited data ingestion", "historical backtesting", "advisory recommendations", "ROI baseline"]
        if s["blocker_level"] == "conditional":
            pilot_contents.extend(["human-review gate", "deployment blocker mitigation plan"])

        return [
            {"package": "Pilot", "contents": pilot_contents, "purpose": "prove value and reduce deployment risk"},
            {"package": "Enterprise Platform", "contents": ["continuous monitoring", "workflow dashboard", "risk scoring", "forecasting engine", "audit trail"], "purpose": "recurring operational intelligence subscription"},
            {"package": "Expansion Modules", "contents": ["supplier-risk graph", "shortage forecasting", "bottleneck recommendations", "ERP integrations", "benchmark intelligence"], "purpose": "increase account value and deepen moat"},
        ]

    def _value_drivers(self, s: Dict[str, Any]) -> List[str]:
        drivers = []
        if s["sector"] == "industrial_supply_chain":
            drivers.extend(["avoided production disruption", "reduced component shortage exposure", "supplier-risk visibility", "procurement prioritization", "resilience planning"])
        if s["buyer_pull_score"] >= 0.75:
            drivers.append("strong buyer pain")
        if s["category_creation_score"] >= 0.75:
            drivers.append("platform/category expansion potential")
        if s["moat_score"] >= 0.65:
            drivers.append("defensible workflow and data position")
        return list(dict.fromkeys(drivers)) or ["validated buyer pain"]

    def _capture_mechanisms(self, s: Dict[str, Any]) -> List[str]:
        mechanisms = ["recurring platform access", "paid workflow modules", "implementation and integration fees", "premium intelligence benchmarks"]
        if s["moat_score"] >= 0.65:
            mechanisms.append("embedded workflow dependency")
            mechanisms.append("proprietary data-loop expansion")
        return list(dict.fromkeys(mechanisms))

    def _economic_benefits(self, s: Dict[str, Any]) -> List[str]:
        benefits = ["faster bottleneck detection", "reduced shortage-related disruption", "improved procurement prioritization", "better supplier-risk visibility"]
        if s["timing_pressure"] >= 0.70:
            benefits.append("near-term timing advantage")
        if s["market_momentum"] >= 0.70:
            benefits.append("alignment with accelerating market adoption")
        return benefits

    def _proof_points_needed(self, s: Dict[str, Any]) -> List[str]:
        proof = ["forecast accuracy against historical disruptions", "false-positive and false-negative rates", "buyer workflow adoption", "economic impact from avoided disruption"]
        if s["blocker_level"] == "conditional":
            proof.append("human-review and override control acceptance")
        if s["enterprise_term_count"] >= 3:
            proof.append("ERP / planning-system integration reliability")
        return proof

    def _expansion_motion(self, s: Dict[str, Any]) -> List[str]:
        if s["sector"] == "industrial_supply_chain":
            return ["supplier-risk graph", "shortage forecasting module", "bottleneck recommendation layer", "procurement command dashboard", "ERP / planning-system integrations", "benchmark intelligence network"]
        return ["workflow expansion", "module expansion", "data integration expansion", "platform-wide deployment"]

    def _commercial_risk_factors(self, s: Dict[str, Any]) -> List[str]:
        factors = []
        if s["blocker_level"] == "conditional":
            factors.append("conditional deployment blocker")
        if s["risk_score"] >= 0.45:
            factors.append("operational or compliance risk")
        if s["procurement_friction_term_count"] >= 3:
            factors.append("enterprise procurement friction")
        if s["financial_risk"] >= 0.40:
            factors.append("financial-risk environment")
        return factors or ["no major commercial risk surfaced"]

    # =========================
    # SCORING HELPERS
    # =========================
    def _clamp(self, value: float, low: float = 0.0, high: float = 0.96) -> float:
        return max(low, min(high, value))

    def _strength(self, score: float) -> str:
        if score >= 0.80:
            return "strong"
        if score >= 0.62:
            return "moderate"
        return "emerging"

    def _level(self, score: float) -> Dict[str, Any]:
        if score >= 0.72:
            level = "strong"
        elif score >= 0.52:
            level = "moderate"
        else:
            level = "early"
        return {"level": level, "score": round(self._clamp(score), 4)}

    def _burden(self, score: float) -> Dict[str, Any]:
        score = self._clamp(score)
        if score >= 0.65:
            level = "high"
        elif score >= 0.42:
            level = "moderate"
        else:
            level = "low"
        return {"level": level, "score": round(score, 4)}

    def _confidence(self, s: Dict[str, Any]) -> float:
        return round(
            self._clamp(
                0.24
                + s["market_gap_confidence"] * 0.14
                + s["buyer_pull_score"] * 0.16
                + s["category_creation_score"] * 0.12
                + s["moat_score"] * 0.12
                + s["market_momentum"] * 0.08
                + min(0.06, s["buyer_segment_count"] * 0.012)
                - s["risk_score"] * 0.04
            ),
            4,
        )
