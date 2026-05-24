from __future__ import annotations


def test_signal_timeseries_store_and_pattern_engine_use_historical_signal_movement():
    from runtime_core.signals.signal_timeseries_store import default_signal_timeseries_store
    from runtime_core.technology.reemergence_pattern_engine import ReemergencePatternEngine

    store = default_signal_timeseries_store()
    readiness = ReemergencePatternEngine(store).compute_readiness("ev_market")

    assert readiness["status"] == "ready"
    assert readiness["series_count"] >= 3
    assert readiness["readiness_score"] > 0.5
    assert readiness["detected_patterns"]
    assert any(item["pattern_id"] in {"technology_catch_up", "infrastructure_catch_up"} for item in readiness["pattern_scores"])


def test_threshold_learner_updates_pattern_thresholds_from_positive_cases():
    from runtime_core.signals.signal_timeseries_store import default_signal_timeseries_store
    from runtime_core.technology.reemergence_pattern_engine import pattern_objects
    from runtime_core.technology.reemergence_threshold_learner import ReemergenceThresholdLearner

    store = default_signal_timeseries_store()
    pattern = next(item for item in pattern_objects() if item.pattern_id == "technology_catch_up")
    learned = ReemergenceThresholdLearner(store).fit_pattern(pattern, ["ev_market", "tablet_market"])

    assert any(req.learned_threshold is not None for req in learned.required_changes)


def test_acs2_graph_has_required_mass_and_data_driven_shape():
    from runtime_core.technology.technology_base import assess_technology_base, get_acs2_graph

    assessment = assess_technology_base("smartphone")
    graph = get_acs2_graph("smartphone")

    assert assessment["technology_lineage"]["acs2_diagram"]["node_count"] >= 500
    assert graph["node_count"] >= 500
    assert graph["edge_count"] >= 500
    assert graph["nodes"]
    assert graph["edges"]


def test_emergence_pattern_reinforcer_learns_from_hit_miss_outcomes():
    from datetime import datetime, timezone

    from runtime_core.emergence.system_emergence_engine import (
        EmergenceCycleRecord,
        EmergenceMemoryStore,
        EmergencePatternReinforcer,
    )

    store = EmergenceMemoryStore()
    store.append(
        EmergenceCycleRecord(
            cycle_id="one",
            timestamp=datetime.now(timezone.utc),
            entity_id="ev_market",
            predicted_stage="re_emerging",
            predicted_patterns=["technology_catch_up"],
            readiness_score=0.82,
            route_taken="breakthrough_design",
            outcome_label="hit",
        )
    )
    store.append(
        EmergenceCycleRecord(
            cycle_id="two",
            timestamp=datetime.now(timezone.utc),
            entity_id="vr_market",
            predicted_stage="pre_reemergence_watch",
            predicted_patterns=["technology_catch_up"],
            readiness_score=0.55,
            route_taken="portfolio_creation_optimization",
            outcome_label="miss",
        )
    )

    confidence = EmergencePatternReinforcer(store).compute_pattern_confidence()
    assert confidence["technology_catch_up"] == 0.5


def test_acs2_visual_command_center_endpoints_are_mounted():
    from fastapi.testclient import TestClient

    from runtime_core.app import create_app

    client = TestClient(create_app())
    graph = client.get("/api/acs2/graph", params={"query": "smartphone"})
    timeline = client.get("/api/acs2/timeline/smartphone")

    assert graph.status_code == 200
    assert graph.json()["node_count"] >= 500
    assert timeline.status_code == 200
    assert timeline.json()["status"] == "ready"
    assert timeline.json()["timelines"][0]["root_year"] <= 1700


def test_system_emergence_engine_reports_reinforcement_contract():
    from runtime_core.emergence.system_emergence_engine import build_system_emergence_engine

    payload = build_system_emergence_engine(
        "smartphone agentic interface ambient computing predictive assistance",
        context={"source_authority": {"source_evidence_present": True}},
        memory_records=[
            {
                "run_id": "cycle-one",
                "result": {
                    "route_selected": "breakthrough_design",
                    "outcome_label": "hit",
                    "emergence_engine": {
                        "cycle_stage": "re_emerging",
                        "readiness_score": 0.78,
                        "detected_patterns": [{"pattern_id": "platformization"}],
                    },
                },
            }
        ],
    )

    assert payload["pattern_reinforcement"]["status"] == "active"
    assert payload["pattern_reinforcement"]["pattern_confidence"]["platformization"] == 1.0
    assert payload["pipeline_bindings"]["whole_system"]
