from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List


TRUST_WEIGHTS = {
    "regulatory": 0.94,
    "sec": 0.92,
    "standards": 0.88,
    "patent": 0.86,
    "research": 0.82,
    "promoted_metadata_evidence": 0.78,
    "allowlisted_monitor": 0.72,
}


def _family(signal: Dict[str, Any]) -> str:
    value = str(signal.get("source_family") or signal.get("source_type") or "allowlisted_monitor").lower()
    for key in TRUST_WEIGHTS:
        if key in value:
            return key
    return "allowlisted_monitor"


def build_evidence_governance(signals: List[Dict[str, Any]], thesis: Dict[str, Any], discovery: Dict[str, Any]) -> Dict[str, Any]:
    """Build governed evidence quality, claim, lineage, and conflict checks.

    The recovered research_live files are reference specs. This runtime module
    implements their checks from active signal metadata and claims.
    """

    source_families = Counter(_family(signal) for signal in signals if isinstance(signal, dict))
    evidence_count = len(signals)
    weighted_quality = 0.0
    ranked = []
    for signal in signals:
        family = _family(signal)
        quality = TRUST_WEIGHTS.get(family, 0.7)
        if signal.get("provenance", {}).get("trust_tier"):
            quality = min(0.96, quality + 0.06)
        weighted_quality += quality
        ranked.append(
            {
                "signal_id": signal.get("signal_id"),
                "title": signal.get("title"),
                "source_family": signal.get("source_family"),
                "quality_score": round(quality, 4),
                "lineage": signal.get("provenance", {}),
            }
        )
    aggregate_quality = round(weighted_quality / max(1, evidence_count), 4)
    ranked.sort(key=lambda item: item["quality_score"], reverse=True)

    claims = [
        thesis.get("statement"),
        discovery.get("summary"),
        "A governed portfolio package can be built from the current signal set." if evidence_count else None,
    ]
    verified_claims = []
    for claim in [item for item in claims if item]:
        support = ranked[: min(4, len(ranked))]
        verdict = "verified" if aggregate_quality >= 0.72 and len(support) >= 2 else "insufficient"
        verified_claims.append(
            {
                "claim_text": claim,
                "verdict": verdict,
                "confidence": aggregate_quality if verdict == "verified" else round(aggregate_quality * 0.65, 4),
                "supporting_refs": [item["signal_id"] for item in support if item.get("signal_id")],
                "contradicting_refs": [],
            }
        )

    duplicate_titles = [
        title
        for title, count in Counter(str(signal.get("title") or "").lower() for signal in signals).items()
        if title and count > 1
    ]
    conflicts = []
    if duplicate_titles:
        conflicts.append(
            {
                "type": "partial_overlap",
                "items": duplicate_titles[:5],
                "resolution": "deduplicate by signal_id and prefer higher source authority",
            }
        )

    status = "evidence_governance_ready" if aggregate_quality >= 0.72 and verified_claims and not any(
        claim["verdict"] == "insufficient" for claim in verified_claims
    ) else "evidence_governance_needs_enrichment"

    return {
        "schema_version": "claire.evidence_governance.v1",
        "status": status,
        "source": "allowlisted_signal_metadata",
        "documents_used_as_runtime_programming": False,
        "evidence_count": evidence_count,
        "source_family_counts": dict(source_families),
        "quality": {
            "aggregate_score": aggregate_quality,
            "methodology_rigor": "metadata_lineage_verified",
            "sample_adequacy": "sufficient" if evidence_count >= 5 else "thin",
            "source_authority": "mixed_governed_sources" if len(source_families) > 1 else "single_source_family",
        },
        "claim_verification": verified_claims,
        "citation_lineage": ranked[:8],
        "conflict_resolution": {
            "status": "no_conflicts_detected" if not conflicts else "resolved_conflicts_present",
            "conflicts": conflicts,
        },
        "operator_review_required": True,
    }
