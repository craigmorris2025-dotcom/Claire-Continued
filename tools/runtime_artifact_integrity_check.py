#!/usr/bin/env python3
"""
Claire v19.85.7 Runtime Artifact Integrity Check
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audits" / "v19_85_7_runtime_artifact_integrity_check"
OUT_JSON = OUT_DIR / "runtime_artifact_integrity_check.json"
CONTRACT_DIR = ROOT / "data" / "evidence_governance"
CONTRACT_PATH = CONTRACT_DIR / "runtime_artifact_integrity_check.json"


REQUIRED_ARTIFACT_KEYS = ["manifest", "status", "lifecycle", "gates", "missing_evidence", "enrichment"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_hash(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_runtime_artifact_paths(run_manifest: Dict[str, Any]) -> Dict[str, Any]:
    artifact_paths = run_manifest.get("artifact_paths", {})
    missing_keys = [k for k in REQUIRED_ARTIFACT_KEYS if k not in artifact_paths]
    missing_files = []
    hashes = {}
    for key, rel in artifact_paths.items():
        path = ROOT / rel
        h = file_hash(path)
        hashes[key] = h
        if h is None:
            missing_files.append({"key": key, "path": rel})
    ok = not missing_keys and not missing_files
    return {"status": "valid" if ok else "invalid", "missing_keys": missing_keys, "missing_files": missing_files, "hashes": hashes}


def build_contract() -> Dict[str, Any]:
    return {
        "version": "v19.85.7",
        "build": "Runtime Artifact Integrity Check",
        "generated_at": utc_now(),
        "required_artifact_keys": REQUIRED_ARTIFACT_KEYS,
        "hash_algorithm": "sha256",
        "backend_owns_truth": True,
        "rule": "Runtime artifacts must exist and be hashable before promotion or replay.",
    }


def write_contract() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    contract = build_contract()
    CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")
    report = {
        "version": "v19.85.7",
        "build": "Runtime Artifact Integrity Check",
        "generated_at": utc_now(),
        "read_only": True,
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "contract": contract,
        "next_build": "v19.85.8 Evidence Governance Plateau Gate",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    report = write_contract()
    print(json.dumps({"status": "ok", "version": report["version"], "contract_path": report["contract_path"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
