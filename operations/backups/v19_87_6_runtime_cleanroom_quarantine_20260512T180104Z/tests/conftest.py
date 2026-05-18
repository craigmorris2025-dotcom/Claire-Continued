"""
Shared test fixtures for Claire Syntalion test suite.
"""
import os
import sys
import pytest

# Ensure project root on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("CLAIRE_ENV", "test")
os.environ.setdefault("CLAIRE_DB_PATH", "data/test_claire.db")
os.environ.setdefault("CLAIRE_DATA_DIR", "data")


@pytest.fixture
def sample_input():
    return "Quantum-resistant encryption platform for defense satellite communications"


@pytest.fixture
def sample_intent():
    from backend.claire.contract import ClaireIntent
    return ClaireIntent(
        raw_input="Quantum-resistant encryption platform for defense satellite communications",
        mode="deterministic",
        request_type="evaluate",
    )


@pytest.fixture
def sample_scores():
    return {
        "semantic_score": 0.72,
        "ingestion_score": 0.68,
        "market_score": 0.55,
        "strategy_score": 0.78,
        "synergy_score": 0.61,
        "risk_score": 0.40,
        "innovation_score": 0.80,
        "breakthrough_score": 0.75,
        "forecast_score": 0.50,
        "predictive_score": 0.48,
        "deal_score": 0.65,
        "decision_score": 0.70,
        "portfolio_score": 0.62,
        "_confidence": 0.66,
    }


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_claire.db")

# CLAIRE_V19_87_4_1_QUARANTINE_COLLECTION_GUARD
def pytest_ignore_collect(collection_path, config):
    path_text = str(collection_path).replace("\\", "/")
    if "tests/_quarantine_legacy_backend_imports/" in path_text:
        return True
    if path_text.endswith("tests/_quarantine_legacy_backend_imports"):
        return True
    return False

