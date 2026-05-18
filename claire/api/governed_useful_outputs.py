from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Mapping

ROUTE_OUTPUT_LABELS = {
    "portfolio": "portfolio_observation",
    "breakthrough": "breakthrough_possibility",
    "design": "design_signal",
    "discovery": "discovery_observation",
}

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(encoded).hexdigest()[:16]}"

def build_useful_output_candidate(discovery_candidate: Mapping[str, Any]) -> Dict[str, Any]:
    route = str(discovery_candidate.get("candidate_type") or "discovery")
    output_type = ROUTE_OUTPUT_LABELS.get(route, "discovery_observation")
    signals = discovery_candidate.get("signals") if isinstance(discovery_candidate.get("signals"), list) else []
    payload = {
        "discovery_candidate_id": discovery_candidate.get("candidate_id"),
        "route": route,
        "signals": signals,
        "headline": discovery_candidate.get("headline"),
    }
    return {
        "output_candidate_id": _stable_id("out", payload),
        "candidate_version": "S86",
        "created_at": _utc_now(),
        "route": route,
        "output_type": output_type,
        "status": "review_required",
        "headline": discovery_candidate.get("headline", "Useful output candidate"),
        "summary": "Route-aware useful output candidate derived from a quarantined discovery candidate. Manual approval is required before export.",
        "recommended_operator_action": "review",
        "source_discovery_candidate_id": discovery_candidate.get("candidate_id"),
        "source_evidence_ids": list(discovery_candidate.get("source_evidence_ids") or []),
        "signals": signals,
        "confidence": float(discovery_candidate.get("confidence", 0.0) or 0.0),
        "trust_score": float(discovery_candidate.get("trust_score", 0.0) or 0.0),
        "authority": {
            "runtime_truth": "blocked",
            "runtime_truth_write": "blocked",
            "automatic_update": "blocked",
            "autonomous_execution": "blocked",
            "manual_review_required": True,
            "export_allowed_after_approval": True,
        },
        "lineage": {
            "discovery_candidate_id": discovery_candidate.get("candidate_id"),
            "evidence_basket_id": (discovery_candidate.get("lineage") or {}).get("evidence_basket_id") if isinstance(discovery_candidate.get("lineage"), Mapping) else None,
        },
    }
