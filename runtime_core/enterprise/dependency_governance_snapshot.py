
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DEPENDENCY_SNAPSHOT_PATH = Path("data/enterprise/dependency_governance_snapshot.json")


def _read_text_if_exists(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def _pip_freeze() -> List[str]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def build_dependency_governance_snapshot() -> Dict[str, Any]:
    snapshot = {
        "version": "16.76",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "python_executable": sys.executable,
        "python_version": sys.version,
        "requirements_txt_present": Path("requirements.txt").exists(),
        "pyproject_toml_present": Path("pyproject.toml").exists(),
        "pytest_ini_present": Path("pytest.ini").exists(),
        "requirements_txt_excerpt": _read_text_if_exists("requirements.txt")[:5000],
        "pyproject_toml_excerpt": _read_text_if_exists("pyproject.toml")[:5000],
        "installed_packages": _pip_freeze(),
        "audit_notes": [
            "This snapshot is for diligence visibility and reproducibility review.",
            "A production audit should add pip-audit or equivalent dependency vulnerability checks.",
            "Dependency pinning should be reviewed before enterprise deployment.",
        ],
    }

    DEPENDENCY_SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEPENDENCY_SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot
