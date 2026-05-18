from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request


router = APIRouter(tags=["Operational File Readiness"])


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_ROOTS = {
    "claire": "AI and intelligence platform code",
    "frontend": "operator cockpit and dashboard assets",
    "tests": "regression and operational verification",
    "tools": "safe build, audit, and verification tools",
    "data": "runtime data, memory, seed fixtures, proof inputs",
    "runtime": "current runtime state and governed live-probe state",
    "config": "platform configuration",
}

REQUIRED_FILES = {
    "main.py": "FastAPI entrypoint",
    "requirements.txt": "pinned runtime dependency set",
    "pyproject.toml": "package metadata",
    "pytest.ini": "test configuration",
    "LAUNCH_CLAIRE.bat": "operator launcher",
    ".env.example": "safe environment template",
    "LICENSE": "license declaration",
}

TARGET_STRUCTURE = {
    "backend": "desired enterprise backend service boundary; currently absent and should be created as a wrapper/extraction layer",
    "claire": "canonical intelligence and AI system",
    "frontend": "canonical operational cockpit and UI",
}

POLLUTION_ROOTS = {
    "exports": "large generated export history; should be externalized from product root",
    "archive": "historical archive tree; should be externalized",
    "backups": "backup tree; should be externalized",
    "_claire_archives": "historical archive tree; should be externalized",
    "quarantine_legacy_placeholders": "legacy placeholder quarantine; archive or delete after snapshot",
    "reports": "proof/audit reports; keep only active operational reports in product root",
    "audits": "audit outputs; externalize most proof history",
    "audit": "audit outputs; externalize most proof history",
    "output": "generated runtime/install/dashboard output; keep selected live support only",
    "runtime_reports": "runtime proof reports; externalize after snapshot",
    "__pycache__": "generated Python cache; delete after snapshot",
    ".pytest_cache": "generated pytest cache; delete after snapshot",
}


def _file_count(path: Path) -> int:
    if path.is_file():
        return 1
    if not path.exists():
        return 0
    try:
        return sum(1 for item in path.rglob("*") if item.is_file())
    except Exception:
        return -1


def _size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0
    try:
        if path.is_file():
            return round(path.stat().st_size / (1024 * 1024), 3)
        total = sum(item.stat().st_size for item in path.rglob("*") if item.is_file())
        return round(total / (1024 * 1024), 3)
    except Exception:
        return -1.0


def _root_entry(name: str, purpose: str, required: bool) -> dict[str, Any]:
    path = ROOT / name
    exists = path.exists()
    return {
        "name": name,
        "path": str(path),
        "purpose": purpose,
        "required": required,
        "exists": exists,
        "status": "present" if exists else "missing",
        "file_count": _file_count(path),
        "size_mb": _size_mb(path),
    }


def _root_file(name: str, purpose: str) -> dict[str, Any]:
    path = ROOT / name
    exists = path.exists()
    return {
        "name": name,
        "path": str(path),
        "purpose": purpose,
        "exists": exists,
        "status": "present" if exists else "missing",
        "size_mb": _size_mb(path),
    }


def _generated_summary() -> dict[str, Any]:
    patterns = {
        "pyc_files": "*.pyc",
        "bak_files": "*.bak*",
        "pytest_cache_dirs": ".pytest_cache",
        "python_cache_dirs": "__pycache__",
        "installer_scripts": "install_claire_*.py",
        "launcher_backups": "LAUNCH_CLAIRE*.bak*",
        "version_backups": "version.json.bak*",
    }
    summary: dict[str, Any] = {}
    for key, pattern in patterns.items():
        try:
            summary[key] = len(list(ROOT.rglob(pattern)))
        except Exception:
            summary[key] = -1
    return summary


