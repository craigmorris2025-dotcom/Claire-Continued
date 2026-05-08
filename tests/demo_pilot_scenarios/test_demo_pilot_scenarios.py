from claire.demo_pilot_scenarios.demo_readiness_check import DemoReadinessCheck
from claire.demo_pilot_scenarios.sample_input_library import SampleInputLibrary

def test_demo_readiness_blocks_missing():
    assert DemoReadinessCheck().evaluate({})["status"] == "blocked"

def test_sample_inputs_exist():
    assert len(SampleInputLibrary().default_inputs()) >= 3
