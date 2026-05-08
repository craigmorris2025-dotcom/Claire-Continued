
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

VERSION = "17.62.4"
BUILD_NAME = "Workspace Stack Fix"
FILES = {'src/frontend/command_center/modern/claire_workspace_stack_fix.css': '/*\n  Claire v17.62.4 — Workspace Stack Fix\n\n  The dashboard shell is still clipping the Command panel and letting generated\n  runtime/validation/memory panels collide. This hotfix forces the center\n  workspace into a clean vertical document flow.\n\n  Runtime logic unchanged.\n*/\n\n/* Named classes added by claire_workspace_stack_fix.js */\n.claire-main-workspace-fixed {\n  height: auto !important;\n  min-height: 0 !important;\n  overflow: visible !important;\n}\n\n.claire-main-workspace-fixed > * {\n  position: relative !important;\n  height: auto !important;\n  min-height: 0 !important;\n  overflow: visible !important;\n  transform: none !important;\n}\n\n.claire-main-workspace-fixed .claire-stack-panel,\n.claire-main-workspace-fixed .claire-command-stack-panel,\n.claire-main-workspace-fixed .claire-validation-stack-panel,\n.claire-main-workspace-fixed .claire-memory-stack-panel {\n  position: relative !important;\n  display: block !important;\n  width: 100% !important;\n  height: auto !important;\n  min-height: 0 !important;\n  max-height: none !important;\n  overflow: visible !important;\n  clear: both !important;\n  margin: 0 0 22px 0 !important;\n  z-index: auto !important;\n}\n\n/* Command panel specifically: stop nested clipping. */\n.claire-command-stack-panel,\n.claire-command-stack-panel *,\n.claire-command-stack-panel [style] {\n  max-height: none !important;\n}\n\n.claire-command-stack-panel {\n  min-height: 420px !important;\n  padding-bottom: 28px !important;\n}\n\n.claire-command-stack-panel .claire-stack-scroll-kill,\n.claire-command-stack-panel .claire-stack-scroll-kill * {\n  max-height: none !important;\n}\n\n.claire-command-stack-panel .claire-stack-scroll-kill {\n  overflow: visible !important;\n  height: auto !important;\n  min-height: 0 !important;\n}\n\n/* Give runtime summary cards enough vertical room. */\n.claire-command-stack-panel [class*="card"],\n.claire-command-stack-panel [class*="metric"],\n.claire-command-stack-panel [class*="summary"],\n.claire-command-stack-panel [class*="run"],\n.claire-command-stack-panel [class*="route"],\n.claire-command-stack-panel [class*="terminal"] {\n  height: auto !important;\n  min-height: 120px !important;\n  overflow: visible !important;\n}\n\n/* Validation and memory generated panels need normal stack behavior. */\n#claire-validation-authority-panel,\n#claire-verified-memory-panel,\n.claire-validation-authority-panel,\n.claire-memory-panel,\n.claire-validation-stack-panel,\n.claire-memory-stack-panel {\n  position: relative !important;\n  display: block !important;\n  width: 100% !important;\n  height: auto !important;\n  min-height: 260px !important;\n  max-height: none !important;\n  overflow: visible !important;\n  clear: both !important;\n  margin: 22px 0 !important;\n  z-index: auto !important;\n}\n\n/* Stop the large circular status badges from forcing overlap. */\n.claire-validation-authority-panel .claire-validation-pill,\n.claire-memory-panel .claire-memory-pill,\n#claire-validation-authority-panel .claire-validation-pill,\n#claire-verified-memory-panel .claire-memory-pill {\n  min-width: 0 !important;\n  width: auto !important;\n  max-width: 170px !important;\n  min-height: 0 !important;\n  height: auto !important;\n  border-radius: 999px !important;\n  padding: 8px 12px !important;\n  line-height: 1.25 !important;\n}\n\n/* Some earlier cards created giant circle status badges through inherited rules. */\n.claire-validation-authority-panel [class*="pill"],\n.claire-memory-panel [class*="pill"] {\n  aspect-ratio: auto !important;\n}\n\n/* Make validation/memory headers wrap without collision. */\n.claire-validation-header,\n.claire-memory-header {\n  align-items: flex-start !important;\n  flex-wrap: wrap !important;\n}\n\n/* Internal grids must sit below headers. */\n.claire-validation-grid,\n.claire-memory-grid,\n.claire-validation-checks,\n.claire-memory-reasons {\n  position: relative !important;\n  clear: both !important;\n  width: 100% !important;\n}\n\n/* Right rail may scroll independently, but should not dictate center clipping. */\n.live-rail,\n.right-rail,\n.narrative-rail,\naside[class*="rail"],\nsection[class*="rail"] {\n  max-height: calc(100vh - 180px) !important;\n  overflow-y: auto !important;\n}\n\n/* The bottom proofbar should not float over the center workspace. */\n.proofbar,\n.status-rail,\n.bottom-rail,\n.claire-proofbar,\n[class*="proofbar"],\n[class*="bottom"] {\n  position: relative !important;\n  clear: both !important;\n  z-index: 2 !important;\n}\n\n/* Remove visible scrollbars from command content specifically. */\n.claire-command-stack-panel ::-webkit-scrollbar {\n  width: 0 !important;\n  height: 0 !important;\n}\n\n/* If old shell uses a fixed viewport workspace, allow vertical scrolling at page/root instead. */\nhtml,\nbody {\n  min-height: 100% !important;\n}\n\nbody {\n  overflow-y: auto !important;\n}\n\n/* If a dashboard has a main-center column, it should be vertical. */\n.center-column,\n.main-column,\n.content-column,\n.workspace-column,\n[class*="center"],\n[class*="workspace"] {\n  min-height: 0 !important;\n}\n\n/* Responsive: stack everything. */\n@media (max-width: 1180px) {\n  .claire-command-stack-panel {\n    min-height: 480px !important;\n  }\n\n  .claire-validation-grid,\n  .claire-memory-grid {\n    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)) !important;\n  }\n}\n\n@media (max-width: 780px) {\n  .claire-command-stack-panel,\n  #claire-validation-authority-panel,\n  #claire-verified-memory-panel,\n  .claire-validation-authority-panel,\n  .claire-memory-panel {\n    min-height: 0 !important;\n  }\n}\n', 'src/frontend/command_center/modern/claire_workspace_stack_fix.js': '(function () {\n  "use strict";\n\n  function norm(value) {\n    return String(value || "").replace(/\\s+/g, " ").trim().toLowerCase();\n  }\n\n  function textOf(node) {\n    return norm(node?.innerText || node?.textContent || "");\n  }\n\n  function findPanelByHeading(headingText) {\n    const headings = Array.from(document.querySelectorAll("h1,h2,h3,h4,.section-title,.surface-title,.panel-title"));\n    const wanted = headingText.toLowerCase();\n\n    for (const heading of headings) {\n      if (!textOf(heading).includes(wanted)) continue;\n\n      const panel = heading.closest(\n        "section, article, .dashboard-panel, .claire-panel, .surface, .claire-surface, .portal, .claire-portal, .command-panel, .command-surface, div"\n      );\n\n      if (panel && panel !== document.body) return panel;\n    }\n\n    return null;\n  }\n\n  function likelyMainWorkspace() {\n    const selectors = [\n      "#main-workspace",\n      "#workspace",\n      "#app",\n      "main",\n      ".main-workspace",\n      ".workspace",\n      ".workspace-column",\n      ".content-column",\n      ".main-column",\n      ".center-column",\n      ".dashboard-shell",\n      ".claire-shell",\n      ".operating-environment"\n    ];\n\n    for (const selector of selectors) {\n      const node = document.querySelector(selector);\n      if (node) return node;\n    }\n\n    return document.body;\n  }\n\n  function killScrollContainersInside(panel) {\n    if (!panel) return;\n    const nodes = [panel, ...Array.from(panel.querySelectorAll("*"))];\n\n    for (const node of nodes) {\n      const style = window.getComputedStyle(node);\n      const hasScroll = ["auto", "scroll", "hidden"].includes(style.overflowY) || ["auto", "scroll", "hidden"].includes(style.overflow);\n      const heightLimited =\n        style.maxHeight !== "none" ||\n        (style.height && style.height !== "auto" && node.scrollHeight > node.clientHeight + 20);\n\n      if (hasScroll || heightLimited) {\n        node.classList.add("claire-stack-scroll-kill");\n        node.style.overflow = "visible";\n        node.style.overflowY = "visible";\n        node.style.maxHeight = "none";\n        if (node !== document.body && node !== document.documentElement) {\n          node.style.height = "auto";\n        }\n      }\n    }\n  }\n\n  function applyStackFix() {\n    const main = likelyMainWorkspace();\n    main.classList.add("claire-main-workspace-fixed");\n\n    const commandPanel = findPanelByHeading("command");\n    if (commandPanel) {\n      commandPanel.classList.add("claire-stack-panel", "claire-command-stack-panel");\n      killScrollContainersInside(commandPanel);\n    }\n\n    const validationPanel =\n      document.getElementById("claire-validation-authority-panel") ||\n      document.querySelector(".claire-validation-authority-panel") ||\n      findPanelByHeading("validation authority");\n\n    if (validationPanel) {\n      validationPanel.classList.add("claire-stack-panel", "claire-validation-stack-panel");\n      validationPanel.style.position = "relative";\n      validationPanel.style.height = "auto";\n      validationPanel.style.maxHeight = "none";\n      validationPanel.style.overflow = "visible";\n    }\n\n    const memoryPanel =\n      document.getElementById("claire-verified-memory-panel") ||\n      document.querySelector(".claire-memory-panel") ||\n      findPanelByHeading("verified memory");\n\n    if (memoryPanel) {\n      memoryPanel.classList.add("claire-stack-panel", "claire-memory-stack-panel");\n      memoryPanel.style.position = "relative";\n      memoryPanel.style.height = "auto";\n      memoryPanel.style.maxHeight = "none";\n      memoryPanel.style.overflow = "visible";\n    }\n\n    // If validation/memory were appended inside a cramped surface, move them after\n    // the command panel inside the main workspace in a stable order.\n    if (commandPanel && main && validationPanel && validationPanel.parentElement !== main) {\n      commandPanel.insertAdjacentElement("afterend", validationPanel);\n    }\n\n    if (validationPanel && main && memoryPanel && memoryPanel.parentElement !== main) {\n      validationPanel.insertAdjacentElement("afterend", memoryPanel);\n    } else if (commandPanel && main && memoryPanel && memoryPanel.parentElement !== main) {\n      commandPanel.insertAdjacentElement("afterend", memoryPanel);\n    }\n  }\n\n  function boot() {\n    applyStackFix();\n\n    // Prior bridge scripts mount validation/memory after DOMContentLoaded.\n    // Run a few times to catch late-mounted panels.\n    setTimeout(applyStackFix, 400);\n    setTimeout(applyStackFix, 1200);\n    setTimeout(applyStackFix, 2400);\n  }\n\n  if (document.readyState === "loading") {\n    document.addEventListener("DOMContentLoaded", boot);\n  } else {\n    boot();\n  }\n})();\n', 'docs/dashboard/v17.62.4_workspace_stack_fix.md': '# Claire v17.62.4 — Workspace Stack Fix\n\n## Purpose\n\nThe dashboard still showed a clipped Command panel and overlapping validation/memory surfaces after v17.62.3. This hotfix adds a small JS classifier and CSS stack fix to force major center workspace surfaces into normal vertical flow.\n\n## What it fixes\n\n- Command panel stops clipping its internal runtime cards\n- Command panel scroll container is neutralized\n- Validation Authority panel is moved into the center stack if it was mounted inside a cramped surface\n- Verified Memory panel is moved into the same stack after validation\n- Large status pills stop behaving like giant circular badges\n- Main workspace sections flow vertically\n\n## Files\n\n```text\nsrc/frontend/command_center/modern/claire_workspace_stack_fix.css\nsrc/frontend/command_center/modern/claire_workspace_stack_fix.js\n```\n\nPatched:\n\n```text\nsrc/frontend/command_center/modern/index.html\n```\n\n## Scope\n\nNo runtime logic changes.\nNo validation changes.\nNo memory changes.\nLayout/DOM placement only.\n', 'docs/update_packs/v17.62.4_dashboard_hotfix_pack.md': '# v17.62.4 Dashboard Hotfix Pack\n\n## User-facing fix\n\nFixes the center workspace stack so Command, Validation Authority, and Verified Memory stop colliding.\n\n## Verification\n\nAfter install and hard refresh:\n\n1. Command cards should not be clipped.\n2. Validation panel should begin below the Command section.\n3. Memory panel should begin below Validation.\n4. Giant circular status badges should be replaced by compact pills.\n5. Right Live Intelligence rail can still scroll independently.\n', 'data/build_manifests/v17.62.4_workspace_stack_fix_manifest.json': '{\n  "version": "17.62.4",\n  "name": "Workspace Stack Fix",\n  "build_type": "dashboard_hotfix",\n  "purpose": "Force main workspace surfaces into clean vertical stack and stop command/validation/memory overlap.",\n  "depends_on": [\n    "v17.62.3 Overlap Fix Hotfix"\n  ],\n  "installed_files": [\n    "docs/dashboard/v17.62.4_workspace_stack_fix.md",\n    "docs/update_packs/v17.62.4_dashboard_hotfix_pack.md",\n    "src/frontend/command_center/modern/claire_workspace_stack_fix.css",\n    "src/frontend/command_center/modern/claire_workspace_stack_fix.js"\n  ],\n  "safety": {\n    "rollback_backups": true,\n    "launcher_path_preserved": "src/frontend/command_center/modern/index.html",\n    "runtime_logic_unchanged": true,\n    "validation_logic_unchanged": true,\n    "memory_logic_unchanged": true\n  }\n}\n'}

