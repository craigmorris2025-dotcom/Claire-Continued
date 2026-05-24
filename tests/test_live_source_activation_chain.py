from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def test_specified_live_sources_feed_promoted_evidence_into_runtime_spine(tmp_path, monkeypatch):
    connected_search = importlib.import_module("runtime_core.api.governed_connected_search")
    runtime = importlib.import_module("runtime_core.api.routes_continuous_runtime")
    app_module = importlib.import_module("runtime_core.app")

    monkeypatch.setenv("PLATFORM_SEARCH_PROVIDER", "brave")
    monkeypatch.setenv("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER", "1")
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-key")
    monkeypatch.setattr(connected_search, "project_root", lambda: tmp_path)
    monkeypatch.setattr(runtime, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(runtime, "CONTINUOUS_DIR", tmp_path / "data" / "continuous_runtime")
    monkeypatch.setattr(
        connected_search,
        "execute_provider_search",
        lambda provider, key, query, max_results: [
            {
                "title": "SEC AI governance compliance filing signal",
                "url": "https://www.sec.gov/edgar/search/",
                "snippet": f"Metadata-only result constrained by {query}.",
            }
        ],
    )

    (tmp_path / "data" / "live").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "live_intelligence").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "source_universes").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "live" / "source_registry.json").write_text("{}", encoding="utf-8")
    (tmp_path / "data" / "live_intelligence" / "latest_monitor_run.json").write_text("{}", encoding="utf-8")
    (tmp_path / "data" / "source_universes" / "universe_index.json").write_text("{}", encoding="utf-8")

    client = TestClient(app_module.create_app())
    plan = connected_search.build_specified_source_plan("AI governance compliance", ["sec.gov", "unknown.example"])
    assert plan["eligible_source_count"] == 1
    assert "site:sec.gov" in plan["query_strategy"]["provider_query"]

    search = client.post(
        "/api/search/provider/query",
        json={"query": "AI governance compliance", "source_domains": ["sec.gov", "unknown.example"]},
    ).json()
    assert search["status"] == "metadata_results_quarantined"
    assert search["source_activation"]["eligible_source_count"] == 1
    assert "site:sec.gov" in search["provider_query"]
    assert search["authority"]["body_read_performed"] is False

    promoted = client.post(
        "/api/search/evidence/promote",
        json={"confirm_text": "PROMOTE_METADATA_TO_EVIDENCE"},
    ).json()
    assert promoted["status"] == "promoted_to_evidence"
    assert promoted["promoted_count"] == 1

    cycle = runtime.create_cycle_payload(trigger="specified_live_source_test")
    current_run = runtime.read_json(runtime.CONTINUOUS_DIR / "current_run.json", {})

    assert cycle["cycle"]["candidate_counts"]["discoveries"] >= 1
    assert current_run["quality_gate"]["fresh_input_present"] is True
    assert any(
        signal.get("provenance", {}).get("origin") == "data/internet_evidence/promoted_metadata_evidence_store.json"
        for signal in current_run["signals"]
    )
    assert current_run["authority"]["body_read_performed"] is False
    assert current_run["authority"]["runtime_truth_mutated"] is False


def test_real_provider_configuration_contract_supports_brave(monkeypatch):
    contract = importlib.import_module("runtime_core.api.governed_provider_configuration_contract")

    monkeypatch.setenv("PLATFORM_SEARCH_PROVIDER", "brave")
    payload = contract.get_governed_provider_configuration_contract()

    assert payload["provider_declared"] is True
    assert payload["provider_supported"] is True
    assert any(item["id"] == "brave" and item["required_env_vars"] == ["BRAVE_SEARCH_API_KEY"] for item in payload["supported_providers"])
    assert payload["network_request"] == "blocked"
    assert payload["response_body_reads"] == "blocked"


def test_searchgov_stack_requires_affiliate_and_access_key(tmp_path, monkeypatch):
    connected_search = importlib.import_module("runtime_core.api.governed_connected_search")

    monkeypatch.setattr(connected_search, "project_root", lambda: tmp_path)
    monkeypatch.setenv("PLATFORM_SEARCH_PROVIDER", "searchgov")
    monkeypatch.setenv("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER", "1")
    monkeypatch.setenv("SEARCHGOV_ACCESS_KEY", "secret-access-key")
    monkeypatch.delenv("SEARCHGOV_AFFILIATE", raising=False)

    state = connected_search.provider_state()
    assert state["provider"] == "searchgov"
    assert state["required_key_present"] is False
    assert state["execution_allowed"] is False

    monkeypatch.setenv("SEARCHGOV_AFFILIATE", "operator-affiliate")
    state = connected_search.provider_state()
    assert state["required_key_present"] is True
    assert state["execution_allowed"] is True
