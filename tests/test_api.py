"""Tests for API schemas and data validation."""
import pytest
from pydantic import ValidationError


class TestSchemas:
    def test_evaluate_request_valid(self):
        from backend.api.schemas import EvaluateRequest
        req = EvaluateRequest(input_text="Test input for evaluation")
        assert req.mode == "deterministic"
        assert req.source == "api"

    def test_evaluate_request_too_short(self):
        from backend.api.schemas import EvaluateRequest
        with pytest.raises(ValidationError):
            EvaluateRequest(input_text="ab")

    def test_evaluate_request_invalid_mode(self):
        from backend.api.schemas import EvaluateRequest
        with pytest.raises(ValidationError):
            EvaluateRequest(input_text="Valid input text", mode="invalid_mode")

    def test_evaluate_response(self):
        from backend.api.schemas import EvaluateResponse
        resp = EvaluateResponse(
            run_id="run-001", status="success", mode="deterministic",
            decision_classification="GO", breakthrough_classification="HIGH",
            scores={"test": 0.5}, domain="technology",
        )
        assert resp.run_id == "run-001"

    def test_health_response(self):
        from backend.api.schemas import HealthResponse
        h = HealthResponse(status="healthy", version="4.0.0", passed=8, total=8)
        assert h.status == "healthy"

    def test_acquirer_profile(self):
        from backend.api.schemas import AcquirerProfile
        a = AcquirerProfile(
            name="TestCo", ticker="TST", sector="defense",
            fit=0.9, capacity=0.8, strategy_alignment=0.85,
            tech_alignment=0.82, focus=["AI", "cyber"],
        )
        assert a.ticker == "TST"
        assert len(a.focus) == 2
