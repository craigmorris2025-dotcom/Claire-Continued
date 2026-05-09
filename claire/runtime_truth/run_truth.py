from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .runtime_truth_contract import first_present, normalize_route, normalize_stage_status, normalize_terminal, now_utc


@dataclass
class RunTruth:
    run_id: str
    run_type: str
    started_at: str
    updated_at: str
    status: str
    active_stage: int | None
    selected_route: str
    terminal_state: str
    output_path: str
    validation_status: str
    memory_status: str
    source_path: str


def _active_stage(raw: Mapping[str, Any]) -> int | None:
    value = first_present(raw, ["active_stage", "current_stage", "stage", "core_lifecycle_summary.active_stage"], None)
    if isinstance(value, Mapping):
        value = first_present(value, ["number", "stage_number", "id"], None)
    try:
        if value is None:
            return None
        text = str(value).strip().lower().replace("stage_", "")
        number = int("".join(ch for ch in text if ch.isdigit()))
        return number if 1 <= number <= 30 else None
    except Exception:
        return None


def build_run_truth(raw: Mapping[str, Any], source_path: Optional[Path] = None) -> Dict[str, Any]:
    route_obj = raw.get("route_decision") if isinstance(raw.get("route_decision"), Mapping) else {}
    validation_obj = raw.get("validation_result") if isinstance(raw.get("validation_result"), Mapping) else raw.get("validation") if isinstance(raw.get("validation"), Mapping) else {}
    memory_obj = raw.get("memory") if isinstance(raw.get("memory"), Mapping) else raw.get("memory_eligibility") if isinstance(raw.get("memory_eligibility"), Mapping) else {}
    selected_route = normalize_route(first_present(raw, ["route_selected", "selected_route", "route", "route_type", "core_lifecycle_summary.route_selected"], None) or first_present(route_obj, ["route_selected", "selected_route", "route"], ""))
    terminal_state = normalize_terminal(first_present(raw, ["terminal_state", "status_terminal", "core_lifecycle_summary.terminal_state"], ""))
    status_raw = first_present(raw, ["status", "run_status", "core_lifecycle_summary.status"], None)
    status = normalize_stage_status(status_raw, default="pending")
    if terminal_state:
        status = "completed" if terminal_state not in {"failed", "blocked"} else terminal_state
    validation_status = str(first_present(validation_obj, ["status", "validation_status", "result", "passed"], first_present(raw, ["validation_status"], "unverified")))
    memory_status = str(first_present(memory_obj, ["status", "memory_status", "eligibility", "eligible"], first_present(raw, ["memory_status"], "unverified")))
    truth = RunTruth(
        run_id=str(first_present(raw, ["run_id", "id", "session_id", "trace_id"], "not_reported")),
        run_type=str(first_present(raw, ["run_type", "request_type", "intent", "mode"], "not_reported")),
        started_at=str(first_present(raw, ["started_at", "start_time", "created_at", "timestamp"], "not_reported")),
        updated_at=str(first_present(raw, ["updated_at", "completed_at", "timestamp"], now_utc())),
        status=status,
        active_stage=_active_stage(raw),
        selected_route=selected_route or "not_reported",
        terminal_state=terminal_state or "not_reported",
        output_path=str(first_present(raw, ["validated_output_path", "output_path", "export_path", "core_run_output_path"], source_path or "not_reported")),
        validation_status=validation_status,
        memory_status=memory_status,
        source_path=str(source_path) if source_path else "not_reported",
    )
    return asdict(truth)
