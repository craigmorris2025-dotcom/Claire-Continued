from __future__ import annotations

import importlib


def test_s47r1_live_status_zones_are_visible_and_safe():
    module = importlib.import_module("runtime_core.api.s47_live_status_zones")
    payload = module.build_live_status_zones()

    assert payload["version"] == "v19.89.8-S47R1-R8"
    assert payload["status"] == "live_status_zones_ready"
    assert payload["zone_count"] == 5
    assert payload["backend_owns_truth"] is True
    assert payload["cockpit_presentation_only"] is True
    assert payload["runtime_truth_mutation_allowed"] is False
    assert payload["operator_mutation_enabled"] is False

    states = {zone["zone_id"]: zone["state"] for zone in payload["zones"]}
    assert states["authority"] == "locked"
    assert states["governed_web"] == "fail_closed"
    assert states["evidence_review"] == "manual_review"

    for zone in payload["zones"]:
        assert zone["visible"] is True
        assert zone["presentation_only"] is True
        assert zone["runtime_truth_mutation_allowed"] is False
        assert zone["response_mode"] == "read_only_artifact"


def test_s47r4_live_status_zones_verify_cleanly():
    module = importlib.import_module("runtime_core.api.s47_live_status_zones")
    verification = module.verify_live_status_zones()

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["zone_count"] == 5
