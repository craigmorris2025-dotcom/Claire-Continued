from claire.pilot_operations.pilot_acceptance_criteria import PilotAcceptanceCriteria
from claire.pilot_operations.pilot_run_registry import PilotRunRegistry

def test_pilot_run_registry():
    run = PilotRunRegistry().create_pilot_run("p1", "test pilot")
    assert run["status"] == "created"

def test_pilot_acceptance_blocks_empty():
    result = PilotAcceptanceCriteria().evaluate({})
    assert result["status"] == "blocked"
