from __future__ import annotations


def test_s289_s295_compat_repair_restores_s149_s183_import_contracts():
    from runtime_core.api.governed_cockpit_payload_visibility_s149_s155 import (
        build_governed_operations_visibility_contract,
        governed_operations_payload_fragment,
    )

    fragment = governed_operations_payload_fragment()
    contract = build_governed_operations_visibility_contract()

    assert fragment["proposal_only"] is True
    assert fragment["authority_locks"]["runtime_truth_write_allowed"] is False
    assert fragment["authority_locks"]["runtime_mutation_allowed"] is False
    assert fragment["authority_locks"]["automatic_updates_allowed"] is False
    assert fragment["authority_locks"]["autonomous_execution_allowed"] is False
    assert fragment["authority_locks"]["continuous_crawling_allowed"] is False

    assert contract["proposal_only"] is True
    assert contract["authority_locks"]["runtime_truth_write_allowed"] is False
    assert "authority_locks" in contract["required_fields"]
    assert "proposal_only" in contract["required_fields"]
