"""Governance scoring for run-level signals."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable


class SignalGovernanceScorer:
    WEAK_SIGNAL_TERMS = {
        "early", "emerging", "weak", "fragmented", "lag", "repricing",
        "withdrawal", "pressure", "gap", "unmet", "shift", "inflection",
    }
    MOMENTUM_TERMS = {
        "rising", "accelerating", "increasing", "surging", "demand",
        "growth", "losses", "adoption", "capacity", "concentration",
    }
    NOISE_TERMS = {
        "random", "misc", "unclear", "rumor", "unsupported", "spam",
    }

    def score(self, signal: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        text = self._text(signal)
        weak_hits = self._hits(text, self.WEAK_SIGNAL_TERMS)
        momentum_hits = self._hits(text, self.MOMENTUM_TERMS)
        relevance_hits = self._hits(text, context.get("keywords", []))
        noise_hits = self._hits(text, self.NOISE_TERMS)

        freshness = self.freshness_score(signal)
        relevance = min(1.0, 0.32 + relevance_hits * 0.08 + weak_hits * 0.04 + momentum_hits * 0.04)
        weak_signal = min(1.0, 0.20 + weak_hits * 0.12)
        momentum = min(1.0, 0.18 + momentum_hits * 0.12)
        agreement = self.agreement_score(signal, context)
        noise = min(1.0, noise_hits * 0.18)
        quality = max(0.0, min(1.0, (freshness * 0.20) + (relevance * 0.32) + (weak_signal * 0.16) + (momentum * 0.16) + (agreement * 0.16) - noise))

        return {
            "freshness_score": round(freshness, 3),
            "relevance_score": round(relevance, 3),
            "weak_signal_score": round(weak_signal, 3),
            "momentum_score": round(momentum, 3),
            "agreement_score": round(agreement, 3),
            "noise_score": round(noise, 3),
            "quality_score": round(quality, 3),
            "quality_label": self._label(quality),
            "noise_rejection": noise < 0.34,
            "hits": {
                "weak_signal_terms": weak_hits,
                "momentum_terms": momentum_hits,
                "relevance_terms": relevance_hits,
                "noise_terms": noise_hits,
            },
        }

    def freshness_score(self, signal: Dict[str, Any]) -> float:
        created_at = signal.get("created_at")
        if not created_at:
            return 0.50
        try:
            parsed = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
        except ValueError:
            return 0.45
        age_days = max(0, (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).days)
        return max(0.10, 1.0 - min(age_days, 90) / 100.0)

    def agreement_score(self, signal: Dict[str, Any], context: Dict[str, Any]) -> float:
        domain = str(context.get("domain") or context.get("industry_domain") or "").replace("_", " ").lower()
        text = self._text(signal)
        if domain and domain in text:
            return 0.70
        return 0.50

    def _text(self, signal: Dict[str, Any]) -> str:
        return " ".join(str(value or "") for value in [
            signal.get("title"),
            signal.get("summary"),
            signal.get("raw_input"),
        ]).lower()

    def _hits(self, text: str, terms: Iterable[Any]) -> int:
        return sum(1 for term in terms if str(term).lower().replace("_", " ") in text)

    def _label(self, score: float) -> str:
        if score >= 0.72:
            return "strong"
        if score >= 0.48:
            return "usable"
        return "weak"
