"""
Connected opportunity enricher.

v5.49:
- Uses normalized feed signals to enrich public opportunity cards and protected
  launch prompts.
- Does not expose internal discovery construction.
"""

from __future__ import annotations

from typing import Any, Dict, List

from runtime_core.enrichment.enrichment_contracts import OpportunityEnrichment


class ConnectedOpportunityEnricher:
    """Match normalized feed signals to opportunity candidates."""

    def enrich_candidate(
        self,
        candidate: Dict[str, Any],
        normalized_signals: List[Dict[str, Any]] | None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        candidate = dict(candidate or {})
        enrichment = self.enrichment(candidate, normalized_signals or [], context or {})
        candidate["connected_enrichment"] = enrichment.to_dict()
        candidate["selection_score"] = self.adjust_selection_score(candidate.get("selection_score"), enrichment)
        candidate["confidence_label"] = self.adjust_confidence(candidate.get("confidence_label"), enrichment)
        candidate["raw_input"] = self.enrich_raw_input(candidate.get("raw_input", ""), enrichment)
        return candidate

    def enrichment(
        self,
        candidate: Dict[str, Any],
        normalized_signals: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> OpportunityEnrichment:
        matched = self.match_signals(candidate, normalized_signals, context)
        safe = [signal for signal in matched if signal.get("safe_to_enrich")]
        top_types = self._top_values(safe, "signal_type")
        source_categories = self._top_values(safe, "source_category")
        score = self._score(safe)
        relevance = self._label(score)
        thesis = self._thesis(candidate, safe, top_types)

        return OpportunityEnrichment(
            status="enriched" if safe else "no_connected_match",
            enrichment_mode=context.get("execution_mode") or candidate.get("execution_mode") or "deterministic",
            signal_count=len(normalized_signals),
            matched_signal_count=len(safe),
            top_signal_types=top_types,
            source_categories=source_categories,
            opportunity_relevance=relevance,
            enrichment_score=score,
            connected_thesis=thesis,
            timing_window=self._timing_window(safe),
            safe_to_enrich=bool(safe),
            supporting_signals=[self._public_signal(signal) for signal in safe[:5]],
        )

    def match_signals(
        self,
        candidate: Dict[str, Any],
        normalized_signals: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        candidate_text = self._candidate_text(candidate, context)
        universe = candidate.get("market_universe") or context.get("market_universe")
        domain = candidate.get("industry_domain") or context.get("industry_domain")
        matches: List[Dict[str, Any]] = []

        for signal in normalized_signals:
            if signal.get("governance_status") in {"block", "review"}:
                continue
            score = 0.0
            if universe and signal.get("market_universe") == universe:
                score += 0.30
            if domain and signal.get("industry_domain") == domain:
                score += 0.25
            signal_text = self._signal_text(signal)
            score += min(0.25, self._term_overlap(candidate_text, signal_text) * 0.035)
            score += float(signal.get("opportunity_relevance_score") or 0.0) * 0.12
            score += float(signal.get("signal_strength_score") or 0.0) * 0.08
            if score >= 0.28:
                enriched = dict(signal)
                enriched["_match_score"] = round(min(1.0, score), 3)
                matches.append(enriched)

        return sorted(matches, key=lambda item: item.get("_match_score", 0.0), reverse=True)

    def adjust_selection_score(self, current: Any, enrichment: OpportunityEnrichment) -> float:
        base = float(current or 0.0)
        if not enrichment.safe_to_enrich:
            return round(base, 3)
        boost = min(0.08, enrichment.enrichment_score * 0.08)
        return round(min(0.97, base + boost), 3)

    def adjust_confidence(self, current: Any, enrichment: OpportunityEnrichment) -> str:
        if enrichment.enrichment_score >= 0.72:
            return "high_connected"
        if enrichment.enrichment_score >= 0.45:
            return "medium_connected"
        return str(current or "medium")

    def enrich_raw_input(self, raw_input: str, enrichment: OpportunityEnrichment) -> str:
        if not enrichment.safe_to_enrich:
            return raw_input
        signal_lines = []
        for signal in enrichment.supporting_signals[:3]:
            signal_lines.append(
                f"- {signal.get('signal_type')} / {signal.get('opportunity_relevance')} relevance: {signal.get('title')}"
            )
        return (
            f"{raw_input} "
            f"Connected enrichment context: {enrichment.connected_thesis} "
            f"Supporting normalized public signals: {' '.join(signal_lines)} "
            f"Use connected signals as public-market context only; preserve deterministic reasoning and governance boundaries."
        )

    def _score(self, signals: List[Dict[str, Any]]) -> float:
        if not signals:
            return 0.0
        values = []
        for signal in signals:
            rel = float(signal.get("opportunity_relevance_score") or 0.0)
            strength = float(signal.get("signal_strength_score") or 0.0)
            match = float(signal.get("_match_score") or 0.0)
            values.append(rel * 0.45 + strength * 0.30 + match * 0.25)
        return round(sum(values) / len(values), 3)

    def _label(self, score: float) -> str:
        if score >= 0.68:
            return "high"
        if score >= 0.42:
            return "medium"
        return "low"

    def _timing_window(self, signals: List[Dict[str, Any]]) -> str:
        if any(signal.get("signal_type") in {"market_pressure", "ai_infrastructure"} for signal in signals):
            return "near_term"
        if signals:
            return "watchlist"
        return "unconfirmed"

    def _thesis(self, candidate: Dict[str, Any], signals: List[Dict[str, Any]], top_types: List[str]) -> str:
        if not signals:
            return "No safe normalized connected signal currently strengthens this opportunity."
        direction = candidate.get("opportunity_direction") or candidate.get("title") or "this opportunity"
        types = ", ".join(top_types[:3]) or "public market"
        return (
            f"Safe normalized public signals indicate {types} pressure around {direction}. "
            f"This strengthens the candidate as a connected opportunity for further Claire evaluation."
        )

    def _public_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "signal_id": signal.get("signal_id"),
            "title": signal.get("title"),
            "signal_type": signal.get("signal_type"),
            "market_universe": signal.get("market_universe"),
            "industry_domain": signal.get("industry_domain"),
            "source_category": signal.get("source_category"),
            "governance_status": signal.get("governance_status"),
            "opportunity_relevance": signal.get("opportunity_relevance"),
            "opportunity_relevance_score": signal.get("opportunity_relevance_score"),
            "signal_strength": signal.get("signal_strength"),
            "signal_strength_score": signal.get("signal_strength_score"),
            "safe_to_enrich": signal.get("safe_to_enrich"),
        }

    def _top_values(self, signals: List[Dict[str, Any]], key: str) -> List[str]:
        counts: Dict[str, int] = {}
        for signal in signals:
            value = str(signal.get(key) or "")
            if value:
                counts[value] = counts.get(value, 0) + 1
        return [value for value, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True)]

    def _candidate_text(self, candidate: Dict[str, Any], context: Dict[str, Any]) -> str:
        parts = [
            candidate.get("title"),
            candidate.get("opportunity_direction"),
            candidate.get("market_gap"),
            candidate.get("needed_solution"),
            candidate.get("why_now"),
            context.get("signal"),
            context.get("industry_domain"),
            context.get("objective"),
        ]
        return self._normalize(" ".join(str(part or "") for part in parts))

    def _signal_text(self, signal: Dict[str, Any]) -> str:
        parts = [
            signal.get("title"),
            signal.get("summary"),
            signal.get("signal_type"),
            signal.get("industry_domain"),
            signal.get("source_category"),
        ]
        return self._normalize(" ".join(str(part or "") for part in parts))

    def _term_overlap(self, left: str, right: str) -> int:
        stop = {"the", "and", "for", "with", "from", "this", "that", "into", "signal"}
        left_terms = {term for term in left.split() if len(term) > 3 and term not in stop}
        right_terms = {term for term in right.split() if len(term) > 3 and term not in stop}
        return len(left_terms & right_terms)

    def _normalize(self, text: str) -> str:
        chars = []
        for ch in (text or "").lower():
            chars.append(ch if ch.isalnum() else " ")
        return " ".join("".join(chars).split())


__all__ = ["ConnectedOpportunityEnricher"]
