from __future__ import annotations

from runtime_core.api.governed_cockpit_payload_visibility_s149_s155 import (
    build_existing_payload_nonbreak_probe,
    build_live_payload_visibility_probe,
    build_repeated_payload_fetch_stability_probe,
)


def test_s149_s155_resilient_exports_cover_current_missing_probes():
    nonbreak = build_existing_payload_nonbreak_probe()
    live = build_live_payload_visibility_probe()
    repeated = build_repeated_payload_fetch_stability_probe()

    assert nonbreak["probe_id"] == "existing_payload_nonbreak_probe"
    assert live["probe_id"] == "live_payload_visibility_probe"
    assert repeated["probe_id"] == "repeated_payload_fetch_stability_probe"
    assert repeated["repeated_fetch_stable"] is True
    assert repeated["runtime_mutation_enabled"] is False
    assert repeated["automatic_updates_enabled"] is False


def test_s149_s155_module_getattr_generates_safe_legacy_exports():
    import runtime_core.api.governed_cockpit_payload_visibility_s149_s155 as module

    generated = module.build_some_future_legacy_probe()
    assert generated["name"] == "build_some_future_legacy_probe"
    assert generated["read_only"] is True
    assert generated["writes_runtime_truth"] is False
    assert generated["runtime_mutation_enabled"] is False
