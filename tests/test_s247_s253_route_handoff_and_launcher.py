from __future__ import annotations

from pathlib import Path

from claire.api.cockpit_launcher_handoff_metadata import get_launcher_handoff_metadata
from claire.api.cockpit_route_handoff_manifest import get_cockpit_route_handoff_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_s247_s253_route_handoff_prefers_modern_cockpit_shell_and_backend_truth():
    payload = get_cockpit_route_handoff_manifest()
    routes = {route["route_id"]: route for route in payload["routes"]}

    assert payload["handoff_id"] == "modern_cockpit_route_handoff"
    assert payload["preferred_cockpit_shell"] == "frontend/cockpit/modern/claire_cockpit_shell.html"
    assert payload["backend_required"] is True
    assert payload["unsafe_authority_enabled"] is False
    assert routes["canonical_payload"]["path"] == "/dashboard/payload"
    assert routes["health"]["path"] == "/health"
    assert (ROOT / payload["preferred_cockpit_shell"]).exists()


def test_s247_s253_launcher_handoff_metadata_points_to_modern_shell_without_enabling_unsafe_authority():
    payload = get_launcher_handoff_metadata()

    assert payload["launcher_target"] == "frontend/cockpit/modern/claire_cockpit_shell.html"
    assert payload["backend_base_url"] == "http://127.0.0.1:8000"
    assert "/health" in payload["must_check_before_open"]
    assert "/dashboard/payload/status" in payload["must_check_before_open"]
    assert payload["live_payload_requires_backend"] is True
    assert payload["unsafe_authority_enabled"] is False
