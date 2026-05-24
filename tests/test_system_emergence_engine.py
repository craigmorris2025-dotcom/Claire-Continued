from __future__ import annotations


def test_system_emergence_engine_binds_patterns_route_and_learning_memory():
    from runtime_core.emergence.system_emergence_engine import build_system_emergence_engine

    payload = build_system_emergence_engine(
        "telehealth remote broadband regulation digital trust platform distribution inversion",
        context={
            "source_authority": {"source_evidence_present": True, "live_evidence_present": True},
            "advancement_path_decision": {"route_selected": "portfolio_creation_optimization"},
            "quality_gate": {"recursive_learning_complete": True},
        },
        memory_records=[
            {
                "result": {
                    "route_selected": "portfolio_creation_optimization",
                    "emergence_engine": {
                        "cycle_stage": "re_emerging",
                        "detected_patterns": [{"pattern_id": "distribution_inversion"}],
                    },
                }
            }
        ],
    )

    assert payload["status"] in {"emergence_engine_operational", "emergence_engine_foundation_ready"}
    assert payload["product_completion_percent"] >= 60
    assert payload["detected_patterns"]
    assert payload["ready_signal_families"]
    assert payload["longitudinal_learning"]["run_count"] == 1
    assert payload["pipeline_bindings"]["whole_system"].startswith("signal intake")
    assert payload["authority"]["autonomous_promotion_allowed"] is False


def test_continuous_runtime_writes_system_emergence_to_run_and_memory(tmp_path, monkeypatch):
    import importlib

    module = importlib.import_module("runtime_core.api.routes_continuous_runtime")
    monkeypatch.setattr(module, "CONTINUOUS_DIR", tmp_path / "continuous_runtime")

    module.create_cycle_payload(
        trigger="system_emergence_test",
        query="tablet app ecosystem touchscreen battery compute platform convergence market gap",
    )
    current_run = module.read_json(module.CONTINUOUS_DIR / "current_run.json", {})
    memory = module.read_json(module.CONTINUOUS_DIR / "lifecycle_memory.json", {})

    assert current_run["emergence_engine"]["status"] == "emergence_engine_operational"
    assert current_run["quality_gate"]["emergence_engine_complete"] is True
    assert current_run["emergence_engine"]["detected_patterns"]
    assert memory["records"][0]["result"]["emergence_engine"]["detected_patterns"]
    assert memory["recursive_learning"]["emergence_learning"]["status"] == "bound"


def test_pipeline_orchestrator_exposes_system_emergence_engine():
    from runtime_core.domain.contract import ClaireIntent
    from runtime_core.orchestrator.pipeline_v4 import PipelineOrchestrator

    result = PipelineOrchestrator().execute(
        ClaireIntent(
            raw_input="EV battery density charging infrastructure cost autonomy platform gap",
            mode="deterministic",
            source_mode="local_technology_seed",
            sources={"market": {"metrics": {"growth": 0.72}, "signals": ["EV infrastructure demand"]}},
        )
    ).to_dict()

    emergence = result["emergence_engine"]
    assert emergence["status"] in {"emergence_engine_operational", "emergence_engine_foundation_ready"}
    assert emergence["detected_patterns"]
    assert emergence["pipeline_bindings"]["whole_system"]


def test_system_emergence_contract_is_queryable_from_code():
    from runtime_core.emergence.system_emergence_engine import build_system_emergence_engine

    payload = build_system_emergence_engine("portable tv tablet app ecosystem battery platform")

    assert payload["schema_version"] == "claire.system_emergence_engine.v1"
    assert payload["detected_patterns"]
