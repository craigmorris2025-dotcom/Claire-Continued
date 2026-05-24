"""
Checks that all planned capabilities are closed/delivered
=========================================================
ACS2-Claire / Syntalion - 10.3.9-10.4.4

Module: src.claire.completion.capability_closure_checker

Spec: Class CapabilityClosureChecker. Methods: check_closure(capability_registry) -> ClosureReport, verify_capability(capability) -> CapabilityStatus, identify_unclosed(registry) -> list[Capability], compute_closure_rate(registry) -> float, generate_closure_matrix(registry) -> Matrix, export_report(report) -> dict. Writes to data/completion/closure_checks/. CapabilityStatus enum: DELIVERED, PARTIAL, NOT_STARTED, DESCOPED, DEFERRED.
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional

from runtime_core.completion.completion_logic import closure_report

logger = logging.getLogger(__name__)

from enum import Enum, auto

class CapabilityStatus(Enum):
    DELIVERED = auto()
    PARTIAL = auto()
    NOT_STARTED = auto()
    DESCOPED = auto()
    DEFERRED = auto()


class CapabilityClosureChecker:
    """
    Checks that all planned capabilities are closed/delivered
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def check_closure(self, *args, **kwargs):
        """See content_spec for full signature."""
        registry = kwargs.get("capability_registry") or (args[0] if args else [])
        return closure_report(registry)

    def verify_capability(self, capability: dict[str, Any]) -> dict[str, Any]:
        return closure_report([capability])["capabilities"][0]

    def identify_unclosed(self, registry: Any) -> list[dict[str, Any]]:
        return closure_report(registry)["unclosed"]

    def compute_closure_rate(self, registry: Any) -> float:
        return float(closure_report(registry)["closure_rate"])

    def generate_closure_matrix(self, registry: Any) -> dict[str, Any]:
        report = closure_report(registry)
        return {"statuses": {item["name"]: item["closure_status"] for item in report["capabilities"] if "name" in item}}

    def export_report(self, report: dict[str, Any]) -> dict[str, Any]:
        return dict(report)
