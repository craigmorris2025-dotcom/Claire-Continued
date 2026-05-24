from __future__ import annotations

from runtime_core.api.governed_evidence_intake_checkpoints import get_evidence_intake_checkpoints


def test_s205_s211_evidence_intake_requires_quarantine_and_manual_promotion():
    payload = get_evidence_intake_checkpoints()

    assert payload["runtime_truth_write_enabled"] is False
    assert payload["manual_promotion_mandatory"] is True
    assert payload["quarantine_mandatory"] is True

    checkpoints = {item["checkpoint_id"]: item for item in payload["checkpoints"]}
    assert checkpoints["quarantine_write"]["quarantine_required"] is True
    assert checkpoints["operator_review"]["promotion_requires_operator"] is True
    assert checkpoints["promotion_candidate"]["promotion_allowed"] is True
    assert checkpoints["promotion_candidate"]["promotion_requires_operator"] is True
