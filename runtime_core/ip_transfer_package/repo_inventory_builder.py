from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

class RepoInventoryBuilder:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)
    def build_inventory(self) -> Dict[str, Any]:
        files = [str(p.relative_to(self.root)) for p in self.root.rglob("*") if p.is_file() and ".git" not in p.parts]
        return {"record_type": "repo_inventory", "file_count": len(files), "sample": files[:100]}
