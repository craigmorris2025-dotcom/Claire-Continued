#!/usr/bin/env python3
from __future__ import annotations
import ast, json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
SRC = ROOT / "src" / "claire"

def module_name(path: Path) -> str:
    rel = path.relative_to(ROOT / "src").with_suffix("")
    return ".".join(rel.parts)

def imports_for(path: Path):
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
    return sorted(set(i for i in imports if i.startswith("claire")))

def main() -> int:
    modules = []
    for path in SRC.rglob("*.py"):
        modules.append({
            "module": module_name(path),
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "claire_imports": imports_for(path),
        })
    payload = {
        "map": "runtime_dependency_map",
        "version": "v16.28",
        "created_at": datetime.now().isoformat(),
        "module_count": len(modules),
        "modules": modules,
    }
    out_dir = ROOT / "data" / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "runtime_dependency_map.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"map": payload["map"], "module_count": payload["module_count"]}, indent=2))
    print(f"\nDependency map written: {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
