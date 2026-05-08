from claire.lifecycle.stage_registry import ClaireStageRegistry
from claire.lifecycle.threshold_provenance import ThresholdProvenance


def test_stage_registry_matches_claire_lifecycle_spine():
    registry = ClaireStageRegistry()
    payload = registry.as_payload()

    assert payload["stage_count"] == 21
    assert payload["stages"][0]["slug"] == "ingestion"
    assert payload["stages"][7]["slug"] == "breakthrough_synthesis"
    assert payload["stages"][-1]["slug"] == "deal_exit_modeling"
    assert "market_gap" in payload["output_key_map"]


def test_threshold_provenance_exposes_calibration_inputs_and_gates():
    provenance = ThresholdProvenance().as_payload()
    rule_ids = {rule["id"] for rule in provenance["threshold_rules"]}
    fixture_ids = {item["id"] for item in provenance["calibration_inputs"]}

    assert "pipeline_decision_go" in rule_ids
    assert "pipeline_breakthrough_high" in rule_ids
    assert "pipeline_ready_for_syntalion" in rule_ids
    assert {"defense_control_gated", "climate_insurance", "routing_stress_insurance"} <= fixture_ids
