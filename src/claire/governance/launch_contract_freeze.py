"""Claire v17.49 contract freeze utilities."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional


@dataclass(frozen=True)
class FrozenContractSnapshot:
    name: str
    version: str
    digest: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def freeze_contract(name: str, version: str, payload: Mapping[str, Any]) -> FrozenContractSnapshot:
    normalized = json.loads(json.dumps(dict(payload), sort_keys=True, default=str))
    digest = hashlib.sha256(json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return FrozenContractSnapshot(name=name, version=version, digest=digest, payload=normalized)


def write_contract_freeze(path: str | Path, snapshots: Iterable[FrozenContractSnapshot]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"frozen_contracts": [snapshot.to_dict() for snapshot in snapshots]}
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target


def read_contract_freeze(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
