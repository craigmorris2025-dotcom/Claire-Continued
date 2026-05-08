#!/usr/bin/env python3
from __future__ import annotations
import ast, json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
PROTECTED = [
    "main.py",
    "src/claire/app.py",
    "src/claire/api",
    "src/claire/orchestrator",
    "src/claire/lifecycle",
    "src/claire/engines",
    "src/claire/output",
    "src/claire/dashboard",
    "src/claire/technology/technology_intelligence.py",
]

def classify(path: Path) -> str:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    if rel.startswith("archive/") or rel.startswith("tests/placeholder_disabled/"):
        return "disabled_or_archived"
    if rel.startswith("exports/") or rel.startswith("output/") or rel.startswith("logs/"):
        return "generated"
    if rel.startswith(".claire_install/"):
        return "install_record"
    if any(rel == p or rel.startswith(p.rstrip("/") + "/") for p in PROTECTED):
        return "protected_runtime"
    if rel.startswith("src/claire/"):
        return "active_runtime"
    if rel.startswith("tests/"):
        return "active_test"
    if rel.startswith("docs/"):
        return "documentation"
    return "supporting"

def parse_imports(path: Path):
    imports = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig", errors="ignore"))
    except Exception:
        return imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return sorted(set(imports))

def main() -> int:
    records = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if rel.startswith(".git/") or rel.startswith(".venv/"):
            continue
        item = {
            "path": rel,
            "category": classify(path),
            "suffix": path.suffix,
            "size_bytes": path.stat().st_size,
        }
        if rel.startswith("src/claire/") and path.suffix == ".py":
            item["imports"] = parse_imports(path)
        records.append(item)

    category_counts = {}
    for item in records:
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1

    payload = {
        "manifest": "runtime_manifest",
        "version": "v16.28",
        "created_at": datetime.now().isoformat(),
        "root": str(ROOT),
        "file_count": len(records),
        "category_counts": category_counts,
        "protected_paths": PROTECTED,
        "files": records,
    }
    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "runtime_manifest.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ["manifest", "version", "file_count", "category_counts"]}, indent=2))
    print(f"\nManifest written: {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
