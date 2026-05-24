from __future__ import annotations

from runtime_core.api.export_artifact_record_contract import get_export_artifact_record_contract
from runtime_core.api.operator_audit_trail_contract import get_operator_audit_trail_contract


def test_s261_s267_export_artifact_contract_requires_operator_approval_and_lineage():
    payload = get_export_artifact_record_contract()
    fields = {field["field"]: field for field in payload["fields"]}

    assert payload["operator_approval_required"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["persistence_ready"] is True
    assert fields["source_lineage_hash"]["required"] is True
    assert "portfolio_package" in fields["artifact_type"]["allowed"]
    assert "design_package" in fields["artifact_type"]["allowed"]


def test_s261_s267_operator_audit_trail_is_append_only_and_non_mutating():
    payload = get_operator_audit_trail_contract()
    events = {event["event_type"]: event for event in payload["events"]}

    assert payload["append_only"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["persistence_ready"] is True
    assert events["blocked_action_attempted"]["writes_runtime_truth"] is False
    assert events["promotion_candidate_approved"]["requires_operator"] is True
    assert events["export_created"]["writes_runtime_truth"] is False
