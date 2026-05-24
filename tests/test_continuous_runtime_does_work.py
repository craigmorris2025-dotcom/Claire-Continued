from __future__ import annotations

import importlib


def test_continuous_runtime_start_creates_source_backed_candidates(tmp_path, monkeypatch):
    module = importlib.import_module("runtime_core.api.routes_continuous_runtime")
    monkeypatch.setattr(module, "CONTINUOUS_DIR", tmp_path / "continuous_runtime")

    payload = module.create_cycle_payload(trigger="test")
    cycle = payload["cycle"]

    assert cycle["status"] == "completed_allowlisted_input_cycle"
    assert cycle["candidate_counts"]["discoveries"] == 1
    assert cycle["candidate_counts"]["portfolios"] == 1
    assert cycle["candidate_counts"]["breakthroughs"] in {0, 1}
    assert cycle["candidate_counts"]["packages"] == 1
    assert cycle["advancement_path_decision"]["route_selected"] in {"portfolio_creation_optimization", "breakthrough_design"}
    assert cycle["top_candidate"]["route"] == cycle["advancement_path_decision"]["route_selected"]
    assert cycle["run_spine"]["status"] == "valid_continuous_lifecycle_snapshot"
    assert cycle["run_spine"]["stage_count"] == 30
    assert cycle["input_boundary"]["status"] == "enforced"
    assert all(
        item["path"] in {
            "data/continuous_runtime/lifecycle_memory.json",
            "data/source_universes/universe_index.json",
            "data/live/source_registry.json",
            "data/live_intelligence/latest_monitor_run.json",
            "data/internet_evidence/promoted_metadata_evidence_store.json",
        }
        for item in cycle["input_boundary"]["allowed_sources"]
    )
    assert cycle["authority"]["network_request_performed"] is False
    assert cycle["authority"]["runtime_truth_mutated"] is False

    discovery = module.read_json(module.CONTINUOUS_DIR / "discovery_candidates.json", {})
    portfolio = module.read_json(module.CONTINUOUS_DIR / "portfolio_candidates.json", {})
    package = module.read_json(module.CONTINUOUS_DIR / "package_candidates.json", {})
    breakthrough = module.read_json(module.CONTINUOUS_DIR / "breakthrough_candidates.json", {})
    design = module.read_json(module.CONTINUOUS_DIR / "design_candidates.json", {})
    current_run = module.read_json(module.CONTINUOUS_DIR / "current_run.json", {})
    memory = module.read_json(module.CONTINUOUS_DIR / "lifecycle_memory.json", {})
    review_queue = module.read_json(module.CONTINUOUS_DIR / "review_queue.json", {})

    assert discovery["count"] == cycle["candidate_counts"]["discoveries"]
    assert portfolio["count"] == cycle["candidate_counts"]["portfolios"]
    assert package["count"] == cycle["candidate_counts"]["packages"]
    assert breakthrough["count"] == cycle["candidate_counts"]["breakthroughs"]
    assert design["count"] == cycle["candidate_counts"]["designs"]
    assert current_run["advancement_path_policy_respected"] is True
    assert current_run["advancement_path_decision"]["route_selected"] == current_run["route_selected"]
    assert current_run["breakthrough_evaluation"]["threshold_met"] is (current_run["route_selected"] == "breakthrough_design")
    assert current_run["design_gate"]["status"] in {"selected", "not_selected"}
    assert current_run["design_candidate"]["design_proof"]["status"] == "design_proof_ready"
    assert current_run["design_candidate"]["design_proof"]["documents_used_as_runtime_programming"] is False
    assert current_run["quality_gate"]["design_proof_complete"] is True
    assert current_run["evidence_governance"]["status"] == "evidence_governance_ready"
    assert current_run["evidence_governance"]["documents_used_as_runtime_programming"] is False
    assert current_run["quality_gate"]["evidence_governance_complete"] is True
    assert current_run["recursive_learning"]["status"] == "recursive_learning_ready"
    assert current_run["recursive_learning"]["documents_used_as_runtime_programming"] is False
    assert current_run["quality_gate"]["recursive_learning_complete"] is True
    assert memory["records"][0]["result"]["run_quality"]["memory_feedback_eligible"] is True
    assert memory["recursive_learning"]["current_run_id"] == current_run["run_id"]
    route_proofs = module.read_json(module.CONTINUOUS_DIR / "route_capability_proofs.json", {})
    assert route_proofs["routes"][current_run["route_selected"]]["proof_complete"] is True
    assert review_queue["items"][-1]["status"] == "pending_operator_review"
    assert "autonomous advancement routing" in review_queue["items"][-1]["summary"]


