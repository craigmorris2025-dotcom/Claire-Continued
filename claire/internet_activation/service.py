from __future__ import annotations

import asyncio, hashlib
from typing import Any, Dict, List, Optional

from .config import InternetActivationConfig
from .evidence import EvidenceExtractor
from .http_fetcher import GovernedHttpFetcher
from .models import ResearchRun, SearchResult
from .persistence import InternetResearchStore
from .search import SearchProviderError, SearchProviderRegistry


class InternetResearchService:
    def __init__(self, config: Optional[InternetActivationConfig] = None) -> None:
        self.config=config or InternetActivationConfig(); self.fetcher=GovernedHttpFetcher(self.config); self.search_registry=SearchProviderRegistry(self.config); self.extractor=EvidenceExtractor(); self.store=InternetResearchStore(self.config)

    async def research(self, query: str, urls: Optional[List[str]] = None, max_results: Optional[int] = None) -> Dict[str, Any]:
        query=query.strip()
        if not query: raise ValueError("query is required")
        max_results=max(1, min(max_results or self.config.max_results, self.config.max_results))
        provider_name=self.search_registry.configured_provider_name() or "none"
        run_id="internet_run_"+hashlib.sha256(f"{query}|{provider_name}|{urls}".encode()).hexdigest()[:16]
        run=ResearchRun(run_id, query, "running", provider_name)
        warnings=[]; errors=[]; search_results=[]
        if urls:
            search_results=[SearchResult("Direct URL", url, "", "direct_url", idx) for idx,url in enumerate(urls[:max_results],1)]
        else:
            provider=self.search_registry.provider()
            if provider is None:
                run.status="not_configured"; warnings.append("No search provider configured. Add a supported API key to .env or pass explicit URLs.")
            else:
                try: search_results=await self.search_registry.search(query, max_results); run.searched=True
                except SearchProviderError as exc: errors.append(str(exc))
                except Exception as exc: errors.append(f"Search failed: {exc}")
        fetch_outputs=[]; evidence_outputs=[]
        for result in search_results[:max_results]:
            if not result.url: continue
            fetch=await self.fetcher.fetch(result.url); fetch_outputs.append(fetch.to_dict())
            if fetch.status != "success":
                if fetch.error: warnings.append(f"{fetch.url}: {fetch.status} - {fetch.error}")
                continue
            for record in self.extractor.extract(run_id, query, fetch, result):
                self.store.save_evidence(record); run.evidence_ids.append(record.evidence_id); evidence_outputs.append(record.to_dict())
        run.fetched_count=len(fetch_outputs); run.evidence_count=len(evidence_outputs); run.warnings=warnings; run.errors=errors
        run.status="completed" if evidence_outputs else ("completed_no_evidence" if not errors else "failed")
        if not search_results and not errors and warnings: run.status="not_configured"
        output={"layer":"internet_activation","version":"v17.41","run":run.to_dict(),"search_results":[i.to_dict() for i in search_results],"fetch_results":fetch_outputs,"evidence":evidence_outputs,"governance":{"allow_unknown_domains":self.config.allow_unknown_domains,"max_results":self.config.max_results,"max_bytes":self.config.max_bytes,"timeout_seconds":self.config.timeout_seconds,"blocked_extensions":self.config.blocked_extensions,"allowed_content_types":self.config.allowed_content_types}}
        self.store.save_run(run, output); self.store.audit("internet_research_run", {"run_id":run_id,"query":query,"status":run.status,"evidence_count":run.evidence_count,"warnings":warnings,"errors":errors})
        return output

    def research_sync(self, query: str, urls: Optional[List[str]] = None, max_results: Optional[int] = None) -> Dict[str, Any]:
        return asyncio.run(self.research(query, urls, max_results))
    def get_evidence(self, evidence_id: str) -> Dict[str, Any] | None: return self.store.get_evidence(evidence_id)
    def list_evidence(self, limit: int = 50) -> List[Dict[str, Any]]: return self.store.list_evidence(limit)
