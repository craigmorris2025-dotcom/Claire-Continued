from __future__ import annotations

import hashlib
from typing import Dict, Optional

from .models import FetchRequest, FetchResult
from .source_policy import SourcePolicyEngine


class FetchRequestEngine:
    def __init__(self, policy_engine: Optional[SourcePolicyEngine] = None) -> None:
        self.policy_engine = policy_engine or SourcePolicyEngine()

    def create_request(self, query: str, source_url: Optional[str] = None, purpose: str = "research") -> FetchRequest:
        request_id = "fetch_" + hashlib.sha256(f"{query}|{source_url}|{purpose}".encode("utf-8")).hexdigest()[:12]
        domain = self.policy_engine.domain_from_url(source_url) if source_url else None
        return FetchRequest(
            request_id=request_id,
            query=query,
            source_url=source_url,
            domain=domain,
            purpose=purpose,
        )

    def execute_stub(self, request: FetchRequest) -> FetchResult:
        policy = self.policy_engine.evaluate(request.source_url, request.domain)
        decision = str(policy["decision"])

        if decision == "blocked":
            return FetchResult(
                request_id=request.request_id,
                status="blocked",
                source_url=request.source_url,
                domain=request.domain,
                policy_decision=decision,
                error=str(policy["reason"]),
            )

        if decision == "review_required":
            return FetchResult(
                request_id=request.request_id,
                status="review_required",
                source_url=request.source_url,
                domain=request.domain,
                policy_decision=decision,
                error="Operator review required before fetch.",
            )

        # Foundation-only: this does not perform real network calls.
        # It provides the runtime contract that a real web adapter can later satisfy.
        content = f"STUB_FETCH_RESULT for query='{request.query}' source='{request.source_url or 'search_only'}'"
        return FetchResult(
            request_id=request.request_id,
            status="stubbed_success",
            content=content,
            source_url=request.source_url,
            domain=request.domain,
            policy_decision=decision,
        )
