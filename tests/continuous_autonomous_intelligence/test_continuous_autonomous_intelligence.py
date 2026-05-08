from pathlib import Path

from claire.continuous_autonomous_intelligence import ContinuousAutonomousIntelligenceRuntime


def test_continuous_cycle_passes_regression(tmp_path: Path):
    runtime = ContinuousAutonomousIntelligenceRuntime(checkpoint_root=tmp_path)
    result = runtime.run_cycle(
        campaign_name="AI infrastructure monitoring",
        topics=["governed research systems"],
        signal={
            "topic": "governed research systems",
            "confidence": 0.76,
            "novelty": 0.7,
            "urgency": 0.8,
            "contradiction": 0.2,
        },
        evidence_packets=[
            {"stance": "supporting", "confidence": 0.7},
            {"stance": "supporting", "confidence": 0.6},
        ],
    )

    assert result["layer"] == "continuous_autonomous_intelligence"
    assert result["regression"]["regression_status"] == "passed"
    assert result["supervisor_tick"]["status"] == "processed"
    assert result["governance_boundary"] == "bounded_internal_orchestration_no_unreviewed_external_action"


def test_conflict_dominant_routes_to_review(tmp_path: Path):
    runtime = ContinuousAutonomousIntelligenceRuntime(checkpoint_root=tmp_path)
    result = runtime.run_cycle(
        campaign_name="conflict test",
        topics=["market signal"],
        signal={
            "topic": "market signal",
            "confidence": 0.62,
            "novelty": 0.5,
            "urgency": 0.5,
            "contradiction": 0.9,
        },
        evidence_packets=[
            {"stance": "conflicting", "confidence": 0.9},
            {"stance": "supporting", "confidence": 0.2},
        ],
    )

    assert result["reconciliation"]["status"] == "conflict_dominant"
    assert result["escalation"]["route"] == "human_review"
    assert result["regression"]["regression_status"] == "passed"


def test_checkpoint_is_written(tmp_path: Path):
    runtime = ContinuousAutonomousIntelligenceRuntime(checkpoint_root=tmp_path)
    result = runtime.run_cycle(
        campaign_name="checkpoint test",
        topics=["signal"],
        signal={"topic": "signal", "confidence": 0.5},
    )

    assert Path(result["checkpoint"]).exists()
