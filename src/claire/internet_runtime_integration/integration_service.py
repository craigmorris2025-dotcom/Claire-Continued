from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .dashboard_payload import InternetDashboardPayloadBuilder
from .lifecycle_adapter import InternetLifecycleAdapter


class InternetRuntimeIntegrationService:
    def __init__(self, adapter: InternetLifecycleAdapter | None = None) -> None:
        self.adapter = adapter or InternetLifecycleAdapter()
        self.dashboard = InternetDashboardPayloadBuilder()

    async def run_and_build_dashboard(self, query: str, run_id: str, lifecycle_stage: str = "research", urls: Optional[List[str]] = None, max_results: Optional[int] = None, core_output_path: Optional[Path] = None) -> Dict[str, Any]:
        result = await self.adapter.enrich_lifecycle_run(query=query, run_id=run_id, lifecycle_stage=lifecycle_stage, urls=urls, max_results=max_results, core_output_path=core_output_path)
        result["dashboard_payload"] = self.dashboard.build(result["internet_output"])
        return result
