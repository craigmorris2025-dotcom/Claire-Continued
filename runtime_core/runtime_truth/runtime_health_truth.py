from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .runtime_truth_contract import now_utc


@dataclass
class RuntimeHealthTruth:
    api_status: str
    runtime_status: str
    exports_available: bool
    latest_output_found: bool
    rollback_available: bool
    internet_capability: str
    source_registry_status: str
    contract_registry_status: str
    last_error: str
    checked_at: str


def build_runtime_health_truth(root: Optional[Path], source_path: Optional[Path], raw: Mapping[str, Any]) -> Dict[str, Any]:
    root = root or Path.cwd()
    exports = root / "exports"
    backups = root / "backups"
    source_registry = root / "data" / "source_registry.json"
    contract_registry = root / "src" / "frontend" / "command_center" / "modern" / "runtime_truth_contract.json"
    last_error = raw.get("last_error") or raw.get("error") or raw.get("failure_reason") or "none_reported"
    return asdict(RuntimeHealthTruth(
        api_status="not_checked_by_offline_builder",
        runtime_status="runtime_truth_built" if source_path else "no_run_output_found",
        exports_available=exports.exists(),
        latest_output_found=bool(source_path and source_path.exists()),
        rollback_available=backups.exists() and any(backups.iterdir()) if backups.exists() else False,
        internet_capability=str(raw.get("internet_capability") or raw.get("live_capability") or "not_reported"),
        source_registry_status="present" if source_registry.exists() else "not_reported",
        contract_registry_status="present" if contract_registry.exists() else "not_reported",
        last_error=str(last_error),
        checked_at=now_utc(),
    ))
