from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def find_latest_file(project_root: Path, file_name: str) -> Optional[Path]:
    candidates = [
        project_root / "exports" / "latest" / file_name,
        project_root / "output" / file_name,
        project_root / file_name,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    export_root = project_root / "exports"
    if export_root.exists():
        possible = [path for path in export_root.glob(f"**/{file_name}") if path.is_file()]
        if possible:
            possible.sort(key=lambda path: path.stat().st_mtime, reverse=True)
            return possible[0]

    return None


def find_runtime_truth(project_root: Path) -> Optional[Path]:
    return find_latest_file(project_root, "dashboard_runtime_truth.json") or find_latest_file(project_root, "core_run_output.json")


def find_validation_report(project_root: Path) -> Optional[Path]:
    return find_latest_file(project_root, "validation_authority_report.json")
