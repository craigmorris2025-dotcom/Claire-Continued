"""
Compliance Engine — evaluates regulatory compliance, governance risk, and clearance requirements.
Consumes market connector data for regulatory posture and patent data for litigation risk.
"""
from typing import Any, Dict, List
from claire.engines.base import BaseEngine


class ComplianceEngine(BaseEngine):
    """Domain engine: compliance — regulatory and governance assessment."""

    KEYWORDS = {"audit", "cfius", "compliance", "governance", "itar", "legal",
                "policy", "regulatory", "sec", "clearance", "authorization",
                "certification", "accreditation"}

    def get_key(self) -> str:
        return "compliance"

    def get_phase(self) -> str:
        return "portfolio_compliance"

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("raw_input", "").lower()

        regulated_signals = {"itar", "cfius", "sec", "fdic", "hipaa", "fedramp",
                           "classified", "export control", "ear", "ofac",
                           "sanctions", "embargo", "controlled unclassified"}
        clean_signals = {"compliant", "certified", "cleared", "authorized",
                       "approved", "licensed", "accredited", "audited",
                       "soc 2", "iso 27001", "cmmc", "fedramp authorized"}
        risk_signals = {"violation", "fine", "penalty", "investigation",
                       "enforcement", "consent decree", "debarment",
                       "false claims", "qui tam"}

        regulated = self._text_signal(text, regulated_signals)
        clean = self._text_signal(text, clean_signals)
        risk = self._text_signal(text, risk_signals)

        base_risk = 0.55  # neutral baseline

        # Market connector: regulatory posture
        market = self._get_market_data(context)
        regulatory_adj = 0.0
        regulatory_flags: List[str] = []
        if market:
            reg = market.get("regulatory_posture", {})
            if isinstance(reg, dict):
                if reg.get("itar_controlled"):
                    regulatory_adj -= 0.04
                    regulatory_flags.append("ITAR controlled")
                cfius = reg.get("cfius_review", "")
                if cfius == "mandatory":
                    regulatory_adj -= 0.05
                    regulatory_flags.append("CFIUS mandatory")
                elif cfius == "voluntary":
                    regulatory_adj -= 0.02
                    regulatory_flags.append("CFIUS voluntary")
                export_controls = reg.get("export_controls", "")
                if export_controls == "strict":
                    regulatory_adj -= 0.03
                    regulatory_flags.append("Strict export controls")

        # Patent connector: litigation rate
        patent = self._get_patent_data(context)
        litigation_adj = 0.0
        if patent:
            lit_rate = patent.get("litigation_rate", 0)
            if lit_rate > 0.06:
                litigation_adj = -0.06
                regulatory_flags.append("High patent litigation rate")
            elif lit_rate < 0.02:
                litigation_adj = 0.03

        # Detect specific compliance flags in text
        flags_in_text = [s for s in regulated_signals if s in text]

        score = (base_risk + clean * 0.25 - regulated * 0.08 -
                 risk * 0.12 + regulatory_adj + litigation_adj)

        context["compliance"] = {
            "regulatory_exposure": round(regulated, 3),
            "compliance_posture": round(clean, 3),
            "risk_signals": round(risk, 3),
            "overall_score": round(self._clamp(score), 4),
            "flags": flags_in_text,
            "regulatory_flags": regulatory_flags,
        }
        return self._score_with_detail(context, score, {
            "regulatory_exposure": round(regulated, 3),
            "compliance_posture": round(clean, 3),
            "risk_signals": round(risk, 3),
            "regulatory_adj": round(regulatory_adj, 3),
            "litigation_adj": round(litigation_adj, 3),
            "flags": flags_in_text + regulatory_flags,
        })
