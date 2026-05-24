from __future__ import annotations

from runtime_core.api.governed_operational_payload_adapter import (
    get_governed_operational_payload,
    list_dashboard_section_ids,
)


def test_s212_s218_operational_payload_is_dashboard_consumable_and_backend_owned():
    payload = get_governed_operational_payload()

    assert payload["payload_contract"] == "governed_operational_payload_adapter"
    assert payload["backend_owns_truth"] is True
    assert payload["cockpit_presentation_only"] is True

    section_ids = set(list_dashboard_section_ids())
    assert {
        "internet_operations",
        "operator_review",
        "governance",
        "monitoring",
    }.issubset(section_ids)


def test_s212_s218_operational_payload_preserves_authority_locks():
    locks = get_governed_operational_payload()["authority_locks"]

    assert locks["runtime_truth_write"] is False
    assert locks["runtime_mutation"] is False
    assert locks["automatic_updates"] is False
    assert locks["autonomous_execution"] is False
    assert locks["continuous_crawling"] is False
