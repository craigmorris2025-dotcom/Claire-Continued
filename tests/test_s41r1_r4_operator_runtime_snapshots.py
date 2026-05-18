
from __future__ import annotations

import importlib
import json
from pathlib import Path


def sample_payload():
    return {
        "available": True,
        "operator_payload_sha256": "o" * 64,
        "lineage": {"backend_truth_payload_sha256": "b" * 64},
        "sections": [
            {"section": "system_status", "available": True, "summary": {}, "runtime_truth_mutation_allowed": False},
            {"section": "research_queue", "available": False, "summary": {"reason": "missing"}, "path": "output/q", "runtime_truth_mutation_allowed": False},
        ],
    }


def test_s41r1_operator_state_snapshot_is_backend_authoritative():
    module = importlib.import_module("claire.api.governed_operator_runtime_snapshots")
    snapshot = module.build_operator_state_snapshot(sample_payload())

    assert snapshot["backend_owns_truth"] is True
    assert snapshot["cockpit_presentation_only"] is True
    assert snapshot["section_count"] == 2
    assert snapshot["available_section_count"] == 1
    assert snapshot["unavailable_section_count"] == 1
    assert snapshot["runtime_truth_mutation_allowed"] is False
    assert snapshot["automatic_update_allowed"] is False
    assert len(snapshot["operator_state_snapshot_sha256"]) == 64


def test_s41r2_bounded_runtime_summary_is_read_only():
    module = importlib.import_module("claire.api.governed_operator_runtime_snapshots")
    snapshot = module.build_operator_state_snapshot(sample_payload())
    summary = module.build_bounded_runtime_summary(snapshot)

    assert summary["status"] == "partial_surfaces_available"
    assert summary["backend_owns_truth"] is True
    assert summary["cockpit_presentation_only"] is True
    assert summary["runtime_truth_mutation_allowed"] is False
    assert summary["automatic_update_allowed"] is False
    assert len(summary["bounded_runtime_summary_sha256"]) == 64


def test_s41r3_snapshot_lineage_preserves_source_chain():
    module = importlib.import_module("claire.api.governed_operator_runtime_snapshots")
    payload = sample_payload()
    snapshot = module.build_operator_state_snapshot(payload)
    summary = module.build_bounded_runtime_summary(snapshot)
    lineage = module.build_snapshot_lineage(payload, snapshot, summary)

    assert lineage["operator_payload_sha256"] == "o" * 64
    assert lineage["source_lineage"]["backend_truth_payload_sha256"] == "b" * 64
    assert lineage["runtime_truth_mutation_allowed"] is False
    assert lineage["automatic_update_allowed"] is False
    assert len(lineage["snapshot_lineage_sha256"]) == 64


def test_s41r4_verification_and_file_write(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_operator_runtime_snapshots")
    source_dir = tmp_path / "output" / "unified_operator_payload"
    source_dir.mkdir(parents=True)
    (source_dir / "unified_backend_operator_payload.json").write_text(json.dumps(sample_payload()), encoding="utf-8")

    result = module.write_operator_runtime_snapshots(tmp_path, tmp_path / "out")

    assert set(result) == {"snapshot", "summary", "lineage", "verification"}
    for value in result.values():
        assert Path(value).exists()

    verification = json.loads(Path(result["verification"]).read_text(encoding="utf-8"))
    assert verification["verification_ok"] is True
    assert verification["runtime_truth_mutation_allowed"] is False
