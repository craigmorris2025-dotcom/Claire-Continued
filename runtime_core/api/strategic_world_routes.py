from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from runtime_core.strategic_world import build_strategic_world_layer


router = APIRouter(tags=["Claire Strategic World"])


ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return fallback


@router.get("/api/strategic-world/status")
def strategic_world_status() -> dict[str, Any]:
    current_run = _read_json(PROJECT_ROOT / "data" / "continuous_runtime" / "current_run.json", {})
    if isinstance(current_run, dict) and isinstance(current_run.get("strategic_world"), dict):
        return current_run["strategic_world"]
    memory = _read_json(PROJECT_ROOT / "data" / "continuous_runtime" / "lifecycle_memory.json", {})
    records = memory.get("records", []) if isinstance(memory, dict) and isinstance(memory.get("records"), list) else []
    return build_strategic_world_layer(current_run if isinstance(current_run, dict) else {}, memory_records=records)
