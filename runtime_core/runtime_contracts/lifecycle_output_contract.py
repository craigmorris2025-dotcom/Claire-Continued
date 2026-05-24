"""
Lifecycle Output Contract
=========================
ACS2-Claire / Syntalion — v10.3.2

Defines the required output shape for each lifecycle stage. Claire operates
a 30-stage lifecycle with route-aware execution — stages may be completed,
skipped, or deferred depending on the selected route.

This contract ensures every stage output is structurally consistent
regardless of which route processed it.
"""

import json
import hashlib
from typing import Any, Dict, List, Optional, Tuple


class LifecycleOutputContract:
    """Validates lifecycle stage output conformance."""

    VERSION = "10.3.2"
    TOTAL_STAGES = 30

    STAGE_STATUSES = [
        "completed",
        "skipped",
        "skipped_by_route",
        "in_progress",
        "pending",
        "failed",
        "deferred",
    ]

    REQUIRED_STAGE_FIELDS = {
        "stage_number": int,
        "stage_name": str,
        "status": str,
        "started_at": str,
        "completed_at": str,
        "duration_ms": (int, float),
        "route_context": str,
        "evidence_ids": list,
        "output_summary": str,
        "skipped_by_route": bool,
        "skip_reason": str,
    }

    STAGE_NAMES = [
        "signal_ingestion",
        "source_classification",
        "credibility_weighting",
        "trend_detection",
        "weak_signal_amplification",
        "discontinuity_detection",
        "opportunity_formation",
        "convergence_pattern_id",
        "thesis_generation",
        "thesis_validation",
        "route_selection",
        "route_confidence_scoring",
        "portfolio_analysis",
        "breakthrough_classification",
        "technology_assessment",
        "market_potential_scoring",
        "competitive_landscape",
        "financial_modeling",
        "risk_assessment",
        "strategic_alignment",
        "acquisition_target_id",
        "acquirer_matching",
        "deal_structure",
        "design_portal_routing",
        "auto_design_generation",
        "package_construction",
        "evidence_compilation",
        "proof_binder_assembly",
        "terminal_state_resolution",
        "memory_commit",
    ]

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_stage(self, stage_output: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate a single lifecycle stage output."""
        self.errors = []
        self.warnings = []

        for field, expected_type in self.REQUIRED_STAGE_FIELDS.items():
            if field not in stage_output:
                if field in ("skip_reason",):
                    continue
                self.errors.append(f"Stage output missing field: {field}")
            elif not isinstance(stage_output[field], expected_type):
                self.errors.append(
                    f"Stage field '{field}' type mismatch: "
                    f"expected {expected_type}, got {type(stage_output[field])}"
                )

        stage_num = stage_output.get("stage_number", 0)
        if isinstance(stage_num, int) and not (1 <= stage_num <= self.TOTAL_STAGES):
            self.errors.append(f"Invalid stage_number: {stage_num}")

        status = stage_output.get("status", "")
        if status and status not in self.STAGE_STATUSES:
            self.errors.append(f"Invalid stage status: {status}")

        stage_name = stage_output.get("stage_name", "")
        if stage_name and stage_name not in self.STAGE_NAMES:
            self.warnings.append(f"Unrecognized stage_name: {stage_name}")

        if stage_output.get("skipped_by_route") and not stage_output.get("skip_reason"):
            self.warnings.append(
                f"Stage {stage_num} skipped_by_route but no skip_reason provided"
            )

        return len(self.errors) == 0, self.errors.copy(), self.warnings.copy()

    def validate_full_lifecycle(
        self, stages: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str], List[str]]:
        """Validate a complete lifecycle output (all 30 stages)."""
        all_errors = []
        all_warnings = []

        seen_numbers = set()
        for stage in stages:
            valid, errs, warns = self.validate_stage(stage)
            all_errors.extend(errs)
            all_warnings.extend(warns)
            num = stage.get("stage_number", 0)
            if num in seen_numbers:
                all_errors.append(f"Duplicate stage_number: {num}")
            seen_numbers.add(num)

        expected = set(range(1, self.TOTAL_STAGES + 1))
        missing = expected - seen_numbers
        if missing:
            all_warnings.append(f"Missing stage numbers: {sorted(missing)}")

        return len(all_errors) == 0, all_errors, all_warnings

    def get_stage_name(self, stage_number: int) -> str:
        """Return the canonical name for a stage number."""
        if 1 <= stage_number <= len(self.STAGE_NAMES):
            return self.STAGE_NAMES[stage_number - 1]
        return f"unknown_stage_{stage_number}"

    def get_route_skippable_stages(self, route: str) -> List[int]:
        """Return stage numbers that can be skipped for a given route."""
        skip_map = {
            "portfolio": [21, 22, 23, 24, 25],
            "breakthrough": [13, 21, 22, 23],
            "acquisition": [14, 15, 24, 25],
            "system_redesign": [13, 14, 21, 22, 23],
            "operational_optimization": [14, 21, 22, 23, 24, 25],
            "business_model": [14, 15, 21, 22, 23],
        }
        return skip_map.get(route, [])

    def to_dict(self) -> Dict[str, Any]:
        """Serialize contract for audit/export."""
        return {
            "contract_type": "lifecycle_output",
            "version": self.VERSION,
            "total_stages": self.TOTAL_STAGES,
            "stage_names": self.STAGE_NAMES,
            "valid_statuses": self.STAGE_STATUSES,
            "required_fields": list(self.REQUIRED_STAGE_FIELDS.keys()),
        }
