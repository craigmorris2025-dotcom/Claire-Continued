
from __future__ import annotations

import importlib
import json
from pathlib import Path


def sample_audit_boundary():
    return {
        "record_type": "promotion_review_audit_boundary",
        "candidate_id": "CAND-S39-009",
        "proposal_id": "PROP-S39-009",
        "proposal_sha256": "a" * 64,
        "approval_record_sha256": "b" * 64,
        "audit_boundary_sha256": "c" * 64,
        "authority": {
            "runtime_truth_mutation": False,
            "automatic_updates": False,
            "autonomous_execution": False,
            "continuous_live_crawling": False,
            "browser_execution": False,
            "javascript_execution": False,
        },
        "promotion_effect": "none",
        "quarantine_required": True,
        "manual_promotion_required": True,
        "runtime_truth_mutation_allowed": False,
    }


def test_s39r9_readiness_entry_is_non_authoritative():
    module = importlib.import_module("runtime_core.api.governed_promotion_readiness_ledger")
    entry = module.readiness_from_audit_boundary(sample_audit_boundary())

    assert entry["status"] == "candidate_review_ready"
    assert entry["blocked_reasons"] == []
    assert entry["runtime_truth_mutation_allowed"] is False
    assert entry["automatic_update_allowed"] is False
    assert entry["promotion_effect"] == "none"
    assert entry["manual_promotion_required"] is True
    assert len(entry["readiness_ledger_sha256"]) == 64


def test_s39r10_readiness_blocks_bad_boundary():
    module = importlib.import_module("runtime_core.api.governed_promotion_readiness_ledger")
    bad = sample_audit_boundary()
    bad["runtime_truth_mutation_allowed"] = True

    entry = module.readiness_from_audit_boundary(bad)

    assert entry["status"] == "blocked"
    assert "runtime_truth_mutation_not_locked_false" in entry["blocked_reasons"]
    assert entry["runtime_truth_mutation_allowed"] is False


def test_s39r11_operator_decision_is_record_only():
    module = importlib.import_module("runtime_core.api.governed_promotion_readiness_ledger")
    readiness = module.readiness_from_audit_boundary(sample_audit_boundary())
    decision = module.operator_decision_ledger_entry(
        readiness,
        decision="approved_for_candidate_review",
        reviewer="operator",
        operator_ack="YES",
        notes="candidate reviewed only",
    )

    assert decision["decision"] == "approved_for_candidate_review"
    assert decision["decision_effect"] == "record_only"
    assert decision["promotion_effect"] == "none"
    assert decision["manual_promotion_required"] is True
    assert decision["runtime_truth_mutation_allowed"] is False
    assert len(decision["operator_decision_ledger_sha256"]) == 64


def test_s39r12_builds_ledgers_from_audit_boundary_dir(tmp_path: Path):
    module = importlib.import_module("runtime_core.api.governed_promotion_readiness_ledger")
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir()
    (audit_dir / "CAND-S39-009.audit_boundary.json").write_text(
        json.dumps(sample_audit_boundary(), indent=2),
        encoding="utf-8",
    )

    result = module.build_promotion_readiness_ledgers(
        audit_dir,
        tmp_path / "ledger",
        reviewer="operator",
        decision="approved_for_candidate_review",
        operator_ack="YES",
    )

    summary = result["summary"]
    assert summary["total_audit_boundaries"] == 1
    assert summary["ready_count"] == 1
    assert summary["blocked_count"] == 0
    assert summary["runtime_truth_mutation_allowed"] is False
    assert summary["promotion_effect"] == "none"

    assert Path(result["readiness_ledger"]).exists()
    assert Path(result["operator_decision_ledger"]).exists()
    assert Path(result["summary_path"]).exists()
