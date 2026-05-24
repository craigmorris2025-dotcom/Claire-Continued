from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_technology_base_search_filters_reality_based_records():
    from runtime_core.technology.technology_base import assess_technology_base, search_technology_base

    search = search_technology_base("autonomous invention engine feasible manufacturing")
    assert search["status"] == "ready"
    assert search["authority"]["network_request_performed"] is False
    assert search["results"]
    assert search["record_count"] > 6
    assert search["current_buildable_count"] > 6
    assert search["viewpoint_contract"]["runtime_output_echo_allowed"] is False
    assert search["viewpoint_contract"]["source_of_truth"] == "operator_supplied_technology_database_and_timeline_docs"
    assert search["innovation_candidates"]
    assert search["technology_lineage"]["lineage_depth"] >= 8
    assert search["historical_trend_math"]["singularity_math_ready"] is True
    assert search["acs2_transformation_diagram"]["status"] == "ready"
    assert search["predictive_trend_engine"]["status"] == "ready"
    assert all(item["manufacturability"] != "science_fiction" for item in search["results"])

    assessment = assess_technology_base("autonomous invention engine feasible manufacturing")
    assert assessment["status"] == "operational"
    assert assessment["readiness"]["current_technology_grounded"] is True
    assert assessment["readiness"]["science_fiction_filtered"] is True
    assert assessment["viewpoint_contract"]["latest_run_output_primary_source"] is False
    assert assessment["counts"]["evidence_sources"] >= 1
    assert assessment["counts"]["breakthrough_ready_candidates"] >= 1
    assert assessment["counts"]["lineage_edges"] >= 8
    assert assessment["counts"]["lineage_families"] >= 8
    assert assessment["reasoning_capabilities"]["beginning_to_end_lineage"] is True
    assert assessment["reasoning_capabilities"]["historical_linear_spine"] is True
    assert assessment["reasoning_capabilities"]["singularity_math_scaffold"] is True
    assert assessment["reasoning_capabilities"]["acs2_transformation_diagram"] is True
    assert assessment["reasoning_capabilities"]["predictive_trend_engine"] is True
    assert "technical_feasibility" in assessment["next_pipeline_bindings"]
    assert "breakthrough_design" in assessment["next_pipeline_bindings"]


def test_technology_base_tracks_what_became_what_to_autonomous_invention():
    from runtime_core.technology.technology_base import assess_technology_base

    assessment = assess_technology_base("calculator computation internet ai autonomous invention singularity")
    lineage = assessment["technology_lineage"]
    trend_math = assessment["historical_trend_math"]
    edge_chain = [(edge["from_id"], edge["to_id"]) for edge in lineage["edges"]]

    assert ("mechanical_calculator", "programmable_computation") in edge_chain
    assert ("autonomous_agent_orchestration", "autonomous_invention_engine_loop") in edge_chain
    assert any("became" in edge["relationship"] for edge in lineage["edges"])
    assert trend_math["status"] == "ready"
    assert trend_math["historical_linear_spine"]
    assert trend_math["interval_statistics"]["compression_ratio"] > 1
    assert trend_math["projection"]["projected_next_inflection_year"] >= 2026


def test_technology_base_connects_parallel_device_evolution_families():
    from runtime_core.technology.technology_base import assess_technology_base

    assessment = assess_technology_base("car phone mobile phone portable tv tablet apple ii laptop")
    lineage = assessment["technology_lineage"]
    diagram = assessment["acs2_transformation_diagram"]
    edge_chain = {(edge["from_id"], edge["to_id"]) for edge in lineage["edges"]}
    family_names = {item["family"] for item in diagram["family_views"]}
    convergence_nodes = {item["node_id"] for item in diagram["convergence_points"]}
    pattern_names = {item["pattern"] for item in lineage["transformation_patterns"]}

    assert ("car_phone", "mobile_phone") in edge_chain
    assert ("battery_portable_tv", "portable_media_player") in edge_chain
    assert ("portable_media_player", "tablet") in edge_chain
    assert ("apple_ii", "portable_computer") in edge_chain
    assert ("portable_computer", "laptop") in edge_chain
    assert {"communications_portability", "portable_visual_media", "personal_compute_portability"} <= family_names
    assert "tablet" in convergence_nodes
    assert {"miniaturization", "battery_power", "convergence", "network_access"} <= pattern_names


