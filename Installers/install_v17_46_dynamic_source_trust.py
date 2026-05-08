# Claire Syntalion Installer
# v17.46 Dynamic Source Trust + Reputation Intelligence
#
# Adds adaptive trust around internet evidence:
# - source trust profiles
# - reliability history
# - trust updates from evidence outcomes
# - source quarantine
# - domain reputation scoring
# - evidence weighting refinement
# - CLI and FastAPI routes
#
# Place this file in Claire project root and run:
#
#     python install_v17_46_dynamic_source_trust.py
#
# Then test:
#
#     python -m pytest tests/dynamic_source_trust -q

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CLAIRE = SRC / "claire"
LAYER = CLAIRE / "dynamic_source_trust"
TESTS = ROOT / "tests" / "dynamic_source_trust"
DATA = ROOT / "data" / "dynamic_source_trust"
DOCS = ROOT / "docs" / "dynamic_source_trust"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    print("Installing Claire v17.46 Dynamic Source Trust + Reputation Intelligence...")

    write_file(LAYER / "__init__.py", '''
from .service import DynamicSourceTrustService
from .models import SourceTrustProfile, SourceTrustEvent, EvidenceWeightResult
from .store import SourceTrustStore
from .scorer import AdaptiveSourceTrustScorer
from .quarantine import SourceQuarantineEngine

__all__ = [
    "DynamicSourceTrustService",
    "SourceTrustProfile",
    "SourceTrustEvent",
    "EvidenceWeightResult",
    "SourceTrustStore",
    "AdaptiveSourceTrustScorer",
    "SourceQuarantineEngine",
]
''')

    write_file(LAYER / "models.py", '''
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class SourceTrustProfile:
    domain: str
    base_score: float = 0.55
    adaptive_score: float = 0.55
    status: str = "active"
    evidence_count: int = 0
    positive_events: int = 0
    negative_events: int = 0
    contradiction_events: int = 0
    correction_events: int = 0
    last_seen_at: Optional[str] = None
    last_updated_at: str = field(default_factory=utc_now)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceTrustEvent:
    event_id: str
    domain: str
    event_type: str
    evidence_id: Optional[str] = None
    confidence: float = 0.0
    impact: float = 0.0
    reason: str = ""
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceWeightResult:
    evidence_id: str
    domain: str
    original_confidence: float
    source_reliability: float
    adaptive_source_score: float
    weighted_confidence: float
    source_status: str
    weighting_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
''')

    write_file(LAYER / "defaults.py", '''
DEFAULT_SOURCE_BASE_SCORES = {
    "sec.gov": 0.96,
    "federalregister.gov": 0.94,
    "congress.gov": 0.93,
    "nist.gov": 0.93,
    "nih.gov": 0.92,
    "who.int": 0.90,
    "ftc.gov": 0.90,
    "justice.gov": 0.90,
    "treasury.gov": 0.90,
    "fda.gov": 0.90,
    "energy.gov": 0.88,
    "oecd.org": 0.88,
    "worldbank.org": 0.88,
    "imf.org": 0.88,
    "europa.eu": 0.88,
    "ec.europa.eu": 0.88,
    "gov.uk": 0.88,
    "reuters.com": 0.82,
    "apnews.com": 0.82,
    "nature.com": 0.82,
    "science.org": 0.82,
    "arxiv.org": 0.72,
}
''')

    write_file(LAYER / "store.py", '''
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import SourceTrustEvent, SourceTrustProfile
from .models import utc_now


class SourceTrustStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "dynamic_source_trust"
        self.profile_dir = self.root / "profiles"
        self.event_dir = self.root / "events"
        self.audit_dir = self.root / "audit"
        for path in [self.profile_dir, self.event_dir, self.audit_dir]:
            path.mkdir(parents=True, exist_ok=True)

    def profile_path(self, domain: str) -> Path:
        safe = self.safe_domain(domain)
        return self.profile_dir / f"{safe}.json"

    def save_profile(self, profile: SourceTrustProfile) -> Path:
        profile.last_updated_at = utc_now()
        path = self.profile_path(profile.domain)
        path.write_text(json.dumps(profile.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load_profile(self, domain: str) -> Optional[SourceTrustProfile]:
        path = self.profile_path(domain)
        if not path.exists():
            return None
        return SourceTrustProfile(**json.loads(path.read_text(encoding="utf-8")))

    def list_profiles(self) -> List[Dict[str, Any]]:
        profiles = []
        for path in sorted(self.profile_dir.glob("*.json")):
            try:
                profiles.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return profiles

    def save_event(self, event: SourceTrustEvent) -> Path:
        safe_domain = self.safe_domain(event.domain)
        path = self.event_dir / f"{safe_domain}_{event.event_id}.json"
        path.write_text(json.dumps(event.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def list_events(self, domain: str | None = None, limit: int = 100) -> List[Dict[str, Any]]:
        pattern = "*.json" if domain is None else f"{self.safe_domain(domain)}_*.json"
        events = []
        for path in sorted(self.event_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
            try:
                events.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return events

    def audit(self, event_type: str, payload: Dict[str, Any]) -> Path:
        safe = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in event_type)
        path = self.audit_dir / f"{utc_now().replace(':', '').replace('.', '_')}_{safe}.json"
        path.write_text(json.dumps({
            "event_type": event_type,
            "created_at": utc_now(),
            "payload": payload,
        }, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def safe_domain(self, domain: str) -> str:
        return "".join(ch if ch.isalnum() or ch in ".-" else "_" for ch in domain.lower()).strip(".")
''')

    write_file(LAYER / "scorer.py", '''
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
''')

    write_file(LAYER / "quarantine.py", '''
from __future__ import annotations

from .models import SourceTrustProfile


class SourceQuarantineEngine:
    def evaluate(self, profile: SourceTrustProfile) -> SourceTrustProfile:
        if profile.correction_events >= 2:
            profile.status = "quarantined"
            if "Quarantined because correction/retraction events reached threshold." not in profile.notes:
                profile.notes.append("Quarantined because correction/retraction events reached threshold.")
            return profile

        if profile.negative_events >= 3:
            profile.status = "quarantined"
            if "Quarantined because negative trust events reached threshold." not in profile.notes:
                profile.notes.append("Quarantined because negative trust events reached threshold.")
            return profile

        if profile.adaptive_score < 0.35 or profile.contradiction_events >= 3:
            profile.status = "degraded"
            if "Degraded because adaptive trust or contradiction count crossed threshold." not in profile.notes:
                profile.notes.append("Degraded because adaptive trust or contradiction count crossed threshold.")
            return profile

        if profile.status in {"degraded", "quarantined"} and profile.adaptive_score >= 0.65 and profile.negative_events == 0:
            profile.status = "active"

        return profile
''')

    write_file(LAYER / "service.py", '''
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
''')

    write_file(LAYER / "api_routes.py", '''
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .service import DynamicSourceTrustService


router = APIRouter(prefix="/internet/source-trust", tags=["Dynamic Source Trust"])


class TrustEventRequest(BaseModel):
    domain: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)
    evidence_id: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str = ""


class WeightEvidenceRequest(BaseModel):
    evidence: Dict[str, Any]


class WeightEvidenceBatchRequest(BaseModel):
    evidence: List[Dict[str, Any]]


@router.post("/events")
def record_event(request: TrustEventRequest):
    service = DynamicSourceTrustService()
    return service.record_event(
        domain=request.domain,
        event_type=request.event_type,
        evidence_id=request.evidence_id,
        confidence=request.confidence,
        reason=request.reason,
    )


@router.post("/weight")
def weight_evidence(request: WeightEvidenceRequest):
    service = DynamicSourceTrustService()
    return service.weight_evidence(request.evidence)


@router.post("/weight-batch")
def weight_evidence_batch(request: WeightEvidenceBatchRequest):
    service = DynamicSourceTrustService()
    return service.weight_evidence_batch(request.evidence)


@router.post("/quarantine/{domain}")
def quarantine_source(domain: str, reason: str = "Manual quarantine"):
    service = DynamicSourceTrustService()
    return service.quarantine_source(domain, reason=reason)


@router.post("/release/{domain}")
def release_source(domain: str, reason: str = "Manual release"):
    service = DynamicSourceTrustService()
    return service.release_source(domain, reason=reason)


@router.get("/profiles")
def list_profiles():
    service = DynamicSourceTrustService()
    return {"profiles": service.list_profiles()}


@router.get("/events")
def list_events(domain: Optional[str] = None, limit: int = 100):
    service = DynamicSourceTrustService()
    return {"events": service.list_events(domain=domain, limit=limit)}
''')

    write_file(LAYER / "cli.py", '''
from __future__ import annotations

import argparse
import json

from .service import DynamicSourceTrustService


def main() -> None:
    parser = argparse.ArgumentParser(description="Claire dynamic source trust")
    sub = parser.add_subparsers(dest="command", required=True)

    event = sub.add_parser("event")
    event.add_argument("--domain", required=True)
    event.add_argument("--event-type", required=True)
    event.add_argument("--evidence-id", default=None)
    event.add_argument("--confidence", type=float, default=0.0)
    event.add_argument("--reason", default="")

    quarantine = sub.add_parser("quarantine")
    quarantine.add_argument("--domain", required=True)
    quarantine.add_argument("--reason", default="Manual quarantine")

    release = sub.add_parser("release")
    release.add_argument("--domain", required=True)
    release.add_argument("--reason", default="Manual release")

    sub.add_parser("profiles")

    events = sub.add_parser("events")
    events.add_argument("--domain", default=None)
    events.add_argument("--limit", type=int, default=100)

    args = parser.parse_args()
    service = DynamicSourceTrustService()

    if args.command == "event":
        result = service.record_event(
            domain=args.domain,
            event_type=args.event_type,
            evidence_id=args.evidence_id,
            confidence=args.confidence,
            reason=args.reason,
        )
    elif args.command == "quarantine":
        result = service.quarantine_source(args.domain, reason=args.reason)
    elif args.command == "release":
        result = service.release_source(args.domain, reason=args.reason)
    elif args.command == "profiles":
        result = {"profiles": service.list_profiles()}
    elif args.command == "events":
        result = {"events": service.list_events(domain=args.domain, limit=args.limit)}
    else:
        raise SystemExit("Unknown command")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
''')

    write_file(TESTS / "test_dynamic_source_trust.py", '''
from pathlib import Path

from claire.dynamic_source_trust.service import DynamicSourceTrustService
from claire.dynamic_source_trust.store import SourceTrustStore


def test_get_or_create_profile_uses_known_base_score(tmp_path: Path):
    service = DynamicSourceTrustService(store=SourceTrustStore(tmp_path))
    profile = service.get_or_create_profile("sec.gov")

    assert profile.domain == "sec.gov"
    assert profile.base_score >= 0.9
    assert profile.status == "active"


def test_positive_event_increases_score(tmp_path: Path):
    service = DynamicSourceTrustService(store=SourceTrustStore(tmp_path))
    before = service.get_or_create_profile("example.com").adaptive_score
    result = service.record_event("example.com", "confirmed", confidence=0.9)
    after = result["profile"]["adaptive_score"]

    assert after > before


def test_negative_events_quarantine_source(tmp_path: Path):
    service = DynamicSourceTrustService(store=SourceTrustStore(tmp_path))
    for index in range(3):
        service.record_event("bad.example", "failed_validation", confidence=1.0)

    profile = service.get_or_create_profile("bad.example")
    assert profile.status == "quarantined"


def test_quarantined_source_caps_weighted_confidence(tmp_path: Path):
    service = DynamicSourceTrustService(store=SourceTrustStore(tmp_path))
    service.quarantine_source("bad.example")
    result = service.weight_evidence({
        "evidence_id": "ev1",
        "source_domain": "bad.example",
        "confidence": 0.95,
        "source_reliability": 0.8,
    })

    assert result["weighted_confidence"] <= 0.15
    assert result["source_status"] == "quarantined"


def test_batch_weighting(tmp_path: Path):
    service = DynamicSourceTrustService(store=SourceTrustStore(tmp_path))
    result = service.weight_evidence_batch([
        {"evidence_id": "ev1", "source_domain": "sec.gov", "confidence": 0.8, "source_reliability": 0.9},
        {"evidence_id": "ev2", "source_domain": "reuters.com", "confidence": 0.7, "source_reliability": 0.8},
    ])

    assert result["weighted_count"] == 2
    assert len(result["weighted_evidence"]) == 2
''')

    write_file(TESTS / "test_dynamic_source_trust_api.py", '''
from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.dynamic_source_trust import api_routes
from claire.dynamic_source_trust.service import DynamicSourceTrustService


def test_profiles_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    def fake_profiles(self):
        return [{"domain": "sec.gov", "adaptive_score": 0.96}]

    monkeypatch.setattr(DynamicSourceTrustService, "list_profiles", fake_profiles)

    client = TestClient(app)
    response = client.get("/internet/source-trust/profiles")

    assert response.status_code == 200
    assert response.json()["profiles"][0]["domain"] == "sec.gov"
''')

    write_file(DOCS / "v17_46_dynamic_source_trust.md", '''
# Claire v17.46 — Dynamic Source Trust + Reputation Intelligence

This package makes Claire's internet evidence weighting adaptive over time.

## Capabilities

- Source trust profiles
- Static base trust by known authoritative domains
- Adaptive trust score updates
- Positive/negative/contradiction/correction trust events
- Source quarantine
- Source release
- Evidence confidence reweighting
- Batch evidence weighting
- CLI and FastAPI routes

## CLI

```bash
python -m claire.dynamic_source_trust.cli event --domain sec.gov --event-type confirmed --confidence 0.9
python -m claire.dynamic_source_trust.cli quarantine --domain bad.example
python -m claire.dynamic_source_trust.cli profiles
```

## FastAPI Wiring

```python
from claire.dynamic_source_trust.api_routes import router as source_trust_router
app.include_router(source_trust_router)
```

## Boundary

This package does not automatically ban sources without recorded trust events or manual quarantine. It adjusts source weighting and quarantine status through explicit evidence outcome signals.
''')

    write_json(DATA / "dynamic_source_trust_manifest.json", {
        "installed_at": utc_now(),
        "layer": "dynamic_source_trust",
        "version": "v17.46",
        "status": "installed",
        "requires": [
            "claire.internet_activation",
            "claire.persistent_internet_campaigns"
        ],
        "capabilities": [
            "source_trust_profiles",
            "adaptive_source_scores",
            "source_trust_events",
            "source_quarantine",
            "source_release",
            "evidence_weighting",
            "batch_weighting",
            "cli",
            "fastapi_routes",
            "tests"
        ],
        "governance_boundary": "trust_adjustment_only_no_hidden_source_banning_without_event_or_manual_quarantine"
    })

    print("")
    print("INSTALL COMPLETE: Claire v17.46 Dynamic Source Trust + Reputation Intelligence")
    print("")
    print("Run tests with:")
    print("    python -m pytest tests/dynamic_source_trust -q")
    print("")
    print("CLI examples:")
    print("    python -m claire.dynamic_source_trust.cli profiles")
    print("    python -m claire.dynamic_source_trust.cli event --domain sec.gov --event-type confirmed --confidence 0.9")


if __name__ == "__main__":
    main()
