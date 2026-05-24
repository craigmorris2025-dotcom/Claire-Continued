"""
Defines the v10 completion contract — what done looks like
==========================================================
ACS2-Claire / Syntalion - 10.3.9-10.4.4

Module: src.claire.completion.completion_contract

Spec: Class CompletionContract. Methods: define_contract(version, capabilities) -> Contract, validate_contract(contract) -> ValidationResult, check_all_clauses(contract) -> list[ClauseResult], compute_completion_percentage(contract) -> float, identify_blockers(contract) -> list[Blocker], export_contract(contract) -> dict. Contract contains: version, required_capabilities, acceptance_criteria, verification_methods, sign_off_requirements.
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional

from runtime_core.completion.completion_logic import now

logger = logging.getLogger(__name__)


class CompletionContract:
    """
    Defines the v10 completion contract — what done looks like
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def define_contract(self, *args, **kwargs):
        """See content_spec for full signature."""
        version = kwargs.get("version") or (args[0] if args else "v10")
        capabilities = kwargs.get("capabilities") or (args[1] if len(args) > 1 else [])
        required = [item if isinstance(item, dict) else {"name": str(item)} for item in (capabilities or [])]
        return {
            "schema_version": "claire.completion.contract.v1",
            "version": version,
            "generated_at": now(),
            "required_capabilities": required,
            "acceptance_criteria": kwargs.get(
                "acceptance_criteria",
                [
                    "capability has a real implementation path",
                    "tests or proof artifacts exist",
                    "governance locks remain intact",
                    "operator-visible output is available",
                ],
            ),
            "verification_methods": kwargs.get("verification_methods", ["pytest", "py_compile", "proof_binder"]),
            "sign_off_requirements": kwargs.get("sign_off_requirements", ["operator_review"]),
            "manual_review_required": True,
        }

    def validate_contract(self, contract: dict[str, Any]) -> dict[str, Any]:
        missing = [key for key in ("version", "required_capabilities", "acceptance_criteria") if key not in contract]
        return {"status": "valid" if not missing else "invalid", "missing": missing, "checked_at": now()}

    def check_all_clauses(self, contract: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {"clause": criterion, "status": "requires_evidence", "manual_review_required": True}
            for criterion in contract.get("acceptance_criteria", [])
        ]

    def compute_completion_percentage(self, contract: dict[str, Any]) -> float:
        capabilities = contract.get("required_capabilities", [])
        if not capabilities:
            return 0.0
        complete = sum(1 for item in capabilities if isinstance(item, dict) and item.get("status") in {"delivered", "complete", "ready"})
        return round(complete / len(capabilities) * 100, 2)

    def identify_blockers(self, contract: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {"capability": item.get("name"), "reason": item.get("blocked_reason", "not delivered")}
            for item in contract.get("required_capabilities", [])
            if isinstance(item, dict) and item.get("status") not in {"delivered", "complete", "ready", "descoped"}
        ]

    def export_contract(self, contract: dict[str, Any]) -> dict[str, Any]:
        return dict(contract)