def test_technology_base_contains_many_cross_family_transformation_patterns():
    from runtime_core.technology.technology_base import assess_technology_base

    assessment = assess_technology_base("camera maps music payments books messages watches cars medical records")
    lineage = assessment["technology_lineage"]
    diagram = assessment["acs2_transformation_diagram"]

    assert lineage["lineage_depth"] >= 140
    assert lineage["family_count"] >= 45
    assert len(lineage["transformation_patterns"]) >= 40
    assert diagram["convergence_points"]
    assert any(item["family"] == "vehicle_autonomy" for item in diagram["family_views"])
    assert any(item["family"] == "health_record_digitization" for item in diagram["family_views"])


def test_predictive_trend_engine_uses_acs2_patterns_for_analogies():
    from runtime_core.technology.technology_base import assess_technology_base

    assessment = assess_technology_base("manual appliance sensor autonomous ai prediction")
    engine = assessment["predictive_trend_engine"]
    patterns = {item["pattern"] for item in engine["pattern_priorities"]}
    hypotheses = " ".join(item["hypothesis"] for item in engine["predictive_hypotheses"]).lower()

    assert engine["status"] == "ready"
    assert engine["prediction_readiness"] == "foundation_ready_for_operator_review"
    assert {"sensorization", "automation", "network_access", "digitization"} <= patterns
    assert "autonomous" in hypotheses
    assert engine["query_matched_analogies"]
    assert engine["safety_note"]


def test_technology_intelligence_uses_internal_technology_base():
    from runtime_core.technology.technology_intelligence import TechnologyIntelligenceLayer

    payload = TechnologyIntelligenceLayer().analyze(
        {"domain": "technology", "route": "design", "keywords": ["autonomous", "invention", "engine"]}
    )
    assert payload["mode"] == "internal_technology_base"
    assert payload["technology_base"]["status"] == "operational"
    assert payload["technologies_considered"]
    assert payload["innovation_candidates"]
    assert payload["top_innovation_candidate"]["buildability_score"] >= 0.6
    assert payload["confidence"] >= 0.78


def test_technology_base_routes_and_dashboard_state_are_mounted():
    from runtime_core.app import create_app

    client = TestClient(create_app())

    for path in ["/api/technology/base", "/api/technology/search", "/api/technology/intelligence"]:
        response = client.get(path, params={"query": "autonomous invention engine"})
        assert response.status_code == 200, path
        assert response.json()["status"] in {"ready", "operational", "available"}

    dashboard = client.get("/api/dashboard/state").json()
    assert dashboard["technology_base"]["status"] == "operational"
    assert dashboard["metrics"]["technology_records"]["value"] >= 1
    assert dashboard["metrics"]["technology_innovation_candidates"]["value"] >= 1
    assert dashboard["metrics"]["technology_breakthrough_ready"]["value"] >= 1
    assert dashboard["records"]["technology"]
    assert dashboard["records"]["technology_innovation_candidates"]


