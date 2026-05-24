"""
Opportunity Candidate Store — protected in-memory candidate registry.

v5.40:
- Keeps raw Claire launch prompts out of the dashboard UI.
- Dashboard receives public opportunity cards and opaque candidate IDs.
- Server retrieves protected raw_input only when the user runs a selected candidate.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime, timezone
from threading import Lock
import uuid


class OpportunityCandidateStore:
    """Thread-safe in-memory candidate registry for dashboard-generated opportunities."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._candidates: Dict[str, Dict[str, Any]] = {}

    def put(self, candidate: Dict[str, Any]) -> str:
        candidate_id = "opp_" + uuid.uuid4().hex[:12]
        record = dict(candidate)
        record["candidate_id"] = candidate_id
        record["created_at"] = datetime.now(timezone.utc).isoformat()
        with self._lock:
            self._candidates[candidate_id] = record
        return candidate_id

    def get(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            candidate = self._candidates.get(candidate_id)
            return dict(candidate) if candidate else None

    def public_card(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Return only user-facing fields. Do not expose raw_input or internal construction notes."""
        return {
            "candidate_id": candidate.get("candidate_id"),
            "title": candidate.get("title"),
            "market_universe": candidate.get("market_universe"),
            "industry_domain": candidate.get("industry_domain"),
            "buyer_segment": candidate.get("buyer_segment"),
            "objective": candidate.get("objective"),
            "opportunity_direction": candidate.get("opportunity_direction"),
            "market_gap": candidate.get("market_gap"),
            "needed_solution": candidate.get("needed_solution"),
            "why_now": candidate.get("why_now"),
            "selection_score": candidate.get("selection_score"),
            "confidence_label": candidate.get("confidence_label"),
            "connected_enrichment": candidate.get("connected_enrichment"),
            "hybrid_fusion": candidate.get("hybrid_fusion"),
        }


OPPORTUNITY_CANDIDATES = OpportunityCandidateStore()
