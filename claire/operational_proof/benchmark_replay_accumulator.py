from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

class BenchmarkReplayAccumulator:
    """Accumulates benchmark replay records for Claire operational proof."""

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def build_replay_record(self, run_id: str, benchmark_id: str, expected: Dict[str, Any], observed: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "record_type": "benchmark_replay",
            "run_id": run_id,
            "benchmark_id": benchmark_id,
            "expected": expected,
            "observed": observed,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "recorded",
        }

    def score_replay_match(self, record: Dict[str, Any]) -> Dict[str, Any]:
        expected = record.get("expected", {})
        observed = record.get("observed", {})
        keys = set(expected.keys()) | set(observed.keys())
        if not keys:
            score = 0.0
        else:
            matches = sum(1 for k in keys if expected.get(k) == observed.get(k))
            score = round(matches / len(keys), 4)
        return {"score": score, "level": "strong" if score >= 0.8 else "partial" if score >= 0.5 else "weak"}

    def export_record(self, record: Dict[str, Any]) -> Path:
        out = self.root / "data" / "operational_proof" / "benchmark_replays" / f"{record['benchmark_id']}_{record['run_id']}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        record["match_assessment"] = self.score_replay_match(record)
        out.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        return out
