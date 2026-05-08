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
