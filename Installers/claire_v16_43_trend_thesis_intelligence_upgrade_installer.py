#!/usr/bin/env python3
"""
Claire v16.43_trend_thesis_intelligence_upgrade
Trend Thesis Intelligence Upgrade
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


VERSION = "v16.43_trend_thesis_intelligence_upgrade"
FILES = {'tools/trend_thesis_intelligence_upgrade.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\nSIGNALS = ["trend", "thesis", "signal", "cluster", "market", "evidence", "confidence"]\n\ndef main() -> int:\n    search_dirs = [\n        ROOT / "src" / "claire" / "engines",\n        ROOT / "src" / "claire" / "trends",\n        ROOT / "src" / "claire" / "thesis",\n        ROOT / "src" / "claire" / "feeds",\n    ]\n\n    evidence = []\n    corpus = ""\n    for d in search_dirs:\n        if not d.exists():\n            continue\n        for path in d.rglob("*.py"):\n            text = path.read_text(encoding="utf-8", errors="ignore").lower()\n            corpus += text + "\\n"\n            hits = [s for s in SIGNALS if s in text]\n            if hits:\n                evidence.append({\n                    "path": str(path.relative_to(ROOT)).replace("\\\\", "/"),\n                    "signals": hits,\n                })\n\n    signal_coverage = {s: corpus.count(s) for s in SIGNALS}\n    readiness = "strong" if signal_coverage.get("trend", 0) and signal_coverage.get("thesis", 0) else "partial"\n\n    payload = {\n        "upgrade": "trend_thesis_intelligence",\n        "version": "v16.43",\n        "created_at": datetime.now().isoformat(),\n        "status": "available",\n        "readiness": readiness,\n        "signal_coverage": signal_coverage,\n        "evidence_file_count": len(evidence),\n        "evidence": evidence[:200],\n        "recommendations": [\n            "connect trend/thesis scoring to core_run_output",\n            "track confidence and evidence per thesis",\n            "separate trend discovery from breakthrough escalation",\n            "preserve portfolio-first default route",\n        ],\n    }\n\n    out_dir = ROOT / "data" / "intelligence"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out = out_dir / "trend_thesis_intelligence.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps({"upgrade": payload["upgrade"], "readiness": payload["readiness"], "evidence_file_count": payload["evidence_file_count"]}, indent=2))\n    print(f"\\nTrend thesis intelligence written: {out}")\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'src/claire/intelligence/trend_thesis_intelligence.py': 'from __future__ import annotations\nimport json\nfrom pathlib import Path\nfrom typing import Any, Dict\n\ndef load_trend_thesis_intelligence(root: str | Path | None = None) -> Dict[str, Any]:\n    base = Path(root) if root else Path.cwd()\n    path = base / "data" / "intelligence" / "trend_thesis_intelligence.json"\n    if not path.exists():\n        return {"status": "not_available", "message": "Run python tools/trend_thesis_intelligence_upgrade.py first."}\n    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n', 'docs/intelligence/TREND_THESIS_INTELLIGENCE.md': '# Claire Trend/Thesis Intelligence Upgrade\n\nv16.43 adds first-pass introspection and readiness scoring for trend and thesis intelligence.\n', 'tests/regression/test_trend_thesis_intelligence.py': 'import subprocess, sys\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_trend_thesis_intelligence_runs():\n    result = subprocess.run([sys.executable, "tools/trend_thesis_intelligence_upgrade.py"], cwd=ROOT)\n    assert result.returncode == 0\n    assert (ROOT / "data" / "intelligence" / "trend_thesis_intelligence.json").exists()\n\ndef test_trend_thesis_loader_imports():\n    from claire.intelligence.trend_thesis_intelligence import load_trend_thesis_intelligence\n    payload = load_trend_thesis_intelligence(ROOT)\n    assert "readiness" in payload or payload.get("status") == "not_available"\n'}

def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("trend_thesis_intelligence_upgrade", [sys.executable, "tools/trend_thesis_intelligence_upgrade.py"]),
        run_command("trend_thesis_intelligence_tests", [sys.executable, "-m", "pytest", "tests/regression/test_trend_thesis_intelligence.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]

    payload = {
        "installer": VERSION,
        "title": "Trend Thesis Intelligence Upgrade",
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
