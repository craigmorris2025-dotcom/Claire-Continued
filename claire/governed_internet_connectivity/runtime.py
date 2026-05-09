from __future__ import annotations

from typing import Any, Dict, List, Optional

from .connectivity_regression_lock import ConnectivityRegressionLock
from .continuous_monitor import ContinuousMonitor
from .evidence_extractor import EvidenceExtractor
from .fetch_request_engine import FetchRequestEngine
from .signal_refresh_scheduler import SignalRefreshScheduler
from .source_policy import SourcePolicyEngine
from .watchlist_engine import OpportunityWatchlistEngine


class GovernedInternetRuntime:
    def __init__(self) -> None:
        self.policy = SourcePolicyEngine()
        self.fetcher = FetchRequestEngine(self.policy)
        self.extractor = EvidenceExtractor()
        self.monitor = ContinuousMonitor()
        self.watchlists = OpportunityWatchlistEngine()
        self.scheduler = SignalRefreshScheduler()
        self.regression = ConnectivityRegressionLock()

    def run_research_stub(
        self,
        query: str,
        source_url: Optional[str] = None,
        query_terms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        request = self.fetcher.create_request(query=query, source_url=source_url)
        policy_result = self.policy.evaluate(request.source_url, request.domain)
        fetch_result = self.fetcher.execute_stub(request)
        evidence = self.extractor.extract(fetch_result, query_terms=query_terms or query.split()[:5])

        output: Dict[str, Any] = {
            "layer": "governed_internet_connectivity",
            "versions": {
                "source_policy": "v17.01",
                "fetch_request_engine": "v17.02",
                "evidence_extractor": "v17.03",
                "source_reliability": "v17.04",
                "async_ingestion_queue": "v17.05",
                "continuous_monitor": "v17.06",
                "signal_refresh_scheduler": "v17.07",
                "watchlist_engine": "v17.08",
                "runtime_contract": "v17.09",
                "connectivity_regression_lock": "v17.10",
            },
            "governance_boundary": "no_unreviewed_external_action",
            "source_policy": policy_result,
            "request": request.__dict__.copy(),
            "fetch": fetch_result.__dict__.copy(),
            "evidence": [packet.to_dict() for packet in evidence],
        }
        output["regression"] = self.regression.validate(output)
        return output

    def build_watchlist_schedule(self, opportunities: List[Dict[str, object]]) -> Dict[str, Any]:
        items = self.watchlists.create_watchlist(opportunities)
        schedule = self.scheduler.build_schedule([item.to_dict() for item in items])
        return {
            "layer": "governed_internet_connectivity",
            "governance_boundary": "no_unreviewed_external_action",
            "watchlist": [item.to_dict() for item in items],
            "schedule": schedule,
        }

    def seed_monitoring_campaign(self, topics: List[str]) -> Dict[str, Any]:
        return self.monitor.seed_campaign(topics)
