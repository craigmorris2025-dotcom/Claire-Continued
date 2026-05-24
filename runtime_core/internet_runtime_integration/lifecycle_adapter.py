from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from .bridge import InternetRuntimeBridge
from .models import InternetRuntimeRequest
from .output_merger import CoreRunOutputInternetMerger


class InternetLifecycleAdapter:
    def __init__(self, bridge: InternetRuntimeBridge | None = None) -> None:
        self.bridge = bridge or InternetRuntimeBridge()
        self.merger = CoreRunOutputInternetMerger()

    async def enrich_lifecycle_run(self, query: str, run_id: str, lifecycle_stage: str = "research", urls: Optional[List[str]] = None, max_results: Optional[int] = None, core_output: Optional[Dict[str, Any]] = None, core_output_path: Optional[Path] = None) -> Dict[str, Any]:
        request = InternetRuntimeRequest(query=query, run_id=run_id, urls=urls, max_results=max_results, lifecycle_stage=lifecycle_stage)
        internet_output = await self.bridge.run_research(request)
        if core_output is not None:
            merged = self.merger.merge_dict(core_output, internet_output)
        elif core_output_path is not None:
            merged = self.merger.merge_file(core_output_path, internet_output, write_back=True)
        else:
            merged = {"run_id": run_id, "status": "internet_enriched", "internet_research": internet_output}
        return {"run_id": run_id, "lifecycle_stage": lifecycle_stage, "internet_output": internet_output, "merged_output": merged}

    def enrich_lifecycle_run_sync(self, **kwargs: Any) -> Dict[str, Any]:
        return asyncio.run(self.enrich_lifecycle_run(**kwargs))
