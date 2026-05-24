"""
Audit Trail — immutable action logging for governance compliance.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from runtime_core.persistence.database import Database

logger = logging.getLogger("claire.governance.audit")


class AuditTrail:
    """Tracks all significant system actions for auditability."""

    SEVERITIES = ("info", "warning", "critical")

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def log_action(
        self,
        action: str,
        actor: str = "system",
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info",
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record an auditable action."""
        if severity not in self.SEVERITIES:
            severity = "info"

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "actor": actor,
            "severity": severity,
            "run_id": run_id or "",
            "details": json.dumps(details or {}),
        }

        try:
            self.db.log_audit(entry)
        except Exception as e:
            logger.error(f"Audit log DB write failed: {e}")

        logger.info(f"AUDIT [{severity.upper()}] {action} by {actor}")
        return entry

    def get_trail(
        self,
        limit: int = 50,
        severity: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve audit trail entries."""
        try:
            return self.db.get_audit_entries(limit=limit, severity=severity, run_id=run_id)
        except Exception as e:
            logger.error(f"Audit trail retrieval failed: {e}")
            return []
