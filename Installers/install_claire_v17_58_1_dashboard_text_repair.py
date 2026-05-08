#!/usr/bin/env python3
# Claire Syntalion v17.58.1 — Dashboard Text Layout Repair Hotfix
# Place this file in the Claire project root and run:
#   python install_claire_v17_58_1_dashboard_text_repair.py

from __future__ import annotations

import datetime
import json
import shutil
from pathlib import Path

VERSION = "v17.58.1"
BUILD_NAME = "Dashboard Text Layout Repair Hotfix"
CSS_PATH = "src/frontend/command_center/modern/claire_operating_environment.css"
DOC_PATH = "docs/dashboard/v17.58.1_dashboard_text_layout_repair.md"
DASHBOARD_PACK_PATH = "docs/update_packs/v17.58.1_dashboard_update_pack.md"
SYSTEM_PACK_PATH = "docs/update_packs/v17.58.1_system_runtime_update_pack.md"
MANIFEST_PATH = "data/build_manifests/v17.58.1_dashboard_text_repair_manifest.json"
INSTALL_RECORD_PATH = "data/build_manifests/v17.58.1_install_record.json"

REPAIR_MARKER_START = "/* === CLAIRE v17.58.1 TEXT LAYOUT REPAIR START === */"
REPAIR_MARKER_END = "/* === CLAIRE v17.58.1 TEXT LAYOUT REPAIR END === */"
TEXT_REPAIR_CSS = '\n/* === CLAIRE v17.58.1 TEXT LAYOUT REPAIR START === */\n/*\n  Text/layout repair only.\n  Purpose: preserve the v17.57-v17.58 runtime/route dashboard while fixing cramped,\n  clipped, over-compressed, and nowrap text on operating panels.\n*/\n:root {\n  --readable-line: 1.55;\n  --readable-line-tight: 1.35;\n  --readable-card-min: 210px;\n}\n\nbody {\n  text-rendering: optimizeLegibility;\n  -webkit-font-smoothing: antialiased;\n}\n\n.app-shell,\n.sidebar,\n.topbar,\n.workspace,\n.rail,\n.proofbar,\n.card,\n.stage-card,\n.route-card,\n.event,\n.empty,\n.table,\n.workspace-header,\n.rail-header,\n.brand,\n.launch-state,\n.state-chip,\n.nav button {\n  min-width: 0;\n}\n\n/* Stop important panel text from being crushed into one line. */\n.brand p,\n.subtitle,\n.workspace-header p,\n.card p,\n.card li,\n.event p,\n.empty p,\n.muted,\n.small,\n.stage-purpose,\n.stage-name,\n.route-card p,\n.route-card h4,\n.table th,\n.table td,\n.evidence-item p,\n.evidence-item b,\n.code,\n.proof-value,\n.proof-label,\n.status,\n.pill,\n.state-chip b,\n.state-chip span {\n  white-space: normal;\n  overflow-wrap: anywhere;\n  word-break: normal;\n  hyphens: auto;\n}\n\n.brand p,\n.workspace-header p,\n.card p,\n.event p,\n.empty p,\n.stage-purpose,\n.route-card p,\n.table td,\n.evidence-item p {\n  line-height: var(--readable-line);\n}\n\n/* Keep display typography sophisticated but not destructive on dense panels. */\n.kicker,\n.surface-kicker,\n.card-kicker,\n.rail-kicker,\n.section-title,\n.table th,\n.proof-label,\n.state-chip span {\n  letter-spacing: .12em;\n  line-height: var(--readable-line-tight);\n}\n\n.workspace-header h3,\n.topbar h2,\n.card h4,\n.route-card h4,\n.empty h4,\n.rail-header h3 {\n  overflow-wrap: anywhere;\n  line-height: 1.22;\n}\n\n/* Repair left navigation labels that were ellipsized too aggressively. */\n.nav button {\n  align-items: start;\n  min-height: 42px;\n}\n.nav-label {\n  white-space: normal;\n  overflow: visible;\n  text-overflow: clip;\n  line-height: 1.24;\n  padding-top: 1px;\n}\n.nav-num {\n  flex: 0 0 auto;\n}\n\n/* Repair chips/pills so labels remain readable instead of clipped. */\n.launch-state {\n  grid-template-columns: repeat(2, minmax(0, 1fr));\n}\n.state-chip {\n  min-height: 62px;\n}\n.state-chip b {\n  white-space: normal;\n  overflow: visible;\n  text-overflow: clip;\n  line-height: 1.22;\n}\n.pill {\n  white-space: normal;\n  line-height: 1.25;\n}\n.top-actions {\n  max-width: 48vw;\n}\n\n/* Give the topbar enough height when text wraps. */\n.topbar {\n  min-height: 74px;\n  height: auto;\n  padding-top: 12px;\n  padding-bottom: 12px;\n  gap: 14px;\n}\n.subtitle {\n  max-width: 980px;\n}\n\n/* Repair card density on previous panels and new route panels. */\n.grid.two,\n.grid.three,\n.grid.four {\n  grid-template-columns: repeat(auto-fit, minmax(var(--readable-card-min), 1fr));\n}\n.card {\n  padding: 18px;\n  min-height: 0;\n}\n.card h4 {\n  margin-bottom: 10px;\n}\n.metric {\n  line-height: 1.08;\n  overflow-wrap: anywhere;\n}\n\n/* Most text damage came from forcing 30 lifecycle stages into five narrow columns. */\n.stage-grid {\n  grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));\n  gap: 12px;\n}\n.stage-card {\n  min-height: 170px;\n  padding: 15px;\n}\n.stage-name {\n  font-size: 12.5px;\n  line-height: 1.32;\n}\n.stage-purpose {\n  font-size: 11.5px;\n}\n.stage-num {\n  margin-bottom: 11px;\n}\n\n/* Route panels need room for explanation text and stage pills. */\n.route-board {\n  grid-template-columns: minmax(0, 1fr);\n}\n.route-card {\n  padding: 17px;\n}\n.route-stages {\n  gap: 6px;\n}\n.stage-pill {\n  line-height: 1.25;\n  white-space: normal;\n  overflow-wrap: anywhere;\n}\n\n/* Tables should scroll horizontally rather than compress text into unreadable columns. */\n.table {\n  display: block;\n  width: 100%;\n  overflow-x: auto;\n  border-collapse: separate;\n}\n.table thead,\n.table tbody,\n.table tr {\n  width: 100%;\n}\n.table th,\n.table td {\n  min-width: 140px;\n  line-height: 1.45;\n}\n\n/* Proofbar text repair. */\n.proofbar {\n  min-height: 58px;\n}\n.proof-item {\n  overflow: visible;\n}\n.proof-value {\n  white-space: normal;\n  overflow: visible;\n  text-overflow: clip;\n  line-height: 1.2;\n}\n\n/* Right rail readability. */\n.rail-body {\n  gap: 12px;\n}\n.event {\n  padding: 13px;\n}\n.event b {\n  line-height: 1.28;\n  overflow-wrap: anywhere;\n}\n\n/* Avoid cramped desktop columns on moderately sized screens. */\n@media (max-width: 1450px) {\n  .app-shell {\n    grid-template-columns: 270px minmax(0, 1fr) 320px;\n  }\n  .stage-grid {\n    grid-template-columns: repeat(auto-fit, minmax(205px, 1fr));\n  }\n}\n\n@media (max-width: 1250px) {\n  .top-actions {\n    max-width: none;\n  }\n  .stage-grid {\n    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));\n  }\n}\n\n@media (max-width: 860px) {\n  body {\n    overflow: auto;\n  }\n  .app-shell {\n    height: auto;\n    min-height: 100vh;\n  }\n  .topbar,\n  .workspace-header {\n    grid-template-columns: 1fr;\n  }\n  .top-actions {\n    justify-content: flex-start;\n  }\n  .proofbar {\n    grid-template-columns: repeat(2, minmax(0, 1fr));\n  }\n}\n/* === CLAIRE v17.58.1 TEXT LAYOUT REPAIR END === */\n'
DOC = '# Claire v17.58.1 — Dashboard Text Layout Repair Hotfix\n\n## Purpose\n\nRepair panel text that became cramped, clipped, over-compressed, or ellipsized after v17.57-v17.58.\n\n## Scope\n\nThis is a dashboard CSS hotfix only. It does not change runtime orchestration, route contracts, lifecycle stage logic, runtime truth utilities, or backend files.\n\n## Repairs\n\n- Allows previous panel text to wrap naturally.\n- Removes aggressive nowrap/ellipsis behavior from navigation and proof/status panels.\n- Gives lifecycle stage cards more width using responsive auto-fit columns.\n- Gives route panels and tables more readable spacing.\n- Keeps the v17.57-v17.58 runtime execution mirror and route gate surfaces intact.\n\n## Safety\n\nThe installer backs up the current dashboard CSS before applying the repair block.\n'
DASHBOARD_PACK = '# Dashboard Update Pack — Claire v17.58.1\n\n## Name\n\nDashboard Text Layout Repair Hotfix\n\n## Purpose\n\nFix readability regressions in the operating dashboard after v17.57-v17.58.\n\n## Dashboard changes\n\n- Appends a guarded CSS repair block to `claire_operating_environment.css`.\n- Preserves all runtime mirror and route gate JavaScript.\n- Preserves launcher path.\n- Does not add new dashboard features.\n\n## Validation\n\nAfter install, verify:\n\n1. `src/frontend/command_center/modern/index.html` still loads.\n2. Navigation labels are readable.\n3. Previous panels no longer have clipped/overlapping text.\n4. Stage cards wrap names and descriptions cleanly.\n5. Route cards and proofbar text are readable.\n'
SYSTEM_PACK = '# System Runtime Update Pack — Claire v17.58.1\n\n## Name\n\nNo Runtime Change\n\n## Purpose\n\nDocument that v17.58.1 is a dashboard text repair only.\n\n## Runtime impact\n\nNone.\n\n## Files affected\n\n- `src/frontend/command_center/modern/claire_operating_environment.css`\n- docs/build manifest files only\n\n## Runtime safety\n\nNo backend imports, no FastAPI changes, no route execution changes, no lifecycle logic changes, and no runtime truth reader changes.\n'
MANIFEST = {
    "version": VERSION,
    "build_name": BUILD_NAME,
    "created_at": "2026-05-08T00:00:00Z",
    "launcher_path": "src/frontend/command_center/modern/index.html",
    "purpose": "Repair dashboard panel text readability after v17.57-v17.58 without changing runtime behavior.",
    "runtime_changed": False,
    "dashboard_changed": True,
    "files_written_or_updated": [CSS_PATH, DOC_PATH, DASHBOARD_PACK_PATH, SYSTEM_PACK_PATH, MANIFEST_PATH],
    "preserves": [
        "v17.57 runtime execution mirror",
        "v17.58 route gate and route branch surfaces",
        "launcher continuity",
        "rollback safety",
        "stages 16-22 preservation"
    ]
}


def timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def detect_project_root() -> Path:
    root = Path.cwd()
    markers = ["src", "main.py", "pyproject.toml", "requirements.txt"]
    found = [m for m in markers if (root / m).exists()]
    if not found:
        print("[WARN] No standard Claire project markers found in this folder.")
        print("[WARN] Continuing because the installer can create documentation paths, but CSS patch requires the dashboard CSS file.")
    return root


def backup_existing(root: Path, relative_path: str, backup_root: Path) -> None:
    target = root / relative_path
    if not target.exists():
        return
    backup_path = backup_root / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, backup_path)


def write_text(root: Path, relative_path: str, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")


def patch_css(root: Path, backup_root: Path) -> None:
    css_file = root / CSS_PATH
    if not css_file.exists():
        raise FileNotFoundError(f"Missing dashboard CSS file: {CSS_PATH}. Install v17.56 or v17.57-v17.58 first, then run this hotfix.")
    backup_existing(root, CSS_PATH, backup_root)
    current = css_file.read_text(encoding="utf-8")
    if REPAIR_MARKER_START in current and REPAIR_MARKER_END in current:
        before = current.split(REPAIR_MARKER_START)[0].rstrip()
        after = current.split(REPAIR_MARKER_END, 1)[1].lstrip()
        repaired = before + "\n\n" + TEXT_REPAIR_CSS.strip() + "\n"
        if after:
            repaired += "\n" + after
    else:
        repaired = current.rstrip() + "\n\n" + TEXT_REPAIR_CSS.strip() + "\n"
    css_file.write_text(repaired, encoding="utf-8", newline="\n")
    print(f"[PATCH] {CSS_PATH}")


def install() -> None:
    root = detect_project_root()
    backup_root = root / "backups" / f"claire_v17_58_1_{timestamp()}"
    backup_root.mkdir(parents=True, exist_ok=True)
    print(f"[CLAIRE] Installing {VERSION} — {BUILD_NAME}")
    print(f"[CLAIRE] Project root: {root}")
    print(f"[CLAIRE] Backup root: {backup_root}")
    patch_css(root, backup_root)
    docs = {
        DOC_PATH: DOC,
        DASHBOARD_PACK_PATH: DASHBOARD_PACK,
        SYSTEM_PACK_PATH: SYSTEM_PACK,
        MANIFEST_PATH: json.dumps(MANIFEST, indent=2),
    }
    for relative_path, content in docs.items():
        backup_existing(root, relative_path, backup_root)
        write_text(root, relative_path, content)
        print(f"[WRITE] {relative_path}")
    install_record = {
        "version": VERSION,
        "build_name": BUILD_NAME,
        "installed_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "backup_root": str(backup_root),
        "launcher_path": "src/frontend/command_center/modern/index.html",
        "runtime_changed": False,
        "dashboard_changed": True,
        "files_written_or_updated": [CSS_PATH, DOC_PATH, DASHBOARD_PACK_PATH, SYSTEM_PACK_PATH, MANIFEST_PATH],
        "rollback_note": "To rollback, copy the CSS file from backup_root back into the project root."
    }
    write_text(root, INSTALL_RECORD_PATH, json.dumps(install_record, indent=2))
    print(f"[WRITE] {INSTALL_RECORD_PATH}")
    print("")
    print("[DONE] Claire v17.58.1 dashboard text repair installed.")
    print("[NEXT] Restart/refresh the dashboard. If browser cache holds old CSS, use Ctrl+F5.")
    print(r"[PATH] src\frontend\command_center\modern\index.html")


if __name__ == "__main__":
    install()
