from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .models import SourceTrustProfile
from .quarantine import SourceQuarantineEngine
from .scorer import AdaptiveSourceTrustScorer
from .store import SourceTrustStore


class DynamicSourceTrustService:
    def __init__(
        self,
        store: SourceTrustStore | None = None,
        scorer: AdaptiveSourceTrustScorer | None = None,
        quarantine: SourceQuarantineEngine | None = None,
    ) -> None:
        self.store = store or SourceTrustStore()
        self.scorer = scorer or AdaptiveSourceTrustScorer()
        self.quarantine = quarantine or SourceQuarantineEngine()

    def get_or_create_profile(self, domain: str) -> SourceTrustProfile:
        domain = self.normalize_domain(domain)
        profile = self.store.load_profile(domain)
        if profile is not None:
            return profile
        profile = self.scorer.new_profile(domain)
        self.store.save_profile(profile)
        return profile

    def record_event(
        self,
        domain: str,
        event_type: str,
        evidence_id: Optional[str] = None,
        confidence: float = 0.0,
        reason: str = "",
    ) -> Dict[str, Any]:
        profile = self.get_or_create_profile(domain)
        event = self.scorer.build_event(
            domain=profile.domain,
            event_type=event_type,
            evidence_id=evidence_id,
            confidence=confidence,
            reason=reason,
        )
        profile = self.scorer.apply_event(profile, event)
        profile = self.quarantine.evaluate(profile)

        self.store.save_event(event)
        self.store.save_profile(profile)
        self.store.audit("source_trust_event_recorded", {
            "profile": profile.to_dict(),
            "event": event.to_dict(),
        })

        return {
            "profile": profile.to_dict(),
            "event": event.to_dict(),
        }

    def weight_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        domain = str(evidence.get("source_domain") or self.domain_from_url(str(evidence.get("source_url", ""))))
        profile = self.get_or_create_profile(domain)
        profile = self.quarantine.evaluate(profile)
        self.store.save_profile(profile)
        result = self.scorer.weight_evidence(evidence, profile)
        return result.to_dict()

    def weight_evidence_batch(self, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        weighted = [self.weight_evidence(item) for item in evidence]
        return {
            "weighted_count": len(weighted),
            "weighted_evidence": weighted,
        }

    def quarantine_source(self, domain: str, reason: str = "Manual quarantine") -> Dict[str, Any]:
        profile = self.get_or_create_profile(domain)
        profile.status = "quarantined"
        if reason not in profile.notes:
            profile.notes.append(reason)
        self.store.save_profile(profile)
        self.store.audit("source_quarantined", profile.to_dict())
        return profile.to_dict()

    def release_source(self, domain: str, reason: str = "Manual release") -> Dict[str, Any]:
        profile = self.get_or_create_profile(domain)
        profile.status = "active"
        if reason not in profile.notes:
            profile.notes.append(reason)
        self.store.save_profile(profile)
        self.store.audit("source_released", profile.to_dict())
        return profile.to_dict()

    def list_profiles(self) -> List[Dict[str, Any]]:
        return self.store.list_profiles()

    def list_events(self, domain: str | None = None, limit: int = 100) -> List[Dict[str, Any]]:
        return self.store.list_events(domain=domain, limit=limit)

    def normalize_domain(self, domain: str) -> str:
        return domain.lower().replace("www.", "").strip()

    def domain_from_url(self, url: str) -> str:
        try:
            return urlparse(url).netloc.lower().replace("www.", "")
        except Exception:
            return ""
