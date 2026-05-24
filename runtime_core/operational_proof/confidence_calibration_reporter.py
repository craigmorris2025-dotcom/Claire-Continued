from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

class ConfidenceCalibrationReporter:
    """Builds confidence calibration reports from expected vs observed outcomes."""

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_report(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not records:
            avg_error = 1.0
        else:
            errors = []
            for r in records:
                confidence = float(r.get("confidence", 0))
                outcome = 1.0 if r.get("outcome") in ("success", "correct", True) else 0.0
                errors.append(abs(confidence - outcome))
            avg_error = round(sum(errors) / len(errors), 4)
        return {
            "record_type": "confidence_calibration_report",
            "record_count": len(records),
            "average_error": avg_error,
            "calibration_level": "strong" if avg_error <= 0.15 else "partial" if avg_error <= 0.35 else "weak",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    def export_report(self, report: Dict[str, Any]) -> Path:
        out = self.root / "data" / "operational_proof" / "confidence_calibration" / f"confidence_calibration_{report['created_at_utc'].replace(':','-')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return out
