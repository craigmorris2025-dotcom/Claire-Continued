from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

class HealthCheckRunner:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)

    def run_checks(self) -> Dict[str, Any]:
        checks = {
            "launcher_exists": (self.root / "LAUNCH_PLATFORM.bat").exists(),
            "src_exists": (self.root / "src").exists(),
            "version_lock_exists": (self.root / "version_11_42_locked.json").exists() or (self.root / "version_11_50_operational_proof_plateau.json").exists(),
            "modern_dashboard_exists": (self.root / "src" / "frontend" / "command_center" / "modern" / "index.html").exists(),
        }
        return {"status": "pass" if all(checks.values()) else "attention", "checks": checks}
