from __future__ import annotations

import json
from pathlib import Path

from claire.api.governed_manual_promotion_candidates import (
    LOCKED_AUTHORITY,
    build_evidence_review_manifest,
    score_promotion_candidate,
    build_lineage_contradiction_registry,
    build_manual_promotion_package,
    run_s38r9_r12_pipeline,
)


def _write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_s38r9_builds_review_manifest_without_runtime_truth_mutation(tmp_path: Path):
    extraction = _write_json(tmp_path / "output" / "structured_knowledge" / "sample.extraction.json", {"claims": [{"claim_id": "c1", "claim_type": "version", "subject": "Claire", "predicate": "phase", "value": "S38", "claim_text": "Claire is in S38 governed evidence extraction.", "confidence": "requires_review"}]})
    basket = _write_json(tmp_path / "output" / "evidence_baskets" / "sample.basket.json", {"evidence_sha256": "abc123", "items": [{"source": "approved"}]})
    manifest = build_evidence_review_manifest(tmp_path, extraction, basket)
    assert manifest["schema_version"] == "s38r9.review_manifest.v1"
    assert manifest["manual_promotion_required"] is True
    assert manifest["runtime_truth_mutated"] is False
    assert manifest["promotion_state"] == "not_promoted"
    assert manifest["claim_count"] == 1
    assert manifest["locked_authority"]["runtime_truth_mutation_blocked"] is True


def test_s38r10_scores_candidate_as_manual_review_only(tmp_path: Path):
    extraction = _write_json(tmp_path / "output" / "structured_knowledge" / "sample.json", {"claims": ["A governed claim"]})
    basket = _write_json(tmp_path / "output" / "evidence_baskets" / "sample.json", {"evidence_sha256": "abc"})
    manifest = build_evidence_review_manifest(tmp_path, extraction, basket)
    score = score_promotion_candidate(tmp_path)
    assert score["schema_version"] == "s38r10.promotion_candidate_score.v1"
    assert score["candidate_id"] == manifest["candidate_id"]
    assert score["runtime_truth_mutated"] is False
    assert score["manual_promotion_required"] is True
    assert score["promotion_state"] == "not_promoted"
    assert score["promotion_readiness_score"] >= 70


def test_s38r11_registry_tracks_lineage_and_contradictions(tmp_path: Path):
    extraction = _write_json(tmp_path / "output" / "structured_knowledge" / "sample.json", {"claims": [{"claim_id": "c1", "claim_type": "status", "subject": "source", "predicate": "state", "value": "approved"}, {"claim_id": "c2", "claim_type": "status", "subject": "source", "predicate": "state", "value": "rejected"}]})
    basket = _write_json(tmp_path / "output" / "evidence_baskets" / "sample.json", {"evidence_sha256": "abc"})
    build_evidence_review_manifest(tmp_path, extraction, basket)
    registry = build_lineage_contradiction_registry(tmp_path)
    assert registry["schema_version"] == "s38r11.lineage_contradiction_registry.v1"
    assert registry["runtime_truth_mutated"] is False
    assert registry["promotion_state"] == "not_promoted"
    assert registry["contradiction_count"] == 1
    assert registry["claim_lineage"]


def test_s38r12_package_blocks_when_contradictions_exist(tmp_path: Path):
    extraction = _write_json(tmp_path / "output" / "structured_knowledge" / "sample.json", {"claims": [{"claim_id": "c1", "claim_type": "status", "subject": "source", "predicate": "state", "value": "approved"}, {"claim_id": "c2", "claim_type": "status", "subject": "source", "predicate": "state", "value": "rejected"}]})
    basket = _write_json(tmp_path / "output" / "evidence_baskets" / "sample.json", {"evidence_sha256": "abc"})
    build_evidence_review_manifest(tmp_path, extraction, basket)
    score_promotion_candidate(tmp_path)
    build_lineage_contradiction_registry(tmp_path)
    package = build_manual_promotion_package(tmp_path)
    assert package["schema_version"] == "s38r12.manual_promotion_package.v1"
    assert package["runtime_truth_mutated"] is False
    assert package["automatic_update_performed"] is False
    assert package["manual_promotion_required"] is True
    assert package["package_state"] == "manual_review_blocked_pending_resolution"
    assert any("contradictions" in reason for reason in package["blocked_reasons"])


def test_s38r9_r12_pipeline_completes_without_forbidden_authority(tmp_path: Path):
    _write_json(tmp_path / "output" / "structured_knowledge" / "sample.json", {"claims": ["A governed claim"]})
    _write_json(tmp_path / "output" / "evidence_baskets" / "sample.json", {"evidence_sha256": "abc"})
    result = run_s38r9_r12_pipeline(tmp_path)
    assert result["status"] == "manual_promotion_candidate_pipeline_complete"
    assert result["runtime_truth_mutated"] is False
    assert result["automatic_update_performed"] is False
    assert result["manual_promotion_required"] is True
    assert result["locked_authority"] == LOCKED_AUTHORITY
