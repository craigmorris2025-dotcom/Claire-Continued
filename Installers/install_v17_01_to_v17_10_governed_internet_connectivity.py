# Claire Syntalion Installer
# v17.01-v17.10 Governed Internet Connectivity + Continuous Intelligence Foundation
#
# Place this file in the Claire project root and run:
#
#     python install_v17_01_to_v17_10_governed_internet_connectivity.py
#
# Then test:
#
#     python -m pytest tests/governed_internet_connectivity -q

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CLAIRE = SRC / "claire"
LAYER = CLAIRE / "governed_internet_connectivity"
TESTS = ROOT / "tests" / "governed_internet_connectivity"
DATA = ROOT / "data" / "governed_internet_connectivity"
DOCS = ROOT / "docs" / "governed_internet_connectivity"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    print("Installing Claire v17.01-v17.10 Governed Internet Connectivity Foundation...")

    write_file(LAYER / "__init__.py", """
from .runtime import GovernedInternetRuntime
from .source_policy import SourcePolicyEngine
from .fetch_request_engine import FetchRequestEngine
from .evidence_extractor import EvidenceExtractor
from .source_reliability import SourceReliabilityEngine
from .async_ingestion_queue import AsyncIngestionQueue
from .continuous_monitor import ContinuousMonitor
from .signal_refresh_scheduler import SignalRefreshScheduler
from .watchlist_engine import OpportunityWatchlistEngine
from .connectivity_regression_lock import ConnectivityRegressionLock

__all__ = [
    "GovernedInternetRuntime",
    "SourcePolicyEngine",
    "FetchRequestEngine",
    "EvidenceExtractor",
    "SourceReliabilityEngine",
    "AsyncIngestionQueue",
    "ContinuousMonitor",
    "SignalRefreshScheduler",
    "OpportunityWatchlistEngine",
    "ConnectivityRegressionLock",
]
""")

    write_file(LAYER / "models.py", """
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class SourcePolicy:
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    require_review_for_unknown_sources: bool = True
    max_fetches_per_run: int = 10
    governance_mode: str = "review_first"


@dataclass
class FetchRequest:
    request_id: str
    query: str
    source_url: Optional[str] = None
    domain: Optional[str] = None
    purpose: str = "research"
    status: str = "pending_policy_check"
    created_at: str = field(default_factory=utc_now)


@dataclass
class FetchResult:
    request_id: str
    status: str
    content: str = ""
    source_url: Optional[str] = None
    domain: Optional[str] = None
    policy_decision: str = "unknown"
    error: Optional[str] = None
    fetched_at: str = field(default_factory=utc_now)


@dataclass
class EvidencePacket:
    evidence_id: str
    claim: str
    source_url: Optional[str]
    domain: Optional[str]
    reliability_score: float
    confidence: float
    extraction_method: str = "bounded_text_extraction"
    supporting_terms: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    lineage: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueueItem:
    item_id: str
    query: str
    priority: int = 5
    status: str = "queued"
    attempts: int = 0
    max_attempts: int = 3
    created_at: str = field(default_factory=utc_now)


@dataclass
class WatchlistItem:
    watch_id: str
    topic: str
    thesis: str
    cadence: str = "daily"
    status: str = "active"
    last_checked_at: Optional[str] = None
    confidence: float = 0.0
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
""")

    write_file(LAYER / "source_policy.py", """
from __future__ import annotations

from urllib.parse import urlparse
from typing import Dict, Optional

from .models import SourcePolicy


class SourcePolicyEngine:
    def __init__(self, policy: Optional[SourcePolicy] = None) -> None:
        self.policy = policy or SourcePolicy(
            allowed_domains=[
                "sec.gov",
                "federalregister.gov",
                "congress.gov",
                "nist.gov",
                "nih.gov",
                "who.int",
                "oecd.org",
                "worldbank.org",
                "imf.org",
                "reuters.com",
                "apnews.com",
            ],
            blocked_domains=[],
            require_review_for_unknown_sources=True,
            max_fetches_per_run=10,
            governance_mode="review_first",
        )

    def domain_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc.lower().replace("www.", "")

    def evaluate(self, source_url: Optional[str], domain: Optional[str] = None) -> Dict[str, object]:
        resolved_domain = domain or (self.domain_from_url(source_url) if source_url else None)

        if not resolved_domain:
            return {
                "decision": "search_only",
                "domain": None,
                "requires_review": True,
                "reason": "No domain supplied; search request must remain bounded.",
            }

        if resolved_domain in self.policy.blocked_domains:
            return {
                "decision": "blocked",
                "domain": resolved_domain,
                "requires_review": True,
                "reason": "Domain is explicitly blocked.",
            }

        if resolved_domain in self.policy.allowed_domains:
            return {
                "decision": "allowed",
                "domain": resolved_domain,
                "requires_review": False,
                "reason": "Domain is on governed allowlist.",
            }

        return {
            "decision": "review_required",
            "domain": resolved_domain,
            "requires_review": self.policy.require_review_for_unknown_sources,
            "reason": "Domain is unknown and requires operator review.",
        }
""")

    write_file(LAYER / "fetch_request_engine.py", """
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
""")

    write_file(LAYER / "source_reliability.py", """
from __future__ import annotations

from typing import Optional


class SourceReliabilityEngine:
    HIGH_TRUST = {
        "sec.gov": 0.95,
        "federalregister.gov": 0.93,
        "congress.gov": 0.92,
        "nist.gov": 0.92,
        "nih.gov": 0.92,
        "who.int": 0.9,
        "oecd.org": 0.88,
        "worldbank.org": 0.88,
        "imf.org": 0.88,
        "reuters.com": 0.82,
        "apnews.com": 0.82,
    }

    def score(self, domain: Optional[str], content: str = "") -> float:
        if not domain:
            return 0.45

        base = self.HIGH_TRUST.get(domain, 0.55)

        if not content:
            return round(max(0.1, base - 0.1), 4)

        if "STUB_FETCH_RESULT" in content:
            return round(min(base, 0.5), 4)

        if len(content) < 200:
            return round(max(0.1, base - 0.08), 4)

        return round(base, 4)
""")

    write_file(LAYER / "evidence_extractor.py", """
from __future__ import annotations

import hashlib
from typing import List

from .models import EvidencePacket, FetchResult
from .source_reliability import SourceReliabilityEngine


class EvidenceExtractor:
    def __init__(self, reliability_engine: SourceReliabilityEngine | None = None) -> None:
        self.reliability_engine = reliability_engine or SourceReliabilityEngine()

    def extract(self, result: FetchResult, query_terms: List[str] | None = None) -> List[EvidencePacket]:
        terms = query_terms or []
        reliability = self.reliability_engine.score(result.domain, result.content)

        if result.status not in {"stubbed_success", "success"}:
            return []

        claim = self._claim_from_content(result.content)
        evidence_id = "evidence_" + hashlib.sha256(
            f"{result.request_id}|{claim}|{result.source_url}".encode("utf-8")
        ).hexdigest()[:12]

        confidence = min(1.0, max(0.0, reliability * 0.75 + (0.05 * len(terms))))

        return [
            EvidencePacket(
                evidence_id=evidence_id,
                claim=claim,
                source_url=result.source_url,
                domain=result.domain,
                reliability_score=reliability,
                confidence=round(confidence, 4),
                supporting_terms=terms,
                lineage={
                    "request_id": result.request_id,
                    "policy_decision": result.policy_decision,
                    "fetch_status": result.status,
                },
            )
        ]

    def _claim_from_content(self, content: str) -> str:
        text = " ".join(content.split())
        if len(text) > 240:
            return text[:237] + "..."
        return text or "No extractable claim."
""")

    write_file(LAYER / "async_ingestion_queue.py", """
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from .models import QueueItem


class AsyncIngestionQueue:
    def __init__(self) -> None:
        self.items: Dict[str, QueueItem] = {}

    def enqueue(self, query: str, priority: int = 5) -> QueueItem:
        item_id = "queue_" + hashlib.sha256(f"{query}|{priority}".encode("utf-8")).hexdigest()[:12]
        item = QueueItem(item_id=item_id, query=query, priority=priority)
        self.items[item_id] = item
        return item

    def next_item(self) -> Optional[QueueItem]:
        queued = [item for item in self.items.values() if item.status == "queued"]
        if not queued:
            return None
        return sorted(queued, key=lambda item: item.priority, reverse=True)[0]

    def mark_processing(self, item_id: str) -> None:
        self.items[item_id].status = "processing"
        self.items[item_id].attempts += 1

    def mark_done(self, item_id: str) -> None:
        self.items[item_id].status = "done"

    def mark_failed(self, item_id: str) -> None:
        item = self.items[item_id]
        item.status = "failed" if item.attempts >= item.max_attempts else "queued"

    def snapshot(self) -> List[dict]:
        return [item.__dict__.copy() for item in self.items.values()]
""")

    write_file(LAYER / "continuous_monitor.py", """
from __future__ import annotations

from typing import Dict, List

from .async_ingestion_queue import AsyncIngestionQueue


class ContinuousMonitor:
    def __init__(self, queue: AsyncIngestionQueue | None = None) -> None:
        self.queue = queue or AsyncIngestionQueue()

    def seed_campaign(self, topics: List[str]) -> Dict[str, object]:
        created = [self.queue.enqueue(topic, priority=5).__dict__.copy() for topic in topics]
        return {
            "status": "seeded",
            "mode": "bounded_monitoring_foundation",
            "created_items": created,
            "governance": "queued_only_no_external_fetch_without_policy",
        }

    def tick(self) -> Dict[str, object]:
        item = self.queue.next_item()
        if item is None:
            return {"status": "idle", "message": "No queued monitoring items."}

        self.queue.mark_processing(item.item_id)
        self.queue.mark_done(item.item_id)
        return {
            "status": "processed_stub",
            "item_id": item.item_id,
            "query": item.query,
            "boundary": "foundation tick only; no autonomous external action",
        }
""")

    write_file(LAYER / "signal_refresh_scheduler.py", """
from __future__ import annotations

from typing import Dict, List


class SignalRefreshScheduler:
    CADENCE_HOURS = {
        "hourly": 1,
        "daily": 24,
        "weekly": 168,
        "monthly": 720,
    }

    def build_schedule(self, watchlist_items: List[dict]) -> Dict[str, object]:
        schedule = []
        for item in watchlist_items:
            cadence = item.get("cadence", "daily")
            schedule.append(
                {
                    "watch_id": item.get("watch_id"),
                    "topic": item.get("topic"),
                    "cadence": cadence,
                    "refresh_hours": self.CADENCE_HOURS.get(cadence, 24),
                    "status": item.get("status", "active"),
                }
            )
        return {
            "status": "schedule_ready",
            "schedule": schedule,
            "boundary": "schedule contract only; external scheduling requires runtime integration",
        }
""")

    write_file(LAYER / "watchlist_engine.py", """
from __future__ import annotations

import hashlib
from typing import Dict, List

from .models import WatchlistItem


class OpportunityWatchlistEngine:
    def create_watchlist(self, opportunities: List[Dict[str, object]]) -> List[WatchlistItem]:
        items: List[WatchlistItem] = []
        for opportunity in opportunities:
            topic = str(opportunity.get("topic") or opportunity.get("title") or "untitled opportunity")
            thesis = str(opportunity.get("thesis") or opportunity.get("summary") or topic)
            watch_id = "watch_" + hashlib.sha256(f"{topic}|{thesis}".encode("utf-8")).hexdigest()[:12]
            confidence = float(opportunity.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))
            items.append(
                WatchlistItem(
                    watch_id=watch_id,
                    topic=topic,
                    thesis=thesis,
                    cadence=str(opportunity.get("cadence", "daily")),
                    confidence=confidence,
                    notes=list(opportunity.get("notes", [])),
                )
            )
        return items
""")

    write_file(LAYER / "connectivity_regression_lock.py", """
from __future__ import annotations

from typing import Dict, List


class ConnectivityRegressionLock:
    def validate(self, runtime_output: Dict[str, object]) -> Dict[str, object]:
        errors: List[str] = []
        warnings: List[str] = []

        if runtime_output.get("layer") != "governed_internet_connectivity":
            errors.append("Invalid layer name.")

        boundary = runtime_output.get("governance_boundary")
        if boundary != "no_unreviewed_external_action":
            errors.append("Governance boundary missing or invalid.")

        if "fetch" not in runtime_output:
            errors.append("Fetch contract missing.")

        if "evidence" not in runtime_output:
            errors.append("Evidence output missing.")

        fetch = runtime_output.get("fetch", {})
        if isinstance(fetch, dict) and fetch.get("status") == "review_required":
            warnings.append("Fetch requires operator review before execution.")

        return {
            "version": "v17.10",
            "regression_status": "passed" if not errors else "failed",
            "errors": errors,
            "warnings": warnings,
            "checks": {
                "source_policy_present": "source_policy" in runtime_output,
                "fetch_contract_present": "fetch" in runtime_output,
                "evidence_contract_present": "evidence" in runtime_output,
                "bounded_external_action": boundary == "no_unreviewed_external_action",
            },
        }
""")

    write_file(LAYER / "runtime.py", """
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
""")

    write_file(TESTS / "test_governed_internet_connectivity.py", """
from claire.governed_internet_connectivity import GovernedInternetRuntime, SourcePolicyEngine


def test_allowed_source_stub_research_passes_regression():
    runtime = GovernedInternetRuntime()
    result = runtime.run_research_stub(
        query="AI disclosure rules",
        source_url="https://www.sec.gov/newsroom",
        query_terms=["AI", "disclosure"],
    )

    assert result["layer"] == "governed_internet_connectivity"
    assert result["source_policy"]["decision"] == "allowed"
    assert result["fetch"]["status"] == "stubbed_success"
    assert result["regression"]["regression_status"] == "passed"
    assert result["governance_boundary"] == "no_unreviewed_external_action"


def test_unknown_source_requires_review():
    runtime = GovernedInternetRuntime()
    result = runtime.run_research_stub(
        query="unknown source test",
        source_url="https://example-random-site.invalid/report",
    )

    assert result["source_policy"]["decision"] == "review_required"
    assert result["fetch"]["status"] == "review_required"
    assert result["regression"]["regression_status"] == "passed"


def test_watchlist_schedule_contract():
    runtime = GovernedInternetRuntime()
    result = runtime.build_watchlist_schedule(
        [
            {
                "topic": "governed autonomous research systems",
                "thesis": "Demand is rising for auditable AI research infrastructure.",
                "confidence": 0.71,
                "cadence": "daily",
            }
        ]
    )

    assert len(result["watchlist"]) == 1
    assert result["schedule"]["status"] == "schedule_ready"
    assert result["governance_boundary"] == "no_unreviewed_external_action"


def test_policy_blocks_explicit_blocked_domain():
    engine = SourcePolicyEngine()
    engine.policy.blocked_domains.append("bad.example")
    decision = engine.evaluate("https://bad.example/a")
    assert decision["decision"] == "blocked"
""")

    write_file(DOCS / "v17_01_to_v17_10_governed_internet_connectivity.md", """
# Claire v17.01-v17.10 Governed Internet Connectivity Foundation

This build creates the next safe foundation for moving Claire from offline/governed discovery into governed internet-connected intelligence.

## Included Builds

- v17.01 Source Policy Engine
- v17.02 Fetch Request Engine
- v17.03 Evidence Extractor
- v17.04 Source Reliability Engine
- v17.05 Async Ingestion Queue
- v17.06 Continuous Monitor Foundation
- v17.07 Signal Refresh Scheduler
- v17.08 Opportunity Watchlist Engine
- v17.09 Governed Internet Runtime Contract
- v17.10 Connectivity Regression Lock

## Important Boundary

This is not unrestricted autonomous internet operation.

This layer creates:
- source policy
- fetch contracts
- review gates
- evidence extraction
- reliability scoring
- bounded queueing
- monitoring campaign foundation
- watchlist scheduling contracts
- regression protection

External network calls remain stubbed until a later web adapter is explicitly wired under governance.
""")

    write_json(DATA / "connectivity_manifest.json", {
        "installed_at": utc_now(),
        "layer": "governed_internet_connectivity",
        "version_range": "v17.01-v17.10",
        "status": "installed",
        "governance_boundary": "no_unreviewed_external_action",
        "capabilities": [
            "source_policy",
            "fetch_contract",
            "evidence_extraction",
            "source_reliability_scoring",
            "async_ingestion_queue",
            "continuous_monitor_foundation",
            "signal_refresh_schedule_contract",
            "opportunity_watchlists",
            "connectivity_regression_lock",
        ],
        "not_included_yet": [
            "real_network_fetching",
            "browser_automation",
            "distributed_worker_pool",
            "production_streaming_ingestion",
            "authenticated_external_actions",
            "unrestricted_autonomous_browsing",
        ],
        "tests": [
            "tests/governed_internet_connectivity/test_governed_internet_connectivity.py"
        ],
    })

    print("")
    print("INSTALL COMPLETE: Claire v17.01-v17.10 Governed Internet Connectivity Foundation")
    print("")
    print("Run tests with:")
    print("    python -m pytest tests/governed_internet_connectivity -q")
    print("")
    print("Optional smoke test:")
    print("    python -c \"from claire.governed_internet_connectivity import GovernedInternetRuntime; print(GovernedInternetRuntime().run_research_stub('AI rules','https://www.sec.gov/newsroom')['regression']['regression_status'])\"")


if __name__ == "__main__":
    main()
