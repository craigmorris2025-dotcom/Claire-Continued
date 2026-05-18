"""
Claire Syntalion v19.25.2+ stable repair baseline.
End-to-End Search Execution Contract.

Purpose:
- Treat normal search text as governed web search.
- Treat agent-like commands as review-required candidates, not executions.
- Keep search bar safe as both web-search entry point and future agent command surface.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
import re

AGENT_COMMAND_PATTERNS = (
    "run full",
    "execute full",
    "launch full",
    "start full",
    "build full",
    "autonomous",
    "agent command",
    "take over",
    "do the whole thing",
)

@dataclass(frozen=True)
class SearchExecutionRequest:
    query: str
    source: str = "dashboard_search_bar"
    mode: str = "governed_web"
    allow_live: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class SearchExecutionContract:
    query: str
    intent: str
    status: str
    source: str
    mode: str
    allow_live: bool
    governance_required: bool
    execution_allowed: bool
    warnings: List[str]
    evidence_required: bool
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "intent": self.intent,
            "status": self.status,
            "source": self.source,
            "mode": self.mode,
            "allow_live": self.allow_live,
            "governance_required": self.governance_required,
            "execution_allowed": self.execution_allowed,
            "warnings": list(self.warnings),
            "evidence_required": self.evidence_required,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _normalize_query(query: str) -> str:
    return re.sub(r"\s+", " ", (query or "").strip())

def _looks_like_agent_command(query: str) -> bool:
    q = _normalize_query(query).lower()
    return bool(q) and any(pattern in q for pattern in AGENT_COMMAND_PATTERNS)

def classify_search_intent(query: str) -> str:
    q = _normalize_query(query)
    if not q:
        return "empty_query"
    if _looks_like_agent_command(q):
        return "agent_command_candidate"
    return "web_search"

def build_search_execution_contract(request: SearchExecutionRequest | Dict[str, Any]) -> SearchExecutionContract:
    if isinstance(request, dict):
        request = SearchExecutionRequest(**request)

    query = _normalize_query(request.query)
    intent = classify_search_intent(query)
    warnings: List[str] = []
    execution_allowed = True
    status = "ready"

    if intent == "empty_query":
        warnings.append("empty_query_blocked")
        execution_allowed = False
        status = "blocked"
    elif intent == "agent_command_candidate":
        warnings.append("agent_command_detected_review_required")
        warnings.append("not_executed_as_agent_command")
        execution_allowed = False
        status = "review_required"

    return SearchExecutionContract(
        query=query,
        intent=intent,
        status=status,
        source=request.source,
        mode=request.mode,
        allow_live=bool(request.allow_live),
        governance_required=True,
        execution_allowed=execution_allowed,
        warnings=warnings,
        evidence_required=True,
        created_at=_now(),
        metadata=dict(request.metadata or {}),
    )
