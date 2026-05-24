from __future__ import annotations

from typing import Dict, List


def get_export_artifact_record_contract() -> Dict[str, object]:
    return {
        "version": "v19.89.8-S261-S267",
        "contract_id": "export_artifact_record_contract",
        "fields": [
            {"field": "export_id", "required": True, "mutable": False},
            {"field": "review_id", "required": True, "mutable": False},
            {"field": "artifact_type", "required": True, "mutable": False, "allowed": ["evidence_report", "portfolio_package", "breakthrough_package", "design_package", "acquisition_package"]},
            {"field": "created_at", "required": True, "mutable": False},
            {"field": "operator_approved", "required": True, "mutable": True},
            {"field": "artifact_path", "required": True, "mutable": False},
            {"field": "source_lineage_hash", "required": True, "mutable": False},
        ],
        "operator_approval_required": True,
        "runtime_truth_write_enabled": False,
        "persistence_ready": True,
    }
