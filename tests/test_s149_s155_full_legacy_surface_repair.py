from __future__ import annotations

from claire.api.governed_cockpit_payload_visibility_s149_s155 import (
    build_cockpit_payload_read_contract,
    build_governed_cockpit_payload_visibility_s149_s155,
    build_governed_operations_visibility_contract,
    build_live_payload_visibility_contract,
    build_payload_status_visibility_contract,
)


def test_s149_s155_full_legacy_surface_exports_exist_and_preserve_locks():
    read_contract = build_cockpit_payload_read_contract()
    live = build_live_payload_visibility_contract()
    status = build_payload_status_visibility_contract()
    operations = build_governed_operations_visibility_contract()
    payload = build_governed_cockpit_payload_visibility_s149_s155()

    assert read_contract["read_only"] is True
    assert read_contract["runtime_mutation_enabled"] is False
    assert "/dashboard/payload" in read_contract["required_endpoints"]
    assert live["live_payload_visibility"] is True
    assert status["status_endpoint"] == "/dashboard/payload/status"
    assert operations["manual_promotion_required"] is True
    assert payload["backend_owns_truth"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["automatic_updates_enabled"] is False
