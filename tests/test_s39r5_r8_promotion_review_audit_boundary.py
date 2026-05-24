from __future__ import annotations

import importlib
import json
from pathlib import Path


def sample_proposal():
    return {
        "candidate_id": "CAND-S39-001",
        "proposal_id": "PROP-S39-001",
        "operator_review": {"decision": "unreviewed"},
        "governance_warnings": ["manual promotion required"],
        "contradictions": [],
        "approval_checklist": [
            {"item": "source policy", "status": "passed"},
            {"item": "quarantine retained", "status": "complete"},
        ],
        "extracted_knowledge": {
            "claims": [{"claim": "Example governed knowledge claim", "confidence": 0.74}]
        },
    }


def test_s39r5_review_status_is_proposal_only():
    module = importlib.import_module("runtime_core.api.governed_promotion_review_audit_boundary")
    status = module.summarize_review_status(sample_proposal())

    assert status["candidate_id"] == "CAND-S39-001"
    assert status["manual_approval_required"] is True
    assert status["runtime_truth_mutation_allowed"] is False
    assert status["automatic_update_allowed"] is False
    assert status["status"] == "ready_for_manual_review"


def test_s39r6_approval_shell_has_no_promotion_effect():
    module = importlib.import_module("runtime_core.api.governed_promotion_review_audit_boundary")
    shell = module.build_approval_record_shell(
        sample_proposal(),
        operator_ack="YES",
        reviewer="operator",
        decision="approved_for_candidate_review",
        notes="reviewed as candidate only",
    )

    assert shell["operator_ack"] == "YES"
    assert shell["decision"] == "approved_for_candidate_review"
    assert shell["promotion_effect"] == "none"
    assert shell["runtime_truth_mutation_allowed"] is False
    assert shell["manual_promotion_still_required"] is True
    assert shell["authority"]["automatic_updates"] is False
    assert len(shell["approval_record_sha256"]) == 64


def test_s39r7_audit_boundary_is_tamper_evident_and_locked():
    module = importlib.import_module("runtime_core.api.governed_promotion_review_audit_boundary")
    proposal = sample_proposal()
    shell = module.build_approval_record_shell(proposal, operator_ack="YES")
    boundary = module.seal_proposal_audit_boundary(proposal, shell)

    assert boundary["record_type"] == "promotion_review_audit_boundary"
    assert boundary["promotion_effect"] == "none"
    assert boundary["quarantine_required"] is True
    assert boundary["manual_promotion_required"] is True
    assert boundary["runtime_truth_mutation_allowed"] is False
    assert len(boundary["proposal_sha256"]) == 64
    assert len(boundary["approval_record_sha256"]) == 64
    assert len(boundary["audit_boundary_sha256"]) == 64


def test_s39r8_writes_review_audit_files(tmp_path: Path):
    module = importlib.import_module("runtime_core.api.governed_promotion_review_audit_boundary")
    files = module.write_review_audit_artifacts(
        sample_proposal(),
        tmp_path,
        operator_ack="YES",
        reviewer="operator",
        decision="approved_for_candidate_review",
    )

    assert set(files) == {"status", "approval_record_shell", "audit_boundary"}
    for path in files.values():
        assert path.exists()

    status = json.loads(files["status"].read_text(encoding="utf-8"))
    shell = json.loads(files["approval_record_shell"].read_text(encoding="utf-8"))
    boundary = json.loads(files["audit_boundary"].read_text(encoding="utf-8"))

    assert status["runtime_truth_mutation_allowed"] is False
    assert shell["promotion_effect"] == "none"
    assert boundary["manual_promotion_required"] is True
