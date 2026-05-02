"""Legacy engine registry facade."""

from __future__ import annotations

from .base import BaseEngine


PHASE_SEQUENCE = [
    ("ingestion", ["semantic", "ingestion", "market", "company"]),
    ("analysis", ["strategy", "synergy", "risk", "engineering"]),
    ("innovation", ["innovation", "breakthrough", "product", "customer"]),
    ("forecasting", ["forecasting", "predictive", "financial", "operational"]),
    ("deal", ["deal", "portfolio", "competitive", "compliance"]),
    ("decision", ["decision", "acquirer", "fusion", "export"]),
]

DOMAIN_REGISTRY = {
    key: BaseEngine(key, phase)
    for phase, keys in PHASE_SEQUENCE
    for key in keys
}

__all__ = ["BaseEngine", "DOMAIN_REGISTRY", "PHASE_SEQUENCE"]
