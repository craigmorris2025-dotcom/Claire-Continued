from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


class StateRecoveryManager:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "continuous_autonomous_intelligence" / "checkpoints"
        self.root.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, name: str, state: Dict[str, object]) -> Path:
        path = self.root / f"{name}.json"
        path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load_checkpoint(self, name: str) -> Dict[str, object]:
        path = self.root / f"{name}.json"
        if not path.exists():
            return {"status": "missing", "name": name}
        return json.loads(path.read_text(encoding="utf-8"))

    def list_checkpoints(self) -> list[str]:
        return sorted(path.name for path in self.root.glob("*.json"))
