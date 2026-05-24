"""v5.89.7 signal governance skeleton.

This layer governs run-level signals without adding new connectors. Connected
feed metadata continues to use ``claire.feeds``.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from .signal_deduplication import dedupe_signals
from .signal_scoring import SignalGovernanceScorer
from .source_weighting import source_weight


class SignalGovernance:
    version = "v5.89.7_signal_governance_layer"

    def __init__(self) -> None:
        self.scorer = SignalGovernanceScorer()

    def govern(self, raw_signals: Iterable[Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        normalized = [self.normalize(signal, context) for signal in raw_signals]
        deduped = dedupe_signals(normalized)
        for signal in deduped:
            scores = self.scorer.score(signal, context)
            signal["scores"] = scores
            signal["governance_status"] = "accepted" if scores["noise_rejection"] else "noise_rejected"
            signal["safe_for_lifecycle"] = signal["governance_status"] == "accepted" and scores["quality_score"] >= 0.35

        accepted = [signal for signal in deduped if signal.get("safe_for_lifecycle")]
        return {
            "status": "success",
            "version": self.version,
            "raw_signal_count": len(normalized),
            "deduped_signal_count": len(deduped),
            "accepted_signal_count": len(accepted),
            "noise_rejected_count": sum(1 for signal in deduped if signal.get("governance_status") == "noise_rejected"),
            "signals": deduped,
            "summary": self.summary(deduped),
        }

    def normalize(self, raw_signal: Any, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        if isinstance(raw_signal, dict):
            signal = dict(raw_signal)
        else:
            signal = {"raw_input": str(raw_signal or "")}

        raw_input = str(signal.get("raw_input") or signal.get("text") or signal.get("summary") or "")
        source_type = signal.get("source_type") or signal.get("source") or "user_input"
        title = signal.get("title") or self._title(raw_input)
        summary = signal.get("summary") or raw_input

        return {
            "signal_id": signal.get("signal_id") or signal.get("id") or self._stable_id(raw_input, title),
            "source_type": source_type,
            "source_weight": source_weight(source_type),
            "title": title,
            "summary": summary,
            "raw_input": raw_input,
            "created_at": signal.get("created_at") or datetime.now(timezone.utc).isoformat(),
            "metadata": {
                **(signal.get("metadata") or {}),
                "domain": context.get("domain") or context.get("industry_domain"),
                "keywords": context.get("keywords", []),
            },
        }

    def summary(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not signals:
            return {
                "signal_count": 0,
                "accepted_signal_count": 0,
                "average_quality_score": 0.0,
                "average_relevance_score": 0.0,
                "average_momentum_score": 0.0,
                "noise_rejected_count": 0,
            }
        return {
            "signal_count": len(signals),
            "accepted_signal_count": sum(1 for signal in signals if signal.get("safe_for_lifecycle")),
            "average_quality_score": round(sum((signal.get("scores") or {}).get("quality_score", 0.0) for signal in signals) / len(signals), 3),
            "average_relevance_score": round(sum((signal.get("scores") or {}).get("relevance_score", 0.0) for signal in signals) / len(signals), 3),
            "average_momentum_score": round(sum((signal.get("scores") or {}).get("momentum_score", 0.0) for signal in signals) / len(signals), 3),
            "noise_rejected_count": sum(1 for signal in signals if signal.get("governance_status") == "noise_rejected"),
        }

    def _title(self, text: str) -> str:
        words = str(text or "").strip().split()
        return " ".join(words[:10]) if words else "Untitled signal"

    def _stable_id(self, raw_input: str, title: str) -> str:
        digest = hashlib.sha256(f"{raw_input}|{title}".encode("utf-8")).hexdigest()[:12]
        return f"sig_{digest}"
