"""
Governance Decision — standardized allow/review/block response object.

v5.42:
- Used by feed activation, dashboard launch, and legal audit layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid


@dataclass
class GovernanceDecision:
    decision_id: str
    decision: str
    severity: str
    defense_classification: str
    legal_status: str
    reason_summary: str
    triggered_terms: List[str] = field(default_factory=list)
    recommended_action: str = "continue"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        decision: str,
        severity: str,
        defense_classification: str,
        legal_status: str,
        reason_summary: str,
        triggered_terms: List[str] | None = None,
        recommended_action: str = "continue",
        details: Dict[str, Any] | None = None,
    ) -> "GovernanceDecision":
        return cls(
            decision_id="gov_" + uuid.uuid4().hex[:12],
            decision=decision,
            severity=severity,
            defense_classification=defense_classification,
            legal_status=legal_status,
            reason_summary=reason_summary,
            triggered_terms=triggered_terms or [],
            recommended_action=recommended_action,
            details=details or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
