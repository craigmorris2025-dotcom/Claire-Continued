
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

VERSION = "17.62.3"
BUILD_NAME = "Overlap Fix Hotfix"
FILES = {'src/frontend/command_center/modern/claire_overlap_fix.css': '/*\n  Claire v17.62.3 — Overlap Fix Hotfix\n\n  Purpose:\n  - Stop the command/runtime summary region from clipping its cards.\n  - Stop the section below from overlapping upward.\n  - Let main workspace sections size to content.\n  - Keep this CSS broad enough to catch the current shell without changing runtime logic.\n*/\n\n/* Main vertical flow must size to content instead of clipping. */\nmain,\n#app,\n#workspace,\n#main-workspace,\n.command-center,\n.operating-environment,\n.claire-operating-environment,\n.claire-shell,\n.dashboard-shell,\n.workspace-stack,\n.main-stack,\n.surface-stack {\n  height: auto !important;\n  min-height: 0 !important;\n  overflow: visible !important;\n}\n\n/* Major stacked sections in the center column should never overlap. */\nmain > section,\nmain > article,\n#app > section,\n#app > article,\n#main-workspace > section,\n#main-workspace > article,\n.command-panel,\n.command-surface,\n.dashboard-panel,\n.claire-panel,\n.surface,\n.claire-surface,\n.portal,\n.claire-portal {\n  position: relative !important;\n  clear: both !important;\n  height: auto !important;\n  min-height: 0 !important;\n  overflow: visible !important;\n  margin-bottom: 18px !important;\n}\n\n/* Command area and its first summary block need extra room. */\n#command,\n.command,\n.command-panel,\n.command-surface,\n.command-workspace,\n.command-workspace-panel,\n.command-summary,\n.runtime-summary,\n.top-summary,\n.hero-summary,\n.hero-panel {\n  height: auto !important;\n  min-height: 220px !important;\n  overflow: visible !important;\n  padding-bottom: 20px !important;\n}\n\n/* Grids that hold the run/route/terminal cards must expand, not clip. */\n.command-grid,\n.command-summary-grid,\n.runtime-grid,\n.runtime-summary-grid,\n.summary-grid,\n.hero-grid,\n.panel-grid,\n.cards-grid {\n  display: grid !important;\n  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)) !important;\n  gap: 18px !important;\n  height: auto !important;\n  min-height: 0 !important;\n  overflow: visible !important;\n  align-items: stretch !important;\n  margin-bottom: 14px !important;\n}\n\n/* Individual metric cards should never be partially hidden. */\n.run-card,\n.route-card,\n.terminal-card,\n.status-card,\n.metric-card,\n.summary-card,\n.info-card,\n.command-card,\n.dashboard-card,\n.claire-card {\n  position: relative !important;\n  height: auto !important;\n  min-height: 118px !important;\n  overflow: visible !important;\n  padding-bottom: 18px !important;\n}\n\n/* The specific command cards shown in the screenshot are being cut off. */\n[class*="run-id"],\n[class*="route"],\n[class*="terminal"],\n[class*="validation"],\n[class*="memory"],\n[data-surface="run"],\n[data-surface="route"],\n[data-surface="terminal"] {\n  height: auto !important;\n  min-height: 118px !important;\n  overflow: visible !important;\n}\n\n/* Prevent lower panels from sitting on top of the command summary region. */\n#claire-validation-authority-panel,\n#claire-verified-memory-panel,\n.claire-validation-authority-panel,\n.claire-memory-panel,\n.validation-panel,\n.memory-panel {\n  position: relative !important;\n  margin-top: 18px !important;\n  clear: both !important;\n  z-index: 1 !important;\n}\n\n/* Containers that previously had internal scrollbars should stop clipping content here. */\n.command-panel *,\n.command-surface *,\n.command-summary *,\n.runtime-summary * {\n  min-width: 0;\n}\n\n/* The scroll bars visible on the clipped block suggest a nested overflow container. Neutralize it. */\n.command-panel [style*="overflow"],\n.command-surface [style*="overflow"],\n.runtime-summary [style*="overflow"],\n.summary-grid [style*="overflow"] {\n  overflow: visible !important;\n  max-height: none !important;\n}\n\n/* If there is a center content rail, let it flow naturally. */\n.center-column,\n.main-column,\n.content-column,\n.workspace-column {\n  height: auto !important;\n  overflow: visible !important;\n}\n\n/* The next panel should start beneath the previous content, not on top of it. */\nsection + section,\narticle + article,\nsection + article,\narticle + section,\n.command-panel + section,\n.command-surface + section,\n.command-panel + .dashboard-panel,\n.command-surface + .dashboard-panel,\n.command-panel + .claire-validation-authority-panel,\n.command-surface + .claire-validation-authority-panel {\n  margin-top: 18px !important;\n}\n\n/* Responsive: stack these cards on smaller widths to reduce pressure. */\n@media (max-width: 1200px) {\n  .command-grid,\n  .command-summary-grid,\n  .runtime-grid,\n  .runtime-summary-grid,\n  .summary-grid,\n  .hero-grid,\n  .panel-grid,\n  .cards-grid {\n    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)) !important;\n  }\n}\n\n@media (max-width: 760px) {\n  .command-grid,\n  .command-summary-grid,\n  .runtime-grid,\n  .runtime-summary-grid,\n  .summary-grid,\n  .hero-grid,\n  .panel-grid,\n  .cards-grid {\n    grid-template-columns: 1fr !important;\n  }\n\n  .run-card,\n  .route-card,\n  .terminal-card,\n  .status-card,\n  .metric-card,\n  .summary-card,\n  .info-card,\n  .command-card,\n  .dashboard-card,\n  .claire-card {\n    min-height: 108px !important;\n  }\n}\n', 'docs/dashboard/v17.62.3_overlap_fix.md': '# Claire v17.62.3 — Overlap Fix Hotfix\n\n## Purpose\n\nFix the overlap/clipping in the main workspace where the command/runtime summary cards are cut off and the validation panel begins too early.\n\n## What it fixes\n\n- Command/runtime summary region can expand to its full height\n- Run/route/terminal cards stop getting clipped\n- Lower sections stop overlapping upward\n- Center workspace panels size to content instead of fixed clipping\n\n## Files\n\n```text\nsrc/frontend/command_center/modern/claire_overlap_fix.css\n```\n\nPatched:\n\n```text\nsrc/frontend/command_center/modern/index.html\n```\n\n## Scope\n\nNo runtime logic changes.\nNo validation changes.\nNo memory changes.\nCSS/layout only.\n', 'docs/update_packs/v17.62.3_dashboard_hotfix_pack.md': '# v17.62.3 Dashboard Hotfix Pack\n\n## User-facing fix\n\nStops the overlap visible in the command/runtime summary area and the validation panel beneath it.\n\n## Verification\n\nAfter install:\n\n1. Hard refresh with Ctrl+F5.\n2. Confirm the run/route cards are fully visible.\n3. Confirm the section below begins beneath the first block instead of covering it.\n4. Confirm no new runtime behavior changed.\n', 'data/build_manifests/v17.62.3_overlap_fix_manifest.json': '{\n  "version": "17.62.3",\n  "name": "Overlap Fix Hotfix",\n  "build_type": "dashboard_hotfix",\n  "purpose": "Fix command/runtime summary clipping and panel overlap in the main workspace.",\n  "depends_on": [\n    "v17.62.2 Search Relocation + Mic Button Hotfix"\n  ],\n  "installed_files": [\n    "docs/dashboard/v17.62.3_overlap_fix.md",\n    "docs/update_packs/v17.62.3_dashboard_hotfix_pack.md",\n    "src/frontend/command_center/modern/claire_overlap_fix.css"\n  ],\n  "safety": {\n    "rollback_backups": true,\n    "launcher_path_preserved": "src/frontend/command_center/modern/index.html",\n    "runtime_logic_unchanged": true,\n    "layout_only": true\n  }\n}\n'}

