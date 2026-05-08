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
