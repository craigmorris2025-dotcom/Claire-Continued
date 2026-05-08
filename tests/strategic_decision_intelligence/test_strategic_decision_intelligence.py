from claire.strategic_decision_intelligence import StrategicDecisionRuntime


def test_strategic_decision_runtime_regression_passes():
    runtime = StrategicDecisionRuntime()
    result = runtime.run(
        {
            "title": "AI infrastructure opportunity",
            "thesis": "Enterprise teams need governed autonomous research systems.",
            "strategic_context": "Discovery layer indicates durable demand for evidence-linked decisioning.",
            "decision_question": "Should Claire escalate this opportunity into a bounded intervention?",
            "confidence": 0.72,
            "supporting_evidence": [
                {"source": "internal_discovery", "claim": "Repeated demand signal"},
                {"source": "campaign_memory", "claim": "Confidence continuity improving"},
            ],
            "conflicting_evidence": [
                {"source": "risk_review", "claim": "Deployment governance remains incomplete"}
            ],
        }
    )

    assert result["layer"] == "strategic_decision_intelligence"
    assert result["regression"]["regression_status"] == "passed"
    assert result["recommendation"]["execution_boundary"] == "no_external_action_without_user_approval"
    assert len(result["simulations"]) >= 3


def test_expected_actual_variance_tracking():
    runtime = StrategicDecisionRuntime()
    result = runtime.run(
        {
            "title": "Low confidence thesis",
            "thesis": "Weak signal may become a market opportunity.",
            "strategic_context": "Early discovery only.",
            "confidence": 0.35,
        },
        actual_outcome="favorable_if_governed",
        evidence_updates=[{"source": "later_result", "claim": "Outcome improved after small test"}],
    )

    assert result["outcome_record"]["actual_outcome"] == "favorable_if_governed"
    assert result["outcome_record"]["comparison_status"] in {
        "matched",
        "variance_detected",
        "resolved_from_uncertainty",
    }
