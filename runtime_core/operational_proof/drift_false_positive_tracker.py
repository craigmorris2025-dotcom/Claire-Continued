from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class DriftFalsePositiveTracker:
    """Tracks replay drift and false-positive evidence."""

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def record_drift(self, run_id: str, baseline_score: float, current_score: float, notes: str = "") -> Dict[str, Any]:
        delta = round(float(current_score) - float(baseline_score), 4)
        return {
            "record_type": "replay_drift",
            "run_id": run_id,
            "baseline_score": baseline_score,
            "current_score": current_score,
            "delta": delta,
            "severity": "high" if abs(delta) >= 0.25 else "medium" if abs(delta) >= 0.1 else "low",
            "notes": notes,
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def record_false_positive(self, run_id: str, claim: str, reason: str, severity: str = "medium") -> Dict[str, Any]:
        return {
            "record_type": "false_positive",
            "run_id": run_id,
            "claim": claim,
            "reason": reason,
            "severity": severity,
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_record(self, record: Dict[str, Any]) -> Path:
        folder = "false_positives" if record["record_type"] == "false_positive" else "drift_reports"
        out = self.root / "data" / "operational_proof" / folder / f"{record['run_id']}_{record['recorded_at_utc'].replace(':','-')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        return out
