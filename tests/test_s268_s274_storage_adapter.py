from __future__ import annotations

from claire.api.operator_workflow_storage_adapter import (
    append_workflow_record,
    get_storage_adapter_contract,
    get_workflow_counts,
    list_workflow_records,
)


def test_s268_s274_storage_adapter_contract_is_operator_scope_and_non_mutating():
    payload = get_storage_adapter_contract()

    assert payload["version"] == "v19.89.8-S268-S274"
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["runtime_mutation_enabled"] is False
    assert payload["persistence_ready"] is True
    assert "review_queue" in payload["collections"]
    assert "bounded_web_jobs" in payload["collections"]
    assert "exports" in payload["collections"]
    assert "audit_trail" in payload["collections"]


def test_s268_s274_storage_adapter_appends_safe_operator_records():
    before = get_workflow_counts()["counts"]["review_queue"]
    result = append_workflow_record("review_queue", {
        "review_id": "s268-test-review",
        "status": "pending",
        "evidence_basket_id": "basket-test",
    })
    after = get_workflow_counts()["counts"]["review_queue"]
    records = list_workflow_records("review_queue")

    assert result["stored"] is True
    assert result["runtime_truth_write"] is False
    assert result["runtime_mutation"] is False
    assert after == before + 1
    assert records[-1]["storage_scope"] == "operator_workflow_only"
    assert records[-1]["runtime_truth_write"] is False
