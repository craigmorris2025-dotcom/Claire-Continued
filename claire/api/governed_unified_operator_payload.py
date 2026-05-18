
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


SECTION_ORDER = [
    "system_status",
    "governed_web_status",
    "research_queue",
    "source_policy",
    "approved_fetch_plans",
    "quarantined_evidence",
    "extraction_summaries",
    "promotion_governance",
    "blocked_candidates",
    "replay_verification",
    "plateau_status",
]


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


def _safe_summary(payload: Mapping[str, Any]) -> Dict[str, Any]:
    keys = [
        "record_type", "version", "status", "available", "reason", "candidate_count",
        "blocked_count", "ready_count", "missing_count", "available_count",
        "panel_count", "total_audit_boundaries", "replay_ok", "verification_ok",
    ]
    return {key: payload.get(key) for key in keys if key in payload}


def build_operator_section(name: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    section = {
        "section": name,
        "available": bool(payload.get("available", False)),
        "path": payload.get("path"),
        "summary": _safe_summary(payload),
        "source_sha256": (
            payload.get("payload_sha256")
            or payload.get("contracts_sha256")
            or payload.get("package_index_sha256")
            or payload.get("blocked_registry_sha256")
            or payload.get("replay_report_sha256")
            or payload.get("plateau_report_sha256")
            or payload.get("status_sha256")
            or payload.get("registry_sha256")
            or payload.get("verification_sha256")
        ),
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "promotion_effect": "none",
    }
    section["section_sha256"] = _sha256(section)
    return section


def build_unified_operator_payload(root: Path) -> Dict[str, Any]:
    output = root / "output"

    backend_truth_payload = _read_json(output / "backend_truth_surfaces" / "backend_truth_surface_payload.json")
    backend_truth_status = _read_json(output / "backend_truth_surfaces" / "backend_truth_surface_status.json")
    cockpit_contracts = _read_json(output / "cockpit_consumption_contracts" / "cockpit_consumption_contracts.json")
    cockpit_verification = _read_json(output / "cockpit_consumption_contracts" / "cockpit_consumption_contract_verification.json")

    package_index = _read_json(output / "manual_promotion_plateau" / "manual_promotion_package_index.json")
    blocked_registry = _read_json(output / "manual_promotion_plateau" / "blocked_promotion_candidate_registry.json")
    replay_report = _read_json(output / "manual_promotion_plateau" / "promotion_package_replay_verification.json")
    plateau_report = _read_json(output / "manual_promotion_plateau" / "s39_manual_promotion_plateau_report.json")

    surfaces = dict(backend_truth_status.get("surfaces", {}) or {})

    raw_sections = {
        "system_status": backend_truth_status,
        "governed_web_status": surfaces.get("web_needs", {"available": False, "reason": "missing"}),
        "research_queue": surfaces.get("research_queue", {"available": False, "reason": "missing"}),
        "source_policy": surfaces.get("source_policy", {"available": False, "reason": "missing"}),
        "approved_fetch_plans": surfaces.get("approved_fetch_plans", {"available": False, "reason": "missing"}),
        "quarantined_evidence": surfaces.get("quarantined_evidence", {"available": False, "reason": "missing"}),
        "extraction_summaries": surfaces.get("extraction_reports", {"available": False, "reason": "missing"}),
        "promotion_governance": package_index,
        "blocked_candidates": blocked_registry,
        "replay_verification": replay_report,
        "plateau_status": plateau_report,
    }

    sections = [build_operator_section(name, raw_sections.get(name, {})) for name in SECTION_ORDER]

    lineage = {
        "backend_truth_payload_sha256": backend_truth_payload.get("payload_sha256"),
        "backend_truth_status_sha256": backend_truth_status.get("status_sha256"),
        "cockpit_contracts_sha256": cockpit_contracts.get("contracts_sha256"),
        "cockpit_verification_sha256": cockpit_verification.get("verification_sha256"),
        "package_index_sha256": package_index.get("package_index_sha256"),
        "blocked_registry_sha256": blocked_registry.get("blocked_registry_sha256"),
        "replay_report_sha256": replay_report.get("replay_report_sha256"),
        "plateau_report_sha256": plateau_report.get("plateau_report_sha256"),
    }

    payload = {
        "record_type": "unified_backend_operator_payload",
        "version": "v19.89.8-S40R9-R12",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "section_order": list(SECTION_ORDER),
        "section_count": len(sections),
        "available_section_count": sum(1 for section in sections if section.get("available") is True),
        "sections": sections,
        "lineage": lineage,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "browser_execution_allowed": False,
        "javascript_execution_allowed": False,
        "created_at": _utc_now(),
    }
    payload["operator_payload_sha256"] = _sha256(payload)
    return payload


def verify_unified_operator_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    failures: List[str] = []
    sections = list(payload.get("sections", []) or [])

    if payload.get("backend_owns_truth") is not True:
        failures.append("backend_owns_truth_missing")
    if payload.get("cockpit_presentation_only") is not True:
        failures.append("cockpit_presentation_only_missing")
    if payload.get("runtime_truth_mutation_allowed") is not False:
        failures.append("runtime_truth_mutation_not_false")
    if payload.get("automatic_update_allowed") is not False:
        failures.append("automatic_update_not_false")
    if payload.get("browser_execution_allowed") is not False:
        failures.append("browser_execution_not_false")
    if payload.get("javascript_execution_allowed") is not False:
        failures.append("javascript_execution_not_false")
    if [section.get("section") for section in sections] != SECTION_ORDER:
        failures.append("section_order_mismatch")

    for section in sections:
        if section.get("runtime_truth_mutation_allowed") is not False:
            failures.append(f"{section.get('section')}_runtime_mutation_not_false")
        if section.get("automatic_update_allowed") is not False:
            failures.append(f"{section.get('section')}_automatic_update_not_false")
        if section.get("promotion_effect") != "none":
            failures.append(f"{section.get('section')}_promotion_effect_not_none")

    report = {
        "record_type": "unified_operator_payload_verification",
        "version": "v19.89.8-S40R9-R12",
        "verification_ok": not failures,
        "failures": failures,
        "section_count": len(sections),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    report["verification_sha256"] = _sha256(report)
    return report


def write_unified_operator_payload(root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_unified_operator_payload(root)
    verification = verify_unified_operator_payload(payload)

    files = {
        "payload": output_dir / "unified_backend_operator_payload.json",
        "verification": output_dir / "unified_backend_operator_payload_verification.json",
    }
    files["payload"].write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    files["verification"].write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}
