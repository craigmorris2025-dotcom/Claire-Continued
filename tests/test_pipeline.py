"""Tests for the PipelineOrchestrator end-to-end."""
import pytest
from backend.claire.contract import ClaireIntent
from backend.orchestrator.pipeline import PipelineOrchestrator


class TestPipeline:
    def test_pipeline_creates(self):
        p = PipelineOrchestrator()
        assert p is not None

    def test_pipeline_execute(self, sample_intent):
        p = PipelineOrchestrator()
        result = p.execute(sample_intent)
        assert result is not None
        assert result.status == "success"
        assert result.intent_id == sample_intent.id

    def test_pipeline_produces_scores(self, sample_intent):
        p = PipelineOrchestrator()
        result = p.execute(sample_intent)
        assert isinstance(result.scores, dict)
        assert len(result.scores) > 0

    def test_pipeline_decision_classification(self, sample_intent):
        p = PipelineOrchestrator()
        result = p.execute(sample_intent)
        assert result.decision_classification in ("GO", "CAUTION", "NO-GO", "UNKNOWN")

    def test_pipeline_breakthrough_classification(self, sample_intent):
        p = PipelineOrchestrator()
        result = p.execute(sample_intent)
        assert result.breakthrough_classification in ("HIGH", "MODERATE", "LOW", "UNKNOWN")

    def test_pipeline_modes(self):
        for mode in ("deterministic", "connected", "hybrid"):
            intent = ClaireIntent(raw_input="Test evaluation input text", mode=mode)
            p = PipelineOrchestrator()
            result = p.execute(intent)
            assert result.mode == mode
