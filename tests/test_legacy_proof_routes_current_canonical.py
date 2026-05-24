from __future__ import annotations

from fastapi.testclient import TestClient

from runtime_core.app import create_app


def test_legacy_e2e_proof_route_uses_current_dashboard_and_is_not_stop():
    client = TestClient(create_app())

    payload = client.get("/proof/e2e/summary").json()

    assert payload["status"] in {"GO_WITH_WARNINGS", "GO_TO_MANUAL_REVIEW"}
    assert payload["stop_go"]["blocked_domains"] == []
    assert payload["domain_status"]["dashboard_functionality"] == "passed"
    assert payload["automatic_updates_enabled"] is False
    assert payload["live_internet_enabled"] is False


def test_platform_smoke_proof_route_passes_current_canonical_endpoints():
    client = TestClient(create_app())

    payload = client.get("/proof/platform-smoke/summary").json()

    assert payload["status"] == "GO_TO_PLATFORM_LAUNCH_HARDENING"
    assert payload["stop_go"]["blockers"] == []
    assert payload["domain_status"]["updates"] == "passed"
    assert payload["domain_status"]["proof"] == "passed"

