#!/usr/bin/env python3
"""
Claire v16.35_runtime_intelligence_layer Installer
Runtime Intelligence Layer
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

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


def run_command(name: str, cmd: List[str]) -> Dict[str, Any]:
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "name": name,
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-5000:],
        "stderr_tail": completed.stderr[-5000:],
    }


def write_report(version: str, payload: Dict[str, Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"{version}_{TIMESTAMP}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


VERSION = "v16.35_runtime_intelligence_layer"
FILES = {'tools/runtime_intelligence_layer.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\ndef load(path):\n    if not path.exists():\n        return None\n    try:\n        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n    except Exception as exc:\n        return {"error": repr(exc)}\n\ndef main() -> int:\n    runtime = ROOT / "data" / "runtime"\n    manifest = load(runtime / "runtime_manifest.json") or {}\n    modules = load(runtime / "active_module_registry.json") or {}\n    files = manifest.get("files", [])\n    category_counts = manifest.get("category_counts", {})\n    dormant_candidates = [\n        f["path"] for f in files\n        if f.get("category") == "active_runtime"\n        and any(x in f["path"] for x in ["proof", "demo", "maturity", "placeholder"])\n    ][:100]\n    payload = {\n        "layer": "runtime_intelligence_layer",\n        "version": "v16.35",\n        "created_at": datetime.now().isoformat(),\n        "status": "available",\n        "category_counts": category_counts,\n        "active_module_count": modules.get("module_count"),\n        "failed_module_count": modules.get("failed_count"),\n        "dormant_or_review_candidates": dormant_candidates,\n        "recommendations": [\n            "keep protected runtime spine locked",\n            "validate installers before execution",\n            "review dormant candidates before archiving",\n            "keep generated exports outside runtime decisions",\n        ],\n    }\n    out = runtime / "runtime_intelligence.json"\n    runtime.mkdir(parents=True, exist_ok=True)\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps({"layer": payload["layer"], "status": payload["status"], "candidate_count": len(dormant_candidates)}, indent=2))\n    print(f"\\nRuntime intelligence written: {out}")\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'src/claire/runtime/runtime_intelligence.py': 'from __future__ import annotations\nimport json\nfrom pathlib import Path\nfrom typing import Any, Dict\n\ndef load_runtime_intelligence(root: str | Path | None = None) -> Dict[str, Any]:\n    base = Path(root) if root else Path.cwd()\n    path = base / "data" / "runtime" / "runtime_intelligence.json"\n    if not path.exists():\n        return {"status": "not_available", "message": "Run python tools/runtime_intelligence_layer.py first."}\n    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n', 'docs/runtime/RUNTIME_INTELLIGENCE_LAYER.md': '# Claire Runtime Intelligence Layer\n\nv16.35 gives Claire a first-pass understanding of active modules, degraded systems, dormant candidates, and safe next actions.\n', 'tests/regression/test_runtime_intelligence_layer.py': 'import subprocess, sys\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_runtime_intelligence_layer_runs():\n    result = subprocess.run([sys.executable, "tools/runtime_intelligence_layer.py"], cwd=ROOT, text=True, capture_output=True)\n    assert result.returncode == 0\n    assert (ROOT / "data" / "runtime" / "runtime_intelligence.json").exists()\n\ndef test_runtime_intelligence_loader_imports():\n    from claire.runtime.runtime_intelligence import load_runtime_intelligence\n    payload = load_runtime_intelligence(ROOT)\n    assert "status" in payload\n'}


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("runtime_intelligence_layer", [sys.executable, "tools/runtime_intelligence_layer.py"]),
        run_command("runtime_intelligence_layer_tests", [sys.executable, "-m", "pytest", "tests/regression/test_runtime_intelligence_layer.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]
    report = {
        "installer": VERSION,
        "title": "Runtime Intelligence Layer",
        "created_at": datetime.now().isoformat(),
        "status": "success" if not failed else "installed_with_warnings",
        "root": str(ROOT),
        "actions": actions,
        "validations": validations,
        "failed_validation_count": len(failed),
    }
    report_path = write_report(VERSION, report)
    print(json.dumps(report, indent=2))
    print(f"\nInstall report written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
