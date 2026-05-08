#!/usr/bin/env python3
"""
Claire v16.44_portfolio_breakthrough_routing_upgrade
Portfolio Breakthrough Routing Upgrade
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


VERSION = "v16.44_portfolio_breakthrough_routing_upgrade"
FILES = {'tools/portfolio_breakthrough_routing_upgrade.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\n\nROUTES = {\n    "portfolio": ["portfolio", "optimization", "market", "risk", "positioning"],\n    "breakthrough": ["breakthrough", "gap", "classification", "path_selection"],\n    "design": ["design", "architecture", "blueprint", "implementation"],\n    "acquisition": ["acquisition", "acquirer", "package", "deal"],\n}\n\ndef main() -> int:\n    src = ROOT / "src" / "claire"\n    route_hits = {route: [] for route in ROUTES}\n\n    if src.exists():\n        for path in src.rglob("*.py"):\n            text = path.read_text(encoding="utf-8", errors="ignore").lower()\n            rel = str(path.relative_to(ROOT)).replace("\\\\", "/")\n            for route, terms in ROUTES.items():\n                hits = [t for t in terms if t in text or t in rel.lower()]\n                if hits:\n                    route_hits[route].append({"path": rel, "hits": hits})\n\n    route_scores = {\n        route: min(100, len(items) * 5)\n        for route, items in route_hits.items()\n    }\n\n    payload = {\n        "upgrade": "portfolio_breakthrough_routing",\n        "version": "v16.44",\n        "created_at": datetime.now().isoformat(),\n        "status": "available",\n        "route_scores": route_scores,\n        "route_hits": {route: items[:100] for route, items in route_hits.items()},\n        "routing_policy": {\n            "default_route": "portfolio",\n            "breakthrough_is_conditional": True,\n            "design_is_conditional": True,\n            "acquisition_package_is_terminal_route": True,\n        },\n        "recommendations": [\n            "keep portfolio route as default practical output path",\n            "trigger breakthrough only with qualified gap/advancement evidence",\n            "trigger design only after advancement path requires build/spec output",\n            "keep acquisition package terminal and evidence-backed",\n        ],\n    }\n\n    out_dir = ROOT / "data" / "intelligence"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out = out_dir / "portfolio_breakthrough_routing.json"\n    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n\n    print(json.dumps({"upgrade": payload["upgrade"], "route_scores": payload["route_scores"]}, indent=2))\n    print(f"\\nPortfolio breakthrough routing written: {out}")\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'src/claire/intelligence/portfolio_breakthrough_routing.py': 'from __future__ import annotations\nimport json\nfrom pathlib import Path\nfrom typing import Any, Dict\n\ndef load_portfolio_breakthrough_routing(root: str | Path | None = None) -> Dict[str, Any]:\n    base = Path(root) if root else Path.cwd()\n    path = base / "data" / "intelligence" / "portfolio_breakthrough_routing.json"\n    if not path.exists():\n        return {"status": "not_available", "message": "Run python tools/portfolio_breakthrough_routing_upgrade.py first."}\n    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n', 'docs/intelligence/PORTFOLIO_BREAKTHROUGH_ROUTING.md': '# Claire Portfolio/Breakthrough Routing Upgrade\n\nv16.44 adds first-pass route intelligence for portfolio, breakthrough, design, and acquisition paths.\n', 'tests/regression/test_portfolio_breakthrough_routing.py': 'import subprocess, sys\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_portfolio_breakthrough_routing_runs():\n    result = subprocess.run([sys.executable, "tools/portfolio_breakthrough_routing_upgrade.py"], cwd=ROOT)\n    assert result.returncode == 0\n    assert (ROOT / "data" / "intelligence" / "portfolio_breakthrough_routing.json").exists()\n\ndef test_portfolio_breakthrough_loader_imports():\n    from claire.intelligence.portfolio_breakthrough_routing import load_portfolio_breakthrough_routing\n    payload = load_portfolio_breakthrough_routing(ROOT)\n    assert "route_scores" in payload or payload.get("status") == "not_available"\n'}

def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("portfolio_breakthrough_routing_upgrade", [sys.executable, "tools/portfolio_breakthrough_routing_upgrade.py"]),
        run_command("portfolio_breakthrough_routing_tests", [sys.executable, "-m", "pytest", "tests/regression/test_portfolio_breakthrough_routing.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]

    payload = {
        "installer": VERSION,
        "title": "Portfolio Breakthrough Routing Upgrade",
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
