"""Legacy import wrapper for score calibration."""

from claire.scoring.calibrator import ScoreCalibrator as ActiveScoreCalibrator


class ScoreCalibrator(ActiveScoreCalibrator):
    def calibrate(self, raw_scores):
        if not raw_scores:
            return {"decision_score": 0, "portfolio_score": 0, "_confidence": 0}
        return super().calibrate(raw_scores)

__all__ = ["ScoreCalibrator"]
