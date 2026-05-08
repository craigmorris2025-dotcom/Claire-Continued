from __future__ import annotations

import hashlib
from typing import Dict

from .defaults import DEFAULT_SOURCE_BASE_SCORES
from .models import EvidenceWeightResult, SourceTrustEvent, SourceTrustProfile
from .models import utc_now


class AdaptiveSourceTrustScorer:
    POSITIVE_TYPES = {"confirmed", "matched_prediction", "high_quality", "authoritative"}
    NEGATIVE_TYPES = {"false", "misleading", "low_quality", "failed_validation"}
    CONTRADICTION_TYPES = {"contradicted", "conflicting"}
    CORRECTION_TYPES = {"corrected", "retracted"}

    def base_score_for_domain(self, domain: str) -> float:
        domain = domain.lower().replace("www.", "")
        if domain in DEFAULT_SOURCE_BASE_SCORES:
            return DEFAULT_SOURCE_BASE_SCORES[domain]
        for known, score in DEFAULT_SOURCE_BASE_SCORES.items():
            if domain.endswith("." + known):
                return score
        return 0.55

    def new_profile(self, domain: str) -> SourceTrustProfile:
        base = self.base_score_for_domain(domain)
        return SourceTrustProfile(domain=domain, base_score=base, adaptive_score=base)

    def build_event(
        self,
        domain: str,
        event_type: str,
        evidence_id: str | None = None,
        confidence: float = 0.0,
        reason: str = "",
    ) -> SourceTrustEvent:
        impact = self.impact_for_event(event_type, confidence)
        event_id = "trust_event_" + hashlib.sha256(
            f"{domain}|{event_type}|{evidence_id}|{utc_now()}".encode("utf-8")
        ).hexdigest()[:16]
        return SourceTrustEvent(
            event_id=event_id,
            domain=domain,
            event_type=event_type,
            evidence_id=evidence_id,
            confidence=max(0.0, min(1.0, confidence)),
            impact=impact,
            reason=reason,
        )

    def apply_event(self, profile: SourceTrustProfile, event: SourceTrustEvent) -> SourceTrustProfile:
        profile.evidence_count += 1
        profile.last_seen_at = utc_now()

        if event.event_type in self.POSITIVE_TYPES:
            profile.positive_events += 1
        elif event.event_type in self.NEGATIVE_TYPES:
            profile.negative_events += 1
        elif event.event_type in self.CONTRADICTION_TYPES:
            profile.contradiction_events += 1
        elif event.event_type in self.CORRECTION_TYPES:
            profile.correction_events += 1

        profile.adaptive_score = round(max(0.0, min(1.0, profile.adaptive_score + event.impact)), 4)
        return profile

    def impact_for_event(self, event_type: str, confidence: float) -> float:
        confidence = max(0.0, min(1.0, confidence))
        if event_type in self.POSITIVE_TYPES:
            return round(0.015 + 0.025 * confidence, 4)
        if event_type in self.NEGATIVE_TYPES:
            return round(-0.04 - 0.06 * confidence, 4)
        if event_type in self.CONTRADICTION_TYPES:
            return round(-0.02 - 0.03 * confidence, 4)
        if event_type in self.CORRECTION_TYPES:
            return round(-0.03 - 0.05 * confidence, 4)
        return 0.0

    def weight_evidence(self, evidence: Dict[str, object], profile: SourceTrustProfile) -> EvidenceWeightResult:
        evidence_id = str(evidence.get("evidence_id", "unknown"))
        original_confidence = float(evidence.get("confidence", 0.0))
        source_reliability = float(evidence.get("source_reliability", profile.base_score))
        adaptive = profile.adaptive_score

        if profile.status == "quarantined":
            weighted = min(original_confidence, 0.15)
            reason = "Source is quarantined; confidence capped."
        elif profile.status == "degraded":
            weighted = original_confidence * 0.65
            reason = "Source is degraded; confidence reduced."
        else:
            weighted = original_confidence * 0.5 + source_reliability * 0.25 + adaptive * 0.25
            reason = "Weighted by original confidence, static reliability, and adaptive trust."

        return EvidenceWeightResult(
            evidence_id=evidence_id,
            domain=profile.domain,
            original_confidence=round(original_confidence, 4),
            source_reliability=round(source_reliability, 4),
            adaptive_source_score=round(adaptive, 4),
            weighted_confidence=round(max(0.0, min(1.0, weighted)), 4),
            source_status=profile.status,
            weighting_reason=reason,
        )
