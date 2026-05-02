from __future__ import annotations

from claire.domain.contract import ContractValidator
from claire.orchestrator.pipeline_v4 import PipelineOrchestrator
from claire.signals.signal_governance import SignalGovernance


def test_signal_governance_normalizes_dedupes_and_scores_raw_input():
    governance = SignalGovernance()
    result = governance.govern(
        [
            {"raw_input": "Rising climate insurance losses create repricing pressure and regional withdrawal risk."},
            {"raw_input": "Rising climate insurance losses create repricing pressure and regional withdrawal risk."},
        ],
        context={"domain": "insurance", "keywords": ["climate", "insurance", "repricing"]},
    )

    assert result["status"] == "success"
    assert result["raw_signal_count"] == 2
    assert result["deduped_signal_count"] == 1
    assert result["accepted_signal_count"] == 1
    signal = result["signals"][0]
    assert signal["safe_for_lifecycle"] is True
    assert signal["scores"]["quality_score"] > 0
    assert signal["scores"]["noise_rejection"] is True


def test_pipeline_exposes_governed_signals_without_breaking_lifecycle():
    result = PipelineOrchestrator().execute(
        ContractValidator().validate_intent({
            "raw_input": "Evaluate climate insurance repricing lag and risk-transfer demand.",
            "mode": "deterministic",
        })
    ).to_dict()

    governed = result["governed_signals"]
    assert governed["status"] == "success"
    assert governed["accepted_signal_count"] >= 1
    assert result["core_lifecycle"]["stage_count"] == 30
