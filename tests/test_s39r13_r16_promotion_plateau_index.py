
from __future__ import annotations

import importlib
import json
from pathlib import Path


def readiness_rows():
    return [
        {
            "candidate_id": "CAND-A",
            "proposal_id": "PROP-A",
            "status": "candidate_review_ready",
            "blocked_reasons": [],
            "proposal_sha256": "a" * 64,
            "approval_record_sha256": "b" * 64,
            "audit_boundary_sha256": "c" * 64,
            "readiness_ledger_sha256": "d" * 64,
        },
        {
            "candidate_id": "CAND-B",
            "proposal_id": "PROP-B",
            "status": "blocked",
            "blocked_reasons": ["runtime_truth_mutation_not_locked_false"],
            "proposal_sha256": "e" * 64,
            "approval_record_sha256": "f" * 64,
            "audit_boundary_sha256": "1" * 64,
            "readiness_ledger_sha256": "2" * 64,
        },
    ]


def decision_rows():
    return [
        {
            "candidate_id": "CAND-A",
            "proposal_id": "PROP-A",
            "decision": "approved_for_candidate_review",
            "decision_effect": "record_only",
            "operator_decision_ledger_sha256": "3" * 64,
        }
    ]


def test_s39r13_builds_package_index_without_authority():
    module = importlib.import_module("claire.api.governed_s39_promotion_plateau_index")
    index = module.build_promotion_package_index(readiness_rows(), decision_rows())

    assert index["candidate_count"] == 2
    assert index["runtime_truth_mutation_allowed"] is False
    assert index["automatic_update_allowed"] is False
    assert index["promotion_effect"] == "none"
    assert index["manual_promotion_required"] is True
    assert len(index["package_index_sha256"]) == 64


def test_s39r14_blocked_candidate_registry():
    module = importlib.import_module("claire.api.governed_s39_promotion_plateau_index")
    registry = module.build_blocked_candidate_registry(readiness_rows())

    assert registry["blocked_count"] == 1
    assert registry["blocked_candidates"][0]["candidate_id"] == "CAND-B"
    assert registry["runtime_truth_mutation_allowed"] is False
    assert registry["promotion_effect"] == "none"


def test_s39r15_replay_verifier_matches_index():
    module = importlib.import_module("claire.api.governed_s39_promotion_plateau_index")
    index = module.build_promotion_package_index(readiness_rows(), decision_rows())
    replay = module.verify_promotion_replay(index, readiness_rows(), decision_rows())

    assert replay["replay_ok"] is True
    assert replay["runtime_truth_mutation_allowed"] is False
    assert replay["promotion_effect"] == "none"


def test_s39r16_writes_plateau_artifacts(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_s39_promotion_plateau_index")
    readiness_path = tmp_path / "promotion_readiness_ledger.jsonl"
    decision_path = tmp_path / "operator_decision_ledger.jsonl"

    readiness_path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in readiness_rows()) + "\n", encoding="utf-8")
    decision_path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in decision_rows()) + "\n", encoding="utf-8")

    result = module.build_s39_plateau_artifacts(readiness_path, decision_path, tmp_path / "out")
    for value in result.values():
        assert Path(value).exists()

    plateau = json.loads(Path(result["plateau_report"]).read_text(encoding="utf-8"))
    assert plateau["status"] == "plateau_ready"
    assert plateau["candidate_count"] == 2
    assert plateau["blocked_count"] == 1
    assert plateau["runtime_truth_mutation_allowed"] is False
    assert plateau["next_phase"] == "S40 backend truth surfaces for cockpit consumption"
