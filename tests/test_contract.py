"""Tests for CLAIRE Contract Layer."""
import pytest
from backend.claire.contract import ClaireIntent, ClaireResult, ContractValidator


class TestClaireIntent:
    def test_create_intent(self, sample_input):
        intent = ClaireIntent(raw_input=sample_input, mode="deterministic")
        assert intent.raw_input == sample_input
        assert intent.mode == "deterministic"
        assert intent.id.startswith("intent-")

    def test_validate_valid_intent(self, sample_intent):
        errors = sample_intent.validate()
        assert errors == []

    def test_validate_empty_input(self):
        intent = ClaireIntent(raw_input="", mode="deterministic")
        errors = intent.validate()
        assert any("raw_input" in e for e in errors)

    def test_validate_invalid_mode(self, sample_input):
        intent = ClaireIntent(raw_input=sample_input, mode="invalid")
        errors = intent.validate()
        assert any("mode" in e.lower() for e in errors)

    def test_to_dict(self, sample_intent):
        d = sample_intent.to_dict()
        assert "id" in d
        assert d["raw_input"] == sample_intent.raw_input
        assert d["mode"] == "deterministic"


class TestClaireResult:
    def test_create_result(self):
        result = ClaireResult()
        assert result.status == "success"
        assert result.scores == {}

    def test_to_dict(self):
        result = ClaireResult(intent_id="test-001", mode="hybrid")
        d = result.to_dict()
        assert d["intent_id"] == "test-001"
        assert d["mode"] == "hybrid"
        assert "scores" in d


class TestContractValidator:
    def test_validate_input_ok(self, sample_intent):
        v = ContractValidator()
        errors = v.validate_input(sample_intent)
        assert errors == []

    def test_validate_input_empty(self):
        v = ContractValidator()
        intent = ClaireIntent(raw_input="", mode="deterministic")
        errors = v.validate_input(intent)
        assert len(errors) > 0
