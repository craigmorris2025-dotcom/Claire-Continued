
from __future__ import annotations


def test_s149_s155_full_export_repair_contract_names():
    from claire.api.governed_cockpit_payload_visibility_s149_s155 import (
        build_dashboard_payload_visibility_contract,
        build_governed_operations_visibility_contract,
        build_live_payload_visibility_contract,
        dashboard_payload_visibility_fragment,
        governed_operations_payload_fragment,
        live_payload_visibility_fragment,
    )

    exports = [
        build_dashboard_payload_visibility_contract(),
        build_governed_operations_visibility_contract(),
        build_live_payload_visibility_contract(),
        dashboard_payload_visibility_fragment(),
        governed_operations_payload_fragment(),
        live_payload_visibility_fragment(),
    ]

    for payload in exports:
        assert payload["ok"] is True
        assert payload["proposal_only"] is True
        assert payload["authority_locks"]["runtime_truth_write_allowed"] is False
        assert payload["authority_locks"]["runtime_mutation_allowed"] is False
        assert payload["authority_locks"]["automatic_updates_allowed"] is False
        assert payload["authority_locks"]["autonomous_execution_allowed"] is False
        assert payload["authority_locks"]["continuous_crawling_allowed"] is False
        assert payload["runtime_truth_modified"] is False
