"""
Feed signal scoring.

v5.47:
- Lightweight deterministic scoring for raw public metadata signals.
- Produces opportunity relevance and signal strength labels without external models.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


class FeedSignalScorer:
    """Score raw feed signals for opportunity relevance and strength."""

    STRONG_TERMS = {
        "ai", "artificial intelligence", "infrastructure", "security", "risk",
        "compliance", "governance", "automation", "supply chain", "shortage",
        "demand", "growth", "investment", "regulation", "capacity", "market",
        "cloud", "data center", "energy", "insurance", "defense", "platform",
    }
    PRESSURE_TERMS = {
        "pressure", "constraint", "gap", "need", "failure", "delay", "cost",
        "loss", "volatility", "withdrawal", "bottleneck", "exposure", "threat",
        "shortfall", "mandate", "requirement", "transition",
    }
    LOW_VALUE_STATUSES = {"blocked", "error", "fetch_failed", "unsupported", "live_disabled"}

    def score(self, raw_signal: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        text = self._text(raw_signal, context)
        words = set(text.split())
        phrase_hits = self._phrase_hits(text, self.STRONG_TERMS)
        pressure_hits = self._phrase_hits(text, self.PRESSURE_TERMS)
        domain_hits = self._domain_hits(text, context)

        status = str(raw_signal.get("status") or "").lower()
        status_penalty = 0.22 if status in self.LOW_VALUE_STATUSES else 0.0
        warning_penalty = min(0.18, 0.045 * len(raw_signal.get("warnings") or []))

        density = min(0.35, (len(words) / 180.0) * 0.35)
        strength_score = 0.18 + density + min(0.28, phrase_hits * 0.045) + min(0.22, pressure_hits * 0.055)
        relevance_score = 0.15 + min(0.30, phrase_hits * 0.042) + min(0.25, pressure_hits * 0.050) + min(0.18, domain_hits * 0.060)

        if raw_signal.get("source_url"):
            strength_score += 0.05
            relevance_score += 0.04

        strength_score = self._clamp(strength_score - status_penalty - warning_penalty)
        relevance_score = self._clamp(relevance_score - status_penalty - warning_penalty)

        return {
            "signal_strength_score": round(strength_score, 3),
            "signal_strength": self._label(strength_score),
            "opportunity_relevance_score": round(relevance_score, 3),
            "opportunity_relevance": self._label(relevance_score),
            "term_hits": phrase_hits,
            "pressure_hits": pressure_hits,
            "domain_hits": domain_hits,
        }

    def _text(self, raw_signal: Dict[str, Any], context: Dict[str, Any]) -> str:
        parts: List[str] = [
            str(raw_signal.get("title") or ""),
            str(raw_signal.get("snippet") or ""),
            str(raw_signal.get("summary") or ""),
            str((raw_signal.get("metadata") or {}).get("signal") or ""),
            str(context.get("industry_domain") or ""),
            str(context.get("objective") or ""),
        ]
        return " ".join(" ".join(parts).lower().replace("/", " ").replace("-", " ").split())

    def _phrase_hits(self, text: str, terms: Iterable[str]) -> int:
        return sum(1 for term in terms if term in text)

    def _domain_hits(self, text: str, context: Dict[str, Any]) -> int:
        domain = str(context.get("industry_domain") or "").replace("_", " ").lower()
        objective = str(context.get("objective") or "").replace("_", " ").lower()
        hits = 0
        if domain and domain != "cross sector" and domain in text:
            hits += 1
        if objective and objective in text:
            hits += 1
        return hits

    def _label(self, score: float) -> str:
        if score >= 0.68:
            return "high"
        if score >= 0.42:
            return "medium"
        return "low"

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value or 0.0)))


__all__ = ["FeedSignalScorer"]
