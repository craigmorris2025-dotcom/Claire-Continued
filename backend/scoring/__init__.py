"""Legacy scoring compatibility package."""

from .calibrator import ScoreCalibrator
from claire.scoring.scorecard import ScoreCard

__all__ = ["ScoreCalibrator", "ScoreCard"]
