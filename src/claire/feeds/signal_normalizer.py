"""
Feed signal normalizer.

v5.47:
- Transforms raw public metadata signals into normalized Claire opportunity signals.
- Adds signal type, strength, relevance, governance status, and enrichability.
"""

from __future__ import annotations

from typing import Any, Dict, List

from claire.feeds.signal_contracts import NormalizedFeedSignal
from claire.feeds.signal_scoring import FeedSignalScorer


class FeedSignalNormalizer:
    """Normalize raw feed output into Claire-ready opportunity intelligence."""

    def __init__(self) -> None:
        self.scorer = FeedSignalScorer()

    def normalize_many(
        self,
        signals: List[Dict[str, Any]] | None,
        context: Dict[str, Any] | None = None,
        activation_decision: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        context = context or {}
        activation_decision = activation_decision or {}
        normalized = [
            self.normalize(signal, context=context, activation_decision=activation_decision).to_dict()
            for signal in (signals or [])
        ]
        return {
            "status": "success",
            "normalized_count": len(normalized),
            "signals": normalized,
            "summary": self.summary(normalized),
        }

    def normalize(
        self,
        raw_signal: Dict[str, Any],
        context: Dict[str, Any] | None = None,
        activation_decision: Dict[str, Any] | None = None,
    ) -> NormalizedFeedSignal:
        context = context or {}
        activation_decision = activation_decision or {}
        metadata = raw_signal.get("metadata") or {}
        market_universe = raw_signal.get("market_universe") or context.get("market_universe") or "custom_universe"
        industry_domain = metadata.get("industry_domain") or context.get("industry_domain") or "cross_sector"
        source_category = raw_signal.get("source_category") or activation_decision.get("source_category") or "unknown_source"
        governance_status = activation_decision.get("decision") or "unknown"
        scores = self.scorer.score(raw_signal, {**context, "industry_domain": industry_domain})
        signal_type = self.classify_signal_type(raw_signal, industry_domain=industry_domain)
        safe_to_enrich = self.safe_to_enrich(raw_signal, activation_decision, scores)

        return NormalizedFeedSignal.create(
            raw_signal_id=raw_signal.get("signal_id", ""),
            market_universe=market_universe,
            industry_domain=industry_domain,
            source_category=source_category,
            governance_status=governance_status,
            signal_type=signal_type,
            signal_strength=scores["signal_strength"],
            signal_strength_score=scores["signal_strength_score"],
            opportunity_relevance=scores["opportunity_relevance"],
            opportunity_relevance_score=scores["opportunity_relevance_score"],
            safe_to_enrich=safe_to_enrich,
            title=raw_signal.get("title") or "Untitled public signal",
            summary=self._summary(raw_signal, signal_type),
            source_url=raw_signal.get("source_url", ""),
            warnings=raw_signal.get("warnings") or [],
            evidence={
                "raw_status": raw_signal.get("status"),
                "term_hits": scores.get("term_hits", 0),
                "pressure_hits": scores.get("pressure_hits", 0),
                "domain_hits": scores.get("domain_hits", 0),
            },
            metadata={
                "raw_signal": raw_signal,
                "context": context,
                "activation_decision": activation_decision,
            },
        )

    def classify_signal_type(self, raw_signal: Dict[str, Any], industry_domain: str = "cross_sector") -> str:
        text = " ".join([
            str(raw_signal.get("title") or ""),
            str(raw_signal.get("snippet") or ""),
            str((raw_signal.get("metadata") or {}).get("signal") or ""),
            industry_domain or "",
        ]).lower()
        categories = [
            ("governance", ["governance", "compliance", "regulation", "risk", "audit"]),
            ("ai_infrastructure", ["ai", "artificial intelligence", "data center", "cloud", "compute", "infrastructure"]),
            ("market_pressure", ["pressure", "shortage", "bottleneck", "demand", "volatility", "cost", "capacity"]),
            ("security_defense", ["security", "defense", "mission", "threat", "surveillance"]),
            ("financial_market_signal", ["financial", "capital", "liquidity", "portfolio", "earnings", "margin"]),
            ("energy_infrastructure", ["energy", "grid", "transmission", "utility", "power"]),
        ]
        for label, terms in categories:
            if any(term in text for term in terms):
                return label
        if raw_signal.get("signal_type"):
            return str(raw_signal.get("signal_type"))
        return "public_market_metadata"

    def safe_to_enrich(
        self,
        raw_signal: Dict[str, Any],
        activation_decision: Dict[str, Any],
        scores: Dict[str, Any],
    ) -> bool:
        if activation_decision.get("decision") in {"block", "review"}:
            return False
        if raw_signal.get("status") not in {"success", "ready", "metadata_only"}:
            return False
        if raw_signal.get("warnings"):
            return False
        return scores.get("opportunity_relevance_score", 0.0) >= 0.35

    def summary(self, normalized: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not normalized:
            return {
                "signal_count": 0,
                "safe_to_enrich_count": 0,
                "top_signal_type": "none",
                "average_strength_score": 0.0,
                "average_relevance_score": 0.0,
            }
        type_counts: Dict[str, int] = {}
        for signal in normalized:
            key = signal.get("signal_type") or "unknown"
            type_counts[key] = type_counts.get(key, 0) + 1
        top_type = sorted(type_counts.items(), key=lambda item: item[1], reverse=True)[0][0]
        return {
            "signal_count": len(normalized),
            "safe_to_enrich_count": sum(1 for signal in normalized if signal.get("safe_to_enrich")),
            "top_signal_type": top_type,
            "average_strength_score": round(sum(signal.get("signal_strength_score", 0.0) for signal in normalized) / len(normalized), 3),
            "average_relevance_score": round(sum(signal.get("opportunity_relevance_score", 0.0) for signal in normalized) / len(normalized), 3),
        }

    def _summary(self, raw_signal: Dict[str, Any], signal_type: str) -> str:
        snippet = (raw_signal.get("snippet") or "").strip()
        title = (raw_signal.get("title") or "Public metadata signal").strip()
        base = snippet or title
        if len(base) > 280:
            base = base[:277].rstrip() + "..."
        return f"{signal_type.replace('_', ' ').title()}: {base}"


__all__ = ["FeedSignalNormalizer"]
