"""
Audit Trail — records every pipeline decision for governance and compliance.
Immutable append-only log with cryptographic chaining.
"""
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("claire.governance.audit")

AUDIT_DIR = Path("data/audit")
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


class AuditTrail:
    """Append-only audit log with hash chaining for tamper detection."""

    def __init__(self, log_file: str = "audit_log.jsonl"):
        self.log_path = AUDIT_DIR / log_file
        self._last_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        if self.log_path.exists():
            lines = self.log_path.read_text(encoding="utf-8").strip().split("\n")
            if lines and lines[-1]:
                try:
                    return json.loads(lines[-1]).get("hash", "genesis")
                except json.JSONDecodeError:
                    pass
        return "genesis"

    def _compute_hash(self, entry: Dict[str, Any]) -> str:
        raw = json.dumps(entry, sort_keys=True, default=str) + self._last_hash
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def record(self, event_type: str, data: Dict[str, Any],
               actor: str = "system") -> Dict[str, Any]:
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "actor": actor,
            "data": data,
            "prev_hash": self._last_hash,
        }
        entry["hash"] = self._compute_hash(entry)
        self._last_hash = entry["hash"]

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

        logger.info(f"Audit: {event_type} by {actor} [{entry['hash']}]")
        return entry

    def record_pipeline_run(self, run_id: str, mode: str,
                            decision: str, scores: Dict[str, float]) -> Dict[str, Any]:
        return self.record("pipeline_run", {
            "run_id": run_id, "mode": mode,
            "decision": decision, "scores": scores,
        })

    def record_update(self, from_version: str, to_version: str,
                      files_changed: int) -> Dict[str, Any]:
        return self.record("platform_update", {
            "from_version": from_version, "to_version": to_version,
            "files_changed": files_changed,
        })

    def record_resolution(self, gaps_resolved: int, method: str) -> Dict[str, Any]:
        return self.record("auto_resolution", {
            "gaps_resolved": gaps_resolved, "method": method,
        })

    def get_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        lines = self.log_path.read_text(encoding="utf-8").strip().split("\n")
        entries = []
        for line in lines[-limit:]:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries

    def verify_integrity(self) -> Dict[str, Any]:
        entries = self.get_log(limit=10000)
        if not entries:
            return {"valid": True, "entries": 0}
        prev_hash = "genesis"
        for i, entry in enumerate(entries):
            if entry.get("prev_hash") != prev_hash:
                return {"valid": False, "broken_at": i, "entry": entry}
            prev_hash = entry.get("hash", "")
        return {"valid": True, "entries": len(entries), "head_hash": prev_hash}
