from __future__ import annotations

from claire.api.cockpit_validation_lanes import get_validation_lanes


def test_s191_s197_validation_lanes_define_fast_and_full_gates():
    payload = get_validation_lanes()
    lanes = {lane["lane_id"]: lane for lane in payload["lanes"]}

    assert payload["version"] == "v19.89.8-S191-S197"
    assert "fast_smoke" in lanes
    assert "contract_pack" in lanes
    assert "full_pytest" in lanes

    assert lanes["fast_smoke"]["plateau_required"] is False
    assert lanes["contract_pack"]["plateau_required"] is False
    assert lanes["full_pytest"]["plateau_required"] is True
    assert lanes["full_pytest"]["recommended_command"] == "pytest"


def test_s191_s197_validation_lanes_preserve_authority_locks():
    payload = get_validation_lanes()
    locks = payload["authority_locks"]

    assert locks["runtime_truth_write"] is False
    assert locks["runtime_mutation"] is False
    assert locks["automatic_updates"] is False
    assert locks["autonomous_execution"] is False
    assert locks["continuous_crawling"] is False
