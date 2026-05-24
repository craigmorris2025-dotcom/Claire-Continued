from __future__ import annotations

import importlib
from pathlib import Path


def test_s527_evidence_item_schema_and_item_are_safe():
    module = importlib.import_module("runtime_core.api.update_evidence_review_queue_s527_s533")

    schema = module.build_s527_update_evidence_item_schema()
    item = module.make_update_evidence_item(
        "operator_note",
        "Operator note",
        "Sample note",
        "test",
        "sample_source",
    )

    assert "inspection_metadata" in schema["evidence_types"]
    assert item["evidence_id"].startswith("update_evidence_")
    assert item["capture_scope"] == "in_memory_payload_only"

    for flag in module.BLOCKED_AUTHORITY:
        assert item[flag] is False


def test_s528_capture_bundle_uses_existing_payloads_only():
    module = importlib.import_module("runtime_core.api.update_evidence_review_queue_s527_s533")

    bundle = module.capture_update_evidence_bundle()
    assert bundle["evidence_bundle_id"].startswith("update_evidence_bundle_")
    assert bundle["item_count"] >= 5
    assert bundle["capture_scope"] == "in_memory_payload_only"
    assert any(item["evidence_type"] == "command_manifest" for item in bundle["items"])

    for flag in module.BLOCKED_AUTHORITY:
        assert bundle[flag] is False


def test_s529_operator_review_packet_and_s530_queue_are_review_only():
    module = importlib.import_module("runtime_core.api.update_evidence_review_queue_s527_s533")

    bundle = module.capture_update_evidence_bundle()
    packet = module.build_operator_review_packet(bundle, operator_note="review this")
    queue = module.build_operator_review_queue([packet])

    assert packet["review_packet_id"].startswith("operator_review_packet_")
    assert packet["review_only"] is True
    assert packet["decision_execution_allowed"] is False
    assert packet["queue_persistent_write_allowed"] is False

    assert queue["packet_count"] == 1
    assert queue["queue_persistent_write_performed"] is False
    assert packet["review_packet_id"] in sum(queue["by_status"].values(), [])

    for flag in module.BLOCKED_AUTHORITY:
        assert packet[flag] is False
        assert queue[flag] is False


def test_blocked_candidate_stays_visible_in_queue_and_recommendation_rejects():
    module = importlib.import_module("runtime_core.api.update_evidence_review_queue_s527_s533")
    inspector = importlib.import_module("runtime_core.api.governed_update_inspector_s506_s512")

    blocked_inspection = inspector.inspect_update_package_candidate(
        inspector.build_sample_update_candidate(
            package_id="blocked_queue_test",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            apply_allowed=True,
        )
    )
    bundle = module.capture_update_evidence_bundle(inspection=blocked_inspection)
    packet = module.build_operator_review_packet(bundle)
    queue = module.build_operator_review_queue([packet])
    decision = module.build_review_decision_recommendation(packet)

    assert packet["review_status"] == "blocked"
    assert packet["blockers"]
    assert packet["review_packet_id"] in queue["blocked_packets"]
    assert decision["recommendation"] == "reject_candidate"
    assert decision["decision_execution_allowed"] is False
    assert decision["can_apply_update"] is False


def test_s531_decision_recommendation_is_not_execution():
    module = importlib.import_module("runtime_core.api.update_evidence_review_queue_s527_s533")

    packet = module.build_operator_review_packet()
    decision = module.build_review_decision_recommendation(packet)

    assert decision["allowed_result"] == "operator_review_recommendation_only"
    assert decision["operator_decision_execution_performed"] is False
    assert decision["can_promote_update"] is False
    assert decision["can_apply_update"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert decision[flag] is False


def test_s532_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_update_evidence_review_queue.js"
    css = root / "frontend/cockpit/shell/assets/claire_update_evidence_review_queue.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireUpdateEvidenceReviewQueueVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "queuePersistentWritePerformed: false" in text
    assert "operatorDecisionExecutionPerformed: false" in text


def test_s533_stop_gate_allows_forward_motion_and_marks_stop_point(tmp_path):
    module = importlib.import_module("runtime_core.api.update_evidence_review_queue_s527_s533")

    gate = module.build_s533_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert "STOP POINT A" in gate["stop_point"]
    assert gate["checks"]["blocked_packet_visible"] is True
    assert gate["checks"]["no_queue_persistence"] is True
    assert (tmp_path / "s533_claire_update_evidence_review_queue_stop_gate.json").exists()


def test_s527_s533_rollup_ready():
    module = importlib.import_module("runtime_core.api.update_evidence_review_queue_s527_s533")

    rollup = module.build_update_evidence_review_queue_s527_s533(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s527"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["queue_persistent_write_performed"] is False
    assert rollup["operator_decision_execution_performed"] is False
