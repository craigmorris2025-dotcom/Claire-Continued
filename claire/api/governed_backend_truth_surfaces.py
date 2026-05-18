
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


LOCKED_AUTHORITY = {
    "runtime_truth_mutation": False,
    "automatic_updates": False,
    "autonomous_execution": False,
    "continuous_live_crawling": False,
    "browser_execution": False,
    "javascript_execution": False,
}


SURFACE_NAMES = [
    "system_inventory",
    "web_needs",
    "research_queue",
    "source_policy",
    "approved_fetch_plans",
    "quarantined_evidence",
    "extraction_reports",
    "manual_promotion_status",
    "update_proposal_status",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "available": False,
            "path": str(path),
            "reason": "missing",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            payload["available"] = True
            payload.setdefault("path", str(path))
            return payload
        return {"available": True, "path": str(path), "value": payload}
    except Exception as exc:
        return {
            "available": False,
            "path": str(path),
            "reason": f"unreadable:{type(exc).__name__}",
        }


def _count_json_files(path: Path) -> int:
    if not path.exists():
        return 0
    return len(list(path.glob("*.json")))


def build_backend_truth_surface_registry(root: Path) -> Dict[str, Any]:
    output = root / "output"
    registry = {
        "record_type": "backend_truth_surface_registry",
        "version": "v19.89.8-S40R1-R4",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "surface_names": list(SURFACE_NAMES),
        "surface_count": len(SURFACE_NAMES),
        "created_at": _utc_now(),
    }
    registry["registry_sha256"] = _sha256(registry)
    return registry


def build_backend_truth_surface_status(root: Path) -> Dict[str, Any]:
    output = root / "output"
    status = {
        "record_type": "backend_truth_surface_status",
        "version": "v19.89.8-S40R1-R4",
        "surfaces": {
            "system_inventory": {
                "available": (output / "system_inventory").exists(),
                "path": str(output / "system_inventory"),
            },
            "web_needs": {
                "available": (output / "governed_web_needs").exists(),
                "path": str(output / "governed_web_needs"),
            },
            "research_queue": {
                "available": (output / "governed_research_queue").exists(),
                "path": str(output / "governed_research_queue"),
            },
            "source_policy": {
                "available": (output / "source_policy").exists(),
                "path": str(output / "source_policy"),
            },
            "approved_fetch_plans": {
                "available": (output / "approved_fetch_plans").exists(),
                "path": str(output / "approved_fetch_plans"),
            },
            "quarantined_evidence": {
                "available": (output / "quarantined_evidence").exists(),
                "path": str(output / "quarantined_evidence"),
                "json_count": _count_json_files(output / "quarantined_evidence"),
            },
            "extraction_reports": {
                "available": (output / "structured_knowledge").exists(),
                "path": str(output / "structured_knowledge"),
                "json_count": _count_json_files(output / "structured_knowledge"),
            },
            "manual_promotion_status": {
                "available": (output / "manual_promotion_plateau" / "s39_manual_promotion_plateau_report.json").exists(),
                "path": str(output / "manual_promotion_plateau" / "s39_manual_promotion_plateau_report.json"),
            },
            "update_proposal_status": {
                "available": (output / "manual_promotion_plateau" / "manual_promotion_package_index.json").exists(),
                "path": str(output / "manual_promotion_plateau" / "manual_promotion_package_index.json"),
            },
        },
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    status["available_count"] = sum(1 for item in status["surfaces"].values() if item.get("available") is True)
    status["missing_count"] = len(status["surfaces"]) - status["available_count"]
    status["status_sha256"] = _sha256(status)
    return status


def build_backend_truth_surface_payload(root: Path) -> Dict[str, Any]:
    output = root / "output"
    registry = build_backend_truth_surface_registry(root)
    status = build_backend_truth_surface_status(root)

    manual_promotion = _read_json(output / "manual_promotion_plateau" / "s39_manual_promotion_plateau_report.json")
    package_index = _read_json(output / "manual_promotion_plateau" / "manual_promotion_package_index.json")
    blocked_registry = _read_json(output / "manual_promotion_plateau" / "blocked_promotion_candidate_registry.json")
    replay_report = _read_json(output / "manual_promotion_plateau" / "promotion_package_replay_verification.json")

    payload = {
        "record_type": "backend_truth_surface_payload",
        "version": "v19.89.8-S40R1-R4",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "registry": registry,
        "status": status,
        "manual_promotion": {
            "plateau_report": manual_promotion,
            "package_index": package_index,
            "blocked_registry": blocked_registry,
            "replay_report": replay_report,
        },
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "browser_execution_allowed": False,
        "javascript_execution_allowed": False,
        "created_at": _utc_now(),
    }
    payload["payload_sha256"] = _sha256(payload)
    return payload


def write_backend_truth_surface_payload(root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    registry = build_backend_truth_surface_registry(root)
    status = build_backend_truth_surface_status(root)
    payload = build_backend_truth_surface_payload(root)

    files = {
        "registry": output_dir / "backend_truth_surface_registry.json",
        "status": output_dir / "backend_truth_surface_status.json",
        "payload": output_dir / "backend_truth_surface_payload.json",
    }
    files["registry"].write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
    files["status"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["payload"].write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}
