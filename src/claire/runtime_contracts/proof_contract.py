"""
Proof Contract
==============
ACS2-Claire / Syntalion — v10.3.2

Defines the structure and requirements for evidence/proof binders.
Proof binders are the evidentiary record that supports every runtime
decision, route selection, and terminal state resolution.

Every claim in an export package must be traceable to entries in the
proof binder. The proof contract enforces this lineage.
"""

import json
import hashlib
from typing import Any, Dict, List, Optional, Tuple


class ProofContract:
    """Validates proof/evidence binder conformance."""

    VERSION = "10.3.2"

    EVIDENCE_TYPES = [
        "source_document",
        "api_response",
        "computation_result",
        "model_output",
        "human_input",
        "connector_fetch",
        "historical_run",
        "external_data",
        "internal_analysis",
        "governance_record",
    ]

    CREDIBILITY_LEVELS = [
        "verified",
        "high_confidence",
        "moderate_confidence",
        "low_confidence",
        "unverified",
        "contested",
    ]

    REQUIRED_BINDER_FIELDS = {
        "binder_id": str,
        "run_id": str,
        "created_at": str,
        "route_used": str,
        "terminal_state": str,
        "entries": list,
        "lineage_chain": list,
        "integrity_hash": str,
    }

    REQUIRED_ENTRY_FIELDS = {
        "entry_id": str,
        "evidence_type": str,
        "source": str,
        "content_hash": str,
        "credibility": str,
        "relevance_score": (int, float),
        "lifecycle_stage": int,
        "timestamp": str,
        "content_summary": str,
    }

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(self, binder: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate a proof binder against the contract."""
        self.errors = []
        self.warnings = []

        for field, expected_type in self.REQUIRED_BINDER_FIELDS.items():
            if field not in binder:
                self.errors.append(f"Missing binder field: {field}")
            elif not isinstance(binder[field], expected_type):
                self.errors.append(f"Binder field '{field}' type mismatch")

        entries = binder.get("entries", [])
        if isinstance(entries, list):
            if len(entries) == 0:
                self.warnings.append("Proof binder has no entries")
            for i, entry in enumerate(entries):
                self._validate_entry(i, entry)

        lineage = binder.get("lineage_chain", [])
        if isinstance(lineage, list):
            self._validate_lineage(lineage, entries)

        integrity = binder.get("integrity_hash", "")
        if integrity:
            computed = self._compute_integrity_hash(entries)
            if computed != integrity:
                self.errors.append(
                    f"Integrity hash mismatch: expected {computed}, got {integrity}"
                )

        return len(self.errors) == 0, self.errors.copy(), self.warnings.copy()

    def _validate_entry(self, index: int, entry: Dict[str, Any]):
        """Validate a single evidence entry."""
        if not isinstance(entry, dict):
            self.errors.append(f"Entry {index} is not a dict")
            return

        for field in self.REQUIRED_ENTRY_FIELDS:
            if field not in entry:
                self.errors.append(f"Entry {index} missing field: {field}")

        ev_type = entry.get("evidence_type", "")
        if ev_type and ev_type not in self.EVIDENCE_TYPES:
            self.warnings.append(f"Entry {index} unknown evidence_type: {ev_type}")

        cred = entry.get("credibility", "")
        if cred and cred not in self.CREDIBILITY_LEVELS:
            self.warnings.append(f"Entry {index} unknown credibility: {cred}")

        relevance = entry.get("relevance_score", 0)
        if isinstance(relevance, (int, float)) and not (0 <= relevance <= 1):
            self.warnings.append(f"Entry {index} relevance_score outside 0-1 range")

    def _validate_lineage(self, lineage: List, entries: List):
        """Validate the lineage chain references valid entry IDs."""
        entry_ids = {e.get("entry_id") for e in entries if isinstance(e, dict)}
        for link in lineage:
            if isinstance(link, dict):
                ref = link.get("entry_id", "")
                if ref and ref not in entry_ids:
                    self.warnings.append(f"Lineage references unknown entry_id: {ref}")

    def _compute_integrity_hash(self, entries: List) -> str:
        """Compute the expected integrity hash from entries."""
        content_hashes = []
        for entry in entries:
            if isinstance(entry, dict) and "content_hash" in entry:
                content_hashes.append(entry["content_hash"])
        combined = "|".join(sorted(content_hashes))
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def create_entry_id(self, evidence_type: str, source: str, stage: int) -> str:
        """Generate a deterministic entry ID."""
        raw = f"{evidence_type}_{source}_{stage}_{datetime.utcnow().isoformat()}"
        return f"ev_{hashlib.md5(raw.encode()).hexdigest()[:10]}"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize contract for audit/export."""
        return {
            "contract_type": "proof_binder",
            "version": self.VERSION,
            "evidence_types": self.EVIDENCE_TYPES,
            "credibility_levels": self.CREDIBILITY_LEVELS,
            "required_binder_fields": list(self.REQUIRED_BINDER_FIELDS.keys()),
            "required_entry_fields": list(self.REQUIRED_ENTRY_FIELDS.keys()),
        }
