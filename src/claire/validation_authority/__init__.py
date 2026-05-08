"""
Claire v17.60 Validation Authority package.

This package turns runtime truth into an auditable pass/fail authority report.
It does not execute the lifecycle. It validates and indexes the truth emitted by
the runtime truth backbone.
"""

from .validation_authority import ValidationAuthority, build_validation_report
from .evidence_traceability import build_evidence_traceability_index

__all__ = [
    "ValidationAuthority",
    "build_validation_report",
    "build_evidence_traceability_index",
]
