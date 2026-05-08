from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .live_connectivity_regression_lock import LiveConnectivityRegressionLock
from .live_ingestion_worker import LiveIngestionWorker
from .search_adapter import GovernedSearchAdapter


class RealGovernedLiveConnectivityRuntime:
    def __init__(self, live_enabled: bool = False, evidence_root: Path | None = None) -> None:
        self.live_enabled = live_enabled
        self.worker = LiveIngestionWorker(live_enabled=live_enabled, evidence_root=evidence_root)
        self.search = GovernedSearchAdapter(configured=False)
        self.regression = LiveConnectivityRegressionLock()

    def ingest_url(self, url: str) -> Dict[str, Any]:
        ingestion = self.worker.ingest_url(url)
        output: Dict[str, Any] = {
            "layer": "real_governed_live_connectivity",
            "versions": {
                "live_http_client_adapter": "v17.11",
                "live_search_adapter_contract": "v17.12",
                "rate_limit_guard": "v17.13",
                "content_normalizer": "v17.14",
                "evidence_persistence": "v17.15",
                "retry_deadletter": "v17.16",
                "live_ingestion_worker": "v17.17",
                "source_policy_bridge": "v17.18",
                "runtime_contract": "v17.19",
                "regression_lock": "v17.20",
            },
            "live_enabled": self.live_enabled,
            "governance_boundary": "policy_review_rate_limited_no_unapproved_external_action",
            "ingestion": ingestion,
        }
        output["regression"] = self.regression.validate(output)
        return output

    def search_query(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        request = self.search.create_request(query=query, max_results=max_results)
        result = self.search.search(request)
        return {
            "layer": "real_governed_live_connectivity",
            "live_enabled": self.live_enabled,
            "governance_boundary": "policy_review_rate_limited_no_unapproved_external_action",
            "search_request": request.to_dict(),
            "search_result": result.to_dict(),
        }