CSS_FILE = "claire_overlap_fix.css"

def utc_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def project_root() -> Path:
    return Path.cwd().resolve()

def backup_existing(root: Path, relative_path: str, backup_root: Path) -> None:
    target = root / relative_path
    if not target.exists():
        return
    backup_path = backup_root / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file():
        shutil.copy2(target, backup_path)
    elif target.is_dir():
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(target, backup_path)

def write_text(root: Path, relative_path: str, content: str, backup_root: Path) -> None:
    target = root / relative_path
    backup_existing(root, relative_path, backup_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

def patch_index_html(root: Path, backup_root: Path) -> bool:
    index_rel = "src/frontend/command_center/modern/index.html"
    index_path = root / index_rel
    if not index_path.exists():
        return False

    html = index_path.read_text(encoding="utf-8", errors="ignore")
    original = html

    if CSS_FILE not in html:
        css_tag = '\n<link rel="stylesheet" href="claire_overlap_fix.css">\n'
        if "</head>" in html:
            html = html.replace("</head>", css_tag + "</head>", 1)
        else:
            html = css_tag + html

    if html != original:
        backup_existing(root, index_rel, backup_root)
        index_path.write_text(html, encoding="utf-8")

    return True

def write_install_record(root: Path, backup_root: Path, index_patched: bool) -> None:
    record = {
        "version": VERSION,
        "build_name": BUILD_NAME,
        "installed_at_utc": datetime.utcnow().isoformat() + "Z",
        "project_root": str(root),
        "backup_root": str(backup_root),
        "index_patched": index_patched,
        "files_written": sorted(FILES.keys()),
        "notes": [
            "Fixes overlap in command/runtime summary area.",
            "Lets cards and panels expand to content height.",
            "Runtime logic unchanged."
        ]
    }
    record_path = root / "data" / "build_manifests" / "v17.62.3_install_record.json"
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

def main() -> None:
    root = project_root()
    backup_root = root / "backups" / f"claire_v17_62_3_{utc_stamp()}"
    backup_root.mkdir(parents=True, exist_ok=True)

    for relative_path, content in FILES.items():
        write_text(root, relative_path, content, backup_root)

    index_patched = patch_index_html(root, backup_root)
    write_install_record(root, backup_root, index_patched)

    print("=" * 72)
    print(f"Claire v{VERSION} installed: {BUILD_NAME}")
    print("=" * 72)
    print(f"Project root: {root}")
    print(f"Backups:      {backup_root}")
    print("")
    print("Fixed main workspace overlap/clipping:")
    print("  - command/runtime summary can expand")
    print("  - cards stop being cut off")
    print("  - lower panels stop overlapping upward")
    print("")
    print("Hard refresh the dashboard with Ctrl+F5.")
    print("=" * 72)

if __name__ == "__main__":
    main()
