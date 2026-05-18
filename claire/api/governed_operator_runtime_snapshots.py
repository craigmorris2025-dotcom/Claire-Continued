
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping


LOCKED_AUTHORITY = {
    "runtime_truth_mutation": False,
    "automatic_updates": False,
    "autonomous_execution": False,
    "continuous_live_crawling": False,
    "browser_execution": False,
    "javascript_execution": False,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"available": False, "path": str(path), "reason": "missing"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("available", True)
            data.setdefault("path", str(path))
            return data
        return {"available": True, "path": str(path), "value": data}
    except Exception as exc:
        return {"available": False, "path": str(path), "reason": f"unreadable:{type(exc).__name__}"}


def build_operator_state_snapshot(unified_payload: Mapping[str, Any]) -> Dict[str, Any]:
    sections = list(unified_payload.get("sections", []) or [])
    blocked = [
        section for section in sections
        if section.get("available") is False
    ]
    snapshot = {
        "record_type": "operator_state_snapshot",
        "version": "v19.89.8-S41R1-R4",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "source_operator_payload_sha256": unified_payload.get("operator_payload_sha256"),
        "section_count": len(sections),
        "available_section_count": sum(1 for section in sections if section.get("available") is True),
        "unavailable_section_count": len(blocked),
        "unavailable_sections": [
            {
                "section": section.get("section"),
                "reason": section.get("summary", {}).get("reason"),
                "path": section.get("path"),
            }
            for section in blocked
        ],
        "runtime_state": "operator_payload_available" if unified_payload.get("available", True) is not False else "operator_payload_missing",
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "autonomous_execution_allowed": False,
        "created_at": _utc_now(),
    }
    snapshot["operator_state_snapshot_sha256"] = _sha256(snapshot)
    return snapshot


def build_bounded_runtime_summary(snapshot: Mapping[str, Any]) -> Dict[str, Any]:
    status = "ready_for_cockpit_rendering"
    if snapshot.get("unavailable_section_count", 0) > 0:
        status = "partial_surfaces_available"
    if snapshot.get("source_operator_payload_sha256") in {None, ""}:
        status = "operator_payload_unverified"

    summary = {
        "record_type": "bounded_runtime_summary",
        "version": "v19.89.8-S41R1-R4",
        "status": status,
        "section_count": snapshot.get("section_count", 0),
        "available_section_count": snapshot.get("available_section_count", 0),
        "unavailable_section_count": snapshot.get("unavailable_section_count", 0),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "source_operator_state_snapshot_sha256": snapshot.get("operator_state_snapshot_sha256"),
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    summary["bounded_runtime_summary_sha256"] = _sha256(summary)
    return summary


def build_snapshot_lineage(unified_payload: Mapping[str, Any], snapshot: Mapping[str, Any], summary: Mapping[str, Any]) -> Dict[str, Any]:
    lineage = {
        "record_type": "operator_snapshot_lineage",
        "version": "v19.89.8-S41R1-R4",
        "operator_payload_sha256": unified_payload.get("operator_payload_sha256"),
        "operator_state_snapshot_sha256": snapshot.get("operator_state_snapshot_sha256"),
        "bounded_runtime_summary_sha256": summary.get("bounded_runtime_summary_sha256"),
        "source_lineage": dict(unified_payload.get("lineage", {}) or {}),
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    lineage["snapshot_lineage_sha256"] = _sha256(lineage)
    return lineage


def verify_operator_runtime_snapshot(
    unified_payload: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    summary: Mapping[str, Any],
    lineage: Mapping[str, Any],
) -> Dict[str, Any]:
    failures: List[str] = []
    if snapshot.get("runtime_truth_mutation_allowed") is not False:
        failures.append("snapshot_runtime_truth_mutation_not_false")
    if summary.get("automatic_update_allowed") is not False:
        failures.append("summary_automatic_update_not_false")
    if lineage.get("runtime_truth_mutation_allowed") is not False:
        failures.append("lineage_runtime_truth_mutation_not_false")
    if snapshot.get("source_operator_payload_sha256") != unified_payload.get("operator_payload_sha256"):
        failures.append("snapshot_source_payload_sha_mismatch")
    if summary.get("source_operator_state_snapshot_sha256") != snapshot.get("operator_state_snapshot_sha256"):
        failures.append("summary_source_snapshot_sha_mismatch")
    if lineage.get("operator_state_snapshot_sha256") != snapshot.get("operator_state_snapshot_sha256"):
        failures.append("lineage_snapshot_sha_mismatch")
    if lineage.get("bounded_runtime_summary_sha256") != summary.get("bounded_runtime_summary_sha256"):
        failures.append("lineage_summary_sha_mismatch")

    report = {
        "record_type": "operator_runtime_snapshot_verification",
        "version": "v19.89.8-S41R1-R4",
        "verification_ok": not failures,
        "failures": failures,
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    report["verification_sha256"] = _sha256(report)
    return report


def write_operator_runtime_snapshots(root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    unified_payload = _read_json(root / "output" / "unified_operator_payload" / "unified_backend_operator_payload.json")
    snapshot = build_operator_state_snapshot(unified_payload)
    summary = build_bounded_runtime_summary(snapshot)
    lineage = build_snapshot_lineage(unified_payload, snapshot, summary)
    verification = verify_operator_runtime_snapshot(unified_payload, snapshot, summary, lineage)

    files = {
        "snapshot": output_dir / "operator_state_snapshot.json",
        "summary": output_dir / "bounded_runtime_summary.json",
        "lineage": output_dir / "operator_snapshot_lineage.json",
        "verification": output_dir / "operator_runtime_snapshot_verification.json",
    }
    files["snapshot"].write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    files["summary"].write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    files["lineage"].write_text(json.dumps(lineage, indent=2, sort_keys=True), encoding="utf-8")
    files["verification"].write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}
