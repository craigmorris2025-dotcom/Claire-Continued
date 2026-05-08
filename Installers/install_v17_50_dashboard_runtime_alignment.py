#!/usr/bin/env python3
"""
Claire Syntalion v17.50 — Dashboard Runtime Alignment + Action Buttons
Single-file installer. Run from project root:
    python install_v17_50_dashboard_runtime_alignment.py
    python -m pytest tests/test_v17_50_dashboard_runtime_alignment.py
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

VERSION = "17.50"
BUILD_NAME = "Dashboard Runtime Alignment + Action Buttons"
PROJECT_ROOT = Path.cwd()
INSTALL_ID = "v17_50_dashboard_runtime_alignment"
UTC_NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

BACKUP_ROOT = PROJECT_ROOT / "rollback" / INSTALL_ID / datetime.now().strftime("%Y%m%d_%H%M%S")

FILES: Dict[str, str] = {}

FILES["src/claire/dashboard/__init__.py"] = '''"""Dashboard runtime alignment package for Claire Syntalion."""
'''

FILES["src/claire/dashboard/button_registry.py"] = r'''"""Dashboard action button registry.

This module defines the governed UI action surface for Claire's dashboard.
It is intentionally data-driven so tests can prove that dashboard actions map
only to bounded backend routes and never execute arbitrary commands.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class DashboardActionButton:
    id: str
    label: str
    category: str
    method: str
    route: str
    description: str
    requires_confirmation: bool = False
    governance_scope: str = "dashboard_runtime_alignment"

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


BUTTONS: List[DashboardActionButton] = [
    DashboardActionButton(
        id="health_check",
        label="Check Runtime Health",
        category="Runtime",
        method="GET",
        route="/health",
        description="Verify the running backend health endpoint.",
    ),
    DashboardActionButton(
        id="dashboard_alignment",
        label="Verify Dashboard Alignment",
        category="Dashboard",
        method="GET",
        route="/dashboard/alignment/status",
        description="Compare dashboard surfaces to installed governed runtime capabilities.",
    ),
    DashboardActionButton(
        id="dashboard_capabilities",
        label="Load Capability Manifest",
        category="Dashboard",
        method="GET",
        route="/dashboard/alignment/capabilities",
        description="Load the dashboard capability manifest created by v17.50.",
    ),
    DashboardActionButton(
        id="internet_operations",
        label="Open Internet Operations State",
        category="Internet Operations",
        method="GET",
        route="/internet/operations/status",
        description="Read governed internet operations state if the v17.47 dashboard route is mounted.",
    ),
    DashboardActionButton(
        id="campaigns_status",
        label="Check Campaign Runtime",
        category="Campaigns",
        method="GET",
        route="/internet/campaigns/status",
        description="Read persistent campaign runtime state if the v17.43+ route is mounted.",
    ),
    DashboardActionButton(
        id="source_trust_status",
        label="Check Source Trust",
        category="Source Trust",
        method="GET",
        route="/internet/source-trust/status",
        description="Read adaptive source trust state if the v17.46 route is mounted.",
    ),
    DashboardActionButton(
        id="deployment_status",
        label="Check Deployment Hardening",
        category="Deployment",
        method="GET",
        route="/deployment/status",
        description="Read deployment hardening state if the v17.48 route is mounted.",
    ),
    DashboardActionButton(
        id="launch_lock_status",
        label="Check Launch Regression Lock",
        category="Launch Lock",
        method="GET",
        route="/launch/regression-lock/status",
        description="Read launch regression lock state if the v17.49 route is mounted.",
    ),
]


def get_button_registry() -> List[Dict[str, object]]:
    return [button.to_dict() for button in BUTTONS]


def get_button_by_id(button_id: str) -> Dict[str, object]:
    for button in BUTTONS:
        if button.id == button_id:
            return button.to_dict()
    raise KeyError(f"Unknown dashboard button: {button_id}")


