
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


def build_current_state_digest(snapshot: Mapping[str, Any], summary: Mapping[str, Any]) -> Dict[str, Any]:
    unavailable_count = int(snapshot.get("unavailable_section_count", 0) or 0)
    state = "ready"
    if unavailable_count > 0:
        state = "partial"
    if summary.get("status") == "operator_payload_unverified":
        state = "unverified"

    digest = {
        "record_type": "operator_current_state_digest",
        "version": "v19.89.8-S41R5-R8",
        "state": state,
        "summary_status": summary.get("status"),
        "section_count": snapshot.get("section_count", 0),
        "available_section_count": snapshot.get("available_section_count", 0),
        "unavailable_section_count": unavailable_count,
        "source_snapshot_sha256": snapshot.get("operator_state_snapshot_sha256"),
        "source_summary_sha256": summary.get("bounded_runtime_summary_sha256"),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    digest["current_state_digest_sha256"] = _sha256(digest)
    return digest


def build_operator_alert_summary(snapshot: Mapping[str, Any], digest: Mapping[str, Any]) -> Dict[str, Any]:
    alerts: List[Dict[str, Any]] = []
    for item in snapshot.get("unavailable_sections", []) or []:
        alerts.append({
            "severity": "info",
            "code": "surface_unavailable",
            "section": item.get("section"),
            "reason": item.get("reason"),
            "path": item.get("path"),
            "operator_action": "review_missing_surface_if_expected",
        })

    if digest.get("state") == "unverified":
        alerts.append({
            "severity": "warning",
            "code": "operator_payload_unverified",
            "operator_action": "rebuild_unified_operator_payload_before_cockpit_use",
        })

    summary = {
        "record_type": "operator_alert_summary",
        "version": "v19.89.8-S41R5-R8",
        "alert_count": len(alerts),
        "alerts": alerts,
        "source_current_state_digest_sha256": digest.get("current_state_digest_sha256"),
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    summary["operator_alert_summary_sha256"] = _sha256(summary)
    return summary


def build_snapshot_replay_index(snapshot: Mapping[str, Any], summary: Mapping[str, Any], digest: Mapping[str, Any], alerts: Mapping[str, Any]) -> Dict[str, Any]:
    index = {
        "record_type": "operator_snapshot_replay_index",
        "version": "v19.89.8-S41R5-R8",
        "snapshot_sha256": snapshot.get("operator_state_snapshot_sha256"),
        "summary_sha256": summary.get("bounded_runtime_summary_sha256"),
        "digest_sha256": digest.get("current_state_digest_sha256"),
        "alerts_sha256": alerts.get("operator_alert_summary_sha256"),
        "replay_order": [
            "operator_state_snapshot",
            "bounded_runtime_summary",
            "operator_current_state_digest",
            "operator_alert_summary",
        ],
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    index["snapshot_replay_index_sha256"] = _sha256(index)
    return index


def build_s41_readiness_report(digest: Mapping[str, Any], alerts: Mapping[str, Any], replay_index: Mapping[str, Any]) -> Dict[str, Any]:
    status = "s41_ready"
    if digest.get("state") == "unverified":
        status = "blocked_unverified_payload"

    report = {
        "record_type": "s41_operator_runtime_snapshot_readiness_report",
        "version": "v19.89.8-S41R5-R8",
        "status": status,
        "state": digest.get("state"),
        "alert_count": alerts.get("alert_count", 0),
        "replay_index_sha256": replay_index.get("snapshot_replay_index_sha256"),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "next_phase": "S41R9-R12 operator payload route contracts or S42 cockpit route exposure",
        "created_at": _utc_now(),
    }
    report["s41_readiness_report_sha256"] = _sha256(report)
    return report


def verify_s41_digest_artifacts(digest: Mapping[str, Any], alerts: Mapping[str, Any], replay_index: Mapping[str, Any], readiness: Mapping[str, Any]) -> Dict[str, Any]:
    failures: List[str] = []
    for name, payload in {
        "digest": digest,
        "alerts": alerts,
        "replay_index": replay_index,
        "readiness": readiness,
    }.items():
        if payload.get("runtime_truth_mutation_allowed") is not False:
            failures.append(f"{name}_runtime_truth_mutation_not_false")
        if payload.get("automatic_update_allowed") is not False:
            failures.append(f"{name}_automatic_update_not_false")

    if replay_index.get("digest_sha256") != digest.get("current_state_digest_sha256"):
        failures.append("replay_index_digest_sha_mismatch")
    if replay_index.get("alerts_sha256") != alerts.get("operator_alert_summary_sha256"):
        failures.append("replay_index_alerts_sha_mismatch")
    if readiness.get("replay_index_sha256") != replay_index.get("snapshot_replay_index_sha256"):
        failures.append("readiness_replay_index_sha_mismatch")

    report = {
        "record_type": "s41_digest_artifact_verification",
        "version": "v19.89.8-S41R5-R8",
        "verification_ok": not failures,
        "failures": failures,
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    report["verification_sha256"] = _sha256(report)
    return report


def write_s41_operator_state_digest(root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    source_dir = root / "output" / "operator_runtime_snapshots"
    snapshot = _read_json(source_dir / "operator_state_snapshot.json")
    summary = _read_json(source_dir / "bounded_runtime_summary.json")

    digest = build_current_state_digest(snapshot, summary)
    alerts = build_operator_alert_summary(snapshot, digest)
    replay_index = build_snapshot_replay_index(snapshot, summary, digest, alerts)
    readiness = build_s41_readiness_report(digest, alerts, replay_index)
    verification = verify_s41_digest_artifacts(digest, alerts, replay_index, readiness)

    files = {
        "digest": output_dir / "operator_current_state_digest.json",
        "alerts": output_dir / "operator_alert_summary.json",
        "replay_index": output_dir / "operator_snapshot_replay_index.json",
        "readiness": output_dir / "s41_operator_runtime_snapshot_readiness_report.json",
        "verification": output_dir / "s41_digest_artifact_verification.json",
    }
    files["digest"].write_text(json.dumps(digest, indent=2, sort_keys=True), encoding="utf-8")
    files["alerts"].write_text(json.dumps(alerts, indent=2, sort_keys=True), encoding="utf-8")
    files["replay_index"].write_text(json.dumps(replay_index, indent=2, sort_keys=True), encoding="utf-8")
    files["readiness"].write_text(json.dumps(readiness, indent=2, sort_keys=True), encoding="utf-8")
    files["verification"].write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}
