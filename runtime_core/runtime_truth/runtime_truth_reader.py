#!/usr/bin/env python3
"""Claire runtime truth reader.

This module converts an existing Claire core_run_output.json into a dashboard_runtime_truth.json
payload that the operating environment can read. It does not fabricate run results.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

STAGE_COUNT = 30
VALID_STATUSES = {"completed", "skipped_by_route", "blocked", "failed", "waiting", "not_started", "running", "not_reported"}

ROUTE_REQUIRED_STAGES = {
    "portfolio": [1,2,3,4,5,6,7,8,9,10,23,26,27,30],
    "breakthrough": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,23,24,25,26,30],
    "design": list(range(1,23)) + [23,24,25,26,30],
    "acquisition": [1,2,3,4,5,6,7,8,9,10,23,24,25,26,28,29,30],
    "insufficient_data": [1,2,3,4,5,10],
}

ROUTE_TERMINALS = {
    "portfolio": {"portfolio_action_ready", "portfolio_optimization_ready", "final_package_ready"},
    "breakthrough": {"breakthrough_classified", "advancement_path_selected", "final_package_ready"},
    "design": {"design_output_ready", "advancement_path_selected", "final_package_ready"},
    "acquisition": {"acquisition_ready", "final_package_ready"},
    "insufficient_data": {"insufficient_data", "blocked", "failed"},
}


def normalize_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")


def normalize_route(value: Any) -> str:
    route = normalize_key(value)
    if not route:
        return "not_reported"
    if "portfolio" in route:
        return "portfolio"
    if "acquisition" in route or "acquirer" in route:
        return "acquisition"
    if any(token in route for token in ("design", "autodesign", "invention", "solution")):
        return "design"
    if "breakthrough" in route or "discovery" in route:
        return "breakthrough"
    if "insufficient" in route or "blocked" in route:
        return "insufficient_data"
    return route


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_output_paths(root: Path) -> List[Path]:
    fixed = [
        root / "exports" / "latest" / "core_run_output.json",
        root / "exports" / "latest" / "dashboard_runtime_truth.json",
        root / "output" / "core_run_output.json",
        root / "core_run_output.json",
    ]
    found = [p for p in fixed if p.exists()]
    exports = root / "exports"
    if exports.exists():
        found.extend(sorted(exports.rglob("core_run_output.json"), key=lambda p: p.stat().st_mtime, reverse=True))
    dedup: List[Path] = []
    seen = set()
    for p in found:
        key = p.resolve()
        if key not in seen:
            dedup.append(p)
            seen.add(key)
    return dedup


def find_latest_core_output(root: Path) -> Optional[Path]:
    candidates = candidate_output_paths(root)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def stage_number(value: Any) -> Optional[int]:
    if isinstance(value, int) and 1 <= value <= STAGE_COUNT:
        return value
    if isinstance(value, str):
        match = re.search(r"(?:stage[_ -]?)?(\d{1,2})", value, flags=re.I)
        if match:
            num = int(match.group(1))
            return num if 1 <= num <= STAGE_COUNT else None
    if isinstance(value, dict):
        for key in ("number", "stage_number", "stage", "id", "name", "stage_id"):
            num = stage_number(value.get(key))
            if num:
                return num
    return None


def infer_status(payload: Any) -> str:
    if payload in (None, ""):
        return "not_reported"
    if isinstance(payload, str):
        status = normalize_key(payload)
        return status if status in VALID_STATUSES else "completed"
    if isinstance(payload, dict):
        for key in ("status", "state", "result", "outcome"):
            status = normalize_key(payload.get(key))
            if status:
                if status == "passed":
                    return "completed"
                if status in VALID_STATUSES:
                    return status
        return "completed" if payload else "not_reported"
    return "completed"


def merge_stage(existing: Optional[Dict[str, Any]], incoming: Dict[str, Any]) -> Dict[str, Any]:
    if not existing:
        return incoming
    rank = {"failed": 8, "blocked": 8, "running": 7, "completed": 6, "skipped_by_route": 5, "waiting": 4, "not_started": 3, "not_reported": 1}
    if rank.get(incoming.get("status", "not_reported"), 0) >= rank.get(existing.get("status", "not_reported"), 0):
        merged = dict(existing)
        merged.update(incoming)
        return merged
    merged = dict(incoming)
    merged.update(existing)
    return merged


def normalize_stage_object(num: int, payload: Any) -> Dict[str, Any]:
    obj = payload if isinstance(payload, dict) else {"value": payload}
    return {
        "number": num,
        "status": infer_status(payload),
        "summary": obj.get("summary") or obj.get("output_summary") or obj.get("result_summary"),
        "reason_if_skipped": obj.get("reason_if_skipped") or obj.get("skip_reason") or obj.get("reason"),
        "confidence": obj.get("confidence"),
        "evidence": obj.get("evidence") or obj.get("evidence_chain"),
        "payload": payload,
    }


def add_stage_candidate(stage_map: Dict[int, Dict[str, Any]], candidate: Any) -> None:
    if not candidate:
        return
    if isinstance(candidate, list):
        for item in candidate:
            num = stage_number(item)
            if num:
                stage_map[num] = merge_stage(stage_map.get(num), normalize_stage_object(num, item))
    elif isinstance(candidate, dict):
        for key, value in candidate.items():
            num = stage_number(value) or stage_number(key)
            if num:
                stage_map[num] = merge_stage(stage_map.get(num), normalize_stage_object(num, value))


def build_stage_map(raw: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    stage_map: Dict[int, Dict[str, Any]] = {}
    for key in ("lifecycle_stages", "core_lifecycle_stages", "stage_statuses", "stages"):
        add_stage_candidate(stage_map, raw.get(key))
    for container_key in ("core_lifecycle", "lifecycle", "runtime", "execution"):
        container = raw.get(container_key)
        if isinstance(container, dict):
            add_stage_candidate(stage_map, container.get("stages"))
    for key, value in raw.items():
        match = re.match(r"stage[_-]?(\d{1,2})(?:_|$)", key, flags=re.I)
        if match:
            num = int(match.group(1))
            stage_map[num] = merge_stage(stage_map.get(num), normalize_stage_object(num, value))
    for key, status in (("stages_completed", "completed"), ("completed_stages", "completed"), ("stages_skipped", "skipped_by_route"), ("skipped_stages", "skipped_by_route"), ("stages_failed", "failed"), ("failed_stages", "failed")):
        items = raw.get(key) or []
        if not isinstance(items, list):
            items = [items]
        for item in items:
            num = stage_number(item)
            if num:
                stage_map[num] = merge_stage(stage_map.get(num), {"number": num, "status": status, "payload": item})
    return stage_map


def normalize_validation(value: Any) -> Dict[str, Any]:
    if isinstance(value, str):
        return {"status": normalize_key(value), "raw": value}
    if isinstance(value, bool):
        return {"status": "pass" if value else "fail", "raw": value}
    if isinstance(value, dict):
        raw_status = value.get("status") or value.get("result") or value.get("validation_status") or value.get("passed") or value.get("pass")
        if isinstance(raw_status, bool):
            status = "pass" if raw_status else "fail"
        else:
            status = normalize_key(raw_status) or "not_reported"
            if status == "passed":
                status = "pass"
            elif status == "failed":
                status = "fail"
        return {"status": status, "raw": value}
    return {"status": "not_reported", "raw": value}


def build_runtime_truth(raw: Dict[str, Any], source_path: Optional[Path] = None) -> Dict[str, Any]:
    route_decision = raw.get("route_decision") or raw.get("route") or raw.get("routing") or raw.get("core_lifecycle_summary") or {}
    validation = normalize_validation(raw.get("validation_result") or raw.get("validation") or raw.get("output_validation"))
    stage_map = build_stage_map(raw)
    route_selected = normalize_route(raw.get("route_selected") or raw.get("selected_route") or route_decision.get("route_selected") or route_decision.get("selected_route") or route_decision.get("route") or raw.get("route_type"))
    terminal_state = raw.get("terminal_state") or raw.get("status_terminal") or (raw.get("core_lifecycle_summary") or {}).get("terminal_state") or raw.get("status") or "not_reported"
    route_contract = ROUTE_REQUIRED_STAGES.get(route_selected, [])
    stage_records = []
    for number in range(1, STAGE_COUNT + 1):
        record = stage_map.get(number, {"number": number, "status": "not_reported"})
        record["required_for_selected_route"] = number in route_contract
        record["critical_design_stage"] = number in {16,17,18,19,20,21,22}
        stage_records.append(record)
    evidence = raw.get("evidence_chain") or raw.get("evidence") or raw.get("sources") or []
    if not isinstance(evidence, list):
        evidence = [evidence]
    completed = sum(1 for item in stage_records if item.get("status") == "completed")
    skipped = sum(1 for item in stage_records if item.get("status") == "skipped_by_route")
    failed = sum(1 for item in stage_records if item.get("status") in {"failed", "blocked"})
    proof_checks = {
        "route_selected": route_selected != "not_reported",
        "terminal_state_present": terminal_state != "not_reported",
        "validation_reported": validation.get("status") != "not_reported",
        "all_30_stages_reported": all(item.get("status") != "not_reported" for item in stage_records),
        "route_terminal_fit": terminal_state in ROUTE_TERMINALS.get(route_selected, set()),
        "evidence_chain_reported": bool(evidence),
    }
    return {
        "schema_version": "v17.57-v17.58",
        "source_path": str(source_path) if source_path else None,
        "run_id": raw.get("run_id") or raw.get("id") or raw.get("session_id") or "not_reported",
        "timestamp": raw.get("timestamp") or raw.get("created_at") or raw.get("completed_at") or raw.get("started_at") or "not_reported",
        "route_selected": route_selected,
        "route_decision": route_decision,
        "routes_rejected": raw.get("routes_rejected") or route_decision.get("routes_rejected") or route_decision.get("rejected_routes") or [],
        "terminal_state": terminal_state,
        "validation_result": validation,
        "validated_output_path": raw.get("validated_output_path") or raw.get("output_path") or raw.get("export_path") or "not_reported",
        "memory_eligibility": raw.get("memory_eligibility") or (raw.get("memory") or {}).get("eligibility") or "not_reported",
        "evidence_chain": evidence,
        "confidence_scores": raw.get("confidence_scores") or raw.get("confidence") or route_decision.get("confidence_scores") or {},
        "governance_stamp": raw.get("governance_stamp") or raw.get("governance") or raw.get("source_governance") or "not_reported",
        "lifecycle_stages": stage_records,
        "stage_counts": {"completed": completed, "skipped_by_route": skipped, "failed_or_blocked": failed, "total": STAGE_COUNT},
        "route_contract": {"required_stages": route_contract, "terminal_states": sorted(ROUTE_TERMINALS.get(route_selected, []))},
        "proof_checks": proof_checks,
        "raw": raw,
    }


def write_dashboard_runtime_truth(root: Path, runtime_truth: Dict[str, Any]) -> Path:
    output_dir = root / "exports" / "latest"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "dashboard_runtime_truth.json"
    output_path.write_text(json.dumps(runtime_truth, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build Claire dashboard_runtime_truth.json from an existing core_run_output.json")
    parser.add_argument("--root", default=".", help="Claire project root")
    parser.add_argument("--input", help="Specific core_run_output.json path")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    input_path = Path(args.input).resolve() if args.input else find_latest_core_output(root)
    if not input_path or not input_path.exists():
        print("[CLAIRE] No core_run_output.json found. No runtime truth file was generated.")
        return 2
    raw = read_json(input_path)
    truth = build_runtime_truth(raw, input_path)
    output_path = write_dashboard_runtime_truth(root, truth)
    print(f"[CLAIRE] Runtime truth written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
