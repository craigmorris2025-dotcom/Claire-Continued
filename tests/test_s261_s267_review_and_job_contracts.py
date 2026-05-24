from __future__ import annotations

from runtime_core.api.bounded_web_job_record_contract import get_bounded_web_job_record_contract
from runtime_core.api.operator_review_queue_contract import get_review_queue_contract


def test_s261_s267_review_queue_contract_is_manual_and_non_mutating():
    payload = get_review_queue_contract()
    fields = {field["field"]: field for field in payload["fields"]}

    assert payload["contract_id"] == "operator_review_queue_contract"
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["manual_review_required"] is True
    assert payload["persistence_ready"] is True
    assert fields["review_id"]["mutable"] is False
    assert "approved" in fields["status"]["allowed"]
    assert "needs_more_evidence" in fields["status"]["allowed"]


def test_s261_s267_bounded_web_job_contract_blocks_continuous_crawling():
    payload = get_bounded_web_job_record_contract()
    fields = {field["field"]: field for field in payload["fields"]}

    assert payload["continuous_crawling_enabled"] is False
    assert payload["operator_approval_required"] is True
    assert payload["persistence_ready"] is True
    assert "running_bounded" in payload["allowed_states"]
    assert fields["quarantine_location"]["required"] is True
    assert fields["operator_approved"]["mutable"] is True
