from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict

class RecoveryPointBuilder:
    def build_recovery_point(self, version: str, git_commit: str = "unknown") -> Dict[str, Any]:
        return {
            "record_type": "recovery_point",
            "version": version,
            "git_commit": git_commit,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "restore_rule": "Use git checkout/tag plus archived install reports to recover this checkpoint.",
        }