def build_operational_file_readiness() -> dict[str, Any]:
    required_roots = [_root_entry(name, purpose, True) for name, purpose in REQUIRED_ROOTS.items()]
    required_files = [_root_file(name, purpose) for name, purpose in REQUIRED_FILES.items()]
    desired_roots = [_root_entry(name, purpose, name in REQUIRED_ROOTS) for name, purpose in TARGET_STRUCTURE.items()]
    pollution_roots = [
        {
            **_root_entry(name, purpose, False),
            "cleanup_class": "archive_or_delete_after_snapshot"
            if name in {"__pycache__", ".pytest_cache"}
            else "archive_external_or_keep_selected_proof",
        }
        for name, purpose in POLLUTION_ROOTS.items()
        if (ROOT / name).exists()
    ]

    missing_required = [
        item["name"] for item in [*required_roots, *required_files] if not item["exists"]
    ]
    target_missing = [item["name"] for item in desired_roots if not item["exists"]]
    pollution_file_count = sum(
        item["file_count"] for item in pollution_roots if isinstance(item.get("file_count"), int) and item["file_count"] > 0
    )
    pollution_size_mb = round(
        sum(item["size_mb"] for item in pollution_roots if isinstance(item.get("size_mb"), (int, float)) and item["size_mb"] > 0),
        3,
    )
    generated = _generated_summary()

    blockers = []
    if missing_required:
        blockers.append("missing_required_files_or_roots")
    if "backend" in target_missing:
        blockers.append("desired_backend_boundary_absent")
    if pollution_file_count:
        blockers.append("pollution_present_in_product_root")
    if generated.get("pyc_files", 0) or generated.get("bak_files", 0):
        blockers.append("generated_or_backup_artifacts_present")

    return {
        "ok": True,
        "status": "degraded" if blockers else "ready",
        "root": str(ROOT),
        "backend_owns_truth": True,
        "cleanup_approved": False,
        "destructive_cleanup_performed": False,
        "missing_required": missing_required,
        "target_missing": target_missing,
        "blockers": blockers,
        "required_roots": required_roots,
        "required_files": required_files,
        "desired_target_roots": desired_roots,
        "pollution_roots": pollution_roots,
        "pollution_summary": {
            "pollution_root_count": len(pollution_roots),
            "pollution_file_count": pollution_file_count,
            "pollution_size_mb": pollution_size_mb,
            **generated,
        },
        "next_actions": [
            "lock canonical payload and route owners",
            "build operational cockpit readiness panel",
            "snapshot before cleanup",
            "move archives/exports/backups outside product root",
            "delete generated caches after snapshot",
            "create backend wrapper boundary once runtime tests are green",
        ],
    }


@router.get("/api/system/file-readiness")
def get_system_file_readiness() -> dict[str, Any]:
    return build_operational_file_readiness()


@router.get("/dashboard/system/file-readiness")
def get_dashboard_file_readiness() -> dict[str, Any]:
    return build_operational_file_readiness()


def build_route_integrity(app: Any) -> dict[str, Any]:
    route_entries = []
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", "")
        methods = sorted(getattr(route, "methods", []) or [])
        endpoint = getattr(route, "endpoint", None)
        route_entries.append(
            {
                "path": path,
                "methods": methods,
                "name": getattr(route, "name", ""),
                "module": getattr(endpoint, "__module__", ""),
                "endpoint": getattr(endpoint, "__name__", ""),
            }
        )

    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in route_entries:
        key = f"{','.join(item['methods'])} {item['path']}"
        grouped.setdefault(key, []).append(item)

    duplicates = [
        {"route": key, "owners": owners}
        for key, owners in sorted(grouped.items())
        if len(owners) > 1
    ]
    dashboard_payload_owners = [
        item
        for item in route_entries
        if item["path"] == "/dashboard/payload" and "GET" in item["methods"]
    ]
    canonical_payload_owner = dashboard_payload_owners[0] if dashboard_payload_owners else None
    canonical_payload_locked = bool(
        canonical_payload_owner
        and canonical_payload_owner.get("module") in {"claire.app", "claire.api.dashboard_payload_bridge"}
    )
    duplicate_payload_owners = max(0, len(dashboard_payload_owners) - 1)

    return {
        "ok": True,
        "status": "degraded" if duplicates or not canonical_payload_locked else "ready",
        "route_count": len(route_entries),
        "duplicate_route_count": len(duplicates),
        "duplicates": duplicates[:50],
        "dashboard_payload": {
            "owner_count": len(dashboard_payload_owners),
            "duplicate_owner_count": duplicate_payload_owners,
            "canonical_payload_locked": canonical_payload_locked,
            "canonical_owner": canonical_payload_owner,
            "owners": dashboard_payload_owners,
        },
        "blockers": [
            *([] if canonical_payload_locked else ["canonical_dashboard_payload_owner_not_locked"]),
            *(["duplicate_route_owners_present"] if duplicates else []),
            *(["duplicate_dashboard_payload_owners_present"] if duplicate_payload_owners else []),
        ],
    }


@router.get("/api/system/route-integrity")
def get_route_integrity(request: Request) -> dict[str, Any]:
    return build_route_integrity(request.app)


@router.get("/dashboard/system/route-integrity")
def get_dashboard_route_integrity(request: Request) -> dict[str, Any]:
    return build_route_integrity(request.app)
