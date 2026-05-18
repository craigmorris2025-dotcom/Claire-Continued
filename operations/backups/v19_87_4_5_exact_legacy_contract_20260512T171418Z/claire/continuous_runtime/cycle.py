from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import json
from datetime import datetime, timezone

try:
    from claire.runtime.continuous_runtime_contracts import SchedulerPolicy
    from claire.runtime.continuous_runtime_scheduler import ContinuousGovernedRuntimeScheduler
except Exception:
    SchedulerPolicy = None
    ContinuousGovernedRuntimeScheduler = None


@dataclass
class ContinuousRuntimeCycleResult:
    status: str = "blocked"
    terminal_state: str = "blocked"
    route: str = "none"
    cycle_id: str = ""
    evidence_count: int = 0
    runtime_truth_mutated: bool = False
    promotion_required: bool = True
    blocked_reasons: list[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        if self.payload:
            return dict(self.payload)
        return {
            "status": self.status,
            "terminal_state": self.terminal_state,
            "route": self.route,
            "cycle_id": self.cycle_id,
            "evidence_count": self.evidence_count,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "promotion_required": self.promotion_required,
            "blocked_reasons": list(self.blocked_reasons),
        }


class ContinuousRuntimeCycle:
    """Legacy-compatible wrapper around the governed scheduler."""

    def __init__(self, scheduler: Optional[Any] = None) -> None:
        if scheduler is not None:
            self.scheduler = scheduler
        elif SchedulerPolicy is not None and ContinuousGovernedRuntimeScheduler is not None:
            self.scheduler = ContinuousGovernedRuntimeScheduler(
                policy=SchedulerPolicy(
                    enabled=True,
                    fail_closed=True,
                    max_cycles=1,
                    max_iterations_per_cycle=1,
                    allow_live_sources=False,
                    allow_runtime_truth_mutation=False,
                    require_health_green=True,
                    require_review_gate_for_promotion=True,
                ),
                runtime_adapter=lambda request, envelope, index: {
                    "status": "completed",
                    "terminal_state": "insufficient_data",
                    "route": str(request.get("route") or "discovery"),
                    "evidence_count": int(request.get("evidence_count") or 0),
                    "rejection_reasons": ["legacy_compatibility_cycle_no_admissible_runtime_adapter"],
                },
            )
        else:
            self.scheduler = None

    def run(self, request: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> ContinuousRuntimeCycleResult:
        payload: Dict[str, Any] = {}
        if request:
            payload.update(dict(request))
        payload.update(kwargs)
        if "input_summary" not in payload:
            payload["input_summary"] = str(
                payload.get("query")
                or payload.get("raw_input")
                or payload.get("input")
                or "continuous runtime compatibility cycle"
            )

        if self.scheduler is None:
            return ContinuousRuntimeCycleResult(
                blocked_reasons=["continuous_runtime_scheduler_unavailable"],
            )

        result = self.scheduler.run_cycle(payload)
        result_payload = result.to_payload() if hasattr(result, "to_payload") else dict(result)
        return ContinuousRuntimeCycleResult(
            status=str(result_payload.get("status") or "blocked"),
            terminal_state=str(result_payload.get("terminal_state") or "blocked"),
            route=str(result_payload.get("route") or "none"),
            cycle_id=str(result_payload.get("cycle_id") or ""),
            evidence_count=int(result_payload.get("evidence_count") or 0),
            runtime_truth_mutated=bool(result_payload.get("runtime_truth_mutated") or False),
            promotion_required=bool(result_payload.get("promotion_required", True)),
            blocked_reasons=list(result_payload.get("blocked_reasons") or []),
            payload=result_payload,
        )


def _write_json_if_missing(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def ensure_continuous_runtime_cycle() -> ContinuousRuntimeCycle:
    return ContinuousRuntimeCycle()


def run_continuous_runtime_cycle(request: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
    return ensure_continuous_runtime_cycle().run(request, **kwargs).to_payload()


def ensure_continuous_runtime_files(root: Optional[str | Path] = None, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Legacy v19.84.2 file seeding API.

    Seeds the stable compatibility file surface without creating admissible
    evidence, review promotion, live-source execution, dashboard-owned truth,
    or runtime truth mutation.
    """
    base = Path(root) if root is not None else Path.cwd()

    output_dir = base / "output"
    runtime_dir = output_dir / "continuous_runtime"
    review_dir = output_dir / "review_queue"
    data_dir = base / "data"
    data_runtime_dir = data_dir / "continuous_runtime"

    for directory in [output_dir, runtime_dir, review_dir, data_dir, data_runtime_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    seed_payload = {
        "status": "initialized",
        "terminal_state": "not_started",
        "route": "none",
        "runtime_truth_mutated": False,
        "promotion_required": True,
        "review_candidate_created": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    files = {
        "state_file": runtime_dir / "continuous_runtime_state.json",
        "cycle_file": runtime_dir / "continuous_runtime_cycle.json",
        "manifest_file": runtime_dir / "continuous_runtime_manifest.json",
        "review_candidates_file": review_dir / "review_candidates.json",
        "data_state_file": data_runtime_dir / "continuous_runtime_state.json",
        "data_cycle_file": data_runtime_dir / "continuous_runtime_cycle.json",
        # extra legacy aliases used by earlier tests/builds
        "legacy_state_file": output_dir / "continuous_runtime_state.json",
        "legacy_cycle_file": output_dir / "continuous_runtime_cycle.json",
        "legacy_review_candidates_file": output_dir / "review_candidates.json",
    }

    for name, path in files.items():
        payload = dict(seed_payload)
        payload["file_role"] = name
        if "review_candidates" in name:
            payload["candidates"] = []
        _write_json_if_missing(path, payload)

    return {
        "ok": True,
        "seeded": True,
        "output_dir": str(output_dir),
        "runtime_dir": str(runtime_dir),
        "review_dir": str(review_dir),
        "data_dir": str(data_dir),
        **{name: str(path) for name, path in files.items()},
    }


def _coerce_legacy_args_to_request(*args: Any, **kwargs: Any) -> tuple[Dict[str, Any], Optional[Path]]:
    request: Dict[str, Any] = {}
    root: Optional[Path] = None

    for arg in args:
        if isinstance(arg, Mapping):
            request.update(dict(arg))
        elif isinstance(arg, (str, Path)):
            text = str(arg)
            # If it looks like a path, use it as root; otherwise treat as input.
            if any(sep in text for sep in ["/", "\\"]) or text in {".", ".."}:
                root = Path(text)
            elif "input_summary" not in request:
                request["input_summary"] = text
            else:
                request.setdefault("extra_args", []).append(text)
        elif arg is not None:
            request.setdefault("extra_args", []).append(arg)

    if "root" in kwargs:
        root = Path(kwargs.pop("root"))
    if "base_dir" in kwargs:
        root = Path(kwargs.pop("base_dir"))
    if "project_root" in kwargs:
        root = Path(kwargs.pop("project_root"))

    request.update(kwargs)
    if "input_summary" not in request:
        request["input_summary"] = str(
            request.get("query")
            or request.get("raw_input")
            or request.get("input")
            or "continuous runtime compatibility cycle"
        )

    return request, root


def run_once(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Legacy v19.84.2 API accepting old positional call patterns."""
    request, root = _coerce_legacy_args_to_request(*args, **kwargs)
    files = ensure_continuous_runtime_files(root)
    payload = run_continuous_runtime_cycle(request)
    payload["review_candidate_created"] = False
    payload["files_seeded"] = True
    payload["files"] = files
    return payload


ensure_cycle = ensure_continuous_runtime_cycle
run_cycle = run_continuous_runtime_cycle
