from pathlib import Path
import pytest
from claire.internet_activation.config import InternetActivationConfig
from claire.internet_activation.models import FetchResult
from claire.internet_activation.policy import InternetPolicyEngine
from claire.internet_activation.service import InternetResearchService


def test_policy_blocks_executable_extension(tmp_path: Path):
    decision=InternetPolicyEngine(InternetActivationConfig(root=tmp_path)).evaluate_url("https://www.sec.gov/file.exe")
    assert decision.decision == "blocked"


def test_policy_allows_allowlisted_domain(tmp_path: Path):
    decision=InternetPolicyEngine(InternetActivationConfig(root=tmp_path)).evaluate_url("https://www.sec.gov/newsroom")
    assert decision.decision == "allowed"


def test_policy_unknown_domain_requires_review_by_default(tmp_path: Path):
    decision=InternetPolicyEngine(InternetActivationConfig(root=tmp_path)).evaluate_url("https://example.com/report")
    assert decision.decision == "review_required"


@pytest.mark.asyncio
async def test_research_with_mocked_fetch_saves_evidence(tmp_path: Path, monkeypatch):
    service=InternetResearchService(InternetActivationConfig(root=tmp_path, data_dir=Path("data")/"internet_activation"))
    async def fake_fetch(url: str):
        return FetchResult(url=url,status="success",http_status=200,content_type="text/html",text="<html><title>SEC AI Rule</title><body>Artificial intelligence disclosure rules and governance requirements are increasing for public companies.</body></html>",binary_size=150,policy={"url_policy":{"decision":"allowed"}})
    monkeypatch.setattr(service.fetcher, "fetch", fake_fetch)
    result=await service.research("artificial intelligence disclosure rules", urls=["https://www.sec.gov/newsroom"], max_results=1)
    assert result["run"]["status"] == "completed"
    assert result["run"]["evidence_count"] == 1
    assert service.get_evidence(result["evidence"][0]["evidence_id"]) is not None


@pytest.mark.asyncio
async def test_search_not_configured_without_urls_returns_not_configured(tmp_path: Path):
    result=await InternetResearchService(InternetActivationConfig(root=tmp_path)).research("test query", urls=None, max_results=1)
    assert result["run"]["status"] == "not_configured"
    assert result["run"]["evidence_count"] == 0


@pytest.mark.asyncio
async def test_review_required_url_does_not_fetch_evidence(tmp_path: Path):
    result=await InternetResearchService(InternetActivationConfig(root=tmp_path)).research("unknown domain", urls=["https://unknown-domain-example.invalid/page"], max_results=1)
    assert result["run"]["evidence_count"] == 0
    assert result["fetch_results"][0]["status"] == "review_required"
