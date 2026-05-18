"""
Claire Syntalion v18.49.1
Governed Search Evidence Basket Import Path Repair

Purpose:
- Ensure the v18.49 governed search evidence basket is available from the
  active root-level claire package import path.
- Preserve fail-closed behavior.
- Preserve runtime truth immutability.
- Do not perform autonomous mutation, automatic updates, or unbounded execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
import hashlib


MAX_EVIDENCE_ITEMS = 25
MAX_TITLE_CHARS = 240
MAX_URL_CHARS = 1000
MAX_SNIPPET_CHARS = 1200


@dataclass(frozen=True)
class GovernedSearchEvidenceItem:
    evidence_id: str
    title: str
    url: str
    snippet: str = ""
    provider: str = "unknown"
    trust_score: float = 0.0
    rank: int = 0
    captured_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    review_required: bool = True
    runtime_truth_mutation_allowed: bool = False
    automatic_update_allowed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GovernedSearchEvidenceBasket:
    status: str
    query: str
    evidence_items: List[GovernedSearchEvidenceItem]
    governance_state: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    review_required: bool = True
    runtime_truth_mutation_allowed: bool = False
    automatic_update_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "query": self.query,
            "created_at": self.created_at,
            "review_required": self.review_required,
            "runtime_truth_mutation_allowed": self.runtime_truth_mutation_allowed,
            "automatic_update_allowed": self.automatic_update_allowed,
            "governance_state": dict(self.governance_state),
            "evidence_items": [item.to_dict() for item in self.evidence_items],
            "evidence_count": len(self.evidence_items),
        }


def _safe_text(value: Any, limit: int) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.split())
    return text[:limit]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number < 0:
        return 0.0
    if number > 1:
        return 1.0
    return number


def _safe_int(value: Any, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


def _evidence_id(query: str, url: str, title: str, rank: int) -> str:
    seed = f"{query}|{url}|{title}|{rank}".encode("utf-8", errors="ignore")
    return "ev_" + hashlib.sha256(seed).hexdigest()[:16]


def build_governed_search_evidence_basket(
    query: str,
    results: Optional[Iterable[Dict[str, Any]]],
    governance_state: Optional[Dict[str, Any]] = None,
) -> GovernedSearchEvidenceBasket:
    """Build a review-safe evidence basket from normalized search results.

    This function is intentionally pure and side-effect free. It does not write
    files, mutate runtime truth, perform network calls, or approve updates.
    """
    safe_query = _safe_text(query, 500)
    state = dict(governance_state or {})
    state.setdefault("fail_closed", True)
    state.setdefault("review_required", True)
    state.setdefault("runtime_truth_mutation_allowed", False)
    state.setdefault("automatic_update_allowed", False)
    state.setdefault("autonomous_execution_allowed", False)

    if not safe_query:
        return GovernedSearchEvidenceBasket(
            status="blocked_empty_query",
            query="",
            evidence_items=[],
            governance_state=state,
        )

    if results is None:
        return GovernedSearchEvidenceBasket(
            status="no_results",
            query=safe_query,
            evidence_items=[],
            governance_state=state,
        )

    items: List[GovernedSearchEvidenceItem] = []
    seen_urls = set()

    for index, raw in enumerate(results):
        if len(items) >= MAX_EVIDENCE_ITEMS:
            state["truncated"] = True
            state["max_evidence_items"] = MAX_EVIDENCE_ITEMS
            break

        if not isinstance(raw, dict):
            continue

        title = _safe_text(raw.get("title") or raw.get("name"), MAX_TITLE_CHARS)
        url = _safe_text(raw.get("url") or raw.get("link"), MAX_URL_CHARS)
        snippet = _safe_text(raw.get("snippet") or raw.get("description") or raw.get("summary"), MAX_SNIPPET_CHARS)
        provider = _safe_text(raw.get("provider") or raw.get("source") or "unknown", 120)
        rank = _safe_int(raw.get("rank"), index + 1)
        trust_score = _safe_float(raw.get("trust_score") or raw.get("score") or 0.0)

        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        items.append(
            GovernedSearchEvidenceItem(
                evidence_id=_evidence_id(safe_query, url, title, rank),
                title=title or url,
                url=url,
                snippet=snippet,
                provider=provider,
                trust_score=trust_score,
                rank=rank,
                review_required=True,
                runtime_truth_mutation_allowed=False,
                automatic_update_allowed=False,
                metadata={
                    "raw_keys": sorted(str(k) for k in raw.keys()),
                    "captured_by": "v18.49.1_evidence_basket_import_path_repair",
                },
            )
        )

    return GovernedSearchEvidenceBasket(
        status="evidence_captured" if items else "no_eligible_evidence",
        query=safe_query,
        evidence_items=items,
        governance_state=state,
    )
