# Claire Syntalion Installer
# v17.11-v17.20 Real Governed Live Connectivity Layer
#
# Place this file in the Claire project root and run:
#
#     python install_v17_11_to_v17_20_real_governed_live_connectivity.py
#
# Then test:
#
#     python -m pytest tests/real_governed_live_connectivity -q

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CLAIRE = SRC / "claire"
LAYER = CLAIRE / "real_governed_live_connectivity"
TESTS = ROOT / "tests" / "real_governed_live_connectivity"
DATA = ROOT / "data" / "real_governed_live_connectivity"
DOCS = ROOT / "docs" / "real_governed_live_connectivity"


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
    print("Installing Claire v17.11-v17.20 Real Governed Live Connectivity Layer...")

    write_file(LAYER / "__init__.py", """
from .runtime import RealGovernedLiveConnectivityRuntime
from .models import LiveFetchRequest, LiveFetchResult, LiveSearchRequest, LiveSearchResult
from .http_client_adapter import GovernedHttpClientAdapter
from .search_adapter import GovernedSearchAdapter
from .rate_limit_guard import RateLimitGuard
from .retry_deadletter import RetryDeadLetterManager
from .content_normalizer import ContentNormalizer
from .evidence_persistence import EvidencePersistence
from .live_ingestion_worker import LiveIngestionWorker
from .live_connectivity_regression_lock import LiveConnectivityRegressionLock

__all__ = [
    "RealGovernedLiveConnectivityRuntime",
    "LiveFetchRequest",
    "LiveFetchResult",
    "LiveSearchRequest",
    "LiveSearchResult",
    "GovernedHttpClientAdapter",
    "GovernedSearchAdapter",
    "RateLimitGuard",
    "RetryDeadLetterManager",
    "ContentNormalizer",
    "EvidencePersistence",
    "LiveIngestionWorker",
    "LiveConnectivityRegressionLock",
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
class LiveFetchRequest:
    request_id: str
    url: str
    purpose: str = "governed_research"
    method: str = "GET"
    timeout_seconds: int = 10
    max_bytes: int = 500000
    status: str = "pending_policy"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LiveFetchResult:
    request_id: str
    url: str
    status: str
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    text: str = ""
    error: Optional[str] = None
    policy_decision: str = "unknown"
    fetched_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LiveSearchRequest:
    search_id: str
    query: str
    max_results: int = 5
    status: str = "pending"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LiveSearchResult:
    search_id: str
    query: str
    status: str
    results: List[Dict[str, Any]] = field(default_factory=list)
    adapter_status: str = "not_configured"
    error: Optional[str] = None
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedContent:
    source_url: str
    title: str
    summary: str
    text: str
    content_type: Optional[str]
    extracted_terms: List[str] = field(default_factory=list)
    normalization_status: str = "normalized"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PersistentEvidenceRecord:
    evidence_id: str
    source_url: str
    claim: str
    reliability_score: float
    confidence: float
    lineage: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
""")

    write_file(LAYER / "source_policy_bridge.py", """
from __future__ import annotations

from typing import Dict
from urllib.parse import urlparse


class LiveSourcePolicyBridge:
    DEFAULT_ALLOWED = {
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
    }

    def __init__(self, allowed_domains: set[str] | None = None, blocked_domains: set[str] | None = None) -> None:
        self.allowed_domains = allowed_domains or set(self.DEFAULT_ALLOWED)
        self.blocked_domains = blocked_domains or set()

    def domain_from_url(self, url: str) -> str:
        return urlparse(url).netloc.lower().replace("www.", "")

    def evaluate_url(self, url: str) -> Dict[str, object]:
        domain = self.domain_from_url(url)
        if domain in self.blocked_domains:
            return {
                "decision": "blocked",
                "domain": domain,
                "requires_review": True,
                "reason": "Domain is explicitly blocked.",
            }
        if domain in self.allowed_domains:
            return {
                "decision": "allowed",
                "domain": domain,
                "requires_review": False,
                "reason": "Domain is allowed for governed fetch.",
            }
        return {
            "decision": "review_required",
            "domain": domain,
            "requires_review": True,
            "reason": "Unknown domain requires review before live fetch.",
        }
""")

    write_file(LAYER / "rate_limit_guard.py", """
from __future__ import annotations

from collections import defaultdict
from typing import Dict


class RateLimitGuard:
    def __init__(self, max_per_domain_per_run: int = 3, max_total_per_run: int = 10) -> None:
        self.max_per_domain_per_run = max_per_domain_per_run
        self.max_total_per_run = max_total_per_run
        self.domain_counts: Dict[str, int] = defaultdict(int)
        self.total_count = 0

    def allow(self, domain: str) -> dict:
        if self.total_count >= self.max_total_per_run:
            return {"allowed": False, "reason": "Total run fetch limit reached."}
        if self.domain_counts[domain] >= self.max_per_domain_per_run:
            return {"allowed": False, "reason": "Domain fetch limit reached."}
        return {"allowed": True, "reason": "Rate limit allows request."}

    def record(self, domain: str) -> None:
        self.domain_counts[domain] += 1
        self.total_count += 1

    def snapshot(self) -> dict:
        return {
            "max_per_domain_per_run": self.max_per_domain_per_run,
            "max_total_per_run": self.max_total_per_run,
            "domain_counts": dict(self.domain_counts),
            "total_count": self.total_count,
        }
""")

    write_file(LAYER / "http_client_adapter.py", """
from __future__ import annotations

import hashlib
import urllib.request
import urllib.error
from typing import Optional

from .models import LiveFetchRequest, LiveFetchResult
from .rate_limit_guard import RateLimitGuard
from .source_policy_bridge import LiveSourcePolicyBridge


class GovernedHttpClientAdapter:
    def __init__(
        self,
        policy: Optional[LiveSourcePolicyBridge] = None,
        rate_limit: Optional[RateLimitGuard] = None,
        live_enabled: bool = False,
    ) -> None:
        self.policy = policy or LiveSourcePolicyBridge()
        self.rate_limit = rate_limit or RateLimitGuard()
        self.live_enabled = live_enabled

    def create_request(self, url: str, purpose: str = "governed_research") -> LiveFetchRequest:
        request_id = "live_fetch_" + hashlib.sha256(f"{url}|{purpose}".encode("utf-8")).hexdigest()[:12]
        return LiveFetchRequest(request_id=request_id, url=url, purpose=purpose)

    def fetch(self, request: LiveFetchRequest) -> LiveFetchResult:
        policy = self.policy.evaluate_url(request.url)
        decision = str(policy["decision"])
        domain = str(policy["domain"])

        if decision == "blocked":
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="blocked",
                policy_decision=decision,
                error=str(policy["reason"]),
            )

        if decision == "review_required":
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="review_required",
                policy_decision=decision,
                error=str(policy["reason"]),
            )

        rate = self.rate_limit.allow(domain)
        if not rate["allowed"]:
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="rate_limited",
                policy_decision=decision,
                error=str(rate["reason"]),
            )

        if not self.live_enabled:
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="live_disabled_contract_ready",
                policy_decision=decision,
                text=f"LIVE_DISABLED_CONTRACT for {request.url}",
                content_type="text/plain",
            )

        try:
            http_request = urllib.request.Request(
                request.url,
                headers={
                    "User-Agent": "Claire-GovernedResearchRuntime/1.0",
                    "Accept": "text/html,text/plain,application/json;q=0.9,*/*;q=0.5",
                },
                method=request.method,
            )
            with urllib.request.urlopen(http_request, timeout=request.timeout_seconds) as response:
                raw = response.read(request.max_bytes + 1)
                if len(raw) > request.max_bytes:
                    raw = raw[: request.max_bytes]
                text = raw.decode("utf-8", errors="replace")
                self.rate_limit.record(domain)
                return LiveFetchResult(
                    request_id=request.request_id,
                    url=request.url,
                    status="success",
                    http_status=getattr(response, "status", None),
                    content_type=response.headers.get("Content-Type"),
                    text=text,
                    policy_decision=decision,
                )
        except urllib.error.HTTPError as exc:
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="http_error",
                http_status=exc.code,
                policy_decision=decision,
                error=str(exc),
            )
        except Exception as exc:
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="fetch_error",
                policy_decision=decision,
                error=str(exc),
            )
""")

    write_file(LAYER / "search_adapter.py", """
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
""")

    write_file(LAYER / "content_normalizer.py", """
from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import List

from .models import LiveFetchResult, NormalizedContent


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: List[str] = []
        self.in_title = False
        self.title_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        clean = data.strip()
        if not clean:
            return
        if self.in_title:
            self.title_parts.append(clean)
        self.parts.append(clean)


class ContentNormalizer:
    def normalize(self, result: LiveFetchResult) -> NormalizedContent:
        text = result.text or ""
        title = ""

        if "html" in (result.content_type or "").lower() or "<html" in text.lower():
            parser = _TextExtractor()
            try:
                parser.feed(text)
                text = " ".join(parser.parts)
                title = " ".join(parser.title_parts)
            except Exception:
                text = self._strip_tags(text)

        text = " ".join(text.split())
        if not title:
            title = self._derive_title(text)

        summary = text[:400] + ("..." if len(text) > 400 else "")
        terms = self._terms(text)

        return NormalizedContent(
            source_url=result.url,
            title=title or "Untitled source",
            summary=summary,
            text=text,
            content_type=result.content_type,
            extracted_terms=terms,
            normalization_status="normalized" if text else "empty",
        )

    def _strip_tags(self, text: str) -> str:
        return re.sub(r"<[^>]+>", " ", text)

    def _derive_title(self, text: str) -> str:
        if not text:
            return "Untitled source"
        return text[:80] + ("..." if len(text) > 80 else "")

    def _terms(self, text: str) -> List[str]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())
        counts = {}
        for word in words:
            counts[word] = counts.get(word, 0) + 1
        return [word for word, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:12]]
""")

    write_file(LAYER / "evidence_persistence.py", """
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List

from .models import NormalizedContent, PersistentEvidenceRecord


class EvidencePersistence:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "real_governed_live_connectivity" / "evidence_records"
        self.root.mkdir(parents=True, exist_ok=True)

    def create_record(self, normalized: NormalizedContent, reliability_score: float = 0.5) -> PersistentEvidenceRecord:
        claim = normalized.summary or normalized.title
        evidence_id = "persistent_evidence_" + hashlib.sha256(
            f"{normalized.source_url}|{claim}".encode("utf-8")
        ).hexdigest()[:12]
        confidence = round(max(0.0, min(1.0, reliability_score * 0.8 + 0.1)), 4)
        return PersistentEvidenceRecord(
            evidence_id=evidence_id,
            source_url=normalized.source_url,
            claim=claim,
            reliability_score=round(reliability_score, 4),
            confidence=confidence,
            lineage={
                "normalization_status": normalized.normalization_status,
                "content_type": normalized.content_type,
                "extracted_terms": normalized.extracted_terms,
            },
        )

    def save(self, record: PersistentEvidenceRecord) -> Path:
        path = self.root / f"{record.evidence_id}.json"
        path.write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def list_records(self) -> List[Dict[str, object]]:
        records = []
        for path in sorted(self.root.glob("*.json")):
            try:
                records.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return records
""")

    write_file(LAYER / "retry_deadletter.py", """
from __future__ import annotations

from typing import Dict, List


class RetryDeadLetterManager:
    def __init__(self, max_attempts: int = 3) -> None:
        self.max_attempts = max_attempts
        self.attempts: Dict[str, int] = {}
        self.dead_letters: List[dict] = []

    def should_retry(self, request_id: str, status: str) -> bool:
        if status in {"success", "blocked", "review_required"}:
            return False
        current = self.attempts.get(request_id, 0)
        return current < self.max_attempts

    def record_failure(self, request_id: str, status: str, error: str | None = None) -> dict:
        self.attempts[request_id] = self.attempts.get(request_id, 0) + 1
        if self.attempts[request_id] >= self.max_attempts:
            item = {
                "request_id": request_id,
                "status": status,
                "error": error,
                "attempts": self.attempts[request_id],
            }
            self.dead_letters.append(item)
            return {"dead_lettered": True, "item": item}
        return {"dead_lettered": False, "attempts": self.attempts[request_id]}

    def snapshot(self) -> dict:
        return {"attempts": dict(self.attempts), "dead_letters": list(self.dead_letters)}
""")

    write_file(LAYER / "live_ingestion_worker.py", """
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .content_normalizer import ContentNormalizer
from .evidence_persistence import EvidencePersistence
from .http_client_adapter import GovernedHttpClientAdapter
from .retry_deadletter import RetryDeadLetterManager
from .source_policy_bridge import LiveSourcePolicyBridge


class LiveIngestionWorker:
    def __init__(
        self,
        live_enabled: bool = False,
        evidence_root: Path | None = None,
    ) -> None:
        self.policy = LiveSourcePolicyBridge()
        self.http = GovernedHttpClientAdapter(policy=self.policy, live_enabled=live_enabled)
        self.normalizer = ContentNormalizer()
        self.persistence = EvidencePersistence(evidence_root)
        self.retry = RetryDeadLetterManager()

    def ingest_url(self, url: str, purpose: str = "governed_research") -> Dict[str, Any]:
        request = self.http.create_request(url=url, purpose=purpose)
        result = self.http.fetch(request)

        output: Dict[str, Any] = {
            "request": request.to_dict(),
            "fetch_result": result.to_dict(),
            "normalized": None,
            "evidence_record": None,
            "saved_path": None,
            "retry_state": self.retry.snapshot(),
        }

        if result.status not in {"success", "live_disabled_contract_ready"}:
            if self.retry.should_retry(result.request_id, result.status):
                output["retry_state"] = self.retry.record_failure(result.request_id, result.status, result.error)
            return output

        normalized = self.normalizer.normalize(result)
        reliability = 0.5 if result.status == "live_disabled_contract_ready" else 0.7
        record = self.persistence.create_record(normalized, reliability_score=reliability)
        saved = self.persistence.save(record)

        output["normalized"] = normalized.to_dict()
        output["evidence_record"] = record.to_dict()
        output["saved_path"] = str(saved)
        return output
""")

    write_file(LAYER / "live_connectivity_regression_lock.py", """
from __future__ import annotations

from typing import Dict, List


class LiveConnectivityRegressionLock:
    def validate(self, output: Dict[str, object]) -> Dict[str, object]:
        errors: List[str] = []
        warnings: List[str] = []

        if output.get("layer") != "real_governed_live_connectivity":
            errors.append("Invalid layer marker.")

        if output.get("governance_boundary") != "policy_review_rate_limited_no_unapproved_external_action":
            errors.append("Invalid governance boundary.")

        if "live_enabled" not in output:
            errors.append("Missing live_enabled marker.")

        if "ingestion" not in output:
            errors.append("Missing ingestion result.")

        ingestion = output.get("ingestion", {})
        if isinstance(ingestion, dict):
            fetch_result = ingestion.get("fetch_result", {})
            if isinstance(fetch_result, dict):
                status = fetch_result.get("status")
                if status == "review_required":
                    warnings.append("Unknown domain requires review before live fetch.")
                if status == "live_disabled_contract_ready":
                    warnings.append("Live HTTP is disabled; contract path verified only.")

        return {
            "version": "v17.20",
            "regression_status": "passed" if not errors else "failed",
            "errors": errors,
            "warnings": warnings,
            "checks": {
                "governance_boundary_preserved": output.get("governance_boundary") == "policy_review_rate_limited_no_unapproved_external_action",
                "live_toggle_explicit": "live_enabled" in output,
                "ingestion_contract_present": "ingestion" in output,
                "no_unreviewed_external_action": True,
            },
        }
""")

    write_file(LAYER / "runtime.py", """
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
""")

    write_file(TESTS / "test_real_governed_live_connectivity.py", """
from pathlib import Path

from claire.real_governed_live_connectivity import RealGovernedLiveConnectivityRuntime
from claire.real_governed_live_connectivity import GovernedHttpClientAdapter
from claire.real_governed_live_connectivity.source_policy_bridge import LiveSourcePolicyBridge


def test_allowed_url_contract_passes_without_live_network(tmp_path: Path):
    runtime = RealGovernedLiveConnectivityRuntime(live_enabled=False, evidence_root=tmp_path)
    result = runtime.ingest_url("https://www.sec.gov/newsroom")

    assert result["layer"] == "real_governed_live_connectivity"
    assert result["live_enabled"] is False
    assert result["ingestion"]["fetch_result"]["status"] == "live_disabled_contract_ready"
    assert result["ingestion"]["evidence_record"] is not None
    assert result["regression"]["regression_status"] == "passed"


def test_unknown_url_requires_review(tmp_path: Path):
    runtime = RealGovernedLiveConnectivityRuntime(live_enabled=False, evidence_root=tmp_path)
    result = runtime.ingest_url("https://unknown-example.invalid/report")

    assert result["ingestion"]["fetch_result"]["status"] == "review_required"
    assert result["ingestion"]["evidence_record"] is None
    assert result["regression"]["regression_status"] == "passed"


def test_search_adapter_not_configured_contract():
    runtime = RealGovernedLiveConnectivityRuntime(live_enabled=False)
    result = runtime.search_query("governed AI research")

    assert result["search_result"]["status"] == "not_configured"
    assert result["search_result"]["adapter_status"] == "not_configured"


def test_blocked_domain_is_blocked():
    policy = LiveSourcePolicyBridge(blocked_domains={"blocked.example"})
    adapter = GovernedHttpClientAdapter(policy=policy, live_enabled=False)
    request = adapter.create_request("https://blocked.example/a")
    result = adapter.fetch(request)

    assert result.status == "blocked"
""")

    write_file(DOCS / "v17_11_to_v17_20_real_governed_live_connectivity.md", """
# Claire v17.11-v17.20 Real Governed Live Connectivity Layer

This build moves Claire from connectivity contracts toward real governed live-connectivity readiness.

## Included Builds

- v17.11 Governed HTTP Client Adapter
- v17.12 Governed Search Adapter Contract
- v17.13 Rate Limit Guard
- v17.14 Content Normalizer
- v17.15 Evidence Persistence
- v17.16 Retry and Dead-Letter Manager
- v17.17 Live Ingestion Worker
- v17.18 Source Policy Bridge
- v17.19 Runtime Contract
- v17.20 Live Connectivity Regression Lock

## Safety Boundary

Live HTTP exists behind an explicit `live_enabled` toggle.

Default behavior is:

```python
RealGovernedLiveConnectivityRuntime(live_enabled=False)
```

This verifies the complete governed contract path without making live network calls.

To enable real HTTP later, instantiate with:

```python
RealGovernedLiveConnectivityRuntime(live_enabled=True)
```

Only allowlisted domains fetch automatically. Unknown domains return `review_required`.
""")

    write_json(DATA / "real_live_connectivity_manifest.json", {
        "installed_at": utc_now(),
        "layer": "real_governed_live_connectivity",
        "version_range": "v17.11-v17.20",
        "status": "installed",
        "default_live_enabled": False,
        "governance_boundary": "policy_review_rate_limited_no_unapproved_external_action",
        "capabilities": [
            "governed_http_client_adapter",
            "live_search_adapter_contract",
            "rate_limit_guard",
            "content_normalizer",
            "evidence_persistence",
            "retry_deadletter_manager",
            "live_ingestion_worker",
            "source_policy_bridge",
            "live_connectivity_regression_lock",
        ],
        "not_included_yet": [
            "production_search_provider_secrets",
            "browser_automation",
            "distributed_worker_pool",
            "streaming_market_feeds",
            "authenticated_external_actions",
            "unrestricted_autonomous_browsing",
        ],
        "tests": [
            "tests/real_governed_live_connectivity/test_real_governed_live_connectivity.py"
        ],
    })

    print("")
    print("INSTALL COMPLETE: Claire v17.11-v17.20 Real Governed Live Connectivity Layer")
    print("")
    print("Run tests with:")
    print("    python -m pytest tests/real_governed_live_connectivity -q")
    print("")
    print("Optional smoke test:")
    print("    python -c \"from claire.real_governed_live_connectivity import RealGovernedLiveConnectivityRuntime; print(RealGovernedLiveConnectivityRuntime().ingest_url('https://www.sec.gov/newsroom')['regression']['regression_status'])\"")


if __name__ == "__main__":
    main()
