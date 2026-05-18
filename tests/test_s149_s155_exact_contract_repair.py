from __future__ import annotations

from claire.api.governed_cockpit_payload_visibility_s149_s155 import (
    build_cockpit_live_visibility_readiness,
    build_cockpit_payload_manifest,
    build_cockpit_payload_read_contract,
    build_existing_payload_nonbreak_probe,
    build_live_payload_visibility_probe,
    build_repeated_payload_fetch_stability_probe,
    build_s149_s155_stop_gate,
)


def test_s149_s155_exact_stage_versions_match_legacy_test_expectations():
    assert build_cockpit_payload_read_contract()["stage_version"] == "S149"
    assert build_live_payload_visibility_probe()["stage_version"] == "S150"
    assert build_existing_payload_nonbreak_probe()["stage_version"] == "S151"
    assert build_repeated_payload_fetch_stability_probe(fetch_count=3)["stage_version"] == "S152"
    assert build_cockpit_payload_manifest()["stage_version"] == "S153"
    assert build_cockpit_live_visibility_readiness()["stage_version"] == "S154"
    assert build_s149_s155_stop_gate()["stage_version"] == "S155"


def test_s149_s155_exact_contract_preserves_authority_locks():
    for payload in [
        build_cockpit_payload_read_contract(),
        build_live_payload_visibility_probe(),
        build_existing_payload_nonbreak_probe(),
        build_repeated_payload_fetch_stability_probe(fetch_count=3),
        build_cockpit_payload_manifest(),
        build_cockpit_live_visibility_readiness(),
        build_s149_s155_stop_gate(),
    ]:
        assert payload["runtime_truth_write_enabled"] is False
        assert payload["runtime_mutation_enabled"] is False
        assert payload["automatic_updates_enabled"] is False
        assert payload["autonomous_execution_enabled"] is False
