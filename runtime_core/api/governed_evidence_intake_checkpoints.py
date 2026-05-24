from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class EvidenceCheckpoint:
    checkpoint_id: str
    label: str
    purpose: str
    quarantine_required: bool
    promotion_allowed: bool
    promotion_requires_operator: bool


CHECKPOINTS: List[EvidenceCheckpoint] = [
    EvidenceCheckpoint("source_capture", "Source Capture", "Record source reference and retrieval context.", True, False, True),
    EvidenceCheckpoint("lineage_record", "Lineage Record", "Bind evidence to source lineage and trust metadata.", True, False, True),
    EvidenceCheckpoint("trust_score_assignment", "Trust Score Assignment", "Attach provisional source confidence.", True, False, True),
    EvidenceCheckpoint("quarantine_write", "Quarantine Write", "Store evidence outside runtime truth.", True, False, True),
    EvidenceCheckpoint("operator_review", "Operator Review", "Human review before promotion eligibility.", True, False, True),
    EvidenceCheckpoint("promotion_candidate", "Promotion Candidate", "Prepare but do not write runtime truth.", True, True, True),
    EvidenceCheckpoint("export_package_ready", "Export Package Ready", "Allow reviewed output export.", True, True, True),
]


def get_evidence_intake_checkpoints() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S205-S211",
        "stage_range": "S205-S211",
        "checkpoints": [asdict(item) for item in CHECKPOINTS],
        "runtime_truth_write_enabled": False,
        "manual_promotion_mandatory": True,
        "quarantine_mandatory": True,
    }
