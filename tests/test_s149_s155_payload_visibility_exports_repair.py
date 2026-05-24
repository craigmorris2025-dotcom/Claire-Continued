from __future__ import annotations

from runtime_core.api.governed_cockpit_payload_visibility_s149_s155 import (
    build_s149_s155_live_payload_visibility,
    get_governed_cockpit_payload_visibility_s149_s155,
)
from runtime_core.api.governed_payload_bridge_live_patch_s142_s148 import (
    governed_operations_payload_fragment,
)


def test_s149_s155_payload_visibility_exports_repair():
    fragment = governed_operations_payload_fragment()
    payload = build_s149_s155_live_payload_visibility()
    getter = get_governed_cockpit_payload_visibility_s149_s155()

    assert fragment["fragment_id"] == "governed_operations_payload_fragment"
    assert fragment["governed_operations"]["runtime_mutation_enabled"] is False
    assert payload["cockpit_payload_visibility"] is True
    assert payload["runtime_truth_write_enabled"] is False
    assert payload["automatic_updates_enabled"] is False
    assert getter["backend_owns_truth"] is True