CSS_FILE = "claire_workspace_stack_fix.css"
JS_FILE = "claire_workspace_stack_fix.js"

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
        css_tag = '\n<link rel="stylesheet" href="claire_workspace_stack_fix.css">\n'
        if "</head>" in html:
            html = html.replace("</head>", css_tag + "</head>", 1)
        else:
            html = css_tag + html

    if JS_FILE not in html:
        script_tag = '\n<script src="claire_workspace_stack_fix.js"></script>\n'
        if "</body>" in html:
            html = html.replace("</body>", script_tag + "</body>", 1)
        else:
            html = html + script_tag

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
            "Forces Command, Validation, and Memory panels into stable vertical flow.",
            "Neutralizes clipped scroll containers inside Command.",
            "Runtime, validation, and memory logic unchanged."
        ]
    }
    record_path = root / "data" / "build_manifests" / "v17.62.4_install_record.json"
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

def main() -> None:
    root = project_root()
    backup_root = root / "backups" / f"claire_v17_62_4_{utc_stamp()}"
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
    print("Fixed center workspace stacking:")
    print("  - Command panel can expand")
    print("  - Validation panel stacks below Command")
    print("  - Memory panel stacks below Validation")
    print("  - Giant circular status badges are compacted")
    print("")
    print("Hard refresh the dashboard with Ctrl+F5.")
    print("=" * 72)

if __name__ == "__main__":
    main()
