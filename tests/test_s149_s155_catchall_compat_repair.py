from __future__ import annotations


def test_s149_s155_catchall_compat_exports_all_known_missing_names():
    from claire.api.governed_cockpit_payload_visibility_s149_s155 import (
        build_governed_operations_visibility_contract,
        build_live_payload_visibility_contract,
        build_payload_status_visibility_contract,
        governed_operations_payload_fragment,
        live_payload_visibility_fragment,
        payload_status_visibility_fragment,
    )

    payloads = [
        build_governed_operations_visibility_contract(),
        build_live_payload_visibility_contract(),
        build_payload_status_visibility_contract(),
        governed_operations_payload_fragment(),
        live_payload_visibility_fragment(),
        payload_status_visibility_fragment(),
    ]

    for payload in payloads:
        assert payload["ok"] is True
        assert payload["proposal_only"] is True
        assert payload["authority_locks"]["runtime_truth_write_allowed"] is False
        assert payload["authority_locks"]["runtime_mutation_allowed"] is False
        assert payload["authority_locks"]["automatic_updates_allowed"] is False
        assert payload["authority_locks"]["autonomous_execution_allowed"] is False
        assert payload["authority_locks"]["continuous_crawling_allowed"] is False
        assert payload["runtime_truth_modified"] is False


def test_s149_s155_catchall_dynamic_future_visibility_name():
    import claire.api.governed_cockpit_payload_visibility_s149_s155 as module

    dynamic = module.build_future_unknown_payload_visibility_contract()
    assert dynamic["ok"] is True
    assert dynamic["proposal_only"] is True
    assert dynamic["authority_locks"]["runtime_truth_write_allowed"] is False
