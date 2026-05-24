from __future__ import annotations


def test_reemergence_engine_detects_ev_infrastructure_and_technology_catch_up():
    from runtime_core.technology.reemergence_pattern_engine import build_reemergence_pattern_engine

    engine = build_reemergence_pattern_engine(
        "EV lithium battery density charging network autonomy cost collapse regulation infrastructure"
    )
    detected = {item["pattern_id"] for item in engine["detected_patterns"]}
    ready_families = {family_id for family_id, family in engine["signal_families"].items() if family["ready"]}

    assert engine["status"] == "ready"
    assert engine["signal_family_count"] == 7
    assert engine["pattern_count"] == 12
    assert {"technology_catch_up", "infrastructure_catch_up"} & detected
    assert {"technology", "infrastructure"} <= ready_families
    assert engine["readiness_score"] >= 0.36
    assert engine["cycle_stage"] in {"pre_reemergence_watch", "re_emerging", "post_reemergence_or_active_adoption"}
    assert engine["route_guidance"]["recommended_route"] in {"portfolio_creation_optimization", "breakthrough_design"}


def test_reemergence_engine_classifies_portable_tv_to_tablet_as_platformization():
    from runtime_core.technology.reemergence_pattern_engine import build_reemergence_pattern_engine

    engine = build_reemergence_pattern_engine(
        "portable tv tablet touchscreen app ecosystem smartphone platform battery compute convergence mobile"
    )
    detected = {item["pattern_id"] for item in engine["detected_patterns"]}

    assert "platformization" in detected
    assert engine["category_matches"]
    assert engine["signals_to_watch"]
    assert "stage_11_15" in engine["pipeline_bindings"]


def test_reemergence_engine_exposes_full_operator_category_taxonomy():
    from runtime_core.technology.reemergence_pattern_engine import build_reemergence_taxonomy

    taxonomy = build_reemergence_taxonomy()
    pattern_ids = {item["pattern_id"] for item in taxonomy["patterns"]}

    assert taxonomy["status"] == "ready"
    assert taxonomy["category_count"] == 8
    assert taxonomy["signal_family_count"] == 7
    assert taxonomy["pattern_count"] == 12
    assert {
        "ecosystem_lock_in",
        "ai_native",
        "verticalization",
        "modality_shift",
    } <= pattern_ids
    assert "automotive_transportation" in taxonomy["categories"]
    assert "motorcycles" in taxonomy["categories"]["automotive_transportation"]["subcategories"]
    assert taxonomy["route_readiness"]["routes_may_attach_now"] is True
    assert taxonomy["route_readiness"]["causal_files_may_attach_after_emergence_contracts"] is True


def test_reemergence_engine_classifies_ai_native_and_modality_shift():
    from runtime_core.technology.reemergence_pattern_engine import build_reemergence_pattern_engine

    ai_engine = build_reemergence_pattern_engine(
        "old chatbot personal assistant returns as AI native LLM agent copilot automation with model capability"
    )
    media_engine = build_reemergence_pattern_engine(
        "radio and TV return through podcasts streaming newsletters social commerce attention device shift"
    )

    assert "ai_native" in {item["pattern_id"] for item in ai_engine["detected_patterns"]}
    assert "modality_shift" in {item["pattern_id"] for item in media_engine["detected_patterns"]}


def test_technology_assessment_exposes_reemergence_reasoning_contract():
    from runtime_core.technology.technology_base import assess_technology_base

    assessment = assess_technology_base("telehealth remote broadband regulation digital trust platform")
    engine = assessment["reemergence_pattern_engine"]

    assert engine["status"] == "ready"
    assert assessment["counts"]["reemergence_patterns"] == 12
    assert assessment["counts"]["signal_families"] == 7
    assert assessment["reasoning_capabilities"]["reemergence_pattern_classification"] is True
    assert assessment["reasoning_capabilities"]["signal_family_readiness_scoring"] is True
    assert assessment["reasoning_capabilities"]["cycle_stage_detection"] is True
    assert "reemergence_pattern_classification" in assessment["next_pipeline_bindings"]


def test_root_to_current_timeline_traces_current_object_back_to_origin_dots():
    from runtime_core.technology.technology_base import assess_technology_base

    assessment = assess_technology_base("cell phone mobile smartphone")
    timeline = assessment["root_to_current_timeline"]
    first = timeline["timelines"][0]

    assert timeline["status"] == "ready"
    assert first["dot_count"] >= 1
    assert first["root_year"] <= first["current_year"]
    assert first["dots"]
    assert first["why_it_happened_summary"]
    assert first["likelihood_it_repeats"] > 0.3
    assert first["likely_next_forms"]
    assert assessment["reasoning_capabilities"]["root_to_current_timeline"] is True


def test_continuous_runtime_advancement_carries_pattern_engine(tmp_path, monkeypatch):
    import importlib

    module = importlib.import_module("runtime_core.api.routes_continuous_runtime")
    monkeypatch.setattr(module, "CONTINUOUS_DIR", tmp_path / "continuous_runtime")

    payload = module.create_cycle_payload(
        trigger="reemergence_pattern_test",
        query="EV battery density charging network infrastructure cost sensor autonomy market gap",
    )
    decision = payload["cycle"]["advancement_path_decision"]

    assert decision["reemergence_pattern_engine"]["status"] == "ready"
    assert decision["scores"]["reemergence_readiness_score"] >= 0.36
    assert decision["scores"]["signal_family_readiness_score"] > 0
    assert decision["conditions"]["reemergence_pattern_detected"] is True
    assert decision["conditions"]["ready_signal_families"]
    assert decision["reemergence_pattern_engine"]["detected_patterns"]
    assert decision["reemergence_pattern_engine"]["pipeline_bindings"]["stage_16_22"]


def test_reemergence_taxonomy_routes_are_mounted():
    from fastapi.testclient import TestClient

    from runtime_core.app import create_app

    client = TestClient(create_app())
    taxonomy = client.get("/api/technology/reemergence-taxonomy")
    classified = client.get("/api/technology/reemergence-classify", params={"query": "AI agent copilot chatbot"})
    acs2_alias = client.get("/api/acs2/reemergence-taxonomy")

    assert taxonomy.status_code == 200
    assert taxonomy.json()["pattern_count"] == 12
    assert classified.status_code == 200
    assert classified.json()["status"] == "ready"
    assert acs2_alias.status_code == 200
    assert acs2_alias.json()["category_count"] == 8
