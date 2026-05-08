"""
Regression fixtures for Claire's deterministic lifecycle tests.

These inputs are intentionally compact enough for fast local pytest runs,
but rich enough to exercise routing, control-gating, productization, binder,
and lifecycle-stage activation.
"""

DEFENSE_CONTROL_GATED_INPUT = {
    "raw_input": (
        "A secure mission intelligence platform that ingests authorized mission context, "
        "sensor summaries, operator constraints, and simulation results to recommend "
        "advisory coordination options for human review. The system does not automate "
        "operational decisions. It runs mission simulations, scores coordination risk, "
        "routes recommendations through a secure command review console, requires human "
        "authorization, records override decisions, and preserves a mission-use audit log. "
        "The buyer pain is that defense teams need reviewable autonomy support in contested "
        "environments, but deployment must remain control-gated with allowed-use boundaries, "
        "operator trust, and auditability."
    ),
    "metadata": {
        "source": "regression_suite",
        "priority": "high",
        "tags": ["defense", "control_gated", "mission_intelligence"],
    },
}

CLIMATE_INSURANCE_INPUT = {
    "raw_input": (
        "A climate insurance risk intelligence platform for insurers, reinsurers, and "
        "underwriting teams that combines historical weather losses, property exposure data, "
        "catastrophe scenarios, regional climate concentration, premium adequacy signals, "
        "and market withdrawal patterns. The system detects repricing pressure before legacy "
        "underwriting workflows react, generates exposure benchmarks, recommends risk-transfer "
        "countermeasures, and routes all pricing-impact outputs through underwriter review "
        "controls with scenario versioning and audit logs."
    ),
    "metadata": {
        "source": "regression_suite",
        "priority": "high",
        "tags": ["climate_insurance", "underwriting", "repricing"],
    },
}

ROUTING_STRESS_INSURANCE_INPUT = {
    "raw_input": (
        "An AI-powered climate insurance platform that helps property insurers and reinsurers "
        "evaluate weather losses, wildfire exposure, flood concentration, underwriting repricing "
        "pressure, catastrophe scenarios, and market withdrawal risk. Although the system uses "
        "geospatial data, financial loss estimates, and infrastructure exposure, the primary buyer "
        "is insurance underwriting and reinsurance portfolio teams. The product recommends "
        "risk-transfer planning, premium adequacy review, and exposure concentration countermeasures "
        "with underwriter approval gates and model audit trails."
    ),
    "metadata": {
        "source": "regression_suite",
        "priority": "medium",
        "tags": ["routing_stress", "insurance", "mixed_signal"],
    },
}

ALL_FIXTURES = {
    "defense_control_gated": DEFENSE_CONTROL_GATED_INPUT,
    "climate_insurance": CLIMATE_INSURANCE_INPUT,
    "routing_stress_insurance": ROUTING_STRESS_INSURANCE_INPUT,
}
