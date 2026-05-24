from __future__ import annotations

from runtime_core.api.governed_cockpit_payload_visibility_s149_s155 import (
    build_existing_payload_nonbreak_probe,
    build_governed_cockpit_payload_visibility_s149_s155,
    build_live_payload_visibility_probe,
)


def test_s149_s155_nonbreak_probe_exports_exist_and_preserve_locks():
    nonbreak = build_existing_payload_nonbreak_probe()
    visibility = build_live_payload_visibility_probe()
    payload = build_governed_cockpit_payload_visibility_s149_s155()

    assert nonbreak["probe_id"] == "existing_payload_nonbreak_probe"
    assert nonbreak["preserves_existing_payload"] is True
    assert nonbreak["nonbreaking"] is True
    assert nonbreak["mutates_payload"] is False
    assert nonbreak["writes_runtime_truth"] is False
    assert visibility["probe_id"] == "live_payload_visibility_probe"
    assert payload["existing_payload_nonbreak_probe"]["runtime_mutation_enabled"] is False
    assert payload["runtime_truth_write_enabled"] is False
