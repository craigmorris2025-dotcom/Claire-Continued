from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def seed_runtime(root: Path) -> None:
    write_json(
        root / "data" / "continuous_runtime" / "status.json",
        {
            "status": "active",
            "continuous_runtime_status": "configured_not_running",
            "operator_approval_required": True,
            "loop_running": False,
            "runtime_truth_mutated": False,
            "runtime_state": "requested_start",
            "last_cycle_id": "cycle_test",
        },
    )
    write_json(
        root / "data" / "continuous_runtime" / "manifest.json",
        {
            "status": "success",
            "continuous_runtime_status": "configured_not_running",
            "loop_running": False,
            "runtime_truth_mutated": False,
        },
    )
    write_json(
        root / "data" / "continuous_runtime" / "review_queue.json",
        {"items": [{"id": "review_cycle", "status": "awaiting_sources", "summary": "cycle waiting"}]},
    )
    write_json(
        root / "data" / "governed_action_queue.json",
        {"items": [{"id": "action_gate", "label": "Gate", "status": "pending_operator_approval", "risk_level": "high"}]},
    )
    write_json(
        root / "data" / "governed_review_queue.json",
        {"queue": [{"review_item_id": "review_1", "status": "pending_review", "headline": "Needs operator"}], "decisions": []},
    )
    write_json(
        root / "data" / "runtime_truth" / "runtime_state.json",
        {"state": "idle", "governance_state": "ready", "continuous_runtime": {"implemented": True}},
    )
    write_json(
        root / "data" / "runtime_truth" / "runtime_truth_consumption_report.json",
        {"status": "truth_firewall_ready", "runtime_truth_mutation_enabled": False},
    )


def seed_live_sources(root: Path) -> None:
    write_json(
        root / "data" / "source_universes" / "universe_index.json",
        {
            "status": "configured",
            "universes": [
                {"universe_id": "market_intelligence", "label": "Market Intelligence", "purpose": "Markets and SEC filings", "status": "configured"},
                {"universe_id": "technology_breakthroughs", "label": "Technology Breakthroughs", "purpose": "Technology breakthrough monitoring", "status": "configured"},
            ],
        },
    )
    write_json(
        root / "data" / "live" / "source_registry.json",
        {
            "allowed_domains": {"sec.gov": {"use_allowed": True}, "bls.gov": {"use_allowed": True}},
            "blocked_domains": {},
            "pending_review_domains": {},
        },
    )
    write_json(root / "data" / "live_sources" / "source_health_snapshot.json", {"source_count": 2, "healthy_count": 2, "live_fetch_performed": False})
    write_json(root / "data" / "internet_live_probe" / "live_probe_status.json", {"status": "BLOCKED_PROVIDER_NOT_READY"})
    write_json(root / "data" / "real_governed_live_connectivity" / "real_live_connectivity_manifest.json", {"status": "installed", "capabilities": ["governed_http_client_adapter"]})
    write_json(
        root / "data" / "live" / "approved_live_ingestion_records.json",
        [
            {
                "source_url": "https://www.sec.gov",
                "title": "SEC approved source",
                "source_evaluation": {"domain": "sec.gov", "may_score": True},
                "status": "approved_for_low_risk_ingestion",
            }
        ],
    )
    write_json(
        root / "data" / "live_intelligence" / "latest_monitor_run.json",
        {
            "summary": {"signals": 1, "clusters": 1, "gaps": 1, "live_opportunities_ready": True},
            "result": {
                "connectors": {
                    "results": [
                        {
                            "records": [
                                {
                                    "record_id": "signal_1",
                                    "entity_name": "Microsoft",
                                    "source_type": "public_regulatory",
                                    "source_url": "https://www.sec.gov/edgar/search/",
                                    "title": "Microsoft filing signal",
                                    "status": "metadata_only",
                                }
                            ]
                        }
                    ]
                }
            },
        },
    )


def test_v1957_runtime_status_reads_governed_runtime_files(tmp_path, monkeypatch):
    import runtime_core.api.operator_cockpit_runtime as runtime_routes

    seed_runtime(tmp_path)
    monkeypatch.setattr(runtime_routes, "PROJECT_ROOT", tmp_path)

    payload = runtime_routes.runtime_status_payload()

    assert payload["schema_version"] == "v19.57_operator_cockpit_runtime"
    assert payload["runtime"]["mode"] == "configured_not_running"
    assert payload["runtime"]["loop_running"] is False
    assert payload["runtime"]["operator_approval_required"] is True
    assert payload["runtime"]["runtime_truth_mutated"] is False
    assert payload["deltas"]["pending_actions"] == 1
    assert payload["deltas"]["pending_reviews"] == 2
    assert payload["deltas"]["risk_level"] == "high"
    assert payload["deltas"]["truth_firewall_status"] == "truth_firewall_ready"
    assert payload["sources"]["governed_action_queue"] == "data/governed_action_queue.json"


