from __future__ import annotations

from claire.api.internet_operation_readiness_snapshot import get_internet_operation_readiness_snapshot


def test_s205_s211_internet_operation_readiness_snapshot_preserves_locks():
    payload = get_internet_operation_readiness_snapshot()
    readiness = payload["readiness"]

    assert payload["plateau"] == "governed_internet_operation_readiness"
    assert readiness["bounded_web_jobs"] == "contract_ready"
    assert readiness["evidence_intake"] == "checkpoint_ready"
    assert readiness["quarantine"] == "mandatory"
    assert readiness["manual_review"] == "mandatory"
    assert readiness["update_proposals"] == "proposal_only"
    assert readiness["continuous_crawling"] == "blocked"
    assert readiness["automatic_updates"] == "blocked"
    assert readiness["runtime_mutation"] == "blocked"
