#!/usr/bin/env python3
"""
Claire v16.28_runtime_manifest_system Installer
Runtime Manifest System
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


VERSION = "v16.28_runtime_manifest_system"
FILES = {'tools/runtime_manifest_builder.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport ast, json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\nPROTECTED = [\n    "main.py",\n    "src/claire/app.py",\n    "src/claire/api",\n    "src/claire/orchestrator",\n    "src/claire/lifecycle",\n    "src/claire/engines",\n    "src/claire/output",\n    "src/claire/dashboard",\n    "src/claire/technology/technology_intelligence.py",\n]\n\ndef classify(path: Path) -> str:\n    rel = str(path.relative_to(ROOT)).replace("\\\\", "/")\n    if rel.startswith("archive/") or rel.startswith("tests/placeholder_disabled/"):\n        return "disabled_or_archived"\n    if rel.startswith("exports/") or rel.startswith("output/") or rel.startswith("logs/"):\n        return "generated"\n    if rel.startswith(".claire_install/"):\n        return "install_record"\n    if any(rel == p or rel.startswith(p.rstrip("/") + "/") for p in PROTECTED):\n        return "protected_runtime"\n    if rel.startswith("src/claire/"):\n        return "active_runtime"\n    if rel.startswith("tests/"):\n        return "active_test"\n    if rel.startswith("docs/"):\n        return "documentation"\n    return "supporting"\n\ndef parse_imports(path: Path):\n    imports = []\n    try:\n        tree = ast.parse(path.read_text(encoding="utf-8-sig", errors="ignore"))\n    except Exception:\n        return imports\n    for node in ast.walk(tree):\n        if isinstance(node, ast.Import):\n            imports.extend(alias.name for alias in node.names)\n        elif isinstance(node, ast.ImportFrom) and node.module:\n            imports.append(node.module)\n    return sorted(set(imports))\n\ndef main() -> int:\n    records = []\n    for path in ROOT.rglob("*"):\n        if not path.is_file():\n            continue\n        rel = str(path.relative_to(ROOT)).replace("\\\\", "/")\n        if rel.startswith(".git/") or rel.startswith(".venv/"):\n            continue\n        item = {\n            "path": rel,\n            "category": classify(path),\n            "suffix": path.suffix,\n            "size_bytes": path.stat().st_size,\n        }\n        if rel.startswith("src/claire/") and path.suffix == ".py":\n            item["imports"] = parse_imports(path)\n        records.append(item)\n\n    category_counts = {}\n    for item in records:\n        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1\n\n    payload = {\n        "manifest": "runtime_manifest",\n        "version": "v16.28",\n        "created_at": datetime.now().isoformat(),\n        "root": str(ROOT),\n        "file_count": len(records),\n        "category_counts": category_counts,\n        "protected_paths": PROTECTED,\n        "files": records,\n    }\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / "runtime_manifest.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps({k: payload[k] for k in ["manifest", "version", "file_count", "category_counts"]}, indent=2))\n    print(f"\\nManifest written: {out_path}")\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'tools/active_module_registry.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport importlib, json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\nMODULES = [\n    "claire.app",\n    "claire.api.routes_pipeline",\n    "claire.orchestrator.pipeline_v4",\n    "claire.lifecycle.lifecycle_runner",\n    "claire.lifecycle.stage_registry",\n    "claire.output.core_output_builder",\n    "claire.dashboard.dashboard_state_builder",\n    "claire.technology.technology_intelligence",\n]\n\ndef main() -> int:\n    records = []\n    for module in MODULES:\n        try:\n            imported = importlib.import_module(module)\n            records.append({"module": module, "status": "active", "file": getattr(imported, "__file__", None)})\n        except Exception as exc:\n            records.append({"module": module, "status": "failed", "error": repr(exc)})\n    payload = {\n        "registry": "active_module_registry",\n        "version": "v16.28",\n        "created_at": datetime.now().isoformat(),\n        "module_count": len(records),\n        "failed_count": len([r for r in records if r["status"] != "active"]),\n        "modules": records,\n    }\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / "active_module_registry.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps(payload, indent=2))\n    print(f"\\nRegistry written: {out_path}")\n    return 0 if payload["failed_count"] == 0 else 1\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'tools/runtime_dependency_map.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport ast, json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\nSRC = ROOT / "src" / "claire"\n\ndef module_name(path: Path) -> str:\n    rel = path.relative_to(ROOT / "src").with_suffix("")\n    return ".".join(rel.parts)\n\ndef imports_for(path: Path):\n    imports = []\n    try:\n        tree = ast.parse(path.read_text(encoding="utf-8-sig", errors="ignore"))\n    except Exception:\n        return imports\n    for node in ast.walk(tree):\n        if isinstance(node, ast.Import):\n            imports.extend(alias.name for alias in node.names)\n        elif isinstance(node, ast.ImportFrom) and node.module:\n            imports.append(node.module)\n    return sorted(set(i for i in imports if i.startswith("claire")))\n\ndef main() -> int:\n    modules = []\n    for path in SRC.rglob("*.py"):\n        modules.append({\n            "module": module_name(path),\n            "path": str(path.relative_to(ROOT)).replace("\\\\", "/"),\n            "claire_imports": imports_for(path),\n        })\n    payload = {\n        "map": "runtime_dependency_map",\n        "version": "v16.28",\n        "created_at": datetime.now().isoformat(),\n        "module_count": len(modules),\n        "modules": modules,\n    }\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / "runtime_dependency_map.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps({"map": payload["map"], "module_count": payload["module_count"]}, indent=2))\n    print(f"\\nDependency map written: {out_path}")\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'tools/install_manifest_reader.py': '#!/usr/bin/env python3\nfrom __future__ import annotations\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path.cwd()\nREPORTS = ROOT / ".claire_install" / "reports"\n\ndef main() -> int:\n    manifests = []\n    if REPORTS.exists():\n        for path in sorted(REPORTS.glob("*.json")):\n            try:\n                data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))\n            except Exception:\n                continue\n            manifests.append({\n                "path": str(path.relative_to(ROOT)).replace("\\\\", "/"),\n                "installer": data.get("installer") or data.get("guard") or data.get("check") or data.get("inventory"),\n                "status": data.get("status"),\n                "created_at": data.get("created_at"),\n            })\n    payload = {\n        "reader": "install_manifest_reader",\n        "version": "v16.28",\n        "created_at": datetime.now().isoformat(),\n        "manifest_count": len(manifests),\n        "manifests": manifests[-100:],\n    }\n    out_dir = ROOT / "data" / "runtime"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / "install_manifest_index.json"\n    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")\n    print(json.dumps(payload, indent=2))\n    print(f"\\nInstall manifest index written: {out_path}")\n    return 0\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', 'docs/runtime/RUNTIME_MANIFEST_SYSTEM.md': '# Claire Runtime Manifest System\n\nv16.28 gives Claire a machine-readable view of itself.\n', 'tests/regression/test_runtime_manifest_system.py': 'import json\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\n\ndef test_runtime_manifest_builder_runs():\n    result = subprocess.run([sys.executable, "tools/runtime_manifest_builder.py"], cwd=ROOT, text=True, capture_output=True)\n    assert result.returncode == 0\n    assert (ROOT / "data" / "runtime" / "runtime_manifest.json").exists()\n\ndef test_active_module_registry_runs():\n    result = subprocess.run([sys.executable, "tools/active_module_registry.py"], cwd=ROOT, text=True, capture_output=True)\n    assert result.returncode == 0\n    data = json.loads((ROOT / "data" / "runtime" / "active_module_registry.json").read_text(encoding="utf-8"))\n    assert data["failed_count"] == 0\n\ndef test_dependency_map_runs():\n    result = subprocess.run([sys.executable, "tools/runtime_dependency_map.py"], cwd=ROOT, text=True, capture_output=True)\n    assert result.returncode == 0\n    assert (ROOT / "data" / "runtime" / "runtime_dependency_map.json").exists()\n'}


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    backup_dir(VERSION).mkdir(parents=True, exist_ok=True)

    actions = []
    for path, content in FILES.items():
        actions.append(write_file(ROOT / path, content, VERSION))

    validations = [
        run_command("runtime_manifest_builder", [sys.executable, "tools/runtime_manifest_builder.py"]),
        run_command("install_manifest_reader", [sys.executable, "tools/install_manifest_reader.py"]),
        run_command("runtime_dependency_map", [sys.executable, "tools/runtime_dependency_map.py"]),
        run_command("active_module_registry", [sys.executable, "tools/active_module_registry.py"]),
        run_command("runtime_manifest_tests", [sys.executable, "-m", "pytest", "tests/regression/test_runtime_manifest_system.py", "-q"]),
    ]

    failed = [v for v in validations if v["returncode"] != 0]
    report = {
        "installer": VERSION,
        "title": "Runtime Manifest System",
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
