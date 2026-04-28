"""Tests for scoring calibrator and scorecard."""
import pytest
from backend.scoring.calibrator import ScoreCalibrator
from backend.scoring.scorecard import ScoreCard


class TestCalibrator:
    def test_calibrate(self, sample_scores):
        cal = ScoreCalibrator()
        result = cal.calibrate(sample_scores)
        assert "decision_score" in result
        assert "portfolio_score" in result
        assert "_confidence" in result
        assert 0 <= result["decision_score"] <= 1
        assert 0 <= result["portfolio_score"] <= 1

    def test_calibrate_empty(self):
        cal = ScoreCalibrator()
        result = cal.calibrate({})
        assert result["decision_score"] == 0
        assert result["_confidence"] == 0


class TestScorecard:
    def test_render(self, sample_scores):
        card = ScoreCard()
        text = card.render(sample_scores)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_render_empty(self):
        card = ScoreCard()
        text = card.render({})
        assert isinstance(text, str)
