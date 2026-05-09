"""
Verified Memory Store — persistent storage for validated outputs only

Version: 5.99.1
Module: src.claire.memory.store
Architecture: LOCKED at v5.90.2
Layer: 5 — Verified Memory & Recursive Learning
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


logger = logging.getLogger("claire.memory")


class Store:
    """
    Verified Memory Store.

    Purpose:
    - Persist completed run outputs by run_id
    - Maintain lightweight run history
    - Avoid breaking the runtime if memory write fails
    """

    def __init__(self, memory_root: Optional[str | Path] = None):
        self.logger = logging.getLogger(f"claire.memory.{type(self).__name__}")

        self.memory_root = Path(memory_root or "data/memory")
        self.runs_dir = self.memory_root / "runs"
        self.history_file = self.memory_root / "run_history.json"

        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.memory_root.mkdir(parents=True, exist_ok=True)

    def _utc_now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_json(self, value: Any) -> Any:
        """
        Convert unknown objects into JSON-safe values.
        """
        try:
            json.dumps(value)
            return value
        except TypeError:
            if hasattr(value, "to_dict") and callable(value.to_dict):
                return self._safe_json(value.to_dict())
            if isinstance(value, dict):
                return {str(k): self._safe_json(v) for k, v in value.items()}
            if isinstance(value, list):
                return [self._safe_json(v) for v in value]
            if isinstance(value, tuple):
                return [self._safe_json(v) for v in value]
            return str(value)

    def _validate_input(self, stage_input: dict):
        """
        Validate input matches the I/O contract.
        """
        required = ["stage_id", "source_stage", "payload", "metadata", "timestamp"]
        missing = [f for f in required if f not in stage_input]
        if missing:
            raise ValueError(f"Input contract violation — missing fields: {missing}")

    def _build_output(
        self,
        status: str = "completed",
        confidence: float = 0.0,
        evidence: list | None = None,
        failure_reasons: list | None = None,
        payload: dict | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """
        Build a contract-compliant output dict.
        """
        return {
            "stage_id": None,
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": self._utc_now_iso(),
        }

    def save_run(
        self,
        run_id: str,
        result: dict,
        intent_id: Optional[str] = None,
        raw_input: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> dict:
        """
        Persist a full pipeline run result to disk.
        """
        if not run_id:
            raise ValueError("run_id is required for memory persistence")

        safe_result = self._safe_json(result)

        record = {
            "run_id": run_id,
            "intent_id": intent_id,
            "mode": mode,
            "raw_input": raw_input,
            "status": safe_result.get("status") if isinstance(safe_result, dict) else "unknown",
            "decision_classification": safe_result.get("decision_classification") if isinstance(safe_result, dict) else None,
            "breakthrough_classification": safe_result.get("breakthrough_classification") if isinstance(safe_result, dict) else None,
            "domain": safe_result.get("domain") if isinstance(safe_result, dict) else None,
            "created_at": self._utc_now_iso(),
            "result": safe_result,
        }

        run_file = self.runs_dir / f"{run_id}.json"

        with run_file.open("w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        self._append_history(record, run_file)

        return {
            "status": "success",
            "run_id": run_id,
            "memory_path": str(run_file),
            "stored_at": record["created_at"],
        }

    def _append_history(self, record: dict, run_file: Path) -> None:
        """
        Append lightweight run metadata to run_history.json.
        """
        history = []

        if self.history_file.exists():
            try:
                with self.history_file.open("r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        history = loaded
            except Exception:
                history = []

        history_entry = {
            "run_id": record.get("run_id"),
            "intent_id": record.get("intent_id"),
            "mode": record.get("mode"),
            "status": record.get("status"),
            "decision_classification": record.get("decision_classification"),
            "breakthrough_classification": record.get("breakthrough_classification"),
            "domain": record.get("domain"),
            "created_at": record.get("created_at"),
            "memory_path": str(run_file),
        }

        history.append(history_entry)

        with self.history_file.open("w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def load_run(self, run_id: str) -> Optional[dict]:
        """
        Load a persisted run by run_id.
        """
        run_file = self.runs_dir / f"{run_id}.json"

        if not run_file.exists():
            return None

        with run_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def list_runs(self) -> list[dict]:
        """
        Return lightweight run history.
        """
        if not self.history_file.exists():
            return []

        try:
            with self.history_file.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
                return loaded if isinstance(loaded, list) else []
        except Exception:
            return []