#!/usr/bin/env python3
"""
Claire v16.42_lifecycle_quality_scorer
Lifecycle Quality Scorer
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

ROOT = Path.cwd()
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_DIR = ROOT / ".claire_install" / "reports"

def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")

def backup_dir(version: str) -> Path:
    return ROOT / ".claire_install" / "backups" / f"{version}_{TIMESTAMP}"

def backup(path: Path, version: str) -> str | None:
    if not path.exists():
        return None
    target = backup_dir(version) / rel(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return rel(target)

def write_file(path: Path, content: str, version: str) -> Dict[str, Any]:
    action = {
        "action": "write_file",
        "path": rel(path),
        "existed_before": path.exists(),
        "backup_path": backup(path, version),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return action

def run_command(name: str, cmd: list[str]) -> Dict[str, Any]:
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "name": name,
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-3000:],
        "stderr_tail": completed.stderr[-3000:],
    }

def write_report(version: str, payload: Dict[str, Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{version}_{TIMESTAMP}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


VERSION = "v16.42_lifecycle_quality_scorer"
FILES = {'tools/lifecycle_quality_scorer.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\nEXPECTED_STAGE_HINTS = [\n    "signal",\n    "normalization",\n    "validation",\n    "trend",\n    "thesis",\n    "portfolio",\n    "breakthrough",\n    "design",\n    "acquisition",\n    "package",\n]\n\ndef main() -> int:\n    lifecycle_dir = ROOT / "src" / "claire" / "lifecycle"\n    files = sorted(str(p.relative_to(ROOT)).replace("\\\\", "/") for p in lifecycle_dir.glob("*.py")) if lifecycle_dir.exists() else []\n\n    text_blob = ""\n    for path in lifecycle_dir.glob("*.py") if lifecycle_dir.exists() else []:\n        text_blob += path.read_text(encoding="utf-8", errors="ignore").lower() + "\\n"\n\n    covered = [hint for hint in EXPECTED_STAGE_HINTS if hint in text_blob]\n    missing = [hint for hint in EXPECTED_STAGE_HINTS if hint not in covered]\n\n    score = round((len(covered) / len(EXPECTED_STAGE_HINTS)) * 100, 2)\n\n    payload = {\n        "scorer": "lifecycle_quality_scorer",\n        "version": "v16.42",\n        "created_at": datetime.now().isoformat(),\n        "status": "available",\n        "score": score,\n        "covered_stage_hints": covered,\n        "missing_stage_hints": missing,\n        "lifecycle_file_count": len(files),\n        "lifecycle_files": files,\n        "recommendations": [\n            "increase explicit lifecycle stage coverage",\n            "ensure terminal states remain route-aware",\n            "keep skipped_by_route reasons visible",\n            "connect quality scoring to runtime outputs before UI expansion",\n        ],\n    }\n\n    out_dir = ROOT / "data" / "intelligence"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out = out_dir / "lifecycle_quality_score.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps({"scorer": payload["scorer"], "score": payload["score"], "missing": payload["missing_stage_hints"]}, indent=2))\n    print(f"\\nLifecycle quality score written: {out}")\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'src/claire/intelligence/lifecycle_quality.py': 'from __future__ import annotations\nimport json\nfrom pathlib import Path\nfrom typing import Any, Dict\n\ndef load_lifecycle_quality_score(root: str | Path | None = None) -> Dict[str, Any]:\n    base = Path(root) if root else Path.cwd()\n    path = base / "data" / "intelligence" / "lifecycle_quality_score.json"\n    if not path.exists():\n        return {"status": "not_available", "message": "Run python tools/lifecycle_quality_scorer.py first."}\n    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n', 'docs/intelligence/LIFECYCLE_QUALITY_SCORER.md': '# Claire Lifecycle Quality Scorer\n\nv16.42 adds a first-pass intelligence quality score for lifecycle coverage and stage visibility.\n', 'tests/regression/test_lifecycle_quality_scorer.py': 'import subprocess, sys\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_lifecycle_quality_scorer_runs():\n    result = subprocess.run([sys.executable, "tools/lifecycle_quality_scorer.py"], cwd=ROOT)\n    assert result.returncode == 0\n    assert (ROOT / "data" / "intelligence" / "lifecycle_quality_score.json").exists()\n\ndef test_lifecycle_quality_loader_imports():\n    from claire.intelligence.lifecycle_quality import load_lifecycle_quality_score\n    payload = load_lifecycle_quality_score(ROOT)\n    assert "score" in payload or payload.get("status") == "not_available"\n'}

def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("lifecycle_quality_scorer", [sys.executable, "tools/lifecycle_quality_scorer.py"]),
        run_command("lifecycle_quality_scorer_tests", [sys.executable, "-m", "pytest", "tests/regression/test_lifecycle_quality_scorer.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]

    payload = {
        "installer": VERSION,
        "title": "Lifecycle Quality Scorer",
        "created_at": datetime.now().isoformat(),
        "status": "success" if not failed else "installed_with_warnings",
        "actions": actions,
        "validations": validations,
        "failed_validation_count": len(failed),
    }

    report = write_report(VERSION, payload)
    print(json.dumps(payload, indent=2))
    print(f"\nInstall report written: {report}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
