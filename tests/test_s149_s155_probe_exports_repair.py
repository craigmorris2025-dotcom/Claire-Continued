from __future__ import annotations

from claire.api.governed_cockpit_payload_visibility_s149_s155 import (
    build_cockpit_payload_read_contract,
    build_governed_cockpit_payload_visibility_s149_s155,
    build_live_payload_visibility_probe,
)


def test_s149_s155_probe_exports_exist_and_preserve_locks():
    probe = build_live_payload_visibility_probe()
    read_contract = build_cockpit_payload_read_contract()
    payload = build_governed_cockpit_payload_visibility_s149_s155()

    assert probe["probe_id"] == "live_payload_visibility_probe"
    assert probe["allowed_methods"] == ["GET"]
    assert probe["runtime_mutation_enabled"] is False
    assert read_contract["read_only"] is True
    assert payload["live_payload_visibility_probe"]["visible"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["automatic_updates_enabled"] is False