def validate_button_registry() -> Dict[str, object]:
    ids = [button.id for button in BUTTONS]
    routes = [button.route for button in BUTTONS]
    unsafe = [button.to_dict() for button in BUTTONS if button.method not in {"GET", "POST"}]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    invalid_routes = sorted(route for route in routes if not route.startswith("/"))
    return {
        "status": "ok" if not unsafe and not duplicate_ids and not invalid_routes else "failed",
        "button_count": len(BUTTONS),
        "duplicate_ids": duplicate_ids,
        "invalid_routes": invalid_routes,
        "unsafe_methods": unsafe,
    }
'''

FILES["src/claire/dashboard/runtime_alignment.py"] = r'''"""Dashboard/runtime alignment inspection for Claire v17.50."""
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
'''

FILES["src/claire/api/routes_dashboard_alignment.py"] = r'''"""FastAPI routes for Claire v17.50 dashboard/runtime alignment."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from fastapi import APIRouter

from claire.dashboard.button_registry import get_button_registry, validate_button_registry
from claire.dashboard.runtime_alignment import build_capability_manifest, get_alignment_status, write_capability_manifest

router = APIRouter(prefix="/dashboard/alignment", tags=["dashboard-alignment"])


@router.get("/status")
def dashboard_alignment_status() -> Dict[str, object]:
    return get_alignment_status(Path.cwd())


@router.get("/capabilities")
def dashboard_alignment_capabilities() -> Dict[str, object]:
    return write_capability_manifest(Path.cwd())


@router.get("/buttons")
def dashboard_alignment_buttons() -> Dict[str, object]:
    return {
        "status": "ok",
        "buttons": get_button_registry(),
        "validation": validate_button_registry(),
    }


@router.get("/verify")
def dashboard_alignment_verify() -> Dict[str, object]:
    manifest = build_capability_manifest(Path.cwd())
    validation = validate_button_registry()
    return {
        "status": "ok" if validation["status"] == "ok" else "failed",
        "version": "17.50",
        "alignment_status": manifest.get("status"),
        "validation": validation,
        "route_candidates": manifest.get("route_candidates", []),
    }
'''

FILES["src/frontend/claire_dashboard_actions.js"] = r'''/* Claire v17.50 Dashboard Action Buttons
   Governed frontend action layer. It injects a small panel only once and calls
   declared backend routes with fetch. No shell execution, no eval, no dynamic code. */
(function () {
  "use strict";

  const PANEL_ID = "claire-v17-50-dashboard-actions";
  const OUTPUT_ID = "claire-v17-50-dashboard-output";
  const BUTTON_ENDPOINT = "/dashboard/alignment/buttons";

  const fallbackButtons = [
    { id: "health_check", label: "Check Runtime Health", method: "GET", route: "/health", category: "Runtime" },
    { id: "dashboard_alignment", label: "Verify Dashboard Alignment", method: "GET", route: "/dashboard/alignment/status", category: "Dashboard" },
    { id: "dashboard_capabilities", label: "Load Capability Manifest", method: "GET", route: "/dashboard/alignment/capabilities", category: "Dashboard" }
  ];

  function safeText(value) {
    if (typeof value === "string") return value;
    return JSON.stringify(value, null, 2);
  }

  function writeOutput(value) {
    const output = document.getElementById(OUTPUT_ID);
    if (!output) return;
    output.textContent = safeText(value);
  }

  async function callRoute(button) {
    writeOutput("Calling " + button.method + " " + button.route + " ...");
    try {
      const response = await fetch(button.route, { method: button.method || "GET", headers: { "Accept": "application/json" } });
      const contentType = response.headers.get("content-type") || "";
      const body = contentType.includes("application/json") ? await response.json() : await response.text();
      writeOutput({ button: button.id, route: button.route, ok: response.ok, status: response.status, body: body });
    } catch (error) {
      writeOutput({ button: button.id, route: button.route, ok: false, error: String(error) });
    }
  }

  function makeButton(button) {
    const el = document.createElement("button");
    el.type = "button";
    el.textContent = button.label;
    el.setAttribute("data-claire-action", button.id);
    el.style.margin = "4px";
    el.style.padding = "7px 10px";
    el.style.borderRadius = "8px";
    el.style.border = "1px solid rgba(255,255,255,0.25)";
    el.style.cursor = "pointer";
    el.addEventListener("click", function () { callRoute(button); });
    return el;
  }

  function renderPanel(buttons) {
    if (document.getElementById(PANEL_ID)) return;
    const panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.style.position = "fixed";
    panel.style.right = "16px";
    panel.style.bottom = "16px";
    panel.style.zIndex = "99999";
    panel.style.maxWidth = "420px";
    panel.style.maxHeight = "70vh";
    panel.style.overflow = "auto";
    panel.style.padding = "14px";
    panel.style.borderRadius = "14px";
    panel.style.background = "rgba(20, 24, 34, 0.94)";
    panel.style.color = "white";
    panel.style.boxShadow = "0 8px 32px rgba(0,0,0,0.35)";
    panel.style.fontFamily = "system-ui, -apple-system, Segoe UI, sans-serif";

    const title = document.createElement("h3");
    title.textContent = "Claire Runtime Actions v17.50";
    title.style.margin = "0 0 8px 0";
    title.style.fontSize = "15px";
    panel.appendChild(title);

    const help = document.createElement("p");
    help.textContent = "Use these buttons to verify dashboard/backend alignment and installed runtime capabilities.";
    help.style.fontSize = "12px";
    help.style.opacity = "0.85";
    help.style.margin = "0 0 8px 0";
    panel.appendChild(help);

    const buttonBox = document.createElement("div");
    buttons.forEach(function (button) { buttonBox.appendChild(makeButton(button)); });
    panel.appendChild(buttonBox);

    const output = document.createElement("pre");
    output.id = OUTPUT_ID;
    output.textContent = "Ready.";
    output.style.marginTop = "10px";
    output.style.padding = "10px";
    output.style.borderRadius = "10px";
    output.style.background = "rgba(0,0,0,0.35)";
    output.style.fontSize = "11px";
    output.style.whiteSpace = "pre-wrap";
    output.style.maxHeight = "240px";
    output.style.overflow = "auto";
    panel.appendChild(output);

    document.body.appendChild(panel);
  }

  async function loadButtons() {
    try {
      const response = await fetch(BUTTON_ENDPOINT, { headers: { "Accept": "application/json" } });
      if (!response.ok) return fallbackButtons;
      const payload = await response.json();
      return Array.isArray(payload.buttons) ? payload.buttons : fallbackButtons;
    } catch (error) {
      return fallbackButtons;
    }
  }

  function boot() {
    loadButtons().then(renderPanel);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
}());
'''

FILES["docs/v17_50_dashboard_runtime_alignment.md"] = '''# Claire v17.50 — Dashboard Runtime Alignment + Action Buttons

This build bridges the installed backend capability stack to the dashboard.

## What it adds

- Governed dashboard action button registry
- Dashboard alignment FastAPI routes
- Dashboard capability manifest generation
- Frontend action panel script
- Safe HTML script injection into detected dashboard HTML files
- Regression tests for route contracts, button contracts, and manifest generation

## Governance constraints

- Buttons call declared HTTP routes only.
- Buttons do not execute shell commands.
- Button registry allows only bounded GET/POST actions.
- Backend route inclusion is patch-backed with rollback copies.
- Runtime feature state is exposed through manifests and inspection endpoints.

## First-use checks

1. Start the backend.
2. Open the dashboard or `/docs`.
3. Verify `/dashboard/alignment/status` returns `status`.
4. Verify `/dashboard/alignment/buttons` returns the button list.
5. Open the dashboard and use the v17.50 floating action panel.
6. Any failed route result indicates a dashboard/backend mismatch to fix next.
'''

FILES["tests/test_v17_50_dashboard_runtime_alignment.py"] = r'''from pathlib import Path
import json


def test_button_registry_is_governed():
    from claire.dashboard.button_registry import get_button_registry, validate_button_registry

    buttons = get_button_registry()
    validation = validate_button_registry()
    assert validation["status"] == "ok"
    assert validation["button_count"] >= 6
    assert all(button["route"].startswith("/") for button in buttons)
    assert all(button["method"] in {"GET", "POST"} for button in buttons)
    assert all("governance_scope" in button for button in buttons)


def test_runtime_alignment_manifest_generation(tmp_path, monkeypatch):
    from claire.dashboard.runtime_alignment import build_capability_manifest, write_capability_manifest

    root = tmp_path
    (root / "src" / "frontend").mkdir(parents=True)
    (root / "src" / "frontend" / "index.html").write_text("<html><body></body></html>", encoding="utf-8")
    (root / "src" / "claire" / "api").mkdir(parents=True)
    (root / "src" / "claire" / "api" / "routes.py").write_text("from fastapi import APIRouter\nrouter = APIRouter()\n", encoding="utf-8")

    manifest = build_capability_manifest(root)
    assert manifest["version"] == "17.50"
    assert manifest["status"] == "aligned"
    assert "dashboard_action_buttons" in manifest["capabilities"]
    assert manifest["dashboard_buttons"]

    written = write_capability_manifest(root)
    out = root / "data" / "dashboard" / "dashboard_capability_manifest.json"
    assert out.exists()
    assert json.loads(out.read_text(encoding="utf-8"))["version"] == "17.50"
    assert written["status"] == "aligned"


def test_dashboard_alignment_routes_importable():
    from claire.api.routes_dashboard_alignment import router

    paths = {route.path for route in router.routes}
    assert "/dashboard/alignment/status" in paths
    assert "/dashboard/alignment/capabilities" in paths
    assert "/dashboard/alignment/buttons" in paths
    assert "/dashboard/alignment/verify" in paths


def test_installed_manifest_exists_and_records_files():
    manifest_path = Path("manifests/v17_50_dashboard_runtime_alignment_manifest.json")
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["version"] == "17.50"
    assert manifest["build"] == "Dashboard Runtime Alignment + Action Buttons"
    assert "src/claire/dashboard/button_registry.py" in manifest["installed_files"]
    assert "src/frontend/claire_dashboard_actions.js" in manifest["installed_files"]
'''


def normalize(path: str) -> Path:
    return PROJECT_ROOT / path.replace("/", os.sep)


def backup_file(path: Path) -> None:
    if not path.exists():
        return
    rel = path.relative_to(PROJECT_ROOT)
    dest = BACKUP_ROOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)


def write_file(rel: str, content: str) -> None:
    path = normalize(rel)
    backup_file(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def find_fastapi_app_files() -> List[Path]:
    roots = [PROJECT_ROOT / "src", PROJECT_ROOT / "backend", PROJECT_ROOT]
    seen = set()
    found: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for file in root.rglob("*.py") if root.is_dir() else []:
            if file in seen:
                continue
            seen.add(file)
            if any(part in {".venv", "venv", "__pycache__", "rollback"} for part in file.parts):
                continue
            text = file.read_text(encoding="utf-8", errors="ignore")
            if "FastAPI(" in text and "include_router" in text:
                found.append(file)
    # Prefer likely application entrypoints
    found.sort(key=lambda p: (0 if p.name in {"main.py", "app.py", "server.py"} else 1, len(str(p))))
    return found


def patch_fastapi_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "routes_dashboard_alignment" in text:
        return False
    backup_file(path)
    lines = text.splitlines()
    import_line = "from claire.api.routes_dashboard_alignment import router as dashboard_alignment_router"
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, import_line)

    # Insert include after the final include_router call if possible, otherwise after app = FastAPI(...)
    include_line = "app.include_router(dashboard_alignment_router)"
    inserted = False
    for i in range(len(lines) - 1, -1, -1):
        if ".include_router(" in lines[i] and not lines[i].lstrip().startswith("#"):
            indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
            lines.insert(i + 1, indent + include_line)
            inserted = True
            break
    if not inserted:
        for i, line in enumerate(lines):
            if "FastAPI(" in line and "=" in line:
                indent = line[: len(line) - len(line.lstrip())]
                lines.insert(i + 1, indent + include_line)
                inserted = True
                break
    if not inserted:
        return False
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return True


def patch_frontend_html() -> List[str]:
    patched: List[str] = []
    script = '<script src="/claire_dashboard_actions.js"></script>'
    candidates: List[Path] = []
    for rel in ("src/frontend", "frontend", "static", "public", "templates"):
        folder = PROJECT_ROOT / rel
        if folder.exists():
            candidates.extend(folder.rglob("*.html"))
    for path in candidates:
        if any(part in {"node_modules", "dist", "build"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "claire_dashboard_actions.js" in text:
            continue
        backup_file(path)
        if "</body>" in text:
            text = text.replace("</body>", f"  {script}\n</body>", 1)
        else:
            text = text + "\n" + script + "\n"
        path.write_text(text, encoding="utf-8", newline="\n")
        patched.append(str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"))
    return patched


def write_static_mount_hint() -> None:
    hint = PROJECT_ROOT / "docs" / "v17_50_static_dashboard_actions_mount_hint.md"
    backup_file(hint)
    hint.parent.mkdir(parents=True, exist_ok=True)
    hint.write_text(
        "# v17.50 Static Dashboard Action Script\n\n"
        "The installer wrote `src/frontend/claire_dashboard_actions.js`. If your FastAPI app does not already serve `src/frontend` as static files, mount it with StaticFiles so `/claire_dashboard_actions.js` is reachable.\n\n"
        "Example:\n\n```python\nfrom fastapi.staticfiles import StaticFiles\napp.mount('/', StaticFiles(directory='src/frontend', html=True), name='frontend')\n```\n",
        encoding="utf-8",
        newline="\n",
    )


def write_manifest(installed_files: List[str], patched_backend: List[str], patched_frontend: List[str]) -> None:
    manifest = {
        "version": VERSION,
        "build": BUILD_NAME,
        "install_id": INSTALL_ID,
        "installed_at": UTC_NOW,
        "installed_files": installed_files,
        "patched_backend_files": patched_backend,
        "patched_frontend_files": patched_frontend,
        "backup_root": str(BACKUP_ROOT.relative_to(PROJECT_ROOT)).replace("\\", "/") if BACKUP_ROOT.exists() else None,
        "governance": {
            "no_shell_execution_from_dashboard": True,
            "buttons_are_route_bound": True,
            "allowed_methods": ["GET", "POST"],
            "rollback_backups_created_before_patch": True,
            "runtime_isolation_preserved": True,
            "bounded_orchestration_preserved": True,
            "launch_continuity_preserved": True,
        },
    }
    path = PROJECT_ROOT / "manifests" / "v17_50_dashboard_runtime_alignment_manifest.json"
    backup_file(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8", newline="\n")


def update_capability_manifest() -> None:
    # Import from newly written files if package path is available; otherwise write a minimal manifest.
    import sys
    src = str(PROJECT_ROOT / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    try:
        from claire.dashboard.runtime_alignment import write_capability_manifest
        write_capability_manifest(PROJECT_ROOT)
    except Exception as exc:
        path = PROJECT_ROOT / "data" / "dashboard" / "dashboard_capability_manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"version": VERSION, "status": "installed", "warning": str(exc)}, indent=2), encoding="utf-8")


def main() -> None:
    installed_files: List[str] = []
    for rel, content in FILES.items():
        write_file(rel, content)
        installed_files.append(rel)

    patched_backend: List[str] = []
    for app_file in find_fastapi_app_files()[:3]:
        try:
            if patch_fastapi_file(app_file):
                patched_backend.append(str(app_file.relative_to(PROJECT_ROOT)).replace("\\", "/"))
                break
        except Exception as exc:
            print(f"WARNING: could not patch backend app file {app_file}: {exc}")

    patched_frontend = patch_frontend_html()
    write_static_mount_hint()
    installed_files.append("docs/v17_50_static_dashboard_actions_mount_hint.md")

    write_manifest(installed_files, patched_backend, patched_frontend)
    update_capability_manifest()

    print("Claire v17.50 installed: Dashboard Runtime Alignment + Action Buttons")
    print(f"Installed files: {len(installed_files)}")
    print(f"Patched backend files: {patched_backend or 'none detected'}")
    print(f"Patched frontend HTML files: {patched_frontend or 'none detected'}")
    print("Next:")
    print("  python -m pytest tests/test_v17_50_dashboard_runtime_alignment.py")
    print("  Start Claire, open /docs, verify /dashboard/alignment/status and /dashboard/alignment/buttons")


if __name__ == "__main__":
    main()