def test_pipeline_source_authority_keeps_live_sources_as_scoring_owner():
    from runtime_core.domain.contract import ClaireIntent
    from runtime_core.orchestrator.pipeline_v4 import PipelineOrchestrator

    authority = PipelineOrchestrator()._build_source_authority(
        intent=ClaireIntent(
            raw_input="connected_signal_stream",
            mode="deterministic",
            source_mode="live_source_packet",
            sources={"patent": {"metrics": {"activity": 0.82, "novelty": 0.76}}},
        ),
        request_sources={"patent": {"metrics": {"activity": 0.82, "novelty": 0.76}}},
        external={"patent": {"activity": 0.82, "novelty": 0.76}},
        source_count=1,
        source_quality_score=0.8,
        coverage_score=0.72,
        evidence_signal_score=0.74,
        market_growth=0.55,
        patent_activity=0.82,
        patent_novelty=0.76,
    )

    assert authority["trend_freshness_owner"] == "live_sources"
    assert authority["discovery_scoring_owner"] == "live_signal_engines_and_connector_sources"
    assert authority["breakthrough_scoring_owner"] == "live_signal_engines_and_connector_sources"
    assert authority["internal_reference_role"] == "blocked_from_runtime_evidence"
    assert "local_technology_database_role" not in authority
    assert authority["local_prior_can_seed_candidate"] is False
    assert authority["local_prior_can_promote_breakthrough_without_live_validation"] is False
    assert authority["runtime_output_echo_allowed"] is False


def test_pipeline_source_authority_labels_local_sources_pending_live_validation():
    from runtime_core.domain.contract import ClaireIntent
    from runtime_core.orchestrator.pipeline_v4 import PipelineOrchestrator

    authority = PipelineOrchestrator()._build_source_authority(
        intent=ClaireIntent(
            raw_input="autonomous invention engine",
            mode="deterministic",
            source_mode="local_technology_seed",
            sources={"technology": {"metrics": {"activity": 0.72}}},
        ),
        request_sources={"technology": {"metrics": {"activity": 0.72}}},
        external={"technology": {"activity": 0.72}},
        source_count=0,
        source_quality_score=0.7,
        coverage_score=0.65,
        evidence_signal_score=0.62,
        market_growth=0.5,
        patent_activity=0.72,
        patent_novelty=0.68,
    )

    assert authority["source_evidence_present"] is True
    assert authority["live_evidence_present"] is False
    assert authority["effective_source_count"] == 1
    assert authority["trend_freshness_owner"] == "local_operator_sources_pending_live_validation"


def test_pipeline_runtime_blocks_internal_technology_base_as_evidence():
    from runtime_core.domain.contract import ClaireIntent
    from runtime_core.orchestrator.pipeline_v4 import PipelineOrchestrator

    class FailingTechnologyIntelligence:
        def analyze(self, _context):
            raise AssertionError("internal technology base must not run inside runtime evidence path")

    class NoopExportWriter:
        def write(self, **_kwargs):
            return {
                "status": "skipped_in_test",
                "export_writer_score": {"score": 1.0, "level": "test"},
                "output_dir": None,
                "written_file_count": 0,
            }

    orchestrator = PipelineOrchestrator()
    orchestrator.technology_intelligence = FailingTechnologyIntelligence()
    orchestrator.export_writer = NoopExportWriter()

    result = orchestrator.execute(
        ClaireIntent(
            raw_input="connected_signal_stream",
            mode="deterministic",
            source_mode="live_source_packet",
            sources={
                "market": {
                    "source": "https://www.sec.gov/edgar/search/",
                    "growth": 0.12,
                    "signals": ["AI governance demand", "enterprise compliance pressure"],
                },
                "patent": {
                    "source": "https://www.uspto.gov/patents/search",
                    "activity": 0.58,
                    "novelty": 0.42,
                },
            },
        )
    ).to_dict()

    authority = result["source_authority"]
    technology = result["technology_intelligence"]

    assert result["source_boundary"]["status"] == "enforced"
    assert "local_technology_database" not in authority
    assert authority["local_prior_can_seed_candidate"] is False
    assert technology["status"] == "blocked_internal_system_zone"
    assert technology["mode"] == "runtime_evidence_blocked"
    assert "technology_base" not in technology


def test_dashboard_exposes_technology_base_section():
    js = Path("frontend/command_center/modern/platform_dashboard.js").read_text(encoding="utf-8")

    assert "Tech Base" in js
    assert "renderTechnology" in js
    assert "technology_base" in js
    assert "Reality Filter" in js
    assert "Manufacturable" in js
