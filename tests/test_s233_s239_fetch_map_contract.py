from __future__ import annotations

from runtime_core.api.cockpit_fetch_map_contract import get_cockpit_fetch_map_contract


def test_s233_s239_fetch_map_is_read_only_and_prevents_endpoint_invention():
    payload = get_cockpit_fetch_map_contract()

    assert payload["fetch_map_id"] == "safe_cockpit_fetch_map"
    assert payload["frontend_may_invent_endpoints"] is False
    assert payload["unsafe_methods_allowed"] is False
    assert payload["allowed_methods"] == ["GET"]

    endpoints = {endpoint["endpoint_id"]: endpoint for endpoint in payload["endpoints"]}
    assert endpoints["canonical_payload"]["path"] == "/dashboard/payload"
    assert endpoints["canonical_payload"]["required"] is True
    assert endpoints["health"]["required"] is True
    assert endpoints["governed_live_search"]["authority"] == "operator_requested"