def test_v1957_runtime_routes_mutate_loop_state_through_operator_controls(tmp_path, monkeypatch):
    import runtime_core.api.operator_cockpit_runtime as runtime_routes
    from runtime_core.app import create_app

    seed_runtime(tmp_path)
    monkeypatch.setattr(runtime_routes, "PROJECT_ROOT", tmp_path)
    client = TestClient(create_app())

    for path in [
        "/runtime/status",
        "/runtime/loop",
        "/runtime/next",
        "/runtime/truth",
        "/runtime/gate",
        "/runtime/manifest",
        "/governed/actions",
        "/governed/decisions",
        "/governed/reviews",
    ]:
        assert client.get(path).status_code == 200, path

    started = client.post("/runtime/start", json={"operator": "test"}).json()
    assert started["runtime"]["loop_running"] is True
    assert started["runtime"]["mode"] == "running"

    stopped = client.post("/runtime/stop", json={"operator": "test"}).json()
    assert stopped["runtime"]["loop_running"] is False
    assert stopped["runtime"]["mode"] == "halted"

    for path in [
        "/runtime/approve",
        "/runtime/reject",
        "/runtime/truth/refresh",
        "/runtime/gate/trigger",
        "/runtime/safe_mode",
        "/runtime/freeze",
        "/runtime/reset",
        "/runtime/replay",
    ]:
        response = client.post(path, json={"operator": "test", "target_id": "action_gate"})
        assert response.status_code == 200, path
        payload = response.json()
        assert payload["operator_action"]["unsafe_authority_unlocked"] is False
        assert payload["operator_action"]["runtime_truth_write"] == "blocked"


def test_v1957_frontend_uses_runtime_wiring_not_endpoint_first_controls():
    html = Path("frontend/command_center/modern/platform_dashboard.html").read_text(encoding="utf-8")
    js = Path("frontend/command_center/modern/platform_dashboard.js").read_text(encoding="utf-8")

    for token in [
        'data-action="/runtime/continuous/start"',
        'data-action="/evaluate"',
        "data-prompt=",
        "Platform AI",
    ]:
        assert token in html

    assert 'fetchJson("/operator/status")' in js
    assert 'fetchJson("/api/dashboard/state")' in js
    assert "dashboardState.metrics" in js
    assert "renderBreakthroughList" in js
    assert "renderSignalList" in js
    assert "renderLiveSourceActivation" in js
    assert "renderSourceUniverseList" in js
    assert "Source Universes" in js
    for simulated in [
        "Quantum-Semantic Fusion Layer",
        "DeepMind patents autonomous reasoning layer",
        "OpenAI files 14 new patents",
        "IBM 1000q milestone",
    ]:
        assert simulated not in js
    assert "runAction" in js
    assert "renderQueue" in js
    assert "/dashboard/payload" not in html


def test_v1957_dashboard_state_adapter_exposes_backend_owned_panel_metrics(tmp_path, monkeypatch):
    import runtime_core.api.operator_cockpit_runtime as runtime_routes
    from runtime_core.dashboard.cockpit_dashboard_state import build_cockpit_dashboard_state

    seed_runtime(tmp_path)
    write_json(tmp_path / "data" / "continuous_runtime" / "portfolio_candidates.json", {"items": []})
    write_json(tmp_path / "data" / "continuous_runtime" / "breakthrough_candidates.json", {"items": []})
    write_json(tmp_path / "data" / "continuous_runtime" / "discovery_candidates.json", {"items": []})
    write_json(tmp_path / "data" / "continuous_runtime" / "design_candidates.json", {"items": []})
    write_json(tmp_path / "data" / "continuous_runtime" / "package_candidates.json", {"items": []})
    seed_live_sources(tmp_path)
    write_json(
        tmp_path / "data" / "runs" / "run_test" / "lifecycle_state.json",
        {
            "run_id": "run_test",
            "stage_count": 2,
            "stages": [
                {"stage_number": 1, "stage_name": "Signal Ingestion", "status": "initialized"},
                {"stage_number": 2, "stage_name": "Signal Normalization", "status": "waiting"},
            ],
        },
    )
    monkeypatch.setattr(runtime_routes, "PROJECT_ROOT", tmp_path)

    payload = build_cockpit_dashboard_state(tmp_path)

    assert payload["schema_version"] == "v19.89.8_cockpit_dashboard_state"
    assert payload["simulated_values_present"] is False
    assert payload["metrics"]["breakthroughs"]["value"] == 0
    assert payload["metrics"]["portfolio_items"]["value"] == 0
    assert payload["metrics"]["pending_actions"]["value"] == 1
    assert payload["metrics"]["pending_reviews"]["value"] == 2
    assert payload["metrics"]["source_universes"]["value"] == 2
    assert payload["metrics"]["allowed_sources"]["value"] == 2
    assert payload["metrics"]["catalog_sources"]["value"] == 2
    assert payload["metrics"]["latest_monitor_signals"]["value"] == 1
    assert payload["live_sources"]["connectivity_layer"] == "installed"
    assert payload["live_sources"]["probe_status"] == "BLOCKED_PROVIDER_NOT_READY"
    assert payload["live_sources"]["provider"]["live_search_enabled"] is False
    assert payload["records"]["breakthroughs"] == []
    assert len(payload["records"]["signals"]) == 2
    assert len(payload["records"]["source_universes"]) == 2
    assert payload["lifecycle"]["stage_count"] == 2
    assert payload["lifecycle"]["stages"][0]["visual_status"] == "done"


