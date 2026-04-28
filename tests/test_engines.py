"""Tests for engine registry and individual engines."""
import pytest
from backend.engines import DOMAIN_REGISTRY, PHASE_SEQUENCE
from backend.engines.base import BaseEngine


class TestEngineRegistry:
    def test_24_engines_registered(self):
        assert len(DOMAIN_REGISTRY) == 24

    def test_6_phases(self):
        assert len(PHASE_SEQUENCE) == 6

    def test_all_engines_are_base_engine(self):
        for key, engine in DOMAIN_REGISTRY.items():
            assert isinstance(engine, BaseEngine), f"{key} is not a BaseEngine"

    def test_all_engines_have_process(self):
        for key, engine in DOMAIN_REGISTRY.items():
            assert hasattr(engine, "process"), f"{key} missing process()"
            assert callable(engine.process)

    def test_all_engines_have_phase(self):
        for key, engine in DOMAIN_REGISTRY.items():
            phase = engine.get_phase()
            assert phase, f"{key} has no phase"

    def test_phase_engine_keys_exist(self):
        for phase_name, engine_keys in PHASE_SEQUENCE:
            for key in engine_keys:
                assert key in DOMAIN_REGISTRY, f"{key} in phase {phase_name} not in registry"

    def test_engine_process_returns_dict(self):
        engine = list(DOMAIN_REGISTRY.values())[0]
        result = engine.process({"raw_input": "test input"}, {})
        assert isinstance(result, dict)
