from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class PilotReadinessGate:
    """Evaluates whether Claire is ready for controlled pilot operations."""

    REQUIRED = {
        "data_readiness_score": 0.55,
        "telemetry_density_score": 0.45,
        "benchmark_replay_score": 0.50,
        "governance_score": 0.70,
    }

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def evaluate(self, scores: Dict[str, float]) -> Dict[str, Any]:
        failures = []
        for key, threshold in self.REQUIRED.items():
            if float(scores.get(key, 0)) < threshold:
                failures.append({"metric": key, "required": threshold, "actual": scores.get(key, 0)})
        return {
            "record_type": "pilot_readiness_gate",
            "status": "pass" if not failures else "blocked",
            "failures": failures,
            "scores": scores,
            "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
            "rule": "Pilot activation requires data, telemetry, benchmark, and governance proof.",
        }

    def export_decision(self, decision: Dict[str, Any]) -> Path:
        out = self.root / "data" / "operational_proof" / "pilot_gates" / f"pilot_gate_{decision['evaluated_at_utc'].replace(':','-')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(decision, indent=2, sort_keys=True), encoding="utf-8")
        return out
