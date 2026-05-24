from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from runtime_core.config.env import legacy_env_name


def clear_platform_env(monkeypatch, *names: str) -> None:
    for name in names:
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(legacy_env_name(name), raising=False)


def test_connected_search_provider_query_uses_operator_enabled_fallback_without_enterprise_key(monkeypatch):
    import runtime_core.api.governed_connected_search as connected_search
    from runtime_core.app import create_app

    clear_platform_env(
        monkeypatch,
        "PLATFORM_SEARCH_PROVIDER",
        "PLATFORM_ALLOW_REAL_SEARCH_PROVIDER",
        "PLATFORM_ALLOW_DUCKDUCKGO_FALLBACK",
    )
    for key in [
        "BRAVE_SEARCH_API_KEY",
        "BING_SEARCH_API_KEY",
        "SERPAPI_API_KEY",
        "TAVILY_API_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(
        connected_search,
        "execute_provider_search",
        lambda provider, key, query, max_results: [
            {
                "title": "Fallback AI governance metadata",
                "url": "https://example.com/ai-governance",
                "snippet": "Metadata-only fallback result.",
            }
        ],
    )

    client = TestClient(create_app())
    response = client.post("/api/search/provider/query", json={"query": "AI governance Microsoft"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "metadata_results_quarantined"
    assert payload["provider"]["provider_used"] == "duckduckgo"
    assert payload["authority"]["network_request_performed"] is True
    assert payload["authority"]["body_read_performed"] is False
    assert payload["quarantine"]["written"] is True

    lane_config = client.get("/api/search/lane-config")
    assert lane_config.status_code == 200
    lanes = lane_config.json()["lanes"]
    assert lanes["research_intake"]["feeds_pipeline"] is True
    assert lanes["research_intake"]["quarantine_required"] is True
    assert lanes["platform_open"]["feeds_pipeline"] is False
    assert lanes["platform_open"]["scripts_removed"] is True


def test_connected_search_provider_query_quarantines_metadata_results(tmp_path, monkeypatch):
    import runtime_core.api.governed_connected_search as connected_search
    from runtime_core.app import create_app

    monkeypatch.setenv("PLATFORM_SEARCH_PROVIDER", "brave")
    monkeypatch.setenv("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER", "1")
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-key")
    monkeypatch.setattr(connected_search, "project_root", lambda: tmp_path)
    monkeypatch.setattr(
        connected_search,
        "execute_provider_search",
        lambda provider, key, query, max_results: [
            {
                "title": "Microsoft governance filing signal",
                "url": "https://www.sec.gov/edgar/search/",
                "snippet": "Metadata-only SEC search result.",
            },
            {
                "title": "Enterprise AI governance market signal",
                "url": "https://www.reuters.com/markets/",
                "snippet": "Metadata-only market result.",
            },
        ],
    )

    client = TestClient(create_app())
    response = client.post("/api/search/provider/query", json={"query": "AI governance Microsoft", "max_results": 2})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "metadata_results_quarantined"
    assert payload["authority"]["network_request_performed"] is True
    assert payload["authority"]["body_read_performed"] is False
    assert payload["authority"]["runtime_truth_write"] == "blocked"
    assert payload["quarantine"]["written"] is True
    assert len(payload["result_cards"]) == 2
    assert all(item["quarantine_state"] in {"quarantined_for_operator_review", "denied"} for item in payload["result_cards"])

    latest = tmp_path / "data" / "quarantine" / "connected_search_metadata" / "latest_search_results.json"
    assert latest.exists()
    stored = json.loads(latest.read_text(encoding="utf-8"))
    assert stored["query"] == "AI governance Microsoft"
    assert stored["authority"]["body_read_performed"] is False


def test_duckduckgo_provider_requires_explicit_fallback_enablement(tmp_path, monkeypatch):
    import runtime_core.api.governed_connected_search as connected_search
    from runtime_core.app import create_app

    monkeypatch.setenv("PLATFORM_SEARCH_PROVIDER", "duckduckgo")
    monkeypatch.setenv("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER", "1")
    clear_platform_env(monkeypatch, "PLATFORM_ALLOW_DUCKDUCKGO_FALLBACK")
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    monkeypatch.delenv("BING_SEARCH_API_KEY", raising=False)
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.setattr(connected_search, "project_root", lambda: tmp_path)
    monkeypatch.setattr(
        connected_search,
        "execute_provider_search",
        lambda provider, key, query, max_results: [
            {
                "title": "Current AI governance search result",
                "url": "https://example.com/ai-governance",
                "snippet": "Metadata-only direct web result.",
            },
        ],
    )

    client = TestClient(create_app())
    status = client.get("/api/search/provider/status")
    assert status.status_code == 200
    status_payload = status.json()
    assert status_payload["status"] == "blocked"
    assert status_payload["provider"]["required_key_name"] == ""
    assert status_payload["provider"]["required_key_present"] is False
    assert status_payload["provider"]["duckduckgo_fallback_allowed"] is False

    blocked = client.post("/api/search/provider/query", json={"query": "AI governance", "max_results": 1})
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "blocked"
    assert blocked.json()["reason"] == "provider_key_missing"

    monkeypatch.setenv("PLATFORM_ALLOW_DUCKDUCKGO_FALLBACK", "1")
    status = client.get("/api/search/provider/status")
    assert status.status_code == 200
    status_payload = status.json()
    assert status_payload["status"] == "ready"
    assert status_payload["provider"]["required_key_present"] is True
    assert status_payload["provider"]["duckduckgo_fallback_allowed"] is True

    response = client.post("/api/search/provider/query", json={"query": "AI governance", "max_results": 1})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "metadata_results_quarantined"
    assert payload["provider"]["provider"] == "duckduckgo"
    assert payload["authority"]["body_read_performed"] is False
    assert payload["result_cards"][0]["title"] == "Current AI governance search result"


def test_connected_search_provider_failure_returns_governed_error(tmp_path, monkeypatch):
    import runtime_core.api.governed_connected_search as connected_search
    from runtime_core.app import create_app

    monkeypatch.setenv("PLATFORM_SEARCH_PROVIDER", "brave")
    monkeypatch.setenv("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER", "1")
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-key")
    monkeypatch.setattr(connected_search, "project_root", lambda: tmp_path)

    def fail_provider(*args, **kwargs):
        raise TimeoutError("provider timeout")

    monkeypatch.setattr(connected_search, "execute_provider_search", fail_provider)

    client = TestClient(create_app())
    response = client.post("/api/search/provider/query", json={"query": "AI governance Microsoft"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "provider_error"
    assert payload["reason"] == "provider_request_failed"
    assert payload["authority"]["network_request_performed"] is False
    assert payload["authority"]["body_read_performed"] is False
    assert payload["quarantine"]["written"] is False


def test_promote_metadata_and_build_hybrid_result(tmp_path, monkeypatch):
    import runtime_core.api.governed_connected_search as connected_search
    from runtime_core.app import create_app

    monkeypatch.setenv("PLATFORM_SEARCH_PROVIDER", "brave")
    monkeypatch.setenv("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER", "1")
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-key")
    monkeypatch.setattr(connected_search, "project_root", lambda: tmp_path)
    monkeypatch.setattr(
        connected_search,
        "execute_provider_search",
        lambda provider, key, query, max_results: [
            {
                "title": "Microsoft AI governance SEC filing signal",
                "url": "https://www.sec.gov/edgar/search/",
                "snippet": "Enterprise AI governance and compliance risk metadata.",
            },
            {
                "title": "AI governance market compliance signal",
                "url": "https://www.reuters.com/markets/",
                "snippet": "Enterprise buyers are watching compliance automation.",
            },
        ],
    )

    client = TestClient(create_app())
    search = client.post("/api/search/provider/query", json={"query": "Microsoft AI governance compliance"})
    assert search.status_code == 200
    assert search.json()["status"] == "metadata_results_quarantined"

    blocked = client.post("/api/search/evidence/promote", json={"confirm_text": "wrong"})
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "blocked"

    promoted = client.post(
        "/api/search/evidence/promote",
        json={"confirm_text": "PROMOTE_METADATA_TO_EVIDENCE"},
    )
    assert promoted.status_code == 200
    promoted_payload = promoted.json()
    assert promoted_payload["status"] == "promoted_to_evidence"
    assert promoted_payload["promoted_count"] == 2
    assert (tmp_path / "data" / "internet_evidence" / "promoted_metadata_evidence_store.json").exists()

    result = client.post("/api/cockpit/hybrid/result", json={"query": "Microsoft AI governance compliance"})
    assert result.status_code == 200
    payload = result.json()
    assert payload["status"] == "hybrid_result_ready_for_review"
    assert payload["candidate"]["status"] == "pending_operator_review"
    assert payload["authority"]["body_read_performed"] is False
    assert payload["authority"]["runtime_truth_write"] == "blocked"
    assert (tmp_path / "data" / "continuous_runtime" / "results" / "latest_result.json").exists()

    latest = client.get("/api/cockpit/hybrid/latest")
    assert latest.status_code == 200
    assert latest.json()["candidate"]["candidate_id"] == payload["candidate"]["candidate_id"]

    review_queue = json.loads((tmp_path / "data" / "governed_review_queue.json").read_text(encoding="utf-8"))
    assert review_queue["queue"][0]["status"] == "pending_review"


def test_platform_browser_render_blocks_localhost_and_rewrites_links(monkeypatch):
    import runtime_core.api.governed_connected_search as connected_search
    from runtime_core.app import create_app

    monkeypatch.setattr(
        connected_search,
        "http_html_for_browser",
        lambda url: (
            '<!doctype html><html><head><title>Result</title></head><body>'
            '<a href="/next" target="_blank" rel="nofollow">Next</a>'
            '<a href=/l/?uddg=https%3A%2F%2Ftarget.example%2Fpage>Redirected</a>'
            '<form action="/search"><input name="q"></form>'
            '<p>This is enough readable content for the governed platform render output.</p>'
            '<script>window.top.location="https://bad.example"</script>'
            "</body></html>"
        ),
    )

    client = TestClient(create_app())
    blocked = client.get("/api/platform/browser/render", params={"url": "http://127.0.0.1:8000/health"})
    assert blocked.status_code == 400

    rendered = client.get("/api/platform/browser/render", params={"url": "https://example.com/start"})
    assert rendered.status_code == 200
    assert "Claire platform browser render" in rendered.text
    assert "<script>window.top" not in rendered.text
    assert "Result" in rendered.text
    assert "/api/platform/browser/render?url=https%3A%2F%2Fexample.com%2Fnext" in rendered.text
    assert "/api/platform/browser/render?url=https%3A%2F%2Ftarget.example%2Fpage" in rendered.text
    assert "/api/platform/browser/render?url=https%3A%2F%2Fexample.com%2Fsearch" in rendered.text
    assert "Claire loaded this page" not in rendered.text
    assert "rel=\"nofollow\"" not in rendered.text
    assert rendered.text.count("target=\"_blank\"") == 1


def test_dashboard_search_bar_calls_connected_provider_query():
    html = Path("frontend/command_center/modern/platform_dashboard.html").read_text(encoding="utf-8")
    js = Path("frontend/command_center/modern/platform_dashboard.js").read_text(encoding="utf-8")
    css = Path("frontend/command_center/modern/platform_dashboard.css").read_text(encoding="utf-8")

    assert "/api/cockpit/command/plan" in js
    assert "/api/search/provider/query" in js
    assert "connected_search" in js
    assert "No connected search results" in js
    assert "Direct Web Results" in js
    assert "Local Knowledge Base" in js
    assert "Knowledge hits" in js
    assert "local_knowledge_matches" in js
    assert "Direct web results blocked" in js
    assert "search-web-btn" in html
    assert "Web Search" in html
    assert "search-submit-btn" in html
    assert "Governed Web Results" in js
    assert "Command History" in js
    assert "RESEARCH INTAKE" in js
    assert "renderCommandHistory" in js
    assert "Research Intake" in js
    assert "Open Page" in js
    assert "buildSearchOnlyPlan" in js
    assert "Platform Web View" in js
    assert "Open in platform" in js
    assert "Open site" in js
    assert "inline-external-btn" in css
    assert "platform-browser-frame" in css
    assert "providerSearchUrl" in js
    assert "platformRenderUrl" in js
    assert "/api/platform/browser/render" in js
    assert "html.duckduckgo.com/html" in js
    assert "openExternalSearch" in js
    assert "https://www.google.com/search" in js
    assert 'src="/dashboard/assets/platform_dashboard.js"' in html


def test_main_loads_dotenv_before_creating_app():
    text = Path("main.py").read_text(encoding="utf-8")

    assert "load_dotenv" in text
    assert ".env" in text
