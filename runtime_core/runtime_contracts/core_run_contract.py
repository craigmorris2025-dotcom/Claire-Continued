"""
Core Run Output Contract
========================
ACS2-Claire / Syntalion — v10.3.2

Defines the required fields, types, and constraints for core_run_output.json —
the canonical runtime truth produced by every Claire evaluation run.

Every downstream consumer (dashboard, export, proof, memory) depends on this
contract being satisfied. No output may proceed without validation.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class CoreRunContract:
    """Validates and enforces the shape of core_run_output.json."""

    VERSION = "10.3.2"

    REQUIRED_TOP_LEVEL_FIELDS = {
        "run_id": str,
        "timestamp": str,
        "company_name": str,
        "ticker": str,
        "sector": str,
        "thesis": str,
        "route_selected": str,
        "terminal_state": str,
        "overall_score": (int, float),
        "confidence": (int, float),
        "lifecycle_stage": int,
        "lifecycle_stage_name": str,
        "evidence_count": int,
        "stages_completed": list,
        "stages_skipped": list,
        "scores": dict,
        "evidence": list,
        "metadata": dict,
    }

    VALID_ROUTES = [
        "portfolio",
        "breakthrough",
        "acquisition",
        "system_redesign",
        "operational_optimization",
        "business_model",
    ]

    VALID_TERMINAL_STATES = [
        "actionable",
        "monitoring",
        "rejected",
        "escalated",
        "deferred",
        "archived",
    ]

    SCORE_FIELDS = [
        "market_potential",
        "technical_feasibility",
        "strategic_alignment",
        "competitive_position",
        "financial_viability",
        "risk_assessment",
        "innovation_index",
        "execution_readiness",
    ]

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(self, output: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a core_run_output dict against the contract.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        self._check_required_fields(output)
        self._check_field_types(output)
        self._check_route_validity(output)
        self._check_terminal_state(output)
        self._check_scores(output)
        self._check_evidence(output)
        self._check_lifecycle_stage(output)
        self._check_metadata(output)

        return len(self.errors) == 0, self.errors.copy(), self.warnings.copy()

    def _check_required_fields(self, output: Dict[str, Any]):
        for field in self.REQUIRED_TOP_LEVEL_FIELDS:
            if field not in output:
                self.errors.append(f"Missing required field: {field}")

    def _check_field_types(self, output: Dict[str, Any]):
        for field, expected_type in self.REQUIRED_TOP_LEVEL_FIELDS.items():
            if field in output:
                value = output[field]
                if not isinstance(value, expected_type):
                    self.errors.append(
                        f"Field '{field}' expected {expected_type}, got {type(value)}"
                    )

    def _check_route_validity(self, output: Dict[str, Any]):
        route = output.get("route_selected", "")
        if route and route not in self.VALID_ROUTES:
            self.errors.append(
                f"Invalid route_selected '{route}'. Valid: {self.VALID_ROUTES}"
            )

    def _check_terminal_state(self, output: Dict[str, Any]):
        state = output.get("terminal_state", "")
        if state and state not in self.VALID_TERMINAL_STATES:
            self.errors.append(
                f"Invalid terminal_state '{state}'. Valid: {self.VALID_TERMINAL_STATES}"
            )

    def _check_scores(self, output: Dict[str, Any]):
        scores = output.get("scores", {})
        if isinstance(scores, dict):
            for field in self.SCORE_FIELDS:
                if field not in scores:
                    self.warnings.append(f"Score field missing: {field}")
                else:
                    val = scores[field]
                    if isinstance(val, (int, float)):
                        if not (0 <= val <= 100):
                            self.warnings.append(
                                f"Score '{field}' value {val} outside 0-100 range"
                            )

    def _check_evidence(self, output: Dict[str, Any]):
        evidence = output.get("evidence", [])
        if isinstance(evidence, list):
            count = output.get("evidence_count", 0)
            if count != len(evidence):
                self.warnings.append(
                    f"evidence_count ({count}) != len(evidence) ({len(evidence)})"
                )
            for i, item in enumerate(evidence):
                if isinstance(item, dict):
                    for req in ("source", "content", "relevance"):
                        if req not in item:
                            self.warnings.append(
                                f"Evidence item {i} missing '{req}'"
                            )

    def _check_lifecycle_stage(self, output: Dict[str, Any]):
        stage = output.get("lifecycle_stage", 0)
        if isinstance(stage, int) and not (1 <= stage <= 30):
            self.errors.append(
                f"lifecycle_stage {stage} outside valid range 1-30"
            )

    def _check_metadata(self, output: Dict[str, Any]):
        meta = output.get("metadata", {})
        if isinstance(meta, dict):
            recommended = ["pipeline_version", "orchestrator", "duration_ms", "source_count"]
            for key in recommended:
                if key not in meta:
                    self.warnings.append(f"Metadata missing recommended field: {key}")

    def generate_contract_hash(self) -> str:
        """Generate a deterministic hash of the contract definition."""
        contract_def = json.dumps(
            {
                "required_fields": list(self.REQUIRED_TOP_LEVEL_FIELDS.keys()),
                "valid_routes": self.VALID_ROUTES,
                "valid_terminal_states": self.VALID_TERMINAL_STATES,
                "score_fields": self.SCORE_FIELDS,
                "version": self.VERSION,
            },
            sort_keys=True,
        )
        return hashlib.sha256(contract_def.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize contract definition for audit/export."""
        return {
            "contract_type": "core_run_output",
            "version": self.VERSION,
            "required_fields": list(self.REQUIRED_TOP_LEVEL_FIELDS.keys()),
            "valid_routes": self.VALID_ROUTES,
            "valid_terminal_states": self.VALID_TERMINAL_STATES,
            "score_fields": self.SCORE_FIELDS,
            "contract_hash": self.generate_contract_hash(),
        }
