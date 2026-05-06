#!/usr/bin/env python3
# Desktop version sync helper for Claire.
#
# This helper is intentionally lightweight and safe:
# - reads version files if present
# - reads installer registry if present
# - detects latest locked version file
# - writes dashboard/system state snapshots
# - does not mutate runtime, routing, scoring, or lifecycle output

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": str(exc), "_path": str(path)}
    return None


def read_text(path: Path) -> Optional[str]:
    try:
        if path.exists():
            return path.read_text(encoding="utf-8", errors="ignore").strip()
    except Exception:
        return None
    return None


def normalize_version_tuple(value: str) -> tuple:
    numbers = re.findall(r"\d+", value or "")
    return tuple(int(n) for n in numbers[:4]) if numbers else (0,)


def find_locked_versions(root: Path) -> List[Dict[str, str]]:
    locked = []
    for path in root.glob("version_*_locked.json"):
        version = path.stem.replace("version_", "").replace("_locked", "").replace("_", ".")
        locked.append({"version": version, "path": str(path.relative_to(root))})
    locked.sort(key=lambda item: normalize_version_tuple(item["version"]))
    return locked


def find_recent_preflights(root: Path, limit: int = 12) -> List[Dict[str, str]]:
    reports_dir = root / ".claire_install" / "reports"
    reports = []
    if reports_dir.exists():
        for path in reports_dir.glob("*_preflight_*.json"):
            reports.append({
                "name": path.name,
                "path": str(path.relative_to(root)),
                "modified_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            })
    reports.sort(key=lambda item: item["modified_utc"], reverse=True)
    return reports[:limit]


def detect_launcher_target(root: Path) -> Dict[str, Any]:
    portable = root / "tools" / "portable_launcher.py"
    main = root / "main.py"
    return {
        "preferred_target": "tools/portable_launcher.py --live --app" if portable.exists() else "main.py" if main.exists() else "missing",
        "portable_launcher_exists": portable.exists(),
        "main_py_exists": main.exists(),
    }


def build_state(root: Path, mode: str) -> Dict[str, Any]:
    claire_version = read_text(root / ".claire_version")
    version_json = read_json(root / "version.json")
    install_registry = read_json(root / ".claire_install" / "install_registry.json")
    locked_versions = find_locked_versions(root)
    recent_preflights = find_recent_preflights(root)

    latest_locked = locked_versions[-1]["version"] if locked_versions else None

    version_candidates = [
        claire_version,
        version_json.get("version") if isinstance(version_json, dict) else None,
        latest_locked,
    ]
    active_version = next((v for v in version_candidates if v), "unknown")

    launcher_target = detect_launcher_target(root)

    return {
        "status": "success" if launcher_target["preferred_target"] != "missing" else "launcher_target_missing",
        "mode": mode,
        "synced_at_utc": utc_now(),
        "root": str(root),
        "active_version": active_version,
        "claire_version_file": claire_version,
        "version_json": version_json,
        "latest_locked_version": latest_locked,
        "locked_versions": locked_versions,
        "recent_preflight_reports": recent_preflights,
        "installer_registry_present": isinstance(install_registry, dict),
        "launcher": {
            "desktop_launcher": "START_CLAIRE_DESKTOP.bat",
            "launcher_version": "11.27-11.33",
            **launcher_target,
        },
        "contracts": {
            "does_not_modify_runtime": True,
            "does_not_modify_routing": True,
            "does_not_modify_scoring": True,
            "does_not_modify_core_run_output": True,
            "purpose": "Connect desktop launcher to current version state and dashboard proof snapshots.",
        },
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Claire project root")
    parser.add_argument("--mode", default="desktop", help="Launch mode label")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    state = build_state(root, args.mode)

    write_json(root / "data" / "version_sync" / "desktop_launcher_version_state.json", state)
    write_json(root / "data" / "dashboard" / "state_snapshots" / "desktop_launcher_state.json", state)

    print("[Claire Desktop Version Sync]", state["status"])
    print("active_version:", state["active_version"])
    print("launcher_target:", state["launcher"]["preferred_target"])
    return 0 if state["status"] == "success" else 2


if __name__ == "__main__":
    raise SystemExit(main())
