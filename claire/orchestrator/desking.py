"""
Desking — Distribution, routing, and output allocation.
Determines how results are distributed to downstream consumers.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger("claire.orchestrator.desking")


class Desking:
    """Routes pipeline outputs to appropriate channels and formats."""

    CHANNELS = {
        "executive_summary": {
            "required_scores": ["decision_score", "breakthrough_score", "portfolio_score"],
            "format": "summary",
            "priority": "high",
        },
        "technical_detail": {
            "required_scores": ["ingestion_score", "semantic_score", "engineering_score"],
            "format": "detailed",
            "priority": "medium",
        },
        "acquirer_report": {
            "required_scores": ["acquirer_matching_score", "synergy_score", "deal_score"],
            "format": "report",
            "priority": "high",
        },
        "compliance_audit": {
            "required_scores": ["compliance_score", "risk_score"],
            "format": "audit",
            "priority": "medium",
        },
    }

    def distribute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        distributions = []
        for channel_name, config in self.CHANNELS.items():
            available_scores = {
                k: context.get(k, 0)
                for k in config["required_scores"]
            }
            readiness = sum(1 for v in available_scores.values() if v > 0) / max(len(available_scores), 1)

            distributions.append({
                "channel": channel_name,
                "format": config["format"],
                "priority": config["priority"],
                "readiness": round(readiness, 2),
                "scores": available_scores,
                "ready": readiness >= 0.5,
            })

        context["desking_distributions"] = distributions
        ready_count = sum(1 for d in distributions if d["ready"])
        logger.info(f"Desking: {ready_count}/{len(distributions)} channels ready")
        return context
