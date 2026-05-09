from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from .models import LiveSearchRequest, LiveSearchResult


class GovernedSearchAdapter:
    def __init__(self, configured: bool = False) -> None:
        self.configured = configured

    def create_request(self, query: str, max_results: int = 5) -> LiveSearchRequest:
        search_id = "live_search_" + hashlib.sha256(f"{query}|{max_results}".encode("utf-8")).hexdigest()[:12]
        return LiveSearchRequest(search_id=search_id, query=query, max_results=max_results)

    def search(self, request: LiveSearchRequest) -> LiveSearchResult:
        if not self.configured:
            return LiveSearchResult(
                search_id=request.search_id,
                query=request.query,
                status="not_configured",
                results=[],
                adapter_status="not_configured",
                error="No live search provider configured.",
            )

        # Provider wiring belongs to a later secrets-managed adapter.
        return LiveSearchResult(
            search_id=request.search_id,
            query=request.query,
            status="provider_contract_ready",
            results=[],
            adapter_status="provider_contract_ready",
        )
