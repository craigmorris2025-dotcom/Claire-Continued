"""Persistent live intelligence monitor history."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import uuid


class LiveIntelligenceHistoryStore:
    """Append monitor runs and keep a latest snapshot."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.data_dir = project_root / "data" / "live_intelligence"
        self.history_path = self.data_dir / "monitor_history.jsonl"
        self.latest_path = self.data_dir / "latest_monitor_run.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def record(self, result: Dict[str, Any], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        monitor_run_id = "live_run_" + uuid.uuid4().hex[:12]
        record = {
            "monitor_run_id": monitor_run_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "context": context or {},
            "summary": self._summary(result),
            "result": result,
        }
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        self.latest_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return {
            "status": "success",
            "monitor_run_id": monitor_run_id,
            "history_path": str(self.history_path),
            "latest_path": str(self.latest_path),
            "summary": record["summary"],
        }

    def latest(self) -> Dict[str, Any]:
        if not self.latest_path.exists():
            return {"status": "not_found", "message": "No live monitor run has been recorded yet."}
        payload = json.loads(self.latest_path.read_text(encoding="utf-8-sig"))
        payload["status"] = "success"
        return payload

    def list(self, limit: int = 20) -> Dict[str, Any]:
        if not self.history_path.exists():
            return {"status": "success", "run_count": 0, "runs": []}
        rows: List[Dict[str, Any]] = []
        for line in self.history_path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        rows = rows[-max(0, int(limit)):]
        rows.reverse()
        return {
            "status": "success",
            "run_count": len(rows),
            "runs": [
                {
                    "monitor_run_id": row.get("monitor_run_id"),
                    "recorded_at": row.get("recorded_at"),
                    "summary": row.get("summary", {}),
                    "context": row.get("context", {}),
                }
                for row in rows
            ],
        }

    def _summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": result.get("status"),
            "connector_records": (result.get("connectors") or {}).get("record_count", 0),
            "signals": (result.get("extracted") or {}).get("signal_count", 0),
            "clusters": (result.get("clusters") or {}).get("cluster_count", 0),
            "gaps": (result.get("gaps") or {}).get("gap_count", 0),
            "solutions": (result.get("solutions") or {}).get("candidate_count", 0),
            "live_opportunities_ready": result.get("live_opportunities_ready", False),
            "top_candidate_title": ((result.get("solutions") or {}).get("candidates") or [{}])[0].get("title"),
        }
