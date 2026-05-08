"""
Claire v17.61 Verified Memory + Recursive Feedback Gate.

This package does not perform autonomous learning. It creates the governance gate
that decides whether a validated Claire output may enter verified memory and
whether recursive feedback is permitted.
"""

from .memory_gate import MemoryGate, build_memory_gate_report
from .recursive_feedback_gate import RecursiveFeedbackGate, build_recursive_feedback_report

__all__ = [
    "MemoryGate",
    "RecursiveFeedbackGate",
    "build_memory_gate_report",
    "build_recursive_feedback_report",
]
