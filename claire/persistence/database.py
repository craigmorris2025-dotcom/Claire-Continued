"""
SQLite Persistence — stores every pipeline run with full audit trail.
"""
import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from claire.config.settings import get_settings

logger = logging.getLogger("claire.persistence")


class Database:
    """SQLite database for pipeline run storage and audit."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = get_settings().db_path
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self.db_path = db_path
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        conn = self._connect()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT UNIQUE NOT NULL,
                    mode TEXT NOT NULL,
                    input_text TEXT,
                    decision_score REAL DEFAULT 0,
                    decision_class TEXT DEFAULT '',
                    breakthrough_score REAL DEFAULT 0,
                    portfolio_score REAL DEFAULT 0,
                    confidence REAL DEFAULT 0,
                    result_json TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    action TEXT NOT NULL,
                    actor TEXT DEFAULT 'system',
                    severity TEXT DEFAULT 'info',
                    detail TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                CREATE INDEX IF NOT EXISTS idx_runs_mode ON pipeline_runs(mode);
                CREATE INDEX IF NOT EXISTS idx_runs_created ON pipeline_runs(created_at);
                CREATE INDEX IF NOT EXISTS idx_audit_run ON audit_log(run_id);
                CREATE INDEX IF NOT EXISTS idx_audit_severity ON audit_log(severity);
            """)
            conn.commit()
        finally:
            conn.close()

    def save_run(self, run_data: Dict[str, Any]) -> str:
        run_id = run_data.get("run_id", f"run-{uuid.uuid4().hex[:6]}")
        conn = self._connect()
        try:
            conn.execute("""
                INSERT INTO pipeline_runs
                (run_id, mode, input_text, decision_score, decision_class,
                 breakthrough_score, portfolio_score, confidence, result_json,
                 started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                run_data.get("mode", "deterministic"),
                run_data.get("input_text", "")[:500],
                run_data.get("decision_score", 0),
                run_data.get("decision_class", ""),
                run_data.get("breakthrough_score", 0),
                run_data.get("portfolio_score", 0),
                run_data.get("confidence", 0),
                json.dumps(run_data.get("full_result", {}), default=str),
                run_data.get("started_at", ""),
                run_data.get("completed_at", datetime.utcnow().isoformat()),
            ))
            conn.execute(
                "INSERT INTO audit_log (run_id, action, detail) VALUES (?, ?, ?)",
                (run_id, "pipeline_complete", f"mode={run_data.get('mode')}")
            )
            conn.commit()
            logger.info(f"Saved run {run_id}")
        finally:
            conn.close()
        return run_id

    def get_runs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM pipeline_runs ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM pipeline_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if row:
                data = dict(row)
                if data.get("result_json"):
                    try:
                        data["full_result"] = json.loads(data["result_json"])
                    except json.JSONDecodeError:
                        data["full_result"] = {}
                return data
            return None
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        conn = self._connect()
        try:
            total = conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0]
            modes = {}
            for row in conn.execute("SELECT mode, COUNT(*) as cnt FROM pipeline_runs GROUP BY mode"):
                modes[row["mode"]] = row["cnt"]
            avgs = conn.execute("""
                SELECT COALESCE(AVG(decision_score), 0) as ad,
                       COALESCE(AVG(breakthrough_score), 0) as ab,
                       COALESCE(AVG(portfolio_score), 0) as ap,
                       COALESCE(AVG(confidence), 0) as ac
                FROM pipeline_runs
            """).fetchone()
            go = conn.execute("SELECT COUNT(*) FROM pipeline_runs WHERE decision_class='GO'").fetchone()[0]
            caution = conn.execute("SELECT COUNT(*) FROM pipeline_runs WHERE decision_class='CAUTION'").fetchone()[0]
            no_go = conn.execute("SELECT COUNT(*) FROM pipeline_runs WHERE decision_class='NO-GO'").fetchone()[0]
            return {
                "total_runs": total,
                "by_mode": modes,
                "avg_decision_score": round(avgs["ad"], 4),
                "avg_breakthrough": round(avgs["ab"], 4),
                "avg_portfolio": round(avgs["ap"], 4),
                "avg_confidence": round(avgs["ac"], 4),
                "go_count": go,
                "caution_count": caution,
                "no_go_count": no_go,
            }
        finally:
            conn.close()

    def log_audit(self, entry: Dict[str, Any]) -> None:
        """Write an audit trail entry."""
        conn = self._connect()
        try:
            conn.execute("""
                INSERT INTO audit_log (run_id, action, actor, severity, detail)
                VALUES (?, ?, ?, ?, ?)
            """, (
                entry.get("run_id", ""),
                entry.get("action", ""),
                entry.get("actor", "system"),
                entry.get("severity", "info"),
                entry.get("details", ""),
            ))
            conn.commit()
        finally:
            conn.close()

    def get_audit_entries(
        self,
        limit: int = 50,
        severity: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve audit trail entries with optional filters."""
        conn = self._connect()
        try:
            query = "SELECT * FROM audit_log WHERE 1=1"
            params: list = []
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            if run_id:
                query += " AND run_id = ?"
                params.append(run_id)
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
