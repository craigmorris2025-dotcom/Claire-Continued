"""Threshold and calibration provenance for Claire lifecycle scoring."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class ThresholdRule:
    id: str
    layer: str
    source: str
    metric: str
    rule: str
    purpose: str


@dataclass(frozen=True)
class CalibrationInput:
    id: str
    source: str
    domain_expectation: str
    raw_input_summary: str
    expected_assertions: List[str]


class ThresholdProvenance:
    """Documents the active gates and the fixtures used to protect them."""

    version = "v5.52_stage_threshold_provenance"

    def threshold_rules(self) -> List[Dict[str, Any]]:
        return [asdict(rule) for rule in self._threshold_rules()]

    def calibration_inputs(self) -> List[Dict[str, Any]]:
        return [asdict(item) for item in self._calibration_inputs()]

    def as_payload(self) -> Dict[str, Any]:
        rules = self.threshold_rules()
        fixtures = self.calibration_inputs()
        return {
            "status": "success",
            "provenance_version": self.version,
            "purpose": "Expose the inputs and gates used to protect Claire discovery, breakthrough, routing, and lifecycle behavior.",
            "threshold_rule_count": len(rules),
            "calibration_input_count": len(fixtures),
            "threshold_rules": rules,
            "calibration_inputs": fixtures,
            "notes": [
                "Pipeline v4 is the active deterministic scoring path for dashboard runs.",
                "The older interpreter thresholds are retained as legacy provenance because earlier outputs referenced them.",
                "Regression fixtures are black-box contract inputs; they protect routing, lifecycle activation, binder output, and governance posture rather than exact floating-point scores.",
            ],
        }

    def validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        result = result or {}
        scores = result.get("scores") or {}
        failures = []

        if "discovery_score" not in scores and "discovery" not in scores:
            failures.append("missing discovery score")
        if "breakthrough_score" not in scores:
            failures.append("missing breakthrough score")
        if result.get("decision_classification") is None:
            failures.append("missing decision classification")
        if result.get("breakthrough_classification") is None:
            failures.append("missing breakthrough classification")
        if "phase_log" not in result:
            failures.append("missing phase log")

        return {
            "status": "success" if not failures else "partial",
            "failures": failures,
            "observed": {
                "decision_classification": result.get("decision_classification"),
                "breakthrough_classification": result.get("breakthrough_classification"),
                "ready_for_syntalion": result.get("ready_for_syntalion"),
                "discovery_score": scores.get("discovery_score", scores.get("discovery")),
                "breakthrough_score": scores.get("breakthrough_score"),
                "portfolio_score": scores.get("portfolio_score"),
            },
        }

    def _threshold_rules(self) -> List[ThresholdRule]:
        return [
            ThresholdRule("pipeline_phase_strong", "pipeline_v4.phase_log", "src/claire/orchestrator/pipeline_v4.py::_decision", "phase score", "> 0.70 => STRONG", "Labels discovery, breakthrough, feasibility, acquisition, and portfolio phases as strong."),
            ThresholdRule("pipeline_phase_moderate", "pipeline_v4.phase_log", "src/claire/orchestrator/pipeline_v4.py::_decision", "phase score", "> 0.50 and <= 0.70 => MODERATE", "Labels phase momentum that is present but not yet strong."),
            ThresholdRule("pipeline_decision_go", "pipeline_v4.final_decision", "src/claire/orchestrator/pipeline_v4.py", "portfolio_signal", "> 0.70 => GO", "Advances high-confidence portfolio outcomes."),
            ThresholdRule("pipeline_decision_consider", "pipeline_v4.final_decision", "src/claire/orchestrator/pipeline_v4.py", "portfolio_signal", "> 0.50 and <= 0.70 => CONSIDER", "Keeps mid-confidence outcomes reviewable without dropping them."),
            ThresholdRule("pipeline_breakthrough_high", "pipeline_v4.breakthrough_classification", "src/claire/orchestrator/pipeline_v4.py", "breakthrough_signal", "> 0.65 => HIGH", "Marks candidates with enough synthesized discovery, novelty, timing, and market formation pressure as breakthrough-level."),
            ThresholdRule("pipeline_ready_for_syntalion", "pipeline_v4.readiness", "src/claire/orchestrator/pipeline_v4.py", "portfolio_signal", "> 0.65 => ready_for_syntalion", "Marks candidates ready for Syntalion packaging even if the final decision is still below full GO."),
            ThresholdRule("breakthrough_spike_discovery_patent_activity", "pipeline_v4.breakthrough_spike", "src/claire/orchestrator/pipeline_v4.py", "discovery_signal and patent_activity", "discovery_signal > 0.50 and patent_activity > 0.60 adds breakthrough spike", "Rewards discovery context combined with activity signal."),
            ThresholdRule("breakthrough_spike_patent_novelty", "pipeline_v4.breakthrough_spike", "src/claire/orchestrator/pipeline_v4.py", "patent_novelty", "> 0.55 adds breakthrough spike", "Rewards novelty when breakthrough synthesis is forming."),
            ThresholdRule("breakthrough_spike_market_pressure", "pipeline_v4.breakthrough_spike", "src/claire/orchestrator/pipeline_v4.py", "strategic pressure", ">= 0.65 adds breakthrough spike", "Rewards urgent buyer or market pressure."),
            ThresholdRule("breakthrough_spike_formation", "pipeline_v4.breakthrough_spike", "src/claire/orchestrator/pipeline_v4.py", "inevitability, momentum, category, buyer pull", "inevitability >= 0.75, momentum >= 0.72, category >= 0.78, buyer_pull >= 0.78 can add spike", "Captures formation signals that turn an idea into market timing."),
            ThresholdRule("breakthrough_spike_defensibility", "pipeline_v4.breakthrough_spike", "src/claire/orchestrator/pipeline_v4.py", "moat and value capture", "moat >= 0.70, value_capture >= 0.70, buyer_roi >= 0.70 can add spike", "Rewards defensibility and economic capture."),
            ThresholdRule("legacy_interpreter_decision", "legacy_interpreter", "src/claire/core/interpreter.py", "decision_score", ">= 0.65 => GO; >= 0.35 => CAUTION", "Preserves earlier deterministic output interpretation for older runs."),
            ThresholdRule("legacy_interpreter_breakthrough", "legacy_interpreter", "src/claire/core/interpreter.py", "breakthrough_score", ">= 0.70 => HIGH-BREAKTHROUGH; >= 0.40 => MODERATE", "Preserves older breakthrough interpretation used before pipeline v4 became the dashboard path."),
        ]

    def _calibration_inputs(self) -> List[CalibrationInput]:
        return [
            CalibrationInput(
                "defense_control_gated",
                "tests/regression/fixtures/lifecycle_inputs.py",
                "defense_autonomy",
                "Secure mission intelligence platform with authorized mission context, advisory coordination, human authorization, audit logs, and allowed-use boundaries.",
                [
                    "routes dominant sector and market gap to defense_autonomy",
                    "preserves conditional blocker level",
                    "applies control_gated readiness modifiers",
                    "keeps strict launch controls",
                    "matches plausible defense/acquisition buyers",
                ],
            ),
            CalibrationInput(
                "climate_insurance",
                "tests/regression/fixtures/lifecycle_inputs.py",
                "climate_insurance",
                "Climate insurance risk intelligence for insurers, reinsurers, underwriting teams, catastrophe scenarios, repricing pressure, and withdrawal patterns.",
                [
                    "routes dominant sector to climate_insurance",
                    "creates insurance buyer segments",
                    "preserves underwriter review controls",
                    "activates lifecycle stages and binder output",
                ],
            ),
            CalibrationInput(
                "routing_stress_insurance",
                "tests/regression/fixtures/lifecycle_inputs.py",
                "climate_insurance",
                "Mixed-signal climate insurance input with geospatial, financial, infrastructure, underwriting, reinsurance, catastrophe, and portfolio language.",
                [
                    "keeps insurance routing despite mixed geospatial and infrastructure terms",
                    "routes market gap, opportunity, and risk regulation to climate_insurance",
                    "protects buyer-segment expectations",
                ],
            ),
            CalibrationInput(
                "legacy_quantum_defense_sample",
                "tests/conftest.py",
                "defense / encryption",
                "Quantum-resistant encryption platform for defense satellite communications.",
                [
                    "historical sample carried breakthrough_score around 0.75",
                    "historical sample carried decision_score around 0.70",
                    "historical sample carried portfolio_score around 0.62",
                ],
            ),
        ]
