from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def test_portfolio_artifact_is_created_viewable_and_downloadable(tmp_path, monkeypatch):
    runtime = importlib.import_module("runtime_core.api.routes_continuous_runtime")
    artifacts = importlib.import_module("runtime_core.api.portfolio_artifacts")
    app_module = importlib.import_module("runtime_core.app")
    dashboard = importlib.import_module("runtime_core.dashboard.cockpit_dashboard_state")

    monkeypatch.setattr(runtime, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(runtime, "CONTINUOUS_DIR", tmp_path / "data" / "continuous_runtime")
    monkeypatch.setattr(artifacts, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(artifacts, "CONTINUOUS_DIR", tmp_path / "data" / "continuous_runtime")
    monkeypatch.setattr(artifacts, "PORTFOLIO_ARTIFACT_DIR", tmp_path / "data" / "continuous_runtime" / "artifacts" / "portfolio")

    for rel in [
        "data/live/source_registry.json",
        "data/source_universes/universe_index.json",
    ]:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
    monitor = tmp_path / "data/live_intelligence/latest_monitor_run.json"
    monitor.parent.mkdir(parents=True, exist_ok=True)
    monitor.write_text(
        '{"result":{"connectors":{"results":[{"source_family":"sec_public_filings","records":[{"record_id":"r1","entity_name":"Microsoft","title":"Microsoft SEC AI governance signal","snippet":"AI governance and compliance pressure metadata.","source_type":"public_regulatory"}]}]}}}',
        encoding="utf-8",
    )

    payload = runtime.create_cycle_payload(trigger="portfolio_artifact_test")
    run_id = payload["cycle"]["cycle_id"]
    artifact = payload["cycle"]["portfolio_artifact"]

    assert artifact["view_url"] == f"/portfolio/artifacts/{run_id}/view"
    assert artifact["download_url"] == f"/portfolio/artifacts/{run_id}/download"
    assert (tmp_path / "data" / "continuous_runtime" / "artifacts" / "portfolio" / run_id / "portfolio_brief.json").exists()
    assert (tmp_path / "data" / "continuous_runtime" / "artifacts" / "portfolio" / run_id / "portfolio_brief.html").exists()

    state = dashboard.build_cockpit_dashboard_state(tmp_path)
    assert state["records"]["portfolio"][0]["view_url"] == artifact["view_url"]
    assert state["records"]["portfolio"][0]["download_url"] == artifact["download_url"]

    client = TestClient(app_module.create_app())
    view = client.get(f"/portfolio/artifacts/{run_id}/view")
    download = client.get(f"/portfolio/artifacts/{run_id}/download")

    assert view.status_code == 200
    assert "Portfolio Thesis" in view.text
    assert "Executive Summary" in view.text
    assert "Market Validation & Valuation" in view.text
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("application/json")

    portfolio_payload = download.json()
    business = portfolio_payload["business_portfolio"]
    assert business["portfolio_type"] == "industry_standard_business_portfolio"
    assert business["runtime_basis"]["source"] == "30_stage_runtime"
    assert business["signal_to_portfolio_chain"]["innovation_possible"]["design_portal_required"] is True
    assert business["solution_portfolio"]["design_portal_handoff"]["required"] is True
    assert business["acquirer_strategy"]["matches"]
    assert business["market_validation"]["valuation"]["verified_current_market_value_status"] == "not_verified_without_promoted_live_market_source"
    finance = business["financial_portfolio_verification"]
    assert finance["status"] == "finance_math_verified_market_data_pending"
    assert finance["spreadsheet_checks"]["weights_sum_to_100_percent"] is True
    assert finance["spreadsheet_checks"]["weight_total_percent"] == 100.0
    assert finance["candidate_holdings"]
    assert finance["acceptance_checks"]["holdings_and_weights_traceable"] is True
    assert finance["acceptance_checks"]["market_prices_timestamped_and_verifiable"] is False
    assert business["industry_standard_readiness"]["ready_for_internal_operator_review"] is True
    assert business["industry_standard_readiness"]["ready_for_external_public_claims"] is False
