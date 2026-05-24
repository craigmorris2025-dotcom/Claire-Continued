from runtime_core.output.core_output_builder import CoreOutputBuilder
from runtime_core.validation.run_quality_gate import evaluate_run_quality


def test_run_quality_separates_local_seed_from_live_truth():
    payload = {
        "source_authority": {
            "source_evidence_present": True,
            "live_evidence_present": False,
            "effective_source_count": 4,
            "scores": {
                "source_quality_score": 0.66,
                "coverage_score": 0.96,
                "evidence_signal_score": 0.63,
            },
        },
        "user_facing_result": {
            "headline": "autonomous invention: technology discovery records",
            "summary": "Source-backed local seed for design validation.",
        },
    }

    quality = evaluate_run_quality(payload)

    assert quality["status"] == "local_source_seed_pending_live_validation"
    assert quality["live_evidence_present"] is False
    assert quality["request_source_evidence_present"] is True
    assert quality["dashboard_truth_eligible"] is True
    assert quality["live_truth_eligible"] is False
    assert quality["memory_feedback_eligible"] is False
    assert "pending_live_validation" in quality["warnings"]


def test_run_quality_blocks_missing_source_evidence():
    quality = evaluate_run_quality(
        {
            "source_authority": {
                "source_evidence_present": False,
                "live_evidence_present": False,
                "effective_source_count": 0,
                "scores": {},
            },
            "user_facing_result": {"headline": "portfolio opportunities cross-sector"},
        }
    )

    assert quality["status"] == "trash_run_blocked_from_truth"
    assert quality["dashboard_truth_eligible"] is False
    assert "no_live_or_request_source_evidence" in quality["blockers"]
    assert "no_source_count_from_knowledge_ingestion" in quality["blockers"]


def test_solution_design_headline_prefers_specific_trend_name():
    headline = CoreOutputBuilder()._headline(
        "solution_design",
        {
            "discovered_trends": [
                {"name": "autonomous invention: technology discovery records"}
            ]
        },
        {},
        {},
        {"category_name": "opportunity intelligence"},
    )

    assert headline == "autonomous invention: technology discovery records: solution/design route"


def test_pipeline_persistence_skips_memory_when_quality_blocks_feedback(monkeypatch):
    from runtime_core.api import routes_pipeline

    calls = {"memory": 0, "dashboard": 0}

    class FakeMemoryStore:
        def save_run(self, **kwargs):
            calls["memory"] += 1
            return {"status": "success", "memory_path": "not-used", "stored_at": "not-used"}

    def fake_dashboard_persist(*args, **kwargs):
        calls["dashboard"] += 1

    monkeypatch.setattr(routes_pipeline, "memory_store", FakeMemoryStore())
    monkeypatch.setattr(routes_pipeline, "_persist_dashboard_run_state", fake_dashboard_persist)

    response = routes_pipeline._persist_run(
        {
            "status": "success",
            "run_quality": {
                "status": "local_source_seed_pending_live_validation",
                "memory_feedback_eligible": False,
            },
        },
        "run-test",
        "intent-test",
        "local source seed",
        "deterministic",
    )

    assert calls == {"memory": 0, "dashboard": 1}
    assert response["memory"]["status"] == "skipped"
    assert response["memory"]["reason"] == "run_quality_gate_blocked_memory_feedback"
