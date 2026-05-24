from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime_core.internet_activation import InternetResearchService
from runtime_core.internet_activation.config import InternetActivationConfig

from .evidence_continuity import InternetEvidenceContinuityStore
from .models import InternetRuntimeRequest, RuntimeInternetSummary


class InternetRuntimeBridge:
    def __init__(self, data_root: Path | None = None, research_service: InternetResearchService | None = None, continuity_store: InternetEvidenceContinuityStore | None = None) -> None:
        if research_service is None:
            research_service = InternetResearchService(InternetActivationConfig())
        self.research_service = research_service
        self.continuity = continuity_store or InternetEvidenceContinuityStore(data_root)

    async def run_research(self, request: InternetRuntimeRequest) -> Dict[str, Any]:
        run_id = request.run_id or self._run_id(request.query, request.urls)
        result = await self.research_service.research(query=request.query, urls=request.urls, max_results=request.max_results)
        activation_run = result.get("run", {})
        result["runtime_run_id"] = run_id
        result["attached_lifecycle_stage"] = request.lifecycle_stage

        links = []
        for evidence in result.get("evidence", []):
            link = self.continuity.link_evidence(run_id=run_id, query=request.query, evidence=evidence, lifecycle_stage=request.lifecycle_stage)
            links.append(link.to_dict())

        summary = RuntimeInternetSummary(
            run_id=run_id,
            query=request.query,
            internet_status=str(activation_run.get("status", "unknown")),
            searched=bool(activation_run.get("searched", False)),
            fetched_count=int(activation_run.get("fetched_count", 0)),
            evidence_count=int(activation_run.get("evidence_count", len(links))),
            warnings=list(activation_run.get("warnings", [])),
            errors=list(activation_run.get("errors", [])),
            evidence_ids=[link["evidence_id"] for link in links],
        )
        return {"runtime_run_id": run_id, "internet_activation_result": result, "internet_summary": summary.to_dict(), "evidence_links": links}

    def run_research_sync(self, request: InternetRuntimeRequest) -> Dict[str, Any]:
        return asyncio.run(self.run_research(request))

    def _run_id(self, query: str, urls: Optional[List[str]]) -> str:
        return "runtime_internet_" + hashlib.sha256(f"{query}|{urls}".encode("utf-8")).hexdigest()[:16]
