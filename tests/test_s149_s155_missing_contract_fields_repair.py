from __future__ import annotations

from pathlib import Path

from runtime_core.api.governed_cockpit_payload_visibility_s149_s155 import (
    build_cockpit_live_visibility_readiness,
    build_cockpit_payload_manifest,
    build_cockpit_payload_read_contract,
    build_existing_payload_nonbreak_probe,
    build_live_payload_visibility_probe,
    build_repeated_payload_fetch_stability_probe,
    build_s149_s155_stop_gate,
)


def test_s149_s155_missing_contract_fields_repair_matches_active_test(tmp_path: Path):
    contract = build_cockpit_payload_read_contract()
    assert contract["stage_version"] == "S149"
    assert contract["status"] == "cockpit_payload_read_contract_ready"
    assert contract["payload_key"] == "governed_operations"
    assert contract["read_only"] is True

    probe = build_live_payload_visibility_probe()
    assert probe["stage_version"] == "S150"
    assert probe["ok"] is True
    assert "runtime_spine" in probe["visible_panel_keys"]
    assert "review_export" in probe["visible_panel_keys"]

    nonbreak = build_existing_payload_nonbreak_probe()
    assert nonbreak["stage_version"] == "S151"
    assert nonbreak["ok"] is True
    assert nonbreak["rules"]["governed_operations_appended_only"] is True
    assert nonbreak["rules"]["app_py_patch_performed"] is False

    repeated = build_repeated_payload_fetch_stability_probe(fetch_count=3)
    assert repeated["stage_version"] == "S152"
    assert repeated["ok"] is True
    assert repeated["stable_top_level_keys"] is True
    assert repeated["stable_panel_keys"] is True

    manifest = build_cockpit_payload_manifest()
    assert manifest["stage_version"] == "S153"
    assert manifest["status"] == "cockpit_payload_manifest_ready"
    assert manifest["panel_count"] >= 4

    readiness = build_cockpit_live_visibility_readiness()
    assert readiness["stage_version"] == "S154"
    assert readiness["ok"] is True
    assert readiness["checks"]["runtime_truth_write_blocked"] is True

    report = build_s149_s155_stop_gate(report_dir=tmp_path / "reports")
    assert report["stage_version"] == "S155"
    assert report["ok"] is True
    assert report["forward_motion_allowed"] is True
    assert report["remaining_countdown"]["packs_remaining_after_this"] == 3
    assert Path(report["report_path"]).exists()
