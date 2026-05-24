from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()


INGESTION_ALLOWLIST = [
    "data/continuous_runtime/lifecycle_memory.json",
    "data/source_universes/universe_index.json",
    "data/live/source_registry.json",
    "data/live_intelligence/latest_monitor_run.json",
    "data/internet_evidence/promoted_metadata_evidence_store.json",
]

FORBIDDEN_PREFIXES = [
    "data/dashboard",
    "data/design",
    "data/buyer",
    "data/build_",
    "data/demo",
    "data/cockpit",
    "data/desktop",
    "data/installer",
    "data/cleanup",
    "data/completion",
    "data/deployment",
    "data/backups",
    "data/baselines",
    "data/benchmark",
    "data/config",
    "data/audit",
    "data/reports",
    "data/runtime_reports",
    "data/runs",
    "data/memory",
    "data/continuous_runtime/discovery_candidates.json",
    "data/continuous_runtime/breakthrough_candidates.json",
    "data/continuous_runtime/portfolio_candidates.json",
    "data/continuous_runtime/design_candidates.json",
    "data/continuous_runtime/review_queue.json",
    "claire/",
    "backend/",
    "frontend/",
    "tools/",
    "docs/",
    ".git/",
    ".venv/",
]

PATH_KEYS = {
    "path",
    "file",
    "filepath",
    "file_path",
    "source",
    "source_path",
    "artifact",
    "store_root",
    "memory_path",
}


def project_relative(path: str | Path, root: Path = PROJECT_ROOT) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return candidate.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return str(path).replace("\\", "/").lstrip("./")


def is_forbidden(path: str | Path, root: Path = PROJECT_ROOT) -> bool:
    rel = project_relative(path, root)
    return any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def is_allowed_input_path(path: str | Path, root: Path = PROJECT_ROOT) -> bool:
    rel = project_relative(path, root)
    return rel in INGESTION_ALLOWLIST and not is_forbidden(rel, root)


def allowed_input_files(root: Path = PROJECT_ROOT) -> List[Path]:
    files: List[Path] = []
    for rel in INGESTION_ALLOWLIST:
        path = root / rel
        if path.exists() and is_allowed_input_path(path, root):
            files.append(path)
    return files


def _iter_path_values(value: Any, parent_key: str = "") -> Iterable[str]:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in PATH_KEYS and isinstance(item, str):
                yield item
            yield from _iter_path_values(item, key_text)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_path_values(item, parent_key)


def source_violations(payload: Any, root: Path = PROJECT_ROOT) -> List[str]:
    violations: List[str] = []
    for path in _iter_path_values(payload):
        normalized = path.replace("\\", "/")
        if normalized.startswith(("http://", "https://")):
            continue
        if is_forbidden(normalized, root):
            violations.append(project_relative(normalized, root))
    return sorted(set(violations))


def filter_sources(sources: Dict[str, Any] | None, root: Path = PROJECT_ROOT) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    clean: Dict[str, Any] = {}
    rejected: Dict[str, Any] = {}
    for name, payload in (sources or {}).items():
        violations = source_violations(payload, root)
        if violations:
            rejected[name] = {
                "reason": "source_boundary_forbidden_path",
                "violations": violations,
            }
        else:
            clean[name] = payload
    return clean, {
        "status": "enforced",
        "allowlist": list(INGESTION_ALLOWLIST),
        "forbidden_prefix_count": len(FORBIDDEN_PREFIXES),
        "rejected_sources": rejected,
    }
