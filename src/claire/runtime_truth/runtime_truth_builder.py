from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from .evidence_truth import build_evidence_truth
from .memory_truth import build_memory_truth
from .route_truth import build_route_truth
from .run_truth import build_run_truth
from .runtime_health_truth import build_runtime_health_truth
from .runtime_truth_contract import SCHEMA_VERSION, now_utc
from .stage_truth import build_stage_truth
from .terminal_truth import build_terminal_truth
from .validation_truth import build_validation_truth

CORE_OUTPUT_NAMES = {"core_run_output.json", "dashboard_runtime_truth.json", "run_output.json", "latest_run_output.json"}


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def find_latest_core_output(root: Path) -> Optional[Path]:
    candidates: List[Path] = []
    for base in [root / "exports", root / "output", root / "data"]:
        if not base.exists():
            continue
        for path in base.rglob("*.json"):
            if path.name in CORE_OUTPUT_NAMES or path.name.endswith("core_run_output.json"):
                # Avoid recursively consuming the canonical truth file unless no real core output exists.
                candidates.append(path)
    real = [p for p in candidates if p.name != "dashboard_runtime_truth.json"]
    selected = real or candidates
    if not selected:
        return None
    return max(selected, key=lambda p: p.stat().st_mtime)


def build_runtime_truth(raw: Mapping[str, Any], source_path: Optional[Path] = None, root: Optional[Path] = None) -> Dict[str, Any]:
    run_truth = build_run_truth(raw, source_path)
    selected_route = run_truth.get("selected_route", "not_reported")
    stage_truth = build_stage_truth(raw, selected_route)
    route_truth = build_route_truth(raw, stage_truth)
    terminal_truth = build_terminal_truth(raw, route_truth.get("route_selected", selected_route))
    evidence_truth = build_evidence_truth(raw, route_truth.get("route_selected", selected_route))
    validation_truth = build_validation_truth(raw, route_truth, terminal_truth, evidence_truth, raw.get("memory") or raw.get("memory_eligibility"))
    memory_truth = build_memory_truth(raw, validation_truth)
    runtime_health_truth = build_runtime_health_truth(root, source_path, raw)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "build": "v17.59 Runtime Truth Backbone + Dashboard Data Contract",
        "built_at": now_utc(),
        "source_path": str(source_path) if source_path else "not_reported",
        "run_truth": run_truth,
        "stage_truth": stage_truth,
        "route_truth": route_truth,
        "terminal_truth": terminal_truth,
        "validation_truth": validation_truth,
        "evidence_truth": evidence_truth,
        "memory_truth": memory_truth,
        "runtime_health_truth": runtime_health_truth,
        "dashboard_summary": {
            "run_id": run_truth.get("run_id"),
            "status": run_truth.get("status"),
            "route": route_truth.get("route_selected"),
            "terminal_state": terminal_truth.get("terminal_state"),
            "validation_status": validation_truth.get("validation_status"),
            "validation_passed": validation_truth.get("validation_passed"),
            "memory_status": memory_truth.get("memory_status"),
            "evidence_count": len(evidence_truth),
            "stages_completed": len([s for s in stage_truth if s.get("status") == "completed"]),
            "stages_blocked_or_failed": len([s for s in stage_truth if s.get("status") in {"blocked", "failed"}]),
            "critical_design_stages_present": len([s for s in stage_truth if s.get("critical_design_stage") and s.get("status") != "not_applicable"]),
        },
        "raw": raw,
    }
    return payload


def write_runtime_truth(root: Path, truth: Mapping[str, Any]) -> Path:
    canonical_path = root / "exports" / "latest" / "dashboard_runtime_truth.json"
    write_json(canonical_path, truth)
    frontend_status_path = root / "src" / "frontend" / "command_center" / "modern" / "runtime_truth_status.json"
    status = {
        "version": "v17.59",
        "status": "runtime_truth_available",
        "updated_at": truth.get("built_at"),
        "canonical_output": str(canonical_path.relative_to(root)) if canonical_path.is_relative_to(root) else str(canonical_path),
        "run_id": truth.get("run_truth", {}).get("run_id"),
        "route": truth.get("route_truth", {}).get("route_selected"),
        "terminal_state": truth.get("terminal_truth", {}).get("terminal_state"),
        "validation_status": truth.get("validation_truth", {}).get("validation_status"),
        "memory_status": truth.get("memory_truth", {}).get("memory_status"),
        "no_fake_data": True,
    }
    write_json(frontend_status_path, status)
    return canonical_path


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build Claire v17.59 canonical runtime truth from core_run_output.json")
    parser.add_argument("--root", default=".", help="Claire project root")
    parser.add_argument("--input", help="Specific core_run_output.json path")
    parser.add_argument("--print", action="store_true", help="Print the generated runtime truth to stdout")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    source_path = Path(args.input).resolve() if args.input else find_latest_core_output(root)
    if not source_path or not source_path.exists():
        print("[CLAIRE] No core_run_output.json or run output was found. No fake runtime truth was generated.")
        print("[CLAIRE] Run Claire first, then run: python tools/claire_build_runtime_truth.py")
        return 2
    raw = read_json(source_path)
    truth = build_runtime_truth(raw, source_path=source_path, root=root)
    output = write_runtime_truth(root, truth)
    if args.print:
        print(json.dumps(truth, indent=2, ensure_ascii=False))
    print(f"[CLAIRE] Runtime truth written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
