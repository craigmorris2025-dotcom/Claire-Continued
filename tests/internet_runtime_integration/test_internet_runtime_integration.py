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
