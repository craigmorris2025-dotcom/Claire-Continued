"""Signal extraction workers for connector output."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class SignalExtractionWorker:
    """Convert connector records into structured live intelligence signals."""

    RULES = [
        ("risk_regulation_compliance", ["risk", "regulation", "compliance", "governance", "audit"]),
        ("ai_infrastructure_pressure", ["ai", "compute", "infrastructure", "cloud", "data center"]),
        ("market_competition_pressure", ["market", "pressure", "demand", "competition", "launch"]),
        ("technical_feasibility_moat", ["patent", "innovation", "technical feasibility", "defensibility", "moat"]),
        ("capital_growth_strategy", ["earnings", "growth", "capital", "investor", "strategy"]),
    ]

    def extract(self, connector_payload: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        signals = [self._extract_record(record, context) for record in connector_payload.get("records", [])]
        return {
            "status": "success",
            "worker": "signal_extraction_worker_v1",
            "signal_count": len(signals),
            "signals": signals,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _extract_record(self, record: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        text = " ".join([
            record.get("title", ""),
            record.get("snippet", ""),
            " ".join(record.get("terms", [])),
        ]).lower()
        signal_type = "public_market_signal"
        for label, terms in self.RULES:
            if any(term in text for term in terms):
                signal_type = label
                break
        urgency = "high" if any(term in text for term in ["pressure", "risk", "compliance", "demand"]) else "medium"
        return {
            "signal_id": f"live_{record.get('record_id')}",
            "entity_id": record.get("entity_id"),
            "entity_name": record.get("entity_name"),
            "ticker": record.get("ticker"),
            "market_universe": record.get("market_universe") or context.get("market_universe", "sp500_public"),
            "industry_domain": record.get("industry_domain") or context.get("industry_domain", "cross_sector"),
            "source_family": record.get("source_family"),
            "source_type": record.get("source_type"),
            "source_url": record.get("source_url"),
            "signal_type": signal_type,
            "urgency": urgency,
            "title": record.get("title"),
            "summary": record.get("snippet"),
            "evidence_terms": record.get("terms", []),
            "status": "structured",
            "metadata": record.get("metadata", {}),
        }
