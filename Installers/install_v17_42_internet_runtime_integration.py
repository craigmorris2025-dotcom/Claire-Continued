# Claire Syntalion Installer
# v17.42 Internet Runtime Integration
#
# Place this file in Claire project root and run:
#     python install_v17_42_internet_runtime_integration.py
# Then test:
#     python -m pytest tests/internet_runtime_integration -q

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
LAYER = ROOT / "src" / "claire" / "internet_runtime_integration"
TESTS = ROOT / "tests" / "internet_runtime_integration"
DATA = ROOT / "data" / "internet_runtime_integration"
DOCS = ROOT / "docs" / "internet_runtime_integration"


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
    print("Installing Claire v17.42 Internet Runtime Integration...")

    write_file(LAYER / "__init__.py", '''
from .bridge import InternetRuntimeBridge
from .lifecycle_adapter import InternetLifecycleAdapter
from .output_merger import CoreRunOutputInternetMerger
from .evidence_continuity import InternetEvidenceContinuityStore
from .dashboard_payload import InternetDashboardPayloadBuilder
from .integration_service import InternetRuntimeIntegrationService

__all__ = [
    "InternetRuntimeBridge",
    "InternetLifecycleAdapter",
    "CoreRunOutputInternetMerger",
    "InternetEvidenceContinuityStore",
    "InternetDashboardPayloadBuilder",
    "InternetRuntimeIntegrationService",
]
''')

    write_file(LAYER / "models.py", '''
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class InternetRuntimeRequest:
    query: str
    run_id: Optional[str] = None
    urls: Optional[List[str]] = None
    max_results: Optional[int] = None
    attach_to_core_output: bool = True
    lifecycle_stage: str = "research"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InternetEvidenceLink:
    evidence_id: str
    run_id: str
    query: str
    source_url: str
    source_domain: str
    confidence: float
    source_reliability: float
    lifecycle_stage: str = "research"
    linked_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeInternetSummary:
    run_id: str
    query: str
    internet_status: str
    searched: bool
    fetched_count: int
    evidence_count: int
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
''')

    write_file(LAYER / "evidence_continuity.py", '''
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .models import InternetEvidenceLink, utc_now


class InternetEvidenceContinuityStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "internet_runtime_integration"
        self.links_dir = self.root / "evidence_links"
        self.index_path = self.root / "internet_evidence_index.json"
        self.links_dir.mkdir(parents=True, exist_ok=True)

    def link_evidence(self, run_id: str, query: str, evidence: Dict[str, Any], lifecycle_stage: str = "research") -> InternetEvidenceLink:
        link = InternetEvidenceLink(
            evidence_id=str(evidence.get("evidence_id")),
            run_id=run_id,
            query=query,
            source_url=str(evidence.get("source_url", "")),
            source_domain=str(evidence.get("source_domain", "")),
            confidence=float(evidence.get("confidence", 0.0)),
            source_reliability=float(evidence.get("source_reliability", 0.0)),
            lifecycle_stage=lifecycle_stage,
        )
        self.save_link(link)
        return link

    def save_link(self, link: InternetEvidenceLink) -> Path:
        path = self.links_dir / f"{link.run_id}_{link.evidence_id}.json"
        path.write_text(json.dumps(link.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        self._update_index(link)
        return path

    def _update_index(self, link: InternetEvidenceLink) -> None:
        index = self.load_index()
        index.setdefault("runs", {})
        bucket = index["runs"].setdefault(link.run_id, {"evidence_ids": [], "queries": []})
        if link.evidence_id not in bucket["evidence_ids"]:
            bucket["evidence_ids"].append(link.evidence_id)
        if link.query not in bucket["queries"]:
            bucket["queries"].append(link.query)
        index["updated_at"] = utc_now()
        self.index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")

    def load_index(self) -> Dict[str, Any]:
        if not self.index_path.exists():
            return {"created_at": utc_now(), "runs": {}}
        return json.loads(self.index_path.read_text(encoding="utf-8"))

    def links_for_run(self, run_id: str) -> List[Dict[str, Any]]:
        links: List[Dict[str, Any]] = []
        for path in sorted(self.links_dir.glob(f"{run_id}_*.json")):
            try:
                links.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return links
''')

    write_file(LAYER / "bridge.py", '''
from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from claire.internet_activation import InternetResearchService
from claire.internet_activation.config import InternetActivationConfig

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
''')

    write_file(LAYER / "output_merger.py", '''
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class CoreRunOutputInternetMerger:
    def merge_dict(self, core_output: Dict[str, Any], internet_output: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(core_output)
        internet_summary = internet_output.get("internet_summary", {})
        evidence_links = internet_output.get("evidence_links", [])
        merged["internet_research"] = {
            "status": internet_summary.get("internet_status"),
            "summary": internet_summary,
            "evidence_links": evidence_links,
            "activation_result": internet_output.get("internet_activation_result", {}),
        }
        merged.setdefault("evidence", {})
        if isinstance(merged["evidence"], dict):
            merged["evidence"].setdefault("internet", []).extend(evidence_links)
        merged.setdefault("runtime_capabilities", {})
        if isinstance(merged["runtime_capabilities"], dict):
            merged["runtime_capabilities"]["internet_research"] = True
        return merged

    def merge_file(self, core_output_path: Path, internet_output: Dict[str, Any], write_back: bool = True) -> Dict[str, Any]:
        if core_output_path.exists():
            core_output = json.loads(core_output_path.read_text(encoding="utf-8"))
        else:
            core_output = {"status": "created_by_internet_runtime_integration", "note": "core_run_output file did not exist before merge"}
        merged = self.merge_dict(core_output, internet_output)
        if write_back:
            core_output_path.parent.mkdir(parents=True, exist_ok=True)
            core_output_path.write_text(json.dumps(merged, indent=2, sort_keys=True), encoding="utf-8")
        return merged
''')

    write_file(LAYER / "lifecycle_adapter.py", '''
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
''')

    write_file(LAYER / "dashboard_payload.py", '''
from __future__ import annotations

from typing import Any, Dict, List


class InternetDashboardPayloadBuilder:
    def build(self, internet_output: Dict[str, Any]) -> Dict[str, Any]:
        activation = internet_output.get("internet_activation_result", {})
        summary = internet_output.get("internet_summary", {})
        return {
            "panel": "internet_research",
            "title": "Internet Research",
            "status": summary.get("internet_status", "unknown"),
            "query": summary.get("query"),
            "searched": summary.get("searched", False),
            "fetched_count": summary.get("fetched_count", 0),
            "evidence_count": summary.get("evidence_count", 0),
            "warnings": summary.get("warnings", []),
            "errors": summary.get("errors", []),
            "sources": self._sources(activation.get("search_results", []), activation.get("fetch_results", [])),
            "evidence": activation.get("evidence", []),
            "evidence_links": internet_output.get("evidence_links", []),
            "governance": activation.get("governance", {}),
        }

    def _sources(self, searches: List[Dict[str, Any]], fetches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_url: Dict[str, Dict[str, Any]] = {}
        for item in searches:
            url = item.get("url")
            if url:
                by_url[url] = {"url": url, "title": item.get("title", ""), "snippet": item.get("snippet", ""), "search_source": item.get("source", ""), "rank": item.get("rank", 0), "fetch_status": None}
        for fetch in fetches:
            url = fetch.get("url")
            if not url:
                continue
            by_url.setdefault(url, {"url": url})
            by_url[url]["fetch_status"] = fetch.get("status")
            by_url[url]["http_status"] = fetch.get("http_status")
            by_url[url]["content_type"] = fetch.get("content_type")
            by_url[url]["error"] = fetch.get("error")
        return list(by_url.values())
''')

    write_file(LAYER / "integration_service.py", '''
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
''')

    write_file(LAYER / "api_routes.py", '''
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .integration_service import InternetRuntimeIntegrationService


router = APIRouter(prefix="/runtime/internet", tags=["Internet Runtime Integration"])


class RuntimeInternetRequest(BaseModel):
    query: str = Field(..., min_length=1)
    run_id: str = Field(..., min_length=1)
    lifecycle_stage: str = "research"
    urls: Optional[List[str]] = None
    max_results: Optional[int] = Field(default=None, ge=1, le=20)
    core_output_path: Optional[str] = None


@router.post("/enrich")
async def enrich_runtime_with_internet(request: RuntimeInternetRequest):
    service = InternetRuntimeIntegrationService()
    try:
        path = Path(request.core_output_path) if request.core_output_path else None
        return await service.run_and_build_dashboard(query=request.query, run_id=request.run_id, lifecycle_stage=request.lifecycle_stage, urls=request.urls, max_results=request.max_results, core_output_path=path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/dashboard")
async def build_runtime_internet_dashboard(request: RuntimeInternetRequest):
    service = InternetRuntimeIntegrationService()
    result = await service.run_and_build_dashboard(query=request.query, run_id=request.run_id, lifecycle_stage=request.lifecycle_stage, urls=request.urls, max_results=request.max_results)
    return result["dashboard_payload"]
''')

    write_file(TESTS / "test_internet_runtime_integration.py", '''
from pathlib import Path

import pytest

from claire.internet_runtime_integration import InternetLifecycleAdapter
from claire.internet_runtime_integration.bridge import InternetRuntimeBridge
from claire.internet_runtime_integration.dashboard_payload import InternetDashboardPayloadBuilder
from claire.internet_runtime_integration.evidence_continuity import InternetEvidenceContinuityStore
from claire.internet_runtime_integration.models import InternetRuntimeRequest
from claire.internet_runtime_integration.output_merger import CoreRunOutputInternetMerger


class FakeResearchService:
    async def research(self, query, urls=None, max_results=None):
        return {
            "layer": "internet_activation",
            "version": "v17.41",
            "run": {"run_id": "internet_run_fake", "query": query, "status": "completed", "searched": False, "fetched_count": 1, "evidence_count": 1, "warnings": [], "errors": [], "evidence_ids": ["ev_fake"]},
            "search_results": [{"title": "SEC", "url": "https://www.sec.gov/newsroom", "snippet": "", "source": "direct_url", "rank": 1}],
            "fetch_results": [{"url": "https://www.sec.gov/newsroom", "status": "success", "http_status": 200, "content_type": "text/html"}],
            "evidence": [{"evidence_id": "ev_fake", "run_id": "internet_run_fake", "query": query, "source_url": "https://www.sec.gov/newsroom", "title": "SEC", "claim": "AI disclosure governance is increasing.", "summary": "AI disclosure governance is increasing.", "source_domain": "sec.gov", "source_reliability": 0.96, "confidence": 0.88}],
            "governance": {"max_results": 1},
        }


@pytest.mark.asyncio
async def test_bridge_links_evidence(tmp_path: Path):
    bridge = InternetRuntimeBridge(data_root=tmp_path, research_service=FakeResearchService(), continuity_store=InternetEvidenceContinuityStore(tmp_path))
    result = await bridge.run_research(InternetRuntimeRequest(query="AI disclosure", run_id="core_run_1", urls=["https://www.sec.gov/newsroom"], max_results=1, lifecycle_stage="discovery"))
    assert result["internet_summary"]["evidence_count"] == 1
    assert result["evidence_links"][0]["run_id"] == "core_run_1"
    assert result["evidence_links"][0]["source_domain"] == "sec.gov"


def test_output_merger_adds_internet_research_section():
    merger = CoreRunOutputInternetMerger()
    merged = merger.merge_dict({"run_id": "core_run_1", "evidence": {}}, {"internet_summary": {"internet_status": "completed", "evidence_count": 1}, "evidence_links": [{"evidence_id": "ev_fake"}], "internet_activation_result": {"run": {"status": "completed"}}})
    assert merged["runtime_capabilities"]["internet_research"] is True
    assert merged["internet_research"]["status"] == "completed"
    assert merged["evidence"]["internet"][0]["evidence_id"] == "ev_fake"


@pytest.mark.asyncio
async def test_lifecycle_adapter_merges_core_output(tmp_path: Path):
    bridge = InternetRuntimeBridge(data_root=tmp_path, research_service=FakeResearchService(), continuity_store=InternetEvidenceContinuityStore(tmp_path))
    adapter = InternetLifecycleAdapter(bridge=bridge)
    result = await adapter.enrich_lifecycle_run(query="AI disclosure", run_id="core_run_2", lifecycle_stage="thesis", urls=["https://www.sec.gov/newsroom"], max_results=1, core_output={"run_id": "core_run_2", "status": "existing"})
    assert result["merged_output"]["internet_research"]["summary"]["evidence_count"] == 1
    assert result["merged_output"]["runtime_capabilities"]["internet_research"] is True


def test_dashboard_payload_builder():
    builder = InternetDashboardPayloadBuilder()
    payload = builder.build({"internet_summary": {"internet_status": "completed", "query": "AI disclosure", "searched": False, "fetched_count": 1, "evidence_count": 1, "warnings": [], "errors": []}, "internet_activation_result": {"search_results": [{"title": "SEC", "url": "https://www.sec.gov/newsroom", "source": "direct_url", "rank": 1}], "fetch_results": [{"url": "https://www.sec.gov/newsroom", "status": "success", "http_status": 200}], "evidence": [{"evidence_id": "ev_fake"}], "governance": {"max_results": 1}}, "evidence_links": [{"evidence_id": "ev_fake"}]})
    assert payload["panel"] == "internet_research"
    assert payload["status"] == "completed"
    assert payload["sources"][0]["fetch_status"] == "success"
''')

    write_file(TESTS / "test_internet_runtime_integration_api.py", '''
from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.internet_runtime_integration import api_routes
from claire.internet_runtime_integration.integration_service import InternetRuntimeIntegrationService


def test_runtime_internet_dashboard_route(monkeypatch):
    app = FastAPI()
    app.include_router(api_routes.router)

    async def fake_run_and_build_dashboard(self, query, run_id, lifecycle_stage="research", urls=None, max_results=None, core_output_path=None):
        return {"dashboard_payload": {"panel": "internet_research", "status": "completed", "query": query, "evidence_count": 1}}

    monkeypatch.setattr(InternetRuntimeIntegrationService, "run_and_build_dashboard", fake_run_and_build_dashboard)
    client = TestClient(app)
    response = client.post("/runtime/internet/dashboard", json={"query": "AI disclosure", "run_id": "core_run_api", "urls": ["https://www.sec.gov/newsroom"], "max_results": 1})
    assert response.status_code == 200
    assert response.json()["panel"] == "internet_research"
    assert response.json()["evidence_count"] == 1
''')

    write_file(DOCS / "v17_42_internet_runtime_integration.md", '''
# Claire v17.42 — Internet Runtime Integration

This package integrates the working v17.41 internet activation core into Claire runtime outputs.

## Adds

- InternetRuntimeBridge
- InternetLifecycleAdapter
- CoreRunOutputInternetMerger
- InternetEvidenceContinuityStore
- InternetDashboardPayloadBuilder
- InternetRuntimeIntegrationService
- FastAPI routes: POST /runtime/internet/enrich and POST /runtime/internet/dashboard

## Boundary

This package does not rewrite unknown dashboard component files automatically.
It provides a stable dashboard payload for the Research tab to consume.
It does not perform unrestricted browsing. It uses the v17.41 governed internet service.
''')

    write_json(DATA / "internet_runtime_integration_manifest.json", {
        "installed_at": utc_now(),
        "layer": "internet_runtime_integration",
        "version": "v17.42",
        "status": "installed",
        "requires": ["claire.internet_activation"],
        "capabilities": ["runtime_bridge_to_v17_41", "lifecycle_adapter", "core_run_output_merger", "evidence_continuity_links", "dashboard_payload_builder", "fastapi_runtime_routes", "integration_tests"],
        "governance_boundary": "uses_v17_41_governed_internet_activation_no_unrestricted_browsing",
    })

    print("\nINSTALL COMPLETE: Claire v17.42 Internet Runtime Integration")
    print("\nRun tests with:")
    print("    python -m pytest tests/internet_runtime_integration -q")
    print("\nOptional route wiring:")
    print("    from claire.internet_runtime_integration.api_routes import router as internet_runtime_router")
    print("    app.include_router(internet_runtime_router)")


if __name__ == "__main__":
    main()
