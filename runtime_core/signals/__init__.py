"""Run-level signal governance for Claire v5.89.7."""

from .signal_governance import SignalGovernance
from .signal_deduplication import dedupe_signals
from .signal_scoring import SignalGovernanceScorer
from .source_weighting import source_weight

__all__ = [
    "SignalGovernance",
    "SignalGovernanceScorer",
    "dedupe_signals",
    "source_weight",
]
