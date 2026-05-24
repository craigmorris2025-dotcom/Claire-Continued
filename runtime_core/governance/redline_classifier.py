"""
Redline Classifier — defense classification and hard-stop detection.

v5.42:
- Allows lawful opportunity discovery.
- Logs and routes legal/compliance-sensitive issues.
- Blocks only hard redline autonomous weaponization or clearly prohibited categories.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import re

from runtime_core.governance.defense_risk_taxonomy import DefenseRiskTaxonomy
from runtime_core.governance.governance_decision import GovernanceDecision


class RedlineClassifier:
    """Classify defense/legal risk without suppressing lawful opportunity pathways."""

    def __init__(self) -> None:
        self.taxonomy = DefenseRiskTaxonomy()
        self.categories = self.taxonomy.categories()

    def classify(self, text: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        text = text or ""
        context = context or {}
        lowered = text.lower()

        matches = {
            category: self._matched_terms(lowered, terms)
            for category, terms in self.categories.items()
        }

        if matches["autonomous_weaponization"]:
            return GovernanceDecision.create(
                decision="block",
                severity="critical",
                defense_classification="autonomous_weaponization",
                legal_status="blocked_hard_stop",
                reason_summary="Autonomous weaponization hard-stop terms were detected. Claire should not continue this pathway.",
                triggered_terms=matches["autonomous_weaponization"],
                recommended_action="block_and_log",
                details={"matches": matches, "context": context},
            ).to_dict()

        if self._export_or_classified_risk(lowered) or matches["sensitive_defense_component"]:
            triggered = matches["sensitive_defense_component"] + self._matched_terms(lowered, [
                "export controlled", "itar", "classified", "classified-adjacent", "controlled technical data"
            ])
            return GovernanceDecision.create(
                decision="review",
                severity="high",
                defense_classification="sensitive_defense_component",
                legal_status="review_required",
                reason_summary="Sensitive defense, export-control, classified-adjacent, or platform-component indicators were detected. Preserve the opportunity pathway but require legal/compliance review before connected ingestion or detailed technical output.",
                triggered_terms=triggered,
                recommended_action="log_and_require_review",
                details={"matches": matches, "context": context},
            ).to_dict()

        if matches["dual_use_defense_adjacent"]:
            return GovernanceDecision.create(
                decision="allow_with_log",
                severity="medium",
                defense_classification="dual_use_defense_adjacent",
                legal_status="logged",
                reason_summary="Dual-use or defense-adjacent indicators were detected. Claire may continue with logging and bounded outputs.",
                triggered_terms=matches["dual_use_defense_adjacent"],
                recommended_action="continue_with_audit_log",
                details={"matches": matches, "context": context},
            ).to_dict()

        if matches["normal_defense_government"] or self._defense_context(lowered, context):
            return GovernanceDecision.create(
                decision="allow",
                severity="low",
                defense_classification="normal_defense_government",
                legal_status="clear_logged",
                reason_summary="Normal defense/government opportunity indicators were detected. This is allowed and should not interrupt opportunity discovery.",
                triggered_terms=matches["normal_defense_government"],
                recommended_action="continue",
                details={"matches": matches, "context": context},
            ).to_dict()

        return GovernanceDecision.create(
            decision="allow",
            severity="low",
            defense_classification="general_commercial_or_unknown",
            legal_status="clear",
            reason_summary="No defense redline indicators detected. Continue normal opportunity discovery.",
            triggered_terms=[],
            recommended_action="continue",
            details={"matches": matches, "context": context},
        ).to_dict()

    def _matched_terms(self, lowered: str, terms: List[str]) -> List[str]:
        found: List[str] = []
        for term in terms:
            pattern = r"\b" + re.escape(term.lower()) + r"\b"
            if re.search(pattern, lowered):
                found.append(term)
        return found

    def _export_or_classified_risk(self, lowered: str) -> bool:
        indicators = [
            "itar", "export controlled", "export-control", "controlled technical data",
            "classified", "classified-adjacent", "secret clearance", "top secret",
        ]
        return any(indicator in lowered for indicator in indicators)

    def _defense_context(self, lowered: str, context: Dict[str, Any]) -> bool:
        context_values = " ".join(str(v).lower() for v in context.values() if v is not None)
        combined = lowered + " " + context_values
        return any(term in combined for term in [
            "defense", "government", "federal", "mission", "military", "dod",
            "critical infrastructure", "national security"
        ])
