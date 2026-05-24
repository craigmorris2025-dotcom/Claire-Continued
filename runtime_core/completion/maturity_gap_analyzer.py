"""
Analyzes gaps between current and target maturity
=================================================
ACS2-Claire / Syntalion - 10.3.9-10.4.4

Module: src.claire.completion.maturity_gap_analyzer

Spec: Class MaturityGapAnalyzer. Methods: analyze_gaps(current_maturity, target_maturity) -> GapAnalysis, prioritize_gaps(gaps) -> list[PrioritizedGap], estimate_closure_effort(gap) -> EffortEstimate, suggest_remediation(gap) -> RemediationPlan, compute_maturity_trajectory(history) -> Trajectory, export_analysis(analysis) -> dict. Writes to data/completion/maturity_reports/.
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional

from runtime_core.completion.completion_logic import maturity_gaps

logger = logging.getLogger(__name__)


class MaturityGapAnalyzer:
    """
    Analyzes gaps between current and target maturity
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_gaps(self, *args, **kwargs):
        """See content_spec for full signature."""
        current = kwargs.get("current_maturity") or (args[0] if args else {})
        target = kwargs.get("target_maturity") or (args[1] if len(args) > 1 else {})
        return maturity_gaps(current if isinstance(current, dict) else {}, target if isinstance(target, dict) else {})

    def prioritize_gaps(self, gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(gaps, key=lambda item: ({"high": 0, "medium": 1, "low": 2}.get(item.get("priority"), 3), -float(item.get("gap", 0))))

    def estimate_closure_effort(self, gap: dict[str, Any]) -> dict[str, Any]:
        value = float(gap.get("gap", 0.0))
        return {"effort": "large" if value >= 0.4 else "medium" if value >= 0.2 else "small", "gap": value}

    def suggest_remediation(self, gap: dict[str, Any]) -> dict[str, Any]:
        return {"dimension": gap.get("dimension"), "steps": [gap.get("remediation", "Add evidence and verification.")]}

    def compute_maturity_trajectory(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        return {"status": "trajectory_ready", "points": history, "point_count": len(history)}

    def export_analysis(self, analysis: dict[str, Any]) -> dict[str, Any]:
        return dict(analysis)
