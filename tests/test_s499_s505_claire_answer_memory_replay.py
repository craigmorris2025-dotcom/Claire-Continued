from __future__ import annotations

import importlib
from pathlib import Path


def test_s499_memory_schema_is_ready_and_safe():
    module = importlib.import_module("claire.api.claire_answer_memory_replay_s499_s505")

    schema = module.build_s499_answer_memory_schema()
    assert "memory_id" in schema["memory_record_fields"]
    assert "replay_trace" in schema["memory_record_fields"]
    assert "replay_ready" in schema["replay_statuses"]

    for flag in module.BLOCKED_AUTHORITY:
        assert schema[flag] is False


def test_s500_build_answer_memory_record_from_preview():
    module = importlib.import_module("claire.api.claire_answer_memory_replay_s499_s505")
    preview_module = importlib.import_module("claire.api.claire_useful_output_package_preview_s492_s498")

    preview = preview_module.build_useful_output_package_preview(
        "Can Claire build a market trend brief with portfolio implications?",
        preferred_package_type="market_brief",
        preferred_domain="market",
    )
    record = module.build_answer_memory_record(preview["question"], package_preview=preview)

    assert record["memory_id"].startswith("answer_memory_")
    assert record["package_type"] == "market_brief"
    assert record["replay_trace"]["trace_available"] is True
    assert record["governance"]["memory_record_only"] is True
    assert record["governance"]["persistent_write_performed"] is False

    for flag in module.BLOCKED_AUTHORITY:
        assert record[flag] is False
        assert record["governance"][flag] is False


def test_s501_memory_index_groups_records_without_persistent_write():
    module = importlib.import_module("claire.api.claire_answer_memory_replay_s499_s505")
    preview_module = importlib.import_module("claire.api.claire_useful_output_package_preview_s492_s498")

    market = preview_module.build_useful_output_package_preview(
        "Can Claire build a market trend brief?",
        preferred_package_type="market_brief",
        preferred_domain="market",
    )
    engineering = preview_module.build_useful_output_package_preview(
        "Can Claire build an engineering feasibility preview?",
        preferred_package_type="engineering_feasibility_preview",
        preferred_domain="engineering",
    )

    records = [
        module.build_answer_memory_record(market["question"], package_preview=market),
        module.build_answer_memory_record(engineering["question"], package_preview=engineering),
    ]
    index = module.build_answer_memory_index(records)

    assert index["record_count"] == 2
    assert "market_brief" in index["by_package_type"]
    assert "engineering_feasibility_preview" in index["by_package_type"]
    assert index["persistent_memory_write_performed"] is False


def test_s502_replay_is_reference_only_and_safe():
    module = importlib.import_module("claire.api.claire_answer_memory_replay_s499_s505")

    record = module.build_answer_memory_record("Can Claire produce a useful market package?")
    replay = module.replay_answer_memory_record(record, "Replay this for comparison.")

    assert replay["replay_id"].startswith("answer_replay_")
    assert replay["status"] in module.REPLAY_STATUS
    assert replay["governance"]["reference_only"] is True
    assert replay["governance"]["runtime_truth_write_allowed"] is False
    assert "mutate_runtime_truth" in replay["blocked_use"]

    for flag in module.BLOCKED_AUTHORITY:
        assert replay[flag] is False
        assert replay["governance"][flag] is False


def test_s503_memory_comparison_is_operator_review_only():
    module = importlib.import_module("claire.api.claire_answer_memory_replay_s499_s505")
    preview_module = importlib.import_module("claire.api.claire_useful_output_package_preview_s492_s498")

    left_preview = preview_module.build_useful_output_package_preview(
        "Can Claire build a market trend brief?",
        preferred_package_type="market_brief",
        preferred_domain="market",
    )
    right_preview = preview_module.build_useful_output_package_preview(
        "Can Claire build an engineering feasibility preview?",
        preferred_package_type="engineering_feasibility_preview",
        preferred_domain="engineering",
    )

    left = module.build_answer_memory_record(left_preview["question"], package_preview=left_preview)
    right = module.build_answer_memory_record(right_preview["question"], package_preview=right_preview)
    comparison = module.compare_memory_records(left, right)

    assert comparison["comparison_id"].startswith("memory_comparison_")
    assert comparison["same_package_type"] is False
    assert comparison["comparison_use"] == "operator_review_only"

    for flag in module.BLOCKED_AUTHORITY:
        assert comparison[flag] is False


def test_s504_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_answer_memory_replay.js"
    css = root / "frontend/cockpit/shell/assets/claire_answer_memory_replay.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireAnswerMemoryReplayVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "persistentMemoryWritePerformed: false" in text
    assert "recursiveSelfIngestionExecuted: false" in text


def test_s505_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("claire.api.claire_answer_memory_replay_s499_s505")

    gate = module.build_s505_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["no_persistent_write"] is True
    assert gate["checks"]["no_recursive_self_ingestion_execution"] is True
    assert (tmp_path / "s505_claire_answer_memory_replay_stop_gate.json").exists()


def test_s499_s505_rollup_ready():
    module = importlib.import_module("claire.api.claire_answer_memory_replay_s499_s505")

    rollup = module.build_claire_answer_memory_replay_s499_s505(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s499"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["persistent_memory_write_performed"] is False
    assert rollup["recursive_self_ingestion_executed"] is False
