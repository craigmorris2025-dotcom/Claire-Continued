"""Dashboard/runtime alignment inspection for Claire v17.50."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .button_registry import get_button_registry, validate_button_registry


PROJECT_ROOT = Path.cwd()
MANIFEST_PATH = PROJECT_ROOT / "manifests" / "v17_50_dashboard_runtime_alignment_manifest.json"
CAPABILITY_PATH = PROJECT_ROOT / "data" / "dashboard" / "dashboard_capability_manifest.json"

EXPECTED_CAPABILITIES = [
    "governed_external_search",
    "persistent_longitudinal_campaigns",
    "recurring_refresh_cycles",
    "bounded_orchestration",
    "retry_recovery_governance",
    "degraded_mode_execution",
    "source_trust_memory",
    "adaptive_evidence_weighting",
    "source_quarantine_release",
    "operational_dashboard_aggregation",
    "deployment_hardening",
    "launch_regression_lock",
    "dashboard_action_buttons",
]

KNOWN_ROUTE_CANDIDATES = [
    "/health",
    "/docs",
    "/dashboard/alignment/status",
    "/dashboard/alignment/capabilities",
    "/internet/operations/status",
    "/internet/campaigns/status",
    "/internet/source-trust/status",
    "/deployment/status",
    "/launch/regression-lock/status",
]


def _read_json(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # defensive: alignment should report, not crash dashboard
        return {"_read_error": str(exc)}


def _find_frontend_files(root: Path) -> List[str]:
    candidates: List[str] = []
    for rel in ("src/frontend", "frontend", "static", "public", "templates"):
        folder = root / rel
        if not folder.exists():
            continue
        for pattern in ("*.html", "*.js", "*.jsx", "*.tsx", "*.ts"):
            for file in folder.rglob(pattern):
                if any(part in {"node_modules", "dist", "build"} for part in file.parts):
                    continue
                candidates.append(str(file.relative_to(root)).replace("\\", "/"))
    return sorted(set(candidates))


def _find_backend_route_files(root: Path) -> List[str]:
    candidates: List[str] = []
    for rel in ("src", "backend"):
        folder = root / rel
        if not folder.exists():
            continue
        for file in folder.rglob("*.py"):
            if any(part in {".venv", "venv", "__pycache__"} for part in file.parts):
                continue
            text = file.read_text(encoding="utf-8", errors="ignore")
            if "@router." in text or "include_router" in text or "FastAPI(" in text:
                candidates.append(str(file.relative_to(root)).replace("\\", "/"))
    return sorted(set(candidates))


def build_capability_manifest(root: Optional[Path] = None) -> Dict[str, object]:
    root = root or PROJECT_ROOT
    button_validation = validate_button_registry()
    frontend_files = _find_frontend_files(root)
    backend_route_files = _find_backend_route_files(root)
    manifest = _read_json(MANIFEST_PATH)
    installed_files = manifest.get("installed_files", []) if isinstance(manifest, dict) else []
    return {
        "version": "17.50",
        "status": "aligned" if button_validation["status"] == "ok" else "needs_attention",
        "capabilities": EXPECTED_CAPABILITIES,
        "route_candidates": KNOWN_ROUTE_CANDIDATES,
        "dashboard_buttons": get_button_registry(),
        "button_validation": button_validation,
        "frontend_files_detected": frontend_files,
        "backend_route_files_detected": backend_route_files,
        "installed_files": installed_files,
        "notes": [
            "v17.50 adds a governed dashboard action panel and backend alignment routes.",
            "Buttons are bounded to declared HTTP routes and do not execute shell commands.",
            "Route availability is verified at runtime by using the dashboard buttons against the running app.",
        ],
    }


def write_capability_manifest(root: Optional[Path] = None) -> Dict[str, object]:
    root = root or PROJECT_ROOT
    data = build_capability_manifest(root)
    path = root / "data" / "dashboard" / "dashboard_capability_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return data


def get_alignment_status(root: Optional[Path] = None) -> Dict[str, object]:
    root = root or PROJECT_ROOT
    manifest = write_capability_manifest(root)
    return {
        "status": manifest["status"],
        "version": "17.50",
        "build": "Dashboard Runtime Alignment + Action Buttons",
        "button_count": len(manifest["dashboard_buttons"]),
        "capability_count": len(manifest["capabilities"]),
        "frontend_file_count": len(manifest["frontend_files_detected"]),
        "backend_route_file_count": len(manifest["backend_route_files_detected"]),
        "capability_manifest": "data/dashboard/dashboard_capability_manifest.json",
    }
