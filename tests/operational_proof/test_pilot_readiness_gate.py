from claire.operational_proof.pilot_readiness_gate import PilotReadinessGate

def test_pilot_gate_blocks_low_scores():
    decision = PilotReadinessGate().evaluate({})
    assert decision["status"] == "blocked"
    assert decision["failures"]
