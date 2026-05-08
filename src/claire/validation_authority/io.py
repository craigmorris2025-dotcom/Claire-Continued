from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return value


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def find_latest_runtime_truth(project_root: Path) -> Optional[Path]:
    candidates = [
        project_root / "exports" / "latest" / "dashboard_runtime_truth.json",
        project_root / "exports" / "latest" / "core_run_output.json",
        project_root / "output" / "core_run_output.json",
        project_root / "core_run_output.json",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    export_root = project_root / "exports"
    if export_root.exists():
        possible = []
        for name in ("dashboard_runtime_truth.json", "core_run_output.json"):
            possible.extend(export_root.glob(f"**/{name}"))
        possible = [path for path in possible if path.is_file()]
        if possible:
            possible.sort(key=lambda path: path.stat().st_mtime, reverse=True)
            return possible[0]

    return None
