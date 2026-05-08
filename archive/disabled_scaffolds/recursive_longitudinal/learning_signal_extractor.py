"""
Extracts actionable learning signals from run outcomes
======================================================
ACS2-Claire / Syntalion

Module: src.claire.recursive.longitudinal.learning_signal_extractor
Role: Extracts actionable learning signals from run outcomes
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SignalType(Enum):
    IMPROVEMENT = "improvement"
    REGRESSION = "regression"
    PLATEAU = "plateau"
    ANOMALY = "anomaly"
    BREAKTHROUGH = "breakthrough"


class LearningSignalExtractor:
    """
    Extracts actionable learning signals from run outcomes

    Writes to data/recursive/learning_signals/..
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"{self.__class__.__name__} initialized")

    def extract_signals(run_outcome):
        """Returns list[Signal]."""
        raise NotImplementedError

    def classify_signal(signal):
        """Returns SignalType."""
        raise NotImplementedError

    def measure_signal_strength(signal):
        """Returns float."""
        raise NotImplementedError

    def correlate_signals(signals):
        """Returns CorrelationMatrix."""
        raise NotImplementedError

    def filter_noise(signals:
        """Returns Any."""
        raise NotImplementedError

    def threshold):
        """Returns list."""
        raise NotImplementedError

    def export_signals(signals):
        """Returns dict."""
        raise NotImplementedError

