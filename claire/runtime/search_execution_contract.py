"""
Claire Syntalion v19.25 - End-to-End Search Execution Contract.

This module converts a permanent search-bar request into a normalized, governed,
reviewable search execution object. It is intentionally read-only and deterministic.
Later packs attach live retrieval, evidence ingestion, routing, and dashboard sync.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, List, Optional
from uuid import uuid4


ALLOWED_EXECUTION_MODES = {"simulation", "dry_run", "live_read_only"}
ALLOWED_INTENTS = {
    "web_search",
    "governed_research",
    "runtime_search",
    "system_search",
    "agent_command_candidate",
}


@dataclass(frozen=True)
class SearchExecutionRequest:
    query: str
    intent: str = "web_search"
    requested_by: str = "operator"
    source: str = "dashboard_search_bar"
    execution_mode: str = "dry_run"
    session_id: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchExecutionContract:
    execution_id: str
    query: str
    normalized_query: str
    query_hash: str
    intent: str
    requested_by: str
    source: str
    execution_mode: str
    session_id: str
    created_at: str
    governance_required: bool
    retrieval_allowed: bool
    pipeline_ingestion_candidate: bool
    dashboard_review_required: bool
    blocked: bool
    block_reasons: List[str]
    warnings: List[str]
    next_required_stage: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_search_query(query: str) -> str:
    return " ".join((query or "").strip().split())


def classify_search_intent(query: str, explicit_intent: Optional[str] = None) -> str:
    normalized = normalize_search_query(query).lower()
    if explicit_intent in ALLOWED_INTENTS:
        return explicit_intent

    command_words = ("run ", "execute ", "build ", "launch ", "create ", "start ")
    system_words = ("claire", "runtime", "pipeline", "dashboard", "manifest", "contract")
    research_words = ("research", "analyze", "compare", "evidence", "sources", "latest")

    if normalized.startswith(command_words):
        return "agent_command_candidate"
    if any(word in normalized for word in system_words):
        return "system_search"
    if any(word in normalized for word in research_words):
        return "governed_research"
    return "web_search"


def build_search_execution_contract(request: SearchExecutionRequest | Dict[str, Any]) -> SearchExecutionContract:
    if isinstance(request, dict):
        request = SearchExecutionRequest(**request)

    normalized_query = normalize_search_query(request.query)
    warnings: List[str] = []
    block_reasons: List[str] = []

    if not normalized_query:
        block_reasons.append("empty_query")
    if len(normalized_query) < 2:
        block_reasons.append("query_too_short")
    if len(normalized_query) > 1000:
        block_reasons.append("query_too_long")
    if request.execution_mode not in ALLOWED_EXECUTION_MODES:
        block_reasons.append("unsupported_execution_mode")
    if request.source not in {"dashboard_search_bar", "api", "runtime", "test"}:
        warnings.append("unknown_request_source")

    intent = classify_search_intent(normalized_query, request.intent)
    if intent == "agent_command_candidate":
        warnings.append("agent_command_detected_but_not_autonomously_executed")

    blocked = bool(block_reasons)
    retrieval_allowed = (not blocked) and request.execution_mode in {"dry_run", "live_read_only", "simulation"}
    pipeline_ingestion_candidate = retrieval_allowed and intent in {"web_search", "governed_research"}

    if blocked:
        next_required_stage = "operator_query_correction"
    elif request.execution_mode == "simulation":
        next_required_stage = "simulated_retrieval_preview"
    else:
        next_required_stage = "governed_retrieval"

    query_hash = sha256(normalized_query.encode("utf-8")).hexdigest()[:16]

    return SearchExecutionContract(
        execution_id=f"search-exec-{uuid4().hex[:12]}",
        query=request.query,
        normalized_query=normalized_query,
        query_hash=query_hash,
        intent=intent,
        requested_by=request.requested_by,
        source=request.source,
        execution_mode=request.execution_mode,
        session_id=request.session_id,
        created_at=_utc_now(),
        governance_required=True,
        retrieval_allowed=retrieval_allowed,
        pipeline_ingestion_candidate=pipeline_ingestion_candidate,
        dashboard_review_required=True,
        blocked=blocked,
        block_reasons=block_reasons,
        warnings=warnings,
        next_required_stage=next_required_stage,
        metadata=dict(request.metadata or {}),
    )


def summarize_search_execution_contract(contract: SearchExecutionContract | Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(contract, SearchExecutionContract):
        contract = contract.to_dict()
    return {
        "execution_id": contract["execution_id"],
        "normalized_query": contract["normalized_query"],
        "intent": contract["intent"],
        "execution_mode": contract["execution_mode"],
        "blocked": contract["blocked"],
        "retrieval_allowed": contract["retrieval_allowed"],
        "pipeline_ingestion_candidate": contract["pipeline_ingestion_candidate"],
        "next_required_stage": contract["next_required_stage"],
        "dashboard_review_required": contract["dashboard_review_required"],
    }
