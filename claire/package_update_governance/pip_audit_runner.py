from __future__ import annotations
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class PipAuditRunner:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def run_audit(self) -> Dict[str, Any]:
        try:
            proc = subprocess.run([sys.executable, "-m", "pip_audit"], text=True, capture_output=True, timeout=180)
            return {
                "record_type": "pip_audit_report",
                "status": "success" if proc.returncode == 0 else "attention",
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            return {
                "record_type": "pip_audit_report",
                "status": "not_available",
                "error": str(exc),
                "hint": "Install with: python -m pip install pip-audit",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
            }

    def export_report(self, report: Dict[str, Any]) -> Path:
        out = self.root / "data" / "package_update_governance" / "audit_reports" / "pip_audit_report.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return out
