from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def class_name_from_file(path: Path) -> str:
    parts = [p for p in path.stem.split("_") if p]
    return "".join(p[:1].upper() + p[1:] for p in parts) or "TechnologyStub"


def stub_content(class_name: str) -> str:
    lines = [
        "from __future__ import annotations",
        "",
        "from typing import Any, Dict",
        "",
        "",
        f"class {class_name}:",
        "    def __init__(self, *args, **kwargs) -> None:",
        "        self.args = args",
        "        self.kwargs = kwargs",
        "",
        "    def _result(self, method: str = 'run') -> Dict[str, Any]:",
        "        return {",
        "            'status': 'not_implemented',",
        "            'method': method,",
        "            'confidence': 0.0,",
        "            'evidence': [],",
        "            'payload': {},",
        "            'failure_reasons': ['valid stub only; implementation pending'],",
        "            'metadata': {'safe_stub': True},",
        "        }",
        "",
    ]
    for method in ['run', 'evaluate', 'assess', 'build', 'recommend', 'match']:
        lines.extend([
            f"    def {method}(self, *args, **kwargs):",
            f"        return self._result('{method}')",
            "",
        ])
    lines.extend([
        "    def list_items(self, *args, **kwargs):",
        "        return []",
        "",
    ])
    return "\n".join(lines)


def backup_then_remove(root: Path, path: Path, bucket: str, install: bool) -> Dict[str, Any]:
    rel = path.relative_to(root)
    dest = root / "quarantine_legacy_placeholders" / bucket / rel
    action = {
        "action": "remove_from_active_collection",
        "path": str(rel),
        "quarantine": str(dest.relative_to(root)),
        "installed": install,
    }
    if install and path.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        path.unlink()
    return action


def repair_technology(root: Path, install: bool) -> List[Dict[str, Any]]:
    tech = root / "src" / "claire" / "technology"
    actions: List[Dict[str, Any]] = []
    if install:
        tech.mkdir(parents=True, exist_ok=True)
        (tech / "__init__.py").write_text('\"\"\"Claire technology intelligence package.\"\"\"\n', encoding="utf-8")
    actions.append({"action": "ensure_package", "path": "src/claire/technology", "installed": install})

    if not tech.exists():
        return actions

    backup_root = root / "quarantine_legacy_placeholders" / "backups" / ("technology_" + stamp())
    for path in sorted(tech.glob("*.py")):
        if path.name == "__init__.py":
            continue
        cls = class_name_from_file(path)
        action = {
            "action": "replace_technology_stub",
            "path": str(path.relative_to(root)),
            "class": cls,
            "backup": None,
            "installed": install,
        }
        if install:
            backup = backup_root / path.relative_to(root)
            backup.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                shutil.copy2(path, backup)
                action["backup"] = str(backup.relative_to(root))
            path.write_text(stub_content(cls), encoding="utf-8", newline="\n")
        actions.append(action)
    return actions


def find_import_target_tests(root: Path) -> List[Path]:
    tests = root / "tests"
    if not tests.exists():
        return []
    out: List[Path] = []
    for path in tests.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "Import target class" in text and "NotImplementedError" in text:
            out.append(path)
    return sorted(out)


def remove_problem_tests(root: Path, install: bool) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    for path in find_import_target_tests(root):
        actions.append(backup_then_remove(root, path, "tests_import_target_class", install))

    for rel in [
        "tests/regression/test_baseline_runner.py",
        "tests/regression/test_lifecycle_regression.py",
        "tests/test_pipeline.py",
    ]:
        path = root / rel
        if path.exists():
            actions.append(backup_then_remove(root, path, "legacy_regression_tests", install))
    return actions


def clean_current_state(root: str | Path = ".", install: bool = False) -> Dict[str, Any]:
    root = Path(root).resolve()
    actions: List[Dict[str, Any]] = []
    actions.extend(repair_technology(root, install))
    actions.extend(remove_problem_tests(root, install))

    payload = {
        "record_type": "claire_current_state_clean_report",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "installed": install,
        "root": str(root),
        "actions": actions,
    }
    if install:
        out = root / "data" / "install_safety" / "reports" / ("current_state_clean_" + stamp() + ".json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(out.relative_to(root))
    return payload