def test_existing_system_replacement_route_follows_uploaded_pipeline(tmp_path, monkeypatch):
    module = importlib.import_module("runtime_core.api.routes_continuous_runtime")
    monkeypatch.setattr(module, "CONTINUOUS_DIR", tmp_path / "continuous_runtime")

    payload = module.create_cycle_payload(
        trigger="existing_system_route_test",
        query="existing system ingestion legacy AI compliance workflow architecture decomposition integration gap superior system replacement",
    )
    current_run = module.read_json(module.CONTINUOUS_DIR / "current_run.json", {})

    assert current_run["route_selected"] == "existing_system_replacement"
    assert current_run["advancement_path_decision"]["conditions"]["existing_system_replacement_required"] is True
    assert current_run["existing_system_replacement"]["existing_system_ingestion"]["status"] == "completed"
    assert current_run["existing_system_replacement"]["existing_system_decomposition"]["analysis_type"] == "system_ingestion_decomposition"
    assert current_run["existing_system_replacement"]["superior_system_design"]["status"] == "draft_ready_for_design_portal_review"
    assert current_run["design_candidate"]["design_proof"]["architecture_feasibility"]["verdict"] in {
        "feasible",
        "conditionally_feasible",
    }
    assert current_run["design_candidate"]["design_proof"]["build_sequence"]["status"] == "valid_order"
    assert current_run["quality_gate"]["design_proof_complete"] is True
    assert current_run["quality_gate"]["evidence_governance_complete"] is True
    assert current_run["quality_gate"]["recursive_learning_complete"] is True
    assert current_run["quality_gate"]["existing_system_decomposition_present"] is True
    assert current_run["quality_gate"]["superior_system_design_present"] is True
    assert {item["output_key"] for item in current_run["route_insertions"]} >= {
        "existing_system_ingestion",
        "existing_system_decomposition",
        "superior_system_design",
    }
    assert payload["cycle"]["advancement_path_decision"]["route_selected"] == "existing_system_replacement"
    route_proofs = module.read_json(module.CONTINUOUS_DIR / "route_capability_proofs.json", {})
    proof = route_proofs["routes"]["existing_system_replacement"]
    assert proof["proof_complete"] is True
    assert proof["last_successful_run_id"] == current_run["run_id"]
    assert proof["documents_used_as_runtime_programming"] is False


def test_bounded_scheduler_tick_proves_continuous_cycle_without_daemon_claim(tmp_path, monkeypatch):
    module = importlib.import_module("runtime_core.api.routes_continuous_runtime")
    monkeypatch.setattr(module, "CONTINUOUS_DIR", tmp_path / "continuous_runtime")

    initial = module.scheduler_status_payload()
    assert initial["scheduler_state"]["status"] == "bounded_scheduler_ready"
    assert initial["scheduler_state"]["daemon_installed"] is False
    assert initial["scheduler_state"]["task_runner_installed"] is False
    assert initial["authority"]["documents_used_as_runtime_programming"] is False

    tick = module.run_scheduler_tick(
        {
            "query": (
                "scheduled AI market signal existing system ingestion architecture gap "
                "superior replacement portfolio acquirer"
            )
        }
    )

    assert tick["status"] == "scheduler_tick_completed"
    assert tick["cycle"]["trigger"] == "bounded_scheduler_tick"
    assert tick["cycle"]["run_spine"]["status"] == "valid_continuous_lifecycle_snapshot"
    assert tick["cycle"]["run_spine"]["stage_count"] == 30
    assert "documents remain validation references only" in tick["cycle"]["rule"]
    assert tick["scheduler_state"]["tick_count"] == 1
    assert tick["scheduler_state"]["last_tick_result"] == "cycle_created"
    assert tick["scheduler_state"]["daemon_installed"] is False
    assert tick["scheduler_state"]["task_runner_installed"] is False
    assert tick["continuous_runtime"]["scheduler_policy"]["status"] == "bounded_scheduler_tick_proven_not_daemonized"
    assert tick["authority"]["runtime_truth_mutation_allowed"] is False