def test_v1957_cockpit_command_plan_maps_query_to_sources_and_evidence(tmp_path, monkeypatch):
    from runtime_core.dashboard.cockpit_command_plan import build_cockpit_command_plan, persist_latest_command_plan

    seed_live_sources(tmp_path)
    monkeypatch.chdir(tmp_path)

    payload = build_cockpit_command_plan("Microsoft SEC filing governance", tmp_path)
    persist_latest_command_plan(payload, tmp_path)

    assert payload["schema_version"] == "v19.89.8_cockpit_command_plan"
    assert payload["status"] == "planned"
    assert payload["authority"]["network_request_performed"] is False
    assert payload["authority"]["runtime_truth_mutation"] is False
    assert payload["provider"]["live_search_enabled"] is False
    assert payload["local_knowledge_matches"]["status"] == "ready"
    assert payload["local_knowledge_matches"]["authority"]["network_request_performed"] is False
    assert any(result["doc_id"] == "claire_governance_and_safety" for result in payload["local_knowledge_matches"]["results"])
    assert payload["source_universe_matches"]
    assert payload["evidence_preview"]
    assert (tmp_path / "data" / "operator" / "search_command" / "latest_command_plan.json").exists()


def test_v1957_cockpit_command_plan_uses_local_tech_base_for_technology_queries(tmp_path, monkeypatch):
    from runtime_core.dashboard.cockpit_command_plan import build_cockpit_command_plan

    seed_live_sources(tmp_path)
    monkeypatch.chdir(tmp_path)

    payload = build_cockpit_command_plan("autonomous invention engine technology feasibility manufacturing", tmp_path)

    knowledge = payload["local_knowledge_matches"]
    assert "technology_intelligence" in knowledge["inferred_domains"]
    assert "engineering" in knowledge["inferred_domains"]
    assert any(result["doc_id"] == "claire_technology_database" for result in knowledge["results"])
    assert knowledge["authority"]["network_request_performed"] is False


def test_v1957_cockpit_command_plan_route_persists_latest(tmp_path, monkeypatch):
    from runtime_core.app import create_app

    seed_live_sources(tmp_path)
    monkeypatch.chdir(tmp_path)
    client = TestClient(create_app())

    response = client.post("/api/cockpit/command/plan", json={"query": "Microsoft SEC filing governance"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "v19.89.8_cockpit_command_plan"
    assert payload["authority"]["provider_execution_performed"] is False
    assert payload["evidence_preview"]

    latest = client.get("/api/cockpit/command/latest")
    assert latest.status_code == 200
    assert latest.json()["query"] == "Microsoft SEC filing governance"

    history = client.get("/api/cockpit/command/history")
    assert history.status_code == 200
    history_payload = history.json()
    assert history_payload["schema_version"] == "v19.89.8_cockpit_command_history"
    assert history_payload["status"] == "ready"
    assert history_payload["items"][0]["query"] == "Microsoft SEC filing governance"
    assert history_payload["items"][0]["evidence_count"] > 0
    assert history_payload["items"][0]["local_knowledge_count"] > 0


def test_v1957_dashboard_state_routes_serve_modern_cockpit_payload():
    from runtime_core.app import create_app

    client = TestClient(create_app())

    for path in ["/api/dashboard/state", "/dashboard/state", "/operator/dashboard/state"]:
        response = client.get(path)
        assert response.status_code == 200, path
        payload = response.json()
        assert payload["schema_version"] == "v19.89.8_cockpit_dashboard_state"
        assert payload["simulated_values_present"] is False
        assert "metrics" in payload
        assert "lifecycle" in payload
        assert "command_history" in payload
        assert payload["search_lanes"]["lanes"]["research_intake"]["feeds_pipeline"] is True
        assert payload["search_lanes"]["lanes"]["platform_open"]["feeds_pipeline"] is False
